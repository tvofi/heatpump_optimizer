"""Round 9, D6, verifier V2 (independent lens): one harness per finding, own metric definitions.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round9/D6/verify-v2/v2_measure.py [--only F1,F2,...] [--null]

Prints one RESULT line per number. All numbers are counts or hours derived from driven production
symbols (contention-immune). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: round-9 G4-V2
cloud container, 4 CPU, CPython 3.14.0rc2.

Perturbations: --perturb-f1 (idle -> 'off', F1 2->1), --perturb-f2 (orientation row moved to
building_preset, F2 4->3), --perturb-f9 (wood keys dropped, F9 5->0), --null (F3 continue path 0,
F4 expires_at omitted 19 h, F7 MAX_DOWN_PER_WEEK=0.3 0.458 K).

Metrics (each keyed on what the production seam delivers):
  F1 v2_action_values_absent_from_readme  distinct HeatPumpActionSensor.native_value strings obtained by
      driving the real producers (optimizer.get_current_action on an empty result and on a pre-horizon
      clock; coordinator._run_system_identification with the experiment commanding heat) that are not
      backticked in README's "Heat Pump Action" table row.                       expected 2, exact
  F2 v2_readme_page_mismatch_fields  fields named in README's "not all on one page" paragraph whose
      _OPTION_FIELDS step label differs from the page the paragraph names (strict: only noun phrases
      that name a field unambiguously).                                            expected >=3, exact
  F3 v2_finishnow_disabled_unlisted  entities with entity_registry_enabled_default False on the entry
      the REAL config flow creates on user -> finish_setup menu -> "Finish setup now" -> overview
      submit, whose translated name is neither in README's "Disabled by default:" list nor in a README
      table row saying "disabled".  --null drives "Continue setup" instead.     expected 6 (null 0)
  F4 v2_manual_pin_hours_after_apply  largest whole hour k after apply at which the override returned
      by services.handle_apply_manual_plan(space_slots=[], expires_at=now+48h) still pins step 0 of a
      plan anchored at now+k.  --null omits expires_at.                        expected 47 (null 19)
  F5 v2_entity_census_minus_configuration_md  entities the six platforms add for the flow-created
      entry, minus the integer before "entities appear" in docs/configuration.md.   expected 1
  F6 v2_forms_after_weather_submit  flow results returned after the weather_sensitivity page is
      submitted and before create_entry, on the real "Continue setup" path; plus
      v2_flow_steps_absent_from_flowchart: real step_ids on that path whose step is not a node of the
      configuration.md flowchart (mapped by hand, listed).                         expected 1 / >=2
  F7 v2_curve_max_drop_168h  largest bias drop between any two instants 168 h apart, CurveLearner.record_day
      fed once per calendar day at a random 00:00-00:40 time with margin 1.0 K, 120 days, 20 seeds
      (max over seeds; min over seeds also printed); v2_curve_mean_rate_k_per_week the long-run mean.
      --null sets MAX_DOWN_PER_WEEK=0.3 in memory.                                  expected 0.6
  F8 v2_space_candidates_*  len(candidates) at every optimizer._multi_start_minimize call over three
      stress.build_case cells (winter single-zone no-DHW; winter single-zone DHW; winter two-zone DHW);
      v2_lbfgsb_runs_* the number of scipy L-BFGS-B minimize calls in the same solve.
  F9 v2_simulate_plan_schema_keys_missing_from_prose  keys of services.SERVICE_SCHEMA_SIMULATE_PLAN as
      handed to hass.services.async_register, absent from the backticked names of the configuration.md
      paragraph starting "**`simulate_plan`**".  expected 5; --perturb-f9 drops the wood keys before
      registration -> 0.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402

ARGS = sys.argv[1:]
NULL = "--null" in ARGS
ONLY = None
for a in ARGS:
    if a.startswith("--only"):
        ONLY = set(a.split("=", 1)[1].split(","))


def want(tag):
    return ONLY is None or tag in ONLY


README = (ROOT / "README.md").read_text()
CONFMD = (ROOT / "docs/configuration.md").read_text()
STRINGS = json.loads((ROOT / "custom_components/heatpump_optimizer/strings.json").read_text())

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
import heatpump_optimizer.config_flow as cf  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


def _schema_defaults(schema, extra=None):
    """Submit a form with every default: voluptuous fills them from an empty dict,
    sections included (recursively)."""
    import voluptuous as vol
    payload = {}
    for marker, val in schema.schema.items():
        key = str(getattr(marker, "schema", marker))
        inner = getattr(val, "schema", None)
        if inner is not None and hasattr(inner, "schema") and isinstance(getattr(inner, "schema", None), dict):
            payload[key] = {}
    payload.update(extra or {})
    return schema(payload)


def drive_flow(menu_choices):
    flow = cf.HeatPumpOptimizerConfigFlow()
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    hass.states.set("sensor.prices", FakeState("1.0"))
    flow.hass = hass
    flow.context = {}
    run = asyncio.run
    res = run(flow.async_step_user())
    trail = []
    first = True
    choices = iter(menu_choices)
    after_weather = None
    while True:
        t = res.get("type")
        t = getattr(t, "value", t)
        trail.append((t, res.get("step_id")))
        if after_weather is not None and t != "create_entry":
            after_weather.append(res.get("step_id"))
        if t == "create_entry":
            return trail, res.get("data"), after_weather
        if len(trail) > 40:
            raise RuntimeError(f"flow did not end: {trail}")
        if t == "menu":
            res = run(getattr(flow, f"async_step_{next(choices)}")())
            continue
        step = res["step_id"]
        extra = None
        if first:
            extra = {const.CONF_PRICE_SOURCE: "entity", "price_entity": "sensor.prices",
                     const.CONF_WEATHER_ENTITY: "weather.home"}
            first = False
        submitted = _schema_defaults(res["data_schema"], extra)
        res = run(getattr(flow, f"async_step_{step}")(submitted))
        if step == "weather_sensitivity":
            after_weather = []


def platform_entities(data):
    import importlib
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    entry = FakeEntry(data=dict(data))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    try:
        asyncio.run(coord._update_current_state())
    except Exception as exc:  # reported
        print(f"# input cycle raised {exc!r}")
    entry.runtime_data = coord
    out = []
    for plat in const.PLATFORMS:
        name = getattr(plat, "value", str(plat)).split(".")[-1].lower()
        mod = importlib.import_module(f"heatpump_optimizer.{name}")
        got = []
        asyncio.run(mod.async_setup_entry(hass, entry, lambda ents, *_a, **_k: got.extend(ents)))
        out.extend((name, e) for e in got)
    return out


def entity_name(domain, e):
    key = getattr(e, "translation_key", None) or getattr(e, "_attr_translation_key", None)
    n = STRINGS.get("entity", {}).get(domain, {}).get(key, {}).get("name")
    return n or getattr(e, "_attr_name", None) or key


def enabled_default(e):
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))


# ---------------------------------------------------------------- F1 (D6-s1-01)
if want("F1"):
    from heatpump_optimizer.sensor import HeatPumpActionSensor
    from heatpump_optimizer.optimizer import OptimizationResult
    from heatpump_optimizer.sysid import PHASE_ARMED
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
    hass = FakeHass({"sensor.indoor": FakeState("21.0"), "sensor.outdoor": FakeState("2.0"),
                     "weather.home": FakeState("sunny")})
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    if "--perturb-f1" in ARGS:
        # perturbation: _idle_action publishes 'off' (a documented state) -> metric 2 -> 1
        _orig_idle = type(coord._optimizer)._idle_action
        type(coord._optimizer)._idle_action = lambda self: {**_orig_idle(self), "mode": "off"}
    sensor = HeatPumpActionSensor(coord, entry)
    published = set()
    # producer 1: empty result
    empty = OptimizationResult.__new__(OptimizationResult)
    empty.timestamps = []
    act = coord._optimizer.get_current_action(empty, datetime(2026, 1, 5, 12, tzinfo=timezone.utc))
    coord.data = {"current_action": act}
    published.add(sensor.native_value)
    # producer 2: pre-horizon clock, beyond one step
    pre = OptimizationResult.__new__(OptimizationResult)
    t0 = datetime(2026, 1, 5, 12, tzinfo=timezone.utc)
    pre.timestamps = [t0, t0 + timedelta(minutes=15)]
    act = coord._optimizer.get_current_action(pre, t0 - timedelta(hours=1))
    coord.data = {"current_action": act}
    published.add(sensor.native_value)
    # producer 3: system identification commanding heat (experiment's decision stubbed, label real)
    coord._current_action = {"power": 1.0, "mode": "normal", "space_reason": None, "dhw_reason": None}
    coord._sysid.phase = PHASE_ARMED
    coord._sysid.step = lambda **kw: 2.0
    try:
        coord._run_system_identification(np.array([1.0] * 96))
    except Exception as exc:
        print(f"# sysid drive raised {exc!r}")
    coord.data = {"current_action": coord._current_action}
    published.add(sensor.native_value)
    row = next(l for l in README.splitlines() if l.startswith("| Heat Pump Action |"))
    documented = set(re.findall(r"`([a-z_]+)`", row))
    absent = sorted(v for v in published if v not in documented)
    print(f"# F1 published={sorted(published)} documented={sorted(documented)} absent={absent}")
    elsewhere = {v: [str(p) for p in sorted((ROOT / 'docs').glob('*.md'))
                     if f"`{v}`" in p.read_text() and 'audit' not in p.name and 'plan' not in p.name
                     and 'backlog' not in p.name and 'HANDOVER' not in p.name]
                 for v in absent}
    print(f"# F1 absent values backticked in user docs/*.md: {elsewhere}")
    print(f"RESULT v2_action_values_absent_from_readme={len(absent)} count")

# ---------------------------------------------------------------- F2 (D6-s1-02)
if want("F2"):
    if "--perturb-f2" in ARGS:
        # perturbation: render solar_orientation_factor on building_preset -> metric 4 -> 3
        import dataclasses
        cf._OPTION_FIELDS = tuple(
            (dataclasses.replace(r, step="building_preset") if dataclasses.is_dataclass(r) else r._replace(step="building_preset"))
            if r.key == const.CONF_SOLAR_ORIENTATION_FACTOR else r
            for r in cf._OPTION_FIELDS)
    pages = {p.step: p.label for p in cf._OPTION_PAGES}
    step_of = {row.key: row.step for row in cf._OPTION_FIELDS}
    para = README[README.index("Both paths land on the same model"):]
    para = para[:para.index("\n\n")]
    flat = " ".join(para.split())
    # the paragraph's own sentence structure: "<list> are on **X**; <thing> is on **Y**; <list> are on **Z**."
    clauses = re.findall(r"([^;.]*?) (?:are|is) on \*\*(?:Advanced settings → )?([^*]+)\*\*", flat)
    phrase_keys = {
        # unambiguous noun phrases only
        "two-zone split": [const.CONF_INTER_ZONE_TRANSFER, const.CONF_RADIATOR_POWER_FRACTION,
                           const.CONF_UPPER_FLOOR_AREA_RATIO],
        "power limits": [const.CONF_HEAT_PUMP_MAX_POWER, getattr(const, "CONF_HEAT_PUMP_MIN_POWER", "heat_pump_min_power")],
        "buffer tank volume": [const.CONF_BUFFER_TANK_VOLUME],
        "window area": [const.CONF_WINDOW_AREA],
        "orientation factor": [const.CONF_SOLAR_ORIENTATION_FACTOR],
        "SHGC": [const.CONF_SOLAR_HEAT_GAIN_COEFF],
    }
    mismatch, checked = [], []
    for text, page in clauses:
        for phrase, keys in phrase_keys.items():
            if phrase in text:
                for k in keys:
                    if k not in step_of:
                        print(f"# F2 {k} not an options field")
                        continue
                    real = pages[step_of[k]]
                    checked.append((k, page.strip(), real))
                    if real != page.strip():
                        mismatch.append((phrase, k, page.strip(), real))
    for c in checked:
        print(f"# F2 checked {c}")
    for m in mismatch:
        print(f"# F2 MISMATCH {m}")
    # the ambiguous phrase "The masses, losses": per-floor keys, reported separately
    perfloor = [const.CONF_UPPER_FLOOR_THERMAL_MASS, const.CONF_LOWER_FLOOR_THERMAL_MASS,
                const.CONF_UPPER_FLOOR_HEAT_LOSS, const.CONF_LOWER_FLOOR_HEAT_LOSS]
    print(f"# F2 per-floor masses/losses live on: {sorted({pages[step_of[k]] for k in perfloor})}")
    print(f"RESULT v2_readme_page_mismatch_fields={len(mismatch)} count")
    print(f"RESULT v2_readme_page_fields_checked={len(checked)} count")

# ---------------------------------------------------------------- F3 / F5 / F6
flow_cache = {}


def flow(kind):
    if kind not in flow_cache:
        choices = {"finish_now": ["finish_now"],
                   "continue": ["temperature", "building_describe"]}[kind]
        flow_cache[kind] = drive_flow(choices)
    return flow_cache[kind]


if want("F3"):
    kind = "continue" if NULL else "finish_now"
    trail, data, _ = flow(kind)
    print(f"# F3 path={kind} trail={trail}")
    print(f"# F3 entry keys={sorted(data)}")
    ents = platform_entities(data)
    disabled = [(d, entity_name(d, e)) for d, e in ents if not enabled_default(e)]
    lst = README[README.index("Disabled by default:"):]
    lst = " ".join(lst[:lst.index("\n\n")].split())
    rows_disabled = set()
    for l in README.splitlines():
        if l.startswith("| ") and re.search(r"[Dd]isabled", l):
            rows_disabled.add(l.split("|")[1].strip())
    unlisted = [(d, n) for d, n in disabled if n not in lst and n not in rows_disabled]
    print(f"# F3 disabled={len(disabled)} unlisted={unlisted}")
    print(f"RESULT v2_disabled_total={len(disabled)} count")
    print(f"RESULT v2_finishnow_disabled_unlisted={len(unlisted)} count  (path={kind})")

if want("F5"):
    for kind in ("continue", "finish_now"):
        trail, data, _ = flow(kind)
        n = len(platform_entities(data))
        m = re.search(r"All (\d+) entities appear", CONFMD)
        print(f"RESULT v2_entities_{kind}={n} count")
        print(f"RESULT v2_entity_census_minus_configuration_md_{kind}={n - int(m.group(1))} count  (doc says {m.group(1)})")

if want("F6"):
    trail, data, after = flow("continue")
    print(f"# F6 trail={trail}")
    print(f"RESULT v2_forms_after_weather_submit={len(after)} count  ({after})")
    fc = CONFMD[CONFMD.index("```mermaid"):]
    fc = fc[:fc.index("```\n", 10)]
    # my hand mapping of real step_ids to flowchart node text
    node_words = {
        "user": "Basics", "temperature": "Temperatures", "building": "describe your building",
        "building_describe": "Questionnaire", "building_extras": "Your heat pump",
        "dhw": "Hot water", "weather_sensitivity": "Weather sensitivity",
    }
    steps = [s for t, s in trail if t in ("form", "menu")]
    absent = [s for s in steps if not (s in node_words and node_words[s] in fc)]
    print(f"RESULT v2_flow_steps_absent_from_flowchart={len(absent)} count  ({absent})")

# ---------------------------------------------------------------- F4 (D6-s1-04)
if want("F4"):
    import heatpump_optimizer.services as svc
    from homeassistant.util import dt as dt_util
    now = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
    captured = []

    class _Coord:
        async def async_apply_manual_plan(self, ov):
            captured.append(ov)
            return {"ok": True}

    class _Call:
        def __init__(self, data):
            self.data = data

    data = {"space_slots": []}
    if not NULL:
        data["expires_at"] = (now + timedelta(hours=48)).isoformat()
    with mock.patch.object(dt_util, "now", lambda: now), \
         mock.patch.object(svc, "_manual_targets", lambda hass, t: [("e1", _Coord())]):
        asyncio.run(svc.handle_apply_manual_plan(FakeHass(), _Call(data)))
    ov = captured[0]
    last_k = -1
    for k in range(0, 73):
        anchor = now + timedelta(hours=k)
        steps = [anchor + timedelta(minutes=15 * i) for i in range(96)]
        pins = ov.channel_pins("space", steps)
        if pins is not None and not np.isnan(pins[0]):
            last_k = k
    print(f"RESULT v2_manual_pin_hours_after_apply={last_k} h  (expires_at {'omitted' if NULL else 'now+48h'}; README says up to 20)")

# ---------------------------------------------------------------- F7 (D6-s2-03)
if want("F7"):
    import heatpump_optimizer.curve_learning as cl
    patch = mock.patch.object(cl, "MAX_DOWN_PER_WEEK", 0.3) if NULL else mock.patch.object(cl, "MAX_DOWN_PER_WEEK", cl.MAX_DOWN_PER_WEEK)
    worst, best, rates = [], [], []
    with patch:
        for seed in range(20):
            rnd = random.Random(seed)
            L = cl.CurveLearner()
            t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
            hist = [(t0, 0.0)]
            for d in range(120):
                t = t0 + timedelta(days=d, minutes=rnd.uniform(0, 40))
                L.record_day(t, 1.0)
                hist.append((t, L.bias))
            # bias(t) is a step function; evaluate max drop between any instants 168 h apart
            def bias_at(x):
                b = 0.0
                for tt, bb in hist:
                    if tt <= x:
                        b = bb
                return b
            mx = 0.0
            for tt, _ in hist:
                for anchor in (tt - timedelta(hours=168), tt - timedelta(hours=168) + timedelta(seconds=1)):
                    mx = max(mx, bias_at(anchor) - bias_at(tt))
            worst.append(mx)
            # mean rate over days 7..42 (before the -4 K clamp at ~day 60)
            b7, b42 = bias_at(t0 + timedelta(days=7, hours=1)), bias_at(t0 + timedelta(days=42, hours=1))
            rates.append((b7 - b42) / 5.0)
    print(f"RESULT v2_curve_max_drop_168h={max(worst):.3f} K  (min over seeds {min(worst):.3f}; MAX_DOWN_PER_WEEK={'0.3 null' if NULL else '0.5'})")
    print(f"RESULT v2_curve_mean_rate_k_per_week={np.mean(rates):.3f} K/week")

# ---------------------------------------------------------------- F8 (D6-s2-04)
if want("F8"):
    import stress
    import heatpump_optimizer.optimizer as optmod
    import scipy.optimize as so
    orig = optmod._multi_start_minimize
    cells = [("sz_nodhw", dict(season="winter", two_zone=False, dhw=False)),
             ("sz_dhw", dict(season="winter", two_zone=False, dhw=True)),
             ("tz_dhw", dict(season="winter", two_zone=True, dhw=True))]
    for tag, kw in cells:
        calls = []
        lb = [0]
        real_min = so.minimize

        def spy(objective, candidates, *a, **k):
            calls.append(len(candidates))
            return orig(objective, candidates, *a, **k)

        def cnt(*a, **k):
            if k.get("method", a[2] if len(a) > 2 else None) == "L-BFGS-B":
                lb[0] += 1
            return real_min(*a, **k)

        with mock.patch.object(optmod, "_multi_start_minimize", spy), \
             mock.patch.object(so, "minimize", cnt):
            if hasattr(optmod, "minimize"):
                with mock.patch.object(optmod, "minimize", cnt):
                    stress.build_case(**kw)
            else:
                stress.build_case(**kw)
        print(f"RESULT v2_space_candidates_{tag}={calls} per multi-start call")
        print(f"RESULT v2_lbfgsb_runs_{tag}={lb[0]} count")

# ---------------------------------------------------------------- F9 (D6-s2-05)
if want("F9"):
    import heatpump_optimizer.services as svc
    registered = {}

    class _Svc:
        def async_register(self, domain, name, handler, schema=None, supports_response=None):
            registered[name] = schema

        def has_service(self, *a):
            return False

    hass = FakeHass()
    hass.services = _Svc()
    if "--perturb-f9" in ARGS:
        # perturbation: register simulate_plan without the five wood keys -> metric to 0
        import voluptuous as vol
        svc.SERVICE_SCHEMA_SIMULATE_PLAN = vol.Schema(
            {m: v for m, v in svc.SERVICE_SCHEMA_SIMULATE_PLAN.schema.items()
             if not str(getattr(m, "schema", m)).startswith("wood_")})
    r = svc.async_register_services(hass)
    if asyncio.iscoroutine(r):
        asyncio.run(r)
    schema = registered["simulate_plan"]
    keys = {str(getattr(m, "schema", m)) for m in schema.schema}
    para = CONFMD[CONFMD.index("**`simulate_plan`**"):]
    para = para[:para.index("\n\n")]
    named = set(re.findall(r"`([a-z_0-9]+)`", para))
    missing = sorted(keys - named)
    print(f"# F9 schema={len(keys)} named={len(named & keys)} missing={missing}")
    print(f"RESULT v2_simulate_plan_schema_keys_missing_from_prose={len(missing)} count")

_p, _t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT thread_factor={_p / _t if _t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in Path('/proc/vmstat').read_text().splitlines() if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
