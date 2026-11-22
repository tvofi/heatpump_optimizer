#!/usr/bin/env python3
# Metric: max |plan_mutant - plan_baseline| (kW) of DhwPlanner._plan_dhw_min_cost when the largest refill premium is exactly 1e-9.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_6e1174561ae9297c.py
# EXPECTED RESULT tie_premium=1e-09 (prices 0 and 1e-9: refill - price == 1e-9 exactly)
# EXPECTED RESULT tie_delta_kw=0.0 kW (the mutant keeps a 1e-9 premium the LP's tolerance does not resolve)
# EXPECTED RESULT differing_inputs=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1546
#   `if not np.any(premium > 1e-9):`).
# Perturbation: mutant 6e1174561ae9297c (CMP_BOUND) `if not np.any(premium > 1e-9):` -> `if not np.any(premium >= 1e-9):`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: none found.
# Null control: the premium-0 case (flat prices): 0 by construction.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if not np.any(premium > 1e-9):'
NEW = 'if not np.any(premium >= 1e-9):'
MUT = mutant('_plan_dhw_min_cost', '            if not np.any(premium > 1e-9):', '            if not np.any(premium >= 1e-9):', 1546)

pl, params = planner()
N = 6
req = np.array([40, 40, 40, 40, 55, 40.0]); dr = np.zeros(N); mx = np.full(N, 65.0)
rows = []
for prices, sd in ((np.array([0.0, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9]), np.array([5.0, 0, 0, 0, 0, 0])),
                   (np.array([1e-9, 1e-9, 0.0, 1e-9, 1e-9, 1e-9]), np.array([0.0, 0, 5, 0, 0, 0])),
                   (np.array([0.0, 1e-9, 0.0, 1e-9, 0.0, 1e-9]), np.array([5.0, 0, 5, 0, 5, 0]))):
    assert float(np.max(np.where(sd > 0, 1e-9 - prices, 0))) == 1e-9
    c = ctx(pl, params, prices)
    a = (pl, c, 45.0, req, dr, mx, sd, 3.0)
    rows.append(max_abs(call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a)))
print("RESULT tie_premium=1e-09")
print(f"RESULT tie_inputs={len(rows)}")
print(f"RESULT tie_delta_kw={max(rows):.3g} kW")

n, d, w = sweep_min_cost(MUT, trials=80)
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT inputs_tried=3 tie layouts (full step at price 0 beside spare steps at 1e-9); 80 random")
footer()
