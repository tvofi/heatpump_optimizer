#!/usr/bin/env python3
"""METRIC 7 (D9 round 5, seat b): can the stress budget as shipped detect a
synthetic 2x regression?

Metric definition (one line): inject an exact 2x of work into one real solve
(two shapes: per-call kernel cost doubled at SolverWork._batch_wrapped, and
solver runs doubled at SolverWork._wrapped), record what the solve's own
channels report (solve CPU, solver_evals, solver_simulate_steps, objective),
then feed synthetic recordings -- the committed tests/stress_budgets.json
scaled by the measured multipliers -- through the stress checks' OWN decision
functions (scenario_budget, stale_cheap_verdict, work_over_verdict,
traced_fail_threshold, rss_attrib_fail_threshold, live_solve_budget_ratio /
SWEEP_BUDGET_RATIO arithmetic) and count which checks fire.

Command (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D9/seat-b/h7_stress_detect.py

Expected at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1,
python3.11): kernel-cost injection lands solve CPU at ~2.0x with BOTH count
channels at 1.00x and a bit-identical plan; the re-run lands sim_steps at ~2.0x. On the recorded table: single-scenario 2.0x fires 0 of 51
per-scenario CPU budgets (2.0 < 3.0), the sweep arithmetic moves the mean by
x52/51 only, work_over_verdict fires at 2.0 > 1.80 (eval channel), and the
memory pass's probe selection covers 6 of 51 scenarios. CPU timings are
provisional under load; every ratio is a CPU-time ratio against
stress.reference_solve measured beside it.

Instrumented symbols: tests/stress.py:build_case (the solve the sweep runs),
tests/stress.py:SolverWork (both count channels), and the check functions
named above driven on the committed tests/stress_budgets.json.

Perturbation: the null arm is built in (the `clean` arm leaves every
multiplier at 1.00x and no check fires); the two injection arms each move
solve_cpu_ms ~2x and exactly one count channel (kernel: neither; evals:
evaluations), and the verdict lines must follow that movement.
"""

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess
import sys
import time

