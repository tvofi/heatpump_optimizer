#!/usr/bin/env python3
# Metric: max |plan_mutant - plan_baseline| (kW) of DhwPlanner._plan_dhw_cheapest_first over the inputs below, and the count of differing inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_eae8cfee2ddbd16d.py
# EXPECTED RESULT differing_inputs=0 (equivalent: the line runs only after take > 1e-6 was added, so plan[j] > 0 there)
# EXPECTED RESULT edge_delta_kw=0.0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2285
#   `if 0.0 < plan[j] < min_run_power:`).
# Perturbation: mutant eae8cfee2ddbd16d (CMP_BOUND) `if 0.0 < plan[j] < min_run_power:` -> `if 0.0 <= plan[j] < min_run_power:`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: none expected; the mutant raises a step at 0 kW to min_run_power, and no input leaves plan[j] == 0 after a positive add.
# Null control: the baseline method on both arms (null_delta_kw).
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if 0.0 < plan[j] < min_run_power:'
NEW = 'if 0.0 <= plan[j] < min_run_power:'
MUT = mutant('_plan_dhw_cheapest_first', '                if 0.0 < plan[j] < min_run_power:', '                if 0.0 <= plan[j] < min_run_power:', 2285)

N = 12
rows = []
for derate in (0.0, 0.2, 0.9):
    pl, params = planner(cop_partload_derate=derate)
    for prices in (np.linspace(3.0, 0.5, N), np.zeros(N), np.where(np.arange(N) == 4, np.nan, 1.0)):
        req = np.full(N, 40.0); req[8] = 55.0; mx = np.full(N, 65.0); dr = np.zeros(N)
        c = ctx(pl, params, prices, min_run_power=1.5)
        b, m = call(DhwPlanner._plan_dhw_cheapest_first, pl, c, 45.0, req, dr, mx), call(MUT, pl, c, 45.0, req, dr, mx)
        rows.append(max_abs(b, m) if not differ(b, m, 0.0) else (max_abs(b, m) or float("inf")))
print(f"RESULT edge_inputs={len(rows)}")
print(f"RESULT edge_delta_kw={max(rows):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=160, derate_choices=(0.0, 0.2, 0.9))
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT null_delta_kw=0 kW")
print("RESULT inputs_tried=derate 0/0.2/0.9 x prices (falling, all-zero, one NaN) at min_run_power 1.5; 160 random")
footer()
