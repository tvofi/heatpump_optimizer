"""R10-SETPOINT-POWER: the rounded-level flat band, census over synthetic installs.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_setpoint_power.py

Every cell is a synthetic 750 L buffered install behind a manual mixing valve
whose levels ship rounded (``clamp_planned_levels``), p_min 1.5 kW, p_max
5.5 kW: two-zone off/on x hot water off/on x heat-loss scale 0.6/1.0 x outdoor
mean -4/+2 degC x starting tank 25/34 degC = 32 cells, one sinusoidal price
day (1.3 +/- 0.9) and its flat mean. Each cell is solved twice per price
vector on the tree it runs in: as shipped, and with
``optimizer._relaxed_starts`` replaced by the identity (the control arm; on a
tree without the function both arms are the tree). Printed per price vector:
how many cells the shipped solve scores lower / higher by the plan's own
``objective_value`` than the control arm, how many publish the identical plan,
and the failure count. No private data: every input is written here.
"""
from __future__ import annotations

import itertools
from datetime import datetime, timezone

import numpy as np

from heatpump_optimizer import optimizer as opt_mod
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

STEPS = np.arange(96)
SPREAD = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)
FLAT = np.full(96, float(SPREAD.mean()))
CELLS = list(itertools.product(
    (False, True), (False, True), (0.6, 1.0), (-4.0, 2.0), (25.0, 34.0),
))


def solve(cell: tuple, prices: np.ndarray, relaxed: bool) -> tuple[np.ndarray, float]:
    two_zone, dhw, loss, out_mean, tank = cell
    params = ThermalParameters()
    params.mixing_valve_mode = "manual"
    params.buffer_tank_volume = 750.0
    params.min_electrical_power, params.max_electrical_power = 1.5, 5.5
    params.two_zone_enabled, params.dhw_enabled = two_zone, dhw
    params.house_heat_loss_scale = loss
    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(clamp_planned_levels=True))
    kept = getattr(opt_mod, "_relaxed_starts", None)
    if not relaxed and kept is not None:
        opt_mod._relaxed_starts = lambda _opt, *args: args[-2]
    try:
        result = opt.optimize(inputs=solve_inputs(
            initial_state=ThermalState(
                room_temperature=20.5, upper_floor_temperature=20.5,
                lower_floor_temperature=20.5, slab_temperature=21.0,
                outdoor_temperature=float(outdoor[0]),
                buffer_tank_temperature=tank, dhw_temperature=50.0,
            ),
            prices=prices, outdoor_temps=outdoor,
            start_time=datetime(2026, 1, 10, tzinfo=timezone.utc),
        ))
    finally:
        if kept is not None:
            opt_mod._relaxed_starts = kept
    return np.asarray(result.power_schedule, float), float(result.objective_value)


def main() -> int:
    failures = 0
    for tag, prices in (("spread", SPREAD), ("flat", FLAT)):
        lower = higher = same = 0
        for cell in CELLS:
            try:
                plan, value = solve(cell, prices, True)
                ctl_plan, ctl_value = solve(cell, prices, False)
            except Exception as err:  # counted, never dropped
                failures += 1
                print(f"  {tag} {cell} failed: {err}")
                continue
            lower += value < ctl_value - 1e-9
            higher += value > ctl_value + 1e-9
            same += bool(np.array_equal(plan, ctl_plan))
        print(f"{tag}: cells {len(CELLS)} objective lower {lower} higher {higher} "
              f"identical plan {same}")
    print(f"failures {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
