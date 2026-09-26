"""D1-s1-52 (instrument, P11): the hastub dt_util.now() is naive unless HASTUB_TZ is set or the
clock is frozen aware, while Home Assistant's is always aware -- so on the stub's default clock the
naive-vs-aware verdict of every stored-timestamp seam is inverted.

Metric: of 6 cells (3 production seams x stored stamp aware/naive), count those whose raise/no-raise
verdict with now = the stub's default dt_util.now() differs from the verdict with now = an aware
instant (what Home Assistant's dt_util.now() returns). Seams: snapshots.SnapshotRing.due,
curve_learning.CurveLearner._step_down, comfort_learning.ComfortLearner._decay (D1-s1-01's three).
Count key: whether the production seam raises TypeError.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/stub_naive_clock.py
  (perturbation: HASTUB_TZ=UTC PYTHONPATH=tests/hastub ... same script -> divergent=0)
Expected: divergent=6 of 6 (stub clock: aware stored raises 3/3, naive stored 0/3; aware clock:
aware 0/3, naive 3/3). stub_now_naive=1.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
from datetime import datetime, timedelta, timezone
from homeassistant.util import dt as dt_util
from heatpump_optimizer.snapshots import SnapshotRing
from heatpump_optimizer.curve_learning import CurveLearner
from heatpump_optimizer.comfort_learning import ComfortLearner

dt_util.freeze(None)
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


stub_now = dt_util.now()
ha_now = datetime.now(timezone.utc) + timedelta(0)
sv, hv = verdicts(stub_now), verdicts(ha_now)
div = sum(sv[k] != hv[k] for k in sv)
print(f"RESULT stub_now_naive={int(stub_now.tzinfo is None)}")
for k in sv:
    print(f"RESULT cell_{k[0]}_{k[1]}: stub_raises={sv[k]} ha_raises={hv[k]}")
print(f"RESULT divergent={div} of_{len(sv)}")
_rig.tail()
