"""The heat-curve displace's one owner: its MQTT arms and its entity arm.

``async_publish_ecl110_command`` forms the one integer every displace passes
(the plan, the fixed modes, boost, the peak guard and the learned curve bias
reach it there) and hands it to :func:`publish`, which fans it out: the ECL110
``/set`` topic and legacy JSON topic, unchanged, then a Home Assistant
``number`` the user names (R10-GENERIC-HEAT-CURVE, design note
``design/R10-GENERIC-HEAT-CURVE``).

**Kind ``offset`` (the first build).** The entity is a zero-neutral, volatile
whole-curve offset, written as a temperature *difference* in the entity's own
unit: identity for kelvin and Celsius, x9/5 for Fahrenheit, any other unit
refused. Never through the absolute set-point helpers, which read a kelvin
entity's -2 as -275.15 degC. Bounded to +-``heat_curve_offset_band_k`` and to
the entity's own range; an entity whose range excludes 0 is no offset, and is
refused at save and again here.

**Write policy (W1-W6), for a volatile target:** no call while the reading is
within half a step of the target (W1); every write is recorded and a reading
inside :data:`HELD_GRACE_S` proves nothing, after it the first miss is written
once more (W2); a second miss for the same target latches a warning and stops
rewriting it until the target changes or the reading holds (W3); more than
``2 x 1440 / optimization_interval`` writes in 24 h is a loop bug, refused and
latched (W4); the MQTT arms' integer is sent (W5), saturated and latched once
where the entity's range is narrower (W6).

**Kind ``persistent``** (R10-GENERIC-HEAT-CURVE-PERSISTENT, design note
``design/R10-GENERIC-HEAT-CURVE-PERSISTENT``). The entity is a curve
parameter the controller stores, so every write wears it. The arm writes the
baseline ``b`` plus the displace as a difference, on the entity's step,
within ``b`` +-``heat_curve_persistent_band_k`` and the entity's range (I1).
``b`` is the reading :mod:`off_restore` captured with the entity before the
first write; a reading that is neither the last write nor the one before it,
after the grace, is the user's edit, and ``b`` moves with it, bounded to the
entity's range (:func:`off_restore.async_rebaseline`). Writes are held for
``heat_curve_persistent_min_dwell_minutes`` after the last one and capped at
``heat_curve_persistent_writes_per_day`` a local day, restores included, one
always kept back for the restore (I2); the record of both lives in
off_restore's per-entry record, so it survives a restart. W4 is not consulted.

**Off and unload** restore through :mod:`off_restore`, the shared hook this
module registers with: 0 for kind ``offset``, the captured baseline for kind
``persistent``. The hook reports the restore back so the record above names
it as the last write; the arm itself writes nothing while the mode is off.
"""
from __future__ import annotations

import json
import logging
import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.util import dt as dt_util

from . import off_restore
from .const import DOMAIN, HEAT_CURVE_KIND_PERSISTENT
from .payload import CurrentAction, Ecl110Payload
from .inputs import NumberReading, number_reading, setpoint_step, write_setpoint
from .log_latch import log_held

_LOGGER = logging.getLogger(__name__)

#: The restore hook's key for this arm.
CONSUMER = "heat_curve"
#: The domains a whole-curve offset is written through.
DOMAINS = ("number", "input_number")
#: A difference in the entity's unit per kelvin. No unit is kelvin: a bare
#: offset number (one integration's states K; others state nothing).
_DELTA_PER_K = {
    "K": 1.0, "°C": 1.0, "C": 1.0, "degC": 1.0, "": 1.0,
    "°F": 1.8, "F": 1.8, "degF": 1.8,
}
#: W2's grace. Not the pump arbiter's ``ECHO_GRACE_S`` (20 s, the Tuya fork's
#: 8 s sent-value window): an offset number is read back by its integration's
#: own poll, Home Assistant's default 30 s scan for a polled entity, so two
#: polls and margin. The arm runs once per publish, minutes apart, so the
#: grace only decides a publish that follows another within it (a mode change
#: right after a cycle).
HELD_GRACE_S = 90.0
_DAY_S = 86400.0


@dataclass
class HeatCurveState:
    """Per config entry, the entity arm's record (``pump_arbiter.state_for``'s shape)."""

    #: The last value written, in the entity's unit, and its monotonic stamp.
    written: float | None = None
    written_at: float = 0.0
    #: Consecutive misses of ``written`` after the grace.
    misses: int = 0
    #: Monotonic stamps of the writes in the last 24 h (W4).
    writes: deque[float] = field(default_factory=deque)


