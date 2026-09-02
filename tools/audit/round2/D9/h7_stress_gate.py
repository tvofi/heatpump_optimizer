"""D9 metric 7: can the stress gate as shipped detect a synthetic 2x regression?

Metric: tests/stress.py's two relative checks, re-run over its own
``combinations`` list with its own ``Calibration`` and ``build_case`` --
per-scenario ratio = scenario solve CPU / trailing-median reference CPU,
gated at SOLVE_BUDGET_RATIO; sweep ratio = total solve CPU / total reference
CPU, gated at SWEEP_BUDGET_RATIO -- first unmodified, then with
``HeatPumpOptimizer.optimize`` made to do its work twice (an exact 2x CPU
regression injected at the symbol the gate times). Headroom = budget /
observed; a k-fold uniform regression is detected iff k > headroom. Ratios
against the reference solve are CPU ratios and final on the shared box.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h7_stress_gate.py

Expected (baseline c398fc8; ratios +-20 % run to run):
    plain sweep: worst scenario ratio ~40-60x against a 1400x budget
    (headroom > 20x); sweep ratio ~10-20x against a 450x budget (headroom
    > 20x); injected 2x: nothing trips -- the gate cannot see a 2x, nor a
    10x, uniform regression. CI (.github/workflows/tests.yml, tests/run.sh)
    sets none of STRESS_SOLVE_RATIO / STRESS_SWEEP_RATIO (grep count 0), so
    these defaults are what CI runs. No memory instrumentation exists in
    tests/ (grep count 0 for tracemalloc/getrusage/ru_maxrss).
    perturbation STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75 in the
    environment (between the plain and the injected ratios): plain still
    passes, the injected 2x sweep trips (tripped counts > 0). Measured on
    the fan-out box: plain worst 299x / sweep 50.7x, injected 591x / 105x.

Instrumented symbols: optimizer:HeatPumpOptimizer.optimize (the injection),
tests/stress.py:reference_solve / Calibration / build_case (the gate's own
ruler and cases, executed from the file).
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import copy
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

stress = d9lib.load_stress_prefix(marker="failures = 0")
build_case = stress["build_case"]
Calibration = stress["Calibration"]
SOLVE_BUDGET_RATIO = stress["SOLVE_BUDGET_RATIO"]
SWEEP_BUDGET_RATIO = stress["SWEEP_BUDGET_RATIO"]
CALIBRATION_WINDOW = stress["CALIBRATION_WINDOW"]
COMBINATIONS = stress["combinations"]

d9lib.result("combinations", len(COMBINATIONS), "count")
d9lib.result("solve_budget_ratio", SOLVE_BUDGET_RATIO, "ratio")
d9lib.result("sweep_budget_ratio", SWEEP_BUDGET_RATIO, "ratio")


def sweep(label: str):
    calibration = Calibration(CALIBRATION_WINDOW)
    calibration.warm_up()
    ratios, slow = [], []
    sweep_ref = sweep_solve = sweep_thread = 0.0
    for combo in copy.deepcopy(COMBINATIONS):
        name = combo.pop("label")
        sample_ms = calibration.sample()
        unit_ms = max(calibration.unit_ms, 1e-6)
        run = build_case(**combo)
        solve_ms = float(run["solve_cpu_ms"])
        ratio = solve_ms / unit_ms
        ratios.append((ratio, name))
        sweep_ref += sample_ms
        sweep_solve += solve_ms
        sweep_thread += float(run["solve_thread_ms"])
        if solve_ms > SOLVE_BUDGET_RATIO * unit_ms:
            slow.append(name)
    worst = max(ratios)
    sweep_ratio = sweep_solve / max(sweep_ref, 1e-6)
    d9lib.result(f"{label}.reference_unit", calibration.unit_ms, "ms_provisional")
    d9lib.result(f"{label}.worst_scenario", worst[1], "label")
    d9lib.result(f"{label}.worst_ratio", worst[0], "ratio")
    d9lib.result(f"{label}.median_ratio", float(np.median([r for r, _ in ratios])), "ratio")
    d9lib.result(f"{label}.sweep_ratio", sweep_ratio, "ratio")
    d9lib.result(f"{label}.per_scenario_headroom", SOLVE_BUDGET_RATIO / worst[0], "ratio")
    d9lib.result(f"{label}.sweep_headroom", SWEEP_BUDGET_RATIO / sweep_ratio, "ratio")
    d9lib.result(f"{label}.per_scenario_tripped", len(slow), "count")
    d9lib.result(f"{label}.sweep_tripped", int(sweep_ratio > SWEEP_BUDGET_RATIO), "count")
    d9lib.result(f"{label}.solve_cpu_total", sweep_solve, "ms_provisional")
    d9lib.result(f"{label}.thread_factor", sweep_solve / max(sweep_thread, 1e-9), "ratio")
    return worst[0], sweep_ratio, sweep_solve / max(sweep_thread, 1e-9)


plain_worst, plain_sweep, tf1 = sweep("plain")

_orig = opt_mod.HeatPumpOptimizer.optimize


def doubled(self, *a, **k):
    _orig(self, *a, **k)
    return _orig(self, *a, **k)


opt_mod.HeatPumpOptimizer.optimize = doubled
try:
    inj_worst, inj_sweep, tf2 = sweep("injected_2x")
finally:
    opt_mod.HeatPumpOptimizer.optimize = _orig

d9lib.result("injected_over_plain_worst", inj_worst / plain_worst, "ratio")
d9lib.result("injected_over_plain_sweep", inj_sweep / plain_sweep, "ratio")
d9lib.result("smallest_detectable_uniform_regression",
             min(SOLVE_BUDGET_RATIO / plain_worst, SWEEP_BUDGET_RATIO / plain_sweep), "ratio")

# What CI actually sets, and what instrumentation the suite has: executed greps.
root = os.getcwd()


def grep_count(pattern: str, paths: list[str]) -> int:
    out = subprocess.run(["grep", "-E", "-c", pattern] + paths, capture_output=True, text=True)
    return sum(int(line.rsplit(":", 1)[-1]) for line in out.stdout.splitlines() if ":" in line)


ci = [os.path.join(root, ".github", "workflows", "tests.yml"), os.path.join(root, "tests", "run.sh")]
d9lib.result("ci_sets_stress_ratio", grep_count(r"^[^#]*STRESS_(SOLVE|SWEEP)_RATIO\s*[:=]", ci), "count")
tests = [os.path.join(root, "tests", f) for f in os.listdir(os.path.join(root, "tests")) if f.endswith(".py")]
d9lib.result("tests_memory_instrumentation", grep_count(r"tracemalloc|getrusage|ru_maxrss", tests), "count")
d9lib.closing(float(np.median([tf1, tf2])))
