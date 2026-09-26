"""V2 (independent) check of D9-s2-03: the smallest CPU-only multiplier on
ONE scenario that any tests/stress.py CPU rule can see, per scenario.

Metric A (own definition), from one clean sweep of stress.sweep_combinations()
timed with the gate's own stress.Calibration ruler: for each scenario s,
  k_s = min( scenario_budget(s)/ratio_s,                     per-scenario rule
             live_solve_budget_ratio()/ratio_s,               ceiling rule
             1 + (SWEEP_BUDGET_RATIO*sum_ref - sum_cpu)/cpu_s ) sweep rule
the factor by which scenario s alone must grow in solve CPU before a CPU rule
trips. Extra work outside the three metered simulate seams moves none of the
count/kernel channels by construction (SolverWork meters only the seams), so
k_s is the whole detection threshold for such work. Reported: the number of
scenarios with k_s > 2.0, min/median/max of k_s, leave-one-out.
Metric B: one production-located injection on one victim (winter/2z/dhw):
HeatPumpOptimizer._comfort_terms_batch (objective assembly, outside the
simulate seams) evaluated --repeat times per call, returning the production
value; victim solve CPU over its clean solve (interleaved), the counts and
kernel channels judged with stress.work_drift_compare against the clean
solve, and the victim's k_s. Plan sha compared.
Count key: the gate's own verdict functions over build_case's own figures.

Command (repo root; takes the gate lease as stress.py does):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tests/gate_lock.py \
    auto-lease --label g3v2-d9 -- /home/claude/venv/bin/python \
    tools/audit/round9/D9/verify-v2/v2_stress_headroom.py [--repeat 4]
Perturbation: --repeat raises the victim's CPU without moving a count; the
victim trips only once its cpu_x exceeds its k_s.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import hashlib
import statistics

import numpy as np

import stress
from heatpump_optimizer.optimizer import HeatPumpOptimizer

PROD = HeatPumpOptimizer._comfort_terms_batch
TABLE = stress.load_budget_table()


def row(run, unit):
    return {"cpu": float(run["solve_cpu_ms"]), "unit": unit, "ratio": float(run["solve_cpu_ms"]) / unit,
            "evals": int(run["solver_evals"]), "sim": int(run["solver_simulate_steps"]),
            "kernel": float(run["solver_kernel_ms"]), "obj": float(run["result"].objective_value),
            "sha": hashlib.sha1(np.asarray(run["result"].power_schedule, float).tobytes()).hexdigest()[:16]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=4)
    ap.add_argument("--victim", default="winter/2z/dhw")
    args = ap.parse_args()
    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
    cal.warm_up()
    rows, sref, scpu, specs = {}, 0.0, 0.0, {}
    for combo in [dict(c) for c in stress.sweep_combinations()]:
        name = combo.pop("label")
        specs[name] = combo
        sample = cal.sample()
        unit = max(cal.unit_ms, 1e-6)
        rows[name] = row(stress.build_case(**combo), unit)
        sref += sample
        scpu += rows[name]["cpu"]
    ks = {}
    for n, r in rows.items():
        b = stress.scenario_budget(n, TABLE)
        cands = [stress.live_solve_budget_ratio() / r["ratio"],
                 1 + (stress.SWEEP_BUDGET_RATIO * sref - scpu) / r["cpu"]]
        if b is not None:
            cands.append(b / r["ratio"])
        ks[n] = min(cands)
    vals = sorted(ks.values())
    V.result("scenarios", len(vals), "count")
    V.result("sweep_ratio", round(scpu / sref, 3), "ratio")
    V.result("sweep_budget", stress.SWEEP_BUDGET_RATIO, "ratio")
    V.result("k_over_2_count", sum(1 for v in vals if v > 2.0), f"of {len(vals)} (scenarios whose lone 2x CPU trips no CPU rule)")
    V.result("k_min", round(vals[0], 3), "x")
    V.result("k_min_label", min(ks, key=ks.get))
    V.result("k_median", round(statistics.median(vals), 3), "x")
    V.result("k_max", round(vals[-1], 3), "x")
    V.result("k_min_drop_lowest", round(vals[1], 3), "x (leave-one-out)")
    V.result("sweep_rule_k_min", round(min(1 + (stress.SWEEP_BUDGET_RATIO * sref - scpu) / r["cpu"]
                                           for r in rows.values()), 3), "x")
    # Metric B: production-located non-kernel injection on the victim.
    v = args.victim
    unit = rows[v]["unit"]

    def slow(self, *a, **k):
        out = None
        for _ in range(args.repeat):
            out = PROD(self, *a, **k)
        return out
    clean, inj = [], []
    for _ in range(2):
        clean.append(row(stress.build_case(**specs[v]), unit))
        HeatPumpOptimizer._comfort_terms_batch = slow
        try:
            inj.append(row(stress.build_case(**specs[v]), unit))
        finally:
            HeatPumpOptimizer._comfort_terms_batch = PROD
    c = min(clean, key=lambda r: r["cpu"]); i = min(inj, key=lambda r: r["cpu"])
    cpu_x = statistics.median(r["cpu"] for r in inj) / statistics.median(r["cpu"] for r in clean)
    base = {v: {"evals": c["evals"], "simulate": c["sim"], "objective": c["obj"], "kernel_ms": c["kernel"]}}
    d = stress.work_drift_compare({v: i["evals"]}, {v: i["sim"]}, {v: i["obj"]}, {v: i["kernel"]}, base)
    V.result(f"victim[{v}].repeat", args.repeat, "x _comfort_terms_batch")
    V.result(f"victim[{v}].cpu_x", round(cpu_x, 3), "ratio (provisional)")
    V.result(f"victim[{v}].k", round(ks[v], 3), "x")
    V.result(f"victim[{v}].cpu_rule_trips", int(cpu_x > ks[v]), "bool")
    V.result(f"victim[{v}].evals_x", round(i["evals"] / c["evals"], 4), "ratio")
    V.result(f"victim[{v}].sim_x", round(i["sim"] / c["sim"], 4), "ratio")
    V.result(f"victim[{v}].kernel_x", round(i["kernel"] / c["kernel"], 3), "ratio")
    V.result(f"victim[{v}].work_rules_tripped", len(d.over) + len(d.sim_over) + len(d.cost_over), "count")
    V.result(f"victim[{v}].plan_sha_equal", int(c["sha"] == i["sha"]), "bool")
    # The same edit on disk is not confined to one label: every two-zone
    # scenario runs the two-zone branch. Scale each two-zone row by the
    # victim's measured cpu_x and re-judge the CPU rules over the sweep.
    tz = [n for n, sp in specs.items() if sp.get("two_zone")]
    scpu2 = scpu + sum(rows[n]["cpu"] * (cpu_x - 1) for n in tz)
    per2 = sum(1 for n in tz if (b := stress.scenario_budget(n, TABLE)) is not None
               and rows[n]["ratio"] * cpu_x > b)
    V.result("two_zone_scenarios", len(tz), "count")
    V.result("two_zone_share_of_sweep_cpu", round(sum(rows[n]["cpu"] for n in tz) / scpu, 4), "ratio")
    V.result("all_two_zone_scaled.sweep_ratio", round(scpu2 / sref, 3), "ratio")
    V.result("all_two_zone_scaled.sweep_trips", int(scpu2 / sref > stress.SWEEP_BUDGET_RATIO), "bool")
    V.result("all_two_zone_scaled.per_scenario_trips", per2, "count")
    V.result("clean_vs_clean_spread", round(max(r["cpu"] for r in clean) / min(r["cpu"] for r in clean) - 1, 4), "ratio")
    V.trailer()


if __name__ == "__main__":
    main()
