#!/usr/bin/env python3
"""Read decision 0018's `regret` term: the same-information oracle per grid cell, the cost record per install-day.

Usage: python3 -I tools/audit/regret_oracle.py grid [--plane price-weather|all] [--cells C,...] [--plant-error X]
                                                    [--days N] [--jobs N] [--repo DIR]
       python3 -I tools/audit/regret_oracle.py installs [--bundle LABEL=PATH ...] [--repo DIR]
       python3 -I tools/audit/regret_oracle.py --self-test
  grid      universe `enumerate.py d0-grid` (default `--plane price-weather`, its cells run at PLANE_LEVELS; `all`
            names every level of the cell). Per cell, `C_real` is the integration's loop (`tests/rolling.py`
            `run_rolling`'s shape: the optimizer on its configured model, re-planned every REPLAN_H, each step
            applied to the plant), costed as the energy it commanded times the price. `C_model` is each executed
            step's booked cost, read off the plan that executed it. `C_same` is the least cost among the
            candidates given the same information, each costed on the same prices and held to the executed
            plan's own bound violation on the plant (comfort floor and ceiling, the hot-water minimum in its
            windows and the tank rating) and to the pump's 0..max_electrical_power: the executed plan; the same
            loop with the optimizer given the plant's parameters; and `tests/optimality.py`'s two challengers on
            the executed space-heating series (the same energy moved greedily to the cheapest steps, and
            energy-preserving perturbations), which are open-loop and so also may not end the window with less
            heat stored than the executed plan left (room, slab, zones, tank). The row names the winner. The
            loop's forecast is the realised series, so `C_fore` equals `C_same` and the floor prints 0 with that
            reason. `regret = C_real - C_same` is a lower bound and never negative: the executed plan is a
            candidate. `--plant-error` scales the plant's heat loss against the model (1.0: the plant is the
            model; learning is off in every loop). A cell whose plant level no loop models prints NO-READ.
  installs  universe `enumerate.py d15-installs`. Per install given a bundle (`hpo-debug/1`), `C_real` is the
            energy store's `total_cost` (NO-READ when the store counts from before the bundle's window), beside
            the metered power times the price over the window as the cross-check; `C_model` is the accuracy
            store's day-ahead promise cost summed over the window's local dates; the model gap is beside both.
            `C_same` prints NO-READ, never a number, with the reason the tree gives (NO_SAME_INFORMATION).
Each model gap is judged against `thresholds.band_model_gap` times that cell's `C_real`; `undecided` while the
owner's value is null. Stdout: every universe item with its read, a MEAN line (each mean with two standard
errors of its cells), then `RESULT read=regret universe=N examined=n ...`; exit 0. A missing or empty
universe source, an unreadable bundle or an unknown --cells item exits 2 with no RESULT line.
Null control: --self-test runs the design's controls (design/R11-PRE-PRODUCT-READS section 6): a plant leakier
in the model than in fact on non-flat prices reads regret above two standard errors; the plant equal to the
model, and a flat price, read 0; a bundle with its metered power scaled moves `C_real` and the gap while the
unscaled bundle reads the same gap twice; `C_same` per install-day is NO-READ in both; an emptied universe
source exits 2 with no RESULT. It prints `SELF-TEST passed (N arms)` or names the failing arm and exits 1.
"""
import argparse, ast, concurrent.futures, contextlib, io, json, math, os, shutil, subprocess, sys, tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enumerate as census  # noqa: E402  (tools/audit/enumerate.py, the universes and their refusals)

# The plane's cells run at these levels of the axes `--plane price-weather` folds (run_rolling's defaults).
PLANE_LEVELS = ("single-zone", "dhw", "plain", "24h")
LOOP_PLANTS = ("plain",)  # the plant levels the loop models; any other prints NO-READ
REPLAN_H = 2.0  # tests/rolling.py's REPLAN_HOURS
START = datetime(2026, 1, 15)  # tests/rolling.py's START
PERTURB_TRIES, PERTURB_SEED = 300, 0
EPS = 1e-9  # a candidate wins only below the incumbent by more than float noise
VIOL_TOL = 1e-6  # degree-hours: optimality.py's own comfort tolerance
NO_SAME_INFORMATION = "no code identifies the measured house from a window"
REPLAY_DOC = "custom_components/heatpump_optimizer/replay_doc.py"


class Refuse(Exception):
    pass


def universe(repo, name, **kw):
    try:
        return census.run(name, repo, **kw)
    except census.Refuse as e:
        raise Refuse(str(e))


def band(repo):
    """thresholds.band_model_gap's owner value, or None while it is unset."""
    t = json.loads((Path(repo) / census.OBJECTIVE).read_text()).get("thresholds", {}).get("band_model_gap", {})
    return t.get("value")


def judge_gap(gap, c_real, share):
    if share is None:
        return "undecided (thresholds.band_model_gap is null)"
    return "inside" if gap <= share * abs(c_real) else "outside"


def mean_2se(xs):
    n = len(xs)
    m = sum(xs) / n if n else 0.0
    if n < 2:
        return m, float("nan")
    return m, 2 * math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1) / n)


# --------------------------------------------------------------------------------------------------- grid

