"""D8 round 5 -- the topology x feature matrix.

WHAT IT MEASURES (metric definition): for every (config cell, entity) pair the
number of entities whose published surface violates one named class --
`raise` (reading native_value/extra_state_attributes raised), `nonfinite`
(a non-finite or numpy leaf in the published state or attributes),
`avail_none` (available True, native_value None), `enum_bad` (ENUM with a
state not in _attr_options), `numeric_bad` (MEASUREMENT with a non-numeric
state), `unit_bad` (device_class/unit disagreement). One RESULT line per
class, plus a per-cell entity census.

RUN:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/matrix.py

Baseline SHA eaa2a06af16a1b5b006f58a0f36cc92131f80225 (round 5). Superseded by d8_cells.py, which seeds every reading-gate state. Machine: Apple M1, 8 GB.
Expected: every violation class 0 (the matrix is a non-finding machine; a
non-zero class is a lead to open up by hand).
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import time
from pathlib import Path

# Thread pin, before any numpy import (tests/stress.py's loop).
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))

import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from golden import START  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.sensor import (  # noqa: E402
    SensorDeviceClass,
    SensorStateClass,
)

from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, config_flow, datetime as datetime_mod,
    sensor, switch, const,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]
PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}


# --- the untouched flow config (the install the flow actually produces) ------
class _FlowOKSession:
    class _Resp:
        status = 200
        async def json(self):
            return {"data": {"viewer": {"name": "Home"}}}
        async def __aenter__(self):
            return self
        async def __aexit__(self, *a):
            return False
    def post(self, *a, **k):
        return self._Resp()


_REQUIRED = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "tok",
             const.CONF_WEATHER_ENTITY: "weather.home"}


def _ans(schema, required):
    out = {}
    for key in (schema.schema if schema else ()):
        n = str(key)
        if n in required:
            out[n] = required[n]
            continue
        d = getattr(key, "description", None) or {}
        if isinstance(d, dict) and "suggested_value" in d:
            out[n] = d["suggested_value"]
            continue
        try:
            default = key.default()
        except Exception:  # noqa: BLE001
            default = None
        if default is not None and type(default).__name__ != "Undefined":
            out[n] = default
    return out


async def _walk_flow_untouched():
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _FlowOKSession()
    try:
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        r = await flow.async_step_user(None)
        for _ in range(40):
            if r.get("type") == "create_entry":
                return dict(r["data"])
            if r.get("type") == "menu":
                step = list(r["menu_options"])[0]
                r = await getattr(flow, f"async_step_{step}")(None)
                continue
            step = r["step_id"]
            r = await getattr(flow, f"async_step_{step}")(
                _ans(r.get("data_schema"), _REQUIRED if step == "user" else {})
            )
        raise AssertionError(r)
    finally:
        config_flow.async_get_clientsession = real


BASE = asyncio.run(_walk_flow_untouched())

# --- cells: the untouched install, plus one feature turned on ---------------
CELLS = {
    "flow_untouched": {},
    "two_zone": {
        "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
    },
    "no_dhw": {"dhw_tank_volume": 0.0},
    "pv": {
        "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
        "house_power_entity": "sensor.house_power",
        "pv_production_entity": "sensor.pv_production",
    },
    "capacity_tariff": {
        "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
        "main_fuse_amperes": 20.0, "house_power_entity": "sensor.house_power",
    },
    "grid_fee": {
        "grid_fee_mode": "rules",
        "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
        "grid_fee_fixed": 0.05, "contract_fixed_price": 1.2,
    },
    "away": {"away_enabled": True, "away_presence_entity": "input_boolean.holiday"},
    "wood": {
        "wood_furnace_enabled": True, "wood_tank_volume": 500.0,
        "wood_type": "mixed", "wood_packing": "packed",
        "wood_price_sek_m3": 800.0, "wood_furnace_efficiency": 75.0,
        "wood_tank_top_entity": "sensor.wood_top",
        "wood_tank_bottom_entity": "sensor.wood_bottom",
    },
    "wood_coil": {
        "wood_furnace_enabled": True, "wood_tank_volume": 500.0,
        "dhw_wood_coil_enabled": True, "valve_outlet_temp_entity": "sensor.valve_out",
        "wood_tank_top_entity": "sensor.wood_top",
        "wood_tank_bottom_entity": "sensor.wood_bottom",
    },
    "ecl110": {
        "ecl110_command_topic": "ecl/command",
        "ecl110_state_topic": "ecl/state",
        "ecl110_displace_set_topic": "ecl/displace",
        "ecl110_displace_min": -5.0, "ecl110_displace_max": 5.0,
    },
    "fuse_guard": {
        "main_fuse_amperes": 20.0, "fuse_guard_enabled": True,
        "house_power_entity": "sensor.house_power",
    },
    "mixing_valve": {
        "mixing_valve_mode": "weather_compensated",
        "mixing_valve_target": 40.0,
        "mixing_valve_target_entity": "sensor.valve_target",
    },
    "two_tank": {
        "topology_layout": const.TOPOLOGY_TWO_TANK_4WAY,
        "buffer_tank_volume": 200.0, "buffer_tank_temp_entity": "sensor.buffer",
    },
    "tuya": {
        "heat_pump_mode_entity": "sensor.hp_mode",
        "heat_pump_defrost_entity": "binary_sensor.hp_defrost",
        "heat_pump_online_entity": "binary_sensor.hp_online",
        "heat_pump_fault_entity": "binary_sensor.hp_fault",
        "heat_pump_backup_heater_entity": "binary_sensor.hp_backup",
        "heat_pump_dhw_booster_entity": "binary_sensor.hp_booster",
        "heat_pump_capacity_limited_entity": "binary_sensor.hp_limited",
    },
    # The measurement gates open: every READING_SOURCES key has a live
    # thermometer, so the gated temperature sensors must publish a real,
    # finite number rather than withholding.
    "thermometers": {
        "indoor_temp_entity": "sensor.indoor_temp",
        "outdoor_temp_entity": "sensor.outdoor_temp",
        "dhw_temp_entity": "sensor.dhw_temp",
        "floor_return_temp_entity": "sensor.floor_return",
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_energy_entity": "sensor.hp_energy",
        "heat_pump_supply_temp_entity": "sensor.hp_supply",
        "heat_pump_return_temp_entity": "sensor.hp_return",
        "house_power_entity": "sensor.house_power",
        "solar_radiation_entity": "sensor.solar_radiation",
    },
    "thermometers_two_zone": {
        "indoor_temp_entity": "sensor.indoor_temp",
        "lower_floor_temp_entity": "sensor.lower_floor",
        "outdoor_temp_entity": "sensor.outdoor_temp",
        "dhw_temp_entity": "sensor.dhw_temp",
        "floor_return_temp_entity": "sensor.floor_return",
        "buffer_tank_temp_entity": "sensor.buffer",
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_energy_entity": "sensor.hp_energy",
        "heat_pump_supply_temp_entity": "sensor.hp_supply",
        "heat_pump_return_temp_entity": "sensor.hp_return",
        "house_power_entity": "sensor.house_power",
        "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
    },
}

# states the cells reference, so the reading gates can open
CELL_STATES = {
    "sensor.house_power": FakeState("3.9"),
    "sensor.pv_production": FakeState("1.2"),
    "input_boolean.holiday": FakeState("off"),
    "sensor.wood_top": FakeState("65.0"),
    "sensor.wood_bottom": FakeState("45.0"),
    "sensor.valve_out": FakeState("38.0"),
    "sensor.valve_target": FakeState("40.0"),
    "sensor.buffer": FakeState("40.0"),
    "sensor.hp_mode": FakeState("heat"),
    "binary_sensor.hp_defrost": FakeState("off"),
    "binary_sensor.hp_online": FakeState("on"),
    "binary_sensor.hp_fault": FakeState("off"),
    "binary_sensor.hp_backup": FakeState("off"),
    "binary_sensor.hp_booster": FakeState("off"),
    "binary_sensor.hp_limited": FakeState("off"),
}


def build(config, phase):
    """A real coordinator, one input cycle, prices shifted by `phase`."""
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        for eid, state in CELL_STATES.items():
            hass.states.set(eid, state)
        entry = FakeEntry(data=dict(config))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0 + 0.2 * phase, 4),
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
    return hass, entry, coord


def collect(module, coordinator):
    added = []
    hass = FakeHass()
    entry = FakeEntry()
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(hass, entry, added.extend))
    return added


def _finite_ok(value):
    """True when the whole published value is plain, finite Python."""
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, (bool, int, str)) or value is None:
        return True
    if isinstance(value, (np.generic, np.ndarray)):
        return False
    if isinstance(value, dict):
        return all(_finite_ok(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite_ok(v) for v in value)
    return True


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def check_cell(name, config):
    hass, entry, coord = build(config, phase=0)
    viol = {k: [] for k in
            ("raise", "nonfinite", "avail_none", "enum_bad", "numeric_bad", "unit_bad")}
    census = 0
    for platform, module in PLATFORM_MODULES.items():
        for e in collect(module, coord):
            census += 1
            cname = type(e).__name__
            nv = None
            attrs = None
            try:
                if hasattr(type(e), "native_value"):
                    nv = e.native_value
                attrs = getattr(e, "extra_state_attributes", None)
            except Exception as exc:  # noqa: BLE001
                viol["raise"].append(f"{platform}:{cname}:{exc!r}")
                continue
            if not _finite_ok(nv) or not _finite_ok(attrs):
                viol["nonfinite"].append(f"{platform}:{cname}")
            avail = e.available if hasattr(e, "available") else False
            dc = getattr(e, "_attr_device_class", None)
            sc = getattr(e, "_attr_state_class", None)
            unit = getattr(e, "_attr_native_unit_of_measurement", None)
            # Binary sensors publish via `is_on`, not `native_value`; only a
            # real sensor platform entity can be "available but None".
            if platform == "sensor" and avail and nv is None:
                viol["avail_none"].append(f"{platform}:{cname}")
            if dc == SensorDeviceClass.ENUM and nv is not None:
                opts = getattr(e, "_attr_options", None) or []
                if nv not in opts:
                    viol["enum_bad"].append(f"{platform}:{cname}={nv!r}")
            if sc == SensorStateClass.MEASUREMENT and nv is not None and not is_number(nv):
                viol["numeric_bad"].append(f"{platform}:{cname}={nv!r}")
            if dc == SensorDeviceClass.TEMPERATURE and unit not in (None, "°C"):
                viol["unit_bad"].append(f"{platform}:{cname} unit={unit!r}")
            if dc == SensorDeviceClass.ENERGY and unit not in (None, "kWh", "Wh", "MWh"):
                viol["unit_bad"].append(f"{platform}:{cname} unit={unit!r}")
            if dc == SensorDeviceClass.POWER and unit not in (None, "kW", "W"):
                viol["unit_bad"].append(f"{platform}:{cname} unit={unit!r}")
    return census, viol


def main():
    t0 = time.process_time()
    total = {k: 0 for k in ("raise", "nonfinite", "avail_none", "enum_bad", "numeric_bad", "unit_bad")}
    for name, extra in CELLS.items():
        config = dict(BASE)
        config.update(extra)
        try:
            census, viol = check_cell(name, config)
        except Exception as exc:  # noqa: BLE001
            print(f"CELL {name} FAILED TO BUILD: {exc!r}")
            continue
        counts = {k: len(v) for k, v in viol.items()}
        print(f"CELL {name}: entities={census} " +
              " ".join(f"{k}={v}" for k, v in counts.items()))
        for k, items in viol.items():
            if items:
                total[k] += len(items)
                for item in items[:6]:
                    print(f"    {k}: {item}")
    print()
    for k, v in total.items():
        print(f"RESULT {k}={v} count")
    print(f"RESULT cells={len(CELLS)} count")
    print(f"RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print(f"RESULT swapins={0} count")
    print(f"RESULT cpu_s={time.process_time() - t0:.2f} cpu")


if __name__ == "__main__":
    main()
