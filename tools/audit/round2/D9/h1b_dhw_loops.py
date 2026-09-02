"""D9 metric 1 (DHW planning loops): tank-step equivalents and CPU share.

Metric (tools/audit/briefs/D9.md, "each DHW planning loop"): per call of
``HeatPumpOptimizer._build_dhw_requirements`` -- the entry point that runs
the LP seed (``_plan_dhw_min_cost``), the greedy repair
(``_plan_dhw_cheapest_first``, twice) and the min-run rounding
(``_apply_dhw_min_run``) -- the number of ``ThermalModel.simulate_dhw_only``
calls, the tank steps they cost (calls x n_steps, the Python-loop equivalent
of ``simulate_step`` for the tank), and the planner's thread-CPU as a share
of the whole solve and as a ratio to tests/stress.py:reference_solve.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h1b_dhw_loops.py

Expected (baseline c398fc8, n = 96, counts exact, ratios +-15 %):
    two_zone_dhw   dhw_requirement_calls = 1 (2 when _co_optimize replans),
                   simulate_dhw_only calls per planning call of order 10-100,
                   planner CPU ~ 4x the reference solve
    single_zone_dhw the planner is the majority (> 50 %) of the solve's CPU
    perturbation   horizon 24 h -> 48 h: tank steps per call rise (n doubles
                   and the greedy loop sees more windows)

Instrumented symbols: thermal_model:ThermalModel.simulate_dhw_only,
thermal_model:ThermalModel.compute_cop_dhw, optimizer:HeatPumpOptimizer.
_build_dhw_requirements / _plan_dhw_min_cost / _plan_dhw_cheapest_first /
_apply_dhw_min_run, optimizer:linprog.
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402

C: dict = {}


def reset():
    C.update(dhw_only_calls=0, tank_steps=0, cop_calls=0, req_calls=0,
             lp_calls=0, greedy_calls=0, minrun_calls=0, linprog_calls=0,
             t_req=0.0, t_lp=0.0, t_greedy=0.0, t_minrun=0.0, t_linprog=0.0,
             t_dhw_only=0.0, greedy_iters=[])


reset()


def timed(name_count, name_time, orig):
    def wrapper(*a, **k):
        C[name_count] += 1
        t0 = time.thread_time()
        try:
            return orig(*a, **k)
        finally:
            C[name_time] += time.thread_time() - t0
    return wrapper


_orig_dhw_only = tm_mod.ThermalModel.simulate_dhw_only
_orig_cop = tm_mod.ThermalModel.compute_cop_dhw


def hooked_dhw_only(self, initial_temp, dhw_power_schedule, *a, **k):
    C["dhw_only_calls"] += 1
    C["tank_steps"] += int(len(dhw_power_schedule))
    t0 = time.thread_time()
    try:
        return _orig_dhw_only(self, initial_temp, dhw_power_schedule, *a, **k)
    finally:
        C["t_dhw_only"] += time.thread_time() - t0


def hooked_cop(self, *a, **k):
    C["cop_calls"] += 1
    return _orig_cop(self, *a, **k)


tm_mod.ThermalModel.simulate_dhw_only = hooked_dhw_only
tm_mod.ThermalModel.compute_cop_dhw = hooked_cop
HP = opt_mod.HeatPumpOptimizer
HP._build_dhw_requirements = timed("req_calls", "t_req", HP._build_dhw_requirements)
HP._plan_dhw_min_cost = timed("lp_calls", "t_lp", HP._plan_dhw_min_cost)
HP._apply_dhw_min_run = timed("minrun_calls", "t_minrun", HP._apply_dhw_min_run)
_orig_greedy = HP._plan_dhw_cheapest_first


def hooked_greedy(self, *a, **k):
    C["greedy_calls"] += 1
    before = C["dhw_only_calls"]
    t0 = time.thread_time()
    try:
        return _orig_greedy(self, *a, **k)
    finally:
        C["t_greedy"] += time.thread_time() - t0
        C["greedy_iters"].append(C["dhw_only_calls"] - before)


HP._plan_dhw_cheapest_first = hooked_greedy
opt_mod.linprog = timed("linprog_calls", "t_linprog", opt_mod.linprog)

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
unit_ms, _ = d9lib.reference_unit_ms(stress, 5)
d9lib.result("reference_solve_cpu", unit_ms, "ms_provisional")


def report(label, clocks, n):
    req = max(C["req_calls"], 1)
    d9lib.result(f"{label}.n_steps", n, "count")
    d9lib.result(f"{label}.dhw_requirement_calls", C["req_calls"], "count")
    d9lib.result(f"{label}.lp_calls", C["lp_calls"], "count")
    d9lib.result(f"{label}.linprog_calls", C["linprog_calls"], "count")
    d9lib.result(f"{label}.greedy_calls", C["greedy_calls"], "count")
    d9lib.result(f"{label}.greedy_resimulations", ",".join(str(x) for x in C["greedy_iters"]), "count_list")
    d9lib.result(f"{label}.minrun_calls", C["minrun_calls"], "count")
    d9lib.result(f"{label}.simulate_dhw_only_calls", C["dhw_only_calls"], "count")
    d9lib.result(f"{label}.simulate_dhw_only_per_planning_call", C["dhw_only_calls"] / req, "count")
    d9lib.result(f"{label}.tank_steps", C["tank_steps"], "count")
    d9lib.result(f"{label}.tank_steps_per_planning_call", C["tank_steps"] / req, "count")
    d9lib.result(f"{label}.compute_cop_dhw_calls", C["cop_calls"], "count")
    tot = max(clocks.thread_ms / 1000.0, 1e-9)
    d9lib.result(f"{label}.solve_cpu", clocks.proc_ms, "ms_provisional")
    d9lib.result(f"{label}.planner_cpu", C["t_req"] * 1000.0, "ms_provisional")
    d9lib.result(f"{label}.planner_share_of_solve", C["t_req"] / tot, "ratio")
    d9lib.result(f"{label}.planner_over_reference", C["t_req"] * 1000.0 / unit_ms, "ratio")
    d9lib.result(f"{label}.lp_share_of_planner", C["t_lp"] / max(C["t_req"], 1e-9), "ratio")
    d9lib.result(f"{label}.linprog_share_of_planner", C["t_linprog"] / max(C["t_req"], 1e-9), "ratio")
    d9lib.result(f"{label}.greedy_share_of_planner", C["t_greedy"] / max(C["t_req"], 1e-9), "ratio")
    d9lib.result(f"{label}.minrun_share_of_planner", C["t_minrun"] / max(C["t_req"], 1e-9), "ratio")
    d9lib.result(f"{label}.tank_sim_share_of_planner", C["t_dhw_only"] / max(C["t_req"], 1e-9), "ratio")


tfs = []
for label, kw in (
    ("two_zone_dhw", dict(season="winter", two_zone=True, dhw=True)),
    ("single_zone_dhw", dict(season="winter", two_zone=False, dhw=True)),
    ("shoulder_single_zone_dhw", dict(season="shoulder", two_zone=False, dhw=True)),
    ("summer_single_zone_dhw", dict(season="summer", two_zone=False, dhw=True)),
    ("heavy_old_winter_dhw", dict(season="winter", building="heavy_old", two_zone=False, dhw=True)),
    ("perturb_h48_two_zone_dhw", dict(season="winter", two_zone=True, dhw=True, hours=48)),
):
    reset()
    with d9lib.Clocks() as c:
        run = build_case(**kw)
    report(label, c, run["n"])
    tfs.append(c.thread_factor)

d9lib.closing(float(np.median(tfs)))
