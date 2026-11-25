#!/usr/bin/env python3
# Metric: calls of PriceShapeModel.quarter_factor whose value differs baseline vs mutant, over models loaded by from_dict (production domain)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c9f07b68ade152e6.py
# EXPECTED RESULT prod_differ=0 count (of 900)  (exact: counts; tolerance 0)
# EXPECTED RESULT null_differ=0 count  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_factor_nan_trust0 baseline=1.0 mutant=nan (outside from_dict's domain)  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.quarter_factor (price_model.py line 303).
# Perturbation: `if trust <= 0.0:` -> `if trust < 0.0:` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: none in production; at trust == 0 the mutant computes 1 + (f - 1) * 0 == 1.0 for every finite f.
# Null control: trust 1, factor 1.3.
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

LINE, OLD, NEW = 303, "        if trust <= 0.0:", "        if trust < 0.0:"
M = pm.PriceShapeModel
MUT = mutant(M.quarter_factor, LINE, OLD, NEW)
WHENS = [datetime(2026, 1, 14, h, m) for h in (0, 7, 17, 23) for m in (0, 15, 30, 45)] + \
        [datetime(2026, 1, 17, h, m) for h in (3, 18) for m in (0, 45)]


def stored(factor, qdays):
    """A persisted model as from_dict loads it (the only way a model reaches production)."""
    return M.from_dict({"quarter_factors": [[factor] * pm.QUARTERS_PER_DAY for _ in range(2)],
                        "quarter_days": [qdays, qdays]})


def direct(factor, qdays):
    m = M()
    m.quarter_factors = [[factor] * pm.QUARTERS_PER_DAY for _ in range(2)]
    m.quarter_days = [qdays, qdays]
    return m


def arms(model):
    base = [call(model.quarter_factor, w) for w in WHENS]
    with mock.patch.object(M, "quarter_factor", MUT):
        mut = [call(model.quarter_factor, w) for w in WHENS]
    return base, mut


prod_inputs = [(f, q) for f in (0.25, 0.5, 1.0, 1.3, 4.0, float("nan"), float("inf"), -1.0, 0.0) for q in (0, 1, 3, 5, 9)]
prod_diff = 0
for f, q in prod_inputs:
    b, m = arms(stored(f, q))
    prod_diff += sum(not same(x, y) for x, y in zip(b, m))
null_diff = sum(not same(x, y) for x, y in zip(*arms(stored(1.3, 5))))
direct_inputs = [(float("nan"), 0), (float("inf"), 0), (-float("inf"), 0), (1.3, 0), (0.25, 0)]
direct_rows = {}
for f, q in direct_inputs:
    b, m = arms(direct(f, q))
    direct_rows[(f, q)] = (b[0], m[0], sum(not same(x, y) for x, y in zip(b, m)))
print(f"INPUTS production(from_dict) factor x quarter_days={prod_inputs} at {len(WHENS)} instants each")
print(f"INPUTS direct(construct, outside from_dict's domain)={direct_inputs}")
print(f"RESULT prod_differ={prod_diff} count (of {len(prod_inputs) * len(WHENS)} calls)")
print(f"RESULT null_differ={null_diff} count (trust 1, factor 1.3)")
for (f, q), (b, m, d) in direct_rows.items():
    print(f"RESULT direct_factor_{f}_trust0 baseline={b} mutant={m} differ={d}")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
