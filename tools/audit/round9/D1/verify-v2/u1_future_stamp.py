"""V2 (independent) harness for D1-s1-04.

Metric (one line): per seam, the extra delay in hours (hourly ticks, UTC aware
clock) before the production call first acts when its persisted stamp lies A
days in the future of the corrected clock, relative to the same stamp at now
(A=0), for A in {1,7,30}: Cusum.release_if_starved (6 h starve rule),
SnapshotRing.due (7 d), CurveLearner._step_down (non-zero step).
Count key: the production return value / state change (tripped cleared, due True,
bias moved), stamp loaded via Cusum.load / SnapshotRing.from_dict / CurveLearner.from_dict.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_future_stamp.py [--clamp]
Expected: extra_h = 24*A (+-1 h) for each seam; --clamp (future stamp clamped to now at call, in memory): 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import logging; logging.disable(logging.CRITICAL)
from heatpump_optimizer import drift, snapshots, curve_learning
from heatpump_optimizer.const import VENT_CUSUM_STARVE_HOURS

CLAMP = "--clamp" in sys.argv
NOW = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
H = 24 * 400


def stamp(a):
    s = NOW + timedelta(days=a)
    return (min(s, NOW) if CLAMP else s).isoformat()


def first_act(a):
    out = {}
    c = drift.Cusum(threshold=5.0, drift=0.1)
    c.load({"stat": 6.0, "tripped": True, "last_fed": stamp(a)})
    for h in range(H):
        if c.release_if_starved(NOW + timedelta(hours=h), VENT_CUSUM_STARVE_HOURS):
            out["cusum"] = h; break
    r = snapshots.SnapshotRing.from_dict({"snapshots": [{"taken_at": stamp(a), "healthy": True}]})
    for h in range(H):
        if r.due(NOW + timedelta(hours=h)):
            out["snapshot"] = h; break
    cl = curve_learning.CurveLearner.from_dict({"bias": -1.0, "last_step_at": stamp(a)})
    b0 = cl.bias
    for h in range(H):
        cl._step_down(NOW + timedelta(hours=h))
        if cl.bias != b0:
            out["curve"] = h; break
    return out


base = first_act(0)
for a in (1, 7, 30):
    r = first_act(a)
    for k in ("cusum", "snapshot", "curve"):
        print(f"RESULT A{a}_{k}_extra_h={r.get(k, H) - base.get(k, H)} hours (base {base.get(k)} h)")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
