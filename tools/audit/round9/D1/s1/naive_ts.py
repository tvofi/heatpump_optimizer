"""D1-s1 naive-timestamp harness: a persisted tz-naive timestamp leaf, loaded
through the real QuarantiningStore + loader, reaches an aware subtraction.

Metric (one line): per seam, the number of consumer calls (one per simulated
day, 21 days, aware clock) that raise after the store was loaded with the
seam's timestamp leaf written tz-naive; plus the snapshots the #42 ring took.
Count key: exceptions raised by the production consumer on the object the
production loader delivered (not any attribute of the input payload).

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/naive_ts.py [--fix] [--aware]
  default   naive leaf           expected: snapshot raises=21 taken=0, curve raises>=19,
                                 comfort raises=21 (override) and 21 (quiet)   (exact)
  --aware   control, aware leaf  expected: every raises=0, snapshot taken=3
  --fix     perturbation: each seam module's `datetime.fromisoformat` treats a
            naive stored time as UTC (the one-line rule drift.Cusum.load already
            applies) -> every raises=0
Sibling controls (always printed): drift.Cusum.load and AccuracyTracker.from_dict
lead_pending already normalise/drop a naive leaf -> 0 raises.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import comfort_learning, const, curve_learning, drift, snapshots  # noqa: E402
from heatpump_optimizer.accuracy import AccuracyTracker  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

FIX = "--fix" in sys.argv
AWARE = "--aware" in sys.argv
START = datetime(2026, 1, 12, 12, 0, tzinfo=timezone.utc)
DAYS = 21


class _AwareDatetime(datetime):
    @classmethod
    def fromisoformat(cls, s):  # the drift.Cusum.load rule
        v = datetime.fromisoformat(s)
        return v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)


def stamp(when):
    return when.isoformat() if AWARE else when.replace(tzinfo=None).isoformat()


def coordinator():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_COMFORT_LEARNING_ENABLED: True}
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    return coord


def run():
    out = {}
    past = START - timedelta(days=3)
    # --- seam 1: SnapshotRing.due via the #42 heartbeat -------------------
    coord = coordinator()
    ring = {"snapshots": [{"taken_at": stamp(past - timedelta(days=5)), "healthy": True,
                           "alarmed_at_capture": False, "accuracy": {}, "learners": {}}]}
    asyncio.run(coord._snapshot_store.async_save(ring))
    asyncio.run(coord._async_load_snapshots())
    before = len(coord._snapshot_ring.snapshots)
    raises = 0
    for d in range(DAYS):
        dt_util.freeze(START + timedelta(days=d))
        try:
            asyncio.run(coord._async_watch_learning_drift())
        except Exception:  # the production call site swallows this at DEBUG
            raises += 1
    total = len(coord._snapshot_ring.snapshots)
    out["snapshot_raises"] = raises
    # ring holds RING_SIZE=8 max; count snapshots newer than the stored one
    out["snapshot_taken"] = sum(1 for s in coord._snapshot_ring.snapshots
                                if s["taken_at"] >= START.isoformat()) if total >= before else -1
    # --- seam 2: CurveLearner._step_down via record_day ------------------
    coord = coordinator()
    thermal = {"curve_learner": {"bias": -1.0, "comfortable_days": 0, "resets": 0,
                                 "last_day": "", "last_step_at": stamp(past)}}
    asyncio.run(coord._thermal_learning_store.async_save(thermal))
    asyncio.run(coord._async_load_thermal_learning())
    raises = 0
    for d in range(DAYS):
        try:
            coord._curve_learner.record_day(START + timedelta(days=d), 5.0)
        except Exception:
            raises += 1
    out["curve_raises"] = raises
    out["curve_bias_after"] = round(coord._curve_learner.bias, 3)
    # --- seam 3: ComfortLearner._decay via the coordinator's two feeders --
    coord = coordinator()
    weight = float(coord._comfort_learner.configured_weight)
    acc = {"comfort": {"configured_weight": weight, "learned_weight": weight,
                       "evidence": 0.0, "overrides": 0, "last_update": stamp(past),
                       "history": []}}
    asyncio.run(coord._accuracy_store.async_save(acc))
    asyncio.run(coord._async_load_accuracy())
    coord._current_action = {"setpoint": 21.0}
    coord._prices = [{"total": 1.0}]
    raises = 0
    for d in range(DAYS):
        dt_util.freeze(START + timedelta(days=d))
        try:
            coord.record_setpoint_override(23.0)  # climate.py:345's call
        except Exception:
            raises += 1
    out["comfort_override_raises"] = raises
    coord = coordinator()
    asyncio.run(coord._accuracy_store.async_save(acc))
    asyncio.run(coord._async_load_accuracy())
    coord._optimization_result = SimpleNamespace(
        room_temp_trajectory=[21.0] * 48, prices=[0.5 + (h % 12) / 12 for h in range(48)],
        power_schedule=[1.0] * 48)
    raises = 0
    for d in range(DAYS):
        dt_util.freeze(START + timedelta(days=d))
        try:
            coord._record_quiet_comfort_period()  # coordinator.py:5096, unguarded in the solve
        except Exception:
            raises += 1
    out["comfort_quiet_raises"] = raises
    dt_util.freeze(None)
    # --- sibling controls: seams that already normalise -------------------
    c = drift.Cusum(threshold=5.0, drift=0.1)
    c.load({"stat": 1.0, "tripped": True, "last_fed": past.replace(tzinfo=None).isoformat()})
    sib = 0
    try:
        c.release_if_starved(START, 72.0)
    except Exception:
        sib += 1
    t = AccuracyTracker.from_dict({"lead_pending": [[past.replace(tzinfo=None).isoformat(), 1.0, 21.0]]})
    try:
        t.score_lead_predictions(START, 21.0)
    except Exception:
        sib += 1
    out["sibling_raises"] = sib
    return out


if FIX:
    with mock.patch.object(comfort_learning, "datetime", _AwareDatetime), \
         mock.patch.object(curve_learning, "datetime", _AwareDatetime), \
         mock.patch.object(snapshots, "datetime", _AwareDatetime):
        res = run()
else:
    res = run()
print(f"# arm={'fix' if FIX else 'aware' if AWARE else 'naive'}")
for k, v in res.items():
    print(f"RESULT {k}={v} count")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
