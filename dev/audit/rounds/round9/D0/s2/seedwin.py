"""D0-s2 per-seed diagnostic: which single bang-bang energy anchor reaches
the best basin on one cell's captured seam call (round 9, D0.M2).

Metric: for each energy fraction fr of the bounds' max energy, the objective
the production seam `optimizer:_multi_start_minimize` reaches from the single
seed `_price_ranked_start(prices, fr*Emax)`, relative to the shipped point.
Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
      tools/audit/round9/D0/s2/seedwin.py --cell two,dhw,summer_typical,winter_cold [--call 0]
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "VECLIB_MAXIMUM_OPERATIONS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import race as R
M = R.M

ap = argparse.ArgumentParser()
ap.add_argument("--cell", required=True)
ap.add_argument("--call", type=int, default=0)
ap.add_argument("--horizon", type=int, default=24)
a = ap.parse_args()
tz, dhw, pp, wp = a.cell.split(",")
t0, th0 = time.process_time(), time.thread_time()
o, m, pr, ot, wi, ra, so, st = R.inputs(tz == "two", pp, wp, dhw == "dhw", a.horizon)
r, calls, _ = R.capture(o, pr, ot, wi, ra, so, st, "none")
c = calls[a.call]
prs = R.obj_prices(c)
f = lambda x: float(c["objective"](x, *c["args"]))
f0 = f(c["x"])
ub = np.array(c["bounds"])[:, 1]
emax = float(ub.sum() * R.DT); pmax = float(ub.max())
print(f"shipped f={f0:.6f} kWh={c['x'].sum()*R.DT:.2f} Emax={emax:.1f} n_cand={len(c['candidates'])}")
for i, cand in enumerate(c["candidates"]):
    rr = M._multi_start_minimize(c["objective"], [cand], c["bounds"], args=c["args"],
                                 maxiter=c["maxiter"], batch_objective=c["batch"], fd_eps=c["fd_eps"])
    print(f"  prod cand {i}: start kWh {cand.sum()*R.DT:6.2f} -> f {f(rr.x):.6f} ({100*(f0-f(rr.x))/abs(f0):+.4f}%)")
best = (np.inf, None)
for fr in R.LADDER:
    s = np.minimum(M._price_ranked_start(prs, emax * fr, pmax, R.DT), ub)
    rr = M._multi_start_minimize(c["objective"], [s], c["bounds"], args=c["args"],
                                 maxiter=c["maxiter"], batch_objective=c["batch"], fd_eps=c["fd_eps"])
    v = f(rr.x)
    best = min(best, (v, fr))
    print(f"  seed fr={fr:4.2f} (kWh {s.sum()*R.DT:6.2f}) -> f {v:.6f} ({100*(f0-v)/abs(f0):+.4f}%) kWh_end {rr.x.sum()*R.DT:.2f}")
print(f"RESULT best_seed_fraction={best[1]}")
print(f"RESULT best_seed_gap={100*(f0-best[0])/abs(f0):.4f} %")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
