"""R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges shipped as runs, measured on one tree.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r11_honest_dhw_runs.py fixtures|stores|hysteresis|kernel|tail|combi|seconds

Synthetic throughout; no private data. The finding, the store program and
the tail are outside pull request 3529's (Bankaifan), which has no finder
harness; this one prints what the commit stage
(``dhw_planner.commit_charges``) does to the plans the group's design note
reads. Nothing here asserts; ``tests/features.py``'s block of the same name
does.

``fixtures``: the two golden plan scenarios that price a start
(``cycling_cost``, ``everything_on``), each solved as the tree solves it and
with the planner handed no ``ChargeRuns`` (the uncommitted plan, what the
tree shipped before the commit stage). Per solve: hot-water charges, steps
between the running rule and the floor (all, and those that are not a
charge's last step), the same for the combined draw, the worst gap under
the requirement, the start count of the combined draw and of the hot-water
plan alone, the published starts, energy and ``predicted_cost``. Per build
of the committed solve: whether a space plan was known, the program's
rounds beside ``STARTABLE_ROUNDS``, each candidate with the clause that
refused it or its ranked cost, and which shipped. On a tree without the
commit stage the two solves are one and the per-build lines are absent.

``stores``: the planner's linear store against its walk (the simulation)
along each build's uncommitted plan, on the same two fixtures: the largest
difference in kelvin, which ``_STORE_MARGIN_K`` is sized against.

``hysteresis``: the two fixtures with a start hysteresis injected at ten
values from 0.5 to 10 K (no golden sets one). Per cell and build: the
program's rounds, the candidates' verdicts, and how many charges
``drop_unstartable`` removes from what shipped (the acceptance's start
clause read back; 0 where it held).

``kernel``: a sha1 over ``runs.commit``'s masks and band verdicts on 1200
random cases, which a tree before the kernel was generalised prints too: the
two digests are what the change must not move. Then, on a tree with
``runs.advance``, the kernel on an affine store with hard bounds and two
levels against an exhaustive search over nine steps, at 800, 400, 100 and
20 cells, and the same search with the bounds ignored (the null).

``tail``: starts with a charge's tail allowed against refused on the three
installs of ``r11_honest_starts_runs.py`` and the combi fixture. Allowed
means the planner is told the install can end a run inside a step; the
optimizer's own projection is left as it is, so on a clamped install a tail
the planner writes is raised to the floor when it ships. Per cell: hot-water
steps under the floor as planned and as shipped, starts of the combined
draw, energy and the worst gap under the requirement.

``combi``: the exchange on the combi fixture with a start priced, an install
that cannot duty-cycle, and neither (the null): rounds, committed builds,
whether the committed build shipped, steps under the floor and the worst
gap under the requirement.

``seconds``: CPU seconds (``time.process_time``) of the two fixtures' solves,
the least of five, as the tree solves them and with the planner handed no
``ChargeRuns``; on a tree without the commit stage the one arm. The second
arm on this tree against the one arm on the base tree is the noise this box
puts on the difference.
"""
from __future__ import annotations

import hashlib
import sys
import time
from dataclasses import replace
from datetime import datetime
from types import SimpleNamespace

import numpy as np

import heatpump_optimizer.dhw_planner as dp
import heatpump_optimizer.optimizer as om
from heatpump_optimizer import runs
from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW, ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs

FIXTURES = ("cycling_cost", "everything_on")
HAS_STAGE = hasattr(dp, "commit_charges")


def low(plan, floor: float) -> tuple[int, int]:
    """Steps between the running rule and the floor: all, and not a run's last."""
    plan = np.asarray(plan, float)
    under = (plan > MIN_RUNNING_DRAW_KW) & (plan < floor - 1e-9)
    last = np.r_[plan[1:] <= 0.0, True] & np.r_[False, plan[:-1] >= floor - 1e-9]
    return int(under.sum()), int(np.sum(under & ~last))


def charges(plan) -> int:
    on = np.asarray(plan, float) > 0.0
    return int(np.sum(on & ~np.r_[False, on[:-1]]))


