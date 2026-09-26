"""V3 reach for D1-s3-05 (boost's two-hour maximum is an absolute instant) under real HA.

Metric: hours (15-min sampling, cap 72 h) a space boost stays live in the production
boost.apply(coord) on the REAL coordinator and a real hass: (a) jumpJ -- boost set by
boost.set_channel at T0, then the wall clock steps back J hours (the simulated clock,
swapped in memory for boost.dt_util.now since real HA has no freeze); (b)
restore_2099 -- a boost store file on a real .storage directory holding until
2099-01-01, loaded by the production boost.restore through the real Store.
Count key: coord._current_action["boost_space"] after boost.apply.
Perturbation --perturb: BoostState.expire also drops an end more than BOOST_HOURS
after now -> jump1/6/24 and restore_2099 fall to 0.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-05_realha.py [--perturb]
Expected (finder's stub numbers): jump0=2.0 jump1=3.0 jump6=8.0 jump24=26.0 restore_2099=72.0.
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import json
import logging
from datetime import datetime, timedelta
from unittest import mock

logging.disable(logging.CRITICAL)
PERTURB = "--perturb" in sys.argv
CAP_H = 72


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import boost
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import DOMAIN
    clock = {"t": dt_util.now()}
    n = iter(range(1000))

    def coord(eid=None):
        eid = eid or f"b{next(n)}"
        return HeatPumpOptimizerCoordinator(hass, make_entry({
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
            "dhw_tank_volume": 180.0}, entry_id=eid))

    def live_hours(c, start):
        live = 0
        for k in range(CAP_H * 4):
            clock["t"] = start + timedelta(minutes=15 * k)
            c._current_action = {"mode": "eco", "power": 0.5}
            boost.apply(c)
            if c._current_action.get("boost_space"):
                live += 1
            else:
                break
        return live / 4.0

    orig = boost.BoostState.expire

    def bounded(self, now):
        orig(self, now)
        for ch, end in list(self.until.items()):
            if end - now > timedelta(hours=boost.BOOST_HOURS):
                self.until.pop(ch, None)
    out = {}
    t0 = dt_util.now().replace(second=0, microsecond=0)
    with mock.patch.object(boost.dt_util, "now", lambda *a, **k: clock["t"]), \
         mock.patch.object(boost.BoostState, "expire", bounded if PERTURB else orig):
        for j in (0, 1, 6, 24):
            c = coord()
            await asyncio.sleep(0.05)
            clock["t"] = t0
            await boost.set_channel(c, "space", True, refresh=False)
            out[f"jump{j}"] = live_hours(c, t0 - timedelta(hours=j))
        eid = "b2099"
        key = f"{DOMAIN}_{eid}_boost"
        path = os.path.join(hass.config.path(".storage"), key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump({"version": 1, "minor_version": 1, "key": key, "data": {"space": {
            "until": datetime(2099, 1, 1, tzinfo=dt_util.DEFAULT_TIME_ZONE).isoformat()}}}, open(path, "w"))
        c = coord(eid)
        await asyncio.sleep(0.05)
        clock["t"] = t0
        await boost.restore(c)
        out["restore_2099"] = live_hours(c, t0)
    print(f"# arm={'perturb' if PERTURB else 'default'}")
    for k, v in out.items():
        print(f"RESULT {k}_live_hours={v:.2f} h")

asyncio.run(main())
tail()
os._exit(0)
