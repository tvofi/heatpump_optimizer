#!/usr/bin/env python3
"""D2.M1 physical bounds over every golden plan scenario, solved live.

Metric (one line): count of (scenario, store) pairs whose live-solved
trajectory crosses its store's physical bound by more than 1e-9 K:
buffer <= max(buffer_max_temp, T0) behind a valve; wood <= max(95, T0);
DHW <= max(dhw_hard_max_temp, T0) and >= min(inlet, DHW ambient);
every building store >= min(min outdoor, its own T0) (no store is cooled
below the coldest thing it touches: all inputs are non-negative heat).

Count key: the trajectories HeatPumpOptimizer.optimize returns (the
published plan), compared with bounds read from the scenario's own
ThermalParameters -- never the fixture JSON.

Hooks: optimizer:HeatPumpOptimizer.optimize via tests/golden.py:capture
(which drives thermal_model:ThermalModel.simulate_trajectory_with_dhw).

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D2/s1/m1_golden.py
  ... --perturb=cap  (buffer_max_temp and dhw_hard_max_temp read 10 K lower
                      by the bound check only; the count must go UP, which
                      proves the check can fire on this data)
Expected at baseline: 0 violations.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B4 (cloud container, linux).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import golden  # noqa: E402
from heatpump_optimizer import mixing_valve  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")
SHIFT = 10.0 if PERTURB == "cap" else 0.0
TOL = 1e-9

_t0p, _t0t = time.process_time(), time.thread_time()

viol = []
checked = 0
for name, spec in golden.SCENARIOS.items():
    built = golden.make(**spec)
    p = built["optimizer"].model.params
    st = built["state"]
    pay = golden.capture(name, spec)
    out_min = float(np.min(pay["outdoor_temps"]))

    def chk(key, lo=None, hi=None):
        global checked
        s = pay.get(key)
        if not s:
            return
        checked += 1
        a = np.asarray(s, dtype=float)
        if hi is not None and np.max(a) > hi + TOL:
            viol.append((name, key, "max", float(np.max(a)), hi))
        if lo is not None and np.min(a) < lo - TOL:
            viol.append((name, key, "min", float(np.min(a)), lo))

    if mixing_valve.is_throttling(p.mixing_valve_mode):
        chk("buffer_temp_trajectory",
            hi=max(p.buffer_max_temp - SHIFT, st.buffer_tank_temperature))
    if st.wood_tank_temperature is not None:
        chk("wood_temp_trajectory", hi=max(tm.WOOD_TANK_MAX_TEMP, st.wood_tank_temperature))
    if p.dhw_enabled:
        chk("dhw_temp_trajectory",
            lo=min(p.dhw_inlet_reference, tm.DHW_AMBIENT_TEMP, st.dhw_temperature),
            hi=max(p.dhw_hard_max_temp - SHIFT, st.dhw_temperature))
    for key, t0 in (("room_temp_trajectory", st.room_temperature),
                    ("slab_temp_trajectory", st.slab_temperature),
                    ("upper_temp_trajectory", st.upper_floor_temperature),
                    ("lower_temp_trajectory", st.lower_floor_temperature)):
        chk(key, lo=min(out_min, t0))

print(f"RESULT golden_scenarios={len(golden.SCENARIOS)} count")
print(f"RESULT golden_series_checked={checked} count")
print(f"RESULT golden_bound_violations={len(viol)} count")
for v in viol[:20]:
    print(f"# {v}")
pc, tc = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        sw = next(int(ln.split()[1]) for ln in fh if ln.startswith("pswpin"))
except (OSError, StopIteration):
    sw = -1
print(f"RESULT swapins={sw}")
