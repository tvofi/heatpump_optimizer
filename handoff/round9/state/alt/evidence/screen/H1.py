"""H1: while async_run_optimization is parked on its solve await with the away
setback applied in place to _opt_config/_thermal_params, does a concurrent
_async_update_data cycle (which skips its own solve: "already in flight")
publish the SET-BACK comfort band as the configured one?

Sequence per arm:
  A = coord.async_run_optimization()  (the Optimize-now press / the action),
      its solve await held open on an asyncio.Event
  B = coord._async_update_data()      (the scheduled / requested refresh) runs
      to completion inside A's window -> data_B (what entities publish until
      the next refresh)
  release A; C = coord._async_update_data() after the window -> data_C
Arms: probe = away override active (no return time); null = away inactive.
Also an extra probe arm with economy mode (min_temp widening, same envelope).
"""
import asyncio

import rig

FIELDS = ("comfort_temp_day", "comfort_temp_night", "min_temperature", "dhw_min_temperature", "dhw_idle_min_temperature")


def pick(d):
    return {k: d.get(k) for k in FIELDS}


async def arm(name, *, away, mode="auto"):
    c = rig.make(f"h1_{name}")
    await c._async_update_data()  # a plan exists
    if mode != "auto":
        await c.async_set_mode(mode, refresh=False)
    c._away_state.override_active = bool(away)
    configured = {
        "comfort_temp_day": c._opt_config.comfort_temp_day,
        "comfort_temp_night": c._opt_config.comfort_temp_night,
        "min_temperature": c._opt_config.min_temp,
        "dhw_min_temperature": c._thermal_params.dhw_min_temp,
        "dhw_idle_min_temperature": c._thermal_params.dhw_idle_min_temp,
    }
    rig.GATE.arm()
    a = asyncio.get_running_loop().create_task(c.async_run_optimization())
    await asyncio.wait_for(rig.GATE.entered.wait(), 60)
    data_b = await c._async_update_data()
    rig.GATE.release.set()
    ra = await a
    rig.GATE.disarm()
    data_c = await c._async_update_data()
    return name, configured, pick(data_b), pick(data_c), ra, (data_c.get("away") or {}).get("away_active", data_c.get("away_active"))


async def main():
    rows = [
        await arm("probe/away", away=True),
        await arm("probe/economy", away=False, mode="economy"),
        await arm("null/no_away_auto", away=False),
    ]
    for name, conf, b, cc, ra, aa in rows:
        print(f"== {name}  (A returned {ra!r}; away_active published after: {aa})")
        print("  field".ljust(30) + "configured".ljust(14) + "data_B(inside)".ljust(18) + "data_C(after)")
        for k in FIELDS:
            print(f"  {k}".ljust(30) + str(conf[k]).ljust(14) + str(b[k]).ljust(18) + str(cc[k]))


asyncio.run(main())
