#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s5-03: rows delivered when one row carries a JSON integer too
large for a double, with the payload arriving as JSON TEXT decoded by json.loads (aiohttp's
default ClientResponse.json decoder, which open_meteo._get_json and price_model's Tibber fetch use).

Metric: rows delivered by price_model:prices_from_tibber_payload (Tibber) and by
  open_meteo:OpenMeteoSolar.async_refresh (forecast points held) for 24 (resp. 72) valid rows plus
  one hostile row, swept over the hostile literal's digit count (308 = finite control, 309, 400,
  4000) and its position (first, middle, last); a raise counts as 0.
Count key: rows the production parser delivers.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_huge_int.py
Expected (exact): digits 308 (finite control) -> tibber 25 (the 1e308 row itself is kept), open_meteo 72;
  digits 309/400/4000 -> 0 in every position; string '1e999' control -> 24.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, sys, time
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path[:0] = [".", "tests", "tests/hastub"]
p0, t0 = time.process_time(), time.thread_time()
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402
from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402


def tibber_text(lit, pos):
    rows = [f'{{"total": {0.5 + 0.02 * h:.2f}, "startsAt": "2026-01-15T{h:02d}:00:00+01:00", "level": "NORMAL"}}'
            for h in range(24)]
    hostile = f'{{"total": {lit}, "startsAt": "2026-01-16T{pos:02d}:30:00+01:00", "level": "NORMAL"}}'
    rows.insert({"first": 0, "middle": 12, "last": 24}[pos_name[pos]], hostile)
    return '{"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": [' + ",".join(rows) + ']}}}]}}}'


pos_name = {0: "first", 1: "middle", 2: "last"}


def tibber_rows(lit, pos):
    try:
        data = json.loads(tibber_text(lit, pos))
    except ValueError as e:
        return f"json_reject({type(e).__name__})"
    try:
        out = pm.prices_from_tibber_payload(data)
    except Exception:  # noqa: BLE001
        return 0
    return len(out) if isinstance(out, list) else 0


def om_points(lit, pos):
    t_0 = datetime(2026, 3, 10, tzinfo=timezone.utc)
    times = [(t_0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(73)]
    vals = ["100.0"] * 72
    vals.insert({0: 0, 1: 36, 2: 72}[pos], lit)
    text = '{"hourly": {"time": ' + json.dumps(times) + ', "' + om._VARIABLE + '": [' + ",".join(vals) + ']}}'
    try:
        payload = json.loads(text)
    except ValueError as e:
        return f"json_reject({type(e).__name__})"

    async def fake(self, session, url, params):
        return payload if url == om.OPEN_METEO_FORECAST_URL else None
    solar = om.OpenMeteoSolar(object(), 60.0, 18.0)
    with mock.patch.object(om, "async_get_clientsession", lambda h: object()), \
            mock.patch.object(om.OpenMeteoSolar, "_get_json", fake):
        try:
            asyncio.run(solar.async_refresh(t_0, force=True))
        except Exception:  # noqa: BLE001
            return 0
    return len(solar.forecast.times)


for digits in (308, 309, 400, 4000):
    lit = "1" + "0" * digits
    for pos in (0, 1, 2):
        print(f"RESULT tibber.digits{digits}.{pos_name[pos]}={tibber_rows(lit, pos)} rows (of 24 valid)")
        print(f"RESULT open_meteo.digits{digits}.{pos_name[pos]}={om_points(lit, pos)} points (of 72 valid)")
for pos in (0, 1, 2):
    print(f"RESULT tibber.control_1e999str.{pos_name[pos]}={tibber_rows(chr(34) + '1e999' + chr(34), pos)} rows (of 24 valid)")
p1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
