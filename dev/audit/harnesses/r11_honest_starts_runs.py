"""R11-OUTSIDE-HONEST-STARTS-RUNS: what the committed runs ship, measured on one tree.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|defaults|gradient|stress|kernels|identity|stage

Synthetic throughout; no private data. The finding is outside pull request
3529 (Bankaifan), which has no finder harness; this one reproduces the pull
request body's figures.

``fixtures``: the two golden plan scenarios that set a cycling cost
(``cycling_cost``, ``everything_on``), captured by ``tests/golden.py`` on the
tree this runs in. Printed per scenario: the space plan's steps between the
plan's running rule (0.1 kW) and the 1.0 kW floor, the same for the combined
draw (hot-water levels are the planner's), off-to-on edges of the combined
draw, energy, ``predicted_cost`` and the lowest room temperature. Runs on a
tree before the pull request too: it reads the published arrays only.

``c1``: the same two lines with ``optimizer._engaged`` reduced to
``clamp_planned_levels`` alone, ruling c1's other arm as one predicate and
nothing else (the swing term stays deleted). Read against ``fixtures`` on
this tree and on the merge base: the arm is a null only where its lines
equal the merge base's. Exits 2 on a tree without ``_engaged``.

``descents``: a solve that prices a duty switch descends twice, with the
switch operand and as a solve that prices no stop would
(``optimizer._relaxed_plans``). Three installs (duty-cycle, modulating
clamped, fixed-speed) x four days, the contributor's pair (a certain stop
from hot water to heating, 501 s off), cycling cost 0.3. Per cell and arm
(both descents, the operand's alone, the unpriced one alone): the published
objective and the shipped plan's switch weight at the combined draw. Null
control: with an empty pair the arms have one descent each and print one
plan; the harness exits 1 otherwise. On a tree without ``_relaxed_plans`` it
prints that there is nothing to compare and exits 0.

``grid``: a buffered single-zone house, space only, at cycling cost 0 / 0.25
and clamped or not: steps under the floor, edges, energy and solve seconds
(``time.process_time``) per cell. The unpriced duty-cycle cell is the null:
it must never enter the candidate stage where the tree has one.

``defaults``: owner ruling Q2's measurement (R11-OUTSIDE-HONEST-STARTS-RUNS-P3):
what a default start price would do to an install with ``clamp_planned_levels``
on and no configured price. The rule measured: the default replaces a
configured cycling cost of zero on a clamped install and nothing else. For
each candidate on ``DEFAULT_LADDER`` (zero, then across the options field's
0 to 10 range), on the ``grid`` mode's clamped unpriced cell and on the two
fixtures ``fixtures`` reads, each solved clamped at a configured price of
zero, per solve: off-to-on edges of the combined draw, energy, the
optimizer's ``predicted_cost`` (the objective carries the start price, so it
is not comparable across candidates) and the lowest room temperature. Null
controls, solved with no default and with the ladder's highest: the same
three installs at their own configured price (clamped), and the same three
unclamped at price zero; each pair must ship array-equal plans. Exits 1 when
a null pair differs. On a tree that ships the default
(``om.CLAMPED_DEFAULT_START_PRICE``) each candidate patches it and the tree's
own rule applies it, so the nulls test that rule; on a tree without it the
rule is applied by the harness and the nulls hold by construction.

``gradient``: what the batched finite-difference gradient simulates
(``optimizer._batch_fd_gradient``, design note n6). Four goldens that fix
part of the horizon (a committed mask, hot-water blocks) and one grid cell
that fixes none, the null. Per solve: gradient calls, the share of their
variables the bounds fix, the rows the batch objective was handed against
the rows a batch of every variable holds, CPU seconds, and a sha1 over
every gradient returned and over the shipped plan. Runs on a tree before
the change too: there the two row counts are equal on every line, and the
two digests are what the change must not move. Exits 1 when the null cell
has a fixed variable or was handed fewer rows than the full batch.

``stress``: what the second descent costs, by ``tests/stress.py``'s own
measure (design verdict item r3). The sweep's scenarios that price a cycle
(``sweep_combinations()``, ``cycling`` above zero; all hold hot water) are
built by its ``build_case`` with a duty-switch pair on the config the case
constructs, and each solve's CPU is divided by the trailing median of its
reference solve, sampled beside it, as the sweep does. Arms: the
contributor's pair as the tree solves it; the same with the second
descent's guard reading no stop for the length of ``_relaxed_plans`` (one
descent and one relaxed plan for the stage to commit; the solve's other
readers of the stops run outside that call); and an
empty pair in both forms, the null, which descends once either way. Per
scenario and arm: the median ratio over ``STRESS_REPEATS`` solves (default
3), descents per space solve, the calls of the multi-start, and the
scenario's own recorded budget from ``tests/stress_budgets.json``. The last
lines print the second descent's cost per scenario and the null's two forms
against each other, the noise this box puts on such a difference. Runs on a
tree without ``_relaxed_plans`` too: there each pair has the one arm. Exits
1 when a null solve descends twice, the null's two forms ship different
plans, or the pair's solve never descends twice on a tree that can.

``kernels``: the acceptance checks of the two ``tests/features.py`` blocks
that solve this group's fixtures, once per OpenBLAS kernel (``tests/README.md``,
"A knife-edge optimizer comparison must be measured across BLAS kernels").
Per kernel (``OPENBLAS_CORETYPE``; SkylakeX, Haswell, Sandybridge and Nehalem,
or those named after the mode) both blocks run through
``tools/audit/seat/features_block.py`` in the checkout this is run from, one thread,
and each check whose name starts ``acceptance`` is printed with its verdict
and its detail string. Beside them, on the same solves, the two clauses the
round-4 repair replaced: the order of the two switch weights in starts on
the modulating clamped install, and the shipped energy within one floor step
of the relaxed plan's, with the figures each reads, and the two start counts
of the kept clause. The replaced clauses are
the null control of the restated ones: they read False under the kernels the
restated checks read True on. Runs on a tree before the restatement too,
where the checks printed are the replaced clauses themselves. Exits 1 when
a block fails a check or does not complete under any kernel, so the mode
with one kernel named is a command ``tools/audit/seat/mutant_run.py`` can
drive; a kernel this processor cannot run is printed as such and counted as
not completed.

``identity [seed]``: the leaf's identity arms (design note round 3, item a2).
The design review's leaf generator (``ev/reviewer_leaf_props.py`` of the
round-1 fix verdict at 04e5bcfca3, seed 0 by default), 3000 realizable
plans, ``runs.commit`` at band 2 with one-step lengths and the cap at p_max:
per arm, the masks other than the plan's own. Arms: prices and start price as
generated; start price zero; a flat price of 1.0 and start price zero; price
and start price zero; that arm with ``runs._TIE_BREAK`` at 0, the
perturbation. Exits 1 when the zero arm moves a mask or its perturbation
moves none.

``stage [seed] [cells]``: the candidate stage per call (design note round 3,
item a2; design verdict item r1), a spy on ``optimizer._commit_runs`` over
the 12 cells of ``descents`` and over the design review's generated solves
(``ev/reviewer_solve_props.py``'s generator at 04e5bcfca3, seed 1 and 140
cells by default; 0 cells reads the ``descents`` cells alone).
Per set: engaged stage calls; of those handed two relaxed plans, the shipped
score against the same call re-run with the first relaxed plan alone, both
in their shipped scopes (below, equal, above); and the calls whose first
relaxed plan is realizable beside the tank, shipped changed or not and how
many price a start. Per changed one: the gain, the relaxed plan clipped into
the shipped scope's box and scored in that scope less the shipped score,
printed beside the clip distance (kW the relaxed plan lay outside that box),
and the edges of the combined draw before and after. Exits 1 when a call's
two plans score above its first alone or a changed realizable plan scores
above its clipped relaxed plan.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone

import numpy as np

import heatpump_optimizer.optimizer as om
from heatpump_optimizer import duty_legs
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

STEPS = np.arange(96)
T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
RUNS_AT = 0.1
PAIR, OFF = (1.0, 0.0), (501.0, 0.0)
INSTALLS = (("duty-cycle", False, 1.5), ("modulating clamped", True, 1.5), ("fixed-speed", True, 5.5))
DAYS = ((30, 2.0), (60, 2.0), (30, -4.0), (0, 6.0))


def edges(total) -> int:
    on = np.asarray(total, float) > RUNS_AT
    return int(np.sum(on & ~np.r_[False, on[:-1]]))


def under(plan, floor: float) -> int:
    plan = np.asarray(plan, float)
    return int(np.sum((plan > RUNS_AT) & (plan < floor - 1e-9)))


def fixtures() -> int:
    import golden

    for name in ("cycling_cost", "everything_on"):
        got = golden.capture(name, golden.SCENARIOS[name])
        space = np.asarray(got["power_schedule"], float)
        dhw = np.asarray(got.get("dhw_power_schedule") or np.zeros_like(space), float)
        rooms = np.asarray(got["room_temp_trajectory"], float)
        print(f"{name}: space steps under 1.0 kW {under(space, 1.0)}, combined {under(space + dhw, 1.0)},"
              f" edges {edges(space + dhw)}, published starts {got['compressor_starts']},"
              f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f},"
              f" predicted_cost {got['predicted_cost']:.2f}, lowest_room {float(rooms.min()):.2f}")
    return 0


def c1() -> int:
    if not hasattr(om, "_engaged"):
        print("this tree has no optimizer._engaged: nothing to reduce")
        return 2
    kept = om._engaged
    om._engaged = lambda opt: opt.config.clamp_planned_levels
    try:
        return fixtures()
    finally:
        om._engaged = kept


def _switch_solve(clamp: bool, p_min: float, pair, arm: str, phase: int, out_mean: float):
    params = ThermalParameters()
    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
    params.dhw_enabled = True
    cfg = om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=0.3)
    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, OFF
    opt = om.HeatPumpOptimizer(ThermalModel(params), cfg)
    kept, counts = om._relaxed_plans, []

    def plans(*args):
        res, relaxed = kept(*args)
        counts.append(len(relaxed))
        return res, {"operand": relaxed[:1], "unpriced": relaxed[-1:]}.get(arm, relaxed)

    om._relaxed_plans = plans
    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    try:
        result = opt.optimize(inputs=solve_inputs(
            initial_state=ThermalState(
                room_temperature=20.5, upper_floor_temperature=20.5,
                lower_floor_temperature=20.5, slab_temperature=21.0,
                outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
                dhw_temperature=45.0, dhw_hours_since_legionella=20.0,
            ),
            prices=1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - phase) / 96.0),
            outdoor_temps=outdoor, start_time=T0,
        ))
    finally:
        om._relaxed_plans = kept
    space = np.asarray(result.power_schedule, float)
    dhw = np.asarray(result.dhw_power_schedule, float)
    weight = duty_legs.switch_weight(space, dhw, PAIR, 5.5, p_min if clamp else None, om._leg_rule(opt))
    return float(result.objective_value), float(weight), set(counts), space, dhw


def descents() -> int:
    if not hasattr(om, "_relaxed_plans"):
        print("this tree has one descent per space solve: nothing to compare")
        return 0
    null_bad = 0
    for name, clamp, p_min in INSTALLS:
        for phase, out_mean in DAYS:
            row = {arm: _switch_solve(clamp, p_min, PAIR, arm, phase, out_mean)
                   for arm in ("both", "operand", "unpriced")}
            print(f"{name} price phase {phase} outdoor {out_mean}: " + ", ".join(
                f"{arm} objective {got[0]:.4f} switch_weight {got[1]:.4f}" for arm, got in row.items()))
        nulls = [_switch_solve(clamp, p_min, (0.0, 0.0), arm, 30, 2.0) for arm in ("both", "operand", "unpriced")]
        same = all(np.array_equal(nulls[0][3], n[3]) and np.array_equal(nulls[0][4], n[4]) for n in nulls)
        descended = set().union(*(n[2] for n in nulls))
        print(f"{name} null (empty pair): one plan across the arms {same}, descents per space solve {sorted(descended)}")
        null_bad += (not same) or descended != {1}
    print(f"null cells that moved or descended twice {null_bad}")
    return 1 if null_bad else 0


GRID_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)


def _grid_solve(cost: float, clamp: bool, p_min: float, loss: float, out_mean: float):
    params = ThermalParameters()
    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
    params.dhw_enabled, params.house_heat_loss_scale = False, loss
    opt = om.HeatPumpOptimizer(
        ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    return opt.optimize(inputs=solve_inputs(
        initial_state=ThermalState(
            room_temperature=20.5, upper_floor_temperature=20.5,
            lower_floor_temperature=20.5, slab_temperature=21.0,
            outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
            dhw_temperature=50.0,
        ),
        prices=GRID_PRICES, outdoor_temps=outdoor, start_time=T0,
    ))


def grid() -> int:
    staged, bad = [], 0
    kept = getattr(om, "_run_plans", None)
    if kept is not None:
        om._run_plans = lambda *args: (staged.append(1), kept(*args))[1]
    try:
        for cost, clamp, p_min, loss, out_mean in (
            (0.0, False, 1.1, 0.4, 8.0), (0.25, False, 1.1, 0.4, 8.0), (0.25, False, 0.53, 0.4, 8.0),
            (0.0, True, 1.1, 0.4, 8.0), (0.25, True, 1.1, 0.4, 8.0), (0.25, False, 1.1, 1.0, 2.0),
        ):
            staged.clear()
            t = time.process_time()
            result = _grid_solve(cost, clamp, p_min, loss, out_mean)
            seconds = time.process_time() - t
            plan = np.asarray(result.power_schedule, float)
            print(f"cost {cost} clamp {clamp} p_min {p_min} loss {loss}: steps under the floor"
                  f" {under(plan, max(p_min, RUNS_AT))}, edges {edges(plan)},"
                  f" energy_kwh {float(plan.sum()) * 0.25:.2f}, objective {float(result.objective_value):.4f},"
                  f" stage entered {bool(staged)}, solve_s {seconds:.2f}")
            bad += bool(staged) and not (cost > 0 or clamp)
    finally:
        if kept is not None:
            om._run_plans = kept
    print(f"null (unpriced duty-cycle) cells that entered the stage {bad}")
    return 1 if bad else 0


#: Candidate default start prices; the options field (``config_flow``'s wear
#: group) takes 0 to 10 in steps of 0.05.
DEFAULT_LADDER = (0.0, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.5, 5.0, 10.0)


def _default_installs():
    """(label, configured price, solve(clamp, price)) for the grid cell and the two fixtures."""
    import golden

    def fixture(name):
        spec = golden.SCENARIOS[name]

        def solve(clamp, price):
            opt = dict(spec.get("opt_overrides") or {}, clamp_planned_levels=clamp, cycling_cost=price)
            got = golden.capture(name, dict(spec, opt_overrides=opt))
            space = np.asarray(got["power_schedule"], float)
            dhw = np.asarray(got.get("dhw_power_schedule") or np.zeros_like(space), float)
            return space + dhw, float(got["predicted_cost"]), float(np.min(got["room_temp_trajectory"]))
        return name, float(spec["opt_overrides"]["cycling_cost"]), solve

    def grid_cell(clamp, price):
        r = _grid_solve(price, clamp, 1.1, 0.4, 8.0)
        return (np.asarray(r.power_schedule, float), float(r.predicted_cost),
                float(np.min(r.room_temp_trajectory)))
    return [("grid p_min 1.1 loss 0.4", 0.25, grid_cell), fixture("cycling_cost"), fixture("everything_on")]


def _effective(clamp: bool, configured: float, default: float) -> float:
    """The measured rule: the default replaces a configured zero on a clamped install only."""
    return default if clamp and configured == 0 else configured


def _at_default(solve, clamp: bool, configured: float, default: float):
    """``solve`` with ``default`` as the clamped default start price.

    Where the tree ships the default (``om.CLAMPED_DEFAULT_START_PRICE``),
    the tree's own rule applies it, patched to the candidate; on a tree
    without it, the measured rule above is applied here.
    """
    if not hasattr(om, "CLAMPED_DEFAULT_START_PRICE"):
        return solve(clamp, _effective(clamp, configured, default))
    kept = om.CLAMPED_DEFAULT_START_PRICE
    om.CLAMPED_DEFAULT_START_PRICE = default
    try:
        return solve(clamp, configured)
    finally:
        om.CLAMPED_DEFAULT_START_PRICE = kept


def defaults() -> int:
    def line(plan, cost, room):
        return (f"starts {edges(plan)}, energy_kwh {float(np.sum(plan)) * 0.25:.2f},"
                f" predicted_cost {cost:.4f}, lowest_room {room:.2f}")

    bad = 0
    for label, priced, solve in _default_installs():
        for default in DEFAULT_LADDER:
            plan, cost, room = _at_default(solve, True, 0.0, default)
            print(f"{label}, clamped, configured 0, default {default}: {line(plan, cost, room)}")
        top = DEFAULT_LADDER[-1]
        for arm, clamp, configured in (("priced clamped", True, priced), ("unpriced unclamped", False, 0.0)):
            without = _at_default(solve, clamp, configured, 0.0)
            with_ = _at_default(solve, clamp, configured, top)
            same = np.array_equal(without[0], with_[0])
            print(f"{label}, null {arm} (configured {configured}): without default {line(*without)};"
                  f" default {top}: {line(*with_)}; array-equal {same}")
            bad += not same
    print(f"null pairs that differ {bad}")
    return 1 if bad else 0


def _metered(solve):
    """Run ``solve`` with the batched gradient metered; its plan and the meter."""
    kept = om._batch_fd_gradient
    seen = {"calls": 0, "variables": 0, "fixed": 0, "rows": 0, "full": 0}
    digest = hashlib.sha1()

    def metered(batch_objective, args, x0, f0, eps, bounds):
        def counted(rows, *a):
            seen["rows"] += int(np.asarray(rows).shape[0])
            return batch_objective(rows, *a)

        grad = kept(counted, args, x0, f0, eps, bounds)
        seen["calls"] += 1
        seen["variables"] += len(bounds)
        seen["fixed"] += sum(1 for lo, hi in bounds if not lo < hi)
        seen["full"] += len(bounds) + (1 if f0 is None else 0)
        digest.update(np.asarray(grad, float).tobytes())
        return grad

    om._batch_fd_gradient = metered
    t = time.process_time()
    try:
        plan = solve()
    finally:
        om._batch_fd_gradient = kept
    seen["seconds"] = time.process_time() - t
    seen["gradients"] = digest.hexdigest()[:12]
    seen["plan"] = hashlib.sha1(np.asarray(plan, float).tobytes()).hexdigest()[:12]
    return seen


def _null_cell():
    params = ThermalParameters()
    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = 1.1, 5.5
    params.dhw_enabled, params.house_heat_loss_scale = False, 0.4
    opt = om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig())
    outdoor = 8.0 + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    result = opt.optimize(inputs=solve_inputs(
        initial_state=ThermalState(
            room_temperature=20.5, upper_floor_temperature=20.5,
            lower_floor_temperature=20.5, slab_temperature=21.0,
            outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
            dhw_temperature=50.0,
        ),
        prices=1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0),
        outdoor_temps=outdoor, start_time=T0,
    ))
    return result.power_schedule


def gradient() -> int:
    import golden

    def fixture(name):
        got = golden.capture(name, golden.SCENARIOS[name])
        return np.r_[got["power_schedule"], got.get("dhw_power_schedule") or []]

    cells = [(name, lambda name=name: fixture(name))
             for name in ("cycling_cost", "everything_on", "winter_two_zone_dhw", "valve_storage")]
    cells.append(("null: unpriced duty-cycle, space only", _null_cell))
    bad = 0
    for name, solve in cells:
        got = _metered(solve)
        print(f"{name}: gradients {got['calls']}, variables fixed {got['fixed']} of {got['variables']},"
              f" rows simulated {got['rows']} of {got['full']} in a full batch,"
              f" cpu_s {got['seconds']:.2f}, gradients sha1 {got['gradients']}, plan sha1 {got['plan']}")
        if name.startswith("null"):
            bad += got["fixed"] != 0 or got["rows"] != got["full"]
    print(f"null cell with a fixed variable or a short batch {bad}")
    return 1 if bad else 0


def _stress_case(stress, spec: dict, pair, first_alone: bool) -> dict:
    """One build of a sweep scenario with ``pair`` on its config: the solve's
    CPU ms, descents per space solve, multi-start calls and the plan."""
    kept_cfg, kept_min = stress.OptimizationConfig, om._multi_start_minimize
    kept_plans, kept_stops = getattr(om, "_relaxed_plans", None), om._priced_stops
    seen = {"descents": [], "multi_starts": 0}

    def config(**kw):
        cfg = kept_cfg(**kw)
        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, OFF
        return cfg

    def counted(*args, **kw):
        seen["multi_starts"] += 1
        return kept_min(*args, **kw)

    def plans(*args):
        if first_alone:
            om._priced_stops = lambda opt: None
        try:
            out = kept_plans(*args)
        finally:
            om._priced_stops = kept_stops
        seen["descents"].append(len(out[1]))
        return out

    stress.OptimizationConfig, om._multi_start_minimize = config, counted
    if kept_plans is not None:
        om._relaxed_plans = plans
    try:
        run = stress.build_case(**{k: v for k, v in spec.items() if k != "label"})
    finally:
        stress.OptimizationConfig, om._multi_start_minimize = kept_cfg, kept_min
        if kept_plans is not None:
            om._relaxed_plans = kept_plans
    result = run["result"]
    seen["cpu_ms"] = float(run["solve_cpu_ms"])
    seen["plan"] = np.r_[result.power_schedule, result.dhw_power_schedule]
    return seen


def stress_cost() -> int:
    import stress

    repeats = int(os.environ.get("STRESS_REPEATS", "3"))
    table = stress.load_budget_table()
    specs = [spec for spec in stress.sweep_combinations() if spec.get("cycling")]
    two = hasattr(om, "_relaxed_plans")
    arms = [("pair", PAIR, False), ("null", (0.0, 0.0), False)]
    if two:
        arms[1:1] = [("pair, first descent alone", PAIR, True)]
        arms.append(("null, guard off", (0.0, 0.0), True))
    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
    cal.warm_up()
    bad, cost, noise = 0, [], []
    for spec in specs:
        row = {}
        for name, pair, first_alone in arms:
            ratios = []
            for _ in range(repeats):
                cal.sample()
                got = _stress_case(stress, spec, pair, first_alone)
                ratios.append(got["cpu_ms"] / max(cal.unit_ms, 1e-6))
            row[name] = (float(np.median(ratios)), sorted(set(got["descents"])), got["multi_starts"], got["plan"])
        budget = stress.scenario_budget(spec["label"], table)
        print(f"{spec['label']} (recorded budget {budget:.1f}x): " + "; ".join(
            f"{name} {ratio:.1f}x, descents {descents or 'one per solve, no stage to count'},"
            f" multi-starts {calls}" for name, (ratio, descents, calls, _plan) in row.items()))
        if two:
            cost.append(row["pair"][0] - row["pair, first descent alone"][0])
            noise.append(row["null"][0] - row["null, guard off"][0])
            bad += row["null"][1] != [1] or row["null, guard off"][1] != [1]
            bad += not np.array_equal(row["null"][3], row["null, guard off"][3])
            bad += 2 not in row["pair"][1] or row["pair, first descent alone"][1] != [1]
    lo, mid, hi = cal.spread()
    print(f"reference solve {mid:.1f} ms of CPU (min {lo:.1f}, max {hi:.1f}) over {cal.count} samples;"
          f" {repeats} solve(s) per arm, the median ratio printed")
    if two:
        print("second descent, pair less its first descent alone, x reference per scenario: "
              + ", ".join(f"{c:+.1f}" for c in cost) + f"; median {float(np.median(cost)):+.1f}")
        print("null, as the tree less guard off (one descent in both), x reference per scenario: "
              + ", ".join(f"{c:+.1f}" for c in noise) + f"; median {float(np.median(noise)):+.1f}")
    else:
        print("this tree has one descent per space solve: no second descent to cost")
    print(f"scenarios whose null descended twice or moved, or whose pair never descended twice {bad}")
    return 1 if bad else 0


def identity() -> int:
    from heatpump_optimizer import runs

    rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    arms = ("as generated", "start price zero", "flat price, start price zero",
            "price zero, start price zero", "price zero, start price zero, tie break 0")
    moved, kept_tie = dict.fromkeys(arms, 0), runs._TIE_BREAK
    for t in range(3000):
        # The design review's leaf generator, its draws in its order: only the
        # realizable plan, its step width, prices and start price are read.
        n = int(rng.integers(1, 40))
        f = float(rng.choice([0.0, 0.05, 0.53, 1.0, 1.1, 5.5]))
        floor = runs.floor_kw(f)
        p_max = max(5.5, floor)
        q = np.where(rng.random(n) < 0.5, rng.uniform(floor, p_max, n), 0.0)
        rng.uniform(0, p_max, (5, n)), rng.random((5, n))
        if n >= 2:
            rng.random(n)
        dt = float(rng.choice([1 / 12, 0.25, 0.5, 1.0]))
        rng.uniform(0, p_max, n), rng.random(n), rng.choice([0.2, 1.0])
        rng.random(n), rng.uniform(0, floor * 1.2, n), rng.random(n), rng.random(n)
        prices = rng.uniform(-0.2, 3, n) if t % 3 else np.full(n, 1.0)
        start = float(rng.choice([0.0, 0.25, 5.0]))
        rng.random()
        for arm, price, cost in zip(arms, (prices, prices, 1.0, 0.0, 0.0), (start, 0.0, 0.0, 0.0, 0.0)):
            runs._TIE_BREAK = 0.0 if arm.endswith("tie break 0") else kept_tie
            try:
                mask = runs.commit(q, price, f, p_max, cost, 2, dt=dt, lengths=(1, 1))[0]
            finally:
                runs._TIE_BREAK = kept_tie
            moved[arm] += not np.array_equal(mask, q > 0.0)
    for arm in arms:
        print(f"{arm}: masks other than the realizable plan's own {moved[arm]} of 3000")
    bad = moved[arms[3]] != 0 or moved[arms[4]] == 0
    print(f"identity arm moved, or its perturbation moved nothing {int(bad)}")
    return 1 if bad else 0


_SOLVE_INSTALLS = {"duty1.1": (False, 1.1), "duty0": (False, 0.0), "clamp1.5": (True, 1.5), "fixed5.5": (True, 5.5)}


def _generated_cells(seed: int, count: int):
    """The design review's solve generator (``ev/reviewer_solve_props.py`` at 04e5bcfca3): each
    cell's installation, price, extras and outdoor mean, with its own draws."""
    import itertools

    rng = np.random.default_rng(seed)
    prices = {
        "sine": lambda: 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0), "flat": lambda: np.full(96, 1.0),
        "spiky": lambda: np.where(rng.random(96) < 0.2, 4.0, 0.6) - 0.8 * (rng.random(96) < 0.1),
    }
    cells = list(itertools.product(
        _SOLVE_INSTALLS, (0.0, 0.25, 2.0), (False, True), ((0.0, 0.0), (1.0, 0.0), (0.6, 0.9)), (False, True),
        prices, ("none", "caps", "pins_on", "pins_off", "off_steps"), (-4.0, 4.0, 10.0)))
    rng.shuffle(cells)
    done = 0
    for cell in cells:
        if done >= count:
            return
        inst, cost, dhw_on, pair, running, price, extra, out_mean = cell
        if not dhw_on and pair != (0.0, 0.0):
            continue
        done += 1
        clamp, p_min = _SOLVE_INSTALLS[inst]
        params = ThermalParameters()
        params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
        params.min_electrical_power, params.max_electrical_power = p_min, 5.5
        params.dhw_enabled = dhw_on
        cfg = om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost)
        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, (501.0, 300.0)
        outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
        kw = {}
        win = np.zeros(96, bool)
        a = int(rng.integers(0, 80))
        win[a:a + int(rng.integers(1, 12))] = True
        if extra == "caps":
            kw["power_caps_extra"] = np.where(win, float(rng.choice([0.0, 0.6, 1.2, 2.0])), 99.0)
        if extra in ("pins_on", "pins_off"):
            kw["space_pins"] = np.where(win, 1.0 if extra == "pins_on" else 0.0, np.nan)
        if extra == "off_steps":
            kw["off_steps"] = win
        inputs = solve_inputs(
            initial_state=ThermalState(
                room_temperature=20.5, upper_floor_temperature=20.5, lower_floor_temperature=20.5,
                slab_temperature=21.0, outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
                dhw_temperature=45.0, dhw_hours_since_legionella=20.0),
            prices=prices[price](), outdoor_temps=outdoor, start_time=T0, **kw)
        yield cell, om.HeatPumpOptimizer(ThermalModel(params), cfg), replace(inputs, compressor_running=running)


