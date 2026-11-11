"""D1-s5 lead probe: DS18B20 sentinel temperatures (-127 degC 'no sensor', 85 degC 'power-on reset')
are delivered as ok readings by InputReader.

Metric: of 6 temperature inputs (indoor, outdoor, dhw, floor return, buffer tank, lower floor) x 2
sentinels, count cells InputReader.read delivers as ok with the sentinel as value. Count key: the
InputReading (ok, value) production hands every consumer.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/sentinel_temps.py [--range]
--range (perturbation): a plausibility window (-60..110 degC outside the DHW/buffer keys' 0..100,
indoor/floor 0..45) applied to the reading in memory -> fewer delivered.
Null control: 21.3 on every key -> 6 of 6 ok.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
from datetime import timedelta
from harness import FakeHass, FakeState
from heatpump_optimizer import const
from heatpump_optimizer.inputs import InputReader

RANGE = "--range" in sys.argv
KEYS = {
    const.CONF_INDOOR_TEMP_ENTITY: (0, 45), const.CONF_OUTDOOR_TEMP_ENTITY: (-60, 60),
    const.CONF_DHW_TEMP_ENTITY: (0, 100), const.CONF_FLOOR_RETURN_TEMP_ENTITY: (0, 60),
    const.CONF_BUFFER_TANK_TEMP_ENTITY: (0, 100), const.CONF_LOWER_FLOOR_TEMP_ENTITY: (0, 45),
}


def delivered(raw):
    _rig.freeze()
    hass = FakeHass()
    cfg = {}
    for i, key in enumerate(KEYS):
        eid = f"sensor.t{i}"
        cfg[key] = eid
        hass.states.set(eid, FakeState(raw, last_updated=_rig.NOW - timedelta(minutes=1), unit="°C"))
    reader = InputReader(hass, cfg, now=lambda: _rig.NOW)
    n = 0
    for key, (lo, hi) in KEYS.items():
        r = reader.read(key)
        ok = r.ok and r.value is not None
        if ok and RANGE and not (lo <= r.value <= hi):
            ok = False
        n += ok
    return n


s127, s85, ctl = delivered("-127"), delivered("85"), delivered("21.3")
print(f"RESULT delivered_minus127={s127} of_6")
print(f"RESULT delivered_85={s85} of_6")
print(f"RESULT delivered_sentinels={s127 + s85} of_12")
print(f"RESULT control_21_3={ctl} of_6")
_rig.tail()
