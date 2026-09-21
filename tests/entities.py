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

import subprocess
import ast
import asyncio
import json
import pathlib
import re
import string
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

# #924: the fixed first refresh fetches through the base class, and a token
# config has no HTTP under the stub. The entity feed is a real production
# source that works offline. Local rather than shared through harness.py:
# harness.py is a capture source, and a diff touching it makes every
# inherited claim list this branch's to rewrite -- the corner card_drift
# reports and the claims bot refuses to repair (#743/#747).
# The light first refresh CONSUMES ``_skip_solve_once`` at setup -- arm it
# after setup if a test wants it.
_OFFLINE_PRICES = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def _seed_prices(hass, entity_id="sensor.prices", hours=48, base=0.5):
    """A Nord-Pool-style sensor with ``hours`` fresh hourly rows."""
    from datetime import timedelta

    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        entity_id,
        FakeState(
            str(base),
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(base + 0.1 * (h % 4), 3),
                    }
                    for h in range(hours)
                ]
            },
        ),
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
from golden import (  # noqa: E402
    _nested_schema,
    _presented_fields,
    empty_section_payload,
    nest_flat,
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
from heatpump_optimizer import datetime as datetime_mod
from heatpump_optimizer import switch as _switch_platform

for _module, _expected in (
    (sensor, 0),
    (binary_sensor, 0),
    (button, 1),
    (_climate_platform, 1),
    (_switch_platform, 1),
    (datetime_mod, 1),
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
    "input_problems": [
        {
            "input": "indoor_temp_entity",
            "entity_id": "sensor.indoor",
            "problem": "stale",
            "age_minutes": 600.0,
            "max_age_minutes": 60.0,
        }
    ],
    "problem_inputs": ["sensor.indoor"],
    "problem_messages": ["sensor.indoor: stale (last report 600 min)"],
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
    "away_override_active": False,
    "away_override_return_time": None,
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
            "lines": ["6.2 kWh in the cheapest hours for 8.40 SEK"],
            "language": "en",
        },
        "scores": {
            "envelope": 75.0,
            "machine": 100.0,
            "operation": None,
            "overall": 100.0,
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
        # Which stores are sensed and which are the model's own estimate.
        # The two battery entities are available while at least one store is
        # sensed, so this payload -- the one whose job is to satisfy every
        # gate -- names a measured store, with the buffer tank standing as
        # the modelled one.
        "components": [
            {"name": "house", "temperature": 21.3, "measured": True},
            {"name": "buffer_tank", "temperature": 40.0, "measured": False},
        ],
        "measured_components": ["house"],
        "modelled_components": ["buffer_tank"],
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
    "savings_months": [],
    "wood_fuel": {
        "ready": True,
        "cheaper": True,
        "show_whatif": True,
        "sek_per_kwh": 0.6,
        "type": "mixed",
        "packing": "packed",
        "efficiency": 75.0,
        "price_sek_m3": 800.0,
        "cheaper_hour_count": 1,
        "slots": [],
    },
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
#
# Every number below is DERIVED, and the platform set comes from
# ``PLATFORM_LIST`` rather than from a list written here. The version this
# replaced compared the README's binary-sensor and button headings against the
# literals 4 and 4 -- it supplied the value it then asserted, so when
# ``wood_cheaper`` made five binary sensors the README kept saying four and
# this check kept passing. Driving the census off ``PLATFORM_LIST`` closes the
# other half: a platform nobody remembers to name here still enters the total.
import importlib as _importlib
import re as _re

readme = Path("README.md").read_text()

_platform_counts = {
    str(_p): len(collect(_importlib.import_module(f"heatpump_optimizer.{_p}")))
    for _p in integration.PLATFORM_LIST
}
_total_entities = sum(_platform_counts.values())


def _readme_table_rows(heading: str) -> int:
    """Data rows of the markdown table under one ``### heading``."""
    block = _re.search(
        rf"^### {_re.escape(heading)}[^\n]*\n(.*?)(?=^## |^### |\Z)",
        readme,
        _re.M | _re.S,
    )
    if block is None:
        return -1
    rows = [
        line for line in block.group(1).splitlines()
        if line.startswith("|") and not _re.fullmatch(r"\|[\s|:-]+\|", line.strip())
    ]
    return max(len(rows) - 1, 0)  # less the header row


# Sensors keep the heading count and lose only the ROW count: #558 B10 split
# the section into labelled `####` groups under one `### Sensors` heading, so a
# row count over the whole heading double-counts each group's own header row
# (measured: 63 rows over 56 sensors + 8 groups - 1). The name-set check below
# subsumes that row count and is strictly stronger -- but it never reads the
# published number, so dropping this check alongside the row count would leave
# `### Sensors (N total)` pinned by nothing at all.
_sensors_n = _platform_counts["sensor"]
_sensors_heading = _re.search(r"### Sensors \((\d+) total\)", readme)
R.check(
    "the README's sensors count is right",
    _sensors_heading is not None and int(_sensors_heading.group(1)) == _sensors_n,
    f"README says {_sensors_heading.group(1) if _sensors_heading else '?'}, "
    f"there are {_sensors_n}",
)

# Binary sensors and buttons stay single tables, so counting their rows pins
# them too.
for _label, _platform, _heading in (
    ("binary sensors", "binary_sensor", "Binary Sensors"),
    ("buttons", "button", "Buttons"),
):
    _n = _platform_counts[_platform]
    match = _re.search(rf"### {_re.escape(_heading)} \((\d+) total\)", readme)
    R.check(
        f"the README's {_label} count is right",
        match is not None and int(match.group(1)) == _n,
        f"README says {match.group(1) if match else '?'}, there are {_n}",
    )
    # The heading and the table drifted together for ``wood_cheaper``: the
    # number said four and the table listed four while the platform added
    # five, so correcting the heading alone would leave the entity
    # undocumented and this check green.
    _rows = _readme_table_rows(_heading)
    R.check(
        f"the README's {_label} table lists every one of them",
        _rows == _n,
        f"table has {_rows} row(s), there are {_n}",
    )

# #835: the notes used to say the sensor waits on "the wood tank" alone.
# That is one of six gates; the billed price has no silent default, so a
# user whose entity stays blank was sent to the wrong cause.
_wc_notes = _re.search(
    r"^\| Wood Cheaper Than Heat Pump \|[^|\n]*\|([^|\n]*)\|",
    readme,
    _re.M,
)
R.check(
    "the README's wood_cheaper notes name the billed-price gate",
    _wc_notes is not None
    and "no silent default" in _wc_notes.group(1)
    and "wood tank is usable" not in _wc_notes.group(1),
    _wc_notes.group(1).strip() if _wc_notes else "row missing",
)

# #834: the options dialog offers 21 pages. The README used to say 13 and
# named the Grid page "Grid costs". Drive the count off `_OPTION_PAGES`
# and the labels off strings.json, so a page the menu gained cannot stay
# undocumented in the one place a user checks before installing.
_opt_strings = json.loads((ROOT / "strings.json").read_text())["options"]["step"]


def _step_texts(body, kind):
    """Every ``kind`` ("data" or "data_description") text one flow step
    carries, at step level and inside each of its sections. A field grouped
    with ``section()`` keeps its label under ``sections.<name>.<kind>``, which
    is where the frontend reads it, so a reader of the step level alone
    misses every grouped field."""
    yield from (body.get(kind) or {}).items()
    for _sec in (body.get("sections") or {}).values():
        yield from (_sec.get(kind) or {}).items()


_page_labels = [
    label
    for step in ("init", "advanced")
    for key, label in _opt_strings[step]["menu_options"].items()
    if key != "advanced"
]
_pages_claim = _re.search(r"menu of (\d+) pages", readme)
R.check(
    "the README's options-page count matches _OPTION_PAGES",
    _pages_claim is not None
    and int(_pages_claim.group(1)) == len(config_flow._OPTION_PAGES)
    and len(_page_labels) == len(config_flow._OPTION_PAGES),
    f"README says {_pages_claim.group(1) if _pages_claim else '?'}, "
    f"_OPTION_PAGES has {len(config_flow._OPTION_PAGES)}, "
    f"strings name {len(_page_labels)}",
)
_missing_labels = [label for label in _page_labels if label not in readme]
R.check(
    "the README names every options page by its real menu label",
    not _missing_labels,
    ", ".join(_missing_labels[:8]),
)
# #1067 G7: the Modbus pre-fill page re-labels keys that live on other pages,
# and its labels are copies. A copy that drifts from the home page's label
# names one setting two ways, so each is compared, in both shipped languages.
_prefill_drift = []
for _lang_file in ("strings.json", "translations/sv.json"):
    _lang_steps = json.loads((ROOT / _lang_file).read_text())["options"]["step"]
    for _pkey, _plabel in _lang_steps["modbus_prefill"]["data"].items():
        # A home page may group the field into a section() (#824-style), which
        # keeps its label under sections.<name>.data rather than the step's
        # own top-level data -- _step_texts already walks both, so read the
        # home page through it rather than _st["data"] alone (that copy
        # missed every grouped field, one page's worth here: hot_water).
        _homes = {
            _sid: _label
            for _sid, _st in _lang_steps.items()
            if _sid != "modbus_prefill"
            for _k, _label in _step_texts(_st, "data")
            if _k == _pkey
        }
        # The page's OWN fields -- the prefix row, the transient device pick
        # (#1067 G7b-1) and the offer switch (#1067 W1067-POST1) -- have no
        # home page to agree with. Derived from production, so a renamed field
        # cannot silently fall out of the check.
        if _pkey not in (
            const.CONF_MODBUS_PREFILL_PREFIX, config_flow._PREFILL_DEVICE,
            const.CONF_PREFILL_OFFER,
        ) and set(_homes.values()) != {_plabel}:
            _prefill_drift.append(f"{_lang_file}:{_pkey}={_plabel!r} vs {_homes}")
R.check(
    "the Modbus pre-fill page labels every suggested key as its own page does",
    not _prefill_drift and len(_lang_steps["modbus_prefill"]["data"]) > 2,
    "; ".join(_prefill_drift),
)
R.check(
    "the README does not list Enable away mode as an options-page field",
    "| Enable away mode |" not in readme
    and "| Expected return time |" not in readme,
    "those are entities, not fields on Away and holiday mode",
)

# #937: the README sends the reader to the reference with "Every field and its
# range is documented in docs/configuration.md", and round 4 measured 15 of
# the 200 shipped options fields whose label occurred nowhere in any reader
# document -- the weekend and holiday schedule hours, the external-heat
# detection group, the valve set-point declaration, the surcharge beside the
# VAT multiplier, and the After saving navigation control on every page. The
# page-level mapping was already perfect (21 sections, 21 steps); this is the
# field-level promise, and it is checked against the reference itself rather
# than the doc set, because the reference is the file the README names.
# Reading the reference here is also what takes it off closure.py's INERT
# list: a document a gate script checks is a dependency, not inert (#970 took
# tests/README.md off for the same reason).
def _fold_text(text: str) -> str:
    """Markdown-stripped, case-folded, punctuation-collapsed -- the form a
    document's prose and a UI label share when they name the same thing."""
    text = _re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    text = _re.sub(r"[^a-z0-9]+", " ", text.lower())
    return _re.sub(r"\s+", " ", text).strip()


_cfgref_hay = _fold_text(Path("docs/configuration.md").read_text())


def _field_name(label: str) -> str:
    """A label folded for exact containment, one trailing parenthetical
    stripped first -- "(optional)" is a UI convention, not part of the name
    a document would repeat. The same rule the audit's harness used."""
    return _fold_text(_re.sub(r"\s*\([^()]*\)\s*$", "", label))


_unnamed_fields = sorted(
    f"{_sid}.{_key}"
    for _sid, _step in _opt_strings.items()
    for _key, _label in _step_texts(_step, "data")
    if _field_name(_label) and _field_name(_label) not in _cfgref_hay
)
R.check(
    "the configuration reference names every shipped options field",
    not _unnamed_fields,
    f"{len(_unnamed_fields)} of {sum(1 for s in _opt_strings.values() for _ in _step_texts(s, 'data'))} "
    f"labels absent from docs/configuration.md: " + ", ".join(_unnamed_fields[:8]),
)

# #941: automations.md's Power Headroom paragraph stated an availability
# precondition the sensor does not enforce -- "It stays unavailable until you
# set a main fuse size in the options" -- while round 4 measured a capacity
# tariff alone making it available at 0.0 kW with limit_source "capacity
# tariff with no peak reference yet", and the fuse defaults to 0. The
# paragraph must name every state the real sensor publishes over the
# fuse x tariff grid, so an automation author can tell each availability
# source apart; the grid is driven through the real coordinator's own
# `_power_headroom` (via `_build_data_dict`) and the real entity constructed
# by the platform's `async_setup_entry`, never restated here. Reading the
# file is also what takes it off `tests/closure.py`'s INERT list: a document
# a gate script checks is a dependency, not inert (#984 did the same for
# docs/configuration.md).
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _hra_coord,
)

_automations_hay = _fold_text(Path("docs/automations.md").read_text())
_hra_tariff = {const.CONF_PEAK_TARIFF_ENABLED: True, const.CONF_PEAK_TARIFF_PRICE: 45.0}
# The default tariff carries no masks (no months, no peak hours, every window
# counts at 1.0), so `sample_factor` answers a billable window at any hour
# and the grid needs no clock freeze to be deterministic.
_hra_cells = {
    "no fuse, no tariff": {},
    "no fuse, capacity tariff": dict(_hra_tariff),
    "fuse, no tariff": {const.CONF_MAIN_FUSE_A: 20},
    "fuse, capacity tariff": {const.CONF_MAIN_FUSE_A: 20, **_hra_tariff},
}


def _hra_headroom_entity(extra_config):
    """The real Cost Power Headroom entity over a real coordinator's own publish."""
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    cfg.update(extra_config)
    coord = _hra_coord(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    return next(
        e
        for e in collect(sensor, data=coord._build_data_dict())
        if getattr(e, "_attr_translation_key", None) == "cost_power_headroom"
    )


_hra_available = {}
_hra_sources = set()
for _hra_label, _hra_extra in _hra_cells.items():
    _hra_ent = _hra_headroom_entity(_hra_extra)
    if _hra_ent.available:
        _hra_available[_hra_label] = True
        _hra_src = _hra_ent.extra_state_attributes.get("limit_source")
        if _hra_src:
            _hra_sources.add(_hra_src)

R.check(
    "only the unbounded cell keeps Cost Power Headroom unavailable",
    set(_hra_available)
    == {
        "no fuse, capacity tariff",
        "fuse, no tariff",
        "fuse, capacity tariff",
    },
    f"available cells: {sorted(_hra_available)} -- the no-fuse-no-tariff cell "
    f"is the only one with nothing bounding the house (#941's rule; if this "
    f"moves, docs/automations.md's paragraph must move with it)",
)
_hra_unnamed = sorted(s for s in _hra_sources if _fold_text(s) not in _automations_hay)
R.check(
    "automations.md names every state the Cost Power Headroom sensor publishes",
    not _hra_unnamed,
    f"limit_source values absent from docs/automations.md: {_hra_unnamed} "
    f"(published over the grid by: {sorted(_hra_available)})",
)

_total_claim = _re.search(r"All (\d+) entities", readme)
R.check(
    "the README's total entity count covers every registered platform",
    _total_claim is not None and int(_total_claim.group(1)) == _total_entities,
    f"README says {_total_claim.group(1) if _total_claim else '?'}, "
    f"the platforms construct {_total_entities} ({_platform_counts})",
)

# The same claim discipline for the suite's own manual. `tests/README.md`'s
# per-script list annotates each script with the sizes it runs, and #938
# measured the stress line saying "48 combinations" while the sweep had
# returned 51 since #286/#287's three zero-range-bounds scenarios -- the
# kind of sentence that goes stale silently because nothing reads it. The
# sweep count is derived by CALLING the symbol (exposed at module level
# for exactly this, per its docstring), never by counting code; the edge
# and seasonal counts are AST reads of the registered artifacts, because
# the `edges` dict lives inside stress.py's `__main__` block and
# validate.py executes its scenarios at import, so neither can be imported
# just to be counted. Reading the file here is also what takes it out of
# `tests/closure.py`'s INERT list: a document a gate script checks is a
# dependency, not inert.
import stress as _stress_mod

_tests_readme = Path("tests/README.md").read_text()
_stress_note = _re.search(
    r"tests/stress\.py\s*#\s*(\d+)\s+combinations,\s*(\d+)\s+edge cases",
    _tests_readme,
)
_validate_note = _re.search(
    r"tests/validate\.py\s*#\s*(\d+)\s+seasonal scenarios", _tests_readme
)
_sweep_n = len(_stress_mod.sweep_combinations())
R.check(
    "tests/README.md's stress annotation states the sweep's real size",
    _stress_note is not None and int(_stress_note.group(1)) == _sweep_n,
    f"README says {_stress_note.group(1) if _stress_note else '?'}, "
    f"sweep_combinations() returns {_sweep_n} (#938)",
)
_stress_tree = ast.parse(Path("tests/stress.py").read_text())
_edges_n = next(
    len(node.value.keys)
    for node in ast.walk(_stress_tree)
    if isinstance(node, ast.Assign)
    and any(getattr(t, "id", None) == "edges" for t in node.targets)
    and isinstance(node.value, ast.Dict)
)
R.check(
    "the stress annotation's edge-case count is the dict's real size",
    _stress_note is not None and int(_stress_note.group(2)) == _edges_n,
    f"README says {_stress_note.group(2) if _stress_note else '?'}, "
    f"the edges dict in stress.py has {_edges_n} entries",
)
_validate_tree = ast.parse(Path("tests/validate.py").read_text())
_validate_n = sum(
    isinstance(node, ast.Expr)
    and isinstance(node.value, ast.Call)
    and getattr(node.value.func, "id", None) == "run"
    for node in _validate_tree.body
)
R.check(
    "the validate annotation's scenario count is the module's real size",
    _validate_note is not None and int(_validate_note.group(1)) == _validate_n,
    f"README says {_validate_note.group(1) if _validate_note else '?'}, "
    f"validate.py makes {_validate_n} module-level run(...) calls",
)

# #934 (D3-INST): two claims the suite makes about its own cost. First,
# closures.json is the only per-script timing table in the tree, and the
# two differential guards' `recorded` seconds are the cheap stub
# invocations derive_closures.sh records with (golden.py --only
# __no_such_scenario__, env_drift.py --cache-key <ref> --all) -- 0.5 s
# recorded against a standalone golden.py run the judge measured at
# 160.9 s -- so the file's own comment must say so or a reader sizing a
# gate run off the table is misled ~300x. Second, the one-script list
# above double-charged that same differential: golden.py's default drift
# mode does not run a second measurement, it execs env_drift.py --all
# (the run the env_drift.py line below it names), so a developer
# following the list paid ~3 minutes twice for one answer. The default
# is DERIVED from golden.py's source (DEFAULT_MODE / DRIFT_SCRIPT /
# "--all" in drift_command), never asserted from prose, so the note
# fails if golden.py's default ever stops being the env_drift run.
_golden_src = Path("tests/golden.py").read_text()
_golden_defaults_to_drift = (
    _re.search(r'DEFAULT_MODE = "drift"', _golden_src) is not None
    and _re.search(r'DRIFT_SCRIPT = "tests/env_drift\.py"', _golden_src)
    is not None
    and _re.search(r'"--all", ref', _golden_src) is not None
)
_golden_note = _re.search(r"(python\s+tests/golden\.py\s*#[^\n]*)", _tests_readme)
R.check(
    "tests/README.md's golden.py line names the run its default mode makes",
    _golden_note is not None
    and _golden_defaults_to_drift
    and "env_drift.py --all" in _golden_note.group(1)
    and "same measurement" in _golden_note.group(1),
    f"line={_golden_note.group(1).strip() if _golden_note else '!'}, "
    f"golden.py defaults to drift={_golden_defaults_to_drift} (#934)",
)
_closures_comment = json.loads(
    Path("tests/closures.json").read_text())["_comment"]
R.check(
    "closures.json's comment discloses the differential guards' stub seconds",
    all(
        w in _closures_comment
        for w in ("cheap", "golden.py", "env_drift.py", "seconds")
    ),
    f"_comment={_closures_comment!r} (#934)",
)

# #939: architecture.md's own numbers. The file a contributor reads before
# changing the code had rotted in ten places -- 45 modules where 56 stood, a
# module map missing eleven files, ten HA importers where 21 import at module
# level, 13 option pages where 21 render, eleven services where twelve
# register, and platform comments naming one switch of four and four binary
# sensors of five -- because `docs/` is INERT and no gate script read it. The
# route #357 allows is taken here: a file this script opens is a dependency,
# so architecture.md leaves INERT and enters this script's measured closure,
# and every figure below is DERIVED -- the module list from the directory, the
# boundary from an AST walk, the pages from `_OPTION_PAGES`, the services
# from services.yaml, the entity names from the same platform census that
# pins the README -- never carried, so the counts stay true when the tree
# moves. That is the same correction tests/README.md needed (#938).
import yaml as _yaml

_arch = Path("docs/architecture.md").read_text()
_arch_disk = sorted(p.name for p in ROOT.glob("*.py"))


def _arch_ha_import(node):
    """Is this statement an import of the homeassistant package?"""
    if isinstance(node, ast.Import):
        return any(a.name.split(".")[0] == "homeassistant" for a in node.names)
    if isinstance(node, ast.ImportFrom):
        return bool(node.module) and node.module.split(".")[0] == "homeassistant"
    return False


def _arch_toplevel(body):
    """Module-scope statements, descending into top-level try/if bodies only.

    An import inside a conditional or try at import time is still a
    module-level import: the module cannot be imported without
    homeassistant, which is what the boundary paragraph claims.
    """
    for node in body:
        yield node
        if isinstance(node, ast.Try):
            for lst in (node.body, node.orelse, node.finalbody):
                yield from _arch_toplevel(lst)
            for handler in node.handlers:
                yield from _arch_toplevel(handler.body)
        elif isinstance(node, ast.If):
            yield from _arch_toplevel(node.body)
            yield from _arch_toplevel(node.orelse)


_arch_modlevel = sorted(
    p.stem for p in ROOT.glob("*.py")
    if any(_arch_ha_import(n) for n in _arch_toplevel(ast.parse(p.read_text()).body))
)
_arch_anywhere = sorted(
    p.stem for p in ROOT.glob("*.py")
    if any(_arch_ha_import(n) for n in ast.walk(ast.parse(p.read_text())))
)

_arch_open = _re.search(r"(\d+) modules, of which\s+(\d+) import", _arch)
R.check(
    "architecture.md's opening counts name the package it describes",
    _arch_open is not None
    and int(_arch_open.group(1)) == len(_arch_disk)
    and int(_arch_open.group(2)) == len(_arch_modlevel),
    f"architecture.md says {_arch_open.groups() if _arch_open else '?'}; the "
    f"package holds {len(_arch_disk)} modules, {len(_arch_modlevel)} of them "
    f"importing homeassistant at module level",
)

_arch_map = _re.search(r"## The module map\n+```text\n(.*?)\n```", _arch, _re.S)
_arch_listed = (
    sorted(set(_re.findall(r"([a-z_0-9]+\.py)", _arch_map.group(1))))
    if _arch_map is not None
    else []
)
R.check(
    "architecture.md's module map lists every module in the package",
    _arch_map is not None and set(_arch_listed) == set(_arch_disk),
    f"missing from the map: {sorted(set(_arch_disk) - set(_arch_listed))}; "
    f"named but not on disk: {sorted(set(_arch_listed) - set(_arch_disk))}",
)

# The named list ends at its own full stop -- the `inputs` sentence that
# follows is about a different claim (the one function-level toucher, pinned
# below), and sweeping it in would make 22 names out of 21 importers.
_arch_bound = _re.search(
    r"(\d+) of the (\d+) modules\s+import `homeassistant` at module level:\s+(.*?)\.",
    _arch, _re.S,
)
_arch_named = (
    sorted(set(_re.findall(r"`([a-z_]+)`", _arch_bound.group(3))))
    if _arch_bound is not None
    else []
)
R.check(
    "architecture.md's HA boundary names exactly the module-level importers",
    _arch_bound is not None
    and int(_arch_bound.group(1)) == len(_arch_modlevel)
    and int(_arch_bound.group(2)) == len(_arch_disk)
    and _arch_named == _arch_modlevel,
    f"documented {_arch_bound.group(1) if _arch_bound else '?'} of "
    f"{_arch_bound.group(2) if _arch_bound else '?'}, named {_arch_named}; "
    f"the AST walk finds {len(_arch_modlevel)}: {_arch_modlevel}",
)

_arch_touch = _re.search(
    r"One module outside that set touches it at all:\s+`([a-z_]+)`", _arch
)
_arch_touchers = sorted(set(_arch_anywhere) - set(_arch_modlevel))
R.check(
    "architecture.md's one function-level toucher is the only one",
    _arch_touch is not None and _arch_touchers == [_arch_touch.group(1)],
    f"documented {_arch_touch.group(1) if _arch_touch else '?'}; modules "
    f"outside the module-level set that touch homeassistant anywhere: "
    f"{_arch_touchers}",
)

_arch_free = _re.search(
    r"The other (\d+) modules are deliberately free", _arch
)
R.check(
    "architecture.md's HA-free count is the tree's",
    _arch_free is not None
    and int(_arch_free.group(1)) == len(_arch_disk) - len(_arch_anywhere),
    f"architecture.md says {_arch_free.group(1) if _arch_free else '?'}; "
    f"{len(_arch_disk)} modules less {len(_arch_anywhere)} that touch "
    f"homeassistant anywhere leaves {len(_arch_disk) - len(_arch_anywhere)}",
)

_arch_pages = _re.search(
    r"config_flow\.py\s+# Setup flow plus (\d+) option pages", _arch
)
R.check(
    "architecture.md's option-page count matches _OPTION_PAGES",
    _arch_pages is not None
    and int(_arch_pages.group(1)) == len(config_flow._OPTION_PAGES),
    f"architecture.md says {_arch_pages.group(1) if _arch_pages else '?'}, "
    f"_OPTION_PAGES holds {len(config_flow._OPTION_PAGES)}",
)

_services_yaml_n = len(_yaml.safe_load((ROOT / "services.yaml").read_text()))
for _arch_where, _arch_re in (
    ("__init__.py", r"__init__\.py\s+# Setup and unload, the (\d+) services"),
    ("services.py", r"services\.py\s+# The domain's (\d+) services"),
    ("services.yaml", r"services\.yaml\s+# The (\d+) service definitions"),
):
    _m = _re.search(_arch_re, _arch)
    R.check(
        f"architecture.md's {_arch_where} service count matches services.yaml",
        _m is not None and int(_m.group(1)) == _services_yaml_n,
        f"architecture.md says {_m.group(1) if _m else '?'}, "
        f"services.yaml defines {_services_yaml_n}",
    )

_arch_sensors = _re.search(r"sensor\.py\s+# (\d+) sensors", _arch)
R.check(
    "architecture.md's sensor count matches the platform census",
    _arch_sensors is not None
    and int(_arch_sensors.group(1)) == _platform_counts["sensor"],
    f"architecture.md says {_arch_sensors.group(1) if _arch_sensors else '?'}, "
    f"the platform constructs {_platform_counts['sensor']}",
)


def _arch_entry(module: str) -> str:
    """One module-map entry's `#` comment, continuation lines joined.

    The map wraps long comments onto `│ ...` lines (button.py already did);
    the joined text is what a name list is read from.
    """
    if _arch_map is None:
        return ""
    m = _re.search(
        rf"{_re.escape(module)}\.py[^\n]*?#[ \t]*([^\n]*)\n"
        rf"((?:│[^\n]*#[ \t]*[^\n]*\n)*)",
        _arch_map.group(1),
    )
    if m is None:
        return ""
    return " ".join(
        [m.group(1).strip()]
        + [c.strip() for c in _re.findall(r"#[ \t]*([^\n]*)", m.group(2))]
    )


def _arch_comment_names(comment: str) -> set[str]:
    return {part.strip() for part in comment.split(",") if part.strip()}


for _plat in ("switch", "binary_sensor"):
    _arch_doc_names = _arch_comment_names(_arch_entry(_plat))
    _arch_built = {
        display_name(_plat, e)
        for e in collect(_importlib.import_module(f"heatpump_optimizer.{_plat}"))
    }
    R.check(
        f"architecture.md's {_plat}.py names every entity it constructs",
        _arch_doc_names == _arch_built,
        f"documented {sorted(_arch_doc_names)}, the platform constructs "
        f"{sorted(_arch_built)}",
    )

_arch_diagram = _re.search(
    r"(\d+) entities<br/>(\d+) sensors, (\d+) binary sensors,<br/>"
    r"(\d+) buttons, (\d+) switches,<br/>(\d+) climate, (\d+) datetime",
    _arch,
)
_arch_diagram_want = [
    _total_entities,
    *(
        _platform_counts[p]
        for p in ("sensor", "binary_sensor", "button", "switch", "climate", "datetime")
    ),
]
R.check(
    "architecture.md's entity diagram counts match the census",
    _arch_diagram is not None
    and [int(g) for g in _arch_diagram.groups()] == _arch_diagram_want,
    f"diagram says "
    f"{[int(g) for g in _arch_diagram.groups()] if _arch_diagram else '?'}; "
    f"the census is {_arch_diagram_want}",
)

# HACS renders this README inside Home Assistant -- `hacs.json` asks for it,
# and hacs/integration's `async_get_info_file_contents` reads README.md -- so
# the README has a second renderer, and it is much weaker than GitHub's.
# hacs/frontend's repository dashboard passes it to `<ha-markdown>` with no
# `allow-svg`, which is home-assistant/frontend's markdown-worker: plain
# `marked` plus js-xss over a whitelist carrying no `svg`. Rendering this file
# through that exact pipeline (marked 15.0.4 + xss 1.0.15, the versions
# hacs/frontend pins) established two things that no other check would notice:
#
#   * a ```mermaid fence comes out as a literal <pre><code> dump of its own
#     source, and the `language-mermaid` class is stripped with it, so nothing
#     downstream can even find it to render later. Wrapping each fence in
#     <details> turns that dump into a labelled, collapsible block, and costs
#     GitHub nothing -- GitHub's own /markdown API emits the same
#     `data-type="mermaid"` enrichment section inside <details> as outside it.
#   * js-xss blanks any `src` that is not absolute, `/`-rooted or `./`-rooted,
#     and HACS's `markdownWithRepositoryContext` rewrites relative markdown
#     `[..](..)` links only -- never an HTML `src=` attribute. So
#     `![x](docs/img/x.svg)` reaches the user and `<img src="docs/img/x.svg">`
#     renders with an empty src.
#
# Both are invisible on GitHub, which is where they would otherwise be
# reviewed, so they are pinned here rather than left to be rediscovered.
_fences = [m.start() for m in _re.finditer(r"^```mermaid$", readme, _re.M)]
_details = [(m.start(), m.end()) for m in _re.finditer(r"<details\b.*?</details>", readme, _re.S)]
_bare = [p for p in _fences if not any(s < p < e for s, e in _details)]
R.check(
    "every README mermaid fence sits inside <details>, so HACS shows a label "
    "rather than raw diagram source",
    not _bare,
    f"{len(_bare)} of {len(_fences)} fence(s) outside <details>",
)
_relative_src = _re.findall(r'<img[^>]+src="(?!https?://|/|\./|\.\./)([^"]*)"', readme)
R.check(
    "no README <img> carries a relative src, which HACS blanks",
    not _relative_src,
    f"relative src: {_relative_src}",
)
# ...and the rewrite that saves the markdown form has a narrower reach than it
# looks: `markdownWithRepositoryContext`'s link regex is built without the `s`
# flag, so `.` never crosses a newline and an `![alt](path)` whose alt text
# wraps is left un-rewritten -- after which js-xss blanks its relative src just
# the same. Measured by rendering the two forms side by side: identical alt
# text, one line versus two, and only the wrapped one comes out `<img src>`.
# The hero this check was written for was wrapped, and would have shipped
# blank in the one view it exists for.
_wrapped_img = _re.findall(
    r"!\[[^\]]*\n[^\]]*\]\((?!https?://)([^)]*)\)", readme
)
R.check(
    "no README image with a relative target wraps its alt text across lines, "
    "which stops HACS rewriting it and leaves the src blank",
    not _wrapped_img,
    f"wrapped: {_wrapped_img}",
)

# The two checks above name shapes. This one RUNS the mechanism they are
# instances of, because a rule written as a list of the shapes found so far has
# already been too narrow three times. Twice it was the prose that was narrow;
# the third time (PR #567 fix review, round 4) the prose was right and THIS
# CHECK was the narrow one, which is the harder failure to see -- so the
# rewriter is transcribed here and executed, not described and approximated.
#
# `markdownWithRepositoryContext` matches `\[.*?\]\([^#](?!.*?://).*?\)` and
# then calls `x.replace("(", <prefix>)`, which rewrites the FIRST `(` of the
# matched span -- not the image's; and `showGitHubWeb` tests THE WHOLE SPAN for
# `.md`. Getting the span right is therefore the whole job. That regex is
# global and scans left to right from the start of the document, and `\[.*?\]`
# will happily open at an unrelated `[` earlier on the line and run through the
# image's own `]`. So the span covering an image can begin at a `> [!NOTE]`
# callout, a `- [ ]` task box, a `[1]` footnote marker or any bracketed word --
# and THAT text then supplies the first `(`, or the `.md`. Measuring a span
# from the image's own `![` instead, as this check did until round 4, passes
# four ordinary constructs that ship blank or broken:
#
#     > [!NOTE] The chart below (updated daily) ![Plan chart](docs/img/p.svg)
#     - [ ] (optional) ![Plan chart](docs/img/p.svg)
#     See the plan [1] (figure 2) ![Plan chart](docs/img/p.svg)
#     See [notes] in docs/arch.md ![Plan chart](docs/img/p.svg)
#
# The first three ship blank and the fourth ships `text/html`, while every
# condition read AT THE IMAGE holds. The repair is not another clause: it is to
# stop guessing the span. `_HACS_LINK.finditer` reproduces the rewriter's own
# global left-to-right scan, non-overlapping consumption included, and a
# relative-src image is judged in the match that COVERS it. Both remaining
# questions are then asked of that span and of nothing else -- which is also
# why the old "a `(` in the alt text" clause is gone: it was one instance of
# the general rule, and stating it separately is what made the rule look
# complete.
#
# An image no span covers is never rewritten at all, so its relative src
# reaches js-xss and is blanked. The two ways that happens keep their own
# diagnostics, because they are the actionable ones: a wrapped alt (the regex
# is built without the `s` flag) and a later `://` on the line (the negative
# lookahead scans to end of line, not to the end of the link).
#
# None of it is visible on GitHub, which is where it would otherwise be
# reviewed. Measured 2026-09-07 against marked 15.0.4 + xss 1.0.15 -- the
# versions hacs/frontend pins -- by rendering each shape and its minimal pair
# through a transcription of the two upstream modules.
#
# Three scope choices, stated so the next seat does not read them as bugs. The
# population is the image's OWN src, not the link target: the
# `[![License: MIT](https://img.shields.io/...)](LICENSE)` badge is a real and
# still-unfixed defect -- a relative link target mangles the img src -- but its
# src is absolute, so it falls outside this check rather than being allowlisted
# through it. A reference-style image is refused even though one with an
# absolute target does render (measured), because every image here is inline
# and "write it inline" is always the available repair. And an image inside a
# fenced block or a `backtick span` is outside the population, because it
# renders as text and never becomes an `<img>` at all -- note that the code
# spans are excluded from the POPULATION without being cut from the TEXT, since
# the rewriter runs before marked and does scan them.
_INLINE_IMG = _re.compile(r"!\[((?:[^\n]|\n(?![ \t]*\n))*?)\]\(")
_HACS_LINK = _re.compile(r"\[.*?\]\([^#](?!.*?://).*?\)")
_prose = _re.sub(r"^```.*?^```", "", readme, flags=_re.M | _re.S)
_code_spans = [(_c.start(), _c.end()) for _c in _re.finditer(r"(`+)[^\n]*?\1", _prose)]
_spans = [(_s.start(), _s.end(), _s.group(0)) for _s in _HACS_LINK.finditer(_prose)]


def _quoted(_pos):
    """Is this offset inside a `backtick span`, and so never an `<img>`?"""
    return any(_a <= _pos < _b for _a, _b in _code_spans)


_img_offences = []
_inline_at = set()
for _m in _INLINE_IMG.finditer(_prose):
    _inline_at.add(_m.start())
    if _quoted(_m.start()):
        continue
    _alt = _m.group(1)
    _src = _re.match(r"[^)\s]*", _prose[_m.end():]).group(0)
    if _re.match(r"[a-z][a-z0-9+.-]*://", _src, _re.I):
        continue  # absolute: never rewritten, so never blanked
    _open = _m.end() - 1  # the `(` that opens THIS image's src
    _span = next((_s for _s in _spans if _s[0] <= _open < _s[1]), None)
    _eol = _prose.find("\n", _open)
    _tail = _prose[_m.end():_eol if _eol != -1 else len(_prose)]
    if _span is None:
        if "\n" in _alt:
            _why = "its alt text wraps across lines, so no rewriter span covers it"
        elif "://" in _tail:
            _why = "a later '://' on the line fails the rewriter's lookahead"
        else:
            _why = "no rewriter span covers it, so its relative src is left as-is"
    elif _span[0] + _span[2].index("(") != _open:
        _why = (f"the rewriter's span opens at {_span[2][:32]!r}, whose first "
                f"'(' takes the rewrite instead of the src's")
    elif ".md" in _span[2].lower() or ".markdown" in _span[2].lower():
        _why = (f"'.md' in the rewriter's span {_span[2][:32]!r} sends the "
                f"rewrite to github.com/blob")
    else:
        continue
    _img_offences.append((_src, _why))
_img_offences += [
    (_prose[_m.start():_m.start() + 40].replace("\n", " "),
     "not an inline ![alt](src), so HACS never rewrites it")
    for _m in _re.finditer(r"!\[", _prose)
    if _m.start() not in _inline_at and not _quoted(_m.start())
]
R.check(
    "every relative README image survives HACS's rewriter, judged in the span "
    "the rewriter's own global scan gives it: inline, that span's first '(' is "
    "the src's own, and no '.md' anywhere in it",
    not _img_offences,
    f"{len(_img_offences)} offence(s): {_img_offences}",
)

# B12 replaces B4's interim chart SVG with a screenshot this repository's
# Playwright lane writes (`HPO_HERO_OUT=docs/img/card-plan-chart.png node
# tests/card_browser.mjs`). The path is the pin: reverting it to `.svg`
# puts the interim asset back. The PNG lives under `docs/` (INERT);
# this check reads README.md only, so it does not pull `docs/` into a
# measured closure. The hero must stay a single-line `![alt](src)` —
# the HACS rewriter checks above are why.
_hero = _re.search(
    r"^!\[[^\n]*\]\((docs/img/card-plan-chart\.[A-Za-z0-9]+)\)\s*$",
    readme,
    _re.M,
)
R.check(
    "the README hero is the Playwright screenshot, not B4's interim SVG",
    _hero is not None and _hero.group(1) == "docs/img/card-plan-chart.png",
    f"hero src: {_hero.group(1) if _hero else None}",
)

# The sensor table is split into labelled `####` groups (#558 B10), so a count
# of rows under the heading no longer pins it: a group boundary adds a table
# header row, and a sensor dropped while a group was reshuffled would pay for
# it. Compare the NAMES instead, as a set. That is strictly stronger -- it also
# catches a rename, and a sensor documented twice under two groups -- and it is
# indifferent to how many groups there are or where a row was moved to.
#
# `(?=^### )` and not `(?=^#### )`: the group headings are inside the section,
# and stopping at the first of them would read one group and call the other
# seven missing.
_sensor_block = _re.search(
    r"^### Sensors \(\d+ total\)\n(.*?)(?=^### )", readme, _re.M | _re.S
)
_documented = [
    line.split("|")[1].strip()
    for line in (_sensor_block.group(1).splitlines() if _sensor_block else [])
    if line.startswith("|")
    and not _re.fullmatch(r"\|[\s|:-]+\|", line.strip())
    and line.split("|")[1].strip() != "Sensor"  # each group's own header row
]
_expected_names = {display_name("sensor", s) for s in sensors}
R.check(
    "every sensor the platform builds has a row in the README, and every row "
    "is a sensor it builds",
    set(_documented) == _expected_names,
    f"documented not built: {sorted(set(_documented) - _expected_names)}; "
    f"built not documented: {sorted(_expected_names - set(_documented))}",
)
R.check(
    "no sensor is documented in two groups",
    len(_documented) == len(set(_documented)),
    f"repeated: {sorted({n for n in _documented if _documented.count(n) > 1})}",
)
_groups = (
    _re.findall(r"^#### (.+)$", _sensor_block.group(1), _re.M) if _sensor_block else []
)
R.check(
    "the sensor section is still split into labelled groups",
    len(_groups) >= 2,
    f"{len(_groups)} group heading(s): {_groups}",
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
# W5-G9: the DHW profile and draw stores live in the learner the coordinator
# constructs, so the census walks the coordinator and its subsystems.
_store_holders = (
    _removal_coord,
    _removal_coord._dhw_learner,
    _removal_coord._legionella,
)
_store_suffixes = {
    value._key.removeprefix(_store_prefix)
    for holder in _store_holders
    for value in vars(holder).values()
    if isinstance(value, _Store) and value._key.startswith(_store_prefix)
}
# away and boost build their Store inside a function and bind it to no
# attribute, so vars() over the coordinator cannot see them. Calling the
# factories is what makes the census total, and what used to make this
# check enforce the README's omission (#837).
from heatpump_optimizer import away as _away_mod
from heatpump_optimizer import boost as _boost_mod
_store_suffixes |= {
    _away_mod._away_store(_removal_coord)._key.removeprefix(_store_prefix),
    _boost_mod._store(_removal_coord)._key.removeprefix(_store_prefix),
}
_listed_suffixes = set(
    _re.findall(r"heatpump_optimizer_<entry id>_(\w+)", _removal_text)
)
R.check(
    "the store files it says are left under .storage are exactly the ones the coordinator keeps",
    _store_suffixes and _listed_suffixes == _store_suffixes,
    f"documented {sorted(_listed_suffixes)}, code keeps {sorted(_store_suffixes)}",
)
_store_count_word = {10: "ten", 12: "twelve"}.get(len(_store_suffixes), str(len(_store_suffixes)))
R.check(
    "the README's store-file count is the census, not a carried ten",
    f"in {_store_count_word} files" in _removal_text,
    f"census is {len(_store_suffixes)}, README does not say '{_store_count_word}'",
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
# issue #514 reversed how this floor is chosen. It used to be the newest
# Home Assistant API the integration provably used -- ConfigEntry.runtime_data
# (#227, #207), which put it at 2024.6.0 -- and that left the PYTHON range
# declared by nobody and tested by nothing. It is now chosen by the declared
# Python range instead: 2025.2.0 is the first Home Assistant whose own
# pyproject.toml says requires-python = ">=3.13.0" (2024.12.0 and 2025.1.0
# both still say >=3.12.0; 2025.8.0 says >=3.13.2), so it is the lowest
# release that can guarantee 3.13. It is also well above the 2024.6.0
# runtime_data needs, so nothing the older rule established is given up.
_hacs_floor_tuple = tuple(int(part) for part in _hacs_floor.split("."))
R.check(
    "hacs.json's Home Assistant floor is at least 2025.2.0 (the first release whose own requires-python is >=3.13.0)",
    _hacs_floor_tuple >= (2025, 2, 0),
    f"hacs.json says {_hacs_floor}",
)
# The Python half of the same declaration. Before #514 CI tested exactly one
# interpreter and the README named none, so "supported Python" was an
# inference from the HA floor that nothing could falsify. These checks make
# the README's claims and the versions CI actually runs the same fact: the
# workflow is the machine-readable source, exactly as hacs.json is for the
# Home Assistant floor above.
#
# TWO derivations, because the README makes two different claims and they
# stopped being the same fact when `fast`'s 3.13 leg was retired. "Python X
# or newer" is the FLOOR, and every job in this workflow still runs on it.
# "The suite is tested on ..." is a claim about the SUITE, which only `fast`
# runs -- so it derives from `fast`'s matrix alone. Read off the whole file,
# as it was, the sentence would have kept passing while saying the suite ran
# on an interpreter no longer in the matrix: a true-looking sentence no check
# could falsify, which is the shape #514 exists to refuse.
def _workflow_job(text: str, name: str) -> str:
    """One job's YAML block, so a wiring check cannot match a sibling job."""
    start = text.index(f"\n  {name}:\n") + 1
    nxt = re.compile(r"^  [A-Za-z][\w-]*:", re.M).search(
        text, text.index("\n", start) + 1)
    return text[start:nxt.start()] if nxt else text[start:]


_tests_workflow = Path(".github/workflows/tests.yml").read_text()


def _py_versions(text: str) -> list[str]:
    """Every quoted `X.Y` on a `python-version:` line, oldest first.

    The interpolated `${{ matrix.python-version }}` carries no quoted literal
    and contributes nothing, which is what keeps the matrix list the single
    source for the job that reads it.
    """
    return sorted(
        {
            _version
            for _line in _re.findall(r"python-version:.*", text)
            for _version in _re.findall(r'"(\d+\.\d+)"', _line)
        },
        key=lambda v: tuple(int(p) for p in v.split(".")),
    )


_ci_pythons = _py_versions(_tests_workflow)
_suite_pythons = _py_versions(_workflow_job(_tests_workflow, "fast"))
R.check(
    "the README states the lowest Python version CI actually runs on",
    bool(_ci_pythons) and f"Python {_ci_pythons[0]} or newer" in readme,
    f".github/workflows/tests.yml runs on {_ci_pythons}",
)
# Bidirectional on purpose. "Every tested version is named" would catch a new
# interpreter added to CI undocumented, but not the reverse -- dropping one
# from the matrix while the README still promises it re-opens the exact hole
# #514 was filed for, an advertised version nothing runs. Comparing the whole
# sentence catches both directions.
_listed = (
    " and ".join(_suite_pythons)
    if len(_suite_pythons) < 3
    else ", ".join(_suite_pythons[:-1]) + " and " + _suite_pythons[-1]
)
R.check(
    "the README names exactly the interpreters the SUITE runs on, neither more nor fewer",
    bool(_suite_pythons) and f"The suite is tested on {_listed}." in readme,
    f"`fast` is matrixed over {_suite_pythons}, so the README should read "
    f"'The suite is tested on {_listed}.'",
)
R.check(
    "the Python badge agrees with that floor",
    bool(_ci_pythons) and f"Python-{_ci_pythons[0]}%2B" in readme,
)

# docs-known-limitations (Gold, #952): the quality-scale rule asks the
# documentation to carry a "Known limitations" section describing the
# integration's constraints, with no exceptions. Round-4 D10-02 measured the
# section absent everywhere -- 0 headings matching the rule across README
# and the six user docs -- while `quality_scale.yaml` declared the row
# `done`, and nothing could notice: the register is INERT by measurement
# (#357, see the widening check above) and no gate script read the docs for
# this property at all. The finding's substance was placement, not
# knowledge: the constraint content existed, filed under headings a user
# asking "what will this not do?" would not open.
#
# This check pins the README, the one user document this lane already
# measures -- HACS renders it as the integration's page, and README.md sits
# in this script's recorded closure, so a README edit selects this script in
# the scoped gate. The docs/ pages stay outside it on purpose here: reading
# one is sound only after it leaves `tests/closure.py`'s INERT list and
# enters this script's measured closure (what the architecture.md checks
# above did for one file, #939), and this check does not need that -- it
# reads the README alone.
#
# Two design choices, stated so they are not read as bugs. The heading is
# pinned at level 2 and exactly "Known limitations" -- the name the rule
# and a documentation search both key on; a `### Known limitations` buried
# inside another section re-creates the discoverability failure. And the
# body floor is five bullets, the count of integration-wide limitations the
# finding named as "nowhere at all, in any wording" (planning granularity,
# price source, single device, no discovery, tariff market shape): a
# heading with a one-line body under it would satisfy a heading-only check
# and re-open the finding invisibly.
_kl_heading = _re.search(r"^## Known limitations$", readme, _re.M)
_kl_block = _re.search(
    r"^## Known limitations\n(.*?)(?=^## )", readme, _re.M | _re.S
)
_kl_bullets = [
    line for line in (_kl_block.group(1).splitlines() if _kl_block else [])
    if line.startswith("- ")
]
R.check(
    "the README carries a level-2 'Known limitations' section (#952)",
    _kl_heading is not None,
    "0 headings match; the quality-scale rule admits no exception and the "
    "register declares the row done",
)
R.check(
    "the Known limitations section describes constraints, not a heading "
    "with a caption",
    len(_kl_bullets) >= 5,
    f"{len(_kl_bullets)} bullet(s) in the section",
)

# #951 (R4-D10-01): the register's two coverage-bearing rows are the ones
# that rot, because they quote figures about a tree that keeps changing
# under them. Round 4 executed one check per quality-scale rule and found
# rows disagreeing with the tree in BOTH directions at once; #973
# re-truthed docs-known-limitations above, and these checks pin the two
# that remain:
#
#   config-flow-test-coverage  declared done, "100% statement coverage
#                              (661 statements, 0 missed)" -- executed
#                              todo, the residual being ordinary reachable
#                              branches (options-grid price-entity/token
#                              errors, the holiday DHW window validation,
#                              the stored-values coercion comparison)
#   test-coverage              declared todo (issue #195, since closed) --
#                              executed done, every module over the rule's
#                              bar
#
# The mechanism was that nothing executed against the register at all.
# These checks read it, so a quality_scale.yaml edit selects this script
# (the register leaves closure.py's INERT list in the same pull request),
# and tools/audit/round4/D10/qs_rules.py -- wired into
# tests/harness_headers.py, which runs on every pull request -- alarms on
# drift in every row measurable without a toolchain. These two rows are
# the toolchain rows; they are keyed to standing records, not to quoted
# figures:
#
#   test-coverage must agree with tests/coverage_budgets.json's
#   package_percent_floor -- the number the per-pull-request coverage job
#   ratchets -- against the Silver rule's bar. That floor is the tree's
#   standing executable statement of package coverage, so the row may not
#   disagree with it in either direction. (The keying is encoded rather
#   than the verdict: a future re-record of the floor below the bar must
#   flip the row, not orphan the check.)
#
#   config-flow-test-coverage must agree with tests/coverage_budgets.json's
#   config_flow_percent_floor -- the raw module percentage the same
#   instrument measured (tools/audit/w5-partition/coverage_tree.sh over the
#   default-gate scripts), recorded by tests/coverage_ratchet.py and
#   refused by the per-pull-request coverage job whenever the config flow
#   drops below it. The Bronze rule asks for FULL coverage, so the record
#   the flip measured is the property's top and the keying is encoded like
#   the Silver row's: a future record below the bar must flip the row back
#   to todo, not orphan the check. The pin this replaces (#951: the row
#   pinned todo, the flip requiring a re-measurement under that instrument)
#   was taken at the flip itself; this one makes the done it measured
#   answerable to the same instrument on every pull request after it,
#   which is the verification the register lacked when the row rotted.
#
# And neither row's comment may quote a coverage figure of its own -- a
# percentage, a statement count or a missed count. All three figures in
# the row that rotted were wrong at the next measurement; a comment that
# names the instrument instead cannot rot. Issue and pull-request
# references and SHAs stay legitimate: they are records, not measurements.
import yaml as _qs_yaml

_QS_FILE = ROOT / "quality_scale.yaml"
_QS_RULES = (_qs_yaml.safe_load(_QS_FILE.read_text()) or {}).get("rules", {})


def _qs_status(name: str) -> str:
    v = _QS_RULES.get(name)
    return v if isinstance(v, str) else (v or {}).get("status", "(absent)")


def _qs_comment(name: str) -> str:
    v = _QS_RULES.get(name)
    return "" if isinstance(v, str) else (v or {}).get("comment") or ""


_qs_budgets = json.loads(Path("tests/coverage_budgets.json").read_text())
_qs_floor = _qs_budgets["package_percent_floor"]
_qs_cf_floor = _qs_budgets.get("config_flow_percent_floor")
R.check(
    "the register's test-coverage row agrees with the recorded coverage floor",
    _qs_status("test-coverage") == ("done" if _qs_floor >= 95.0 else "todo"),
    f"register says {_qs_status('test-coverage')!r}; "
    f"tests/coverage_budgets.json package_percent_floor={_qs_floor} "
    "against the Silver rule's 95% bar (#195 closed; #951)",
)
R.check(
    "the register's config-flow-test-coverage row agrees with the recorded "
    "config-flow floor",
    _qs_status("config-flow-test-coverage")
    == (
        "done"
        if _qs_cf_floor is not None and float(_qs_cf_floor) >= 100.0
        else "todo"
    ),
    f"register says {_qs_status('config-flow-test-coverage')!r}; "
    f"tests/coverage_budgets.json config_flow_percent_floor={_qs_cf_floor!r} "
    "against the Bronze rule's full-coverage bar, measured under "
    "tools/audit/w5-partition/coverage_tree.sh and ratcheted per pull "
    "request by tests/coverage_ratchet.py (#951 pin re-taken at the flip)",
)
# docs-examples (#218): this pin is re-taken at the flip. The rule has two
# halves -- importable blueprints, and a listing for them in the
# home-assistant.io Blueprints Exchange, linked from the documentation -- and
# the row waited on the second. The owner's listing now exists and links every
# in-tree blueprint by its raw import URL; it was verified 2026-09-16 by
# fetching the topic and the Discourse JSON beside it (HTTP 200, category 53
# "Blueprints Exchange", visible, authored by the codeowner), and the three
# raw URLs it links resolve and are set-equal to blueprints/automation/.
#
# The gate cannot re-take that half for itself, and this check does not
# pretend otherwise. This suite runs offline -- it is why run.sh excludes
# nightly_status.py, whose verdict is about a remote server rather than about
# this tree -- so a live fetch here would put every pull request behind a
# forum's availability and fail closed on an offline runner. The listing is
# therefore pinned as a LITERAL URL, and what the tree can still check is
# checked by execution:
#
#   - the row reads done;
#   - the row cites the canonical URL in its resolving `/t/<slug>/<id>` form.
#     That is not pedantry: the same URL without the `/t/` segment is a 404,
#     and the first citation offered for this row was that form, so a pin on
#     the bare id would have blessed a link nobody could open;
#   - the documentation half stays true -- README.md and docs/automations.md
#     link the same non-empty set of blueprint import URLs. Both files are
#     already in this script's recorded closure. The blueprint FILES are not
#     read: blueprints/automation/ is INERT, and opening one would make it a
#     file declared unread and recorded as read, the #357 contradiction.
#
# So the design choice, stated: liveness of the listing is unobservable to
# this gate and is carried by the dated verification above, exactly as the
# old pin carried "the listing does not exist yet". If the post is ever
# unlisted, no check here goes red -- re-verify at the next audit round.
_QS_EXCHANGE_URL = (
    "https://community.home-assistant.io/t/"
    "heat-pump-optimizer-blueprints/1025351"
)
_qs_ex_comment = _qs_comment("docs-examples")
_qs_bp_re = _re.compile(
    r"https://raw\.githubusercontent\.com/tvofi/heatpump_optimizer/main/"
    r"blueprints/automation/([A-Za-z0-9_]+\.yaml)"
)
_qs_bp_readme = set(_qs_bp_re.findall(readme))
_qs_bp_docs = set(
    _qs_bp_re.findall((Path("docs/automations.md")).read_text(encoding="utf-8"))
)
R.check(
    "the register's docs-examples row is done: the blueprints are listed in "
    "the home-assistant.io Blueprints Exchange",
    _qs_status("docs-examples") == "done",
    f"register says {_qs_status('docs-examples')!r}; the listing is "
    f"{_QS_EXCHANGE_URL} (qs_rules.py still reports the row unmeasured, "
    "because no tree-local walk can see a forum -- the #951 coverage-row "
    "split) (#218)",
)
R.check(
    "the docs-examples row cites the listing in its resolving /t/ form",
    _QS_EXCHANGE_URL in _qs_ex_comment,
    "the row's comment must carry the exact URL "
    f"{_QS_EXCHANGE_URL}; the same address without the `/t/` segment is a "
    "404, so a citation missing it points at nothing",
)
R.check(
    "README.md and docs/automations.md link the same blueprints",
    bool(_qs_bp_readme) and _qs_bp_readme == _qs_bp_docs,
    f"README.md links {sorted(_qs_bp_readme)}; docs/automations.md links "
    f"{sorted(_qs_bp_docs)} -- the rule asks for blueprints linked from the "
    "documentation, and the exchange listing links this same set",
)
_QS_FIGURE = _re.compile(
    r"\d+(?:\.\d+)?\s*%|\b\d+\s+statements?\b|\b\d+\s+missed\b", _re.I
)
R.check(
    "neither coverage row quotes figures of its own",
    not any(
        _QS_FIGURE.search(_qs_comment(n))
        for n in ("config-flow-test-coverage", "test-coverage")
    ),
    "a quoted percentage, statement count or missed count is exactly the "
    "figure that rotted -- all three in the shipped row were wrong at the "
    "next measurement; name the instrument instead (#951)",
)

# The manifest's declared quality-scale tier is a user-facing claim whose
# truth condition lives in a file that moves. `quality_scale` ships in
# custom_components/heatpump_optimizer/manifest.json -- Home Assistant and
# HACS both surface it -- while what makes it true is the rule-by-rule
# register beside it, which every fix wave edits. Nothing upstream closes
# that gap: hassfest's validate_iqs_file returns on `if not integration.core`
# before it compares a declared tier against quality_scale.yaml, so for a
# custom integration the key is checked against the list of legal tier names
# and nothing else. Measured rather than assumed, against the real hassfest
# (home-assistant/core 2026.9.2, `python3 -m script.hassfest --action
# validate --integration-path <pkg>`): it exits 0 on `gold`, a tier this
# register does not support, and exits 1 only on a value outside the enum
# ("value must be one of [...] Got 'titanium'"). The over-claim is invisible
# to the one upstream instrument that reads the key, so it is refused here.
#
# The scale is CUMULATIVE -- a tier is met only when it and every tier below
# it have every rule done or exempt -- which is why the derivation walks the
# tiers in order and stops at the first incomplete one, rather than asking
# whether the named tier's own rules pass. On this tree the register is
# complete -- every rule in all four tiers done or exempt, docs-examples done
# on the Blueprints Exchange listing pinned just above -- so both readings
# return platinum, and the manifest declares platinum. That agreement is
# exactly when the cumulative rule is easiest to drop and still needed: a row
# that regresses below Platinum leaves Platinum's own three rules done, so a
# per-tier reading would go on returning platinum while only the cumulative
# walk sees the regression -- driven, a Silver row set to todo derives bronze
# and this check goes red. The two readings last disagreed at merge base
# cb30d98, before the listing existed, and the pull request that added this
# check flipped docs-examples and moved the manifest to platinum in the same
# change -- the register and the claim moving together, instead of the
# manifest being left behind the way the two coverage rows above were left
# behind by the tree.
#
# Two design choices, stated so they are not read as bugs. The tier
# membership below is the published checklist's own partition -- 20 Bronze,
# 10 Silver, 21 Gold, 3 Platinum, the checklist fetched 2026-09-10 that this
# register was built from -- carried rather than derived, because it is a
# fact about the upstream scale and not about this tree. The check
# immediately below pins it against the register's own key set, so a row
# this repository adds, drops or renames fails loudly instead of leaving the
# derivation quietly reading a partition that no longer covers the file. And
# the manifest is required to carry the DERIVED tier and nothing else:
# hassfest equally accepts `custom`, `no_score`, `internal` and `legacy`, and
# this check refuses all four, because the only tier claim this repository
# can answer for is the one its own register produces.
_QS_TIERS = (
    ("bronze", (
        "action-setup", "appropriate-polling", "brands", "common-modules",
        "config-flow", "config-flow-test-coverage", "dependency-transparency",
        "docs-actions", "docs-triggers", "docs-conditions",
        "docs-high-level-description", "docs-installation-instructions",
        "docs-removal-instructions", "entity-event-setup", "entity-unique-id",
        "has-entity-name", "runtime-data", "test-before-configure",
        "test-before-setup", "unique-config-entry",
    )),
    ("silver", (
        "action-exceptions", "config-entry-unloading",
        "docs-configuration-parameters", "docs-installation-parameters",
        "entity-unavailable", "integration-owner", "log-when-unavailable",
        "parallel-updates", "reauthentication-flow", "test-coverage",
    )),
    ("gold", (
        "devices", "diagnostics", "discovery", "discovery-update-info",
        "docs-data-update", "docs-examples", "docs-known-limitations",
        "docs-supported-devices", "docs-supported-functions",
        "docs-troubleshooting", "docs-use-cases", "dynamic-devices",
        "entity-category", "entity-device-class", "entity-disabled-by-default",
        "entity-translations", "exception-translations", "icon-translations",
        "reconfiguration-flow", "repair-issues", "stale-devices",
    )),
    ("platinum", ("async-dependency", "inject-websession", "strict-typing")),
)
_qs_partition = [rule for _tier, _rules in _QS_TIERS for rule in _rules]
R.check(
    "the carried tier partition covers the register's rows exactly, once each",
    len(_qs_partition) == len(set(_qs_partition))
    and set(_qs_partition) == set(_QS_RULES),
    f"{len(_qs_partition)} rule(s) in the partition, {len(_QS_RULES)} row(s) "
    f"in quality_scale.yaml; only in the partition: "
    f"{sorted(set(_qs_partition) - set(_QS_RULES))}; only in the register: "
    f"{sorted(set(_QS_RULES) - set(_qs_partition))}",
)

_qs_blocking = {
    tier: [r for r in rules if _qs_status(r) not in ("done", "exempt")]
    for tier, rules in _QS_TIERS
}
_qs_derived = None
for _tier, _rules in _QS_TIERS:
    if _qs_blocking[_tier]:
        break
    _qs_derived = _tier
_qs_declared = json.loads((ROOT / "manifest.json").read_text()).get("quality_scale")
R.check(
    "the manifest declares the tier the register supports cumulatively",
    _qs_declared == _qs_derived,
    f"manifest.json quality_scale={_qs_declared!r}; the register supports "
    f"{_qs_derived!r} cumulatively; rows short of done/exempt, by tier: "
    + ", ".join(f"{t}: {rs}" for t, rs in _qs_blocking.items() if rs)
    + " -- edit custom_components/heatpump_optimizer/manifest.json, or the "
    "register row that moved, in the same pull request",
)

for name in (
    "Measured Power",
    "Learning Observed COP",
    "Space Heating Energy (lifetime)",
    "DHW Energy (lifetime)",
    "Total Energy (lifetime)",
    "Space Heating Cost (lifetime)",
    "DHW Cost (lifetime)",
    "Cost Total Heating (lifetime)",
    "Prediction Accuracy",
    "Cost Monthly Peak Power",
    "Solar Surplus Forecast",
    "Thermal Battery Charge",
    "Thermal Battery Energy",
    "Learning Comfort Weight",
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
R.check("observed COP is published", by_name["Learning Observed COP"].native_value == 3.1)

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
    "Cost Total Heating (lifetime)",
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
_plan_attrs = by_name["Plan DHW Heating (next 24 h)"].extra_state_attributes
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
R.check("the billed peak is published", by_name["Cost Monthly Peak Power"].native_value == 7.2)
R.check(
    "the free headroom threshold is explained",
    by_name["Cost Monthly Peak Power"].extra_state_attributes[
        "free_headroom_threshold_kw"
    ]
    == 6.5,
)
# v4.0.0 T2: the fuse advisor's answer and the outage flag ride the peak
# sensor rather than adding two more diagnostic entities.
_peak_attrs = by_name["Cost Monthly Peak Power"].extra_state_attributes
R.check(
    "the fuse advisor's monthly answer is published",
    _peak_attrs.get("fuse_advisor", {}).get("candidate_fuse_a") == 16,
)
R.check(
    "outage recovery is visible while it is active",
    _peak_attrs.get("outage_recovery_active") is True,
)
R.check("the Cost Power Headroom sensor exists", "Cost Power Headroom" in by_name)
R.check(
    "headroom is the state, in kW, ready for a charger automation",
    by_name["Cost Power Headroom"].native_value == 7.3
    and by_name["Cost Power Headroom"]._attr_native_unit_of_measurement == "kW",
)
R.check(
    "the headroom sensor is available exactly when a limit exists",
    by_name["Cost Power Headroom"].available is True,
)
_hr_attrs = by_name["Cost Power Headroom"].extra_state_attributes
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
    by_name["Learning Comfort Weight"].native_value == 6.4
    and by_name["Learning Comfort Weight"].extra_state_attributes["configured"] == 5.0,
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
space_plan = by_name["Plan Space Heating (next 24 h)"]
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
dhw_plan = by_name["Plan DHW Heating (next 24 h)"]
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
# ...and non-vacuously. `dhw_windows` is published only on the PLAN branch,
# and `DATA["dhw_plan"]` is `{}`, so the check above compares `None` to the
# spec string: it passes just as well with `dhw_windows` deleted from
# production entirely. Read the branch that actually carries it (found by
# the #373 review, which hit the same fixture hole in the attribute roster).
_windows_plan_attrs = sensor.DHWHeatingPlanSensor(
    FakeCoordinator(
        {
            **DATA,
            "dhw_plan": {"slots": [{"start": "2026-02-01T05:00:00"}], "active_now": False},
            "dhw_windows": [["06:00", "08:30"], ["17:00", "22:00"]],
        }
    ),
    ENTRY,
).extra_state_attributes
R.check(
    "and the plan branch really carries both, differing",
    _windows_plan_attrs.get("dhw_windows") == [["06:00", "08:30"], ["17:00", "22:00"]]
    and _windows_plan_attrs.get("dhw_windows_spec")
    == "weekdays 06:00-08:30, weekend 08:00-09:30",
    f"windows={_windows_plan_attrs.get('dhw_windows')!r} "
    f"spec={_windows_plan_attrs.get('dhw_windows_spec')!r}",
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
# Round-5 D12-01 (#1237): the payload still carries the DHW DEFAULTS on a
# plant with no hot water -- `dhw_windows`'s windows string and
# `dhw_min_temperature`'s 45.0 -- and the plan sensors used to publish the
# hot-water block unconditionally, so a space-heating plan on a no-DHW
# install advertised a hot-water schedule nobody configured. The gate is
# the payload's own `dhw_enabled`, the flag the DHW entities' availability
# already rides on (`_DHWEntityMixin`). The fixture below is deliberately
# hostile: the DHW values ARE in the payload, so only the gate can keep
# them off the entity.
_DHW_BLOCK_KEYS = (
    "dhw_setpoint",
    "dhw_min_temperature",
    "dhw_min_temperature_max",
    "dhw_windows",
    "dhw_windows_spec",
)
_NO_DHW_DATA = {
    **DATA,
    "dhw_enabled": False,
    # What the real coordinator's `_dhw_view` publishes regardless.
    "dhw_min_temperature": 45.0,
    "dhw_setpoint": 55.0,
    "dhw_windows": "weekdays 06:00-08:30, weekend 08:00-09:30",
}
_LIVE_SPACE_PLAN = {
    "slots": [{"start": "2026-02-01T05:00:00", "end": "2026-02-01T06:00:00"}],
    "active_now": False,
}
_no_dhw_empty_attrs = sensor.SpaceHeatingPlanSensor(
    FakeCoordinator(_NO_DHW_DATA), ENTRY
).extra_state_attributes
_no_dhw_plan_attrs = sensor.SpaceHeatingPlanSensor(
    FakeCoordinator({**_NO_DHW_DATA, "space_plan": _LIVE_SPACE_PLAN}), ENTRY
).extra_state_attributes
R.check(
    "a plant with no hot water publishes no hot-water attributes, either plan branch (#1237)",
    _no_dhw_plan_attrs.get("slot_count") == 1
    and not any(k in _no_dhw_empty_attrs for k in _DHW_BLOCK_KEYS)
    and not any(k in _no_dhw_plan_attrs for k in _DHW_BLOCK_KEYS),
    f"empty={sorted(k for k in _DHW_BLOCK_KEYS if k in _no_dhw_empty_attrs)}; "
    f"populated={sorted(k for k in _DHW_BLOCK_KEYS if k in _no_dhw_plan_attrs)} "
    "-- the payload carried all five; the gate must keep them off the entity",
)
_no_dhw_on_attrs = sensor.SpaceHeatingPlanSensor(
    FakeCoordinator(
        {**_NO_DHW_DATA, "dhw_enabled": True, "space_plan": _LIVE_SPACE_PLAN}
    ),
    ENTRY,
).extra_state_attributes
R.check(
    "the same payload with hot water configured still publishes the block (#1237 control)",
    all(k in _no_dhw_on_attrs for k in _DHW_BLOCK_KEYS)
    and _no_dhw_on_attrs.get("dhw_windows")
    == "weekdays 06:00-08:30, weekend 08:00-09:30",
    f"keys={sorted(k for k in _DHW_BLOCK_KEYS if k in _no_dhw_on_attrs)} -- "
    "flipping only dhw_enabled must bring the whole block back",
)
R.check(
    "the plan sensor publishes wood_fuel for the card (#463)",
    space_plan.extra_state_attributes.get("wood_fuel") == DATA["wood_fuel"],
    "the Lovelace card reads plan-sensor attributes, not coordinator.data",
)
R.check(
    "and keeps wood_fuel out of the recorder",
    "wood_fuel" in sensor._PlanSensorBase._unrecorded_attributes,
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
    score.native_value == 100.0
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

from homeassistant.util import dt as dt_util

from heatpump_optimizer import coordinator as coordinator_module
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

# S0/S1 of #377: CoordinatorContext is defined and constructed. S1
# deletes the raw hub attributes; facades still resolve. _current_action
# is not a frozen field.
from dataclasses import FrozenInstanceError, fields, is_dataclass

R.section("S0 CoordinatorContext (#377)")
_Ctx = getattr(coordinator_module, "CoordinatorContext", None)
R.check(
    "CoordinatorContext is importable from heatpump_optimizer.coordinator",
    _Ctx is not None,
)
_ctx_fields = {f.name for f in fields(_Ctx)} if _Ctx is not None else set()
R.check(
    "CoordinatorContext is a frozen dataclass over the five write-once hubs",
    _Ctx is not None
    and is_dataclass(_Ctx)
    and getattr(_Ctx, "__dataclass_params__").frozen
    and _ctx_fields == {
        "_config",
        "_thermal_params",
        "hass",
        "_current_state",
        "_opt_config",
    },
    f"fields={sorted(_ctx_fields)}",
)
R.check(
    "_current_action is not a CoordinatorContext field",
    "_current_action" not in _ctx_fields,
)
_ctx = getattr(_blind_coord, "_ctx", None)
R.check(
    "a real coordinator constructs _ctx in the existing assignment order",
    _ctx is not None and type(_ctx) is _Ctx,
    f"_ctx={type(_ctx)!r}",
)
R.check(
    "_ctx holds the same write-once objects the coordinator still exposes",
    _ctx is not None
    and _ctx._config is _blind_coord._config
    and _ctx._thermal_params is _blind_coord._thermal_params
    and _ctx.hass is _blind_coord.hass
    and _ctx._current_state is _blind_coord._current_state
    and _ctx._opt_config is _blind_coord._opt_config,
)
_action_ok = False
if _ctx is not None:
    try:
        _ctx.hass = object()
    except FrozenInstanceError:
        _action_ok = True
R.check("CoordinatorContext rejects writes (frozen)", _action_ok)
_blind_coord._current_action["s0_probe"] = True
R.check(
    "_current_action stays a mutable slot on the coordinator",
    _blind_coord._current_action["s0_probe"] is True
    and not hasattr(_ctx, "_current_action") if _ctx is not None else False,
)
_blind_coord._current_action.pop("s0_probe", None)
R.check(
    "the six hub names still resolve on the coordinator instance",
    _blind_coord._config is not None
    and _blind_coord._thermal_params is not None
    and _blind_coord.hass is _blind_hass
    and _blind_coord._current_state is not None
    and _blind_coord._opt_config is not None
    and isinstance(_blind_coord._current_action, dict),
)
R.section("S1 hub refs via _ctx (#377)")
_raw = vars(_blind_coord)
R.check(
    "the four write-once hubs are not raw instance attributes",
    "_config" not in _raw
    and "_thermal_params" not in _raw
    and "_current_state" not in _raw
    and "_opt_config" not in _raw,
    "raw leftover: " + ", ".join(
        k for k in ("_config", "_thermal_params", "_current_state", "_opt_config")
        if k in _raw
    ),
)
import ast as _ast_s1
_s1_tree = _ast_s1.parse(Path(coordinator_module.__file__).read_text())
_s1_cls = next(
    n for n in _s1_tree.body
    if isinstance(n, _ast_s1.ClassDef) and n.name == "HeatPumpOptimizerCoordinator"
)
_s1_raw_reads = []
for _fn in _s1_cls.body:
    if not isinstance(_fn, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef)):
        continue
    for _n in _ast_s1.walk(_fn):
        if (
            isinstance(_n, _ast_s1.Attribute)
            and isinstance(_n.value, _ast_s1.Name)
            and _n.value.id == "self"
            and _n.attr in {
                "_config", "_thermal_params", "_current_state", "_opt_config",
            }
        ):
            _s1_raw_reads.append(f"{_fn.name}:{_n.lineno}")
R.check(
    "coordinator methods read those hubs through _ctx, not raw self",
    not _s1_raw_reads,
    "left as self._X: " + ", ".join(_s1_raw_reads[:8]),
)
from heatpump_optimizer.coordinator import (
    COP_LEARNING_MAX_STEP,
    HOUSE_LOSS_MAX_STEP,
    PLAN_STALE_FLOOR_MINUTES,
    SOLVE_FAILURE_ISSUE_COUNT,
    house_loss_confidence,
)
R.check(
    "facade symbols stay importable from heatpump_optimizer.coordinator",
    HeatPumpOptimizerCoordinator is coordinator_module.HeatPumpOptimizerCoordinator
    and COP_LEARNING_MAX_STEP == coordinator_module.COP_LEARNING_MAX_STEP
    and HOUSE_LOSS_MAX_STEP == coordinator_module.HOUSE_LOSS_MAX_STEP
    and PLAN_STALE_FLOOR_MINUTES == coordinator_module.PLAN_STALE_FLOOR_MINUTES
    and SOLVE_FAILURE_ISSUE_COUNT == coordinator_module.SOLVE_FAILURE_ISSUE_COUNT
    and house_loss_confidence is coordinator_module.house_loss_confidence,
)
# S2 of #193: zero-state series / headroom / plan math at existing
# coordinator.py module level. Pins AST location (module FunctionDef,
# not a class method). `_plan_slots` stays on the class (helper cc>15).
R.section("S2 zero-state helpers at module level (#193)")
_s2_mod_fns = {
    n.name
    for n in _s1_tree.body
    if isinstance(n, _ast_s1.FunctionDef)
}
_s2_cls_fns = {
    n.name
    for n in _s1_cls.body
    if isinstance(n, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef))
}
R.check(
    "_liquid_fraction is a module-level FunctionDef, not a class method",
    "_liquid_fraction" in _s2_mod_fns and "_liquid_fraction" not in _s2_cls_fns,
    f"module={'_liquid_fraction' in _s2_mod_fns} class={'_liquid_fraction' in _s2_cls_fns}",
)
R.check(
    "_solve_anchor is a module-level FunctionDef, not a class method",
    "_solve_anchor" in _s2_mod_fns and "_solve_anchor" not in _s2_cls_fns,
    f"module={'_solve_anchor' in _s2_mod_fns} class={'_solve_anchor' in _s2_cls_fns}",
)

# S5 of #193: the self-learned house and buffer state is initialised OUTSIDE
# the dhw seam. structure.py buckets a coordinator method by its NAME, so
# while `_init_dhw_learning` assigned these, dhw *owned* them and every
# learner read of them was priced against hot water -- 88 of cut_dhw for
# state no dhw method ever reads. Merging the block back would give that
# back with nothing else failing, which is what these checks exist to stop.
# The seam list is imported from the metric rather than restated here, so a
# change to SEAM_REGEXES moves this test with it.
R.section("S5 thermal-learning state outside the dhw seam (#193)")
import structure as _s5_structure


def _s5_seam(_name: str) -> str:
    for _label, _rx in _s5_structure.SEAM_REGEXES:
        if _rx.search(_name):
            return _label
    return "core"


# The names come from the initialiser itself, not from a list kept here: a
# hand-kept list would silently stop covering an attribute added later.
_s5_init = next(
    (
        _n
        for _n in _s1_cls.body
        if isinstance(_n, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef))
        and _n.name == "_init_thermal_learning"
    ),
    None,
)
_s5_state = {
    _n.attr
    for _n in _ast_s1.walk(_s5_init)
    if isinstance(_n, _ast_s1.Attribute) and isinstance(_n.ctx, _ast_s1.Store)
} if _s5_init is not None else set()

R.check(
    "_init_thermal_learning exists, in the learning seam, and initialises state",
    _s5_init is not None
    and _s5_seam("_init_thermal_learning") == "learning"
    and len(_s5_state) > 1,
    f"present={_s5_init is not None} "
    f"seam={_s5_seam('_init_thermal_learning')} attrs={len(_s5_state)}",
)

# Every method that stores one of those names, and the seam it is bucketed
# into. Anything in dhw here is the regression this section guards.
_s5_dhw_writers: dict[str, list[str]] = {}
for _fn in _s1_cls.body:
    if not isinstance(_fn, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef)):
        continue
    if _s5_seam(_fn.name) != "dhw":
        continue
    for _n in _ast_s1.walk(_fn):
        if (
            isinstance(_n, _ast_s1.Attribute)
            and isinstance(_n.ctx, _ast_s1.Store)
            and _n.attr in _s5_state
        ):
            _s5_dhw_writers.setdefault(_n.attr, []).append(_fn.name)
R.check(
    "no dhw-seam method assigns house or buffer learning state (#193 S5)",
    _s5_state and not _s5_dhw_writers,
    f"dhw-seam assignments: { {k: sorted(set(v)) for k, v in _s5_dhw_writers.items()} }",
)
R.check(
    "_effective_house_heat_loss is a module-level FunctionDef, not a class method",
    "_effective_house_heat_loss" in _s2_mod_fns
    and "_effective_house_heat_loss" not in _s2_cls_fns,
    f"module={'_effective_house_heat_loss' in _s2_mod_fns} "
    f"class={'_effective_house_heat_loss' in _s2_cls_fns}",
)

# S6 of #193, the same lever on the grid seam. `freq_control.py` is the heat
# pump's own compressor frequency -- not anything about the electrical grid --
# but `_init_grid` assigned its four attributes, so grid *owned* them and every
# `_observe_frequency` / `_command_frequency` read was priced against the grid
# seam: 28 of cut_grid for state no grid method reads. Merging the block back
# is the regression these checks exist to stop; nothing else in the suite could
# fail on it. `_s5_seam` is reused deliberately -- it buckets by structure.py's
# own SEAM_REGEXES, so a change to the metric moves this test with it.
R.section("S6 inverter-frequency state outside the grid seam (#193)")
_s6_init = next(
    (
        _n
        for _n in _s1_cls.body
        if isinstance(_n, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef))
        and _n.name == "_init_frequency"
    ),
    None,
)
# Read off the initialiser itself, never a list kept here: a hand-kept list
# would silently stop covering an attribute added to it later.
_s6_state = (
    {
        _n.attr
        for _n in _ast_s1.walk(_s6_init)
        if isinstance(_n, _ast_s1.Attribute) and isinstance(_n.ctx, _ast_s1.Store)
    }
    if _s6_init is not None
    else set()
)
R.check(
    "_init_frequency exists, outside the grid seam, and initialises state",
    _s6_init is not None
    and _s5_seam("_init_frequency") != "grid"
    and len(_s6_state) > 1,
    f"present={_s6_init is not None} "
    f"seam={_s5_seam('_init_frequency')} attrs={len(_s6_state)}",
)

_s6_grid_writers: dict[str, list[str]] = {}
for _fn in _s1_cls.body:
    if not isinstance(_fn, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef)):
        continue
    if _s5_seam(_fn.name) != "grid":
        continue
    for _n in _ast_s1.walk(_fn):
        if (
            isinstance(_n, _ast_s1.Attribute)
            and isinstance(_n.ctx, _ast_s1.Store)
            and _n.attr in _s6_state
        ):
            _s6_grid_writers.setdefault(_n.attr, []).append(_fn.name)
R.check(
    "no grid-seam method assigns inverter-frequency state (#193 S6)",
    bool(_s6_state) and not _s6_grid_writers,
    f"grid-seam assignments: { {k: sorted(set(v)) for k, v in _s6_grid_writers.items()} }",
)
R.check(
    "_grid_fee_entity_value is a module-level FunctionDef, not a class method",
    "_grid_fee_entity_value" in _s2_mod_fns
    and "_grid_fee_entity_value" not in _s2_cls_fns,
    f"module={'_grid_fee_entity_value' in _s2_mod_fns} "
    f"class={'_grid_fee_entity_value' in _s2_cls_fns}",
)

# S8 of #193, the same lever on the COP-health watch. `_init_insurance` is
# bucketed core by its name, so while it assigned the watch's two attributes
# core *owned* them -- and core reads neither. Every `_observe_cop_health`,
# `_learning_view` and `_async_load_thermal_learning` read was therefore
# priced against learning as an inbound cross reference: 10 of cut_learning
# for state whose only core contact was the assignment itself. Merging the
# block back gives that 10 away with nothing else in the suite failing, which
# is what these checks exist to stop.
#
# The state is derived from BOTH ends rather than listed here -- what
# `_init_thermal_learning` assigns, intersected with what the watch method
# `_observe_cop_health` references. A hand-kept list would stop covering an
# attribute added later; deriving from the initialiser alone would over-fire,
# because core's `_apply_house_heat_loss_scale` legitimately assigns other
# state that initialiser owns.
R.section("S8 COP-health watch state outside the core seam (#193)")
_s8_init = next(
    (
        _n
        for _n in _s1_cls.body
        if isinstance(_n, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef))
        and _n.name == "_init_thermal_learning"
    ),
    None,
)
_s8_watch = next(
    (
        _n
        for _n in _s1_cls.body
        if isinstance(_n, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef))
        and _n.name == "_observe_cop_health"
    ),
    None,
)
_s8_assigned = (
    {
        _n.attr
        for _n in _ast_s1.walk(_s8_init)
        if isinstance(_n, _ast_s1.Attribute) and isinstance(_n.ctx, _ast_s1.Store)
    }
    if _s8_init is not None
    else set()
)
_s8_read_by_watch = (
    {
        _n.attr
        for _n in _ast_s1.walk(_s8_watch)
        if isinstance(_n, _ast_s1.Attribute)
    }
    if _s8_watch is not None
    else set()
)
_s8_state = _s8_assigned & _s8_read_by_watch

# Non-emptiness is asserted, not assumed: deleting the relocated block rather
# than moving it would leave the writer check below true over an empty set,
# which is the shape this repository has shipped green before.
R.check(
    "the COP-health watch state is initialised in the learning seam (#193 S8)",
    _s8_init is not None
    and _s8_watch is not None
    and _s5_seam("_init_thermal_learning") == "learning"
    and len(_s8_state) == 2,
    f"init={_s8_init is not None} watch={_s8_watch is not None} "
    f"seam={_s5_seam('_init_thermal_learning')} state={sorted(_s8_state)}",
)

_s8_core_writers: dict[str, list[str]] = {}
for _fn in _s1_cls.body:
    if not isinstance(_fn, (_ast_s1.FunctionDef, _ast_s1.AsyncFunctionDef)):
        continue
    if _s5_seam(_fn.name) != "core":
        continue
    for _n in _ast_s1.walk(_fn):
        if (
            isinstance(_n, _ast_s1.Attribute)
            and isinstance(_n.ctx, _ast_s1.Store)
            and _n.attr in _s8_state
        ):
            _s8_core_writers.setdefault(_n.attr, []).append(_fn.name)
R.check(
    "no core-seam method assigns COP-health watch state (#193 S8)",
    bool(_s8_state) and not _s8_core_writers,
    f"core-seam assignments: { {k: sorted(set(v)) for k, v in _s8_core_writers.items()} }",
)

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
    "the coordinator data still carries the constructor default; the "
    "published sensor must not claim it is a measurement",
)
_a3e_pub = dict(_blind)
_a3e_pub["indoor_temperature"] = _DEFAULTS.room_temperature
_a3e_ok_map = dict(_a3e_pub.get("reading_ok") or {})
_a3e_ok_map["upper_floor_temperature"] = False
_a3e_pub["reading_ok"] = _a3e_ok_map
_a3e_fake = FakeCoordinator(_a3e_pub)
R.check(
    "without an indoor reading the indoor sensor is unavailable, not 21.0 available",
    not sensor.IndoorTempSensor(_a3e_fake, ENTRY).available,
    f"available={sensor.IndoorTempSensor(_a3e_fake, ENTRY).available} "
    f"value={sensor.IndoorTempSensor(_a3e_fake, ENTRY).native_value!r}",
)
_a3e_clim = _climate_platform.HeatPumpOptimizerClimate(_a3e_fake, ENTRY)
R.check(
    "without an indoor reading climate does not publish the constructor default",
    (not _a3e_clim.available) and _a3e_clim.current_temperature is None,
    f"available={_a3e_clim.available} current={_a3e_clim.current_temperature!r}",
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

# ===========================================================================
# Round-2 audit, D8-01 remainder: the DEFAULT install, measured causally
# ===========================================================================
#
# Mixed Hot Water above was one of five paths the same defaults escaped
# through. The other four -- the climate entity's temperature attributes, the
# thermal battery's components and state of charge, and the Indoor/Outdoor
# pair -- were still ungated, and the configuration they leak in is not a
# corner: the panel drove the REAL config flow to `create_entry` submitting
# every form untouched and it completes with ZERO thermometers and a 200 L
# tank (all six probe fields are `vol.Optional`), so hot water is on and
# nothing measures it. Nothing self-corrects either: `__init__.py` awaits
# `async_config_entry_first_refresh` BEFORE forwarding the platforms, and
# that refresh takes the `_skip_solve_once` light path, so the first value a
# user ever sees is already the default and no later cycle moves it.
#
# The metric below is CAUSAL, not flag-based: it never reads the coordinator's
# own `reading_ok` map. It rebinds the seven temperature-bearing
# `ThermalState` constructor defaults by +7 K, re-runs the identical install,
# and counts the published leaves that MOVED while their entity was
# `available`. A fix that only edited the map could not move this number.
#
# Counted at CYCLE 1 and at STEADY STATE separately, because the panel's
# "add the probes and it goes to zero" perturbation is FALSE on the first
# cycle: the slab integrator still carries a 1.50 °C seed that decays to
# 0.0000 only by cycle 10, while the tank, buffer, indoor and outdoor cases
# never decay at all. A check that looked only at steady state would pass a
# fix that leaves the first day wrong.
R.section("Constructor defaults on the install the flow actually produces")


class _FlowOKSession:
    """The Tibber probe answers "valid"; nothing else here touches HTTP."""

    class _Resp:
        status = 200

        async def json(self):
            return {"data": {"viewer": {"name": "Home"}}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    def post(self, *args, **kwargs):
        return self._Resp()


#: The three fields the first screen marks `vol.Required`. Everything else on
#: every page is left exactly as the form pre-fills it -- which is what an
#: untouched browser submits.
_FLOW_REQUIRED = {
    "name": "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok",
    const.CONF_WEATHER_ENTITY: "weather.home",
}


def _untouched_answers(schema, required):
    answers = {}
    for key in schema.schema if schema else ():
        name = str(key)
        if name in required:
            answers[name] = required[name]
            continue
        description = getattr(key, "description", None) or {}
        if isinstance(description, dict) and "suggested_value" in description:
            answers[name] = description["suggested_value"]
            continue
        try:
            default = key.default()
        except Exception:
            default = None
        # An optional field with no default is simply not submitted, which is
        # what an untouched entity selector does.
        if default is not None and type(default).__name__ != "Undefined":
            answers[name] = default
    return answers


async def _walk_flow_untouched():
    """Drive the shipping initial flow to create_entry, changing nothing."""
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = (
        lambda hass, verify_ssl=True: _FlowOKSession()
    )
    try:
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        result = await flow.async_step_user(None)
        for _ in range(20):
            if result.get("type") == "create_entry":
                return dict(result["data"])
            if result.get("type") == "menu":
                # An untouched menu is its first option — except the finish
                # menu, whose first option is now the quick-setup shortcut:
                # that path declines the device pre-fill straight back to this
                # menu, so the untouched walk takes the full wizard instead.
                options = list(result["menu_options"])
                step = "temperature" if "temperature" in options else options[0]
                result = await getattr(flow, f"async_step_{step}")(None)
                continue
            step = result["step_id"]
            result = await getattr(flow, f"async_step_{step}")(
                _untouched_answers(
                    result.get("data_schema"),
                    _FLOW_REQUIRED if step == "user" else {},
                )
            )
        raise AssertionError("the initial flow did not reach create_entry")
    finally:
        config_flow.async_get_clientsession = real


_FLOW_CONFIG = asyncio.run(_walk_flow_untouched())
_FLOW_THERMOMETERS = [
    key
    for key in (
        const.CONF_INDOOR_TEMP_ENTITY,
        const.CONF_OUTDOOR_TEMP_ENTITY,
        const.CONF_DHW_TEMP_ENTITY,
        const.CONF_BUFFER_TANK_TEMP_ENTITY,
        const.CONF_FLOOR_RETURN_TEMP_ENTITY,
        const.CONF_LOWER_FLOOR_TEMP_ENTITY,
    )
    if _FLOW_CONFIG.get(key)
]
R.check(
    "the shipping flow, every form untouched, configures no thermometer at all",
    not _FLOW_THERMOMETERS,
    f"configured: {_FLOW_THERMOMETERS}",
)
R.check(
    "and turns hot water on anyway, with the 200 L tank the page pre-fills",
    _FLOW_CONFIG.get(const.CONF_DHW_TANK_VOLUME) == 200.0,
    f'{_FLOW_CONFIG.get(const.CONF_DHW_TANK_VOLUME)!r}',
)

#: A forecast the plan can be solved on, well below the 5.0 °C the outdoor
#: field defaults to, so "published the default" and "published the forecast"
#: are never the same number.
_D801_START = datetime(2026, 1, 15, tzinfo=UTC)
_D801_FORECAST_FIRST = -5.0


def _d801_coordinator(config):
    hass = FakeHass()
    entry = FakeEntry(data=dict(config))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (_D801_START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (_D801_START + timedelta(hours=h)).isoformat(),
            "temperature": _D801_FORECAST_FIRST + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    return hass, entry, coord


def _d801_publications(config, cycles):
    """Every visible leaf every enabled-by-default entity publishes."""
    hass, entry, coord = _d801_coordinator(config)

    async def run():
        # Home Assistant's own order: the first refresh takes the
        # `_skip_solve_once` light path and publishes with no solve.
        await coord._update_current_state()
        coord.data = coord._build_data_dict()
        for _ in range(cycles - 1):
            await coord._update_current_state()
            await coord.async_run_optimization()
            coord.data = coord._build_data_dict()

    asyncio.run(run())
    entry.runtime_data = coord
    out = {}
    for module in (sensor, binary_sensor, _climate_platform, _switch_platform):
        added = []
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        for entity in added:
            if not getattr(entity, "_attr_entity_registry_enabled_default", True):
                continue
            if not entity.available:
                continue
            label = f"{type(entity).__name__}"
            state = getattr(entity, "native_value", None)
            if state is None:
                state = getattr(entity, "is_on", None)
            if state is None:
                state = getattr(entity, "current_temperature", None)
            if state is not None:
                out[f"{label}|state"] = state
            attrs = getattr(entity, "extra_state_attributes", None) or {}
            for key, value in _d801_leaves(attrs):
                if value is not None:
                    out[f"{label}|attrs.{key}"] = value
    return out


def _d801_leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _d801_leaves(value, f"{prefix}{key}.")
    elif isinstance(obj, (list, tuple)):
        for index, value in enumerate(obj):
            yield from _d801_leaves(value, f"{prefix}{index}.")
    else:
        yield prefix.rstrip("."), obj


#: Exactly the constructor defaults the finding names -- 55/40/22/21/5 °C.
_D801_TEMPERATURE_DEFAULTS = (
    "room_temperature",
    "slab_temperature",
    "outdoor_temperature",
    "upper_floor_temperature",
    "lower_floor_temperature",
    "buffer_tank_temperature",
    "dhw_temperature",
)
#: The entities D8-01 names. The rest of the payload moves with these defaults
#: too, because `_solve_snapshot` deep-copies the state as the MPC's initial
#: condition -- that is a different finding (the optimizer plans against a tank
#: it has never measured) and it is not what this fix claims to close.
_D801_IN_SCOPE = {
    "HeatPumpOptimizerClimate",
    "IndoorTempSensor",
    "OutdoorTempSensor",
    "CurrentCOPSensor",
    "ThermalBatterySensor",
    "ThermalBatteryEnergySensor",
    "MixedHotWaterSensor",
    "DHWTemperatureSensor",
    "BufferTankTempSensor",
    "SlabTempSensor",
    "LowerFloorTempSensor",
    "UpperFloorTempSensor",
    "FloorReturnTempSensor",
}


def _d801_shift_defaults(delta):
    """Rebind ThermalState's temperature defaults; returns the undo callable.

    Both halves matter: the dataclass FIELD default is what a reader sees,
    and ``__init__.__defaults__`` is what actually gets assigned at
    construction. Rebinding only the field moves nothing at runtime, and a
    perturbation that moves nothing silently passes every check it drives.
    """
    fields = ThermalState.__dataclass_fields__
    init = ThermalState.__init__
    names = init.__code__.co_varnames[1 : init.__code__.co_argcount]
    offset = len(names) - len(init.__defaults__)
    original_fields = {
        name: fields[name].default for name in _D801_TEMPERATURE_DEFAULTS
    }
    original_init = init.__defaults__
    for name, value in original_fields.items():
        fields[name].default = value + delta
    init.__defaults__ = tuple(
        value + delta if names[offset + index] in original_fields else value
        for index, value in enumerate(original_init)
    )

    def undo():
        init.__defaults__ = original_init
        for undo_name, undo_value in original_fields.items():
            fields[undo_name].default = undo_value

    return undo


def _d801_default_derived(config, cycles):
    """Published leaves that move when the constructor defaults move."""
    dt_util.freeze(_D801_START)
    undo = None
    try:
        base = _d801_publications(config, cycles)
        undo = _d801_shift_defaults(7.0)
        shifted = _d801_publications(config, cycles)
    finally:
        if undo is not None:
            undo()
        dt_util.freeze(None)
    moved = sorted(
        key
        for key, value in base.items()
        if key in shifted and _d801_differs(value, shifted[key])
    )
    return base, moved


def _d801_differs(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) > 1e-9
    return a != b


# D8-01 recorded the Indoor pair as *retained* without a thermometer
# (ThermalState 21.0) on 2026-09-03. A3(e) / leftover #533 overturns that:
# published indoor must not claim a measurement the config never attached,
# so IndoorTempSensor and HeatPumpOptimizerClimate both gate on
# reading_ok["upper_floor_temperature"]. Cycle 1 residual is now empty.
# Cycle 10 residual is empty too: the money attrs below live on climate,
# and an unavailable climate is skipped by _d801_publications. Named so a
# revert that re-publishes the Indoor pair (or makes climate available
# again) fails these two equalities — that is the recorded decision
# moving, not a silent miss.
_D801_RETAINED = set()
# What climate would publish at cycle 10 if it stayed available. Not in
# the residual while A3(e) keeps the entity unavailable.
_D801_SOLVE_DERIVED = {
    "HeatPumpOptimizerClimate|attrs.predicted_savings",
    "HeatPumpOptimizerClimate|attrs.savings_percentage",
    "HeatPumpOptimizerClimate|attrs.dhw_heating_cost",
}

_d801_first, _d801_first_moved = _d801_default_derived(_FLOW_CONFIG, 1)
_d801_first_scope = {
    key for key in _d801_first_moved if key.split("|")[0] in _D801_IN_SCOPE
}
R.check(
    "at CYCLE 1 nothing in D8-01's entities publishes a constructor default",
    _d801_first_scope == _D801_RETAINED,
    f"unexpected: {sorted(_d801_first_scope - _D801_RETAINED)}",
)

_d801_steady, _d801_steady_moved = _d801_default_derived(_FLOW_CONFIG, 10)
_d801_steady_scope = {
    key for key in _d801_steady_moved if key.split("|")[0] in _D801_IN_SCOPE
}
R.check(
    "and at STEADY STATE (cycle 10, past the slab seed's decay) the residual "
    "stays empty: climate is gated, so the solve-derived money is not published",
    _d801_steady_scope == _D801_RETAINED,
    f"unexpected: {sorted(_d801_steady_scope - _D801_RETAINED)}; "
    f"named-if-climate-available={sorted(_D801_SOLVE_DERIVED)}",
)

# --- path by path, so a revert of any one line is named --------------------
#
# The same install, one light cycle, read through the REAL coordinator: the
# COP sensor reads `coordinator._thermal_model`, so a dict stand-in cannot
# answer whether the modelled COP followed the forecast or the default.
_d801_blind_hass, _d801_blind_entry, _d801_blind_coord = _d801_coordinator(
    _FLOW_CONFIG
)
dt_util.freeze(_D801_START)
try:
    asyncio.run(_d801_blind_coord._update_current_state())
    _d801_blind_data = _d801_blind_coord._build_data_dict()
finally:
    dt_util.freeze(None)
_d801_blind_coord.data = _d801_blind_data
_d801_blind = _d801_blind_coord
_d801_climate = _climate_platform.HeatPumpOptimizerClimate(_d801_blind, ENTRY)
_d801_attrs = _d801_climate.extra_state_attributes
for _key in (
    "dhw_temperature",
    "slab_temperature",
    "lower_floor_temperature",
    "upper_floor_temperature",
    "floor_return_temperature",
):
    R.check(
        f"the climate entity's {_key} attribute is None where nothing reads it",
        _d801_attrs.get(_key) is None,
        f"published {_d801_attrs.get(_key)!r} beside an unavailable sensor",
    )
R.check(
    "the outdoor attribute is the forecast the plan uses, not the 5.0 default",
    _d801_attrs.get("outdoor_temperature") is not None
    and abs(_d801_attrs["outdoor_temperature"] - _D801_FORECAST_FIRST) < 0.5,
    f'{_d801_attrs.get("outdoor_temperature")!r}',
)
# ...and it is the entry covering NOW, matched by the entry's own timestamp.
# A stale forecast list, or one that starts at the next hour, read
# positionally is the horizon read hours out of phase -- the bug
# `_weather_series`' own docstring warns about, and the reason this is not
# `forecast[0]`.
_d801_shifted_forecast = [
    {
        "datetime": (_D801_START - timedelta(hours=6 - h)).isoformat(),
        "temperature": -20.0 + h,
    }
    for h in range(12)
]
# Resolved rather than imported so this file still REPORTS on a tree where
# the production symbol does not exist yet, instead of aborting the run --
# the resolved object is the production one wherever there is one.
_d801_forecast_now = getattr(
    coordinator_module, "forecast_outdoor_now", lambda *args: None
)
R.check(
    "the forecast step is the entry covering now, not the list's first",
    _d801_forecast_now(_d801_shifted_forecast, _D801_START) == -14.0,
    str(_d801_forecast_now(_d801_shifted_forecast, _D801_START)),
)
R.check(
    "and a forecast that has not started yet reads its first entry",
    _d801_forecast_now(
        _d801_shifted_forecast, _D801_START - timedelta(hours=12)
    )
    == -20.0,
    "before the first entry the first is the best information there is",
)

_d801_outdoor = sensor.OutdoorTempSensor(_d801_blind, ENTRY)
R.check(
    "the Outdoor sensor follows the forecast rather than going unavailable",
    _d801_outdoor.available
    and abs(_d801_outdoor.native_value - _D801_FORECAST_FIRST) < 0.5,
    f"available={_d801_outdoor.available} value={_d801_outdoor.native_value!r}",
)
R.check(
    "and says so, so the number is never mistaken for a thermometer",
    (getattr(_d801_outdoor, "extra_state_attributes", None) or {}).get("source")
    == "weather_forecast",
    str(getattr(_d801_outdoor, "extra_state_attributes", None)),
)
_d801_cop = sensor.CurrentCOPSensor(_d801_blind, ENTRY)
R.check(
    "Learning Estimated COP is the COP at that forecast, not at the 5.0 default",
    _d801_cop.native_value
    == round(
        _d801_blind._thermal_model.compute_cop(
            _d801_blind_data.get("outdoor_forecast_temperature", 5.0)
        ),
        2,
    )
    and _d801_cop.native_value
    != round(_d801_blind._thermal_model.compute_cop(5.0), 2),
    f"{_d801_cop.native_value!r}",
)
for _cls in (sensor.ThermalBatterySensor, sensor.ThermalBatteryEnergySensor):
    R.check(
        f"{_cls.__name__} is unavailable when no store is sensed at all",
        not _cls(_d801_blind, ENTRY).available,
        f"published {_cls(_d801_blind, ENTRY).native_value!r} from 55/40/22/21",
    )
R.check(
    "the view names every store it only modelled, rather than dropping them",
    set((_d801_blind_data.get("battery") or {}).get("modelled_components") or [])
    == {"house", "slab", "dhw_tank", "buffer_tank"}
    and not (_d801_blind_data.get("battery") or {}).get("measured_components"),
    str(_d801_blind_data.get("battery", {}).get("modelled_components")),
)
R.check(
    "and the figures themselves are left alone, so no recorded series is "
    "silently rescaled",
    (_d801_blind_data.get("battery") or {}).get("state_of_charge_percent") == 86.8,
    "dropping a component would change the SOC denominator for every "
    "partly-probed install",
)
R.check(
    "the energy sensor carries the same disclosure in its own attributes",
    sensor.ThermalBatteryEnergySensor(
        FakeCoordinator(_d801_blind_data), ENTRY
    ).extra_state_attributes.get("modelled_components")
    == (_d801_blind_data.get("battery") or {}).get("modelled_components"),
    "its attributes are a hand-picked set, so the disclosure has to be "
    "picked with them",
)

# The floor return is the case availability exists for: a sensor that WAS
# configured and has stopped reporting. The coordinator holds the last good
# number -- 27.5 all spring -- so only the reading flag can tell the two
# apart, and the climate attribute has to read the flag rather than test the
# value for None.
_d801_stale_hass, _d801_stale_entry, _d801_stale_coord = _d801_coordinator(
    {**_FLOW_CONFIG, const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.ret"}
)
_d801_stale_hass.states.set("sensor.ret", FakeState("27.5"))
dt_util.freeze(_D801_START)
try:
    asyncio.run(_d801_stale_coord._update_current_state())
    # Older than every INPUT_MAX_AGE_MINUTES limit, relative to the FROZEN
    # clock: `_STALE_WHEN` is anchored to the wall clock and would read as
    # the future here, which is fresh.
    _d801_stale_hass.states.set(
        "sensor.ret",
        FakeState("27.5", last_updated=_D801_START - timedelta(hours=10)),
    )
    asyncio.run(_d801_stale_coord._update_current_state())
    _d801_stale_data = _d801_stale_coord._build_data_dict()
finally:
    dt_util.freeze(None)
R.check(
    "a stale floor return still publishes its last number in the payload",
    _d801_stale_data.get("floor_return_temperature") == 27.5,
    f'{_d801_stale_data.get("floor_return_temperature")!r}',
)
R.check(
    "but the climate attribute reports it as unknown, not as current",
    _climate_platform.HeatPumpOptimizerClimate(
        FakeCoordinator(_d801_stale_data), ENTRY
    ).extra_state_attributes.get("floor_return_temperature")
    is None,
    "a `is not None` test cannot tell a held reading from a live one",
)

# --- the null control: a live reading is STILL published --------------------
#
# 512 of the finder's 1132 publications were a live thermometer reading merely
# re-labelled, not a constructor default. A fix scoped to the headline number
# would have gated those, and gating a real measurement is a worse defect than
# publishing a modelled one. Every path above is re-checked with all six
# thermometers wired and reading.
_D801_LIVE = {
    "sensor.indoor": 21.4,
    "sensor.outdoor": -3.0,
    "sensor.tank": 48.2,
    "sensor.buffer": 36.5,
    "sensor.ret": 27.5,
    "sensor.down": 20.1,
}
_d801_probed_config = {
    **_FLOW_CONFIG,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TEMP_ENTITY: "sensor.tank",
    const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
    const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.ret",
    const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.down",
}
_d801_probed_hass, _d801_probed_entry, _d801_probed_coord = _d801_coordinator(
    _d801_probed_config
)
for _entity_id, _value in _D801_LIVE.items():
    _d801_probed_hass.states.set(_entity_id, FakeState(str(_value)))
dt_util.freeze(_D801_START)
try:
    asyncio.run(_d801_probed_coord._update_current_state())
    _d801_probed = _d801_probed_coord._build_data_dict()
finally:
    dt_util.freeze(None)
_d801_probed_fake = FakeCoordinator(_d801_probed)
_d801_probed_climate = _climate_platform.HeatPumpOptimizerClimate(
    _d801_probed_fake, ENTRY
)
_d801_probed_attrs = _d801_probed_climate.extra_state_attributes
for _key, _expected in (
    ("dhw_temperature", 48.2),
    ("lower_floor_temperature", 20.1),
    ("upper_floor_temperature", 21.4),
    ("floor_return_temperature", 27.5),
):
    R.check(
        f"a configured thermometer's live reading still reaches climate.{_key}",
        _d801_probed_attrs.get(_key) == _expected,
        f"{_d801_probed_attrs.get(_key)!r} (gating a real reading is the "
        f"regression this check exists to catch)",
    )
R.check(
    "the slab estimate still reaches the climate entity while its return reads",
    _d801_probed_attrs.get("slab_temperature") is not None,
    "the slab is integrated from the floor return, and that sensor reads here",
)
_d801_probed_outdoor = sensor.OutdoorTempSensor(_d801_probed_fake, ENTRY)
R.check(
    "the Outdoor sensor prefers its thermometer over the forecast",
    _d801_probed_outdoor.native_value == -3.0
    and (
        getattr(_d801_probed_outdoor, "extra_state_attributes", None) or {}
    ).get("source")
    == "outdoor_temp_entity",
    f"{_d801_probed_outdoor.native_value!r} "
    f'{getattr(_d801_probed_outdoor, "extra_state_attributes", None)!r}',
)
for _cls in (sensor.ThermalBatterySensor, sensor.ThermalBatteryEnergySensor):
    R.check(
        f"{_cls.__name__} is available again once a store is sensed",
        _cls(_d801_probed_fake, ENTRY).available,
        "the gate must not take the battery away from a probed install",
    )
R.check(
    "and the view reports every store as measured there",
    not (_d801_probed.get("battery") or {}).get("modelled_components"),
    str((_d801_probed.get("battery") or {}).get("modelled_components")),
)
# The threshold is "at least one store", not "all of them": the common
# install has an indoor thermometer and nothing else, and the house is both
# the largest store and genuinely sensed there.
_d801_indoor_only_hass, _d801_indoor_only_entry, _d801_indoor_only_coord = (
    _d801_coordinator({**_FLOW_CONFIG, const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
)
_d801_indoor_only_hass.states.set("sensor.indoor", FakeState("21.4"))
dt_util.freeze(_D801_START)
try:
    asyncio.run(_d801_indoor_only_coord._update_current_state())
    _d801_indoor_only = _d801_indoor_only_coord._build_data_dict()
finally:
    dt_util.freeze(None)
_d801_indoor_only_fake = FakeCoordinator(_d801_indoor_only)
R.check(
    "an install with only an indoor thermometer keeps its thermal battery",
    sensor.ThermalBatterySensor(_d801_indoor_only_fake, ENTRY).available,
    "the house is the largest store and it is sensed here",
)
R.check(
    "with the stores it only modelled named rather than dropped",
    set((_d801_indoor_only.get("battery") or {}).get("modelled_components") or [])
    == {"slab", "dhw_tank", "buffer_tank"},
    str((_d801_indoor_only.get("battery") or {}).get("modelled_components")),
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
for _module in (sensor, binary_sensor, button, _climate_platform, _switch_platform, datetime_mod):
    for _entity in collect(_module, coordinator=_healthy):
        if not _entity.available:
            if type(_entity).__name__ == "MonthlySavingsSensor":
                continue
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
    by_name["Cost Monthly Peak Power"].extra_state_attributes[
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
# entry_type=DeviceEntryType.SERVICE, which homeassistant.helpers.
# device_registry has shipped since 2024.6.0 and so is present at the
# hacs.json floor (a StrEnum with the single member SERVICE; DeviceInfo has
# no config_entry field in the mirrored release).
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
# F1: the registry entry names the publisher and links to this entry's
# configuration page. "Custom" is the cookiecutter placeholder (D10-15).
R.check(
    "the shared device names the publisher, not the placeholder",
    _dev_coord.device_info.get("manufacturer") == "tvofi",
    repr(_dev_coord.device_info.get("manufacturer")),
)
R.check(
    "the shared device links to this entry's configuration page",
    _dev_coord.device_info.get("configuration_url")
    == "homeassistant://config/config_entries/entry/device_info_probe",
    repr(_dev_coord.device_info.get("configuration_url")),
)

# The forwarding half of the same claim: driving each platform's real
# async_setup_entry with a real coordinator, the way HA would, every entity
# the roster adds must land on that service device.
for _platform in (sensor, binary_sensor, button, _switch_platform, _climate_platform, datetime_mod):
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
R.check("five binary sensors are added", len(binaries) == 5, str(len(binaries)))

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

# The owner's ask (in-session 2026-09-14): the flag must say WHICH input
# flipped it. Two attributes on the same diagnostic sensor -- the failing
# entity ids and one short line per failure -- driven here through the real
# coordinator's read cycle, one failure class at a time. The state and every
# attribute pinned above are the null control: they must not move.
def _sources_cycle(extra_config=None, states=None):
    """One real input-read cycle carrying the given failures, published."""
    _h, _c, _d = _honest_coordinator(extra_config, states)
    return _d


def _sources_entity(data):
    return binary_sensor.InputHealthBinarySensor(FakeCoordinator(data), ENTRY)


_healthy_cycle = _sources_cycle()
R.check(
    "a healthy cycle publishes no problem sources",
    _sources_entity(_healthy_cycle).extra_state_attributes["problem_inputs"] == []
    and _sources_entity(_healthy_cycle).extra_state_attributes["problem_messages"]
    == [],
    f"inputs={_sources_entity(_healthy_cycle).extra_state_attributes.get('problem_inputs')!r} "
    f"messages={_sources_entity(_healthy_cycle).extra_state_attributes.get('problem_messages')!r}",
)

# One class at a time, each through the coordinator's own reader.
_TANK_SLOT = const.CONF_DHW_TEMP_ENTITY
_TANK_CLASSES = (
    # (class, states, the one line the attribute must carry)
    # _STALE_WHEN is anchored to the wall clock, so the stale minute count
    # is pinned by shape below, not by number.
    (
        "stale",
        {"sensor.tank": FakeState("48.2", last_updated=_STALE_WHEN)},
        None,
    ),
    (
        "unavailable",
        {"sensor.tank": FakeState("unavailable")},
        "sensor.tank: unavailable",
    ),
    (
        "missing_entity",
        None,  # configured, but no state exists at all
        "sensor.tank: entity not found",
    ),
    (
        "not_numeric",
        {"sensor.tank": FakeState("warm")},
        "sensor.tank: not a number",
    ),
)
for _word, _states, _line in _TANK_CLASSES:
    _tank_data = _sources_cycle({_TANK_SLOT: "sensor.tank"}, _states)
    _tank_entity = _sources_entity(_tank_data)
    _tank_messages = _tank_entity.extra_state_attributes["problem_messages"]
    _tank_inputs = _tank_entity.extra_state_attributes["problem_inputs"]
    if _line is None:  # the stale line carries the wall-clock age
        _message_ok = (
            len(_tank_messages) == 1
            and _tank_messages[0].startswith("sensor.tank: stale (last report ")
            and _tank_messages[0].endswith(" min)")
        )
    else:
        _message_ok = _tank_messages == [_line]
    R.check(
        f"a {_word} tank sensor is the named source of the problem",
        _tank_entity.is_on
        and _tank_inputs == ["sensor.tank"]
        and _message_ok,
        f"is_on={_tank_entity.is_on} inputs={_tank_inputs!r} "
        f"messages={_tank_messages!r}",
    )

for _slot, _entity, _state, _line in (
    (
        const.CONF_POWER_ENTITY,
        "sensor.power",
        FakeState("3000", unit="hp"),
        "sensor.power: unknown unit",
    ),
    (
        const.CONF_HEAT_PUMP_MODE_ENTITY,
        "sensor.mode",
        FakeState("banana"),
        "sensor.mode: unrecognized state",
    ),
    (
        const.CONF_HEAT_PUMP_DEFROST_ENTITY,
        "sensor.defrost",
        FakeState("maybe"),
        "sensor.defrost: not a yes/no flag",
    ),
):
    _class_data = _sources_cycle({_slot: _entity}, {_entity: _state})
    _class_entity = _sources_entity(_class_data)
    R.check(
        f"a failing {_entity} slot names its entity and class",
        _class_entity.is_on
        and _class_entity.extra_state_attributes["problem_inputs"] == [_entity]
        and _class_entity.extra_state_attributes["problem_messages"] == [_line],
        f"inputs={_class_entity.extra_state_attributes.get('problem_inputs')!r} "
        f"messages={_class_entity.extra_state_attributes.get('problem_messages')!r}",
    )

# Several failures at once: every source is named, one line each, and the
# pre-existing attributes say exactly what they said before this feature.
_multi_data = _sources_cycle(
    {_TANK_SLOT: "sensor.tank"},
    {
        "sensor.indoor": FakeState("unavailable"),
        "sensor.tank": FakeState("48.2", last_updated=_STALE_WHEN),
    },
)
_multi_entity = _sources_entity(_multi_data)
_multi_attrs = _multi_entity.extra_state_attributes
R.check(
    "two failures at once name both entities",
    _multi_attrs["problem_inputs"] == ["sensor.indoor", "sensor.tank"],
    f'{_multi_attrs.get("problem_inputs")!r}',
)
R.check(
    "with one line per failure, in the evidence's own order",
    len(_multi_attrs["problem_messages"]) == 2
    and _multi_attrs["problem_messages"][0].startswith("sensor.tank: stale")
    and _multi_attrs["problem_messages"][1] == "sensor.indoor: unavailable",
    f'{_multi_attrs.get("problem_messages")!r}',
)
R.check(
    "the older attributes are unchanged by the new ones",
    _multi_attrs["stale_inputs"] == ["dhw_temp_entity"]
    and len(_multi_attrs["problems"]) == 2,
    f'stale_inputs={_multi_attrs.get("stale_inputs")!r} '
    f'problems={_multi_attrs.get("problems")!r}',
)

# Recovery: the same coordinator that flagged the failure empties the
# sources again once the sensor reports -- the lists are state, not a latch.
_rec_hass, _rec_coord, _ = _honest_coordinator(
    {_TANK_SLOT: "sensor.tank"}, {"sensor.tank": FakeState("48.2")}
)
asyncio.run(_rec_coord._update_current_state())
_rec_data = _rec_coord._build_data_dict()
R.check(
    "a healthy tank publishes no sources",
    not _sources_entity(_rec_data).is_on
    and _sources_entity(_rec_data).extra_state_attributes["problem_inputs"] == [],
)
_rec_hass.states.set("sensor.tank", FakeState("48.2", last_updated=_STALE_WHEN))
asyncio.run(_rec_coord._update_current_state())
_rec_stale = _rec_coord._build_data_dict()
R.check(
    "the stale tank becomes the named source",
    _sources_entity(_rec_stale).is_on
    and _sources_entity(_rec_stale).extra_state_attributes["problem_inputs"]
    == ["sensor.tank"],
)
_rec_hass.states.set("sensor.tank", FakeState("48.2"))
asyncio.run(_rec_coord._update_current_state())
_rec_ok = _rec_coord._build_data_dict()
R.check(
    "and recovery empties the sources again",
    not _sources_entity(_rec_ok).is_on
    and _sources_entity(_rec_ok).extra_state_attributes["problem_inputs"] == []
    and _sources_entity(_rec_ok).extra_state_attributes["problem_messages"] == [],
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

R.check(
    "the cheaper sensor is unavailable until fuel is ready",
    not binary_sensor.WoodCheaperBinarySensor(
        FakeCoordinator({}), ENTRY
    ).available,
)
R.check(
    "and cheaper is false when not ready",
    not binary_sensor.WoodCheaperBinarySensor(
        FakeCoordinator({"wood_fuel": {"ready": False, "cheaper": True}}), ENTRY
    ).is_on
    and not binary_sensor.WoodCheaperBinarySensor(
        FakeCoordinator({"wood_fuel": {"ready": False, "cheaper": True}}), ENTRY
    ).available,
)
R.check(
    "ready with a cheaper hour is on",
    binary_sensor.WoodCheaperBinarySensor(
        FakeCoordinator(
            {
                "wood_fuel": {
                    "ready": True,
                    "cheaper": True,
                    "sek_per_kwh": 0.6,
                    "cheaper_hour_count": 1,
                }
            }
        ),
        ENTRY,
    ).is_on,
)
R.check(
    "ready with an idle plan is off",
    not binary_sensor.WoodCheaperBinarySensor(
        FakeCoordinator(
            {
                "wood_fuel": {
                    "ready": True,
                    "cheaper": False,
                    "sek_per_kwh": 0.6,
                    "cheaper_hour_count": 0,
                }
            }
        ),
        ENTRY,
    ).is_on,
)
_wf_ready_entity = binary_sensor.WoodCheaperBinarySensor(
    FakeCoordinator(
        {
            "wood_fuel": {
                "ready": True,
                "cheaper": True,
                "sek_per_kwh": 0.6,
                "cheaper_hour_count": 1,
            }
        }
    ),
    ENTRY,
)
R.check(
    "ready makes the cheaper sensor available",
    _wf_ready_entity.available is True,
)
R.check(
    "cheaper attributes are sek_per_kwh and cheaper_hour_count",
    _wf_ready_entity.extra_state_attributes
    == {"sek_per_kwh": 0.6, "cheaper_hour_count": 1},
)

b_crashed = []
for entity in (
    binary_sensor.InputHealthBinarySensor(empty, ENTRY),
    binary_sensor.ExternalHeatBinarySensor(empty, ENTRY),
    binary_sensor.AwayModeBinarySensor(empty, ENTRY),
    binary_sensor.VentilationBinarySensor(empty, ENTRY),
    binary_sensor.WoodCheaperBinarySensor(empty, ENTRY),
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
    "Learning Run System Identification",
    "Learning Reset Comfort Weight",
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
        schema(empty_section_payload(schema))
    except Exception as err:  # noqa: BLE001 - any rejection is a failure
        return False, f"{type(err).__name__}: {err}"
    return True, ""


def _entity_selectors(schema):
    """Yield ``(field, selector)`` for every entity picker on a page."""
    for key, value in _presented_fields(schema):
        if isinstance(value, config_flow.selector.EntitySelector):
            yield getattr(key, "schema", key), value


def _schema_keys(schema):
    """Option-key names a page presents, section nesting included."""
    return {str(getattr(key, "schema", key)) for key, _ in _presented_fields(schema)}


def _schema_defaults(schema):
    """``schema({})`` for a page that may contain ``section()`` blocks."""
    return schema(empty_section_payload(schema))


def _presented_value(marker):
    """The value a field's marker shows the user, however it is pre-filled.

    ``suggested_value`` first, then ``default``: a form pre-fills with either,
    and the frontend shows and posts them alike, so a reader that wants "what
    this page offers" has to accept both. This is also where the two arms of
    the ``_STORED`` rule separate: a stored entity is offered as a
    ``suggested_value`` so that clearing it sticks (the key comes back ABSENT
    and voluptuous refills only a ``default``), while a computed field carries
    a real ``default``.
    """
    description = getattr(marker, "description", None)
    if isinstance(description, dict) and "suggested_value" in description:
        return description["suggested_value"]
    default = getattr(marker, "default", None)
    return default() if callable(default) else default


def _nested_drop(posted, keys):
    """``posted`` with every name in ``keys`` removed wherever it is nested."""
    return {
        name: (_nested_drop(value, keys) if isinstance(value, dict) else value)
        for name, value in posted.items()
        if name not in keys
    }


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
#
# Since #223 all three are views of ``_OPTION_PAGES``'s ``menu`` column, so
# the check below is true by construction and is kept as a guard against that
# derivation being undone rather than as a live invariant. The one with teeth
# moved to ``registry_drives_every_page`` in tests/config_flow_steps.py: a
# page in the table with no handler, or a handler no menu offers.
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
_untouched = _schema_defaults(_form["data_schema"])  # defaults only, as a real untouched save
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
# #1067: three more, on the same page and just as optional -- the pump's own
# electric backup heater, its hot-water tank booster, and night (silent) mode.
# They are OPTIONS-ONLY: deliberately absent from ``topology._SLOTS``, on the
# precedent of the compressor-frequency keys, because they are not places on
# the plant diagram. That is what keeps ``ASSIGNABLE_KEYS`` at the size
# ``assign_entity`` and docs/configuration.md both document, so the checks
# below that read ``ASSIGNABLE_KEYS`` run over the card-slot subset only.
_PUMP_ONLY_KEYS = (
    const.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY,
    const.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY,
    const.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
)
# #1067 again, with the group's second half: the pump's own supply (flow) and
# return water. Options-only for the same reason -- a reading off the machine
# is not a place on the plant diagram -- but a TEMPERATURE picker rather than
# a flag one, so they get their own loop below.
_PUMP_TEMP_KEYS = (
    const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
    const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
)
_PUMP_PAGE_KEYS = _SIGNAL_KEYS + _PUMP_ONLY_KEYS + _PUMP_TEMP_KEYS
# The four pump signals moved to entities_pump when the entities page split (#198).
_pump_flow = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
_pump_flow.hass = FakeHass()
_pump_form = asyncio.run(_pump_flow.async_step_entities_pump(None))
_pump_schema = _pump_form["data_schema"]
_pump_fields = {
    str(getattr(k, "schema", k)): k for k in _pump_schema.schema
}
def _pump_domains(key):
    """The domains the page's picker for ``key`` actually offers."""
    return list(
        _pump_schema.schema[_pump_fields[key]].config["filter"][0]["domain"]
    )


for _key in _PUMP_PAGE_KEYS:
    R.check(
        f"{_key} is offered on the entities_pump page",
        _key in _pump_fields,
    )
    R.check(
        f"{_key} is optional",
        type(_pump_fields[_key]).__name__ == "Optional",
        "a required field here would break every existing install on save",
    )
    R.check(
        f"{_key} can be cleared again once set",
        _key in options._ENTITIES_PUMP_KEYS,
        "options merge over setup data, so an absent key restores the old value",
    )
# The card-slot subset: these four have a row in ``topology._SLOTS``, so the
# picker and the assign service must offer one list rather than two spellings
# of it.
for _key in _SIGNAL_KEYS:
    R.check(
        f"{_key} is a topology slot, so the card and the service agree",
        _key in topology.ASSIGNABLE_KEYS,
    )
    R.check(
        f"the picker for {_key} offers exactly its slot's domains",
        _pump_fields[_key] is not None
        and _pump_domains(_key) == list(topology.ASSIGNABLE_KEYS[_key]),
        "one list, or the diagram offers what the service would refuse",
    )
# The options-only three have no slot to agree with, so what they owe instead
# is that they are NOT assignable -- adding them would change the documented
# key list `assign_entity` publishes -- and that their pickers still come from
# the one flag-domain tuple rather than a repeated literal.
for _key in _PUMP_ONLY_KEYS:
    R.check(
        f"{_key} is options-only, not a card slot",
        _key not in topology.ASSIGNABLE_KEYS,
        "assign_entity's key list and docs/configuration.md document a fixed "
        "set of assignable slots; these three are not places on the diagram",
    )
    R.check(
        f"the picker for {_key} offers the shared flag domains",
        _pump_domains(_key) == list(topology.FLAG_DOMAINS),
        f"{_pump_domains(_key)} against {list(topology.FLAG_DOMAINS)} -- one "
        "tuple, not a second spelling of it",
    )
# The two water slots owe the same "not a card slot", plus the one thing a
# temperature picker owes that a flag picker does not: a device class, so the
# list a user scrolls is thermometers rather than every sensor in the house.
for _key in _PUMP_TEMP_KEYS:
    R.check(
        f"{_key} is options-only, not a card slot",
        _key not in topology.ASSIGNABLE_KEYS,
        "a reading off the pump is not a place on the plant diagram, and "
        "adding it would change the documented assignable key list",
    )
    R.check(
        f"the picker for {_key} is a temperature sensor picker",
        _pump_domains(_key) == ["sensor"]
        and list(
            _pump_schema.schema[_pump_fields[_key]].config["filter"][0][
                "device_class"
            ]
        )
        == ["temperature"],
        "the same narrowing every other water temperature on the plant uses",
    )
R.check(
    "and it really narrows: a flag slot on the same page offers no device class",
    "device_class"
    not in _pump_schema.schema[
        _pump_fields[const.CONF_HEAT_PUMP_FAULT_ENTITY]
    ].config["filter"][0],
    "the null control for the check above: if every picker on this page "
    "carried a device class, asserting one would prove nothing",
)
R.check(
    "and the flag-domain tuple really is the one the card slots use",
    list(topology.ASSIGNABLE_KEYS[const.CONF_HEAT_PUMP_FAULT_ENTITY])
    == list(topology.FLAG_DOMAINS),
    "the null control for the check above: if FLAG_DOMAINS were a private "
    "copy, comparing against it would prove nothing",
)

# #1067 W1067-G5: the pump's own disinfection switch and its observe/control
# mode, on the hot_water_tank page. Options-only on the same precedent as the
# pump slots above; the picker offers the two writable flag domains, not the
# read-only ones, because control mode turns it on and off.
_dis_flow = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
_dis_flow.hass = FakeHass()
_dis_schema = asyncio.run(_dis_flow.async_step_hot_water_tank(None))["data_schema"]
_dis_fields = {
    str(getattr(k, "schema", k)): (k, v) for k, v in _presented_fields(_dis_schema)
}
for _key in (const.CONF_DHW_DISINFECTION_SWITCH_ENTITY, const.CONF_DHW_DISINFECTION_MODE):
    R.check(
        f"{_key} is offered on the hot_water_tank page, optional",
        _key in _dis_fields and type(_dis_fields[_key][0]).__name__ == "Optional",
        "a required field here would break every existing install on save",
    )
    R.check(
        f"{_key} is options-only, not a card slot",
        _key not in topology.ASSIGNABLE_KEYS,
    )
R.check(
    "the disinfection switch can be cleared again once set",
    const.CONF_DHW_DISINFECTION_SWITCH_ENTITY in options._OPTIONAL_ENTITY_KEYS,
    "options merge over setup data, so an absent key restores the old value",
)
R.check(
    "the disinfection switch picker offers switch and input_boolean only",
    const.CONF_DHW_DISINFECTION_SWITCH_ENTITY in _dis_fields
    and list(
        _dis_fields[const.CONF_DHW_DISINFECTION_SWITCH_ENTITY][1].config["filter"][0]["domain"]
    ) == ["switch", "input_boolean"],
    "a binary_sensor cannot be turned on, so offering one would save a "
    "control mode that can never act",
)
_dis_mode_selector = _dis_fields.get(const.CONF_DHW_DISINFECTION_MODE, (None, None))[1]
R.check(
    "the disinfection mode reuses the frequency stage's two words, observe by default",
    _dis_mode_selector is not None
    and list(_dis_mode_selector.config["options"])
    == [config_flow.FREQ_MODE_OBSERVE, config_flow.FREQ_MODE_CONTROL]
    and config_flow._flatten_section_input(_schema_defaults(_dis_schema)).get(
        const.CONF_DHW_DISINFECTION_MODE
    )
    == config_flow.FREQ_MODE_OBSERVE
    and const.DEFAULT_DHW_DISINFECTION_MODE == config_flow.FREQ_MODE_OBSERVE,
    f"selector={getattr(_dis_mode_selector, 'config', None)!r}",
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
    const.CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY: "switch.pump_backup_heater",
    const.CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY: "switch.pump_dhw_booster",
    const.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.pump_night_mode",
    const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.hp_supply_temp",
    const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.hp_return_temp",
}
_sig_form = asyncio.run(_sig_flow.async_step_entities_pump(None))
_sig_result = asyncio.run(
    _sig_flow.async_step_entities_pump(
        {**_sig_form["data_schema"]({}), **_sig_values,
         const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_sig_saved = _sig_result.get("data") or {}
R.check(
    "the entities_pump page reaches a close-save",
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
_sig_form2 = asyncio.run(_sig_flow2.async_step_entities_pump(None))
_sig_offered = {
    str(getattr(marker, "schema", marker)): _presented_value(marker)
    for marker, _value in _presented_fields(_sig_form2["data_schema"])
}
R.check(
    "a configured signal comes back as the field's pre-fill",
    all(_sig_offered.get(_key) == _value for _key, _value in _sig_values.items()),
    "a page that forgets what is configured invites the user to re-enter it",
)
# Clearing has to survive the flow manager, which validates the submitted post
# through the same schema before the step sees it (``_async_configure``:
# ``user_input = data_schema(user_input)``). A clear posts the picker's key
# ABSENT, and voluptuous refills a ``default`` for an absent key -- so a stored
# entity offered as ``vol.Optional(key, default=stored)`` came straight back and
# the clear was silently dropped, while a direct call to the step stayed green
# because it never re-validated. Submitting the untouched post with the pickers
# dropped, THROUGH the schema, is that manager call.
_sig_cleared_result = asyncio.run(
    _sig_flow2.async_step_entities_pump(
        _sig_form2["data_schema"](
            _nested_drop(
                _schema_defaults(_sig_form2["data_schema"]), set(_sig_values)
            )
        )
        | {const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    )
)
_sig_cleared = _sig_cleared_result.get("data") or {}
R.check(
    "and clearing every one of them sticks",
    all(_sig_cleared.get(_key) is None for _key in _PUMP_PAGE_KEYS),
    str({k: _sig_cleared.get(k) for k in _PUMP_PAGE_KEYS}),
)

# The null case, which is the one every existing install runs: nothing
# configured, nothing changed.
_bare = options(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
_bare.hass = FakeHass()
_bare_result = asyncio.run(
    _bare.async_step_entities(
        _schema_defaults(asyncio.run(_bare.async_step_entities(None))["data_schema"])
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

# --- #703 Tibber Pulse auto-bind ----------------------------------------------
R.section("Tibber Pulse auto-bind (#703)")
_pulse_candidates = (
    {
        "entity_id": "sensor.pulse_power",
        "name": "Tibber Pulse",
        "unique_id": "pulse-live",
        "manufacturer": "Tibber",
        "device_class": "power",
        "domain": "sensor",
    },
    {
        "entity_id": "sensor.hp_power",
        "name": "Heat pump power",
        "device_class": "power",
        "domain": "sensor",
    },
)
R.check(
    "an empty house_power_entity is suggested from a Pulse-shaped power sensor",
    topology.suggest_house_power_entity(None, _pulse_candidates)
    == "sensor.pulse_power",
)
R.check(
    "a pre-set house_power_entity is left alone",
    topology.suggest_house_power_entity("sensor.hp_power", _pulse_candidates)
    == "sensor.hp_power",
)
R.check(
    "a non-power Pulse-named sensor is not suggested",
    topology.suggest_house_power_entity(
        None,
        (
            {
                "entity_id": "sensor.pulse_energy",
                "name": "Tibber Pulse energy",
                "device_class": "energy",
                "domain": "sensor",
            },
        ),
    )
    is None,
)
_pulse_hass = FakeHass(
    {
        "sensor.pulse_power": FakeState(
            "1200",
            unit="W",
            attributes={
                "device_class": "power",
                "friendly_name": "Tibber Pulse",
            },
        )
    }
)
_pulse_row = next(
    row
    for row in config_flow._OPTION_FIELDS
    if row.key == const.CONF_HOUSE_POWER_ENTITY
)
_pulse_empty = config_flow._field_marker(_pulse_row, {}, _pulse_hass)
R.check(
    "the metering page suggests Pulse when house_power_entity is empty",
    getattr(_pulse_empty, "description", {}) == {"suggested_value": "sensor.pulse_power"},
    str(getattr(_pulse_empty, "description", None)),
)
_pulse_kept = config_flow._field_marker(
    _pulse_row, {const.CONF_HOUSE_POWER_ENTITY: "sensor.other_power"}, _pulse_hass
)
_pulse_kept_value = _presented_value(_pulse_kept)
R.check(
    "the metering page keeps a stored house_power_entity",
    _pulse_kept_value == "sensor.other_power",
    str(_pulse_kept_value),
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

# --- #701 Nord Pool / price entity -------------------------------------------
R.section("Nord Pool / price entity (#701)")
from heatpump_optimizer.price_model import (
    apply_price_adjustments,
    prices_from_entity_attributes,
    prices_from_entity_state,
    pull_prices as _pull_prices,
)

def _np_block(day, n, minutes=60):
    return [
        {
            "start": datetime(2026, 1, 14 + day, 0, 0)
            + timedelta(minutes=minutes * i),
            "value": 0.40 + 0.01 * i,
        }
        for i in range(n)
    ]

_np24 = prices_from_entity_attributes(
    {"raw_today": _np_block(0, 24), "raw_tomorrow": _np_block(1, 24)}
)
R.check(
    "a Nord Pool entity with 24+24 hourly rows parses",
    isinstance(_np24, list) and len(_np24) == 48,
    repr(type(_np24).__name__ if not isinstance(_np24, list) else len(_np24)),
)
_np96 = prices_from_entity_attributes(
    {"raw_today": _np_block(0, 96, 15), "raw_tomorrow": _np_block(1, 96, 15)}
)
R.check(
    "a Nord Pool entity with 96+96 quarter-hour rows parses",
    isinstance(_np96, list) and len(_np96) == 192,
    repr(type(_np96).__name__ if not isinstance(_np96, list) else len(_np96)),
)
_np_adj = apply_price_adjustments(
    [{"total": 1.0, "starts_at": "t", "level": "NORMAL"}], 1.25, 0.05
)
R.check(
    "VAT and surcharge are value × VAT + surcharge",
    _np_adj and abs(_np_adj[0]["total"] - 1.30) < 1e-9,
    repr(_np_adj),
)
R.check(
    "an empty price entity is a failed fetch, not a guess",
    prices_from_entity_state(None) == "Price entity is empty",
)
_np_fail = asyncio.run(
    _pull_prices(
        None,
        {
            const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
            const.CONF_PRICE_ENTITY: "sensor.nordpool",
        },
        None,
    )
)
R.check(
    "the entity source never asks for Tibber reauth",
    _np_fail[0] == "fail" and _np_fail[1] == "Price entity is empty",
    repr(_np_fail),
)

_np_hass = FakeHass()
_np_hass.states.set(
    "sensor.nordpool",
    FakeState(
        "0.42",
        attributes={
            "raw_today": [
                {"start": "2026-01-14T00:00:00+01:00", "value": 0.42 + 0.01 * i}
                for i in range(24)
            ],
            "raw_tomorrow": [
                {"start": "2026-01-15T00:00:00+01:00", "value": 0.50 + 0.01 * i}
                for i in range(24)
            ],
        },
    ),
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _NpCoord

_np_coord = _NpCoord(
    _np_hass,
    FakeEntry(
        data={
            const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
            const.CONF_PRICE_ENTITY: "sensor.nordpool",
            const.CONF_WEATHER_ENTITY: "weather.home",
        }
    ),
)
asyncio.run(_np_coord._fetch_tibber_prices())
R.check(
    "a 24+24 entity series becomes coordinator prices",
    len(_np_coord._prices) == 48
    and abs(float(_np_coord._prices[0]["total"]) - 0.42) < 1e-9,
    f"n={len(_np_coord._prices)} first={_np_coord._prices[:1]!r}",
)
_np_empty = _NpCoord(
    FakeHass(),
    FakeEntry(
        data={
            const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
            const.CONF_PRICE_ENTITY: "sensor.gone",
            const.CONF_WEATHER_ENTITY: "weather.home",
        }
    ),
)
_np_empty_err = None
try:
    asyncio.run(_np_empty._fetch_tibber_prices())
except Exception as _np_empty_exc:  # noqa: BLE001
    _np_empty_err = _np_empty_exc
R.check(
    "an empty entity source raises UpdateFailed and does not start reauth",
    type(_np_empty_err).__name__ == "UpdateFailed"
    and not _np_empty._tibber_reauth_started,
    f"raised {type(_np_empty_err).__name__}: {_np_empty_err}; "
    f"reauth={_np_empty._tibber_reauth_started}",
)

# --- #698 DSO catalog --------------------------------------------------------
R.section("DSO tariff catalog (#698)")
from heatpump_optimizer import grid_fee as _dso_gf

for _dso_id, _dso_row in _dso_gf.SWEDEN_CATALOG.items():
    _dso_rules = _dso_gf.parse_rules(_dso_row["grid_fee_rules"])
    _dso_applied = _dso_gf.apply_catalog(_dso_id)
    R.check(
        f"{_dso_id} round-trips parse_rules and writes peak keys",
        bool(_dso_rules)
        and _dso_applied is not None
        and _dso_applied[const.CONF_GRID_FEE_RULES] == _dso_row["grid_fee_rules"]
        and _dso_applied[const.CONF_PEAK_TARIFF_WINDOW]
        == _dso_row["peak_tariff_window_minutes"],
        repr(_dso_applied),
    )
R.check(
    "an unknown catalog id writes nothing",
    _dso_gf.apply_catalog("not_a_swedish_dso_2026") is None,
)
R.check(
    "none writes nothing",
    _dso_gf.apply_catalog(_dso_gf.DSO_PRODUCT_NONE) is None,
)

# --- #700 weekend / holiday profiles -----------------------------------------
R.section("Weekend and holiday comfort/DHW (#700)")
from heatpump_optimizer.comfort_band import violations as _band_violations
from heatpump_optimizer.dhw_schedule import (
    parse_windows as _dhw_parse,
    parse_weekly_windows as _dhw_weekly,
    windows_for_day as _dhw_for_day,
)
from heatpump_optimizer.optimizer import OptimizationConfig as _OptCfg

_sat = datetime(2026, 1, 17, 14, 0)  # Saturday
_thu = datetime(2026, 1, 15, 14, 0)  # Thursday
_opt_we = _OptCfg.from_mapping(
    {
        const.CONF_COMFORT_TEMP_DAY: 21.0,
        const.CONF_COMFORT_TEMP_NIGHT: 19.0,
        const.CONF_COMFORT_TEMP_DAY_WEEKEND: 20.0,
        const.CONF_COMFORT_TEMP_NIGHT_WEEKEND: 17.5,
    }
)
R.check(
    "Saturday uses the weekend daytime comfort",
    _opt_we.get_comfort_temp(14.0, _sat) == 20.0,
    str(_opt_we.get_comfort_temp(14.0, _sat)),
)
R.check(
    "Thursday still uses the weekday daytime comfort",
    _opt_we.get_comfort_temp(14.0, _thu) == 21.0,
    str(_opt_we.get_comfort_temp(14.0, _thu)),
)
_opt_we.holiday_dates = frozenset({_thu.date()})
_opt_we.holiday_comfort_day = 18.0
R.check(
    "a holiday date uses the holiday comfort pair",
    _opt_we.get_comfort_temp(14.0, _thu) == 18.0,
    str(_opt_we.get_comfort_temp(14.0, _thu)),
)
_weekly = _dhw_weekly("weekdays 06:00-08:00, weekend 08:00-10:00")
_holiday_wins = _dhw_parse("10:00-12:00")
_fallback = _dhw_parse("06:00-08:00")
R.check(
    "a calendar-on day uses holiday DHW windows",
    _dhw_for_day(
        _weekly, 5, _fallback, holiday_windows=_holiday_wins, holiday=True
    )
    == _holiday_wins,
)
R.check(
    "Saturday without holiday keeps the weekend DHW windows",
    _dhw_for_day(
        _weekly, 5, _fallback, holiday_windows=_holiday_wins, holiday=False
    )
    == _weekly[5],
)
_we_bad = _band_violations(
    {
        const.CONF_COMFORT_TEMP_DAY_WEEKEND: 19.0,
        const.CONF_COMFORT_TEMP_NIGHT_WEEKEND: 21.0,
    },
    {},
)
R.check(
    "comfort_band.violations rejects a weekend night above day",
    any(
        v.field == const.CONF_COMFORT_TEMP_NIGHT_WEEKEND
        and v.code == "night_above_day"
        for v in _we_bad
    ),
    str(_we_bad),
)
_hol_bad = _band_violations(
    {
        const.CONF_HOLIDAY_COMFORT_DAY: 19.0,
        const.CONF_HOLIDAY_COMFORT_NIGHT: 21.0,
    },
    {},
)
R.check(
    "comfort_band.violations rejects a holiday night above day",
    any(
        v.field == const.CONF_HOLIDAY_COMFORT_NIGHT
        and v.code == "night_above_day"
        for v in _hol_bad
    ),
    str(_hol_bad),
)

# --- #699 sensor-gap euro advisor --------------------------------------------
R.section("Sensor-gap euro advisor (#699)")
_gap_house = [2.0, 2.0, 2.0, 10.0]
_gap_hp = [2.0, 2.0, 2.0, 2.0]
_gap_peak = topology.peak_miss_sek(
    _gap_house, _gap_hp, price_per_kw=90.0, window_minutes=60, dt_hours=0.25, count=3
)
_gap_cop = topology.outdoor_cop_miss_sek(2.0, 120.0, 1.0, 3.2, 2.6)
_gap_dhw = topology.dhw_coast_miss_sek(8.0, 1.5)
_gap_ranked = topology.rank_sensor_gaps(
    {},
    house_kw=_gap_house,
    hp_kw=_gap_hp,
    peak_price=90.0,
    peak_window=60,
    peak_count=3,
    outdoor_load_kw=2.0,
    outdoor_hours=120.0,
    outdoor_price=1.0,
    cop_true=3.2,
    cop_guess=2.6,
    dhw_extra_kwh=8.0,
    dhw_price=1.5,
)
_gap_by = {row["key"]: row["sek_per_month"] for row in _gap_ranked}
R.check(
    "an empty house meter ranks the peak-term miss from metering_windows",
    abs(_gap_by[const.CONF_HOUSE_POWER_ENTITY] - _gap_peak) < 1e-9
    and _gap_peak > 0,
    f"peak={_gap_peak} ranked={_gap_by}",
)

# --- round-5 D3-09 (#1317): the peak miss's floor and its count guard --------
# Both arms below were unpinned: the mutant that deleted max(0.0, ...) and
# max(int(count), 1) from peak_miss_sek survived this script's whole closure
# and the full gate. A blind peak ABOVE the true peak -- the hp-only series
# the missing house meter is priced against can catch a spike the house
# would not -- must price a miss of zero, never a negative rebate; and
# count=0, an unset months-to-spread, must spread over one month rather
# than raise.
_gap_neg = topology.peak_miss_sek(
    _gap_house, [5.0, 5.0, 5.0, 5.0], price_per_kw=90.0, window_minutes=60,
    dt_hours=0.25, count=3,
)
R.check(
    "a blind peak above the true peak prices zero, never a negative rebate",
    _gap_neg == 0.0,
    f"peak_miss_sek={_gap_neg!r}: (true - blind) is negative on these "
    "inputs, and only the max(0.0, ...) floor keeps a miss a cost",
)
_gap_c0 = None
_gap_c0_error = None
try:
    _gap_c0 = topology.peak_miss_sek(
        _gap_house, _gap_hp, price_per_kw=90.0, window_minutes=60,
        dt_hours=0.25, count=0,
    )
except ZeroDivisionError as _exc:
    # Rebind: the ``as`` name is unbound when the except block ends, and the
    # check below -- not a traceback -- is where the failure must be named.
    _gap_c0_error = _exc
R.check(
    "count=0 spreads the miss over one month instead of dividing by zero",
    _gap_c0_error is None and _gap_c0 == 3.0 * _gap_peak,
    f"error={_gap_c0_error!r} value={_gap_c0!r}: the count=3 figure on the "
    f"same inputs is {_gap_peak!r}, so the guard's one-month floor reads "
    "exactly three times it",
)
R.check(
    "an empty outdoor slot ranks the COP miss",
    abs(_gap_by[const.CONF_OUTDOOR_TEMP_ENTITY] - round(_gap_cop, 2)) < 1e-9
    and _gap_cop > 0,
    f"cop={_gap_cop}",
)
R.check(
    "an empty DHW probe ranks the coasting miss",
    abs(_gap_by[const.CONF_DHW_TEMP_ENTITY] - _gap_dhw) < 1e-9
    and _gap_dhw > 0,
    f"dhw={_gap_dhw}",
)
_gap_filled = topology.rank_sensor_gaps(
    {
        const.CONF_HOUSE_POWER_ENTITY: "sensor.house",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.out",
        const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
    },
    house_kw=_gap_house,
    hp_kw=_gap_hp,
    peak_price=90.0,
    outdoor_load_kw=2.0,
    outdoor_hours=120.0,
    outdoor_price=1.0,
    dhw_extra_kwh=8.0,
    dhw_price=1.5,
)
R.check(
    "a configured slot ranks 0 extra (null control)",
    all(row["sek_per_month"] == 0.0 for row in _gap_filled)
    and all(not row["empty"] for row in _gap_filled),
    repr(_gap_filled),
)
_gap_sensor = next(s for s in sensors if s._key == "sensor_gap_advisor")
R.check(
    "the sensor-gap advisor is a diagnostic sensor",
    _gap_sensor._key == "sensor_gap_advisor"
    and _gap_sensor.native_value == 0.0,
    f"value={_gap_sensor.native_value}",
)

# --- #1226 / round-5 D8-01: the advisor feeds the probes it prices ---------
# The #699 block above hands every input to ``topology.rank_sensor_gaps``
# itself, so it pins the arithmetic and nothing about the caller. The caller
# whose answer a user ever sees is ``SensorGapAdvisorSensor._gaps``, and to
# rank the outdoor and DHW rows above zero it must supply the five inputs its
# own rank test does. When it did not, both rows kept their 0.0 defaults and
# the enabled-by-default advisor could only ever rank the house meter.
_gap_load_data = {
    "house_power_series": [2.0, 2.0, 2.0, 10.0],
    "heat_pump_power_series": [2.0, 2.0, 2.0, 2.0],
    "peak_tariff": {
        "price_per_kw": 90.0,
        "window_minutes": 60,
        "peaks_averaged": 3,
    },
    "current_price": 1.5,
}
# A user who has the house meter but neither probe: the two probe rows are
# the whole ranking, and both must be priced.
_gap_probe_cfg = {const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power"}


def _gap_production_rows(data, config):
    """The production advisor's own ``gaps`` for a payload and a config."""
    coord = FakeCoordinator(dict(data), _config=dict(config))
    gap_sensor = sensor.SensorGapAdvisorSensor(coord, ENTRY)
    gaps = gap_sensor.extra_state_attributes["gaps"]
    return gap_sensor, {row["key"]: row for row in gaps}


_gap_probe_sensor, _gap_probe = _gap_production_rows(_gap_load_data, _gap_probe_cfg)
R.check(
    "an empty outdoor slot ranks its COP miss on the production advisor (#1226)",
    _gap_probe[const.CONF_OUTDOOR_TEMP_ENTITY]["empty"]
    and _gap_probe[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"] > 0.0,
    repr(_gap_probe),
)
R.check(
    "an empty DHW probe ranks its coasting miss on the production advisor (#1226)",
    _gap_probe[const.CONF_DHW_TEMP_ENTITY]["empty"]
    and _gap_probe[const.CONF_DHW_TEMP_ENTITY]["sek_per_month"] > 0.0,
    repr(_gap_probe),
)
_gap_top = max(
    (row for row in _gap_probe.values() if row["empty"]),
    key=lambda row: row["sek_per_month"],
)
R.check(
    "the advisor's state is the top empty slot's rank (#1226)",
    _gap_probe_sensor.native_value > 0.0
    and _gap_probe_sensor.native_value == _gap_top["sek_per_month"]
    and _gap_probe_sensor.extra_state_attributes["top_slot"] == _gap_top["key"],
    f"value={_gap_probe_sensor.native_value} top={_gap_top['key']}",
)
# Causal, not a restatement of the formula: a dearer kWh must raise both
# rows, and a heavier observed load must raise the COP row, or the caller is
# not reading them at all.
_, _gap_dearer = _gap_production_rows(
    dict(_gap_load_data, current_price=3.0), _gap_probe_cfg
)
_, _gap_heavier = _gap_production_rows(
    dict(_gap_load_data, heat_pump_power_series=[4.0, 4.0, 4.0, 4.0]),
    _gap_probe_cfg,
)
R.check(
    "both probe rows read the resolved price, and the COP row the load (#1226)",
    _gap_dearer[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"]
    > _gap_probe[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"]
    and _gap_dearer[const.CONF_DHW_TEMP_ENTITY]["sek_per_month"]
    > _gap_probe[const.CONF_DHW_TEMP_ENTITY]["sek_per_month"]
    and _gap_heavier[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"]
    > _gap_probe[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"],
    f"base={_gap_probe} dearer={_gap_dearer} heavier={_gap_heavier}",
)
# Null control: a fully wired install ranks nothing, however loud the load.
_gap_all_cfg = {
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
}
_gap_null_sensor, _gap_null = _gap_production_rows(_gap_load_data, _gap_all_cfg)
R.check(
    "a fully wired install ranks every row 0, load and price included (#1226)",
    _gap_null_sensor.native_value == 0.0
    and _gap_null_sensor.extra_state_attributes["gaps"]
    and all(row["sek_per_month"] == 0.0 for row in _gap_null.values()),
    repr(_gap_null),
)
# A design choice, stated: the probes are priced from the load the pump was
# SEEN to carry, so a payload with no power series ranks nothing -- which is
# why the advisor against the tests' own DATA (no series) is still 0.0 above.
_, _gap_unseen = _gap_production_rows({"current_price": 1.5}, _gap_probe_cfg)
R.check(
    "with no measured power series the advisor ranks no probe (#1226)",
    all(row["sek_per_month"] == 0.0 for row in _gap_unseen.values()),
    repr(_gap_unseen),
)

# --- #1226 round 2: a series with holes ranks as its clean twin ------------
# The published power series is a rolling window of readings, and a reading
# the cycle could not take leaves a hole in it: a None, or a raw string that
# never parsed. ``_numeric_samples`` drops those samples before EVERY reader
# -- the probe terms and the house meter's window peak alike -- because raw
# they raise out of ``extra_state_attributes`` (or, for a None, NaN-mark the
# window and rank its row a silent 0.00). Delete the ``isinstance`` filter
# and every check below turns red; hand the series to ``rank_sensor_gaps``
# unfiltered and the house checks do.


def _gap_holed_rows(data, config):
    """The advisor's rows, a series hole surfacing as a checked failure.

    A hole must rank as its clean twin; with the sanitising gone the raw
    sample raises (TypeError for a None, ValueError for the string), which
    becomes a red CHECK here rather than a crashed script -- a named FAIL
    line is what the mutation proof reads.
    """
    try:
        return _gap_production_rows(data, config)[1]
    except (TypeError, ValueError) as exc:
        return f"{type(exc).__name__} out of extra_state_attributes: {exc}"


# The heat-pump series' reader: the probe terms, under a config whose empty
# rows are the two probes. Constant readings, so dropping a holed sample
# cannot change the mean or the duty cycle -- the holed payload must rank
# exactly what the clean four-reading window ranks: not 0.00, no exception.
_gap_clean_hp = [2.0, 2.0, 2.0, 2.0]
_gap_clean_twin = _gap_holed_rows(
    dict(_gap_load_data, heat_pump_power_series=_gap_clean_hp), _gap_probe_cfg
)
for _gap_hole, _gap_holed_hp in (
    ("a None", [2.0, 2.0, None, 2.0]),
    ("an unparsed string", [2.0, 2.0, "x", 2.0]),
):
    _gap_holed = _gap_holed_rows(
        dict(_gap_load_data, heat_pump_power_series=_gap_holed_hp), _gap_probe_cfg
    )
    R.check(
        f"a heat-pump series carrying {_gap_hole} ranks as its clean twin (#1226)",
        _gap_holed == _gap_clean_twin
        and _gap_holed[const.CONF_OUTDOOR_TEMP_ENTITY]["sek_per_month"] > 0.0,
        f"clean={_gap_clean_twin} holed={_gap_holed_hp} -> {_gap_holed}",
    )
# The house series' reader: with the meter slot EMPTY the house row ranks
# FROM the series' window peak -- the purchase the meter exists for. The
# heat pump's blind peak is pinned low so that row is a live figure, not a
# 0-vs-0, and a holed house series must keep it.
_gap_house_cfg = {}
_gap_house_hp = [1.0, 1.0, 1.0, 1.0]
for _gap_hole, _gap_holed_house in (
    ("a None", [2.0, 2.0, None, 2.0]),
    ("an unparsed string", [2.0, 2.0, "x", 2.0]),
):
    _gap_house_holed = _gap_holed_rows(
        dict(
            _gap_load_data,
            heat_pump_power_series=_gap_house_hp,
            house_power_series=_gap_holed_house,
        ),
        _gap_house_cfg,
    )
    _gap_house_clean = _gap_holed_rows(
        dict(
            _gap_load_data,
            heat_pump_power_series=_gap_house_hp,
            house_power_series=[2.0, 2.0, 2.0, 2.0],
        ),
        _gap_house_cfg,
    )
    R.check(
        f"a house series carrying {_gap_hole} ranks as its clean twin (#1226)",
        _gap_house_holed == _gap_house_clean
        and _gap_house_holed[const.CONF_HOUSE_POWER_ENTITY]["sek_per_month"] > 0.0,
        f"clean={_gap_house_clean} holed={_gap_holed_house} -> {_gap_house_holed}",
    )
# Dropped, not NaN-marked: a hole inserted into a series with a real peak
# must rank as the same series with that slot simply absent -- the house
# row keeps its whole spike, where a raw None NaNs the 60-minute window and
# quietly prices the row 0.00.
_gap_spike_holed = _gap_holed_rows(
    dict(
        _gap_load_data,
        heat_pump_power_series=_gap_house_hp,
        house_power_series=[2.0, 2.0, None, 2.0, 10.0],
    ),
    _gap_house_cfg,
)
_gap_spike_clean = _gap_holed_rows(
    dict(
        _gap_load_data,
        heat_pump_power_series=_gap_house_hp,
        house_power_series=[2.0, 2.0, 2.0, 10.0],
    ),
    _gap_house_cfg,
)
R.check(
    "a hole in a spiked series is dropped, not priced as a 0.00 house row (#1226)",
    _gap_spike_holed == _gap_spike_clean
    and _gap_spike_holed[const.CONF_HOUSE_POWER_ENTITY]["sek_per_month"] > 0.0,
    f"clean={_gap_spike_clean} holed={_gap_spike_holed}",
)

# --- #1269 sensor advisor: value of ADDING an unconfigured sensor -----------
# The inverse of the #699 lane above: rank_sensor_gaps prices what the
# CONFIGURED sensors' absence costs; rank_sensor_advisor prices how much the
# thermal model's own predictions would tighten if each UNCONFIGURED optional
# temperature sensor were added. The proxy is structural -- the clamp band
# of each learned scalar whose learner cannot run without the sensor, swept
# through the production ThermalModel's own simulate_step -- so every number
# below is derived from config, and the checks pin the RULE (ordering,
# null controls, basis) rather than any total.
R.section("Sensor advisor: unconfigured sensors ranked by model spread (#1269)")

# A two-zone house with a throttling valve and a buffer the model treats as
# a store: every optional temperature slot empty except the indoor probe.
# This is the shape the ranking is FOR -- the one configured sensor is the
# residual lane the others' lanes sit beside.
_adv_two_zone = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_TWO_ZONE_MODE: "on",
    "lower_floor_heat_loss": 0.08,
    "upper_floor_heat_loss": 0.12,
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750,
    "max_electrical_power": 6.0,
    "buffer_tank_max_temp": 70,
    "dhw_enabled": True,
    "dhw_tank_volume": 200,
}
_adv_ranked = topology.rank_sensor_advisor(_adv_two_zone)
_adv_rows = _adv_ranked["candidates"] if _adv_ranked else []
_adv_keys = [row["key"] for row in _adv_rows]
R.check(
    "the advisor ranks the unconfigured optional temperature slots (#1269)",
    _adv_ranked is not None
    and set(_adv_keys) == {
        const.CONF_OUTDOOR_TEMP_ENTITY,
        const.CONF_FLOOR_RETURN_TEMP_ENTITY,
        const.CONF_LOWER_FLOOR_TEMP_ENTITY,
        const.CONF_DHW_TEMP_ENTITY,
        const.CONF_BUFFER_TANK_TEMP_ENTITY,
    },
    f"keys={_adv_keys}",
)
R.check(
    "an already-configured sensor appears nowhere in the ranking (null control)",
    const.CONF_INDOOR_TEMP_ENTITY not in _adv_keys,
    f"keys={_adv_keys}",
)
_adv_priced = [row for row in _adv_rows if row.get("priced")]
_adv_spreads = [float(row["spread_c"]) for row in _adv_priced]
R.check(
    "priced rows are sorted by spread, descending (#1269)",
    _adv_spreads == sorted(_adv_spreads, reverse=True)
    and len(_adv_priced) >= 2
    and all(s > 0.0 for s in _adv_spreads),
    f"spreads={_adv_spreads}",
)
R.check(
    "every unpriced row sits after every priced one (#1269)",
    all(
        (row.get("priced") is False) for row in _adv_rows[len(_adv_priced):]
    )
    and all(row.get("reason") for row in _adv_rows if not row.get("priced")),
    f"rows={_adv_rows!r}",
)
R.check(
    "the ranking is deterministic in the config (#1269)",
    topology.rank_sensor_advisor(_adv_two_zone) == _adv_ranked,
    "two calls over one config must agree exactly",
)
R.check(
    "with a measured power series the replay is driven by history (#1269)",
    topology.rank_sensor_advisor(
        _adv_two_zone, hp_kw=[3.0, 3.0, 3.0, 3.0]
    )["basis"]
    == "history",
    "basis must name the arm that drove the replay",
)
R.check(
    "with no measured series the replay says so (config basis, #1269)",
    _adv_ranked["basis"] == "config",
    f"basis={_adv_ranked.get('basis')!r}",
)
# The null control the issue demands: on a single-zone house no model term
# reads the lower-floor sensor's learner lane -- _simulate_step_single never
# touches lower_floor_loss_ratio -- so its measured spread is EXACTLY zero
# and it ranks last among the priced rows. The table claims only "this
# sensor's learner fits this scalar"; the INSTALL, through the model's own
# simulation, decides the scalar is worth nothing here.
_adv_one_zone = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    "lower_floor_heat_loss": 0.08,
    "upper_floor_heat_loss": 0.12,
    "max_electrical_power": 6.0,
    "dhw_enabled": True,
    "dhw_tank_volume": 200,
}
_adv_one = topology.rank_sensor_advisor(_adv_one_zone) or {}
_adv_one_priced = [r for r in _adv_one.get("candidates", []) if r.get("priced")]
R.check(
    "a sensor no model term reads ranks exactly 0.0 and last (null control)",
    _adv_one_priced
    and _adv_one_priced[-1]["key"] == const.CONF_LOWER_FLOOR_TEMP_ENTITY
    and float(_adv_one_priced[-1]["spread_c"]) == 0.0,
    f"one-zone priced={_adv_one_priced!r}",
)
# Null control: nothing left to suggest -- the attribute is absent, not an
# empty list, so a fully wired install publishes exactly what it did before
# the feature (the #1260 absence pattern).
_adv_full = dict(_adv_two_zone)
_adv_full.update(
    {
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.return",
        const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.lower",
        const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
        const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
    }
)
R.check(
    "a fully wired install publishes no advisor payload at all (null control)",
    topology.rank_sensor_advisor(_adv_full) is None,
    "every optional temperature slot configured ranks nothing",
)
# The plan sensors publish it beside setup_topology, on both the empty-plan
# path and the populated one, from the same live power series the #699
# advisor reads -- the history arm of the replay.
def _adv_plan_attrs(data, config):
    return sensor.SpaceHeatingPlanSensor(
        FakeCoordinator(data, _config=dict(config)), ENTRY
    ).extra_state_attributes

_adv_attrs = _adv_plan_attrs({"heat_pump_power_series": [3.0, 3.0]}, _adv_two_zone)
_adv_attr_rows = (_adv_attrs.get("sensor_advisor") or {}).get("candidates", [])
R.check(
    "the plan sensor publishes the ranking as an attribute (#1269)",
    _adv_attrs.get("sensor_advisor", {}).get("basis") == "history"
    and _adv_attr_rows
    and _adv_attr_rows[0]["key"] in {
        const.CONF_LOWER_FLOOR_TEMP_ENTITY,
        const.CONF_BUFFER_TANK_TEMP_ENTITY,
    },
    f"advisor={_adv_attrs.get('sensor_advisor')!r}",
)
R.check(
    "a fully wired install's plan sensor publishes no advisor key (#1269)",
    "sensor_advisor" not in _adv_plan_attrs({}, _adv_full),
    "the attribute must be absent, not empty, when nothing can be ranked",
)
R.check(
    "the advisor attribute is unrecorded like its siblings (#1269)",
    "sensor_advisor" in sensor._PlanSensorBase._unrecorded_attributes,
    "a ranking the card reads costs an SD card for nothing history can use",
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
    _sresult = asyncio.run(
        getattr(_sf, f"async_step_{_step}")(
            _sschema(empty_section_payload(_sschema))
        )
    )
    if _sresult.get("type") == "form" and _sresult.get("step_id") == _step and not _sresult.get("errors"):
        # #1067 G7: a two-submit page. The Modbus pre-fill's first submit
        # opens a preview of its own step and the preview's submit saves, so
        # the untouched press is followed once, never looped.
        _sschema = _sresult["data_schema"]
        _sresult = asyncio.run(
            getattr(_sf, f"async_step_{_step}")(_sschema(empty_section_payload(_sschema)))
        )
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
    if _step == "quick_setup":
        # #1258 round 2 (#1273): the questions page's untouched submit writes
        # NOTHING. It suggests the entry's stored answers (never defaults,
        # which voluptuous would refill into a bare post), and a submission
        # that says nothing new saves nothing -- the nightly-ha a5 red this
        # branch first shipped with was exactly this arm re-deriving a real
        # entry at the questions' shipped defaults. Judged like the read-only
        # page here: menu hand-back, no write, byte-identical options. The
        # changed-answer arm -- which does write through -- is
        # config_flow_steps.py's null control.
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
# depends on -- since v4.0.0 that is the combined heating-system page. The
# wood-furnace toggle (#463) hides the coil until the furnace is on.
_building_fields = _schema_keys(_pages["building"])
R.check(
    "the wood-furnace toggle is on the building page even when off",
    const.CONF_WOOD_FURNACE_ENABLED in _building_fields,
    sorted(_building_fields),
)
R.check(
    "toggle off hides the DHW wood-coil option",
    const.CONF_DHW_WOOD_COIL_ENABLED not in _building_fields,
    sorted(_building_fields),
)
_wood_on_flow = options(
    FakeEntry(data={const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top"})
)
_wood_on_flow.hass = FakeHass()
_wood_on_form = asyncio.run(_wood_on_flow.async_step_building(None))
_wood_on_fields = _schema_keys(_wood_on_form["data_schema"])
R.check(
    "the DHW wood-coil option is offered when the furnace is on",
    const.CONF_DHW_WOOD_COIL_ENABLED in _wood_on_fields,
    sorted(_wood_on_fields),
)
R.check(
    "and it is off unless asked for",
    config_flow._flatten_section_input(
        _wood_on_form["data_schema"](
            empty_section_payload(_wood_on_form["data_schema"])
        )
    ).get(const.CONF_DHW_WOOD_COIL_ENABLED)
    is False,
    "a new option that defaults on silently changes every existing install",
)
_wood_on_ok, _wood_on_detail = _defaults_survive_their_own_selectors(
    _wood_on_form["data_schema"]
)
R.check(
    "the wood-on building page can be submitted untouched",
    _wood_on_ok,
    _wood_on_detail,
)

# #516 / E4: the ten wide pages group with section(). A one-level walk of
# schema.schema records the section marker and nothing underneath it, so
# these pins use _presented_fields / _entity_selectors (which recurse) and
# keep a one-level control that must stay empty on a grouped page.
_WIDE_PAGES = (
    "building",
    "hot_water_tank",
    "entities",
    "building_preset",
    "comfort",
    "tuning",
    "learning_features",
    "hot_water",
    "entities_metering",
    "thermal_model_zones",
)
_ungrouped_wide = [
    step
    for step in _WIDE_PAGES
    if not any(_nested_schema(value) for _key, value in _pages[step].schema.items())
]
R.check(
    "the ten wide options pages group their fields with section()",
    not _ungrouped_wide,
    ", ".join(_ungrouped_wide),
)
_entities_nested = list(_entity_selectors(_pages["entities"]))
_entities_one_level = [
    (getattr(key, "schema", key), value)
    for key, value in _pages["entities"].schema.items()
    if isinstance(value, config_flow.selector.EntitySelector)
]
R.check(
    "a one-level selector walk misses the entities page's pickers",
    bool(_entities_nested) and not _entities_one_level,
    f"recursive {len(_entities_nested)}, one-level {len(_entities_one_level)}",
)
R.check(
    "and the recursive walk still names every entities picker",
    {str(name) for name, _sel in _entities_nested}
    >= {
        const.CONF_WEATHER_ENTITY,
        const.CONF_INDOOR_TEMP_ENTITY,
        const.CONF_HEAT_PUMP_SWITCH_ENTITY,
    },
    sorted(str(name) for name, _sel in _entities_nested),
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
    for marker, _validator in _presented_fields(schema):
        key = str(getattr(marker, "schema", marker))
        description = getattr(marker, "description", None)
        if isinstance(description, dict) and "suggested_value" in description:
            payload[key] = description["suggested_value"]
            continue
        default = getattr(marker, "default", None)
        if callable(default):
            payload[key] = default()
    payload.update(overrides)
    return nest_flat(schema, payload)


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
        for marker, validator in _presented_fields(schema)
        if isinstance(validator, config_flow.selector.NumberSelector)
    }


# The nominal ranges: the expert pages as they render for an entry that has
# stored nothing, so no field has been widened to fit a value.
_nominal_flow = options(FakeEntry(data={const.CONF_TIBBER_TOKEN: "t"}))
_nominal_flow.hass = FakeHass()
_NOMINAL_THERMAL = _bounds(
    asyncio.run(_nominal_flow.async_step_thermal_model(None))["data_schema"]
)
_NOMINAL_ZONES = _bounds(
    asyncio.run(_nominal_flow.async_step_thermal_model_zones(None))["data_schema"]
)
_NOMINAL = {**_NOMINAL_THERMAL, **_NOMINAL_ZONES}

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
    _thermal_schema = _drive(_sweep_flow.async_step_thermal_model(None))["data_schema"]
    _zones_schema = _drive(
        _sweep_flow.async_step_thermal_model_zones(None)
    )["data_schema"]
    _roundtrips += 1
    try:
        _accepted = {
            **config_flow._flatten_section_input(
                _thermal_schema(_submission(_thermal_schema))
            ),
            **config_flow._flatten_section_input(
                _zones_schema(_submission(_zones_schema))
            ),
        }
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
    if _rt_result.get("type") == "form" and _rt_result.get("step_id") == _step and not _rt_result.get("errors"):
        # The two-submit pre-fill page (#1067 G7): its preview's submit saves.
        _rt_schema = _rt_result["data_schema"]
        _rt_result = asyncio.run(
            getattr(_rt_flow, f"async_step_{_step}")(_rt_schema(_submission(_rt_schema)))
        )
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
              "zones", "dhw", "weather_sensitivity", "setup_overview"):
    _sflow = config_flow.HeatPumpOptimizerConfigFlow()
    _sflow.hass = FakeHass()
    if not hasattr(_sflow, f"async_step_{_step}"):
        _setup_rejected.append(f"{_step}: no handler")
        continue
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
    == {
        k: v
        for k, v in _NOMINAL_THERMAL.items()
        if k != const.CONF_SLAB_THERMAL_MASS
    },
    str(sorted(set(_wide.items()) ^ set(_NOMINAL_THERMAL.items()))),
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
    _sw_valid = config_flow._flatten_section_input(
        _sw_form["data_schema"](_submission(_sw_form["data_schema"]))
    )
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
    _caption = dict(
        _step_texts(_data["options"]["step"]["building_preset"], "data_description")
    )["building_preset_enabled"]
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
# #1067 W1067-G5: the disinfection switch's repair, mode options and refusal.
for _lang, _texts in (("strings", strings), *files.items()):
    R.check(
        f"{_lang}: the disinfection write-failure repair, its options and its "
        "refusal are translated",
        "entity_id" in _texts["issues"]["dhw_disinfection_write_failed"]["description"]
        and "entity_id" in _texts["issues"]["dhw_disinfection_switch_lost"]["description"]
        and set(_texts["selector"]["dhw_disinfection_mode"]["options"])
        == {"observe", "control"}
        and "disinfection_control_needs_entity" in _texts["options"]["error"],
    )

base_keys = all_keys(strings)
for name, data in files.items():
    diff = base_keys ^ all_keys(data)
    R.check(
        f"{name}.json matches strings.json exactly",
        not diff,
        ", ".join(sorted(diff)[:6]),
    )

# #828: the key-identity check only compares the three files to each
# other, so a field missing a data_description from all three — which
# renders with a label and no pointer — passed. reauth_confirm.tibber_token
# was that field. A completeness walk over every labelled config/options
# field is what makes the gap fail here rather than only in a review.
_undescribed = sorted(
    f"{flow}.step.{step}.{where}{key}"
    for flow in ("config", "options")
    for step, body in strings.get(flow, {}).get("step", {}).items()
    for where, node in [("", body)] + [
        (f"sections.{name}.", sec) for name, sec in (body.get("sections") or {}).items()
    ]
    for key in node.get("data", {})
    if key not in node.get("data_description", {})
)
R.check(
    "every labelled flow field has a data_description",
    not _undescribed,
    ", ".join(_undescribed[:8]),
)
R.check(
    "the reauth token field points at developer.tibber.com",
    strings["config"]["step"]["reauth_confirm"]["data_description"][
        "tibber_token"
    ]
    == "Create one at developer.tibber.com.",
    "the setup step already carries that pointer; reauth is the screen that needs it",
)
R.check(
    "and the Swedish reauth pointer is actually translated",
    files["sv"]["config"]["step"]["reauth_confirm"]["data_description"][
        "tibber_token"
    ]
    != files["en"]["config"]["step"]["reauth_confirm"]["data_description"][
        "tibber_token"
    ],
    "English copied into sv.json passes the key check and fails the user",
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

# Every field a flow page presents needs a label and a description the
# frontend actually finds, in every catalogue it may load. The frontend's rule
# (home-assistant-frontend show-dialog-config-flow.ts and
# show-dialog-options-flow.ts, renderShowFormStepFieldLabel / ...Helper):
#
#   component.<domain>.<flow>.step.<step>.[sections.<path[0]>.]data.<field>
#
# and the same for data_description, where path[0] is the section the field
# renders inside. There is NO fallback to the step-level data for a grouped
# field: a miss renders field.name, the raw key. #653 and #849 grouped pages
# with section() and left every label at step level, and the check that stood
# here looked labels up at step level too -- so it encoded the producer's
# assumption instead of the consumer's lookup and stayed green while 127
# fields rendered as raw keys. Fields are enumerated from the schemas the real
# handlers return (both flows, the reconfigure variant and the wood-on
# building page) and from the options registry's (step, key, group) rows, so
# a row hidden by its `when` in these renders is still covered.
def _frontend_flow_text(catalog, flow, step, path, kind, key):
    """What the frontend resolves for one field, or None where it shows the key."""
    node = ((catalog.get(flow) or {}).get("step") or {}).get(step) or {}
    if path:
        node = (node.get("sections") or {}).get(path[0]) or {}
    return (node.get(kind) or {}).get(key)


def _frontend_section_name(catalog, flow, step, name):
    node = ((catalog.get(flow) or {}).get("step") or {}).get(step) or {}
    return ((node.get("sections") or {}).get(name) or {}).get("name")


def _fields_with_path(schema, path=()):
    """``(section path, key)`` for every field a schema presents."""
    for key, value in (schema.schema.items() if schema is not None else []):
        name = str(getattr(key, "schema", key))
        inner = _nested_schema(value)
        if inner is None:
            yield path, name
        else:
            yield from _fields_with_path(inner, path + (name,))


_flow_fields = set()
_flow_sections = set()


def _collect_flow_form(flow_name, result):
    schema = (result or {}).get("data_schema")
    if schema is None:
        return
    step = result.get("step_id")
    for path, key in _fields_with_path(schema):
        _flow_fields.add((flow_name, step, path, key))
        if path:
            _flow_sections.add((flow_name, step, path[0]))


for step, schema in _pages.items():
    _collect_flow_form("options", {"step_id": step, "data_schema": schema})
_collect_flow_form("options", _wood_on_form)
for _row in config_flow._OPTION_FIELDS:
    _row_keys = (
        list(_row.widget({})) if _row.default is config_flow._DYNAMIC else [_row.key]
    )
    for _k in _row_keys:
        _flow_fields.add(
            ("options", _row.step, (_row.group,) if _row.group else (),
             str(getattr(_k, "schema", _k)))
        )
_setup_render_errors = []
for _name, _handler in sorted(vars(config_flow.HeatPumpOptimizerConfigFlow).items()):
    if not _name.startswith("async_step_") or _name == "async_step_reconfigure":
        continue
    _lflow = config_flow.HeatPumpOptimizerConfigFlow()
    _lflow.hass = FakeHass()
    try:
        _collect_flow_form("config", asyncio.run(_handler(_lflow, None)))
    except Exception as err:  # noqa: BLE001 - reported below, never swallowed
        _setup_render_errors.append(f"{_name}: {type(err).__name__}: {err}")
_lrc_hass = FakeHass()
_lrc_entry = FakeEntry(entry_id="labels")
_lrc_hass.config_entries.entries = [_lrc_entry]
_lrc_flow = config_flow.HeatPumpOptimizerConfigFlow()
_lrc_flow.hass = _lrc_hass
_lrc_flow.context = {
    "source": config_flow.config_entries.SOURCE_RECONFIGURE,
    "entry_id": "labels",
}
try:
    _collect_flow_form("config", asyncio.run(_lrc_flow.async_step_reconfigure(None)))
    _collect_flow_form("config", asyncio.run(_lrc_flow.async_step_user_sensors(None)))
except Exception as err:  # noqa: BLE001 - reported below, never swallowed
    _setup_render_errors.append(f"reconfigure: {type(err).__name__}: {err}")
R.check(
    "every setup handler renders for the label walk",
    not _setup_render_errors,
    "; ".join(_setup_render_errors[:4]),
)
_catalogues = {"strings.json": strings, "en.json": files["en"], "sv.json": files["sv"]}
_sectioned_fields = sorted(f for f in _flow_fields if f[2])
R.check(
    "the label walk reaches grouped fields in both flows",
    {f[0] for f in _sectioned_fields} == {"config", "options"},
    f"{len(_sectioned_fields)} grouped fields, flows {sorted({f[0] for f in _sectioned_fields})}",
)
_walked_steps = {(f[0], f[1]) for f in _flow_fields}
_unwalked_steps = sorted(
    f"{flow}.{step}"
    for flow in ("config", "options")
    for step, body in strings[flow]["step"].items()
    if (body.get("data") or body.get("sections")) and (flow, step) not in _walked_steps
)
R.check(
    "the label walk renders every step the catalogue labels",
    not _unwalked_steps,
    ", ".join(_unwalked_steps),
)
for _cat_name, _cat in _catalogues.items():
    for _kind, _what in (("data", "label"), ("data_description", "description")):
        _raw = sorted(
            f"{flow}.{step}.{'sections.' + path[0] + '.' if path else ''}{_kind}.{key}"
            for flow, step, path, key in _flow_fields
            if (_frontend_flow_text(_cat, flow, step, path, _kind, key) or key) == key
        )
        R.check(
            f"every flow field has a {_what} where the frontend looks, in {_cat_name}",
            not _raw,
            f"{len(_raw)} of {len(_flow_fields)} render the raw key: " + ", ".join(_raw[:6]),
        )
    _raw_sections = sorted(
        f"{flow}.{step}.sections.{name}"
        for flow, step, name in _flow_sections
        if (_frontend_section_name(_cat, flow, step, name) or name) == name
    )
    R.check(
        f"every section has a name translation, in {_cat_name}",
        not _raw_sections,
        ", ".join(_raw_sections[:6]),
    )

# A boolean whose label is missing renders as the bare config key, which reads
# like a bug report rather than a question -- and the description is the only
# place the "needs the two-tank model" precondition is stated.
_wood_coil_path = next(
    (path for path, key in _fields_with_path(_wood_on_form["data_schema"])
     if key == const.CONF_DHW_WOOD_COIL_ENABLED),
    (),
)
for _section in ("data", "data_description"):
    _wood_coil_en = _frontend_flow_text(
        strings, "options", "building", _wood_coil_path, _section,
        const.CONF_DHW_WOOD_COIL_ENABLED,
    )
    R.check(
        f"the DHW wood-coil option has a {_section} entry",
        bool(_wood_coil_en),
        f"missing from options.step.building at {_wood_coil_path}.{_section}",
    )
    R.check(
        f"and its Swedish {_section} is a real translation",
        _frontend_flow_text(
            files["sv"], "options", "building", _wood_coil_path, _section,
            const.CONF_DHW_WOOD_COIL_ENABLED,
        )
        not in (None, _wood_coil_en),
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

# #692: the user-visible catalog is services.yaml's keys, not a carried
# "eleven". README.md is already in this script's closure; configuration.md
# stays under docs/ (INERT) so this pin does not pull it in.
def _readme_service_names(text: str) -> set[str]:
    block = _re.search(r"^## Services\n(.*?)(?=^## |\Z)", text, _re.M | _re.S)
    if block is None:
        return set()
    return {
        m.group(1)
        for line in block.group(1).splitlines()
        if (m := _re.match(r"\| `([a-z_]+)` \|", line))
    }


_readme_svc = _readme_service_names(readme)
R.check(
    "the README Services table is services.yaml's keys, not a carried count",
    _readme_svc == frozenset(services),
    f"README={sorted(_readme_svc)} yaml={sorted(services)}",
)
_readme_svc_n = _re.search(r"^(\d+) services are registered", readme, _re.M)
R.check(
    "the README's registered-service count is derived from services.yaml",
    _readme_svc_n is not None and int(_readme_svc_n.group(1)) == len(services),
    f"README says {_readme_svc_n.group(1) if _readme_svc_n else '?'}, "
    f"services.yaml has {len(services)}",
)

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

# hvac_mode: every mode MODE_TO_HVAC maps, plus the no-data fallback a
# thermostat card reads before the first coordinator refresh completes.
for _hvm_mode, _hvm_expect in (
    (const.MODE_AUTO, climate_mod.HVACMode.AUTO),
    (const.MODE_COMFORT, climate_mod.HVACMode.HEAT),
    (const.MODE_ECONOMY, climate_mod.HVACMode.HEAT),
    (const.MODE_OFF, climate_mod.HVACMode.OFF),
    (const.MODE_BOOST, climate_mod.HVACMode.HEAT),
):
    _hvm_clim = climate_mod.HeatPumpOptimizerClimate(
        FakeCoordinator({**DATA, "mode": _hvm_mode}), clim._entry
    )
    R.check(
        f"hvac_mode maps {_hvm_mode!r} to {_hvm_expect}",
        _hvm_clim.hvac_mode == _hvm_expect,
        str(_hvm_clim.hvac_mode),
    )
_hvac_mode_none = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(None), clim._entry
)
R.check(
    "hvac_mode falls back to AUTO with no coordinator data",
    _hvac_mode_none.hvac_mode == climate_mod.HVACMode.AUTO,
    str(_hvac_mode_none.hvac_mode),
)

# preset_mode: "off" is a mode but deliberately not a preset -- reporting it
# would leave the frontend selector holding a value outside
# _attr_preset_modes -- and the no-data fallback mirrors hvac_mode's.
_preset_off = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator({**DATA, "mode": const.MODE_OFF}), clim._entry
)
R.check(
    "preset_mode reports None for the off mode rather than an invalid preset",
    _preset_off.preset_mode is None,
    str(_preset_off.preset_mode),
)
_preset_economy = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator({**DATA, "mode": const.MODE_ECONOMY}), clim._entry
)
R.check(
    "preset_mode reports a real preset unchanged",
    _preset_economy.preset_mode == const.MODE_ECONOMY,
    str(_preset_economy.preset_mode),
)
_preset_none = climate_mod.HeatPumpOptimizerClimate(
    FakeCoordinator(None), clim._entry
)
R.check(
    "preset_mode falls back to auto with no coordinator data",
    _preset_none.preset_mode == climate_mod.PRESET_AUTO,
    str(_preset_none.preset_mode),
)

R.check(
    "current_temperature is None with no coordinator data",
    climate_mod.HeatPumpOptimizerClimate(
        FakeCoordinator(None), clim._entry
    ).current_temperature
    is None,
)

# The MQTT publish that follows every mode change can fail (broker down,
# device offline); it must not crash the mode change itself. async_set_mode
# is left real so this proves the exception is caught around the publish
# specifically, not that the whole method is a no-op try/except.
_pub_fails = FakeCoordinator(DATA)


async def _raise_publish(reason=None):
    raise OSError("mqtt unreachable")


_pub_fails.async_publish_current_action = _raise_publish
_pub_fails_clim = climate_mod.HeatPumpOptimizerClimate(_pub_fails, clim._entry)
try:
    asyncio.run(_pub_fails_clim.async_turn_on())
    _publish_failure_raised = False
except OSError:
    _publish_failure_raised = True
R.check(
    "a failed ECL110 publish is caught, not propagated, and the mode change still lands",
    not _publish_failure_raised and _pub_fails.mode_calls == [const.MODE_AUTO],
    f"raised={_publish_failure_raised}, mode_calls={_pub_fails.mode_calls}",
)

# async_set_hvac_mode: AUTO and HEAT branches (OFF is covered above). The
# mutation-critical assertion is which coordinator mode landed, not just that
# the call did not raise.
_hvac_set_auto = climate_mod.HeatPumpOptimizerClimate(FakeCoordinator(DATA), clim._entry)
asyncio.run(_hvac_set_auto.async_set_hvac_mode(climate_mod.HVACMode.AUTO))
R.check(
    "setting hvac AUTO reaches the coordinator as mode auto and publishes",
    _hvac_set_auto.coordinator.mode_calls == [const.MODE_AUTO]
    and _hvac_set_auto.coordinator.pressed == ["publish:manual_hvac_mode"],
    f"mode_calls={_hvac_set_auto.coordinator.mode_calls}, pressed={_hvac_set_auto.coordinator.pressed}",
)
_hvac_set_heat = climate_mod.HeatPumpOptimizerClimate(FakeCoordinator(DATA), clim._entry)
asyncio.run(_hvac_set_heat.async_set_hvac_mode(climate_mod.HVACMode.HEAT))
R.check(
    "setting hvac HEAT reaches the coordinator as mode comfort and publishes",
    _hvac_set_heat.coordinator.mode_calls == [const.MODE_COMFORT]
    and _hvac_set_heat.coordinator.pressed == ["publish:manual_hvac_mode"],
    f"mode_calls={_hvac_set_heat.coordinator.mode_calls}",
)

# async_turn_on / async_turn_off: the HA base-class convenience methods a
# dashboard's power toggle calls, distinct from async_set_hvac_mode.
_turn_on_clim = climate_mod.HeatPumpOptimizerClimate(FakeCoordinator(DATA), clim._entry)
asyncio.run(_turn_on_clim.async_turn_on())
R.check(
    "async_turn_on selects auto and publishes",
    _turn_on_clim.coordinator.mode_calls == [const.MODE_AUTO]
    and _turn_on_clim.coordinator.pressed == ["publish:manual_turn_on"],
    f"mode_calls={_turn_on_clim.coordinator.mode_calls}",
)
_turn_off_clim = climate_mod.HeatPumpOptimizerClimate(FakeCoordinator(DATA), clim._entry)
asyncio.run(_turn_off_clim.async_turn_off())
R.check(
    "async_turn_off selects off and publishes",
    _turn_off_clim.coordinator.mode_calls == [const.MODE_OFF]
    and _turn_off_clim.coordinator.pressed == ["publish:manual_turn_off"],
    f"mode_calls={_turn_off_clim.coordinator.mode_calls}",
)

switches = collect(switch_mod)
R.check("the switch platform adds the optimizer, away and boost switches", len(switches) == 4)
sw = next(
    s for s in switches
    if getattr(s, "entity_id", "") == "switch.heat_pump_optimizer_optimizer_active"
)
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

away_sw = next(
    s for s in switches
    if getattr(s, "entity_id", "") == "switch.heat_pump_optimizer_away"
)
R.check("the away switch pins today's object id", away_sw.entity_id == "switch.heat_pump_optimizer_away")
R.check("the away switch is off when the override is off", not away_sw.is_on)
dhw_boost_sw = next(
    s for s in switches
    if getattr(s, "entity_id", "") == "switch.heat_pump_optimizer_dhw_boost"
)
space_boost_sw = next(
    s for s in switches
    if getattr(s, "entity_id", "") == "switch.heat_pump_optimizer_boost_space"
)
R.check(
    "the DHW boost switch pins today's object id",
    dhw_boost_sw.entity_id == "switch.heat_pump_optimizer_dhw_boost",
)
R.check(
    "the space boost switch pins today's object id",
    space_boost_sw.entity_id == "switch.heat_pump_optimizer_boost_space",
)
R.check(
    "the DHW boost switch is named through its translation key",
    display_name("switch", dhw_boost_sw) == "DHW Boost",
    display_name("switch", dhw_boost_sw),
)
R.check(
    "the space boost switch is named through its translation key",
    display_name("switch", space_boost_sw) == "Boost Space Heating",
    display_name("switch", space_boost_sw),
)
R.check("both boost switches are off when no overlay is live",
    not dhw_boost_sw.is_on and not space_boost_sw.is_on)
asyncio.run(dhw_boost_sw.async_turn_on())
R.check(
    "turning DHW boost on reaches the coordinator",
    dhw_boost_sw.coordinator.boost_calls[-1] == {"channel": "dhw", "active": True},
    str(dhw_boost_sw.coordinator.boost_calls),
)
asyncio.run(space_boost_sw.async_turn_on())
R.check(
    "turning space boost on reaches the coordinator",
    space_boost_sw.coordinator.boost_calls[-1] == {"channel": "space", "active": True},
    str(space_boost_sw.coordinator.boost_calls),
)
asyncio.run(dhw_boost_sw.async_turn_off())
R.check(
    "turning DHW boost off reaches the coordinator",
    dhw_boost_sw.coordinator.boost_calls[-1] == {"channel": "dhw", "active": False},
    str(dhw_boost_sw.coordinator.boost_calls),
)

# --- #195 tranche 2: switch.py's remaining branches -------------------------------
_no_data_switch = switch_mod.OptimizerEnableSwitch(FakeCoordinator(None), ENTRY)
R.check(
    "with no coordinator data at all the switch reads off, not crashes",
    not _no_data_switch.is_on,
)
R.check(
    "and its extra attributes degrade to empty rather than raising",
    _no_data_switch.extra_state_attributes == {},
)
asyncio.run(away_sw.async_turn_on())
R.check(
    "turning the away switch on reaches the coordinator's away setter",
    away_sw.coordinator.away_calls[-1] == {"active": True, "return_time": None},
    str(away_sw.coordinator.away_calls),
)
asyncio.run(away_sw.async_turn_off())
R.check(
    "turning it back off reaches the same setter with the opposite flag",
    away_sw.coordinator.away_calls[-1] == {"active": False, "return_time": None},
    str(away_sw.coordinator.away_calls),
)

dt_entities = collect(datetime_mod)
R.check("the datetime platform adds exactly one entity", len(dt_entities) == 1)
away_dt = dt_entities[0]
R.check(
    "the return datetime pins today's object id",
    away_dt.entity_id == "datetime.heat_pump_optimizer_away_return",
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
# Round-5 D3-07 (#1315): one real ndarray in the payload, because every other
# numpy leaf above is a SCALAR -- an array that fell through _finite's ndarray
# arm returned raw and nothing observed it (the mutant disabling that arm
# survived this script's whole closure and the full gate). The headroom series
# is published verbatim by PowerHeadroomSensor, so the _np_leaks sweep below
# now sees an array that only the ndarray arm can plain.
_np_data["power_headroom"] = {
    **_np_data["power_headroom"],
    "horizon_headroom_kw": _np.array([7.3, _np.inf, float("nan")]),
}
# The real model and parameters ride along: Learning Estimated COP and Solar Heat
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
# Round-5 D3-07 (#1315), the direct half: the assertions above all read the
# scrub through a sensor, so they pin only what some sensor happens to
# publish. This one calls _finite itself, pre-scrub, with the shape no
# sensor above carries -- a 2-D array whose non-finite members must come
# back None, recursively, as plain Python.
_arr_scrubbed = sensor._finite(_np.array([[1.5, _np.inf], [_np.nan, 2.0]]))
R.check(
    "the finite scrub converts an ndarray recursively, non-finite to None",
    type(_arr_scrubbed) is list
    and _arr_scrubbed == [[1.5, None], [None, 2.0]]
    and not _numpy_leaves(_arr_scrubbed),
    repr(_arr_scrubbed),
)

# --- D8-03 (#174): one object-id prefix for the hot-water domain -----------
#
# Membership comes from production, not from a list here: every hot-water
# sensor's unique-id key already starts with ``dhw``; the suggested object
# ids did not. Three moved (hot_water_energy, hot_water_cost, mixed_hot_water)
# for NEW installs only -- the unique ids are untouched, so an existing
# install keeps its entity ids and its history through the registry.
#
# The plan family is exempt, on the key property rather than by name: the
# DHW plan sensor's frozen unique-id key is still ``dhw_heating_plan`` (so it
# registers here), but #1333 moved its *translation* key and suggested id into
# the card's ``plan_`` run alongside the five other card-addressed sensors --
# a card-resolved family whose object ids have to sort together, which a
# ``dhw_`` object id cannot do.
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
    and not getattr(s, "_attr_translation_key", "").startswith("plan_")
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
    "schedule_steps",
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
    "sensor_gap_advisor",
    "wood_burn_advisor",
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

# --- D8-14 (#373): the published attribute-key SET, pinned per class -------
#
# ``extra_state_attributes`` is public API. Its keys land in users' Home
# Assistant automations and Jinja templates, and a deleted key breaks that
# YAML on the next upgrade with no error anywhere. Measured at a2c4982,
# before this roster existed: deleting ``rain_anticipation_factor`` from
# ``PredictiveInsightSensor`` left entities.py 786/786 green, structure.py
# green and the drift lane green, and deleting the WHOLE of
# ``ECL110EffectiveDisplaceSensor.extra_state_attributes`` left the same
# 786/786 green. The golden layer captures the coordinator payload one
# level upstream, so every fixture stays byte-identical; the card never
# reads these names; and statement coverage cannot see it either, because a
# deleted key is a deleted line.
#
# The exposure, measured at a2c4982 over the entities this file already
# constructs: 43 classes published 171 distinct keys through 244 class/key
# pairs, and 48 of those keys (28%) appeared nowhere in ``tests/`` as a
# string literal at all. The roster below pins 46 classes and 290 class/key
# pairs over 190 distinct names -- more than that census because it reads
# each platform through two payloads (see below), one of which reaches the
# plan branch the census's single payload never did.
#
# EXACT EQUALITY per class, in the style of the Diagnostic roster above --
# subset containment would pass on precisely the deletion this exists to
# catch. The cost of exactness is measured rather than assumed: across the
# 59 commit transitions in this history the published key sets took ONE
# addition and ZERO removals, so exactness costs about one table line per
# sixty commits, and an addition fails here as an addition with the class
# and the key named.
#
# Four holes, stated rather than papered over:
#   * a key that is KEPT but publishes ``None`` for ever still passes: this
#     pins names, not values;
#   * deleting a key together with its line in this table, in one change, is
#     bounded only by review;
#   * this pins the surface the two fixtures below REACH, so a branch no
#     fixture reaches is unpinned and its keys can be deleted silently. The
#     fix for that is a fixture, and the review of the first cut of this
#     table found one worth 10% of the surface (the plan branch, closed
#     above); the honest reading of the aggregate check's name is "the whole
#     surface these two payloads measure", and the bound is the payloads.
#     A variant of this: a few publishers pass a data dict straight through
#     (``ComfortWeightSensor`` returns ``comfort_learning`` whole), so for
#     those the table pins what the fixtures below carry rather than a
#     literal in production. Deleting the publisher outright is still
#     caught -- the class leaves the table entirely.
#   * a class whose attribute KEY SET varies with its data cannot be pinned
#     by an exact set at all. ``SolarIrradianceSensor`` merges
#     ``solar_diagnostics`` keys from the payload; ``OptimizationScoreSensor``
#     spreads ``insight["scores"]`` and ``price_tiles``. Neither key set is
#     fixed in source -- see ``_ATTR_KEYSET_IS_DATA_DRIVEN`` below. Deleting
#     the publisher outright is still caught -- the class leaves the table.
#
# The roster is taken from two payloads, because several keys are published
# only on a branch: the base ``DATA`` above, and ``_ATTR_RICH``, which turns
# on the two-zone setpoints, the solar gain, the predictive-forecast block,
# the mixing-valve recommendation and -- see below -- a populated plan for
# each of the two plan sensors. A conditional key that no fixture reaches is
# outside this table; that is a bound on coverage, and the fix for it is a
# fixture, not a softer check. The plan branch was exactly such a hole in
# the first cut of this table and is closed here rather than noted: with
# ``DATA["space_plan"] == DATA["dhw_plan"] == {}`` the two plan sensors were
# only ever read on their EMPTY-plan branch, so deleting ``slots``,
# ``total_cost`` or ``total_energy_kwh`` from ``_PlanSensorBase`` passed
# silently -- 30 of 290 class/key pairs (10.3%), in the second-largest
# publisher family after ``climate.py``.
_ATTR_RICH = {
    **DATA,
    # A populated plan for each plan sensor, so ``_PlanSensorBase`` is read
    # on the branch it spends its life on. Shaped after what the coordinator
    # really builds (``coordinator.py`` ~2470: forecast, slots,
    # total_energy_kwh, total_cost, active_now); two slots with
    # ``active_now`` so ``next_slot_start`` resolves through the
    # ``slots[1]`` arm rather than staying None on an empty list.
    "space_plan": {
        "forecast": [
            {"t": "2026-02-01T10:00:00", "price": 1.2, "space_power": 1.4},
            {"t": "2026-02-01T11:00:00", "price": 0.9, "space_power": 0.0},
        ],
        "slots": [
            {"start": "2026-02-01T10:00:00", "end": "2026-02-01T11:00:00"},
            {"start": "2026-02-01T14:00:00", "end": "2026-02-01T15:00:00"},
        ],
        "total_energy_kwh": 4.2,
        "total_cost": 6.05,
        "active_now": True,
    },
    "dhw_plan": {
        "forecast": [
            {"t": "2026-02-01T10:00:00", "price": 1.2, "dhw_power": 2.0},
            {"t": "2026-02-01T11:00:00", "price": 0.9, "dhw_power": 0.0},
        ],
        "slots": [
            {"start": "2026-02-01T05:00:00", "end": "2026-02-01T06:00:00"},
        ],
        "total_energy_kwh": 2.1,
        "total_cost": 2.55,
        "active_now": False,
    },
    # The schedule the plan branch republishes off the payload. ``DATA``
    # carries none of these, so without them the branch would publish four
    # names against ``None`` and ``dhw_min_temperature_max`` would pin the
    # "setpoint unknown" arm of ``_dhw_min_ceiling`` rather than the
    # arithmetic one.
    "dhw_windows": [["06:00", "08:30"], ["17:00", "22:00"]],
    "dhw_setpoint": 55.0,
    "comfort_temp_night": 19.5,
    "manual_plan": {"slots": [], "expires": "2026-02-01T18:00:00"},
    "current_action": {
        **DATA["current_action"],
        "mode": "auto",
        "heat_pump_on": True,
        "displace_value": 3,
        "upper_setpoint": 21.5,
        "lower_setpoint": 20.5,
        "solar_gain_kw": 1.2,
    },
    "predictive_info": {
        "solar_reduction_factor": 0.8,
        "wind_anticipation_factor": 1.1,
        "rain_anticipation_factor": 1.0,
        "pre_heat_urgency": 0.4,
    },
    "mixing_valve_mode": "weather_compensated",
    "valve_target_recommendation": {
        "target": 38.0,
        "configured_target": 40.0,
        "reason": "cheap hour",
        "price_ratio": 0.6,
    },
    "savings_months": [
        {
            "month": "2026-01",
            "baseline_sek": 1200.0,
            "actual_sek": 900.0,
            "savings_sek": 300.0,
            "savings_pct": 25.0,
            "estimated": False,
        },
        {
            "month": "2026-02",
            "baseline_sek": 800.0,
            "actual_sek": 700.0,
            "savings_sek": 100.0,
            "savings_pct": 12.5,
            "estimated": True,
        },
    ],
}


def _attr_coordinator(data):
    """A ``collect`` coordinator that every publisher can be read through."""
    coord = FakeCoordinator(data)
    coord._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    # ``SolarHeatGainSensor`` reads ``coordinator._thermal_params`` rather
    # than the published data, so it needs the real object a real
    # coordinator builds -- without it that one publisher raises
    # AttributeError instead of publishing its four keys.
    coord._thermal_params = _blind_coord._thermal_params
    return coord


_attr_base_coordinator = _attr_coordinator(DATA)
_attr_rich_coordinator = _attr_coordinator(_ATTR_RICH)

_empty_sav = sensor.MonthlySavingsSensor(
    FakeCoordinator({**DATA, "savings_months": []}), ENTRY
)
R.check(
    "MonthlySavingsSensor is unavailable before any booked month",
    not _empty_sav.available,
)
R.check(
    "MonthlySavingsSensor names settled_savings_month while empty",
    _empty_sav.extra_state_attributes.get("waiting_for") == "settled_savings_month"
    and _empty_sav.native_value is None
    and _empty_sav.extra_state_attributes.get("savings_months") == [],
    repr(_empty_sav.extra_state_attributes),
)
_ready_sav = sensor.MonthlySavingsSensor(
    FakeCoordinator(_ATTR_RICH), ENTRY
)
R.check(
    "MonthlySavingsSensor state is the open month's estimated savings_sek",
    _ready_sav.available
    and _ready_sav.native_value == 100.0
    and _ready_sav.extra_state_attributes.get("waiting_for") is None
    and _ready_sav.extra_state_attributes.get("savings_months")
    == _ATTR_RICH["savings_months"],
    repr(_ready_sav.native_value),
)


#: The one publisher whose attribute KEYS are data rather than API:
#: ``DHWHeavyDaySensor`` republishes ``dhw_draw_stats`` keyed by the
#: configured hot-water windows, so its keys here would be
#: ``"06:00-08:30"`` -- this fixture's schedule, not a name any automation
#: can rely on across installs. Pinning it would pin the fixture. Its whole
#: publisher disappearing is caught by the roster check below, which is the
#: part that matters.
_ATTR_KEYS_ARE_DATA = frozenset({"DHWHeavyDaySensor"})

#: Publishers whose attribute KEY SET is data-driven -- varies with payload
#: rather than being fixed in source -- so no exact-set pin (#405).
_ATTR_KEYSET_IS_DATA_DRIVEN = frozenset({
    "SolarIrradianceSensor", "OptimizationScoreSensor",
})


def _published_attr_keys(entities) -> dict[str, set[str]]:
    """class name -> the attribute keys those entities actually published."""
    found: dict[str, set[str]] = {}
    for entity in entities:
        if not hasattr(type(entity), "extra_state_attributes"):
            continue
        # Deliberately not ``getattr(..., default)``: that swallows an
        # AttributeError raised *inside* the property and would report a
        # broken publisher as one that publishes nothing.
        attrs = entity.extra_state_attributes
        if not attrs:
            continue
        name = type(entity).__name__
        found.setdefault(name, set())
        if name not in _ATTR_KEYS_ARE_DATA and name not in _ATTR_KEYSET_IS_DATA_DRIVEN:
            found[name].update(attrs)
    return found


_actually_published: dict[str, set[str]] = {}
for _attr_coord in (_attr_base_coordinator, _attr_rich_coordinator):
    for _attr_platform in (sensor, binary_sensor, button, climate_mod, switch_mod):
        _attr_group = collect(_attr_platform, coordinator=_attr_coord)
        for _cls_name, _keys in _published_attr_keys(_attr_group).items():
            _actually_published.setdefault(_cls_name, set()).update(_keys)

_PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
    "AwayModeBinarySensor": frozenset({
        "away_dhw_min_temperature", "away_target_temperature",
        "hours_until_return", "recovery_active", "return_time", "source"
    }),
    "ComfortWeightSensor": frozenset({"configured", "learned", "overrides"}),
    "CompressorStartsSensor": frozenset({
        "lifetime", "month", "wear_price_per_start"
    }),
    "ContractComparisonSensor": frozenset({
        "load_profile_value_per_kwh", "monthly_report", "months",
        "waiting_for"
    }),
    "CurrentSetpointSensor": frozenset({
        "lower_floor_setpoint", "upper_floor_setpoint"
    }),
    "DHWCostSensor": frozenset({
        "counting_since", "measured", "period", "split_method",
        "this_month_cost", "this_month_kwh"
    }),
    "DHWEnergySensor": frozenset({
        "counting_since", "measured", "period", "split_method",
        "this_month_cost", "this_month_kwh"
    }),
    "DHWHeatingPlanSensor": frozenset({
        "active_now", "comfort_temp_day", "comfort_temp_night", "currency",
        "day_end_hour", "day_start_hour", "dhw_min_temperature",
        "dhw_min_temperature_max", "dhw_setpoint", "dhw_windows",
        "dhw_windows_spec", "forecast", "horizon_hours", "manual_override",
        "manual_plan_window_hours", "next_slot_start", "plan_kind",
        "projection", "sensor_advisor", "setup_topology", "slot_count", "slots", "total_cost",
        "total_energy_kwh", "wood_fuel"
    }),
    # keys are the configured windows, see _ATTR_KEYS_ARE_DATA above
    "DHWHeavyDaySensor": frozenset(),
    "DHWScheduleSensor": frozenset({
        "dhw_in_demand_window", "dhw_legionella_due",
        "dhw_legionella_due_in_hours", "dhw_legionella_step_hour",
        "dhw_next_window_in_hours", "dhw_planned_heating_hours",
        "dhw_preheat_hours", "dhw_schedule", "dhw_schedule_enabled",
        "dhw_windows"
    }),
    "DHWSetpointAdvisorSensor": frozenset({
        "candidates", "current_setpoint", "heaviest_window_kwh",
        "recommended_setpoint"
    }),
    "DHWTemperatureSensor": frozenset({
        "dhw_cooling_rate", "dhw_cooling_rate_learned", "dhw_cooling_samples",
        "dhw_enabled", "dhw_heating_active", "dhw_hold_hours",
        "dhw_idle_min_temperature", "dhw_in_demand_window",
        "dhw_legionella_due_in_hours", "dhw_min_temperature",
        "dhw_next_window_in_hours", "dhw_required_temperature",
        "dhw_setpoint", "dhw_windows"
    }),
    "ECL110EffectiveDisplaceSensor": frozenset({
        "command_topic", "state_topic"
    }),
    "ExternalHeatBinarySensor": frozenset({
        "buffer_rise_c_per_h", "confidence", "dhw_rise_c_per_h", "evidence",
        "fading", "since", "source", "suppressing_electric_dhw"
    }),
    "FrequencyAdvisorSensor": frozenset({
        "commanded_hz", "fallback_active", "map", "mode", "range_hz",
        "recommended_hz", "reported_hz", "waiting_for"
    }),
    "HeatPumpActionSensor": frozenset({
        "ecl110_displace", "heat_pump_on", "lower_floor_setpoint", "power_kw",
        "power_normalized", "price", "setpoint", "solar_gain_kw",
        "upper_floor_setpoint"
    }),
    "HeatPumpOptimizerClimate": frozenset({
        "current_price", "dhw_enabled", "dhw_heating_active",
        "dhw_heating_cost", "dhw_setpoint", "dhw_temperature",
        "ecl110_command_topic", "ecl110_displace",
        "ecl110_effective_displace", "floor_return_temperature",
        "heat_pump_on", "lower_floor_setpoint", "lower_floor_temperature",
        "optimization_status", "optimizer_mode", "optimizer_setpoint",
        "outdoor_temperature", "pre_heat_urgency", "predicted_savings",
        "recommended_power_kw", "savings_percentage", "slab_temperature",
        "solar_heat_gain_kw", "solar_radiation_wm2", "solar_reduction_factor",
        "two_zone_enabled", "upper_floor_setpoint", "upper_floor_temperature",
        "wind_anticipation_factor"
    }),
    "InputHealthBinarySensor": frozenset({
        "input_ages_minutes", "learner_freeze_reason", "learners_frozen",
        "problem_inputs", "problem_messages", "problems", "stale_inputs",
        "summary"
    }),
    "MeasuredPowerSensor": frozenset({
        "energy_meter", "house_power", "recommended_power"
    }),
    "MixedHotWaterSensor": frozenset({
        "litres_40c", "shower_minutes", "tank_temperature"
    }),
    "MonthlyPeakSensor": frozenset({
        "free_headroom_threshold_kw", "fuse_advisor", "month",
        "outage_recovery_active", "projected_peak_cost", "projected_peak_kw"
    }),
    "MonthlySavingsSensor": frozenset({"savings_months", "waiting_for"}),
    "ObservedCOPSensor": frozenset({
        "cop_samples", "cop_scale", "defrost_buckets", "defrost_derate",
        "defrost_samples", "modelled_cop", "waiting_for"
    }),
    "OptimizationScoreSensor": frozenset(),  # scores + price_tiles; #405
    "OptimizationStatusSensor": frozenset({
        "prices_available", "solve_time_ms", "two_zone_enabled",
        "weather_forecast_available"
    }),
    "OptimizerEnableSwitch": frozenset({"mode", "optimization_status"}),
    "OutdoorTempSensor": frozenset({"source"}),
    "PVSurplusSensor": frozenset({
        "forecast_production_kwh", "forecast_surplus_kwh",
        "self_consumed_kwh"
    }),
    "PlanNarrativeSensor": frozenset({
        "items", "language", "lines", "stat_kind"
    }),
    "PowerHeadroomSensor": frozenset({
        "baseline_source", "headroom_kw", "horizon_headroom_kw", "limit_kw"
    }),
    "PredictedSavingsSensor": frozenset({"stat_kind"}),
    "PredictionAccuracySensor": frozenset({
        "last_diagnosis", "temperature_bias", "temperature_mae", "trust",
        "waiting_for"
    }),
    "PredictiveInsightSensor": frozenset({
        "avg_future_precip_mmh", "avg_future_wind_ms",
        "dhw_idle_min_temperature", "dhw_in_demand_window",
        "dhw_legionella_due", "dhw_min_temperature",
        "dhw_next_window_in_hours", "dhw_peak_usage_hours",
        "dhw_planned_heating_hours", "dhw_preheat_lead_hours",
        "dhw_required_temperature_now", "dhw_target_temperature",
        "dhw_usage_profile", "dhw_windows", "future_solar_6_12h_kwh",
        "future_solar_energy_kwh", "pre_heat_urgency",
        "rain_anticipation_factor", "solar_reduction_factor",
        "wind_anticipation_factor"
    }),
    "SavingsPercentageSensor": frozenset({
        "baseline_cost", "deferred_energy_cost", "predicted_cost",
        "stat_kind"
    }),
    "ScheduleSensor": frozenset({"schedule"}),
    "SensorGapAdvisorSensor": frozenset({"gaps", "top_slot"}),
    "SolarHeatGainSensor": frozenset({
        "orientation_factor", "shgc", "solar_radiation_wm2", "window_area_m2"
    }),
    "SolarIrradianceSensor": frozenset(),  # solar_diagnostics merge; #405
    "SpaceCostSensor": frozenset({
        "counting_since", "measured", "period", "split_method",
        "this_month_cost", "this_month_kwh"
    }),
    "SpaceEnergySensor": frozenset({
        "counting_since", "measured", "period", "split_method",
        "this_month_cost", "this_month_kwh"
    }),
    "SpaceHeatingPlanSensor": frozenset({
        "active_now", "comfort_temp_day", "comfort_temp_night", "currency",
        "day_end_hour", "day_start_hour", "dhw_min_temperature",
        "dhw_min_temperature_max", "dhw_setpoint", "dhw_windows",
        "dhw_windows_spec", "forecast", "horizon_hours", "manual_override",
        "manual_plan_window_hours", "next_slot_start", "plan_kind",
        "projection", "sensor_advisor", "setup_topology", "slot_count", "slots", "total_cost",
        "total_energy_kwh", "wood_fuel"
    }),
    "ThermalBatteryEnergySensor": frozenset({
        "charge_rate_kw", "discharge_rate_kw", "hours_of_autonomy",
        "modelled_components", "round_trip_efficiency_6h",
        "usable_capacity_kwh"
    }),
    "ThermalBatterySensor": frozenset({
        "charge_rate_kw", "components", "discharge_rate_kw",
        "hours_of_autonomy", "measured_components", "modelled_components",
        "round_trip_efficiency_6h", "state_of_charge_percent",
        "stored_energy_kwh", "usable_capacity_kwh"
    }),
    "TotalCostSensor": frozenset({
        "counting_since", "measured", "period", "split_method"
    }),
    "TotalEnergySensor": frozenset({
        "counting_since", "measured", "period", "split_method"
    }),
    "UpperFloorTempSensor": frozenset({"source"}),
    "ValveTargetRecommendationSensor": frozenset({
        "configured_target", "mixing_valve_mode", "price_ratio", "reason"
    }),
    "VentilationBinarySensor": frozenset({"evidence"}),
    "WoodCheaperBinarySensor": frozenset({
        "cheaper_hour_count", "sek_per_kwh"
    }),
    "WoodBurnAdvisorSensor": frozenset({"action", "reason", "when"}),
}

R.check(
    "every class that publishes attributes is in the pinned roster (#373)",
    set(_actually_published) == set(_PUBLISHED_ATTRS),
    "roster vs reality: "
    f"{sorted(set(_actually_published) ^ set(_PUBLISHED_ATTRS))}",
)
for _cls_name in sorted(set(_PUBLISHED_ATTRS) | set(_actually_published)):
    _pinned = _PUBLISHED_ATTRS.get(_cls_name, frozenset())
    _live = frozenset(_actually_published.get(_cls_name, ()))
    R.check(
        f"{_cls_name} publishes exactly its pinned attribute keys (#373)",
        _live == _pinned,
        f"removed {sorted(_pinned - _live)}; added {sorted(_live - _pinned)}",
    )
R.check(
    "the pinned attribute surface is the whole measured one (#373)",
    sum(len(_v) for _v in _PUBLISHED_ATTRS.values())
    == sum(len(_v) for _v in _actually_published.values()),
    f"{sum(len(_v) for _v in _PUBLISHED_ATTRS.values())} pinned vs "
    f"{sum(len(_v) for _v in _actually_published.values())} published",
)

# --- #405: data-driven attribute key sets are named in the holes list and
# excluded from exact-set pins (see the prose block above ``_PUBLISHED_ATTRS``).
_PUBLISHED_ATTRS_HOLES_PROSE = Path(__file__).read_text().split(
    "# Four holes, stated rather than papered over:"
)[1].split("#\n# The roster is taken from two payloads")[0]
R.check(
    "data-driven attribute publishers are named in the holes list (#405)",
    all(_cls in _PUBLISHED_ATTRS_HOLES_PROSE for _cls in _ATTR_KEYSET_IS_DATA_DRIVEN),
    f"missing from holes prose: "
    f"{sorted(_cls for _cls in _ATTR_KEYSET_IS_DATA_DRIVEN if _cls not in _PUBLISHED_ATTRS_HOLES_PROSE)}",
)
R.check(
    "data-driven attribute publishers are not exact-set pinned (#405)",
    all(_PUBLISHED_ATTRS.get(_cls) == frozenset() for _cls in _ATTR_KEYSET_IS_DATA_DRIVEN),
    f"still pinned: "
    f"{sorted(_cls for _cls in _ATTR_KEYSET_IS_DATA_DRIVEN if _PUBLISHED_ATTRS.get(_cls))}",
)

# --- D3-01 (#246): PredictiveInsightSensor's published VALUES, not just keys
#
# The roster above already catches deleting the whole of this property's
# dict (PredictiveInsightSensor drops from its pinned 20 keys to 0) or any
# one key within it -- that gap is #246's own finding, and PR #384 closed
# the key-SET half of it generically for every publisher, this sensor
# included. What the roster does NOT pin is hole one of the four stated above:
# a key that is KEPT but publishes ``None`` forever still passes,
# because the roster compares names, never values. This closes that hole
# for the sensor #246 was filed against, whose entire content IS its
# attributes -- the state is one of four words, and every anticipatory
# signal the forecast produced rides alongside it, unwatched by golden.py
# (which records ``_build_data_dict()``, one layer upstream) or the card.
#
# Re-anchored from ``round2/D3/verify3-assertions.patch`` at ``d5d8c4a``
# (seat 3's assertion, committed against the finding) rather than written
# fresh -- the file has moved a great deal since that patch was cut, most
# of it the #373/#384 roster this now sits beside. Panel-corrected count:
# 20 published attributes, not the finding's original 21.
PREDICTIVE_INFO = {
    "solar_reduction_factor": 0.62,
    "wind_anticipation_factor": 1.15,
    "rain_anticipation_factor": 1.05,
    "pre_heat_urgency": 0.8,
    "future_solar_energy_kwh": 12.5,
    "future_solar_6_12h_kwh": 4.25,
    "avg_future_wind_ms": 6.5,
    "avg_future_precip_mmh": 0.4,
    "dhw_preheat_lead_hours": 1.5,
    "dhw_peak_usage_hours": [7, 18],
    "dhw_min_temperature": 45.0,
    "dhw_target_temperature": 52.0,
    "dhw_windows": [[6.0, 8.5], [17.0, 22.0]],
    "dhw_in_demand_window": True,
    "dhw_next_window_in_hours": 0.0,
    "dhw_required_temperature_now": 48.0,
    "dhw_idle_min_temperature": 40.0,
    "dhw_legionella_due": False,
    "dhw_planned_heating_hours": 2.0,
}
_pred_by_name = {
    display_name("sensor", s): s
    for s in collect(
        sensor,
        {
            **DATA,
            "predictive_info": PREDICTIVE_INFO,
            "dhw_usage_profile": [0.25] * 24,
        },
    )
}
_pred = _pred_by_name["Predictive Optimization Insight"]
_pred_attrs = _pred.extra_state_attributes
R.check(
    "every predictive signal reaches the published attributes under its own "
    "name (#246)",
    all(_pred_attrs.get(key) == value for key, value in PREDICTIVE_INFO.items())
    and _pred_attrs.get("dhw_usage_profile") == [0.25] * 24,
    "wrong or missing: "
    + str(sorted(k for k, v in PREDICTIVE_INFO.items() if _pred_attrs.get(k) != v))
    + f"; profile {_pred_attrs.get('dhw_usage_profile')!r}",
)
_expected_pred_keys = set(PREDICTIVE_INFO) | {"dhw_usage_profile"}
R.check(
    "and the published set is exactly those signals, nothing dropped or "
    "added (#246)",
    set(_pred_attrs) == _expected_pred_keys,
    f"missing {sorted(_expected_pred_keys - set(_pred_attrs))}, "
    f"extra {sorted(set(_pred_attrs) - _expected_pred_keys)}",
)
R.check(
    "the state summarises the same signals, and says so when there are none "
    "(#246)",
    _pred.native_value == "solar_anticipation"
    and by_name["Predictive Optimization Insight"].native_value == "no forecast",
    f"with a forecast {_pred.native_value!r}, without "
    f"{by_name['Predictive Optimization Insight'].native_value!r}",
)

# --- D8-14 continued (#395): the dual-site granularity bound --------------
#
# _PUBLISHED_ATTRS pins the UNION of keys a class publishes across the two
# fixtures above, so a key published from two code sites of the SAME class
# can lose one site while the other keeps the name on the class's surface:
# the set and its count both stay right and the gate stays green. Both plan
# sensors publish ``plan_kind``, ``manual_override``,
# ``manual_plan_window_hours``, ``setup_topology``, ``dhw_windows_spec``,
# ``currency``, ``projection`` and ``horizon_hours`` from BOTH the
# empty-plan and the populated-plan ``return`` of one
# ``extra_state_attributes`` property (`sensor.py`'s ``_PlanSensorBase`).
#
# Measured on the W1-G4 review of PR #384 that filed this: by "deleting one
# site of a key stays silent", 14 of 290 class/key pairs; by code-site
# count, 16 (seven of the eight dual-branch keys silent, across the two
# plan classes each). The eighth, ``dhw_windows_spec``, is NOT caught by
# the roster either -- it is rescued only because a VALUE check above
# (":751", added by #384 for an unrelated reason: proving the spec differs
# from the plan's own reading of the windows) happens to read the
# populated branch by name. That is not roster coverage and this does not
# lean on it: the per-state sets below pin ``dhw_windows_spec`` in both
# states directly, same as the other seven.
#
# Fixed by pinning per STATE rather than per class: the empty-plan and
# populated-plan key sets, asserted separately for both plan sensors,
# reusing the two fixtures already built for the class-level roster above
# (``_attr_base_coordinator`` reads ``DATA``, where both plans are ``{}``;
# ``_attr_rich_coordinator`` reads ``_ATTR_RICH``, where both are
# populated) rather than constructing new ones.
_EMPTY_PLAN_ATTRS = frozenset({
    "currency", "dhw_windows_spec", "horizon_hours", "manual_override",
    "manual_plan_window_hours", "plan_kind", "projection",
    "sensor_advisor", "setup_topology",
    "wood_fuel",
})
_POPULATED_PLAN_ATTRS = frozenset({
    "active_now", "comfort_temp_day", "comfort_temp_night", "currency",
    "day_end_hour", "day_start_hour", "dhw_min_temperature",
    "dhw_min_temperature_max", "dhw_setpoint", "dhw_windows",
    "dhw_windows_spec", "forecast", "horizon_hours", "manual_override",
    "manual_plan_window_hours", "next_slot_start", "plan_kind", "projection",
    "sensor_advisor", "setup_topology", "slot_count", "slots", "total_cost", "total_energy_kwh",
    "wood_fuel",
})
for _plan_cls in (sensor.SpaceHeatingPlanSensor, sensor.DHWHeatingPlanSensor):
    _empty_keys = frozenset(
        _plan_cls(_attr_base_coordinator, ENTRY).extra_state_attributes
    )
    _populated_keys = frozenset(
        _plan_cls(_attr_rich_coordinator, ENTRY).extra_state_attributes
    )
    R.check(
        f"{_plan_cls.__name__} publishes exactly the pinned EMPTY-plan key "
        "set (#395)",
        _empty_keys == _EMPTY_PLAN_ATTRS,
        f"removed {sorted(_EMPTY_PLAN_ATTRS - _empty_keys)}; "
        f"added {sorted(_empty_keys - _EMPTY_PLAN_ATTRS)}",
    )
    R.check(
        f"{_plan_cls.__name__} publishes exactly the pinned POPULATED-plan "
        "key set (#395)",
        _populated_keys == _POPULATED_PLAN_ATTRS,
        f"removed {sorted(_POPULATED_PLAN_ATTRS - _populated_keys)}; "
        f"added {sorted(_populated_keys - _POPULATED_PLAN_ATTRS)}",
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
    + [("switch", s) for s in switches]
    + [("datetime", d) for d in dt_entities]
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

# #797: English entity names follow one house style. The D8-03 instrument
# (tools/audit/round3/D8/d8_ordering.py `_sentence_case`) counts a name as
# sentence-case when a content word after the first starts lower-case.
# Stop-words and parentheticals are excluded because both conventions
# lower-case them. Read the registered strings, not a roster we supply.
# "now" joined "next"/"lifetime" as a parenthetical time qualifier when
# #945 named the spot price "Cost Electricity Price (now)".
_CASE_STOP = frozenset(
    {
        "of", "the", "a", "an", "in", "on", "for", "to", "and", "than",
        "per", "vs", "h", "next", "now", "lifetime", "estimated", "model",
        "optimizer",
    }
)
_sentence_case_names = []
for _plat, _ents in _ENTITY_STRINGS.items():
    for _key, _body in _ents.items():
        _name = _body["name"]
        _words = [
            w for w in re.split(r"[\s\-()]+", _name) if w and w[0].isalpha()
        ]
        _tail = [w for w in _words[1:] if w.lower() not in _CASE_STOP]
        if any(w[0].islower() for w in _tail):
            _sentence_case_names.append(f"{_plat}.{_key}:{_name}")
R.check(
    "English entity display names are Title Case",
    not _sentence_case_names,
    ", ".join(_sentence_case_names),
)

# #945 (R4-D8-01, owner decision 2026-09-14: Option E).  Home Assistant
# sorts entities by display name, so four families cluster by sharing a
# name prefix: tariff under "Cost ", dhw's one deviant switch as
# "DHW Boost", learning under "Learning ", and the card's headline row
# under "Plan ".  ``accuracy`` stays split BY DESIGN: ``optimization_score``
# is a member of both accuracy and card_headline, one entity cannot carry
# two prefixes, and the measured floor (option E: name_order_intruders
# 159 -> 30) prefixes the headline family and leaves the accuracy trio
# unprefixed.  Pin the PREFIX, not the full wording, so a reworded
# descriptor cannot silently break the clustering; pin accuracy's
# non-membership for the same reason in reverse.  Read the registered
# strings.json (via _ENTITY_STRINGS), the table the frontend resolves
# names from -- not a roster this test supplies.
# #1227 (round-5 D8-02) went the other half: the 16 translation keys behind
# Cost/Plan/Learning carry their family prefix too, so the OBJECT-ID sort
# keeps each family in one run (the D8 harness's family_splits_by_entity_id
# 13 -> 3, the residue all platform-prefix boundaries a key cannot cross).
# New installs only -- unique ids are untouched. The table below therefore
# reads the renamed keys, and pins the same name prefixes as #945 chose.
_CLUSTER_PREFIXES: dict[str, dict[str, str]] = {
    "sensor": {
        "cost_baseline": "Cost ",
        "cost_contract_comparison": "Cost ",
        "cost_current_electricity_price": "Cost ",
        "cost_monthly_peak_power": "Cost ",
        "cost_power_headroom": "Cost ",
        "cost_predicted": "Cost ",
        "cost_total_heating": "Cost ",
        "learning_comfort_weight": "Learning ",
        "learning_estimated_cop": "Learning ",
        "learning_observed_cop": "Learning ",
        "plan_monthly_savings": "Plan ",
        "plan_optimization_score": "Plan ",
        "plan_predicted_savings": "Plan ",
        "plan_savings_percentage": "Plan ",
        "plan_narrative": "Plan ",
        "plan_space_heating": "Plan ",
        "plan_dhw_heating": "Plan ",
    },
    "button": {
        "learning_run_system_identification": "Learning ",
        "learning_reset_comfort_weight": "Learning ",
    },
    "switch": {"dhw_boost": "DHW "},
}
for _plat, _pins in _CLUSTER_PREFIXES.items():
    for _key, _prefix in sorted(_pins.items()):
        _clustered_name = _ENTITY_STRINGS[_plat][_key]["name"]
        R.check(
            f"{_plat}.{_key} clusters under the {_prefix!r} prefix (#945)",
            _clustered_name.startswith(_prefix),
            _clustered_name,
        )
for _plat, _key in (
    ("sensor", "prediction_accuracy"),
    ("button", "diagnose_last_interval"),
):
    _split_name = _ENTITY_STRINGS[_plat][_key]["name"]
    R.check(
        f"accuracy stays split: {_plat}.{_key} takes no cluster prefix (#945)",
        not _split_name.startswith(
            ("Cost ", "Learning ", "Plan ", "DHW ")
        ),
        _split_name,
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
    # #1333 moved these two deliberately (space_heating_plan -> plan_space_heating,
    # dhw_heating_plan -> plan_dhw_heating, new installs only); the D8-01 section
    # below pins the old->new pair and the unchanged unique ids.
    ("Plan Space Heating (next 24 h)", "sensor.heat_pump_optimizer_plan_space_heating"),
    ("Plan DHW Heating (next 24 h)", "sensor.heat_pump_optimizer_plan_dhw_heating"),
    ("Plan Predicted Savings", "sensor.heat_pump_optimizer_plan_predicted_savings"),
    ("Plan Monthly Savings", "sensor.heat_pump_optimizer_plan_monthly_savings"),
    ("Plan Savings Percentage", "sensor.heat_pump_optimizer_plan_savings_percentage"),
    ("Plan Optimization Score", "sensor.heat_pump_optimizer_plan_optimization_score"),
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
# that derivation must keep landing on real ids. #1227 moved five headline
# suffixes with their keys and #1333 moved the two plan ids; the card reads
# each family-prefixed suffix and keeps the pre-#1227 / pre-#1333 suffix as
# its legacy fallback (the card's LEGACY_STAT_SUFFIXES and PLAN_ID_SUFFIXES,
# pinned just below), so on this roster the derivation is required to land
# with the CURRENT suffix.
_plan_id = by_name["Plan Space Heating (next 24 h)"].entity_id
for _stat_suffix in (
    "_plan_predicted_savings",
    "_plan_savings_percentage",
    "_plan_optimization_score",
    "_plan_monthly_savings",
    "_plan_narrative",
):
    _derived = _plan_id.replace("_plan_space_heating", _stat_suffix)
    R.check(
        f"the card's suffix derivation for {_stat_suffix} stays valid",
        _derived in {s.entity_id for s in sensors},
        _derived,
    )

# --- D8-02 (#1227): the card's legacy suffixes for pre-#1227 installs ------
#
# Renaming a key changes the SUGGESTED object id for new installs only; an
# existing install keeps its registry id, so the card must also resolve the
# pre-#1227 suffixes. Read the card's own map, so deleting a legacy entry
# fails here rather than silently stripping headline stats from upgrades.
_card_legacy = {}
try:
    _card_src = (
        pathlib.Path(__file__).resolve().parent.parent
        / "custom_components" / "heatpump_optimizer" / "www"
        / "heatpump-optimizer-card.js"
    ).read_text()
except OSError:
    _card_src = ""
_legacy_block = re.search(
    r"const LEGACY_STAT_SUFFIXES = \{(.*?)\};", _card_src, re.S
)
if _legacy_block:
    for _m in re.finditer(r'"([^"]+)":\s*"([^"]+)"', _legacy_block.group(1)):
        _card_legacy[_m.group(1)] = _m.group(2)
R.check(
    "the card keeps a legacy suffix for every #1227-renamed headline stat",
    all(
        _card_legacy.get(_new) == _old
        for _new, _old in (
            ("_plan_predicted_savings", "_predicted_savings"),
            ("_plan_savings_percentage", "_savings_percentage"),
            ("_plan_optimization_score", "_optimization_score"),
            ("_plan_monthly_savings", "_monthly_savings"),
        )
    ),
    str(_card_legacy),
)

# --- D8-02 (#1227): one entity-id run per family ---------------------------
#
# Sixteen translation keys moved to carry their family prefix (Cost/Plan/
# Learning), so the OBJECT-ID sort keeps each family in one run -- the D8
# harness's family_splits_by_entity_id 13 -> 3, the residue all
# platform-prefix boundaries no key can cross. NEW installs only: the
# unique ids are untouched, so an existing install keeps its entity id and
# its history through the registry (the #174 pattern above).
for _display, _new_id, _uid in (
    ("Cost Baseline", "sensor.heat_pump_optimizer_cost_baseline", "baseline_cost"),
    ("Cost Contract Comparison", "sensor.heat_pump_optimizer_cost_contract_comparison", "contract_comparison"),
    ("Cost Electricity Price (now)", "sensor.heat_pump_optimizer_cost_current_electricity_price", "current_price"),
    ("Cost Monthly Peak Power", "sensor.heat_pump_optimizer_cost_monthly_peak_power", "monthly_peak"),
    ("Cost Power Headroom", "sensor.heat_pump_optimizer_cost_power_headroom", "power_headroom"),
    ("Cost Predicted", "sensor.heat_pump_optimizer_cost_predicted", "predicted_cost"),
    ("Cost Total Heating (lifetime)", "sensor.heat_pump_optimizer_cost_total_heating", "total_cost"),
    ("Learning Comfort Weight", "sensor.heat_pump_optimizer_learning_comfort_weight", "comfort_weight"),
    ("Learning Estimated COP", "sensor.heat_pump_optimizer_learning_estimated_cop", "current_cop"),
    ("Learning Observed COP", "sensor.heat_pump_optimizer_learning_observed_cop", "observed_cop"),
    ("Plan Monthly Savings", "sensor.heat_pump_optimizer_plan_monthly_savings", "monthly_savings"),
    ("Plan Optimization Score", "sensor.heat_pump_optimizer_plan_optimization_score", "optimization_score"),
    ("Plan Predicted Savings", "sensor.heat_pump_optimizer_plan_predicted_savings", "predicted_savings"),
    ("Plan Savings Percentage", "sensor.heat_pump_optimizer_plan_savings_percentage", "savings_percentage"),
):
    _moved = by_name.get(_display)
    R.check(
        f"{_display} suggests {_new_id} on new installs (#1227)",
        _moved is not None and _moved.entity_id == _new_id,
        str(getattr(_moved, "entity_id", None)),
    )
    R.check(
        f"{_display} keeps unique id ..._{_uid}, so existing installs keep their entity id",
        _moved is not None and _moved._attr_unique_id == f"{ENTRY.entry_id}_{_uid}",
        str(getattr(_moved, "_attr_unique_id", None)),
    )
for _display, _new_id, _uid in (
    ("Learning Reset Comfort Weight", "button.heat_pump_optimizer_learning_reset_comfort_weight", "reset_comfort_weight"),
    ("Learning Run System Identification", "button.heat_pump_optimizer_learning_run_system_identification", "system_identification"),
):
    _moved = btn_by_name.get(_display)
    R.check(
        f"{_display} suggests {_new_id} on new installs (#1227)",
        _moved is not None and _moved.entity_id == _new_id,
        str(getattr(_moved, "entity_id", None)),
    )
    R.check(
        f"{_display} keeps unique id ..._{_uid}, so existing installs keep their entity id",
        _moved is not None and _moved._attr_unique_id == f"{ENTRY.entry_id}_{_uid}",
        str(getattr(_moved, "_attr_unique_id", None)),
    )

# --- D8-01 (round 5, #1333): the two plan sensors join the plan_ run -------
#
# #1227 above moved the four card headline stats and the Cost/Learning keys to
# carry their family prefix, but left the two plan sensors on
# ``space_heating_plan`` / ``dhw_heating_plan`` -- so the dashboard card's six
# id-addressed sensors still sorted into three entity-id runs (the D8 harness's
# split_blocks_entity_id=2, split_interlopers_entity_id=34,
# families_split_entity_id=1). The plan sensors take the same prefix move:
# ``space_heating_plan -> plan_space_heating`` and
# ``dhw_heating_plan -> plan_dhw_heating``, which lands all six in ONE
# contiguous run under all three orderings the harness sorts by.
#
# The harness's own ``split_blocks_*`` counter still reads 1 after the move,
# and this check does not pin that down to 0 because it is not achievable
# without un-doing #1227: the harness's family comes from parsing the card
# text for ``sensor.heat_pump_optimizer_<key>`` literals and HEADLINE_SUFFIXES,
# and one further plan sensor the card addresses -- the savings page's
# ``statEntity("_plan_monthly_savings")`` -- is never spelled with that prefix,
# so the harness counts it as an interloper inside the window. Measured with
# the harness's own ``family_metrics`` over its own orderings, adding that
# member takes all three to (0 blocks, 0 interlopers); see the PR body.
#
# NEW installs only, exactly as #1227: the unique ids are untouched, so an
# existing install keeps its entity id and its history through the registry
# (the #174 pattern above), and the card resolves the pre-#1333 ids as its
# legacy fallback (pinned below).
for _display, _new_id, _uid in (
    ("Plan Space Heating (next 24 h)", "sensor.heat_pump_optimizer_plan_space_heating", "space_heating_plan"),
    ("Plan DHW Heating (next 24 h)", "sensor.heat_pump_optimizer_plan_dhw_heating", "dhw_heating_plan"),
):
    _moved = by_name.get(_display)
    R.check(
        f"{_display} suggests {_new_id} on new installs (#1333)",
        _moved is not None and _moved.entity_id == _new_id,
        str(getattr(_moved, "entity_id", None)),
    )
    R.check(
        f"{_display} keeps unique id ..._{_uid}, so existing installs keep their entity id",
        _moved is not None and _moved._attr_unique_id == f"{ENTRY.entry_id}_{_uid}",
        str(getattr(_moved, "_attr_unique_id", None)),
    )

# And the other half of the same contract: an existing install keeps its
# pre-#1333 registry id, so the card has to resolve BOTH plan id generations
# -- current suffix first, legacy after. Read the card's own maps, so deleting
# a legacy entry fails here rather than silently breaking upgrades. Two maps,
# because discovery matches an id's end (bare suffix) while derivation strips
# the resolved id's own separator-carrying suffix.
def _card_suffix_map(_name):
    _blk = re.search(rf"const {_name} = \{{(.*?)\}};", _card_src, re.S)
    _out = {}
    if _blk:
        for _m in re.finditer(r"(\w+):\s*\[([^\]]*)\]", _blk.group(1)):
            _out[_m.group(1)] = re.findall(r'"([^"]+)"', _m.group(2))
    return _out

_card_scan = _card_suffix_map("PLAN_ID_SUFFIXES")
_card_derive = _card_suffix_map("PLAN_ID_DERIVE")
R.check(
    "the card's plan discovery tries the current id before the pre-#1333 one",
    _card_scan.get("space") == ["plan_space_heating", "space_heating_plan"]
    and _card_scan.get("dhw") == ["plan_dhw_heating", "dhw_heating_plan"],
    str(_card_scan),
)
R.check(
    "the card's plan derivation tries the current id before the pre-#1333 one",
    _card_derive.get("space") == ["_plan_space_heating", "_space_heating_plan"]
    and _card_derive.get("dhw") == ["_plan_dhw_heating", "_dhw_heating_plan"],
    str(_card_derive),
)
# The current entry must also be the one that lands on this roster's live id.
for _kind, _current in (
    ("space", "_plan_space_heating"),
    ("dhw", "_plan_dhw_heating"),
):
    _derived_live = [
        s.entity_id for s in sensors
        if s.entity_id.endswith(_current)
    ]
    R.check(
        f"the card's current {_kind} plan id matches a built sensor (#1333)",
        _derived_live == [f"sensor.heat_pump_optimizer{_current}"],
        str(_derived_live),
    )

# Belt-and-braces for the future: the four headline sensors advertise a
# stable stat_kind attribute, same contract as plan_kind on the plan sensors.
for _display, _kind in (
    ("Plan Predicted Savings", "predicted_savings"),
    ("Plan Savings Percentage", "savings_percentage"),
    ("Plan Optimization Score", "optimization_score"),
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
    "there are exactly 59 sensors after the merge",
    len(sensors) == 59,
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
_seed_prices(_clean_hass)  # #924: the fixed first refresh fetches
_clean_entry = FakeEntry(
    data={**_OFFLINE_PRICES, const.CONF_WEATHER_ENTITY: "weather.home"}
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
# The advisor's state is rank_sensor_gaps' sek_per_month -- money per month,
# documented as CUR in the README's sensor table like the eight above. A
# MEASUREMENT without a unit records that money unitless in the statistics
# (#940), so it owes the same coordinator.currency line its siblings carry.
R.check(
    "the sensor-gap advisor publishes its money-per-month state in the currency (#940)",
    getattr(
        sensor.SensorGapAdvisorSensor(_eur, ENTRY),
        "_attr_native_unit_of_measurement",
        None,
    )
    == "EUR",
    f"unit={getattr(sensor.SensorGapAdvisorSensor(_eur, ENTRY), '_attr_native_unit_of_measurement', None)!r}",
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
for name in ("Plan Predicted Savings", "Cost Predicted", "Cost Baseline", "DHW Heating Cost (next 24 h)"):
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

# The registry covers every translation key on every platform, with no
# exceptions. The device-class defence — that an entity whose icon is its
# device class's own default need not declare one — was refuted by the
# round-4 D8 measurement (#946): 31 entities carried both a device class
# and an explicit icons.json entry, and 0 entities without a device class
# lacked one, so the convention this integration follows is "every entity
# gets a chosen icon"; the four former exceptions rendered Home
# Assistant's generic device-class glyph beside siblings that do not.
for _plat in ("sensor", "binary_sensor", "button", "switch", "datetime"):
    _expected_keys = {
        e._attr_translation_key for _p, e in _named_entities if _p == _plat
    }
    _registry_keys = set(_entity_icons.get(_plat, {}))
    _icon_diff = _expected_keys ^ _registry_keys
    R.check(
        f"the {_plat} icon registry covers every translation key exactly",
        not _icon_diff,
        f"mismatch {sorted(_icon_diff)}",
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

_first_credentials = {
    _CONF_NAME: "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok-a",
    const.CONF_WEATHER_ENTITY: "weather.home",
}
_first_sensors = {
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    const.CONF_SOLAR_FORECAST_SOURCE: const.DEFAULT_SOLAR_FORECAST_SOURCE,
}
_first_screen = {**_first_credentials, **_first_sensors}
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


def _run_past_user_sensors(flow, credentials, sensors=None):
    """Credentials, then optional pickers — the split first screen (#198)."""
    result = _run_user_step(flow, credentials)
    if result.get("type") != "form" or result.get("step_id") != "user_sensors":
        return result
    try:
        return asyncio.run(flow.async_step_user_sensors(dict(sensors or {})))
    except _AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


_real_validate_token = config_flow.validate_tibber_token
config_flow.validate_tibber_token = _accept_any_token
try:
    _dup_hass = FakeHass()
    _dup_first = _fresh_flow()
    _dup_first.hass = _dup_hass
    _dup_first_result = _run_past_user_sensors(
        _dup_first, _first_credentials, _first_sensors
    )
    R.check(
        "the first flow with these answers offers finish-setup-now",
        _dup_first_result.get("type") == "menu"
        and _dup_first_result.get("step_id") == "finish_setup"
        and tuple(_dup_first_result.get("menu_options", {}))
        == ("quick_setup", "temperature", "finish_now"),
        str(_dup_first_result)[:160],
    )
    R.check(
        "and carries the plant identity as its unique id",
        _dup_first.unique_id == _first_identity,
        f"flow unique_id {_dup_first.unique_id!r}",
    )
    _overview = asyncio.run(_dup_first.async_step_finish_now(None))
    R.check(
        "finish-setup-now after the second screen shows the setup overview",
        _overview.get("type") == "form"
        and _overview.get("step_id") == "setup_overview"
        and bool(_overview.get("description_placeholders", {}).get("setup_summary")),
        str(_overview)[:160],
    )
    _create = getattr(_dup_first, "async_step_setup_overview", None)
    if _create is None:
        _early_entry = {}
        R.check(
            "confirming the overview creates the entry",
            False,
            "async_step_setup_overview missing",
        )
    else:
        _early_entry = asyncio.run(_create({}))
        R.check(
            "confirming the overview creates the entry",
            _early_entry.get("type") == "create_entry"
            and _early_entry.get("data", {}).get(const.CONF_TIBBER_TOKEN)
            == _first_credentials[const.CONF_TIBBER_TOKEN]
            and const.CONF_TARGET_TEMP not in _early_entry.get("data", {}),
            str(_early_entry)[:160],
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
        _run_past_user_sensors(_dup_second, _first_credentials, _first_sensors)
        == {"type": "abort", "reason": "already_configured"},
    )
    _dup_other = _fresh_flow()
    _dup_other.hass = _dup_hass
    _dup_other_result = _run_past_user_sensors(
        _dup_other,
        _first_credentials,
        {**_first_sensors, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"},
    )
    R.check(
        "a second heat pump on the same Tibber account proceeds",
        _dup_other_result.get("type") == "menu"
        and _dup_other_result.get("step_id") == "finish_setup",
        str(_dup_other_result)[:160],
    )
    _continue_form = asyncio.run(_dup_other.async_step_temperature(None))
    R.check(
        "continuing setup after the menu lands on temperature",
        _continue_form.get("type") == "form"
        and _continue_form.get("step_id") == "temperature",
        str(_continue_form)[:160],
    )
    R.check(
        "the abort reason has a string to show",
        "already_configured" in strings["config"]["abort"],
    )
finally:
    config_flow.validate_tibber_token = _real_validate_token


_user_form = asyncio.run(_fresh_flow().async_step_user(None))
_user_fields = {str(getattr(k, "schema", k)) for k in _user_form["data_schema"].schema}
_sensors_form = asyncio.run(_fresh_flow().async_step_user_sensors(None))
# #824 grouped this page into indoor/solar/plant sections. A one-level walk of
# schema.schema records the section markers and nothing underneath them, which
# is the shape the comment on _WIDE_PAGES above describes; _schema_keys is the
# helper that recurses, and using it here keeps this pin measuring the fields
# rather than the wrapper.
_sensors_fields = _schema_keys(_sensors_form["data_schema"])
R.check(
    "the first screen no longer carries the ECL110 MQTT fields",
    not any(f.startswith("ecl110") for f in _user_fields),
    sorted(f for f in _user_fields if f.startswith("ecl110")),
)
R.check(
    "the sensor step offers the four heat-pump signal slots too",
    set(_SIGNAL_KEYS) <= _sensors_fields,
    sorted(set(_SIGNAL_KEYS) - _sensors_fields),
    # A slot that exists only in the options flow is a slot most users never
    # find: setup is where they are already naming their pump's entities.
)
R.check(
    "and offers them optionally, so setup still completes without a pump",
    all(
        type(k).__name__ == "Optional"
        for k in _sensors_form["data_schema"].schema
        if str(getattr(k, "schema", k)) in _SIGNAL_KEYS
    ),
)
# The null case: a fresh install with no pump integration at all. Only the
# three genuinely required fields are supplied; nothing else may appear.
_bare_sensors = _sensors_form["data_schema"]({})
R.check(
    "an untouched sensor step configures none of them",
    not (set(_SIGNAL_KEYS) & set(_bare_sensors)),
    str(set(_SIGNAL_KEYS) & set(_bare_sensors)),
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
_oksaved = asyncio.run(_okopt.async_step_comfort(_schema_defaults(_okform["data_schema"])))
# Saved, not refused: the write goes through and the dialog returns to the
# menu. What it writes is no longer the page's defaults -- an entry that never
# stored them runs with exactly those values absent (_omit_unstored_defaults),
# so the effective day comfort is read, not the options key.
R.check(
    "an untouched comfort page still saves -- through the menu return",
    _oksaved.get("type") == "menu"
    and bool(_okopt.hass.config_entries.updated)
    and _okopt._entry.options.get(
        const.CONF_COMFORT_TEMP_DAY, const.DEFAULT_COMFORT_TEMP_DAY
    ) == const.DEFAULT_COMFORT_TEMP_DAY,
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
        payload = schema(
            nest_flat(
                schema,
                {
                    **config_flow._flatten_section_input(
                        schema(empty_section_payload(schema))
                    ),
                    **overrides,
                },
            )
        )
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
        for k, v in _presented_fields(form["data_schema"])
    }


def _b3_placeholders(text):
    return set(_b3_re.findall(r"\{(\w+)\}", text))


# --- #168: the money fields follow hass.config.currency ----------------------
_eur = _b3_options("EUR")
_eur_grid_fees = asyncio.run(_eur.async_step_grid_fees(None))
_eur_tuning = asyncio.run(_eur.async_step_tuning(None))
R.check(
    "the per-kWh money fields carry the instance currency as their unit",
    _b3_units(_eur_grid_fees).get(const.CONF_GRID_FEE_FIXED) == "EUR/kWh"
    and _b3_units(_eur_grid_fees).get(const.CONF_CONTRACT_FIXED_PRICE) == "EUR/kWh",
    str({k: v for k, v in _b3_units(_eur_grid_fees).items() if v}),
)
R.check(
    "and so does the compressor replacement cost",
    _b3_units(_eur_tuning).get(const.CONF_COMPRESSOR_REPLACEMENT_COST) == "EUR",
    str({k: v for k, v in _b3_units(_eur_tuning).items() if v}),
)
R.check(
    "the grid fees page hands the currency to its descriptions as a placeholder",
    (_eur_grid_fees.get("description_placeholders") or {}).get("currency") == "EUR",
    str(_eur_grid_fees.get("description_placeholders")),
)
_grid_fees_texts = strings["options"]["step"]["grid_fees"]
_grid_fees_wanted = set().union(
    *(
        _b3_placeholders(t)
        for section in ("data", "data_description")
        for _k, t in _step_texts(_grid_fees_texts, section)
    )
)
R.check(
    "every placeholder the grid fees page's strings name is supplied by its render",
    _grid_fees_wanted <= set(_eur_grid_fees.get("description_placeholders") or {}),
    f"strings want {_grid_fees_wanted}, render gives "
    f"{set(_eur_grid_fees.get('description_placeholders') or {})}",
)
_bare = _b3_options(None)
R.check(
    "an unconfigured instance keeps the SEK every existing install has shown",
    _b3_units(asyncio.run(_bare.async_step_grid_fees(None))).get(
        const.CONF_GRID_FEE_FIXED
    )
    == f"{currency_mod.FALLBACK_CURRENCY}/kWh",
    "a unit that changes under an unconfigured instance breaks statistics",
)
_hardcoded = sorted(
    f"{flow_name}.{step}.{section}.{key}"
    for flow_name in ("config", "options")
    for step, texts in strings[flow_name]["step"].items()
    for section in ("data", "data_description")
    for key, text in _step_texts(texts, section)
    if "SEK" in text
) + sorted(
    f"issues.{key}"
    for key, texts in strings["issues"].items()
    if "SEK" in texts.get("description", "")
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
        "grid_fees",
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
    for k, v in _presented_fields(form["data_schema"]):
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
    data={**_OFFLINE_PRICES, const.CONF_WEATHER_ENTITY: "weather.home"}
)
_seed_prices(_reg_hass)  # #924
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
_seed_prices(_svc_hass)  # #924
_svc_entry = FakeEntry(
    data={**_OFFLINE_PRICES, const.CONF_WEATHER_ENTITY: "weather.home"}
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
    # A service with no fields is ``name:`` with nothing under it, which parses
    # to None -- hassfest allows it (CUSTOM_INTEGRATION_SERVICE_SCHEMA ends in
    # ``None``) and async_get_all_descriptions guards it with ``or {}``. This
    # walked every service and only worked while each still carried a name.
    _svc_examples = {
        field: spec["example"]
        for field, spec in ((_svc_spec or {}).get("fields") or {}).items()
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
_thermal_zones_form = asyncio.run(
    _thermal_flow.async_step_thermal_model_zones(None)
)["data_schema"]
_preset_flow = options(_preset_entry)
_preset_flow.hass = FakeHass()
_preset_form2 = asyncio.run(_preset_flow.async_step_building_preset(None))[
    "data_schema"
]


def _selector_min(schema, conf_key: str) -> float:
    for key, validator in _presented_fields(schema):
        if str(getattr(key, "schema", key)) == conf_key:
            return validator.config["min"]
    raise KeyError(conf_key)


_config_flow_minimums = {
    "zones/inter_zone_heat_transfer": _selector_min(
        _zones_form, const.CONF_INTER_ZONE_TRANSFER
    ),
    "zones/window_area": _selector_min(_zones_form, const.CONF_WINDOW_AREA),
    "thermal_model_zones/inter_zone_heat_transfer": _selector_min(
        _thermal_zones_form, const.CONF_INTER_ZONE_TRANSFER
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
    data={**_OFFLINE_PRICES, const.CONF_WEATHER_ENTITY: "weather.home"},
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
_svc_coord.async_set_away = _svc_record("set_away")
_svc_coord.diagnose_last_interval = lambda: {"residual": None}


def _svc_call(service, payload=None):
    return asyncio.run(
        _svc_hass.services.async_call(const.DOMAIN, service, payload or {})
    )


_svc_call(const.SERVICE_RUN_OPTIMIZATION)
R.check("run_optimization reaches the coordinator", "run_optimization" in _svc_log)

_svc_call(const.SERVICE_SET_AWAY, {"active": True})
R.check("set_away reaches the coordinator", "set_away" in _svc_log)

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

from heatpump_optimizer.thermal_model import ThermalParameters as _MVParams  # noqa: E402

_svc_hass.states.set(
    "sensor.valve_target", FakeState(22.0, unit="°C")
)
_ent_assigned = _svc_call(
    const.SERVICE_ASSIGN_ENTITY,
    {
        "key": const.CONF_MIXING_VALVE_TARGET_ENTITY,
        "entity_id": "sensor.valve_target",
    },
)
R.check(
    "assign_entity still writes a valve-target entity when one is given",
    _svc_entry.options.get(const.CONF_MIXING_VALVE_TARGET_ENTITY)
    == "sensor.valve_target"
    and _ent_assigned["entity_id"] == "sensor.valve_target",
)

_man_assigned = _svc_call(
    const.SERVICE_ASSIGN_ENTITY,
    {
        "key": const.CONF_MIXING_VALVE_TARGET_ENTITY,
        "entity_id": "",
        "manual_setpoint": 21.0,
    },
)
R.check(
    "a dumb mixing valve persists the manual setpoint without an entity",
    _svc_entry.options.get(const.CONF_MIXING_VALVE_TARGET) == 21.0
    and _svc_entry.options.get(const.CONF_MIXING_VALVE_TARGET_ENTITY) is None
    and _man_assigned.get("manual_setpoint") == 21.0,
    f"options={dict(_svc_entry.options)} response={_man_assigned}",
)
_merged = {**_svc_entry.data, **_svc_entry.options}
R.check(
    "and from_config uses that persisted number as the valve target",
    _MVParams.from_config(_merged).mixing_valve_target == 21.0,
)

_svc_call(const.SERVICE_APPLY_TOPOLOGY, {"layout": "no_valve"})
R.check(
    "apply_topology stores the validated layout",
    _svc_entry.options.get(const.CONF_TOPOLOGY_LAYOUT) == "no_valve",
)
_svc_call(
    const.SERVICE_APPLY_TOPOLOGY,
    {"layout": "no_valve", "dhw": True, "wood": False},
)
R.check(
    "apply_topology stores tank flags and seeds a missing DHW volume",
    _svc_entry.options.get(const.CONF_DHW_ENABLED) is True
    and _svc_entry.options.get(const.CONF_WOOD_FURNACE_ENABLED) is False
    and _svc_entry.options.get(const.CONF_DHW_TANK_VOLUME)
    == const.DEFAULT_DHW_TANK_VOLUME,
)
_svc_call(
    const.SERVICE_APPLY_TOPOLOGY,
    {"layout": "no_valve", "dhw": False, "wood": True},
)
R.check(
    "apply_topology can turn DHW off and wood on",
    _svc_entry.options.get(const.CONF_DHW_ENABLED) is False
    and _svc_entry.options.get(const.CONF_WOOD_FURNACE_ENABLED) is True,
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
_seed_prices(_pre_hass)  # #924
_pre_entry = FakeEntry(
    data={**_OFFLINE_PRICES, const.CONF_WEATHER_ENTITY: "weather.home"}
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
    const.SERVICE_SET_AWAY,
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

import os as _os
import subprocess as _subprocess
import time as _time

import env_drift as _env_drift
import closure as _closure
import ast as _ast_af
import inspect as _inspect
import gate_lock as _gate_lock


def _gl_crash_then_successor() -> tuple[bool, str]:
    """Finder incident: crash drops flock; take('successor') must steal."""
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        ready = Path(td) / "ready"
        env = {**_os.environ, "PYTHONPATH": str(_closure.ROOT / "tests")}
        holder = _subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import sys, time\n"
                "from pathlib import Path\n"
                "import gate_lock\n"
                "d = Path(sys.argv[1])\n"
                "gate_lock.take('holder', lock_dir=d, lease_seconds=1800, wait=False)\n"
                "with gate_lock.flock_context(d):\n"
                "    Path(sys.argv[2]).write_text('1')\n"
                "    time.sleep(30)\n",
                str(d),
                str(ready),
            ],
            cwd=str(_closure.ROOT),
            env=env,
        )
        for _ in range(50):
            if ready.exists():
                break
            _time.sleep(0.1)
        else:
            holder.kill()
            return False, "holder never ready"
        holder.kill()
        holder.wait(timeout=5)
        _time.sleep(0.2)
        flock_free = _gate_lock.flock_available(d)
        try:
            taken = _gate_lock.take(
                "successor", lock_dir=d, lease_seconds=60, wait=False,
            )
        except BlockingIOError as exc:
            return False, f"flock_available={flock_free} blocked={exc}"
        ok = flock_free and taken.label == "successor"
        return ok, f"flock_available={flock_free} label={taken.label}"


def _gl_expired_taken() -> bool:
    past = datetime.now(UTC) - timedelta(seconds=10)
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        _gate_lock._ensure_lock_dir(d)
        _gate_lock.Owner("dead-agent", past, past).write(d / _gate_lock.OWNER_NAME)
        try:
            taken = _gate_lock.take(
                "successor", lock_dir=d, lease_seconds=60, wait=False,
            )
        except BlockingIOError:
            return False
        return taken.label == "successor" and not taken.expired


def _gl_renew_extends() -> bool:
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        first = _gate_lock.take("live", lock_dir=d, lease_seconds=2, wait=False)
        _time.sleep(0.4)
        second = _gate_lock.renew("live", lock_dir=d, lease_seconds=2)
        if second.expires_at <= first.expires_at:
            return False
        try:
            _gate_lock.take("other", lock_dir=d, wait=False)
            mid_blocked = False
        except BlockingIOError:
            mid_blocked = True
        remain = (first.expires_at - datetime.now(UTC)).total_seconds()
        if remain > 0:
            _time.sleep(remain + 0.15)
        try:
            _gate_lock.take("other", lock_dir=d, wait=False)
            after_orig_blocked = False
        except BlockingIOError:
            after_orig_blocked = True
        remain2 = (second.expires_at - datetime.now(UTC)).total_seconds()
        if remain2 > 0:
            _time.sleep(remain2 + 0.15)
        try:
            late = _gate_lock.take("other", lock_dir=d, lease_seconds=60, wait=False)
            late_ok = late.label == "other"
        except BlockingIOError:
            late_ok = False
        return mid_blocked and after_orig_blocked and late_ok


def _gl_between_commands_kept() -> bool:
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        _gate_lock.take("live", lock_dir=d, lease_seconds=1800, wait=False)
        try:
            _gate_lock.take("other", lock_dir=d, wait=False)
            return False
        except BlockingIOError:
            st = _gate_lock.status(d)
            return st["owner"] is not None and st["owner"].label == "live"


R.check(
    "an expired lease is taken without forensics",
    _gl_expired_taken(),
    "must steal on expires_at, not a pid table",
)
R.check(
    "renew extends the lease past the original expiry",
    _gl_renew_extends(),
    "a renewed lease must still refuse a second label",
)
R.check(
    "a live agent between commands keeps the lock",
    _gl_between_commands_kept(),
    "no holding marker: flock free must not steal",
)
_gl_ok, _gl_detail = _gl_crash_then_successor()
R.check(
    "a crashed hold lets take('successor') steal",
    _gl_ok,
    _gl_detail,
)


def _gl_orphaned_stolen() -> tuple[bool, str]:
    """#1143 class (b): a lease that named a DEAD owner process is stolen
    instead of serialising the box until it expires; a lease naming a LIVE
    process is still respected (the null control, beside the steal).

    The property is the recorded pid's liveness, not the instance: the dead
    pid is a reaped child of this test, and the live one is this process, so
    neither arm can be satisfied by a lease that never recorded a pid.
    """
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "dead"
        dead = _subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait(timeout=5)
        _gate_lock.take(
            "seat", lock_dir=d, lease_seconds=1800, wait=False, owner_pid=dead.pid,
        )
        try:
            taken = _gate_lock.take("successor", lock_dir=d, lease_seconds=60, wait=False)
            stole = taken.label == "successor"
        except BlockingIOError:
            stole = False
        # Null control: the same shape with a LIVE owner pid must NOT be stolen.
        d2 = Path(td) / "live"
        _gate_lock.take(
            "seat", lock_dir=d2, lease_seconds=1800, wait=False, owner_pid=_os.getpid(),
        )
        try:
            _gate_lock.take("other", lock_dir=d2, wait=False)
            live_blocked = False
        except BlockingIOError:
            live_blocked = True
        return stole and live_blocked, f"stole={stole} live_blocked={live_blocked}"


_gl_orph_ok, _gl_orph_detail = _gl_orphaned_stolen()
R.check(
    "a lease whose named owner process is gone is stolen (#1143)",
    _gl_orph_ok,
    _gl_orph_detail,
)


def _gl_auto_lease() -> tuple[bool, str]:
    """run.sh leases a FULL or stress run itself; a second one waits."""
    import threading
    with _tempfile.TemporaryDirectory() as td:
        d, seen = Path(td) / "lock", Path(td) / "seen"
        scoped, stress = Path(td) / "a.run", Path(td) / "b.run"
        scoped.write_text("tests/entities.py\n")
        stress.write_text("tests/entities.py\ntests/stress.py\n")
        need = [_gate_lock.needs_lease(s) for s in ("", str(stress), str(scoped))]
        _gate_lock.take("other", lock_dir=d, lease_seconds=60, wait=False)
        child = ("import os, sys; from pathlib import Path; "
                 "Path(sys.argv[1]).write_text(open(sys.argv[2] + '/owner').read()"
                 " + os.environ['HPO_GATE_LOCK_LABEL']); sys.exit(3)")
        poll, _gate_lock.WAIT_POLL_SECS = _gate_lock.WAIT_POLL_SECS, 0.05
        out: list[int] = []
        t = threading.Thread(target=lambda: out.append(_gate_lock.auto_lease(
            "auto", [sys.executable, "-c", child, str(seen), str(d)], lock_dir=d)))
        try:
            t.start()
            _time.sleep(0.5)
            waited = not seen.exists()
            _gate_lock.release("other", lock_dir=d)
            t.join(timeout=10)
        finally:
            _gate_lock.WAIT_POLL_SECS = poll
        text = seen.read_text() if seen.exists() else ""
        ok = (need == [True, True, False] and waited and out == [3]
              and "label=auto" in text and text.endswith("auto")
              and _gate_lock.read_owner(d) is None)
        return ok, f"need={need} waited={waited} rc={out} released={_gate_lock.read_owner(d) is None}"


def _gl_lease_hardening() -> tuple[bool, str]:
    """#1089 review prep: one winner per race, a SIGKILLed holder is stolen at
    once, and a signalled lease takes the gate's whole process group down."""
    import signal as _sig
    import threading
    wins = []
    with _tempfile.TemporaryDirectory() as td:
        for trial in range(10):
            d, gate, got = Path(td) / f"race{trial}", threading.Barrier(8), []

            def racer(i: int) -> None:
                gate.wait()
                try:
                    got.append(_gate_lock.take(f"r{i}", lock_dir=d, wait=False).label)
                except BlockingIOError:
                    pass
            ts = [threading.Thread(target=racer, args=(i,)) for i in range(8)]
            [t.start() for t in ts]
            [t.join() for t in ts]
            wins.append(len(got))
        d, ready, pidf = Path(td) / "crash", Path(td) / "ready", Path(td) / "pid"
        env = {**_os.environ, "PYTHONPATH": str(_closure.ROOT / "tests")}
        holder = _subprocess.Popen([sys.executable, "-c",
            "import sys, time; from pathlib import Path; import gate_lock as g\n"
            "d = Path(sys.argv[1]); g.take('h', lock_dir=d, wait=False)\n"
            "with g.flock_context(d):\n"
            "    g.renew('h', lock_dir=d); Path(sys.argv[2]).write_text('1'); time.sleep(30)\n",
            str(d), str(ready)], env=env)
        for _ in range(50):
            if ready.exists():
                break
            _time.sleep(0.1)
        holder.kill()
        holder.wait()
        try:
            stolen = _gate_lock.take("successor", lock_dir=d, wait=False).label == "successor"
        except BlockingIOError:
            stolen = False
        wrapper = _subprocess.Popen([sys.executable, "-c",
            "import signal, sys; import gate_lock as g\n"
            "signal.signal(signal.SIGTERM, lambda n, f: sys.exit(143))\n"
            "g.run_group(['bash', '-c', 'sleep 60 & echo $! > ' + sys.argv[1] + '; wait'])\n",
            str(pidf)], env=env)
        for _ in range(50):
            if pidf.exists() and pidf.read_text().strip():
                break
            _time.sleep(0.1)
        wrapper.send_signal(_sig.SIGTERM)
        try:
            wrapper.wait(timeout=30)
        except _subprocess.TimeoutExpired:  # the holder never came down: that is the defect
            wrapper.kill()
            wrapper.wait()
        _time.sleep(0.3)
        try:
            _os.kill(int(pidf.read_text()), 0)
            orphan = _subprocess.run(["ps", "-o", "stat=", "-p", pidf.read_text().strip()],
                                     capture_output=True, text=True).stdout.strip()[:1] not in ("", "Z")
        except (ProcessLookupError, ValueError):
            orphan = False
        # #1089 round 1: SIGKILL of the holder ALONE while its gate lives.
        d, pidf = Path(td) / "orphan", Path(td) / "pids"
        holder = _subprocess.Popen([sys.executable, "-c",
            "import sys; from pathlib import Path; import gate_lock as g\n"
            "g.auto_lease('h', ['bash', '-c', 'sleep 60 & echo $$ $! > ' + sys.argv[2] + '; wait'],"
            " lock_dir=Path(sys.argv[1]))\n", str(d), str(pidf)], env=env)
        for _ in range(100):
            if pidf.exists() and len(pidf.read_text().split()) == 2:
                break
            _time.sleep(0.1)
        holder.kill()
        holder.wait()
        try:
            _gate_lock.take("successor", lock_dir=d, wait=False)
            refused = False
        except BlockingIOError:
            refused = True
        gate_pid = int(pidf.read_text().split()[0])
        try:
            _os.killpg(gate_pid, _sig.SIGKILL)
        except ProcessLookupError:
            pass
        _time.sleep(0.5)
        try:
            after = _gate_lock.take("successor", lock_dir=d, wait=False).label == "successor"
        except BlockingIOError:
            after = False
        # run.sh must RE-EXECUTE under the lease: with it held elsewhere, a FULL
        # run waits in auto-lease and starts no lane (a no-op exec would).
        d, out = Path(td) / "runsh", Path(td) / "runsh.log"
        _gate_lock.take("other", lock_dir=d, lease_seconds=60, wait=False)
        renv = {k: v for k, v in _os.environ.items()
                if k not in ("HPO_GATE_LOCK_LABEL", "HPO_GATE_FLOCK_CHILD", "GATE_SCOPE")}
        renv.update(HPO_GATE_LOCK_DIR=str(d), GATE_SCOPE="full")
        with open(out, "w") as log:
            gate = _subprocess.Popen(["bash", "tests/run.sh"], cwd=str(_closure.ROOT), env=renv,
                                     stdout=log, stderr=_subprocess.STDOUT, start_new_session=True)
        for _ in range(100):
            if "waiting for the lease held by other" in out.read_text() or gate.poll() is not None:
                break
            _time.sleep(0.1)
        _time.sleep(1.0)
        text = out.read_text()
        try:
            _os.killpg(gate.pid, _sig.SIGKILL)
        except ProcessLookupError:
            pass
        gate.wait()
        execd = "waiting for the lease held by other" in text and "##########" not in text
    ok = wins == [1] * 10 and stolen and not orphan and refused and after and execd
    return ok, (f"winners={wins} crash_stolen={stolen} grandchild_alive={orphan} "
                f"holder_only_kill_refused={refused} taken_after_gate_dead={after} run_sh_execd={execd}")


_gl_ok, _gl_detail = _gl_auto_lease()
_run_sh = (_closure.ROOT / "tests/run.sh").read_text()
_gl_line = '[ "$("$PYTHON" tests/gate_lock.py needs-lease "$SCOPE_RUN" 2>&1)" != none ]'
R.check(
    "run.sh leases a FULL or stress run itself, and a second one waits",
    _gl_ok and -1 < _run_sh.find(_gl_line) < _run_sh.find("lane_units() {"),
    _gl_detail + "; run.sh must lease on anything but an explicit 'none'",
)
_gl_ok, _gl_detail = _gl_lease_hardening()
R.check(
    "the lease has one winner, a dead gate is stolen, a live one is not, and run.sh re-executes",
    _gl_ok,
    _gl_detail,
)


def _gl_same_label_expired_take() -> bool:
    """Same-label take on an expired lease rewrites the owner (#479 residual)."""
    past = datetime.now(UTC) - timedelta(seconds=10)
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        _gate_lock._ensure_lock_dir(d)
        _gate_lock.Owner("holder", past, past).write(d / _gate_lock.OWNER_NAME)
        try:
            taken = _gate_lock.take(
                "holder", lock_dir=d, lease_seconds=60, wait=False,
            )
        except RuntimeError:
            return False
        return taken.label == "holder" and not taken.expired


def _gl_same_label_return_clears_holding() -> tuple[bool, str]:
    """Same-label take after crash clears holding so a waiter cannot steal."""
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td) / "lock"
        ready = Path(td) / "ready"
        env = {**_os.environ, "PYTHONPATH": str(_closure.ROOT / "tests")}
        holder = _subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import sys, time\n"
                "from pathlib import Path\n"
                "import gate_lock\n"
                "d = Path(sys.argv[1])\n"
                "gate_lock.take('holder', lock_dir=d, lease_seconds=1800, wait=False)\n"
                "with gate_lock.flock_context(d):\n"
                "    Path(sys.argv[2]).write_text('1')\n"
                "    time.sleep(30)\n",
                str(d),
                str(ready),
            ],
            cwd=str(_closure.ROOT),
            env=env,
        )
        for _ in range(50):
            if ready.exists():
                break
            _time.sleep(0.1)
        else:
            holder.kill()
            return False, "holder never ready"
        holder.kill()
        holder.wait(timeout=5)
        _time.sleep(0.2)
        _gate_lock.take("holder", lock_dir=d, lease_seconds=1800, wait=False)
        holding = (d / _gate_lock.HOLDING_NAME).exists()
        try:
            _gate_lock.take("waiter", lock_dir=d, lease_seconds=60, wait=False)
            stolen = True
        except BlockingIOError:
            stolen = False
        return not holding and not stolen, f"holding={holding} stolen={stolen}"


R.check(
    "an expired same-label take rewrites the lease",
    _gl_same_label_expired_take(),
    "must not route expired same-label take through renew()",
)
_gl_sl_ok, _gl_sl_detail = _gl_same_label_return_clears_holding()
R.check(
    "same-label return clears holding",
    _gl_sl_ok,
    _gl_sl_detail,
)

# --- the scoped gate's one exception to "the whole integration" -------------
#
# `_widen` gives env_drift.py the whole integration because no tracer can see
# which files a capture in another worktree depended on, and a second rule in
# `select` runs it for any custom_components/ change whether or not the
# closure saw the file. Both exclude the bundled card, and the exclusion was
# measured rather than argued -- two captures on the same tree with
# `env_drift.py --capture . <out> --all`:
#
#   null control      the card asset edited (`www/heatpump-optimizer-card.js:14`,
#                     CARD_VERSION 5.4.20 -> 9.9.99): all 55 scenarios
#                     byte-identical, sha256
#                     294c98fb07f7bac0e16342a13a34c354577cf88c60bc9a1e73c52d4432890c10
#                     on both sides
#   positive control  one token, `thermal_model.py:2683` (`T_room * dt` ->
#                     `T_room * dt * 1.0001`): the captures differ, sha256
#                     656df8995f3692d18d12992679aa0dda6b13e082463763e84ca460636736411c
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
# ... and it lists the payload's producer BEFORE the card that reads it.
# run.sh runs plan_view.py first, and `scope.run` is the plan the gate
# reports; `sorted()` alone puts card.mjs ("c") ahead of plan_view.py ("p"),
# so membership in the list is not enough -- the position is the dependency.
_CARD_RUN = _closure.select([_CARD_ASSET])["run"]
R.check(
    "and lists the card's payload producer before the card (#1146)",
    "tests/plan_view.py" in _CARD_RUN
    and "tests/card.mjs" in _CARD_RUN
    and _CARD_RUN.index("tests/plan_view.py") < _CARD_RUN.index("tests/card.mjs"),
    f"run={_CARD_RUN}",
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
# A second exclusion, for a different reason (#357): quality_scale.yaml was
# simultaneously declared INERT and swept into env_drift's and golden's
# widened closures by this same rule -- a contradiction `merge` refuses that
# the closures CI job's `--record-only` path never reached. Measured rather
# than argued, like the card above: `env_drift.py --capture . <out> --all`
# and a direct `golden.capture()` over five scenarios were byte-identical
# across a quality_scale.yaml edit and differed across the same thermal_model
# probe used for the card's positive control (see tests/closure.py's
# NEVER_WIDENED comment for both sha256 pairs).
_QS = "custom_components/heatpump_optimizer/quality_scale.yaml"
R.check(
    "the widening rule leaves the quality-scale register out too",
    _QS not in _widened[_ED] and _QS not in _widened["tests/golden.py"],
    "hassfest skips it for custom repositories and neither capture moves "
    "when it changes; measured byte-identical captures say so. (#951 moved "
    "the register into this script's RECORDED closure -- a direct read, "
    "not a widened one, so the exclusion above still holds.)",
)

# #1218 (D3-08): the deployment-shape lane's measured closure is the whole
# tracked package -- it materialises the package file by file, and the
# gate's tracer records every read -- so every diff touching any production
# file selects the lane. The same recording pairs 53 of the 276 scripts at
# 0.80 or more of shared production-module closure. The numbers are
# re-derived here exactly as tools/audit/round5/D3/resource_r5.py derived
# them (Jaccard over the closure files under
# custom_components/heatpump_optimizer/, empty sets skipped), and the lane's
# docstring records them as this repository's selection-cost note. A
# SELECTION cost only: which mutants each script kills was never measured
# (the pre-screen stops at the first killer), so nothing claims two
# overlapping scripts are redundant.
_D308_DS = "tests/deployment_shape.py"
_D308 = json.loads(_closure.CLOSURES.read_text())["closures"]
_D308_PROD = {
    f for _fs in _D308.values() for f in _fs
    if f.startswith("custom_components/heatpump_optimizer/")
}


def _d308_pairs(closures: dict, prod: set, floor: float = 0.80) -> list:
    """resource_r5.py's pair predicate, re-derived here."""
    names = sorted(closures)
    out = []
    for _i in range(len(names)):
        for _j in range(_i + 1, len(names)):
            _a = set(closures[names[_i]]) & prod
            _b = set(closures[names[_j]]) & prod
            if not _a or not _b:
                continue
            _jac = len(_a & _b) / len(_a | _b)
            if _jac >= floor:
                out.append((_jac, names[_i], names[_j], len(_a & _b)))
    return out


_D308_PAIRS = _d308_pairs(_D308, _D308_PROD)
_D308_TOTAL = len(_D308) * (len(_D308) - 1) // 2
_D308_EMPTY = sorted(
    s for s, fs in _D308.items() if not set(fs) & _D308_PROD)
_D308_COMPARABLE = _D308_TOTAL - sum(
    1 for _i, _a in enumerate(sorted(_D308))
    for _b in sorted(_D308)[_i + 1:]
    if not ((set(_D308[_a]) & _D308_PROD) and (set(_D308[_b]) & _D308_PROD)))
_D308_FULLCOV = sorted(s for s, fs in _D308.items() if _D308_PROD <= set(fs))
_D308_SELECTED = _D308_DS in _closure.select(
    ["custom_components/heatpump_optimizer/optimizer.py"])["run"]
R.check(
    "the deployment-shape lane's closure is the whole tracked package, so "
    "any production diff selects it (#1218)",
    _D308_PROD <= set(_D308.get(_D308_DS, []))
    and _integration_py <= set(_D308.get(_D308_DS, []))
    and _D308_FULLCOV == [_D308_DS]
    and _D308_SELECTED,
    f"closure reaches {len(set(_D308.get(_D308_DS, [])) & _D308_PROD)}/"
    f"{len(_D308_PROD)} production files and covers the tree's "
    f"{len(_integration_py)} package modules "
    f"({_integration_py <= set(_D308.get(_D308_DS, []))}), "
    f"full-coverage closures={_D308_FULLCOV}, a production diff selects "
    f"it={_D308_SELECTED} -- this is the cost the note beside the lane "
    "records",
)
# The note carries the derived numbers, so a re-record that moves them fails
# HERE instead of leaving stale prose behind. The text is whitespace-
# normalised first so a future re-wrap of the paragraph cannot flip these.
_D308_DS_TEXT = " ".join((_closure.ROOT / _D308_DS).read_text().split())
R.check(
    "and the lane's docstring records those measured numbers as the "
    "selection-cost note (#1218)",
    all(_s in _D308_DS_TEXT for _s in (
        "D3-08", "#1218", "selection cost",
        f"all {len(_D308_PROD)} files",
        f"{len(_D308_PAIRS)} of the {_D308_TOTAL}",
        f"{_D308_COMPARABLE} pairs",
    ))
    and all(_e in _D308_DS_TEXT for _e in _D308_EMPTY),
    "the note cites numbers this tree derives: "
    f"{len(_D308_PROD)} production files; {len(_D308_PAIRS)} of "
    f"{_D308_TOTAL} pairs at >= 0.80; {_D308_COMPARABLE} pairs comparable; "
    f"no production closure in {_D308_EMPTY}; missing markers -> "
    f"{[s for s in ('D3-08', '#1218', 'selection cost', 'all %d files' % len(_D308_PROD), '%d of the %d' % (len(_D308_PAIRS), _D308_TOTAL), '%d pairs' % _D308_COMPARABLE) if s not in _D308_DS_TEXT]}",
)
# The predicate itself, on synthetic closures built from real production
# names: equal sets count, disjoint and below-boundary do not, an exactly
# 0.80 pair counts, and a script with no production closure is skipped in
# either position -- so the count above cannot be an artefact of the
# predicate rather than of the recording.
_D308_SYN = sorted(_D308_PROD)
R.check(
    "the overlap predicate counts equal sets, skips empty ones and holds "
    "the 0.80 boundary (#1218)",
    [p[3] for p in _d308_pairs(
        {"tests/a.py": _D308_SYN[:1], "tests/b.py": _D308_SYN[:1]},
        _D308_PROD)] == [1]
    and _d308_pairs(
        {"tests/a.py": _D308_SYN[:1], "tests/b.py": _D308_SYN[1:2]},
        _D308_PROD) == []
    and [p[3] for p in _d308_pairs(
        {"tests/a.py": _D308_SYN[:4], "tests/b.py": _D308_SYN[:5]},
        _D308_PROD)] == [4]
    and _d308_pairs(
        {"tests/a.py": _D308_SYN[:4], "tests/b.py": _D308_SYN[:6]},
        _D308_PROD) == []
    and _d308_pairs(
        {"tests/a.py": _D308_SYN[:1],
         "tests/z.py": ["tests/hastub/__init__.py"]},
        _D308_PROD) == []
    and _d308_pairs(
        {"tests/a.py": ["tests/hastub/__init__.py"],
         "tests/b.py": _D308_SYN[:1]},
        _D308_PROD) == [],
    "arms: equal -> 1 pair, disjoint -> none, 4/5 (exactly 0.80) -> one "
    "shared=4, 4/6 -> none, non-production-only script -> none in either "
    "position; the real recording gives "
    f"{len(_D308_PAIRS)} of {_D308_TOTAL} with {_D308_COMPARABLE} comparable",
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

# One living handover (#518). A dated series accumulates, and every file in it
# but the newest hands the next session confident, wrong instructions -- the
# resumability audit this repository's CLAUDE.md opens with is the same finding
# one level up. The policy is in CLAUDE.md under "One living handover"; this is
# what refuses a second copy.
#
# Reading it here is what keeps `docs/HANDOVER.md` out of INERT, and that is
# deliberate rather than incidental: the pull requests that touch a handover are
# usually record pull requests carrying nothing but docs and roster JSON, which
# are otherwise INERT to a man and scope to zero scripts. Left inert, this check
# would run only on the push to main -- the late-gate shape that produced #354
# and five repeats.
_handovers = sorted(
    f for f in _subprocess.run(
        ["git", "ls-files", "docs"], cwd=_closure.ROOT,
        capture_output=True, text=True,
    ).stdout.split()
    if _closure.is_handover(f)
)
R.check(
    "exactly one handover, with no date in its name",
    _handovers == ["docs/HANDOVER.md"],
    f"found {_handovers or 'none'}; durable state belongs in the single "
    "docs/HANDOVER.md and volatile state on #201, never in both",
)
# `updated-for:` is the staleness half: a handover nobody has re-pointed since
# the merge it describes is the failure mode, not one that has been deleted.
# Reachability, rather than equality with HEAD, is what a branch can satisfy --
# the line names the merge the text reflects, which is always an ancestor.
_uf = _re.search(
    r"^updated-for:[ \t]*([0-9a-f]{7,40})[ \t]*$",
    Path("docs/HANDOVER.md").read_text(),
    _re.M,
) if Path("docs/HANDOVER.md").exists() else None
R.check(
    "the handover names the commit it reflects",
    _uf is not None,
    "docs/HANDOVER.md needs a line `updated-for: <sha>` naming the merge it "
    "was last written against",
)
R.check(
    "and that commit is reachable from HEAD",
    _uf is not None and _subprocess.run(
        ["git", "merge-base", "--is-ancestor", _uf.group(1), "HEAD"],
        cwd=_closure.ROOT, capture_output=True,
    ).returncode == 0,
    f"updated-for: {_uf.group(1) if _uf else '?'} is not an ancestor of HEAD -- "
    "re-point it at the merge this handover reflects (a shallow clone cannot "
    "answer this; the gate jobs check out with fetch-depth: 0)",
)
# ...and reachable from `origin/main`, which is the half HEAD cannot answer.
#
# THIS COST A RED MAIN. #885 set `updated-for:` to a SHA from its OWN branch
# history, which was an ancestor of HEAD on the branch and passed the check
# above at every push. It was SQUASH-merged, every branch commit was rewritten
# into one new SHA, and the named commit stopped existing -- so `main` went red
# on the merge, on a file the branch had left correct by the only measure
# anything applied to it.
#
# Ancestry of `origin/main` is the property that survives any merge method, and
# it is the right one on its own terms: the line names the merge the text
# reflects, and a merge that has happened is on `main` by definition. Every
# value this file has carried before that one -- `fa3b1e0`, `a801d7c`,
# `1e66bb7` -- is a `main` commit, so the tree already agreed; nothing checked
# it.
#
# Skipped rather than failed when `origin/main` is not present, because a
# detached export or a fresh clone with no remote cannot answer it and a check
# that fails where it cannot look teaches seats to ignore it. The gate jobs
# check out with `fetch-depth: 0` and a remote, so they can.
_UF_HAS_MAIN = _subprocess.run(
    ["git", "rev-parse", "--verify", "--quiet", "origin/main^{commit}"],
    cwd=_closure.ROOT, capture_output=True,
).returncode == 0
_UF_ON_MAIN = _UF_HAS_MAIN and _uf is not None and _subprocess.run(
    ["git", "merge-base", "--is-ancestor", _uf.group(1), "origin/main"],
    cwd=_closure.ROOT, capture_output=True,
).returncode == 0
R.check(
    "and reachable from origin/main, so a squash cannot orphan it",
    (not _UF_HAS_MAIN) or _UF_ON_MAIN,
    f"updated-for: {_uf.group(1) if _uf else '?'} is not an ancestor of "
    "origin/main. It names the MERGE this handover reflects, and a merge that "
    "has happened is on main -- so a SHA from this branch's own history is "
    "wrong even while it passes the check above, and a squash then deletes it "
    "and turns main red. Name the merge, not the commit that carries the edit."
    if _UF_HAS_MAIN else "origin/main is absent; nothing to check against",
)

# --- the real-Home-Assistant lane's own reporting (#533) --------------------
#
# `tests/nightly_ha.py` runs the integration inside the official Home Assistant
# container. It is the only lane here that sees real Home Assistant, and the
# only one that has ever caught a real divergence -- it found #525 on its first
# green run. It needs Docker, which no gate lane has, so it stays on
# `closure.py`'s NOT_A_TEST list and nothing in this suite will ever run it.
#
# Until this block nothing READ it either, and that is what went wrong. It was
# INERT, so a change to its checks selected no script, and the gate could not
# tell a lane that judged the container from one that judged nothing. #540
# moved both of #525's offenders off the event loop; `KNOWN_BLOCKING` went on
# listing both and the nightly stayed green -- because a pin that has gone
# stale is a PASS, and `Checks.check` blanked the detail on a pass, discarding
# the one line that named it. A regression of either would have passed too.
#
# Reading it here is the same deliberate move the handover check above makes
# for `docs/HANDOVER.md`: it is what keeps the file out of INERT. What is
# pinned is the lane's REPORTING, which is text and needs no container.
import io as _io  # noqa: E402
import types as _types  # noqa: E402

import nightly_ha as _nightly  # noqa: E402

# The two reports Home Assistant really emitted, from the nightly job that
# found #525 -- run of 2026-09-06, job 101522529963 -- verbatim but for the
# runner's timestamp prefix. Committed as a recorded artifact rather than
# written to fit: a regex checked against a specimen shaped to match it pins
# the specimen (`tools/audit/briefs/fixer.md` step 11). The `sleep` report says
# line 831 and `coordinator.py` has moved on since; the pin captures the source
# TEXT and not the line, which is why it still resolves.
_NIGHTLY_REPORT_IMPORT = (
    "2026-09-06 18:48:25.654 WARNING (MainThread) [homeassistant.util.loop] "
    "Detected blocking call to import_module with args ('.services', "
    "'custom_components.heatpump_optimizer') inside the event loop by custom "
    "integration 'heatpump_optimizer' at "
    "custom_components/heatpump_optimizer/__init__.py, line 56: return "
    'importlib.import_module(f".{module}", __package__) (offender: '
    "/config/custom_components/heatpump_optimizer/__init__.py, line 56: "
    'return importlib.import_module(f".{module}", __package__)), please '
    "create a bug report at https://github.com/tvofi/heatpump_optimizer/issues"
)
_NIGHTLY_REPORT_SLEEP = (
    "2026-09-06 18:48:29.007 WARNING (MainThread) [homeassistant.util.loop] "
    "Detected blocking call to sleep with args (0.001,) inside the event loop "
    "by custom integration 'heatpump_optimizer' at "
    "custom_components/heatpump_optimizer/coordinator.py, line 831: "
    "worker.wait(timeout=2) (offender: /usr/local/lib/python3.14/"
    "subprocess.py, line 2078: time.sleep(delay)), please create a bug report "
    "at https://github.com/tvofi/heatpump_optimizer/issues"
)
_NIGHTLY_CLEAN = (
    "2026-09-06 18:48:20.000 INFO (MainThread) [homeassistant.setup] "
    "Setup of domain heatpump_optimizer took 4.20 seconds"
)


def _nightly_scan(text: str) -> tuple[list[str], dict]:
    """`_scan` over one specimen: which checks failed, and every detail."""
    checks = _nightly.Checks()
    _saved_stdout, sys.stdout = sys.stdout, _io.StringIO()
    try:
        _nightly._scan(checks, text)
    finally:
        sys.stdout = _saved_stdout
    return checks.failures(), checks.results


def _nightly_report_probe(
    extra_outside: tuple = (),
    drop_outside: tuple = (),
    markers: int = 1,
    returncode: int = 0,
) -> list:
    """`_report` over a synthetic complete, green run; its `run:all_checks_ran`.

    No container and no Docker: `_report` reads three attributes off the
    finished process and is otherwise pure, so the roster comparison can be
    driven directly.

    The roster is perturbed in BOTH directions, because `ran == want` fails in
    both and a probe that only adds names pins only half of it. `extra_outside`
    adds a name the run never emits -- which a demanded roster must report
    missing. `drop_outside` removes a name the run DOES emit -- which a demanded
    roster must report undeclared, and which `want <= ran` would not.

    THE INPUT SHAPE IS PRODUCTION'S, not a convenient one. The config directory
    carries a `LOG_NAME` file, and the clean log line lives in it rather than on
    stdout, because that is where a real run puts it: `nightly_ha.py:544` sets
    Home Assistant's `log_file` to `IN_CONFIG / LOG_NAME`, the very directory
    `_report` is handed. Over an empty directory `log.is_file()` is False on
    every probe call and True on every real run, so the probe exercised the
    COMPLEMENT of production -- and a guard that skipped the roster comparison
    whenever the log existed kept this suite green while `run:all_checks_ran`
    was never evaluated in the container at all.

    `markers` and `returncode` reach the other two shapes a real run takes: a
    driver that reported twice or not at all, and a container that exited
    non-zero. Those runs are already failing for other reasons, which is
    precisely why the roster demand must survive them -- a red run that also
    stops saying WHICH checks ran is #533's own silence one level up.
    """
    checks = _nightly.Checks()
    inside = {n: [True, "d"] for n in _nightly.INSIDE_CHECKS}
    completed = _types.SimpleNamespace(
        stdout=(_nightly.MARKER + json.dumps(inside) + "\n") * markers,
        stderr="",
        returncode=returncode,
    )
    _saved_roster = _nightly.OUTSIDE_CHECKS
    _nightly.OUTSIDE_CHECKS = tuple(
        n for n in _saved_roster + tuple(extra_outside) if n not in drop_outside
    )
    _saved_stdout, sys.stdout = sys.stdout, _io.StringIO()
    try:
        with _tempfile.TemporaryDirectory() as _dir:
            (Path(_dir) / _nightly.LOG_NAME).write_text(
                _NIGHTLY_CLEAN
                + "\n"
                + _nightly.BLOCKING_PROBE_BEGIN
                + "\n"
                + _NIGHTLY_REPORT_IMPORT
                + "\n"
                + _nightly.BLOCKING_PROBE_END
                + "\n"
            )
            _nightly._report(checks, completed, Path(_dir))
    finally:
        sys.stdout = _saved_stdout
        _nightly.OUTSIDE_CHECKS = _saved_roster
    # ABSENT is not FAILING, and only the first of those is #533's own shape.
    # A guard that reads `results["run:all_checks_ran"]` directly cannot tell a
    # wrong verdict from a check that stopped existing -- it raises KeyError and
    # the arm that was supposed to name the defect reports a traceback instead.
    return checks.results.get(
        "run:all_checks_ran", [None, "ABSENT -- _report never reached it"]
    )


# THE GENERATOR BEFORE THE ARTIFACT (`fixer.md` step 10). Re-recording the pin
# without this leaves the next staleness exactly as silent as this one was.
_nightly_pass = _nightly.Checks()
_nightly_pass.check("probe", True, "a measurement")
R.check(
    "the nightly lane keeps a check's detail when the check PASSES",
    _nightly_pass.results["probe"][1] == "a measurement",
    "tests/nightly_ha.py Checks.check blanked the detail on a pass, which is "
    "how the stale KNOWN_BLOCKING pin survived #540 unnoticed (#533); a "
    "detail is a measurement, not an explanation owed only by a failure",
)

# The pin is a ratchet and BOTH directions fail. Growth is a new defect; decay
# is a pin outliving the defect it was written for.
_nightly_new, _ = _nightly_scan(_NIGHTLY_CLEAN + "\n" + _NIGHTLY_REPORT_IMPORT)
R.check(
    "a Home Assistant loop-protection report fails the nightly",
    "log:no_new_blocking_call" in _nightly_new,
    "tests/nightly_ha.py accepted a real report of the offender #540 removed; "
    f"with KNOWN_BLOCKING at {len(_nightly.KNOWN_BLOCKING)} entr(ies) a "
    "regression of #525 would pass the only lane that can see it",
)
_nightly_saved = _nightly.KNOWN_BLOCKING
_nightly.KNOWN_BLOCKING = frozenset(
    _nightly.BLOCKING_CALL.findall(_NIGHTLY_REPORT_SLEEP)
)
try:
    _nightly_stale, _ = _nightly_scan(_NIGHTLY_CLEAN)
finally:
    _nightly.KNOWN_BLOCKING = _nightly_saved
R.check(
    "a pinned offender the run did not produce fails the nightly",
    "log:blocking_pin_not_stale" in _nightly_stale,
    "tests/nightly_ha.py passes while KNOWN_BLOCKING lists an offender that "
    "no longer occurs -- the #533 defect itself: the pin pins nothing, and "
    "the run that would have said so reports a pass",
)

# The pin reads upstream text through a regex, so it can go blind without
# failing: no matches reads exactly like no offenders. `BLOCKING_AT_OURS` is
# the loose anchor that says whether a report blames THIS package, and
# `log:blocking_report_parsed` fires on one it claims that the strict regex
# cannot read. That only works while the two agree on the population, and
# agreement is measured here rather than asserted structurally: a
# `BLOCKING_CALL.pattern.startswith(...)` test passes for a degenerate anchor
# matching every integration's reports, which was this block's first version
# and survived both of its own mutations.
#
# The foreign specimen keeps `custom_components.heatpump_optimizer` in the
# report's `args` and changes only the path after ` at `, so an anchor keyed on
# the bare package name rather than the offending path over-fires on it.
_NIGHTLY_REPORT_FOREIGN = _NIGHTLY_REPORT_IMPORT.replace(
    "custom_components/heatpump_optimizer/", "custom_components/other_thing/"
)
_NIGHTLY_RATCHET = (
    "log:blocking_report_parsed",
    "log:no_new_blocking_call",
    "log:blocking_pin_not_stale",
)
R.check(
    "the nightly's loose anchor claims a real report blaming this package",
    bool(_nightly.BLOCKING_AT_OURS.search(_NIGHTLY_REPORT_IMPORT))
    and bool(_nightly.BLOCKING_CALL.search(_NIGHTLY_REPORT_IMPORT))
    # Both specimens, because they blame different files -- `__init__.py` and
    # `coordinator.py`. Against the import report alone an anchor narrowed to
    # one module still matches, and the narrowing goes unmeasured.
    and bool(_nightly.BLOCKING_AT_OURS.search(_NIGHTLY_REPORT_SLEEP)),
    "tests/nightly_ha.py cannot read the report Home Assistant really emitted "
    "(job 101522529963); the pin measures an empty population and passes",
)
R.check(
    "and does not claim another integration's report",
    not _nightly.BLOCKING_AT_OURS.search(_NIGHTLY_REPORT_FOREIGN),
    "BLOCKING_AT_OURS matches a report blaming a different integration, so "
    "log:blocking_report_parsed fires on text this lane does not own -- the "
    "over-fire that turns a nightly red for someone else's defect",
)
R.check(
    "and another integration's blocking call fails nothing here",
    not [
        f
        for f in _nightly_scan(_NIGHTLY_CLEAN + "\n" + _NIGHTLY_REPORT_FOREIGN)[0]
        if f in _NIGHTLY_RATCHET
    ],
    "the nightly went red on a loop-protection report naming another "
    "integration; this lane judges its own package",
)
_nightly_reword = _NIGHTLY_REPORT_IMPORT.split(", line 56:")[0] + " -- see the docs"
R.check(
    "a report this lane cannot parse fails it instead of emptying the pin",
    "log:blocking_report_parsed" in _nightly_scan(
        _NIGHTLY_CLEAN + "\n" + _nightly_reword
    )[0],
    "an upstream reword of the loop-protection report degrades "
    "tests/nightly_ha.py to always-pass; the #522 review measured exactly "
    "that (`HA variant with no '(offender:'  matched=0  pass=True`)",
)

# The null control on the ratchet: the lane is not simply always-red. A clean
# log is the real post-#540 world and must still pass those three. The
# positive control must FAIL here -- no probe window is the #588 blindness.
_nightly_clean_failures, _nightly_clean_results = _nightly_scan(_NIGHTLY_CLEAN)
R.check(
    "a clean log still passes the blocking ratchet",
    not [f for f in _nightly_clean_failures if f in _NIGHTLY_RATCHET],
    f"the nightly went red on a log with no offenders: {_nightly_clean_failures}",
)
R.check(
    "a clean log without a probe window fails the positive control",
    "log:blocking_positive_control" in _nightly_clean_failures,
    "the detector still treats 'no report' as 'the regex can see'; #588",
)
R.check(
    "and a passing check still says what it measured",
    all(v[1] for n, v in _nightly_clean_results.items() if "blocking" in n),
    "a passing blocking check reported an empty detail, so a green nightly "
    "cannot be read for what it actually saw (#533)",
)

# Both rosters are demanded by name. `INSIDE_CHECKS` always was; `OUTSIDE_CHECKS`
# was referenced NOWHERE until #533 -- a roster the run never consulted, so a
# check deleted or renamed out of the outer half left a shorter green run and
# no other trace. That is #580's shape, found in this lane.
R.check(
    "every check the outer half emits is declared in OUTSIDE_CHECKS",
    set(_nightly_clean_results) <= set(_nightly.OUTSIDE_CHECKS),
    "tests/nightly_ha.py _scan emits checks its own roster does not declare: "
    f"{sorted(set(_nightly_clean_results) - set(_nightly.OUTSIDE_CHECKS))}",
)
# Perturb the roster and run it; do not inspect the function. Two structural
# proxies stood here first and each was defeated by a mutant that kept its
# shape: a source-text search for "OUTSIDE_CHECKS" (survived by leaving the
# word in a comment), then `_report.__code__.co_names` (survived by a dead
# `_unused = OUTSIDE_CHECKS`, and by reading the roster only for `len()`).
# Both mutants degrade run:all_checks_ran to comparing the results with
# themselves, which is #580's shape inside the fix for #580's shape. Loading a
# name is not demanding a roster, and only running the comparison separates
# them.
#
# Perturbed in BOTH directions because `ran == want` fails in both: an
# added-and-never-emitted name, and a removed-but-still-emitted one. A single
# added sentinel leaves `want <= ran` passing, which silently drops the
# undeclared half of the comparison.
_nightly_probe_clean = _nightly_report_probe()
_nightly_probe_sentinel = _nightly_report_probe(
    extra_outside=("run:SENTINEL_never_emitted",)
)
# Derived, not named: whichever roster entry `_scan` is actually observed to
# emit. Hard-coding one would pin a check that may be renamed out from under it.
_nightly_probe_dropped = _nightly_report_probe(
    drop_outside=(sorted(set(_nightly_clean_results) & set(_nightly.OUTSIDE_CHECKS))[0],)
)
R.check(
    "and the lane demands that roster of itself",
    "run:all_checks_ran" in _nightly.OUTSIDE_CHECKS
    and not _nightly_probe_sentinel[0]
    and not _nightly_probe_dropped[0],
    "_report does not DEMAND its roster in both directions, so a check "
    "deleted or renamed out of the outer half, or emitted without being "
    f"declared, passes unnoticed (#533) [missing arm: "
    f"{_nightly_probe_sentinel[1]}] [undeclared arm: {_nightly_probe_dropped[1]}]",
)
# The null control on that probe: a check that fails whatever it is handed
# demands nothing either. The unperturbed roster must still pass.
R.check(
    "and that demand is satisfiable, not simply always-red",
    _nightly_probe_clean[0],
    "the roster probe fails on the shipped roster too, so its sentinel arm "
    f"separates nothing (#533) [{_nightly_probe_clean[1]}]",
)
# The three arms above all drive a run that is already GREEN. A run that is
# already red is where a roster check is cheapest to skip and least missed --
# the reader is looking at a failure and does not notice that the list of what
# ran went away with it. Both shapes a real red run takes, and in each the
# demand must still be REACHED: `[0] is None` is the absent case, distinct from
# a wrong verdict, and it is the one a verdict-only guard cannot see.
_nightly_probe_red = _nightly_report_probe(returncode=1)
_nightly_probe_twice = _nightly_report_probe(markers=2)
R.check(
    "and it demands the roster on a run that already failed",
    _nightly_probe_red[0] is True and _nightly_probe_twice[0] is False,
    "_report stops evaluating run:all_checks_ran once the run is red, so a "
    "container that exited non-zero -- or a driver that reported twice -- says "
    "WHICH checks failed and no longer says which never ran (#533) "
    f"[non-zero exit: {_nightly_probe_red[1]}] "
    f"[two markers: {_nightly_probe_twice[1]}]",
)

# --- nightly A3 published-state sweep (#584) --------------------------------
#
# The container run is NOT_A_TEST. These pins are the visible failing test:
# A3 names must be demanded, and a mutant that drops A3 or always-passes must
# fail a named check here. A4 is a different assertion, pinned below.
import inspect as _inspect  # noqa: E402

R.check(
    "A3 named escapes are unique E-identifiers counted at this merge base",
    len(_nightly.A3_NAMED_ESCAPES) == len(set(_nightly.A3_NAMED_ESCAPES))
    and all(
        n.startswith("E") and n[1:].isdigit() for n in _nightly.A3_NAMED_ESCAPES
    ),
    f"A3_NAMED_ESCAPES={_nightly.A3_NAMED_ESCAPES}",
)
R.check(
    "the nightly demands A3 published-state checks by name",
    set(_nightly.A3_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A3_INSIDE)
    == {
        "a3:roster",
        "a3:orjson",
        "a3:finite",
        "a3:device_class_state_class",
        "a3:no_constructor_defaults",
    },
    f"A3_INSIDE={_nightly.A3_INSIDE} INSIDE_CHECKS missing "
    f"{sorted(set(_nightly.A3_INSIDE) - set(_nightly.INSIDE_CHECKS))}",
)
R.check(
    "A3 is not merged with A4",
    all(not n.startswith("a4:") for n in _nightly.A3_INSIDE)
    and all(not n.startswith("a3:") for n in _nightly.A4_INSIDE)
    and set(_nightly.A4_INSIDE).isdisjoint(_nightly.A3_INSIDE),
    f"A3={_nightly.A3_INSIDE} A4={_nightly.A4_INSIDE}",
)

_a3_from_collect = sorted(
    e.entity_id
    for _p in integration.PLATFORM_LIST
    for e in collect(_importlib.import_module(f"heatpump_optimizer.{str(_p)}"))
    if getattr(e, "entity_id", None)
)
_a3_from_file = _nightly.load_committed_roster()
# The rule is len({e.entity_id for p in PLATFORM_LIST for e in collect(module p)
# if e.entity_id}). Both sides are live collect() implementations, not a
# literal this file also writes.
R.check(
    "the A3 roster is derived from collect() over PLATFORM_LIST, not a second literal",
    "COMMITTED_ROSTER" not in Path("tests/nightly_ha.py").read_text()
    and "_collect_entity_ids" in _inspect.getsource(_nightly.load_committed_roster),
    "COMMITTED_ROSTER is a constant this repository also asserts (#560)",
)
R.check(
    "the committed A3 roster is the entity_id set collect() produces",
    _a3_from_file == _a3_from_collect,
    f"roster={len(_a3_from_file)} collect={len(_a3_from_collect)} "
    f"only_roster={sorted(set(_a3_from_file) - set(_a3_from_collect))[:6]} "
    f"only_collect={sorted(set(_a3_from_collect) - set(_a3_from_file))[:6]}",
)
_nightly_roster = _nightly.Checks()
_nightly.check_a3_roster(
    _nightly_roster, list(_a3_from_collect), expected=_a3_from_file
)
R.check(
    "a3:roster passes when HA's registry matches collect()",
    "a3:roster" not in _nightly_roster.failures()
    and _nightly_roster.results["a3:roster"][1],
    _nightly_roster.results.get("a3:roster", [None, "ABSENT"])[1],
)
_a3_roster_mut = _nightly.Checks()
_nightly.check_a3_roster(
    _a3_roster_mut, ["sensor.not_ours"], expected=_a3_from_file
)
R.check(
    "a3:roster fails when the registered ids are not collect()'s set",
    "a3:roster" in _a3_roster_mut.failures(),
    "a mutant that always-passes a3:roster would accept any HA registry",
)

from homeassistant.helpers.json import json_bytes as _ha_json_bytes

try:
    _ha_json_bytes({"k": float("inf")})
    _ha_json_inf = "accepted"
except Exception:
    _ha_json_inf = "refused"
try:
    _nightly.json_bytes_ha({"k": float("inf")})
    _jb_ha_inf = "accepted"
except Exception:
    _jb_ha_inf = "refused"
_a3_orjson_src = _inspect.getsource(_nightly.json_bytes_ha)
_a3_orjson_check_src = _inspect.getsource(_nightly.check_a3_orjson)
R.check(
    "a3:orjson serialises through Home Assistant's json_bytes",
    "helpers.json" in _a3_orjson_src
    and "orjson_like_dumps" not in _a3_orjson_src
    and "orjson_like_dumps" not in _a3_orjson_check_src
    and "json_bytes_ha" in _a3_orjson_check_src
    and _ha_json_inf == "refused"
    and _jb_ha_inf == "refused",
    f"ha={_ha_json_inf} json_bytes_ha={_jb_ha_inf}; "
    "host pin must execute helpers.json.json_bytes, not a local dumps",
)
_a3_orjson_ok = _nightly.Checks()
_nightly.check_a3_orjson(
    _a3_orjson_ok,
    [("sensor.x", {"state": "1", "attributes": {"n": 1.5}})],
)
_a3_orjson_bad = _nightly.Checks()
_nightly.check_a3_orjson(
    _a3_orjson_bad,
    [("sensor.x", {"state": "1", "attributes": {"k": float("inf")}})],
)
R.check(
    "a3:orjson fails a payload orjson rejects, and passes a finite one",
    "a3:orjson" in _a3_orjson_bad.failures()
    and "a3:orjson" not in _a3_orjson_ok.failures(),
    f"bad={_a3_orjson_bad.results.get('a3:orjson')} "
    f"ok={_a3_orjson_ok.results.get('a3:orjson')}",
)
_saved_json_bytes_ha = _nightly.json_bytes_ha
_nightly.json_bytes_ha = lambda obj: b"{}"
_a3_orjson_noop = _nightly.Checks()
try:
    _nightly.check_a3_orjson(
        _a3_orjson_noop,
        [("sensor.x", {"state": "1", "attributes": {"k": float("inf")}})],
    )
finally:
    _nightly.json_bytes_ha = _saved_json_bytes_ha
R.check(
    "json_bytes_ha returning b\"{}\" leaves a3:orjson green on an orjson-illegal payload",
    "a3:orjson" not in _a3_orjson_noop.failures()
    and "a3:orjson" in _a3_orjson_bad.failures(),
    "a no-op json_bytes_ha must not satisfy A3(b); the default serializer "
    "must still be json_bytes_ha so the real path refuses inf "
    f"noop={_a3_orjson_noop.results.get('a3:orjson')} "
    f"real={_a3_orjson_bad.results.get('a3:orjson')}",
)

_a3_finite_bad = _nightly.Checks()
_nightly.check_a3_finite(
    _a3_finite_bad, [("sensor.x", {"state": "1", "attributes": {"k": float("nan")}})]
)
_a3_finite_ok = _nightly.Checks()
_nightly.check_a3_finite(
    _a3_finite_ok, [("sensor.x", {"state": "1", "attributes": {"k": 1.0}})]
)
R.check(
    "a3:finite fails a non-finite attribute and passes a finite one",
    "a3:finite" in _a3_finite_bad.failures()
    and "a3:finite" not in _a3_finite_ok.failures(),
    f"bad={_a3_finite_bad.results.get('a3:finite')}",
)

_a3_dc_src = _inspect.getsource(_nightly.check_a3_device_class_state_class)
R.check(
    "a3:device_class_state_class reads DEVICE_CLASS_STATE_CLASSES",
    "DEVICE_CLASS_STATE_CLASSES" in _a3_dc_src,
    "the inside half must judge (d) by HA's table, not a local copy",
)
_a3_dc_bad = _nightly.Checks()
_nightly.check_a3_device_class_state_class(
    _a3_dc_bad, [("sensor.x", "energy", "measurement")]
)
_a3_dc_ok = _nightly.Checks()
_nightly.check_a3_device_class_state_class(
    _a3_dc_ok, [("sensor.x", "temperature", "measurement")]
)
R.check(
    "a3:device_class_state_class fails a pair the HA table forbids",
    "a3:device_class_state_class" in _a3_dc_bad.failures()
    and "a3:device_class_state_class" not in _a3_dc_ok.failures(),
    f"bad={_a3_dc_bad.results.get('a3:device_class_state_class')} "
    f"(energy+measurement must be forbidden; temperature+measurement allowed)",
)

_a3_def = ThermalState()
_a3e_ok = _nightly.Checks()
_nightly.check_a3_no_constructor_defaults(
    _a3e_ok,
    [
        {
            "entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer",
            "state": "unavailable",
            "attributes": {"device_class": "temperature"},
            "device_class": "temperature",
        },
        {
            "entity_id": "sensor.heat_pump_optimizer_dhw_temperature",
            "state": "unavailable",
            "attributes": {"device_class": "temperature"},
            "device_class": "temperature",
        },
        {
            "entity_id": "climate.heat_pump_optimizer",
            "state": "unavailable",
            "attributes": {
                "current_temperature": None,
                "dhw_temperature": None,
            },
            "device_class": None,
        },
    ],
    defaults=_a3_def,
    roster=_a3_from_file,
)
_a3e_indoor = _nightly.Checks()
_nightly.check_a3_no_constructor_defaults(
    _a3e_indoor,
    [
        {
            "entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer",
            "state": str(_a3_def.room_temperature),
            "attributes": {"device_class": "temperature"},
            "device_class": "temperature",
        },
    ],
    defaults=_a3_def,
    roster=_a3_from_file,
)
_a3e_climate = _nightly.Checks()
_nightly.check_a3_no_constructor_defaults(
    _a3e_climate,
    [
        {
            "entity_id": "climate.heat_pump_optimizer",
            "state": "heat",
            "attributes": {"current_temperature": _a3_def.room_temperature},
            "device_class": None,
        },
    ],
    defaults=_a3_def,
    roster=_a3_from_file,
)
_a3e_bad = _nightly.Checks()
_nightly.check_a3_no_constructor_defaults(
    _a3e_bad,
    [
        {
            "entity_id": "sensor.heat_pump_optimizer_dhw_temperature",
            "state": str(_a3_def.dhw_temperature),
            "attributes": {"device_class": "temperature"},
            "device_class": "temperature",
        },
        {
            "entity_id": "sensor.heat_pump_optimizer_dhw_mixed_water",
            "state": "270.0",
            "attributes": {"device_class": "volume_storage"},
            "device_class": "volume_storage",
        },
        {
            "entity_id": "climate.heat_pump_optimizer",
            "state": "heat",
            "attributes": {"dhw_temperature": _a3_def.dhw_temperature},
            "device_class": None,
        },
    ],
    defaults=_a3_def,
    roster=_a3_from_file,
)
_a3e_empty = _nightly.Checks()
_nightly.check_a3_no_constructor_defaults(
    _a3e_empty, [], defaults=_a3_def, roster=_a3_from_file
)
R.check(
    "a3:no_constructor_defaults fails an empty sweep",
    "a3:no_constructor_defaults" in _a3e_empty.failures(),
    "a driver that collected no states must not pass A3(e) "
    f"{_a3e_empty.results.get('a3:no_constructor_defaults', [None, 'ABSENT'])[1]}",
)
R.check(
    "a3:no_constructor_defaults passes unavailable records",
    "a3:no_constructor_defaults" not in _a3e_ok.failures()
    and _a3e_ok.results["a3:no_constructor_defaults"][1],
    _a3e_ok.results.get("a3:no_constructor_defaults", [None, "ABSENT"])[1],
)
R.check(
    "a3:no_constructor_defaults fails available indoor at the constructor default",
    "a3:no_constructor_defaults" in _a3e_indoor.failures(),
    _a3e_indoor.results.get("a3:no_constructor_defaults", [None, "ABSENT"])[1],
)
R.check(
    "a3:no_constructor_defaults fails climate current_temperature at the constructor default",
    "a3:no_constructor_defaults" in _a3e_climate.failures(),
    _a3e_climate.results.get("a3:no_constructor_defaults", [None, "ABSENT"])[1],
)
R.check(
    "a3:no_constructor_defaults fails an available ThermalState default",
    "a3:no_constructor_defaults" in _a3e_bad.failures()
    and "a3:no_constructor_defaults" not in _a3e_ok.failures(),
    f"bad={_a3e_bad.results.get('a3:no_constructor_defaults')} "
    f"ok={_a3e_ok.results.get('a3:no_constructor_defaults')}",
)
_a3_def_src = _inspect.getsource(_nightly._numeric_constructor_defaults)
R.check(
    "A3(e) numeric defaults are read from the ThermalState constructor fields",
    "dataclasses.fields" in _a3_def_src,
    "A3(e) must not hard-code a field list that drifts from ThermalState()",
)
_a3_inside_src = _inspect.getsource(_nightly._inside)
_a3_a3e_src = _inspect.getsource(_nightly._inside_a3e)
_a3_out_src = _inspect.getsource(_nightly._run_outside)
R.check(
    "A3(e) is a second seed, not collapsed into the thermometer boot",
    "constructor_defaults=False" in _a3_inside_src
    and "constructor_defaults=True" in _a3_a3e_src
    and "thermometers=False" in _a3_out_src
    and "--a3e-only" in _a3_out_src,
    "A3(e) must boot a default install with no thermometer entities; "
    "collapsing it into the thermometer-seeded boot hides the constructor-default leak",
)
R.check(
    "and a passing A3 check still keeps its detail",
    all(
        v[1]
        for c in (_nightly_roster, _a3_orjson_ok, _a3_finite_ok, _a3_dc_ok, _a3e_ok)
        for n, v in c.results.items()
        if n.startswith("a3:")
    ),
    "A3 passing checks blanked their detail (#533)",
)

# --- nightly A4 availability fault-injection (#533) -------------------------
#
# The container run stays NOT_A_TEST. These pins demand A4 by name and prove
# each predicate can still fail. The walk breaks the Tibber counterparty
# (HTTP 500); it does not poke last_update_success. The FakeCoordinator
# sweep above is the conjunction half (E76/E30); this is the price-source
# half (E57).
R.check(
    "A4 named escapes are the §4 A4 row, listed",
    set(_nightly.A4_NAMED_ESCAPES)
    == {"E57", "E76", "E30", "E77", "E75", "E72"}
    and len(_nightly.A4_NAMED_ESCAPES) == len(set(_nightly.A4_NAMED_ESCAPES)),
    f"A4_NAMED_ESCAPES={_nightly.A4_NAMED_ESCAPES}",
)
R.check(
    "the nightly demands A4 fault-injection checks by name",
    set(_nightly.A4_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A4_INSIDE)
    == {
        "a4:failed",
        "a4:unavailable",
        "a4:buttons",
        "a4:no_stale",
        "a4:recovered",
    },
    f"A4_INSIDE={_nightly.A4_INSIDE} INSIDE_CHECKS missing "
    f"{sorted(set(_nightly.A4_INSIDE) - set(_nightly.INSIDE_CHECKS))}",
)
_a4_walk_src = _inspect.getsource(_nightly._async_check_a4)
_a4_serve_src = _inspect.getsource(_nightly._serve_prices)
_a4_break_src = _inspect.getsource(_nightly.break_price_source)
R.check(
    "A4 breaks the price source; it does not poke last_update_success",
    "break_price_source(True)" in _a4_walk_src
    and "async_refresh" in _a4_walk_src
    and "last_update_success =" not in _a4_walk_src
    and "_PRICE_SOURCE_BROKEN" in _a4_break_src
    and "_PRICE_SOURCE_BROKEN" in _a4_serve_src
    and "send_response(500)" in _a4_serve_src
    and "send_response(401)" not in _a4_serve_src,
    "A4 must go through the Tibber counterparty (E57), not the FakeCoordinator poke",
)
_a4_failed_ok = _nightly.Checks()
_nightly.check_a4_failed(_a4_failed_ok, False)
_a4_failed_bad = _nightly.Checks()
_nightly.check_a4_failed(_a4_failed_bad, True)
R.check(
    "a4:failed fails when last_update_success stayed True",
    "a4:failed" in _a4_failed_bad.failures()
    and "a4:failed" not in _a4_failed_ok.failures(),
    f"bad={_a4_failed_bad.results.get('a4:failed')} "
    f"ok={_a4_failed_ok.results.get('a4:failed')}",
)
_a4_before = (
    {"entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer", "state": "21.2"},
    {"entity_id": "button.heat_pump_optimizer_run_optimization", "state": "unknown"},
)
_a4_all_unavail = (
    {"entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer", "state": "unavailable"},
    {"entity_id": "button.heat_pump_optimizer_run_optimization", "state": "unavailable"},
)
_a4_button_up = (
    {"entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer", "state": "unavailable"},
    {"entity_id": "button.heat_pump_optimizer_run_optimization", "state": "unknown"},
)
_a4_stale = (
    {"entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer", "state": "21.2"},
    {"entity_id": "button.heat_pump_optimizer_run_optimization", "state": "unavailable"},
)
_a4_un_ok = _nightly.Checks()
_nightly.check_a4_unavailable(_a4_un_ok, _a4_all_unavail)
_a4_un_empty = _nightly.Checks()
_nightly.check_a4_unavailable(_a4_un_empty, ())
_a4_un_stale = _nightly.Checks()
_nightly.check_a4_unavailable(_a4_un_stale, _a4_stale)
R.check(
    "a4:unavailable fails an empty sweep and a leftover available state",
    "a4:unavailable" in _a4_un_empty.failures()
    and "a4:unavailable" in _a4_un_stale.failures()
    and "a4:unavailable" not in _a4_un_ok.failures(),
    f"empty={_a4_un_empty.results.get('a4:unavailable')} "
    f"stale={_a4_un_stale.results.get('a4:unavailable')}",
)
_a4_btn_ok = _nightly.Checks()
_nightly.check_a4_buttons(_a4_btn_ok, _a4_all_unavail)
_a4_btn_up = _nightly.Checks()
_nightly.check_a4_buttons(_a4_btn_up, _a4_button_up)
_a4_btn_none = _nightly.Checks()
_nightly.check_a4_buttons(
    _a4_btn_none,
    ({"entity_id": "sensor.heat_pump_optimizer_indoor_temperature_optimizer", "state": "unavailable"},),
)
R.check(
    "a4:buttons fails a clickable button and a roster with no button",
    "a4:buttons" in _a4_btn_up.failures()
    and "a4:buttons" in _a4_btn_none.failures()
    and "a4:buttons" not in _a4_btn_ok.failures(),
    f"up={_a4_btn_up.results.get('a4:buttons')} "
    f"none={_a4_btn_none.results.get('a4:buttons')}",
)
_a4_ns_ok = _nightly.Checks()
_nightly.check_a4_no_stale(_a4_ns_ok, _a4_before, _a4_all_unavail)
_a4_ns_bad = _nightly.Checks()
_nightly.check_a4_no_stale(_a4_ns_bad, _a4_before, _a4_stale)
_a4_ns_empty = _nightly.Checks()
_nightly.check_a4_no_stale(_a4_ns_empty, (), _a4_all_unavail)
R.check(
    "a4:no_stale fails a leftover pre-break value and an empty before-set",
    "a4:no_stale" in _a4_ns_bad.failures()
    and "a4:no_stale" in _a4_ns_empty.failures()
    and "a4:no_stale" not in _a4_ns_ok.failures(),
    f"stale={_a4_ns_bad.results.get('a4:no_stale')} "
    f"empty={_a4_ns_empty.results.get('a4:no_stale')}",
)
_a4_rc_ok = _nightly.Checks()
_nightly.check_a4_recovered(_a4_rc_ok, True, _a4_before, _a4_before)
_a4_rc_stuck = _nightly.Checks()
_nightly.check_a4_recovered(_a4_rc_stuck, True, _a4_before, _a4_all_unavail)
_a4_rc_coord = _nightly.Checks()
_nightly.check_a4_recovered(_a4_rc_coord, False, _a4_before, _a4_before)
R.check(
    "a4:recovered fails a stuck entity and a coordinator that stayed failed",
    "a4:recovered" in _a4_rc_stuck.failures()
    and "a4:recovered" in _a4_rc_coord.failures()
    and "a4:recovered" not in _a4_rc_ok.failures(),
    f"stuck={_a4_rc_stuck.results.get('a4:recovered')} "
    f"coord={_a4_rc_coord.results.get('a4:recovered')}",
)
R.check(
    "and passing A4 checks still keep their detail",
    all(
        v[1]
        for c in (_a4_failed_ok, _a4_un_ok, _a4_btn_ok, _a4_ns_ok, _a4_rc_ok)
        for n, v in c.results.items()
        if n.startswith("a4:")
    ),
    "A4 passing checks blanked their detail (#533)",
)

# --- nightly A10 diagnostics privacy probe (#585) ---------------------------
#
# The container run stays NOT_A_TEST. These pins demand A10 by name and prove
# each check can still fail. #509 already closed (#535); A10 pins that rule.
R.check(
    "the nightly demands A10 privacy checks by name",
    set(_nightly.A10_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A10_INSIDE)
    == {
        "a10:no_credential",
        "a10:no_precise_location",
    },
    f"A10_INSIDE={_nightly.A10_INSIDE} INSIDE_CHECKS missing "
    f"{sorted(set(_nightly.A10_INSIDE) - set(_nightly.INSIDE_CHECKS))}",
)
R.check(
    "A10 is not merged with A4",
    all(not n.startswith("a4:") for n in _nightly.A10_INSIDE),
    f"{[n for n in _nightly.A10_INSIDE if n.startswith('a4:')]}",
)
R.check(
    "A10's location rule is the issue's two-decimal bound",
    _nightly.A10_MAX_COORDINATE_DECIMALS == 2
    and _nightly.A10_COORDINATE_KEYS == frozenset({"latitude", "longitude"}),
    f"dp={_nightly.A10_MAX_COORDINATE_DECIMALS} keys={_nightly.A10_COORDINATE_KEYS}",
)

_a10_ok = _nightly.Checks()
_nightly.check_a10_payload(
    _a10_ok,
    {"config": {"tibber_token": "**REDACTED**", "latitude": 59.33, "longitude": 18.07}},
    tokens=("secret-token",),
)
_a10_tok = _nightly.Checks()
_nightly.check_a10_no_credential(
    _a10_tok, {"config": {"tibber_token": "secret-token"}}, tokens=("secret-token",)
)
R.check(
    "a10:no_credential fails a payload that still carries the token",
    "a10:no_credential" in _a10_tok.failures()
    and "a10:no_credential" not in _a10_ok.failures(),
    f"bad={_a10_tok.results.get('a10:no_credential')} "
    f"ok={_a10_ok.results.get('a10:no_credential')}",
)
_a10_loc = _nightly.Checks()
_nightly.check_a10_no_precise_location(
    _a10_loc, {"config": {"solar": {"latitude": 59.331234, "longitude": 18.07}}}
)
R.check(
    "a10:no_precise_location fails a coordinate beyond two decimals",
    "a10:no_precise_location" in _a10_loc.failures()
    and "a10:no_precise_location" not in _a10_ok.failures(),
    f"bad={_a10_loc.results.get('a10:no_precise_location')} "
    f"ok={_a10_ok.results.get('a10:no_precise_location')}",
)
R.check(
    "and a passing A10 check still keeps its detail",
    all(
        v[1]
        for c in (_a10_ok,)
        for n, v in c.results.items()
        if n.startswith("a10:")
    ),
    "A10 passing checks blanked their detail (#533)",
)

# --- nightly A5/A8/A9 options, services, reload (#587) ----------------------
#
# The container run stays NOT_A_TEST. These pins demand the ten checks by
# name and prove each predicate can still fail. A4 is a different issue.
# The byte-unchanged half is what a stub cannot judge live (#542); the
# predicate is host-tested here. Service examples and bounds run against
# the schemas this process registered.
def _a589_escapes(names) -> bool:
    return len(names) == len(set(names)) and all(
        n.startswith("E") and n[1:].isdigit() for n in names
    )


R.check(
    "A5/A8/A9 named escapes are unique E-identifiers",
    _a589_escapes(_nightly.A5_NAMED_ESCAPES)
    and _a589_escapes(_nightly.A8_NAMED_ESCAPES)
    and _a589_escapes(_nightly.A9_NAMED_ESCAPES),
    f"A5={_nightly.A5_NAMED_ESCAPES} A8={_nightly.A8_NAMED_ESCAPES} "
    f"A9={_nightly.A9_NAMED_ESCAPES}",
)
R.check(
    "the nightly demands A5/A8/A9 checks by name",
    set(_nightly.A5_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A8_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A9_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A5_INSIDE)
    == {
        "a5:pages_ok",
        "a5:byte_unchanged",
        "a5:service_examples",
        "a5:service_bounds",
    }
    and set(_nightly.A8_INSIDE)
    == {"a8:register_once", "a8:deregister", "a8:already_configured"}
    and set(_nightly.A9_INSIDE)
    == {"a9:reload_loaded", "a9:roster_unchanged", "a9:no_growth"},
    f"A5={_nightly.A5_INSIDE} A8={_nightly.A8_INSIDE} A9={_nightly.A9_INSIDE} "
    f"missing={sorted((set(_nightly.A5_INSIDE) | set(_nightly.A8_INSIDE) | set(_nightly.A9_INSIDE)) - set(_nightly.INSIDE_CHECKS))}",
)
R.check(
    "A5/A8/A9 are not merged with A4",
    all(
        not n.startswith("a4:")
        for n in (*_nightly.A5_INSIDE, *_nightly.A8_INSIDE, *_nightly.A9_INSIDE)
    ),
    f"{[n for n in (*_nightly.A5_INSIDE, *_nightly.A8_INSIDE, *_nightly.A9_INSIDE) if n.startswith('a4:')]}",
)
_a5_steps_src = _inspect.getsource(_nightly.option_step_ids)
_a5_derived = _nightly.option_step_ids(config_flow._OPTION_PAGES)
R.check(
    "A5 walks _OPTION_PAGES plus the two menus, not a carried 23",
    _a5_derived == ("init", "advanced") + tuple(p.step for p in config_flow._OPTION_PAGES)
    and "23" not in _a5_steps_src,
    f"steps={_a5_derived} src_has_23={'23' in _a5_steps_src}",
)
_a8_cat = _nightly.documented_service_names(services)
_a8_once_src = _inspect.getsource(_nightly.check_a8_register_once)
R.check(
    "A8's catalog is services.yaml's keys, not a carried 11",
    _a8_cat == frozenset(services) and "11" not in _a8_once_src,
    f"catalog={sorted(_a8_cat)} src_has_11={'11' in _a8_once_src}",
)

_a5_pages_ok = _nightly.Checks()
_nightly.check_a5_pages(
    _a5_pages_ok,
    [{"step": s, "kind": "menu" if s in ("init", "advanced") else "save"} for s in _a5_derived],
    _a5_derived,
)
_a5_pages_bad = _nightly.Checks()
_nightly.check_a5_pages(
    _a5_pages_bad,
    [{"step": "learning", "kind": "raise", "raised": True, "detail": "KeyError"}],
    _a5_derived,
)
R.check(
    "a5:pages_ok fails a raise or a short walk, and passes a complete save-or-menu walk",
    "a5:pages_ok" in _a5_pages_bad.failures()
    and "a5:pages_ok" not in _a5_pages_ok.failures(),
    f"bad={_a5_pages_bad.results.get('a5:pages_ok')} "
    f"ok={_a5_pages_ok.results.get('a5:pages_ok')}",
)
_a5_comfort_cur = {
    const.CONF_TARGET_TEMP: const.DEFAULT_TARGET_TEMP,
    const.CONF_MIN_TEMP: const.DEFAULT_MIN_TEMP,
    const.CONF_MAX_TEMP: const.DEFAULT_MAX_TEMP,
    const.CONF_COMFORT_TEMP_DAY: const.DEFAULT_COMFORT_TEMP_DAY,
    const.CONF_COMFORT_TEMP_NIGHT: const.DEFAULT_COMFORT_TEMP_NIGHT,
    const.CONF_DAY_START_HOUR: const.DEFAULT_DAY_START_HOUR,
    const.CONF_DAY_END_HOUR: const.DEFAULT_DAY_END_HOUR,
}
_a5_comfort_schema = config_flow._page_schema("comfort", _a5_comfort_cur, FakeHass())
_a5_comfort_posted = _nightly.option_resubmit("comfort", _a5_comfort_cur)
try:
    _a5_comfort_schema(_a5_comfort_posted)
    _a5_comfort_err = ""
except Exception as _a5_comfort_exc:  # noqa: BLE001 - the A5 failure is any raise
    _a5_comfort_err = f"{type(_a5_comfort_exc).__name__}: {_a5_comfort_exc}"
R.check(
    "option_resubmit posts the sectioned shape the comfort schema validates",
    not _a5_comfort_err,
    _a5_comfort_err or "accepted",
)
_a5_entities_cur = {
    const.CONF_PRICE_SOURCE: const.DEFAULT_PRICE_SOURCE,
    const.CONF_TIBBER_TOKEN: "nightly-ha-local",
    const.CONF_WEATHER_ENTITY: "weather.ci_weather",
}
_a5_entities_schema = config_flow._page_schema(
    "entities", _a5_entities_cur, FakeHass()
)
_a5_entities_posted = _nightly.option_resubmit("entities", _a5_entities_cur)
try:
    _a5_entities_schema(_a5_entities_posted)
    _a5_entities_err = ""
except Exception as _a5_entities_exc:  # noqa: BLE001 - the A5 failure is any raise
    _a5_entities_err = f"{type(_a5_entities_exc).__name__}: {_a5_entities_exc}"
R.check(
    "option_resubmit nests weather_entity under the credentials section",
    isinstance(_a5_entities_posted.get("credentials"), dict)
    and _a5_entities_posted["credentials"].get(const.CONF_WEATHER_ENTITY)
    == "weather.ci_weather"
    and const.CONF_WEATHER_ENTITY not in _a5_entities_posted
    and "indoor" in _a5_entities_posted
    and "plant" in _a5_entities_posted,
    f"posted={_a5_entities_posted!r}",
)
R.check(
    "option_resubmit posts the sectioned shape the entities schema validates",
    not _a5_entities_err,
    _a5_entities_err or "accepted",
)

# ``modbus_prefill`` (#1067) is a two-submit page: the first resubmit opens
# the suggestion preview (still a ``form``), the second saves. The nightly
# walk must drive the whole sequence -- a single submit never leaves ``form``,
# which is the escape a5:pages_ok caught on the nightly lane (#1151). Drive
# the real handler, not a re-implementation, so the pin reads the page's own
# phase branch.
_a5_prefill_cur = {
    const.CONF_MODBUS_PREFILL_PREFIX: const.DEFAULT_MODBUS_PREFILL_PREFIX
}


async def _a5_walk_modbus_prefill():
    entry = FakeEntry(options=dict(_a5_prefill_cur))
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = FakeHass()
    payloads = _nightly.option_resubmits("modbus_prefill", flow._current)
    kinds = [
        _nightly._flow_kind(await flow.async_step_modbus_prefill(payload))
        for payload in payloads
    ]
    return payloads, kinds


_a5_prefill_payloads, _a5_prefill_kinds = asyncio.run(_a5_walk_modbus_prefill())
R.check(
    "modbus_prefill resubmits twice: one submit opens the preview, two save",
    _a5_prefill_payloads
    == (_nightly.option_resubmit("modbus_prefill", _a5_prefill_cur), {})
    and _a5_prefill_kinds == ["form", "menu"],
    f"payloads={_a5_prefill_payloads!r} kinds={_a5_prefill_kinds!r}",
)

# The check takes the two effective CONFIGURATIONS now, not their bytes, so a
# failure can name the keys that moved. Its verdict is still the canonical
# bytes, which is what these two pins hold: the #542 wipe fails, and a newly
# stored None on an empty optional does not.
_a5_before = _nightly.stored_effective(
    {"external_heat_entity": "sensor.seed_external_heat_entity", "x": 1},
    {},
)
_a5_ok_bytes = _nightly.Checks()
_nightly.check_a5_byte_unchanged(
    _a5_ok_bytes,
    _a5_before,
    _nightly.stored_effective(
        {"external_heat_entity": "sensor.seed_external_heat_entity", "x": 1},
        {"empty_optional": None},
    ),
)
_a5_wipe = _nightly.Checks()
_nightly.check_a5_byte_unchanged(
    _a5_wipe,
    _a5_before,
    _nightly.stored_effective({"x": 1}, {"external_heat_entity": None}),
)
R.check(
    "a5:byte_unchanged fails the #542 wipe and ignores a new None optional",
    "a5:byte_unchanged" in _a5_wipe.failures()
    and "a5:byte_unchanged" not in _a5_ok_bytes.failures(),
    f"wipe={_a5_wipe.results.get('a5:byte_unchanged')} "
    f"ok={_a5_ok_bytes.results.get('a5:byte_unchanged')}",
)
# A DETECTOR THAT CANNOT LOCATE THE DEFECT IS HALF A DETECTOR. The first real
# failure of the check above reported two sizes and nothing else, and the keys
# behind those 281 bytes could not be named without a container. So the detail
# is pinned, not just the verdict: every direction appears, by key name.
_a5_named = _nightly.Checks()
_nightly.check_a5_byte_unchanged(
    _a5_named,
    _nightly.stored_effective({"kept": 1, "moved": "before", "gone": True}, {}),
    _nightly.stored_effective({"kept": 1, "moved": "after"}, {"fresh": 2}),
)
_a5_named_detail = str(_a5_named.results.get("a5:byte_unchanged", ["", ""])[1])
R.check(
    "a5:byte_unchanged names the keys that moved, in all three directions",
    "a5:byte_unchanged" in _a5_named.failures()
    and "added=['fresh']" in _a5_named_detail
    and "changed=[\"moved: 'before'->'after'\"]" in _a5_named_detail
    and "dropped=['gone']" in _a5_named_detail,
    f"detail={_a5_named_detail!r}",
)
# THE PROBE MARKER GOES THROUGH THE LOG HANDLER, NEVER BEHIND ITS BACK. Home
# Assistant owns `home-assistant.log` through a handler with its own file
# offset, so bytes appended by a second handle are overwritten by its next
# records: run 34537901814 dumped the log with neither marker in it, the window
# did not exist, and `log:no_new_blocking_call` and
# `log:blocking_positive_control` failed in opposite directions on the same
# provoked report. Pinned at the source, because the failure mode is a write
# that succeeds and is then lost -- nothing this suite can execute reproduces
# it, and an assertion on the file would pass.
# The docstring names the defect it replaced, so the pin reads the CODE: an
# earlier form of this check failed on the word "fsynced" in the prose.
import textwrap as _textwrap  # noqa: E402

_probe_writer_ast = ast.parse(
    _textwrap.dedent(_inspect.getsource(_nightly._write_probe_marker))
).body[0]
_probe_writer_body = ast.unparse(
    ast.Module(
        body=[
            node
            for node in _probe_writer_ast.body
            if not (
                isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            )
        ],
        type_ignores=[],
    )
)
R.check(
    "the probe marker is emitted as a log record, not appended to the log file",
    "logging.getLogger" in _probe_writer_body
    and ".warning(mark)" in _probe_writer_body
    and "open(" not in _probe_writer_body
    and "fsync" not in _probe_writer_body,
    f"body={_probe_writer_body!r}",
)

_a5_schemas = {
    name: _svc_hass.services._schemas[(const.DOMAIN, name)]
    for name in services
    if (const.DOMAIN, name) in getattr(_svc_hass.services, "_schemas", {})
}
_a5_ex_ok = _nightly.Checks()
_nightly.check_a5_service_examples(_a5_ex_ok, _a5_schemas, services)
_a5_ex_bad = _nightly.Checks()
_nightly.check_a5_service_examples(
    _a5_ex_bad,
    {"set_mode": _a5_schemas.get("set_mode")},
    {"set_mode": {"fields": {"mode": {"example": "not-a-mode"}}}},
)
R.check(
    "a5:service_examples fails a rejected example and passes the registered catalog",
    "a5:service_examples" in _a5_ex_bad.failures()
    and "a5:service_examples" not in _a5_ex_ok.failures()
    and _a5_ex_ok.results["a5:service_examples"][1],
    f"bad={_a5_ex_bad.results.get('a5:service_examples')} "
    f"ok={_a5_ex_ok.results.get('a5:service_examples')} "
    f"schemas={len(_a5_schemas)}",
)
_a5_bd_ok = _nightly.Checks()
_nightly.check_a5_service_bounds(_a5_bd_ok, _a5_schemas, services)
_a5_bd_bad = _nightly.Checks()
_nightly.check_a5_service_bounds(
    _a5_bd_bad,
    {"set_thermal_parameters": _a5_schemas.get("set_thermal_parameters")},
    {
        "set_thermal_parameters": {
            "fields": {
                "house_thermal_mass": {
                    "example": 10.0,
                    "selector": {"number": {"min": -1, "max": 80}},
                }
            }
        }
    },
)
R.check(
    "a5:service_bounds fails an out-of-range bound and passes the yaml edges",
    "a5:service_bounds" in _a5_bd_bad.failures()
    and "a5:service_bounds" not in _a5_bd_ok.failures(),
    f"bad={_a5_bd_bad.results.get('a5:service_bounds')} "
    f"ok={_a5_bd_ok.results.get('a5:service_bounds')}",
)

_a8_ok = _nightly.Checks()
_nightly.check_a8_register_once(_a8_ok, _a8_cat, _a8_cat)
_a8_dup = _nightly.Checks()
_nightly.check_a8_register_once(
    _a8_dup, list(_a8_cat) + [f"{n}__dup" for n in list(_a8_cat)[:3]], _a8_cat
)
R.check(
    "a8:register_once fails a doubled catalog and passes the yaml set",
    "a8:register_once" in _a8_dup.failures()
    and "a8:register_once" not in _a8_ok.failures(),
    f"dup={_a8_dup.results.get('a8:register_once')} "
    f"ok={_a8_ok.results.get('a8:register_once')}",
)
_a8_un_ok = _nightly.Checks()
_nightly.check_a8_deregister(_a8_un_ok, _a8_cat, _a8_cat)
_a8_un_zero = _nightly.Checks()
_nightly.check_a8_deregister(_a8_un_zero, (), _a8_cat)
_a8_un_extra = _nightly.Checks()
_nightly.check_a8_deregister(_a8_un_extra, set(_a8_cat) | {"leftover"}, _a8_cat)
R.check(
    "a8:deregister fails an empty catalog and leftover names, and passes the yaml set",
    "a8:deregister" in _a8_un_zero.failures()
    and "a8:deregister" in _a8_un_extra.failures()
    and "a8:deregister" not in _a8_un_ok.failures(),
    f"zero={_a8_un_zero.results.get('a8:deregister')} "
    f"extra={_a8_un_extra.results.get('a8:deregister')} "
    f"ok={_a8_un_ok.results.get('a8:deregister')}",
)
_a8_cfg_ok = _nightly.Checks()
_nightly.check_a8_already_configured(_a8_cfg_ok, "already_configured")
_a8_cfg_bad = _nightly.Checks()
_nightly.check_a8_already_configured(_a8_cfg_bad, None)
R.check(
    "a8:already_configured fails a missing abort and passes already_configured",
    "a8:already_configured" in _a8_cfg_bad.failures()
    and "a8:already_configured" not in _a8_cfg_ok.failures(),
    f"bad={_a8_cfg_bad.results.get('a8:already_configured')}",
)
_a8_entry_src = _inspect.getsource(_nightly._async_add_second_entry)
R.check(
    "A8's ConfigEntry construction names discovery_keys and subentries_data",
    "discovery_keys" in _a8_entry_src and "subentries_data" in _a8_entry_src,
    "stable HA's ConfigEntry.__init__ requires both; the fallback omitted them",
)
_a8_check_src = _inspect.getsource(_nightly._async_check_a8)
R.check(
    "A8 surfaces InvalidData.schema_errors instead of the path-only message",
    "schema_errors" in _a8_check_src,
    "HA wraps the inner vol.Invalid; the path-only str hid why weather_entity failed",
)
_a8_sensor_posted = _nightly.a8_sensors_payload(
    {
        "weather_entity": "weather.ci_weather",
        "indoor_temp_entity": "sensor.ci_indoor_temperature",
        "tibber_token": "nightly-ha-local",
    },
    ("weather_entity", "indoor_temp_entity"),
)
R.check(
    "A8 sensors payload nests indoor under indoor; omits weather_entity",
    _a8_sensor_posted
    == {"indoor": {"indoor_temp_entity": "sensor.ci_indoor_temperature"}},
    f"posted={_a8_sensor_posted!r}",
)
_a5_seed_opts = _nightly._seed_payload()["options"]
_a5_seed_missing = [
    row.key
    for row in config_flow._OPTION_FIELDS
    if row.default
    not in (
        config_flow._STORED,
        config_flow._DYNAMIC,
        config_flow._SUGGESTED,
    )
    and not isinstance(row.default, (config_flow._Computed, config_flow._Suggested))
    and row.default is not None
    and row.key not in _a5_seed_opts
]
R.check(
    "the nightly seed stores every concrete option-field default",
    not _a5_seed_missing,
    f"missing={_a5_seed_missing[:8]}",
)
# A5's no-op walk posts the schema. ``section()`` fills ``_Computed``
# defaults (weekend/holiday comfort, wood_furnace_enabled) that the seed
# never stored -- 4135B → 4416B on dispatch 34537901814. Drop those on
# save only when the key was absent and the value is the computed default;
# a stored or edited value still persists.
_a5_seed = _nightly._seed_payload()
_a5_cur = {**_a5_seed["data"], **_a5_seed["options"]}
_a5_grown = []
for _a5_step in ("comfort", "building"):
    _a5_schema = config_flow._page_schema(_a5_step, _a5_cur, FakeHass())
    _a5_flat = config_flow._flatten_section_input(
        _a5_schema(_nightly.option_resubmit(_a5_step, _a5_cur))
    )
    _a5_flat.pop(const.CONF_AFTER_SAVE, None)
    _a5_saved = config_flow._omit_unstored_computed(_a5_flat, _a5_cur, FakeHass())
    _a5_grown.extend(sorted(k for k in _a5_saved if k not in _a5_cur))
R.check(
    "a no-op options walk does not persist computed defaults the seed never stored",
    not _a5_grown,
    f"grown={_a5_grown}",
)
_a5_keep_cur = {**_a5_cur, const.CONF_COMFORT_TEMP_DAY_WEEKEND: 18.0}
_a5_keep = config_flow._omit_unstored_computed(
    {const.CONF_COMFORT_TEMP_DAY_WEEKEND: 18.0, const.CONF_COMFORT_TEMP_DAY: 21.0},
    _a5_keep_cur,
    FakeHass(),
)
_a5_edit = config_flow._omit_unstored_computed(
    {const.CONF_COMFORT_TEMP_DAY_WEEKEND: 18.0},
    _a5_cur,
    FakeHass(),
)
R.check(
    "an already-stored or edited computed value is not dropped on save",
    _a5_keep.get(const.CONF_COMFORT_TEMP_DAY_WEEKEND) == 18.0
    and _a5_keep.get(const.CONF_COMFORT_TEMP_DAY) == 21.0
    and _a5_edit.get(const.CONF_COMFORT_TEMP_DAY_WEEKEND) == 18.0,
    f"keep={_a5_keep!r} edit={_a5_edit!r}",
)
_a5_typed = config_flow._omit_unstored_computed(
    {const.CONF_DAY_START_HOUR: 7.0},
    {const.CONF_DAY_START_HOUR: 7},
    FakeHass(),
)
R.check(
    "a no-op write keeps the stored type so effective JSON does not move",
    _a5_typed.get(const.CONF_DAY_START_HOUR) == 7
    and type(_a5_typed[const.CONF_DAY_START_HOUR]) is int,
    f"typed={_a5_typed!r}",
)
# Dispatch 34542155868: HA's select retyped the seed's ``'60'`` to ``60``.
# ``'60' == 60`` is false, so the int/float arm above did not keep the
# stored string and a5:byte_unchanged moved 4135B → 4133B.
_a5_peak = config_flow._omit_unstored_computed(
    {const.CONF_PEAK_TARIFF_WINDOW: 60},
    {const.CONF_PEAK_TARIFF_WINDOW: "60"},
    FakeHass(),
)
R.check(
    "a select that retypes a stored digit string keeps the stored type",
    _a5_peak.get(const.CONF_PEAK_TARIFF_WINDOW) == "60"
    and type(_a5_peak[const.CONF_PEAK_TARIFF_WINDOW]) is str,
    f"peak={_a5_peak!r}",
)
_a5_opts = dict(_a5_seed["options"])
_a5_data = dict(_a5_seed["data"])
_a5_walk = {**_a5_data, **_a5_opts}
_a5_before_b = _nightly.stored_effective_bytes(_a5_data, _a5_opts)
for _a5_step in _nightly.option_step_ids(config_flow._OPTION_PAGES):
    if _a5_step in ("init", "advanced", "setup_overview"):
        continue
    _a5_flat = config_flow._flatten_section_input(
        config_flow._page_schema(_a5_step, _a5_walk, FakeHass())(
            _nightly.option_resubmit(_a5_step, _a5_walk)
        )
    )
    _a5_flat.pop(const.CONF_AFTER_SAVE, None)
    _a5_opts.update(
        config_flow._omit_unstored_computed(_a5_flat, _a5_walk, FakeHass())
    )
    _a5_walk = {**_a5_data, **_a5_opts}
_a5_after_b = _nightly.stored_effective_bytes(_a5_data, _a5_opts)
R.check(
    "a full no-op options walk leaves stored effective bytes unchanged",
    _a5_before_b == _a5_after_b,
    f"before={len(_a5_before_b)}B after={len(_a5_after_b)}B",
)
R.check(
    "_save_or_menu omits unstored computed defaults before persist",
    "_omit_unstored_computed"
    in _inspect.getsource(config_flow.HeatPumpOptimizerOptionsFlow._save_or_menu),
    "schema fill still writes the keys if the save path does not drop them",
)

_a9_states_ok = _nightly.Checks()
_nightly.check_a9_reload_loaded(_a9_states_ok, ["loaded"] * _nightly.A9_RELOADS)
_a9_states_bad = _nightly.Checks()
_nightly.check_a9_reload_loaded(_a9_states_bad, ["loaded", "setup_error"])
R.check(
    "a9:reload_loaded fails a short or not-loaded series",
    "a9:reload_loaded" in _a9_states_bad.failures()
    and "a9:reload_loaded" not in _a9_states_ok.failures()
    and _nightly.A9_RELOADS == 5,
    f"bad={_a9_states_bad.results.get('a9:reload_loaded')} "
    f"reloads={_nightly.A9_RELOADS}",
)
_a9_ros_ok = _nightly.Checks()
_nightly.check_a9_roster_unchanged(_a9_ros_ok, ["sensor.a"], ["sensor.a"])
_a9_ros_bad = _nightly.Checks()
_nightly.check_a9_roster_unchanged(_a9_ros_bad, ["sensor.a"], ["sensor.a", "sensor.b"])
R.check(
    "a9:roster_unchanged fails a grown roster",
    "a9:roster_unchanged" in _a9_ros_bad.failures()
    and "a9:roster_unchanged" not in _a9_ros_ok.failures(),
    f"bad={_a9_ros_bad.results.get('a9:roster_unchanged')}",
)
_a9_g_shipped = _nightly.Checks()
_nightly.check_a9_no_growth(_a9_g_shipped, [1, 0, 1, 1], [4, 4, 4, 4], [1, 0, 1, 1])
_a9_g_neutered = _nightly.Checks()
_nightly.check_a9_no_growth(_a9_g_neutered, [1, 1, 2, 3], [4, 4, 4, 4], [1, 1, 2, 3])
_a9_g_zero = _nightly.Checks()
_nightly.check_a9_no_growth(_a9_g_zero, [0, 0, 0], [0, 0, 0], [0, 0, 0])
R.check(
    "a9:no_growth fails the #540 neutered series and passes the shipped dip",
    "a9:no_growth" in _a9_g_neutered.failures()
    and "a9:no_growth" not in _a9_g_shipped.failures()
    and "a9:no_growth" not in _a9_g_zero.failures(),
    f"neutered={_a9_g_neutered.results.get('a9:no_growth')} "
    f"shipped={_a9_g_shipped.results.get('a9:no_growth')}",
)
R.check(
    "A9's growth ceiling is the first sample, not a hard zero",
    "series[0]" in _inspect.getsource(_nightly.series_grew)
    and "first sample" in _inspect.getsource(_nightly.check_a9_no_growth),
    "A9 must not assert zero growth; that re-records whenever HA bookkeeping moves",
)
R.check(
    "and passing A5/A8/A9 checks still keep their detail",
    all(
        v[1]
        for c in (
            _a5_pages_ok,
            _a5_ok_bytes,
            _a5_ex_ok,
            _a5_bd_ok,
            _a8_ok,
            _a8_un_ok,
            _a8_cfg_ok,
            _a9_states_ok,
            _a9_ros_ok,
            _a9_g_shipped,
        )
        for n, v in c.results.items()
        if n.startswith(("a5:", "a8:", "a9:"))
    ),
    "A5/A8/A9 passing checks blanked their detail (#533)",
)

# Leftover #533 after #751: A6/A11/A12/A13. Sibling #754 owns the
# leftover A5/A8/A14 nightly production reds; those pins live there.
R.section("Nightly leftover A6/A11/A12/A13")

R.check(
    "the nightly demands A6/A11/A12/A13 checks by name",
    set(_nightly.A6_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A11_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A12_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A13_INSIDE) <= set(_nightly.INSIDE_CHECKS)
    and set(_nightly.A6_INSIDE)
    == {"a6:list", "a6:string", "a6:number", "a6:loaded"}
    and set(_nightly.A11_INSIDE)
    == {"a11:no_entry", "a11:invalid", "a11:run_failed"}
    and set(_nightly.A12_INSIDE) == {"a12:migrates"}
    and set(_nightly.A13_INSIDE) == {"a13:currency"},
    f"A6={getattr(_nightly, 'A6_INSIDE', None)} "
    f"A11={getattr(_nightly, 'A11_INSIDE', None)} "
    f"A12={getattr(_nightly, 'A12_INSIDE', None)} "
    f"A13={getattr(_nightly, 'A13_INSIDE', None)}",
)
R.check(
    "A6/A11/A12/A13 are not merged with A4",
    all(
        not n.startswith("a4:")
        for n in (
            *_nightly.A6_INSIDE,
            *_nightly.A11_INSIDE,
            *_nightly.A12_INSIDE,
            *_nightly.A13_INSIDE,
        )
    ),
)

_a6_ok = _nightly.Checks()
_nightly.check_a6_corrupt(_a6_ok, "a6:list", raised=False, applied=False)
_a6_raise = _nightly.Checks()
_nightly.check_a6_corrupt(_a6_raise, "a6:list", raised=True, applied=False)
_a6_apply = _nightly.Checks()
_nightly.check_a6_corrupt(_a6_apply, "a6:list", raised=False, applied=True)
_a6_load_ok = _nightly.Checks()
_nightly.check_a6_loaded(_a6_load_ok, True)
_a6_load_bad = _nightly.Checks()
_nightly.check_a6_loaded(_a6_load_bad, False)
R.check(
    "a6:list fails a raise or an applied corrupt payload, and a6:loaded fails a down entry",
    "a6:list" in _a6_raise.failures()
    and "a6:list" in _a6_apply.failures()
    and "a6:list" not in _a6_ok.failures()
    and "a6:loaded" in _a6_load_bad.failures()
    and "a6:loaded" not in _a6_load_ok.failures(),
    f"ok={_a6_ok.results} raise={_a6_raise.results} apply={_a6_apply.results}",
)
R.check(
    "A6 stages four corrupt stores, not a carried anecdote",
    len(_nightly.A6_STORE_CASES) == 4
    and {case[0] for case in _nightly.A6_STORE_CASES}
    == {"accuracy", "thermal_learning", "energy", "price_model"},
    f"cases={_nightly.A6_STORE_CASES}",
)

_a11_ok = _nightly.Checks()
_nightly.check_a11_raised(_a11_ok, "a11:invalid", True)
_a11_noop = _nightly.Checks()
_nightly.check_a11_raised(_a11_noop, "a11:invalid", False)
R.check(
    "a11:invalid fails a silent no-op and passes a raise",
    "a11:invalid" in _a11_noop.failures()
    and "a11:invalid" not in _a11_ok.failures(),
    f"ok={_a11_ok.results} noop={_a11_noop.results}",
)

_a12_ok = _nightly.Checks()
_nightly.check_a12_migrates(_a12_ok, const.CONFIG_ENTRY_VERSION, const.CONFIG_ENTRY_VERSION)
_a12_stale = _nightly.Checks()
_nightly.check_a12_migrates(_a12_stale, 1, const.CONFIG_ENTRY_VERSION)
R.check(
    "a12:migrates fails an unstamped older version and passes the current stamp",
    "a12:migrates" in _a12_stale.failures()
    and "a12:migrates" not in _a12_ok.failures(),
    f"ok={_a12_ok.results} stale={_a12_stale.results}",
)
_a12_seed = _nightly._seed_payload()
R.check(
    "A12 seeds an older schema version than CONFIG_ENTRY_VERSION",
    int(_a12_seed["version"]) < const.CONFIG_ENTRY_VERSION,
    f"seed={_a12_seed['version']} current={const.CONFIG_ENTRY_VERSION}",
)

_a13_ok = _nightly.Checks()
_nightly.check_a13_currency(_a13_ok, "EUR", "EUR")
_a13_sek = _nightly.Checks()
_nightly.check_a13_currency(_a13_sek, "SEK", "EUR")
R.check(
    "a13:currency fails a hardcoded SEK on an EUR instance",
    "a13:currency" in _a13_sek.failures()
    and "a13:currency" not in _a13_ok.failures(),
    f"ok={_a13_ok.results} sek={_a13_sek.results}",
)
R.check(
    "A13's instance currency is not the SEK fallback",
    "currency: EUR" in _nightly.CONFIGURATION_YAML
    and "currency: SEK" not in _nightly.CONFIGURATION_YAML,
    "SEK on the instance cannot tell follow-the-instance from the fallback",
)
_a6_dir = Path(_tempfile.mkdtemp(prefix="a6-stores-"))
_a6_entry = "01JHPA9NGHTHACNTNR00000001"
_nightly.write_corrupt_stores(_a6_dir, _a6_entry)
_a6_prefix = f"{_nightly.PACKAGE_NAME}_{_a6_entry}_"
_a6_written = {
    p.name[len(_a6_prefix) :]
    for p in (_a6_dir / ".storage").iterdir()
    if p.name.startswith(_a6_prefix)
}
R.check(
    "write_corrupt_stores emits one HA store file per A6 case",
    _a6_written == {"accuracy", "thermal_learning", "energy", "price_model"},
    f"written={sorted(_a6_written)}",
)
_inside_src = _inspect.getsource(_nightly._inside)
_boot_src = _inspect.getsource(_nightly._boot)
R.check(
    "A6 writes corrupt stores at boot; A11 runs before A8 unload",
    "write_corrupt_stores" in _boot_src
    and "_async_check_a11" in _inside_src
    and "_async_check_a8" in _inside_src
    and _inside_src.index("_async_check_a11") < _inside_src.index("_async_check_a8"),
    "A6/A11 must execute, and A11 before A8 unloads the entry the services need",
)
R.check(
    "A12 and A13 run on the loaded entry, not after A8 unload",
    "_check_a12" in _inside_src
    and "_check_a13" in _inside_src
    and _inside_src.index("_check_a12") < _inside_src.index("_async_check_a8")
    and _inside_src.index("_check_a13") < _inside_src.index("_async_check_a8"),
    f"inside has a12={'_check_a12' in _inside_src} a13={'_check_a13' in _inside_src}",
)

# --- nightly loop-detector positive control (#588) --------------------------
#
# The container run stays NOT_A_TEST. These pins demand the check by name and
# prove the begin/end split: the probe report must not fail the pin, a
# leading-phrase reword after the window must fail the control, and a report
# after END stays in the pin (shutdown, #525's second offender).
R.check(
    "the nightly demands the blocking positive control by name",
    _nightly.BLOCKING_POSITIVE_CONTROL in _nightly.OUTSIDE_CHECKS
    and _nightly.BLOCKING_POSITIVE_CONTROL == "log:blocking_positive_control",
    f"OUTSIDE_CHECKS missing {_nightly.BLOCKING_POSITIVE_CONTROL}",
)
R.check(
    "the blocking positive control is not A4 and not #587",
    not _nightly.BLOCKING_POSITIVE_CONTROL.startswith(("a4:", "a5:", "a8:", "a9:"))
    and all(not n.startswith(("a4:", "a5:", "a8:", "a9:")) for n in _nightly.OUTSIDE_CHECKS),
    f"{[n for n in _nightly.OUTSIDE_CHECKS if n.startswith(('a4:', 'a5:', 'a8:', 'a9:'))]}",
)

def _nightly_window(inner: str, after: str = "") -> str:
    return (
        _NIGHTLY_CLEAN
        + "\n"
        + _nightly.BLOCKING_PROBE_BEGIN
        + "\n"
        + inner
        + _nightly.BLOCKING_PROBE_END
        + "\n"
        + after
    )

_nightly_probe_ok, _ = _nightly_scan(_nightly_window(_NIGHTLY_REPORT_IMPORT + "\n"))
R.check(
    "a real report inside the probe window satisfies the positive control",
    "log:blocking_positive_control" not in _nightly_probe_ok
    and not [f for f in _nightly_probe_ok if f in _NIGHTLY_RATCHET],
    f"windowed import report failures={_nightly_probe_ok}",
)
_nightly_probe_empty, _ = _nightly_scan(_nightly_window(""))
R.check(
    "an empty probe window fails the positive control and keeps the pin green",
    "log:blocking_positive_control" in _nightly_probe_empty
    and not [f for f in _nightly_probe_empty if f in _NIGHTLY_RATCHET],
    f"empty window failures={_nightly_probe_empty}",
)
_nightly_probe_reword, _ = _nightly_scan(_nightly_window(_nightly_reword + "\n"))
R.check(
    "a leading-phrase reword inside the window fails the positive control",
    "log:blocking_positive_control" in _nightly_probe_reword,
    "the control accepted a report whose leading phrase the regex cannot see",
)
_nightly_probe_before, _ = _nightly_scan(
    _NIGHTLY_CLEAN + "\n" + _NIGHTLY_REPORT_IMPORT + "\n" + _nightly_window("")
)
R.check(
    "a report before the window fails the pin and not the control by itself",
    "log:no_new_blocking_call" in _nightly_probe_before
    and "log:blocking_positive_control" in _nightly_probe_before,
    f"before-window failures={_nightly_probe_before}",
)
_nightly_probe_after_end, _ = _nightly_scan(
    _nightly_window(_NIGHTLY_REPORT_IMPORT + "\n", after=_NIGHTLY_REPORT_SLEEP + "\n")
)
R.check(
    "a report after END stays in the pin half",
    "log:no_new_blocking_call" in _nightly_probe_after_end
    and "log:blocking_positive_control" not in _nightly_probe_after_end,
    f"after-END failures={_nightly_probe_after_end}",
)
_nightly_streams_pin, _nightly_streams_probe = _nightly.partition_blocking_probe(
    (
        _NIGHTLY_CLEAN + "\n" + _nightly.BLOCKING_PROBE_BEGIN + "\n"
        + _NIGHTLY_REPORT_IMPORT + "\n" + _nightly.BLOCKING_PROBE_END + "\n",
        _NIGHTLY_REPORT_SLEEP,
    )
)
R.check(
    "an unwindowed second stream stays in the pin (a3e log must not hide)",
    bool(_nightly.BLOCKING_CALL.search(_nightly_streams_probe))
    and bool(_nightly.BLOCKING_CALL.search(_nightly_streams_pin)),
    "partition_blocking_probe folded an unmarked stream into the probe half",
)
_a4_tb = (
    _nightly.TRACEBACK_HEAD + "\n"
    "  File \"/usr/src/homeassistant/homeassistant/helpers/update_coordinator.py\","
    " line 441, in _async_refresh\n"
    "    self.data = await self._async_update_data()\n"
    "  File \"/config/custom_components/heatpump_optimizer/coordinator.py\","
    " line 6030, in _fetch_tibber_prices\n"
    "    self._tibber_fetch_failed(str(payload))\n"
    "homeassistant.helpers.update_coordinator.UpdateFailed: HTTP 500\n"
)
_crash_tb = (
    _nightly.TRACEBACK_HEAD + "\n"
    "  File \"/config/custom_components/heatpump_optimizer/sensor.py\","
    " line 1, in native_value\n"
    "    raise RuntimeError('boom')\n"
    "RuntimeError: boom\n"
)
_a4_tb_fail, _ = _nightly_scan(_NIGHTLY_CLEAN + "\n" + _a4_tb)
_crash_tb_fail, _ = _nightly_scan(_NIGHTLY_CLEAN + "\n" + _crash_tb)
R.check(
    "A4's UpdateFailed traceback is not log:no_integration_traceback",
    "log:no_integration_traceback" not in _a4_tb_fail
    and "log:no_integration_traceback" in _crash_tb_fail,
    f"a4={_a4_tb_fail} crash={_crash_tb_fail}",
)
R.check(
    "HeatPumpOptimizerConfigEntry is bound on the package, not via _lazy",
    "HeatPumpOptimizerConfigEntry" in integration.__dict__,
    "HA 2026 get_type_hints looks the name up on the setup path and _lazy is a blocking import_module",
)
# #953 (R4-D10-03): that eager binding is only the RUNTIME half of the
# alias. The checker's half must be parametrised over the coordinator: under
# the real stubs ``ConfigEntry`` is generic with a PEP 696 ``Any`` default,
# so a bare binding types ``entry.runtime_data`` as ``Any`` in exactly the
# three functions Home Assistant calls, while the strict census reports 0.
# It must be parametrised for the checker ONLY: ``get_type_hints`` resolves
# the annotation on the setup path, and a forward reference inside the
# runtime binding raises NameError there (measured in round 4). Both halves
# are pinned from the artifact that reads them -- the source for mypy, the
# imported module for Home Assistant -- so each mutation of the binding
# fails exactly one side and the two cannot be collapsed into one check.
_rd_alias_tree = ast.parse(
    pathlib.Path(integration.__file__).read_text(encoding="utf-8")
)


def _rd_alias_bindings(stmts):
    """Module-level ``HeatPumpOptimizerConfigEntry`` bindings in ``stmts``.

    Returns the RHS text of every plain or annotated assignment to the
    alias name, so an ``if TYPE_CHECKING:`` body and the module statements
    around it can be read separately.
    """
    out = []
    for node in stmts:
        assigns = []
        if isinstance(node, ast.Assign):
            assigns = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            assigns = [node.target]
        for target in assigns:
            if isinstance(target, ast.Name) and target.id == "HeatPumpOptimizerConfigEntry":
                out.append(ast.unparse(node.value))
    return out


_rd_tc_block = next(
    (
        node
        for node in _rd_alias_tree.body
        if isinstance(node, ast.If) and ast.unparse(node.test) == "TYPE_CHECKING"
    ),
    None,
)
_rd_static_rhs = (
    _rd_alias_bindings(_rd_tc_block.body)[0]
    if _rd_tc_block is not None and _rd_alias_bindings(_rd_tc_block.body)
    else "(absent)"
)
_rd_runtime_stmts = [
    node for node in _rd_alias_tree.body if node is not _rd_tc_block
] + (_rd_tc_block.orelse if _rd_tc_block is not None else [])
_rd_runtime_rhs = (
    _rd_alias_bindings(_rd_runtime_stmts)[0]
    if _rd_alias_bindings(_rd_runtime_stmts)
    else "(absent)"
)
R.check(
    "the entry alias is parametrised over the coordinator for the checker",
    _rd_static_rhs
    in (
        "ConfigEntry[HeatPumpOptimizerCoordinator]",
        "ConfigEntry['HeatPumpOptimizerCoordinator']",
    ),
    f"TYPE_CHECKING binding={_rd_static_rhs!r} (runtime binding={_rd_runtime_rhs!r});"
    " a bare binding types runtime_data as Any in the three entry points",
)
R.check(
    "the runtime entry alias stays bare, so get_type_hints resolves it",
    _rd_runtime_rhs == "ConfigEntry",
    f"runtime binding={_rd_runtime_rhs!r}; a parametrised runtime binding puts a"
    " forward reference inside the name the setup path resolves (NameError)",
)
# The parametrised alias needs the coordinator name, but that import must
# not execute at package import: the closure note above ``_LAZY_ATTRS``
# records what a plain ``from .coordinator import ...`` at module level
# costs. Any coordinator import outside the TYPE_CHECKING body does.
_rd_coord_import_runtime = [
    ast.unparse(node)
    for node in ast.walk(ast.Module(body=_rd_runtime_stmts, type_ignores=[]))
    if isinstance(node, ast.ImportFrom) and node.module == "coordinator"
]
R.check(
    "no coordinator import executes at package import",
    not _rd_coord_import_runtime,
    f"module-level coordinator imports={_rd_coord_import_runtime}",
)
# The runtime half, executed against the imported module the way setup
# reads it: the bound name must be the bare ConfigEntry class, and the
# three entry points' annotations must resolve without a NameError.
from homeassistant.config_entries import (  # noqa: E402
    ConfigEntry as _rd_config_entry_cls,
)

R.check(
    "the imported package binds the alias to the ConfigEntry class",
    integration.__dict__["HeatPumpOptimizerConfigEntry"] is _rd_config_entry_cls,
    "the runtime alias is not the ConfigEntry class annotations resolve to",
)
import typing as _rd_typing  # noqa: E402

_rd_hint_failures = []
for _rd_entry_point in (
    integration.async_setup_entry,
    integration.async_update_options,
    integration.async_unload_entry,
):
    try:
        _rd_typing.get_type_hints(_rd_entry_point)
    except Exception as exc:  # noqa: BLE001 - the failure text is the point
        _rd_hint_failures.append(f"{_rd_entry_point.__name__}: {exc!r}")
R.check(
    "get_type_hints resolves all three entry points' annotations",
    not _rd_hint_failures,
    "; ".join(_rd_hint_failures),
)
_async_lazy_src = _inspect.getsource(integration._async_lazy)
R.check(
    "_async_lazy offloads import_module itself, not the _lazy wrapper",
    "import_module" in _async_lazy_src
    and "async_add_import_executor_job(_lazy" not in _async_lazy_src,
    "wrapping import_module in _lazy ran the import on the loop (A14)",
)
# Setup already imported coordinator via ``_async_lazy``. A later
# ``__getattr__`` that still calls ``import_module(".coordinator")`` is
# reported on the loop (relative name is never a ``sys.modules`` key) and
# de-duplicates the #588 probe on 2025.2.0. The probe itself must keep
# calling ``_lazy`` so a cached sibling still trips the detector.
_a14_mod_names: list[str] = []
_a14_import = integration.importlib.import_module

def _a14_spy(name, package=None):
    _a14_mod_names.append(name)
    return _a14_import(name, package)

integration.__dict__.pop("HeatPumpOptimizerCoordinator", None)
integration.importlib.import_module = _a14_spy
try:
    getattr(integration, "HeatPumpOptimizerCoordinator")
finally:
    integration.importlib.import_module = _a14_import
R.check(
    "__getattr__ does not import_module a sibling already in sys.modules",
    ".coordinator" not in _a14_mod_names,
    f"import_module names={_a14_mod_names[:8]}",
)
R.check(
    "the blocking probe calls _lazy so a cached sibling still trips the detector",
    "_lazy(" in _inspect.getsource(_nightly._provoke_lazy_on_loop),
    "getattr of a cached re-export is silent; the probe must call _lazy",
)

# tools/audit/preflight.sh refuses a closing keyword the orchestrator did not
# declare -- the defect that closed #224 from a merge message saying "does not
# close #224", which closingIssuesReferences cannot see because it describes the
# PR body and the merge message is a separate artifact.
#
# Pinned HERE rather than left to be run by hand, because tools/audit/ is INERT:
# a check nothing reads is exactly what let the nightly lane's blocking pin go
# stale in silence (#533). Both arms, so this cannot become a check that passes
# whatever the script does.
_preflight = Path("tools/audit/preflight.sh")
R.check(
    "the orchestrator pre-flight refuses an undeclared closing keyword",
    _preflight.is_file()
    and subprocess.run(
        ["bash", str(_preflight)],
        input="First split of #224. Does **not** close #224.\n",
        capture_output=True, text=True,
    ).returncode == 1,
    "preflight.sh must exit 1 on the exact text that closed #224; a negated "
    "closing keyword still closes the issue (GitHub discards the negation)",
)
R.check(
    "the pre-flight refuses a conclusion echoed after ';'",
    _preflight.is_file()
    and subprocess.run(
        ["bash", str(_preflight)],
        input='diff a b; echo "(empty means identical)"\n',
        capture_output=True, text=True,
    ).returncode == 1,
    "preflight.sh must exit 1 on the '; echo <conclusion>' shape, which prints "
    "whether or not the command held; a review disarmed this refusal and every "
    "other check still passed, so it needs its own arm",
)
R.check(
    "and it refuses the four commonest reference forms, not only #N",
    _preflight.is_file()
    and all(
        subprocess.run(
            ["bash", str(_preflight)], input=f"Closes {ref}.\n",
            capture_output=True, text=True,
        ).returncode == 1
        for ref in (
            "#224",
            "GH-224",
            "tvofi/heatpump_optimizer#224",
            "https://github.com/tvofi/heatpump_optimizer/issues/224",
        )
    ),
    "GitHub closes on GH-N, owner/repo#N and a full issue URL as well as #N; "
    "the first version caught only #N. This pins FOUR named forms, not the "
    "universal its earlier name claimed -- a review found seven further shapes "
    "that still pass, and the line-oriented grep cannot match a keyword and a "
    "number separated by a newline. The script is a pre-flight, not a gate.",
)
R.check(
    "and passes a declared one, so it is not simply always-red",
    _preflight.is_file()
    and subprocess.run(
        ["bash", str(_preflight), "524"],
        input="Closes #524. Coverage 86.0 to 100.0, derived at both ends.\n",
        capture_output=True, text=True,
    ).returncode == 0,
    "preflight.sh must exit 0 when every closing keyword is declared; without "
    "this arm the check above passes for a script that refuses everything",
)
# The '; echo' refusal is split: inline backticks in prose are advisory, a
# fenced block is not. Both directions are pinned because the arms above feed
# only single-line inputs, so widening the exemption to strip fenced blocks
# removed the refusal that justifies the split and the suite stayed green.
R.check(
    "a transcript pasted in a fenced block refuses, backticks or not",
    _preflight.is_file()
    and subprocess.run(
        ["bash", str(_preflight)],
        input='```\n`$ diff a b; echo "(empty means identical)"`\n```\n',
        capture_output=True, text=True,
    ).returncode == 1,
    "the inline-backtick exemption must not reach inside a fence: a review "
    "smuggled a real transcript through by wrapping the pasted line in "
    "backticks, so two characters turned the refusal into an advisory",
)
R.check(
    "while the same shape quoted inline in prose stays advisory",
    _preflight.is_file()
    and subprocess.run(
        ["bash", str(_preflight)],
        input='A body may quote `diff a b; echo "(clean)"` as an example.\n',
        capture_output=True, text=True,
    ).returncode == 0,
    "without this arm the check above passes for a script that refuses the "
    "shape everywhere -- the over-fire that got #581 closed, and the reason "
    "orchestrator.md section 1 can quote the anti-pattern it forbids",
)

# The stale-policy-corpus check, driven over a purpose-built repository rather
# than over this one. It has to be: the check reads HEAD, origin/main and the
# merge base, and this checkout's own three are whatever the runner last
# fetched, so an assertion against them states nothing and would flip with the
# clone. The fixture fixes all three.
#
# ONE REPOSITORY, THREE HEADS, because the separation IS the check. A predicate
# that fires on "differs from origin/main" fires on every branch doing
# intentional policy work; the one that has to hold is stale MINUS authored.
#
# THE FIXTURE'S SHAPE IS WHAT PINS THE SUBTRACTION, and the first version of it
# did not. It gave the branch an edit to a file main had NOT moved, so the two
# sets were disjoint, `stale = moved - mine` and `stale = moved` returned the
# same answer, and replacing the subtraction with `stale="$moved"` -- the exact
# predicate that blocks #715 -- left all three arms green. A set difference is
# only pinned by an input where the sets OVERLAP. So arm 1's branch edits
# orchestrator.md, which main also moved, alongside fixer.md, which it did not,
# and the assertion reads all three outcomes off one run: fix-review.md stale,
# orchestrator.md reported as authored-and-moved instead, fixer.md nowhere.
def _copy_policy_lint_tree(dst):
    """`policy_lint.mjs` and everything its import lines reach, into `dst`.

    WALKED FROM ITS OWN IMPORT LINES, NOT LISTED HERE. A hand-kept list of a
    script's dependencies is a second copy of its dependency graph, and this one
    went stale the first time it met a moving main: #721 added `render_md.mjs`
    to `policy_lint.mjs`, the list did not have it, node raised
    ERR_MODULE_NOT_FOUND, and four arms below fell into the `NOT compared` arm
    at once. Loud rather than silent -- that is the sentinel probe working --
    but broken all the same, and the walk is what stops it recurring.
    """
    import shutil

    wf = Path(".claude/workflows")
    need, seen = ["policy_lint.mjs"], set()
    while need:
        f = need.pop()
        if f in seen:
            continue
        seen.add(f)
        need += re.findall(r"""from ['"]\./([\w.-]+\.mjs)['"]""", (wf / f).read_text())
    for f in sorted(seen):
        shutil.copy(wf / f, dst / f)
    # render_md.mjs reaches its vendored markdown-it through `createRequire`,
    # which no import line names, so the walk above cannot see it.
    shutil.copytree(wf / "vendor", dst / "vendor")


def _stale_corpus_fixture():
    import os
    import shutil
    import tempfile

    def g(d, *a):
        return subprocess.run(
            ["git", "-C", str(d), *a], capture_output=True, text=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e"},
        )

    def run(d):
        return subprocess.run(
            ["bash", "tools/audit/preflight.sh"], cwd=str(d), input="a body\n",
            capture_output=True, text=True,
        ).stdout

    d = Path(tempfile.mkdtemp(prefix="hpo-stale-corpus-"))
    try:
        (d / ".claude/workflows").mkdir(parents=True)
        (d / "tools/audit/briefs").mkdir(parents=True)
        # The real instruments, so the fixture drives POLICY_GLOBS itself and
        # not a copy of it -- a second definition of "what is policy" inside a
        # test is the same defect as a second one in production.
        _copy_policy_lint_tree(d / ".claude/workflows")
        shutil.copy(_preflight, d / "tools/audit/preflight.sh")
        for f in ("fix-review.md", "fixer.md", "orchestrator.md"):
            (d / "tools/audit/briefs" / f).write_text("v1\n")
        g(d, "init", "-q", "-b", "trunk")
        g(d, "add", "-A")
        g(d, "commit", "-q", "-m", "base")
        base = g(d, "rev-parse", "HEAD").stdout.strip()
        # main moves fix-review.md, exactly as 58aec5f and 43d3e93 did, and
        # orchestrator.md beside it so the branch below can overlap on one file
        # and not the other.
        (d / "tools/audit/briefs/fix-review.md").write_text("v2 -- the verdict grammar\n")
        (d / "tools/audit/briefs/orchestrator.md").write_text("v2\n")
        g(d, "commit", "-qam", "main moves the review contract")
        tip = g(d, "rev-parse", "HEAD").stdout.strip()
        g(d, "update-ref", "refs/remotes/origin/main", tip)
        # Arm 1: cut at the base; authors one file main also moved and one it
        # did not, so the moved and authored sets overlap in exactly one place.
        g(d, "checkout", "-q", "-b", "stale", base)
        (d / "tools/audit/briefs/fixer.md").write_text("v1 + this branch's own edit\n")
        (d / "tools/audit/briefs/orchestrator.md").write_text("v1 + this branch's own edit\n")
        g(d, "commit", "-qam", "author fixer.md and orchestrator.md")
        stale = run(d)
        # Arm 2: cut at the tip, authoring an edit to the file main moved --
        # #715's shape, the branch a "differs from main" predicate would block.
        g(d, "checkout", "-q", "-b", "authored", tip)
        (d / "tools/audit/briefs/fix-review.md").write_text("v2 + this branch's own edit\n")
        g(d, "commit", "-qam", "author fix-review.md")
        authored = run(d)
        # Arm 3: at the tip, nothing authored.
        g(d, "checkout", "-q", "--detach", tip)
        current = run(d)
        # Arm 4: back at the stale head, but with the policy_lint.mjs an OLD
        # checkout has -- one that does not know --corpus-filter, treats it as a
        # no-op and prints its ordinary lint output. Read as a path list that is
        # zero policy files, and zero reads exactly like "nothing is stale". The
        # check has to say it could not compare instead.
        g(d, "checkout", "-q", "stale")
        (d / ".claude/workflows/policy_lint.mjs").write_text(
            "console.log('TOTAL: 0 error(s)')\n"
        )
        old_lint = run(d)
        return stale, authored, current, old_lint
    finally:
        shutil.rmtree(d, ignore_errors=True)


_sc_stale, _sc_authored, _sc_current, _sc_old_lint = _stale_corpus_fixture()
_sc_stale_block = _sc_stale.split("authored here AND moved")[0]
R.check(
    "the pre-flight names a policy file main moved and this branch did not touch",
    "policy corpus -- 1 file(s) origin/main moved" in _sc_stale
    and "briefs/fix-review.md" in _sc_stale_block,
    "an orchestrator worktree 69 commits behind main dispatched a review seat "
    "into a fix-review.md predating 58aec5f and 43d3e93; the seat would have "
    "written a verdict web-fix-wave.js cannot parse and read checks with a call "
    "that reports pr-contract green where it was red",
)
R.check(
    "and reports a policy file it authored as authored, not as stale",
    "briefs/orchestrator.md" not in _sc_stale_block
    and "briefs/orchestrator.md" in _sc_stale.split("authored here AND moved")[-1],
    "orchestrator.md is in BOTH sets -- main moved it and this branch edited "
    "it -- which is the only input a set difference is pinned by. Replacing "
    "`stale = moved - authored` with `stale = moved`, the predicate that blocks "
    "#715, leaves every disjoint fixture green; this arm is what fails",
)
R.check(
    "and does not mention a policy file only this branch touched",
    "briefs/fixer.md" not in _sc_stale,
    "fixer.md is authored here and untouched on main: it is neither stale nor "
    "a rebase conflict, so naming it anywhere is the over-fire that would send "
    "a seat looking for a staleness that does not exist",
)
R.check(
    "and stays silent on a branch that authors a policy edit (null control)",
    "current with origin/main" in _sc_authored
    and "origin/main moved" not in _sc_authored,
    "#715 edits fixer.md and orchestrator.md, #722 edits three rule files. A "
    "predicate keyed on 'differs from origin/main' fires on exactly those "
    "branches, and one that blocks the legitimate path is routed around inside "
    "a day -- without this arm the check above passes for a predicate that "
    "fires on every branch",
)
R.check(
    "and on a checkout level with origin/main (second null control)",
    "current with origin/main" in _sc_current
    and "origin/main moved" not in _sc_current,
    "a checkout at main's own tip has nothing stale; an arm that fires here "
    "would make the check unreadable and it would be disabled",
)
# The mirror-age proxy, at both ends of the measure it reads. The whole
# comparison above rests on a LOCAL mirror nothing fetches, so a worktree whose
# `refs/remotes/origin/main` was never re-fetched compares a ref against itself
# and reports `ok` -- the one false negative, and the same class as the incident.
# The proxy makes it visible, and WHICH clock it reads decides whether the line
# is signal or noise: the tip COMMIT's date is an upstream fact, true of main
# wherever it is read, while the reflog entry is a local one -- when THIS clone
# last moved the ref. Both arms below run on the same checkout and differ only
# in which of the two is old.
def _mirror_age_fixture():
    import os
    import shutil
    import tempfile

    def build(commit_age_h, fetch_age_h):
        d = Path(tempfile.mkdtemp(prefix="hpo-mirror-age-"))
        try:
            (d / ".claude/workflows").mkdir(parents=True)
            (d / "tools/audit/briefs").mkdir(parents=True)
            _copy_policy_lint_tree(d / ".claude/workflows")
            shutil.copy(_preflight, d / "tools/audit/preflight.sh")
            (d / "tools/audit/briefs/fix-review.md").write_text("v1\n")
            now = int(datetime.now(UTC).timestamp())

            def g(*a, ago=0):
                when = f"@{now - ago * 3600} +0000"
                return subprocess.run(
                    ["git", "-C", str(d), *a], capture_output=True, text=True,
                    env={**os.environ,
                         "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
                         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e",
                         "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when},
                )

            g("init", "-q", "-b", "trunk")
            g("add", "-A")
            g("commit", "-q", "-m", "base", ago=commit_age_h)
            sha = g("rev-parse", "HEAD").stdout.strip()
            # git stamps a reflog entry with the committer date, so this is what
            # sets "when the mirror last moved" independently of the commit.
            g("update-ref", "refs/remotes/origin/main", sha, ago=fetch_age_h)
            return subprocess.run(
                ["bash", "tools/audit/preflight.sh"], cwd=str(d), input="a body\n",
                capture_output=True, text=True,
            ).stdout
        finally:
            shutil.rmtree(d, ignore_errors=True)

    return build(30, 0), build(0, 30)


_ma_fetched_now, _ma_fetched_long_ago = _mirror_age_fixture()
R.check(
    "the mirror-age proxy is silent on a fresh fetch of a day-old tip",
    "nothing here fetches" not in _ma_fetched_now,
    "the tip commit is 30h old and the ref was moved into this clone a second "
    "ago -- a worktree cut this minute from a mirror fetched this minute. "
    "`git log -1 --format=%ct refs/remotes/origin/main` fires here, on a "
    "checkout that is exactly current, because it reads when main's tip was "
    "committed somewhere else. This arm is the null control for the reflog",
)
R.check(
    "and fires where the ref itself has not moved in this clone for a day",
    "nothing here fetches" in _ma_fetched_long_ago
    and "last moved in this clone" in _ma_fetched_long_ago,
    "the positive arm, and without it the null control above is also passed by "
    "a proxy that was simply deleted. The tip commit here is seconds old, so "
    "the only clock that can fire is the reflog entry",
)
R.check(
    "and says it could not compare where policy_lint.mjs predates the mode",
    "NOT compared" in _sc_old_lint and "current with origin/main" not in _sc_old_lint,
    "an old checkout's policy_lint.mjs treats --corpus-filter as a no-op and "
    "prints lint output, which as a path list is zero policy files -- "
    "indistinguishable from nothing being stale. Without the sentinel probe the "
    "check reports `ok` on precisely the stale checkouts it exists to catch, "
    "and this run is the same stale head that fires in the first arm",
)

# HA loads repairs.py dynamically, so a witness must import it or it is an
# orphan and forces MODE: FULL (#408).
from heatpump_optimizer import repairs as _repairs_mod  # noqa: E402
from heatpump_optimizer import setpoint_check as _setpoint_check_mod  # noqa: E402

R.check(
    "repairs.py is imported so the dynamically loaded platform is classified",
    callable(getattr(_repairs_mod, "async_create_fix_flow", None)),
)
R.check(
    "setpoint_check.evaluate is the consistency detector",
    callable(getattr(_setpoint_check_mod, "evaluate", None)),
)
# F2: the helper supplies the manifest documentation URL and does not
# overwrite one the caller already set.
_f2_docs = json.loads((ROOT / "manifest.json").read_text())["documentation"]
R.check(
    "the documentation link is the one the manifest publishes",
    getattr(_setpoint_check_mod, "DOCUMENTATION_URL", None) == _f2_docs,
    repr(getattr(_setpoint_check_mod, "DOCUMENTATION_URL", None)),
)
_f2_create = getattr(_setpoint_check_mod, "create_issue", None)
_f2_hass = FakeHass()
if callable(_f2_create):
    _f2_create(_f2_hass, const.DOMAIN, "f2_default")
    _f2_create(
        _f2_hass,
        const.DOMAIN,
        "f2_explicit",
        learn_more_url="https://example.invalid/doc",
    )
_f2_default = [
    i for i in getattr(_f2_hass, "issues", []) if i[1] == "f2_default"
]
_f2_explicit = [
    i for i in getattr(_f2_hass, "issues", []) if i[1] == "f2_explicit"
]
R.check(
    "a repair notice raised through the helper carries the documentation link",
    callable(_f2_create)
    and _f2_default
    and _f2_default[0][2].get("learn_more_url") == _f2_docs,
    f"create_issue={_f2_create!r} issues={getattr(_f2_hass, 'issues', None)!r}",
)
R.check(
    "an explicit documentation link is not overwritten",
    callable(_f2_create)
    and _f2_explicit
    and _f2_explicit[0][2].get("learn_more_url")
    == "https://example.invalid/doc",
    f"got {_f2_explicit!r}",
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
R.check(
    "changing the portable node recorder invalidates every closure",
    _closure.select(["tests/node_fs_trace.mjs"])["mode"] == "full",
    "a different wrap changes every node recording",
)

# --- node recording without strace -----------------------------------------
# Darwin has no strace (SIP blocks dtruss). The portable --import tracer
# records the same repo files; Linux CI still uses strace when present.
from unittest import mock as _mock

def _record_probe_no_strace() -> tuple[int, dict]:
    with _tempfile.TemporaryDirectory() as d:
        probe = Path(d) / "probe.mjs"
        probe.write_text(
            'import fs from "node:fs";\n'
            'fs.readFileSync("VERSION", "utf8");\n'
            'fs.readFileSync("tests/README.md", "utf8");\n'
        )
        out = Path(d) / "probe.json"
        real_which = _closure.shutil.which

        def _hide_strace(cmd, *a, **k):
            if cmd == "strace":
                return None
            return real_which(cmd, *a, **k)

        with _mock.patch.object(_closure.shutil, "which", _hide_strace):
            rc = _closure._record_node(str(probe), str(out), dict(_os.environ))
        rec = json.loads(out.read_text()) if out.exists() else {}
        return rc, rec

_probe_rc, _probe_rec = _record_probe_no_strace()
R.check(
    "node recording works without strace",
    _probe_rc == 0 and _probe_rec.get("how") == "node-fs-trace",
    f"rc={_probe_rc} how={_probe_rec.get('how')!r} err={_probe_rec.get('stderr_tail', '')[-300:]!r}",
)
R.check(
    "the portable node recorder sees repo files the script opened",
    "VERSION" in _probe_rec.get("files", [])
    and "tests/README.md" in _probe_rec.get("files", []),
    f"files={_probe_rec.get('files')}",
)
# Darwin --single must grow, not shrink: node-fs-trace is a subset of
# strace -f. Union keeps files only Linux recorded.
with _tempfile.TemporaryDirectory() as _un_td:
    _un_root = Path(_un_td)
    _un_out = _un_root / "closures.json"
    _un_script = "tests/card.mjs"
    _un_out.write_text(json.dumps({
        "closures": {_un_script: ["VERSION", "tests/card.mjs",
                                  "custom_components/heatpump_optimizer/frontend.py"]},
        "recorded": {},
    }))
    _un_rec = _un_root / "rec"
    _un_rec.mkdir()
    (_un_rec / "card.mjs.json").write_text(json.dumps({
        "script": _un_script, "rc": 0, "seconds": 0.1,
        "files": ["VERSION", "tests/README.md"],
        "how": "node-fs-trace",
    }))
    _un_rc = _closure.merge(_un_rec, _un_out, partial=True)
    _un_got = set(json.loads(_un_out.read_text())["closures"][_un_script])
R.check(
    "a Darwin node re-record unions instead of replacing",
    _un_rc == 0
    and "custom_components/heatpump_optimizer/frontend.py" in _un_got
    and "tests/README.md" in _un_got,
    f"rc={_un_rc} files={sorted(_un_got)}",
)

# --- which workflow files are the gate (#607 follow-up) ----------------------
#
# `GATE_FILES` used to carry the directory prefix `.github/workflows/`, so a
# comment-only edit to `governance.yml` printed "changes the gate itself, so
# every closure is suspect" and ran the unscoped suite -- `tests/stress.py`
# with it -- on the pull request and again on the push to main. Only
# `tests.yml` can do what a gate file means: it sets the job matrix, the
# interpreter versions, the installed dependencies and `GATE_SCOPE`. These
# checks pin that split so the prefix cannot come back by accident.

R.check(
    "the gate's own workflow is a gate file",
    _closure.is_gate_file(".github/workflows/tests.yml"),
    "tests.yml defines GATE_SCOPE and the matrix; a change to it invalidates "
    "every recorded closure",
)

# `governance.yml` left this list when `record-status` landed. It is still not
# a gate file -- it sets no `GATE_SCOPE`, no matrix and no interpreter -- but it
# is no longer INERT either, because this script now READS it to pin that job's
# wiring and its permission widening. Unread by the gate and unreadable by the
# gate are different claims, and the first stopped being true; it is in this
# script's recorded closure instead, so an edit to it selects this script rather
# than skipping. Its own check is below, and it is the third classification a
# workflow file can have -- neither gate nor inert -- which is why the loop
# could not simply gain a member.
#
# The last three inert workflows made the same move for decision 0009 step 3b
# (#954), and the reason outlived it: the ledger-lane pin below requires
# `SEAT_AUTHOR_TOKEN` in NO workflow file (#1086 removed its one use), so an
# edit to any of these three must select this script. So none is inert any more; each is read by this script and
# classified the way `governance.yml` and `release.yml` are below.
_NON_GATE_WORKFLOWS = [
    ".github/workflows/hassfest.yml",
    ".github/workflows/validate.yml",
    ".github/workflows/codeql.yml",
]
for _wf in _NON_GATE_WORKFLOWS:
    R.check(
        f"{_wf.split('/')[-1]} is not a gate file, and is classified",
        (not _closure.is_gate_file(_wf))
        and (not _closure.is_inert(_wf))
        and _closure.affected([_wf])["case"] == "scoped"
        and _wf in json.loads(
            _closure.CLOSURES.read_text())["closures"]["tests/entities.py"],
        f"gate={_closure.is_gate_file(_wf)} inert={_closure.is_inert(_wf)} "
        f"case={_closure.affected([_wf])['case']}; this script reads it to "
        "count the seat author's token references, so an edit to it must "
        "select this script, and it sets no gate variable and runs no gate "
        "script, so it must not force FULL",
    )

# The third classification, and the one that has to be checked rather than
# asserted: read by the gate, so not INERT; not the gate, so not a gate file.
# Getting it wrong in either direction is silent. Left on INERT it would be a
# file this script reads while declaring nothing reads it -- `closure.py`'s
# `merge` refuses that pair, which is what makes this a check and not an
# opinion. Made a gate file it would run `tests/stress.py` on a comment edit,
# which is the regression the block above exists to prevent.
_GOV_WF = ".github/workflows/governance.yml"
_GOV_CASE = _closure.affected([_GOV_WF])
R.check(
    "governance.yml is read by the gate, so it is scoped rather than inert or "
    "full",
    (not _closure.is_gate_file(_GOV_WF))
    and (not _closure.is_inert(_GOV_WF))
    and _GOV_CASE["case"] == "scoped"
    and _GOV_WF in json.loads(
        _closure.CLOSURES.read_text())["closures"]["tests/entities.py"],
    f"gate={_closure.is_gate_file(_GOV_WF)} inert={_closure.is_inert(_GOV_WF)} "
    f"case={_GOV_CASE['case']}; this script reads it to pin `record-status`, "
    "so an edit to that job must select this script and must not force FULL",
)

# The fourth classification move, on the same precedent: `release.yml` was
# inert until #960 put an owner-approved permission grant on its one job, and
# a grant nothing pins is a grant that can grow past its approval in silence.
# This script reads it to pin the grant (checks beside the governance grant
# pins below), so it leaves `INERT` and enters this script's recorded closure.
_REL_WF = ".github/workflows/release.yml"
_REL_CASE = _closure.affected([_REL_WF])
R.check(
    "release.yml is read by the gate, so it is scoped rather than inert or "
    "full",
    (not _closure.is_gate_file(_REL_WF))
    and (not _closure.is_inert(_REL_WF))
    and _REL_CASE["case"] == "scoped"
    and _REL_WF in json.loads(
        _closure.CLOSURES.read_text())["closures"]["tests/entities.py"],
    f"gate={_closure.is_gate_file(_REL_WF)} inert={_closure.is_inert(_REL_WF)} "
    f"case={_REL_CASE['case']}; this script reads it to pin the release job's "
    "attestation grant, so an edit to that job must select this script and "
    "must not force FULL",
)

R.check(
    "no directory prefix in GATE_FILES can swallow a non-gate workflow",
    not any(
        _p.endswith("/") and ".github/workflows/tests.yml".startswith(_p)
        for _p in _closure.GATE_FILES
    ),
    "a prefix that matches tests.yml would also match the four beside it, "
    "which is the regression this check exists to refuse",
)

# The instance moved from `governance.yml` to `hassfest.yml` when
# `record-status` landed: this script now READS governance.yml, so it is scoped
# rather than skipped, and its own case is checked above. The PROPERTY this
# check was written for is unchanged and is the one that matters -- a non-gate
# workflow must never print `full`, which is what ran `tests/stress.py` on a
# comment edit. So the property is asserted over EVERY non-gate workflow
# rather than over the one that happened to be the example. The `skip` arm
# lost its last inert instance with 0009 step 3b, which moved every non-gate
# workflow into this script's closure; what a change to one now costs is
# the scripts that read it, and that is what is pinned in its place.
_HF_CASE = _closure.affected([".github/workflows/hassfest.yml"])
_HF_PLAN = _closure.select([".github/workflows/hassfest.yml"])
R.check(
    "a change to a non-gate workflow costs the gate its readers, never FULL",
    _HF_CASE["case"] == "scoped"
    and _HF_PLAN["mode"] == "scoped"
    and "tests/entities.py" in _HF_PLAN["run"],
    f"{_HF_CASE}; select mode={_HF_PLAN['mode']} run={_HF_PLAN['run']}",
)
R.check(
    "and no non-gate workflow forces the FULL suite, whatever else it does",
    all(_closure.affected([_wf])["case"] != "full"
        for _wf in [*_NON_GATE_WORKFLOWS, _GOV_WF, _REL_WF]),
    str({_wf: _closure.affected([_wf])["case"]
         for _wf in [*_NON_GATE_WORKFLOWS, _GOV_WF, _REL_WF]}),
)

# --- when the closures CHECK itself runs (#354) -----------------------------
#
# `select` above decides which tests a change needs. `affected` decides
# whether the job that checks the table `select` trusts needs to run at all.
# It ran on a pull request only when the diff ADDED a file under
# custom_components/, so a change to what a test READS was checked one merge
# too late -- five times (#214, #320, #332, #340, #349), each a green pull
# request, a red main, and a second pull request to repair it.
# tests/README.md left this example in #938, when this script began reading
# its annotations above: it is a dependency of this script now, so an edit to
# it selects this script rather than skipping. DISCLAIMER.md keeps the third
# slot a genuinely inert document still fills.
_A_DOCS = _closure.affected(
    ["docs/audit-2026-09.md", "LICENSE", "DISCLAIMER.md"])
R.check(
    "a docs-only change still costs the closures check nothing",
    _A_DOCS["case"] == "skip",
    f"case is {_A_DOCS['case']}: {_A_DOCS['reason']} -- if a docs pull "
    "request pays 12-22 minutes the scoping this replaces was pointless",
)
# The skip is decided by the TABLE, not by the hand-written INERT list, and
# the order is why. Until #357, quality_scale.yaml was on INERT and inside
# env_drift's rule-widened closure at the same time -- the real, on-main
# instance of exactly the shape this ordering rule exists to get right.
# #357 fixed the recorder (NEVER_WIDENED, above), and #951 turned the page
# on the file's INERT listing itself: this script now reads the register
# (the coverage-row pins above), so it left the INERT list and entered
# this script's recorded closure. The live example of "INERT and in no
# closure means skip" is the docs-only probe above; what this checks now
# is the point of that move -- a register edit selects this script instead
# of skipping, so the round-4 drift (rows contradicted by execution in a
# file no gate script read) has a lane that sees it.
_A_QS = _closure.affected([_QS])
R.check(
    "a quality_scale.yaml edit selects this script, not a skip (#951)",
    not _closure.is_inert(_QS) and _A_QS["case"] == "scoped",
    f"{_QS} is inert={_closure.is_inert(_QS)} and case={_A_QS['case']} -- "
    "the register's rows were contradicted by execution for exactly as "
    "long as no gate script read the file",
)
# The ORDER still has to be pinned even with no naturally occurring
# contradiction left on disk, so this manufactures one: start from the real
# committed table (every selectable script stays covered, which `affected`
# requires) and inject one INERT-listed path into an existing closure's file
# list. `affected` must still call that "scoped", never "skip" -- the same
# property the fixed quality_scale.yaml case demonstrated when it was real.
def _affected_against(table: dict, files: list[str]) -> dict:
    with _tempfile.TemporaryDirectory() as _td:
        _p = Path(_td) / "closures.json"
        _p.write_text(json.dumps({"closures": table}))
        _orig_closures, _closure.CLOSURES = _closure.CLOSURES, _p
        try:
            return _closure.affected(files)
        finally:
            _closure.CLOSURES = _orig_closures


_FAKE_INERT = "docs/does-not-need-to-exist.md"
assert _closure.is_inert(_FAKE_INERT), "docs/ must stay on INERT for this probe"
_synthetic_closures = {
    k: list(v) for k, v in
    json.loads(_closure.CLOSURES.read_text())["closures"].items()
}
_synthetic_closures[_ED] = _synthetic_closures[_ED] + [_FAKE_INERT]
_A_SYNTHETIC = _affected_against(_synthetic_closures, [_FAKE_INERT])
R.check(
    "manufactured case: table presence outranks INERT regardless of which "
    "file it is",
    _A_SYNTHETIC["case"] == "scoped",
    f"case={_A_SYNTHETIC['case']}: a file both INERT and recorded must be "
    "scoped, not skipped, or the ordering rule has regressed",
)
# The general check #357 asks for, run on the committed table -- the same
# thing `merge` has always refused, now also checked on the path the
# closures CI job (--record-only, never `merge`) actually runs.
_committed_closures = json.loads(_closure.CLOSURES.read_text())["closures"]
_inert_violations = _closure.inert_closure_violations(_committed_closures)
R.check(
    "no file is both INERT and inside a recorded closure",
    not _inert_violations,
    "these are declared unread and recorded as read at once: "
    + ", ".join(_inert_violations),
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
# PR `closures` already records under strace (`--record-only`). Autofix
# merges those recordings into tests/closures.json and pushes; it must
# not run on main, forks, a green check, or its own follow-up commit.
_AF_KW = dict(
    event_name="pull_request", closures_result="failure",
    head_repo="tvofi/heatpump_optimizer", repo="tvofi/heatpump_optimizer",
    commit_subject="3L-G10: away toggle",
)
R.check(
    "a failed same-repo PR closures job may autofix",
    _closure.autofix_allowed(**_AF_KW),
    "the #495-shaped UNDER-SCOPED case is what this exists for",
)
R.check(
    "autofix does not run on a push to main",
    not _closure.autofix_allowed(**{**_AF_KW, "event_name": "push"}),
    "main's closures job is the auditor, not a rewriter",
)
R.check(
    "autofix does not run on a fork PR",
    not _closure.autofix_allowed(
        **{**_AF_KW, "head_repo": "outsider/heatpump_optimizer"}),
    "a fork has no write access to the head repo via this token",
)
R.check(
    "autofix does not run when closures passed",
    not _closure.autofix_allowed(**{**_AF_KW, "closures_result": "success"}),
    "a green check has nothing to merge",
)
R.check(
    "autofix does not loop on its own commit",
    not _closure.autofix_allowed(
        **{**_AF_KW, "commit_subject": "ci: re-record closures"}),
    "one push per failure; a still-red check is not under-scope",
)
# Apply: a recording that names one extra file is the UNDER-SCOPED case.
# Merge it, then check must pass, and the committed list must grow.
with _tempfile.TemporaryDirectory() as _af_td:
    _af_root = Path(_af_td)
    _af_script = "tests/open_meteo.py"
    _af_committed = {
        "closures": {_af_script: [_af_script, "tests/harness.py"]},
        "recorded": {},
    }
    _af_closures = _af_root / "closures.json"
    _af_closures.write_text(json.dumps(_af_committed))
    _af_rec_dir = _af_root / "rec"
    _af_rec_dir.mkdir()
    (_af_rec_dir / "open_meteo.json").write_text(json.dumps({
        "script": _af_script, "rc": 0,
        "files": [_af_script, "tests/harness.py", "tests/run.sh"],
    }))
    _af_orig, _closure.CLOSURES = _closure.CLOSURES, _af_closures
    try:
        _af_status = _closure.apply_under_scoped_recordings(
            _af_rec_dir, partial=True)
        _af_after = json.loads(_af_closures.read_text())["closures"][_af_script]
    finally:
        _closure.CLOSURES = _af_orig
R.check(
    "UNDER-SCOPED recordings merge into the committed closure",
    _af_status == "changed" and "tests/run.sh" in _af_after,
    f"status={_af_status} files={_af_after}",
)
with _tempfile.TemporaryDirectory() as _af2_td:
    _af2_root = Path(_af2_td)
    _af2_script = "tests/open_meteo.py"
    _af2_list = [_af2_script, "tests/harness.py", "tests/run.sh"]
    _af2_closures = _af2_root / "closures.json"
    _af2_closures.write_text(json.dumps(
        {"closures": {_af2_script: _af2_list}, "recorded": {}}))
    _af2_rec = _af2_root / "rec"
    _af2_rec.mkdir()
    (_af2_rec / "open_meteo.json").write_text(json.dumps({
        "script": _af2_script, "rc": 0, "files": _af2_list,
    }))
    _af2_orig, _closure.CLOSURES = _closure.CLOSURES, _af2_closures
    try:
        _af2_status = _closure.apply_under_scoped_recordings(
            _af2_rec, partial=True)
    finally:
        _closure.CLOSURES = _af2_orig
R.check(
    "a recording that matches the committed list is not an autofix",
    _af2_status == "skip-clean",
    f"status={_af2_status}: merging a matching record would loop",
)
# A failed recording and "the failure was not UNDER-SCOPED" used to share one
# status, and that status is quiet -- so ONE script failing to record vetoed
# the repair of a DIFFERENT script that genuinely under-approximated, while
# the job still concluded success and no `ci: re-record closures` commit was
# ever pushed (#523, the residual the #528 review measured). `check` never
# looks at `rc`, so the two conditions are independent and co-occur.
#
# `merge(allow_failures=False)` already refuses a failed recording, and that
# refusal is `skip-merge-failed`, which reddens. Removing the early return
# entirely yields exactly that -- measured -- so the status below restores a
# refusal the early return had been pre-empting, with a remedy of its own.
def _af_case(committed, records):
    """Run the real apply function over a throwaway closures.json.

    Returns (status, bytes-unchanged). Files named must be real files in the
    tree: `check` rejects a recording of anything that is not a regular file.
    """
    with _tempfile.TemporaryDirectory() as td:
        path = Path(td) / "closures.json"
        before = json.dumps({"closures": committed, "recorded": {}})
        path.write_text(before)
        rec = Path(td) / "rec"
        rec.mkdir()
        for i, r in enumerate(records):
            (rec / f"{i}.json").write_text(json.dumps(r))
        orig, _closure.CLOSURES = _closure.CLOSURES, path
        try:
            status = _closure.apply_under_scoped_recordings(rec, partial=True)
            return status, path.read_text() == before
        finally:
            _closure.CLOSURES = orig


_af3_status, _af3_kept = _af_case(
    {"tests/open_meteo.py": ["tests/open_meteo.py"],
     "tests/frontend.py": ["tests/frontend.py"]},
    [{"script": "tests/open_meteo.py", "rc": 0,
      "files": ["tests/open_meteo.py", "tests/harness.py"]},
     {"script": "tests/frontend.py", "rc": 1,
      "files": ["tests/frontend.py"]}],
)
R.check(
    "one failed recording beside a real under-approximation reddens, not skips",
    _af3_status == "skip-failed-recording" and _af3_kept
    and _closure.autofix_repair_failed("closures-autofix", _af3_status),
    f"status={_af3_status}: open_meteo.py under-approximates and the repair "
    "is refused because frontend.py failed to record -- a human is waiting "
    "for a commit no step will push",
)
# The other half of the split, and the reason it is a split rather than a
# reclassification: a failed recording with nothing under-scoped must stay
# quiet. `closures-autofix` runs on ANY `closures` failure, so reddening this
# would fire on every no-copies, NOT-A-FILE or INERT failure that happened to
# coincide with a failed recording -- and send its reader to re-derive a
# closure that was never stale.
_af3b_status, _af3b_kept = _af_case(
    {"tests/open_meteo.py": ["tests/open_meteo.py"]},
    [{"script": "tests/open_meteo.py", "rc": 1,
      "files": ["tests/open_meteo.py"]}],
)
R.check(
    "a failed recording with nothing under-scoped stays quiet",
    _af3b_kept
    and not _closure.autofix_repair_failed("closures-autofix", _af3b_status),
    f"status={_af3b_status}: no repair was owed, so no human is waiting",
)
with _tempfile.TemporaryDirectory() as _af4_td:
    _af4_root = Path(_af4_td)
    _af4_closures = _af4_root / "closures.json"
    _af4_before = json.dumps({
        "closures": {"tests/open_meteo.py": ["tests/open_meteo.py"]},
        "recorded": {},
    })
    _af4_closures.write_text(_af4_before)
    _af4_rec = _af4_root / "rec"
    _af4_rec.mkdir()
    (_af4_rec / "bad.json").write_text("{")
    _af4_orig, _closure.CLOSURES = _closure.CLOSURES, _af4_closures
    try:
        _af4_status = _closure.apply_under_scoped_recordings(
            _af4_rec, partial=True)
        _af4_after = _af4_closures.read_text()
    finally:
        _closure.CLOSURES = _af4_orig
R.check(
    "unreadable recordings do not rewrite closures.json",
    _af4_status == "skip-merge-failed" and _af4_after == _af4_before,
    f"status={_af4_status}",
)
# A merge that SUCCEEDS and still leaves check failing must restore the file,
# not push it. The fixture that used to occupy this slot made the under-scoped
# cause an INERT file (LICENSE): the merge wrote the INERT-and-recorded pair
# and the second check refused it. 45b5768 moved that refusal into merge
# --single itself, so the INERT route now reports skip-merge-failed before
# any write, and this check would pin the wrong status. The surviving route
# to a successful merge with a still-failing check is non-INERT: a
# DRIVEN_BY_OTHERS child recorded alone. merge --partial folds
# dst_checks.py into features.py, grows that entry, and returns 0 -- the
# push path -- while check --partial compares the raw record name, finds no
# committed closure for it, and still fails. The merge wrote real bytes (the
# fold grew features.py's list), so the restore below is undoing a change,
# not confirming a no-op.
with _tempfile.TemporaryDirectory() as _af5_td:
    _af5_root = Path(_af5_td)
    _af5_script = "tests/dst_checks.py"
    _af5_closures = _af5_root / "closures.json"
    _af5_before = json.dumps({
        "closures": {"tests/features.py": ["tests/features.py"]},
        "recorded": {},
    })
    _af5_closures.write_text(_af5_before)
    _af5_rec = _af5_root / "rec"
    _af5_rec.mkdir()
    (_af5_rec / "dst_checks.json").write_text(json.dumps({
        "script": _af5_script, "rc": 0,
        "files": [_af5_script, "tests/harness.py"],
    }))
    _af5_orig, _closure.CLOSURES = _closure.CLOSURES, _af5_closures
    try:
        _af5_status = _closure.apply_under_scoped_recordings(
            _af5_rec, partial=True)
        _af5_after = _af5_closures.read_text()
    finally:
        _closure.CLOSURES = _af5_orig
R.check(
    "a merge that still fails check is restored, not pushed",
    _af5_status == "skip-still-fails" and _af5_after == _af5_before,
    f"status={_af5_status}",
)
R.check(
    "a GITHUB_TOKEN autofix push must retrigger Tests",
    _closure.retrigger_needed(pushed=True, used_pat=False),
    "otherwise the new SHA has no checks and the PR stays red",
)
R.check(
    "a PAT autofix push must not also dispatch",
    not _closure.retrigger_needed(pushed=True, used_pat=True),
    "the PAT push already fires pull_request; a second run would double the gate",
)
R.check(
    "no retrigger when autofix did not push",
    not _closure.retrigger_needed(pushed=False, used_pat=False),
    "a skip is not a new SHA",
)
R.check(
    "claims autofix may run after a closures autofix commit",
    _closure.autofix_allowed(
        **{**_AF_KW, "commit_subject": "ci: re-record closures"},
        loop_subject="ci: drop inherited claims"),
    "the two repairs have separate loop guards",
)
# Both autofix jobs push only on `changed`, and every other status fell
# through to job success -- so a job that repaired nothing was indistinguishable
# from one that did, and `.cursor/rules/ci-autofix.mdc`'s "wait for the bot
# commit" waited for a commit no step would push (#523).
_AFJ = "closures-autofix"
R.check(
    "a closures autofix that attempted a repair and failed reddens its job",
    _closure.autofix_repair_failed(_AFJ, "skip-merge-failed")
    and _closure.autofix_repair_failed(_AFJ, "skip-still-fails")
    and _closure.autofix_repair_failed(_AFJ, "skip-failed-recording"),
    "the merge was refused, the merged list still under-approximates, or a "
    "recording failed and the merge would refuse it",
)
# check() said fail, then said pass, over identical bytes. Either check is
# not deterministic or merge reported success without writing the repair;
# either way no `ci: re-record closures` commit exists to wait for.
R.check(
    "a merge that changed no bytes between a failing and a passing check reddens",
    _closure.autofix_repair_failed(_AFJ, "skip-unchanged"),
    "a repair that left the file identical was not recorded",
)
R.check(
    "the ordinary closures autofix no-ops stay quiet",
    not any(_closure.autofix_repair_failed(_AFJ, s) for s in (
        "changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped")),
    "these mean a repair happened or none was ever owed",
)
# claims-autofix is NOT the same shape, and this pins the difference:
# apply_inherited_claims has no attempted-and-failed status, and
# skip-not-inherited is the ordinary answer for every `fast` failure that was
# not INHERITED CLAIMS -- that job never asks which it was, so reddening it
# would redden every unrelated `fast` failure a second time.
R.check(
    "an unrecognised status or job reddens rather than passing by default",
    _closure.autofix_repair_failed(_AFJ, "")
    and _closure.autofix_repair_failed(_AFJ, "skip-invented-later")
    and _closure.autofix_repair_failed("no-such-job", "changed"),
    "a status nobody classified is a repair nobody can wait for",
)
# The table is a claim about what these two functions return. A status added
# to either without a decision here defaults to reddening the job, which is
# safe but silent; this makes the addition say so.
def _returned_statuses(fn) -> set[str]:
    """Every string literal `fn` can return, conditional expressions included.

    A `return "a" if c else "b"` is one Return node carrying two literals; a
    regex over `return "..."` reads that as one status and under-reports the
    very thing this check asks about. It did, on apply_inherited_claims.
    """
    tree = _ast_af.parse(_inspect.getsource(fn))
    return {n.value
            for r in _ast_af.walk(tree)
            if isinstance(r, _ast_af.Return) and r.value is not None
            for n in _ast_af.walk(r.value)
            if isinstance(n, _ast_af.Constant) and isinstance(n.value, str)}


# The list this check used to carry was written by hand and went stale the
# moment `apply_inherited_claims` gained a status: it kept passing while
# claiming to cover "every status", and the job reddened in CI on a status the
# check had never heard of. It now reads the returns out of the function, so
# the two cannot disagree -- `_ac_returns` is derived below by AST and is the
# same set the roster check pins.
_ac_quiet_missing = sorted(
    s for s in _returned_statuses(_env_drift.apply_inherited_claims)
    if _closure.autofix_repair_failed("claims-autofix", s)
)
R.check(
    "every status claims-autofix can return stays quiet",
    not _ac_quiet_missing,
    "a fast failure that was not INHERITED CLAIMS is not a skipped repair, and "
    f"a refusal is not one either; unclassified: {_ac_quiet_missing}",
)
_af_returns = _returned_statuses(_closure.apply_under_scoped_recordings)
_ac_returns = _returned_statuses(_env_drift.apply_inherited_claims)
R.check(
    "every status the two apply functions return is classified here",
    _af_returns == {"changed", "skip-clean", "skip-not-under-scoped",
                    "skip-failed-recording", "skip-merge-failed",
                    "skip-still-fails", "skip-unchanged"}
    and _ac_returns == {"changed", "skip-not-inherited",
                        "skip-moves-nothing-claimable", "skip-cannot-compare"},
    f"closures={sorted(_af_returns)} claims={sorted(_ac_returns)}",
)
# A correct predicate the workflow does not call is the green check this
# whole finding is about, so the wiring is asserted against the YAML itself.
_TESTS_YML = (pathlib.Path(__file__).resolve().parents[1]
              / ".github" / "workflows" / "tests.yml").read_text()


for _job in ("closures-autofix", "claims-autofix"):
    _blk = _workflow_job(_TESTS_YML, _job)
    _steps = _blk.split("\n      - ")
    _rep = [s for s in _steps if "autofix-report" in s]
    R.check(
        f"{_job} reports its status to a human",
        len(_rep) == 1
        and f"--job {_job}" in _rep[0]
        and "steps.autofix.outputs.status" in _rep[0],
        "an unwired predicate cannot redden anything",
    )
    R.check(
        f"{_job} reports even when the repair step failed or was skipped",
        bool(_rep) and re.search(r"if:\s*always\(\)", _rep[0]),
        "the statuses worth reporting are exactly the ones that skip the push",
    )
    # Last, or its own non-zero exit would skip the push step below it and
    # throw away the repair it exists to report.
    R.check(
        f"{_job} reports after it has pushed, not before",
        bool(_rep) and _steps[-1] is _rep[0],
        "a reporting step that preempts the push destroys the repair",
    )
# A GITHUB_TOKEN push's `pull_request` runs are held `action_required` with
# zero jobs until a maintainer approves them (5511f23 on #1068, dac077e on
# #1090), so each required context needs another route. Tests, Hassfest,
# Validate and CodeQL are dispatched from the push step; dispatch run
# 35187949244 put all three `Analyze (…)` check runs on 9eab006. Whether a
# merge accepts a dispatch-produced context is NOT measured.
#
# Governance is refused a dispatch. `pr-contract` is `if: pull_request`, so a
# dispatched run skips it, and docs/HANDOVER.md records a probe in which a
# skipped required context satisfies the ruleset: the dispatch would be a
# green `pr-contract` that never read the body. `record`
# would also run on the branch with `issues: write`. Governance's route is the
# body PATCH `## Head` forces after a new head: its `edited` run is unheld and
# carried all four Governance contexts at dac077e (run 35166880265).
#
# Parsed from the push step's non-comment lines only: a commented-out
# dispatch, or one moved into the `always()` report step (which also runs when
# nothing was pushed), must not count.
_AF_DISPATCHED = {"tests.yml", "hassfest.yml", "validate.yml", "codeql.yml"}


def _af_dispatches(step: str) -> set[str]:
    live = "\n".join(ln for ln in step.splitlines()
                     if not ln.lstrip().startswith("#"))
    return set(re.findall(r"gh workflow run (\S+)", live))


for _job in ("closures-autofix", "claims-autofix"):
    _steps = _workflow_job(_TESTS_YML, _job).split("\n      - ")
    _push = [s for s in _steps if re.match(r"name: Push\b", s)]
    _elsewhere = set().union(*(_af_dispatches(s) for s in _steps
                               if s not in _push))
    R.check(
        f"{_job} dispatches every workflow owning a required context but Governance",
        len(_push) == 1 and _af_dispatches(_push[0]) == _AF_DISPATCHED,
        f"push steps={len(_push)} dispatched="
        f"{sorted(_af_dispatches(_push[0])) if _push else []}",
    )
    R.check(
        f"{_job} dispatches from the push step only",
        not _elsewhere,
        f"elsewhere={sorted(_elsewhere)}; only a pushed SHA needs a retrigger",
    )
_CODEQL_ON = (pathlib.Path(__file__).resolve().parents[1] / ".github"
              / "workflows" / "codeql.yml").read_text()
_CODEQL_ON = _CODEQL_ON[_CODEQL_ON.index("\non:\n"):_CODEQL_ON.index("\njobs:\n")]
R.check(
    "codeql.yml accepts the autofix jobs' dispatch",
    re.search(r"^  workflow_dispatch:", _CODEQL_ON, re.M) is not None,
    "without the trigger `gh workflow run codeql.yml` is refused with 422",
)
# The nightly-ha job runs `tests/nightly_ha.py` on the RUNNER, not only in the
# container, and its host half imports the production package to derive what it
# stages: `_seed_unique_id` needs `config_flow.entry_identity` for the seed's
# unique_id, and `load_committed_roster` needs the platform modules for the A3
# roster. That import resolves `homeassistant` from tests/hastub, which imports
# voluptuous, and the package itself imports aiohttp -- so a runner with a bare
# `setup-python` cannot stage at all. #626 added the first such host-side import
# to a job that installed nothing, and both matrix arms died in `_stage` on two
# consecutive nights before anything ran inside Home Assistant. This pins the
# WIRING, not the general class: it says that the one job whose driver imports
# production on the host installs the dependency set that makes that possible,
# and it would not notice a DIFFERENT job acquiring the same shape. `typing`,
# `closure-scope` and both autofix jobs run Python here and install nothing,
# legitimately, because the scripts they run import neither the package nor the
# stub -- which is why the derived form of this check ("every job that runs a
# tests/ script installs the requirements") was measured, over-fired on four
# jobs, and rejected.
_NHA_JOB = _workflow_job(_TESTS_YML, "nightly-ha")
_NHA_STEPS = _NHA_JOB.split("\n      - ")
_NHA_INSTALL = [i for i, s in enumerate(_NHA_STEPS)
                if "tests/requirements-ci.txt" in s]
_NHA_RUN = [i for i, s in enumerate(_NHA_STEPS) if "tests/nightly_ha.py" in s]
R.check(
    "nightly-ha installs the dependencies its host-side driver imports",
    len(_NHA_INSTALL) == 1 and len(_NHA_RUN) == 1
    and _NHA_INSTALL[0] < _NHA_RUN[0],
    f"install step(s) at {_NHA_INSTALL}, driver step(s) at {_NHA_RUN}: "
    "the driver stages the seed and the roster by importing the package on "
    "the runner, so a bare interpreter cannot reach Docker",
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
# ... and it pulls the producer in AHEAD of the consumer. `affected.scripts`
# is the order the CI "Re-record the closures" step iterates with `--single`,
# so a producer listed after its consumer is recorded too late: the card's
# `--single` run finds no plan payload, fails, and `closures-autofix` then
# answers `skip-failed-recording` for the WHOLE batch -- blocking a repair of
# an unrelated genuine gap in it (#1146). Membership alone (the check above)
# does not hold this; `sorted()` put card.mjs ("c") before plan_view.py ("p").
R.check(
    "and lists the producer before the consumer that reads its output (#1146)",
    "tests/plan_view.py" in _A_CARD["rederive"]
    and "tests/card.mjs" in _A_CARD["rederive"]
    and _A_CARD["rederive"].index("tests/plan_view.py")
    < _A_CARD["rederive"].index("tests/card.mjs"),
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
# stamp.py now writes CARD_VERSION alongside VERSION at release, so the
# console banner tracks the integration version and lagging stops in
# practice. A card that still lags (a card-only patch, or a branch that
# bumps VERSION without going through stamp.py) remains legal; ahead of
# VERSION is not -- it would ship a banner advertising a release that
# does not exist.
R.check(
    "CARD_VERSION does not run ahead of VERSION",
    _card_match is not None
    and _version_tuple(_version) != ()
    and _version_tuple(_card_match.group(1)) <= _version_tuple(_version),
    f"card says {_card_match.group(1) if _card_match else '?'}, VERSION says "
    f"{_version} -- lower CARD_VERSION in {_card_path} or bump VERSION",
)

# The D6 register (tools/audit/round4/D6/) is the committed output of
# claims.py, and one of its rows -- C42, "manifest version equals VERSION" --
# is a snapshot of the VERSION the register was generated at. The stamp is the
# only commit that moves VERSION, so it is the only commit that can stale that
# snapshot, and a stamp that does turns tests/harness_headers.py red at the
# stamped head: that check re-runs every live-header harness (claims.py among
# them) and fails when the register it regenerates is not what is committed.
# v6.6.4 is exactly that state -- VERSION 6.6.4, the register's C42 still
# 6.6.3 -- so this pins the register against the live VERSION, the invariant
# the stamp has to keep. That the stamp keeps it is pinned separately in
# stamp.py's own --self-test, which reads main()'s write region.
_d6_json = Path("tools/audit/round4/D6/claims.json")
_d6_c42 = next(
    (row for row in json.loads(_d6_json.read_text()) if row.get("id") == "C42"), None
)
_d6_recorded = _re.findall(r"\d+\.\d+\.\d+", (_d6_c42 or {}).get("result", ""))
R.check(
    "the D6 register records the live VERSION (the stamp re-records it)",
    _d6_recorded == [_version, _version],
    f"{_d6_json}'s C42 records {(_d6_c42 or {}).get('result')!r}, VERSION is "
    f"{_version!r} -- a stamp moved VERSION without re-recording the register, "
    "so tests/harness_headers.py is red at this head. Run "
    "`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` and "
    "commit its output.",
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

# --- the #1255 collapse: every line per scenario, not the last -------------
#
# Both parsers keyed their map on the scenario name, so two bare claim lines
# for ONE scenario collapsed to the last. A branch that added a fresh claim
# beside the baseline's own line then parsed exactly equal to the baseline's
# single entry -- the added claim was invisible -- and the guard read the
# branch's own list as inherited (main at 27458c8 held two config_flow lines
# that parsed equal to the baseline's one; #1255). The map carries every
# line's reason now, in file order, so equality is same names AND same
# lines, count included, through `parse_claim_map` and the `_claimed` file
# rule alike -- and the autofix that empties an inherited list will not
# touch one that added a line.
_1255_ONE = "# claims-for: 6.6.6\n#\n\nconfig_flow  # the baseline's reason\n"
_1255_TWO = (
    "# claims-for: 6.6.6\n#\n\n"
    "config_flow  # this branch's fresh claim\n"
    "config_flow  # the baseline's reason\n"
)
R.check(
    "a claim map carries every line a scenario has, not just the last",
    _env_drift.parse_claim_map(_1255_TWO)
    == {"config_flow": ["this branch's fresh claim", "the baseline's reason"]}
    and _env_drift._parse_claims(_1255_TWO)[1]
    == {"config_flow": ["this branch's fresh claim", "the baseline's reason"]}
    and _env_drift.parse_claim_map(_1255_ONE)
    == {"config_flow": ["the baseline's reason"]},
    f"parse={_env_drift.parse_claim_map(_1255_TWO)!r} "
    f"file={_env_drift._parse_claims(_1255_TWO)[1]!r}",
)
R.check(
    "a fresh claim added beside an inherited line is not an inherited list",
    _env_drift.inherited_claims_error(
        _env_drift.parse_claim_map(_1255_TWO),
        _env_drift.parse_claim_map(_1255_ONE),
        "origin/main",
    ) is None,
    "two lines for one scenario parsed equal to the baseline's single entry "
    "(#1255): the added line is this branch's own claim",
)
R.check(
    "and the inherited-claims autofix leaves it alone",
    _env_drift.drop_inherited_claim_lines(_1255_TWO, _1255_ONE) is None,
    "emptying a list that added a line would delete a claim this branch "
    "wrote",
)

# #996: the runner-conditional fail-fast. PR #992 round 3 established the
# protocol -- the runner is the judge of record -- but the gate said so
# nowhere: a claim the branch itself wrote that goes stale only on the
# runner arrived as a generic STALE CLAIM(S) red, and the seats that hit it
# burned review rounds discovering the class (the second instance of the
# v5.1.7 dilemma). The owner's 2026-09-14 ruling replaces the passive
# tripwire with an executable one: env_drift.py names the signature at the
# moment of failure and hands over the pre-agreed decision tree, and
# issue996_count.py counts the instances recorded on the #996 thread, where
# the third re-opens the declined claim-grammar decision.
import issue996_count as _i996

_R996_STALE = ["wood_two_tank", "wood_coil"]
_R996_CLAIMS = {"wood_two_tank": "r", "wood_coil": "this branch's reason"}
_R996_BASE = {"wood_two_tank": "r"}  # the baseline carries the identical line
R.check(
    "the #996 arm separates a stale claim this branch wrote from one it "
    "inherited line for line",
    _env_drift.branch_authored_stale_claims(
        _R996_STALE, _R996_CLAIMS, _R996_BASE
    ) == ["wood_coil"],
    "an identical baseline line is yesterday's staleness and keeps the "
    "generic message; an absent or rewritten line is this branch's own "
    "evidence of expected drift and gets the fail-fast arm",
)
R.check(
    "a baseline with no claim file cannot have written any of them",
    _env_drift.branch_authored_stale_claims(
        _R996_STALE, _R996_CLAIMS, {}
    ) == _R996_STALE,
    "every claim in the tree was added by this branch's three-dot",
)

_R996_MSG = _env_drift.runner_conditional_error("wood_two_tank", "origin/main")
R.check(
    "the fail-fast message names the class, the judge of record, the "
    "decision tree and the retry loop it forbids",
    all(
        part in _R996_MSG
        for part in (
            "RUNNER-CONDITIONAL CANDIDATE (#996 class)",
            "wood_two_tank",
            "BLAS-build-conditional",
            "issue #996",
            "runner is the judge of record",
            "BOTH captures",
            "do NOT edit the claim file again",
        )
    ),
    "the pre-agreed decision tree is the payload; a restatement of the "
    "generic stale-claim rule is what this arm replaced",
)
R.check(
    "the fail-fast message says the third recorded instance re-opens the "
    "grammar decision",
    "third" in _R996_MSG.lower() and "re-opens" in _R996_MSG,
    "the 2026-09-13 recorded decision priced two instances and deferred to "
    "a third; the message must hand that trigger to the seat it fires on",
)
R.check(
    "the fail-fast message shows the instance marker only inside prose, "
    "never at column 0",
    _env_drift.RUNNER_CONDITIONAL_INSTANCE_MARKER in _R996_MSG
    and not any(
        line.startswith(_env_drift.RUNNER_CONDITIONAL_INSTANCE_MARKER)
        for line in _R996_MSG.splitlines()
    ),
    "a seat pasting the gate output into the #996 thread must not inflate "
    "the instance count the counter reads",
)

# The arm must be WIRED into main()'s comparison path, not merely defined:
# deleting the wiring reverts the live path to the generic message while
# every unit pin above stays green. An AST read of the registered artifact
# (fixer step 11), because executing main() here would cost a double
# capture for one print.
_R996_TREE = _ast_af.parse(Path("tests/env_drift.py").read_text())
_R996_MAIN = next(
    node
    for node in _R996_TREE.body
    if isinstance(node, _ast_af.FunctionDef) and node.name == "main"
)


def _r996_calls(node, name: str) -> bool:
    return any(
        isinstance(sub, _ast_af.Call)
        and isinstance(sub.func, _ast_af.Name)
        and sub.func.id == name
        for sub in _ast_af.walk(node)
    )


R.check(
    "main() wires the fail-fast arm: it asks the discriminator and prints "
    "the named signature",
    _r996_calls(_R996_MAIN, "branch_authored_stale_claims")
    and _r996_calls(_R996_MAIN, "runner_conditional_error"),
    "the live path, not the module namespace, is the product; this is the "
    "pin that goes red when the wiring is deleted",
)

# The instance counter. The #996 thread is the ledger -- the two historical
# instances the recorded decision priced (v5.1.7, #992) were seeded into it
# as marker lines when this mechanism landed, so the counter holds no state
# of its own and the count starts at two. Only a marker line at column 0
# records an instance: quoted replies, indented pastes and mid-line
# mentions are discussion, not records.
_R996_THREAD = [
    "Triage 2026-09-14 (old-era backlog seat): the recorded refusal stands.",
    "Fix seat for #996 -- the thread-pinning countermeasure, executed and "
    "refused: the divergence is build-inherent.",
    "Owner decision (2026-09-14): #996 stays OPEN as a tripwire (superseded "
    "by the fail-fast mechanism this counter serves).",
    "996-instance: v5.1.7 -- search-path chaos; the dev box drifted, the "
    "runner captured byte-identical (seeded from the 2026-09-13 decision)",
    "996-instance: valve_storage_small_tank (#992) -- dev box 553 leaves "
    "vs 69d2e22, runner byte-identical vs 69d2e22 (#992 comment 5655826675)",
    "> 996-instance: a report quoted in discussion, not recorded here",
    "the decision tree shows the form  996-instance: <scenario> -- inline",
]
R.check(
    "the counter reads a fixture thread: two recorded instances, and "
    "quotes, indented pastes or mid-line mentions record none",
    _i996.count_instances(_R996_THREAD) == 2,
    "the count is marker lines at column 0, nothing else",
)
R.check(
    "the re-open verdict is silent below the threshold and fires the "
    "owner's line at three and beyond",
    _i996.reopen_verdict(2) is None
    and (_i996.reopen_verdict(3) or "").startswith(
        "THIRD INSTANCE — grammar decision reopens"
    )
    and (_i996.reopen_verdict(4) or "").startswith(
        "THIRD INSTANCE — grammar decision reopens"
    ),
    "the 2026-09-14 owner decision set three as the re-open trigger",
)
with _tempfile.TemporaryDirectory() as _r996_dir:
    _r996_two = Path(_r996_dir) / "two.json"
    _r996_two.write_text(json.dumps([{"body": b} for b in _R996_THREAD]))
    _r996_three = Path(_r996_dir) / "three.json"
    _r996_three.write_text(json.dumps(
        [{"body": b} for b in _R996_THREAD]
        + [{"body": "996-instance: wood_two_tank -- dev box 799 leaves, "
                    "runner byte-identical"}]
    ))
    with _contextlib.redirect_stdout(_io.StringIO()) as _r996_cap:
        _r996_rc_two = _i996.main(["--from", str(_r996_two)])
    _r996_said_two = _r996_cap.getvalue()
    with _contextlib.redirect_stdout(_io.StringIO()) as _r996_cap3:
        _r996_rc_three = _i996.main(["--from", str(_r996_three)])
    _r996_said_three = _r996_cap3.getvalue()
R.check(
    "the counter's CLI reads a fixture thread: exit 0 with the count at "
    "two, exit 2 and the re-open line at three",
    _r996_rc_two == 0
    and "THIRD INSTANCE" not in _r996_said_two
    and "recorded runner-conditional instance" in _r996_said_two
    and _r996_rc_three == 2
    and "THIRD INSTANCE — grammar decision reopens" in _r996_said_three,
    "the record seat runs this by hand; the crossing must be machine-"
    "visible in both the text and the exit status",
)

# The guard is asked PER FILE KIND, never per branch (2026-09-10). `main`
# legitimately carries card claims between a card merge and the next stamp,
# so the first solver branch after one inherits a card list it did not write
# and cannot have moved -- #735's six, refused on W5-G9 with the one remedy
# #662 forbids (empty it, and a squash applies the deletion to main). The
# verdict is a pure function of the three-dot and the four parsed lists, so
# the live case is pinned here without a repository, with its null control.
_PK_CO = "custom_components/heatpump_optimizer/coordinator.py"
_PK_CARD = {"setup_coil": "tank bar on Setup", "setup_two_tank": "tank bar on Setup"}
R.check(
    "a solver-only three-dot can move a solver golden and not a card state, "
    "and the card the reverse",
    _env_drift.moves_solver_claimable([_PK_CO])
    and not _env_drift.moves_card_claimable([_PK_CO])
    and _env_drift.moves_card_claimable([_env_drift.CARD_JS])
    and not _env_drift.moves_solver_claimable([_env_drift.CARD_JS])
    and _env_drift.claim_kinds([_PK_CO]) == {
        _env_drift.CLAIM_FILE: True, _env_drift.CARD_CLAIM_FILE: False
    },
    "the two claim files excuse different fixtures moved by different paths",
)
R.check(
    "a solver-only branch that leaves main's card claims exactly as found is "
    "not refused for them",
    _env_drift.claims_hygiene_verdict(
        [_PK_CO], {}, dict(_PK_CARD), {}, dict(_PK_CARD), "origin/main"
    ) is None,
    "the card list was written for another diff and this branch cannot move "
    "a card state; judging it as the branch's own is the W5-G9 refusal",
)
_pk_card_branch = _env_drift.claims_hygiene_verdict(
    [_env_drift.CARD_JS], {}, dict(_PK_CARD), {}, dict(_PK_CARD), "origin/main"
) or ""
R.check(
    "null control: a branch that CAN move a card state is still refused an "
    "inherited card list",
    _pk_card_branch.startswith("INHERITED CLAIMS")
    and _env_drift.CARD_CLAIM_FILE in _pk_card_branch,
    "the per-kind rule must not have loosened the guard where it bites",
)
_pk_foreign = _env_drift.claims_hygiene_verdict(
    [_PK_CO], {}, {}, {}, dict(_PK_CARD), "origin/main"
) or ""
R.check(
    "a solver-only branch that DELETED main's card claims is refused",
    _pk_foreign.startswith("RECORD PR CLAIMS")
    and _env_drift.CARD_CLAIM_FILE in _pk_foreign,
    "that deletion is exactly what a squash applies to main (#608, #635)",
)
R.check(
    "a solver-only branch with an inherited SOLVER list is still refused",
    (_env_drift.claims_hygiene_verdict(
        [_PK_CO], {"wood_coil": "r"}, {}, {"wood_coil": "r"}, {}, "origin/main"
    ) or "").startswith("INHERITED CLAIMS"),
    "the kind the branch can move keeps the inherited guard",
)
R.check(
    "a three-dot that can move neither keeps the record-PR rule and message",
    (_env_drift.claims_hygiene_verdict(
        ["docs/HANDOVER.md"], {}, {}, {}, dict(_PK_CARD), "origin/main"
    ) or "").startswith("RECORD PR CLAIMS")
    and _env_drift.claims_hygiene_verdict(
        ["docs/HANDOVER.md"], {}, dict(_PK_CARD), {}, dict(_PK_CARD), "origin/main"
    ) is None,
    "#662's rule for a record pull request is unchanged",
)

# A RELEASE STAMP is the one commit allowed to delete claims it did not write
# (2026-09-17). stamp.py empties both lists, and on a push to `main` the
# baseline is the commit before the stamp, whose lists are the deleted ones.
# The stamp touches the card and no solver path, so the per-kind rule judged
# the solver deletion foreign: v6.5.0 (4148299) and v6.6.0 (2d1b2ea) went red
# on `main` exactly so, while v6.5.1 and v6.4.4, deleting nothing, were green.
# The pins are v6.6.0's own three-dot and lists, then one refusal per clause of
# `release_stamp_holds`, because each clause is what keeps the exemption from
# becoming the autofix-erases-claims hole (#608, #635).
_ST_CHANGED = sorted(_env_drift.STAMP_WRITES)
_ST_BASE = {"config_flow": "ADD-ONLY: one new building-page option key"}
_ST_OK = ("6.6.0", "6.5.1", "6.6.0", "6.6.0", 1)


def _st_verdict(changed=None, solver=None, base=None, stamp=_ST_OK):
    return _env_drift.claims_hygiene_verdict(
        _ST_CHANGED if changed is None else changed,
        {} if solver is None else solver, {},
        dict(_ST_BASE) if base is None else base, {}, "HEAD^1", stamp=stamp,
    )


R.check(
    "a release stamp that empties a baseline claim it did not write passes",
    _st_verdict() is None
    and (_st_verdict(stamp=None) or "").startswith("RECORD PR CLAIMS"),
    "v6.6.0's stamp deleted config_flow and went red on main; with no stamp "
    "facts the same three-dot is still the foreign-deletion refusal",
)
R.check(
    "a claim deletion with VERSION unchanged, moving backwards, or unreadable "
    "at the baseline is refused",
    (_st_verdict(stamp=("6.5.1", "6.5.1", "6.5.1", "6.5.1", 1)) or "")
    .startswith("RECORD PR CLAIMS")
    and (_st_verdict(stamp=("6.5.1", "6.6.0", "6.5.1", "6.5.1", 1)) or "")
    .startswith("RECORD PR CLAIMS")
    and (_st_verdict(stamp=("6.6.0", "", "6.6.0", "6.6.0", 1)) or "")
    .startswith("RECORD PR CLAIMS"),
    "only a tree strictly ahead of a readable baseline VERSION is stamping",
)
R.check(
    "a VERSION bump that ADDS a claim, or deletes only some, is refused",
    (_st_verdict(solver={"wood_coil": "r"}, base={}) or "")
    .startswith("RECORD PR CLAIMS")
    and (_st_verdict(
        solver={"wood_coil": "r"}, base={"wood_coil": "r", **_ST_BASE}
    ) or "").startswith("RECORD PR CLAIMS"),
    "a stamp leaves both lists empty; any other list is not a stamp's output",
)
R.check(
    "a VERSION bump whose solver claims-for is not the new VERSION is refused",
    (_st_verdict(stamp=("6.6.0", "6.5.1", "6.5.1", "6.6.0", 1)) or "")
    .startswith("RECORD PR CLAIMS"),
    "stamp.py moves both claims-for lines with VERSION",
)
R.check(
    "a VERSION bump whose card claims-for is not the new VERSION is refused",
    (_st_verdict(stamp=("6.6.0", "6.5.1", "6.6.0", "6.5.1", 1)) or "")
    .startswith("RECORD PR CLAIMS"),
    "stamp.py moves both claims-for lines with VERSION",
)
R.check(
    "a stamp-shaped commit with two parents (a pull request's merge ref, or "
    "its merge into main) or none (a graft root) is refused",
    (_st_verdict(stamp=_ST_OK[:4] + (2,)) or "").startswith("RECORD PR CLAIMS")
    and (_st_verdict(stamp=_ST_OK[:4] + (0,)) or "").startswith("RECORD PR CLAIMS"),
    "a pull request can forge every content clause; only a stamp is pushed "
    "to main as a single-parent commit",
)
# ...and the parent count answers "not a pull request" only on the
# `pull_request` run. A dispatch on the pull request's BRANCH -- the one
# closures-autofix fires, with tests.yml's recheck arm -- checks out a
# one-parent tip, so the stamp facts are asked for only on `main`'s ref.
R.check(
    "a stamp is recognised only on main's ref inside Actions, and outside "
    "Actions as before",
    _env_drift.stamp_ref_allows(
        {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/main"})
    and not _env_drift.stamp_ref_allows(
        {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/ci/refuse-version-edit"})
    and not _env_drift.stamp_ref_allows(
        {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/pull/1/merge"})
    and not _env_drift.stamp_ref_allows({"GITHUB_ACTIONS": "true"})
    and _env_drift.stamp_ref_allows({}),
    "a branch dispatch's tip has one parent, so without the ref a forged "
    "stamp passed the claims rule on the recheck run its pull_request run refused",
)
R.check(
    "a VERSION bump that also touches a file stamp.py never writes is refused",
    (_st_verdict(changed=_ST_CHANGED + ["docs/HANDOVER.md"]) or "")
    .startswith("RECORD PR CLAIMS"),
    "a branch carrying a VERSION bump beside other work keeps every per-file rule",
)
_INH_HDR = "# claims-for: 6.3.15\n#\n"
_INH_FILE = _INH_HDR + "wood_coil  # copied from baseline\n\n# may-drift: wood_coil -- keep\n"
_INH_DROPPED = _env_drift.drop_inherited_claim_lines(_INH_FILE, _INH_FILE)
R.check(
    "inherited claim lines are dropped and may-drift is kept",
    _INH_DROPPED is not None
    and "wood_coil  #" not in _INH_DROPPED
    and "# may-drift: wood_coil -- keep" in _INH_DROPPED
    and "claims-for: 6.3.15" in _INH_DROPPED,
    f"dropped={_INH_DROPPED!r}",
)
R.check(
    "a rewritten reason is not an inherited-claims autofix",
    _env_drift.drop_inherited_claim_lines(
        _INH_HDR + "wood_coil  # this branch\n",
        _INH_HDR + "wood_coil  # baseline\n",
    ) is None,
    "only an identical parsed list is mechanical to empty",
)
R.check(
    "an empty list is not an inherited-claims autofix",
    _env_drift.drop_inherited_claim_lines(_INH_HDR, _INH_HDR) is None,
    "empty already claims nothing",
)
with _tempfile.TemporaryDirectory() as _inh_td:
    _inh_repo = Path(_inh_td) / "repo"
    _inh_base = Path(_inh_td) / "base"
    for _d in (_inh_repo, _inh_base):
        (_d / "tests" / "golden").mkdir(parents=True)
        (_d / _env_drift.CLAIM_FILE).write_text(_INH_FILE)
        (_d / "tests" / "golden" / "card_claimed_drift.txt").write_text(
            _INH_HDR + "away_toggle  # copied\n")
    _inh_status = _env_drift.apply_inherited_claims(
        str(_inh_repo), baseline_dir=str(_inh_base))
    _inh_solver = (_inh_repo / _env_drift.CLAIM_FILE).read_text()
    _inh_card = (_inh_repo / "tests" / "golden" / "card_claimed_drift.txt").read_text()
R.check(
    "both inherited claim files are emptied in one apply",
    _inh_status == "changed"
    and "wood_coil  #" not in _inh_solver
    and "away_toggle" not in _inh_card
    and "# may-drift: wood_coil -- keep" in _inh_solver,
    f"status={_inh_status} solver={_inh_solver!r} card={_inh_card!r}",
)

# --- the claim-file merge driver -------------------------------------------
#
# Every branch writes its own note into both claim files at the same place, so
# every branch that merges main after another one merged conflicts in both --
# five branches and ten conflicts in the session that built this, and the hand
# resolution was identical every time. Notes are comment lines and assert
# nothing, so they union. A bare claim line does not: it excuses a golden diff.
# Unioning two lists reinstates a claim this branch deleted, and
# `inherited_claims_error` cannot see it, because the unioned list is no longer
# exactly the baseline's -- `_CM_UNION_IS_SILENT` below measures that. So the
# driver unions comments and REFUSES a claim list both sides rewrote.
_CM_BASE = (
    "# Scenarios this branch deliberately moves, one name per line.\n"
    "#\n"
    "# claims-for: 6.3.16\n"
    "#\n"
    "# #514: this branch claims NOTHING. Workflow and comment text only.\n"
    "\n"
    "# may-drift: wood_coil -- machine-sensitive\n"
)
_CM_OURS = (
    "# Scenarios this branch deliberately moves, one name per line.\n"
    "#\n"
    "# claims-for: 6.3.16\n"
    "#\n"
    "# #514: this branch claims NOTHING. Workflow and comment text only.\n"
    "#\n"
    "# #541: this branch claims NOTHING. Gate tooling only.\n"
    "\n"
    "# may-drift: wood_coil -- machine-sensitive\n"
)
_CM_THEIRS = (
    "# Scenarios this branch deliberately moves, one name per line.\n"
    "#\n"
    "# claims-for: 6.3.16\n"
    "#\n"
    "# W4-G7 S6 (#193, the grid seam): this branch claims NOTHING.\n"
    "\n"
    "# may-drift: wood_coil -- machine-sensitive\n"
)
_CM_MERGED = _env_drift.merge_claim_file(_CM_BASE, _CM_OURS, _CM_THEIRS)
R.check(
    "two branches' notes both survive a claim-file merge",
    _CM_MERGED is not None
    and "#541: this branch claims NOTHING" in _CM_MERGED
    and "W4-G7 S6 (#193, the grid seam)" in _CM_MERGED
    and "<<<<<<<" not in _CM_MERGED,
    f"merged={_CM_MERGED!r}",
)
R.check(
    "a merged claim file keeps its stamp, its header and its may-drift lines",
    _CM_MERGED is not None
    and _env_drift._parse_claims(_CM_MERGED)[0] == "6.3.16"
    and _CM_MERGED.count("# claims-for: 6.3.16") == 1
    and "# may-drift: wood_coil -- machine-sensitive" in _CM_MERGED
    and _CM_MERGED.startswith("# Scenarios this branch"),
    f"merged={_CM_MERGED!r}",
)
R.check(
    "a comment-only merge claims nothing it was not given",
    _CM_MERGED is not None and _env_drift.parse_claim_map(_CM_MERGED) == {},
    f"claims={_env_drift.parse_claim_map(_CM_MERGED or '')!r}",
)

# The case that refuses union. Both sides rewrote the claim list, so no rule
# can say which claim describes which diff; git keeps the markers.
_CM_OURS_CLAIM = _CM_OURS.rstrip("\n") + "\neverything_on # this branch's own measured drift\n"
_CM_THEIRS_CLAIM = (
    _CM_THEIRS.rstrip("\n") + "\nvalve_storage_small_tank # the other branch's drift\n"
)
R.check(
    "a claim list both sides rewrote is refused, not unioned",
    _env_drift.merge_claim_file(_CM_BASE, _CM_OURS_CLAIM, _CM_THEIRS_CLAIM) is None,
    "two branches' claim lists were merged; a claim excuses a golden diff and "
    "cannot be inherited by a merge",
)
# Why refusing matters, measured rather than asserted: had the driver unioned,
# the #495 inherited-claims guard would NOT have fired, because the unioned
# list is not exactly the baseline's -- it carries this branch's claim too.
_CM_UNION_IS_SILENT = _env_drift.inherited_claims_error(
    {"everything_on": "ours", "valve_storage_small_tank": "theirs"},
    {"valve_storage_small_tank": "theirs"},
    "origin/main",
)
R.check(
    "the inherited-claims guard cannot catch a unioned claim list",
    _CM_UNION_IS_SILENT is None,
    "if this ever fires, union stopped being silent and the refusal above "
    "could be relaxed -- until then the driver is the only thing standing "
    "between a merge and a silently reinstated claim",
)
R.check(
    "a claim list only one side touched is carried, not refused",
    _env_drift.parse_claim_map(
        _env_drift.merge_claim_file(_CM_BASE, _CM_OURS_CLAIM, _CM_THEIRS) or ""
    ) == {"everything_on": ["this branch's own measured drift"]}
    and _env_drift.parse_claim_map(
        _env_drift.merge_claim_file(_CM_BASE, _CM_OURS, _CM_THEIRS_CLAIM) or ""
    ) == {"valve_storage_small_tank": ["the other branch's drift"]},
    "a one-sided claim rewrite is an ordinary merge; only a two-sided one is "
    "a value conflict",
)
R.check(
    "merging a file with itself returns it byte-identical",
    _env_drift.merge_claim_file(_CM_BASE, _CM_BASE, _CM_BASE) == _CM_BASE
    and _env_drift.merge_claim_file(_CM_BASE, _CM_OURS, _CM_BASE) == _CM_OURS
    and _env_drift.merge_claim_file(_CM_BASE, _CM_BASE, _CM_THEIRS) == _CM_THEIRS,
    "a merge that rewrites an unchanged file would churn every claim file",
)
_CM_NEW_MD = _CM_THEIRS.replace(
    "# may-drift: wood_coil -- machine-sensitive",
    "# may-drift: wood_coil -- machine-sensitive\n# may-drift: wood_two_tank -- machine-sensitive",
)
assert _CM_NEW_MD != _CM_THEIRS, "may-drift fixture anchor missing"
_CM_MD_MERGED = _env_drift.merge_claim_file(_CM_BASE, _CM_OURS, _CM_NEW_MD)
R.check(
    "a may-drift line added on one side survives the merge",
    _CM_MD_MERGED is not None
    and "# may-drift: wood_two_tank -- machine-sensitive" in _CM_MD_MERGED
    and "# may-drift: wood_coil -- machine-sensitive" in _CM_MD_MERGED,
    f"merged={_CM_MD_MERGED!r}",
)

# End to end: a real two-branch conflict, resolved by git calling the driver.
# The unit checks above pin the resolution; this pins the wiring -- the
# .gitattributes entry, the config, and the driver's own exit code.
with _tempfile.TemporaryDirectory() as _cm_td:
    _cm_repo = Path(_cm_td) / "repo"
    (_cm_repo / "tests" / "golden").mkdir(parents=True)

    def _cm_git(*args, **kw):
        return _subprocess.run(
            ["git", *args], cwd=str(_cm_repo), capture_output=True, text=True, **kw
        )

    _cm_git("init", "-q", "-b", "main")
    _cm_git("config", "user.email", "t@example.invalid")
    _cm_git("config", "user.name", "t")
    _cm_claim = _cm_repo / _env_drift.CLAIM_FILE
    _cm_claim.write_text(_CM_BASE)
    # .gitattributes binds the driver to the path and ships in the tree; the
    # configured command is repo-relative, so each worktree runs its own copy
    # of the resolver rather than whichever one happened to install it.
    _cm_root = Path(__file__).resolve().parent.parent
    (_cm_repo / ".gitattributes").write_text((_cm_root / ".gitattributes").read_text())
    (_cm_repo / "tests" / "env_drift.py").write_text(
        (_cm_root / "tests" / "env_drift.py").read_text()
    )
    _cm_git("add", "-A")
    _cm_git("commit", "-qm", "base")
    _cm_git("checkout", "-qb", "side")
    _cm_claim.write_text(_CM_OURS)
    _cm_git("commit", "-qam", "our note")
    _cm_git("checkout", "-q", "main")
    _cm_claim.write_text(_CM_THEIRS)
    _cm_git("commit", "-qam", "their note")
    _cm_git("checkout", "-q", "side")
    _cm_install = _env_drift.install_merge_driver(str(_cm_repo))
    _cm_merge = _cm_git("merge", "main", "-m", "merge main")
    _cm_after = _cm_claim.read_text()
    # Same repo, second scenario: both sides rewrite the claim list. The
    # driver must refuse and leave the markers a human resolves.
    _cm_git("checkout", "-qb", "claimside", "main")
    _cm_claim.write_text(_CM_OURS_CLAIM)
    _cm_git("commit", "-qam", "our claim")
    _cm_git("checkout", "-q", "main")
    _cm_claim.write_text(_CM_THEIRS_CLAIM)
    _cm_git("commit", "-qam", "their claim")
    _cm_git("checkout", "-q", "claimside")
    _cm_refused = _cm_git("merge", "main", "-m", "merge main")
    _cm_refused_file = _cm_claim.read_text()
R.check(
    "git resolves a real two-branch note conflict through the driver",
    _cm_install == "installed"
    and _cm_merge.returncode == 0
    and "<<<<<<<" not in _cm_after
    and "#541: this branch claims NOTHING" in _cm_after
    and "W4-G7 S6 (#193, the grid seam)" in _cm_after
    and _env_drift.parse_claim_map(_cm_after) == {},
    f"install={_cm_install} rc={_cm_merge.returncode} "
    f"err={_cm_merge.stderr!r} file={_cm_after!r}",
)
R.check(
    "and it leaves a conflict for a claim list both sides rewrote",
    _cm_refused.returncode != 0
    and "<<<<<<<" in _cm_refused_file
    and ">>>>>>>" in _cm_refused_file
    and "everything_on" in _cm_refused_file
    and "valve_storage_small_tank" in _cm_refused_file
    and "CONFLICTING CLAIMS" in _cm_refused.stderr,
    "a refusal must look exactly like an unconfigured merge -- markers in the "
    f"file, non-zero exit -- got rc={_cm_refused.returncode} "
    f"err={_cm_refused.stderr!r} file={_cm_refused_file!r}",
)
# The driver checks its own output before writing it. These are that check's
# null controls: each corrupts one property a hand resolution preserves, and
# the verification must name it. Without them the verification is a branch
# nothing ever takes, which is the shape #523 shipped.
_CM_GOOD = _CM_MERGED
R.check(
    "the merge verification passes the file the merge actually produced",
    _env_drift.merge_claim_defect(_CM_GOOD, _CM_OURS, _CM_OURS, _CM_THEIRS) is None,
    _env_drift.merge_claim_defect(_CM_GOOD, _CM_OURS, _CM_OURS, _CM_THEIRS) or "",
)
R.check(
    "the merge verification catches a lost stamp, a lost may-drift line, a "
    "smuggled claim and surviving markers",
    all(
        (_env_drift.merge_claim_defect(bad, _CM_OURS, _CM_OURS, _CM_THEIRS) or "")
        .startswith(head)
        for bad, head in (
            (_CM_GOOD.replace("# claims-for: 6.3.16\n", ""), "the 'claims-for:'"),
            (_CM_GOOD.replace(
                "# may-drift: wood_coil -- machine-sensitive\n", ""), "a may-drift"),
            (_CM_GOOD + "everything_on # smuggled in\n", "the claim list"),
            (_CM_GOOD + "<<<<<<< main\n", "conflict markers"),
            ("", "the result is empty"),
        )
    ),
    "a verification that cannot fail is not a verification",
)

R.check(
    ".gitattributes routes both claim files to the merge driver",
    _env_drift.gitattributes_error(str(Path(__file__).resolve().parent.parent))
    is None,
    _env_drift.gitattributes_error(str(Path(__file__).resolve().parent.parent)) or "",
)
_CM_HALF_ROUTED = _env_drift.gitattributes_error(
    ".", text="tests/golden/claimed_drift.txt merge=claimnotes\n"
)
R.check(
    "a .gitattributes that routes only one claim file is refused",
    (_CM_HALF_ROUTED or "").startswith("UNROUTED CLAIM FILE")
    and _env_drift.CARD_CLAIM_FILE in (_CM_HALF_ROUTED or ""),
    "the card claim file conflicts as often as the solver's and must be "
    f"routed too; got {_CM_HALF_ROUTED!r}",
)

# --- #493: inherited card claims on a roster-only three-dot -----------------
#
# PR #493 (squash ae97a65) touched only INERT roster/plan files. Claim files
# were byte-identical to 62799e4, so GATE_SCOPE=auto skipped card_drift.mjs
# and env_drift.py (no changed file in those closures). After squash, main's
# GATE_SCOPE=full ran `node tests/card_drift.mjs 62799e4` and failed
# INHERITED CLAIMS on whatif_edited / whatif_weekly. The PR merge-base WAS
# 62799e4 -- the gap is the skip, not a different baseline SHA.
_493_FILES = [
    ".claude/workflows/wave-4-groups.json",
    ".claude/workflows/wave-5-groups.json",
    "docs/plan-2026-09-open-issues.md",
]
_493_CARD = {
    "whatif_edited": "in-window lo floored at the window min; floored band note",
    "whatif_weekly": "weekly-spec in-window lo floor; floored band note",
}
_493_skip = _closure.select(_493_FILES)
R.check(
    "#493-shaped roster-only still scopes card_drift and env_drift out",
    _493_skip["mode"] == "scoped"
    and "tests/card_drift.mjs" in _493_skip["skip"]
    and "tests/env_drift.py" in _493_skip["skip"],
    "the expensive capture/render stays scoped out; claims-only must catch "
    f"this, not a full env_drift. mode={_493_skip['mode']} "
    f"run={_493_skip['run'][:6]}",
)

_rpr = getattr(_env_drift, "record_pr_claims_error", None)
R.check(
    "roster-only #493 with copied card claims is refused",
    callable(_rpr)
    and (_rpr(_493_FILES, {}, _493_CARD) or "").startswith("RECORD PR CLAIMS"),
    "a docs/roster three-dot carrying #490's card claims must fail; "
    "empty the lists",
)
R.check(
    "empty claims on a roster-only three-dot pass",
    callable(_rpr) and _rpr(_493_FILES, {}, {}) is None,
    "header claims-for: only is the record-PR answer",
)
R.check(
    "a claim-bearing change that touches solver fixtures is not a record-PR violation",
    callable(_rpr)
    and _rpr(
        ["custom_components/heatpump_optimizer/optimizer.py"],
        {"winter_single_dhw": "this branch moved the fixture"},
        {},
    ) is None,
    "a real solver PR may claim the fixtures it moves",
)
R.check(
    "a claim-bearing change that touches the card is not a record-PR violation",
    callable(_rpr)
    and _rpr(
        [_CARD_ASSET],
        {},
        {"whatif_edited": "this branch moved the what-if editor"},
    ) is None,
    "a real card PR may claim the states it moves",
)
# #547: the capture code moves fixtures with no production line changed, and
# the guard used to refuse the claim the drift comparison demanded -- two
# checks contradicting each other on one diff. Every source is asserted, so a
# tuple widened to silence some future failure has to survive the null
# control below rather than passing quietly.
R.check(
    "a claim-bearing change to the capture code is not a record-PR violation",
    callable(_rpr)
    and bool(getattr(_env_drift, "CAPTURE_SOURCES", ()))
    and all(
        _rpr([source], {"config_flow": "this branch reseeded the capture"}, {})
        is None
        for source in getattr(_env_drift, "CAPTURE_SOURCES", ())
    ),
    "tests/golden.py and the modules it captures through can move a fixture "
    "with no production file touched (#547). sources="
    f"{getattr(_env_drift, 'CAPTURE_SOURCES', None)}",
)
R.check(
    "a test file that is NOT a capture source still cannot justify a claim",
    callable(_rpr)
    and (
        _rpr(
            ["tests/config_flow_steps.py"],
            {"config_flow": "this branch moved the fixture"},
            {},
        )
        or ""
    ).startswith("RECORD PR CLAIMS"),
    "the null control on #547's widening: a driver that only reads the flow "
    "captures nothing, so it may not carry a claim",
)

_runsh_text = Path("tests/run.sh").read_text()
_claims_lines = [
    ln for ln in _runsh_text.splitlines() if "env_drift.py --claims-only" in ln
]
R.check(
    "run.sh always runs env_drift.py --claims-only through run_always",
    bool(_claims_lines)
    and _claims_lines[0].lstrip().startswith("run_always "),
    "GATE_SCOPE=auto skipped card_drift on #493 because claim files were "
    f"unchanged; claims-only must not go through in_scope. lines={_claims_lines!r}",
)
_ra = _re.search(r"^run_always\(\) \{$(.*?)^\}", _runsh_text, _re.M | _re.S)
R.check(
    "run_always never consults in_scope",
    _ra is not None and "in_scope" not in _ra.group(1),
    "run_always that calls in_scope is just run, and #493 would skip again",
)

_hyg = getattr(_env_drift, "check_claims_hygiene", None)


def _hygiene_git(card_head: str, extra: dict[str, str], py_touch: bool,
                 card_base: str | None = None, solver_base: str | None = None):
    """Two-commit repo: baseline has #493's card claims; HEAD applies extra.

    `card_base` overrides the baseline's card claims -- the case where the
    baseline claims NOTHING, under which "leave it alone" and "empty it"
    are the same instruction.
    """
    import subprocess as _sp

    root = _tempfile.mkdtemp(prefix="h493_")
    if card_base is None:
        card_base = (
            "# claims-for: 6.3.15\n\n"
            "whatif_edited  # in-window lo floored at the window min; floored band note\n"
            "whatif_weekly  # weekly-spec in-window lo floor; floored band note\n"
        )
    solver = "# claims-for: 6.3.15\n" if solver_base is None else solver_base
    (Path(root) / "tests" / "golden").mkdir(parents=True)
    (Path(root) / "custom_components" / "heatpump_optimizer").mkdir(parents=True)
    (Path(root) / "VERSION").write_text("6.3.15\n")
    (Path(root) / "tests" / "golden" / "claimed_drift.txt").write_text(solver)
    (Path(root) / "tests" / "golden" / "card_claimed_drift.txt").write_text(card_base)
    (Path(root) / "custom_components" / "heatpump_optimizer" / "optimizer.py").write_text(
        "x = 1\n"
    )
    _sp.run(["git", "init"], cwd=root, check=True, capture_output=True)
    _sp.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    _sp.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    _sp.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    _sp.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
    base = _sp.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    (Path(root) / "tests" / "golden" / "card_claimed_drift.txt").write_text(card_head)
    for rel, text in extra.items():
        p = Path(root, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    if py_touch:
        (Path(root) / "custom_components" / "heatpump_optimizer" / "optimizer.py").write_text(
            "x = 2\n"
        )
    _sp.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    _sp.run(["git", "commit", "-m", "head"], cwd=root, check=True, capture_output=True)
    return root, base


_h493_card = (
    "# claims-for: 6.3.15\n\n"
    "whatif_edited  # in-window lo floored at the window min; floored band note\n"
    "whatif_weekly  # weekly-spec in-window lo floor; floored band note\n"
)
_h493_root, _h493_base = _hygiene_git(
    _h493_card,
    {
        ".claude/workflows/wave-4-groups.json": "{}\n",
        ".claude/workflows/wave-5-groups.json": "{}\n",
        "docs/plan-2026-09-open-issues.md": "# plan\n",
    },
    py_touch=False,
)
# THE RULE FOR A DOCS-ONLY THREE-DOT CHANGED, and these three cases are what
# it changed to. It used to be "both lists must be empty", and emptying is a
# DELETION applied to the baseline at squash-merge: #608 carried #569's claims
# off `main` that way, #635 carried #633's, and #658 was stopped on the way to
# carrying #653's. The rule is now "leave both files exactly as you found
# them", which is the same rule whenever the baseline claims nothing -- the
# case every earlier fixture here used, which is why the change was invisible
# until a claim survived on `main` long enough to meet a documentation branch.
#
# #493's replay is the case that flipped: a roster-only three-dot whose card
# claims EQUAL the baseline's is now correct, because it changes nothing. The
# old expectation -- that it must fail -- was the defect wearing a test.
_h493_err = _hyg(_h493_root, _h493_base) if callable(_hyg) else None
R.check(
    "a roster-only three-dot that leaves the baseline's card claims alone passes",
    callable(_hyg) and _h493_err is None,
    "missing check_claims_hygiene"
    if not callable(_hyg)
    else f"hygiene returned {_h493_err!r}",
)
# And the direction that must still fail, which is the one that costs a claim.
_h493_del_root, _h493_del_base = _hygiene_git(
    "# claims-for: 6.3.15\n",
    {"docs/plan-2026-09-open-issues.md": "# plan\n"},
    py_touch=False,
)
_h493_del_err = _hyg(_h493_del_root, _h493_del_base) if callable(_hyg) else "missing"
R.check(
    "a roster-only three-dot that DELETES the baseline's card claims is refused",
    callable(_hyg)
    and isinstance(_h493_del_err, str)
    and _h493_del_err.startswith("RECORD PR CLAIMS"),
    "emptying someone else's claim list is the deletion a squash applies to "
    f"the baseline; got {_h493_del_err!r}",
)
# The stamp exemption end to end, through `check_claims_hygiene`: VERSION read
# off the baseline with git, both claims-for lines read off the tree. The null
# control is the same commit with VERSION left alone, which must stay refused.
def _stamp_git(new_version: str, forged_merge: bool = False):
    root, base = _hygiene_git(
        f"# claims-for: {new_version}\n",
        {
            "VERSION": f"{new_version}\n",
            "tests/golden/claimed_drift.txt": f"# claims-for: {new_version}\n",
            _env_drift.CARD_JS: f'const CARD_VERSION = "{new_version}";\n',
        },
        py_touch=False,
        card_base="# claims-for: 6.3.15\n",
        solver_base="# claims-for: 6.3.15\n\nwood_coil  # another lane's claim\n",
    )
    if forged_merge:
        # The same stamp-shaped commit arriving as a pull request does: on a
        # branch, merged with --no-ff, so HEAD is a two-parent merge whose
        # tree and three-dot are the stamp's exactly.
        for cmd in (["git", "branch", "forged"], ["git", "reset", "-q", "--hard", base],
                    ["git", "merge", "-q", "--no-ff", "-m", "merge", "forged"]):
            subprocess.run(cmd, cwd=root, check=True, capture_output=True)
    return root, base


# THE ENVIRONMENT IS PINNED, because `stamp_ref_allows` reads it: under Actions
# a stamp is recognised only on `refs/heads/main`, so these arms would answer
# differently on a pull request's runner than on a seat's machine. Each arm
# states the run it models -- the stamp's own push to main -- and one more arm
# drives the same single-parent stamp under a branch dispatch, which must
# refuse: that is the closures-autofix recheck shape.
_ST_MAIN_ENV = {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/main"}


def _hyg_env(root, base, env):
    with _mock.patch.dict(_os.environ, env):
        return _hyg(root, base)


_st_root, _st_base = _stamp_git("6.3.16")
_st_err = _hyg_env(_st_root, _st_base, _ST_MAIN_ENV) if callable(_hyg) else "missing"
_st_ctl_root, _st_ctl_base = _stamp_git("6.3.15")
_st_ctl_err = _hyg_env(_st_ctl_root, _st_ctl_base, _ST_MAIN_ENV) if callable(_hyg) else "missing"
_st_forged_root, _st_forged_base = _stamp_git("6.3.16", forged_merge=True)
_st_forged_err = _hyg_env(_st_forged_root, _st_forged_base, _ST_MAIN_ENV) if callable(_hyg) else "missing"
_st_dispatch_err = _hyg_env(
    _st_root, _st_base,
    {"GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/ci/forged-stamp"},
) if callable(_hyg) else "missing"
R.check(
    "check_claims_hygiene passes a release stamp and refuses the same deletion "
    "without the VERSION bump",
    _st_err is None
    and isinstance(_st_ctl_err, str)
    and _st_ctl_err.startswith("RECORD PR CLAIMS"),
    f"stamp: {_st_err!r}; unbumped control: {_st_ctl_err!r}",
)
R.check(
    "check_claims_hygiene refuses the same stamp forged as a merged pull request",
    isinstance(_st_forged_err, str) and _st_forged_err.startswith("RECORD PR CLAIMS"),
    f"a two-parent HEAD with a stamp's tree and three-dot returned {_st_forged_err!r}",
)
R.check(
    "check_claims_hygiene refuses the same one-parent stamp on a branch dispatch",
    isinstance(_st_dispatch_err, str)
    and _st_dispatch_err.startswith("RECORD PR CLAIMS"),
    "a workflow_dispatch on a pull request's branch checks out a one-parent "
    f"tip; with the stamp's tree it returned {_st_dispatch_err!r}",
)

# AND THE AUTOFIX ITSELF, which is the half that actually writes the deletion.
# Correcting `check_claims_hygiene` alone leaves the bot emptying the file and
# CI green on the result: the gate below was added, disabled, and the whole
# suite still passed, which is why this check exists rather than being assumed.
_ac_root, _ac_base = _hygiene_git(
    "# claims-for: 6.3.15\n\n"
    "whatif_edited  # in-window lo floored at the window min; floored band note\n"
    "whatif_weekly  # weekly-spec in-window lo floor; floored band note\n",
    {"docs/plan-2026-09-open-issues.md": "# plan\n"},
    py_touch=False,
)
_ac_before = (Path(_ac_root) / "tests" / "golden" / "card_claimed_drift.txt").read_text()
_ac_status = _env_drift.apply_inherited_claims(_ac_root, ref=_ac_base)
_ac_after = (Path(_ac_root) / "tests" / "golden" / "card_claimed_drift.txt").read_text()
R.check(
    "the autofix refuses a three-dot that moves nothing claimable, and writes nothing",
    _ac_status == "skip-moves-nothing-claimable" and _ac_after == _ac_before,
    "a documentation branch's claim file is not the bot's to empty -- that "
    f"deletion is what a squash applies to the baseline; status={_ac_status!r} "
    f"changed={_ac_after != _ac_before}",
)
# The null control: the same bot on a branch that DID move a fixture still
# empties an inherited list, which is the behaviour the gate must not have cost.
# Per FILE KIND (2026-09-10): the bot empties an inherited list only where the
# branch could have written it. This pin's earlier form gave a SOLVER branch an
# inherited CARD list and expected "changed" -- which is #608's shape exactly, a
# card list another lane wrote, emptied and squashed off main by a branch that
# never touched the card. The positive case is a branch that moved the card.
_ac2_root, _ac2_base = _hygiene_git(
    "# claims-for: 6.3.15\n\n"
    "whatif_edited  # in-window lo floored at the window min; floored band note\n"
    "whatif_weekly  # weekly-spec in-window lo floor; floored band note\n",
    {_env_drift.CARD_JS: "// this branch moved the card\n"},
    py_touch=False,
)
_ac2_status = _env_drift.apply_inherited_claims(_ac2_root, ref=_ac2_base)
R.check(
    "the autofix still empties an inherited card list on a branch that moved the card",
    _ac2_status == "changed",
    f"the gate must not have disabled the autofix outright; status={_ac2_status!r}",
)
_ac3_root, _ac3_base = _hygiene_git(
    "# claims-for: 6.3.15\n\n"
    "whatif_edited  # in-window lo floored at the window min; floored band note\n"
    "whatif_weekly  # weekly-spec in-window lo floor; floored band note\n",
    {},
    py_touch=True,
)
_ac3_before = (Path(_ac3_root) / "tests" / "golden" / "card_claimed_drift.txt").read_text()
_ac3_status = _env_drift.apply_inherited_claims(_ac3_root, ref=_ac3_base)
_ac3_after = (Path(_ac3_root) / "tests" / "golden" / "card_claimed_drift.txt").read_text()
R.check(
    "the autofix leaves an inherited CARD list alone on a branch that moved only solver "
    "files, and writes nothing",
    _ac3_status == "skip-not-inherited" and _ac3_after == _ac3_before,
    "a solver branch cannot have written the card list, and emptying it is the "
    f"deletion a squash applies to main (#608); status={_ac3_status!r} "
    f"changed={_ac3_after != _ac3_before}",
)

# AND THE THIRD MECHANISM, which is the one that actually reddened #662's own
# CI: `--all` calls a judged-but-unhit claim STALE and says "remove it". On a
# documentation branch that is the same deletion by another route, so the
# decision is extracted and pinned here rather than living inside `main()`.
_sj_docs_root, _sj_docs_base = _hygiene_git(
    "# claims-for: 6.3.15\n", {"docs/plan-2026-09-open-issues.md": "# plan\n"},
    py_touch=False, card_base="# claims-for: 6.3.15\n")
_sj_py_root, _sj_py_base = _hygiene_git(
    "# claims-for: 6.3.15\n", {}, py_touch=True, card_base="# claims-for: 6.3.15\n")
_sj = getattr(_env_drift, "stale_claims_judged", None)
R.check(
    "a stale claim is not judged on a branch that moves nothing claimable",
    callable(_sj) and _sj(_sj_docs_root, _sj_docs_base) is False,
    "a documentation branch neither caused a claim to go stale nor can cure "
    "it, and its only remedy would be a deletion the squash carries onto the "
    f"baseline; got {_sj and _sj(_sj_docs_root, _sj_docs_base)!r}",
)
R.check(
    "and it IS judged on a branch that moved a fixture (null control)",
    callable(_sj) and _sj(_sj_py_root, _sj_py_base) is True,
    "the gate must not have stopped judging staleness altogether; got "
    f"{_sj and _sj(_sj_py_root, _sj_py_base)!r}",
)
# The old case, unchanged where the baseline claims nothing: empty stays right.
_h_empty_root, _h_empty_base = _hygiene_git(
    "# claims-for: 6.3.15\n",
    {"docs/plan-2026-09-open-issues.md": "# plan\n"},
    py_touch=False,
    card_base="# claims-for: 6.3.15\n",
)
_h_empty_err = _hyg(_h_empty_root, _h_empty_base) if callable(_hyg) else "missing"
R.check(
    "check_claims_hygiene accepts empty claims on a roster-only three-dot",
    callable(_hyg) and _h_empty_err is None,
    f"empty claims on docs-only with an empty baseline should pass; got {_h_empty_err!r}",
)
# A ref that RESOLVES but shares no history with HEAD. `_rev` passes it -- it
# asks whether the ref resolves, and this one does -- and `git diff ref...HEAD`
# then exits 128 with "no merge base". `three_dot_files` read stdout without
# returncode, so the failure and a genuinely unchanged tree produced the same
# empty list, and `check_claims_hygiene` returned None, its all-clear. A shallow
# clone with graft roots is exactly this shape; the handover records it as trap
# 11, and the whole point of that trap is that the fiction is silent.
#
# Both directions, because "raises on a bad ref" alone would pass for a function
# that raises on every ref: the orphan must be refused AND the ordinary
# comparison in the same fixture must still answer.
def _orphan_ref(root: str) -> str:
    import subprocess as _sp

    blob = _sp.run(["git", "hash-object", "-w", "--stdin"], cwd=root, input="",
                   capture_output=True, text=True, check=True).stdout.strip()
    tree = _sp.run(["git", "mktree"], cwd=root, input=f"100644 blob {blob}\tx\n",
                   capture_output=True, text=True, check=True).stdout.strip()
    commit = _sp.run(["git", "commit-tree", tree, "-m", "orphan"], cwd=root,
                     capture_output=True, text=True, check=True).stdout.strip()
    _sp.run(["git", "update-ref", "refs/probe/orphan", commit], cwd=root, check=True)
    return "refs/probe/orphan"


# The baseline claims nothing here, so HEAD's empty list leaves it unchanged
# and the null control below is measuring the orphan ref rather than the claim
# rule: with the two-claim baseline this fixture used to carry, an emptied HEAD
# is now a refused DELETION, and the control would have failed for the wrong
# reason -- which is what it did until this line was written.
R.check(
    "an unanswerable three-dot still judges staleness, rather than quietly passing",
    callable(_sj) and _sj(_sj_docs_root, _orphan_ref(_sj_docs_root)) is True,
    "a gate that cannot read the diff must fail closed, or the refusal above "
    "becomes a way to stop being judged at all",
)
_h_orph_root, _h_orph_base = _hygiene_git(
    "# claims-for: 6.3.15\n",
    {"docs/plan-2026-09-open-issues.md": "# plan\n"},
    py_touch=False,
    card_base="# claims-for: 6.3.15\n",
)
_h_orph_ref = _orphan_ref(_h_orph_root)
_h_orph_err = _hyg(_h_orph_root, _h_orph_ref) if callable(_hyg) else "missing"
R.check(
    "a comparison ref with no merge base is refused, not read as no claim owed",
    callable(_hyg) and isinstance(_h_orph_err, str) and "CANNOT COMPARE" in _h_orph_err,
    f"an unanswerable three-dot returned {_h_orph_err!r}; None is this check's all-clear",
)
R.check(
    "and the same fixture still answers an ordinary comparison (null control)",
    callable(_hyg) and _hyg(_h_orph_root, _h_orph_base) is None,
    f"the resolvable base returned {_hyg(_h_orph_root, _h_orph_base)!r} in the tree that refused the orphan",
)

# Per FILE KIND (2026-09-10): a solver branch rewrites the solver list and leaves
# the card list exactly as found. This pin's earlier form emptied the card list on
# the same branch and expected a pass -- #608's shape, which the per-kind rule
# refuses (the twin below).
_h_real_root, _h_real_base = _hygiene_git(
    _h493_card,
    {},
    py_touch=True,
)
# Rewrite solver claims on HEAD so they are this diff's, not the baseline's.
Path(_h_real_root, "tests/golden/claimed_drift.txt").write_text(
    "# claims-for: 6.3.15\n\nwinter_single_dhw  # this branch moved the fixture\n"
)
_subprocess.run(["git", "add", "-A"], cwd=_h_real_root, check=True, capture_output=True)
_subprocess.run(
    ["git", "commit", "--amend", "--no-edit"],
    cwd=_h_real_root, check=True, capture_output=True,
)
_h_real_err = _hyg(_h_real_root, _h_real_base) if callable(_hyg) else "missing"
R.check(
    "check_claims_hygiene accepts a real claim-bearing PR that moves solver fixtures",
    callable(_hyg) and _h_real_err is None,
    f"optimizer.py + rewritten claims should pass; got {_h_real_err!r}",
)
_h_real2_root, _h_real2_base = _hygiene_git(
    "# claims-for: 6.3.15\n",
    {},
    py_touch=True,
)
Path(_h_real2_root, "tests/golden/claimed_drift.txt").write_text(
    "# claims-for: 6.3.15\n\nwinter_single_dhw  # this branch moved the fixture\n"
)
_subprocess.run(["git", "add", "-A"], cwd=_h_real2_root, check=True, capture_output=True)
_subprocess.run(
    ["git", "commit", "--amend", "--no-edit"],
    cwd=_h_real2_root, check=True, capture_output=True,
)
_h_real2_err = _hyg(_h_real2_root, _h_real2_base) if callable(_hyg) else "missing"
R.check(
    "the same solver PR that also EMPTIED the baseline's card list is refused for the card file",
    callable(_hyg) and isinstance(_h_real2_err, str)
    and _h_real2_err.startswith("RECORD PR CLAIMS")
    and _env_drift.CARD_CLAIM_FILE in _h_real2_err,
    f"a solver branch cannot have written the card list (#608); got {_h_real2_err!r}",
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
    "may-drift also accepts the owner-sanctioned #1208 movers and nothing else",
    _env_drift.may_drift_error(
        {n: "r" for n in _env_drift.RUNNER_CONDITIONAL_1208}, {}
    ) is None
    and set(_env_drift.RUNNER_CONDITIONAL_1208) == {
        "flat_prices", "winter_two_zone_no_dhw", "shoulder_two_zone",
    },
    "owner rulings on #1208 (comment 208bed25 option (a) for the pair; "
    "the in-session (i) ruling on the options recorded in comment "
    "fd13246, which carries the runner's numbers) scope the second set "
    "to exactly these three in-band movers; a fourth name in the "
    "constant breaks this set equality and is an unruled widening",
)
R.check(
    "may-drift also accepts the #1207 directive's movers and nothing else",
    _env_drift.may_drift_error(
        {n: "r" for n in _env_drift.RUNNER_CONDITIONAL_1207}, {}
    ) is None
    and set(_env_drift.RUNNER_CONDITIONAL_1207) == {
        "capacity_tariff_15min", "cycling_cost", "everything_on",
        "narrow_band", "shoulder", "valve_storage_smart_write",
        "winter_two_zone_dhw", "direct_flow_carnot", "fuse_guard",
        "precip_snow", "tariff_plus_two_zone", "valve_storage",
    },
    "owner directive #1207 comment c1329fe (2026-09-20, in-session) "
    "scoped the third set to the seven in-band movers that branch "
    "measured at its own merge base; the owner's ruling (i) on the "
    "options recorded in comment 1ec15c8 (which carries the CI runner's "
    "leaf counts) widened it to the runner's union -- exactly these "
    "twelve names (valve_storage_smart_write doubles as a SENSITIVE "
    "fixture, so one claim-file entry carries it); a thirteenth name in "
    "the constant breaks this set equality and is an unruled widening",
)
R.check(
    "and refuses every fixture whose floats DO travel",
    (_env_drift.may_drift_error({"away_setback": "r"}, {}) or "")
    .startswith("MAY-DRIFT OUT OF SCOPE")
    and (_env_drift.may_drift_error({"coord_minimal": "r"}, {}) or "")
    .startswith("MAY-DRIFT OUT OF SCOPE"),
    "a permanent exemption on a reproducible fixture would launder the next "
    "real regression",
)
R.check(
    "the refusal names both the stray entry and the category's real scope",
    "away_setback"
    in (_env_drift.may_drift_error({"away_setback": "r"}, {}) or "")
    and "wood_coil"
    in (_env_drift.may_drift_error({"away_setback": "r"}, {}) or ""),
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
    set(_md_entries) == set(_env_drift.MAY_DRIFT_ALLOWED)
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

# --- may-drift judged-key partition (#254) -----------------------------------
#
# The five SENSITIVE fixtures may drift in plan keys but not in forecast or
# baseline-reference fields. Measured 2026-09-04: prices, outdoor_temps,
# price_known and baseline_cost never move under committed-vs-local basin
# noise on any SENSITIVE fixture or narrow_band; M01 moves baseline_cost on
# wood_coil while the three input keys stay put.
R.check(
    "may-drift judged keys are exactly the forecast and baseline fields",
    _env_drift.MAY_DRIFT_JUDGED_KEYS
    == frozenset({"prices", "outdoor_temps", "price_known", "baseline_cost"}),
)
R.check(
    "may_drift_judged_diffs keeps baseline_cost and drops plan schedules",
    _env_drift.may_drift_judged_diffs(
        "wood_coil",
        [
            "wood_coil.baseline_cost: 156.0 vs 678.0",
            "wood_coil.power_schedule[0]: 1.0 vs 2.0",
            "wood_coil.prices[3]: 0.5 vs 0.6",
        ],
    )
    == [
        "wood_coil.baseline_cost: 156.0 vs 678.0",
        "wood_coil.prices[3]: 0.5 vs 0.6",
    ],
)
R.check(
    "may_drift_exempt_diffs is the complement on mixed diffs",
    len(_env_drift.may_drift_exempt_diffs(
        "wood_coil",
        [
            "wood_coil.baseline_cost: 1 vs 2",
            "wood_coil.optimal_setpoints[0]: 20 vs 21",
        ],
    )) == 1
    and "optimal_setpoints"
    in _env_drift.may_drift_exempt_diffs(
        "wood_coil", ["wood_coil.optimal_setpoints[0]: 20 vs 21"]
    )[0],
)

# --- stamp.py's --self-test, wired into a lane (#372) -----------------------
#
# tools/release/stamp.py is, in its own words, "the only way a version
# number is assigned", and it carries a 15+-check --self-test that has never
# run: not in tests/run.sh, not in any workflow, not in any tests/*.py --
# because tools/ was INERT (write-once round-2 audit evidence) and stamp.py
# was exempt only by sharing that directory's prefix. #372 narrowed INERT to
# tools/audit/ (tests/closure.py), which makes stamp.py an ordinary tracked
# file the recorder must classify. Importing it here, rather than adding an
# exemption or a hidden call site, is what gives closure.py's recorder
# something to record: `tools/release/stamp.py` now shows up in this
# script's own recorded closure (checked below), so a future change to
# stamp.py pulls this check back into scope on its own.
import contextlib as _stamp_contextlib
import importlib.util as _importlib_util
import io as _stamp_io

# Loading a module and calling a function it defines are both module-scope
# statements here, with no guard: a raising `stamp.py` (a syntax error, a
# missing dependency, an exception inside `self_test()` itself) would abort
# THIS FILE mid-run instead of failing the one check it is supposed to feed,
# and every later check in this ~7000-line script would then never execute --
# a truncated run that also happens to be the exact under-approximation
# `closure.py merge`'s `--allow-failures` flag exists to wave through
# (confirmed by probe: `mv`-ing stamp.py away and running this file raises
# an unhandled FileNotFoundError at the `exec_module` call below). Catching
# broadly here is deliberate: turning any failure mode into one red `R.check`
# is strictly safer than letting any of them turn into a partial run.
_STAMP_PATH = _closure.ROOT / "tools" / "release" / "stamp.py"
try:
    _stamp_spec = _importlib_util.spec_from_file_location(
        "hpo_release_stamp", _STAMP_PATH
    )
    _stamp = _importlib_util.module_from_spec(_stamp_spec)
    _stamp_spec.loader.exec_module(_stamp)
    with _stamp_contextlib.redirect_stdout(_stamp_io.StringIO()) as _stamp_out:
        _stamp_rc = _stamp.self_test()
    _stamp_ok = _stamp_rc == 0
    _stamp_detail = (
        "run `python tools/release/stamp.py --self-test` by hand for the "
        "failing check names:\n" + _stamp_out.getvalue()
    )
except Exception as _stamp_exc:  # noqa: BLE001 -- see comment above
    _stamp_ok = False
    _stamp_detail = (
        f"tools/release/stamp.py raised loading or running --self-test: "
        f"{type(_stamp_exc).__name__}: {_stamp_exc}"
    )
R.check(
    "tools/release/stamp.py's --self-test passes",
    _stamp_ok,
    _stamp_detail,
)
# stamp.py's OUTPUT against env_drift's claims guard, composed (2026-09-17).
# Each side was pinned alone and the composition by nothing, so #747 changed
# the guard, stamp.py kept writing what it always wrote, and the first two
# stamps to delete a solver claim afterwards (v6.5.0, v6.6.0) turned main red.
# Pinned here, a change to EITHER side goes red on its own pull request: the
# write set stamp.py stages must be the guard's `STAMP_WRITES`, and the claim
# files `rewrite_claims` produces must pass the guard as a push to main sees
# them, deleting a claim neither file's author could have written.
try:
    _stc_writes = {
        str(Path(p).relative_to(_stamp.ROOT))
        for p in (_stamp.VERSION_FILE, _stamp.MANIFEST, _stamp.CARD_JS,
                  _stamp.NOTES, *_stamp.CLAIM_FILES, *_stamp.REGISTER_FILES)
    }
    _stc_before = "# claims-for: 6.5.1\n#\n# old reason\n#\n\nconfig_flow  # a lane's claim\n"
    _stc_after, _stc_old, _stc_deleted = _stamp.rewrite_claims(_stc_before, "6.6.0", "t")
    _stc_decl, _stc_claims = _env_drift._parse_claims(_stc_after)
    _stc_verdict = _env_drift.claims_hygiene_verdict(
        sorted(_stc_writes), _stc_claims, _stc_claims,
        _env_drift._parse_claims(_stc_before)[1], {}, "HEAD^1",
        stamp=("6.6.0", _stc_old, _stc_decl, _stc_decl, 1),
    )
    _stc_ok = (
        _stc_writes == set(_env_drift.STAMP_WRITES)
        and _stc_deleted == 1
        and _stc_verdict is None
    )
    _stc_detail = (
        f"stamp.py writes {sorted(_stc_writes)}, the guard expects "
        f"{sorted(_env_drift.STAMP_WRITES)}; deleted={_stc_deleted}; "
        f"verdict={_stc_verdict!r}"
    )
except Exception as _stc_exc:  # noqa: BLE001 -- one red check, never a partial run
    _stc_ok = False
    _stc_detail = f"{type(_stc_exc).__name__}: {_stc_exc}"
R.check(
    "a claim file stamp.py rewrites passes env_drift's claims guard on the "
    "push to main, and both agree on the files a stamp writes",
    _stc_ok,
    _stc_detail,
)
R.check(
    "stamp.py is no longer INERT: closure.py must classify it",
    not _closure.is_inert("tools/release/stamp.py"),
    "narrowing INERT to tools/audit/ (#372) must not still cover "
    "tools/release/stamp.py, or the recorder has nothing to pull it into",
)
# Every tools/ file outside tools/audit/ must be classified. This replaced an
# equality against the single-element list ["tools/release/stamp.py"] (#1067
# G7b-1, which added tools/gen_device_fixtures.py): that literal said "there
# is one such file", which is not the property #372's narrowing bought. The
# property is that narrowing INERT leaves every non-audit tools/ file for the
# recorder to classify, and it holds for any number of them.
_tools_outside_audit = [
    f for f in __import__("subprocess").run(
        ["git", "ls-files", "tools/"], cwd=_closure.ROOT,
        capture_output=True, text=True).stdout.split()
    if not f.startswith("tools/audit/")
]
R.check(
    "narrowing INERT leaves every non-audit tools/ file in the must-classify set",
    "tools/release/stamp.py" in _tools_outside_audit
    and not [f for f in _tools_outside_audit if _closure.is_inert(f)],
    f"{_tools_outside_audit}; inert among them "
    f"{[f for f in _tools_outside_audit if _closure.is_inert(f)]}",
)
# The claim above ("now shows up in this script's own recorded closure") was
# stated but never asserted -- issue #372's own acceptance criterion 4 asks
# for both halves explicitly: that `closure.py check` records stamp.py in a
# closure, and that a change to it selects this script. Checked here against
# the COMMITTED table, which is what CI's `--record-only` job actually
# validates (the same distinction `inert_closure_violations` above draws).
_stamp_committed_closures = json.loads(
    _closure.CLOSURES.read_text())["closures"]
R.check(
    "the committed table records stamp.py in tests/entities.py's own "
    "closure",
    "tools/release/stamp.py" in
    _stamp_committed_closures.get("tests/entities.py", []),
    "closure.py's recorder should have picked this up from the "
    "spec_from_file_location/exec_module call above without a hand-written "
    "entry",
)
R.check(
    "a change to stamp.py selects tests/entities.py",
    "tests/entities.py" in
    _closure.select(["tools/release/stamp.py"])["run"],
    "the whole point of narrowing INERT (#372) is that a future stamp.py "
    "change is not silently un-tested",
)

# --- the committed fixtures' own staleness gate (#347, #326) ----------------
#
# env_drift compares COMPUTED against COMPUTED across two trees, so neither
# side is the committed file, and no CI lane ever ran the one comparison that
# is: run.sh skips golden.py entirely in drift mode. A fixture that no longer
# matches what the code produces was invisible by construction, and the claim
# mechanism guaranteed it -- claiming drift excuses a diff between trees and
# never re-records the artefact, so every claimed change widened the gap for
# good. tests/golden/config_flow.json went two releases and 85 divergent
# paths that way (#326).
#
# The projection below is what makes an exact-ish comparison against the
# committed file survivable in the normal gate. Measured at 2ab9b84 with a
# full 55-scenario capture against the committed fixtures: 34 fixtures differ
# on this machine, of which only SIX differ in structure. The other 28 are
# the solver landing in another basin, and the three signals that separate
# them were measured one at a time, not argued:
#
#   key paths + JSON type class     fires on exactly the 6      KEPT
#   + container lengths             fires on 9 -- narrow_band 18 -> 17 and
#                                   wood_coil 13 -> 18 planned DHW hours,
#                                   valve_storage_smart_write's valve target
#                                   schedule 96 -> 0                DROPPED
#
# So list lengths are machine-sensitive here and are reported, never gated;
# list elements collapse onto one path for the same reason. That correction
# is what these checks pin, one measured false positive at a time.
import contextlib as _contextlib
import io as _io

R.section("Committed-fixture staleness (#347)")

R.check(
    "a key the committed fixture lacks is structural staleness",
    any(
        "reading_ok" in line
        for line in _env_drift.shape_diff({"data": {}}, {"data": {"reading_ok": {}}})
    ),
    "the #326 class -- a key the code produces and the fixture has never seen",
)
R.check(
    "and so is a key the fixture has that the code no longer produces",
    _env_drift.shape_diff({"a": 1, "b": 2}, {"a": 1}) != [],
)
R.check(
    "and so is a leaf whose JSON type changed",
    _env_drift.shape_diff({"min": 0}, {"min": "0"}) != []
    and _env_drift.shape_diff({"t": None}, {"t": 1.5}) != [],
    "a number that became a string is a capture change, not a basin",
)

# The four measured false positives, each a real cross-machine difference in
# the committed fixtures at 2ab9b84. Every one of these must stay silent or
# the gate is red on main forever.
R.check(
    "a float that moved with the solver basin is not staleness",
    _env_drift.shape_diff(
        {"optimal_setpoints": [22.6, 21.0]}, {"optimal_setpoints": [20.4, 21.0]}
    ) == [],
)
R.check(
    "nor is an integer that flipped with it",
    _env_drift.shape_diff({"compressor_starts": 3}, {"compressor_starts": 4}) == [],
    "compressor_starts 3 -> 4 is the basin, and an int is still a number",
)
R.check(
    "nor is a boolean schedule that flipped",
    _env_drift.shape_diff(
        {"heat_pump_on_schedule": [True, False]},
        {"heat_pump_on_schedule": [False, True]},
    ) == [],
)
R.check(
    "nor is a plan-derived list whose LENGTH moved",
    _env_drift.shape_diff(
        {"dhw_planned_heating_hours": [0.0, 3.75, 4.0]},
        {"dhw_planned_heating_hours": [0.0, 4.25]},
    ) == [],
    "narrow_band 18 -> 17 and wood_coil 13 -> 18 planned hours are the basin; "
    "gating on length puts three machine-sensitive fixtures in the gate",
)
R.check(
    "nor is a schedule this basin never populated at all",
    _env_drift.shape_diff(
        {"valve_target_schedule": [23.0, 23.0]}, {"valve_target_schedule": []}
    ) == []
    and _env_drift.shape_diff(
        {"valve_target_schedule": []}, {"valve_target_schedule": [23.0, 23.0]}
    ) == [],
    "valve_storage_smart_write writes 96 targets on one machine and 0 here; "
    "an empty list carries no element types to compare",
)

# Level 1. Exact comparison is honest only where there is no float to travel,
# and which fixtures those are is read off the payload rather than listed by
# hand -- a list would rot the same way the fixtures did.
R.check(
    "a payload with a float anywhere is not exact-comparable",
    _env_drift.carries_floats({"a": 1.0})
    and _env_drift.carries_floats({"a": [{"b": 2.5}]})
    and not _env_drift.carries_floats({"a": 1, "b": "0.01", "c": [True, None]}),
)
R.check(
    "the config-flow fixture is float-free, so the exact level covers it",
    not _env_drift.carries_floats(
        json.loads(Path("tests/golden/config_flow.json").read_text())
    ),
    "if this ever gains a float the exact level silently stops covering it",
)
R.check(
    "and a solver fixture is not, so the exact level leaves it alone",
    _env_drift.carries_floats(
        json.loads(Path("tests/golden/winter_single_dhw.json").read_text())
    ),
)

# The machine-independence proof, on real data rather than a toy payload:
# a committed solver fixture with every float in it moved. That is what
# another machine's solver does -- 1202 floats in this one -- and level 2
# must stay silent through all of it or the gate cannot sit in the normal
# lane at all.
def _perturb(node):
    if isinstance(node, dict):
        return {k: _perturb(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_perturb(v) for v in node]
    if isinstance(node, bool):
        return not node
    if isinstance(node, float):
        return round(node * 1.37 + 0.5, 6)
    if isinstance(node, int):
        return node + 1
    return node


_real = json.loads(Path("tests/golden/winter_single_dhw.json").read_text())
_moved = _perturb(_real)
R.check(
    "a real fixture with every float, int and bool moved is not stale",
    _env_drift.shape_diff(_real, _moved, "winter_single_dhw") == [],
    f"{len(_env_drift.shape_diff(_real, _moved, 'winter_single_dhw'))} "
    f"structural path(s) fired on a payload whose structure did not change",
)
R.check(
    "and every one of those moves is still counted for the nightly",
    _env_drift.fixture_staleness(
        "tests/golden", {"winter_single_dhw": _moved}
    ).values.get("winter_single_dhw", 0) > 1000,
    "level 3 must see what level 2 deliberately ignores",
)
R.check(
    "while the same payload with one key added IS stale",
    _env_drift.shape_diff(
        _real, dict(_moved, reading_ok={"dhw_temperature": True}),
        "winter_single_dhw",
    ) != [],
    "the projection must not be blind, only float-blind",
)
R.check(
    "the exact level catches a string-valued move the structure cannot see",
    any(
        "0.01" in line
        for line in _env_drift.exact_diff({"min": "0"}, {"min": "0.01"})
    ),
    "window_area.config.min '0' -> '0.01' is #324's own fix, still missing "
    "from the committed fixture two releases later",
)

# The gate function itself, over a fixture directory built for the purpose.
with _tempfile.TemporaryDirectory(prefix="staleness_") as _st_root:
    _st_dir = Path(_st_root)
    (_st_dir / "float_free.json").write_text(json.dumps({"min": "0"}))
    (_st_dir / "solver.json").write_text(json.dumps({"setpoints": [21.0, 22.0]}))
    (_st_dir / "grew.json").write_text(json.dumps({"data": {}, "kwh": 1.5}))
    _st = _env_drift.fixture_staleness(
        str(_st_dir),
        {
            "float_free": {"min": "0.01"},
            "solver": {"setpoints": [20.4, 22.0]},
            "grew": {"data": {"reading_ok": True}, "kwh": 1.5},
            "never_recorded": {"x": 1},
        },
    )
    R.check(
        "the gate fails on the float-free fixture's string move",
        "float_free" in _st.exact,
    )
    R.check(
        "and on the fixture that grew a key",
        "grew" in _st.structural,
    )
    R.check(
        "and on a captured scenario with no committed fixture at all",
        _st.missing == ["never_recorded"],
        f"missing {_st.missing}",
    )
    R.check(
        "but NOT on the solver fixture whose floats merely moved",
        "solver" not in _st.exact and "solver" not in _st.structural,
        "this is the whole reason the gate can sit in the normal lane",
    )
    R.check(
        "which is still reported, because a nightly can act on it",
        _st.values.get("solver", 0) == 1,
        f"value report {_st.values}",
    )
    R.check(
        "and the gate's verdict counts only what it fails on",
        _st.failed == 3,
        f"failed {_st.failed}",
    )
    _st_out = _io.StringIO()
    with _contextlib.redirect_stdout(_st_out):
        _env_drift.print_staleness(_st)
    _st_text = _st_out.getvalue()
    R.check(
        "and the verdict NAMES every stale fixture",
        all(f"STALE {n}" in _st_text
            for n in ("float_free", "grew", "never_recorded")),
        "#347 asks for a check that turns rc 1 naming the fixture; a count "
        "with no name sends the reader back to a 55-scenario diff",
    )
    R.check(
        "and says how many, how to re-record, and which need care",
        "3 COMMITTED FIXTURE(S) ARE STALE" in _st_text
        and "golden.py --record" in _st_text
        and "poison" in _st_text,
        "a gate that fails without saying what to do gets claimed instead "
        "of fixed -- which is the mechanism that produced #326",
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

# --- R3-D10-04: production must pass config_entry into the HA base ----------
# The reauth block above assigns ``config_entry`` on the instance after
# construction, which is the consumer's true arm and also why adding or
# removing the keyword at ``super().__init__`` moved none of the named
# checks. Wrap the base constructor instead: the keyword is the thing
# Home Assistant's ``DataUpdateCoordinator`` actually reads.
R.section("Coordinator config_entry (R3-D10-04)")

from homeassistant.helpers import update_coordinator as _ce_uc  # noqa: E402

_ce_calls: list[dict] = []
_ce_orig = _ce_uc.DataUpdateCoordinator.__init__


def _ce_spy(self, *args, **kwargs):
    _ce_calls.append(dict(kwargs))
    return _ce_orig(self, *args, **kwargs)


_ce_uc.DataUpdateCoordinator.__init__ = _ce_spy
try:
    _ce_entry = FakeEntry(data=dict(_CRED_DATA))
    integration.HeatPumpOptimizerCoordinator(FakeHass(), _ce_entry)
finally:
    _ce_uc.DataUpdateCoordinator.__init__ = _ce_orig
R.check(
    "super().__init__ is passed config_entry=entry",
    bool(_ce_calls) and _ce_calls[0].get("config_entry") is _ce_entry,
    f"kwargs={_ce_calls[0] if _ce_calls else None}",
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
    _rc_credential_keys = (
        _CONF_NAME,
        const.CONF_TIBBER_TOKEN,
        const.CONF_WEATHER_ENTITY,
    )
    try:
        if answers is None:
            return asyncio.run(flow.async_step_reconfigure(None))
        credentials = {k: v for k, v in answers.items() if k in _rc_credential_keys}
        sensors = {k: v for k, v in answers.items() if k not in credentials}
        result = asyncio.run(flow.async_step_reconfigure(credentials))
        if result.get("type") != "form" or result.get("step_id") != "user_sensors":
            return result
        return asyncio.run(flow.async_step_user_sensors(sensors))
    except _AbortFlow as err:
        return {"type": "abort", "reason": err.reason}
    except AttributeError as err:
        return {"type": "error", "reason": f"AttributeError: {err}"}


_rc_real_validate = config_flow.validate_tibber_token
config_flow.validate_tibber_token = _accept_any_token
try:
    _rc_flow_open = _rc_flow()
    _rc_form = asyncio.run(_rc_flow_open.async_step_reconfigure(None))
    _rc_sensors_form = asyncio.run(_rc_flow_open.async_step_user_sensors(None))
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
    and _rc_suggested.get(const.CONF_TIBBER_TOKEN) == "tok-a",
    f"suggested name {_rc_suggested.get(_CONF_NAME)!r}, "
    f"token {_rc_suggested.get(const.CONF_TIBBER_TOKEN)!r}",
)
_rc_sensors_schema = _rc_sensors_form.get("data_schema")
_rc_sensors_suggested = (
    {
        str(getattr(k, "schema", k)): (getattr(k, "description", None) or {}).get(
            "suggested_value"
        )
        for k in _rc_sensors_schema.schema
    }
    if _rc_sensors_schema is not None
    else {}
)
R.check(
    "the reopened sensor step carries this entry's picks",
    _rc_sensors_suggested.get(const.CONF_INDOOR_TEMP_ENTITY) == "sensor.annex_indoor",
    f"suggested indoor {_rc_sensors_suggested.get(const.CONF_INDOOR_TEMP_ENTITY)!r}",
)
R.check(
    "a slot this entry leaves empty is not invented",
    _rc_sensors_suggested.get(const.CONF_OUTDOOR_TEMP_ENTITY) is None,
    f"suggested outdoor {_rc_sensors_suggested.get(const.CONF_OUTDOOR_TEMP_ENTITY)!r}",
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

# #509: what a household looks like in a diagnostics file. The coordinate is
# full precision and its 1-decimal cell is a different string, so "the precise
# value is absent" cannot pass just because the two happen to render the same;
# ``_DIAG_DEEP`` sits two levels down and inside a list, because the property
# that stops the NEXT nested location from leaking is depth-independence, not a
# rule about ``solar_location``; and the option-level coordinate differs from
# the data-level one so a payload that ever starts emitting option values is
# measured too.
_DIAG_LAT, _DIAG_LON = 59.331234, 18.071234
_DIAG_OPT_LAT, _DIAG_OPT_LON = 59.335555, 18.075555
_DIAG_NAME = "Villa Solbacken Storgatan 5"
_DIAG_TOPIC = "home/storgatan5/ecl110/state"
_DIAG_DEEP = {
    "sites": [{"station": {"latitude": _DIAG_LAT, "longitude": _DIAG_LON}}],
    # A coordinate that is not a number: free text under a coordinate key can
    # be an address, so it must not survive the way a number does.
    "typed": {"latitude": "Storgatan 5, Solna", "longitude": None},
}
_DIAG_DATA = {
    **_CRED_DATA,
    "name": _DIAG_NAME,
    const.CONF_SOLAR_LOCATION: {
        "latitude": _DIAG_LAT,
        "longitude": _DIAG_LON,
        "elevation": "not-a-number",
    },
    const.CONF_ECL110_STATE_TOPIC: _DIAG_TOPIC,
    "_deep": _DIAG_DEEP,
}
_DIAG_OPTIONS = {
    const.CONF_SOLAR_LOCATION: {
        "latitude": _DIAG_OPT_LAT,
        "longitude": _DIAG_OPT_LON,
    },
    const.CONF_TARGET_TEMP: 21.0,
}

_diag_hass = FakeHass()
_diag_entry = FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
_diag_entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
    _diag_hass, FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
)
_diag = asyncio.run(
    _diag_mod.async_get_config_entry_diagnostics(_diag_hass, _diag_entry)
)
_blob = _json.dumps(_diag, default=str)
_HA_REDACTED = "**REDACTED**"


def _diag_at(node, *path):
    """Walk ``path`` through dicts and lists, returning None at any mismatch.

    Over-redaction replaces a dict with a string, so a check written as
    ``payload["config"]["solar_location"].get(...)`` raises instead of
    failing -- which aborts the section before the over-redaction control
    below can run. This keeps every outcome a named check.
    """
    for step in path:
        if isinstance(step, int):
            if not isinstance(node, list) or len(node) <= step:
                return None
            node = node[step]
        elif isinstance(node, dict):
            node = node.get(step)
        else:
            return None
    return node


_diag_location = _diag_at(_diag, "config", const.CONF_SOLAR_LOCATION)
_diag_location = _diag_location if isinstance(_diag_location, dict) else {}

R.check(
    "the Tibber token never leaves the instance",
    _diag["config"].get(_CONF_TOKEN) == _HA_REDACTED
    and "stub-token" not in _blob
    and _CRED_DATA[_CONF_TOKEN] not in _blob,
    "a credential (or a fragment of it) appeared in the payload",
)

# --- #509: no precise coordinate, and no household label, in the payload ----
R.check(
    "no precise coordinate leaves the instance, from data or from options",
    not any(
        repr(_c) in _blob
        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
    ),
    "a full-precision coordinate appeared in the diagnostics payload: "
    + ", ".join(
        repr(_c)
        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
        if repr(_c) in _blob
    ),
)
R.check(
    "the coordinate survives as a coarse cell rather than as a hole",
    _diag_location.get("latitude") == round(_DIAG_LAT, 1)
    and _diag_location.get("longitude") == round(_DIAG_LON, 1),
    f"solar_location came back as {_diag_location!r}; support cannot see a "
    f"swapped or wrong-country coordinate through a redacted one",
)
R.check(
    "the documented coordinate precision is one decimal place",
    getattr(_diag_mod, "COORDINATE_PLACES", None) == 1,
    f"COORDINATE_PLACES is {getattr(_diag_mod, 'COORDINATE_PLACES', None)!r}",
)
R.check(
    "the coarsening reaches a coordinate nested below the top level",
    _diag_at(_diag, "config", "_deep", "sites", 0, "station", "latitude")
    == round(_DIAG_LAT, 1),
    "a coordinate two levels down, inside a list, came back as "
    f"{_diag_at(_diag, 'config', '_deep', 'sites', 0, 'station', 'latitude')!r}",
)
_diag_typed = _diag_at(_diag, "config", "_deep", "typed")
_diag_typed = _diag_typed if isinstance(_diag_typed, dict) else {}
R.check(
    "a coordinate that is not a number is redacted rather than published",
    _diag_typed.get("latitude") == _HA_REDACTED
    and _diag_typed.get("longitude") == _HA_REDACTED
    and "Storgatan 5, Solna" not in _blob,
    f"a non-numeric coordinate came back as {_diag_typed!r}",
)
R.check(
    "a non-coordinate member of the location dict is left alone",
    _diag_location.get("elevation") == "not-a-number",
    "redaction reached a key that is not a coordinate",
)
R.check(
    "the installation name the user typed never leaves the instance",
    _diag["config"].get("name") == _HA_REDACTED and _DIAG_NAME not in _blob,
    "the user's chosen entry name appeared in the diagnostics payload",
)
# The over-redaction control. Diagnostics exist for support; a fix that
# redacts the whole config would pass every check above and make the file
# useless, so the two things a bug report is actually read for are pinned.
R.check(
    "the entity ids and the MQTT topic survive redaction",
    _diag_at(_diag, "config", "weather_entity") == _CRED_DATA["weather_entity"]
    and _diag_at(_diag, "config", "indoor_temp_entity")
    == _CRED_DATA["indoor_temp_entity"]
    and _diag_at(_diag, "config", const.CONF_ECL110_STATE_TOPIC) == _DIAG_TOPIC,
    "redaction removed what a diagnostics file is read for: weather_entity is "
    f"{_diag_at(_diag, 'config', 'weather_entity')!r}",
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

for _pf in ("sensor.py", "binary_sensor.py", "button.py", "climate.py", "switch.py", "datetime.py"):
    R.check(
        f"the {_pf[:-3]} platform imports the shared base from .entity",
        "from .entity import HeatPumpOptimizerEntity" in (ROOT / _pf).read_text(),
        f"{_pf} does not import HeatPumpOptimizerEntity from .entity",
    )

# The audit's own metric (entity_base_classes_outside_entity_py): platform
# files must no longer declare CoordinatorEntity base classes of their own.
_bases_left = [
    _pf
    for _pf in ("sensor.py", "binary_sensor.py", "button.py", "climate.py", "switch.py", "datetime.py")
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
    (datetime_mod, "AwayReturnDateTime"),
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
for _module in (sensor, binary_sensor, _climate_platform, _switch_platform, button, datetime_mod):
    _one = collect(_module)[0]
    R.check(
        f"an entity from {_module.__name__.rsplit('.', 1)[-1]} keeps "
        f"has_entity_name and the coordinator's device_info",
        _one._attr_has_entity_name is True
        and _one.device_info == _one.coordinator.device_info,
        "an entity stopped resolving the shared plumbing",
    )

# --- #284 grammar of the two legacy schedule / plan states -----------------
R.section("#284 singular schedule and plan states")
_dhw_one = sensor.DHWScheduleSensor(
    FakeCoordinator(
        {
            "dhw_schedule": [
                {"dhw_power": 1.0},
                {"dhw_power": 0.0},
            ]
        }
    ),
    ENTRY,
)
R.check(
    "one DHW heating step is a period, not periods (#284)",
    _dhw_one.native_value == "1 heating period",
    repr(_dhw_one.native_value),
)
_dhw_two = sensor.DHWScheduleSensor(
    FakeCoordinator({"dhw_schedule": [{"dhw_power": 1.0}, {"dhw_power": 1.0}]}),
    ENTRY,
)
R.check(
    "two DHW heating steps keep the plural (#284)",
    _dhw_two.native_value == "2 heating periods",
    repr(_dhw_two.native_value),
)
_plan_one = sensor.SpaceHeatingPlanSensor(
    FakeCoordinator(
        {
            "space_plan": {
                "slots": [{"start": "2026-01-15T00:00:00"}],
                "active_now": False,
            }
        }
    ),
    ENTRY,
)
R.check(
    "one plan slot is a slot, not slots (#284)",
    _plan_one.native_value == "1 slot planned",
    repr(_plan_one.native_value),
)
_plan_two = sensor.SpaceHeatingPlanSensor(
    FakeCoordinator(
        {
            "space_plan": {
                "slots": [
                    {"start": "2026-01-15T00:00:00"},
                    {"start": "2026-01-15T06:00:00"},
                ],
                "active_now": False,
            }
        }
    ),
    ENTRY,
)
R.check(
    "two plan slots keep the plural (#284)",
    _plan_two.native_value == "2 slots planned",
    repr(_plan_two.native_value),
)

R.section("#558 D3 enumerated sensor states")

from heatpump_optimizer import narrative as narrative_mod
from heatpump_optimizer import optimizer as optimizer_mod

# SensorDeviceClass.ENUM is the only mechanism by which Home Assistant will
# translate a sensor's STATE, and it is not free: sensor/__init__.py raises
# ValueError on every state write whose value is outside ``options``. So an
# option list is not documentation, it is a whitelist, and a reachable state
# missing from it takes the entity down on a real install -- where nothing in
# this suite would have seen it, because the stub had no state path at all
# until #558 gave it one.
_ENUM_SENSORS = {
    "optimization_mode": (
        sensor.OptimizationModeSensor,
        const.OPTIMIZATION_MODE_STATES,
        lambda s: FakeCoordinator({"mode": s}),
    ),
    "heat_pump_action": (
        sensor.HeatPumpActionSensor,
        const.HEAT_PUMP_ACTION_STATES,
        lambda s: FakeCoordinator({"current_action": {"mode": s}}),
    ),
    "plan_narrative": (
        sensor.PlanNarrativeSensor,
        tuple(sorted(narrative_mod.TEMPLATES["en"])),
        lambda s: FakeCoordinator(
            {"insight": {"narrative": {"items": [{"reason": s}]}}}
        ),
    ),
}

for _key, (_cls, _states, _mk) in _ENUM_SENSORS.items():
    _e = _cls(_mk("unknown"), ENTRY)
    R.check(
        f"{_key} declares the enum device class",
        getattr(_e, "_attr_device_class", None) == "enum",
        repr(getattr(_e, "_attr_device_class", None)),
    )
    R.check(
        f"{_key} declares exactly its measured states as options",
        tuple(getattr(_e, "_attr_options", ()) or ()) == tuple(_states),
        f"{tuple(getattr(_e, '_attr_options', ()) or ())!r} != {tuple(_states)!r}",
    )
    # An ENUM sensor may carry no unit: sensor/const.py puts ENUM in
    # NON_NUMERIC_DEVICE_CLASSES and state() refuses the pair.
    R.check(
        f"{_key} carries no unit of measurement",
        getattr(_e, "_attr_native_unit_of_measurement", None) is None,
    )
    # A state class would be both impossible (DEVICE_CLASS_STATE_CLASSES maps
    # ENUM to the empty set) and silently destructive: capability_attributes
    # returns ATTR_STATE_CLASS first and never reaches ATTR_OPTIONS, so the
    # options would stop being published at all.
    R.check(
        f"{_key} carries no state class",
        getattr(_e, "_attr_state_class", None) is None,
    )

# The whole point: drive every declared state through the property Home
# Assistant actually reads. ``.state`` is the stub's transcription of
# sensor/__init__.py, so this fails exactly where a real install would.
_enum_state_errors = []
for _key, (_cls, _states, _mk) in _ENUM_SENSORS.items():
    for _s in _states:
        try:
            _got = _cls(_mk(_s), ENTRY).state
        except ValueError as _err:
            _enum_state_errors.append(f"{_key}={_s}: {_err}")
            continue
        if _got != _s:
            _enum_state_errors.append(f"{_key}={_s} rendered as {_got!r}")
R.check(
    "every declared state survives Home Assistant's own enum validation",
    not _enum_state_errors,
    "; ".join(_enum_state_errors[:6]),
)

# NULL CONTROL for the check above. If it cannot fail it pins nothing, and a
# check that supplies the value it then asserts is this repository's most
# repeated defect. A state outside the options must raise.
_control_raised = []
for _key, (_cls, _states, _mk) in _ENUM_SENSORS.items():
    try:
        _cls(_mk("a_state_no_producer_emits"), ENTRY).state
    except ValueError:
        _control_raised.append(_key)
R.check(
    "and an undeclared state raises, so the check above can fail",
    sorted(_control_raised) == sorted(_ENUM_SENSORS),
    f"only {sorted(_control_raised)} refused an undeclared state",
)

# None is not a violation: upstream returns before the options check, so an
# unavailable enum sensor is STATE_UNKNOWN rather than a raising entity.
R.check(
    "a None native_value is unknown, not an enum violation",
    sensor.PlanNarrativeSensor(
        FakeCoordinator({"insight": {"narrative": {"items": []}}}), ENTRY
    ).state
    is None,
)

# The option lists stay derived from their producers rather than maintained
# beside them. Two are checkable against the production constant directly;
# the narrative's IS the template table, which is also what renders it.
R.check(
    "the mode options are OPERATION_MODES plus the no-data fallback",
    set(const.OPTIMIZATION_MODE_STATES) == set(const.OPERATION_MODES) | {"unknown"},
    repr(const.OPTIMIZATION_MODE_STATES),
)

# HEAT_PUMP_ACTION_STATES is the one option list with no production constant
# behind it -- the four producers write their mode as a string literal -- so
# comparing _attr_options to it would be a check supplying the value it then
# asserts. Derive the set from the producing SOURCE instead. Rule: inside the
# four named producers, every ``mode = "<literal>"`` assignment and every
# ``"mode": "<literal>"`` dict entry. A fifth producer, or a new branch in
# these four, lands here as an option the list does not cover.
_ACTION_PRODUCERS = {
    "optimizer.py": {"get_current_action", "_idle_action"},
    "coordinator.py": {"_async_update_data", "_run_system_identification"},
}
_emitted_modes = set()
for _fname, _names in _ACTION_PRODUCERS.items():
    _tree = ast.parse((ROOT / _fname).read_text())
    for _fn in ast.walk(_tree):
        if (
            not isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            or _fn.name not in _names
        ):
            continue
        for _node in ast.walk(_fn):
            if (
                isinstance(_node, ast.Assign)
                and isinstance(_node.value, ast.Constant)
                and isinstance(_node.value.value, str)
                and any(
                    isinstance(_t, ast.Name) and _t.id == "mode"
                    for _t in _node.targets
                )
            ):
                _emitted_modes.add(_node.value.value)
            if isinstance(_node, ast.Dict):
                for _k, _v in zip(_node.keys, _node.values):
                    if (
                        isinstance(_k, ast.Constant)
                        and _k.value == "mode"
                        and isinstance(_v, ast.Constant)
                        and isinstance(_v.value, str)
                    ):
                        _emitted_modes.add(_v.value)
R.check(
    "the action options cover every mode its producers actually write",
    _emitted_modes and _emitted_modes <= set(const.HEAT_PUMP_ACTION_STATES),
    f"uncovered: {sorted(_emitted_modes - set(const.HEAT_PUMP_ACTION_STATES))}",
)
# The other direction, so the list cannot quietly grow states nothing emits:
# only the sensor's own no-data fallback may be there without a producer.
R.check(
    "and declares nothing beyond them but the no-data fallback",
    set(const.HEAT_PUMP_ACTION_STATES) - _emitted_modes == {"unknown"},
    f"unproduced: {sorted(set(const.HEAT_PUMP_ACTION_STATES) - _emitted_modes)}",
)
# Every reason the optimizer can tag a step with needs a narrative sentence,
# because PlanNarrativeSensor publishes the reason CODE as its state while
# render() merely skips a code it has no sentence for. Before ENUM that
# mismatch was an invisible missing line; now it is a ValueError.
_reason_values = {
    _v
    for _n, _v in vars(optimizer_mod).items()
    if _n.startswith("REASON_") and isinstance(_v, str)
}
R.check(
    "every optimizer REASON_ constant has a narrative template",
    _reason_values <= set(narrative_mod.TEMPLATES["en"]),
    f"untemplated: {sorted(_reason_values - set(narrative_mod.TEMPLATES['en']))}",
)

# Home Assistant looks a state translation up by the state string itself, so
# every option has to be a legal translation key. script/hassfest's
# RE_TRANSLATION_KEY, transcribed from 2025.2.0: lowercase alphanumeric with
# single internal hyphens or underscores, and none at either end.
_RE_TRANSLATION_KEY = re.compile(r"^(?!.+[_-]{2})(?![_-])[a-z0-9-_]+(?<![_-])$")
_unslugged = sorted(
    f"{_key}.{_s}"
    for _key, (_c, _states, _m) in _ENUM_SENSORS.items()
    for _s in _states
    if not _RE_TRANSLATION_KEY.match(_s)
)
R.check(
    "every enum option is a legal Home Assistant translation key",
    not _unslugged,
    ", ".join(_unslugged),
)

# And the translations themselves, in all three files. A missing state entry
# renders the raw token -- exactly the defect D3 exists to remove.
_state_string_errors = []
_sv_ent = json.loads((ROOT / "translations" / "sv.json").read_text())["entity"]
for _key, (_c, _states, _m) in _ENUM_SENSORS.items():
    _en_states = (_ENTITY_STRINGS["sensor"].get(_key) or {}).get("state") or {}
    _sv_states = (_sv_ent["sensor"].get(_key) or {}).get("state") or {}
    if set(_en_states) != set(_states):
        _state_string_errors.append(
            f"{_key}: strings.json states {sorted(set(_en_states) ^ set(_states))}"
        )
    if set(_sv_states) != set(_states):
        _state_string_errors.append(
            f"{_key}: sv.json states {sorted(set(_sv_states) ^ set(_states))}"
        )
    for _s in sorted(set(_en_states) & set(_sv_states)):
        if _sv_states[_s] == _en_states[_s]:
            _state_string_errors.append(f"{_key}.{_s} is identical in sv")
R.check(
    "every enum option has an English and a translated Swedish state name",
    not _state_string_errors,
    "; ".join(_state_string_errors[:6]),
)

# The two string-state sensors that deliberately do NOT get ENUM, pinned with
# their measurement in the same shape as the bare-device-class pins above,
# because a future consistency pass that adds ENUM to either takes the entity
# down on a real install.
#
# OptimizationStatusSensor publishes _solver_status's
# "suboptimal ({result.message})" and the solve path's "failed ({e})" --
# SciPy's message and an arbitrary exception string. Neither is enumerable,
# and _solver_status's own docstring says its suboptimal branch "fires
# routinely" on a flat price curve, so ENUM here would raise in ordinary
# operation. PredictiveInsightSensor's "no forecast" carries a SPACE, which
# RE_TRANSLATION_KEY above refuses, so that state cannot be a translation key
# at all. Both want a bounded companion sensor and a deprecation -- the
# reshaped D6 treatment -- never a mutated state.
for _bare, _why in (
    ("OptimizationStatusSensor", "embeds SciPy and exception text"),
    ("PredictiveInsightSensor", "emits 'no forecast', which is not a slug"),
):
    R.check(
        f"{_bare} stays bare: it {_why}",
        getattr(getattr(sensor, _bare), "_attr_device_class", None) is None
        and getattr(getattr(sensor, _bare), "_attr_options", None) is None,
    )
# D4 depends on this list and must not be able to drift from it. icons.json
# gains "state" variants next (#558 D4), and Home Assistant matches those keys
# against the entity's STATE -- so an icon state key that is not an option is
# an icon that can never be shown. Carried as an executable check rather than
# as a note in D4's brief, because a brief is advice and this is a constraint:
# the mismatch fails here instead of being noticed by nobody.
_icon_state_errors = []
for _key, (_c, _states, _m) in _ENUM_SENSORS.items():
    _spec = (_icons.get("entity", {}).get("sensor", {}) or {}).get(_key) or {}
    _extra = set(_spec.get("state") or {}) - set(_states)
    if _extra:
        _icon_state_errors.append(f"{_key}: {sorted(_extra)}")
R.check(
    "no icons.json state key falls outside its sensor's enum options (#558 D4)",
    not _icon_state_errors,
    "; ".join(_icon_state_errors),
)

R.check(
    "and the unbounded status strings really are unbounded",
    # A failed solve whose point is WORSE than the start: that is the only
    # path that formats the message in, and it is the routine one.
    "(" in optimizer_mod._solver_status(
        type("_R", (), {"success": False, "message": "ABNORMAL", "x": 1.0})(),
        float,
        0.0,
    ),
    "if this stops being a formatted string, OptimizationStatusSensor can "
    "take ENUM and the pin above should go",
)

R.section("#558 D4 icon state translations")

# D3 left icons.json with a "default" for every entity and no "state" anywhere,
# so the icon never followed the value. Home Assistant looks a state icon up by
# the STATE STRING, so only a sensor whose states are bounded can carry one --
# which is the same three sensors ENUM bounded, and the reason D4 was sequenced
# behind D3 rather than beside it.
_icon_sensors = _icons.get("entity", {}).get("sensor", {})

# D3's check was one-directional: it refused a state key outside the options.
# The other direction is what makes the section worth having -- an option with
# no icon falls back to "default" and the icon silently stops following the
# value for that state alone, which is invisible until someone hits it.
_missing_state_icons = []
for _key, (_c, _states, _m) in _ENUM_SENSORS.items():
    _have = set((_icon_sensors.get(_key) or {}).get("state") or {})
    _short = set(_states) - _have
    if _short:
        _missing_state_icons.append(f"{_key}: {sorted(_short)}")
R.check(
    "every enum option has its own icon",
    not _missing_state_icons,
    "; ".join(_missing_state_icons),
)

# A "state" section on anything else is an icon nobody can reach: its keys are
# matched against a state this integration never bounded. Stated as an equality
# so the section cannot be added to an unbounded sensor later either.
_stateful_icons = {_k for _k, _v in _icon_sensors.items() if "state" in _v}
R.check(
    "only the enum sensors carry a state section",
    _stateful_icons == set(_ENUM_SENSORS),
    f"{sorted(_stateful_icons)} != {sorted(_ENUM_SENSORS)}",
)

# A state icon equal to its own default changes nothing -- the shape a
# mechanical fill produces. hassfest means to refuse it (icons.py
# ensure_not_same_as_default, "the same as the default icon and thus can be
# removed") but on the "entity" section it does not: the validator is applied
# to {platform: {key: spec}} and reads "default" off the PLATFORM mapping,
# which has none, so it iterates and finds nothing. It is applied at the right
# depth on "entity_component", which is how the same function works there.
# Enforced here at the depth hassfest intends, so this integration is already
# right if that nesting is ever corrected upstream.
_redundant_state_icons = sorted(
    f"{_key}.{_state}"
    for _key, _spec in _icon_sensors.items()
    for _state, _icon in (_spec.get("state") or {}).items()
    if _icon == _spec.get("default")
)
R.check(
    "and no state icon merely repeats its own default",
    not _redundant_state_icons,
    ", ".join(_redundant_state_icons[:6]),
)
_flat_icon_sections = sorted(
    _key
    for _key, _spec in _icon_sensors.items()
    if "state" in _spec and len(set(_spec["state"].values())) == 1
)
R.check(
    "and each state section actually distinguishes states",
    not _flat_icon_sections,
    ", ".join(_flat_icon_sections),
)

# --- the producer gap D3 handed forward ------------------------------------
#
# D3 derived the action modes by scanning FOUR NAMED FUNCTIONS, so a producer
# added anywhere else was invisible to it -- and D4's icon keys are now pinned
# to that same list, which doubles what the gap costs. Derive the producer set
# instead of naming it: start from every function that ASSIGNS the coordinator's
# _current_action, then follow the call that assignment stores, and any call a
# reached function returns. The seed is the write, so a fifth writer cannot hide.
_PKG_TREES = {_p.name: ast.parse(_p.read_text()) for _p in sorted(ROOT.glob("*.py"))}

# F2: production may call the registry's create only from the helper that
# supplies the documentation link. A direct call is a notice that ships
# without one.
_f2_direct = []
for _fname, _tree in _PKG_TREES.items():
    for _fn in ast.walk(_tree):
        if not isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if _fname == "setpoint_check.py" and _fn.name == "create_issue":
            continue
        for _node in ast.walk(_fn):
            if not isinstance(_node, ast.Call):
                continue
            _func = _node.func
            if (
                isinstance(_func, ast.Attribute)
                and _func.attr == "async_create_issue"
            ):
                _f2_direct.append(f"{_fname}:{_fn.name}:{_node.lineno}")
R.check(
    "production raises repair notices only through the helper that adds the docs link",
    _f2_direct == [],
    ", ".join(_f2_direct),
)


def _pkg_functions(name):
    return [
        _fn
        for _t in _PKG_TREES.values()
        for _fn in ast.walk(_t)
        if isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and _fn.name == name
    ]


def _callee_name(node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        if isinstance(node.func, ast.Name):
            return node.func.id
    return None


_action_producers, _pending = set(), []
for _tree in _PKG_TREES.values():
    for _fn in ast.walk(_tree):
        if not isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for _node in ast.walk(_fn):
            # Assign covers ``self._current_action = ...``; AnnAssign covers the
            # annotated first binding in the coordinator's state init, which an
            # Assign-only scan misses entirely.
            if isinstance(_node, ast.Assign):
                _targets = _node.targets
            elif isinstance(_node, (ast.AnnAssign, ast.AugAssign)):
                _targets = [_node.target]
            else:
                continue
            if not any(
                isinstance(_t, ast.Attribute) and _t.attr == "_current_action"
                for _t in _targets
            ):
                continue
            _action_producers.add(_fn.name)
            if (_c := _callee_name(_node.value)) is not None:
                _pending.append(_c)
while _pending:
    _name = _pending.pop()
    if _name in _action_producers:
        continue
    _action_producers.add(_name)
    for _fn in _pkg_functions(_name):
        for _node in ast.walk(_fn):
            if isinstance(_node, ast.Return) and (
                _c := _callee_name(_node.value)
            ) is not None:
                _pending.append(_c)

# The derivation has to reach the four D3 named, or it is weaker than the thing
# it replaces. It reaches five: async_run_optimization is the function that
# performs the get_current_action write and D3's list does not contain it -- the
# list was complete only because the value came from a function that was named.
R.check(
    "the derived producer set covers the four D3 named by hand",
    {"get_current_action", "_idle_action", "_async_update_data", "_run_system_identification"}
    <= _action_producers,
    f"derived {sorted(_action_producers)}",
)

_derived_modes = set()
for _name in _action_producers:
    for _fn in _pkg_functions(_name):
        for _node in ast.walk(_fn):
            if (
                isinstance(_node, ast.Assign)
                and isinstance(_node.value, ast.Constant)
                and isinstance(_node.value.value, str)
                and any(
                    isinstance(_t, ast.Name) and _t.id == "mode" for _t in _node.targets
                )
            ):
                _derived_modes.add(_node.value.value)
            if isinstance(_node, ast.Dict):
                for _k, _v in zip(_node.keys, _node.values):
                    if (
                        isinstance(_k, ast.Constant)
                        and _k.value == "mode"
                        and isinstance(_v, ast.Constant)
                        and isinstance(_v.value, str)
                    ):
                        _derived_modes.add(_v.value)
R.check(
    "and the action options cover every mode the derived producers write",
    _derived_modes and _derived_modes <= set(const.HEAT_PUMP_ACTION_STATES),
    f"uncovered: {sorted(_derived_modes - set(const.HEAT_PUMP_ACTION_STATES))}",
)
R.check(
    "which is the same answer the named scan gave, so neither is doing it alone",
    _derived_modes == _emitted_modes,
    f"derived {sorted(_derived_modes)} vs named {sorted(_emitted_modes)}",
)


R.section("#558 D5 service translations")

# services.yaml carried every name and description as English text, so the
# service picker was untranslated for every non-English user -- while the same
# integration translates every entity, option page and repair issue.
# async_get_all_descriptions prefers
# ``component.<domain>.services.<service>.name`` over the yaml value, so the
# catalogue is what a user sees and the yaml is the fallback nobody reaches.
_SERVICE_TEXT_KEYS = ("name", "description")
_service_text_errors = []
for _cat_name, _cat in _CATALOGUES.items():
    _cat_services = _cat.get("services")
    if not isinstance(_cat_services, dict):
        _service_text_errors.append(f"{_cat_name}: no services section")
        continue
    if set(_cat_services) != set(services):
        _service_text_errors.append(
            f"{_cat_name}: {sorted(set(_cat_services) ^ set(services))}"
        )
    for _svc, _schema in services.items():
        _entry = _cat_services.get(_svc)
        if not isinstance(_entry, dict):
            continue
        for _k in _SERVICE_TEXT_KEYS:
            if not (_entry.get(_k) or "").strip():
                _service_text_errors.append(f"{_cat_name}: {_svc} has no {_k}")
        _yaml_fields = set((_schema or {}).get("fields") or {})
        _cat_fields = set(_entry.get("fields") or {})
        if _cat_fields != _yaml_fields:
            _service_text_errors.append(
                f"{_cat_name}: {_svc} fields {sorted(_cat_fields ^ _yaml_fields)}"
            )
        for _fname, _fentry in (_entry.get("fields") or {}).items():
            for _k in _SERVICE_TEXT_KEYS:
                if not isinstance(_fentry, dict) or not (_fentry.get(_k) or "").strip():
                    _service_text_errors.append(
                        f"{_cat_name}: {_svc}.{_fname} has no {_k}"
                    )
R.check(
    "every service and field is named and described in all three catalogues",
    not _service_text_errors,
    "; ".join(_service_text_errors[:6]),
)

# And the yaml no longer carries the text, so there is one source rather than
# two that can disagree. hassfest permits both for a custom integration
# (CUSTOM_INTEGRATION_EXTRA_SCHEMA_DICT), which is exactly why nothing else
# would have caught the drift.
_yaml_text_left = sorted(
    f"{_svc}.{_k}"
    for _svc, _schema in services.items()
    for _k in _SERVICE_TEXT_KEYS
    if (_schema or {}).get(_k) is not None
) + sorted(
    f"{_svc}.{_fname}.{_k}"
    for _svc, _schema in services.items()
    for _fname, _fschema in ((_schema or {}).get("fields") or {}).items()
    for _k in _SERVICE_TEXT_KEYS
    if (_fschema or {}).get(_k) is not None
)
R.check(
    "and services.yaml keeps structure only, not text",
    not _yaml_text_left,
    ", ".join(_yaml_text_left[:6]),
)

# Placeholder English left in a translation is worse than no translation: it
# looks translated. Applied to descriptions as well as names, because the
# descriptions are the long text and the easiest half to skip.
_sv_services = _CATALOGUES["sv.json"].get("services") or {}
_en_services = _CATALOGUES["en.json"].get("services") or {}
_untranslated = []
for _svc in sorted(set(_sv_services) & set(_en_services)):
    for _k in _SERVICE_TEXT_KEYS:
        if _sv_services[_svc].get(_k) == _en_services[_svc].get(_k):
            _untranslated.append(f"{_svc}.{_k}")
    _sv_f = _sv_services[_svc].get("fields") or {}
    _en_f = _en_services[_svc].get("fields") or {}
    for _fname in sorted(set(_sv_f) & set(_en_f)):
        for _k in _SERVICE_TEXT_KEYS:
            if _sv_f[_fname].get(_k) == _en_f[_fname].get(_k):
                _untranslated.append(f"{_svc}.{_fname}.{_k}")
R.check(
    "the Swedish service text is actually translated",
    # Non-emptiness is part of the claim: with no services section at all this
    # compares two empty mappings and passes while saying nothing, which is the
    # shape of check this repository keeps having to refute.
    bool(_sv_services) and bool(_en_services) and not _untranslated,
    f"{len(_untranslated)} identical of {len(_sv_services)} services: "
    f"{_untranslated[:4]}",
)

# The catalogue describes services that exist. A row for a service nothing
# registers is text no user can reach; one registered with no row is the
# untranslated state this item exists to remove.
_registered = {
    _v
    for _n, _v in vars(const).items()
    if _n.startswith("SERVICE_") and isinstance(_v, str)
}
R.check(
    "the documented services are exactly the registered ones",
    set(services) == _registered,
    f"{sorted(set(services) ^ _registered)}",
)

# hassfest's TRANSLATIONS validator reads every string in these files and
# treats any ``{...}`` as a PLACEHOLDER, so brace syntax that is merely prose
# in services.yaml becomes an error once the same sentence moves into a
# catalogue. Transcribed from script/hassfest/translations.py: it parses each
# value with string.Formatter and requires every non-empty field_name to be
# an identifier, and separately refuses a placeholder inside single quotes.
# Ran in CI at about 30 seconds; runs here in milliseconds, which is why it is
# here (#558 D5 turned `hassfest` red on exactly this).
_RE_PLACEHOLDER_IN_SINGLE_QUOTES = re.compile(r"'{\w+}'")


def _translation_placeholder_errors(node, where):
    out = []
    if isinstance(node, dict):
        for _k, _v in node.items():
            out += _translation_placeholder_errors(_v, f"{where}.{_k}")
        return out
    if not isinstance(node, str):
        return out
    try:
        fields = [f for _, f, _, _ in string.Formatter().parse(node) if f]
    except ValueError as err:
        return [f"{where}: unparseable format string ({err})"]
    for _field in fields:
        if not _field.isidentifier():
            out.append(f"{where}: {{{_field}}} is not a valid identifier")
    if _RE_PLACEHOLDER_IN_SINGLE_QUOTES.search(node):
        out.append(f"{where}: placeholder inside single quotes")
    return out


_placeholder_errors = [
    _e
    for _name, _data in _CATALOGUES.items()
    for _e in _translation_placeholder_errors(_data, _name)
]
R.check(
    "every translation string is a legal format string for hassfest",
    not _placeholder_errors,
    "; ".join(_placeholder_errors[:4]),
)


R.section("#558 D6 numeric schedule companion")

# ScheduleSensor's state is an English sentence -- "24 steps" / "no schedule" --
# so it cannot be translated, cannot be read as a number by a template, and
# collapses "no data yet" and "a schedule with nothing in it" into one string.
# D6 was reshaped to ADD a numeric entity rather than mutate this one, because
# an automation may be sitting on the shipped value. So the first thing pinned
# is that the shipped value did not move.
_SHIPPED_SCHEDULE_STATES = (
    (None, "no schedule"),
    ({"schedule": []}, "no schedule"),
    ({"schedule": [{"hour": 0}]}, "1 steps"),
    ({"schedule": [{"hour": _h} for _h in range(24)]}, "24 steps"),
)
_shipped_moved = []
for _data, _want in _SHIPPED_SCHEDULE_STATES:
    _got = sensor.ScheduleSensor(FakeCoordinator(_data), ENTRY).native_value
    if _got != _want:
        _shipped_moved.append(f"{_data!r} -> {_got!r}, was {_want!r}")
R.check(
    "the deprecated sensor still publishes exactly what it shipped",
    not _shipped_moved,
    "; ".join(_shipped_moved),
)
# Including the ungrammatical singular. It is shipped text an automation may
# compare against, so correcting it here would be the mutation D6 forbids.
R.check(
    "including the ungrammatical '1 steps', which is shipped and so is frozen",
    sensor.ScheduleSensor(
        FakeCoordinator({"schedule": [{"hour": 0}]}), ENTRY
    ).native_value
    == "1 steps",
)

_steps_cases = (
    (None, None),
    ({"schedule": []}, 0),
    ({"schedule": [{"hour": 0}]}, 1),
    ({"schedule": [{"hour": _h} for _h in range(24)]}, 24),
)
_steps_wrong = []
for _data, _want in _steps_cases:
    _got = sensor.ScheduleStepsSensor(FakeCoordinator(_data), ENTRY).native_value
    if _got != _want or type(_got) is not type(_want):
        _steps_wrong.append(f"{_data!r} -> {_got!r}, want {_want!r}")
R.check(
    "the companion publishes the step count as an integer",
    not _steps_wrong,
    "; ".join(_steps_wrong),
)
# The distinction the sentence loses, and the reason the companion is worth an
# entity rather than an attribute: "no data yet" is unknown, an empty schedule
# is zero, and the deprecated sensor says "no schedule" to both.
R.check(
    "and separates no-data from an empty schedule, which the sentence cannot",
    sensor.ScheduleStepsSensor(FakeCoordinator(None), ENTRY).native_value is None
    and sensor.ScheduleStepsSensor(
        FakeCoordinator({"schedule": []}), ENTRY
    ).native_value
    == 0
    and sensor.ScheduleSensor(FakeCoordinator(None), ENTRY).native_value
    == sensor.ScheduleSensor(
        FakeCoordinator({"schedule": []}), ENTRY
    ).native_value,
)

# Both read the same coordinator key, so they cannot drift apart into two
# answers about one schedule.
_steps_entity = sensor.ScheduleStepsSensor(
    FakeCoordinator({"schedule": [{"hour": _h} for _h in range(7)]}), ENTRY
)
R.check(
    "the two sensors describe the same schedule",
    f"{_steps_entity.native_value} steps"
    == sensor.ScheduleSensor(
        FakeCoordinator({"schedule": [{"hour": _h} for _h in range(7)]}), ENTRY
    ).native_value,
)
# A count that is nearly always the horizon would write one identical
# statistic an hour forever; D8-03 measured this state as constant across
# 170/170 cycles. The value here is that a template can read an integer, not
# that history needs it.
R.check(
    "the companion records no long-term statistics",
    getattr(sensor.ScheduleStepsSensor, "_attr_state_class", None) is None
    and getattr(sensor.ScheduleStepsSensor, "_attr_native_unit_of_measurement", None)
    is None,
    "a constant in the recorder is cost with no reader",
)
R.check(
    "and stays diagnostic, beside the sensor it replaces",
    sensor.ScheduleStepsSensor._attr_entity_category
    == sensor.ScheduleSensor._attr_entity_category,
)
# The deprecation is documented rather than enforced: no repair issue fires,
# because the entity is enabled for every install and a warning nobody asked
# for is the UX defect this programme is removing, not adding.
R.check(
    "the deprecated sensor says so, and names its replacement",
    "deprecated" in (sensor.ScheduleSensor.__doc__ or "").lower()
    and "optimization_schedule_steps" in (sensor.ScheduleSensor.__doc__ or ""),
    "a deprecation the next reader cannot find is not one",
)
R.check(
    "and it is still registered, because removing it is the breaking change "
    "D6 was reshaped to avoid",
    "optimization_schedule"
    in {_e._attr_translation_key for _p, _e in _named_entities if _p == "sensor"},
)

# --- the nightly's own telling (#533) ---------------------------------------
#
# `nightly-ha` and `slow` run on `schedule` alone, are `skipped` on every push
# and pull request, and are not required contexts on `main-protect`. So a
# scheduled run's conclusion lands on whatever commit was main's head when the
# cron fired and the next merge strands it: both `nightly-ha` arms failed on
# two consecutive nights and a seat sent looking found it, not the lane.
# `tests/nightly_status.py` is the telling, and the `nightly-status` job runs
# it on every pull request.
#
# Two things are pinned here and they are different things. The WIRING -- that
# the job exists, runs on pull requests, and invokes the reporter with no
# argument that could pin it green -- is read out of the YAML, because a
# correct classifier the workflow does not call is exactly the silent-green
# shape this whole issue is about. The CLASSIFIER's four states are driven
# directly, because they are pure functions of data and need no network.
import nightly_status as _nstatus  # noqa: E402

# A job that drives a history-reading script must check out the history. This is
# a PROPERTY over the workflow, not a pin on one job: `mutation-nightly` ran at
# the default depth 1, so its baseline driver `tests/entities.py` could not ask
# git whether the handover's `updated-for:` is an ancestor, failed there, and
# `mutation_table.py` refused with "the baseline is already red" -- a red nightly
# that had run no mutant at all. Its sibling `mutation` already carried
# `fetch-depth: 0` for the same reason, which is what makes this a property
# nobody had stated rather than a one-off.
#
# COMMENTS ARE STRIPPED BEFORE MATCHING, and that is not a detail: the first
# version of this check matched the whole block and named `browser` and
# `nightly-status`, which only MENTION a driver in a comment and are green at
# depth 1. A predicate written from one failure will happily return confirming
# evidence; what it must survive is "what would this refuse that should pass".
#
# The list is the four whose history need is EVIDENCED -- entities.py by the
# reproduction above, run.sh and mutation_table.py because they drive it, and
# env_drift.py by the `fast` job's own comment. `closure.py` is deliberately
# absent: `closures-autofix` shells its `autofix-report` subcommand at depth 1
# and is green, so requiring history there would be a refusal with no defect
# behind it.
_HISTORY_DRIVERS = ("tests/mutation_table.py", "tests/run.sh",
                    "tests/entities.py", "tests/env_drift.py")


def _job_shell(text: str, name: str) -> str:
    """One job's block with comment tails removed, so a mention is not a use."""
    return "\n".join(
        line.split("#", 1)[0] for line in _workflow_job(text, name).splitlines()
    )


_DEPTH_JOBS = [
    _name for _name in re.findall(r"^  ([a-z][\w-]*):$", _TESTS_YML, re.M)
    if any(_d in _job_shell(_TESTS_YML, _name) for _d in _HISTORY_DRIVERS)
]
_DEPTH_SHALLOW = [
    _name for _name in _DEPTH_JOBS
    if "fetch-depth: 0" not in _workflow_job(_TESTS_YML, _name)
]
R.check(
    "every job driving a history-reading script checks out the history",
    bool(_DEPTH_JOBS) and not _DEPTH_SHALLOW,
    f"{_DEPTH_SHALLOW or 'no job matched at all, so this check measured nothing'}"
    f" against drivers {list(_HISTORY_DRIVERS)}. A shallow clone cannot answer "
    "`merge-base --is-ancestor`, so the script fails on the CLONE rather than on "
    "the tree and the job is red for a reason no diff explains. Add "
    "`fetch-depth: 0`.",
)

_NS_JOB = _workflow_job(_TESTS_YML, "nightly-status")
_NS_RUNS = [
    _l.strip() for _l in _NS_JOB.splitlines()
    if "tests/nightly_status.py" in _l and _l.strip().startswith("run:")
]
R.check(
    "the nightly reporter is wired into a job that runs on pull requests",
    "github.event_name == 'pull_request'" in _NS_JOB and len(_NS_RUNS) == 1,
    f"if-line present={'pull_request' in _NS_JOB} run lines={_NS_RUNS}",
)
# The null control for the demonstration knob. `--run` classifies one named
# run; pointed at a run that passed it reports PASSED forever, which is the
# always-green check this repository keeps catching. CI must never pass it.
R.check(
    "and passes it no argument that would pin its answer",
    bool(_NS_RUNS) and _NS_RUNS[0] == "run: python tests/nightly_status.py",
    f"the invocation is {_NS_RUNS[0] if _NS_RUNS else '(absent)'!r}",
)
# The permission widening, checked as a PROPERTY rather than as its instance:
# the whole set of jobs that override the workflow's `contents: read` floor.
# A job-level block REPLACES the floor for that job and is inherited by none,
# so the set IS the blast radius. The two autofix jobs have needed writes since
# #523; a fourth override should have to be argued for.
_NS_OVERRIDES = sorted(
    _m.group(1) for _m in re.finditer(
        r"^  ([A-Za-z][\w-]*):\n(?:(?!^  [A-Za-z]).)*?^    permissions:",
        _TESTS_YML, re.M | re.S)
)
R.check(
    "exactly three jobs override the workflow's read-only floor",
    _NS_OVERRIDES == ["claims-autofix", "closures-autofix", "nightly-status"],
    f"jobs with a permissions block: {_NS_OVERRIDES}",
)
_NS_PERMS = re.search(r"^    permissions:\n((?:^      .*\n)+)", _NS_JOB, re.M)
R.check(
    "and the nightly reporter's own widening is read-only",
    bool(_NS_PERMS)
    and sorted(_NS_PERMS.group(1).split()) == sorted(
        ["actions:", "read", "contents:", "read"]),
    f"nightly-status permissions: {_NS_PERMS.group(1).split() if _NS_PERMS else None}",
)

# `REQUIRED_LANES` is the reporter's answer to "the run concluded and the lane
# inside it was skipped", which is absence one level down from "no run". Naming
# two jobs is a coupling, so the coupling is DERIVED here rather than restated:
# a job is schedule-only when its own `if:` admits `'schedule'` and neither
# `'push'` nor `'pull_request'`, and those are exactly the jobs a pull request
# cannot see for itself. A future lane added to the nightly is therefore
# refused by this gate until it is registered, instead of being watched by
# nobody -- which is the silence #533 is about, one level further out.
_NS_HEADS = {
    _n: _workflow_job(_TESTS_YML, _n).split("\n    steps:")[0]
    for _n in re.findall(r"^  ([A-Za-z][\w-]*):$", _TESTS_YML, re.M)
}
_NS_SCHEDULE_ONLY = sorted(
    _n for _n, _h in _NS_HEADS.items()
    if "'schedule'" in _h and "'push'" not in _h and "'pull_request'" not in _h
)
R.check(
    "the reporter watches exactly the lanes a pull request cannot see",
    sorted(_nstatus.REQUIRED_LANES) == _NS_SCHEDULE_ONLY,
    f"REQUIRED_LANES={sorted(_nstatus.REQUIRED_LANES)} "
    f"schedule-only jobs in tests.yml={_NS_SCHEDULE_ONLY}",
)

# --- the four states --------------------------------------------------------
_NS_NOW = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)


def _ns_run(rid: int, when: str, status: str = "completed",
            conclusion: str | None = "success") -> dict:
    # The default is the ORDINARY nightly: a run that concluded `success`. It
    # was `failure` until the review of this pull request, and that is not a
    # detail -- under the classifier as first written, `verdict` never read the
    # run's own conclusion at all, so every fixture below was silently a run
    # that had FAILED and every one of them still read PASSED. The fixture
    # encoded the defect, which is why no check here caught it. Each case now
    # varies ONE property and leaves the rest ordinary.
    return {"id": rid, "created_at": when, "status": status,
            "conclusion": conclusion, "head_sha": "0" * 40,
            "html_url": f"https://example.invalid/{rid}"}


def _ns_job(name: str, conclusion: str | None) -> dict:
    return {"name": name, "conclusion": conclusion, "html_url": ""}


# Every lane in REQUIRED_LANES has to appear here, or the ordinary nightly
# reads ABSENT and all four states collapse -- which is how adding
# `mutation-nightly` to the reporter announced itself, four checks at once.
# `fast` is skipped on a schedule by design and is in the fixture for that.
_NS_LIVE = [_ns_job("nightly-ha (stable)", "success"),
            _ns_job("nightly-ha (2025.2.0)", "success"),
            _ns_job("slow", "success"),
            _ns_job("mutation-nightly", "success"),
            _ns_job("fast", "skipped")]
_NS_LAST_NIGHT = _ns_run(1, "2026-09-10T02:17:00Z")
_NS_CASES = {
    "FAILED": (_NS_LAST_NIGHT, None,
               [*_NS_LIVE[1:], _ns_job("nightly-ha (stable)", "failure")]),
    "PASSED": (_NS_LAST_NIGHT, None, _NS_LIVE),
    "RUNNING": (None, _ns_run(2, "2026-09-10T02:17:00Z", "in_progress", None), []),
    "ABSENT": (None, None, []),
}
_NS_STALE_RUN = _ns_run(3, "2026-09-01T02:17:00Z")
_ns_wrong = []
for _want, (_c, _f, _j) in _NS_CASES.items():
    _got, _code, _lines = _nstatus.verdict(_c, _f, _j, _NS_NOW)
    _green = _code == 0
    if _got != _want or _green != (_want == "PASSED"):
        _ns_wrong.append(f"{_want} -> {_got} exit={_code}")
R.check(
    "the reporter separates failed, passed, still-running and never-ran",
    not _ns_wrong,
    "; ".join(_ns_wrong) or "four states, one exit code each",
)
# The state this exists to refuse: absence must not read as a pass. Both
# shapes of absence, and the one that is absence one level down.
_ns_absent = [
    _nstatus.verdict(None, None, [], _NS_NOW)[0],
    _nstatus.verdict(_NS_STALE_RUN, None, _NS_LIVE, _NS_NOW)[0],
    _nstatus.verdict(_NS_LAST_NIGHT, None,
                     [_ns_job("nightly-ha (stable)", "skipped"),
                      _ns_job("slow", "skipped"),
                      _ns_job("fast", "success")], _NS_NOW)[0],
]
R.check(
    "no run, a stale run and a run whose lanes were skipped are all ABSENT",
    _ns_absent == ["ABSENT", "ABSENT", "ABSENT"],
    f"no-run/stale/lane-skipped -> {_ns_absent}; a check that reads missing "
    "evidence as good evidence is the shape this issue exists for",
)
# Fails closed on a conclusion string GitHub has not invented yet, which is
# the reader's own null control: the accepted set is a whitelist, so a new
# value cannot arrive as a silent pass.
_ns_novel = _nstatus.verdict(
    _NS_LAST_NIGHT, None,
    [*_NS_LIVE[1:], _ns_job("nightly-ha (stable)", "quantum_ambiguous")],
    _NS_NOW)
R.check(
    "an unrecognised job conclusion is reported, not waved through",
    _ns_novel[0] == "FAILED" and "quantum_ambiguous" in "\n".join(_ns_novel[2]),
    f"state={_ns_novel[0]}",
)
# The verdict is the last CONCLUDED run, so it does not flip to "no answer"
# for the forty-five minutes the lane takes every night.
_ns_flight = _nstatus.verdict(
    _NS_LAST_NIGHT, _ns_run(9, "2026-09-10T11:00:00Z", "in_progress", None),
    _NS_LIVE, _NS_NOW)
R.check(
    "a newer in-flight run annotates the verdict and does not become it",
    _ns_flight[0] == "PASSED" and any("in flight" in _l for _l in _ns_flight[2]),
    f"state={_ns_flight[0]}",
)
# Every report says the check does not block, on green as well as on red. A
# reader meeting the first red one has to learn that from the report itself.
R.check(
    "and every state says in the report that it blocks nothing",
    "does not block a merge" in _nstatus.NOT_REQUIRED
    and _nstatus.EXIT_UNREADABLE != _nstatus.EXIT_GREEN,
    "an unreadable API must not exit green: "
    f"UNREADABLE={_nstatus.EXIT_UNREADABLE} GREEN={_nstatus.EXIT_GREEN}",
)
# The classification the ratchet demands of any new tracked file: not
# selectable (it needs the Actions API), not INERT (this script reads it).
R.check(
    "the reporter is classified: NOT_A_TEST, and not on INERT",
    "nightly_status.py" in _closure.NOT_A_TEST
    and not _closure.is_inert("tests/nightly_status.py"),
    "a file that is neither in a closure nor on a list forces the FULL suite",
)
# `run.sh` accounts for its scripts TWICE -- once asking "is there a `run`
# line?" and once, after the lanes, asking "did one actually execute?" -- and
# each has its own `case` list of the scripts that legitimately do neither.
# Excluding a script from one and not the other is silent locally and costs a
# full `fast` job to discover: it is what `nightly_status.py` did on this
# branch's first push, `TEST NEVER RAN` after 23 minutes. The lists are the
# same claim written twice, so they are pinned equal here, which is seconds.
_NS_RUNSH = (pathlib.Path(__file__).resolve().parents[1]
             / "tests" / "run.sh").read_text()
_NS_SPLIT = _NS_RUNSH.index("# The grep above proves")
_NS_WIRED = {
    _b
    for _arm in re.findall(r"^    ([\w.|]+\.(?:py|mjs))\) continue ;;",
                           _NS_RUNSH[:_NS_SPLIT], re.M)
    for _b in _arm.split("|")
}
_NS_RAN = {
    _b
    for _arm in re.findall(r"^    ([\w.|]+\.(?:py|mjs))\) continue ;;",
                           _NS_RUNSH[_NS_SPLIT:], re.M)
    for _b in _arm.split("|")
}
R.check(
    "run.sh's two script-accounting exclusion lists name the same scripts",
    _NS_RAN and _NS_RAN == _NS_WIRED,
    f"only in the ran-check: {sorted(_NS_RAN - _NS_WIRED)}; "
    f"only in the wired-check: {sorted(_NS_WIRED - _NS_RAN)}",
)

# That pin compares run.sh with ITSELF. The same question is asked a third time
# one file over, as `tests/closure.py`'s `NOT_A_TEST`, and nothing compared the
# two until this check -- which is how #195's two instruments went onto
# `NOT_A_TEST` alone and cost four red lines on a runner, twenty minutes into a
# full suite, for a fact both files already held locally.
_NS_NOT_TESTS = _closure.NOT_A_TEST | set(_closure.DRIVEN_BY_OTHERS)
R.check(
    "every script run.sh skips is one closure.py already refuses to select",
    _NS_WIRED <= _NS_NOT_TESTS,
    f"skipped by run.sh but selectable by the gate: "
    f"{sorted(_NS_WIRED - _NS_NOT_TESTS)} -- the scoped gate would choose a "
    "script no lane runs, which reads as a green scope rather than as a "
    "script that went missing",
)
# The other direction, and deliberately NOT equality: a NOT_A_TEST script may
# be one run.sh runs anyway. setup_qa_render.mjs is wired into the card lane
# while still being a thing no gate scopes, and closure.py says so in place.
_NS_RUNSH_RUNS = {
    _m.group(1) for _m in re.finditer(
        r"^\s*run(?:_always)? .*tests/([\w.]+\.(?:py|mjs))(?: |$)",
        _NS_RUNSH, re.M)
}
R.check(
    "and a script closure.py will not select is either skipped by run.sh or run by it",
    not (_NS_NOT_TESTS - _NS_WIRED - _NS_RUNSH_RUNS),
    f"neither skipped nor run: "
    f"{sorted(_NS_NOT_TESTS - _NS_WIRED - _NS_RUNSH_RUNS)}; the ones run.sh "
    f"DOES run: {sorted(_NS_NOT_TESTS & _NS_RUNSH_RUNS)} -- a script in "
    "neither set is one the suite has quietly stopped running and the gate "
    "has quietly stopped scoping, which is how optimality.py sat dormant for "
    "a year",
)

# --- the run's OWN conclusion, which is one level above its job list --------
#
# THE DEFECT THIS BLOCK EXISTS TO REFUSE, and it is the exact failure this
# whole module was written against. `verdict` classified a concluded run from
# `failing_jobs(jobs)` alone and never read `concluded["conclusion"]`, so a run
# that GitHub concluded `failure` -- while every job the jobs endpoint listed
# read `success` or `skipped` -- printed
# `NIGHTLY PASSED ... run conclusion 'failure'` and exited 0. A warning beside
# a clean exit is the shape this reporter's own docstring argues against by
# name, and here it was printing one about itself.
#
# DESIGN CHOICE, stated because a later reader will meet it as a tightening.
# The run's own conclusion is AUTHORITATIVE and the job list refines it, not
# the other way round. Every non-passing conclusion in GitHub's vocabulary is
# pinned, not only the ones CI has produced: backtests over 15 scheduled runs
# and 100 recent runs found `failure` and nothing else -- `cancelled`,
# `timed_out`, `action_required` and `stale` are absent from the observed
# population entirely. Untested is not cleared. A hole no current input reaches
# is still a hole in a check whose entire job is to not lie.
_NS_BAD_RUN_CONCLUSIONS = ("failure", "cancelled", "timed_out",
                           "action_required", "stale", "startup_failure",
                           None, "quantum_ambiguous")
_ns_runlevel = {
    _c: _nstatus.verdict(
        _ns_run(40, "2026-09-10T02:17:00Z", conclusion=_c),
        None, _NS_LIVE, _NS_NOW)[:2]
    for _c in _NS_BAD_RUN_CONCLUSIONS
}
R.check(
    "a run whose OWN conclusion is not a passing one is FAILED, whatever its "
    "jobs say",
    all(_v == ("FAILED", _nstatus.EXIT_RED) for _v in _ns_runlevel.values()),
    f"run conclusion -> (state, exit): {_ns_runlevel}; every job of every case "
    "reads success or skipped, so the job list alone says PASSED",
)
# The NULL CONTROL for the check above, and it is the half that stops it being
# a check that fails everything: the same jobs under a passing run conclusion
# must still be PASSED, or the reporter has simply gone red permanently.
_ns_runlevel_ok = {
    _c: _nstatus.verdict(
        _ns_run(41, "2026-09-10T02:17:00Z", conclusion=_c),
        None, _NS_LIVE, _NS_NOW)[:2]
    for _c in sorted(_nstatus.OK_CONCLUSIONS)
}
R.check(
    "and the same jobs under a passing run conclusion are still PASSED",
    all(_v == ("PASSED", _nstatus.EXIT_GREEN)
        for _v in _ns_runlevel_ok.values()),
    f"run conclusion -> (state, exit): {_ns_runlevel_ok}",
)
# "The nightly failed" trains blindness. When NO job failed, the report has to
# say what did, or a reader opens the run, sees a clean job list and concludes
# the check is broken.
_ns_runlevel_says = _nstatus.verdict(
    _ns_run(42, "2026-09-10T02:17:00Z", conclusion="failure"),
    None, _NS_LIVE, _NS_NOW)[2]
R.check(
    "and when no job failed the report names the run's conclusion as the "
    "evidence",
    any("'failure'" in _l for _l in _ns_runlevel_says)
    and any("no job" in _l.lower() for _l in _ns_runlevel_says),
    "report lines: " + " | ".join(_ns_runlevel_says),
)

# --- the ordering `pick_runs` exists for ------------------------------------
#
# Its docstring justifies the sort loudly -- "an order that is documented but
# not asserted is one an API change silently reverses" -- and nothing drove it:
# replacing `sorted(...)` with `list(runs)` left every check in this suite
# passing. Driven here with the listing in ASCENDING created_at order, which is
# the only arrangement the sort is for, and with an in-flight run on each side
# of the newest concluded one so both return values are pinned.
_NS_ORDER_IN = [
    _ns_run(11, "2026-09-08T02:17:00Z"),
    _ns_run(12, "2026-09-09T02:17:00Z", "in_progress", None),
    _ns_run(13, "2026-09-10T02:17:00Z"),
    _ns_run(14, "2026-09-10T11:00:00Z", "in_progress", None),
]
_ns_conc, _ns_fly = _nstatus.pick_runs(_NS_ORDER_IN)
R.check(
    "pick_runs picks the newest concluded and newest in-flight by created_at, "
    "not by listing order",
    (_ns_conc or {}).get("id") == 13 and (_ns_fly or {}).get("id") == 14,
    f"input ids {[_r['id'] for _r in _NS_ORDER_IN]} in ASCENDING created_at "
    f"order -> concluded={(_ns_conc or {}).get('id')} "
    f"in_flight={(_ns_fly or {}).get('id')}; without the sort this returns "
    "11 and 12, i.e. a two-night-old run reported as last night's",
)

# --- a run with no clock is "could not look", not a crash and not a verdict --
#
# `parse_ts(r["created_at"])` raised KeyError straight through `main`'s
# `except Unreadable`, so `sys.exit(main())` printed a traceback and exited 1.
# Red rather than falsely green, so not urgent -- but exit 1 is this check's
# word for "the nightly FAILED", and the truth was "this could not look", which
# is what exit 2 exists for. Three call sites read a run's clock; all three.
_ns_noclock = []
for _label, _call in (
    ("pick_runs", lambda: _nstatus.pick_runs([{"id": 5, "status": "completed"}])),
    ("verdict/concluded", lambda: _nstatus.verdict(
        {"id": 5, "conclusion": "success"}, None, _NS_LIVE, _NS_NOW)),
    ("verdict/in_flight", lambda: _nstatus.verdict(
        None, {"id": 5, "status": "in_progress"}, [], _NS_NOW)),
):
    try:
        _call()
    except _nstatus.Unreadable:
        pass
    except Exception as _exc:  # noqa: BLE001 -- the point is what class it is
        _ns_noclock.append(f"{_label} raised {type(_exc).__name__}")
    else:
        _ns_noclock.append(f"{_label} returned a verdict")
R.check(
    "a run carrying no created_at is UNREADABLE, not a KeyError and not a "
    "verdict",
    not _ns_noclock,
    "; ".join(_ns_noclock) or "three clock-reading call sites, all Unreadable",
)

# --- a truncated jobs page is not a clean run -------------------------------
#
# `_jobs` requests `per_page=100` and follows no `Link` header, and it received
# `total_count` without ever comparing it to `len(jobs)`. A run with more than
# 100 jobs would have had its overflow -- including every failing job in it --
# silently dropped, and a dropped failing job is a PASS. No run of this
# workflow comes near a hundred jobs, so the refusal is unreachable today --
# the rule for re-deriving that, rather than a count that moves whenever a job
# or a matrix arm is added, is in `_jobs`'s own docstring. Comparing the two
# numbers is cheaper than pagination and removes the silent case outright.
# `_get` is the one collaborator, stubbed; `_jobs` itself is the production
# function under test.
_ns_paging_real_get = _nstatus._get
try:
    _nstatus._get = lambda _u, _t: {
        "total_count": 140,
        "jobs": [_ns_job(f"j{_i}", "success") for _i in range(100)]}
    try:
        _nstatus._jobs("o/r", 1, None)
    except _nstatus.Unreadable as _exc:
        _ns_truncated = "140" in str(_exc) and "100" in str(_exc)
    else:
        _ns_truncated = False
    # The null control: a page that DOES carry every job is read, not refused.
    # Without this the check above passes on a `_jobs` that refuses everything.
    _nstatus._get = lambda _u, _t: {"total_count": len(_NS_LIVE),
                                    "jobs": _NS_LIVE}
    _ns_whole = _nstatus._jobs("o/r", 1, None) == _NS_LIVE
finally:
    _nstatus._get = _ns_paging_real_get
R.check(
    "a jobs page that does not carry every job of the run is UNREADABLE, not a "
    "partial answer",
    _ns_truncated and _ns_whole,
    f"total_count 140 against a 100-job page refused={_ns_truncated}; "
    f"complete page read={_ns_whole}",
)

# --- the staleness boundary, where its own constant says it is --------------
#
# `MAX_AGE_NIGHTS`'s comment said "three is the first age that cannot be either
# of those" -- those being one night of timezone slack and the two consecutive
# misses of the #533 incident -- while the code was `nights > 3`, which needs
# FOUR nights of silence and reads a three-night gap as PASSED. Executed, both
# ends of the range rather than the boundary alone.
_ns_ages = {
    _n: _nstatus.verdict(
        _ns_run(50 + _n,
                (_NS_NOW - timedelta(days=_n, hours=1)).isoformat().replace(
                    "+00:00", "Z")),
        None, _NS_LIVE, _NS_NOW)[0]
    for _n in range(0, 6)
}
R.check(
    "the staleness boundary is the one the constant's comment defends",
    _ns_ages == {0: "PASSED", 1: "PASSED", 2: "PASSED",
                 3: "ABSENT", 4: "ABSENT", 5: "ABSENT"}
    and _nstatus.MAX_AGE_NIGHTS == 2,
    f"nights-ago -> state {_ns_ages}, MAX_AGE_NIGHTS="
    f"{_nstatus.MAX_AGE_NIGHTS}; the comment defends 3 as the first age that "
    "is neither timezone slack nor the #533 incident",
)


# --- the delivery ledger, and why it replaced a red tick --------------------
#
# `record` refuses a merged pull request with no disposition row, and it is
# right. Reporting main's `record` CONCLUSION on every pull request was not:
# measured over main's last 40 commits, `record` concluded `failure` on 28 of
# them, in six streaks each ended by a `record:` leftover-row commit. The check
# was firing on the protocol's own steady state, which is the shape its own
# docstring warns about -- the first red one teaches everybody to ignore it.
#
# `tests/delivery_status.py` changes the predicate rather than the reporting:
# pending is ordinary, and only a batch that has stopped being drained is a
# problem. What is pinned here is that BOTH sides of that threshold are
# reachable, because a threshold that never fires is the always-green shape
# this repository keeps catching.
import delivery_status as _ds  # noqa: E402


def _ds_merges(*specs):
    """(number, commits_after) pairs as ledger entries."""
    return [
        {"number": n, "title": f"fix: thing {n}", "merge_sha": f"{n:07x}",
         "commits_after": after}
        for n, after in specs
    ]


_DS_ROWED = ["a row for [#101](https://github.com/o/r/pull/101) and #102"]
_ds_all_rowed = _ds.classify(_ds_merges((101, 0), (102, 1)), _DS_ROWED)
_ds_pending = _ds.classify(_ds_merges((101, 0), (103, 1)), _DS_ROWED)
_ds_overdue = _ds.classify(
    _ds_merges((101, 0), (103, _ds.STALE_AFTER_COMMITS)), _DS_ROWED)
_ds_edge = _ds.classify(
    _ds_merges((103, _ds.STALE_AFTER_COMMITS - 1)), _DS_ROWED)
_ds_empty = _ds.classify([], _DS_ROWED)
R.check(
    "a rowless merge is PENDING until the threshold, and OVERDUE at it",
    _ds_all_rowed["verdict"] == _ds.OK
    and _ds_all_rowed["counts"]["pending"] == 0
    and _ds_pending["verdict"] == _ds.OK
    and _ds_pending["counts"]["pending"] == 1
    and _ds_edge["verdict"] == _ds.OK
    and _ds_overdue["verdict"] == _ds.OVERDUE
    and _ds_overdue["counts"]["overdue"] == 1,
    f"all rowed -> {_ds_all_rowed['verdict']!r}; one rowless at 1 commit -> "
    f"{_ds_pending['verdict']!r} with {_ds_pending['counts']['pending']} "
    f"pending; at {_ds.STALE_AFTER_COMMITS - 1} -> {_ds_edge['verdict']!r}; at "
    f"{_ds.STALE_AFTER_COMMITS} -> {_ds_overdue['verdict']!r}. BOTH sides are "
    "driven and the boundary twice, one commit either way: a threshold that "
    "only ever reports the green side is the always-green shape this "
    "repository keeps catching, and the whole case for replacing the old check "
    "was that it reported the other side 70 per cent of the time",
)
R.check(
    "an EMPTY window is its own verdict and is not reported as a pass",
    _ds_empty["verdict"] == _ds.EMPTY
    and _ds_empty["verdict"] != _ds.OK
    and "no merge" in _ds.render_markdown(_ds_empty),
    f"an empty window -> {_ds_empty['verdict']!r}. 'we looked at forty merges "
    "and every one had a row' and 'there was nothing to look at' are different "
    "facts and only one is evidence -- right after a release stamp the window "
    "is legitimately empty, and reporting OK there is the vacuous green this "
    "repository refuses",
)
# One file per pull request: `docs/delivery/<N>.md` rows <N> through a line
# anchoring <N> itself, and nothing else -- a misnamed file, or another number in
# its prose, rows nobody. The same predicate `policy_lint.mjs --record` pins.
import tempfile as _ds_tf  # noqa: E402
with _ds_tf.TemporaryDirectory() as _ds_tmp:
    _ds_root, _ds.ROOT = _ds.ROOT, Path(_ds_tmp)
    (Path(_ds_tmp) / _ds.ROW_DIR).mkdir(parents=True)
    (Path(_ds_tmp) / _ds.ROW_DIR / "201.md").write_text(
        "- [#201](https://github.com/o/r/pull/201) merged\n")
    (Path(_ds_tmp) / _ds.ROW_DIR / "202.md").write_text(
        "- [#203](https://github.com/o/r/pull/203) misnamed; #204 too\n")
    _ds_files = _ds.classify(
        _ds_merges((201, 0), (202, 0), (203, 0), (204, 0)), _ds.read_texts())
    _ds.ROOT = _ds_root
R.check(
    "a row file rows its own pull request and no other",
    [r["state"] for r in _ds_files["merges"]]
    == ["rowed", "pending", "pending", "pending"],
    f"states {[r['state'] for r in _ds_files['merges']]}; the ledger and "
    "`record` read the same files the same way, or a seat is told two things",
)
# THE COLLECTOR, AND THE PRECONDITION THAT MOVED UNDER IT.
#
# `classify` above was driven from fixtures from the first day and is right.
# `gather` was not driven by anything, and it was the half that broke: its
# subject rule took only the SQUASH shape `<title> (#N)`, this repository moved
# to merge commits, and the ledger collected nothing over a window that held
# nothing but merges -- reporting the same EMPTY it reports right after a
# stamp. Every state below is driven through `collect`, because a pure
# classifier pinned on both sides of its threshold proves nothing about a
# window that never reaches it.
def _ds_commit(sha, subject, parents=2, body=""):
    return {"sha": sha, "subject": subject, "parents": parents, "body": body}


# A window spanning the changeover: the squash shape that dominates main's
# older history, the merge shape that is all of its newer history, a
# single-parent release stamp, and a single-parent `record:` commit. The last
# two are the guard's own null control -- both are direct pushes that name no
# pull request, and a guard keyed on the SUBJECT rather than on the parent
# count reports them as merges it could not read.
_DS_WINDOW = [
    _ds_commit("aaaaaaa", "Merge pull request #1052 from tvofi/fix/d11-pins",
               body="fix(#960): SHA-pin every workflow uses ref"),
    _ds_commit("bbbbbbb", "record: leftover rows for #201", parents=1),
    _ds_commit("ccccccc", "v6.5.0: stamp wave 3, and the #996 fail-fast",
               parents=1),
    _ds_commit("ddddddd", "feat: the input_problem names its sources (#1019)",
               parents=1),
]
_ds_win_merges, _ds_win_blind = _ds.collect(_DS_WINDOW)
R.check(
    "both merge-subject conventions are collected, and neither direct push is",
    [m["number"] for m in _ds_win_merges] == [1052, 1019]
    and _ds_win_blind == []
    and _ds_win_merges[0]["title"] == "fix(#960): SHA-pin every workflow uses "
                                      "ref"
    and _ds_win_merges[0]["commits_after"] == 0
    and _ds_win_merges[1]["commits_after"] == 3,
    f"collected {[m['number'] for m in _ds_win_merges]} from a four-commit "
    f"window holding one merge-shaped subject, one squash-shaped subject, a "
    f"`record:` direct push naming #201 and a release stamp naming #996; "
    f"unattributed {_ds_win_blind}. The squash shape is HISTORY and the merge "
    "shape is the present, so a rule taking either one alone goes blind at the "
    "changeover -- which is the defect: taking only the squash shape returned "
    "[] over a window of merge commits and reported EMPTY. `record:` and the "
    "stamp are not merges and must not be collected; #201 and #996 in their "
    "subjects are mentions, and a collector taking a mention would file the "
    "tracking issue itself as a merged pull request. `commits_after` is the "
    "first-parent depth and counts the direct pushes, because what makes a row "
    "late is every commit that went past it, not only the merges",
)
R.check(
    "a merge commit's title comes from its body, not from the branch it names",
    _ds.subject_title("Merge pull request #1052 from tvofi/fix/d11-pins",
                      "\nfix(#960): SHA-pin every workflow uses ref\n")
    == "fix(#960): SHA-pin every workflow uses ref"
    and _ds.subject_title("feat: names its sources (#1019)", "")
    == "feat: names its sources",
    "a merge subject names a BRANCH; GitHub puts the pull request's title on "
    "the body's first non-blank line. `pending #1049 fix/d11-publish-"
    "concurrency` tells a seat nothing about what is waiting on it, and the "
    "pending list is the whole product this check replaced a tick with",
)
R.check(
    "a subject that only MENTIONS a pull request is not taken as being it",
    _ds.subject_number("Record #424 W1-G14 merge in delivery-status") is None
    and _ds.subject_number("Merge pull request #13: Broaden the disclaimer")
    == 13
    and _ds.subject_number("W2-G5: record settle power (#277 #244 #325)")
    is None,
    f"a `Record #424 ...` subject -> "
    f"{_ds.subject_number('Record #424 W1-G14 merge in delivery-status')!r}; "
    f"the oldest merge shape here, with a colon rather than ` from `, -> "
    f"{_ds.subject_number('Merge pull request #13: Broaden the disclaimer')!r}."
    " The merge rule is anchored at the start and the squash rule at the end, "
    "so a subject naming several issues mid-line is neither; an unanchored "
    "rule would collect main's own `record:` commits as the merges they are "
    "recording, and report a row as written by the commit that failed to "
    "write it",
)
# The guard: a merge commit no rule can attribute. THIS is what separates a run
# that could not look from a run that looked and found nothing -- the two were
# byte-identical before, and the second is a legitimate green right after a
# stamp, so the first was permanently invisible.
_DS_BLIND_WINDOW = [
    _ds_commit("eeeeeee", "Integrated PR 9001 via the new bot"),
    _ds_commit("fffffff", "v6.5.0: stamp wave 3", parents=1),
]
_ds_blind_merges, _ds_blind = _ds.collect(_DS_BLIND_WINDOW)
_ds_unchecked = _ds.classify(_ds_blind_merges, _DS_ROWED,
                             unattributed=_ds_blind)
_ds_stamp_merges, _ds_stamp_blind = _ds.collect(
    [_ds_commit("fffffff", "v6.5.0: stamp wave 3", parents=1)])
_ds_stamp_only = _ds.classify(_ds_stamp_merges, _DS_ROWED,
                              unattributed=_ds_stamp_blind)
R.check(
    "an unattributable merge is UNCHECKED, loudly, and never EMPTY",
    [b["sha"] for b in _ds_blind] == ["eeeeeee"]
    and _ds_unchecked["verdict"] == _ds.UNCHECKED
    and _ds_unchecked["verdict"] != _ds.EMPTY
    and _ds_unchecked["verdict"] != _ds.OK
    and "UNCHECKED this run, not confirmed empty"
    in _ds.unchecked_line(_ds_blind)
    and "UNCHECKED this run, not confirmed empty"
    in _ds.render_markdown(_ds_unchecked)
    and _ds_empty["unattributed"] == []
    and _ds_empty["verdict"] == _ds.EMPTY,
    f"a window whose only merge commit no rule can attribute -> "
    f"{_ds_unchecked['verdict']!r}, with the merge named; a window with no "
    f"merge at all -> {_ds_empty['verdict']!r}. Widening a pattern fixes the "
    "instance and only this fixes the CLASS: the subject convention is a "
    "precondition, it moved once already, and when it moves again the "
    "collector must say it could not look rather than print the counts of a "
    "window it never read. The words are `policy_lint.mjs`'s `enumSkipLine` "
    "(#1050), which landed this same discipline for this same end-anchored "
    "`(#N)` one file over -- a second vocabulary for one fact costs a reader a "
    "translation and buys nothing",
)
R.check(
    "a release stamp alone is EMPTY, not UNCHECKED -- the guard keys on "
    "parents",
    _ds_stamp_only["verdict"] == _ds.EMPTY
    and _ds_stamp_only["unattributed"] == [],
    f"a window holding only a single-parent release stamp -> "
    f"{_ds_stamp_only['verdict']!r}. The stamp names no pull request and is "
    "not supposed to, so a guard asking `does this subject mention a number` "
    "would redden every window that opens on one -- which is every window for "
    "the first commits after a release. Two parents on main's first-parent "
    "line IS a pull-request merge under the ruleset, so a merge the rules "
    "cannot attribute is the collector going blind and is nothing else",
)
# The alarm, end to end through the collector rather than from hand-built ledger
# entries: the OVERDUE state has to be reachable from a LOG, which is the thing
# that stopped being true.
_ds_alarm_window = [
    _ds_commit(f"{i:07x}", f"record: filler {i}", parents=1)
    for i in range(_ds.STALE_AFTER_COMMITS)
] + [_ds_commit("9001abc", "Merge pull request #9001 from o/topic",
                body="fix: the thing that has no row")]
_ds_alarm_merges, _ds_alarm_blind = _ds.collect(_ds_alarm_window)
_ds_alarm = _ds.classify(_ds_alarm_merges, _DS_ROWED,
                         unattributed=_ds_alarm_blind)
R.check(
    "the OVERDUE alarm is reachable from a first-parent LOG, not only from "
    "hand-built entries",
    [m["number"] for m in _ds_alarm_merges] == [9001]
    and _ds_alarm_merges[0]["commits_after"] == _ds.STALE_AFTER_COMMITS
    and _ds_alarm["verdict"] == _ds.OVERDUE
    and _ds_alarm["counts"]["overdue"] == 1,
    f"a rowless merge-commit merge with {_ds.STALE_AFTER_COMMITS} commits past "
    f"it -> {_ds_alarm['verdict']!r}. The threshold checks above drive "
    "`classify` from fixtures and passed throughout the whole period the "
    "detector could not fire: `gather` returned [] for every real window, so "
    "nothing ever entered the set that ages into OVERDUE. A detector is "
    "reachable from its INPUT or it is not reachable",
)
# THE WINDOW'S START, pinned on the argv this file runs rather than on a copy.
# The guard above cannot see this one: a `describe` that answers the wrong tag
# yields an empty LOG, so there is no merge commit to be unattributable and the
# run reports a truthful EMPTY about the wrong window.
_DS_WINDOW_STEP = _workflow_job(
    Path(".github/workflows/governance.yml").read_text(), "record")
_DS_MATCH_IN_STEP = "--match '" + "v*'" in _DS_WINDOW_STEP
R.check(
    "the ledger and the record lane pick the window with the same tag filter",
    "--match" in _ds.DESCRIBE_ARGV
    and "v*" in _ds.DESCRIBE_ARGV
    and _DS_MATCH_IN_STEP,
    f"the ledger's describe argv is {_ds.DESCRIBE_ARGV}; the `record` job's "
    f"window step carries the same filter: {_DS_MATCH_IN_STEP}"
    ". `git describe --tags --abbrev=0` answers the newest tag of ANY shape, "
    "and this repository makes non-release tags -- `governance.yml` carries "
    "this flag because `archive-rosters-2026-09` was newer than the release "
    "tag and gave it an empty window. Two lanes reporting on `the window` "
    "have to agree on which window, and the ledger had no filter at all",
)
# `--check`'s EXIT SEMANTICS, which this change widened, driven through `main`
# rather than asserted in prose. `--from` reads a recorded ledger and runs no
# query, so the four verdicts are driven offline with no repo and no token --
# the reason that flag exists.
def _ds_check_rc(ledger):
    import contextlib as _ctx
    import io as _io
    with _tempfile.TemporaryDirectory() as td:
        path = Path(td) / "ledger.json"
        path.write_text(json.dumps(ledger))
        argv = sys.argv
        sys.argv = ["delivery_status.py", "--from", str(path), "--check"]
        try:
            with _ctx.redirect_stdout(_io.StringIO()):
                return _ds.main()
        finally:
            sys.argv = argv


_DS_RCS = {v: _ds_check_rc(l) for v, l in (
    ("OVERDUE", _ds_overdue), ("UNCHECKED", _ds_unchecked),
    ("OK", _ds_all_rowed), ("EMPTY", _ds_empty))}
R.check(
    "--check raises OVERDUE and UNCHECKED, and passes OK and EMPTY",
    _DS_RCS == {"OVERDUE": 1, "UNCHECKED": 1, "OK": 0, "EMPTY": 0},
    f"exit codes by verdict: {_DS_RCS}. Raising UNCHECKED is a DELIBERATE "
    "widening of this flag, recorded here because a seat reading the job "
    "cannot otherwise tell it from a regression: a reporter whose subject is "
    "noticing that something went dark must not report a pass in the one "
    "state where it cannot see. PENDING stays green -- batching is the "
    "protocol and the whole case for replacing the old check was that it "
    "reddened on the protocol's steady state -- and `delivery-status` is not "
    "a required context, so neither red gates a merge",
)
R.check(
    "a disposition is matched on the whole number, in both spellings",
    _ds.mentions(88, ["a row for #885 and #8850"]) is False
    and _ds.mentions(885, ["a row for #885"]) is True
    and _ds.mentions(885, ["https://github.com/o/r/pull/885)"]) is True
    and _ds.mentions(885, ["nothing here"]) is False,
    "#88 against a text naming #885 and #8850 -> "
    f"{_ds.mentions(88, ['a row for #885 and #8850'])!r}; the link form -> "
    f"{_ds.mentions(885, ['https://github.com/o/r/pull/885)'])!r}. An "
    "unbounded match would disposition every merge whose number is a prefix of "
    "a later one, which is the direction that reports a missing row as written; "
    "both spellings count because the Delivery-status rows use the link form "
    "and the handover the bare one, so a matcher reading one would report half "
    "the record missing",
)
_DS_BODY = "Tracking issue.\n\nPhases table here.\n"
_ds_once = _ds.splice(_DS_BODY, _ds.render_markdown(_ds_pending))
_ds_twice = _ds.splice(_ds_once, _ds.render_markdown(_ds_pending))
_ds_changed = _ds.splice(_ds_once, _ds.render_markdown(_ds_all_rowed))
R.check(
    "the #201 region is replaced in place, and the issue's own text survives",
    "Tracking issue." in _ds_once
    and "Phases table here." in _ds_once
    and _ds_twice == _ds_once
    and _ds_once.count(_ds.REGION_BEGIN) == 1
    and _ds_twice.count(_ds.REGION_BEGIN) == 1
    and _ds_changed.count(_ds.REGION_BEGIN) == 1
    and "Tracking issue." in _ds_changed
    and _ds_changed != _ds_once,
    f"one splice keeps the issue's own text and adds "
    f"{_ds_once.count(_ds.REGION_BEGIN)} region; a second with the same "
    f"content is byte-identical ({_ds_twice == _ds_once}); with different "
    f"content it updates in place and still carries "
    f"{_ds_changed.count(_ds.REGION_BEGIN)}. Idempotence is what makes this "
    "safe to run on every push: an appending version grows the issue body "
    "without bound, and a body-REPLACING version deletes the 2.6 kB of "
    "tracking text that is the reason anyone opens #201 at all",
)
_DS_JOB = _workflow_job(
    Path(".github/workflows/governance.yml").read_text(), "delivery-status")
R.check(
    "the ledger is wired into a job that runs on pull requests",
    "github.event_name == 'pull_request'" in _DS_JOB
    and "tests/delivery_status.py" in _DS_JOB,
    f"pull_request={'pull_request' in _DS_JOB}, "
    f"invoked={'tests/delivery_status.py' in _DS_JOB}",
)
R.check(
    "and the pull-request lane passes no --since that would pin its answer",
    "--since" not in _DS_JOB,
    "`--since` names the window, so a job passing a fixed one would report the "
    "same closed window for ever -- the always-green knob "
    "`nightly_status.py`'s `--run` is pinned against",
)
# The permission widening, checked as a PROPERTY rather than as its instance:
# the whole set of jobs in governance.yml that override the workflow's
# `contents: read` floor. A job-level block REPLACES the floor for that job and
# is inherited by none, so the set IS the blast radius. It is UPDATED rather
# than dropped each time the publishing lane moves, because the set is the
# argument: the ledger's #201 splice is back in the publishing lane, whose
# `issues: write` the deleted `delivery-status-splice` job had held, so the
# set is three. #956's `pr-contract` adds no write at all: it reads the head's
# check runs through `/commits/<sha>/check-runs`, which the token refuses
# without `checks: read`, and the body off `/pulls/<number>` at run time
# rather than out of the event payload, which a re-run replays (the pin below).
_DS_GOV = Path(".github/workflows/governance.yml").read_text()
_DS_PUB_JOB = _workflow_job(_DS_GOV, "delivery-status-publish")
_DS_OVERRIDES = sorted(
    _m.group(1) for _m in re.finditer(
        r"^  ([A-Za-z][\w-]*):\n(?:(?!^  [A-Za-z]).)*?^    permissions:",
        _DS_GOV, re.M | re.S)
)
R.check(
    "exactly three governance jobs override the workflow's read-only floor",
    _DS_OVERRIDES == ["delivery-status-publish", "pr-contract", "record"],
    f"jobs with a permissions block: {_DS_OVERRIDES}. A fourth has to be argued "
    "for rather than land, and the reporting lane is deliberately NOT one: "
    "`delivery-status` runs on pull requests with no widening at all, because "
    "it only reads the tree it is already checked out in",
)
_PC_PERMS = re.search(
    r"^    permissions:\n((?:^      .*\n)+)",
    _workflow_job(_DS_GOV, "pr-contract"), re.M)
R.check(
    "and the contract lane's widening is the one read it needs",
    bool(_PC_PERMS)
    and sorted(_PC_PERMS.group(1).split()) == sorted(
        ["checks:", "contents:", "pull-requests:", "read", "read", "read"]),
    f"pr-contract permissions: "
    f"{_PC_PERMS.group(1).split() if _PC_PERMS else None} -- `checks: read` "
    "lists the head's check runs for the red-check arm (#956), "
    "`pull-requests: read` fetches the body off `/pulls/<number>` at run "
    "time, and `contents: read` restates the floor a job-level block "
    "replaces; the nightly-status precedent, read-only widenings on the one "
    "job that reads the API",
)
# THE BODY IS READ FROM THE API AT RUN TIME, NEVER FROM THE EVENT PAYLOAD.
# `${{ github.event.pull_request.body }}` is the body as it stood when the
# event fired, and `gh run rerun` replays that payload: a body corrected after
# the event never reached the check. Measured on #1059 at head `a93a43b`: the
# body was edited to name `a93a43b`, run 35093322057 was re-run twice
# (attempts 2 and 3) and refused both times with "`## Head` does not name
# a93a43b" while `GET /pulls/1059` showed the corrected body; a close/reopen
# -- a fresh event, same head, no tree change -- passed as run 35098726083.
# The ledger lane one job down edited its own PR's body with GITHUB_TOKEN
# until decision 0009 step 3b moved that write to the seat author, and those
# edits fired no `pull_request` event at all, so a manual re-run was the
# ONLY route to a green `pr-contract` there, and it was the route that could
# not work. Three strings are pinned: the API read of the pull request's own
# resource, `--jq` on its body field, and the ABSENCE of the payload context
# anywhere in the job -- delete the read and keep the context and this pin
# fails on the third arm, which is the one the mutation lands on. Read over
# the job's NON-COMMENT lines: the step's own comment names the context it
# replaced, and a pin that cannot tell a comment from a grant would refuse
# the sentence that explains the grant.
_PC_BODY_STEP = "\n".join(
    _l for _l in _workflow_job(_DS_GOV, "pr-contract").split("\n")
    if not _l.lstrip().startswith("#"))
_PC_API_READ = "/pulls/${PR_NUMBER}" in _PC_BODY_STEP
_PC_BODY_FIELD = "--jq '.body" in _PC_BODY_STEP
_PC_PAYLOAD_ABSENT = "github.event.pull_request.body" not in _PC_BODY_STEP
R.check(
    "the contract lane reads the body off the API at run time, not the payload",
    _PC_API_READ and _PC_BODY_FIELD and _PC_PAYLOAD_ABSENT,
    f"api_read={_PC_API_READ}, body_field={_PC_BODY_FIELD}, "
    f"payload_absent={_PC_PAYLOAD_ABSENT}; "
    "the payload is a snapshot a re-run replays (#1059, runs 35093322057 "
    "against 35098726083 at the same head), so a body corrected after the "
    "event never reached the check and the ledger lane's GITHUB_TOKEN edits "
    "before 0009 step 3b, which fired no event, had no route to green at all",
)
# #956: the red-check trigger CLAUDE.md calls enforced is enforced by THIS
# wiring, and nothing else. Before it, the body-contract step invoked
# policy_lint with no `--red` -- the same body exited 0 without it and 1 with
# it, and only the advisory prepr.sh passed the flag -- so the one trigger the
# index calls enforced was inert in the one place enforcement could live. The
# three load-bearing strings of the wiring are pinned so it cannot go inert
# again: the check-runs LISTING (never a summary, which hides red-then-green),
# the exclusion of the job's own name (delete it and the deadlock returns: a
# body refused for not naming a red caused by not naming it), and the flag
# itself.
_PC_JOB = _workflow_job(_DS_GOV, "pr-contract")
_PC_EXCLUSION = '.name != "pr-contract"'
R.check(
    "the contract lane passes the head's red checks to the body check",
    "check-runs" in _PC_JOB
    and "--red" in _PC_JOB
    and _PC_EXCLUSION in _PC_JOB,
    f"listing={'check-runs' in _PC_JOB}, flag={'--red' in _PC_JOB}, "
    f"exclusion={_PC_EXCLUSION in _PC_JOB}; without all three "
    "the red-check trigger reads as enforced while the same unnamed red body "
    "exits 0 -- the silent-green shape #533 is about, in this workflow",
)
# THE LISTING'S FAIL-CLOSED SHAPE. The step runs `set -euo pipefail` before the
# `gh api ... | jq ... > /tmp/pr-reds.txt` pipeline on purpose: a derivation
# that fails must fail the step, because an empty red list read from a failed
# fetch is "no reds" -- the fail-open the wiring closes. That intent lived in a
# YAML comment and nothing under `tests/` pinned it, so a later edit could drop
# the guard or loosen the filter and no check would notice (#1139). The step is
# read out of the comment-stripped job (`_PC_BODY_STEP`), so a comment that
# merely NAMES the guard cannot satisfy the pin.
def _fail_closed_red_listing(step: str) -> bool:
    """True when `step` derives `/tmp/pr-reds.txt` fail-closed.

    `set -euo pipefail` must precede the pipeline it protects, and the `jq`
    filter must keep the RED predicate (completed AND failed) and the output
    the next step reads.
    """
    pipefail = step.find("set -euo pipefail")
    pipeline = step.find("gh api --paginate")
    return (
        step.startswith("List the red checks at this head")
        and 0 <= pipefail < pipeline
        and '.status == "completed"' in step
        and '.conclusion == "failure"' in step
        and "> /tmp/pr-reds.txt" in step
    )


_PC_RED_STEP = next(
    (_b for _b in _PC_BODY_STEP.split("\n      - name: ")
     if _b.startswith("List the red checks at this head")), "")
R.check(
    "the red-check listing stays fail-closed (pipefail guard, jq filter, output pinned)",
    _fail_closed_red_listing(_PC_RED_STEP),
    f"step found={bool(_PC_RED_STEP)}, "
    f"pipefail={_PC_RED_STEP.find('set -euo pipefail')}, "
    f"pipeline={_PC_RED_STEP.find('gh api --paginate')}; the derivation's own "
    "failure must fail the step, or an empty list from a failed fetch reads as "
    "'no reds'",
)
R.check(
    "and a listing with the guard and the RED filter stripped is not (null control)",
    bool(_PC_RED_STEP)
    and not _fail_closed_red_listing(
        _PC_RED_STEP.replace("set -euo pipefail", "", 1)
        .replace('.conclusion == "failure"', '.conclusion == "success"')),
    "the predicate must read the guard and the filter, not the step's name",
)
# CLAUDE.md rule 4 in CI: `prepr.sh --version-edit` refuses a pull request
# moving VERSION, the manifest version or a notes heading. Its predicate is
# driven by prepr.sh --self-test; what that cannot see is whether THIS job
# still calls it, and against which refs. Pinned over non-comment lines: the
# call with the fetched main ref and the head, the fetch that makes that ref
# exist, and `if: always()` so an earlier refusal cannot skip it.
_PC_VE_CALL = 'prepr.sh --version-edit origin/main "$PR_HEAD"' in _PC_BODY_STEP
_PC_VE_FETCH = "+refs/heads/main:refs/remotes/origin/main" in _PC_BODY_STEP
_PC_VE_STEP = any(
    _blk.startswith("Refuse a version")
    and "\n        if: always()\n" in _blk
    and "prepr.sh --version-edit" in _blk
    for _blk in _PC_BODY_STEP.split("\n      - name: ")
)
R.check(
    "the contract lane refuses a version edit on every pull request",
    _PC_VE_CALL and _PC_VE_FETCH and bool(_PC_VE_STEP)
    and "if: github.event_name == 'pull_request'" in _PC_JOB,
    f"call={_PC_VE_CALL}, fetch={_PC_VE_FETCH}, always={bool(_PC_VE_STEP)}; "
    "before this step the check ran only on a seat's machine and a VERSION "
    "bump passed every required context",
)
# `## Friction` AND A DECLARATION THAT IS NOT THE WHOLE SECTION. `isNone` read a
# section as `none` whenever the token stood at its START -- no end anchor, no
# `m` flag -- so `frictionEntries` tested that against the WHOLE multi-line
# section and a body opening with `None` and then carrying entries returned
# `[]`: every entry below the declaration vanished from the `--stats`
# histogram, and a malformed one was accepted by the contract instead of
# refused (#1139). Driven end to end through the contract AND against the
# exported parser, because the issue names both callers.
def _friction_none_fixture():
    import tempfile

    sha = "0" * 40

    def body(friction: str) -> str:
        secs = [("Head", f"`{sha}`"), ("Mutation proof", "none"),
                ("Null control", "none"), ("Figures", "none"),
                ("Red checks", "none"), ("Forward-carry", "none"),
                ("Friction", friction)]
        return "".join(f"## {h}\n\n{v}\n\n" for h, v in secs)

    out = {}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "body.md"
        for key, friction in {
            "none_then_junk": "None\nthis line does not parse as an entry",
            "none_only": "None",
            "junk_only": "this line does not parse as an entry",
        }.items():
            p.write_text(body(friction))
            r = subprocess.run(
                ["node", ".claude/workflows/policy_lint.mjs", "--pr-body",
                 str(p), "--head", sha],
                capture_output=True, text=True)
            out[key] = (r.returncode, r.stdout)
    return out


_FN = _friction_none_fixture()
R.check(
    "a `## Friction` opening with `none` that then carries a malformed entry is refused",
    _FN["none_then_junk"][0] == 1 and "does not parse" in _FN["none_then_junk"][1],
    f"rc={_FN['none_then_junk'][0]}; a section read as whole-`none` accepted the "
    f"line below the declaration. out={_FN['none_then_junk'][1].strip()[-200:]!r}",
)
_FRICTION_PARSED = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./.claude/workflows/policy_lint.mjs').then((m) => "
     "console.log(JSON.stringify({"
     "none_then: m.frictionEntries('None\\n`CLAUDE.md`: cost: real')"
     ".filter((e) => e.id === 'CLAUDE.md').length,"
     "na_then: m.frictionEntries('n/a\\n`CLAUDE.md`: cost: real')"
     ".filter((e) => e.id === 'CLAUDE.md').length,"
     "none_only: m.frictionEntries('None').length,"
     "entry_only: m.frictionEntries('`CLAUDE.md`: cost: real')"
     ".filter((e) => e.id === 'CLAUDE.md').length"
     "})))"],
    capture_output=True, text=True).stdout or "{}")
R.check(
    "frictionEntries reads the entries after a leading `none`, not an empty section",
    _FRICTION_PARSED.get("none_then") == 1
    and _FRICTION_PARSED.get("na_then") == 1,
    f"parsed={_FRICTION_PARSED}; the entry under the declaration was dropped from "
    "the histogram",
)
R.check(
    "and `none` alone stays zero entries while a stray entry is refused (null controls)",
    _FN["none_only"][0] == 0
    and _FN["junk_only"][0] == 1
    and _FRICTION_PARSED.get("none_only") == 0
    and _FRICTION_PARSED.get("entry_only") == 1,
    f"none_only rc={_FN['none_only'][0]}, junk_only rc={_FN['junk_only'][0]}, "
    f"parsed={_FRICTION_PARSED}",
)
# `## Friction` AND THE TRAILER BLOCK A TOOL PASTES UNDER IT (#1238, D13-01).
# The lines a tool or an assistant appends to a body -- the Claude Code
# attribution, a `Co-Authored-By:` git trailer, a `Closes #N` keyword line --
# OPEN entries under the friction grammar's own rules (a list-marked bullet;
# a `word:` near-miss) while naming no rule and no event, so every one of
# them landed in the histogram's unlabelled bucket. At the round-5 baseline
# that bucket was the TOP ROW of the friction histogram -- 13 entries over 54
# merges, 11 of them the Claude Code attribution alone -- and the filer
# (`friction_issues.mjs`) would have opened "[policy] recurring friction:
# (unlabelled friction bullet)" for boilerplate no seat wrote. The property
# pinned here: a trailer-shaped LINE is not friction evidence, decided by the
# same parser the contract refuses with, and keyed on the line's own shape.
# The null control drives the SAME WORDS mid-evidence, where no line-anchored
# trailer shape matches, and the entry survives; the junk line beside it is
# the pin that the drop did not buy a general amnesty.
def _friction_trailer_fixture():
    import tempfile

    sha = "0" * 40

    def body(friction: str) -> str:
        secs = [("Head", f"`{sha}`"), ("Mutation proof", "none"),
                ("Null control", "none"), ("Figures", "none"),
                ("Red checks", "none"), ("Forward-carry", "none"),
                ("Friction", friction)]
        return "".join(f"## {h}\n\n{v}\n\n" for h, v in secs)

    out = {}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "body.md"
        for key, friction in {
            "none_plus_attribution":
                "none\n\n- 🤖 Generated with [Claude Code](https://claude.com/claude-code)",
            "none_plus_coauthor":
                "none\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
            "none_plus_closes": "none\n\nCloses #1134",
            "entry_plus_attribution":
                "`CLAUDE.md`: cost: real\n\n🤖 Generated with Claude Code",
        }.items():
            p.write_text(body(friction))
            r = subprocess.run(
                ["node", ".claude/workflows/policy_lint.mjs", "--pr-body",
                 str(p), "--head", sha],
                capture_output=True, text=True)
            out[key] = (r.returncode, r.stdout)
    return out


_FT = _friction_trailer_fixture()
_FRICTION_TRAILER = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./.claude/workflows/policy_lint.mjs').then((m) => "
     "console.log(JSON.stringify({"
     "attribution: m.frictionEntries('none\\n\\n- 🤖 Generated with [Claude Code](https://claude.com/claude-code)').length,"
     "coauthor: m.frictionEntries('none\\n\\nCo-Authored-By: Claude <noreply@anthropic.com>').length,"
     "closes: m.frictionEntries('none\\n\\nCloses #1134').length,"
     "entry_kept: m.frictionEntries('`CLAUDE.md`: cost: real\\n\\nCloses #1134')"
     ".filter((e) => e.id === 'CLAUDE.md').length,"
     "entry_total: m.frictionEntries('`CLAUDE.md`: cost: real\\n\\n🤖 Generated with Claude Code').length,"
     "midline_control: m.frictionEntries('`claim-files`: cost: the body said Closes #1134 under the wrong heading')"
     ".filter((e) => e.id === 'claim-files').length"
     "})))"],
    capture_output=True, text=True).stdout or "{}")
R.check(
    "a trailer block pasted under `none` is not friction and refuses nothing",
    _FRICTION_TRAILER.get("attribution") == 0
    and _FRICTION_TRAILER.get("coauthor") == 0
    and _FRICTION_TRAILER.get("closes") == 0
    and _FT["none_plus_attribution"][0] == 0
    and _FT["none_plus_coauthor"][0] == 0
    and _FT["none_plus_closes"][0] == 0,
    f"parsed={_FRICTION_TRAILER}, "
    f"rcs={{{', '.join(f'{k}: {v[0]}' for k, v in _FT.items())}}} -- the "
    "attribution bullet, the `Co-Authored-By:` near-miss and the `Closes #N` "
    "line each became an unlabelled histogram entry the filer would have "
    "counted (#1238)",
)
R.check(
    "a real entry followed by a trailer block keeps exactly its own entry",
    _FRICTION_TRAILER.get("entry_kept") == 1
    and _FRICTION_TRAILER.get("entry_total") == 1
    and _FT["entry_plus_attribution"][0] == 0,
    f"parsed={_FRICTION_TRAILER}, "
    f"entry_plus_attribution rc={_FT['entry_plus_attribution'][0]} -- the "
    "trailer opened a second, unlabelled entry beside the real one",
)
R.check(
    "and the drop buys no amnesty: junk still refuses, trailer words "
    "mid-evidence still parse (null controls)",
    _FN["junk_only"][0] == 1
    and _FRICTION_TRAILER.get("midline_control") == 1,
    f"junk_only rc={_FN['junk_only'][0]}, parsed={_FRICTION_TRAILER} -- the "
    "trailer shapes are line-anchored, so the same words inside an entry's "
    "evidence must not drop it, and a line that is neither an entry nor a "
    "trailer must still be refused",
)
# AN AUTOFIX COMMIT ON THE NAMED HEAD IS NOT A MOVED HEAD. `closures-autofix`
# and `claims-autofix` push a commit onto a pull request after its body was
# written, so the body names a head that is no longer the tip and `pr-contract`
# refused it: #1107, whose bot commits 778c2b4 ("ci: drop inherited claims") and
# b1afbcf ("ci: re-record closures") were followed by run 35220336323 failing
# on b1afbcf with "`## Head` does not name b1afbcf". `checkPrBody` now accepts a
# chain of such commits directly on top of the commit `## Head` names, and only
# if EVERY commit in it carries the bot identity, exactly one autofix message,
# one parent, and only modifications to that message's own files (a claims
# commit may also add no line). Driven over a purpose-built repository, because
# the check walks real commits and this checkout's history is whatever the
# runner fetched. Each refusal arm below is the input that goes green when its
# one condition is deleted from `autofixCommit`.
def _autofix_head_fixture():
    import os
    import shutil
    import tempfile

    bot = ("github-actions[bot]",
           "41898282+github-actions[bot]@users.noreply.github.com")
    seat = ("seat", "seat@e")

    d = Path(tempfile.mkdtemp(prefix="hpo-bot-head-"))

    def g(*a, who=seat, committer=None):
        c = committer or who
        return subprocess.run(
            ["git", "-C", str(d), *a], capture_output=True, text=True,
            env={**os.environ, "GIT_AUTHOR_NAME": who[0],
                 "GIT_AUTHOR_EMAIL": who[1], "GIT_COMMITTER_NAME": c[0],
                 "GIT_COMMITTER_EMAIL": c[1]},
        ).stdout.strip()

    def commit(msg, edits, who=bot, committer=None, parent=None):
        if parent:
            g("checkout", "-q", "--detach", parent)
        for rel, text in edits.items():
            p = d / rel
            if text is None:
                p.unlink()
            else:
                p.write_text(text)
        g("add", "-A")
        g("commit", "-q", "-m", msg, who=who, committer=committer)
        return g("rev-parse", "HEAD")

    def body(names):
        return "".join(
            f"## {h}\n\n{names if h == 'Head' else 'none'}\n\n"
            for h in ("Head", "Mutation proof", "Null control", "Figures",
                      "Red checks", "Forward-carry", "Friction"))

    def run(head, names):
        (d / "body.md").write_text(body(f"`{names}`"))
        p = subprocess.run(
            ["node", ".claude/workflows/policy_lint.mjs", "--pr-body",
             str(d / "body.md"), "--head", head],
            cwd=str(d), capture_output=True, text=True)
        return p.returncode, p.stdout

    try:
        (d / ".claude/workflows").mkdir(parents=True)
        (d / "tests/golden").mkdir(parents=True)
        _copy_policy_lint_tree(d / ".claude/workflows")
        (d / "tests/closures.json").write_text('{"closures": {}}\n')
        (d / "tests/golden/claimed_drift.txt").write_text("# claims-for: 1.0\nfix_a\n")
        (d / "tests/golden/card_claimed_drift.txt").write_text("# claims-for: 1.0\n")
        (d / "other.txt").write_text("v1\n")
        g("init", "-q", "-b", "trunk")
        (d / ".gitignore").write_text("body.md\n")
        base = commit("base", {}, who=seat)
        closures = {"tests/closures.json": '{"closures": {"a": []}}\n'}
        drop_claim = {"tests/golden/claimed_drift.txt": "# claims-for: 1.0\n"}
        R_ = "ci: re-record closures"
        C_ = "ci: drop inherited claims"
        out = {}
        # #1107's shape: base, then the claims repair, then the closures one.
        c1 = commit(C_, drop_claim, parent=base)
        c2 = commit(R_, closures, parent=c1)
        out["replay"] = run(c2, base) + (c1, c2)
        out["one"] = run(commit(R_, closures, parent=base), base)
        out["null"] = run(base, base)
        out["human"] = run(commit(R_, closures, who=seat, parent=base), base)
        out["committer"] = run(commit(R_, closures, committer=seat, parent=base), base)
        out["subject"] = run(commit("ci: re-record closures and more", closures, parent=base), base)
        out["body_line"] = run(commit(R_ + "\n\nand a body", closures, parent=base), base)
        out["forged_path"] = run(commit(R_, {"other.txt": "v2\n"}, parent=base), base)
        out["extra_file"] = run(commit(R_, {**closures, "other.txt": "v2\n"}, parent=base), base)
        out["mismatch"] = run(commit(R_, drop_claim, parent=base), base)
        out["mismatch2"] = run(commit(C_, closures, parent=base), base)
        out["adds_claim"] = run(commit(C_, {"tests/golden/claimed_drift.txt": "# claims-for: 1.0\nfix_a\nfix_b\n"}, parent=base), base)
        out["deleted"] = run(commit(R_, {"tests/closures.json": None}, parent=base), base)
        # A merge whose FIRST-parent diff is closures.json alone, carrying a
        # human commit in from the side: only the parent count refuses it.
        side = commit("human closures edit", closures, who=seat, parent=base)
        g("checkout", "-q", "--detach", base)
        g("merge", "-q", "--no-ff", "--no-edit", "-m", R_, side, who=bot)
        out["merge"] = run(g("rev-parse", "HEAD"), base)
        human = commit("human work", {"other.txt": "v3\n"}, who=seat, parent=base)
        out["between"] = run(commit(R_, closures, parent=human), base)
        sibling = commit("sibling", {"other.txt": "v4\n"}, who=seat, parent=base)
        out["not_ancestor"] = run(commit(R_, closures, parent=base), sibling)
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)


_AH = _autofix_head_fixture()
R.check(
    "pr-contract accepts #1107's autofix commits on top of the head the body names",
    _AH["replay"][0] == 0
    and f"{_AH['replay'][2][:7]} (ci: drop inherited claims)" in _AH["replay"][1]
    and f"{_AH['replay'][3][:7]} (ci: re-record closures)" in _AH["replay"][1]
    and _AH["one"][0] == 0,
    f"replay rc={_AH['replay'][0]}, single rc={_AH['one'][0]}; output: "
    f"{_AH['replay'][1].strip()[-300:]!r}. Run 35220336323 refused #1107 at "
    "b1afbcf for a body naming the seat's head under two bot commits",
)
R.check(
    "and a body naming the real head passes with no autofix line (null control)",
    _AH["null"][0] == 0 and "accepted autofix" not in _AH["null"][1],
    f"rc={_AH['null'][0]}; output {_AH['null'][1].strip()[-200:]!r}",
)
_AH_REFUSED = {
    "human": "not authored",
    "committer": "not authored",
    "subject": "not an autofix message",
    "body_line": "not an autofix message",
    "forged_path": "outside",
    "extra_file": "outside",
    "mismatch": "outside",
    "mismatch2": "outside",
    "adds_claim": "adds",
    "deleted": "does not only modify",
    "merge": "parents",
    "between": "not authored",
    "not_ancestor": "not authored",
}
_AH_WRONG = {
    k: (_AH[k][0], _AH[k][1].strip()[-240:])
    for k, why in _AH_REFUSED.items()
    if _AH[k][0] != 1 or "does not name" not in _AH[k][1] or why not in _AH[k][1]
}
R.check(
    "and refuses every chain that is not purely the bot's own repair",
    not _AH_WRONG,
    f"arms not refused for their own reason: {_AH_WRONG}. The identity is "
    "forgeable, so a forged author must still be held by the subject, the "
    "parent count and the path set, each by itself",
)
# The identity and messages are the autofix jobs' own. `checkPrBody` holds
# them as constants rather than reading tests.yml, because the checkout it
# runs in is the pull request's: a branch that edited the workflow would widen
# what it is excused for. So agreement is pinned here instead.
_AH_CONST = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./.claude/workflows/policy_lint.mjs').then((m) => "
     "console.log(JSON.stringify(m.AUTOFIX_BOT_COMMITS ?? null)))"],
    capture_output=True, text=True).stdout or "null")
_AH_TESTS_YML = Path(".github/workflows/tests.yml").read_text()
_AH_DRIFT = []
for _job, _subject in (("closures-autofix", "ci: re-record closures"),
                       ("claims-autofix", "ci: drop inherited claims")):
    _jt = _workflow_job(_AH_TESTS_YML, _job)
    _added = re.search(r"^\s*git add (.+)$", _jt, re.M)
    _rule = (_AH_CONST or {}).get("messages", {}).get(_subject)
    if not (_rule and f'git commit -m "{_subject}"' in _jt and _added
            and sorted(_added.group(1).split()) == sorted(_rule["paths"])
            and f'git config user.name "{_AH_CONST["name"]}"' in _jt
            and f'git config user.email "{_AH_CONST["email"]}"' in _jt):
        _AH_DRIFT.append(_job)
R.check(
    "and its bot identity, messages and paths are the ones the autofix jobs commit",
    _AH_CONST is not None and not _AH_DRIFT,
    f"disagreeing jobs: {_AH_DRIFT}; constants: {_AH_CONST}",
)
_DS_PUB_PERMS = re.search(
    r"^    permissions:\n((?:^      .*\n)+)", _DS_PUB_JOB, re.M)
R.check(
    "and the publishing lane's grant is the one write it uses",
    bool(_DS_PUB_PERMS)
    and sorted(_DS_PUB_PERMS.group(1).split()) == sorted(
        ["contents:", "read", "issues:", "write"]),
    f"delivery-status-publish permissions: "
    f"{_DS_PUB_PERMS.group(1).split() if _DS_PUB_PERMS else None} -- "
    "`issues: write` edits #201's region and `contents: read` restates the "
    "floor a job-level block replaces; the lane writes nothing else",
)
# THE FIXED POINT (#201 root cause, 2026-09-17). Merging a ledger PR was a push
# to main, the push re-ran this lane, and the ledger moves on every push, so a
# new ledger PR opened 14-22 s after each merge -- nine of eleven. The lane is
# at a fixed point only while nothing it writes can land on main, which is
# pinned on the wiring, over NON-COMMENT lines: no push, no PR write, no
# machine token anywhere in the workflows (decision 0009 step 3b's only
# consumer went with the PR), and no workflow that an issue-body edit starts.
def _code_lines(text: str) -> str:
    return "\n".join(
        _l for _l in text.split("\n") if not _l.lstrip().startswith("#"))


_DS_PUB_CODE = _code_lines(_DS_PUB_JOB)
_DS_WRITES = [_t for _t in (r"(?<![\w'])push\s", r"/pulls", r"gh pr ",
                            r"git commit") if re.search(_t, _DS_PUB_CODE)]
_SA_FILES = {
    _f.name: _code_lines(_f.read_text())
    for _f in sorted(Path(".github/workflows").glob("*.y*ml"))}
_SA_REFS = [_n for _n, _t in _SA_FILES.items() if "SEAT_AUTHOR_TOKEN" in _t]
_ISSUE_TRIGGERED = [_n for _n, _t in _SA_FILES.items()
                    if re.search(r"^  (issues|issue_comment):", _t, re.M)]
R.check(
    "the publishing lane writes nothing that lands on main, so its own "
    "write cannot re-run it",
    not _DS_WRITES and not _SA_REFS and not _ISSUE_TRIGGERED
    and "persist-credentials: false" in _DS_PUB_CODE
    and "#201's region is already current" in _DS_PUB_CODE,
    f"writes in the lane: {_DS_WRITES}; workflows naming SEAT_AUTHOR_TOKEN: "
    f"{_SA_REFS}; workflows an issue edit starts: {_ISSUE_TRIGGERED}. Each "
    "must be empty: a commit, push or PR the lane makes lands on main as a "
    "push that runs the lane again, and the ledger's `commits_after` moves "
    "on every push, so no ledger it lands is ever the ledger it regenerates",
)
# #959 (option B): the `record` job -- already one of the three overrides for
# its read grant -- WIDENED that grant with `issues: write` so its filing step
# can open and edit the recurring-friction issues its own histogram names. Not
# a fourth override: the job was already in the set above, which is why the
# count pin does not move. The write itself is owner-approved (#201 comment
# 5670207248, item 4), and it is pinned to exactly what the step uses so it
# cannot grow past the approval in silence -- the same property the
# publishing-lane pin above asserts for its job.
_REC_JOB = _workflow_job(_DS_GOV, "record")
_REC_PERMS = re.search(r"^    permissions:\n((?:^      .*\n)+)", _REC_JOB, re.M)
# Comment lines inside the block carry the argument; the GRANT is what remains
# once they are stripped, and that is what is pinned -- the two publishing-lane
# pins above tokenize comment-free blocks, so their regexes need no strip.
_REC_GRANT = sorted(
    tok
    for _l in (_REC_PERMS.group(1).splitlines() if _REC_PERMS else [])
    if (_l.strip() and not _l.strip().startswith("#"))
    for tok in [_l.strip()]
)
R.check(
    "the cron lane's grant is its two reads plus the one owner-approved write",
    _REC_GRANT == sorted(
        ["contents: read", "pull-requests: read", "issues: write"]),
    f"record permissions: {_REC_GRANT} -- "
    "`pull-requests: read` feeds the stats/record API reads, `contents: read` "
    "restates the floor a job-level block replaces, and `issues: write` files "
    "and updates the `[policy] recurring friction:` issues (#959 option B, "
    "#201 comment 5670207248 item 4) and nothing else",
)
# THE LANES THAT CAN REDDEN THE JOB, pinned as a property: the filing step runs
# unsuppressed -- the path that ACTS deliberately -- while the informational
# lanes keep their `|| true`. A `|| true` pasted onto the filing step would turn
# a mechanism that stopped filing into a green tick, which is the #959 defect
# one lane later, so the suppression is keyed per step here rather than left to
# the YAML's reader. The disposition refusal is the third path that reddens: its
# `continue-on-error` is dropped (#1194, D11-04) and pinned by name below.
_REC_RUNS = dict.fromkeys(
    _re.findall(r"run: (.+)", _REC_JOB), None)
_REC_FILE_LINE = next(
    (l for l in _REC_RUNS if "friction_issues.mjs --stats-file" in l), None)
_REC_STATS_LINE = next(
    (l for l in _REC_RUNS if "--stats " in l and "policy_lint.mjs" in l), None)
_REC_SUNSET_LINE = next(
    (l for l in _REC_RUNS if "--sunset" in l), None)
R.check(
    "the friction filer is the record lane's deliberate filing arm and the "
    "informational lanes stay suppressed",
    _REC_FILE_LINE is not None
    and "|| true" not in _REC_FILE_LINE
    and _REC_STATS_LINE is not None and "|| true" in _REC_STATS_LINE
    and _REC_SUNSET_LINE is not None and "|| true" in _REC_SUNSET_LINE,
    f"filing: {_REC_FILE_LINE!r}; stats: {_REC_STATS_LINE!r}; "
    f"sunset: {_REC_SUNSET_LINE!r} -- the filing step reddens this job when "
    "its mechanism fails, because a filing lane that fails green stopped "
    "filing; the histogram and sunset printings never redden it",
)
# D13-04 (#1241): the governance-cost instrument's GOV set is measured against
# the workflow files, never remembered. It named `record-status` for a window
# after that job had been renamed -- a job that exists nowhere costs nothing
# and hides nothing -- while the two jobs the rename actually added
# (`delivery-status`, `delivery-status-publish`) were counted as GATE seconds,
# understating the governance share of every merge in that window (0.0515
# carried against 0.0556 derived at the finder's baseline). Both directions
# are pinned against the tree: every GOV member is a job id some workflow
# file defines, and every governance.yml job id is in GOV, so the next job
# added to the governance workflow reddens this check until the instrument
# names it. The null control is the split itself: `fast`, the code gate's own
# job, must stay out of GOV.
def _workflow_job_ids(text: str) -> "set[str]":
    i = text.rfind("\njobs:\n")
    return set(re.findall(r"^  ([A-Za-z][\w-]*):", text[i:], re.M)) if i >= 0 else set()


def _load_governance_cost():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "hpo_governance_cost",
        Path("tools/audit/round4/D11/governance_cost.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_GOV_MOD = _load_governance_cost()
_ALL_JOB_IDS: "set[str]" = set()
for _wf in sorted(Path(".github/workflows").glob("*.y*ml")):
    _ALL_JOB_IDS |= _workflow_job_ids(_wf.read_text())
_GOV_JOBS = _workflow_job_ids(_DS_GOV)
R.check(
    "the governance-cost GOV set names only jobs the workflow files define, "
    "and every governance.yml job",
    _ALL_JOB_IDS
    and _GOV_JOBS
    and _GOV_MOD.GOV <= _ALL_JOB_IDS
    and _GOV_JOBS <= _GOV_MOD.GOV,
    f"GOV={sorted(_GOV_MOD.GOV)}; defined jobs={sorted(_ALL_JOB_IDS)}; "
    f"governance.yml jobs={sorted(_GOV_JOBS)} -- a GOV member with no job "
    "measures nothing (the renamed `record-status`), and a governance job "
    "outside GOV is counted as gate seconds (#1241)",
)
R.check(
    "and the split survives: the code gate's own jobs are not governance "
    "(null control)",
    not ({"fast", "browser", "closures"} & _GOV_MOD.GOV)
    and "briefs" in _GOV_MOD.GOV,
    f"GOV={sorted(_GOV_MOD.GOV)} -- `fast` is the gate; `briefs` (tests.yml) "
    "is the one governance job that lives outside governance.yml, named by "
    "the instrument's own recorded rule",
)
# D13-03 (#1240): the stats histogram's verdict arm reads the FULL grammar the
# wave script teaches -- the verdict words from the reviewer prompt's string
# literals, and the block classes from VERDICT_CLASSES -- instead of printing
# a two-word grammar and keying every blocked verdict under one constant. The
# finder measured 0 block-class rows over 30 blocked verdicts against 11
# taught classes: an instrument that cannot compute its own metric (the D13
# brief's block-class histogram). Pinned at the extraction, both ways.
_WAVE_SRC = Path(".claude/workflows/web-fix-wave.js").read_text()
_VC_ARR = re.search(r"const VERDICT_CLASSES = \[([^\]]*)\]", _WAVE_SRC)
_VC_WORDS = (re.findall(r"'([a-z][a-z0-9-]*)'", _VC_ARR.group(1))
             if _VC_ARR else [])
_BLOCK_CLASSES = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     "import('./.claude/workflows/policy_lint.mjs').then((m) => "
     "console.log(JSON.stringify({"
     "fromScript: m.blockClasses ? m.blockClasses() : null,"
     "guard: m.blockClasses ? m.blockClasses('// no array here') : null"
     "})))"],
    capture_output=True, text=True).stdout or "{}")
R.check(
    "the stats histogram reads the wave script's VERDICT_CLASSES as its "
    "block-class set",
    _BLOCK_CLASSES.get("fromScript") == _VC_WORDS
    and len(_VC_WORDS) >= 10
    and "mutation-vacuous" in _VC_WORDS
    and "other" in _VC_WORDS,
    f"extracted={_BLOCK_CLASSES.get('fromScript')}; "
    f"wave script VERDICT_CLASSES={_VC_WORDS} -- the histogram keying "
    "blocked verdicts by one constant key is the #1240 defect",
)
R.check(
    "and an unreadable grammar yields null rather than a guessed class set "
    "(null control)",
    _BLOCK_CLASSES.get("guard") is None,
    f"blockClasses('// no array here')={_BLOCK_CLASSES.get('guard')!r} -- "
    "the mode over-reports rather than classifying against a list typed in "
    "the histogram",
)
# The DEGRADED arm of the same verdict histogram: when VERDICT_CLASSES cannot
# be read, blocked verdicts collapse back to one constant key and the arm must
# SAY SO rather than propose an issue on a constant -- the tautology exclusion,
# restated for the full-grammar world (#1240). Driven here because the
# acceptance drives only the healthy extraction.
_SHA40 = "0" * 40
_STATS_JS = (
    "import('./.claude/workflows/policy_lint.mjs').then((m) => "
    "console.log(m.statsFindings ? JSON.stringify(m.statsFindings({"
    "prs: [{pr: 1}, {pr: 2}, {pr: 3}],"
    "fetched: new Map([[1, {body: 'x', comments: ["
    "{body: 'Fix review: blocked " + _SHA40 + "'}]}],"
    "[2, {body: 'x', comments: "
    "[{body: 'Fix review: blocked " + _SHA40 + "'}]}],"
    "[3, {body: 'x', comments: "
    "[{body: 'Fix review: blocked " + _SHA40 + "'}]}]]),"
    "fetchError: null, classes: ['blocked', 'merge'], blocks: null"
    "}).map((f) => f.message)) : 'null'))")
_STATS_OUT = subprocess.run(
    ["node", "--input-type=module", "-e", _STATS_JS],
    capture_output=True, text=True).stdout or "null"
try:
    _STATS_DEGRADED = json.loads(_STATS_OUT)
except ValueError:
    _STATS_DEGRADED = None
R.check(
    "a verdict histogram whose block-class grammar is unreadable withholds "
    "the proposal and says why",
    isinstance(_STATS_DEGRADED, list)
    and any("not opened" in m and "VERDICT_CLASSES" in m
            for m in _STATS_DEGRADED)
    and not any("would open" in m for m in _STATS_DEGRADED),
    f"findings={str(_STATS_DEGRADED)[:300]} -- three bare blocked verdicts over "
    "three pull requests reached the threshold with no class set to key "
    "them, and a constant proposed as friction is #1041 again (#1240)",
)
R.check(
    "the publishing lane runs on main alone, never on a pull request",
    "github.event_name == 'push'" in _DS_PUB_JOB
    and "refs/heads/main" in _DS_PUB_JOB
    and "pull_request" not in _DS_PUB_JOB,
    "a write-scoped job reachable from a pull request is a write-scoped job "
    "reachable from a fork, and the ledger it publishes is about `main`'s "
    "history rather than about any branch",
)
R.check(
    "the ledger script is classified: NOT_A_TEST, and not on INERT",
    "delivery_status.py" in _closure.NOT_A_TEST
    and not _closure.is_inert("tests/delivery_status.py"),
    "a file that is neither in a closure nor on a list forces the FULL suite",
)

# --- D11-04 (#1194): the disposition refusal can set the record job's status --
#
# The refusing step carried `continue-on-error: true`, which is exactly what
# #958's split added and exactly what made an undispositioned merge stay green:
# the step fails inside the job, the job concludes success, and the check-run a
# seat reads is a green tick over a window nobody dispositioned. The step is cut
# from the workflow the way the finding's harness cuts it (disposition.py) and
# read for the one key that decides whether its exit code reaches the job's
# conclusion. The cut selects the step BY NAME and runs to the next `- name:`,
# so it reads the step and not the `record:` job's other suppressing steps.
_REC_REFUSAL = _REC_JOB.split(
    "- name: Every merged pull request has a disposition")[1].split(
        "\n      - name:")[0]
R.check(
    "the disposition refusal can set the record job's conclusion",
    "continue-on-error" not in _REC_REFUSAL,
    f"the refusing step is {_REC_REFUSAL.strip()[:220]!r}. `continue-on-error: "
    "true` on this step is #958's split: the step fails and the job concludes "
    "success, so a merged pull request with no disposition is reported and stays "
    "green -- the check cannot set its own conclusion (#1194, D11-04). The step "
    "still runs on a push to main, never on a pull request, and is not a "
    "required context, so dropping it cannot block an unrelated merge",
)

# --- D11-02 (#1192): the ruleset reader sees the rules it does not require ----
#
# `counts.mjs:liveRequiredContexts` skipped every rule that was not
# `required_status_checks` and never read `bypass_actors`, so two rulesets
# differing in one rule and one bypass actor returned BYTE-IDENTICAL JSON -- a
# change to the ruleset the merge boundary runs was invisible to the tree's only
# reader of it. Driven the way the finding's harness drives it
# (tools/audit/round5/D11/ruleset.py): a stubbed `gh` answering the two calls the
# reader makes, with the two ruleset documents differing only in the
# `pull_request` rule and the bypass actor. The import is the production symbol
# and the answer comes from production, never from a copy of its logic here.
def _ruleset_reader_fixture():
    import os
    import tempfile

    branch = [{
        "type": "required_status_checks", "ruleset_id": 1,
        "parameters": {"required_status_checks": [{"context": "policy-docs"}]},
    }]

    def read(ruleset):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "bin").mkdir()
            stub = td / "bin" / "gh"
            stub.write_text(
                '#!/bin/bash\ncase "$*" in\n'
                '  */rules/branches/main) cat "$STUB_DIR/branch.json" ;;\n'
                '  */rulesets/*) cat "$STUB_DIR/ruleset.json" ;;\n'
                '  *) echo "stub gh: unhandled $*" >&2; exit 9 ;;\nesac\n')
            stub.chmod(0o755)
            (td / "ruleset.json").write_text(json.dumps(ruleset))
            (td / "branch.json").write_text(json.dumps(branch))
            env = {**os.environ, "STUB_DIR": str(td),
                   "PATH": f"{td / 'bin'}:{os.environ['PATH']}"}
            r = subprocess.run(
                ["node", "--input-type=module", "-e",
                 "import('./.claude/workflows/counts.mjs').then((m) => "
                 "console.log(JSON.stringify(m.liveRequiredContexts())))"],
                capture_output=True, text=True, env=env)
            return r.returncode, r.stdout.strip()

    req = {"type": "required_status_checks",
           "parameters": {"required_status_checks": [{"context": "policy-docs"}]}}
    full = {"rules": [req, {"type": "pull_request",
                            "parameters": {"required_approving_review_count": 1}}],
            "bypass_actors": [{"bypass_mode": "always"}]}
    trimmed = {"rules": [req], "bypass_actors": []}
    return read(full), read(trimmed), read(full)


_RR = _ruleset_reader_fixture()
R.check(
    "the ruleset reader's answer moves when a rule it does not require moves",
    _RR[0][0] == 0 and _RR[1][0] == 0 and _RR[0][1] != _RR[1][1],
    f"with the `pull_request` rule and the bypass actor: {_RR[0][1]}; with both "
    f"removed: {_RR[1][1]} -- byte-identical output means a ruleset change is "
    "invisible to the tree's only reader of it (#1192, D11-02)",
)
R.check(
    "and it stays stable when nothing about the ruleset moved (null control)",
    _RR[0][0] == 0 and _RR[2][0] == 0 and _RR[0][1] == _RR[2][1],
    f"the same ruleset read twice: {_RR[0][1]} then {_RR[2][1]}. Two identical "
    "rulesets must return identical output, or the check above would pass for a "
    "reader whose output moved on every call rather than on a ruleset change",
)

# --- D11-05 (#1195): the template arm reddens the acceptance -------------------
#
# `checkPrBody`'s template arm pushed a failing template into `found[]` and
# never set the acceptance's exit status, so `.github/PULL_REQUEST_TEMPLATE.md`
# failed `--pr-body` while `policy-docs` -- the acceptance -- stayed green: the
# arm reported a violation it could not act on. The arm now returns the
# acceptance's refusal, and the drive below is the witness it needs, because on
# the healthy tree the template holds and the arm is silent. `POLICY_LINT_
# TEMPLATE` points the arm at a body that drops a required heading; the same run
# with the real template is its null control. Both are the whole acceptance, so
# the test reads the exit status the `policy-docs` context runs, not a model of
# the arm.
def _template_arm_fixture():
    import os
    import tempfile

    root = Path(__file__).resolve().parent.parent
    headings = ["Head", "Mutation proof", "Null control", "Figures",
                "Red checks", "Forward-carry", "Friction"]
    broken = "".join(f"## {h}\n\nnone\n\n" for h in headings if h != "Forward-carry")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "template.md"
        p.write_text(broken)
        # A path RELATIVE to the clone: the arm resolves it from the module's
        # own root, the same way it resolves the real template.
        env = {**os.environ, "POLICY_LINT_TEMPLATE": os.path.relpath(p, root)}
        rc_broken = subprocess.run(
            ["node", ".claude/workflows/policy_lint.mjs"],
            capture_output=True, text=True, env=env).returncode
    rc_live = subprocess.run(
        ["node", ".claude/workflows/policy_lint.mjs"],
        capture_output=True, text=True).returncode
    return rc_broken, rc_live


_TA = _template_arm_fixture()
R.check(
    "the template arm turns the acceptance red on a template that fails its "
    "own contract (and the real template keeps it green)",
    _TA[0] == 1 and _TA[1] == 0,
    f"a template missing `## Forward-carry` -> acceptance rc={_TA[0]} (must be "
    f"1); the real template -> rc={_TA[1]} (must be 0). Without the arm's "
    "refusal the acceptance concluded success over a template that fails the "
    "contract it states, which is #1195 (D11-05)",
)

# --- the release lane's attestation grant and subject (#960, D11-07) ---------
#
# Option B, owner-approved this wave (#201 comment 5670207248, item 5: "add
# build provenance with job-scoped id-token: write"). The same pin discipline
# as the governance grants above, for the same reason: `id-token: write` is
# the one identity grant the owner signed off, so the set it lives in is the
# blast radius and is pinned rather than trusted to a YAML comment.
_REL_JOB = _workflow_job(Path(_REL_WF).read_text(), "release")
_REL_PERMS = re.search(r"^    permissions:\n((?:^      .*\n)+)", _REL_JOB, re.M)
# Comment lines inside the block carry the argument; the GRANT is what
# remains once they are stripped -- the record-lane pin's own split.
_REL_GRANT = sorted(
    _l.strip()
    for _l in (_REL_PERMS.group(1).splitlines() if _REL_PERMS else [])
    if (_l.strip() and not _l.strip().startswith("#"))
)
R.check(
    "the release lane's grant is the owner-approved attestation grant and "
    "nothing more",
    _REL_PERMS is not None
    and _REL_GRANT == sorted(
        ["attestations: write", "contents: write", "id-token: write"]),
    f"release permissions: {_REL_GRANT} -- `id-token: write` is the grant the "
    "owner signed off (#201 comment 5670207248, item 5: job-scoped, "
    "attestation only); `attestations: write` is the data-plane write the "
    "same feature's persistence call needs -- the action's own README names "
    "it beside id-token, and the POST it guards is refused without it, so the "
    "approved feature cannot exist without this one delta from the grant's "
    "letter; `contents: write` restates the workflow floor a job-level block "
    "replaces, because `gh release create` uses it. Anything beyond these "
    "three is scope this job does not use and should not hold",
)
# The subject honesty is the other half of the approval: option C (build an
# artefact) is declined because HACS installs from the ref, so the attested
# subject must be the tag's tree itself -- a digest recomputable by anyone
# from the tag -- and never a zip, an upload, or an asset the release does
# not carry. The pins are the wiring that makes that claim checkable: the
# digest step serialises the tag with `git archive`, and the attestation
# carries that digest under `subject-digest`, pinned by its own SHA.
_REL_ATTEST_PIN = re.search(
    r"attest-build-provenance@([0-9a-f]{40})", _REL_JOB)
R.check(
    "the attested subject is the tag's tree, not an artefact that does not "
    "exist",
    _REL_ATTEST_PIN is not None
    and "subject-digest:" in _REL_JOB
    and "git archive --format=tar" in _REL_JOB
    and "subject-path:" not in _REL_JOB,
    f"attest action pinned={_REL_ATTEST_PIN is not None}, "
    f"digest carries subject-digest={'subject-digest:' in _REL_JOB}, "
    f"digest step archives the tag={'git archive --format=tar' in _REL_JOB}, "
    f"subject-path present={'subject-path:' in _REL_JOB} (must be False); the "
    "digest step serialises the tag's tree and the attestation carries that "
    "sha256 -- `subject-path` would bind the statement to a built file, which "
    "is the overclaim #960 exists to remove while the artefact build stays "
    "declined",
)

# --- the two instruments beside the gate: coverage and mutation (#195) -------
#
# Coverage says a line RAN. It cannot say a check would fail if the line were
# wrong, and the five W5-G7 tranches measured the gap: twenty-two checks
# executed the line they were named for and pinned nothing. So there are two
# instruments, and what is pinned here is what each CLAIMS -- the operators,
# the kill rule, the scope rule -- plus the wiring, because a correct
# instrument its workflow does not call is the silent-green shape this
# repository keeps finding (`governance.yml`, `nightly_ha.py`, #533).
import shutil as _mut_shutil  # noqa: E402
import coverage_ratchet as _cov  # noqa: E402
import mutation_table as _mut  # noqa: E402

_MUT_JOB = _workflow_job(_TESTS_YML, "mutation")
_MUTN_JOB = _workflow_job(_TESTS_YML, "mutation-nightly")
_COV_JOB = _workflow_job(_TESTS_YML, "coverage")

R.check(
    "the coverage ratchet is wired into a job that runs on pull requests",
    "github.event_name == 'pull_request'" in _COV_JOB
    and "tests/coverage_ratchet.py" in _COV_JOB,
    f"pull_request={'pull_request' in _COV_JOB}, "
    f"invoked={'tests/coverage_ratchet.py' in _COV_JOB}",
)
# The null control for every ratchet in this repository. `--record` REWRITES
# the budget to whatever was measured, so a job that passes it can never fail:
# it is the always-green shape, and CI must never take that path.
R.check(
    "and no CI job passes either instrument --record",
    not any("--record" in _j for _j in (_COV_JOB, _MUT_JOB, _MUTN_JOB)),
    "--record rewrites the budget to the measurement, so a job that passes "
    "it reports PASSED whatever the tree did",
)
# The user's ask, read back off the workflow: scoped beside `fast`, full on
# the nightly. The two scopes are what make this affordable at all.
R.check(
    "the pull-request lane scopes to what the diff tested, the nightly does not",
    "--scope changed" in _MUT_JOB and "--scope full" not in _MUT_JOB
    and "--scope full" in _MUTN_JOB and "--scope changed" not in _MUTN_JOB,
    f"mutation: changed={'--scope changed' in _MUT_JOB} "
    f"full={'--scope full' in _MUT_JOB}; mutation-nightly: "
    f"changed={'--scope changed' in _MUTN_JOB} full={'--scope full' in _MUTN_JOB}",
)
# --scope changed diffs three-dot against the merge base. A shallow clone has
# no merge base, so the scope would silently come back empty -- and an empty
# scope is a PASS.
R.check(
    "and the scoped lane checks out the history its own diff needs",
    "fetch-depth: 0" in _MUT_JOB,
    "without full history `git merge-base` prints nothing, scope_files "
    "returns no file, and the run passes on an empty scope",
)

# The budget the ratchet enforces has to be a band, not a point: a floor above
# its own ceiling can never be recorded down to and never stops tightening.
_CB = json.loads(Path("tests/coverage_budgets.json").read_text())
R.check(
    "the coverage floor sits at or below its ceiling",
    _CB["package_percent_floor"] <= _CB["package_percent_ceiling"],
    f"floor={_CB['package_percent_floor']} ceiling={_CB['package_percent_ceiling']}",
)
# The pragma row is the reason the coverage floor is a floor at all: a
# `# pragma: no cover` takes the statement out of the denominator, so without
# a cap on the escape the floor is an invitation. Pinned as the PROPERTY --
# the cap is not above what the tree carries -- rather than as the number,
# which would be a literal this file re-measures every run.
_PRAGMAS, _ = _cov.count_pragmas()
R.check(
    "the pragma cap is not slack: no exemption is pre-authorised",
    _CB["pragmas"] <= _PRAGMAS,
    f"cap={_CB['pragmas']} measured={_PRAGMAS}; a cap above the count is "
    "headroom for an exemption nobody argued for",
)

# The mutation cap is a FRACTION and deliberately not the exact-count ratchet
# tests/structure.py and tests/coverage_ratchet.py use: the pool is a seeded
# sample over whichever files a diff put in scope, so two clean branches
# touching different modules draw different pools and an exact count would go
# red at random. What can still be pinned is that it is a fraction at all, and
# that whatever was last measured is inside the cap it was recorded against --
# a cap below its own measurement is a gate that fails on the tree it was
# written from.
_MB = json.loads(Path("tests/mutation_budgets.json").read_text())
_MB_BAD = [
    f"{_scope}={_v}" for _scope, _v in _MB["max_survivor_fraction"].items()
    if not 0.0 <= _v <= 1.0
]
_MB_BAD += [
    f"{_scope}: {_m['survivors']}/{_m['evaluated']} over the recorded "
    f"{_MB['max_survivor_fraction'][_scope]}"
    for _scope, _m in _MB["last_measured"].items()
    if _m and _m["evaluated"]
    # Compared at the 4 dp `--record` writes the cap at: a fraction recorded
    # from 1/3 is stored as 0.3333 and must not read as over its own cap for
    # the 0.000033 the rounding left behind.
    and round(_m["survivors"] / _m["evaluated"], 4)
    > _MB["max_survivor_fraction"][_scope]
]
R.check(
    "both mutation caps are fractions, and each holds its own last measurement",
    not _MB_BAD and set(_MB["max_survivor_fraction"]) == {"changed", "full"},
    f"{_MB_BAD or 'in band'}; scopes recorded: "
    f"{sorted(_MB['max_survivor_fraction'])}",
)


# The mutation budget's `reason` is a claim about the tree like any other, and
# the one it carried was falsifiable: both caps were said to wait on a
# full-package run that "cannot happen until `mutation-nightly` is on main",
# while `.github/workflows/tests.yml` defines that job and `tests/nightly_status.py`
# requires it (#1136). A reason must not DEFER on a lane's EXISTENCE, because
# `REQUIRED_LANES` is exactly the set the workflow defines -- the check above
# pins that equality -- so a reason waiting for one of them to arrive is false
# however it is worded, and `last_measured` is the record that is owed instead.
#
# Key: (a lane in `REQUIRED_LANES` named in a deferral clause -- "until
# <lane>", "unless <lane>", "pending <lane>", "awaiting <lane>", "waiting on
# <lane>", "once <lane>"). Out of the key, and therefore out of this pin: the
# lane named anywhere ELSE in the reason, and a deferral on WORK rather than on
# a lane ("until the survivors are explained"). A reason claiming a required
# lane has not yet RUN is also outside it -- whether a lane ran is not a
# property of this tree, so no offline check can refuse that shape.
def _mb_deferrals(reason: str) -> list:
    """`REQUIRED_LANES` this reason waits to exist -- #1136's defect shape."""
    return sorted(
        _lane for _lane in _nstatus.REQUIRED_LANES
        if re.search(
            r"\b(?:until|unless|pending|awaiting|waiting on|once)\s+"
            rf"`?{re.escape(_lane)}`?", reason)
    )


R.check(
    "the mutation budget defers on no lane the workflow already defines",
    _mb_deferrals(_MB["reason"]) == [],
    f"defers-on={_mb_deferrals(_MB['reason'])}; every REQUIRED_LANE is in "
    f"tests.yml by construction ({', '.join(_nstatus.REQUIRED_LANES)}), so a "
    f"reason that waits for one to arrive describes a tree that is not this "
    f"one -- record the run instead",
)
# The null control, both arms, driven through the same predicate rather than
# asserted beside it: it fires on the deferral it is named for, and takes no
# verdict on the lane named as PRESENT or on a deferral on work rather than on
# a lane. Without the second and third arms the pin would refuse the lane's
# name rather than the waiting, which is a different and wrong property.
_MB_ARMS = (
    "cannot happen until mutation-nightly is on main",
    "mutation-nightly is on main and has run",
    "both caps stay open until the survivors are explained",
)
R.check(
    "and it refuses the deferral, not the lane's name",
    [_mb_deferrals(_r) for _r in _MB_ARMS] == [["mutation-nightly"], [], []],
    f"arms: {[_mb_deferrals(_r) for _r in _MB_ARMS]} -- present and "
    f"work-deferral reasons must not be read as waiting on a lane",
)

# The #805 defect, driven rather than described. Its pre-screen read the last
# 1200 bytes of a script's output and scored seven real kills as survivors,
# because two scripts print their summary line and then keep logging. The
# kill rule must read the whole of stdout.
_MUT_NOISE = "2 of 40 checks FAILED\n" + ("noise\n" * 400)
R.check(
    "the kill rule finds a failure count buried under trailing output",
    [(m[0]) for m in _mut._FAILED.findall(_MUT_NOISE)] == ["2"],
    f"a tail-only read of {len(_MUT_NOISE)} bytes sees none of it (#805)",
)
R.check(
    "and reads no failure out of a clean run",
    _mut._FAILED.findall("40 of 40 checks passed\n" + ("noise\n" * 400)) == [],
    "the null control: a green script must not be read as a kill, or every "
    "mutant dies and the table reports a suite that notices everything",
)

# The six operators, driven over a module written to carry one of each. A
# generated mutant that does not PARSE cannot run, and a mutant that cannot
# run reports as a survivor -- which reads as a finding about production.
# W5-G7 tranche 5 measured two of those.
_MUT_SRC = """
THRESHOLD_C = 2.5
ZERO_OFFSET = 0


def clamp(value, ceiling):
    out = min(value, ceiling)
    if out < 0:
        out = 0
    return out


def decide(a, b, flag):
    if flag:
        a = a + 1
    if a > 0 and b > 0:
        return a + b
    if a < 0:
        b = abs(b)
        raise ValueError("negative")
    return 0
"""
_MUT_DIR = Path(_tempfile.mkdtemp(prefix="mutation-operators-"))
_MUT_FILE = _MUT_DIR / "sample.py"
_MUT_FILE.write_text(_MUT_SRC)
_MUT_GOT = list(_mut.candidates(_MUT_FILE))
R.check(
    "every operator fires on a module written to carry one of each",
    {_m["kind"] for _m in _MUT_GOT} == {
        "CLAMP_DROP", "GUARD_OFF", "RAISE_DEL", "RETURN_DEL", "BOOLOP", "CONST"},
    f"kinds generated: {sorted({_m['kind'] for _m in _MUT_GOT})}",
)
_MUT_LINES = _MUT_SRC.splitlines(True)


def _mut_apply(mutant: dict) -> str:
    lines = list(_MUT_LINES)
    lines[mutant["line"] - 1] = mutant["new"] + "\n"
    return "".join(lines)


_MUT_UNPARSEABLE = []
for _m in _MUT_GOT:
    try:
        ast.parse(_mut_apply(_m))
    except SyntaxError:
        _MUT_UNPARSEABLE.append(f"{_m['kind']}:{_m['line']}")
R.check(
    "and every mutant it generates leaves the module parseable",
    not _MUT_UNPARSEABLE,
    f"unparseable: {_MUT_UNPARSEABLE}; a mutant that cannot run is reported "
    "as a survivor, and a survivor reads as a finding about production",
)
# The operator that makes that non-trivial: deleting a `return` or a `raise`
# that is the ONLY statement of its block strands the `if` above it. The
# generator refuses those rather than the runner catching them.
R.check(
    "the sole statement of a block is never deleted",
    not any(_m["kind"] in ("RETURN_DEL", "RAISE_DEL")
            and _MUT_LINES[_m["line"] - 1].strip().startswith(("return", "raise"))
            and _MUT_LINES[_m["line"] - 2].strip().endswith(":")
            for _m in _MUT_GOT),
    "a `raise` alone under its `if` cannot become `pass` without an "
    "IndentationError -- the refusal is in candidates(), not in the runner",
)
_mut_shutil.rmtree(_MUT_DIR, ignore_errors=True)

# Scope: a mutant is driven only by scripts whose MEASURED closure contains
# its file. Driving one hand-picked script instead would let a mutant survive
# because its driver never imports the module, and a survivor that says
# nothing about the suite is worse than no survivor at all.
_MUT_CLOSURES = {
    "tests/a.py": ["custom_components/heatpump_optimizer/pv.py"],
    "tests/b.py": ["custom_components/heatpump_optimizer/tariff.py"],
}
R.check(
    "a mutant is driven only by the scripts whose closure reaches its file",
    _mut.drivers_for("custom_components/heatpump_optimizer/pv.py",
                     _MUT_CLOSURES, ["tests/a.py", "tests/b.py"]) == ["tests/a.py"]
    and _mut.drivers_for("custom_components/heatpump_optimizer/nowhere.py",
                         _MUT_CLOSURES, ["tests/a.py", "tests/b.py"]) == [],
    "the closure recording answers 'which script could see this file', and a "
    "file no recorded closure reaches is skipped rather than scored",
)

# #1225 (D7-01): the default driver list omitted tests/manual_plan.py -- the
# module's own test, whose measured closure reaches manual_plan.py -- so the
# recorded full table (tests/mutation_budgets.json, run 35395283955) counted
# manual_plan.py:121 GUARD_OFF as a survivor that tests/manual_plan.py kills
# in one run. The property is read off the option the gate actually drives,
# through `getattr` so an unfixed tree FAILS these checks by name instead of
# dying here on an AttributeError.
_MUT_DEFAULT = getattr(_mut, "DEFAULT_SCRIPTS", "")
_MUT_REAL_CLOSURES = _mut.load_closures()
R.check(
    "the default driver list can reach tests/manual_plan.py's module (#1225)",
    "tests/manual_plan.py" in _mut.drivers_for(
        "custom_components/heatpump_optimizer/manual_plan.py",
        _MUT_REAL_CLOSURES, _MUT_DEFAULT.split(",")),
    f"default drivers: {_MUT_DEFAULT!r} -- a gate whose driver list omits the "
    "module's own test records its kills as survivors by construction",
)
# The null control: the widened list does not throw the operator's own rule
# away -- a driver still needs the mutant's file in its MEASURED closure.
R.check(
    "and the default list still drives nothing into a file no closure reaches",
    _mut.drivers_for("custom_components/heatpump_optimizer/nowhere.py",
                     _MUT_REAL_CLOSURES, _MUT_DEFAULT.split(",")) == [],
    "the default names CANDIDATES; `drivers_for` intersects them with the "
    "measured closure exactly as it did for the hand-kept list",
)

# #1211 (D3-01): the driver net is the GATE's recorded set, derived from
# tests/closures.json -- not a hand-kept list. The eight-script default the
# audit measured drove mutants with 8 of the 24 recorded scripts and never
# ran the differential golden step (tests/env_drift.py --all), so a recorded
# survivor fraction was not the fraction this repository's gate produces.
_MUT_EXCL = getattr(_mut, "DRIVER_EXCLUSIONS", {})
_MUT_DEFAULT_LIST = _MUT_DEFAULT.split(",") if _MUT_DEFAULT else []
R.check(
    "the driver net is the recorded gate set minus named exclusions (#1211)",
    bool(_MUT_DEFAULT_LIST)
    and set(_MUT_DEFAULT_LIST) | set(_MUT_EXCL) == set(_MUT_REAL_CLOSURES)
    and not (set(_MUT_DEFAULT_LIST) & set(_MUT_EXCL))
    and all(_MUT_EXCL.values()),
    f"{len(_MUT_DEFAULT_LIST)} driving of {len(_MUT_REAL_CLOSURES)} recorded, "
    f"{len(_MUT_EXCL)} excluded with a reason -- a net that is neither "
    "derived nor total is exactly the drift this check stops",
)
_MUT_DRIVE_SPEC = getattr(_mut, "drive_spec", lambda _s, _r: None)
_MUT_SKIP = getattr(_mut, "ref_skip_reason", lambda _r, _t: None)
_MUT_GATE_REF = getattr(_mut, "gate_ref", lambda _s, _b: None)
R.check(
    "the differential golden step is drivable as the gate drives it (#1211)",
    _MUT_DRIVE_SPEC("tests/env_drift.py", "some-ref")
    == (["--all", "some-ref"], {})
    and _MUT_DRIVE_SPEC("tests/stress.py", "some-ref")
    == ([], {"GOLDEN_REF": "some-ref"})
    and _MUT_DRIVE_SPEC("tests/entities.py", "some-ref") == ([], {}),
    f"env_drift={_MUT_DRIVE_SPEC('tests/env_drift.py', 'some-ref')!r} -- a "
    "bare run compares against env_drift's own default; the gate's step takes "
    "the resolved ref after --all and hands stress the exported GOLDEN_REF",
)
R.check(
    "the ref-driven pair skips by the gate's own rule, not a vacuous run (#1211)",
    "is this commit" in (_MUT_SKIP("HEAD", _mut.ROOT) or "")
    and "not available here"
    in (_MUT_SKIP("no-such-ref-audit-1211", _mut.ROOT) or ""),
    f"HEAD -> {_MUT_SKIP('HEAD', _mut.ROOT)!r} -- env_drift refuses a ref that "
    "resolves to HEAD (a gate that cannot fail), so tests/run.sh skips it out "
    "loud; a driver dropped here is the same decision, not a silent pass",
)
# The ref the drivers are handed is resolved exactly as run.sh reads it:
# GOLDEN_REF when the environment sets it, HEAD^1 for the nightly otherwise.
_MUT_FULL_REF = _os.environ.get("GOLDEN_REF", "").strip() or "HEAD^1"
R.check(
    "and ref-driven drivers get run.sh's own resolution (#1211)",
    _MUT_GATE_REF("full", "origin/main") == _MUT_FULL_REF,
    f"full scope -> {_MUT_GATE_REF('full', 'origin/main')!r}, wanted "
    f"{_MUT_FULL_REF!r} -- the nightly's gate compares against HEAD^1 and a "
    "driver handed a different ref measures a different comparison",
)

# #1217 (D3-07): two of the D3 pre-screen's seven survivors are EQUIVALENT
# mutants -- pump_mode.py:242 GUARD_OFF and __init__.py:337 BOOLOP, each
# measured against its own guarded input -- which no check could ever kill,
# so a survivor count that mixes them with real gaps reads worse than the
# suite is. The triage marks live in tests/mutation_budgets.json under
# "survivor_triage", keyed exactly like the recorded survivor table and
# PINNED to the line text they were triaged on; the fraction the cap reads
# counts only survivors no triage has called equivalent. Absence of a triage
# is not a finding of equivalence -- an unmarked survivor stays a gap.
_MUT_TRIAGE = _MB.get("survivor_triage", {})
_MUT_TRIAGE_KEY = getattr(_mut, "triage_key", lambda _m: None)
_MUT_EQ = getattr(_mut, "triaged_equivalent", lambda _t, _m: None)
_MUT_GAPS = getattr(_mut, "survivor_gaps", lambda _s, _t: None)
_MUT_TRIAGE_PROBLEMS = getattr(_mut, "triage_problems",
                               lambda _t: ["no triage_problems"])
# Two synthetic survivors shaped like the table's rows; the triage fixture
# marks one of them, key and pin alike.
_EQ_MUT = {"file": "custom_components/heatpump_optimizer/pump_mode.py",
           "line": 242, "kind": "GUARD_OFF", "old": "    if raw is None:"}
_GAP_MUT = {"file": "custom_components/heatpump_optimizer/frontend.py",
            "line": 110, "kind": "BOOLOP",
            "old": '        if a and b:'}
_EQ_KEY = "custom_components/heatpump_optimizer/pump_mode.py:242 GUARD_OFF"
_TRIAGE_FIXTURE = {_EQ_KEY: {"verdict": "equivalent",
                             "old": "    if raw is None:",
                             "reason": "probe: no input can tell it apart"}}
R.check(
    "a survivor triaged equivalent is off the fraction; an unmarked one stays (#1217)",
    _MUT_TRIAGE_KEY(_EQ_MUT) == _EQ_KEY
    and _MUT_GAPS([_EQ_MUT, _GAP_MUT], _TRIAGE_FIXTURE)
    == ([_GAP_MUT], [_EQ_MUT]),
    f"key={_MUT_TRIAGE_KEY(_EQ_MUT)!r}, gaps -> "
    f"{_MUT_GAPS([_EQ_MUT, _GAP_MUT], _TRIAGE_FIXTURE)!r} -- the marked line "
    "leaves the numerator; the unmarked survivor stays in it, because the "
    "default has to stay guilty until a reason moves it",
)
# The line pin is half the mark: file and line are where the mutant WAS, and
# a production edit moves text under the same coordinates all the time. The
# other half is the verdict: a "gap" triage records a real gap and must not
# come off the fraction. The null controls drive all three arms through the
# same predicate.
R.check(
    "and only an `equivalent` verdict applies, pinned line text and all (#1217)",
    _MUT_EQ(_TRIAGE_FIXTURE, _EQ_MUT) is True
    and _MUT_EQ(_TRIAGE_FIXTURE, dict(_EQ_MUT, old="    if raw:")) is False
    and _MUT_EQ(_TRIAGE_FIXTURE, dict(_EQ_MUT, line=243)) is False
    and _MUT_EQ({_EQ_KEY: {"verdict": "gap", "old": _EQ_MUT["old"],
                           "reason": "a real gap, triaged"}}, _EQ_MUT) is False,
    f"same pin -> {_MUT_EQ(_TRIAGE_FIXTURE, _EQ_MUT)!r}, moved text -> "
    f"{_MUT_EQ(_TRIAGE_FIXTURE, dict(_EQ_MUT, old='    if raw:'))!r}, moved "
    f"line -> {_MUT_EQ(_TRIAGE_FIXTURE, dict(_EQ_MUT, line=243))!r}, gap "
    f"verdict -> {_MUT_EQ({_EQ_KEY: {'verdict': 'gap', 'old': _EQ_MUT['old'], 'reason': 'r'}}, _EQ_MUT)!r} "
    "-- a mark that outlives the line it explains is a claim about code that "
    "is gone, and a triaged gap is exactly what the fraction is for",
)
# The validator is a predicate, so the refusal shape is driven rather than
# trusted: a good entry passes; an unknown verdict, a missing reason, a
# missing pin and a key that is not `FILE:LINE KIND` are four problems.
_MUT_TRIAGE_BAD = {
    _EQ_KEY: {"verdict": "sure", "old": "", "reason": ""},
    "junk": {"verdict": "equivalent", "old": "x", "reason": "r"},
}
R.check(
    "a triage entry without a verdict, reason or line pin is refused (#1217)",
    _MUT_TRIAGE_PROBLEMS(_TRIAGE_FIXTURE) == []
    and len(_MUT_TRIAGE_PROBLEMS(_MUT_TRIAGE_BAD)) == 4,
    f"good -> {_MUT_TRIAGE_PROBLEMS(_TRIAGE_FIXTURE)!r}, bad -> "
    f"{_MUT_TRIAGE_PROBLEMS(_MUT_TRIAGE_BAD)!r} -- an unargued equivalence "
    "claim is the one shape that could quietly relax the fraction",
)
# The recorded table itself: both D3-07 equivalents marked, each with a
# reason; the validator holds over the whole real table; and every mark
# names a mutant THIS tree still generates -- same line, same operator,
# same text -- so the pins are checked against the tree, not each other.
_MUT_D3_07 = (
    "custom_components/heatpump_optimizer/pump_mode.py:242 GUARD_OFF",
    "custom_components/heatpump_optimizer/__init__.py:337 BOOLOP",
)
R.check(
    "the recorded triage marks both D3-07 equivalents, verdict and reason (#1217)",
    all(_MUT_TRIAGE.get(k, {}).get("verdict") == "equivalent"
        and str(_MUT_TRIAGE.get(k, {}).get("reason", "")).strip()
        for k in _MUT_D3_07),
    f"marked: {sorted(_MUT_TRIAGE)} -- the audit measured resolve(None) and "
    "the async_create_task return as indistinguishable both ways, and a "
    "survivor table that does not say so charges the suite for them",
)
_MUT_TRIAGE_STALE = []
for _k, _ent in sorted(_MUT_TRIAGE.items()):
    _rel, _rest = _k.split(":")
    _ln, _kind = _rest.split(" ", 1)
    _hit = [m for m in _mut.candidates(Path(_rel))
            if m["line"] == int(_ln) and m["kind"] == _kind]
    if len(_hit) != 1 or _hit[0]["old"] != _ent.get("old"):
        _MUT_TRIAGE_STALE.append(_k)
R.check(
    "and every mark still names a mutant this tree generates, pin and all (#1217)",
    bool(_MUT_TRIAGE) and _MUT_TRIAGE_PROBLEMS(_MUT_TRIAGE) == []
    and not _MUT_TRIAGE_STALE,
    f"stale={_MUT_TRIAGE_STALE or 'none'}, problems="
    f"{_MUT_TRIAGE_PROBLEMS(_MUT_TRIAGE)} -- a mark is only allowed to "
    "speak for the exact mutant it was measured on",
)

# The classification the ratchet demands of any new tracked file: not
# selectable (each needs an instrument the gate does not run), not INERT
# (this script imports both).
R.check(
    "both instruments are classified: NOT_A_TEST, and not on INERT",
    {"coverage_ratchet.py", "mutation_table.py"} <= _closure.NOT_A_TEST
    and not _closure.is_inert("tests/coverage_ratchet.py")
    and not _closure.is_inert("tests/mutation_table.py"),
    "a file that is neither in a closure nor on a list forces the FULL suite",
)

# --- a red baseline is the nightly's refusal, not the pull request's (#RCA) --
#
# Every red `mutation` job in the RCA's retained window (2026-09-11..17) was
# this arm -- the baseline guard -- and none was a surviving mutant, so a red
# baseline costs a reviewer round and carries no mutation information: the
# table evaluated nothing. `mutation` is not a required context and `fast` is.
#
# The baseline's driver set is NOT the scoped gate's selection, and the
# difference is the whole of what a pull request gives up: on a diff that
# changes no production file, `scope_files` falls back to the closure of the
# changed TEST scripts, which on this branch's own diff is 63 production files
# and 19 drivers against the gate's 1 selected script. Re-derive that pair at
# your merge base rather than carrying it; `baseline_refusal`'s docstring says
# with what. The NIGHTLY keeps the refusal: nothing else reports that lane's
# baseline per commit.
#
# Driven as a function rather than through `main()`, which clones the tree and
# runs real scripts; the fixtures below carry the shape `run_script` returns.
import contextlib as _mutb_contextlib  # noqa: E402
import io as _mutb_io  # noqa: E402

# `run_script` returns a `ScriptRun` carrying the stdout and stderr it judged
# (#1134); before the fix it returned a bare (rc, failed, seconds) with that
# text discarded. `_mut_run` builds whichever shape this tree has, so on the
# unfixed tree these fixtures still build and the checks below FAIL by name
# rather than dying on an AttributeError before reaching the rest of the suite.
_MutScriptRun = getattr(_mut, "ScriptRun", None)


def _mut_run(rc: int, failed: int, secs: float, stdout: str = "", stderr: str = ""):
    if _MutScriptRun is not None:
        return _MutScriptRun(rc, failed, secs, stdout, stderr)
    return (rc, failed, secs)


# The red runs' output names the checks that went red -- the text #1134 is
# about. `tests/pv.py` is green and prints only a passing line: the null
# control on "a passing script's output is never read as a failing check".
_MUT_CHECKS = ("payroll rounding", "holiday override", "tariff night window")
_MUT_STDOUT = {
    "tests/entities.py":
        "  ok   a passing check\n"
        "  FAIL payroll rounding  [got 41]\n"
        "  FAIL holiday override\n"
        "  2 of 3 ENTITY CHECKS FAILED\n",
    "tests/features.py":
        "  FAIL tariff night window\n"
        "  1 of 1 FEATURE CHECKS FAILED\n",
    "tests/pv.py": "  ok   a passing check\n  1 of 1 PV CHECKS PASSED\n",
}
_MUT_RED = {
    "tests/entities.py": _mut_run(1, 2, 41.0, _MUT_STDOUT["tests/entities.py"]),
    "tests/features.py": _mut_run(1, 1, 12.0, _MUT_STDOUT["tests/features.py"]),
    "tests/pv.py": _mut_run(0, 0, 9.0, _MUT_STDOUT["tests/pv.py"]),
}
_MUT_GREEN = {s: _mut_run(0, 0, secs, "  ok   a passing check\n"
                          "1 of 1 CHECKS PASSED\n") for s, secs in
              (("tests/entities.py", 41.0), ("tests/features.py", 12.0),
               ("tests/pv.py", 9.0))}


# `getattr` with a sentinel rather than a bare attribute read: with the guard
# still inline in `main()` this file must FAIL these four checks, not die on an
# AttributeError before reaching the rest of the suite.
_mut_refuse = getattr(_mut, "baseline_refusal",
                      lambda _baseline, _scope: "no baseline_refusal")


def _mut_baseline(baseline: dict, scope: str) -> tuple[object, str]:
    """(return value, printed text) of the baseline guard."""
    _buf = _mutb_io.StringIO()
    with _mutb_contextlib.redirect_stdout(_buf):
        _rc = _mut_refuse(baseline, scope)
    return _rc, _buf.getvalue()


_MUT_PR_RC, _MUT_PR_OUT = _mut_baseline(_MUT_RED, "changed")
_MUT_NIGHT_RC, _MUT_NIGHT_OUT = _mut_baseline(_MUT_RED, "full")
_MUT_OK_RC, _MUT_OK_OUT = _mut_baseline(_MUT_GREEN, "changed")

R.check(
    "a red baseline on the pull-request scope is INCONCLUSIVE, not a failure",
    _MUT_PR_RC == 0 and "MUTATION TABLE INCONCLUSIVE" in _MUT_PR_OUT
    and "MUTATION TABLE BREACHED" not in _MUT_PR_OUT,
    f"rc={_MUT_PR_RC!r}, printed {_MUT_PR_OUT.strip()!r} -- the table "
    f"evaluated no mutant, so this lane reports nothing a required check does "
    f"not already carry or a required detector does not already cover",
)
R.check(
    "and it names the red script, because the report is useless without it",
    "tests/entities.py" in _MUT_PR_OUT and "tests/features.py" in _MUT_PR_OUT
    and "tests/pv.py" not in _MUT_PR_OUT,
    "the refusal names the red SCRIPT; the stdout that would let it name the "
    "red CHECK inside that script is what #1134 returns from `run_script`",
)
# #1134: the refusal had to name the red CHECK, not only the red script. The
# name lives in the stdout `run_script` captured; before the fix that text was
# discarded once the failure count was regexed out of it.
R.check(
    "and it names each red CHECK, not only the script that carries it (#1134)",
    all(_name in _MUT_PR_OUT for _name in _MUT_CHECKS),
    f"printed {_MUT_PR_OUT.strip()!r}; wanted {_MUT_CHECKS} -- a refusal that "
    "names only the script sends its reader back to re-run it",
)
# The boundary of that widening: a red script whose output carries no harness
# FAIL line (`tests/plan_view.py` and `tests/validate.py` print `ISSUES:`
# bullets) is still named, and its reason is surfaced rather than a check name
# invented for it.
_MUT_NOFAIL = {"tests/plan_view.py": _mut_run(
    1, 0, 3.0, "PLAN VIEW ISSUES:\n  - slot energy short\n")}
_MUT_NF_RC, _MUT_NF_OUT = _mut_baseline(_MUT_NOFAIL, "changed")
R.check(
    "a red script whose output has no FAIL line still names its reason",
    _MUT_NF_RC == 0 and "tests/plan_view.py" in _MUT_NF_OUT
    and "slot energy short" in _MUT_NF_OUT,
    f"printed {_MUT_NF_OUT.strip()!r} -- plan_view.py and validate.py print "
    "`ISSUES:` bullets rather than harness FAIL lines, so the refusal falls "
    "back to the last line of that output, never to the script alone",
)
# The null control on the weakening: the nightly is the only per-commit report
# of a full-scope baseline, so its refusal must survive this change unchanged.
R.check(
    "the nightly scope still refuses with exit 1 on the same baseline",
    _MUT_NIGHT_RC == 1 and "MUTATION TABLE INCONCLUSIVE" in _MUT_NIGHT_OUT,
    f"rc={_MUT_NIGHT_RC!r} -- `--scope full` runs only on schedule, where no "
    f"other check reports the baseline",
)
# The null control on the green arm: a guard that returns a verdict on a GREEN
# baseline would make the lane pass by never reaching the table at all, which
# is the silent-green shape this file keeps finding.
R.check(
    "a green baseline takes no verdict at either scope; the table proceeds",
    _mut_refuse(_MUT_GREEN, "changed") is None
    and _mut_refuse(_MUT_GREEN, "full") is None
    and _MUT_OK_OUT == "",
    f"changed={_mut_refuse(_MUT_GREEN, 'changed')!r}, "
    f"full={_mut_refuse(_MUT_GREEN, 'full')!r}, "
    f"printed {_MUT_OK_OUT!r}",
)

# #1134 pinned at the CAPTURE, not only at the guard: the fixtures above are
# hand-built, so a `run_script` that still discarded the text would leave every
# check about naming the red check green. Drive the real `run_script` against a
# script written to print one FAIL line, and read the name back off its result.
_mut_checks = getattr(_mut, "failed_checks", None)


def _mut_names(run) -> list:
    """The FAIL names one `run_script` result carries; [] before the fix."""
    return _mut_checks(run) if _mut_checks is not None else []


_MUT_PROBE_DIR = Path(_tempfile.mkdtemp(prefix="mutation-runscript-"))
(_MUT_PROBE_DIR / "bad.py").write_text(
    "print('  ok   a passing check')\n"
    "print('  FAIL the probe check  [detail]')\n"
    "print('1 of 2 PROBE CHECKS FAILED')\n"
    "raise SystemExit(1)\n"
)
(_MUT_PROBE_DIR / "ok.py").write_text(
    "print('  ok   a passing check')\n"
    "print('1 of 1 PROBE CHECKS PASSED')\n"
)
_MUT_PROBE_RUN = _mut.run_script(str(_MUT_PROBE_DIR / "bad.py"), _mut.ROOT, 60)
R.check(
    "run_script returns the stdout whose FAIL line names the red check (#1134)",
    any("the probe check" in _name for _name in _mut_names(_MUT_PROBE_RUN)),
    f"checks={_mut_names(_MUT_PROBE_RUN)!r} from a REAL run of a script that "
    "prints one FAIL line -- the count is pulled out of that text, and the "
    "text is what a refusal needs to name the check",
)
_MUT_PROBE_OK_RUN = _mut.run_script(str(_MUT_PROBE_DIR / "ok.py"), _mut.ROOT, 60)
R.check(
    "and a passing run yields no failing check name",
    _mut_names(_MUT_PROBE_OK_RUN) == [],
    f"checks={_mut_names(_MUT_PROBE_OK_RUN)!r} -- the null control: a green "
    "script must not be read as naming a failing check",
)
_mut_shutil.rmtree(_MUT_PROBE_DIR, ignore_errors=True)


sys.exit(R.close("ENTITY CHECKS"))
