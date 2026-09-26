"""V3 reach for D1-s3-03 (pump_arbiter._load installs non-numeric set-point values) under real HA.

Metric: for each non-numeric set-point leaf ("55", [55], {"v": 55}) written as
written.dhw_setpoint[0] in the pump_duty store file on a real .storage directory
(stamp aware, one hour old), the count of 3 production pump_arbiter.apply(coord)
passes that raise, on the REAL coordinator and a real hass (real QuarantiningStore /
orjson load, real aware clock); plus file_still_corrupt (the corrupt leaf is still in
the file after the 3 passes). Control: the numeric leaf 55.0.
Count key: exceptions out of pump_arbiter.apply.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-03_realha.py [--control]
Expected: 3 leaves x 3 passes = 9 raises, file_still_corrupt=3; --control: 0.
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import json
import logging
from datetime import timedelta

logging.disable(logging.CRITICAL)
CONTROL = "--control" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import pump_arbiter
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import MODE_AUTO, DOMAIN
    opts = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]
    hass.states.async_set("sensor.indoor", "21.4", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.outdoor", "-3.0", {"unit_of_measurement": "°C"})
    hass.states.async_set("select.pump_mode", "Heating + DHW", {"options": opts})
    hass.states.async_set("number.dhw_set", "40", {"min": 40, "max": 63, "unit_of_measurement": "°C"})
    hass.states.async_set("number.water_set", "25", {"min": 25, "max": 63, "unit_of_measurement": "°C"})

    async def ok(call):
        return None
    hass.services.async_register("select", "select_option", ok)
    hass.services.async_register("number", "set_value", ok)
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
           "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
           "space_setpoint_unit": "flow", "dhw_tank_volume": 180.0}
    leaves = [55.0] if CONTROL else ["55", [55], {"v": 55}]
    raises = still = 0
    at = (dt_util.now() - timedelta(hours=1)).isoformat()
    for i, leaf in enumerate(leaves):
        eid = f"pd{i}"
        key = f"{DOMAIN}_{eid}_pump_duty"
        path = os.path.join(hass.config.path(".storage"), key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump({"version": 1, "minor_version": 1, "key": key,
                   "data": {"written": {"dhw_setpoint": [leaf, at]}}}, open(path, "w"))
        coord = HeatPumpOptimizerCoordinator(hass, make_entry(dict(cfg), entry_id=eid))
        coord._mode = MODE_AUTO
        await asyncio.sleep(0.05)
        for _ in range(3):
            try:
                await pump_arbiter.apply(coord)
            except TypeError:
                raises += 1
        pump_arbiter.release_listeners(coord)
        await asyncio.sleep(0.05)
        back = json.load(open(path))["data"].get("written", {}).get("dhw_setpoint", [None])[0]
        still += int(back == leaf and not isinstance(leaf, float))
    print(f"# arm={'control' if CONTROL else 'default'} leaves={leaves}")
    print(f"RESULT apply_raises={raises} count_of_{3 * len(leaves)}")
    print(f"RESULT file_still_corrupt={still} count_of_{len(leaves)}")

asyncio.run(main())
tail()
os._exit(0)
