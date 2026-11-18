"""D12 generalization: drive setup and one coordinator cycle for one plant cell.

Metric definition (one line): a cell FAILS when driving setup + one real
coordinator cycle + every platform's ``async_setup_entry`` raises, publishes no
plan without a named refusal, or publishes a value for a plant part the config
omitted.

Not a harness itself -- the runnable harnesses import it.  Run them from the
repository root with PYTHONPATH=tests/hastub.

Baseline: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697.  Machine: MacBookAir10,1
(8-core Apple M1, 8 GB).  Every number it produces is a COUNT, immune to box
load.
"""
from __future__ import annotations

import os

# Thread pin, copied from tests/stress.py, before any numpy import.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor as binary_sensor_mod,
    button as button_mod,
    climate as climate_mod,
    const,
    datetime as datetime_mod,
    sensor as sensor_mod,
    switch as switch_mod,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = golden.START

PLATFORMS = (
    ("sensor", sensor_mod),
    ("binary_sensor", binary_sensor_mod),
    ("button", button_mod),
    ("climate", climate_mod),
    ("switch", switch_mod),
    ("datetime", datetime_mod),
)


def _prices():
    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def _weather():
    return [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


def _solar():
    return [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


def build(config, states=None):
    """A coordinator with the same injected inputs golden.py:_capture_coordinator uses."""
    hass = FakeHass()
    for entity_id, state in (states or {}).items():
        hass.states.set(entity_id, state)
    entry = FakeEntry(data=dict(config))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = _prices()
    coord._weather_forecast = _weather()
    coord._solar_radiation_forecast = _solar()
    return hass, entry, coord


def _entity_state(entity):
    for attr in ("native_value", "is_on", "current_temperature", "native_unit_of_measurement"):
        if hasattr(entity, attr):
            return getattr(entity, attr)
    return None


def drive_cell(name, config, states=None, run_solve=True):
    """Setup + one coordinator cycle + every platform's entities.

    Returns a dict with ``ok`` and, when it is False, ``first_failing_step``
    and ``detail``.  Steps, in the order they are attempted:

      construct -> update_state -> solve -> build_data -> setup_<platform>
      -> publish_<platform>
    """
    out = {
        "cell": name,
        "ok": True,
        "first_failing_step": None,
        "detail": None,
        "solve_status": None,
        "plan_steps": 0,
        "entities": 0,
        "unavailable": 0,
        "data": None,
        "published": {},
    }
    dt_util.freeze(START)
    try:
        try:
            hass, entry, coord = build(config, states)
        except Exception as err:  # noqa: BLE001
            out.update(ok=False, first_failing_step="construct",
                       detail=f"{type(err).__name__}: {err}",
                       traceback=traceback.format_exc()[-1500:])
            return out

        async def _cycle():
            await coord._update_current_state()
            if run_solve:
                out["solve_status"] = await coord.async_run_optimization()
            coord.data = coord._build_data_dict()

        try:
            asyncio.run(_cycle())
        except Exception as err:  # noqa: BLE001
            out.update(ok=False, first_failing_step="cycle",
                       detail=f"{type(err).__name__}: {err}",
                       traceback=traceback.format_exc()[-1500:])
            return out

        data = coord.data
        out["data"] = data
        out["plan_steps"] = len(data.get("schedule") or [])
        if run_solve and out["solve_status"] is None and out["plan_steps"] == 0:
            out.update(ok=False, first_failing_step="plan",
                       detail="solve reported success and published an empty schedule")

        entry.runtime_data = coord
        for pname, module in PLATFORMS:
            added = []
            try:
                asyncio.run(module.async_setup_entry(hass, entry, added.extend))
            except Exception as err:  # noqa: BLE001
                if out["ok"]:
                    out.update(ok=False, first_failing_step=f"setup_{pname}",
                               detail=f"{type(err).__name__}: {err}",
                               traceback=traceback.format_exc()[-1500:])
                continue
            for entity in added:
                out["entities"] += 1
                key = getattr(entity, "_key", None) or type(entity).__name__
                try:
                    available = bool(entity.available)
                except Exception as err:  # noqa: BLE001
                    if out["ok"]:
                        out.update(ok=False, first_failing_step=f"publish_{pname}",
                                   detail=f"{key}.available: {type(err).__name__}: {err}",
                                   traceback=traceback.format_exc()[-1500:])
                    continue
                if not available:
                    out["unavailable"] += 1
                try:
                    value = _entity_state(entity)
                    attrs = getattr(entity, "extra_state_attributes", None)
                except Exception as err:  # noqa: BLE001
                    if out["ok"]:
                        out.update(ok=False, first_failing_step=f"publish_{pname}",
                                   detail=f"{key}: {type(err).__name__}: {err}",
                                   traceback=traceback.format_exc()[-1500:])
                    continue
                out["published"][str(key)] = {
                    "available": available,
                    "value": value,
                    "attrs": attrs,
                }
        return out
    finally:
        dt_util.freeze(None)


def load1():
    return round(os.getloadavg()[0], 2)


def swapins():
    return resource.getrusage(resource.RUSAGE_SELF).ru_nswap


class Timer:
    def __enter__(self):
        self.w0, self.c0 = time.perf_counter(), time.process_time()
        return self

    def __exit__(self, *a):
        self.wall = time.perf_counter() - self.w0
        self.cpu = time.process_time() - self.c0
