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
from homeassistant.util import dt as dt_util  # noqa: E402
from custom_components.heatpump_optimizer import const, coordinator as cm  # noqa: E402
from custom_components.heatpump_optimizer import inputs as inputs_mod  # noqa: E402
from custom_components.heatpump_optimizer import pump_arbiter as pa_mod  # noqa: E402

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

#: The R10 sweep's static-only five (and the solver's per-failed-solve
#: reports), each held over four passes and latched through ``log_latch._log_held``.
#: These exercise the production site directly rather than a full cycle, so the
#: condition is held by construction.
DIRECT = {
    "solve_failure": "_note_solve_failure under a solver that always fails",
    "stale_plan": "_apply_action under a plan older than the stale bound",
    "valve_mistyped": "_command_valve_target under a mis-typed valve entity",
    "space_target_misdeclared": "_space_target under an indoor set-point whose minimum is above the room target",
    "future_stamp": "_age_gate under a future last-reported stamp",
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


class _FakeResult:
    """The two plan series ``_space_target`` reads: timestamps and set-points."""


async def direct_arm(name):
    """Hold one OWED condition over four passes and count what it logs."""
    from datetime import timedelta
    storage._DISK.clear(); storage._VERSIONS.clear()
    F.CFG.clear(); F.CFG.update(BASE)
    F.CFG.pop(const.CONF_WEATHER_ENTITY, None)
    F.CFG[const.CONF_WEATHER_ENTITY] = "weather.home"

    if name == "valve_mistyped":
        F.CFG[const.CONF_MIXING_VALVE_MODE] = "smart_write"
        F.CFG[const.CONF_MIXING_VALVE_WRITE_ENTITY] = "switch.valve"
    elif name == "space_target_misdeclared":
        F.CFG[const.CONF_SPACE_SETPOINT_ENTITY] = "number.space_setpoint"

    h, c = F.build()
    await F.drain(c)
    cap = Cap(); logging.getLogger().addHandler(cap)

    if name == "solve_failure":
        for _ in range(4):
            cm._note_solve_failure(c, RuntimeError("probe solve failure"))
    elif name == "stale_plan":
        c._mode = const.MODE_AUTO
        c._current_action = {"heat_pump_on": True, "displace_value": 0.5}
        c._last_optimization = dt_util.now() - timedelta(minutes=400)
        for _ in range(4):
            await c._apply_action()
    elif name == "valve_mistyped":
        for _ in range(4):
            await c._command_valve_target()
    elif name == "space_target_misdeclared":
        h.states.set("number.space_setpoint",
                     F.FakeState("21.0", attributes={"min": 25.0, "max": 30.0}))
        now = dt_util.now()
        inp = c.arbiter_inputs()
        result = _FakeResult()
        result.timestamps = [now]
        result.optimal_setpoints = [21.0]
        for _ in range(4):
            pa_mod._space_target(inp, result, now, "space")
    elif name == "future_stamp":
        for _ in range(4):
            st = dt_util.utcnow() + timedelta(minutes=60)
            h.states.set("sensor.indoor", F.FakeState("21.4", last_updated=st, last_reported=st))
            h.states.set("sensor.outdoor", F.FakeState("-3.0", last_updated=st, last_reported=st))
            await F.cycle(c)

    logging.getLogger().removeHandler(cap)
    return cap.c


async def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ARMS) + list(DIRECT)
    for n in names:
        c = await (direct_arm(n) if n in DIRECT else arm(n))
        floods = {m: k for m, k in c.items() if k >= 4}
        print(f"RESULT {n}.floods={len(floods)} count")
        for m, k in sorted(c.items()):
            print(f"  {k}x {m}")

asyncio.run(main())
