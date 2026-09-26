"""The pump-duty arbiter: which duty the pump serves, step by step.

The plan decides per 15-minute step whether the pump heats the house, the
tank, both or neither. Without this module that decision never reaches the
pump: it runs its own two thermostats and serves whichever demand it sees. So
a planned hot-water-only step in a warm house turns into space heating.

**What it writes.** One logic over three optional entity slots the options
flow already has: the pump's operating-mode select
(``heat_pump_mode_entity``), its hot-water set-point (``dhw_setpoint_entity``)
and its space set-point (``space_setpoint_entity``). Per step:

=============  ==================  ================  ===============
plan step      mode                hot water set     space set
=============  ==================  ================  ===============
hot water only DHW only, if offered configured       suitable, or
                                                     the space gate
space only     Heating, if offered  configured, or   suitable
                                    the DHW gate
both           Heating + DHW        configured       suitable
idle           unchanged            configured       suitable
baseline       Heating + DHW        configured       suitable
=============  ==================  ================  ===============

*Configured* is the hot-water set-point from the config flow
(``dhw_setpoint``), never a literal. *Suitable* is the plan's own number:
the weather-curve supply temperature for a flow set-point, or the step's
planned room temperature for an indoor one. A space-only step is heating
only (tvofi, 2026-09-24): the cheapest hours for the house need not be the
ones that keep the tank ready for its next hot-water window, so the pump's
own tank thermostat must not spend them. A disinfection cycle the
integration holds on (``DisinfectionSwitch.memo``) turns a space-only step
into Heating + DHW, so the planned anti-legionella run can make hot water.
*Idle* writes no mode: see :func:`desired`.

**Two transports, one logic.** The Tuya fork offers DHW-only and Heating,
so the mode is the gate there. The GCHV/Rotenso Modbus package's mode
register offers only Off / Cool + DHW / Heat + DHW -- no single heating
duty in either direction -- so where the select lists no such option the
gate is the other duty's set-point, lowered to the entity's own minimum
(never below :data:`FLOW_GATE_C` / :data:`DHW_GATE_C`). Which one applies
is read off the select's ``options``, not configured.

**While active, it holds what it wrote** (tvofi, 2026-09-25). Every value
it writes is recorded. A reading that differs from the record after
:data:`ECHO_GRACE_S` -- a person, an automation or the pump's own reset --
is written again at once: while "Optimizer active" is on the optimizer is
the pump's one writer, and turning it off is how a person takes the pump
back (the baseline row is written once, then nothing). A value the pump
still does not hold after that rewrite raises a warning repair and is sent
again every :data:`RETRY_MINUTES`; the first reading that holds it clears
the repair. Readings inside the grace prove nothing either way: the fork
shows a sent value for a few seconds whether or not the device took it.
While the configured power switch reads off, nothing is compared or
written.

The v6.6.12 design stood down on any change it could not explain as an
ignored write, turning the optimizer off. On tvofi's install the fork's
echo, a set-point the device refused, a restart that lost the record's
evidence and the pump's own reset to 25 degC when switched off all read as
a person, so the optimizer kept switching itself off.

**Its own writes are not evidence.** A mode the arbiter wrote must not reach
the next solve as "the pump cannot heat" (:func:`own`), or a DHW-only step
would block space heat for the whole horizon and nothing would ever write
Heating + DHW back. Under control that holds for any of its three modes,
not only the last one written: a pump that has not yet shown the next
write, one it is about to rewrite, or the first solve after a restart all
read the pump before the record agrees (v6.6.12).

**Rails.** Hot-water-only is leased: at most :data:`LEASE_MINUTES`, and
:data:`COLD_LEASE_MINUTES` below :data:`COLD_RAIL_C` outdoors, while the
house is below the plan's room temperature for the step. A house at or
above it needs no space heat, so the lease does not hand the pump's own
space thermostat a warm house (tvofi, v6.6.12). A stale or
missing plan, a fixed-rule mode, an experiment, a boost and the end of the
lease all get the baseline row above. Unloading writes the baseline too.

It acts at step boundaries: a one-minute tick (only while the option is not
off) re-derives the step, since the solve runs every 30 minutes and a plan
step is 15.

**Observe keeps a ledger**, in observe and in control: per 15-minute step,
the planned duty against what the pump did, read from what the integration
already reads -- the measured electrical draw (running or not), the mode
select (DHW only) and the tank temperature (a rise of :data:`TANK_RISE_C`
over the step is hot water). Each step is ``delivered``,
``space-instead``, ``dhw-instead``, ``idle-instead``, ``unknown`` (no power
meter and no tank rise) or ``baseline``. A concurrent Heating + DHW run
reads as hot water; a big draw can hide a tank rise. The last
:data:`LOG_STEPS` steps and their counts are in the diagnostics; the ledger
is not persisted. It is what decides whether control is worth turning on:
``delivered`` over the other verdicts is how often the pump already does
what the plan wanted.
"""
from __future__ import annotations

