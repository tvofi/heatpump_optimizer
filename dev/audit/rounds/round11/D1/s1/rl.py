"""Real-loop scaffolding shared by the D1-s1 round-11 harnesses (not a harness itself).

``RealHass`` subclasses ``tests/harness.py:FakeHass`` so that
``async_add_executor_job`` runs in a ``ThreadPoolExecutor`` on a real asyncio
loop and ``async_create_task`` schedules instead of closing (D1.md M1). The
stub's ``async_track_time_interval`` (a no-op) and ``async_call_later`` (a
recorded list nobody fires) are replaced by loop-backed versions that keep
every live registration in ``REGISTRY`` so a harness can ask what still
references a torn-down coordinator.

``ha_unload_faithful`` is Home Assistant's ``ConfigEntry.async_unload`` order
(homeassistant/config_entries.py, ``_async_process_on_unload``): the
integration's ``async_unload_entry``, then the ``async_on_unload`` callbacks
POPPED (last registered first), a returned coroutine scheduled as a task,
then the entry's background tasks cancelled and every task awaited.

Run from the repository root with PYTHONPATH=tests/hastub.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import asyncio
import gc
import inspect
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

sys.path.insert(0, "tests")
import harness  # noqa: E402  (inserts custom_components on sys.path)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402,F401

import homeassistant.helpers.event as ev  # noqa: E402

REGISTRY: dict[int, dict] = {}
_seq = [0]


def _site(depth: int = 2) -> str:
    """file:line of the first production frame above this helper."""
    f = sys._getframe(depth)
    while f is not None:
        fn = f.f_code.co_filename
        if "custom_components/heatpump_optimizer/" in fn:
            return f"{fn.split('custom_components/')[-1]}:{f.f_lineno}"
        f = f.f_back
    return "?"


SITES: list[tuple[str, str]] = []  # (kind, site) of every registration seen


def _register(kind: str, obj, cancel):
    _seq[0] += 1
    k = _seq[0]
    site = _site(3)
    SITES.append((kind, site))
    REGISTRY[k] = {"kind": kind, "obj": obj, "site": site, "cancel": cancel}

    def _unsub():
        rec = REGISTRY.pop(k, None)
        if rec and rec["cancel"]:
            rec["cancel"]()
    return _unsub


def _real_interval(hass, action, interval, *a, **k):
    loop = asyncio.get_running_loop()
    secs = interval.total_seconds() if isinstance(interval, timedelta) else float(interval)
    holder = {}

    def fire():
        res = action(None)
        if inspect.iscoroutine(res):
            hass.async_create_task(res)
        holder["h"] = loop.call_later(secs, fire)

    holder["h"] = loop.call_later(secs, fire)
    return _register("async_track_time_interval", action, lambda: holder["h"].cancel())


def _real_call_later(hass, delay, action):
    if not (getattr(action, "_hass_callback", False) or inspect.iscoroutinefunction(action)):
        raise TypeError(f"{action!r} is neither @callback nor a coroutine function")
    loop = asyncio.get_running_loop()
    secs = delay.total_seconds() if isinstance(delay, timedelta) else float(delay)
    box = {}

    def fire():
        REGISTRY.pop(box.get("k"), None)
        res = action(None)
        if inspect.iscoroutine(res):
            hass.async_create_task(res)

    h = loop.call_later(secs, fire)
    unsub = _register("async_call_later", action, h.cancel)
    box["k"] = _seq[0]
    return unsub


_stub_state = ev.async_track_state_change_event


def _tracked_state(hass, entity_ids, action):
    unsub = _stub_state(hass, entity_ids, action)
    k = _register("async_track_state_change_event", action, unsub)
    return k


ev.async_track_time_interval = _real_interval
ev.async_call_later = _real_call_later
ev.async_track_state_change_event = _tracked_state


def patch_imported(*modules) -> None:
    """Rebind the helpers in modules that imported them by name."""
    for m in modules:
        for name, fn in (("async_track_time_interval", _real_interval),
                         ("async_call_later", _real_call_later),
                         ("async_track_state_change_event", _tracked_state)):
            if hasattr(m, name):
                setattr(m, name, fn)


DELIBERATE = [0.0]  # CPU seconds spent on the executor threads (deliberate second-thread work)


def _timed(func, *args):
    t = time.thread_time()
    try:
        return func(*args)
    finally:
        DELIBERATE[0] += time.thread_time() - t


class RealHass(FakeHass):
    """FakeHass on a real loop: a pooled executor, tasks that run."""

    def __init__(self, states=None, workers: int = 4) -> None:
        super().__init__(states)
        self.loop = asyncio.get_running_loop()
        self.executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="hass-exec")
        self.tasks: set = set()
        self.executor_futures: set = set()
        self.executor_jobs: list = []  # (fn qualname, site, future, (fn, args))
        self._bus_listen_once = self.bus.async_listen_once
        self.bus.async_listen_once = self._listen_once
        self.fired: list = []
        self.bus.async_fire = lambda event_type, data=None, *a, **k: self.fired.append((event_type, data))

    def _listen_once(self, event_type, listener):
        SITES.append(("async_listen_once", _site(2)))
        return self._bus_listen_once(event_type, listener)

    def async_create_task(self, coro, name=None, eager_start=True):
        t = self.loop.create_task(coro, name=name)
        t.hpo_site = _site(2)
        self.tasks.add(t)
        SITES.append(("async_create_task", _site(2)))
        t.add_done_callback(self.tasks.discard)
        return t

    def async_create_background_task(self, coro, name=None, eager_start=True):
        return self.async_create_task(coro, name=name)

    async def async_add_executor_job(self, func, *args):
        fut = self.loop.run_in_executor(self.executor, _timed, func, *args)
        self.executor_futures.add(fut)
        site = _site(2)
        SITES.append(("async_add_executor_job", site))
        self.executor_jobs.append((getattr(func, "__qualname__", repr(func)), site, fut, (func, args)))
        fut.add_done_callback(self.executor_futures.discard)
        return await fut


class RecordingEntry(FakeEntry):
    """FakeEntry whose update listener is kept, as upstream's is."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.update_listeners: list = []
        self.minor_version = 1

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)
        SITES.append(("add_update_listener", _site(2)))

        def _remove():
            if listener in self.update_listeners:
                self.update_listeners.remove(listener)
        return _remove

    def async_on_unload(self, func):
        SITES.append(("async_on_unload", _site(2)))
        self._on_unload.append(func)


