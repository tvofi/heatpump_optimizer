#!/usr/bin/env python
"""D2 harness -- the COP, heat-loss, buffer-cooling and zone-split learners' clamps.

Metric: after calling the coordinator's apply-methods with values far outside the
documented bands (1e-6 and 1e6), the value read back from the live ThermalParameters,
compared with the band edges COP_SCALE_MIN/MAX, HOUSE_HEAT_LOSS_SCALE_MIN/MAX,
buffer_cooling_rate_bounds(volume) and LOWER_FLOOR_LOSS_RATIO_MIN/MAX; and whether a
NaN input is refused or clamped.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/learner_clamps.py
Expected (c398fc84): clamp_violations = 0; nan_leaks reports how many learners let NaN
  through to the model (np.clip(nan) is nan).
Perturbation: config buffer_tank_volume 200 -> 750 moves buffer_cooling_low/high down
  (the bounds follow volume^(-1/3)).
Instrumented: coordinator:HeatPumpOptimizerCoordinator._apply_cop_scale,
  _apply_house_heat_loss_scale, _apply_buffer_cooling_rate, _apply_lower_floor_loss_ratio.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import resource
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

from harness import FakeEntry, FakeHass
from heatpump_optimizer.const import (
    COP_SCALE_MAX, COP_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX, HOUSE_HEAT_LOSS_SCALE_MIN,
    LOWER_FLOOR_LOSS_RATIO_MAX, LOWER_FLOOR_LOSS_RATIO_MIN, buffer_cooling_rate_bounds,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

cfg = {"tibber_token": "x", "weather_entity": "weather.home", "buffer_tank_volume": 200.0,
       "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0}
coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
p = coord._thermal_params
low_b, high_b = buffer_cooling_rate_bounds(p.buffer_tank_volume)
print(f"CELL buffer cooling bounds for {p.buffer_tank_volume:.0f} L: [{low_b:.3f}, {high_b:.3f}] degC/h")
print(f"RESULT buffer_cooling_low={low_b:.4f} degC_per_h")
print(f"RESULT buffer_cooling_high={high_b:.4f} degC_per_h")

viol = 0
nan_leaks = 0
learners = (
    ("cop_scale", coord._apply_cop_scale, lambda: p.cop_scale, COP_SCALE_MIN, COP_SCALE_MAX),
    ("house_heat_loss_scale", coord._apply_house_heat_loss_scale, lambda: p.house_heat_loss_scale,
     HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX),
    ("buffer_cooling_rate", coord._apply_buffer_cooling_rate, lambda: p.buffer_cooling_rate, low_b, high_b),
    ("lower_floor_loss_ratio", coord._apply_lower_floor_loss_ratio, lambda: p.lower_floor_loss_ratio,
     LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX),
)
for name, apply, read, lo, hi in learners:
    apply(1e-6)
    got_lo = read()
    apply(1e6)
    got_hi = read()
    apply(0.5 * (lo + hi))
    got_mid = read()
    ok = abs(got_lo - lo) < 1e-12 and abs(got_hi - hi) < 1e-12 and abs(got_mid - 0.5 * (lo + hi)) < 1e-12
    viol += int(not ok)
    try:
        apply(float("nan"))
        leaked = not np.isfinite(read())
    except (ValueError, TypeError):
        leaked = False
    nan_leaks += int(leaked)
    apply(1.0)
    print(f"CELL {name}: band [{lo:.3f}, {hi:.3f}] read back low={got_lo:.4f} high={got_hi:.4f} mid={got_mid:.4f} "
          f"nan_leaks={int(leaked)}")
print(f"RESULT clamp_learners={len(learners)} count")
print(f"RESULT clamp_violations={viol} count")
print(f"RESULT clamp_nan_leaks={nan_leaks} count")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
