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


@dataclass
class InputReading:
    """One attempt to read a configured entity."""

    key: str
    entity_id: str | None
    value: float | None = None
    age_minutes: float | None = None
    max_age_minutes: float | None = None
    #: ``None`` when the read succeeded, otherwise why it did not.
    problem: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the value may be used."""
        return self.value is not None and self.problem is None

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

    def read(
        self,
        key: str,
        *,
        max_age_minutes: float | None = None,
        entity_id: str | None = None,
    ) -> InputReading:
        """Read one configured numeric entity.

        ``key`` is the configuration key, which also selects the age limit.
        """
        entity_id = entity_id if entity_id is not None else self.config.get(key)
        limit = (
            max_age_minutes
            if max_age_minutes is not None
            else max_age_for(key, self.scale)
        )
        reading = InputReading(
            key=key, entity_id=entity_id, max_age_minutes=limit
        )

        if not entity_id:
            reading.problem = "not_configured"
            return self.health.record(reading)

        state = self.hass.states.get(entity_id)
        if state is None:
            reading.problem = "missing_entity"
            return self.health.record(reading)

        raw = getattr(state, "state", None)
        if raw is None or str(raw).lower() in _INVALID_STATES:
            reading.problem = "unavailable"
            return self.health.record(reading)

        try:
            value = float(raw)
        except (TypeError, ValueError):
            reading.problem = "not_numeric"
            return self.health.record(reading)

        age = self._age_minutes(state)
        reading.age_minutes = age
        reading.value = value

        if self.enabled and limit is not None and age is not None and age > limit:
            # Keep ``value`` populated so a caller that explicitly wants the
            # last known value can still degrade gracefully, but mark it so the
            # default path treats it as absent.
            reading.problem = "stale"
            _LOGGER.debug(
                "Input %s (%s) is %.0f min old, over its %.0f min limit; "
                "treating as missing",
                key,
                entity_id,
                age,
                limit,
            )

        return self.health.record(reading)

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
