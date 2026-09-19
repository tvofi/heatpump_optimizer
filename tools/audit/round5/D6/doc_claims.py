#!/usr/bin/env python3
# D6 — the documentation claim table.
#
# METRIC DEFINITION: one `RESULT <claim>=<value>` per documented claim, hand
# transcribed from README.md / docs/*.md into the CHECKS table below and
# recomputed here from the production symbols. A claim counts as `held` when
# its recomputed value equals the documented one exactly. The headline number
# is `RESULT doc_claims_failed_collection=` — the count of checks whose value
# disagrees with the documentation (and their names, on the next line).
#
# RUN (from the repository root):
#     PYTHONPATH=tests/hastub python3 tools/audit/round5/D6/doc_claims.py
#
# EXPECTED (baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225):
#     RESULT doc_claims_failed_collection=0 count
#     RESULT services_yaml_examples_valid=6 of 6
#     RESULT services_yaml_selectors_within_schema=32 of 32
#     RESULT documented_defaults_held=41 of 41
#     (tolerance: exact; a nonzero failure count is itself the finding)
#     `--perturb` must move documented_defaults_held 41 -> 40 and name
#     `default dhw_min_temp` as the only failure.
#
# MACHINE: macOS Darwin 25.6.0, Apple Silicon, CPython 3.x (see RESULT
# python_version). Requires PyYAML (present on this box, 6.0.1).
#
# INSTRUMENTED SYMBOL: `custom_components.heatpump_optimizer.const:*`,
# `...config_flow:_OPTION_PAGES`, `...services:SERVICE_SCHEMA_*` and
# `...topology:ASSIGNABLE_KEYS` — every value is read off the production
# module, none is re-typed. A `RESULT ..._failed` line for any group means the
# documentation and the code disagree about that group.
#
# PERTURBATION: the group counts are only meaningful against a moved number.
# Run with `--perturb` and the harness edits ONE production constant in memory
# (`const.DEFAULT_DHW_MIN_TEMP` 45 -> 44) and re-runs the default table; that
# check must flip from pass to fail, and only that one. It proves the table is
# wired to the production value rather than to the documentation.
#
# NO TIMING RESULT: every number is a deterministic count; no block here
# carries a `thread_factor`, and none is claimed. `load1` and `swapins` are
# printed at the end.

import json
import os
import pathlib
import re
import sys

# Thread pin, before any numpy import (the contract's first rule).
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))

import yaml  # noqa: E402

import time  # noqa: E402

# CPU ruler for the block's `thread_factor`. Every check here is single
# threaded (no BLAS call is made after the pin), so the ratio is ~1.0; it is
# measured, not asserted.
_T0_PROC = time.process_time()
_T0_THREAD = time.thread_time()

from custom_components.heatpump_optimizer import (  # noqa: E402
    config_flow,
    const,
    services,
    topology,
)

PERTURB = "--perturb" in sys.argv
if PERTURB:
    const.DEFAULT_DHW_MIN_TEMP = 44.0

PKG = ROOT / "custom_components" / "heatpump_optimizer"
DOCS = ROOT / "docs"

results: list[tuple[str, object, str]] = []   # (name, value, unit)
failures: list[str] = []


def check(name: str, value, documented, unit: str = "") -> None:
    """Record one claim: `value` recomputed from production, `documented` the
    number the documentation states."""
    ok = value == documented
    results.append((name, value, unit))
    if not ok:
        failures.append(f"{name}: docs say {documented!r}, code says {value!r}")


# ---------------------------------------------------------------- page counts
# docs/configuration.md:9 "the 22 options pages behind two menus"
# docs/configuration.md:201 "22 pages: six on the first menu, and sixteen more"
# README.md:725 "menu of 22 pages — 21 you can edit plus a read-only overview"
pages = config_flow._OPTION_PAGES
check("option_pages_total", len(pages), 22, "pages")
check("option_pages_first_menu", sum(p.menu == "top" for p in pages), 6, "pages")
check("option_pages_advanced", sum(p.menu == "advanced" for p in pages), 16, "pages")
check(
    "option_pages_read_only",
    sum(1 for p in pages if p.step == "setup_overview"),
    1,
    "pages",
)

