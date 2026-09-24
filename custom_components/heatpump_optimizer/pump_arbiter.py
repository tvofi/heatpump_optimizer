"""The pump-duty arbiter: which duty the pump serves, step by step.

The plan decides per 15-minute step whether the pump heats the house, the
tank, both or neither. Without this module that decision never reaches the
pump: it runs its own two thermostats and serves whichever demand it sees. So
a planned hot-water-only step in a warm house turns into space heating.

**What it writes.** One logic over three optional entity slots the options
flow already has: the pump's operating-mode select
(``heat_pump_mode_entity``), its hot-water set-point (``dhw_setpoint_entity``)
and its space set-point (``space_setpoint_entity``). Per step:

=============  ==========================  =============  ===============
plan step      mode                        hot water set  space set
=============  ==========================  =============  ===============
hot water only DHW only, if offered        configured     suitable, or
                                                          the gate value
anything else  Heating + DHW               configured     suitable
=============  ==========================  =============  ===============

*Configured* is the hot-water set-point from the config flow
(``dhw_setpoint``), never a literal. *Suitable* is the plan's own number:
the weather-curve supply temperature for a flow set-point, or the step's
planned room temperature for an indoor one. Heating-only is never written:
it blocks the pump's own hot water and its disinfection.

**Two transports, one logic.** The Tuya fork offers a DHW-only mode, so the
mode is the space gate there. The GCHV/Rotenso Modbus package's mode register
offers only Off / Cool + DHW / Heat + DHW, so where the select lists no
DHW-only option the space gate is the space set-point instead, lowered to
the entity's own minimum on hot-water-only steps. Which one applies is read
off the select's ``options``, not configured.

**It never overrides a person.** Every value it writes is recorded. A state
that differs from the record, read more than :data:`ECHO_GRACE_S` after the
write, is a change somebody else made: the Tuya fork forces the sent value
back for 8 s after a write, so a differing reading past that is a real device
report. On one, the arbiter stops writing, turns the "optimizer active"
switch off and raises a repair notice. Turning the switch back on hands
control back and clears the notice; nothing is overridden before that.

**Its own writes are not evidence.** A mode the arbiter wrote must not reach
the next solve as "the pump cannot heat" (:func:`own`), or a DHW-only step
would block space heat for the whole horizon and nothing would ever write
Heating + DHW back.

**Rails.** Hot-water-only is leased: at most :data:`LEASE_MINUTES`, and
:data:`COLD_LEASE_MINUTES` below :data:`COLD_RAIL_C` outdoors. A stale or
missing plan, a fixed-rule mode, an experiment, a boost and the end of the
lease all get the baseline row above. Unloading writes the baseline too.

It acts at step boundaries: a one-minute tick (only while the option is not
off) re-derives the step, since the solve runs every 30 minutes and a plan
step is 15.
"""
from __future__ import annotations

import asyncio
import bisect
import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from . import boost, pump_mode
from .const import (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_PUMP_DUTY_MODE,
    CONF_SPACE_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_UNIT,
    DEFAULT_PUMP_DUTY_MODE,
    DEFAULT_SPACE_SETPOINT_UNIT,
    DOMAIN,
    MODE_AUTO,
    MODE_ECONOMY,
    MODE_OFF,
    PUMP_DUTY_MODES,
)
from .inputs import state_unit, temperature_c, temperature_from_c
from .repairs import _write_setpoint
from .setpoint_check import _read_setpoint, create_issue
from .store import QuarantiningStore

_LOGGER = logging.getLogger(__name__)

DUTY_OFF, DUTY_CONTROL = PUMP_DUTY_MODES[0], PUMP_DUTY_MODES[2]

#: Past the fork's 8 s sent-value window and its 1 s local debounce, with
#: room for a cloud round trip: a differing reading after this is the device.
ECHO_GRACE_S = 20.0
LEASE_MINUTES = 90.0
COLD_LEASE_MINUTES = 30.0
COLD_RAIL_C = -10.0
#: The floor of a flow set-point gate when the entity declares no minimum;
#: the GCHV water set-points accept 25 degC and up.
FLOW_GATE_C = 25.0
SETPOINT_TOLERANCE = 0.3
ISSUE_MANUAL = "pump_manual_change"
_STORE_VERSION = 1
_TICK = timedelta(minutes=1)


