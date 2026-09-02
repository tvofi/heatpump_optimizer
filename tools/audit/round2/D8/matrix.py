"""D8 sensor verification matrix: topology x feature x entity, two cycles.

Metric (one line): per (cell, cycle, entity) snapshot of every entity of every
platform, constructed through the real ``async_setup_entry`` against a real
coordinator that was fed golden-style prices/forecasts, read its inputs
through ``_update_current_state`` and solved through
``async_run_optimization``; one RESULT count per violation class.

Command (from the repository root, thread pin is set below):

    PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py            # full matrix
    PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py --quick    # 5 topologies + 2 x features
    PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py --no-solve # unsolved cells only (fast)
    PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py --cells coord_minimal

Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, full matrix, exact;
measured twice on 2026-09-02, identical):
    RESULT cells=85  RESULT entities=65  RESULT snapshots=11050
    RESULT exceptions=0  unknown_where_data_exists=0  type_violations=0
    RESULT metadata_violations=0  nonfinite_attributes=0  stale_entities=0
    RESULT follows_payload_mismatch=0  duplicate_unique_ids=0  bad_entity_ids=0
    RESULT default_temperature_leaks=1132   (D8-01; to_zero for the `probes` cells, i.e. when
                                             every temperature has a reading; down (300->266.7 L on
                                             Mixed Hot Water) when ThermalState.dhw_temperature = 50.0)
    RESULT outdoor_default_published=10     (D8-01; the five weather_only cells x 2 cycles)
    RESULT numpy_attribute_sites=3          (D8-02; to_zero when _build_data_dict wraps the result
    RESULT unserialisable_attributes=3630    scalars/trajectories in _plain_types)
    RESULT numpy_state=30
    RESULT schedule_truncated=170           (D8-03; to_zero when the [:24] slices become [:n])
    RESULT family_splits_entity_id=15  family_splits_name_en=15  family_splits_name_sv=16
                                            (D8-04; down when hot_water_*/mixed_hot_water keys join dhw_*)
    RESULT enabled_unavailable_minimal=18  enabled_none_minimal=1  disabled_by_default=6
    RESULT first_hour_disabled=0  translation_key_mismatch=0  sv_untranslated=0

Instrumented symbols: heatpump_optimizer.sensor:async_setup_entry (and the four
other platforms' async_setup_entry), heatpump_optimizer.coordinator:
HeatPumpOptimizerCoordinator._build_data_dict / async_run_optimization /
_update_current_state, heatpump_optimizer.thermal_model:ThermalState.

Machine: MacBookAir10,1 (Apple M1, 8 GB), numpy on OpenBLAS, thread-pinned.
Writes only ``tools/audit/round2/D8/matrix_results.json``. No network, no
gate lock, deterministic (frozen clock, fixed inputs).

Harness notes (facts about the stub, not about production):
  * ``FakeHass.async_add_executor_job`` runs the solve inline.
  * ``dt_util`` is frozen at a tz-aware START so ``last_optimization`` is
    tz-aware, as in Home Assistant; ``_next_optimization`` is set by
    ``_async_update_data`` (network path) and is mirrored here by hand.
  * orjson is not installed in the venv: serialisability is checked by a
    walk that applies orjson's rules (numpy rejected, NaN/inf -> null, str keys
    unless OPT_NON_STR_KEYS, which Home Assistant passes).
  * ``HeatPumpOptimizerSensorBase.__init_subclass__`` scrubs non-finite
    values on the sensor platform only; binary_sensor/climate/switch are not
    scrubbed, and the walk covers them all.
"""
from __future__ import annotations

import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import asyncio
import copy
import json
import math
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.components.sensor import DEVICE_CLASS_STATE_CLASSES
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.util import dt as dt_util

from heatpump_optimizer import binary_sensor, button, climate, const, sensor, switch
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.thermal_model import ThermalState

from golden import START, coordinator_scenarios

HERE = Path(__file__).resolve().parent
ROOT = Path("custom_components/heatpump_optimizer")
PLATFORMS = (
    ("sensor", sensor),
    ("binary_sensor", binary_sensor),
    ("button", button),
    ("switch", switch),
    ("climate", climate),
)
INTERVAL_MINUTES = 30
START_AWARE = START.replace(tzinfo=timezone.utc)

# ---------------------------------------------------------------------------
# The matrix
# ---------------------------------------------------------------------------

#: entity_id -> (state in cycle A, state in cycle B, unit, extra attributes)
ROOM_SENSORS = {
    "sensor.indoor": ("21.4", "20.6", "°C", {}),
    "sensor.outdoor": ("-3.0", "-8.0", "°C", {}),
}
ROOM_CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
}

_VALVE = {
    const.CONF_MIXING_VALVE_MODE: "manual",
    const.CONF_BUFFER_TANK_VOLUME: 750.0,
    const.CONF_BUFFER_MAX_TEMP: 70.0,
}
_TWO_ZONE = {
    const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0,
    const.CONF_LOWER_FLOOR_THERMAL_MASS: 8.0,
    const.CONF_UPPER_FLOOR_HEAT_LOSS: 0.08,
    const.CONF_LOWER_FLOOR_HEAT_LOSS: 0.07,
}
_DHW = {
    const.CONF_DHW_TANK_VOLUME: 200.0,
    const.CONF_DHW_SETPOINT: 55.0,
    const.CONF_DHW_MIN_TEMP: 45.0,
    const.CONF_DHW_WINDOWS: "06:00-08:30, 17:00-22:00",
}
_WOOD_PROBE = {
    const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
    const.CONF_WOOD_TANK_VOLUME: 500.0,
}
_WOOD_STATES = {"sensor.wood_top": ("55.0", "50.0", "°C", {})}

