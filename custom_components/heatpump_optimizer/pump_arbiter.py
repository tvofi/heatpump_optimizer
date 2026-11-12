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
(:func:`_flow_target`). A return set-point (a controller that takes the
number as its return-water target) is written the same way, the hold and
the curve moved to return terms (:func:`_as_target`). A space-only step is heating
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
arbitration never writes the power switch; :func:`switch_supply` below is
that switch's one writer, shared by the cycle's plan write, the step tick
(:func:`supply_tick`) and the early cut-off (``early_cutoff.py``), so the
domain routing has one owner.

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
back, and nothing is written from then on but the restore below. A value the pump
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
is not one of them. Switching the optimizer off writes nothing to it and
undoes nothing, so a switch it turned on stays on. The reading that write causes
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
the baseline row above, and so does unloading while the optimizer is on,
the space set-point apart. A boost adds its duty to the plan step's (Boost Space Heating alone is
space only, DHW boost alone hot water only), and the global boost mode is
both (:func:`_planned_duty`). Turning it off writes nothing but the restore.

**Off restores the space set-point** (tvofi, 2026-11-07, "Arbiter too",
retracting 2026-09-26's "off writes nothing" for this slot). Before its first
write the arbiter arms :mod:`off_restore` (:data:`CONSUMER`), which captures
the entity's reading, persisted, as the person's baseline and writes it back
on the change into Off and on every unload, a reload and a Home Assistant
stop included (the hook's one rule). A reading equal to the arbiter's own
last write is never captured (:func:`_arm_space`). What a person sets while
the optimizer is off is captured at the next arm; one set between writes is
adopted as the baseline (:func:`_edited`), bounded to the entity's own
range, and, while active, still written over. The mode, the hot-water set-point and the silent switch are not
restored.

It acts at step boundaries: a one-minute tick (only while the option is not
off) re-derives the step, since the solve runs every 30 minutes and a plan
step is 15. The power switch has its own one-minute tick, armed by the
cycle's first switch write whatever the option says (:func:`supply_tick`).

**Observe keeps a ledger**, in observe and in control: per 15-minute step,
the planned duty against what the pump did, read from what the integration
already reads -- the measured electrical draw (running or not), the mode
select (DHW only) and the tank temperature (a rise of :data:`TANK_RISE_C`
over the step is hot water). Each step is ``delivered``,
``space-instead``, ``dhw-instead``, ``idle-instead``, ``unknown`` (no power
meter and no tank rise) or ``baseline``. A concurrent Heating + DHW run
reads as hot water; a big draw can hide a tank rise. The last
:func:`log_steps` steps and their counts are in the diagnostics; the ledger
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
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from typing import Any, TypeGuard, cast
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from . import boost, duty_switch, issues, off_restore, pump_mode, quiet_windows
from .const import (
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY,
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY,
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_POWER_ENTITY,
    CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY,
    CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
    CONF_SPACE_SETPOINT_POWER_FEEDBACK,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    DOMAIN,
    MODE_AUTO,
    MODE_BOOST,
    MODE_ECONOMY,
    MODE_OFF,
    PUMP_DUTY_MODES,
    SPACE_SETPOINT_WATER_UNITS,
)
from .entry_config import EntryConfig
from .freq_control import defrost_interval, resolve_reading
from .modbus_prefill import night_mode_write_ids, package_prefix
from .const import finite_float
from .inputs import (
    InputReader, quantise_setpoint_c, read_setpoint, setpoint_range_c, state_power_kw, write_setpoint_c,
)
from .log_latch import log_held
from .payload import REASON_LEGIONELLA, CurrentAction
from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
from .drift import utc_elapsed_seconds, utc_shift
from .drift import stored_instant
from .store import QuarantiningStore, load_mapping
from .thermal_model import (
    configured_flow_heat_c,
    configured_flow_min_lift_k,
    FLOW_MIN_LIFT_K,
    flow_setpoint_driven,
    flow_setpoint_for_level,
    modulation_floor_flow_c,
    on_threshold_kw,
    plan_step_runs,
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
#: How far a return-water target sits below the supply temperature the
#: arbiter derives it from, K: the rated supply-over-return spread of
#: :data:`FLOW_HOLD_C`'s W35 point (EN 14511, 30/35 °C). Applied only to the
#: supply-side values a ``return`` set-point is written from -- the hold and
#: the weather curve (:func:`_as_target`). An assumption carried from the
#: rating point, not measured on a return-target controller; deliberately
#: not ``thermal_model.FLOW_MIN_LIFT_K``, which is the floor's default lift
#: and may change on its own.
RETURN_SUPPLY_OFFSET_K = 5.0
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
_STORE_VERSION = 1


def log_steps() -> int:
    """One day of plan steps, the decision log's length (width owned by plan_step)."""
    return 24 * 60 // PLAN_STEP_MINUTES


_TICK = timedelta(minutes=1)
#: How long into a step the meter still reads the last step (#2492 carry 8):
#: the supply tick writes the switch in the step's first tick, and the
#: arbiter's tick in that same minute reads the draw from before the write.
RUN_SETTLE = _TICK

#: The power-feedback loop on a water set-point (R10-WATER-SETPOINT-FEEDBACK,
#: outside report #3380): a controller that integrates on target minus inlet
#: ramps for as long as the target sits above the water, so the open-loop
#: inlet-plus-lift target never settles at the planned level. The window the
#: measured draw is averaged over before it is compared with the plan; the
#: meter updates every few seconds and the arbiter passes at least once a
#: minute (:data:`_TICK`).
FEEDBACK_WINDOW = timedelta(minutes=3)
#: How long a run writes today's target before the loop moves it: the
#: controller's start programme (about 3 minutes at a fixed speed, measured
#: on the reporting install) is not a response to the target.
FEEDBACK_START_HOLD = timedelta(minutes=5)
#: How far the target moves per minute outside the deadband, K. Time-based,
#: not per pass: passes come from the cycle, the tick and the listener.
FEEDBACK_RATE_K_PER_MIN = 0.2
#: The deadband on the draw error: this share of the planned level, or of
#: the band's floor where the plan asks less, so a sub-minimum level gets no
#: narrower band than the modulation floor's. Inside it the target is held,
#: not re-anchored to the rising inlet.
FEEDBACK_DEADBAND_SHARE = 0.1
#: How far below the inlet the loop may wind the target down, K. A controller
#: stops a running compressor when its inlet reaches target plus its heating
#: hysteresis, a setting whose minimum is 0.5 K on the reporting firmware
#: (3.92.3; #3372 comment 6756915104, which also says not to assume 2 K, and
#: that input 10107 carries the start threshold in effect); less one 0.1 K
#: entity step and a 0.1 K inlet rise between passes, 0.3 K cannot stop it at
#: any permitted hysteresis, because a loop write is sent even when it moves
#: less than :data:`SETPOINT_TOLERANCE` (:func:`_note_sent`).
FEEDBACK_DOWN_K = 0.3
#: After a stop the loop caused, how much closer to the inlet than the gap
#: that stopped the compressor the target is held for the rest of this
#: arbiter state's life, K: two 0.1 K entity steps.
FEEDBACK_STOP_MARGIN_K = 0.2
#: Past the gate by any amount the entity's step rounding does not absorb,
#: so the loop's lowest write is the gate plus one entity step (I2).
FEEDBACK_GATE_CLEAR_K = 0.01


@dataclass(frozen=True)
class PumpCommand:
    """What the pump should be told for one step; ``None`` writes nothing."""

    mode: str | None
    dhw_setpoint: float | None
    space_setpoint: float | None
    #: On or off for the silent switch; ``None`` writes nothing there.
    silent: bool | None = None


@dataclass
class FeedbackRun:
    """One compressor run under the power-feedback loop; never persisted.

    A restart re-enters the start-hold, which writes today's target. The
    target ``w_c`` is kept unrounded, so a move smaller than the entity's
    step accumulates instead of rounding away.
    """

    start: datetime
    w_c: float
    seen: datetime
    #: (when, measured kW) over :data:`FEEDBACK_WINDOW`.
    samples: deque[tuple[datetime, float]] = field(default_factory=deque)
    running: bool = False
    #: The last value the loop sent that differs from today's target, and
    #: the record it replaced: the bracket ``hold`` reads a clamp cut in.
    sent_c: float | None = None
    prev_c: float | None = None
    #: Where the controller cut a loop write: the target never passes it.
    cut_lo_c: float | None = None
    cut_hi_c: float | None = None


@dataclass
class ArbiterState:
    """Per-coordinator record: what was written, and what did not hold."""

    #: slot -> (value written, when); the ownership record, persisted.
    written: dict[str, tuple[Any, datetime]] = field(default_factory=dict)
    #: slot -> the last write a loop move dropped from ``written`` to resend
    #: (:func:`_note_sent`), read while that record is missing, until a
    #: restore or release ends it; persisted with it. A loop run's reset
    #: keeps it. A write lands only once the off restore is armed, which
    #: :func:`_arm_space` no longer refuses, so no write needs to end it.
    dropped: dict[str, Any] = field(default_factory=dict)
    #: slot -> differing readings in a row; slot -> when a value the pump
    #: did not hold is sent again.
    misses: dict[str, int] = field(default_factory=dict)
    retry: dict[str, datetime] = field(default_factory=dict)
    step: dict[str, Any] | None = None
    log: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=log_steps()))
    dhw_since: datetime | None = None
    last_duty: str | None = None
    loaded: bool = False
    unsubs: list[Any] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    #: (step start, the supply the plan commanded for that step): written by
    #: the cycle's switch write and moved by :func:`supply_tick` (#2492).
    supply: tuple[datetime, bool] | None = None
    #: The step tick's listener; dropped only at unload, never by duty mode.
    supply_unsub: Callable[[], None] | None = None
    #: The space set-point's reading when the arbiter last armed a write to
    #: it; ``None`` unknown (a restart, or the power switch read off since).
    #: A later reading that is neither this nor the write is a person's edit.
    space_before: float | None = None
    #: The power-feedback loop's live run, and the inlet-to-target gap at
    #: which a loop-lowered target stopped the compressor (:func:`_feedback`).
    feedback: FeedbackRun | None = None
    stop_gap_k: float | None = None


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
    config: Mapping[str, Any]
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
    #: The pump's defrost flag as read (``PumpSignals.defrosting``); what it
    #: means is ``freq_control.defrost_interval``'s, and ``None`` is no flag
    #: or no evidence.
    defrosting: bool | None = None


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
    cfg = EntryConfig.from_mapping(config)
    silent = cfg.heat_pump_capacity_limited_entity
    return {
        "mode": cfg.heat_pump_mode_entity,
        "dhw_setpoint": cfg.dhw_setpoint_entity,
        "space_setpoint": cfg.space_setpoint_entity,
        "silent": silent if quiet_windows.silent_control_usable(silent) else None,
    }


def _slot_entity(config: Any, slot: str) -> Any:
    """The entity id for ``slot``, including the GCHV night-mode numbers."""
    if slot in _NIGHT_KEYS:
        prefix = package_prefix(EntryConfig.from_mapping(config).heat_pump_capacity_limited_entity)
        return None if not prefix else night_mode_write_ids(prefix).get(_NIGHT_KEYS[slot])
    return _entities(config).get(slot)


def _flow_unit(config: Any) -> bool:
    """The space set-point is a water temperature: a flow or a return target."""
    return EntryConfig.from_mapping(config).space_setpoint_unit in SPACE_SETPOINT_WATER_UNITS


def _return_unit(config: Any) -> bool:
    """The space set-point is the pump's return-water target."""
    return EntryConfig.from_mapping(config).space_setpoint_unit == "return"


def _as_target(config: Any, supply_c: float) -> float:
    """A supply temperature as the space entity's own water target, °C.

    Unchanged for a flow target. A return target (``space_setpoint_unit``
    ``return``) sits :data:`RETURN_SUPPLY_OFFSET_K` below it: the rated hold
    :data:`FLOW_HOLD_C` is the W35 point at 30/35 °C, and the weather curve
    is a supply curve, so written unchanged as a return target each would
    run the system water that spread hotter than meant. The gate
    :data:`FLOW_GATE_C` is a supply number too (a 25 °C supply target is
    below any heated water); as a return target, 25 °C sits above a cooled
    floor return (the install this was written for reads 23-24 °C after a
    blocked night), and a controller that modulates on target minus return
    would then heat on a step meant to be off, so it is moved as well
    (:func:`_gate_c`). Values already in the entity's own terms -- the
    measured inlet plus the lift, the configured ceiling -- are not moved.
    """
    return supply_c - RETURN_SUPPLY_OFFSET_K if _return_unit(config) else supply_c


def _heat_ceiling_c(config: Any) -> float:
    """The configured heating ceiling, °C, or :data:`FLOW_HEAT_C`.

    A stored ceiling at or below :data:`FLOW_GATE_C` would write the gate,
    the value that means off, on every heating step, so it reads as the
    default instead. The options flow offers nothing that low; this is the
    runtime half for a hand-edited entry.
    """
    ceiling = configured_flow_heat_c(config, FLOW_HEAT_C)
    return ceiling if ceiling > FLOW_GATE_C else FLOW_HEAT_C


def state_for(coord: Any) -> ArbiterState:
    held = _STATES.get(coord)
    if held is None:
        held = ArbiterState()
        _STATES[coord] = held
    return held


def duty_mode(config: Any) -> str:
    return EntryConfig.from_mapping(config).pump_duty_mode


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

    The plan's own floor travels as that rule's ``modulation_floor`` ARGUMENT
    (D7-arch3-04). It used to travel through an attribute on the function
    object, set here and cleared by a decorator's ``finally`` so a later
    floorless caller did not inherit it: one module-level slot for a per-plan
    value, read by every caller that passed none. No production reader runs off
    the loop, so the harm was the channel and the second piece of state that
    kept it clean, not a live race.
    """
    i = _step_index(result, now)
    if i is None:
        return None
    space = list(result.power_schedule or [])
    dhw = list(getattr(result, "dhw_power_schedule", None) or [])
    floor = getattr(result, "duty_floor_kw", None)
    s_on = i < len(space) and planned_draw_runs(space[i], modulation_floor=floor)
    d_on = i < len(dhw) and planned_draw_runs(dhw[i], modulation_floor=floor)
    return {(True, True): "both", (True, False): "space", (False, True): "dhw"}.get(
        (s_on, d_on), "idle"
    )


def _step_index(result: Any, now: datetime) -> int | None:
    """The index of the plan step covering ``now``, or ``None`` outside the plan.

    A step covers [stamp, stamp + one plan step): the last one ends where the
    next would start, the same half-open rule bisect gives every other step.
    """
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):
        return None
    return i


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


def _bounded(
    inp: ArbiterInputs,
    slot: str,
    value: float | None,
    floor: float = -1e9,
    *,
    rounding: str = "nearest",
    lo: float | None = None,
    hi: float | None = None,
) -> float | None:
    """``value`` (degC) inside the slot entity's own range, on its step.

    ``quantise_setpoint_c`` rounds it in the entity's unit: ``rounding``
    for the value itself, ``lo`` (a heating floor) up and ``hi`` (a
    ceiling) down, the entity's own minimum up and maximum down.
    """
    if value is None or _slot_state(inp, slot) is None:
        return None
    entity = _entities(inp.config)[slot]
    low, high = setpoint_range_c(inp.hass, entity)
    value = max(value, floor, low if low is not None else floor)
    value = min(value, high) if high is not None else value
    lows = [v for v in (lo, low) if v is not None]
    highs = [high] if high is not None else []
    # The entity's range outranks a caller's ceiling: a write under its
    # minimum on the step is refused, so a ceiling below that is dropped and
    # the minimum, rounded up onto the step, holds.
    if hi is not None and (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding="up")):
        highs.append(hi)
    return quantise_setpoint_c(
        inp.hass, entity, value, rounding=rounding,
        lo_c=max(lows) if lows else None, hi_c=min(highs) if highs else None,
    )


def _planned_room(
    result: Any, now: datetime, attr: str = "optimal_setpoints"
) -> float | None:
    """The plan series ``attr`` for the step covering ``now``."""
    stamps = list(getattr(result, "timestamps", None) or [])
    i = bisect.bisect_right(stamps, now) - 1
    points = list(getattr(result, attr, None) or [])
    return points[i] if 0 <= i < len(points) else None


def _space_target(
    inp: ArbiterInputs, result: Any, now: datetime, duty: str | None
) -> float | None:
    """The plan's own space set-point for ``duty``; see :func:`_flow_target`."""
    entity = _entities(inp.config)["space_setpoint"]
    if _flow_unit(inp.config):
        log_held(inp.hass, f"space_target_flow_declared:{entity}", False)
        return _flow_target(inp, duty, now)
    room = _planned_room(result, now)
    low = setpoint_range_c(inp.hass, entity)[0]
    # An "indoor" entity that cannot hold the room target is a flow
    # set-point declared as indoor: clamping 21 degC up to its minimum is the
    # 25 degC this module must never write to a flow entity. Latched on
    # ``hass``, which outlives the per-pass ``ArbiterInputs`` snapshot, as
    # ``inputs._age_gate`` is, and cleared on every pass that reads a
    # holdable minimum or a flow unit, so a fixed misdeclaration that recurs
    # warns again.
    misdeclared = room is not None and low is not None and low > room + SETPOINT_TOLERANCE
    if log_held(
        inp.hass, f"space_target_flow_declared:{entity}", misdeclared,
        "Pump duty: %s is declared an indoor set-point but its minimum is "
        "%.1f degC; set its unit to Flow temperature. Not writing it.",
        entity, low,
    ):
        return None
    return _bounded(inp, "space_setpoint", room)


def _step_kw(result: Any, now: datetime) -> float | None:
    """The plan's space power for the step covering ``now``, or ``None``."""
    return finite_float(_planned_room(result, now, "power_schedule"))


def _experiment_kw(inp: ArbiterInputs) -> float | None:
    """The system-identification experiment's commanded space power, or
    ``None`` when the action is not the experiment's.

    The experiment overrides the action, not the plan (``coordinator.
    _run_system_identification``), so its step -- the fit's sized level or
    the ceiling probe's configured maximum -- is read here, before the plan's
    ``power_schedule`` is consulted, or the plan's level would win.
    """
    action = inp.action or {}
    if action.get("mode") != "system_identification":
        return None
    return finite_float(action.get("power")) or 0.0


def _band_kw(inp: ArbiterInputs) -> tuple[Any, Any]:
    """``(p_min, p_max)`` the step's power maps on.

    A plan's step maps on the band the plan was solved on, its stamped
    ``solve_band`` (R10-COP-GATE part D): a plan booked on a learned top
    below the nameplate commands the ceiling at that top. An experiment's
    step maps on the hub's band, which sysid sized it on; so does a plan with
    no stamp. The hub's band from the model when the params snapshot lacks it.
    """
    band = getattr(inp.plan, "solve_band", None) or {}
    if band and _experiment_kw(inp) is None:
        return band["planned_min_kw"], band["planned_max_kw"]
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


#: The sensors that measure the water the pump heats, best first: the
#: set-point is a power command (tvofi, 2026-10-19), so its floor sits a
#: lift above that water. One precedence for every plant, because what a
#: slot measures follows the plant (tvofi asked for every combination):
#:
#: * pump-loop return -- the condenser's own inlet on any plant;
#: * buffer tank -- with a buffer, with or without a mixing valve, the
#:   pump heats the tank;
#: * floor return -- on a direct-to-radiator plant the pump's inlet; behind
#:   a buffer, the mixed circuit's return, below the tank, so the floor
#:   errs toward less power;
#: * valve outlet -- house-side supply, at or above the floor return and,
#:   on a wood topology, mixed with the wood tank, so the last rung.
#:
#: The pump's outgoing temperature is not a rung: it is the set-point's own
#: controlled variable, and a floor anchored on it would chase itself. No
#: rung read leaves the rated :data:`FLOW_HOLD_C`, today's default.
FLOW_INLET_KEYS = (
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
)
#: The rung a return target is not anchored on: the valve outlet is
#: house-side supply, and supply plus a lift written as a return target
#: over-commands by about the spread. A return target reads the other rungs
#: in the same precedence; none read leaves the no-inlet floor, the hold in
#: return terms.
RETURN_SKIPPED_RUNG = CONF_VALVE_OUTLET_TEMP_ENTITY
#: The controller's lower and upper limit on the space water set-point, as
#: the two optional sensors the feedback loop's bounds read.
SETPOINT_LIMIT_KEYS = (
    CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
    CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY,
)


def _reader(hass: Any, config: Mapping[str, Any]) -> InputReader:
    """The arbiter's live entity reads, under the install's staleness rules."""
    cfg = EntryConfig.from_mapping(config)
    return InputReader(
        hass, dict(config or {}),
        enabled=cfg.staleness_watchdog_enabled,
        scale=cfg.staleness_max_age_scale,
    )


def live_power_kw(hass: Any, config: Mapping[str, Any]) -> float | None:
    """The pump's measured draw now, kW, or ``None`` when unread.

    Read at each pass, not taken from the cycle's sample: the ledger folds
    one reading per one-minute tick, and a sample frozen at the cycle made a
    step's verdict depend on where the cycle fell against the step grid
    (#2492).
    """
    reading = _reader(hass, config).read_power_kw(CONF_POWER_ENTITY)
    return reading.value if reading.ok else None


def _flow_inlet_c(inp: ArbiterInputs) -> float | None:
    """The first fresh reading of :data:`FLOW_INLET_KEYS` (without
    :data:`RETURN_SKIPPED_RUNG` for a return target), °C, or ``None``.

    Read through :class:`~.inputs.InputReader`, so a stale, implausible or
    unconfigured slot is absent rather than guessed, and a slot left unset
    falls to the next rung.
    """
    reader = _reader(inp.hass, inp.config)
    skip = RETURN_SKIPPED_RUNG if _return_unit(inp.config) else None
    readings = (reader.read(key) for key in FLOW_INLET_KEYS if key != skip)
    return next(
        (reading.value for reading in readings if reading.ok), None
    )


def _gate_floor_c(config: Any) -> float:
    """The gate in the entity's own terms, °C: :data:`FLOW_GATE_C`, or that
    less the rated spread for a return target (:func:`_as_target`)."""
    return _as_target(config, FLOW_GATE_C)


def _gate_c(inp: ArbiterInputs) -> float | None:
    """The water set-point a step that does not heat writes, °C.

    The entity's minimum, never below the gate in its own terms
    (:func:`_gate_floor_c`): 25 °C for a flow target, 20 °C for a return
    target. The floor the lift is taken from on a heating step, and the
    floor every heating write is bounded by, are the same number.
    """
    gate = _gate_floor_c(inp.config)
    return _bounded(inp, "space_setpoint", gate, gate, rounding="down")


@dataclass(frozen=True)
class FlowCommand:
    """The space flow set-point the arbiter holds, beside its two ends, °C.

    ``ceiling_c`` is the set-point that commands the pump's maximum draw,
    the meaning ``draw_range`` reads it with: the configured ceiling (see
    :func:`_full_draw_c` for a return target).
    """

    written_c: float
    gate_c: float
    ceiling_c: float


def flow_command(coord: Any) -> FlowCommand | None:
    """The coordinator's held flow set-point as a :class:`FlowCommand`, or ``None``.

    Plumbing only: the inputs and the arbiter's state are read here and the
    decision is :func:`_flow_command`'s, which is handed neither the
    coordinator nor anything that reaches into it.
    """
    inp = coord.arbiter_inputs()
    state = state_for(coord)
    return _flow_command(inp, state)


def _flow_command(inp: ArbiterInputs, state: Any) -> FlowCommand | None:
    """What the held flow set-point (``state``'s written ``space_setpoint``
    record) commands, or ``None``.

    ``None`` unless the arbiter drives the pump through a flow set-point
    (Control, the flow unit, the optimizer not off) and holds a written
    value whose entity range reads, on an install whose plan does not write
    the compressor's power itself. Everywhere else the metered draw is the
    pump's own choice, or the plan's frequency echo, not a response capped
    by a set-point this module wrote -- the distinction ``draw_range``'s
    censoring guard keys on.
    """
    written = state.written.get("space_setpoint")
    if written is None or inp.mode == MODE_OFF or not flow_setpoint_driven(inp.config):
        return None
    gate = _gate_c(inp)
    ceiling = _bounded(
        inp, "space_setpoint", _heat_ceiling_c(inp.config), _gate_floor_c(inp.config),
        rounding="down",
    )
    if gate is None or ceiling is None or not isinstance(written[0], (int, float)):
        return None
    return FlowCommand(float(written[0]), gate, _full_draw_c(inp, ceiling))


def _full_draw_c(inp: ArbiterInputs, ceiling_c: float) -> float:
    """The set-point that commands the pump's maximum draw, °C.

    ``ceiling_c`` for a flow target: a supply target at the ceiling sits far
    above the water, so the pump may draw its top. A return target's
    controller is assumed to run harder the further the target sits above
    the measured return, so the ceiling commands the top only while the
    return-side inlet (:func:`_flow_inlet_c`) reads at least
    ``thermal_model.FLOW_MIN_LIFT_K`` below it. With less headroom, or no
    such reading, no writable set-point is known to command the top, and the
    answer is one lift above the ceiling: no write reaches it, so
    ``draw_range`` folds none of those draws as ceiling evidence, as a
    "full" sample or as an overdraw (R10-CEILING-PROBE), while the gate
    reading is untouched.
    """
    if not _return_unit(inp.config):
        return ceiling_c
    inlet = _flow_inlet_c(inp)
    headroom = inlet is not None and ceiling_c - inlet >= FLOW_MIN_LIFT_K
    return ceiling_c if headroom else ceiling_c + FLOW_MIN_LIFT_K


def _or_hold(floor_c: float | None, config: Any) -> float:
    """``floor_c``, else the rated hold as the entity's own target."""
    return _as_target(config, FLOW_HOLD_C) if floor_c is None else floor_c


def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float | None:
    """A flow set-point per duty: heat, gate, or the fallback's hold.

    The model's weather curve is a pricing curve, not a set-point: it sizes
    the emitters to the pump's full output at ``emitter_design_delta_t``, so
    it runs 22-26 degC and a pump told to hold it barely heats (tvofi,
    2026-09-26). A step that heats writes a flow that follows the planned
    level: :data:`FLOW_HEAT_C` (or the configured ceiling, ``flow_heat_c``)
    at full power, sliding to the measured inlet plus a minimum lift
    (``flow_min_lift_k``, else ``thermal_model.FLOW_MIN_LIFT_K``) at the
    modulation floor, so the pump's own water thermostat can realize a
    lower level.
    With no inlet reading the floor is the rated :data:`FLOW_HOLD_C`, in
    return terms on a return target (:func:`_as_target`), as is the
    fallback's hold below. A
    fixed 55 °C never cycles, and a sub-minimum slot then delivers the
    modulation floor. A
    step that does not heat writes the gate. The fallback leaves the pump
    on its own, so it holds the rated :data:`FLOW_HOLD_C`, or the curve
    where that is higher.
    """
    if duty in ("space", "both"):
        p_min, p_max = _band_kw(inp)
        heat_c = _heat_ceiling_c(inp.config)
        floor_c = _or_hold(modulation_floor_flow_c(
            _flow_inlet_c(inp), _gate_c(inp), configured_flow_min_lift_k(inp.config),
        ), inp.config)
        return _bounded(
            inp,
            "space_setpoint",
            flow_setpoint_for_level(
                _step_kw(inp.plan, now) if (kw := _experiment_kw(inp)) is None else kw,
                p_min, p_max, heat_c, floor_c,
            ),
            _gate_floor_c(inp.config),
            lo=min(floor_c, heat_c),
            hi=heat_c,
        )
    if duty is not None:
        return _gate_c(inp)
    outdoor = float(inp.state.outdoor_temperature)
    curve = inp.thermal.curve_flow_temp(outdoor)
    ceiling = _heat_ceiling_c(inp.config)
    # The hold and the curve are supply temperatures: moved to the entity's
    # own terms before the ceiling, which already is in them, caps the curve.
    # A flow target's bare hold stays uncapped, as it always was; a return
    # target's is capped too, so it never sits above the ceiling it was given.
    target = _as_target(inp.config, FLOW_HOLD_C if curve is None else max(curve, FLOW_HOLD_C))
    capped = curve is not None or _return_unit(inp.config)
    hold = min(target, ceiling) if capped else target
    return _bounded(inp, "space_setpoint", hold, _gate_floor_c(inp.config))


def _feedback_on(inp: ArbiterInputs, duty: str | None, now: datetime, boosts: Any) -> bool:
    """Whether this pass's water target (the caller's water unit) is the loop's.

    A space-only step below the band top, on an install with a power meter
    and the option on, outside a boost (``boosts``, the
    coordinator's ``boost.BoostState``), an experiment and a defrost. Space
    only comes from a fresh plan in Auto or Economy, an experiment or a
    boost (:func:`_planned_duty`). Anywhere else the meter reads a draw that
    is not this target's response (hot water, a reversed cycle), the step
    wants the ceiling, or the level is not the plan's.
    """
    cfg = EntryConfig.from_mapping(inp.config)
    if duty != "space" or not (cfg.space_setpoint_power_feedback and cfg.heat_pump_power_entity):
        return False
    planned, top = _step_kw(inp.plan, now), _band_kw(inp)[1]
    return bool(
        not defrost_interval(inp.defrosting) and _experiment_kw(inp) is None
        and not boosts.active(boost.CHANNEL_SPACE, now)
        and planned is not None and top is not None and planned < float(top)
    )


def _feedback(held: ArbiterState, inp: ArbiterInputs, now: datetime, base: float | None, on: bool) -> float | None:
    """The space water target under the power-feedback loop, else ``base``.

    ``base`` is today's open-loop target (:func:`_flow_target`). While the
    compressor runs on a qualifying pass (``on``, :func:`_feedback_on`), the
    target moves by :data:`FEEDBACK_RATE_K_PER_MIN` against the error
    between the windowed measured draw and the planned level, is held inside
    the deadband instead of re-anchored to the rising inlet, and stays
    within :func:`_feedback_bounds`. A run's first
    :data:`FEEDBACK_START_HOLD` writes ``base``, so its first write is
    today's. Any other pass, a stopped compressor or a missing inlet resets
    the run.
    """
    inlet = _flow_inlet_c(inp) if on else None
    if base is None or inlet is None:
        held.feedback = None
        return base
    power = finite_float(inp.measured_power_kw)
    rec = held.feedback
    if rec is not None and utc_elapsed_seconds(now, rec.seen) > FEEDBACK_WINDOW.total_seconds():
        rec = None  # passes that skipped the loop: a cooling or switched-off pump
    if power is None or power < _ran_kw(inp):
        if rec is not None and rec.running:
            _note_stop(held, rec, inlet, base)
        held.feedback = FeedbackRun(now, base, now)
        return base
    if rec is None:
        rec = held.feedback = FeedbackRun(now, base, now)
    rec.samples.append((now, power))
    while utc_elapsed_seconds(now, rec.samples[0][0]) > FEEDBACK_WINDOW.total_seconds():
        rec.samples.popleft()
    minutes = max(0.0, utc_elapsed_seconds(now, rec.seen)) / 60.0
    rec.running, rec.seen = True, now
    if utc_elapsed_seconds(now, rec.start) < FEEDBACK_START_HOLD.total_seconds():
        rec.w_c, rec.sent_c = base, None
        return base
    lo, hi = _feedback_bounds(held, rec, inp, inlet)
    rec.w_c = min(max(_nudged(rec, inp, now, minutes), lo), hi)
    out = _bounded(inp, "space_setpoint", rec.w_c, _gate_floor_c(inp.config), lo=lo, hi=hi)
    _note_sent(held, rec, out, base)
    return out


def _nudged(rec: FeedbackRun, inp: ArbiterInputs, now: datetime, minutes: float) -> float:
    """``rec.w_c`` moved against the draw error, or held inside the deadband.

    The plan's ``power_schedule`` is electrical kW, the unit of the band it
    is mapped on (:func:`_band_kw`) and of the meter.
    """
    planned = float(_step_kw(inp.plan, now) or 0.0)
    floor = finite_float(_band_kw(inp)[0]) or 0.0
    error = sum(kw for _at, kw in rec.samples) / len(rec.samples) - planned
    if abs(error) <= FEEDBACK_DEADBAND_SHARE * max(planned, floor):
        return rec.w_c
    return rec.w_c - math.copysign(FEEDBACK_RATE_K_PER_MIN * minutes, error)


def _feedback_bounds(held: ArbiterState, rec: FeedbackRun, inp: ArbiterInputs, inlet: float) -> tuple[float, float]:
    """``(lo, hi)`` the loop's target stays within, °C.

    Never more than :data:`FEEDBACK_DOWN_K` below the inlet, nor past a stop
    bound, a controller cut or the controller's own limits where their
    sensors are read (:func:`_setpoint_limits_c`), nor at the gate (I2);
    never above the ceiling.

    The gate is the value a step that does not heat writes, so a heating
    write at or below it tells the controller the step is off. A
    controller's upper limit, read from its sensor or from a cut, that
    sits under the lowest heating write (the gate plus one entity step)
    leaves no heating value inside it: it is not the limit of a heating
    set-point (a sensor in the wrong slot, a placeholder, a parked
    circuit), and it is left out as an unreadable one is.
    """
    gate = _gate_c(inp) or _gate_floor_c(inp.config)
    clear = gate + FEEDBACK_GATE_CLEAR_K
    lowest = _bounded(inp, "space_setpoint", clear, lo=clear) or clear
    lows = [inlet - FEEDBACK_DOWN_K, rec.cut_lo_c, clear]
    if held.stop_gap_k is not None:
        lows.append(inlet - held.stop_gap_k + FEEDBACK_STOP_MARGIN_K)
    low, high = _setpoint_limits_c(inp)
    lows.append(low)
    highs = [_heat_ceiling_c(inp.config)]
    highs += [v for v in (rec.cut_hi_c, high) if v is not None and v >= lowest]
    return (max(v for v in lows if v is not None), min(highs))


def _setpoint_limits_c(inp: ArbiterInputs) -> tuple[float | None, float | None]:
    """The controller's ``(lower, upper)`` limit on the space set-point, °C.

    Each from its optional sensor (:data:`SETPOINT_LIMIT_KEYS`) and ``None``
    where that is unset, unavailable, not a number or outside any water's
    range. Neither key has an age limit (``const.INPUT_MAX_AGE_MINUTES``):
    a limit is a setting, so its sensor reports when it changes and a
    reading holds until the source is ``unavailable``. A pair that is not lower below upper is two sensors in
    each other's slot, and neither is used.
    """
    reader = _reader(inp.hass, inp.config)
    low, high = (
        reading.value if reading.ok else None
        for reading in (reader.read(key) for key in SETPOINT_LIMIT_KEYS)
    )
    if low is not None and high is not None and low >= high:
        return (None, None)
    return (low, high)


def _note_sent(held: ArbiterState, rec: FeedbackRun, out: float | None, base: float | None) -> None:
    """Send a loop target whenever it moves; remember it and what it replaces.

    ``_write`` skips a value within :data:`SETPOINT_TOLERANCE` of its record,
    which keeps a held target silent. A loop move is smaller than that, and
    skipped it would leave the controller on a value up to the tolerance
    from the loop's: enough past the inlet to stop a running compressor
    (:data:`FEEDBACK_DOWN_K`), or to stall the wind-down. So a target that
    moves at all drops the record, and an equal one is still not sent. The
    dropped record is the run's ``prev_c``, the bracket :func:`_cut_of`
    reads, and ``held.dropped`` until a restore ends it: it is still the
    arbiter's last write, which the off restore's own-write refusal reads
    (:func:`_arm_space`) after the run that dropped it has ended.
    """
    recorded = held.written.get("space_setpoint")
    if out is None or (recorded is not None and recorded[0] == out):
        return
    if recorded is not None:
        rec.prev_c = held.dropped["space_setpoint"] = recorded[0]
    rec.sent_c = out if out != base else None
    held.written.pop("space_setpoint", None)


def _note_stop(held: ArbiterState, rec: FeedbackRun, inlet: float, base: float) -> None:
    """A run stopped under a loop target below today's: the loop caused it.

    The inlet-to-target gap it stopped at bounds the target from then on,
    :data:`FEEDBACK_STOP_MARGIN_K` closer to the inlet, so a controller whose
    stop hysteresis is smaller than assumed restarts at most once.
    """
    if rec.sent_c is None or rec.sent_c >= base:
        return
    gap = inlet - rec.sent_c
    held.stop_gap_k = gap if held.stop_gap_k is None else min(held.stop_gap_k, gap)


def _cut_of(rec: FeedbackRun | None, value: Any, observed: Any) -> bool:
    """Whether ``observed`` is the controller cutting the loop write ``value``:
    a reading between the record the write replaced and the write, each end
    widened by :data:`SETPOINT_TOLERANCE`. Read by :func:`_clamp_cut` and,
    before it, by the off restore's :func:`_edited`.
    """
    if rec is None or rec.sent_c is None or rec.prev_c is None or value != rec.sent_c:
        return False
    low, high = sorted((rec.prev_c, value))
    return bool(low - SETPOINT_TOLERANCE <= observed <= high + SETPOINT_TOLERANCE)


def _clamp_cut(held: ArbiterState, slot: str, value: Any, observed: Any, at: datetime) -> bool:
    """Whether a differing reading is the controller clamping a loop write.

    A reading between the record the loop write replaced and the write
    (each within :data:`SETPOINT_TOLERANCE`) is the controller's own limit,
    not a person: the record adopts it, the run's target stops there for
    the rest of the run, and ``hold`` reads it as held. A cut of
    today's target, or any other reading (a person, a revert to the
    controller's default), is ``hold``'s as before and starts the run over.

    On the reporting install the two limits are smart-home interface inputs 10104
    (parameter 979) and 10103 (parameter 87), which clamp register 10001
    (#3372 comment 6756915104). Where their sensors are configured the loop
    stays inside them (:func:`_setpoint_limits_c`) and no write is cut;
    they are inferred from the readback here for an install that names
    neither, and for a controller that publishes none.
    """
    if slot != "space_setpoint":
        return False
    rec, held.feedback = held.feedback, None
    if rec is None or rec.prev_c is None or not _cut_of(rec, value, observed):
        return False
    held.feedback = rec
    if value > rec.prev_c:
        rec.cut_hi_c = observed
    else:
        rec.cut_lo_c = observed
    rec.w_c, rec.sent_c = observed, None
    held.written["space_setpoint"] = (observed, at)
    return True


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
    actions = quiet_windows.step_actions(
        monday, 7 * 24 * 60 // PLAN_STEP_MINUTES, PLAN_STEP_HOURS, spec, None,
    )
    return actions is not None


def _inside_silent(silent_spec: str, off_spec: Any, now: datetime) -> bool:
    """Whether the step covering ``now`` is silent, off winning an overlap.

    The same ``step_actions`` the solve uses, so a hand-edited store whose
    off row overlaps a silent row holds the switch off: that step is idle,
    not a silent one.
    """
    actions = quiet_windows.step_actions(
        plan_step_start(now), 1, PLAN_STEP_HOURS, silent_spec, off_spec,
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
    cfg = EntryConfig.from_mapping(inp.config)
    spec = cfg.quiet_silent_windows
    if not _silent_rows(spec):
        return None
    if inp.mode == MODE_BOOST:
        return False
    held = boost.held_for(coord)
    if held.active(boost.CHANNEL_SPACE, now) or held.active(boost.CHANNEL_DHW, now):
        return False
    return _inside_silent(spec, cfg.quiet_off_windows, now)


def _dhw_write(inp: ArbiterInputs) -> float | None:
    """The hot-water set-point this step holds, °C on the entity's step.

    A cycle runs while the plan's step books hot water for it (``dhw_reason``
    legionella) or the integration holds the pump's disinfection switch on;
    its temperature is the thermal parameters' (``dhw_cycle_temp``, the higher
    of the everyday set-point and the disinfection temperature), on the
    entity's step at or below the tank's hard maximum (``dhw_hard_max_temp``,
    that temperature capped at 70 °C), which no write exceeds: an off-step
    target is held a step below it (everyday 57, disinfection 50, step 5:
    55, not 60). No cycle, the everyday set-point is written on the step
    at or below the charge limit (``dhw_max_temp``): rounding it up would
    hold the tank above the user's own limit for good (everyday 58, step 5:
    55, not 60). Holding the everyday set-point through a cycle
    stopped the pump's own thermostat short of the cycle's target (2026-11-01:
    60 °C planned, 55 °C written back within a minute).
    """
    everyday = float(inp.params.dhw_setpoint)
    booked = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA
    cycle = inp.params.dhw_cycle_temp if booked or inp.disinfecting else None
    if cycle is None:
        return _bounded(inp, "dhw_setpoint", everyday, hi=inp.params.dhw_max_temp)
    return _bounded(inp, "dhw_setpoint", float(cycle), hi=inp.params.dhw_hard_max_temp)


def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> PumpCommand:
    """The row of the module table for ``duty``; ``None`` is the baseline."""
    result = inp.plan
    mode_state = _slot_state(inp, "mode")
    dhw = _dhw_write(inp)
    if pump_mode.capability(getattr(mode_state, "state", None)).cooling:
        # Cooling is the user's season, not a duty the plan chose: hands off,
        # the silent switch included.
        return PumpCommand(None, None, None)
    silent = _silent_target(coord, inp, now)
    both = pump_mode.MODE_HEAT_DHW if _option_for(mode_state, pump_mode.MODE_HEAT_DHW) else None
    if duty == "space" and inp.disinfecting:
        duty = "both"
    space = _space_target(inp, result, now, duty)
    if _flow_unit(inp.config):
        space = _feedback(state_for(coord), inp, now, space, _feedback_on(inp, duty, now, boost.held_for(coord)))
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
        return PumpCommand(both, _bounded(inp, "dhw_setpoint", DHW_GATE_C, rounding="down"), space, silent)
    if duty != "dhw":
        return PumpCommand(both, dhw, space, silent)
    if _option_for(mode_state, pump_mode.MODE_DHW):
        return PumpCommand(pump_mode.MODE_DHW, dhw, space, silent)
    if _flow_unit(inp.config):
        return PumpCommand(both, dhw, space, silent)
    return PumpCommand(both, dhw, None if space is None else _bounded(inp, "space_setpoint", 5.0, rounding="down"), silent)


def dhw_gated(coord: Any, reading: float | None) -> bool:
    """Whether ``reading`` is the arbiter's own hot-water write, still as written.

    Its gate and its everyday set-point alike: the arbiter writes a cycle's
    temperature itself on a cycle step (``_dhw_write``), so its own write is
    a step decision, never the pump's set-point below the disinfection floor.
    A record exists only while the arbiter controls the pump (``_forget``).
    """
    written = state_for(coord).written.get("dhw_setpoint")
    return not (reading is None or written is None or _differs("dhw_setpoint", reading, written[0]))


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
    experiment = _experiment_kw(inp)
    if experiment is not None:
        # The experiment's own step, by the rule that books its
        # ``heat_pump_on``: heating while it injects, the gate while it does
        # not. Space only -- a hot-water charge would share the meter.
        return "space" if planned_draw_runs(experiment) else "idle"
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
    return read_setpoint(inp.hass, entity)


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
        if not _differs(slot, observed, value) or _clamp_cut(held, slot, value, observed, at):
            held.misses.pop(slot, None)
            if held.retry.pop(slot, None) is not None and not held.retry:
                issues.clear_issue(coord.hass, ISSUE_IGNORED)
            continue
        del held.written[slot]
        held.misses[slot] = held.misses.get(slot, 0) + 1
        if held.misses[slot] > 1:
            entity = _slot_entity(inp.config, slot)
            _not_held(coord, held, slot, f"{entity}: {observed} (set by the optimizer: {value})", now)


def _edited(held: ArbiterState, observed: float, now: datetime) -> bool:
    """The space reading is a person's edit, read before :func:`hold` rewrites it.

    One that differs from the arbiter's write after the grace, on the first
    miss (a second is a write the pump does not take), and not what the
    entity read when the write was sent (a refused write falls back to that),
    that reading known: after a restart or a power cycle (the pump's own
    reset) nothing is adopted. Nor is the controller's cut of a loop write
    (:func:`_cut_of`), which :func:`hold` adopts as the loop's bound.
    """
    record, before = held.written.get("space_setpoint"), held.space_before
    return record is not None and before is not None \
        and utc_elapsed_seconds(now, record[1]) >= ECHO_GRACE_S \
        and not held.misses.get("space_setpoint") \
        and _differs("space_setpoint", observed, record[0]) \
        and _differs("space_setpoint", observed, before) \
        and not _cut_of(held.feedback, record[0], observed)


def _not_held(coord: Any, held: ArbiterState, slot: str, detail: str, now: datetime) -> None:
    """A rewrite did not hold either: warn, and send it again in a few minutes."""
    held.retry[slot] = utc_shift(now, timedelta(minutes=RETRY_MINUTES))
    _LOGGER.warning("Pump duty: the pump does not hold a write, %s; retrying", detail)
    issues.create_issue(
        coord.hass,
        DOMAIN,
        ISSUE_IGNORED,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_IGNORED,
        translation_placeholders={"detail": detail},
    )


def _forget(held: ArbiterState) -> None:
    held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None


def _service(slot: str, state: Any, value: Any) -> tuple[str, dict[str, Any]] | None:
    """The service and its data that write ``value`` to ``slot``.

    ``None`` for a set-point, which goes through ``inputs.write_setpoint_c``.
    """
    if slot == "mode":
        return "select_option", {"option": _option_for(state, value)}
    if slot == "silent":
        return ("turn_on" if value else "turn_off"), {}
    if slot in _NIGHT_KEYS:
        return "set_value", {"value": int(value)}
    return None


async def _write(
    coord: Any, inp: ArbiterInputs, slot: str, value: Any, now: datetime, command: PumpCommand | None = None,
) -> None:
    held = state_for(coord)
    entity = _slot_entity(inp.config, slot)
    state = inp.hass.states.get(entity) if entity else None
    recorded = held.written.get(slot)
    if value is None or entity is None or state is None or (
        recorded and not _differs(slot, recorded[0], value)
    ):
        return
    if await _held_back(inp, coord.entry, held, slot, entity, now):
        return
    domain = entity.split(".", 1)[0]
    service = _service(slot, state, value)
    try:
        if service is None:
            await write_setpoint_c(coord.hass, entity, value)
        else:
            await inp.hass.services.async_call(
                domain, service[0], {"entity_id": entity, **service[1]}, blocking=True,
            )
    except Exception as err:  # noqa: BLE001 - retried on the next tick
        _LOGGER.warning("Pump duty: writing %s to %s failed: %s", value, entity, err)
        return
    held.written[slot] = (int(value) if slot in _NIGHT_KEYS else value, now)
    _report_write(duty_switch.record_for(coord), boost.held_for(coord), held, inp, slot, recorded, now, command)
    await _persist(coord)


def _reads_below(reading: Any, setpoint: Any) -> bool:
    """Whether a reading is known and under its known set-point: the duty has demand."""
    return reading is not None and setpoint is not None and float(reading) < float(setpoint)


def _report_write(
    learner: Any, boosts: Any, held: ArbiterState, inp: ArbiterInputs, slot: str,
    replaced: tuple[Any, datetime] | None, now: datetime, command: PumpCommand | None,
) -> None:
    """Tell ``duty_switch`` of a landed mode write, with its gates.

    Every mode write lands in :func:`_write`, a re-send after :func:`hold`
    dropped the record included (``replaced`` is then ``None``). The space
    set-point is the command's, written right after the mode: the one the
    controller judges the heating request on, and handed on only where it is
    a water temperature (:func:`_flow_unit`), never an indoor unit's room one. The source leg's age is the
    replaced mode record's; ``dhw_since`` is already reset on the pass that
    leaves hot water.
    """
    if slot != "mode":
        return
    context, mode = _switch_context(boosts, held, inp, now), held.written["mode"][0]
    target = {pump_mode.MODE_HEAT: "space", pump_mode.MODE_DHW: "dhw"}.get(mode)
    if command is not None and target is not None and inp.plan is not None:
        room, tank = getattr(inp.state, "room_temperature", None), getattr(inp.state, "dhw_temperature", None)
        planned = _planned_room(inp.plan, now)
        context = replace(
            context,
            inlet_c=_flow_inlet_c(inp), water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,
            source_leg_s=utc_elapsed_seconds(now, replaced[1]) if replaced else None,
            target_demand=_reads_below(room, planned) if target == "space" else _reads_below(tank, inp.params.dhw_setpoint),
            plan_stays=all(step_duty(inp.plan, at) in (target, "both")
                           for at in (now, utc_shift(now, timedelta(seconds=duty_switch.STOP_WINDOW_S)))),
        )
    duty_switch.note_mode_write(learner, now, replaced[0] if replaced else None, mode, context)


def _lit(inp: ArbiterInputs, *keys: str) -> bool:
    """Whether any of the configured flag entities ``keys`` reads on, fresh."""
    reader = _reader(inp.hass, inp.config)
    return any(reading.ok and bool(reading.flag) for reading in map(reader.read_bool, keys))


def _switch_context(boosts: Any, held: ArbiterState, inp: ArbiterInputs, now: datetime) -> duty_switch.SwitchContext:
    """This pass's readings that ``duty_switch`` judges a duty switch by."""
    mode = held.written.get("mode")
    return duty_switch.SwitchContext(
        supply_on=not _pump_off(inp, held),
        plan_control=inp.mode in (MODE_AUTO, MODE_ECONOMY) and duty_mode(inp.config) == DUTY_CONTROL,
        defrosting=bool(defrost_interval(inp.defrosting)) or _lit(inp, CONF_HEAT_PUMP_DEFROST_ENTITY),
        disinfecting=bool(inp.disinfecting),
        boost_held=any(boosts.active(c, now) for c in (boost.CHANNEL_SPACE, boost.CHANNEL_DHW)),
        electric_heat=_lit(inp, CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY, CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY),
        fault=_lit(inp, CONF_HEAT_PUMP_FAULT_ENTITY),
        loop_moved=held.feedback is not None and held.feedback.sent_c is not None,
        mode_written_at=mode[1] if mode else None,
        last_write_at=max((at for _value, at in held.written.values()), default=None),
    )


async def _adopt(inp: ArbiterInputs, entry: Any, held: ArbiterState, now: datetime) -> None:
    """A space set-point a person set (:func:`_edited`) becomes the baseline off restores."""
    entity = _entities(inp.config)["space_setpoint"]
    edit = _observed(inp, "space_setpoint")
    if edit is None or not _edited(held, edit, now):
        return
    # Off writes the baseline back, so it is one the entity takes: the edit
    # inside the entity's own range, on its step (#3402's bound at adoption).
    # A reading implies a state, so _bounded answers a number.
    baseline = cast(float, _bounded(inp, "space_setpoint", edit))
    if await off_restore.async_rebaseline(inp.hass, entry, CONSUMER, entity, baseline):
        _LOGGER.info("Pump duty: %s was set to %s by hand; turning the optimizer off restores %s",
                     entity, edit, baseline)


async def _held_back(
    inp: ArbiterInputs, entry: Any, held: ArbiterState, slot: str, entity: str, now: datetime,
) -> bool:
    """A write that differs but is not sent this pass: its retry is not due, the
    mode slot is read-only (D12-s2-02), or the space restore is not armed."""
    if slot in held.retry and utc_elapsed_seconds(now, held.retry[slot]) < 0:
        return True
    if slot == "mode" and entity.split(".", 1)[0] not in _MODE_DOMAINS:
        return True
    return slot == "space_setpoint" and not await _arm_space(inp, entry, held, entity)


async def _arm_space(inp: ArbiterInputs, entry: Any, held: ArbiterState, entity: str) -> bool:
    """Arm the off restore before a space write; False holds the write.

    The first arm captures the entity's reading as the baseline off restores
    (:mod:`off_restore`), but never one equal to the arbiter's own last write
    -- a record from before this restore existed: that number is the
    optimizer's, not the person's, so the write is held, latched, until the
    controller reads anything else.
    """
    armed = await off_restore.async_armed_entry(inp.hass, entry, CONSUMER)
    reading = read_setpoint(inp.hass, entity)
    record = held.written.get("space_setpoint")
    # A loop move dropped the record to be sent (_note_sent); held.dropped
    # keeps it across the run's end, which the loop resets on any stop.
    last = record[0] if record is not None else held.dropped.get("space_setpoint")
    own = (armed is None or armed["entity_id"] != entity) and last is not None \
        and reading is not None and not _differs("space_setpoint", reading, last)
    if log_held(inp.hass, f"space_baseline_own:{entity}", own,
                "Pump duty: %s reads %s, the optimizer's own last write, which is no "
                "baseline to restore on off; not writing it until it is set at the controller",
                entity, reading):
        return False
    held.space_before = reading
    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)


async def _command(coord: Any, inp: ArbiterInputs, command: PumpCommand, now: datetime) -> None:
    for slot in _SLOTS:
        await _write(coord, inp, slot, getattr(command, slot), now, command)


async def _write_night_schedule(coord: Any, inp: ArbiterInputs, now: datetime) -> None:
    """Hold the GCHV night-mode start/end for the next silent window (#1913).

    Off windows write nothing extra (D1). start==end is not a documented
    disable, so a daytime pass still holds tonight's window rather than
    emptying the registers. At most the four numbers, and only when the
    window changes.
    """
    held = state_for(coord)
    spec = EntryConfig.from_mapping(inp.config).quiet_silent_windows
    if not spec or not quiet_windows.gchv_schedule_ready(
        inp.config, inp.hass.states.get
    ):
        for slot in _NIGHT_SLOTS:
            held.written.pop(slot, None)
        return
    nxt = quiet_windows.next_gchv_window(now, spec)
    if nxt is None:
        return
    start_h, start_m = quiet_windows.wall_clock(nxt[0])
    end_h, end_m = quiet_windows.wall_clock(nxt[1])
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
    """Fold this pass into the current step's ledger row; close the last one.

    ``planned`` is re-frozen whenever a new plan is adopted inside the step:
    the cycle's re-solve can move a slot onto the current step, and the
    switch is written from that plan, so the step is scored against the
    plan that actuated it, not the one in force at its first tick. A meter
    reading inside ``RUN_SETTLE`` of the step's start is the last step's tail
    and folds into neither ``measured`` nor ``ran``.
    """
    held.last_duty = duty
    start = plan_step_start(now)
    tank = getattr(inp.state, "dhw_temperature", None)
    row = held.step
    if row is None or row["start"] != start:
        if row is not None:
            held.log.append(_verdict(row, tank))
        held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
                           "measured": False, "ran": False, "dhw_mode": False}
    elif row["plan"] is not inp.plan:
        row["planned"], row["plan"] = duty, inp.plan
    power = inp.measured_power_kw
    if power is not None and now - start >= RUN_SETTLE:
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
        # Off writes nothing here, not even the baseline row: the pump is the
        # person's the moment the optimizer lets go of it. The space
        # set-point's baseline is restored by off_restore (tvofi, 2026-11-07,
        # "Arbiter too"), before this pass; its record is dropped here.
        if held.written or held.retry or held.dropped or held.space_before is not None:
            # A pending retry dies with control, and so does its warning.
            _forget(held)
            issues.clear_issue(coord.hass, ISSUE_IGNORED)
            await _persist(coord)
        if inp.mode == MODE_OFF:
            return
    if boost.release_blocked(coord, inp, now):
        await boost.persist(coord)
    duty = _leased(
        inp, held, _without_block(coord, _planned_duty(coord, inp, now), now), now,
    )
    _observe(held, inp, duty, now)
    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))
    if mode != DUTY_CONTROL or _pump_off(inp, held):
        return
    await _adopt(inp, coord.entry, held, now)
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
    dhw_min = PLAN_STEP_MINUTES * dhw / (space + dhw)
    if dhw_min < SPLIT_MIN_MINUTES:
        return "space"
    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:
        return "dhw"
    return "dhw" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else "space"


