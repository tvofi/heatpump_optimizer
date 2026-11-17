"""D1-s2 round 11, D1.M3: a weather forecast that stopped advancing is published as fresh.

Metric (one line): of 5 cells where the weather provider keeps answering
``weather.get_forecasts`` with the same 48 rows and the clock has passed the
LAST row by 1, 6, 12, 24 and 48 h (every row in the past), how many cycles of
the real ``_async_update_data`` publish ``weather_forecast_stale_hours`` as
None (fresh) -- i.e. ``_fetch_weather`` reads the stale reply as a recovery.
Count key: the published ``weather_forecast_stale_hours`` (and the coordinator's
own ``_weather_stale_since``), never the planted reply.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/weather_stuck.py [--fix] [--advancing]
Expected at baseline: RESULT stuck_published_fresh=5 (of 5). --advancing (null
control: the provider's rows start at the current hour, as a live one's do)
-> 0 cells with every row in the past, stale_hours None correctly. --fix
(perturbation, in memory: ``coordinator._plausible_forecast_rows`` also drops a
row whose hour (``datetime`` + 1 h) has ended, so an all-past reply is an
empty one) -> 0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

WX = "weather.home"
BASE = L.T0.replace(minute=0)
LAST_ROW = BASE + timedelta(hours=47)
CELLS_H = [1, 6, 12, 24, 48]  # hours past the last row
MODE = {"advancing": False}


def fc_rows(start):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(), "temperature": -4.0 + 0.1 * h,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80} for h in range(48)]


async def get_forecasts(call):
    start = L.dtu.now().replace(minute=0, second=0, microsecond=0) if MODE["advancing"] else BASE
    return {WX: {"forecast": fc_rows(start)}}


def fixed_rows(real):
    def rows(forecast):
        out = real(forecast)
        now = L.dtu.now()
        keep = []
        for r in out:
            when = L.dtu.parse_datetime(str(r.get("datetime") or ""))
            if when is None or when + timedelta(hours=1) > now:  # the row's hour has not ended
                keep.append(r)
        return keep
    return rows


async def run_cells():
    hass = L.SchedHass(L.base_states())
    hass.states.set(WX, L.FakeState("cloudy", attributes={"temperature": -3.0}, last_updated=L.T0, last_reported=L.T0))
    hass.services.async_register("weather", "get_forecasts", get_forecasts)
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({"weather_entity": WX})))
    await L.drain(hass)
    d = await coord._async_update_data()  # healthy first fetch at T0
    await L.drain(hass)
    print(f"CELL first_fetch stale_hours={d.get('weather_forecast_stale_hours')}")
    hidden = past = 0
    for h in CELLS_H:
        now = LAST_ROW + timedelta(hours=h)
        L.dtu.freeze(now)
        for k, v in L.base_states().items():
            hass.states.set(k, L.FakeState(v.state, last_updated=now, last_reported=now))
        d = await coord._async_update_data()
        await L.drain(hass)
        last = coord._weather_forecast[-1].get("datetime") if coord._weather_forecast else None
        all_past = last is not None and L.dtu.parse_datetime(last) < now
        sh = d.get("weather_forecast_stale_hours")
        outdoor = coord._forecast_arrays()[1][:3]
        print(f"CELL +{h}h past last row: all_rows_past={all_past} stale_hours={sh} "
              f"outdoor_array[:3]={[round(float(x), 2) for x in outdoor]}")
        past += all_past
        hidden += all_past and sh is None
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return past, hidden


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--advancing", action="store_true")
    a = ap.parse_args()
    MODE["advancing"] = a.advancing
    proc0, thr0 = time.process_time(), time.thread_time()
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    if a.fix:
        ps.append(mock.patch.object(L.coord_mod, "_plausible_forecast_rows", fixed_rows(L.coord_mod._plausible_forecast_rows)))
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    try:
        past, hidden = asyncio.run(run_cells())
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()
    print(f"RESULT cells={len(CELLS_H)} count")
    print(f"RESULT cells_all_rows_past={past} count")
    print(f"RESULT stuck_published_fresh={hidden} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
