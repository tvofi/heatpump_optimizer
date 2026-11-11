"""D1-s3 M1: the pump-duty arbiter re-arms its listeners on an unloaded coordinator.

Metric: live arbiter registrations (time-interval timers + state-change
listeners) whose callback closes over the coordinator, counted after
``HeatPumpOptimizerCoordinator.async_shutdown`` returned and every task drained;
plus pump service writes issued by the released coordinator after shutdown.
Count key: the registrations production's ``pump_arbiter._listen`` delivers to
the (recording) helpers, keyed on the callback's closure cell holding ``coord``.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/arbiter_unload.py [--perturb] [--null]
  --null     no pump state event before the unload (control arm; expect 0).
  --perturb  in-memory fix: pump_arbiter.apply returns once coord._entry_released
             (expect 0).
Expected (default arm): live_registrations_after_unload=2 (exact), writes_after_unload=2 (exact);
--null and --perturb: 0 and 0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
Real asyncio loop: async_create_task schedules a real task; the executor is a
ThreadPoolExecutor. The unload is the coordinator's own async_shutdown, the
call HA's entry state machine makes; the concurrency is the event bus
dispatching a pump state change (``_changed``) just before the unload, which
HA does whenever the pump's select/number changes state.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
# Real HA's dt_util.now() is tz-aware; the stub is naive unless HASTUB_TZ is set.
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import sys
import time
import asyncio
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402

from heatpump_optimizer import pump_arbiter  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402

PERTURB = "--perturb" in sys.argv
NULL = "--null" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()

_POOL = ThreadPoolExecutor(max_workers=2)
TIMERS: list = []


class LoopHass(FakeHass):
    def async_create_task(self, coro, *a, **k):
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, func, *args):
        return await asyncio.get_running_loop().run_in_executor(_POOL, func, *args)


def _track_interval(hass, action, interval, *a, **k):
    entry = (action, interval)
    TIMERS.append(entry)

    def _unsub():
        if entry in TIMERS:
            TIMERS.remove(entry)
    return _unsub


def _holds(fn, coord):
    for cell in (getattr(fn, "__closure__", None) or ()):
        try:
            if cell.cell_contents is coord:
                return True
        except ValueError:
            pass
    return False


async def main():
    states = {
        "sensor.indoor": FakeState("21.4"),
        "sensor.outdoor": FakeState("-3.0"),
        "select.pump_mode": FakeState("Heating + DHW", attributes={
            "options": ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]}),
        "number.dhw_set": FakeState("40", attributes={"min": 40, "max": 63}),
        "number.water_set": FakeState("25", attributes={"min": 25, "max": 63}),
    }
    hass = LoopHass(states)
    cfg = {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "pump_duty_mode": "control",
        "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set",
        "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow",
        "dhw_tank_volume": 180.0,
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id="d1s3_unload"))
    coord._mode = MODE_AUTO
    await asyncio.sleep(0.05)          # deferred store loads land
    await pump_arbiter.apply(coord)    # one arbitration pass: listeners armed
    armed = sum(_holds(a, coord) for a, _ in TIMERS) + sum(
        _holds(a, coord) for _, a in getattr(hass, "state_listeners", []))
    if not NULL:
        # The event bus dispatches a pump state change: production's @callback.
        for ents, action in list(getattr(hass, "state_listeners", [])):
            if "select.pump_mode" in ents and _holds(action, coord):
                action(object())
    await coord.async_shutdown()       # the unload
    n_calls_at_unload = len(hass.services.calls)
    for _ in range(20):                # drain every task the loop holds
        await asyncio.sleep(0.01)
    live = sum(_holds(a, coord) for a, _ in TIMERS) + sum(
        _holds(a, coord) for _, a in getattr(hass, "state_listeners", []))
    # One tick of the leaked timer, as HA would fire it a minute later.
    hass.states.get("select.pump_mode").state = "Heating"
    from homeassistant.util import dt as dt_util
    dt_util.freeze(dt_util.now() + timedelta(minutes=2))
    for action, _ in list(TIMERS):
        if _holds(action, coord):
            await action()
    writes_after = len(hass.services.calls) - n_calls_at_unload
    return armed, live, writes_after


async def _guarded_apply(coord, now=None, _orig=pump_arbiter.apply):
    if getattr(coord, "_entry_released", False):
        return
    await _orig(coord, now)

with mock.patch.object(pump_arbiter, "async_track_time_interval", _track_interval):
    if PERTURB:
        with mock.patch.object(pump_arbiter, "apply", _guarded_apply):
            armed, live, writes = asyncio.run(main())
    else:
        armed, live, writes = asyncio.run(main())

_pool_cpu = 0.0
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"arm={'perturb' if PERTURB else 'null' if NULL else 'default'} armed_before_unload={armed}")
print(f"RESULT live_registrations_after_unload={live} count")
print(f"RESULT writes_after_unload={writes} count")
print(f"RESULT deliberate_thread_cpu={_pool_cpu:.3f} s")
print(f"RESULT thread_factor={(cpu - _pool_cpu) / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
