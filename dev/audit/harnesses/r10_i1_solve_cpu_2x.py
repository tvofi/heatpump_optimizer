"""R10 D9-s3-01, the sweep side: does the whole-solve CPU channel see an
exact 2x of HeatPumpOptimizer.optimize that moves no count and no kernel
second, and does an unchanged tree stay quiet?

Metric: the baseline half is captured exactly as the sweep captures it
(stress.capture_baseline_work: a pristine worktree of ``ref``, the shared
WORK_PROBE_DRIVER, a child process); this tree then solves the same
scenarios in process, a reference sample before each as the sweep takes
one, with every optimize() call's CPU scaled by ``--factor``
(stress.cpu_scaler, the finder's injection). The production statistic
(stress.solve_cpu_median over work_drift_compare's covered set) and verdict
(stress.solve_cpu_over_verdict) judge it. RESULT flagged is 1 when the
verdict fires.

Null: --factor 1.0 (flagged 0). Perturbation: --factor 2.0 (flagged 1).
Labels: every sweep scenario, or the first N with --first N.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_i1_solve_cpu_2x.py \\
        [--factor 2.0] [--ref origin/main] [--first N]

Timing figures are machine readings: quote them with the command, the
factor and the load1 line beside them.
"""
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse
import sys
import time

ROOT = str(repo_root(__file__))
os.chdir(ROOT)
for _part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(ROOT, _part))
_argv, sys.argv = sys.argv, sys.argv[:1]
import stress  # noqa: E402  (import runs no sweep)
sys.argv = _argv
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--factor", type=float, default=2.0)
ap.add_argument("--ref", default=os.environ.get("GOLDEN_REF") or "origin/main")
ap.add_argument("--first", type=int, default=0)
a = ap.parse_args()

combos = stress.sweep_combinations()
if a.first:
    combos = combos[: a.first]
labels = [c["label"] for c in combos]
t0 = time.perf_counter()
baseline, note = stress.capture_baseline_work(ROOT, a.ref, labels)
if baseline is None:
    sys.exit(f"no baseline: {note}")
print(f"baseline: {note} in {time.perf_counter() - t0:.0f} s")

cal = stress.Calibration(stress.CALIBRATION_WINDOW)
cal.warm_up()
original = HeatPumpOptimizer.optimize
evals, simulate, objective, kernel, solve_ms = {}, {}, {}, {}, {}
for combo in combos:
    spec = {k: v for k, v in combo.items() if k != "label"}
    cal.sample()
    if a.factor != 1.0:
        HeatPumpOptimizer.optimize = stress.cpu_scaler(a.factor)(original)
    try:
        run = stress.build_case(**spec)
    finally:
        HeatPumpOptimizer.optimize = original
    label = combo["label"]
    evals[label] = int(run["solver_evals"])
    simulate[label] = int(run.get("solver_simulate_steps", 0))
    objective[label] = float(run["result"].objective_value)
    kernel[label] = float(run.get("solver_kernel_ms", 0.0))
    solve_ms[label] = float(run["solve_cpu_ms"])

drift = stress.work_drift_compare(evals, simulate, objective, kernel, baseline)
median, judged = stress.solve_cpu_median(
    solve_ms, evals, simulate, baseline, drift.covered
)
for label in drift.covered:
    base = baseline[label]
    print(f"  {label:28s} solve x{solve_ms[label] / base['solve_cpu_ms']:.2f} "
          f"kernel x{kernel[label] / base['kernel_ms']:.2f} "
          f"evals {evals[label]}/{base['evals']}")
flagged = int(median is not None and stress.solve_cpu_over_verdict(median))
print(f"RESULT flagged={flagged}")
print(f"RESULT median_solve_cpu_ratio={median if median is None else round(median, 3)}")
print(f"RESULT factor={stress.SWEEP_SOLVE_CPU_FACTOR:.4f}")
print(f"RESULT judged={judged} of {len(labels)}")
print(f"RESULT count_or_kernel_fired={len(drift.over) + len(drift.sim_over) + len(drift.cost_over)}")
print(f"RESULT injected_factor={a.factor}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
