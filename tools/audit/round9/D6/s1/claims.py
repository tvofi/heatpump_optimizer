#!/usr/bin/env python3
"""D6-s1 round 9: README.md claims, each checked against executed production code.

METRIC (one line): per README claim, the fact the production symbol delivers
when executed, compared with what README.md states; verdict true/false/stale/
unverifiable. Four finding metrics are printed as their own RESULT lines:

  action_states_undocumented   count of states sensor:HeatPumpActionSensor can
                               publish (its ENUM options, less "unknown", with
                               "idle" confirmed by calling the real
                               optimizer:HeatPumpOptimizer._idle_action) that
                               README's Heat Pump Action row does not name.
                               KEY: the option list the production sensor
                               delivers to Home Assistant, not README text.
  option_page_misplaced        README field->page statements contradicted by the
                               page config_flow:_OPTION_FIELDS actually renders
                               the field on. KEY: the _F row's step column.
  no_dhw_disabled_undocumented entities whose registry default the real
                               platforms report False on a "Finish setup now"
                               entry (token + weather only) that README neither
                               lists as disabled-by-default nor says, in their
                               row or prose, are disabled. KEY: the delivered
                               entity_registry_enabled_default.
  manual_pin_hours_beyond_20   hours of the 24 h horizon pinned by an
                               apply_manual_plan call (services:
                               handle_apply_manual_plan -> the override its
                               coordinator receives -> channel_pins) beyond
                               README's "up to 20 hours". KEY: the pins the
                               override delivers per 15-min step.

RUN (from the export / repository root, never elsewhere):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py
  perturbations (in memory, one at a time):
    --perturb=action_states   drop idle + system_identification from the
                              sensor's options and make _idle_action say "off"
                              -> action_states_undocumented to_zero
    --perturb=orientation     move solar_orientation_factor's _F row to
                              building_preset -> option_page_misplaced down by 1
    --perturb=dhw_config      the Finish-now entry also carries a tank volume
                              (config change) -> no_dhw_disabled_undocumented to_zero
    --perturb=clamp_expiry    clamp the handler's expires_at to now+20 h
                              -> manual_pin_hours_beyond_20 to_zero
  links: external HEAD requests run unless --no-net. Relative links missing
  from an export (the audit pages are stripped) are re-checked in git when
  HPO_BASELINE_GIT (a checkout) and HPO_BASELINE_SHA are set.

EXPECTED at 1936d5ca (exact, counts): action_states_undocumented=2,
option_page_misplaced=3, no_dhw_disabled_undocumented=6,
manual_pin_hours_beyond_20=4.0 h.
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE: round-9 box B1 (linux cloud container), CPython 3.14.0rc2.
ROOT RULE: ROOT = Path.cwd() -- measures the tree it is run from.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib
import json
import re
import subprocess
import sys
import time
import types
import urllib.error
import urllib.request
from datetime import timedelta
from pathlib import Path

_T0P, _T0T = time.process_time(), time.thread_time()

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]

from harness import FakeHass, FakeEntry  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    boost, config_flow, const, curve_learning, freq_control, frontend,
    manual_plan, power_guard, sensor, services, snapshots,
)
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")
NO_NET = "--no-net" in sys.argv

README = (ROOT / "README.md").read_text()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
STRINGS = json.loads((PKG / "strings.json").read_text())
ENT_STR = STRINGS["entity"]

ROWS: list[tuple[str, str, str, str, str]] = []  # id, claim, check, result, verdict


def claim(cid: str, text: str, check: str, observed, ok, truth: str = "") -> None:
    verdict = ok if isinstance(ok, str) else ("true" if ok else "false")
    res = str(observed)
    if verdict != "true" and truth:
        res += f" -- TRUE STATEMENT: {truth}"
    ROWS.append((cid, text, check, res, verdict))


def rline(text: str) -> int:
    """README line number of the first occurrence (for the table's source)."""
    i = README.find(text)
    return README.count("\n", 0, i) + 1 if i >= 0 else -1


# ---------------------------------------------------------------------------
# Entity census through the real async_setup_entry, on a real coordinator
# ---------------------------------------------------------------------------
if PERTURB == "action_states":
    sensor.HeatPumpActionSensor._attr_options = [
        s for s in sensor.HeatPumpActionSensor._attr_options
        if s not in ("idle", "system_identification")
    ]
    _orig_idle = opt_mod.HeatPumpOptimizer._idle_action

    def _idle_off(self):
        return {**_orig_idle(self), "mode": "off"}

    opt_mod.HeatPumpOptimizer._idle_action = _idle_off


def census(extra: dict | None = None):
    cfg = {const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home",
           **(extra or {})}
    hass, entry = FakeHass(), FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    out = []
    for p in integ.PLATFORM_LIST:
        mod = importlib.import_module(f"heatpump_optimizer.{p}")
        added: list = []
        asyncio.run(mod.async_setup_entry(hass, entry, lambda e, *a, **k: added.extend(e)))
        for e in added:
            key = getattr(e, "_attr_translation_key", None)
            name = ENT_STR.get(str(p), {}).get(key, {}).get("name", f"<{p}:{key}>")
            default = getattr(e, "entity_registry_enabled_default",
                              getattr(e, "_attr_entity_registry_enabled_default", True))
            unit = getattr(e, "_attr_native_unit_of_measurement", None)
            if unit is None:
                try:
                    unit = e.native_unit_of_measurement
                except Exception:
                    unit = None
            cat = getattr(e, "_attr_entity_category", None)
            out.append(dict(platform=str(p), name=name, default=bool(default),
                            unit=unit, diag=str(cat) == "diagnostic", entity=e))
    return coord, out


FINISH_NOW_EXTRA = {const.CONF_DHW_TANK_VOLUME: 200.0} if PERTURB == "dhw_config" else {}
_c_min, ENT_MIN = census(FINISH_NOW_EXTRA)          # "Finish setup now" entry
_c_dhw, ENT_DHW = census({const.CONF_DHW_TANK_VOLUME: 200.0})  # hot water, no probes

by_plat: dict[str, list] = {}
for e in ENT_DHW:
    by_plat.setdefault(e["platform"], []).append(e)
n = {p: len(v) for p, v in by_plat.items()}

m = re.search(r"All (\d+) entities appear", README)
claim("C01", f"All {m.group(1)} entities appear", "sum over PLATFORM_LIST of real async_setup_entry",
      sum(n.values()), int(m.group(1)) == sum(n.values()))
for cid, plat, head in (("C02", "sensor", "Sensors"), ("C03", "binary_sensor", "Binary Sensors"),
                        ("C04", "button", "Buttons")):
    m = re.search(rf"### {head} \((\d+) total\)", README)
    claim(cid, f"{head} ({m.group(1)} total)", f"len(collect({plat}))", n[plat], int(m.group(1)) == n[plat])
sw = sorted(e["name"] for e in by_plat["switch"])
claim("C05", "switches: Optimizer Active, Away, DHW Boost, Boost Space Heating",
      "switch.async_setup_entry names", sw,
      sw == sorted(["Optimizer Active", "Away", "DHW Boost", "Boost Space Heating"]))
dt = [e["name"] for e in by_plat["datetime"]]
claim("C06", "a datetime entity Expected Return", "datetime.async_setup_entry", dt, dt == ["Expected Return"])
claim("C07", "one climate entity", "climate.async_setup_entry", n["climate"], n["climate"] == 1)

# The disabled-by-default census (README line ~549 and the list after the tables)
dis_dhw = sorted(e["name"] for e in ENT_DHW if not e["default"])
lst = re.search(r"Disabled by default: (.*?)\.\n", README, re.S).group(1).replace("\n", " ")
listed = sorted(x.strip() for x in re.split(r",| and ", lst) if x.strip())
claim("C08", "Nineteen entities (eighteen sensors and the wood binary sensor) disabled by default",
      "registry default, hot-water install without probes", f"{len(dis_dhw)} ({sum(1 for e in ENT_DHW if not e['default'] and e['platform']=='sensor')} sensors)",
      len(dis_dhw) == 19 and sum(1 for e in ENT_DHW if not e["default"] and e["platform"] == "sensor") == 18)
claim("C09", "the 'Disabled by default:' list names exactly those", "set compare vs census (hot water on)",
      f"listed-not-disabled={sorted(set(listed)-set(dis_dhw))} disabled-not-listed={sorted(set(dis_dhw)-set(listed))}",
      set(listed) == set(dis_dhw))

# README row text per entity name
row_text = {}
for line in README.splitlines():
    if line.startswith("| ") and line.count("|") >= 4:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        row_text.setdefault(cells[0], cells)
dis_min = [e for e in ENT_MIN if not e["default"]]


def _documented_disabled(name: str) -> bool:
    if name in listed:
        return True
    cells = row_text.get(name)
    if cells and "disabled" in " ".join(cells[1:]).lower():
        return True
    # prose: "<name> ... disabled by default" in one sentence
    prose = " ".join(ln for ln in README.splitlines() if not ln.startswith("|"))
    for sent in re.split(r"(?<=\.)\s", prose):
        if name in sent and "disabled by default" in sent:
            return True
    return False


undoc = sorted(e["name"] for e in dis_min if not _documented_disabled(e["name"]))
claim("C10", "…because the ordinary install cannot light them (the list is every such entity)",
      "registry default on a Finish-setup-now entry (token+weather only)",
      f"{len(dis_min)} disabled; undocumented: {undoc}", not undoc,
      "on an install without hot water (Finish setup now, or Quick setup without a tank) "
      f"{len(dis_min)} entities are disabled by default; the hot-water gate also disables {undoc}")
RESULT_NO_DHW = len(undoc)

# Per-row unit / Diagnostic / disabled notes for the sensor tables
unit_bad, diag_bad, dis_bad, checked_rows = [], [], [], 0
for e in by_plat["sensor"] + by_plat["binary_sensor"]:
    cells = row_text.get(e["name"])
    if not cells:
        continue
    checked_rows += 1
    notes = cells[-1]
    if e["platform"] == "sensor":
        doc_unit = cells[1]
        want = None if doc_unit == "—" else doc_unit.replace("CUR", "SEK")
        if want != e["unit"]:
            unit_bad.append(f"{e['name']}: README {doc_unit}, code {e['unit']}")
    if ("Diagnostic" in notes) != e["diag"]:
        diag_bad.append(f"{e['name']}: README diag={'Diagnostic' in notes}, code {e['diag']}")
    says_dis = "disabled by default" in notes.lower()
    if says_dis and e["default"]:
        dis_bad.append(f"{e['name']}: README disabled, code enabled")
claim("C11", "every sensor row's Unit column", "native_unit_of_measurement (CUR=SEK on a stub instance)",
      f"{checked_rows} rows; mismatches {unit_bad}", not unit_bad)
claim("C12", "every row marked 'Diagnostic' is diagnostic and vice versa", "_attr_entity_category",
      f"mismatches {diag_bad}", not diag_bad)
claim("C13", "every row saying 'Disabled by default' is disabled", "entity_registry_enabled_default (hot water on)",
      f"mismatches {dis_bad}", not dis_bad)

# "Not recorded" notes
nr_bad = []
for nm in ("Optimization Schedule", "DHW Heating Schedule", "Plan Space Heating (next 24 h)",
           "Plan DHW Heating (next 24 h)"):
    ent = next(e for e in by_plat["sensor"] if e["name"] == nm)["entity"]
    unrec = set(getattr(ent, "_unrecorded_attributes", frozenset())) | set(
        getattr(ent, "_entity_component_unrecorded_attributes", frozenset()))
    if not unrec:
        nr_bad.append(nm)
claim("C14", "Optimization Schedule / DHW Heating Schedule / plan forecasts 'not recorded'",
      "_unrecorded_attributes non-empty", f"without exclusions: {nr_bad}", not nr_bad)

# Heat Pump Action states (row: 'What the plan is doing now: ...')
hpa_row = row_text["Heat Pump Action"][2]
hpa_named = set(re.findall(r"`(\w+)`", hpa_row))
opts = set(sensor.HeatPumpActionSensor._attr_options) - {"unknown"}
_fake = types.SimpleNamespace(model=types.SimpleNamespace(params=types.SimpleNamespace(min_electrical_power=0.5)),
                              config=types.SimpleNamespace(target_temp=21.0))
idle_mode = opt_mod.HeatPumpOptimizer._idle_action(_fake)["mode"]
opts_live = {s for s in opts if s != "idle" or idle_mode == "idle"}
undoc_states = sorted(opts_live - hpa_named)
claim("C15", "Heat Pump Action: off, hot_water, eco, normal, pre_heat or boost, and comfort",
      "HeatPumpActionSensor._attr_options (+ HeatPumpOptimizer._idle_action executed)",
      f"publishable {sorted(opts_live)}; README omits {undoc_states}", not undoc_states,
      "the sensor also publishes `idle` (the empty-plan / pre-horizon fallback) and "
      "`system_identification` (while the step-response experiment drives the pump)")
RESULT_ACTION = len(undoc_states)

mode_opts = set(sensor.OptimizationModeSensor._attr_options) - {"unknown"}
claim("C16", "Optimization Mode: auto, comfort, economy, boost or off", "OptimizationModeSensor._attr_options",
      sorted(mode_opts), mode_opts == {"auto", "comfort", "economy", "boost", "off"})

clim = next(e for e in ENT_DHW if e["platform"] == "climate")["entity"]
claim("C17", "climate HVAC modes (off, heat, auto) and presets (auto, comfort, economy, boost)",
      "climate entity _attr_hvac_modes/_attr_preset_modes",
      f"{[str(x) for x in clim._attr_hvac_modes]} {clim._attr_preset_modes}",
      {str(x).split('.')[-1].lower() for x in clim._attr_hvac_modes} == {"off", "heat", "auto"}
      and set(clim._attr_preset_modes) == {"auto", "comfort", "economy", "boost"})

dboost = next(e for e in ENT_MIN if e["name"] == "DHW Boost")
claim("C18", "Without hot water configured, DHW Boost is unavailable and disabled by default",
      "DHW Boost default+available on Finish-now entry", f"default={dboost['default']} available={dboost['entity'].available}",
      (not dboost["default"]) and not dboost["entity"].available)

btn = next(e for e in by_plat["button"] if e["name"] == "Optimize Now")["entity"]
_c_dhw._optimization_running = True
try:
    avail_running = btn.available
finally:
    _c_dhw._optimization_running = False
claim("C19", "Optimize Now: unavailable while one is in flight", "button.available with optimization_running=True",
      avail_running, avail_running is False)

# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
reg: dict[str, dict] = {}
hass_s = FakeHass()
_orig_reg = hass_s.services.async_register


def _rec(domain, service, handler, schema=None, **kw):
    reg[service] = dict(schema=schema, **kw)
    return _orig_reg(domain, service, handler, schema=schema, **kw)


hass_s.services.async_register = _rec
services.async_register_services(hass_s)
m = re.search(r"(\d+) services are registered", README)
claim("C20", f"{m.group(1)} services are registered under heatpump_optimizer",
      "services.async_register_services recorder", len(reg), int(m.group(1)) == len(reg))
tbl = re.search(r"\| Service \| What it does \| Returns \|\n\|[-| ]+\|\n(.*?)\n\n", README, re.S).group(1)
doc_svc = {}
for line in tbl.splitlines():
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    doc_svc[c[0].strip("`")] = c[2]
claim("C21", "the services table names every registered service", "set compare",
      f"doc-only={sorted(set(doc_svc)-set(reg))} code-only={sorted(set(reg)-set(doc_svc))}",
      set(doc_svc) == set(reg))
ret_bad = []
for s, ret in doc_svc.items():
    sr = str(reg.get(s, {}).get("supports_response", "NONE")).split(".")[-1].upper()
    want = {"—": "NONE", "Always": "ONLY", "Optional": "OPTIONAL"}[ret]
    if sr != want:
        ret_bad.append(f"{s}: README {ret}, code {sr}")
claim("C22", "the Returns column", "supports_response passed to async_register", ret_bad or "all match", not ret_bad)
m = re.search(r"all (\d+) fields of `set_thermal_parameters`", README)
nf = len(services.SERVICE_SCHEMA_SET_THERMAL_PARAMS.schema)
claim("C23", f"all {m.group(1)} fields of set_thermal_parameters", "len(SERVICE_SCHEMA_SET_THERMAL_PARAMS.schema)",
      nf, int(m.group(1)) == nf)
modes = set(services.SERVICE_SCHEMA_SET_MODE.schema[next(iter(services.SERVICE_SCHEMA_SET_MODE.schema))].container)
claim("C24", "set_mode: auto, comfort, economy, boost or off", "SERVICE_SCHEMA_SET_MODE vol.In container",
      sorted(modes), modes == {"auto", "comfort", "economy", "boost", "off"})
ok_empty = services.SERVICE_SCHEMA_APPLY_MANUAL_PLAN({"dhw_slots": []})
claim("C25", "`dhw_slots: []` is accepted as an explicit empty list", "SERVICE_SCHEMA_APPLY_MANUAL_PLAN",
      ok_empty, ok_empty == {"dhw_slots": []})

# apply_manual_plan "for up to 20 hours": drive the real handler
captured: dict = {}


class _Coord:
    async def async_apply_manual_plan(self, override):
        captured["o"] = override
        return {"ok": True}


services._manual_targets = lambda hass, entry: [("e1", _Coord())]
from homeassistant.util import dt as dt_util  # noqa: E402

now = dt_util.now().replace(second=0, microsecond=0)
if PERTURB == "clamp_expiry":
    _orig_build = services.build_override

    def _clamped(**kw):
        kw["expires_at"] = min(kw["expires_at"], kw["now"] + timedelta(hours=const.MANUAL_PLAN_WINDOW_HOURS))
        return _orig_build(**kw)

    services.build_override = _clamped
call = types.SimpleNamespace(data={"space_slots": [], "expires_at": (now + timedelta(hours=48)).isoformat()})
asyncio.run(services.handle_apply_manual_plan(None, call))
t0 = captured["o"].created_at  # the handler's own "now": the horizon starts where the pins do
steps = [t0 + timedelta(minutes=15 * i) for i in range(96)]
pins = captured["o"].channel_pins(manual_plan.CHANNEL_SPACE, steps)
pinned_h = sum(1 for p in pins if p == p) * 0.25  # not NaN
beyond = max(0.0, pinned_h - 20.0)
claim("C26", "apply_manual_plan: pin exact run slots for up to 20 hours",
      "services.handle_apply_manual_plan(expires_at=now+48h, space_slots=[]) -> channel_pins over 96x15 min",
      f"{pinned_h} h of the 24 h horizon pinned (off)", beyond == 0.0,
      "20 hours is only the default expiry; an explicit expires_at is accepted unbounded, "
      "and one past the horizon pins every step")
RESULT_PIN = beyond

# ---------------------------------------------------------------------------
# Defaults and bounded behaviours
# ---------------------------------------------------------------------------
for cid, text, got, want in (
    ("C27", "target 21 °C", const.DEFAULT_TARGET_TEMP, 21.0),
    ("C28", "comfort day 21 °C", const.DEFAULT_COMFORT_TEMP_DAY, 21.0),
    ("C29", "comfort night 19.5 °C", const.DEFAULT_COMFORT_TEMP_NIGHT, 19.5),
    ("C30", "day runs 07:00-22:00", (const.DEFAULT_DAY_START_HOUR, const.DEFAULT_DAY_END_HOUR), (7, 22)),
    ("C31", "DHW frames `06:00-08:30, 17:00-22:00` by default", const.DEFAULT_DHW_WINDOWS, "06:00-08:30, 17:00-22:00"),
    ("C32", "anti-legionella on by default", const.DEFAULT_DHW_LEGIONELLA_ENABLED, True),
    ("C33", "legionella 60 °C every 7 days", (const.DEFAULT_DHW_LEGIONELLA_TEMP, const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS), (60.0, 7.0)),
    ("C34", "wind 3 % per m/s", const.DEFAULT_WIND_SENSITIVITY, 0.03),
    ("C35", "rain 15 %", const.DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER, 1.15),
    ("C36", "optimization interval 30 minutes by default", const.DEFAULT_OPTIMIZATION_INTERVAL, 30),
    ("C37", "comfort_weight default 5", const.DEFAULT_COMFORT_WEIGHT, 5.0),
    ("C38", "mold breach margin default 0.5 °C", const.DEFAULT_MOLD_FLOOR_BREACH_MARGIN, 0.5),
    ("C39", "weekly snapshots, last eight kept", (snapshots.RING_SIZE, snapshots.SNAPSHOT_INTERVAL_DAYS), (8, 7.0)),
    ("C40", "cool-only heat-curve correction at most 0.5 K per week", curve_learning.MAX_DOWN_PER_WEEK, 0.5),
    ("C41", "frequency: at most one write per five minutes", freq_control.FREQ_WRITE_MIN_INTERVAL_S, 300.0),
    ("C42", "frequency watchdog: three active ticks", freq_control.FREQ_WATCHDOG_TICKS, 3),
    ("C43", "boosts last two hours", boost.BOOST_HOURS, 2),
    ("C44", "peak guard: 2 agree to engage, 2 to clear", power_guard.HYSTERESIS_SAMPLES, 2),
    ("C45", "Observe is the default frequency mode", const.DEFAULT_FREQ_CONTROL_MODE, "observe"),
    ("C46", "Mixed Water: litres of 40 °C water", const.DHW_MIXED_USE_TEMP, 40.0),
    ("C47", "capacity tariff: mean of the three highest peaks", const.DEFAULT_PEAK_TARIFF_COUNT, 3),
    ("C48", "system identification off on a fresh install",
     next(f.default for f in config_flow._OPTION_FIELDS if f.key == "system_identification_enabled"), False),
):
    claim(cid, text, "import const/module constant", got, got == want)

# ECL110 topics ship empty (README: "The two command topics ship empty")
tops = {f.key: f.default for f in config_flow._OPTION_FIELDS if f.step == "heat_curve" and f.key.endswith("topic")}
claim("C49", "ECL110 MQTT topics ship empty", "_OPTION_FIELDS heat_curve topic defaults", tops,
      all(v == "" for v in tops.values()))
cfg_keys = set()
for step in STRINGS["config"]["step"].values():
    cfg_keys |= set((step.get("data") or {}).keys())
    for sec in (step.get("sections") or {}).values():
        cfg_keys |= set((sec.get("data") or {}).keys())
ecl_cfg = sorted(k for k in cfg_keys if k.startswith("ecl110"))
claim("C50", "Since v4.1.0 ECL110 settings live only on the options page, not initial setup",
      "strings.json config.step field keys", ecl_cfg or "none", not ecl_cfg)

# Options menu
pages = config_flow._OPTION_PAGES
m = re.search(r"menu of (\d+) pages — (\d+) you can edit", README)
claim("C51", f"a menu of {m.group(1)} pages — {m.group(2)} you can edit plus a read-only overview",
      "len(_OPTION_PAGES); setup_overview has no _F rows",
      f"{len(pages)} pages, {sum(1 for p in pages if any(f.step == p.step for f in config_flow._OPTION_FIELDS) or p.step == 'quick_setup')} editable",
      len(pages) == int(m.group(1)) and not any(f.step == "setup_overview" for f in config_flow._OPTION_FIELDS))
label = {p.step: STRINGS["options"]["step"]["advanced" if p.menu == "advanced" else "init"]["menu_options"][p.step]
         for p in pages}
fpage = {f.key: f.step for f in config_flow._OPTION_FIELDS}
if PERTURB == "orientation":
    fpage["solar_orientation_factor"] = "building_preset"
located = [  # README 'Changing settings' + Quick start step 5 statements
    ("house_thermal_mass", "thermal_model"), ("slab_thermal_mass", "thermal_model"),
    ("house_heat_loss_coefficient", "thermal_model"), ("heat_pump_max_power", "thermal_model"),
    ("heat_pump_min_power", "thermal_model"),
    ("inter_zone_heat_transfer", "thermal_model"), ("radiator_power_fraction", "thermal_model"),
    ("buffer_tank_volume", "building"), ("window_area", "building_preset"),
    ("solar_orientation_factor", "building_preset"), ("solar_heat_gain_coefficient", "building_preset"),
    ("comfort_weight", "tuning"),
]
mis = [f"{k}: README '{label[w]}', code '{label[fpage[k]]}'" for k, w in located if fpage[k] != w]
claim("C52", "masses, losses, the two-zone split and power limits are on Thermal model (expert); buffer volume on "
      "Heating system; window area, orientation factor and SHGC on Building type and emitters; comfort_weight on "
      "Savings vs comfort", "_OPTION_FIELDS step of each named field", mis or "all match", not mis,
      "the two-zone split (inter-zone transfer, radiator fraction, per-floor masses/losses) and the "
      "orientation factor are on Advanced settings -> Two-zone model")
RESULT_PAGES = len(mis)
cw_label = STRINGS["options"]["step"]["tuning"].get("data", {}).get("comfort_weight")
if cw_label is None:
    for sec in (STRINGS["options"]["step"]["tuning"].get("sections") or {}).values():
        cw_label = cw_label or (sec.get("data") or {}).get("comfort_weight")
claim("C53", "comfort_weight is labelled 'How strictly to hold the temperature'", "strings.json tuning label",
      cw_label, cw_label == "How strictly to hold the temperature")

# Finish menu
fm = STRINGS["config"]["step"]["finish_setup"]
claim("C54", "menu 'Finish setup now?' with Quick setup (recommended), Continue setup, Finish setup now",
      "strings.json config.step.finish_setup", f"{fm.get('title')!r} {list(fm['menu_options'].values())}",
      list(fm["menu_options"].values()) == ["Quick setup (recommended)", "Continue setup", "Finish setup now"])

# Store files and the card resource
coord_s = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={const.CONF_TIBBER_TOKEN: "x",
                                                                     const.CONF_WEATHER_ENTITY: "w.h"}))
