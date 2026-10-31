#!/usr/bin/env python3
"""R10-UX-HEALTH part 3 (plan-energy live probe, item b): is the whole-house
heat loss inert in two-zone mode?

The carry asks the options flow to hide or label
``house_heat_loss_coefficient`` on a two-zone entry, on the probe's finding
that the model ignores it there. That holds only if NO two-zone reader
remains. This sweeps the coefficient across its range (``SWEEP``) on the
probe's owner-like two-zone config through two production paths:

* the solve -- ``OptimizationConfig.from_mapping`` ->
  ``ThermalParameters.from_config`` -> ``HeatPumpOptimizer.optimize``;
* system identification's step sizer -- ``HousePlant.of_params`` ->
  ``SystemIdentification._size_step_power``, the call the coordinator's
  sysid tick makes, which reads ``heat_loss_coefficient`` with no two-zone
  branch.

The null control for both is the same sweep in single-zone mode, where the
coefficient must move each output (a harness that reads zero there is blind).
The field is inert in two-zone mode only when every two_zone_* line is 0;
until then the UI must keep offering it.

  two_zone_max_dkw       largest |planned power| difference, kW (two zones)
  two_zone_max_dcost     largest |predicted cost| difference (two zones)
  single_zone_max_dkw    the solve's null control, must be > 0
  two_zone_sysid_steps   the sysid step sizes across the sweep, kW (``None``:
                         no step fits); one distinct value means inert
  single_zone_sysid_steps  the sizer's null control

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r10_two_zone_hhl_inert.py
"""
from __future__ import annotations

from datetime import datetime

import numpy as np

from heatpump_optimizer import const as C
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.sysid import HousePlant, SystemIdentification
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

START = datetime(2026, 10, 30, 18, 45)
N = 96
HOURS = np.array([(START.hour + START.minute / 60 + i * 0.25) % 24 for i in range(N)])
PRICE = np.interp(HOURS, [0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 23, 24],
                  [0.45, 0.35, 0.40, 1.30, 1.50, 0.90, 0.85, 1.40, 1.80, 1.10, 0.60, 0.45]) + 1.15
OUT = 6.0 + 2.0 * np.cos((HOURS - 14) / 24 * 2 * np.pi)
CFG = {
    "target_temperature": 18.0, "comfort_temp_day": 19.5, "comfort_temp_night": 18.5,
    "min_temperature": 18.0, "max_temperature": 21.0, "comfort_weight": 2.0,
    "upper_floor_area_ratio": 0.5, "inter_zone_heat_transfer": 0.5,
    "lower_floor_heat_loss": 0.2, "upper_floor_heat_loss": 0.13,
    "lower_floor_thermal_mass": 1.0, "upper_floor_thermal_mass": 1.26,
    "slab_thermal_mass": 1.0, "slab_heat_transfer": 1.5,
}
SWEEP = (0.1, 0.4, 1.0)


def _solve(mode: str, hhl: float) -> tuple[np.ndarray, float]:
    cfg = {**CFG, C.CONF_TWO_ZONE_MODE: mode, C.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hhl}
    params = ThermalParameters.from_config(cfg)
    state = ThermalState(room_temperature=20.0, outdoor_temperature=float(OUT[0]),
                         upper_floor_temperature=20.0, lower_floor_temperature=19.0,
                         slab_temperature=20.0)
    result = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig.from_mapping(cfg)).optimize(
        inputs=solve_inputs(initial_state=state, prices=PRICE, outdoor_temps=OUT, start_time=START))
    return np.asarray(result.power_schedule, float), float(result.predicted_cost)


def _sysid_steps(mode: str) -> list[float | None]:
    steps = []
    for hhl in SWEEP:
        params = ThermalParameters.from_config(
            {**CFG, C.CONF_TWO_ZONE_MODE: mode, C.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hhl})
        plant = HousePlant.of_params(params)
        kw = SystemIdentification()._size_step_power(
            5.0, 3.0, 20.0, 5.0, plant.ua, plant.capacity, plant.gains, plant.slab_mass, plant.slab_transfer)
        steps.append(None if kw is None else round(kw, 3))
    return steps


def _spread(mode: str) -> tuple[float, float]:
    runs = [_solve(mode, hhl) for hhl in SWEEP]
    dkw = max(float(np.max(np.abs(p - runs[0][0]))) for p, _ in runs)
    dcost = max(abs(c - runs[0][1]) for _, c in runs)
    return dkw, dcost


if __name__ == "__main__":
    two_dkw, two_dcost = _spread(C.TWO_ZONE_MODE_ON)
    one_dkw, _ = _spread(C.TWO_ZONE_MODE_OFF)
    print(f"RESULT two_zone_max_dkw={two_dkw:.6f}")
    print(f"RESULT two_zone_max_dcost={two_dcost:.6f}")
    print(f"RESULT single_zone_max_dkw={one_dkw:.6f}")
    print(f"RESULT two_zone_sysid_steps={','.join(map(str, _sysid_steps(C.TWO_ZONE_MODE_ON)))}")
    print(f"RESULT single_zone_sysid_steps={','.join(map(str, _sysid_steps(C.TWO_ZONE_MODE_OFF)))}")
