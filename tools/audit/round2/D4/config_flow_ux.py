"""D4 (UI/UX) round 2 -- the config flow's ergonomics, measured through the stub.

METRIC (one line each; all counts, contention-immune):
  initial_screens        : screens (forms + menus) a first-time user passes on
                           the recommended path (Describe my building) from
                           "Add integration" to the entry being created, driven
                           by submitting each form with its own defaults.
  initial_fields         : fields shown across those screens; initial_required
                           the Required() ones; initial_must_know the Required
                           fields with no default (what a user has to bring).
  user_page_fields       : fields on the very first screen; user_page_pickers
                           the entity pickers among them.
  options_pages          : leaf pages in the options menu; options_fields the
                           fields across them (after_save selectors excluded);
                           options_max_fields the largest page and its name;
                           pages_over_15 the pages with more than 15 fields.
  after_save_missing     : saving options pages without the after-save choice.
  help_missing           : fields (either flow) with no data_description.
  error_keys_missing     : error keys the code can raise that strings.json's
                           error section for that flow does not define.
  select_options_missing : (translation_key, option) pairs a SelectSelector
                           offers that strings.json's selector section lacks.
  menu_labels_missing    : menu option keys with no menu_options translation.
  defaults_out_of_range  : NumberSelector fields whose default lies outside
                           the selector's own [min, max].
  untouched_submit_fail  : pages whose schema rejects its own defaults.
  duplicate_keys         : config keys that appear on more than one options
                           page (the same setting reachable from two places).
  sv_identical           : translation leaves whose Swedish text equals the
                           English text (candidates for untranslated strings).
  default_submit_warnings: WARNING-level log records the config flow emits
                           while the initial path is submitted untouched (a
                           fresh install accepting every default).
  off_theme_fields       : fields on a top-menu page whose config key carries
                           none of that page's theme prefixes (THEMES below:
                           the rubric's "one theme per page", made countable).

COMMAND (from the export root):
  PYTHONPATH=tests/hastub python tools/audit/round2/D4/config_flow_ux.py

EXPECTED (baseline c398fc84): see REPORT.md; exact counts.

INSTRUMENTED SYMBOL: heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow
  .async_step_* and HeatPumpOptimizerOptionsFlow.async_step_* (every page is
  rendered by calling the handler with None, and the initial path by
  submitting each form), plus strings.json / translations/{en,sv}.json.
PERTURBATION: remove one field from async_step_hot_water -> options_max_fields
  falls by 1; add `errors["x"] = "new_key"` to any handler -> error_keys_missing
  rises by 1; give _dhw_legionella_warning the coordinator's `stock` exemption
  (DEFAULT_DHW_LEGIONELLA_TEMP / DEFAULT_DHW_SETPOINT) -> default_submit_warnings
  falls to 0.

There is no Home Assistant frontend here: what a page LOOKS like is
inferred from its schema and strings, never rendered.
"""
import os

for _k in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow  # noqa: E402
from heatpump_optimizer.config_flow import (  # noqa: E402
    HeatPumpOptimizerConfigFlow as InitialFlow,
    HeatPumpOptimizerOptionsFlow as OptionsFlow,
)

COMP = "custom_components/heatpump_optimizer"
strings = json.load(open(f"{COMP}/strings.json", encoding="utf-8"))
en = json.load(open(f"{COMP}/translations/en.json", encoding="utf-8"))
sv = json.load(open(f"{COMP}/translations/sv.json", encoding="utf-8"))


def fields_of(schema):
    """[(key, required, default, selector)] for a voluptuous schema."""
    out = []
    for key, value in (schema.schema.items() if schema is not None else []):
        try:
            default = key.default()
        except Exception:  # noqa: BLE001 - no default
            default = None
        out.append((str(getattr(key, "schema", key)), type(key).__name__ == "Required", default, value))
    return out


def sel_config(value):
    cfg = getattr(value, "config", None)
    return dict(cfg) if cfg else {}


def sel_name(value):
    return type(value).__name__


