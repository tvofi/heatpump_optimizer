"""V2 (independent) harness for D1-s2-02.

Metric (one line): Euler sub-steps per model step returned by production
ThermalModel._stability_substeps(wind, 0, dt=0.25 h) for default single-zone
ThermalParameters, per forecast wind speed in {3, 60, 500, 1e6, 1e12, 1e20} m/s.
Count key: the production return value (contention-immune).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_wind_substeps.py [--clip]
Expected: 1 sub-step up to 500 m/s; linear in wind above (1e12 -> ~7.5e7 at dt 0.25 h);
  --clip (wind clipped to [0, 60] before the call): 1 everywhere.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

CLIP = "--clip" in sys.argv
m = ThermalModel(ThermalParameters())
DT = 0.25
for w in (3.0, 60.0, 500.0, 1e6, 1e12, 1e20):
    wc = float(np.clip(w, 0, 60)) if CLIP else w
    n = m._stability_substeps(wc, 0.0, DT)
    print(f"RESULT wind{w:g}_substeps={n} count")
print(f"RESULT thread_factor={(time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
