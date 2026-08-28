"""Guarded reads of Home Assistant states, with a staleness watchdog.

Every sensor the optimizer depends on is read through :class:`InputReader`
rather than directly from ``hass.states``. Two things are enforced here that a
bare read cannot express:

**Freshness.** ``unavailable`` and ``unknown`` are the easy failures; they are
visible and every call site already handles them. The dangerous failure is a
sensor that stops updating while continuing to report its last value. A dead
battery in a tank probe or a dropped Zigbee room sensor leaves a perfectly
valid-looking constant in the state machine indefinitely. The optimizer then
plans against a fiction — but the worse consequence is that the learners
observe a flatline, attribute it to thermal behaviour, and persist a corrupted
parameter that survives a restart. A learner that stops learning is
recoverable; one that learns from a flatline is not. So an over-age value is
reported as *missing*, and the caller is expected to freeze rather than guess.

**Units.** Power entities report W, kW or MW depending on the device, and the
internal model works in kW throughout. Assuming kW reads a 3000 W draw as
3000 kW, which would silently dominate every cost calculation.

**Not everything is a number.** An operating mode is a word, and a defrost or
online flag is ``on``/``off``. ``read`` rejects those as ``not_numeric``, so
until v5.2.0 the only string input in the integration — the external-heat
override — was read by hand, straight out of ``hass.states``, with no
freshness guard at all. That is precisely backwards: a stuck ``on`` on a
flag that *suppresses* heating is more dangerous than a stuck temperature,
because it costs a warm house rather than a little accuracy. ``read_state``
and ``read_bool`` put strings and flags through the same guard as every
number, and produce the same :class:`InputReading` the rest of the code
already understands.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .const import (
    INPUT_MAX_AGE_MINUTES,
    POWER_UNIT_TO_KW,
    STALENESS_SCALE_MAX,
    STALENESS_SCALE_MIN,
)

_LOGGER = logging.getLogger(__name__)

_INVALID_STATES = ("unknown", "unavailable", "none", "")


class _Unbounded:
    """Sentinel for ``max_age_minutes``: read with no freshness horizon.

    Distinct from ``None``, which means "whatever :data:`INPUT_MAX_AGE_MINUTES`
    says for this key". A caller passes this when age is not evidence about
    the entity in question — the case being an entity nothing ever re-writes,
    such as an ``input_boolean`` or a template flag fed by one, where the
    timestamp records when a *person* last decided something rather than when
    the reading was last confirmed. Ageing those out turns a deliberate
    setting into no setting at all.
    """

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "UNBOUNDED"


#: See :class:`_Unbounded`.
UNBOUNDED = _Unbounded()


@dataclass
class InputReading:
    """One attempt to read a configured entity."""

    key: str
    entity_id: str | None
    value: float | None = None
    #: The raw state string, for inputs whose meaning is a word rather than a
    #: number (``read_state``). ``read`` never sets it, so every existing
    #: caller sees exactly the reading it saw before.
    text: str | None = None
    #: The boolean ``text`` was interpreted as (``read_bool``).
    flag: bool | None = None
    age_minutes: float | None = None
    max_age_minutes: float | None = None
    #: ``None`` when the read succeeded, otherwise why it did not.
    problem: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the reading may be used.

        Widened in v5.2.0 from "has a number" to "has *something*", so that a
        string or a flag participates in ``InputHealth`` — and therefore in
        ``_learning_frozen`` and the diagnostics — on exactly the same terms
        as a temperature. ``read`` still populates only ``value``, so this is
        unchanged for every numeric caller.
        """
        return (
            self.value is not None or self.text is not None
        ) and self.problem is None

    @property
    def stale(self) -> bool:
        """Whether a value was present but too old to trust."""
        return self.problem == "stale"