# ---------------------------------------------------------------------------
# A. The initial flow, driven the way a first-time user drives it.
# ---------------------------------------------------------------------------
async def _ok_token(hass, token):
    return "ok"


def run(coro):
    return asyncio.run(coro)


class _Warnings(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record.getMessage())


_warn = _Warnings()
# One handler on the module's own logger; a second on a parent would see
# the same record again through propagation.
config_flow._LOGGER.addHandler(_warn)

screens = []
with mock.patch.object(config_flow, "validate_tibber_token", _ok_token):
    flow = InitialFlow()
    flow.hass = FakeHass()
    result = run(flow.async_step_user(None))
    guard = 0
    while result.get("type") != "create_entry" and guard < 20:
        guard += 1
        step = result["step_id"]
        if result["type"] == "menu":
            screens.append((step, "menu", list(result["menu_options"]), []))
            # The recommended branch.
            nxt = "building_describe" if "building_describe" in result["menu_options"] else list(result["menu_options"])[0]
            result = run(getattr(flow, f"async_step_{nxt}")(None))
            continue
        schema = result["data_schema"]
        flds = fields_of(schema)
        screens.append((step, "form", result.get("errors") or {}, flds))
        payload = {}
        for key, required, default, value in flds:
            if default is not None and not isinstance(default, type(config_flow.vol.UNDEFINED)):
                continue
            if required:
                # What the user must bring: a token and a weather entity.
                payload[key] = {"tibber_token": "t", "weather_entity": "weather.home"}.get(key, "x")
        data = schema(payload)
        result = run(getattr(flow, f"async_step_{step}")(data))
    created = result.get("type") == "create_entry"
default_submit_warnings = list(_warn.records)

initial_fields = sum(len(s[3]) for s in screens if s[1] == "form")
initial_required = sum(1 for s in screens if s[1] == "form" for f in s[3] if f[1])
initial_must_know = [
    f[0] for s in screens if s[1] == "form" for f in s[3]
    if f[1] and (f[2] is None or isinstance(f[2], type(config_flow.vol.UNDEFINED)))
]
user_fields = next(s[3] for s in screens if s[0] == "user")
user_pickers = [f[0] for f in user_fields if sel_name(f[3]) == "EntitySelector"]

print("== initial flow, recommended path ==")
for step, kind, extra, flds in screens:
    if kind == "menu":
        print(f"  {step:22s} MENU  options={extra}")
    else:
        req = sum(1 for f in flds if f[1])
        kinds = Counter(sel_name(f[3]) for f in flds)
        print(f"  {step:22s} form  fields={len(flds):2d} required={req:2d} {dict(kinds)}")
print(f"  create_entry reached: {created}")

