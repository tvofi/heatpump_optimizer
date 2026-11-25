#!/usr/bin/env python3
# Metric: max planned DHW power (kW) DhwPlanner._plan_dhw_cheapest_first returns, against ctx.p_dhw_max.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_61862d35b6b2885d.py
# EXPECTED RESULT plan_max_baseline=3.0 kW (min_run_power 3.5 > p_dhw_max 3.0: the clip holds the rating)
# EXPECTED RESULT plan_max_mutant=3.5 kW (the min-run raise at line 2285 is returned above the rating)
# EXPECTED RESULT sweep_differing_inputs=0 (min_run_power <= p_dhw_max: nothing to clip)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2307
#   `return np.clip(plan, 0.0, p_dhw_max)`).
# Perturbation: mutant 61862d35b6b2885d (CLAMP_DROP) `return np.clip(plan, 0.0, p_dhw_max)` -> `return (plan)`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: plan max up, above p_dhw_max, only when min_run_power > p_dhw_max.
# Null control: min_run_power 0.1 < p_dhw_max: plan_max_null_delta=0.
# Count key: the returned plan array's maximum (kW), the value the method delivers.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'return np.clip(plan, 0.0, p_dhw_max)'
NEW = 'return (plan)'
MUT = mutant('_plan_dhw_cheapest_first', '        return np.clip(plan, 0.0, p_dhw_max)', '        return (plan)', 2307)

pl, params = planner()
N = 12
prices = np.linspace(3.0, 0.5, N); req = np.full(N, 40.0); req[8] = 55.0; mx = np.full(N, 65.0); dr = np.zeros(N)
c = ctx(pl, params, prices, min_run_power=3.5, p_dhw_max=3.0)
b, m = DhwPlanner._plan_dhw_cheapest_first(pl, c, 45.0, req, dr, mx), MUT(pl, c, 45.0, req, dr, mx)
print(f"RESULT plan_baseline={fmt(b)}")
print(f"RESULT plan_mutant={fmt(m)}")
print(f"RESULT plan_max_baseline={float(np.max(b)):.6g} kW")
print(f"RESULT plan_max_mutant={float(np.max(m)):.6g} kW")
c0 = ctx(pl, params, prices, min_run_power=0.1, p_dhw_max=3.0)
print(f"RESULT plan_max_null_delta={max_abs(DhwPlanner._plan_dhw_cheapest_first(pl, c0, 45.0, req, dr, mx), MUT(pl, c0, 45.0, req, dr, mx)):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=160, derate_choices=(0.0, 0.2, 0.9))
print(f"RESULT sweep_inputs={n}")
print(f"RESULT sweep_differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT reach=DhwPlanner.optimize sets min_run_power = min(p_dhw_run, ...) (dhw_planner.py:1141), so min_run_power > p_dhw_max is not produced by optimize; the method itself is the seam")
print("RESULT inputs_tried=min_run_power 3.5/p_dhw_max 3.0; null 0.1/3.0; 160 random (derate 0/0.2/0.9, initial plans) for a float overshoot")
footer()
