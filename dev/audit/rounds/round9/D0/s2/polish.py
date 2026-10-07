"""D0-s2 stop-rule residue harness (round 9, D0.M2).

Metric (one line): per cell, gap = (f_prod - f_pol)/|f_prod| where f_prod is
the recorded objective at the plan the FIRST `optimizer:_multi_start_minimize`
call returns and f_pol is production's own L-BFGS-B (`optimizer:_scoped_minimize`,
same bounds, same batched jac) restarted from that plan at ftol=1e-12,
gtol=1e-10, maxiter=5000. Count key: the production objective closure's value.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
      tools/audit/round9/D0/s2/polish.py [--horizon 48] [--perturb none|ftol_tight] \
      [--prices summer_typical,summer_negative,shoulder,flat] [--weather winter_cold,shoulder]
Perturbation: --perturb ftol_tight rewrites the ftol production passes to
`_scoped_minimize` from 1e-6 to 1e-12 (in memory) -> gap goes to ~0.
Null control: the same cells at --prices flat.
Expected (this box): h48 two|dhw|summer_typical|winter_cold ~0.65 % (+-0.05 pp).
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


def run_cell(tz, dhw, pp, wp, horizon, perturb):
    o, m, pr, ot, wi, ra, so, st = R.inputs(tz, pp, wp, dhw, horizon)
    cap = []
    real_ms, real_sc = M._multi_start_minimize, M._scoped_minimize
    nit = [0]

    def rec(objective, candidates, bounds, *a, **kw):
        res = real_ms(objective, candidates, bounds, *a, **kw)
        cap.append(dict(objective=objective, candidates=candidates,
                        bounds=[tuple(float(v) for v in b) for b in bounds],
                        args=tuple(kw.get("args", ())), maxiter=kw.get("maxiter"),
                        batch=kw.get("batch_objective"), fd_eps=kw.get("fd_eps", 1e-4),
                        x=np.asarray(res.x, float).copy()))
        return res

    def sc(*a, **kw):
        if perturb == "ftol_tight":
            kw = dict(kw); o_ = dict(kw["options"]); o_["ftol"] = 1e-12
            kw["options"] = o_
        r = real_sc(*a, **kw)
        nit[0] += int(r.nit)
        return r

    with mock.patch.object(M, "_multi_start_minimize", rec), \
            mock.patch.object(M, "_scoped_minimize", sc):
        o.optimize(st, pr, ot, wi, ra, so, R.START)
    c = cap[0]
    f = lambda x: float(c["objective"](x, *c["args"]))
    xp = R.polish(c, c["x"])
    f0, f1 = f(c["x"]), f(xp)
    prs = R.obj_prices(c)
    return dict(f0=f0, f1=f1, gap=(f0 - f1) / abs(f0), gap_abs=f0 - f1,
                viol0=R.violation(c, c["x"]), viol1=R.violation(c, xp),
                s0=(float(c["x"][0]), float(xp[0])), nit=nit[0],
                e=(R.energy_sek(c, c["x"], prs), R.energy_sek(c, xp, prs)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="none")
    ap.add_argument("--horizon", type=int, default=48)
    ap.add_argument("--prices", default="summer_typical,summer_negative,shoulder,flat")
    ap.add_argument("--weather", default="winter_cold,shoulder")
    ap.add_argument("--tz", default="0,1")
    ap.add_argument("--dhw", default="0,1")
    a = ap.parse_args()
    t0, th0 = time.process_time(), time.thread_time()
    per = {}
    for pp in a.prices.split(","):
        for wp in a.weather.split(","):
            for tz in (bool(int(x)) for x in a.tz.split(",")):
                for dhw in (bool(int(x)) for x in a.dhw.split(",")):
                    d = run_cell(tz, dhw, pp, wp, a.horizon, a.perturb)
                    name = f"{'two' if tz else 'one'}|{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|h{a.horizon}"
                    per.setdefault(pp, []).append(d)
                    print(f"CELL {name:46s} f {d['f0']:9.5f} -> {d['f1']:9.5f} gap "
                          f"{100*d['gap']:+.4f}% ({d['gap_abs']:+.4f}) viol {d['viol0']:.4f}->{d['viol1']:.4f} "
                          f"step0 {d['s0'][0]:.2f}->{d['s0'][1]:.2f} energySEK {d['e'][0]:.3f}->{d['e'][1]:.3f} "
                          f"prod_nit {d['nit']}", flush=True)
    for pp, rows in per.items():
        g = np.array([d["gap"] for d in rows]); ab = np.array([d["gap_abs"] for d in rows])
        print(f"RESULT {pp}_cells={len(g)} count")
        print(f"RESULT {pp}_gap_max={100*g.max():.4f} %")
        print(f"RESULT {pp}_gap_min={100*g.min():.4f} %")
        print(f"RESULT {pp}_gap_mean={100*g.mean():.4f} %")
        if len(g) >= 5:
            print(f"RESULT {pp}_gap_mean_drop_most_favourable={100*np.sort(g)[:-1].mean():.4f} %")
        print(f"RESULT {pp}_gap_abs_max={ab.max():.4f} SEK")
        print(f"RESULT {pp}_cells_over_0p1pct={int((g > 1e-3).sum())} count")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
