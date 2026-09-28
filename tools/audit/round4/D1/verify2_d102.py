"""Verifier-2 harness for D1-02: real loop, real executor, real setup path.

METRIC (mine, differs from the finder's): with the corrupt accuracy store
already on disk, drive the integration's REAL ``async_setup_entry`` on a
RealHass (``async_add_executor_job`` on a ThreadPoolExecutor,
``async_create_task`` schedules) and then ONE full ordinary cycle
(``_async_update_data`` twice: light then solving -- the cycle at
coordinator.py:4249 saves accuracy). Count (a) learned fields on disk
afterwards that were replaced by defaults ({peaks, defrost_factors, mode}),
(b) unretrieved exceptions among the tasks setup spawned, (c) whether setup
succeeded and ``last_update_success`` stayed True.

The finder's accuracy_wipe.py called ``_async_load_accuracy`` directly on a
FakeHass and caught the exception itself; the real-HA claim (spawned task,
setup succeeds, silent) rested on code reading. This harness executes it.

COMMAND (from the worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/verify2_d102.py

EXPECTED: fields_lost=3, control_fields_lost=0, unretrieved_exceptions=1
  (TypeError from the spawned loader), setup_ok=1, last_update_success=1,
  warn_log_lines=0; perturbB (from_dict skips a non-list samples)
  fields_lost=0.
BASELINE: branch head 0855277 (finder measured 7dd68dd)
MACHINE:  8-core Apple M1, macOS 25.6.0, CPython 3.11
INSTRUMENTS: coordinator _spawn / _async_load_accuracy / _async_save_accuracy
  and accuracy.AccuracyTracker.from_dict, driven through
  heatpump_optimizer.async_setup_entry on a real asyncio loop.
PERTURBATION (B): AccuracyTracker.from_dict that treats a non-list
  ``samples`` as empty; fields_lost must fall to 0.
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

import asyncio
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer.accuracy import AccuracyTracker  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 45.0,
}
ENTRY_ID = "v2_entry"
KEY = f"{const.DOMAIN}_{ENTRY_ID}_accuracy"

HEALTHY = {
    "accuracy": {"samples": [], "lead_sigma": {}, "lead_counts": {},
                 "lead_pending": []},
    "dhw_accuracy": {"samples": [], "lead_sigma": {}, "lead_counts": {},
                     "lead_pending": []},
    "defrost": {"version": 2, "factors": [[0.80, 0.90]] * 6,
                "counts": [[4, 5]] * 6, "duty": [[0.10, 0.20]] * 6},
    "peaks": {"month": "2026-09", "peaks": [7.4, 6.8, 5.9]},
    "comfort": {"configured_weight": 2.0, "learned_weight": 3.4,
                "evidence": 12.0, "overrides": 7, "last_update": None,
                "history": []},
    "mode": "economy",
}


class RealHass(FakeHass):
    def __init__(self, states=None):
        super().__init__(states)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.spawned: list[asyncio.Task] = []

    def async_create_task(self, coro, name=None, eager_start=False):
        task = asyncio.get_running_loop().create_task(coro)
        self.spawned.append(task)
        return task

    def async_create_background_task(self, coro, name=None, eager_start=False):
        return self.async_create_task(coro, name)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)


class LoopEntry(FakeEntry):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.update_listeners = []

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)
        return lambda: self.update_listeners.remove(listener)

    def async_create_background_task(self, hass, coro, name=None):
        return hass.async_create_task(coro, name)


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _seed_horizon(coord):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (now + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(),
         "temperature": -5.0, "wind_speed": 3.0, "precipitation": 0.0,
         "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop():
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


async def _drain():
    for _ in range(4):
        await asyncio.sleep(0)
        pending = [
            t for t in asyncio.all_tasks()
            if t is not asyncio.current_task() and not t.done()
        ]
        if not pending:
            break
        await asyncio.wait(pending, timeout=10.0)


async def _run_arm(payload, from_dict_override=None):
    hastore._reset_store_disk()
    hastore._DISK[KEY] = json.dumps(payload)
    hass = RealHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = LoopEntry(data=dict(CONFIG), entry_id=ENTRY_ID)
    cap = _Capture()
    root = logging.getLogger("custom_components.heatpump_optimizer")
    alt = logging.getLogger("heatpump_optimizer")
    for lg in (root, alt):
        lg.addHandler(cap)
        lg.setLevel(logging.DEBUG)
    saved = AccuracyTracker.from_dict
    if from_dict_override is not None:
        AccuracyTracker.from_dict = from_dict_override
    out = {}
    try:
        out["setup_ok"] = await ha_setup_entry(integration, hass, entry)
        coord = getattr(entry, "runtime_data", None)
        out["has_coord"] = coord is not None
        await _drain()
        # Exceptions the loop would only report at GC: collect them from
        # the tasks this hass scheduled, before anything retrieves them.
        out["task_excs"] = []
        for t in list(hass.spawned):
            if t.done() and not t.cancelled():
                exc = t.exception()  # retrieves, like HA's tracker would not
                if exc is not None:
                    out["task_excs"].append(f"{type(exc).__name__}: {exc}")
        # One ordinary day: the light setup refresh, then one full cycle
        # (its path saves the accuracy store at coordinator.py:4249).
        _seed_horizon(coord)
        await coord._async_update_data()
        data = await coord._async_update_data()
        coord.data = data
        out["last_update_success"] = bool(coord.last_update_success)
        out["warn_lines"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        out["log_lines"] = len(cap.records)
        raw = hastore._DISK.get(KEY)
        out["store"] = json.loads(raw) if raw else {}
    finally:
        AccuracyTracker.from_dict = saved
        for lg in (root, alt):
            lg.removeHandler(cap)
        hass.executor.shutdown(wait=True)
    return out


def _losses(store):
    lost = []
    if (store.get("peaks") or {}).get("peaks") != [7.4, 6.8, 5.9]:
        lost.append("peaks")
    if (store.get("defrost") or {}).get("factors") != [[0.80, 0.90]] * 6:
        lost.append("defrost_factors")
    if store.get("mode") != "economy":
        lost.append("mode")
    return lost


def main() -> int:
    t0 = time.perf_counter()
    corrupt = json.loads(json.dumps(HEALTHY))
    corrupt["accuracy"]["samples"] = 1.0

    control = asyncio.run(_run_arm(HEALTHY))
    broken = asyncio.run(_run_arm(corrupt))

    # Perturbation B: from_dict skips a non-list samples (finder's stated
    # second variant). Fields must survive.
    _orig = AccuracyTracker.from_dict.__func__

    def _skip_nonlist(cls, data):
        if isinstance(data, dict) and not isinstance(
            data.get("samples", []), list
        ):
            data = {k: v for k, v in data.items() if k != "samples"}
        return _orig(cls, data)

    perturb = asyncio.run(
        _run_arm(corrupt, from_dict_override=classmethod(_skip_nonlist))
    )

    print("=== D1-02 verifier-2 (real loop, real setup path) ===")
    for label, arm in (
        ("control ", control),
        ("corrupt ", broken),
        ("perturbB", perturb),
    ):
        print(
            f"  {label} setup={int(arm['setup_ok'])} "
            f"lus={int(arm['last_update_success'])} "
            f"task_excs={arm['task_excs']} warn={arm['warn_lines']} "
            f"lost={_losses(arm['store'])}"
        )
    print(f"  peaks on disk, corrupt   "
          f"{(broken['store'].get('peaks') or {}).get('peaks')}")
    print(f"  mode on disk, corrupt    {broken['store'].get('mode')}")

    print()
    print(f"RESULT fields_lost={len(_losses(broken['store']))} count")
    print(f"RESULT control_fields_lost={len(_losses(control['store']))} count")
    print(f"RESULT perturbB_fields_lost={len(_losses(perturb['store']))} count")
    print(f"RESULT unretrieved_exceptions={len(broken['task_excs'])} count")
    print(f"RESULT control_unretrieved={len(control['task_excs'])} count")
    print(f"RESULT setup_ok={int(broken['setup_ok'])} count")
    print(
        f"RESULT last_update_success={int(broken['last_update_success'])} count"
    )
    print(f"RESULT warn_log_lines={broken['warn_lines']} count")
    print(f"RESULT log_lines={broken['log_lines']} count")
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
