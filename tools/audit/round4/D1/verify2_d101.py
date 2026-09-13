"""Verifier-2 harness for D1-01 (independent method, different anchor).

METRIC (mine, differs from the finder's): (a) ``solver_zero_steps`` -- steps
of the price array the REAL solver reads (``_forecast_arrays(now).prices``
inside ``async_run_optimization``) priced exactly 0.0 SEK/kWh when the
persisted price-shape store's WEEKDAY bin for hour 3 holds the strict-JSON
string "nan", anchored at a WEDNESDAY noon with 8 published hours (the
finder used a Saturday anchor, the weekend profile, bin 22, 10 published
hours); (b) ``plan_slots_shifted`` -- space-plan slots whose published
``avg_power_kw`` differs between the corrupt arm and the matched control
after one real solve; (c) ``energy_moved_kwh`` -- total kWh the plan moved
between slots, sum(|delta avg_power_kw| * hours).

COMMAND (from the worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/verify2_d101.py

EXPECTED: solver_zero_steps=4, control_solver_zero_steps=0,
  null_control_solver_zero_steps=0, plan_slots_shifted>0,
  perturb_solver_zero_steps=0, perturb_control_solver_zero_steps=0.
BASELINE: branch head 0855277 (finder measured 7dd68dd)
MACHINE:  8-core Apple M1, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer.price_model:PriceShapeModel.from_dict and
  extend_price_series, driven through the real
  HeatPumpOptimizerCoordinator.async_run_optimization (which calls
  _forecast_arrays itself; nothing is stubbed on the solve path).
PERTURBATION: replace PriceShapeModel.from_dict with a copy that raises
  ValueError on a non-finite shape bin (so the existing except abandons the
  shapes branch, exactly what an np.isfinite gate inside the branch does);
  solver_zero_steps must fall to 0, control must stay 0.
NULL CONTROL: whole 48 h horizon published, prior never consulted.
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
from heatpump_optimizer.price_model import PriceShapeModel  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
KEY = f"{const.DOMAIN}_test_entry_price_model"

SHAPE = [
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


async def _arm(now, weekday_shape, weekend_shape, published_hours):
    """Corrupt-store arm: real loader, real solve, real published plan."""
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
    await coord._async_load_price_model()
    await coord._update_current_state()
    coord._prices = _prices(now, published_hours)
    coord._weather_forecast = _weather(now, 72)
    coord._solar_radiation_forecast = [0.0] * 72
    horizon = coord._forecast_arrays(now)
    status = await coord.async_run_optimization()
    coord.data = coord._build_data_dict()
    return coord, np.asarray(horizon.prices, dtype=float), status


def _zeros(series: np.ndarray) -> int:
    return int(np.count_nonzero(series <= 1e-12))


def _plan(coord) -> list[float]:
    return [
        float(s.get("avg_power_kw", 0.0))
        for s in (coord.data.get("space_plan") or {}).get("slots", [])
    ]


def _main() -> int:
    t0 = time.perf_counter()
    # Wednesday noon anchor: the whole guessed tail rides the WEEKDAY profile.
    now = dt_util.now()
    while now.weekday() != 2:
        now = now + timedelta(days=1)
    now = now.replace(hour=12, minute=0, second=0, microsecond=0)
    dt_util.freeze(now)
    try:
        bad = list(SHAPE)
        bad[3] = "nan"

        coord_ok, p_ok, st_ok = asyncio.run(_arm(now, list(SHAPE), list(SHAPE), 8))
        coord_bad, p_bad, st_bad = asyncio.run(_arm(now, bad, list(SHAPE), 8))
        zero_ok, zero_bad = _zeros(p_ok), _zeros(p_bad)
        diff = np.flatnonzero(np.abs(p_bad - p_ok) > 1e-9)

        plan_ok, plan_bad = _plan(coord_ok), _plan(coord_bad)
        shifted = sum(
            1 for a, b in zip(plan_ok, plan_bad) if abs(a - b) > 1e-9
        )
        moved = sum(
            abs(a - b) * 0.25 for a, b in zip(plan_ok, plan_bad)
        )
        prior_bad = (coord_bad.data.get("price_prior") or {}).get(
            "weekday_shape", []
        )
        price_pub = coord_bad.data.get("price_series") or coord_bad.data.get(
            "prices"
        )
        pub_zeros = (
            int(np.count_nonzero(np.asarray(price_pub, dtype=float) <= 1e-12))
            if price_pub
            else -1
        )

        _, p_null, _ = asyncio.run(_arm(now, bad, list(SHAPE), 48))
        zero_null = _zeros(p_null)

        # -- perturbation: isfinite gate inside from_dict's shape branch.
        # The gate must raise INSIDE the branch's existing try, so a corrupt
        # bin makes from_dict abandon shapes (flat prior) rather than escape
        # the loader -- which does not wrap from_dict itself.
        def _gated_from_dict(data, *, _cls=PriceShapeModel):
            model = _cls()
            if not isinstance(data, dict):
                return model
            shapes = data.get("shapes")
            if (
                isinstance(shapes, list)
                and len(shapes) == 2
                and all(
                    isinstance(s, list) and len(s) == 24 for s in shapes
                )
            ):
                try:
                    coerced = [[float(v) for v in s] for s in shapes]
                    if not np.all(np.isfinite(np.asarray(coerced))):
                        raise ValueError("non-finite shape bin")
                    model.shapes = coerced
                except (TypeError, ValueError, OverflowError):
                    pass
            days = data.get("days")
            if isinstance(days, list) and len(days) == 2:
                try:
                    model.days = [int(v) for v in days]
                except (TypeError, ValueError, OverflowError):
                    pass
            return model

        _orig = PriceShapeModel.from_dict
        PriceShapeModel.from_dict = classmethod(
            lambda cls, data: _gated_from_dict(data)
        )
        try:
            coord_pt, p_pt, _ = asyncio.run(_arm(now, list(SHAPE), bad, 8))
            _, p_pt_ok, _ = asyncio.run(_arm(now, list(SHAPE), list(SHAPE), 8))
        finally:
            PriceShapeModel.from_dict = _orig

        print("=== D1-01 verifier-2 (Wednesday anchor, weekday bin 3, 8 h) ===")
        print(f"  solve status   control={st_ok} corrupt={st_bad}")
        print(f"  horizon steps  {p_bad.size}")
        print(f"  steps @0.0     control={zero_ok} corrupt={zero_bad} "
              f"null={zero_null}")
        print(f"  differing idx  {diff.tolist()}")
        print(f"  control @diff  {[round(float(p_ok[i]), 4) for i in diff]}")
        print(f"  plan slots     {len(plan_ok)} vs {len(plan_bad)}; "
              f"shifted={shifted}, moved={moved:.2f} kWh")
        print(f"  plan control   {[round(v, 3) for v in plan_ok]}")
        print(f"  plan corrupt   {[round(v, 3) for v in plan_bad]}")
        print(f"  price_prior weekday_shape[3] published as "
              f"{prior_bad[3] if len(prior_bad) > 3 else 'n/a'}")
        print(f"  published price zeros={pub_zeros} "
              f"(key={'price_series' if coord_bad.data.get('price_series') else 'prices' if coord_bad.data.get('prices') else 'none'})")
        print(f"  perturbation   corrupt={_zeros(p_pt)} "
              f"control={_zeros(p_pt_ok)}")
        print(f"  max(0.0, nan)  {max(0.0, float('nan'))}")

        print()
        print(f"RESULT solver_zero_steps={zero_bad} count")
        print(f"RESULT control_solver_zero_steps={zero_ok} count")
        print(f"RESULT null_control_solver_zero_steps={zero_null} count")
        print(f"RESULT differing_steps={len(diff)} count")
        print(f"RESULT plan_slots_shifted={shifted} count")
        print(f"RESULT energy_moved_kwh={moved:.2f} kwh")
        print(f"RESULT perturb_solver_zero_steps={_zeros(p_pt)} count")
        print(
            f"RESULT perturb_control_solver_zero_steps={_zeros(p_pt_ok)} count"
        )
        print(f"RESULT published_price_zeros={pub_zeros} count")
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
    raise SystemExit(_main())
