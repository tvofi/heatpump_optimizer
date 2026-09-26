"""V2 (independent) harness for D1-s3-02.

Metric (one line): of K=31 unload offsets k (the coordinator's async_shutdown
starts k event-loop yields after a pump-mode state change is dispatched to the
arbiter's production state listener), the count after which, all tasks drained,
at least one pump_arbiter registration (1-min timer or state listener) still
closes over the released coordinator; the pump services here behave like real
Home Assistant: select_option / number.set_value yield once, write the state and
dispatch state_changed to the registered listeners.
Count key: registrations production pump_arbiter._listen delivers to the
recording async_track_time_interval / stub async_track_state_change_event,
keyed on the closure cell holding the coordinator.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_arbiter_window.py [--guard]
Expected: leaking_offsets >= 1 of 31 at baseline; --guard (apply returns when
coord._entry_released, in memory): 0 of 31.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, sys, time, logging
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry, FakeState  # noqa
from heatpump_optimizer import pump_arbiter  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa
from heatpump_optimizer.const import MODE_AUTO  # noqa

GUARD = "--guard" in sys.argv
POOL = ThreadPoolExecutor(max_workers=1)
TIMERS = []


class Hass(FakeHass):
    def async_create_task(self, coro, *a, **k):
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, f, *a):
        return await asyncio.get_running_loop().run_in_executor(POOL, f, *a)


class Ev:
    def __init__(self, eid, st):
        self.data = {"entity_id": eid, "new_state": st, "old_state": None}


def _interval(hass, action, interval, *a, **k):
    e = (action, interval); TIMERS.append(e)
    return lambda: TIMERS.remove(e) if e in TIMERS else None


def holds(fn, coord):
    return any(getattr(c, "cell_contents", None) is coord for c in (getattr(fn, "__closure__", None) or ()))


def fire(hass, eid):
    for ents, action in list(getattr(hass, "state_listeners", [])):
        if eid in ents:
            action(Ev(eid, hass.states.get(eid)))


async def trial(k):
    TIMERS.clear()
    opts = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]
    hass = Hass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0"),
                 "select.pump_mode": FakeState("Heating + DHW", attributes={"options": opts}),
                 "number.dhw_set": FakeState("40", attributes={"min": 40, "max": 63}),
                 "number.water_set": FakeState("25", attributes={"min": 25, "max": 63})})

    async def select_option(call):
        await asyncio.sleep(0)
        hass.states.get(call.data["entity_id"]).state = call.data["option"]
        fire(hass, call.data["entity_id"])

    async def set_value(call):
        await asyncio.sleep(0)
        hass.states.get(call.data["entity_id"]).state = str(call.data["value"])
        fire(hass, call.data["entity_id"])
    hass.services.async_register("select", "select_option", select_option)
    hass.services.async_register("number", "set_value", set_value)
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
           "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
           "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0}
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id=f"u1arb{k}"))
    coord._mode = MODE_AUTO
    await asyncio.sleep(0.02)
    await pump_arbiter.apply(coord)
    for _ in range(20):
        await asyncio.sleep(0)
    # someone changes the pump mode; HA dispatches state_changed to the arbiter
    hass.states.get("select.pump_mode").state = "Cooling"
    fire(hass, "select.pump_mode")
    for _ in range(k):
        await asyncio.sleep(0)
    await coord.async_shutdown()
    for _ in range(30):
        await asyncio.sleep(0.002)
    live = sum(holds(a, coord) for a, _ in TIMERS) + sum(holds(a, coord) for _, a in getattr(hass, "state_listeners", []))
    return live


async def _guarded(coord, now=None, _o=pump_arbiter.apply):
    if getattr(coord, "_entry_released", False):
        return
    await _o(coord, now)


async def main():
    leaks = []
    for k in range(31):
        if await trial(k):
            leaks.append(k)
    return leaks


with mock.patch.object(pump_arbiter, "async_track_time_interval", _interval):
    if GUARD:
        with mock.patch.object(pump_arbiter, "apply", _guarded):
            leaks = asyncio.run(main())
    else:
        leaks = asyncio.run(main())
print(f"# leaking offsets k: {leaks}")
print(f"RESULT leaking_offsets={len(leaks)} count_of_31")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print("RESULT deliberate_thread_cpu_s=~0 (store I/O only)")
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
