#!/usr/bin/env python3
# Metric: the solver_status label optimizer._solver_status returns for a SciPy result with success=True, and the objective evaluations it spends classifying it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_e196155b7525014c.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED status_success_worse_than_x0 baseline 'optimal', mutant 'suboptimal (...)'
# EXPECTED status_real_lbfgsb_x0_outside_bounds baseline 'optimal', mutant 'suboptimal (...)' (scipy's own result)
# EXPECTED moved=3 count over the 4 success inputs (success_better is the in-arm control); objective_evals per success 0 -> 2
# EXPECTED null_delta=0 count (success=False results: the guard is false either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_solver_status line 2844 `if result.success:`; called at optimizer.py:4983 and 5574.
# Perturbation: key e196155b7525014c GUARD_OFF `    if result.success:` -> `    if False:`, in memory (re-compiled from its own source). Direction: 'optimal' -> 'suboptimal (<message>)' on a success whose point scores above its start.
# Null control: success=False results (ABNORMAL_TERMINATION_IN_LNSRCH, better and worse than the start): identical labels.
# Values are exact (deterministic); no timing is measured.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_CPU0, _THR0 = time.process_time(), time.thread_time()


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for _p in (str(ROOT), str(ROOT / "tests"), str(ROOT / "custom_components")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np  # noqa: E402
# The package as tests/golden.py imports it, so the reach sweep's spies and this probe share one module.
from heatpump_optimizer import optimizer as opt  # noqa: E402
from heatpump_optimizer import price_model as pm  # noqa: E402


def mutant(mod, name, lineno, old, new):
    """`name` re-compiled from its own source with line `lineno` (exactly `old`) replaced by `new`."""
    fn = getattr(mod, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + "".join(lines), mod.__file__, "exec"), ns)
    return ns[name]


def call(fn, *a, **k):
    """The value, or the exception's type name: a raise is an observable outcome too."""
    try:
        return fn(*a, **k)
    except Exception as exc:  # noqa: BLE001
        return f"raises {type(exc).__name__}"


def same(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (math.isnan(a) and math.isnan(b))
    return a == b


def footer():
    cpu, thr = time.process_time() - _CPU0, time.thread_time() - _THR0
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swapins = int([l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")][0])
    except Exception:  # noqa: BLE001
        swapins = -1
    print(f"RESULT swapins={swapins} count")


def reach(symbol):
    """--reach: the shared golden-matrix sweep (reach_sweep.py beside this probe) for `symbol`."""
    if "--reach" not in sys.argv:
        print("RESULT reach=skipped (pass --reach to solve the 50 golden scenarios with spies)")
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("reach_sweep", Path(__file__).resolve().parent / "reach_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rec = mod.sweep({symbol})
    mod.print_reach(rec)
    return rec

from scipy.optimize import minimize
mut = mutant(opt, "_solver_status", 2844, "    if result.success:", "    if False:")
evals = [0]


def f(x):
    evals[0] += 1
    return float(np.sum(np.square(np.asarray(x, dtype=float) - 2.0)))


def boom(x):
    raise RuntimeError("objective unavailable")


x0 = np.zeros(3)
# A real L-BFGS-B success whose point scores ABOVE its start: x0 = 2 lies outside the box [0, 1],
# SciPy projects it in, converges at 1 (f = 1) while f(x0) = 0.
real = minimize(lambda x: float((x[0] - 2.0) ** 2), np.array([2.0]), method="L-BFGS-B", bounds=[(0.0, 1.0)])
print(f"RESULT real_lbfgsb_success={bool(real.success)} f_x={float(real.fun):.6f} f_x0=0.000000")
cases = {
    "success_better": (SimpleNamespace(success=True, x=np.full(3, 2.0), message="CONVERGENCE"), f, x0),
    "success_worse_than_x0": (SimpleNamespace(success=True, x=np.full(3, 5.0), message="CONVERGENCE"), f, x0),
    "success_objective_raises": (SimpleNamespace(success=True, x=np.ones(3), message="CONVERGENCE"), boom, x0),
    "real_lbfgsb_x0_outside_bounds": (real, lambda x: float((np.asarray(x)[0] - 2.0) ** 2), np.array([2.0])),
}
nulls = {
    "fail_worse": (SimpleNamespace(success=False, x=np.full(3, 5.0), message="ABNORMAL_TERMINATION_IN_LNSRCH"), f, x0),
    "fail_better": (SimpleNamespace(success=False, x=np.full(3, 2.0), message="ABNORMAL_TERMINATION_IN_LNSRCH"), f, x0),
}
moved = 0
for name, (res, obj, start) in cases.items():
    evals[0] = 0; b = call(opt._solver_status, res, obj, start); eb = evals[0]
    evals[0] = 0; m = call(mut, res, obj, start); em = evals[0]
    print(f"RESULT status_{name}_baseline={b!r}")
    print(f"RESULT status_{name}_mutant={m!r}")
    if obj is f:
        print(f"RESULT objective_evals_{name}={eb}->{em} count")
    moved += not same(b, m)
print(f"RESULT moved={moved} count")
null_delta = 0
for name, (res, obj, start) in nulls.items():
    null_delta += not same(call(opt._solver_status, res, obj, start), call(mut, res, obj, start))
print(f"RESULT null_delta={null_delta} count")
reach("solver_status")
footer()
