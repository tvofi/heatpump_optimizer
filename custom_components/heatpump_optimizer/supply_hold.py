"""The supply switch's minimum run and minimum pause.

The plan switches the supply at its 15-minute step boundaries, but a
re-solve, a cycle, a restart or a late write can land inside a step, and the
supply switch bypasses the compressor's own interlocks. So the one gate the
cycle and the step tick write through (``coordinator._write_supply``) holds a
write back that would

* end a run younger than :data:`MIN_RUN`;
* end a pause younger than :data:`MIN_PAUSE`;
* start a run the plan ends within :data:`MIN_RUN`: an on write inside a
  step whose next step is planned off. Not where the step heats the tank
  and the tank needs it now (:func:`tank_reason`): that run starts, and the
  minimum carries it past the boundary.

**One clock.** A run's and a pause's age is the switch's own ``last_changed``,
as ``early_cutoff`` measures its minimum run, so a run started by a boost, a
fixed mode, the user or the cut-off counts like one this gate wrote. A reload
of the integration leaves the stamp alone. A restart of Home Assistant builds
a new state machine whose first write stamps the restart
(``tests/ha_contract.py``, ``StateMachine.async_set``), so a pump found
running reads as a run that started then and is held on for at most
:data:`MIN_RUN`, and a pump found stopped is held off for at most
:data:`MIN_PAUSE`. A write that leaves the state keeps the stamp. A stamp missing or ahead of the clock is an unknown age and
holds nothing (#775: unknowable, never 0).

**Running and stopped** are read as ``pump_arbiter._pump_off`` reads them:
``off`` is stopped, any other readable state is running, so a ``climate`` or
``input_boolean`` target (``on_off_service``) is held like a switch.

**Only a delay.** The gate never makes a write; it returns ``None`` for one it
holds and sets :attr:`ArbiterState.supply_held`, and ``pump_arbiter.
supply_tick`` retries it each minute with the step's own command, or the
action's where the plan gives none, so it lands once its minimum has passed.
A write of ``None``, a non-plan mode, a live boost, system identification and
an unreadable switch pass unchanged. Both minimums sit below the plan's step,
so a write on a step boundary after a step-long run or pause is never held.

**The learners.** A held interval ran other than the plan commanded, so
:func:`freeze_reason` freezes it through ``_learning_frozen``
(:data:`FREEZE_HELD`), as ``early_cutoff`` freezes a cut one.

The minimums are constants, not options, for the reason ``early_cutoff``
gives for its margin; ``early_cutoff`` reads them too.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .boost import CHANNEL_DHW, CHANNEL_SPACE
from .const import MODE_AUTO, MODE_ECONOMY
from .entry_config import EntryConfig
from .plan_step import PLAN_STEP_MINUTES, plan_step_start
from .pump_arbiter import ArbiterInputs, ArbiterState, step_duty, step_supply, supply_switch

#: The shortest run and pause the gate lets a write end; the early cut-off's too.
MIN_RUN = timedelta(minutes=10)
MIN_PAUSE = timedelta(minutes=10)

#: The ``_learning_frozen`` reason for an interval in which a write was held.
FREEZE_HELD = "supply_held"

#: Switch states that say nothing about the pump.
_UNREADABLE = (None, "unavailable", "unknown")


def hold_supply(held: ArbiterState, inputs: Any, boosts: Any, value: bool | None,
                now: datetime | None = None) -> bool | None:
    """``value``, or ``None`` while a minimum holds the write back.

    ``inputs`` is the coordinator's ``arbiter_inputs`` builder, called only
    for a write that is not ``None``.
    """
    held.supply_held = False
    if value is None:
        return value
    now = dt_util.as_utc(now or dt_util.now())
    inp = inputs()
    age = _held_for(inp, value, now)
    if age is None or _passes(inp, boosts, now):
        return value
    wait = (age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value else age < MIN_RUN
    if wait:
        held.supply_held, held.held_until = True, now + _freeze_span(inp.config)
    return None if wait else value


def freeze_reason(held: ArbiterState, now: datetime | None = None) -> str | None:
    """:data:`FREEZE_HELD` while a learner's interval may have had a write held, else ``None``."""
    until = held.held_until
    held_now = until is not None and dt_util.as_utc(now or dt_util.now()) < until
    return FREEZE_HELD if held_now else None


def _freeze_span(config: Any) -> timedelta:
    """Two plan intervals, as ``early_cutoff.CutoffState.interval_cut`` counts
    the open cycle and the one just closed: freezing one too many is the
    fail-closed side. Fixed when the write is held, where the config is in hand.
    """
    return 2 * timedelta(minutes=EntryConfig.from_mapping(config).optimization_interval)


def tank_reason(inp: ArbiterInputs) -> str | None:
    """Why the tank must be heated now: a disinfection hold or a cold tank."""
    if inp.disinfecting:
        return "disinfecting"
    params = inp.params
    cold = getattr(params, "dhw_enabled", False) and float(inp.state.dhw_temperature) < float(
        params.dhw_min_temp
    )
    return "tank_cold" if cold else None


def _held_for(inp: ArbiterInputs, value: bool, now: datetime) -> timedelta | None:
    """How long the switch has been in the state ``value`` would end, or ``None``.

    ``None`` where the write changes nothing, the switch is unreadable or its
    stamp is missing or ahead of ``now``.
    """
    switch = supply_switch(inp)
    state = getattr(switch, "state", None)
    if state in _UNREADABLE or (state != "off") is value:
        return None
    return switch_age(switch, now)


def switch_age(switch: Any, now: datetime) -> timedelta | None:
    """How long the switch has held its value, by its ``last_changed``, or ``None``.

    The run length is the age of the VALUE: ``inputs.state_stamp`` answers
    when the entity was last heard from, which a re-reported ``on`` resets.
    A stamp missing or ahead of ``now`` is unknowable, never 0 (#775).
    """
    since = getattr(switch, "last_changed", None)
    if since is None:
        return None
    since, now = dt_util.as_utc(since), dt_util.as_utc(now)
    return None if since > now else now - since


def _passes(inp: ArbiterInputs, boosts: Any, now: datetime) -> bool:
    """A write the gate never holds: a non-plan mode, an experiment, a boost."""
    return (inp.mode not in (MODE_AUTO, MODE_ECONOMY)
            or (inp.action or {}).get("mode") == "system_identification"
            or boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now))


def _ends_soon(inp: ArbiterInputs, boosts: Any, now: datetime) -> bool:
    """A start whose run the plan ends within :data:`MIN_RUN`, the tank not owed it."""
    nxt = plan_step_start(now) + timedelta(minutes=PLAN_STEP_MINUTES)
    if nxt - now >= MIN_RUN or step_supply(inp, boosts, nxt) is not False:
        return False
    return not (step_duty(inp.plan, now) in ("dhw", "both") and tank_reason(inp))
