"""D9 verify-v3 (round 9, lens V3) for D9-s2-03: how many of the 51 sweep
scenarios could have a solve-CPU regression of 2x, confined to that scenario
and outside the metered simulate seams (counts unchanged), turn any CPU rule of
tests/stress.py red -- judged with the gate's OWN recorded table and constants.

Metric (one line): per scenario i with recorded ratio r_i (stress.load_budget_table),
trips_i = [2 r_i > scenario_budget(i)] or [mean(r) + r_i/N > SWEEP_BUDGET_RATIO]
or [2 r_i > live_solve_budget_ratio()]; reported as the count of scenarios with
trips_i true, plus the smallest confined multiple that trips any CPU rule per
scenario (min over scenarios, and for winter/2z/dhw). The count channels
(evaluations, simulate steps) are 1.00x by the finding's construction.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s2_03_budget.py [--machine-scale 1.0]
Instrumented symbols: tests/stress.py:scenario_budget, load_budget_table,
SWEEP_BUDGET_RATIO, live_solve_budget_ratio (called, not re-implemented).
Perturbation: --machine-scale 1.02 (a runner reading every ratio 2% above record
-> scenarios tripping at 2x go UP via the sweep rule, whose record
headroom is 3.3%; at 1.6 every scenario is red at 1.0x, a degenerate arm).
Expected at scale 1.0: 9 of 51 (exact given the committed table), all via the sweep rule;
at 1.02: 21 of 51.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine printed.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse
import stress


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--machine-scale", type=float, default=1.0)
    a = ap.parse_args()
    s = a.machine_scale
    table = stress.load_budget_table()
    rec = {k: float(v["ratio"]) for k, v in table.items() if isinstance(v, dict) and float(v.get("ratio", 0)) > 0}
    N = len(rec); mean = sum(rec.values()) / N
    ceil = stress.live_solve_budget_ratio()
    trips = 0; kmin = {}
    for lab, r in rec.items():
        budget = stress.scenario_budget(lab, table)
        def tripped(k):
            return (k * r * s > budget) or ((mean * s) + (k - 1) * r * s / N > stress.SWEEP_BUDGET_RATIO) or (k * r * s > ceil)
        trips += tripped(2.0)
        k = 1.0
        while k < 20 and not tripped(k):
            k = round(k + 0.01, 2)
        kmin[lab] = k
    tag = "" if s == 1.0 else f"scale{s}_"
    V.R(f"{tag}recorded_scenarios", N, "count")
    V.R(f"{tag}recorded_mean_ratio", round(mean, 2), "x ref")
    V.R(f"{tag}sweep_budget_ratio", stress.SWEEP_BUDGET_RATIO)
    V.R(f"{tag}solve_ceiling_ratio", round(ceil, 2))
    V.R(f"{tag}scenario_budget_factor", stress.SCENARIO_BUDGET_FACTOR)
    V.R(f"{tag}confined_2x_scenarios_tripping_any_cpu_rule", trips, f"of {N} (exact)")
    lo = min(kmin, key=kmin.get)
    V.R(f"{tag}min_confined_multiple_to_trip", kmin[lo], f"x ({lo})")
    for lab in ("winter/2z/dhw", "winter/1z/dhw"):
        if lab in kmin:
            V.R(f"{tag}confined_multiple_to_trip.{lab}", kmin[lab], "x")
    V.trailer()


if __name__ == "__main__":
    main()
