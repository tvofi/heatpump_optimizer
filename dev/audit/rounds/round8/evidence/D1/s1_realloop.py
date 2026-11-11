"""Real-loop Home Assistant fakes for D1 seat s1 (round 8). Library, not a harness.

Imported by s1_lifecycle.py and s1_setback_race.py. It subclasses
tests/harness.py:FakeHass so that
  * async_add_executor_job runs on a real concurrent.futures.ThreadPoolExecutor
    through loop.run_in_executor (FakeHass runs it inline on the loop thread);
  * async_create_task schedules a real asyncio.Task (FakeHass closes the coro);
and gives the config entry Home Assistant's own state-machine semantics
(homeassistant/config_entries.py, 2025.x):
  * async_setup / async_unload / async_reload serialised by a per-entry
    asyncio.Lock (``setup_lock``), reload = unload then setup under one hold;
  * ConfigEntry.async_on_unload callbacks popped LIFO after a successful
    unload; a callback that returns a coroutine is scheduled and awaited;
  * async_create_background_task tasks tracked per entry and cancelled at
    unload, then awaited (10 s cap), as _async_process_on_unload does;
  * runtime_data deleted after a successful unload.
The solve itself runs in the production process worker
(coordinator._run_in_process), i.e. a real child interpreter.

Run nothing from here; see the two harnesses for commands.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import os
import sys
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeConfigEntries, FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402


class RealLoopHass(FakeHass):
    def __init__(self, states=None, max_workers: int = 4) -> None:
        super().__init__(states)
        self.loop = asyncio.get_running_loop()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="SyncWorker"
        )
        self.created_tasks: list[asyncio.Task] = []
        self.executor_futures: list[asyncio.Future] = []
        self.config_entries = RealConfigEntries(self)

    def async_create_task(self, coro, name=None, eager_start=True):
        task = self.loop.create_task(coro, name=name)
        self.created_tasks.append(task)
        return task

    def async_create_background_task(self, coro, name=None, eager_start=True):
        return self.async_create_task(coro, name=name)

    def async_add_executor_job(self, func, *args):
        fut = self.loop.run_in_executor(self.executor, func, *args)
        self.executor_futures.append(fut)
        return fut

    async def async_add_import_executor_job(self, func, *args):
        self.import_jobs.append(func)
        return await self.loop.run_in_executor(self.executor, func, *args)


class RealEntry(FakeEntry):
    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.setup_lock = asyncio.Lock()
        self._tasks: set[asyncio.Task] = set()
        self._background_tasks: set[asyncio.Task] = set()
        self.update_listeners: list = []

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)

        def _remove():
            if listener in self.update_listeners:
                self.update_listeners.remove(listener)

        return _remove

    def async_create_task(self, hass, coro, name=None, eager_start=True):
        task = hass.async_create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def async_create_background_task(self, hass, coro, name=None, eager_start=True):
        task = hass.async_create_task(coro, name=name)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    async def _async_process_on_unload(self, hass) -> None:
        while self._on_unload:
            job = self._on_unload.pop()()
            if asyncio.iscoroutine(job):
                self.async_create_task(hass, job)
        if not self._tasks and not self._background_tasks:
            return
        for task in self._background_tasks:
            task.cancel(f"Config entry {self.title} unloading")
        _, pending = await asyncio.wait(
            [*self._tasks, *self._background_tasks], timeout=10
        )
        self.unload_pending = len(pending)


class RealConfigEntries(FakeConfigEntries):
    def __init__(self, hass) -> None:
        super().__init__()
        self.hass = hass
        self.integration = None

    async def _setup(self, entry) -> bool:
        entry.state = ConfigEntryState.SETUP_IN_PROGRESS
        ok = await self.integration.async_setup_entry(self.hass, entry)
        entry.state = ConfigEntryState.LOADED if ok else ConfigEntryState.SETUP_ERROR
        return ok

    async def _unload(self, entry) -> bool:
        entry.state = ConfigEntryState.UNLOAD_IN_PROGRESS \
            if hasattr(ConfigEntryState, "UNLOAD_IN_PROGRESS") else entry.state
        ok = await self.integration.async_unload_entry(self.hass, entry)
        if ok:
            entry.state = ConfigEntryState.NOT_LOADED
            if hasattr(entry, "runtime_data"):
                delattr(entry, "runtime_data")
            await entry._async_process_on_unload(self.hass)
        return ok

    async def async_setup(self, entry_id) -> bool:
        entry = self.async_get_entry(entry_id)
        async with entry.setup_lock:
            return await self._setup(entry)

    async def async_unload(self, entry_id) -> bool:
        entry = self.async_get_entry(entry_id)
        async with entry.setup_lock:
            return await self._unload(entry)

    async def async_reload(self, entry_id) -> bool:
        self.reloaded.append(entry_id)
        entry = self.async_get_entry(entry_id)
        async with entry.setup_lock:
            if not await self._unload(entry):
                return False
            return await self._setup(entry)

    def async_update_entry(self, entry, options=None, **kwargs):
        changed = options is not None and dict(options) != dict(entry.options)
        super().async_update_entry(entry, options=options, **kwargs)
        if changed:
            for listener in list(entry.update_listeners):
                self.hass.async_create_task(listener(self.hass, entry))


def price_state(now=None) -> FakeState:
    """A Nord Pool-shaped price entity: 48 hourly rows from today's midnight."""
    now = now or dt_util.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = [
        {
            "start": (midnight + timedelta(hours=h)).isoformat(),
            "end": (midnight + timedelta(hours=h + 1)).isoformat(),
            "value": round(0.6 + 0.5 * ((h * 7) % 12) / 12.0, 4),
        }
        for h in range(48)
    ]
    return FakeState(
        "0.8",
        last_updated=now,
        attributes={"raw_today": rows[:24], "raw_tomorrow": rows[24:]},
    )


def base_states(now=None) -> dict:
    now = now or dt_util.now()
    return {
        "sensor.indoor": FakeState("21.4", last_updated=now),
        "sensor.outdoor": FakeState("-3.0", last_updated=now),
        "sensor.price": price_state(now),
    }


def base_config(const) -> dict:
    return {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price",
        const.CONF_DHW_TANK_VOLUME: 180.0,
    }


def load1() -> float:
    try:
        return float(open("/proc/loadavg").read().split()[0])
    except Exception:  # noqa: BLE001
        return float("nan")


def swapins() -> int:
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except Exception:  # noqa: BLE001
        pass
    return 0
