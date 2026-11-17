#!/usr/bin/env python3
"""D14-s3 (round 11): N-reap-lock -- stop and reload latency against a long
job holding ``coordinator._PROCESS_LOCK`` in the REAL process worker.

Two seams of the class's mechanism (teardown ordered behind the lock a solve
holds), each timed with a real child interpreter (``coordinator._ensure_worker``
spawning ``process_worker.py``) running ``time.sleep(JOB_S)`` as the job:

  stop    ``coordinator._shutdown_process_pool()`` (Home Assistant's stop, on
          the executor) called 1 s into the job: wall until it returns.
  reload  the entry's unload path (``__init__.async_unload_entry`` ->
          ``HeatPumpOptimizerCoordinator.async_shutdown``) does not reap the
          worker; a new entry's first job submitted 1 s into the old one:
          wall until that job returns (``coordinator._run_in_process``).

Metric: seconds (wall, provisional) of each, and the ratio to JOB_S.
Null control: the same calls with no job in flight (both ~0).
Perturbation (``--perturb``): the worker's ``kill``/``terminate`` made no-ops
(a read the kill does not break), so ``stop`` must rise to the
``_SHUTDOWN_LOCK_TIMEOUT_S`` bound (+ the 2 s terminate wait): up.

Perturbation of the reload seam (``--reap-on-unload``): the unload also runs
``_shutdown_process_pool`` after the cancel -> reload walls go down (to ~0).

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/reap_lock.py
Expected at 92d38ecb6: stop < 1 s; reload ~ JOB_S - 1 (the new job waits out
the old one). Wall numbers: provisional. Machine: box B7, 4 vCPU.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components"):
    sys.path.insert(0, str(_p))

JOB_S = 6.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--reap-on-unload", action="store_true",
                    help="perturbation of the reload seam: the unload reaps the worker")
    a = ap.parse_args()
    from heatpump_optimizer import coordinator as cm

    c0, t0c = time.process_time(), time.thread_time()

    def job_thread(seconds, out):
        began = time.monotonic()
        try:
            cm._run_in_process(time.sleep, (seconds,))
            out["ok"] = True
        except Exception as err:  # noqa: BLE001
            out["err"] = type(err).__name__
        out["wall"] = time.monotonic() - began

    # Null control: no job in flight.
    cm._run_in_process(time.sleep, (0.0,))  # spawn + warm
    began = time.monotonic()
    cm._shutdown_process_pool()
    stop_null = time.monotonic() - began
    began = time.monotonic()
    cm._run_in_process(time.sleep, (0.0,))
    reload_null = time.monotonic() - began

    # stop: the reap while a long job holds the lock.
    if a.perturb:
        w = cm._ensure_worker()
        w.kill = lambda: None
        w.terminate = lambda: None
    first: dict = {}
    th = threading.Thread(target=job_thread, args=(JOB_S, first))
    th.start()
    time.sleep(1.0)
    began = time.monotonic()
    cm._shutdown_process_pool()
    stop = time.monotonic() - began
    th.join()
    if a.perturb and cm._PROCESS_WORKER is not None:
        import subprocess
        subprocess.Popen.kill(cm._PROCESS_WORKER)
        cm._PROCESS_WORKER = None

    # reload: what the unload does to a refresh in flight -- cancel the task
    # awaiting ``_await_process`` (``async_shutdown``: ``refresh.cancel()``) --
    # on a real loop with a real thread-pool executor, as Home Assistant runs
    # it; then the new entry's first job through the same ``_await_process``.
    import asyncio
    import concurrent.futures

    class Hass:
        def __init__(self, loop, pool):
            self.loop, self.pool = loop, pool

        async def async_add_executor_job(self, fn, *args):
            return await self.loop.run_in_executor(self.pool, fn, *args)

    async def reload_arm(n_reloads):
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor(8)
        hass = Hass(loop, pool)
        await cm._await_process(hass, time.sleep, 0.0)  # warm
        olds = []
        for _ in range(n_reloads):
            task = asyncio.ensure_future(cm._await_process(hass, time.sleep, JOB_S))
            await asyncio.sleep(0.2)
            task.cancel()  # the unload: async_shutdown cancels the refresh in flight
            if a.reap_on_unload:  # what a fix would add to the unload path
                await hass.async_add_executor_job(cm._shutdown_process_pool)
            olds.append(task)
        await asyncio.sleep(1.0 - 0.2 * n_reloads if n_reloads < 5 else 0.0)
        began = time.monotonic()
        await cm._await_process(hass, time.sleep, 0.0)
        wall = time.monotonic() - began
        pool.shutdown(wait=True)
        return wall, [t.cancelled() for t in olds]

    reload1, c1 = asyncio.run(reload_arm(1))
    new = {"wall": reload1}
    old = {"cancelled": c1}
    reload3, c3 = asyncio.run(reload_arm(3))
    new3 = {"wall": reload3}
    cm._shutdown_process_pool()
    print(f"reload x3: new entry's 0 s job took {reload3:.2f} s behind 3 cancelled refreshes {c3}")
    print(f"RESULT reload3_first_job_wall_s={reload3:.2f} s (provisional)")
    print(f"RESULT reload3_ratio_to_one_job={reload3 / JOB_S:.2f} ratio")

    print(f"stop: {stop:.2f} s with a {JOB_S:g} s job in flight (null {stop_null:.2f} s); "
          f"in-flight job ended {first}")
    print(f"reload: new entry's 0 s job took {new.get('wall', -1):.2f} s "
          f"(null {reload_null:.2f} s); old job {old}")
    print(f"RESULT stop_wall_s={stop:.2f} s (provisional)")
    print(f"RESULT stop_null_wall_s={stop_null:.2f} s (provisional)")
    print(f"RESULT reload_first_job_wall_s={new.get('wall', -1):.2f} s (provisional)")
    print(f"RESULT reload_null_wall_s={reload_null:.2f} s (provisional)")
    print(f"RESULT reload_ratio_to_remaining={new.get('wall', 0) / (JOB_S - 1.0):.2f} ratio")
    pc, tc = time.process_time() - c0, time.thread_time() - t0c
    print(f"RESULT thread_factor={(pc / tc) if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
