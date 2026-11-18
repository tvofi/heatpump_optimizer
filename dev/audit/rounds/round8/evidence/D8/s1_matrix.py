#!/usr/bin/env python3
"""D8-s1 matrix harness: topology x feature crossed, real async_setup_entry,
two cycles, per-entity property checks (method steps 1, 2, 5).

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round8/D8/s1_matrix.py

Metric definitions (one line each, printed as RESULT lines):
  - round_trip_stale=<n>: entities whose native_value at data=cycle-A (first
    build) differs from native_value at data=cycle-A (rebuilt from the same
    inputs, after an intervening data=cycle-B assignment), read off the SAME
    entity object with no re-construction -- a value that does not return
    home when the input does is cached/stale, not re-derived from
    coordinator.data.
  - non_orjson=<n>: entities whose native_value or extra_state_attributes is
    not orjson-serialisable (NaN, bare numpy scalar/array) after
    async_setup_entry, across all scenarios/platforms/cycles.
  - stateclass_type_violation=<n>: MEASUREMENT/TOTAL/TOTAL_INCREASING sensors
    whose native_value is neither None nor int/float (str leaking through a
    numeric state_class, which Home Assistant would reject at write time).
  - enum_violation=<n>: SensorDeviceClass.ENUM sensors whose native_value is
    not None and not a member of _attr_options.
  - timestamp_naive=<n>: SensorDeviceClass.TIMESTAMP sensors whose
    native_value is a naive datetime (no tzinfo) -- HA logs a warning and
    drops the state.

Instrumented symbols: heatpump_optimizer.sensor / .binary_sensor / .button /
.climate / .switch / .datetime -- every concrete entity class's
native_value/state/extra_state_attributes property, driven through the real
async_setup_entry (tests/entities.py:collect), against coordinator.data built
by tests/golden.py:_capture_coordinator's own machinery, for
tests/golden.py:coordinator_scenarios()'s five topology/feature configs.

Perturbation: coordinator.data is swapped between two independently built
48h price/weather/forecast input sets (cycle A, cycle B, then A again) with
different numeric content; a value that is a pure function of coordinator.data
must return to its cycle-A value on the second A assignment. Direction: the
round-trip diff count must be 0 at HEAD and is expected to move to a positive
number when a one-line perturbation makes a property cache its first read
(see s1_perturb_cache.py) -- run separately since it edits production code
under a restore-in-finally.

Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: 4-vCPU cloud container (see BASELINE.md); all numbers here are
counts/booleans, not timing, so they are final, not provisional.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

import harness  # noqa: E402  (adds tests/, custom_components/ to sys.path)
import golden  # noqa: E402
# Deliberately NOT `import entities`: tests/entities.py runs its entire
# accreted check suite (~1700 checks, many of them subprocess-driven CI/
# governance lanes unrelated to sensors) at import time and calls
# sys.exit(0/1) at the end -- importing it here silently truncated this
# harness before a single RESULT line printed (see REPORT.md "harness
# gaps"). `collect()` is an eight-line function; it is inlined below
# instead, unchanged from tests/entities.py:238-263.
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor, binary_sensor, button, climate, switch, datetime as dt_platform  # noqa: E402


def collect_live(module, hass, entry):
    """tests/entities.py:238 `collect`, against a real, already-wired
    coordinator on `entry.runtime_data` instead of a freshly built
    FakeCoordinator -- so setup runs against the same coordinator object
    whose `.data` this harness swaps between cycles."""
    added = []

    def add_entities(es):
        added.extend(es)

    asyncio.run(module.async_setup_entry(hass, entry, add_entities))
    return added

t_start = time.process_time()

PLATFORMS = [sensor, binary_sensor, button, climate, switch, dt_platform]
SCENARIOS = golden.coordinator_scenarios()
START = golden.START


def _build_inputs(coord, base_price, base_temp):
    """One cycle's 48h prices/weather/solar, distinct by the two bases."""
    coord._prices = [
        {
            "total": round(base_price + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": base_temp + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    arrays = coord._forecast_arrays()
    data = coord._build_data_dict()
    coord.data = data
    return data


def _orjson_ok(value):
    try:
        import orjson
        orjson.dumps(value)
        return True
    except Exception:
        pass
    # Fallback definition matching sensor.py's own contract if orjson is
    # unavailable in this env: no NaN/Inf floats, no numpy scalars/arrays.
    def walk(v):
        if isinstance(v, float):
            return math.isfinite(v)
        if isinstance(v, np.generic) or isinstance(v, np.ndarray):
            return False
        if isinstance(v, dict):
            return all(walk(k) and walk(x) for k, x in v.items())
        if isinstance(v, (list, tuple)):
            return all(walk(x) for x in v)
        return True
    return walk(value)


round_trip_stale = []
non_orjson = []
stateclass_violation = []
enum_violation = []
timestamp_naive = []
total_entities_checked = 0
total_cells = 0

for scen_name, config in SCENARIOS.items():
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        entry = FakeEntry(data=config)
        coord = HeatPumpOptimizerCoordinator(hass, entry)

        data_a1 = _build_inputs(coord, base_price=0.6, base_temp=-5.0)

        entry.runtime_data = coord
        added = []
        for module in PLATFORMS:
            added.extend(collect_live(module, hass, entry))
        total_cells += 1

        # ---- cycle-A properties ----
        vals_a1 = {}
        for ent in added:
            total_entities_checked += 1
            key = getattr(ent, "_key", None) or f"{type(ent).__name__}@{id(ent)}"
            try:
                nv = ent.native_value if hasattr(ent, "native_value") else getattr(ent, "state", None)
            except Exception as exc:
                nv = f"<raised {exc!r}>"
            try:
                attrs = getattr(ent, "extra_state_attributes", None)
            except Exception:
                attrs = None
            vals_a1[key] = (type(ent), nv)

            if not _orjson_ok(nv) or not _orjson_ok(attrs):
                non_orjson.append((scen_name, type(ent).__name__, key))

            state_class = getattr(ent, "_attr_state_class", None) or getattr(
                type(ent), "_attr_state_class", None
            )
            if state_class in (
                SensorStateClass.MEASUREMENT,
                SensorStateClass.TOTAL,
                SensorStateClass.TOTAL_INCREASING,
            ):
                if nv is not None and not isinstance(nv, (int, float)):
                    stateclass_violation.append(
                        (scen_name, type(ent).__name__, key, repr(nv))
                    )

            device_class = getattr(ent, "_attr_device_class", None) or getattr(
                type(ent), "_attr_device_class", None
            )
            if device_class == SensorDeviceClass.ENUM:
                options = getattr(ent, "_attr_options", None) or getattr(
                    type(ent), "_attr_options", None
                ) or []
                if nv is not None and nv not in options:
                    enum_violation.append(
                        (scen_name, type(ent).__name__, key, repr(nv), options)
                    )
            if device_class == SensorDeviceClass.TIMESTAMP:
                if nv is not None and getattr(nv, "tzinfo", "absent") in (None, "absent"):
                    if hasattr(nv, "tzinfo"):
                        timestamp_naive.append((scen_name, type(ent).__name__, key))

        # ---- cycle B: different numbers ----
        _build_inputs(coord, base_price=1.9, base_temp=9.0)

        # ---- cycle A again: same numbers as the first build ----
        _build_inputs(coord, base_price=0.6, base_temp=-5.0)

        for ent in added:
            key = getattr(ent, "_key", None) or f"{type(ent).__name__}@{id(ent)}"
            try:
                nv2 = ent.native_value if hasattr(ent, "native_value") else getattr(ent, "state", None)
            except Exception as exc:
                nv2 = f"<raised {exc!r}>"
            _, nv1 = vals_a1.get(key, (None, None))
            same = (nv1 == nv2) or (
                isinstance(nv1, float) and isinstance(nv2, float)
                and math.isnan(nv1) and math.isnan(nv2)
            )
            if not same:
                round_trip_stale.append(
                    (scen_name, type(ent).__name__, key, repr(nv1), repr(nv2))
                )
    finally:
        dt_util.freeze(None)

thread_cpu = time.thread_time()
proc_cpu = time.process_time() - t_start
thread_factor = (proc_cpu / thread_cpu) if thread_cpu else 1.0

print(f"RESULT scenarios={len(SCENARIOS)} count")
print(f"RESULT platforms={len(PLATFORMS)} count")
print(f"RESULT total_entities_checked={total_entities_checked} count")
print(f"RESULT round_trip_stale={len(round_trip_stale)} count")
print(f"RESULT non_orjson={len(non_orjson)} count")
print(f"RESULT stateclass_type_violation={len(stateclass_violation)} count")
print(f"RESULT enum_violation={len(enum_violation)} count")
print(f"RESULT timestamp_naive={len(timestamp_naive)} count")

if round_trip_stale:
    print("-- round_trip_stale detail (first 20) --")
    for row in round_trip_stale[:20]:
        print("  ", row)
if non_orjson:
    print("-- non_orjson detail (first 20) --")
    for row in non_orjson[:20]:
        print("  ", row)
if stateclass_violation:
    print("-- stateclass_type_violation detail (first 20) --")
    for row in stateclass_violation[:20]:
        print("  ", row)
if enum_violation:
    print("-- enum_violation detail (first 20) --")
    for row in enum_violation[:20]:
        print("  ", row)
if timestamp_naive:
    print("-- timestamp_naive detail (first 20) --")
    for row in timestamp_naive[:20]:
        print("  ", row)

print(f"RESULT thread_factor={thread_factor:.4f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
