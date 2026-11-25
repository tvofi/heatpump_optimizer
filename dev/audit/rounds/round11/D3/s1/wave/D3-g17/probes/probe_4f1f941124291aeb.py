#!/usr/bin/env python3
# Metric: planned power (kW) at the step whose simulated tank temperature equals its ceiling minus 0.1 C exactly.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_4f1f941124291aeb.py
# EXPECTED RESULT step3_baseline=0 kW (the step is not a candidate at the tie)
# EXPECTED RESULT step3_mutant=0.1 kW (a candidate: min_run_power 0.1 is planned there)
# EXPECTED RESULT delta_kw=0.1 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_cheapest_first (dhw_planner.py:2228
#   `and temps[j + 1] < ceiling[j] - 0.1`).
# Perturbation: mutant 4f1f941124291aeb (CMP_BOUND) `and temps[j + 1] < ceiling[j] - 0.1` -> `and temps[j + 1] <= ceiling[j] - 0.1`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: the tied step's power up from 0, the later steps' down.
# Null control: the same inputs with the step's ceiling one ulp higher (strictly above the tie in both arms): null_delta_kw.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'and temps[j + 1] < ceiling[j] - 0.1'
NEW = 'and temps[j + 1] <= ceiling[j] - 0.1'
MUT = mutant('_plan_dhw_cheapest_first', '                    and temps[j + 1] < ceiling[j] - 0.1', '                    and temps[j + 1] <= ceiling[j] - 0.1', 2228)

pl, params = planner()
N = 12
prices = np.full(N, 3.0); prices[3] = 0.1
req = np.full(N, 40.0); req[9] = 55.0; dr = np.zeros(N); dr[8] = 6.0
c = ctx(pl, params, prices)
temps0 = pl._ctx_temps(c, 62.0, dr, np.zeros(N))
j = 3; t = float(temps0[j + 1]); v = t + 1.1
def g(x):  # the ceiling the method derives for step j while the floor at step 9 binds: max(max_temp - 1, 55) - 0.1
    return max(x - 1.0, 55.0) - 0.1
for _ in range(5000):
    if g(v) == t:
        break
    v = np.nextafter(v, -np.inf) if g(v) > t else np.nextafter(v, np.inf)
assert g(v) == t, "no exact tie found"
mx = np.full(N, 70.0); mx[j] = v
b, m = DhwPlanner._plan_dhw_cheapest_first(pl, c, 62.0, req, dr, mx), MUT(pl, c, 62.0, req, dr, mx)
print(f"RESULT tie_temp={t!r} C max_temp_step3={v!r} C")
print(f"RESULT plan_baseline={fmt(b)}")
print(f"RESULT plan_mutant={fmt(m)}")
print(f"RESULT step3_baseline={b[3]:.9g} kW")
print(f"RESULT step3_mutant={m[3]:.9g} kW")
print(f"RESULT delta_kw={max_abs(b, m):.3g} kW")
mx2 = mx.copy(); mx2[j] = np.nextafter(np.nextafter(v, np.inf), np.inf)
print(f"RESULT null_delta_kw={max_abs(DhwPlanner._plan_dhw_cheapest_first(pl, c, 62.0, req, dr, mx2), MUT(pl, c, 62.0, req, dr, mx2)):.3g} kW")
n, d, w = sweep_cheapest_first(MUT, trials=120)
print(f"RESULT sweep_inputs={n} sweep_differing_inputs={d}")
print("RESULT inputs_tried=exact tie temps[4]==ceiling[3]-0.1 (max_temp searched by nextafter); ceiling 2 ulp up (null); 120 random (0 differ)")
footer()
