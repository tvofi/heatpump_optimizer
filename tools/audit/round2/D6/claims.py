#!/usr/bin/env python3
"""D6 harness: the documentation claims table, one executed check per claim.

Metric: for each numbered claim extracted from README.md, docs/*.md,
DISCLAIMER.md, services.yaml, strings.json, the translations, manifest.json
and hacs.json, the executed observation and a verdict in
{true, false, stale, unverifiable}. The RESULT lines are counts over that
table.

Command (from the export root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D6/claims.py
    D6_OFFLINE=1 ... skips the HEAD link checks (they become unverifiable)
    D6_ROLLING_OUT=<path> reads the RESULT lines of rolling_learning.py

Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, 8-core Apple M1,
tests/hastub stub, network on, rolling_learning.out present): claims_extracted=273,
claims_true=258, claims_false=1, claims_stale=4, claims_unverifiable=10 (exact;
the table is deterministic apart from the link checks, which flip to
unverifiable offline, and C293, which reads rolling_learning.out).

Instrumented symbols: the entity rosters through the real platform
``async_setup_entry`` of sensor/binary_sensor/button/switch/climate driven by
tests/harness.py:FakeCoordinator over the DATA payload of tests/entities.py;
the service registry through heatpump_optimizer.__init__:async_setup_entry
on a recording FakeServices; the config/options schemas through
config_flow.HeatPumpOptimizer{Config,Options}Flow.async_step_*; the
voluptuous service schemas; const.py; freq_control.FrequencyWatchdog,
power_guard.GuardState, curve_learning.CurveLearner, snapshots.SnapshotRing,
currency.resolve_currency driven directly.
Perturbation (per false claim, see REPORT.md): editing the documented
sentence to the observed value flips that row to true; editing the
production symbol the row reads flips it the other way.

Writes nothing but stdout; ``sys.dont_write_bytecode`` keeps __pycache__ out
of the export.
"""
import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import ast
import asyncio
import inspect
import json
import re
import resource
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import voluptuous as vol
import yaml

from harness import FakeCoordinator, FakeEntry, FakeHass, FakeServices

import heatpump_optimizer as integration
from heatpump_optimizer import (
    away,
    binary_sensor,
    button,
    climate,
    config_flow,
    const,
    currency,
    curve_learning,
    defrost,
    dhw_draws,
    drift,
    freq_control,
    frontend,
    grid_fee,
    optimizer,
    power_guard,
    price_model,
    sensor,
    snapshots,
    switch,
    topology,
)
from homeassistant.helpers import selector as ha_selector

ROOT = Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"
README = (ROOT / "README.md").read_text(encoding="utf-8")
DOCS = {p.name: p.read_text(encoding="utf-8") for p in (ROOT / "docs").glob("*.md")}
DISCLAIMER = (ROOT / "DISCLAIMER.md").read_text(encoding="utf-8")
MANIFEST = json.loads((PKG / "manifest.json").read_text())
HACS = json.loads((ROOT / "hacs.json").read_text())
STRINGS = json.loads((PKG / "strings.json").read_text())
SERVICES_YAML = yaml.safe_load((PKG / "services.yaml").read_text())
CARD_JS = (PKG / "www" / "heatpump-optimizer-card.js").read_text(encoding="utf-8")
SRC = {p.name: p.read_text(encoding="utf-8") for p in PKG.glob("*.py")}
OFFLINE = os.environ.get("D6_OFFLINE") == "1"

# ---------------------------------------------------------------------------
# The claims table
# ---------------------------------------------------------------------------
ROWS: list[dict] = []


def claim(cid: str, source: str, text: str, check):
    """Run ``check`` and record a row. ``check`` returns (observed, verdict, truth)."""
    try:
        observed, verdict, truth = check()
    except Exception as exc:  # noqa: BLE001 - a crashed check is an unverifiable row
        observed, verdict, truth = f"check raised {type(exc).__name__}: {exc}", "unverifiable", ""
    ROWS.append(
        {"id": cid, "source": source, "claim": text, "observed": str(observed), "verdict": verdict, "truth": truth}
    )


def eq(observed, expected, truth_if_false: str = "", stale: bool = False):
    """Equality check; ``stale`` labels a wrong-but-historical claim."""
    ok = observed == expected
    return (
        f"observed={observed!r} expected={expected!r}",
        "true" if ok else ("stale" if stale else "false"),
        "" if ok else (truth_if_false or f"the code has {observed!r}"),
    )


def ok(cond: bool, observed: str, truth_if_false: str = "", stale: bool = False):
    return observed, "true" if cond else ("stale" if stale else "false"), "" if cond else truth_if_false


def unverifiable(observed: str):
    return observed, "unverifiable", ""


def src_has(module: str, pattern: str) -> bool:
    return re.search(pattern, SRC[module]) is not None


