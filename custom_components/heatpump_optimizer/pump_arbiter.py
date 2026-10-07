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
both           DHW only, then       configured       suitable
               Heating (split)
idle           unchanged            configured       suitable
baseline       Heating + DHW        configured       suitable
=============  ==================  ================  ===============

*Configured* is the hot-water set-point from the config flow
(``dhw_setpoint``), never a literal. *Suitable* is the plan's own number.
For an indoor set-point it is the step's planned room temperature. For a
flow set-point it follows the planned level, from the return temperature
(or :data:`FLOW_HOLD_C`) up to :data:`FLOW_HEAT_C` at full power, on a step
that heats the house; the gate on one that does not; and on the baseline
:data:`FLOW_HOLD_C` or the weather curve where that is higher
(:func:`_flow_target`). A space-only step is heating
only (tvofi, 2026-09-24): the cheapest hours for the house need not be the
ones that keep the tank ready for its next hot-water window, so the pump's
own tank thermostat must not spend them. A disinfection cycle the
integration holds on (``DisinfectionSwitch.memo``) turns a space-only step
into Heating + DHW, so the planned anti-legionella run can make hot water.
*Idle* writes no mode: see :func:`desired`. A both step is split by
:func:`_share`: DHW only for the step's hot-water share of its 15 minutes,
then Heating, each through its own row above; a share under
:data:`SPLIT_MIN_MINUTES` goes to the other duty (tvofi, 2026-09-27).
A block drops its duty out of :func:`_planned_duty` and again out of
whatever :func:`_share` and the hot-water lease return, so a blocked
duty is served as idle and a lease expiry cannot hand it back. The
power switch is not written.

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
back, and nothing is written from then on. A value the pump
still does not hold after that rewrite raises a warning repair and is sent
again every :data:`RETRY_MINUTES`; the first reading that holds it clears
the repair. Readings inside the grace prove nothing either way: the fork
shows a sent value for a few seconds whether or not the device took it.
While the configured power switch reads off, nothing is compared or
written.

**The silent switch** is a fourth held slot on that same record, and only
when the capacity-limited entity is a ``switch`` and at least one silent
row is configured (#1911). Inside a silent window it is held on; outside
one, off; a boost releases it for the boost and it is held again after.
An install with no silent rows never has it written. An Off window adds
no write of its own: those steps are the idle row, and the power switch
is not one of them. Switching the optimizer off writes nothing and undoes
nothing, so a switch it turned on stays on. The reading that write causes
keeps the learners off the interval, and it is not a further cap on the
plan: the window's ceiling is the solve's.

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
missing plan, comfort, an experiment and the end of the lease all get
the baseline row above, and so does unloading while the optimizer is on.
A boost adds its duty to the plan step's (Boost Space Heating alone is
space only, DHW boost alone hot water only), and the global boost mode is
both (:func:`_planned_duty`). Turning it off writes nothing.

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
import math
from collections import Counter, deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, TypeGuard
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from . import boost, pump_mode, quiet_windows, setpoint_check
from .const import (
    CONF_DHW_SETPOINT_ENTITY,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_PUMP_DUTY_MODE,
    CONF_QUIET_OFF_WINDOWS,
    CONF_QUIET_SILENT_WINDOWS,
    CONF_SPACE_SETPOINT_ENTITY,
    CONF_SPACE_SETPOINT_UNIT,
    DEFAULT_PUMP_DUTY_MODE,
    DEFAULT_SPACE_SETPOINT_UNIT,
    DOMAIN,
    MODE_AUTO,
    MODE_BOOST,
    MODE_ECONOMY,
    MODE_OFF,
    PUMP_DUTY_MODES,
)
from .modbus_prefill import night_mode_write_ids, package_prefix
from .inputs import state_unit, temperature_c, temperature_from_c
from .payload import CurrentAction
from .repairs import _write_setpoint
from .accuracy import utc_elapsed_seconds, utc_shift
from .drift import stored_instant
from .store import QuarantiningStore, load_mapping
from .thermal_model import (
    configured_flow_heat_c,
    flow_setpoint_for_level,
    on_threshold_kw,
    planned_draw_runs,
)

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
#: A flow set-point on a step the plan heats (tvofi, 2026-09-26): the design
#: flow of a heat-pump radiator system, so the pump's own water thermostat
#: never cuts a planned heating step short. The supply itself settles where
#: the emitters take the pump's output, below this in all but the coldest
#: weather.
FLOW_HEAT_C = 55.0
#: The fallback's flow set-point: the W35 point the nameplate COP is rated at.
FLOW_HOLD_C = 35.0
SETPOINT_TOLERANCE = 0.3
#: The v6.6.12 stand-down repair, cleared wherever a record from then loads.
ISSUE_MANUAL = "pump_manual_change"
ISSUE_IGNORED = "pump_write_ignored"
#: How long an ignored write waits before it is sent again.
RETRY_MINUTES = 5.0
#: The shortest single-duty share of a both step; a shorter share goes to
#: the other duty for the whole step (valve travel and compressor cycling).
SPLIT_MIN_MINUTES = 5.0
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
    #: On or off for the silent switch; ``None`` writes nothing there.
    silent: bool | None = None


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