@dataclass(frozen=True)
class PumpCommand:
    """What the pump should be told for one step; ``None`` writes nothing."""

    mode: str | None
    dhw_setpoint: float | None
    space_setpoint: float | None


@dataclass
class ArbiterState:
    """Per-coordinator record: what was written, when, and why it stopped."""

    #: slot -> (value written, when); the ownership record.
    written: dict[str, tuple[Any, datetime]] = field(default_factory=dict)
    manual: str | None = None
    dhw_since: datetime | None = None
    last_duty: str | None = None
    loaded: bool = False
    unsubs: list[Any] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_STATES: WeakKeyDictionary[Any, ArbiterState] = WeakKeyDictionary()
_SLOTS = ("mode", "dhw_setpoint", "space_setpoint")


def _entities(config: Any) -> dict[str, Any]:
    """Slot -> the configured entity id; the three writable pump slots."""
    return {
        "mode": config.get(CONF_HEAT_PUMP_MODE_ENTITY),
        "dhw_setpoint": config.get(CONF_DHW_SETPOINT_ENTITY),
        "space_setpoint": config.get(CONF_SPACE_SETPOINT_ENTITY),
    }


def _flow(config: Any) -> bool:
    return config.get(CONF_SPACE_SETPOINT_UNIT, DEFAULT_SPACE_SETPOINT_UNIT) == "flow"


def state_for(coord: Any) -> ArbiterState:
    held = _STATES.get(coord)
    if held is None:
        held = ArbiterState()
        _STATES[coord] = held
    return held


def duty_mode(config: Any) -> str:
    mode = config.get(CONF_PUMP_DUTY_MODE, DEFAULT_PUMP_DUTY_MODE)
    return mode if mode in PUMP_DUTY_MODES else DUTY_OFF


def step_duty(result: Any, now: datetime, on_kw: float) -> str | None:
    """``dhw``, ``space``, ``both`` or ``idle`` for the plan step covering now."""
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] > timedelta(minutes=15)):
        return None
    space = list(result.power_schedule or [])
    dhw = list(getattr(result, "dhw_power_schedule", None) or [])
    s_on = i < len(space) and space[i] >= on_kw
    d_on = i < len(dhw) and dhw[i] > 0.1
    return {(True, True): "both", (True, False): "space", (False, True): "dhw"}.get(
        (s_on, d_on), "idle"
    )


def own(coord: Any, signals: Any) -> Any:
    """``signals`` with the arbiter's own mode marked as not a block."""
    written = state_for(coord).written.get("mode")
    if duty_mode(coord._config) != DUTY_CONTROL or written is None:
        return signals
    if signals.mode.key != written[0]:
        return signals
    return replace(signals, mode_owned=True)


def _state(coord: Any, slot: str) -> Any:
    entity = _entities(coord._config)[slot]
    return coord.hass.states.get(entity) if entity else None


def _option_for(state: Any, key: str) -> str | None:
    options = (getattr(state, "attributes", None) or {}).get("options") or ()
    return next((o for o in options if pump_mode.resolve(o) == key), None)


def _bounded(state: Any, value: float | None, floor: float = -1e9) -> float | None:
    """``value`` (degC) inside the entity's own range, on a half degree."""
    if value is None or state is None:
        return None
    attrs = getattr(state, "attributes", None) or {}
    unit = state_unit(state)
    low = temperature_c(attrs.get("min"), unit)
    high = temperature_c(attrs.get("max"), unit)
    value = max(value, floor, low if low is not None else floor)
    value = min(value, high) if high is not None else value
    return round(value * 2.0) / 2.0


def _space_target(coord: Any, result: Any, now: datetime) -> float | None:
    """The plan's own space set-point: the curve supply, or the room target."""
    state = _state(coord, "space_setpoint")
    if _flow(coord._config):
        outdoor = float(coord._current_state.outdoor_temperature)
        return _bounded(state, coord._thermal_model.curve_flow_temp(outdoor), FLOW_GATE_C)
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    points = list(getattr(result, "optimal_setpoints", None) or [])
    return _bounded(state, points[i] if 0 <= i < len(points) else None)