class Watch:
    """Records every ``commit_charges`` call of the solves run inside it."""

    def __init__(self, committed: bool = True, tails: bool | None = None, hysteresis_k: float | None = None):
        self.committed, self.tails, self.hysteresis_k = committed, tails, hysteresis_k
        self.builds: list[dict] = []
        self.opt = None

    def __enter__(self):
        self.kept = {"solve": om.HeatPumpOptimizer.optimize}
        watch = self

        def solve(opt, *, inputs):
            watch.opt = opt
            if watch.hysteresis_k is not None:
                inputs = replace(inputs, state=replace(inputs.state, dhw_start_hysteresis_k=watch.hysteresis_k))
            return watch.kept["solve"](opt, inputs=inputs)

        om.HeatPumpOptimizer.optimize = solve
        if not HAS_STAGE:
            return self
        self.kept.update(runs_arg=om._charge_runs, stage=dp.commit_charges, refusal=dp.charge_refusal,
                         plan=dp._StoreProgram.plan)

        def runs_arg(opt, running):
            got = watch.kept["runs_arg"](opt, running)
            if got is None or not watch.committed:
                return None
            return got if watch.tails is None else got._replace(clamped=not watch.tails)

        def stage(planner, plan, store, limits, forced_off, start_below, space_demand):
            if planner.charge_runs is None:
                return watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand)
            build = {"space": space_demand is not None, "rounds": 0, "verdicts": [], "plan": np.array(plan)}
            watch.builds.append(build)
            ctx = store[0]
            build["temps_of"] = lambda x: planner._ctx_temps(ctx, store[1], store[2], np.asarray(x, float))
            build["start_below"], build["requirement"], build["store"] = start_below, limits[0], store
            floor = runs.floor_kw(planner.model.params.min_electrical_power)
            space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)
            build["cost"] = lambda x: float(np.sum(ctx.prices * x) * ctx.dt) + planner.charge_runs.start_cost * (
                runs.start_count(space + x, floor, planner.charge_runs.running))
            out = watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand)
            build["out"] = np.array(out)
            return out

        def refusal(candidate, start_below, temps_of, held):
            got = watch.kept["refusal"](candidate, start_below, temps_of, held)
            if watch.builds:
                watch.builds[-1]["verdicts"].append((np.array(candidate), got))
            return got

        def plan(program, may_start):
            if watch.builds:
                watch.builds[-1]["rounds"] += 1
                watch.builds[-1]["program"] = program
            return watch.kept["plan"](program, may_start)

        om._charge_runs, dp.commit_charges, dp.charge_refusal, dp._StoreProgram.plan = runs_arg, stage, refusal, plan
        return self

    def __exit__(self, *exc):
        om.HeatPumpOptimizer.optimize = self.kept["solve"]
        if HAS_STAGE:
            om._charge_runs, dp.commit_charges = self.kept["runs_arg"], self.kept["stage"]
            dp.charge_refusal, dp._StoreProgram.plan = self.kept["refusal"], self.kept["plan"]


def solve_line(label: str, got, opt, floor: float = 1.0) -> None:
    space, dhw = np.asarray(got["power_schedule"], float), np.asarray(got["dhw_power_schedule"], float)
    gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(got["dhw_temp_trajectory"], float)[1:]))
    print(f"{label}: charges {charges(dhw)}, hot-water steps under the floor {low(dhw, floor)[0]}"
          f" (not a charge's last {low(dhw, floor)[1]}), combined {low(space + dhw, floor)[0]}"
          f" ({low(space + dhw, floor)[1]}), worst gap {gap:.3f} K,"
          f" start count combined {runs.start_count(space + dhw, floor):.2f} hot water alone"
          f" {runs.start_count(dhw, floor):.2f}, published starts {got['compressor_starts']},"
          f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f}, predicted_cost {got['predicted_cost']:.2f}")


def build_lines(builds: list[dict]) -> None:
    for i, b in enumerate(builds):
        if "out" not in b:
            continue
        shipped = "the uncommitted plan" if np.array_equal(b["out"], b["plan"]) else "a committed plan"
        print(f"  build {i}: space plan known {b['space']}, uncommitted charges {charges(b['plan'])}"
              f" under the floor {low(b['plan'], 1.0)[0]}, program rounds {b['rounds']} of {dp.STARTABLE_ROUNDS},"
              f" shipped {shipped} at ranked cost {b['cost'](b['out']):.4f}"
              f" (the uncommitted plan's {b['cost'](b['plan']):.4f})")
        for candidate, verdict in b["verdicts"]:
            kind = "lifted" if np.array_equal(candidate > 0, b["plan"] > 0) else "program"
            print(f"    {kind} candidate, charges {charges(candidate)}:"
                  f" {'accepted, ranked cost %.4f' % b['cost'](candidate) if verdict is None else 'refused %s at step %d' % verdict}")


