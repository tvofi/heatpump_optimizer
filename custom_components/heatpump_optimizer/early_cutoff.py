"""Early cut-off inside a plan interval: the room is warm enough, stop now.

The switch is written once per cycle and the plan re-solves once per
interval, so between two cycles nothing reacts to the room. A pump that
delivers more heat than the plan assumed keeps doing so for the rest of the
interval. This module listens to the room thermometer, as the peak guard
listens to the meter. When the room passes the active comfort target plus
:data:`MARGIN_K` on a step the plan gave to space heating, it switches the
pump off once. The next cycle writes the plan's own action again, so the
pump resumes then (decision recorded on #201, comment 6067353918).

**The threshold** is the higher of the active comfort target and the room
temperature the plan predicts for the end of the current step, plus the margin. A plan that pre-heats
into a cheap hour means to run the room above the target. Cutting that off
at the target would undo the price decision the plan just made, so the
cut-off only acts on overshoot past what the plan itself expected.

**A guard, measured inert.** In every closed-loop case measured
(``dev/audit/harnesses/early_cutoff_closed_loop.py``) the 30-minute
re-solve already had the pump off before the room passed this threshold, so
the cut-off never fired. The decision's literal rule (target + margin alone)
did act, and cut a correct plan's pre-heat on the null control, so it does
not ship. The measured overshoot goes into the floor store, which the slab
observer corrects; this module stays as the guard for a room that does run
past its plan within one interval.

**The margin is a constant, not an option.** An options-flow field moves the
``tests/golden/config_flow.json`` fixture, which only a claim can move, and
adds a string to both translation files. The decision fixed 0.5 K, and
nothing yet measures what another value would buy.

**Short cycles.** The integration has no minimum on-time or off-time of its
own. The pump's own controller enforces its compressor's limits, but a
power switch that cuts the supply bypasses them. So this module adds both:
it does not cut a pump that has been on for less than :data:`MIN_ON`, or
when the next scheduled cycle is less than :data:`MIN_OFF` away; and an
early refresh inside :data:`MIN_OFF` of a cut keeps the pump off
(:func:`allow_on`). It cuts at most once per cycle.

**What it leaves alone.** It acts only on a step whose duty is space heating
alone. Hot water, a both step, idle, a boost on either channel, a
disinfection hold, a running defrost and a tank below its minimum are all
exempt, because the power switch stops the tank as well as the house. A
non-plan mode (comfort, boost, off) and a stale plan are exempt too, as are
an install with no switch and a two-zone house whose lower floor is below
its target. It writes only the power switch, through ``pump_arbiter.switch_supply``,
the switch's one writer. The ECL110 displacement, the arbiter's slots and
the peak guard keep their own writers. The arbiter
writes nothing while the switch reads off, so it cannot switch the pump
back on inside the cycle.

**The learners.** A cut interval did not run the power the plan commanded,
so every learner that replays commanded power would read it wrong.
:attr:`CutoffState.interval_cut` is the one reason the coordinator's
``_learning_frozen`` returns for it (:data:`FREEZE_CUT`).

**What it takes.** Plain values: the record from :func:`state_for`, the
coordinator's ``arbiter_inputs`` builder (the published read-only view the
arbiter reads), the boost record and the optimizer config. No function here
receives the coordinator itself, except :func:`state_for`, which keys on it.
"""
from __future__ import annotations

import bisect
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from weakref import WeakKeyDictionary

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .boost import CHANNEL_DHW, CHANNEL_SPACE, BoostState
from .const import MODE_AUTO, MODE_ECONOMY, ROOM_AIR_RANGE_C
from .entry_config import EntryConfig
from .inputs import parse_bool, temperature_c
from .pump_arbiter import ArbiterInputs, step_duty, switch_supply

_LOGGER = logging.getLogger(__name__)

#: Kelvin above the threshold's base before the pump is cut (decision 0.5 K).
MARGIN_K = 0.5
#: The shortest run a cut may end; the plan's own step is 15 minutes.
MIN_ON = timedelta(minutes=10)
#: The shortest stop a cut may cause before the next cycle can restart it.
MIN_OFF = timedelta(minutes=10)


#: The ``_learning_frozen`` reason for an interval the cut-off ended early.
FREEZE_CUT = "early_cutoff"


