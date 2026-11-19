"""D1-s2 round 11, D1.M3: the price and weather feeds -- stuck, empty, failing.

Metric (one line): per phase of each feed on a real asyncio loop and the real
cycle (``_async_update_data`` with the real ``_fetch_tibber_prices`` /
``pull_prices`` entity path and the real weather fetch through a registered
``weather.get_forecasts`` service), the published freshness signal against
the truth: for weather, ``weather_forecast_stale_hours`` against the age of
the forecast's first row the plan stands on; for prices, ``current_price`` /
``plan_stale`` once the entity's rows stop covering now.
Counted defects:
  weather_stale_hidden   a phase whose forecast rows all lie in the past (the
                         provider stopped updating), published stale_hours == 0/None
  weather_empty_hidden   an empty forecast published with stale_hours None
  price_stuck_hidden     entity rows no longer cover now, yet current_price is
                         published or plan_stale is False
Count key: the published payload, never the planted service reply.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/price_weather.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

WX = "weather.home"
NP = "sensor.nordpool"
REPLY = {"mode": "ok", "base": None}


def fc_rows(start):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(), "temperature": -4.0 + 0.1 * h,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80} for h in range(48)]


async def get_forecasts(call):
    mode = REPLY["mode"]
    if mode == "raise":
        raise RuntimeError("weather integration down")
    if mode == "empty":
        return {WX: {"forecast": []}}
    start = REPLY["base"] if mode == "stuck" else L.dtu.now().replace(minute=0, second=0, microsecond=0)
    return {WX: {"forecast": fc_rows(start)}}


def np_rows(day0):
    return [{"start": (day0 + timedelta(hours=h)).isoformat(), "end": (day0 + timedelta(hours=h + 1)).isoformat(),
             "value": round(0.8 + 0.4 * (h % 12) / 12, 3)} for h in range(24)]


def np_state(day0, stamp, state="1.0"):
    return L.FakeState(state, attributes={"unit_of_measurement": "SEK/kWh", "raw_today": np_rows(day0),
                                          "raw_tomorrow": np_rows(day0 + timedelta(days=1))},
                       last_updated=stamp, last_reported=stamp)


def refresh_core(hass, now):
    for k, v in L.base_states().items():
        hass.states.set(k, L.FakeState(v.state, last_updated=now, last_reported=now))


async def weather_arm(out):
    hass = L.SchedHass(L.base_states())
    hass.states.set(WX, L.FakeState("cloudy", attributes={"temperature": -3.0}, last_updated=L.T0, last_reported=L.T0))
    hass.services.async_register("weather", "get_forecasts", get_forecasts)
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({"weather_entity": WX})))
    await L.drain(hass)
    plan = [("healthy", 0, "ok"), ("empty", 1, "empty"), ("healthy2", 2, "ok"), ("raise", 3, "raise"),
            ("healthy3", 4, "ok"), ("stuck+6h", 10, "stuck"), ("stuck+30h", 34, "stuck"), ("stuck+60h", 64, "stuck")]
    REPLY["base"] = (L.T0 + timedelta(hours=4)).replace(minute=0)
    hidden = empty_hidden = 0
    for tag, h, mode in plan:
        now = L.T0 + timedelta(hours=h)
        L.dtu.freeze(now)
        refresh_core(hass, now)
        REPLY["mode"] = mode
        try:
            d = await coord._async_update_data()
        except Exception as e:  # noqa: BLE001
            d = {"_err": repr(e)[:100]}
        await L.drain(hass)
        first = (coord._weather_forecast or [{}])[0].get("datetime")
        last = (coord._weather_forecast or [{}])[-1].get("datetime")
        sh = d.get("weather_forecast_stale_hours")
        print(f"WX {tag}: stale_hours={sh} first_row={first} last_row={last} "
              f"outdoor_forecast={str(d.get('outdoor_forecast_temperature'))[:40]} err={d.get('_err')}")
        if mode == "stuck" and last is not None and L.dtu.parse_datetime(last) < now and not sh:
            hidden += 1
        if mode == "empty" and sh is None:
            empty_hidden += 1
    out["weather_stale_hidden"] = hidden
    out["weather_empty_hidden"] = empty_hidden
    await coord.async_shutdown()
    await L.drain(hass, 5)


async def price_arm(out):
    day0 = L.T0.replace(hour=0)
    hass = L.SchedHass(L.base_states())
    hass.states.set(NP, np_state(day0, L.T0))
    cfg = L.base_config({"price_source": "entity", "price_entity": NP})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    hidden = 0
    for tag, h, unavailable in (("healthy", 0, False), ("unavailable_covered", 2, True), ("stuck+12h", 12, False),
                                ("stuck+50h", 50, False), ("stuck+74h", 74, False)):
        now = L.T0 + timedelta(hours=h)
        L.dtu.freeze(now)
        refresh_core(hass, now)
        if unavailable:
            hass.states.set(NP, L.FakeState("unavailable", attributes={}, last_updated=now, last_reported=now))
        else:
            hass.states.set(NP, np_state(day0, L.T0))
        try:
            d = await coord._async_update_data()
        except Exception as e:  # noqa: BLE001
            d = {"_err": repr(e)[:100]}
        await L.drain(hass)
        covered = bool(coord._known_prices_for([L.coord_mod.plan_step_start(now)]))
        print(f"PRICE {tag}: covered={covered} current_price={d.get('current_price')} plan_stale={d.get('plan_stale')} "
              f"err={d.get('_err')}")
        if not covered and (d.get("current_price") is not None or d.get("plan_stale") is False):
            hidden += 1
    out["price_stuck_hidden"] = hidden
    await coord.async_shutdown()
    await L.drain(hass, 5)


def main():
    proc0, thr0 = time.process_time(), time.thread_time()
    out = {}
    for arm in (weather_arm, price_arm):
        L.reset_globals()
        ps = L.patches() + [mock.patch.object(L.coord_mod, "async_get_clientsession", lambda h: object())]
        if arm is weather_arm:
            ps += L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(L.T0)
        try:
            asyncio.run(arm(out))
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
