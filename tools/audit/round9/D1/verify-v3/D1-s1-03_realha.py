"""V3 reach for D1-s1-03 (out-of-range DHW thermometer sample) under real Home Assistant.

Metric: the DHW temperature goes through the production input path a real install
uses -- a real homeassistant State ("-127", unit degC) read by
inputs.InputReader.read(CONF_DHW_TEMP_ENTITY) -- and the delivered value feeds
DhwProfileLearner.async_learn_dynamics (5-min ticks, glitch on day DAY 06:35).
Reported: reader_ok_for_glitch (1 = the reader delivered the glitch as a usable
value), glitch_value_delivered, and the window p90 (DrawStats.quantile 0.9, kWh)
with and without the glitch. Count key: the value InputReader delivers.
Clock: dhw_learning's dt_util.now is swapped in memory for a simulated clock
(real HA has no freeze); staleness is disabled so the simulated clock does not
age the real State.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s1-03_realha.py [--glitch -127|85|1e6] [--day 4]
Expected (--glitch -127 --day 4): reader_ok_for_glitch=1, p90 glitch 25.760 vs control 1.073 kWh
(the finder's stub numbers; any difference is a real-HA divergence).
Perturbation --reader-guard: the reader value is dropped outside [0,100] C -> p90 back to control.
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
GLITCH = float(sys.argv[sys.argv.index("--glitch") + 1]) if "--glitch" in sys.argv else -127.0
DAY = int(sys.argv[sys.argv.index("--day") + 1]) if "--day" in sys.argv else 4
GUARD = "--reader-guard" in sys.argv


async def run(hass, glitch):
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import dhw_learning
    from heatpump_optimizer.dhw_learning import DhwProfileLearner
    from heatpump_optimizer.thermal_model import ThermalParameters
    from heatpump_optimizer.inputs import InputReader
    from heatpump_optimizer.const import CONF_DHW_TEMP_ENTITY, CONF_STALENESS_ENABLED

    start = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
    clock = {"t": start}
    cfg = {CONF_DHW_TEMP_ENTITY: "sensor.dhw", CONF_STALENESS_ENABLED: False}
    params = ThermalParameters(); params.dhw_enabled = True
    heating = {"on": False}
    dl = DhwProfileLearner(hass, "g", params, frozen=lambda *a: None,
                           heating_active=lambda: heating["on"], external_heat_active=lambda: False)
    temp = 55.0
    ok_glitch = None
    delivered = None
    with mock.patch.object(dhw_learning.dt_util, "now", lambda *a, **k: clock["t"]):
        for i in range((DAY + 1) * 288):
            t = start + timedelta(minutes=5 * i)
            h = (t - start).seconds / 3600.0
            if 6.5 <= h < 7.0:
                temp -= 0.8
            elif 7.0 <= h < 8.0:
                temp = min(55.0, temp + 1.4)
            else:
                temp -= 0.03
            if h < 0.1:
                temp = 55.0
            v = temp
            is_glitch = glitch is not None and i == DAY * 288 + 6 * 12 + 36 // 5
            if is_glitch:
                v = glitch
            clock["t"] = t
            heating["on"] = 7.0 <= h < 8.0
            hass.states.async_set("sensor.dhw", repr(v), {"unit_of_measurement": "°C"})
            r = InputReader(hass, cfg, enabled=False, now=lambda: clock["t"]).read(CONF_DHW_TEMP_ENTITY)
            if is_glitch:
                ok_glitch, delivered = int(bool(r.ok)), r.value
            if not (r.ok and r.value is not None):
                continue
            if GUARD and not (0.0 <= r.value <= 100.0):
                continue
            await dl.async_learn_dynamics(r.value)
    dl.draw_stats.fold(clock["t"] + timedelta(days=1), "", 0.0)
    p90 = max((dl.draw_stats.quantile(k) or 0.0) for k in dl.draw_stats.reservoirs) if dl.draw_stats.reservoirs else 0.0
    ev = [e for v in dl.draw_stats.reservoirs.values() for e in v]
    return ok_glitch, delivered, p90, max(ev) if ev else 0.0


async def main():
    hass = await make_hass()
    c = await run(hass, None)
    g = await run(hass, GLITCH)
    print(f"# arm glitch={GLITCH} day={DAY} reader_guard={GUARD}")
    print(f"RESULT reader_ok_for_glitch={g[0]} flag")
    print(f"RESULT glitch_value_delivered={g[1]} degC")
    print(f"RESULT control_window_p90_kwh={c[2]:.3f} kWh")
    print(f"RESULT glitch_window_p90_kwh={g[2]:.3f} kWh")
    print(f"RESULT glitch_max_event_kwh={g[3]:.3f} kWh")

asyncio.run(main())
tail()
os._exit(0)
