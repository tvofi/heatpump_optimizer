"""Leads seat (round 10), owner D0-s2: does the shipped winter single-zone DHW plan breach its OWN comfort floor?

Metric: degree-steps of OptimizationResult.room_temp_trajectory[1:] below the per-step lower bound
  production itself builds (OptimizationConfig.get_temp_bounds, which is min_temp in the comfort
  window and min_temp - 0.5 outside it), summed over the 24 h plan; beside it the same sum against a
  constant config.min_temp (the yardstick D0-s3's terminal.py used).
Count key: the trajectory production returns, against the bounds production's own config returns.
Command (from the export root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/leads/tail_floor_own_bounds.py [--perturb]
Expected at 17f1c55fad1b (winter_typical/winter_cold, single zone, DHW on, start 2026-01-15 00:00):
  RESULT breach_vs_constant_floor=0.232 degree-steps (+-0.01), RESULT breach_vs_own_floor=0.000.
Perturbation (--perturb): OptimizationConfig.get_temp_bounds patched in memory to return min_temp all
  day (no night setback); breach_vs_constant_floor must fall 0.232 -> 0.000 (measured: the plan then ends
  at 17.000): the plan follows the floor production builds, so the 0.232 is the night setback, not a
  solver shortfall. Null arm: DHW off, where both yardsticks read 0 in both arms.
Machine: macOS arm64 (leads seat). A count of degree-steps, contention-immune.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import sys
import time
from datetime import datetime, timedelta
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import prices, weather, house, solve_inputs, DT  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
if "--perturb" in sys.argv:
    O.OptimizationConfig.get_temp_bounds = lambda self, hour, when=None: (self.min_temp, self.max_temp)
start = datetime(2026, 1, 15)
for dhw in (1, 0):
    p = ThermalParameters.from_config(house(two_zone=False)); p.dhw_enabled = bool(dhw)
    opt = O.HeatPumpOptimizer(ThermalModel(p), O.OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices("winter_typical", start); ot, wi, ra, so = weather("winter_cold", start)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      buffer_tank_temperature=40.0, dhw_temperature=48.0)
    r = opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot, wind_speeds=wi,
                                         precipitation=ra, solar_radiation=so, start_time=start))
    room = np.asarray(r.room_temp_trajectory, float)[1:]
    whens = [start + timedelta(hours=(i + 1) * DT) for i in range(room.size)]
    own = np.array([opt.config.get_temp_bounds(w.hour + w.minute / 60.0, when=w)[0] for w in whens])
    b_const = float(np.maximum(0.0, 17.0 - room).sum()); b_own = float(np.maximum(0.0, own - room).sum())
    tag = "" if dhw else "_dhw_off_null"
    print(f"cell dhw={dhw} end_room={room[-1]:.3f} tail_floor={own[-1]:.2f} min_room={room.min():.3f}")
    print(f"RESULT breach_vs_constant_floor{tag}={b_const:.3f} degree-steps")
    print(f"RESULT breach_vs_own_floor{tag}={b_own:.3f} degree-steps")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=na")
