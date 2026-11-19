"""The previous tag's half of cells.py's ``upgrade`` state; never run alone.

cells.py extracts ``git archive v10.0.2`` into a temp root and runs this file
there (cwd = that root, PYTHONPATH=tests/hastub), feeding the rig on stdin.
It drives that release's coordinator through steps K-1 (idle) and K
(partial) and prints its stores and the devices' states as one JSON line.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, sys
from datetime import datetime, timedelta, timezone
sys.path[:0] = ["tests", "custom_components"]
from harness import FakeEntry, FakeHass, FakeServices, FakeState
from homeassistant.helpers import storage as _storage
from homeassistant.util import dt as dt_util
import heatpump_optimizer.coordinator as coord_mod
from heatpump_optimizer import boost
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, OptimizationResult

rig = json.loads(sys.stdin.read())
TS = [datetime.fromisoformat(t) for t in rig["ts"]]
K, N = rig["K"], len(TS)
calls = []


class Emu(FakeServices):
    def __init__(self, hass):
        super().__init__()
        self._hass = hass

    async def async_call(self, domain, service, data=None, **kw):
        data = dict(data or {})
        st = self._hass.states.get(data.get("entity_id"))
        value = data.get("value", data.get("option"))
        calls.append([domain, service, data.get("entity_id"), value])
        if st is not None:
            st.state = {"turn_on": "on", "turn_off": "off"}.get(service, str(value))
        return await super().async_call(domain, service, data, **kw)


dt_util.DEFAULT_TIME_ZONE = timezone.utc
hass = FakeHass({e: FakeState(s, attributes=a) for e, (s, a) in rig["states"].items()})
hass.services = Emu(hass)
entry = FakeEntry(data=rig["config"], entry_id=rig["entry_id"])
c = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
entry.runtime_data = c
sp, dh = [0.0] * N, [0.0] * N
sp[K], dh[K] = rig["book"]
res = OptimizationResult(
    power_schedule=sp, room_temp_trajectory=[20.5 + 0.1 * i for i in range(N)],
    slab_temp_trajectory=[21.0] * N, timestamps=TS, prices=[1.0] * N, predicted_cost=0.0,
    baseline_cost=0.0, predicted_savings=0.0, savings_percentage=0.0,
    optimal_setpoints=[20.0 + 0.25 * i for i in range(N)], status="ok", dhw_power_schedule=dh,
    duty_floor_kw=rig["F"], heat_pump_on_schedule=[(a > 0 or b > 0) for a, b in zip(sp, dh)],
    solve_band={"planned_min_kw": rig["F"], "planned_max_kw": rig["P"]})


async def go():
    for t in (TS[K - 1] + timedelta(minutes=2), TS[K] + timedelta(minutes=2)):
        dt_util.freeze(t)
        c._optimization_result, c._last_optimization = res, t
        boost.adopt_plan(c, HeatPumpOptimizer(c._thermal_model, OptimizationConfig()).get_current_action(res, t))
        boost.apply(c, boost.BoostOverlay(max_power=rig["P"], max_temp=float(c._opt_config.max_temp),
                                          ecl_max=float(c._ecl110_displace_max)))
        await c._apply_action()

asyncio.run(go())
print(json.dumps({"disk": dict(_storage._DISK), "versions": dict(_storage._VERSIONS), "calls": calls,
                  "states": {e: [s.state, s.attributes] for e, s in hass.states._states.items()}}))
