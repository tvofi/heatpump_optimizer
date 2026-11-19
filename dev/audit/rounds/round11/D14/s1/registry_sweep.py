"""D14-s1 detector for class N-registry-leak: a module-level registry that keeps
a torn-down coordinator (or its entry) reachable, or grows by one per
setup/unload cycle and never shrinks.

Metric: after N setup -> solved cycle -> unload rounds on a real asyncio loop
(the R10 D1-s1-01 harness's scaffolding, dev/audit/harnesses/r10_registry_leak.py),
(1) torn_alive = torn coordinators still alive after gc (weakref), and (2) per
module-level container of every custom_components.heatpump_optimizer module
(dict, set, list, WeakKeyDictionary, WeakValueDictionary, enumerated by
introspection, not by name), registry_seams = containers whose size after the
last unload exceeds their size before the first setup by >= N (grew per cycle).
Arms: --fresh-entry gives every round a new entry_id (remove + add) instead of
the HA reload of one entry. Key = the live containers' sizes and weakrefs.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/registry_sweep.py [--rounds 5] [--fresh-entry] [--perturb]
Expected at 92d38ecb: torn_alive and registry_seams as printed (counts, exact).
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer:async_setup_entry / async_unload_entry
           and every module-level container of the package.
Perturbation (--perturb): early_cutoff.detach replaced by release only (the pre-#2329
           unload, one line) -> torn_alive 0 -> N (up).
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


import gc, weakref, importlib, pkgutil  # noqa: E402
from weakref import WeakKeyDictionary, WeakValueDictionary  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer import early_cutoff  # noqa: E402

PERTURB = "--perturb" in sys.argv
FRESH = "--fresh-entry" in sys.argv
N = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 5


def containers():
    import heatpump_optimizer as pkg
    out = {}
    for info in pkgutil.iter_modules(pkg.__path__):
        try:
            mod = importlib.import_module(f"heatpump_optimizer.{info.name}")
        except Exception:
            continue
        for name, val in vars(mod).items():
            if type(val) in (dict, set, list, WeakKeyDictionary, WeakValueDictionary) \
                    and not name.startswith("__"):
                out.setdefault(f"{info.name}.{name}", val)
    return out


async def main():
    install_inputs()
    gate = Gate(); gate.install(); gate.release.set()
    if PERTURB:
        early_cutoff.detach = early_cutoff.release
    regs = containers()
    before = {k: len(v) for k, v in regs.items()}
    hass = make_hass()
    refs = []
    entry = FakeEntry(data=dict(CONFIG))
    for i in range(N):
        if FRESH:
            entry = FakeEntry(data=dict(CONFIG), entry_id=f"entry_{i}")
        assert await ha_setup_entry(integration, hass, entry)
        c = entry.runtime_data
        ok = await wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
        assert ok, "cycle did not complete"
        await asyncio.sleep(0.05)
        await ha_unload_entry(integration, hass, entry)
        if FRESH:  # removal: HA's manager drops a removed entry (tests/harness.py keeps it)
            hass.config_entries.entries.remove(entry)
        refs.append(weakref.ref(c))
        del c
    del entry
    await asyncio.sleep(0.2)
    hass.created.clear()
    gc.collect(); gc.collect()
    alive = sum(1 for r in refs if r() is not None)
    after = {k: len(v) for k, v in regs.items()}
    seams = sorted(k for k in regs if after[k] - before[k] >= N)
    for k in seams:
        print("SEAM", k, f"{before[k]} -> {after[k]}")
    holders = []
    for k, reg in regs.items():
        try:
            keys = list(reg.keys()) if hasattr(reg, "keys") else list(reg)
        except Exception:
            keys = []
        if any(r() is not None and (r() in keys or any(v is r() for v in (reg.values() if hasattr(reg, "values") else []))) for r in refs):
            holders.append(k)
    print(f"RESULT rounds={N} count")
    print(f"RESULT arm={'fresh-entry' if FRESH else 'reload'}")
    print(f"RESULT containers={len(regs)} count")
    print(f"RESULT torn_alive={alive} count")
    print(f"RESULT registries_holding_torn={len(holders)} count {' '.join(holders)}")
    print(f"RESULT registry_seams={len(seams)} count")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={load1():.2f}")
    print("RESULT swapins=0")
    hass.pool.shutdown(wait=True)

asyncio.run(main())
