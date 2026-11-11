"""A corrupt bin in the persisted price shape prices a planning hour at 0.

METRIC: number of planning steps whose price is exactly 0.0 SEK/kWh after
loading a price-shape store whose one hourly bin holds the JSON string
"nan" (strictly valid JSON, so it survives Home Assistant's orjson
round-trip), with the matched control being the identical store carrying a
finite value in that bin.

MECHANISM: price_model.py:PriceShapeModel.from_dict coerces each shape bin
with ``float(v)`` inside a ``try/except (TypeError, ValueError,
OverflowError)`` and checks no finiteness -- while
``PriceShapeModel.observe_day``, the WRITER of the same field, rejects a
non-finite day at line 137. NaN then reaches
``price_model.py:extend_price_series``'s ``prices.append(max(0.0,
model.predict(when, level)))``, and ``max(0.0, nan)`` is 0.0 in CPython, so
the guessed tail is priced as free electricity instead of failing loudly.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/price_prior_zero.py

EXPECTED: RESULT zero_priced_steps=4 (exact), RESULT control_zero_priced_steps=0
  (exact), RESULT bins_reaching_zero=14 of 24 (exact), RESULT
  null_control_zero_priced_steps=0 (exact).
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer.price_model:PriceShapeModel.from_dict and
  heatpump_optimizer.price_model:extend_price_series, driven through
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  ._async_load_price_model and ._forecast_arrays.
PERTURBATION: add ``if not np.all(np.isfinite(model.shapes)): raise
  ValueError`` (or an ``np.isfinite`` filter) inside
  ``PriceShapeModel.from_dict``'s shape branch; zero_priced_steps must fall
  to 0 while control_zero_priced_steps stays 0.
NULL CONTROL: the same corrupt store with the WHOLE horizon published, so
  ``extend_price_series`` never consults the prior. The effect must vanish.
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

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
KEY = f"{const.DOMAIN}_test_entry_price_model"

#: A plausible learned diurnal shape: night trough, morning and evening peaks.
LEARNED = [
    0.70, 0.65, 0.62, 0.60, 0.62, 0.75, 1.00, 1.35,
    1.40, 1.20, 1.05, 1.00, 0.98, 0.95, 0.95, 1.00,
    1.15, 1.35, 1.30, 1.15, 1.00, 0.90, 0.82, 0.75,
]


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


def _arm(now, weekday_shape, weekend_shape, published_hours):
    """Load a price-shape store, then read the planning price series."""
    hastore._reset_store_disk()
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = "test_entry"
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    hastore._DISK[KEY] = json.dumps(
        {
            "model": {
                "shapes": [weekday_shape, weekend_shape],
                "days": [30, 30],
            },
            "days_seen": [],
            "quarter_days_seen": [],
        }
    )

    async def go():
        await coord._async_load_price_model()
        await coord._update_current_state()
        coord._prices = _prices(now, published_hours)
        coord._weather_forecast = _weather(now, 72)
        coord._solar_radiation_forecast = [0.0] * 72
        return coord._forecast_arrays(now)

    arrays = asyncio.run(go())
    return coord, np.asarray(arrays[0], dtype=float), np.asarray(
        arrays[5], dtype=bool
    )


def _zero_steps(series) -> int:
    return int(np.count_nonzero(series <= 1e-12))


def main() -> int:
    t0 = time.perf_counter()
    # A Saturday noon anchor, so the horizon runs through the WEEKEND profile
    # first -- ``_profile_index`` picks the profile per step, and corrupting
    # the profile the horizon never visits proves nothing.
    now = dt_util.now()
    while now.weekday() != 5:
        now = now + timedelta(days=1)
    now = now.replace(hour=12, minute=0, second=0, microsecond=0)
    dt_util.freeze(now)
    try:
        # -- headline: one corrupt bin, 10 h of published prices ------------
        bad = list(LEARNED)
        bad[22] = "nan"
        coord_bad, p_bad, known_bad = _arm(now, list(LEARNED), bad, 10)
        coord_ok, p_ok, known_ok = _arm(now, list(LEARNED), list(LEARNED), 10)
        zero_bad = _zero_steps(p_bad)
        zero_ok = _zero_steps(p_ok)
        diff = np.flatnonzero(np.abs(p_bad - p_ok) > 1e-9)

        # -- null control: the whole horizon published, prior unused --------
        _, p_null, known_null = _arm(now, list(LEARNED), bad, 48)
        zero_null = _zero_steps(p_null)

        # -- leave-one-out over the 24 hourly bins -------------------------
        per_bin = []
        for hour in range(24):
            shape = list(LEARNED)
            shape[hour] = "nan"
            _, series, _ = _arm(now, list(LEARNED), shape, 10)
            per_bin.append((hour, _zero_steps(series)))
        reaching = [h for h, n in per_bin if n > 0]
        counts = [n for _, n in per_bin if n > 0]

        print("\n=== one corrupt bin in the persisted price shape ===")
        print(f"  horizon steps            {p_bad.size}")
        print(f"  steps from published     {int(known_bad.sum())}")
        print(f"  control  min price       {float(p_ok.min()):.4f} SEK/kWh")
        print(f"  corrupt  min price       {float(p_bad.min()):.4f} SEK/kWh")
        print(f"  steps differing          {diff.tolist()}")
        print(
            f"  control @ those steps    "
            f"{[round(float(p_ok[i]), 4) for i in diff[:8]]}"
        )
        print(
            f"  corrupt @ those steps    "
            f"{[round(float(p_bad[i]), 4) for i in diff[:8]]}"
        )
        print(
            f"  published shape bin      "
            f"{coord_bad._price_model.summary().get('weekend_shape', [])[22]}"
        )
        print(f"\n  bins reaching zero       {reaching}")
        print(f"  zero steps per such bin  min={min(counts, default=0)} "
              f"max={max(counts, default=0)}")
        print(
            f"  null control (all 48 h published, prior unused): "
            f"{zero_null} zero-priced steps, "
            f"{int(known_null.sum())} of {p_null.size} steps known"
        )

        print()
        print(f"RESULT zero_priced_steps={zero_bad} count")
        print(f"RESULT control_zero_priced_steps={zero_ok} count")
        print(f"RESULT null_control_zero_priced_steps={zero_null} count")
        print(f"RESULT bins_reaching_zero={len(reaching)} count")
        print(f"RESULT bins_tested={len(per_bin)} count")
        print(
            f"RESULT zero_steps_per_bin_min={min(counts, default=0)} count"
        )
        print(
            f"RESULT zero_steps_per_bin_max={max(counts, default=0)} count"
        )
        print(
            f"RESULT zero_steps_drop_most_favourable="
            f"{sum(counts) - max(counts, default=0)} count"
        )
        print(f"RESULT differing_steps={len(diff)} count")
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