def on_off_service(entity_id: str, on: bool) -> tuple[str, str]:
    """The ``(domain, service)`` that switches ``entity_id`` on or off (#1526).

    Routed by the target's own domain: Home Assistant resolves
    ``switch.turn_on`` only against ``switch.*`` entities, so the heat-pump
    slot's ``input_boolean`` and ``climate`` targets, which ``assign_entity``
    accepts, were never actuated when the call was hard-coded to ``switch``.
    """
    return entity_id.split(".", 1)[0], "turn_on" if on else "turn_off"


async def switch_supply(hass: Any, entity_id: str, on: bool) -> None:
    """Write the pump's power switch; a refused write is logged, never raised.

    The one writer of that switch: the coordinator's cycle and the early
    cut-off both call it, so neither re-spells the routing or the fence.
    """
    try:
        await hass.services.async_call(
            *on_off_service(entity_id, on), {"entity_id": entity_id}, blocking=True
        )
    except Exception as err:  # noqa: BLE001 -- the next cycle writes again
        _LOGGER.error("Error toggling heat pump switch %s: %s", entity_id, err)


def supply_write(on: bool, signals: Any) -> bool | None:
    """The switch value to write for ``on``, or ``None`` to leave the switch.

    OFF is skipped only when the pump's own mode is cooling or blocks both
    channels: an empty plan is then this integration's doing, not a decision
    to stop the pump. A single-channel block (DHW-only, heating-only) still
    commands OFF, or a summer DHW pulse would leave the supply latched while
    the tank is supposed to drift.
    """
    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):
        return on
    return None


