"""Shared builders for round 11 D0-s3's harnesses (not a harness itself).

Imported by race.py, loop.py, decomp.py and oracle.py in this directory. Every
harness copies tests/stress.py's thread pin BEFORE importing this module.

What it provides:
  cell(name)      -- one line of `python3 tools/audit/enumerate.py d0-grid`
                     built as a production optimizer + inputs. The plant axis
                     is mapped to production configuration as stated in PLANTS.
  Capture         -- the tests/optimality.py patch idiom, extended: records
                     every `optimizer._multi_start_minimize` call (objective,
                     candidates, bounds, args, maxiter, batch_objective,
                     move_starts, result) and every `optimizer._commit_runs`
                     call (opt, h, scope, relaxed, dhw, maxiter, rescope,
                     result), so a race scores a challenger on the call's
                     own descent objective AND its committed form on the
                     true objective, the way production ships it.
  race_call(...)  -- D0.md step 2's challengers, cheapest first, on one
                     captured call.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any

ROOT = os.getcwd()
for p in ("tests", "custom_components"):
    q = os.path.join(ROOT, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402

from golden import make, START  # noqa: E402
from profiles import solve_inputs, house  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.thermal_model import WeatherSeries  # noqa: E402

ORIG_MS = om._multi_start_minimize
ORIG_COMMIT = om._commit_runs
ORIG_SCOPED = om._scoped_minimize

_VALVE_STORE = {
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    "buffer_max_temperature": 70.0,
}
#: plant level -> (config_overrides, state_overrides). Sources: golden.py
#: SCENARIOS `valve_storage` and `wood_two_tank` for the first two; the
#: manual-valve-buffer level is the house's own 200 L tank behind a manual
#: valve; flow-setpoint-behind-valve is the 750 L store + manual valve
#: driven through a switch + flow set-point with a power meter and no
#: frequency entity, which production's `thermal_model.levels_clamped`
#: reads as "cannot duty-cycle" (the pump runs at or above p_min).
PLANTS: dict[str, tuple[dict, dict]] = {
    "plain": ({}, {}),
    "valve-storage": (dict(_VALVE_STORE), {"buffer_tank_temperature": 32.0}),
    "wood": (
        {**_VALVE_STORE, "wood_tank_top_entity": "sensor.wood_top", "wood_tank_volume": 500.0},
        {"buffer_tank_temperature": 32.0, "wood_tank_temperature": 55.0},
    ),
    "manual-valve-buffer": ({"mixing_valve_mode": "manual"}, {}),
    "flow-setpoint-behind-valve": (
        {
            **_VALVE_STORE,
            "heat_pump_switch_entity": "switch.hp",
            "space_setpoint_entity": "number.hp_flow",
            "space_setpoint_unit": "flow",
            "pump_duty_mode": "control",
            "power_entity": "sensor.hp_power",
        },
        {"buffer_tank_temperature": 32.0},
    ),
}


def parse(name: str) -> dict:
    price, weather, topo, dhw, plant, hor = name.split("/")
    return dict(price=price, weather=weather, two_zone=topo == "two-zone",
                dhw=dhw == "dhw", plant=plant, hours=int(hor.rstrip("h")))


def spec_of(name: str, price: str | None = None, extra_cfg: dict | None = None) -> dict:
    c = parse(name)
    cfg_over, st_over = PLANTS[c["plant"]]
    cfg_over = {**cfg_over, **(extra_cfg or {})}
    full = house(two_zone=c["two_zone"], dhw=c["dhw"])
    full.update(cfg_over)
    opt_over = {}
    clamp = tm.levels_clamped(full)  # production's own reading of the plant
    if clamp:
        opt_over["clamp_planned_levels"] = True
    return dict(two_zone=c["two_zone"], dhw=c["dhw"], price_profile=price or c["price"],
                weather_profile=c["weather"], hours=c["hours"], config_overrides=cfg_over,
                state_overrides=dict(st_over), opt_overrides=opt_over)


def build(name: str, price: str | None = None, extra_cfg: dict | None = None,
          param_overrides: dict | None = None) -> dict:
    spec = spec_of(name, price, extra_cfg)
    if param_overrides:
        spec["param_overrides"] = param_overrides
    b = make(**spec)
    b["spec"] = spec
    return b


def inputs_of(b: dict, state=None, start=None, sl: slice | None = None):
    s = sl or slice(None)
    return solve_inputs(
        initial_state=state or b["state"], prices=b["prices"][s], outdoor_temps=b["outdoor"][s],
        wind_speeds=b["wind"][s], precipitation=b["rain"][s], solar_radiation=b["solar"][s],
        start_time=start or START)


@dataclass
class MsCall:
    objective: Any
    candidates: list
    bounds: list
    args: tuple
    maxiter: int
    batch: Any
    move_starts: Any
    result: Any = None
    cpu: float = 0.0
    commit: dict | None = None


class Capture:
    """Patch `_multi_start_minimize` and `_commit_runs`; pair each commit with
    the multi-start call that preceded it."""

    def __init__(self, extra_seeds=None):
        self.calls: list[MsCall] = []
        self.extra_seeds = extra_seeds  # callable(call)->list[np.ndarray] (augmented arm)
        self.runs: list[tuple[int, int, int]] = []  # (nit, status, maxiter) of every L-BFGS-B run

    def _scoped(self, *a, **kw):
        r = ORIG_SCOPED(*a, **kw)
        mi = int((kw.get("options") or {}).get("maxiter", -1))
        self.runs.append((int(getattr(r, "nit", -1)), int(getattr(r, "status", -1)), mi))
        return r

    def binding(self) -> int:
        """L-BFGS-B runs that stopped on a budget (status 1: maxiter or maxfun)."""
        return sum(1 for nit, st, mi in self.runs if st == 1 or (mi > 0 and nit >= mi))

    def _ms(self, objective, candidates, bounds, args=(), maxiter=300,
            batch_objective=None, move_starts=None):
        ms = move_starts if move_starts is not None else (lambda c, m: c)
        call = MsCall(objective, [np.array(c, dtype=float) for c in candidates], list(bounds),
                      tuple(args), maxiter, batch_objective, ms)
        cands = list(candidates)
        if self.extra_seeds is not None:
            cands = cands + list(self.extra_seeds(call))
        t = time.process_time()
        res = ORIG_MS(objective, cands, bounds, args, maxiter=maxiter,
                      batch_objective=batch_objective, move_starts=ms)
        call.cpu = time.process_time() - t
        call.result = res
        self.calls.append(call)
        return res

    def _commit(self, opt, h, scope, relaxed, dhw, maxiter, rescope=None):
        out = ORIG_COMMIT(opt, h, scope, relaxed, dhw, maxiter, rescope)
        if self.calls and self.calls[-1].commit is None:
            self.calls[-1].commit = dict(opt=opt, h=h, scope=scope, dhw=dhw, maxiter=maxiter,
                                         rescope=rescope, out=np.asarray(out[0], dtype=float),
                                         out_scope=out[1])
        return out

    def __enter__(self):
        self._p1 = mock.patch.object(om, "_multi_start_minimize", self._ms)
        self._p2 = mock.patch.object(om, "_commit_runs", self._commit)
        self._p3 = mock.patch.object(om, "_scoped_minimize", self._scoped)
        self._p1.start(); self._p2.start(); self._p3.start()
        return self

    def __exit__(self, *exc):
        self._p3.stop(); self._p2.stop(); self._p1.stop()
        return False


def solve(b: dict, extra_seeds=None, opt=None, inputs=None):
    o = opt or b["optimizer"]
    with Capture(extra_seeds) as cap:
        t = time.process_time()
        r = o.optimize(inputs=inputs or inputs_of(b))
        cpu = time.process_time() - t
    return r, cap.calls, cpu, cap.binding()


# ---------------------------------------------------------------------------
# Scoring one captured call
# ---------------------------------------------------------------------------

def committed(call: MsCall, x: np.ndarray) -> tuple[np.ndarray, float]:
    """x as production would ship it from this call, and its true-objective score."""
    x = np.asarray(x, dtype=float)
    lo = np.array([b[0] for b in call.bounds]); hi = np.array([b[1] for b in call.bounds])
    x = np.clip(x, lo, hi)
    c = call.commit
    if c is None:
        return x, float(call.objective(x, *call.args))
    if not om._engaged(c["opt"]):
        return x, float(c["scope"][1](x, *call.args))
    out, scope = ORIG_COMMIT(c["opt"], c["h"], c["scope"], [x], c["dhw"], c["maxiter"], c["rescope"])
    out = np.asarray(out, dtype=float)
    return out, float(scope[1](out, *call.args))


def shipped_of(call: MsCall) -> tuple[np.ndarray, float]:
    """The plan production shipped from this call and its true-objective score."""
    c = call.commit
    if c is None:
        x = np.asarray(call.result.x, dtype=float)
        return x, float(call.objective(x, *call.args))
    return c["out"], float(c["out_scope"][1](c["out"], *call.args))


def comfort_breach(call: MsCall, x: np.ndarray) -> tuple[float, float]:
    """(degree-steps below the per-step floor, above the ceiling) on the
    production model's own trajectory, across every zone it simulates."""
    c = call.commit
    if c is None:
        return float("nan"), float("nan")
    h, opt = c["h"], c["opt"]
    ws = WeatherSeries(outdoor_temps=h.outdoor_temps, wind_speeds=h.wind_speeds,
                       precipitation=h.precipitation, solar_radiation=h.solar_radiation)
    tr = opt.model.simulate_trajectory(h.initial_state, np.asarray(x, dtype=float), ws, dt_hours=h.dt,
                                       valve_targets=getattr(h, "valve_targets", None))
    zones = [tr[0]] + ([tr[2], tr[3]] if opt.model.params.two_zone_enabled else [])
    lo = np.asarray(h.temp_min_bounds, dtype=float); hi = np.asarray(h.temp_max_bounds, dtype=float)
    below = sum(float(np.maximum(0.0, lo - z[1:]).sum()) for z in zones)
    above = sum(float(np.maximum(0.0, z[1:] - hi).sum()) for z in zones)
    return below, above