@dataclass(frozen=True)
class ArbiterInputs:
    """One pass's read-only inputs from the coordinator (#1739).

    The coordinator builds a snapshot per arbitration pass through its
    published ``arbiter_inputs``; the arbiter names no private member.
    ``plan`` rides along ungated beside ``plan_stale`` because the share
    split and the baseline read it without the staleness gate, exactly as
    the privates did.
    """

    hass: Any
    config: dict[str, Any]
    mode: str
    plan: Any
    plan_stale: bool
    entry_released: bool
    state: Any
    thermal: Any
    params: Any
    action: CurrentAction
    measured_power_kw: float | None
    disinfecting: bool


_STATES: WeakKeyDictionary[Any, ArbiterState] = WeakKeyDictionary()
_OWN_MODES = frozenset((pump_mode.MODE_HEAT, pump_mode.MODE_DHW, pump_mode.MODE_HEAT_DHW))
_SLOTS = ("mode", "dhw_setpoint", "space_setpoint", "silent")
#: GCHV night-mode registers 518/519 as hour then minute per register (#1913).
_NIGHT_KEYS = {
    "night_start_hour": "start_hour",
    "night_start_minute": "start_minute",
    "night_end_hour": "end_hour",
    "night_end_minute": "end_minute",
}
_NIGHT_SLOTS = tuple(_NIGHT_KEYS)
#: The mode slot's writable domains; its third, ``sensor``, is read-only.
_MODE_DOMAINS = frozenset(("select", "input_select"))


def _entities(config: Any) -> dict[str, Any]:
    """Slot -> the configured entity id.

    The silent slot is the capacity-limited entity only while that entity
    is a switch the arbiter can hold. A binary sensor stays a reading.
    """
    silent = config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY)
    return {
        "mode": config.get(CONF_HEAT_PUMP_MODE_ENTITY),
        "dhw_setpoint": config.get(CONF_DHW_SETPOINT_ENTITY),
        "space_setpoint": config.get(CONF_SPACE_SETPOINT_ENTITY),
        "silent": silent if quiet_windows.silent_control_usable(silent) else None,
    }


def _slot_entity(config: Any, slot: str) -> Any:
    """The entity id for ``slot``, including the GCHV night-mode numbers."""
    if slot in _NIGHT_KEYS:
        prefix = package_prefix(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY))
        return None if not prefix else night_mode_write_ids(prefix).get(_NIGHT_KEYS[slot])
    return _entities(config).get(slot)


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


def _release_duty_floor(
    fn: Callable[..., str | None],
) -> Callable[..., str | None]:
    """Drop the plan's modulation floor if ``step_duty`` raises between the reads."""
    @wraps(fn)
    def _wrapped(*args: Any, **kwargs: Any) -> str | None:
        try:
            return fn(*args, **kwargs)
        finally:
            setattr(planned_draw_runs, "modulation_floor", None)
    return (
        _wrapped
    )


