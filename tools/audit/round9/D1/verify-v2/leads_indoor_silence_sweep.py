"""V2 (independent) for D1-s5-51: sweep the indoor thermometer's report silence and the shipped
staleness scale, and read both the published entity and the value the cycle uses.

Metric: over silence ages {45, 60, 61, 75, 119, 121, 239, 241, 600} min x staleness_max_age_scale
{1, 2, 4} (27 cells), with the source state '22.4' degC valid in HA (last_updated =
last_reported = now - age), count cells where IndoorTempSensor.available is False after one input
cycle, and cells where the cycle's current_state indoor temperature is not 22.4 (the reading
withheld); report the first unavailable age per scale. Count key: the entity's own available
property and coordinator._current_state (production values).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_indoor_silence_sweep.py
Expected: first unavailable age = 61 / 121 / 241 min at scale 1 / 2 / 4 (limit 60 x scale);
unavailable=7+4+2=13 of 27 and withheld=13 (exact; the cycle then uses 21.0, not 22.4).
Perturbation: the 22.4 re-reported 1 min ago (last_reported fresh, last_updated old) -> available
in every cell (--rereport).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import asyncio
from datetime import timedelta
from harness import FakeState
from heatpump_optimizer import const
from heatpump_optimizer.sensor import IndoorTempSensor

REREPORT = "--rereport" in sys.argv
AGES = (45, 60, 61, 75, 119, 121, 239, 241, 600)
SCALES = (1.0, 2.0, 4.0)


def cell(age, scale):
    rig.freeze()
    reported = 1 if REREPORT else age
    st = FakeState("22.4", last_updated=rig.NOW - timedelta(minutes=age),
                   last_reported=rig.NOW - timedelta(minutes=reported), unit="°C")
    hass = rig.hass_with(states={"sensor.room": st})
    hass, entry, coord = rig.coordinator(rig.config(**{const.CONF_STALENESS_SCALE: scale}), hass=hass)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    ent = IndoorTempSensor(coord, entry)
    cs = coord._current_state
    used = getattr(cs, "indoor_temperature", None)
    if used is None:
        used = getattr(cs, "upper_floor_temperature", None)
    return ent.available, used


unav = withheld = 0
for scale in SCALES:
    first = None
    for age in AGES:
        av, used = cell(age, scale)
        unav += not av
        withheld += used is None or abs(float(used) - 22.4) > 1e-9
        if not av and first is None:
            first = age
        print(f"RESULT scale{scale:g}_age{age}: available={int(av)} cycle_indoor={used}")
    print(f"RESULT scale{scale:g}_first_unavailable_age={first}")
print(f"RESULT unavailable={unav} of_{len(AGES) * len(SCALES)}")
print(f"RESULT withheld={withheld} of_{len(AGES) * len(SCALES)}")
print(f"RESULT rereport={int(REREPORT)}")
rig.tail()
