"""The what-if's own state and arithmetic, off the coordinator (#2257).

``async_simulate`` prices a hypothetical configuration against the plan in
force. What it owns besides the solves is here.

THE SCRATCH COPIES. A what-if never writes the configuration it reads:
``scratch_copies`` deep-copies the solve's configuration and parameters and
applies the overrides to the copies (#240), refusing a spelling it cannot
parse before any solve starts.

THE USER'S SLOT. A solve is seconds of CPU, so user callers get one start
per ``SIMULATE_MIN_INTERVAL_SECONDS`` and the answer of the last one in
between. Background callers neither read nor write the slot or that answer.

THE STEADY FIGURE. The plan's spend from the measured house carries a one-off:
the coast a cooler schedule starts with, the heat-up a warmer one does, and a
month multiplies it by every horizon. The monthly figure the panel, the cap
tile and the fuse advisor read carries none, in one of two ways. An ask that
moves a comfort target (``schedule_days``) is priced with no further solve,
by ``price_tiles.schedule_figure``: two plans' money read such an ask against
its own sign. Any other ask is THE STEADY PAIR: two more solves, the live
configuration and the what-if one, each from a start held at its own schedule
(``SolveInputs.held_start``). The live side depends on nothing the what-if
overrides, so it is kept, one slot, for the next what-if against the same
plan from the same start at the same solve instant. A pair that fails leaves
the answer without the figure and the slot as it was: no caller falls back
to a figure that prices something else.

THE REFERENCE DAY. ``schedule_figure``'s energy is
``HeatPumpOptimizer.reference_day``'s, and three things would otherwise ride
in it beside the schedule. The start: each day's thermostat loop runs twice
and the second pass, started where the first ended, is the one counted, so
the day is one of an unbroken run of such days and neither a coast nor a
heat-up. The hour's weather: a day-window change moves heat across the
window's edge, and priced in each hour's own weather the difference carried
two days' COP and read against the change, so every series is its mean over
the horizon's first day. The weekday: a schedule with weekend temperatures
holds other setpoints from Friday night on, so one day's energy moved with
the day asked on and a weekend ask moved no setpoint on a Monday; the seven
days from the horizon's start are each priced, one pair of passes per
distinct day, and averaged. Two passes settle what the setpoints hold. They
do not settle a store no setpoint holds (a two-zone house's buffer without a
valve keeps a few tenths a month of the measured tank), nor a thermostat that
never reaches its setpoint, whose days tie
(``dev/audit/harnesses/r10_advisor_steady_seams.py``, arm ``fields``).

The state lives in a per-coordinator side table (``boost.py``'s discipline),
so the coordinator class holds no state it never computes with.
"""
from __future__ import annotations

import copy
import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from weakref import WeakKeyDictionary

from .const import SIMULATE_MIN_INTERVAL_SECONDS
from .dhw_schedule import DHWWindowError, parse_weekly_windows, parse_windows
from .drift import utc_elapsed_seconds
from .plan_slots import plan_slots

_LOGGER = logging.getLogger(__name__)

#: The answer's steady figure; absent when the pair did not run or failed.
STEADY_KEY = "monthly_steady_cost_delta"

# The what-if's override spelling: config fields by cast (the schedule
# hours are integers because they index hours), and the parameter fields
# whose scratch name differs from the override key.
OVERRIDE_CONFIG_CASTS: tuple[tuple[str, Any], ...] = (
    ("target_temp", float),
    ("min_temp", float),
    ("max_temp", float),
    ("comfort_temp_day", float),
    ("comfort_temp_night", float),
    ("comfort_temp_day_weekend", float),
    ("comfort_temp_night_weekend", float),
    ("holiday_comfort_day", float),
    ("holiday_comfort_night", float),
    ("comfort_weight", float),
    ("day_start_hour", int),
    ("day_end_hour", int),
)
OVERRIDE_PARAM_FIELDS: tuple[tuple[str, str], ...] = (
    ("max_temp", "comfort_ceiling"),
    ("dhw_setpoint", "dhw_setpoint"),
    ("dhw_min_temperature", "dhw_min_temp"),
)


class Refused(ValueError):
    """An override the what-if cannot price; its text is the answer's error."""


