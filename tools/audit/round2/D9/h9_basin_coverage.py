"""D9 metric 9 (#387): does the solver-work check still cover the sweep on a
machine whose solver lands in basins no table has recorded?

Metric: the number of the fifty-one sweep scenarios the tree's own
solver-work rule JUDGES (as opposed to exempts), when the multi-start
cohort lands in a basin the committed table does not hold -- which is what
CI run 33841375106 observed, and what made main red. Reported as
`covered`, against the tree's own floor (`floor`), plus `fires`, 1 when the
tree's coverage check would fail.

The same observation set is put to whichever shape the tree under test
has, driving that tree's PRODUCTION symbols and never re-implementing the
arithmetic:

  * the recorded-fingerprint shape (#346, v6.3.11): stress.matching_basin()
    against the committed tests/stress_budgets.json, floor
    stress.SCENARIO_BASIN_MIN_COVERED;
  * the captured-baseline shape (#387): stress.work_drift_compare() against
    a baseline capture taken in the SAME environment, floor
    stress.SCENARIO_WORK_MIN_COVERED.

Both are given the identical event -- the 22 bimodal scenarios solved into
a third basin -- because the two shapes differ only in what they compare
that event against. The perturbation is applied to the OBJECTIVE, which is
exactly what a different CPU model and BLAS kernel do to a multi-start
solve; the size, 1e-3 relative, sits inside the 4.41e-5 to 2.24e-3 band of
the fifteen genuine basin changes executed for #346 and three orders above
same-basin float drift.

Section 2 stops simulating and moves the real hardware's decision: one
scenario is solved twice through the production symbol
`optimizer._price_guess_weights`, once normally and once from a different
legal start, so the solver genuinely lands in another local minimum. Each
shape is then asked the same question about that solve.

Command (from the repository root of the tree to measure, PYTHONPATH set):
    PYTHONPATH=tests/hastub python3 tools/audit/round2/D9/h9_basin_coverage.py

Expected: at the merge base b0703f7 (the v6.3.11 shape) covered=29 of 51
against floor=40, fires=1 -- the failure CI run 33841375106 reported
verbatim. After #387's fix covered=51, floor=40, fires=0, on the same
input. Tolerance: exact; these are counts, not timings.

Instrumented symbols: tests/stress.py:matching_basin /
tests/stress.py:work_drift_compare (the coverage rule itself),
tests/stress.py:SCENARIO_BASIN_MIN_COVERED / SCENARIO_WORK_MIN_COVERED
(the floor), optimizer:_price_guess_weights (the real basin move in
section 2).
Perturbation: the objective fingerprint of the 22 scenarios that carry an
`alt_basins` entry is moved by 1e-3 relative -- a third basin. Under it
`covered` must fall for a shape that compares against recorded numbers and
must NOT fall for one that compares two captures made in one environment.
Root rule: os.getcwd() -- copy this file into the tree to be measured and
run it from that tree's root. It never resolves anything from __file__.
Baseline SHA: b0703f7b7e0af96026e8272830b8ccd9a451803e.
Machine: 4-core Linux microVM (audit box).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402  (after the pin, deliberately)

import stress  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

#: The commit whose committed table defines "the recorded set". Read with
#: `git show`, so this harness measures the same recorded numbers whether
#: the tree under test still carries them or has removed them.
BASE = os.environ.get("H9_BASE", "b0703f7b7e0af96026e8272830b8ccd9a451803e")
#: Relative objective move that stands for "another local minimum".
FLIP = float(os.environ.get("H9_FLIP", "1e-3"))
#: The scenario section 2 solves for real.
VICTIM = os.environ.get("H9_VICTIM", "shoulder/cycle")


def result(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def concurrent() -> int:
    out = os.popen(
        "ps ax -o args= | grep -E '[s]tress\\.py|[t]ests/run\\.sh|[h]9_basin'"
    ).read().splitlines()
    return len(out)


def recorded_table() -> dict:
    """The fingerprint table as BASE committed it, whatever this tree holds."""
    proc = subprocess.run(
        ["git", "show", f"{BASE}:tests/stress_budgets.json"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"cannot read the recorded table: {proc.stderr[-200:]}")
    return json.loads(proc.stdout)


TABLE = recorded_table()
SHAPE = (
    "captured-baseline" if hasattr(stress, "work_drift_compare")
    else "recorded-fingerprint" if hasattr(stress, "matching_basin")
    else "none"
)
FLOOR = int(
    getattr(stress, "SCENARIO_WORK_MIN_COVERED", None)
    or getattr(stress, "SCENARIO_BASIN_MIN_COVERED")
)
result("shape", SHAPE, "name")
result("floor", FLOOR, "count")
result("scenarios", len(TABLE), "count")

# The cohort: exactly the scenarios the recorded table gave a second basin,
# which #387 measured to be exactly the 22 that flipped together on CI.
COHORT = sorted(k for k, v in TABLE.items() if v.get("alt_basins"))
result("cohort", len(COHORT), "count")


def observation(flip_cohort: bool) -> tuple[dict, dict]:
    """What a runner reports: (evals, objective) for all 51 scenarios.

    Unchanged production, so the evaluation counts are the recorded ones;
    only which basin the solver fell into differs, and only for the cohort.
    """
    evals, objective = {}, {}
    for label, row in TABLE.items():
        evals[label] = int(row["evals"])
        moved = flip_cohort and label in COHORT
        objective[label] = float(row["objective"]) * (1.0 + FLIP if moved else 1.0)
    return evals, objective


def covered(evals: dict, objective: dict) -> int:
    """How many scenarios this tree's rule JUDGES, on that observation.

    Each branch calls the tree's own production symbol. The
    captured-baseline shape is handed the baseline the same runner would
    have produced from the unchanged merge base -- the same objectives,
    because one environment cannot disagree with itself about a basin --
    which is the entire difference between the two shapes.
    """
    if SHAPE == "captured-baseline":
        baseline = {
            label: {"evals": evals[label], "objective": objective[label]}
            for label in evals
        }
        return len(stress.work_drift_compare(evals, objective, baseline).covered)
    return sum(
        1 for label in evals
        if stress.matching_basin(TABLE, label, objective[label]) is not None
    )


for tag, flip in (("recorded_basins", False), ("third_basin_cohort", True)):
    _evals, _objective = observation(flip)
    _covered = covered(_evals, _objective)
    result(f"{tag}.covered", _covered, "count")
    result(f"{tag}.fires", int(_covered < FLOOR), "bool")

# -- section 2: a basin the hardware chose, not one this file wrote --------
_orig_guess = opt_mod._price_guess_weights


def _elsewhere(prices):
    """A different, still legal, multi-start start: the band reversed."""
    return np.clip(1.2 - _orig_guess(prices), 0.2, 1.0)


#: Process CPU over this-thread CPU across the two real solves. No number
#: here is a timing, so nothing depends on it -- it is printed because a
#: threaded BLAS would mean the two solves were not the pinned,
#: single-threaded ones the rest of this suite measures.
CPU = {"process": 0.0, "thread": 0.0}


def solve(label: str, perturb: bool) -> tuple[int, float]:
    combo = next(
        dict(c) for c in stress.sweep_combinations() if c["label"] == label
    )
    combo.pop("label")
    if perturb:
        opt_mod._price_guess_weights = _elsewhere
    started, started_thread = time.process_time(), time.thread_time()
    try:
        run = stress.build_case(**combo)
    finally:
        opt_mod._price_guess_weights = _orig_guess
    CPU["process"] += time.process_time() - started
    CPU["thread"] += time.thread_time() - started_thread
    return int(run["solver_evals"]), float(run["result"].objective_value)


plain_evals, plain_obj = solve(VICTIM, False)
moved_evals, moved_obj = solve(VICTIM, True)
result("real.plain_evals", plain_evals, "count")
result("real.moved_evals", moved_evals, "count")
result("real.objective_rel_move",
       abs(moved_obj - plain_obj) / abs(plain_obj), "relative")
result("real.evals_ratio", moved_evals / max(plain_evals, 1), "ratio")

# The question both shapes are asked: with the solver in the basin THIS
# MACHINE chose, is that scenario still judged?
if SHAPE == "captured-baseline":
    _judged = len(stress.work_drift_compare(
        {VICTIM: moved_evals},
        {VICTIM: moved_obj},
        {VICTIM: {"evals": moved_evals, "objective": moved_obj}},
    ).covered)
else:
    _judged = int(stress.matching_basin(TABLE, VICTIM, moved_obj) is not None)
result("real.judged_after_move", _judged, "count")

result("thread_factor", CPU["process"] / max(CPU["thread"], 1e-9), "ratio")
result("load1", float(os.getloadavg()[0]), "load")
result("concurrent_processes", concurrent(), "count")
try:
    with open("/proc/vmstat") as fh:
        result("swapins",
               next(int(l.split()[1]) for l in fh if l.startswith("pswpin")),
               "count")
except (OSError, StopIteration):
    result("swapins", 0, "count")
