#!/usr/bin/env python3
# Metric: max |plan_mutant - plan_baseline| (kW) of DhwPlanner._plan_dhw_cheapest_first, and the count of differing inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_fd9b39c806b43b56.py
# EXPECTED RESULT differing_inputs=0 (equivalent: `added` is 0.0 or a take > 1e-6, never exactly 1e-9)
# EXPECTED RESULT tiny_gap_delta_kw=0.0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2303
#   `if added <= 1e-9:`).
# Perturbation: mutant fd9b39c806b43b56 (CMP_BOUND) `if added <= 1e-9:` -> `if added < 1e-9:`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: none expected; only added == 1e-9 exactly separates, and the take <= 1e-6 skip keeps every non-zero added above 1e-6.
# Null control: the baseline method on both arms (null_delta_kw).
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if added <= 1e-9:'
NEW = 'if added < 1e-9:'
MUT = mutant('_plan_dhw_cheapest_first', '            if added <= 1e-9:', '            if added < 1e-9:', 2303)

pl, params = planner()
N = 12
rows = []
for it in (54.99, 54.999999, 54.9999999999, 55.0):  # shortfalls down to the take threshold
    prices = np.linspace(3.0, 0.5, N); req = np.full(N, 40.0); req[1] = 55.0; mx = np.full(N, 65.0); dr = np.zeros(N)
    c = ctx(pl, params, prices)
    b, m = call(DhwPlanner._plan_dhw_cheapest_first, pl, c, it, req, dr, mx), call(MUT, pl, c, it, req, dr, mx)
    rows.append(max_abs(b, m))
print(f"RESULT tiny_gap_delta_kw={max(rows):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=160)
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT null_delta_kw=0 kW")
print("RESULT inputs_tried=initial temp 54.99/54.999999/54.9999999999/55.0 against a 55 C floor (shortfall at the take threshold); 160 random")
footer()
