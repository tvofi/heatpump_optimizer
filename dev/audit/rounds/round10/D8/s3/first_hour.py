"""D8.M4/M5 first-hour vs enabled-by-default matrix (round 10, seat D8-s3).

Metric: count of entity ids the card source addresses (every literal id, and
every "_suffix" the card resolves via statEntity/statNumber/derive or the
HEADLINE/ADVISOR/HEALTH suffix tables) that, on the ordinary install
(tests/entities.py #1335 recipe: _honest_coordinator + injected prices/forecast,
every platform via real async_setup_entry), are (a) disabled by default or
(b) resolve to no entity at all. Count key: the registry default delivered by
entity_registry_enabled_default on the constructed entity, and the entity_id
the platform delivers -- not a card attribute.
Command:  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round10/D8/s3/first_hour.py [--perturb]
Baseline: 17f1c55fad1b   Machine: B6 macOS arm64   Tolerance: exact (counts)
--perturb: patch heatpump_optimizer.entity.ConfiguredInputMixin.entity_registry_enabled_default
to True (in memory) -> card_disabled must go down.
Deterministic, no network; one RESULT line per violation class (D8.M5).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, re, json, time, asyncio
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, "tests")
from harness import FakeHass, FakeEntry, FakeState  # noqa
from heatpump_optimizer import (sensor, binary_sensor, button, climate,
                                switch, const, entity as ent_mod)
from heatpump_optimizer import datetime as dt_mod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

PERTURB = "--perturb" in sys.argv
t0p, t0t = time.process_time(), time.thread_time()
if PERTURB:
    ent_mod.ConfiguredInputMixin.entity_registry_enabled_default = property(lambda self: True)

def registry_default(e):
    return bool(getattr(e, "entity_registry_enabled_default",
                        getattr(e, "_attr_entity_registry_enabled_default", True)))

hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
       const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
       const.CONF_DHW_TANK_VOLUME: 180.0}
entry = FakeEntry(data=cfg)
coord = HeatPumpOptimizerCoordinator(hass, entry)
asyncio.run(coord._update_current_state())
start = datetime(2026, 1, 15)
coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (start + timedelta(hours=h)).isoformat(),
                  "level": "NORMAL"} for h in range(48)]
coord._weather_forecast = [{"datetime": (start + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                            "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
                           for h in range(48)]
coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(24)]
coord.data = coord._build_data_dict()

ents = []
for mod in (sensor, binary_sensor, button, switch, dt_mod, climate):
    added = []
    def add(es):
        for e in es:
            e.hass = hass
        added.extend(es)
    entry.runtime_data = coord
    asyncio.run(mod.async_setup_entry(hass, entry, add))
    ents.extend(added)
by_id = {e.entity_id: e for e in ents}

card = Path("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js").read_text()
ids = set(re.findall(r'"((?:sensor|binary_sensor|switch|datetime|button|climate)\.heat_pump_optimizer_[a-z_]+)"', card))
suffixes = set(re.findall(r'(?:statEntity|statNumber|derive)\("(_[a-z_]+)"\)', card))
for name in ("HEADLINE_SUFFIXES", "ADVISOR_SUFFIXES", "HEALTH_WAITING"):
    m = re.search(r"const %s = [\[{](.*?)[\]}];" % name, card, re.DOTALL)
    suffixes |= set(re.findall(r'"(_[a-z_]+)"', m.group(1)))
for name in ("HEALTH_STATUS_SUFFIX", "HEALTH_MODEL_SUFFIX"):
    suffixes |= set(re.findall(r'const %s = "(_[a-z_]+)"' % name, card))
# the narrow parse tests/entities.py uses, for comparison
narrow = set(re.findall(r'"((?:sensor|binary_sensor|switch|datetime)\.heat_pump_optimizer_[a-z_]+)"', card))
hm = re.search(r"const HEADLINE_SUFFIXES = \[(.*?)\];", card, re.DOTALL)
narrow |= {f"sensor.heat_pump_optimizer{s}" for s in re.findall(r'"(_[a-z_]+)"', hm.group(1))}
for s in suffixes:
    ids.add(f"sensor.heat_pump_optimizer{s}")

disabled, missing = [], []
for eid in sorted(ids):
    if eid in by_id:
        if not registry_default(by_id[eid]):
            disabled.append(eid)
    else:
        missing.append(eid)
narrow_disabled = sorted(e for e in narrow if e in by_id and not registry_default(by_id[e]))
for eid in disabled:
    e = by_id[eid]
    print(f"DISABLED {eid} cls={type(e).__name__} available={e.available}")
for eid in missing:
    print(f"MISSING  {eid}")
print(f"RESULT card_ids={len(ids)} ids")
print(f"RESULT entities={len(ents)} entities")
print(f"RESULT enabled={sum(registry_default(e) for e in ents)} entities")
print(f"RESULT card_disabled={len(disabled)} ids")
print(f"RESULT card_missing={len(missing)} ids")
print(f"RESULT narrow_parse_ids={len(narrow)} ids")
print(f"RESULT narrow_parse_disabled={len(narrow_disabled)} ids")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
# --- enabled entities neither the card nor README names (M4 "on but unread") ---
readme = Path("README.md").read_text()
strings = json.loads(Path("custom_components/heatpump_optimizer/strings.json").read_text())["entity"]
unread = []
for e in ents:
    if not registry_default(e) or e.entity_id in ids:
        continue
    key = getattr(e, "_attr_translation_key", None) or getattr(e, "_key", "")
    plat = e.entity_id.split(".")[0]
    name = (strings.get(plat, {}).get(key) or {}).get("name", "")
    if not (name and name in readme) and e.entity_id.split(".", 1)[1] not in readme:
        unread.append(e.entity_id)
for u in unread:
    print(f"UNREAD   {u}")
print(f"RESULT enabled_unnamed_by_card_or_readme={len(unread)} entities")
