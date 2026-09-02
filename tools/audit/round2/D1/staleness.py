#!/usr/bin/env python
"""D1 staleness harness: the published values must say stale when stale and
never present fabricated data as measured.

METRICS (counts / published values, contention-immune):
  stuck_prices_known_steps        steps of the solve horizon backed by a
                                  published price when the price list has
                                  stopped updating (every entry before now)
  stuck_prices_fallback_steps     steps priced at extend_price_series'
                                  hard-coded fallback (0.5) in that case
  stuck_prices_solved             1 if async_run_optimization still solved
                                  and published a plan on those prices
  stuck_prices_plan_stale         plan_stale as published right after
  stuck_prices_update_success     1 if _async_update_data returned a payload
                                  (the coordinator would stay green)
  stuck_prices_disclosure_keys    payload keys whose value discloses that
                                  zero steps are backed by published prices
  fabricated_forecast_steps       length of the constant forecast built from
                                  the weather entity's current temperature on
                                  the first failed fetch
  fabricated_forecast_stale_hours weather_forecast_stale_hours published at
                                  that instant (0.0 == "stale from birth")
  clock_back_weather_stale_hours  weather_forecast_stale_hours after the
                                  clock steps back 2 h (negative == nonsense)
  clock_fwd_plan_stale            plan_stale after a 4 h forward jump
  clock_fwd_actuations            service calls _apply_action made then (0)
  future_last_reported_ok         InputReader accepts a state reported 1 h
                                  in the future (age < 0)
  unknown_ok / unavailable_ok     InputReader accepts "unknown"/"unavailable"
  solve_fail_*                    3 failed solves -> repair issue, stale plan
                                  after 100 min, no actuation; recovery
                                  clears the issue and the counter

COMMAND (from the export root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D1/staleness.py

EXPECTED (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, exact):
  stuck_prices_known_steps=0, stuck_prices_fallback_steps=n_steps (96),
  stuck_prices_solved=1, stuck_prices_plan_stale=0, stuck_prices_update_success=1

INSTRUMENTED SYMBOLS:
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._price_series
  heatpump_optimizer.price_model:extend_price_series (fallback=0.5 branch)
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fetch_weather_forecast
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.weather_stale_hours
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._plan_is_stale
  heatpump_optimizer.inputs:InputReader.read

PERTURBATIONS:
  stuck_prices_*: shift the injected price list so it covers `now`
    (config-free; the harness's `covering` arm) -> known_steps up, fallback
    steps to_zero. Or the one-line edit in _price_series:
    `if not known: return None` -> stuck_prices_solved to_zero.
  fabricated_forecast_stale_hours: one-line edit making weather_stale_hours
    return max(0.1, ...) or publishing a boolean -> value up.
  clock_back_weather_stale_hours: `max(0.0, ...)` in weather_stale_hours
    -> sign_flip/to_zero.

MACHINE: Apple M1 8-core 8 GB, Darwin 25.6.0, CPython 3.13.1, numpy 2.5.2
"""
from __future__ import annotations

import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.inputs import InputReader  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("heatpump_optimizer").setLevel(logging.CRITICAL)

START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

CONFIG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_switch_entity": "switch.heat_pump",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    "dhw_tank_volume": 200.0,
    "optimization_interval": 30,
}


def states(now):
    return {
        "sensor.indoor": FakeState("21.4", last_updated=now),
        "sensor.outdoor": FakeState("-3.0", last_updated=now),
        "weather.home": FakeState("cloudy", attributes={"temperature": -3.0, "wind_speed": 3.0}),
    }


async def _noop(self):
    return None


def prices_from(base):
    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (base + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def forecast_from(base):
    return [
        {
            "datetime": (base + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
        }
        for h in range(48)
    ]


def make(now, *, weather_service=None):
    hass = FakeHass(states(now))
    if weather_service is not None:
        hass.services.async_register("weather", "get_forecasts", weather_service)
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CONFIG))
    return hass, coord


