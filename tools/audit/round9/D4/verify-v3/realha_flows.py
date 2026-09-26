"""D4 verifier V3 (reach and class): the config and options flows driven through REAL Home Assistant.

Metric (one line per RESULT): counts read off the real ``homeassistant`` 2026.2.3
FlowManager / OptionsFlowManager, the real ``voluptuous_serialize`` + ``cv.custom_serializer``
wire format the frontend receives, and the real ``helpers.translation`` /
``helpers.icon`` loaders -- never ``tests/hastub``.

Command (from the repository root; NOT with PYTHONPATH=tests/hastub):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
      /home/claude/havenv/bin/python tools/audit/round9/D4/verify-v3/realha_flows.py
    (the component's numpy/scipy are borrowed from /home/claude/venv's site-packages,
    appended AFTER havenv's so ``homeassistant`` resolves to the real package; override
    with HPO_NUMPY_SITE=<dir>)

What is real: HomeAssistant core object, loader (custom_components discovery),
ConfigEntries + flow managers (schema validation of every posted user_input, menu
handling, create_entry), device/entity registries, translation and icon loaders.
What is stubbed, deliberately: ``async_process_deps_reqs`` (would pip-install the
manifest requirements and set up ``http``) and ``ConfigEntries.async_setup`` (an entry
is stored but its coordinator is not started). The frontend's pre-fill is emulated
from the serialized schema by the rule of HA frontend's computeInitialHaFormData
(suggested_value, else default, else nothing for an optional field) -- an emulation,
stated as such.

Expected at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact, counts): see the
RESULT lines; the V3 report quotes them (two_zone_expert_real=1, two_zone_expert_cleared_fields_real=1,
prefill_unlabelled_real_en=3, menu_identical_after_quick_real=1, ...). Perturbation (--perturb-zones):
ConfigFlow.async_step_zones is swapped in memory for one that stores nothing from the zones page
(the value voluptuous refilled included) -> two_zone_expert_real and ..._cleared_fields_real go 1 -> 0.
thread_factor here is >1.05 by construction: real HA runs translation/icon/loader I/O on its own
executor threads (deliberate, not BLAS); every RESULT above it is a count, not a timing.
Machine: G2-V3 cloud container, 4 cores, Linux 6.18, CPython 3.14.0rc2.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import re
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

sys.path.append(os.environ.get("HPO_NUMPY_SITE", "/home/claude/venv/lib/python3.14/site-packages"))

import typing  # noqa: E402

# havenv's mashumaro reads typing.ByteString, which CPython 3.14 removed; a shim, not
# a behaviour change of Home Assistant (it only lets core_config import).
if not hasattr(typing, "ByteString"):
    typing.ByteString = (bytes, bytearray, memoryview)  # type: ignore[attr-defined]

import homeassistant  # noqa: E402

assert "hastub" not in (homeassistant.__file__ or ""), "run WITHOUT PYTHONPATH=tests/hastub"

from homeassistant import config_entries, core, data_entry_flow, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import (  # noqa: E402
    area_registry as ar, config_validation as cv, device_registry as dr,
    entity_registry as er, floor_registry as fr, icon, label_registry as lr, translation,
)
import voluptuous_serialize  # noqa: E402

_P0, _T0 = time.process_time(), time.thread_time()
REPO = Path.cwd()
DOMAIN = "heatpump_optimizer"
PERTURB_ZONES = "--perturb-zones" in sys.argv
print(f"# homeassistant {HA_VERSION} from {homeassistant.__file__}")


def ser(schema):
    return voluptuous_serialize.convert(schema, custom_serializer=cv.custom_serializer) if schema else []


def initial(fields):
    """HA frontend computeInitialHaFormData, for the field kinds these pages use."""
    out = {}
    for f in fields:
        desc = f.get("description") or {}
        if desc.get("suggested_value") is not None:
            out[f["name"]] = desc["suggested_value"]
        elif "default" in f:
            out[f["name"]] = f["default"]
        elif f.get("type") == "expandable":
            out[f["name"]] = initial(f.get("schema", []))
        elif not f.get("required"):
            continue
        elif "selector" in f:
            sel = f["selector"]
            if "boolean" in sel:
                out[f["name"]] = False
            elif "number" in sel:
                out[f["name"]] = sel["number"].get("min", 0)
            elif "select" in sel:
                o = sel["select"]["options"][0]
                out[f["name"]] = o["value"] if isinstance(o, dict) else o
            else:
                out[f["name"]] = ""
    return out


def flat_fields(fields, prefix=""):
    for f in fields:
        if f.get("type") == "expandable":
            yield from flat_fields(f.get("schema", []))
        else:
            yield f


async def make_hass(tmp: Path, currency="EUR"):
    (tmp / "custom_components").mkdir()
    (tmp / "custom_components" / DOMAIN).symlink_to(REPO / "custom_components" / DOMAIN)
    hass = core.HomeAssistant(str(tmp))
    hass.config.currency = currency
    hass.config.language = "en"
    hass.config.skip_pip = True
    hass.config.safe_mode = False
    loader.async_setup(hass)
    for reg in (ar, fr, lr, dr, er):
        await reg.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    return hass


def add_entry(hass, domain, data=None, options=None, title="x"):
    entry = config_entries.ConfigEntry(
        data=data or {}, discovery_keys={}, domain=domain, minor_version=1, options=options or {},
        source="user", subentries_data=None, title=title, unique_id=None, version=1,
    )
    hass.config_entries._entries[entry.entry_id] = entry
    return entry


DEVICE = [
    ("sensor.pump_outdoor_temperature", "Outdoor temperature", "temperature", "°C", "-2.0"),
    ("sensor.pump_compressor_frequency", "Compressor frequency", "frequency", "Hz", "48"),
    ("number.pump_dhw_minimum_temperature", "DHW minimum temperature", None, "°C", "42"),
    ("number.pump_legionella_temperature", "Legionella temperature", None, "°C", "65"),
]
NOTHING = [("sensor.utility_humidity", "Utility humidity", "humidity", "%", "40")]


def seed_devices(hass):
    tuya = add_entry(hass, "localtuya")
    dreg, ereg = dr.async_get(hass), er.async_get(hass)
    ids = {}
    for key, rows, name in (("pump", DEVICE, "Pump"), ("nothing", NOTHING, "Utility meter cupboard")):
        dev = dreg.async_get_or_create(config_entry_id=tuya.entry_id, identifiers={("localtuya", key)}, name=name)
        ids[key] = dev.id
        for eid, oname, dc, unit, state in rows:
            domain, obj = eid.split(".")
            ereg.async_get_or_create(
                domain, "localtuya", eid.replace(".", "_"), suggested_object_id=obj,
                config_entry=tuya, device_id=dev.id, original_name=oname,
                original_device_class=dc, unit_of_measurement=unit,
            )
            hass.states.async_set(eid, state, {"unit_of_measurement": unit, "friendly_name": f"{name} {oname}"})
    return ids


FIRST = {"name": "Heat Pump Optimizer", "price_source": "entity",
         "price_entity": "sensor.nordpool", "weather_entity": "weather.home"}


async def translations(hass, lang, cat):
    return await translation.async_get_translations(hass, lang, cat, {DOMAIN})


def res(name, value, unit="count"):
    print(f"RESULT {name}={value} {unit}")


async def main():
    tmp = Path(tempfile.mkdtemp(prefix="d4v3-realha-"))
    with mock.patch.object(config_entries, "async_process_deps_reqs", mock.AsyncMock()):
        hass = await make_hass(tmp)
        hass.config_entries.async_setup = mock.AsyncMock(return_value=True)
        hass.states.async_set("sensor.nordpool", "1.0", {"unit_of_measurement": "EUR/kWh"})
        hass.states.async_set("weather.home", "sunny")
        ids = seed_devices(hass)
        tr = {lang: {c: await translations(hass, lang, c) for c in ("config", "options", "services")} for lang in ("en", "sv")}
        FM = hass.config_entries.flow

        async def start():
            for prog in FM.async_progress():
                FM.async_abort(prog["flow_id"])
            for e in list(hass.config_entries.async_entries(DOMAIN)):
                del hass.config_entries._entries[e.entry_id]
            r = await FM.async_init(DOMAIN, context={"source": "user"})
            r = await FM.async_configure(r["flow_id"], FIRST)
            assert r["step_id"] == "user_sensors", r
            r = await FM.async_configure(r["flow_id"], initial(ser(r["data_schema"])))
            return r

        # ---- D4-s2-01 / D4-s2-07: the recommended quick path, fresh install -------
        r = await start()
        first_menu = dict(r["menu_options"]) if r["type"] == "menu" else None
        print(f"# after user_sensors: {r['type']}/{r.get('step_id')} menu={first_menu}")
        flow_id = r["flow_id"]
        r = await FM.async_configure(flow_id, {"next_step_id": "quick_setup"})
        r = await FM.async_configure(flow_id, initial(ser(r["data_schema"])))
        print(f"# quick_setup submit -> {r['type']}/{r.get('step_id')}")
        res("quick_path_reaches_device_prefill_real", int(r.get("step_id") == "device_prefill"))
        pick_field = [f["name"] for f in flat_fields(ser(r["data_schema"]))]
        print(f"# device pick page fields={pick_field}")
        r = await FM.async_configure(flow_id, {pick_field[0]: ids["pump"]})
        fields = [f["name"] for f in flat_fields(ser(r["data_schema"]))]
        print(f"# preview {r['type']}/{r.get('step_id')} fields={fields} errors={r.get('errors')}")
        for lang in ("en", "sv"):
            t = tr[lang]["config"]
            miss = [k for k in fields if f"component.{DOMAIN}.config.step.device_prefill.data.{k}" not in t]
            print(f"#   {lang} real-loader unlabelled: {miss}")
            res(f"prefill_unlabelled_real_{lang}", len(miss))
        preview_input = initial(ser(r["data_schema"]))
        r = await FM.async_configure(flow_id, preview_input)
        after = dict(r["menu_options"]) if r["type"] == "menu" else None
        print(f"# after preview submit: {r['type']}/{r.get('step_id')} menu={after}")
        res("menu_identical_after_quick_real", int(after == first_menu and after is not None))
        # the refusal
        r2 = await start()
        f2 = r2["flow_id"]
        r2 = await FM.async_configure(f2, {"next_step_id": "quick_setup"})
        r2 = await FM.async_configure(f2, initial(ser(r2["data_schema"])))
        r2 = await FM.async_configure(f2, {pick_field[0]: ids["nothing"]})
        errs = sorted(set((r2.get("errors") or {}).values()))
        print(f"# unreadable device -> {r2.get('step_id')} errors={r2.get('errors')}")
        for lang in ("en", "sv"):
            miss = [e for e in errs if f"component.{DOMAIN}.config.error.{e}" not in tr[lang]["config"]]
            res(f"prefill_error_untranslated_real_{lang}", len(miss))
        FM.async_abort(f2)

        # ---- D4-s2-04: expert path, every page as the frontend pre-fills it ------
        async def expert(branch, clear_zones=False):
            r = await start()
            fid = r["flow_id"]
            trail = []
            r = await FM.async_configure(fid, {"next_step_id": "temperature"})
            while r["type"] in ("form", "menu"):
                trail.append(r["step_id"])
                if r["type"] == "menu":
                    nxt = branch if r["step_id"] == "building" else next(iter(r["menu_options"]))
                    r = await FM.async_configure(fid, {"next_step_id": nxt})
                    continue
                post = initial(ser(r["data_schema"]))
                if clear_zones and r["step_id"] == "zones":
                    post = {}  # every zone field cleared by the user before Submit
                r = await FM.async_configure(fid, post)
                if len(trail) > 20:
                    break
            trail.append(r["type"])
            return r, trail

        if PERTURB_ZONES:
            from custom_components.heatpump_optimizer import config_flow as cf  # type: ignore
            orig = cf.HeatPumpOptimizerConfigFlow.async_step_zones

            async def zones_no_defaults(self, user_input=None):
                if user_input is not None:
                    return await self.async_step_dhw()
                return await orig(self, None)
            cf.HeatPumpOptimizerConfigFlow.async_step_zones = zones_no_defaults
        from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # type: ignore
        for branch in ("thermal", "building_describe"):
            r, trail = await expert(branch)
            data = dict(r.get("result").data) if r["type"] == "create_entry" else {}
            flag = int(ThermalParameters.from_config(data).two_zone_enabled) if data else -1
            print(f"# {branch}: {' -> '.join(map(str, trail))}")
            res(f"two_zone_{'expert' if branch == 'thermal' else 'describe'}_real", flag)
        # the other two first-run paths, at their pre-filled answers
        for first in ("quick_setup", "finish_now"):
            r = await start()
            fid = r["flow_id"]
            r = await FM.async_configure(fid, {"next_step_id": first})
            hops = 0
            while r["type"] in ("form", "menu") and hops < 12:
                hops += 1
                if r["type"] == "menu":
                    r = await FM.async_configure(fid, {"next_step_id": "finish_now" if "finish_now" in r["menu_options"] else next(iter(r["menu_options"]))})
                else:
                    r = await FM.async_configure(fid, initial(ser(r["data_schema"])))
            data = dict(r.get("result").data) if r["type"] == "create_entry" else {}
            res(f"two_zone_{first}_real", int(ThermalParameters.from_config(data).two_zone_enabled) if data else -1)
        r, trail = await expert("thermal", clear_zones=True)
        data = dict(r.get("result").data) if r["type"] == "create_entry" else {}
        res("two_zone_expert_cleared_fields_real", int(ThermalParameters.from_config(data).two_zone_enabled) if data else -1)

        # ---- D4-s2-03: the dhw_min_too_close text as the real loader returns it --
        for flow_type in ("config", "options"):
            for lang in ("en", "sv"):
                s = tr[lang][flow_type].get(f"component.{DOMAIN}.{flow_type}.error.dhw_min_too_close", "")
                res(f"escaped_seq_{flow_type}_{lang}_real", len(re.findall(r"\\u[0-9a-fA-F]{4}", s)))
        all_bad = sum(1 for lang in tr for c in tr[lang] for v in tr[lang][c].values()
                      if re.search(r"\\u[0-9a-fA-F]{4}", v))
        res("escaped_leaves_all_real_loader", all_bad)

        # ---- D4-s2-08: service icons through the real icon loader ---------------
        icons = await icon.async_get_icons(hass, "services", {DOMAIN})
        ent_icons = await icon.async_get_icons(hass, "entity", {DOMAIN})
        from custom_components.heatpump_optimizer import services as svc  # type: ignore
        names = sorted(re.findall(r'^([a-z_]+):\s*$', (REPO / "custom_components" / DOMAIN / "services.yaml").read_text(), re.M))
        print(f"# real icon loader services={icons.get(DOMAIN)} entity-block-present={bool(ent_icons.get(DOMAIN))}")
        res("services_yaml_names", len(names))
        res("services_without_icon_real", sum(1 for n in names if n not in (icons.get(DOMAIN) or {})))

        # ---- D4-s2-06 / D4-s2-09: translation texts via real loader --------------
        for lang in ("en", "sv"):
            d = tr[lang]["options"].get(f"component.{DOMAIN}.options.step.thermal_model_zones.description", "")
            d2 = tr[lang]["options"].get(f"component.{DOMAIN}.options.step.thermal_model.description", "")
            res(f"zones_desc_has_placeholder_real_{lang}", int("{preset_warning}" in d))
            res(f"thermal_model_desc_has_placeholder_real_{lang}", int("{preset_warning}" in d2))
            bare = [k for c in ("config", "options") for k, v in tr[lang][c].items()
                    if ".data_description." in k and re.search(r"(\d) C\b|\bm2\b", v)]
            res(f"bare_unit_data_descriptions_real_{lang}", len(bare))

        # ---- D4-s2-02 / D4-s2-05 / D4-s2-06: options flow on a real entry --------
        entry = add_entry(hass, DOMAIN, data={"name": "HPO", "price_source": "entity",
                          "price_entity": "sensor.nordpool", "weather_entity": "weather.home"},
                          options={"wood_furnace_enabled": True, "external_heat_enabled": True}, title="HPO")
        OM = hass.config_entries.options
        from custom_components.heatpump_optimizer import config_flow as cf  # type: ignore
        steps = list(cf.HeatPumpOptimizerOptionsFlow._MENU_LABELS)
        money, foreign, box_off, slider_off, box_n, slider_n = [], [], [], [], 0, 0
        seen = set()
        for step in steps:
            r = await OM.async_init(entry.entry_id)
            fid = r["flow_id"]
            flow = OM._progress[fid]
            try:
                r = await getattr(flow, f"async_step_{step}")()
            except Exception as err:  # noqa: BLE001
                print(f"#   options {step}: {type(err).__name__}: {err}")
                OM.async_abort(fid)
                continue
            for f in flat_fields(ser(r.get("data_schema"))):
                num = (f.get("selector") or {}).get("number")
                if not num:
                    continue
                unit = num.get("unit_of_measurement") or ""
                codes = re.findall(r"\b(SEK|EUR|NOK|DKK|USD|GBP)\b", unit)
                if codes:
                    money.append((step, f["name"], unit))
                    if any(c != hass.config.currency for c in codes):
                        foreign.append((step, f["name"], unit))
                if (step, f["name"]) in seen:
                    continue
                seen.add((step, f["name"]))
            OM.async_abort(fid)
        for m in money:
            print(f"#   money {m[0]}.{m[1]}: {m[2]}{'  <-- foreign' if m in foreign else ''}")
        res("options_money_fields_real", len(money))
        res("options_foreign_currency_units_real", len(foreign))

        # D4-s2-06: armed questionnaire on a two-zone entry, rendered through the real options manager
        from custom_components.heatpump_optimizer import const as K  # type: ignore
        answers = {K.CONF_BUILDING_STRUCTURE: "timber_slab", K.CONF_BUILDING_ERA: "1980_2005",
                   K.CONF_BUILDING_FOUNDATION: "none", K.CONF_HEATED_AREA: 140.0,
                   K.CONF_UPPER_EMITTER: "radiators", K.CONF_LOWER_EMITTER: "floor"}
        seed = {K.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
        armed = {**seed, **cf._derive_preset(answers, seed), K.CONF_BUILDING_PRESET_ENABLED: True}
        e2 = add_entry(hass, DOMAIN, data={"name": "HPO2", "price_source": "entity", "price_entity": "sensor.nordpool",
                       "weather_entity": "weather.home"}, options=armed, title="HPO2")
        for lang in ("en", "sv"):
            hass.config.language = lang
            for step in ("thermal_model", "thermal_model_zones"):
                r = await OM.async_init(e2.entry_id)
                fid = r["flow_id"]
                r = await getattr(OM._progress[fid], f"async_step_{step}")()
                keys = [f["name"] for f in flat_fields(ser(r.get("data_schema"))) if f["name"] in cf.DERIVED_THERMAL_KEYS]
                desc = tr[lang]["options"].get(f"component.{DOMAIN}.options.step.{step}.description", "")
                ph = r.get("description_placeholders") or {}
                shown = desc
                for k, v in ph.items():
                    shown = shown.replace("{" + k + "}", str(v))
                has = bool(ph.get("preset_warning")) and ph["preset_warning"] in shown
                print(f"#   {lang} {step}: derived={len(keys)} placeholder_returned={bool(ph.get('preset_warning'))} shown={has}")
                res(f"derived_{'unwarned' if not has else 'warned'}_{step}_real_{lang}", len(keys))
                OM.async_abort(fid)
        hass.config.language = "en"

        # D4-s2-05: the wire format the frontend receives for the config-flow thermal/zones pages
        r = await start()
        fid = r["flow_id"]
        r = await FM.async_configure(fid, {"next_step_id": "temperature"})
        r = await FM.async_configure(fid, initial(ser(r["data_schema"])))
        r = await FM.async_configure(fid, {"next_step_id": "thermal"})
        wire = []
        for _ in range(2):
            fs = ser(r["data_schema"])
            wire += [(r["step_id"], f) for f in flat_fields(fs)]
            r = await FM.async_configure(fid, initial(fs))
        FM.async_abort(fid)
        from decimal import Decimal
        off = []
        for step, f in wire:
            num = (f.get("selector") or {}).get("number")
            if not num or "default" not in f:
                continue
            base = Decimal(str(num.get("min", 0)))
            stp = num.get("step", 1)
            if stp == "any":
                continue
            q = (Decimal(str(f["default"])) - base) / Decimal(str(stp))
            if q != q.to_integral_value():
                off.append((step, f["name"], num.get("mode"), f["default"], num.get("min"), stp))
        for o in off:
            print(f"#   off-grid on the wire: {o[0]}.{o[1]} mode={o[2]} default={o[3]} min={o[4]} step={o[5]}")
        res("wire_offgrid_defaults_config_thermal_zones", len(off))
        res("wire_offgrid_defaults_box_mode", sum(1 for o in off if o[2] == "box"))

    _p, _t = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        _s = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
        print(f"RESULT swapins={_s[0].split()[1] if _s else 0}")
    except OSError:
        print("RESULT swapins=0")
    await hass.async_stop(force=True)


asyncio.run(main())
