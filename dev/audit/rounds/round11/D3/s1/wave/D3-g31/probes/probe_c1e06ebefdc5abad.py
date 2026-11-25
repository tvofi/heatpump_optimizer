#!/usr/bin/env python3
# Metric: calls of extend_price_series whose (prices, mask, sigma) differ baseline vs mutant, over the coordinator's call shape (step_starts = utc_step_starts(midnight, n_steps, ...))
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c1e06ebefdc5abad.py
# EXPECTED RESULT prod_differ=0 count (of 192)  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_short_starts_known1_n4_len2 baseline=[0.4]*4 mutant=IndexError  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_differ=2 count (of 6)  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:extend_price_series (price_model.py line 541).
# Perturbation: `if i < len(step_start_times)` -> `if i <= len(step_start_times)` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: none in production (i < n_steps == len(step_starts)); IndexError off-contract.
# Null control: production cases.
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

from custom_components.heatpump_optimizer.drift import utc_step_starts  # noqa: E402

LINE = 541
OLD = "            if i < len(step_start_times)"
NEW = "            if i <= len(step_start_times)"
MUT = mutant(pm.extend_price_series, LINE, OLD, NEW)
STEP = timedelta(minutes=15)
MIDNIGHT = datetime(2026, 1, 16, 0, 0)  # a Friday: the horizon crosses into the weekend


def models():
    young = pm.PriceShapeModel()
    young.days = [2, 2]
    trusted = pm.PriceShapeModel.from_dict({
        "shapes": [[0.6] * 6 + [1.4] * 4 + [0.9] * 6 + [1.6] * 4 + [0.8] * 4, [1.0] * 24],
        "residual_var": [[0.04] * 24, [0.09] * 24], "days": [9, 9], "quarter_days": [9, 9]})
    return {"none": None, "fresh": pm.PriceShapeModel(), "young": young, "trusted": trusted}


def arms(known, n, starts, model):
    return call(pm.extend_price_series, known, n, starts, model), call(MUT, known, n, starts, model)


def production_cases():
    """Calls as coordinator._price_series makes them: step_starts = utc_step_starts(midnight, n, 15 min, offset)."""
    out = []
    for n in (0, 1, 4, 96, 192):
        for offset in (0, 37):
            starts = utc_step_starts(MIDNIGHT, n, STEP, offset)
            for kc in sorted({0, 1, max(n - 1, 0), n, n + 3, n // 2}):
                known = [0.3 + 0.1 * ((i * 7) % 11) - (0.5 if i % 13 == 0 else 0.0) for i in range(kc)]
                for name, model in models().items():
                    out.append((f"n{n}_off{offset}_known{kc}_{name}", known, n, starts, model))
    return out


def direct_cases():
    """Outside the coordinator's contract: step_start_times shorter than the horizon or the known run."""
    t = [MIDNIGHT + STEP * i for i in range(8)]
    tr = models()["trusted"]
    return [
        ("short_starts_known3_n5_len1", [0.4, 0.5, 0.6], 5, t[:1], tr),
        ("short_starts_known1_n4_len2", [0.4], 4, t[:2], tr),
        ("short_starts_known2_n6_len2", [0.4, 0.6], 6, t[:2], tr),
        ("empty_starts_known2_n2", [0.4, 0.6], 2, [], tr),
        ("long_known_n3_len1", [0.4, 0.5, 0.6, 0.7], 3, t[:1], tr),
        ("short_starts_known4_n4_len2", [0.4, 0.5, 0.6, 0.7], 4, t[:2], tr),
    ]


prod = production_cases()
prod_diff = sum(not same(*arms(*c[1:])) for c in prod)
print(f"INPUTS production: {len(prod)} calls, n_steps in (0,1,4,96,192) x offset (0,37) x known lengths "
      f"(0,1,n-1,n,n+3,n/2, negative prices included) x models (None, fresh, young, trusted)")
print(f"RESULT prod_differ={prod_diff} count (of {len(prod)})")
dd = 0
for name, *args in direct_cases():
    b, m = arms(*args)
    d = not same(b, m)
    dd += d
    show = lambda r: type(r).__name__ if isinstance(r, BaseException) else np.round(r[0], 4).tolist()
    print(f"RESULT direct_{name} prices baseline={show(b)} mutant={show(m)} differ={int(d)}")
print(f"RESULT direct_differ={dd} count (of {len(direct_cases())})")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