# ------------------------------------------------------------------- services
# README.md:596 / docs/configuration.md:739 "12 services"
check(
    "services_registered",
    len(re.findall(r"hass\.services\.async_register\(", (PKG / "services.py").read_text())),
    12,
    "services",
)
# README.md:597 / docs/configuration.md:757 "28 fields of set_thermal_parameters"
check(
    "set_thermal_parameters_fields",
    len(services.SERVICE_SCHEMA_SET_THERMAL_PARAMS.schema),
    28,
    "fields",
)
# docs/configuration.md:758 "simulate_plan | 16 optional comfort and wood fields"
check(
    "simulate_plan_fields",
    len(services.SERVICE_SCHEMA_SIMULATE_PLAN.schema),
    16,
    "fields",
)
# docs/configuration.md:759 "apply_schedule | 5 optional schedule fields + entry_id"
check(
    "apply_schedule_fields",
    sum(
        1
        for k in services.SERVICE_SCHEMA_APPLY_SCHEDULE.schema
        if getattr(k, "schema", None) != "entry_id"
    ),
    5,
    "fields",
)
# docs/configuration.md:739-745 "seven ... accept an optional entry_id"
check(
    "services_with_entry_id",
    sum(
        1
        for s in (
            services.SERVICE_SCHEMA_ASSIGN_ENTITY,
            services.SERVICE_SCHEMA_APPLY_TOPOLOGY,
            services.SERVICE_SCHEMA_APPLY_SCHEDULE,
            services.SERVICE_SCHEMA_APPLY_MANUAL_PLAN,
            services.SERVICE_SCHEMA_CLEAR_MANUAL_PLAN,
            services.SERVICE_SCHEMA_RESTORE_SNAPSHOT,
            services.SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
        )
        if any(getattr(k, "schema", None) == "entry_id" for k in s.schema)
    ),
    7,
    "services",
)
# docs/configuration.md:831 "key is one of the 21 assignable configuration keys"
check("assignable_keys", len(topology.ASSIGNABLE_KEYS), 21, "keys")
DOC_KEYS = {
    "outdoor_temp_entity", "solar_radiation_entity", "pv_production_entity",
    "indoor_temp_entity", "lower_floor_temp_entity", "floor_return_temp_entity",
    "heat_pump_switch_entity", "heat_pump_power_entity", "heat_pump_energy_entity",
    "house_power_entity", "heat_pump_mode_entity", "heat_pump_defrost_entity",
    "heat_pump_online_entity", "heat_pump_fault_entity", "buffer_tank_temp_entity",
    "mixing_valve_target_entity", "dhw_temp_entity", "external_heat_entity",
    "wood_tank_top_entity", "wood_tank_bottom_entity", "valve_outlet_temp_entity",
}
check("assignable_keys_doc_set_matches", set(topology.ASSIGNABLE_KEYS) == DOC_KEYS, True)

# ---------------------------------------------------------------- .storage set
# README.md:279-293 "twelve files under .storage/" plus the twelve names.
DOC_STORES = {
    "thermal_learning", "price_model", "accuracy", "ledger", "energy",
    "snapshots", "dhw_profile", "dhw_draws", "dhw_legionella", "manual_plan",
    "away", "boost",
}
src = "\n".join((PKG / f).read_text() for f in (
    "away.py", "boost.py", "dhw_learning.py", "coordinator.py", "legionella.py"))
CODE_STORES = set(re.findall(r"\{DOMAIN\}_\{[^}]+\}_([a-z_]+)\"", src))
check("storage_files_total", len(CODE_STORES), 12, "files")
check("storage_files_doc_set_matches", CODE_STORES == DOC_STORES, True)

# ------------------------------------------------------------------ versions
# README.md badge / manifest.json / the card's own version banner.
check("version_file", (ROOT / "VERSION").read_text().strip(),
      json.loads((PKG / "manifest.json").read_text())["version"])
check(
    "card_version_matches_integration",
    re.search(r'const CARD_VERSION = "([^"]+)"', (PKG / "www" / "heatpump-optimizer-card.js").read_text()).group(1),
    json.loads((PKG / "manifest.json").read_text())["version"],
)

