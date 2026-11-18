"""Verifier D1#1, V2 for D1-s2-03: a non-advancing forecast, on my own grid and with a cover check.

Metric: over clock offsets past the last forecast row of {0.5, 2, 3, 72, 168} h (every row past),
the number of cycles of the real _async_update_data whose published weather_forecast_stale_hours
is None AND whose outdoor array step 0 is the last row's value (the plan runs on a held-flat
past value). Control arm: offsets of -40, -10 h (rows still cover now): stale None is right, so
these count only into null_cover_flagged (rows past and stale None) which must be 0.
The finder rig (weather_stuck.py's service stub and coordinator setup) is reused; grid and
count keys are mine.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_03_weather_grid.py
"""
import asyncio
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s2"))
import weather_stuck as W  # noqa: E402

L = W.L


async def cells():
    hass = L.SchedHass(L.base_states())
    hass.states.set(W.WX, L.FakeState("cloudy", attributes={"temperature": -3.0}, last_updated=L.T0, last_reported=L.T0))
    hass.services.async_register("weather", "get_forecasts", W.get_forecasts)
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({"weather_entity": W.WX})))
    await L.drain(hass)
    await coord._async_update_data()
    await L.drain(hass)
    last_row_temp = W.fc_rows(W.BASE)[-1]["temperature"]
    stuck = ctrl_flag = 0
    for h in (-40, -10, 0.5, 2, 3, 72, 168):
        now = W.LAST_ROW + timedelta(hours=h)
        L.dtu.freeze(now)
        for k, v in L.base_states().items():
            hass.states.set(k, L.FakeState(v.state, last_updated=now, last_reported=now))
        d = await coord._async_update_data()
        await L.drain(hass)
        rows = coord._weather_forecast or []
        all_past = bool(rows) and all(L.dtu.parse_datetime(r["datetime"]) + timedelta(hours=1) <= now for r in rows)
        sh = d.get("weather_forecast_stale_hours")
        o0 = float(coord._forecast_arrays()[1][0])
        print(f"offset {h:+}h all_past={all_past} stale_hours={sh} outdoor0={o0:.2f} last_row={last_row_temp:.2f}")
        if h > 0 and all_past and sh is None and abs(o0 - last_row_temp) < 0.05:
            stuck += 1
        if h < 0 and all_past and sh is None:
            ctrl_flag += 1
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return stuck, ctrl_flag


L.reset_globals()
ps = L.patches() + L.price_patches()
for p in ps:
    p.start()
L.dtu.freeze(L.T0)
try:
    s, c = asyncio.run(cells())
finally:
    L.dtu.freeze(None)
    for p in ps:
        p.stop()
print(f"RESULT stuck_fresh_heldflat={s} of 5")
print(f"RESULT null_cover_flagged={c} of 2")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