def fixtures() -> int:
    import golden

    for name in FIXTURES:
        for committed in (True, False) if HAS_STAGE else (True,):
            with Watch(committed) as w:
                got = golden.capture(name, golden.SCENARIOS[name])
            solve_line(f"{name} {'committed' if committed and HAS_STAGE else 'uncommitted'}", got, w.opt)
            build_lines(w.builds)
    return 0


def stores() -> int:
    import golden

    if not HAS_STAGE:
        print("this tree has no commit stage: no store program to compare")
        return 0
    for name in FIXTURES:
        with Watch() as w:
            golden.capture(name, golden.SCENARIOS[name])
        for i, b in enumerate(w.builds):
            if "program" not in b:
                continue
            program, (ctx, initial, draws) = b["program"], b["store"]
            for label, plan in (("uncommitted", b["plan"]), ("shipped", b["out"])):
                at, line = np.array([initial]), [initial]
                for k in range(ctx.n_steps):
                    at = ctx.coast(draws, k, at) + (program._rise(k, at, plan[k]) if plan[k] > 0 else 0.0)
                    line.append(float(at[0]))
                print(f"{name} build {i} {label} plan: linear store less walk, largest"
                      f" {float(np.max(np.abs(np.array(line) - b['temps_of'](plan)))):.4f} K"
                      f" (margin {dp._STORE_MARGIN_K} K)")
    return 0


def hysteresis() -> int:
    import golden

    if not HAS_STAGE:
        print("this tree has no commit stage")
        return 0
    for name in FIXTURES:
        for k in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0):
            with Watch(hysteresis_k=k) as w:
                got = golden.capture(name, golden.SCENARIOS[name])
            dhw = np.asarray(got["dhw_power_schedule"], float)
            print(f"{name} hysteresis {k} K: shipped steps under the floor not a charge's last {low(dhw, 1.0)[1]}")
            for i, b in enumerate(w.builds):
                if "out" not in b:
                    continue
                lost = 0
                if b["start_below"] is not None:
                    kept = dp.drop_unstartable(b["out"], b["start_below"], b["temps_of"])
                    lost = charges(b["out"]) - charges(kept)
                verdicts = ", ".join("accepted" if v is None else f"{v[0]}@{v[1]}" for _c, v in b["verdicts"])
                shipped = "uncommitted" if np.array_equal(b["out"], b["plan"]) else "committed"
                print(f"  build {i}: start condition known {b['start_below'] is not None}, rounds {b['rounds']},"
                      f" verdicts [{verdicts}], shipped {shipped}, charges drop_unstartable removes from it {lost}")
    return 0


def _small(seed: int, cells: int, bounds: bool = True) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n, heats, decay, top = 9, (1.0, 2.5), 0.97, 20.0
    price, drift = rng.uniform(0.5, 2.0, n), rng.uniform(-1.5, -0.2, n)
    floors, ceiling = rng.uniform(2.0, 6.0, n), float(rng.uniform(9.0, 13.0))
    start, first = float(rng.choice([0.0, 0.7])), float(rng.uniform(6.0, 9.0))
    width = top / cells

    def place(k):
        def rule(v, _charged):
            j = np.rint(v / width).astype(np.int64)
            inside = (v >= floors[k]) & (v <= ceiling) & (j >= 0) & (j <= cells)
            return np.clip(j, 0, cells), np.where(inside, 0.0, np.inf)
        return rule

    cost = np.full((2, cells + 1), np.inf)
    val = np.zeros_like(cost)
    cost[1, int(round(first / width))], val[1, int(round(first / width))] = 0.0, first
    for k in range(n):
        actions = ([lambda v, _r, h=h, k=k: (decay * v + drift[k] + h, price[k] * h) for h in heats],
                   [lambda v, _r, k=k: (decay * v + drift[k], 0.0)])
        cost, val, _back = runs.advance(cost, val, runs.moves(1, 1, np.nan), actions, start, place(k), 1)
    grid = np.indices((3,) * n).reshape(n, -1).T
    v, paid = np.full(len(grid), first), np.zeros(len(grid))
    ok, was = np.ones(len(grid), dtype=bool), np.zeros(len(grid), dtype=bool)
    for k in range(n):
        on = grid[:, k] > 0
        heat = np.where(on, np.take(heats, np.maximum(grid[:, k] - 1, 0)), 0.0)
        v = decay * v + drift[k] + heat
        paid += price[k] * heat + start * (on & ~was)
        if bounds:
            ok &= (v >= floors[k]) & (v <= ceiling)
        was = on
    return float(np.min(np.where(ok, paid, np.inf))), float(np.min(cost))


