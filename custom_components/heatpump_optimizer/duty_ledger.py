"""The pump-duty step ledger: per plan step, the planned duty against what the pump did.

Kept in observe and in control, from what the integration already reads --
the measured electrical draw (running or not), the mode select (DHW only) and
the tank temperature (a rise of :data:`TANK_RISE_C` over the step is hot
water). Each step gets one verdict:

* ``delivered``, ``space-instead``, ``dhw-instead`` or ``idle-instead``;
* ``not-startable``: a hot-water step left idle on a tank at or above the
  pump's own start temperature, the step's target less ``dhw_hysteresis_entity``;
* ``device-fault``: a pass inside the step found the pump's fault alarm
  holding actuation (``fault_hold``);
* ``unknown`` (no power meter and no tank rise) or ``baseline``.

A concurrent Heating + DHW run reads as
hot water; a big draw can hide a tank rise. A row is closed when its step
ends, so the step in which a long fault began keeps its own verdict.

A leaf over ``plan_step``: ``pump_arbiter`` computes what each pass read (the
run threshold, the DHW mode, the start temperature) and passes it in, and owns
the record (``ArbiterState``) the rows live on.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .plan_step import plan_step_start

#: A tank rise over one step that reads as hot water, K.
TANK_RISE_C = 0.5
#: How long into a step the meter still reads the last step (#2492 carry 8).
#: The supply tick writes the switch in the step's first tick, and the
#: arbiter's tick in that same minute reads the draw from before the write.
RUN_SETTLE = timedelta(minutes=1)


def observe(held: Any, inp: Any, duty: str | None, now: datetime, *, ran: bool | None,
            dhw_mode: bool, start_below: Any, faulted: bool) -> None:
    """Fold this pass into the current step's row; close the last one.

    ``planned`` is re-frozen whenever a new plan is adopted inside the step.
    The cycle's re-solve can move a slot onto the current step, and the
    switch is written from that plan, so the step is scored against the
    plan that actuated it, not the one in force at its first tick. ``ran`` is
    ``None`` with no meter reading, or one inside :data:`RUN_SETTLE` of the
    step's start, which folds into neither ``measured`` nor ``ran``.
    """
    held.last_duty = duty
    start = plan_step_start(now)
    tank = getattr(inp.state, "dhw_temperature", None)
    row = held.step
    if row is None or row["start"] != start:
        if row is not None:
            held.log.append(step_verdict(row, tank))
        held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
                           "measured": False, "ran": False, "dhw_mode": False, "faulted": False}
        row["start_below"] = start_below
    elif row["plan"] is not inp.plan:
        row["planned"], row["plan"] = duty, inp.plan
    if ran is not None and now - start >= RUN_SETTLE:
        row["measured"] = True
        row["ran"] = row["ran"] or ran
    row["dhw_mode"] = row["dhw_mode"] or dhw_mode
    row["faulted"] = row["faulted"] or faulted


def _not_startable(row: dict[str, Any]) -> bool:
    """Whether the step's tank opened at or above the pump's start temperature.

    Its own hysteresis then kept the pump off, so an idle hot-water step says
    nothing about whether the pump obeys the plan (Bankaifan, #3440).
    """
    start, tank = row.get("start_below"), row["tank"]
    return start is not None and tank is not None and float(tank) >= start


def _missed(row: dict[str, Any], planned: str, actual: str) -> str:
    """The verdict for a step that did something other than its plan."""
    if planned == "dhw" and actual == "idle" and _not_startable(row):
        return "not-startable"
    return f"{actual}-instead"


def step_verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
    """What the pump did over one step, against what the plan wanted."""
    rose = None not in (tank, row["tank"]) and float(tank) - float(row["tank"]) >= TANK_RISE_C
    hot = rose or row["dhw_mode"]
    if row["measured"]:
        actual: str | None = ("dhw" if hot else "space") if row["ran"] else "idle"
    else:
        actual = "dhw" if rose else None
    planned = row["planned"]
    if row.get("faulted"):
        result = "device-fault"
    elif planned is None:
        result = "baseline"
    elif actual is None:
        result = "unknown"
    elif actual == planned or (planned == "both" and actual != "idle"):
        result = "delivered"
    else:
        result = _missed(row, planned, actual)
    return {"start": row["start"].isoformat(), "planned": planned,
            "actual": actual, "verdict": result}
