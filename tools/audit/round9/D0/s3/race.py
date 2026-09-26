"""D0 round 9, seat D0-s3, step D0.M5 (null control) and the cell data D0.M6 reads.

Metric: per cell, gap = (J_prod - J_chal) / |J_prod| in %, where J is the
production objective value (OptimizationResult.objective_value) of the plan
HeatPumpOptimizer.optimize ships, and J_chal is the same field when every
optimizer._multi_start_minimize call inside the same optimize() is replaced by
production's own call PLUS a stronger search on the exact captured objective,
bounds, args and batched-jac path (structured bang-bang seeds at 0.1..1.5x the
production plan's energy, a warm restart from production's answer, L-BFGS-B at
ftol 1e-12 / maxiter 3000 / maxfun 60000), keeping whichever scores lower.
The challenger never ships a plan worse than production's on the captured
objective, so gap >= 0 per call; a cell's gap can still differ in sign from
that because downstream stages (_co_optimize, valve hold) re-decide on it.
Count key: the value J the production objective returns for the delivered
schedule (never an input attribute).

Feasibility parity is reported per cell: degree-steps below the per-step
comfort floor (OptimizationConfig.get_temp_bounds) on the shipped trajectory,
both arms; a cell whose challenger is colder than production is flagged
infeasible and excluded from the "cheaper" verdict.

Null control (D0.M5): the price profile "flat" is one axis value of the grid;
the harness prints the gap at flat beside the gap at the priced profiles.

Command (from the export root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D0/s3/race.py \
    [--shard i/n] [--out DIR] [--topo one,two] [--dhw 0,1] \
    [--prices p1,p2] [--weather w1,w2] [--perturb nochal]
  Then: race.py --summarise DIR   (prints the RESULT lines over all shards)
Perturbation: --perturb nochal makes the challenger return production's own
result, so every gap must go to_zero.
Expected values (baseline 1936d5ca, B3 container, 4-CPU Linux): see REPORT.md;
counts and ratios exact up to BLAS noise (tolerance +-0.05 percentage points).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, json, time, argparse, tempfile, glob
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from scipy.optimize import minimize
from profiles import prices as P_prices, weather as P_weather, house, DT
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer import optimizer as om

PRICES = ["winter_typical", "winter_extreme", "winter_narrow", "winter_moderate",
          "summer_typical", "summer_negative", "shoulder", "flat"]
WEATHER = ["winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder"]
START = datetime(2026, 1, 15)
FRACTIONS = (0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.25, 1.5)
ORIG_MSM = om._multi_start_minimize


def build(two_zone, dhw, price_p, weather_p, horizon_h=24, start=START, extra=None):
    cfg = house(two_zone=two_zone)
    cfg.update(extra or {})
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = bool(dhw)
    m = ThermalModel(p)
    oc = OptimizationConfig(horizon_hours=horizon_h, time_step_minutes=15,
                            target_temp=21.0, min_temp=17.0, max_temp=23.0)
    o = HeatPumpOptimizer(m, oc)
    n = int(horizon_h / DT)
    pr = P_prices(price_p, start)
    ot, wi, ra, so = P_weather(weather_p, start)
    reps = int(np.ceil(n / len(pr)))
    pr, ot, wi, ra, so = (np.tile(a, reps)[:n] for a in (pr, ot, wi, ra, so))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    return o, m, oc, st, pr, ot, wi, ra, so


class Challenger:
    """Replaces optimizer._multi_start_minimize; records every call."""

    def __init__(self, prices, dt, disabled=False):
        self.prices = np.asarray(prices, float)
        self.dt = dt
        self.disabled = disabled
        self.calls = []

    def _jac(self, objective, batch_objective, bounds, fd_eps):
        if batch_objective is None or not om._bounds_supported_by_batch(bounds):
            return None
        def jac(x, *a):
            return om._batch_fd_gradient(batch_objective, a, x,
                                         float(objective(x, *a)), fd_eps, bounds)
        return jac

    def __call__(self, objective, candidates, bounds, args=(), maxiter=300,
                 batch_objective=None, fd_eps=1e-4):
        prod = ORIG_MSM(objective, candidates, bounds, args=args, maxiter=maxiter,
                        batch_objective=batch_objective, fd_eps=fd_eps)
        f = lambda x: float(objective(np.asarray(x, float), *args))
        ps = f(prod.x)
        rec = {"n_cand": len(candidates), "prod": ps, "best": ps, "winner": "prod"}
        if self.disabled:
            self.calls.append(rec)
            return prod
        lb = np.array([b[0] for b in bounds], float)
        ub = np.array([b[1] for b in bounds], float)
        n = len(bounds)
        pr = self.prices[:n]
        e_prod = float(np.sum(prod.x) * self.dt)
        pmax = float(np.max(ub)) if n else 0.0
        seeds = [("warm", np.asarray(prod.x, float))]
        for fr in FRACTIONS:
            s = om._price_ranked_start(pr, e_prod * fr, pmax, self.dt)
            seeds.append((f"bb{fr}", np.clip(s, lb, ub)))
        jac = self._jac(objective, batch_objective, bounds, fd_eps)
        best_x, best_s, win = np.asarray(prod.x, float), ps, "prod"
        for name, x0 in seeds:
            try:
                r = minimize(objective, x0, args=args, jac=jac, method="L-BFGS-B",
                             bounds=bounds, options={"maxiter": 3000, "maxfun": 60000,
                                                     "ftol": 1e-12, "gtol": 1e-9,
                                                     "eps": fd_eps})
                r2 = minimize(objective, r.x, args=args, jac=jac, method="L-BFGS-B",
                              bounds=bounds, options={"maxiter": 3000, "maxfun": 60000,
                                                      "ftol": 1e-12, "gtol": 1e-9,
                                                      "eps": fd_eps})
                x = np.clip(r2.x, lb, ub)
                s = f(x)
            except Exception:
                continue
            if np.isfinite(s) and s < best_s - 1e-12:
                best_x, best_s, win = x, s, name
        rec.update(best=best_s, winner=win,
                   gap_pct=100.0 * (ps - best_s) / max(abs(ps), 1e-12))
        self.calls.append(rec)
        if win == "prod":
            return prod
        prod.x = best_x
        prod.fun = best_s
        return prod


def floor_violation(res, oc):
    hrs = [(t.hour + t.minute / 60.0) for t in res.timestamps]
    floor = np.array([oc.get_temp_bounds(h)[0] for h in hrs])
    if res.upper_temp_trajectory:
        room = np.minimum(np.asarray(res.upper_temp_trajectory, float),
                          np.asarray(res.lower_temp_trajectory, float))
    else:
        room = np.asarray(res.room_temp_trajectory, float)
    room = room[-len(floor):]
    return float(np.maximum(0.0, floor - room).sum())


def energy_cost(res):
    sp = np.asarray(res.power_schedule, float)
    dh = np.asarray(res.dhw_power_schedule, float) if res.dhw_power_schedule else 0 * sp
    return float(np.sum(np.asarray(res.prices, float) * (sp + dh) * DT))


def run_arm(two_zone, dhw, price_p, weather_p, chal, horizon_h=24, extra=None):
    o, m, oc, st, pr, ot, wi, ra, so = build(two_zone, dhw, price_p, weather_p,
                                             horizon_h, extra=extra)
    ch = Challenger(pr, DT, disabled=(chal == "off"))
    saved = om._multi_start_minimize
    om._multi_start_minimize = ch
    try:
        t0 = time.process_time()
        res = o.optimize(st, pr, ot, wi, ra, so, START)
        cpu = time.process_time() - t0
    finally:
        om._multi_start_minimize = saved
    return res, oc, ch.calls, cpu


def cell(two_zone, dhw, price_p, weather_p, perturb):
    rp, oc, calls_p, cpu_p = run_arm(two_zone, dhw, price_p, weather_p, "off")
    rc, _, calls_c, cpu_c = run_arm(two_zone, dhw, price_p, weather_p,
                                    "off" if perturb == "nochal" else "on")
    jp, jc = float(rp.objective_value), float(rc.objective_value)
    vp, vc = floor_violation(rp, oc), floor_violation(rc, oc)
    ep, ec = energy_cost(rp), energy_cost(rc)
    sp0 = float(rp.power_schedule[0]); sc0 = float(rc.power_schedule[0])
    dp0 = float(rp.dhw_power_schedule[0]) if rp.dhw_power_schedule else 0.0
    dc0 = float(rc.dhw_power_schedule[0]) if rc.dhw_power_schedule else 0.0
    return {
        "cell": f"{'two' if two_zone else 'one'}|{int(dhw)}|{price_p}|{weather_p}",
        "J_prod": jp, "J_chal": jc,
        "gap_pct": 100.0 * (jp - jc) / max(abs(jp), 1e-12),
        "viol_prod": vp, "viol_chal": vc,
        "feasible": vc <= vp + 1e-6,
        "energy_sek_prod": ep, "energy_sek_chal": ec,
        "step0_space_prod": sp0, "step0_space_chal": sc0,
        "step0_dhw_prod": dp0, "step0_dhw_chal": dc0,
        "step0_diff_kw": abs(sp0 - sc0) + abs(dp0 - dc0),
        "calls": calls_c, "n_calls": len(calls_c),
        "call_gaps_pct": [c.get("gap_pct", 0.0) for c in calls_c],
        "winners": [c["winner"] for c in calls_c],
        "cpu_prod_s": cpu_p, "cpu_chal_s": cpu_c,
    }


def summarise(d):
    rows = []
    for fn in sorted(glob.glob(os.path.join(d, "cell_*.json"))):
        with open(fn) as fh:
            rows.append(json.load(fh))
    print(f"cells={len(rows)}")
    by = {}
    for r in rows:
        topo, dhw, pp, wp = r["cell"].split("|")
        by.setdefault(pp, []).append(r)
        flag = "" if r["feasible"] else "  INFEASIBLE(colder)"
        print(f"{r['cell']:<45} gap {r['gap_pct']:8.4f}%  dE {r['energy_sek_prod']-r['energy_sek_chal']:7.3f} SEK"
              f"  bill {r['energy_sek_prod']:7.2f}  step0 {r['step0_diff_kw']:.3f} kW  win {','.join(r['winners'])}{flag}")
    for pp in PRICES:
        g = [r["gap_pct"] for r in by.get(pp, []) if r["feasible"]]
        if not g:
            continue
        g = np.array(g)
        print(f"RESULT gap_mean_{pp}={g.mean():.4f} %   (max {g.max():.4f}, cells {len(g)}, >0.1%: {int((g>0.1).sum())})")
    pos = [r for r in rows if r["feasible"]]
    priced = np.array([r["gap_pct"] for r in pos if r["cell"].split("|")[2] != "flat"])
    flat = np.array([r["gap_pct"] for r in pos if r["cell"].split("|")[2] == "flat"])
    if len(priced):
        print(f"RESULT gap_mean_priced={priced.mean():.4f} %")
        print(f"RESULT gap_max_priced={priced.max():.4f} %")
        s = np.sort(priced)
        print(f"RESULT gap_mean_priced_drop_best={s[:-1].mean():.4f} %")
    if len(flat):
        print(f"RESULT gap_mean_flat={flat.mean():.4f} %")
        print(f"RESULT gap_max_flat={flat.max():.4f} %")
    # D0.M5 null-control reading: match every priced cell to the flat cell of
    # the same topology / DHW / weather, and split the challenger's gain into
    # money (energy SEK) and the rest of the objective.
    flat_of = {tuple(r["cell"].split("|")[i] for i in (0, 1, 3)): r
               for r in pos if r["cell"].split("|")[2] == "flat"}
    gapped = [r for r in pos if r["gap_pct"] > 0.1 and r["cell"].split("|")[2] != "flat"]
    above_flat = 0
    money_up = 0
    abs_j = []
    for r in gapped:
        key = tuple(r["cell"].split("|")[i] for i in (0, 1, 3))
        f = flat_of.get(key)
        if f is not None and r["gap_pct"] > f["gap_pct"] + 0.1:
            above_flat += 1
        if r["energy_sek_chal"] > r["energy_sek_prod"] + 1e-6:
            money_up += 1
        abs_j.append(r["J_prod"] - r["J_chal"])
    print(f"RESULT priced_cells_gap_gt_0p1={len(gapped)}")
    print(f"RESULT priced_gapped_cells_above_matched_flat_by_0p1pt={above_flat}")
    print(f"RESULT priced_gapped_cells_where_challenger_spends_more_money={money_up}")
    if abs_j:
        print(f"RESULT priced_gapped_abs_J_gap_mean={np.mean(abs_j):.4f} objective units (max {np.max(abs_j):.4f})")
    fg = [r for r in pos if r["cell"].split("|")[2] == "flat" and r["gap_pct"] > 0.1]
    print(f"RESULT flat_cells_gap_gt_0p1={len(fg)} of {len(flat_of)}")
    print(f"RESULT cells_infeasible={sum(1 for r in rows if not r['feasible'])}")
    print(f"RESULT cells_gap_gt_0p1={sum(1 for r in pos if r['gap_pct'] > 0.1)}")
    print(f"RESULT cells_gap_gt_0p1_step0_differs={sum(1 for r in pos if r['gap_pct'] > 0.1 and r['step0_diff_kw'] > 0.05)}")
    tf = time.process_time() / max(time.thread_time(), 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--topo", default="one,two")
    ap.add_argument("--dhw", default="0,1")
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default=",".join(WEATHER))
    ap.add_argument("--perturb", default="")
    ap.add_argument("--summarise", default=None)
    a = ap.parse_args()
    if a.summarise:
        summarise(a.summarise)
        return
    out = a.out or tempfile.mkdtemp(prefix="d0s3race_")
    os.makedirs(out, exist_ok=True)
    i, k = (int(x) for x in a.shard.split("/"))
    grid = [(t == "two", int(d), pp, wp)
            for t in a.topo.split(",") for d in a.dhw.split(",")
            for pp in a.prices.split(",") for wp in a.weather.split(",")]
    for j, (tz, dhw, pp, wp) in enumerate(grid):
        if j % k != i:
            continue
        fn = os.path.join(out, f"cell_{'two' if tz else 'one'}_{dhw}_{pp}_{wp}.json")
        if os.path.exists(fn):
            continue
        r = cell(tz, dhw, pp, wp, a.perturb)
        with open(fn, "w") as fh:
            json.dump(r, fh)
        print(f"{r['cell']:<45} gap {r['gap_pct']:8.4f}%  viol {r['viol_prod']:.3f}/{r['viol_chal']:.3f}"
              f"  step0 {r['step0_diff_kw']:.3f}  cpu {r['cpu_prod_s']:.1f}/{r['cpu_chal_s']:.1f}", flush=True)
    print(f"OUT {out}")
    summarise(out)


if __name__ == "__main__":
    main()
