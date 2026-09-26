#!/usr/bin/env python3
"""D8 round 9, verifier V2 (independent) for D8-s1-01.

METRIC: minutes of one local day (1440, sampled at every whole minute) at which
  CurrentPriceSensor.native_value differs by > 1e-6 from the spot price of the
  entry whose interval [starts_at, next starts_at) contains now; plus the
  time-weighted mean absolute error (SEK/kWh). KEY: the value the entity
  returns; prices enter through the production ingest
  price_model.pull_prices (Tibber QUARTER_HOURLY query, fake HTTP session),
  so the entry shape is what production stores in coordinator._prices.
PRICES: hourly base = tests/profiles.py prices("winter_typical"), each hour's
  four quarters = base * (0.97, 0.99, 1.01, 1.03) (intra-hour spread +-3 %).
RUN:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v2/v2_price_minutes.py
      [--flat-quarters]  null control: every quarter of an hour priced equal
      [--hourly]         null control: Tibber answers hourly rows (hourly market)
      [--perturb]        _current_spot_price covers [start, next start)
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact): wrong_minutes=1425
  of 1440 (only 00:00-00:14 right), mean_abs_error 0.24757; hourly 0; perturb 0;
  flat-quarters 270 (NOT a null: equal quarters still publish the previous
  hour's price for 45 min after each hourly price change, 6 changes x 45).
  profiles.prices spans 24 h, so 96 entries are ingested.
MACHINE: G2-V2 cloud container, 4 CPU, CPython 3.14.0rc2, /home/claude/venv.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import argparse, asyncio, logging, sys, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import sensor, price_model  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
import profiles  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
DAY = datetime(2026, 2, 10, 0, 0, tzinfo=TZ)
SPREAD = (0.97, 0.99, 1.01, 1.03)


class _Resp:
    def __init__(self, payload): self.status, self._p = 200, payload
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def json(self): return self._p


class _Session:
    def __init__(self, quarter_rows, hourly_rows, hourly_only):
        self.q, self.h, self.hourly_only = quarter_rows, hourly_rows, hourly_only
    def post(self, url, data=None, headers=None, timeout=None):
        quarter = "QUARTER_HOURLY" in data
        rows = self.h if (not quarter or self.hourly_only) else self.q
        today = [r for r in rows if r["startsAt"] < (DAY + timedelta(days=1)).isoformat()]
        tom = [r for r in rows if r not in today]
        return _Resp({"data": {"viewer": {"homes": [{"currentSubscription": {
            "priceInfo": {"current": rows[0] if rows else None, "today": today, "tomorrow": tom}}}]}}})


def rows(flat: bool):
    base = profiles.prices("winter_typical", DAY.replace(tzinfo=None))
    per_h = int(round(1 / profiles.DT))
    vals = [float(v) for v in list(base)[::per_h]][:48]
    hourly = [{"total": round(v, 4), "startsAt": (DAY + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
              for h, v in enumerate(vals)]
    quarter = [{"total": round(v * (1.0 if flat else SPREAD[q]), 4),
                "startsAt": (DAY + timedelta(hours=h, minutes=15 * q)).isoformat(), "level": "NORMAL"}
               for h, v in enumerate(vals) for q in range(4)]
    return quarter, hourly


def covering(prices, now):
    st = [datetime.fromisoformat(p["starts_at"]) for p in prices]
    for i, s in enumerate(st):
        end = st[i + 1] if i + 1 < len(st) else s + timedelta(hours=1)
        if s <= now < end:
            return prices[i]["total"]
    raise AssertionError(now)


def perturbed(self):
    now = dt_util.now()
    st = [datetime.fromisoformat(p["starts_at"]) for p in self._prices]
    for i, s in enumerate(st):
        end = st[i + 1] if i + 1 < len(st) else s + timedelta(hours=1)
        if s <= now < end:
            return cm._raw_value(self._prices[i]) or 0.0
    return cm._raw_value(self._prices[0]) or 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat-quarters", action="store_true")
    ap.add_argument("--hourly", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    if a.perturb:
        cm.HeatPumpOptimizerCoordinator._current_spot_price = perturbed
    t0, th0 = time.process_time(), time.thread_time()
    q, h = rows(a.flat_quarters)
    cfg = {"tibber_token": "x", "weather_entity": "weather.home", "target_temperature": 21.0,
           "min_temperature": 17.0, "max_temperature": 23.0,
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
    verdict, prices = asyncio.run(price_model.pull_prices(_Session(q, h, a.hourly), cfg))
    assert verdict == "ok", prices
    hass, entry = FakeHass(), FakeEntry(data=cfg)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    coord._prices = prices
    ents: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, ents.extend))
    ent = next(e for e in ents if e._attr_translation_key == "cost_current_electricity_price")
    wrong, abs_sum = 0, 0.0
    for m in range(1440):
        now = DAY + timedelta(minutes=m)
        dt_util.freeze(now)
        coord.data = coord._build_data_dict()
        got, want = ent.native_value, covering(prices, now)
        err = abs((got if got is not None else 0.0) - want)
        abs_sum += err
        if got is None or err > 1e-6:
            wrong += 1
    dt_util.freeze(None)
    print(f"RESULT entries_ingested={len(prices)} count")
    print(f"RESULT wrong_minutes={wrong} count (of 1440)")
    print(f"RESULT mean_abs_error={abs_sum / 1440:.5f} SEK/kWh")
    cpu, thr = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
