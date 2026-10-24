"""D1-s1 executor-boundary harness (D1.M4), restricted to the learner state in
D1-s1's cells that reaches the solve: DhwProfileLearner (params.dhw_hourly_draw_pattern,
params.dhw_cooling_rate), ComfortLearner (opt_config.comfort_weight via
_apply_comfort_weight), AccuracyTracker (the margins array, built on the loop).

Metric (one line): number of solve-input fields (the objects _solve_snapshot hands the
worker) that differ after every loop-side writer of those learners runs while a real
ThreadPoolExecutor worker holds the snapshot and re-reads it 2000 times.
Count key: equality of the worker's snapshot fields before/after, and torn reads seen
by the worker thread.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/mid_solve.py [--share]
  default  expected: changed_fields=0 torn_reads=0 (exact)
  --share  perturbation: _solve_snapshot's copy.deepcopy replaced by identity (the
           snapshot shares the live objects) -> changed_fields>=3, direction up
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
The worker thread's CPU is deliberate: thread_factor is the residual per README.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import copy
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const, coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.comfort_learning import OverrideEvent  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

SHARE = "--share" in sys.argv
hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0, const.CONF_COMFORT_LEARNING_ENABLED: True}))
asyncio.run(coord._update_current_state())

ctx_patch = mock.patch.object(coord_mod.copy, "deepcopy", lambda x, *a: x) if SHARE else None
if ctx_patch:
    ctx_patch.start()
state, opt = coord._solve_snapshot()
if ctx_patch:
    ctx_patch.stop()
params, config = opt.model.params, opt.config


def fields():
    return {"dhw_pattern": tuple(params.dhw_hourly_draw_pattern),
            "dhw_cooling_rate": params.dhw_cooling_rate,
            "comfort_weight": config.comfort_weight}


before = fields()
stop = threading.Event()
torn = [0]
wcpu = [0.0]


def worker():
    t = time.thread_time()
    for _ in range(2000):
        p = list(params.dhw_hourly_draw_pattern)
        if len(p) != 24:
            torn[0] += 1
    wcpu[0] = time.thread_time() - t


with ThreadPoolExecutor(1) as ex:
    fut = ex.submit(worker)
    dl = coord._dhw_learner
    dl.apply_cooling_rate(dl.cooling_rate * 1.7 + 0.3)
    dl.apply_payload({"hourly_profile": [2.0] * 12 + [0.5] * 12, "cooling_rate": 1.9})
    coord._comfort_learner.learned_weight = coord._comfort_learner.learned_weight * 2.5
    coord._apply_comfort_weight()
    coord.record_setpoint_override(24.0)
    fut.result()
after = fields()
changed = sum(1 for k in before if before[k] != after[k])
print(f"# share={SHARE}")
print(f"RESULT changed_fields={changed} count")
print(f"RESULT torn_reads={torn[0]} count")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT deliberate_thread_cpu={wcpu[0]:.4f} s")
print(f"RESULT thread_factor={(p - wcpu[0]) / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