@_release_duty_floor
def step_duty(result: Any, now: datetime) -> str | None:
    """``dhw``, ``space``, ``both`` or ``idle`` for the plan step covering now.

    Each circuit's draw is read by the plan's own running rule
    (``planned_draw_runs``), so the duty the arbiter serves is the duty the
    plan booked. This used to take the threshold from its caller, which handed
    it the METER's threshold -- half the pump's modulation floor -- and split
    the two circuits on two different numbers (R9 D12-s2-01, #1644 P2): on a
    fixed-speed pump a step the plan priced as 1.0 kW of delivered heat read as
    no space duty at all, so the arbiter wrote the pump's hot-water mode over
    it. A caller-supplied threshold is the shape that let them diverge, so the
    parameter is gone rather than defaulted.
    """
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] > timedelta(minutes=15)):
        return None
    space = list(result.power_schedule or [])
    dhw = list(getattr(result, "dhw_power_schedule", None) or [])
    setattr(
        planned_draw_runs, "modulation_floor",
        getattr(result, "duty_floor_kw", None),
    )
    s_on = i < len(space) and planned_draw_runs(space[i])
    d_on = i < len(dhw) and planned_draw_runs(dhw[i])
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

    A capacity-limited reading the arbiter caused by holding the silent
    switch is left on ``signals``. The learners skip that interval, which
    is what the flag is for, and the reading is not a plan block: the
    window's ceiling is already the solve's, and this flag adds none.
    """
    inp = coord.arbiter_inputs()
    if duty_mode(inp.config) != DUTY_CONTROL or inp.mode == MODE_OFF:
        return signals
    if signals.mode.key not in _OWN_MODES:
        return signals
    return replace(signals, mode_owned=True)


def _slot_state(inp: ArbiterInputs, slot: str) -> Any:
    entity = _entities(inp.config)[slot]
    return inp.hass.states.get(entity) if entity else None


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


def _planned_room(
    result: Any, now: datetime, attr: str = "optimal_setpoints"
) -> float | None:
    """The plan series ``attr`` for the step covering ``now``."""
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    points = list(getattr(result, attr, None) or [])
    return points[i] if 0 <= i < len(points) else None


def _space_target(inp: ArbiterInputs, result: Any, now: datetime, duty: str | None) -> float | None:
    """The plan's own space set-point for ``duty``; see :func:`_flow_target`."""
    state = _slot_state(inp, "space_setpoint")
    if _flow_unit(inp.config):
        return _flow_target(inp, state, duty, now)
    room = _planned_room(result, now)
    low = temperature_c((getattr(state, "attributes", None) or {}).get("min"), state_unit(state))
    if room is not None and low is not None and low > room + SETPOINT_TOLERANCE:
        # An "indoor" entity that cannot hold the room target is a flow
        # set-point declared as indoor: clamping 21 degC up to its minimum
        # is the 25 degC this module must never write to a flow entity.
        _LOGGER.warning(
            "Pump duty: %s is declared an indoor set-point but its minimum is "
            "%.1f degC; set its unit to Flow temperature. Not writing it.",
            _entities(inp.config)["space_setpoint"], low,
        )
        return None
    return _bounded(state, room)


def _step_kw(result: Any, now: datetime) -> float | None:
    """The plan's space power for the step covering ``now``, or ``None``."""
    return (
        _finite_or_none(_planned_room(result, now, "power_schedule"))
    )


def _finite_or_none(value: Any) -> float | None:
    return (
        float(value) if isinstance(value, (int, float)) else None
    )


def _band_kw(inp: ArbiterInputs) -> tuple[Any, Any]:
    """``(p_min, p_max)`` from the model when the params snapshot lacks them."""
    params = inp.params
    thermal_params = getattr(inp.thermal, "params", None)
    p_min = getattr(params, "min_electrical_power", None)
    p_max = getattr(params, "max_electrical_power", None)
    return (
        (
            p_min if p_min is not None
            else getattr(thermal_params, "min_electrical_power", None)
        ),
        (
            p_max if p_max is not None
            else getattr(thermal_params, "max_electrical_power", None)
        ),
    )


def _flow_inlet_c(inp: ArbiterInputs) -> float:
    """Floor-return temperature, else the rated hold flow."""
    value = getattr(inp.state, "floor_return_temperature", None)
    finite = tuple(
        float(item) for item in (value,)
        if isinstance(item, (int, float))
        if math.isfinite(item)
    )
    return (
        finite[0] if finite else FLOW_HOLD_C
    )


def _flow_target(
    inp: ArbiterInputs, state: Any, duty: str | None, now: datetime
) -> float | None:
    """A flow set-point per duty: heat, gate, or the fallback's hold.

    The model's weather curve is a pricing curve, not a set-point: it sizes
    the emitters to the pump's full output at ``emitter_design_delta_t``, so
    it runs 22-26 degC and a pump told to hold it barely heats (tvofi,
    2026-09-26). A step that heats writes a flow that follows the planned
    level: :data:`FLOW_HEAT_C` (or the configured ceiling) at full power,
    toward the return temperature at the modulation floor, so the pump's
    own water thermostat can realize a lower level. A fixed 55 °C never
    cycles, and a sub-minimum slot then delivers the modulation floor. A
    step that does not heat writes the gate. The fallback leaves the pump
    on its own, so it holds the rated :data:`FLOW_HOLD_C`, or the curve
    where that is higher.
    """
    if duty in ("space", "both"):
        p_min, p_max = _band_kw(inp)
        return _bounded(
            state,
            flow_setpoint_for_level(
                _step_kw(inp.plan, now),
                p_min,
                p_max,
                configured_flow_heat_c(inp.config, FLOW_HEAT_C),
                _flow_inlet_c(inp),
            ),
            FLOW_GATE_C,
        )
    if duty is not None:
        return _bounded(state, FLOW_GATE_C, FLOW_GATE_C)
    outdoor = float(inp.state.outdoor_temperature)
    curve = inp.thermal.curve_flow_temp(outdoor)
    ceiling = configured_flow_heat_c(inp.config, FLOW_HEAT_C)
    hold = FLOW_HOLD_C if curve is None else min(max(curve, FLOW_HOLD_C), ceiling)
    return _bounded(state, hold, FLOW_GATE_C)


