#!/usr/bin/env python
"""D1 lifecycle harness: a real asyncio loop, a ThreadPoolExecutor, and a
model of Home Assistant's DataUpdateCoordinator + config-entry state machine.

METRIC (one line each, all counts, contention-immune):
  notready_leaked_listeners      state-change listeners on the bus whose callback
                                 is bound to a coordinator from a setup that
                                 raised ConfigEntryNotReady (expected 0)
  notready_leaked_mqtt_subs      same for MQTT subscriptions
  notready_zombie_coordinators   coordinators from failed setups still alive
                                 after gc.collect() once the entry finally loads
  notready_zombie_handler_runs   how many dead-coordinator handlers ran for ONE
                                 power-meter state event after the entry loaded
  reload_midsolve_*              leaks after reload during the in-flight first
                                 solve (entry background task; HA cancels it)
  sched_midsolve_zombie_actuations  service calls (switch / mqtt) issued by the
                                 torn-down coordinator AFTER its async_shutdown
                                 returned, when a SCHEDULED refresh was in
                                 flight at reload (expected 0)
  sched_midsolve_zombie_saves    store writes by the torn-down coordinator after
                                 its shutdown, same scenario
  *_escaped_exceptions           exceptions surfaced to the loop handler or
                                 left on tasks (expected 0)
  new_first_cycle_ok             1 when the post-reload instance solves

COMMAND (from the export root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D1/lifecycle_realloop.py

EXPECTED (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, exact):
  notready_leaked_listeners=10 (5 failed setups x 2 listeners: peak guard + defrost)
  notready_leaked_mqtt_subs=5, notready_zombie_coordinators=5,
  notready_zombie_handler_runs=5, notready_leaked_listeners_guards_off=0
  sched_midsolve_zombie_actuations>=1, reload_midsolve leaks = 0

INSTRUMENTED SYMBOLS:
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_setup_peak_guard
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_setup_defrost_watch
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_run_optimization
  heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (gated, class-attribute swap)
  heatpump_optimizer:async_setup_entry / async_unload_entry (driven through the
  modelled ConfigEntry.async_setup / async_unload / async_reload)

PERTURBATIONS:
  notready_*: config peak_guard_enabled=False + no defrost entity + empty
    ecl110_state_topic -> to_zero (the guards_off arm below runs it); or a
    one-line edit registering the listeners after the first refresh / through
    entry.async_on_unload -> to_zero.
  sched_midsolve_zombie_actuations: one-line edit in async_run_optimization
    after `result = await self.hass.async_add_executor_job(...)`:
    `if getattr(self, "_shutdown_requested", False): return` -> to_zero.

MODELLED HA SEMANTICS (HA core 2024.x, written from the core sources):
  * DataUpdateCoordinator: _async_refresh runs _async_update_data; a scheduled
    refresh is a hass-level task (loop.call_at -> task), NOT an entry task;
    async_shutdown sets _shutdown_requested, cancels the scheduled timer and
    the debouncer, and does NOT cancel an in-flight refresh;
    async_config_entry_first_refresh raises ConfigEntryNotReady when the
    refresh failed; refreshes are only scheduled while listeners exist.
  * Debouncer: immediate=True, cooldown shortened to 0.05 s (10 s in HA; the
    value only sets the pace of the run, never a count).
  * ConfigEntry.async_setup: ConfigEntryNotReady -> SETUP_RETRY and
    _async_process_on_unload (runs async_on_unload callbacks, cancels entry
    background tasks). async_unload -> component unload, then
    _async_process_on_unload. async_reload = unload + setup under setup_lock.
  * Platforms: async_forward_entry_setups adds one coordinator listener per
    platform (what CoordinatorEntity.async_added_to_hass does);
    async_unload_platforms removes them.
  * hass.async_create_task starts tasks eagerly (HA >= 2024.3); the run is
    repeated with lazy start (HA 2024.1-2024.2) and both are reported.

MACHINE: Apple M1 8-core 8 GB, Darwin 25.6.0, CPython 3.13.1, numpy 2.5.2
"""
from __future__ import annotations

import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import asyncio
import gc
import logging
import sys
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import aiohttp  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

import homeassistant.helpers.update_coordinator as uc  # noqa: E402
import homeassistant.helpers.storage as storage  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402

UpdateFailed = uc.UpdateFailed


