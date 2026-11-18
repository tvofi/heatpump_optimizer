#!/usr/bin/env python3
"""D8-s1 (audit round 9), D8.M2: Current Electricity Price against quarter-hour prices.

METRIC: of the 96 quarter-hour instants of one day (each frozen 7 minutes into
  its quarter), how many publish a sensor.…_cost_current_electricity_price
  ``native_value`` that differs from the price entry whose quarter covers now.
KEY: the value the entity returns (``CurrentPriceSensor.native_value`` over the
  payload ``_build_data_dict`` builds), against the price list the coordinator
  holds -- never the entity's own attributes.
RUN:   PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/price15.py
       [--hourly]        null control: the same day at hourly resolution
       [--fix]           perturbation: _current_spot_price covers [start, next start)
       [--cycle]         also one full _async_update_data cycle, against current_action["price"]
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact): wrong_quarters=95 of 96
  (all but 00:07: the earliest entry within the last hour is published), worst 0.30; hourly 0, --fix 0; --cycle sensor-minus-plan 0.08 at 06:40.
MACHINE: B6 cloud container, 4 CPU, CPython 3.14.0rc2. Clock frozen, tz-aware
  Europe/Stockholm (HASTUB_TZ).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from replay import InProcessWorker  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import sensor  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
DAY = datetime(2026, 1, 15, 0, 0, tzinfo=TZ)
CONFIG = {"tibber_token": "x", "weather_entity": "weather.home",
          "target_temperature": 21.0, "min_temperature": 17.0,
          "max_temperature": 23.0, "indoor_temp_entity": "sensor.indoor",
          "outdoor_temp_entity": "sensor.outdoor"}


def quarter_price(q: int) -> float:
    # A real intra-hour ramp: each quarter of an hour priced differently.
    return round(0.60 + 0.02 * (q // 4) + 0.10 * (q % 4), 4)


def price_list(hourly: bool) -> list[dict]:
    if hourly:
        return [{"total": quarter_price(4 * h), "starts_at": (DAY + timedelta(hours=h)).isoformat(),
                 "level": "NORMAL"} for h in range(48)]
    return [{"total": quarter_price(q),
             "starts_at": (DAY + timedelta(minutes=15 * q)).isoformat(), "level": "NORMAL"}
            for q in range(192)]


def expected(prices: list[dict], now: datetime) -> float:
    starts = [datetime.fromisoformat(p["starts_at"]) for p in prices]
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else s + timedelta(hours=1)
        if s <= now < end:
            return prices[i]["total"]
    raise AssertionError(now)


def fixed_spot(self) -> float:
    """The perturbation: the entry covering now is [its start, the next start)."""
    now = dt_util.now()
    entries = [(datetime.fromisoformat(p["starts_at"]), p) for p in self._prices]
    for i, (s, p) in enumerate(entries):
        end = entries[i + 1][0] if i + 1 < len(entries) else s + timedelta(hours=1)
        if s <= now < end:
            return cm._raw_value(p) or 0.0
    return cm._raw_value(self._prices[0]) or 0.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hourly", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--cycle", action="store_true")
    args = ap.parse_args(argv)
    if args.fix:
        cm.HeatPumpOptimizerCoordinator._current_spot_price = fixed_spot
    t_cpu, t_thr = time.process_time(), time.thread_time()
    worker = InProcessWorker()
    cm._ensure_worker = lambda: worker
    hass = FakeHass()
    entry = FakeEntry(data=CONFIG)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    prices = price_list(args.hourly)
    coord._prices = prices
    ents: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, ents.extend))
    ent = next(e for e in ents if e._attr_translation_key == "cost_current_electricity_price")
    wrong, worst = 0, 0.0
    examples = []
    for q in range(96):
        now = DAY + timedelta(minutes=15 * q + 7)
        dt_util.freeze(now)
        coord.data = coord._build_data_dict()
        got = ent.native_value
        want = expected(prices, now)
        if got is None or abs(got - want) > 1e-6:
            wrong += 1
            worst = max(worst, abs((got or 0.0) - want))
            if len(examples) < 4:
                examples.append(f"{now:%H:%M} published={got} covering-quarter={want}")
    for ex in examples:
        print("  ", ex)
    print(f"RESULT wrong_quarters={wrong} count (of 96)")
    print(f"RESULT worst_abs_error={worst:.4f} SEK/kWh")
    if args.cycle:
        async def fetch() -> None:
            coord._prices = prices
        coord._fetch_tibber_prices = fetch

        async def forecasts(call):
            now = dt_util.now()
            return {"weather.home": {"forecast": [
                {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -4.0,
                 "wind_speed": 3.0, "precipitation": 0.0} for h in range(48)]}}
        hass.services.async_register("weather", "get_forecasts", forecasts)
        now = DAY + timedelta(hours=6, minutes=40)
        dt_util.freeze(now)
        for eid, v in (("sensor.indoor", 21.0), ("sensor.outdoor", -4.0)):
            hass.states.set(eid, FakeState(str(v), last_updated=now, unit="°C"))
        coord.data = asyncio.run(coord._async_update_data())
        print(f"   cycle 06:40: sensor={ent.native_value} current_action.price="
              f"{(coord.data.get('current_action') or {}).get('price')} covering-quarter={expected(prices, now)}")
        print(f"RESULT cycle_sensor_minus_plan={ent.native_value - coord.data['current_action']['price']:.4f} SEK/kWh")
    dt_util.freeze(None)
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    print(f"RESULT swapins={swap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
