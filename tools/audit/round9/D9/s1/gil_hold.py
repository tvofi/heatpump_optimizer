"""D9-s1 H4: longest contiguous GIL hold and starvation share of an in-process
solve (the coordinator's worker-fallback route: optimize_in_process on HA's
executor), measured on a REAL asyncio loop with a real ThreadPoolExecutor.

Metric: gap = time between consecutive 1 ms heartbeat ticks of a task on the
loop while optimizer.optimize_in_process runs in a ThreadPoolExecutor;
report max gap (ms), p99 gap, and starvation share = fraction of the solve's
wall time covered by gaps > 5 ms. Gaps are attributed to the solve phase
(named optimizer methods, hooked) active at the gap's midpoint.
Count key: heartbeat timestamps taken on the loop thread (perf_counter).

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/gil_hold.py [--no-yield] [--switch MS]
Perturbations: --no-yield swaps optimizer._gil_yield for a no-op (the
in-iteration yield); --switch 20 sets sys.setswitchinterval(0.020): the max
gap must go UP under the latter (the interpreter's forced switch bounds it).
Provisional (wall-clock): re-take on a quiet box.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import asyncio
import bisect
import concurrent.futures
import threading
import time

import numpy as np

import stress
from heatpump_optimizer import optimizer as opt_mod
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PHASES = ["_plan_dhw_min_cost", "_plan_dhw_cheapest_first", "_repair_dhw_floor",
          "_clamp_dhw_to_capacity", "_apply_dhw_min_run", "_build_dhw_requirements",
          "_compute_baseline_power", "_build_result", "_baseline_dhw_economics",
          "_analyze_forecast_trajectory", "_deferred_energy_cost", "_terminal_cost"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-yield", action="store_true")
    ap.add_argument("--switch", type=float, default=0.0)
    ap.add_argument("--cell", default="two_zone_dhw_winter")
    args = ap.parse_args()
    cells = {"two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
             "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True)}
    spec = cells[args.cell]
    # Build the inputs once (solve inline), then re-solve under the loop.
    run = stress.build_case(**spec)
    optimizer = run["optimizer"]
    positional = (run["prices"], run["outdoor"], run["wind"], run["rain"], run["solar"],
                  stress.START, None, run["surplus"])
    keywords = dict(space_pins=run["space_pins"], power_caps_extra=run["power_caps_extra"])

    events: list[tuple[float, int, str]] = []  # (t, +1/-1, phase)
    lock = threading.Lock()
    saved = []
    for name in PHASES:
        orig = getattr(HeatPumpOptimizer, name, None)
        if orig is None:
            continue

        def w(self, *a, _o=orig, _n=name, **k):
            events.append((time.perf_counter(), 1, _n))
            try:
                return _o(self, *a, **k)
            finally:
                events.append((time.perf_counter(), -1, _n))
        saved.append((HeatPumpOptimizer, name, orig))
        setattr(HeatPumpOptimizer, name, w)
    o_msm = opt_mod._multi_start_minimize

    def msm(*a, **k):
        events.append((time.perf_counter(), 1, "_multi_start_minimize"))
        try:
            return o_msm(*a, **k)
        finally:
            events.append((time.perf_counter(), -1, "_multi_start_minimize"))
    saved.append((opt_mod, "_multi_start_minimize", o_msm))
    opt_mod._multi_start_minimize = msm
    yields: list[float] = []
    o_gy = opt_mod._gil_yield
    saved.append((opt_mod, "_gil_yield", o_gy))
    if args.no_yield:
        opt_mod._gil_yield = lambda: yields.append(time.perf_counter())
    else:
        def gy():
            yields.append(time.perf_counter())
            o_gy()
        opt_mod._gil_yield = gy
    if args.switch:
        sys.setswitchinterval(args.switch / 1000.0)

    ticks: list[float] = []
    solver_cpu = {"ms": 0.0}

    def job():
        t0 = time.thread_time()
        try:
            return opt_mod.optimize_in_process(optimizer, run["initial"], positional, keywords)
        finally:
            solver_cpu["ms"] = (time.thread_time() - t0) * 1000

    async def heartbeat(stop):
        while not stop.is_set():
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.001)

    async def drive():
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        stop = asyncio.Event()
        hb = asyncio.create_task(heartbeat(stop))
        await asyncio.sleep(0.05)
        t_start = time.perf_counter()
        await loop.run_in_executor(pool, job)
        t_end = time.perf_counter()
        stop.set()
        await hb
        pool.shutdown()
        return t_start, t_end

    p0, th0 = time.process_time(), time.thread_time()
    t_start, t_end = asyncio.run(drive())
    proc_ms = (time.process_time() - p0) * 1000
    loop_thread_ms = (time.thread_time() - th0) * 1000
    for obj, name, orig in saved:
        setattr(obj, name, orig)
    sys.setswitchinterval(0.005)

    ts = [t for t in ticks if t_start <= t <= t_end]
    gaps = np.diff(ts) * 1000
    wall = (t_end - t_start) * 1000
    long_ = gaps[gaps > 5.0]
    # phase attribution at each long gap's midpoint
    ev = sorted(events)
    times = [e[0] for e in ev]
    by_phase: dict[str, list[float]] = {}
    for i, g in enumerate(gaps):
        if g <= 5.0:
            continue
        mid = ts[i] + g / 2000
        k = bisect.bisect_right(times, mid)
        stack: list[str] = []
        for t, d, n in ev[:k]:
            if d > 0:
                stack.append(n)
            elif n in stack:
                stack.remove(n)
        ph = stack[-1] if stack else "other"
        by_phase.setdefault(ph, []).append(g)
    tag = args.cell + ("_noyield" if args.no_yield else "") + (f"_switch{args.switch:g}" if args.switch else "")
    C.result(f"{tag}.solve_wall_ms", round(wall, 1), "ms (provisional)")
    C.result(f"{tag}.ticks", len(ts), "count")
    C.result(f"{tag}.max_gap_ms", round(float(gaps.max()), 2), "ms (provisional)")
    C.result(f"{tag}.p99_gap_ms", round(float(np.percentile(gaps, 99)), 2), "ms (provisional)")
    C.result(f"{tag}.median_gap_ms", round(float(np.median(gaps)), 2), "ms (provisional)")
    C.result(f"{tag}.gaps_over_5ms", int(long_.size), "count")
    C.result(f"{tag}.starvation_share", round(float(long_.sum()) / wall, 4), "ratio (provisional)")
    for ph, gs in sorted(by_phase.items(), key=lambda kv: -max(kv[1])):
        C.result(f"{tag}.long_gaps[{ph}]", f"n={len(gs)},max={max(gs):.2f}", "ms (provisional)")
    ys = [y for y in yields if t_start <= y <= t_end]
    if len(ys) > 1:
        iv = np.diff(ys) * 1000
        k = int(np.argmax(iv))
        mid = ys[k] + iv[k] / 2000
        kk = bisect.bisect_right(times, mid)
        stack = []
        for t, d, n in ev[:kk]:
            if d > 0:
                stack.append(n)
            elif n in stack:
                stack.remove(n)
        C.result(f"{tag}.gil_yield_calls", len(ys), "count")
        C.result(f"{tag}.max_interval_between_gil_yields_ms", round(float(iv.max()), 2), "ms (provisional)")
        C.result(f"{tag}.p99_interval_between_gil_yields_ms", round(float(np.percentile(iv, 99)), 2), "ms (provisional)")
        C.result(f"{tag}.max_interval_phase", stack[-1] if stack else "other")
        first, last = ys[0] - t_start, t_end - ys[-1]
        C.result(f"{tag}.solve_head_before_first_yield_ms", round(first * 1000, 1), "ms (provisional)")
        C.result(f"{tag}.solve_tail_after_last_yield_ms", round(last * 1000, 1), "ms (provisional)")
    C.result(f"{tag}.solver_thread_cpu_ms", round(solver_cpu["ms"], 1), "ms (deliberate executor thread, subtracted)")
    tf = (proc_ms - solver_cpu["ms"]) / loop_thread_ms if loop_thread_ms > 0 else 1.0
    C.trailer(round(tf, 3))


if __name__ == "__main__":
    main()
