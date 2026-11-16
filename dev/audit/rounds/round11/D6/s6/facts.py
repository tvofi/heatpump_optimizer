"""Production facts the de.json ledger checks against, each read by running the code.

Measures: nothing on its own; ledger.py imports it. Every fact here is produced
by driving a production symbol, never by reading text:
  - config-flow steps: each HeatPumpOptimizerConfigFlow.async_step_<s>(None) rendered
  - options pages: config_flow._OPTION_FIELDS rows (every row, `when` ignored) and the
    options flow's own rendered steps (init/advanced menus, quick_setup, modbus_prefill,
    factory_reset, setup_overview)
  - selectors: every SelectSelector constructed while config_flow imports and renders
    (SelectSelector.__init__ wrapped), plus services.yaml selectors
  - entities: each platform's async_setup_entry over a real HeatPumpOptimizerCoordinator
    with one completed input cycle (the tests/entities.py:collect shape)
  - services: services.async_register_services on FakeHass; the registered schemas' keys
  - error/abort/issue/exception keys: every string constant in the production package (AST)
  - card strings: the card's STRINGS table evaluated by node
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s6/facts.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (4 vCPU container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, asyncio, json, pathlib, subprocess, sys

ROOT = pathlib.Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tests" / "hastub"), str(ROOT)]
PKG = ROOT / "custom_components" / "heatpump_optimizer"

from homeassistant.helpers import selector as _sel  # noqa: E402

SELECTORS: dict[str, set[str]] = {}
_orig_init = _sel.SelectSelector.__init__


def _rec_init(self, config=None, *a, **k):
    _orig_init(self, config, *a, **k)
    c = getattr(self, "config", None) or config or {}
    tk = c.get("translation_key") if isinstance(c, dict) else None
    if tk:
        opts = set()
        for o in c.get("options", []):
            opts.add(o["value"] if isinstance(o, dict) else str(o))
        SELECTORS.setdefault(tk, set()).update(opts)


_sel.SelectSelector.__init__ = _rec_init

import voluptuous as vol  # noqa: E402
import yaml  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import config_flow as cf  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402


def _marker_key(m):
    return str(getattr(m, "schema", m))


def walk_schema(schema, out, section=None):
    """{key: info} for every field, recursing into sections; info keeps the marker and widget."""
    for marker, widget in (schema.schema.items() if isinstance(schema, vol.Schema) else schema.items()):
        key = _marker_key(marker)
        inner = getattr(widget, "schema", None)
        if isinstance(inner, vol.Schema):
            out.setdefault("__sections__", {}).setdefault(key, set())
            sub = {}
            walk_schema(inner, sub, key)
            for k, v in sub.items():
                if k == "__sections__":
                    continue
                out["__sections__"][key].add(k)
                out[k] = v
            continue
        cfg = getattr(widget, "config", None)
        out[key] = {
            "required": isinstance(marker, vol.Required),
            "default": getattr(marker, "default", None),
            "config": dict(cfg) if isinstance(cfg, dict) else {},
            "widget": widget,
            "section": section,
        }
    return out


CONFIG_STEPS = ["user", "user_sensors", "temperature", "building", "building_describe", "building_extras",
                "thermal", "zones", "dhw", "weather_sensitivity", "finish_setup", "quick_setup",
                "setup_overview", "device_prefill", "reauth_confirm"]


async def _render_config():
    out = {}
    for step in CONFIG_STEPS:
        f = cf.HeatPumpOptimizerConfigFlow()
        f.hass = FakeHass()
        r = await getattr(f, "async_step_" + step)(None)
        fields = walk_schema(r["data_schema"], {}) if r.get("data_schema") is not None else {}
        out[step] = {"type": r.get("type"), "fields": fields, "menu": list(r.get("menu_options") or [])}
    # the device pre-fill's second form, the preview of every suggestible key
    out["device_prefill"]["fields"].update(walk_schema(cf._prefill_schema(sorted(prefill_keys()), {}), {}))
    return out


def _options_flow():
    hass = FakeHass()
    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"}, options={}, entry_id="d6s6")
    hass.config_entries.entries.append(entry)
    flow = cf.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    return flow


async def _render_options():
    out = {}
    for step in ["init", "advanced", "setup_overview", "quick_setup", "modbus_prefill", "factory_reset"]:
        flow = _options_flow()
        try:
            r = await getattr(flow, "async_step_" + step)(None)
        except Exception as e:  # noqa: BLE001
            out[step] = {"type": "error", "fields": {}, "menu": [], "error": repr(e)}
            continue
        fields = walk_schema(r["data_schema"], {}) if r.get("data_schema") is not None else {}
        out[step] = {"type": r.get("type"), "fields": fields, "menu": list(r.get("menu_options") or [])}
    # registry pages: every row, revealed or not; sections from the row's group
    for row in cf._OPTION_FIELDS:
        page = out.setdefault(row.step, {"type": "form", "fields": {}, "menu": []})
        if row.default is cf._DYNAMIC:
            for marker, widget in row.widget({}).items():
                page["fields"][_marker_key(marker)] = {"required": isinstance(marker, vol.Required), "default": getattr(marker, "default", None),
                                                       "config": dict(getattr(widget, "config", {}) or {}), "widget": widget, "section": row.group}
                if row.group:
                    page["fields"].setdefault("__sections__", {}).setdefault(row.group, set()).add(_marker_key(marker))
            continue
        w = row.widget.of(FakeHass()) if isinstance(row.widget, cf._ByHass) else row.widget
        page["fields"][row.key] = {"required": row.required, "default": row.default, "config": dict(getattr(w, "config", {}) or {}),
                                   "widget": w, "section": row.group, "row": row}
        if row.group:
            page["fields"].setdefault("__sections__", {}).setdefault(row.group, set()).add(row.key)
    # the pre-fill preview (second form of modbus_prefill): one field per suggestible key
    preview = walk_schema(cf._prefill_schema(sorted(prefill_keys()), {}), {})
    out["modbus_prefill"]["fields"].update(preview)
    out["after_save"] = True
    return out


def prefill_keys():
    """Keys the device pre-fill can suggest: every CONF_ name modbus_prefill.py references."""
    tree = ast.parse((PKG / "modbus_prefill.py").read_text())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id.startswith("CONF_")}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr.startswith("CONF_")}
    from custom_components.heatpump_optimizer import modbus_prefill
    return {getattr(modbus_prefill, n, None) or getattr(const, n, None) for n in names} - {None}


def entities(extra=None):
    from custom_components.heatpump_optimizer import binary_sensor, button, climate, sensor, switch
    from custom_components.heatpump_optimizer import datetime as dtm
    from custom_components.heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0, **(extra or {})}
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())
    entry.runtime_data = coord
    out = {}
    for plat, mod in (("sensor", sensor), ("binary_sensor", binary_sensor), ("button", button),
                      ("switch", switch), ("climate", climate), ("datetime", dtm)):
        added = []

        def add(es, *_a, **_k):
            for e in es:
                e.hass = hass
            added.extend(es)
        asyncio.run(mod.async_setup_entry(hass, entry, add))
        for e in added:
            tk = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
            out.setdefault(plat, {})[tk] = e
    return out


def services():
    from custom_components.heatpump_optimizer import services as svc
    hass = FakeHass()
    svc.async_register_services(hass)
    reg = {}
    for (dom, name), schema in hass.services._schemas.items():
        keys = set()
        if schema is not None:
            s = getattr(schema, "schema", schema)
            if isinstance(s, dict):
                keys = {_marker_key(m) for m in s}
            elif hasattr(s, "validators"):
                for v in s.validators:
                    vs = getattr(v, "schema", None)
                    if isinstance(vs, dict):
                        keys |= {_marker_key(m) for m in vs}
        reg[name] = keys
    ydoc = yaml.safe_load((PKG / "services.yaml").read_text())
    for name, spec in (ydoc or {}).items():
        for f, fs in ((spec or {}).get("fields") or {}).items():
            sel = (fs or {}).get("selector") or {}
            s = sel.get("select") or {}
            if s.get("translation_key"):
                SELECTORS.setdefault(s["translation_key"], set()).update(
                    o["value"] if isinstance(o, dict) else str(o) for o in s.get("options", []))
    return reg, ydoc


def string_constants():
    """Every str constant (and f-string literal head) in the production package.

    The framework's own abort reasons count when the flow calls the helper that raises them.
    """
    out = set()
    src = (PKG / "config_flow.py").read_text()
    if "_abort_if_unique_id_configured" in {n.attr for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Attribute)}:
        out.add("already_configured")
    for p in PKG.glob("*.py"):
        if p.name.startswith("._"):  # macOS AppleDouble export artefacts, not source
            continue
        for n in ast.walk(ast.parse(p.read_bytes())):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                out.add(n.value)
            elif isinstance(n, ast.JoinedStr) and n.values and isinstance(n.values[0], ast.Constant):
                out.add(n.values[0].value + "{")
    return out


def card_strings():
    # eval runs the repository's own card table (an object literal), nothing fetched.
    js = r'''
const fs=require("fs");const s=fs.readFileSync(process.argv[1],"utf8");
const i=s.indexOf("const STRINGS = {");let d=0,j=i+16;for(;j<s.length;j++){if(s[j]=="{")d++;else if(s[j]=="}"){d--;if(!d)break;}}
const S=eval("("+s.slice(i+16,j+1)+")");process.stdout.write(JSON.stringify(S));'''
    out = subprocess.run(["node", "-e", js, str(PKG / "www" / "heatpump-optimizer-card.js")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def collect():
    cfgs = asyncio.run(_render_config())
    opts = asyncio.run(_render_options())
    svc_reg, svc_yaml = services()
    return {
        "config": cfgs,
        "options": opts,
        "prefill": prefill_keys(),
        "entities": entities({const.CONF_TWO_ZONE: True} if hasattr(const, "CONF_TWO_ZONE") else None),
        "services": svc_reg,
        "services_yaml": svc_yaml,
        "selectors": SELECTORS,
        "strings": string_constants(),
        "card": card_strings(),
    }


if __name__ == "__main__":
    F = collect()
    print("RESULT config_steps=%d" % len(F["config"]))
    print("RESULT option_pages=%d" % len([k for k in F["options"] if k != "after_save"]))
    print("RESULT selectors=%d" % len(F["selectors"]))
    print("RESULT entity_keys=%d" % sum(len(v) for v in F["entities"].values()))
    print("RESULT services=%d" % len(F["services"]))
    print("RESULT card_de_strings=%d" % len(F["card"]["de"]))
