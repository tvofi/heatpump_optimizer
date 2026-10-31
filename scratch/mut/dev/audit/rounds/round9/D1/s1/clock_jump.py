"""D1-s1 staleness harness (D1.M3): a timestamp persisted while the host clock ran
AHEAD, re-read after the clock is corrected (a backward jump), pins the stale-
timeout seams of the learners in D1-s1's cells.

Metric (one line): per seam, days of corrected wall-clock (1-day ticks, aware
clock, DST-crossing start) until the seam acts again, for a clock that ran ahead
by A days; capped at 400 (= never within the run).
  cusum_release   : drift.Cusum.release_if_starved(now, 72 h) releases a tripped latch
  snapshot_due    : snapshots.SnapshotRing.due(now) is True again
  curve_step      : curve_learning.CurveLearner.record_day steps the bias
Count key: the day index at which the production call first acts.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/clock_jump.py [--ahead 0|1|30|365]
  --ahead 0 (null control): cusum 4, snapshot 8, curve 2 (the designed timeouts, DST-shifted)
  --ahead A: each = null + A (30 -> 33, 37, 31; 365 -> 369, 373, 366; exact)
Perturbation: --clamp treats a stored stamp later than `now` as `now` (one-line
min() in each loader) -> every seam returns to the --ahead 0 value.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
from heatpump_optimizer.curve_learning import CurveLearner  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing  # noqa: E402

args = sys.argv[1:]
AHEAD = int(args[args.index("--ahead") + 1]) if "--ahead" in args else 30
CLAMP = "--clamp" in args
TZ = ZoneInfo("Europe/Stockholm")
NOW0 = datetime(2026, 3, 27, 12, 0, tzinfo=TZ)  # the corrected clock; DST starts 2026-03-29
STAMP = NOW0 + timedelta(days=AHEAD)             # written while the clock ran ahead
CAP = 400


def clampstr(s):
    return min(datetime.fromisoformat(s), NOW0).isoformat() if CLAMP else s


def first(pred):
    for d in range(CAP):
        if pred(NOW0 + timedelta(days=d)):
            return d
    return CAP


c = Cusum(threshold=5.0, drift=0.1)
c.load({"stat": 6.0, "tripped": True, "last_fed": clampstr(STAMP.isoformat())})
cusum = first(lambda now: c.release_if_starved(now, 72.0))

ring = SnapshotRing.from_dict({"snapshots": [{"taken_at": clampstr(STAMP.isoformat()), "healthy": True}]})
snap = first(lambda now: ring.due(now))

cl = CurveLearner.from_dict({"bias": -1.0, "comfortable_days": 0, "last_day": "",
                             "last_step_at": clampstr(STAMP.isoformat())})
before = cl.bias
curve = first(lambda now: (cl.record_day(now, 5.0), cl.bias != before)[1])

print(f"# ahead={AHEAD} clamp={CLAMP}")
print(f"RESULT cusum_release_day={cusum} count")
print(f"RESULT snapshot_due_day={snap} count")
print(f"RESULT curve_step_day={curve} count")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