from homeassistant.helpers.storage import Store  # noqa: E402
from heatpump_optimizer import away as _away  # noqa: E402

pre = f"{const.DOMAIN}_{coord_s.entry.entry_id}_"
keys = {v._key.removeprefix(pre) for h in (coord_s, coord_s._dhw_learner, coord_s._legionella)
        for v in vars(h).values() if isinstance(v, Store) and v._key.startswith(pre)}
keys |= {_away._away_store(coord_s)._key.removeprefix(pre), boost._store(coord_s)._key.removeprefix(pre)}
doc_keys = set(re.findall(r"heatpump_optimizer_<entry id>_(\w+)", README))
claim("C55", "twelve store files under .storage, named", "Store keys the coordinator constructs",
      f"{len(keys)}; diff {sorted(keys ^ doc_keys)}", len(keys) == 12 and keys == doc_keys)
claim("C56", "card resource /heatpump_optimizer_static/heatpump-optimizer-card.js", "frontend.URL_BASE/CARD_FILENAME",
      f"{frontend.URL_BASE}/{frontend.CARD_FILENAME}",
      f"{frontend.URL_BASE}/{frontend.CARD_FILENAME}" == "/heatpump_optimizer_static/heatpump-optimizer-card.js")

# Versions, requirements, translations
man = json.loads((PKG / "manifest.json").read_text())
hacs = json.loads((ROOT / "hacs.json").read_text())
claim("C57", "Home Assistant 2025.2.0 or newer (README text and badge)", "hacs.json homeassistant",
      hacs["homeassistant"], hacs["homeassistant"] == "2025.2.0" and "Home%20Assistant-2025.2.0%2B" in README)
