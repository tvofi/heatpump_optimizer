#!/usr/bin/env python3
"""V3 (round 9) D1-s5-04: which of Open-Meteo's two forecast blocks one off-grid
stamp can poison, and which delivered series it erases.

Metric (one line): of 192 quarter-hour steps (48 h from T0+2 h) the number for
which production OpenMeteoSolar.irradiance_for / humidity_for DELIVER None after
one refresh, per arm:
  hourly_only_stray    - the finder's arm (hourly block only, one sample +1 min off grid)
  fine_present_hourly_stray - a full 15-minute block also present (what the API
                         serves where it has 15-min data); stray in the hourly block
  fine_stray           - healthy hourly block; stray (+1 min) in the 15-minute block
  healthy_both         - control: both blocks healthy
Command:  PYTHONPATH=. /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s5-04_blocks.py [--perturb]
  (also runs as PYTHONPATH=tests/hastub /root/venv314/bin/python ...; the parse is pure)
  --perturb: median gap instead of min in _parse_block (the finder's fix shape);
  every None count must go to 0.
Environment shim (real-HA venv only): typing.ByteString aliased to bytes.
Expected: measured, exact.  Baseline SHA 1936d5ca (evidence tree).
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import typing  # noqa: E402
if not hasattr(typing, "ByteString"):
    typing.ByteString = bytes

import asyncio  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402
import homeassistant.const as hac  # noqa: E402

PERTURB = "--perturb" in sys.argv
UTC = timezone.utc
T0 = datetime(2026, 3, 10, tzinfo=UTC)


def ghi(t):
    h = t.hour + t.minute / 60.0
    return round(max(0.0, 600.0 * math.sin(math.pi * (h - 6.0) / 12.0)), 1) if 6 <= h <= 18 else 0.0


def block(step_min, n, stray, with_side):
    ts = [T0 + timedelta(minutes=step_min * i) for i in range(n)]
    if stray:
        ts.append(T0 + timedelta(hours=30, minutes=1))
    ts.sort()
    b = {"time": [t.strftime("%Y-%m-%dT%H:%M") for t in ts], om._VARIABLE: [ghi(t) for t in ts]}
    if with_side:
        b[om._VARIABLE_HUMIDITY] = [80.0] * len(ts)
        b[om._VARIABLE_SNOWFALL] = [0.0] * len(ts)
    return b


ARMS = {
    "healthy_both": (False, True, False),
    "hourly_only_stray": (True, False, None),
    "fine_present_hourly_stray": (True, True, False),
    "fine_stray": (False, True, True),
}

if PERTURB:
    _orig = om._parse_block

    def _median(block_, variable, max_value=om._MAX_PLAUSIBLE_GHI):
        s = _orig(block_, variable, max_value)
        if not s or len(s.times) < 3:
            return s
        gaps = [(b - a).total_seconds() for a, b in zip(s.times, s.times[1:]) if b > a]
        return om.IrradianceSeries(times=s.times, values=s.values,
                                   resolution=timedelta(seconds=statistics.median(gaps)))
    om._parse_block = _median


def measure(hourly_stray, fine_present, fine_stray):
    payload = {"hourly": block(60, 72, hourly_stray, True)}
    if fine_present:
        payload["minutely_15"] = block(15, 72 * 4, fine_stray, False)

    async def fake(self, session, url, params):
        return payload if url == om.OPEN_METEO_FORECAST_URL else None

    solar = om.OpenMeteoSolar(object(), 60.0, 18.0)
    with mock.patch.object(om, "async_get_clientsession", lambda h: object()), \
         mock.patch.object(om.OpenMeteoSolar, "_get_json", fake):
        asyncio.run(solar.async_refresh(T0, force=True))
    start = T0 + timedelta(hours=2)
    q = timedelta(minutes=15)
    irr = sum(solar.irradiance_for(start + q * i, q) is None for i in range(192))
    hum = sum(solar.humidity_for(start + q * i, q) is None for i in range(192))
    return irr, hum, solar.forecast.resolution


print(f"HA {hac.__version__} perturb={PERTURB} stub={'hastub' in (om.__dict__.get('__file__') or '') or any('hastub' in p for p in sys.path)}")
for arm, spec in ARMS.items():
    irr, hum, res = measure(*spec)
    print(f"  {arm}: forecast_resolution={res}")
    print(f"RESULT {arm}_irradiance_none={irr} steps (of 192)")
    print(f"RESULT {arm}_humidity_none={hum} steps (of 192)")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
