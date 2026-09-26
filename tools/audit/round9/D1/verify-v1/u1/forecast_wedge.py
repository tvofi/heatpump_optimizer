"""V1 verifier harness for D1-s2-01: after ONE malformed weather.get_forecasts
response, how many of the following K healthy-forecast cycles still raise?

Metric (one line): per malformed payload shape, of K=6 consecutive
coordinator._async_update_data cycles run after the malformed cycle with a
healthy 48-row forecast served, the number that raise; summed (wedged_cycles).
Count key: exceptions escaping production _async_update_data.

Shapes: non-dict row ("x", None, 5, ["a"]) at index 0; forecast a string; a dict.
Null control (--null): the first cycle is served a healthy forecast too -> 0.
Perturbation (--perturb, in memory): coordinator._current_humidity skips
non-dict rows (the reader the wedge runs through) -> 0.

Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v1/u1/forecast_wedge.py [--null|--perturb]
Baseline 1936d5ca (evidence tree 6f51db2c). Machine: 4 vCPU cloud container (G1-V1).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import logging
import sys
import time
from datetime import timedelta
from unittest import mock

logging.disable(logging.CRITICAL)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round9/D1/s2")
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from lifecycle import _states  # noqa: E402  (the finder's healthy entity states)

NULL = "--null" in sys.argv
PERTURB = "--perturb" in sys.argv
K = 6
_c0, _t0 = time.process_time(), time.thread_time()
CFG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "price_source": "entity", "price_entity": "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
}


def healthy():
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    return [{"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -5.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


SHAPES = {
    "row_str": lambda: {"weather.home": {"forecast": ["x"] + healthy()}},
    "row_none": lambda: {"weather.home": {"forecast": [None] + healthy()}},
    "row_int": lambda: {"weather.home": {"forecast": [5] + healthy()}},
    "row_list": lambda: {"weather.home": {"forecast": [["a"]] + healthy()}},
    "forecast_str": lambda: {"weather.home": {"forecast": "x"}},
    "forecast_dict": lambda: {"weather.home": {"forecast": {"a": 1}}},
}


def run(shape):
    hass = FakeHass(_states())
    state = {"p": {"weather.home": {"forecast": healthy()}} if NULL else SHAPES[shape]()}

    async def handler(call):
        return state["p"]
    hass.services.async_register("weather", "get_forecasts", handler)
    c = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CFG)))
    first = 0
    try:
        asyncio.run(c._async_update_data())
    except Exception:  # noqa: BLE001
        first = 1
    state["p"] = {"weather.home": {"forecast": healthy()}}
    wedged = 0
    for _ in range(K):
        try:
            asyncio.run(c._async_update_data())
        except Exception:  # noqa: BLE001
            wedged += 1
    return first, wedged


_orig_hum = cm.HeatPumpOptimizerCoordinator._current_humidity


def _hum_skip(self):
    fc = self._weather_forecast
    if isinstance(fc, list):
        with mock.patch.object(self, "_weather_forecast", [r for r in fc if isinstance(r, dict)]):
            return _orig_hum(self)
    with mock.patch.object(self, "_weather_forecast", []):
        return _orig_hum(self)


total = 0
ctx = mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_current_humidity", _hum_skip) if PERTURB else None
if ctx:
    ctx.start()
for s in SHAPES:
    f, w = run(s)
    total += w
    print(f"  shape={s} first_cycle_raised={f} wedged_cycles={w}/{K}")
if ctx:
    ctx.stop()
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT wedged_cycles={total} cycles_of_{K * len(SHAPES)}")
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