#: feature -> (config overlay, states overlay). Room sensors are part of the
#: base (the realistic install); ``weather_only`` removes them.
FEATURES: dict[str, tuple[dict, dict]] = {
    "none": ({}, {}),
    "weather_only": ({}, {}),  # handled specially: drops ROOM_CONFIG/ROOM_SENSORS
    "dhw": (_DHW, {}),
    "two_zone": (_TWO_ZONE, {}),
    "valve_storage": ({**_TWO_ZONE, **_VALVE}, {}),
    "two_tank": ({**_TWO_ZONE, **_VALVE, **_WOOD_PROBE}, _WOOD_STATES),
    "coil": (
        {**_TWO_ZONE, **_VALVE, **_WOOD_PROBE, **_DHW, const.CONF_DHW_WOOD_COIL_ENABLED: True},
        _WOOD_STATES,
    ),
    "wood": (
        {
            const.CONF_EXTERNAL_HEAT_ENABLED: True,
            const.CONF_EXTERNAL_HEAT_ENTITY: "binary_sensor.flue",
            **_WOOD_PROBE,
        },
        {**_WOOD_STATES, "binary_sensor.flue": ("on", "on", None, {})},
    ),
    "ecl110": (
        {
            const.CONF_ECL110_COMMAND_TOPIC: "house/ecl110/command",
            const.CONF_ECL110_DISPLACE_SET_TOPIC: "house/ecl110/displace/set",
            const.CONF_ECL110_STATE_TOPIC: "house/ecl110/displace",
            const.CONF_ECL110_DISPLACE_MIN: -10.0,
            const.CONF_ECL110_DISPLACE_MAX: 10.0,
        },
        {},
    ),
    "pv": (
        {
            const.CONF_PV_ENABLED: True,
            const.CONF_PV_PEAK_KW: 8.0,
            const.CONF_PV_EXPORT_PRICE: 0.3,
            const.CONF_PV_PRODUCTION_ENTITY: "sensor.pv_prod",
        },
        {"sensor.pv_prod": ("1200", "300", "W", {})},
    ),
    "capacity_tariff": (
        {
            const.CONF_PEAK_TARIFF_ENABLED: True,
            const.CONF_PEAK_TARIFF_PRICE: 45.0,
            const.CONF_MAIN_FUSE_A: 20,
        },
        {},
    ),
    "grid_fee": (
        {
            const.CONF_GRID_FEE_MODE: "rules",
            const.CONF_GRID_FEE_RULES: "Mon-Fri 06:00-22:00 = 0.25",
            const.CONF_GRID_FEE_FIXED: 0.05,
            const.CONF_CONTRACT_FIXED_PRICE: 1.2,
        },
        {},
    ),
    "tuya": (
        {
            const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode",
            const.CONF_HEAT_PUMP_DEFROST_ENTITY: "binary_sensor.hp_defrost",
            const.CONF_HEAT_PUMP_ONLINE_ENTITY: "binary_sensor.hp_online",
            const.CONF_HEAT_PUMP_FAULT_ENTITY: "sensor.hp_fault",
        },
        {
            "select.hp_mode": ("HEATDHW", "heat", None, {}),
            "binary_sensor.hp_defrost": ("off", "on", None, {}),
            "binary_sensor.hp_online": ("on", "on", None, {}),
            "sensor.hp_fault": ("0", "0", None, {}),
        },
    ),
    "away": (
        {
            const.CONF_AWAY_ENABLED: True,
            const.CONF_AWAY_PRESENCE_ENTITY: "input_boolean.away",
            const.CONF_AWAY_RETURN_ENTITY: "input_datetime.back",
        },
        {
            "input_boolean.away": ("on", "on", None, {}),
            "input_datetime.back": ("2026-01-17T18:00:00", "2026-01-17T18:00:00", None, {}),
        },
    ),
    "measured_power": (
        {
            const.CONF_POWER_ENTITY: "sensor.hp_power",
            const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
            const.CONF_ENERGY_ENTITY: "sensor.hp_energy",
        },
        {
            "sensor.hp_power": ("2400", "1100", "W", {}),
            "sensor.house_power": ("3900", "2500", "W", {}),
            "sensor.hp_energy": ("1234.5", "1240.1", "kWh", {}),
        },
    ),
    "probes": (
        {
            const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
            const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
            const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.lower",
            const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.floor_return",
            const.CONF_SOLAR_RADIATION_ENTITY: "sensor.solar",
        },
        {
            "sensor.dhw": ("48.0", "52.0", "°C", {}),
            "sensor.buffer": ("38.0", "42.0", "°C", {}),
            "sensor.lower": ("20.5", "19.8", "°C", {}),
            "sensor.floor_return": ("27.0", "29.0", "°C", {}),
            "sensor.solar": ("120", "60", "W/m²", {}),
        },
    ),
    "frequency": (
        {const.CONF_COMPRESSOR_FREQ_ENTITY: "number.hp_freq"},
        {"number.hp_freq": ("47", "62", "Hz", {"min": 20, "max": 120})},
    ),
}

