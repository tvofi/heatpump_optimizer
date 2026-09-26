"""V2 (independent) harness for D0-s2-01: stop-rule residue at the shipped first-stage
plan, measured with a jac production does not use, at the horizon production ships.

Metric (one line): per cell, resid = (f_prod - f_scipy)/|f_prod| where f_prod is the
captured objective at the x the FIRST optimizer:_multi_start_minimize call returned and
f_scipy is scipy L-BFGS-B from that x with scipy's OWN 2-point FD gradient (jac=None,
not production's _batch_fd_gradient), ftol=1e-10, gtol=1e-8, maxiter 3000, on the same
captured objective/bounds/args. Second number per cell: iter = the same drop reached by
iterating production's own optimizer:_lbfgsb_restart up to 30 times (stops when it
returns its input). Also prints the main-run stop messages hooked at _scoped_minimize.
Count key: the production objective closure's value. Reachability: RESULT
shipped_n_steps = OptimizationConfig.from_mapping({}).n_steps (what a real install gets).

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/verify-v2/v2_stoprule.py --horizon 24|48 \
    [--prices shoulder,summer_typical,flat] [--weather winter_cold,summer_cool] [--tz 0,1] [--dhw 0,1] [--jobs 2]
Expected: finder's cell (48 h, two|dhw|summer_typical|winter_cold) resid ~0.65 % +- 0.05 pp
if the residue is jac-independent; 24 h values: measured, see verify-v2.md.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2,
4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from collections import Counter
from datetime import datetime
from unittest import mock
from scipy.optimize import minimize
from profiles import prices as P_prices, weather as P_weather, house
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig

START = datetime(2026, 1, 15)
REAL_MS, REAL_SC = om._multi_start_minimize, om._scoped_minimize


def cell(a):
    tz, dhw, pp, wp, horizon = a
    p = ThermalParameters.from_config(house(two_zone=tz))
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=horizon, time_step_minutes=15,
                                                target_temp=21.0, min_temp=17.0, max_temp=23.0))
    n = horizon * 4
    pr = P_prices(pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    k = int(np.ceil(horizon / 24))
    pr, ot, wi, ra, so = (np.tile(v, k)[:n] for v in (pr, ot, wi, ra, so))
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    caps, msgs = [], Counter()

    def ms_w(objective, candidates, bounds, *aa, **kw):
        res = REAL_MS(objective, candidates, bounds, *aa, **kw)
        if not caps:
            caps.append(dict(objective=objective, bounds=list(bounds), kw=dict(kw),
                             x=np.asarray(res.x, float).copy()))
        return res

    def sc_w(*aa, **kw):
        r = REAL_SC(*aa, **kw)
        if len(caps) == 0:
            msgs[str(r.message)[:40]] += 1
        return r

    with mock.patch.object(om, "_multi_start_minimize", ms_w), \
            mock.patch.object(om, "_scoped_minimize", sc_w):
        res = o.optimize(st, pr, ot, wi, ra, so, START)
    c = caps[0]
    args = tuple(c["kw"].get("args", ()))
    f = lambda x: float(c["objective"](np.asarray(x, float), *args))
    f0 = f(c["x"])
    r = minimize(c["objective"], c["x"], args=args, jac=None, method="L-BFGS-B",
                 bounds=c["bounds"], options={"maxiter": 3000, "maxfun": 10**6,
                                               "ftol": 1e-10, "gtol": 1e-8, "eps": 1e-4})
    f1 = f(r.x)
    # production's own restart, iterated
    best = type("R", (), {})()
    best.x = c["x"].copy()
    it = 0
    for it in range(1, 31):
        nb = om._lbfgsb_restart(best, c["objective"], c["bounds"], args,
                                c["kw"].get("maxiter", 300), c["kw"].get("batch_objective"),
                                c["kw"].get("fd_eps", 1e-4))
        if nb is best:
            break
        best = nb
    f2 = f(best.x)
    return dict(cell=f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|h{horizon}",
                f0=f0, f1=f1, f2=f2, shipped=float(res.objective_value),
                resid=(f0 - f1) / abs(f0), iter=(f0 - f2) / abs(f0), n_restart=it,
                msgs=dict(msgs), kwh0=float(np.sum(c["x"]) * .25), kwh1=float(np.sum(r.x) * .25))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--prices", default="shoulder,summer_typical,flat")
    ap.add_argument("--weather", default="winter_cold,summer_cool")
    ap.add_argument("--tz", default="0,1")
    ap.add_argument("--dhw", default="0,1")
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()
    print(f"RESULT shipped_n_steps={OptimizationConfig.from_mapping({}).n_steps} count "
          f"(horizon_hours={OptimizationConfig.from_mapping({}).horizon_hours})")
    cells = [(bool(int(t)), bool(int(d)), pp, wp, a.horizon) for pp in a.prices.split(",")
             for wp in a.weather.split(",") for t in a.tz.split(",") for d in a.dhw.split(",")]
    t0p, t0t = time.process_time(), time.thread_time()
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool:
            rows = pool.map(cell, cells)
    else:
        rows = [cell(c) for c in cells]
    for r in rows:
        print(f"CELL {r['cell']:44s} f {r['f0']:.5f} -> scipyFD {r['f1']:.5f} ({100*r['resid']:+.4f}%) "
              f"prod-restart x{r['n_restart']} {r['f2']:.5f} ({100*r['iter']:+.4f}%) shipped={r['shipped']:.5f} "
              f"kWh {r['kwh0']:.2f}->{r['kwh1']:.2f} stops={r['msgs']}")
    by = {}
    for r in rows:
        by.setdefault(r["cell"].split("|")[2], []).append(r)
    for pp, rs in by.items():
        v = np.array([r["resid"] for r in rs]); w = np.array([r["iter"] for r in rs])
        print(f"RESULT {pp}_resid_max={100*v.max():.4f} %")
        print(f"RESULT {pp}_resid_mean={100*v.mean():.4f} %")
        if len(v) >= 5:
            print(f"RESULT {pp}_resid_mean_drop_best={100*np.delete(v, v.argmax()).mean():.4f} %")
        print(f"RESULT {pp}_iterrestart_max={100*w.max():.4f} %")
        print(f"RESULT {pp}_cells_over_0.1pct={int((v > 1e-3).sum())} of {len(v)} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
