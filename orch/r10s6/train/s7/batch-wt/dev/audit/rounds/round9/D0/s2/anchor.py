"""D0-s2 missed high-energy basin harness (round 9, D0.M2/M4).

Metric (one line): per cell, gap = (f_prod - f_chal)/|f_prod| of the FIRST
`optimizer:_multi_start_minimize` call's recorded objective, where f_chal is
the same seam re-run on production's own candidate list plus bang-bang seeds
`_price_ranked_start(prices, k*E1)` for k in (1.25, 1.5, 2.0), E1 = energy of
production's own 1.0x price-ranked anchor (candidate index 1).
Count key: the objective value the production closure returns at the plan the
seam delivers.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
      tools/audit/round9/D0/s2/anchor.py [--perturb none|add_anchors] \
      [--prices summer_typical,summer_negative,shoulder,flat] [--tz 0,1] [--dhw 0,1]
Perturbation: --perturb add_anchors hands the same three seeds to production's
own seam (in memory, mock.patch.object) -> every cell's gap goes to 0.
Expected (this box): see REPORT.md, gap_max ~1.2 % (tolerance +-0.05 pp; the
basin choice is BLAS-dependent across boxes).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B2, 4 CPU.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "VECLIB_MAXIMUM_OPERATIONS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from unittest import mock
import race as R
M = R.M
K = (1.25, 1.5, 2.0)
WEATHER = ("winter_cold", "winter_mild", "summer_cool", "shoulder")


def seeds_for(cands, bounds, prs):
    ub = np.array(bounds)[:, 1]
    e1 = float(np.sum(cands[1]) * R.DT)
    pmax = float(ub.max())
    return [np.minimum(M._price_ranked_start(prs, e1 * k, pmax, R.DT), ub) for k in K]


def run_cell(tz, dhw, pp, wp, perturb):
    o, m, pr, ot, wi, ra, so, st = R.inputs(tz, pp, wp, dhw, 24)
    cap = []
    real = M._multi_start_minimize

    def rec(objective, candidates, bounds, *a, **kw):
        cands = [np.asarray(c, float) for c in candidates]
        n_orig = len(cands)
        if perturb == "add_anchors" and not cap:
            cands = cands + seeds_for(cands, bounds, R.obj_prices(
                {"objective": objective}))
        res = real(objective, cands, bounds, *a, **kw)
        cap.append(dict(objective=objective, candidates=cands, bounds=bounds,
                        args=tuple(kw.get("args", ())), maxiter=kw.get("maxiter"),
                        batch=kw.get("batch_objective"), x=np.asarray(res.x, float),
                        n_orig=n_orig))
        return res

    with mock.patch.object(M, "_multi_start_minimize", rec):
        r = o.optimize(st, pr, ot, wi, ra, so, R.START)
    c = cap[0]
    prs = R.obj_prices(c)
    f = lambda x: float(c["objective"](x, *c["args"]))
    base = c["candidates"][:c["n_orig"]]
    res = real(c["objective"], list(base) + seeds_for(base, c["bounds"], prs),
               c["bounds"], args=c["args"], maxiter=c["maxiter"],
               batch_objective=c["batch"])
    f0, f1 = f(c["x"]), f(res.x)
    return dict(f0=f0, f1=f1, gap=(f0 - f1) / abs(f0), gap_abs=f0 - f1,
                viol0=R.violation(c, c["x"]), viol1=R.violation(c, res.x),
                s0=(float(c["x"][0]), float(res.x[0])),
                kwh=(float(c["x"].sum() * R.DT), float(res.x.sum() * R.DT)),
                e=(R.energy_sek(c, c["x"], prs), R.energy_sek(c, res.x, prs)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="none")
    ap.add_argument("--prices", default="summer_typical,summer_negative,shoulder,flat")
    ap.add_argument("--tz", default="0,1")
    ap.add_argument("--dhw", default="0,1")
    a = ap.parse_args()
    t0, th0 = time.process_time(), time.thread_time()
    per_price = {}
    for pp in a.prices.split(","):
        for wp in WEATHER:
            for tz in (bool(int(x)) for x in a.tz.split(",")):
                for dhw in (bool(int(x)) for x in a.dhw.split(",")):
                    d = run_cell(tz, dhw, pp, wp, a.perturb)
                    name = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}"
                    per_price.setdefault(pp, []).append((name, d))
                    print(f"CELL {name:42s} f {d['f0']:9.5f} -> {d['f1']:9.5f} gap "
                          f"{100*d['gap']:+.4f}% ({d['gap_abs']:+.4f} SEK) viol "
                          f"{d['viol0']:.4f}->{d['viol1']:.4f} step0 {d['s0'][0]:.2f}->{d['s0'][1]:.2f} "
                          f"kWh {d['kwh'][0]:.2f}->{d['kwh'][1]:.2f} energySEK "
                          f"{d['e'][0]:.3f}->{d['e'][1]:.3f}", flush=True)
    allg = []
    for pp, rows in per_price.items():
        g = np.array([d["gap"] for _, d in rows]); ab = np.array([d["gap_abs"] for _, d in rows])
        allg += list(g)
        print(f"RESULT {pp}_cells={len(g)} count")
        print(f"RESULT {pp}_gap_max={100*g.max():.4f} %")
        print(f"RESULT {pp}_gap_min={100*g.min():.4f} %")
        print(f"RESULT {pp}_gap_mean={100*g.mean():.4f} %")
        print(f"RESULT {pp}_gap_mean_drop_most_favourable={100*np.sort(g)[:-1].mean():.4f} %")
        print(f"RESULT {pp}_gap_abs_max={ab.max():.4f} SEK")
        print(f"RESULT {pp}_cells_over_0p5pct={int((g > 5e-3).sum())} count")
        print(f"RESULT {pp}_viol_worse={sum(1 for _, d in rows if d['viol1'] > d['viol0'] + 1e-6)} count")
    print(f"RESULT gap_max_all={100*max(allg):.4f} %")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