_STATES: WeakKeyDictionary[Any, HeatCurveState] = WeakKeyDictionary()


def state_for(entry: Any) -> HeatCurveState:
    held = _STATES.get(entry)
    if held is None:
        held = _STATES[entry] = HeatCurveState()
    return held


def _restorer(config: Any) -> off_restore.Restorer | None:
    entity_id = config.heat_curve_displace_entity
    if not entity_id:
        return None
    if config.heat_curve_target_kind == HEAT_CURVE_KIND_PERSISTENT:
        return off_restore.Restorer(entity_id, write_setpoint, baseline_of=_baseline_reading,
                                    restored=_persistent_restored)
    # EntryConfig reads any other kind as offset.
    return off_restore.Restorer(entity_id, write_setpoint, neutral=0.0, restored=_restore_recorded)


def _restore_recorded(entry: Any, _entity_id: str, value: float) -> None:
    """The restore wrote ``value``: the entity's last instruction, a new target.

    W2 and W3 then judge the next publish against the restore's write, never
    against the plan's write before it, which would hold a re-enable in grace
    or latch W3 on a healthy entity. Not a W4 write: the guard counts the
    arm's own loop.
    """
    held = state_for(entry)
    held.written, held.written_at, held.misses = value, time.monotonic(), 0


def _baseline_reading(hass: Any, entity_id: str) -> float | None:
    """Kind persistent's baseline: the entity's own reading, before the first write."""
    reading = number_reading(hass, entity_id)
    return None if reading is None else reading.value


def _persistent_restored(entry: Any, entity_id: str, value: float) -> None:
    """The restore wrote the baseline: the last write, counted to its local day.

    Persisted by the restore's own save. A restore of an entity this record
    does not name (rule R, after the option changed) is not this record's.
    """
    state = off_restore.consumer_state(entry, CONSUMER)
    if state.get("entity_id") != entity_id:
        return
    _record_write(state, value, dt_util.utcnow(), state.get("written"))


off_restore.register_consumer(CONSUMER, _restorer, write=write_setpoint)


def ecl110_legacy_payload(
    reason: str,
    heat_pump_on: bool,
    displace_int: int,
    current_action: CurrentAction,
) -> Ecl110Payload:
    """The legacy JSON command body, over the action passed in.

    Takes ``current_action`` as a value rather than reading it off the
    coordinator: a module-level helper handed ``self`` would keep every
    reference it moved -- ``tests/structure.py`` walks only class methods
    and matches ``self.<attr>``, so the seam metric would fall while the
    coupling stood. Same rule as ``plan_step.plan_step_start`` and ``_liquid_fraction``.
    """
    return {
        "source": DOMAIN,
        "reason": reason,
        "timestamp": dt_util.now().isoformat(),
        "command": {
            "type": "ecl110_control",
            "heat_pump_on": bool(heat_pump_on),
            "displace": displace_int,
        },
        "context": {
            "price": current_action.get("price"),
            "mode": current_action.get("mode"),
            "pre_heat_urgency": current_action.get("pre_heat_urgency"),
        },
    }


async def publish_ecl110_topics(
    hass: Any,
    set_topic: str | None,
    command_topic: str | None,
    qos: Any,
    retain: Any,
    displace_int: int,
    legacy_payload: Ecl110Payload,
) -> None:
    """Write the displace command to whichever ECL110 topics are configured.

    Each arm swallows its own MQTT failure, so a broken legacy topic never
    suppresses the direct ``/set`` write that supersedes it.
    """
    if not set_topic and not command_topic:
        return

    # Preferred path: write plain numeric payload directly to /set topic.
    if set_topic:
        try:
            await hass.services.async_call(
                "mqtt",
                "publish",
                {
                    "topic": set_topic,
                    "payload": str(displace_int),
                    "qos": int(qos),
                    "retain": bool(retain),
                },
                blocking=True,
            )
        except Exception as err:
            _LOGGER.error("Error publishing ECL110 direct displace MQTT command: %s", err)

    # Backward compatibility path: optional legacy JSON command topic.
    if command_topic:
        try:
            await hass.services.async_call(
                "mqtt",
                "publish",
                {
                    "topic": command_topic,
                    "payload": json.dumps(legacy_payload),
                    "qos": int(qos),
                    "retain": bool(retain),
                },
                blocking=True,
            )
        except Exception as err:
            _LOGGER.error("Error publishing ECL110 legacy MQTT command: %s", err)


