"""D9 verify-v3 (round 9, lens V3) for D9-s2-03, verifier.md step 4: a
single-line PRODUCTION mutation of the finding's class, measured on the victim.

Mutation (in memory, never on disk): optimizer.py HeatPumpOptimizer.
_comfort_terms_batch's row loop `for b in range(n_rows):` run 4 times over
(each pass rewrites the same penalty[b]/comfort_cost[b], so values, plan and
every count are unchanged) -- emulated by calling the production method 4x and
returning the last result, which is what that one-line edit executes.
Metric (one line): solve thread CPU mutant / plain on stress.build_case
winter/2z/dhw (ABAB, median of 2 each), with stress.SolverWork's evaluation and
simulate step-equivalent counts for both arms, and the victim's per-scenario
budget headroom scenario_budget / live ratio.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s2_03_lineclass.py [--passes 4]
Perturbation: --passes 1 (the null control) -> ratio ~1.00.
Expected: ratio ~1.9-2.0 at 4 passes, counts equal (exact), headroom > ratio.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, hashlib, statistics
import numpy as np
import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PROD = HeatPumpOptimizer._comfort_terms_batch


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--passes", type=int, default=4)
    a = ap.parse_args()

    def mutant(self, *args):
        for _ in range(a.passes - 1):
            PROD(self, *args)
        return PROD(self, *args)
    spec = dict(season="winter", two_zone=True, dhw=True)
    ref = sorted(stress.reference_solve()[1] for _ in range(5))[2]

    def run(fn):
        HeatPumpOptimizer._comfort_terms_batch = fn
        try:
            r = stress.build_case(**spec)
        finally:
            HeatPumpOptimizer._comfort_terms_batch = PROD
        w = r.get("work") or {}
        sha = hashlib.sha1(np.asarray(r["result"].power_schedule, float).tobytes()).hexdigest()[:16]
        return r["solve_thread_ms"], sha, {k: r.get(k) for k in ("solver_calls", "solver_evals", "solver_simulate_steps")}
    P, M = [], []
    for _ in range(2):
        t, sp, wp = run(PROD); P.append(t)
        t, sm, wm = run(mutant); M.append(t)
    ratio = statistics.median(M) / statistics.median(P)
    table = stress.load_budget_table()
    budget = stress.scenario_budget("winter/2z/dhw", table)
    live = statistics.median(P) / ref
    V.R(f"passes{a.passes}.solve_cpu_ratio_mutant_over_plain", round(ratio, 3), "ratio (provisional)")
    V.R(f"passes{a.passes}.plan_sha_equal", sp == sm)
    V.R(f"passes{a.passes}.work_plain", str(wp).replace(" ", ""))
    V.R(f"passes{a.passes}.work_mutant", str(wm).replace(" ", ""))
    V.R(f"passes{a.passes}.victim_live_ratio", round(live, 2), "x reference_solve")
    V.R(f"passes{a.passes}.per_scenario_headroom", round(budget / live, 3), "x (budget / live)")
    V.trailer()


if __name__ == "__main__":
    main()
