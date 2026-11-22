#!/usr/bin/env python3
# Metric: DHW plan (kW per step) and its price-weighted cost DhwPlanner._plan_dhw_min_cost returns on a 16-step horizon whose refill window (6 h) is shorter than the horizon.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1074e70396100d8.py
# EXPECTED RESULT plan_baseline=[1.75073672,0,...,0] (step 10's full-capacity premium uses the 6 h window's refill price 4.0: DHW bought at step 0)
# EXPECTED RESULT plan_mutant=[0,...,0,1.47660443 at step 10,0,...] (the window reaches back to step 0's 0.9 refill: premium 0.8, DHW bought at step 10)
# EXPECTED RESULT cost_baseline=1.5757 cost_mutant=0.14766
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1538
#   `lo = max(0, j - window)`).
# Perturbation: mutant b1074e70396100d8 (CLAMP_DROP) `lo = max(0, j - window)` -> `lo = (0)`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: DHW moves from step 0 to step 10; the premium the LP charges at step 10 falls from 3.9 to 0.8.
# Null control: a horizon no longer than the window (8 steps of 1 h, window 6: lo = max(0, j-6) only differs for j > 6, here no spare step precedes it): null_delta_kw; and flat prices.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'lo = max(0, j - window)'
NEW = 'lo = (0)'
MUT = mutant('_plan_dhw_min_cost', '                lo = max(0, j - window)', '                lo = (0)', 1538)

pl, params = planner()
N = 16
prices = np.full(N, 3.0); prices[0] = 0.9; prices[14] = 4.0; prices[10] = 0.1
sd = np.full(N, 5.0); sd[0] = 0.0; sd[14] = 0.0
req = np.full(N, 40.0); req[11] = 55.0
c = ctx(pl, params, prices)
a = (pl, c, 45.0, req, np.zeros(N), np.full(N, 65.0), sd, 3.0)
b, m = DhwPlanner._plan_dhw_min_cost(*a), MUT(*a)
print(f"RESULT plan_baseline={fmt(b)}")
print(f"RESULT plan_mutant={fmt(m)}")
print(f"RESULT cost_baseline={float(np.dot(b, prices)):.5g}")
print(f"RESULT cost_mutant={float(np.dot(m, prices)):.5g}")
print(f"RESULT delta_kw={max_abs(b, m):.4g} kW")
cf = ctx(pl, params, np.full(N, 2.0))
af = (pl, cf, 45.0, req, np.zeros(N), np.full(N, 65.0), sd, 3.0)
print(f"RESULT null_flat_delta_kw={max_abs(DhwPlanner._plan_dhw_min_cost(*af), MUT(*af)):.3g} kW")

n, d, w = sweep_min_cost(MUT, trials=120, dts=(1.0,))
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT inputs_tried=16 steps dt 1 h: spare cheap step 0, full steps 1-13 and 15, step 10 cheapest, spare step 14 at 4.0; flat prices (null); 120 random at dt 1")
footer()
