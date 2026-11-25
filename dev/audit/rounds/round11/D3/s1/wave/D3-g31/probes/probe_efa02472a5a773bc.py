#!/usr/bin/env python3
# Metric: max over 24 bins of PriceShapeModel.summary()['weekend_sigma'] after 28 observed days (published as GridView.price_prior)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_efa02472a5a773bc.py
# EXPECTED RESULT weekend_sigma_max_baseline=0.4726  (exact: counts; tolerance 0)
# EXPECTED RESULT weekend_sigma_max_mutant=0.0  (exact: counts; tolerance 0)
# EXPECTED RESULT weekend_sigma_bins_differ=24 count  (exact: counts; tolerance 0)
# EXPECTED RESULT null_bins_differ=0 count  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.summary (price_model.py line 421).
# Perturbation: `round(float(np.sqrt(max(0.0, v))), 4)` (weekend_sigma) -> `round(float(np.sqrt((0.0))), 4)` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: to_zero.
# Null control: a fresh model (residual_var 0): both arms all zeros.
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


from datetime import date, datetime, timedelta  # noqa: E402

LINE = 421
OLD = "                round(float(np.sqrt(max(0.0, v))), 4)"
NEW = "                round(float(np.sqrt((0.0))), 4)"
FIELD = "weekend_sigma"
M = pm.PriceShapeModel
MUT = mutant(M.summary, LINE, OLD, NEW)
rng = np.random.default_rng(11)
base_day = np.array([0.6] * 6 + [1.2] * 4 + [0.9] * 6 + [1.6] * 4 + [0.8] * 4)


def learned(n_days):
    """A model that folded n_days real days through observe_day (the production learner)."""
    m = M()
    d0 = date(2026, 1, 5)  # a Monday
    for i in range(n_days):
        day = d0 + timedelta(days=i)
        prices = base_day * float(rng.uniform(0.7, 1.4)) * (1.0 + rng.normal(0.0, 0.25, 24))
        m.observe_day(datetime(day.year, day.month, day.day, 12), [float(abs(p)) + 0.05 for p in prices])
    return m


def arms(model):
    b = model.summary()[FIELD]
    with mock.patch.object(M, "summary", MUT):
        mt = model.summary()[FIELD]
    return b, mt


model = learned(28)
b, mt = arms(model)
other = "weekend_sigma" if FIELD == "weekday_sigma" else "weekday_sigma"
other_base = model.summary()[other]
with mock.patch.object(M, "summary", MUT):
    other_moved = int(model.summary()[other] != other_base)
nb, nm = arms(M())
idx = pm.PROFILE_WEEKDAY if FIELD == "weekday_sigma" else pm.PROFILE_WEEKEND
print("INPUTS 28 observed days (Mon 2026-01-05..), seeded rng 11; null: a fresh model")
print(f"RESULT residual_var_max={max(model.residual_var[idx]):.6f}")
print(f"RESULT {FIELD}_max_baseline={max(b)}")
print(f"RESULT {FIELD}_max_mutant={max(mt)}")
print(f"RESULT {FIELD}_bins_differ={sum(x != y for x, y in zip(b, mt))} count (of 24)")
print(f"RESULT other_field_moved={other_moved} count")
print(f"RESULT null_bins_differ={sum(x != y for x, y in zip(nb, nm))} count (fresh model, var 0)")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
