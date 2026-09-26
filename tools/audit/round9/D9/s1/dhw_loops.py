"""D9-s1 H5: CPU share and step work of the DHW planning loops, and how the
work scales with the horizon.

Metric: per DHW planner method of optimizer.HeatPumpOptimizer (hooked,
exclusive of nested planners; the total is the outermost inclusive CPU), thread CPU / optimize() thread CPU, and
ThermalModel.simulate_dhw_step calls made under it (hooked), per cell.
Count key: calls delivered to ThermalModel.simulate_dhw_step.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/dhw_loops.py [--hours 48]
Perturbation: --hours 48 (horizon length): dhw step calls must go UP; the
ratio calls(48h)/calls(24h) says whether the loops are linear (~2) or
superlinear (>2) in the horizon.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import collections
import time

import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PLANNERS = ["_build_dhw_requirements", "_plan_dhw_min_cost", "_plan_dhw_cheapest_first",
            "_repair_dhw_floor", "_clamp_dhw_to_capacity", "_apply_dhw_min_run",
            "_dhw_legionella_plan", "_dhw_window_floors", "_dhw_coil_wood_forecast",
            "_baseline_dhw_economics"]

CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_dhw_summer": dict(season="summer", two_zone=False, dhw=True),
    "single_zone_dhw_winter_extreme": dict(season="winter_extreme", two_zone=False, dhw=True),
    "single_zone_dhw_flat": dict(season="flat", two_zone=False, dhw=True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()
    cpu = collections.Counter()
    calls = collections.Counter()
    # Exclusive attribution: CPU and dhw-step calls are charged to the
    # innermost active planner (a stack), and "total" is the outermost
    # planner's inclusive CPU.
    stack: list[list] = []  # [name, t_enter, child_cpu]
    incl = {"t": 0.0}
    depth = {"who": None}
    saved = []
    for name in PLANNERS:
        orig = getattr(HeatPumpOptimizer, name)

        def w(self, *a, _o=orig, _n=name, **k):
            stack.append([_n, time.thread_time(), 0.0])
            depth["who"] = _n
            try:
                return _o(self, *a, **k)
            finally:
                n_, t0, child = stack.pop()
                el = time.thread_time() - t0
                cpu[n_] += el - child
                if stack:
                    stack[-1][2] += el
                    depth["who"] = stack[-1][0]
                else:
                    incl["t"] += el
                    depth["who"] = None
        saved.append((name, orig))
        setattr(HeatPumpOptimizer, name, w)
    o_dhw = stress.SolverWork._dhw_step_wrapped

    def dstep(*a, **k):
        calls[depth["who"] or "other"] += 1
        return o_dhw(*a, **k)
    stress.SolverWork._dhw_step_wrapped = dstep
    tot_tf = 1.0
    try:
        for cell, spec in CELLS.items():
            cpu.clear(); calls.clear(); incl["t"] = 0.0
            with C.Clock() as clk:
                run = stress.build_case(hours=args.hours, **spec)
            tot_tf = max(tot_tf, clk.thread_factor)
            solve = run["solve_thread_ms"] / 1000
            tag = f"{cell}_h{args.hours}"
            dsum = incl["t"]
            C.result(f"{tag}.dhw_planners_share_of_solve", round(dsum / solve, 4), "ratio")
            C.result(f"{tag}.dhw_step_calls_total", sum(calls.values()), "calls")
            for n, v in sorted(cpu.items(), key=lambda kv: -kv[1]):
                C.result(f"{tag}.share[{n}]", round(v / solve, 4), f"ratio; dhw_step_calls={calls[n]}")
            C.result(f"{tag}.solve_thread_ms", round(solve * 1000, 1), "ms (provisional)")
    finally:
        stress.SolverWork._dhw_step_wrapped = o_dhw
        for name, orig in saved:
            setattr(HeatPumpOptimizer, name, orig)
    C.trailer(tot_tf)


if __name__ == "__main__":
    main()
