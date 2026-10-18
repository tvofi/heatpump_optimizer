"""N-log-flood runtime probe: a persisting condition held over 4 real cycles.

Per arm, counts each distinct WARNING/ERROR message the package logs over 4
``_async_update_data`` cycles, with runs of digits folded to one placeholder.
A message logged 4 times under a condition that did not change is a flood (an
instance); the control arm must print zero floods and the script exits 1 when
any arm floods.

The digit fold is what makes a varying WARNING visible: a site that renders a
per-cycle age or failure count logs four different texts, so keying on the raw
text reads each as a one-off and reports zero. Folding the numbers measures
the condition, not the arithmetic (#2351 round 3).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py [arm ...] [--perturb]

--perturb re-introduces one line: _weather_fetch_failed's latch test is
replaced by ``if True:`` in memory, so the stale-weather arm must move 1 -> 4.

The ``recur_*`` arms (the #2351 round-6 reviewer's hold/clear/recur harness,
adopted here) ask the other half of a transition latch: a condition held for
two passes, cleared for two, then held again must log at WARNING or above on
the recurrence and log nothing while cleared. A latch whose clearing call is
missing reads ``recur=0`` and fails the script; so does a clear phase that
logs. ``recur_reload`` holds a hass-owned condition, unloads the coordinator
and holds it again on a new one, which must warn again.
"""
import os, re, sys, asyncio, logging, collections
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
#: reports), each held over four passes and latched through ``log_latch.log_held``.
#: These exercise the production site directly rather than a full cycle, so the
#: condition is held by construction.
DIRECT = {
    "solve_failure": "_note_solve_failure under a solver that always fails",
    "stale_plan": "_apply_action under a plan older than the stale bound",
    "valve_mistyped": "_command_valve_target under a mis-typed valve entity",
    "space_target_misdeclared": "_space_target under an indoor set-point whose minimum is above the room target",
    "future_stamp": "_age_gate under a future last-reported stamp",
}


_DIGITS = re.compile(r"\d+")


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.c = collections.Counter()
    def emit(self, r):
        if "heatpump" in r.name:
            self.c[_DIGITS.sub("#", r.getMessage())] += 1


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
        interval = c.effective_config.optimization_interval
        for _ in range(4):
            # Production cadence, not a frozen snapshot: the next cycle runs
            # one solve interval later (the stamp is fixed, so the age grows
            # by ``interval``) and that cycle's failed solve increments the
            # count the message renders. The round-2 arm advanced neither, so
            # all four texts were identical and the latch's per-cycle WARNING
            # was invisible (#2351 round 3).
            c._last_optimization -= timedelta(minutes=interval)
            cm._note_solve_failure(c, RuntimeError("probe solve failure"))
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


class _Count(logging.Handler):
    """WARNING-and-above records from the package whose text holds ``pat``."""
    def __init__(self, pat):
        super().__init__(logging.WARNING); self.n = 0; self.pat = pat
    def emit(self, r):
        if "heatpump" in r.name and self.pat in r.getMessage():
            self.n += 1


def _fresh(extra=None):
    storage._DISK.clear(); storage._VERSIONS.clear()
    F.CFG.clear(); F.CFG.update(BASE); F.CFG[const.CONF_WEATHER_ENTITY] = "weather.home"
    F.CFG.update(extra or {})
    return F.build()


async def _phases(pat, hold, clear):
    out = []
    for fn in (hold, clear, hold):
        cap = _Count(pat); logging.getLogger().addHandler(cap)
        for _ in range(2):
            await fn()
        logging.getLogger().removeHandler(cap); out.append(cap.n)
    return out


def _stamps(h, minutes_ahead):
    from datetime import timedelta
    st = dt_util.utcnow() + timedelta(minutes=minutes_ahead)
    for ent, val in (("sensor.indoor", "21.4"), ("sensor.outdoor", "-3.0")):
        h.states.set(ent, F.FakeState(val, last_updated=st, last_reported=st))


async def recur_arm(name):
    """``[hold, clear, recur]`` WARNING+ counts for one latched site."""
    if name == "recur_future_stamp":
        h, c = _fresh(); await F.drain(c)
        async def bad(): _stamps(h, 60); await F.cycle(c)
        async def ok(): _stamps(h, 0); await F.cycle(c)
        return await _phases("ahead of the host clock", bad, ok)
    if name == "recur_solve_failure":
        h, c = _fresh(); await F.drain(c)
        async def bad(): cm._note_solve_failure(c, RuntimeError("probe solve failure"))
        async def ok(): await F.cycle(c)  # a real successful solve
        return await _phases("Optimization failed", bad, ok)
    if name == "recur_space_target":
        h, c = _fresh({const.CONF_SPACE_SETPOINT_ENTITY: "number.space_setpoint"}); await F.drain(c)
        now = dt_util.now()
        result = _FakeResult(); result.timestamps = [now]; result.optimal_setpoints = [21.0]
        def target(low):
            h.states.set("number.space_setpoint",
                         F.FakeState("21.0", attributes={"min": low, "max": 30.0}))
            pa_mod._space_target(c.arbiter_inputs(), result, now, "space")
        async def bad(): target(25.0)
        async def ok(): target(5.0)
        return await _phases("declared an indoor set-point", bad, ok)
    if name == "recur_valve_write":
        h, c = _fresh({const.CONF_MIXING_VALVE_MODE: "smart_write",
                       const.CONF_MIXING_VALVE_WRITE_ENTITY: "number.valve"})
        await F.drain(c)
        saved = cm.write_setpoint_c
        async def raising(*_a): raise RuntimeError("probe valve offline")
        async def writing(*_a): return True
        def via(fn):
            async def run():
                cm.write_setpoint_c = fn
                c._valve_commanded_target = None  # never skipped as unchanged
                try:
                    await c._command_valve_target()
                finally:
                    cm.write_setpoint_c = saved
            return run
        return await _phases("Valve write entity", via(raising), via(writing))
    if name == "recur_reload":
        h, c = _fresh(); await F.drain(c)
        async def bad(): _stamps(h, 60); await F.cycle(c)
        cap = _Count("ahead of the host clock"); logging.getLogger().addHandler(cap)
        await bad(); first = cap.n
        await c.async_shutdown()
        c = cm.HeatPumpOptimizerCoordinator(h, F.FakeEntry(data=dict(F.CFG)))
        await bad()
        logging.getLogger().removeHandler(cap)
        return [first, 0, cap.n - first]
    raise KeyError(name)


RECUR = ("recur_future_stamp", "recur_solve_failure", "recur_space_target",
         "recur_valve_write", "recur_reload")


async def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ARMS) + list(DIRECT) + list(RECUR)
    flooded = []
    for n in names:
        if n in RECUR:
            hold, clear, recur = await recur_arm(n)
            print(f"RESULT {n}.hold={hold} clear={clear} recur={recur} count")
            if not hold or clear or not recur:
                flooded.append(n)
            continue
        c = await (direct_arm(n) if n in DIRECT else arm(n))
        floods = {m: k for m, k in c.items() if k >= 4}
        print(f"RESULT {n}.floods={len(floods)} count")
        for m, k in sorted(c.items()):
            print(f"  {k}x {m}")
        if floods:
            flooded.append(n)
    if flooded:
        print(f"PROBE FAILED: {len(flooded)} arm(s) flood or never re-warn: {', '.join(flooded)}",
              file=sys.stderr)
        sys.exit(1)

asyncio.run(main())