async def ha_unload_faithful(integration, hass, entry):
    """``ConfigEntry.async_unload`` + ``_async_process_on_unload``, upstream's order."""
    ok = await integration.async_unload_entry(hass, entry)
    scheduled = 0
    if ok:
        tasks = []
        while entry._on_unload:
            job = entry._on_unload.pop()()
            if job is not None and inspect.isawaitable(job):
                scheduled += 1
                tasks.append(hass.async_create_task(job))
        if tasks:
            await asyncio.gather(*(asyncio.shield(t) for t in tasks))
        if hasattr(entry, "runtime_data"):
            delattr(entry, "runtime_data")
        entry.state = harness.ConfigEntryState.NOT_LOADED
    return ok, scheduled


def reaches(root, target, limit: int = 60000, skip_ids=()) -> bool:
    """Whether ``target`` is reachable from ``root`` over gc referents (bounded BFS).

    ``skip_ids`` are never traversed (the hass and the entry: every coordinator
    is reachable through them, so a path over them says nothing of the holder).
    """
    tid = id(target)
    # Module namespaces are not traversed either: a function's __globals__ would
    # otherwise reach every coordinator a module-level table holds.
    seen = {id(root), *skip_ids, *(id(vars(m)) for m in list(sys.modules.values()) if m is not None)}
    try:  # nor the loop, whose ready/scheduled queues hold every instance's callbacks
        seen.add(id(asyncio.get_running_loop()))
    except RuntimeError:
        pass
    q = [root]
    i = 0
    skip = (types.ModuleType, type)
    while i < len(q) and len(seen) < limit:
        o = q[i]
        i += 1
        for r in gc.get_referents(o):
            if id(r) == tid:
                return True
            if isinstance(r, skip) or id(r) in seen:
                continue
            if isinstance(r, (str, bytes, int, float)):
                continue
            seen.add(id(r))
            q.append(r)
    return False


def env_results(t_cpu0: float, p_cpu0: float, deliberate: float | None = None) -> None:
    if deliberate is None:
        deliberate = DELIBERATE[0]
    tc = time.thread_time() - t_cpu0
    pc = time.process_time() - p_cpu0
    tf = (pc - deliberate) / tc if tc > 0 else 1.0
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT deliberate_thread_cpu={deliberate:.3f} s")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            sw = next((int(l.split()[1]) for l in f if l.startswith("pswpin ")), 0)
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw}")
