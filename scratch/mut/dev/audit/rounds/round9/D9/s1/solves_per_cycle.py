"""D9-s1 H8: full solves (entries into optimizer._multi_start_minimize) per
optimize() call, by path, the CPU share of each, and whether the co-optimize
re-solve (HeatPumpOptimizer._co_optimize) was adopted.

Metric: per cell, entries into _multi_start_minimize (hooked) split by caller
(first space solve vs the _co_optimize re-solve), the thread-CPU share of the
optimize() call each entry took, the candidate count each was handed, and
adopted = _co_optimize returned the re-solved space plan (identity of the
returned array with the re-solve's).
Count key: calls delivered to _multi_start_minimize; adoption keyed on the
array _co_optimize RETURNS.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/solves_per_cycle.py [--no-coopt]
Perturbation: --no-coopt swaps _co_optimize for the identity (returns its
inputs): entries per two-zone DHW cell must go DOWN from 2 to 1.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import time

import stress
from heatpump_optimizer import optimizer as opt_mod
from heatpump_optimizer.optimizer import HeatPumpOptimizer

CELLS = {
    "two_zone_dhw_winter": dict(season="winter", two_zone=True, dhw=True),
    "two_zone_dhw_shoulder": dict(season="shoulder", two_zone=True, dhw=True),
    "two_zone_dhw_winter_extreme": dict(season="winter_extreme", two_zone=True, dhw=True),
    "two_zone_dhw_summer": dict(season="summer", two_zone=True, dhw=True),
    "single_zone_dhw_winter": dict(season="winter", two_zone=False, dhw=True),
    "single_zone_dhw_shoulder": dict(season="shoulder", two_zone=False, dhw=True),
    "single_zone_dhw_winter_extreme": dict(season="winter_extreme", two_zone=False, dhw=True),
    "single_zone_dhw_fuse_3p68": dict(season="winter", two_zone=False, dhw=True, power_cap_kw=3.68),
    "two_zone_dhw_flat": dict(season="flat", two_zone=True, dhw=True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-coopt", action="store_true")
    args = ap.parse_args()
    o_msm = opt_mod._multi_start_minimize
    o_co = HeatPumpOptimizer._co_optimize
    log = []
    state = {"in_co": False, "co": None}

    def msm(objective, candidates, *a, **k):
        t0 = time.thread_time()
        try:
            return o_msm(objective, candidates, *a, **k)
        finally:
            log.append(("co_optimize" if state["in_co"] else "first", len(candidates),
                        time.thread_time() - t0))

    def co(self, h, **kw):
        if args.no_coopt:
            return kw["space_power"], kw["dhw_power"], kw["status"]
        state["in_co"] = True
        try:
            out = o_co(self, h, **kw)
        finally:
            state["in_co"] = False
        state["co"] = out[0] is not kw["space_power"]
        return out
    opt_mod._multi_start_minimize = msm
    HeatPumpOptimizer._co_optimize = co
    tf = 1.0
    wasted = []
    try:
        for cell, spec in CELLS.items():
            log.clear(); state["co"] = None
            with C.Clock() as clk:
                run = stress.build_case(**spec)
            tf = max(tf, clk.thread_factor)
            solve = run["solve_thread_ms"] / 1000
            tag = cell + ("_nocoopt" if args.no_coopt else "")
            C.result(f"{tag}.multi_start_entries", len(log), "count")
            for i, (path, ncand, t) in enumerate(log):
                C.result(f"{tag}.entry{i}.path", path)
                C.result(f"{tag}.entry{i}.candidates", ncand, "count")
                C.result(f"{tag}.entry{i}.share_of_solve", round(t / solve, 4), "ratio")
            C.result(f"{tag}.coopt_resolve_adopted", state["co"])
            co_share = sum(t for p, _, t in log if p == "co_optimize") / solve
            if state["co"] is False:
                wasted.append(co_share)
            C.result(f"{tag}.solve_thread_ms", round(solve * 1000, 1), "ms (provisional)")
    finally:
        opt_mod._multi_start_minimize = o_msm
        HeatPumpOptimizer._co_optimize = o_co
    C.result("cells_with_rejected_resolve", len(wasted), "count")
    if wasted:
        C.result("rejected_resolve_share_mean", round(sum(wasted) / len(wasted), 4), "ratio")
    C.trailer(tf)


if __name__ == "__main__":
    main()
