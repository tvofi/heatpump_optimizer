"""D9-s1 solves_per_cycle, shadow/what-if path: solves a burst of card
what-ifs starts, and how long they hold the solve worker ahead of the
scheduled solve.

Metric: worker jobs started (entries into coordinator._run_in_process, the
production process-worker submit, each holding _PROCESS_LOCK for one solve)
by K user what-ifs -- HeatPumpOptimizerCoordinator.async_simulate(overrides,
steady=True), the simulate_plan service's call -- issued with the frozen
clock advanced SIMULATE_MIN_INTERVAL_SECONDS + 0.05 s between them (each
passes whatif.limited_answer), all in flight together as a user's nudges
are when each answer takes longer than the interval. Reported beside it:
solver thread CPU per what-if in reference solves (contention-robust),
wall time from the first request to the last answer, and the latency of a
scheduled solve submitted right behind the burst over its latency alone
(k0, no burst). Keyed on _run_in_process entries.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_whatif_backlog.py [--k 4]

Route: the SHIPPED one (real persistent process worker, real _PROCESS_LOCK),
on a real asyncio loop with an 8-thread executor (HA's executor is wider).
Perturbation (in memory): whatif.limited_answer also answers from the held
state while a user what-if is in flight (an in-flight guard) -> jobs started
must go DOWN from K*per_whatif to per_whatif. Null control: K = 1.
Counts exact; wall/CPU provisional.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402


async def burst(k: int, guard: bool):
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import whatif
    from heatpump_optimizer.const import SIMULATE_MIN_INTERVAL_SECONDS
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=8)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    coord = L.make_coordinator(hass, dict(house(two_zone=True, dhw=True)),
                               entry_id=f"wb_{k}_{int(guard)}")
    for i in range(2):
        now = L.CYCLE_NOW + timedelta(minutes=30 * i)
        dtu.freeze(now)
        L.feed(coord, now)
        coord.data = await coord._async_update_data()

    entries = []
    lock_wait = []
    real_run = cm._run_in_process

    def counting_run(fn, args):
        name = getattr(fn, "__qualname__", "?")
        t = time.perf_counter()
        entries.append((name, t))
        out = real_run(fn, args)
        return out

    cm._run_in_process = counting_run
    real_limited = whatif.limited_answer
    inflight = {"n": 0}
    if guard:
        def guarded(held, now):
            # the asking call counts itself in inflight["n"]
            if inflight["n"] > 1:
                return {**(held.answer or {}), "rate_limited": True}
            return real_limited(held, now)
        whatif.limited_answer = guarded

    async def one(i):
        inflight["n"] += 1
        try:
            return await coord.async_simulate({"target_temp": 20.0 + 0.1 * i}, steady=True)
        finally:
            inflight["n"] -= 1

    try:
        base = L.CYCLE_NOW + timedelta(minutes=30, seconds=60)
        t0 = time.perf_counter()
        tasks = []
        for i in range(k):
            dtu.freeze(base + timedelta(seconds=(SIMULATE_MIN_INTERVAL_SECONDS + 0.05) * i))
            tasks.append(asyncio.create_task(one(i)))
            await asyncio.sleep(0.05)  # the request reaches the executor
        n_whatif_jobs_queued = len(entries)
        # the scheduled solve, submitted right behind the burst
        solve_start = time.perf_counter()
        opt, inp, _ = L.make_solve("two_zone_dhw")
        sched = asyncio.create_task(cm._await_optimize(hass, opt, inp))
        answers = await asyncio.gather(*tasks)
        t_last = time.perf_counter()
        await sched
        sched_done = time.perf_counter()
    finally:
        cm._run_in_process = real_run
        whatif.limited_answer = real_limited
        cm._shutdown_process_pool()
        pool.shutdown()
    jobs = len(entries) - 1  # minus the scheduled solve's own
    limited = sum(1 for a in answers if isinstance(a, dict) and a.get("rate_limited"))
    return {"jobs": jobs, "limited": limited, "burst_wall": t_last - t0,
            "sched_total": sched_done - solve_start, "queued": n_whatif_jobs_queued}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=4)
    a = ap.parse_args()
    swap0 = L.swapins()
    solo = asyncio.run(burst(0, False))
    L.result("k0.scheduled_solve_total_s", solo["sched_total"], "s")
    for k, guard in ((1, False), (a.k, False), (a.k, True)):
        r = asyncio.run(burst(k, guard))
        tag = f"k{k}" + (".inflight_guard" if guard else "")
        L.result(f"{tag}.worker_jobs_started", r["jobs"], "count")
        L.result(f"{tag}.worker_jobs_per_whatif", r["jobs"] / k, "count")
        L.result(f"{tag}.scheduled_solve_latency_over_solo", r["sched_total"] / solo["sched_total"], "ratio")
        L.result(f"{tag}.answers_rate_limited", r["limited"], "count")
        L.result(f"{tag}.burst_wall_s", r["burst_wall"], "s")
        L.result(f"{tag}.scheduled_solve_total_s", r["sched_total"], "s")
    rclock = L.Clock()
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.tail(rclock, swap0=swap0)


if __name__ == "__main__":
    main()
