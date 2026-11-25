#!/usr/bin/env python3
# Metric: calls of PriceShapeModel.sigma whose value differs baseline vs mutant, over from_dict models and finite levels (production domain)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_45cd5752f930a064.py
# EXPECTED RESULT prod_differ=0 count (of 840)  (exact: counts; tolerance 0)
# EXPECTED RESULT null_differ=0 count  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_var-1e-3_level0.5 baseline=0.0 mutant=nan  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_var0_level_inf baseline=0.0 mutant=nan  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.sigma (price_model.py line 357).
# Perturbation: `if var <= 0.0:` -> `if False:` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: none in production (from_dict floors var at 0, extend_price_series passes a finite level); 0.0 -> nan off-domain.
# Null control: var 0.04, trust 1.
# Count key: the value the production symbol returns (or the learner state it writes), never an input attribute.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
_T0 = (time.process_time(), time.thread_time())
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)


def mutant(func, line, old, new):
    """``func`` recompiled from its own source with file line ``line`` mutated (in memory only)."""
    lines, start = inspect.getsourcelines(func)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor line {line} moved: {lines[i]!r}"
    lines[i] = new + "\n"
    src = textwrap.dedent("".join(lines))
    ns = dict(pm.__dict__)
    exec(compile(src, pm.__file__, "exec"), ns)
    return ns[func.__name__]


def same(a, b):
    """Exact equality that treats nan == nan and compares arrays and exceptions."""
    if isinstance(a, BaseException) or isinstance(b, BaseException):
        return type(a) is type(b)
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True)
    if isinstance(a, float) and isinstance(b, float):
        return (a == b) or (np.isnan(a) and np.isnan(b))
    return a == b


def call(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except Exception as err:  # the mutant may raise where the baseline does not
        return err


from datetime import datetime  # noqa: E402

LINE, OLD, NEW = 357, "        if var <= 0.0:", "        if False:"
M = pm.PriceShapeModel
MUT = mutant(M.sigma, LINE, OLD, NEW)
WHENS = [datetime(2026, 1, 14, h) for h in (0, 8, 17)] + [datetime(2026, 1, 18, h) for h in (2, 19)]


def stored(var, days):
    return M.from_dict({"residual_var": [[var] * pm.HOURS_PER_DAY for _ in range(2)], "days": [days, days]})


def direct(var, days):
    m = M()
    m.residual_var = [[var] * pm.HOURS_PER_DAY for _ in range(2)]
    m.days = [days, days]
    return m


def arms(model, levels):
    base = [call(model.sigma, w, lv) for w in WHENS for lv in levels]
    with mock.patch.object(M, "sigma", MUT):
        mut = [call(model.sigma, w, lv) for w in WHENS for lv in levels]
    return base, mut


# Production: from_dict floors var at 0; extend_price_series passes a finite level
# (finite known prices over a shape mean > 1e-6), negative when prices are.
LEVELS = (0.0, -0.0, 0.5, 2.0, -0.3, 1e-300, 1e300)
prod_inputs = [(v, d) for v in (0.0, -0.0, 1e-12, 0.04, -0.01, -5.0) for d in (0, 1, 5, 9)]
prod_diff = 0
for v, d in prod_inputs:
    b, m = arms(stored(v, d), LEVELS)
    prod_diff += sum(not same(x, y) for x, y in zip(b, m))
null_diff = sum(not same(x, y) for x, y in zip(*arms(stored(0.04, 5), LEVELS)))
direct = {
    "var-1e-3_level0.5": (direct(-1e-3, 5), (0.5,)),
    "var0_level_inf": (direct(0.0, 5), (float("inf"),)),
    "var0_level_nan": (direct(0.0, 5), (float("nan"),)),
    "var-0.0_level_inf": (direct(-0.0, 5), (float("inf"),)),
}
print(f"INPUTS production(from_dict) var x days={prod_inputs} x levels={LEVELS} x {len(WHENS)} instants")
print(f"RESULT prod_differ={prod_diff} count (of {len(prod_inputs) * len(LEVELS) * len(WHENS)} calls)")
print(f"RESULT null_differ={null_diff} count (var 0.04, trust 1)")
for name, (model, lv) in direct.items():
    b, m = arms(model, lv)
    print(f"RESULT direct_{name} baseline={b[0]} mutant={m[0]} differ={sum(not same(x, y) for x, y in zip(b, m))}")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
