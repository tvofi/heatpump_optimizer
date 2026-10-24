"""D8-s3 / D8.M4 -- an entity LIT by a setup-time input stays disabled by default.

Metric (one line): over every entity slot the initial setup flow can write
(config_flow._user_sensors_fields keys, plus modbus_prefill._NAMED -- the
device pre-fill page that runs in the setup flow and lands in entry.data), the
number of entities whose `available` goes False -> True when that one slot is
configured, yet whose registry default (entity_registry_enabled_default, read
the way tests/entities.py:registry_default reads it) stays False.
Count key: the entity's own `available` and registry default as the platform
delivers them through async_setup_entry, never a config attribute.

Command (repo root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m4_setup_inputs.py
    ... --perturb   (in memory: DHWTemperatureSensor's probe-gated default
                     replaced by a static False -- instrument sensitivity)
Expected: lit_but_off=0 (exact; a NON-finding); under --perturb 1 (up).
Note: the Compressor Frequency Advisor (static off) is NOT lit by its
setup-time slot (modbus_prefill writes compressor_freq_sensor): it waits for
the kW-per-Hz map, which needs measured power, an options-page slot.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B4 (linux).
Instrumented: heatpump_optimizer.sensor:DHWTemperatureSensor, FrequencyAdvisorSensor (and every
entity of the six platforms via async_setup_entry); config_flow:_user_sensors_fields;
modbus_prefill:_NAMED.
Null control: the same sweep over the slots whose entities already carry the
configured-input gate (floor return, lower floor, buffer tank, DHW probe)
reports them in lit_and_on, not lit_but_off.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roster  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import config_flow, modbus_prefill, sensor, const  # noqa: E402
from harness import FakeHass  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    # Instrument sensitivity (this is a non-finding at baseline): remove the
    # configured-input default from one gated sibling, as a static-off class
    # would be written; the tank probe must then land in lit_but_off.
    sensor.DHWTemperatureSensor.entity_registry_enabled_default = property(lambda self: False)

t0p, t0t = time.process_time(), time.thread_time()
BASE = {
    "tibber_token": "x", "weather_entity": "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
BASE_STATES = {"sensor.indoor": "21.4", "sensor.outdoor": "-3.0"}

setup_slots = sorted(
    {str(getattr(m, "schema", m)) for m in config_flow._user_sensors_fields(FakeHass())}
    | {k for k in modbus_prefill._NAMED if k != "unit_capacity"}
)
# Only entity pickers: a slot whose value is an entity id.
setup_slots = [s for s in setup_slots if s.endswith(("_entity", "_sensor"))]
STATE_FOR = {"switch": "on", "binary_sensor": "off", "number": "45", "select": "heat"}


def snapshot(config, states):
    hass, entry, coord = roster.build_honest(config, states, cycles=2)
    try:
        return {e.entity_id: (bool(e.available), roster.enabled_default(e))
                for _p, e in roster.collect(hass, entry, coord)}
    finally:
        dt_util.freeze(None)


base = snapshot(BASE, BASE_STATES)
lit_but_off, lit_and_on = [], []
for slot in setup_slots:
    if slot in BASE:
        continue
    domain = "sensor"
    eid = f"{domain}.probe_{slot}"
    states = dict(BASE_STATES)
    states[eid] = STATE_FOR.get(domain, "45.0")
    snap = snapshot({**BASE, slot: eid}, states)
    for ent, (avail, default) in snap.items():
        if avail and not base[ent][0]:
            (lit_and_on if default else lit_but_off).append((slot, ent))

for slot, ent in lit_but_off:
    print(f"LIT_BUT_OFF {slot} -> {ent}")
for slot, ent in lit_and_on:
    print(f"lit_and_on  {slot} -> {ent}")
print(f"RESULT setup_slots_swept={len(setup_slots)} count")
print(f"RESULT lit_and_on={len(lit_and_on)} count")
print(f"RESULT lit_but_off={len(lit_but_off)} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
