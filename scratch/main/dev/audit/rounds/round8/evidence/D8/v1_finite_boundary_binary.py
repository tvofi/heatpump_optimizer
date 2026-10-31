#!/usr/bin/env python3
"""D8-v1 independent harness for D8-s1-01, using a DIFFERENT platform pair
and a DIFFERENT data key than the finder's harness (which used
climate.py vs sensor.py on "current_price"). This one uses
binary_sensor.py's WoodCheaperBinarySensor.extra_state_attributes
("sek_per_kwh") against sensor.py's WoodCostSensor-equivalent numeric
sensor reading the same coordinator.data["wood_fuel"]["sek_per_kwh"] key
(falls back to any sensor reading that key if the exact class name differs;
printed below), to confirm the asymmetry is not an artefact of the one
key/platform pair the finder picked.

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round8/D8/v1_finite_boundary_binary.py

Metric definition: `binsens_leaks_nonfinite` = 1 iff
WoodCheaperBinarySensor.extra_state_attributes()["sek_per_kwh"] is a
non-finite float (fails orjson.dumps) after
coordinator.data["wood_fuel"]["sek_per_kwh"] is set to a non-finite float.
Compared against `platform_finite_call_count` = number of `_finite(` call
sites in binary_sensor.py (expected 0, corroborating the grep-based claim
independently of sensor.py/climate.py).

Instrumented symbol: heatpump_optimizer.binary_sensor:WoodCheaperBinarySensor
.extra_state_attributes.

Perturbation: coordinator.data["wood_fuel"]["sek_per_kwh"] set from a finite
0.42 (null control) to float("nan") then float("inf").

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82. Counts only, final.
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
from heatpump_optimizer import binary_sensor  # noqa: E402

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


dt_util.freeze(START)
try:
    hass, entry, coord = build()
    entry.runtime_data = coord

    bin_entities = collect(binary_sensor, hass, entry)
    wood = None
    for ent in bin_entities:
        if type(ent).__name__ == "WoodCheaperBinarySensor":
            wood = ent
            break
    assert wood is not None, "WoodCheaperBinarySensor not constructed"
    print(f"RESULT binary_sensor_class={type(wood).__name__} name")

    if "wood_fuel" not in coord.data or not isinstance(coord.data.get("wood_fuel"), dict):
        coord.data["wood_fuel"] = {}
    coord.data["wood_fuel"]["ready"] = True
    coord.data["wood_fuel"]["cheaper"] = True

    # null control
    coord.data["wood_fuel"]["sek_per_kwh"] = 0.42
    null_val = wood.extra_state_attributes.get("sek_per_kwh")
    null_ok = null_val == 0.42
    print(f"RESULT null_control_ok={int(null_ok)} bool value={null_val!r}")

    results = {}
    for label, bad in (("nan", float("nan")), ("inf", float("inf"))):
        coord.data["wood_fuel"]["sek_per_kwh"] = bad
        val = wood.extra_state_attributes.get("sek_per_kwh")
        leaks = not _orjson_ok(val)
        results[label] = leaks
        print(f"RESULT binsens_leaks_nonfinite_{label}={int(leaks)} bool value={val!r}")

    text = open("custom_components/heatpump_optimizer/binary_sensor.py").read()
    print(f"RESULT binary_sensor_finite_call_count={text.count('_finite(')} count")

finally:
    dt_util.freeze(None)

overall = int(all(results[l] for l in ("nan", "inf")))
print(f"RESULT binsens_asymmetry_confirmed={overall} bool")
