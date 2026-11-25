#!/usr/bin/env python3
# Metric: what HeatPumpOptimizer._normalise_pins returns (the padded array, or the exception) for a pin array SHORTER
#   than the horizon, baseline vs mutant; the same through optimize(space_pins=short); and, as the reach arm, the
#   plan's max |power| difference when the pins are as long as the price array the coordinator sizes them from
#   (coordinator.py:6289 `_manual_pins(solve_now, len(horizon.prices))`), including a shorter weather series.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_be3a3a75280c7b7e.py
# EXPECTED RESULT short_baseline=array:1,0,nan,nan
# EXPECTED RESULT short_mutant=raise:ValueError
# EXPECTED RESULT optimize_short_pins_baseline=ok
# EXPECTED RESULT optimize_short_pins_mutant=raise:ValueError
# EXPECTED RESULT null_delta=0 count  (pins as long as or longer than the horizon: identical arrays)
# EXPECTED RESULT reach_plan_maxabs_diff_kw=0.0000 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._normalise_pins
#   (line 5016 `        take = min(n_steps, src.size)`), callers optimizer.py:4432-4433 in optimize().
# Perturbation: line 5016 -> `        take = (n_steps)` (CLAMP_DROP be3a3a75280c7b7e), in memory. Direction: NaN padding
#   -> ValueError (broadcast of a shorter source into n_steps slots) for a short pin array.
# Null control: pins of horizon length and longer (both arms identical).
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
NAME = "_normalise_pins"
OLD, NEW = "take = min(n_steps, src.size)", "take = (n_steps)"
f = lambda *a: outcome(lambda: HeatPumpOptimizer._normalise_pins(*a))  # noqa: E731
short, exact, longer = np.array([1.0, 0.0]), np.array([1.0, 0.0, np.nan, 1.0]), np.array([1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
b = (f(short, 4), f(exact, 4), f(longer, 4))
with mutated(NAME, OLD, NEW):
    m = (f(short, 4), f(exact, 4), f(longer, 4))
print(f"RESULT short_baseline={b[0]}")
print(f"RESULT short_mutant={m[0]}")
print(f"RESULT null_delta={int(b[1:] != m[1:])} count")


def solve(pins, n_out=24):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    r = o.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
        start_time=datetime(2026, 1, 15, 0, 0),
        forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(n_out, -5.0)), limits=SolveLimits(space_pins=pins)))
    return np.asarray(r.power_schedule, float)


short24 = np.array([1.0, 1.0, 0.0])
full24 = np.full(24, np.nan)
full24[:3] = [1.0, 1.0, 0.0]
ob = outcome(lambda: solve(short24))
pb, pb2 = solve(full24), solve(full24, n_out=20)
with mutated(NAME, OLD, NEW):
    om = outcome(lambda: solve(short24))
    pm, pm2 = solve(full24), solve(full24, n_out=20)
print(f"RESULT optimize_short_pins_baseline={'ok' if ob.startswith('array') else ob}")
print(f"RESULT optimize_short_pins_mutant={'ok' if om.startswith('array') else om}")
print(f"RESULT reach_plan_maxabs_diff_kw={max(float(np.max(np.abs(pb - pm))), float(np.max(np.abs(pb2 - pm2)))):.4f} kW")
footer()