@dataclass
class CutoffState:
    """Per-coordinator record: the listener, this cycle, the last cut."""

    unsub: Callable[[], None] | None = None
    cycle_end: datetime | None = None
    cut_this_cycle: bool = False
    #: Whether the cycle before this one was cut; see :attr:`interval_cut`.
    cut_last_cycle: bool = False
    #: When the last cut was written (UTC); an early refresh inside
    #: :data:`MIN_OFF` of it keeps the pump off (:func:`allow_on`).
    cut_at: datetime | None = None
    wiring: CutoffInputs | None = None
    count: int = 0
    last: dict[str, Any] | None = None
    #: Why the last reading above the threshold did not cut.
    last_held: str | None = None

    @property
    def interval_cut(self) -> bool:
        """Whether the interval a learner replays may have been cut.

        Both cycles count: a learner that runs before this cycle's arm
        replays the cycle still open, one that runs after it the cycle just
        closed. Freezing one interval too many is the fail-closed side.
        """
        return self.cut_this_cycle or self.cut_last_cycle


@dataclass(frozen=True)
class CutoffInputs:
    """What one room reading is judged against; built by :func:`arm`."""

    inputs: Callable[[], ArbiterInputs]
    boosts: BoostState
    opt_config: Any


_STATES: WeakKeyDictionary[Any, CutoffState] = WeakKeyDictionary()


def state_for(coord: Any) -> CutoffState:
    """In-memory record for this coordinator, created on first use."""
    return _STATES.setdefault(coord, CutoffState())


async def arm(
    held: CutoffState,
    inputs: Callable[[], ArbiterInputs],
    boosts: BoostState,
    opt_config: Any,
    on_unload: Callable[[Callable[[], None]], Any],
    now: datetime | None = None,
) -> None:
    """Start a plan cycle: the cycle's own write resumes the pump.

    Called by every cycle before it actuates. The record of this cycle's cut
    is cleared, and the listener is registered on first use, or dropped when
    the entry is released or no switch or room thermometer is configured.
    """
    now = now or dt_util.now()
    held.wiring = CutoffInputs(inputs, boosts, opt_config)
    inp = inputs()
    cfg = EntryConfig.from_mapping(inp.config)
    # In UTC: local wall-clock arithmetic is an hour off across a DST change.
    held.cycle_end = dt_util.as_utc(now) + timedelta(minutes=cfg.optimization_interval)
    held.cut_last_cycle, held.cut_this_cycle = held.cut_this_cycle, False
    room = cfg.indoor_temp_entity
    if inp.entry_released or not room or not cfg.heat_pump_switch_entity:
        release(held)
        return
    if held.unsub is None:

        @callback
        def _changed(event: Any) -> None:
            if held.wiring is not None:
                on_room_event(held, held.wiring, event)

        held.unsub = async_track_state_change_event(inp.hass, [room], _changed)
        # Dropped with the entry, as every other registration is (#236).
        on_unload(lambda: release(held))
        _LOGGER.debug("Early cut-off listening on %s", room)


def allow_on(held: CutoffState, on: bool, now: datetime | None = None) -> bool:
    """``on``, unless a cut within :data:`MIN_OFF` must keep the pump off.

    The scheduled cycle never lands inside that window, because a cut is
    refused with less than :data:`MIN_OFF` to the cycle end. An early
    refresh (a mode change, a manual plan, a button) can, and would
    otherwise write the plan's ``on`` a minute after the cut. A step the
    cut-off would not touch -- a boost, hot water, a non-plan mode -- is
    let through.
    """
    if not on or held.cut_at is None or held.wiring is None:
        return on
    now = dt_util.as_utc(now or dt_util.now())
    if now - held.cut_at >= MIN_OFF:
        return True
    return _exempt(held.wiring.inputs(), held.wiring.boosts, now) is not None


def release(held: CutoffState) -> None:
    """Drop the room listener; idempotent."""
    unsub, held.unsub = held.unsub, None
    if unsub is not None:
        unsub()


def _exempt(inp: ArbiterInputs, boosts: BoostState, now: datetime) -> str | None:
    """Why this step is not one the cut-off may touch, or ``None``."""
    if inp.mode not in (MODE_AUTO, MODE_ECONOMY):
        return "mode"
    if inp.plan_stale or not inp.action or not inp.action.get("heat_pump_on"):
        return "plan_off"
    if inp.plan is None or step_duty(inp.plan, now) != "space":
        return "duty"
    if boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now):
        return "boost"
    if inp.disinfecting:
        return "disinfecting"
    return _plant_exempt(inp)


def _plant_exempt(inp: ArbiterInputs) -> str | None:
    """The plant states that outrank a warm room: defrost, a cold tank."""
    defrost = EntryConfig.from_mapping(inp.config).heat_pump_defrost_entity
    flag = inp.hass.states.get(defrost) if defrost else None
    if flag is not None and parse_bool(getattr(flag, "state", None)):
        return "defrost"
    params, state = inp.params, inp.state
    if getattr(params, "dhw_enabled", False) and float(state.dhw_temperature) < float(
        params.dhw_min_temp
    ):
        return "tank_cold"
    return None


