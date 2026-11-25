#!/usr/bin/env python3
# Metric: the terminal row cost _terminal_row_cost(...)'s row_cost returns on its split (cop_buffer != cop_end) with a refill law branch for terms [2, 3] at a cop_buffer below the 1e-6 floor; and the smallest COP production can hand it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_55022279c6d6bbda.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED row_cost at cop_buffer=0.0: baseline a finite 2e6-scale value, mutant 'raises ZeroDivisionError'
# EXPECTED moved=3 count of 4 sub-floor COPs (0, -1, 1e-9 move; 1e-6 is the floor itself and ties)
# EXPECTED null_delta=0 count
# EXPECTED reach_min_cop_over_scan >= 1.0 (ThermalModel._cop_law: max(cop, 1.0))
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_terminal_row_cost.row_cost line 3329; built at optimizer.py:3695 from ThermalModel.compute_cop / marginal_cop.
# Perturbation: key 55022279c6d6bbda CLAMP_DROP `+ buffer_deficit / max(cop_buffer, 1e-6)` -> `+ buffer_deficit / (cop_buffer)`, in memory (the enclosing _terminal_row_cost re-compiled). Direction: a finite floored cost -> ZeroDivisionError / sign flip below COP 1e-6.
# Null control: COPs at or above the floor (1.0, 1.05, 2.5, 4.0) and nan: identical.
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

mut = mutant(opt, "_terminal_row_cost", 3329, '                    + buffer_deficit / max(cop_buffer, 1e-6)', '                    + buffer_deficit / (cop_buffer)')
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
stores = ((10.0, "room", 21.0, 1.0), (5.0, "buffer", 50.0, 1.0))
terms = [2.0, 3.0]


def ident(e):
    return e


def row(fn, cop):
    rc, _ = fn(1.0, *(lambda cop: (3.0, cop, stores, ident))(cop))
    return call(rc, terms)


moved, tried = 0, []
for cop in (0.0, -1.0, 1e-9, 1e-6):
    b, m = row(opt._terminal_row_cost, cop), row(mut, cop)
    print(f"RESULT row_cost_cop_buffer_{cop!r}_baseline={b!r}")
    print(f"RESULT row_cost_cop_buffer_{cop!r}_mutant={m!r}")
    moved += not same(b, m); tried.append(cop)
print(f"RESULT moved={moved} count of {len(tried)} sub-floor COPs")
null_delta = sum(not same(row(opt._terminal_row_cost, c), row(mut, c)) for c in (1.0, 1.05, 2.5, 4.0, float("nan")))
print(f"RESULT null_delta={null_delta} count (COP 1.0, 1.05, 2.5, 4.0, nan)")
# Reach: every COP the terminal cost receives is ThermalModel._cop_law's, floored by `return max(cop, 1.0)`.
lo = math.inf
for kw in ({}, {"cop_flow_carnot": True}, {"cop_flow_carnot": True, "flow_curve_cop": True}):
    p = ThermalParameters()
    for k, v in kw.items():
        setattr(p, k, v)
    m_ = ThermalModel(p)
    for t in np.linspace(-60.0, 45.0, 106):
        for hum in (None, 0.0, 60.0, 100.0):
            lo = min(lo, m_.compute_cop(float(t), humidity=hum))
            for st in (20.0, 35.0, 55.0, 70.0, 90.0):
                lo = min(lo, m_.marginal_cop(float(t), "buffer", store_temp=st, humidity=hum))
print(f"RESULT reach_min_cop_over_scan={lo:.4f} (outdoor -60..45 C, humidity, store 20..90 C, 3 parameter sets)")
reach("terminal_row_cost")
footer()
