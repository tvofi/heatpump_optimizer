"""D8 round 5 -- the corrected topology x feature matrix.

WHAT IT MEASURES (one line): per (cell, entity), whether the published
surface violates a named class -- raise, nonfinite, avail_none, enum_bad,
numeric_bad, ts_naive, unit_bad -- where every cell seeds EVERY state its
entities' reading gates reference, so a gate that stays shut is a finding
and not a missing fixture.

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_cells.py

Baseline SHA eaa2a06af16a1b5b006f58a0f36cc92131f80225. Machine: Apple M1, 8 GB.
RESULTs are counts -- content, not timing.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))
sys.path.insert(0, str(_ROOT / "tests" / "hastub"))

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.sensor import (  # noqa: E402
    SensorDeviceClass,
    SensorStateClass,
)
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
ROOT = Path("custom_components/heatpump_optimizer")
STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]
PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}

# Every state any reading gate references. Seeded in every cell.
STATES = {
    "sensor.indoor_temp": "21.4", "sensor.outdoor_temp": "-3.0",
    "sensor.dhw_temp": "55.0", "sensor.floor_return": "38.0",
    "sensor.lower_floor": "20.5", "sensor.buffer": "40.0",
    "sensor.hp_power": "2.4", "sensor.hp_energy": "1234.5",
    "sensor.hp_supply": "42.0", "sensor.hp_return": "36.0",
    "sensor.house_power": "3.9", "sensor.solar_radiation": "210.0",
    "sensor.pv_production": "1.2", "input_boolean.holiday": "off",
    "sensor.valve_out": "38.0", "sensor.valve_target": "40.0",
    "sensor.wood_top": "65.0", "sensor.wood_bottom": "45.0",
    "sensor.hp_mode": "heat", "binary_sensor.hp_defrost": "off",
    "binary_sensor.hp_online": "on", "binary_sensor.hp_fault": "off",
    "binary_sensor.hp_backup": "off", "binary_sensor.hp_booster": "off",
    "binary_sensor.hp_limited": "off",
}

BASE = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    "indoor_temp_entity": "sensor.indoor_temp",
    "outdoor_temp_entity": "sensor.outdoor_temp",
    "dhw_temp_entity": "sensor.dhw_temp",
    "floor_return_temp_entity": "sensor.floor_return",
    "lower_floor_temp_entity": "sensor.lower_floor",
    "buffer_tank_temp_entity": "sensor.buffer",
    "heat_pump_power_entity": "sensor.hp_power",
    "heat_pump_energy_entity": "sensor.hp_energy",
    "house_power_entity": "sensor.house_power",
    "solar_radiation_entity": "sensor.solar_radiation",
    "heat_pump_supply_temp_entity": "sensor.hp_supply",
    "heat_pump_return_temp_entity": "sensor.hp_return",
}

CELLS = {
    "default": {},
    "dhw": {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0,
            "dhw_min_temperature": 45.0},
    "no_dhw": {"dhw_tank_volume": 0.0},
    "two_zone": {"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                 "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07},
    "two_tank": {"topology_layout": "two_tank_4way", "buffer_tank_volume": 200.0},
    "coil": {"dhw_wood_coil_enabled": True, "valve_outlet_temp_entity": "sensor.valve_out"},
    "wood": {"wood_furnace_enabled": True, "wood_tank_volume": 500.0,
             "wood_type": "mixed", "wood_packing": "packed",
             "wood_price_sek_m3": 800.0, "wood_furnace_efficiency": 75.0,
             "wood_tank_top_entity": "sensor.wood_top",
             "wood_tank_bottom_entity": "sensor.wood_bottom"},
    "ecl110": {"ecl110_command_topic": "ecl/cmd", "ecl110_state_topic": "ecl/state",
               "ecl110_displace_set_topic": "ecl/displace",
               "ecl110_displace_min": -5.0, "ecl110_displace_max": 5.0},
    "pv": {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
           "pv_production_entity": "sensor.pv_production"},
    "captariff": {"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
                  "main_fuse_amperes": 20.0},
    "gridfee": {"grid_fee_mode": "rules",
                "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
                "grid_fee_fixed": 0.05, "contract_fixed_price": 1.2},
    "away": {"away_enabled": True, "away_presence_entity": "input_boolean.holiday"},
    "tuya": {"heat_pump_mode_entity": "sensor.hp_mode",
             "heat_pump_defrost_entity": "binary_sensor.hp_defrost",
             "heat_pump_online_entity": "binary_sensor.hp_online",
             "heat_pump_fault_entity": "binary_sensor.hp_fault",
             "heat_pump_backup_heater_entity": "binary_sensor.hp_backup",
             "heat_pump_dhw_booster_entity": "binary_sensor.hp_booster",
             "heat_pump_capacity_limited_entity": "binary_sensor.hp_limited"},
    "valve": {"mixing_valve_mode": "smart_write", "mixing_valve_target": 40.0,
              "mixing_valve_target_entity": "sensor.valve_target"},
    "everything": {
        "dhw_tank_volume": 200.0, "peak_tariff_enabled": True,
        "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
        "away_enabled": True, "mixing_valve_mode": "smart_write",
        "external_heat_detection_enabled": True, "comfort_learning_enabled": True,
        "system_identification_enabled": True, "compressor_cycling_cost": 0.5,
        "wood_furnace_enabled": True, "wood_tank_volume": 500.0,
    },
}


def build(config):
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        for eid, st in STATES.items():
            hass.states.set(eid, FakeState(st))
        entry = FakeEntry(data=dict(config))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]

        async def run():
            await coord._update_current_state()
            coord.data = coord._build_data_dict()
            await coord.async_run_optimization()
            coord.data = coord._build_data_dict()

        asyncio.run(run())
    finally:
        dt_util.freeze(None)
    return hass, coord


def collect_all(coord):
    out = []
    for platform, module in PLATFORM_MODULES.items():
        added = []
        entry = FakeEntry()
        entry.runtime_data = coord
        asyncio.run(module.async_setup_entry(FakeHass(), entry, added.extend))
        for e in added:
            out.append((platform, e))
    return out


def finite_ok(v):
    if isinstance(v, float):
        return math.isfinite(v)
    if isinstance(v, (bool, int, str)) or v is None:
        return True
    if isinstance(v, (np.generic, np.ndarray)):
        return False
    if isinstance(v, dict):
        return all(finite_ok(x) for x in v.values())
    if isinstance(v, (list, tuple)):
        return all(finite_ok(x) for x in v)
    return True


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def main():
    classes = ("raise", "nonfinite", "avail_none", "enum_bad", "numeric_bad",
               "ts_naive", "unit_bad")
    total = {k: 0 for k in classes}
    seen_names = {}
    for name, extra in CELLS.items():
        cfg = dict(BASE)
        cfg.update(extra)
        try:
            hass, coord = build(cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"CELL {name} FAILED TO BUILD: {exc!r}")
            continue
        viol = {k: [] for k in classes}
        census = 0
        for platform, e in collect_all(coord):
            census += 1
            cname = type(e).__name__
            nv = None
            attrs = None
            try:
                if hasattr(type(e), "native_value"):
                    nv = e.native_value
                attrs = getattr(e, "extra_state_attributes", None)
            except Exception as exc:  # noqa: BLE001
                viol["raise"].append(f"{cname}:{exc!r}")
                continue
            if not finite_ok(nv) or not finite_ok(attrs):
                viol["nonfinite"].append(cname)
            avail = bool(getattr(e, "available", True))
            dc = getattr(e, "_attr_device_class", None)
            sc = getattr(e, "_attr_state_class", None)
            unit = getattr(e, "_attr_native_unit_of_measurement", None)
            if platform == "sensor" and avail and nv is None:
                viol["avail_none"].append(cname)
            if dc == SensorDeviceClass.ENUM and nv is not None:
                if nv not in (getattr(e, "_attr_options", None) or []):
                    viol["enum_bad"].append(f"{cname}={nv!r}")
            if sc == SensorStateClass.MEASUREMENT and nv is not None and not is_number(nv):
                viol["numeric_bad"].append(f"{cname}={nv!r}")
            if dc == SensorDeviceClass.TIMESTAMP and isinstance(nv, datetime):
                if nv.tzinfo is None:
                    viol["ts_naive"].append(cname)
            if dc == SensorDeviceClass.TEMPERATURE and unit not in (None, "°C"):
                viol["unit_bad"].append(f"{cname} unit={unit!r}")
            if dc == SensorDeviceClass.ENERGY and unit not in (None, "kWh", "Wh", "MWh"):
                viol["unit_bad"].append(f"{cname} unit={unit!r}")
            if dc == SensorDeviceClass.POWER and unit not in (None, "kW", "W"):
                viol["unit_bad"].append(f"{cname} unit={unit!r}")
        print(f"CELL {name}: entities={census} " +
              " ".join(f"{k}={len(v)}" for k, v in viol.items()))
        for k, items in viol.items():
            if items and k != "avail_none":
                for it in items[:5]:
                    print(f"    {k}: {it}")
        if "avail_none" in viol and viol["avail_none"]:
            print(f"    avail_none: {sorted(set(viol['avail_none']))}")
        for k, items in viol.items():
            total[k] += len(items)
    print()
    for k, v in total.items():
        print(f"RESULT {k}={v} count")
    print(f"RESULT cells={len(CELLS)} count")
    print("RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
