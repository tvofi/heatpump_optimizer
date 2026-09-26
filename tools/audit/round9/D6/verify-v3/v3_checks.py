#!/usr/bin/env python3
"""D6 round 9, verifier V3 (reach and class): an independent number per finding.

METRIC (one line per finding; the finding id is the RESULT name prefix):
  s1_01_states_undocumented  states a real HeatPumpActionSensor can publish
                             (every "mode" string literal written into an action
                             dict in optimizer.py/coordinator.py, found by AST,
                             intersected with the sensor's ENUM options; idle
                             confirmed by calling get_current_action on an empty
                             result) that README's Heat Pump Action row omits.
  s1_02_page_misplaced       README field->page statements whose page (resolved
                             to a step through strings.json's real menu labels)
                             differs from the _OPTION_FIELDS step; plus the
                             same check over the README page statements OUTSIDE
                             the finder's seam rows (s1_02_other_page_claims_false).
  s1_03_disabled_undocumented entities whose entity_registry_enabled_default is
                             False on the entry the REAL config flow creates via
                             the "Finish setup now" menu, not named as disabled in
                             README (the Disabled-by-default list or its own row).
  s1_04_pinned_hours_beyond_20 hours the REAL coordinator reports pinned
                             (async_apply_manual_plan's pinned_space_steps x 0.25 h,
                             on its own horizon lattice) for one ON slot now..now+72h
                             and expires_at=now+48h, less 20 h.
  s2_01_count_delta          entities the six platforms create for the entry the
                             real flow creates, minus configuration.md's "All N
                             entities" number.
  s2_02_weather_submit_type  flow-result type returned by submitting the real
                             weather_sensitivity step (1 if create_entry else 0).
  s2_03_max_7day_drop_k      max bias drop over any 7x24 h window, CurveLearner
                             fed hourly (record_day de-duplicates per day) for 365
                             comfortable days starting at 06:00 local.
  s2_04_max_candidates       max len(candidates) handed to
                             optimizer._multi_start_minimize over five golden
                             SCENARIOS solved through HeatPumpOptimizer.optimize.
  s2_05_missing_fields       simulate_plan schema keys (as the registered
                             schema) absent from configuration.md's prose list.

RUN (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/verify-v3/v3_checks.py
  --perturb  (in memory, all at once; each metric must go to 0 / below 0.5 K):
     README gets idle+system_identification; README page names corrected;
     README row notes for the 6 DHW entities; build_override expiry clamped to
     20 h; configuration.md count set to the census; weather submit calls
     _create_setup_entry; curve_learning.MAX_DOWN_PER_WEEK=0.4; the doc list
     gets the wood fields. s2_04 has no perturbation here (the finder's moves).
EXPECTED at 1936d5ca (+ round-9 evidence), exact counts: s1_01=2, s1_02=3
  (other page claims false=0 of 3), s1_03=6 (26 disabled finish-now, 19 full
  wizard), s1_04=4.0 h on the coordinator's 96-step horizon (override live 100 h
  into a 168 h expiry=1), s2_01=1 (75 entities), s2_02=0, s2_03=0.6 K (5.0 % of
  windows > 0.5 K), s2_04 min 1 / max 5 candidates, s2_05=5.
  --perturb: 0, 0, 0, 0.25 h (a 20 h expiry pins 81 overlapping 15-min steps),
  0, 1, 0.543 K (first step is uncapped), 5 (unperturbed), 0.
  Trap: hastub's Entity models no entity_registry_enabled_default, so read the
  _attr_ fallback as upstream does (enabled_default below) or s1_03 counts 15/8.
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  MACHINE: 4-CPU linux cloud
container, CPython 3.14.  Root rule: ROOT = Path.cwd().
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import asyncio
import importlib
import json
import re
import sys
import time
import types
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

_T0P, _T0T = time.process_time(), time.thread_time()
ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]
PERTURB = "--perturb" in sys.argv

import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    config_flow as cf, const, curve_learning, manual_plan, sensor, services,
)
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PKG = ROOT / "custom_components" / "heatpump_optimizer"
README = (ROOT / "README.md").read_text()
CONFMD = (ROOT / "docs" / "configuration.md").read_text()
STRINGS = json.loads((PKG / "strings.json").read_text())
R: dict[str, object] = {}

# ---------------------------------------------------------------- s1-01
modes: set[str] = set()
for fn in ("optimizer.py", "coordinator.py", "boost.py", "pump_arbiter.py"):
    tree = ast.parse((PKG / fn).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "mode" and isinstance(v, ast.Constant) \
                        and isinstance(v.value, str):
                    modes.add(v.value)
options = set(sensor.HeatPumpActionSensor._attr_options)
publishable = (modes & options) - {"unknown"}
# idle, executed: an empty result
_b = golden.make(**golden.SCENARIOS[next(iter(golden.SCENARIOS))])
_empty = types.SimpleNamespace(timestamps=[])
idle_mode = _b["optimizer"].get_current_action(_empty, dt_util.now())["mode"]
row = next(l for l in README.splitlines() if l.startswith("| Heat Pump Action |"))
if PERTURB:
    row += " `idle` `system_identification`"
documented = set(re.findall(r"`([a-z_]+)`", row))
undoc = sorted(publishable - documented)
# real-HA display: every option must carry a state translation (ENUM validates on write)
st = STRINGS["entity"]["sensor"]["heat_pump_action"].get("state", {})
R["s1_01_ast_modes_in_options"] = len(publishable)
R["s1_01_idle_executed_is_idle"] = int(idle_mode == "idle")
R["s1_01_states_undocumented"] = len(undoc)
R["s1_01_untranslated_options"] = len([o for o in options if o not in st])
print("# s1-01 undocumented:", undoc, "| options:", sorted(options))

# ---------------------------------------------------------------- s1-02
menu = {}
for key in ("init", "advanced"):
    menu.update(STRINGS["options"]["step"].get(key, {}).get("menu_options", {}))
label2step = {v: k for k, v in menu.items()}
field_step = {f.key: f.step for f in cf._OPTION_FIELDS if isinstance(f.key, str) and f.key}
para = README[README.index("Both paths land on the same model"):]
para = para[:para.index("\n\n")]
if PERTURB:
    para = para.replace("the two-zone split\nand the power limits", "and the power limits") \
               .replace("orientation factor and SHGC are on", "and SHGC are on")
claims_pg = []  # (field key, README page label) -- my own reading of the paragraph
for seg in re.split(r";", para):
    m = re.search(r"\*\*(?:Advanced settings → )?([^*]+)\*\*", seg)
    if not m:
        continue
    page = m.group(1).strip()
    s = seg.replace("\n", " ")
    if "two-zone split" in s:
        claims_pg += [(const.CONF_INTER_ZONE_TRANSFER, page), (const.CONF_RADIATOR_POWER_FRACTION, page)]
    if "power limits" in s:
        claims_pg += [(const.CONF_HEAT_PUMP_MAX_POWER, page), (const.CONF_HEAT_PUMP_MIN_POWER, page)]
    if "masses" in s:
        claims_pg += [(const.CONF_SLAB_THERMAL_MASS, page)]
    if "buffer tank volume" in s:
        claims_pg += [(const.CONF_BUFFER_TANK_VOLUME, page)]
    if "window area" in s:
        claims_pg += [(const.CONF_WINDOW_AREA, page)]
    if "orientation factor" in s:
        claims_pg += [(const.CONF_SOLAR_ORIENTATION_FACTOR, page)]
    if "SHGC" in s:
        claims_pg += [(const.CONF_SOLAR_HEAT_GAIN_COEFF, page)]
bad = [(k, p, field_step.get(k)) for k, p in claims_pg if label2step.get(p) != field_step.get(k)]
R["s1_02_page_statements"] = len(claims_pg)
R["s1_02_page_misplaced"] = len(bad)
print("# s1-02 misplaced:", bad)
# README page statements outside the finder's C52/C53 rows (seam enumeration check)
other = [
    ("README:421 sysid toggle", const.CONF_SYSID_ENABLED, "Self-learning and diagnostics"),
    ("README:815 comfort_weight", const.CONF_COMFORT_WEIGHT, "Savings vs comfort"),
    ("README:898 ECL110 topics", const.CONF_ECL110_COMMAND_TOPIC, "Heat curve control (ECL110)"),
]
other_false = [o for o in other if label2step.get(o[2]) != field_step.get(o[1])]
R["s1_02_other_page_claims_checked"] = len(other)
R["s1_02_other_page_claims_false"] = len(other_false)
print("# s1-02 other page claims false:", other_false)


# ---------------------------------------------------------------- flow driver
def _defaults(schema, extra=None):
    payload = golden.empty_section_payload(schema)
    payload.update(extra or {})
    return schema(payload)


def drive(menu_choices):
    flow = cf.HeatPumpOptimizerConfigFlow()
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    hass.states.set("sensor.prices", FakeState("1.0"))
    flow.hass, flow.context = hass, {}
    run = asyncio.run
    res = run(flow.async_step_user())
    res = run(flow.async_step_user(_defaults(res["data_schema"], {
        const.CONF_PRICE_SOURCE: "entity", const.CONF_PRICE_ENTITY: "sensor.prices",
        const.CONF_WEATHER_ENTITY: "weather.home"})))
    it = iter(menu_choices)
    trail, weather_submit = [], None
    for _ in range(40):
        t = getattr(res.get("type"), "value", res.get("type"))
        trail.append(f"{t}:{res.get('step_id')}")
        if t == "create_entry":
            return trail, res["data"], weather_submit
        if t == "menu":
            res = run(getattr(flow, f"async_step_{next(it)}")())
            continue
        sid = res["step_id"]
        res = run(getattr(flow, f"async_step_{sid}")(_defaults(res["data_schema"])))
        if sid == "weather_sensitivity":
            weather_submit = getattr(res.get("type"), "value", res.get("type"))
    raise RuntimeError(trail)


def census(data):
    hass = FakeHass()
    hass.states.set("weather.home", FakeState("sunny"))
    entry = FakeEntry(data=dict(data))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    out = []
    for p in const.PLATFORMS:
        name = getattr(p, "value", str(p)).split(".")[-1].lower()
        mod = importlib.import_module(f"heatpump_optimizer.{name}")
        asyncio.run(mod.async_setup_entry(hass, entry, lambda ents, *a, **k: out.extend(ents)))
    return coord, out


def ent_name(e):
    plat = type(e).__module__.rsplit(".", 1)[-1]
    key = getattr(e, "_attr_translation_key", None)
    return STRINGS["entity"].get(plat, {}).get(key, {}).get("name", f"{plat}:{key}")


# ---------------------------------------------------------------- s1-03 / s2-01 / s2-02
if PERTURB:
    _orig_ws = cf.HeatPumpOptimizerConfigFlow.async_step_weather_sensitivity

    async def _ws(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self._create_setup_entry()
        return await _orig_ws(self, user_input)
    cf.HeatPumpOptimizerConfigFlow.async_step_weather_sensitivity = _ws

trail_now, data_now, _ = drive(["finish_now"])
trail_full, data_full, ws = drive(["temperature", "building_describe"])
print("# finish-now trail:", trail_now)
print("# full-wizard trail:", trail_full)
R["s2_02_weather_submit_creates_entry"] = int(ws == "create_entry")
R["s2_02_forms_after_weather"] = len(trail_full) - 1 - next(
    i for i, s in enumerate(trail_full) if s.endswith(":weather_sensitivity"))
print("# finish-now entry keys:", sorted(data_now))
_, ents_now = census(data_now)
_, ents_full = census(data_full)


def enabled_default(e):
    # Upstream Entity.entity_registry_enabled_default returns
    # self._attr_entity_registry_enabled_default (default True); the stub's Entity
    # models only entity_category, so read the property where a class defines one
    # and the _attr_ otherwise -- exactly what real Home Assistant reads.
    for klass in type(e).__mro__:
        if "entity_registry_enabled_default" in vars(klass):
            return bool(e.entity_registry_enabled_default)
    return bool(getattr(e, "_attr_entity_registry_enabled_default", True))


dis_now = [e for e in ents_now if not enabled_default(e)]
dis_full = [e for e in ents_full if not enabled_default(e)]
lst = re.search(r"Disabled by default: (.*?)\.\n", README, re.S).group(1).replace("\n", " ")
listed = {x.strip() for x in re.split(r",| and ", lst) if x.strip()}
rows = {}
for l in README.splitlines():
    if l.startswith("| "):
        rows.setdefault(l.split("|")[1].strip(), l)


def documented_disabled(name):
    if name in listed:
        return True
    r = rows.get(name, "")
    if PERTURB and name.startswith(("DHW", "Plan DHW")):
        return True
    if "disabled" in r.lower():
        return True
    # a prose sentence naming the entity and saying it is disabled
    prose = " ".join(l for l in README.splitlines() if not l.lstrip().startswith("|"))
    return any(name in sent and "disabled" in sent
               for sent in re.split(r"(?<=[.!?])\s+", prose))


und = sorted(ent_name(e) for e in dis_now if not documented_disabled(ent_name(e)))
R["s1_03_finish_now_has_tank"] = int(const.CONF_DHW_TANK_VOLUME in data_now)
R["s1_03_disabled_finish_now"] = len(dis_now)
R["s1_03_disabled_full_wizard"] = len(dis_full)
R["s1_03_disabled_undocumented"] = len(und)
print("# s1-03 undocumented:", und)
m = re.search(r"All (\d+) entities appear at once", CONFMD)
doc_n = len(ents_full) if PERTURB else int(m.group(1))
R["s2_01_entities_full_wizard"] = len(ents_full)
R["s2_01_entities_finish_now"] = len(ents_now)
R["s2_01_count_delta"] = len(ents_full) - doc_n
counts = {n: CONFMD.count(n) for n in re.findall(r"\b(\d+) entities\b", CONFMD)}
print("# s2-01 'N entities' in configuration.md:", counts)

# ---------------------------------------------------------------- s1-04 (real coordinator)
coord, _ = census(data_full)
coord.async_request_refresh = mock.AsyncMock()
services._manual_targets = lambda hass, entry: [("e1", coord)]
if PERTURB:
    _ob = services.build_override

    def _cl(**kw):
        kw["expires_at"] = min(kw["expires_at"], kw["now"] + timedelta(hours=const.MANUAL_PLAN_WINDOW_HOURS))
        return _ob(**kw)
    services.build_override = _cl
now = dt_util.now()
beyond = {}
for h in (20, 24, 48, 168):
    # one ON slot spanning 72 h: the coordinator's own response counts ON steps on its horizon
    slot = [{"start": now.isoformat(), "end": (now + timedelta(hours=72)).isoformat()}]
    call = types.SimpleNamespace(data={"space_slots": slot, "expires_at": (now + timedelta(hours=h)).isoformat()})
    resp = asyncio.run(services.handle_apply_manual_plan(None, call))
    pinned = resp["applied"]["e1"]["pinned_space_steps"]
    beyond[h] = pinned * 0.25
print("# s1-04 pinned hours by expires_at offset:", beyond,
      "| coordinator n_steps:", coord._opt_config.n_steps if hasattr(coord, "_opt_config") else
      coord._ctx._opt_config.n_steps)
R["s1_04_pinned_hours_48h"] = beyond[48]
# wall-clock duration: is a 168 h override still live 100 h later?
_ov = services.build_override(space_slots=[], dhw_slots=None,
                              expires_at=now + timedelta(hours=168), now=now)
R["s1_04_override_live_after_100h"] = int(not _ov.is_expired(now + timedelta(hours=100)))
R["s1_04_pinned_hours_beyond_20"] = max(0.0, beyond[48] - 20.0)

# ---------------------------------------------------------------- s2-03
if PERTURB:
    curve_learning.MAX_DOWN_PER_WEEK = 0.4
cl = curve_learning.CurveLearner()
t0 = datetime(2026, 1, 1, 6, 0)
hist = []
for hr in range(365 * 24):
    t = t0 + timedelta(hours=hr)
    cl.record_day(t, 1.0)
    hist.append(cl.bias)
worst = max(hist[i - 168] - hist[i] for i in range(168, len(hist)))
windows = sum(1 for i in range(168, len(hist)) if hist[i - 168] - hist[i] > 0.5 + 1e-9)
R["s2_03_max_7day_drop_k"] = round(worst, 3)
R["s2_03_windows_over_0p5_frac"] = round(windows / (len(hist) - 168), 3)

# ---------------------------------------------------------------- s2-04
seen = []
_orig_ms = opt_mod._multi_start_minimize


def _spy(objective, candidates, *a, **k):
    seen.append(len(candidates))
    return _orig_ms(objective, candidates, *a, **k)


names = list(golden.SCENARIOS)[:5]
with mock.patch.object(opt_mod, "_multi_start_minimize", _spy):
    per = {}
    for nm in names:
        before = len(seen)
        golden.capture(nm, golden.SCENARIOS[nm])
        per[nm] = seen[before:]
print("# s2-04 candidates per multistart call:", per)
R["s2_04_min_candidates"] = min(seen)
R["s2_04_max_candidates"] = max(seen)

# ---------------------------------------------------------------- s2-05
schema_keys = {str(getattr(k, "schema", k)) for k in services.SERVICE_SCHEMA_SIMULATE_PLAN.schema}
i = CONFMD.index("**`simulate_plan`**")
seg = CONFMD[i:CONFMD.index("\n\n", i)]
seg = seg[re.search(r"Fields,\s+all optional:", seg).start():]
listed_f = set(re.findall(r"`([a-z_0-9]+)`", seg))
if PERTURB:
    listed_f |= {k for k in schema_keys if k.startswith("wood_")}
missing = sorted(schema_keys - listed_f)
R["s2_05_schema_keys"] = len(schema_keys)
R["s2_05_missing_fields"] = len(missing)
print("# s2-05 missing:", missing)

# ---------------------------------------------------------------- footer
for k, v in R.items():
    print(f"RESULT {k}={v} count")
tp, tt = time.process_time() - _T0P, time.thread_time() - _T0T
print(f"RESULT perturbation={'on' if PERTURB else 'none'}")
print(f"RESULT thread_factor={tp / max(tt, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
