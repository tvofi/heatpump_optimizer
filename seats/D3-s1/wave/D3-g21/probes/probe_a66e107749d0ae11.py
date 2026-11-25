#!/usr/bin/env python3
# Metric: predictive_info["dhw_required_temperature_now"] (C) from a hot-water optimize() at a start hour inside the
#   default morning demand window, baseline vs mutant, scanned over all 24 start hours (count of hours that differ).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a66e107749d0ae11.py
# EXPECTED RESULT required_now_baseline=55.0 C
# EXPECTED RESULT required_now_mutant=20.0 C
# EXPECTED RESULT hours_differ=4 count  (of 24 start hours)
# EXPECTED RESULT null_delta=0 count  (hours outside every window: ready[0] <= floor[0], both arms equal)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_with_dhw
#   (line 5945 `                    float(max(dhw_floor_temps[0], dhw_ready_temps[0]))`), published as
#   predictive_info.dhw_required_temperature_now.
# Perturbation: line 5945 -> `                    float((dhw_floor_temps[0]))` (CLAMP_DROP a66e107749d0ae11), in memory.
#   Direction: inside a demand window the published required temperature falls from the ready target to the floor.
# Null control: start hours where ready[0] <= floor[0] (outside the windows): identical.
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
NAME = "_optimize_with_dhw"
OLD = "float(max(dhw_floor_temps[0], dhw_ready_temps[0]))"
NEW = "float((dhw_floor_temps[0]))"


def required(hour):
    o = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
        horizon_hours=24, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.array([0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4)
    r = o.optimize(inputs=SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0, dhw_temperature=50.0),
        start_time=datetime(2026, 1, 15, hour, 0), forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(24, -5.0))))
    return float(r.predictive_info["dhw_required_temperature_now"])


HOURS = range(24)
b = {h: required(h) for h in HOURS}
with mutated(NAME, OLD, NEW):
    m = {h: required(h) for h in HOURS}
diff = [h for h in HOURS if b[h] != m[h]]
first = diff[0] if diff else 0
print(f"RESULT first_differing_hour={first}")
print(f"RESULT required_now_baseline={b[first]} C")
print(f"RESULT required_now_mutant={m[first]} C")
print(f"RESULT hours_differ={len(diff)} count")
print(f"RESULT differing_hours={','.join(map(str, diff))}")
print(f"RESULT null_delta={sum(b[h] != m[h] for h in HOURS if h not in diff)} count")
footer()
