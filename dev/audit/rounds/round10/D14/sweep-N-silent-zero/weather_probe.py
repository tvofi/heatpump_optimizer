"""Probe for the weather seam: a get_forecasts response whose rows are all
non-dict is non-empty at the guard, empty after _plausible_forecast_rows, and is
stored over a good 48-row forecast with the staleness latch cleared.
RESULT empty_ok_wipes=1 on the instance; --perturb adds the missing output guard
(an empty plausible result is refused as a failed fetch) and gives 0."""
import asyncio, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry
from heatpump_optimizer import coordinator as C

if "--perturb" in sys.argv:
    _orig = C._plausible_forecast_rows
    C._plausible_forecast_rows = lambda f: _orig(f) or (_ for _ in ()).throw(ValueError("empty"))

class Svc:
    def __init__(self): self.rows = []
    async def async_call(self, *a, **k): return {"weather.home": {"forecast": self.rows}}

cfg = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
c = C.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))
svc = Svc(); c.hass.services = svc
async def main():
    svc.rows = [{"datetime": f"2026-10-15T{h%24:02d}:00:00+00:00", "temperature": 3.0} for h in range(48)]
    await c._fetch_weather_forecast(); before, s1 = len(c._weather_forecast), c._weather_stale_since
    svc.rows = ["x"] * 48
    await c._fetch_weather_forecast(); after, s2 = len(c._weather_forecast), c._weather_stale_since
    print(f"# before={before} stale={s1}; after={after} stale={s2}")
    print(f"RESULT empty_ok_wipes={int(before == 48 and after == 0 and s2 is None)} count")
asyncio.run(main())