reqs = sorted(re.split(r"[<>=]", r)[0] for r in man["requirements"])
claim("C58", "numpy, scipy and threadpoolctl installed from the manifest", "manifest.json requirements", reqs,
      reqs == ["numpy", "scipy", "threadpoolctl"])
langs = sorted(p.stem for p in (PKG / "translations").glob("*.json"))
claim("C59", "entity names translated (English and Swedish)", "translations/*.json", langs, langs == ["en", "sv"])
rn = (ROOT / "RELEASE_NOTES.md").read_text()
sec = re.search(r"^## v6\.6\.5\n(.*?)^## ", rn, re.M | re.S).group(1)
claim("C60", "Quick setup arrived in v6.6.5", "RELEASE_NOTES v6.6.5 section names the quick-setup path",
      "#1251 present" if "#1251" in sec else "absent", "quick-setup path in the initial config flow" in sec)
claim("C61", "every v6.0.0 or later release has its detail in RELEASE_NOTES.md", "headings vs VERSION",
      (ROOT / "VERSION").read_text().strip(), f"## v{(ROOT / 'VERSION').read_text().strip()}" in rn and "## v6.0.0" in rn)
bp = sorted(p.name for p in (ROOT / "blueprints" / "automation").glob("*.yaml"))
bp_doc = sorted(set(re.findall(r"blueprints/automation/(\w+\.yaml)", README)))
claim("C62", "three blueprints, one per automations.md example", "blueprints/automation/*.yaml", bp, bp == bp_doc)
claim("C63", "Python 3.13+ badge / 'Python 3.13 or newer'", "tests/requirements-ci or pyproject python floor",
      "badge 3.13; HA 2025.2.0 floor", "unverifiable")

# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------
rel = sorted(set(re.findall(r"\]\(((?!https?:|#)[^)\s]+)\)", README)))
missing = [p for p in rel if not (ROOT / p).exists()]
git_dir, git_sha = os.environ.get("HPO_BASELINE_GIT"), os.environ.get("HPO_BASELINE_SHA")
in_git = []
if git_dir and git_sha:
    for p in list(missing):
        if subprocess.run(["git", "-C", git_dir, "cat-file", "-e", f"{git_sha}:{p}"],
                          capture_output=True).returncode == 0:
            in_git.append(p)
            missing.remove(p)
claim("C64", f"{len(rel)} relative links resolve", "Path.exists (+ git cat-file at the baseline for stripped pages)",
      f"missing={missing} resolved-in-git={in_git}", not missing)
anchors = sorted(set(re.findall(r"\]\(#([^)]+)\)", README)))
heads = {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
         for h in re.findall(r"^#+ (.+)$", README, re.M)}
bad_a = [a for a in anchors if a not in heads]
claim("C65", f"{len(anchors)} in-page anchors resolve", "GitHub slug of every heading", bad_a or "all resolve", not bad_a)
ext = sorted(set(re.findall(r"\]\((https?://[^)\s]+)\)", README)))
ext_res = {}
if not NO_NET:
    for u in ext:
        try:
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0 d6-audit"})
            ext_res[u] = urllib.request.urlopen(req, timeout=15).status
        except urllib.error.HTTPError as err:
            ext_res[u] = err.code
        except Exception as err:  # proxy refusal / DNS: not a verdict on the link
            ext_res[u] = f"unreachable:{type(err).__name__}"