@dataclass
class InputHealth:
    """A snapshot of every guarded read from one update cycle."""

    readings: dict[str, InputReading] = field(default_factory=dict)

    def record(self, reading: InputReading) -> InputReading:
        self.readings[reading.key] = reading
        return reading

    @property
    def stale_keys(self) -> list[str]:
        return sorted(k for k, r in self.readings.items() if r.stale)

    @property
    def missing_keys(self) -> list[str]:
        """Configured entities that produced no usable value at all."""
        return sorted(
            k
            for k, r in self.readings.items()
            if r.entity_id and not r.ok and not r.stale
        )

    @property
    def healthy(self) -> bool:
        return not self.stale_keys and not self.missing_keys

    def ages(self) -> dict[str, float]:
        return {
            k: round(r.age_minutes, 1)
            for k, r in self.readings.items()
            if r.age_minutes is not None
        }

    def details(self) -> list[dict[str, Any]]:
        """Per-input evidence, so a user can see *why* something is flagged."""
        out = []
        for key in sorted(self.readings):
            reading = self.readings[key]
            if reading.entity_id is None or reading.ok:
                continue
            out.append(
                {
                    "input": key,
                    "entity_id": reading.entity_id,
                    "problem": reading.problem,
                    "age_minutes": (
                        round(reading.age_minutes, 1)
                        if reading.age_minutes is not None
                        else None
                    ),
                    "max_age_minutes": reading.max_age_minutes,
                }
            )
        return out


def max_age_for(key: str, scale: float = 1.0) -> float | None:
    """Age limit in minutes for a configuration key, or ``None`` if unbounded."""
    base = INPUT_MAX_AGE_MINUTES.get(key)
    if base is None:
        return None
    scale = min(max(float(scale), STALENESS_SCALE_MIN), STALENESS_SCALE_MAX)
    return base * scale


def normalize_power_kw(value: float, unit: Any) -> float | None:
    """Convert a power reading to kW using the entity's declared unit.

    An unrecognised unit returns ``None`` rather than a guess: a wrongly scaled
    power value is worse than no power value, because everything downstream
    (COP learning, peak tracking, cost reconciliation) trusts it.
    """
    if unit is None:
        # Home Assistant requires a unit on any sensor with a device class, so
        # a missing one means the entity is not really a power sensor.
        return None
    factor = POWER_UNIT_TO_KW.get(str(unit).strip())
    if factor is None:
        return None
    return value * factor


#: State strings that mean "yes". Deliberately wide: the same configuration
#: slot may be filled with a ``binary_sensor`` (``on``/``off``), a ``switch``,
#: an ``input_boolean``, or a plain ``sensor`` carrying whatever word the
#: source integration happened to publish. Being strict here would not make a
#: wrong answer less likely — it would only turn a readable flag into
#: ``not_boolean`` for half the users who configure it correctly.
BOOL_TRUE: frozenset[str] = frozenset(
    {
        "on",
        "true",
        "yes",
        "1",
        "home",
        "open",
        "opened",
        "heat",
        "heating",
        "detected",
        "active",
        "enable",
        "enabled",
        "online",
        "connected",
        "running",
    }
)

#: State strings that mean "no".
BOOL_FALSE: frozenset[str] = frozenset(
    {
        "off",
        "false",
        "no",
        "0",
        "not_home",
        "closed",
        "clear",
        "idle",
        "inactive",
        "disable",
        "disabled",
        "offline",
        "disconnected",
        "standby",
        "stopped",
    }
)


def parse_bool(raw: Any) -> bool | None:
    """Interpret a state string as a flag, or ``None`` if it is not one.

    Numbers are read as "non-zero means yes". That is not a guess: the Tuya
    fault DP is a code where zero means healthy and anything else is a fault,
    and the source integration's own mapping is literally ``value != 0``. A
    user who points a flag slot at the raw code sensor instead of the derived
    binary sensor must get the same answer as the binary sensor would give.
    The same rule reads the defrost DP (0/1) correctly.

    Kept module-level rather than buried in ``read_bool`` so callers with
    their own extra rule on top — the external-heat override reads a flue
    *temperature* as a threshold, which is a heuristic about one sensor and
    emphatically not a general boolean — can reuse the vocabulary without
    inheriting a numeric rule that would be wrong for them.
    """
    if isinstance(raw, bool):
        return raw
    token = str(raw).strip().lower()
    if token in BOOL_TRUE:
        return True
    if token in BOOL_FALSE:
        return False
    try:
        return float(token) != 0.0
    except (TypeError, ValueError):
        return None


