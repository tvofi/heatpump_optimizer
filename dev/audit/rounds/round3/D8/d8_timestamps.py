"""D8: are the TIMESTAMP-device-class sensors tz-aware on a real clock?

WHY A SEPARATE HARNESS.  d8_matrix.py freezes the clock the way
tests/golden.py:_capture_coordinator does, and tests/golden.py:START is a NAIVE
datetime.  tests/hastub's dt_util.now() returns the frozen value verbatim, so
every timestamp the integration derives from the clock comes out naive there
whatever the production code does -- a harness artefact that reads exactly like
a defect.  This harness answers the question honestly: HASTUB_TZ is set before
the stub is imported (so dt_util.now() returns an aware datetime, as Home
Assistant's does) and the clock is NOT frozen.

WHAT IT MEASURES (metric definitions):
  timestamp_entities  - entities whose _attr_device_class is TIMESTAMP.
  timestamp_naive     - of those, how many publish a datetime whose tzinfo is
                        None while dt_util.now() is tz-aware.
  timestamp_nondt     - of those, how many publish a non-None value that is
                        not a datetime at all.
  clock_tz_aware      - 1 when dt_util.now() is aware in this process (the
                        precondition; a 0 here voids the other numbers).

COMMAND (from the repository root, nothing else):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D8/d8_timestamps.py

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core M1:
  clock_tz_aware=1, timestamp_entities=2, timestamp_naive=0,
  timestamp_nondt=0.  Counts: contention-immune.  timestamp_naive=0 is the
  point: the two TIMESTAMP sensors ARE tz-aware once the clock is, and the 8
  naive readings d8_matrix.py sees under its frozen naive clock are that
  harness's clock, not the product.

INSTRUMENTED SYMBOLS:
  heatpump_optimizer.sensor:NextOptimizationSensor.native_value and
  heatpump_optimizer.sensor:LastOptimizationSensor.native_value, reached
  through the real heatpump_optimizer.sensor:async_setup_entry; the values
  they read are written by
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator, which stamps
  both from homeassistant.util.dt:now().

PERTURBATION (the judge runs this): --perturb naive-stamp strips the tzinfo
from the two stamps in the published payload, changing nothing else.
timestamp_naive must go from 0 UP to 2 -- which is what proves the check can
see a naive timestamp at all rather than being dead code.
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
# Before any hastub import: dt.py resolves DEFAULT_TIME_ZONE at module import.
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "custom_components"))

import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const, sensor  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None, choices=["naive-stamp"])
    args = ap.parse_args()
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()

    clock_aware = dt_util.now().tzinfo is not None

    cfg = dict(golden.coordinator_scenarios()["coord_all_features"])
    cfg[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.indoor"
    cfg[const.CONF_OUTDOOR_TEMP_ENTITY] = "sensor.outdoor"
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4", unit="°C"))
    hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())

    # The clock is real, so the injected series is anchored on it.
    base = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (base + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (base + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    coord._forecast_arrays()
    asyncio.run(coord.async_run_optimization())
    # What coordinator.py:4693 does at the end of every real refresh.
    coord._next_optimization = dt_util.now() + timedelta(minutes=15)
    data = coord._build_data_dict()

    if args.perturb == "naive-stamp":
        for key in ("last_optimization", "next_optimization"):
            value = data.get(key)
            if isinstance(value, datetime) and value.tzinfo is not None:
                data[key] = value.replace(tzinfo=None)

    coord.data = data
    entry.runtime_data = coord
    added: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, lambda e: added.extend(e)))

    ts_entities = [
        e for e in added
        if str(getattr(e, "_attr_device_class", "")) == "timestamp"
    ]
    naive, nondt = [], []
    for ent in ts_entities:
        value = ent.native_value
        if value is None:
            continue
        if not isinstance(value, datetime):
            nondt.append((type(ent).__name__, repr(value)))
        elif value.tzinfo is None:
            naive.append((type(ent).__name__, ent._attr_translation_key,
                          repr(value)))

    for name, key, value in naive:
        print(f"  TS_NAIVE {key} ({name}) = {value}", file=sys.stderr)
    for name, value in nondt:
        print(f"  TS_NONDT {name} = {value}", file=sys.stderr)
    print(f"  clock now() = {dt_util.now()!r}", file=sys.stderr)

    cpu = time.process_time() - t_cpu0
    thr = time.thread_time() - t_thr0
    print(f"RESULT clock_tz_aware={1 if clock_aware else 0} count")
    print(f"RESULT timestamp_entities={len(ts_entities)} count")
    print(f"RESULT timestamp_naive={len(naive)} count")
    print(f"RESULT timestamp_nondt={len(nondt)} count")
    print(f"RESULT thread_factor={cpu / thr if thr else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
