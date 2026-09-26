"""V2 (independent) harness for D1-s1-01.

Metric (one line): per learner seam, of 21 consumer calls (one per day, aware
Europe/Stockholm clock) on an object built by the production from_dict from a
payload whose timestamp leaf is tz-naive, the count that raise; plus, as the
reach arm, the count of tz-naive timestamps the production writers emit when
driven by an aware clock and round-tripped through as_dict/from_dict/json.
Count key: exceptions raised by the production consumer; tzinfo of the string
the production writer produced.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_naive_ts.py [--fix]
Expected: naive arm snapshot=21 curve>=19 comfort=21 cusum(control)=0; aware arm all 0;
  writer_naive_stamps=0 (+-0, deterministic). --fix (naive->UTC at parse, in memory): all 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, sys, time
from datetime import datetime, timedelta, timezone
from unittest import mock
from zoneinfo import ZoneInfo
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import logging; logging.disable(logging.CRITICAL)
from heatpump_optimizer import snapshots, curve_learning, comfort_learning, drift  # noqa

TZ = ZoneInfo("Europe/Stockholm")
START = datetime(2026, 3, 20, 12, 0, tzinfo=TZ)  # spans the DST change
FIX = "--fix" in sys.argv


class _Fixed(datetime):
    @classmethod
    def fromisoformat(cls, s):
        v = datetime.fromisoformat(s)
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)


def stamp(dt, naive):
    return dt.replace(tzinfo=None).isoformat() if naive else dt.isoformat()


def arm(naive):
    past = START - timedelta(days=9)
    out = {}
    ring = snapshots.SnapshotRing.from_dict({"snapshots": [{"taken_at": stamp(past, naive), "healthy": True,
                                            "alarmed_at_capture": False, "accuracy": {}, "learners": {}}]})
    r = 0
    for d in range(21):
        try:
            ring.due(START + timedelta(days=d))
        except TypeError:
            r += 1
    out["snapshot_due"] = r
    cl = curve_learning.CurveLearner.from_dict({"bias": -1.0, "last_step_at": stamp(past, naive)})
    r = 0
    for d in range(21):
        try:
            cl.record_day(START + timedelta(days=d), 5.0)
        except TypeError:
            r += 1
    out["curve_record_day"] = r
    co = comfort_learning.ComfortLearner.from_dict({"configured_weight": 1.0, "learned_weight": 1.0,
                                                    "evidence": 1.0, "last_update": stamp(past, naive)}, 1.0)
    r = 0
    for d in range(21):
        try:
            co._decay(START + timedelta(days=d))
        except TypeError:
            r += 1
    out["comfort_decay"] = r
    cu = drift.Cusum(threshold=5.0, drift=0.1)
    cu.load({"stat": 1.0, "tripped": True, "last_fed": stamp(past, naive)})
    r = 0
    for d in range(21):
        try:
            cu.release_if_starved(START + timedelta(days=d), 72.0)
        except TypeError:
            r += 1
    out["cusum_control"] = r
    return out


def writers():
    """Production writers under an aware clock: count naive stamps emitted."""
    naive = 0
    ring = snapshots.SnapshotRing()
    cl = curve_learning.CurveLearner()
    cl.bias = -1.0
    co = comfort_learning.ComfortLearner(configured_weight=1.0, learned_weight=1.0)
    for d in range(30):
        now = START + timedelta(days=d)
        if ring.due(now):
            ring.take(now, {}, {}, True)
        cl.record_day(now, 5.0)
        co._decay(now)
    ring = snapshots.SnapshotRing.from_dict(json.loads(json.dumps(ring.as_dict())))
    cl = curve_learning.CurveLearner.from_dict(json.loads(json.dumps(cl.as_dict())))
    co = comfort_learning.ComfortLearner.from_dict(json.loads(json.dumps(co.as_dict())), 1.0)
    stamps = [s["taken_at"] for s in ring.snapshots] + [cl.as_dict()["last_step_at"], co.as_dict()["last_update"]]
    for s in stamps:
        if s and datetime.fromisoformat(s).tzinfo is None:
            naive += 1
    return naive, len([s for s in stamps if s])


def main():
    ctx = []
    if FIX:
        ctx = [mock.patch.object(m, "datetime", _Fixed) for m in (snapshots, curve_learning, comfort_learning)]
    for c in ctx:
        c.start()
    n = arm(True)
    a = arm(False)
    for c in ctx:
        c.stop()
    for k, v in n.items():
        print(f"RESULT naive_{k}_raises={v} count_of_21")
    for k, v in a.items():
        print(f"RESULT aware_{k}_raises={v} count_of_21")
    wn, wt = writers()
    print(f"RESULT writer_naive_stamps={wn} count_of_{wt}")


main()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
