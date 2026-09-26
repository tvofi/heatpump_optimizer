"""V2 (independent) check of D9-s2-03, topology-confined shape: does
tests/stress.py see a ~2x of every SINGLE-ZONE scenario's solve CPU when the
extra work sits outside the metered simulate seams?

Mutation (in memory, production-located): HeatPumpOptimizer._comfort_terms_batch
evaluated --repeat times per call when the model is single-zone (the shape of a
one-line edit to its single-zone loop: `for _rep in range(R):` around it),
returning the production value, so counts, kernel per-call cost and plans are
unchanged by construction. Two full sweeps of stress.sweep_combinations() in
one process, timed with the gate's stress.Calibration: plain, then mutated.
Metric (own definition): number of stress.py rules tripped for the mutated
sweep, judged with the gate's own functions (live_solve_budget_ratio,
scenario_budget, SWEEP_BUDGET_RATIO, work_drift_compare against the plain
sweep of the same process); plus the single-zone scenarios' cpu_x range and
the sweep ratio over plain.
Count key: the gate's own verdict functions over build_case's own figures.

Command (repo root, under the gate lease):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tests/gate_lock.py \
    auto-lease --label g3v2-d9 -- /home/claude/venv/bin/python \
    tools/audit/round9/D9/verify-v2/v2_stress_1z_mutation.py [--repeat 10]
Perturbation: --repeat (single-zone cpu_x rises with it; tripped rules only
move once cpu_x passes each scenario's per-scenario budget, ~2.9-4x).
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import statistics

import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PROD = HeatPumpOptimizer._comfort_terms_batch
TABLE = stress.load_budget_table()
R = {"n": 1}


def mutated(self, *a, **k):
    reps = 1 if self.model.params.two_zone_enabled else R["n"]
    out = None
    for _ in range(reps):
        out = PROD(self, *a, **k)
    return out


def sweep():
    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
    cal.warm_up()
    rows, sref, scpu = {}, 0.0, 0.0
    for combo in [dict(c) for c in stress.sweep_combinations()]:
        name = combo.pop("label")
        s = cal.sample()
        unit = max(cal.unit_ms, 1e-6)
        run = stress.build_case(**combo)
        cpu = float(run["solve_cpu_ms"])
        rows[name] = {"ratio": cpu / unit, "cpu": cpu, "unit": unit, "2z": bool(combo.get("two_zone")),
                      "evals": int(run["solver_evals"]), "sim": int(run["solver_simulate_steps"]),
                      "kernel": float(run["solver_kernel_ms"]),
                      "obj": float(run["result"].objective_value)}
        sref += s
        scpu += cpu
    return rows, scpu / sref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=10)
    args = ap.parse_args()
    plain, sr0 = sweep()
    R["n"] = args.repeat
    HeatPumpOptimizer._comfort_terms_batch = mutated
    try:
        mut, sr1 = sweep()
    finally:
        HeatPumpOptimizer._comfort_terms_batch = PROD
    ceiling = sum(1 for r in mut.values() if r["cpu"] > stress.live_solve_budget_ratio() * r["unit"])
    per = sum(1 for n, r in mut.items()
              if (b := stress.scenario_budget(n, TABLE)) is not None and r["ratio"] > b)
    sw = int(sr1 > stress.SWEEP_BUDGET_RATIO)
    d = stress.work_drift_compare(
        {n: r["evals"] for n, r in mut.items()}, {n: r["sim"] for n, r in mut.items()},
        {n: r["obj"] for n, r in mut.items()}, {n: r["kernel"] for n, r in mut.items()},
        {n: {"evals": r["evals"], "simulate": r["sim"], "objective": r["obj"], "kernel_ms": r["kernel"]}
         for n, r in plain.items()})
    work = len(d.over) + len(d.sim_over) + len(d.cost_over)
    one = [n for n, r in plain.items() if not r["2z"]]
    xs = sorted(mut[n]["cpu"] / plain[n]["cpu"] for n in one)
    V.result("single_zone_scenarios", len(one), "count")
    V.result("single_zone_share_of_plain_sweep_cpu", round(sum(plain[n]["cpu"] for n in one) / sum(r["cpu"] for r in plain.values()), 4), "ratio")
    V.result("repeat", args.repeat, "x single-zone _comfort_terms_batch")
    V.result("single_zone_cpu_x_min", round(xs[0], 3), "ratio (provisional)")
    V.result("single_zone_cpu_x_median", round(statistics.median(xs), 3), "ratio (provisional)")
    V.result("single_zone_cpu_x_max", round(xs[-1], 3), "ratio (provisional)")
    V.result("single_zone_cpu_x_drop_max", round(xs[-2], 3), "ratio (leave-one-out)")
    V.result("sweep_ratio_plain", round(sr0, 3), "ratio")
    V.result("sweep_ratio_mutated", round(sr1, 3), "ratio")
    V.result("sweep_budget", stress.SWEEP_BUDGET_RATIO, "ratio")
    V.result("tripped_ceiling", ceiling, "count")
    V.result("tripped_per_scenario", per, "count")
    V.result("tripped_sweep", sw, "count")
    V.result("tripped_work_channels", work, "count")
    V.result("tripped_total", ceiling + per + sw + work, "count (exact)")
    two = [n for n, r in plain.items() if r["2z"]]
    V.result("null_two_zone_cpu_x_median", round(statistics.median(mut[n]["cpu"] / plain[n]["cpu"] for n in two), 3), "ratio (unmutated rows)")
    V.trailer()


if __name__ == "__main__":
    main()
