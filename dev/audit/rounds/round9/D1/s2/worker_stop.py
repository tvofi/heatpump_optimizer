"""D1.M1/M4: Home Assistant stop while a solve is in flight.

Metric (one line): wall seconds the EVENT_HOMEASSISTANT_STOP listener that
``coordinator.async_register_worker_shutdown`` registers takes to return when
fired 0.1 s into a real coordinator solve (``stop_latency_inflight_s``), as a
fraction of that solve's own duration (``stop_latency_ratio``), against the
same listener fired with no solve in flight (null control,
``stop_latency_idle_s``).
Count key: the listener's own await, timed around the production callable;
the solve is the production ``async_run_optimization`` through the real
process worker (``_run_in_process`` / ``_shutdown_process_pool``).

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/worker_stop.py [--perturb unlocked_reap] [--reps 5]
Expected at baseline: stop_latency_ratio ~0.8-1.0 (the listener waits out the
solve), stop_latency_idle_s < 0.1; ratio is load-robust, absolutes are
provisional. Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation ``unlocked_reap``: the reap stops queueing behind the solve's
lock (in memory, ``_PROCESS_LOCK`` rebound to a fresh lock for the stop call
only, which is what a reap that terminates the child without taking the
transport lock does). stop_latency_ratio must fall toward 0.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import logging
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from homeassistant.const import EVENT_HOMEASSISTANT_STOP  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from lifecycle import CFG, RealLoopHass, _states, _wait  # noqa: E402


async def one(loop, pool, perturb):
    hass = RealLoopHass(_states(), loop, pool)
    entry = FakeEntry(data=dict(CFG))
    assert await ha_setup_entry(integration, hass, entry)
    c = entry.runtime_data
    # warm: the background first solve spawns the worker and imports
    await _wait(lambda: c._optimization_result is not None and not c._optimization_running, 90)
    (stop,) = hass.bus.listeners_for(EVENT_HOMEASSISTANT_STOP)

    # null control: nothing in flight
    t0 = time.monotonic()
    await stop(None)
    idle = time.monotonic() - t0
    # re-warm the worker the idle reap just ended
    await c.async_run_optimization()

    # a solve alone, for its duration
    t0 = time.monotonic()
    await c.async_run_optimization()
    solve = time.monotonic() - t0

    # the arm: stop fired 0.1 s into a solve
    task = loop.create_task(c.async_run_optimization())
    await _wait(lambda: c._optimization_running, 10)
    await asyncio.sleep(0.1)
    saved = cm._PROCESS_LOCK
    if perturb == "unlocked_reap":
        cm._PROCESS_LOCK = threading.Lock()
    t0 = time.monotonic()
    await stop(None)
    inflight = time.monotonic() - t0
    cm._PROCESS_LOCK = saved
    status = await task
    await ha_unload_entry(integration, hass, entry)
    return idle, solve, inflight, status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    ap.add_argument("--reps", type=int, default=5)
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    concurrent = sum(1 for _ in os.popen("ps aux | grep -E '[s]tress\\.py|[t]ests/run\\.sh'"))
    rows = []
    for _ in range(args.reps):
        loop = asyncio.new_event_loop()
        pool = ThreadPoolExecutor(max_workers=4)
        try:
            rows.append(loop.run_until_complete(one(loop, pool, args.perturb)))
        finally:
            pool.shutdown(wait=True)
            loop.close()
            cm._shutdown_process_pool()
    idle = statistics.median(r[0] for r in rows)
    solve = statistics.median(r[1] for r in rows)
    inflight = statistics.median(r[2] for r in rows)
    ratios = [r[2] / r[1] for r in rows]
    print(f"  per-rep (idle, solve, inflight, solve_status): {[tuple(round(x, 3) if isinstance(x, float) else x for x in r) for r in rows]}")
    print(f"RESULT stop_latency_idle_s={idle:.3f} s (median of {args.reps}) provisional")
    print(f"RESULT solve_s={solve:.3f} s provisional")
    print(f"RESULT stop_latency_inflight_s={inflight:.3f} s provisional")
    print(f"RESULT stop_latency_ratio={statistics.median(ratios):.3f} ratio (min {min(ratios):.3f}, max {max(ratios):.3f})")
    print(f"RESULT concurrent_stress_processes={concurrent}")
    print("RESULT deliberate_thread_cpu_s=0.000 (solve runs in the child process)")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
