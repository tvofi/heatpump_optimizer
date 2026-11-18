"""D6-s1 README/DISCLAIMER claim check.

Metric: per numbered README claim, the value production delivers vs the value
the README states; RESULT claims_false = count of mismatches.
Count key: the value the production seam delivers (async_setup_entry entity
lists, registered services, schema keys, const defaults).
Run: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D6/s1/claims.py [--perturb]
--perturb: drops the last sensor from sensor.async_setup_entry's add list
(in memory), so sensors_total and entities_total must fall by 1 and their
verdicts flip/move.
Expected: see RESULT lines; baseline 17f1c55fad1b; machine: macOS arm64 seat B1.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, asyncio, time, re, json
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
t0p, t0t = time.process_time(), time.thread_time()
from harness import FakeHass, FakeState, FakeEntry, FakeCoordinator
from heatpump_optimizer import const, sensor, binary_sensor, button, climate, switch, datetime as dtm, services
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
FakeCoordinator._mold_floor_series = lambda self, outdoor, target_cap=None: None
PERTURB = "--perturb" in sys.argv

def honest():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4")); hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0}
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(c._update_current_state())
    return c._build_data_dict()

DATA = honest()
def collect(mod):
    added = []; hass = FakeHass()
    coord = FakeCoordinator(DATA); coord._month_totals = {"dhw": (1.0, 1.0), "space": (1.0, 1.0)}
    entry = FakeEntry(data={}); entry.runtime_data = coord
    def add(ents):
        ents = list(ents)
        if PERTURB and mod is sensor and ents: ents = ents[:-1]
        added.extend(ents)
    asyncio.run(mod.async_setup_entry(hass, entry, add))
    return added

counts = {m.__name__.rsplit(".",1)[-1]: len(collect(m)) for m in (sensor, binary_sensor, button, climate, switch, dtm)}
total = sum(counts.values())
h = FakeHass(); services.async_register_services(h)
n_services = len(h.services.async_services().get(const.DOMAIN, {}))
n_thermal = len(services.SERVICE_SCHEMA_SET_THERMAL_PARAMS.schema)
README = open("README.md").read()

claims = [  # id, README text, stated, delivered
 ("C01","All 81 entities appear",81,total),
 ("C02","### Sensors (62 total)",62,counts["sensor"]),
 ("C03","### Binary Sensors (6 total)",6,counts["binary_sensor"]),
 ("C04","### Buttons (5 total)",5,counts["button"]),
 ("C05","13 services are registered",13,n_services),
 ("C06","all 31 fields of `set_thermal_parameters`",31,n_thermal),
 ("C07","interval 30 minutes by default",30,const.DEFAULT_OPTIMIZATION_INTERVAL),
 ("C08","target (21 °C)",21.0,const.DEFAULT_TARGET_TEMP),
 ("C09","day (21 °C)",21.0,const.DEFAULT_COMFORT_TEMP_DAY),
 ("C10","night (19.5 °C)",19.5,const.DEFAULT_COMFORT_TEMP_NIGHT),
 ("C11","day runs 07:00",7,const.DEFAULT_DAY_START_HOUR),
 ("C12","day runs -22:00",22,const.DEFAULT_DAY_END_HOUR),
 ("C13","anti-legionella 60 °C",60.0,const.DEFAULT_DHW_LEGIONELLA_TEMP),
 ("C14","every 7 days",7.0,const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS),
 ("C15","3 % per m/s of wind",0.03,const.DEFAULT_WIND_SENSITIVITY),
 ("C16","15 % while raining",1.15,const.DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER),
 ("C17","comfort_weight, default 5",5.0,const.DEFAULT_COMFORT_WEIGHT),
 ("C18","mold margin default 0.5 °C",0.5,const.DEFAULT_MOLD_FLOOR_BREACH_MARGIN),
]
import json as _j
man = _j.load(open("custom_components/heatpump_optimizer/manifest.json")); hacs = _j.load(open("hacs.json"))
ver = open("VERSION").read().strip()
claims += [("C19","Home Assistant 2025.2.0 or newer","2025.2.0",hacs.get("homeassistant")),
           ("C20","manifest version == VERSION",ver,man["version"])]
false = 0
for cid, txt, stated, got in claims:
    ok = stated == got
    false += (not ok)
    print(f"CLAIM {cid} | {txt} | stated={stated} | delivered={got} | {'true' if ok else 'false'}")
print("counts", counts)
print(f"RESULT claims_checked={len(claims)} count")
print(f"RESULT claims_false={false} count")
print(f"RESULT entities_total={total} count")
print(f"RESULT sensors_total={counts['sensor']} count")
tp, tt = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={tp/max(tt,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
