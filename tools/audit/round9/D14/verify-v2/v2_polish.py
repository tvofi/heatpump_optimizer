"""D14 round 9, verifier V2 (independent) for D14-s3-02: does the multi-start seam ship a non-stationary point?

Metric (one line): per production optimizer:_multi_start_minimize call, polish_gap =
(shipped fun - fun after a tight L-BFGS-B polish STARTED FROM THE SHIPPED x, same objective, same
args, same bounds, same batched FD gradient at the production eps, ftol 1e-12, gtol 1e-9,
maxiter 3000) / |shipped fun|; v2_polish_misses = calls with polish_gap > 1e-3.
Different from the finder's metric (re-solve from the seam's own candidates): this one asks only
whether the shipped point is stationary under the shipped gradient model.
Key: the objective value production's own objective returns at production's x and at the polished x.

Cells: tests/golden.py SCENARIOS (hand-picked, listed below), each built by golden.make and solved
by the real HeatPumpOptimizer.optimize through golden.capture.
Null control: the flat_prices / valve_storage_flat_prices cells are reported separately; a gap
there is not a price-arbitrage gap (the finder says the gap survives flat prices).
Perturbation (--loose): production ftol multiplied by 100 (options patched in memory on
optimizer._scoped_minimize) -> misses expected to rise.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_polish.py [--loose] [--cells a,b,...]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging, contextlib, io
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import golden  # noqa: E402
import heatpump_optimizer.optimizer as O  # noqa: E402

cells = ["winter_single_no_dhw", "winter_two_zone_no_dhw", "winter_single_dhw", "shoulder",
         "extreme_prices", "negative_prices", "narrow_band", "flat_prices"]
for a in sys.argv:
    if a.startswith("--cells="):
        cells = a.split("=", 1)[1].split(",")
LOOSE = "--loose" in sys.argv
NULL = {"flat_prices", "valve_storage_flat_prices"}

orig_ms = O._multi_start_minimize
orig_sm = O._scoped_minimize
records = []
STAT = []


def scoped(*a, **k):
    if LOOSE and "options" in k and "ftol" in k["options"]:
        k = dict(k, options=dict(k["options"], ftol=k["options"]["ftol"] * 100))
    return orig_sm(*a, **k)


def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    r = orig_ms(objective, candidates, bounds, args, maxiter, batch_objective, fd_eps)
    x0 = np.asarray(r.x, dtype=float)
    f_ship = float(objective(x0, *args))
    jac = None
    if batch_objective is not None and O._bounds_supported_by_batch(bounds):
        def jac(x, *a):
            return O._batch_fd_gradient(batch_objective, a, x, float(objective(x, *a)), fd_eps, bounds)
    p = minimize(objective, x0, args=args, jac=jac, method="L-BFGS-B", bounds=bounds,
                 options={"ftol": 1e-12, "gtol": 1e-9, "maxiter": 3000})
    # second polish without the production gradient: scipy's own 2-point FD at eps 1e-7,
    # so an ABNORMAL line-search exit caused by the coarse production eps cannot hide a descent.
    p2 = minimize(objective, x0, args=args, method="L-BFGS-B", bounds=bounds,
                  options={"ftol": 1e-12, "gtol": 1e-9, "maxiter": 3000, "eps": 1e-7})
    f_pol = min(float(p.fun), float(p2.fun), f_ship)
    records.append((f_ship, f_pol, len(x0)))
    STAT.append((int(p.nit), str(p.message)[:40], int(p2.nit), str(p2.message)[:40]))
    return r


O._multi_start_minimize = ms
O._scoped_minimize = scoped
rows = []
for name in cells:
    records.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        golden.capture(name, golden.SCENARIOS[name])
    for i, (fs, fp, n) in enumerate(records):
        gap = (fs - fp) / abs(fs) if fs else 0.0
        rows.append((name, i, gap))
        print(f"CALL {name}#{i} n={n} shipped={fs:.6f} polished={fp:.6f} gap={gap * 100:.4f}% polish={STAT[len(rows) - 1]}", flush=True)
calls = len(rows)
miss = [r for r in rows if r[2] > 1e-3]
nmiss = [r for r in miss if r[0] in NULL]
print(f"RESULT v2_calls={calls} count")
print(f"RESULT v2_polish_misses={len(miss)} count")
print(f"RESULT v2_polish_misses_null_flat={len(nmiss)}_of_{sum(1 for r in rows if r[0] in NULL)} count")
if rows:
    g = sorted(r[2] for r in rows)
    print(f"RESULT v2_polish_gap_max={g[-1] * 100:.4f} %")
    print(f"RESULT v2_polish_gap_max_drop_worst={g[-2] * 100 if len(g) > 1 else 0:.4f} %")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
