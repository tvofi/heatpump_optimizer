#!/usr/bin/env python3
# Metric: weekend days learned from one folded Mon..Sun week, and the guessed Saturday 03:00 price at level 1.0
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_28de20de50a9540b.py
# EXPECTED RESULT weekend_days baseline=2 mutant=1  (exact: counts; tolerance 0)
# EXPECTED RESULT weekday_days baseline=5 mutant=6  (exact: counts; tolerance 0)
# EXPECTED RESULT saturday_0300_predict_level1 baseline=0.737143 mutant=0.564779  (exact: counts; tolerance 0)
# EXPECTED RESULT null_days_differ=0 count  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:_profile_index (via PriceShapeLearner.fold, PriceShapeModel.predict) (price_model.py line 155).
# Perturbation: `weekday() >= 5` -> `weekday() > 5` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: down (Saturday folds into and is predicted from the weekday profile).
# Null control: Mon-Fri and Sunday index identically.
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


from datetime import datetime, timedelta  # noqa: E402

LINE = 155
OLD = "    return PROFILE_WEEKEND if when.weekday() >= 5 else PROFILE_WEEKDAY"
NEW = "    return PROFILE_WEEKEND if when.weekday() > 5 else PROFILE_WEEKDAY"
MUT = mutant(pm._profile_index, LINE, OLD, NEW)
weekday_shape = [0.6] * 6 + [1.4] * 4 + [0.9] * 6 + [1.6] * 4 + [0.8] * 4
weekend_shape = [0.9] * 24
weekend_shape[3] = 0.3


def fold_week(start):
    """Seven consecutive days folded through the production learner (PriceShapeLearner.fold)."""
    rows = []
    for i in range(7):
        day = start + timedelta(days=i)
        shape = weekend_shape if day.weekday() >= 5 else weekday_shape
        for h in range(24):
            rows.append({"total": shape[h], "starts_at": (day + timedelta(hours=h)).isoformat()})
    lr = pm.PriceShapeLearner()
    lr.fold(rows)
    return lr.model


def measure():
    m = fold_week(datetime(2026, 1, 5))  # Monday..Sunday
    sat = datetime(2026, 1, 10, 3)
    return (m.days[pm.PROFILE_WEEKDAY], m.days[pm.PROFILE_WEEKEND],
            pm._profile_index(sat), round(m.predict(sat, 1.0), 6))


b = measure()
with mock.patch.object(pm, "_profile_index", MUT):
    m = measure()
nulls = [datetime(2026, 1, 5) + timedelta(days=i) for i in range(7) if i != 5]
null_diff = sum(pm._profile_index(d) != MUT(d) for d in nulls)
print("INPUTS one week Mon 2026-01-05..Sun 01-11 hourly; Saturday 2026-01-10 03:00")
print(f"RESULT weekday_days baseline={b[0]} mutant={m[0]}")
print(f"RESULT weekend_days baseline={b[1]} mutant={m[1]}")
print(f"RESULT saturday_profile_index baseline={b[2]} mutant={m[2]}")
print(f"RESULT saturday_0300_predict_level1 baseline={b[3]} mutant={m[3]}")
print(f"RESULT null_days_differ={null_diff} count (Mon-Fri, Sun)")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
