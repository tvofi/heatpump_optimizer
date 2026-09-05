"""D9-05 judge instrument (#290): event-loop GIL starvation under solve.

Metric: with the solve running under a REAL asyncio loop (never FakeHass,
whose executor is inline), a heartbeat does ``await asyncio.sleep(0.001)``
and records gaps between wake-ups. Score ``gap_p50`` and ``starvation_share``
(gaps over 5 ms divided by solve wall). The thread-pool arm shows the
residual; the production ``async_run_solve_job`` arm shows the process fix.

Command (from the repository root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \\
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \\
      python3 tools/audit/round2/D9/j5_gil.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer.solve_process import (  # noqa: E402
    async_run_solve_job,
    run_optimize_worker,
)

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
START = stress["START"]


def _optimize(run: dict) -> None:
    run["optimizer"].optimize(
        run["initial"],
        run["prices"],
        run["outdoor"],
        run["wind"],
        run["rain"],
        run["solar"],
        START,
        None,
        run["surplus"],
    )


async def measure(label: str, solve_coro, duration_if_idle: float | None = None):
    gaps: list[float] = []
    running = True

    async def heartbeat():
        last = time.perf_counter()
        while running:
            await asyncio.sleep(0.001)
            now = time.perf_counter()
            gaps.append(now - last)
            last = now

    hb = asyncio.create_task(heartbeat())
    await asyncio.sleep(0.2)
    gaps.clear()
    proc0, thr0 = time.process_time(), time.thread_time()
    t0 = time.perf_counter()
    if duration_if_idle is not None:
        await asyncio.sleep(duration_if_idle)
    else:
        await solve_coro
    wall = time.perf_counter() - t0
    proc = time.process_time() - proc0
    thr_loop = time.thread_time() - thr0
    running = False
    await hb

    g = np.asarray(gaps) * 1000.0
    over = g[g > 5.0]
    d9lib.result(f"{label}.wall", wall * 1000.0, "ms_provisional")
    d9lib.result(f"{label}.executor_cpu", (proc - thr_loop) * 1000.0, "ms_provisional")
    d9lib.result(f"{label}.ticks", int(g.size), "count")
    d9lib.result(f"{label}.ticks_per_second", g.size / max(wall, 1e-9), "hz_provisional")
    d9lib.result(f"{label}.gap_p50", float(np.median(g)) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.gap_p99", float(np.percentile(g, 99)) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.longest_gil_hold", float(g.max()) if g.size else 0.0, "ms_provisional")
    d9lib.result(f"{label}.gaps_over_5ms", int(over.size), "count")
    d9lib.result(f"{label}.starvation_share", float(over.sum() / 1000.0 / max(wall, 1e-9)), "ratio_provisional")
    return proc, thr_loop


async def thread_solve(run: dict):
    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        await loop.run_in_executor(pool, _optimize, run)
    finally:
        pool.shutdown(wait=True)


async def process_solve(run: dict):
    os.environ["HPO_SOLVE_PROCESS"] = "1"
    try:
        sigma = np.zeros_like(run["prices"], dtype=float)
        await async_run_solve_job(
            None,
            run_optimize_worker,
            run["optimizer"],
            run["initial"],
            run["prices"],
            run["outdoor"],
            run["wind"],
            run["rain"],
            run["solar"],
            START,
            None,
            run["surplus"],
            sigma,
        )
    finally:
        os.environ.pop("HPO_SOLVE_PROCESS", None)


async def main():
    d9lib.result("switch_interval", sys.getswitchinterval() * 1000.0, "ms")
    await measure("idle_control", None, duration_if_idle=2.0)

    run_tz = build_case(season="winter", two_zone=True, dhw=True)
    await measure("thread_pool_two_zone_dhw", thread_solve(run_tz))
    await measure("process_pool_two_zone_dhw", process_solve(run_tz))

    orig = sys.getswitchinterval()
    sys.setswitchinterval(0.0005)
    try:
        d9lib.result("perturb_switch_interval", sys.getswitchinterval() * 1000.0, "ms")
        await measure("perturb_fast_thread_two_zone_dhw", thread_solve(run_tz))
    finally:
        sys.setswitchinterval(orig)


if __name__ == "__main__":
    asyncio.run(main())
    d9lib.closing(1.0)
