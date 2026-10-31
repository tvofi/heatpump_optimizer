"""D0 round 8, seat s1: does L-BFGS-B's stopping rule stop the shipped solve short?

Metric (one line): per cell, rel_gap = (J_prod - J_arm) / |J_prod|, J = the shipped
OptimizationResult.objective_value of HeatPumpOptimizer.optimize, where arm re-runs the
SAME optimize with only the L-BFGS-B stopping options changed at the production seam
optimizer:_scoped_minimize (every L-BFGS-B run: each multi-start refinement and each
_lbfgsb_restart polish); comfort parity = room degree-steps below min_temp no worse.

Count key: the shipped objective_value and the scipy result's own ``message`` for every
L-BFGS-B run production makes (RELATIVE REDUCTION OF F = ftol stop, PGTOL = gtol stop,
ITERATIONS = maxiter).

Command (from the tree root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python3 tools/audit/round8/D0/s1_budget.py --tz 1 --dhw 0 [--prices ..] [--weather ..]

Arms: prod (options as shipped: maxiter 200/300, ftol 1e-6, gtol default 1e-5,
maxfun default 15000); ftol (ftol 1e-12 only); gtol (gtol 1e-10 only); maxiter (x10
only); tight (ftol 1e-12 and gtol 1e-10).
Perturbation = the 'ftol' arm itself: a one-line production edit of the two
``"ftol": 1e-6`` literals in optimizer.py to 1e-12 moves rel_gap(ftol) of production to 0
(production becomes the arm), and --perturb-prod ftol runs that edit via the seam so the
judge can check the prod count 'runs_stopped_by_ftol' goes to zero.

Expected (baseline cdf82daa, 4-vCPU cloud container): see REPORT-s1.md; objective
ratios exact to ~1e-6 (BLAS drift), nfev/nit counts exact on this box.
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
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_race import setup, START, PRICES, WEATHER  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

ORIG_SCOPED = O._scoped_minimize
ARMS = {
    "prod": {},
    "ftol": {"ftol": 1e-12},
    "gtol": {"gtol": 1e-10},
    "maxiter": {"maxiter_x": 10},
    "tight": {"ftol": 1e-12, "gtol": 1e-10},
}


def run(pp, wp, dhw, tz, over):
    opt, m, pr, ot, wi, ra, so, st = setup(pp, wp, dhw, tz)
    runs = []

    def scoped(*a, **k):
        opts = dict(k.get("options", {}))
        for key, v in over.items():
            if key == "maxiter_x":
                opts["maxiter"] = int(opts.get("maxiter", 15000) * v)
            else:
                opts[key] = v
        k["options"] = opts
        r = ORIG_SCOPED(*a, **k)
        runs.append((int(r.nit), int(r.nfev), str(r.message)))
        return r

    with mock.patch.object(O, "_scoped_minimize", scoped):
        res = opt.optimize(st, pr, ot, wi, ra, so, START)
    room = np.asarray(res.room_temp_trajectory[1:], float)
    short = float(np.maximum(0.0, 17.0 - room).sum())
    return res, runs, short


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dhw", default="0")
    ap.add_argument("--tz", default="1")
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default=",".join(WEATHER))
    ap.add_argument("--arms", default="prod,ftol,gtol,maxiter,tight")
    ap.add_argument("--perturb-prod", default="none", help="'ftol': prod runs with ftol 1e-12")
    a = ap.parse_args()
    arms = a.arms.split(",")
    dhw, tz = a.dhw == "1", a.tz == "1"
    cpu0, th0 = time.process_time(), time.thread_time()
    rows = []
    for pp in a.prices.split(","):
        for wp in a.weather.split(","):
            row = {"cell": f"{pp}|{wp}|dhw={int(dhw)}|tz={int(tz)}", "pp": pp}
            for arm in arms:
                over = dict(ARMS[arm])
                if arm == "prod" and a.perturb_prod == "ftol":
                    over = {"ftol": 1e-12}
                res, runs, short = run(pp, wp, dhw, tz, over)
                row[arm] = dict(J=float(res.objective_value), cost=float(res.predicted_cost),
                                short=short, runs=runs, step0=float(res.power_schedule[0]),
                                nfev=sum(r[1] for r in runs), nit=sum(r[0] for r in runs))
            jp = row["prod"]["J"]
            parts = []
            for arm in arms[1:]:
                g = (jp - row[arm]["J"]) / abs(jp)
                feas = row[arm]["short"] <= row["prod"]["short"] + 1e-9
                row[arm]["gap"] = g if feas else 0.0
                parts.append(f"{arm}={g:+.3e}{'' if feas else '(INFEAS)'} "
                             f"cost={row[arm]['cost']:.3f} nfev={row[arm]['nfev']}")
            pr_runs = row["prod"]["runs"]
            nft = sum(1 for r in pr_runs if "REDUCTION OF F" in r[2])
            print(f"CELL {row['cell']} J={jp:.6f} cost={row['prod']['cost']:.3f} "
                  f"nfev={row['prod']['nfev']} ftol_stops={nft}/{len(pr_runs)} step0={row['prod']['step0']:.3f} | "
                  + " | ".join(parts), flush=True)
            rows.append(row)
    all_runs = [r for row in rows for r in row["prod"]["runs"]]
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT prod_lbfgsb_runs={len(all_runs)} count")
    print(f"RESULT runs_stopped_by_ftol={sum(1 for r in all_runs if 'REDUCTION OF F' in r[2])} count")
    print(f"RESULT runs_stopped_by_pgtol={sum(1 for r in all_runs if 'PGTOL' in r[2])} count")
    print(f"RESULT runs_stopped_by_maxiter={sum(1 for r in all_runs if 'ITERATIONS' in r[2])} count")
    print(f"RESULT runs_stopped_other={sum(1 for r in all_runs if not any(s in r[2] for s in ('REDUCTION OF F', 'PGTOL', 'ITERATIONS')))} count")
    for arm in arms[1:]:
        g = np.array([row[arm]["gap"] for row in rows])
        dc = np.array([row["prod"]["cost"] - row[arm]["cost"] for row in rows])
        nf = np.array([row[arm]["nfev"] / max(row["prod"]["nfev"], 1) for row in rows])
        print(f"RESULT {arm}_cells_gap_gt_1e-3={int(np.sum(g > 1e-3))} count")
        print(f"RESULT {arm}_cells_gap_lt_-1e-4={int(np.sum(g < -1e-4))} count")
        print(f"RESULT {arm}_gap_max={g.max():.4e} ratio")
        print(f"RESULT {arm}_gap_min={g.min():.4e} ratio")
        print(f"RESULT {arm}_gap_mean={g.mean():.4e} ratio")
        if len(g) >= 5:
            print(f"RESULT {arm}_gap_mean_drop_best={np.delete(g, int(np.argmax(g))).mean():.4e} ratio")
        flat = [row[arm]["gap"] for row in rows if row["pp"] == "flat"]
        if flat:
            print(f"RESULT {arm}_flat_gap_max={max(flat):.4e} ratio")
            print(f"RESULT {arm}_flat_gap_mean={np.mean(flat):.4e} ratio")
            nonflat = [row[arm]["gap"] for row in rows if row["pp"] != "flat"]
            if nonflat:
                print(f"RESULT {arm}_nonflat_gap_mean={np.mean(nonflat):.4e} ratio")
        print(f"RESULT {arm}_cost_delta_max={dc.max():.4f} SEK/day")
        print(f"RESULT {arm}_cost_delta_mean={dc.mean():.4f} SEK/day")
        print(f"RESULT {arm}_nfev_ratio_median={float(np.median(nf)):.3f} ratio")
        print(f"RESULT {arm}_nfev_ratio_max={float(np.max(nf)):.3f} ratio")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
