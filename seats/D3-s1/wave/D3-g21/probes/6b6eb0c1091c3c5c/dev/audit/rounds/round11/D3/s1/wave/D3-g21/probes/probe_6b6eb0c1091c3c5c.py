#!/usr/bin/env python3
# Metric: HeatPumpOptimizer._pin_on_power(upper) with upper below the floor, baseline vs mutant; and the solver bounds
#   _apply_pins_to_bounds builds from it plus the planned power on pinned-ON steps through optimize(), for a pump whose
#   minimum power exceeds the per-step ceiling (min 1.0 kW, power caps 0.5 kW from a fuse limit) and for min > max.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6b6eb0c1091c3c5c.py
# EXPECTED RESULT direct_baseline=0.5 kW
# EXPECTED RESULT direct_mutant=1.0 kW
# EXPECTED RESULT bounds_differ=0 count
# EXPECTED RESULT plan_maxabs_diff_kw=0.0000 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._pin_on_power
#   (line 5284 `        return min(floor, upper)`); every production caller passes upper=p_max (optimizer.py:597, 5492)
#   and _apply_pins_to_bounds (optimizer.py:2418) clamps the result again to each step's own upper bound.
# Perturbation: line 5284 -> `        return (floor)` (CLAMP_DROP 6b6eb0c1091c3c5c), in memory. Expected direction: none at
#   the bounds -- `min(min_on_power, high)` with high <= p_max re-applies the dropped clamp: an equivalent mutant.
# Null control: min power below the ceiling (the clamp is inactive in both arms).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, resource
from datetime import datetime, timedelta
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, SolveInputs, ForecastSeries, SolveLimits)
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_P0, _T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """HeatPumpOptimizer.<name> recompiled from its own source with the one line swapped."""
    raw = inspect.getattr_static(HeatPumpOptimizer, name)
    fn = raw.__func__ if isinstance(raw, staticmethod) else raw
    src = textwrap.dedent(inspect.getsource(fn))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = {}
    # globals = the live module dict, so a collaborator patched on the module is seen by both arms alike
    exec(compile(src.replace(old, new, 1), optimizer.__file__, "exec"), optimizer.__dict__, ns)
    out = ns[name]
    if isinstance(raw, staticmethod) and not isinstance(out, staticmethod):
        out = staticmethod(out)
    return out


def mutated(name, old, new):
    """Context manager: the class attribute swapped to the mutant for the block."""
    return mock.patch.object(HeatPumpOptimizer, name, mutant_method(name, old, new))


def outcome(fn, *a, **k):
    try:
        r = fn(*a, **k)
    except Exception as exc:  # the mutant's failure is the number
        return f"raise:{type(exc).__name__}"
    if r is None:
        return "None"
    if isinstance(r, np.ndarray):
        return "array:" + ",".join(f"{v:g}" for v in r.tolist())
    return repr(r)


def footer():
    p, t = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
NAME = "_pin_on_power"
OLD, NEW = "return min(floor, upper)", "return (floor)"
PR = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
PINS = np.full(24, np.nan)
PINS[16:20] = 1.0
PINS[2:4] = 0.0


def mk(min_kw, max_kw=5.0):
    return HeatPumpOptimizer(ThermalModel(ThermalParameters(min_electrical_power=min_kw, max_electrical_power=max_kw)),
                             OptimizationConfig(horizon_hours=24, time_step_minutes=60, target_temp=21.0,
                                                min_temp=19.0, max_temp=23.0))


def plan(min_kw, max_kw, caps):
    o = mk(min_kw, max_kw)
    seen = []
    real = optimizer._apply_pins_to_bounds

    def spy(bounds, pins, mop):
        out = real(bounds, pins, mop)
        seen.append(tuple(out))
        return out
    with mock.patch.object(optimizer, "_apply_pins_to_bounds", spy):
        r = o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
            start_time=datetime(2026, 1, 15, 0, 0), forecast=ForecastSeries(prices=PR, outdoor_temps=np.full(24, -5.0)),
            limits=SolveLimits(space_pins=PINS, power_caps_extra=caps)))
    return seen, np.asarray(r.power_schedule, float)


CASES = {"caps_below_min": (1.0, 5.0, np.full(24, 0.5)), "min_above_max": (6.0, 5.0, None), "null": (1.0, 5.0, None)}
b = (mk(1.0)._pin_on_power(0.5), {k: plan(*v) for k, v in CASES.items()})
with mutated(NAME, OLD, NEW):
    m = (mk(1.0)._pin_on_power(0.5), {k: plan(*v) for k, v in CASES.items()})
print(f"RESULT direct_baseline={b[0]} kW")
print(f"RESULT direct_mutant={m[0]} kW")
print(f"RESULT bounds_differ={sum(int(b[1][k][0] != m[1][k][0]) for k in CASES)} count")
print(f"RESULT plan_maxabs_diff_kw={max(float(np.max(np.abs(b[1][k][1] - m[1][k][1]))) for k in CASES):.4f} kW")
print(f"RESULT bounds_calls={sum(len(b[1][k][0]) for k in CASES)} count")
footer()
