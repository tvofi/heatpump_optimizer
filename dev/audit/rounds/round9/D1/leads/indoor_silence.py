"""Carried lead (orchestrator, #1643): the integration's Indoor Temperature sensor goes unavailable
while Home Assistant still holds a valid indoor reading, once the thermometer has been silent for
more than INPUT_MAX_AGE_MINUTES[indoor] = 60 min.

Metric: of 7 silence cells (source state '21.3' degC, valid in HA, last reported 5/30/59/61/90/240/
480 min ago), count those where IndoorTempSensor.available is False after a real input cycle
(_update_current_state + _build_data_dict). Plus the re-report arm: last_updated 480 min ago but
last_reported 5 min ago (a sensor re-writing an unchanged value). Count key: the entity's own
available property (reading_ok['upper_floor_temperature'] from InputReader._age_gate).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/indoor_silence.py [--scale 8]
Expected: unavailable=4 of 7 (61/90/240/480 min), rereport_unavailable=0 (InputReader honours
last_reported, so D1-s5-01's age_of mechanism is not this path). --scale 8 (perturbation: the shipped
staleness_max_age_scale option at its ceiling) or --no-watchdog (staleness_watchdog_enabled off)
-> fewer / 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio
from datetime import timedelta
from harness import FakeState
from heatpump_optimizer import const
from heatpump_optimizer.sensor import IndoorTempSensor

extra = {}
if "--scale" in sys.argv:
    extra[const.CONF_STALENESS_SCALE] = float(sys.argv[sys.argv.index("--scale") + 1])
if "--no-watchdog" in sys.argv:
    extra[const.CONF_STALENESS_ENABLED] = False
AGES = [5, 30, 59, 61, 90, 240, 480]


def cell(updated_ago, reported_ago):
    _rig.freeze()
    st = FakeState("21.3", last_updated=_rig.NOW - timedelta(minutes=updated_ago),
                   last_reported=_rig.NOW - timedelta(minutes=reported_ago), unit="°C")
    hass = _rig.make_hass(states={"sensor.indoor": st})
    hass, entry, coord = _rig.make_coord(_rig.base_config(**extra), hass=hass)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    ent = IndoorTempSensor(coord, entry)
    return ent.available, ent.native_value


unavail = 0
for age in AGES:
    av, val = cell(age, age)
    unavail += not av
    print(f"RESULT silent_{age}min: available={int(av)} value={val}")
av, val = cell(480, 5)
print(f"RESULT unavailable={unavail} of_{len(AGES)}")
print(f"RESULT rereport_unavailable={int(not av)} of_1 (value={val})")
_rig.tail()