async def publish(
    hass: Any,
    entry: Any,
    config: Any,
    displace_int: int,
    legacy_payload: Ecl110Payload,
    *,
    mode_off: bool = False,
) -> None:
    """Fan one displace out: the MQTT arms first, then the entity arm.

    ``entry`` keys the arm's record and its latches, so the coordinator
    carries no attribute and is not handed in.
    """
    await publish_ecl110_topics(
        hass,
        config.ecl110_displace_set_topic,
        config.ecl110_command_topic,
        config.ecl110_mqtt_qos,
        config.ecl110_mqtt_retain,
        displace_int,
        legacy_payload,
    )
    if config.heat_curve_displace_entity and not mode_off:
        persistent = config.heat_curve_target_kind == HEAT_CURVE_KIND_PERSISTENT
        await (write_persistent if persistent else write_displace)(hass, entry, config, displace_int)


def range_excludes_zero(reading: NumberReading) -> bool:
    """T2: the entity's own declared range leaves 0 out, so it is no offset.

    One rule for the options flow's save and the arm's every write.
    """
    lo, hi = reading.lo, reading.hi
    return (lo is not None and lo > 0.0) or (hi is not None and hi < 0.0)


def offset_target(
    reading: NumberReading | None, displace_k: float, band_k: float
) -> tuple[float | None, str | None, bool]:
    """(target in the entity's unit, why not, saturated by the entity's range).

    Pure over the raw reading: the convert of the entity arm.
    """
    if reading is None or reading.value is None:
        return None, "is unavailable", False
    per_k = _DELTA_PER_K.get(reading.unit)
    if per_k is None:
        return None, f"states unit {reading.unit!r}, not a temperature difference", False
    lo, hi = reading.lo, reading.hi
    if range_excludes_zero(reading):
        return None, f"declares range {lo}..{hi}, which excludes 0: not an offset", False
    banded = max(-band_k, min(band_k, displace_k)) * per_k
    target = banded
    if lo is not None:
        target = max(lo, target)
    if hi is not None:
        target = min(hi, target)
    return target, None, target != banded


def _decide(held: HeatCurveState, target: float, reading: float | None, half_step: float, now: float) -> str | None:
    """The write decision for ``target``: None to write, else why not."""
    if reading is not None and abs(reading - target) <= half_step:
        held.misses = 0
        return "holds"  # W1
    if held.written is None or abs(held.written - target) > half_step:
        held.misses = 0
        return None  # a new target
    if now - held.written_at < HELD_GRACE_S:
        return "in grace"  # W2: a differing reading proves nothing yet
    held.misses += 1
    return "gave up" if held.misses >= 2 else None  # W3 on the second miss


def write_cap_per_day(config: Any) -> int:
    """W4: twice the publishes a day the configured interval makes."""
    return int(2 * 1440 / max(1.0, float(config.optimization_interval)))


async def write_displace(hass: Any, entry: Any, config: Any, displace_int: int) -> bool:
    """The entity arm: write ``displace_int`` K to the offset entity; True when sent.

    Every failure is latched on ``entry`` and swallowed: the cycle and the
    MQTT arms are never affected by the entity.
    """
    entity_id = config.heat_curve_displace_entity
    reading = number_reading(hass, entity_id)
    domain = entity_id.split(".", 1)[0]
    target: float | None = None
    why: str | None = f"is a {domain}, not a number"
    saturated = False
    if domain in DOMAINS:
        target, why, saturated = offset_target(reading, float(displace_int), float(config.heat_curve_offset_band_k))
    if target is None or reading is None:
        log_held(entry, "heat_curve_entity", True, "Heat-curve entity %s %s: not written", entity_id, why)
        return False
    log_held(entry, "heat_curve_entity", False)
    log_held(entry, "heat_curve_saturated", saturated,
             "Heat-curve entity %s range narrower than the displace %s K: sending %s",
             entity_id, displace_int, target)
    held = state_for(entry)
    now = time.monotonic()
    step = setpoint_step(hass, entity_id)
    decision = _decide(held, target, reading.value, step / 2.0, now)
    if log_held(entry, "heat_curve_not_held", decision == "gave up",
                "Heat-curve entity %s does not hold %s after a rewrite: not resent until the target changes",
                entity_id, target) or decision is not None:
        return False
    while held.writes and now - held.writes[0] > _DAY_S:
        held.writes.popleft()
    cap = write_cap_per_day(config)
    if log_held(entry, "heat_curve_write_cap", len(held.writes) >= cap,
                "Heat-curve entity %s: %d writes in 24 h reached the guard, refused", entity_id, cap):
        return False
    if not await off_restore.async_arm(hass, entry, config, CONSUMER) \
            or not await _send(hass, entry, entity_id, target):
        return False
    held.written, held.written_at = target, now
    held.writes.append(now)
    return True