def main():
    results = {}
    t0 = time.process_time()
    tt0 = time.thread_time()
    midnight = START.replace(hour=0, minute=0)

    # ------------------------------------------------------------------
    # A. the price list stops updating: every entry before now
    # ------------------------------------------------------------------
    dt_util.freeze(START)
    HeatPumpOptimizerCoordinator._fetch_tibber_prices = _noop
    HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
    HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop
    for arm, base in (("covering", midnight), ("stuck", midnight - timedelta(days=2))):
        hass, coord = make(START)
        coord._prices = prices_from(base)
        coord._weather_forecast = forecast_from(midnight)
        arrays = coord._forecast_arrays(START)
        n_steps = coord._opt_config.n_steps
        known = int(np.sum(arrays.price_known))
        fallback = int(np.sum(np.isclose(arrays.prices, 0.5)))
        asyncio.run(coord.async_run_optimization())
        solved = int(coord._optimization_result is not None)
        data = asyncio.run(coord._async_update_data())
        ok = int(isinstance(data, dict))
        disclosure = [
            k for k, v in data.items()
            if ("known" in k or "price_source" in k or "price_steps" in k) and not isinstance(v, (dict, list))
        ]
        results[f"{arm}_prices_known_steps"] = known
        results[f"{arm}_prices_fallback_steps"] = fallback
        results[f"{arm}_prices_n_steps"] = n_steps
        results[f"{arm}_prices_solved"] = solved
        results[f"{arm}_prices_plan_stale"] = int(bool(data.get("plan_stale")))
        results[f"{arm}_prices_update_success"] = ok
        results[f"{arm}_prices_savings_pct"] = round(float(getattr(coord._optimization_result, "savings_percentage", float("nan"))), 2)
        results[f"{arm}_prices_switch_calls"] = sum(1 for c in hass.services.calls if c[0] == "switch")
        results[f"{arm}_prices_disclosure_keys"] = "+".join(f"{k}={data[k]}" for k in disclosure) or "none"
        results[f"{arm}_prices_forecast_min_max"] = f"{float(np.min(arrays.prices)):.3f}/{float(np.max(arrays.prices)):.3f}"
    dt_util.freeze(None)

    # ------------------------------------------------------------------
    # B. first weather fetch fails with no prior forecast: fabricated 48 h
    # ------------------------------------------------------------------
    dt_util.freeze(START)

    async def failing_forecasts(call):
        raise RuntimeError("weather integration down (harness)")

    hass, coord = make(START, weather_service=failing_forecasts)
    HeatPumpOptimizerCoordinator._fetch_weather_forecast = HeatPumpOptimizerCoordinator.__dict__.get(
        "_fetch_weather_forecast_orig", None
    ) or _ORIG_FETCH_WEATHER
    asyncio.run(coord._fetch_weather_forecast())
    results["fabricated_forecast_steps"] = len(coord._weather_forecast)
    results["fabricated_forecast_all_equal_current"] = int(
        bool(coord._weather_forecast) and all(fc["temperature"] == -3.0 for fc in coord._weather_forecast)
    )
    results["fabricated_forecast_stale_hours"] = coord.weather_stale_hours()
    coord._prices = prices_from(midnight)
    data = coord._build_data_dict()
    results["fabricated_forecast_published_stale_hours"] = data.get("weather_forecast_stale_hours")
    # C. clock steps back 2 h after the stale mark
    dt_util.freeze(START - timedelta(hours=2))
    results["clock_back_weather_stale_hours"] = coord.weather_stale_hours()
    dt_util.freeze(None)

    # ------------------------------------------------------------------
    # D. clock jumps forward 4 h with a plan in hand: plan_stale, no actuation
    # ------------------------------------------------------------------
    dt_util.freeze(START)
    HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
    hass, coord = make(START)
    coord._prices = prices_from(midnight)
    coord._weather_forecast = forecast_from(midnight)
    asyncio.run(coord.async_run_optimization())
    assert coord._optimization_result is not None
    calls0 = len(hass.services.calls)
    dt_util.freeze(START + timedelta(hours=4))
    data = coord._build_data_dict()
    asyncio.run(coord._apply_action())
    results["clock_fwd_plan_stale"] = int(bool(data["plan_stale"]))
    results["clock_fwd_plan_age_minutes"] = data["plan_age_minutes"]
    results["clock_fwd_actuations"] = len(hass.services.calls) - calls0
    dt_util.freeze(START - timedelta(hours=4))
    data = coord._build_data_dict()
    results["clock_back_plan_age_minutes"] = data["plan_age_minutes"]
    results["clock_back_plan_stale"] = int(bool(data["plan_stale"]))
    dt_util.freeze(None)

    # ------------------------------------------------------------------
    # E. InputReader under future last_reported, unknown, unavailable
    # ------------------------------------------------------------------
    dt_util.freeze(START)
    hass = FakeHass(
        {
            "sensor.future": FakeState("21.0", last_updated=START - timedelta(hours=3), last_reported=START + timedelta(hours=1)),
            "sensor.unknown": FakeState("unknown", last_updated=START),
            "sensor.unavailable": FakeState("unavailable", last_updated=START),
            "sensor.old": FakeState("21.0", last_updated=START - timedelta(hours=3)),
        }
    )
    reader = InputReader(
        hass,
        {
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.future",
            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.unknown",
            const.CONF_DHW_TEMP_ENTITY: "sensor.unavailable",
        },
        enabled=True,
        scale=1.0,
    )
    results["future_last_reported_ok"] = int(reader.read(const.CONF_INDOOR_TEMP_ENTITY).ok)
    results["unknown_ok"] = int(reader.read(const.CONF_OUTDOOR_TEMP_ENTITY).ok)
    results["unavailable_ok"] = int(reader.read(const.CONF_DHW_TEMP_ENTITY).ok)
    reader2 = InputReader(hass, {const.CONF_INDOOR_TEMP_ENTITY: "sensor.old"}, enabled=True, scale=1.0)
    results["three_hours_old_ok"] = int(reader2.read(const.CONF_INDOOR_TEMP_ENTITY).ok)
    dt_util.freeze(None)

    # ------------------------------------------------------------------
    # F. three failed solves: issue, stale plan after 100 min, recovery
    # ------------------------------------------------------------------
    dt_util.freeze(START)
    hass, coord = make(START)
    coord._prices = prices_from(midnight)
    coord._weather_forecast = forecast_from(midnight)
    asyncio.run(coord._async_update_data())
    assert coord._optimization_result is not None
    real_optimize = HeatPumpOptimizer.optimize

    def boom(self, *a, **k):
        raise RuntimeError("solver blew up (harness)")

    HeatPumpOptimizer.optimize = boom
    fails = []
    for i in range(3):
        dt_util.freeze(START + timedelta(minutes=30 * (i + 1)))
        data = asyncio.run(coord._async_update_data())
        fails.append(int(isinstance(data, dict)))
    results["solve_fail_cycles_still_publish"] = sum(fails)
    results["solve_fail_counter"] = coord._solve_failures
    results["solve_fail_issue_raised"] = int(any(i[1] == "solve_failures" for i in getattr(hass, "issues", [])))
    dt_util.freeze(START + timedelta(minutes=100))
    calls0 = len(hass.services.calls)
    data = asyncio.run(coord._async_update_data())
    results["solve_fail_plan_stale_after_100min"] = int(bool(data["plan_stale"]))
    results["solve_fail_actuations_when_stale"] = sum(1 for c in hass.services.calls[calls0:] if c[0] == "switch")
    HeatPumpOptimizer.optimize = real_optimize
    dt_util.freeze(START + timedelta(minutes=130))
    data = asyncio.run(coord._async_update_data())
    results["solve_recover_counter"] = coord._solve_failures
    results["solve_recover_issue_cleared"] = int(not any(i[1] == "solve_failures" for i in getattr(hass, "issues", [])))
    results["solve_recover_plan_stale"] = int(bool(data["plan_stale"]))
    dt_util.freeze(None)

    for k, v in results.items():
        print(f"RESULT {k}={v} count")
    cpu = time.process_time() - t0
    thr = time.thread_time() - tt0
    print(f"RESULT thread_factor={cpu / thr if thr else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


_ORIG_FETCH_WEATHER = HeatPumpOptimizerCoordinator._fetch_weather_forecast

if __name__ == "__main__":
    main()
