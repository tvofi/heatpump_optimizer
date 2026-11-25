#!/usr/bin/env python3
# Metric: what DhwPlanner._plan_dhw_min_cost returns (plan, None, or the exception type) at a non-positive step length.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_247372989ae65baa.py
# EXPECTED RESULT dt0_baseline=a plan (window 6e6 steps, the whole horizon)
# EXPECTED RESULT dt0_mutant=ZeroDivisionError
# EXPECTED RESULT dtneg_baseline=a plan; dtneg_mutant=None (window collapses to 1)
# EXPECTED RESULT positive_dt_differing=0 (dt 1, 0.25, 1e-7: identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1535
#   `window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6))))`).
# Perturbation: mutant 247372989ae65baa (CLAMP_DROP) `window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6))))` -> `window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / (dt))))`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: a plan becomes an exception (dt 0) or None (dt < 0); no change for any dt > 0 tried.
# Null control: dt 1.0, 0.25 and 1e-7: positive_dt_differing=0.
# Count key: the type of the returned value (plan/None/exception) and the plan array.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6))))'
NEW = 'window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / (dt))))'
MUT = mutant('_plan_dhw_min_cost', '            window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6))))', '            window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / (dt))))', 1535)

import warnings
pl, params = planner()
N = 16
prices = np.full(N, 3.0); prices[0] = 0.9; prices[14] = 4.0; prices[10] = 0.1
sd = np.full(N, 5.0); sd[0] = 0.0; sd[14] = 0.0
req = np.full(N, 40.0); req[11] = 55.0
out = {}
for dt in (1.0, 0.25, 1e-7, 0.0, -1.0):
    c = ctx(pl, params, prices, dt=dt)
    a = (pl, c, 45.0, req, np.zeros(N), np.full(N, 65.0), sd, 3.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out[dt] = (call(DhwPlanner._plan_dhw_min_cost, *a), call(MUT, *a))
def kind(v):
    return type(v).__name__ if isinstance(v, BaseException) else ("None" if v is None else "plan")
print(f"RESULT positive_dt_differing={sum(differ(*out[d], 1e-12) for d in (1.0, 0.25, 1e-7))}")
print(f"RESULT dt0_baseline={kind(out[0.0][0])} dt0_mutant={kind(out[0.0][1])}")
print(f"RESULT dtneg_baseline={kind(out[-1.0][0])} dtneg_mutant={kind(out[-1.0][1])}")
print("RESULT reach=ctx.dt is the configured step length in hours (positive); no input with dt > 0 separates the arms")
print("RESULT inputs_tried=dt 1.0, 0.25, 1e-7 (window >= horizon in both), 0.0, -1.0")
footer()
