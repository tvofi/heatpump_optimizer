"""V3 reach for D1-s3-01 (tz-less set_away return_time wedges the away resolution) under real HA.

Metric: for each return_time VALUE, the service data is first validated by the
production services.SERVICE_SCHEMA_SET_AWAY on the REAL homeassistant cv (real
cv.string / cv.boolean); if accepted, the REAL coordinator's async_set_away(active=True,
return_time=VALUE, refresh=False) runs on a real hass (real aware dt_util.now()), then
coordinator._resolve_away() -- the call async_run_optimization makes every solve --
runs 6 times. Reported: schema_accepted, service_raised (of 1), resolve_raises (of 6).
Values: the card's <input type=datetime-local> shape (no seconds, no offset), the
services.yaml example (seconds, no offset), and the control with an explicit offset.
Count key: exceptions out of async_set_away / _resolve_away.
Perturbation --perturb: away._parse_return_time wrapped to return dt_util.as_local(d)
for a naive d -> every count 0.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-01_realha.py [--perturb]
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
from datetime import timedelta
from unittest import mock

logging.disable(logging.CRITICAL)
PERTURB = "--perturb" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import away as away_mode
    from heatpump_optimizer import services
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    ret = dt_util.now() + timedelta(days=1)
    values = {
        "card_datetime_local": ret.strftime("%Y-%m-%dT%H:%M"),
        "services_yaml_shape": ret.strftime("%Y-%m-%dT%H:%M:%S"),
        "control_with_offset": ret.isoformat(timespec="seconds"),
    }
    orig = away_mode._parse_return_time

    def localized(raw):
        d = orig(raw)
        return dt_util.as_local(d) if d is not None and d.tzinfo is None else d
    totals = {"service_raised": 0, "resolve_raises": 0}
    with mock.patch.object(away_mode, "_parse_return_time", localized if PERTURB else orig):
        for name, v in values.items():
            try:
                data = services.SERVICE_SCHEMA_SET_AWAY({"return_time": v, "active": "on"})
                accepted = 1
            except Exception:  # noqa: BLE001
                data, accepted = None, 0
            coord = HeatPumpOptimizerCoordinator(hass, make_entry(
                {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"},
                entry_id=f"away_{name}"))
            await asyncio.sleep(0.05)
            sr = 0
            if data is not None:
                try:
                    await coord.async_set_away(active=data["active"], return_time=data["return_time"], refresh=False)
                except TypeError:
                    sr = 1
            rr = 0
            for _ in range(6):
                try:
                    coord._resolve_away()
                except TypeError:
                    rr += 1
            if name != "control_with_offset":
                totals["service_raised"] += sr
                totals["resolve_raises"] += rr
            print(f"RESULT {name}: schema_accepted={accepted} service_raised={sr} resolve_raises={rr} count_of_6 value={v!r}")
    print(f"RESULT naive_service_raised={totals['service_raised']} count_of_2")
    print(f"RESULT naive_resolve_raises={totals['resolve_raises']} count_of_12")

asyncio.run(main())
tail()
os._exit(0)