def _step_start(now: datetime) -> datetime:
    """The 15-minute step start covering ``now``, on the solver's clock."""
    return now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)


def _silent_rows(spec: Any) -> TypeGuard[str]:
    """Whether ``spec`` names a silent window the week can reach.

    The same ``step_actions`` the solve uses, over seven days from a Monday,
    so a weekday token and an overnight window are rows and an empty or
    unreadable spec is not. No rows means the switch is never written.
    True only for a ``str``, which is what lets the caller pass it to
    :func:`_inside_silent`.
    """
    if not isinstance(spec, str) or not spec.strip():
        return False
    monday = datetime(2026, 1, 5, tzinfo=timezone.utc)
    actions = quiet_windows.step_actions(monday, 7 * 96, 0.25, spec, None)
    return actions is not None


def _inside_silent(silent_spec: str, off_spec: Any, now: datetime) -> bool:
    """Whether the step covering ``now`` is silent, off winning an overlap.

    The same ``step_actions`` the solve uses, so a hand-edited store whose
    off row overlaps a silent row holds the switch off: that step is idle,
    not a silent one.
    """
    actions = quiet_windows.step_actions(
        _step_start(now), 1, 0.25, silent_spec, off_spec,
    )
    return actions is not None and int(actions[0]) == quiet_windows.ACTION_SILENT


def _silent_target(coord: Any, inp: ArbiterInputs, now: datetime) -> bool | None:
    """On inside a silent window, off outside; ``None`` when the slot is not ours.

    ``None`` when the capacity-limited entity is not a switch, or no silent
    row is configured: that install never has the switch written. A boost,
    a channel or the global boost mode, releases it for the boost.
    """
    if _entities(inp.config)["silent"] is None:
        return None
    spec = inp.config.get(CONF_QUIET_SILENT_WINDOWS)
    if not _silent_rows(spec):
        return None
    if inp.mode == MODE_BOOST:
        return False
    held = boost.held_for(coord)
    if held.active(boost.CHANNEL_SPACE, now) or held.active(boost.CHANNEL_DHW, now):
        return False
    return _inside_silent(spec, inp.config.get(CONF_QUIET_OFF_WINDOWS), now)


def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> PumpCommand:
    """The row of the module table for ``duty``; ``None`` is the baseline."""
    result = inp.plan
    mode_state = _slot_state(inp, "mode")
    space_state = _slot_state(inp, "space_setpoint")
    dhw = _bounded(_slot_state(inp, "dhw_setpoint"), float(inp.params.dhw_setpoint))
    if pump_mode.capability(getattr(mode_state, "state", None)).cooling:
        # Cooling is the user's season, not a duty the plan chose: hands off,
        # the silent switch included.
        return PumpCommand(None, None, None)
    silent = _silent_target(coord, inp, now)
    both = pump_mode.MODE_HEAT_DHW if _option_for(mode_state, pump_mode.MODE_HEAT_DHW) else None
    if duty == "space" and inp.disinfecting:
        duty = "both"
    space = _space_target(inp, result, now, duty)
    if duty == "idle":
        # No mode write. The mode last written served the duty that just
        # finished, whose thermostat the plan has just satisfied, so it is
        # the one least likely to start anything; Heating + DHW would arm
        # both thermostats the plan kept off, and the other single duty
        # arms the one it did not just satisfy. The DHW-only lease keeps
        # counting across idle (``_leased``).
        return PumpCommand(None, dhw, space, silent)
    if duty == "space":
        if _option_for(mode_state, pump_mode.MODE_HEAT):
            return PumpCommand(pump_mode.MODE_HEAT, dhw, space, silent)
        return PumpCommand(both, _bounded(_slot_state(inp, "dhw_setpoint"), DHW_GATE_C), space, silent)
    if duty != "dhw":
        return PumpCommand(both, dhw, space, silent)
    if _option_for(mode_state, pump_mode.MODE_DHW):
        return PumpCommand(pump_mode.MODE_DHW, dhw, space, silent)
    if _flow_unit(inp.config):
        return PumpCommand(both, dhw, space, silent)
    return PumpCommand(both, dhw, None if space is None else _bounded(space_state, 5.0), silent)


