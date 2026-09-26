"""V1 verifier harness for D1-s3-03: which persisted set-point value types in the
pump_duty store make pump_arbiter.apply raise on every call?

Metric (one line): per (slot, value) cell, whether the SECOND pump_arbiter.apply
after the real loader (pump_arbiter._load) read a pump_duty payload whose
written[slot][0] is that value, with an aware ISO time, still raises; summed
over the non-numeric cells (repeat_raise_nonnumeric) and the numeric control
cells (repeat_raise_numeric, expect 0).
Count key: an exception escaping production pump_arbiter.apply.

Cells: slots {space_setpoint, dhw_setpoint, mode} x values
  {"abc", "40", [40], {"v": 40}, None, true, 40, 40.0}.
Perturbation (--perturb, in memory): after the real _load, drop any set-point
slot whose value is not a real number and any mode slot whose value is not a
str (the finder's fix, non-numeric part only) -> repeat_raise_nonnumeric 0.

Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v1/u1/pump_setpoint_types.py [--perturb]
Baseline 1936d5ca (evidence tree 6f51db2c). Machine: 4 vCPU cloud container (G1-V1).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from unittest import mock

logging.disable(logging.CRITICAL)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import pump_arbiter  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = "--perturb" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()
TZ = dt_util.DEFAULT_TIME_ZONE
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=TZ)
SLOTS = ["space_setpoint", "dhw_setpoint", "mode"]
NONNUM = ["abc", "40", [40], {"v": 40}, None, True]
NUM = [40, 40.0]


def _coord(i):
    states = {
        "sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0"),
        "select.pump_mode": FakeState("Heating + DHW", attributes={
            "options": ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]}),
        "number.dhw_set": FakeState("40", attributes={"min": 40, "max": 63}),
        "number.water_set": FakeState("25", attributes={"min": 25, "max": 63}),
    }
    cfg = {
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0,
    }
    c = HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg, entry_id=f"v1ps{i}"))
    c._mode = MODE_AUTO
    return c


_orig_load = pump_arbiter._load


async def _fixed_load(coord):
    await _orig_load(coord)
    held = pump_arbiter.state_for(coord)
    for slot, (value, _at) in list(held.written.items()):
        ok = isinstance(value, str) if slot == "mode" else (
            isinstance(value, (int, float)) and not isinstance(value, bool))
        if not ok:
            del held.written[slot]


async def cell(i, slot, value):
    c = _coord(i)
    at = (T0 - timedelta(minutes=5)).isoformat()
    _storage._DISK[f"heatpump_optimizer_{c.entry.entry_id}_pump_duty"] = json.dumps(
        {"written": {slot: [value, at]}})
    raised = []
    for k in range(2):
        now = T0 + timedelta(minutes=2 * k)
        dt_util.freeze(now)
        try:
            await pump_arbiter.apply(c, now)
            raised.append(None)
        except Exception as err:  # noqa: BLE001
            raised.append(type(err).__name__)
    return raised


async def main():
    rows, i = [], 0
    for slot in SLOTS:
        for v in NONNUM + NUM:
            i += 1
            rows.append((slot, v, await cell(i, slot, v)))
    return rows


if PERTURB:
    with mock.patch.object(pump_arbiter, "_load", _fixed_load):
        rows = asyncio.run(main())
else:
    rows = asyncio.run(main())
nn = num = 0
for slot, v, r in rows:
    print(f"  cell slot={slot} value={json.dumps(v)} raises={r}")
    if r[1] is not None:
        if v in NUM and not isinstance(v, bool):
            num += 1
        else:
            nn += 1
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT repeat_raise_nonnumeric={nn} cells_of_{len(SLOTS) * len(NONNUM)}")
print(f"RESULT repeat_raise_numeric={num} cells_of_{len(SLOTS) * len(NUM)}")
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
