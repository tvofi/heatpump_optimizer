#!/usr/bin/env python3
"""VD3L V2 D3-s1-69: whole-module mutant of dhw_planner.py:1559 (np.max -> np.min in the shortfall
price), swapped in as optimizer.DhwPlanner, through the PUBLIC HeatPumpOptimizer.optimize on the
suite's house() (DHW on) for every tests/profiles.py price profile, plus a x1000 price scale and an
undersized tank-start (cold start) so the shortfall slack is live. Metric: |delta| of the solved DHW
schedule's energy (kWh) between arms, per cell; null = flat profile."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from unittest import mock
from datetime import datetime
import numpy as np
from mutload import load
b, m = load("dhw_planner", 1559, "shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)",
            "shortfall_price = 1000.0 * (float(np.min(np.abs(prices))) + 1.0)")
opt_mod = load("optimizer"); tm = load("thermal_model")
sys.path.insert(0, os.path.join(os.environ["VROOT"], "tests"))
from profiles import prices, weather, house, DT
def solve_inputs(*, initial_state, start_time, **fc):
    return opt_mod.SolveInputs(state=initial_state, start_time=start_time, forecast=opt_mod.ForecastSeries(**fc), limits=opt_mod.SolveLimits())
start = datetime(2026, 1, 15)
cells = []
for prof in ("winter_typical", "winter_extreme", "summer_typical", "summer_negative", "shoulder", "winter_narrow", "winter_moderate", "flat"):
    for scale in (1.0, 1000.0):
        for dhw0 in (50.0, 15.0):
            out = []
            for arm in (b, m):
                p = tm.ThermalParameters.from_config(house())
                model = tm.ThermalModel(p)
                opt = opt_mod.HeatPumpOptimizer(model, opt_mod.OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                                                target_temp=21.0, min_temp=17.0, max_temp=23.0))
                pr = prices(prof, start) * scale
                ot, wi, ra, so = weather("winter_cold", start)
                st = tm.ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                                     buffer_tank_temperature=40.0, dhw_temperature=dhw0)
                with mock.patch.object(opt_mod, "DhwPlanner", arm.DhwPlanner):
                    res = opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
                                                           precipitation=ra, solar_radiation=so, start_time=start))
                out.append(float(np.sum(res.dhw_power_schedule) * DT))
            cells.append((prof, scale, dhw0, round(out[0], 4), round(out[1] - out[0], 4)))
            print(f"CELL {cells[-1]}", flush=True)
moved = [c for c in cells if abs(c[4]) > 1e-3]
print(f"RESULT 69_cells={len(cells)} moved={len(moved)} max_abs_delta_kwh={max(abs(c[4]) for c in cells):.4f}")
print(f"RESULT 69_null_flat_moved={sum(1 for c in moved if c[0]=='flat')}")
print(f"RESULT 69_moved_cells={moved}")
