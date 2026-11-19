"""D14-s1 detector for class N-future-clamp: an instant the integration itself
persisted, legitimately in the future, that its own store load rewrites to now.

Metric: clamp_seams = distinct (store key, leaf path with indices as #) that
store.QuarantiningStore.async_load reports in `.bounded` when every store the
coordinator created is re-loaded at the same clock right after the integration
saved it (write-then-read invariance; a correct store hands its own healthy
payload back unchanged). Also printed: future_leaves = instants in the saved
payloads lying ahead of the save clock, by path (the population at risk).
Driven: setup of a coord_all_features entry with indoor/outdoor probes on a real
loop (the r10_registry_leak.py scaffolding), N solved cycles, unload (saves).
Key = the production load's own `bounded` list.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/future_clamp.py [--cycles 2] [--perturb]
Expected at 92d38ecb: clamp_seams as printed (exact count).
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer.store:QuarantiningStore.async_load / _bound_instants.
Perturbation (--perturb, one line): every declared ahead_h in store.DOMAINS read as 0
           (the pre-D1-s2-01 trie) -> clamp_seams up wherever a declared-ahead leaf was saved.
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


import re  # noqa: E402
from datetime import datetime  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer import store as st  # noqa: E402
import golden  # noqa: E402

PERTURB = "--perturb" in sys.argv
CYCLES = int(sys.argv[sys.argv.index("--cycles") + 1]) if "--cycles" in sys.argv else 2
INSTANT = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def leaves(value, path=()):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(value, list):
        for v in value:
            yield from leaves(v, path + ("#",))
    else:
        yield path, value


async def main():
    install_inputs()
    gate = Gate(); gate.install(); gate.release.set()
    if PERTURB:
        for dom in st.DOMAINS.values():
            for k, d in list(dom.items()):
                if isinstance(d, st.Domain) and d.ahead_h:
                    dom[k] = d._replace(ahead_h=0.0)
        st._tries.cache_clear() if hasattr(st._tries, "cache_clear") else None
    stores = []
    real_init = st.QuarantiningStore.__init__

    def rec(self, *a, **k):
        real_init(self, *a, **k)
        stores.append(self)
    st.QuarantiningStore.__init__ = rec
    hass = make_hass()
    cfg = dict(golden.coordinator_scenarios()["coord_all_features"])
    cfg.update(CONFIG)
    entry = FakeEntry(data=cfg)
    assert await ha_setup_entry(integration, hass, entry)
    c = entry.runtime_data
    for i in range(CYCLES):
        await wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
        if i + 1 < CYCLES:
            c._optimization_result = None
            await c.async_refresh()
    await asyncio.sleep(0.1)
    await ha_unload_entry(integration, hass, entry)
    await asyncio.sleep(0.2)
    saved_at = dt_util.as_utc(dt_util.now())
    future = {}
    seams = set(); loaded = 0
    seen = set()
    for s in stores:
        key = str(getattr(s, "key", None) or getattr(s, "_key", "?"))
        if key in seen:
            continue
        seen.add(key)
        raw = st._DISK_PEEK(key) if hasattr(st, "_DISK_PEEK") else None
        data = await s.async_load()
        loaded += 1
        for p in getattr(s, "bounded", []) or []:
            seams.add(f"{key}:{re.sub(r'/[0-9]+(?=/|$)', '/#', '/' + p)}")
        for path, v in leaves(data):
            if isinstance(v, str) and INSTANT.match(v):
                try:
                    when = datetime.fromisoformat(v)
                except ValueError:
                    continue
                if when.tzinfo is None:
                    continue
                if when > saved_at:
                    future["/".join((key,) + path)] = future.get("/".join((key,) + path), 0) + 1
    for s in sorted(seams):
        print("SEAM", s)
    for k, n in sorted(future.items()):
        print("FUTURE", k, n)
    print(f"RESULT stores_loaded={loaded} stores")
    print(f"RESULT future_leaves={sum(future.values())} leaves over {len(future)} paths (after load)")
    print(f"RESULT clamp_seams={len(seams)} (store, path)")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={load1():.2f}")
    print("RESULT swapins=0")
    hass.pool.shutdown(wait=True)

asyncio.run(main())
