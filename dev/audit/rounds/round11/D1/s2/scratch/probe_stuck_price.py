import sys, asyncio
sys.path.insert(0, "dev/audit/rounds/round11/D1/s2")
import d1s2_lib as L
from datetime import timedelta
from unittest import mock

EID = "sensor.nordpool"


def rows(day0):
    return [{"start": (day0 + timedelta(hours=h)).isoformat(), "end": (day0 + timedelta(hours=h + 1)).isoformat(),
             "value": round(0.8 + 0.4 * (h % 12) / 12, 3)} for h in range(24)]


def pstate(day0, stamp, state="1.0"):
    return L.FakeState(state, attributes={"unit_of_measurement": "SEK/kWh", "raw_today": rows(day0),
                                          "raw_tomorrow": rows(day0 + timedelta(days=1))},
                       last_updated=stamp, last_reported=stamp)


async def main():
    day0 = L.T0.replace(hour=0)
    states = {**L.base_states(), EID: pstate(day0, L.T0)}
    hass = L.SchedHass(states)
    cfg = L.base_config({"price_source": "entity", "price_entity": EID})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    for tag, dt_h in (("healthy", 0), ("stuck+12h", 12), ("stuck+30h", 30), ("stuck+50h", 50), ("stuck+74h", 74)):
        now = L.T0 + timedelta(hours=dt_h)
        L.dtu.freeze(now)
        for k in ("sensor.indoor", "sensor.outdoor"):
            hass.states.set(k, L.FakeState(states[k].state, last_updated=now, last_reported=now))
        m = L.mark()
        try:
            d = await coord._async_update_data()
            print(tag, "ok current_price=", d.get("current_price"), "prices_available=", d.get("prices_available"),
                  "plan_stale=", d.get("plan_stale"), "price_known_steps=", d.get("price_known_steps"),
                  "status=", d.get("optimization_status"), "price_prior=", str(d.get("price_prior"))[:80])
        except Exception as e:
            print(tag, "raised", type(e).__name__, str(e)[:150])
        await L.drain(hass)
        for r in L.since(m):
            print("   LOG", L.template(r)[:160])
        print("   issues:", sorted(getattr(hass, "issues", {}) or [])[:5] if hasattr(hass, "issues") else "?")

L.reset_globals()
ps = L.patches() + [mock.patch.object(L.coord_mod, "async_get_clientsession", lambda h: object())]
for p in ps:
    p.start()
L.dtu.freeze(L.T0)
asyncio.run(main())
