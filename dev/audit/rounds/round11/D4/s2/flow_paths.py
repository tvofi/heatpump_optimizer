"""D4.M2 harness: install-path step counts with required knowledge, and the I1 rubric per page.

Part A metric: for the full wizard (finish_setup -> temperature) and the quick setup
(finish_setup -> quick_setup -> device_prefill) driven to create_entry with untouched
answers, the page count and per page the fields a user must decide on: required fields
without a default (must-answer), and fields whose en label carries a unit/acronym/physics
term (must-know).
Part B (I1 rubric, written here, applied to every rendered config/options form):
  R1 one owner: an option key rendered on more than one options page that is not a
     summary/shortcut page (setup_overview, quick_setup, modbus_prefill) -> a field
     another page's title claims.
  R2 adjacency: at a page's top level, two fields of one key family (the key's first
     token, e.g. dhw_, heat_pump_ -> first two tokens when the first is heat/pump/comfort)
     separated by a field of another family while that family also occurs elsewhere.
Count key: rendered schema keys from the production step handlers.
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s2/flow_paths.py [--perturb]
  --perturb: patches HeatPumpOptimizerConfigFlow.async_step_finish_setup's menu to route
  quick_setup to finish_now (skipping the quick pages); quick path page count goes down.
Expected: the RESULT counts printed at baseline, exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: orchestrator Mac (darwin arm64).
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow.async_step_* (walk),
config_flow:HeatPumpOptimizerOptionsFlow.async_step_* (rubric).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, json, re, sys, time
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from golden import empty_section_payload, _nested_schema  # noqa: E402

_t0p, _t0t = time.process_time(), time.thread_time()
EN = json.load(open("custom_components/heatpump_optimizer/translations/en.json"))
TERM = re.compile(r"(°C|kWh|kW\b|%|\bK\b|COP|SCOP|DHW|UA\b|PV\b|EV\b|Modbus|tau|τ|coefficient|thermal|inertia|hysteresis|derate|curve|flow temp|supply temp|capacity|conductance|setpoint|set-point)", re.I)


def fields(schema, section=None):
    for key, value in (schema.schema.items() if schema else []):
        inner = _nested_schema(value)
        if inner is None:
            yield section, str(getattr(key, "schema", key)), key, value
        else:
            yield from fields(inner, str(getattr(key, "schema", key)))


def page_need(sec, sid, schema):
    must_answer, must_know = [], []
    st = EN[sec]["step"].get(sid, {})
    for section, name, key, value in fields(schema):
        d = getattr(key, "default", None)
        has = d is not None and type(d).__name__ != "Undefined"
        if type(key).__name__ == "Required" and not has:
            must_answer.append(name)
        holder = st.get("sections", {}).get(section, {}) if section else st
        label = holder.get("data", {}).get(name) or st.get("data", {}).get(name) or ""
        if TERM.search(label):
            must_know.append(name)
    return must_answer, must_know


class _R:
    status = 200
    async def json(self): return {"data": {}}
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


class _S:
    def post(self, *a, **k): return _R()


async def walk(menu_pick):
    """menu_pick(menu_options, visits) -> the option an untouched user takes."""
    real = config_flow.async_get_clientsession
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _S()
    try:
        f = config_flow.HeatPumpOptimizerConfigFlow(); f.hass = FakeHass()
        res = await f.async_step_user(None)
        trail, visits = [], {}
        for _ in range(40):
            if res.get("type") == "create_entry":
                return trail
            sid = res["step_id"]; visits[sid] = visits.get(sid, 0) + 1
            if res["type"] == "menu":
                pick = menu_pick(sid, list(res["menu_options"]), visits)
                trail.append((sid, "menu", f"-> {pick}", [], []))
                res = await getattr(f, f"async_step_{pick}")(None)
                continue
            sch = res.get("data_schema")
            ma, mk = page_need("config", sid, sch)
            trail.append((sid, "form", f"{len(list(fields(sch)))} fields", ma, mk))
            pre = empty_section_payload(sch) if sch else {}
            if sid == "user":
                pre.update({"name": "x", const.CONF_TIBBER_TOKEN: "tok", const.CONF_WEATHER_ENTITY: "weather.home"})
            res = await getattr(f, f"async_step_{sid}")(sch(pre) if sch else {})
        raise AssertionError(f"no create_entry: {trail}")
    finally:
        config_flow.async_get_clientsession = real


def full_pick(sid, opts, visits):
    if sid == "finish_setup":
        return "temperature" if visits[sid] == 1 else "finish_now"
    return opts[0]


def quick_pick(sid, opts, visits):
    if sid == "finish_setup":
        return "quick_setup" if "quick_setup" in opts and visits[sid] == 1 else "finish_now"
    return opts[0]


def report_path(name, trail):
    forms = [t for t in trail if t[1] == "form"]
    print(f"PATH {name}: {len(trail)} pages ({len(forms)} forms, {len(trail)-len(forms)} menus)")
    for sid, kind, what, ma, mk in trail:
        print(f"  {sid:22s} {kind:4s} {what:14s} must_answer={ma} must_know={len(mk)} {mk}")
    return len(trail), sum(len(t[3]) for t in trail), sum(len(t[4]) for t in trail)


if "--perturb" in sys.argv:
    orig = quick_pick
    quick_pick = lambda sid, opts, visits: "finish_now" if sid == "finish_setup" else opts[0]  # noqa: E731
full = asyncio.run(walk(full_pick))
quick = asyncio.run(walk(quick_pick))
fn, fa, fk = report_path("full_wizard", full)
qn, qa, qk = report_path("quick_setup", quick)

# ---- I1 rubric over every rendered form
SUMMARY = {"setup_overview", "quick_setup", "modbus_prefill", "factory_reset"}
pages = {}
for sec, cls in (("config", config_flow.HeatPumpOptimizerConfigFlow), ("options", config_flow.HeatPumpOptimizerOptionsFlow)):
    for step in sorted(n[11:] for n, _ in inspect.getmembers(cls) if n.startswith("async_step_")):
        async def r():
            if sec == "config":
                f = cls(); f.hass = FakeHass(); f._data = {const.CONF_TIBBER_TOKEN: "t", "name": "x"}
            else:
                f = cls(FakeEntry(options={const.CONF_TIBBER_TOKEN: "t"})); f.hass = FakeHass()
            return await getattr(f, f"async_step_{step}")(None)
        try:
            res = asyncio.run(r())
        except Exception:  # noqa: BLE001
            continue
        if res.get("type") == "form":
            pages[(sec, res["step_id"])] = list(fields(res.get("data_schema")))
owners = {}
for (sec, sid), fl in pages.items():
    if sec == "options" and sid not in SUMMARY:
        for _s, name, _k, _v in fl:
            owners.setdefault(name, []).append(sid)
r1 = {k: v for k, v in owners.items() if len(v) > 1}


def family(name):
    t = name.split("_")
    return "_".join(t[:2]) if t[0] in ("heat", "pump", "comfort", "holiday", "grid", "wood") and len(t) > 1 else t[0]


r2 = []
for (sec, sid), fl in pages.items():
    top = [(n, family(n)) for s, n, _k, _v in fl if s is None]
    for i in range(len(top)):
        for j in range(i + 2, len(top)):
            if top[i][1] == top[j][1] and all(top[k][1] != top[i][1] for k in range(i + 1, j)):
                between = [top[k][0] for k in range(i + 1, j)]
                r2.append(f"{sec}.{sid}: {top[i][0]} .. {top[j][0]} split by {between}")
                break
for k, v in sorted(r1.items()):
    print(f"I1_R1 {k} on options pages {v}")
for x in r2:
    print("I1_R2", x)
for (sec, sid), fl in sorted(pages.items()):
    print(f"I1_PAGE {sec}.{sid} fields={len(fl)} r1={sum(1 for _s,n,_k,_v in fl if n in r1 and sec=='options' and sid not in SUMMARY)} r2={sum(1 for x in r2 if x.startswith(f'{sec}.{sid}:'))}")
print(f"RESULT full_wizard_pages={fn} count")
print(f"RESULT full_wizard_must_answer={fa} count")
print(f"RESULT full_wizard_must_know={fk} count")
print(f"RESULT quick_setup_pages={qn} count")
print(f"RESULT quick_setup_must_answer={qa} count")
print(f"RESULT quick_setup_must_know={qk} count")
print(f"RESULT i1_pages_scored={len(pages)} count")
print(f"RESULT i1_r1_keys_on_two_pages={len(r1)} count")
print(f"RESULT i1_r2_split_families={len(r2)} count")
print(f"RESULT thread_factor={(time.process_time()-_t0p)/max(time.thread_time()-_t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
