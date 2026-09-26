"""V1 verifier harness for D1-s2-01 (reach attack): the finder's 200 seeded hostile
get_forecasts payloads, delivered the way Home Assistant core's weather service
delivers them.

HA core's async_get_forecasts_service builds the response itself:
{"forecast": weather._convert_forecast(native_list)}, and _convert_forecast
does `dict(row)` on every native row -- so the integration always receives a
list of dicts, and a row dict() cannot build makes the service call itself
raise (read at homeassistant 2024.3.3, components/weather/__init__.py:821-822
and :1171-1178). This harness applies that shaping to each payload the finder's
generator (tools/audit/round9/D1/s2/parsers.py:hostile) produces, then runs the
finder's own two-cycle check.

Metric (one line): of N seeded payloads (seed 9), after core-style shaping, the
count whose second full cycle (healthy forecast restored) still raises
(core_wedged); beside it the unshaped count (raw_wedged, the finder's 35).
Count key: exceptions escaping production _async_update_data.
Null control: raw_wedged is the finder's arm in the same run (expect 35).
Perturbation (--no-shape): shaping off -> core_wedged equals raw_wedged.

Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v1/u1/forecast_core_shape.py [--n 200] [--seed 9] [--no-shape]
Baseline 1936d5ca (evidence tree 6f51db2c). Machine: 4 vCPU cloud container (G1-V1).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio
import copy
import logging
import random
import sys
import time
from unittest import mock

sys.path.insert(0, "tools/audit/round9/D1/s2")
import parsers as P  # noqa: E402  (the finder's generator and fixtures)

N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 200
SEED = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 9
SHAPE = "--no-shape" not in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)


def core_shape(payload):
    """What HA core's get_forecasts could have returned for this payload."""
    if not isinstance(payload, dict) or "weather.home" not in payload:
        return payload            # entity absent: core returns no key for it
    ent = payload["weather.home"]
    fc = ent.get("forecast") if isinstance(ent, dict) else None
    if fc is None:
        return {"weather.home": {"forecast": []}}
    if not isinstance(fc, list):
        raise TypeError("native forecast is not a list (core iterates it)")
    return {"weather.home": {"forecast": [dict(r) for r in fc]}}


def run(shape):
    rng = random.Random(f"{SEED}:weather")
    wedged = unreachable = 0
    for _ in range(N):
        payload, kind = P.hostile(rng)
        hass = P.FakeHass(P._states())
        state = {"payload": payload}

        async def handler(call):
            p = state["payload"]
            return core_shape(p) if shape else p
        hass.services.async_register("weather", "get_forecasts", handler)
        c = P.cm.HeatPumpOptimizerCoordinator(hass, P.FakeEntry(data=dict(P.CFG)))
        if shape:
            try:
                core_shape(payload)
            except Exception:  # noqa: BLE001
                unreachable += 1
        try:
            asyncio.run(c._async_update_data())
        except Exception:  # noqa: BLE001
            state["payload"] = {"weather.home": {"forecast": P.healthy_forecast()}}
            try:
                asyncio.run(c._async_update_data())
            except Exception:  # noqa: BLE001
                wedged += 1
    return wedged, unreachable


# The finder's setup: one real solve cached, then _await_optimize returns it.
hass0 = P.FakeHass(P._states())
hass0.services.async_register("weather", "get_forecasts",
                              lambda call: P._ret({"weather.home": {"forecast": P.healthy_forecast()}}))
c0 = P.cm.HeatPumpOptimizerCoordinator(hass0, P.FakeEntry(data=dict(P.CFG)))
asyncio.run(c0._async_update_data())
cached = copy.deepcopy(c0._optimization_result)
P.cm._shutdown_process_pool()


async def fake_opt(hass, optimizer, state, *a, **k):
    return copy.deepcopy(cached)

with mock.patch.object(P.cm, "_await_optimize", fake_opt):
    raw_w, _ = run(False)
    core_w, unreach = run(True) if SHAPE else (raw_w, 0)
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT raw_wedged={raw_w} payloads_of_{N}")
print(f"RESULT core_wedged={core_w} payloads_of_{N}")
print(f"RESULT core_rejected_at_service={unreach} payloads_of_{N}")
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