def kernel() -> int:
    rng = np.random.default_rng(7)
    digest, cases = hashlib.sha1(), 1200
    for _ in range(cases):
        n, dt = int(rng.integers(4, 60)), float(rng.choice([1 / 12, 0.25, 0.5]))
        floor = float(rng.choice([0.5, 1.0, 1.8]))
        q = np.where(rng.random(n) < 0.4, 0.0, rng.uniform(0.05, 3.0, n))
        prices, caps = rng.uniform(0.05, 0.6, n), np.where(rng.random(n) < 0.1, floor * 0.5, 4.0)
        forced = np.where(rng.random(n) < 0.1, rng.integers(0, 2, n).astype(float), np.nan)
        mask, tracked = runs.commit(
            q, prices, floor, caps, float(rng.choice([0.0, 0.3, 1.5])), int(rng.choice(runs.BANDS)), dt=dt,
            running=bool(rng.integers(0, 2)), forced=forced,
            lengths=(runs.steps_at_least(runs.MIN_RUN, dt), runs.steps_at_least(runs.MIN_PAUSE, dt)))
        digest.update(np.packbits(mask).tobytes() + bytes([tracked]))
    print(f"runs.commit over {cases} random cases: sha1 {digest.hexdigest()}")
    if not hasattr(runs, "advance"):
        print("this tree has no runs.advance: no generalised kernel to compare")
        return 0
    for cells in (800, 400, 100, 20):
        rows = [_small(s, cells) for s in range(60)]
        live = [(b, c) for b, c in rows if np.isfinite(b)]
        print(f"{cells} cells: kernel cost equals the exhaustive search's on"
              f" {sum(abs(b - c) <= 1e-9 for b, c in live)} of {len(live)} feasible cases (60 drawn),"
              f" beats it on {sum(c < b - 1e-9 for b, c in live)}, finds no plan on {sum(not np.isfinite(c) for _b, c in live)}")
    null = [_small(s, 800, bounds=False) for s in range(60)]
    print(f"null, the search with the bounds ignored: cheaper than the kernel on"
          f" {sum(b < c - 1e-9 for b, c in null)} of 60, equal on {sum(abs(b - c) <= 1e-9 for b, c in null)}")
    return 0


def _install_solve(clamp: bool, p_min: float, watch: Watch):
    params = ThermalParameters()
    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
    params.dhw_enabled = True
    opt = om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=0.3))
    steps = np.arange(96)
    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (steps - 50) / 96.0)
    with watch:
        res = opt.optimize(inputs=solve_inputs(
            initial_state=ThermalState(
                room_temperature=20.5, upper_floor_temperature=20.5, lower_floor_temperature=20.5,
                slab_temperature=21.0, outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
                dhw_temperature=45.0, dhw_hours_since_legionella=20.0),
            prices=1.3 + 0.9 * np.sin(2 * np.pi * (steps - 30) / 96.0), outdoor_temps=outdoor,
            start_time=datetime(2026, 1, 10)))
    return opt, res


def _tail_line(label: str, opt, res, watch: Watch, floor: float) -> None:
    space, dhw = np.asarray(res.power_schedule, float), np.asarray(res.dhw_power_schedule, float)
    gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(res.dhw_temp_trajectory, float)[1:]))
    planned = [b["out"] for b in watch.builds if "out" in b]
    print(f"{label}: hot-water steps under the floor as planned"
          f" {low(planned[-1], floor)[0] if planned else 'n/a'} as shipped {low(dhw, floor)[0]},"
          f" start count combined {runs.start_count(space + dhw, floor):.2f},"
          f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f}, worst gap {gap:.3f} K")