def _stage_calls(solve) -> list[dict]:
    """Each engaged ``_commit_runs`` call of ``solve()``: the shipped plan's
    score; with two relaxed plans, the same call's with the first alone; and
    with a realizable first relaxed plan, its gain and clip distance."""
    from heatpump_optimizer import runs

    kept, calls = om._commit_runs, []

    def spy(opt, h, scope, relaxed, dhw, maxiter, rescope=None):
        before = opt._space_avail
        plan, shipped = kept(opt, h, scope, relaxed, dhw, maxiter, rescope)
        if not om._engaged(opt):
            return plan, shipped
        after, args = opt._space_avail, (() if dhw is None else (dhw,))
        row = {"score": float(shipped[1](plan, *args))}
        if len(relaxed) > 1:
            opt._space_avail = before
            alone, alone_scope = kept(opt, h, scope, relaxed[:1], dhw, maxiter, rescope)
            row["alone"] = float(alone_scope[1](alone, *args))
        lo, hi, other, _ = om._stage_box(opt, shipped[0], dhw)
        if runs.realizable(relaxed[0] + other, runs.floor_kw(opt.model.params.min_electrical_power)):
            clipped = np.clip(relaxed[0], lo, hi)
            row["realizable"] = {
                "changed": not np.array_equal(plan, relaxed[0]), "priced": opt.config.cycling_cost > 0,
                "gain": float(shipped[1](clipped, *args)) - row["score"],
                "clip_kw": float(np.max(np.abs(clipped - relaxed[0]))),
                "edges": (edges(relaxed[0] + other), edges(plan + other)),
            }
        opt._space_avail = after
        calls.append(row)
        return plan, shipped

    om._commit_runs = spy
    try:
        solve()
    finally:
        om._commit_runs = kept
    return calls


