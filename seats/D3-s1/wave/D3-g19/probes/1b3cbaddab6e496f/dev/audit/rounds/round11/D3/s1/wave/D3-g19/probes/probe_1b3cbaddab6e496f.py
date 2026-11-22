#!/usr/bin/env python3
# Metric: max |weight_baseline - weight_mutant| of HeatPumpOptimizer._anticipatory_weights over a sweep of step lengths,
#   including dt > 8 h where lookahead = int(8/dt) = 0 and end == i (the only inputs that reach `continue`).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_1b3cbaddab6e496f.py
# EXPECTED RESULT guard_hits_baseline>0 count  (dt 9 h and 24 h: every step takes `continue`)
# EXPECTED RESULT max_abs_delta=0.0  (EQUIVALENT: with end == i the mutant takes np.mean of an empty slice = nan; nan > 0.5
#   and nan > 1.1 are False, so weights[i] stays 1.0 exactly as the `continue` leaves it; only a RuntimeWarning differs)
# EXPECTED RESULT mutant_runtime_warnings>0 count
# EXPECTED RESULT null_max_abs_delta=0.0  (dt 0.25 and 1 h with sun and loss signals: the guard never fires)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._anticipatory_weights (line 3402
#   `            if end <= i:`), called at optimizer.py:5463 and 5735 to shape the initial guess.
# Perturbation: `if end <= i:` -> `if False:` (GUARD_OFF 1b3cbaddab6e496f), applied in memory (method recompiled from its own
#   source, called on the same instance for the mutant arm). Direction: none observable on any input tried.
# Null control: dt 0.25 h and 1 h, where end > i always.
# Inputs tried: dt in (0.25, 1, 4, 8, 8.5, 9, 24) h x signals (sun 2 kW / loss 1.3, sun 0 / loss 1.0, sun nan / loss nan,
#   sun inf), n_steps 1..6.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
from pathlib import Path
from unittest import mock


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
sys.path.insert(0, str(ROOT))
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer as O  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters, ThermalModel  # noqa: E402

H = O.HeatPumpOptimizer
opt = H(ThermalModel(ThermalParameters()), O.OptimizationConfig(
    horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
mut = mutated(O, H, "_anticipatory_weights", 3402, "            if end <= i:", "            if False:")
base = H._anticipatory_weights
sig = inspect.signature(base)
print(f"RESULT signature={list(sig.parameters)}")


def call(fn, n, dt, sun, loss):
    kw = {}
    for name in list(sig.parameters)[1:]:
        if name == "n_steps":
            kw[name] = n
        elif name == "dt":
            kw[name] = dt
        elif "solar" in name:
            kw[name] = np.full(n, sun)
        elif "loss" in name:
            kw[name] = np.full(n, loss)
    return fn(opt, **kw)


hits = warns = 0
worst = null_worst = 0.0
for dt in (0.25, 1.0, 4.0, 8.0, 8.5, 9.0, 24.0):
    for sun, loss in ((2.0, 1.3), (0.0, 1.0), (float("nan"), float("nan")), (float("inf"), 1.0)):
        for n in range(1, 7):
            with warnings.catch_warnings(record=True) as wb:
                warnings.simplefilter("always")
                b = call(base, n, dt, sun, loss)
            with warnings.catch_warnings(record=True) as wm:
                warnings.simplefilter("always")
                m = call(mut, n, dt, sun, loss)
            warns += len(wm) - len(wb)
            if int(8 / dt) == 0:
                hits += n
            d = float(np.nanmax(np.abs(b - m))) if np.any(np.isfinite(b - m)) else 0.0
            d = d if np.array_equal(np.isnan(b), np.isnan(m)) else float("inf")
            if dt <= 1.0:
                null_worst = max(null_worst, d)
            worst = max(worst, d)
print(f"RESULT guard_hits_baseline={hits} count")
print(f"RESULT max_abs_delta={worst}")
print(f"RESULT mutant_runtime_warnings={warns} count")
print(f"RESULT null_max_abs_delta={null_worst}")
tail()
