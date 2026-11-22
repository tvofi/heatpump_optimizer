#!/usr/bin/env python3
# Metric: numpy RuntimeWarnings DhwPlanner._plan_dhw_min_cost emits on one call, and max |plan delta| (kW).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_c1d6f40c74ee74ad.py
# EXPECTED RESULT warnings_baseline=0 at tank decay 0.0
# EXPECTED RESULT warnings_mutant=1 at tank decay 0.0 ('divide by zero encountered in power': 0.0**negative lag)
# EXPECTED RESULT plan_delta_kw=0.0 kW (np.where masks the inf entries; the plan is identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1510
#   `influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0)`).
# Perturbation: mutant c1d6f40c74ee74ad (CLAMP_DROP) `influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0)` -> `influence = np.where(lag >= 0, np.power(decay, (lag)) / c_dhw, 0.0)`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: warning count up from 0 to 1 when the tank decay is 0.0; plan unchanged.
# Null control: decay 0.988 (dhw_cooling_rate 0.3, a 200 l tank): warnings 0 in both arms.
# Count key: the count of warnings the call raises (warnings.catch_warnings, always), and the returned plan.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0)'
NEW = 'influence = np.where(lag >= 0, np.power(decay, (lag)) / c_dhw, 0.0)'
MUT = mutant('_plan_dhw_min_cost', '        influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0)', '        influence = np.where(lag >= 0, np.power(decay, (lag)) / c_dhw, 0.0)', 1510)

import warnings
N = 24
def one(fn, cool, cap):
    pl, p = planner(dhw_cooling_rate=cool)
    c = ctx(pl, p, np.linspace(0.5, 3, N), cap=cap)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plan = call(fn, pl, c, 45.0, np.full(N, 50.0), np.zeros(N), np.full(N, 65.0))
    return plan, len(w), c.tank_decay[0]
for label, cool, cap in (("null", 0.3, 0.232), ("decay0", 3.0, 0.01)):
    b, wb, dec = one(DhwPlanner._plan_dhw_min_cost, cool, cap)
    m, wm, _ = one(MUT, cool, cap)
    print(f"RESULT {label}_decay={dec:.6g}")
    print(f"RESULT {label}_warnings_baseline={wb}")
    print(f"RESULT {label}_warnings_mutant={wm}")
    print(f"RESULT {label}_plan_delta_kw={max_abs(b, m):.3g} kW")

n, d, w = sweep_min_cost(MUT, trials=80)
print(f"RESULT sweep_inputs={n}")
print(f"RESULT differing_inputs={d}")
print(f"RESULT sweep_max_delta_kw={w:.3g} kW")
print("RESULT reach=decay 0 needs the tank's standby loss over one step to reach its whole stored heat (here dhw_cooling_rate 3.0 on a 0.01 kWh/C store); a realistic 200 l tank decays 0.988 per hour")
print("RESULT inputs_tried=decay 0.988 (null) and 0.0, 24 steps; 80 random scenarios at decay 0.988 for plan deltas")
footer()