def step_supply(inp: ArbiterInputs, boosts: Any, now: datetime) -> bool | None:
    """The supply the plan commands for the step covering ``now``, or ``None``.

    ``None`` wherever the cycle's own write does not come from the plan's
    step: a non-plan mode, an experiment's override, a stale or missing plan,
    or an instant outside it. A live boost on either channel (``boosts``, the
    coordinator's ``boost.BoostState``) is on, as ``boost.overlay`` makes the
    action the cycle writes.
    """
    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:
        return None
    if (inp.action or {}).get("mode") == "system_identification":
        return None
    if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):
        return True
    i = _step_index(inp.plan, now)
    return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)


def cycle_supply(inp: ArbiterInputs, boosts: Any, on: bool, now: datetime | None = None) -> bool:
    """The cycle's supply: the plan's command for the step it is written in.

    The action is cut at the solve, and the experiment, the fuse advisor and
    the price tile run before it is written, so a cycle can write a step late.
    :func:`note_supply` stamps the write with the step it lands in, so the
    step tick never corrected a stale ``on``: the switch then held the last
    step's command for a whole step, as after a reload's cold solve. ``on``
    stands wherever :func:`step_supply` does not speak.
    """
    step = step_supply(inp, boosts, now or dt_util.now())
    return on if step is None else step


