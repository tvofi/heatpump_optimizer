#!/usr/bin/env python3
# Metric: count of hours listed in predictive_info.dhw_planned_heating_hours (published by sensor.py:1248/1350), from a hot-water optimize() under a fuse-guard ceiling whose minimum is 0.1 kW (every planned DHW
#   step then sits at exactly the 0.1 kW planning floor), baseline vs mutant; plus the count of planned steps at 0.1.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_4e5a67b907d13871.py
# EXPECTED RESULT dhw_planned_heating_hours_baseline=0
# EXPECTED RESULT dhw_planned_heating_hours_mutant=22
# EXPECTED RESULT null_delta=0 count  (no fuse cap: DHW steps at >= 0.6 kW, both arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_with_dhw
#   (line 5956 `for idx in np.where(optimal_dhw > 0.1)[0][:48].tolist()`).
# Perturbation: line 5956 `> 0.1` -> `>= 0.1` (CMP_BOUND 4e5a67b907d13871), in memory. Direction: the planned 0.1 kW DHW
#   steps, excluded on the baseline, are counted under the mutant.
# Null control: the same solve without the fuse cap (no DHW step at exactly 0.1 kW).
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

# The production seam: a fuse-guard ceiling (SolveLimits.power_caps_extra) whose horizon minimum is at or under
# 0.1 kW makes dhw_planner.py:1138-1141 plan every hot-water step at exactly the 0.1 kW planning floor.
import logging  # noqa: E402


def dhw_cap_solve(cap_min, hour=0, dhw_temp=42.0):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    caps = np.full(24, 6.0)
    caps[20] = cap_min
    logged = []

    class _H(logging.Handler):
        def emit(self, rec):
            if rec.msg.startswith("DHW+Space optimization completed"):
                logged.append(int(rec.args[3]))
    h = _H()
    optimizer._LOGGER.addHandler(h)
    old_level = optimizer._LOGGER.level
    optimizer._LOGGER.setLevel(logging.INFO)
    try:
        r = o.optimize(inputs=SolveInputs(
            state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=5.0,
                               dhw_temperature=dhw_temp),
            start_time=datetime(2026, 1, 15, hour, 0),
            forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(24, 5.0)),
            limits=SolveLimits(power_caps_extra=caps)))
    finally:
        optimizer._LOGGER.removeHandler(h)
        optimizer._LOGGER.setLevel(old_level)
    d = np.asarray(r.dhw_power_schedule, float)
    return r, d, (logged[-1] if logged else None)
NAME = "_optimize_with_dhw"
OLD = "for idx in np.where(optimal_dhw > 0.1)[0][:48].tolist()"
NEW = "for idx in np.where(optimal_dhw >= 0.1)[0][:48].tolist()"


def metric(cap):
    r, d, logged = dhw_cap_solve(cap)
    return len(r.predictive_info['dhw_planned_heating_hours']), int(np.sum(d == 0.1)), r


vb, n01, rb = metric(0.1)
nb = metric(6.0)
with mutated(NAME, OLD, NEW):
    vm, _, rm = metric(0.1)
    nm = metric(6.0)
print(f"RESULT dhw_steps_at_0p1={n01} count")
print(f"RESULT dhw_planned_heating_hours_baseline={vb}")
print(f"RESULT dhw_planned_heating_hours_mutant={vm}")
print(f"RESULT null_delta={int(nb[0] != nm[0])} count")
print(f"RESULT plan_dhw_maxabs_diff_kw={float(np.max(np.abs(np.asarray(rb.dhw_power_schedule) - np.asarray(rm.dhw_power_schedule)))):.4f} kW")
footer()