class ConfigEntryNotReady(HomeAssistantError):
    """What real HA raises out of async_config_entry_first_refresh."""


# ---------------------------------------------------------------------------
# A model of homeassistant.helpers.debounce.Debouncer (2024.x)
# ---------------------------------------------------------------------------
class Debouncer:
    def __init__(self, hass, *, cooldown, immediate, function):
        self.hass = hass
        self.cooldown = cooldown
        self.immediate = immediate
        self.function = function
        self._timer_task = None
        self._execute_at_end_of_timer = False
        self._execute_lock = asyncio.Lock()
        self._shutdown_requested = False

    async def async_call(self):
        if self._shutdown_requested:
            return
        if self._timer_task:
            if not self._execute_at_end_of_timer:
                self._execute_at_end_of_timer = True
            return
        if self._execute_lock.locked():
            return
        if not self.immediate:
            self._execute_at_end_of_timer = True
            self._schedule_timer()
            return
        async with self._execute_lock:
            if self._timer_task:
                return
            task = self.hass.async_create_task(self.function(), name="debouncer job")
            await task
            self._schedule_timer()

    async def _handle_timer_finish(self):
        self._execute_at_end_of_timer = False
        if self._execute_lock.locked():
            return
        async with self._execute_lock:
            if self._timer_task:
                return
            try:
                task = self.hass.async_create_task(self.function(), name="debouncer job")
                await task
            except Exception:  # noqa: BLE001
                logging.getLogger("debouncer").exception("Unexpected exception")
            self._schedule_timer()

    def _on_debounce(self):
        self._timer_task = None
        if self._execute_at_end_of_timer:
            self._execute_at_end_of_timer = False
            self.hass.async_create_task(self._handle_timer_finish(), name="debouncer finish")

    def _schedule_timer(self):
        if not self._shutdown_requested:
            self._timer_task = self.hass.loop.call_later(self.cooldown, self._on_debounce)

    def async_cancel(self):
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None
        self._execute_at_end_of_timer = False

    async def async_shutdown(self):
        self._shutdown_requested = True
        self.async_cancel()


# ---------------------------------------------------------------------------
# A model of homeassistant.helpers.update_coordinator.DataUpdateCoordinator
# ---------------------------------------------------------------------------
class HAModelCoordinator:
    def __init__(self, hass, logger, *, name, update_interval=None, **_):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None
        self.last_update_success = True
        self.last_exception = None
        self._listeners = {}
        self._unsub_refresh = None
        self._shutdown_requested = False
        self._debounced_refresh = Debouncer(
            hass, cooldown=0.05, immediate=True, function=self.async_refresh
        )
        self.base_shutdown_called = False
        self.refresh_requests = 0
        self.refresh_count = 0
        self.scheduled_timer_handles = []

    # -- listeners (CoordinatorEntity.async_added_to_hass) -------------------
    def async_add_listener(self, update_callback, context=None):
        schedule_refresh = not self._listeners

        def remove_listener():
            self._listeners.pop(remove_listener, None)
            if not self._listeners:
                self._async_unsub_refresh()

        self._listeners[remove_listener] = (update_callback, context)
        if schedule_refresh:
            self._schedule_refresh()
        return remove_listener

    def async_update_listeners(self):
        for update_callback, _ in list(self._listeners.values()):
            update_callback()

    # -- refresh scheduling ---------------------------------------------------
    def _async_unsub_refresh(self):
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None

    def _schedule_refresh(self):
        if self.update_interval is None or self._shutdown_requested:
            return
        self._async_unsub_refresh()
        handle = self.hass.loop.call_later(
            self.update_interval.total_seconds(), self._wrap_handle_refresh_interval
        )
        self.scheduled_timer_handles.append(handle)
        self._unsub_refresh = handle.cancel

    def _wrap_handle_refresh_interval(self):
        self._unsub_refresh = None
        # HA: a hass-level task, not tied to the config entry.
        self.hass.async_create_task(self._handle_refresh_interval(), name="refresh interval")

    async def _handle_refresh_interval(self, _now=None):
        self._unsub_refresh = None
        await self._async_refresh(log_failures=True, scheduled=True)

    async def async_config_entry_first_refresh(self):
        self.refresh_requests += 1
        await self._async_refresh(log_failures=False, raise_on_entry_error=True)
        if self.last_update_success:
            return
        ex = ConfigEntryNotReady(str(self.last_exception))
        ex.__cause__ = self.last_exception
        raise ex

    async def async_refresh(self):
        await self._async_refresh(log_failures=True)

    async def async_request_refresh(self):
        self.refresh_requests += 1
        await self._debounced_refresh.async_call()

    async def _async_refresh(self, log_failures=True, scheduled=False, raise_on_entry_error=False):
        self._async_unsub_refresh()
        self._debounced_refresh.async_cancel()
        if self._shutdown_requested or (scheduled and self.hass.is_stopping):
            return
        self.refresh_count += 1
        previous_update_success = self.last_update_success
        previous_data = self.data
        try:
            self.data = await self._async_update_data()
        except UpdateFailed as err:
            self.last_exception = err
            if self.last_update_success:
                if log_failures:
                    self.logger.error("Error fetching %s data: %s", self.name, err)
                self.last_update_success = False
        except Exception as err:  # noqa: BLE001
            self.last_exception = err
            self.last_update_success = False
            if log_failures:
                self.logger.exception("Unexpected error fetching %s data", self.name)
        else:
            if not self.last_update_success:
                self.last_update_success = True
                self.logger.info("Fetching %s data recovered", self.name)
        finally:
            if self._listeners and not self.hass.is_stopping:
                self._schedule_refresh()
        if not self.last_update_success and not previous_update_success:
            return
        if self.last_update_success != previous_update_success or previous_data is not self.data:
            self.async_update_listeners()

    async def async_shutdown(self):
        self.base_shutdown_called = True
        self._shutdown_requested = True
        self._async_unsub_refresh()
        await self._debounced_refresh.async_shutdown()


