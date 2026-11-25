#!/usr/bin/env python3
# Metric: the reason list classify_space_steps returns for n_steps == 0, baseline vs mutant, over in-contract array inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_4434c1fcedef6b6d.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED moved_in_contract=0 count of 6 inputs (every arm returns [])
# EXPECTED power_none: baseline [] mutant 'raises ...' (out of contract)
# EXPECTED reach: n_steps_zero absent (0) over the 50 golden scenarios
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2286 `if n_steps == 0:`.
# Perturbation: key 4434c1fcedef6b6d GUARD_OFF `    if n_steps == 0:` -> `    if False:`, in memory. Direction: none found in contract.
# Null control: the n_steps >= 1 call (guard false either way): identical.
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

mut = mutant(opt, "classify_space_steps", 2286, "    if n_steps == 0:", "    if False:")
E = np.array([])
four = np.array([0.0, 1.0, 2.0, 0.0])
inputs = {
    "all_empty": (E, E, np.array([21.0]), E, E, None),
    "four_long": (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "prices_empty": (four, E, np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "prices_nan": (four, np.full(4, np.nan), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None),
    "surplus_given": (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), np.ones(4)),
    "room_empty": (four, np.ones(4), E, np.full(4, 19.0), np.ones(4), None),
}
moved = 0
for name, a in inputs.items():
    b, m = call(opt.classify_space_steps, *a, 0), call(mut, *a, 0)
    moved += not same(b, m)
    print(f"RESULT n0_{name}_baseline={b!r} mutant={m!r}")
print(f"RESULT moved_in_contract={moved} count of {len(inputs)} inputs")
b = call(opt.classify_space_steps, None, None, None, None, None, None, 0)
m = call(mut, None, None, None, None, None, None, 0)
print(f"RESULT power_none_baseline={b!r} mutant={m!r} (out of contract: the annotations say np.ndarray)")
a = (four, np.ones(4), np.full(5, 21.0), np.full(4, 19.0), np.ones(4), None)
print(f"RESULT null_delta={int(not same(call(opt.classify_space_steps, *a, 4), call(mut, *a, 4)))} count")
reach("classify_space_steps")
footer()
