"""S1: does a cancelled space boost survive in _current_action through a
no_prices / solve_failed cycle, and reach actuation?

Sequence per arm (auto mode, real coordinator, real solve in-process):
  cycle 1: boost(space)=ON  -> successful solve -> boost.apply overlays
  cancel : boost.set_channel(space, False)       (what the switch calls)
  cycle 2: the arm's cycle outcome
Arms:
  probe/no_prices    : cycle 2 has no published prices   (async_run_optimization -> "no_prices")
  probe/solve_failed : cycle 2's solve raises            (-> "solve_failed")
  null/solve_ok      : cycle 2 solves normally           (action replaced)
  null/no_boost      : never boosted; cycle 2 no_prices  (the retained plan action alone)
Observed after cycle 2: what the switch was told, what ECL displace was
published, the action's boost keys, data['current_action'], and the
published boost_space_active flag.
"""
import asyncio

import rig
from heatpump_optimizer import boost as boost_mod


async def arm(name, *, boost, outcome, channel="space"):
    c = rig.make(f"s1_{name}", extra={"dhw_enabled": True} if channel == "dhw" else None)
    rig.GATE.fail = False
    sent = rig.spy_publish(c)
    ret = {}
    orig_run = c.async_run_optimization

    async def _run():
        r = await orig_run()
        ret["reason"] = r
        return r

    c.async_run_optimization = _run
    if boost:
        await boost_mod.set_channel(c, channel, True, refresh=False)
    await c._async_update_data()
    r1 = ret.get("reason")
    act1 = dict(c._current_action)
    if boost:
        await boost_mod.set_channel(c, channel, False, refresh=False)
    if outcome == "no_prices":
        c._prices = []
    elif outcome == "solve_failed":
        rig.GATE.fail = True
    n0 = len(c.hass.services.calls)
    data = await c._async_update_data()
    rig.GATE.fail = False
    acts = rig.actuations(c.hass, n0)
    sw = [s for d, s, _ in acts if d in ("switch", "homeassistant")]
    disp = [x.get("payload") for d, s, x in acts if d == "mqtt" and x.get("topic", "").endswith("/set")]
    a = c._current_action
    return {
        "arm": name,
        "cycle1": r1,
        "cycle2": ret.get("reason"),
        "c1_mode": act1.get("mode"),
        "c1_disp": act1.get("displace_value"),
        "c2_action_mode": a.get("mode"),
        "c2_power_kw": round(float(a.get("power") or 0.0), 2),
        "c2_boost_space_key": a.get("boost_space"),
        "c2_displace": a.get("displace_value"),
        "c2_boost_dhw_key": a.get("boost_dhw"),
        "c2_dhw_power_kw": a.get("dhw_power"),
        "c2_dhw_heating_active": a.get("dhw_heating_active"),
        "switch_cmd": sw,
        "ecl_displace_published": disp,
        "data.current_action.mode": (data.get("current_action") or {}).get("mode"),
        "switch.<channel>_boost is_on": boost_mod.held_for(c).active(channel, rig.dt_util.now()),
        "sensor recommended_power": __import__("heatpump_optimizer.sensor", fromlist=["x"]).commanded_power_kw(data.get("current_action")),
        "max_kw": c._thermal_model.params.max_electrical_power,
        "ecl_max": c._ecl110_displace_max,
    }


async def main():
    rows = []
    rows.append(await arm("probe/no_prices", boost=True, outcome="no_prices"))
    rows.append(await arm("probe/solve_failed", boost=True, outcome="solve_failed"))
    rows.append(await arm("null/solve_ok", boost=True, outcome="ok"))
    rows.append(await arm("null/no_boost", boost=False, outcome="no_prices"))
    rows.append(await arm("probe/dhw/no_prices", boost=True, outcome="no_prices", channel="dhw"))
    rows.append(await arm("null/dhw/solve_ok", boost=True, outcome="ok", channel="dhw"))
    keys = [k for k in rows[0] if k != "arm"]
    w = 21
    print("field".ljust(26) + "".join(r["arm"].ljust(w) for r in rows))
    for k in keys:
        print(k.ljust(26) + "".join(str(r[k]).ljust(w) for r in rows))



async def persistence():
    """How long: boost(space) on -> solve -> cancel -> Tibber outage (no prices),
    clock stepped 30 min per cycle (dt.freeze). Probe: boosted; null: never boosted."""
    from datetime import timedelta
    out = {}
    for name, boosted in (("probe/boost-cancelled", True), ("null/no-boost", False)):
        t0 = rig.dt_util.now().replace(second=0, microsecond=0)
        rig.dt_util.freeze(t0)
        c = rig.make(f"s1p_{name}")
        if boosted:
            await boost_mod.set_channel(c, "space", True, refresh=False)
        await c._async_update_data()
        if boosted:
            await boost_mod.set_channel(c, "space", False, refresh=False)
        c._prices = []
        row = []
        for k in range(1, 6):
            rig.dt_util.freeze(t0 + timedelta(minutes=30 * k))
            n0 = len(c.hass.services.calls)
            d = await c._async_update_data()
            acts = rig.actuations(c.hass, n0)
            sw = [s for dd, s, _ in acts if dd == "switch"]
            row.append(f"+{30*k}min:{(d.get('current_action') or {}).get('mode')}/{sw[0] if sw else 'no-write'}")
        out[name] = row
        rig.dt_util.freeze(None)
    print("\nPersistence under a price outage (published mode / switch write per cycle):")
    for k, v in out.items():
        print(f"  {k:24s} " + "  ".join(v))


async def _all():
    await main()
    await persistence()


asyncio.run(_all())
