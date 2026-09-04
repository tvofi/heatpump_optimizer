"""D9 metric 8 (#346): can the gate detect a 2x regression confined to ONE
scenario, and does it stay quiet on a multi-start basin flip?

Metric: the sweep of tests/stress.py is run three times over its own
``sweep_combinations()`` with its own ``Calibration``/``build_case``, and
after each run EVERY per-scenario rule the file owns is evaluated over the
committed ``tests/stress_budgets.json``:

  * the global CPU ceiling      solve_cpu > SOLVE_BUDGET_RATIO * unit
  * the per-scenario CPU budget solve_ratio > recorded * SCENARIO_BUDGET_FACTOR
  * the sweep CPU budget        sweep_ratio > SWEEP_BUDGET_RATIO
  * the solver-work rule (head only, #346)
                                evals > recorded_evals * SCENARIO_WORK_FACTOR,
                                applied only where same_basin() holds

Since #387 that last rule has no recorded numbers to read: the baseline is
captured in the same environment, so here the PLAIN sweep -- this tree,
this process, minutes earlier -- is what the other three runs are judged
against, through stress.work_drift_compare(). The plain run's verdict
against itself is printed as the null control and must be empty.

The four runs are: PLAIN; INJECTED, with HeatPumpOptimizer.optimize made to
do its work twice for ONE scenario (the h7 injection, scoped -- an exact 2x
on that scenario and nothing else); BASIN, with that scenario's multi-start
initial guesses perturbed through the production symbol
_price_guess_weights so the solver starts elsewhere and lands in another
local minimum; and BASIN_2X, both at once -- another basin AND twice the
work, which is the null control proper. That is what CI did to
shoulder/tariff+cycle at 2.28x, and the gate must NOT fail on it.

Command (from the repository root, on an idle box, holding /tmp/hpo-gate.lock):
    PYTHONPATH=tests/hastub python3 tools/audit/round2/D9/h8_single_scenario.py

Expected: at the merge base d7fa97f the injected 2x trips 0 rules of any
kind (that is #346). At the head it trips exactly one, the solver-work rule,
on exactly the injected scenario, and the BASIN run trips none.

Instrumented symbols: optimizer:HeatPumpOptimizer.optimize (the injection),
optimizer:_price_guess_weights (the basin perturbation),
tests/stress.py:build_case / Calibration / reference_solve (the gate's own
cases and ruler, executed from the file under test).
Root rule: os.getcwd() -- copy this file into the tree to be measured and
run it from that tree's root. It never resolves anything from __file__.
Machine: 4-core Linux microVM (audit box).
"""
from __future__ import annotations

import os
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

VICTIM = os.environ.get("H8_VICTIM", "shoulder/cycle")