for i, u in enumerate(ext):
    r = ext_res.get(u, "skipped")
    v = "true" if isinstance(r, int) and r < 400 else ("false" if r == 404 else "unverifiable")
    claim(f"L{i + 1:02d}", f"link {u}", "HTTP HEAD", r, v)

# ---------------------------------------------------------------------------
# Claims this seat could not execute cheaply
# ---------------------------------------------------------------------------
for cid, text in (
    ("U01", "closed loop: +35 % loss converges in three simulated days, a correct model left alone within ±12 %"),
    ("U02", "sysid two-state gate: residual noise under ~0.02 °C, five-hour window"),
    ("U03", "capacity tariff typically 30–90 SEK/kW"),
    ("U04", "HA 2025.2.0 is the first release whose requires-python is >=3.13.0"),
):
    claim(cid, text, "SLOW rolling run / external fact -- not executed this round", "-", "unverifiable")

# ---------------------------------------------------------------------------
print("| id | README line | claim | check | result | verdict |")
print("|---|---|---|---|---|---|")
for cid, text, chk, res, ver in ROWS:
    ln = rline(text.split(":")[0][:25]) if cid.startswith("C") else -1
    ln = f"README.md:{ln}" if ln > 0 else "README.md"
    print(f"| {cid} | {ln} | {text} | {chk} | {res.replace('|', '/')} | {ver} |")
counts = {v: sum(1 for r in ROWS if r[4] == v) for v in ("true", "false", "stale", "unverifiable")}
print(f"RESULT claims_checked={len(ROWS)} count")
for k, v in counts.items():
    print(f"RESULT claims_{k}={v} count")
print(f"RESULT action_states_undocumented={RESULT_ACTION} count")
print(f"RESULT option_page_misplaced={RESULT_PAGES} count")
print(f"RESULT no_dhw_disabled_undocumented={RESULT_NO_DHW} count")
print(f"RESULT manual_pin_hours_beyond_20={RESULT_PIN} h")
print(f"RESULT perturbation={PERTURB or 'none'}")
_p, _t = time.process_time() - _T0P, time.thread_time() - _T0T
print(f"RESULT thread_factor={_p / _t if _t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = [ln for ln in Path("/proc/vmstat").read_text().splitlines() if ln.startswith("pswpin")]
    print(f"RESULT swapins={_sw[0].split()[1] if _sw else 0}")
except OSError:
    print("RESULT swapins=0")
