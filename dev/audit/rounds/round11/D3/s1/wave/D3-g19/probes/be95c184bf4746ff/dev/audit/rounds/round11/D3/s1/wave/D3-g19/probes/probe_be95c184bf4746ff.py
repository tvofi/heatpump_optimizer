#!/usr/bin/env python3
# Metric: pre_heat_urgency HeatPumpOptimizer._analyze_forecast_trajectory returns for an EMPTY forecast (n = 0).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_be95c184bf4746ff.py
# EXPECTED RESULT pre_heat_urgency_baseline=0.5
# EXPECTED RESULT pre_heat_urgency_mutant=0.0  (the empty-weight sums are 0, so urgency clamps to 0)
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT extra_keys_mutant=3 count  (avg_future_wind_ms, avg_future_precip_mmh, future_solar_6_12h_kwh appear)
# EXPECTED RESULT null_delta=0 count  (a non-empty 24-step forecast)
# EXPECTED RESULT reach_optimize_empty: whether optimize() reaches the method with n=0 (no; see the reach line)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._analyze_forecast_trajectory (line 4211
#   `if n == 0:`), called once per solve at optimizer.py:4377; its dict shapes the initial guess and is
#   published as the plan's predictive_info (solar_reduction_factor, pre_heat_urgency, ...).
# Perturbation: `if n == 0:` -> `if False:` (GUARD_OFF be95c184bf4746ff), applied in memory (method recompiled from its own
#   source, called on the same optimizer instance for the mutant arm only). Direction: pre_heat_urgency 0.5 -> 0.0 for n = 0.
# Null control: a 24-step forecast (sun 300 W/m2, rain 0.5 mm/h).
# Inputs tried: n=0 (all six summary keys compared); the 24-step null; optimize() with horizon_hours=0 and 0.1 for reach.
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
mut = mutated(O, H, "_analyze_forecast_trajectory", 4211, '        if n == 0:', '        if False:')
base = H._analyze_forecast_trajectory


def call(fn, sr, precip, out, dt=1.0):
    n = len(sr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(opt, np.asarray(sr, float), np.zeros(n), np.asarray(precip, float), np.asarray(out, float), dt)


def delta(case):
    b, m = call(base, **case), call(mut, **case)
    return b, m, {k: (b.get(k), m.get(k)) for k in set(b) | set(m) if repr(b.get(k)) != repr(m.get(k))}
b, m, d = delta(dict(sr=[], precip=[], out=[]))
nb, nm, nd = delta(dict(sr=[300.0] * 24, precip=[0.5] * 24, out=[0.0] * 24))
print(f"RESULT pre_heat_urgency_baseline={b['pre_heat_urgency']}")
print(f"RESULT pre_heat_urgency_mutant={m['pre_heat_urgency']}")
print(f"RESULT moved={int(b['pre_heat_urgency'] != m['pre_heat_urgency'])} count")
print(f"RESULT extra_keys_mutant={len(set(m) - set(b))} count")
print(f"RESULT null_delta={len(nd)} count")
reached = []
real = H._analyze_forecast_trajectory


def spy(self, sr, *a):
    reached.append(len(sr))
    return real(self, sr, *a)


from datetime import datetime  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalState  # noqa: E402
for hh in (0, 0.1):
    try:
        o2 = H(ThermalModel(ThermalParameters()), O.OptimizationConfig(horizon_hours=hh, time_step_minutes=60,
               target_temp=21.0, min_temp=19.0, max_temp=23.0))
        with mock.patch.object(H, "_analyze_forecast_trajectory", spy), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            o2.optimize(inputs=O.SolveInputs(state=ThermalState(room_temperature=21.0, slab_temperature=22.0,
                        outdoor_temperature=0.0), start_time=datetime(2026, 1, 15, 12, 0),
                        forecast=O.ForecastSeries(prices=np.full(1, 1.0), outdoor_temps=np.full(1, 0.0))))
        print(f"RESULT reach_optimize_horizon_{hh}=ran n_seen={reached[-1] if reached else None}")
    except Exception as exc:
        print(f"RESULT reach_optimize_horizon_{hh}={type(exc).__name__} n_seen={reached[-1] if reached else None}")
print(f"RESULT reach_optimize_empty={int(0 in reached)} count")
tail()
