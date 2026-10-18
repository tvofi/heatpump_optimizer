"""N-log-flood runtime probe: a persisting condition held over 4 real cycles.

Per arm, counts each distinct WARNING/ERROR message (first 48 chars) the
package logs over 4 _async_update_data cycles. A message logged 4 times
under a condition that did not change is a flood (an instance); the control
arm must print zero floods.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py [arm ...] [--perturb]

--perturb re-introduces one line: _weather_fetch_failed's latch test is
replaced by ``if True:`` in memory, so the stale-weather arm must move 1 -> 4.
"""
import os, sys, asyncio, logging, collections
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "D1", "s2"))
_a = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa: E402
sys.argv = _a
from homeassistant.helpers import storage  # noqa: E402
from custom_components.heatpump_optimizer import const, coordinator as cm  # noqa: E402

if "--perturb" in sys.argv:
    import inspect, textwrap
    src = textwrap.dedent(inspect.getsource(cm.HeatPumpOptimizerCoordinator._weather_fetch_failed))
    src = src.replace("if not self._weather_outage_cycles:", "if True:", 1)
    ns = {}; exec(compile(src, cm.__file__, "exec"), cm.__dict__, ns)
    cm.HeatPumpOptimizerCoordinator._weather_fetch_failed = ns["_weather_fetch_failed"]

BASE = dict(F.CFG)
ARMS = {
    "control": ({}, None),
    "no_weather_entity": ({"__drop__": const.CONF_WEATHER_ENTITY}, None),
    "weather_fetch_fails": ({const.CONF_WEATHER_ENTITY: "weather.missing"}, None),
    "open_meteo_no_coord": ({const.CONF_SOLAR_FORECAST_SOURCE: const.SOLAR_SOURCE_OPEN_METEO,
                             const.CONF_SOLAR_LOCATION: {"latitude": None}}, "nohome"),
    "open_meteo_bad_coord": ({const.CONF_SOLAR_FORECAST_SOURCE: const.SOLAR_SOURCE_OPEN_METEO,
                              const.CONF_SOLAR_LOCATION: {"latitude": "x", "longitude": "y"}}, "nohome"),
    "no_prices": ({}, "noprices"),
    "bad_peak_months": ({const.CONF_PEAK_TARIFF_ENABLED: True, const.CONF_PEAK_TARIFF_MONTHS: "Smarch"}, None),
    "bad_peak_hours": ({const.CONF_PEAK_TARIFF_ENABLED: True, const.CONF_PEAK_TARIFF_HOURS: "25:99-xx"}, None),
}


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.c = collections.Counter()
    def emit(self, r):
        if "heatpump" in r.name:
            self.c[r.getMessage()[:48]] += 1


async def arm(name):
    over, mode = ARMS[name]
    storage._DISK.clear(); storage._VERSIONS.clear()
    F.CFG.clear(); F.CFG.update(BASE)
    F.CFG.pop(const.CONF_WEATHER_ENTITY, None)
    if name != "no_weather_entity":
        F.CFG[const.CONF_WEATHER_ENTITY] = "weather.home"
    F.CFG.update({k: v for k, v in over.items() if k != "__drop__"})
    h, c = F.build()
    if name != "weather_fetch_fails":
        from datetime import timedelta
        from homeassistant.util import dt as dt_util
        async def handler(call):
            now = dt_util.now().replace(minute=0, second=0, microsecond=0)
            return {"weather.home": {"forecast": [{"datetime": (now + timedelta(hours=k)).isoformat(),
                    "temperature": -3.0, "wind_speed": 3.0} for k in range(48)]}}
        h.services.async_register("weather", "get_forecasts", handler)
    if mode == "nohome":
        h.config.latitude = None; h.config.longitude = None
    if mode == "noprices":
        async def fp():
            c._prices = []
        c._fetch_tibber_prices = fp
    await F.drain(c)
    cap = Cap(); logging.getLogger().addHandler(cap)
    for _ in range(4):
        await F.cycle(c)
    logging.getLogger().removeHandler(cap)
    return cap.c


async def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ARMS)
    for n in names:
        c = await arm(n)
        floods = {m: k for m, k in c.items() if k >= 4}
        print(f"RESULT {n}.floods={len(floods)} count")
        for m, k in sorted(c.items()):
            print(f"  {k}x {m}")

asyncio.run(main())