import asyncio
import bisect
import logging
from collections import Counter, deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from . import boost, pump_mode, setpoint_check
from .const import (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
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
from .drift import stored_instant
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
#: The floor of the hot-water gate on a transport with no heating-only mode.
DHW_GATE_C = 30.0
SETPOINT_TOLERANCE = 0.3
#: The v6.6.12 stand-down repair, cleared wherever a record from then loads.
ISSUE_MANUAL = "pump_manual_change"
ISSUE_IGNORED = "pump_write_ignored"
#: How long an ignored write waits before it is sent again.
RETRY_MINUTES = 5.0
TANK_RISE_C = 0.5
LOG_STEPS = 96
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
    """Per-coordinator record: what was written, and what did not hold."""

    #: slot -> (value written, when); the ownership record, persisted.
    written: dict[str, tuple[Any, datetime]] = field(default_factory=dict)
    #: slot -> differing readings in a row; slot -> when a value the pump
    #: did not hold is sent again.
    misses: dict[str, int] = field(default_factory=dict)
    retry: dict[str, datetime] = field(default_factory=dict)
    step: dict[str, Any] | None = None
    log: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=LOG_STEPS))
    dhw_since: datetime | None = None
    last_duty: str | None = None
    loaded: bool = False
    unsubs: list[Any] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_STATES: WeakKeyDictionary[Any, ArbiterState] = WeakKeyDictionary()
_OWN_MODES = frozenset((pump_mode.MODE_HEAT, pump_mode.MODE_DHW, pump_mode.MODE_HEAT_DHW))
_SLOTS = ("mode", "dhw_setpoint", "space_setpoint")


def _entities(config: Any) -> dict[str, Any]:
    """Slot -> the configured entity id; the three writable pump slots."""
    return {
        "mode": config.get(CONF_HEAT_PUMP_MODE_ENTITY),
        "dhw_setpoint": config.get(CONF_DHW_SETPOINT_ENTITY),
        "space_setpoint": config.get(CONF_SPACE_SETPOINT_ENTITY),
    }


def _flow_unit(config: Any) -> bool:
    return bool(config.get(CONF_SPACE_SETPOINT_UNIT, DEFAULT_SPACE_SETPOINT_UNIT) == "flow")


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
    """``signals`` with a heating mode marked as the arbiter's, not a block.

    Under control, whichever of its three modes the pump reads is the
    arbiter's step decision: its own last write, one it wrote before the
    pump showed the next, or one from before a restart; anything else is
    rewritten within a tick. With the optimizer off the reading blocks
    again, since the pump is the person's then.
    """
    if duty_mode(coord._config) != DUTY_CONTROL or coord._mode == MODE_OFF:
        return signals
    if signals.mode.key not in _OWN_MODES:
        return signals
    return replace(signals, mode_owned=True)


def _slot_state(coord: Any, slot: str) -> Any:
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


def _planned_room(result: Any, now: datetime) -> float | None:
    """The plan's room temperature for the step covering ``now``."""
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    points = list(getattr(result, "optimal_setpoints", None) or [])
    return points[i] if 0 <= i < len(points) else None


def _space_target(coord: Any, result: Any, now: datetime) -> float | None:
    """The plan's own space set-point: the curve supply, or the room target."""
    state = _slot_state(coord, "space_setpoint")
    if _flow_unit(coord._config):
        outdoor = float(coord._current_state.outdoor_temperature)
        return _bounded(state, coord._thermal_model.curve_flow_temp(outdoor), FLOW_GATE_C)
    return _bounded(state, _planned_room(result, now))


def desired(coord: Any, duty: str | None, now: datetime) -> PumpCommand:
    """The row of the module table for ``duty``; ``None`` is the baseline."""
    result = getattr(coord, "_optimization_result", None)
    mode_state = _slot_state(coord, "mode")
    space_state = _slot_state(coord, "space_setpoint")
    dhw = _bounded(_slot_state(coord, "dhw_setpoint"), float(coord._thermal_params.dhw_setpoint))
    space = _space_target(coord, result, now)
    if pump_mode.capability(getattr(mode_state, "state", None)).cooling:
        # Cooling is the user's season, not a duty the plan chose: hands off.
        return PumpCommand(None, None, None)
    both = pump_mode.MODE_HEAT_DHW if _option_for(mode_state, pump_mode.MODE_HEAT_DHW) else None
    if duty == "space" and _disinfecting(coord):
        duty = "both"
    if duty == "idle":
        # No mode write. The mode last written served the duty that just
        # finished, whose thermostat the plan has just satisfied, so it is
        # the one least likely to start anything; Heating + DHW would arm
        # both thermostats the plan kept off, and the other single duty
        # arms the one it did not just satisfy. The DHW-only lease keeps
        # counting across idle (``_leased``).
        return PumpCommand(None, dhw, space)
    if duty == "space":
        if _option_for(mode_state, pump_mode.MODE_HEAT):
            return PumpCommand(pump_mode.MODE_HEAT, dhw, space)
        return PumpCommand(both, _bounded(_slot_state(coord, "dhw_setpoint"), DHW_GATE_C), space)
    if duty != "dhw":
        return PumpCommand(both, dhw, space)
    if _option_for(mode_state, pump_mode.MODE_DHW):
        return PumpCommand(pump_mode.MODE_DHW, dhw, space)
    gate = _bounded(space_state, FLOW_GATE_C if _flow_unit(coord._config) else 5.0)
    return PumpCommand(both, dhw, gate)