def dhw_gated(coord: Any, reading: float | None) -> bool:
    """Whether ``reading`` is the arbiter's own hot-water gate, below configured."""
    written = state_for(coord).written.get("dhw_setpoint")
    if reading is None or written is None or _differs("dhw_setpoint", reading, written[0]):
        return False
    configured = float(coord.arbiter_inputs().params.dhw_setpoint)
    return bool(written[0] < configured - SETPOINT_TOLERANCE)


def _planned_duty(coord: Any, inp: ArbiterInputs, now: datetime) -> str | None:
    """The duty to serve now, or ``None`` for the baseline.

    A boost adds its duty to the plan's step, not the baseline (tvofi,
    2026-09-27): Heating + DHW would hand the other duty to the pump's own
    thermostat for the boost's two hours, and when that duty runs is the
    plan's. So Boost Space Heating is heating only, DHW boost hot water
    only (leased like any), and ``both`` where the step or the other boost
    wants the other duty too. The global boost mode plans no hot water, so
    it is ``both``: the heating flow, not the baseline's hold.
    """
    if inp.mode == MODE_BOOST:
        return "both"
    if inp.mode not in (MODE_AUTO, MODE_ECONOMY):
        return None
    if (inp.action or {}).get("mode") == "system_identification":
        return None
    held = boost.held_for(coord)
    result = None if inp.plan_stale else inp.plan
    duty = None if result is None else step_duty(result, now)
    space = held.active(boost.CHANNEL_SPACE, now)
    dhw = held.active(boost.CHANNEL_DHW, now)
    if not (space or dhw):
        return duty
    space = space or duty in ("space", "both")
    dhw = dhw or duty in ("dhw", "both")
    return "both" if space and dhw else "space" if space else "dhw"


def _without_block(coord: Any, duty: str | None, now: datetime) -> str | None:
    """Drop a blocked duty. No block leaves ``duty`` unchanged, including None."""
    held = boost.held_for(coord)
    space_off = held.block_active(boost.CHANNEL_SPACE, now)
    dhw_off = held.block_active(boost.CHANNEL_DHW, now)
    if not space_off and not dhw_off:
        return duty
    if duty == "idle":
        return "idle"
    # None is the baseline row: both duties. Idle is already neither.
    if duty is None:
        space, dhw = not space_off, not dhw_off
    else:
        space = duty in ("space", "both") and not space_off
        dhw = duty in ("dhw", "both") and not dhw_off
    if space and dhw:
        return "both"
    if space:
        return "space"
    if dhw:
        return "dhw"
    return "idle"


def block_cold_lease(inp: ArbiterInputs, now: datetime) -> bool:
    """Whether the cold rail would hand space heat back.

    Outdoor below :data:`COLD_RAIL_C` and the room below the plan's
    temperature for this step — the pair :func:`_leased` consults, without
    the lease timer. An unknown room or plan while it is that cold counts,
    so a block cannot keep space heat off on a missing reading.
    """
    outdoor = getattr(inp.state, "outdoor_temperature", None)
    if outdoor is None or float(outdoor) >= COLD_RAIL_C:
        return False
    room = getattr(inp.state, "room_temperature", None)
    planned = _planned_room(None if inp.plan_stale else inp.plan, now)
    if room is None or planned is None:
        return True
    return float(room) < float(planned)


def _ran_kw(inp: ArbiterInputs) -> float:
    """The MEASURED draw above which this step's ledger row counts a run.

    The meter's question, owned by ``thermal_model.on_threshold_kw`` and not
    the plan's: this reads the pass's measured draw
    (``ArbiterInputs.measured_power_kw``), so half the modulation
    floor is the right separator, and the plan's own running rule (which the
    duty above takes) would count a standby draw as a run. One formula answered
    both until R9 D12-s2-01; the two names are what keeps them apart.
    """
    return on_threshold_kw(inp.thermal.params)


