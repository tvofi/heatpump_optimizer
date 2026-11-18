"""The plan's step grid: how wide one step is, and which step an instant is in.

One concern with one owner. The optimizer plans at this resolution, every
forecast series is resampled to it, and the pump arbiter keys its ledger row
and its silent-window lookup on the same step. Two modules spelled the floor
and its width apart until R10-PUMP-MODEL -- ``coordinator._solve_anchor`` on
``FORECAST_STEP_MINUTES``, ``pump_arbiter._step_start`` on a literal 15 -- and
they agreed only while the two widths happened to be equal. A leaf module, so
both import it and neither imports the other.

It owns "the step covering an instant" too (round-11 ADR-001 part 2,
D7-s3-03): four readers bisected the plan's stamps apart, and the two with no
end rule held the last step's value at any instant past the plan.
"""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Final

#: Resolution the optimizer plans at, and therefore the resolution every
#: forecast series is resampled to and the pump arbiter's ledger is keyed on.
PLAN_STEP_MINUTES: Final = 15

#: One plan step in hours, the unit ``quiet_windows.step_actions`` takes.
PLAN_STEP_HOURS: Final = PLAN_STEP_MINUTES / 60

#: One plan step as a span, the width of a plan's last step.
PLAN_STEP: Final = timedelta(minutes=PLAN_STEP_MINUTES)


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


def covering_index(
    starts: Sequence[Any], now: Any, lone_span: Any, last_span: Any = None
) -> int | None:
    """The index of the entry whose ``[start, end)`` covers ``now``, or ``None``.

    ``starts`` is sorted. An entry ends where the next begins; the last ends
    one predecessor's span after its own start (``lone_span`` when it is the
    only entry), so a series its source stopped extending stops covering now
    (R10 N-no-expiry, #2229: ``bisect_right(...) - 1`` alone held the last
    entry current forever, and a stale price was published and booked). Before
    the first entry nothing covers ``now`` either; a caller wanting the head
    there says so itself. A series on a fixed grid passes its width as
    ``last_span``: its last entry is that wide whatever gap precedes it. Works
    on any ordered stamps whose difference adds back to a stamp: datetimes
    with timedelta spans, or epoch seconds.
    """
    i = bisect_right(starts, now) - 1
    if i < 0:
        return None
    if i + 1 < len(starts):
        return i
    if last_span is not None:
        span = last_span
    else:
        span = starts[i] - starts[i - 1] if i > 0 else lone_span
    return i if now < starts[i] + span else None


def plan_step_index(result: Any, now: datetime) -> int | None:
    """The index of the plan step covering ``now``, or ``None`` outside the plan.

    The one reading of a plan's ``timestamps`` that every series lookup takes
    its index from (:func:`covering_index`). A plan is on the step grid, so
    its last step is one :data:`PLAN_STEP` wide, whatever gap precedes it --
    the arbiter's ``_step_index`` rule this replaced: past it the plan says
    nothing.
    """
    stamps = list(getattr(result, "timestamps", None) or [])
    return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)
