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
import pathlib
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from harness import (
    FakeCoordinator,
    FakeEntry,
    FakeHass,
    FakeState,
    Results,
    ha_setup_component,
    ha_setup_entry,
    ha_unload_entry,
)

from homeassistant.components.sensor import SensorStateClass

import heatpump_optimizer as integration
from homeassistant import const as ha_const
from heatpump_optimizer import (
    binary_sensor,
    button,
    config_flow,
    const,
    sensor,
    topology,
)

R = Results("Entities and platforms")

ROOT = Path("custom_components/heatpump_optimizer")
ENTRY = FakeEntry()

# v5.0.0: display names live in the translation files, not in ``_attr_name``.
# The tests keep addressing entities by their English display name — resolved
# through strings.json exactly the way Home Assistant's frontend would — so a
# missing translation entry fails loudly here rather than rendering as a raw
# key in the UI.
_ENTITY_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]


def display_name(platform: str, entity) -> str:
    key = getattr(entity, "_attr_translation_key", None)
    return _ENTITY_STRINGS.get(platform, {}).get(key, {}).get(
        "name", f"<untranslated {platform}:{key}>"
    )


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
# Home Assistant's real ``Platform`` enum, transcribed from
# homeassistant/const.py. The stub in tests/hastub carries only the members
# this integration uses, and nothing stops it carrying one Home Assistant
# does not have -- which is exactly what happened: v6.3.1 added
# ``DIAGNOSTICS`` to the stub AND to PLATFORM_LIST, every gate stayed green,
# and the integration failed to import in Home Assistant with
# ``AttributeError: type object 'Platform' has no attribute 'DIAGNOSTICS'``.
# A stub may be SMALLER than the real thing; it may never be different.
_REAL_HA_PLATFORMS = frozenset(
    {
        "air_quality", "alarm_control_panel", "assist_satellite",
        "binary_sensor", "button", "calendar", "camera", "climate",
        "conversation", "cover", "date", "datetime", "device_tracker",
        "event", "fan", "geo_location", "humidifier", "image",
        "image_processing", "lawn_mower", "light", "lock", "media_player",
        "notify", "number", "remote", "scene", "select", "sensor", "siren",
        "stt", "switch", "text", "time", "todo", "tts", "update", "vacuum",
        "valve", "wake_word", "water_heater", "weather",
    }
)

_stub_platform_members = {
    name: value
    for name, value in vars(ha_const.Platform).items()
    if not name.startswith("_") and isinstance(value, str)
}
_invented = sorted(
    v for v in _stub_platform_members.values() if v not in _REAL_HA_PLATFORMS
)
R.check(
    "every member of the test stub's Platform exists in Home Assistant's own",
    not _invented,
    f"invented by the stub: {_invented}",
)
_unreal = sorted(p for p in const.PLATFORMS if p not in _REAL_HA_PLATFORMS)
R.check(
    "every entry of PLATFORMS is a real Home Assistant platform",
    not _unreal,
    f"not platforms Home Assistant knows: {_unreal}",
)
_unreal_list = sorted(p for p in platform_list if p not in _REAL_HA_PLATFORMS)
R.check(
    "every entry of PLATFORM_LIST is a real Home Assistant platform",
    not _unreal_list,
    f"not platforms Home Assistant knows: {_unreal_list}",
)
# Diagnostics is a module Home Assistant discovers by name, never a platform
# to forward. Forwarding it is what broke setup in v6.3.1.
R.check(
    "diagnostics.py exists",
    (
        pathlib.Path(__file__).resolve().parents[1]
        / "custom_components"
        / "heatpump_optimizer"
        / "diagnostics.py"
    ).is_file(),
)
R.check(
    "diagnostics is NOT forwarded as a platform",
    "diagnostics" not in const.PLATFORMS and "diagnostics" not in platform_list,
    f"PLATFORMS={const.PLATFORMS} PLATFORM_LIST={platform_list}",
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

# parallel-updates (Silver, #184): every platform states how many of its
# entities may update or act at once, read from the module so a platform
# that drops the line fails here rather than silently taking Home
# Assistant's default. The two coordinator-fed read-only platforms declare
# 0 -- the coordinator already serialises the inbound refresh and nothing
# outbound exists to throttle. The three that act (a button press, the mode
# switch, the thermostat's setpoint and mode) declare 1: every action lands
# on the coordinator, which commands one heat pump, and two of them racing
# is two commands to one machine.
from heatpump_optimizer import climate as _climate_platform
from heatpump_optimizer import switch as _switch_platform

for _module, _expected in (
    (sensor, 0),
    (binary_sensor, 0),
    (button, 1),
    (_climate_platform, 1),
    (_switch_platform, 1),
):
    _platform_name = _module.__name__.rsplit(".", 1)[-1]
    R.check(
        f"the {_platform_name} platform declares PARALLEL_UPDATES = {_expected}",
        getattr(_module, "PARALLEL_UPDATES", None) == _expected,
        f"PARALLEL_UPDATES is {getattr(_module, 'PARALLEL_UPDATES', '<undeclared>')!r}",
    )


def collect(module, data=None, coordinator=None):
    """Instantiate every entity a platform would add, for a given data dict.

    Driven through the real ``async_setup_entry`` rather than by listing the
    classes here, so a new entity that is written but never registered still
    shows up as missing — and so a whole-platform sweep cannot quietly miss
    the one entity nobody thought to name.
    """
    added = []

    def add_entities(entities):
        added.extend(entities)

    if coordinator is None:
        coordinator = FakeCoordinator(DATA if data is None else data)
        # The month figures and the counting-since date the accumulators
        # publish (#4): set here so every entity test sees a coordinator
        # that has been running, not one booted this minute.
        coordinator._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    hass = FakeHass()
    # Where a platform finds its coordinator: on the entry, as runtime_data
    # (runtime-data, Bronze). Nothing is put in hass.data -- a platform that
    # still looked there would find nothing and fail here.
    ENTRY.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(hass, ENTRY, add_entities))
    return added


# A representative published payload, covering every key the new entities read.
DATA = {
    "energy_totals_counting_since": "2026-08-15",
    "mode": "auto",
    "indoor_temperature": 21.3,
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
    # Every gate the entities read is satisfied here, so an entity that is
    # unavailable against this payload is unavailable for a reason of its own
    # -- which is what makes the coordinator-failure sweep below meaningful.
    "dhw_enabled": True,
    "reading_ok": {
        "upper_floor_temperature": True,
        "lower_floor_temperature": True,
        "floor_return_temperature": True,
        "slab_temperature": True,
        "buffer_tank_temperature": True,
        "dhw_temperature": True,
    },
    "contract_comparison": {
        "load_profile_value_per_kwh": -0.031,
        "months": 2,
    },
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
    # The horizon the plan sensors publish (#4): the projection attribute
    # reads it off the optimizer's own configuration.
    "horizon_hours": 24.0,
}


# ===========================================================================
# Sensors
# ===========================================================================
R.section("Sensors")

sensors = collect(sensor)
by_name = {display_name("sensor", s): s for s in sensors}
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

# docs-removal-instructions (Bronze, #183): the README says how to remove the
# integration and what removal leaves behind, in the Installation section
# next to how to install it. Two of its claims are checked against the code
# rather than trusted: the store files it lists under `.storage/` are the
# coordinator's own Store keys (the stub Store records its key), and the
# Home Assistant floor it states is the one hacs.json declares -- both are
# numbers a user acts on, and both drift silently otherwise.
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _Coord
from homeassistant.helpers.storage import Store as _Store

_removal = _re.search(
    r"^### Removal\n(.*?)(?=^## |^### )", readme, _re.M | _re.S
)
_removal_text = _removal.group(1) if _removal else ""
R.check(
    "the README has a Removal section, under Installation",
    _removal is not None
    and readme.index("## Installation")
    < readme.index("### Removal")
    < readme.index("## Quick start"),
)
R.check(
    "it names the standard delete path",
    "Devices & services" in _removal_text and "Delete" in _removal_text,
)
R.check(
    "it says the card's Lovelace resource stays behind, and where to remove it",
    "Resources" in _removal_text and "heatpump-optimizer-card.js" in _removal_text,
)
R.check(
    "it says the code is uninstalled through HACS or by deleting the folder",
    "HACS" in _removal_text and "custom_components/heatpump_optimizer" in _removal_text,
)
_removal_coord = _Coord(
    FakeHass(),
    FakeEntry(
        data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
    ),
)
_store_prefix = f"{const.DOMAIN}_{_removal_coord.entry.entry_id}_"
_store_suffixes = {
    value._key.removeprefix(_store_prefix)
    for value in vars(_removal_coord).values()
    if isinstance(value, _Store) and value._key.startswith(_store_prefix)
}
_listed_suffixes = set(
    _re.findall(r"heatpump_optimizer_<entry id>_(\w+)", _removal_text)
)
R.check(
    "the store files it says are left under .storage are exactly the ones the coordinator keeps",
    _store_suffixes and _listed_suffixes == _store_suffixes,
    f"documented {sorted(_listed_suffixes)}, code keeps {sorted(_store_suffixes)}",
)
_hacs_floor = json.loads(Path("hacs.json").read_text())["homeassistant"]
R.check(
    "the README's requirement line states the Home Assistant floor hacs.json declares",
    f"Home Assistant {_hacs_floor} or newer" in readme,
    f"hacs.json says {_hacs_floor}",
)
R.check(
    "and the README badge agrees",
    f"Home%20Assistant-{_hacs_floor}%2B" in readme,
)
# issue #227 (hacs.json floor): ConfigEntry.runtime_data (read by every
# platform since B5, #207) is the only API in this integration with a
# minimum Home Assistant release established from repo evidence --
# tests/hastub/homeassistant/config_entries.py's docstring ("Mirrored from
# Home Assistant 2024.6.0 ... the release that introduced
# ConfigEntry.runtime_data") and RELEASE_NOTES.md's v6.3.0 entry ("verified
# against the upstream tags: absent at 2024.5.0, present ... at 2024.6.0").
# The reconfigure flow (#196) has since established its minimum the way
# this comment asked: upstream homeassistant/config_entries.py carries
# SOURCE_RECONFIGURE, async_start_reconfigure and ConfigEntry.
# supports_reconfigure from 2024.4.0 (verified against the 2024.4.0 and
# 2024.6.0 tags when #196 landed), so the 2024.6.0 floor below covers it
# and no bump was needed. Config-flow sections and icon translations
# (#189) still have no minimum established anywhere in this repository.
_hacs_floor_tuple = tuple(int(part) for part in _hacs_floor.split("."))
R.check(
    "hacs.json's Home Assistant floor is at least 2024.6.0 (ConfigEntry.runtime_data, the one API establishable from repo evidence)",
    _hacs_floor_tuple >= (2024, 6, 0),
    f"hacs.json says {_hacs_floor}",
)

for name in (
    "Measured Power",
    "Observed COP",
    "Space Heating Energy (lifetime)",
    "DHW Energy (lifetime)",
    "Total Energy (lifetime)",
    "Space Heating Cost (lifetime)",
    "DHW Cost (lifetime)",
    "Total Heating Cost (lifetime)",
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
    "Space Heating Energy (lifetime)",
    "DHW Energy (lifetime)",
    "Total Energy (lifetime)",
):
    R.check(
        f"{name} is TOTAL_INCREASING",
        by_name[name]._attr_state_class == SensorStateClass.TOTAL_INCREASING,
    )
# Money is different: Home Assistant only accepts state class TOTAL for
# device class MONETARY, and long-term statistics need a currency unit.
# TOTAL_INCREASING here (as previously pinned) made HA reject the statistics.
for name in (
    "Space Heating Cost (lifetime)",
    "DHW Cost (lifetime)",
    "Total Heating Cost (lifetime)",
):
    R.check(
        f"{name} is a TOTAL in a currency",
        by_name[name]._attr_state_class == SensorStateClass.TOTAL
        and by_name[name]._attr_native_unit_of_measurement == "SEK",
    )
