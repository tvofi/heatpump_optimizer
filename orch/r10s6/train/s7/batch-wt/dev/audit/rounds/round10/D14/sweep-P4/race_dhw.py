"""D0-s1 race: production multi-start vs challengers on the SAME captured objective.

Metric: per captured `_multi_start_minimize` call inside `HeatPumpOptimizer.optimize`,
  gap_rel = (f(prod.x) - min_feasible_challenger f(x)) / |f(prod.x)|, f = the captured
  production objective (comfort, cycling, everything it prices), challengers are counted
  only if their simulated room trajectory violates the [min,max] band by no more
  degree-steps than production's (feasibility parity, D0.M3) and stay inside the bounds.
  Count key: the captured objective's value at the x the production seam returns.
Challengers (D0.M2): C1 production candidates + structured seeds (price-ranked bang-bang
  at 0.3/0.5/0.7/1.0/1.3 x prod energy, constant 0/25/50/75/100 % of ub, prod.x) through
  the production `_multi_start_minimize` itself (same jac path); C2 warm L-BFGS-B from the
  C1 best with maxiter 5000, maxfun 1e6, ftol 1e-12, gtol 1e-10, same batched jac;
  C3 = C2 with fd eps 1e-6.
Command:  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
            dev/audit/rounds/round10/D0/s1/race.py [--prices a,b] [--weather a,b] [--tz 0,1]
            [--dhw 0|1] [--perturb-maxiter N] [--perturb-fd-eps E]
Perturbation: --perturb-maxiter 2000 runs the production call at maxiter 2000 (gap must
  NOT go down: measured flat, the call converges before its budget); --perturb-maxiter 20
  (gap goes up). --perturb-fd-eps 1e-6 hands the production call's batched-FD jac a 1e-6
  step instead of 1e-4 (gap must go down: the finding's mechanism).
Expected: see REPORT.md (counts/ratios exact to ~1e-3 relative across BLAS builds).
Baseline 17f1c55fad1b; machine: Apple Silicon macOS (B1), venv-ci python.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from unittest import mock
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
from profiles import prices, weather, house, DT, N, solve_inputs
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)

ap = argparse.ArgumentParser()
ap.add_argument("--prices", default="winter_typical,winter_extreme,winter_narrow,winter_moderate,"
                "summer_typical,summer_negative,shoulder,flat")
ap.add_argument("--weather", default="winter_cold,winter_mild,summer_warm,summer_cool,shoulder")
ap.add_argument("--tz", default="0,1")
ap.add_argument("--dhw", type=int, default=0)
ap.add_argument("--horizon", type=int, default=24)
ap.add_argument("--perturb-maxiter", type=int, default=0)
ap.add_argument("--perturb-fd-eps", type=float, default=0.0)
a = ap.parse_args()

ORIG = O._multi_start_minimize
START = datetime(2026, 1, 15)
MINT, MAXT = 17.0, 23.0


def setup(tz, pp, wp, dhw, horizon):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = bool(dhw)
    m = ThermalModel(p)
    opt = O.HeatPumpOptimizer(m, O.OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=MINT, max_temp=MAXT))
    n = horizon * 4
    pr = prices(pp, START)[:n]
    ot, wi, ra, so = (s[:n] for s in weather(wp, START))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      **({"dhw_temperature": 50.0} if dhw else {}))
    return opt, m, pr, ot, wi, ra, so, st


def viol(m, x, st, ot, wi, ra, so):
    room = m.simulate_trajectory(st, x, WeatherSeries(outdoor_temps=ot, wind_speeds=wi,
                                 precipitation=ra, solar_radiation=so), dt_hours=DT)[0][1:]
    return float(np.maximum(0, MINT - room).sum() + np.maximum(0, room - MAXT).sum())


def challenge(cap, pr):
    obj, cands, bounds, args, maxiter, bobj = (cap[k] for k in
        ("objective", "candidates", "bounds", "args", "maxiter", "batch_objective"))
    lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
    px = np.asarray(cap["result"].x, float)
    n = len(lb)
    p = pr[:n] if len(pr) >= n else np.resize(pr, n)
    energy = float(px.sum())
    seeds = [px.copy()]
    order = np.argsort(p, kind="stable")
    for frac in (0.3, 0.5, 0.7, 1.0, 1.3):
        s = np.zeros(n); left = energy * frac
        for i in order:
            t = min(ub[i], left); s[i] = t; left -= t
            if left <= 0: break
        seeds.append(s)
    for c in (0, .25, .5, .75, 1.0):
        seeds.append(ub * c)
    seeds = [np.clip(s, lb, ub) for s in seeds]
    nf = [0]
    def cobj(x, *aa):
        nf[0] += 1
        return obj(x, *aa)
    c1 = ORIG(cobj, list(cands) + seeds, bounds, args=args, maxiter=maxiter,
              batch_objective=bobj)
    best = np.asarray(c1.x, float)
    out = {"c1": best}
    for tag, eps in (("c2", 1e-4), ("c3", 1e-6)):
        memo = O._memoized_value_and_gradient(bobj, bounds, eps, {})
        if memo is not None and O._bounds_supported_by_batch(bounds):
            fun, jac = memo, True
        else:
            fun, jac = obj, None
        r = minimize(fun, best, args=args, jac=jac, method="L-BFGS-B", bounds=bounds,
                     options={"maxiter": 5000, "maxfun": 10**6, "ftol": 1e-12,
                              "gtol": 1e-10, "eps": eps})
        out[tag] = np.clip(np.asarray(r.x, float), lb, ub)
    return out, nf[0]


rows = []
pt0 = time.process_time(); tt0 = time.thread_time()
for tz in [int(t) for t in a.tz.split(",")]:
    for pp in a.prices.split(","):
        for wp in a.weather.split(","):
            opt, m, pr, ot, wi, ra, so, st = setup(tz, pp, wp, a.dhw, a.horizon)
            caps = []
            def wrap(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
                     fd_eps=1e-4, move_starts=lambda c, mi: c):
                mi = a.perturb_maxiter or maxiter
                cands = [np.array(c, float) for c in candidates]
                res = ORIG(objective, candidates, bounds, args=args, maxiter=mi,
                           batch_objective=batch_objective, fd_eps=a.perturb_fd_eps or fd_eps, move_starts=move_starts)
                caps.append(dict(objective=objective, candidates=cands, bounds=bounds,
                                 args=args, maxiter=maxiter, batch_objective=batch_objective,
                                 result=res))
                return res
            with mock.patch.object(O, "_multi_start_minimize", wrap):
                opt.optimize(inputs=solve_inputs(initial_state=st, prices=pr, outdoor_temps=ot,
                             wind_speeds=wi, precipitation=ra, solar_radiation=so,
                             start_time=START))
            for ci, cap in enumerate(caps):
                obj, args = cap["objective"], cap["args"]
                px = np.asarray(cap["result"].x, float)
                fp = float(obj(px, *args))
                space_call = len(px) == len(pr) and not args  # space-only path
                vp = viol(m, px, st, ot, wi, ra, so) if space_call else 0.0
                chal, nf = challenge(cap, pr)
                best_f, best_k, best_x = fp, "prod", px
                disc = 0; per = {}
                for k, x in chal.items():
                    f = float(obj(x, *args)); per[k] = (fp - f) / max(abs(fp), 1e-12)
                    if space_call and viol(m, x, st, ot, wi, ra, so) > vp + 1e-6:
                        disc += 1; continue
                    if f < best_f:
                        best_f, best_k, best_x = f, k, x
                gap = (fp - best_f) / max(abs(fp), 1e-12)
                dsek = float(np.sum(pr[:len(px)] * (px - best_x) * DT)) if space_call else float("nan")
                bill = float(np.sum(pr[:len(px)] * px * DT)) if space_call else float("nan")
                rows.append((tz, pp, wp, ci, fp, best_f, gap, best_k, dsek, bill, disc))
                print(f"cell tz={tz} {pp:16s} {wp:12s} call{ci} f_prod={fp:.5f} f_best={best_f:.5f} "
                      f"gap_rel={gap:.3e} by={best_k} dSEK={dsek:.3f} bill={bill:.2f} "
                      f"infeasible_discarded={disc} "
                      + " ".join(f"{k}={v:.2e}" for k, v in per.items()), flush=True)

g = np.array([r[6] for r in rows])
print(f"RESULT cells={len(rows)} count")
print(f"RESULT gap_rel_max={g.max():.4e} ratio")
print(f"RESULT gap_rel_mean={g.mean():.4e} ratio")
print(f"RESULT cells_gap_gt_1e-3={int((g > 1e-3).sum())} count")
print(f"RESULT cells_gap_gt_1e-2={int((g > 1e-2).sum())} count")
if len(g) > 1:
    print(f"RESULT gap_rel_mean_drop_max={np.sort(g)[:-1].mean():.4e} ratio")
nonflat = np.array([r[6] for r in rows if r[1] != "flat"])
flat = np.array([r[6] for r in rows if r[1] == "flat"])
if len(flat): print(f"RESULT flat_gap_rel_max={flat.max():.4e} ratio")
if len(nonflat): print(f"RESULT nonflat_gap_rel_max={nonflat.max():.4e} ratio")
pt = time.process_time() - pt0; tt = time.thread_time() - tt0
print(f"RESULT thread_factor={pt / max(tt, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
except Exception:
    print("RESULT swapins=nan")
