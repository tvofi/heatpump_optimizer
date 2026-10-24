"""D0-s1 round 9: the coordinator captures -- race the multi-start calls of a
real HeatPumpOptimizerCoordinator.async_run_optimization cycle.

Metric (one line): per coordinator cell, gap = (shipped objective - best feasible
challenger objective) / |shipped objective|, on the exact captured production
objective of every optimizer:_multi_start_minimize call the cycle makes.
Count key: production's own captured objective evaluated at the returned plan.

Command (from the repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
    tools/audit/round9/D0/s1/coord.py [--cells coord_dhw:winter_typical,...]
Inputs: tests/golden.py:coordinator_scenarios() configs; prices = the axis profile
(tests/profiles.py, hourly, two days); weather = winter_cold hourly; clock frozen
at golden.START. The solve is run in-process (coordinator._await_optimize patched
to call optimize_in_process inline) so the seam can be captured.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box B1 (4 vCPU Linux, CPython 3.14.0rc2).
Expected: see REPORT.md; tolerance +/-0.05 pp.
Perturbation: none of its own -- this is the M4 coordinator-capture grid; a
production edit to the seed set or stop rule moves its gaps exactly as it moves
race.py's (same challenger code, imported).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, asyncio, argparse, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from datetime import timedelta
from unittest import mock
import race
from race import om, tight, seam, LADDER
from profiles import prices as P_prices, weather as P_weather
import golden
from harness import FakeEntry, FakeHass
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as cm
from heatpump_optimizer.optimizer import HeatPumpOptimizer, optimize_in_process

FEAS_TOL = race.FEAS_TOL


def feas_opt(o, st, space, h):
    m = o.model
    room, slab, up, lo, *_ = m.simulate_trajectory(
        st, space, h["ot"], h["wi"], h["ra"], h["so"], 0.25)
    tz = bool(m.params.two_zone_enabled)
    zones = [np.asarray(up[1:]), np.asarray(lo[1:])] if tz else [np.asarray(room[1:])]
    tmin = np.asarray(h["tmin"])[: len(zones[0])]
    fl = sum(float(np.maximum(0, tmin - z).sum()) for z in zones)
    ce = sum(float(np.maximum(0, z - 23.0).sum()) for z in zones)
    return fl, ce


def run(name, pp):
    cfg = dict(golden.coordinator_scenarios()[name])
    dt_util.freeze(golden.START)
    hass = FakeHass(); coord = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    pq = P_prices(pp, golden.START)          # 96 quarter steps, hourly-constant
    ot, wi, ra, so = P_weather("winter_cold", golden.START)
    coord._prices = [{"total": float(pq[(h % 24) * 4]), "level": "NORMAL",
                      "starts_at": (golden.START + timedelta(hours=h)).isoformat()} for h in range(48)]
    coord._weather_forecast = [{"datetime": (golden.START + timedelta(hours=h)).isoformat(),
                                "temperature": float(ot[(h % 24) * 4]), "wind_speed": 2.0,
                                "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [float(so[(h % 24) * 4]) for h in range(48)]
    got = {}
    caps = []

    async def inline(hass_, optimizer, state, *positional, **keywords):
        got["opt"], got["state"], got["pos"], got["kw"] = optimizer, state, positional, keywords
        return optimize_in_process(optimizer, state, positional, keywords)

    def rec(objective, candidates, bounds, *a, **kw):
        cands = [np.asarray(c, float).copy() for c in candidates]
        res = race.REAL_MS(objective, candidates, bounds, *a, **kw)
        x = np.asarray(res.x, float).copy()
        args = tuple(kw.get("args", a[0] if a else ()))
        caps.append({"objective": objective, "candidates": cands,
                     "bounds": [tuple(float(v) for v in b) for b in bounds], "args": args,
                     "maxiter": kw.get("maxiter", 300), "batch": kw.get("batch_objective"),
                     "fd_eps": kw.get("fd_eps", 1e-4), "x": x, "f": float(objective(x, *args))})
        return res

    real_base = HeatPumpOptimizer._compute_baseline_power

    def base_rec(self, *a, **kw):
        out = real_base(self, *a, **kw)
        got.setdefault("base_e", float(np.sum(out[0]) * 0.25))
        return out

    with mock.patch.object(cm, "_await_optimize", inline), \
            mock.patch.object(HeatPumpOptimizer, "_compute_baseline_power", base_rec), \
            mock.patch.object(om, "_multi_start_minimize", rec):
        asyncio.run(coord.async_run_optimization())
    dt_util.freeze(None)
    res = coord._optimization_result
    o, st = got["opt"], got["state"]
    pos = got["pos"]
    pr = np.asarray(pos[0], float)
    h = {"ot": np.asarray(pos[1], float), "wi": np.asarray(pos[2], float),
         "ra": np.asarray(pos[3], float), "so": np.asarray(pos[4], float),
         "tmin": np.asarray(getattr(res, "min_temp_bounds", None) or
                            [o.config.min_temp] * len(pr), float)}
    shipped = np.asarray(res.power_schedule, float)
    fl0, ce0 = feas_opt(o, st, shipped, h)
    base_e = got.get("base_e", 1.0)
    pmax = float(o.model.params.max_electrical_power)
    best = (np.inf, None, None)
    lines = []
    for ci, cap in enumerate(caps):
        ub = np.array([b[1] for b in cap["bounds"]])
        trials = []
        xp, fp, _ = tight(cap, cap["x"]); trials.append(("polish", xp, fp))
        for k, c in enumerate(cap["candidates"]):
            x, f = seam(cap, [c]); trials.append((f"cand{k}", x, f))
        for fr in LADDER:
            s = np.minimum(om._price_ranked_start(pr, base_e * fr, pmax, 0.25), ub)
            x, f = seam(cap, [s]); trials.append((f"anchor{fr}", x, f))
        ok = []
        for n, x, f in trials:
            fl, ce = feas_opt(o, st, x, h)
            if fl <= fl0 + FEAS_TOL and ce <= ce0 + FEAS_TOL:
                ok.append((f, n, x))
        ok.sort(key=lambda t: t[0])
        fb, nb, xb = ok[0]
        xw, fw, _ = tight(cap, xb)
        flw, cew = feas_opt(o, st, xw, h)
        if fw < fb and flw <= fl0 + FEAS_TOL and cew <= ce0 + FEAS_TOL:
            fb, nb, xb = fw, nb + "+tight", xw
        lines.append(f"   call{ci} n_cand={len(cap['candidates'])} f_prod={cap['f']:.6f} "
                     f"polish={fp:.6f} best={fb:.6f} ({nb}) Efrac prod={np.sum(cap['x'])*0.25/base_e:.3f} "
                     f"best={np.sum(xb)*0.25/base_e:.3f} step0 {cap['x'][0]:.3f}->{xb[0]:.3f}")
        if fb < best[0]:
            best = (fb, ci, nb)
    f0 = float(res.objective_value)
    gap = (f0 - best[0]) / abs(f0)
    print(f"CELL {name}|{pp}: n_steps={len(pr)} dhw={o.model.params.dhw_enabled} "
          f"two_zone={o.model.params.two_zone_enabled} shipped={f0:.6f} best={best[0]:.6f} "
          f"gap={100*gap:.4f}% abs={f0-best[0]:.4f} via call{best[1]}:{best[2]} floor={fl0:.4f} calls={len(caps)}")
    for l in lines:
        print(l)
    return gap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="")
    a = ap.parse_args()
    if a.cells:
        cells = [tuple(c.split(":")) for c in a.cells.split(",")]
    else:
        cells = [(n, pp) for n in ("coord_minimal", "coord_dhw", "coord_two_zone", "coord_all_features")
                 for pp in race.PRICES]
    t0p, t0t = time.process_time(), time.thread_time()
    gaps = [run(n, pp) for n, pp in cells]
    g = np.array(gaps)
    print(f"RESULT cells={len(g)} count")
    print(f"RESULT gap_rel_max={100*g.max():.4f} %")
    print(f"RESULT cells_gap_over_0.1pct={int((g > 1e-3).sum())} count")
    if len(g) >= 2:
        print(f"RESULT gap_rel_mean={100*g.mean():.4f} %")
        print(f"RESULT gap_rel_mean_drop_max={100*np.delete(g, g.argmax()).mean():.4f} %")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
