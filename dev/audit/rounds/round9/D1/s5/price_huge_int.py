#!/usr/bin/env python3
"""D1-s5 (round 9, D1.M6): one huge-integer price row fails the whole fetch.

Metric (one line): price rows delivered by production `price_model.pull_prices`
(entity source) and `price_model.prices_from_tibber_payload` for a day of 24
valid rows plus ONE row whose value is a JSON integer too large for a float;
a raise delivers 0 rows.

Mechanism: `price_model._raw_value` catches (TypeError, ValueError) around
`float(raw)`; `float(10**400)` raises OverflowError, which escapes, so the
#1090/#1297 drop-the-row rule the parser applies to every other malformed
value (None, "abc", "nan", "1e999", nested objects) becomes drop-the-FETCH.
Its sibling `tariff._stored_peaks` already catches exactly this
(`except OverflowError:  # a huge JSON int`). The attribute persists on the
entity, so every following cycle fails the same way.

Count key: len() of the delivered row list (0 when the call raises).

Arms: control (the hostile row is the string "1e999", which float() turns
into inf and the parser drops) and huge_int.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s5/price_huge_int.py [--perturb]
  --perturb adds OverflowError to _raw_value's except tuple in memory (one-line
  edit): huge_int rows rise from 0 to 24 on both seams.

Expected (baseline): RESULT entity_control_rows=24, entity_huge_int_rows=0,
tibber_control_rows=24, tibber_huge_int_rows=0, open_meteo_control_rows=72,
open_meteo_huge_int_rows=0 (exact). --perturb: 24, 24, 24, 24, 72, 72.
The open_meteo seam: `_parse_block`'s float() has the same except tuple; its
OverflowError is caught one level up by the #1519 fence, which drops the whole
refresh's series (72 good samples) instead of the one row.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container
(box B5, Linux x86_64), Python 3.14 venv. Counts are contention-immune.
Root rule: imports from the working directory (run from the export root).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import math
import sys
import time
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

_p0, _t0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402

from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402
from custom_components.heatpump_optimizer.const import (  # noqa: E402
    CONF_PRICE_ENTITY, CONF_PRICE_SOURCE, PRICE_SOURCE_ENTITY,
)

PERTURB = "--perturb" in sys.argv
HUGE = 10 ** 400


def _rows(hostile):
    rows = [{"start": f"2026-01-15T{h:02d}:00:00+01:00", "value": 0.5 + 0.02 * h} for h in range(24)]
    rows.append({"start": "2026-01-16T00:00:00+01:00", "value": hostile})
    return rows


def entity_rows(hostile):
    state = SimpleNamespace(state="0.61", attributes={"raw_today": _rows(hostile),
                                                     "unit_of_measurement": "SEK/kWh"})
    cfg = {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY, CONF_PRICE_ENTITY: "sensor.nordpool"}
    try:
        verdict, payload = asyncio.run(pm.pull_prices(None, cfg, state))
    except Exception as err:  # noqa: BLE001 - the raise is the measurement
        print(f"  entity  hostile={type(hostile).__name__:3s}: raised {type(err).__name__}")
        return 0
    n = len(payload) if verdict == "ok" else 0
    print(f"  entity  hostile={type(hostile).__name__:3s}: verdict={verdict} rows={n}")
    return n


def tibber_rows(hostile):
    today = [{"total": r["value"], "startsAt": r["start"], "level": "NORMAL"} for r in _rows(hostile)]
    payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": today}}}]}}}
    try:
        out = pm.prices_from_tibber_payload(payload)
    except Exception as err:  # noqa: BLE001
        print(f"  tibber  hostile={type(hostile).__name__:3s}: raised {type(err).__name__}")
        return 0
    n = len(out) if isinstance(out, list) else 0
    print(f"  tibber  hostile={type(hostile).__name__:3s}: rows={n}")
    return n


def open_meteo_points(hostile):
    """Forecast points held after one refresh whose hourly block has 72 valid
    samples and one hostile one (open_meteo._parse_block's float() site)."""
    from datetime import datetime, timedelta, timezone
    from custom_components.heatpump_optimizer import open_meteo as om
    t0 = datetime(2026, 3, 10, tzinfo=timezone.utc)
    times = [(t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(73)]
    vals = [100.0] * 72 + [hostile]
    payload = {"hourly": {"time": times, om._VARIABLE: vals}}

    async def fake(self, session, url, params):
        return payload if url == om.OPEN_METEO_FORECAST_URL else None

    solar = om.OpenMeteoSolar(object(), 60.0, 18.0)
    patches = [mock.patch.object(om, "async_get_clientsession", lambda h: object()),
               mock.patch.object(om.OpenMeteoSolar, "_get_json", fake)]
    if PERTURB:
        patches.append(mock.patch.object(om, "float", _safe_float, create=True))
    for pt in patches:
        pt.start()
    try:
        asyncio.run(solar.async_refresh(t0, force=True))
    finally:
        for pt in patches:
            pt.stop()
    n = len(solar.forecast.times)
    print(f"  openmeteo hostile={type(hostile).__name__:3s}: forecast_points={n}")
    return n


def _safe_float(x=0.0):
    """float() that turns OverflowError into ValueError: the one-line edit
    `except (TypeError, ValueError, OverflowError)` at _parse_block's site."""
    try:
        return float(x)
    except OverflowError as err:
        raise ValueError(str(err)) from None


def _fixed_raw_value(item):
    raw = item.get("value")
    if raw is None:
        raw = item.get("total")
    if raw is None:
        raw = item.get("price")
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if np.isfinite(value) else None


def _swapins():
    try:
        with open("/proc/vmstat") as f:
            for line in f:
                if line.startswith("pswpin"):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


def run():
    return {
        "entity_control": entity_rows("1e999"),
        "entity_huge_int": entity_rows(HUGE),
        "tibber_control": tibber_rows("1e999"),
        "tibber_huge_int": tibber_rows(HUGE),
        "open_meteo_control": open_meteo_points("1e999"),
        "open_meteo_huge_int": open_meteo_points(HUGE),
    }


if __name__ == "__main__":
    print(f"arm: {'PERTURBED (_raw_value catches OverflowError)' if PERTURB else 'baseline'}")
    if PERTURB:
        with mock.patch.object(pm, "_raw_value", _fixed_raw_value):
            res = run()
    else:
        res = run()
    for k, v in res.items():
        print(f"RESULT {k}_rows={v} rows (valid in payload: 24 price rows, 72 open_meteo samples)")
    p, t = time.process_time() - _p0, time.thread_time() - _t0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
