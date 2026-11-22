#!/usr/bin/env python3
# Metric: rain_anticipation_factor _analyze_forecast_trajectory returns for 4.0 mm/h of rain all day (intensity 2, past the 1.0 cap), 24 x 1 h.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_9644a454ac8f288b.py
# EXPECTED RESULT rain_anticipation_baseline=1.15
# EXPECTED RESULT rain_anticipation_mutant=1.3  (intensity 2.0 uncapped)
# EXPECTED RESULT abs_delta=0.15
# EXPECTED RESULT pre_heat_urgency_moved=1 count (0.75 -> 1.0)
# EXPECTED RESULT null_delta=0 count  (1.0 mm/h: intensity 0.5 under the cap)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._analyze_forecast_trajectory (line 4272
#   `rain_intensity = min(avg_future_precip / 2.0, 1.0)`), called once per solve at optimizer.py:4377; its dict shapes the initial guess and is
#   published as the plan's predictive_info (solar_reduction_factor, pre_heat_urgency, ...).
# Perturbation: `rain_intensity = min(avg_future_precip / 2.0, 1.0)` -> `rain_intensity = (avg_future_precip / 2.0)` (CLAMP_DROP 9644a454ac8f288b), applied in memory (method recompiled from its own
#   source, called on the same optimizer instance for the mutant arm only). Direction: rain_anticipation rises above 1 + (multiplier - 1) for precipitation > 2 mm/h.
# Null control: 1.0 mm/h.
# Inputs tried: 4.0 mm/h; 2.0 mm/h (at the cap: identical); null 1.0 mm/h.
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
mut = mutated(O, H, "_analyze_forecast_trajectory", 4272, '            rain_intensity = min(avg_future_precip / 2.0, 1.0)', '            rain_intensity = (avg_future_precip / 2.0)')
base = H._analyze_forecast_trajectory


def call(fn, sr, precip, out, dt=1.0):
    n = len(sr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(opt, np.asarray(sr, float), np.zeros(n), np.asarray(precip, float), np.asarray(out, float), dt)


def delta(case):
    b, m = call(base, **case), call(mut, **case)
    return b, m, {k: (b.get(k), m.get(k)) for k in set(b) | set(m) if repr(b.get(k)) != repr(m.get(k))}
b, m, d = delta(dict(sr=[0.0] * 24, precip=[4.0] * 24, out=[0.0] * 24))
at_cap = len(delta(dict(sr=[0.0] * 24, precip=[2.0] * 24, out=[0.0] * 24))[2])
nd = len(delta(dict(sr=[0.0] * 24, precip=[1.0] * 24, out=[0.0] * 24))[2])
print(f"RESULT rain_anticipation_baseline={b['rain_anticipation_factor']:.4f}")
print(f"RESULT rain_anticipation_mutant={m['rain_anticipation_factor']:.4f}")
print(f"RESULT abs_delta={abs(b['rain_anticipation_factor'] - m['rain_anticipation_factor']):.4f}")
print(f"RESULT pre_heat_urgency={b['pre_heat_urgency']:.4f}->{m['pre_heat_urgency']:.4f}")
print(f"RESULT pre_heat_urgency_moved={int(abs(b['pre_heat_urgency'] - m['pre_heat_urgency']) > 1e-12)} count")
print(f"RESULT at_cap_delta={at_cap} count")
print(f"RESULT null_delta={nd} count")
tail()