# ------------------------------------------------- strings.json / translations
# services.yaml:1-5 "Every name and description lives in the translation
# catalogues (strings.json / translations/*.json)".
strings = json.loads((PKG / "strings.json").read_text())
check("services_in_strings_json", len(strings.get("services", {})), 12, "services")
check(
    "translations_en_identical_to_strings",
    json.loads((PKG / "translations" / "en.json").read_text()) == strings,
    True,
)


def leaves(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(leaves(v, p + "/" + k))
    else:
        out[p] = o
    return out


sv = json.loads((PKG / "translations" / "sv.json").read_text())
check("sv_missing_leaves", len(set(leaves(strings)) - set(leaves(sv))), 0, "keys")

# ------------------------------------------------- plan-sensor documented attrs
# docs/dashboard-card.md:229/308 sensor.py must publish these on the plan
# sensors, and keep `forecast` out of the recorder (line 206).
sensor_src = (PKG / "sensor.py").read_text()
_plan_cls = sensor_src.index("class _PlanSensorBase")
_plan_unrecorded = sensor_src[_plan_cls:][
    : sensor_src[_plan_cls:].index("_unrecorded_attributes")
    + 400
]
for attr in ("plan_kind", "manual_plan_window_hours", "dhw_windows_spec", "currency"):
    check(f"plan_sensor_attr_{attr}", f'"{attr}"' in sensor_src, True)
check(
    "plan_forecast_unrecorded",
    '"forecast"' in _plan_unrecorded,
    True,
)

# ------------------------------------------------------ services.yaml vs schema
# The D6 brief's designed check: every `example` in services.yaml fed through
# the voluptuous schema the service actually uses, and every selector's range
# contained in the schema's range.
SERVICES_YAML = yaml.safe_load((PKG / "services.yaml").read_text())
SCHEMAS = {
    "run_optimization": services.SERVICE_SCHEMA_RUN_OPTIMIZATION,
    "set_away": services.SERVICE_SCHEMA_SET_AWAY,
    "set_mode": services.SERVICE_SCHEMA_SET_MODE,
    "set_thermal_parameters": services.SERVICE_SCHEMA_SET_THERMAL_PARAMS,
    "simulate_plan": services.SERVICE_SCHEMA_SIMULATE_PLAN,
    "apply_schedule": services.SERVICE_SCHEMA_APPLY_SCHEDULE,
    "assign_entity": services.SERVICE_SCHEMA_ASSIGN_ENTITY,
    "apply_topology": services.SERVICE_SCHEMA_APPLY_TOPOLOGY,
    "apply_manual_plan": services.SERVICE_SCHEMA_APPLY_MANUAL_PLAN,
    "clear_manual_plan": services.SERVICE_SCHEMA_CLEAR_MANUAL_PLAN,
    "restore_learned_snapshot": services.SERVICE_SCHEMA_RESTORE_SNAPSHOT,
    "diagnose_interval": services.SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
}
check("services_yaml_service_count", len([k for k, v in SERVICES_YAML.items()]), 12, "services")


def inner_range(node):
    """(min, max) from a vol.All(..., vol.Range(...)) or None."""
    import voluptuous as vol

    for v in getattr(node, "validators", []) or []:
        if isinstance(v, vol.Range):
            lo = None if v.min is None else (0 if v.min_included is None else v.min)
            hi = None if v.max is None else (0 if v.max_included is None else v.max)
            return (v.min, v.max)
    return None


def schema_fields(node):
    """The {key: validator} map of a vol.Schema, unwrapping a vol.All wrapper
    (SERVICE_SCHEMA_SET_AWAY is vol.All(vol.Schema(...), fn))."""
    import voluptuous as vol

    if isinstance(node, vol.Schema):
        return node.schema
    for v in getattr(node, "validators", []) or []:
        if isinstance(v, vol.Schema):
            return v.schema
    raise TypeError(f"no vol.Schema inside {node!r}")


examples_ok = examples_total = 0
ranges_ok = ranges_total = 0
for name, spec in SERVICES_YAML.items():
    schema = SCHEMAS[name]
    fields_map = schema_fields(schema)
    fields = (spec or {}).get("fields") or {}
    # The service's documented example as a whole: every field that carries
    # an `example` in services.yaml, fed through the service's own schema.
    doc_example = {f: fs["example"] for f, fs in fields.items() if "example" in fs}
    if doc_example:
        examples_total += 1
        try:
            schema(doc_example)
            examples_ok += 1
        except Exception as e:  # noqa: BLE001
            failures.append(f"{name}: documented example {doc_example!r} rejected: {e}")
    for fname, fspec in fields.items():
        node = None
        for key in fields_map:
            if getattr(key, "schema", None) == fname:
                node = fields_map[key]
        if node is None:
            failures.append(f"{name}.{fname}: services.yaml documents a field the schema rejects")
            continue
        sel = fspec.get("selector") or {}
        num = sel.get("number")
        if isinstance(num, dict) and ("min" in num or "max" in num):
            r = inner_range(node)
            if r:
                ranges_total += 1
                lo, hi = r
                if (num.get("min") is None or lo is None or num["min"] >= lo) and (
                    num.get("max") is None or hi is None or num["max"] <= hi
                ):
                    ranges_ok += 1
                else:
                    failures.append(
                        f"{name}.{fname}: selector {num.get('min')}..{num.get('max')} "
                        f"exceeds schema {lo}..{hi}"
                    )
results.append(("services_yaml_examples_valid", examples_ok, "of"))
results.append(("services_yaml_examples_total", examples_total, "services"))
results.append(("services_yaml_selectors_within_schema", ranges_ok, "of"))
results.append(("services_yaml_selectors_total", ranges_total, "selectors"))
if examples_ok != examples_total:
    failures.append(f"services_yaml examples: {examples_ok}/{examples_total} valid")
if ranges_ok != ranges_total:
    failures.append(f"services_yaml selectors: {ranges_ok}/{ranges_total} within schema")

# ------------------------------------------------------ documented default table
# (documented value, production symbol, doc source). Transcribed from the
# Default column of docs/configuration.md and README.md.
DEFAULTS = [
    ("target_temp", const.DEFAULT_TARGET_TEMP, 21.0),
    ("min_temp", const.DEFAULT_MIN_TEMP, 19.0),
    ("max_temp", const.DEFAULT_MAX_TEMP, 23.0),
    ("comfort_temp_day", const.DEFAULT_COMFORT_TEMP_DAY, 21.0),
    ("comfort_temp_night", const.DEFAULT_COMFORT_TEMP_NIGHT, 19.5),
    ("day_start_hour", const.DEFAULT_DAY_START_HOUR, 7),
    ("day_end_hour", const.DEFAULT_DAY_END_HOUR, 22),
    ("dhw_setpoint", const.DEFAULT_DHW_SETPOINT, 55.0),
    ("dhw_min_temp", const.DEFAULT_DHW_MIN_TEMP, 45.0),
    ("dhw_idle_min_temp", const.DEFAULT_DHW_IDLE_MIN_TEMP, 20.0),
    ("dhw_windows", const.DEFAULT_DHW_WINDOWS, "06:00-08:30, 17:00-22:00"),
    ("dhw_legionella_enabled", const.DEFAULT_DHW_LEGIONELLA_ENABLED, True),
    ("dhw_legionella_temp", const.DEFAULT_DHW_LEGIONELLA_TEMP, 60.0),
    ("dhw_legionella_interval_days", const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS, 7.0),
    ("dhw_cooling_rate", const.DEFAULT_DHW_COOLING_RATE, 0.3),
    ("dhw_tank_volume", const.DEFAULT_DHW_TANK_VOLUME, 200.0),
    ("dhw_daily_consumption", const.DEFAULT_DHW_DAILY_CONSUMPTION, 150.0),
    ("buffer_cooling_rate", const.DEFAULT_BUFFER_COOLING_RATE, 6.0),
    ("buffer_tank_volume", const.DEFAULT_BUFFER_TANK_VOLUME, 35.0),
    ("wind_sensitivity", const.DEFAULT_WIND_SENSITIVITY, 0.03),
    ("rain_multiplier", const.DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER, 1.15),
    ("optimization_interval", const.DEFAULT_OPTIMIZATION_INTERVAL, 30),
    ("comfort_weight", const.DEFAULT_COMFORT_WEIGHT, 5.0),
    ("house_thermal_mass", const.DEFAULT_HOUSE_THERMAL_MASS, 10.0),
    ("house_heat_loss", const.DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT, 0.15),
    ("slab_thermal_mass", const.DEFAULT_SLAB_THERMAL_MASS, 5.0),
    ("slab_heat_transfer", const.DEFAULT_SLAB_HEAT_TRANSFER, 0.8),
    ("upper_floor_thermal_mass", const.DEFAULT_UPPER_FLOOR_THERMAL_MASS, 3.0),
    ("lower_floor_thermal_mass", const.DEFAULT_LOWER_FLOOR_THERMAL_MASS, 8.0),
    ("upper_floor_heat_loss", const.DEFAULT_UPPER_FLOOR_HEAT_LOSS, 0.08),
    ("lower_floor_heat_loss", const.DEFAULT_LOWER_FLOOR_HEAT_LOSS, 0.07),
    ("inter_zone_transfer", const.DEFAULT_INTER_ZONE_TRANSFER, 0.5),
    ("radiator_power_fraction", const.DEFAULT_RADIATOR_POWER_FRACTION, 0.4),
    ("window_area", const.DEFAULT_WINDOW_AREA, 10.0),
    ("solar_orientation", const.DEFAULT_SOLAR_ORIENTATION_FACTOR, 0.7),
    ("solar_heat_gain", const.DEFAULT_SOLAR_HEAT_GAIN_COEFF, 0.7),
    ("wood_tank_volume", const.DEFAULT_WOOD_TANK_VOLUME, 500.0),
    ("wood_furnace_efficiency", const.DEFAULT_WOOD_FURNACE_EFFICIENCY, 75.0),
    ("peak_tariff_price", const.DEFAULT_PEAK_TARIFF_PRICE, 45.0),
    ("peak_tariff_count", const.DEFAULT_PEAK_TARIFF_COUNT, 3),
    ("peak_guard_margin", const.DEFAULT_PEAK_GUARD_MARGIN_KW, 0.5),
]
held = 0
for name, code_value, doc_value in DEFAULTS:
    if code_value == doc_value:
        held += 1
    else:
        failures.append(f"default {name}: docs {doc_value!r}, code {code_value!r}")
results.append(("documented_defaults_held", held, "of"))
results.append(("documented_defaults_total", len(DEFAULTS), "claims"))

# --------------------------------------------------------- blueprint paths (claim)
BLUEPRINTS = [
    "blueprints/automation/charge_ev_from_grid_headroom.yaml",
    "blueprints/automation/economy_mode_on_price_peak.yaml",
    "blueprints/automation/notify_on_manual_plan.yaml",
]
for bp in BLUEPRINTS:
    check(f"blueprint_exists_{pathlib.Path(bp).stem}", (ROOT / bp).is_file(), True)

# ---------------------------------------------------------------------- output
for name, value, unit in results:
    print(f"RESULT {name}={value} {unit}".rstrip())
print(f"RESULT doc_claims_failed_collection={len(failures)} count")
print(f"RESULT doc_claims_failed_names={'; '.join(failures) if failures else '(none)'}")
_dp = time.process_time() - _T0_PROC
_dt = time.thread_time() - _T0_THREAD
print(f"RESULT process_cpu_s={_dp:.3f} s")
print(f"RESULT thread_cpu_s={_dt:.3f} s")
print(f"RESULT thread_factor={(_dp / _dt) if _dt > 0 else 1.0:.3f} ratio")
try:
    import subprocess

    print(f"RESULT load1={os.getloadavg()[0]} 1min")
    print(f"RESULT swapins={subprocess.run(['sysctl','-n','vm.swapusage'],capture_output=True,text=True).stdout.strip().replace(' ','_')}")
except Exception:  # noqa: BLE001
    pass
print(f"RESULT python_version={sys.version.split()[0]}")
if PERTURB:
    print("PERTURBED: const.DEFAULT_DHW_MIN_TEMP 45 -> 44 must appear above as a failure")
