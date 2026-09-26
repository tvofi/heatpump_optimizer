"""V3 verify of D1-s5-51: a genuine homeassistant.core.State, through the REAL InputReader, into
the REAL IndoorTempSensor entity, on genuine Home Assistant 2026.2.3 (no tests/hastub) -- reading
what the entity actually publishes (native_value/available), not a stand-in state object.

Metric: of 7 silence cells (source state '21.3', valid in HA, last-reported/last-updated 5, 30,
59, 61, 90, 240, 480 minutes before "now"), count where IndoorTempSensor.available is False after
one real input cycle (coordinator._update_current_state + _build_data_dict). Plus the re-report
arm: last_updated 480 min ago but last_reported 5 min ago.

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s5-51_realha_indoor_silence.py
Expected: unavailable=4 of 7 (61, 90, 240, 480 min), rereport_unavailable=0 of 1 -- matching the
stub's indoor_silence.py.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402
import asyncio  # noqa: E402
from datetime import timedelta  # noqa: E402
import homeassistant.core as core  # noqa: E402
from heatpump_optimizer.sensor import IndoorTempSensor  # noqa: E402

AGES = [5, 30, 59, 61, 90, 240, 480]


async def cell(updated_ago, reported_ago):
    stops = rig.freeze_now()
    try:
        # A genuine homeassistant.core.State via a real StateMachine: last_changed is
        # forced to the older of the two timestamps (real HA's own invariant --
        # last_changed <= last_updated <= last_reported does not hold in general, but
        # StateMachine.async_set only takes ONE timestamp, so the real State object is
        # built directly to carry last_updated and last_reported independently, exactly
        # as a real report-on-change integration's state is: unchanged state ->
        # last_updated frozen, last_reported advances).
        coord = await rig.abuild_coordinator()
        updated_at = rig.NOW - timedelta(minutes=updated_ago)
        reported_at = rig.NOW - timedelta(minutes=reported_ago)
        real_state = core.State(
            "sensor.indoor", "21.3", {"unit_of_measurement": "°C"},
            last_changed=min(updated_at, reported_at),
            last_updated=updated_at,
            last_reported=reported_at,
        )
        coord.hass.states._states["sensor.indoor"] = real_state
        await coord._update_current_state()
        coord.data = coord._build_data_dict()
        ent = IndoorTempSensor(coord, coord.entry)
        return bool(ent.available), ent.native_value
    finally:
        for p in stops:
            p.stop()


async def main():
    unavail = 0
    for age in AGES:
        av, val = await cell(age, age)
        unavail += not av
        print(f"RESULT real_silent_{age}min: available={int(av)} value={val}")
    av, val = await cell(480, 5)
    print(f"RESULT real_unavailable={unavail} of_{len(AGES)}")
    print(f"RESULT real_rereport_unavailable={int(not av)} of_1 (value={val})")


asyncio.run(main())
rig.tail()