def _leased(inp: ArbiterInputs, held: ArbiterState, duty: str | None, now: datetime) -> str | None:
    """``duty``, or ``None`` once a hot-water-only stretch outlives its lease.

    An idle step keeps whatever mode is on the pump, so it keeps counting.
    """
    if duty != "dhw" and (duty != "idle" or held.dhw_since is None):
        held.dhw_since = None
        return duty
    held.dhw_since = held.dhw_since or now
    cold = float(inp.state.outdoor_temperature) < COLD_RAIL_C
    cap = COLD_LEASE_MINUTES if cold else LEASE_MINUTES
    if now - held.dhw_since <= timedelta(minutes=cap):
        return duty
    room = getattr(inp.state, "room_temperature", None)
    planned = _planned_room(inp.plan, now)
    warm = room is not None and planned is not None and float(room) >= float(planned)
    return duty if warm else None


def _differs(slot: str, observed: Any, value: Any) -> bool:
    """``observed`` is the select's state for the mode, degC for a set-point."""
    if slot in _NIGHT_KEYS:
        if observed is None or value is None:
            return False
        return int(observed) != int(value)
    if slot == "mode":
        return bool(pump_mode.resolve(observed) != value)
    if slot == "silent":
        return bool(observed is not value)
    if observed is None or value is None:
        return False
    return bool(abs(observed - value) > SETPOINT_TOLERANCE)


def _observed(inp: ArbiterInputs, slot: str) -> Any:
    """The reading, or ``None`` when there is none: an unavailable select is not a mode."""
    entity = _slot_entity(inp.config, slot)
    if slot in _NIGHT_KEYS:
        raw = getattr(inp.hass.states.get(entity) if entity else None, "state", None)
        if raw is None:
            return None
        try:
            return int(round(float(raw)))
        except (TypeError, ValueError):
            return None
    if slot == "mode":
        raw = getattr(inp.hass.states.get(entity) if entity else None, "state", None)
        return raw if pump_mode.resolve(raw) is not None else None
    if slot == "silent":
        raw = getattr(inp.hass.states.get(entity) if entity else None, "state", None)
        if raw == "on":
            return True
        if raw == "off":
            return False
        return None
    return setpoint_check._read_setpoint(inp.hass, entity)


def hold(coord: Any, now: datetime) -> None:
    """Drop the record of every slot the pump does not hold, so it is rewritten.

    The first differing reading is rewritten at once; one that still differs
    after that rewrite is warned about and retried every few minutes.
    """
    held = state_for(coord)
    inp = coord.arbiter_inputs()
    for slot, (value, at) in list(held.written.items()):
        observed = _observed(inp, slot)
        if observed is None or utc_elapsed_seconds(now, at) < ECHO_GRACE_S:
            continue
        if not _differs(slot, observed, value):
            held.misses.pop(slot, None)
            if held.retry.pop(slot, None) is not None and not held.retry:
                _clear(coord, ISSUE_IGNORED)
            continue
        del held.written[slot]
        held.misses[slot] = held.misses.get(slot, 0) + 1
        if held.misses[slot] > 1:
            entity = _slot_entity(inp.config, slot)
            _not_held(coord, held, slot, f"{entity}: {observed} (set by the optimizer: {value})", now)


def _not_held(coord: Any, held: ArbiterState, slot: str, detail: str, now: datetime) -> None:
    """A rewrite did not hold either: warn, and send it again in a few minutes."""
    held.retry[slot] = utc_shift(now, timedelta(minutes=RETRY_MINUTES))
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


def _service(slot: str, state: Any, value: Any) -> tuple[str, dict[str, Any]] | None:
    """The service and its data that write ``value`` to ``slot``.

    ``None`` for a set-point, which goes through ``_write_setpoint``.
    """
    if slot == "mode":
        return "select_option", {"option": _option_for(state, value)}
    if slot == "silent":
        return ("turn_on" if value else "turn_off"), {}
    if slot in _NIGHT_KEYS:
        return "set_value", {"value": int(value)}
    return None


async def _write(coord: Any, inp: ArbiterInputs, slot: str, value: Any, now: datetime) -> None:
    held = state_for(coord)
    entity = _slot_entity(inp.config, slot)
    state = inp.hass.states.get(entity) if entity else None
    recorded = held.written.get(slot)
    if value is None or entity is None or state is None or (
        recorded and not _differs(slot, recorded[0], value)
    ):
        return
    if slot in held.retry and utc_elapsed_seconds(now, held.retry[slot]) < 0:
        return
    domain = entity.split(".", 1)[0]
    if slot == "mode" and domain not in _MODE_DOMAINS:
        return  # a read-only mode slot is read, never written (D12-s2-02)
    service = _service(slot, state, value)
    try:
        if service is None:
            await _write_setpoint(coord.hass, entity, temperature_from_c(value, state_unit(state)))
        else:
            await inp.hass.services.async_call(
                domain, service[0], {"entity_id": entity, **service[1]}, blocking=True,
            )
    except Exception as err:  # noqa: BLE001 - retried on the next tick
        _LOGGER.warning("Pump duty: writing %s to %s failed: %s", value, entity, err)
        return
    held.written[slot] = (int(value) if slot in _NIGHT_KEYS else value, now)
    await _persist(coord)


