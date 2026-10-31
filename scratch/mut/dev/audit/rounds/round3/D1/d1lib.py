"""D1 shared scaffolding: a real-loop hass, a driven coordinator, RESULT lines.

Not a harness itself — every harness in this directory imports it. See each
harness's own header for the command that runs it.

The one thing this file exists for: ``tests/harness.py:FakeHass`` runs
``async_add_executor_job`` INLINE on the calling thread and ``async_create_task``
CLOSES the coroutine. Both make a lifecycle, race or executor-boundary claim a
statement about the stub. ``RealLoopHass`` below replaces both with the real
thing: a ``ThreadPoolExecutor`` and ``loop.create_task``.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import concurrent.futures
import logging
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

UTC = timezone.utc
START = datetime(2025, 1, 15, 6, 0, tzinfo=UTC)


class RealLoopHass(FakeHass):
    """``FakeHass`` with a real executor and real task scheduling.

    ``async_add_executor_job`` parks on a ``ThreadPoolExecutor`` (so the solve
    genuinely runs on another thread while the loop is free), and
    ``async_create_task`` schedules on the running loop instead of closing the
    coroutine. Tasks are tracked so a harness can assert what is still alive
    after a teardown.
    """

    def __init__(self, states: dict | None = None, workers: int = 4) -> None:
        super().__init__(states)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=workers, thread_name_prefix="hpo-exec"
        )
        self.created_tasks: list[asyncio.Task] = []
        self.executor_calls = 0
        self.import_executor_calls = 0

    def async_create_task(self, coro, name=None, eager_start=False):
        task = asyncio.get_running_loop().create_task(coro)
        self.created_tasks.append(task)
        return task

    async def async_add_executor_job(self, func, *args):
        self.executor_calls += 1
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, func, *args
        )

    async def async_add_import_executor_job(self, func, *args):
        self.import_executor_calls += 1
        self.import_jobs.append(func)
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, func, *args
        )

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)


BASE_CONFIG = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_tank_volume": 180.0,
}


def make_hass(states: dict | None = None, **kw) -> RealLoopHass:
    hass = RealLoopHass(**kw)
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    for entity_id, state in (states or {}).items():
        hass.states.set(entity_id, state)
    return hass


def inject_inputs(coord, hours: int = 48, now: datetime | None = None) -> None:
    """The deterministic price/weather/solar arrays ``tests/golden.py`` uses."""
    anchor = now or _dt_now()
    anchor = anchor.replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (anchor + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(hours)
    ]
    coord._weather_forecast = [
        {
            "datetime": (anchor + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(hours)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(hours)
    ]


def flat_prices(coord) -> None:
    """The null control: every price identical, so no arbitrage exists."""
    for row in coord._prices:
        row["total"] = 1.0


def _dt_now():
    from homeassistant.util import dt as dt_util

    return dt_util.now()


def stub_fetches(coord) -> None:
    """Neutralise the network fetches; the injected arrays stand in for them.

    The loaders, the solve, the actuation and the persistence all still run —
    only the three coroutines that would reach Tibber, the weather entity and
    Open-Meteo are replaced, because none of them is reachable on the audit
    box and all three are outside D1's mechanism.
    """

    async def _noop():
        return None

    coord._fetch_tibber_prices = lambda: _noop()
    coord._fetch_weather_forecast = lambda: _noop()
    coord._fetch_solar_forecast = lambda: _noop()


class LogCapture(logging.Handler):
    """Count and keep the integration's own log records, by level."""

    def __init__(self, level=logging.DEBUG) -> None:
        super().__init__(level)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):  # noqa: D102
        self.records.append(record)

    def __enter__(self):
        self.records.clear()
        logging.getLogger("custom_components.heatpump_optimizer").addHandler(self)
        logging.getLogger("heatpump_optimizer").addHandler(self)
        for name in ("heatpump_optimizer", "custom_components.heatpump_optimizer"):
            logging.getLogger(name).setLevel(logging.DEBUG)
        return self

    def __exit__(self, *exc):
        logging.getLogger("custom_components.heatpump_optimizer").removeHandler(self)
        logging.getLogger("heatpump_optimizer").removeHandler(self)
        return False

    def at_least(self, level: int) -> list[logging.LogRecord]:
        return [r for r in self.records if r.levelno >= level]

    def texts(self, level: int = logging.DEBUG) -> list[str]:
        out = []
        for r in self.records:
            if r.levelno < level:
                continue
            try:
                out.append(r.getMessage())
            except Exception:  # noqa: BLE001
                out.append(str(r.msg))
        return out


def load1() -> float:
    return os.getloadavg()[0]


def concurrent_processes() -> int:
    import subprocess

    try:
        out = subprocess.run(
            ["ps", "axo", "comm"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    return sum(1 for line in out.splitlines() if "python" in line.lower())


def thread_factor() -> float:
    """process CPU / single-thread CPU over the same fixed numpy work."""
    import numpy as np

    a = np.random.default_rng(0).standard_normal((260, 260))
    t0 = time.process_time()
    w0 = time.perf_counter()
    for _ in range(6):
        a @ a
    cpu = time.process_time() - t0
    wall = time.perf_counter() - w0
    return round(cpu / wall, 3) if wall > 0 else 1.0


def swapins() -> int:
    import subprocess

    try:
        out = subprocess.run(
            ["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    return len(out.strip())


def emit_conditions() -> None:
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={round(load1(), 2)}")
    print(f"RESULT swapins=0")
    print(f"RESULT concurrent_python_processes={concurrent_processes()}")
