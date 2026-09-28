"""Shared instruments for round-5 D1 seat-a: a real-asyncio-loop FakeHass.

Subclasses ``tests/harness.py:FakeHass`` so that (per the D1 brief):

* ``async_add_executor_job`` runs the target in a real
  ``concurrent.futures.ThreadPoolExecutor`` via ``loop.run_in_executor``
  -- the executor boundary is a real second thread, not the stub's
  inline call;
* ``async_create_task`` schedules the coroutine on the loop instead of
  closing it -- the coordinator's ``_spawn``ed store loads and the
  deferred first solve actually run.

Thread-pin (audit README): set before any numpy import.
Everything here is in-memory only; production and tests on disk are never
modified. Run scripts from the repository root with PYTHONPATH=tests/hastub.
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[5]  # file -> seat-a -> D1 -> round5 -> audit -> tools -> root
for _p in (str(_REPO / "tests"), str(_REPO / "custom_components")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

UTC = timezone.utc
#: Deterministic clock anchor (same discipline as tests/golden.py START).
START = datetime(2026, 1, 15, 6, 0, tzinfo=UTC)


class LoopHass(FakeHass):
    """FakeHass with real-loop task scheduling and a real executor thread.

    ``loop`` and the executor are bound by :meth:`bind_loop` because a
    coordinator is constructed with the hass and then awaited on the loop;
    ``hass.loop`` is what the Debouncer stub reads for ``call_later``.

    Executor CPU is measured per job (``time.thread_time`` on the worker
    thread) so a harness can print the residual thread_factor the audit
    README mandates for a deliberate second thread.
    """

    def __init__(self, states=None) -> None:
        super().__init__(states)
        self.loop: asyncio.AbstractEventLoop | None = None
        self._executor: ThreadPoolExecutor | None = None
        self.tasks: list[asyncio.Task] = []
        self.task_failures: list[tuple[str, BaseException]] = []
        self.executor_jobs: list[dict] = []
        self.executor_thread_cpu: float = 0.0
        self._executor_cpu_lock = threading.Lock()
        # Optional mid-solve gate: (arm, submitted_evt, release_evt)
        self.solve_gate: tuple[bool, threading.Event, threading.Event] | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="hpo-d1a-exec"
        )

    async def shutdown_executor(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None

    def _on_task_done(self, task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            self.task_failures.append((task.get_name(), exc))

    def async_create_task(self, coro):
        assert self.loop is not None, "bind_loop() first"
        task = self.loop.create_task(coro)
        self.tasks.append(task)
        task.add_done_callback(self._on_task_done)
        return task

    def _executor_target(self, func, meta: dict):
        def _run(*args):
            t0 = time.thread_time()
            try:
                meta["done_ok"] = True
                return func(*args)
            except BaseException as err:  # recorded, re-raised into the future
                meta["raised"] = repr(err)
                raise
            finally:
                with self._executor_cpu_lock:
                    self.executor_thread_cpu += time.thread_time() - t0

        return _run

    async def async_add_executor_job(self, func, *args):
        assert self.loop is not None and self._executor is not None
        meta: dict = {"func": getattr(func, "__name__", repr(func))}
        gate = self.solve_gate
        if (
            gate is not None
            and gate[0]
            and getattr(func, "__name__", "") == "_run_in_process"
        ):
            # Deterministic mid-solve point: the solve job has been
            # submitted to the executor but has not started yet.
            meta["gated"] = True
            gate[1].set()
            gate[2].wait(timeout=60.0)
        self.executor_jobs.append(meta)
        fut = self.loop.run_in_executor(
            self._executor, self._executor_target(func, meta), *args
        )
        try:
            return await fut
        except asyncio.CancelledError:
            # The awaiting task went away (unload); the executor thread
            # keeps running, exactly as in Home Assistant.
            meta["await_cancelled"] = True
            raise

    async def async_add_import_executor_job(self, func, *args):
        self.import_jobs.append(func)
        return await self.async_add_executor_job(func, *args)


def seed_states(hass: LoopHass, now: datetime = START) -> None:
    """Offline sensor/weather/price inputs for a full update cycle.

    Prices come from an entity (``price_source: entity``) so no network is
    touched; weather comes from a registered ``get_forecasts`` handler.
    """
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    hass.states.set(
        "sensor.house_power", FakeState("1.1", unit="kW", last_updated=now)
    )
    rows_today = [
        {
            "start": (now + timedelta(hours=h)).isoformat(),
            "total": round(0.4 + 0.4 * ((h % 12) / 12.0), 4),
        }
        for h in range(0, 24)
    ]
    rows_tomorrow = [
        {
            "start": (now + timedelta(hours=h)).isoformat(),
            "total": round(0.4 + 0.4 * (((h + 6) % 12) / 12.0), 4),
        }
        for h in range(24, 48)
    ]
    hass.states.set(
        "sensor.prices",
        FakeState(
            "0.6",
            last_updated=now,
            attributes={"raw_today": rows_today, "raw_tomorrow": rows_tomorrow},
        ),
    )
    forecast = [
        {
            "datetime": (now + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * ((h % 24) / 24.0),
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(30)
    ]

    async def _get_forecasts(call):
        return {"weather.home": {"forecast": forecast}}

    hass.services.async_register("weather", "get_forecasts", _get_forecasts)


def base_config(entry_id: str = "d1a_entry") -> dict:
    return {
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "weather_entity": "weather.home",
        "price_source": "entity",
        "price_entity": "sensor.prices",
        "house_power_entity": "sensor.house_power",
        "peak_guard_enabled": True,
        "dhw_tank_volume": 180.0,
        "dhw_setpoint": 55.0,
        "dhw_min_temperature": 45.0,
        "dhw_windows": "06:00-08:30, 17:00-22:00",
        "heat_pump_defrost_entity": "binary_sensor.defrost",
        "optimization_interval": 30,
    }


def make_entry(entry_id: str = "d1a_entry", config: dict | None = None) -> FakeEntry:
    return FakeEntry(data=dict(config or base_config(entry_id)), entry_id=entry_id)


async def drain_tasks(rounds: int = 6) -> None:
    """Let the loop run every ready callback and pending task step."""
    for _ in range(rounds):
        await asyncio.sleep(0)


def box_conditions() -> dict:
    """load1, concurrent test processes, thread factor inputs."""
    import subprocess

    load1 = None
    try:
        out = subprocess.run(
            ["ps", "ax", "-o", "command"], capture_output=True, text=True
        ).stdout
        conc = sum(
            1
            for line in out.splitlines()
            if ("stress.py" in line or "tests/run.sh" in line)
            and "grep" not in line
        )
    except Exception:
        conc = -1
    try:
        with open("/proc/loadavg") as fh:
            load1 = float(fh.read().split()[0])
    except OSError:
        out = subprocess.run(
            ["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True
        ).stdout
        try:
            load1 = float(out.strip().strip("{ }").split()[1])
        except Exception:
            load1 = -1.0
    return {"load1": load1, "concurrent_test_processes": conc}
