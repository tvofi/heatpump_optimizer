"""D1.M6 external-input parsers in the coordinator: the weather.get_forecasts
response (``_fetch_weather_forecast`` -> ``_forecast_in_model_units`` ->
``_forecast_arrays``) and the ECL110 MQTT state handler
(``_async_handle_ecl110_state_message``), driven with seeded hostile payloads.

Metric (one line): per parser, of N seeded hostile payloads, the count whose
first or second full cycle raises (``cycle_raised`` / ``wedged``: the second
cycle, with a HEALTHY forecast restored, still raises), the count whose solve
receives a non-finite or physically impossible weather series
(``poisoned_series``: |T| > 100 degC, wind < 0 or > 100 m/s, rain < 0), and for
ECL110 the count that raise out of the handler or land a non-finite value on
the live state.
Count key: the arrays ``coordinator._forecast_arrays`` returns (the series the
solve receives) and exceptions out of ``_async_update_data`` / the handler.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/parsers.py [--n 200] [--seed 9] [--perturb NAME]
Expected: see RESULT lines (exact for a fixed seed). Baseline
1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B4.

Perturbation ``row_filter``: the stored forecast is validated where it is
stored (``_forecast_in_model_units`` wrapped, in memory, to keep only dict
rows of a list and [] for anything else); weather.wedged must go to 0.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import copy
import json
import logging
import math
import random
import sys
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from lifecycle import _states  # noqa: E402

CFG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "price_source": "entity",
    "price_entity": "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
}


def healthy_forecast():
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    return [{"datetime": (now + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


HOSTILE_VALUES = [float("nan"), float("inf"), float("-inf"), "NaN", "abc", None,
                  1e308, -1e308, -50.0, 1e6, "", [], {}, True, "12,5"]
FIELDS = ["datetime", "temperature", "wind_speed", "precipitation", "humidity",
          "solar_irradiance", "native_solar_irradiance"]


def hostile(rng):
    fc = healthy_forecast()
    kind = rng.choice(["field", "field", "field", "entry", "shape", "oversize",
                       "order", "dt"])
    if kind == "field":
        for _ in range(rng.randint(1, 5)):
            i = rng.randrange(len(fc))
            fc[i][rng.choice(FIELDS)] = rng.choice(HOSTILE_VALUES)
        return {"weather.home": {"forecast": fc}}, kind
    if kind == "entry":
        i = rng.randrange(len(fc))
        fc[i] = rng.choice(["x", None, 5, [], ["a"]])
        return {"weather.home": {"forecast": fc}}, kind
    if kind == "shape":
        return rng.choice([
            {"weather.home": {"forecast": "x"}}, {"weather.home": {"forecast": {"a": 1}}},
            {"weather.home": "x"}, {"weather.home": None}, {"weather.home": []},
            {"weather.home": {"forecast": None}}, {"other": {}}, None, [],
        ]), kind
    if kind == "oversize":
        big = []
        base = dt_util.now()
        for h in range(20000):
            big.append({"datetime": (base + timedelta(minutes=h)).isoformat(),
                        "temperature": 1.0, "wind_speed": 1.0, "precipitation": 0.0})
        return {"weather.home": {"forecast": big}}, kind
    if kind == "order":
        rng.shuffle(fc)
        fc += copy.deepcopy(fc[:5])
        return {"weather.home": {"forecast": fc}}, kind
    # dt: naive, other-offset, garbage and far-future stamps
    for i in rng.sample(range(len(fc)), 6):
        fc[i]["datetime"] = rng.choice([
            fc[i]["datetime"][:19], "2026-13-01T00:00:00+00:00", "9999-12-31T23:00:00+00:00",
            "0001-01-01T00:00:00+00:00", 1767225600, "yesterday"])
    return {"weather.home": {"forecast": fc}}, kind


def poisoned(h):
    bad = 0
    for arr, lo, hi in ((h.outdoor_temps, -100, 100), (h.wind_speeds, 0, 100),
                        (h.precipitation, 0, 1000), (h.solar_radiation, 0, 2000)):
        a = np.asarray(arr, dtype=float)
        if a.size and (not np.all(np.isfinite(a)) or a.min() < lo or a.max() > hi):
            bad += 1
    return bad


def weather_part(n, seed, cached, perturb):
    rng = random.Random(f"{seed}:weather")
    agg = {"cycle_raised": 0, "wedged": 0, "poisoned_series": 0}
    ex = {}
    for i in range(n):
        payload, kind = hostile(rng)
        hass = FakeHass(_states())
        state = {"payload": payload}

        async def handler(call):
            return state["payload"]

        hass.services.async_register("weather", "get_forecasts", handler)
        c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
        seen = {"poison": 0}
        orig_fa = c._forecast_arrays

        def fa(*a, **k):
            h = orig_fa(*a, **k)
            seen["poison"] = max(seen["poison"], poisoned(h))
            return h
        c._forecast_arrays = fa
        try:
            asyncio.run(c._async_update_data())
        except Exception as err:  # noqa: BLE001
            agg["cycle_raised"] += 1
            ex.setdefault("cycle_raised", []).append((i, kind, f"{type(err).__name__}: {str(err)[:100]}"))
            state["payload"] = {"weather.home": {"forecast": healthy_forecast()}}
            try:
                asyncio.run(c._async_update_data())
            except Exception as err2:  # noqa: BLE001
                agg["wedged"] += 1
                ex.setdefault("wedged", []).append((i, kind, f"{type(err2).__name__}: {str(err2)[:100]}"))
        if seen["poison"]:
            agg["poisoned_series"] += 1
            ex.setdefault("poisoned_series", []).append((i, kind, json.dumps(payload, default=str)[:160]))
    for k, v in agg.items():
        print(f"RESULT weather.{k}={v} payloads_of_{n}")
    from collections import Counter
    print(f"  wedged by kind: {dict(Counter(r[1] for r in ex.get('wedged', [])))}")
    for k, rows in ex.items():
        for r in rows[:4]:
            print(f"  ex weather.{k}: {r}")


def ecl_part(n, seed):
    rng = random.Random(f"{seed}:ecl")
    hass = FakeHass(_states())
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
    raised = nonfinite = 0
    shapes = [b'{"displace": %s}', b'{"command": {"displace": %s}}', b'%s',
              b'{"effective_displace": %s, "displace": 1}']
    vals = [b"NaN", b"Infinity", b"-1e999", b"1e308", b'"3"', b'"x"', b"[1]", b"{}", b"null",
            b"true", b"\xff\xfe", b"9" * 5000, b"[" * 5000]
    for _ in range(n):
        body = rng.choice(shapes) % rng.choice(vals)
        msg = SimpleNamespace(payload=rng.choice([body, body.decode("utf-8", "ignore")]))
        try:
            c._async_handle_ecl110_state_message(msg)
        except Exception:  # noqa: BLE001
            raised += 1
        st = c._ctx._current_state
        for v in (st.ecl110_displace_command, st.ecl110_effective_displace, c._ecl110_current_displace):
            if not (isinstance(v, (int, float)) and math.isfinite(float(v))) or abs(float(v)) > 1e6:
                nonfinite += 1
                break
    print(f"RESULT ecl110.handler_raised={raised} payloads_of_{n}")
    print(f"RESULT ecl110.state_nonfinite_or_absurd={nonfinite} payloads_of_{n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=9)
    ap.add_argument("--perturb", default="")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    hass = FakeHass(_states())
    hass.services.async_register("weather", "get_forecasts",
                                 lambda call: _ret({"weather.home": {"forecast": healthy_forecast()}}))
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
    asyncio.run(c._async_update_data())
    cached = copy.deepcopy(c._optimization_result)
    cm._shutdown_process_pool()

    async def fake_opt(hass, optimizer, state, *a, **k):
        return copy.deepcopy(cached)
    patches = [mock.patch.object(cm, "_await_optimize", fake_opt)]
    if args.perturb == "row_filter":
        orig = cm._forecast_in_model_units

        def filtered(state, forecast):
            rows = [r for r in forecast if isinstance(r, dict)] if isinstance(forecast, list) else []
            return orig(state, rows)
        patches.append(mock.patch.object(cm, "_forecast_in_model_units", filtered))
    for p in patches:
        p.start()
    try:
        weather_part(args.n, args.seed, cached, args.perturb)
    finally:
        for p in patches:
            p.stop()
    ecl_part(args.n, args.seed)
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


async def _ret(v):
    return v


if __name__ == "__main__":
    main()
