#!/usr/bin/env python3
# Metric: the energy cost HeatPumpOptimizer._energy_cost_fn prices for a fixed 24-step schedule when the PV-surplus
#   forecast's largest value is EXACTLY 1e-6 kW (the tie of the grid-only shortcut), baseline vs mutant; and through
#   optimize() with that surplus forecast, the plan's predicted cost.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a4f4c88e7480a514.py
# EXPECTED RESULT tie_cost_baseline=29.00000000
# EXPECTED RESULT tie_cost_mutant=28.99999600
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (surplus 2e-6 and 0: past the tie both arms take the same branch)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._energy_cost_fn
#   (line 4033 `        if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):`).
# Perturbation: line 4033 `> 1e-6` -> `>= 1e-6` (CMP_BOUND a4f4c88e7480a514), in memory. Direction: at a 1e-6 kW
#   surplus the piecewise PV pricing replaces the grid-only one, crediting margin * 1e-6 kW * dt per such step (a
#   ~1e-6 relative cost change).
# Null control: surplus 0 and 2e-6 kW.
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
NAME = "_energy_cost_fn"
OLD = "if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):"
NEW = "if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
    horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0, pv_export_price=0.0))
PR = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
POWER = np.full(24, 1.0)


def cost(peak):
    s = np.zeros(24)
    s[10:14] = peak
    opt._pv_surplus = s
    return float(opt._energy_cost_fn(PR, 1.0)(POWER))


def plan_cost(peak):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0, pv_export_price=0.0))
    s = np.zeros(24)
    s[10:14] = peak
    r = o.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0),
        start_time=datetime(2026, 1, 15, 0, 0),
        forecast=ForecastSeries(prices=PR, outdoor_temps=np.full(24, -5.0), pv_surplus=s)))
    return float(r.predicted_cost), np.asarray(r.power_schedule, float)


b = (cost(1e-6), cost(0.0), cost(2e-6))
pb = plan_cost(1e-6)
with mutated(NAME, OLD, NEW):
    m = (cost(1e-6), cost(0.0), cost(2e-6))
    pm = plan_cost(1e-6)
print(f"RESULT tie_cost_baseline={b[0]:.8f}")
print(f"RESULT tie_cost_mutant={m[0]:.8f}")
print(f"RESULT moved={int(b[0] != m[0])} count")
print(f"RESULT null_delta={int(b[1:] != m[1:])} count")
print(f"RESULT plan_predicted_cost_baseline={pb[0]:.8f}")
print(f"RESULT plan_predicted_cost_mutant={pm[0]:.8f}")
print(f"RESULT plan_maxabs_diff_kw={float(np.max(np.abs(pb[1] - pm[1]))):.6f} kW")
footer()