# ---------------------------------------------------------------------------
# Entities through the real platform setup
# ---------------------------------------------------------------------------
def _entities_data() -> dict:
    """The DATA payload of tests/entities.py, read as a literal (that module runs on import)."""
    tree = ast.parse((ROOT / "tests" / "entities.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "DATA" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise RuntimeError("DATA not found in tests/entities.py")


DATA = _entities_data()
ENTRY = FakeEntry()


def collect(module, data=None, coordinator=None):
    added = []

    def add_entities(entities):
        added.extend(entities)

    if coordinator is None:
        coordinator = FakeCoordinator(DATA if data is None else data)
        coordinator._month_totals = {"dhw": (41.5, 62.25), "space": (120.0, 180.0)}
    hass = FakeHass()
    hass.data[const.DOMAIN] = {ENTRY.entry_id: coordinator}
    asyncio.run(module.async_setup_entry(hass, ENTRY, add_entities))
    return added


def display_name(platform: str, entity) -> str:
    key = getattr(entity, "_attr_translation_key", None)
    return STRINGS["entity"].get(platform, {}).get(key, {}).get("name", f"<untranslated {platform}:{key}>")


SENSORS = collect(sensor)
BINARY = collect(binary_sensor)
BUTTONS = collect(button)
SWITCHES = collect(switch)
CLIMATES = collect(climate)
SENSOR_BY_NAME = {display_name("sensor", s): s for s in SENSORS}
SENSOR_BY_KEY = {s._attr_translation_key: s for s in SENSORS}


def md_table_rows(text: str, start_marker: str, end_marker: str) -> list[list[str]]:
    block = text.split(start_marker, 1)[1].split(end_marker, 1)[0]
    rows = []
    for line in block.splitlines():
        if line.startswith("| ") and not line.startswith("|---") and not line.startswith("| Sensor |") \
                and not line.startswith("| Binary sensor |") and not line.startswith("| Button |") \
                and not line.startswith("| Service |"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


README_SENSOR_ROWS = md_table_rows(README, "### Sensors (55 total)", "Disabled by default:")
README_BINARY_ROWS = md_table_rows(README, "### Binary Sensors (4 total)", "### Buttons")
README_BUTTON_ROWS = md_table_rows(README, "### Buttons (4 total)", "### Switch and climate")
README_SERVICE_ROWS = md_table_rows(README, "## Services", "`assign_entity` and `apply_topology` are")

UNIT_MAP = {"—": None, "CUR": "SEK", "CUR/kWh": "SEK/kWh", "%": "%", "°C": "°C", "kW": "kW",
            "W/m²": "W/m²", "kWh": "kWh", "L": "L", "Hz": "Hz"}


def _readme_name_to_entity(name: str):
    """README names omit the '(lifetime)' / '(next 24 h)' qualifiers; resolve by prefix."""
    if name in SENSOR_BY_NAME:
        return SENSOR_BY_NAME[name], True
    for full, ent in SENSOR_BY_NAME.items():
        if full.startswith(name + " ("):
            return ent, False
    return None, False


# ---------------------------------------------------------------------------
# The service registry through the real integration setup
# ---------------------------------------------------------------------------
class RecordingServices(FakeServices):
    def __init__(self):
        super().__init__()
        self.kwargs = {}

    def async_register(self, domain, service, handler, schema=None, **kwargs):
        super().async_register(domain, service, handler, schema, **kwargs)
        self.kwargs[service] = kwargs


_svc_hass = FakeHass()
_svc_hass.services = RecordingServices()
_svc_entry = FakeEntry(data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"})
_svc_hass.config_entries.entries.append(_svc_entry)
asyncio.run(integration.async_setup_entry(_svc_hass, _svc_entry))
REGISTERED = dict(_svc_hass.services.async_services().get(const.DOMAIN, {}))
SCHEMAS = {name: _svc_hass.services._schemas[(const.DOMAIN, name)] for name in REGISTERED}
RESPONSES = {name: str(_svc_hass.services.kwargs[name].get("supports_response", "none")) for name in REGISTERED}
LIVE_COORD = _svc_hass.data[const.DOMAIN][_svc_entry.entry_id]


def schema_keys(schema) -> dict:
    """{key: marker} for a voluptuous dict schema."""
    return {getattr(m, "schema", m): m for m in schema.schema}


def accepts(schema, payload: dict) -> bool:
    try:
        schema(payload)
        return True
    except (vol.Invalid, ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Config and options pages rendered through the flows
# ---------------------------------------------------------------------------
def render_options_pages() -> dict:
    pages = {}
    flow_cls = config_flow.HeatPumpOptimizerOptionsFlow
    for step in flow_cls._MENU_LABELS:
        flow = flow_cls(FakeEntry())
        flow.hass = FakeHass()
        result = asyncio.run(getattr(flow, f"async_step_{step}")(None))
        pages[step] = result.get("data_schema")
    return pages


def render_setup_pages() -> dict:
    pages = {}
    flow_cls = config_flow.HeatPumpOptimizerConfigFlow
    for step in ("user", "temperature", "building_describe", "building_extras", "thermal", "zones",
                 "dhw", "weather_sensitivity"):
        flow = flow_cls()
        flow.hass = FakeHass()
        try:
            result = asyncio.run(getattr(flow, f"async_step_{step}")(None))
        except Exception as exc:  # noqa: BLE001
            pages[step] = f"error: {exc}"
            continue
        pages[step] = result.get("data_schema")
    return pages


OPTION_PAGES = render_options_pages()
SETUP_PAGES = render_setup_pages()


def page_fields(schema) -> list[str]:
    if schema is None or isinstance(schema, str):
        return []
    return [k for k in schema_keys(schema) if k != const.CONF_AFTER_SAVE]


def _number_cfg(value):
    if isinstance(value, ha_selector.NumberSelector):
        c = value.config
        return (c.get("min"), c.get("max"), c.get("step"))
    if isinstance(value, vol.All):
        for v in value.validators:
            got = _number_cfg(v)
            if got:
                return got
    return None


def all_number_ranges() -> dict:
    """{conf_key: {page: (min, max, step)}} over every rendered page."""
    out: dict = {}
    for name, schema in {**{f"setup:{k}": v for k, v in SETUP_PAGES.items()},
                         **{f"options:{k}": v for k, v in OPTION_PAGES.items()}}.items():
        if schema is None or isinstance(schema, str):
            continue
        for marker, value in schema.schema.items():
            cfg = _number_cfg(value)
            if cfg:
                out.setdefault(getattr(marker, "schema", marker), {})[name] = cfg
    return out


RANGES = all_number_ranges()


def range_claim(key: str, lo, hi, step=None):
    """Documented range for ``key`` must match every page that offers it."""
    def check():
        pages = RANGES.get(key)
        if not pages:
            return unverifiable(f"{key}: no NumberSelector on any rendered page")
        bad = {p: c for p, c in pages.items()
               if (c[0], c[1]) != (lo, hi) or (step is not None and c[2] != step)}
        return ok(not bad, f"{key}: {pages}", f"selector says {bad}")
    return check


# ---------------------------------------------------------------------------
# Link checks
# ---------------------------------------------------------------------------
def head(url: str):
    if OFFLINE:
        return unverifiable(f"{url}: skipped (D6_OFFLINE=1)")
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "hpo-audit-d6/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except Exception as exc:  # noqa: BLE001
        return unverifiable(f"{url}: {type(exc).__name__}: {exc}")
    return ok(code < 400 or code in (403, 405), f"{url}: HTTP {code}", f"link returns HTTP {code}")


def link_check(url: str):
    return lambda: head(url)


def file_link(rel: str, removed_by_export: bool = False):
    def check():
        exists = (ROOT / rel).exists()
        if not exists and removed_by_export:
            return unverifiable(f"{rel}: absent from the export by design (audit-era file removed)")
        return ok(exists, f"{rel}: exists={exists}", f"{rel} does not exist")
    return check


# ===========================================================================
# Claims
# ===========================================================================

# --- Versions, manifest, hacs, links ----------------------------------------
claim("C001", "VERSION / manifest.json", "VERSION and manifest.json carry the same version",
      lambda: eq(MANIFEST["version"], (ROOT / "VERSION").read_text().strip()))
claim("C002", "README:10,140 / hacs.json", "Home Assistant 2024.1.0 or newer (badge and Requirements) matches hacs.json",
      lambda: eq(HACS["homeassistant"], "2024.1.0") if "2024.1.0" in README else eq("badge", "2024.1.0"))
claim("C003", "README:143 / manifest.json", "numpy and scipy are installed from the manifest",
      lambda: ok(any(r.startswith("numpy") for r in MANIFEST["requirements"]) and any(r.startswith("scipy") for r in MANIFEST["requirements"]),
                 f"requirements={MANIFEST['requirements']} (threadpoolctl is a third requirement the README does not name)"))
claim("C004", "hacs.json / manifest.json", "hacs.json name equals manifest name",
      lambda: eq(HACS["name"], MANIFEST["name"]))
claim("C005", "manifest.json", "documentation URL is reachable", link_check(MANIFEST["documentation"]))
claim("C006", "manifest.json", "issue_tracker URL is reachable", link_check(MANIFEST["issue_tracker"]))
claim("C007", "manifest.json / const.py:8", "the five platforms sensor, binary_sensor, button, climate, switch are the PLATFORMS",
      lambda: eq(sorted(const.PLATFORMS), sorted(["sensor", "binary_sensor", "button", "climate", "switch"])))
claim("C008", "README:19", "strutsfarm/heatpump_optimizer link", link_check("https://github.com/strutsfarm/heatpump_optimizer"))
claim("C009", "README:23", "strutsfarm/ecl110 link", link_check("https://github.com/strutsfarm/ecl110"))
claim("C010", "README:9", "hacs.xyz link", link_check("https://hacs.xyz"))
claim("C011", "README:10", "home-assistant.io link", link_check("https://www.home-assistant.io"))
claim("C012", "README:141", "developer.tibber.com link", link_check("https://developer.tibber.com"))
claim("C013", "README:9-11", "shields.io badge images resolve",
      link_check("https://img.shields.io/badge/HACS-custom-41BDF5.svg"))
claim("C014", "README:26,629,640", "NOTICE, LICENSE and DISCLAIMER.md exist",
      lambda: ok(all((ROOT / f).exists() for f in ("NOTICE", "LICENSE", "DISCLAIMER.md")), "all three exist"))
claim("C015", "README:26", "LICENSE is the verbatim MIT text",
      lambda: ok("MIT License" in (ROOT / "LICENSE").read_text() and "Permission is hereby granted, free of charge" in (ROOT / "LICENSE").read_text(), "MIT header and grant present"))
claim("C016", "README:26 / NOTICE", "the upstream (strutsfarm) attribution is recorded in NOTICE",
      lambda: ok("strutsfarm" in (ROOT / "NOTICE").read_text(), "NOTICE names strutsfarm"))
for i, rel in enumerate(("docs/how-it-works.md", "docs/configuration.md", "docs/dashboard-card.md",
                         "docs/architecture.md", "docs/ecl110.md")):
    claim(f"C0{17 + i}", "README:623-627", f"{rel} exists", file_link(rel))
claim("C022", "README:610,617,628 / how-it-works.md:1279", "docs/backlog.md exists (linked four times)",
      file_link("docs/backlog.md", removed_by_export=True))
claim("C023", "const.py:49 / how-it-works.md:647", "api.open-meteo.com/v1/forecast is reachable",
      link_check(const.OPEN_METEO_FORECAST_URL))
claim("C024", "README:134,258", "entity names are translated: en.json equals strings.json byte for byte",
      lambda: eq((PKG / "translations" / "en.json").read_bytes(), (PKG / "strings.json").read_bytes(), "en.json differs from strings.json"))


def _sv_parity():
    def keys(d, p=""):
        out = set()
        for k, v in d.items():
            out.add(p + k)
            if isinstance(v, dict):
                out |= keys(v, p + k + "/")
        return out
    sv = json.loads((PKG / "translations" / "sv.json").read_text())
    a, b = keys(STRINGS), keys(sv)
    return ok(a == b, f"en keys={len(a)} sv keys={len(b)} en-only={len(a - b)} sv-only={len(b - a)}", "translation key sets differ")


claim("C025", "README:134,258", "Swedish translation carries every key the English one has", _sv_parity)

# --- Entity counts and rosters ----------------------------------------------
claim("C030", "README:53,234 / architecture.md:36 / configuration.md:186", "65 entities in total",
      lambda: eq(len(SENSORS) + len(BINARY) + len(BUTTONS) + len(SWITCHES) + len(CLIMATES), 65))
claim("C031", "README:262 / architecture.md:36,146", "55 sensors", lambda: eq(len(SENSORS), 55))
claim("C032", "README:329", "4 binary sensors", lambda: eq(len(BINARY), 4))
claim("C033", "README:338", "4 buttons", lambda: eq(len(BUTTONS), 4))
claim("C034", "README:53 / architecture.md:36", "1 switch and 1 climate entity",
      lambda: eq((len(SWITCHES), len(CLIMATES)), (1, 1)))
claim("C035", "README:262-323", "the README sensor table has 55 rows", lambda: eq(len(README_SENSOR_ROWS), 55))
claim("C036", "README:329-336", "the README binary-sensor table has 4 rows and matches the roster names",
      lambda: eq(sorted(r[0] for r in README_BINARY_ROWS), sorted(display_name("binary_sensor", b) for b in BINARY)))
claim("C037", "README:338-345", "the README button table has 4 rows and matches the roster names",
      lambda: eq(sorted(r[0] for r in README_BUTTON_ROWS), sorted(display_name("button", b) for b in BUTTONS)))
claim("C038", "README:349 / strings.json", "the switch is named Optimizer Active",
      lambda: eq(display_name("switch", SWITCHES[0]), "Optimizer Active"))
claim("C039", "README:255,325-327", "six sensors are disabled by default: the six named",
      lambda: eq(sorted(display_name("sensor", s) for s in SENSORS if getattr(s, "_attr_entity_registry_enabled_default", True) is False),
                 sorted(["ECL110 Displace", "ECL110 Effective Displace", "Contract Comparison", "DHW Heavy Day Demand",
                         "Valve Target Recommendation", "Compressor Frequency Advisor"])))


def _readme_names_exact():
    missing = [r[0] for r in README_SENSOR_ROWS if r[0] not in SENSOR_BY_NAME]
    resolved = [(n, _readme_name_to_entity(n)[0]) for n in missing]
    unresolved = [n for n, e in resolved if e is None]
    return ok(not missing,
              f"{len(missing)} README names differ from strings.json: {missing}; unresolved={unresolved}",
              "strings.json names carry '(lifetime)' / '(next 24 h)' qualifiers the README table omits: "
              + ", ".join(f"{n} -> {display_name('sensor', e)}" for n, e in resolved if e is not None),
              stale=not unresolved)


claim("C040", "README:259 'the tables below show the English names'", "every README sensor name is the strings.json English name", _readme_names_exact)


def _units():
    bad = []
    for row in README_SENSOR_ROWS:
        ent, _ = _readme_name_to_entity(row[0])
        if ent is None:
            bad.append((row[0], "no entity"))
            continue
        want = UNIT_MAP.get(row[1], row[1])
        got = getattr(ent, "_attr_native_unit_of_measurement", None)
        if want != got:
            bad.append((row[0], row[1], got))
    return ok(not bad, f"{len(README_SENSOR_ROWS) - len(bad)} units agree; mismatches={bad}", f"units differ: {bad}")


claim("C041", "README:267-323 Unit column", "every sensor's unit is as the table says (CUR=SEK on a SEK instance)", _units)


def _diag():
    bad = []
    for row in README_SENSOR_ROWS:
        ent, _ = _readme_name_to_entity(row[0])
        said = "Diagnostic" in row[3]
        is_diag = getattr(ent, "_attr_entity_category", None) == sensor.EntityCategory.DIAGNOSTIC
        if said != is_diag:
            bad.append((row[0], said, is_diag))
    for row, ent in zip(README_BINARY_ROWS, [dict((display_name("binary_sensor", b), b) for b in BINARY)[r[0]] for r in README_BINARY_ROWS]):
        said = "Diagnostic" in row[2]
        is_diag = getattr(ent, "_attr_entity_category", None) == binary_sensor.EntityCategory.DIAGNOSTIC
        if said != is_diag:
            bad.append((row[0], said, is_diag))
    return ok(not bad, f"diagnostic flags agree for all rows; mismatches={bad}", f"category differs: {bad}")


claim("C042", "README Notes 'Diagnostic'", "every sensor/binary sensor marked Diagnostic has EntityCategory.DIAGNOSTIC and no other does", _diag)


def _disabled_notes():
    bad = []
    for row in README_SENSOR_ROWS:
        ent, _ = _readme_name_to_entity(row[0])
        said = "isabled by default" in row[3]
        is_off = getattr(ent, "_attr_entity_registry_enabled_default", True) is False
        if said != is_off:
            bad.append((row[0], said, is_off))
    return ok(not bad, f"mismatches={bad}", f"registry default differs: {bad}")


claim("C043", "README Notes 'Disabled by default'", "the Notes column's disabled-by-default marks match entity_registry_enabled_default", _disabled_notes)


def _unrecorded():
    bad, unmarked = [], []
    for row in README_SENSOR_ROWS:
        ent, _ = _readme_name_to_entity(row[0])
        said = "ot recorded" in row[3]
        has = bool(getattr(ent, "_unrecorded_attributes", None))
        if said and not has:
            bad.append((row[0], getattr(ent, "_unrecorded_attributes", None)))
        if has and not said:
            unmarked.append((row[0], sorted(getattr(ent, "_unrecorded_attributes"))))
    return ok(not bad, f"every marked sensor declares _unrecorded_attributes; marked-but-recorded={bad}; unrecorded-but-unmarked (omission, not a false claim)={unmarked}",
              f"recorder exclusion missing: {bad}")


claim("C044", "README Notes 'Not recorded' / 'forecast not recorded'", "every sensor marked not-recorded declares _unrecorded_attributes", _unrecorded)
claim("C045", "README:283-284 'Timestamp'", "Next/Last Optimization are timestamp sensors",
      lambda: eq([SENSOR_BY_NAME[n]._attr_device_class for n in ("Next Optimization", "Last Optimization")],
                 [sensor.SensorDeviceClass.TIMESTAMP] * 2))
claim("C046", "README:302-307 'Accumulating, for the Energy dashboard'", "the three energy sensors are TOTAL_INCREASING kWh with the ENERGY device class",
      lambda: eq([(SENSOR_BY_NAME[n]._attr_state_class, SENSOR_BY_NAME[n]._attr_device_class) for n in
                  ("Space Heating Energy (lifetime)", "Hot Water Energy (lifetime)", "Total Energy (lifetime)")],
                 [(sensor.SensorStateClass.TOTAL_INCREASING, sensor.SensorDeviceClass.ENERGY)] * 3))
claim("C047", "README:305-307", "the three cost sensors are accumulating (TOTAL, MONETARY)",
      lambda: eq([(SENSOR_BY_NAME[n]._attr_state_class, SENSOR_BY_NAME[n]._attr_device_class) for n in
                  ("Space Heating Cost (lifetime)", "Hot Water Cost (lifetime)", "Total Heating Cost (lifetime)")],
                 [(sensor.SensorStateClass.TOTAL, sensor.SensorDeviceClass.MONETARY)] * 3))
claim("C048", "README:281 / __init__.py RETIRED_ENTITIES", "Solar Irradiance absorbed the former Solar Radiation sensor in v5.0.0",
      lambda: eq(integration.RETIRED_ENTITIES, (("sensor", "solar_radiation"),)))
claim("C049", "README:264 / currency.py", "CUR is the instance currency, SEK when the instance has none",
      lambda: eq((currency.resolve_currency(FakeHass()), currency.resolve_currency(type("H", (), {"config": type("C", (), {"currency": None})()})())), ("SEK", "SEK")))


def _sensor_attrs(name: str, keys: tuple, data=None):
    ent = SENSOR_BY_NAME[name] if data is None else {display_name("sensor", s): s for s in collect(sensor, data)}[name]
    attrs = ent.extra_state_attributes or {}
    missing = [k for k in keys if k not in attrs]
    return ok(not missing, f"{name} attributes={sorted(attrs)[:12]}... missing={missing}", f"attributes lack {missing}")


claim("C050", "README:582-586", "DHW Temperature exposes dhw_in_demand_window, dhw_next_window_in_hours, dhw_required_temperature, dhw_cooling_rate, dhw_cooling_rate_learned, dhw_cooling_samples, dhw_hold_hours",
      lambda: _sensor_attrs("DHW Temperature", ("dhw_in_demand_window", "dhw_next_window_in_hours", "dhw_required_temperature",
                                                "dhw_cooling_rate", "dhw_cooling_rate_learned", "dhw_cooling_samples", "dhw_hold_hours")))
claim("C051", "README:416 / dashboard-card.md:208", "the plan sensors publish manual_override and manual_plan_window_hours=20",
      lambda: eq((SENSOR_BY_NAME["Space Heating Plan (next 24 h)"].extra_state_attributes.get("manual_plan_window_hours"),
                  "manual_override" in SENSOR_BY_NAME["DHW Heating Plan (next 24 h)"].extra_state_attributes),
                 (20, True)))
claim("C052", "dashboard-card.md:527 / README:298", "the plan/solar sensors publish plan_kind space, dhw, solar",
      lambda: eq([SENSOR_BY_NAME[n].extra_state_attributes.get("plan_kind") for n in
                  ("Space Heating Plan (next 24 h)", "DHW Heating Plan (next 24 h)", "Solar Irradiance")], ["space", "dhw", "solar"]))
claim("C053", "README:281", "Solar Irradiance carries the forecast horizon in attributes",
      lambda: _sensor_attrs("Solar Irradiance", ("forecast", "source")))
claim("C054", "README:300", "Measured Power carries the commanded power alongside",
      lambda: _sensor_attrs("Measured Power", ("recommended_power",)))
claim("C055", "README:308,345", "Prediction Accuracy carries the signed bias and the last diagnosis",
      lambda: _sensor_attrs("Prediction Accuracy", ("temperature_bias", "last_diagnosis")))
claim("C056", "README:374", "the frequency view publishes an evidence_exhausted attribute (Compressor Frequency Advisor)",
      lambda: ok("evidence_exhausted" in LIVE_COORD._freq_view(), f"_freq_view keys={sorted(LIVE_COORD._freq_view())}"))
claim("C057", "README:333", "Input Problem carries the evidence and which learners are frozen",
      lambda: ok(all(k in (dict((display_name("binary_sensor", b), b) for b in BINARY)["Input Problem"].extra_state_attributes or {})
                     for k in ("stale_inputs", "learners_frozen")),
                 f"attrs={sorted(dict((display_name('binary_sensor', b), b) for b in BINARY)['Input Problem'].extra_state_attributes or {})}"))
claim("C058", "README:336", "Away Mode carries the return time and recovery state",
      lambda: ok(all(k in (dict((display_name("binary_sensor", b), b) for b in BINARY)["Away Mode"].extra_state_attributes or {})
                     for k in ("return_time", "recovery_active")),
                 f"attrs={sorted(dict((display_name('binary_sensor', b), b) for b in BINARY)['Away Mode'].extra_state_attributes or {})}"))
claim("C059", "README:335", "External Heat Source carries evidence",
      lambda: ok("evidence" in (dict((display_name("binary_sensor", b), b) for b in BINARY)["External Heat Source"].extra_state_attributes or {}),
                 f"attrs={sorted(dict((display_name('binary_sensor', b), b) for b in BINARY)['External Heat Source'].extra_state_attributes or {})}"))


def _unavailable_when(name: str, mutate):
    data = json.loads(json.dumps(DATA))
    mutate(data)
    ents = {display_name("sensor", s): s for s in collect(sensor, data)}
    full = SENSOR_BY_NAME[name].available
    return ok(full and not ents[name].available, f"{name}: available(full)={full} available(feature off)={ents[name].available}",
              f"availability did not follow the feature gate")


def _set(path: str, value):
    def m(d):
        cur = d
        parts = path.split(".")
        for p in parts[:-1]:
            cur = cur[p]
        cur[parts[-1]] = value
    return m


claim("C060", "README:309", "Monthly Peak Power is unavailable unless the capacity tariff is enabled",
      lambda: _unavailable_when("Monthly Peak Power", _set("peak_tariff_enabled", False)))
claim("C061", "README:310", "Solar Surplus Forecast is unavailable unless PV is enabled",
      lambda: _unavailable_when("Solar Surplus Forecast", _set("pv_enabled", False)))
claim("C062", "README:300", "Measured Power is unavailable until a power or energy entity is configured",
      lambda: _unavailable_when("Measured Power", _set("measured_power_available", False)))
claim("C063", "README:301", "Observed COP needs measured power",
      lambda: _unavailable_when("Observed COP", _set("measured_cop", None)))
claim("C064", "README:314", "Contract Comparison needs a configured contract comparison",
      lambda: _unavailable_when("Contract Comparison", _set("contract_comparison", None)))
claim("C065", "README:315", "Power Headroom is unavailable until it can be computed",
      lambda: _unavailable_when("Power Headroom", _set("power_headroom.available", False)))
claim("C066", "README:316", "DHW Setpoint Advisor is unavailable until there is a recommendation",
      lambda: _unavailable_when("DHW Setpoint Advisor", _set("dhw_advisor", None)))
claim("C067", "README:317", "Mixed Hot Water is unavailable without mixed-water data",
      lambda: _unavailable_when("Mixed Hot Water", _set("dhw_mixed", None)))
claim("C068", "README:318", "DHW Heavy Day Demand needs draw statistics",
      lambda: _unavailable_when("DHW Heavy Day Demand", _set("dhw_draw_stats", {})))
claim("C069", "README:321", "Optimization Score is unavailable until the scores have evidence",
      lambda: _unavailable_when("Optimization Score", _set("insight.scores", {"overall": None})))
claim("C070", "README:323", "Compressor Frequency Advisor needs a compressor frequency entity",
      lambda: _unavailable_when("Compressor Frequency Advisor", _set("freq_control.mode", "unconfigured")))
claim("C071", "README:253-254", "every entity exists on a bare payload (unconfigured features report unavailable, not absent)",
      lambda: eq(len(collect(sensor, {"mode": "auto"})), 55))
claim("C072", "README:342", "Optimize Now is unavailable while a run is in flight",
      lambda: eq([b.available for b in collect(button, coordinator=FakeCoordinator(DATA, optimization_running=True))
                  if display_name("button", b) == "Optimize Now"], [False]))
claim("C073", "README:343 / coordinator.py:10538", "Run System Identification: arming reads the sysid option, off by default",
      lambda: ok(const.DEFAULT_SYSID_ENABLED is False and src_has("coordinator.py", r"async_arm_system_identification[\s\S]{0,300}CONF_SYSID_ENABLED"),
                 f"DEFAULT_SYSID_ENABLED={const.DEFAULT_SYSID_ENABLED}; arm() re-reads the option"))
claim("C074", "README:285", "Heat Pump Action values are off, eco, normal, pre_heat, boost (+ comfort while comfort mode holds)",
      lambda: ok(all(src_has("optimizer.py", rf'mode = "{m}"') for m in ("off", "eco", "normal", "pre_heat", "boost"))
                 and src_has("coordinator.py", r'"mode": "comfort"'), "all six mode strings present in the mode mapper"))


def _switch_only_from_off():
    on_from_comfort = FakeCoordinator({**DATA, "mode": "comfort"})
    sw = collect(switch, coordinator=on_from_comfort)[0]
    asyncio.run(sw.async_turn_on())
    from_off = FakeCoordinator({**DATA, "mode": "off"})
    sw2 = collect(switch, coordinator=from_off)[0]
    asyncio.run(sw2.async_turn_on())
    return eq((on_from_comfort.mode_calls, from_off.mode_calls), ([], ["auto"]))


claim("C075", "README:349-350", "Optimizer Active turning on only acts from off", _switch_only_from_off)
claim("C076", "README:352-353", "climate HVAC modes are off, heat, auto and presets auto, comfort, economy, boost",
      lambda: eq((sorted(str(m) for m in CLIMATES[0]._attr_hvac_modes), list(CLIMATES[0]._attr_preset_modes)),
                 (sorted(["off", "heat", "auto"]), ["auto", "comfort", "economy", "boost"])))


def _climate_records_override():
    coord = FakeCoordinator(DATA)
    ent = collect(climate, coordinator=coord)[0]
    asyncio.run(ent.async_set_temperature(temperature=21.5))
    return ok(any(p.startswith("override:") for p in coord.pressed) and coord.target_temperature == 21.5,
              f"pressed={coord.pressed} target={coord.target_temperature}")


claim("C077", "README:354-355", "setting the climate target records a comfort-weight observation", _climate_records_override)
claim("C078", "README:352", "the climate target is the comfort target (coordinator.target_temperature), not the per-step setpoint",
      lambda: eq(CLIMATES[0].target_temperature, 21.0))

# --- Services ----------------------------------------------------------------
claim("C080", "README:389 / configuration.md:535 / architecture.md", "eleven services are registered", lambda: eq(len(REGISTERED), 11))
claim("C081", "README:395-405", "the README service table lists exactly the registered services",
      lambda: eq(sorted(r[0].strip("`") for r in README_SERVICE_ROWS), sorted(REGISTERED)))
claim("C082", "services.yaml", "services.yaml describes exactly the registered services", lambda: eq(sorted(SERVICES_YAML), sorted(REGISTERED)))
claim("C083", "README:390 / configuration.md:547,565", "set_thermal_parameters has 28 fields",
      lambda: eq(len(schema_keys(SCHEMAS["set_thermal_parameters"])), 28))
claim("C084", "configuration.md:548,592-595", "simulate_plan has 11 optional fields",
      lambda: eq((len(schema_keys(SCHEMAS["simulate_plan"])), all(isinstance(m, vol.Optional) for m in schema_keys(SCHEMAS["simulate_plan"]).values())), (11, True)))
claim("C085", "configuration.md:549,600", "apply_schedule has 5 schedule fields + entry_id",
      lambda: eq(sorted(schema_keys(SCHEMAS["apply_schedule"])), sorted(["day_start_hour", "day_end_hour", "dhw_windows", "comfort_temp_day", "dhw_min_temperature", "entry_id"])))
claim("C086", "configuration.md:535-541", "seven services accept entry_id; the other four act on every entry",
      lambda: eq(sorted(n for n, s in SCHEMAS.items() if "entry_id" in schema_keys(s)),
                 sorted(["apply_schedule", "assign_entity", "apply_topology", "apply_manual_plan", "clear_manual_plan", "restore_learned_snapshot", "diagnose_interval"])))


def _responses():
    want = {}
    for row in README_SERVICE_ROWS:
        want[row[0].strip("`")] = {"Always": "only", "Optional": "optional", "—": "none"}[row[2]]
    bad = {n: (want[n], RESPONSES[n]) for n in want if want[n] != RESPONSES[n]}
    return ok(not bad, f"README Returns column vs supports_response: mismatches={bad}", f"differs: {bad}")


claim("C087", "README Returns column / configuration.md:543-555", "Returns: simulate_plan always, run/set_mode/set_thermal none, the rest optional", _responses)
claim("C088", "README:396 / services.yaml set_mode / const.OPERATION_MODES", "set_mode accepts auto, comfort, economy, boost, off",
      lambda: eq((sorted(const.OPERATION_MODES), sorted(SERVICES_YAML["set_mode"]["fields"]["mode"]["selector"]["select"]["options"]),
                  all(accepts(SCHEMAS["set_mode"], {"mode": m}) for m in const.OPERATION_MODES), accepts(SCHEMAS["set_mode"], {"mode": "eco"})),
                 (sorted(["auto", "comfort", "economy", "boost", "off"]), sorted(["auto", "comfort", "economy", "boost", "off"]), True, False)))


def _yaml_fields_vs_schema():
    bad = {}
    for name, spec in SERVICES_YAML.items():
        yf = set((spec or {}).get("fields", {}) or {})
        sk = set(schema_keys(SCHEMAS[name]))
        if yf != sk:
            bad[name] = {"yaml_only": sorted(yf - sk), "schema_only": sorted(sk - yf)}
    return ok(not bad, f"field sets agree for all services; mismatches={bad}", f"differs: {bad}")


claim("C089", "services.yaml fields", "every services.yaml field is a schema key and vice versa", _yaml_fields_vs_schema)


def _yaml_required():
    bad = []
    for name, spec in SERVICES_YAML.items():
        markers = schema_keys(SCHEMAS[name])
        for f, fs in ((spec or {}).get("fields", {}) or {}).items():
            req = bool((fs or {}).get("required", False))
            is_req = isinstance(markers[f], vol.Required)
            if req != is_req:
                bad.append((name, f, req, is_req))
    return ok(not bad, f"required flags agree; mismatches={bad}", f"differs: {bad}")


claim("C090", "services.yaml required:", "the required flags match vol.Required in the schemas", _yaml_required)


def _yaml_example(value):
    if isinstance(value, str) and value.strip().startswith("["):
        return json.loads(value)
    return value


def _yaml_examples():
    """Each example is validated together with the service's other required examples."""
    bad = []
    n = 0
    for name, spec in SERVICES_YAML.items():
        fields = (spec or {}).get("fields", {}) or {}
        required = {f: _yaml_example(fs["example"]) for f, fs in fields.items()
                    if fs and fs.get("required") and "example" in fs}
        for f, fs in fields.items():
            if fs and "example" in fs:
                n += 1
                payload = {**required, f: _yaml_example(fs["example"])}
                if not accepts(SCHEMAS[name], payload):
                    bad.append((name, f, fs["example"]))
    return ok(not bad, f"{n} examples validated; rejected={bad}", f"examples rejected by their own schema: {bad}")


claim("C091", "services.yaml examples", "every services.yaml example validates through its voluptuous schema", _yaml_examples)


def _selector_within_schema():
    bad = []
    n = 0
    for name, spec in SERVICES_YAML.items():
        for f, fs in ((spec or {}).get("fields", {}) or {}).items():
            num = ((fs or {}).get("selector") or {}).get("number")
            if not num:
                continue
            n += 1
            for bound in ("min", "max"):
                if not accepts(SCHEMAS[name], {f: num[bound]}):
                    bad.append((name, f, bound, num[bound]))
    return ok(not bad, f"{n} number selectors; bounds rejected by schema: {bad}", f"selector bound outside schema: {bad}")


claim("C092", "services.yaml selectors", "every number selector's min and max are accepted by the schema", _selector_within_schema)
claim("C093", "services.yaml wind_sensitivity_factor (example 0.15, '0.15 means 15% more heat loss per m/s')",
      "the wind example/description matches the shipped default",
      lambda: eq(SERVICES_YAML["set_thermal_parameters"]["fields"]["wind_sensitivity_factor"]["example"], const.DEFAULT_WIND_SENSITIVITY,
                 f"default is {const.DEFAULT_WIND_SENSITIVITY} (3 %/m/s) since the 0.15 default was replaced; the example still shows the old value", stale=True))

DOC_RANGES = {
    "house_thermal_mass": (0.01, 200), "slab_thermal_mass": (0.01, 200), "house_heat_loss_coefficient": (0.01, 10),
    "slab_heat_transfer": (0.01, 50), "heat_pump_cop_nominal": (1.0, 8.0), "upper_floor_thermal_mass": (0.01, 200),
    "lower_floor_thermal_mass": (0.01, 200), "inter_zone_heat_transfer": (0.01, 50), "radiator_power_fraction": (0, 1),
    "window_area": (0.01, 500), "solar_heat_gain_coefficient": (0, 1), "dhw_tank_volume": (0.01, 2000),
    "dhw_setpoint": (30, 75), "dhw_min_temperature": (10, 70), "dhw_daily_consumption": (0.01, 2000),
    "dhw_cooling_rate": (0.01, 5), "buffer_cooling_rate": (0.01, 50), "dhw_idle_min_temperature": (5, 60),
    "dhw_legionella_temperature": (55, 75), "dhw_legionella_interval_days": (0.01, 60), "wind_sensitivity_factor": (0, 1),
    "rain_heat_loss_multiplier": (1, 2), "ecl110_pid_time_constant_hours": (0.01, 24), "ecl110_displace_min": (-30, 0),
    "ecl110_displace_max": (0, 30),
}


def _doc_ranges():
    s = SCHEMAS["set_thermal_parameters"]
    bad = []
    for f, (lo, hi) in DOC_RANGES.items():
        eps = 1e-3 if abs(lo) < 1 or abs(hi) < 1 else 0.01
        good = accepts(s, {f: lo}) and accepts(s, {f: hi}) and not accepts(s, {f: lo - eps}) and not accepts(s, {f: hi + eps})
        if not good:
            bad.append(f)
    return ok(not bad, f"{len(DOC_RANGES)} documented ranges checked at both bounds; wrong={bad}", f"ranges differ: {bad}")


claim("C094", "configuration.md:571-588", "the 25 documented set_thermal_parameters ranges are the schema's bounds", _doc_ranges)
claim("C095", "configuration.md:607-616", "assign_entity accepts exactly the 21 documented keys",
      lambda: eq(sorted(topology.ASSIGNABLE_KEYS), sorted(["outdoor_temp_entity", "solar_radiation_entity", "pv_production_entity", "indoor_temp_entity",
                 "lower_floor_temp_entity", "floor_return_temp_entity", "heat_pump_switch_entity", "heat_pump_power_entity", "heat_pump_energy_entity",
                 "house_power_entity", "heat_pump_mode_entity", "heat_pump_defrost_entity", "heat_pump_online_entity", "heat_pump_fault_entity",
                 "buffer_tank_temp_entity", "mixing_valve_target_entity", "dhw_temp_entity", "external_heat_entity", "wood_tank_top_entity",
                 "wood_tank_bottom_entity", "valve_outlet_temp_entity"])))
claim("C096", "configuration.md:523-529,622", "four selectable layouts; slab_shunt is recorded but not selectable",
      lambda: eq((sorted(k for k, v in topology.LAYOUTS.items() if v.selectable), "slab_shunt" in topology.LAYOUTS and not topology.LAYOUTS["slab_shunt"].selectable,
                  accepts(SCHEMAS["apply_topology"], {"layout": "slab_shunt"})),
                 (sorted(["no_valve", "single_tank_valve", "two_tank_4way", "valve_upper_direct_slab"]), True, False)))
claim("C097", "README:400 / services.yaml apply_manual_plan / const.py", "manual plans pin up to 20 hours",
      lambda: eq(const.MANUAL_PLAN_WINDOW_HOURS, 20))
claim("C098", "README:411-413", "apply_manual_plan: an omitted channel stays automatic, an explicit [] arrives as []",
      lambda: eq((SCHEMAS["apply_manual_plan"]({}).get("dhw_slots", "absent"), SCHEMAS["apply_manual_plan"]({"dhw_slots": []})["dhw_slots"]), ("absent", [])))
claim("C099", "services.yaml set_mode economy / configuration.md:561-562", "economy widens the floor by 1.5 K, never below 15 °C",
      lambda: eq((const.ECONOMY_MIN_TEMP_WIDENING, const.ECONOMY_ABSOLUTE_FLOOR), (1.5, 15.0)))
claim("C100", "README:398 / const.py:482", "simulate_plan is rate-limited (3 s minimum interval)",
      lambda: eq(const.SIMULATE_MIN_INTERVAL_SECONDS, 3.0))
claim("C101", "configuration.md:594", "simulate_plan day_start_hour 0–23 and day_end_hour 0–24",
      lambda: eq((accepts(SCHEMAS["simulate_plan"], {"day_start_hour": 23}), accepts(SCHEMAS["simulate_plan"], {"day_start_hour": 24}),
                  accepts(SCHEMAS["simulate_plan"], {"day_end_hour": 24}), accepts(SCHEMAS["simulate_plan"], {"day_end_hour": 25})), (True, False, True, False)))
claim("C102", "strings.json", "strings.json carries no services section (service names come from services.yaml)",
      lambda: eq("services" in STRINGS, False))

# --- Defaults against const.py -----------------------------------------------
DEFAULTS = [
    ("C110", "README:192 / configuration.md:79", "target 21 °C", "DEFAULT_TARGET_TEMP", 21.0),
    ("C111", "configuration.md:80-81", "min 19 / max 23 °C", ("DEFAULT_MIN_TEMP", "DEFAULT_MAX_TEMP"), (19.0, 23.0)),
    ("C112", "README:193 / configuration.md:82-83", "day 21 °C, night 19.5 °C", ("DEFAULT_COMFORT_TEMP_DAY", "DEFAULT_COMFORT_TEMP_NIGHT"), (21.0, 19.5)),
    ("C113", "README:194 / configuration.md:84-85", "day runs 07:00–22:00", ("DEFAULT_DAY_START_HOUR", "DEFAULT_DAY_END_HOUR"), (7, 22)),
    ("C114", "README:218 / configuration.md:173", "DHW windows default 06:00-08:30, 17:00-22:00", "DEFAULT_DHW_WINDOWS", "06:00-08:30, 17:00-22:00"),
    ("C115", "README:222 / how-it-works.md:575", "anti-legionella on by default, 60 °C every 7 days", ("DEFAULT_DHW_LEGIONELLA_ENABLED", "DEFAULT_DHW_LEGIONELLA_TEMP", "DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS"), (True, 60.0, 7.0)),
    ("C116", "README:227 / configuration.md:183-184 / how-it-works.md:291-295", "wind 3 %/(m/s), rain +15 %", ("DEFAULT_WIND_SENSITIVITY", "DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER"), (0.03, 1.15)),
    ("C117", "README:235,431 / how-it-works.md:47", "optimization interval 30 min", "DEFAULT_OPTIMIZATION_INTERVAL", 30),
    ("C118", "README:526 / configuration.md:136 / how-it-works.md:130", "comfort_weight default 5, price weight 1.0", ("DEFAULT_COMFORT_WEIGHT", "DEFAULT_PRICE_WEIGHT"), (5.0, 1.0)),
    ("C119", "README:49,86 / architecture.md / how-it-works.md:1154", "weekly snapshots, last 8 kept", ("RING_SIZE", "SNAPSHOT_INTERVAL_DAYS"), (8, 7.0), snapshots),
    ("C120", "how-it-works.md:1157", "drift alarm after five consecutive days out of band", "BIAS_TRIP_DAYS", 5, snapshots),
    ("C121", "how-it-works.md:1176", "the CUSUM statistic is capped at 1.5× the threshold", "STAT_CAP_FACTOR", 1.5, drift),
    ("C122", "README:85 / configuration.md:453 / ecl110.md:39 / how-it-works.md:1117", "heat-curve correction cool-only, at most 0.5 K per week, clamped [−4, 0]", ("MAX_DOWN_PER_WEEK", "BIAS_MIN", "BIAS_MAX"), (0.5, -4.0, 0.0), curve_learning),
    ("C123", "README:368 / configuration.md:341", "frequency control writes at most once per five minutes", "FREQ_WRITE_MIN_INTERVAL_S", 300.0, freq_control),
    ("C124", "README:369 / configuration.md:341", "three divergent ticks stand the controller down", "FREQ_WATCHDOG_TICKS", 3, freq_control),
    ("C125", "README:444,478 / how-it-works.md:78,758", "peak guard: two agreeing samples engage, two clear", "HYSTERESIS_SAMPLES", 2, power_guard),
    ("C126", "configuration.md:167-170 / how-it-works.md:439", "DHW tank 200 L, setpoint 55, minimum 45, 150 L/day", ("DEFAULT_DHW_TANK_VOLUME", "DEFAULT_DHW_SETPOINT", "DEFAULT_DHW_MIN_TEMP", "DEFAULT_DHW_DAILY_CONSUMPTION"), (200.0, 55.0, 45.0, 150.0)),
    ("C127", "configuration.md:171,174 / how-it-works.md:543,557", "tank cooling 0.3 °C/h clamped 0.05–3.0; idle minimum 20 °C", ("DEFAULT_DHW_COOLING_RATE", "DHW_COOLING_RATE_MIN", "DHW_COOLING_RATE_MAX", "DEFAULT_DHW_IDLE_MIN_TEMP"), (0.3, 0.05, 3.0, 20.0)),
    ("C128", "configuration.md:169", "the DHW minimum must sit 5 °C below the setpoint", "DHW_MIN_TEMP_SETPOINT_MARGIN", 5.0),
    ("C129", "configuration.md:127-133 / how-it-works.md:276", "house 10 kWh/°C, 0.15 kW/°C, slab 5 / 0.8, COP 3.5, 5 kW / 1 kW", ("DEFAULT_HOUSE_THERMAL_MASS", "DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT", "DEFAULT_SLAB_THERMAL_MASS", "DEFAULT_SLAB_HEAT_TRANSFER", "DEFAULT_HEAT_PUMP_COP_NOMINAL", "DEFAULT_HEAT_PUMP_MAX_POWER", "DEFAULT_HEAT_PUMP_MIN_POWER"), (10.0, 0.15, 5.0, 0.8, 3.5, 5.0, 1.0)),
    ("C130", "configuration.md:142-149 / how-it-works.md:274-276", "two-zone 3/8 kWh/°C, 0.08/0.07 kW/°C, 0.5 inter-zone, 0.4 radiator share, 0.5 area ratio, 35 L buffer", ("DEFAULT_UPPER_FLOOR_THERMAL_MASS", "DEFAULT_LOWER_FLOOR_THERMAL_MASS", "DEFAULT_UPPER_FLOOR_HEAT_LOSS", "DEFAULT_LOWER_FLOOR_HEAT_LOSS", "DEFAULT_INTER_ZONE_TRANSFER", "DEFAULT_RADIATOR_POWER_FRACTION", "DEFAULT_UPPER_FLOOR_AREA_RATIO", "DEFAULT_BUFFER_TANK_VOLUME"), (3.0, 8.0, 0.08, 0.07, 0.5, 0.4, 0.5, 35.0)),
    ("C131", "configuration.md:150-152 / how-it-works.md:310-313", "solar: 10 m², orientation 0.7, SHGC 0.7, 40 % upper", ("DEFAULT_WINDOW_AREA", "DEFAULT_SOLAR_ORIENTATION_FACTOR", "DEFAULT_SOLAR_HEAT_GAIN_COEFF", "DEFAULT_SOLAR_UPPER_FRACTION"), (10.0, 0.7, 0.7, 0.4)),
    ("C132", "configuration.md:149,355-356 / how-it-works.md:419", "buffer store threshold 100 L, max buffer temperature 70 °C", ("BUFFER_STORE_MIN_VOLUME", "DEFAULT_BUFFER_MAX_TEMP"), (100.0, 70.0)),
    ("C133", "configuration.md:285-287", "capacity tariff 45 per kW, 3 peaks, 60-minute window, off by default", ("DEFAULT_PEAK_TARIFF_PRICE", "DEFAULT_PEAK_TARIFF_COUNT", "DEFAULT_PEAK_TARIFF_WINDOW", "DEFAULT_PEAK_TARIFF_ENABLED"), (45.0, 3, 60, False)),
    ("C134", "configuration.md:292-296", "main fuse 0 A (unconfigured), 3 phases, guards off, margin 0.5 kW", ("DEFAULT_MAIN_FUSE_A", "DEFAULT_MAIN_FUSE_PHASES", "DEFAULT_FUSE_GUARD_ENABLED", "DEFAULT_PEAK_GUARD_ENABLED", "DEFAULT_PEAK_GUARD_MARGIN_KW"), (0, 3, False, False, 0.5)),
    ("C135", "configuration.md:314-318", "away mode off, 16 °C, DHW minimum 20 °C", ("DEFAULT_AWAY_ENABLED", "DEFAULT_AWAY_TEMPERATURE", "DEFAULT_AWAY_DHW_MIN_TEMP"), (False, 16.0, 20.0)),
    ("C136", "configuration.md:438-441", "external heat detection off, 1.5 °C/h, 90 min decay", ("DEFAULT_EXTERNAL_HEAT_ENABLED", "DEFAULT_EXTERNAL_HEAT_MIN_RISE", "DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES"), (False, 1.5, 90.0)),
    ("C137", "configuration.md:445 / how-it-works.md:771-773", "outage: gap > 90 min, 2-hour recovery, hot water queues 45 min", ("OUTAGE_GAP_MINUTES", "OUTAGE_RECOVERY_HOURS", "OUTAGE_DHW_DELAY_MINUTES", "DEFAULT_OUTAGE_RECOVERY_ENABLED"), (90.0, 2.0, 45.0, False)),
    ("C138", "configuration.md:232-234,270 / how-it-works.md:1137,1143", "confidence margin cap 0.8 °C; mould guard 80 % RH, fRsi 0.75", ("CONFIDENCE_MARGIN_CAP_C", "MOLD_SURFACE_RH_LIMIT", "DEFAULT_THERMAL_BRIDGE_FRSI", "DEFAULT_MOLD_GUARD_ENABLED"), (0.8, 0.8, 0.75, False)),
    ("C139", "configuration.md:446,450-451 / how-it-works.md:1114-1115,1128", "open-window relax 1 °C; capacity floor 60 %; solar aperture [0.3, 2.0]", ("OPEN_WINDOW_RELAX_C", "CAPACITY_FLOOR_FRACTION", "SOLAR_APERTURE_MIN", "SOLAR_APERTURE_MAX"), (1.0, 0.6, 0.3, 2.0)),
    ("C140", "configuration.md:449 / how-it-works.md:301", "snow halves solar gain for two days", ("SNOW_ROOF_DAMPING", "SNOW_ROOF_DAYS"), (0.5, 2.0)),
    ("C141", "configuration.md:268,271-273", "cycling cost 0, replacement cost 0, rated starts 100 000, wear autotune off", ("DEFAULT_CYCLING_COST", "DEFAULT_COMPRESSOR_REPLACEMENT_COST", "DEFAULT_COMPRESSOR_RATED_STARTS", "DEFAULT_WEAR_AUTOTUNE_ENABLED"), (0.0, 0.0, 100000, False)),
    ("C142", "configuration.md:421-424", "PV off, 0 kWp, efficiency 0.80, export price 0", ("DEFAULT_PV_ENABLED", "DEFAULT_PV_PEAK_KW", "DEFAULT_PV_EFFICIENCY", "DEFAULT_PV_EXPORT_PRICE"), (False, 0.0, 0.80, 0.0)),
    ("C143", "configuration.md:243-253 / how-it-works.md:534,587,612", "inlet 10 °C, amplitude 0, greywater 0, legionella min interval 5 d, shower 8 L/min, VVC lead 20 min", ("DEFAULT_DHW_INLET_TEMP", "DEFAULT_DHW_INLET_SEASONAL_AMPLITUDE", "DEFAULT_GREYWATER_RECOVERY", "DEFAULT_DHW_LEGIONELLA_MIN_INTERVAL_DAYS", "DEFAULT_SHOWER_FLOW_LPM", "DEFAULT_VVC_LEAD_MINUTES"), (10.0, 0.0, 0.0, 5.0, 8.0, 20)),
    ("C144", "how-it-works.md:988,1047", "COP scale bounded [0.5, 1.6]; tracking-error gate 30 %", ("COP_SCALE_MIN", "COP_SCALE_MAX", "COP_TRACKING_ERROR_GATE"), (0.5, 1.6, 0.3)),
    ("C145", "configuration.md:436-437 / how-it-works.md:909-910", "staleness on by default, slack 0.5–10; ages 60 indoor/tank, 180 outdoor, 30 power", ("DEFAULT_STALENESS_ENABLED", "STALENESS_SCALE_MIN", "STALENESS_SCALE_MAX"), (True, 0.5, 10.0)),
    ("C146", "configuration.md:444", "price prior on by default", "DEFAULT_PRICE_PRIOR_ENABLED", True),
    ("C147", "configuration.md:442-443 / README:239", "comfort learning and system identification off by default", ("DEFAULT_COMFORT_LEARNING_ENABLED", "DEFAULT_SYSID_ENABLED"), (False, False)),
    ("C148", "ecl110.md:83-90 / configuration.md:462-469", "ECL110 defaults: set/command/state topics, QoS 1, retain off, ±20, 1.5 h", ("DEFAULT_ECL110_DISPLACE_SET_TOPIC", "DEFAULT_ECL110_COMMAND_TOPIC", "DEFAULT_ECL110_STATE_TOPIC", "DEFAULT_ECL110_QOS", "DEFAULT_ECL110_RETAIN", "DEFAULT_ECL110_DISPLACE_MIN", "DEFAULT_ECL110_DISPLACE_MAX", "DEFAULT_ECL110_PID_TIME_CONSTANT"), ("ecl110/flow_temp_control/displace/set", "ecl110/command", "ecl110/flow_temp_control/displace", 1, False, -20.0, 20.0, 1.5)),
    ("C149", "ecl110.md:33-35", "the peak guard lowers the displace by 2 °C while suppressing", "PEAK_GUARD_DISPLACE_NUDGE_C", 2.0),
    ("C150", "how-it-works.md:827,850 / README:98", "external heat promised at most two hours ahead; wood tank settled up to 95 °C", ("EXTERNAL_HEAT_FORECAST_MAX_HOURS", "WOOD_TANK_MAX_TEMP"), (2.0, 95.0)),
    ("C151", "how-it-works.md:686-687", "price shape damped below five days, factors guard-railed to [0.2, 3.0]", ("SHAPE_CONFIDENCE_DAYS", "SHAPE_MIN", "SHAPE_MAX"), (5, 0.2, 3.0), price_model),
    ("C152", "how-it-works.md:1007,1025", "defrost derate = 1 − duty × 1.5, clamped at 1.0", ("DEFROST_LOSS_MULTIPLIER", "DERATE_MAX"), (1.5, 1.0), defrost),
    ("C153", "how-it-works.md:706", "a fee component above 10 SEK/kWh is flagged", "IMPLAUSIBLE_FEE_SEK_PER_KWH", 10.0, grid_fee),
    ("C154", "how-it-works.md:886-888", "recovery starts a full duration plus an hour before return, capped at 24 h", ("RECOVERY_MARGIN_HOURS", "MAX_RECOVERY_HOURS"), (1.0, 24.0), away),
    ("C155", "how-it-works.md:97 / optimizer.py:91", "the congestion premium searches a 6-hour window", "_DHW_REFILL_WINDOW_HOURS", 6.0, optimizer),
    ("C156", "how-it-works.md:108-110", "the space solve keeps two starts", "_MULTI_START_SOLVES", 2, optimizer),
    ("C157", "how-it-works.md:48,72", "24-hour horizon on a 15-minute grid",
     None, None),
    ("C158", "how-it-works.md:598-601 / README:106", "heavy-day target is the 90th percentile per window", None, None),
    ("C159", "configuration.md:632-633 / how-it-works.md:585 / const.py:636", "legionella credit is hold-verified (20 minutes)", "DHW_LEGIONELLA_HOLD_MINUTES", 20.0),
    ("C160", "README:99 / const.py:225", "the DHW coil is off by default with a fixed 0.5 effectiveness", ("DEFAULT_DHW_WOOD_COIL_ENABLED", "DHW_WOOD_COIL_EFFECTIVENESS"), (False, 0.5)),
]
for row in DEFAULTS:
    cid, source, text, names, expected = row[:5]
    module = row[5] if len(row) > 5 else const
    if names is None:
        continue
    if isinstance(names, tuple):
        claim(cid, source, text, (lambda n=names, e=expected, m=module: eq(tuple(getattr(m, x) for x in n), e)))
    else:
        claim(cid, source, text, (lambda n=names, e=expected, m=module: eq(getattr(m, n), e)))
claim("C157", "how-it-works.md:48,72", "24-hour horizon on a 15-minute grid",
      lambda: eq((optimizer.OptimizationConfig().horizon_hours, optimizer.OptimizationConfig().time_step_minutes, optimizer.OptimizationConfig().n_steps), (24.0, 15.0, 96)))
claim("C158", "how-it-works.md:598-601 / README:106", "heavy-day target is the 90th percentile per window",
      lambda: eq(inspect.signature(dhw_draws.DrawStatistics.quantile if hasattr(dhw_draws, "DrawStatistics") else
                                   next(getattr(dhw_draws, n) for n in dir(dhw_draws) if hasattr(getattr(dhw_draws, n), "quantile")).quantile).parameters["q"].default, 0.9))
claim("C161", "how-it-works.md:909-910", "input ages: indoor 60, DHW 60, outdoor 180, power 30 minutes",
      lambda: eq(tuple(const.INPUT_MAX_AGE_MINUTES[k] for k in (const.CONF_INDOOR_TEMP_ENTITY, const.CONF_DHW_TEMP_ENTITY, const.CONF_OUTDOOR_TEMP_ENTITY, const.CONF_POWER_ENTITY)), (60.0, 60.0, 180.0, 30.0)))

# --- Behaviours driven directly -----------------------------------------------


def _watchdog():
    w = freq_control.FrequencyWatchdog()
    w.note_command(50.0)
    trips = [w.note_report(80.0, active=True) for _ in range(4)]  # first is the grace tick
    w2 = freq_control.FrequencyWatchdog()
    w2.note_command(50.0)
    w2.note_report(80.0, active=True)
    w2.note_report(80.0, active=True)
    w2.note_report(80.0, active=True)
    before = w2.strikes
    w2.note_report(0.0, active=False)  # idle: not divergence
    return ok(trips == [False, False, False, True] and before == 2 and w2.strikes == 0 and not w2.tripped,
              f"trip sequence={trips} (grace, strike, strike, trip); idle tick reset strikes {before}->{w2.strikes}")


claim("C170", "README:368-371", "the watchdog trips on the third consecutive active divergent tick; idle ticks are not divergence", _watchdog)


def _guard():
    g = power_guard.GuardState()
    t = datetime(2026, 2, 1, 12, 0)
    seq = []
    for i, proj in enumerate((9.0, 9.0, 3.0, 3.0)):
        g.update(t + timedelta(seconds=20 * i), "w", proj, 8.0, 0.5, floor_hold=False)
        seq.append(g.suppressing)
    return eq(seq, [False, True, True, False])


claim("C171", "README:444,478 / how-it-works.md:758", "the peak guard engages on the second crossing sample and releases on the second clear one", _guard)


def _curve():
    c = curve_learning.CurveLearner()
    t0 = datetime(2026, 1, 1, 12, 0)
    for d in range(7):
        c.record_day(t0 + timedelta(days=d), 1.0)
    week = c.bias
    c.record_day(t0 + timedelta(days=7), -0.1)
    return ok(-0.5 <= week < 0 and c.bias == 0.0 and c.resets == 1,
              f"bias after 7 comfortable days={week:.2f} K (≥ −0.5); after one miss={c.bias} resets={c.resets}")


claim("C172", "README:85 / how-it-works.md:1117", "the curve bias moves at most 0.5 K per week and resets to 0 on a comfort miss", _curve)


def _ring():
    r = snapshots.SnapshotRing()
    t0 = datetime(2026, 1, 1)
    for i in range(12):
        r.take(t0 + timedelta(days=7 * i), {"x": {"v": i}}, {"temperature_bias": 0.0}, True)
    return eq((len(r.snapshots), r.snapshots[-1]["learners"]["x"]["v"]), (8, 11))


claim("C173", "README:86 / how-it-works.md:1154", "the snapshot ring keeps the last eight", _ring)
claim("C174", "README:389 / architecture.md", "13 options pages: 6 on the first menu and 7 behind Advanced settings, one read-only",
      lambda: eq((len(config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS), len(config_flow.HeatPumpOptimizerOptionsFlow._TOP_MENU),
                  len(config_flow.HeatPumpOptimizerOptionsFlow._ADVANCED_MENU), page_fields(OPTION_PAGES["setup_overview"])), (13, 6, 7, [])))
claim("C175", "README:500-517 / configuration.md:200-217", "the README/configuration page names are the menu labels",
      lambda: eq(sorted(config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS.values()),
                 sorted(["Your system, as configured", "Comfort and temperatures", "Hot water", "Savings vs comfort", "Grid costs", "Away and holiday mode",
                         "Sensors and entities", "Heating system and heat storage", "Building type and emitters", "Thermal model (expert)", "Solar panels",
                         "Self-learning and diagnostics", "Heat curve control (ECL110)"])))
claim("C176", "ecl110.md:76 / configuration.md:68", "all eight ECL110 settings live on the Heat curve page",
      lambda: eq(len(page_fields(OPTION_PAGES["heat_curve"])), 8))
claim("C177", "configuration.md:322-325", "Sensors and entities has 22 fields",
      lambda: eq(len(page_fields(OPTION_PAGES["entities"])), 22))
claim("C178", "configuration.md:227-228", "Comfort and temperatures has the seven setup fields plus three more (10)",
      lambda: eq(len(page_fields(OPTION_PAGES["comfort"])), 10))
claim("C179", "configuration.md:238-239", "Hot water has the eleven setup fields plus twelve more (23)",
      lambda: eq(len(page_fields(OPTION_PAGES["hot_water"])), 23))
claim("C180", "configuration.md:13,51-52 / README:185", "only the Tibber token and the weather entity are required without a default",
      lambda: eq(sorted(k for k, m in schema_keys(SETUP_PAGES["user"]).items() if isinstance(m, vol.Required) and m.default is vol.UNDEFINED),
                 sorted([const.CONF_TIBBER_TOKEN, const.CONF_WEATHER_ENTITY])))
claim("C181", "configuration.md:68-70 / README:603 / ecl110.md:77", "no ECL110 field is asked at initial setup",
      lambda: eq([k for p in SETUP_PAGES.values() if not isinstance(p, (str, type(None))) for k in schema_keys(p) if k.startswith("ecl110")], []))
claim("C182", "configuration.md:77-85", "temperature ranges: target 15–28/0.5, min 14–25, max 18–28, day 16–26, night 15–24, start 0–12, end 18–23",
      lambda: ok(all(range_claim(k, lo, hi, st)()[1] == "true" for k, lo, hi, st in (
          (const.CONF_TARGET_TEMP, 15, 28, 0.5), (const.CONF_MIN_TEMP, 14, 25, None), (const.CONF_MAX_TEMP, 18, 28, None),
          (const.CONF_COMFORT_TEMP_DAY, 16, 26, None), (const.CONF_COMFORT_TEMP_NIGHT, 15, 24, None),
          (const.CONF_DAY_START_HOUR, 0, 12, None), (const.CONF_DAY_END_HOUR, 18, 23, None))),
          f"{ {k: RANGES.get(k) for k in (const.CONF_TARGET_TEMP, const.CONF_MIN_TEMP, const.CONF_MAX_TEMP, const.CONF_COMFORT_TEMP_DAY, const.CONF_COMFORT_TEMP_NIGHT, const.CONF_DAY_START_HOUR, const.CONF_DAY_END_HOUR)} }",
          "a selector range differs (see observed)"))
RANGE_CLAIMS = [
    ("C183", "configuration.md:104", const.CONF_HEATED_AREA, 20, 1000, 5),
    ("C184", "configuration.md:112-114", const.CONF_HEAT_PUMP_COP_NOMINAL, 1.5, 6.0, 0.1),
    ("C185", "configuration.md:113", const.CONF_HEAT_PUMP_MAX_POWER, 1, 20, 0.5),
    ("C186", "configuration.md:114", const.CONF_HEAT_PUMP_MIN_POWER, 0, 10, 0.5),
    ("C187", "configuration.md:127", const.CONF_HOUSE_THERMAL_MASS, 0.5, 80, 0.5),
    ("C188", "configuration.md:128", const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT, 0.01, 1.0, 0.01),
    ("C189", "configuration.md:129", const.CONF_SLAB_THERMAL_MASS, 0.1, 60, 0.5),
    ("C190", "configuration.md:130", const.CONF_SLAB_HEAT_TRANSFER, 0.02, 5.0, 0.1),
    ("C191", "configuration.md:134,267", const.CONF_OPTIMIZATION_INTERVAL, 10, 120, 5),
    ("C192", "configuration.md:135,265", const.CONF_PRICE_WEIGHT, 0.1, 10, 0.1),
    ("C193", "configuration.md:136,266", const.CONF_COMFORT_WEIGHT, 0.1, 20, 0.1),
    ("C194", "configuration.md:142-143", const.CONF_UPPER_FLOOR_THERMAL_MASS, 0.25, 60, None),
    ("C195", "configuration.md:144-145", const.CONF_UPPER_FLOOR_HEAT_LOSS, 0.001, 1.0, None),
    ("C196", "configuration.md:146", const.CONF_INTER_ZONE_TRANSFER, 0.0, 3.0, None),
    ("C197", "configuration.md:147", const.CONF_RADIATOR_POWER_FRACTION, 0.0, 1.0, 0.05),
    ("C198", "configuration.md:148", const.CONF_UPPER_FLOOR_AREA_RATIO, 0.1, 0.9, None),
    ("C199", "configuration.md:149,355", const.CONF_BUFFER_TANK_VOLUME, 10, 1500, 5),
    ("C200", "configuration.md:150,373", const.CONF_WINDOW_AREA, 0, 50, 0.5),
    ("C201", "configuration.md:151", const.CONF_SOLAR_ORIENTATION_FACTOR, 0.0, 1.0, None),
    ("C202", "configuration.md:152,374", const.CONF_SOLAR_HEAT_GAIN_COEFF, 0.1, 1.0, None),
    ("C203", "configuration.md:167", const.CONF_DHW_TANK_VOLUME, 50, 1500, 10),
    ("C204", "configuration.md:168", const.CONF_DHW_SETPOINT, 40, 65, None),
    ("C205", "configuration.md:169", const.CONF_DHW_MIN_TEMP, 35, 55, None),
    ("C206", "configuration.md:170", const.CONF_DHW_DAILY_CONSUMPTION, 50, 1500, None),
    ("C207", "configuration.md:171", const.CONF_DHW_COOLING_RATE, 0.05, 3.0, 0.05),
    ("C208", "configuration.md:174", const.CONF_DHW_IDLE_MIN_TEMP, 10, 55, None),
    ("C209", "configuration.md:176", const.CONF_DHW_LEGIONELLA_TEMP, 55, 70, None),
    ("C210", "configuration.md:177", const.CONF_DHW_LEGIONELLA_INTERVAL_DAYS, 1, 30, None),
    ("C211", "configuration.md:183,375", const.CONF_WIND_SENSITIVITY, 0.0, 0.5, 0.01),
    ("C212", "configuration.md:184,376", const.CONF_RAIN_HEAT_LOSS_MULTIPLIER, 1.0, 1.5, 0.01),
    ("C213", "configuration.md:234", const.CONF_THERMAL_BRIDGE_FRSI, 0.3, 0.98, 0.01),
    ("C214", "configuration.md:243-244", const.CONF_DHW_INLET_TEMP, 2, 25, 0.5),
    ("C215", "configuration.md:244", const.CONF_DHW_INLET_SEASONAL_AMPLITUDE, 0, 8, 0.5),
    ("C216", "configuration.md:246", const.CONF_GREYWATER_RECOVERY, 0, 0.9, 0.05),
    ("C217", "configuration.md:250", const.CONF_DHW_LEGIONELLA_MIN_INTERVAL_DAYS, 1, 14, None),
    ("C218", "configuration.md:251", const.CONF_SHOWER_FLOW_LPM, 4, 20, 0.5),
    ("C219", "configuration.md:253", const.CONF_VVC_LEAD_MINUTES, 0, 120, 5),
    ("C220", "configuration.md:268", const.CONF_CYCLING_COST, 0, 10, 0.05),
    ("C221", "configuration.md:269", const.CONF_PRICE_RISK_LAMBDA, 0.0, 2.0, 0.05),
    ("C222", "configuration.md:271", const.CONF_COMPRESSOR_REPLACEMENT_COST, 0, 100000, 100),
    ("C223", "configuration.md:272", const.CONF_COMPRESSOR_RATED_STARTS, 1000, 1000000, None),
    ("C224", "configuration.md:285", const.CONF_PEAK_TARIFF_PRICE, 0, 500, None),
    ("C225", "configuration.md:286", const.CONF_PEAK_TARIFF_COUNT, 1, 10, None),
    ("C226", "configuration.md:291", const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR, 0.0, 1.0, 0.05),
    ("C227", "configuration.md:292", const.CONF_MAIN_FUSE_A, 0, 125, None),
    ("C228", "configuration.md:293", const.CONF_MAIN_FUSE_PHASES, 1, 3, None),
    ("C229", "configuration.md:296", const.CONF_PEAK_GUARD_MARGIN_KW, 0.0, 3.0, 0.1),
    ("C230", "configuration.md:298", const.CONF_GRID_FEE_FIXED, 0, 5, 0.01),
    ("C231", "configuration.md:301", const.CONF_CONTRACT_FIXED_PRICE, 0, 10, 0.01),
    ("C232", "configuration.md:317", const.CONF_AWAY_TEMPERATURE, 5, 21, 0.5),
    ("C233", "configuration.md:318", const.CONF_AWAY_DHW_MIN_TEMP, 10, 55, None),
    ("C234", "configuration.md:352", const.CONF_MIXING_VALVE_TARGET, 0, 30, 0.5),
    ("C235", "configuration.md:356", const.CONF_BUFFER_MAX_TEMP, 40, 90, None),
    ("C236", "configuration.md:360", const.CONF_WOOD_TANK_VOLUME, 50, 3000, 50),
    ("C237", "configuration.md:422", const.CONF_PV_PEAK_KW, 0, 100, 0.1),
    ("C238", "configuration.md:423", const.CONF_PV_EFFICIENCY, 0.3, 1.0, 0.01),
    ("C239", "configuration.md:424", const.CONF_PV_EXPORT_PRICE, 0, 10, 0.01),
    ("C240", "configuration.md:437", const.CONF_STALENESS_SCALE, 0.5, 10.0, 0.5),
    ("C241", "configuration.md:440", const.CONF_EXTERNAL_HEAT_MIN_RISE, 0.5, 10, 0.1),
    ("C242", "configuration.md:441", const.CONF_EXTERNAL_HEAT_DECAY_MINUTES, 15, 360, 15),
    ("C243", "configuration.md:465-469 / ecl110.md:87-90", const.CONF_ECL110_QOS, 0, 2, 1),
    ("C244", "configuration.md:467 / ecl110.md:88", const.CONF_ECL110_DISPLACE_MIN, -30, 0, 0.5),
    ("C245", "configuration.md:468 / ecl110.md:89", const.CONF_ECL110_DISPLACE_MAX, 0, 30, 0.5),
    ("C246", "configuration.md:469 / ecl110.md:90", const.CONF_ECL110_PID_TIME_CONSTANT, 0.25, 6.0, 0.25),
]
for cid, source, key, lo, hi, step in RANGE_CLAIMS:
    claim(cid, source, f"{key} range {lo}–{hi}" + (f" step {step}" if step is not None else ""), range_claim(key, lo, hi, step))

# --- Source-scan checks of described mechanisms (not measurements) -------------
claim("C250", "ecl110.md:17-18 / optimizer.py:5568", "heat_pump_on threshold is half the modulation floor, at least 0.1 kW",
      lambda: ok(src_has("optimizer.py", r"max\(0\.1, p\.min_electrical_power \* 0\.5\)"), "optimizer.py: max(0.1, p.min_electrical_power * 0.5)"))
claim("C251", "ecl110.md:22-25 / optimizer.py:5541", "the anticipation bias applies over the first eight hours of the displace schedule",
      lambda: ok(src_has("optimizer.py", r"if i < int\(max\(1, 8 / self\.config\.dt_hours\)\)"), "optimizer.py: i < 8 / dt_hours"))
claim("C252", "ecl110.md:27-30 / coordinator.py:6357", "the published displace is rounded to a whole number",
      lambda: ok(src_has("coordinator.py", r"displace_int = int\(round\(displace\)\)"), "coordinator.py: int(round(displace))"))
claim("C253", "ecl110.md:31-32 / coordinator.py:4379-4395", "comfort commands +4 °C (or the maximum), boost the maximum, off the minimum",
      lambda: ok(src_has("coordinator.py", r'"displace_value": min\(4\.0, self\._ecl110_displace_max\)') and
                 src_has("coordinator.py", r'"mode": "boost"[\s\S]{0,200}_ecl110_displace_max') and
                 src_has("coordinator.py", r'"mode": "off"[\s\S]{0,200}_ecl110_displace_min'), "coordinator.py fixed-mode displace values"))
claim("C254", "how-it-works.md:324-329 / thermal_model.py:2833-2836", "T_slab = 0.7 × (T_return + 1 °C) + 0.3 × T_slab_model",
      lambda: ok(src_has("thermal_model.py", r"estimated_slab = return_temp \+ 1\.0") and src_has("thermal_model.py", r"0\.7 \* estimated_slab \+ 0\.3 \* state\.slab_temperature"), "thermal_model.py update_slab_from_return_temp"))
claim("C255", "how-it-works.md:491-493", "the floor repair is bounded at 48 rounds",
      lambda: ok(src_has("optimizer.py", r"for _ in range\(48\):"), "optimizer.py: range(48)"))
claim("C256", "how-it-works.md:503", "the tank is never planned above min(70 °C, max(setpoint, legionella))",
      lambda: ok(src_has("optimizer.py", r"boost_top = min\(70\.0, float\(params\.dhw_hard_max_temp\)\)"), "optimizer.py: boost_top = min(70.0, dhw_hard_max_temp)"))
claim("C257", "how-it-works.md:634-641 / README:457-460", "irradiance precedence: local sensor, then Open-Meteo, else the weather entity",
      lambda: ok(src_has("coordinator.py", r"solar = reader\.read\(CONF_SOLAR_RADIATION_ENTITY\)[\s\S]{0,400}if not solar_from_sensor and self\._open_meteo is not None"), "coordinator.py: sensor wins, Open-Meteo fills, weather forecast is the default source"))
claim("C258", "how-it-works.md:989", "a COP sample only counts above a third of nameplate",
      lambda: ok(src_has("coordinator.py", r"Below a third of nameplate") and src_has("coordinator.py", r"floor = max\(0\.3 \* params\.max_electrical_power, 0\.2\)"),
                 "coordinator.py: floor = max(0.3 × nameplate, 0.2 kW)", "the gate is 0.3 × nameplate (floored at 0.2 kW), i.e. 30 %, not a third"))
claim("C259", "how-it-works.md:1094-1099", "sysid guards: gains −0.5..2.0 kW, tau 0.1–200 h, UA 0.01–5",
      lambda: ok(src_has("sysid.py", r"if not \(-0\.5 <= gains_kw <= 2\.0\)") and src_has("sysid.py", r"0\.1 <= tau <= 200\.0\) or not \(0\.01 <= ua <= 5\.0"), "sysid.py bounds present"))
claim("C260", "how-it-works.md:278-279 / thermal_model.py:935", "hot water activates when any of a DHW sensor, a tank volume or demand windows is configured",
      lambda: ok(src_has("thermal_model.py", r'values\["dhw_enabled"\] = any\('), "thermal_model.py: dhw_enabled = any(presence trio)"))
claim("C261", "README:126-127 / how-it-works.md:906-907", "an over-age input is treated as missing and freezes the learners",
      lambda: ok("learners_frozen" in DATA and src_has("coordinator.py", r"learners_frozen"), "coordinator publishes learners_frozen / learner_freeze_reason"))
claim("C262", "dashboard-card.md:24-25 / architecture.md", "the card is one self-contained file with no Chart.js/ApexCharts/CDN dependency",
      lambda: eq((sorted(p.name for p in (PKG / "www").iterdir()), bool(re.search(r"chart\.js|apexcharts|cdn\.jsdelivr|unpkg\.com", CARD_JS, re.I))),
                 (["heatpump-optimizer-card.js"], False)))
claim("C263", "dashboard-card.md:385,405 / frontend.py", "the card is served at /heatpump_optimizer_static/heatpump-optimizer-card.js",
      lambda: eq(f"{frontend.URL_BASE}/{frontend.CARD_FILENAME}", "/heatpump_optimizer_static/heatpump-optimizer-card.js"))
claim("C264", "dashboard-card.md:153", "the chart is drawn in a fixed 900x380 coordinate system",
      lambda: ok(src_has and re.search(r"const VIEW_W = 900;\s*\nconst VIEW_H = 380;", CARD_JS) is not None, "VIEW_W=900 VIEW_H=380"))
claim("C265", "dashboard-card.md:141-143", "labelled gridlines snap to 1, 2, 3, 4, 6, 8, 12 or 24 hours",
      lambda: ok("const TIME_LABEL_STEPS = [1, 2, 3, 4, 6, 8, 12, 24];" in CARD_JS, "TIME_LABEL_STEPS present"))
claim("C266", "dashboard-card.md:461,510", "hours must be > 0 and at most 168",
      lambda: ok("hours <= 0 || hours > 168" in CARD_JS, "card rejects hours <= 0 or > 168"))
claim("C267", "dashboard-card.md:514", "series keys are price, dhw_slots, space_slots, outdoor, dhw_temp, house_temp, solar (seven)",
      lambda: eq(sorted(set(re.findall(r'^\s+key: "([a-z_]+)",$', CARD_JS, re.M))), sorted(["price", "dhw_slots", "space_slots", "outdoor", "dhw_temp", "house_temp", "solar"])))


def _card_strings():
    script = ("const fs=require('fs');const s=fs.readFileSync(process.argv[1],'utf8');"
              "const m=s.match(/const STRINGS = (\\{[\\s\\S]*?\\n\\});/);const o=new Function('return '+m[1])();"
              "console.log(JSON.stringify({en:Object.keys(o.en),sv:Object.keys(o.sv)}))")
    out = subprocess.run(["node", "-e", script, str(PKG / "www" / "heatpump-optimizer-card.js")], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        return unverifiable(f"node failed: {out.stderr[:200]}")
    keys = json.loads(out.stdout)
    en, sv = set(keys["en"]), set(keys["sv"])
    return ok(en == sv and 150 <= len(en) <= 250, f"en={len(en)} sv={len(sv)} en-only={sorted(en - sv)} sv-only={sorted(sv - en)}",
              f"Swedish table is missing {sorted(en - sv)}")


claim("C268", "dashboard-card.md:108-109", "about 200 card strings in English and Swedish, with no Swedish entry missing", _card_strings)
claim("C269", "dashboard-card.md:428-435", "the card prints its own version on load (CARD_VERSION, separate from the integration version)",
      lambda: ok(re.search(r'const CARD_VERSION = "[0-9.]+";', CARD_JS) is not None and "v${CARD_VERSION}" in CARD_JS,
                 f"CARD_VERSION={re.search(r'const CARD_VERSION = \"([0-9.]+)\"', CARD_JS).group(1)} vs integration {MANIFEST['version']}"))
claim("C270", "dashboard-card.md:207-209 / 527", "the card reads manual_plan_window_hours from the plan sensors and discovers them by plan_kind",
      lambda: ok('"manual_plan_window_hours"' in CARD_JS and "attrs.plan_kind === kind" in CARD_JS, "both lookups present in the card"))
claim("C271", "dashboard-card.md:541-543", "a pre-v4.2.0 localStorage key is still read as a fallback",
      lambda: ok("storageKeyLegacy" in CARD_JS, "storageKeyLegacy read present"))
claim("C272", "README:552-554 / dashboard-card.md:272", "what_if: false hides the editor and the lanes",
      lambda: ok(re.search(r"what_if", CARD_JS) is not None and "editor.what_if" in CARD_JS, "what_if option handled"))

# --- Architecture -------------------------------------------------------------
MODULES = sorted(p.stem for p in PKG.glob("*.py"))
HA_IMPORTERS = sorted(m for m in MODULES if re.search(r"^(from|import) homeassistant", SRC[m + ".py"], re.M))
claim("C280", "architecture.md:8", "45 modules", lambda: eq(len(MODULES), 45))
claim("C281", "architecture.md:8,99-102", "exactly ten modules import homeassistant at module level: __init__, config_flow, coordinator, open_meteo, frontend and the five platforms",
      lambda: eq(HA_IMPORTERS, sorted(["__init__", "config_flow", "coordinator", "open_meteo", "frontend", "sensor", "binary_sensor", "button", "climate", "switch"])))
claim("C282", "architecture.md:102-104", "inputs reaches for homeassistant.util.dt inside a function only",
      lambda: ok(re.search(r"^\s+from homeassistant\.util import dt as dt_util", SRC["inputs.py"], re.M) is not None and "inputs" not in HA_IMPORTERS, "indented import present, no module-level one"))


def _module_map():
    mapped = set(re.findall(r"[├└]── ([a-z_]+)\.py", DOCS["architecture.md"]))
    return eq((sorted(mapped - set(MODULES)), sorted(set(MODULES) - mapped)), ([], []))


claim("C283", "architecture.md:66-140", "the module map names every module and nothing else", _module_map)
claim("C284", "architecture.md:70,138 / README:389", "__init__ registers 11 services; services.yaml has 11 definitions; config_flow has 13 option pages",
      lambda: eq((len(REGISTERED), len(SERVICES_YAML), len(config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS)), (11, 11, 13)))

# --- Closed-loop and measured claims --------------------------------------------
ROLL = (ROOT / "tests" / "rolling.py").read_text(encoding="utf-8")
claim("C290", "README:483-485 / how-it-works.md:1229-1231", "the learning test uses a house losing 35 % more heat (plant_error 1.35) over three days with a 4.25 kW pump",
      lambda: ok("TRUE_ERROR = 1.35" in ROLL and '_BOUND_PUMP = {"heat_pump_max_power": 4.25}' in ROLL and "days=3, dhw=False, plant_error=TRUE_ERROR, learn=True" in ROLL, "rolling.py constants present"))
claim("C291", "how-it-works.md:1233-1240", "asserted: >10 samples, moves toward truth, overshoot ≤ 0.15, last-quarter spread < 0.05, correct model drift < 0.12 over two days",
      lambda: ok(all(s in ROLL for s in ("int(samples[-1]) > 10", "scale[-1] <= TRUE_ERROR + 0.15", "< 0.05", "abs(float(drift[-1]) - 1.0) < 0.12", "days=2, dhw=False, plant_error=1.0, learn=True")), "all five assertions present verbatim"))
claim("C292", "how-it-works.md:1215-1227", "stability arm: 25 % model error, 5–35 °C, < 3 degree-hours, worst day < 1.6× best",
      lambda: ok(all(s in ROLL for s in ("plant_error: float = 1.25", "> 5.0 and", "< 35.0", "violation < 3.0", "< 1.6")), "rolling.py thresholds present"))


def _rolling_numbers():
    path = os.environ.get("D6_ROLLING_OUT", "tools/audit/round2/D6/rolling_learning.out")
    if not Path(path).exists():
        return unverifiable(f"{path} absent: run tools/audit/round2/D6/rolling_learning.py")
    vals = dict(re.findall(r"^RESULT (\w+)=([-0-9.]+)", Path(path).read_text(), re.M))
    if "breach_learned" not in vals:
        return unverifiable(f"{path} has no RESULT lines")
    b0, b1 = float(vals["breach_uncorrected"]), float(vals["breach_learned"])
    return ok(abs(b0 - 6.7) <= 0.5 and b1 == 0.0,
              f"breach_uncorrected={b0} breach_learned={b1} scale_end={vals['scale_end']} drift={vals['correct_model_drift']} (re-executed on this box)",
              f"re-executed numbers are {b0} -> {b1} degree-hours; the asserted property (learning cuts the breach) holds, the quoted figures do not reproduce",
              stale=True)


claim("C293", "README:486-487 / how-it-works.md:1237-1238", "in the reference run the breach goes from 6.7 degree-hours to zero", _rolling_numbers)
claim("C294", "README:487-488", "a model that is already correct is left alone within ±12 %",
      lambda: ok("abs(float(drift[-1]) - 1.0) < 0.12" in ROLL, "rolling.py asserts drift < 0.12 (the README's ±12 %)"))
for cid, src, text in (
    ("C295", "how-it-works.md:105-106", "hot water displaced 2.6–4.7 kWh of space heating without the premium (validation scenarios)"),
    ("C296", "how-it-works.md:110-112", "two starts were 2.2 % cheaper; a third bought 0.2 %"),
    ("C297", "how-it-works.md:142-147", "halving the target pull: 28.55 vs 23.28 SEK, 18 % of the bill, 0.32 K"),
    ("C298", "how-it-works.md:154-157,174", "the removed smoothness term cost ~5 %; removing anticipation terms made shoulder plans 4–6 % cheaper"),
    ("C299", "how-it-works.md:399-401", "a commanded valve is worth 1–2 SEK/day on the author's winter curve"),
    ("C300", "how-it-works.md:1252-1262", "comfort-weight table: 19.4 °C/53 % … 20.4 °C/47 % on the author's house"),
    ("C301", "README:610 / docs/backlog.md", "backlog items 1–33 are all delivered"),
    ("C302", "dashboard-card.md:436-437", "v5.0.0 shipped card 4.3.0 unchanged"),
):
    claim(cid, src, text, (lambda t=text: unverifiable("historical measurement / removed document; not re-measured in this round (would need a quiet-box harness)")))
claim("C303", "README:271", "only the hot-water half of the savings baseline is always-on; the space half follows the comfort schedule",
      lambda: ok(src_has("optimizer.py", r"Baseline DHW: an always-hot tank held at the setpoint") and
                 src_has("optimizer.py", r"Simulate a conventional thermostat following the comfort schedule"),
                 "optimizer.py:4786 always-hot DHW baseline; optimizer.py:5177 space baseline tracks the per-step comfort targets"))
claim("C304", "README:612-614 / plan-v4.0.0-program.md:1,11,155-1138", "36 selected proposals delivered as tranches T0 through T8",
      lambda: ok("36-feature program" in DOCS["plan-v4.0.0-program.md"] and all(f"## T{i}" in DOCS["plan-v4.0.0-program.md"] for i in range(9)), "36 proposals and T0..T8 headers present"))
claim("C305", "DISCLAIMER.md:71-72", "the savings baseline is 'a simulated always-on thermostat'",
      lambda: ok(False, "optimizer.py:5177 'Simulate a conventional thermostat following the comfort schedule'; README:271 says only the hot-water half is always-on",
                 "the space-heating baseline follows the comfort schedule (day/night targets); only the hot-water baseline is kept permanently hot", stale=True))
claim("C306", "README:281 / const.py", "irradiance sources: local sensor, Open-Meteo (opt-in), weather entity default",
      lambda: eq((const.DEFAULT_SOLAR_FORECAST_SOURCE, const.SOLAR_SOURCES), ("weather", ("weather", "open_meteo"))))
claim("C307", "README:76 / how-it-works.md:47", "the plan is re-solved every interval; first refresh skips the solve (README: first plan within one interval)",
      lambda: ok(src_has("__init__.py", r"coordinator\._skip_solve_once = True"), "__init__.py sets _skip_solve_once before the first refresh"))
claim("C308", "README:24 'Versions 2.3.0 onward were developed in this fork'", "the fork point is upstream 2.2.0",
      lambda: unverifiable("no upstream history in the export"))

# ===========================================================================
# Output
# ===========================================================================
print("| id | source | claim | observed | verdict | true statement |")
print("|---|---|---|---|---|---|")
for r in ROWS:
    cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    print(f"| {r['id']} | {cell(r['source'])} | {cell(r['claim'])} | {cell(r['observed'])[:220]} | {r['verdict']} | {cell(r['truth'])[:220]} |")

counts = {v: sum(1 for r in ROWS if r["verdict"] == v) for v in ("true", "false", "stale", "unverifiable")}
print()
print(f"RESULT claims_extracted={len(ROWS)} count")
print(f"RESULT claims_checked={len(ROWS) - counts['unverifiable']} count")
print(f"RESULT claims_true={counts['true']} count")
print(f"RESULT claims_false={counts['false']} count")
print(f"RESULT claims_stale={counts['stale']} count")
print(f"RESULT claims_unverifiable={counts['unverifiable']} count")
_pt, _tt = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(_pt / _tt) if _tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
json.dump(ROWS, open(os.environ.get("D6_TABLE_JSON", os.devnull), "w"), indent=1)