async def _command(coord: Any, inp: ArbiterInputs, command: PumpCommand, now: datetime) -> None:
    for slot in _SLOTS:
        await _write(coord, inp, slot, getattr(command, slot), now)


def _night_clock(hour: float) -> tuple[int, int]:
    minutes = int(round(hour * 60.0)) % (24 * 60)
    return minutes // 60, minutes % 60


async def _write_night_schedule(coord: Any, inp: ArbiterInputs, now: datetime) -> None:
    """Hold the GCHV night-mode start/end for the next silent window (#1913).

    Off windows write nothing extra (D1). start==end is not a documented
    disable, so a daytime pass still holds tonight's window rather than
    emptying the registers. At most the four numbers, and only when the
    window changes.
    """
    held = state_for(coord)
    spec = inp.config.get(CONF_QUIET_SILENT_WINDOWS)
    if not spec or not quiet_windows.gchv_schedule_ready(
        inp.config, inp.hass.states.get
    ):
        for slot in _NIGHT_SLOTS:
            held.written.pop(slot, None)
        return
    nxt = quiet_windows.next_gchv_window(now, spec)
    if nxt is None:
        return
    start_h, start_m = _night_clock(nxt[0])
    end_h, end_m = _night_clock(nxt[1])
    if (start_h, start_m) == (end_h, end_m):
        return
    values = {
        "night_start_hour": start_h,
        "night_start_minute": start_m,
        "night_end_hour": end_h,
        "night_end_minute": end_m,
    }
    for slot in _NIGHT_SLOTS:
        await _write(coord, inp, slot, values[slot], now)


def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: datetime) -> None:
    """Fold this pass into the current step's ledger row; close the last one."""
    held.last_duty = duty
    start = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
    tank = getattr(inp.state, "dhw_temperature", None)
    row = held.step
    if row is None or row["start"] != start:
        if row is not None:
            held.log.append(_verdict(row, tank))
        held.step = row = {"start": start, "planned": duty, "tank": tank,
                           "measured": False, "ran": False, "dhw_mode": False}
    power = inp.measured_power_kw
    if power is not None:
        row["measured"] = True
        row["ran"] = row["ran"] or float(power) >= _ran_kw(inp)
    mode = pump_mode.resolve(getattr(_slot_state(inp, "mode"), "state", None))
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
    mode = duty_mode(coord.arbiter_inputs().config)
    if mode == DUTY_OFF:
        release_listeners(coord)
        return
    async with held.lock:
        await _load(coord)
        inp = coord.arbiter_inputs()
        if inp.entry_released:
            return  # queued before the unload: arm and write nothing (D1-s3-02)
        _listen(coord)
        await _arbitrate(coord, held, inp, mode, now)


async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: str, now: datetime) -> None:
    if inp.mode == MODE_OFF or mode != DUTY_CONTROL:
        # Off writes nothing, not even the baseline (tvofi, 2026-09-26): the
        # pump is the person's the moment the optimizer lets go of it.
        if held.written or held.retry:
            # A pending retry dies with control, and so does its warning.
            _forget(held)
            _clear(coord, ISSUE_IGNORED)
            await _persist(coord)
        if inp.mode == MODE_OFF:
            return
    if boost.release_blocked(coord, inp, now):
        await boost.persist(coord)
    duty = _leased(
        inp, held, _without_block(coord, _planned_duty(coord, inp, now), now), now,
    )
    _observe(held, inp, duty, now)
    if mode != DUTY_CONTROL or _pump_off(inp):
        return
    hold(coord, now)
    await _command(
        coord, inp,
        desired(coord, inp, _without_block(coord, _share(coord, inp, duty, now), now), now),
        now,
    )
    await _write_night_schedule(coord, inp, now)


