#!/usr/bin/env python3
"""D8-s1-01 harness: the non-finite scrub sensor.py installs on every
`HeatPumpOptimizerSensorBase` subclass (`__init_subclass__`, sensor.py:327)
is not installed anywhere in climate.py, switch.py, binary_sensor.py or
datetime.py. A NaN/Inf that reaches `coordinator.data` under a key those
platforms read straight through `extra_state_attributes`/`is_on` (no
`_finite()` call exists outside sensor.py -- `grep -c _finite
custom_components/heatpump_optimizer/{climate,switch,binary_sensor,datetime}.py`
is 0,0,0,0) is published unscrubbed, while the identical value reaching the
identically-named sensor field is silently nulled.

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round8/D8/s1_finite_boundary.py

Metric definition: `climate_leaks_nonfinite` = 1 iff
ClimateEntity.extra_state_attributes()["current_price"] is a non-finite
float (fails `orjson.dumps`) after `coordinator.data["current_price"]` is
set to `float("nan")`; `sensor_scrubs_same_key` = 1 iff
CurrentPriceSensor.native_value is `None` (not NaN) under the identical
`coordinator.data`. Both read the same dict key off the same coordinator
object -- the only thing that differs is which platform's base class the
entity subclasses.

Instrumented symbols: heatpump_optimizer.climate:HeatPumpOptimizerClimate
.extra_state_attributes (or whichever climate entity class is constructed --
printed below), heatpump_optimizer.sensor:CurrentPriceSensor.native_value.

Perturbation: coordinator.data["current_price"] is set from a finite float
to float("nan") (expected direction: sensor_scrubs_same_key becomes/stays 1,
climate_leaks_nonfinite becomes/stays 1) and then to float("inf") (same
expected direction). The null control is the unperturbed run with a finite
current_price, where both must read the plain finite number back
unmangled -- printed as `RESULT null_control_ok=1`.

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82. Counts only, final
(not provisional) -- no timing or memory numbers are reported here.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import math
import sys
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import harness  # noqa: E402
import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor, climate  # noqa: E402

try:
    import orjson

    def _orjson_ok(value) -> bool:
        try:
            orjson.dumps(value)
            return True
        except Exception:
            return False
except ImportError:
    def _orjson_ok(value) -> bool:
        if isinstance(value, float):
            return math.isfinite(value)
        if isinstance(value, dict):
            return all(_orjson_ok(v) for v in value.values())
        return True


START = golden.START
CONFIG = golden.coordinator_scenarios()["coord_minimal"]


def build():
    hass = FakeHass()
    entry = FakeEntry(data=CONFIG)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {"total": 0.7, "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(), "temperature": 2.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0 for _ in range(48)]
    coord._forecast_arrays()
    data = coord._build_data_dict()
    coord.data = data
    return hass, entry, coord


def collect(module, hass, entry):
    added = []

    def add_entities(es):
        added.extend(es)

    asyncio.run(module.async_setup_entry(hass, entry, add_entities))
    return added


def find_price_sensor(added):
    for ent in added:
        if type(ent).__name__ == "CurrentPriceSensor":
            return ent
    return None


def find_climate(added):
    return added[0] if added else None


dt_util.freeze(START)
try:
    hass, entry, coord = build()
    entry.runtime_data = coord

    climate_entities = collect(climate, hass, entry)
    sensor_entities = collect(sensor, hass, entry)
    price_sensor = find_price_sensor(sensor_entities)
    climate_ent = find_climate(climate_entities)
    assert price_sensor is not None, "CurrentPriceSensor not constructed"
    assert climate_ent is not None, "no climate entity constructed"
    print(f"RESULT climate_class={type(climate_ent).__name__} name")

    # ---- null control: finite value, unperturbed ----
    coord.data["current_price"] = 0.73
    null_climate = climate_ent.extra_state_attributes.get("current_price")
    null_sensor = price_sensor.native_value
    null_ok = (null_climate == 0.73) and (null_sensor == 0.73)
    print(f"RESULT null_control_ok={int(null_ok)} bool  climate={null_climate!r} sensor={null_sensor!r}")

    results = {}
    for label, bad in (("nan", float("nan")), ("inf", float("inf"))):
        coord.data["current_price"] = bad
        climate_val = climate_ent.extra_state_attributes.get("current_price")
        sensor_val = price_sensor.native_value

        climate_leaks = not _orjson_ok(climate_val)
        sensor_scrubs = sensor_val is None
        results[label] = (climate_leaks, sensor_scrubs, climate_val, sensor_val)
        print(
            f"RESULT climate_leaks_nonfinite_{label}={int(climate_leaks)} bool "
            f"value={climate_val!r}"
        )
        print(
            f"RESULT sensor_scrubs_same_key_{label}={int(sensor_scrubs)} bool "
            f"value={sensor_val!r}"
        )

    for platform_name, path in (
        ("climate", "custom_components/heatpump_optimizer/climate.py"),
        ("switch", "custom_components/heatpump_optimizer/switch.py"),
        ("binary_sensor", "custom_components/heatpump_optimizer/binary_sensor.py"),
        ("datetime", "custom_components/heatpump_optimizer/datetime.py"),
        ("sensor", "custom_components/heatpump_optimizer/sensor.py"),
    ):
        text = open(path).read()
        print(f"RESULT {platform_name}_finite_call_count={text.count('_finite(')} count")

finally:
    dt_util.freeze(None)

all_leak = all(results[l][0] for l in ("nan", "inf"))
all_scrub = all(results[l][1] for l in ("nan", "inf"))
print(f"RESULT overall_asymmetry_confirmed={int(all_leak and all_scrub)} bool")
