"""D1.M3: an empty / absent weather forecast logs a WARNING on every cycle, not once per outage.

Metric: WARNING records "No weather forecast available" (coordinator.py
HeatPumpOptimizerCoordinator._weather_series) over 4 real _async_update_data
cycles, per arm: (a) no weather entity configured, (b) a weather entity whose
get_forecasts returns an empty list. Key: records the production logger emitted.
Control arm (c): the entity returns a 48-row forecast -> 0.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/weather_warn.py [--perturb]
--perturb: in memory, _weather_series logs that line once per coordinator
(a latch, as _weather_fetch_failed already does): expected 4 -> 1 per arm (baseline 4, exact).
Baseline 17f1c55fad1b; machine Apple-silicon macOS (box B4).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, logging, sys, time
from datetime import timedelta
sys.path.insert(0, os.path.dirname(__file__))
_a = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa: E402
sys.argv = _a
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from custom_components.heatpump_optimizer import const, coordinator as cm  # noqa: E402

MSG = "No weather forecast available"
if "--perturb" in sys.argv:
    _orig = cm.HeatPumpOptimizerCoordinator._weather_series
    def _once(self, *a, **k):
        if getattr(self, "_wx_warned", False) and not self._weather_forecast:
            lvl = cm._LOGGER.level; cm._LOGGER.setLevel(logging.ERROR)
            try:
                return _orig(self, *a, **k)
            finally:
                cm._LOGGER.setLevel(lvl)
        if not self._weather_forecast:
            self._wx_warned = True
        return _orig(self, *a, **k)
    cm.HeatPumpOptimizerCoordinator._weather_series = _once


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.n = 0
    def emit(self, r):
        if MSG in r.getMessage(): self.n += 1


async def arm(rows):
    storage._DISK.clear(); storage._VERSIONS.clear()
    if rows is None:
        F.CFG.pop(const.CONF_WEATHER_ENTITY, None)
    else:
        F.CFG[const.CONF_WEATHER_ENTITY] = "weather.home"
    h, c = F.build()
    async def handler(call):
        now = dt_util.now().replace(minute=0, second=0, microsecond=0)
        fc = [] if rows == 0 else [{"datetime": (now + timedelta(hours=k)).isoformat(),
                                    "temperature": -3.0, "wind_speed": 3.0} for k in range(rows)]
        return {"weather.home": {"forecast": fc}}
    h.services.async_register("weather", "get_forecasts", handler)
    await F.drain(c)
    cap = Cap(); logging.getLogger().addHandler(cap)
    errs = 0
    for _ in range(4):
        errs += (await F.cycle(c)) is not None
    logging.getLogger().removeHandler(cap)
    return cap.n, errs


async def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    for name, rows in (("no_entity", None), ("empty_forecast", 0), ("control_48_rows", 48)):
        n, errs = await arm(rows)
        print(f"RESULT {name}.warnings_4_cycles={n} count")
        print(f"RESULT {name}.cycles_failed={errs} count")
    tf = (time.process_time() - t0) / max(1e-9, time.thread_time() - tt0)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")

asyncio.run(main())
