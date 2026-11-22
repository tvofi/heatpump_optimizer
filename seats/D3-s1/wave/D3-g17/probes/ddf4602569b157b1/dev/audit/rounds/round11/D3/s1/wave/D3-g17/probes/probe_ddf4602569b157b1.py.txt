#!/usr/bin/env python3
# Metric: DHW power (kW) DhwPlanner._plan_dhw_min_cost plans at a step whose space demand is exactly p_total_max - 1e-6.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_ddf4602569b157b1.py
# EXPECTED RESULT plan_baseline=[1e-06,0,0,1.31032673,0,0] (step 0 is full: DHW there pays the refill premium 2)
# EXPECTED RESULT plan_mutant=[1.37938921,0,0,0,0,0] (step 0 counts as spare: premium 0, DHW bought there)
# EXPECTED RESULT step0_delta_kw=1.379 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1529
#   `spare = demand < p_total_max - 1e-6`).
# Perturbation: mutant ddf4602569b157b1 (CMP_BOUND) `spare = demand < p_total_max - 1e-6` -> `spare = demand <= p_total_max - 1e-6`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: DHW moves to the tied step (step 0 up, step 3 down).
# Null control: space demand p_total_max - 2e-6 at step 0 (strictly spare in both arms): null_delta_kw.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'spare = demand < p_total_max - 1e-6'
NEW = 'spare = demand <= p_total_max - 1e-6'
MUT = mutant('_plan_dhw_min_cost', '            spare = demand < p_total_max - 1e-6', '            spare = demand <= p_total_max - 1e-6', 1529)

pl, params = planner()
N = 6; pm = 3.0
prices = np.array([1.0, 3.0, 3.0, 3.0, 3.0, 3.0])
req = np.array([40, 40, 40, 40, 55, 40.0]); dr = np.zeros(N); mx = np.full(N, 65.0)
c = ctx(pl, params, prices)
sd = np.array([pm - 1e-6, 0, 0, 0, 0, 0])
b, m = DhwPlanner._plan_dhw_min_cost(pl, c, 45.0, req, dr, mx, sd, pm), MUT(pl, c, 45.0, req, dr, mx, sd, pm)
print(f"RESULT plan_baseline={fmt(b)}")
print(f"RESULT plan_mutant={fmt(m)}")
print(f"RESULT step0_delta_kw={abs(m[0] - b[0]):.4g} kW")
print(f"RESULT cost_baseline={float(np.dot(b, prices)):.6g} cost_mutant={float(np.dot(m, prices)):.6g}")
sd2 = sd.copy(); sd2[0] = pm - 2e-6
print(f"RESULT null_delta_kw={max_abs(DhwPlanner._plan_dhw_min_cost(pl, c, 45.0, req, dr, mx, sd2, pm), MUT(pl, c, 45.0, req, dr, mx, sd2, pm)):.3g} kW")

n, d, w = sweep_min_cost(MUT, trials=80)
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT inputs_tried=step-0 demand exactly p_total_max-1e-6 (tie); p_total_max-2e-6 (null); 80 random (no tie: 0 differ)")
footer()
