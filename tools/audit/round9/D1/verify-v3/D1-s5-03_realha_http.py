#!/usr/bin/env python3
"""V3 (round 9) D1-s5-03 reach on REAL Home Assistant: the huge JSON integer
(10**400) delivered the way each source really delivers it.
  tibber / open_meteo - a local aiohttp server returns the payload as JSON TEXT;
    production pull_prices / OpenMeteoSolar.async_refresh fetch it through the
    genuine homeassistant.helpers.aiohttp_client.async_get_clientsession (whose
    HassClientResponse.json decodes with HA's orjson json_loads).
  entity - the rows are an attribute of a state set on the genuine StateMachine,
    read by production pull_prices (entity source).
Metric (one line): price rows / forecast points delivered for 24 (72) valid rows
plus one hostile row; a raise counts 0.  Arms: control (hostile = "1e999"),
huge_int (hostile = 10**400), each under baseline and --perturb.
Command:  PYTHONPATH=. /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s5-03_realha_http.py [--perturb]
  --perturb: the finder's fix (OverflowError caught at _raw_value and _parse_block's
  float); on a seam where the fix changes nothing in real HA the huge_int count stays 0.
Environment shims: the DNS resolver is aiohttp's ThreadedResolver (no\nnetwork integration here); typing.ByteString aliased to bytes before importing HA (CPython
3.14.0rc2 removed it; mashumaro in HA 2026.2.3 needs it). Not a product change.
Expected: measured, exact.  Baseline SHA 1936d5ca (evidence tree).  HA 2026.2.3.
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
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from aiohttp import web  # noqa: E402
from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers.aiohttp_client import async_get_clientsession  # noqa: E402
import homeassistant.const as hac  # noqa: E402
from custom_components.heatpump_optimizer import open_meteo as om  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402
from custom_components.heatpump_optimizer.const import (  # noqa: E402
    CONF_PRICE_ENTITY, CONF_PRICE_SOURCE, CONF_TIBBER_TOKEN, PRICE_SOURCE_ENTITY,
    PRICE_SOURCE_TIBBER,
)

import aiohttp  # noqa: E402
import homeassistant.helpers.aiohttp_client as hac_client  # noqa: E402
# Environment shim: the zeroconf DNS resolver needs the network integration set
# up; the resolver does not touch response decoding (HassClientResponse.json).
class _Resolver(aiohttp.ThreadedResolver):
    async def real_close(self):
        await self.close()


hac_client._async_make_resolver = lambda hass: _Resolver()

assert "tests/hastub" not in " ".join(sys.path)
spec = importlib.util.spec_from_file_location("phi", "tools/audit/round9/D1/s5/price_huge_int.py")
PHI = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PHI)  # __main__-guarded: only its builders and fix shapes
PERTURB = "--perturb" in sys.argv
HUGE_TEXT = "1" + "0" * 400
BODY = {}


def _rows(hostile_token):
    rows = [{"start": f"2026-01-15T{h:02d}:00:00+01:00", "value": 0.5 + 0.02 * h} for h in range(24)]
    rows.append({"start": "2026-01-16T00:00:00+01:00", "value": hostile_token})
    return rows


def _text(obj):
    return json.dumps(obj).replace('"__HUGE__"', HUGE_TEXT)


def tibber_text(hostile):
    today = [{"total": r["value"], "startsAt": r["start"], "level": "NORMAL"} for r in _rows(hostile)]
    return _text({"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": today}}}]}}})


def om_text(hostile):
    t0 = datetime(2026, 3, 10, tzinfo=timezone.utc)
    times = [(t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(73)]
    return _text({"hourly": {"time": times, om._VARIABLE: [100.0] * 72 + [hostile]}})


async def handler(request):
    return web.Response(text=BODY["text"], content_type="application/json")


async def main():
    hass = HomeAssistant(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    url = f"http://127.0.0.1:{port}/x"
    session = async_get_clientsession(hass)
    res = {}
    for arm, hostile in (("control", "1e999"), ("huge_int", "__HUGE__")):
        # tibber
        BODY["text"] = tibber_text(hostile)
        try:
            with mock.patch.object(pm, "TIBBER_API_URL", url):
                verdict, payload = await pm.pull_prices(session, {CONF_PRICE_SOURCE: PRICE_SOURCE_TIBBER,
                                                                   CONF_TIBBER_TOKEN: "t"})
            res[f"tibber_{arm}"] = (len(payload) if verdict == "ok" else 0, verdict)
        except Exception as err:  # noqa: BLE001
            res[f"tibber_{arm}"] = (0, f"raised {type(err).__name__}")
        # open-meteo
        BODY["text"] = om_text(hostile)
        solar = om.OpenMeteoSolar(hass, 60.0, 18.0)
        with mock.patch.object(om, "OPEN_METEO_FORECAST_URL", url), \
             mock.patch.object(om, "OPEN_METEO_SATELLITE_URL", url + "sat"):
            await solar.async_refresh(datetime(2026, 3, 10, tzinfo=timezone.utc), force=True)
        res[f"open_meteo_{arm}"] = (len(solar.forecast.times), "")
        # entity
        val = 10 ** 400 if hostile == "__HUGE__" else hostile
        hass.states.async_set("sensor.nordpool", "0.61",
                              {"raw_today": _rows(val), "unit_of_measurement": "SEK/kWh"})
        try:
            verdict, payload = await pm.pull_prices(None, {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY,
                                                           CONF_PRICE_ENTITY: "sensor.nordpool"},
                                                    hass.states.get("sensor.nordpool"))
            res[f"entity_{arm}"] = (len(payload) if verdict == "ok" else 0, verdict)
        except Exception as err:  # noqa: BLE001
            res[f"entity_{arm}"] = (0, f"raised {type(err).__name__}")
    await runner.cleanup()
    await hass.async_stop(force=True)
    return res


patches = []
if PERTURB:
    patches = [mock.patch.object(pm, "_raw_value", PHI._fixed_raw_value),
               mock.patch.object(om, "float", PHI._safe_float, create=True)]
for p in patches:
    p.start()
try:
    out = asyncio.run(main())
finally:
    for p in patches:
        p.stop()
print(f"HA {hac.__version__} perturb={PERTURB}")
for k, (n, note) in out.items():
    print(f"  {k}: {n} {note}")
    print(f"RESULT realha_{k}_rows={n} rows")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
