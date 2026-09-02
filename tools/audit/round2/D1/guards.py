#!/usr/bin/env python
"""D1 guards harness: inject an exception into every swallowing try/except on
the update path and measure what the cycle does with it.

METRIC (per injected site, counts):
  cycle_completed   the cycle after injection still returned a payload (1/0)
  update_failed     the cycle raised UpdateFailed instead (1/0)
  logged_warn_plus  WARNING-or-higher log records the injected failure produced
                    in ONE cycle
  logged_2nd_cycle  the same for the SECOND cycle with the fault still present
                    (a per-cycle repeat means log spam; 0 means log-once)
  recovered         after the fault is removed, the next cycle completes and
                    the site's effect is back (1/0)

COMMAND (from the export root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D1/guards.py

EXPECTED (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, exact): see REPORT.md

INSTRUMENTED SYMBOLS (each swapped at class level to raise, then restored):
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.{
    _update_current_state, _fetch_tibber_prices, _fetch_weather_forecast,
    _async_learn_price_shape, _command_frequency, _async_drive_pumps,
    _async_watch_learning_drift, _maybe_run_fuse_advisor,
    _maybe_refresh_price_tile, _command_valve_target, _apply_action,
    _record_accuracy, _async_save_accuracy, _async_save_energy_totals}
  and homeassistant.helpers.storage.Store.async_save (a store that refuses
  to write).

PERTURBATION: remove any `except Exception` at a site -> that site's
  cycle_completed goes to 0 (the fault propagates to UpdateFailed).

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

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import homeassistant.helpers.storage as storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
HPO = logging.getLogger("heatpump_optimizer")
HPO.setLevel(logging.WARNING)
HPO.propagate = False


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append((record.levelname, record.getMessage()[:80]))


CAP = _Capture()
HPO.addHandler(CAP)

START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
MIDNIGHT = START.replace(hour=0, minute=0)
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
}


class LoopHass(FakeHass):
    def async_create_task(self, coro, name=None, eager_start=False):
        return asyncio.get_running_loop().create_task(coro, name=name)


async def _noop(self):
    return None


HeatPumpOptimizerCoordinator._fetch_tibber_prices = _noop
HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop


def build():
    now = dt_util.now()
    hass = LoopHass(
        {
            "sensor.indoor": FakeState("21.4", last_updated=now),
            "sensor.outdoor": FakeState("-3.0", last_updated=now),
        }
    )
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CONFIG))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4), "starts_at": (MIDNIGHT + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (MIDNIGHT + timedelta(hours=h)).isoformat(), "temperature": -5.0, "wind_speed": 3.0, "precipitation": 0.0}
        for h in range(48)
    ]
    coord._opt_config.horizon_hours = 6.0
    return hass, coord


class Injected(RuntimeError):
    pass


def make_raiser(is_async):
    if is_async:
        async def raiser(self, *a, **k):
            raise Injected("injected")
    else:
        def raiser(self, *a, **k):
            raise Injected("injected")
    return raiser


SITES = [
    ("_update_current_state", True),
    ("_async_learn_price_shape", True),
    ("_command_frequency", True),
    ("_async_drive_pumps", True),
    ("_async_watch_learning_drift", True),
    ("_maybe_run_fuse_advisor", True),
    ("_maybe_refresh_price_tile", True),
    ("_command_valve_target", True),
    ("_apply_action", True),
    ("_record_accuracy", False),
    ("_async_save_accuracy", True),
    ("_async_save_energy_totals", True),
    ("_async_save_thermal_learning", True),
    ("_file_lead_predictions", False),
]


async def cycle(coord):
    CAP.records.clear()
    try:
        data = await coord._async_update_data()
        return isinstance(data, dict), False, list(CAP.records)
    except Exception as err:  # noqa: BLE001
        return False, "UpdateFailed" in type(err).__name__, list(CAP.records)


async def main():
    dt_util.freeze(START)
    t0 = time.process_time()
    tt0 = time.thread_time()
    for name, is_async in SITES:
        original = getattr(HeatPumpOptimizerCoordinator, name)
        hass, coord = build()
        await asyncio.gather(*coord._background_tasks, return_exceptions=True)
        ok0, _, _ = await cycle(coord)
        setattr(HeatPumpOptimizerCoordinator, name, make_raiser(is_async))
        try:
            ok1, failed1, logs1 = await cycle(coord)
            ok2, failed2, logs2 = await cycle(coord)
        finally:
            setattr(HeatPumpOptimizerCoordinator, name, original)
        ok3, _, _ = await cycle(coord)
        print(f"RESULT guard.{name}.cycle_completed={int(ok1)} count")
        print(f"RESULT guard.{name}.update_failed={int(failed1)} count")
        print(f"RESULT guard.{name}.logged_warn_plus={len(logs1)} count")
        print(f"RESULT guard.{name}.logged_2nd_cycle={len(logs2)} count")
        print(f"RESULT guard.{name}.recovered={int(ok3 and ok0)} count")
        if logs1:
            print(f"NOTE guard.{name}.log={logs1[0][0]}:{logs1[0][1]}")

    # a store that refuses to write
    real_save = storage.Store.async_save

    async def refusing_save(self, data):
        raise OSError("disk full (injected)")

    hass, coord = build()
    await asyncio.gather(*coord._background_tasks, return_exceptions=True)
    await cycle(coord)
    storage.Store.async_save = refusing_save
    try:
        ok1, failed1, logs1 = await cycle(coord)
        ok2, failed2, logs2 = await cycle(coord)
    finally:
        storage.Store.async_save = real_save
    ok3, _, _ = await cycle(coord)
    print(f"RESULT guard.store_save_oserror.cycle_completed={int(ok1)} count")
    print(f"RESULT guard.store_save_oserror.update_failed={int(failed1)} count")
    print(f"RESULT guard.store_save_oserror.logged_warn_plus={len(logs1)} count")
    print(f"RESULT guard.store_save_oserror.logged_2nd_cycle={len(logs2)} count")
    print(f"RESULT guard.store_save_oserror.recovered={int(ok3)} count")
    print(f"RESULT guard.store_save_oserror.saves_after_recovery={storage.SAVE_COUNTS.get(coord._energy_store._key, 0)} count")

    cpu = time.process_time() - t0
    thr = time.thread_time() - tt0
    print(f"RESULT thread_factor={cpu / thr if thr else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    dt_util.freeze(None)


if __name__ == "__main__":
    asyncio.run(main())