def scratch_copies(config: Any, params: Any, overrides: Mapping[str, Any]) -> tuple[Any, Any]:
    """Private copies of ``config`` and ``params`` with ``overrides`` applied.

    #240: ``replace`` copies scalars and shares the rest by reference, so the
    what-if carried the LIVE learner, draw pattern and windows into the
    executor, where ``observe`` could write them mid-solve. Hence deep copies.
    """
    scratch_config = copy.deepcopy(config)
    for key, cast in OVERRIDE_CONFIG_CASTS:
        if key in overrides:
            setattr(scratch_config, key, cast(overrides[key]))
    scratch_params = copy.deepcopy(params)
    # max_temp reaches the model's comfort ceiling: the valve's default
    # target follows it, so a simulated ceiling change moves both.
    for key, attr in OVERRIDE_PARAM_FIELDS:
        if key in overrides:
            setattr(scratch_params, attr, float(overrides[key]))
    if "dhw_windows" in overrides:
        spec = str(overrides["dhw_windows"]).strip()
        if not spec:
            # An explicitly empty schedule means "no demand windows", which
            # is a legitimate thing to simulate: it is what the plan looks
            # like with hot water availability unconstrained.
            scratch_params.dhw_windows = []
            scratch_params.dhw_weekly_windows = None
        else:
            try:
                scratch_params.dhw_windows = parse_windows(spec)
                scratch_params.dhw_weekly_windows = parse_weekly_windows(spec)
            except DHWWindowError as err:
                raise Refused(f"invalid_windows: {err}") from err
    return scratch_config, scratch_params


@dataclass
class WhatIfState:
    """One coordinator's what-if state: the user's slot and the kept live side."""

    #: When the last user what-if started a solve.
    last_at: datetime | None = None
    #: That what-if's answer, returned while the slot is spent.
    answer: dict[str, Any] = field(default_factory=dict)
    #: The kept live steady solve: what it was solved against, and its result.
    live_steady: tuple[Any, Any, Any] | None = None


_STATES: WeakKeyDictionary[Any, WhatIfState] = WeakKeyDictionary()


def state_for(owner: Any) -> WhatIfState:
    """``owner``'s what-if state, created on first use."""
    return _STATES.setdefault(owner, WhatIfState())


def limited_answer(held: WhatIfState, now: datetime) -> dict[str, Any] | None:
    """The last answer, marked, while the user's slot is spent; else None."""
    if (
        held.last_at is not None
        and utc_elapsed_seconds(now, held.last_at)
        < SIMULATE_MIN_INTERVAL_SECONDS
    ):
        return {
            **held.answer,
            "rate_limited": True,
        }
    return None


def slot_counts(simulated: Any, dt_hours: float) -> dict[str, int]:
    """How many runs each channel of the simulated plan has, as the plan view cuts them."""
    space, dhw = list(simulated.power_schedule), list(simulated.dhw_power_schedule or [])
    prices = list(simulated.prices)
    return {
        "dhw_slots": len(plan_slots(simulated.timestamps, dhw, prices, dt_hours, other_powers=space)),
        "space_slots": len(plan_slots(simulated.timestamps, space, prices, dt_hours, other_powers=dhw)),
    }


def schedule_days(live: tuple[Any, Any], sim: tuple[Any, Any]) -> tuple[float, float] | None:
    """The live and the what-if side's day energy when the ask moves a comfort target; else None.

    Each side is an unsolved optimizer and its inputs, built at one instant
    from one set of arrays, and ``reference_day`` gives each one's setpoints
    over the week ahead and the energy a thermostat holding them draws on its
    average day. The branch is taken on
    the setpoints, element by element, never on the energies: two schedules
    a thermostat cannot tell apart (held at the pump's maximum both ways) are
    still a schedule ask, whose figure is then 0, and an ask that moves no
    setpoint reads the pair whatever its energies.
    """
    (live_targets, live_kwh), (sim_targets, sim_kwh) = (o.reference_day(i) for o, i in (live, sim))
    return None if live_targets == sim_targets else (live_kwh, sim_kwh)


async def steady_pair(
    held: WhatIfState, anchor: Any, key: Any, solve: Callable[[Mapping[str, Any]], Awaitable[Any]],
    overrides: Mapping[str, Any],
) -> tuple[Any, Any] | None:
    """The live and the what-if plan from held starts, live first; None when either fails.

    ``solve`` runs one held-start solve of the overrides it is handed, on an
    optimizer of its own. The live side is reused when the kept one was
    solved against this very ``anchor`` (the plan object, or the background
    caller's record: identity, never equality, a re-solve hands out a new
    one) under an equal ``key`` (the solve instant, the measured start and
    whatever else the caller's live side reads). Nothing is kept from a pair
    that failed.
    """
    kept = held.live_steady
    try:
        if kept is not None and kept[0] is anchor and kept[1] == key:
            live = kept[2]
        else:
            live = await solve({})
        sim = await solve(overrides)
    except Exception as err:  # noqa: BLE001 - the figure is dropped, the answer stands
        _LOGGER.debug("What-if steady pair failed: %s", err)
        return None
    held.live_steady = (anchor, key, live)
    return live, sim
