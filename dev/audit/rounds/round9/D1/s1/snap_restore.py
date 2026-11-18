"""D1-s1 snapshot-restore harness: a snapshot whose accuracy.temperature_bias leaf
is JSON-legal but not a number (a string, list or dict) passes
SnapshotRing.from_dict and makes SnapshotRing.best_restore raise, which (a) fails
the restore_learned_snapshot service and (b) on the #42 drift path aborts the
heartbeat before the accuracy_drift repair issue is raised -- and, the ring's
`alarmed` latch being already set, no later day raises it either.

Metric (one line): over bias-leaf variants V = {"0.3", "garbage", [0.3], {"v":0.3}},
(1) count of variants where the coordinator's restore service raises, and
(2) count of variants where 10 out-of-band days end with NO accuracy_drift issue.
Count key: exceptions from, and issues raised by, production calls on the ring the
production loader (QuarantiningStore -> SnapshotRing.from_dict) delivered.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/snap_restore.py [--fix] [--control]
  default    expected: service_raises=4 missing_issue=4          (exact)
  --control  bias leaf 0.3 (a number) in every variant -> 0 and 0
  --fix      perturbation: best_restore's np.isfinite reads float(bias) under a
             (TypeError, ValueError) guard, skipping the snapshot -> 0 and 0
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
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, snapshots as snap_mod  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

FIX = "--fix" in sys.argv
CONTROL = "--control" in sys.argv
START = datetime(2026, 1, 12, 12, 0, tzinfo=timezone.utc)
VARIANTS = ["0.3", "garbage", [0.3], {"v": 0.3}]


def coordinator():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    return hass, coord


def ring_payload(bias):
    return {"snapshots": [{"taken_at": (START - timedelta(days=20)).isoformat(), "healthy": True,
                           "alarmed_at_capture": False,
                           "accuracy": {"temperature_bias": 0.3 if CONTROL else bias},
                           "learners": {}}]}


def run():
    service_raises = missing_issue = 0
    _orig_healthy = HeatPumpOptimizerCoordinator._inputs_healthy
    for bias in VARIANTS:
        hass, coord = coordinator()
        asyncio.run(coord._snapshot_store.async_save(ring_payload(bias)))
        asyncio.run(coord._async_load_snapshots())
        try:
            asyncio.run(coord.async_restore_learned_snapshot())
        except Exception:
            service_raises += 1
        # drift path: bias +1.0 °C for 10 days on healthy inputs
        hass, coord = coordinator()
        asyncio.run(coord._snapshot_store.async_save(ring_payload(bias)))
        asyncio.run(coord._async_load_snapshots())
        for i in range(20):
            coord._accuracy.record(AccuracySample(when=START, predicted_temp=22.0, actual_temp=21.0))
        with mock.patch.object(HeatPumpOptimizerCoordinator, "_inputs_healthy", lambda self: True):
            for d in range(10):
                dt_util.freeze(START + timedelta(days=d))
                try:
                    asyncio.run(coord._async_watch_learning_drift())
                except Exception:
                    pass  # coordinator.py's call site swallows this at DEBUG
        dt_util.freeze(None)
        issues = [i for i in (getattr(hass, "issues", None) or []) if i[1] == "accuracy_drift"]
        if not issues:
            missing_issue += 1
    return service_raises, missing_issue


_orig = snap_mod.SnapshotRing.best_restore


def _fixed(self):
    real = snap_mod.np.isfinite
    def guarded(x):
        try:
            return real(float(x))
        except (TypeError, ValueError, OverflowError):
            return False
    with mock.patch.object(snap_mod.np, "isfinite", guarded):
        return _orig(self)


if FIX:
    with mock.patch.object(snap_mod.SnapshotRing, "best_restore", _fixed):
        s, m = run()
else:
    s, m = run()
print(f"# arm={'fix' if FIX else 'control' if CONTROL else 'defect'} variants={len(VARIANTS)}")
print(f"RESULT service_raises={s} count")
print(f"RESULT missing_issue={m} count")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
