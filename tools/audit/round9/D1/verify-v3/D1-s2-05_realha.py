"""V3 reach for D1-s2-05 (HA stop waits out an in-flight solve) under real Home Assistant.

Metric: wall seconds of a REAL hass.async_stop() (the whole staged shutdown: stopping,
stop, final_write, close, executor shutdown) on a started real hass with the
integration's coordinator.async_register_worker_shutdown listener registered, when a
job of HOLD seconds (time.sleep, run by the real process worker through
coordinator._run_in_process on an executor thread) is in flight; ratio = stop wall /
HOLD. Control: the same stop with no job in flight. Perturbation --unlocked-reap:
coordinator._PROCESS_LOCK rebound to a fresh Lock just before the stop (the reap no
longer queues behind the transport) -> ratio falls toward 0.
Wall numbers are provisional (shared box); the ratio is the claim.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s2-05_realha.py [--hold 6] [--unlocked-reap] [--idle]
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
import threading

logging.disable(logging.CRITICAL)
HOLD = float(sys.argv[sys.argv.index("--hold") + 1]) if "--hold" in sys.argv else 6.0
UNLOCKED = "--unlocked-reap" in sys.argv
IDLE = "--idle" in sys.argv


async def main():
    hass = await make_hass()
    await hass.async_start()
    from heatpump_optimizer import coordinator as cm
    entry = make_entry({"indoor_temp_entity": "sensor.indoor"}, entry_id="v3stop")
    cm.async_register_worker_shutdown(hass, entry)
    await hass.async_add_executor_job(cm._run_in_process, time.sleep, (0.0,))  # warm the worker
    job = None
    if not IDLE:
        job = hass.loop.run_in_executor(None, _job)
        await asyncio.sleep(0.5)
        assert cm._PROCESS_LOCK.locked()
    if UNLOCKED:
        cm._PROCESS_LOCK = threading.Lock()
    t0 = time.monotonic()
    await hass.async_stop()
    wall = time.monotonic() - t0
    print(f"# arm={'idle' if IDLE else 'inflight'} unlocked_reap={UNLOCKED} hold={HOLD}s worker_after={cm._PROCESS_WORKER}")
    print(f"RESULT stop_wall_s={wall:.3f} s provisional")
    print(f"RESULT stop_over_hold={wall / HOLD:.3f} ratio")


def _job():
    from heatpump_optimizer import coordinator as cm
    try:
        cm._run_in_process(time.sleep, (HOLD,))
    except Exception as err:  # noqa: BLE001
        print(f"# job ended: {type(err).__name__}")

asyncio.run(main())
tail()
os._exit(0)
