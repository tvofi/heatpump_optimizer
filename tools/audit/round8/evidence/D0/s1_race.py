"""D0 round 8, seat s1: seeding, multi-start and solver-budget race.

Metric (one line): per cell, rel_gap = (J_prod - J_best_challenger) / |J_prod| on the
EXACT objective production handed ``optimizer:_multi_start_minimize`` (captured by
mock.patch.object, same bounds, same args, same batched-jac path), where a challenger
counts only if its end-to-end plan holds comfort no worse than production (room
degree-steps below min_temp, DHW schedule identical).

Count key: the objective value production's own captured ``objective`` returns for the
``res.x`` the seam delivers -- never an input attribute.

Command (from the tree root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python3 tools/audit/round8/D0/s1_race.py [--dhw 0|1] [--prices p1,p2] [--weather w1,w2] \
        [--perturb NAME]

--perturb (applied to production inside try/finally, restored):
    seeds_plus  : production _multi_start_minimize receives the challenger seed set in
                  addition to its own candidates (the proposed fix shape) -> gap to_zero
    none        : baseline

Expected (baseline cdf82daa, 4-vCPU cloud container): see REPORT-s1.md; counts exact,
rel gaps +-1e-6 absolute (BLAS float drift).

Arms per captured call:
  prod      production result (all candidates refined + polished, maxiter as passed)
  percand   each production candidate refined ALONE through production's own
            _multi_start_minimize (which candidate's basin wins; spread)
  seeds     bang-bang (_price_ranked_start) at energy fractions F of the production
            plan's energy, plus all-zero and all-upper-bound, each through production
            _multi_start_minimize (same maxiter, same jac)
  budget    production candidates, L-BFGS-B at maxiter 20000, maxfun 1e6, ftol 1e-13,
            gtol 1e-10, same batched jac (production's _batch_fd_gradient)
  eps6/eps3 production candidates, fd_eps 1e-6 / 1e-3 via production's own kwarg
  cd        derivative-free coordinate search from the best arm (moves: x_i to lb, ub,
            x_i +- 0.25/1.0 kW; evaluated through the production batch objective),
            alternated with a production L-BFGS-B polish; an outer bound, not a fix
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from unittest import mock
from scipy.optimize import minimize
from profiles import prices, weather, house, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import optimizer as O

PRICES = ["winter_typical", "winter_extreme", "summer_typical", "summer_negative",
          "shoulder", "winter_narrow", "winter_moderate", "flat"]
WEATHER = ["winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder"]
FRACS = [0.10, 0.20, 0.50, 0.65, 0.80, 1.00, 1.20, 1.50]
START = datetime(2026, 1, 15)
ORIG_MS = O._multi_start_minimize
ORIG_SCOPED = O._scoped_minimize


def setup(price_p, weather_p, dhw, two_zone=False):
    cfg = house(two_zone=two_zone)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    opt = O.HeatPumpOptimizer(m, O.OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    return opt, m, pr, ot, wi, ra, so, st


class Res:
    def __init__(self, x, fun, nit=0, success=True, message="challenger"):
        self.x = np.asarray(x, dtype=float)
        self.fun = fun
        self.nit = nit
        self.success = success
        self.message = message
        self.status = 0


def _budget_arm(objective, cands, bounds, args, batch):
    best, bs = None, np.inf
    nits = []
    for g in cands:
        def jac(x, *a):
            return O._batch_fd_gradient(batch, a, x, float(objective(x, *a)), 1e-4, bounds)
        r = minimize(objective, g, args=args, jac=jac if batch is not None else None,
                     method="L-BFGS-B", bounds=bounds,
                     options={"maxiter": 20000, "maxfun": 10**6, "ftol": 1e-13,
                              "gtol": 1e-10, "eps": 1e-4})
        nits.append(int(r.nit))
        s = float(objective(r.x, *args))
        if s < bs:
            best, bs = r.x, s
    return best, bs, nits


def _cd_arm(objective, x0, bounds, args, batch, maxiter, rounds=40):
    """Coordinate moves via the production batch objective, alternated with polish."""
    lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
    x = np.clip(np.asarray(x0, float), lb, ub)
    fx = float(objective(x, *args))
    n = x.size
    for _ in range(rounds):
        moves = []
        for target in ("lb", "ub", 0.25, -0.25, 1.0, -1.0):
            X = np.tile(x, (n, 1))
            idx = np.arange(n)
            if target == "lb":
                X[idx, idx] = lb
            elif target == "ub":
                X[idx, idx] = ub
            else:
                X[idx, idx] = np.clip(x + target, lb, ub)
            moves.append(X)
        X = np.vstack(moves)
        if batch is not None:
            f = np.asarray(batch(X, *args), dtype=float)
        else:
            f = np.array([objective(r, *args) for r in X])
        k = int(np.argmin(f))
        if not f[k] < fx - 1e-12 * max(1.0, abs(fx)):
            break
        x = X[k].copy()
        fx = float(objective(x, *args))
        r = ORIG_MS(objective, [x], bounds, args=args, maxiter=maxiter, batch_objective=batch)
        fr = float(objective(r.x, *args))
        if fr < fx:
            x, fx = np.asarray(r.x, float), fr
    return x, fx


def race_call(objective, cands, bounds, args, maxiter, batch, dt, pr_prices, arms):
    out = {}
    prod = ORIG_MS(objective, cands, bounds, args=args, maxiter=maxiter, batch_objective=batch)
    jp = float(objective(prod.x, *args))
    out["prod"] = jp
    ub = np.array([b[1] for b in bounds]); lb = np.array([b[0] for b in bounds])
    xs = {"prod": np.asarray(prod.x, float)}
    # which candidate wins, pre-score ranking
    pre = [float(objective(c, *args)) for c in cands]
    per = []
    for c in cands:
        r = ORIG_MS(objective, [c], bounds, args=args, maxiter=maxiter, batch_objective=batch)
        per.append(float(objective(r.x, *args)))
    out["percand"] = per
    out["prescore"] = pre
    out["n_cands"] = len(cands)
    if "seeds" in arms:
        E = float(np.sum(prod.x) * dt)
        seeds = [np.clip(O._price_ranked_start(pr_prices, E * f, float(ub.max()), dt), lb, ub)
                 for f in FRACS]
        seeds += [lb.copy(), ub.copy()]
        best, bs = None, np.inf
        seed_scores = []
        for s in seeds:
            r = ORIG_MS(objective, [s], bounds, args=args, maxiter=maxiter, batch_objective=batch)
            v = float(objective(r.x, *args))
            seed_scores.append(v)
            if v < bs:
                best, bs = np.asarray(r.x, float), v
        out["seeds"] = bs
        out["seed_scores"] = seed_scores
        xs["seeds"] = best
    if "budget" in arms:
        bx, bsc, nits = _budget_arm(objective, cands, bounds, args, batch)
        out["budget"] = bsc; out["budget_nits"] = nits
        xs["budget"] = bx
    if "eps" in arms:
        for tag, e in (("eps6", 1e-6), ("eps3", 1e-3)):
            r = ORIG_MS(objective, cands, bounds, args=args, maxiter=maxiter,
                        batch_objective=batch, fd_eps=e)
            out[tag] = float(objective(r.x, *args)); xs[tag] = np.asarray(r.x, float)
    if "cd" in arms:
        k0 = min(xs, key=lambda k: float(objective(xs[k], *args)))
        cx, cf = _cd_arm(objective, xs[k0], bounds, args, batch, maxiter)
        out["cd"] = cf; xs["cd"] = cx
    return out, xs


def run_cell(price_p, weather_p, dhw, arms, perturb="none", two_zone=False):
    opt, m, pr, ot, wi, ra, so, st = setup(price_p, weather_p, dhw, two_zone)
    records = []
    nits = []

    def scoped(*a, **k):
        r = ORIG_SCOPED(*a, **k)
        nits.append((int(r.nit), int(r.nfev), str(r.message)))
        return r

    def capture(objective, cands, bounds, *a, **k):
        args = k.get("args", a[0] if a else ())
        maxiter = k.get("maxiter", 300)
        batch = k.get("batch_objective")
        if perturb == "seeds_plus":
            ubv = np.array([b[1] for b in bounds]); lbv = np.array([b[0] for b in bounds])
            base = ORIG_MS(objective, cands, bounds, args=args, maxiter=maxiter,
                           batch_objective=batch)
            E = float(np.sum(base.x) * DT)
            extra = [np.clip(O._price_ranked_start(pr, E * f, float(ubv.max()), DT), lbv, ubv)
                     for f in FRACS] + [lbv.copy(), ubv.copy()]
            return ORIG_MS(objective, list(cands) + extra, bounds, args=args,
                           maxiter=maxiter, batch_objective=batch)
        nits.clear()
        r = ORIG_MS(objective, cands, bounds, *a, **k)
        rec = {"maxiter": maxiter, "n_bounds": len(bounds), "lbfgsb_runs": list(nits),
               "batch": batch is not None}
        if arms:
            res, xs = race_call(objective, cands, bounds, args, maxiter, batch, DT, pr, arms)
            rec.update(res)
            rec["_xs"] = xs
            rec["_obj"] = (objective, args)
        records.append(rec)
        return r

    with mock.patch.object(O, "_multi_start_minimize", capture), \
            mock.patch.object(O, "_scoped_minimize", scoped):
        r_prod = opt.optimize(st, pr, ot, wi, ra, so, START)
    out = {"cell": f"{price_p}|{weather_p}|dhw={int(dhw)}|tz={int(two_zone)}",
           "calls": len(records),
           "prod_objective_value": float(r_prod.objective_value),
           "prod_cost": float(r_prod.predicted_cost),
           "prod_min_room": float(np.min(r_prod.room_temp_trajectory[1:])),
           "prod_room_short": float(np.maximum(0.0, 17.0 - np.asarray(r_prod.room_temp_trajectory[1:])).sum())}
    if not arms or not records:
        out["records"] = records
        return out
    # end-to-end feasibility parity: inject the best challenger x at the FIRST call
    rec0 = records[0]
    obj0, args0 = rec0.pop("_obj")
    xs = rec0.pop("_xs")
    for rr in records[1:]:
        rr.pop("_obj", None); rr.pop("_xs", None)
    kbest = min((k for k in xs if k != "prod"), key=lambda k: float(obj0(xs[k], *args0)))
    injected = {"done": False}

    def inject(objective, cands, bounds, *a, **k):
        r = ORIG_MS(objective, cands, bounds, *a, **k)
        if not injected["done"]:
            injected["done"] = True
            args = k.get("args", a[0] if a else ())
            xb = xs[kbest]
            if float(objective(xb, *args)) < float(objective(r.x, *args)):
                return Res(xb, float(objective(xb, *args)))
        return r

    with mock.patch.object(O, "_multi_start_minimize", inject):
        r_ch = opt.optimize(st, pr, ot, wi, ra, so, START)
    out.update({
        "best_arm": kbest,
        "chal_objective_value": float(r_ch.objective_value),
        "chal_cost": float(r_ch.predicted_cost),
        "chal_min_room": float(np.min(r_ch.room_temp_trajectory[1:])),
        "chal_room_short": float(np.maximum(0.0, 17.0 - np.asarray(r_ch.room_temp_trajectory[1:])).sum()),
        "dhw_identical": bool(np.array_equal(np.asarray(r_prod.dhw_power_schedule),
                                             np.asarray(r_ch.dhw_power_schedule))),
        "step0_prod": float(r_prod.power_schedule[0]),
        "step0_chal": float(r_ch.power_schedule[0]),
    })
    out["records"] = records
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dhw", default="0")
    ap.add_argument("--tz", default="0")
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default=",".join(WEATHER))
    ap.add_argument("--arms", default="seeds,budget,eps,cd")
    ap.add_argument("--perturb", default="none")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    arms = [x for x in a.arms.split(",") if x]
    cpu0, th0 = time.process_time(), time.thread_time()
    rows = []
    for p in a.prices.split(","):
        for w in a.weather.split(","):
            if a.perturb != "none":
                # the fix-shape arm: production sees extra seeds; race the SAME challengers
                base = run_cell(p, w, a.dhw == "1", [], "none", a.tz == "1")
                pert = run_cell(p, w, a.dhw == "1", [], a.perturb, a.tz == "1")
                row = {"cell": base["cell"], "prod_obj": base["prod_objective_value"],
                       "pert_obj": pert["prod_objective_value"],
                       "rel": (base["prod_objective_value"] - pert["prod_objective_value"]) /
                              abs(base["prod_objective_value"])}
                rows.append(row)
                print(f"CELL {row['cell']} prod={row['prod_obj']:.6f} perturbed={row['pert_obj']:.6f} rel={row['rel']:.3e}")
                continue
            r = run_cell(p, w, a.dhw == "1", arms, "none", a.tz == "1")
            rows.append(r)
            rec = r["records"][0]
            jp = rec["prod"]
            arm_vals = {k: rec[k] for k in ("seeds", "budget", "eps6", "eps3", "cd") if k in rec}
            jb = min(arm_vals.values()) if arm_vals else jp
            rel = (jp - jb) / abs(jp)
            r["rel_gap"] = rel
            feas = r.get("chal_room_short", 0) <= r["prod_room_short"] + 1e-9 and r.get("dhw_identical", True)
            r["feasible"] = feas
            e2e = (r["prod_objective_value"] - r.get("chal_objective_value", r["prod_objective_value"])) / abs(r["prod_objective_value"])
            r["e2e_rel"] = e2e
            win = int(np.argmin(rec["percand"]))
            spread = (max(rec["percand"]) - min(rec["percand"])) / abs(jp)
            maxnit = max(x[0] for x in rec["lbfgsb_runs"])
            print(f"CELL {r['cell']} calls={r['calls']} maxiter={rec['maxiter']} ncand={rec['n_cands']} "
                  f"J_prod={jp:.6f} " + " ".join(f"{k}={(jp - v) / abs(jp):+.3e}" for k, v in arm_vals.items()) +
                  f" best={r.get('best_arm')} gap={rel:.3e} e2e={e2e:.3e} feas={feas} "
                  f"cost {r['prod_cost']:.3f}->{r.get('chal_cost', float('nan')):.3f} "
                  f"step0 {r.get('step0_prod', 0):.3f}->{r.get('step0_chal', 0):.3f} "
                  f"win_cand={win} cand_spread={spread:.3e} max_nit={maxnit} "
                  f"budget_nits={rec.get('budget_nits')}")
    if a.perturb == "none" and rows:
        gaps = np.array([r["rel_gap"] if r.get("feasible") else 0.0 for r in rows])
        print(f"RESULT cells={len(rows)} count")
        print(f"RESULT cells_gap_gt_1e-3={int(np.sum(gaps > 1e-3))} count")
        print(f"RESULT cells_gap_gt_1e-4={int(np.sum(gaps > 1e-4))} count")
        print(f"RESULT gap_mean={gaps.mean():.4e} ratio")
        print(f"RESULT gap_max={gaps.max():.4e} ratio")
        print(f"RESULT gap_min={gaps.min():.4e} ratio")
        if len(gaps) >= 5:
            print(f"RESULT gap_mean_drop_best={np.delete(gaps, int(np.argmax(gaps))).mean():.4e} ratio")
        for arm in ("seeds", "budget", "eps6", "eps3", "cd"):
            vals = [(r["records"][0]["prod"] - r["records"][0][arm]) / abs(r["records"][0]["prod"])
                    for r in rows if arm in r["records"][0]]
            if vals:
                print(f"RESULT arm_{arm}_cells_gt_1e-4={int(np.sum(np.array(vals) > 1e-4))} count")
                print(f"RESULT arm_{arm}_max={max(vals):.4e} ratio")
        allruns = [x for r in rows for rec in r["records"] for x in rec["lbfgsb_runs"]]
        print(f"RESULT lbfgsb_runs={len(allruns)} count")
        print(f"RESULT lbfgsb_runs_hit_maxiter={sum(1 for x in allruns if 'ITERATIONS' in x[2])} count")
        print(f"RESULT lbfgsb_runs_pgtol={sum(1 for x in allruns if 'PGTOL' in x[2])} count")
        print(f"RESULT lbfgsb_median_nit={int(np.median([x[0] for x in allruns]))} count")
        print(f"RESULT lbfgsb_max_nit={max(x[0] for x in allruns)} count")
    elif rows:
        rels = np.array([r["rel"] for r in rows])
        print(f"RESULT perturbed_cells_improved_gt_1e-4={int(np.sum(rels > 1e-4))} count")
        print(f"RESULT perturbed_rel_max={rels.max():.4e} ratio")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")
    if a.json:
        def clean(o):
            if isinstance(o, dict):
                return {k: clean(v) for k, v in o.items() if not k.startswith("_")}
            if isinstance(o, (list, tuple)):
                return [clean(v) for v in o]
            if isinstance(o, (np.floating, np.integer)):
                return o.item()
            return o
        with open(a.json, "w") as fh:
            json.dump(clean(rows), fh, indent=1)


if __name__ == "__main__":
    main()
