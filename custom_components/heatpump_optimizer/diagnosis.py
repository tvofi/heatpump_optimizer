"""Why did the room end up where it did? (T6 #52)

The accuracy tracker says HOW WRONG the last interval's prediction was; this
module says WHY. It re-runs the interval through the same thermal model the
plan used, swapping one realised input at a time into the forecast set —
realised outdoor for forecast outdoor, measured power for commanded power,
and so on — and charges each swap with the temperature shift it alone
causes. What no swap explains is the model's own residual, printed as such:
"unexplained" shrinking toward zero is the model earning trust, and a large
unexplained term is a bug report aimed at exactly the right module.

One-at-a-time is a first-order attribution, and honestly so: interactions
between inputs land in the unexplained term rather than being smeared
across the swaps pro rata. The arithmetic guarantees
``predicted + sum(contributions) + unexplained == actual`` by construction,
so the attribution always accounts for the whole residual.

One structural honesty note: in the single-zone model this step's
electrical power heats the SLAB, and the room only sees the slab a step
later — so the power swap's room contribution is genuinely ~0 there, and a
power shortfall shows up under "unexplained" until the following interval.
That is the model's answer, not a gap in the attribution: two-zone
installs (where power reaches the radiator zone within the step) see the
power swap directly.

Kept free of Home Assistant imports so it can be unit-tested directly.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import Any

import numpy as np

from .thermal_model import ThermalModel

_LOGGER = logging.getLogger(__name__)

#: The inputs a swap can attribute, in publication order. Each maps to a
#: ``simulate_step`` keyword; power is positional and handled by name too.
SWAPPABLE = (
    "electrical_power",
    "outdoor_temp",
    "wind_speed",
    "solar_radiation",
    "external_heat_kw",
)


def _room_after(model, state, inputs: dict[str, Any]) -> float:
    """The indoor temperature one step ahead under one input set."""
    after = model.simulate_step(
        replace(state),
        electrical_power=float(inputs.get("electrical_power") or 0.0),
        outdoor_temp=float(inputs.get("outdoor_temp") or 0.0),
        wind_speed=float(inputs.get("wind_speed") or 0.0),
        precipitation=float(inputs.get("precipitation") or 0.0),
        solar_radiation=float(inputs.get("solar_radiation") or 0.0),
        dt_hours=float(inputs.get("dt_hours") or 0.25),
        external_heat_kw=float(inputs.get("external_heat_kw") or 0.0),
        humidity=inputs.get("humidity"),
        hour_of_day=inputs.get("hour_of_day"),
    )
    # Two-zone installs read the indoor sensor upstairs; the residual being
    # attributed was measured against that same sensor.
    if model.params.two_zone_enabled:
        return float(after.upper_floor_temperature)
    return float(after.room_temperature)


def attribute(
    model,
    state,
    planned: dict[str, Any],
    realised: dict[str, Any],
    actual_temp: float,
) -> dict[str, Any] | None:
    """Attribute the interval's temperature residual input by input.

    ``planned`` holds the inputs the plan's prediction assumed, ``realised``
    the same keys as measured after the fact; a realised key that is None or
    non-finite keeps the planned value (nothing to attribute — the input was
    never measured). Returns None only when the baseline itself cannot run.
    """
    if not np.isfinite(actual_temp):
        return None
    try:
        baseline = _room_after(model, state, planned)
    except Exception:  # noqa: BLE001 - diagnosis must never break operations
        return None

    contributions: dict[str, float] = {}
    for key in SWAPPABLE:
        value = realised.get(key)
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(value):
            continue
        planned_value = float(planned.get(key) or 0.0)
        if abs(value - planned_value) < 1e-9:
            continue
        swapped = dict(planned)
        swapped[key] = value
        try:
            shifted = _room_after(model, state, swapped)
        except Exception:  # noqa: BLE001 - skip the swap, keep the rest
            continue
        delta = shifted - baseline
        if abs(delta) >= 0.005:
            contributions[key] = round(delta, 3)

    residual = float(actual_temp) - baseline
    unexplained = residual - sum(contributions.values())
    return {
        "predicted": round(baseline, 2),
        "actual": round(float(actual_temp), 2),
        "residual": round(residual, 3),
        "contributions": contributions,
        "unexplained": round(unexplained, 3),
    }


def diagnose_record(record, params):
    """Picklable diagnosis worker; the coordinator itself is not picklable.

    A scratch model, never the live one: ``simulate_step`` writes per-call
    scratch on the model instance, and the scheduled solve may be walking
    the same instance in another process. Same idiom as the what-if solves.
    """
    if not record:
        return None
    try:
        scratch_model = ThermalModel(replace(params))
        report = attribute(
            scratch_model,
            record["state"],
            dict(record["planned"], dt_hours=record["dt_hours"]),
            record["realised"],
            record["actual"],
        )
    except Exception as err:  # noqa: BLE001 - never break ops for insight
        _LOGGER.debug("Interval diagnosis failed: %s", err)
        return None
    if report is not None:
        report["interval_end"] = record["when"]
    return report