def tail() -> int:
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    import r11_honest_starts_runs as hsr

    if not HAS_STAGE:
        print("this tree has no commit stage")
        return 0
    for name, clamp, p_min in hsr.INSTALLS:
        for tails in (False, True):
            watch = Watch(tails=tails)
            opt, res = _install_solve(clamp, p_min, watch)
            _tail_line(f"{name} (clamped {clamp}, floor {p_min}) tail {'allowed' if tails else 'refused'}",
                       opt, res, watch, runs.floor_kw(p_min))
    for tails in (False, True):
        watch = Watch(tails=tails)
        opt, res, _calls = _combi_solve(0.0, True, watch)
        _tail_line(f"combi fixture (clamped True) tail {'allowed' if tails else 'refused'}", opt, res, watch, 1.0)
    return 0


def _combi_solve(cost: float, clamp: bool, watch: Watch | None = None):
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    import r10_combi_tank as ct

    opt = ct.opt_for(ct.params())
    opt.config = replace(opt.config, cycling_cost=cost, clamp_planned_levels=clamp)
    real, build, calls = om._combi_flux_exchange, dp.DhwPlanner._build_dhw_requirements, []

    def exchange(o, h, planner, *rest):
        builds = []

        def counted(self, *a, **k):
            got = build(self, *a, **k)
            builds.append((getattr(self, "charge_runs", None) is not None, np.array(got[0].schedule)))
            return got

        dp.DhwPlanner._build_dhw_requirements = counted
        try:
            out = real(o, h, planner, *rest)
        finally:
            dp.DhwPlanner._build_dhw_requirements = build
        calls.append(SimpleNamespace(builds=builds, out=np.array(out)))
        return out

    om._combi_flux_exchange = exchange
    prices = np.where((np.arange(96) // 4) % 24 < 6, 0.5, 2.0)
    try:
        with watch or Watch():
            res = opt.optimize(inputs=solve_inputs(
                initial_state=ct.state(50.0), prices=prices, outdoor_temps=np.full(96, 0.0),
                wind_speeds=np.zeros(96), precipitation=np.zeros(96), solar_radiation=np.zeros(96),
                start_time=datetime(2026, 1, 15)))
    finally:
        om._combi_flux_exchange = real
    return opt, res, calls


def combi() -> int:
    for label, cost, clamp in (("a start priced", 0.5, False), ("cannot duty-cycle", 0.0, True), ("null, unengaged", 0.0, False)):
        opt, res, calls = _combi_solve(cost, clamp)
        last = calls[-1]
        rounds = [s for c, s in last.builds if not c]
        commits = [s for c, s in last.builds if c]
        if not HAS_STAGE:  # every build is the one planner's, and none commits
            rounds, commits = [s for _c, s in last.builds], []
        dhw, space = np.asarray(res.dhw_power_schedule, float), np.asarray(res.power_schedule, float)
        gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(res.dhw_temp_trajectory, float)[1:]))
        print(f"combi, {label}: rounds {len(rounds)}, committed builds {len(commits)},"
              f" committed build shipped {bool(commits) and np.array_equal(commits[-1], last.out)},"
              f" hot-water steps under the floor {low(dhw, 1.0)[0]} (not a charge's last {low(dhw, 1.0)[1]}),"
              f" combined {low(space + dhw, 1.0)[0]}, worst gap {gap:.3f} K, dhw_kwh {float(dhw.sum()) * 0.25:.2f}")
    return 0


def seconds() -> int:
    import golden

    for name in FIXTURES:
        for committed in (True, False) if HAS_STAGE else (False,):
            took = []
            for _ in range(5):
                with Watch(committed):
                    t0 = time.process_time()
                    golden.capture(name, golden.SCENARIOS[name])
                    took.append(time.process_time() - t0)
            print(f"{name} {'committed' if committed else 'uncommitted'}: {min(took):.2f} CPU s (least of 5)")
    return 0


ARMS = {"seconds": seconds, "fixtures": fixtures, "stores": stores, "hysteresis": hysteresis, "kernel": kernel, "tail": tail, "combi": combi}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ARMS:
        sys.exit(f"usage: r11_honest_dhw_runs.py {'|'.join(ARMS)}")
    sys.exit(ARMS[sys.argv[1]]())
