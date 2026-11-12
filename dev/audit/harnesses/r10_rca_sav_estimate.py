#!/usr/bin/env python3
"""RCA of the savings estimate (dev/audit/rca/R10-RCA-SAV-ESTIMATE.md): the booked thermostat step.

WHY IT EXISTS. The month row books one step of the thermostat reference per
re-plan. On a valved install that step is decided by the tanks as measured, so
it reads far below the reference's own horizon, and the row publishes a loss the
plan's own figure contradicts. Every earlier savings harness measured either
step 0 on a house with no valve (`r10_sav_baseline.py`) or the horizon sum on a
house with one (`r10_buffer_store.py reference`). Run from the repository root,
at any tree:

    PYTHONPATH=tests/hastub:tests:custom_components \
        python3 dev/audit/harnesses/r10_rca_sav_estimate.py <arm> [args]

Arms:

  ledger BUNDLE   Ratios only, from a diagnostics export: each month's booked
                  thermostat kWh over its metered kWh, against the row's floor.
  attrib BUNDLE   The export's snapshots through `_compute_baseline_power`, with
                  the tanks measured, the wood tank cold, the buffer at the
                  curve, and both: step 0 over the horizon mean.
  blind           The R10-SAV-BASELINE transient metric (the spread of step 0
                  across room and slab starts) on the installs it never ran.
  census          The countermeasure. One solve per install x tank cell at a
                  steady day, booked through `get_current_action`: the booked
                  step over the reference's horizon mean must sit in BAND.
                  Exits 1 on any cell out of it, or if a cell did not run.

Null control: the `census` cells with no store (`single`, `unvalved`) stay in
band on a defective tree, so the check is not reading the install's size. The
mutation is the defect itself: this arm is red on v7.0.4 and on v7.1.1.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from datetime import datetime

import numpy as np

from heatpump_optimizer import ledger, mixing_valve
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)
from profiles import house, prices, solve_inputs, weather

T0 = datetime(2026, 1, 15, 12, 0)
STEPS = 96
DT = 0.25
#: A steady day (one outdoor temperature, no sun, one comfort target, one price)
#: leaves a thermostat nothing to vary, so its booked step and its horizon mean
#: differ only by what the measured tanks do to step 0. Wide, because the
#: reference's first hours may honestly differ; the defect reads 0.00.
BAND = (0.5, 1.5)
#: The month row's floor is production's own rule (``ledger.below_meter_floor``,
#: R10-SAV-METER-FLOOR). It has no ceiling: wood raises the ratio without limit
#: (triage P387).


def _valved(volume: float, **over) -> dict:
    return dict(
        two_zone=True, dhw=False, mixing_valve_mode="manual", mixing_valve_target=21.0,
        buffer_tank_volume=volume, **over,
    )


WOOD = dict(wood_furnace_enabled=True, wood_tank_top_entity="sensor.wood", wood_tank_volume=500.0)
#: name -> (house kwargs, buffer C, wood C).
CELLS = {
    "single": (dict(two_zone=False, dhw=False), 40.0, None),
    "unvalved": (dict(two_zone=True, dhw=False), 40.0, None),
    "valve-at-curve": (_valved(750.0), 26.0, None),
    "valve-charged": (_valved(750.0), 45.0, None),
    "wood-warm": (_valved(500.0, **WOOD), 30.0, 30.0),
    "wood-hot": (_valved(500.0, **WOOD), 45.0, 60.0),
}


def _optimizer(cfg: dict) -> tuple[HeatPumpOptimizer, ThermalParameters]:
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    return (
        HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
            horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=21.0 - 3.0,
            max_temp=23.0, comfort_temp_day=21.0, comfort_temp_night=21.0,
        )),
        params,
    )


def arm_census() -> int:
    bad, ran = [], 0
    flat = prices("flat", T0)
    for name, (kw, buf, wood) in CELLS.items():
        opt, _ = _optimizer(house(**kw))
        plan = opt.optimize(inputs=solve_inputs(
            initial_state=ThermalState(
                room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=0.0,
                upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
                buffer_tank_temperature=buf, wood_tank_temperature=wood,
            ),
            prices=flat, outdoor_temps=np.full(STEPS, 0.0), wind_speeds=np.full(STEPS, 2.0),
            precipitation=np.zeros(STEPS), solar_radiation=np.zeros(STEPS), start_time=T0,
        ))
        booked = float(opt.get_current_action(plan, T0)["baseline_kw"])
        mean = float(np.mean(plan.baseline_power_schedule))
        ratio = booked / mean if mean > 0.0 else float("nan")
        ran += 1
        sound = BAND[0] <= ratio <= BAND[1]
        print(f"RESULT census {name}: booked over horizon mean {ratio:.2f} "
              f"{'ok' if sound else 'OUT OF BAND'}")
        if not sound:
            bad.append(name)
    print(f"census: {ran} of {len(CELLS)} cells ran, {len(bad)} out of band: {' '.join(bad) or '-'}")
    return 1 if bad or ran != len(CELLS) else 0


def arm_blind() -> int:
    """#2411's metric: step 0 across start states. A constant zero reads sound."""
    starts = ((21.0, 22.0), (20.0, 21.0), (19.0, 20.0), (22.0, 23.5))
    out, wind, rain, sol = weather("winter_mild", T0)
    for name in ("unvalved", "valve-charged", "wood-hot"):
        kw, buf, wood = CELLS[name]
        opt, _ = _optimizer(house(**kw))
        firsts = []
        for room, slab in starts:
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=ThermalState(
                    room_temperature=room, slab_temperature=slab,
                    outdoor_temperature=float(out[0]), upper_floor_temperature=room,
                    lower_floor_temperature=room, dhw_temperature=52.0,
                    dhw_hours_since_legionella=20.0, buffer_tank_temperature=buf,
                    wood_tank_temperature=wood,
                ),
                prices=prices("flat", T0), outdoor_temps=out, wind_speeds=wind,
                precipitation=rain, solar_radiation=sol, start_time=T0,
            ))
            firsts.append(float(plan.baseline_power_schedule[0]))
        spread = max(firsts) - min(firsts)
        print(f"RESULT blind {name}: step 0 {[round(v, 3) for v in firsts]} "
              f"spread {spread:.3f} -> {'SOUND' if spread < 0.05 else 'DEFECT'} (the metric's verdict)")
    return 0