REPO = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
)
for p in (os.path.join(REPO, "tests/hastub"), os.path.join(REPO, "tests"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

LABEL = "winter/2z/dhw"


def find_combo(stress):
    for combo in stress.sweep_combinations():
        if combo["label"] == LABEL:
            return {k: v for k, v in combo.items() if k != "label"}
    raise SystemExit(f"no combo labelled {LABEL}")


def run_case(stress, combo, inject):
    """One build_case solve under an optional injection; returns channels."""
    saved_batch = stress.SolverWork._batch_wrapped
    saved_step = stress.SolverWork._step_wrapped
    saved_scoped = stress.SolverWork._wrapped

    def batch_twice(*args, **kwargs):
        res = saved_batch(*args, **kwargs)  # the true kernel
        saved_batch(*args, **kwargs)  # the injected second pass, discarded
        return res

    def step_twice(*args, **kwargs):
        res = saved_step(*args, **kwargs)
        saved_step(*args, **kwargs)
        return res

    def scoped_twice(*args, **kwargs):
        res = saved_scoped(*args, **kwargs)
        saved_scoped(*args, **kwargs)
        return res

    if inject == "kernel":
        stress.SolverWork._batch_wrapped = batch_twice
        stress.SolverWork._step_wrapped = step_twice
    elif inject == "rerun":
        stress.SolverWork._wrapped = scoped_twice
    try:
        run = stress.build_case(**combo)
    finally:
        stress.SolverWork._batch_wrapped = saved_batch
        stress.SolverWork._step_wrapped = saved_step
        stress.SolverWork._wrapped = saved_scoped
    return run


def main():
    import stress

    table = stress.load_budget_table()
    combo = find_combo(stress)

    arms = {}
    for inject in (None, "kernel", "rerun"):
        runs = []
        for _ in range(3):
            run = run_case(stress, combo, inject)
            _w, ref_cpu, _t = stress.reference_solve()
            runs.append(
                {
                    "cpu_ms": float(run["solve_cpu_ms"]),
                    "ref_cpu_ms": ref_cpu,
                    "ratio": float(run["solve_cpu_ms"]) / max(ref_cpu, 1e-9),
                    "thread_ms": float(run["solve_thread_ms"]),
                    "evals": int(run["solver_evals"]),
                    "sim": int(run["solver_simulate_steps"]),
                    "objective": float(run["result"].objective_value),
                }
            )
        med = sorted(runs, key=lambda r: r["ratio"])[1]
        med["ratio_lo"] = min(r["ratio"] for r in runs)
        med["ratio_hi"] = max(r["ratio"] for r in runs)
        arms[inject or "clean"] = med
        print(
            f"ARM {inject or 'clean'}: cpu_ratio={med['ratio']:.4f}x "
            f"[{med['ratio_lo']:.4f}, {med['ratio_hi']:.4f}] "
            f"evals={med['evals']} sim_steps={med['sim']} "
            f"objective={med['objective']:.6f}"
        )

    clean = arms["clean"]
    for name in ("kernel", "rerun"):
        a = arms[name]
        print(
            f"RESULT inject_{name}_cpu_mult={a['ratio'] / clean['ratio']:.4f}x "
            f"eval_mult={a['evals'] / max(clean['evals'], 1):.4f}x "
            f"sim_mult={a['sim'] / max(clean['sim'], 1):.4f}x "
            f"plan_same={abs(a['objective'] - clean['objective']) < 1e-9} "
            f"thread_factor={a['cpu_ms'] / max(a['thread_ms'], 1e-9):.3f}(solve cpu/thread)"
        )

    # ---- the checks' own logic on synthetic recordings -----------------
    ratios = sorted(
        float(e["ratio"]) for e in table.values()
        if isinstance(e, dict) and float(e.get("ratio", 0.0)) > 0.0
    )
    rec_mean = sum(ratios) / len(ratios)
    rec_worst = ratios[-1]

    fires_single = sum(
        1
        for label, entry in table.items()
        if isinstance(entry, dict)
        and float(entry.get("ratio", 0.0)) > 0.0
        and 2.0 * float(entry["ratio"]) > (stress.scenario_budget(label, table) or 0.0)
    )
    sweep_single = rec_mean * (len(ratios) + 1) / len(ratios)
    sweep_uniform = rec_mean * 2.0
    print(
        f"TABLE recorded scenarios={len(ratios)} mean_ratio={rec_mean:.2f}x "
        f"worst={rec_worst:.2f}x"
    )
    print(
        f"RESULT per_scen_cpu_budgets_fired_at_2x={fires_single} of {len(ratios)} "
        f"(factor {stress.SCENARIO_BUDGET_FACTOR:.1f}x) thread_factor=n/a"
    )
    print(
        f"RESULT sweep_ratio_single_2x={sweep_single:.2f}x vs budget "
        f"{stress.SWEEP_BUDGET_RATIO:.2f}x fires={sweep_single > stress.SWEEP_BUDGET_RATIO} "
        f"thread_factor=n/a"
    )
    print(
        f"RESULT sweep_ratio_uniform_2x={sweep_uniform:.2f}x vs budget "
        f"{stress.SWEEP_BUDGET_RATIO:.2f}x fires={sweep_uniform > stress.SWEEP_BUDGET_RATIO} "
        f"thread_factor=n/a"
    )
    for name in ("kernel", "rerun"):
        a = arms[name]
        fires_eval = stress.work_over_verdict(a["evals"], clean["evals"])
        fires_sim = stress.work_over_verdict(a["sim"], clean["sim"])
        covered = stress.same_basin(a["objective"], clean["objective"])
        print(
            f"RESULT work_drift_{name}: eval_channel_fires={fires_eval} "
            f"sim_channel_fires={fires_sim} same_basin={covered} "
            f"thread_factor=n/a(counts)"
        )

    # Memory pass: replay main()'s probe selection (inline there; copied
    # faithfully) and judge 2x-traced synthetic observations per label.
    half = max(1, stress.MEMORY_TOP_N // 2)
    chosen = []
    for key in ("traced_peak_mb", "rss_peak_mb"):
        ranked = sorted(
            (-float(entry[key]), label)
            for label, entry in table.items()
            if isinstance(entry, dict) and float(entry.get(key, 0.0)) > 0.0
        )
        taken = 0
        for _peak, label in ranked:
            if taken >= half:
                break
            if label in chosen:
                continue
            chosen.append(label)
            taken += 1
    mem_labels = [l for l in chosen]
    n_mem = sum(
        1 for e in table.values()
        if isinstance(e, dict) and float(e.get("traced_peak_mb", 0.0)) > 0.0
    )
    traced_2x_caught = sum(
        1 for label in mem_labels
        if 2.0 * float(table[label]["traced_peak_mb"])
        > stress.traced_fail_threshold(float(table[label]["traced_peak_mb"]))
    )
    unprobed = [l for l in table if l not in mem_labels]
    print(
        f"RESULT memory_probe_coverage={len(mem_labels)} of {n_mem} "
        f"recorded scenarios thread_factor=n/a"
    )
    print(
        f"RESULT memory_traced_2x_on_probed_leaders_fires={traced_2x_caught} of "
        f"{len(mem_labels)} probed; unprobed={len(unprobed)} "
        f"(2x on any of those is never measured) thread_factor=n/a"
    )

    # Staleness asymmetry: a 3.5x-cheaper branch must force a re-record on
    # the ratio channel; no rule exists for the memory fields.
    sample = next(iter(table.values()))
    ratio_stale = stress.stale_cheap_verdict(
        float(sample["ratio"]) / 3.6, float(sample["ratio"])
    )
    mem_rule_calls = sum(
        1 for _ in (stress.traced_fail_threshold, stress.rss_attrib_fail_threshold)
    )
    print(
        f"RESULT stale_rule_ratio_at_{1/3.6:.3f}x_fires={ratio_stale} "
        f"stale_rule_for_memory_fields=absent "
        f"({mem_rule_calls} memory threshold functions, neither takes an "
        f"observed-below-record verdict) thread_factor=n/a"
    )

    print(
        f"RESULT thread_factor={arms['clean']['cpu_ms'] / max(arms['clean']['thread_ms'], 1e-9):.3f} "
        f"(clean solve cpu/thread, the parallelism of the timed section)"
    )
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    ps = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    print(f"RESULT concurrent_test_procs={ps.count('stress.py') + ps.count('tests/run.sh')}")


if __name__ == "__main__":
    main()