#: Translation key -> payload paths the entity's ``native_value``/``is_on``
#: reads (mapped by reading sensor.py / binary_sensor.py at the baseline).
SOURCES: dict[str, list[str]] = {
    "optimization_mode": ["mode"],
    "optimization_status": ["optimization_status"],
    "predicted_savings": ["predicted_savings"],
    "savings_percentage": ["savings_percentage"],
    "predicted_cost": ["predicted_cost"],
    "baseline_cost": ["baseline_cost"],
    "current_electricity_price": ["current_price"],
    "optimal_setpoint": ["current_action.setpoint"],
    "recommended_power": ["current_action.power"],
    "estimated_cop": ["outdoor_temperature"],
    "indoor_temperature_optimizer": ["indoor_temperature"],
    "outdoor_temperature_optimizer": ["outdoor_temperature"],
    "solar_irradiance": ["solar_radiation"],
    "slab_temperature_estimated": ["slab_temperature"],
    "next_optimization": ["next_optimization"],
    "last_optimization": ["last_optimization"],
    "heat_pump_action": ["current_action.mode"],
    "optimization_schedule": ["schedule"],
    "upper_floor_temperature": ["upper_floor_temperature"],
    "lower_floor_temperature": ["lower_floor_temperature"],
    "floor_heating_return_temperature": ["floor_return_temperature"],
    "solar_heat_gain": ["solar_heat_gain"],
    "buffer_tank_temperature_model": ["buffer_tank_temperature"],
    "dhw_temperature": ["dhw_temperature"],
    "dhw_heating_schedule": ["dhw_schedule"],
    "dhw_heating_cost": ["dhw_heating_cost"],
    "predictive_optimization_insight": ["predictive_info"],
    "ecl110_displace": ["ecl110_displace"],
    "ecl110_effective_displace": ["ecl110_effective_displace"],
    "space_heating_plan": ["space_plan"],
    "dhw_heating_plan": ["dhw_plan"],
    "measured_power": ["measured_power"],
    "observed_cop": ["measured_cop"],
    "space_heating_energy": ["space_energy_kwh"],
    "hot_water_energy": ["dhw_energy_kwh"],
    "total_energy": ["total_energy_kwh"],
    "space_heating_cost": ["space_cost"],
    "hot_water_cost": ["dhw_cost"],
    "total_heating_cost": ["total_cost"],
    "prediction_accuracy": ["accuracy.temperature_mae"],
    "monthly_peak_power": ["billed_peak_kw"],
    "solar_surplus_forecast": ["pv.forecast_surplus_kwh"],
    "thermal_battery_charge": ["battery.state_of_charge_percent"],
    "thermal_battery_energy": ["battery.stored_energy_kwh"],
    "valve_target_recommendation": ["valve_target_recommendation.target"],
    "comfort_weight": ["comfort_weight"],
    "contract_comparison": ["contract_comparison.load_profile_value_per_kwh"],
    "power_headroom": ["power_headroom.headroom_kw"],
    "dhw_setpoint_advisor": ["dhw_advisor.recommended_setpoint"],
    "mixed_hot_water": ["dhw_mixed.litres_40c"],
    "dhw_heavy_day_demand": ["dhw_draw_stats"],
    "plan_narrative": ["insight.narrative.items"],
    "optimization_score": ["insight.scores.overall"],
    "compressor_starts": ["insight.compressor_starts.lifetime"],
    "compressor_frequency_advisor": ["freq_control.recommended_hz"],
    "input_problem": ["stale_inputs", "input_problems"],
    "external_heat_source": ["external_heat_active"],
    "away_mode": ["away_active"],
    "open_window_detected": ["ventilation_active"],
    "optimizer_active": ["mode"],
}

#: Entities whose state is a direct numeric read (possibly rounded) of the
#: first SOURCES path: the value must follow that key within rounding.
DIRECT_NUMERIC = {
    "predicted_savings", "savings_percentage", "predicted_cost", "baseline_cost",
    "current_electricity_price", "optimal_setpoint", "recommended_power",
    "indoor_temperature_optimizer", "outdoor_temperature_optimizer",
    "solar_irradiance", "slab_temperature_estimated", "upper_floor_temperature",
    "lower_floor_temperature", "floor_heating_return_temperature",
    "solar_heat_gain", "buffer_tank_temperature_model", "dhw_temperature",
    "dhw_heating_cost", "ecl110_displace", "ecl110_effective_displace",
    "measured_power", "observed_cop", "space_heating_energy", "hot_water_energy",
    "total_energy", "space_heating_cost", "hot_water_cost", "total_heating_cost",
    "prediction_accuracy", "monthly_peak_power", "solar_surplus_forecast",
    "thermal_battery_charge", "thermal_battery_energy",
    "valve_target_recommendation", "comfort_weight", "contract_comparison",
    "power_headroom", "dhw_setpoint_advisor", "mixed_hot_water",
    "compressor_starts", "compressor_frequency_advisor",
}

