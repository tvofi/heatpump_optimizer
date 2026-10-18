"""Reviewer's own harness (not the finder's): does a condition that CLEARS and
then RECURS log a WARNING/ERROR on recurrence? Phases: hold (2) -> clear (2) ->
recur (2). A transition latch owes >=1 on recurrence; a flood logs 2."""
import os, sys, re, asyncio, logging, collections
from datetime import timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "D1", "s2"))
_a = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa
sys.argv = _a
from homeassistant.helpers import storage  # noqa
from homeassistant.util import dt as dt_util  # noqa
from custom_components.heatpump_optimizer import const, coordinator as cm  # noqa
from custom_components.heatpump_optimizer import pump_arbiter as pa  # noqa
BASE = dict(F.CFG)

class Cap(logging.Handler):
    def __init__(self, pat):
        super().__init__(logging.WARNING); self.n = 0; self.pat = pat
    def emit(self, r):
        if "heatpump" in r.name and self.pat in r.getMessage(): self.n += 1

def fresh(extra=None):
    storage._DISK.clear(); storage._VERSIONS.clear()
    F.CFG.clear(); F.CFG.update(BASE); F.CFG[const.CONF_WEATHER_ENTITY] = "weather.home"
    F.CFG.update(extra or {})
    return F.build()

async def phases(name, pat, hold, clear):
    out = []
    for ph, fn in (("hold", hold), ("clear", clear), ("recur", hold)):
        cap = Cap(pat); logging.getLogger().addHandler(cap)
        for _ in range(2): await fn()
        logging.getLogger().removeHandler(cap); out.append(cap.n)
    print(f"RESULT {name}.hold={out[0]} clear={out[1]} recur={out[2]} count")

async def main():
    # future_stamp: owner hass (inputs._age_gate)
    h, c = fresh(); await F.drain(c)
    async def fut():
        st = dt_util.utcnow() + timedelta(minutes=60)
        h.states.set("sensor.indoor", F.FakeState("21.4", last_updated=st, last_reported=st))
        h.states.set("sensor.outdoor", F.FakeState("-3.0", last_updated=st, last_reported=st))
        await F.cycle(c)
    async def ok():
        st = dt_util.utcnow()
        h.states.set("sensor.indoor", F.FakeState("21.4", last_updated=st, last_reported=st))
        h.states.set("sensor.outdoor", F.FakeState("-3.0", last_updated=st, last_reported=st))
        await F.cycle(c)
    await phases("future_stamp", "ahead of the host clock", fut, ok)

    # solve_failure: owner coordinator; clear = a real successful cycle
    h, c = fresh(); await F.drain(c)
    async def fail(): cm._note_solve_failure(c, RuntimeError("probe solve failure"))
    async def good():
        await F.cycle(c)
    await phases("solve_failure", "Optimization failed", fail, good)
    print(f"  solve_failures_after={c._solve_failures}")

    # space_target: owner hass; clear = entity min fixed
    h, c = fresh({const.CONF_SPACE_SETPOINT_ENTITY: "number.space_setpoint"}); await F.drain(c)
    now = dt_util.now()
    class R: pass
    r = R(); r.timestamps = [now]; r.optimal_setpoints = [21.0]
    async def bad():
        h.states.set("number.space_setpoint", F.FakeState("21.0", attributes={"min": 25.0, "max": 30.0}))
        pa._space_target(c.arbiter_inputs(), r, now, "space")
    async def fixed():
        h.states.set("number.space_setpoint", F.FakeState("21.0", attributes={"min": 5.0, "max": 30.0}))
        pa._space_target(c.arbiter_inputs(), r, now, "space")
    await phases("space_target", "declared an indoor set-point", bad, fixed)

    # reload: future_stamp on a NEW coordinator, same hass (entry reload)
    h, c = fresh(); await F.drain(c)
    await fut()
    c2 = cm.HeatPumpOptimizerCoordinator(h, F.FakeEntry(data=dict(F.CFG))); c2._fetch_tibber_prices = c._fetch_tibber_prices
    cap = Cap("ahead of the host clock"); logging.getLogger().addHandler(cap)
    st = dt_util.utcnow() + timedelta(minutes=60)
    h.states.set("sensor.indoor", F.FakeState("21.4", last_updated=st, last_reported=st))
    await F.cycle(c2)
    logging.getLogger().removeHandler(cap)
    print(f"RESULT future_stamp_after_reload.warnings={cap.n} count")

asyncio.run(main())
