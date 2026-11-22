#!/usr/bin/env python3
# Metric: what DhwPlanner._plan_dhw_min_cost returns (plan, None, or the exception type) when linprog raises.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b7a6f145165338bf.py
# EXPECTED RESULT nan_price_linprog_raised=ValueError (a NaN price reaches linprog's input check)
# EXPECTED RESULT nan_price_baseline=None (the caller falls back to the greedy planner)
# EXPECTED RESULT nan_price_mutant=UnboundLocalError (falls through to `result.success` with no result)
# EXPECTED RESULT finite_differing=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1606
#   `return best`).
# Perturbation: mutant b7a6f145165338bf (RETURN_DEL) `return best` -> `pass`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: None becomes an UnboundLocalError on the first-pass solver exception.
# Null control: the same horizon with every price finite: finite_differing=0 (linprog does not raise; the line is not reached).
# Count key: the type of the returned value (plan/None/exception).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'return best'
NEW = 'pass'
MUT = mutant('_plan_dhw_min_cost', '                return best', '                pass', 1606)

pl, params = planner()
N = 16
prices = np.full(N, 3.0); prices[0] = 0.9; prices[10] = 0.1
req = np.full(N, 40.0); req[11] = 55.0
pn = prices.copy(); pn[3] = float("nan")
raised = []
real = dhw_planner.linprog
def spy(*a, **k):
    try:
        return real(*a, **k)
    except Exception as err:
        raised.append(type(err).__name__)
        raise
from unittest import mock
def kind(v):
    return type(v).__name__ if isinstance(v, BaseException) else ("None" if v is None else "plan")
with mock.patch.object(dhw_planner, "linprog", spy):
    c = ctx(pl, params, pn)
    a = (pl, c, 45.0, req, np.zeros(N), np.full(N, 65.0))
    b, m = call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a)
print(f"RESULT nan_price_linprog_raised={','.join(sorted(set(raised)))}")
print(f"RESULT nan_price_baseline={kind(b)}")
print(f"RESULT nan_price_mutant={kind(m)}")
c = ctx(pl, params, prices)
a = (pl, c, 45.0, req, np.zeros(N), np.full(N, 65.0))
print(f"RESULT finite_differing={int(differ(call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a), 1e-12))}")
print("RESULT reach=the line IS reachable by a direct call: one NaN price makes linprog raise ValueError on its first pass; whether DhwPlanner.optimize can hand this method a NaN price is not established here (no closure script's traced baseline executes line 1606)")
print("RESULT inputs_tried=one NaN price at step 3; all-finite prices (null)")
footer()
