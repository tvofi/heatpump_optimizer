"""V2 (independent) harness for D1-s3-03.

Metric (one line): per stored set-point value variant in the pump_duty store
("written": {"dhw_setpoint": [V, <aware stamp 1 h ago>]}), loaded by production
pump_arbiter._load through the entry's store, the number of 5 consecutive
production pump_arbiter.apply() calls (control duty, auto mode) that raise;
variants V in {40.0, 40, "40", "abc", [40], {"v": 40}, true, null}.
Count key: exceptions out of apply(); the persisted record re-read after the calls.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_pump_duty_load.py
Expected: 5 of 5 for "40", "abc", [40], {"v":40}; 0 for 40.0, 40, null; true (bool is a number) 0 (+-0);
  extra arm: an unknown slot key ("dhw") with a numeric value, 5 of 5 (KeyError in hold).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, json, sys, time, logging
from datetime import timedelta
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry, FakeState  # noqa
from homeassistant.util import dt as dt_util  # noqa
from heatpump_optimizer import pump_arbiter  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa
from heatpump_optimizer.const import MODE_AUTO  # noqa

VARIANTS = [40.0, 40, "40", "abc", [40], {"v": 40}, True, None]


async def trial(v, i, slot="dhw_setpoint"):
    opts = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]
    hass = FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0"),
                     "select.pump_mode": FakeState("Heating + DHW", attributes={"options": opts}),
                     "number.dhw_set": FakeState("48", attributes={"min": 40, "max": 63}),
                     "number.water_set": FakeState("25", attributes={"min": 25, "max": 63})})
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
           "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
           "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0}
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id=f"u1pd{i}"))
    c._mode = MODE_AUTO
    stamp = (dt_util.now() - timedelta(hours=1)).isoformat()
    payload = json.loads(json.dumps({"written": {slot: [v, stamp]}}))
    await pump_arbiter._store(c).async_save(payload)
    raised = 0
    for _ in range(5):
        try:
            await pump_arbiter.apply(c)
        except Exception:  # noqa: BLE001
            raised += 1
    rec = pump_arbiter.state_for(c).written.get(slot)
    return raised, (rec[0] if rec else "<none>")


async def main():
    tot = 0
    for i, v in enumerate(VARIANTS):
        r, kept = await trial(v, i)
        tot += int(r == 5)
        print(f"RESULT V{json.dumps(v)}_apply_raises={r} count_of_5 (record after: {kept!r})")
    print(f"RESULT variants_raising_every_call={tot} count_of_{len(VARIANTS)}")
    r, _ = await trial(40.0, 99, slot="dhw")
    print(f"RESULT unknown_slot_key_apply_raises={r} count_of_5 (slot 'dhw', value 40.0)")


asyncio.run(main())
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
