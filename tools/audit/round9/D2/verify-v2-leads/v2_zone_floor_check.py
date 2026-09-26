"""Verifier V2 (independent) check on D2-s2-81.

Metric (own): same floor_deg_steps = sum(max(0, min_temp - T)) definition as the finder, but on an
independently chosen, smaller grid (2 price profiles the finder's own worst cells came from,
DHW on only, winter_cold) plus a direct code-level check that _COMFORT_FLOOR_L1 is multiplied by
0.5 * weight in the two-zone branch but by weight (no halving) in the single-zone branch of
optimizer.py:_comfort_terms (grep, not read-and-trust: printed from the live module source).

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
  tools/audit/round9/D2/verify-v2-leads/v2_zone_floor_check.py [--perturb]
Instrumented symbol: heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize via _comfort_terms
  and the module constant _COMFORT_FLOOR_L1.
Perturbation (--perturb): optimizer._COMFORT_FLOOR_L1 2.0 -> 4.0 in memory (independent re-take of
  the finder's own perturbation, same direction check).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    optmod._COMFORT_FLOOR_L1 = 4.0

src = inspect.getsource(optmod.HeatPumpOptimizer._comfort_terms)
two_zone_scaled = "0.5 * weight * (" in src
single_zone_scaled = src.count("weight * (") - src.count("0.5 * weight * (")
print(f"RESULT source_two_zone_half_weight={int(two_zone_scaled)} bool")
print(f"RESULT source_single_zone_unhalved_blocks={single_zone_scaled} count")


def cell(two_zone, pp):
    b = golden.make(two_zone=two_zone, dhw=True, price_profile=pp, weather_profile="winter_cold")
    opt = b["optimizer"]
    res = opt.optimize(b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"], b["solar"], golden.START)
    floor = float(opt.config.min_temp)
    if two_zone:
        u = np.asarray(res.upper_temp_trajectory[1:])
        lo = np.asarray(res.lower_temp_trajectory[1:])
        return float(np.maximum(0, floor - u).sum() + np.maximum(0, floor - lo).sum())
    rm = np.asarray(res.room_temp_trajectory[1:])
    return float(np.maximum(0, floor - rm).sum())


t0, th0 = time.process_time(), time.thread_time()
PRICES = ["winter_typical", "winter_narrow"]
two_sum = one_sum = 0.0
for pp in PRICES:
    tv = cell(True, pp)
    ov = cell(False, pp)
    two_sum += tv
    one_sum += ov
    print(f"CELL {pp:16s} two_zone_deg_steps={tv:.4f} single_zone_deg_steps={ov:.4f}")

print(f"RESULT two_zone_deg_steps_sum={two_sum:.4f} degree-steps")
print(f"RESULT single_zone_deg_steps_sum={one_sum:.4f} degree-steps (null arm)")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