class InputReader:
    """Reads configured entities, applying the freshness and unit guards."""

    def __init__(
        self,
        hass: Any,
        config: dict[str, Any],
        *,
        enabled: bool = True,
        scale: float = 1.0,
        now: Any = None,
    ) -> None:
        self.hass = hass
        self.config = config
        self.enabled = bool(enabled)
        self.scale = float(scale)
        self._now = now
        self.health = InputHealth()

    def _utcnow(self) -> datetime:
        if callable(self._now):
            return self._now()
        from homeassistant.util import dt as dt_util

        return dt_util.utcnow()

    def _age_minutes(self, state: Any) -> float | None:
        """Minutes since the sensor last reported, or ``None`` if not knowable.

        ``last_reported`` is preferred where Home Assistant provides it:
        ``last_updated`` only moves when the state *object* changes, so a live
        sensor re-reporting an unchanged value — a stable tank overnight — was
        flagged stale while a genuinely dead sensor looked no different. A dead
        sensor stops reporting too, so the fail-closed intent is preserved.
        """
        stamp = (
            getattr(state, "last_reported", None)
            or getattr(state, "last_updated", None)
            or getattr(state, "last_changed", None)
        )
        if not isinstance(stamp, datetime):
            return None
        now = self._utcnow()
        if stamp.tzinfo is None or now.tzinfo is None:
            # Mixing naive and aware datetimes raises; without a comparable
            # pair the age is unknown, which is not the same as "fresh".
            return None
        return max(0.0, (now - stamp).total_seconds() / 60.0)

    def _begin(
        self,
        key: str,
        max_age_minutes: float | _Unbounded | None,
        entity_id: str | None,
    ) -> tuple[InputReading, Any]:
        """Resolve the entity and reject the states no reader can use.

        The half of a read that is identical whether the value turns out to
        be a number, a word or a flag: which entity, which age limit, and the
        three ways a read fails before its content is even looked at. Shared
        so that a string input cannot quietly acquire different rules about
        ``unavailable`` from a temperature.

        Returns ``(reading, state)``; ``state`` is ``None`` exactly when
        ``reading.problem`` has already been set and the caller should record
        and return it as-is.
        """
        entity_id = entity_id if entity_id is not None else self.config.get(key)
        if max_age_minutes is UNBOUNDED:
            # Recorded as "no limit" rather than as a very large one, so the
            # diagnostics say what is actually true about this read.
            limit: float | None = None
        elif max_age_minutes is not None:
            limit = float(max_age_minutes)
        else:
            limit = max_age_for(key, self.scale)
        reading = InputReading(
            key=key, entity_id=entity_id, max_age_minutes=limit
        )

        if not entity_id:
            reading.problem = "not_configured"
            return reading, None

        state = self.hass.states.get(entity_id)
        if state is None:
            reading.problem = "missing_entity"
            return reading, None

        raw = getattr(state, "state", None)
        if raw is None or str(raw).lower() in _INVALID_STATES:
            reading.problem = "unavailable"
            return reading, None

        return reading, state

    def _age_gate(self, reading: InputReading, state: Any) -> None:
        """Record the reading's age and flag it stale when over the limit."""
        age = self._age_minutes(state)
        reading.age_minutes = age
        limit = reading.max_age_minutes
        if self.enabled and limit is not None and age is not None and age > limit:
            # Keep the content populated so a caller that explicitly wants the
            # last known value can still degrade gracefully, but mark it so the
            # default path treats it as absent.
            reading.problem = "stale"
            _LOGGER.debug(
                "Input %s (%s) is %.0f min old, over its %.0f min limit; "
                "treating as missing",
                reading.key,
                reading.entity_id,
                age,
                limit,
            )

    def read(
        self,
        key: str,
        *,
        max_age_minutes: float | _Unbounded | None = None,
        entity_id: str | None = None,
    ) -> InputReading:
        """Read one configured numeric entity.

        ``key`` is the configuration key, which also selects the age limit.
        """
        reading, state = self._begin(key, max_age_minutes, entity_id)
        if state is None:
            return self.health.record(reading)

        try:
            value = float(getattr(state, "state", None))
        except (TypeError, ValueError):
            reading.problem = "not_numeric"
            return self.health.record(reading)

        reading.value = value
        self._age_gate(reading, state)
        return self.health.record(reading)

    def read_state(
        self,
        key: str,
        *,
        max_age_minutes: float | _Unbounded | None = None,
        entity_id: str | None = None,
        valid: Any = None,
    ) -> InputReading:
        """Read one configured entity whose state is a word, not a number.

        The same contract as :meth:`read` in every respect that matters —
        the same problems, the same age limit from ``INPUT_MAX_AGE_MINUTES``,
        the same ``InputHealth`` record — with the content landing in
        ``text`` instead of ``value``. An operating mode nobody has reported
        for an hour is not evidence about the pump's current state, and
        pretending otherwise is the same mistake as trusting a flatlined
        thermometer.

        ``valid``, when given, is either a container of acceptable states
        (compared case-insensitively) or a predicate. A state outside it is
        reported as ``unknown_value`` rather than passed on, so a caller
        cannot mistake an unrecognised word for a meaningful one. Staleness
        outranks it: an old unrecognised value is stale first.
        """
        reading, state = self._begin(key, max_age_minutes, entity_id)
        if state is None:
            return self.health.record(reading)

        reading.text = str(getattr(state, "state", "")).strip()
        self._age_gate(reading, state)
        if reading.problem is None and valid is not None:
            if callable(valid):
                accepted = bool(valid(reading.text))
            else:
                accepted = reading.text.lower() in {
                    str(v).strip().lower() for v in valid
                }
            if not accepted:
                reading.problem = "unknown_value"
        return self.health.record(reading)

    def read_bool(
        self,
        key: str,
        *,
        max_age_minutes: float | _Unbounded | None = None,
        entity_id: str | None = None,
    ) -> InputReading:
        """Read one configured entity as a flag.

        A thin layer over :meth:`read_state` so a defrost, online or fault
        signal inherits the freshness discipline rather than being read by
        hand. ``flag`` carries the interpretation; ``text`` keeps the word it
        came from, because "which state did it actually report" is the first
        question asked of a flag that is behaving oddly.
        """
        reading = self.read_state(
            key, max_age_minutes=max_age_minutes, entity_id=entity_id
        )
        if reading.text is None:
            return reading
        flag = parse_bool(reading.text)
        if flag is None:
            if reading.problem is None:
                reading.problem = "not_boolean"
            return reading
        # Set even on a stale reading, mirroring ``read`` keeping ``value``:
        # ``ok`` is already False, and a caller that deliberately wants the
        # last known flag must be able to reach it.
        reading.flag = flag
        return reading

    def read_power_kw(self, key: str) -> InputReading:
        """Read a power entity and normalise it to kW."""
        reading = self.read(key)
        if reading.value is None:
            return reading
        state = self.hass.states.get(reading.entity_id)
        unit = None
        attributes = getattr(state, "attributes", None)
        if attributes is not None:
            try:
                unit = attributes.get("unit_of_measurement")
            except AttributeError:  # pragma: no cover - defensive
                unit = None
        converted = normalize_power_kw(reading.value, unit)
        if converted is None:
            reading.value = None
            if reading.problem is None:
                reading.problem = "unknown_unit"
            return reading
        reading.value = converted
        return reading

    def value(self, key: str, default: float | None = None) -> float | None:
        """Convenience: the usable value for a key, or ``default``."""
        reading = self.health.readings.get(key)
        if reading is None or not reading.ok:
            return default
        return reading.value

    def text(self, key: str, default: str | None = None) -> str | None:
        """Convenience: the usable state string for a key, or ``default``."""
        reading = self.health.readings.get(key)
        if reading is None or not reading.ok:
            return default
        return reading.text

    def flag(self, key: str, default: bool | None = None) -> bool | None:
        """Convenience: the usable flag for a key, or ``default``."""
        reading = self.health.readings.get(key)
        if reading is None or not reading.ok or reading.flag is None:
            return default
        return reading.flag


def stale_summary(health: InputHealth) -> str:
    """One-line description for the diagnostic entity's state."""
    stale = health.stale_keys
    missing = health.missing_keys
    if not stale and not missing:
        return "ok"
    parts = []
    if stale:
        parts.append(f"{len(stale)} stale")
    if missing:
        parts.append(f"{len(missing)} missing")
    return ", ".join(parts)


def age_of(state: Any, now: datetime) -> timedelta | None:
    """Age of a Home Assistant state object, for callers outside the reader."""
    stamp = getattr(state, "last_updated", None) or getattr(
        state, "last_changed", None
    )
    if not isinstance(stamp, datetime):
        return None
    if stamp.tzinfo is None or now.tzinfo is None:
        return None
    return now - stamp