def stage() -> int:
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 140
    if not hasattr(om, "_commit_runs"):
        print("this tree has no candidate stage: nothing to read")
        return 0
    bad = 0
    sets = {
        "descents cells": [
            (f"{name} price phase {phase} outdoor {out_mean}",
             lambda c=clamp, p=p_min, ph=phase, o=out_mean: _switch_solve(c, p, PAIR, "both", ph, o))
            for name, clamp, p_min in INSTALLS for phase, out_mean in DAYS],
        f"generated cells, seed {seed}": [
            (str(cell), lambda o=opt, i=inputs: o.optimize(inputs=i)) for cell, opt, inputs in _generated_cells(seed, count)],
    }
    for label, cells in sets.items():
        two, real = {"below": 0, "equal": 0, "above": 0}, []
        engaged = 0
        for name, solve in cells:
            for row in _stage_calls(solve):
                engaged += 1
                if "alone" in row:
                    gap = row["score"] - row["alone"]
                    two["below" if gap < -1e-9 else "above" if gap > 1e-9 else "equal"] += 1
                if "realizable" in row:
                    real.append((name, row["realizable"]))
        changed = [(n, r) for n, r in real if r["changed"]]
        print(f"{label}: {len(cells)} solves, {engaged} engaged stage calls; with two relaxed plans, both"
              f" against the first alone: {sum(two.values())} calls, below {two['below']}, equal {two['equal']},"
              f" above {two['above']}")
        print(f"{label}: a realizable first relaxed plan in {len(real)} calls, shipped changed {len(changed)}"
              f" ({sum(r['priced'] for _, r in changed)} pricing a start), unchanged {len(real) - len(changed)}"
              f" ({sum(r['priced'] for n, r in real if not r['changed'])} pricing a start)")
        for name, r in changed:
            print(f"  {name}: priced {r['priced']}, gain {r['gain']:.4f} against the relaxed plan clipped"
                  f" {r['clip_kw']:.3f} kW into the shipped scope's box, edges {r['edges'][0]} to {r['edges'][1]}")
        bad += two["above"] + sum(r["gain"] < -1e-9 for _, r in changed)
    print(f"calls whose two plans scored above the first alone, or a changed realizable plan scored above it {bad}")
    return 1 if bad else 0