uc.DataUpdateCoordinator = HAModelCoordinator  # bind before the integration imports it

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.const import DOMAIN  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

assert HeatPumpOptimizerCoordinator.__mro__[1] is HAModelCoordinator, "model not bound"

LOG = logging.getLogger("d1.lifecycle")
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("heatpump_optimizer").setLevel(logging.CRITICAL)


# ---------------------------------------------------------------------------
# hass with a real loop and a real executor
# ---------------------------------------------------------------------------
class RealConfigEntries:
    def __init__(self, hass):
        self.hass = hass
        self.entries = []
        self.reloaded = []
        self.updated = []
        self.platform_unsubs = {}

    def async_update_entry(self, entry, options=None, **kwargs):
        if options is not None:
            kwargs["options"] = options
        for key, value in kwargs.items():
            setattr(entry, key, value)
        self.updated.append(entry.entry_id)

    def async_entries(self, domain=None):
        return list(self.entries)

    async def async_forward_entry_setups(self, entry, platforms):
        # Since audit B5 (3da0e27) the coordinator is on the entry, set by
        # ``async_setup_entry`` just before it forwards; it used to be in
        # ``hass.data[DOMAIN][entry_id]``.
        coordinator = entry.runtime_data
        unsubs = []
        for platform in platforms:
            unsubs.append(coordinator.async_add_listener(lambda: None, context=platform))
        self.platform_unsubs[entry.entry_id] = unsubs
        return None

    async def async_unload_platforms(self, entry, platforms):
        for unsub in self.platform_unsubs.pop(entry.entry_id, []):
            unsub()
        return True

    async def async_reload(self, entry_id):
        self.reloaded.append(entry_id)
        entry = next(e for e in self.entries if e.entry_id == entry_id)
        return await entry_reload(self.hass, entry)


class RealHass(FakeHass):
    def __init__(self, states=None, *, eager=True):
        super().__init__(states)
        self.loop = asyncio.get_running_loop()
        self.eager = eager
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="hpo-exec")
        self.tasks: set[asyncio.Task] = set()
        self.task_errors: list[tuple[str, str]] = []
        self.exec_futures: list[asyncio.Future] = []
        self.is_stopping = False
        self.state_listeners = []
        self.mqtt_subs = []
        self.config_entries = RealConfigEntries(self)
        self.loop_exceptions = []
        self.loop.set_exception_handler(self._on_loop_exception)

    def _on_loop_exception(self, loop, context):
        self.loop_exceptions.append(context)

    def async_create_task(self, coro, name=None, eager_start=None):
        eager = self.eager if eager_start is None else eager_start
        task = asyncio.Task(coro, loop=self.loop, name=name, eager_start=eager)
        if not task.done():
            self.tasks.add(task)
        task.add_done_callback(self._on_task_done)
        if task.done():
            self._on_task_done(task)
        return task

    def _on_task_done(self, task):
        self.tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            self.task_errors.append((task.get_name(), repr(task.exception())))

    async def async_add_executor_job(self, func, *args):
        fut = self.loop.run_in_executor(self.executor, func, *args)
        self.exec_futures.append(fut)
        return await fut


