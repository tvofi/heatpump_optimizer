#!/usr/bin/env python3
# Metric: solar_reduction_factor _analyze_forecast_trajectory returns when 6 x typical heat loss is below the 0.1 floor (outdoor 20.99 C vs target 21.0, 0.15 kW/K) with 1 W/m2 sun, 24 x 1 h.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_7f048d7823b17826.py
# EXPECTED RESULT solar_reduction_baseline=0.8824
# EXPECTED RESULT solar_reduction_mutant=0.6  (denominator 0.009 instead of 0.1: solar_fraction saturates)
# EXPECTED RESULT abs_delta=0.2824 (tolerance 1e-3)
# EXPECTED RESULT null_delta=0 count  (outdoor 15.0 C: 6 x loss = 5.4 > 0.1)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._analyze_forecast_trajectory (line 4250
#   `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)`), called once per solve at optimizer.py:4377; its dict shapes the initial guess and is
#   published as the plan's predictive_info (solar_reduction_factor, pre_heat_urgency, ...).
# Perturbation: `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)` -> `solar_fraction = min(future_solar_6_12h / (typical_heat_loss * 6), 1.0)` (CLAMP_DROP 7f048d7823b17826), applied in memory (method recompiled from its own
#   source, called on the same optimizer instance for the mutant arm only). Direction: solar_reduction falls (fraction rises) whenever 0 < 6*loss < 0.1.
# Null control: outdoor 15.0 C.
# Inputs tried: outdoor 20.9 and 20.99 C x sun 1.0 and 0.1 W/m2; null outdoor 15.0 C.
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
mut = mutated(O, H, "_analyze_forecast_trajectory", 4250, '            solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)', '            solar_fraction = min(future_solar_6_12h / (typical_heat_loss * 6), 1.0)')
base = H._analyze_forecast_trajectory


def call(fn, sr, precip, out, dt=1.0):
    n = len(sr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(opt, np.asarray(sr, float), np.zeros(n), np.asarray(precip, float), np.asarray(out, float), dt)


def delta(case):
    b, m = call(base, **case), call(mut, **case)
    return b, m, {k: (b.get(k), m.get(k)) for k in set(b) | set(m) if repr(b.get(k)) != repr(m.get(k))}
b, m, d = delta(dict(sr=[1.0] * 24, precip=[0.0] * 24, out=[20.99] * 24))
moved = sum(int(bool(delta(dict(sr=[s] * 24, precip=[0.0] * 24, out=[t] * 24))[2])) for t in (20.9, 20.99) for s in (1.0, 0.1))
nd = len(delta(dict(sr=[1.0] * 24, precip=[0.0] * 24, out=[15.0] * 24))[2])
print(f"RESULT solar_reduction_baseline={b['solar_reduction_factor']:.4f}")
print(f"RESULT solar_reduction_mutant={m['solar_reduction_factor']:.4f}")
print(f"RESULT abs_delta={abs(b['solar_reduction_factor'] - m['solar_reduction_factor']):.4f}")
print(f"RESULT inputs_moved={moved} of 4 count")
print(f"RESULT null_delta={nd} count")
tail()
