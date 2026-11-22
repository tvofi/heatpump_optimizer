#!/usr/bin/env python3
# Metric: max |plan_mutant - plan_baseline| (kW) of DhwPlanner._plan_dhw_cheapest_first over the inputs below, and the count of inputs where the plans differ.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_0aa6eaace756da92.py
# EXPECTED RESULT differing_inputs=0 (equivalent: at plan[j] == min_run_power the mutant assigns the value plan[j] already holds)
# EXPECTED RESULT tie_delta_kw=0.0 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2285
#   `if 0.0 < plan[j] < min_run_power:`).
# Perturbation: mutant 0aa6eaace756da92 (CMP_BOUND) `if 0.0 < plan[j] < min_run_power:` -> `if 0.0 < plan[j] <= min_run_power:`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: none expected; any differing input would refute equivalence.
# Null control: the same call with the baseline method on both arms (null_delta_kw).
# Count key: the returned plan array (kW per step), the value the method delivers.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if 0.0 < plan[j] < min_run_power:'
NEW = 'if 0.0 < plan[j] <= min_run_power:'
MUT = mutant('_plan_dhw_cheapest_first', '                if 0.0 < plan[j] < min_run_power:', '                if 0.0 < plan[j] <= min_run_power:', 2285)

pl, params = planner()
N = 12
prices = np.linspace(3.0, 0.5, N); req = np.full(N, 40.0); req[8] = 55.0; mx = np.full(N, 65.0); dr = np.zeros(N)
base = DhwPlanner._plan_dhw_cheapest_first(pl, ctx(pl, params, prices), 45.0, req, dr, mx)
# The tie: set min_run_power to exactly the power the baseline lands on, so plan[j] == min_run_power after the add.
tie = float(np.max(base))
c = ctx(pl, params, prices, min_run_power=tie)
b, m = call(DhwPlanner._plan_dhw_cheapest_first, pl, c, 45.0, req, dr, mx), call(MUT, pl, c, 45.0, req, dr, mx)
print(f"RESULT tie_min_run_power={tie:.12g} kW")
print(f"RESULT tie_plan_baseline={fmt(b)}")
print(f"RESULT tie_plan_mutant={fmt(m)}")
print(f"RESULT tie_delta_kw={max_abs(b, m):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=160, mrp_choices=(0.1, 0.5, 1.5, 3.0))
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print(f"RESULT null_delta_kw={max_abs(b, call(DhwPlanner._plan_dhw_cheapest_first, pl, c, 45.0, req, dr, mx)):.3g} kW")
print("RESULT inputs_tried=tie(min_run_power==landed power);160 random (derate 0/0.2, min_run_power 0.1/0.5/1.5/3.0, initial plans with 0/0.5/3.0, integer-price ties)")
footer()
