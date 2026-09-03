"""D9 metric 6: published payload bytes versus the recorder exclusion set.

Metric (binding, tools/audit/briefs/D9.md): JSON bytes (``json.dumps``,
``default=str``, UTF-8) of ``_build_data_dict()`` and of every entity's
``extra_state_attributes`` after one real coordinator cycle, the latter split
into what the entity's ``_unrecorded_attributes`` keeps out of the recorder
and what it lets through; per cycle, and per day at the default 30-minute
interval (48 cycles). Entities are instantiated through each platform's real
``async_setup_entry`` (the tests/entities.py:collect idiom -- that module
cannot be imported, it runs its suite at import).

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h6_payload_bytes.py

Expected (baseline c398fc8; bytes, final -- deterministic inputs):
    payload (_build_data_dict) of order 50-100 KB per cycle; entity
    attributes of order 60-120 KB per cycle of which the plan sensors'
    ``forecast``/``slots`` and the schedule sensors' lists are excluded; the
    recorded remainder per cycle is what the recorder may write each time an
    attribute changes (an upper bound: HA dedups identical attribute blobs)
    perturbation horizon 24 h -> 48 h: payload and attribute bytes rise

Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._build_data_dict,
sensor/binary_sensor/climate/switch/button:async_setup_entry and every
entity's extra_state_attributes / _unrecorded_attributes.
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import binary_sensor, button, climate, const, sensor, switch  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
CYCLES_PER_DAY = 24 * 60 // const.DEFAULT_OPTIMIZATION_INTERVAL
CONFIG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
}


def jbytes(obj) -> int:
    return len(json.dumps(obj, default=str, separators=(",", ":")).encode("utf-8"))


def make(horizon: float | None):
    hass = FakeHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
    entry = FakeEntry(data=CONFIG)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    if horizon is not None:
        coord._opt_config.horizon_hours = horizon
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(72)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(72)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(72)
    ]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    # The platforms read ``entry.runtime_data`` since audit B5 (3da0e27);
    # the ``hass.data`` slot is what they read before it. Both are set.
    hass.data[const.DOMAIN] = {entry.entry_id: coord}
    entry.runtime_data = coord
    return hass, entry, coord


def collect(hass, entry):
    added = []
    for module in (sensor, binary_sensor, climate, switch, button):
        asyncio.run(module.async_setup_entry(hass, entry, lambda ents: added.extend(ents)))
    return added


def measure(label: str, horizon: float | None):
    hass, entry, coord = make(horizon)
    dt_util.freeze(START + timedelta(hours=8, minutes=3))
    coord.data = asyncio.run(coord._async_update_data())
    dt_util.freeze(START + timedelta(hours=8, minutes=33))
    coord.data = asyncio.run(coord._async_update_data())
    data = coord.data
    dt_util.freeze(None)

    payload = jbytes(data)
    d9lib.result(f"{label}.n_steps", coord._opt_config.n_steps, "count")
    d9lib.result(f"{label}.payload_keys", len(data), "count")
    d9lib.result(f"{label}.payload_bytes_per_cycle", payload, "bytes")
    d9lib.result(f"{label}.payload_bytes_per_day", payload * CYCLES_PER_DAY, "bytes")
    top = sorted(((jbytes(v), k) for k, v in data.items()), reverse=True)[:6]
    for b, k in top:
        d9lib.result(f"{label}.payload_key.{k}", b, "bytes")

    entities = collect(hass, entry)
    total = recorded = unrecorded = 0
    with_attrs = 0
    failures = 0
    rows = []
    for ent in entities:
        # The test stub's Entity base has no default for the property, so an
        # entity that never defines extra_state_attributes (buttons, plain
        # value sensors) raises AttributeError here: that is "no attributes",
        # not a failure. Anything else raised inside a defined property is.
        if not any("extra_state_attributes" in vars(cls) for cls in type(ent).__mro__):
            continue
        try:
            attrs = ent.extra_state_attributes
        except Exception:  # noqa: BLE001 - report, do not stop
            failures += 1
            continue
        if not attrs:
            continue
        with_attrs += 1
        excl = set(getattr(type(ent), "_unrecorded_attributes", frozenset()) or ())
        b_all = jbytes(attrs)
        b_rec = jbytes({k: v for k, v in attrs.items() if k not in excl})
        total += b_all
        recorded += b_rec
        unrecorded += b_all - b_rec
        rows.append((b_rec, b_all, type(ent).__name__, sorted(attrs), sorted(excl & set(attrs))))
    d9lib.result(f"{label}.entities", len(entities), "count")
    d9lib.result(f"{label}.entities_with_attributes", with_attrs, "count")
    d9lib.result(f"{label}.entity_attribute_failures", failures, "count")
    d9lib.result(f"{label}.attr_bytes_per_cycle", total, "bytes")
    d9lib.result(f"{label}.attr_unrecorded_bytes_per_cycle", unrecorded, "bytes")
    d9lib.result(f"{label}.attr_recorded_bytes_per_cycle", recorded, "bytes")
    d9lib.result(f"{label}.attr_recorded_bytes_per_day", recorded * CYCLES_PER_DAY, "bytes")
    d9lib.result(f"{label}.attr_recorded_share", recorded / max(total, 1), "ratio")
    for b_rec, b_all, name, keys, excluded in sorted(rows, reverse=True)[:8]:
        d9lib.result(f"{label}.entity.{name}.recorded", b_rec, "bytes")
        d9lib.result(f"{label}.entity.{name}.total", b_all, "bytes")
        d9lib.result(f"{label}.entity.{name}.excluded_keys", ",".join(excluded) or "-", "keys")
        d9lib.result(f"{label}.entity.{name}.recorded_keys",
                     ",".join(k for k in keys if k not in excluded)[:300], "keys")


measure("two_zone_dhw", None)
measure("perturb_h48_two_zone_dhw", 48.0)
d9lib.closing(1.0)
