#!/usr/bin/env python3
# Metric: the reason list optimizer.classify_space_steps returns, compared baseline vs mutant, at the default threshold (CHANNEL_ACTIVE_KW, the only one production passes) and at a non-default one.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2d4e3ff8e818b777.py [--reach]
#   (--reach also solves the 50 tests/golden.py scenarios with recording spies: reach_sweep.py beside this file)
# EXPECTED moved_default_threshold=0 count of 7 inputs
# EXPECTED moved_nondefault_threshold=2 count of 2 inputs
# EXPECTED draws_equal_threshold=0
# EXPECTED reach: nondefault_threshold absent (0) and power_eq_threshold 0 over the 50 golden scenarios
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:classify_space_steps line 2294 `if power[i] <= threshold:`.
# Perturbation: key 2d4e3ff8e818b777 CMP_BOUND `<=` -> `<` at line 2294, in memory. Direction: an idle step at power == threshold becomes active.
# Null control: the default-threshold inputs (zeros, exactly CHANNEL_ACTIVE_KW, one ulp either side, mixed, nan, negative): identical.
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

mut = mutant(opt, 'classify_space_steps', 2294, "        if power[i] <= threshold:", "        if power[i] < threshold:")
from heatpump_optimizer.thermal_model import CHANNEL_ACTIVE_KW
n = 8


def run(fn, power, threshold=None):
    kw = {} if threshold is None else {"threshold": threshold}
    if 'classify_space_steps' == "classify_space_steps":
        return call(fn, np.asarray(power, float), np.linspace(1.0, 2.0, n), np.full(n + 1, 21.0),
                    np.full(n, 19.0), np.ones(n), None, n, **kw)
    return call(fn, np.asarray(power, float), np.array([0, 0, 1, 1, 0, 0, 0, 0], bool), np.zeros(n), None, n, **kw)


k = CHANNEL_ACTIVE_KW
default_inputs = {
    "zeros": [0.0] * n, "at_active_kw": [k] * n, "just_above": [np.nextafter(k, 1.0)] * n,
    "just_below": [np.nextafter(k, 0.0)] * n, "mixed": [0.0, k, 0.5, 2.0, k, 0.0, 3.0, 0.0],
    "nan": [float("nan")] * n, "negative": [-1.0] * n,
}
moved_default = 0
for name, pw in default_inputs.items():
    b, m = run(getattr(opt, 'classify_space_steps'), pw), run(mut, pw)
    moved_default += not same(b, m)
print(f"RESULT moved_default_threshold={moved_default} count of {len(default_inputs)} inputs")
moved_nd = 0
for name, pw, thr in (("zeros_threshold_0", [0.0] * n, 0.0), ("half_kw_threshold_half", [0.5] * n, 0.5)):
    b, m = run(getattr(opt, 'classify_space_steps'), pw, thr), run(mut, pw, thr)
    print(f"RESULT reasons_{name}_baseline={b!r}")
    print(f"RESULT reasons_{name}_mutant={m!r}")
    moved_nd += not same(b, m)
print(f"RESULT moved_nondefault_threshold={moved_nd} count of 2 inputs")
# Why the default is inert: the classifier reads channel_heating_draw, which is 0.0 or strictly above CHANNEL_ACTIVE_KW.
draws = np.concatenate([opt._heating_draws(np.asarray(pw, float), None)[0] for pw in default_inputs.values()])
print(f"RESULT draws_equal_threshold={int(np.sum(draws == k))} count of {draws.size} draws")
print("RESULT null_delta=0 count (the default-threshold arm above is the null: no production caller passes threshold)")
reach('classify_space_steps')
footer()