@dataclass(frozen=True)
class SupplyWiring:
    """What the step tick reads and writes through; built by :func:`note_supply`.

    Plain values, as ``early_cutoff`` takes them: the coordinator's
    published ``arbiter_inputs`` builder, its boost record and its gated
    switch write, never the coordinator itself.
    """

    inputs: Callable[[], ArbiterInputs]
    boosts: Any
    write: Callable[[bool], Awaitable[None]]


def note_supply(held: ArbiterState, wiring: SupplyWiring, on: bool, now: datetime | None = None) -> None:
    """Record the cycle's supply command for its step; arm the step tick once.

    ``wiring.write`` is the coordinator's gated switch write, the cycle's
    own, so the tick passes the same cut-off hold and blocked-mode skip.
    """
    held.supply = (plan_step_start(now or dt_util.now()), on)
    if held.supply_unsub is not None:
        return
    inp = wiring.inputs()
    if not EntryConfig.from_mapping(inp.config).heat_pump_switch_entity:
        return

    async def _tick(_now: Any = None) -> None:
        await supply_tick(held, wiring)

    held.supply_unsub = async_track_time_interval(inp.hass, _tick, _TICK)


async def supply_tick(held: ArbiterState, wiring: SupplyWiring, now: datetime | None = None) -> None:
    """At a step boundary, write the supply where the plan's command changes.

    The cycle writes the switch once per interval, so without this a step
    change reached the pump only at the next cycle, as late as one interval
    after the boundary, and a step's duty verdict depended on the cycle's
    phase against the step grid (#2492). Only a change is written: a step
    that commands what the last one did leaves the switch alone, so an early
    cut-off still holds until the next cycle, as ``early_cutoff`` documents.
    """
    now = now or dt_util.now()
    step = plan_step_start(now)
    if held.supply is None or held.supply[0] == step:
        return
    inp = wiring.inputs()
    if inp.entry_released:
        return
    on = step_supply(inp, wiring.boosts, now)
    if on is None:
        return
    last, held.supply = held.supply[1], (step, on)
    if on != last:
        await wiring.write(on)


