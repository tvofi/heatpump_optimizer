"""V2 (independent) harness for D0-s2-02: do seeds from a family unrelated to the
finder's Emax bang-bang ladder find lower basins than production's seed set, and more
so at shoulder prices than at flat prices?

Metric (one line): per cell, gap = (f_prod - f_rand)/|f_prod| where f_prod is the
captured objective at the x the FIRST optimizer:_multi_start_minimize call returned and
f_rand is the REAL _multi_start_minimize re-run on the same captured objective/bounds/
args/jac with production's candidates plus K=12 seeded random starts (seed k: per-step
U(0,1) * ub * s_k, s_k = k/12 energy scale, rng seeded by cell name), counted only if
the arm's floor violation (degree-steps below the closure's temp_min_bounds, zones the
objective scores) is no worse than production's + 0.01. Paired excess per matched
(topology, dhw, weather): gap_shoulder - gap_flat.
Count key: the production objective closure's value.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/verify-v2/v2_random_seeds.py [--jobs 2]
Expected: measured, see verify-v2.md (finder: shoulder max 1.2012 %, mean 0.3909 %;
flat max 0.3247 %, mean 0.0918 %, with its ladder family).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2,
4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse, zlib
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
REAL_MS = om._multi_start_minimize
K = 12


def cmap(fn):
    return {n: c.cell_contents for n, c in zip(fn.__code__.co_freevars, fn.__closure__ or ())}


def viol(obj, x, tz):
    cm = cmap(obj)
    tr = cm["_space_traj"](np.asarray(x, float))
    tmin = cm["temp_min_bounds"]
    zs = (tr[2][1:], tr[3][1:]) if tz else (tr[0][1:],)
    return float(sum(np.maximum(0, tmin - z).sum() for z in zs))


def cell(a):
    tz, dhw, pp, wp = a
    p = ThermalParameters.from_config(house(two_zone=tz))
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    o = HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                                                target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = P_prices(pp, START)
    ot, wi, ra, so = P_weather(wp, START)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                      dhw_temperature=48.0)
    caps = []

    def ms_w(objective, candidates, bounds, *aa, **kw):
        res = REAL_MS(objective, candidates, bounds, *aa, **kw)
        if not caps:
            caps.append(dict(objective=objective, cands=[np.asarray(c, float).copy() for c in candidates],
                             bounds=list(bounds), kw=dict(kw), x=np.asarray(res.x, float).copy()))
        return res

    with mock.patch.object(om, "_multi_start_minimize", ms_w):
        o.optimize(st, pr, ot, wi, ra, so, START)
    c = caps[0]
    args = tuple(c["kw"].get("args", ()))
    f = lambda x: float(c["objective"](np.asarray(x, float), *args))
    f0 = f(c["x"])
    v0 = viol(c["objective"], c["x"], tz)
    lb = np.array([b[0] for b in c["bounds"]], float)
    ub = np.array([b[1] for b in c["bounds"]], float)
    name = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{wp}"
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    seeds = [np.clip(rng.uniform(0, 1, ub.size) * ub * (k / K), lb, ub) for k in range(1, K + 1)]
    r = REAL_MS(c["objective"], c["cands"] + seeds, c["bounds"], **c["kw"])
    f1, v1 = f(r.x), viol(c["objective"], r.x, tz)
    ok = v1 <= v0 + 0.01
    gap = (f0 - f1) / abs(f0) if ok else 0.0
    return dict(cell=f"{name}|{pp}", key=name, pp=pp, f0=f0, f1=f1, gap=gap, v0=v0, v1=v1, ok=ok,
                kwh0=float(np.sum(c["x"]) * .25), kwh1=float(np.sum(r.x) * .25),
                s00=float(c["x"][0]), s01=float(r.x[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--weather", default="winter_cold,winter_mild,summer_cool,shoulder")
    a = ap.parse_args()
    cells = [(t, d, pp, wp) for pp in ("shoulder", "flat") for wp in a.weather.split(",")
             for t in (False, True) for d in (False, True)]
    t0p, t0t = time.process_time(), time.thread_time()
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool:
            rows = pool.map(cell, cells)
    else:
        rows = [cell(c) for c in cells]
    for r in rows:
        print(f"CELL {r['cell']:40s} f {r['f0']:.5f} -> {r['f1']:.5f} gap {100*r['gap']:+.4f}% "
              f"(abs {r['f0']-r['f1']:+.4f}) viol {r['v0']:.4f}->{r['v1']:.4f} ok={r['ok']} "
              f"kWh {r['kwh0']:.2f}->{r['kwh1']:.2f} step0 {r['s00']:.2f}->{r['s01']:.2f}")
    g = {pp: {r["key"]: r["gap"] for r in rows if r["pp"] == pp} for pp in ("shoulder", "flat")}
    for pp in ("shoulder", "flat"):
        v = np.array(list(g[pp].values()))
        print(f"RESULT {pp}_gap_max={100*v.max():.4f} %")
        print(f"RESULT {pp}_gap_mean={100*v.mean():.4f} %")
        print(f"RESULT {pp}_gap_mean_drop_best={100*np.delete(v, v.argmax()).mean():.4f} %")
        print(f"RESULT {pp}_cells_over_0.1pct={int((v > 1e-3).sum())} of {len(v)} count")
    ex = np.array([g["shoulder"][k] - g["flat"][k] for k in g["shoulder"]])
    print(f"RESULT paired_excess_max={100*ex.max():.4f} pp")
    print(f"RESULT paired_excess_mean={100*ex.mean():.4f} pp")
    print(f"RESULT paired_excess_mean_drop_best={100*np.delete(ex, ex.argmax()).mean():.4f} pp")
    print(f"RESULT paired_excess_cells_over_0.1pp={int((ex > 1e-3).sum())} of {len(ex)} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