def _disinfecting(coord: Any) -> bool:
    """Whether the integration holds the disinfection switch on right now."""
    switch = getattr(getattr(coord, "_legionella", None), "disinfect", None)
    return getattr(switch, "memo", None) is True


def dhw_gated(coord: Any, reading: float | None) -> bool:
    """Whether ``reading`` is the arbiter's own hot-water gate, below configured."""
    written = state_for(coord).written.get("dhw_setpoint")
    if reading is None or written is None or _differs("dhw_setpoint", reading, written[0]):
        return False
    configured = float(coord._thermal_params.dhw_setpoint)
    return bool(written[0] < configured - SETPOINT_TOLERANCE)


setpoint_check.dhw_gated = dhw_gated


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
    return step_duty(result, now, _on_kw(coord))


def _on_kw(coord: Any) -> float:
    return max(0.1, float(coord._thermal_model.params.min_electrical_power) * 0.5)


def _leased(coord: Any, held: ArbiterState, duty: str | None, now: datetime) -> str | None:
    """``duty``, or ``None`` once a hot-water-only stretch outlives its lease.

    An idle step keeps whatever mode is on the pump, so it keeps counting.
    """
    if duty != "dhw" and (duty != "idle" or held.dhw_since is None):
        held.dhw_since = None
        return duty
    held.dhw_since = held.dhw_since or now
    cold = float(coord._current_state.outdoor_temperature) < COLD_RAIL_C
    cap = COLD_LEASE_MINUTES if cold else LEASE_MINUTES
    if now - held.dhw_since <= timedelta(minutes=cap):
        return duty
    room = getattr(coord._current_state, "room_temperature", None)
    planned = _planned_room(getattr(coord, "_optimization_result", None), now)
    warm = room is not None and planned is not None and float(room) >= float(planned)
    return duty if warm else None


def _differs(slot: str, observed: Any, value: Any) -> bool:
    """``observed`` is the select's state for the mode, degC for a set-point."""
    if slot == "mode":
        return bool(pump_mode.resolve(observed) != value)
    if observed is None or value is None:
        return False
    return bool(abs(observed - value) > SETPOINT_TOLERANCE)


def _observed(coord: Any, slot: str) -> Any:
    """The reading, or ``None`` when there is none: an unavailable select is not a mode."""
    entity = _entities(coord._config)[slot]
    if slot == "mode":
        raw = getattr(coord.hass.states.get(entity) if entity else None, "state", None)
        return raw if pump_mode.resolve(raw) is not None else None
    return setpoint_check._read_setpoint(coord.hass, entity)


def hold(coord: Any, now: datetime) -> None:
    """Drop the record of every slot the pump does not hold, so it is rewritten.

    The first differing reading is rewritten at once; one that still differs
    after that rewrite is warned about and retried every few minutes.
    """
    held = state_for(coord)
    for slot, (value, at) in list(held.written.items()):
        observed = _observed(coord, slot)
        if observed is None or (now - at).total_seconds() < ECHO_GRACE_S:
            continue
        if not _differs(slot, observed, value):
            held.misses.pop(slot, None)
            if held.retry.pop(slot, None) is not None and not held.retry:
                _clear(coord, ISSUE_IGNORED)
            continue
        del held.written[slot]
        held.misses[slot] = held.misses.get(slot, 0) + 1
        if held.misses[slot] > 1:
            entity = _entities(coord._config)[slot]
            _not_held(coord, held, slot, f"{entity}: {observed} (set by the optimizer: {value})", now)


def _not_held(coord: Any, held: ArbiterState, slot: str, detail: str, now: datetime) -> None:
    """A rewrite did not hold either: warn, and send it again in a few minutes."""
    held.retry[slot] = now + timedelta(minutes=RETRY_MINUTES)
    _LOGGER.warning("Pump duty: the pump does not hold a write, %s; retrying", detail)
    setpoint_check.create_issue(
        coord.hass,
        DOMAIN,
        ISSUE_IGNORED,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_IGNORED,
        translation_placeholders={"detail": detail},
    )


