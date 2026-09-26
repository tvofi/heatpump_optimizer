"""V3 verify of D1-s5-52: genuine homeassistant.core.State objects, through the REAL InputReader,
into the REAL sensor entities (IndoorTempSensor, DHWTemperatureSensor), on genuine Home Assistant
2026.2.3 (no tests/hastub) -- so the "published as the entity's state" half of the claim is an
executed number on the real entity, not an inference from InputReader alone.

Metric (a): of 6 temperature-input keys x {-127, 85} degC, count InputReader.read cells that
deliver the sentinel as an ok reading (ok=True, value == sentinel).
Metric (b): the REAL IndoorTempSensor and DHWTemperatureSensor entities' native_value/available,
built from a real coordinator whose one input cycle saw a -127 (and separately 85) sentinel on
the indoor and DHW entities -- reading exactly what Home Assistant would show as the entity's
published state.

Command (no tests/hastub on the path):
    PYTHONPATH=custom_components:tests /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s5-52_realha_sentinel_temps.py
Expected: delivered_sentinels=12 of 12 (matching the stub's sentinel_temps.py); the real
IndoorTempSensor/DHWTemperatureSensor publish native_value=-127.0 / 85.0 and available=True for
the -127/85 cycles -- an entity, not merely an internal reading, carries the sentinel.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Home Assistant 2026.2.3 (venvha).
"""
import sys
sys.path.insert(0, "tools/audit/round9/D1/verify-v3-leads")
import _realha_rig as rig  # noqa: E402
import asyncio  # noqa: E402
from datetime import timedelta  # noqa: E402
import homeassistant.core as core  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.inputs import InputReader  # noqa: E402
from heatpump_optimizer.sensor import IndoorTempSensor, DHWTemperatureSensor  # noqa: E402

KEYS = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
    const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.floor_return",
    const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.buffer",
    const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.lower_floor",
}


def real_state(entity_id, raw):
    return core.State(
        entity_id, raw, {"unit_of_measurement": "°C"},
        last_updated=rig.NOW - timedelta(minutes=1),
        last_reported=rig.NOW - timedelta(minutes=1),
    )


async def input_reader_delivered(raw):
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator()
        for key, eid in KEYS.items():
            coord.hass.states._states[eid] = real_state(eid, raw)
        reader = InputReader(coord.hass, dict(KEYS), now=lambda: rig.NOW)
        n = 0
        for key in KEYS:
            r = reader.read(key)
            ok = r.problem is None and r.value is not None and r.value == float(raw)
            n += ok
        return n
    finally:
        for p in stops:
            p.stop()


async def entity_publish(raw):
    """Run a real input cycle with the sentinel on indoor and DHW, then read
    the REAL entity's native_value/available -- what Home Assistant shows."""
    stops = rig.freeze_now()
    try:
        coord = await rig.abuild_coordinator(config={const.CONF_DHW_TEMP_ENTITY: "sensor.dhw"})
        coord.hass.states._states["sensor.indoor"] = real_state("sensor.indoor", raw)
        coord.hass.states._states["sensor.dhw"] = real_state("sensor.dhw", raw)
        await coord._update_current_state()
        coord.data = coord._build_data_dict()
        indoor = IndoorTempSensor(coord, coord.entry)
        dhw = DHWTemperatureSensor(coord, coord.entry)
        return {
            "indoor_available": bool(indoor.available), "indoor_native_value": indoor.native_value,
            "dhw_available": bool(dhw.available), "dhw_native_value": dhw.native_value,
        }
    finally:
        for p in stops:
            p.stop()


async def main():
    n127 = await input_reader_delivered("-127")
    n85 = await input_reader_delivered("85")
    nctl = await input_reader_delivered("21.3")
    print(f"RESULT real_delivered_minus127={n127} of_6")
    print(f"RESULT real_delivered_85={n85} of_6")
    print(f"RESULT real_delivered_sentinels={n127 + n85} of_12")
    print(f"RESULT real_control_21_3={nctl} of_6")

    e127 = await entity_publish("-127")
    e85 = await entity_publish("85")
    print(f"RESULT real_entity_minus127={e127}")
    print(f"RESULT real_entity_85={e85}")


asyncio.run(main())
rig.tail()
