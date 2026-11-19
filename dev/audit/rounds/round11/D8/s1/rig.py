"""D8-s1 rig: the topology x feature matrix, two production cycles, every entity.

Not a harness on its own (no RESULT lines): `matrix.py` and the probe harnesses
import it. Run from the export root with PYTHONPATH=tests/hastub.

Each cell is a coordinator config plus input states. A cycle is the production
`HeatPumpOptimizerCoordinator._async_update_data` with only the three network
fetchers replaced by no-ops (prices, forecast and irradiance are injected the
way tests/golden.py:_capture_coordinator injects them), so the published dict
is the one `async_setup_entry`'s entities read in Home Assistant. Cycle B
advances the frozen clock 15 minutes and changes every input (indoor, outdoor,
power, prices), so a value that cannot follow its payload is observable.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import binary_sensor, button, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_module  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
PLATFORMS = (("sensor", sensor), ("binary_sensor", binary_sensor), ("button", button),
             ("climate", climate), ("switch", switch))

BASE = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.hp_power",
    "house_power_entity": "sensor.house_power",
}

# Input states per cycle: (A, B). Every one changes between the cycles.
STATES = {
    "sensor.indoor": ("21.4", "20.7"),
    "sensor.outdoor": ("-3.0", "-6.5"),
    "sensor.hp_power": ("1200", "2700"),
    "sensor.house_power": ("2600", "4100"),
    "sensor.upper": ("21.8", "21.1"),
    "sensor.lower": ("20.9", "20.2"),
    "sensor.tank": ("47.0", "44.5"),
    "sensor.buffer": ("38.0", "35.0"),
    "sensor.wood_top": ("62.0", "58.0"),
    "sensor.wood_bottom": ("40.0", "37.0"),
    "sensor.outlet": ("33.0", "31.0"),
    "sensor.pv": ("400", "1900"),
    "select.hp_mode": ("Heating + DHW", "Heating + DHW"),
    "sensor.slab": ("24.0", "23.2"),
    "binary_sensor.home": ("on", "on"),
    "input_boolean.stove": ("off", "off"),
}
ATTRS = {"select.hp_mode": {"options": ["Cooling", "Heating", "DHW (Hot Water)", "Cooling + DHW", "Heating + DHW"]}}
UNITS = {"sensor.hp_power": "W", "sensor.house_power": "W", "sensor.pv": "W"}


def cells() -> dict[str, dict]:
    """Topology x feature cells: golden's five topologies (sensors added) and
    one overlay per feature toggle the brief lists."""
    import golden

    out = {name: {**BASE, **cfg} for name, cfg in golden.coordinator_scenarios().items()}
    m = out["coord_minimal"]
    out["feat_two_zone_probes"] = {**out["coord_two_zone"], "upper_floor_temp_entity": "sensor.upper",
                                   "lower_floor_temp_entity": "sensor.lower"}
    out["feat_dhw_probe"] = {**out["coord_dhw"], "dhw_temp_entity": "sensor.tank"}
    out["feat_valve_storage"] = {**m, "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
                                 "buffer_tank_temp_entity": "sensor.buffer"}
    out["feat_two_tank"] = {**m, "dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.tank",
                            "mixing_valve_mode": "manual", "buffer_tank_volume": 500.0,
                            "buffer_tank_temp_entity": "sensor.buffer"}
    wood = {"wood_furnace_enabled": True, "external_heat_detection_enabled": True,
            "external_heat_entity": "input_boolean.stove", "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_bottom_entity": "sensor.wood_bottom", "valve_outlet_temp_entity": "sensor.outlet",
            "wood_tank_volume": 1000.0, "mixing_valve_mode": "manual", "buffer_tank_volume": 500.0}
    out["feat_wood"] = {**m, **wood}
    out["feat_coil"] = {**m, **wood, "dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.tank",
                        "dhw_wood_coil_enabled": True}
    out["feat_ecl110"] = {**m, "ecl110_displace_set_topic": "ecl110/displace/set",
                          "ecl110_state_topic": "ecl110/state"}
    out["feat_pv"] = {**m, "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
                      "pv_production_entity": "sensor.pv"}
    out["feat_capacity"] = {**m, "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0}
    out["feat_tuya_dhw_only"] = {**out["coord_dhw"], "dhw_temp_entity": "sensor.tank",
                                 "heat_pump_mode_entity": "select.hp_mode"}
    out["feat_away"] = {**m, "away_enabled": True, "away_presence_entity": "binary_sensor.home"}
    out["feat_min_modulation"] = {**out["coord_dhw"], "heat_pump_min_power": 1.0,
                                  "compressor_modulation": False}
    out["feat_slab"] = {**m, "slab_temp_entity": "sensor.slab"}
    return out


def _prices(start, shift):
    return [{"total": round(0.6 + shift + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (start + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)]


def _forecast(start, delta):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + delta + 3.0 * (h % 24) / 24.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


def set_states(hass, idx, when, overrides=None):
    for eid, pair in STATES.items():
        seq = (overrides or {}).get(eid, pair)
        val = seq[idx % len(seq)]
        hass.states.set(eid, FakeState(val, last_updated=when, unit=UNITS.get(eid), attributes=ATTRS.get(eid)))


async def _noop(*_a, **_k):
    return None


def build(config, overrides=None, hass_hook=None):
    hass = FakeHass()
    entry = FakeEntry(data=dict(config))
    dt_util.freeze(START)
    set_states(hass, 0, START, overrides)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._skip_solve_once = False
    coord._prices = _prices(START.replace(hour=0), 0.0)
    coord._weather_forecast = _forecast(START.replace(hour=0), 0.0)
    coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    if hass_hook:
        hass_hook(hass, coord)
    entry.runtime_data = coord
    return hass, entry, coord


def entities(hass, entry):
    out = []
    for pname, mod in PLATFORMS:
        added = []

        def add(ents, _added=added):
            for e in ents:
                e.hass = hass
            _added.extend(ents)

        asyncio.run(mod.async_setup_entry(hass, entry, add))
        out += [(pname, e) for e in added]
    return out


def cycle(hass, coord, idx, overrides=None):
    when = START + timedelta(minutes=15 * idx)
    dt_util.freeze(when)
    set_states(hass, idx, when, overrides)
    if idx:
        coord._prices = _prices(START.replace(hour=0), 0.35)
        coord._weather_forecast = _forecast(START.replace(hour=0), -3.5)
    err = None
    try:
        coord.data = asyncio.run(coord._async_update_data())
        coord.last_update_success = True
    except Exception as exc:  # noqa: BLE001 - a failed cycle is a recorded fact
        err = f"{type(exc).__name__}: {exc}"
        coord.last_update_success = False
    return err


def run_cell(config, overrides=None, hass_hook=None, n=2):
    """[(err, data)] per cycle, plus the entity list (constructed once, as HA does)."""
    hass, entry, coord = build(config, overrides, hass_hook)
    ents = None
    cycles = []
    for idx in range(n):
        err = cycle(hass, coord, idx, overrides)
        if ents is None:
            ents = entities(hass, entry)
        cycles.append((err, coord.data, snapshot(ents)))
    dt_util.freeze(None)
    return coord, ents, cycles


def _safe(fn):
    try:
        return fn(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def state_of(pname, e):
    if pname == "sensor":
        return _safe(lambda: e.native_value)
    if pname in ("binary_sensor", "switch"):
        return _safe(lambda: e.is_on)
    if pname == "climate":
        return _safe(lambda: e.hvac_mode)
    return None, None


def snapshot(ents):
    rows = []
    for pname, e in ents:
        val, verr = state_of(pname, e)
        attrs, aerr = _safe(lambda: getattr(e, "extra_state_attributes", None))  # HA Entity defaults it to None; the stub omits it
        avail, _ = _safe(lambda: e.available)
        rows.append({
            "platform": pname, "cls": type(e).__name__, "uid": getattr(e, "_attr_unique_id", None),
            "key": getattr(e, "_key", None), "tkey": getattr(e, "_attr_translation_key", None),
            "state": val, "state_err": verr, "attrs": attrs, "attrs_err": aerr, "available": avail,
            "device_class": _safe(lambda: e.device_class)[0],
            "state_class": _safe(lambda: getattr(e, "state_class", None))[0],
            "unit": _safe(lambda: getattr(e, "native_unit_of_measurement", None))[0],
            "options": _safe(lambda: getattr(e, "options", None))[0],
            "category": _safe(lambda: getattr(e, "entity_category", None))[0],
            "icon": _safe(lambda: getattr(e, "icon", None))[0],
            "enabled_default": bool(getattr(e, "entity_registry_enabled_default",
                                            getattr(e, "_attr_entity_registry_enabled_default", True))),
            "entity": e,
        })
    return rows
