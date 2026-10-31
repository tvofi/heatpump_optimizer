#!/usr/bin/env python3
"""D7.M6 runtime sentinel -- do the statically dead members run from production?

Metric: per instrumented class member, the number of invocations whose
IMMEDIATE caller frame is a file under custom_components/ (a production call
site), while production is driven through the five golden coordinator
scenarios (tests/golden.py:_capture_coordinator) plus one Open-Meteo-solar
scenario (om_solar; _get_json answers a canned 96 h hourly body) AND, per scenario, a full
HeatPumpOptimizerCoordinator._async_update_data cycle followed by every
platform's async_setup_entry and a read of every entity attribute Home
Assistant reads (reach.py:HA_ATTRIBUTE_SURFACE).  Count key: the production
caller frame's filename -- a fix that wires a production reader moves it, a
test read never does.

Instrumented: the nine members reach.py lists dead, one collision-kept method
(defrost.DefrostDerate.samples, alive in both static screens only because
accuracy.AccuracyTracker has a field named `samples`), and six LIVE sibling
controls on the same classes (coordinator.mode, coordinator.optimization_running,
inputs.InputHealth.stale_keys, open_meteo.IrradianceSeries.end,
defrost.DefrostDerate.factor, optimizer._Horizon.timestamps) which must count > 0, proving the drive reaches
those classes and the sentinel sees production reads.

Perturbation (in memory, `--perturb`): replace sensor.NextOptimizationSensor.
native_value with the one-line production edit
`return _as_datetime(self.coordinator.next_optimization)` -- the property then
has a production reader and its count must rise from 0 to >= 1.

Command (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D7/s3/sentinel.py [--perturb]
Expected at 1936d5ca: RESULT dead_members_called_from_production=0 count
(+-0), live_controls_called=6 of 6; with --perturb the first becomes 1.
Machine: B5 cloud container (linux).  Baseline 1936d5ca72a0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import asyncio
import contextlib
import io
import sys
import time
from collections import Counter
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D7/s3")

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()

t0, tt0 = time.process_time(), time.thread_time()

import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import defrost, inputs, open_meteo, optimizer, sensor  # noqa: E402
from heatpump_optimizer import binary_sensor, switch, climate, button, datetime as dt_plat  # noqa: E402

PROD = os.path.abspath("custom_components")
calls: Counter = Counter()
all_calls: Counter = Counter()

C = coord_mod.HeatPumpOptimizerCoordinator
DEAD = [
    (C, "last_optimization"), (C, "next_optimization"), (C, "floor_return_temp"),
    (C, "current_action"), (defrost.DefrostDerate, "measured"),
    (inputs.InputHealth, "healthy"), (open_meteo.IrradianceSeries, "start"),
    (open_meteo.OpenMeteoSolar, "last_success"), (optimizer._Horizon, "weather"),
    (defrost.DefrostDerate, "samples"),
]
LIVE = [
    (C, "mode"), (C, "optimization_running"), (inputs.InputHealth, "stale_keys"),
    (open_meteo.IrradianceSeries, "end"), (defrost.DefrostDerate, "factor"),
    (optimizer._Horizon, "timestamps"),
]


def instrument(cls, name):
    key = f"{cls.__module__.split('.')[-1]}.{cls.__name__}.{name}"
    raw = cls.__dict__[name]

    def mark():
        f = sys._getframe(2)
        all_calls[key] += 1
        if os.path.abspath(f.f_code.co_filename).startswith(PROD):
            calls[key] += 1

    if isinstance(raw, property):
        fget = raw.fget

        def g(self):
            mark()
            return fget(self)
        setattr(cls, name, property(g, raw.fset, raw.fdel, raw.__doc__))
    else:
        def w(self, *a, **k):
            mark()
            return raw(self, *a, **k)
        setattr(cls, name, w)
    return key


dead_keys = [instrument(c, n) for c, n in DEAD]
live_keys = [instrument(c, n) for c, n in LIVE]

# The solve normally crosses into a process-pool worker, where this
# instrumentation does not exist; route it through the production in-process
# fallback (coordinator.optimize_in_process, the #511 path) so the whole plan
# computation runs under the sentinels.
async def _inproc(hass, optimizer_obj, state, *positional, **keywords):
    return coord_mod.optimize_in_process(optimizer_obj, state, positional, keywords)
coord_mod._await_optimize = _inproc

if args.perturb:
    # The one-line production edit, compiled under sensor.py's own filename so
    # the new reader is a production frame exactly as the edited file would be.
    _code = (
        "def _perturbed_native_value(self):\n"
        "    return _as_datetime(self.coordinator.next_optimization)\n"
    )
    exec(compile(_code, sensor.__file__, "exec"), sensor.__dict__)
    sensor.NextOptimizationSensor.native_value = property(sensor.__dict__["_perturbed_native_value"])

SURFACE = ["available", "native_value", "extra_state_attributes", "is_on",
           "current_temperature", "target_temperature", "hvac_mode", "hvac_modes",
           "hvac_action", "preset_mode", "preset_modes", "device_info", "name",
           "unique_id", "icon", "entity_registry_enabled_default",
           "native_unit_of_measurement", "options", "state", "min_temp", "max_temp"]


async def full_cycle(config):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **config}
    entry = FakeEntry(data=cfg)
    coord = C(hass, entry)
    start = golden.START
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (start + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48)]
    coord._weather_forecast = [{"datetime": (start + timedelta(hours=h)).isoformat(),
                                "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
                                "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    prices = list(coord._prices)

    async def _prices_ok():
        # the Tibber fetch is the only network seam; it succeeds with the
        # golden prices so the cycle runs its real solve and publish path
        coord._prices = list(prices)
    coord._fetch_tibber_prices = _prices_ok
    ok = 0
    for _ in range(2):
        try:
            coord.data = await coord._async_update_data()
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"  cycle error {type(e).__name__}: {e}", file=sys.stderr)
    entry.runtime_data = coord
    ents = []
    for plat in (sensor, binary_sensor, switch, climate, button, dt_plat):
        try:
            await plat.async_setup_entry(hass, entry, lambda es, *a, **k: ents.extend(es))
        except Exception as e:  # noqa: BLE001
            print(f"  setup {plat.__name__} {type(e).__name__}: {e}", file=sys.stderr)
    reads = 0
    for e in ents:
        for a in SURFACE:
            try:
                getattr(e, a)
                reads += 1
            except Exception:  # noqa: BLE001
                pass
    return ok, len(ents), reads


# A sixth scenario selects Open-Meteo irradiance so the OpenMeteoSolar /
# IrradianceSeries members are on the drive; the one network seam
# (_get_json) answers with a canned 72 h hourly body.
_om_times = [(golden.START + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M")
             for h in range(-24, 72)]
_OM_BODY = {"hourly": {
    "time": _om_times,
    "shortwave_radiation": [max(0.0, 300.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(96)],
    "relative_humidity_2m": [85.0] * 96, "snowfall": [0.0] * 96}}


async def _om_get_json(self, session, url, params):
    return _OM_BODY
open_meteo.OpenMeteoSolar._get_json = _om_get_json
open_meteo.async_get_clientsession = lambda hass: object()

SCEN = dict(golden.coordinator_scenarios())
SCEN["om_solar"] = {**SCEN["coord_minimal"], "solar_forecast_source": "open_meteo"}

cycles = ents_n = reads_n = 0
dt_util.freeze(golden.START)
try:
    for name, cfg in SCEN.items():
        with contextlib.redirect_stdout(io.StringIO()):
            if name in golden.coordinator_scenarios():
                golden._capture_coordinator(cfg)
            ok, ne, nr = asyncio.run(full_cycle(cfg))
        cycles += ok
        ents_n += ne
        reads_n += nr
finally:
    dt_util.freeze(None)

for k in dead_keys + live_keys:
    tag = "dead" if k in dead_keys else "live"
    print(f"SENTINEL {tag} {k}: production_calls={calls[k]} all_calls={all_calls[k]}")
print(f"RESULT scenarios={len(SCEN)} count")
print(f"RESULT update_cycles_completed={cycles} count")
print(f"RESULT entities_read={ents_n} count")
print(f"RESULT entity_attribute_reads={reads_n} count")
print(f"RESULT dead_members_called_from_production={sum(1 for k in dead_keys if calls[k])} count")
print(f"RESULT dead_member_production_calls_total={sum(calls[k] for k in dead_keys)} count")
print(f"RESULT live_controls_called={sum(1 for k in live_keys if calls[k])} of {len(live_keys)}")
cpu, th = time.process_time() - t0, time.thread_time() - tt0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
