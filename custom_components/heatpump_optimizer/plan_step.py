"""The plan's step grid: how wide one step is, and which step an instant is in.

One concern with one owner. The optimizer plans at this resolution, every
forecast series is resampled to it, and the pump arbiter keys its ledger row
and its silent-window lookup on the same step. Two modules spelled the floor
and its width apart until R10-PUMP-MODEL -- ``coordinator._solve_anchor`` on
``FORECAST_STEP_MINUTES``, ``pump_arbiter._step_start`` on a literal 15 -- and
they agreed only while the two widths happened to be equal. A leaf module, so
both import it and neither imports the other.
"""
from __future__ import annotations

from datetime import datetime
from typing import Final

#: Resolution the optimizer plans at, and therefore the resolution every
#: forecast series is resampled to and the pump arbiter's ledger is keyed on.
PLAN_STEP_MINUTES: Final = 15

#: One plan step in hours, the unit ``quiet_windows.step_actions`` takes.
PLAN_STEP_HOURS: Final = PLAN_STEP_MINUTES / 60


def plan_step_start(now: datetime) -> datetime:
    """``now`` floored onto the plan's step grid, on the solver's clock.

    ``coordinator._forecast_arrays`` anchors every price and weather step at
    ``midnight + PLAN_STEP_MINUTES·k``, so a solve labelled with the raw
    instant (12:07) published timestamps seven minutes off the quarter its own
    arrays described -- and pins, capacity-window offsets, filed lead promises
    and every card timestamp inherited that skew. The granularity is the
    forecast grid's, deliberately not ``time_step_minutes``: if the two ever
    diverge the arrays disagree first, and the anchor must follow the arrays.
    Wall-clock lookups INTO the plan (``get_current_action``,
    ``_async_drive_pumps``) stay on the raw clock -- they ask what applies now,
    not where step 0 is. The pump arbiter's ledger row and silent-window lookup
    read this same step. ``fold`` and ``tzinfo`` are carried through, so the
    autumn hour's two passes stay two steps.
    """
    step = int(PLAN_STEP_MINUTES)
    return now.replace(minute=(now.minute // step) * step, second=0, microsecond=0)
