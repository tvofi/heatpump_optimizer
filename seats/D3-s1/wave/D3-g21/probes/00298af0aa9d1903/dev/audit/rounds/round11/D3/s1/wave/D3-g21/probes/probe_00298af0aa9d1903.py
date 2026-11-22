#!/usr/bin/env python3
# Metric: what HeatPumpOptimizer._derive_hold_schedule returns when charging and an expensive block both exist but no
#   step lies between them ("None" or the target array), baseline vs mutant; then through optimize() (smart-write
#   valve, 500 L store, -15 C) the count of proposed schedules (each one a full re-solve), the plan's max |power|
#   difference and the solve CPU.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_00298af0aa9d1903.py
# EXPECTED RESULT nohold_baseline=None
# EXPECTED RESULT nohold_mutant=array:23,23,23,23,23,23,23,23
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (a profile with hold steps: both arms return the same schedule)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5074 `        if not bool(hold.any()):`), caller optimizer.py:4601.
# Perturbation: line 5074 -> `        if False:` (GUARD_OFF 00298af0aa9d1903), in memory. Direction: None -> an all-default
#   target array (no hold step), which the caller re-solves in full and then discards (same objective, not < -1e-9).
# Null control: an input with hold steps (the guard is false in both arms).
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
NAME = "_derive_hold_schedule"
OLD, NEW = "if not bool(hold.any()):", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
f8 = np.full(8, 19.0)
adjacent = (np.array([pmax] * 5 + [0.0] * 3), np.array([0.5] * 5 + [3.0] * 3), f8)     # charge right up to the peak
with_hold = (np.array([pmax, pmax, 0.5, 0.5, 0.5, 0, 0, 0]), np.array([0.5, 0.5, 1, 1, 1, 3, 3, 3.0]), f8)
call = lambda a: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, *a))  # noqa: E731
b, bn = call(adjacent), call(with_hold)
with mutated(NAME, OLD, NEW):
    m, mn = call(adjacent), call(with_hold)
print(f"RESULT nohold_baseline={b}")
print(f"RESULT nohold_mutant={m}")
print(f"RESULT moved={int(b != m)} count")
print(f"RESULT null_delta={int(bn != mn)} count")

# Reach: optimize() with the valve in smart_write and a 500 L store buffer, the one production caller
# (optimizer.py:4601), on the price profile PR; spy counts the schedules the derivation proposes.
from custom_components.heatpump_optimizer import mixing_valve  # noqa: E402


def reach(prices, arm_ctx, outdoor=-15.0):
    seen = {"calls": 0, "proposed": 0}
    inner = HeatPumpOptimizer._derive_hold_schedule

    def spy(self, power, pr, floors):
        r = inner(self, power, pr, floors)
        seen["calls"] += 1
        seen["proposed"] += int(r is not None)
        return r
    params = ThermalParameters(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE, buffer_tank_volume=500.0)
    o = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=len(prices), time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    c0 = time.thread_time()
    with arm_ctx():
        inner = HeatPumpOptimizer._derive_hold_schedule
        with mock.patch.object(HeatPumpOptimizer, "_derive_hold_schedule", spy):
            r = o.optimize(inputs=SolveInputs(
                state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=outdoor),
                start_time=datetime(2026, 1, 15, 0, 0),
                forecast=ForecastSeries(prices=np.asarray(prices, float), outdoor_temps=np.full(len(prices), outdoor))))
    seen["cpu_s"] = time.thread_time() - c0
    return seen, np.asarray(r.power_schedule, float), float(r.objective_value)


def base_ctx():
    return mock.patch.object(HeatPumpOptimizer, "__doc__", HeatPumpOptimizer.__doc__)
PROFILES = {"two_level_16_8": [1.0] * 16 + [1.2] * 8, "cheap_then_peak_12_12": [0.5] * 12 + [3.0] * 12}
for tag, PR in PROFILES.items():
    sb, pb, ob = reach(PR, base_ctx)
    sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
    print(f"RESULT reach_{tag}_proposed_baseline={sb['proposed']} count")
    print(f"RESULT reach_{tag}_proposed_mutant={sm['proposed']} count")
    print(f"RESULT reach_{tag}_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
    print(f"RESULT reach_{tag}_objective_delta={om - ob:.6f}")
    print(f"RESULT reach_{tag}_cpu_baseline_s={sb['cpu_s']:.2f} s (provisional)")
    print(f"RESULT reach_{tag}_cpu_mutant_s={sm['cpu_s']:.2f} s (provisional)")
footer()
