"""V2 (independent) for D1-s5-52: physically impossible temperatures on every temperature input
key InputReader ages, plus one end-to-end publish.

Metric A: of every temperature key in const.INPUT_MAX_AGE_MINUTES (enumerated at run time: key
contains 'temp') x 4 values impossible for any of them (-127 DS18B20 no-sensor, -273.15 absolute
zero, 327.67 the int16/100 saturation code, 1000), count cells InputReader.read returns ok with the
value. Metric B: with the indoor thermometer at -127 degC (fresh, valid unit), the value
IndoorTempSensor.native_value publishes and the indoor temperature in coordinator._current_state
after one input cycle. Count key: the InputReading (ok, value) and the production entity/state.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_sentinel_census.py
Expected: keys=9; delivered=36 of 36 (exact); control 20.5 -> 9 of 9; B published=-127.0 and
cycle indoor=-127.0. Perturbation --range: a -60..150 degC window applied to the delivered value
(in memory) -> delivered=0 of 36, control 9 of 9.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import asyncio
from datetime import timedelta
from harness import FakeHass, FakeState
from heatpump_optimizer import const
from heatpump_optimizer.inputs import InputReader
from heatpump_optimizer.sensor import IndoorTempSensor

RANGE = "--range" in sys.argv
KEYS = [k for k in const.INPUT_MAX_AGE_MINUTES if "temp" in k]
BAD = ("-127", "-273.15", "327.67", "1000")


def delivered(raw):
    rig.freeze()
    hass = FakeHass()
    cfg = {}
    for i, key in enumerate(KEYS):
        cfg[key] = f"sensor.k{i}"
        hass.states.set(cfg[key], FakeState(raw, last_updated=rig.NOW - timedelta(minutes=2), unit="°C"))
    reader = InputReader(hass, cfg, now=lambda: rig.NOW)
    n = 0
    for key in KEYS:
        r = reader.read(key)
        ok = bool(r.ok) and r.value is not None
        if ok and RANGE and not (-60.0 <= r.value <= 150.0):
            ok = False
        n += ok
    return n


def end_to_end():
    rig.freeze()
    hass = rig.hass_with(states={"sensor.room": FakeState("-127", last_updated=rig.NOW - timedelta(minutes=2), unit="°C")})
    hass, entry, coord = rig.coordinator(hass=hass)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    ent = IndoorTempSensor(coord, entry)
    cs = coord._current_state
    used = getattr(cs, "indoor_temperature", None)
    if used is None:
        used = getattr(cs, "upper_floor_temperature", None)
    return ent.native_value if ent.available else "unavailable", used


total = sum(delivered(b) for b in BAD)
print(f"RESULT keys={len(KEYS)} ({','.join(KEYS)})")
print(f"RESULT delivered={total} of_{len(KEYS) * len(BAD)}")
print(f"RESULT control_20_5={delivered('20.5')} of_{len(KEYS)}")
pub, used = end_to_end()
print(f"RESULT indoor_minus127_published={pub} cycle_indoor={used}")
print(f"RESULT range_perturbation={int(RANGE)}")
rig.tail()
