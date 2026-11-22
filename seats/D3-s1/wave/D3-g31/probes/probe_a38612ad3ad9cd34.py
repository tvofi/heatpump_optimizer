#!/usr/bin/env python3
# Metric: max |shape delta| after PriceShapeModel.from_dict of a persisted weekday shape, and the guessed 17:00 price at level 1.0
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_a38612ad3ad9cd34.py
# EXPECTED RESULT all_zero max_abs_shape_delta=1 warnings baseline=1 mutant=0 tail_price_17h baseline=1 mutant=0  (exact: counts; tolerance 0)
# EXPECTED RESULT cases_moved=1 count (of 8)  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:_in_domain (via PriceShapeModel.from_dict) (price_model.py line 141).
# Perturbation: `low > 0.0` -> `low >= 0.0` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: to_zero (an all-zero persisted shape is kept and prices the guessed tail at 0).
# Null control: flat ones, the learner's cone edge [0.2]*23+[3.0]: identical.
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

LINE = 141
OLD = "    if low > 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):"
NEW = "    if low >= 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):"
MUT = mutant(pm._in_domain, LINE, OLD, NEW)
lo, hi = pm.SHAPE_MIN, pm.SHAPE_MAX
a = 0.5
edge = a * (hi / lo) * (1.0 + 1e-9)  # the same expression the guard evaluates


def load(shape):
    """PriceShapeModel.from_dict on a persisted payload (production restore path)."""
    return pm.PriceShapeModel.from_dict({"shapes": [list(shape), [1.0] * 24], "days": [9, 9]})


def arms(shape):
    with mock.patch.object(pm._LOGGER, "warning") as w0:
        b = load(shape)
    with mock.patch.object(pm, "_in_domain", MUT), mock.patch.object(pm._LOGGER, "warning") as w1:
        m = load(shape)
    return b, m, w0.call_count, w1.call_count


def tail_price(model):
    """A guessed price for a Wednesday 17:00 step at level 1.0 (what the optimizer reads)."""
    return model.predict(datetime(2026, 1, 14, 17), 1.0)


cases = {
    "all_zero": [0.0] * 24,
    "one_zero": [0.0] + [1.0] * 23,
    "negative_bin": [-0.5] + [1.0] * 23,
    "at_edge": [a] * 23 + [edge],
    "edge_nextafter_up": [a] * 23 + [float(np.nextafter(edge, 10.0))],
    "edge_nextafter_down": [a] * 23 + [float(np.nextafter(edge, 0.0))],
    "flat_ones(null)": [1.0] * 24,
    "learner_cone_max": [lo] * 23 + [hi],
}
moved = 0
for name, shape in cases.items():
    b, m, wb, wm = arms(shape)
    d = float(np.max(np.abs(np.asarray(b.shapes[0]) - np.asarray(m.shapes[0]))))
    moved += int(d > 0 or wb != wm)
    print(f"RESULT {name} max_abs_shape_delta={d:.6g} warnings baseline={wb} mutant={wm} "
          f"tail_price_17h baseline={tail_price(b):.6g} mutant={tail_price(m):.6g}")
print(f"RESULT cases_moved={moved} count (of {len(cases)})")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
