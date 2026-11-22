#!/usr/bin/env python3
# Metric: one _fetch_weather_forecast with no weather entity configured: (weather service calls made, held forecast rows, outage cycles, warning text).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_d05457b7adf4d691.py
# Expected: calls 0 -> 1 (weather.get_forecasts called with entity_id None) and warning 'No weather entity configured' -> 'No forecast data returned for None'; tolerance exact (counts and values, no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fetch_weather_forecast (line 7056 `if not weather_entity:`).
# Perturbation: `if not weather_entity:` -> `if False:` (mutant d05457b7adf4d691), applied in memory: the method is recompiled from its own source with the one
#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.
# Null control: weather entity configured, empty forecast: identical in both arms.
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

WE = "weather.home"


def fetch(fn, weather_entity, response, held=None):
    """One _fetch_weather_forecast; (service calls, held forecast rows, outage cycles, warning texts)."""
    c = coord({WE: FakeState("-5.0", attributes={"temperature": -5.0, "temperature_unit": "°C"})},
              weather_entity=weather_entity)
    if response is not ...:
        async def handler(call):
            return response
        c.hass.services.async_register("weather", "get_forecasts", handler)
    c._weather_forecast = list(held or [])
    warns = []
    with mock.patch.object(co._LOGGER, "warning", lambda *a, **k: warns.append(a[1] if len(a) > 1 else a[0])):
        asyncio.run(fn(c))
    return len(c.hass.services.calls), len(c._weather_forecast), c._weather_outage_cycles, warns


OLD, NEW = "if not weather_entity:", "if False:"
MUT = mutant_method("_fetch_weather_forecast", OLD, NEW)
moved = 0
for name, ent, resp in (("unset_empty", "", ...), ("unset_none", None, ...), ("unset_with_service", "", {})):
    b, m = fetch(CLS._fetch_weather_forecast, ent, resp), fetch(MUT, ent, resp)
    moved += int(b != m)
    print(f"RESULT {name} baseline(calls,rows,outages,warn)={b} mutant={m}")
nb = fetch(CLS._fetch_weather_forecast, WE, {WE: {"forecast": []}})
nm = fetch(MUT, WE, {WE: {"forecast": []}})
print(f"RESULT null_configured baseline={nb} mutant={nm}")
print(f"RESULT moved_cases={moved} count")
tail()
