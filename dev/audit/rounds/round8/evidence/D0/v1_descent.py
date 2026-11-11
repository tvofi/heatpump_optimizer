"""D0 round 8, verifier v1: how much local descent is left at the point production ships?

Metric (one line): per cell, headroom = (J_prod - J_cont) / |J_prod|, J = the shipped
HeatPumpOptimizer.optimize(...).objective_value, where the "cont" arm lets every
production _multi_start_minimize call finish as shipped and then CONTINUES from its
returned x with an independent descent (L-BFGS-B, ftol 1e-15, gtol 1e-9, maxiter 3000,
my own CENTRAL-difference gradient h=1e-5 through production's batch_objective, clipped at
the bounds), keeping the continuation only if it is lower on the captured objective;
counted only where room/zone degree-steps below min_temp are no worse than production.

Arms (all end-to-end through optimize, same inputs):
  prod   : as shipped
  cont   : shipped result + local continuation (measures what the stop left on the table)
  ftol9  : ftol 1e-9 at optimizer:_scoped_minimize (a practical fix size) -- gap + nfev
  ftol12 : ftol 1e-12 at the same seam (the finder's arm, re-implemented here)
Perturbation: --prod-ftol 1e-12 edits the seam for prod itself (and for cont's base);
  expected: cont headroom -> ~0 IF the gap is a stop-rule gap; any residual is what a
  forward-difference eps=1e-4 gradient cannot see (not an ftol effect).
Null control: the flat price profile rows (RESULT *_flat_*).

Command (tree root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  python3 tools/audit/round8/D0/v1_descent.py --tz 1 --dhw 0 [--arms prod,cont,ftol9,ftol12]
Baseline cdf82daa; 4-vCPU cloud container, shared (timings not used; counts/ratios only).
Expected: see verify-v1.md; ratios +-1e-6 absolute (BLAS drift).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from datetime import datetime
from unittest import mock
from scipy.optimize import minimize
from profiles import prices, weather, house
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import optimizer as O

PRICES = ["winter_typical", "winter_extreme", "summer_typical", "summer_negative",
          "shoulder", "winter_narrow", "winter_moderate", "flat"]
WEATHER = ["winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder"]
START = datetime(2026, 1, 15)
MIN_T = 17.0
ORIG_MS = O._multi_start_minimize
ORIG_SCOPED = O._scoped_minimize


def build(pp, wp, dhw, tz):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    opt = O.HeatPumpOptimizer(ThermalModel(p), O.OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=21.0, min_temp=MIN_T, max_temp=23.0))
    pr = prices(pp, START)
    ot, wi, ra, so = weather(wp, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    return opt, (st, pr, ot, wi, ra, so, START)


def central_grad(batch, args, x, bounds, h=1e-5):
    n = x.size
    lb = np.array([b[0] for b in bounds], float)
    ub = np.array([b[1] for b in bounds], float)
    xp = np.minimum(x + h, ub)
    xm = np.maximum(x - h, lb)
    P = np.tile(x, (2 * n, 1))
    P[np.arange(n), np.arange(n)] = xp
    P[n + np.arange(n), np.arange(n)] = xm
    f = np.asarray(batch(P, *args), float)
    d = xp - xm
    g = np.zeros(n)
    np.divide(f[:n] - f[n:], d, out=g, where=d > 0)
    return g


class Stats:
    def __init__(self):
        self.nfev = 0
        self.calls = 0
        self.cont_calls_improved = 0


def run(opt, inp, arm, prod_ftol, stats):
    seam_ftol = {"ftol9": 1e-9, "ftol12": 1e-12}.get(arm, prod_ftol)

    def scoped(*a, **k):
        opts = dict(k.get("options", {}))
        if seam_ftol is not None:
            opts["ftol"] = seam_ftol
        k["options"] = opts
        r = ORIG_SCOPED(*a, **k)
        stats.nfev += int(r.nfev)
        return r

    def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
           fd_eps=1e-4):
        res = ORIG_MS(objective, candidates, bounds, args=args, maxiter=maxiter,
                      batch_objective=batch_objective, fd_eps=fd_eps)
        stats.calls += 1
        if arm != "cont" or batch_objective is None:
            return res
        x0 = np.asarray(res.x, float)
        f0 = float(objective(x0, *args))
        c = minimize(objective, x0, args=args, method="L-BFGS-B", bounds=bounds,
                     jac=lambda x, *a: central_grad(batch_objective, a, x, bounds),
                     options={"maxiter": 3000, "ftol": 1e-15, "gtol": 1e-9, "maxfun": 100000})
        f1 = float(objective(c.x, *args))
        if np.isfinite(f1) and f1 < f0:
            stats.cont_calls_improved += 1
            res.x = np.asarray(c.x, float)
            res.fun = f1
        return res

    with mock.patch.object(O, "_scoped_minimize", scoped), \
            mock.patch.object(O, "_multi_start_minimize", ms):
        r = opt.optimize(*inp)
    short = 0.0
    for tr in (r.room_temp_trajectory, r.upper_temp_trajectory, r.lower_temp_trajectory):
        if tr:
            short += float(np.maximum(0.0, MIN_T - np.asarray(tr[1:], float)).sum())
    return r, short


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tz", default="1")
    ap.add_argument("--dhw", default="0")
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default=",".join(WEATHER))
    ap.add_argument("--arms", default="prod,cont,ftol9,ftol12")
    ap.add_argument("--prod-ftol", type=float, default=None,
                    help="perturbation: production's own ftol at the seam")
    a = ap.parse_args()
    tz, dhw = a.tz == "1", a.dhw == "1"
    arms = a.arms.split(",")
    cpu0, th0 = time.process_time(), time.thread_time()
    rows = []
    for pp in a.prices.split(","):
        for wp in a.weather.split(","):
            row = {"pp": pp, "cell": f"{pp}|{wp}"}
            for arm in arms:
                opt, inp = build(pp, wp, dhw, tz)
                s = Stats()
                r, short = run(opt, inp, arm, a.prod_ftol, s)
                row[arm] = dict(J=float(r.objective_value), cost=float(r.predicted_cost),
                                short=short, nfev=s.nfev, imp=s.cont_calls_improved,
                                step0=float(r.power_schedule[0]))
            jp = row["prod"]["J"]
            out = [f"CELL {row['cell']} J={jp:.6f} cost={row['prod']['cost']:.3f} nfev={row['prod']['nfev']} short={row['prod']['short']:.4f}"]
            for arm in arms[1:]:
                g = (jp - row[arm]["J"]) / abs(jp)
                ok = row[arm]["short"] <= row["prod"]["short"] + 1e-9
                row[arm]["gap"] = g if ok else 0.0
                out.append(f"{arm}={g:+.3e}{'' if ok else '(COMFORT-WORSE)'} dcost="
                           f"{row['prod']['cost'] - row[arm]['cost']:+.3f} nfev={row[arm]['nfev']} "
                           f"ds0={row[arm]['step0'] - row['prod']['step0']:+.3f} short={row[arm]['short']:.4f}")
            print(" | ".join(out), flush=True)
            rows.append(row)
    print(f"RESULT cells={len(rows)} count")
    for arm in arms[1:]:
        g = np.array([r[arm]["gap"] for r in rows])
        dc = np.array([r["prod"]["cost"] - r[arm]["cost"] for r in rows])
        s0 = sum(1 for r in rows if abs(r[arm]["step0"] - r["prod"]["step0"]) > 1e-3)
        print(f"RESULT {arm}_cells_gap_gt_1e-3={int((g > 1e-3).sum())} count")
        print(f"RESULT {arm}_cells_gap_lt_-1e-4={int((g < -1e-4).sum())} count")
        print(f"RESULT {arm}_gap_mean={g.mean():.4e} ratio")
        print(f"RESULT {arm}_gap_max={g.max():.4e} ratio")
        print(f"RESULT {arm}_gap_min={g.min():.4e} ratio")
        print(f"RESULT {arm}_gap_mean_drop_best={np.delete(g, int(np.argmax(g))).mean():.4e} ratio")
        loo = [np.delete(g, i).mean() for i in range(len(g))]
        print(f"RESULT {arm}_loo_mean_min={min(loo):.4e} ratio")
        print(f"RESULT {arm}_loo_mean_max={max(loo):.4e} ratio")
        fl = [r[arm]["gap"] for r in rows if r["pp"] == "flat"]
        nf = [r[arm]["gap"] for r in rows if r["pp"] != "flat"]
        if fl:
            print(f"RESULT {arm}_flat_gap_mean={np.mean(fl):.4e} ratio")
            print(f"RESULT {arm}_flat_gap_max={max(fl):.4e} ratio")
        if nf:
            print(f"RESULT {arm}_nonflat_gap_mean={np.mean(nf):.4e} ratio")
        print(f"RESULT {arm}_cost_delta_mean={dc.mean():.4f} SEK/day")
        print(f"RESULT {arm}_cost_delta_min={dc.min():.4f} SEK/day")
        print(f"RESULT {arm}_cost_delta_max={dc.max():.4f} SEK/day")
        print(f"RESULT {arm}_step0_changed={s0} count")
        print(f"RESULT {arm}_cells_comfort_worse={sum(1 for r in rows if r[arm]['short'] > r['prod']['short'] + 1e-9)} count")
        graw = np.array([(r['prod']['J'] - r[arm]['J']) / abs(r['prod']['J']) for r in rows])
        print(f"RESULT {arm}_rawgap_mean={graw.mean():.4e} ratio")
        print(f"RESULT {arm}_rawgap_cells_gt_1e-3={int((graw > 1e-3).sum())} count")
        if arm != "cont":
            ratios = [r[arm]["nfev"] / max(r["prod"]["nfev"], 1) for r in rows]
            print(f"RESULT {arm}_nfev_ratio_median={float(np.median(ratios)):.3f} ratio")
            print(f"RESULT {arm}_nfev_total_ratio={sum(r[arm]['nfev'] for r in rows) / max(1, sum(r['prod']['nfev'] for r in rows)):.3f} ratio")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