R.check(
    "the DHW/space split is described rather than implied",
    "apportioned"
    in by_name["Space Heating Energy (lifetime)"].extra_state_attributes["split_method"],
    "one meter cannot separate two circuits, and pretending otherwise is worse",
)
R.check(
    "the energy split reconciles with the total",
    abs(
        by_name["Space Heating Energy (lifetime)"].native_value
        + by_name["DHW Energy (lifetime)"].native_value
        - by_name["Total Energy (lifetime)"].native_value
    )
    < 1e-6,
)
# The period clarity (owner report #4): a lifetime number that states no
# period reads as "very high", and the plan sensors' horizon numbers read
# as the same figure with a different magnitude. Both now say what they
# are, in the name and in the attributes.
_hwc = by_name["DHW Cost (lifetime)"].extra_state_attributes
R.check(
    "the accumulators state their period in words",
    "never reset" in _hwc["period"] and "whole history" in _hwc["period"],
    _hwc["period"],
)
R.check(
    "and carry this month's figures next to the lifetime state",
    _hwc["this_month_kwh"] == 41.5 and _hwc["this_month_cost"] == 62.25,
    str({k: _hwc.get(k) for k in ("this_month_kwh", "this_month_cost")}),
)
R.check(
    "and the date they started counting, when the store has one",
    _hwc["counting_since"] == "2026-08-15",
    str(_hwc.get("counting_since")),
)
_plan_attrs = by_name["DHW Heating Plan (next 24 h)"].extra_state_attributes
R.check(
    "the plan sensors say their numbers are projections, not history",
    "recomputed" in _plan_attrs["projection"]
    and _plan_attrs["horizon_hours"] == 24.0,
    _plan_attrs["projection"],
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
    by_name["DHW Mixed Water"].native_value == 450.0
    and by_name["DHW Mixed Water"].extra_state_attributes["shower_minutes"]
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
space_plan = by_name["Space Heating Plan (next 24 h)"]
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

# The schedule editor edits the CONFIGURED hot-water windows, which are not
# what `dhw_windows` carries (the plan's reading: learned windows when none
# are configured, one day's set of a weekly spec). The configuration travels
# on its own attribute, in the spec grammar, on both paths and unrecorded.
dhw_plan = by_name["DHW Heating Plan (next 24 h)"]
R.check(
    "the plan sensor publishes the configured hot-water windows for the card",
    dhw_plan.extra_state_attributes.get("dhw_windows_spec")
    == dhw_plan.coordinator.configured_dhw_windows()
    == "weekdays 06:00-08:30, weekend 08:00-09:30",
    "the editor would otherwise show a weekly schedule flattened to one day",
)
R.check(
    "and it differs from the plan's own reading of the windows",
    dhw_plan.extra_state_attributes.get("dhw_windows")
    != dhw_plan.extra_state_attributes.get("dhw_windows_spec"),
)
R.check(
    "and publishes it before the first plan exists",
    sensor.DHWHeatingPlanSensor(no_plan_coord, ENTRY).extra_state_attributes.get(
        "dhw_windows_spec"
    )
    == no_plan_coord.configured_dhw_windows(),
)
R.check(
    "and keeps it out of the recorder, like the windows it explains",
    "dhw_windows_spec" in sensor._PlanSensorBase._unrecorded_attributes,
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
# Sensors say what they actually know
# ===========================================================================
R.section("A published number is a reading or it is nothing")

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.tariff import CapacityTariff, PeakTracker
from heatpump_optimizer.thermal_model import ThermalState

# These go through a REAL coordinator rather than a hand-written dict. The
# question being asked is precisely "did this number come from an entity or
# from `ThermalState`'s constructor", and a fixture that writes the number
# itself cannot answer it: it would pass just as happily against the bug.
_DEFAULTS = ThermalState()
#: Older than every ``INPUT_MAX_AGE_MINUTES`` limit in the package.
_STALE_WHEN = datetime.now(UTC) - timedelta(hours=10)


def _honest_coordinator(extra_config=None, states=None, dhw=True):
    """A coordinator that has completed one real input-read cycle."""
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    for entity_id, state in (states or {}).items():
        hass.states.set(entity_id, state)
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    if dhw:
        # Presence of a tank volume is what makes `dhw_enabled` true, so hot
        # water is on here without a tank thermometer being configured --
        # which is the ordinary install, not a corner case.
        config[const.CONF_DHW_TANK_VOLUME] = 180.0
    config.update(extra_config or {})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    return hass, coord, coord._build_data_dict()


_blind_hass, _blind_coord, _blind = _honest_coordinator()
_blind_fake = FakeCoordinator(_blind)

# The premise, stated in production's own terms: with nothing sensing the
# tank, the buffer or the lower floor, what gets published IS the dataclass
# default. No magic numbers here -- they are read off `ThermalState()`.
R.check(
    "with no tank sensor the published tank temperature is the model default",
    _blind["dhw_temperature"] == _DEFAULTS.dhw_temperature,
    f'{_blind["dhw_temperature"]} vs default {_DEFAULTS.dhw_temperature}',
)
R.check(
    "with no buffer probe the published buffer temperature is the default too",
    _blind["buffer_tank_temperature"] == _DEFAULTS.buffer_tank_temperature,
    f'{_blind["buffer_tank_temperature"]}',
)
R.check(
    "with no lower-floor sensor the lower floor IS the indoor temperature",
    _blind["lower_floor_temperature"] == _blind["indoor_temperature"],
    f'{_blind["lower_floor_temperature"]} vs {_blind["indoor_temperature"]}',
)
R.check(
    "and the upper floor is the indoor temperature, always",
    _blind["upper_floor_temperature"] == _blind["indoor_temperature"],
    "there is no upper-floor input anywhere in the package",
)

# The fix: those numbers stop claiming to be measurements.
for _cls, _label in (
    (sensor.DHWTemperatureSensor, "the hot water tank"),
    (sensor.BufferTankTempSensor, "the buffer tank"),
    (sensor.SlabTempSensor, "the slab"),
    (sensor.LowerFloorTempSensor, "the lower floor"),
    (sensor.FloorReturnTempSensor, "the floor return"),
):
    R.check(
        f"nothing reading {_label} means that sensor is unavailable",
        not _cls(_blind_fake, ENTRY).available,
        f"{_cls.__name__} published {_cls(_blind_fake, ENTRY).native_value!r}",
    )
R.check(
    "the indoor sensor, which IS read, keeps reporting",
    sensor.IndoorTempSensor(_blind_fake, ENTRY).available
    and sensor.IndoorTempSensor(_blind_fake, ENTRY).native_value == 21.4,
    "gating everything would be as useless as gating nothing",
)
# The upper floor is the one entity that is not gated on an input of its own,
# because it has never had one: it follows the indoor thermometer, so it lives
# and dies with the Indoor Temperature sensor rather than holding 21.4 on its
# own after that thermometer stops reporting.
_indoor_stale_hass, _indoor_stale_coord, _indoor_stale = _honest_coordinator(
    states={"sensor.indoor": FakeState("21.4", last_updated=_STALE_WHEN)}
)
_indoor_stale_fake = FakeCoordinator(_indoor_stale)
R.check(
    "the upper floor is available exactly while the indoor thermometer reads",
    sensor.UpperFloorTempSensor(_blind_fake, ENTRY).available
    and not sensor.UpperFloorTempSensor(_indoor_stale_fake, ENTRY).available,
    "it is the indoor reading under another name, and now says so",
)
R.check(
    "and a stale indoor thermometer publishes the model default, as before",
    _indoor_stale["indoor_temperature"] == _DEFAULTS.room_temperature,
    "Indoor Temperature is deliberately left ungated here: it is the "
    "integration's primary entity and its staleness already has a home in "
    "the Input Problem binary sensor and the repair issues",
)
R.check(
    "the upper floor names where its number comes from",
    sensor.UpperFloorTempSensor(_blind_fake, ENTRY).extra_state_attributes.get(
        "source"
    )
    == "indoor_temperature",
    "two entities carrying one number look like corroboration until one owns up",
)

# Wire the thermometers up and the same entities come back to life, with the
# sensors' values rather than the defaults.
_sensed_hass, _sensed_coord, _sensed = _honest_coordinator(
    {
        const.CONF_DHW_TEMP_ENTITY: "sensor.tank",
        const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
        const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.return",
        const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.downstairs",
    },
    {
        "sensor.tank": FakeState("48.2"),
        "sensor.buffer": FakeState("36.5"),
        "sensor.return": FakeState("27.5"),
        "sensor.downstairs": FakeState("20.1"),
    },
)
_sensed_fake = FakeCoordinator(_sensed)
for _cls, _expected in (
    (sensor.DHWTemperatureSensor, 48.2),
    (sensor.BufferTankTempSensor, 36.5),
    (sensor.FloorReturnTempSensor, 27.5),
    (sensor.LowerFloorTempSensor, 20.1),
):
    _entity = _cls(_sensed_fake, ENTRY)
    R.check(
        f"{_cls.__name__} reports its sensor once one is configured",
        _entity.available and _entity.native_value == _expected,
        f"available={_entity.available} value={_entity.native_value!r}",
    )
R.check(
    "the slab estimate lives while the return temperature drives it",
    sensor.SlabTempSensor(_sensed_fake, ENTRY).available,
    "the slab is integrated from the floor return, never sensed directly",
)

# The case availability exists for: the sensor was configured and has stopped
# reporting. The published number does not change -- the coordinator keeps the
# last good read -- so nothing except availability can tell the two apart.
_stale_hass, _stale_coord, _ = _honest_coordinator(
    {const.CONF_DHW_TEMP_ENTITY: "sensor.tank"},
    {"sensor.tank": FakeState("48.2")},
)
# One good cycle, then the thermometer stops reporting. The coordinator holds
# the last good value, which is the whole problem.
_stale_hass.states.set("sensor.tank", FakeState("48.2", last_updated=_STALE_WHEN))
asyncio.run(_stale_coord._update_current_state())
_stale = _stale_coord._build_data_dict()
R.check(
    "a stale tank sensor still publishes its last number",
    _stale["dhw_temperature"] == 48.2,
    f'{_stale["dhw_temperature"]!r}',
)
R.check(
    "but the entity goes unavailable rather than holding it out as current",
    not sensor.DHWTemperatureSensor(FakeCoordinator(_stale), ENTRY).available,
    "a thermometer that died in January reads 48.2 all spring",
)

# Round-2 audit, D8-01. The gate above protects the temperature sensor and
# stops there. Mixed Hot Water is the SAME number in shower clothes --
# V*(T_tank - T_inlet)/(40 - T_inlet) litres -- and it was ungated, so on the
# install the config flow produces with every form left untouched (no tank
# thermometer; hot water on with a 200 L tank) it published 270 litres and
# 33.8 shower minutes, rock-steady across cycles, while DHW Temperature beside
# it was correctly unavailable and the input-problem binary sensor read "ok".
#
# A litre count carries a state_class, so Home Assistant writes long-term
# statistics for it: the constructor default does not merely show once, it is
# recorded as history. Availability is the mechanism, exactly as it is for the
# temperature the litres are computed from.
_mixed_stale = sensor.MixedHotWaterSensor(FakeCoordinator(_stale), ENTRY)
R.check(
    "mixed hot water follows the thermometer it is computed from",
    not _mixed_stale.available,
    "270 litres of shower water derived from a tank reading nobody trusts",
)
# And the null control: with the reading good, it is available as before, so
# the gate is not simply switching the entity off.
_mixed_ok = sensor.MixedHotWaterSensor(FakeCoordinator(DATA), ENTRY)
R.check(
    "and it is still available when the tank really is being read",
    _mixed_ok.available,
    "the gate must not take the sensor away from installs that have a probe",
)

# --- hot water that is not configured is not a zero -------------------------
R.section("Hot water entities exist only where there is hot water")

_no_dhw_hass, _no_dhw_coord, _no_dhw = _honest_coordinator(dhw=False)
R.check(
    "a config with no hot water publishes dhw_enabled False",
    _no_dhw.get("dhw_enabled") is False,
    str(_no_dhw.get("dhw_enabled")),
)
_no_dhw_fake = FakeCoordinator(_no_dhw)
_dhw_on_fake = FakeCoordinator(DATA)
for _cls in (
    sensor.DHWEnergySensor,
    sensor.DHWCostSensor,
    sensor.DHWTemperatureSensor,
    sensor.DHWScheduleSensor,
    sensor.DHWHeatingCostSensor,
    sensor.DHWHeatingPlanSensor,
):
    R.check(
        f"{_cls.__name__} is unavailable with hot water switched off",
        not _cls(_no_dhw_fake, ENTRY).available,
        f"published {_cls(_no_dhw_fake, ENTRY).native_value!r} instead",
    )
R.check(
    "the Energy dashboard is offered a hot water meter only when there is one",
    sensor.DHWEnergySensor(_no_dhw_fake, ENTRY).native_value == 0.0
    and not sensor.DHWEnergySensor(_no_dhw_fake, ENTRY).available,
    "a flat zero forever looks exactly like a working meter on an idle pump",
)
for _cls in (
    sensor.DHWEnergySensor,
    sensor.DHWCostSensor,
    sensor.DHWScheduleSensor,
    sensor.DHWHeatingCostSensor,
    sensor.DHWHeatingPlanSensor,
    sensor.DHWTemperatureSensor,
):
    R.check(
        f"{_cls.__name__} is available again once hot water is configured",
        _cls(_dhw_on_fake, ENTRY).available,
        "the gate must be able to open, or it is not a gate",
    )

# --- unknown-versus-broken --------------------------------------------------
R.section("Waiting for evidence is not the same as broken")

for _cls, _key, _missing, _code in (
    (
        sensor.ObservedCOPSensor,
        "measured_cop",
        None,
        "first_cop_sample",
    ),
    (
        sensor.FrequencyAdvisorSensor,
        "freq_control",
        {"mode": "observe", "recommended_hz": None},
        "first_frequency_map_sample",
    ),
    (
        sensor.ContractComparisonSensor,
        "contract_comparison",
        {"months": 0},
        "settled_metered_month",
    ),
):
    _waiting = _cls(FakeCoordinator({**DATA, _key: _missing}), ENTRY)
    R.check(
        f"{_cls.__name__} is unavailable while its evidence is missing",
        not _waiting.available,
        "Unknown reads as broken; unavailable reads as 'nothing yet'",
    )
    R.check(
        f"{_cls.__name__} names what it is waiting for",
        _waiting.extra_state_attributes.get("waiting_for") == _code,
        str(_waiting.extra_state_attributes.get("waiting_for")),
    )
    _ready = _cls(FakeCoordinator(DATA), ENTRY)
    R.check(
        f"{_cls.__name__} is available, and waiting for nothing, once it lands",
        _ready.available
        and _ready.extra_state_attributes.get("waiting_for") is None,
        f"available={_ready.available} value={_ready.native_value!r}",
    )
R.check(
    "an unconfigured source is distinguished from a missing sample",
    sensor.ObservedCOPSensor(
        FakeCoordinator({**DATA, "measured_power_available": False}), ENTRY
    ).extra_state_attributes.get("waiting_for")
    == "measured_power_entity",
)

# --- a failed refresh reaches every entity ----------------------------------
R.section("A failed refresh reaches every entity")

# `CoordinatorEntity.available` is False after a failed update. An override
# that forgets to conjoin it replaces that answer instead of narrowing it, so
# the entity keeps publishing a number from a coordinator that has stopped
# updating -- and nothing anywhere says so.
#
# Two-sided on purpose. The first half proves DATA satisfies every gate, so
# the second half can only be failing for the reason it claims. Without it,
# deleting a `super().available and` would still pass: everything would be
# unavailable for its own reasons and the sweep would never notice.
_healthy = FakeCoordinator(DATA)
_broken = FakeCoordinator(DATA)
_broken.last_update_success = False
# Every platform is in the roster (#295). The two action buttons were once
# held out of it on the theory that "run an optimization now" is exactly what
# a user reaches for when the last refresh failed -- but a press during an
# outage lands on the same failing fetch while the button reports ready, so
# the round-2 panel ruled the omission the same oversight, not a choice.
# Every entity class is driven through its platform's real setup, so a new
# entity nobody thought to name cannot sit this sweep out either.
_dead_when_healthy = []
_alive_when_broken = []
for _module in (sensor, binary_sensor, button, _climate_platform, _switch_platform):
    for _entity in collect(_module, coordinator=_healthy):
        if not _entity.available:
            _dead_when_healthy.append(type(_entity).__name__)
    for _entity in collect(_module, coordinator=_broken):
        if _entity.available:
            _alive_when_broken.append(type(_entity).__name__)
R.check(
    "every entity is available against a payload that satisfies every gate",
    not _dead_when_healthy,
    "; ".join(sorted(set(_dead_when_healthy))),
)
R.check(
    "and none of them is available after a failed coordinator refresh",
    not _alive_when_broken,
    "; ".join(sorted(set(_alive_when_broken))),
)


# ===========================================================================
# Nothing non-finite, and nothing unlabelled, reaches a published state
# ===========================================================================
R.section("No published attribute is non-finite, in any configuration")

import math as _math

from homeassistant.components.sensor import DEVICE_CLASS_STATE_CLASSES

_INF = float("inf")


def _non_finite(node, path, found):
    """Every float in a published payload, checked for finiteness."""
    if isinstance(node, dict):
        for key, value in node.items():
            _non_finite(value, f"{path}.{key}", found)
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            _non_finite(value, f"{path}[{index}]", found)
    elif isinstance(node, float) and not _math.isfinite(node):
        found.append(f"{path} = {node!r}")


# The configurations worth sweeping are the ones that actually produce a
# non-finite number in production, plus the empty ones that produce nothing.
# `peak_threshold_kw` is +inf on the 1st of every month for every install with
# a capacity tariff, straight out of `PeakTracker.threshold_kw`.
_CONFIGURATIONS = {
    "the representative payload": DATA,
    "before the first update": None,
    "an empty payload": {},
    "the 1st of the month, capacity tariff, no peak reference yet": {
        **DATA,
        "peak_threshold_kw": PeakTracker().threshold_kw(
            CapacityTariff(enabled=True, price_per_kw=60.0)
        ),
    },
    "a nan sneaking through a learner": {
        **DATA,
        "comfort_weight": float("nan"),
        "battery": {**DATA["battery"], "hours_of_autonomy": _INF},
        "pv": {**DATA["pv"], "forecast_surplus_kwh": -_INF},
        "power_headroom": {
            **DATA["power_headroom"],
            "horizon_headroom_kw": [7.3, _INF, float("nan")],
        },
    },
}

_offenders = []
for _label, _payload in _CONFIGURATIONS.items():
    for _module in (sensor, binary_sensor, button):
        for _entity in collect(_module, data=_payload):
            _name = type(_entity).__name__
            _non_finite(
                getattr(_entity, "native_value", None),
                f"{_label}: {_name}.native_value",
                _offenders,
            )
            # Not every platform entity defines extra attributes; the ones
            # that do are where the non-finite numbers actually ride.
            _non_finite(
                getattr(_entity, "extra_state_attributes", None),
                f"{_label}: {_name}",
                _offenders,
            )
R.check(
    "no entity publishes a non-finite state or attribute, in any configuration",
    not _offenders,
    "; ".join(_offenders[:6]),
)
# ... and the sweep is only worth anything if the fixture really does carry
# infinities into the entities. This is the half that stops it going vacuous
# if someone later "tidies" the payloads.
R.check(
    "the sweep's fixtures really do feed non-finite numbers in",
    _math.isinf(
        _CONFIGURATIONS[
            "the 1st of the month, capacity tariff, no peak reference yet"
        ]["peak_threshold_kw"]
    )
    and _math.isnan(_CONFIGURATIONS["a nan sneaking through a learner"]["comfort_weight"]),
    "a sweep over finite fixtures proves nothing",
)
# The specific one the frontend and the recorder disagree about: orjson
# writes inf as null, so the database and a Jinja template already saw two
# different values for this attribute.
_inf_peak = sensor.MonthlyPeakSensor(
    FakeCoordinator(
        {
            "peak_tariff_enabled": True,
            "peak_threshold_kw": PeakTracker().threshold_kw(
                CapacityTariff(enabled=True, price_per_kw=60.0)
            ),
        }
    ),
    ENTRY,
)
R.check(
    "the free headroom threshold is None, not +inf, when there is no reference",
    _inf_peak.extra_state_attributes["free_headroom_threshold_kw"] is None,
    repr(_inf_peak.extra_state_attributes["free_headroom_threshold_kw"]),
)
R.check(
    "and a real threshold still comes through untouched",
    by_name["Monthly Peak Power"].extra_state_attributes[
        "free_headroom_threshold_kw"
    ]
    == 6.5,
    "mapping every number to None would pass the sweep and publish nothing",
)

# --- the headroom entity must not vanish on the 1st -------------------------
R.section("Power headroom survives the turn of the month")

_cap_only = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 60.0,
    # The default. A capacity tariff does not imply a configured fuse.
    const.CONF_MAIN_FUSE_A: 0,
}
_cap_hass = FakeHass()
_cap_hass.states.set("sensor.indoor", FakeState("21.4"))
_cap_hass.states.set("sensor.outdoor", FakeState("-3.0"))
_cap_coord = HeatPumpOptimizerCoordinator(_cap_hass, FakeEntry(data=_cap_only))
asyncio.run(_cap_coord._update_current_state())
R.check(
    "the tracker really has no reference peak at the turn of the month",
    not _cap_coord._peak_tracker.peaks
    and _math.isinf(
        _cap_coord._peak_tracker.threshold_kw(_cap_coord._capacity_tariff())
    ),
    "this is the state every install is in on the 1st",
)
_fresh_month = _cap_coord._power_headroom()
R.check(
    "the headroom entity still exists on the 1st with no fuse configured",
    _fresh_month.get("available") is True,
    str(_fresh_month),
)
R.check(
    "and answers 0 kW free, because the month's bill is set from zero",
    _fresh_month.get("headroom_kw") == 0.0
    and _fresh_month.get("limit_source")
    == "capacity tariff with no peak reference yet",
    str(_fresh_month),
)
R.check(
    "the headroom sensor is available and numeric there",
    sensor.PowerHeadroomSensor(
        FakeCoordinator({"power_headroom": _fresh_month}), ENTRY
    ).available
    and sensor.PowerHeadroomSensor(
        FakeCoordinator({"power_headroom": _fresh_month}), ENTRY
    ).native_value
    == 0.0,
    "an EV charger's dynamic limit used to lose its input every month",
)
# Once a window closes the real threshold takes over again.
_closing = datetime(2026, 2, 1, 0, 5)
for _i in range(4):
    _cap_coord._peak_tracker.observe(
        _closing + timedelta(minutes=15 * _i), 5.0, _cap_coord._capacity_tariff()
    )
_cap_coord._peak_tracker.observe(
    _closing + timedelta(hours=1, minutes=5), 5.0, _cap_coord._capacity_tariff()
)
_settled = _cap_coord._power_headroom()
R.check(
    "and the measured threshold takes over once a window has closed",
    _settled.get("limit_kw") == 5.0
    and _settled.get("limit_source") == "capacity threshold",
    str(_settled),
)
# Nothing configured at all is still nothing to say.
_bare_hass = FakeHass()
_bare_hass.states.set("sensor.indoor", FakeState("21.4"))
_bare_hass.states.set("sensor.outdoor", FakeState("-3.0"))
_bare_coord = HeatPumpOptimizerCoordinator(
    _bare_hass,
    FakeEntry(
        data={
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        }
    ),
)
asyncio.run(_bare_coord._update_current_state())
R.check(
    "with no fuse and no capacity tariff there is still nothing to report",
    _bare_coord._power_headroom() == {"available": False},
    str(_bare_coord._power_headroom()),
)

# --- device classes ---------------------------------------------------------
R.section("Device classes on the three that were bare")

for _display, _expected in (
    ("DHW Setpoint Advisor", "temperature"),
    ("DHW Mixed Water", "volume_storage"),
    ("Thermal Battery Energy", "energy_storage"),
):
    R.check(
        f"{_display} declares device class {_expected}",
        getattr(by_name[_display], "_attr_device_class", None) == _expected,
        repr(getattr(by_name[_display], "_attr_device_class", None)),
    )

# Home Assistant checks the (device class, state class) pair on every state
# write and logs "state class ... is impossible considering device class" --
# the trap MONETARY + TOTAL_INCREASING already sprang here once. The table is
# Home Assistant's own, mirrored in the stub.
_impossible = []
for _entity in sensors:
    _dc = getattr(_entity, "_attr_device_class", None)
    _sc = getattr(_entity, "_attr_state_class", None)
    if _dc is None or _sc is None:
        continue
    _allowed = DEVICE_CLASS_STATE_CLASSES.get(_dc)
    if _allowed is not None and _sc not in _allowed:
        _impossible.append(f"{type(_entity).__name__}: {_dc} + {_sc}")
R.check(
    "no sensor pairs a device class with a state class HA forbids",
    not _impossible,
    "; ".join(_impossible),
)

# Two the audit brief flagged and this PR deliberately leaves alone, pinned so
# a future "consistency" pass does not add a device class to either.
R.check(
    "ECL110 Displace stays bare: it is a parallel shift, not a temperature",
    getattr(by_name["ECL110 Displace"], "_attr_device_class", None) is None
    and by_name["ECL110 Displace"]._attr_native_unit_of_measurement == "°C",
    "a TEMPERATURE device class would have HA convert a delta as an absolute",
)
R.check(
    "Prediction Accuracy stays bare for the same reason: it is a mean error",
    getattr(by_name["Prediction Accuracy"], "_attr_device_class", None) is None
    and by_name["Prediction Accuracy"]._attr_native_unit_of_measurement == "°C",
)
R.check(
    "a device class with no state class is legal, so the valve target is fine",
    getattr(by_name["Valve Target Recommendation"], "_attr_device_class", None)
    == "temperature"
    and getattr(by_name["Valve Target Recommendation"], "_attr_state_class", None)
    is None,
    "HA validates the pair only when a state class is set; it never demands one",
)

# The two kWh sensors round 2's D10 audit flagged (#305), pinned for the
# same reason as the deltas above but with the opposite evidence: no device
# class is honest for either. Home Assistant's own table (sensor/const.py
# DEVICE_CLASS_STATE_CLASSES, mirrored above) admits ENERGY only with
# TOTAL/TOTAL_INCREASING -- consumption meters -- and rejects the
# MEASUREMENT pair on every state write. ENERGY_STORAGE, which Thermal
# Battery Energy earns by genuinely measuring stored energy, is documented
# in the floor's own source as "stored energy ... currently stored in a
# battery or the capacity of a battery"; a rolling PV-surplus forecast and
# a learned p90 day-demand are estimates recomputed every cycle, not energy
# sitting anywhere. The Gold rule asks for device classes "where possible"
# -- for these two it is not.
R.check(
    "Solar Surplus Forecast stays bare: a forecast is not a consumption meter",
    getattr(by_name["Solar Surplus Forecast"], "_attr_device_class", None) is None
    and by_name["Solar Surplus Forecast"]._attr_state_class
    == SensorStateClass.MEASUREMENT
    and by_name["Solar Surplus Forecast"]._attr_native_unit_of_measurement == "kWh",
    "ENERGY demands TOTAL/TOTAL_INCREASING; ENERGY_STORAGE would claim stored energy",
)
R.check(
    "DHW Heavy Day Demand stays bare: a learned p90 quantile is not a meter either",
    getattr(by_name["DHW Heavy Day Demand"], "_attr_device_class", None) is None
    and by_name["DHW Heavy Day Demand"]._attr_state_class
    == SensorStateClass.MEASUREMENT
    and by_name["DHW Heavy Day Demand"]._attr_native_unit_of_measurement == "kWh",
    "no kWh device class admits an estimate that is not a total or a storage",
)


# ===========================================================================
# The shared device
# ===========================================================================
R.section("The one device is a service device")

from homeassistant.helpers.device_registry import DeviceEntryType

# Every platform forwards ``device_info`` to the coordinator's single
# DeviceInfo, so the device is described in exactly one place (#305). This
# integration is a cloud API (Tibber) plus the user's own entities -- there
# is no physical device -- and Home Assistant's device registry has a
# dedicated kind for that: the Gold "devices" rule asks for
# entry_type=DeviceEntryType.SERVICE, which the hacs.json floor (2024.6.0)
# ships in homeassistant.helpers.device_registry (a StrEnum with the single
# member SERVICE; DeviceInfo has no config_entry field at the floor).
_dev_coord = HeatPumpOptimizerCoordinator(
    FakeHass(),
    FakeEntry(
        data={
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        },
        entry_id="device_info_probe",
    ),
)
R.check(
    "the shared device declares itself a service device",
    _dev_coord.device_info.get("entry_type") == DeviceEntryType.SERVICE,
    repr(_dev_coord.device_info),
)
R.check(
    "and it is identified by the config entry, not by anything physical",
    _dev_coord.device_info.get("identifiers")
    == {(const.DOMAIN, "device_info_probe")},
    repr(_dev_coord.device_info.get("identifiers")),
)

# The forwarding half of the same claim: driving each platform's real
# async_setup_entry with a real coordinator, the way HA would, every entity
# the roster adds must land on that service device.
for _platform in (sensor, binary_sensor, button, _switch_platform, _climate_platform):
    _platform_entities = collect(_platform, coordinator=_blind_coord)
    _not_service = [
        type(e).__name__
        for e in _platform_entities
        if e.device_info.get("entry_type") != DeviceEntryType.SERVICE
    ]
    R.check(
        f"every {_platform.__name__.rsplit('.', 1)[-1]} entity sits on the service device",
        bool(_platform_entities) and not _not_service,
        "; ".join(_not_service),
    )


# ===========================================================================
# Binary sensors
# ===========================================================================
R.section("Binary sensors")

binaries = collect(binary_sensor)
b_by_name = {display_name("binary_sensor", b): b for b in binaries}
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
btn_by_name = {display_name("button", b): b for b in buttons}
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
_saved = asyncio.run(
    _flow.async_step_entities({**_untouched, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE})
)["data"]
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

# v5.3.0: the four signals the pump publishes about itself. All optional; an
# install that leaves every one of them empty must behave exactly as it did
# before they existed, which is what the "unchanged" checks below pin.
_SIGNAL_KEYS = (
    const.CONF_HEAT_PUMP_MODE_ENTITY,
    const.CONF_HEAT_PUMP_DEFROST_ENTITY,
    const.CONF_HEAT_PUMP_ONLINE_ENTITY,
    const.CONF_HEAT_PUMP_FAULT_ENTITY,
)
# ``_form`` above is this page's rendered schema; ``_pages`` is not built
# until further down the file.
_entities_schema = _form["data_schema"]
_entities_fields = {
    str(getattr(k, "schema", k)): k for k in _entities_schema.schema
}
for _key in _SIGNAL_KEYS:
    R.check(
        f"{_key} is offered on the sensors page",
        _key in _entities_fields,
    )
    R.check(
        f"{_key} is optional",
        type(_entities_fields[_key]).__name__ == "Optional",
        "a required field here would break every existing install on save",
    )
    R.check(
        f"{_key} can be cleared again once set",
        _key in options._ENTITIES_PAGE_KEYS,
        "options merge over setup data, so an absent key restores the old value",
    )
    R.check(
        f"{_key} is a topology slot, so the card and the service agree",
        _key in topology.ASSIGNABLE_KEYS,
    )
    R.check(
        f"the picker for {_key} offers exactly its slot's domains",
        _entities_fields[_key] is not None
        and list(
            _entities_schema.schema[_entities_fields[_key]].config["filter"][0][
                "domain"
            ]
        )
        == list(topology.ASSIGNABLE_KEYS[_key]),
        "one list, or the diagram offers what the service would refuse",
    )

# Round trip: set all four, save, read them back; then clear them and check
# the clearing sticks rather than being undone by the options merge.
_sig_flow = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
_sig_flow.hass = FakeHass()
_sig_values = {
    const.CONF_HEAT_PUMP_MODE_ENTITY: "select.pump_mode",
    const.CONF_HEAT_PUMP_DEFROST_ENTITY: "binary_sensor.pump_defrost",
    const.CONF_HEAT_PUMP_ONLINE_ENTITY: "binary_sensor.pump_online",
    const.CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.pump_fault",
}
_sig_form = asyncio.run(_sig_flow.async_step_entities(None))
_sig_result = asyncio.run(
    _sig_flow.async_step_entities(
        {**_sig_form["data_schema"]({}), **_sig_values,
         const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_sig_saved = _sig_result.get("data") or {}
R.check(
    "the entities page reaches a close-save",
    _sig_result.get("type") == "create_entry",
    str(_sig_result.get("type")),
)
for _key, _value in _sig_values.items():
    R.check(
        f"{_key} survives a save of the page it lives on",
        _sig_saved.get(_key) == _value,
        f"stored {_value!r}, page save produced {_sig_saved.get(_key)!r}",
    )
_sig_flow2 = options(
    FakeEntry(options={const.CONF_TIBBER_TOKEN: "t", **_sig_values})
)
_sig_flow2.hass = FakeHass()
_sig_form2 = asyncio.run(_sig_flow2.async_step_entities(None))
R.check(
    "a configured signal comes back as the field's default",
    all(
        _sig_form2["data_schema"]({}).get(_key) == _value
        for _key, _value in _sig_values.items()
    ),
    "a page that forgets what is configured invites the user to re-enter it",
)
_sig_cleared_result = asyncio.run(
    _sig_flow2.async_step_entities(
        {
            k: v
            for k, v in _sig_form2["data_schema"]({}).items()
            if k not in _sig_values
        }
        | {const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_sig_cleared = _sig_cleared_result.get("data") or {}
R.check(
    "and clearing all four sticks",
    all(_sig_cleared.get(_key) is None for _key in _SIGNAL_KEYS),
    str({k: _sig_cleared.get(k) for k in _SIGNAL_KEYS}),
)

# The null case, which is the one every existing install runs: nothing
# configured, nothing changed.
_bare = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
_bare.hass = FakeHass()
_bare_result = asyncio.run(
    _bare.async_step_entities(
        asyncio.run(_bare.async_step_entities(None))["data_schema"]({})
        | {const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_bare_saved = _bare_result.get("data") or {}
R.check(
    "an install that configures none of them stores none of them set",
    all(_bare_saved.get(_key) is None for _key in _SIGNAL_KEYS),
    str({k: _bare_saved.get(k) for k in _SIGNAL_KEYS}),
)
_bare_setup = topology.describe_setup({const.CONF_INDOOR_TEMP_ENTITY: "sensor.i"})
R.check(
    "and sees them as four empty slots on the heat pump, not as faults",
    [
        s["key"]
        for s in _bare_setup["slots"]
        if s["key"] in _SIGNAL_KEYS
    ]
    == list(_SIGNAL_KEYS)
    and all(
        s["entity"] is None and s["place"] == "heat_pump"
        for s in _bare_setup["slots"]
        if s["key"] in _SIGNAL_KEYS
    ),
    "an empty slot is shown empty; that is the point of the diagram",
)

# What a slot is ASKING FOR, beside the domains it accepts. The card's picker
# ranks a matching device class to the top, which is what makes a temperature
# slot usable on an install with hundreds of sensors -- and that expectation
# used to live in a second table inside the card, keyed by slot id, reachable
# by no test at all. Published on the slot now, from the same row as the
# domains, so the two cannot describe different slots.
#
# The configuration below has every conditional place present, so every slot in
# the table is in the answer: two zones, a hot water tank, a wood tank, a valve.
_dc_setup = topology.describe_setup(
    {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 4.5,
        "dhw_tank_volume": 200.0,
        "mixing_valve_mode": "manual",
        "buffer_tank_volume": 750.0,
        const.CONF_EXTERNAL_HEAT_ENABLED: True,
        const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
    }
)
_dc_slots = {s["key"]: s for s in _dc_setup["slots"]}
R.check(
    "every slot says what it is asking for, even when the answer is nothing",
    all("device_class" in s for s in _dc_setup["slots"]),
    str([s["key"] for s in _dc_setup["slots"] if "device_class" not in s]),
)
_dc_expected = {
    const.CONF_INDOOR_TEMP_ENTITY: "temperature",
    const.CONF_OUTDOOR_TEMP_ENTITY: "temperature",
    const.CONF_DHW_TEMP_ENTITY: "temperature",
    const.CONF_BUFFER_TANK_TEMP_ENTITY: "temperature",
    const.CONF_LOWER_FLOOR_TEMP_ENTITY: "temperature",
    const.CONF_POWER_ENTITY: "power",
    const.CONF_ENERGY_ENTITY: "energy",
    const.CONF_HOUSE_POWER_ENTITY: "power",
    const.CONF_SOLAR_RADIATION_ENTITY: "irradiance",
    const.CONF_PV_PRODUCTION_ENTITY: "power",
}
for _key, _want in _dc_expected.items():
    R.check(
        f"{_key} asks for a {_want} probe",
        _dc_slots.get(_key, {}).get("device_class") == _want,
        f"published {_dc_slots.get(_key, {}).get('device_class')!r}",
    )
_dc_unranked = (
    const.CONF_HEAT_PUMP_SWITCH_ENTITY,
    const.CONF_HEAT_PUMP_MODE_ENTITY,
    const.CONF_HEAT_PUMP_DEFROST_ENTITY,
    const.CONF_EXTERNAL_HEAT_ENTITY,
)
R.check(
    "a slot with no narrower answer than its domains says so, not a guess",
    # Presence asserted, not filtered for: `all()` over a set that quietly
    # filtered itself empty is True, and this file has six documented
    # vacuous tests already.
    all(_k in _dc_slots for _k in _dc_unranked)
    and all(_dc_slots[_k].get("device_class") is None for _k in _dc_unranked),
    "a flag that arrives as any of four domains has no class to rank on: "
    + str({_k: _dc_slots.get(_k, {}).get("device_class") for _k in _dc_unranked}),
)
R.check(
    "and nothing asks for a class its own domains could never carry",
    all(
        "sensor" in s["domains"]
        for s in _dc_setup["slots"]
        if s.get("device_class") is not None
    ),
    str(
        [
            s["key"]
            for s in _dc_setup["slots"]
            if s.get("device_class") is not None
            and "sensor" not in s["domains"]
        ]
    ),
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
_vsaved = asyncio.run(
    _vflow.async_step_building({const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE})
)["data"]
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
    # after_save rides every form (#100) and is stripped by the flow; it
    # is not a thermal default and must not count as a leak.
    {k: v for k, v in _tuntouched.items() if k != const.CONF_AFTER_SAVE} == {},
    f"defaults leaked into the submission: {_tuntouched}",
)
_tsaved = asyncio.run(
    _tflow.async_step_thermal_model({**_tuntouched, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE})
)["data"]
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
    _eflow.async_step_thermal_model(
        {const.CONF_HEAT_PUMP_MAX_POWER: 9.0,
         const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
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
    _zflow.async_step_thermal_model(
        {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0,
         const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
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
_off_result = asyncio.run(
    _off_flow.async_step_thermal_model(
        {const.CONF_TWO_ZONE_MODE: "off", const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
# Guarded before indexing (#100's prerequisite): a page that stops
# returning create_entry must fail the check, not KeyError the suite.
R.check(
    "turning two-zone off reaches the save",
    _off_result.get("type") == "create_entry" and isinstance(
        _off_result.get("data"), dict
    ),
    str(_off_result.get("type")),
)
_off_saved = _off_result.get("data") or {}
R.check(
    "the mode select can turn two-zone off despite stored zone keys",
    not ThermalParameters.from_config(
        {**_off_entry.data, **_off_saved}
    ).two_zone_enabled,
    "options merge over data, so only an explicit override can disable it",
)
_on_flow = options(_legacy)
_on_flow.hass = FakeHass()
_on_result = asyncio.run(
    _on_flow.async_step_thermal_model(
        {const.CONF_TWO_ZONE_MODE: "on", const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
R.check(
    "turning two-zone on reaches the save",
    _on_result.get("type") == "create_entry" and isinstance(
        _on_result.get("data"), dict
    ),
    str(_on_result.get("type")),
)
_on_saved = _on_result.get("data") or {}
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
_saved_pages: list[str] = []
_menu_pages: list[str] = []
_unwritten_menus: list[str] = []
_odd_outcomes: list[str] = []
for _step in options._MENU_LABELS:
    _sf = options(FakeEntry(data=dict(_legacy.data)))
    _sf.hass = FakeHass()
    _sform = asyncio.run(getattr(_sf, f"async_step_{_step}")(None))
    _sschema = _sform.get("data_schema")
    if _sschema is None:
        _odd_outcomes.append(f"{_step}: rendered without a schema")
        continue
    _sresult = asyncio.run(getattr(_sf, f"async_step_{_step}")(_sschema({})))
    _kind = _sresult.get("type")
    if _kind == "create_entry":
        # The explicit close choice (#100). Untouched submissions default
        # to the menu, so an untouched run never lands here -- a page that
        # closes on an untouched submit is a regression to report.
        _saved_pages.append(_step)
        _odd_outcomes.append(f"{_step}: untouched submit closed the dialog")
        continue
    if _kind != "menu":
        _odd_outcomes.append(f"{_step}: untouched submit returned {_kind!r}")
        continue
    _menu_pages.append(_step)
    if not _sresult.get("menu_options"):
        _odd_outcomes.append(f"{_step}: menu without menu_options")
        continue
    if _step == "setup_overview":
        # The one read-only page: back to the menu with nothing written.
        if _sf._entry.options or _sf.hass.config_entries.updated:
            _unwritten_menus.append(_step)
        continue
    # Every saving page now writes through and returns to the menu (#100).
    # The write is the assertion: a menu hand-back that saved nothing is
    # the feature silently missing.
    if not _sf.hass.config_entries.updated:
        _unwritten_menus.append(_step)
        continue
    _ssaved = dict(_sf._entry.options)
    if const.CONF_AFTER_SAVE in _ssaved:
        _odd_outcomes.append(f"{_step}: the after-save choice persisted")
        continue
    _wrote = [k for k in _presence_quad if k in _ssaved and k not in _legacy.data]
    R.check(
        f"an untouched save of the {_step} page cannot flip two-zone",
        not _wrote
        and not ThermalParameters.from_config(
            {**_legacy.data, **_ssaved}
        ).two_zone_enabled,
        f"wrote presence keys {_wrote}",
    )
# The net's own net (the #100 prerequisite, delivered in v6.0.4): the sweep
# must EXERCISE every page and account for each outcome -- the menu-return
# feature changed what the outcomes are, and these checks are what made
# that change visible instead of silent.
R.check(
    "every options page answers an untouched submit with the menu",
    not _odd_outcomes,
    "; ".join(_odd_outcomes),
)
R.check(
    "and every saving page wrote its settings through before returning",
    not _unwritten_menus,
    f"no write-through from: {_unwritten_menus}",
)
R.check(
    "the untouched-save sweep exercised every page",
    len(_menu_pages) == len(options._MENU_LABELS)
    and len(_menu_pages) > 1,
    f"menu {len(_menu_pages)} of {len(options._MENU_LABELS)} pages "
    f"(read-only overview included)",
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
    and {k: v for k, v in _pform["data_schema"]({}).items()
         if k != const.CONF_AFTER_SAVE} == {},
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
# Stored values and field ranges
# ===========================================================================
R.section("Stored values and field ranges")

# The defect this section exists for: a bounded numeric field validates the
# value it was *given back* on submit, and the frontend submits every field on
# the page, not just the ones the user touched. So a stored value outside its
# own field's range does not merely look odd -- it makes the whole page
# impossible to save, silently, because voluptuous rejects the submission
# before any handler runs and the dialog simply re-renders. The user sees a
# Submit button that does nothing, "90% of the time".
#
# It shipped because the only round trip tested here was ``schema({})``, an
# empty submission. That exercises the ``default=`` path and nothing else, and
# the expert thermal page is built entirely from ``suggested_value``: it has
# no defaults, so the empty dict proved only that the page writes nothing.
# The checks below submit what the frontend would actually post.

from heatpump_optimizer import presets


def _submission(schema, **overrides):
    """What the browser posts back when the user changes nothing.

    Every field pre-filled from a stored value is echoed back verbatim --
    from ``suggested_value`` or from ``default``, the frontend cannot tell
    the two apart -- and a field with neither is left out.
    """
    payload = {}
    for marker, _validator in schema.schema.items():
        key = str(getattr(marker, "schema", marker))
        description = getattr(marker, "description", None)
        if isinstance(description, dict) and "suggested_value" in description:
            payload[key] = description["suggested_value"]
            continue
        default = getattr(marker, "default", None)
        if callable(default):
            payload[key] = default()
    payload.update(overrides)
    return payload


def _drive(coro):
    """Run a config-flow step that never awaits, without an event loop.

    The sweeps below run thousands of round trips; ``asyncio.run`` per call
    costs twice as much as the flow itself.
    """
    try:
        coro.send(None)
    except StopIteration as stop:
        return stop.value
    raise AssertionError("this step awaited something; use asyncio.run")


def _bounds(schema):
    """``{field: (min, max)}`` for every numeric field on a page."""
    return {
        str(getattr(marker, "schema", marker)): (
            validator.config.get("min"),
            validator.config.get("max"),
        )
        for marker, validator in schema.schema.items()
        if isinstance(validator, config_flow.selector.NumberSelector)
    }


# The nominal ranges: the expert page as it renders for an entry that has
# stored nothing, so no field has been widened to fit a value.
_nominal_flow = options(FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"}))
_nominal_flow.hass = FakeHass()
_NOMINAL = _bounds(
    asyncio.run(_nominal_flow.async_step_thermal_model(None))["data_schema"]
)

# The same keys are also editable during initial setup. Two pages storing one
# key under two different ranges is the same defect with a longer fuse: the
# setup flow would write a value the options page then refuses to show back.
_initial = config_flow.HeatPumpOptimizerConfigFlow()
_initial.hass = FakeHass()
_setup_bounds = {}
for _step in ("thermal", "zones"):
    _setup_bounds.update(
        _bounds(asyncio.run(getattr(_initial, f"async_step_{_step}")(None))["data_schema"])
    )
_mismatched = sorted(
    f"{key} setup {_setup_bounds[key]} vs expert {_NOMINAL[key]}"
    for key in _setup_bounds
    if key in _NOMINAL and _setup_bounds[key] != _NOMINAL[key]
)
R.check(
    "setup and the expert page agree on every shared field's range",
    not _mismatched,
    "; ".join(_mismatched),
)

# No field may accept a value the model will then quietly override.
# ``ThermalParameters.clamp`` raises every store below THERMAL_MASS_FLOOR,
# so a field minimum under it is a window in which the page stores one number
# and the model runs another -- with nothing gained, since ``presets.derive``
# floors its own radiator-loop mass at exactly the same place.
from heatpump_optimizer.thermal_model import THERMAL_MASS_FLOOR

_below_floor = sorted(
    f"{key} starts at {_NOMINAL[key][0]}, below the model's floor {THERMAL_MASS_FLOOR}"
    for key in (
        const.CONF_HOUSE_THERMAL_MASS,
        const.CONF_SLAB_THERMAL_MASS,
        const.CONF_UPPER_FLOOR_THERMAL_MASS,
        const.CONF_LOWER_FLOOR_THERMAL_MASS,
    )
    if _NOMINAL[key][0] < THERMAL_MASS_FLOOR
)
R.check(
    "no thermal-mass field accepts a value the model would clamp away",
    not _below_floor,
    "; ".join(_below_floor),
)

# --- The invariant: derived physics fits the field that stores it ----------
#
# ``presets.derive`` scales every thermal parameter by heated area and knows
# nothing about the ranges the config flow declares. Sweep what it can emit
# and require the storing field to accept it.
#
# Exhaustive over every discrete axis -- structure, era, foundation, both
# emitters, single- and two-zone, and all seventeen positions of the area-
# ratio slider. Heated area is continuous, so it is walked at the ends of the
# plausible band and inside it; ``derive`` is linear in area, so the extremes
# live at the ends, and the interior points are there to catch a future term
# that is not.
_RATIOS = [round(0.1 + 0.05 * i, 2) for i in range(17)]
_PLAUSIBLE_AREAS = (40.0, 100.0, 140.0, 200.0, 300.0, 400.0)


def _derived(structure, era, foundation, area, upper, lower, two_zone, ratio):
    values = presets.derive(
        presets.BuildingPreset(
            structure=structure,
            era=era,
            foundation=foundation,
            heated_area_m2=area,
            upper_emitter=upper,
            lower_emitter=lower,
            upper_area_ratio=ratio,
            two_zone=two_zone,
        )
    )
    # Informational, and not a field on any page.
    values.pop("heating_response_hours", None)
    return values


def _matrix(areas, ratios):
    for structure in presets.STRUCTURES:
        for era in presets.ERAS:
            for foundation in presets.FOUNDATIONS:
                for upper in presets.EMITTERS:
                    for lower in presets.EMITTERS:
                        for area in areas:
                            for two_zone in (False, True):
                                for ratio in ratios if two_zone else (0.5,):
                                    yield (
                                        structure, era, foundation, area,
                                        upper, lower, two_zone, ratio,
                                    )


_outside = {}
_swept = 0
for _case in _matrix(_PLAUSIBLE_AREAS, _RATIOS):
    _swept += 1
    for _key, _value in _derived(*_case).items():
        _low, _high = _NOMINAL[_key]
        if _value < _low or _value > _high:
            _worst = _outside.setdefault(_key, [0, _value, _value, _case])
            _worst[0] += 1
            _worst[1] = min(_worst[1], _value)
            _worst[2] = max(_worst[2], _value)
R.check(
    f"every value derivable for a 40-400 m² house fits its field ({_swept:,} cases)",
    not _outside,
    "; ".join(
        f"{key}: {count:,} outside {_NOMINAL[key]}, seen {low:g}..{high:g} e.g. {case}"
        for key, (count, low, high, case) in sorted(_outside.items())
    ),
)

# The questionnaire accepts 20 to 1000 m², which is wider than any range
# tight enough to catch a typo. Those houses are carried by the widening in
# ``_fit_stored_values`` instead -- so here the check is the real one: store
# what the questionnaire derived, open the page, and submit it back untouched
# the way the browser would.
_EXTREME_AREAS = (20.0, 40.0, 140.0, 400.0, 1000.0)
_unsubmittable = []
_roundtrips = 0
_entry_for_sweep = FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"})
_sweep_flow = options(_entry_for_sweep)
_sweep_flow.hass = FakeHass()
for _case in _matrix(_EXTREME_AREAS, (0.1, 0.5, 0.9)):
    _stored = _derived(*_case)
    _entry_for_sweep.options = dict(_stored)
    _schema = _drive(_sweep_flow.async_step_thermal_model(None))["data_schema"]
    _roundtrips += 1
    try:
        _accepted = _schema(_submission(_schema))
    except Exception as err:  # noqa: BLE001 - any rejection is the bug
        _unsubmittable.append(f"{_case}: {type(err).__name__}: {err}")
        continue
    for _key, _value in _stored.items():
        if _accepted.get(_key) != _value:
            _unsubmittable.append(
                f"{_case}: {_key} came back {_accepted.get(_key)!r}, stored {_value!r}"
            )
R.check(
    f"any house the questionnaire can describe can still save the expert page "
    f"({_roundtrips:,} round trips)",
    not _unsubmittable,
    "; ".join(_unsubmittable[:3]),
)

# And the edit the owner reported: change one number on a page whose other
# values are out of the nominal range, and the change must stick.
_reported = _derived(
    "timber_crawlspace", "pre_1960", "crawlspace", 80.0,
    "radiators", "radiators", False, 0.5,
)
_edit_entry = FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"}, options=dict(_reported))
_edit_flow = options(_edit_entry)
_edit_flow.hass = FakeHass()
_edit_form = asyncio.run(_edit_flow.async_step_thermal_model(None))
_edit_payload = _submission(
    _edit_form["data_schema"], **{const.CONF_HOUSE_THERMAL_MASS: 4.5}
)
try:
    _edit_valid = _edit_form["data_schema"](_edit_payload)
    _edit_error = ""
except Exception as err:  # noqa: BLE001
    _edit_valid = None
    _edit_error = f"{type(err).__name__}: {err}"
R.check(
    "an expert edit sticks on a radiator house (slab mass 0.16, page floor was 1)",
    _edit_valid is not None
    and _edit_valid.get(const.CONF_HOUSE_THERMAL_MASS) == 4.5,
    _edit_error or str(_edit_valid),
)
_edit_saved = asyncio.run(
    _edit_flow.async_step_thermal_model(
        {**(_edit_valid or {}), const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
R.check(
    "and reaches the save rather than dying in the schema",
    _edit_saved.get("type") == "create_entry"
    and (_edit_saved.get("data") or {}).get(const.CONF_HOUSE_THERMAL_MASS) == 4.5,
    str(_edit_saved.get("type")),
)

# --- The same round trip, on every page ------------------------------------
#
# The hazard is not the thermal page's alone. ``apply_schedule`` and the
# climate entity write config keys straight into the entry's options with
# their own, wider limits, so any page can end up displaying a value its own
# selector would refuse. Load every page with a full configuration and post
# it back the way the browser would.
_FULL_CONFIG = {
    const.CONF_TIBBER_TOKEN: "t",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_TARGET_TEMP: 21.0,
    const.CONF_MIN_TEMP: 19.0,
    const.CONF_MAX_TEMP: 23.0,
    const.CONF_COMFORT_TEMP_DAY: 21.0,
    const.CONF_COMFORT_TEMP_NIGHT: 19.5,
    const.CONF_DAY_START_HOUR: 6,
    const.CONF_DAY_END_HOUR: 22,
    const.CONF_DHW_SETPOINT: 52.0,
    const.CONF_DHW_MIN_TEMP: 42.0,
    const.CONF_DHW_WINDOWS: "06:00-08:00",
    const.CONF_BUILDING_PRESET_ENABLED: True,
    const.CONF_HEATED_AREA: 80.0,
    const.CONF_BUILDING_STRUCTURE: presets.STRUCTURE_TIMBER_CRAWLSPACE,
    const.CONF_BUILDING_ERA: presets.ERA_PRE_1960,
    const.CONF_BUILDING_FOUNDATION: presets.FOUNDATION_CRAWLSPACE,
    const.CONF_UPPER_EMITTER: presets.EMITTER_RADIATORS,
    const.CONF_LOWER_EMITTER: presets.EMITTER_RADIATORS,
    **_reported,
}
_rejected = []
for _step in options._MENU_LABELS:
    _rt_flow = options(FakeEntry(data=dict(_FULL_CONFIG)))
    _rt_flow.hass = FakeHass()
    _rt_form = asyncio.run(getattr(_rt_flow, f"async_step_{_step}")(None))
    _rt_schema = _rt_form.get("data_schema")
    if _rt_schema is None:
        continue
    try:
        _rt_valid = _rt_schema(_submission(_rt_schema))
    except Exception as err:  # noqa: BLE001
        _rejected.append(f"{_step}: {type(err).__name__}: {err}")
        continue
    _rt_result = asyncio.run(getattr(_rt_flow, f"async_step_{_step}")(_rt_valid))
    if _rt_result.get("type") not in ("create_entry", "menu"):
        _rejected.append(f"{_step}: submit returned {_rt_result.get('type')}")
    elif _rt_result.get("type") == "menu" and not _rt_result.get("menu_options"):
        # A menu hand-back must actually be the menu; anything else is a
        # page that lost its way home (#100's prerequisite).
        _rejected.append(f"{_step}: menu without menu_options")
    elif (
        _rt_result.get("type") == "create_entry"
        and not isinstance(_rt_result.get("data"), dict)
    ):
        _rejected.append(f"{_step}: save without data")
R.check(
    "every options page accepts the values it displays, on a full configuration",
    not _rejected,
    "; ".join(_rejected),
)

# The same, for the pages of the initial setup flow. A default outside its own
# range breaks first-run setup, which nobody can work around.
_setup_rejected = []
for _step in ("temperature", "building_describe", "building_extras", "thermal",
              "zones", "dhw", "weather_sensitivity"):
    _sflow = config_flow.HeatPumpOptimizerConfigFlow()
    _sflow.hass = FakeHass()
    _sform = asyncio.run(getattr(_sflow, f"async_step_{_step}")(None))
    _sschema = _sform.get("data_schema")
    if _sschema is None:
        continue
    try:
        _sschema(_submission(_sschema))
    except Exception as err:  # noqa: BLE001
        _setup_rejected.append(f"{_step}: {type(err).__name__}: {err}")
R.check(
    "every setup page accepts the values it displays",
    not _setup_rejected,
    "; ".join(_setup_rejected),
)

# --- The widening itself ---------------------------------------------------
#
# Only the field holding the odd value may relax; the rest of the page keeps
# the bounds that make a typo catchable.
# A 1000 m² masonry block with a heated basement and floor heating: the
# questionnaire accepts it, and its slab store is far above anything a range
# tight enough to be useful would admit.
_WIDE_VALUE = _derived(
    "masonry", "pre_1960", "heated_basement", 1000.0, "floor", "floor", False, 0.5
)[const.CONF_SLAB_THERMAL_MASS]
_wide_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "t"},
    options={const.CONF_SLAB_THERMAL_MASS: _WIDE_VALUE},
)
_wide_flow = options(_wide_entry)
_wide_flow.hass = FakeHass()
_wide_form = asyncio.run(_wide_flow.async_step_thermal_model(None))
_wide = _bounds(_wide_form["data_schema"])
R.check(
    f"the field holding an out-of-range value ({_WIDE_VALUE:g}) widens to admit it",
    _wide[const.CONF_SLAB_THERMAL_MASS]
    == (_NOMINAL[const.CONF_SLAB_THERMAL_MASS][0], _WIDE_VALUE),
    str(_wide[const.CONF_SLAB_THERMAL_MASS]),
)
R.check(
    "the widened field is named to the user, not silently patched",
    _wide_form.get("errors", {}).get(const.CONF_SLAB_THERMAL_MASS)
    == config_flow.ERROR_STORED_VALUE_OUT_OF_RANGE,
    f"a page that quietly accepts an odd value teaches nothing: "
    f"{_wide_form.get('errors')}",
)
_clean_form = asyncio.run(_nominal_flow.async_step_thermal_model(None))
R.check(
    "a page with nothing out of range reports no error at all",
    not _clean_form.get("errors"),
    f"an error on a page with nothing wrong would cry wolf: "
    f"{_clean_form.get('errors')}",
)
R.check(
    "and no other field on the page moves",
    {k: v for k, v in _wide.items() if k != const.CONF_SLAB_THERMAL_MASS}
    == {k: v for k, v in _NOMINAL.items() if k != const.CONF_SLAB_THERMAL_MASS},
    str(sorted(set(_wide.items()) ^ set(_NOMINAL.items()))),
)

# The ``default=`` half of the hazard, which breaks a page the same way and is
# reachable today: ``apply_schedule`` stores comfort_temp_day anywhere in
# 5-30 °C, while the comfort page's own field stops at 16-26.
_service_written = options(
    FakeEntry(
        data=dict(_FULL_CONFIG),
        options={const.CONF_COMFORT_TEMP_DAY: 28.0, const.CONF_DAY_START_HOUR: 14},
    )
)
_service_written.hass = FakeHass()
_sw_form = asyncio.run(_service_written.async_step_comfort(None))
_sw_bounds = _bounds(_sw_form["data_schema"])
try:
    _sw_valid = _sw_form["data_schema"](_submission(_sw_form["data_schema"]))
    _sw_error = ""
except Exception as err:  # noqa: BLE001
    _sw_valid = None
    _sw_error = f"{type(err).__name__}: {err}"
R.check(
    "a comfort value stored by apply_schedule can still be shown and saved",
    _sw_valid is not None
    and _sw_valid.get(const.CONF_COMFORT_TEMP_DAY) == 28.0
    and _sw_bounds[const.CONF_COMFORT_TEMP_DAY][1] == 28.0,
    _sw_error or str(_sw_bounds[const.CONF_COMFORT_TEMP_DAY]),
)

# The two comfort mechanisms this release and the last one added meet on this
# page, and they answer different questions: widening is about a value outside
# ONE field's range, the band rules are about fields contradicting EACH OTHER,
# which no single range can see. They compose through `errors.setdefault`
# above -- a real validation error on a field outranks a notice about a value
# that has been on disk for months -- so pin that both survive together.
def _comfort_errors(stored, submit):
    flow = options(FakeEntry(data=dict(_FULL_CONFIG), options=dict(stored)))
    flow.hass = FakeHass()
    asyncio.run(flow.async_step_comfort(None))
    return asyncio.run(flow.async_step_comfort(submit)).get("errors") or {}


_compose_stored = _comfort_errors({const.CONF_COMFORT_TEMP_DAY: 28.0}, None)
_compose_band = _comfort_errors(
    {const.CONF_COMFORT_TEMP_DAY: 28.0},
    {
        const.CONF_COMFORT_TEMP_DAY: 18.0,
        const.CONF_COMFORT_TEMP_NIGHT: 22.0,
        const.CONF_DAY_START_HOUR: 6,
        const.CONF_DAY_END_HOUR: 22,
    },
)
R.check(
    "an out-of-range stored comfort value is flagged on its own field",
    _compose_stored.get(const.CONF_COMFORT_TEMP_DAY)
    == config_flow.ERROR_STORED_VALUE_OUT_OF_RANGE,
    str(_compose_stored),
)
R.check(
    "and a band contradiction is still reported when one is submitted",
    _compose_band.get(const.CONF_COMFORT_TEMP_NIGHT) == "night_above_day",
    str(_compose_band),
)

# ===========================================================================
# Derived values and the questionnaire
# ===========================================================================
R.section("Derived values and the questionnaire")

# The questionnaire owns ten of the expert page's fields. The page has to
# know which ten: an edit to one of them means the user is overriding the
# derivation, and derivation left armed would take it back on the next save
# of the questionnaire page.
_two_zone_derived = _derived(
    presets.STRUCTURE_MASONRY, presets.ERA_PRE_1960, presets.FOUNDATION_BASEMENT,
    180.0, presets.EMITTER_RADIATORS, presets.EMITTER_FLOOR, True, 0.5,
)
_single_derived = _derived(
    presets.STRUCTURE_MASONRY, presets.ERA_PRE_1960, presets.FOUNDATION_BASEMENT,
    180.0, presets.EMITTER_RADIATORS, presets.EMITTER_FLOOR, False, 0.5,
)
R.check(
    "the derived-key roster is exactly what presets.derive writes",
    set(config_flow.DERIVED_THERMAL_KEYS) == set(_two_zone_derived)
    and set(_single_derived) <= set(config_flow.DERIVED_THERMAL_KEYS),
    str(sorted(set(config_flow.DERIVED_THERMAL_KEYS) ^ set(_two_zone_derived))),
)

_armed = {
    const.CONF_TIBBER_TOKEN: "t",
    const.CONF_BUILDING_PRESET_ENABLED: True,
    **_single_derived,
}


def _thermal_save(overrides):
    """Post the expert page back the way the browser does, and return the save.

    Through ``_submission``, never a hand-built dict. The distinction is the
    whole subject of this file's previous section, and the first version of
    the disarm rule below was certified with partial dicts the frontend
    never sends -- ``{heat_pump_max_power: 9.0}`` and ``schema({})`` -- so
    every check passed while a no-op Submit silently disarmed the
    questionnaire for every user who had taken the recommended setup path.
    """
    flow = options(FakeEntry(data=dict(_armed)))
    flow.hass = FakeHass()
    schema = asyncio.run(flow.async_step_thermal_model(None))["data_schema"]
    payload = schema(_submission(schema, **overrides))
    # Close-choice: these checks read the create_entry payload, which now
    # requires asking for it (#100); the default menu-return writes through
    # to entry.options instead.
    result = asyncio.run(
        flow.async_step_thermal_model(
            {**payload, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
        )
    )
    return result.get("data") or {}


# The case that matters most, because it is the cheapest thing a user can do
# and the one nobody thinks to test: open the page, press Submit, touch
# nothing. The browser still posts every pre-filled field, so "was a derived
# key submitted?" is true here -- and answering that question instead of
# "did a derived value change?" is what made this a regression.
_noop = _thermal_save({})
R.check(
    "a no-op Submit leaves the derivation exactly as it was",
    const.CONF_BUILDING_PRESET_ENABLED not in _noop,
    f"pressing Submit with nothing touched wrote {_noop!r}",
)
R.check(
    "and changes nothing it wrote back",
    all(_noop[k] == _armed[k] for k in _noop if k in _armed)
    and not set(_noop) - set(_armed) - {const.CONF_TWO_ZONE_MODE},
    f"a no-op Submit altered something: {_noop!r}",
)

_same = _thermal_save(
    {const.CONF_HOUSE_THERMAL_MASS: _single_derived[const.CONF_HOUSE_THERMAL_MASS]}
)
R.check(
    "re-typing a derived value unchanged is not an override",
    const.CONF_BUILDING_PRESET_ENABLED not in _same,
    f"saved {_same!r}",
)

_unrelated = _thermal_save({const.CONF_HEAT_PUMP_MAX_POWER: 9.0})
R.check(
    "editing a field the questionnaire does not own leaves it armed",
    _unrelated.get(const.CONF_HEAT_PUMP_MAX_POWER) == 9.0
    and const.CONF_BUILDING_PRESET_ENABLED not in _unrelated,
    f"saved {_unrelated!r}",
)

_override = _thermal_save({const.CONF_HOUSE_THERMAL_MASS: 4.5})
R.check(
    "changing a derived value switches the derivation off, so the value keeps",
    _override.get(const.CONF_HOUSE_THERMAL_MASS) == 4.5
    and _override.get(const.CONF_BUILDING_PRESET_ENABLED) is False,
    f"saved {_override!r}",
)

# The consequence the user would actually feel, end to end: after the four
# submits above, is the questionnaire still able to recalculate?
_still_armed_flow = options(FakeEntry(data=dict(_armed), options=dict(_noop)))
_still_armed_flow.hass = FakeHass()
_preset_form = asyncio.run(_still_armed_flow.async_step_building_preset(None))
_preset_result = asyncio.run(
    _still_armed_flow.async_step_building_preset(
        _preset_form["data_schema"](
            _submission(
                _preset_form["data_schema"],
                **{const.CONF_BUILDING_ERA: presets.ERA_POST_2005},
            )
        )
        | {const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_preset_saved = _preset_result.get("data") or {}
R.check(
    "and the questionnaire still recalculates after a no-op Submit",
    _preset_saved.get(const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT)
    not in (None, _single_derived[const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT]),
    f"changing the era recalculated nothing: {_preset_saved!r}",
)

# The user-visible text, in all three files. (The Translations section below
# checks they carry the same keys; these checks are about what those keys
# say.)
_CATALOGUES = {
    "strings.json": json.loads((ROOT / "strings.json").read_text()),
    "en.json": json.loads((ROOT / "translations" / "en.json").read_text()),
    "sv.json": json.loads((ROOT / "translations" / "sv.json").read_text()),
}

# Home Assistant has no way to grey a field out, so the page says in words
# what it cannot show. An unfilled placeholder renders as literal braces.
_armed_flow = options(FakeEntry(data=dict(_armed)))
_armed_flow.hass = FakeHass()
_armed_form = asyncio.run(_armed_flow.async_step_thermal_model(None))
R.check(
    "the expert page warns while the derivation is armed",
    _armed_form["description_placeholders"]["preset_warning"],
    "a user editing a value that will be overwritten deserves to know",
)
R.check(
    "and says nothing when it is off",
    _clean_form["description_placeholders"]["preset_warning"] == "",
    "a warning about a derivation nobody enabled is noise",
)
for _name, _data in _CATALOGUES.items():
    _step = _data["options"]["step"]["thermal_model"]
    R.check(
        f"{_name} gives the warning somewhere to appear",
        "{preset_warning}" in _step["description"],
        "the placeholder has to be in the description it fills",
    )
    R.check(
        f"{_name} does not carry the text as a step key",
        "preset_warning" not in _step,
        "hassfest rejects any step key outside title/description/data/"
        "data_description/menu_options/submit/sections, and it did",
    )

# The text itself lives in code, because a description *placeholder* is
# substituted verbatim by the frontend and a step has nowhere valid to keep
# a free-standing sentence. So the languages have to be checked here.
R.check(
    "the warning is carried in code, in both languages",
    set(config_flow.PRESET_WARNING) == {"en", "sv"}
    and all(len(v) > 80 for v in config_flow.PRESET_WARNING.values()),
    "an English-only warning would ship untranslated to every Swedish user",
)
R.check(
    "and an unknown language falls back to English rather than a KeyError",
    config_flow.PRESET_WARNING.get("de", config_flow.PRESET_WARNING["en"])
    == config_flow.PRESET_WARNING["en"],
    "a form must never fail to render",
)

# The caption that sent the owner's own value 27 percent high: an absolute
# rule of thumb ("roughly 3 kWh/°C") printed on a field the model scales by
# heated area, and on the *fast* store at that -- the heavy floor is counted
# separately. A user correcting a derived 1.44 up to 3 would inflate the
# store the plan coasts on.
for _name, _data in _CATALOGUES.items():
    for _flow_name, _step_id in (("config", "thermal"), ("options", "thermal_model")):
        _text = _data[_flow_name]["step"][_step_id]["data_description"][
            "house_thermal_mass"
        ]
        R.check(
            f"{_name} {_flow_name} scales the house-mass advice by area",
            "m²" in _text,
            "an absolute figure on an area-scaled field invites a harmful edit",
        )

# The same page names a page that does not exist: all ten derived keys live
# on the expert page, none on "Heating system and heat storage".
for _name, _data in _CATALOGUES.items():
    _caption = _data["options"]["step"]["building_preset"]["data_description"][
        "building_preset_enabled"
    ]
    _expert_title = _data["options"]["step"]["thermal_model"]["title"]
    R.check(
        f"{_name} points the derivation at the page it actually overwrites",
        _expert_title in _caption,
        f"names {_caption!r}, expert page is {_expert_title!r}",
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

# The stored-value warning is rendered on a form the user merely opened, so
# an untranslated one is especially visible. It has to exist for both flows —
# the widening applies to initial setup as well — and be a real translation.
_warning = config_flow.ERROR_STORED_VALUE_OUT_OF_RANGE
for _flow_name in ("config", "options"):
    R.check(
        f"the out-of-range warning has a {_flow_name} message",
        strings[_flow_name]["error"].get(_warning),
        "a missing error string renders as the raw key",
    )
    R.check(
        f"and the Swedish {_flow_name} message is actually translated",
        files["sv"][_flow_name]["error"].get(_warning)
        not in (None, files["en"][_flow_name]["error"].get(_warning)),
        "placeholder English left in a translation is worse than no translation",
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
# D6-02 (#172): the documented example is what a user pastes into Developer
# Tools. Folded into a string it read as JSON and failed the schema's own
# ``[dict]`` the moment it was submitted.
_manual_examples = {
    field: spec["example"]
    for field, spec in services["apply_manual_plan"]["fields"].items()
    if "example" in spec
}


def _example_passes(schema, payload) -> tuple[bool, str]:
    try:
        schema(dict(payload))
    except Exception as err:  # noqa: BLE001 - any rejection is the finding
        return False, f"{type(err).__name__}: {err}"
    return True, ""


_manual_ok, _manual_why = _example_passes(
    integration.SERVICE_SCHEMA_APPLY_MANUAL_PLAN, _manual_examples
)
R.check(
    "the documented apply_manual_plan example passes the service's own schema",
    bool(_manual_examples) and _manual_ok,
    _manual_why,
)
R.check(
    "and its slot examples are structured lists, not folded strings",
    all(
        isinstance(_manual_examples.get(f), list) and _manual_examples[f]
        for f in ("space_slots", "dhw_slots")
    ),
    str({f: type(_manual_examples.get(f)).__name__ for f in ("space_slots", "dhw_slots")}),
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

from homeassistant.exceptions import ServiceValidationError

from heatpump_optimizer import climate as climate_mod
from heatpump_optimizer import comfort_band
from heatpump_optimizer import switch as switch_mod

climates = collect(climate_mod)
R.check("the climate platform adds exactly one entity", len(climates) == 1)
clim = climates[0]
R.check(
    "the climate unique id is prefixed with the entry id",
    str(clim._attr_unique_id).startswith(ENTRY.entry_id),
    str(clim._attr_unique_id),
)
R.check(
    "the climate entity is device-named (name None with has_entity_name)",
    clim._attr_has_entity_name and clim._attr_name is None,
    "a literal name equal to the device name would render doubled",
)
R.check(
    "the climate entity pins the corrected object id for new installs",
    clim.entity_id == "climate.heat_pump_optimizer",
    str(getattr(clim, "entity_id", None)),
)
R.check(
    "the climate hvac modes are off, heat and auto",
    set(clim._attr_hvac_modes) == {"off", "heat", "auto"},
    str(clim._attr_hvac_modes),
)
R.check(
    "the thermostat shows the user's target, not the per-step setpoint",
    clim.target_temperature == clim.coordinator.target_temperature,
)
R.check(
    "current temperature reads the published payload",
    clim.current_temperature == DATA["indoor_temperature"],
    str(clim.current_temperature),
)
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
# v5.1.7: the slider ran a degree past the ceiling AND a degree below the
# floor, writing whatever it was given unchecked. Adding the check made both
# overshoots worse than useless -- the band refuses `min > target` and
# `target > max` unconditionally, so every value in those outer degrees was
# advertised and then refused. A control must not offer a position it will
# reject, so the slider now offers exactly the band.
R.check(
    "the thermostat's slider stops at the comfort ceiling",
    clim._attr_max_temp == const.DEFAULT_MAX_TEMP,
    f"max_temp {clim._attr_max_temp}, ceiling {const.DEFAULT_MAX_TEMP}",
)
R.check(
    "and starts at the comfort floor, not a degree below it",
    clim._attr_min_temp == const.DEFAULT_MIN_TEMP,
    f"min_temp {clim._attr_min_temp}, floor {const.DEFAULT_MIN_TEMP}",
)
# The check that ties the two together, and the one whose absence let a
# slider advertise a minimum it always refused: walk every position the
# control offers and require the coordinator to accept it.
_slider_coord = FakeCoordinator()
_slider_refused = []
for _i in range(
    int(round((clim._attr_max_temp - clim._attr_min_temp)
              / clim._attr_target_temperature_step)) + 1
):
    _pos = round(
        clim._attr_min_temp + _i * clim._attr_target_temperature_step, 2
    )
    _probe = comfort_band.violations({const.CONF_TARGET_TEMP: _pos}, {})
    if _probe:
        _slider_refused.append((_pos, comfort_band.describe(_probe)))
R.check(
    "every position the slider offers is one the band will accept",
    not _slider_refused,
    f"refused: {_slider_refused}",
)
# A refused setpoint must not reach the comfort learner. The override is the
# only evidence the learner ever gets about `comfort_weight`, and it used to
# be recorded BEFORE the write that can now refuse -- so a rejected slider
# move trained the weight from a temperature the house was never asked to
# hold, while the stored target did not move at all.
_reject = FakeCoordinator()


async def _refuse(temp):
    raise ServiceValidationError("out of band")


_reject.async_set_target_temperature = _refuse
_reject_clim = climate_mod.HeatPumpOptimizerClimate(_reject, clim._entry)
try:
    asyncio.run(_reject_clim.async_set_temperature(temperature=30.0))
    _reject_raised = False
except ServiceValidationError:
    _reject_raised = True
R.check(
    "a refused setpoint trains nothing",
    _reject_raised and not [p for p in _reject.pressed if p.startswith("override")],
    f"raised={_reject_raised}, learner saw {_reject.pressed}",
)

# D3-06: ``hvac_action`` has zero test references anywhere in the suite
# despite being the property Home Assistant's thermostat card reads to show
# "Heating"/"Idle"/"Off" — one of the most visible always-on pieces of
# state in the whole integration. This asserts the actual contract for all
# three branches directly against the real property.
_hvac_heating = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(
        {**DATA, "mode": const.MODE_AUTO,
         "current_action": {"power": 4.0, "power_normalized": 0.85}}
    ),
    clim._entry,
)
R.check(
    "hvac_action reports HEATING while the compressor runs at high power",
    _hvac_heating.hvac_action == climate_mod.HVACAction.HEATING,
    str(_hvac_heating.hvac_action),
)
_hvac_idle = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(
        {**DATA, "mode": const.MODE_AUTO,
         "current_action": {"power": 0.0, "power_normalized": 0.0}}
    ),
    clim._entry,
)
R.check(
    "hvac_action reports IDLE while auto but the compressor is not running",
    _hvac_idle.hvac_action == climate_mod.HVACAction.IDLE,
    str(_hvac_idle.hvac_action),
)
_hvac_off = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(
        {**DATA, "mode": const.MODE_OFF,
         "current_action": {"power": 4.0, "power_normalized": 0.85}}
    ),
    clim._entry,
)
R.check(
    "hvac_action reports OFF for the off mode even with a nonzero action",
    _hvac_off.hvac_action == climate_mod.HVACAction.OFF,
    str(_hvac_off.hvac_action),
)
_hvac_none = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(None), clim._entry
)
R.check(
    "hvac_action is None with no coordinator data at all",
    _hvac_none.hvac_action is None,
)

switches = collect(switch_mod)
R.check("the switch platform adds exactly one entity", len(switches) == 1)
sw = switches[0]
R.check(
    "the switch unique id is prefixed with the entry id",
    str(sw._attr_unique_id).startswith(ENTRY.entry_id),
)
R.check(
    "the switch entity is named through its translation key",
    display_name("switch", sw) == "Optimizer Active",
    display_name("switch", sw),
)
R.check(
    "the switch pins today's object id for new installs",
    sw.entity_id == "switch.heat_pump_optimizer_optimizer_active",
    str(getattr(sw, "entity_id", None)),
)
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


# ===========================================================================
# Entity organisation and typing hygiene (audit round 1, group B4)
# ===========================================================================
R.section("Entity organisation and typing hygiene (audit B4)")

import numpy as _np

from homeassistant.helpers.entity import EntityCategory

# --- D8-01 (#173): a numpy scalar never leaves a sensor --------------------
#
# The coordinator hands the entities whatever the optimizer produced, and the
# solar-gain trajectory is a list of ``numpy.float64``. ``np.float64`` is a
# float *subclass*, so a scrub that tests ``isinstance(value, float)`` first
# waves it through untouched. The published boundary has to hand Home
# Assistant plain Python whatever it was given, so every numeric leaf of DATA
# is replaced by its numpy twin here and every sensor is read back through
# the real setup.


def _numpy_leaves(value) -> int:
    """How many leaves of a published value are numpy objects."""
    if isinstance(value, (_np.generic, _np.ndarray)):
        return 1
    if isinstance(value, dict):
        return sum(_numpy_leaves(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(_numpy_leaves(v) for v in value)
    return 0


def _numpy_twin(value):
    """The same payload with every int and float leaf as a numpy scalar."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return _np.int64(value)
    if isinstance(value, float):
        return _np.float64(value)
    if isinstance(value, dict):
        return {k: _numpy_twin(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_numpy_twin(v) for v in value]
    return value


_np_data = _numpy_twin(DATA)
_np_data["schedule"] = [
    {
        "time": "2026-01-15T00:00:00",
        "power": _np.float64(1.5),
        "setpoint": _np.float32(21.0),
        "price": _np.float64(0.9),
        "solar_gain": _np.float64(0.25),
        "heat_pump_on": _np.bool_(True),
    }
]
# The real model and parameters ride along: Estimated COP and Solar Heat
# Gain read them off the coordinator, and every sensor is swept here.
_np_coordinator = FakeCoordinator(
    _np_data,
    _thermal_model=_blind_coord._thermal_model,
    _thermal_params=_blind_coord._thermal_params,
    _month_totals={"dhw": (41.5, 62.25), "space": (120.0, 180.0)},
)
_np_leaks = sorted(
    s._key
    for s in collect(sensor, coordinator=_np_coordinator)
    if _numpy_leaves(s.native_value)
    or _numpy_leaves(getattr(s, "extra_state_attributes", None))
)
R.check(
    "no numpy scalar leaves any sensor's state or attributes (#173)",
    not _np_leaks,
    ", ".join(_np_leaks),
)
_np_step = sensor.ScheduleSensor(FakeCoordinator(_np_data), ENTRY).extra_state_attributes[
    "schedule"
][0]
R.check(
    "the schedule's solar gain is published as a plain float",
    type(_np_step["solar_gain"]) is float and _np_step["solar_gain"] == 0.25,
    repr(type(_np_step["solar_gain"])),
)
R.check(
    "np.float64, a float subclass, is converted rather than waved through",
    type(_np_step["power"]) is float,
    repr(type(_np_step["power"])),
)
R.check(
    "np.bool_ becomes a plain bool",
    type(_np_step["heat_pump_on"]) is bool,
    repr(type(_np_step["heat_pump_on"])),
)

# --- D8-03 (#174): one object-id prefix for the hot-water domain -----------
#
# Membership comes from production, not from a list here: every hot-water
# sensor's unique-id key already starts with ``dhw``; the suggested object
# ids did not. Three moved (hot_water_energy, hot_water_cost, mixed_hot_water)
# for NEW installs only -- the unique ids are untouched, so an existing
# install keeps its entity ids and its history through the registry.
_dhw_keyed = [s for s in sensors if s._key.startswith("dhw")]
R.check(
    "the hot-water domain is the nine dhw-keyed sensors",
    len(_dhw_keyed) == 9,
    str(sorted(s._key for s in _dhw_keyed)),
)
_dhw_stray = sorted(
    f"{s._key}->{s.entity_id}"
    for s in _dhw_keyed
    if not s.entity_id.startswith("sensor.heat_pump_optimizer_dhw_")
)
R.check(
    "every hot-water sensor suggests a dhw_ object id (#174)",
    not _dhw_stray,
    ", ".join(_dhw_stray),
)
for _display, _new_id, _uid in (
    ("DHW Energy (lifetime)", "sensor.heat_pump_optimizer_dhw_energy", "dhw_energy"),
    ("DHW Cost (lifetime)", "sensor.heat_pump_optimizer_dhw_cost", "dhw_cost_total"),
    ("DHW Mixed Water", "sensor.heat_pump_optimizer_dhw_mixed_water", "dhw_mixed_water"),
):
    _moved = by_name.get(_display)
    R.check(
        f"{_display} suggests {_new_id} on new installs",
        _moved is not None and _moved.entity_id == _new_id,
        str(getattr(_moved, "entity_id", None)),
    )
    R.check(
        f"{_display} keeps unique id ..._{_uid}, so existing installs keep their entity id",
        _moved is not None and _moved._attr_unique_id == f"{ENTRY.entry_id}_{_uid}",
        str(getattr(_moved, "_attr_unique_id", None)),
    )

# --- D8-04 (#175): the headline family shares one category -----------------
_stat_family = {
    s._key: getattr(s, "_attr_entity_category", None)
    for s in sensors
    if (getattr(s, "extra_state_attributes", None) or {}).get("stat_kind")
}
R.check(
    "the stat_kind headline family is four sensors",
    len(_stat_family) == 4,
    str(sorted(_stat_family)),
)
R.check(
    "the stat_kind family shares one entity_category (#175)",
    len(set(_stat_family.values())) == 1,
    str(_stat_family),
)
R.check(
    "and that category is primary, not Diagnostic: the card's headline is the product",
    set(_stat_family.values()) == {None},
    str(_stat_family),
)

# --- D8-05 (#176): prediction accuracy waits for evidence like its siblings -
_unscored = sensor.PredictionAccuracySensor(
    FakeCoordinator(
        {
            **DATA,
            "accuracy": {
                "samples": 0,
                "temperature_mae": None,
                "temperature_bias": None,
                "trust": 0.0,
            },
        }
    ),
    ENTRY,
)
R.check(
    "prediction accuracy is unavailable until an interval has been scored (#176)",
    not _unscored.available,
)
R.check(
    "and names what it is waiting for",
    _unscored.extra_state_attributes.get("waiting_for") == "first_scored_interval",
    repr(_unscored.extra_state_attributes.get("waiting_for")),
)
R.check(
    "a real fresh coordinator's accuracy sensor is unavailable, not Unknown",
    not sensor.PredictionAccuracySensor(_blind_fake, ENTRY).available,
)
_scored = by_name["Prediction Accuracy"]
R.check(
    "with a scored interval it is available and waits for nothing",
    _scored.available
    and _scored.extra_state_attributes.get("waiting_for") is None
    and _scored.native_value == 0.3,
)

# --- D8-06 (#177) and D4-10 (#179): the Diagnostic roster, pinned ----------
#
# Diagnostic is for the integration's own machinery -- solver status, the
# cycle timestamps, the raw solve dump, the forecast-analysis factors,
# learned parameters and opt-in hardware advisories -- not for a quantity
# about the house, the money or the plan. Pinned literally, like the
# disabled roster above, so a sensor cannot drift between the two halves of
# the device page unnoticed.
_expected_diagnostic = {
    "optimization_status",
    "next_optimization",
    "last_optimization",
    "schedule",
    "predictive_insight",
    "ecl110_displace",
    "ecl110_effective_displace",
    "prediction_accuracy",
    "comfort_weight",
    "contract_comparison",
    "dhw_setpoint_advisor",
    "dhw_heavy_day",
    "valve_target_recommendation",
    "compressor_starts",
    "frequency_advisor",
}
_actually_diagnostic = {
    s._key
    for s in sensors
    if getattr(s, "_attr_entity_category", None) == EntityCategory.DIAGNOSTIC
}
R.check(
    "exactly the machinery sensors are Diagnostic (#177, #179)",
    _actually_diagnostic == _expected_diagnostic,
    f"unexpected {sorted(_actually_diagnostic ^ _expected_diagnostic)}",
)
R.check(
    "every disabled-by-default sensor is Diagnostic (#177)",
    _actually_disabled <= _actually_diagnostic,
    f"not diagnostic: {sorted(_actually_disabled - _actually_diagnostic)}",
)

# --- D7-06 (#178): the five dead symbols stay deleted ----------------------
for _module, _name in (
    (config_flow, "_translated_text"),
    (const, "ATTR_DHW_COOLING_RATE"),
    (const, "ATTR_BUFFER_COOLING_RATE"),
    (presets, "_floor_heated_area"),
    (topology, "_CONDITIONAL_PLACES"),
):
    R.check(
        f"{_module.__name__.rsplit('.', 1)[-1]}.{_name} stays deleted (#178)",
        not hasattr(_module, _name),
    )


# ===========================================================================
# Breaking naming release (v5.0.0)
# ===========================================================================
R.section("Naming, translation keys and id stability (v5.0.0)")

_named_entities = (
    [("sensor", s) for s in sensors]
    + [("binary_sensor", b) for b in binaries]
    + [("button", b) for b in buttons]
    + [("switch", sw)]
)

# Every entity resolves its display name through the translation files. The
# climate entity is the deliberate exception: device-named (checked above).
_missing_key = sorted(
    f"{platform}:{e._attr_unique_id}"
    for platform, e in _named_entities
    if not getattr(e, "_attr_translation_key", None)
)
R.check(
    "every entity carries a translation key",
    not _missing_key,
    ", ".join(_missing_key),
)
_literal_names = sorted(
    f"{platform}:{e._attr_unique_id}"
    for platform, e in _named_entities
    if getattr(e, "_attr_name", None) is not None
)
R.check(
    "no entity carries a literal _attr_name any more",
    not _literal_names,
    ", ".join(_literal_names),
)

# The translation rosters and the entity rosters must cover each other
# exactly, per platform: a missing entry renders as a raw key, an orphan
# entry is a translation nobody can ever see. (en.json and sv.json are
# already pinned key-identical to strings.json by the Translations section,
# so checking strings.json covers all three files.)
_used_keys: dict[str, set] = {}
for _platform, _e in _named_entities:
    _used_keys.setdefault(_platform, set()).add(_e._attr_translation_key)
for _platform in sorted(_used_keys):
    _have = set(_ENTITY_STRINGS.get(_platform, {}))
    _diff = _have ^ _used_keys[_platform]
    R.check(
        f"the {_platform} translation roster matches the entities exactly",
        not _diff,
        f"mismatch {sorted(_diff)}",
    )
R.check(
    "the translation files carry no platforms without entities",
    set(_ENTITY_STRINGS) == set(_used_keys),
    str(set(_ENTITY_STRINGS) ^ set(_used_keys)),
)
_sv_entities = json.loads(
    (ROOT / "translations" / "sv.json").read_text()
)["entity"]
_untranslated = sum(
    1
    for _platform, _entries in _ENTITY_STRINGS.items()
    for _key, _val in _entries.items()
    if _sv_entities[_platform][_key]["name"] == _val["name"]
)
_total_names = sum(len(v) for v in _ENTITY_STRINGS.values())
R.check(
    "the Swedish entity names are actually translated",
    _untranslated < _total_names / 4,
    f"{_untranslated} of {_total_names} identical to English",
)

# CRITICAL id stability: pre-assigning ``entity_id`` is the integration
# suggested-object-id mechanism, used verbatim at first registration only.
# It must reproduce exactly the object ids v4.x generated from the English
# names, or new installs diverge from every doc, automation example and the
# card's id-suffix fallback. Existing installs keep their ids via unique_id.
_bad_ids = sorted(
    e._attr_unique_id
    for _platform, e in _named_entities
    if getattr(e, "entity_id", None)
    != f"{_platform}.heat_pump_optimizer_{e._attr_translation_key}"
)
R.check(
    "every entity pre-assigns its suggested object id",
    not _bad_ids,
    ", ".join(_bad_ids),
)
# Spot-pins against the pre-v5.0.0 slugs, written out literally so a renamed
# translation key cannot silently move the goalposts of the check above.
for _display, _expected_id in (
    ("Solar Irradiance", "sensor.heat_pump_optimizer_solar_irradiance"),
    ("Space Heating Plan (next 24 h)", "sensor.heat_pump_optimizer_space_heating_plan"),
    ("DHW Heating Plan (next 24 h)", "sensor.heat_pump_optimizer_dhw_heating_plan"),
    ("Predicted Savings", "sensor.heat_pump_optimizer_predicted_savings"),
    ("Savings Percentage", "sensor.heat_pump_optimizer_savings_percentage"),
    ("Optimization Score", "sensor.heat_pump_optimizer_optimization_score"),
    ("Plan Narrative", "sensor.heat_pump_optimizer_plan_narrative"),
    ("Optimal Setpoint", "sensor.heat_pump_optimizer_optimal_setpoint"),
    ("Recommended Power", "sensor.heat_pump_optimizer_recommended_power"),
    # #174 moved this one deliberately (hot_water_cost -> dhw_cost, new
    # installs only); the B4 section above pins the old->new pair and the
    # unchanged unique id.
    ("DHW Cost (lifetime)", "sensor.heat_pump_optimizer_dhw_cost"),
):
    R.check(
        f"{_display} keeps its v4.x entity id on new installs",
        by_name[_display].entity_id == _expected_id,
        str(by_name[_display].entity_id),
    )
# The card derives headline-stat ids from the plan sensor id by suffix swap;
# that derivation must keep landing on real ids.
_plan_id = by_name["Space Heating Plan (next 24 h)"].entity_id
for _stat_suffix in (
    "_predicted_savings",
    "_savings_percentage",
    "_optimization_score",
    "_plan_narrative",
):
    _derived = _plan_id.replace("_space_heating_plan", _stat_suffix)
    R.check(
        f"the card's suffix derivation for {_stat_suffix} stays valid",
        _derived in {s.entity_id for s in sensors},
        _derived,
    )

# Belt-and-braces for the future: the four headline sensors advertise a
# stable stat_kind attribute, same contract as plan_kind on the plan sensors.
for _display, _kind in (
    ("Predicted Savings", "predicted_savings"),
    ("Savings Percentage", "savings_percentage"),
    ("Optimization Score", "optimization_score"),
    ("Plan Narrative", "plan_narrative"),
):
    R.check(
        f"{_display} advertises stat_kind={_kind}",
        by_name[_display].extra_state_attributes.get("stat_kind") == _kind,
    )

# The merge: Solar Radiation (Optimizer) is gone; Solar Irradiance is the
# survivor and still publishes the merged value and the card's marker.
R.check(
    "the SolarRadiationSensor class no longer exists",
    not hasattr(sensor, "SolarRadiationSensor"),
)
R.check(
    "no sensor claims the retired solar_radiation unique id",
    not [s for s in sensors if s._attr_unique_id.endswith("_solar_radiation")],
)
R.check(
    "there are exactly 55 sensors after the merge",
    len(sensors) == 55,
    str(len(sensors)),
)
R.check(
    "the survivor still publishes the shared irradiance value",
    by_name["Solar Irradiance"].native_value == 210.0,
)
R.check(
    "the survivor keeps its own unique id, so history stays put",
    by_name["Solar Irradiance"]._attr_unique_id == f"{ENTRY.entry_id}_solar_irradiance",
)

# The retired unique_id's registry entry is removed at setup, so existing
# installs do not keep a permanently-unavailable "restored" entity around.
from homeassistant.helpers import entity_registry as er_stub

_clean_hass = FakeHass()
_clean_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_clean_hass.config_entries.entries.append(_clean_entry)
_clean_reg = er_stub.async_get(_clean_hass)
_clean_reg.add(
    "sensor.heat_pump_optimizer_solar_radiation_optimizer",
    unique_id=f"{_clean_entry.entry_id}_solar_radiation",
    config_entry_id=_clean_entry.entry_id,
)
_clean_reg.add(
    "sensor.heat_pump_optimizer_solar_irradiance",
    unique_id=f"{_clean_entry.entry_id}_solar_irradiance",
    config_entry_id=_clean_entry.entry_id,
)
_other_reg_entry = _clean_reg.add(
    "sensor.other_integration_solar_radiation",
    unique_id="someone_elses_solar_radiation",
    config_entry_id="another_entry",
)
asyncio.run(integration.async_setup_entry(_clean_hass, _clean_entry))
R.check(
    "setup removes the retired solar_radiation registry entry",
    "sensor.heat_pump_optimizer_solar_radiation_optimizer" in _clean_reg.removed
    and "sensor.heat_pump_optimizer_solar_radiation_optimizer"
    not in _clean_reg.entities,
)
R.check(
    "and leaves the surviving irradiance entry alone",
    "sensor.heat_pump_optimizer_solar_irradiance" in _clean_reg.entities,
)
R.check(
    "and never touches another config entry's entities",
    _other_reg_entry.entity_id in _clean_reg.entities,
)
# Idempotence: a second setup (reload) with nothing left to remove is a no-op.
_removed_before = list(_clean_reg.removed)
integration._async_remove_retired_entities(_clean_hass, _clean_entry)
R.check(
    "the cleanup is idempotent across reloads",
    _clean_reg.removed == _removed_before,
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
for name in ("Predicted Savings", "Predicted Cost", "Baseline Cost", "DHW Heating Cost (next 24 h)"):
    entity = by_name[name]
    R.check(
        f"{name} stays MEASUREMENT without a MONETARY device class",
        entity._attr_state_class == SensorStateClass.MEASUREMENT
        and getattr(entity, "_attr_device_class", None) is None,
    )

R.check(
    "the mixed hot water sensor uses the volume unit constant",
    by_name["DHW Mixed Water"]._attr_native_unit_of_measurement == "L",
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
# Entity icons (icon translations, audit D10-13 / #189)
# ===========================================================================
R.section("Entity icons (icon translations, audit D10-13)")

# Gold icon-translations: entity icons live in icons.json, keyed per platform
# by translation key, and the frontend reads them from there — not as 64
# hardcoded ``_attr_icon`` pins in the entity classes. The registry is what a
# user (or a future translation) can override; a class pin wins silently over
# it and is exactly the thing this section exists to prevent coming back.
_ic_path = ROOT / "icons.json"
_ic_exists = _ic_path.is_file()
R.check(
    "icons.json exists in the integration root",
    _ic_exists,
    str(_ic_path),
)
try:
    _icons = json.loads(_ic_path.read_text()) if _ic_exists else {}
    R.check("icons.json parses as JSON", True)
except json.JSONDecodeError as _err:
    _icons = {}
    R.check("icons.json parses as JSON", False, str(_err))

# The shape hassfest's icons validator and HA's icon-translation loader read:
# ``{"entity": {platform: {translation_key: {"default": "mdi:..."}}}}``, with
# optional per-entry "state"/"range"/"state_attributes" sections and nothing
# else at any level. Icons are ``mdi:`` slugs, lowercase, digits and dashes.
_icon_shape_errors = []
if set(_icons) - {"entity", "services"}:
    _icon_shape_errors.append(
        f"unexpected top-level keys {sorted(set(_icons) - {'entity', 'services'})}"
    )
_entity_icons = _icons.get("entity")
if not _entity_icons or not isinstance(_entity_icons, dict):
    _icon_shape_errors.append("the entity section is missing or not an object")
    _entity_icons = _entity_icons if isinstance(_entity_icons, dict) else {}
_MDI_SLUG = re.compile(r"^mdi:[a-z0-9-]+$")
for _plat, _entries in sorted(_entity_icons.items()):
    if not isinstance(_entries, dict):
        _icon_shape_errors.append(f"entity.{_plat} is not an object")
        continue
    for _key, _spec in sorted(_entries.items()):
        _where = f"entity.{_plat}.{_key}"
        if not isinstance(_spec, dict):
            _icon_shape_errors.append(f"{_where} is not an object")
            continue
        _extra = set(_spec) - {"default", "state", "range", "state_attributes"}
        if _extra:
            _icon_shape_errors.append(f"{_where} has unexpected keys {sorted(_extra)}")
        _default_icon = _spec.get("default")
        if not isinstance(_default_icon, str) or not _MDI_SLUG.match(_default_icon):
            _icon_shape_errors.append(
                f"{_where}.default is not an mdi slug: {_default_icon!r}"
            )
        for _skey, _sicon in sorted((_spec.get("state") or {}).items()):
            if not isinstance(_sicon, str) or not _MDI_SLUG.match(_sicon):
                _icon_shape_errors.append(
                    f"{_where}.state.{_skey} is not an mdi slug: {_sicon!r}"
                )
R.check(
    "every icons.json entry is the hassfest shape with a valid mdi slug",
    not _icon_shape_errors,
    "; ".join(_icon_shape_errors[:6]),
)

# No entity class pins _attr_icon any more, on any of the four platforms. A
# class-level pin overrides the registry silently; an icon that truly must
# follow state is expressible in the registry as a "state" section.
_icon_pinned = sorted(
    f"{plat}:{e._attr_translation_key}"
    for plat, e in _named_entities
    if getattr(e, "_attr_icon", None) is not None
)
R.check(
    "no entity class pins _attr_icon any more",
    not _icon_pinned,
    ", ".join(_icon_pinned),
)

# The registry covers every translation key on every platform, with exactly
# one exception pinned below: an entity whose icon is its device class's own
# default renders that default anyway, and re-declaring it in the registry
# would override the device class — the one thing the icon-translations rule
# says never to do. (Defaults transcribed from Home Assistant's own
# components/sensor/icons.json at 2026.9.)
_DC_DEFAULT_KEYS = {
    "sensor": {
        "optimal_setpoint",  # temperature renders mdi:thermometer
        "outdoor_temperature_optimizer",  # temperature renders mdi:thermometer
        "measured_power",  # power renders mdi:flash
        "compressor_frequency_advisor",  # frequency renders mdi:sine-wave
    },
}
for _plat in ("sensor", "binary_sensor", "button", "switch"):
    _expected_keys = (
        {e._attr_translation_key for _p, e in _named_entities if _p == _plat}
        - _DC_DEFAULT_KEYS.get(_plat, set())
    )
    _registry_keys = set(_entity_icons.get(_plat, {}))
    _icon_diff = _expected_keys ^ _registry_keys
    R.check(
        f"the {_plat} icon registry covers every translation key exactly",
        not _icon_diff,
        f"mismatch {sorted(_icon_diff)}",
    )

# The exceptions stay exceptions only while the device class actually still
# provides the icon: drop the device class and the entity goes icon-less, so
# each pinned key is checked against the class it leans on.
_sensor_by_tk = {s._attr_translation_key: s for s in sensors}
_dc_pinned_bad = sorted(
    f"sensor:{_key} has no device class to render an icon from"
    for _key in sorted(_DC_DEFAULT_KEYS["sensor"])
    if not getattr(_sensor_by_tk.get(_key), "_attr_device_class", None)
)
R.check(
    "every icon left out of the registry leans on a real device class",
    not _dc_pinned_bad,
    "; ".join(_dc_pinned_bad),
)
# And spot-pins, written out literally so a renamed translation key cannot
# silently move which entities the roster check above excludes.
for _key, _dc in (
    ("optimal_setpoint", "temperature"),
    ("outdoor_temperature_optimizer", "temperature"),
    ("measured_power", "power"),
    ("compressor_frequency_advisor", "frequency"),
):
    _entity = _sensor_by_tk[_key]
    R.check(
        f"sensor:{_key} keeps its {_dc} device class for the default icon",
        getattr(_entity, "_attr_device_class", None) == _dc,
        str(getattr(_entity, "_attr_device_class", None)),
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


# unique-config-entry (Bronze, #182). Several entries are deliberate -- a
# second heat pump gets a second entry -- so what must abort is a TRUE
# duplicate: the same Tibber account pointed at the same plant, which on the
# first screen means the same entities in the same slots. The identity is
# the config flow's own function, imported; a different name, solar source
# or location is the same plant, a different switch or sensor is not, and
# the token itself is hashed out of the id so it never lands in the registry.
from homeassistant.const import CONF_NAME as _CONF_NAME
from homeassistant.data_entry_flow import AbortFlow as _AbortFlow

from heatpump_optimizer.config_flow import entry_identity as _entry_identity

_first_screen = {
    _CONF_NAME: "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok-a",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    const.CONF_SOLAR_FORECAST_SOURCE: const.DEFAULT_SOLAR_FORECAST_SOURCE,
}
_first_identity = _entry_identity(_first_screen)
R.check(
    "the identity is the same for the same answers, whatever their order",
    _entry_identity(dict(reversed(list(_first_screen.items())))) == _first_identity,
)
R.check(
    "a different name is the same plant",
    _entry_identity({**_first_screen, _CONF_NAME: "Garage"}) == _first_identity,
)
R.check(
    "a different solar forecast source is the same plant",
    _entry_identity({**_first_screen, const.CONF_SOLAR_FORECAST_SOURCE: "sensor"})
    == _first_identity,
)
R.check(
    "a different heat pump switch is a different plant",
    _entry_identity(
        {**_first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"}
    )
    != _first_identity,
)
R.check(
    "an extra sensor is a different plant",
    _entry_identity({**_first_screen, const.CONF_DHW_TEMP_ENTITY: "sensor.tank"})
    != _first_identity,
)
R.check(
    "a different Tibber account is a different plant",
    _entry_identity({**_first_screen, const.CONF_TIBBER_TOKEN: "tok-b"})
    != _first_identity,
)
R.check(
    "the token cannot be read back out of the identity",
    "tok-a" not in _first_identity and len(_first_identity) >= 16,
    _first_identity,
)


# The flow itself. The token check is swapped for a stub verdict so the step
# runs to its guard offline (the class-attribute swap idiom, try/finally),
# and an abort surfaces the way it does in Home Assistant: the step raises
# AbortFlow, the flow manager turns that into the abort result.
async def _accept_any_token(hass, token):
    return "ok"


def _run_user_step(flow, answers):
    try:
        return asyncio.run(flow.async_step_user(dict(answers)))
    except _AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


_real_validate_token = config_flow.validate_tibber_token
config_flow.validate_tibber_token = _accept_any_token
try:
    _dup_hass = FakeHass()
    _dup_first = _fresh_flow()
    _dup_first.hass = _dup_hass
    _dup_first_result = _run_user_step(_dup_first, _first_screen)
    R.check(
        "the first flow with these answers proceeds to the temperature step",
        _dup_first_result.get("type") == "form"
        and _dup_first_result.get("step_id") == "temperature",
        str(_dup_first_result)[:120],
    )
    R.check(
        "and carries the plant identity as its unique id",
        _dup_first.unique_id == _first_identity,
        f"flow unique_id {_dup_first.unique_id!r}",
    )
    # What the flow manager does when that flow finishes: an entry that holds
    # the flow's unique id.
    _dup_hass.config_entries.entries.append(
        FakeEntry(
            data=dict(_first_screen),
            entry_id="first_pump",
            unique_id=_dup_first.unique_id,
        )
    )
    _dup_second = _fresh_flow()
    _dup_second.hass = _dup_hass
    R.check(
        "the same answers a second time abort as already configured",
        _run_user_step(_dup_second, _first_screen)
        == {"type": "abort", "reason": "already_configured"},
    )
    _dup_other = _fresh_flow()
    _dup_other.hass = _dup_hass
    _dup_other_result = _run_user_step(
        _dup_other,
        {**_first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"},
    )
    R.check(
        "a second heat pump on the same Tibber account proceeds",
        _dup_other_result.get("type") == "form"
        and _dup_other_result.get("step_id") == "temperature",
        str(_dup_other_result)[:120],
    )
    R.check(
        "the abort reason has a string to show",
        "already_configured" in strings["config"]["abort"],
    )
finally:
    config_flow.validate_tibber_token = _real_validate_token


_user_form = asyncio.run(_fresh_flow().async_step_user(None))
_user_fields = {str(getattr(k, "schema", k)) for k in _user_form["data_schema"].schema}
R.check(
    "the first screen no longer carries the ECL110 MQTT fields",
    not any(f.startswith("ecl110") for f in _user_fields),
    sorted(f for f in _user_fields if f.startswith("ecl110")),
)
R.check(
    "the first screen offers the four heat-pump signal slots too",
    set(_SIGNAL_KEYS) <= _user_fields,
    sorted(set(_SIGNAL_KEYS) - _user_fields),
    # A slot that exists only in the options flow is a slot most users never
    # find: setup is where they are already naming their pump's entities.
)
R.check(
    "and offers them optionally, so setup still completes without a pump",
    all(
        type(k).__name__ == "Optional"
        for k in _user_form["data_schema"].schema
        if str(getattr(k, "schema", k)) in _SIGNAL_KEYS
    ),
)
# The null case: a fresh install with no pump integration at all. Only the
# three genuinely required fields are supplied; nothing else may appear.
_bare_user = _user_form["data_schema"](
    {const.CONF_TIBBER_TOKEN: "t", const.CONF_WEATHER_ENTITY: "weather.home"}
)
R.check(
    "an untouched first screen configures none of them",
    not (set(_SIGNAL_KEYS) & set(_bare_user)),
    str(set(_SIGNAL_KEYS) & set(_bare_user)),
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
    (
        "a day comfort below the band floor",
        {const.CONF_COMFORT_TEMP_DAY: 18.5},
        const.CONF_COMFORT_TEMP_DAY,
        "comfort_outside_band",
    ),
    (
        "a day comfort above the band ceiling",
        {const.CONF_COMFORT_TEMP_DAY: 24.0},
        const.CONF_COMFORT_TEMP_DAY,
        "comfort_outside_band",
    ),
    (
        "a night comfort above the band ceiling",
        {const.CONF_COMFORT_TEMP_NIGHT: 23.5, const.CONF_COMFORT_TEMP_DAY: 23.0},
        const.CONF_COMFORT_TEMP_NIGHT,
        "comfort_outside_band",
    ),
    (
        "a night comfort below the band floor",
        {const.CONF_COMFORT_TEMP_NIGHT: 18.0},
        const.CONF_COMFORT_TEMP_NIGHT,
        "comfort_outside_band",
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

# v5.7.0 (issue #92): the band floor can sit where the night selector
# cannot reach it -- `minimum` spans 14-25 while night stops at 24. The
# rule exempts exactly that window, so the hottest legal bands stay
# submittable; deleting the exemption in comfort_band.dead-ends this
# form, which is the trap the first attempt at the rule fell into.
_hot = _fresh_flow()
_hotres = asyncio.run(
    _hot.async_step_temperature(
        {
            const.CONF_TARGET_TEMP: 25.5,
            const.CONF_MIN_TEMP: 25.0,
            const.CONF_MAX_TEMP: 26.0,
            const.CONF_COMFORT_TEMP_DAY: 25.0,
            const.CONF_COMFORT_TEMP_NIGHT: 24.0,
            const.CONF_DAY_START_HOUR: 7,
            const.CONF_DAY_END_HOUR: 22,
        }
    )
)
R.check(
    "a band floor above the night selector still submits",
    _hotres["type"] == "menu",
    str(_hotres.get("errors")),
)

# The standing satisfiability sweep the issue demands: for EVERY floor
# and ceiling pair the sliders can produce, some full assignment of all
# five fields must pass every rule in comfort_band -- jointly, not one
# rule at a time. A future selector edit that breaks this fails here
# instead of dead-ending a user's setup. The slider spans below are the
# schema's own (target 15-28, min 14-25, max 18-28, day 16-26, night
# 15-24, all at 0.5 °C steps).
def _steps(lo, hi):
    return [round(lo + 0.5 * i, 2) for i in range(int(round((hi - lo) / 0.5)) + 1)]


_target_pos = _steps(15, 28)
_min_pos = _steps(14, 25)
_max_pos = _steps(18, 28)
_day_pos = _steps(16, 26)
_night_pos = _steps(15, 24)
_unsatisfiable = []
for _mn in _min_pos:
    for _mx in _max_pos:
        if _mn > _mx:
            continue
        _ok_any = any(
            not comfort_band.violations(
                {
                    const.CONF_TARGET_TEMP: _tg,
                    const.CONF_MIN_TEMP: _mn,
                    const.CONF_MAX_TEMP: _mx,
                    const.CONF_COMFORT_TEMP_DAY: _dy,
                    const.CONF_COMFORT_TEMP_NIGHT: _nt,
                },
                {},
            )
            for _tg in _target_pos
            if _mn <= _tg <= _mx
            for _dy in _day_pos
            for _nt in _night_pos
        )
        if not _ok_any:
            _unsatisfiable.append((_mn, _mx))
R.check(
    "every floor/ceiling pair the sliders can produce has a submittable form",
    not _unsatisfiable,
    f"unsatisfiable bands: {_unsatisfiable[:5]}",
    )

_okopt = options(FakeEntry())
_okopt.hass = FakeHass()
_okform = asyncio.run(_okopt.async_step_comfort(None))
_oksaved = asyncio.run(_okopt.async_step_comfort(_okform["data_schema"]({})))
R.check(
    "an untouched comfort page still saves -- through the menu return",
    _oksaved.get("type") == "menu"
    and bool(_okopt.hass.config_entries.updated)
    and const.CONF_COMFORT_TEMP_DAY in _okopt._entry.options,
    f"type {_oksaved.get('type')}, updated {_okopt.hass.config_entries.updated}",
)


# ===========================================================================
# Audit round 1, group B3: the form is where the typo happens (#168-#171)
# ===========================================================================
R.section("Config-flow validation and currency (audit B3)")

import re as _b3_re

from heatpump_optimizer import currency as currency_mod
from heatpump_optimizer import dhw_schedule, grid_fee
from heatpump_optimizer.optimizer import OptimizationConfig


def _b3_options(currency="SEK"):
    flow = options(FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"}))
    flow.hass = FakeHass()
    flow.hass.config.currency = currency
    return flow


def _b3_submit(flow, step, overrides):
    """Fill a page's defaults, override, validate through the selectors, submit.

    The selectors run first, the way Home Assistant runs them: a payload a
    slider refuses never reaches the step handler. The two outcomes must not
    be confused -- D4-07 was a real validator hidden behind a slider that
    made it unreachable, and a test that bypassed the schema would have
    called it reachable all along.
    """
    handler = getattr(flow, f"async_step_{step}")
    schema = asyncio.run(handler(None))["data_schema"]
    try:
        payload = schema({**schema({}), **overrides})
    except Exception as err:  # noqa: BLE001 - the rejection is the datum
        # Reported as a result rather than raised, so a slider that refuses
        # the payload fails the check by name instead of ending the script.
        return {"type": "rejected_by_selector", "errors": {"selector": str(err)}}
    return asyncio.run(handler(payload))


def _b3_units(form):
    return {
        str(getattr(k, "schema", k)): (getattr(v, "config", None) or {}).get(
            "unit_of_measurement"
        )
        for k, v in form["data_schema"].schema.items()
    }


def _b3_placeholders(text):
    return set(_b3_re.findall(r"\{(\w+)\}", text))


# --- #168: the money fields follow hass.config.currency ----------------------
_eur = _b3_options("EUR")
_eur_grid = asyncio.run(_eur.async_step_grid(None))
_eur_tuning = asyncio.run(_eur.async_step_tuning(None))
R.check(
    "the per-kWh money fields carry the instance currency as their unit",
    _b3_units(_eur_grid).get(const.CONF_GRID_FEE_FIXED) == "EUR/kWh"
    and _b3_units(_eur_grid).get(const.CONF_CONTRACT_FIXED_PRICE) == "EUR/kWh",
    str({k: v for k, v in _b3_units(_eur_grid).items() if v}),
)
R.check(
    "and so does the compressor replacement cost",
    _b3_units(_eur_tuning).get(const.CONF_COMPRESSOR_REPLACEMENT_COST) == "EUR",
    str({k: v for k, v in _b3_units(_eur_tuning).items() if v}),
)
R.check(
    "the grid page hands the currency to its descriptions as a placeholder",
    (_eur_grid.get("description_placeholders") or {}).get("currency") == "EUR",
    str(_eur_grid.get("description_placeholders")),
)
_grid_texts = strings["options"]["step"]["grid"]
_grid_wanted = set().union(
    *(
        _b3_placeholders(t)
        for section in ("data", "data_description")
        for t in _grid_texts.get(section, {}).values()
    )
)
R.check(
    "every placeholder the grid page's strings name is supplied by its render",
    _grid_wanted and _grid_wanted <= set(_eur_grid.get("description_placeholders") or {}),
    f"strings want {_grid_wanted}, render gives "
    f"{set(_eur_grid.get('description_placeholders') or {})}",
)
_bare = _b3_options(None)
R.check(
    "an unconfigured instance keeps the SEK every existing install has shown",
    _b3_units(asyncio.run(_bare.async_step_grid(None))).get(const.CONF_GRID_FEE_FIXED)
    == f"{currency_mod.FALLBACK_CURRENCY}/kWh",
    "a unit that changes under an unconfigured instance breaks statistics",
)
_hardcoded = sorted(
    f"{flow_name}.{step}.{section}.{key}"
    for flow_name in ("config", "options")
    for step, texts in strings[flow_name]["step"].items()
    for section in ("data", "data_description")
    for key, text in texts.get(section, {}).items()
    if "SEK" in text
) + sorted(
    f"issues.{key}"
    for key, texts in strings["issues"].items()
    if "SEK" in texts["description"]
)
R.check(
    "no field label, description or repair notice hardcodes SEK",
    not _hardcoded,
    ", ".join(_hardcoded[:8]),
)


def _b3_leaves(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _b3_leaves(v, path + (k,))
    elif isinstance(node, str):
        yield path, node


_placeholder_drift = []
for _lang, _data in files.items():
    _theirs = dict(_b3_leaves(_data))
    for _path, _text in _b3_leaves(strings):
        _want = _b3_placeholders(_text)
        if _want and _want != _b3_placeholders(_theirs.get(_path, "")):
            _placeholder_drift.append(f"{_lang}:{'.'.join(_path)}")
R.check(
    "every translation names exactly the placeholders strings.json names",
    not _placeholder_drift,
    ", ".join(_placeholder_drift[:6]),
    # A renamed placeholder that one translation missed renders as literal
    # braces in that language only -- invisible to the key-identity check.
)

# --- #169: a sign or magnitude slip in the fee rules is refused at the form --
def _grid_verdict(spec):
    res = _b3_submit(
        _b3_options(),
        "grid",
        {
            const.CONF_GRID_FEE_MODE: grid_fee.MODE_RULES,
            const.CONF_GRID_FEE_RULES: spec,
        },
    )
    return (res.get("errors") or {}).get(const.CONF_GRID_FEE_RULES), res


_neg_verdict, _neg_res = _grid_verdict("Nov-Mar Mon-Fri 06:00-22:00 = -0.25")
R.check(
    "a negative rule rate is refused with its own error",
    _neg_verdict == grid_fee.ERROR_NEGATIVE,
    f"got {_neg_verdict!r}",
    # A sign-flip typo used to store as a permanent fee subsidy on exactly
    # the hours the grid company charges most for.
)
_big_verdict, _big_res = _grid_verdict("= 25")
R.check(
    "a rate above the implausibility bound is refused too",
    _big_verdict == grid_fee.ERROR_IMPLAUSIBLE,
    f"got {_big_verdict!r}",
)
R.check(
    "and the error message's bound and currency are supplied to it",
    _b3_placeholders(strings["options"]["error"][grid_fee.ERROR_IMPLAUSIBLE])
    <= set(_big_res.get("description_placeholders") or {}),
    str(_big_res.get("description_placeholders")),
)
R.check(
    "a rate at the bound still saves",
    _grid_verdict(f"= {grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH:g}")[0] is None,
)
R.check(
    "and the rule the grammar documents still saves",
    _grid_verdict("Nov-Mar Mon-Fri 06:00-22:00 = 0.25")[0] is None,
)
R.check(
    "an unreadable spec keeps its original error",
    _grid_verdict("Nov-Mar = banana")[0] == grid_fee.ERROR_INVALID,
)
R.check(
    "both new fee errors are translated in every language",
    all(
        key in strings["options"]["error"] and key in files[lang]["options"]["error"]
        for lang in files
        for key in (grid_fee.ERROR_NEGATIVE, grid_fee.ERROR_IMPLAUSIBLE)
    ),
)

# --- #170: the day sliders span the day, and the validator behind them is
#     reachable ----------------------------------------------------------------
_valid_days = [(s, e) for s in range(24) for e in range(1, 25) if s < e]


def _day_bounds(form):
    out = {}
    for k, v in form["data_schema"].schema.items():
        key = str(getattr(k, "schema", k))
        if key in (const.CONF_DAY_START_HOUR, const.CONF_DAY_END_HOUR):
            out[key] = (v.config["min"], v.config["max"])
    return out


for _flow_name, _form in (
    ("setup", asyncio.run(_fresh_flow().async_step_temperature(None))),
    ("options", asyncio.run(_b3_options().async_step_comfort(None))),
):
    _b = _day_bounds(_form)
    (_s_lo, _s_hi), (_e_lo, _e_hi) = (
        _b[const.CONF_DAY_START_HOUR],
        _b[const.CONF_DAY_END_HOUR],
    )
    _forbidden = [
        (s, e)
        for s, e in _valid_days
        if not (_s_lo <= s <= _s_hi and _e_lo <= e <= _e_hi)
    ]
    R.check(
        f"the {_flow_name} day sliders can express every start<end schedule",
        not _forbidden,
        f"{len(_forbidden)} of {len(_valid_days)} forbidden, e.g. {_forbidden[:3]}",
    )
    R.check(
        f"and the {_flow_name} sliders stop where no schedule exists",
        (_s_lo, _s_hi, _e_lo, _e_hi) == (0, 23, 1, 24),
        f"start {_s_lo}-{_s_hi}, end {_e_lo}-{_e_hi}",
        # A day ending at 0 or starting at 24 is empty whatever the other
        # end says; those values would only feed the validator noise.
    )

_empty_opts = _b3_submit(
    _b3_options(),
    "comfort",
    {const.CONF_DAY_START_HOUR: 10, const.CONF_DAY_END_HOUR: 10},
)
R.check(
    "an empty day reaches comfort_band on the options page as day_window_empty",
    _empty_opts.get("type") == "form"
    and _empty_opts.get("errors") == {const.CONF_DAY_END_HOUR: "day_window_empty"},
    f"type {_empty_opts.get('type')}, errors {_empty_opts.get('errors')}",
)
_empty_setup = _b3_submit(
    _fresh_flow(),
    "temperature",
    {const.CONF_DAY_START_HOUR: 10, const.CONF_DAY_END_HOUR: 10},
)
R.check(
    "and on the setup flow",
    _empty_setup.get("type") == "form"
    and _empty_setup.get("errors") == {const.CONF_DAY_END_HOUR: "day_window_empty"},
    f"type {_empty_setup.get('type')}, errors {_empty_setup.get('errors')}",
)
_afternoon = _b3_submit(
    _b3_options(),
    "comfort",
    {const.CONF_DAY_START_HOUR: 14, const.CONF_DAY_END_HOUR: 17},
)
R.check(
    "an afternoon-only heating day, impossible before, saves",
    _afternoon.get("type") == "menu",
    f"type {_afternoon.get('type')}, errors {_afternoon.get('errors')}",
)

# --- #171: a hot-water window shorter than a planning step is refused --------
R.check(
    "the shortest accepted window is exactly one planning step",
    dhw_schedule.MIN_WINDOW_MINUTES == OptimizationConfig().time_step_minutes,
    f"{dhw_schedule.MIN_WINDOW_MINUTES} vs {OptimizationConfig().time_step_minutes}",
    # Window membership is tested at each step's start, so a window shorter
    # than a step can sit between two starts and bind nothing at all.
)


def _dhw_verdicts(spec):
    setup = _b3_submit(_fresh_flow(), "dhw", {const.CONF_DHW_WINDOWS: spec})
    saved = _b3_submit(_b3_options(), "hot_water", {const.CONF_DHW_WINDOWS: spec})
    return (
        (setup.get("errors") or {}).get(const.CONF_DHW_WINDOWS),
        (saved.get("errors") or {}).get(const.CONF_DHW_WINDOWS),
        saved,
    )


_one_minute = _dhw_verdicts("06:05-06:06")
R.check(
    "a one-minute window is refused on both flows, by name",
    _one_minute[:2] == (dhw_schedule.ERROR_TOO_SHORT,) * 2,
    str(_one_minute[:2]),
)
R.check(
    "and the error message's minimum is supplied to it",
    _b3_placeholders(strings["options"]["error"][dhw_schedule.ERROR_TOO_SHORT])
    <= set(_one_minute[2].get("description_placeholders") or {}),
    str(_one_minute[2].get("description_placeholders")),
)
R.check(
    "a window of exactly one step saves on both",
    _dhw_verdicts("06:00-06:15")[:2] == (None, None),
    str(_dhw_verdicts("06:00-06:15")[:2]),
)
R.check(
    "a wrapping ten-minute window is measured across midnight, not as 23 hours",
    _dhw_verdicts("23:55-00:05")[:2] == (dhw_schedule.ERROR_TOO_SHORT,) * 2,
)
R.check(
    "a weekly spec is judged segment by segment",
    _dhw_verdicts("weekdays 06:00-08:30, weekend 08:00-08:01")[:2]
    == (dhw_schedule.ERROR_TOO_SHORT,) * 2,
)
R.check(
    "an unreadable spec keeps its original error",
    _dhw_verdicts("banana")[:2] == (dhw_schedule.ERROR_INVALID,) * 2,
)
R.check(
    "the default windows every install ships with still save",
    _dhw_verdicts(const.DEFAULT_DHW_WINDOWS)[:2] == (None, None),
)
R.check(
    "the too-short error is translated on both flows in every language",
    all(
        dhw_schedule.ERROR_TOO_SHORT in strings[flow_name]["error"]
        and dhw_schedule.ERROR_TOO_SHORT in files[lang][flow_name]["error"]
        for lang in files
        for flow_name in ("config", "options")
    ),
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
    _tm2.async_step_thermal_model(
        {const.CONF_HEAT_PUMP_MIN_POWER: 2.0, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
R.check(
    "and saves a floor that fits under it",
    _tm2res.get("type") == "create_entry"
    and (_tm2res.get("data") or {}).get(const.CONF_HEAT_PUMP_MIN_POWER) == 2.0,
    str(_tm2res.get("type")),
)

# D3-08: ``_dhw_min_too_close`` guards against a DHW minimum that leaves less
# than ``DHW_MIN_TEMP_SETPOINT_MARGIN`` (5.0°C) of deadband below the
# setpoint -- an impossible configuration the solver cannot express (tank
# limits are soft penalties, so it never errors downstream, it just sits in
# permanent slight violation). Only key-presence-style closure checks exist
# elsewhere; this drives both the initial setup flow's ``async_step_dhw``
# and the options flow's ``async_step_hot_water`` end-to-end with a
# violating submission (setpoint 50, minimum 47 -- 3°C of deadband, inside
# the 5°C margin) and a passing boundary case (minimum 40 -- 10°C of
# deadband).
_dhw_bad = _fresh_flow()
_dhw_bad_res = asyncio.run(
    _dhw_bad.async_step_dhw(
        {
            const.CONF_DHW_SETPOINT: 50.0,
            const.CONF_DHW_MIN_TEMP: 47.0,
            const.CONF_DHW_WINDOWS: "",
        }
    )
)
R.check(
    "the setup flow rejects a DHW minimum inside the required margin",
    _dhw_bad_res["type"] == "form"
    and _dhw_bad_res.get("errors", {}).get(const.CONF_DHW_MIN_TEMP)
    == "dhw_min_too_close",
    f"got type={_dhw_bad_res.get('type')} errors={_dhw_bad_res.get('errors')}; "
    "a disabled validator would silently accept a config the solver can "
    "never fully satisfy",
)
_dhw_good = _fresh_flow()
_dhw_good_res = asyncio.run(
    _dhw_good.async_step_dhw(
        {
            const.CONF_DHW_SETPOINT: 50.0,
            const.CONF_DHW_MIN_TEMP: 40.0,
            const.CONF_DHW_WINDOWS: "",
        }
    )
)
R.check(
    "a safely-spaced DHW minimum is accepted, so this is not a blanket rejector",
    not _dhw_good_res.get("errors", {}).get(const.CONF_DHW_MIN_TEMP),
    str(_dhw_good_res.get("errors")),
)
_dhw_opt_bad = options(FakeEntry(data={const.CONF_DHW_SETPOINT: 50.0}))
_dhw_opt_bad.hass = FakeHass()
_dhw_opt_bad_res = asyncio.run(
    _dhw_opt_bad.async_step_hot_water(
        {const.CONF_DHW_MIN_TEMP: 47.0, const.CONF_DHW_WINDOWS: ""}
    )
)
R.check(
    "the options flow enforces the same deadband against the stored setpoint",
    _dhw_opt_bad_res["type"] == "form"
    and _dhw_opt_bad_res.get("errors", {}).get(const.CONF_DHW_MIN_TEMP)
    == "dhw_min_too_close",
    str(_dhw_opt_bad_res.get("errors")),
)
_dhw_opt_good = options(FakeEntry(data={const.CONF_DHW_SETPOINT: 50.0}))
_dhw_opt_good.hass = FakeHass()
_dhw_opt_good_res = asyncio.run(
    _dhw_opt_good.async_step_hot_water(
        {const.CONF_DHW_MIN_TEMP: 40.0, const.CONF_DHW_WINDOWS: ""}
    )
)
R.check(
    "the options flow's boundary case still saves",
    not _dhw_opt_good_res.get("errors", {}).get(const.CONF_DHW_MIN_TEMP),
    str(_dhw_opt_good_res.get("errors")),
)

# --- The dialog behaviour itself (#100) -------------------------------------
R.section("The options dialog stays open after a save")
# Write-through, immediately: the same async_update_entry a save-and-close
# always triggered via create_entry, not a deferral keyed on anything.
# (Fresh entry, not _legacy: that name is a sorted list by this point.)
_wt = options(FakeEntry())
_wt.hass = FakeHass()
asyncio.run(_wt.async_step_comfort(None))
_wtres = asyncio.run(
    _wt.async_step_comfort(
        {const.CONF_COMFORT_TEMP_DAY: 21.5, const.CONF_COMFORT_TEMP_NIGHT: 19.0}
    )
)
R.check(
    "a save returns to the section menu and writes through at once",
    _wtres.get("type") == "menu"
    and _wt._entry.options.get(const.CONF_COMFORT_TEMP_DAY) == 21.5
    and _wt.hass.config_entries.updated,
    f"type {_wtres.get('type')}, options {_wt._entry.options}",
)
R.check(
    "the after-save choice itself never persists",
    const.CONF_AFTER_SAVE not in _wt._entry.options,
    str(sorted(_wt._entry.options)),
)
# An advanced page comes back to the advanced menu, not the top one.
# (_translated_menu under the stub resolves to the step keys, so the
# assertion reads keys, not labels.)
_adv = options(FakeEntry())
_adv.hass = FakeHass()
asyncio.run(_adv.async_step_solar_pv(None))
_advres = asyncio.run(_adv.async_step_solar_pv(_adv._entry.options))
_adv_keys = [m[0] if isinstance(m, (tuple, list)) else m
             for m in (_advres.get("menu_options") or [])]
R.check(
    "an advanced page returns to the advanced menu",
    _advres.get("type") == "menu"
    and "solar_pv" in _adv_keys
    and "comfort" not in _adv_keys
    and "advanced" not in _adv_keys,
    f"menu: {_adv_keys}",
)
# The close choice keeps the historical behaviour exactly.
_cl = options(FakeEntry())
_cl.hass = FakeHass()
asyncio.run(_cl.async_step_comfort(None))
_clres = asyncio.run(
    _cl.async_step_comfort(
        {const.CONF_COMFORT_TEMP_DAY: 21.5, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
R.check(
    "the close choice ends the dialog with a create_entry, as before",
    _clres.get("type") == "create_entry"
    and (_clres.get("data") or {}).get(const.CONF_COMFORT_TEMP_DAY) == 21.5
    and not _cl.hass.config_entries.updated,
    f"type {_clres.get('type')}, mid-flow updates {_cl.hass.config_entries.updated}",
)

# Every error key used by the validators exists in all three string files.
_error_codes = {
    "min_above_target",
    "max_below_target",
    "night_above_day",
    "day_window_empty",
    "comfort_outside_band",
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
R.section("Service registration (action-setup)")

# action-setup (Bronze, #180): the services belong to the domain, not to an
# entry. ``async_setup`` registers them once, before any entry exists, so an
# automation naming one validates while every entry is unloaded; an entry's
# setup adds nothing and re-registers nothing; the last unload removes
# nothing. The honest FakeServices registry is the witness at each step, and
# what async_setup leaves in it is compared name for name with the
# catalogue in services.yaml. A call that finds no loaded entry is refused
# with a ServiceValidationError rather than silently doing nothing.
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

_reg_hass = FakeHass()
R.check(
    "the integration has an async_setup that succeeds without any entry",
    asyncio.run(ha_setup_component(integration, _reg_hass)) is True
    and const.DOMAIN in _reg_hass.config.components,
)
_reg_after_setup = dict(_reg_hass.services.async_services().get(const.DOMAIN, {}))
R.check(
    "async_setup registers every service services.yaml documents, with no entry loaded",
    set(_reg_after_setup) == set(services),
    f"registered {sorted(_reg_after_setup)}, documented {sorted(services)}",
)
_reg_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
)
asyncio.run(ha_setup_entry(integration, _reg_hass, _reg_entry))
R.check(
    "an entry's setup hands its coordinator to the entry as runtime_data",
    isinstance(getattr(_reg_entry, "runtime_data", None), HeatPumpOptimizerCoordinator),
)
R.check(
    "an entry's setup registers nothing and replaces no handler",
    dict(_reg_hass.services.async_services().get(const.DOMAIN, {}))
    == _reg_after_setup,
)
asyncio.run(ha_unload_entry(integration, _reg_hass, _reg_entry))
R.check(
    "every service is still registered after the last entry unloads",
    dict(_reg_hass.services.async_services().get(const.DOMAIN, {}))
    == _reg_after_setup,
)
try:
    asyncio.run(
        _reg_hass.services.async_call(const.DOMAIN, const.SERVICE_RUN_OPTIMIZATION, {})
    )
    _no_entry_outcome = "returned normally"
except ServiceValidationError as err:
    _no_entry_outcome = f"refused: {err}"
R.check(
    "a call with no loaded entry is refused, naming the reason",
    _no_entry_outcome.startswith("refused") and "loaded" in _no_entry_outcome,
    _no_entry_outcome,
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
asyncio.run(ha_setup_entry(integration, _svc_hass, _svc_entry))
_svc_coord = _svc_entry.runtime_data
R.check(
    "setup produced a live coordinator behind the services",
    isinstance(_svc_coord, HeatPumpOptimizerCoordinator),
)

# D6-02 (#172), generalised: every ``example:`` in services.yaml, fed as one
# payload to the schema the service actually registered. The registry is the
# honest source -- a module constant can be renamed without the registration
# following, and it is the registered schema Home Assistant dispatches through.
_bad_examples = []
for _svc_name, _svc_spec in services.items():
    _svc_examples = {
        field: spec["example"]
        for field, spec in (_svc_spec.get("fields") or {}).items()
        if "example" in spec
    }
    if not _svc_examples:
        continue
    _svc_schema = _svc_hass.services._schemas[(const.DOMAIN, _svc_name)]
    _svc_ok, _svc_why = _example_passes(_svc_schema, _svc_examples)
    if not _svc_ok:
        _bad_examples.append(f"{_svc_name}: {_svc_why}")
R.check(
    "every documented service example passes the schema its service registered",
    not _bad_examples,
    "; ".join(_bad_examples)[:300],
)

# D6-03 (#274): inter_zone_heat_transfer and window_area admitted 0 on three
# surfaces the set_thermal_parameters schema's own ``_positive()`` already
# rejected -- the services.yaml selectors, the two config-flow forms that
# ask for these fields (initial setup and options/preset), and a value
# stored before any validation ran. Widening every surface to the same
# ``const.POSITIVE_PARAM_FLOOR`` closes all three; this pins all three so
# a regression on any one of them fails here, not only in the field.
_stp_schema = _svc_hass.services._schemas[
    (const.DOMAIN, const.SERVICE_SET_THERMAL_PARAMS)
]
_zero_ok, _ = _example_passes(
    _stp_schema, {"inter_zone_heat_transfer": 0, "window_area": 0}
)
R.check(
    "the set_thermal_parameters schema still rejects 0 for both fields",
    not _zero_ok,
    "0 was accepted -- _positive()'s floor moved",
)

_yaml_selectors = {
    f: services["set_thermal_parameters"]["fields"][f]["selector"]["number"]["min"]
    for f in ("inter_zone_heat_transfer", "window_area")
}
R.check(
    "services.yaml's selectors floor both fields at POSITIVE_PARAM_FLOOR, not 0",
    all(v == const.POSITIVE_PARAM_FLOOR for v in _yaml_selectors.values()),
    f"{_yaml_selectors}",
)

_zones_form = asyncio.run(_fresh_flow().async_step_zones(None))["data_schema"]
_preset_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "t", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_thermal_flow = options(_preset_entry)
_thermal_flow.hass = FakeHass()
_thermal_form = asyncio.run(_thermal_flow.async_step_thermal_model(None))["data_schema"]
_preset_flow = options(_preset_entry)
_preset_flow.hass = FakeHass()
_preset_form2 = asyncio.run(_preset_flow.async_step_building_preset(None))[
    "data_schema"
]


def _selector_min(schema, conf_key: str) -> float:
    for key, validator in schema.schema.items():
        if str(getattr(key, "schema", key)) == conf_key:
            return validator.config["min"]
    raise KeyError(conf_key)


_config_flow_minimums = {
    "zones/inter_zone_heat_transfer": _selector_min(
        _zones_form, const.CONF_INTER_ZONE_TRANSFER
    ),
    "zones/window_area": _selector_min(_zones_form, const.CONF_WINDOW_AREA),
    "thermal_model/inter_zone_heat_transfer": _selector_min(
        _thermal_form, const.CONF_INTER_ZONE_TRANSFER
    ),
    "building_preset/window_area": _selector_min(_preset_form2, const.CONF_WINDOW_AREA),
}
R.check(
    "all four config-flow forms floor the same two fields at POSITIVE_PARAM_FLOOR, not 0",
    all(v == const.POSITIVE_PARAM_FLOOR for v in _config_flow_minimums.values()),
    f"{_config_flow_minimums}",
)

_zeroed_params = ThermalParameters(inter_zone_transfer=0.0, window_area=0.0)
R.check(
    "a ThermalParameters constructed with 0 for either field is clamped off it",
    _zeroed_params.inter_zone_transfer >= const.POSITIVE_PARAM_FLOOR
    and _zeroed_params.window_area >= const.POSITIVE_PARAM_FLOOR,
    f"inter_zone_transfer={_zeroed_params.inter_zone_transfer} "
    f"window_area={_zeroed_params.window_area}",
)

# Several entries (runtime-data, action-setup): the handlers resolve their
# targets at call time from the entries Home Assistant holds, and act on
# every LOADED one -- or on the one ``entry_id`` names, which must exist and
# be loaded. A second entry is set up alongside the first, then unloaded
# again so the single-entry checks below see exactly one.
_svc_entry2 = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "y", const.CONF_WEATHER_ENTITY: "weather.home"},
    entry_id="second_pump",
)
asyncio.run(ha_setup_entry(integration, _svc_hass, _svc_entry2))
_multi_log: list[str] = []


def _multi_record(name):
    async def _fn(*args, **kwargs):
        _multi_log.append(name)

    return _fn


_svc_coord.async_run_optimization = _multi_record("first")
_svc_entry2.runtime_data.async_run_optimization = _multi_record("second")
_svc_coord.async_clear_manual_plan = _multi_record("clear:first")
_svc_entry2.runtime_data.async_clear_manual_plan = _multi_record("clear:second")
asyncio.run(
    _svc_hass.services.async_call(const.DOMAIN, const.SERVICE_RUN_OPTIMIZATION, {})
)
R.check(
    "an untargeted call reaches every loaded entry",
    sorted(_multi_log) == ["first", "second"],
    str(_multi_log),
)
_multi_log.clear()
_cleared = asyncio.run(
    _svc_hass.services.async_call(
        const.DOMAIN, const.SERVICE_CLEAR_MANUAL_PLAN, {"entry_id": "second_pump"}
    )
)
R.check(
    "an entry_id-targeted call reaches only that entry",
    _multi_log == ["clear:second"] and _cleared == {"cleared": ["second_pump"]},
    f"{_multi_log} {_cleared}",
)


def _targeted_outcome(entry_id):
    try:
        asyncio.run(
            _svc_hass.services.async_call(
                const.DOMAIN, const.SERVICE_CLEAR_MANUAL_PLAN, {"entry_id": entry_id}
            )
        )
        return "returned normally"
    except ServiceValidationError as err:
        return str(err)


R.check(
    "an entry_id nobody has is refused by name",
    "nobody" in _targeted_outcome("nobody"),
    _targeted_outcome("nobody"),
)
asyncio.run(ha_unload_entry(integration, _svc_hass, _svc_entry2))
R.check(
    "an entry that exists but is not loaded is refused as not loaded",
    "not loaded" in _targeted_outcome("second_pump"),
    _targeted_outcome("second_pump"),
)
_multi_log.clear()
asyncio.run(
    _svc_hass.services.async_call(const.DOMAIN, const.SERVICE_RUN_OPTIMIZATION, {})
)
R.check(
    "after the unload an untargeted call reaches only the entry still loaded",
    _multi_log == ["first"],
    str(_multi_log),
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

# v5.1.7 — the comfort band, on every path that writes it.
#
# `apply_schedule` writes `comfort_temp_day` into stored options behind a
# 5-30 range check and nothing else, so a daytime temperature below the
# stored night one went in unremarked: the plan then sat in a contradiction
# the optimizer never reports, because the bounds are priced rather than
# fenced. The service now runs the config flow's own band rules, against the
# effective pair, per entry.
_band_before = _svc_entry.options.get(const.CONF_COMFORT_TEMP_DAY)
_band_rejected = None
try:
    _svc_call(const.SERVICE_APPLY_SCHEDULE, {"comfort_temp_day": 18.0})
except ServiceValidationError as err:
    _band_rejected = str(err)
R.check(
    "apply_schedule refuses a daytime temperature below the stored night one",
    _band_rejected is not None and "night" in _band_rejected.lower(),
    f"stored night is {const.DEFAULT_COMFORT_TEMP_NIGHT}; got {_band_rejected!r}",
)
R.check(
    "and nothing was written when it refused",
    _svc_entry.options.get(const.CONF_COMFORT_TEMP_DAY) == _band_before,
    str(_svc_entry.options.get(const.CONF_COMFORT_TEMP_DAY)),
)
_svc_call(const.SERVICE_APPLY_SCHEDULE, {"comfort_temp_day": 22.0})
R.check(
    "a daytime temperature that clears the band still writes",
    _svc_entry.options.get(const.CONF_COMFORT_TEMP_DAY) == 22.0,
)

# Only violations the call INTRODUCES may refuse it. Judging the merged
# result outright made the service throw on a contradiction already sitting
# in the options and untouched by the call -- and one is genuinely out there,
# because the pre-5.1.7 slider stored `target 24` against a `max 23` ceiling
# unchecked. A nightly `dhw_windows` automation would then have started
# failing at 03:00 about a ceiling it never mentioned.
_pre_hass = FakeHass()
_pre_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_pre_entry.options = {const.CONF_TARGET_TEMP: 24.0}   # max stays at 23.0
asyncio.run(ha_setup_entry(integration, _pre_hass, _pre_entry))


def _pre_call(payload):
    try:
        asyncio.run(
            _pre_hass.services.async_call(
                const.DOMAIN, const.SERVICE_APPLY_SCHEDULE, payload
            )
        )
        return None
    except ServiceValidationError as err:
        return str(err)


R.check(
    "a call touching no band field survives a contradiction already stored",
    _pre_call({"dhw_windows": "06:00-08:00"}) is None
    and _pre_call({"dhw_min_temperature": 45.0}) is None
    and _pre_call({"day_start_hour": 6, "day_end_hour": 22}) is None,
    "the stored target 24 vs max 23 is not this call's doing",
)
R.check(
    "and the write it asked for actually happened",
    _pre_entry.options.get(const.CONF_DHW_WINDOWS) == "06:00-08:00"
    and _pre_entry.options.get(const.CONF_DAY_START_HOUR) == 6,
)
R.check(
    "but a NEW violation is still refused on the same broken entry",
    "night" in (_pre_call({"comfort_temp_day": 18.0}) or "").lower(),
    str(_pre_call({"comfort_temp_day": 18.0})),
)

# The stored contradiction is worth telling the user about -- as a repair
# issue, which is where "your configuration disagrees with itself" belongs,
# not as an exception thrown by an unrelated service call.
_pre_coord = _pre_entry.runtime_data
asyncio.run(_pre_coord._update_current_state())
_band_issues = [
    i for i in getattr(_pre_hass, "issues", [])
    if i[1] == "comfort_band_contradiction"
]
R.check(
    "a stored contradiction raises a repair issue instead",
    len(_band_issues) == 1
    and _band_issues[0][2].get("translation_key") == "comfort_band_contradiction"
    and "23" in _band_issues[0][2]["translation_placeholders"]["problem"],
    str(_band_issues),
)
# Same reload shape as the lower-floor notice: correcting the band writes
# options and reloads, so the clear must not be gated on an in-memory flag.
_fixed_entry = FakeEntry(
    data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
)
_fixed_coord = HeatPumpOptimizerCoordinator(_pre_hass, _fixed_entry)
asyncio.run(_fixed_coord._update_current_state())
R.check(
    "and correcting the band clears it across the reload",
    not [
        i for i in getattr(_pre_hass, "issues", [])
        if i[1] == "comfort_band_contradiction"
    ],
)
_window_rejected = None
try:
    _svc_call(
        const.SERVICE_APPLY_SCHEDULE, {"day_start_hour": 20, "day_end_hour": 8}
    )
except ServiceValidationError as err:
    _window_rejected = str(err)
R.check(
    "the empty-day-window rule survived the move into the shared rules",
    _window_rejected is not None and "daytime period" in _window_rejected,
    f"got {_window_rejected!r}",
)

# The other bypass: the thermostat card's slider writes `target_temperature`
# through the coordinator, which persisted it with no band check at all --
# and the slider's own maximum was `max_temp + 1`, so its top notch stored a
# target above the ceiling by construction.
_target_before = _svc_coord._opt_config.target_temp
_target_rejected = None
try:
    asyncio.run(_svc_coord.async_set_target_temperature(26.0))
except ServiceValidationError as err:
    _target_rejected = str(err)
R.check(
    "the climate entity cannot store a target above the comfort ceiling",
    _target_rejected is not None and "23" in _target_rejected,
    f"ceiling is {const.DEFAULT_MAX_TEMP}; got {_target_rejected!r}",
)
R.check(
    "and the in-memory target is untouched by the refusal",
    _svc_coord._opt_config.target_temp == _target_before
    and _svc_entry.options.get(const.CONF_TARGET_TEMP) is None,
    f"{_svc_coord._opt_config.target_temp} / "
    f"{_svc_entry.options.get(const.CONF_TARGET_TEMP)}",
)
asyncio.run(_svc_coord.async_set_target_temperature(22.0))
R.check(
    "a target inside the band is stored as before",
    _svc_coord._opt_config.target_temp == 22.0
    and _svc_entry.options.get(const.CONF_TARGET_TEMP) == 22.0,
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


# ===========================================================================
# Release metadata
# ===========================================================================
R.section("Release metadata")

# A release is spread over four files that nothing tied together: VERSION,
# the manifest HACS reads, the notes users read, and the card's own version
# banner. Every one of them was bumped by hand, so any one of them could be
# forgotten -- and the claim file was worse than forgotten, it was inherited:
# v4.0.7, v4.2.0 and v4.3.0 all failed CI on main with stale claims left by
# the release before them, for code that was never wrong.
import re as _re
import tempfile as _tempfile

import env_drift as _env_drift
import closure as _closure

# --- the scoped gate's one exception to "the whole integration" -------------
#
# `_widen` gives env_drift.py the whole integration because no tracer can see
# which files a capture in another worktree depended on, and a second rule in
# `select` runs it for any custom_components/ change whether or not the
# closure saw the file. Both exclude the bundled card, and the exclusion was
# measured rather than argued -- two captures on the same tree with
# `env_drift.py --capture . <out> --all`:
#
#   null control      the card asset edited (an added statement, CARD_VERSION
#                     5.4.19 -> 9.9.99): all 55 scenarios byte-identical,
#                     sha256 1f1dcb966bdf7ae9... on both sides
#   positive control  one token in thermal_model.py (`* dt` -> `* dt * 1.0001`):
#                     the captures differ
#
# frontend.py registers `www/` as a static path and never opens the file, so
# there is no path by which its bytes reach a capture. These checks hold the
# rule to exactly that: the card is out, and everything else stays in.
_ED = "tests/env_drift.py"
_CARD_ASSET = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
_ed_closure = set(
    __import__("json").loads(_closure.CLOSURES.read_text())["closures"][_ED]
)
R.check(
    "the drift capture's closure excludes the bundled card",
    _CARD_ASSET not in _ed_closure,
    "a capture cannot read the card, so it must not select on it",
)
_integration_py = {
    str(q.relative_to(_closure.ROOT))
    for q in (_closure.ROOT / "custom_components" / "heatpump_optimizer")
    .rglob("*.py")
    if "__pycache__" not in str(q)
}
R.check(
    "and still covers every python file of the integration",
    _integration_py <= _ed_closure,
    f"missing {sorted(_integration_py - _ed_closure)[:3]}",
)
R.check(
    "a card-only change does not select the drift capture",
    _ED not in _closure.select([_CARD_ASSET])["run"],
    "the most expensive script in the suite ran to prove a plan that "
    "could not have moved",
)
R.check(
    "an integration python change still does",
    _ED in _closure.select(
        ["custom_components/heatpump_optimizer/optimizer.py"])["run"],
    "the belt-and-braces rule must survive being narrowed",
)
# The two rules are independent and each has to be pinned. The one above is
# about SELECTION and reads the committed closures; this one is about the
# WIDENING that produces them, which otherwise only the `closures` job on main
# would catch -- one merge later, and only after a full re-derivation.
_widened = {_ED: set(), "tests/golden.py": set()}
_closure._widen(_widened)
R.check(
    "the widening rule itself leaves the card out",
    _CARD_ASSET not in _widened[_ED],
    "re-widening to the whole integration puts the card back in the closure",
)
R.check(
    "while still widening to the rest of the integration",
    "custom_components/heatpump_optimizer/coordinator.py" in _widened[_ED],
    "the rule must narrow by one subtree, not collapse",
)

# The scoped gate refuses to skip anything when a changed file is in no
# closure -- an unmeasured file is not a safe skip. That is right, and it was
# quietly making gates full: renaming one identifier in setup_qa_render.mjs, a
# script people run by hand, ran all sixteen scripts including stress.py.
# Every tracked file must therefore sit in exactly one of four places: a
# measured closure, INERT, GATE_FILES, or SLOW_GATED. This is the check that
# says so, and it is the reason a new file cannot silently cost every future
# pull request a full suite.
_orphans = _closure.orphan_files()
R.check(
    "every tracked file is either measured or deliberately classified",
    not _orphans,
    "these force the FULL suite when touched: " + ", ".join(_orphans[:8]),
)
R.check(
    "a hand-run QA script does not drag the whole suite in",
    "tests/setup_qa_render.mjs" not in _closure.select(
        ["tests/setup_qa_render.mjs"])["run"]
    or _closure.select(["tests/setup_qa_render.mjs"])["mode"] == "scoped",
    "an unmeasured helper forced sixteen scripts to run",
)
R.check(
    "but changing how the closures are derived still runs everything",
    _closure.select(["tests/derive_closures.sh"])["mode"] == "full",
    "the lanes decide how every recording is taken; that invalidates them all",
)

# --- when the closures CHECK itself runs (#354) -----------------------------
#
# `select` above decides which tests a change needs. `affected` decides
# whether the job that checks the table `select` trusts needs to run at all.
# It ran on a pull request only when the diff ADDED a file under
# custom_components/, so a change to what a test READS was checked one merge
# too late -- five times (#214, #320, #332, #340, #349), each a green pull
# request, a red main, and a second pull request to repair it.
_A_DOCS = _closure.affected(["docs/audit-2026-09.md", "LICENSE", "tests/README.md"])
R.check(
    "a docs-only change still costs the closures check nothing",
    _A_DOCS["case"] == "skip",
    f"case is {_A_DOCS['case']}: {_A_DOCS['reason']} -- if a docs pull "
    "request pays 12-22 minutes the scoping this replaces was pointless",
)
# The skip is decided by the TABLE, not by the hand-written INERT list, and
# the order is why. quality_scale.yaml is on INERT and inside env_drift's
# rule-widened closure at the same time; asking "is every changed file inert?"
# first would skip a change to a file the table says a test reads.
_QS = "custom_components/heatpump_optimizer/quality_scale.yaml"
_A_QS = _closure.affected([_QS])
R.check(
    "a file that is both INERT and inside a recorded closure is not skipped",
    _closure.is_inert(_QS) and _A_QS["case"] == "scoped",
    f"{_QS} is inert={_closure.is_inert(_QS)} and case={_A_QS['case']}: the "
    "hand list may license a file's ABSENCE from the table, never override it",
)
R.check(
    "a gate file re-derives everything, as it does for selection",
    _closure.affected(["tests/run.sh"])["case"] == "full"
    and _closure.affected([".github/workflows/tests.yml"])["case"] == "full",
    "changing the gate invalidates every closure at once",
)
# The rule that catches the five incidents, and it carries no path prefix: an
# unmeasured file is unmeasured wherever it lives. The draft said "under
# custom_components/", which fails OPEN for a file type nobody thought about.
R.check(
    "a file in no recorded closure re-derives everything, wherever it lives",
    _closure.affected(["custom_components/heatpump_optimizer/nonesuch.py"])["case"]
    == "full"
    and _closure.affected(["tests/nonesuch_helper.py"])["case"] == "full",
    "nothing can be inferred about a file the table has never measured",
)
R.check(
    "an empty diff re-derives everything rather than nothing",
    _closure.affected([])["case"] == "full",
    "'no changed files could be determined' must fail closed",
)
# A script another script drives in a subprocess reaches the table only
# through its driver's fold, and --single cannot record it.
R.check(
    "a change to a subprocess-driven script re-derives everything",
    _closure.affected(["tests/dst_checks.py"])["case"] == "full",
    "re-deriving features.py alone would not see dst_checks.py's new reads",
)
# The cost claim: one script's closure touched re-derives ONE entry.
_A_ONE = _closure.affected(["tests/open_meteo.py"])
R.check(
    "a diff inside one closure re-derives one entry, not eighteen",
    _A_ONE["case"] == "scoped" and _A_ONE["rederive"] == ["tests/open_meteo.py"],
    f"case={_A_ONE['case']} rederive={_A_ONE['rederive']}",
)
# A recording is a real run: card.mjs reads the payload plan_view.py writes,
# so re-deriving the consumer alone records a run that found no payload.
_A_CARD = _closure.affected([_CARD_ASSET])
R.check(
    "a scoped re-derive pulls in the producer of anything it selects",
    "tests/card.mjs" in _A_CARD["rederive"]
    and "tests/plan_view.py" in _A_CARD["rederive"]
    and _A_CARD["why"]["tests/plan_view.py"]["via"] == "producer of tests/card.mjs",
    f"rederive={_A_CARD['rederive']}",
)
# The workflow reads these two files and nothing else. If they stop agreeing
# with the plan the job runs the wrong scripts and says so nowhere.
with _tempfile.TemporaryDirectory() as _td:
    _closure.write_affected(_A_ONE, Path(_td))
    _case_f = (Path(_td) / "affected.case").read_text().strip()
    _scripts_f = (Path(_td) / "affected.scripts").read_text().split()
    R.check(
        "the files the workflow reads carry the plan the predicate made",
        _case_f == _A_ONE["case"] and _scripts_f == _A_ONE["rederive"],
        f"affected.case={_case_f!r} affected.scripts={_scripts_f}",
    )

# --- the scoped path's check is the same check ------------------------------
#
# `check --partial` drops one test and one only: "a selectable script with no
# recording at all", which a scoped re-derive fails by construction. The
# under-approximation comparison -- the thing the job exists for -- is
# identical on both paths, and this proves it by feeding a record that lies.
import contextlib as _contextlib
import io as _io

_committed = json.loads(_closure.CLOSURES.read_text())["closures"]


def _check_with(files: list[str], partial: bool) -> int:
    with _tempfile.TemporaryDirectory() as td:
        (Path(td) / "open_meteo.py.json").write_text(json.dumps({
            "script": "tests/open_meteo.py", "rc": 0, "seconds": 1.0,
            "files": files, "spawned": [], "how": "test",
        }))
        with _contextlib.redirect_stdout(_io.StringIO()), \
                _contextlib.redirect_stderr(_io.StringIO()):
            return _closure.check(Path(td), partial=partial)


_honest = list(_committed["tests/open_meteo.py"])
R.check(
    "a one-script re-derive is refused unless it says it is partial",
    _check_with(_honest, partial=False) == 1,
    "the roster check must still fire on the full path, where it means "
    "'a selectable script was never recorded' (#90)",
)
R.check(
    "and is accepted when it does",
    _check_with(_honest, partial=True) == 0,
    "the scoped path records only what the diff can reach",
)
R.check(
    "but a partial check still fails on a closure that under-approximates",
    _check_with(_honest + ["tests/nonesuch_dependency.py"], partial=True) == 1,
    "--partial must drop the roster test and nothing else, or the scoped "
    "path is a gate that cannot fail",
)
# The precondition that makes dropping the roster test safe: `affected` never
# returns `scoped` on a tree where a selectable script has no closure, so the
# scoped path cannot run where that test would have fired.
with _tempfile.TemporaryDirectory() as _td:
    _short = Path(_td) / "closures.json"
    _short.write_text(json.dumps({"closures": {
        k: v for k, v in _committed.items() if k != "tests/open_meteo.py"}}))
    _real = _closure.CLOSURES
    try:
        _closure.CLOSURES = _short
        _A_SHORT = _closure.affected(["custom_components/heatpump_optimizer/optimizer.py"])
    finally:
        _closure.CLOSURES = _real
R.check(
    "a selectable script with no closure forces the full re-derivation",
    _A_SHORT["case"] == "full" and "open_meteo" in _A_SHORT["reason"],
    f"case={_A_SHORT['case']} reason={_A_SHORT['reason']!r} -- this is what "
    "lets the scoped path drop the roster check safely",
)


_version = Path("VERSION").read_text().strip()
R.check(
    "VERSION holds a plain X.Y.Z release number",
    _env_drift._looks_like_version(_version),
    f"VERSION reads {_version!r} -- every check below compares against it",
)
_manifest_version = json.loads((ROOT / "manifest.json").read_text()).get("version")
R.check(
    "manifest.json carries the release version",
    _manifest_version == _version,
    f"VERSION says {_version}, manifest.json says {_manifest_version} -- "
    "edit custom_components/heatpump_optimizer/manifest.json",
)

_notes_heading = _re.search(
    r"^## v(\d+\.\d+\.\d+)", Path("RELEASE_NOTES.md").read_text(), _re.M
)
R.check(
    "RELEASE_NOTES.md opens with this release",
    _notes_heading is not None and _notes_heading.group(1) == _version,
    f"VERSION says {_version}, the first heading is "
    f"{'v' + _notes_heading.group(1) if _notes_heading else '<none>'} -- "
    "add this release's section to the top of RELEASE_NOTES.md",
)

# Same rule env_drift.py enforces, asserted here so it holds in every
# GOLDEN_MODE -- including the strict runs where run.sh skips env_drift
# entirely because the comparison ref is unreachable.
_claim_problem = _env_drift.claim_version_error(".")
R.check(
    "the drift claim file is stamped for this release",
    _claim_problem is None,
    " ".join((_claim_problem or "").split()),
)


def _version_tuple(text: str) -> tuple[int, ...]:
    """Comparable form of an X.Y.Z string, or () when it is not one."""
    if not _env_drift._looks_like_version(text):
        return ()
    return tuple(int(part) for part in text.split("."))


_card_path = ROOT / "www" / "heatpump-optimizer-card.js"
_card_match = _re.search(
    r'CARD_VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']', _card_path.read_text()
)
R.check(
    "the card declares a valid CARD_VERSION",
    _card_match is not None,
    f"no `const CARD_VERSION = \"X.Y.Z\"` in {_card_path}",
)
# A card-only release bumps both files; an integration-only release leaves
# the card behind, which is legal. Ahead of VERSION is not: it would ship a
# banner advertising a release that does not exist.
R.check(
    "CARD_VERSION does not run ahead of VERSION",
    _card_match is not None
    and _version_tuple(_version) != ()
    and _version_tuple(_card_match.group(1)) <= _version_tuple(_version),
    f"card says {_card_match.group(1) if _card_match else '?'}, VERSION says "
    f"{_version} -- lower CARD_VERSION in {_card_path} or bump VERSION",
)


# The stamp check is only worth having if it bites, so mutate a throwaway
# tree and require env_drift to reject exactly the wrong ones -- and to
# reject them for the stated reason, since "rejected" alone was satisfied
# by the very parser bug these probes exist to pin. Delete the guards in
# claim_version_error and the rejections below stop happening.
def _claim_probe(tree_version: str, declared: str | None):
    # Every probe carries the real file's header prose, which mentions
    # `claims-for:` while declaring nothing. An earlier parser matched the
    # marker anywhere in a comment, so that sentence became the
    # declaration -- it sliced "-for:`" out of the middle of the word and
    # no later stamp could win, because the first declaration wins. Only a
    # probe that asserts WHICH answer came back catches that: the v4.1.0
    # probe (whose message must name v4.1.0, not a fragment of a
    # sentence), the `_stale_declared == "4.1.0"` check at the bottom, and
    # the unstamped probe below, which requires the UNSTAMPED verdict.
    # Asserting only "not None" pinned nothing at all: under that parser
    # every one of these files came back MALFORMED -- rejected, but for
    # the wrong reason, and the stamped ones rejected wrongly.
    with _tempfile.TemporaryDirectory(prefix="claim_probe_") as root:
        Path(root, "VERSION").write_text(tree_version + "\n")
        golden_dir = Path(root, "tests", "golden")
        golden_dir.mkdir(parents=True)
        prose = "# The `claims-for:` line below must equal VERSION.\n"
        stamp = f"# claims-for: {declared}\n" if declared is not None else ""
        Path(golden_dir, "claimed_drift.txt").write_text(
            prose + stamp + "wood_coil  # probe\n"
        )
        return _env_drift.claim_version_error(root), _env_drift._claimed(root)


_stale_problem, (_stale_declared, _stale_claims) = _claim_probe("5.0.0", "4.1.0")
R.check(
    "a claim file stamped for another release is rejected",
    _stale_problem is not None
    and "4.1.0" in _stale_problem
    and "5.0.0" in _stale_problem,
    "env_drift accepted a v4.1.0 claim file in a v5.0.0 tree",
)
_unstamped_problem = _claim_probe("5.0.0", None)[0]
R.check(
    "an unstamped claim file is rejected, prose mention and all",
    (_unstamped_problem or "").startswith("UNSTAMPED CLAIM FILE"),
    "a file whose only mention of claims-for: is prose should be "
    f"UNSTAMPED; env_drift said: {' '.join((_unstamped_problem or 'nothing').split())[:120]}",
)
# `declared == version` alone rejects 'next' in a 5.0.0 tree, so that pair
# would pass with _looks_like_version deleted. Stamping a tree with its own
# nonsense version is the case equality accepts and the version parser must
# not: 'next' == 'next' matches, and expires on nothing.
R.check(
    "a claims-for: value that is not a version is rejected, tree and all",
    _claim_probe("next", "next")[0] is not None,
    "env_drift accepted 'claims-for: next' because VERSION also said 'next'",
)
R.check(
    "a claims-for: value that is not a version is named as malformed",
    (_claim_probe("5.0.0", "next")[0] or "").startswith("MALFORMED CLAIM FILE"),
    "'claims-for: next' in a 5.0.0 tree should be MALFORMED, not stale",
)
_fresh_problem, _ = _claim_probe("5.0.0", "5.0.0")
R.check(
    "a claim file stamped for this release is accepted",
    _fresh_problem is None,
    " ".join((_fresh_problem or "").split()),
)
# The stamp is a comment, so it must not be read as a scenario name, and
# real claims must still survive the parser that now returns two things.
R.check(
    "the stamp parses as a declaration, not as a claimed scenario",
    _stale_declared == "4.1.0" and set(_stale_claims) == {"wood_coil"},
    f"declared {_stale_declared!r}, claims {sorted(_stale_claims)}",
)

# The stamp expires claims per VERSION *value*, and consecutive commits
# share one all over this history (7b512bc/401db6e/2248f64 at 4.0.0, the
# ten v4.0.0 T* merges at 3.16.0), so a merge at an unchanged version
# inherits a matching stamp and the stamp alone waves it through. The
# invariant that actually holds is that a claim list must differ from the
# baseline's; env_drift.py checks it in --all mode, once the baseline
# worktree exists and before it captures anything.
R.check(
    "a claim list identical to the baseline's is refused as inherited",
    (_env_drift.inherited_claims_error(
        {"wood_coil": "non-convex solve moved"},
        {"wood_coil": "non-convex solve moved"},
        "origin/main",
    ) or "").startswith("INHERITED CLAIMS"),
    "env_drift accepted a claim list copied wholesale from the baseline",
)
R.check(
    "an inherited claim list names the ref it was inherited from",
    "origin/main" in (_env_drift.inherited_claims_error(
        {"wood_coil": "r"}, {"wood_coil": "r"}, "origin/main") or ""),
    "the inherited-claims message must say what it compared against",
)
R.check(
    "claiming nothing, or claiming something else, is not inheritance",
    _env_drift.inherited_claims_error({}, {}, "origin/main") is None
    and _env_drift.inherited_claims_error(
        {"wood_coil": "this branch's reason"},
        {"wood_coil": "the baseline's reason"},
        "origin/main",
    ) is None,
    "an empty list claims nothing and a changed reason is a rewrite; "
    "neither is an inherited list",
)

# The other end of the same rule (v6.3.3). The inherited-claims check fires
# on whoever forks a main that was stamped with claims still in the file --
# the wrong person, one commit too late. This one fires on the stamp itself:
# a tree whose VERSION is strictly ahead of the baseline's is the release
# commit, a release moves no fixture, so its claim list must be empty. main
# went red exactly this way after v6.3.2, and the branch that paid for it was
# a one-line import hotfix.
R.check(
    "a stamp that leaves claims behind is refused",
    (_env_drift.stamp_claims_error(
        {"wood_coil": "moved by the release being closed"}, "6.3.3", "6.3.2",
    ) or "").startswith("STAMPED WITH CLAIMS"),
    "env_drift accepted a version bump that still claimed a fixture",
)
R.check(
    "the stamped-with-claims message names both versions and the fixture",
    all(part in (_env_drift.stamp_claims_error(
        {"wood_coil": "r"}, "6.3.3", "6.3.2") or "")
        for part in ("6.3.2", "6.3.3", "wood_coil")),
    "the message must say which release it is closing and what it still claims",
)
R.check(
    "a stamp claiming nothing is accepted",
    _env_drift.stamp_claims_error({}, "6.3.3", "6.3.2") is None,
    "an empty claim list is the right answer for a release that moves nothing",
)
# A branch cut before a stamp is compared against a main that has since
# stamped: its VERSION is BEHIND the baseline's, and its claims describe its
# own diff. Firing there would refuse honest work, and every branch open
# across a release would hit it.
R.check(
    "a branch behind the baseline's version may still claim its own drift",
    _env_drift.stamp_claims_error({"wood_coil": "r"}, "6.3.2", "6.3.3") is None
    and _env_drift.stamp_claims_error({"wood_coil": "r"}, "6.3.2", "6.3.2")
    is None,
    "only a tree strictly ahead of the baseline is the one doing the stamping",
)
# Non-version strings reach this from a tree mid-edit; the malformed-VERSION
# rule owns that complaint, and two errors for one mistake help nobody.
R.check(
    "a malformed version is left to the rule that owns it",
    _env_drift.stamp_claims_error({"wood_coil": "r"}, "next", "6.3.2") is None
    and _env_drift.stamp_claims_error({"wood_coil": "r"}, "6.3.3", "") is None,
    "stamp_claims_error must not duplicate the MALFORMED VERSION complaint",
)

# The may-drift category (v5.1.7). A claim asserts "this release moved this
# fixture", which is a statement about the diff. For the five fixtures the
# gate itself declares non-reproducible it is a statement about the runner
# instead: v5.1.7's reason-code change relabels a fall-through that only
# appears when the solve lands on a particular local optimum, so this machine
# sees it in valve_upper_direct_slab and the recording machine sees it in
# valve_storage_smart_write and wood_two_tank_smart_write. A fixed claim list
# is unclaimed drift on one machine and a stale claim on the other -- both
# spellings fail, for a change correct on both.
#
# What keeps the category from becoming a blanket exemption is its scope, so
# that is what these probe.
R.check(
    "may-drift accepts the fixtures the gate calls non-reproducible",
    _env_drift.may_drift_error({"wood_coil": "r"}, {}) is None
    and _env_drift.may_drift_error(
        {n: "r" for n in _env_drift.SENSITIVE}, {}
    ) is None,
)
R.check(
    "and refuses every fixture whose floats DO travel",
    (_env_drift.may_drift_error({"winter_two_zone_no_dhw": "r"}, {}) or "")
    .startswith("MAY-DRIFT OUT OF SCOPE")
    and (_env_drift.may_drift_error({"coord_minimal": "r"}, {}) or "")
    .startswith("MAY-DRIFT OUT OF SCOPE"),
    "a permanent exemption on a reproducible fixture would launder the next "
    "real regression",
)
R.check(
    "the refusal names both the stray entry and the category's real scope",
    "winter_two_zone_no_dhw"
    in (_env_drift.may_drift_error({"winter_two_zone_no_dhw": "r"}, {}) or "")
    and "wood_coil"
    in (_env_drift.may_drift_error({"winter_two_zone_no_dhw": "r"}, {}) or ""),
)
R.check(
    "a scenario cannot be claimed and may-drift at once",
    (_env_drift.may_drift_error({"wood_coil": "r"}, {"wood_coil": "r"}) or "")
    .startswith("CLAIMED AND MAY-DRIFT"),
    "a claim goes stale when nothing moves and may-drift does not; one "
    "scenario cannot be judged both ways",
)
R.check(
    "an empty may-drift list is always fine",
    _env_drift.may_drift_error({}, {"away_setback": "r"}) is None,
)

# Parsing: may-drift entries are comment lines, so `_claimed` must not read
# them as claims -- a claim named "may-drift: wood_coil" would match no
# scenario and fail the run as stale.
_md_declared, _md_claims = _env_drift._claimed(".")
_md_entries = _env_drift._may_drift(".")
R.check(
    "this tree's may-drift entries parse, with reasons",
    set(_md_entries) == set(_env_drift.SENSITIVE)
    and all(v and v != "no reason given" for v in _md_entries.values()),
    f"{sorted(_md_entries)}",
)
R.check(
    "and none of them leaks into the claim list",
    not any("may-drift" in name for name in _md_claims)
    and not (set(_md_claims) & set(_md_entries)),
    f"claims {sorted(_md_claims)}",
)
R.check(
    "this tree's own claim file passes the scope check",
    _env_drift.may_drift_error(_md_entries, _md_claims) is None,
)

# --- D10-08: the reauthentication flow -------------------------------------
R.section("Reauthentication (D10-08)")

_CRED_DATA = {
    "tibber_token": "secret-token-do-not-ship",
    "name": "HP", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}

from heatpump_optimizer.config_flow import HeatPumpOptimizerConfigFlow as _ReauthFlow  # noqa: E402
from heatpump_optimizer.const import CONF_TIBBER_TOKEN as _CONF_TOKEN  # noqa: E402


class _ReauthEntry:
    def __init__(self):
        self.entry_id = "reauth-1"
        self.data = {_CONF_TOKEN: "expired-token", "name": "HP"}
        self.started = []

    def async_start_reauth(self, hass):
        self.started.append(True)


_ra_hass = FakeHass()
_ra_hass.config_entries.async_register = lambda *a, **k: None
_ra_coord = integration.HeatPumpOptimizerCoordinator(
    _ra_hass, FakeEntry(data=dict(_CRED_DATA))
)
_ra_entry = _ReauthEntry()
_ra_coord.config_entry = _ra_entry

# A refused token starts the flow exactly once per outage...
_ra_coord._tibber_start_reauth()
_ra_coord._tibber_start_reauth()
R.check(
    "a refused token starts the reauth flow once, not per cycle",
    _ra_entry.started == [True],
    f"started {len(_ra_entry.started)} time(s)",
)
# ...recovery re-arms it, so a later revocation gets its own flow.
_ra_coord._tibber_fetch_recovered()
_ra_coord._tibber_start_reauth()
R.check(
    "recovery re-arms the flow for a future revocation",
    _ra_entry.started == [True, True],
    f"started {len(_ra_entry.started)} time(s)",
)

_ra_flow = _ReauthFlow()
_ra_flow.hass = _ra_hass
_ra_hass.config_entries.entries = [FakeEntry(data=dict(_CRED_DATA), entry_id="reauth-1")]
_ra_form = asyncio.run(_ra_flow.async_step_reauth(_ra_entry.data))
R.check(
    "the reauth flow opens a confirm form asking for the token",
    _ra_form.get("type") == "form"
    and _ra_form.get("step_id") == "reauth_confirm",
    f"got {_ra_form.get('type')}/{_ra_form.get('step_id')}",
)

_ra_updates = []
_ra_reloads = []


def _ra_update(entry, **kw):
    _ra_updates.append(kw)


async def _ra_reload(entry_id):
    _ra_reloads.append(entry_id)


_ra_hass.config_entries.async_update_entry = _ra_update
_ra_hass.config_entries.async_reload = _ra_reload
_ra_flow._reauth_entry = _ra_entry


class _GoodToken:
    @staticmethod
    async def __call__(hass, token):
        return "ok"


_ra_flow_validate = config_flow.validate_tibber_token
config_flow.validate_tibber_token = _GoodToken()
try:
    _ra_out = asyncio.run(
        _ra_flow.async_step_reauth_confirm({_CONF_TOKEN: "new-token"})
    )
finally:
    config_flow.validate_tibber_token = _ra_flow_validate
R.check(
    "a valid token is written through and the entry reloads",
    _ra_out.get("reason") == "reauth_successful"
    and _ra_updates
    and _ra_updates[0]["data"][_CONF_TOKEN] == "new-token"
    and _ra_reloads == ["reauth-1"],
    f"result {_ra_out}, updates {_ra_updates}, reloads {_ra_reloads}",
)

# --- D10-14: the reconfigure flow (#196) ------------------------------------
R.section("Reconfigure (D10-14)")

# Reconfigure (the Gold-tier reconfiguration-flow rule) is the "change the
# token / point at a renamed sensor without deleting the entry" flow. Home
# Assistant 2024.4+ starts it from the entry's page: the manager sets
# context={"source": "reconfigure", "entry_id": ...} and calls
# async_step_reconfigure with the entry's data, and the entry's own
# ConfigEntry.supports_reconfigure -- hasattr(handler, "async_step_reconfigure")
# in the 2024.6 source -- decides whether the UI offers the button at all.
# The stub mirrors that discovery through its HANDLERS registry, so the first
# check asks it the way the UI would.
_rc_hass = FakeHass()
_rc_entry_data = {
    **_first_screen,  # tok-a / weather.home / switch.pump_a
    _CONF_NAME: "Annex pump",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.annex_indoor",
    "target_temp": 21.5,  # a second-screen setting the first screen never asks
}
_rc_identity = _entry_identity(_rc_entry_data)
_rc_entry = FakeEntry(
    data=dict(_rc_entry_data), entry_id="plant_a", unique_id=_rc_identity
)
_rc_other_data = {
    **_first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"
}
_rc_other = FakeEntry(
    data=dict(_rc_other_data),
    entry_id="plant_b",
    unique_id=_entry_identity(_rc_other_data),
)
_rc_hass.config_entries.entries = [_rc_entry, _rc_other]

_rc_updates = []
_rc_reloads = []


def _rc_update(entry, **kw):
    _rc_updates.append(kw)


async def _rc_reload(entry_id):
    _rc_reloads.append(entry_id)


_rc_hass.config_entries.async_update_entry = _rc_update
_rc_hass.config_entries.async_reload = _rc_reload

R.check(
    "an entry for this handler reports reconfigure support the way HA 2024.6 discovers it",
    config_flow.config_entries.ConfigEntry(domain=const.DOMAIN).supports_reconfigure,
    "ConfigEntry.supports_reconfigure is hasattr(handler, 'async_step_reconfigure')",
)
R.check(
    "the config flow carries the reconfigure step",
    hasattr(initial, "async_step_reconfigure"),
    "no async_step_reconfigure on HeatPumpOptimizerConfigFlow",
)


def _rc_flow(entry_id="plant_a"):
    """A flow as the 2024.6 manager starts one: source and entry stamped."""
    flow = initial()
    flow.hass = _rc_hass
    flow.context = {
        "source": config_flow.config_entries.SOURCE_RECONFIGURE,
        "entry_id": entry_id,
    }
    return flow


def _run_reconfigure(flow, answers):
    try:
        return asyncio.run(flow.async_step_reconfigure(None if answers is None else dict(answers)))
    except _AbortFlow as err:
        return {"type": "abort", "reason": err.reason}
    except AttributeError as err:
        return {"type": "error", "reason": f"AttributeError: {err}"}


_rc_real_validate = config_flow.validate_tibber_token
config_flow.validate_tibber_token = _accept_any_token
try:
    _rc_form = _run_reconfigure(_rc_flow(), None)
finally:
    config_flow.validate_tibber_token = _rc_real_validate

R.check(
    "reconfigure reopens the first screen rather than a fresh wizard",
    _rc_form.get("type") == "form" and _rc_form.get("step_id") == "user",
    f"got {_rc_form.get('type')}/{_rc_form.get('step_id')} ({_rc_form.get('reason')})",
)
# The form is the user step's own schema with this entry's answers carried as
# suggested values -- current values as defaults, never as silent submissions.
_rc_schema = _rc_form.get("data_schema")
_rc_suggested = (
    {
        str(getattr(k, "schema", k)): (getattr(k, "description", None) or {}).get(
            "suggested_value"
        )
        for k in _rc_schema.schema
    }
    if _rc_schema is not None
    else {}
)
R.check(
    "the reopened screen is prefilled with this entry's answers",
    _rc_suggested.get(_CONF_NAME) == "Annex pump"
    and _rc_suggested.get(const.CONF_TIBBER_TOKEN) == "tok-a"
    and _rc_suggested.get(const.CONF_INDOOR_TEMP_ENTITY) == "sensor.annex_indoor",
    f"suggested name {_rc_suggested.get(_CONF_NAME)!r}, "
    f"token {_rc_suggested.get(const.CONF_TIBBER_TOKEN)!r}",
)
R.check(
    "a slot this entry leaves empty is not invented",
    _rc_suggested.get(const.CONF_OUTDOOR_TEMP_ENTITY) is None,
    f"suggested outdoor {_rc_suggested.get(const.CONF_OUTDOOR_TEMP_ENTITY)!r}",
)

_rc_submit_same = {
    **_first_screen,
    _CONF_NAME: "Annex pump",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.annex_indoor",
}


def _drive_reconfigure(answers):
    flow = _rc_flow()
    config_flow.validate_tibber_token = _accept_any_token
    try:
        return _run_reconfigure(flow, answers)
    finally:
        config_flow.validate_tibber_token = _rc_real_validate


# Re-submitting this entry's own identity is the case the plain duplicate
# guard would get wrong: async_entry_for_domain_unique_id finds THIS entry,
# and a naive _abort_if_unique_id_configured would refuse the reconfigure it
# exists to perform.
_rc_out_same = _drive_reconfigure(_rc_submit_same)
R.check(
    "re-submitting this entry's own identity updates it instead of aborting",
    _rc_out_same.get("type") == "abort"
    and _rc_out_same.get("reason") == "reconfigure_successful"
    and _rc_updates
    and _rc_updates[-1]["data"]["target_temp"] == 21.5,
    f"result {_rc_out_same}, updates {[k for k in _rc_updates]}",
)
R.check(
    "the entry reloads on the new answers",
    _rc_reloads == ["plant_a"],
    f"reloads {_rc_reloads}",
)
R.check(
    "a rename is written through, title and all",
    bool(_rc_updates)
    and _drive_reconfigure(
        {**_rc_submit_same, _CONF_NAME: "Annex (renamed)"}
    ).get("reason")
    == "reconfigure_successful"
    and _rc_updates[-1]["data"][_CONF_NAME] == "Annex (renamed)"
    and _rc_updates[-1].get("title") == "Annex (renamed)",
    f"update kwargs keys {sorted(_rc_updates[-1]) if _rc_updates else []}",
)
_rc_cleared = {
    k: v for k, v in _rc_submit_same.items() if k != const.CONF_INDOOR_TEMP_ENTITY
}
R.check(
    "a slot the user cleared is dropped, not silently kept",
    bool(_rc_updates)
    and _drive_reconfigure(_rc_cleared).get("reason") == "reconfigure_successful"
    and const.CONF_INDOOR_TEMP_ENTITY not in _rc_updates[-1]["data"],
    f"cleared slot still in data: "
    f"{_rc_updates[-1]['data'].get(const.CONF_INDOOR_TEMP_ENTITY) if _rc_updates else None!r}",
)
R.check(
    "and the entry's unique id follows the picks, as a delete-and-recreate would",
    bool(_rc_updates)
    and _rc_updates[-1].get("unique_id") == _entry_identity(_rc_cleared),
    f"unique_id kwarg {_rc_updates[-1].get('unique_id') if _rc_updates else None!r}",
)
R.check(
    "reconfiguring into another entry's plant is refused",
    _drive_reconfigure(
        {**_first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"}
    )
    == {"type": "abort", "reason": "already_configured"},
)
R.check(
    "the reconfigure success abort has a string to show",
    "reconfigure_successful" in strings["config"]["abort"],
)

# --- D10-12: the diagnostics payload ---------------------------------------
R.section("Diagnostics (D10-12)")

from heatpump_optimizer import diagnostics as _diag_mod  # noqa: E402
import json as _json

_diag_hass = FakeHass()
_diag_entry = FakeEntry(data=dict(_CRED_DATA))
_diag_entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
    _diag_hass, FakeEntry(data=dict(_CRED_DATA))
)
_diag = asyncio.run(
    _diag_mod.async_get_config_entry_diagnostics(_diag_hass, _diag_entry)
)
_blob = _json.dumps(_diag, default=str)
R.check(
    "the Tibber token never leaves the instance",
    _diag["config"].get(_CONF_TOKEN) == "REDACTED"
    and "stub-token" not in _blob
    and _CRED_DATA[_CONF_TOKEN] not in _blob,
    "a credential (or a fragment of it) appeared in the payload",
)
R.check(
    "the payload is plain JSON and names the coordinator's state",
    isinstance(_diag.get("coordinator"), dict)
    and "tibber_outage_cycles" in _diag["coordinator"]
    and "mode" in _diag["coordinator"],
    f"coordinator keys: {sorted((_diag.get('coordinator') or {}).keys())[:8]}",
)
R.check(
    "the learner summaries are present",
    any(
        k in (_diag.get("coordinator") or {})
        for k in ("accuracy", "comfort_learner", "curve_learner", "price_model")
    ),
    "none of the four learner summaries appeared",
)

# --- D10-08: the shared entity base lives in entity.py ----------------------
#
# The audit found five CoordinatorEntity base classes, one per platform file,
# each re-declaring the same two members: ``_attr_has_entity_name = True`` and
# the ``device_info`` property that delegates to the coordinator. The
# common-modules rule (Bronze) wants that shared base in ``entity.py``, where
# a reader of a Home Assistant integration looks for it. These checks are
# deliberately structural -- reading the production sources the way the audit
# harness does -- because the rule itself is about structure; the behavioural
# pins below it keep the move honest.
R.section("Entity base classes (D10-08)")

try:
    from heatpump_optimizer import entity as _entity_mod  # noqa: E402
except ImportError:  # the pre-#298 tree
    _entity_mod = None

_shared_base = getattr(_entity_mod, "HeatPumpOptimizerEntity", None)
R.check(
    "entity.py exists and defines HeatPumpOptimizerEntity",
    _entity_mod is not None and isinstance(_shared_base, type),
    "custom_components/heatpump_optimizer/entity.py is missing or holds no "
    "HeatPumpOptimizerEntity",
)
from homeassistant.helpers.update_coordinator import (  # noqa: E402
    CoordinatorEntity as _CoordinatorEntity,
)

_plumbing = (
    sorted(k for k in vars(_shared_base) if not k.startswith("__"))
    if isinstance(_shared_base, type)
    else []
)
R.check(
    "the shared base is a CoordinatorEntity declaring the plumbing exactly once",
    (
        isinstance(_shared_base, type)
        and issubclass(_shared_base, _CoordinatorEntity)
        and _shared_base.__dict__.get("_attr_has_entity_name") is True
        and "device_info" in _shared_base.__dict__
    ),
    f" HeatPumpOptimizerEntity holds {_plumbing}",
)

for _pf in ("sensor.py", "binary_sensor.py", "button.py", "climate.py", "switch.py"):
    R.check(
        f"the {_pf[:-3]} platform imports the shared base from .entity",
        "from .entity import HeatPumpOptimizerEntity" in (ROOT / _pf).read_text(),
        f"{_pf} does not import HeatPumpOptimizerEntity from .entity",
    )

# The audit's own metric (entity_base_classes_outside_entity_py): platform
# files must no longer declare CoordinatorEntity base classes of their own.
_bases_left = [
    _pf
    for _pf in ("sensor.py", "binary_sensor.py", "button.py", "climate.py", "switch.py")
    if re.search(
        r"^class \w+\(CoordinatorEntity, \w+Entity\)", (ROOT / _pf).read_text(), re.M
    )
]
R.check(
    "no CoordinatorEntity base classes remain in the platform files",
    not _bases_left,
    f"still declared in: {_bases_left}",
)

# Every root the tests and Home Assistant reach by name stays where it was
# and now builds on the shared base instead of re-declaring its plumbing.
for _module, _root in (
    (sensor, "HeatPumpOptimizerSensorBase"),
    (binary_sensor, "_OptimizerBinarySensorBase"),
    (button, "_OptimizerButtonBase"),
    (_climate_platform, "HeatPumpOptimizerClimate"),
    (_switch_platform, "OptimizerEnableSwitch"),
):
    _cls = getattr(_module, _root, None)
    R.check(
        f"{_module.__name__.rsplit('.', 1)[-1]}.{_root} still exists and builds "
        f"on the shared base",
        (
            isinstance(_cls, type)
            and isinstance(_shared_base, type)
            and issubclass(_cls, _shared_base)
        ),
        "the platform root is gone or no longer subclasses "
        "HeatPumpOptimizerEntity",
    )

# Behaviour is unchanged: an entity from each platform still resolves
# has_entity_name and still lands on the coordinator's device.
for _module in (sensor, binary_sensor, _climate_platform, _switch_platform, button):
    _one = collect(_module)[0]
    R.check(
        f"an entity from {_module.__name__.rsplit('.', 1)[-1]} keeps "
        f"has_entity_name and the coordinator's device_info",
        _one._attr_has_entity_name is True
        and _one.device_info == _one.coordinator.device_info,
        "an entity stopped resolving the shared plumbing",
    )

sys.exit(R.close("ENTITY CHECKS"))
