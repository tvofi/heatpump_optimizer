"""D2-s2 / D2.M3 -- the solver's gradient against a central finite difference.

Metric (one line): per scenario, over K random interior points x (seed 9, uniform in the
  solve's own bounds): rel_err = ||g_prod - g_c||_2 / ||g_c||_2, where g_prod is
  optimizer:_batch_fd_gradient (the jac L-BFGS-B is handed: forward difference, eps 1e-4,
  batched objective) and g_c is a central difference of the SCALAR objective with h=1e-6.
  Also where the worst component sits (step index / n).
  count key: the ndarray _batch_fd_gradient returns (production seam).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/gradient_fd.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT.
Perturbation (--perturb): fd_eps passed to _batch_fd_gradient 1e-4 -> 1e-7 (in memory);
  rel_err must fall (the forward-difference truncation shrinks with the step).
Instrumented: optimizer:_batch_fd_gradient, optimizer:_multi_start_minimize (objective capture)
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

EPS = 1e-7 if "--perturb" in sys.argv else 1e-4
K = 4
SCEN = ["winter_single_no_dhw", "winter_two_zone_no_dhw", "shoulder", "valve_storage",
        "capacity_tariff", "cycling_cost", "flat_prices", "extreme_prices"]
if "--only" in sys.argv:
    SCEN = sys.argv[sys.argv.index("--only") + 1].split(",")
_orig_msm = optmod._multi_start_minimize
cap = {}


def msm(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    if "obj" not in cap:
        cap.update(obj=objective, batch=batch_objective, bounds=list(bounds), args=args)
    return _orig_msm(objective, candidates, bounds, args=args, maxiter=maxiter,
                     batch_objective=batch_objective, fd_eps=fd_eps)


optmod._multi_start_minimize = msm
t0 = time.process_time(); tt0 = time.thread_time()
rng = np.random.default_rng(9)
rows = []
for name in SCEN:
    cap.clear()
    golden.capture(name, golden.SCENARIOS[name])
    if cap.get("batch") is None:
        print(f"# {name}: no batch objective, skipped"); continue
    obj, batch, bounds, args = cap["obj"], cap["batch"], cap["bounds"], cap["args"]
    lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
    errs = []; worst_pos = []
    for _ in range(K):
        x = lb + (ub - lb) * rng.uniform(0.05, 0.95, lb.size)
        f0 = float(obj(x, *args))
        g = optmod._batch_fd_gradient(batch, args, x, f0, EPS, bounds)
        h = 1e-6
        P = np.tile(x, (lb.size, 1)); M = P.copy()
        P[np.arange(lb.size), np.arange(lb.size)] += h
        M[np.arange(lb.size), np.arange(lb.size)] -= h
        gc = (np.asarray(batch(P, *args)) - np.asarray(batch(M, *args))) / (2 * h)
        e = float(np.linalg.norm(g - gc) / max(np.linalg.norm(gc), 1e-12))
        errs.append(e)
        worst_pos.append(int(np.argmax(np.abs(g - gc))) / lb.size)
    rows.append((name, max(errs), float(np.median(errs)), worst_pos))
    print(f"# {name:24s} rel_err max={max(errs):.3e} median={np.median(errs):.3e} worst_at(frac of horizon)={[round(w, 2) for w in worst_pos]}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
mx = [r[1] for r in rows]
print(f"RESULT cells={len(rows)} count")
print(f"RESULT rel_err_max={max(mx):.3e} ratio")
print(f"RESULT rel_err_min_cell={min(mx):.3e} ratio")
print(f"RESULT rel_err_max_drop_worst={sorted(mx)[-2]:.3e} ratio")
print(f"RESULT fd_eps={EPS}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