async def _send(hass: Any, entry: Any, entity_id: str, target: float) -> bool:
    """The one service call of either kind's arm; a failure latched, never raised."""
    try:
        await write_setpoint(hass, entity_id, target)
    except Exception as err:  # noqa: BLE001 - the entity never breaks a cycle
        log_held(entry, "heat_curve_write", True, "Heat-curve entity %s write failed: %s", entity_id, err)
        return False
    log_held(entry, "heat_curve_write", False)
    return True


def _age_s(state: dict[str, Any], now: Any) -> float:
    """Seconds since the record's last write; inf with none.

    A stamp ahead of the clock (a clock stepped back) reads negative, so the
    grace and the dwell hold until the clock passes it again (ghcp-r4).
    """
    stamp = dt_util.parse_datetime(str(state.get("written_at") or ""))
    return math.inf if stamp is None else (now - stamp).total_seconds()


def _record_write(state: dict[str, Any], value: float, now: Any, before: float | None) -> None:
    """One write to the entity, plan or restore, ahead of it: the record and the day's count.

    ``previous`` is what the entity held before (``before``), so a write that
    never landed reads as missed, never as the user's edit.
    """
    state.update(day=_local_day(now), count=writes_today(state, now) + 1,
                 previous=before, written=value, written_at=now.isoformat())


def _local_day(now: Any) -> str:
    return dt_util.as_local(now).date().isoformat()


def writes_today(state: dict[str, Any], now: Any) -> int:
    """The record's writes on the local day of ``now``; a record with no count has none."""
    return int(state.get("count") or 0) if state.get("day") == _local_day(now) else 0


def classify(state: dict[str, Any], reading: float, half_step: float, now: Any) -> str:
    """What the reading says of the last write: ours, in grace, missed or the user's edit.

    ``missed``: it still reads the write before (a write-ahead crash, or the
    controller refused it); ``edit``: neither, after the grace.
    """
    written = state.get("written")
    if written is None or abs(reading - written) <= half_step:
        return "ours"
    if _age_s(state, now) < HELD_GRACE_S:
        return "in grace"
    previous = state.get("previous")
    return "missed" if previous is not None and abs(reading - previous) <= half_step else "edit"


def persistent_target(
    baseline: float, displace_k: float, band_k: float, reading: NumberReading, per_k: float, step: float
) -> tuple[float, bool]:
    """(target in the entity's unit, saturated by its range): ``b + delta`` within the band (I1).

    The difference is whole steps toward the baseline, so rounding never
    leaves the band; the range then bounds it.
    """
    delta = max(-band_k, min(band_k, displace_k)) * per_k
    banded = baseline + math.copysign(math.floor(abs(delta) / step + 1e-9) * step, delta)
    target = _within_range(banded, reading)
    return target, target != banded


def _within_range(value: float, reading: NumberReading) -> float:
    """``value`` bounded to the entity's declared range, each side that it declares."""
    if reading.lo is not None:
        value = max(reading.lo, value)
    if reading.hi is not None:
        value = min(reading.hi, value)
    return value


def outside_own_range(reading: NumberReading) -> bool:
    """P7: a stored parameter reading outside its own declared range is not displaced.

    One rule for the options flow's save and the persistent arm's every write.
    """
    value, lo, hi = reading.value, reading.lo, reading.hi
    return value is not None and ((lo is not None and value < lo) or (hi is not None and value > hi))


def _persistent_refusal(entity_id: str, reading: NumberReading | None) -> tuple[float | None, str | None]:
    """(difference per kelvin, None), or (None, why the entity is not written)."""
    domain = entity_id.partition(".")[0]
    if domain not in DOMAINS:
        return None, f"is a {domain}, not a number"
    if reading is None or reading.value is None:
        return None, "is unavailable"
    per_k = _DELTA_PER_K.get(reading.unit)
    if per_k is None:
        return None, f"states unit {reading.unit!r}, not a temperature"
    if outside_own_range(reading):
        return None, f"reads {reading.value}, outside its own range {reading.lo}..{reading.hi}"
    return per_k, None


