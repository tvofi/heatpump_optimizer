"""Shared real-loop rig for D1-s1 harnesses (not a harness itself).

RealHass subclasses tests/harness.py:FakeHass so async_add_executor_job runs
in a real ThreadPoolExecutor on the running asyncio loop and async_create_task
schedules a real task (D1.M1). The solve is gated: _await_optimize is
replaced by an executor call to the production optimize_in_process wrapped in
a threading.Event gate, so "mid-solve" is deterministic. Prices/weather are
injected at the fetch seams (no network).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d1s1-"))

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import const  # noqa: E402


class RealHass(FakeHass):
    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="exec")
        self.loop = asyncio.get_running_loop()
        self.created = []
        self.exceptions = []
        self.loop.set_exception_handler(lambda l, c: self.exceptions.append(c))

    def async_create_task(self, coro, *a, **k):
        t = self.loop.create_task(coro)
        self.created.append(t)
        return t

    def async_create_background_task(self, coro, *a, **k):
        return self.async_create_task(coro)

    async def async_add_executor_job(self, func, *args):
        return await self.loop.run_in_executor(self.pool, func, *args)

    async def async_add_import_executor_job(self, func, *args):
        self.import_jobs.append(func)
        return await self.loop.run_in_executor(self.pool, func, *args)


class Gate:
    """Holds every solve in the executor thread until released."""
    def __init__(self):
        self.entered = threading.Event()
        self.release = threading.Event()
        self.calls = 0
        self.thread_cpu = 0.0

    def install(self):
        gate = self
        def gated(optimizer, inputs):
            t0 = time.thread_time()
            gate.calls += 1
            gate.entered.set()
            gate.release.wait(30)
            try:
                return cm.optimize_in_process(optimizer, inputs)
            finally:
                gate.thread_cpu += time.thread_time() - t0
        async def _await_optimize(hass, optimizer, inputs):
            return await hass.async_add_executor_job(gated, optimizer, inputs)
        cm._await_optimize = _await_optimize


def install_inputs():
    async def prices(self):
        start = dt_util.now().replace(minute=0, second=0, microsecond=0)
        self._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                         "starts_at": (start + timedelta(hours=h)).isoformat(),
                         "level": "NORMAL"} for h in range(36)]
    async def weather(self):
        start = dt_util.now().replace(minute=0, second=0, microsecond=0)
        self._weather_forecast = [{"datetime": (start + timedelta(hours=h)).isoformat(),
                                   "temperature": -5.0, "wind_speed": 3.0,
                                   "precipitation": 0.0, "humidity": 85.0}
                                  for h in range(36)]
    async def solar(self):
        return None
    cm.HeatPumpOptimizerCoordinator._fetch_tibber_prices = prices
    cm.HeatPumpOptimizerCoordinator._fetch_weather_forecast = weather
    cm.HeatPumpOptimizerCoordinator._fetch_solar_forecast = solar


def make_hass():
    now = dt_util.now()
    hass = RealHass()
    hass.states.set("sensor.indoor", FakeState("21.4", last_updated=now))
    hass.states.set("sensor.outdoor", FakeState("-3.0", last_updated=now))
    return hass


CONFIG = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
          const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}


async def wait_for(pred, timeout=20.0):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.01)
    return True


def load1():
    return os.getloadavg()[0]
