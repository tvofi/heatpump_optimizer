"""V1 verifier harness for D1-s3-02: does the pump-arbiter re-registration after
unload survive Home Assistant's eager task start?

Real HA's hass.async_create_task starts the coroutine eagerly (eager_start=True
by default since 2024), so production's `_changed` callback runs `apply` up to
its first real suspension before the callback returns. The finder's harness
(tools/audit/round9/D1/s3/arbiter_unload.py) schedules the task lazily.

Metric (one line): arbiter timers + state listeners whose closure holds the
coordinator, live after async_shutdown returned and the loop drained; plus pump
service calls issued by the released coordinator's leaked tick afterwards.
Count key: registrations production's pump_arbiter._listen delivers to the
recording helpers (closure cell holding coord), and hass.services.calls.

Arms (--arm):
  lazy        the finder's scheduling (loop.create_task) -> expect 2 / 2
  eager       asyncio.Task(eager_start=True), the HA default -> measured
  eager_lock  eager, and a tick's apply is suspended inside a pump write
              (holding the arbiter lock) when the state event arrives -> measured
  null        eager_lock without the state event -> expect 0 / 0
Perturbation (--perturb): pump_arbiter.apply returns once coord._entry_released
(in memory) -> every arm 0 / 0.

Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v1/u1/arbiter_eager.py --arm eager [--perturb]
Expected: see RESULT lines (exact counts). Baseline 1936d5ca (evidence tree
6f51db2c). Machine: 4 vCPU cloud container (G1-V1 box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import pump_arbiter  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

ARM = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "eager"
PERTURB = "--perturb" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()
_POOL = ThreadPoolExecutor(max_workers=2)
TIMERS: list = []


class LoopHass(FakeHass):
    def async_create_task(self, coro, *a, **k):
        loop = asyncio.get_running_loop()
        if ARM == "lazy":
            return loop.create_task(coro)
        return asyncio.Task(coro, loop=loop, eager_start=True)

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


def _live(hass, coord):
    return sum(_holds(a, coord) for a, _ in TIMERS) + sum(
        _holds(a, coord) for _, a in getattr(hass, "state_listeners", []))


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
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0,
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id="v1_eager"))
    coord._mode = MODE_AUTO
    await asyncio.sleep(0.05)
    await pump_arbiter.apply(coord)
    calls0 = len(hass.services.calls)
    tick_task = None
    if ARM in ("eager_lock", "null"):
        # A tick's apply suspended inside a pump write, holding the lock.
        orig_call = hass.services.async_call

        async def slow_call(*a, **k):
            await asyncio.sleep(0.05)
            return await orig_call(*a, **k)
        hass.services.async_call = slow_call
        # Pump reset by the user: the arbiter will rewrite every slot.
        hass.states.get("select.pump_mode").state = "Heating"
        hass.states.get("number.water_set").state = "63"
        hass.states.get("number.dhw_set").state = "63"
        from homeassistant.util import dt as dt_util
        dt_util.freeze(dt_util.now() + timedelta(minutes=1))
        tick = next(a for a, _ in TIMERS if _holds(a, coord))
        tick_task = asyncio.get_running_loop().create_task(tick())
        await asyncio.sleep(0.01)          # tick now inside slow_call, lock held
        locked = state_lock = pump_arbiter.state_for(coord).lock.locked()
        print(f"tick_holds_lock={locked}")
    if ARM != "null":
        for ents, action in list(getattr(hass, "state_listeners", [])):
            if "select.pump_mode" in ents and _holds(action, coord):
                action(object())
    await coord.async_shutdown()
    n_at_unload = len(hass.services.calls)
    for _ in range(40):
        await asyncio.sleep(0.01)
    if tick_task is not None:
        await tick_task
    live = _live(hass, coord)
    n_drained = len(hass.services.calls)
    # One tick of any leaked timer, as HA fires it later, with the pump reset
    # again (lazy/eager arms: the finder's 2 min; lock arms: past the retry).
    hass.states.get("select.pump_mode").state = "Heating" if ARM in ("lazy", "eager") else "Cooling"
    from homeassistant.util import dt as dt_util
    dt_util.freeze(dt_util.now() + timedelta(minutes=2 if ARM in ("lazy", "eager") else 30))
    for action, _ in list(TIMERS):
        if _holds(action, coord):
            await action()
    _h = pump_arbiter.state_for(coord)
    print(f"after_tick written={_h.written} retry={_h.retry} misses={_h.misses} mode={coord._mode}")
    return live, len(hass.services.calls) - n_drained, n_drained - n_at_unload


async def _guarded_apply(coord, now=None, _orig=pump_arbiter.apply):
    if getattr(coord, "_entry_released", False):
        return
    await _orig(coord, now)

with mock.patch.object(pump_arbiter, "async_track_time_interval", _track_interval):
    if PERTURB:
        with mock.patch.object(pump_arbiter, "apply", _guarded_apply):
            live, leaked_writes, drain_writes = asyncio.run(main())
    else:
        live, leaked_writes, drain_writes = asyncio.run(main())

cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"arm={ARM} perturb={PERTURB}")
print(f"RESULT live_registrations_after_unload={live} count")
print(f"RESULT leaked_tick_writes={leaked_writes} count")
print(f"RESULT writes_during_drain={drain_writes} count")
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