#: Ordering families (translation keys), for the split count.
FAMILIES: dict[str, set[str]] = {
    "dhw": {
        "dhw_heating_cost", "dhw_heating_plan", "dhw_heating_schedule",
        "dhw_heavy_day_demand", "dhw_setpoint_advisor", "dhw_temperature",
        "hot_water_cost", "hot_water_energy", "mixed_hot_water",
    },
    "tariff": {"monthly_peak_power", "power_headroom", "contract_comparison"},
    "learning": {"comfort_weight", "observed_cop", "prediction_accuracy"},
    "accuracy": {"prediction_accuracy", "optimization_score"},
    "ecl110": {"ecl110_displace", "ecl110_effective_displace"},
    "pv": {"solar_surplus_forecast", "solar_irradiance", "solar_heat_gain"},
    "card_headline": {
        "predicted_savings", "savings_percentage", "optimization_score",
        "plan_narrative",
    },
    "lifetime": {
        "space_heating_energy", "hot_water_energy", "total_energy",
        "space_heating_cost", "hot_water_cost", "total_heating_cost",
    },
    "two_zone": {
        "upper_floor_temperature", "lower_floor_temperature",
        "floor_heating_return_temperature", "buffer_tank_temperature_model",
    },
    "thermal_battery": {"thermal_battery_charge", "thermal_battery_energy"},
}

#: The "first hour" set: what the README quick start and the card read.
FIRST_HOUR = {
    ("climate", None), ("switch", "optimizer_active"), ("button", "optimize_now"),
    ("sensor", "space_heating_plan"), ("sensor", "dhw_heating_plan"),
    ("sensor", "solar_irradiance"), ("sensor", "predicted_savings"),
    ("sensor", "savings_percentage"), ("sensor", "optimization_score"),
    ("sensor", "plan_narrative"), ("sensor", "prediction_accuracy"),
    ("binary_sensor", "input_problem"), ("sensor", "optimization_status"),
    ("sensor", "current_electricity_price"), ("sensor", "optimal_setpoint"),
    ("sensor", "recommended_power"), ("sensor", "indoor_temperature_optimizer"),
    ("sensor", "outdoor_temperature_optimizer"), ("sensor", "heat_pump_action"),
}

#: ``reading_ok`` field behind each published temperature (default-leak check).
BATTERY_COMPONENT_FIELD = {
    "dhw_tank": "dhw_temperature",
    "buffer_tank": "buffer_tank_temperature",
    "slab": "slab_temperature",
    "lower_floor": "lower_floor_temperature",
    "house": "upper_floor_temperature",
    "upper_floor": "upper_floor_temperature",
}
CLIMATE_ATTR_FIELD = {
    "dhw_temperature": "dhw_temperature",
    "slab_temperature": "slab_temperature",
    "lower_floor_temperature": "lower_floor_temperature",
    "upper_floor_temperature": "upper_floor_temperature",
}

UNIT_FOR_CLASS = {
    "temperature": {UnitOfTemperature.CELSIUS},
    "power": {UnitOfPower.KILO_WATT, UnitOfPower.WATT},
    "energy": {UnitOfEnergy.KILO_WATT_HOUR},
    "energy_storage": {UnitOfEnergy.KILO_WATT_HOUR},
    "irradiance": {"W/m²"},
    "battery": {PERCENTAGE},
    "frequency": {"Hz"},
    "volume_storage": {UnitOfVolume.LITERS},
    "timestamp": {None},
}


# ---------------------------------------------------------------------------
# Building a cell
# ---------------------------------------------------------------------------


def _prices(shift: float) -> list[dict]:
    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0 + shift, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def _weather(shift: float) -> list[dict]:
    return [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0 + shift,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


def _solar() -> list[float]:
    return [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


def _set_states(hass: FakeHass, states: dict, cycle: int, now: datetime) -> None:
    for entity_id, (a, b, unit, attrs) in states.items():
        hass.states.set(
            entity_id,
            FakeState(a if cycle == 0 else b, last_updated=now, unit=unit, attributes=attrs),
        )


def cell_config(topology: str, feature: str) -> tuple[dict, dict]:
    base = dict(coordinator_scenarios()[topology])
    overlay, states = FEATURES[feature]
    config = {**base, **overlay}
    all_states = dict(states)
    if feature != "weather_only":
        config.update(ROOM_CONFIG)
        all_states.update(ROOM_SENSORS)
    return config, all_states


async def _cycle(coord, hass, states, cycle, solve: bool):
    now = START_AWARE + timedelta(minutes=INTERVAL_MINUTES * cycle)
    dt_util.freeze(now)
    _set_states(hass, states, cycle, now)
    coord._prices = _prices(0.2 * cycle)
    coord._weather_forecast = _weather(-2.0 * cycle)
    coord._solar_radiation_forecast = _solar()
    await coord._update_current_state()
    if solve:
        await coord.async_run_optimization()
        # Mirrors coordinator.py:_async_update_data (the network path).
        coord._next_optimization = dt_util.now() + timedelta(minutes=INTERVAL_MINUTES)
    return coord._build_data_dict()


def collect(coord, config) -> list:
    """Every entity of every platform through the real async_setup_entry."""
    added = []
    for _platform, module in PLATFORMS:
        hass = FakeHass()
        hass.data[const.DOMAIN] = {"test_entry": coord}
        asyncio.run(module.async_setup_entry(hass, FakeEntry(data=config), added.extend))
    return added


# ---------------------------------------------------------------------------
# Snapshots and checks
# ---------------------------------------------------------------------------


def resolve(payload, path: str):
    node = payload
    for part in path.split("."):
        if isinstance(node, dict):
            node = node.get(part)
        else:
            return None
    return node


def present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, dict, tuple, str)):
        return len(value) > 0
    return True


def platform_of(entity) -> str:
    return str(getattr(entity, "entity_id", "")).split(".", 1)[0]