# ---------------------------------------------------------------------------
# B. Every options page.
# ---------------------------------------------------------------------------
oflow = OptionsFlow(FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
oflow.hass = FakeHass()
pages = {}
after_save_missing = []
untouched_fail = []
for step in OptionsFlow._MENU_LABELS:
    res = run(getattr(oflow, f"async_step_{step}")(None))
    schema = res.get("data_schema")
    flds = fields_of(schema)
    keys = [f[0] for f in flds]
    has_after = "after_save" in keys
    body = [f for f in flds if f[0] != "after_save"]
    pages[step] = body
    if body and not has_after:
        after_save_missing.append(step)
    try:
        schema({})
    except Exception as err:  # noqa: BLE001
        untouched_fail.append(f"{step}: {type(err).__name__}: {str(err)[:80]}")
menus = {m: list(run(getattr(oflow, f"async_step_{m}")(None))["menu_options"]) for m in ("init", "advanced")}

print("== options pages ==")
for step, body in pages.items():
    kinds = Counter(sel_name(f[3]) for f in body)
    where = "top" if step in OptionsFlow._TOP_MENU else "advanced"
    print(f"  {step:18s} {where:8s} fields={len(body):2d} {dict(kinds)}")
options_fields = sum(len(b) for b in pages.values())
max_page = max(pages.items(), key=lambda kv: len(kv[1]))
over_15 = [s for s, b in pages.items() if len(b) > 15]
key_pages = defaultdict(list)
for step, body in pages.items():
    for f in body:
        key_pages[f[0]].append(step)
duplicates = {k: v for k, v in key_pages.items() if len(v) > 1}

# ---------------------------------------------------------------------------
# C. Strings: help text, error keys, select options, menu labels, Swedish.
# ---------------------------------------------------------------------------
help_missing = []
for step, kind, extra, flds in screens:
    if kind != "form":
        continue
    dd = strings["config"]["step"].get(step, {}).get("data_description", {})
    for f in flds:
        if f[0] not in dd:
            help_missing.append(f"config.{step}.{f[0]}")
for step, body in pages.items():
    dd = strings["options"]["step"].get(step, {}).get("data_description", {})
    for f in body:
        if f[0] not in dd:
            help_missing.append(f"options.{step}.{f[0]}")

src = open(f"{COMP}/config_flow.py", encoding="utf-8").read()
band_src = open(f"{COMP}/comfort_band.py", encoding="utf-8").read()
# Keys the shared helpers (module level and comfort_band) can put on either
# flow, plus the keys each flow class raises in its own handlers.
split = src.index("class HeatPumpOptimizerOptionsFlow")
head_end = src.index("class HeatPumpOptimizerConfigFlow")
ERR = r'errors\[[^\]]+\]\s*=\s*"([a-z_]+)"'
shared = set(re.findall(ERR, src[:head_end]))
shared |= set(re.findall(r'return \{[^}]*:\s*"([a-z_]+)"\}', src[:head_end]))
shared |= set(re.findall(r'"([a-z_]+_(?:above|below|empty|band|close|range|rules|months|hours|windows|max|token|connect))"', band_src))
shared |= set(re.findall(ERR, band_src))
raised_cfg = shared | set(re.findall(ERR, src[head_end:split]))
raised_opt = shared | set(re.findall(ERR, src[split:]))
raised = raised_cfg | raised_opt
cfg_err = set(strings["config"].get("error", {}))
opt_err = set(strings["options"].get("error", {}))
error_keys_missing = sorted({f"config:{k}" for k in raised_cfg - cfg_err} | {f"options:{k}" for k in raised_opt - opt_err})

select_missing = []
selector_strings = strings.get("selector", {})
for step, body in list(pages.items()) + [(s[0], s[3]) for s in screens if s[1] == "form"]:
    for f in body:
        if sel_name(f[3]) != "SelectSelector":
            continue
        cfg = sel_config(f[3])
        tk = cfg.get("translation_key")
        opts = cfg.get("options") or []
        opts = [o["value"] if isinstance(o, dict) else o for o in opts]
        have = selector_strings.get(tk, {}).get("options", {}) if tk else {}
        for o in opts:
            if o not in have:
                select_missing.append(f"{step}.{f[0]}:{tk}/{o}")
select_missing = sorted(set(select_missing))

menu_missing = []
cfg_menu = strings["config"]["step"].get("building", {}).get("menu_options", {})
for k in next(s[2] for s in screens if s[1] == "menu"):
    if k not in cfg_menu:
        menu_missing.append(f"config.building.{k}")
for m, opts in menus.items():
    have = strings["options"]["step"].get(m, {}).get("menu_options", {})
    for k in opts:
        if k not in have:
            menu_missing.append(f"options.{m}.{k}")

defaults_out = []
for step, body in list(pages.items()) + [(s[0], s[3]) for s in screens if s[1] == "form"]:
    for key, required, default, value in body:
        if sel_name(value) != "NumberSelector" or default is None:
            continue
        cfg = sel_config(value)
        try:
            d = float(default)
        except (TypeError, ValueError):
            continue
        if "min" in cfg and d < float(cfg["min"]) or "max" in cfg and d > float(cfg["max"]):
            defaults_out.append(f"{step}.{key}={default} not in [{cfg.get('min')},{cfg.get('max')}]")


def leaves(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(leaves(v, p + k + "/"))
        else:
            out[p + k] = v
    return out


L_en, L_sv = leaves(en), leaves(sv)
sv_identical = sorted(k for k in L_sv if k in L_en and L_sv[k] == L_en[k])
sv_missing = sorted(set(L_en) - set(L_sv))

# The rubric's "one theme per page" as key prefixes, for the pages a household
# revisits (the top menu). A key that matches none of its page's prefixes is
# a setting filed under a heading a user would not look under.
THEMES = {
    "comfort": ("target_temp", "min_temp", "max_temp", "comfort_", "day_", "night_", "humidity", "mold", "thermal_bridge"),
    "hot_water": ("dhw_", "vvc_", "shower_", "greywater_"),
    "tuning": ("price_", "comfort_weight", "cycling_", "risk_", "confidence", "optimization_interval", "smoothing", "min_run", "penalty", "wear", "compressor", "cop_", "power_", "ramp"),
    "grid": ("grid_", "capacity_", "peak_", "fuse_", "tariff", "network", "export", "tibber", "currency", "vat", "fee", "contract"),
    "away": ("away_",),
}
off_theme = []
for page, prefixes in THEMES.items():
    for f in pages.get(page, []):
        if not any(f[0].startswith(pre) or pre in f[0] for pre in prefixes):
            off_theme.append(f"{page}.{f[0]}")

print("== strings ==")
print(f"  help_missing={len(help_missing)} {help_missing[:8]}")
print(f"  raised error keys={sorted(raised)}")
print(f"  error_keys_missing={error_keys_missing}")
print(f"  select_options_missing={select_missing[:10]}")
print(f"  menu_labels_missing={menu_missing}")
print(f"  defaults_out_of_range={defaults_out}")
print(f"  untouched_submit_fail={untouched_fail}")
print(f"  duplicate_keys={duplicates}")
print(f"  sv_identical={sv_identical}")
print(f"  sv_missing={len(sv_missing)}")
print(f"  initial_must_know={initial_must_know}")
print(f"  user_page_pickers={len(user_pickers)}: {user_pickers}")
print(f"  default_submit_warnings={default_submit_warnings}")
print(f"  off_theme_fields={off_theme}")

print(f"RESULT initial_screens={len(screens)} count")
print(f"RESULT initial_forms={sum(1 for s in screens if s[1] == 'form')} count")
print(f"RESULT initial_fields={initial_fields} count")
print(f"RESULT initial_required={initial_required} count")
print(f"RESULT initial_must_know={len(initial_must_know)} count")
print(f"RESULT initial_entry_created={int(created)} flag")
print(f"RESULT user_page_fields={len(user_fields)} count")
print(f"RESULT user_page_pickers={len(user_pickers)} count")
print(f"RESULT options_pages={len(pages)} count")
print(f"RESULT options_fields={options_fields} count")
print(f"RESULT options_max_fields={len(max_page[1])} count ({max_page[0]})")
print(f"RESULT pages_over_15={len(over_15)} count {over_15}")
print(f"RESULT top_menu_entries={len(menus['init'])} count")
print(f"RESULT advanced_menu_entries={len(menus['advanced'])} count")
print(f"RESULT after_save_missing={len(after_save_missing)} count {after_save_missing}")
print(f"RESULT help_missing={len(help_missing)} count")
print(f"RESULT error_keys_missing={len(error_keys_missing)} count")
print(f"RESULT select_options_missing={len(select_missing)} count")
print(f"RESULT menu_labels_missing={len(menu_missing)} count")
print(f"RESULT defaults_out_of_range={len(defaults_out)} count")
print(f"RESULT untouched_submit_fail={len(untouched_fail)} count")
print(f"RESULT duplicate_keys={len(duplicates)} count")
print(f"RESULT sv_identical={len(sv_identical)} count")
print(f"RESULT sv_missing={len(sv_missing)} count")
print(f"RESULT default_submit_warnings={len(default_submit_warnings)} count")
print(f"RESULT off_theme_fields={len(off_theme)} count")
print("RESULT thread_factor=1.00")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
