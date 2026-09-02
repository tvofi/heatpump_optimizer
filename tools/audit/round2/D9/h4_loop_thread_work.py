"""D9 metric 4: event-loop-thread work per coordinator cycle.

Metric (binding, tools/audit/briefs/D9.md): ``time.thread_time()`` on the
event-loop thread across one ``_async_update_data`` cycle, with the solve
running in a real ``ThreadPoolExecutor`` (so its CPU lands on another thread
and is excluded by construction). Split per stage by wrapping the
coordinator's stage methods on the instance. Also the ratio of loop-thread
work to executor CPU for the same cycle, which is a CPU ratio and final.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h4_loop_thread_work.py

Expected (baseline c398fc8; CPU, provisional on the shared box):
    two_zone_dhw   loop_thread_ms per cycle of order 20-60 ms against an
                   executor solve of ~700-900 ms (ratio ~0.03-0.08);
                   _solve_snapshot's deepcopy and _build_data_dict the
                   largest loop-side stages
    perturbation   horizon_hours 24 -> 48: loop_thread_ms rises (arrays,
                   plan views and payload all scale with the horizon)
    perturbation   price_tiles_enabled: loop_thread_ms rises (a second
                   _forecast_arrays + what-if bookkeeping per cycle)

Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._async_update_data
and its stage methods (listed in STAGES), driven under a real loop with
``loop.run_in_executor``.
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import asyncio
import inspect
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
CONFIG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
}

STAGES = (
    "_update_current_state", "_async_learn_price_shape", "async_run_optimization",
    "_forecast_arrays", "_prepare_dhw_inputs", "_manual_pins", "_solve_snapshot",
    "_record_manual_release", "_file_lead_predictions", "_run_system_identification",
    "_maybe_run_fuse_advisor", "_maybe_refresh_price_tile", "_command_valve_target",
    "_apply_action", "_command_frequency", "_async_drive_pumps", "_record_accuracy",
    "_track_realised_peak", "_async_save_accuracy", "_async_save_energy_totals",
    "_async_watch_learning_drift", "_build_data_dict", "_build_plan_views",
)


class LoopHass(FakeHass):
    """FakeHass with a REAL executor boundary, as Home Assistant has."""

    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.executor_calls = 0

    async def async_add_executor_job(self, func, *args):
        self.executor_calls += 1
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.pool, func, *args)


T: dict = {}


def wrap(coord, name):
    orig = getattr(coord, name)
    if inspect.iscoroutinefunction(orig):
        async def aw(*a, **k):
            t0 = time.thread_time()
            try:
                return await orig(*a, **k)
            finally:
                T[name] = T.get(name, 0.0) + (time.thread_time() - t0)
        setattr(coord, name, aw)
    else:
        def sw(*a, **k):
            t0 = time.thread_time()
            try:
                return orig(*a, **k)
            finally:
                T[name] = T.get(name, 0.0) + (time.thread_time() - t0)
        setattr(coord, name, sw)


def make(extra: dict):
    hass = LoopHass({"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={**CONFIG, **extra}))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    for name in STAGES:
        if hasattr(coord, name):
            wrap(coord, name)
    return hass, coord


async def cycle(coord, when):
    dt_util.freeze(when)
    T.clear()
    proc0, thr0, wall0 = time.process_time(), time.thread_time(), time.perf_counter()
    coord.data = await coord._async_update_data()
    return (time.process_time() - proc0, time.thread_time() - thr0,
            time.perf_counter() - wall0)


def run(label: str, extra: dict, horizon: float | None = None, cycles: int = 3):
    hass, coord = make(extra)
    if horizon is not None:
        coord._opt_config.horizon_hours = horizon
    loop = asyncio.new_event_loop()
    try:
        for i in range(cycles):
            proc, thr, wall = loop.run_until_complete(
                cycle(coord, START + timedelta(hours=8, minutes=3 + 30 * i)))
            tag = f"{label}.cycle{i + 1}"
            d9lib.result(f"{tag}.loop_thread_cpu", thr * 1000.0, "ms_provisional")
            d9lib.result(f"{tag}.executor_cpu", (proc - thr) * 1000.0, "ms_provisional")
            d9lib.result(f"{tag}.wall", wall * 1000.0, "ms_provisional")
            d9lib.result(f"{tag}.loop_over_executor", thr / max(proc - thr, 1e-9), "ratio")
            d9lib.result(f"{tag}.executor_jobs", hass.executor_calls, "count")
            hass.executor_calls = 0
            if i == cycles - 1:
                # Stage split for the steady-state cycle. Nested stages are
                # reported as measured (async_run_optimization contains
                # _forecast_arrays etc.), so shares do not sum to one.
                for name, secs in sorted(T.items(), key=lambda kv: -kv[1]):
                    d9lib.result(f"{tag}.stage.{name}", secs * 1000.0, "ms_provisional")
                    d9lib.result(f"{tag}.stage_share.{name}", secs / max(thr, 1e-9), "ratio")
    finally:
        dt_util.freeze(None)
        loop.close()
        hass.pool.shutdown(wait=True)


run("two_zone_dhw", {})
run("perturb_h48_two_zone_dhw", {}, horizon=48.0)
run("perturb_price_tiles", {const.CONF_PRICE_TILES_ENABLED: True})
d9lib.closing(1.0)