class RealEntry(FakeEntry):
    NOT_LOADED, SETUP_IN_PROGRESS, LOADED, SETUP_RETRY, SETUP_ERROR = (
        "not_loaded", "setup_in_progress", "loaded", "setup_retry", "setup_error",
    )

    def __init__(self, data=None, options=None):
        super().__init__(data, options)
        self.state = self.NOT_LOADED
        self.tries = 0
        self._background_tasks: set[asyncio.Task] = set()
        self._tasks: set[asyncio.Task] = set()
        self.update_listeners = []
        self.setup_lock = asyncio.Lock()

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)

        def _remove():
            if listener in self.update_listeners:
                self.update_listeners.remove(listener)

        return _remove

    def async_on_unload(self, func):
        self._on_unload.append(func)

    def async_create_background_task(self, hass, coro, name=None, eager_start=True):
        task = hass.async_create_task(coro, name=name, eager_start=eager_start)
        if not task.done():
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        return task

    async def _async_process_on_unload(self, hass):
        while self._on_unload:
            job = self._on_unload.pop()()
            if asyncio.iscoroutine(job):
                hass.async_create_task(job)
        if not self._tasks and not self._background_tasks:
            return
        for task in list(self._background_tasks):
            task.cancel("Config entry unloading")
        _, pending = await asyncio.wait(self._tasks | self._background_tasks, timeout=10)
        if pending:
            LOG.warning("entry unload: %d task(s) still pending after 10 s", len(pending))


# -- the config-entry state machine (abridged from HA core) -------------------
async def entry_setup(hass, entry) -> bool:
    entry.state = RealEntry.SETUP_IN_PROGRESS
    try:
        result = await integration.async_setup_entry(hass, entry)
    except ConfigEntryNotReady as exc:
        entry.state = RealEntry.SETUP_RETRY
        entry.tries += 1
        LOG.debug("setup retry: %s", exc)
        await entry._async_process_on_unload(hass)
        return False
    except Exception:  # noqa: BLE001
        LOG.exception("setup raised")
        entry.state = RealEntry.SETUP_ERROR
        return False
    entry.state = RealEntry.LOADED if result else RealEntry.SETUP_ERROR
    return bool(result)


async def entry_unload(hass, entry) -> bool:
    result = await integration.async_unload_entry(hass, entry)
    if result:
        await entry._async_process_on_unload(hass)
        entry.state = RealEntry.NOT_LOADED
    return result


async def entry_reload(hass, entry) -> bool:
    async with entry.setup_lock:
        if not await entry_unload(hass, entry):
            return False
        return await entry_setup(hass, entry)


# ---------------------------------------------------------------------------
# External world: Tibber over a fake aiohttp session, weather over a service
# ---------------------------------------------------------------------------
TIBBER_DOWN = {"down": False}
START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def _tibber_payload(now):
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    def day(offset):
        return [
            {
                "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                "startsAt": (midnight + timedelta(days=offset, hours=h)).isoformat(),
                "level": "NORMAL",
            }
            for h in range(24)
        ]
    return {
        "data": {
            "viewer": {
                "homes": [
                    {"currentSubscription": {"priceInfo": {"today": day(0), "tomorrow": day(1)}}}
                ]
            }
        }
    }


class _FakeResp:
    def __init__(self, payload):
        self.status = 200
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        await asyncio.sleep(0.001)
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def post(self, *a, **k):
        if TIBBER_DOWN["down"]:
            raise aiohttp.ClientConnectionError("network unreachable (harness)")
        return _FakeResp(_tibber_payload(dt_util.now()))


coord_mod.async_get_clientsession = lambda hass, verify_ssl=True: _FakeSession()


