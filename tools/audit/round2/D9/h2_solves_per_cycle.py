"""D9 metric 2: full solves per coordinator cycle, split by path.

Metric (binding, tools/audit/briefs/D9.md): entries into
``optimizer._multi_start_minimize`` during one ``_async_update_data`` cycle,
attributed by the call stack to main solve / shadow-what-if (price tile,
fuse advisor, card) / diagnose / other; plus ``HeatPumpOptimizer.optimize``
calls and simulate-step-equivalents per cycle.

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/h2_solves_per_cycle.py

Expected (baseline c398fc8, exact -- counts):
    two_zone_dhw      cycle 2: optimize_calls = 1, multi_start.main = 2
                      (solve_space, then _co_optimize's re-solve), other = 0
    minimal_nodhw     cycle 2: optimize_calls = 1, multi_start.main = 1
    perturbation price_tiles_enabled=True: optimize_calls per cycle -> 2
                      (one tile what-if solve per scheduled solve), and
                      multi_start.what_if_tile >= 1
    perturbation main_fuse_a=20 (fuse advisor): +1 optimize on the first
                      cycle only (weekly rate limit), 0 on the second

The coordinator runs on tests/harness.py:FakeHass (inline executor -- fine
for COUNTS; the GIL and loop-work metrics use a real loop elsewhere). The
three network fetches are replaced by no-ops after the price, weather and
irradiance lists are filled the way tests/golden.py:_capture_coordinator
fills them; the clock is frozen with dt_util.freeze.

Instrumented symbols: optimizer:_multi_start_minimize,
optimizer:HeatPumpOptimizer.optimize, thermal_model:ThermalModel.simulate_step,
thermal_model:ThermalModel.simulate_trajectory_batch.
Machine: Apple M1 8-core 8 GB (audit box, shared during the fan-out).
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
import traceback
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)

BASE = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
}
DHW = {
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
}
TWO_ZONE = {
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08,
    "lower_floor_heat_loss": 0.07,
}

C: dict = {}


def reset():
    C.update(main=0, what_if_tile=0, what_if_fuse=0, what_if_card=0,
             diagnose=0, other=0, optimize=0, steps=0, rows=0)


reset()
_orig_msm = opt_mod._multi_start_minimize
_orig_opt = opt_mod.HeatPumpOptimizer.optimize
_orig_step = tm_mod.ThermalModel.simulate_step
_orig_batch = tm_mod.ThermalModel.simulate_trajectory_batch


def _path() -> str:
    names = {f.name for f in traceback.extract_stack()}
    if "diagnose_last_interval" in names:
        return "diagnose"
    if "async_simulate" in names:
        if "_maybe_refresh_price_tile" in names:
            return "what_if_tile"
        if "_maybe_run_fuse_advisor" in names:
            return "what_if_fuse"
        return "what_if_card"
    if "async_run_optimization" in names:
        return "main"
    return "other"


def hooked_msm(*a, **k):
    C[_path()] += 1
    return _orig_msm(*a, **k)


def hooked_opt(self, *a, **k):
    C["optimize"] += 1
    return _orig_opt(self, *a, **k)


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


def hooked_batch(self, initial_state, power_matrix, *a, **k):
    C["rows"] += int(np.asarray(power_matrix).shape[0])
    return _orig_batch(self, initial_state, power_matrix, *a, **k)


opt_mod._multi_start_minimize = hooked_msm
opt_mod.HeatPumpOptimizer.optimize = hooked_opt
tm_mod.ThermalModel.simulate_step = hooked_step
tm_mod.ThermalModel.simulate_trajectory_batch = hooked_batch


def make_coordinator(extra: dict):
    hass = FakeHass({
        "sensor.indoor": FakeState("21.4"),
        "sensor.outdoor": FakeState("-3.0"),
    })
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={**BASE, **extra}))
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
    return hass, coord


def run_cycles(label: str, extra: dict, cycles: int = 2):
    hass, coord = make_coordinator(extra)
    tfs = []
    for i in range(cycles):
        dt_util.freeze(START + timedelta(hours=8, minutes=3 + 30 * i))
        reset()
        with d9lib.Clocks() as c:
            coord.data = asyncio.run(coord._async_update_data())
        tfs.append(c.thread_factor)
        tag = f"{label}.cycle{i + 1}"
        d9lib.result(f"{tag}.optimize_calls", C["optimize"], "count")
        for path in ("main", "what_if_tile", "what_if_fuse", "what_if_card", "diagnose", "other"):
            d9lib.result(f"{tag}.multi_start.{path}", C[path], "count")
        d9lib.result(f"{tag}.multi_start.total", sum(C[p] for p in (
            "main", "what_if_tile", "what_if_fuse", "what_if_card", "diagnose", "other")), "count")
        d9lib.result(f"{tag}.simulate_step_calls", C["steps"], "count")
        d9lib.result(f"{tag}.batch_rows", C["rows"], "count")
        d9lib.result(f"{tag}.equivalents", C["steps"] + C["rows"], "count")
        d9lib.result(f"{tag}.cycle_cpu", c.proc_ms, "ms_provisional")
        d9lib.result(f"{tag}.status", coord.data.get("optimization_status"), "text")
    dt_util.freeze(None)
    return tfs


tfs = []
tfs += run_cycles("two_zone_dhw", {**DHW, **TWO_ZONE})
tfs += run_cycles("minimal_nodhw", {})
tfs += run_cycles("perturb_price_tiles", {**DHW, **TWO_ZONE, const.CONF_PRICE_TILES_ENABLED: True})
tfs += run_cycles("perturb_fuse_advisor", {**DHW, **TWO_ZONE, const.CONF_MAIN_FUSE_A: 20})
# The on-demand what-if the card issues (not a per-cycle path): one call.
hass, coord = make_coordinator({**DHW, **TWO_ZONE})
dt_util.freeze(START + timedelta(hours=8, minutes=3))
coord.data = asyncio.run(coord._async_update_data())
dt_util.freeze(START + timedelta(hours=8, minutes=4))
reset()
answer = asyncio.run(coord.async_simulate({"target_temp": 22.0}))
d9lib.result("card_what_if.optimize_calls", C["optimize"], "count")
d9lib.result("card_what_if.multi_start.what_if_card", C["what_if_card"], "count")
d9lib.result("card_what_if.rate_limited", answer.get("rate_limited"), "bool")
dt_util.freeze(None)

d9lib.closing(float(np.median(tfs)))
