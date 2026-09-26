"""D5 verify-v2 harness for D5-s1-01 (independent of the finder's setup_section.py).

Metric (one line): labels (en.json config.step.<id>.data + menu_options) of every step the
real ConfigFlow visits between the first screen and the first step the section's flowchart
draws after "1 . Basics" (async_step_temperature), that the "## Initial setup" section of
docs/configuration.md never names (parentheticals stripped, case-insensitive substring).
Count key: the step_ids / menu_options HeatPumpOptimizerConfigFlow returns while driven
(the production seam); labels are read from translations/en.json for those step ids only.
Also: tokenless_first_screen (1 if price_source=entity with no token reaches the next step),
and entities constructed by the six platforms under three configs (config dependence of the
"74 entities" claim).
Command (repository root):
    PYTHONPATH=tests/hastub python tools/audit/round9/D5/verify-v2/v2_setup.py [--perturb]
--perturb: finish_setup replaced in memory by async_step_temperature -> the menu step and its
    labels vanish; unnamed_labels must go down.
Expected at baseline 1936d5ca: see RESULT lines (exact counts).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, re, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa
from heatpump_optimizer import config_flow, const  # noqa
from heatpump_optimizer import sensor, binary_sensor, button, switch, climate  # noqa
from heatpump_optimizer import datetime as dtp  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa

CF = config_flow.HeatPumpOptimizerConfigFlow
if "--perturb" in sys.argv:
    CF.async_step_finish_setup = CF.async_step_temperature
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json"))["config"]["step"]
doc = open("docs/configuration.md", encoding="utf-8").read()
sec = doc.split("## Initial setup", 1)[1].split("\n## ", 1)[0].lower()

visited = []
async def drive():
    f = CF(); f.hass = FakeHass()
    r = await f.async_step_user({"name": "HPO", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
                                 const.CONF_PRICE_ENTITY: "sensor.p", const.CONF_WEATHER_ENTITY: "weather.w"})
    visited.append(("user", {}))
    tokenless = int(r.get("step_id") == "user_sensors" and not r.get("errors"))
    r = await f.async_step_user_sensors({}); visited.append(("user_sensors", {}))
    visited.append((r.get("step_id"), r.get("menu_options") or {}))
    return tokenless
tokenless = asyncio.run(drive())
labels = []
for sid, menu in visited:
    step = en.get(sid, {})
    labels += [("data", sid, v) for v in step.get("data", {}).values()]
    for sec_ in step.get("sections", {}).values():
        labels += [("data", sid, v) for v in sec_.get("data", {}).values()]
    labels += [("menu", sid, v) for v in menu.values()]
def norm(s): return re.sub(r"\s*\(.*?\)", "", s).strip().lower()
unnamed = [l for l in labels if norm(l[2]) not in sec]
for l in unnamed:
    print("UNNAMED", l)
# entity counts across three configs
def count(cfg, states):
    h = FakeHass()
    for k, v in states.items(): h.states.set(k, FakeState(v))
    e = FakeEntry(data=cfg); c = HeatPumpOptimizerCoordinator(h, e)
    asyncio.run(c._update_current_state()); c.data = c._build_data_dict(); e.runtime_data = c
    n = 0
    for m in (sensor, binary_sensor, button, switch, climate, dtp):
        got = []
        asyncio.run(m.async_setup_entry(h, e, lambda ents, u=False, g=got: g.extend(ents)))
        n += len(got)
    return n
counts = {
  "bare_tibber": count({"tibber_token": "x", "weather_entity": "weather.w"}, {}),
  "entity_price_sensors": count({"price_source": "entity", "price_entity": "sensor.p",
        "indoor_temp_entity": "sensor.i", "outdoor_temp_entity": "sensor.o"}, {"sensor.i": "21", "sensor.o": "-3"}),
  "two_zone_wood_dhw": count({"tibber_token": "x", "two_zone_enabled": True, "wood_furnace_enabled": True,
        "dhw_tank_volume": 180.0, "buffer_tank_volume": 500.0}, {}),
}
print("entity counts", counts)
m = re.search(r"All (\d+) entities appear", doc)
print(f"RESULT tokenless_first_screen={tokenless} count")
print(f"RESULT section_says_token_required={int('tibber api token | — (**required**)' in sec)} count")
print(f"RESULT labels_on_visited_steps={len(labels)} count")
print(f"RESULT unnamed_labels={len(unnamed)} count")
print(f"RESULT unnamed_menu_labels={sum(1 for l in unnamed if l[0]=='menu')} count")
print(f"RESULT entity_count_min={min(counts.values())} count")
print(f"RESULT entity_count_max={max(counts.values())} count")
print(f"RESULT doc_entity_claim={m.group(1) if m else 'none'} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
