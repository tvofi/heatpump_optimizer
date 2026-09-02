"""D9 metric 3: longest contiguous GIL hold and event-loop starvation share.

Metric (binding, tools/audit/briefs/D9.md): with the solve running in a
``ThreadPoolExecutor`` under a REAL asyncio loop (never FakeHass, whose
executor is inline), a heartbeat task does ``await asyncio.sleep(0.001)`` in
a loop and records the gap between consecutive wake-ups. Longest GIL hold =
the maximum gap (ms); starvation share = the summed length of gaps over 5 ms
divided by the solve's wall time. An idle heartbeat (no solve) is the null
control for the box's own scheduling noise.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h3_gil_hold.py

Expected (baseline c398fc8; WALL numbers, provisional on the shared box):
    idle control      max gap a few ms, starvation share ~0
    two_zone_dhw      starvation share > 0.9 (the loop wakes ~every 5 ms,
                      the interpreter's switch interval, for the whole solve;
                      the two sleep(0.002) yields are the only gaps under it),
                      max gap 10-60 ms
    dhw_cap_zero_range (scalar path, ~15-20 s of CPU) the same share sustained
                      for the whole solve; max gap of the same order
    perturbation sys.setswitchinterval 0.005 -> 0.05: max gap and p50 gap
                      rise to ~50 ms (the executor thread keeps the GIL ten
                      times longer per slice)

Instrumented symbols: optimizer:HeatPumpOptimizer.optimize (driven in the
executor), sys.setswitchinterval (the perturbation).
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
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

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
START = stress["START"]

# Stage attribution: the executor thread names what it is doing, the
# heartbeat records the name current when a long gap ends. Read-only hooks.
STAGE = ["-"]


def staged(name, orig, is_method=True):
    def wrapper(*a, **k):
        prev = STAGE[0]
        STAGE[0] = name
        try:
            return orig(*a, **k)
        finally:
            STAGE[0] = prev
    return wrapper


tm_mod.ThermalModel.simulate_trajectory_batch = staged("batch_sim", tm_mod.ThermalModel.simulate_trajectory_batch)
tm_mod.ThermalModel.simulate_trajectory = staged("scalar_sim", tm_mod.ThermalModel.simulate_trajectory)
opt_mod.linprog = staged("linprog", opt_mod.linprog)
opt_mod.HeatPumpOptimizer._plan_dhw_min_cost = staged("dhw_lp_build", opt_mod.HeatPumpOptimizer._plan_dhw_min_cost)
opt_mod.HeatPumpOptimizer._plan_dhw_cheapest_first = staged("dhw_greedy", opt_mod.HeatPumpOptimizer._plan_dhw_cheapest_first)
opt_mod.HeatPumpOptimizer._apply_dhw_min_run = staged("dhw_minrun", opt_mod.HeatPumpOptimizer._apply_dhw_min_run)
opt_mod._batch_fd_gradient = staged("batch_fd_gradient", opt_mod._batch_fd_gradient)
opt_mod.HeatPumpOptimizer._compute_baseline_power = staged("baseline_power", opt_mod.HeatPumpOptimizer._compute_baseline_power)


async def measure(label: str, solve, duration_if_idle: float | None = None):
    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=1)
    gaps: list[float] = []
    long_gaps: list[tuple[float, str]] = []
    running = True

    async def heartbeat():
        last = time.perf_counter()
        while running:
            await asyncio.sleep(0.001)
            now = time.perf_counter()
            gaps.append(now - last)
            if now - last > 0.02:
                long_gaps.append((now - last, STAGE[0]))
            last = now

    hb = loop.create_task(heartbeat())
    await asyncio.sleep(0.2)  # settle
    gaps.clear()
    proc0, thr0 = time.process_time(), time.thread_time()
    t0 = time.perf_counter()
    if solve is None:
        await asyncio.sleep(duration_if_idle)
    else:
        await loop.run_in_executor(pool, solve)
    wall = time.perf_counter() - t0
    proc = time.process_time() - proc0
    thr_loop = time.thread_time() - thr0
    running = False
    await hb
    pool.shutdown(wait=True)

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
    for gap, stage in sorted(long_gaps, reverse=True)[:5]:
        d9lib.result(f"{label}.long_gap", f"{gap * 1000.0:.1f}ms@{stage}", "ms_provisional@stage")
    return proc, thr_loop


def make_solver(run, **extra):
    def solve():
        return run["optimizer"].optimize(
            run["initial"], run["prices"], run["outdoor"], run["wind"],
            run["rain"], run["solar"], START, None, run["surplus"], **extra,
        )
    return solve


async def main():
    d9lib.result("switch_interval", sys.getswitchinterval() * 1000.0, "ms")
    await measure("idle_control", None, duration_if_idle=2.0)

    run_tz = build_case(season="winter", two_zone=True, dhw=True)
    await measure("two_zone_dhw", make_solver(run_tz))

    run_sz = build_case(season="winter", two_zone=False, dhw=True)
    await measure("single_zone_dhw", make_solver(run_sz))

    p_max = float(run_tz["params"].max_electrical_power)
    cap = np.full(run_tz["n"], 0.8 * p_max)
    await measure("dhw_cap_zero_range", make_solver(run_tz, power_caps_extra=cap))

    sys.setswitchinterval(0.05)
    try:
        d9lib.result("perturb_switch_interval", sys.getswitchinterval() * 1000.0, "ms")
        await measure("perturb_switch50ms_two_zone_dhw", make_solver(run_tz))
    finally:
        sys.setswitchinterval(0.005)


asyncio.run(main())
d9lib.closing(1.0)
