#!/usr/bin/env python3
"""D1-s5 (round 9, D1.M6): one off-grid timestamp in an Open-Meteo block.

Metric (one line): of the 192 quarter-hour planning steps of a 48 h horizon
that a healthy Open-Meteo response covers, the number for which production
`OpenMeteoSolar.irradiance_for` delivers None after a response whose hourly
radiation block carries ONE extra sample stamped off the hour grid.

Mechanism under test: `open_meteo._parse_block` infers the series resolution
as the SMALLEST positive gap between samples, so one stray stamp one minute
off the grid makes every sample stand for one minute; `mean_over` then
covers < 50 % of each 15-minute step and returns None for the whole horizon,
and the plan loses its solar term. Nothing is logged at WARNING: the refresh
reports success.

Count key: the delivered `irradiance_for(step)` value (None vs a number).

Arms (per cell): healthy (control: 0 expected), stray_1min, stray_5min,
stray_30min; each over five horizon starts (cells) for leave-one-out.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s5/open_meteo_resolution.py [--perturb]
  --perturb swaps `open_meteo._parse_block` for a copy that takes the MEDIAN
  positive gap instead of the minimum (one-line edit): the stray arms go to 0.

Expected (baseline): RESULT healthy_none_steps=0; stray_1min_none_steps=192;
stray_5min_none_steps=192; stray_30min_none_steps=94 (per cell, exact, all five
cells alike). --perturb: 0 in every arm.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container
(box B5, Linux x86_64), Python 3.14 venv. Counts are contention-immune.
Root rule: imports from the working directory (run from the export root).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import math
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

_p0, _t0 = time.process_time(), time.thread_time()

from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402

PERTURB = "--perturb" in sys.argv
UTC = timezone.utc
T0 = datetime(2026, 3, 10, 0, 0, tzinfo=UTC)


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


LOG = _Count()
logging.getLogger("custom_components.heatpump_optimizer").addHandler(LOG)


def _ghi(t):
    h = t.hour + t.minute / 60.0
    return round(max(0.0, 600.0 * math.sin(math.pi * (h - 6.0) / 12.0)), 1) if 6 <= h <= 18 else 0.0


def hourly_payload(stray_minutes):
    times = [T0 + timedelta(hours=i) for i in range(72)]
    rows = [(t, _ghi(t)) for t in times]
    if stray_minutes:
        # One extra sample, stamped off the grid, inside the horizon.
        s = T0 + timedelta(hours=30, minutes=stray_minutes)
        rows.append((s, _ghi(s)))
    rows.sort()
    return {
        "hourly": {
            "time": [t.strftime("%Y-%m-%dT%H:%M") for t, _ in rows],
            om._VARIABLE: [v for _, v in rows],
            om._VARIABLE_HUMIDITY: [80.0 for _ in rows],
            om._VARIABLE_SNOWFALL: [0.0 for _ in rows],
        }
    }


_orig_parse = om._parse_block


def _median_parse(block, variable, max_value=om._MAX_PLAUSIBLE_GHI):
    s = _orig_parse(block, variable, max_value)
    if not s or len(s.times) < 3:
        return s
    gaps = [(b - a).total_seconds() for a, b in zip(s.times, s.times[1:]) if b > a]
    return om.IrradianceSeries(times=s.times, values=s.values,
                               resolution=timedelta(seconds=statistics.median(gaps)))


def measure(stray_minutes, start_hour):
    payload = hourly_payload(stray_minutes)

    async def fake_get_json(self, session, url, params):
        return payload if url == om.OPEN_METEO_FORECAST_URL else None

    solar = om.OpenMeteoSolar(object(), 60.0, 18.0)
    with mock.patch.object(om, "async_get_clientsession", lambda hass: object()), \
         mock.patch.object(om.OpenMeteoSolar, "_get_json", fake_get_json):
        ok = asyncio.run(solar.async_refresh(T0, force=True))
    start = T0 + timedelta(hours=start_hour)
    none = sum(
        solar.irradiance_for(start + timedelta(minutes=15 * i), timedelta(minutes=15)) is None
        for i in range(192)
    )
    return ok, none, solar.forecast.resolution


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
    results = {}
    for arm, stray in (("healthy", 0), ("stray_1min", 1), ("stray_5min", 5), ("stray_30min", 30)):
        cells = []
        for start_hour in (1, 3, 6, 12, 18):
            LOG.n = 0
            ok, none, res = measure(stray, start_hour)
            cells.append(none)
            print(f"  {arm:12s} start+{start_hour:2d}h refresh_ok={ok} resolution={res} "
                  f"none_steps={none}/192 warnings={LOG.n}")
        results[arm] = cells
    return results


if __name__ == "__main__":
    print(f"arm: {'PERTURBED (median-gap resolution)' if PERTURB else 'baseline'}")
    if PERTURB:
        with mock.patch.object(om, "_parse_block", _median_parse):
            res = run()
    else:
        res = run()
    for arm, cells in res.items():
        loo = sorted(cells)[:-1]
        print(f"RESULT {arm}_none_steps={cells[0]} steps (of 192; cells {cells}, "
              f"range {min(cells)}-{max(cells)}, max-dropped min {min(loo)})")
    p, t = time.process_time() - _p0, time.thread_time() - _t0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
