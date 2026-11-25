#!/usr/bin/env python3
# Metric: count of inputs on which HeatPumpOptimizer._derive_hold_schedule's outcome ("None", the target array, or the
#   exception) differs between baseline and mutant, over hand-picked edge inputs (no charging step, no expensive step,
#   NaN prices, all-zero power, all-maximum power, length 1) plus 3000 seeded random (power, prices) pairs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_8ac9888c3d5fed52.py
# EXPECTED RESULT edge_differ=0 count
# EXPECTED RESULT fuzz_differ=0 count
# EXPECTED RESULT fuzz_guard_true=1113 count  (random cases where the removed guard would have fired)
# EXPECTED RESULT reach_plan_maxabs_diff_kw=0.0000 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5059 `        if not bool(expensive.any()) or not bool(charging.any()):`), caller optimizer.py:4601.
# Perturbation: line 5059 -> `        if False:` (GUARD_OFF 8ac9888c3d5fed52), in memory. Expected direction: none --
#   with no charging step after_charge is all False, with no expensive step before_peak is all False, so `hold` is
#   empty and line 5074's guard returns the same None: an equivalent mutant.
# Null control: the guard-false cases of the same fuzz (outcomes identical in both arms by construction).
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
OLD, NEW = "if not bool(expensive.any()) or not bool(charging.any()):", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
f8 = np.full(8, 19.0)
EDGE = {
    "no_charging": (np.full(8, 0.4 * pmax), np.array([0.5, 0.5, 1, 1, 1, 1, 3, 3.0]), f8),
    "nan_prices_no_expensive": (np.full(8, pmax), np.array([0.5, np.nan, 1, 1, 1, 1, 3, 3.0]), f8),
    "all_nan_prices": (np.full(8, pmax), np.full(8, np.nan), f8),
    "zero_power": (np.zeros(8), np.array([0.5, 0.5, 1, 1, 1, 1, 3, 3.0]), f8),
    "max_power_cheap_only_after_peak": (np.full(8, pmax), np.array([3, 3, 1, 1, 1, 1, 0.5, 0.5]), f8),
    "length_one": (np.array([pmax]), np.array([1.0]), np.array([19.0])),
}
rng = np.random.default_rng(11)
FUZZ = []
for _ in range(3000):
    n = int(rng.integers(2, 25))
    FUZZ.append((rng.uniform(0, pmax, n) * (rng.random(n) < rng.random()), np.round(rng.uniform(0.1, 3.0, n), 1), np.full(n, 19.0)))


def guard_fires(power, prices):
    p40, p85 = np.percentile(prices, [40, 85])
    return (not (prices >= p85).any()) or (not ((power > 0.5 * pmax) & (prices <= p40)).any())


def run_all():
    f = lambda a: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, *a))  # noqa: E731
    return {k: f(v) for k, v in EDGE.items()}, [f(c) for c in FUZZ]


import warnings  # noqa: E402
warnings.simplefilter("ignore")
eb, fb = run_all()
with mutated(NAME, OLD, NEW):
    em, fm = run_all()
print(f"RESULT edge_differ={sum(eb[k] != em[k] for k in EDGE)} count")
for k in EDGE:
    print(f"RESULT edge_{k}={eb[k]}|{em[k]}")
print(f"RESULT fuzz_differ={sum(a != b for a, b in zip(fb, fm))} count")
print(f"RESULT fuzz_guard_true={sum(bool(guard_fires(p, q)) for p, q, _ in FUZZ)} count")

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
PR = [0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4
sb, pb, ob = reach(PR, base_ctx)
sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
print(f"RESULT reach_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
footer()