KERNELS = ("SkylakeX", "Haswell", "Sandybridge", "Nehalem")
_BLOCK = 'R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")'
# The block that follows this group's in tests/features.py; the block runs up to it.
_NEXT = "# --- R10-START-COUNTER-EDGES: the start counter fed from running-signal edges ---"
_BLOCKS = (
    ("duty-switch block", ("from types import SimpleNamespace as _DspNS", _BLOCK)),
    ("starts-and-runs block", (_BLOCK, _NEXT)),
)
# Run as a prelude inside the features namespace: wraps ``R.check``.
_KERNEL_PROBE = r'''
import sys as _kp_sys
_kp_check = R.check
def _kp_probe(name, cond, detail="", _real=_kp_check):
    g = _kp_sys._getframe(1).f_globals
    if name.startswith("acceptance"):
        print("ACCEPT", bool(cond), "|", name, "|", detail, flush=True)
    if name.startswith("acceptance: priced on the contributor's table"):
        old_w, new_w = g["_dsp_accept_starts"]["modulating clamped"]
        print("REPLACED", bool(new_w <= old_w + 1e-9), "| modulating clamped, switch weight in starts,"
              " priced no higher than unpriced |", f"unpriced {old_w:g}, priced {new_w:g}", flush=True)
    if name.startswith("acceptance: a priced plan holds no more starts"):
        cells = {k: v for k, v in g["_hsr_engaged"].items() if k[0] > 0 and not k[1]}
        kwh = {k: float(g["np"].sum(v.space - v.relaxed[-1])) * 0.25 for k, v in cells.items()}
        step = {k: g["_hsr_runs"].floor_kw(k[2]) * 0.25 for k in cells}
        count, free = g["_hsr_count"], {k: g["_hsr_solve"](0.0, False, k[2]).space for k in cells}
        print("KEPT", all(count(v.space, k[2]) <= count(free[k], k[2]) + 1e-9 for k, v in cells.items()),
              "| priced starts no higher than the unpriced plan's by the same count |",
              "; ".join(f"floor {k[2]} kW: {count(v.space, k[2]):g} against {count(free[k], k[2]):.2f}"
                        for k, v in cells.items()), flush=True)
        print("REPLACED", all(abs(kwh[k]) <= step[k] + 1e-9 for k in cells),
              "| shipped energy within one floor step of the relaxed plan's |",
              "; ".join(f"floor {k[2]} kW: {kwh[k]:+.4f} kWh against a step of {step[k]:.4f}" for k in cells),
              flush=True)
    return _real(name, cond, detail)
R.check = _kp_probe
'''


