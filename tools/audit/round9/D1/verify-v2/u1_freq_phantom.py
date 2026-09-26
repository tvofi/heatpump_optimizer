"""V2 (independent) harness for D1-s3-06.

Metric (one line): per phantom stored bucket (decile key, kW/Hz ratio, count 50)
added to a healthy map loaded by production FrequencyMap.from_dict, the number
of truthful folds (plant 0.04 kW/Hz, each fold at the clipped
FrequencyMap.recommend(3 kW) answer, production observe) until the plant
delivers >= 50 % of 3 kW, capped at 10000; cells = keys {-1, 0, 5} x ratios
{0.2, 1.0, 10, 1e6, 1e308}; plus count of cells still under-delivering at 96 folds.
Count key: recommend() return value clipped to [20, 100] Hz as
coordinator._command_frequency clips it; plant kW = 0.04 * Hz.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_freq_phantom.py
Expected: key -1 cells with predicted >= 3 kW never recover (10000 cap); key 0/5 recover in
  ~log(ratio/0.04)/log(1/0.9) folds; stuck_at_96 >= 6 of 15 (+-0, deterministic).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from heatpump_optimizer.freq_control import FrequencyMap

LO, HI, K, TGT = 20.0, 100.0, 0.04, 3.0


def healthy():
    m = FrequencyMap()
    for hz in np.linspace(22, 98, 200):
        m.observe(float(hz), K * float(hz), LO, HI)
    return m.as_dict()


def folds_to_recover(payload, cap=10000):
    m = FrequencyMap.from_dict(json.loads(json.dumps(payload)))
    for n in range(cap + 1):
        rec = m.recommend(TGT, LO, HI)
        hz = HI if rec is None else float(np.clip(rec, LO, HI))
        if K * hz >= 0.5 * TGT:
            return n
        m.observe(hz, K * hz, LO, HI)
    return cap


base = healthy()
print(f"# healthy recommend(3 kW) = {FrequencyMap.from_dict(base).recommend(TGT, LO, HI)} Hz, folds={folds_to_recover(base)}")
stuck96 = 0
for key in (-1, 0, 5):
    for ratio in (0.2, 1.0, 10.0, 1e6, 1e308):
        p = dict(base); p[str(key)] = [ratio, 50]
        n = folds_to_recover(p)
        stuck96 += int(n > 96)
        print(f"RESULT key{key}_ratio{ratio:g}_folds_to_recover={n} folds")
print(f"RESULT stuck_at_96={stuck96} cells_of_15")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
