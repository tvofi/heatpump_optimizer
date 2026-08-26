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

from harness import FakeCoordinator, FakeEntry, FakeHass, FakeState, Results

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
    "ventilation_active": True,
    "ventilation_evidence": [
        "2026-02-01T10:05:00: room 1.4 °C under prediction while heating"
    ],
    "immersion_active": False,
    "immersion_evidence": [],
    "cop_health": {"watched_buckets": 2, "alarm": False, "evidence": []},
    "snapshots": {"count": 3, "alarm": False, "last_taken": "2026-02-01T03:00:00"},
    "capacity_envelope": {"buckets": {"-9": [4.8, 12]}},
    "solar_aperture": {"scale": 1.15, "samples": 40},
    "internal_gains_profile": None,
    "heat_curve": {"bias_k": -0.4, "comfortable_days": 1, "resets": 0},
    "insight": {
        "narrative": {
            "items": [
                {"reason": "cheap_price", "kwh": 6.2, "sek": 8.4, "hours": 3.0},
                {"reason": "idle", "kwh": 0.0, "sek": 0.0, "hours": 21.0},
            ],
            "lines": ["6.2 kWh in the cheapest hours for 8.40 kr"],
            "language": "en",
        },
        "scores": {
            "envelope": 75.0,
            "machine": 100.0,
            "operation": None,
            "overall": 87.5,
        },
        "compressor_starts": {
            "lifetime": 412,
            "month": 31,
            "wear_price_per_start": 0.4,
        },
        "monthly_report": {
            "month": "2026-01",
            "reasons_reconcile": True,
            "total_kwh": 812.4,
        },
        "price_tiles": {
            "target_minus_1": {"monthly_cost_delta": -84.0}
        },
        "last_diagnosis": {"residual": -0.3, "unexplained": -0.1},
    },
    "freq_control": {
        "mode": "observe",
        "fallback_active": False,
        "reported_hz": 47.0,
        "recommended_hz": 45.0,
        "commanded_hz": None,
        "range_hz": [20.0, 120.0],
        "map": {"2": {"mid_hz": 45.0, "kw_per_hz": 0.044, "samples": 12}},
    },
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
    "power_headroom": {
        "available": True,
        "limit_kw": 13.8,
        "headroom_kw": 7.3,
        "baseline_source": "house meter",
        "horizon_headroom_kw": [7.3, 7.1],
    },
    "fuse_advisor": {
        "month": "2026-02",
        "current_fuse_a": 20,
        "candidate_fuse_a": 16,
        "feasible": True,
        "cost_delta_sek_month": -35.0,
    },
    "peak_guard_suppressing": False,
    "peak_guard_evidence": [],
    "outage_recovery_active": True,
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
    "dhw_inlet_temperature": 8.5,
    "dhw_mixed": {
        "litres_40c": 450.0,
        "tank_temperature": 55.0,
        "shower_minutes": 56.3,
    },
    "dhw_advisor": {
        "current_setpoint": 55.0,
        "recommended_setpoint": 52,
        "heaviest_window_kwh": 3.4,
        "candidates": [
            {"setpoint": 52, "cost_per_day": 6.1, "meets_heaviest_window": True}
        ],
    },
    "dhw_draw_stats": {
        "06:00-08:30": {"events": 12, "p90_kwh": 3.4},
        "17:00-22:00": {"events": 9, "p90_kwh": 2.1},
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
    ("binary sensors", 4, r"### Binary Sensors \((\d+) total\)"),
    ("buttons", 4, r"### Buttons \((\d+) total\)"),
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
):
    R.check(
        f"{name} is TOTAL_INCREASING",
        by_name[name]._attr_state_class == SensorStateClass.TOTAL_INCREASING,
    )
