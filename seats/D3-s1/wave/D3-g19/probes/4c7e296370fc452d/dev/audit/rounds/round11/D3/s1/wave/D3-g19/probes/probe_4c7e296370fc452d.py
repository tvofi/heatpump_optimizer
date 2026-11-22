#!/usr/bin/env python3
# Metric: rain_anticipation_factor _analyze_forecast_trajectory returns when the decay-weighted mean precipitation is exactly 0.1 mm/h (a 1-step forecast of 0.1 mm/h).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_4c7e296370fc452d.py
# EXPECTED RESULT rain_anticipation_baseline=1.0
# EXPECTED RESULT rain_anticipation_mutant=1.0075  (1 + (1.15-1) * 0.05)
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (0.09 and 0.2 mm/h)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._analyze_forecast_trajectory (line 4271
#   `if avg_future_precip > 0.1:`), called once per solve at optimizer.py:4377; its dict shapes the initial guess and is
#   published as the plan's predictive_info (solar_reduction_factor, pre_heat_urgency, ...).
# Perturbation: `if avg_future_precip > 0.1:` -> `if avg_future_precip >= 0.1:` (CMP_BOUND 4c7e296370fc452d), applied in memory (method recompiled from its own
#   source, called on the same optimizer instance for the mutant arm only). Direction: rain_anticipation 1.0 -> 1.0075 at exactly 0.1 mm/h.
# Null control: 0.09 and 0.2 mm/h.
# Inputs tried: 0.1 mm/h at n=1, 2, 4, 24 (n>=4 sums to 0.10000000000000002 and both arms fire); 0.09; 0.2.
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
mut = mutated(O, H, "_analyze_forecast_trajectory", 4271, '        if avg_future_precip > 0.1:', '        if avg_future_precip >= 0.1:')
base = H._analyze_forecast_trajectory


def call(fn, sr, precip, out, dt=1.0):
    n = len(sr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(opt, np.asarray(sr, float), np.zeros(n), np.asarray(precip, float), np.asarray(out, float), dt)


def delta(case):
    b, m = call(base, **case), call(mut, **case)
    return b, m, {k: (b.get(k), m.get(k)) for k in set(b) | set(m) if repr(b.get(k)) != repr(m.get(k))}
b, m, d = delta(dict(sr=[0.0], precip=[0.1], out=[0.0]))
moved_n = sum(int(bool(delta(dict(sr=[0.0] * n, precip=[0.1] * n, out=[0.0] * n))[2])) for n in (1, 2, 4, 24))
nd = sum(len(delta(dict(sr=[0.0] * 4, precip=[v] * 4, out=[0.0] * 4))[2]) for v in (0.09, 0.2))
print(f"RESULT rain_anticipation_baseline={b['rain_anticipation_factor']}")
print(f"RESULT rain_anticipation_mutant={m['rain_anticipation_factor']}")
print(f"RESULT moved={int(b['rain_anticipation_factor'] != m['rain_anticipation_factor'])} count")
print(f"RESULT lengths_moved={moved_n} of 4 count")
print(f"RESULT null_delta={nd} count")
tail()