def result(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def concurrent() -> int:
    out = os.popen(
        "ps ax -o args= | grep -E '[s]tress\\.py|[t]ests/run\\.sh|[h]8_single'"
    ).read().splitlines()
    return len(out)


TABLE = stress.load_budget_table()
def combinations() -> list:
    """The sweep's list, from either shape of tests/stress.py.

    The head exposes ``sweep_combinations()``; at the merge base the same
    list only exists inside the file's ``__main__`` block, so it is executed
    out of the source. Identical code runs in both trees, which is the point.
    """
    if hasattr(stress, "sweep_combinations"):
        return stress.sweep_combinations()
    path = os.path.join(ROOT, "tests", "stress.py")
    with open(path) as fh:
        source = fh.read()
    start = source.index("    combinations = []")
    end = source.index("    failures = 0", start)
    block = "\n".join(
        line[4:] if line.startswith("    ") else line
        for line in source[start:end].split("\n")
    )
    namespace = dict(vars(stress))
    exec(compile(block, path, "exec"), namespace)  # noqa: S102
    return namespace["combinations"]


COMBOS = combinations()
# Three shapes have existed. #346 recorded one basin per scenario
# (recorded_evals/recorded_objective), PR #378 recorded several
# (matching_basin), and #387 records none at all: the baseline is CAPTURED
# in the same environment, so here the PLAIN sweep of this same tree in
# this same process is the baseline the other three runs are judged
# against. Without this branch the harness would report head_has_work_rule
# =0 on a current tree and look as though the rule had been deleted.
HAS_DRIFT = hasattr(stress, "work_drift_compare")
HAS_WORK = (
    HAS_DRIFT
    or hasattr(stress, "matching_basin")
    or hasattr(stress, "recorded_evals")
)
PLAIN_ROWS: dict = {}
result("head_has_work_rule", int(HAS_WORK), "bool")
result("scenarios", len(COMBOS), "count")

_orig_optimize = opt_mod.HeatPumpOptimizer.optimize
_orig_guess = opt_mod._price_guess_weights


def _twice(self, *a, **k):
    _orig_optimize(self, *a, **k)
    return _orig_optimize(self, *a, **k)


def _elsewhere(prices):
    """A different, still legal, start: the same [0.2, 1.0] band reversed."""
    base = _orig_guess(prices)
    return np.clip(1.2 - base, 0.2, 1.0)


def sweep(label_tag: str, mode: str):
    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
    cal.warm_up()
    rows, sweep_ref, sweep_cpu = {}, 0.0, 0.0
    started = time.perf_counter()
    for combo in [dict(c) for c in COMBOS]:
        name = combo.pop("label")
        sample = cal.sample()
        unit = max(cal.unit_ms, 1e-6)
        hot = name == VICTIM and mode != "plain"
        if hot and mode == "inject":
            opt_mod.HeatPumpOptimizer.optimize = _twice
        if hot and mode in ("basin", "basin2x"):
            opt_mod._price_guess_weights = _elsewhere
        if hot and mode == "basin2x":
            opt_mod.HeatPumpOptimizer.optimize = _twice
        try:
            run = stress.build_case(**combo)
        finally:
            opt_mod.HeatPumpOptimizer.optimize = _orig_optimize
            opt_mod._price_guess_weights = _orig_guess
        cpu = float(run["solve_cpu_ms"])
        rows[name] = {
            "ratio": cpu / unit,
            "cpu": cpu,
            "unit": unit,
            "wall": float(run["result"].solve_time_ms),
            "evals": int(run.get("solver_evals", 0)),
            "obj": float(run["result"].objective_value),
            "thread": float(run["solve_thread_ms"]),
        }
        sweep_ref += sample
        sweep_cpu += cpu
    sweep_ratio = sweep_cpu / max(sweep_ref, 1e-6)

    ceiling = [n for n, r in rows.items()
               if r["cpu"] > stress.SOLVE_BUDGET_RATIO * r["unit"]]
    budget = []
    stale = []
    for n, r in rows.items():
        allowed = stress.scenario_budget(n, TABLE)
        if allowed is not None and r["ratio"] > allowed:
            budget.append(n)
        rec = TABLE.get(n, {}).get("ratio")
        if rec and r["ratio"] < float(rec) / stress.SCENARIO_STALE_FACTOR:
            stale.append(n)
    sweep_trip = int(sweep_ratio > stress.SWEEP_BUDGET_RATIO)
    work, flipped = [], []
    if HAS_DRIFT and PLAIN_ROWS:
        verdict = stress.work_drift_compare(
            {n: r["evals"] for n, r in rows.items()},
            {n: r["obj"] for n, r in rows.items()},
            {n: {"evals": r["evals"], "objective": r["obj"]}
             for n, r in PLAIN_ROWS.items()},
        )
        work = [f.split()[0] for f in verdict.over]
        flipped = [f.split()[0] for f in verdict.replanned]
    elif HAS_WORK and not HAS_DRIFT:
        for n, r in rows.items():
            if hasattr(stress, "matching_basin"):
                # A scenario may have several recorded basins; the rule
                # judges the work against the count for the basin this
                # solve actually landed in.
                rec_ev = stress.matching_basin(TABLE, n, r["obj"])
            elif stress.recorded_evals(TABLE, n) is None:
                continue
            elif stress.same_basin(
                r["obj"], stress.recorded_objective(TABLE, n)
            ):
                rec_ev = stress.recorded_evals(TABLE, n)
            else:
                rec_ev = None
            if rec_ev is None:
                flipped.append(n)
                continue
            if r["evals"] > rec_ev * stress.SCENARIO_WORK_FACTOR:
                work.append(n)

    total = len(ceiling) + len(budget) + sweep_trip + len(work)
    v = rows[VICTIM]
    result(f"{label_tag}.victim_cpu_ratio", v["ratio"], "ratio")
    result(f"{label_tag}.victim_evals", v["evals"], "count")
    result(f"{label_tag}.victim_objective", v["obj"], "value")
    result(f"{label_tag}.sweep_ratio", sweep_ratio, "ratio")
    result(f"{label_tag}.tripped_cpu_ceiling", len(ceiling), "count")
    result(f"{label_tag}.tripped_cpu_per_scenario", len(budget), "count")
    result(f"{label_tag}.tripped_cpu_stale", len(stale), "count")
    result(f"{label_tag}.tripped_sweep", sweep_trip, "count")
    result(f"{label_tag}.tripped_solver_work", len(work), "count")
    result(f"{label_tag}.solver_work_flipped", len(flipped), "count")
    result(f"{label_tag}.tripped_total", total, "count")
    result(f"{label_tag}.work_names", ",".join(sorted(work)) or "-", "labels")
    result(f"{label_tag}.wall_s", time.perf_counter() - started, "s")
    result(f"{label_tag}.concurrent_processes", concurrent(), "count")
    tf = sum(r["cpu"] for r in rows.values()) / max(
        sum(r["thread"] for r in rows.values()), 1e-9)
    result(f"{label_tag}.thread_factor", tf, "ratio")
    result(f"{label_tag}.load1", float(os.getloadavg()[0]), "load")
    return rows, tf


plain, tf = sweep("plain", "plain")
PLAIN_ROWS.update(plain)
if HAS_DRIFT:
    # The plain run is the baseline for the three that follow, so its own
    # work verdict is taken against itself: the null control, and it must
    # be empty by construction or the comparison is not one.
    _null = stress.work_drift_compare(
        {n: r["evals"] for n, r in plain.items()},
        {n: r["obj"] for n, r in plain.items()},
        {n: {"evals": r["evals"], "objective": r["obj"]}
         for n, r in plain.items()},
    )
    result("plain.null_control_tripped_solver_work", len(_null.over), "count")
    result("plain.null_control_covered", len(_null.covered), "count")
inj, _ = sweep("injected_2x_one_scenario", "inject")
bas, _ = sweep("basin_flip_one_scenario", "basin")
b2x, _ = sweep("basin_flip_and_2x_one_scenario", "basin2x")

result("injected_over_plain_cpu",
       inj[VICTIM]["ratio"] / plain[VICTIM]["ratio"], "ratio")
result("basin_over_plain_cpu",
       bas[VICTIM]["ratio"] / plain[VICTIM]["ratio"], "ratio")
if plain[VICTIM]["evals"]:
    result("injected_over_plain_evals",
           inj[VICTIM]["evals"] / plain[VICTIM]["evals"], "ratio")
    result("basin_over_plain_evals",
           bas[VICTIM]["evals"] / plain[VICTIM]["evals"], "ratio")
result("basin2x_over_plain_cpu",
       b2x[VICTIM]["ratio"] / plain[VICTIM]["ratio"], "ratio")
if plain[VICTIM]["evals"]:
    result("basin2x_over_plain_evals",
           b2x[VICTIM]["evals"] / plain[VICTIM]["evals"], "ratio")
result("basin2x_objective_rel_move",
       abs(b2x[VICTIM]["obj"] - plain[VICTIM]["obj"]) / abs(plain[VICTIM]["obj"]),
       "relative")
result("basin_objective_rel_move",
       abs(bas[VICTIM]["obj"] - plain[VICTIM]["obj"]) / abs(plain[VICTIM]["obj"]),
       "relative")
result("thread_factor", tf, "ratio")
result("load1", float(os.getloadavg()[0]), "load")
try:
    with open("/proc/vmstat") as fh:
        result("swapins", next(int(l.split()[1]) for l in fh
                               if l.startswith("pswpin")), "count")
except Exception:
    result("swapins", -1, "count")
