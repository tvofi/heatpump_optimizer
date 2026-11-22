#!/usr/bin/env python3
# Metric: _external_heat_forecast's return (None or array) for a suppressing detector whose free heat is 0, and what optimizer._horizon_weather hands the solve from it (ForecastSeries.external_heat_kw).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_c39bf88e7fd0066f.py
# Expected: moved_at_symbol=2 (None -> zeros[96]) and moved_at_solve_input=0 (optimizer.py:3049 maps all-zero to None in both arms); tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._external_heat_forecast (line 5259 return) and optimizer:_horizon_weather (optimizer.py:3046-3050).
# Perturbation: `np.any(arr > 0.0)` -> `np.any(arr >= 0.0)` (mutant c39bf88e7fd0066f), applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: the solve-input arm: the same two states read through _horizon_weather, where the effect must vanish.
# Count key: the value the production method returns or files (never an input attribute). Writes nothing.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
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
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """The coordinator method recompiled from its own source with the one-line mutant, in memory."""
    src = textwrap.dedent(inspect.getsource(getattr(CLS, name)))
    assert src.count(old) == 1, f"anchor {old!r} not unique in {name}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def coord(states=None, **extra):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **extra}
    return CLS(FakeHass(dict(states or {})), FakeEntry(data=cfg))


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")


import numpy as np
from custom_components.heatpump_optimizer import optimizer as opt
from custom_components.heatpump_optimizer.external_heat import ExternalHeatObservation
OLD, NEW = "return arr if bool(np.any(arr > 0.0)) else None", "return arr if bool(np.any(arr >= 0.0)) else None"
MUT = mutant_method("_external_heat_forecast", OLD, NEW)
T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def suppressing_coord(**kw):
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    o = dict(now=T0, dhw_temp=None, buffer_temp=None, commanded_power_kw=0.0, measured_power_kw=0.0,
             override=True, outlet_temp=None, wood_top=None, wood_bottom=None, hp_tank_temp=None, space_demand_kw=5.0)
    o.update(kw)
    c._external_heat.update(ExternalHeatObservation(**o))
    return c


def horizon(arr, n=96):
    """optimizer._horizon_weather, the solve's one reader of ForecastSeries.external_heat_kw."""
    s = opt.ForecastSeries(prices=np.ones(n), outdoor_temps=np.zeros(n), wind_speeds=np.zeros(n),
                           precipitation=np.zeros(n), solar_radiation=np.zeros(n), external_heat_kw=arr)
    return opt._horizon_weather(s, n).external_heat_kw


cases = {
    # the user's flag says a fire burns, no outlet/wood probes: suppressing, displacement 0, free heat 0
    "override_on_no_wood_probes": suppressing_coord(),
    # probes present but wood side below the pump tank + margin: displacement 0
    "override_on_cold_wood_tank": suppressing_coord(outlet_temp=40.0, wood_top=41.0, wood_bottom=40.0, hp_tank_temp=40.0),
}
moved_symbol = moved_solve = 0
for name, c in cases.items():
    b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
    hb, hm = horizon(b), horizon(m)
    moved_symbol += int((b is None) != (m is None))
    moved_solve += int((hb is None) != (hm is None) or (hb is not None and not np.array_equal(hb, hm)))
    print(f"RESULT {name} suppressing={c._external_heat.suppressing} free_heat_kw={c._external_heat.state.free_heat_kw} "
          f"symbol_baseline={'None' if b is None else 'array'} symbol_mutant={'None' if m is None else 'zeros[%d]' % len(m)} "
          f"solve_input_baseline={hb} solve_input_mutant={hm}")
print(f"RESULT reach=line_5259_executed_by_this_probe count")
print(f"RESULT moved_at_symbol={moved_symbol} count")
print(f"RESULT moved_at_solve_input={moved_solve} count")
tail()