def read_value(entity):
    if hasattr(entity, "hvac_mode"):
        return {
            "current_temperature": entity.current_temperature,
            "target_temperature": entity.target_temperature,
            "hvac_mode": entity.hvac_mode,
            "hvac_action": entity.hvac_action,
            "preset_mode": entity.preset_mode,
        }
    if hasattr(entity, "native_value"):
        return entity.native_value
    if hasattr(entity, "is_on"):
        return entity.is_on
    return None


def walk_json(value, path, out, depth=0):
    """orjson's rules: numpy rejected, NaN/inf -> null, str keys (HA passes
    OPT_NON_STR_KEYS so non-str keys are counted separately as info)."""
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, (np.generic, np.ndarray)):
        out["numpy"].append(path)
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            out["nonfinite"].append(path)
        return
    if isinstance(value, int):
        return
    if isinstance(value, (datetime, date)):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                out["nonstr_key"].append(f"{path}.{key!r}")
            walk_json(item, f"{path}.{key}", out, depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            walk_json(item, f"{path}[{i}]", out, depth + 1)
        return
    if isinstance(value, (set, frozenset)):
        out["set"].append(path)
        for item in value:
            walk_json(item, f"{path}{{}}", out, depth + 1)
        return
    out["other"].append(f"{path}:{type(value).__name__}")


def meta(entity) -> dict:
    return {
        "platform": platform_of(entity),
        "entity_id": getattr(entity, "entity_id", None),
        "unique_id": getattr(entity, "_attr_unique_id", None),
        "translation_key": getattr(entity, "_attr_translation_key", None),
        "class": type(entity).__name__,
        "icon": getattr(entity, "_attr_icon", None),
        "device_class": getattr(entity, "_attr_device_class", None),
        "state_class": getattr(entity, "_attr_state_class", None),
        "unit": getattr(entity, "_attr_native_unit_of_measurement", None),
        "entity_category": getattr(entity, "_attr_entity_category", None),
        "enabled_default": getattr(entity, "_attr_entity_registry_enabled_default", True),
        "precision": getattr(entity, "_attr_suggested_display_precision", None),
        "options": getattr(entity, "_attr_options", None),
    }


def snapshot(entity, payload) -> dict:
    m = meta(entity)
    try:
        available = bool(entity.available)
    except Exception as err:  # noqa: BLE001 - an exception IS a finding
        available = f"ERR {err!r}"
    try:
        value = read_value(entity)
    except Exception as err:  # noqa: BLE001
        value = f"ERR {err!r}"
    try:
        attrs = getattr(entity, "extra_state_attributes", None) or {}
        attrs = dict(attrs)
    except Exception as err:  # noqa: BLE001
        attrs = {"__error__": repr(err)}
    m.update({"available": available, "value": value, "attrs": attrs})
    return m


def check_snapshot(snap: dict, payload: dict, currency: str, cell: str, cycle: int, viol: dict):
    key = snap["translation_key"]
    tag = f"{cell}/c{cycle}/{snap['entity_id']}"
    value = snap["value"]
    attrs = snap["attrs"]

    if isinstance(snap["available"], str) or (isinstance(value, str) and value.startswith("ERR ")):
        viol["exceptions"].append(tag)
        return
    if "__error__" in attrs:
        viol["exceptions"].append(tag + ":attrs")

    # U: available and None while every source key is present.
    sources = SOURCES.get(key, [])
    if snap["platform"] in ("sensor", "binary_sensor") and snap["available"] and value is None and sources:
        if all(present(resolve(payload, p)) for p in sources):
            viol["unknown_where_data_exists"].append(tag)

    # T: typing.
    if snap["platform"] == "sensor" and value is not None:
        if snap["state_class"] in ("measurement", "total", "total_increasing"):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                viol["type_violations"].append(f"{tag}:state_class={snap['state_class']} value={value!r}")
            elif isinstance(value, float) and not math.isfinite(value):
                viol["type_violations"].append(f"{tag}:nonfinite")
        if snap["device_class"] == "timestamp":
            if not isinstance(value, datetime) or value.tzinfo is None:
                viol["type_violations"].append(f"{tag}:timestamp={value!r}")
        if snap["options"] is not None and value not in snap["options"]:
            viol["type_violations"].append(f"{tag}:enum={value!r}")
        if isinstance(value, (np.generic, np.ndarray)):
            viol["numpy_state"].append(tag)

    # S: attribute serialisability.
    out = {"numpy": [], "nonfinite": [], "nonstr_key": [], "set": [], "other": []}
    walk_json(attrs, "", out)
    for p in out["numpy"]:
        viol["unserialisable_attributes"].append(f"{tag}{p}:numpy")
        # One site per (entity, attribute root, leaf name): the per-value list
        # above scales with the horizon, the site count does not.
        root = p.split(".")[1].split("[")[0] if "." in p else p
        leaf = p.rsplit(".", 1)[-1]
        site = f"{snap['entity_id']}:{root}.{leaf}"
        if site not in viol["numpy_attribute_sites"]:
            viol["numpy_attribute_sites"].append(site)
    for p in out["other"]:
        viol["unserialisable_attributes"].append(f"{tag}{p}")
    for p in out["nonfinite"]:
        viol["nonfinite_attributes"].append(f"{tag}{p}")
    for p in out["set"]:
        viol["set_attributes"].append(f"{tag}{p}")
    for p in out["nonstr_key"]:
        viol["nonstr_keys"].append(f"{tag}{p}")

    # D: ThermalState constructor defaults published through ungated paths.
    reading_ok = payload.get("reading_ok") or {}
    if snap["available"]:
        if snap["platform"] == "climate":
            ct = value.get("current_temperature") if isinstance(value, dict) else None
            if ct is not None and not reading_ok.get("upper_floor_temperature"):
                viol["default_temperature_leaks"].append(f"{tag}:current_temperature={ct}")
            for attr, field in CLIMATE_ATTR_FIELD.items():
                v = attrs.get(attr)
                if v is not None and not reading_ok.get(field):
                    viol["default_temperature_leaks"].append(f"{tag}:{attr}={v}")
        elif key == "indoor_temperature_optimizer" and value is not None and not reading_ok.get("upper_floor_temperature"):
            viol["default_temperature_leaks"].append(f"{tag}:state={value}")
        elif key == "mixed_hot_water" and value is not None and not reading_ok.get("dhw_temperature"):
            viol["default_temperature_leaks"].append(f"{tag}:state={value}")
            if attrs.get("tank_temperature") is not None:
                viol["default_temperature_leaks"].append(f"{tag}:tank_temperature={attrs.get('tank_temperature')}")
        elif key == "thermal_battery_charge":
            for comp in attrs.get("components") or []:
                field = BATTERY_COMPONENT_FIELD.get(comp.get("name"))
                if field and comp.get("temperature") is not None and not reading_ok.get(field):
                    viol["default_temperature_leaks"].append(f"{tag}:components.{comp.get('name')}={comp.get('temperature')}")
        if key == "outdoor_temperature_optimizer" and value is not None and not payload.get("_outdoor_read_ok"):
            viol["outdoor_default_published"].append(f"{tag}:state={value}")

    # Schedule truncation: the legacy schedule vs the plan horizon.
    if key == "optimization_schedule" and snap["available"]:
        schedule = attrs.get("schedule") or []
        forecast = (payload.get("space_plan") or {}).get("forecast") or []
        if schedule and forecast and len(schedule) < len(forecast):
            viol["schedule_truncated"].append(f"{tag}:{len(schedule)}<{len(forecast)}")


def check_metadata(entities: list, currency: str, viol: dict):
    seen: dict[str, str] = {}
    for e in entities:
        m = meta(e)
        tag = m["entity_id"]
        uid = m["unique_id"]
        if uid in seen:
            viol["duplicate_unique_ids"].append(f"{uid}: {seen[uid]} & {tag}")
        seen[uid] = tag
        if m["platform"] != "climate":
            if not m["translation_key"]:
                viol["metadata_violations"].append(f"{tag}: no translation_key")
            if m["entity_id"] != f"{m['platform']}.heat_pump_optimizer_{m['translation_key']}":
                viol["bad_entity_ids"].append(tag)
            if not m["icon"]:
                viol["no_icon"].append(tag)
        if m["platform"] != "sensor":
            continue
        dc, sc, unit = m["device_class"], m["state_class"], m["unit"]
        if dc is not None and sc is not None:
            allowed = DEVICE_CLASS_STATE_CLASSES.get(dc)
            if allowed is not None and sc not in allowed:
                viol["metadata_violations"].append(f"{tag}: state_class {sc} not allowed for {dc}")
        if dc == "monetary":
            if unit != currency:
                viol["metadata_violations"].append(f"{tag}: monetary unit {unit!r} != {currency!r}")
        elif dc in UNIT_FOR_CLASS and unit not in UNIT_FOR_CLASS[dc]:
            viol["metadata_violations"].append(f"{tag}: unit {unit!r} for {dc}")
        if sc in ("measurement", "total", "total_increasing") and unit is None and dc is None:
            viol["unitless_numeric"].append(tag)


def family_splits(order: list[str]) -> dict[str, int]:
    """Per family: number of contiguous runs minus one, in ``order``."""
    out = {}
    for name, members in FAMILIES.items():
        runs, inside = 0, False
        for key in order:
            hit = key in members
            if hit and not inside:
                runs += 1
            inside = hit
        out[name] = max(runs - 1, 0)
    return out


def ordering_report(entities: list) -> dict:
    strings = json.loads((ROOT / "strings.json").read_text())["entity"]
    en = json.loads((ROOT / "translations" / "en.json").read_text())["entity"]
    sv = json.loads((ROOT / "translations" / "sv.json").read_text())["entity"]
    sensors = [e for e in entities if platform_of(e) == "sensor"]
    keys = [e._attr_translation_key for e in sensors]
    by_id = [k for _, k in sorted((e.entity_id, e._attr_translation_key) for e in sensors)]
    by_en = [k for _, k in sorted((strings["sensor"][k]["name"].lower(), k) for k in keys)]
    by_sv = [k for _, k in sorted((sv["sensor"][k]["name"].lower(), k) for k in keys)]
    splits = {
        "entity_id": family_splits(by_id),
        "name_en": family_splits(by_en),
        "name_sv": family_splits(by_sv),
    }
    # Translation parity across the three files.
    mismatch = []
    for platform in set(strings) | set(en) | set(sv):
        s, e_, v = set(strings.get(platform, {})), set(en.get(platform, {})), set(sv.get(platform, {}))
        if not (s == e_ == v):
            mismatch.append(f"{platform}: strings^en={sorted(s ^ e_)} strings^sv={sorted(s ^ v)}")
    used = {}
    for e in entities:
        if platform_of(e) != "climate":
            used.setdefault(platform_of(e), set()).add(e._attr_translation_key)
    for platform, keys_used in used.items():
        diff = keys_used ^ set(strings.get(platform, {}))
        if diff:
            mismatch.append(f"{platform}: entities^strings={sorted(diff)}")
    en_vs_strings = sum(
        1 for p in strings for k in strings[p]
        if en.get(p, {}).get(k, {}).get("name") != strings[p][k]["name"]
    )
    sv_untranslated = [
        f"{p}:{k}" for p in strings for k in strings[p]
        if sv.get(p, {}).get(k, {}).get("name") == strings[p][k]["name"]
    ]
    return {
        "sorted_entity_id": by_id,
        "sorted_name_en": by_en,
        "sorted_name_sv": by_sv,
        "splits": splits,
        "translation_mismatch": mismatch,
        "en_differs_from_strings": en_vs_strings,
        "sv_untranslated": sv_untranslated,
    }


def enabled_report(entities: list, minimal_snaps: list[dict]) -> dict:
    disabled = sorted(
        e.entity_id for e in entities
        if getattr(e, "_attr_entity_registry_enabled_default", True) is False
    )
    first_hour_disabled = []
    for e in entities:
        p = platform_of(e)
        k = None if p == "climate" else e._attr_translation_key
        if (p, k) in FIRST_HOUR and getattr(e, "_attr_entity_registry_enabled_default", True) is False:
            first_hour_disabled.append(e.entity_id)
    enabled_unavailable = sorted(
        s["entity_id"] for s in minimal_snaps
        if s["enabled_default"] and s["available"] is False
    )
    enabled_none = sorted(
        s["entity_id"] for s in minimal_snaps
        if s["enabled_default"] and s["available"] is True and s["value"] is None
        and s["platform"] in ("sensor",)
    )
    return {
        "disabled_by_default": disabled,
        "first_hour_disabled": first_hour_disabled,
        "enabled_unavailable_in_minimal_solved": enabled_unavailable,
        "enabled_available_none_in_minimal_solved": enabled_none,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _swapins() -> int:
    try:
        text = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
        for line in text.splitlines():
            if line.startswith("Swapins:"):
                return int(line.split(":")[1].strip().rstrip("."))
    except Exception:  # noqa: BLE001
        pass
    return -1


def _trim(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _trim(v) for k, v in value.items()}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def run_cell(topology: str, feature: str, solve: bool, viol: dict, records: dict) -> list[dict]:
    cell = f"{topology}+{feature}"
    config, states = cell_config(topology, feature)
    hass = FakeHass()
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    payload1 = asyncio.run(_cycle(coord, hass, states, 0, solve))
    coord.data = payload1
    entities = collect(coord, config)
    check_metadata(entities, coord.currency, viol)

    def annotate(payload):
        payload["_outdoor_read_ok"] = coord._reading_ok(const.CONF_OUTDOOR_TEMP_ENTITY)
        return payload

    annotate(payload1)
    snaps1 = [snapshot(e, payload1) for e in entities]
    for s in snaps1:
        check_snapshot(s, payload1, coord.currency, cell, 1, viol)

    payload2 = asyncio.run(_cycle(coord, hass, states, 1, solve))
    coord.data = payload2
    annotate(payload2)
    snaps2 = [snapshot(e, payload2) for e in entities]
    fresh = collect(coord, config)
    snaps_fresh = [snapshot(e, payload2) for e in fresh]
    for s, f in zip(snaps2, snaps_fresh):
        check_snapshot(s, payload2, coord.currency, cell, 2, viol)
        tag = f"{cell}/c2/{s['entity_id']}"
        # Staleness: the entity constructed on cycle 1 must read exactly what a
        # fresh entity reads from the cycle-2 payload.
        if _trim(s["value"]) != _trim(f["value"]) or s["available"] != f["available"]:
            viol["stale_entities"].append(f"{tag}: cached={s['value']!r} fresh={f['value']!r}")
        # Follows the payload: direct numeric reads within rounding.
        key = s["translation_key"]
        if key in DIRECT_NUMERIC and s["available"] and s["value"] is not None:
            src = resolve(payload2, SOURCES[key][0])
            if isinstance(src, (int, float)) and not isinstance(src, bool) and math.isfinite(src):
                if abs(float(s["value"]) - float(src)) > 0.051:
                    viol["follows_payload_mismatch"].append(f"{tag}: value={s['value']} source={src}")
            elif src is not None and not isinstance(src, (int, float)):
                viol["follows_payload_mismatch"].append(f"{tag}: source type {type(src).__name__}")

    changed_sources = []
    for s1, s2 in zip(snaps1, snaps2):
        key = s1["translation_key"]
        if key not in SOURCES:
            continue
        src_moved = any(_trim(resolve(payload1, p)) != _trim(resolve(payload2, p)) for p in SOURCES[key])
        val_moved = _trim(s1["value"]) != _trim(s2["value"]) or s1["available"] != s2["available"]
        if src_moved and not val_moved:
            changed_sources.append(s1["entity_id"])

    records[cell] = {
        "config_keys": sorted(config),
        "reading_ok": payload2.get("reading_ok"),
        "outdoor_read_ok": payload2.get("_outdoor_read_ok"),
        "status": payload2.get("optimization_status"),
        "dhw_enabled": payload2.get("dhw_enabled"),
        "two_zone_enabled": payload2.get("two_zone_enabled"),
        "pv_enabled": payload2.get("pv_enabled"),
        "peak_tariff_enabled": payload2.get("peak_tariff_enabled"),
        "measured_power_available": payload2.get("measured_power_available"),
        "freq_mode": (payload2.get("freq_control") or {}).get("mode"),
        "away_active": payload2.get("away_active"),
        "external_heat_active": payload2.get("external_heat_active"),
        "two_tank_modelled": payload2.get("two_tank_modelled"),
        "input_problems": payload2.get("input_problems"),
        "schedule_len": len(payload2.get("schedule") or []),
        "plan_len": len((payload2.get("space_plan") or {}).get("forecast") or []),
        "source_moved_value_not": changed_sources,
        "entities": [
            {
                "entity_id": s2["entity_id"],
                "available": [s1["available"], s2["available"]],
                "value": [_trim(s1["value"]), _trim(s2["value"])],
                "attr_keys": len(s2["attrs"]),
            }
            for s1, s2 in zip(snaps1, snaps2)
        ],
    }
    dt_util.freeze(None)
    return snaps2 if solve else snaps1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="5 topologies x none + 2 topologies x every feature")
    parser.add_argument("--no-solve", action="store_true", help="skip async_run_optimization (unsolved payload)")
    parser.add_argument("--cells", default="", help="substring filter on '<topology>+<feature>'")
    args = parser.parse_args()

    topologies = list(coordinator_scenarios())
    features = list(FEATURES)
    cells = [(t, f) for t in topologies for f in features]
    if args.quick:
        cells = [(t, "none") for t in topologies] + [
            (t, f) for t in ("coord_minimal", "coord_all_features") for f in features if f != "none"
        ]
    if args.cells:
        cells = [(t, f) for t, f in cells if args.cells in f"{t}+{f}"]

    viol: dict[str, list] = {
        name: [] for name in (
            "exceptions", "unknown_where_data_exists", "type_violations", "numpy_state",
            "metadata_violations", "unserialisable_attributes", "numpy_attribute_sites",
            "nonfinite_attributes",
            "set_attributes", "nonstr_keys", "stale_entities", "follows_payload_mismatch",
            "default_temperature_leaks", "outdoor_default_published", "schedule_truncated",
            "duplicate_unique_ids", "bad_entity_ids", "no_icon", "unitless_numeric",
        )
    }
    records: dict = {}
    cpu0, thr0, wall0 = time.process_time(), time.thread_time(), time.time()
    entities_ref = None
    minimal_snaps = None
    n_snaps = 0
    for i, (topology, feature) in enumerate(cells):
        t0 = time.time()
        snaps = run_cell(topology, feature, not args.no_solve, viol, records)
        n_snaps += 2 * len(snaps)
        if entities_ref is None:
            config, _ = cell_config(topology, feature)
            hass = FakeHass()
            coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
            coord.data = {}
            entities_ref = collect(coord, config)
        if (topology, feature) == ("coord_minimal", "none"):
            minimal_snaps = snaps
        print(f"cell {i + 1}/{len(cells)} {topology}+{feature} status={records[f'{topology}+{feature}']['status']} "
              f"{time.time() - t0:.1f}s", flush=True)

    ordering = ordering_report(entities_ref)
    enabled = enabled_report(entities_ref, minimal_snaps or [])
    cpu, thr, wall = time.process_time() - cpu0, time.thread_time() - thr0, time.time() - wall0

    summary = {
        "baseline_sha": "c398fc84eec25fc44b60d74aae05b9a2da205884",
        "cells": len(cells),
        "solve": not args.no_solve,
        "entities": len(entities_ref),
        "snapshots": n_snaps,
        "violations": viol,
        "ordering": ordering,
        "enabled": enabled,
        "cells_detail": records,
        "cpu_s": round(cpu, 2),
        "wall_s": round(wall, 2),
    }
    (HERE / ("matrix_results.json" if not args.cells else "matrix_results_subset.json")).write_text(
        json.dumps(summary, indent=1, default=str)
    )

    print(f"RESULT cells={len(cells)} count")
    print(f"RESULT entities={len(entities_ref)} count")
    print(f"RESULT snapshots={n_snaps} count")
    for name, items in viol.items():
        print(f"RESULT {name}={len(items)} count")
    for sort_key, per_family in ordering["splits"].items():
        print(f"RESULT family_splits_{sort_key}={sum(per_family.values())} count")
    print(f"RESULT translation_key_mismatch={len(ordering['translation_mismatch'])} count")
    print(f"RESULT en_differs_from_strings={ordering['en_differs_from_strings']} count")
    print(f"RESULT sv_untranslated={len(ordering['sv_untranslated'])} count")
    print(f"RESULT disabled_by_default={len(enabled['disabled_by_default'])} count")
    print(f"RESULT first_hour_disabled={len(enabled['first_hour_disabled'])} count")
    print(f"RESULT enabled_unavailable_minimal={len(enabled['enabled_unavailable_in_minimal_solved'])} count")
    print(f"RESULT enabled_none_minimal={len(enabled['enabled_available_none_in_minimal_solved'])} count")
    print(f"RESULT thread_factor={cpu / thr if thr else 0.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print(f"RESULT swapins={_swapins()} count")
    print(f"RESULT cpu_s={cpu:.2f} s (provisional, contended box)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