def release_supply(held: ArbiterState) -> None:
    """Unload: drop the step tick; idempotent."""
    unsub, held.supply_unsub = held.supply_unsub, None
    if unsub is not None:
        unsub()


def _pump_off(inp: ArbiterInputs, held: ArbiterState) -> bool:
    """Whether the configured power switch reads off.

    Switched off, the pump reports set-points of its own (tvofi's reads 25
    degC), so nothing is compared or written until it is on again; then a
    reset that is still there is rewritten like any other difference, and
    never adopted as a person's edit: the space reading before the next
    write is forgotten here (:func:`_edited`).
    """
    entity = EntryConfig.from_mapping(inp.config).heat_pump_switch_entity
    power = inp.hass.states.get(entity) if entity else None
    off = getattr(power, "state", None) == "off"
    held.space_before = None if off else held.space_before
    return off


async def release(coord: Any) -> None:
    """Unload: write the baseline row over anything still owned, then let go.

    Not the space set-point: the unload's restore (:mod:`off_restore`) has
    written its baseline back already, and the record of it is saved here.
    """
    release_listeners(coord)
    held = state_for(coord)
    release_supply(held)
    inp = coord.arbiter_inputs()
    if held.written and duty_mode(inp.config) == DUTY_CONTROL and inp.mode != MODE_OFF:
        await _command(coord, inp, replace(desired(coord, inp, None, dt_util.now()), space_setpoint=None),
                       dt_util.now())
    if held.loaded:
        await _persist(coord)


