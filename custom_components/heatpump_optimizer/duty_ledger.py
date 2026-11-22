"""The pump arbiter's step verdicts: what the pump did over one step, against the plan.

``pump_arbiter`` folds each pass into the step's ledger row (``_observe``);
the row is closed here. A rise of :data:`TANK_RISE_C` over the step is hot
water. Each step is ``delivered``, ``space-instead``, ``dhw-instead``,
``idle-instead``, ``not-startable`` (a hot-water step left idle on a tank at
or above the pump's own start temperature, the step's target less
``dhw_hysteresis_entity``), ``unknown`` (no power meter and no tank rise) or
``baseline``. A concurrent Heating + DHW run reads as hot water; a big draw
can hide a tank rise. Pure: a row in, a verdict out.
"""
from __future__ import annotations

from typing import Any

#: The tank rise over a step that reads as hot water, K.
TANK_RISE_C = 0.5


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
    if planned is None:
        verdict = "baseline"
    elif actual is None:
        verdict = "unknown"
    elif actual == planned or (planned == "both" and actual != "idle"):
        verdict = "delivered"
    else:
        verdict = _missed(row, planned, actual)
    return {"start": row["start"].isoformat(), "planned": planned,
            "actual": actual, "verdict": verdict}