def _share(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> str | None:
    """On a planned both step, hot water first for its share, then heating.

    Heating + DHW leaves the split to the pump's own two thermostats (tvofi,
    2026-09-27). The share is the step's hot-water power over its total.
    A boost, a disinfection hold or a non-plan mode keeps Heating + DHW.
    """
    held = boost.held_for(coord)
    if (duty != "both" or inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.disinfecting
            or held.active(boost.CHANNEL_SPACE, now) or held.active(boost.CHANNEL_DHW, now)):
        return duty
    result = inp.plan
    i = bisect.bisect_right(result.timestamps, now) - 1
    space, dhw = result.power_schedule[i], result.dhw_power_schedule[i]
    dhw_min = 15.0 * dhw / (space + dhw)
    if dhw_min < SPLIT_MIN_MINUTES:
        return "space"
    if 15.0 - dhw_min < SPLIT_MIN_MINUTES:
        return "dhw"
    return "dhw" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else "space"


def _pump_off(inp: ArbiterInputs) -> bool:
    """Whether the configured power switch reads off.

    Switched off, the pump reports set-points of its own (tvofi's reads 25
    degC), so nothing is compared or written until it is on again; then a
    reset that is still there is rewritten like any other difference.
    """
    entity = inp.config.get(CONF_HEAT_PUMP_SWITCH_ENTITY)
    power = inp.hass.states.get(entity) if entity else None
    return bool(getattr(power, "state", None) == "off")


async def release(coord: Any) -> None:
    """Unload: write the baseline over anything still owned, then let go."""
    release_listeners(coord)
    held = state_for(coord)
    inp = coord.arbiter_inputs()
    if held.written and duty_mode(inp.config) == DUTY_CONTROL and inp.mode != MODE_OFF:
        await _command(coord, inp, desired(coord, inp, None, dt_util.now()), dt_util.now())


def release_listeners(coord: Any) -> None:
    held = state_for(coord)
    while held.unsubs:
        held.unsubs.pop()()


def _listen(coord: Any) -> None:
    held = state_for(coord)
    if held.unsubs:
        return
    hass = coord.hass
    inp = coord.arbiter_inputs()

    async def _tick(_now: Any = None) -> None:
        await apply(coord)

    @callback
    def _changed(_event: Any) -> None:
        hass.async_create_task(apply(coord))

    held.unsubs.append(async_track_time_interval(hass, _tick, _TICK))
    entities = [e for e in _entities(inp.config).values() if e]
    prefix = package_prefix(inp.config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY))
    if prefix:
        entities.extend(night_mode_write_ids(prefix).values())
    if entities:
        held.unsubs.append(async_track_state_change_event(hass, entities, _changed))


def _store(coord: Any) -> QuarantiningStore[dict[str, Any]]:
    return QuarantiningStore(
        coord.hass,
        _STORE_VERSION,
        f"{DOMAIN}_{coord.entry.entry_id}_pump_duty",
        naive_zone=dt_util.DEFAULT_TIME_ZONE,  # _load's zone
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
    raw = await load_mapping(_store(coord), "the pump duty record")
    if raw is None:
        return
    if raw.get("manual"):
        _clear(coord, ISSUE_MANUAL)
    written = raw.get("written")
    for slot, pair in written.items() if isinstance(written, dict) else ():
        try:
            value, at = pair[0], stored_instant(pair[1], dt_util.DEFAULT_TIME_ZONE)
        except (TypeError, KeyError, IndexError):
            continue
        if at is not None and _writable(slot, value):
            held.written[slot] = (value, at)


def _writable(slot: str, value: Any) -> bool:
    """Whether ``value`` is one the arbiter could have written to ``slot``.

    A restored record is compared and rewritten on every pass, so one of any
    other shape raised there on every cycle (D1-s3-03).
    """
    if slot == "mode":
        return isinstance(value, str) and value in _OWN_MODES
    if slot == "silent":
        return value is True or value is False
    if slot in _NIGHT_KEYS:
        return isinstance(value, int) and not isinstance(value, bool)
    return slot in _SLOTS and isinstance(value, (int, float)) and not isinstance(value, bool)


boost.bind_cold_lease(block_cold_lease)


def diagnostics_view(coord: Any) -> dict[str, Any]:
    """The diagnostics view."""
    held = state_for(coord)
    return {
        "duty_mode": duty_mode(coord.arbiter_inputs().config),
        "last_duty": held.last_duty,
        "misses": dict(held.misses),
        "retrying": sorted(held.retry),
        "written": {k: v for k, (v, _at) in held.written.items()},
        "ledger": {
            "counts": dict(Counter(r["verdict"] for r in held.log)),
            "steps": list(held.log),
        },
    }