def _clear(coord: Any, issue: str) -> None:
    try:
        ir.async_delete_issue(coord.hass, DOMAIN, issue)
    except Exception as err:  # noqa: BLE001 - clearing is best-effort
        _LOGGER.debug("Could not clear %s: %s", issue, err)


def _forget(held: ArbiterState) -> None:
    held.written, held.misses, held.retry = {}, {}, {}


async def _write(coord: Any, slot: str, value: Any, now: datetime) -> None:
    held = state_for(coord)
    state, entity = _slot_state(coord, slot), _entities(coord._config)[slot]
    recorded = held.written.get(slot)
    if value is None or state is None or (recorded and not _differs(slot, recorded[0], value)):
        return
    if slot in held.retry and now < held.retry[slot]:
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


def _observe(coord: Any, held: ArbiterState, duty: str | None, now: datetime) -> None:
    """Fold this pass into the current step's ledger row; close the last one."""
    held.last_duty = duty
    start = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
    tank = getattr(coord._current_state, "dhw_temperature", None)
    row = held.step
    if row is None or row["start"] != start:
        if row is not None:
            held.log.append(_verdict(row, tank))
        held.step = row = {"start": start, "planned": duty, "tank": tank,
                           "measured": False, "ran": False, "dhw_mode": False}
    power = getattr(coord, "_measured_power", None)
    if power is not None:
        row["measured"] = True
        row["ran"] = row["ran"] or float(power) >= _on_kw(coord)
    mode = pump_mode.resolve(getattr(_slot_state(coord, "mode"), "state", None))
    row["dhw_mode"] = row["dhw_mode"] or mode == pump_mode.MODE_DHW


def _verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
    """What the pump did over one step, against what the plan wanted."""
    rose = None not in (tank, row["tank"]) and float(tank) - float(row["tank"]) >= TANK_RISE_C
    hot = rose or row["dhw_mode"]
    if row["measured"]:
        actual: str | None = ("dhw" if hot else "space") if row["ran"] else "idle"
    else:
        actual = "dhw" if rose else None
    planned = row["planned"]
    if planned is None:
        verdict = "baseline"
    elif actual is None:
        verdict = "unknown"
    elif actual == planned or (planned == "both" and actual != "idle"):
        verdict = "delivered"
    else:
        verdict = f"{actual}-instead"
    return {"start": row["start"].isoformat(), "planned": planned,
            "actual": actual, "verdict": verdict}


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
        if held.written and mode == DUTY_CONTROL:
            await _command(coord, desired(coord, None, now), now)
        if held.written or held.retry:
            # A pending retry dies with control, and so does its warning.
            _forget(held)
            _clear(coord, ISSUE_IGNORED)
            await _persist(coord)
        if coord._mode == MODE_OFF:
            return
    duty = _leased(coord, held, _planned_duty(coord, now), now)
    _observe(coord, held, duty, now)
    if mode != DUTY_CONTROL or _pump_off(coord):
        return
    hold(coord, now)
    await _command(coord, desired(coord, duty, now), now)


def _pump_off(coord: Any) -> bool:
    """Whether the configured power switch reads off.

    Switched off, the pump reports set-points of its own (tvofi's reads 25
    degC), so nothing is compared or written until it is on again; then a
    reset that is still there is rewritten like any other difference.
    """
    entity = coord._config.get(CONF_HEAT_PUMP_SWITCH_ENTITY)
    power = coord.hass.states.get(entity) if entity else None
    return bool(getattr(power, "state", None) == "off")


async def release(coord: Any) -> None:
    """Unload: write the baseline over anything still owned, then let go."""
    release_listeners(coord)
    held = state_for(coord)
    if held.written and duty_mode(coord._config) == DUTY_CONTROL:
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

    @callback
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
    if raw.get("manual"):
        _clear(coord, ISSUE_MANUAL)
    for slot, pair in (raw.get("written") or {}).items():
        try:
            at = stored_instant(pair[1])
        except (TypeError, KeyError, IndexError):
            continue
        if at is not None:
            held.written[slot] = (pair[0], at)


def diagnostics_view(coord: Any) -> dict[str, Any]:
    """The diagnostics view."""
    held = state_for(coord)
    return {
        "duty_mode": duty_mode(coord._config),
        "last_duty": held.last_duty,
        "misses": dict(held.misses),
        "retrying": sorted(held.retry),
        "written": {k: v for k, (v, _at) in held.written.items()},
        "ledger": {
            "counts": dict(Counter(r["verdict"] for r in held.log)),
            "steps": list(held.log),
        },
    }
