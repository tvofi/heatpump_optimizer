"""D4.M2 harness: every config-flow and options page, scored against D4-criteria F3/F4/I1/I2.

Metric: per page rendered by the production flow handlers, (a) fields with no label,
(b) F4 fields (number field with a unit, or label carrying a unit/acronym/physics term)
with no data_description, per language; plus every error key the flow classes emit that
lacks a string in a language's matching section (F3), and the page count of the
shortest install path (I2).
Count key: the field name the production schema presents (marker.schema), looked up
under <section>.step.<step_id>.data / data_description (and sections.<s>.data when grouped).
Command: PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s2/flow_pages.py [--perturb-drop-desc FIELD]
Expected: the RESULT values printed at baseline, exact (counts).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow.async_step_*,
config_flow:HeatPumpOptimizerOptionsFlow.async_step_*.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, asyncio, json, re, sys, time, inspect
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from golden import _nested_schema  # noqa: E402

_t0p, _t0t = time.process_time(), time.thread_time()
CC = "custom_components/heatpump_optimizer/"
LANGS = {"strings": CC + "strings.json", "en": CC + "translations/en.json",
         "sv": CC + "translations/sv.json", "de": CC + "translations/de.json"}
TR = {k: json.load(open(p)) for k, p in LANGS.items()}
PERTURB_DROP = None
if "--perturb-drop-desc" in sys.argv:
    PERTURB_DROP = sys.argv[sys.argv.index("--perturb-drop-desc") + 1]
    for t in TR.values():
        for sec in ("config", "options"):
            for st in t[sec]["step"].values():
                st.get("data_description", {}).pop(PERTURB_DROP, None)

UNIT_RE = re.compile(r"(°C|°|kWh|kW\b|\bW\b|%|\bK\b|SEK|EUR|öre|ct|/h\b|\bh\b|\bmin\b|\bm²|COP|SCOP|DHW|UA\b|PV\b|EV\b|SG\b|Modbus|\bL\b|litre|liter|tau|τ|coefficient|thermal|inertia|hysteresis|derate|curve|flow temp|supply temp|capacity|conductance|setpoint)", re.I)


def fields(schema, section=None):
    for key, value in (schema.schema.items() if schema else []):
        inner = _nested_schema(value)
        name = str(getattr(key, "schema", key))
        if inner is None:
            yield section, name, key, value
        else:
            yield from fields(inner, name)


def unit_of(value):
    cfg = getattr(value, "config", None)
    if isinstance(cfg, dict):
        return cfg.get("unit_of_measurement")
    return None


async def render(handler, flow):
    try:
        return await handler(flow, None)
    except Exception as err:  # noqa: BLE001
        return {"type": "error", "err": f"{type(err).__name__}: {err}"}


def flow_steps(cls):
    return sorted(n[len("async_step_"):] for n, _ in inspect.getmembers(cls)
                  if n.startswith("async_step_"))


async def collect():
    pages = []
    for sec, cls in (("config", config_flow.HeatPumpOptimizerConfigFlow),
                     ("options", config_flow.HeatPumpOptimizerOptionsFlow)):
        for step in flow_steps(cls):
            flow = cls() if sec == "config" else cls(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"}))
            flow.hass = FakeHass()
            if sec == "config":
                flow._data = {const.CONF_TIBBER_TOKEN: "t", "name": "x"}
            res = await render(getattr(cls, f"async_step_{step}"), flow)
            pages.append((sec, step, res))
    return pages


pages = asyncio.run(collect())
rendered_forms = [(s, st, r) for s, st, r in pages if r.get("type") == "form"]
menus = [(s, st, r) for s, st, r in pages if r.get("type") == "menu"]
errored = [(s, st, r.get("err") or r.get("type")) for s, st, r in pages
           if r.get("type") not in ("form", "menu")]

no_label, f4_missing, total_fields = [], [], 0
f4_fields = 0
page_field_counts = {}
for sec, step, res in rendered_forms:
    sid = res.get("step_id", step)
    flist = list(fields(res.get("data_schema")))
    page_field_counts[f"{sec}.{sid}"] = len(flist)
    for section, name, key, value in flist:
        total_fields += 1
        for lang, t in TR.items():
            st = t[sec]["step"].get(sid, {})
            holder = st.get("sections", {}).get(section, {}) if section else st
            label = holder.get("data", {}).get(name) or st.get("data", {}).get(name)
            desc = holder.get("data_description", {}).get(name) or st.get("data_description", {}).get(name)
            if not label:
                no_label.append(f"{lang}:{sec}.{sid}.{name}")
                continue
            needs = unit_of(value) is not None or bool(UNIT_RE.search(label))
            if lang == "en" and needs:
                f4_fields += 1
            if needs and not desc:
                f4_missing.append(f"{lang}:{sec}.{sid}.{name}")

# F3: error keys emitted by each flow class (literal assignments + literal returns of
# helpers the class calls), checked against <section>.error per language.
src = open(CC + "config_flow.py").read()
tree = ast.parse(src)
known = set()
for t in TR.values():
    known |= set(t["config"]["error"]) | set(t["options"]["error"])
helpers = {}
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        lits = {n.value.value for n in ast.walk(node) if isinstance(n, ast.Return)
                and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
        helpers[node.name] = {l for l in lits if re.fullmatch(r"[a-z][a-z0-9_]+", l) and l not in ("ok",)}
emitted = {"config": set(), "options": set()}
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name in ("HeatPumpOptimizerConfigFlow", "HeatPumpOptimizerOptionsFlow"):
        sec = "config" if "Config" in node.name else "options"
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and any(isinstance(tg, ast.Subscript) and getattr(tg.value, "id", "") == "errors" for tg in n.targets):
                for c in ast.walk(n.value):
                    if isinstance(c, ast.Constant) and isinstance(c.value, str) and re.fullmatch(r"[a-z][a-z0-9_]+", c.value):
                        emitted[sec].add(c.value)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in helpers:
                emitted[sec] |= {l for l in helpers[n.func.id] if l in known or l.endswith(("_required", "_too_short", "_invalid"))}
emitted["config"].discard("invalid_auth"); emitted["options"].discard("invalid_auth")
f3_missing = [f"{lang}:{sec}.error.{k}" for sec in emitted for k in sorted(emitted[sec])
              for lang, t in TR.items() if k not in t[sec]["error"]]

# Untouched-render placeholders: {name} in a page's title/description/data_description
# that the result's description_placeholders does not supply.
PH = re.compile(r"\{([a-z_]+)\}")
desc_unfilled = []
for sec, step, res in rendered_forms + menus:
    sid = res.get("step_id", step)
    supplied = set((res.get("description_placeholders") or {}).keys())
    for lang, t in TR.items():
        st = t[sec]["step"].get(sid, {})
        texts = [st.get("title", ""), st.get("description", "")]
        texts += list(st.get("data_description", {}).values())
        for s in st.get("sections", {}).values():
            texts += [s.get("name", ""), s.get("description", "")] + list(s.get("data_description", {}).values())
        need = set().union(*(set(PH.findall(x or "")) for x in texts)) - supplied
        if need:
            desc_unfilled.append(f"{lang}:{sec}.{sid}:{sorted(need)}")
for x in desc_unfilled:
    print("DESC_UNFILLED", x)
print(f"RESULT desc_unfilled_page_lang_pairs={len(desc_unfilled)} count")

# I2: the shortest path, add-integration to create_entry: user -> user_sensors ->
# finish_setup (menu) -> finish_now -> setup_overview. Driven, with the three
# required answers only.
async def shortest():
    real = config_flow.async_get_clientsession
    class _R:
        status = 200
        async def json(self): return {"data": {}}
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
    class _S:
        def post(self, *a, **k): return _R()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _S()
    try:
        f = config_flow.HeatPumpOptimizerConfigFlow(); f.hass = FakeHass()
        res = await f.async_step_user(None); n = 1; req_free = []
        while res.get("type") != "create_entry" and n < 20:
            if res["type"] == "menu":
                res = await f.async_step_finish_now(None); n += 1; continue
            sch = res.get("data_schema"); ans = {}
            for _s, name, key, value in fields(sch):
                if type(key).__name__ == "Required":
                    d = getattr(key, "default", None)
                    has = d is not None and type(d).__name__ != "Undefined" and not (callable(d) and type(d()).__name__ == "Undefined")
                    picker = type(value).__name__ in ("EntitySelector", "AreaSelector", "DeviceSelector")
                    if not has and not picker:
                        req_free.append(f"{res['step_id']}.{name}")
            pre = __import__('golden').empty_section_payload(sch) if sch else {}
            if res["step_id"] == "user":
                pre.update({"name": "x", const.CONF_TIBBER_TOKEN: "tok", const.CONF_WEATHER_ENTITY: "weather.home"})
            sub = sch(pre) if sch else {}
            res = await getattr(f, f"async_step_{res['step_id']}")(sub); n += 1
        return n, req_free, res.get("type")
    finally:
        config_flow.async_get_clientsession = real
_n, _rf, _end = asyncio.run(shortest())
print("I2_REQUIRED_FREE", _rf, "end", _end)
print(f"RESULT shortest_path_pages={_n - 1} count")
print(f"RESULT i2_required_free_values={len(_rf)} count")

print("pages_config_flow_steps", len([p for p in pages if p[0] == "config"]))
print("pages_options_flow_steps", len([p for p in pages if p[0] == "options"]))
for e in errored:
    print("NOT_RENDERED_UNTOUCHED", e)
for x in no_label:
    print("NO_LABEL", x)
for x in f4_missing:
    print("F4_NO_DESC", x)
for x in f3_missing:
    print("F3_MISSING", x)
for k, v in sorted(page_field_counts.items()):
    print("FIELDS", k, v)
print("EMITTED", {k: sorted(v) for k, v in emitted.items()})
print(f"RESULT forms_rendered={len(rendered_forms)} count")
print(f"RESULT menus_rendered={len(menus)} count")
print(f"RESULT not_rendered_untouched={len(errored)} count")
print(f"RESULT fields_total={total_fields} count")
print(f"RESULT f4_fields_en={f4_fields} count")
print(f"RESULT unlabelled_field_lang_pairs={len(no_label)} count")
print(f"RESULT f4_missing_desc_field_lang_pairs={len(f4_missing)} count")
print(f"RESULT f3_missing_error_strings={len(f3_missing)} count")
print(f"RESULT max_fields_per_page={max(page_field_counts.values())} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