def energy_cost(call: MsCall, x: np.ndarray) -> float:
    c = call.commit
    if c is None:
        return float("nan")
    h = c["h"]
    return float(np.sum(np.asarray(h.prices, dtype=float) * np.asarray(x, dtype=float)) * h.dt)


# ---------------------------------------------------------------------------
# D0.md step 2's challengers
# ---------------------------------------------------------------------------

def bang_bang(prices, hi, energy, dt):
    """Bound-aware greedy: cheapest steps first, each up to its own upper bound."""
    x = np.zeros_like(hi)
    left = float(energy)
    for i in np.argsort(prices, kind="stable"):
        if left <= 0:
            break
        take = min(hi[i], left / dt)
        x[i] = take
        left -= take * dt
    return x


def structured_seeds(call: MsCall, prev_plan=None):
    hi = np.array([b[1] for b in call.bounds]); lo = np.array([b[0] for b in call.bounds])
    c = call.commit
    prices = np.asarray(c["h"].prices, dtype=float) if c else np.ones_like(hi)
    dt = float(c["h"].dt) if c else 0.25
    if call.result is not None:
        shipped, _ = shipped_of(call)
        e_ref = max(float(np.sum(shipped) * dt), 1e-3)
    else:  # seeding inside a live solve (the augmented arm): no result yet
        e_ref = max(float(np.median([np.sum(c) for c in call.candidates]) * dt), 1e-3)
    e_base = max(float(np.sum(call.candidates[min(2, len(call.candidates) - 1)]) * dt), 1e-3)
    seeds = [bang_bang(prices, hi, f * e_ref, dt) for f in (0.5, 1.0, 1.5)]
    seeds += [bang_bang(prices, hi, f * e_base, dt) for f in (0.5,)]
    seeds += [np.clip(lo, lo, hi), hi.copy()]
    if prev_plan is not None and len(prev_plan) == len(hi):
        seeds.append(np.clip(np.asarray(prev_plan, dtype=float), lo, hi))
    return [np.clip(s, lo, hi) for s in seeds]