def _paths(repo):
    repo = Path(repo).resolve()
    for p in (repo / "tests" / "hastub", repo / "tests", repo / "custom_components"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


def cell_levels(cell):
    parts = cell.split("/")
    if len(parts) == 2:
        parts += list(PLANE_LEVELS)
    if len(parts) != 6 or not parts[5].endswith("h"):
        raise Refuse(f"{cell!r} is no d0-grid cell")
    return dict(price=parts[0], weather=parts[1], two_zone=parts[2] == "two-zone", dhw=parts[3] == "dhw",
                plant=parts[4], horizon_h=int(parts[5][:-1]))


class Loop:
    """One cell's plant, prices and weather; `closed()` runs the integration's loop on a given model."""

    def __init__(self, repo, lv, plant_error, days):
        _paths(repo)
        import numpy as np
        from profiles import DT, house, prices, weather
        from heatpump_optimizer.optimizer import OptimizationConfig
        from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
        self.np, self.DT, self.lv = np, DT, lv
        self.cfg = house(two_zone=lv["two_zone"], dhw=lv["dhw"])

        def params(scale):
            p = ThermalParameters.from_config(self.cfg)
            p.dhw_enabled = lv["dhw"]
            p.heat_loss_coefficient *= scale
            p.upper_floor_heat_loss *= scale
            p.lower_floor_heat_loss *= scale
            return p
        self.params, self.ThermalModel = params, ThermalModel
        self.plant = ThermalModel(params(plant_error))
        self.opt_cfg = OptimizationConfig(horizon_hours=lv["horizon_h"], time_step_minutes=15,
                                          target_temp=self.cfg["target_temperature"],
                                          min_temp=self.cfg["min_temperature"], max_temp=self.cfg["max_temperature"])
        self.T, self.H = int(days * 24 / DT), int(lv["horizon_h"] / DT)
        span = self.T + self.H + 4

        def tile(a):
            a = np.asarray(a, dtype=float)
            return np.tile(a, int(np.ceil(span / len(a))))[:span]
        self.price = tile(prices(lv["price"], START))
        self.out, self.wind, self.rain, self.solar = (tile(a) for a in weather(lv["weather"], START))
        self.WS, self.TS = WeatherSeries, ThermalState
        t0 = self.cfg["target_temperature"]
        self.s0 = ThermalState(room_temperature=t0, slab_temperature=t0 + 1.0, outdoor_temperature=float(self.out[0]),
                               upper_floor_temperature=t0, lower_floor_temperature=t0, dhw_temperature=52.0,
                               dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
        self.pmax = float(self.plant.params.max_electrical_power)
        when = [START + timedelta(hours=(i + 1) * DT) for i in range(self.T)]
        bounds = [self.opt_cfg.get_temp_bounds(w.hour + w.minute / 60.0, w) for w in when]
        self.lo, self.hi = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
        if lv["dhw"]:
            from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
            win = parse_windows(self.cfg.get("dhw_windows", "") or "")
            self.inside = np.array([hour_in_windows(w.hour + w.minute / 60.0, win) for w in when])

    def weather(self, a, b):
        return self.WS(outdoor_temps=self.out[a:b], wind_speeds=self.wind[a:b], precipitation=self.rain[a:b],
                       solar_radiation=self.solar[a:b])

    def simulate(self, state, space, dhw, a, b):
        np = self.np
        if self.lv["dhw"]:
            room, slab, up, low, tank, _, _ = self.plant.simulate_trajectory_with_dhw(
                initial_state=state, space_power_schedule=np.asarray(space, dtype=float),
                dhw_power_schedule=np.asarray(dhw, dtype=float), weather=self.weather(a, b),
                start_hour=(START + timedelta(hours=a * self.DT)).hour + (START + timedelta(hours=a * self.DT)).minute / 60.0,
                dt_hours=self.DT)
        else:
            room, slab, up, low, _, _, _ = self.plant.simulate_trajectory(
                initial_state=state, power_schedule=np.asarray(space, dtype=float), weather=self.weather(a, b), dt_hours=self.DT)
            tank = [state.dhw_temperature] * (b - a + 1)
        return room, slab, up, low, tank

    def closed(self, model_scale):
        """The integration's loop with the optimizer's model at `model_scale`: (space, dhw, booked cost)."""
        from profiles import solve_inputs
        from heatpump_optimizer.optimizer import HeatPumpOptimizer
        np, DT = self.np, self.DT
        opt = HeatPumpOptimizer(self.ThermalModel(self.params(model_scale)), self.opt_cfg)
        every, state, plan = max(1, int(REPLAN_H / DT)), self.s0, None
        space, dhw, booked = [], [], 0.0
        for k in range(self.T):
            if k % every == 0:
                s = slice(k, k + self.H)
                plan = opt.optimize(inputs=solve_inputs(
                    initial_state=state, prices=self.price[s], outdoor_temps=self.out[s], wind_speeds=self.wind[s],
                    precipitation=self.rain[s], solar_radiation=self.solar[s], start_time=START + timedelta(hours=k * DT)))
            o = k % every
            sp = float(plan.power_schedule[o])
            dp = float(plan.dhw_power_schedule[o]) if plan.dhw_power_schedule else 0.0
            booked += (sp + dp) * DT * float(plan.prices[o])
            room, slab, up, low, tank = self.simulate(state, [sp], [dp], k, k + 1)
            state = self.TS(
                room_temperature=float(room[-1]), slab_temperature=float(slab[-1]), outdoor_temperature=float(self.out[k]),
                upper_floor_temperature=float(up[-1]), lower_floor_temperature=float(low[-1]),
                dhw_temperature=float(tank[-1]), buffer_tank_temperature=state.buffer_tank_temperature,
                wood_tank_temperature=state.wood_tank_temperature,
                dhw_hours_since_legionella=(0.0 if float(tank[-1]) >= self.plant.params.dhw_legionella_temp - 1.0
                                            else (state.dhw_hours_since_legionella or 0.0) + DT))
            space.append(sp)
            dhw.append(dp)
        return np.array(space), np.array(dhw), booked

    def cost(self, space, dhw):
        return float(self.np.sum((space + dhw) * self.price[:self.T] * self.DT))

    def score(self, space, dhw):
        """(bound violation in degree-hours on the plant, the state the window ends in)."""
        np, DT = self.np, self.DT
        room, slab, up, low, tank = self.simulate(self.s0, space, dhw, 0, self.T)
        r = np.minimum(up[1:], low[1:]) if self.lv["two_zone"] else np.asarray(room[1:])
        v = float(np.sum(np.maximum(0.0, self.lo - r)) * DT + np.sum(np.maximum(0.0, r - self.hi)) * DT)
        if self.lv["dhw"]:
            t = np.asarray(tank[1:])
            v += float(np.sum(np.maximum(0.0, self.plant.params.dhw_min_temp - t)[self.inside]) * DT
                       + np.sum(np.maximum(0.0, t - self.plant.params.dhw_hard_max_temp)) * DT)
        return v, tuple(float(x[-1]) for x in (room, slab, up, low, tank))

    def in_limits(self, *series):
        return all(bool(self.np.all((s >= -EPS) & (s <= self.pmax + EPS))) for s in series)

    def admits(self, space, dhw, ref, terminal=True):
        """A candidate is inside the pump's limits and no further outside the bounds than the executed plan
        (`ref`, its `score`); an open-loop one (`terminal`) also ends the window with no less heat stored."""
        v, end = self.score(space, dhw)
        return (self.in_limits(space, dhw) and v <= ref[0] + VIOL_TOL
                and (not terminal or all(e >= e0 - VIOL_TOL for e, e0 in zip(end, ref[1]))))


def greedy(space, price, pmax, np):
    """optimality.py challenger 1: the same energy moved to the cheapest steps, at most pmax each."""
    out, left = np.zeros_like(space), float(space.sum())
    for i in np.argsort(price, kind="stable"):
        take = min(pmax, left)
        out[i], left = take, left - take
        if left <= EPS:
            break
    return out


def perturbed(L, space, dhw, ref):
    """optimality.py challenger 2, energy-preserving: random moves between two steps, each kept only when it
    is cheaper and admitted. Returns (series, cost)."""
    rng, best, best_c = L.np.random.default_rng(PERTURB_SEED), space.copy(), L.cost(space, dhw)
    for _ in range(PERTURB_TRIES):
        i, j = (int(x) for x in rng.integers(0, L.T, 2))
        m = min(float(rng.uniform(0, L.pmax)), best[i], L.pmax - best[j])
        if i == j or m <= 0:
            continue
        c = best.copy()
        c[i] -= m
        c[j] += m
        cc = L.cost(c, dhw)
        if cc < best_c - EPS and L.admits(c, dhw, ref):
            best, best_c = c, cc
    return best, best_c


def read_cell(repo, cell, plant_error, days):
    lv = cell_levels(cell)
    if lv["plant"] not in LOOP_PLANTS:
        return dict(cell=cell, line=f"{cell}\tNO-READ: no plant model for {lv['plant']} in the loop", examined=False)
    L = Loop(repo, lv, plant_error, days)
    space, dhw, booked = L.closed(1.0)
    c_real, ref = L.cost(space, dhw), L.score(space, dhw)
    cands = [("executed", c_real)]
    if plant_error == 1.0:
        same_info = None  # the plant's parameters are the model's: this candidate is the executed loop
    else:
        s2, d2, _ = L.closed(plant_error)
        if L.admits(s2, d2, ref, terminal=False):
            cands.append(("plant-model", L.cost(s2, d2)))
        same_info = "run"
    g = greedy(space, L.price[:L.T], L.pmax, L.np)
    if L.admits(g, dhw, ref):
        cands.append(("greedy", L.cost(g, dhw)))
    best_c = perturbed(L, space, dhw, ref)[1]
    if best_c < c_real - EPS:
        cands.append(("perturbed", best_c))
    winner, c_same = cands[0]
    for name, c in cands[1:]:
        if c < c_same - EPS:
            winner, c_same = name, c
    regret, gap = c_real - c_same, abs(c_real - booked)
    return dict(cell=cell, examined=True, regret=regret, floor=0.0, gap=gap, c_real=c_real,
                line=(f"{cell}\tC_real={c_real:.4f}\tC_model={booked:.4f}\tC_same={c_same:.4f} ({winner} of "
                      f"{','.join(n for n, _ in cands)}{'' if same_info else '; plant-model is the executed loop'})"
                      f"\tC_fore={c_same:.4f}\tregret={regret:.4f}\tfloor=0.0000 (the loop's forecast is the realised series)"
                      f"\tmodel_gap={gap:.4f}"))


def read_grid(repo, plane="price-weather", cells=None, plant_error=1.0, days=1, jobs=1):
    items = universe(repo, "d0-grid", plane=None if plane == "all" else plane)
    if cells:
        unknown = [c for c in cells if c not in items]
        if unknown:
            raise Refuse(f"--cells names no item of d0-grid (--plane {plane}): {', '.join(unknown)}")
    share = band(repo)
    run = [c for c in items if not cells or c in cells]
    with concurrent.futures.ProcessPoolExecutor(max(1, jobs)) if jobs > 1 else contextlib.nullcontext() as ex:
        res = (list(ex.map(read_cell, *zip(*[(repo, c, plant_error, days) for c in run]))) if ex
               else [read_cell(repo, c, plant_error, days) for c in run])
    by = {r["cell"]: r for r in res}
    out = []
    for c in items:
        r = by.get(c)
        if r is None:
            out.append(f"{c}\tnot run: outside --cells")
        elif r["examined"]:
            out.append(r["line"] + f"\tband={judge_gap(r['gap'], r['c_real'], share)}")
        else:
            out.append(r["line"])
    done = [r for r in res if r["examined"]]
    stats = {k: mean_2se([r[k] for r in done]) for k in ("regret", "floor", "gap")}
    out.append("MEAN " + " ".join(f"{k}={m:.4f} 2se={s:.4f}" for k, (m, s) in stats.items())
               + f" over {len(done)} cells, plant-error {plant_error}, {days} day(s)")
    out.append(f"RESULT read=regret universe={len(items)} examined={len(done)} value={stats['regret'][0]:.4f}")
    return out


# ------------------------------------------------------------------------------------------- install-day

def attribute_keys(repo):
    tree = ast.parse((Path(repo) / REPLAY_DOC).read_text())
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ATTRIBUTE_KEYS" for t in n.targets):
            return {c.value for c in ast.walk(n.value) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    raise Refuse(f"{REPLAY_DOC}: no ATTRIBUTE_KEYS")


def same_information_reason(repo):
    keys = attribute_keys(repo)
    held = sorted(k for k in keys if "forecast" in k)
    why = ([] if held else ["replay_doc.py ATTRIBUTE_KEYS keeps no forecast as issued"]) + [NO_SAME_INFORMATION]
    return "NO-READ: " + "; ".join(why)


def _series(rows):
    out = []
    for r in rows:
        try:
            out.append((datetime.fromisoformat(r[0]), float(r[1])))
        except (TypeError, ValueError, IndexError):
            continue
    return sorted(out)


def _at(series, t):
    v = None
    for ts, x in series:
        if ts > t:
            break
        v = x
    return v


def read_bundle(path):
    """(C_real, its source note, metered cost, C_model or None, its note) from one hpo-debug/1 bundle."""
    try:
        b = json.loads(Path(path).read_text())
        rp, stores = b["replay"], b["stores"]
        w0, w1 = (datetime.fromisoformat(rp["window"][k]) for k in ("start", "end"))
        entry = rp["entry"]["data"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Refuse(f"{path}: no hpo-debug/1 bundle ({type(e).__name__}: {e})")
    energy = next((v for k, v in stores.items() if k.endswith("_energy")), None)
    acc = next((v for k, v in stores.items() if k.endswith("_accuracy")), None)
    if energy is None or "total_cost" not in energy:
        c_real, note = None, "NO-READ: the bundle holds no energy store"
    elif date.fromisoformat(energy["since"]) < w0.astimezone(timezone.utc).date():
        c_real, note = None, f"NO-READ: the energy store counts since {energy['since']}, before the window"
    else:
        c_real, note = float(energy["total_cost"]), f"energy store since {energy['since']}"
    power = _series(rp["states"].get(entry.get("heat_pump_power_entity"), []))
    price = _series(rp["states"].get(entry.get("price_entity"), []))
    marks = sorted({t for t, _ in power + price if w0 <= t < w1} | {w0, w1})
    metered = 0.0
    for a, z in zip(marks, marks[1:]):
        p, q = _at(power, a), _at(price, a)
        if p is not None and q is not None:
            metered += p * q * (z - a).total_seconds() / 3600.0
    promises = ((acc or {}).get("accuracy") or {}).get("promises") or {}
    days, d = [], w0.date()
    while datetime.combine(d, datetime.min.time(), w0.tzinfo) < w1:
        days.append(d.isoformat())
        d += timedelta(days=1)
    missing = [x for x in days if not (promises.get(x) or {}).get("cost")]
    if missing:
        c_model, mnote = None, f"NO-READ: no day-ahead promise for {', '.join(missing)}"
    else:
        c_model, mnote = sum(float(promises[x]["cost"][-1]) for x in days), f"promises {','.join(days)}"
    return c_real, note, metered, c_model, mnote


def read_installs(repo, bundles=None):
    items = universe(repo, "d15-installs")
    bundles = dict(bundles or {})
    labels = {i.split(" ", 1)[0] for i in items}
    unknown = sorted(set(bundles) - labels)
    if unknown:
        raise Refuse(f"--bundle names no install of d15-installs: {', '.join(unknown)}")
    share, why, out, gaps = band(repo), same_information_reason(repo), [], []
    for i in items:
        label = i.split(" ", 1)[0]
        if label not in bundles:
            out.append(f"{i}\tnot read: no --bundle for {label}")
            continue
        c_real, note, metered, c_model, mnote = read_bundle(bundles[label])
        row = f"{i}\tC_real={'NO-READ' if c_real is None else f'{c_real:.4f}'} ({note})\tmetered={metered:.4f}"
        row += f"\tC_model={'NO-READ' if c_model is None else f'{c_model:.4f}'} ({mnote})"
        if c_real is not None and c_model is not None:
            gap = abs(c_real - c_model)
            gaps.append(gap)
            row += f"\tmodel_gap={gap:.4f}\tband={judge_gap(gap, c_real, share)}"
        else:
            row += "\tmodel_gap=NO-READ"
        out.append(row + f"\tC_same={why}")
    m, s = mean_2se(gaps)
    out.append(f"MEAN model_gap={m:.4f} 2se={s:.4f} over {len(gaps)} install-days; regret NO-READ per install-day")
    out.append(f"RESULT read=regret-installs universe={len(items)} examined={len(gaps)} value=NO-READ")
    return out


ROLLING = "tests/rolling.py"
ROLLING_NAMES = ("START", "REPLAN_HOURS", "DAYS", "tile", "run_rolling")


def rolling_loop(repo):
    """`tests/rolling.py`'s own `run_rolling`, its imports and constants, without the checks its module runs."""
    _paths(repo)
    tree = ast.parse((Path(repo) / ROLLING).read_text())
    keep = [n for n in tree.body if (isinstance(n, (ast.Import, ast.ImportFrom)) and getattr(n, "module", "") not in
                                     ("harness", "heatpump_optimizer.coordinator"))
            or (isinstance(n, ast.FunctionDef) and n.name in ROLLING_NAMES)
            or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ROLLING_NAMES for t in n.targets))]
    ns = {"__name__": "rolling_extract"}
    exec(compile(ast.Module(body=keep, type_ignores=[]), ROLLING, "exec"), ns)
    return ns


def parity(repo, cell, plant_error, oracle_error=None):
    """The oracle's executed loop beside run_rolling's on one cell: (same space series, same dhw series, same
    cost). `oracle_error` runs the oracle's side on another plant, the comparison's own null control."""
    import numpy as np
    lv = cell_levels(cell)
    ns = rolling_loop(repo)
    got = ns["run_rolling"](days=1, dhw=lv["dhw"], two_zone=lv["two_zone"], plant_error=plant_error,
                            price_profile=lv["price"], weather_profile=lv["weather"], horizon_hours=lv["horizon_h"])["history"]
    L = Loop(repo, lv, plant_error if oracle_error is None else oracle_error, 1)
    space, dhw, _ = L.closed(1.0)
    return (bool(np.array_equal(space, got["space_power"])), bool(np.array_equal(dhw, got["dhw_power"])),
            abs(L.cost(space, dhw) - float(np.sum(got["cost"]))) < 1e-9 * max(1.0, abs(L.cost(space, dhw))),
            float(np.sum(got["cost"])))


# ---------------------------------------------------------------------------------------------- self-test

SELF_CELLS = ("winter_typical/winter_cold/single-zone/no-dhw/plain/6h",
              "winter_extreme/winter_cold/single-zone/no-dhw/plain/6h",
              "summer_typical/winter_mild/single-zone/no-dhw/plain/6h",
              "winter_narrow/winter_cold/single-zone/no-dhw/plain/6h")
# the cells whose plant=model regret is 0: no open-loop challenger beats the executed plan there (on
# summer_typical/winter_mild the greedy challenger does, the solver's share, which this null does not read)
NULL_CELLS = SELF_CELLS[:2] + SELF_CELLS[3:]
FLAT_CELL = "flat/winter_cold/single-zone/no-dhw/plain/6h"
DHW_CELL = "winter_typical/winter_cold/single-zone/dhw/plain/6h"
TWO_ZONE_CELL = "shoulder/winter_mild/two-zone/no-dhw/plain/6h"
NO_PLANT_CELL = "winter_typical/winter_cold/single-zone/no-dhw/wood/6h"
BUNDLE_GEN = "tools/replay/dbg_bundle_gen.py"


def _bundle(repo, out, scale):
    """dbg_bundle_gen.py's one-day bundle, its fixture's metered power scaled by `scale` before the replay."""
    code = (f"import json, sys; sys.argv = ['g', '--days', '1', '--out', {str(out)!r}]\n"
            f"sys.path.insert(0, {str(Path(repo, 'tools/replay'))!r}); import dbg_bundle_gen as g\n"
            f"fx = json.loads(g.FIXTURE.read_text()); e = fx['entry']['data']['heat_pump_power_entity']\n"
            f"for r in fx['states'][e]:\n"
            f"    r[1] = str(float(r[1]) * {scale}) if r[1] not in ('unknown', 'unavailable') else r[1]\n"
            f"p = __import__('pathlib').Path({str(out)!r}) / 'fixture.json'; p.parent.mkdir(parents=True, exist_ok=True)\n"
            f"p.write_text(json.dumps(fx)); g.FIXTURE = p; g.main(sys.argv[1:])\n")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(str(Path(repo, p)) for p in ("tests/hastub", "tests"))}
    return subprocess.Popen([sys.executable, "-c", code], cwd=repo, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def synth_bundle(edit=None):
    """A one-day bundle with known numbers: 2 kW at 0.5 for the window's 24 h is 24.0 metered; the store's 23.5
    and the day's promise 20.0."""
    t0 = "2026-01-15T00:00:00+01:00"
    b = {"replay": {"window": {"start": t0, "end": "2026-01-16T00:00:00+01:00"},
                    "entry": {"data": {"heat_pump_power_entity": "sensor.p", "price_entity": "sensor.c"}},
                    "states": {"sensor.p": [["2026-01-14T22:00:00+00:00", "2.0", None, None]],
                               "sensor.c": [["2026-01-14T22:00:00+00:00", "0.5", None, None]]}},
         "stores": {"x_energy": {"total_cost": 23.5, "since": "2026-01-14"},
                    "x_accuracy": {"accuracy": {"promises": {"2026-01-15": {"cost": [1.0, 20.0]}}}}}}
    if edit:
        edit(b)
    return b


SYNTH = (
    ("as built", None, (23.5, "energy store since 2026-01-14", 24.0, 20.0, "promises 2026-01-15")),
    ("store counting from before the window", lambda b: b["stores"]["x_energy"].update(since="2026-01-01"),
     (None, "NO-READ: the energy store counts since 2026-01-01, before the window", 24.0, 20.0, "promises 2026-01-15")),
    ("no energy store", lambda b: b["stores"].pop("x_energy"),
     (None, "NO-READ: the bundle holds no energy store", 24.0, 20.0, "promises 2026-01-15")),
    ("price halved at noon local", lambda b: b["replay"]["states"]["sensor.c"].append(["2026-01-15T11:00:00+00:00", "0.25", None, None]),
     (23.5, "energy store since 2026-01-14", 18.0, 20.0, "promises 2026-01-15")),
    ("a second day with no promise", lambda b: b["replay"]["window"].update(end="2026-01-17T00:00:00+01:00"),
     (23.5, "energy store since 2026-01-14", 48.0, None, "NO-READ: no day-ahead promise for 2026-01-16")),
    ("two days, both promised", lambda b: (b["replay"]["window"].update(end="2026-01-17T00:00:00+01:00"),
                                           b["stores"]["x_accuracy"]["accuracy"]["promises"].update({"2026-01-16": {"cost": [2.0, 5.0]}})),
     (23.5, "energy store since 2026-01-14", 48.0, 25.0, "promises 2026-01-15,2026-01-16")),
)


def _raises(fn):
    try:
        fn()
    except Refuse:
        return True
    return False


def _exit(*argv):
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        rc = main(list(argv))
    return rc, "RESULT" in o.getvalue()


def self_test():
    repo = Path(__file__).resolve().parents[2]
    arms, fails = 0, []

    def arm(name, got, want):
        nonlocal arms
        arms += 1
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    def field(line, key):
        return next(x.split("=", 1)[1].split(" ", 1)[0] for x in line.split("\t") if x.startswith(key + "="))

    with tempfile.TemporaryDirectory() as tmp:
        procs = {s: _bundle(repo, Path(tmp, f"b{s}"), s) for s in (1.0, 2.0)}
        # grid: the planted control and its two nulls, on the live tree
        planted = read_grid(repo, "all", list(SELF_CELLS), plant_error=0.8, jobs=4)
        rows = [l for l in planted if l.split("\t")[0] in SELF_CELLS]
        m = planted[-2].split()
        arm("planted: a plant leaking less than the model reads regret above two standard errors",
            float(m[1].split("=")[1]) > float(m[2].split("=")[1]), True)
        arm("planted: every planted cell reads regret > 0", all(float(field(l, "regret")) > 0 for l in rows), True)
        arm("planted: the plant-model candidate runs in every cell", all("plant-model" in l.split("C_same=")[1].split(")")[0] for l in rows), True)
        arm("planted: and wins where no challenger is cheaper", sum("(plant-model of" in l for l in rows) >= len(NULL_CELLS), True)
        arm("planted: RESULT counts the examined cells", planted[-1].split()[3], f"examined={len(SELF_CELLS)}")
        null = read_grid(repo, "all", list(SELF_CELLS) + [FLAT_CELL, NO_PLANT_CELL, DHW_CELL], plant_error=1.0, jobs=4)
        nrows = {l.split("\t")[0]: l for l in null if "\t" in l}
        arm("null: the plant equal to the model reads regret 0 where no challenger wins",
            [field(nrows[c], "regret") for c in NULL_CELLS], ["0.0000"] * len(NULL_CELLS))
        arm("null: with the plant equal to the model no row's winner is the plant-model candidate",
            [("plant-model is the executed loop" in nrows[c], "(plant-model of" in nrows[c]) for c in SELF_CELLS], [(True, False)] * len(SELF_CELLS))
        arm("null: a flat price reads regret 0", field(nrows[FLAT_CELL], "regret"), "0.0000")
        arm("null: the floor is 0 and says why", "floor=0.0000 (the loop's forecast is the realised series)" in nrows[FLAT_CELL], True)
        arm("null: the model gap is 0 where the loop meters the command", field(nrows[FLAT_CELL], "model_gap"), "0.0000")
        arm("NO-READ: a plant level the loop does not model", nrows[NO_PLANT_CELL].split("\t", 1)[1],
            "NO-READ: no plant model for wood in the loop")
        arm("NO-READ is not examined", null[-1].split()[3], f"examined={len(SELF_CELLS) + 2}")
        arm("a cell outside --cells is printed not run", sum("not run: outside --cells" in l for l in null),
            len(universe(repo, "d0-grid")) - len(SELF_CELLS) - 3)
        # the loop is run_rolling's: its own function, extracted from tests/rolling.py, drives the same series
        arm("parity: a hot-water cell's executed loop is run_rolling's", parity(repo, DHW_CELL, 1.25)[:3], (True, True, True))
        arm("parity: a two-zone cell's", parity(repo, TWO_ZONE_CELL, 0.8)[:3], (True, True, True))
        pn = parity(repo, DHW_CELL, 1.0, 1.25)
        arm("parity null: another plant on the oracle's side differs", pn[0], False)
        arm("a grid row's C_real is run_rolling's cost on its cell", field(nrows[DHW_CELL], "C_real"), f"{pn[3]:.4f}")
        arm("an examined row carries its band", nrows[DHW_CELL].endswith("\tband=undecided (thresholds.band_model_gap is null)"), True)
        arm("the MEAN floor is 0 with the forecast realised", null[-2].split()[3], "floor=0.0000")
        arm("a challenger wins where the solver leaves cost: greedy", "(greedy of" in nrows[SELF_CELLS[2]], True)
        arm("and perturbed", "(perturbed of" in nrows[DHW_CELL], True)
        # admission: bounds, limits, stored heat
        import numpy as np
        L = Loop(repo, cell_levels(SELF_CELLS[0]), 1.0, 1)
        sp, dh, _ = L.closed(1.0)
        ref = L.score(sp, dh)
        g = greedy(sp, L.price[:L.T], L.pmax, np)
        arm("score: the executed plan holds the bounds", ref[0], 0.0)
        arm("score: all off breaks the floor, all on the ceiling", (L.score(sp * 0, dh)[0] > 0, L.score(sp * 0 + L.pmax, dh)[0] > 0), (True, True))
        arm("admits: greedy holds the bounds but ends colder: refused for the heat it borrowed",
            (L.score(g, dh)[0], L.admits(g, dh, ref), L.admits(g, dh, ref, terminal=False)), (0.0, False, True))
        arm("in_limits: 0..pmax, nothing below or above", (L.in_limits(np.array([-EPS, L.pmax])), L.in_limits(np.array([-1e-6])),
                                                          L.in_limits(np.array([L.pmax + 1e-6]))), (True, False, False))
        last = sp.copy()
        last[-1] = L.pmax if sp[-1] < L.pmax / 2 else 0.0
        arm("score: the end state is the window's last step", L.score(last, dh)[1] != ref[1], True)
        Z = Loop(repo, cell_levels(TWO_ZONE_CELL), 1.0, 1)
        zsp, zdh, _ = Z.closed(1.0)
        zref = Z.score(zsp, zdh)
        arm("score: two zones read the colder zone, executed inside, all off outside", (zref[0] < 0.01, Z.score(zsp * 0, zdh)[0] > 1.0), (True, True))
        D = Loop(repo, cell_levels(DHW_CELL), 1.0, 1)
        dsp, ddh, _ = D.closed(1.0)
        dref = D.score(dsp, ddh)
        arm("score: hot water off breaks the tank minimum in its windows", (dref[0] < 0.01, D.score(dsp, ddh * 0)[0] > 1.0), (True, True))
        best, best_c = perturbed(D, dsp, ddh, dref)
        arm("perturbed: cheaper, admitted, the same energy", (best_c < D.cost(dsp, ddh), D.admits(best, ddh, dref),
                                                            round(float(best.sum() - dsp.sum()), 9)), (True, True, 0.0))
        arm("cell_levels: a plane cell runs at PLANE_LEVELS", cell_levels("a/b"),
            dict(price="a", weather="b", two_zone=False, dhw=True, plant="plain", horizon_h=24))
        arm("mean_2se: no cell is a mean of 0", mean_2se([])[0], 0.0)
        arm("cell_levels: a line of no grid shape is refused", _raises(lambda: cell_levels("x")), True)
        arm("_at: the value held at t, a reading stamped at t included", (_at([(1, 5.0), (2, 7.0)], 2), _at([(1, 5.0)], 0)), (7.0, None))
        g = greedy(np.array([1.0, 2.0, 0.0, 3.0]), np.array([3.0, 1.0, 2.0, 0.5]), 4.0, np)
        arm("greedy: the same energy at the cheapest steps, capped at pmax", g.tolist(), [0.0, 2.0, 0.0, 4.0])
        arm("band: undecided while null", judge_gap(1.0, 10.0, None), "undecided (thresholds.band_model_gap is null)")
        arm("band: inside at the owner's share", judge_gap(1.0, 10.0, 0.1), "inside")
        arm("band: outside beyond it", judge_gap(1.01, 10.0, 0.1), "outside")
        arm("mean_2se", tuple(round(x, 6) for x in mean_2se([1.0, 3.0])), (2.0, 2.0))
        # install-day: the scaled bundle moves C_real and the gap; the unscaled reads the same gap twice
        for s, p in procs.items():
            err = p.communicate(timeout=600)[1]
            if p.returncode:
                fails.append(f"bundle x{s}: dbg_bundle_gen.py exited {p.returncode}: {err[-400:]}")
                return arms, fails
        label = universe(repo, "d15-installs")[0].split(" ", 1)[0]
        one = read_installs(repo, {label: str(Path(tmp, "b1.0", "bundle.json"))})
        again = read_installs(repo, {label: str(Path(tmp, "b1.0", "bundle.json"))})
        two = read_installs(repo, {label: str(Path(tmp, "b2.0", "bundle.json"))})
        r1, r2 = one[0], two[0]
        arm("installs planted: scaled metered power moves C_real", float(field(r2, "C_real")) > float(field(r1, "C_real")), True)
        arm("installs planted: and the model gap", field(r2, "model_gap") != field(r1, "model_gap"), True)
        arm("installs planted: and the metered cross-check", float(field(r2, "metered")) > float(field(r1, "metered")), True)
        arm("installs null: the unscaled bundle reads the same gap twice", field(again[0], "model_gap"), field(r1, "model_gap"))
        why = same_information_reason(repo)
        arm("installs: C_same is NO-READ, never a number, in both", [r1.split("\tC_same=")[1], r2.split("\tC_same=")[1]], [why, why])
        arm("installs: the reason is derived from ATTRIBUTE_KEYS", "ATTRIBUTE_KEYS keeps no forecast as issued" in why,
            not any("forecast" in k for k in attribute_keys(repo)))
        arm("installs: RESULT", one[-1], f"RESULT read=regret-installs universe={len(universe(repo, 'd15-installs'))} examined=1 value=NO-READ")
        bare = read_installs(repo)
        arm("installs: no bundle is not read, examined 0", (bare[0].split("\t", 1)[1], bare[-1].split()[3]),
            (f"not read: no --bundle for {label}", "examined=0"))
        arm("installs: the MEAN line", one[-2], f"MEAN model_gap={field(r1, 'model_gap')} 2se=nan over 1 install-days; regret NO-READ per install-day")
        arm("installs planted: twice the metered power is twice the metered cost", field(r2, "metered"), f"{2 * float(field(r1, 'metered')):.4f}")
        for name, edit, want in SYNTH:
            path = Path(tmp, f"synth-{name}.json")
            path.write_text(json.dumps(synth_bundle(edit)))
            arm(f"installs synthetic ({name})", read_bundle(path), want)
        arm("refuse: a --bundle naming no install", _exit("installs", "--repo", str(repo), "--bundle", "nope=x"), (2, False))
        # the refusals: an emptied universe source exits 2 with no RESULT; the head exits 0 with one
        fake = Path(tmp, "fake")
        (fake / "tests").mkdir(parents=True)
        (fake / "dev/audit/config").mkdir(parents=True)
        (fake / "tests/profiles.py").write_text("def prices(profile, s):\n    pass\ndef weather(profile, s):\n    pass\n")
        (fake / census.BUNDLES).write_text(json.dumps({"bundles": []}))
        shutil.copy(repo / census.OBJECTIVE, fake / census.OBJECTIVE)
        arm("band: the owner's value read from objective.json, None while null", band(fake), band(repo))
        obj = json.loads((fake / census.OBJECTIVE).read_text())
        obj["thresholds"]["band_model_gap"]["value"] = 0.1
        (fake / census.OBJECTIVE).write_text(json.dumps(obj))
        arm("band: a set value is read", band(fake), 0.1)
        arm("refuse: an emptied d0-grid source", _exit("grid", "--repo", str(fake)), (2, False))
        arm("refuse: an emptied d15-installs source", _exit("installs", "--repo", str(fake)), (2, False))
        arm("refuse: a --cells item outside the universe", _exit("grid", "--repo", str(repo), "--cells", "nope/nope"), (2, False))
        arm("refuse: an unreadable bundle", _exit("installs", "--repo", str(repo), "--bundle", f"{label}={fake}/none.json"), (2, False))
        arm("head: installs exits 0 with a RESULT", _exit("installs", "--repo", str(repo)), (0, True))
    return arms, fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("read", nargs="?", choices=("grid", "installs"))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--plane", default="price-weather", choices=("price-weather", "all"))
    ap.add_argument("--cells", default="")
    ap.add_argument("--plant-error", type=float, default=1.0)
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--bundle", action="append", default=[])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        arms, fails = self_test()
        for f in fails:
            print(f"FAIL {f}")
        print(f"SELF-TEST {'passed' if not fails else 'FAILED'} ({arms} arms)")
        return 1 if fails else 0
    if not a.read:
        ap.error("name a read: grid or installs")
    try:
        if a.read == "grid":
            out = read_grid(a.repo, a.plane, [c for c in a.cells.split(",") if c], a.plant_error, a.days, a.jobs)
        else:
            if any("=" not in b for b in a.bundle):
                raise Refuse("--bundle is LABEL=PATH")
            out = read_installs(a.repo, dict(b.split("=", 1) for b in a.bundle))
    except (Refuse, OSError, ValueError) as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