async def write_persistent(hass: Any, entry: Any, config: Any, displace_int: int) -> bool:
    """Kind persistent's arm: write baseline + ``displace_int`` K; True when sent.

    Every failure is latched on ``entry`` and swallowed, as the offset arm's.
    """
    entity_id = config.heat_curve_displace_entity
    reading = number_reading(hass, entity_id)
    per_k, why = _persistent_refusal(entity_id, reading)
    if log_held(entry, "heat_curve_entity", per_k is None, "Heat-curve entity %s %s: not written", entity_id, why) \
            or per_k is None or reading is None or reading.value is None:
        return False
    armed = await off_restore.async_armed_entry(hass, entry, CONSUMER)
    if armed is not None and armed["entity_id"] != entity_id:
        armed = None  # the arm restores the recorded entity first (rule R)
    state = await off_restore.async_consumer_state(hass, entry, CONSUMER)
    if state.get("entity_id") != entity_id:  # another entity: only the day's count carries over
        kept: dict[str, Any] = {key: state[key] for key in ("day", "count") if key in state}
        state.clear()
        state.update(kept, entity_id=entity_id)
    step = setpoint_step(hass, entity_id)
    now = dt_util.utcnow()
    baseline = reading.value if armed is None else armed["value"]
    # "in grace" needs no exit of its own: the dwell, 15 min at least, holds
    # every write inside the 90 s grace.
    seen = "ours" if armed is None else classify(state, reading.value, step / 2.0, now)
    if seen == "edit":
        # The edit's own difference, bounded to what the entity holds: off
        # restores this baseline, and a value outside the range is refused.
        baseline = _within_range(reading.value - (state["written"] - baseline), reading)
        await off_restore.async_rebaseline(hass, entry, CONSUMER, entity_id, baseline)
        _LOGGER.info("Heat-curve entity %s was set to %s by hand: its baseline is now %s",
                     entity_id, reading.value, baseline)
        state["written"] = reading.value
    target, saturated = persistent_target(
        baseline, float(displace_int), float(config.heat_curve_persistent_band_k), reading, per_k, step)
    log_held(entry, "heat_curve_saturated", saturated,
             "Heat-curve entity %s range narrower than the displace %s K: sending %s",
             entity_id, displace_int, target)
    return await _write_persistent_target(hass, entry, config, state, reading.value, target, seen)


async def _write_persistent_target(
    hass: Any, entry: Any, config: Any, state: dict[str, Any], reading: float, target: float, seen: str
) -> bool:
    """W1, the dwell, the W3 latch and the day's budget, then arm and write ahead."""
    entity_id = config.heat_curve_displace_entity
    half_step = setpoint_step(hass, entity_id) / 2.0
    now = dt_util.utcnow()
    if abs(reading - target) <= half_step:
        state["misses"] = 0
        return False  # W1
    if _age_s(state, now) < 60.0 * float(config.heat_curve_persistent_min_dwell_minutes):
        return False  # the dwell
    # The same baseline and displace give the same target, to the bit.
    retry = seen == "missed" and state["written"] == target
    if log_held(entry, "heat_curve_not_held", retry and bool(state.get("misses")),
                "Heat-curve entity %s does not hold %s after a rewrite: not resent until the target changes",
                entity_id, target):
        return False
    # One write is always kept back for the restore that takes it home (I2).
    budget = int(config.heat_curve_persistent_writes_per_day)
    if writes_today(state, now) + 2 > budget:
        today = _local_day(now)
        if state.get("refused_day") != today:
            state["refused_day"] = today
            _LOGGER.info("Heat-curve entity %s: %d writes a day reached, refused until tomorrow",
                         entity_id, budget)
        return False
    if not await off_restore.async_arm(hass, entry, config, CONSUMER):
        return False
    _record_write(state, target, now, reading)
    state["misses"] = int(retry)
    await off_restore.async_save_state(hass, entry)
    return await _send(hass, entry, entity_id, target)


def diagnostics(entry: Any, config: Any) -> dict[str, Any]:
    """The entity arm's record, for the diagnostics bundle.

    Counts and numbers only: the entity, kind and band are the config
    section's, so nothing the install names is repeated here.
    """
    if config.heat_curve_target_kind == HEAT_CURVE_KIND_PERSISTENT:
        held_record = off_restore.consumer_state(entry, CONSUMER)
        return {
            "written": held_record.get("written"),
            "misses": int(held_record.get("misses", 0)),
            "writes_today": writes_today(held_record, dt_util.utcnow()),
            "writes_per_day": int(config.heat_curve_persistent_writes_per_day),
            "restore": off_restore.diagnostics(entry),
        }
    held = _STATES.get(entry)
    return {
        "written": None if held is None else held.written,
        "misses": 0 if held is None else held.misses,
        "writes_24h": 0 if held is None else len(held.writes),
        "write_cap_per_day": write_cap_per_day(config),
        "restore": off_restore.diagnostics(entry),
    }