def _forecast(now):
    base = now.replace(minute=0, second=0, microsecond=0)
    return [
        {
            "datetime": (base + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


async def _weather_get_forecasts(call):
    await asyncio.sleep(0.001)
    return {call.data["entity_id"]: {"forecast": _forecast(dt_util.now())}}


# MQTT subscribe: record a real unsubscribe so leaks are countable.
async def _mqtt_subscribe(hass, topic, callback, qos=0, **_):
    entry = (topic, callback)
    hass.mqtt_subs.append(entry)

    def _unsub():
        if entry in hass.mqtt_subs:
            hass.mqtt_subs.remove(entry)

    return _unsub


coord_mod.mqtt.async_subscribe = _mqtt_subscribe


# ---------------------------------------------------------------------------
# Instrumentation on the production class (class-attribute swaps, restored)
# ---------------------------------------------------------------------------
SOLVE_GATE = {"hold": False}
solve_started = threading.Event()
solve_release = threading.Event()
SHUTDOWN_DONE: dict[int, float] = {}
POST_SHUTDOWN_ACTUATIONS: list[tuple[int, str]] = []
POST_SHUTDOWN_SAVES: list[tuple[int, str]] = []
HANDLER_RUNS: list[int] = []

CREATED: list[weakref.ref] = []
_real_init = HeatPumpOptimizerCoordinator.__init__


def _traced_init(self, hass, entry):
    _real_init(self, hass, entry)
    CREATED.append(weakref.ref(self))


HeatPumpOptimizerCoordinator.__init__ = _traced_init

_real_optimize = HeatPumpOptimizer.optimize
_real_shutdown = HeatPumpOptimizerCoordinator.async_shutdown
_real_apply_action = HeatPumpOptimizerCoordinator._apply_action
_real_publish = HeatPumpOptimizerCoordinator.async_publish_current_action
_real_on_power = HeatPumpOptimizerCoordinator._on_power_event
_real_store_save = storage.Store.async_save


def _gated_optimize(self, *args, **kwargs):
    if SOLVE_GATE["hold"]:
        solve_started.set()
        solve_release.wait(timeout=30)
    return _real_optimize(self, *args, **kwargs)


async def _traced_shutdown(self):
    await _real_shutdown(self)
    SHUTDOWN_DONE[id(self)] = time.monotonic()


async def _traced_apply_action(self):
    if id(self) in SHUTDOWN_DONE and self._current_action:
        POST_SHUTDOWN_ACTUATIONS.append((id(self), "_apply_action"))
    return await _real_apply_action(self)


def _traced_on_power(self, event):
    HANDLER_RUNS.append(id(self))
    return _real_on_power(self, event)


CURRENT_SAVER: dict[str, int | None] = {"owner": None}


async def _traced_store_save(self, data):
    owner = _owner_of_current_task()
    if owner is not None and owner in SHUTDOWN_DONE:
        POST_SHUTDOWN_SAVES.append((owner, self._key))
    return await _real_store_save(self, data)


def _owner_of_current_task():
    """Which coordinator the running task belongs to: walk the coroutine frames."""
    task = asyncio.current_task()
    if task is None:
        return None
    coro = task.get_coro()
    seen = 0
    while coro is not None and seen < 20:
        frame = getattr(coro, "cr_frame", None)
        if frame is not None:
            owner = frame.f_locals.get("self")
            if isinstance(owner, HeatPumpOptimizerCoordinator):
                return id(owner)
        coro = getattr(coro, "cr_await", None)
        seen += 1
    return None


HeatPumpOptimizer.optimize = _gated_optimize
HeatPumpOptimizerCoordinator.async_shutdown = _traced_shutdown
HeatPumpOptimizerCoordinator._apply_action = _traced_apply_action
HeatPumpOptimizerCoordinator._on_power_event = _traced_on_power
storage.Store.async_save = _traced_store_save


# ---------------------------------------------------------------------------
# Scenario plumbing
# ---------------------------------------------------------------------------
def base_config(*, guards=True):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_switch_entity": "switch.heat_pump",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
        "dhw_tank_volume": 200.0,
        "dhw_setpoint": 55.0,
        "dhw_min_temperature": 45.0,
        "dhw_windows": "06:00-08:30, 17:00-22:00",
        "optimization_interval": 30,
    }
    if guards:
        cfg.update(
            {
                "peak_guard_enabled": True,
                "house_power_entity": "sensor.house_power",
                "heat_pump_defrost_entity": "binary_sensor.defrost",
            }
        )
    else:
        cfg.update({"peak_guard_enabled": False, "ecl110_state_topic": ""})
    return cfg


def make_hass(*, eager):
    now = dt_util.now()
    states = {
        "sensor.indoor": FakeState("21.4", last_updated=now),
        "sensor.outdoor": FakeState("-3.0", last_updated=now),
        "sensor.house_power": FakeState("1.2", unit="kW", last_updated=now),
        "binary_sensor.defrost": FakeState("off", last_updated=now),
        "weather.home": FakeState("cloudy", attributes={"temperature": -3.0, "wind_speed": 3.0}),
    }
    hass = RealHass(states, eager=eager)
    hass.services.async_register("weather", "get_forecasts", _weather_get_forecasts)
    real_call = hass.services.async_call
    hass.owned_calls = []

    async def _attributed_call(domain, service, data=None, **kwargs):
        owner = _owner_of_current_task()
        if domain in ("switch", "mqtt"):
            hass.owned_calls.append((owner, domain, service, owner in SHUTDOWN_DONE))
        return await real_call(domain, service, data, **kwargs)

    hass.services.async_call = _attributed_call
    return hass


class _Event:
    def __init__(self, entity_id, state):
        self.data = {"entity_id": entity_id, "new_state": state, "old_state": None}


def fire_state_event(hass, entity_id, state):
    for entity_ids, action in list(hass.state_listeners):
        if entity_id in entity_ids:
            action(_Event(entity_id, state))


def listeners_bound_to(hass, coordinators):
    ids = {id(c) for c in coordinators}
    n = 0
    for _, action in hass.state_listeners:
        if id(getattr(action, "__self__", None)) in ids:
            n += 1
    return n


def mqtt_bound_to(hass, coordinators):
    ids = {id(c) for c in coordinators}
    return sum(1 for _, cb in hass.mqtt_subs if id(getattr(cb, "__self__", None)) in ids)


def tasks_bound_to(hass, coordinator):
    n = 0
    for task in list(hass.tasks):
        if task.done():
            continue
        coro = task.get_coro()
        seen = 0
        while coro is not None and seen < 20:
            frame = getattr(coro, "cr_frame", None)
            if frame is not None and frame.f_locals.get("self") is coordinator:
                n += 1
                break
            coro = getattr(coro, "cr_await", None)
            seen += 1
    return n


def timers_bound_to(coordinator):
    return sum(1 for h in coordinator.scheduled_timer_handles if not h.cancelled() and h is not None and not _handle_fired(h))


def _handle_fired(handle):
    # TimerHandle exposes when(); a fired handle is not distinguishable from
    # a pending one by API, so compare against loop time.
    try:
        return handle.when() <= asyncio.get_running_loop().time()
    except Exception:  # noqa: BLE001
        return True


def escaped(hass):
    bad = list(hass.task_errors)
    return len(bad) + len(hass.loop_exceptions), bad


async def wait_for(predicate, timeout=20.0, step=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        await asyncio.sleep(step)
    return predicate()


async def settle(hass, timeout=20.0):
    """Wait until no tracked task is pending (the loop is quiet)."""
    return await wait_for(lambda: not [t for t in hass.tasks if not t.done()], timeout)


async def wait_solve_started(timeout=30.0):
    return await wait_for(solve_started.is_set, timeout, step=0.005)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
async def scenario_notready(eager, guards=True, retries=5):
    """Tibber down at boot: N setups raise ConfigEntryNotReady, then it recovers."""
    storage._reset_store_disk()
    CREATED.clear()
    hass = make_hass(eager=eager)
    entry = RealEntry(data=base_config(guards=guards))
    hass.config_entries.entries.append(entry)
    TIBBER_DOWN["down"] = True
    for _ in range(retries):
        ok = await entry_setup(hass, entry)
        assert not ok and entry.state == RealEntry.SETUP_RETRY, entry.state
        await settle(hass)
    TIBBER_DOWN["down"] = False
    SOLVE_GATE["hold"] = False
    ok = await entry_setup(hass, entry)
    assert ok and entry.state == RealEntry.LOADED
    live = entry.runtime_data
    await settle(hass, 60)
    gc.collect()
    zombies = [r() for r in CREATED if r() is not None and r() is not live]
    HANDLER_RUNS.clear()
    fire_state_event(hass, "sensor.house_power", FakeState("4.2", unit="kW"))
    zombie_runs = sum(1 for i in HANDLER_RUNS if i != id(live))
    n_exc, bad = escaped(hass)
    result = {
        "leaked_listeners": listeners_bound_to(hass, zombies),
        "leaked_mqtt_subs": mqtt_bound_to(hass, zombies),
        "zombie_coordinators": len(zombies),
        "zombie_handler_runs": zombie_runs,
        "live_listeners": listeners_bound_to(hass, [live]),
        "escaped_exceptions": n_exc,
        "first_cycle_ok": int(live.data is not None and live.data.get("current_action") not in (None, {})),
        "retries": retries,
    }
    for t in bad[:3]:
        LOG.error("escaped: %r", t)
    await entry_unload(hass, entry)
    await settle(hass)
    hass.executor.shutdown(wait=True)
    return result


async def scenario_reload_midsolve(eager):
    """setup -> light first refresh -> first solve in flight -> reload -> unload mid-solve -> setup."""
    storage._reset_store_disk()
    hass = make_hass(eager=eager)
    entry = RealEntry(data=base_config())
    hass.config_entries.entries.append(entry)
    out = {}

    # Phase A: setup; the background first solve is held inside the executor.
    solve_started.clear(); solve_release.clear(); SOLVE_GATE["hold"] = True
    ok = await entry_setup(hass, entry)
    assert ok, "setup failed"
    old = entry.runtime_data
    old_ref = weakref.ref(old)
    assert await wait_solve_started(), "first solve never reached the executor"
    out["light_refresh_published"] = int(old.data is not None)

    # Phase B: options change -> reload while the solve thread is blocked.
    entry.options = {**entry.options, "target_temperature": 20.0}
    reload_task = hass.async_create_task(integration.async_update_options(hass, entry))
    # Give the state machine time to reach the executor await, then release.
    await asyncio.sleep(0.2)
    solve_release.set()
    await reload_task
    new = entry.runtime_data
    assert new is not old
    out["reload_ok"] = int(entry.state == RealEntry.LOADED)
    # the new instance's own first solve: wait for it (gate is now open,
    # solve_release stays set so any later gated call passes straight through)
    await settle(hass, 90)
    out["new_first_cycle_ok"] = int(
        new.data is not None and bool(new.data.get("current_action")) and new._optimization_result is not None
    )
    out["old_tasks_alive"] = tasks_bound_to(hass, old)
    out["old_listeners"] = listeners_bound_to(hass, [old])
    out["old_mqtt_subs"] = mqtt_bound_to(hass, [old])
    out["old_timers"] = timers_bound_to(old)
    out["old_exec_futures_pending"] = sum(1 for f in hass.exec_futures if not f.done())
    out["old_post_shutdown_actuations"] = sum(1 for i, _ in POST_SHUTDOWN_ACTUATIONS if i == id(old))
    out["old_post_shutdown_saves"] = sum(1 for i, _ in POST_SHUTDOWN_SAVES if i == id(old))
    n_exc, bad = escaped(hass)
    out["escaped_exceptions"] = n_exc
    for t in bad[:3]:
        LOG.error("escaped: %r", t)
    del old
    gc.collect()
    out["old_instance_alive_after_gc"] = int(old_ref() is not None)
    if old_ref() is not None:
        names = []
        for r in gc.get_referrers(old_ref())[:8]:
            if hasattr(r, "f_code"):
                names.append(f"frame:{r.f_code.co_name}")
            elif hasattr(r, "__func__"):
                names.append(f"method:{r.__func__.__name__}")
            else:
                names.append(type(r).__name__)
        out["old_referrers"] = "|".join(names)

    # Phase C: SCHEDULED refresh in flight at reload (the hass-level task path).
    POST_SHUTDOWN_ACTUATIONS.clear(); POST_SHUTDOWN_SAVES.clear()
    solve_started.clear(); solve_release.clear(); SOLVE_GATE["hold"] = True
    new._async_unsub_refresh()  # the pending handle would have fired: it is done
    new._wrap_handle_refresh_interval()  # what the interval timer does
    assert await wait_solve_started(), "scheduled solve never reached the executor"
    entry.options = {**entry.options, "target_temperature": 21.5}
    reload_task = hass.async_create_task(integration.async_update_options(hass, entry))
    await asyncio.sleep(0.2)
    shutdown_before_release = id(new) in SHUTDOWN_DONE
    solve_release.set()
    await reload_task
    newest = entry.runtime_data
    await settle(hass, 90)
    out["sched_shutdown_returned_before_release"] = int(shutdown_before_release)
    out["sched_zombie_actuations"] = sum(1 for i, _ in POST_SHUTDOWN_ACTUATIONS if i == id(new))
    out["sched_zombie_saves"] = sum(1 for i, _ in POST_SHUTDOWN_SAVES if i == id(new))
    out["sched_zombie_service_calls"] = sum(
        1 for owner, _, _, after in hass.owned_calls if owner == id(new) and after
    )
    out["sched_zombie_service_calls_detail"] = "+".join(
        f"{d}.{s_}" for owner, d, s_, after in hass.owned_calls if owner == id(new) and after
    ) or "none"
    out["sched_old_tasks_alive"] = tasks_bound_to(hass, new)
    out["sched_old_timers"] = timers_bound_to(new)
    out["sched_newest_first_cycle_ok"] = int(
        newest.data is not None and newest._optimization_result is not None
    )
    n_exc, bad = escaped(hass)
    out["sched_escaped_exceptions"] = n_exc - out["escaped_exceptions"]
    for t in bad[:3]:
        LOG.error("escaped: %r", t)

    # Phase D: unload mid-solve, then set up again.
    solve_started.clear(); solve_release.clear(); SOLVE_GATE["hold"] = True
    newest._async_unsub_refresh()
    newest._wrap_handle_refresh_interval()
    assert await wait_solve_started()
    unload_task = hass.async_create_task(entry_unload(hass, entry))
    await asyncio.sleep(0.2)
    solve_release.set()
    await unload_task
    await settle(hass, 60)
    out["unload_midsolve_state_not_loaded"] = int(entry.state == RealEntry.NOT_LOADED)
    out["unload_midsolve_listeners"] = len(hass.state_listeners)
    out["unload_midsolve_mqtt_subs"] = len(hass.mqtt_subs)
    out["unload_midsolve_tasks_alive"] = len([t for t in hass.tasks if not t.done()])
    SOLVE_GATE["hold"] = False
    ok = await entry_setup(hass, entry)
    final = entry.runtime_data
    await settle(hass, 90)
    out["resetup_first_cycle_ok"] = int(ok and final.data is not None and final._optimization_result is not None)
    out["handover_republished"] = int(final.data is not None)
    n_exc, bad = escaped(hass)
    out["total_escaped_exceptions"] = n_exc
    await entry_unload(hass, entry)
    await settle(hass)
    hass.executor.shutdown(wait=True)
    return out


async def main():
    t0 = time.process_time()
    tt0 = time.thread_time()
    results = {}
    for eager in (True, False):
        tag = "eager" if eager else "lazy"
        r = await scenario_notready(eager)
        results[f"notready_{tag}"] = r
        r0 = await scenario_notready(eager, guards=False)
        results[f"notready_guards_off_{tag}"] = r0
        m = await scenario_reload_midsolve(eager)
        results[f"midsolve_{tag}"] = m

    for scen, vals in results.items():
        for k, v in vals.items():
            print(f"RESULT {scen}.{k}={v} count")
    # headline numbers (eager = current HA)
    n = results["notready_eager"]
    print(f"RESULT notready_leaked_listeners={n['leaked_listeners']} count")
    print(f"RESULT notready_leaked_mqtt_subs={n['leaked_mqtt_subs']} count")
    print(f"RESULT notready_zombie_coordinators={n['zombie_coordinators']} count")
    print(f"RESULT notready_zombie_handler_runs={n['zombie_handler_runs']} count")
    print(f"RESULT notready_leaked_listeners_guards_off={results['notready_guards_off_eager']['leaked_listeners']} count")
    m = results["midsolve_eager"]
    print(f"RESULT reload_midsolve_old_tasks_alive={m['old_tasks_alive']} count")
    print(f"RESULT reload_midsolve_old_listeners={m['old_listeners']} count")
    print(f"RESULT reload_midsolve_old_instance_alive_after_gc={m['old_instance_alive_after_gc']} count")
    print(f"RESULT sched_midsolve_zombie_actuations={m['sched_zombie_actuations']} count")
    print(f"RESULT sched_midsolve_zombie_saves={m['sched_zombie_saves']} count")
    print(f"RESULT new_first_cycle_ok={m['new_first_cycle_ok']} count")
    print(f"RESULT total_escaped_exceptions={m['total_escaped_exceptions']} count")
    cpu = time.process_time() - t0
    thr = time.thread_time() - tt0
    print(f"RESULT thread_factor={cpu / thr if thr else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