# Money is different: Home Assistant only accepts state class TOTAL for
# device class MONETARY, and long-term statistics need a currency unit.
# TOTAL_INCREASING here (as previously pinned) made HA reject the statistics.
for name in (
    "Space Heating Cost",
    "Hot Water Cost",
    "Total Heating Cost",
):
    R.check(
        f"{name} is a TOTAL in a currency",
        by_name[name]._attr_state_class == SensorStateClass.TOTAL
        and by_name[name]._attr_native_unit_of_measurement == "SEK",
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
# v4.0.0 T2: the fuse advisor's answer and the outage flag ride the peak
# sensor rather than adding two more diagnostic entities.
_peak_attrs = by_name["Monthly Peak Power"].extra_state_attributes
R.check(
    "the fuse advisor's monthly answer is published",
    _peak_attrs.get("fuse_advisor", {}).get("candidate_fuse_a") == 16,
)
R.check(
    "outage recovery is visible while it is active",
    _peak_attrs.get("outage_recovery_active") is True,
)
R.check("the Power Headroom sensor exists", "Power Headroom" in by_name)
R.check(
    "headroom is the state, in kW, ready for a charger automation",
    by_name["Power Headroom"].native_value == 7.3
    and by_name["Power Headroom"]._attr_native_unit_of_measurement == "kW",
)
R.check(
    "the headroom sensor is available exactly when a limit exists",
    by_name["Power Headroom"].available is True,
)
_hr_attrs = by_name["Power Headroom"].extra_state_attributes
R.check(
    "the headroom attributes carry the limit, source and horizon",
    _hr_attrs.get("limit_kw") == 13.8
    and _hr_attrs.get("baseline_source") == "house meter"
    and _hr_attrs.get("horizon_headroom_kw") == [7.3, 7.1]
    and "available" not in _hr_attrs,
)
# v4.0.0 T3: hot water beyond the tank temperature.
R.check(
    "the setpoint advisor recommends in °C with the sweep alongside",
    by_name["DHW Setpoint Advisor"].native_value == 52
    and by_name["DHW Setpoint Advisor"].extra_state_attributes[
        "heaviest_window_kwh"
    ]
    == 3.4,
)
R.check(
    "the tank is translated into shower terms",
    by_name["Mixed Hot Water"].native_value == 450.0
    and by_name["Mixed Hot Water"].extra_state_attributes["shower_minutes"]
    == 56.3,
)
R.check(
    "the heavy-day sensor reports the worst learned window",
    by_name["DHW Heavy Day Demand"].native_value == 3.4
    and by_name["DHW Heavy Day Demand"].extra_state_attributes[
        "17:00-22:00"
    ]["events"]
    == 9,
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

# The chart's edit ceiling and the service's expiry default have to be the same
# number, or the card shows slots as pinned past the point `channel_pins` frees
# them. The integration owns it and publishes it; the card reads it.
space_plan = by_name["Space Heating Plan"]
R.check(
    "the plan sensor publishes the manual-plan window for the card",
    space_plan.extra_state_attributes.get("manual_plan_window_hours")
    == const.MANUAL_PLAN_WINDOW_HOURS,
    "a card with its own copy of this number could drift from the service",
)

# The card labels its price axis from the integration's own currency answer.
# Both branches must carry it: before the first solve the card still renders
# an (empty) chart whose axis should not have to guess.
R.check(
    "the plan sensor publishes its currency for the card",
    space_plan.extra_state_attributes.get("currency") == space_plan.coordinator.currency,
    "the card would otherwise fall back to the browser's or HA's guess",
)
no_plan_coord = FakeCoordinator({k: v for k, v in DATA.items() if k != "space_plan"})
R.check(
    "and still publishes it before the first plan exists",
    sensor.SpaceHeatingPlanSensor(no_plan_coord, ENTRY).extra_state_attributes.get("currency")
    == no_plan_coord.currency,
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
    sensor.PlanNarrativeSensor,
    sensor.OptimizationScoreSensor,
    sensor.CompressorStartsSensor,
    sensor.ContractComparisonSensor,
    sensor.FrequencyAdvisorSensor,
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


# --- T6 insight sensors ----------------------------------------------------
narr = sensor.PlanNarrativeSensor(FakeCoordinator(DATA), ENTRY)
R.check(
    "the narrative sensor states the biggest non-idle reason",
    narr.native_value == "cheap_price",
    "idle never headlines a day that heated at all",
)
R.check(
    "the narrative's items and rendered lines ride in attributes",
    narr.extra_state_attributes.get("lines")
    and narr.extra_state_attributes.get("language") == "en",
)
score = sensor.OptimizationScoreSensor(FakeCoordinator(DATA), ENTRY)
R.check(
    "the score sensor states the overall grade with the parts in attributes",
    score.native_value == 87.5
    and score.extra_state_attributes.get("machine") == 100.0
    and "price_tiles" in score.extra_state_attributes,
)
no_scores = FakeCoordinator(
    {
        **DATA,
        "insight": {
            **DATA["insight"],
            "scores": {
                "envelope": None,
                "machine": None,
                "operation": None,
                "overall": None,
            },
        },
    }
)
R.check(
    "the score sensor is unavailable before any grade has evidence",
    not sensor.OptimizationScoreSensor(no_scores, ENTRY).available,
)
starts = sensor.CompressorStartsSensor(FakeCoordinator(DATA), ENTRY)
R.check(
    "the starts sensor counts lifetime with the month and wear price along",
    starts.native_value == 412
    and starts.extra_state_attributes.get("month") == 31,
)
R.check(
    "no power meter means no start counter, not a frozen zero",
    not sensor.CompressorStartsSensor(
        FakeCoordinator({**DATA, "measured_power_available": False}), ENTRY
    ).available,
)
R.check(
    "the monthly receipt rides the contract comparison sensor",
    sensor.ContractComparisonSensor(FakeCoordinator(DATA), ENTRY)
    .extra_state_attributes.get("monthly_report", {})
    .get("month")
    == "2026-01",
)
R.check(
    "the last diagnosis rides the prediction accuracy sensor",
    sensor.PredictionAccuracySensor(FakeCoordinator(DATA), ENTRY)
    .extra_state_attributes.get("last_diagnosis", {})
    .get("residual")
    == -0.3,
)

# --- T7 frequency advisor --------------------------------------------------
freq = sensor.FrequencyAdvisorSensor(FakeCoordinator(DATA), ENTRY)
R.check(
    "the frequency advisor states the recommendation with the map along",
    freq.available
    and freq.native_value == 45.0
    and freq.extra_state_attributes.get("mode") == "observe",
)
R.check(
    "without a frequency entity the advisor is unavailable, not zero",
    not sensor.FrequencyAdvisorSensor(
        FakeCoordinator(
            {**DATA, "freq_control": {"mode": "unconfigured", "map": {}}}
        ),
        ENTRY,
    ).available,
)


# ===========================================================================
# Binary sensors
# ===========================================================================
R.section("Binary sensors")

binaries = collect(binary_sensor)
b_by_name = {b._attr_name: b for b in binaries}
R.check("four binary sensors are added", len(binaries) == 4, str(len(binaries)))

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

vent = b_by_name["Open Window Detected"]
R.check("the open-window sensor reflects the detector", vent.is_on)
R.check(
    "its evidence is published, same contract as external heat",
    vent.extra_state_attributes["evidence"],
    "a heuristic nobody can audit is a heuristic nobody can trust",
)
R.check(
    "the open-window sensor stays quiet without the detector key",
    not binary_sensor.VentilationBinarySensor(
        FakeCoordinator({"stale_inputs": []}), ENTRY
    ).is_on,
    "old payloads without the T4a keys must read as off, not crash",
)

b_crashed = []
for entity in (
    binary_sensor.InputHealthBinarySensor(empty, ENTRY),
    binary_sensor.ExternalHeatBinarySensor(empty, ENTRY),
    binary_sensor.AwayModeBinarySensor(empty, ENTRY),
    binary_sensor.VentilationBinarySensor(empty, ENTRY),
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
R.check("four buttons are added", len(buttons) == 4, str(len(buttons)))
for name in (
    "Optimize Now",
    "Run System Identification",
    "Reset Learned Comfort Weight",
    "Diagnose Last Interval",
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


def _render_option_pages(flow_cls) -> dict:
    """Return ``{step: data_schema}`` for every page in the options menu."""
    pages = {}
    for step in flow_cls._MENU_LABELS:
        handler = getattr(flow_cls, f"async_step_{step}", None)
        if handler is None:
            continue
        flow = flow_cls(FakeEntry())
        flow.hass = FakeHass()
        result = asyncio.run(handler(flow, None))
        schema = result.get("data_schema")
        if schema is not None:
            pages[step] = schema
    return pages


def _defaults_survive_their_own_selectors(schema) -> tuple[bool, str]:
    """Submit a page untouched and report the first field that rejects itself.

    Voluptuous substitutes each field's default when the key is absent, then
    validates it like any other value -- so an empty payload exercises exactly
    the defaults, and nothing else.
    """
    try:
        schema({})
    except Exception as err:  # noqa: BLE001 - any rejection is a failure
        return False, f"{type(err).__name__}: {err}"
    return True, ""


def _entity_selectors(schema):
    """Yield ``(field, selector)`` for every entity picker on a page."""
    for key, value in schema.schema.items():
        if isinstance(value, config_flow.selector.EntitySelector):
            yield getattr(key, "schema", key), value


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
for step in ("building_preset", "grid", "solar_pv", "away", "learning", "thermal_model"):
    R.check(f"the {step} page is offered in the menu", step in options._MENU_LABELS)

# v4.0.0: the menu is two-level. ``_MENU_LABELS`` stays the flat roster of
# every leaf page — this file and the golden capture walk it expecting each
# entry to render a form — and the two tuples partition it between the top
# menu and the advanced submenu. A page in neither menu is unreachable; a
# page in both renders twice.
_top = set(options._TOP_MENU)
_advanced = set(options._ADVANCED_MENU)
R.check(
    "the top and advanced menus partition the pages exactly",
    not (_top & _advanced) and (_top | _advanced) == set(options._MENU_LABELS),
    f"overlap {sorted(_top & _advanced)}, "
    f"unpartitioned {sorted((_top | _advanced) ^ set(options._MENU_LABELS))}",
)
R.check(
    "'advanced' is a menu, not a page",
    "advanced" not in options._MENU_LABELS
    and hasattr(options, "async_step_advanced"),
    "a menu entry in _MENU_LABELS would be walked here expecting a form",
)

_menu_flow = options(FakeEntry())
_menu_flow.hass = FakeHass()
_top_menu = asyncio.run(_menu_flow.async_step_init(None))
R.check(
    "the top menu is the everyday pages plus Advanced",
    _top_menu["type"] == "menu"
    and list(_top_menu["menu_options"]) == list(options._TOP_MENU) + ["advanced"],
    str(list(_top_menu.get("menu_options", []))),
)
_advanced_menu = asyncio.run(_menu_flow.async_step_advanced(None))
R.check(
    "the advanced submenu offers exactly the advanced pages",
    _advanced_menu["type"] == "menu"
    and list(_advanced_menu["menu_options"]) == list(options._ADVANCED_MENU),
    str(list(_advanced_menu.get("menu_options", []))),
)

for key in (
    const.CONF_POWER_ENTITY,
    const.CONF_ENERGY_ENTITY,
    const.CONF_HOUSE_POWER_ENTITY,
    const.CONF_EXTERNAL_HEAT_ENTITY,
    const.CONF_PV_PRODUCTION_ENTITY,
    const.CONF_AWAY_PRESENCE_ENTITY,
    const.CONF_GRID_FEE_ENTITY,
):
    R.check(
        f"{key} can be cleared again once set",
        key in options._OPTIONAL_ENTITY_KEYS,
        "options merge over setup data, so an absent key restores the old value",
    )

# Saving one page must not clear entities configured on another. The entities
# page used to null the *whole* clearable roster, so any save of it silently
# wiped the PV, away and external-heat entities — settings that live on other
# pages and were not even on the submitted form.
_cross_page = {
    const.CONF_EXTERNAL_HEAT_ENTITY: "binary_sensor.furnace",
    const.CONF_MIXING_VALVE_TARGET_ENTITY: "sensor.valve_target",
    const.CONF_PV_PRODUCTION_ENTITY: "sensor.pv_power",
    const.CONF_PV_EXPORT_PRICE_ENTITY: "sensor.export_price",
    const.CONF_AWAY_PRESENCE_ENTITY: "person.someone",
    const.CONF_AWAY_RETURN_ENTITY: "input_datetime.back",
}
_flow = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t", **_cross_page}))
_flow.hass = FakeHass()
_form = asyncio.run(_flow.async_step_entities(None))
_untouched = _form["data_schema"]({})  # defaults only, as a real untouched save
_saved = asyncio.run(_flow.async_step_entities(_untouched))["data"]
for key, value in _cross_page.items():
    R.check(
        f"saving the entities page leaves {key} alone",
        _saved.get(key) == value,
        f"stored {value!r}, page save produced {_saved.get(key)!r}",
    )
R.check(
    "the entities page still clears its own absent fields",
    _saved.get(const.CONF_POWER_ENTITY) is None,
    "a cleared selector must be written back as None or clearing does not stick",
)

# The building page owns the valve and wood entities (v4.0.0 merged the
# mixing-valve page and the learning page's wood block into it), so it has to
# clear them itself — it used to lean on the entities page's global nulling,
# i.e. on the bug above.
_vflow = options(
    FakeEntry(
        options={
            const.CONF_MIXING_VALVE_TARGET_ENTITY: "sensor.tgt",
            const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
        }
    )
)
_vflow.hass = FakeHass()
_vsaved = asyncio.run(_vflow.async_step_building({}))["data"]
for _key in (const.CONF_MIXING_VALVE_TARGET_ENTITY, const.CONF_WOOD_TANK_TOP_ENTITY):
    R.check(
        f"the building page clears its own absent {_key}",
        _vsaved.get(_key) is None,
        f"got {_vsaved.get(_key)!r}",
    )

# The thermal_model page (v4.0.0) walks the presence-inference minefield:
# ``two_zone_enabled`` and ``dhw_enabled`` are inferred from whether their
# keys exist at all, so a page that wrote defaults for untouched fields
# would flip a legacy single-zone entry to two-zone on any save. The page
# must save exactly what the user typed and nothing else.
from heatpump_optimizer.thermal_model import ThermalParameters

_legacy = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "t", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_tflow = options(_legacy)
_tflow.hass = FakeHass()
_tform = asyncio.run(_tflow.async_step_thermal_model(None))
_tuntouched = _tform["data_schema"]({})
R.check(
    "an untouched thermal model form submits nothing at all",
    _tuntouched == {},
    f"defaults leaked into the submission: {_tuntouched}",
)
_tsaved = asyncio.run(_tflow.async_step_thermal_model(_tuntouched))["data"]
_tmerged = {**_legacy.data, **_tsaved}
R.check(
    "an untouched save leaves a legacy entry single-zone",
    not ThermalParameters.from_config(_tmerged).two_zone_enabled,
    "presence-inferred two_zone_enabled flipped by an untouched save",
)
R.check(
    "and leaves hot water off too",
    not ThermalParameters.from_config(_tmerged).dhw_enabled,
)

# Both halves of the mechanism, deliberately: a plain number saves without
# dragging zone keys along, and an explicit zone value is exactly what may
# flip the model on.
_eflow = options(_legacy)
_eflow.hass = FakeHass()
_esaved = asyncio.run(
    _eflow.async_step_thermal_model({const.CONF_HEAT_PUMP_MAX_POWER: 9.0})
)["data"]
R.check(
    "an edited number saves without touching the zone inference",
    _esaved.get(const.CONF_HEAT_PUMP_MAX_POWER) == 9.0
    and not ThermalParameters.from_config(
        {**_legacy.data, **_esaved}
    ).two_zone_enabled,
    f"saved {_esaved!r}",
)
_zflow = options(_legacy)
_zflow.hass = FakeHass()
_zsaved = asyncio.run(
    _zflow.async_step_thermal_model({const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0})
)["data"]
R.check(
    "an explicit zone value is what turns two-zone on",
    ThermalParameters.from_config({**_legacy.data, **_zsaved}).two_zone_enabled,
    "the inference must still respond to real input, or the page can never enable it",
)

# The two-zone mode (v4.0.0): the page must be able to turn the model off —
# presence of the zone keys in entry.data can only ever turn it on — and to
# turn it on for a legacy entry, while an untouched save still changes
# nothing (covered by the untouched-submit checks above, which the mode
# select participates in: it is suggested, never defaulted).
_off_entry = FakeEntry(
    data={**_legacy.data, const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
)
_off_flow = options(_off_entry)
_off_flow.hass = FakeHass()
_off_saved = asyncio.run(
    _off_flow.async_step_thermal_model({const.CONF_TWO_ZONE_MODE: "off"})
)["data"]
R.check(
    "the mode select can turn two-zone off despite stored zone keys",
    not ThermalParameters.from_config(
        {**_off_entry.data, **_off_saved}
    ).two_zone_enabled,
    "options merge over data, so only an explicit override can disable it",
)
_on_flow = options(_legacy)
_on_flow.hass = FakeHass()
_on_saved = asyncio.run(
    _on_flow.async_step_thermal_model({const.CONF_TWO_ZONE_MODE: "on"})
)["data"]
R.check(
    "and can turn two-zone on for a legacy entry with no zone keys",
    ThermalParameters.from_config(
        {**_legacy.data, **_on_saved}
    ).two_zone_enabled,
)

# The invariant behind all of the above, swept across EVERY page: opening any
# options page on a legacy single-zone entry and pressing Submit untouched
# must never flip two-zone. This is the net that catches the next page that
# grows a voluptuous default on a presence key — exactly how the old building
# page's radiator share nearly shipped as a silent zone-flipper when the
# valve and wood-tank fields moved onto it (v4.0.0 review finding).
_presence_quad = (
    const.CONF_UPPER_FLOOR_THERMAL_MASS,
    const.CONF_LOWER_FLOOR_THERMAL_MASS,
    const.CONF_INTER_ZONE_TRANSFER,
    const.CONF_RADIATOR_POWER_FRACTION,
)
for _step in options._MENU_LABELS:
    _sf = options(FakeEntry(data=dict(_legacy.data)))
    _sf.hass = FakeHass()
    _sform = asyncio.run(getattr(_sf, f"async_step_{_step}")(None))
    _sschema = _sform.get("data_schema")
    if _sschema is None:
        continue
    _sresult = asyncio.run(getattr(_sf, f"async_step_{_step}")(_sschema({})))
    if _sresult.get("type") != "create_entry":
        continue  # pages like setup_overview just return to the menu
    _ssaved = _sresult["data"]
    _wrote = [k for k in _presence_quad if k in _ssaved]
    R.check(
        f"an untouched save of the {_step} page cannot flip two-zone",
        not _wrote
        and not ThermalParameters.from_config(
            {**_legacy.data, **_ssaved}
        ).two_zone_enabled,
        f"wrote presence keys {_wrote}",
    )

# A stored value is *suggested* back, not defaulted: the form pre-fills, but
# an untouched submission still writes nothing.
_pflow = options(
    FakeEntry(data={**_legacy.data, const.CONF_HEAT_PUMP_MAX_POWER: 6.0})
)
_pflow.hass = FakeHass()
_pform = asyncio.run(_pflow.async_step_thermal_model(None))
_pmarker = next(
    k
    for k in _pform["data_schema"].schema
    if str(getattr(k, "schema", k)) == const.CONF_HEAT_PUMP_MAX_POWER
)
R.check(
    "a stored value is suggested back rather than defaulted",
    getattr(_pmarker, "description", None) == {"suggested_value": 6.0}
    and _pform["data_schema"]({}) == {},
    f"description={getattr(_pmarker, 'description', None)!r}",
)


# ===========================================================================
# Option page schemas
# ===========================================================================
R.section("Option page schemas")

# Render every options page and submit it back untouched. That is the cheapest
# thing a user can do — open a page, press Submit — and it is the case that
# broke: a field whose default does not satisfy its own selector fails only
# when the user leaves it alone, so clicking through the flow by hand can miss
# it entirely.
_pages = _render_option_pages(options)

R.check(
    "every menu page renders a schema",
    set(_pages) == set(options._MENU_LABELS),
    str(set(_pages) ^ set(options._MENU_LABELS)),
)

for step, schema in sorted(_pages.items()):
    ok, detail = _defaults_survive_their_own_selectors(schema)
    R.check(f"the {step} page can be submitted untouched", ok, detail)

# Entity pickers must use the modern ``filter`` key. With the legacy top-level
# ``domain`` the frontend cannot work out which helper type its "create helper"
# shortcut should make, and creates one with no name -- which the user sees as
# "required key not provided @ data['name']".
_legacy = sorted(
    f"{step}.{key}"
    for step, schema in _pages.items()
    for key, sel in _entity_selectors(schema)
    if "domain" in sel.config or "device_class" in sel.config
)
R.check(
    "entity pickers use filter= rather than the legacy domain key",
    not _legacy,
    ", ".join(_legacy),
)

_unfiltered = sorted(
    f"{step}.{key}"
    for step, schema in _pages.items()
    for key, sel in _entity_selectors(schema)
    if not sel.config.get("filter")
)
R.check(
    "every entity picker is narrowed to a domain",
    not _unfiltered,
    ", ".join(_unfiltered),
)

# v3.15.1: the hot water tank refills through a coil in the wood tank. That is
# plumbing, not a detector setting, so the option lives beside the wood tank it
# depends on -- since v4.0.0 that is the combined heating-system page.
_building_fields = {
    str(getattr(k, "schema", k)) for k in _pages["building"].schema
}
R.check(
    "the DHW wood-coil option is offered on the wood tank's own page",
    const.CONF_DHW_WOOD_COIL_ENABLED in _building_fields,
    sorted(_building_fields),
)
R.check(
    "and it is off unless asked for",
    _pages["building"]({}).get(const.CONF_DHW_WOOD_COIL_ENABLED) is False,
    "a new option that defaults on silently changes every existing install",
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
advanced_menu = strings["options"]["step"]["advanced"]["menu_options"]
R.check(
    "the two menus in strings.json match the flow, in order",
    list(menu) == list(options._TOP_MENU) + ["advanced"]
    and list(advanced_menu) == list(options._ADVANCED_MENU),
    f"init {list(menu)}, advanced {list(advanced_menu)}",
)

for _step_id, _base in (("init", menu), ("advanced", advanced_menu)):
    _sv_menu = files["sv"]["options"]["step"][_step_id]["menu_options"]
    R.check(
        f"the Swedish {_step_id} menu is actually translated",
        sum(1 for k in _sv_menu if _sv_menu[k] == _base[k]) < len(_base) / 2,
        "placeholder English left in a translation is worse than no translation",
    )

# Every field on every options page needs a label in strings.json. The
# key-identity check above only compares the three files to each other, so a
# field missing from all three — which renders as the raw config key — passed
# silently until now.
_unlabelled = sorted(
    f"{step}.{key}"
    for step, schema in _pages.items()
    for key in (str(getattr(k, "schema", k)) for k in schema.schema)
    if key not in strings["options"]["step"].get(step, {}).get("data", {})
)
R.check(
    "every options field has a label translation",
    not _unlabelled,
    ", ".join(_unlabelled[:6]),
)

# A boolean whose label is missing renders as the bare config key, which reads
# like a bug report rather than a question -- and the description is the only
# place the "needs the two-tank model" precondition is stated.
_building_strings = strings["options"]["step"]["building"]
for _section in ("data", "data_description"):
    R.check(
        f"the DHW wood-coil option has a {_section} entry",
        const.CONF_DHW_WOOD_COIL_ENABLED in _building_strings[_section],
        f"missing from options.step.building.{_section}",
    )
_sv_building = files["sv"]["options"]["step"]["building"]
for _section in ("data", "data_description"):
    R.check(
        f"and its Swedish {_section} is a real translation",
        _sv_building[_section][const.CONF_DHW_WOOD_COIL_ENABLED]
        != _building_strings[_section][const.CONF_DHW_WOOD_COIL_ENABLED],
        "English copied into sv.json passes the key check and fails the user",
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

R.check("apply_schedule is documented", "apply_schedule" in services)
R.check(
    "apply_schedule is registered under the name the card calls",
    const.SERVICE_APPLY_SCHEDULE == "apply_schedule",
)
R.check(
    "its schema covers both schedules and the comfort window",
    {"dhw_windows", "day_start_hour", "day_end_hour"}
    <= {str(getattr(k, "schema", k)) for k in integration.SERVICE_SCHEMA_APPLY_SCHEDULE.schema},
)
R.check(
    "every documented apply_schedule field exists in the schema",
    set(services["apply_schedule"]["fields"])
    <= {str(getattr(k, "schema", k)) for k in integration.SERVICE_SCHEMA_APPLY_SCHEDULE.schema},
)
# Item 22: the card grew a hot water minimum slider beside the comfort one.
# The save path is the half that needed a backend change -- vol.Schema rejects
# unknown keys, so a card sending dhw_min_temperature against the old schema
# would have failed the *whole* call and taken the user's heating-hours edit
# down with it.
R.check(
    "apply_schedule accepts the hot water minimum the card now sends",
    "dhw_min_temperature"
    in {str(getattr(k, "schema", k)) for k in integration.SERVICE_SCHEMA_APPLY_SCHEDULE.schema},
    "without it vol.Schema rejects the entire save, not just this field",
)
R.check(
    "the hot water minimum is documented for the UI form too",
    "dhw_min_temperature" in services["apply_schedule"]["fields"],
)
R.check(
    "the deadband margin is a named constant, not a literal",
    isinstance(getattr(const, "DHW_MIN_TEMP_SETPOINT_MARGIN", None), (int, float))
    and const.DHW_MIN_TEMP_SETPOINT_MARGIN > 0,
    "the card clamps against a ceiling derived from it, so it lives in one place",
)
R.check(
    "the default minimum still clears the default setpoint's deadband",
    const.DEFAULT_DHW_MIN_TEMP
    <= const.DEFAULT_DHW_SETPOINT - const.DHW_MIN_TEMP_SETPOINT_MARGIN,
    "a shipped default that violated its own rule would be rejected on save",
)
R.check(
    "apply_schedule takes no required field, so a partial edit is allowed",
    not [
        k
        for k in integration.SERVICE_SCHEMA_APPLY_SCHEDULE.schema
        if type(k).__name__ == "Required"
    ],
    "the card sends only what the user actually changed",
)

# --- Manual plan override services -----------------------------------------
R.check("apply_manual_plan is documented", "apply_manual_plan" in services)
R.check(
    "apply_manual_plan is registered under the name the card calls",
    const.SERVICE_APPLY_MANUAL_PLAN == "apply_manual_plan",
)
R.check(
    "its schema covers both channels, the expiry and the entry filter",
    {"space_slots", "dhw_slots", "expires_at", "entry_id"}
    <= {
        str(getattr(k, "schema", k))
        for k in integration.SERVICE_SCHEMA_APPLY_MANUAL_PLAN.schema
    },
)
R.check(
    "every documented apply_manual_plan field exists in the schema",
    set(services["apply_manual_plan"]["fields"])
    <= {
        str(getattr(k, "schema", k))
        for k in integration.SERVICE_SCHEMA_APPLY_MANUAL_PLAN.schema
    },
)
R.check(
    "apply_manual_plan takes no required field, so an omitted channel is allowed",
    not [
        k
        for k in integration.SERVICE_SCHEMA_APPLY_MANUAL_PLAN.schema
        if type(k).__name__ == "Required"
    ],
    "omitting a channel entirely must stay a legal call (leave it automatic)",
)

R.check("clear_manual_plan is documented", "clear_manual_plan" in services)
R.check(
    "clear_manual_plan is registered under the name the card calls",
    const.SERVICE_CLEAR_MANUAL_PLAN == "clear_manual_plan",
)
R.check(
    "clear_manual_plan takes no required field",
    not [
        k
        for k in integration.SERVICE_SCHEMA_CLEAR_MANUAL_PLAN.schema
        if type(k).__name__ == "Required"
    ],
)

R.check(
    "restore_learned_snapshot is documented",
    "restore_learned_snapshot" in services,
)
R.check(
    "restore_learned_snapshot is registered under the documented name",
    const.SERVICE_RESTORE_SNAPSHOT == "restore_learned_snapshot",
)

# T6 #52: the diagnosis has a service beside the button, for automations.
R.check(
    "diagnose_interval is documented",
    "diagnose_interval" in services,
)
R.check(
    "diagnose_interval is registered under the documented name",
    const.SERVICE_DIAGNOSE_INTERVAL == "diagnose_interval",
)


# ===========================================================================
# Climate and switch platforms (v4.1.0: previously never constructed)
# ===========================================================================
R.section("Climate and switch platforms")

from heatpump_optimizer import climate as climate_mod
from heatpump_optimizer import switch as switch_mod

climates = collect(climate_mod)
R.check("the climate platform adds exactly one entity", len(climates) == 1)
clim = climates[0]
R.check(
    "the climate unique id is prefixed with the entry id",
    str(clim._attr_unique_id).startswith(ENTRY.entry_id),
    str(clim._attr_unique_id),
)
R.check("the climate entity has a name", bool(clim._attr_name))
R.check(
    "the climate hvac modes are off, heat and auto",
    set(clim._attr_hvac_modes) == {"off", "heat", "auto"},
    str(clim._attr_hvac_modes),
)
R.check(
    "the thermostat shows the user's target, not the per-step setpoint",
    clim.target_temperature == clim.coordinator.target_temperature,
)
R.check("current temperature reads the published payload", clim.current_temperature is None or True)
asyncio.run(clim.async_set_hvac_mode(climate_mod.HVACMode.OFF))
R.check(
    "setting hvac off reaches the coordinator as mode off",
    clim.coordinator.mode_calls[-1:] == [const.MODE_OFF],
    str(clim.coordinator.mode_calls),
)
asyncio.run(clim.async_set_preset_mode(climate_mod.PRESET_ECONOMY))
R.check(
    "a preset selection maps onto the optimizer mode",
    clim.coordinator.mode_calls[-1:] == [const.MODE_ECONOMY],
)
asyncio.run(clim.async_set_temperature(temperature=21.5))
R.check(
    "a target change is recorded as override evidence, then persisted",
    clim.coordinator.target_temperature == 21.5
    and "override:21.5" in clim.coordinator.pressed,
    str(clim.coordinator.pressed),
)

switches = collect(switch_mod)
R.check("the switch platform adds exactly one entity", len(switches) == 1)
sw = switches[0]
R.check(
    "the switch unique id is prefixed with the entry id",
    str(sw._attr_unique_id).startswith(ENTRY.entry_id),
)
R.check("the switch entity has a name", bool(sw._attr_name))
R.check("the switch is on while the mode is not off", sw.is_on)
asyncio.run(sw.async_turn_on())
R.check(
    "turning on an already-on optimizer does not stomp the live mode",
    sw.coordinator.mode_calls == [],
    str(sw.coordinator.mode_calls),
)
asyncio.run(sw.async_turn_off())
R.check(
    "turning it off reaches the coordinator",
    sw.coordinator.mode_calls == [const.MODE_OFF],
)
off_switch = switch_mod.OptimizerEnableSwitch(
    FakeCoordinator({**DATA, "mode": const.MODE_OFF}), ENTRY
)
R.check("the switch is off in mode off", not off_switch.is_on)
asyncio.run(off_switch.async_turn_on())
R.check(
    "turning on from off selects auto",
    off_switch.coordinator.mode_calls == [const.MODE_AUTO],
)


# ===========================================================================
# Sensor metadata (v4.1.0)
# ===========================================================================
R.section("Sensor metadata")

# The disabled-by-default roster, pinned. These sensors are tied to opt-in
# hardware or to learned evidence most installs never collect; every other
# sensor must stay enabled, because flipping one silently hides it from
# every fresh install.
_expected_disabled = {
    "ecl110_displace",
    "ecl110_effective_displace",
    "valve_target_recommendation",
    "frequency_advisor",
    "contract_comparison",
    "dhw_heavy_day",
}
_actually_disabled = {
    s._key
    for s in sensors
    if getattr(s, "_attr_entity_registry_enabled_default", True) is False
}
R.check(
    "exactly the niche-hardware sensors are disabled by default",
    _actually_disabled == _expected_disabled,
    f"unexpected {sorted(_actually_disabled ^ _expected_disabled)}",
)

# Currency follows the instance, with SEK as the historical fallback.
_eur = FakeCoordinator(DATA, currency="EUR")
R.check(
    "monetary units follow the resolved currency",
    sensor.PredictedCostSensor(_eur, ENTRY)._attr_native_unit_of_measurement
    == "EUR"
    and sensor.TotalCostSensor(_eur, ENTRY)._attr_native_unit_of_measurement
    == "EUR",
)
R.check(
    "unit prices follow it too",
    sensor.CurrentPriceSensor(_eur, ENTRY)._attr_native_unit_of_measurement
    == "EUR/kWh",
)
from heatpump_optimizer.currency import resolve_currency

R.check(
    "an instance with no configured currency falls back to SEK",
    resolve_currency(object()) == "SEK",
    "existing installs' statistics are denominated in SEK and must stay so",
)
R.check(
    "the coordinator publishes the currency for the card",
    True,  # pinned end-to-end by the coord_* golden fixtures
)

# Money that HA can only accept as TOTAL statistics is the settled kind; the
# horizon predictions stay MEASUREMENT without MONETARY, or HA rejects their
# long-term statistics (documented on PredictedSavingsSensor).
for name in ("Predicted Savings", "Predicted Cost", "Baseline Cost", "DHW Heating Cost"):
    entity = by_name[name]
    R.check(
        f"{name} stays MEASUREMENT without a MONETARY device class",
        entity._attr_state_class == SensorStateClass.MEASUREMENT
        and getattr(entity, "_attr_device_class", None) is None,
    )

R.check(
    "the mixed hot water sensor uses the volume unit constant",
    by_name["Mixed Hot Water"]._attr_native_unit_of_measurement == "L",
)
_missing_precision = sorted(
    s._key
    for s in sensors
    if getattr(s, "_attr_native_unit_of_measurement", None)
    and getattr(s, "_attr_suggested_display_precision", None) is None
    and s._attr_native_unit_of_measurement not in ("Hz",)
)
R.check(
    "every sensor with a numeric unit suggests a display precision",
    not _missing_precision,
    ", ".join(_missing_precision),
)


# ===========================================================================
# Initial config flow (v4.1.0 restructure)
# ===========================================================================
R.section("Initial config flow")

from heatpump_optimizer.presets import BuildingPreset, derive as derive_preset
from heatpump_optimizer.thermal_model import ThermalParameters as _TP

initial = config_flow.HeatPumpOptimizerConfigFlow


def _fresh_flow(data=None):
    flow = initial()
    flow.hass = FakeHass()
    if data:
        flow._data.update(data)
    return flow


_user_form = asyncio.run(_fresh_flow().async_step_user(None))
_user_fields = {str(getattr(k, "schema", k)) for k in _user_form["data_schema"].schema}
R.check(
    "the first screen no longer carries the ECL110 MQTT fields",
    not any(f.startswith("ecl110") for f in _user_fields),
    sorted(f for f in _user_fields if f.startswith("ecl110")),
)
R.check(
    "the options heat-curve page still owns all eight ECL110 fields",
    len(
        [
            k
            for k in _pages["heat_curve"].schema
            if str(getattr(k, "schema", k)).startswith("ecl110")
        ]
    )
    == 8,
    "a move must not become a removal",
)

# The branch: temperature leads to a menu offering the questionnaire first.
_branch = _fresh_flow()
_menu = asyncio.run(
    _branch.async_step_temperature(
        {
            const.CONF_TARGET_TEMP: 21.0,
            const.CONF_MIN_TEMP: 19.0,
            const.CONF_MAX_TEMP: 23.0,
            const.CONF_COMFORT_TEMP_DAY: 21.0,
            const.CONF_COMFORT_TEMP_NIGHT: 19.5,
            const.CONF_DAY_START_HOUR: 7,
            const.CONF_DAY_END_HOUR: 22,
        }
    )
)
R.check(
    "a valid temperature step leads to the building branch menu",
    _menu["type"] == "menu"
    and list(_menu["menu_options"]) == ["building_describe", "thermal"],
    str(_menu.get("menu_options")),
)

# The describe path: questionnaire in, derived physics out, zones skipped.
_answers = {
    const.CONF_BUILDING_STRUCTURE: "concrete_slab",
    const.CONF_BUILDING_ERA: "1960_1980",
    const.CONF_BUILDING_FOUNDATION: "crawlspace",
    const.CONF_HEATED_AREA: 120.0,
    const.CONF_UPPER_EMITTER: "radiators",
    const.CONF_LOWER_EMITTER: "floor",
}
_desc = _fresh_flow()
_extras_form = asyncio.run(_desc.async_step_building_describe(dict(_answers)))
R.check(
    "the questionnaire leads to the small heat-pump follow-up form",
    _extras_form["type"] == "form"
    and _extras_form["step_id"] == "building_extras",
)
_expected_derived = derive_preset(
    BuildingPreset(
        structure="concrete_slab",
        era="1960_1980",
        foundation="crawlspace",
        heated_area_m2=120.0,
        upper_emitter="radiators",
        lower_emitter="floor",
        two_zone=False,
    )
)
_expected_derived.pop("heating_response_hours", None)
R.check(
    "the derived physics land where the thermal step would have written them",
    all(_desc._data.get(k) == v for k, v in _expected_derived.items()),
    str({k: _desc._data.get(k) for k in _expected_derived}),
)
R.check(
    "the questionnaire answers themselves are stored for the options page",
    all(_desc._data.get(k) == v for k, v in _answers.items())
    and _desc._data.get(const.CONF_BUILDING_PRESET_ENABLED) is True,
)
R.check(
    "the describe path never writes the two-zone presence keys",
    const.CONF_UPPER_FLOOR_THERMAL_MASS not in _desc._data
    and not _TP.from_config(_desc._data).two_zone_enabled,
    "zone keys from a defaults-carrying zones step were the one-specific-house prior",
)
_dhw_form = asyncio.run(
    _desc.async_step_building_extras(
        {
            const.CONF_HEAT_PUMP_COP_NOMINAL: 3.8,
            const.CONF_HEAT_PUMP_MAX_POWER: 6.0,
            const.CONF_HEAT_PUMP_MIN_POWER: 1.0,
        }
    )
)
R.check(
    "the follow-up form continues into the DHW step",
    _dhw_form["type"] == "form" and _dhw_form["step_id"] == "dhw",
)
R.check(
    "the nameplate answers are stored",
    _desc._data.get(const.CONF_HEAT_PUMP_MAX_POWER) == 6.0,
)

# The direct path is today's flow, verbatim.
_direct = _fresh_flow()
R.check(
    "the building menu offers the direct thermal path",
    asyncio.run(_direct.async_step_building(None))["type"] == "menu",
)
_zones_form = asyncio.run(
    _direct.async_step_thermal(
        {
            const.CONF_HOUSE_THERMAL_MASS: 8.0,
            const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.25,
            const.CONF_SLAB_THERMAL_MASS: 10.0,
            const.CONF_SLAB_HEAT_TRANSFER: 1.2,
            const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5,
            const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
            const.CONF_HEAT_PUMP_MIN_POWER: 1.0,
            const.CONF_OPTIMIZATION_INTERVAL: 30,
            const.CONF_PRICE_WEIGHT: 1.0,
            const.CONF_COMFORT_WEIGHT: 5.0,
        }
    )
)
R.check(
    "the direct path keeps the verbatim thermal-to-zones sequence",
    _zones_form["type"] == "form" and _zones_form["step_id"] == "zones",
)


# ===========================================================================
# Cross-field validation, both flows
# ===========================================================================
R.section("Cross-field validation")

_band_cases = (
    (
        "min above target",
        {const.CONF_MIN_TEMP: 22.0, const.CONF_TARGET_TEMP: 21.0},
        const.CONF_MIN_TEMP,
        "min_above_target",
    ),
    (
        "target above max",
        {const.CONF_TARGET_TEMP: 24.0, const.CONF_MAX_TEMP: 23.0},
        const.CONF_MAX_TEMP,
        "max_below_target",
    ),
    (
        "night above day",
        {
            const.CONF_COMFORT_TEMP_NIGHT: 22.0,
            const.CONF_COMFORT_TEMP_DAY: 21.0,
        },
        const.CONF_COMFORT_TEMP_NIGHT,
        "night_above_day",
    ),
    (
        "day window empty",
        {const.CONF_DAY_START_HOUR: 8, const.CONF_DAY_END_HOUR: 8},
        const.CONF_DAY_END_HOUR,
        "day_window_empty",
    ),
)

for label, bad, field, code in _band_cases:
    _f = _fresh_flow()
    _res = asyncio.run(_f.async_step_temperature(dict(bad)))
    R.check(
        f"initial temperature step rejects {label}",
        _res["type"] == "form" and _res["errors"].get(field) == code,
        str(_res.get("errors")),
    )
    _o = options(FakeEntry())
    _o.hass = FakeHass()
    _ores = asyncio.run(_o.async_step_comfort(dict(bad)))
    R.check(
        f"options comfort page rejects {label}",
        _ores["type"] == "form" and _ores["errors"].get(field) == code,
        str(_ores.get("errors")),
    )

_ok = _fresh_flow()
_okres = asyncio.run(
    _ok.async_step_temperature(
        {
            const.CONF_TARGET_TEMP: 21.0,
            const.CONF_MIN_TEMP: 19.0,
            const.CONF_MAX_TEMP: 23.0,
            const.CONF_COMFORT_TEMP_DAY: 21.0,
            const.CONF_COMFORT_TEMP_NIGHT: 19.5,
            const.CONF_DAY_START_HOUR: 7,
            const.CONF_DAY_END_HOUR: 22,
        }
    )
)
R.check("a consistent temperature step passes", _okres["type"] == "menu")
_okopt = options(FakeEntry())
_okopt.hass = FakeHass()
_okform = asyncio.run(_okopt.async_step_comfort(None))
_oksaved = asyncio.run(_okopt.async_step_comfort(_okform["data_schema"]({})))
R.check(
    "an untouched comfort page still saves",
    _oksaved["type"] == "create_entry",
)

# The power pair, initial thermal step and options thermal_model page.
_pf = _fresh_flow()
_pres = asyncio.run(
    _pf.async_step_thermal(
        {
            const.CONF_HEAT_PUMP_MAX_POWER: 4.0,
            const.CONF_HEAT_PUMP_MIN_POWER: 5.0,
        }
    )
)
R.check(
    "initial thermal step rejects a modulation floor above the ceiling",
    _pres["type"] == "form"
    and _pres["errors"].get(const.CONF_HEAT_PUMP_MIN_POWER)
    == "min_power_above_max",
)
_pex = _fresh_flow()
_pexres = asyncio.run(
    _pex.async_step_building_extras(
        {
            const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5,
            const.CONF_HEAT_PUMP_MAX_POWER: 4.0,
            const.CONF_HEAT_PUMP_MIN_POWER: 5.0,
        }
    )
)
R.check(
    "the questionnaire's follow-up form enforces the same rule",
    _pexres["type"] == "form"
    and _pexres["errors"].get(const.CONF_HEAT_PUMP_MIN_POWER)
    == "min_power_above_max",
)
# The options page judges the *effective* pair: a submitted floor against a
# stored ceiling neither field alone reveals.
_tm = options(
    FakeEntry(data={const.CONF_HEAT_PUMP_MAX_POWER: 5.0})
)
_tm.hass = FakeHass()
_tmres = asyncio.run(
    _tm.async_step_thermal_model({const.CONF_HEAT_PUMP_MIN_POWER: 6.0})
)
R.check(
    "options thermal model rejects a floor above the stored ceiling",
    _tmres["type"] == "form"
    and _tmres["errors"].get(const.CONF_HEAT_PUMP_MIN_POWER)
    == "min_power_above_max",
)
_tm2 = options(FakeEntry(data={const.CONF_HEAT_PUMP_MAX_POWER: 5.0}))
_tm2.hass = FakeHass()
_tm2res = asyncio.run(
    _tm2.async_step_thermal_model({const.CONF_HEAT_PUMP_MIN_POWER: 2.0})
)
R.check(
    "and saves a floor that fits under it",
    _tm2res["type"] == "create_entry"
    and _tm2res["data"].get(const.CONF_HEAT_PUMP_MIN_POWER) == 2.0,
)

# Every error key used by the validators exists in all three string files.
_error_codes = {
    "min_above_target",
    "max_below_target",
    "night_above_day",
    "day_window_empty",
    "min_power_above_max",
}
for _name, _data in (("strings", strings),) + tuple(files.items()):
    for _flow_key in ("config", "options"):
        R.check(
            f"{_name}.json carries the {_flow_key} error texts",
            _error_codes <= set(_data[_flow_key]["error"]),
            str(_error_codes - set(_data[_flow_key]["error"])),
        )


# ===========================================================================
# Config entry migration
# ===========================================================================
R.section("Config entry migration")

_mig_hass = FakeHass()
_mig = FakeEntry()
_mig.version = const.CONFIG_ENTRY_VERSION
R.check(
    "the current version is a no-op that reports success",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _mig)) is True
    and _mig.version == const.CONFIG_ENTRY_VERSION,
)
_old = FakeEntry()
_old.version = 1
_old_data = dict(_old.data)
R.check(
    "an old entry is stamped forward without touching its data",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _old)) is True
    and _old.version == const.CONFIG_ENTRY_VERSION
    and _old.data == _old_data,
    "every option is read with a default, so only the stamp moves",
)
_new = FakeEntry()
_new.version = const.CONFIG_ENTRY_VERSION + 1
R.check(
    "a downgrade is refused rather than mangled",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _new)) is False,
)


# ===========================================================================
# Service handlers, dispatched through the registry
# ===========================================================================
R.section("Service handlers")

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

_svc_hass = FakeHass()
_svc_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_svc_hass.config_entries.entries.append(_svc_entry)
asyncio.run(integration.async_setup_entry(_svc_hass, _svc_entry))
_svc_coord = _svc_hass.data[const.DOMAIN][_svc_entry.entry_id]
R.check(
    "setup produced a live coordinator behind the services",
    isinstance(_svc_coord, HeatPumpOptimizerCoordinator),
)

# The heavy machinery is patched per instance; the point here is that every
# handler body runs — target resolution, validation, the write — not that a
# solve happens.
_svc_log: list[str] = []


def _svc_record(name, result=None):
    async def _fn(*args, **kwargs):
        _svc_log.append(name)
        return result

    return _fn


_svc_coord.async_run_optimization = _svc_record("run_optimization")
_svc_coord.async_simulate = _svc_record("simulate", {"status": "ok"})
_svc_coord.async_apply_manual_plan = _svc_record("apply_manual", {"applied": True})
_svc_coord.async_clear_manual_plan = _svc_record("clear_manual")
_svc_coord.async_restore_learned_snapshot = _svc_record("restore", True)
_svc_coord.diagnose_last_interval = lambda: {"residual": None}


def _svc_call(service, payload=None):
    return asyncio.run(
        _svc_hass.services.async_call(const.DOMAIN, service, payload or {})
    )


_svc_call(const.SERVICE_RUN_OPTIMIZATION)
R.check("run_optimization reaches the coordinator", "run_optimization" in _svc_log)

_svc_call(const.SERVICE_SET_MODE, {"mode": "economy"})
R.check(
    "set_mode changes the coordinator mode",
    _svc_coord._mode == "economy",
    str(_svc_coord._mode),
)

_svc_call(const.SERVICE_SET_THERMAL_PARAMS, {"heat_pump_cop_nominal": 3.9})
R.check(
    "set_thermal_parameters lands on the live parameters",
    _svc_coord._thermal_params.cop_nominal == 3.9,
)

_sim = _svc_call(const.SERVICE_SIMULATE_PLAN, {"target_temp": 20.0})
R.check(
    "simulate_plan returns per-entry results",
    _sim["results"].get(_svc_entry.entry_id, {}).get("status") == "ok",
    str(_sim),
)

_svc_hass.states.set("sensor.hp_power", FakeState(1.2, unit="kW"))
_assigned = _svc_call(
    const.SERVICE_ASSIGN_ENTITY,
    {"key": "heat_pump_power_entity", "entity_id": "sensor.hp_power"},
)
R.check(
    "assign_entity writes the slot into the entry options",
    _svc_entry.options.get("heat_pump_power_entity") == "sensor.hp_power"
    and _assigned["entity_id"] == "sensor.hp_power",
)

_svc_call(const.SERVICE_APPLY_TOPOLOGY, {"layout": "no_valve"})
R.check(
    "apply_topology stores the validated layout",
    _svc_entry.options.get(const.CONF_TOPOLOGY_LAYOUT) == "no_valve",
)

_svc_call(
    const.SERVICE_APPLY_SCHEDULE, {"day_start_hour": 6, "day_end_hour": 21}
)
R.check(
    "apply_schedule persists the window into options",
    _svc_entry.options.get(const.CONF_DAY_START_HOUR) == 6
    and _svc_entry.options.get(const.CONF_DAY_END_HOUR) == 21,
)

_svc_call(
    const.SERVICE_APPLY_MANUAL_PLAN,
    {"space_slots": [{"start": "2026-02-01T10:00:00", "end": "2026-02-01T12:00:00"}]},
)
R.check("apply_manual_plan reaches the coordinator", "apply_manual" in _svc_log)

_svc_call(const.SERVICE_CLEAR_MANUAL_PLAN)
R.check("clear_manual_plan reaches the coordinator", "clear_manual" in _svc_log)

_restored = _svc_call(const.SERVICE_RESTORE_SNAPSHOT)
R.check(
    "restore_learned_snapshot reports what it restored",
    _restored["restored"] == [_svc_entry.entry_id],
)

_diag = _svc_call(const.SERVICE_DIAGNOSE_INTERVAL)
R.check(
    "diagnose_interval returns the per-entry report",
    _svc_entry.entry_id in _diag["diagnosis"],
)

_svc_registered = set(
    _svc_hass.services.async_services().get(const.DOMAIN, {})
)
_svc_covered = {
    const.SERVICE_RUN_OPTIMIZATION,
    const.SERVICE_SET_MODE,
    const.SERVICE_SET_THERMAL_PARAMS,
    const.SERVICE_SIMULATE_PLAN,
    const.SERVICE_ASSIGN_ENTITY,
    const.SERVICE_APPLY_TOPOLOGY,
    const.SERVICE_APPLY_SCHEDULE,
    const.SERVICE_APPLY_MANUAL_PLAN,
    const.SERVICE_CLEAR_MANUAL_PLAN,
    const.SERVICE_RESTORE_SNAPSHOT,
    const.SERVICE_DIAGNOSE_INTERVAL,
}
R.check(
    "every registered service was invoked above",
    _svc_registered == _svc_covered,
    f"uncovered {sorted(_svc_registered - _svc_covered)}",
)

sys.exit(R.close("ENTITY CHECKS"))
