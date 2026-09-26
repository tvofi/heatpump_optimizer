"""D4 round 9, verifier V2 (independent lens): the config/options-flow findings D4-s2-01..09
measured with enumerators and metric definitions written independently of tools/audit/round9/D4/s2.

Metric definitions (one line each; each count is keyed on what the production flow RETURNS or the
shipped translation file the frontend resolves, never on this harness's own labels):
  --check prefill   (D4-s2-01) infer_keys_unlabelled_<lang>: keys modbus_prefill.infer returns for a snapshot in
                    which EVERY role it reads is present (the universe, filtered by config_flow._prefill_fits),
                    with no config.step.device_prefill.data label; refusal_untranslated_<lang>: error values the
                    real config-flow async_step_device_prefill returns for an unresolvable device id with no
                    config.error text.
  --check currency  (D4-s2-02) registry_foreign_units: _OPTION_FIELDS rows whose widget (a _ByHass resolved with
                    hass.config.currency = --currency, default NOK) carries a unit_of_measurement naming a currency
                    code other than resolve_currency(hass).
  --check escaped   (D4-s2-03) escaped_leaves: leaves of strings.json + translations/*.json that, after json.loads,
                    still contain a backslash-u-XXXX sequence; returned_garbled: error texts the real config-flow
                    async_step_dhw returns for dhw_min 53 / setpoint 55 whose en/sv text holds one.
  --check zones     (D4-s2-04) two_zone_after_zones_page: ThermalParameters.from_config(flow._data).two_zone_enabled
                    after async_step_zones is submitted with its own schema applied to an EMPTY dict (what
                    voluptuous stores when the user clears every field or submits as shown).
  --check stepgrid  (D4-s2-05) off_grid_box_fields: box-mode NumberSelectors on config thermal/zones and every
                    options page whose rendered value v (default or suggested) has (v - min) / step not an integer,
                    in Decimal arithmetic (the HTML step base is min).
  --check preset    (D4-s2-06) derived_fields_without_warning_<lang>: DERIVED_THERMAL_KEYS fields rendered on any
                    options page whose translated description template lacks the {preset_warning} placeholder while
                    the step passes a non-empty preset_warning.
  --check quickmenu (D4-s2-07) quick_offered_after_quick: 1 if the menu returned after async_step_quick_setup +
                    an empty device pick still lists quick_setup.
  --check icons     (D4-s2-08) services_without_icon: services the real async_register_services registers on a
                    FakeHass with no icons.json services.<name>; services_yaml_without_icon: same over services.yaml keys.
  --check units     (D4-s2-09) bare_unit_leaves_<lang>: every translation leaf (whole file) matching a digit then
                    ' C' word-boundary, or 'm2' / 'W/m2' as a word.

Command (repository root):
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=tests/hastub \
    /home/claude/venv/bin/python tools/audit/round9/D4/verify-v2/flow_v2.py --check <name> [--perturb]
--perturb applies this harness's own in-memory fix for the checked finding; the headline count must go to 0.
Expected (baseline, exact counts, first recorded 2026-09-26 on box G2-V2; every --perturb -> 0 on the headline):
  prefill   infer_keys=13, infer_keys_unlabelled_{en,sv,strings}=7, refusal_untranslated_*=1, options_twin_unlabelled_*=0
  currency  registry_money_rows=4, registry_foreign_units=1 (NOK and EUR); --currency SEK -> 0 (null control)
  escaped   escaped_leaves=6, escaped_sequences=22, returned_errors=1, returned_garbled_texts=2 (en, sv)
  zones     two_zone_before_zones_page=0, two_zone_after_zones_page=1
  stepgrid  box_fields_with_value=54, off_grid_box_fields=9 (config 8, options 1)
  preset    derived_fields_rendered_{en,sv}=10, derived_fields_without_warning_{en,sv}=6
  quickmenu quick_offered_before_quick=1 (null: first menu), quick_offered_after_quick=1, quick_first_after_quick=1
  icons     services_registered=12, services_without_icon=12, services_yaml_without_icon=12
  units     bare_unit_leaves_{en,sv}=9 (whole file; all under data_description)
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence). Machine: box G2-V2, 4-core Linux 6.18,
CPython 3.14.0rc2. Counts are contention-immune. Writes nothing.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import pathlib
import re
import sys
import time
from decimal import Decimal

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import config_flow, const, modbus_prefill  # noqa: E402
from heatpump_optimizer.currency import resolve_currency  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

_P0, _T0 = time.process_time(), time.thread_time()
ARGS = sys.argv[1:]
CHECK = ARGS[ARGS.index("--check") + 1]
PERTURB = "--perturb" in ARGS
COMP = pathlib.Path("custom_components/heatpump_optimizer")
LANGS = {"en": json.loads((COMP / "translations/en.json").read_text()), "sv": json.loads((COMP / "translations/sv.json").read_text())}
STRINGS = json.loads((COMP / "strings.json").read_text())


def R(name, value, unit="count"):
    print(f"RESULT {name}={value} {unit}")


def leaves(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from leaves(v, f"{path}.{k}")
    elif isinstance(node, str):
        yield path, node


def walk(schema):
    """(key, validator, marker) of every leaf field, sections flattened."""
    for marker, value in (schema.schema.items() if schema else []):
        inner = getattr(value, "schema", None)
        import voluptuous as vol
        if isinstance(inner, vol.Schema):
            yield from walk(inner)
        else:
            yield str(getattr(marker, "schema", marker)), value, marker


def options_flow(options, currency="SEK", lang="en"):
    hass = FakeHass()
    hass.config.currency = currency
    hass.config.language = lang
    flow = config_flow.HeatPumpOptimizerOptionsFlow(FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}, options=options))
    flow.hass = hass
    return flow


# ------------------------------------------------------------------ D4-s2-01
def check_prefill():
    if PERTURB:
        for tree in (*LANGS.values(), STRINGS):
            c, o = tree["config"]["step"]["device_prefill"], tree["options"]["step"]["modbus_prefill"]
            for kind in ("data", "data_description"):
                for k, v in o.get(kind, {}).items():
                    c.setdefault(kind, {}).setdefault(k, v)
            for k, v in tree["options"]["error"].items():
                tree["config"]["error"].setdefault(k, v)
    # A snapshot holding every role modbus_prefill reads, at values each decoder accepts.
    regs = {404: "500", 405: "650", 406: "450", 518: str(22 * 256), 519: str(6 * 256), 601: "7", 711: "1",
            712: str(6 * 256), 713: str(8 * 256), 714: str(0b10000000), 4109: "0"}
    snap = {f"r{a}": (f"sensor.p_gchv_r{a}", v, 0.1 if a in (404, 405, 406) else 1.0) for a, v in regs.items()}
    snap["unit_capacity"] = ("sensor.p_unit_capacity", "8", 1.0)
    for label in modbus_prefill._NAMED:
        if label != "unit_capacity":
            snap[label] = (f"sensor.p_{label}", "1", 1.0)
    current = {**config_flow._ABSENT_FALLBACKS, const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
    keys = sorted(k for k, v in modbus_prefill.infer(snap, current).items() if config_flow._prefill_fits(k, v))
    print(f"# infer universe ({len(keys)}): {keys}")

    async def refuse():
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass(states={})
        return await flow.async_step_device_prefill({config_flow._PREFILL_DEVICE: "no_such_device"})

    res = asyncio.run(refuse())
    errs = sorted(set((res.get("errors") or {}).values()))
    print(f"# refusal: step={res.get('step_id')} errors={errs}")
    R("infer_keys", len(keys))
    for name, tree in (*LANGS.items(), ("strings", STRINGS)):
        page = tree["config"]["step"]["device_prefill"]
        miss = [k for k in keys if k not in page.get("data", {})]
        twin = [k for k in keys if k not in tree["options"]["step"]["modbus_prefill"].get("data", {})]
        bad = [e for e in errs if e not in tree["config"]["error"]]
        print(f"# {name}: unlabelled={miss} refusal_untranslated={bad}")
        R(f"infer_keys_unlabelled_{name}", len(miss))
        R(f"options_twin_unlabelled_{name}", len(twin))
        R(f"refusal_untranslated_{name}", len(bad))


# ------------------------------------------------------------------ D4-s2-02
def check_currency():
    cur = ARGS[ARGS.index("--currency") + 1] if "--currency" in ARGS else "NOK"
    codes = re.compile(r"\b(SEK|EUR|NOK|DKK|GBP|USD|CHF|PLN|ISK)\b")
    if PERTURB:
        rows = list(config_flow._OPTION_FIELDS)
        for i, row in enumerate(rows):
            if row.key == const.CONF_WOOD_PRICE_SEK_M3:
                rows[i] = row._replace(widget=config_flow._ByHass(lambda h: config_flow._number(0, 10000, 10, f"{resolve_currency(h)}/m³")))
        config_flow._OPTION_FIELDS = tuple(rows)
    hass = FakeHass()
    hass.config.currency = cur
    want = resolve_currency(hass)
    money, foreign = 0, []
    for row in config_flow._OPTION_FIELDS:
        w = row.widget
        if isinstance(w, config_flow._ByHass):
            w = w.of(hass)
        unit = ((getattr(w, "config", None) or {}).get("unit_of_measurement")) or ""
        found = codes.findall(unit)
        if found:
            money += 1
            if any(c != want for c in found):
                foreign.append((row.step, row.key, unit))
    print(f"# currency={cur} resolved={want} foreign={foreign}")
    R("registry_money_rows", money)
    R("registry_foreign_units", len(foreign))


# ------------------------------------------------------------------ D4-s2-03
ESC = re.compile(r"\\u[0-9a-fA-F]{4}")


def check_escaped():
    files = {"strings": STRINGS, **LANGS}
    if PERTURB:
        def fix(node):
            if isinstance(node, dict):
                return {k: fix(v) for k, v in node.items()}
            return ESC.sub(lambda m: chr(int(m.group(0)[2:], 16)), node) if isinstance(node, str) else node
        files = {k: fix(v) for k, v in files.items()}
    bad = [(f, p, t) for f, tree in files.items() for p, t in leaves(tree) if ESC.search(t)]
    for f, p, t in bad:
        print(f"# {f}{p}: {ESC.findall(t)}")
    R("escaped_leaves", len(bad))
    R("escaped_sequences", sum(len(ESC.findall(t)) for _, _, t in bad))

    async def dhw_errors():
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        form = await flow.async_step_dhw()
        user = {}
        for key, _v, marker in walk(form.get("data_schema")):
            try:
                user[key] = marker.default()
            except Exception:
                pass
        user[const.CONF_DHW_MIN_TEMP] = 53
        user[const.CONF_DHW_SETPOINT] = 55
        res = await flow.async_step_dhw(user)
        return res.get("step_id"), res.get("errors") or {}

    step, errs = asyncio.run(dhw_errors())
    print(f"# config dhw submit min=53 setpoint=55 -> step={step} errors={errs}")
    garbled = 0
    for lang in ("en", "sv"):
        for e in set(errs.values()):
            txt = files[lang]["config"]["error"].get(e, "")
            n = len(ESC.findall(txt))
            print(f"# {lang} config.error.{e}: {n} escape(s): {txt[:90]!r}")
            garbled += 1 if n else 0
    R("returned_errors", len(set(errs.values())))
    R("returned_garbled_texts", garbled)


# ------------------------------------------------------------------ D4-s2-04
def check_zones():
    async def run():
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        form = await flow.async_step_zones()
        schema = form["data_schema"]
        stored = schema({})  # frontend posts the shown defaults; a cleared field is refilled by vol.Optional(default=)
        if PERTURB:
            # this harness's fix: write the explicit two-zone answer 'off' when nothing on the page differs from its defaults
            base = schema({})
            if all(stored.get(k) == v for k, v in base.items()):
                stored = {**stored, const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_OFF}
        before = ThermalParameters.from_config(dict(flow._data)).two_zone_enabled
        flow._data.update({"name": "x"})
        orig = flow.async_step_dhw

        async def stop(*a, **k):
            return {"type": "form", "step_id": "dhw"}
        flow.async_step_dhw = stop
        await flow.async_step_zones(stored)
        flow.async_step_dhw = orig
        after = ThermalParameters.from_config(dict(flow._data)).two_zone_enabled
        return before, after, sorted(stored)

    before, after, keys = asyncio.run(run())
    print(f"# stored keys from an empty submit: {keys}")
    R("two_zone_before_zones_page", int(before))
    R("two_zone_after_zones_page", int(after))


# ------------------------------------------------------------------ D4-s2-05
def off_grid(v, lo, step):
    try:
        v, lo, step = Decimal(str(v)), Decimal(str(lo)), Decimal(str(step))
    except Exception:
        return False
    return (v - lo) % step != 0


def check_stepgrid():
    if PERTURB:
        orig = config_flow._number

        def patched(minimum, maximum, step, unit=None, *, slider=False):
            sel = orig(minimum, maximum, step, unit, slider=slider)
            if not slider:
                sel.config["step"] = "any"
            return sel
        config_flow._number = patched
        # rows built at import hold selectors already: patch their config in place
        for row in config_flow._OPTION_FIELDS:
            c = getattr(row.widget, "config", None)
            if isinstance(c, dict) and c.get("mode") == "box" and "step" in c:
                c["step"] = "any"
    rows, seen = [], set()

    def scan(tag, result):
        for key, val, marker in walk(result.get("data_schema")):
            c = getattr(val, "config", None) or {}
            if "step" not in c or str(c.get("mode")) not in ("box", "NumberSelectorMode.BOX"):
                continue
            desc = getattr(marker, "description", None) or {}
            v = desc.get("suggested_value") if isinstance(desc, dict) and "suggested_value" in desc else None
            if v is None:
                try:
                    v = marker.default()
                except Exception:
                    v = None
            if v is None or c["step"] == "any":
                continue
            if (tag, key) in seen:
                continue
            seen.add((tag, key))
            rows.append((tag, key, v, c["min"], c["step"], off_grid(v, c["min"], c["step"])))

    async def run():
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        for step in ("thermal", "zones", "dhw", "temperature"):
            try:
                scan(f"config.{step}", await getattr(flow, f"async_step_{step}")())
            except Exception as exc:  # a step needing prior answers
                print(f"# config.{step}: {exc!r}")
        of = options_flow({const.CONF_WOOD_FURNACE_ENABLED: True})
        for step in dict.fromkeys(list(config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS) + ["thermal_model_zones"]):
            try:
                scan(f"options.{step}", await getattr(of, f"async_step_{step}")())
            except Exception as exc:
                print(f"# options.{step}: {exc!r}")

    asyncio.run(run())
    bad = [r for r in rows if r[5]]
    for r in bad:
        print(f"# off-grid {r[0]}.{r[1]}: value={r[2]} min={r[3]} step={r[4]}")
    R("box_fields_with_value", len(rows))
    R("off_grid_box_fields", len(bad))
    R("off_grid_config_fields", len([r for r in bad if r[0].startswith("config.")]))
    R("off_grid_options_fields", len([r for r in bad if r[0].startswith("options.")]))


# ------------------------------------------------------------------ D4-s2-06
def check_preset():
    if PERTURB:
        for tree in LANGS.values():
            tree["options"]["step"]["thermal_model_zones"]["description"] += "\n\n{preset_warning}"
    answers = {const.CONF_BUILDING_STRUCTURE: "timber_slab", const.CONF_BUILDING_ERA: "1980_2005",
               const.CONF_BUILDING_FOUNDATION: "none", const.CONF_HEATED_AREA: 140.0,
               const.CONF_UPPER_EMITTER: "radiators", const.CONF_LOWER_EMITTER: "floor"}
    seed = {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0}
    derived = config_flow._derive_preset(answers, seed)
    options = {**seed, **derived, const.CONF_BUILDING_PRESET_ENABLED: True}
    for lang, tree in LANGS.items():
        of = options_flow(options, lang=lang)
        missing, total = 0, 0

        async def run():
            nonlocal missing, total
            for step in dict.fromkeys(list(config_flow.HeatPumpOptimizerOptionsFlow._MENU_LABELS) + ["thermal_model_zones", "building_preset"]):
                try:
                    res = await getattr(of, f"async_step_{step}")()
                except Exception:
                    continue
                if res.get("type") != "form" and str(res.get("type")) != "FlowResultType.FORM":
                    continue
                keys = [k for k, _v, _m in walk(res.get("data_schema")) if k in config_flow.DERIVED_THERMAL_KEYS]
                if not keys:
                    continue
                ph = (res.get("description_placeholders") or {}).get("preset_warning", "")
                tmpl = tree["options"]["step"].get(res.get("step_id"), {}).get("description", "")
                shown = "{preset_warning}" in tmpl and bool(ph)
                print(f"# {lang} {res.get('step_id')}: derived={len(keys)} placeholder_passed={bool(ph)} template_has_it={'{preset_warning}' in tmpl}")
                total += len(keys)
                missing += 0 if shown else len(keys)
        asyncio.run(run())
        R(f"derived_fields_rendered_{lang}", total)
        R(f"derived_fields_without_warning_{lang}", missing)


# ------------------------------------------------------------------ D4-s2-07
def check_quickmenu():
    src = (COMP / "config_flow.py").read_text()
    cf = config_flow
    if PERTURB:
        import importlib.util
        old = '                    "quick_setup": "Quick setup (recommended)",\n'
        assert src.count(old) == 1
        text = src.replace(old, '                    **({"quick_setup": "Quick setup (recommended)"} if not self._quick_done else {}),\n')
        text = text.replace("            self._data.update(quick_setup.derive(dict(user_input)))\n",
                            "            self._data.update(quick_setup.derive(dict(user_input)))\n            self._quick_done = True\n")
        spec = importlib.util.spec_from_loader("heatpump_optimizer.config_flow", loader=None)
        cf = importlib.util.module_from_spec(spec)
        cf.__file__, cf.__package__ = str(COMP / "config_flow.py"), "heatpump_optimizer"
        sys.modules["heatpump_optimizer.config_flow"] = cf
        exec(compile(text, str(COMP / "config_flow.py"), "exec"), cf.__dict__)
        cf.HeatPumpOptimizerConfigFlow._quick_done = False

    async def run():
        flow = cf.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        flow._data.update({"name": "Heat Pump Optimizer", const.CONF_PRICE_SOURCE: "entity",
                           const.CONF_PRICE_ENTITY: "sensor.nordpool", const.CONF_WEATHER_ENTITY: "weather.home"})
        m0 = await flow.async_step_finish_setup()
        form = await flow.async_step_quick_setup()
        ans = {}
        for key, _v, marker in walk(form.get("data_schema")):
            try:
                ans[key] = marker.default()
            except Exception:
                pass
        r = await flow.async_step_quick_setup(ans)
        steps = [r.get("step_id")]
        if r.get("step_id") == "device_prefill":
            r = await flow.async_step_device_prefill({cf._PREFILL_DEVICE: ""})
            steps.append(r.get("step_id"))
        return m0, r, steps

    m0, m1, steps = asyncio.run(run())
    o0, o1 = list(m0.get("menu_options") or {}), list(m1.get("menu_options") or {})
    print(f"# menu before quick: {o0}; after quick ({' -> '.join(map(str, steps))}): {o1}")
    R("quick_offered_before_quick", int("quick_setup" in o0))
    R("quick_offered_after_quick", int("quick_setup" in o1 and m1.get("step_id") == "finish_setup"))
    R("quick_first_after_quick", int(bool(o1) and o1[0] == "quick_setup"))


# ------------------------------------------------------------------ D4-s2-08
def check_icons():
    from heatpump_optimizer import services
    icons = json.loads((COMP / "icons.json").read_text())
    if PERTURB:
        icons["services"] = {}
    hass = FakeHass()
    services.async_register_services(hass)
    reg = hass.services
    names = set()
    for attr in ("_registry", "_services", "services", "registered", "_handlers"):
        store = getattr(reg, attr, None)
        if isinstance(store, dict):
            for k, v in store.items():
                if isinstance(k, tuple):
                    names.add(k[1])
                elif isinstance(v, dict):
                    names.update(v)
                else:
                    names.add(k)
            break
    if not names:
        print(f"# FakeServices attrs: {vars(reg).keys()}")
    import yaml
    yaml_names = set((yaml.safe_load((COMP / "services.yaml").read_text()) or {}).keys())
    if PERTURB:
        icons["services"] = {n: {"service": "mdi:heat-pump"} for n in names | yaml_names}
    have = set((icons.get("services") or {}).keys())
    print(f"# registered={sorted(names)}")
    R("services_registered", len(names))
    R("services_without_icon", len(names - have))
    R("services_yaml", len(yaml_names))
    R("services_yaml_without_icon", len(yaml_names - have))


# ------------------------------------------------------------------ D4-s2-09
def check_units():
    bare = re.compile(r"\d ?C\b(?![a-zA-Z])|\bW/m2\b|\bm2\b")
    trees = dict(LANGS)
    if PERTURB:
        def fix(node):
            if isinstance(node, dict):
                return {k: fix(v) for k, v in node.items()}
            if isinstance(node, str):
                node = re.sub(r"(\d) ?C\b", r"\1 °C", node)
                return re.sub(r"\bm2\b", "m²", node)
            return node
        trees = {k: fix(v) for k, v in trees.items()}
    for lang, tree in trees.items():
        hits = [(p, t) for p, t in leaves(tree) if bare.search(t) and "°C" not in bare.search(t).group(0)]
        # a digit-space-C inside "°C" never matches because of the degree sign; keep only bare hits
        hits = [(p, t) for p, t in hits if re.search(r"(?<!°)\b\d+ ?C\b|\bm2\b", t)]
        for p, t in hits:
            print(f"# {lang}{p}: {bare.findall(t)}")
        R(f"bare_unit_leaves_{lang}", len(hits))
        R(f"bare_unit_leaves_{lang}_data_description", len([p for p, _ in hits if ".data_description." in p]))


{"prefill": check_prefill, "currency": check_currency, "escaped": check_escaped, "zones": check_zones,
 "stepgrid": check_stepgrid, "preset": check_preset, "quickmenu": check_quickmenu, "icons": check_icons,
 "units": check_units}[CHECK]()
print(f"# perturb={PERTURB}")
_p, _t = time.process_time() - _P0, time.thread_time() - _T0
R("thread_factor", f"{(_p / _t) if _t > 0 else 1.0:.3f}", "")
R("load1", f"{os.getloadavg()[0]:.2f}", "")
try:
    R("swapins", [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1], "")
except (OSError, IndexError):
    R("swapins", 0, "")
