import asyncio, sys; sys.path[:0]=["tests","custom_components"]
from datetime import datetime, timedelta
from homeassistant.util import dt as dt_util
from harness import FakeHass, FakeState, Results
R = Results("f11")
# -- R9-F1.1: the thermostat's target is the user's, even mid-solve -----------
# Round 9, fix F1.1 (#1683, D1-s3-04). ``apply_setback`` writes the away
# setback into the LIVE ``_opt_config.target_temp`` for the solve and unwinds
# it after the executor await; any state write inside that window -- the peak
# guard's event-driven transition is one -- published the setback as "the
# comfort target the user asked for". The solve is the production one; the
# wrapper only issues the listener write from the loop at the await.
from unittest import mock as _f11_mock  # noqa: E402

from harness import FakeEntry as _f11_Entry  # noqa: E402
from heatpump_optimizer import climate as _f11_climate  # noqa: E402
from heatpump_optimizer import coordinator as _f11_cm  # noqa: E402


async def _f11_midsolve(away: bool):
    t0 = datetime(2026, 10, 2, 8, 0)
    hass = FakeHass({"sensor.indoor": FakeState("21.4"),
                     "sensor.outdoor": FakeState("-3.0")})
    entry = _f11_Entry(data={"indoor_temp_entity": "sensor.indoor",
                             "outdoor_temp_entity": "sensor.outdoor",
                             "dhw_tank_volume": 180.0}, entry_id="f11midsolve")
    c = _f11_cm.HeatPumpOptimizerCoordinator(hass, entry)
    c._away_state.migrated_helpers = True
    c._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                  "starts_at": (t0 + timedelta(hours=h)).isoformat(),
                  "level": "NORMAL"} for h in range(48)]
    c._weather_forecast = [{"datetime": (t0 + timedelta(hours=h)).isoformat(),
                            "temperature": -5.0, "wind_speed": 3.0,
                            "precipitation": 0.0, "humidity": 85.0}
                           for h in range(48)]
    dt_util.freeze(t0)
    try:
        await c._update_current_state()
        if away:
            await c.async_set_away(
                active=True, return_time=(t0 + timedelta(days=3)).isoformat(),
                refresh=False)
        ent = _f11_climate.HeatPumpOptimizerClimate(c, entry)
        published: list = []
        c.async_add_listener(lambda: published.append(ent.target_temperature))
        seen: list = []
        solve = _f11_cm._await_optimize

        async def _wrapped(*a, **k):
            n0 = len(published)
            await c._async_peak_guard_transition()
            seen.extend(published[n0:])
            return await solve(*a, **k)

        with _f11_mock.patch.object(_f11_cm, "_await_optimize", _wrapped):
            dt_util.freeze(t0 + timedelta(minutes=15))
            await c.async_run_optimization()
        return seen, ent.target_temperature
    finally:
        dt_util.freeze(None)


_f11_away, _f11_after = asyncio.run(_f11_midsolve(True))
_f11_null, _f11_null_after = asyncio.run(_f11_midsolve(False))
R.check(
    "R9-F1.1 N-shared-config: mid-solve under an away setback the thermostat "
    "publishes the configured 21.0, not the 16.0 setback",
    _f11_away == [21.0] and _f11_after == 21.0,
    f"published mid-solve {_f11_away}, after {_f11_after}",
)
R.check(
    "R9-F1.1 N-shared-config (null arm): with away off the same write "
    "publishes 21.0 and the listener fired",
    _f11_null == [21.0] and _f11_null_after == 21.0,
    f"published mid-solve {_f11_null}, after {_f11_null_after}",
)


sys.exit(R.close("F11"))
