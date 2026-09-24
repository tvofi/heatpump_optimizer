"""Round-5 D9-07, the sweep side: does the per-scenario kernel rule see a
real 2x of per-call kernel cost, and does an unchanged tree stay green?

Metric, per trial, on the probe scenario (sweep_combinations()[0]), which is
the scenario the per-call-cost arm in tests/stress.py also uses:

  * BEFORE -- the rule as origin/main applied it: one baseline reading from
    the capture driver with its seam wrappers inside the tree's own meter
    (the pre-fix driver, rebuilt here by deleting the guard that now keeps
    them out), one reading of this tree, work_drift_compare.
  * AFTER -- the rule as the sweep now applies it: one baseline reading from
    the current driver, one reading of this tree, stress.judge_work -- which
    re-solves a scenario in the kernel doubt band on both trees and judges
    the medians.

INJECTED trials run this tree with every kernel seam call's CPU doubled
(stress.cpu_scaler(2.0), the arm's own injection) -- a miss is a trial where
cost_over stayed empty. CLEAN trials run it unchanged -- a false fire is a
trial where cost_over was not empty, and the RESULT line also counts how
often the doubt band sent a clean tree to a re-solve and what that cost.
BAND trials force the re-solve on a real 2x: this tree doubled, its single
reading replaced by 1.6x of the baseline's (inside the band), so every trial
measures the median-of-KERNEL_DOUBT_ROUNDS confirmation itself -- a miss is
a trial the medians did not carry over the factor.

Run from the repository root, against a baseline ref that is not HEAD:

    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/d907_kernel_band.py \\
        [trials] [ref]

Force the contended condition by starting load beside it first; the PR that
added this names the command it used.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
os.chdir(ROOT)
for _part in ("custom_components", os.path.join("tests", "hastub"), "tests"):
    sys.path.insert(0, os.path.join(ROOT, _part))

import stress  # noqa: E402

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 20
REF = sys.argv[2] if len(sys.argv) > 2 else stress.WORK_DRIFT_REF
_GUARD = "not _tree_meters_kernel and "
assert stress.WORK_PROBE_DRIVER.count(_GUARD) == 2, "the driver guard moved"
OLD_DRIVER = stress.WORK_PROBE_DRIVER.replace(_GUARD, "")
NEW_DRIVER = stress.WORK_PROBE_DRIVER

probe = dict(stress.sweep_combinations()[0])
label = probe.pop("label")
W, TM = stress.SolverWork, stress.ThermalModel
SAVED = (W._batch_wrapped, W._step_wrapped)


def seams(doubled: bool) -> None:
    if doubled:
        twice = stress.cpu_scaler(2.0)
        W._batch_wrapped, W._step_wrapped = twice(SAVED[0]), twice(SAVED[1])
    else:
        W._batch_wrapped, W._step_wrapped = SAVED
        TM.simulate_trajectory_batch, TM.simulate_step = SAVED


def baseline_row(worktree: str, tmp: str, driver: str) -> dict:
    stress.WORK_PROBE_DRIVER = driver
    try:
        rows, note = stress.capture_work_rows(
            worktree, os.path.join(tmp, "row.json"), [label]
        )
    finally:
        stress.WORK_PROBE_DRIVER = NEW_DRIVER
    if rows is None or label not in rows:
        raise SystemExit(f"RESULT error: baseline capture failed -- {note}")
    return rows


def trial(worktree: str, tmp: str, doubled: bool, band: bool = False) -> tuple:
    old_base = baseline_row(worktree, tmp, OLD_DRIVER)
    new_base = baseline_row(worktree, tmp, NEW_DRIVER)
    seams(doubled)
    try:
        run = stress.build_case(**dict(probe))
        obs = (
            {label: int(run["solver_evals"])},
            {label: int(run.get("solver_simulate_steps", 0))},
            {label: float(run["result"].objective_value)},
            {label: float(run.get("solver_kernel_ms", 0.0))},
        )
        if band:
            obs = obs[:3] + ({label: 1.6 * new_base[label]["kernel_ms"]},)
        before = stress.work_drift_compare(*obs, old_base)
        started = time.perf_counter()
        after, ok, note = stress.judge_work(
            *obs, new_base, ROOT, REF, {label: probe}
        )
        spent = time.perf_counter() - started
    finally:
        seams(False)
    here = obs[3][label]
    return (
        bool(before.cost_over), bool(after.cost_over), ok,
        bool(after.cost_doubt) or "re-solved" in note, spent,
        here / old_base[label]["kernel_ms"], here / new_base[label]["kernel_ms"],
    )


with stress.baseline_worktree(ROOT, REF) as (worktree, tmp, where):
    if worktree is None:
        raise SystemExit(f"RESULT error: {where}")
    band = []
    for n in range(TRIALS):
        r = trial(worktree, tmp, True, band=True)
        band.append(r)
        print(f"band {n}: after fired={r[1]} {r[4]:.1f} s ok={r[2]}", flush=True)
    print(f"RESULT band {label} vs {where}: a real 2x forced into the doubt "
          f"band was confirmed {sum(r[1] for r in band)}/{TRIALS} at "
          f"{stress.KERNEL_DOUBT_ROUNDS} rounds; re-measure failures "
          f"{sum(not r[2] for r in band)}; mean re-solve "
          f"{sum(r[4] for r in band) / TRIALS:.1f} s")
    for doubled in (True, False):
        arm = "injected" if doubled else "clean"
        results = []
        for n in range(TRIALS):
            r = trial(worktree, tmp, doubled)
            results.append(r)
            print(f"{arm} {n}: before fired={r[0]} x{r[5]:.3f} | after "
                  f"fired={r[1]} x{r[6]:.3f} re-solved={r[3]} "
                  f"{r[4]:.1f} s ok={r[2]}", flush=True)
        fails = sum(not r[2] for r in results)
        resolved = [r for r in results if r[3]]
        cost = sum(r[4] for r in resolved)
        if doubled:
            print(f"RESULT injected {label} vs {where}: before missed "
                  f"{sum(not r[0] for r in results)}/{TRIALS} (min single "
                  f"x{min(r[5] for r in results):.3f}), after missed "
                  f"{sum(not r[1] for r in results)}/{TRIALS} (min single "
                  f"x{min(r[6] for r in results):.3f}); re-solved "
                  f"{len(resolved)}/{TRIALS}; re-measure failures {fails}")
        else:
            print(f"RESULT clean {label} vs {where}: before fired "
                  f"{sum(r[0] for r in results)}/{TRIALS} (max single "
                  f"x{max(r[5] for r in results):.3f}), after fired "
                  f"{sum(r[1] for r in results)}/{TRIALS} (max single "
                  f"x{max(r[6] for r in results):.3f}); re-solved "
                  f"{len(resolved)}/{TRIALS} costing {cost:.1f} s in all; "
                  f"re-measure failures {fails}")