def _export(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["data"]


def arm_ledger(path: str) -> int:
    data = _export(path)
    stores = data["debug"]["stores"]
    ledger = next(v for k, v in stores.items() if k.endswith("_ledger"))
    for month, body in sorted(ledger["ledger"]["months"].items()):
        lines = body["lines"]
        if "savings_baseline" not in lines:
            continue
        booked, metered = lines["savings_baseline"]["kwh"], lines["savings_actual"]["kwh"]
        ratio = booked / metered
        verdict = "UNDER THE FLOOR" if ledger.below_meter_floor(booked, metered) else "not under the floor"
        print(f"RESULT ledger {month}: booked thermostat over metered {ratio:.2f} {verdict}")
    for snap in data["debug"]["payload_snapshots"]:
        rows = snap["data"].get("savings_months") or []
        print(f"RESULT ledger snapshot: plan's own saving {snap['data']['savings_percentage']:.1f} % "
              f"beside the open row's {rows[-1]['savings_pct']:.1f} %")
    return 0


def arm_attrib(path: str) -> int:
    data = _export(path)
    cfg = data["config"]
    params = ThermalParameters.from_config(cfg)
    model = ThermalModel(params)
    opt = HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=float(cfg["comfort_temp_day"]),
        min_temp=17.0, max_temp=23.0,
    ))
    rows = data["debug"]["cycle_rows"]
    for snap in data["debug"]["payload_snapshots"]:
        x = snap["data"]
        at = datetime.fromisoformat(snap["t"]).timestamp()
        row = min(rows, key=lambda r: abs(datetime.fromisoformat(r["t"]).timestamp() - at))
        out = float(row["outdoor_temp"])
        wind = float(x["predictive_info"].get("avg_future_wind_ms") or 2.0)
        state = ThermalState(
            room_temperature=row["indoor_temp"], slab_temperature=x.get("slab_temperature") or 22.0,
            outdoor_temperature=out,
            upper_floor_temperature=x.get("upper_floor_temperature") or row["indoor_temp"],
            lower_floor_temperature=x.get("lower_floor_temperature") or row["indoor_temp"],
            dhw_temperature=x.get("dhw_temperature") or 50.0, dhw_hours_since_legionella=20.0,
            buffer_tank_temperature=x["buffer_tank_temperature"],
            wood_tank_temperature=x["wood_tank_temperature"],
        )
        series = WeatherSeries(
            outdoor_temps=np.full(STEPS, out), wind_speeds=np.full(STEPS, wind),
            precipitation=np.zeros(STEPS), solar_radiation=np.zeros(STEPS),
            external_heat_kw=None, humidity=None,
        )
        targets = np.full(STEPS, float(cfg["comfort_temp_day"]))
        loss = model.effective_heat_loss_coefficient(params.upper_floor_heat_loss, wind, 0.0) + (
            model.effective_heat_loss_coefficient(params.lower_floor_heat_loss_learned, wind * 0.5, 0.0))
        curve = mixing_valve.flow_setpoint(
            target_temp=params.mixing_valve_target or params.comfort_ceiling, outdoor_temp=out,
            heat_loss_coefficient=loss,
            emitter_ua=params.max_electrical_power * params.cop_nominal_floored
            / params.emitter_design_delta_t_floored,
        )
        cells = (
            ("measured", {}),
            ("wood cold", {"wood_tank_temperature": 5.0}),
            ("buffer at curve", {"buffer_tank_temperature": curve}),
            ("both", {"wood_tank_temperature": 5.0, "buffer_tank_temperature": curve}),
        )
        parts = []
        for label, changes in cells:
            power, _ = opt._compute_baseline_power(series, dataclasses.replace(state, **changes), DT, targets)
            parts.append(f"{label} {float(power[0]) / max(float(np.mean(power)), 1e-9):.2f}")
        print("RESULT attrib step 0 over horizon mean: " + ", ".join(parts))
    return 0


def main(argv: list[str]) -> int:
    arm = argv[0] if argv else "census"
    if arm == "census":
        return arm_census()
    if arm == "blind":
        return arm_blind()
    if arm == "ledger":
        return arm_ledger(argv[1])
    if arm == "attrib":
        return arm_attrib(argv[1])
    print(f"unknown arm {arm}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
