#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s5-04: one off-grid sample in an Open-Meteo block, swept over
every minute offset, in the hourly block and in the minutely_15 block, and across irradiance
and humidity.

Metric: for each stray offset m in 1..59 min (hourly block) / 1..14 min (15-min block), the
  quarter-hour steps of a 48 h horizon (192) for which OpenMeteoSolar.irradiance_for (and
  humidity_for, hourly arm) delivers None after one async_refresh; reported as the number of
  offsets that blank >= 96 of 192 steps, the min and max over offsets, and whether the next
  refresh with a clean payload restores 0 None steps.
Controls: no stray (0 None); a missing sample (one hour dropped); a duplicate stamp.
Count key: None returned by the production accessor.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_om_stray.py
Expected (exact): see RESULT lines.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, logging, math, sys, time
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path[:0] = [".", "tests", "tests/hastub"]
p0, t0 = time.process_time(), time.thread_time()
from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402
logging.getLogger().setLevel(logging.CRITICAL)
T0 = datetime(2026, 4, 2, 0, 0, tzinfo=timezone.utc)


def ghi(t):
    h = t.hour + t.minute / 60.0
    return round(max(0.0, 500.0 * math.sin(math.pi * (h - 6) / 12)), 1) if 6 <= h <= 18 else 0.0


def block(step_min, n, stray=None, drop=None, dup=None):
    ts = [T0 + timedelta(minutes=step_min * i) for i in range(n)]
    if drop is not None:
        ts.pop(drop)
    if dup is not None:
        ts.insert(dup, ts[dup])
    if stray is not None:
        ts.append(T0 + timedelta(hours=20, minutes=stray))
    ts.sort()
    return {"time": [t.strftime("%Y-%m-%dT%H:%M") for t in ts], om._VARIABLE: [ghi(t) for t in ts],
            om._VARIABLE_HUMIDITY: [70.0] * len(ts), om._VARIABLE_SNOWFALL: [0.0] * len(ts)}


def refresh(solar, payload):
    async def fake(self, session, url, params):
        return payload if url == om.OPEN_METEO_FORECAST_URL else None
    with mock.patch.object(om, "async_get_clientsession", lambda h: object()), \
            mock.patch.object(om.OpenMeteoSolar, "_get_json", fake):
        asyncio.run(solar.async_refresh(T0, force=True))


def nones(solar, fn="irradiance_for"):
    f = getattr(solar, fn)
    return sum(f(T0 + timedelta(minutes=15 * i), timedelta(minutes=15)) is None for i in range(192))


def sweep(kind, offsets):
    res = []
    for m in offsets:
        s = om.OpenMeteoSolar(object(), 60.0, 18.0)
        if kind == "hourly":
            refresh(s, {"hourly": block(60, 72, stray=m)})
            res.append((nones(s), nones(s, "humidity_for")))
        else:
            refresh(s, {"hourly": block(60, 72), "minutely_15": block(15, 288, stray=m)})
            res.append((nones(s), None))
    return res


h = sweep("hourly", range(1, 60))
irr = [a for a, _ in h]; hum = [b for _, b in h]
print(f"RESULT hourly.offsets_blanking_ge_half_irradiance={sum(x >= 96 for x in irr)} offsets (of 59)")
print(f"RESULT hourly.irradiance_none_min={min(irr)} max={max(irr)} steps (of 192)")
print(f"RESULT hourly.offsets_blanking_ge_half_humidity={sum(x >= 96 for x in hum)} offsets (of 59)")
f = [a for a, _ in sweep("fine", range(1, 15))]
print(f"RESULT minutely15.offsets_blanking_ge_half_irradiance={sum(x >= 96 for x in f)} offsets (of 14)")
print(f"RESULT minutely15.irradiance_none_min={min(f)} max={max(f)} steps (of 192)")
for name, kw in (("clean", {}), ("missing_hour", {"drop": 30}), ("duplicate_stamp", {"dup": 30})):
    s = om.OpenMeteoSolar(object(), 60.0, 18.0)
    refresh(s, {"hourly": block(60, 72, **kw)})
    print(f"RESULT control.{name}.irradiance_none={nones(s)} steps (of 192)")
s = om.OpenMeteoSolar(object(), 60.0, 18.0)
refresh(s, {"hourly": block(60, 72, stray=1)})
a = nones(s)
refresh(s, {"hourly": block(60, 72)})
print(f"RESULT recovery.stray1_then_clean={a}->{nones(s)} steps (of 192)")
p1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