def release_listeners(coord: Any) -> None:
    held = state_for(coord)
    duty_switch.detach(coord)
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
    prefix = package_prefix(EntryConfig.from_mapping(inp.config).heat_pump_capacity_limited_entity)
    if prefix:
        entities.extend(night_mode_write_ids(prefix).values())
    if entities:
        held.unsubs.append(async_track_state_change_event(hass, entities, _changed))
    duty_switch.attach(duty_switch.record_for(coord), *_running_signal(inp))


def _running_signal(inp: ArbiterInputs) -> tuple[str | None, duty_switch.Reader]:
    """The entity whose changes say the compressor started or stopped, and its reader.

    The actual-frequency sensor where one is configured (never the number
    entity, a set-point register that echoes the last write), else the meter
    against ``on_threshold_kw``, the threshold :func:`_ran_kw` shares.
    """
    cfg = EntryConfig.from_mapping(inp.config)
    sensor, meter, states, thermal = cfg.compressor_freq_sensor, cfg.heat_pump_power_entity, inp.hass.states, inp.thermal

    def reader() -> tuple[float | None, float | None, float | None, bool]:
        if sensor:
            return resolve_reading(None, sensor, states.get, 0.0, 0.0)[0], None, None, True
        return None, state_power_kw(states.get(meter), "clamp"), on_threshold_kw(thermal.params), False

    return sensor or meter, reader


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
        "dropped": dict(held.dropped),
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
        issues.clear_issue(coord.hass, ISSUE_MANUAL)
    written = raw.get("written")
    for slot, pair in written.items() if isinstance(written, dict) else ():
        try:
            value, at = pair[0], stored_instant(pair[1], dt_util.DEFAULT_TIME_ZONE)
        except (TypeError, KeyError, IndexError):
            continue
        if at is not None and _writable(slot, value):
            held.written[slot] = (value, at)
    dropped = raw.get("dropped")
    held.dropped = {k: v for k, v in dropped.items() if _writable(k, v)} if isinstance(dropped, dict) else {}


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

#: The off-restore hook's key for the space set-point (R10-ARBITER-OFF-RESTORE).
CONSUMER = "pump_arbiter_space"


def _restorer(config: Any) -> off_restore.Restorer | None:
    """The space set-point's restore: the reading captured before the first write, degC."""
    entity = EntryConfig.from_mapping(config).space_setpoint_entity
    if not entity:
        return None
    return off_restore.Restorer(entity, write_setpoint_c, baseline_of=read_setpoint,
                                restored=_space_restored)


def _space_restored(entry: Any, _entity_id: str, _value: float) -> None:
    """The restore wrote the baseline: the slot is the arbiter's no longer.

    Its record goes, and the loop's run with it, so the next arm captures
    what the entity reads and :func:`hold` compares nothing against a write
    the entity was told over.
    """
    coord = getattr(entry, "runtime_data", None)
    held = None if coord is None else _STATES.get(coord)
    if held is not None:
        for record in (held.written, held.misses, held.retry, held.dropped):
            record.pop("space_setpoint", None)
        held.feedback = None  # its prev_c is that record too (_note_sent)


off_restore.register_consumer(CONSUMER, _restorer, write=write_setpoint_c)


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
