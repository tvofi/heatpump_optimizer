#!/usr/bin/env python3
# Metric: max |plan_mutant - plan_baseline| (kW) of DhwPlanner._plan_dhw_min_cost when every refill premium is 0, and the count of differing inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_539e5aeaccf156f3.py
# EXPECTED RESULT differing_inputs=0 (equivalent at the output: with premium 0 the displacement variables cost nothing, so the kept headroom rows never bind)
# EXPECTED RESULT edge_delta_kw=0.0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1546
#   `if not np.any(premium > 1e-9):`).
# Perturbation: mutant 539e5aeaccf156f3 (GUARD_OFF) `if not np.any(premium > 1e-9):` -> `if False:`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: none found; the mutant only keeps n_steps zero-cost columns and n_steps rows in the LP.
# Null control: a scenario with a positive premium (the guard does not fire in either arm): 0 by construction.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if not np.any(premium > 1e-9):'
NEW = 'if False:'
MUT = mutant('_plan_dhw_min_cost', '            if not np.any(premium > 1e-9):', '            if False:', 1546)

pl, params = planner()
N = 6
req = np.array([40, 40, 40, 40, 55, 40.0]); dr = np.zeros(N); mx = np.full(N, 65.0)
rows = []
for prices in (np.full(N, 2.0), np.array([3.0, 2.5, 2.0, 1.5, 1.0, 0.5]), np.zeros(N)):
    for sd in (np.full(N, 5.0), np.zeros(N), np.array([5.0, 0, 5, 0, 5, 0])):
        c = ctx(pl, params, prices)
        a = (pl, c, 45.0, req, dr, mx, sd, 3.0)
        rows.append(max_abs(call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a)))
print(f"RESULT edge_inputs={len(rows)}")
print(f"RESULT edge_delta_kw={max(rows):.3g} kW")

n, d, w = sweep_min_cost(MUT, trials=120)
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT inputs_tried=3 price shapes (flat, falling, zero) x 3 demand shapes (all full, all spare, alternating); 120 random")
footer()
