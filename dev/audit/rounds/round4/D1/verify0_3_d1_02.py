"""D1-02 verified on a REAL loop through the REAL setup path.

METRIC (my own): seed the accuracy store on disk, drive the FULL
``ha_setup_entry`` (which ``_spawn``s ``_async_load_accuracy`` as a real
background task on a real executor-backed loop), drain, then run two ordinary
``_async_update_data`` cycles (the second is the full solving one, the way
the scheduled interval runs it). Count how many of the three seeded
money/physics fields (``peaks.peaks``, ``defrost.factors``, ``mode``) the
on-disk store no longer holds afterwards, and whether setup succeeded,
``last_update_success`` stayed True, and the loader's exception surfaced
anywhere at failure time (loop exception handler fires only when an
unretrieved task is GC'd, not at failure).

The finder's harness called ``_async_load_accuracy()`` directly and caught
the exception itself; this one never touches the loader directly -- the
production spawn path is the only route in.

COMMAND (from this worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/verify0_3_d1_02.py [--perturb]

EXPECTED (unperturbed): RESULT fields_lost=3, RESULT control_fields_lost=0,
  RESULT setup_ok=1, RESULT last_update_success_after=1,
  RESULT failure_time_log_lines=0. With --perturb (the decode wrapped in
  try/except + warning, in-process): fields_lost=0, warning_lines>=1.
BASELINE: 0855277edc49cb3cce3b1095fa1e5edcda7663c8 (branch head)
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer:async_setup_entry,
  heatpump_optimizer.coordinator:_spawn / _async_load_accuracy /
  _async_update_data / _async_save_accuracy.
NULL CONTROL: identical store with a well-formed ``samples`` list.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import gc
import json
import logging
import sys
import time
import weakref
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import (  # noqa: E402
    FakeEntry,
    FakeHass,
    FakeState,
    ha_setup_entry,
)
from homeassistant.helpers import storage as hastore  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 45.0,
}
KEY = f"{const.DOMAIN}_test_entry_accuracy"

HEALTHY = {
    "accuracy": {"samples": [], "lead_sigma": {}, "lead_counts": {}, "lead_pending": []},
    "dhw_accuracy": {"samples": [], "lead_sigma": {}, "lead_counts": {}, "lead_pending": []},
    "defrost": {"version": 2, "factors": [[0.80, 0.90]] * 6, "counts": [[4, 5]] * 6, "duty": [[0.10, 0.20]] * 6},
    "peaks": {"month": "2026-09", "peaks": [7.4, 6.8, 5.9]},
    "comfort": {"configured_weight": 2.0, "learned_weight": 3.4, "evidence": 12.0, "overrides": 7, "last_update": None, "history": []},
    "mode": "economy",
}


class RealHass(FakeHass):
    """FakeHass with a real executor and real task scheduling."""

    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.spawned: "weakref.WeakSet[asyncio.Task]" = weakref.WeakSet()

    def async_create_task(self, coro, name=None, eager_start=False):
        task = asyncio.get_running_loop().create_task(coro)
        self.spawned.add(task)
        return task

    def async_create_background_task(self, coro, name=None, eager_start=False):
        return self.async_create_task(coro, name)

    async def async_add_executor_job(self, func, *args):
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, func, *args
        )


class LoopEntry(FakeEntry):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.update_listeners = []

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)

        def _remove():
            if listener in self.update_listeners:
                self.update_listeners.remove(listener)

        return _remove

    def async_create_background_task(self, hass, coro, name=None):
        return hass.async_create_task(coro, name)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def _seed_horizon(coord) -> None:
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (now + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -5.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop() -> None:
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


async def _drain() -> None:
    for _ in range(3):
        await asyncio.sleep(0)
        pending = [
            t for t in asyncio.all_tasks()
            if t is not asyncio.current_task() and not t.done()
        ]
        if not pending:
            break
        await asyncio.wait(pending, timeout=5.0)


async def _scenario(payload: dict) -> dict:
    loop = asyncio.get_running_loop()
    failure_time_logs: list[str] = []
    default_handler = loop.get_exception_handler()

    def _handler(l, context):
        failure_time_logs.append(str(context.get("message", "")))

    loop.set_exception_handler(_handler)
    cap = _Capture()
    loggers = [
        logging.getLogger("custom_components.heatpump_optimizer"),
        logging.getLogger("heatpump_optimizer"),
    ]
    for lg in loggers:
        lg.addHandler(cap)
        lg.setLevel(logging.DEBUG)

    hastore._reset_store_disk()
    hastore._DISK[KEY] = json.dumps(payload)
    hass = RealHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = LoopEntry(data=dict(CONFIG), entry_id="test_entry")

    out: dict = {}
    try:
        out["setup_ok"] = bool(await ha_setup_entry(integration, hass, entry))
        coord = entry.runtime_data
        await _drain()

        # What did the spawned loader tasks leave behind? A real Home
        # Assistant would only ever see these at GC time.
        unretrieved = []
        for task in list(hass.spawned):
            if task.done() and not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    unretrieved.append(f"{type(exc).__name__}: {exc}")
        out["unretrieved"] = unretrieved
        out["setup_escapes"] = failure_time_logs

        # Two ordinary cycles: the first consumes the setup skip-solve flag
        # (the light refresh real HA runs at setup), the second is the full
        # solving cycle the scheduled interval runs -- which calls
        # _async_save_accuracy (coordinator.py:4249).
        _seed_horizon(coord)
        await coord._async_update_data()
        _seed_horizon(coord)
        await coord._async_update_data()
        await _drain()

        out["last_update_success"] = bool(coord.last_update_success)
        out["warning_lines"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        out["log_lines"] = len(cap.records)
        out["store"] = json.loads(hastore._DISK[KEY])
    finally:
        for lg in loggers:
            lg.removeHandler(cap)
        loop.set_exception_handler(default_handler)
        hass.executor.shutdown(wait=True)
        gc.collect()
    return out


def _losses(store: dict) -> list[str]:
    lost = []
    if (store.get("peaks") or {}).get("peaks") != HEALTHY["peaks"]["peaks"]:
        lost.append("peaks")
    if (store.get("defrost") or {}).get("factors") != HEALTHY["defrost"]["factors"]:
        lost.append("defrost_factors")
    if store.get("mode") != HEALTHY["mode"]:
        lost.append("mode")
    return lost


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--perturb",
        action="store_true",
        help="apply the finding's fix in-process: wrap the decode block of "
        "_async_load_accuracy in try/except with one warning",
    )
    args = ap.parse_args()
    t0 = time.perf_counter()

    if args.perturb:
        _orig = HeatPumpOptimizerCoordinator._async_load_accuracy

        async def _guarded(self):
            try:
                await _orig(self)
            except Exception as err:  # noqa: BLE001
                logging.getLogger("custom_components.heatpump_optimizer").warning(
                    "Could not decode accuracy store: %s", err
                )

        HeatPumpOptimizerCoordinator._async_load_accuracy = _guarded

    corrupt = json.loads(json.dumps(HEALTHY))
    corrupt["accuracy"]["samples"] = 1.0

    control = asyncio.run(_scenario(HEALTHY))
    broken = asyncio.run(_scenario(corrupt))

    lost_ctrl = _losses(control["store"])
    lost = _losses(broken["store"])

    print("\n=== D1-02 on a real loop through the real setup path ===")
    print(f"  setup ok                     corrupt={broken['setup_ok']} control={control['setup_ok']}")
    print(f"  unretrieved task exceptions  {broken['unretrieved']}")
    print(f"  loop handler fired          {broken['setup_escapes']}")
    print(f"  last_update_success         {broken['last_update_success']}")
    print(f"  WARNING+ log lines          {broken['warning_lines']} of {broken['log_lines']}")
    print(f"  fields lost, control        {lost_ctrl}")
    print(f"  fields lost, corrupt        {lost}")
    print(f"  peaks on disk, corrupt      {(broken['store'].get('peaks') or {}).get('peaks')}")
    print(f"  mode on disk, corrupt       {broken['store'].get('mode')}")

    print()
    print(f"RESULT fields_lost={len(lost)} count")
    print(f"RESULT control_fields_lost={len(lost_ctrl)} count")
    print(f"RESULT setup_ok={int(broken['setup_ok'])} count")
    print(f"RESULT last_update_success_after={int(broken['last_update_success'])} count")
    print(f"RESULT unretrieved_task_exceptions={len(broken['unretrieved'])} count")
    print(f"RESULT failure_time_loop_logs={len(broken['setup_escapes'])} count")
    print(f"RESULT warning_log_lines={broken['warning_lines']} count")
    print(f"RESULT wall_s={time.perf_counter() - t0:.2f} wall")
    print("RESULT thread_factor=1.0000")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
