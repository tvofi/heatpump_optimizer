"""V3 reach for D1-s3-04 (climate publishes the away setback as the user's target mid-solve) under real HA.

Metric: max |HeatPumpOptimizerClimate.target_temperature - configured target| (degC)
read by a coordinator listener at every async_update_listeners, on the REAL
coordinator and a real hass, while a REAL solve (process worker) is awaited by a
first DataUpdateCoordinator.async_refresh and a SECOND async_refresh arrives 0.3 s
into it (what async_request_refresh from any service, or a scheduled refresh, does;
no peak guard configured, nothing synthesised at the await). Away override active
(return time with an explicit offset, so D1-s3-01 is not involved).
Count key: the value the production entity property returns at listener time.
Arms: default (second refresh); --peak-guard (peak guard on, 16 A fuse, the
whole-house meter sensor.power reads 30 kW three times 10.2 s apart from 0.3 s into
the solve, which is held open 25 s past the production solve to emulate a Pi-class
solve length: real HA's bus dispatches _on_power_event); --null (away off). Perturbation --perturb: the property reads the
configured CONF_TARGET_TEMP instead of the live solve config -> 0.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-04_realha.py [--peak-guard] [--null|--perturb]
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
NULL = "--null" in sys.argv
PEAK = "--peak-guard" in sys.argv
# Pi-class solve length: the production solve, then this many seconds more inside the
# same awaited window (asyncio.sleep, no CPU), so the guard's 10 s event spacing fits.
PI_S = 25.0 if PEAK else 0.0
PERTURB = "--perturb" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import climate as climate_mod
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import CONF_TARGET_TEMP
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.async_set("sensor.indoor", "21.4", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.outdoor", "-3.0", {"unit_of_measurement": "°C"})
    hass.states.async_set("sensor.prices", "0.5", {"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
        for h in range(48)]})
    cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "price_source": "entity", "price_entity": "sensor.prices", CONF_TARGET_TEMP: 21.0}
    if PEAK:
        cfg.update({"peak_guard_enabled": True, "house_power_entity": "sensor.power",
                    "main_fuse_amperes": 16})
        hass.states.async_set("sensor.power", "800", {"unit_of_measurement": "W"})
    entry = make_entry(cfg, entry_id="climate_mid")
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    await asyncio.sleep(0.1)
    if PEAK:
        await coord._async_setup_peak_guard()
    if not NULL:
        await coord.async_set_away(active=True,
                                   return_time=(dt_util.now() + timedelta(days=3)).isoformat(),
                                   refresh=False)
    ent = climate_mod.HeatPumpOptimizerClimate(coord, entry)
    configured = 21.0
    seen = []
    in_solve = {"on": False, "n": 0}

    def listener():
        v = ent.target_temperature
        seen.append((in_solve["on"], v))
    coord.async_add_listener(listener)
    orig_prop = climate_mod.HeatPumpOptimizerClimate.target_temperature
    fixed = property(lambda self: float(self.coordinator._ctx._config.get(CONF_TARGET_TEMP, 21.0)))
    from heatpump_optimizer import coordinator as cm
    orig_opt = cm._await_optimize

    async def watched(*a, **k):
        in_solve["on"] = True
        in_solve["n"] += 1
        try:
            r = await orig_opt(*a, **k)
            if PI_S:
                await asyncio.sleep(PI_S)
            return r
        finally:
            in_solve["on"] = False
    with mock.patch.object(cm, "_await_optimize", watched), \
         mock.patch.object(climate_mod.HeatPumpOptimizerClimate, "target_temperature", fixed if PERTURB else orig_prop):
        first = hass.async_create_task(coord.async_refresh())
        await asyncio.sleep(0.3)
        if PEAK:
            # the whole-house meter reads past the fuse while the solve runs; the guard
            # engages after consecutive over-projections MIN_EVENT_SPACING_S (10 s) apart
            for i in range(3):
                hass.states.async_set("sensor.power", str(30000 + i), {"unit_of_measurement": "W"})
                await asyncio.sleep(10.2)
        else:
            await coord.async_refresh()
        await first
        after = ent.target_temperature
    mid = [abs(v - configured) for on, v in seen if on]
    dev = max(mid) if mid else 0.0
    print(f"# arm={'null' if NULL else 'perturb' if PERTURB else 'default'} peak_guard={PEAK} solves={in_solve['n']} "
          f"writes_mid_solve={len(mid)} writes_total={len(seen)} published={[v for _, v in seen]}")
    print(f"RESULT max_published_deviation={dev:.2f} C")
    print(f"RESULT after_solve_deviation={abs(after - configured):.2f} C")

asyncio.run(main())
tail()
os._exit(0)
