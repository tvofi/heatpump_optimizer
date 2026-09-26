"""V2 (independent) harness for D1-s2-01.

Metric (one line): of the finder's 200 seeded get_forecasts payloads (seed 9),
the count after which 3 further cycles with a healthy forecast ALL still raise
(wedge), in two arms: `raw` serves the payload verbatim (what tests/hastub
allows), `ha` serves what Home Assistant 2026.2.3's weather.get_forecasts can
return: {"forecast": [dict(row) for row in native]} with native None -> [],
and a service exception when dict(row) or iteration raises (source:
homeassistant/components/weather/__init__.py async_get_forecasts_service and
WeatherEntity._convert_forecast, line `forecast_entry = dict(_forecast_entry)`).
Count key: exceptions out of production _async_update_data.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_forecast_ha.py
Expected: raw_wedged=35 (+-0), ha_wedged=0 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, copy, random, sys, time, logging
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D1/s2")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
from harness import FakeEntry, FakeHass  # noqa
from heatpump_optimizer import coordinator as cm  # noqa
import parsers as fp  # finder's generator, reused for identical payloads  # noqa
from lifecycle import _states  # noqa


class ServiceError(Exception):
    pass


def ha_filter(payload):
    """What the real weather.get_forecasts service can hand back."""
    native = None
    if isinstance(payload, dict) and isinstance(payload.get("weather.home"), dict):
        native = payload["weather.home"].get("forecast")
    if native is None:
        return {"weather.home": {"forecast": []}}
    try:
        return {"weather.home": {"forecast": [dict(e) for e in native]}}
    except Exception as err:  # noqa: BLE001 -- HA raises out of the service call
        raise ServiceError(str(err))


def run(arm, n=200, seed=9):
    rng = random.Random(f"{seed}:weather")
    wedged = raised1 = 0
    for i in range(n):
        payload, kind = fp.hostile(rng)
        hass = FakeHass(_states())
        st = {"p": payload}

        async def handler(call):
            return ha_filter(st["p"]) if arm == "ha" else st["p"]
        hass.services.async_register("weather", "get_forecasts", handler)
        c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(fp.CFG)))
        try:
            asyncio.run(c._async_update_data())
        except Exception:  # noqa: BLE001
            raised1 += 1
        st["p"] = {"weather.home": {"forecast": fp.healthy_forecast()}}
        fails = 0
        for _ in range(3):
            try:
                asyncio.run(c._async_update_data())
            except Exception:  # noqa: BLE001
                fails += 1
        if fails == 3:
            wedged += 1
    return raised1, wedged


def main():
    hass = FakeHass(_states())

    async def ok(call):
        return {"weather.home": {"forecast": fp.healthy_forecast()}}
    hass.services.async_register("weather", "get_forecasts", ok)
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(fp.CFG)))
    asyncio.run(c._async_update_data())
    cached = copy.deepcopy(c._optimization_result)
    cm._shutdown_process_pool()

    async def fake_opt(*a, **k):
        return copy.deepcopy(cached)
    with mock.patch.object(cm, "_await_optimize", fake_opt):
        for arm in ("raw", "ha"):
            r1, w = run(arm)
            print(f"RESULT {arm}_first_cycle_raised={r1} payloads_of_200")
            print(f"RESULT {arm}_wedged={w} payloads_of_200")


main()
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
