#!/usr/bin/env python3
# Metric: the reason classify_space_steps gives an active step whose PV surplus is exactly 1e-6 kW.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2aff1f5c0b10dffa.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED tie baseline the next rank ('cheap_price'), mutant 'solar_surplus'
# EXPECTED moved=1 count
# EXPECTED null_delta=0 count (surplus 0, 2e-6, 1.0)
# EXPECTED reach: surplus_eq_1e-6 absent (0) over 1999 active golden steps
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2303 `surplus[i] > 1e-6`.
# Perturbation: key 2aff1f5c0b10dffa CMP_BOUND `>` -> `>=`, in memory. Direction: a lower-ranked reason -> solar_surplus at the exact tie.
# Null control: surplus 0.0, 2e-6, 1.0 at the step: identical.
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

mut = mutant(opt, "classify_space_steps", 2303, '        if surplus is not None and i < len(surplus) and surplus[i] > 1e-6:', '        if surplus is not None and i < len(surplus) and surplus[i] >= 1e-6:')
n = 20


def run(fn, i, room=21.0, floor=19.0, surplus=None, hlf=1.0, room_len=None):
    power = np.zeros(n); power[i] = 3.0
    rooms = np.full(n + 1 if room_len is None else room_len, 21.0); rooms[min(i + 1, len(rooms) - 1)] = room
    floors = np.full(n, floor)
    hl = np.ones(n); hl[i] = hlf
    return call(fn, power, np.linspace(1.0, 2.0, n), rooms, floors, hl, surplus, n)



def sp(v):
    s = np.zeros(n); s[2] = v
    return s


b, m = run(opt.classify_space_steps, 2, surplus=sp(1e-6)), run(mut, 2, surplus=sp(1e-6))
print(f"RESULT tie_reason_baseline={b[2] if isinstance(b, list) else b!r}")
print(f"RESULT tie_reason_mutant={m[2] if isinstance(m, list) else m!r}")
print(f"RESULT moved={int(not same(b, m))} count")
nd = sum(not same(run(opt.classify_space_steps, 2, surplus=sp(v)), run(mut, 2, surplus=sp(v))) for v in (0.0, 2e-6, 1.0))
print(f"RESULT null_delta={nd} count")
# The sibling predicate idle_codes reads for the same series (optimizer.py:2237) is `> 1e-6`: under the mutant the
# two classifiers split at the tie.
codes = opt.idle_codes(4, np.zeros(4), None, None, None, np.array([0.0, 1e-6, 0.0, 0.0]), None, None, 0.05)
print(f"RESULT idle_codes_at_tie={codes!r} (idle_codes's own `> 1e-6` reads the tie as no sun)")

reach("classify_space_steps")
footer()
