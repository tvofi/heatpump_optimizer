"""Entity and platform tests for the new features.

    PYTHONPATH=tests/hastub python tests/entities.py

The entities are thin readers over ``coordinator.data``, so they are exercised
against a data dict rather than a live coordinator. That is deliberate: the
existing ``solar_alignment.py`` fixture has to know exactly which private
attributes a coordinator method touches, and it broke on every new attribute.
Testing the entities against their actual input — the published data — does not
have that problem.

What this catches that nothing else does:

* a platform added to ``PLATFORMS`` but not to ``PLATFORM_LIST``, or vice
  versa, which loads nothing and reports no error;
* an options menu entry with no handler behind it, which renders a menu row
  that does nothing;
* ``strings.json`` drifting from the translations, which had already happened
  twice by v2.7.0;
* an accumulating sensor declared ``MEASUREMENT``, which silently keeps it out
  of the Energy dashboard — the one place the integration's central claim
  should be visible.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from harness import FakeCoordinator, FakeEntry, FakeHass, Results

from homeassistant.components.sensor import SensorStateClass

import heatpump_optimizer as integration
from heatpump_optimizer import binary_sensor, button, config_flow, const, sensor

R = Results("Entities and platforms")

ROOT = Path("custom_components/heatpump_optimizer")
ENTRY = FakeEntry()


# ===========================================================================
# Platform registration
# ===========================================================================
R.section("Platform registration")

platform_list = [str(p) for p in integration.PLATFORM_LIST]
R.check(
    "PLATFORMS and PLATFORM_LIST agree",
    sorted(const.PLATFORMS) == sorted(platform_list),
    f"{sorted(const.PLATFORMS)} vs {sorted(platform_list)}",
)
for name in ("binary_sensor", "button"):
    R.check(f"the {name} platform is registered", name in const.PLATFORMS)
    R.check(
        f"the {name} module exists and sets up entries",
        hasattr(
            {"binary_sensor": binary_sensor, "button": button}[name],
            "async_setup_entry",
        ),
    )


def collect(module):
    """Instantiate every entity a platform would add, for a given data dict.

    Driven through the real ``async_setup_entry`` rather than by listing the
    classes here, so a new entity that is written but never registered still
    shows up as missing.
    """
    added = []

    def add_entities(entities):
        added.extend(entities)

    hass = FakeHass()
    hass.data[const.DOMAIN] = {ENTRY.entry_id: FakeCoordinator(DATA)}
    asyncio.run(module.async_setup_entry(hass, ENTRY, add_entities))
    return added


# A representative published payload, covering every key the new entities read.
DATA = {
    "mode": "auto",
    "current_action": {"power": 2.5, "setpoint": 21.0},
    "measured_power": 2.4,
    "measured_house_power": 3.9,
    "measured_energy": 1234.5,
    "measured_power_available": True,
    "measured_cop": 3.1,
    "cop_scale": 0.95,
    "cop_samples": 12,
    "defrost_derate": 0.92,
    "defrost_samples": 40,
    "defrost_buckets": [{"derate": 0.92, "samples": 40}],
    "stale_inputs": ["indoor_temp_entity"],
    "input_problems": [{"input": "indoor_temp_entity", "problem": "stale"}],
    "input_health": "1 stale",
    "input_ages_minutes": {"indoor_temp_entity": 600.0},
    "learners_frozen": True,
    "learner_freeze_reason": "stale:indoor_temp_entity",
    "external_heat_active": True,
    "external_heat_suppressing": True,
    "external_heat": {
        "confidence": 1.0,
        "fading": False,
        "source": "inferred",
        "evidence": ["DHW tank rising 3.0 °C/h with the compressor off"],
        "since": "2026-01-10T18:00:00",
    },
    "away_active": True,
    "away_source": "input_boolean.holiday",
    "away_return_time": "2026-02-14T18:00:00",
    "away_hours_until_return": 30.0,
    "away_recovery_active": False,
    "away_target_temperature": 16.0,
    "away_dhw_min_temperature": 20.0,
    "space_energy_kwh": 120.5,
    "dhw_energy_kwh": 40.25,
    "total_energy_kwh": 160.75,
    "space_cost": 210.0,
    "dhw_cost": 70.0,
    "total_cost": 280.0,
    "accuracy": {"temperature_mae": 0.3, "temperature_bias": -0.1, "trust": 0.97},
    "peak_tariff_enabled": True,
    "billed_peak_kw": 7.2,
    "peak_threshold_kw": 6.5,
    "peak_month": "2026-02",
    "projected_peak_kw": 6.9,
    "projected_peak_cost": 0.0,
    "pv_enabled": True,
    "pv": {"forecast_surplus_kwh": 5.4, "forecast_production_kwh": 12.0},
    "pv_self_consumed_kwh": 3.2,
    "battery": {
        "state_of_charge_percent": 62.0,
        "stored_energy_kwh": 8.1,
        "usable_capacity_kwh": 13.0,
        "charge_rate_kw": 16.0,
        "discharge_rate_kw": 1.2,
        "hours_of_autonomy": 6.75,
        "round_trip_efficiency_6h": 11.0,
    },
    "comfort_weight": 6.4,
    "comfort_learning": {"configured": 5.0, "learned": 6.4, "overrides": 7},
    "system_identification": {"phase": "idle", "active": False},
    "solar_radiation": 210.0,
    "solar_source": "open_meteo",
    "solar_forecast": [{"t": "2026-02-01T10:00:00", "ghi": 210.0}],
    "space_plan": {},
    "dhw_plan": {},
}


# ===========================================================================
# Sensors
# ===========================================================================
R.section("Sensors")

sensors = collect(sensor)
by_name = {s._attr_name: s for s in sensors}
R.check("all sensors are constructible", len(sensors) > 30, str(len(sensors)))

# Entity counts are published in the README, so they are a claim rather than a
# detail. A count that quietly drifts makes the documentation wrong in the one
# place a user checks before installing.
readme = Path("README.md").read_text()
for label, count, pattern in (
    ("sensors", len(sensors), r"### Sensors \((\d+) total\)"),
    ("binary sensors", 3, r"### Binary Sensors \((\d+) total\)"),
    ("buttons", 3, r"### Buttons \((\d+) total\)"),
):
    import re as _re
    match = _re.search(pattern, readme)
    R.check(
        f"the README's {label} count is right",
        match is not None and int(match.group(1)) == count,
        f"README says {match.group(1) if match else '?'}, there are {count}",
    )
R.check(
    "unique ids are unique",
    len({s._attr_unique_id for s in sensors}) == len(sensors),
)

for name in (
    "Measured Power",
    "Observed COP",
    "Space Heating Energy",
    "Hot Water Energy",
    "Total Energy",
    "Space Heating Cost",
    "Hot Water Cost",
    "Total Heating Cost",
    "Prediction Accuracy",
    "Monthly Peak Power",
    "Solar Surplus Forecast",
    "Thermal Battery Charge",
    "Thermal Battery Energy",
    "Comfort Weight",
):
    R.check(f"the {name} sensor exists", name in by_name)

R.check(
    "measured power is distinguishable from recommended power",
    "Measured Power" in by_name and "Recommended Power" in by_name,
    "two sensors that differ only in plan-versus-measurement will be confused",
)
R.check("measured power reads the measurement", by_name["Measured Power"].native_value == 2.4)
R.check(
    "measured power keeps the commanded value alongside",
    by_name["Measured Power"].extra_state_attributes["recommended_power"] == 2.5,
)
R.check("observed COP is published", by_name["Observed COP"].native_value == 3.1)

# The Energy dashboard only picks up TOTAL_INCREASING. A MEASUREMENT here would
# silently keep every one of these out of it, with no error anywhere.
for name in (
    "Space Heating Energy",
    "Hot Water Energy",
    "Total Energy",
    "Space Heating Cost",
    "Hot Water Cost",
    "Total Heating Cost",
):
    R.check(
        f"{name} is TOTAL_INCREASING",
        by_name[name]._attr_state_class == SensorStateClass.TOTAL_INCREASING,
    )
R.check(
    "the DHW/space split is described rather than implied",
    "apportioned"
    in by_name["Space Heating Energy"].extra_state_attributes["split_method"],
    "one meter cannot separate two circuits, and pretending otherwise is worse",
)
R.check(
    "the energy split reconciles with the total",
    abs(
        by_name["Space Heating Energy"].native_value
        + by_name["Hot Water Energy"].native_value
        - by_name["Total Energy"].native_value
    )
    < 1e-6,
)

R.check("accuracy is published", by_name["Prediction Accuracy"].native_value == 0.3)
R.check(
    "the accuracy bias is published alongside the magnitude",
    by_name["Prediction Accuracy"].extra_state_attributes["temperature_bias"] == -0.1,
)
R.check("the billed peak is published", by_name["Monthly Peak Power"].native_value == 7.2)
R.check(
    "the free headroom threshold is explained",
    by_name["Monthly Peak Power"].extra_state_attributes[
        "free_headroom_threshold_kw"
    ]
    == 6.5,
)
R.check("PV surplus is published", by_name["Solar Surplus Forecast"].native_value == 5.4)
R.check(
    "the battery reports state of charge",
    by_name["Thermal Battery Charge"].native_value == 62.0,
)
R.check(
    "the learned comfort weight is visible",
    by_name["Comfort Weight"].native_value == 6.4
    and by_name["Comfort Weight"].extra_state_attributes["configured"] == 5.0,
    "an invisible self-adjusting objective would be alarming",
)

# The card discovers the irradiance sensor by a stable marker, not by id.
solar_sensor = by_name["Solar Irradiance"]
R.check(
    "the solar sensor advertises a plan_kind marker",
    solar_sensor.extra_state_attributes.get("plan_kind") == "solar",
    "hardcoding an entity id is what caused the v2.6.1 card bug",
)

# Optional inputs must degrade cleanly.
no_power = FakeCoordinator({**DATA, "measured_power_available": False, "measured_power": None})
R.check(
    "the measured power sensor goes unavailable without an entity",
    not sensor.MeasuredPowerSensor(no_power, ENTRY).available,
)
R.check(
    "the observed COP sensor goes unavailable too",
    not sensor.ObservedCOPSensor(no_power, ENTRY).available,
)
R.check(
    "the peak sensor is unavailable without a capacity tariff",
    not sensor.MonthlyPeakSensor(
        FakeCoordinator({**DATA, "peak_tariff_enabled": False}), ENTRY
    ).available,
)
R.check(
    "the PV sensor is unavailable without an array",
    not sensor.PVSurplusSensor(
        FakeCoordinator({**DATA, "pv_enabled": False}), ENTRY
    ).available,
)

# Before the first update, coordinator.data is None.
empty = FakeCoordinator(None)
crashed = []
for cls in (
    sensor.MeasuredPowerSensor,
    sensor.ObservedCOPSensor,
    sensor.SpaceEnergySensor,
    sensor.TotalCostSensor,
    sensor.PredictionAccuracySensor,
    sensor.MonthlyPeakSensor,
    sensor.PVSurplusSensor,
    sensor.ThermalBatterySensor,
    sensor.ThermalBatteryEnergySensor,
    sensor.ComfortWeightSensor,
):
    try:
        entity = cls(empty, ENTRY)
        entity.native_value
        entity.extra_state_attributes
    except Exception as err:  # noqa: BLE001 - that is what is being tested
        crashed.append(f"{cls.__name__}: {err}")
R.check(
    "no sensor crashes before the first update",
    not crashed,
    "; ".join(crashed),
)


# ===========================================================================
# Binary sensors
# ===========================================================================
R.section("Binary sensors")

binaries = collect(binary_sensor)
b_by_name = {b._attr_name: b for b in binaries}
R.check("three binary sensors are added", len(binaries) == 3, str(len(binaries)))

health = b_by_name["Input Problem"]
R.check("a stale input raises the problem flag", health.is_on)
R.check(
    "the problem names the input",
    health.extra_state_attributes["stale_inputs"] == ["indoor_temp_entity"],
)
R.check(
    "the frozen learners are reported with a reason",
    health.extra_state_attributes["learner_freeze_reason"]
    == "stale:indoor_temp_entity",
)
R.check(
    "a healthy install does not flag a problem",
    not binary_sensor.InputHealthBinarySensor(
        FakeCoordinator({"stale_inputs": [], "input_problems": []}), ENTRY
    ).is_on,
)

heat = b_by_name["External Heat Source"]
R.check("the external heat sensor reflects the detector", heat.is_on)
R.check(
    "its evidence is published so a user can check the reasoning",
    heat.extra_state_attributes["evidence"],
    "a heuristic that silently changes the plan cannot be trusted or debugged",
)
R.check(
    "suppression is reported separately from detection",
    heat.extra_state_attributes["suppressing_electric_dhw"] is True,
)

away = b_by_name["Away Mode"]
R.check("away mode is reflected", away.is_on)
R.check(
    "the return time is published",
    away.extra_state_attributes["return_time"] == "2026-02-14T18:00:00",
)

b_crashed = []
for entity in (
    binary_sensor.InputHealthBinarySensor(empty, ENTRY),
    binary_sensor.ExternalHeatBinarySensor(empty, ENTRY),
    binary_sensor.AwayModeBinarySensor(empty, ENTRY),
):
    try:
        entity.is_on
        entity.extra_state_attributes
    except Exception as err:  # noqa: BLE001
        b_crashed.append(str(err))
R.check("no binary sensor crashes before the first update", not b_crashed, "; ".join(b_crashed))


# ===========================================================================
# Buttons
# ===========================================================================
R.section("Buttons")

buttons = collect(button)
btn_by_name = {b._attr_name: b for b in buttons}
R.check("three buttons are added", len(buttons) == 3, str(len(buttons)))
for name in (
    "Optimize Now",
    "Run System Identification",
    "Reset Learned Comfort Weight",
):
    R.check(f"the {name} button exists", name in btn_by_name)

coord = FakeCoordinator(DATA)
force = button.ForceOptimizationButton(coord, ENTRY)
R.check("the run button is available when idle", force.available)
asyncio.run(force.async_press())
R.check("pressing it forces a run", coord.pressed == ["force_optimization"])

busy = FakeCoordinator(DATA, optimization_running=True)
R.check(
    "the run button is unavailable while a run is in flight",
    not button.ForceOptimizationButton(busy, ENTRY).available,
    "a control that appears to do nothing for seconds invites repeated presses",
)
running_sysid = FakeCoordinator(DATA, system_identification_active=True)
R.check(
    "the experiment button is unavailable while one is running",
    not button.SystemIdentificationButton(running_sysid, ENTRY).available,
)

reset = button.ResetComfortWeightButton(coord, ENTRY)
asyncio.run(reset.async_press())
R.check(
    "the reset button reaches the coordinator",
    "reset_comfort_weight" in coord.pressed,
)


# ===========================================================================
# Options flow
# ===========================================================================
R.section("Options flow")

options = config_flow.HeatPumpOptimizerOptionsFlow
missing = [
    step
    for step in options._MENU_LABELS
    if not hasattr(options, f"async_step_{step}")
]
R.check(
    "every menu entry has a handler behind it",
    not missing,
    ", ".join(missing),
    # A menu row with no handler renders and then does nothing at all.
)
for step in ("building_preset", "grid", "solar_pv", "away", "learning"):
    R.check(f"the {step} page is offered in the menu", step in options._MENU_LABELS)

for key in (
    const.CONF_POWER_ENTITY,
    const.CONF_ENERGY_ENTITY,
    const.CONF_HOUSE_POWER_ENTITY,
    const.CONF_EXTERNAL_HEAT_ENTITY,
    const.CONF_PV_PRODUCTION_ENTITY,
    const.CONF_AWAY_PRESENCE_ENTITY,
):
    R.check(
        f"{key} can be cleared again once set",
        key in options._OPTIONAL_ENTITY_KEYS,
        "options merge over setup data, so an absent key restores the old value",
    )


# ===========================================================================
# Translations
# ===========================================================================
R.section("Translations")


def all_keys(data, prefix=""):
    keys = set()
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        keys.add(path)
        if isinstance(value, dict):
            keys |= all_keys(value, path)
    return keys


strings = json.loads((ROOT / "strings.json").read_text())
files = {
    name: json.loads((ROOT / "translations" / f"{name}.json").read_text())
    for name in ("en", "sv")
}
base_keys = all_keys(strings)
for name, data in files.items():
    diff = base_keys ^ all_keys(data)
    R.check(
        f"{name}.json matches strings.json exactly",
        not diff,
        ", ".join(sorted(diff)[:6]),
    )

menu = strings["options"]["step"]["init"]["menu_options"]
R.check(
    "the menu in strings.json matches the flow",
    set(menu) == set(options._MENU_LABELS),
    str(set(menu) ^ set(options._MENU_LABELS)),
)

sv_menu = files["sv"]["options"]["step"]["init"]["menu_options"]
R.check(
    "the Swedish menu is actually translated",
    sum(1 for k in sv_menu if sv_menu[k] == menu[k]) < len(menu) / 2,
    "placeholder English left in a translation is worse than no translation",
)

selectors = strings.get("selector", {})
for key in ("building_structure", "building_era", "building_foundation", "emitter"):
    R.check(f"the {key} dropdown has labels", key in selectors)


# ===========================================================================
# Services
# ===========================================================================
R.section("Services")

import yaml

services = yaml.safe_load((ROOT / "services.yaml").read_text())

R.check("simulate_plan is documented", "simulate_plan" in services)
R.check(
    "its fields are documented for the UI",
    set(services["simulate_plan"]["fields"]) >= {"target_temp", "dhw_setpoint"},
)
R.check(
    "the service schema accepts what the card sends",
    "target_temp" in integration.SERVICE_SCHEMA_SIMULATE_PLAN.schema.__str__(),
)


sys.exit(R.close("ENTITY CHECKS"))
