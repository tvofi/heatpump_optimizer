"""D0-s1 capture-and-race harness: D0.M1 (capture), D0.M2 (challengers), D0.M3 (feasibility parity).

Metric: per multi-start call, gap = f_prod - f_best, where f is the call's own
objective (the exact callable, args and bounds production handed
optimizer:_multi_start_minimize), f_prod its value at the returned x, and f_best
the lowest value any challenger reaches that passes feasibility parity
(bounds, manual pins, per-step comfort floor/ceiling degree-steps, DHW floor
degree-steps in the planner's windows, each no worse than production's).
Count key: the value of the call's objective at the x the production seam
returns (result.x), never an input attribute.
Challengers (cheapest first): `seeds` (production's candidates plus 13
structured seeds: bang-bang at 0.1-1.5x the production plan's energy and flat
fractions of the headroom), `budget` (maxiter x10, maxfun 150000 through
optimizer:_scoped_minimize), `eps-1e-6` / `eps-1e-3` (optimizer:_LBFGSB_FD_EPS),
`global` (scipy differential_evolution over hourly blocks on the same batched
objective, then the production L-BFGS-B run + restart on the full grid: the
outer bound), `warm` (the production L-BFGS-B run + restart from the best
challenger at maxiter x10).

Run one cell:   PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s1/race.py --cell optimizer.py/winter_typical/dhw-24h
Run all:        PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s1/race.py --all [--jobs 2]
Aggregate:      PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s1/race.py --aggregate
Perturbation:   --perturb thermostat-anchor  gives every DHW-path call (_solve_space via
                _relaxed_plans) the space-only path's thermostat-anchored seeds; the
                DHW-path gaps the `seeds` challenger closes must fall.
                --perturb seeds-in-production  adds the `seeds` challenger's structured
                seeds to production's own candidate list (in memory, wrapping
                _multi_start_minimize) -- every gap the seeds close must go to zero.
Expected: per-cell values as recorded in out/*.json, tolerance +-1e-6 relative (BLAS-dependent floats).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B1 (4 vCPU, shared, provisional for timings).
Writes only under this harness's own out/ directory (or $D0S1_OUT).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import json
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), "tests", "custom_components"]

import numpy as np  # noqa: E402
from scipy.optimize import differential_evolution  # noqa: E402

import cells as cellmod  # noqa: E402
import golden  # noqa: E402
import profiles  # noqa: E402
from profiles import solve_inputs  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402
from heatpump_optimizer.thermal_model import WeatherSeries  # noqa: E402

OUT = Path(os.environ.get("D0S1_OUT", HERE / "out"))
WEATHER = {"summer_typical": "summer_cool", "summer_negative": "summer_cool", "shoulder": "shoulder"}
COMFORT_TOL = 1e-3   # degree-steps
DHW_TOL = 1e-3
ORIG_MS = om._multi_start_minimize
ORIG_SCOPED = om._scoped_minimize


def weather_for(profile):
    return WEATHER.get(profile, "winter_cold")


# --------------------------------------------------------------------- builds
def golden_spec(arm, profile):
    w = weather_for(profile)
    base = dict(price_profile=profile, weather_profile=w)
    if arm.startswith("space-"):
        return dict(base, dhw=False, hours=int(arm.split("-")[1][:-1]))
    if arm.startswith("dhw-"):
        return dict(base, dhw=True, hours=int(arm.split("-")[1][:-1]))
    if arm == "twozone-dhw-24h":
        return dict(base, two_zone=True, dhw=True)
    if arm == "pinned-dhw-24h":
        return dict(base, dhw=True)
    if arm == "twozone-24h":
        return dict(base, two_zone=True, dhw=False)
    key = {"valve-storage": "valve_storage", "valve-smart-write": "valve_storage_smart_write",
           "wood-two-tank": "wood_two_tank", "wood-coil": "wood_coil"}[arm]
    spec = dict(golden.SCENARIOS[key])
    spec.update(base)
    return spec


def pins_for(arm, n):
    """The manual-pin arm: space forced on 02-04, forced off 17-19; hot water forced on 03-04, off 06-07."""
    if arm != "pinned-dhw-24h":
        return None, None
    sp = np.full(n, np.nan)
    dp = np.full(n, np.nan)
    sp[8:16] = 1.0
    sp[68:76] = 0.0
    dp[12:16] = 1.0
    dp[24:28] = 0.0
    return sp, dp


def run_plan_cell(arm, profile):
    s = golden.make(**golden_spec(arm, profile))
    n = len(s["prices"])
    sp, dp = pins_for(arm, n)
    res = s["optimizer"].optimize(inputs=solve_inputs(
        initial_state=s["state"], prices=s["prices"], outdoor_temps=s["outdoor"],
        wind_speeds=s["wind"], precipitation=s["rain"], solar_radiation=s["solar"],
        start_time=golden.START, space_pins=sp, dhw_pins=dp))
    return s["optimizer"], res


def run_coord_cell(arm, profile):
    from harness import FakeEntry, FakeHass
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import coordinator as cm

    S = golden.START
    p = profiles.prices(profile, S)
    ot, wi, ra, so = profiles.weather(weather_for(profile), S)
    seen = {}

    async def inline(hass, optimizer, inputs):
        seen["opt"] = optimizer
        seen["res"] = optimizer.optimize(inputs=inputs)
        return seen["res"]

    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = golden.SCENARIO_ZONE
    dt_util.freeze(S)
    try:
        coord = cm.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=golden.coordinator_scenarios()[arm]))
        coord._prices = [{"total": float(p[i % 96]), "starts_at": (S + timedelta(minutes=15 * i)).isoformat(),
                          "level": "NORMAL"} for i in range(192)]
        coord._weather_forecast = [{"datetime": (S + timedelta(hours=h)).isoformat(),
                                    "temperature": float(ot[(4 * h) % 96]), "wind_speed": float(wi[(4 * h) % 96]),
                                    "precipitation": float(ra[(4 * h) % 96]), "humidity": 85.0} for h in range(48)]
        coord._solar_radiation_forecast = [float(so[(4 * h) % 96]) for h in range(48)]
        with mock.patch.object(cm, "_await_optimize", inline):
            status = asyncio.run(coord.async_run_optimization())
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved
    if "res" not in seen:
        raise RuntimeError(f"coordinator ran no solve: {status}")
    return seen["opt"], seen["res"]


# -------------------------------------------------------------------- capture
class Capture:
    def __init__(self):
        self.calls, self.objs, self.dhw, self.runs = [], [], [], []

    def ms(self, objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
           move_starts=lambda c, m: c):
        cands = [np.array(c, dtype=float) for c in candidates]
        r = ORIG_MS(objective, candidates, bounds, args=args, maxiter=maxiter,
                    batch_objective=batch_objective, move_starts=move_starts)
        self.calls.append(dict(objective=objective, candidates=cands, bounds=list(bounds), args=args,
                               maxiter=maxiter, batch=batch_objective, move=move_starts,
                               x=np.array(r.x, dtype=float), obj_ctx=self.objs[-1] if self.objs else None,
                               dhw_ctx=self.dhw[-1] if self.dhw else None))
        return r

    def solve_objectives(self, orig):
        cap = self

        def wrapped(opt, h):
            out = orig(opt, h)
            cap.objs.append(dict(opt=opt, h=h, traj=out[0]))
            return out
        return wrapped

    def dhw_build(self, orig):
        cap = self

        def wrapped(*a, **k):
            out = orig(*a, **k)
            cap.dhw.append(out[0])
            return out
        return wrapped

    def scoped(self, *a, **k):
        r = ORIG_SCOPED(*a, **k)
        self.runs.append((int(getattr(r, "status", -1)), int(getattr(r, "nit", -1)),
                          int(k.get("options", {}).get("maxiter", -1))))
        return r


def capture_cell(cell, perturb=None):
    f, profile, arm = cell.split("/")
    cap = Capture()
    ms = cap.ms
    if perturb == "seeds-in-production":
        def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
               move_starts=lambda c, m: c):
            lo, hi = (np.array(b, dtype=float) for b in zip(*bounds))
            prices = cap.objs[-1]["h"].prices if cap.objs else np.ones(len(bounds))
            dt = cap.objs[-1]["h"].dt if cap.objs else 0.25
            e = max(float(np.sum(np.clip(candidates[0], lo, hi)) * dt), 1e-3)
            extra = structured_seeds(prices[:len(bounds)], lo, hi, e, dt)
            return cap.ms(objective, list(candidates) + extra, bounds, args, maxiter, batch_objective, move_starts)
    if perturb == "thermostat-anchor":
        def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
               move_starts=lambda c, m: c):
            # The space-only path's anchors (_optimize_space_only: the thermostat
            # seed_power, bang-bang at its energy and at _LOW_ENERGY_START_FRACTION
            # of it, and _DEEP_LOW_ENERGY_START_FRACTION on two-zone) handed to a
            # DHW-path call, which anchors on the smooth guess's energy instead.
            extra = []
            if args and cap.objs:
                ctx = cap.objs[-1]
                h, o = ctx["h"], ctx["opt"]
                lo, hi = (np.array(b, dtype=float) for b in zip(*bounds))
                base, _ = o._compute_baseline_power(WeatherSeries.from_horizon(h), h.initial_state, h.dt,
                                                    h.comfort_targets)
                e = float(np.sum(np.minimum(base, hi)) * h.dt)
                pm = float(o.model.params.max_electrical_power)
                fr = [1.0, om._LOW_ENERGY_START_FRACTION]
                if o.model.params.two_zone_enabled:
                    fr.append(om._DEEP_LOW_ENERGY_START_FRACTION)
                extra = [np.clip(base, lo, hi)] + [
                    np.clip(om._price_ranked_start(np.asarray(h.prices, float)[:len(lo)], e * f, pm, h.dt), lo, hi)
                    for f in fr]
            return cap.ms(objective, list(candidates) + extra, bounds, args, maxiter, batch_objective, move_starts)
    with mock.patch.object(om, "_multi_start_minimize", ms), \
            mock.patch.object(om.HeatPumpOptimizer, "_solve_objectives",
                              cap.solve_objectives(om.HeatPumpOptimizer._solve_objectives)), \
            mock.patch.object(om, "_dhw_build", cap.dhw_build(om._dhw_build)), \
            mock.patch.object(om, "_scoped_minimize", cap.scoped):
        if f == "coordinator.py":
            opt, res = run_coord_cell(arm, profile)
        else:
            opt, res = run_plan_cell(arm, profile)
    return cap, opt, res


# ----------------------------------------------------------------- challengers
def structured_seeds(prices, lo, hi, energy, dt):
    p_max = float(np.max(hi)) if np.max(hi) > 0 else 1.0
    out = []
    for frac in (0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.25, 1.5):
        out.append(np.clip(om._price_ranked_start(np.asarray(prices, float), energy * frac, p_max, dt), lo, hi))
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        out.append(np.clip(lo + frac * (hi - lo), lo, hi))
    return out


def fval(call, x):
    try:
        v = float(call["objective"](np.asarray(x, dtype=float), *call["args"]))
    except Exception:
        return float("inf")
    return v if np.isfinite(v) else float("inf")


def ch_seeds(call, prices, dt):
    lo, hi = (np.array(b, dtype=float) for b in zip(*call["bounds"]))
    e = max(float(np.sum(call["x"]) * dt), 1e-3)
    extra = structured_seeds(prices, lo, hi, e, dt)
    r = ORIG_MS(call["objective"], [c.copy() for c in call["candidates"]] + extra, call["bounds"],
                args=call["args"], maxiter=call["maxiter"], batch_objective=call["batch"],
                move_starts=call["move"])
    return np.asarray(r.x, dtype=float)


def ch_budget(call):
    def big(*a, **k):
        o = dict(k.get("options", {}))
        o["maxiter"] = 10 * int(o.get("maxiter", 300))
        o["maxfun"] = 150000
        k["options"] = o
        return ORIG_SCOPED(*a, **k)
    with mock.patch.object(om, "_scoped_minimize", big):
        r = ORIG_MS(call["objective"], [c.copy() for c in call["candidates"]], call["bounds"],
                    args=call["args"], maxiter=call["maxiter"], batch_objective=call["batch"],
                    move_starts=call["move"])
    return np.asarray(r.x, dtype=float)


def ch_eps(call, eps):
    with mock.patch.object(om, "_LBFGSB_FD_EPS", eps):
        r = ORIG_MS(call["objective"], [c.copy() for c in call["candidates"]], call["bounds"],
                    args=call["args"], maxiter=call["maxiter"], batch_objective=call["batch"],
                    move_starts=call["move"])
    return np.asarray(r.x, dtype=float)


def polish(call, x0, maxiter):
    r = om._lbfgsb_run(call["objective"], call["batch"], np.asarray(x0, dtype=float), call["bounds"],
                       call["args"], maxiter, {})
    r = om._lbfgsb_restart(r, call["objective"], call["bounds"], call["args"], maxiter, call["batch"], {})
    return np.asarray(r.x, dtype=float)


def ch_global(call, steps_per_block=4, seed=0):
    lo, hi = (np.array(b, dtype=float) for b in zip(*call["bounds"]))
    n = len(lo)
    nb = int(np.ceil(n / steps_per_block))
    idx = np.minimum(np.arange(n) // steps_per_block, nb - 1)

    def expand(U):  # U (nb, S) -> (S, n)
        return lo[None, :] + U.T[:, idx] * (hi - lo)[None, :]

    if call["batch"] is not None:
        def f(U):
            U = np.atleast_2d(U.T).T if U.ndim == 1 else U
            vals = np.asarray(call["batch"](expand(U), *call["args"]), dtype=float)
            return np.where(np.isfinite(vals), vals, 1e12)
        vec = True
    else:
        def f(u):
            return fval(call, expand(u[:, None])[0])
        vec = False
    pop = 8 if nb > 24 else 10
    r = differential_evolution(f, [(0.0, 1.0)] * nb, popsize=pop, maxiter=120 if nb <= 24 else 80,
                               seed=seed, polish=False, tol=1e-9, vectorized=vec,
                               updating="deferred" if vec else "immediate", init="sobol")
    xg = expand(np.asarray(r.x)[:, None])[0]
    return polish(call, xg, call["maxiter"]), xg


# ---------------------------------------------------------------- feasibility
def feas(call, x, opt):
    """Bounds, pins, comfort degree-steps (below floor / above ceiling), DHW floor degree-steps."""
    x = np.asarray(x, dtype=float)
    lo, hi = (np.array(b, dtype=float) for b in zip(*call["bounds"]))
    out = {"bound_viol": float(np.sum(np.maximum(0, lo - x) + np.maximum(0, x - hi)))}
    ctx = call["obj_ctx"]
    if ctx is None:
        return out
    h = ctx["h"]
    pins = h.space_pins
    if pins is not None:
        p = np.asarray(pins, dtype=float)[:len(x)]
        out["pin_viol"] = int(np.sum((p == 0.0) & (x > 1e-6)) + np.sum((p >= 0.5) & (x < 1e-6)))
    traj = ctx["traj"](x)
    n = len(x)
    tmin = np.asarray(h.temp_min_bounds, dtype=float)[:n]
    tmax = np.asarray(h.temp_max_bounds, dtype=float)[:n]
    lo_v = hi_v = 0.0
    zones = [traj[0]]
    if opt.model.params.two_zone_enabled:
        zones += [traj[2], traj[3]]
    for z in zones:
        z = np.asarray(z, dtype=float)[-n:]
        lo_v += float(np.sum(np.maximum(0, tmin - z)))
        hi_v += float(np.sum(np.maximum(0, z - tmax)))
    out["comfort_lo"], out["comfort_hi"] = lo_v, hi_v
    plan = call["dhw_ctx"]
    if plan is not None and call["args"] and call["args"][0] is not None:
        dhw = np.asarray(call["args"][0], dtype=float)
        try:
            t = opt.model.simulate_trajectory_with_dhw(
                initial_state=h.initial_state, space_power_schedule=x, dhw_power_schedule=dhw,
                weather=WeatherSeries.from_horizon(h),
                start_hour=h.start_time.hour + h.start_time.minute / 60.0, dt_hours=h.dt,
                dhw_draw_rates=plan.draw_rates, valve_targets=h.valve_targets)
            td = np.asarray(t[4], dtype=float)[-n:]
            fl = np.asarray(plan.floor_temps, dtype=float)[:n]
            out["dhw_lo"] = float(np.sum(np.maximum(0, fl - td)))
        except Exception as err:  # noqa: BLE001
            out["dhw_err"] = str(err)
    return out


def no_worse(c, p):
    if c["bound_viol"] > 1e-7:
        return False
    if c.get("pin_viol", 0) > p.get("pin_viol", 0):
        return False
    for k, tol in (("comfort_lo", COMFORT_TOL), ("comfort_hi", COMFORT_TOL), ("dhw_lo", DHW_TOL)):
        if k in c and c[k] > p.get(k, 0.0) + tol:
            return False
    return True


# ------------------------------------------------------------------------ race
def race_cell(cell, perturb=None, full=True):
    t0, c0 = time.time(), time.process_time()
    cap, opt, res = capture_cell(cell, perturb)
    shipped = np.asarray(res.power_schedule, dtype=float)
    dhw_ship = np.asarray(res.dhw_power_schedule, dtype=float) if getattr(res, "dhw_power_schedule", None) is not None else None
    rows = []
    for ci, call in enumerate(cap.calls):
        ctx = call["obj_ctx"]
        prices = np.asarray(ctx["h"].prices, dtype=float)[:len(call["bounds"])] if ctx else np.ones(len(call["bounds"]))
        dt = float(ctx["h"].dt) if ctx else 0.25
        lo, hi = (np.array(b, dtype=float) for b in zip(*call["bounds"]))
        xp = call["x"]
        fp = fval(call, xp)
        fp_feas = feas(call, xp, opt)
        is_shipped = len(shipped) >= len(xp) and bool(np.allclose(np.clip(xp, lo, hi), shipped[:len(xp)], atol=1e-6))
        row = dict(call=ci, n=len(xp), maxiter=call["maxiter"], n_candidates=len(call["candidates"]),
                   batch=call["batch"] is not None, has_dhw_arg=bool(call["args"]),
                   f_prod=fp, prod_feas=fp_feas, shipped=is_shipped,
                   energy_cost_prod=float(np.sum(prices * xp * dt)), challengers={})
        if perturb is None or full:
            chs = [("seeds", lambda: ch_seeds(call, prices, dt)), ("budget", lambda: ch_budget(call)),
                   ("eps-1e-6", lambda: ch_eps(call, 1e-6)), ("eps-1e-3", lambda: ch_eps(call, 1e-3))]
            if perturb is None:
                chs.append(("global", lambda: ch_global(call)[0]))
            xs = {}
            for name, fn in chs:
                tc = time.process_time()
                try:
                    x = fn()
                    xs[name] = x
                    fe = feas(call, x, opt)
                    row["challengers"][name] = dict(f=fval(call, x), feas=fe, feasible=no_worse(fe, fp_feas),
                                                    cpu_s=round(time.process_time() - tc, 3),
                                                    energy_cost=float(np.sum(prices * x * dt)))
                except Exception as err:  # noqa: BLE001
                    row["challengers"][name] = dict(error=repr(err)[:300])
            ok = {k: v for k, v in row["challengers"].items() if v.get("feasible")}
            if ok:
                bestk = min(ok, key=lambda k: ok[k]["f"])
                try:
                    x = polish(call, xs[bestk], 10 * call["maxiter"])
                    fe = feas(call, x, opt)
                    row["challengers"]["warm"] = dict(f=fval(call, x), feas=fe, feasible=no_worse(fe, fp_feas),
                                                      from_=bestk, energy_cost=float(np.sum(prices * x * dt)))
                except Exception as err:  # noqa: BLE001
                    row["challengers"]["warm"] = dict(error=repr(err)[:300])
            ok = {k: v for k, v in row["challengers"].items() if v.get("feasible")}
            if ok:
                bestk = min(ok, key=lambda k: ok[k]["f"])
                row["best"] = bestk
                row["f_best"] = ok[bestk]["f"]
                row["gap"] = fp - ok[bestk]["f"]
                row["gap_rel"] = row["gap"] / max(abs(fp), 1e-9)
            infeas_better = {k: v["f"] for k, v in row["challengers"].items()
                             if "f" in v and not v.get("feasible") and v["f"] < fp - 1e-9}
            row["infeasible_cheaper"] = infeas_better
        rows.append(row)
    lmax = [r for r in cap.runs]
    out = dict(cell=cell, perturb=perturb, baseline="92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
               n_calls=len(cap.calls), status=str(getattr(res, "status", "")),
               objective_value=float(getattr(res, "objective_value", float("nan"))),
               predicted_cost=float(getattr(res, "predicted_cost", float("nan"))),
               shipped_energy_kwh=float(np.sum(shipped) * 0.25 + (np.sum(dhw_ship) * 0.25 if dhw_ship is not None else 0.0)),
               lbfgsb_runs=len(lmax), lbfgsb_hit_maxiter=sum(1 for s, nit, mi in lmax if s == 1),
               lbfgsb_abnormal=sum(1 for s, nit, mi in lmax if s not in (0, 1)),
               calls=rows, wall_s=round(time.time() - t0, 2), cpu_s=round(time.process_time() - c0, 2),
               thread_factor=round(time.process_time() / max(time.thread_time(), 1e-9), 3))
    return out


def cell_gap(d):
    """The cell's gap: the shipped call's, else the largest over calls (objective units)."""
    sh = [r for r in d["calls"] if r.get("shipped") and "gap" in r]
    pool = sh or [r for r in d["calls"] if "gap" in r]
    if not pool:
        return None
    r = max(pool, key=lambda r: r["gap"])
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", default="", help="substring filter on cells for --all")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--perturb", choices=["seeds-in-production", "thermostat-anchor"])
    ap.add_argument("--aggregate", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.cell:
        d = race_cell(a.cell, a.perturb, full=a.perturb is None)
        tag = a.cell.replace("/", "__") + (f"__{a.perturb}" if a.perturb else "")
        (OUT / f"{tag}.json").write_text(json.dumps(d, indent=1, default=float))
        r = cell_gap(d)
        print(f"RESULT f_prod[{a.cell}]={d['calls'][0]['f_prod'] if d['calls'] else 'nan'} objective")
        if r:
            print(f"RESULT gap[{a.cell}]={r['gap']:.6g} objective")
            print(f"RESULT gap_rel[{a.cell}]={r['gap_rel']:.6g} ratio")
            print(f"RESULT best[{a.cell}]={r['best']}")
        print(f"RESULT cpu_s[{a.cell}]={d['cpu_s']} s provisional")
        print(f"RESULT thread_factor={d['thread_factor']}")
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
        return
    if a.all:
        todo = [c for c in cellmod.cells() if a.only in c]
        todo = [c for c in todo if not (OUT / (c.replace('/', '__') + '.json')).exists()]
        procs = []
        env = dict(os.environ)
        for c in todo:
            while len([p for p in procs if p.poll() is None]) >= a.jobs:
                time.sleep(0.5)
            procs.append(subprocess.Popen([sys.executable, __file__, "--cell", c], env=env))
        for p in procs:
            p.wait()
        return
    if a.aggregate:
        aggregate()


def aggregate():
    rows = []
    for c in cellmod.cells():
        p = OUT / (c.replace("/", "__") + ".json")
        if not p.exists():
            print(f"MISSING {c}")
            continue
        d = json.loads(p.read_text())
        r = cell_gap(d)
        rows.append((c, d, r))
    gaps = [(c, r["gap"], r["gap_rel"], r["best"]) for c, d, r in rows if r]
    for c, g, gr, b in sorted(gaps, key=lambda t: -t[2]):
        print(f"{c:60s} gap={g:10.5f} rel={gr*100:8.4f}% best={b}")
    rel = np.array([g[2] for g in gaps])
    print(f"RESULT cells_raced={len(rows)} count")
    print(f"RESULT cells_gap_gt_0.1pct={int(np.sum(rel > 1e-3))} count")
    print(f"RESULT cells_gap_gt_1pct={int(np.sum(rel > 1e-2))} count")
    if len(rel) >= 5:
        print(f"RESULT gap_rel_mean={rel.mean():.6g} ratio")
        print(f"RESULT gap_rel_range={rel.min():.6g}..{rel.max():.6g} ratio")
        drop = np.delete(rel, int(np.argmax(rel)))
        print(f"RESULT gap_rel_mean_drop_most_favourable={drop.mean():.6g} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