def desired(coord: Any, duty: str | None, now: datetime) -> PumpCommand:
    """The row of the module table for ``duty``; ``None`` is the baseline."""
    result = getattr(coord, "_optimization_result", None)
    mode_state = _state(coord, "mode")
    space_state = _state(coord, "space_setpoint")
    dhw = _bounded(_state(coord, "dhw_setpoint"), float(coord._thermal_params.dhw_setpoint))
    space = _space_target(coord, result, now)
    if pump_mode.capability(getattr(mode_state, "state", None)).cooling:
        # Cooling is the user's season, not a duty the plan chose: hands off.
        return PumpCommand(None, None, None)
    both = pump_mode.MODE_HEAT_DHW if _option_for(mode_state, pump_mode.MODE_HEAT_DHW) else None
    if duty != "dhw":
        return PumpCommand(both, dhw, space)
    if _option_for(mode_state, pump_mode.MODE_DHW):
        return PumpCommand(pump_mode.MODE_DHW, dhw, space)
    gate = _bounded(space_state, FLOW_GATE_C if _flow(coord._config) else 5.0)
    return PumpCommand(both, dhw, gate)


def _planned_duty(coord: Any, now: datetime) -> str | None:
    """The duty to serve now, or ``None`` for the baseline."""
    if coord._mode not in (MODE_AUTO, MODE_ECONOMY) or coord._plan_is_stale():
        return None
    if (coord._current_action or {}).get("mode") == "system_identification":
        return None
    if boost.held_for(coord).until:
        return None
    result = getattr(coord, "_optimization_result", None)
    if result is None:
        return None
    on_kw = max(0.1, float(coord._thermal_model.params.min_electrical_power) * 0.5)
    return step_duty(result, now, on_kw)


def _leased(coord: Any, held: ArbiterState, duty: str | None, now: datetime) -> str | None:
    """``duty``, or ``None`` once a hot-water-only stretch outlives its lease."""
    if duty != "dhw":
        held.dhw_since = None
        return duty
    held.dhw_since = held.dhw_since or now
    cold = float(coord._current_state.outdoor_temperature) < COLD_RAIL_C
    cap = COLD_LEASE_MINUTES if cold else LEASE_MINUTES
    return None if now - held.dhw_since > timedelta(minutes=cap) else duty


def _differs(slot: str, observed: Any, value: Any) -> bool:
    """``observed`` is the select's state for the mode, degC for a set-point."""
    if slot == "mode":
        return pump_mode.resolve(observed) != value
    if observed is None or value is None:
        return False
    return bool(abs(observed - value) > SETPOINT_TOLERANCE)


def _observed(coord: Any, slot: str) -> Any:
    entity = _entities(coord._config)[slot]
    if slot == "mode":
        return getattr(coord.hass.states.get(entity) if entity else None, "state", None)
    return _read_setpoint(coord.hass, entity)


def foreign_change(coord: Any, now: datetime) -> str | None:
    """The first slot whose device state is not what the arbiter wrote."""
    for slot, (value, at) in state_for(coord).written.items():
        observed = _observed(coord, slot)
        if observed is None or (now - at).total_seconds() < ECHO_GRACE_S:
            continue
        if _differs(slot, observed, value):
            entity = _entities(coord._config)[slot]
            return f"{entity}: {observed} (set by the optimizer: {value})"
    return None


async def _write(coord: Any, slot: str, value: Any, now: datetime) -> None:
    held = state_for(coord)
    state, entity = _state(coord, slot), _entities(coord._config)[slot]
    recorded = held.written.get(slot)
    if value is None or state is None or (recorded and not _differs(slot, recorded[0], value)):
        return
    try:
        if slot == "mode":
            await coord.hass.services.async_call(
                "select",
                "select_option",
                {"entity_id": entity, "option": _option_for(state, value)},
                blocking=True,
            )
        else:
            await _write_setpoint(coord.hass, entity, temperature_from_c(value, state_unit(state)))
    except Exception as err:  # noqa: BLE001 - retried on the next tick
        _LOGGER.warning("Pump duty: writing %s to %s failed: %s", value, entity, err)
        return
    held.written[slot] = (value, now)
    await _persist(coord)


async def _command(coord: Any, command: PumpCommand, now: datetime) -> None:
    for slot in _SLOTS:
        await _write(coord, slot, getattr(command, slot), now)


async def _stand_down(coord: Any, detail: str) -> None:
    held = state_for(coord)
    held.manual, held.written = detail, {}
    await _persist(coord)
    _LOGGER.warning("Pump duty: manual change on %s; handing control back", detail)
    create_issue(
        coord.hass,
        DOMAIN,
        ISSUE_MANUAL,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_MANUAL,
        translation_placeholders={"detail": detail},
    )
    await coord.async_set_mode(MODE_OFF)


async def _resume(coord: Any) -> None:
    held = state_for(coord)
    held.manual, held.written = None, {}
    await _persist(coord)
    try:
        ir.async_delete_issue(coord.hass, DOMAIN, ISSUE_MANUAL)
    except Exception as err:  # noqa: BLE001 - clearing is best-effort
        _LOGGER.debug("Could not clear %s: %s", ISSUE_MANUAL, err)


def _observe(coord: Any, held: ArbiterState, duty: str | None) -> None:
    if duty == held.last_duty:
        return
    held.last_duty = duty
    state = _state(coord, "mode")
    _LOGGER.info(
        "Pump duty: plan step is %s; pump mode reads %s",
        duty or "baseline",
        getattr(state, "state", "not configured"),
    )


async def apply(coord: Any, now: datetime | None = None) -> None:
    """One arbitration pass; safe to call from the cycle and from the tick."""
    now = now or dt_util.now()
    held = state_for(coord)
    mode = duty_mode(coord._config)
    if mode == DUTY_OFF:
        release_listeners(coord)
        return
    async with held.lock:
        await _load(coord)
        _listen(coord)
        await _arbitrate(coord, held, mode, now)


async def _arbitrate(coord: Any, held: ArbiterState, mode: str, now: datetime) -> None:
    if coord._mode == MODE_OFF or mode != DUTY_CONTROL:
        if held.written and held.manual is None and mode == DUTY_CONTROL:
            await _command(coord, desired(coord, None, now), now)
        if held.written:
            held.written = {}
            await _persist(coord)
        if coord._mode == MODE_OFF:
            return
    if held.manual is not None:
        await _resume(coord)
    duty = _leased(coord, held, _planned_duty(coord, now), now)
    _observe(coord, held, duty)
    if mode != DUTY_CONTROL:
        return
    detail = foreign_change(coord, now)
    if detail is not None:
        await _stand_down(coord, detail)
        return
    await _command(coord, desired(coord, duty, now), now)


async def release(coord: Any) -> None:
    """Unload: write the baseline over anything still owned, then let go."""
    release_listeners(coord)
    held = state_for(coord)
    if held.written and held.manual is None and duty_mode(coord._config) == DUTY_CONTROL:
        await _command(coord, desired(coord, None, dt_util.now()), dt_util.now())


def release_listeners(coord: Any) -> None:
    held = state_for(coord)
    while held.unsubs:
        held.unsubs.pop()()


def _listen(coord: Any) -> None:
    held = state_for(coord)
    if held.unsubs:
        return
    hass = coord.hass

    async def _tick(_now: Any = None) -> None:
        await apply(coord)

    def _changed(_event: Any) -> None:
        hass.async_create_task(apply(coord))

    held.unsubs.append(async_track_time_interval(hass, _tick, _TICK))
    entities = [e for e in _entities(coord._config).values() if e]
    if entities:
        held.unsubs.append(async_track_state_change_event(hass, entities, _changed))


def _store(coord: Any) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(
        coord.hass, _STORE_VERSION, f"{DOMAIN}_{coord.entry.entry_id}_pump_duty"
    )


async def _persist(coord: Any) -> None:
    held = state_for(coord)
    payload = {
        "manual": held.manual,
        "written": {k: [v, at.isoformat()] for k, (v, at) in held.written.items()},
    }
    try:
        await _store(coord).async_save(payload)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not persist the pump duty record: %s", err)


async def _load(coord: Any) -> None:
    """Restore the ownership record once, so a restart keeps what it wrote."""
    held = state_for(coord)
    if held.loaded:
        return
    held.loaded = True
    try:
        raw = await _store(coord).async_load()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not load the pump duty record: %s", err)
        raw = None
    if not isinstance(raw, dict):
        return
    held.manual = raw.get("manual") or None
    for slot, pair in (raw.get("written") or {}).items():
        try:
            held.written[slot] = (pair[0], datetime.fromisoformat(pair[1]))
        except (TypeError, ValueError, IndexError):
            continue


def view(coord: Any) -> dict[str, Any]:
    """The diagnostics view."""
    held = state_for(coord)
    return {
        "duty_mode": duty_mode(coord._config),
        "last_duty": held.last_duty,
        "manual_change": held.manual,
        "written": {k: v for k, (v, _at) in held.written.items()},
    }
