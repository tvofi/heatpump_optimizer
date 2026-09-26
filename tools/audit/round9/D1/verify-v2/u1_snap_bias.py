"""V2 (independent) harness for D1-s1-02.

Metric (one line): of JSON-legal temperature_bias leaf variants in one healthy
snapshot, loaded by the production SnapshotRing.from_dict, the count for which
SnapshotRing.best_restore raises (manual service path, alarm off) and the count
for which it raises on the alarm path (ring alarmed, streak started later); plus
the number of days the ring's alarm latch would report a change over the 10
days after a raising alarm day (observe_bias driven directly).
Count key: exceptions out of best_restore; observe_bias return values.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_snap_bias.py [--fix]
Expected: raise_manual = raise_alarm = 5 of 8 variants ("0.3","garbage",[0.3],{"v":0.3},"nan") and
  0 for 0.3, None, true; latch_changes_after=0. --fix (float() under guard, in memory): 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import logging; logging.disable(logging.CRITICAL)
import numpy as np
from heatpump_optimizer import snapshots

FIX = "--fix" in sys.argv
VARIANTS = [0.3, None, True, "0.3", "garbage", [0.3], {"v": 0.3}, "nan"]
T0 = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


class _NP:
    """np as best_restore sees it under the fix: isfinite on float(x), guarded."""
    def __getattr__(self, n):
        return getattr(np, n)

    @staticmethod
    def isfinite(x):
        try:
            return np.isfinite(float(x))
        except (TypeError, ValueError, OverflowError):
            return False


def ring_for(bias, alarmed):
    d = {"snapshots": [{"taken_at": T0.isoformat(), "healthy": True, "alarmed_at_capture": False,
                        "accuracy": {"temperature_bias": bias}, "learners": {}}]}
    d = json.loads(json.dumps(d))
    if alarmed:
        d.update({"alarmed": True, "streak_started": (T0 + timedelta(days=20)).date().isoformat(),
                  "bias_days": 3})
    return snapshots.SnapshotRing.from_dict(d)


def main():
    rm = ra = 0
    per = []
    for b in VARIANTS:
        out = []
        for alarmed in (False, True):
            try:
                ring_for(b, alarmed).best_restore()
                out.append(0)
            except Exception:
                out.append(1)
        rm += out[0]; ra += out[1]
        per.append(f"{json.dumps(b)}:{out[0]}{out[1]}")
    print("# per-variant (manual,alarm) raise flags: " + " ".join(per))
    print(f"RESULT raise_manual={rm} count_of_{len(VARIANTS)}")
    print(f"RESULT raise_alarm={ra} count_of_{len(VARIANTS)}")
    # latch: drive observe_bias out-of-band until alarm, then 10 more days
    ring = ring_for("garbage", False)
    changes_after = 0
    tripped_day = None
    for d in range(20):
        now = T0 + timedelta(days=30 + d)
        ch = ring.observe_bias(now, 2.0, True)
        if ch and tripped_day is None:
            tripped_day = d
            try:
                ring.best_restore()
            except Exception:
                pass
        elif tripped_day is not None and ch:
            changes_after += 1
    print(f"RESULT alarm_trip_day={tripped_day} day_index")
    print(f"RESULT latch_changes_after={changes_after} count_of_{20 - (tripped_day or 0) - 1}")


if FIX:
    with mock.patch.object(snapshots, "np", _NP()):
        main()
else:
    main()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
