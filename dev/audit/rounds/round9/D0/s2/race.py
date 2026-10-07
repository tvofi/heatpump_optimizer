"""D0-s2 capture-and-race harness (round 9, D0.M1-M4).

Metric (one line): per captured `_multi_start_minimize` call, gap =
(f_prod - f_best_challenger) / |f_prod| on the EXACT recorded objective,
bounds and args, where challengers are (a) production's own L-BFGS-B
re-polished from the shipped point at ftol=1e-12, (b) the recorded
candidates plus bang-bang seeds at energy fractions of the bounds' max
energy re-raced through the production seam, and (c) a re-polish of (b).
Count key: the objective value the production closure returns (never an
input attribute).

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
      tools/audit/round9/D0/s2/race.py [--cells summer_typical,...] \
      [--weather ...] [--tz 0,1] [--dhw 0,1] [--horizon 24] \
      [--perturb deep_anchor_dhw|maxiter_hi|add_emax_ladder|none] [--out FILE]

Expected: see REPORT.md per-cell tables (gap values exact to ~1e-6 rel on
this box; BLAS-dependent across boxes).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Machine: box B2, 4-CPU Linux container, python 3.14 venv, OpenBLAS.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "VECLIB_MAXIMUM_OPERATIONS"):
    os.environ.setdefault(_v, "1")
import sys, json, time, argparse, tempfile
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from unittest import mock
from profiles import prices, weather, house, DT
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
import heatpump_optimizer.optimizer as M

START = datetime(2026, 1, 15)
LADDER = (0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)


def closure_map(fn):
    return {n: c.cell_contents for n, c in
            zip(fn.__code__.co_freevars, fn.__closure__ or ())}


def inputs(tz, pp, wp, dhw, horizon):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(pp, START)
    ot, wi, ra, so = weather(wp, START)
    if horizon > 24:
        k = int(np.ceil(horizon / 24))
        pr, ot, wi, ra, so = (np.tile(a, k) for a in (pr, ot, wi, ra, so))
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return o, m, pr, ot, wi, ra, so, st


def capture(o, pr, ot, wi, ra, so, st, perturb):
    calls = []
    nits = []
    real_ms = M._multi_start_minimize
    real_sc = M._scoped_minimize

    def rec(objective, candidates, bounds, *a, **kw):
        if perturb == "maxiter_hi":
            kw["maxiter"] = 2000
        if perturb == "add_emax_ladder":
            # Perturbation: hand production's own seam the challenger's
            # bang-bang seeds (fractions of the bounds' max energy).
            ub = np.array(bounds, float)[:, 1]
            prs = obj_prices({"objective": objective})
            candidates = list(candidates) + [
                np.minimum(M._price_ranked_start(
                    prs, float(ub.sum() * DT) * fr, float(ub.max()), DT), ub)
                for fr in LADDER]
        res = real_ms(objective, candidates, bounds, *a, **kw)
        calls.append(dict(
            objective=objective,
            candidates=[np.asarray(c, float).copy() for c in candidates],
            bounds=[tuple(float(x) for x in b) for b in bounds],
            args=tuple(kw.get("args", a[0] if a else ())),
            maxiter=kw.get("maxiter", 300),
            batch=kw.get("batch_objective"),
            fd_eps=kw.get("fd_eps", 1e-4),
            x=np.asarray(res.x, float).copy(),
        ))
        return res

    def sc(*a, **kw):
        r = real_sc(*a, **kw)
        nits.append((int(r.nit), int(kw["options"]["maxiter"])))
        return r

    patches = [mock.patch.object(M, "_multi_start_minimize", rec),
               mock.patch.object(M, "_scoped_minimize", sc)]
    if perturb == "deep_anchor_dhw":
        # Perturbation: give the with-DHW space seam the two-zone deep
        # 0.20x anchor the space-only seam carries.
        real_solve = HeatPumpOptimizer._solve_space

        def solve_space(self, dhw_plan, warm_start, h, p_max, n, dt, prs,
                        init_base, *rest):
            if warm_start is None and self.model.params.two_zone_enabled:
                head = np.maximum(0.0, p_max - dhw_plan)
                e = float(np.sum(np.minimum(init_base, head)) * dt)
                seed = np.minimum(M._price_ranked_start(
                    prs, e * M._DEEP_LOW_ENERGY_START_FRACTION, p_max, dt),
                    head)
                import dataclasses
                h2 = dataclasses.replace(
                    h, extra_starts=tuple(h.extra_starts or ()) + (seed,))
                return real_solve(self, dhw_plan, warm_start, h2, p_max,
                                  n, dt, prs, init_base, *rest)
            return real_solve(self, dhw_plan, warm_start, h, p_max, n, dt,
                              prs, init_base, *rest)
        patches.append(mock.patch.object(HeatPumpOptimizer, "_solve_space",
                                         solve_space))
    for p in patches:
        p.start()
    try:
        r = o.optimize(st, pr, ot, wi, ra, so, START)
    finally:
        for p in reversed(patches):
            p.stop()
    return r, calls, nits


def jac_for(c):
    b = c["bounds"]
    if c["batch"] is None or not M._bounds_supported_by_batch(b):
        return None
    obj, bo, eps = c["objective"], c["batch"], c["fd_eps"]

    def j(x, *a):
        return M._batch_fd_gradient(bo, a, x, float(obj(x, *a)), eps, b)
    return j


def polish(c, x0):
    r = M._scoped_minimize(c["objective"], np.asarray(x0, float),
                           args=c["args"], jac=jac_for(c), method="L-BFGS-B",
                           bounds=c["bounds"],
                           options={"maxiter": 5000, "ftol": 1e-12,
                                    "gtol": 1e-10, "eps": 1e-4})
    return np.asarray(r.x, float)


def violation(c, x):
    cm = closure_map(c["objective"])
    traj = cm["_space_traj"](x)
    tmin = cm["temp_min_bounds"]
    if cm["self"].model.params.two_zone_enabled:
        zs = (traj[2][1:], traj[3][1:])
    else:
        zs = (traj[0][1:],)
    return float(sum(np.maximum(0, tmin - z).sum() for z in zs))


def obj_prices(c):
    """The prices the recorded objective prices energy at (its closure)."""
    return np.asarray(closure_map(
        closure_map(c["objective"])["energy_cost_of"])["prices"], float)


def energy_sek(c, x, prs):
    extra = c["args"][0] if c["args"] else 0.0
    return float(np.sum(prs * (x + extra)) * DT)


def race(c, prs):
    f = lambda x: float(c["objective"](x, *c["args"]))
    ub = np.array(c["bounds"])[:, 1]
    emax = float(ub.sum() * DT)
    pmax = float(ub.max()) if ub.size else 0.0
    f0 = f(c["x"])
    arms = {}
    xp = polish(c, c["x"]); arms["polish"] = xp
    seeds = [np.minimum(M._price_ranked_start(prs, emax * fr, pmax, DT), ub)
             for fr in LADDER]
    # seed-wise: which fraction wins alone
    rl = M._multi_start_minimize(c["objective"], c["candidates"] + seeds,
                                 c["bounds"], args=c["args"],
                                 maxiter=c["maxiter"],
                                 batch_objective=c["batch"],
                                 fd_eps=c["fd_eps"])
    xl = np.asarray(rl.x, float); arms["ladder"] = xl
    arms["ladder_polish"] = polish(c, xl)
    scores = {k: f(v) for k, v in arms.items()}
    kbest = min(scores, key=scores.get)
    xb = arms[kbest]
    return dict(
        f_prod=f0, f_best=scores[kbest], best_arm=kbest,
        gap_rel=(f0 - scores[kbest]) / abs(f0) if f0 else 0.0,
        gap_abs=f0 - scores[kbest],
        gap_polish=(f0 - scores["polish"]) / abs(f0) if f0 else 0.0,
        gap_ladder=(f0 - min(scores["ladder"], scores["ladder_polish"])) / abs(f0) if f0 else 0.0,
        viol_prod=violation(c, c["x"]), viol_best=violation(c, xb),
        e_prod=energy_sek(c, c["x"], prs), e_best=energy_sek(c, xb, prs),
        kwh_prod=float(c["x"].sum() * DT), kwh_best=float(xb.sum() * DT),
        step0_prod=float(c["x"][0]), step0_best=float(xb[0]),
        n_cand=len(c["candidates"]), maxiter=c["maxiter"],
        two_arg=bool(c["args"]),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="summer_typical,summer_negative,shoulder,flat")
    ap.add_argument("--weather", default="winter_cold,winter_mild,summer_warm,summer_cool,shoulder")
    ap.add_argument("--tz", default="0,1")
    ap.add_argument("--dhw", default="0,1")
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--perturb", default="none")
    ap.add_argument("--first-only", action="store_true",
                    help="race only the first seam call per cell")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(tempfile.mkdtemp(prefix="d0s2_"), "cells.jsonl")
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    rows = []
    with open(out, "w") as fh:
        for pp in a.cells.split(","):
            for wp in a.weather.split(","):
                for tz in (bool(int(x)) for x in a.tz.split(",")):
                    for dhw in (bool(int(x)) for x in a.dhw.split(",")):
                        o, m, pr, ot, wi, ra, so, st = inputs(tz, pp, wp, dhw, a.horizon)
                        r, calls, nits = capture(o, pr, ot, wi, ra, so, st, a.perturb)
                        prs = np.asarray(pr[: len(calls[0]["x"])] if calls else pr, float)
                        # the prices the objective sees are the stashed ones
                        cm = closure_map(calls[0]["objective"]) if calls else {}
                        cell = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|h{a.horizon}"
                        hit = sum(1 for n, mx in nits if n >= mx)
                        for ci, c in enumerate(calls):
                            if a.first_only and ci:
                                break
                            prs_c = obj_prices(c)
                            res = race(c, prs_c)
                            res.update(cell=cell, call=ci, n_calls=len(calls),
                                       shipped_obj=float(r.objective_value),
                                       maxiter_hits=hit, n_runs=len(nits),
                                       perturb=a.perturb)
                            rows.append(res)
                            fh.write(json.dumps(res) + "\n"); fh.flush()
                            print(f"{cell:48s} call{ci}/{len(calls)} f={res['f_prod']:.5f} "
                                  f"gap={100*res['gap_rel']:+.4f}% ({res['gap_abs']:+.4f}) "
                                  f"pol={100*res['gap_polish']:+.4f}% lad={100*res['gap_ladder']:+.4f}% "
                                  f"arm={res['best_arm']} viol {res['viol_prod']:.4f}->{res['viol_best']:.4f} "
                                  f"kWh {res['kwh_prod']:.1f}->{res['kwh_best']:.1f} "
                                  f"s0 {res['step0_prod']:.2f}->{res['step0_best']:.2f} hits={hit}/{len(nits)}",
                                  flush=True)
    tp, tt = time.process_time() - t_proc0, time.thread_time() - t_thr0
    gaps = [r["gap_rel"] for r in rows if r["call"] == 0]
    print(f"RESULT cells={len(gaps)} count")
    if gaps:
        g = np.array(gaps)
        print(f"RESULT gap_max={100*g.max():.4f} %")
        print(f"RESULT gap_mean={100*g.mean():.4f} %")
        print(f"RESULT cells_over_0p1pct={int((g > 1e-3).sum())} count")
        if len(g) >= 5:
            print(f"RESULT gap_mean_drop_worst={100*np.sort(g)[:-1].mean():.4f} %")
    print(f"RESULT rows_file={out}")
    print(f"RESULT thread_factor={tp / max(tt, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