def _kernel_blocks(kernel: str) -> list[tuple[str, int, list[str]]]:
    env = dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE=kernel, R11_HSR_KERNEL_PROBE=_KERNEL_PROBE,
               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    out = []
    with open("tests/features.py", encoding="utf-8") as fh:
        present = fh.read()
    for label, markers in _BLOCKS:
        markers = tuple(m for m in markers if m in present)  # a tree before the next block holds no _NEXT
        run = subprocess.run(
            [sys.executable, "tools/audit/seat/features_block.py",
             "--prelude", 'import os as _kp_os; exec(_kp_os.environ["R11_HSR_KERNEL_PROBE"])', *markers],
            env=env, capture_output=True, text=True)
        lines = (run.stdout + run.stderr).splitlines()
        out.append((label, run.returncode, [
            ln for ln in lines if ln.startswith(("ACCEPT ", "KEPT ", "REPLACED ")) or "FEATURES BLOCK" in ln]))
    return out


def kernels() -> int:
    names = tuple(sys.argv[2:]) or KERNELS
    with ThreadPoolExecutor(max(1, min(len(names), os.cpu_count() or 1))) as pool:
        results = list(pool.map(_kernel_blocks, names))
    bad = 0
    for kernel, blocks in zip(names, results):
        for label, rc, lines in blocks:
            done = any("FEATURES BLOCK" in ln for ln in lines)
            print(f"{kernel}, {label}: " + (
                f"exit {rc}" if done else f"did not complete (exit {rc}): not runnable on this processor, or the block raised"))
            for ln in lines:
                print("  " + ln)
            bad += not done or rc != 0
    print(f"kernels {', '.join(names)}: blocks that failed a check or did not complete {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit({"fixtures": fixtures, "c1": c1, "descents": descents, "grid": grid, "defaults": defaults, "gradient": gradient,
              "stress": stress_cost, "kernels": kernels,
              "identity": identity, "stage": stage}[sys.argv[1]]())
