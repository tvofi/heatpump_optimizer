"""H4: the DHW learner's external_heat_active callable (coordinator ~2158)
reads ctx._current_state.external_heat_active, which only
async_run_optimization refreshes (~5042). In comfort/boost/off no solve runs.

Real coordinator, DHW on, real _async_update_data cycles.  The LIVE flag
(self._external_heat_active, normally set by _update_external_heat_detection)
is scripted by replacing that one detection method on the instance -- the
signal source, not the reader under test. Between cycles the learner's
last_sample_time is backdated 30 min (= one optimization interval of wall
time), so async_learn_dynamics passes its dt gate and reaches the draw-stat
fold, whose first statement consults the callable.

Script, both arms: cycle 0 in AUTO with a burn (live=True) -> the solve copies
True. Then the arm's mode is selected and the burn ends (live=False) for 6
cycles.  probe = comfort mode; null = auto mode.
Per cycle: live flag, _learning_frozen() (reads the live flag), the value the
learner's callable returns inside async_fold_draw_stats, and whether the
fold got past it (draw-stat reservoir touched).
"""
import asyncio
from datetime import timedelta

import rig
from heatpump_optimizer import dhw_learning


async def arm(name, mode, n=6):
    c = rig.make(f"h4_{name}", extra={"dhw_enabled": True, "dhw_temp_entity": "sensor.dhw"})
    live = {"v": True}

    def _scripted_detection():
        c._external_heat_active = live["v"]

    c._update_external_heat_detection = _scripted_detection
    L = c._dhw_learner
    seen = []
    real_fold = L.async_fold_draw_stats

    async def _fold(now, prev, drop, dt_h):
        cb = bool(L._external_heat_active())
        before = repr(L.draw_stats.as_dict())
        await real_fold(now, prev, drop, dt_h)
        seen.append((cb, repr(L.draw_stats.as_dict()) != before))

    L.async_fold_draw_stats = _fold
    temps = iter([55.0, 54.0, 52.0, 50.5, 49.0, 47.0, 45.5, 44.0, 42.0])
    rows = []

    async def cycle(label):
        c.hass.states.set("sensor.dhw", rig.FakeState(str(next(temps)), unit="°C"))
        if L.last_sample_time is not None:
            L.last_sample_time = L.last_sample_time - timedelta(minutes=30)
        seen.clear()
        await c._async_update_data()
        cb, folded = seen[0] if seen else (None, None)
        rows.append((label, c._mode, live["v"], c._learning_frozen(), c._current_state.external_heat_active, cb, folded))

    await cycle("c0 burn, auto")
    await cycle("c1 burn, auto")
    if mode != "auto":
        await c.async_set_mode(mode, refresh=False)
    live["v"] = False
    for i in range(n):
        await cycle(f"c{i + 2} burn over")
    return name, rows


async def main():
    for name, mode in (("probe/comfort", "comfort"), ("null/auto", "auto")):
        name, rows = await arm(name, mode)
        print(f"== {name}")
        print("  cycle".ljust(20) + "mode".ljust(10) + "live".ljust(7) + "frozen(live)".ljust(24) + "state.copy".ljust(12) + "callable_in_fold".ljust(18) + "draw_stats_folded")
        for r in rows:
            print(f"  {r[0]:18s}{r[1]:10s}{str(r[2]):7s}{str(r[3]):24s}{str(r[4]):12s}{str(r[5]):18s}{r[6]}")


asyncio.run(main())
