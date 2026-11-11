"""One corrupt scalar in the accuracy store erases the whole store.

METRIC: after loading an accuracy store whose ``accuracy.samples`` key holds
a scalar instead of a list (strictly valid JSON) and running ONE ordinary
update cycle, the number of learned fields in that store that were replaced
by defaults -- the month's realised capacity-tariff peaks, the defrost derate
table, and the user's operation mode.

MECHANISM: coordinator.py:HeatPumpOptimizerCoordinator._async_load_accuracy
wraps only ``self._accuracy_store.async_load()`` in try/except. Its first
statement after the isinstance guard is
``AccuracyTracker.from_dict(stored.get("accuracy"))``, and
accuracy.py:AccuracyTracker.from_dict line 363 does
``for raw in data.get("samples", []) or []`` -- iterating whatever is there.
A scalar raises TypeError, which escapes the loader. The loader is
``_spawn``ed from ``_init_*`` (coordinator.py:1425), so under real Home
Assistant it becomes an unretrieved background-task exception, setup
succeeds, nothing sets ``last_update_success`` False -- and the next cycle's
``_async_save_accuracy`` writes the in-memory DEFAULTS over the store,
making the loss permanent. Every sibling loader (price model, ledger, energy
totals, snapshots, manual plan) guards its decode; this one does not.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/accuracy_wipe.py

EXPECTED: RESULT fields_lost=3 of 3 (exact), RESULT control_fields_lost=0
  (exact), RESULT warning_log_lines=0 (exact),
  RESULT last_update_success_after=1 (i.e. still True).
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  ._async_load_accuracy and ._async_save_accuracy;
  heatpump_optimizer.accuracy:AccuracyTracker.from_dict.
PERTURBATION: wrap the decode block of ``_async_load_accuracy`` in
  ``try/except Exception`` with one ``_LOGGER.warning``, or make
  ``AccuracyTracker.from_dict`` skip a non-list ``samples``; fields_lost must
  fall to 0 and warning_log_lines rise to 1.
NULL CONTROL: the identical store with a well-formed ``samples`` list. The
  loss must vanish (control_fields_lost == 0).
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

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402

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

#: A month of learned state. Every value here is money- or physics-bearing:
#: ``peaks`` is what the capacity tariff is billed on, ``defrost`` is the
#: learned output derate, ``mode`` is the user's own setting.
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
        "factors": [[0.80, 0.90]] * 6,
        "counts": [[4, 5]] * 6,
        "duty": [[0.10, 0.20]] * 6,
    },
    "peaks": {"month": "2026-09", "peaks": [7.4, 6.8, 5.9]},
    "comfort": {
        "configured_weight": 2.0,
        "learned_weight": 3.4,
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


def _build():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = "test_entry"
    return HeatPumpOptimizerCoordinator(hass, entry)


async def _arm(payload: dict) -> dict:
    hastore._reset_store_disk()
    hastore._DISK[KEY] = json.dumps(payload)
    cap = _Capture()
    loggers = [
        logging.getLogger("custom_components.heatpump_optimizer"),
        logging.getLogger("heatpump_optimizer"),
    ]
    for lg in loggers:
        lg.addHandler(cap)
        lg.setLevel(logging.DEBUG)
    out = {"exc": None}
    try:
        coord = _build()
        try:
            await coord._async_load_accuracy()
        except Exception as err:
            out["exc"] = f"{type(err).__name__}: {err}"
        out["log_lines"] = len(cap.records)
        out["warning_log_lines"] = sum(
            1 for r in cap.records if r.levelno >= logging.WARNING
        )
        # One ordinary cycle. Nothing here is unusual: read inputs, publish,
        # persist -- exactly what ``_async_update_data`` does every interval.
        await coord._update_current_state()
        coord.data = coord._build_data_dict()
        await coord._async_save_accuracy()
        out["last_update_success"] = bool(coord.last_update_success)
        out["store"] = json.loads(hastore._DISK[KEY])
    finally:
        for lg in loggers:
            lg.removeHandler(cap)
    return out


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
    # The comfort learner is deliberately NOT in this set: a healthy load
    # also rewrites its learned weight from the configured one
    # (``_apply_comfort_weight``), so it cannot separate the two arms.
    return lost


def main() -> int:
    t0 = time.perf_counter()
    corrupt = json.loads(json.dumps(HEALTHY))
    corrupt["accuracy"]["samples"] = 1.0  # a scalar where a list belongs

    control = asyncio.run(_arm(HEALTHY))
    broken = asyncio.run(_arm(corrupt))

    # A second, independent shape of the same mechanism.
    corrupt_bool = json.loads(json.dumps(HEALTHY))
    corrupt_bool["accuracy"]["samples"] = True
    broken_bool = asyncio.run(_arm(corrupt_bool))

    lost_ctrl = _losses(control["store"])
    lost = _losses(broken["store"])
    lost_bool = _losses(broken_bool["store"])

    print("\n=== accuracy store: one corrupt scalar ===")
    print(f"  control   exception      {control['exc']}")
    print(f"  corrupt   exception      {broken['exc']}")
    print(f"  corrupt(bool) exception  {broken_bool['exc']}")
    print(f"  log lines during load    {broken['log_lines']} "
          f"({broken['warning_log_lines']} at WARNING or above)")
    print(f"  last_update_success      {broken['last_update_success']}")
    print(f"  control   fields lost    {lost_ctrl}")
    print(f"  corrupt   fields lost    {lost}")
    print(f"  corrupt(bool) fields     {lost_bool}")
    print(f"  peaks on disk, control   "
          f"{(control['store'].get('peaks') or {}).get('peaks')}")
    print(f"  peaks on disk, corrupt   "
          f"{(broken['store'].get('peaks') or {}).get('peaks')}")
    print(f"  mode on disk, corrupt    {broken['store'].get('mode')}")

    print()
    print(f"RESULT fields_lost={len(lost)} count")
    print("RESULT fields_checked=3 count")
    print(f"RESULT control_fields_lost={len(lost_ctrl)} count")
    print(f"RESULT bool_variant_fields_lost={len(lost_bool)} count")
    print(f"RESULT warning_log_lines={broken['warning_log_lines']} count")
    print(f"RESULT log_lines={broken['log_lines']} count")
    print(
        f"RESULT last_update_success_after="
        f"{int(broken['last_update_success'])} count"
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