def threshold(inp: ArbiterInputs, opt_config: Any, now: datetime) -> float:
    """The room temperature above which the pump is cut, in degC."""
    local = dt_util.as_local(now)
    base = float(opt_config.get_comfort_temp(local.hour + local.minute / 60.0, when=local))
    return max(base, *_planned_room(inp.plan, now)) + MARGIN_K


def _planned_room(plan: Any, now: datetime) -> list[float]:
    """The plan's predicted room temperature at the end of the step covering ``now``.

    The end, never the start: the trajectory's first point is the room the
    solve measured, so a room already warm at the solve would raise its own
    threshold and the cut-off could never act on it.
    """
    i = bisect.bisect_right(list(getattr(plan, "timestamps", None) or []), now) - 1
    trajectory = list(getattr(plan, "room_temp_trajectory", None) or [])
    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []


def _cycle_guard(inp: ArbiterInputs, held: CutoffState, now: datetime) -> str | None:
    """The short-cycle guards: once per cycle, a minimum run, a minimum stop."""
    if held.cut_this_cycle:
        return "already_cut"
    switch = inp.hass.states.get(EntryConfig.from_mapping(inp.config).heat_pump_switch_entity)
    if getattr(switch, "state", None) != "on":
        return "switch_not_on"
    since = getattr(switch, "last_changed", None)
    utc = dt_util.as_utc(now)
    # A missing stamp, or one ahead of the clock, is an unknown run (#775).
    if since is None or dt_util.as_utc(since) > utc or utc - dt_util.as_utc(since) < MIN_ON:
        return "min_on"
    if held.cycle_end is None or held.cycle_end - utc < MIN_OFF:
        return "min_off"
    return None


def _second_zone_cold(inp: ArbiterInputs, limit: float) -> bool:
    """Two zones: the cut must not starve a lower floor below its target."""
    if not getattr(inp.params, "two_zone_enabled", False):
        return False
    return float(inp.state.lower_floor_temperature) < limit - MARGIN_K


def _reading(event: Any) -> float | None:
    """The event's room temperature in degC, or ``None`` if implausible."""
    new_state = getattr(event, "data", {}).get("new_state")
    unit = (getattr(new_state, "attributes", None) or {}).get("unit_of_measurement")
    room = temperature_c(getattr(new_state, "state", None), unit)
    low, high = ROOM_AIR_RANGE_C
    return room if room is not None and low <= room <= high else None


def on_room_event(held: CutoffState, wiring: CutoffInputs, event: Any) -> None:
    """One room reading: cut the pump once when it is past the threshold."""
    if (room := _reading(event)) is None:
        return
    now = dt_util.now()
    inp = wiring.inputs()
    if inp.entry_released:
        release(held)
        return
    if _exempt(inp, wiring.boosts, now) is not None:
        return
    limit = threshold(inp, wiring.opt_config, now)
    if room <= limit:
        return
    reason = _cycle_guard(inp, held, now)
    if reason is None and _second_zone_cold(inp, limit):
        reason = "zone_cold"
    if reason is not None:
        held.last_held = reason
        return
    held.cut_this_cycle = True
    held.cut_at = dt_util.as_utc(now)
    held.count += 1
    switch = str(EntryConfig.from_mapping(inp.config).heat_pump_switch_entity)
    held.last = {"at": now.isoformat(), "room_c": room, "threshold_c": limit, "switch": switch}
    _LOGGER.info(
        "Early cut-off: room %.2f degC is above %.2f degC (plan or target + %.1f K); "
        "switching %s off until the next plan cycle",
        room, limit, MARGIN_K, switch,
    )
    inp.hass.async_create_task(switch_supply(inp.hass, switch, False))


def diagnostics_view(held: CutoffState) -> dict[str, Any]:
    """The diagnostics view: the constants, this cycle, the last cut."""
    return {
        "listening": held.unsub is not None,
        "margin_k": MARGIN_K,
        "min_on_minutes": MIN_ON.total_seconds() / 60.0,
        "min_off_minutes": MIN_OFF.total_seconds() / 60.0,
        "cut_this_cycle": held.cut_this_cycle,
        "interval_cut": held.interval_cut,
        "count": held.count,
        "last": dict(held.last) if held.last else None,
        "last_held": held.last_held,
    }
