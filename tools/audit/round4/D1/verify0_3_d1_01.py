"""D1-01 verified end-to-end: does the corrupt price bin move the real plan?

METRIC (my own, different from the finder's): after loading a price-shape
store whose weekend bin 22 holds the strict-JSON string "nan" and running ONE
full ``_async_update_data`` cycle (real solve, prices published only 10 h of
the 24 h horizon), (a) kWh of electrical space-heating energy the resulting
plan schedules in the 4 zero-priced steps, minus the same quantity under the
matched control store; (b) the plan's true electricity cost evaluated at the
CONTROL (real) prices, corrupt arm minus control arm, in SEK over the
horizon. The finder measured the price ARRAY; this measures the PLAN the
optimizer actually builds on it.

COMMAND (from this worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/verify0_3_d1_01.py [--perturb]

EXPECTED (unperturbed): RESULT zero_priced_steps=4, RESULT
  energy_shift_kwh > 0 (the plan moves load into the "free" hour), RESULT
  true_cost_regression_sek > 0 (the corrupt plan costs more at real prices
  than the control plan does). With --perturb (an np.isfinite filter inside
  PriceShapeModel.from_dict's shape branch, applied in-process):
  zero_priced_steps=0 and both deltas 0.
BASELINE: 0855277edc49cb3cce3b1095fa1e5edcda7663c8 (branch head)
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer.coordinator:_async_update_data /
  async_run_optimization / _forecast_arrays, driving
  heatpump_optimizer.price_model:PriceShapeModel.from_dict and
  extend_price_series; the plan is read from
  OptimizationResult.power_schedule.
NULL CONTROL: identical corrupt store, whole 48 h horizon published, so
  extend_price_series never consults the prior; every delta must vanish.
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
import json
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer.price_model import PriceShapeModel  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 45.0,
}
KEY = f"{const.DOMAIN}_test_entry_price_model"

LEARNED = [
    0.70, 0.65, 0.62, 0.60, 0.62, 0.75, 1.00, 1.35,
    1.40, 1.20, 1.05, 1.00, 0.98, 0.95, 0.95, 1.00,
    1.15, 1.35, 1.30, 1.15, 1.00, 0.90, 0.82, 0.75,
]

STORE_TEMPLATE = {
    "model": {
        "shapes": [None, None],  # filled per arm
        "days": [30, 30],
        "quarter_factors": [[1.0] * 96 for _ in range(2)],
        "quarter_days": [30, 30],
        "residual_var": [[0.01] * 24 for _ in range(2)],
    },
    "days_seen": [],
    "quarter_days_seen": [],
}


def _prices(now, hours):
    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (now + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(hours)
    ]


def _weather(now, hours):
    return [
        {
            "datetime": (now + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(hours)
    ]


async def _cycle(weekday_shape, weekend_shape, published_hours):
    """One full ordinary cycle on a coordinator whose price store is armed."""
    hastore._reset_store_disk()
    payload = json.loads(json.dumps(STORE_TEMPLATE))
    payload["model"]["shapes"] = [weekday_shape, weekend_shape]
    # Strict-JSON round trip: a bare float("nan") would not survive orjson;
    # the STRING "nan" does, and float("nan") is NaN on load.
    hastore._DISK[KEY] = json.dumps(payload, allow_nan=False)

    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = "test_entry"
    coord = HeatPumpOptimizerCoordinator(hass, entry)

    now = dt_util.now()
    coord._prices = _prices(now, published_hours)
    coord._weather_forecast = _weather(now, 72)
    coord._solar_radiation_forecast = [0.0] * 72

    async def _noop() -> None:
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop

    await coord._async_load_price_model()
    data = await coord._async_update_data()  # one full ordinary cycle
    horizon = coord._forecast_arrays(now)
    result = coord._optimization_result
    schedule = list(result.power_schedule) if result is not None else None
    return coord, data, np.asarray(horizon[0], dtype=float), schedule


def _run(weekday_shape, weekend_shape, published_hours):
    return asyncio.run(_cycle(weekday_shape, weekend_shape, published_hours))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--perturb",
        action="store_true",
        help="apply the finding's fix in-process: filter non-finite shape "
        "bins inside PriceShapeModel.from_dict",
    )
    args = ap.parse_args()
    t0 = time.perf_counter()

    if args.perturb:
        _orig = PriceShapeModel.from_dict.__func__

        @classmethod
        def _guarded(cls, data):
            model = _orig(cls, data)
            model.shapes = [
                [v if np.isfinite(v) else 1.0 for v in profile]
                for profile in model.shapes
            ]
            model.days = [0 if not all(np.isfinite(v) for v in p) else d
                          for p, d in zip(model.shapes, model.days)]
            return model

        PriceShapeModel.from_dict = _guarded

    # Saturday noon anchor: the 24 h horizon rides the WEEKEND profile.
    now = dt_util.now()
    while now.weekday() != 5:
        now = now + timedelta(days=1)
    now = now.replace(hour=12, minute=0, second=0, microsecond=0)
    dt_util.freeze(now)
    try:
        bad = list(LEARNED)
        bad[22] = "nan"

        _, _, p_bad, sched_bad = _run(list(LEARNED), bad, 10)
        _, _, p_ok, sched_ok = _run(list(LEARNED), list(LEARNED), 10)
        _, _, p_null, sched_null = _run(list(LEARNED), bad, 48)

        zero_bad = int(np.count_nonzero(p_bad <= 1e-12))
        zero_ok = int(np.count_nonzero(p_ok <= 1e-12))
        zero_null = int(np.count_nonzero(p_null <= 1e-12))

        diff = np.flatnonzero(np.abs(p_bad - p_ok) > 1e-9)
        window = [int(i) for i in diff]

        def _energy(schedule, steps):
            return sum(schedule[i] * 0.25 for i in steps)

        def _true_cost(schedule, prices):
            return sum(schedule[i] * float(prices[i]) * 0.25 for i in range(len(schedule)))

        energy_shift = (
            _energy(sched_bad, window) - _energy(sched_ok, window)
            if window else 0.0
        )
        cost_bad = _true_cost(sched_bad, p_ok)
        cost_ok = _true_cost(sched_ok, p_ok)
        regression = cost_bad - cost_ok
        # Null control: corrupt store, whole horizon published.
        regression_null = _true_cost(sched_null, p_ok) - cost_ok

        solved = int(sched_bad is not None and sched_ok is not None)

        print("\n=== D1-01 end-to-end: corrupt bin -> real plan ===")
        print(f"  solves returned                 {solved}/2")
        print(f"  zero-priced steps (finder metric, reproduced) {zero_bad}")
        print(f"  zero-priced steps, control      {zero_ok}")
        print(f"  zero-priced steps, null control {zero_null}")
        print(f"  affected step indexes           {window}")
        print(f"  energy in window, corrupt       "
              f"{_energy(sched_bad, window) if window else 0:.3f} kWh")
        print(f"  energy in window, control       "
              f"{_energy(sched_ok, window) if window else 0:.3f} kWh")
        print(f"  plan true cost, corrupt  @{ 'real' } prices {cost_bad:.4f} SEK")
        print(f"  plan true cost, control  @ real prices {cost_ok:.4f} SEK")
        print(f"  null-control cost regression    {regression_null:+.6f} SEK")

        print()
        print(f"RESULT solves_returned={solved} count")
        print(f"RESULT zero_priced_steps={zero_bad} count")
        print(f"RESULT control_zero_priced_steps={zero_ok} count")
        print(f"RESULT null_control_zero_priced_steps={zero_null} count")
        print(f"RESULT energy_shift_kwh={energy_shift:.4f} kWh")
        print(f"RESULT true_cost_regression_sek={regression:.4f} SEK")
        print(f"RESULT null_cost_regression_sek={regression_null:.4f} SEK")
        print(f"RESULT wall_s={time.perf_counter() - t0:.2f} wall")
        print("RESULT thread_factor=1.0000")
        try:
            print(f"RESULT load1={os.getloadavg()[0]:.2f}")
        except OSError:
            print("RESULT load1=-1")
        print("RESULT swapins=0")
    finally:
        dt_util.freeze(None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
