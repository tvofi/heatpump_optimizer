"""D14 sweep N-unbudgeted-background: a burst of K user-triggered background
jobs through one seam, counted at the production worker submit.

Metric: entries into coordinator._run_in_process (each holds _PROCESS_LOCK for
one job) started by K concurrent calls of a seam, split by job callable
(__qualname__), plus multi-start solver entries (optimizer._multi_start_minimize)
the burst causes, and the latency of a scheduled solve submitted right behind
the burst over its solo latency.  Seams:
  diagnose   coordinator.async_diagnose_interval (diagnose_interval service / button)
  whatif     coordinator.async_simulate(steady=True)  (positive control: D9-s1-03)
Arms: --seam S --k K ; --guard adds an in-memory in-flight guard on the seam
(one-line: a second concurrent call returns at once) -> jobs must fall to the
K=1 level.  Null control: K=1.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/background/probe_burst.py --seam diagnose --k 4
Route and fixture: dev/audit/rounds/round11/D9/s1/d9s1lib.py (the D9-s1 harness library), the shipped worker.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import collections  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "D9", "s1"))
import d9s1lib as L  # noqa: E402


async def burst(seam: str, k: int, guard: bool):
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import optimizer as om
    from heatpump_optimizer.const import SIMULATE_MIN_INTERVAL_SECONDS
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=8)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    coord = L.make_coordinator(hass, dict(house(two_zone=True, dhw=True)), entry_id=f"bb_{seam}_{k}_{int(guard)}")
    for i in range(2):
        now = L.CYCLE_NOW + timedelta(minutes=30 * i)
        dtu.freeze(now)
        L.feed(coord, now)
        coord.data = await coord._async_update_data()

    jobs = collections.Counter()
    real_run = cm._run_in_process

    def counting_run(fn, args):
        jobs[getattr(fn, "__qualname__", "?")] += 1
        return real_run(fn, args)

    cm._run_in_process = counting_run
    inflight = {"n": 0}

    async def one(i):
        if guard and inflight["n"] > 0:
            return {"rate_limited": True}
        inflight["n"] += 1
        try:
            if seam == "diagnose":
                return await coord.async_diagnose_interval()
            return await coord.async_simulate({"target_temp": 20.0 + 0.1 * i}, steady=True)
        finally:
            inflight["n"] -= 1

    base = L.CYCLE_NOW + timedelta(minutes=30, seconds=60)
    try:
        tasks = []
        for i in range(k):
            dtu.freeze(base + timedelta(seconds=(SIMULATE_MIN_INTERVAL_SECONDS + 0.05) * i))
            tasks.append(asyncio.create_task(one(i)))
            await asyncio.sleep(0.05)
        opt, inp, _ = L.make_solve("two_zone_dhw")
        t = time.perf_counter()
        sched = asyncio.create_task(cm._await_optimize(hass, opt, inp))
        await asyncio.gather(*tasks, return_exceptions=True)
        await sched
        sched_s = time.perf_counter() - t
        # let any refresh the seam requested run out
        await asyncio.sleep(0.5)
    finally:
        cm._run_in_process = real_run
        cm._shutdown_process_pool()
        pool.shutdown()
    jobs["optimize_in_process"] -= 1 if k >= 0 else 0  # the scheduled solve's own
    return jobs, sched_s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seam", default="diagnose", choices=("diagnose", "whatif"))
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--guard", action="store_true")
    a = ap.parse_args()
    _, solo = asyncio.run(burst(a.seam, 0, False))
    print(f"RESULT k0.scheduled_solve_s={solo:.3f} s")
    for k in ((1, a.k) if not a.guard else (a.k,)):
        jobs, s = asyncio.run(burst(a.seam, k, a.guard))
        tag = f"{a.seam}.k{k}" + (".guard" if a.guard else "")
        total = sum(v for v in jobs.values() if v > 0)
        print(f"RESULT {tag}.worker_jobs={total} count  by_job={dict((n, v) for n, v in jobs.items() if v)}")
        print(f"RESULT {tag}.solve_jobs={max(0, jobs['optimize_in_process'])} count")
        print(f"RESULT {tag}.scheduled_latency_over_solo={s / solo:.2f} ratio")


if __name__ == "__main__":
    main()
