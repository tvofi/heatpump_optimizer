"""V2 (independent) harness for D0-s1-01: does the two-zone 0.20x anchor, missing
from HeatPumpOptimizer._solve_space's cold-start seed set, lower the seam objective
MORE than a placebo extra seed does?

Metric (one line): per two-zone DHW-on cell, drop_arm = (f_prod - f_arm)/|f_prod| where
f_prod is the captured objective at the x the DHW path's cold-start
optimizer:_multi_start_minimize call returned, and f_arm is the REAL
_multi_start_minimize re-run on the same captured objective/bounds/args/jac with
production's candidates plus ONE extra seed: 'b020' = 0.20x baseline-thermostat energy
(the finding's missing anchor, baseline power recorded from the same optimize() call's
own _compute_baseline_power), placebos 'i020' = 0.20x of init_base energy (the DHW
path's own key), 'b015' = 0.15x and 'b025' = 0.25x baseline energy.
Count key: the value the captured production objective closure returns.
Seam-level (first-stage) metric; the finder's is the shipped objective_value after
_co_optimize. Both are recorded (shipped_obj printed per cell).

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/verify-v2/v2_dhw_anchor.py [--flat] [--jobs 2]
Expected: b020 max drop ~0.25 % +- 0.05 pp on two|dhw|winter_narrow|winter_cold
(the finder's shipped-level cell); placebos: measured, see verify-v2.md.
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
from datetime import datetime
from unittest import mock
from profiles import prices as P_prices, weather as P_weather, house
from heatpump_optimizer import optimizer as om
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig

START = datetime(2026, 1, 15)
PRICES = ("winter_typical", "winter_extreme", "winter_narrow", "winter_moderate")
WEATHERS = ("winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder")
REAL_MS = om._multi_start_minimize
DT = 0.25


def cell(args):
    pp, wp, flat = args
    p = ThermalParameters.from_config(house(two_zone=True))
    p.dhw_enabled = True
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                                                target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = P_prices("flat" if flat else pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    rec = {"cold": None, "in_cold": False, "base": None, "init_base": None, "prices": None}
    real_solve = HeatPumpOptimizer._solve_space
    real_base = HeatPumpOptimizer._compute_baseline_power

    def solve_w(self, dhw_plan, warm_start, h, p_max, n, dt, prs, init_base, *rest):
        cold = warm_start is None and rec["cold"] is None
        if cold:
            rec["in_cold"] = True
            rec["init_base"] = np.asarray(init_base, float).copy()
            rec["prices"] = np.asarray(prs, float).copy()
            rec["pmax"] = float(p_max)
        try:
            return real_solve(self, dhw_plan, warm_start, h, p_max, n, dt, prs, init_base, *rest)
        finally:
            rec["in_cold"] = False

    def ms_w(objective, candidates, bounds, *a, **kw):
        res = REAL_MS(objective, candidates, bounds, *a, **kw)
        if rec["in_cold"] and rec["cold"] is None:
            rec["cold"] = dict(objective=objective,
                               cands=[np.asarray(c, float).copy() for c in candidates],
                               bounds=list(bounds), kw=dict(kw), x=np.asarray(res.x, float).copy())
        return res

    def base_w(self, *a, **kw):
        out = real_base(self, *a, **kw)
        if rec["base"] is None:
            rec["base"] = np.asarray(out[0], float).copy()
        return out

    with mock.patch.object(om, "_multi_start_minimize", ms_w), \
            mock.patch.object(HeatPumpOptimizer, "_solve_space", solve_w), \
            mock.patch.object(HeatPumpOptimizer, "_compute_baseline_power", base_w):
        res = o.optimize(st, pr, ot, wi, ra, so, START)
    c = rec["cold"]
    args = c["kw"].get("args", ())
    f = lambda x: float(c["objective"](np.asarray(x, float), *args))
    f0 = f(c["x"])
    ub = np.array([b[1] for b in c["bounds"]], float)
    prs, pm = rec["prices"], rec["pmax"]
    eb = float(np.sum(rec["base"]) * DT)
    ei = float(np.sum(np.minimum(rec["init_base"], ub)) * DT)
    seeds = {"b020": eb * 0.20, "i020": ei * 0.20, "b015": eb * 0.15, "b025": eb * 0.25}
    out = {"cell": f"two|dhw|{pp}|{wp}" + ("|FLAT" if flat else ""), "f0": f0,
           "shipped": float(res.objective_value), "ncand": len(c["cands"]),
           "eb": eb, "ei": ei}
    # reproduction arm: production's own candidates re-raced
    r = REAL_MS(c["objective"], c["cands"], c["bounds"], **c["kw"])
    out["repro"] = (f0 - f(r.x)) / abs(f0)
    for k, e in seeds.items():
        s = np.minimum(om._price_ranked_start(prs, e, pm, DT), ub)
        r = REAL_MS(c["objective"], c["cands"] + [s], c["bounds"], **c["kw"])
        out[k] = (f0 - f(r.x)) / abs(f0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    x = ap.parse_args()
    cells = [(pp, wp, x.flat) for pp in (PRICES[:1] if x.flat else PRICES) for wp in WEATHERS]
    t0p, t0t = time.process_time(), time.thread_time()
    if x.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(x.jobs) as pool:
            rows = pool.map(cell, cells)
    else:
        rows = [cell(c) for c in cells]
    arms = ("b020", "i020", "b015", "b025")
    for r in rows:
        print(f"CELL {r['cell']}: f_seam={r['f0']:.6f} shipped={r['shipped']:.6f} ncand={r['ncand']} "
              f"Ebase={r['eb']:.2f} Einit={r['ei']:.2f} repro={100*r['repro']:+.4f}% "
              + " ".join(f"{k}={100*r[k]:+.4f}%" for k in arms))
    for k in ("repro",) + arms:
        v = np.array([r[k] for r in rows])
        print(f"RESULT {k}_max={100*v.max():.4f} %")
        print(f"RESULT {k}_mean={100*v.mean():.4f} %")
        if len(v) >= 5:
            print(f"RESULT {k}_mean_drop_best={100*np.delete(v, v.argmax()).mean():.4f} %")
        print(f"RESULT {k}_cells_over_0.01pct={int((v > 1e-4).sum())} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
