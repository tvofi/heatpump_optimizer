"""Verifier D1#1, V2 for D1-s2-02: PV production read vs the slot's declared age, at the reader alone.

Metric: over report ages {0, 29, 31, 60, 240, 1440, 10080} min and a stamp 90 min in the
future (6 stale cells, 2 fresh), the number of ages where HeatPumpOptimizerCoordinator._pv_measured_production returns a
value while InputReader built with the entry's own staleness settings (as the coordinator's other
readers build it) withholds the same state; null control = ages <= limit (must agree).
Also prints _pv_forecast's step-0 production for the stale arm vs the model (the planning effect).
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_02_pv_direct.py
"""
import asyncio
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s2"))
import d1s2_lib as L  # noqa: E402
from heatpump_optimizer import inputs  # noqa: E402
import numpy as np  # noqa: E402

C = L.const
EID = "sensor.pv_w"
LIMIT = C.INPUT_MAX_AGE_MINUTES[C.CONF_PV_PRODUCTION_ENTITY]


async def main():
    t = L.T0 + timedelta(hours=10)  # 22:00 UTC: night, the model says ~0
    L.dtu.freeze(t)
    hass = L.SchedHass(L.base_states())
    cfg = L.base_config({"pv_enabled": True, "pv_peak_kw": 8.0, C.CONF_PV_PRODUCTION_ENTITY: EID})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    ec = getattr(coord, "_ctx", coord)._config
    disagree = agree_fresh = 0
    for age in (0, 29, 31, 60, 240, 1440, 10080, -90):
        stamp = t - timedelta(minutes=age)
        hass.states._states[EID] = L.FakeState("4000", attributes={"unit_of_measurement": "W", "device_class": "power"},
                                               last_updated=stamp, last_reported=stamp)
        prod = coord._pv_measured_production(coord._pv_config())
        r = inputs.InputReader(hass, ec, enabled=ec.staleness_watchdog_enabled,
                               scale=ec.staleness_max_age_scale).read(C.CONF_PV_PRODUCTION_ENTITY, entity_id=EID)
        rv = r.value if r.ok else None
        stale = age > LIMIT or age < 0
        print(f"age={age} production={prod} reader_ok={r.ok} reader_value={rv}")
        if stale and prod is not None and not r.ok:
            disagree += 1
        if not stale and (prod is not None) == r.ok:
            agree_fresh += 1
    surplus, summ = coord._pv_forecast(np.zeros(8), 8)
    print(f"night stale arm: step0 surplus={surplus[0]:.2f} kW, measured={summ.get('measured_production_kw')}")
    print(f"RESULT stale_ages_used_while_reader_withholds={disagree} of 6")
    print(f"RESULT null_fresh_ages_agree={agree_fresh} of 2")
    print(f"RESULT night_step0_surplus_kw={surplus[0]:.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    await coord.async_shutdown()
    await L.drain(hass, 5)


L.reset_globals()
ps = L.patches() + L.price_patches()
for p in ps:
    p.start()
try:
    asyncio.run(main())
finally:
    L.dtu.freeze(None)
    for p in ps:
        p.stop()
