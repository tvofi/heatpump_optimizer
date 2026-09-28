"""C3: _forecast_arrays is called by the live solve AND by async_simulate
(user what-if, fuse advisor, price tile). It writes live coordinator state as
a side effect: _price_known_steps (published data['price_known_steps']),
_pv_summary/_pv_production (published data['pv']), and the persisted #30
roof-snow memory (_snow_accum_cm/_snow_accum_last/_last_heavy_snow).

Real coordinator, frozen clock (tests/hastub dt.freeze). Published prices
end ~10 h ahead, so the known-price count shrinks as the clock moves. PV on
with a production entity. Snow-roof factor on, Open-Meteo replaced by a
fixed-rate snowfall source (1.0 cm/h), the only input it needs here.
  T0      : auto cycle (real solve) -> data1
  T0+20min: PV meter moves 1.2 -> 3.4 kW
            probe: one user what-if (async_simulate)       null: none
  then    : (i) a cycle in comfort mode (no solve)   -> data2 published
            (ii) separately, an auto cycle (solve)   -> data2' published
Compare published data2 to the plan it annotates (the T0 solve), and the
live/persisted state after the what-if.
"""
import asyncio
from datetime import timedelta

import rig
from homeassistant.util import dt as dt_util


class FakeOpenMeteo:
    available = True
    forecast = []

    def irradiance_for(self, start, step):
        return None

    def humidity_for(self, start, step):
        return None

    def snowfall_for(self, start, step):
        return 1.0

    def current_irradiance(self, *_a):
        return None

    def matches(self, *_a, **_k):
        return True

    async def async_refresh(self, *_a):
        return None

    def diagnostics(self):
        return {}


def snap(c, data=None):
    live = {
        "live._price_known_steps": c._price_known_steps,
        "live._pv_production": c._pv_production,
        "live._pv_summary.measured_kw": (c._pv_summary or {}).get("measured_production_kw"),
        "live.snow_accum_cm": round(c._snow_accum_cm, 4),
        "live.snow_accum_last": c._snow_accum_last.strftime("%H:%M") if c._snow_accum_last else None,
    }
    if data is not None:
        live.update({
            "pub.price_known_steps": data.get("price_known_steps"),
            "pub.pv.measured_kw": (data.get("pv") or {}).get("measured_production_kw"),
        })
    return live


async def arm(name, *, whatif, then):
    t0 = dt_util.now().replace(second=0, microsecond=0)
    t0 = t0.replace(minute=(t0.minute // 15) * 15) + timedelta(minutes=2)
    dt_util.freeze(t0)
    c = rig.make(f"c3_{name}", extra={
        "pv_enabled": True, "pv_peak_kw": 6.0, "pv_production_entity": "sensor.pv",
        "snow_roof_factor_enabled": True,
    })
    c.hass.states.set("sensor.pv", rig.FakeState("1.2", unit="kW"))
    base = t0.replace(minute=0) - timedelta(hours=1)
    c._prices = rig.prices(n=11, t0=base)  # published through ~t0+10h
    c._open_meteo = FakeOpenMeteo()
    d1 = await c._async_update_data()
    plan_known = c._price_known_steps
    r = {"arm": name, "plan(T0).price_known_steps": plan_known, **{f"T0 {k}": v for k, v in snap(c, d1).items() if k.startswith("pub")}}
    dt_util.freeze(t0 + timedelta(minutes=20))
    c.hass.states.set("sensor.pv", rig.FakeState("3.4", unit="kW"))
    if whatif:
        c._last_simulation = None
        ans = await c.async_simulate({"target_temp": 20.0})
        r["whatif.error"] = ans.get("error")
    r.update({f"after-whatif {k}": v for k, v in snap(c).items()})
    if then == "comfort":
        await c.async_set_mode("comfort", refresh=False)
    d2 = await c._async_update_data()
    r.update({f"next-cycle({then}) {k}": v for k, v in snap(c, d2).items() if k.startswith("pub") or "snow" in k})
    r["plan still T0's"] = c._last_optimization is not None and c._last_optimization <= t0 + timedelta(minutes=1)
    dt_util.freeze(None)
    return r


async def main():
    rows = [
        await arm("probe/whatif->comfort", whatif=True, then="comfort"),
        await arm("null/none->comfort", whatif=False, then="comfort"),
        await arm("probe/whatif->auto", whatif=True, then="auto"),
        await arm("null/none->auto", whatif=False, then="auto"),
    ]
    keys = []
    for r in rows:
        for k in r:
            if k != "arm" and k not in keys:
                keys.append(k)
    w = 24
    print("field".ljust(46) + "".join(r["arm"].ljust(w) for r in rows))
    for k in keys:
        print(k.ljust(46) + "".join(str(r.get(k, "-")).ljust(w) for r in rows))


asyncio.run(main())
