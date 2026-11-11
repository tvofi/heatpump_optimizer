#!/usr/bin/env python3
"""R10-ADVISOR-STEADY-START (#2257): the schedule figure's magnitude bracket.

WHY IT EXISTS. A schedule ask's steady figure is a thermostat's day-energy
difference at the horizon's mean price (``price_tiles.schedule_figure``). Its
sign is checked elsewhere (r10_advisor_steady_carrier.py, tests/features.py);
its size has no reference, because the optimiser buys the same energy at
cheaper hours than the mean. This harness prices the same energy difference
two more ways and prints how far the mean-price figure sits from each:

  realised: the what-if solve's own average purchase price, its spend over its
            energy (the one solve the ask already ran);
  minimum:  the lowest price of the horizon.

The ratio mean / realised is why the answer carries the realised pricing too
(``price_tiles.SHIFTED_KEY``) and the card shows the two as a range; the
``range`` line counts the answers whose two figures round apart, and checks
the answer's second figure against this harness's own realised pricing.

Run from the tree root:

  [PRICES=<series>] [OUTDOOR=<series>] PYTHONPATH=tests/hastub:tests:custom_components \
      python3 dev/audit/harnesses/r10_advisor_steady_bracket.py [out.json]

PRICES: sawtooth (default; the fixture's 12 h sawtooth 0.60 to 1.06), flat (the
null: every hour at the sawtooth's mean), spread2 (the perturbation: each
price twice as far from the mean), peaks (a SYNTHETIC high-spread day, the
hourly shape of tests/golden/extreme_prices.json, 0.9 to 7.4; no recorded
price day is in the tree).
OUTDOOR: flat (default, -5) or diurnal (-5 + 4 sin, coldest at 03:00).

Fixture: ``_solve_coord`` of tests/features.py, hours 01..23 step 2, the what-if
asked at the solve's instant: the two tile degrees and the six panel asks, 96
schedule figures. The last line times ``reference_day``, the only work the
schedule branch adds to a what-if (item pass-wall of the design).
"""
from __future__ import annotations

import ast
import asyncio as _asyncio
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta  # noqa: F401 - the sliced fixture reads them
from pathlib import Path

import numpy as np
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeState, with_config  # noqa: F401
from homeassistant.util import dt as dt_util

import heatpump_optimizer.coordinator as cmod
import heatpump_optimizer.optimizer as omod
from heatpump_optimizer import price_tiles, whatif
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: F401

PRICES = os.environ.get("PRICES", "sawtooth")
OUTDOOR = os.environ.get("OUTDOOR", "flat")
OUT = sys.argv[1] if len(sys.argv) > 1 else None
assert PRICES in ("sawtooth", "flat", "spread2", "peaks"), PRICES
assert OUTDOOR in ("flat", "diurnal"), OUTDOOR

_want = {"_SolveHass", "_solve_coord", "_solve_record_now"}
_ns = globals()
for node in ast.parse(Path("tests/features.py").read_text()).body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in _want:
        exec(compile(ast.Module([node], []), "features-slice", "exec"), _ns)  # noqa: S102
        _want.discard(node.name)
assert not _want, _want


async def _no_worker(hass, fn, *args):
    return fn(*args)


cmod._await_process = _no_worker

_seen: dict = {}
_real_optimize = cmod._await_optimize
_real_figure = price_tiles.schedule_figure


async def _optimize(hass, optimizer, inputs):
    result = await _real_optimize(hass, optimizer, inputs)
    _seen["solve"] = (result, inputs, optimizer.config.dt_hours)
    return result


def _figure(live_kwh, sim_kwh, mean_price, extra, horizon_hours, *more):
    _seen["figure"] = (live_kwh, sim_kwh, mean_price)
    return _real_figure(live_kwh, sim_kwh, mean_price, extra, horizon_hours, *more)


_WALL: list[float] = []
_real_reference = omod.HeatPumpOptimizer.reference_day


def _reference(self, inputs):
    start = time.perf_counter()
    try:
        return _real_reference(self, inputs)
    finally:
        _WALL.append(time.perf_counter() - start)


omod.HeatPumpOptimizer.reference_day = _reference
cmod._await_optimize = _optimize
price_tiles.schedule_figure = _figure

WANT = {
    "target_minus_1": -1, "target_plus_1": 1, "panel_comfort_plus_half": 1, "panel_comfort_minus_half": -1,
    "panel_daystart_earlier": 1, "panel_daystart_later": -1, "panel_dayend_later": 1, "panel_dayend_earlier": -1,
}
#: tests/golden/extreme_prices.json's prices, one per hour.
_PEAKS = (0.9, 0.9, 0.9, 0.9, 0.9, 1.8, 1.8, 4.8, 4.8, 4.8, 1.8, 1.8,
          1.8, 1.8, 1.8, 1.8, 7.4, 7.4, 7.4, 7.4, 1.8, 1.8, 1.2, 1.2)


def _reprice(coord):
    totals = [float(row["total"]) for row in coord._prices]
    mean = sum(totals) / len(totals)
    for row, total in zip(coord._prices, totals):
        if PRICES == "flat":
            row["total"] = round(mean, 4)
        elif PRICES == "spread2":
            row["total"] = round(mean + 2.0 * (total - mean), 4)
        elif PRICES == "peaks":
            row["total"] = _PEAKS[dt_util.parse_datetime(row["starts_at"]).hour]
    if OUTDOOR == "diurnal":
        for row in coord._weather_forecast:
            hour = dt_util.parse_datetime(row["datetime"]).hour
            row["temperature"] = -5.0 + 4.0 * math.sin(2.0 * math.pi * (hour - 9) / 24.0)


