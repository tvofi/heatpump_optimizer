#!/usr/bin/env python3
# Metric: the weekday shape confidence, predict() at 08:00 and expected_daily_min after N observed days (PriceShapeModel).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_213a122afd9ff3e1.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED days5 confidence baseline 1.0, mutant 0.5; expected_daily_min baseline a value, mutant None
# EXPECTED moved=N count over N in (1, 5, 7)
# EXPECTED null_delta=0 count (0 days: confidence 0 both; 10 and 12 days: 1.0 both)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:SHAPE_CONFIDENCE_DAYS (line 69), read in PriceShapeModel.confidence (285) and expected_daily_min (342).
# Perturbation: key 213a122afd9ff3e1 CONST `SHAPE_CONFIDENCE_DAYS = 5` -> `10`, by mock.patch.object. Direction: the shape is trusted half as fast; the legionella shopping gate answers None until day 10.
# Null control: 0, 10 and 12 observed days: identical.
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

from datetime import datetime, timedelta
day_a = [0.5] * 6 + [2.0] * 4 + [1.0] * 6 + [2.5] * 4 + [0.8] * 4      # 24 hourly prices
day_b = [1.0] * 6 + [1.0] * 4 + [3.0] * 6 + [1.0] * 4 + [1.0] * 4
mon = datetime(2026, 1, 5, 0, 0)                                        # a Monday: the weekday profile


def learn(days):
    m = pm.PriceShapeModel()
    for k in range(days):
        m.observe_day(mon + timedelta(days=7 * k), day_a if k % 2 == 0 else day_b)
    return m


def metrics(days):
    m = learn(days)
    at = mon + timedelta(days=7 * days, hours=8)
    return {"shape_h8": round(float(m.shapes[0][8]), 9), "confidence": m.confidence(at),
            "predict_h8": round(m.predict(at, 1.0), 9), "expected_daily_min": m.expected_daily_min([0], 1.0)}



moved = 0
for days in (1, 5, 7):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_CONFIDENCE_DAYS", 10):
        m = metrics(days)
    print(f"RESULT days{days}_confidence_baseline={b['confidence']} mutant={m['confidence']}")
    print(f"RESULT days{days}_predict_h8_baseline={b['predict_h8']} mutant={m['predict_h8']}")
    print(f"RESULT days{days}_expected_daily_min_baseline={b['expected_daily_min']} mutant={m['expected_daily_min']}")
    moved += b != m
print(f"RESULT moved={moved} count of 3")
nd = 0
for days in (0, 10, 12):
    b = metrics(days)
    with mock.patch.object(pm, "SHAPE_CONFIDENCE_DAYS", 10):
        nd += b != metrics(days)
print(f"RESULT null_delta={nd} count")

footer()
