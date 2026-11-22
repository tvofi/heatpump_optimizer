#!/usr/bin/env python3
# Metric: what DhwPlanner._plan_dhw_min_cost returns (plan, None) when linprog reports success=False.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_2074f3eefe8521aa.py
# EXPECTED RESULT status1_baseline=None (iteration-limit result carrying an x: greedy fallback)
# EXPECTED RESULT status1_mutant=plan (the unconverged x is published as the seed)
# EXPECTED RESULT status2_baseline=None status2_mutant=None (infeasible: x is None, the next guard returns best)
# EXPECTED RESULT real_differing=0 (unmocked solves succeed)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1608
#   `if not result.success:`).
# Perturbation: mutant 2074f3eefe8521aa (GUARD_OFF) `if not result.success:` -> `if False:`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: None becomes a plan built from an unsuccessful solve, when the failure carries an x.
# Null control: unmocked linprog on the same inputs (success=True): real_differing=0.
# Count key: the type of the returned value and the plan array.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'if not result.success:'
NEW = 'if False:'
MUT = mutant('_plan_dhw_min_cost', '            if not result.success:', '            if False:', 1608)

from unittest import mock
from scipy.optimize import OptimizeResult
pl, params = planner()
N = 16
prices = np.full(N, 3.0); prices[0] = 0.9; prices[10] = 0.1
req = np.full(N, 40.0); req[11] = 55.0
real = dhw_planner.linprog
def failing(status, keep_x):
    def f(*a, **k):
        r = OptimizeResult(dict(real(*a, **k)))
        r.success, r.status, r.message = False, status, f"probe: status {status}"
        if not keep_x:
            r.x = None
        return r
    return f
def kind(v):
    return type(v).__name__ if isinstance(v, BaseException) else ("None" if v is None else "plan")
c = ctx(pl, params, prices)
a = (pl, c, 45.0, req, np.zeros(N), np.full(N, 65.0))
for status, keep in ((1, True), (2, False)):
    with mock.patch.object(dhw_planner, "linprog", failing(status, keep)):
        b, m = call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a)
    print(f"RESULT status{status}_baseline={kind(b)} status{status}_mutant={kind(m)}")
    if kind(m) == "plan":
        print(f"RESULT status{status}_mutant_plan={fmt(m)}")
print(f"RESULT real_differing={int(differ(call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a), 1e-12))}")
print("RESULT reach=the LP carries a priced shortfall slack and finite bounds, so it is feasible and bounded on every input tried; a real success=False needs a solver limit or numerical failure, which this probe stubs (mock.patch.object on dhw_planner.linprog)")
print("RESULT inputs_tried=stubbed status 1 with x; stubbed status 2 without x; unmocked (null)")
footer()
