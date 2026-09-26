"""V3 verify of D1-s1-52 (P11): execute the three named production seams against the REAL
homeassistant.util.dt.now() (genuine Home Assistant 2026.2.3, no tests/hastub), and separately
against the stub's dt_util.now() at its default (no HASTUB_TZ), to get an executed divergent
count rather than a hand-built "aware" stand-in.

Metric: of 6 cells (3 seams x {aware, naive} stored stamp), count whose TypeError-raise verdict
differs between the provider's own dt_util.now() and the other provider's.
Seams: snapshots.SnapshotRing.due, curve_learning.CurveLearner._step_down,
comfort_learning.ComfortLearner._decay (identical to the finder's D1-s1-01 seams).

Command (real half, no tests/hastub on the path):
    PYTHONPATH=custom_components /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s1-52_realha_naive_clock.py --real
Command (stub half):
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s1-52_realha_naive_clock.py --stub
Expected: real half -- dt_util.now() is aware (tzinfo is not None); aware-stored cells raise
0/3, naive-stored cells raise 3/3. Stub half (default, no HASTUB_TZ) -- dt_util.now() is naive;
aware-stored raises 3/3, naive-stored raises 0/3 (the finder's stub_naive_clock.py numbers).
Diffing the two RESULT blocks gives divergent=6 of 6.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Real half on Home Assistant 2026.2.3.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import resource

_T0 = (time.process_time(), time.thread_time())

MODE = "real" if "--real" in sys.argv else ("stub" if "--stub" in sys.argv else None)
if MODE is None:
    print("usage: --real (venvha, no hastub) | --stub (PYTHONPATH=tests/hastub)")
    sys.exit(2)

if MODE == "real":
    import typing
    typing.ByteString = bytes  # CPython 3.14 compat shim, per SUBSEAT.md
else:
    sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from datetime import datetime, timezone  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing  # noqa: E402
from heatpump_optimizer.curve_learning import CurveLearner  # noqa: E402
from heatpump_optimizer.comfort_learning import ComfortLearner  # noqa: E402

if MODE == "stub":
    dt_util.freeze(None)  # explicit default: no HASTUB_TZ, not frozen aware

AWARE_STORED = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
NAIVE_STORED = datetime(2026, 1, 1, 12, 0)


def seams(stored):
    ring = SnapshotRing(snapshots=[{"taken_at": stored.isoformat()}])
    curve = CurveLearner(bias=-1.0, _last_step_at=stored.isoformat())
    comfort = ComfortLearner(last_update=stored)
    return {"ring.due": ring.due, "curve._step_down": curve._step_down, "comfort._decay": comfort._decay}


def verdicts(now):
    out = {}
    for tag, stored in (("aware", AWARE_STORED), ("naive", NAIVE_STORED)):
        for name, fn in seams(stored).items():
            try:
                fn(now)
                out[(name, tag)] = 0
            except TypeError:
                out[(name, tag)] = 1
    return out


now = dt_util.now()
print(f"RESULT {MODE}_now_aware={int(now.tzinfo is not None)}")
v = verdicts(now)
for k, val in v.items():
    print(f"RESULT {MODE}_cell_{k[0]}_{k[1]}_raises={val}")
print(f"RESULT {MODE}_aware_stored_raises={sum(v[(n, 'aware')] for n in ('ring.due', 'curve._step_down', 'comfort._decay'))} of 3")
print(f"RESULT {MODE}_naive_stored_raises={sum(v[(n, 'naive')] for n in ('ring.due', 'curve._step_down', 'comfort._decay'))} of 3")

cpu = time.process_time() - _T0[0]
thr = time.thread_time() - _T0[1]
print(f"RESULT thread_factor={(cpu / thr) if thr else 1.0:.3f}")
try:
    load1 = os.getloadavg()[0]
except OSError:
    load1 = -1.0
print(f"RESULT load1={load1}")
ru = resource.getrusage(resource.RUSAGE_SELF)
print(f"RESULT swapins={ru.ru_minflt}")
