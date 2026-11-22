#!/usr/bin/env python3
# Metric: planned power (kW) at the step whose initial plan sits exactly at p_dhw_max - 1e-6, and the plan's price-weighted sum.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_5b123e9e5b76ebc3.py
# EXPECTED RESULT step7_baseline=2.999999 kW (the step is not a candidate)
# EXPECTED RESULT step7_mutant=3 kW (the tie makes it a candidate; its 1e-6 kW of spare is topped up)
# EXPECTED RESULT delta_kw=1e-06 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2227
#   `plan[j] < p_dhw_max - 1e-6`).
# Perturbation: mutant 5b123e9e5b76ebc3 (CMP_BOUND) `plan[j] < p_dhw_max - 1e-6` -> `plan[j] <= p_dhw_max - 1e-6`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: the tied step's power up by its 1e-6 kW of spare.
# Null control: the same plan with the step at p_dhw_max - 2e-6 (strictly below the bound in both arms): null_delta_kw.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'plan[j] < p_dhw_max - 1e-6'
NEW = 'plan[j] <= p_dhw_max - 1e-6'
MUT = mutant('_plan_dhw_cheapest_first', '                    plan[j] < p_dhw_max - 1e-6', '                    plan[j] <= p_dhw_max - 1e-6', 2227)

pl, params = planner()
N = 12
prices = np.full(N, 3.0); prices[7] = 0.1; req = np.full(N, 20.0); req[10] = 60.0; mx = np.full(N, 70.0); dr = np.zeros(N)
c = ctx(pl, params, prices)
ip = np.zeros(N); ip[7] = 3.0 - 1e-6
b, m = DhwPlanner._plan_dhw_cheapest_first(pl, c, 45.0, req, dr, mx, initial_plan=ip), MUT(pl, c, 45.0, req, dr, mx, initial_plan=ip)
print(f"RESULT plan_baseline={fmt(b)}")
print(f"RESULT plan_mutant={fmt(m)}")
print(f"RESULT step7_baseline={b[7]:.9g} kW")
print(f"RESULT step7_mutant={m[7]:.9g} kW")
print(f"RESULT delta_kw={max_abs(b, m):.3g} kW")
print(f"RESULT cost_baseline={float(np.dot(b, prices)):.9g}")
print(f"RESULT cost_mutant={float(np.dot(m, prices)):.9g}")
ip2 = ip.copy(); ip2[7] = 3.0 - 2e-6
print(f"RESULT null_delta_kw={max_abs(DhwPlanner._plan_dhw_cheapest_first(pl, c, 45.0, req, dr, mx, initial_plan=ip2), MUT(pl, c, 45.0, req, dr, mx, initial_plan=ip2)):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=120)
print(f"RESULT sweep_inputs={n} sweep_differing_inputs={d}")
print("RESULT inputs_tried=initial plan step 7 at p_dhw_max-1e-6 (tie), at p_dhw_max-2e-6 (null); 120 random (no tie: 0 differ)")
footer()