def _loose_budget_scoped(*a, **kw):
    kw = dict(kw)
    o = dict(kw.get("options") or {})
    o["maxfun"] = 200000
    kw["options"] = o
    return ORIG_SCOPED(*a, **kw)


def run_ms(call: MsCall, cands, maxiter=None, eps=None, budget=False):
    patches = []
    if eps is not None:
        patches.append(mock.patch.object(om, "_LBFGSB_FD_EPS", eps))
    if budget:
        patches.append(mock.patch.object(om, "_scoped_minimize", _loose_budget_scoped))
    for p in patches:
        p.start()

    def ms(c, m):
        # production's continuation moves the start at index len(extra_starts);
        # a challenger list shorter than that has no such start, so it is left
        # unmoved (the race's seeds arm can be shorter than production's list)
        try:
            return call.move_starts(c, m)
        except IndexError:
            return c
    try:
        return ORIG_MS(call.objective, list(cands), call.bounds, call.args,
                       maxiter=maxiter or call.maxiter, batch_objective=call.batch,
                       move_starts=ms)
    finally:
        for p in reversed(patches):
            p.stop()


def de_block(call: MsCall, seed=0, block=4, popsize=4, maxiter=25):
    """differential_evolution on an hourly-block coarsening, vectorized through
    the call's own batch objective; the best member is returned at full width."""
    from scipy.optimize import differential_evolution
    hi = np.array([b[1] for b in call.bounds]); lo = np.array([b[0] for b in call.bounds])
    n = hi.size
    nb = int(np.ceil(n / block))
    idx = np.minimum(np.arange(n) // block, nb - 1)
    bh = np.array([hi[idx == k].max() for k in range(nb)])

    def expand(Z):
        Z = np.atleast_2d(Z)
        return np.clip(Z[:, idx], lo, hi)

    if call.batch is not None:
        def f(Z):
            return np.asarray(call.batch(expand(Z.T), *call.args), dtype=float)
        vec = True
    else:
        def f(z):
            return float(call.objective(expand(z)[0], *call.args))
        vec = False
    shipped, _ = shipped_of(call)
    init_member = np.array([shipped[idx == k].mean() for k in range(nb)])
    rng = np.random.default_rng(seed)
    pop = rng.uniform(0, 1, (max(5, popsize * nb), nb)) * bh
    pop[0] = np.minimum(init_member, bh)
    r = differential_evolution(f, [(0.0, float(v)) for v in bh], init=pop, maxiter=maxiter,
                               polish=False, seed=seed, vectorized=vec, updating="deferred" if vec else "immediate",
                               tol=0, atol=0)
    return expand(r.x)[0]


@dataclass
class Race:
    prod: float
    prod_x: np.ndarray
    arms: dict = field(default_factory=dict)  # name -> (score, x)
    cpu: float = 0.0

    def best(self):
        name, (s, x) = min(self.arms.items(), key=lambda kv: kv[1][0])
        return name, s, x


def race_call(call: MsCall, prev_plan=None, with_de=True, binding=True) -> Race:
    """The production candidates are not re-run in the seeds arm: the arm is the
    seeds alone and the race keeps the minimum with production, which is what a
    multi-start over the union would ship (it keeps the cross-candidate minimum).
    The budget arm runs only where a production L-BFGS-B run stopped on its
    budget (`binding`): a deterministic run that converged before maxiter/maxfun
    is unchanged by a larger budget."""
    t0 = time.process_time()
    px, ps = shipped_of(call)
    race = Race(ps, px)

    def arm(name, res_x):
        x, s = committed(call, res_x)
        race.arms[name] = (s, x)

    seeds = structured_seeds(call, prev_plan)
    arm("seeds", run_ms(call, seeds).x)
    if binding:
        arm("budget", run_ms(call, call.candidates, maxiter=3000, budget=True).x)
    if os.environ.get("D0S3_EPS_ARM", "0") == "1":
        # off by default after the first 71 grid cells (box contention): it won 1
        # of 18 gaps there, a flat-price cell; the env flag re-enables it
        arm("eps", run_ms(call, call.candidates, eps=1e-6).x)
    if with_de:
        try:
            g = de_block(call)
            arm("de_block", run_ms(call, [g], maxiter=3000).x)
        except Exception as e:  # noqa: BLE001
            race.arms["de_block_error"] = (float("inf"), px)
    name, s, x = race.best()
    arm("warm", run_ms(call, [x], maxiter=3000).x)
    race.cpu = time.process_time() - t0
    return race


def pin_threads_report():
    pc = time.process_time(); tc = time.thread_time()
    return pc, tc


def load1():
    try:
        return os.getloadavg()[0]
    except OSError:
        return float("nan")


def swapins():
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin"):
                return int(line.split()[1])
    except OSError:
        pass
    return -1


# ---------------------------------------------------------------------------
# Coordinator captures (tests/golden.py:coordinator_scenarios) on a price axis
# ---------------------------------------------------------------------------

COORD_NAMES = ("coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features")


def coord_record(name: str, price: str):
    """The coordinator's own SolveRecord for one golden coordinator capture,
    built through `coordinator._solve_record` and `_warm_seeded` with the
    capture's injected 48 h feed, its prices replaced by
    `profiles.prices(price)` (hourly means of the 15-min curve, tiled)."""
    import asyncio
    from datetime import timedelta
    from golden import coordinator_scenarios, SCENARIO_ZONE
    from harness import FakeEntry, FakeHass
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator, _warm_seeded
    from heatpump_optimizer.plan_step import plan_step_start
    from profiles import prices as price_curve
    cfg = coordinator_scenarios()[name]
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = SCENARIO_ZONE
    start = START.replace(tzinfo=SCENARIO_ZONE)
    dt_util.freeze(start)
    try:
        coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
        hourly = np.asarray(price_curve(price, START), dtype=float).reshape(24, 4).mean(axis=1)
        coord._prices = [{"total": float(hourly[h % 24]), "starts_at": (START + timedelta(hours=h)).isoformat(),
                          "level": "NORMAL"} for h in range(48)]
        coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                    "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
                                    "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
        coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
        now = dt_util.now()
        horizon = coord._forecast_arrays(now)
        try:
            asyncio.run(coord._resolve_away())
        except Exception:  # noqa: BLE001 - away is off in all but one capture
            pass
        record = coord._solve_record(plan_step_start(now), horizon)
        opt = _warm_seeded(coord, record.optimizer())
        return opt, record.inputs
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved
