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

**Off and unload** restore 0 through :mod:`off_restore`, the shared hook this
module registers with, which reports the restore back so the record above
names the 0 as the last write; the arm itself writes nothing while the mode
is off.
"""
from __future__ import annotations

import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.util import dt as dt_util

from . import off_restore
from .const import DOMAIN, HEAT_CURVE_KIND_OFFSET
from .payload import CurrentAction, Ecl110Payload
from .inputs import NumberReading, number_reading, setpoint_step, write_setpoint
from .log_latch import log_held

_LOGGER = logging.getLogger(__name__)

#: The restore hook's key for this arm.
CONSUMER = "heat_curve"
#: The domains a whole-curve offset is written through.
DOMAINS = ("number", "input_number")
#: A difference in the entity's unit per kelvin. No unit is kelvin: a bare
#: offset number (``luxtronik_shi``'s states K; others state nothing).
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
    if not entity_id or config.heat_curve_target_kind != HEAT_CURVE_KIND_OFFSET:
        return None
    return off_restore.Restorer(entity_id, write_setpoint, neutral=0.0, restored=_restore_recorded)


def _restore_recorded(entry: Any, value: float) -> None:
    """The restore wrote ``value``: the entity's last instruction, a new target.

    W2 and W3 then judge the next publish against the restore's write, never
    against the plan's write before it, which would hold a re-enable in grace
    or latch W3 on a healthy entity. Not a W4 write: the guard counts the
    arm's own loop.
    """
    held = state_for(entry)
    held.written, held.written_at, held.misses = value, time.monotonic(), 0


off_restore.register_consumer(CONSUMER, _restorer)


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
        await write_displace(hass, entry, config, displace_int)


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
    if not await off_restore.async_arm(hass, entry, config, CONSUMER):
        return False
    try:
        await write_setpoint(hass, entity_id, target)
    except Exception as err:  # noqa: BLE001 - the entity never breaks a cycle
        log_held(entry, "heat_curve_write", True, "Heat-curve entity %s write failed: %s", entity_id, err)
        return False
    log_held(entry, "heat_curve_write", False)
    held.written, held.written_at = target, now
    held.writes.append(now)
    return True


def diagnostics(entry: Any, config: Any) -> dict[str, Any]:
    """The entity arm's record, for the diagnostics bundle.

    Counts and numbers only: the entity, kind and band are the config
    section's, so nothing the install names is repeated here.
    """
    held = _STATES.get(entry)
    return {
        "written": None if held is None else held.written,
        "misses": 0 if held is None else held.misses,
        "writes_24h": 0 if held is None else len(held.writes),
        "write_cap_per_day": write_cap_per_day(config),
        "restore": off_restore.diagnostics(entry),
    }
