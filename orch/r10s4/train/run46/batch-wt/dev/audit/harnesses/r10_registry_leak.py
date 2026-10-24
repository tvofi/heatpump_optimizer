"""R10-REGISTRY-LEAK finder harness (D1-s1-01): torn-down coordinators kept alive.

Counts HeatPumpOptimizerCoordinator objects still alive (weakref) after N
setup -> solved+actuated cycle -> unload rounds, and per module-level
registry (early_cutoff, boost, pump_arbiter, debugger) how many torn
coordinators it still holds as keys. A real loop; the solve is gated.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_registry_leak.py [--rounds 5] [--perturb]

Expected at baseline 17f1c55fad1b: torn_alive=5, early_cutoff_torn_keys=5.
Expected fixed: torn_alive=0, every registry 0. --perturb pops
early_cutoff._STATES at shutdown: the baseline then also reads 0 (the null
that names the registry as the pin). Thread-CPU lines are contention noise.
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


import gc, weakref
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer import early_cutoff, boost, pump_arbiter, debugger  # noqa: E402

PERTURB = "--perturb" in sys.argv
N = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 5
REGISTRIES = {"early_cutoff": early_cutoff._STATES, "boost_states": boost._STATES,
              "boost_plan_bases": boost._PLAN_BASES, "pump_arbiter": pump_arbiter._STATES,
              "debugger": debugger._COLLECTORS}


async def main():
    install_inputs()
    gate = Gate(); gate.install(); gate.release.set()
    Coord = cm.HeatPumpOptimizerCoordinator
    if PERTURB:
        orig = Coord.async_shutdown
        async def popping(self):
            await orig(self)
            early_cutoff._STATES.pop(self, None)
        Coord.async_shutdown = popping
    armed = {"n": 0}
    orig_arm = early_cutoff.arm
    async def counting_arm(*a, **k):
        armed["n"] += 1
        return await orig_arm(*a, **k)
    early_cutoff.arm = counting_arm
    hass = make_hass()
    entry = FakeEntry(data=dict(CONFIG))
    refs = []
    for _ in range(N):
        assert await ha_setup_entry(integration, hass, entry)
        c = entry.runtime_data
        ok = await wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
        assert ok, "cycle did not complete"
        await asyncio.sleep(0.05)
        await ha_unload_entry(integration, hass, entry)
        refs.append(weakref.ref(c))
        del c
    await asyncio.sleep(0.2)
    hass.created.clear()
    gc.collect(); gc.collect()
    alive = sum(1 for r in refs if r() is not None)
    print(f"RESULT rounds={N} count")
    print(f"RESULT early_cutoff_arm_calls={armed['n']} count")
    print(f"RESULT torn_alive={alive} count")
    for name, reg in REGISTRIES.items():
        held = sum(1 for r in refs if r() is not None and r() in reg)
        print(f"RESULT registry_{name}_torn_keys={held} count")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={load1():.2f}")
    print("RESULT swapins=0")
    hass.pool.shutdown(wait=True)

asyncio.run(main())