async def _one(hour):
    coord = _solve_coord()  # noqa: F821
    _reprice(coord)
    coord._fuse_advisor_at = dt_util.now()
    await coord.async_run_optimization()
    record = _solve_record_now(coord)  # noqa: F821
    c = record.config
    day = c.comfort_temp_day if c.comfort_temp_day is not None else c.target_temp
    asks = list(price_tiles.specs(c, record.params.max_electrical_power))[:2] + [
        ("panel_comfort_plus_half", {"target_temp": c.target_temp + 0.5, "comfort_temp_day": day + 0.5}),
        ("panel_comfort_minus_half", {"target_temp": c.target_temp - 0.5, "comfort_temp_day": day - 0.5}),
        ("panel_daystart_earlier", {"day_start_hour": c.day_start_hour - 1}),
        ("panel_daystart_later", {"day_start_hour": c.day_start_hour + 1}),
        ("panel_dayend_later", {"day_end_hour": c.day_end_hour + 1}),
        ("panel_dayend_earlier", {"day_end_hour": c.day_end_hour - 1}),
    ]
    rows = []
    for name, overrides in asks:
        whatif.state_for(coord).last_at = None
        _seen.clear()
        answer = await coord.async_simulate(dict(overrides), steady=True)
        if "figure" not in _seen or answer.get(whatif.STEADY_KEY) is None:
            rows.append({"hour": hour, "ask": name, "error": answer.get("error") or "no schedule figure"})
            continue
        live_kwh, sim_kwh, mean_price = _seen["figure"]
        result, inputs, dt = _seen["solve"]
        prices = np.asarray(inputs.forecast.prices, dtype=float)
        energy = (float(np.sum(result.power_schedule)) + float(np.sum(result.dhw_power_schedule or []))) * dt
        realised = float(result.predicted_cost) / energy if energy > 0.0 else math.nan
        d_kwh = sim_kwh - live_kwh
        month = lambda price: price_tiles.per_month(d_kwh * price, 24.0)  # noqa: E731
        rows.append({
            "hour": hour, "ask": name, "built": answer[whatif.STEADY_KEY], "d_kwh": d_kwh,
            "mean_price": mean_price, "realised_price": realised, "min_price": float(prices.min()),
            "spread": float(prices.max() - prices.min()),
            "fig_mean": month(mean_price), "fig_realised": month(realised), "fig_min": month(float(prices.min())),
            "shifted": answer.get(price_tiles.SHIFTED_KEY),
        })
    return rows


def main():
    allrows = []
    for hour in range(1, 24, 2):
        dt_util.freeze(dt_util.now().replace(hour=hour, minute=7, second=0, microsecond=0))
        try:
            allrows += _asyncio.run(_one(hour))
        finally:
            dt_util.freeze(None)
    ok = [r for r in allrows if "error" not in r]
    tag = f"prices {PRICES} outdoor {OUTDOOR}"
    if ok:
        rr = [r["mean_price"] / r["realised_price"] for r in ok]
        rm = [r["mean_price"] / r["min_price"] for r in ok]
        agree = sum(1 for r in ok if max(r["fig_mean"], r["fig_realised"], r["fig_min"])
                    - min(r["fig_mean"], r["fig_realised"], r["fig_min"]) <= 0.2)
        print(f"RESULT {tag}: schedule figures {len(ok)} against the ask "
              f"{sum(1 for r in ok if r['built'] * WANT[r['ask']] <= 0.0)}; the answer's figure is the "
              f"mean-price pricing within 0.01 on {sum(1 for r in ok if abs(r['built'] - r['fig_mean']) <= 0.01)}")
        print(f"RESULT {tag}: ratio mean-price / realised-price {min(rr):.3f}..{max(rr):.3f} "
              f"(median {float(np.median(rr)):.3f}), above 1.5 on {sum(1 for x in rr if x > 1.5)} of {len(rr)}")
        print(f"RESULT {tag}: ratio mean-price / minimum-price {min(rm):.3f}..{max(rm):.3f}; "
              f"price spread {min(r['spread'] for r in ok):.2f}..{max(r['spread'] for r in ok):.2f}")
        print(f"RESULT {tag}: the three pricings within 0.2 a month on {agree} of {len(ok)}")
        print(f"RESULT {tag}: range: the answer's second figure is the realised pricing within 0.01 on "
              f"{sum(1 for r in ok if r['shifted'] is not None and abs(r['shifted'] - r['fig_realised']) <= 0.01)}"
              f" of {len(ok)}; the two round apart (the card shows a range) on "
              f"{sum(1 for r in ok if r['shifted'] is not None and round(abs(r['shifted'])) != round(abs(r['built'])))}")
    if _WALL:
        print(f"RESULT {tag}: reference_day calls {len(_WALL)} (two per what-if, on the event loop), "
              f"wall each median {1000.0 * float(np.median(_WALL)):.1f} ms max {1000.0 * max(_WALL):.1f} ms on this host")
    print("ERRORS", len(allrows) - len(ok), [(r["hour"], r["ask"], r["error"]) for r in allrows if "error" in r][:5])
    if OUT:
        Path(OUT).write_text(json.dumps(allrows))


main()
