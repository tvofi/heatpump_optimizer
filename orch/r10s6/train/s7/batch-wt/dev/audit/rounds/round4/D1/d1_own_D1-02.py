"""D1-02 verified independently (verifier seat D1-1, round 4).

MY METRIC (differs from the finder's): with an accuracy store whose
``accuracy.samples`` holds the JSON number 1.0, loaded by a REAL background
task exactly as ``_spawn`` creates it in real Home Assistant (exception
deliberately NOT retrieved until after the measurement), and then ONE FULL
``_async_update_data()`` cycle driven with seeded prices and weather -- the
count of money- or physics-bearing fields on disk that no longer equal the
healthy payload (month peaks, defrost derate table, operation mode), plus
whether the cycle completed (payload published, ``last_update_success``
True) and how many log lines the integration emitted at WARNING or above.

Matched control: identical store, well-formed ``samples`` list. Second
shape: ``samples = true``. Perturbation: ``AccuracyTracker.from_dict``
monkeypatched to skip a non-list ``samples`` (the finding's own one-line
fix) -- the loss must vanish. No production file is edited.

COMMAND (from this worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/d1_own_D1-02.py
EXPECTED: full_cycle_fields_lost=3 of 3 exact, control_fields_lost=0,
  bool_variant_fields_lost=3, fixed_fields_lost=0,
  cycle_completed_and_success=1, warning_log_lines=0,
  spawned_task_raised_typeerror=1, strict_json_payload=1.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (tree verified identical
  for custom_components/heatpump_optimizer/*.py at 0855277).
MACHINE: 8-core Apple M1, macOS 25.6.0, CPython 3.11. All numbers are counts.
INSTRUMENTS: coordinator._async_load_accuracy (as a real spawned task),
  coordinator._async_update_data, coordinator._async_save_accuracy,
  accuracy.AccuracyTracker.from_dict.
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
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer.accuracy import AccuracyTracker  # noqa: E402
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
#: Must equal coordinator.py's f"{DOMAIN}_{entry.entry_id}_accuracy".
KEY = f"{const.DOMAIN}_d1own02_entry_accuracy"

HEALTHY = {
    "accuracy": {
        "samples": [],
        "lead_sigma": {},
        "lead_counts": {},
        "lead_pending": [],
    },
    "dhw_accuracy": {
        "samples": [],
        "lead_sigma": {},
        "lead_counts": {},
        "lead_pending": [],
    },
    "defrost": {
        "version": 2,
        "factors": [[0.77, 0.88]] * 6,
        "counts": [[4, 5]] * 6,
        "duty": [[0.10, 0.20]] * 6,
    },
    "peaks": {"month": "2026-09", "peaks": [7.1, 6.3, 5.2]},
    "comfort": {
        "configured_weight": 2.0,
        "learned_weight": 3.1,
        "evidence": 12.0,
        "overrides": 7,
        "last_update": None,
        "history": [],
    },
    "mode": "economy",
}


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def _seed_horizon(coord) -> None:
    """Deterministic prices and weather, so a full cycle can solve.

    ``now`` is truncated to the hour so the first entry sits exactly on a
    15-minute step boundary -- an entry a few microseconds past the boundary
    covers no step and the cycle skips its solve (learned the hard way).
    """
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {
            "total": round(0.5 + 0.4 * (h % 11) / 11.0, 4),
            "starts_at": (now + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (now + timedelta(hours=h)).isoformat(),
            "temperature": -6.0,
            "wind_speed": 4.0,
            "precipitation": 0.0,
            "humidity": 80.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop() -> None:
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


async def _run_arm(payload: dict) -> dict:
    hastore._reset_store_disk()
    hastore._DISK[KEY] = json.dumps(payload)
    cap = _Capture()
    # The package is imported twice under two names (custom_components.*
    # and top-level heatpump_optimizer); capture both, or the count lies.
    loggers = [
        logging.getLogger("custom_components.heatpump_optimizer"),
        logging.getLogger("heatpump_optimizer"),
    ]
    for lg in loggers:
        lg.addHandler(cap)
        lg.setLevel(logging.DEBUG)
    out: dict = {}
    try:
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("20.8"))
        hass.states.set("sensor.outdoor", FakeState("-4.0"))
        entry = FakeEntry(data=dict(CONFIG))
        entry.entry_id = "d1own02_entry"
        coord = HeatPumpOptimizerCoordinator(hass, entry)

        # Exactly what _spawn does in real HA: a background task whose
        # exception nothing retrieves. Retrieved only AFTER the cycle, so
        # the measurement sees what a user sees: nothing.
        task = asyncio.get_running_loop().create_task(
            coord._async_load_accuracy()
        )
        await asyncio.sleep(0)
        while not task.done():
            await asyncio.sleep(0)
        _seed_horizon(coord)
        data = await coord._async_update_data()
        out["cycle_payload"] = isinstance(data, dict)
        out["solved"] = getattr(coord, "_optimization_result", None) is not None
        out["last_update_success"] = bool(coord.last_update_success)
        out["warn_lines"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        out["all_lines"] = len(cap.records)
        try:
            task.result()
            out["task_exc"] = None
        except Exception as err:  # noqa: BLE001
            out["task_exc"] = f"{type(err).__name__}: {err}"
        out["store"] = json.loads(hastore._DISK[KEY])
        out["messages"] = [r.getMessage() for r in cap.records]
        return out
    finally:
        for lg in loggers:
            lg.removeHandler(cap)


def _losses(store: dict) -> list[str]:
    lost = []
    if (store.get("peaks") or {}).get("peaks") != HEALTHY["peaks"]["peaks"]:
        lost.append("peaks")
    if (store.get("defrost") or {}).get("factors") != HEALTHY["defrost"][
        "factors"
    ]:
        lost.append("defrost_factors")
    if store.get("mode") != HEALTHY["mode"]:
        lost.append("mode")
    return lost


def main() -> int:
    t0 = time.perf_counter()
    print("=== D1-02, verifier's own instrument ===")

    # The corrupt payload is strictly valid JSON: Python's json can dump it
    # with allow_nan=False, i.e. no non-standard literals anywhere; orjson
    # round-trips it.
    corrupt = json.loads(json.dumps(HEALTHY))
    corrupt["accuracy"]["samples"] = 1.0
    corrupt_bool = json.loads(json.dumps(HEALTHY))
    corrupt_bool["accuracy"]["samples"] = True
    strict = 1
    for p in (HEALTHY, corrupt, corrupt_bool):
        try:
            json.dumps(p, allow_nan=False)
        except ValueError:
            strict = 0
    print(f"  payloads dump under allow_nan=False    {bool(strict)}")

    control = asyncio.run(_run_arm(HEALTHY))
    broken = asyncio.run(_run_arm(corrupt))
    broken_bool = asyncio.run(_run_arm(corrupt_bool))

    # Perturbation: the finding's own one-line fix, monkeypatched.
    orig = AccuracyTracker.from_dict.__func__

    def guarded(cls, data):
        if isinstance(data, dict) and not isinstance(
            data.get("samples", []), list
        ):
            data = {k: v for k, v in data.items() if k != "samples"}
        return orig(cls, data)

    AccuracyTracker.from_dict = classmethod(guarded)
    try:
        fixed = asyncio.run(_run_arm(corrupt))
    finally:
        AccuracyTracker.from_dict = classmethod(orig)

    lost_ctrl = _losses(control["store"])
    lost = _losses(broken["store"])
    lost_bool = _losses(broken_bool["store"])
    lost_fix = _losses(fixed["store"])

    print(f"  control: cycle ok {control['cycle_payload']}, "
          f"success {control['last_update_success']}, "
          f"task {control['task_exc']}")
    print(f"  corrupt: cycle ok {broken['cycle_payload']}, "
          f"success {broken['last_update_success']}, "
          f"task {broken['task_exc']}")
    print(f"  corrupt(bool): task {broken_bool['task_exc']}, "
          f"lost {_losses(broken_bool['store'])}")
    print(f"  corrupt: WARNING+ lines {broken['warn_lines']} "
          f"of {broken['all_lines']}: {broken['messages']}")
    print(f"  corrupt: solve produced a result      "
          f"{bool(broken['solved'])}")
    print(f"  peaks on disk control  "
          f"{(control['store'].get('peaks') or {}).get('peaks')}")
    print(f"  peaks on disk corrupt  "
          f"{(broken['store'].get('peaks') or {}).get('peaks')}")
    print(f"  mode on disk corrupt   {broken['store'].get('mode')}")
    print(f"  fixed (guarded from_dict): lost {lost_fix}, "
          f"task {fixed['task_exc']}")

    ok = int(
        broken["cycle_payload"] and broken["last_update_success"]
    )
    print()
    print(f"RESULT strict_json_payload={strict} count")
    print(f"RESULT full_cycle_fields_lost={len(lost)} count")
    print("RESULT fields_checked=3 count")
    print(f"RESULT control_fields_lost={len(lost_ctrl)} count")
    print(f"RESULT bool_variant_fields_lost={len(lost_bool)} count")
    print(f"RESULT fixed_fields_lost={len(lost_fix)} count")
    print(f"RESULT cycle_completed_and_success={ok} count")
    print(f"RESULT warning_log_lines={broken['warn_lines']} count")
    print(f"RESULT all_log_lines={broken['all_lines']} count")
    print(f"RESULT solve_produced_result={int(bool(broken['solved']))} count")
    print(
        f"RESULT spawned_task_raised_typeerror="
        f"{int(isinstance(broken['task_exc'], str) and 'TypeError' in broken['task_exc'])} count"
    )
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
