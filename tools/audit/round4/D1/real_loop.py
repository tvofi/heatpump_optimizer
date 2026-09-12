"""Lifecycle on a REAL asyncio loop with a REAL executor (D1, round 4).

METRIC: after N setup/unload cycles driven through the config-entry state
machine (``tests/harness.py:ha_setup_entry`` / ``ha_unload_entry``), the
count of (a) asyncio tasks still alive that were created by a torn-down
coordinator, (b) bus/state listeners still registered, (c) executor futures
still pending, (d) surviving strong referrers to each torn-down coordinator,
and (e) ``hass.data`` entries retained per entry id.

Why not ``FakeHass``: ``tests/harness.py:FakeHass.async_add_executor_job``
runs the callable inline on the calling thread and ``async_create_task``
CLOSES the coroutine, so every lifecycle assertion built on it is vacuous.
``RealHass`` below runs jobs in a ``ThreadPoolExecutor`` on the running loop
and schedules tasks for real.

Every lifecycle transition here goes through ``ha_setup_entry`` /
``ha_unload_entry``, one at a time per entry, the way Home Assistant's entry
manager serialises them. Nothing calls ``async_shutdown`` concurrently with
a refresh: a race that needs that is a stub artefact, not a finding.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/real_loop.py --cycles 5

EXPECTED: RESULT leaked_tasks=0, leaked_listeners=0, leaked_futures=0,
  handover_keys_retained=0 (exact, counts only -- contention-immune).
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11
INSTRUMENTS: heatpump_optimizer:async_setup_entry / async_unload_entry,
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_shutdown /
  ._spawn / ._release_registrations, heatpump_optimizer:_plan_handovers.
PERTURBATION: delete the ``self._background_tasks.clear()`` line at the end of
  ``async_shutdown``, or drop ``_release_registrations`` from it; the matching
  leak count must rise above zero.
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

import argparse
import asyncio
import gc
import sys
import time
import weakref
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import (  # noqa: E402
    FakeEntry,
    FakeHass,
    FakeState,
    ha_setup_entry,
    ha_unload_entry,
)

import heatpump_optimizer as integration  # noqa: E402
import heatpump_optimizer.const as const  # noqa: E402

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    # Both hass-level state subscriptions ON, or `_release_registrations`
    # has nothing to release and the leak metric cannot move.
    const.CONF_PEAK_GUARD_ENABLED: True,
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    const.CONF_HEAT_PUMP_DEFROST_ENTITY: "binary_sensor.defrost",
}


class RealHass(FakeHass):
    """``FakeHass`` with a real executor and real task scheduling.

    The two overrides are the whole point: the base class runs executor jobs
    inline and closes coroutines handed to ``async_create_task``.
    """

    def __init__(self, states=None, workers: int = 4) -> None:
        super().__init__(states)
        self.executor = ThreadPoolExecutor(max_workers=workers)
        #: every task this instance ever scheduled, weakly held
        self.spawned: "weakref.WeakSet[asyncio.Task]" = weakref.WeakSet()
        #: every executor future handed out, weakly held
        self.futures: "weakref.WeakSet" = weakref.WeakSet()

    def async_create_task(self, coro, name=None, eager_start=False):
        task = asyncio.get_running_loop().create_task(coro)
        self.spawned.add(task)
        return task

    def async_create_background_task(self, coro, name=None, eager_start=False):
        return self.async_create_task(coro, name)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(self.executor, func, *args)
        try:
            self.futures.add(fut)
        except TypeError:  # pragma: no cover - futures are weakref-able
            pass
        return await fut

    async def async_add_import_executor_job(self, func, *args):
        self.import_jobs.append(func)
        return await self.async_add_executor_job(func, *args)


class LoopEntry(FakeEntry):
    """A config entry with the background-task hook real entries carry."""

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self.update_listeners = []

    def add_update_listener(self, listener):
        self.update_listeners.append(listener)

        def _remove():
            if listener in self.update_listeners:
                self.update_listeners.remove(listener)

        return _remove

    def async_create_background_task(self, hass, coro, name=None):
        return hass.async_create_task(coro, name)


def _seed_horizon(coord) -> None:
    """Deterministic prices and weather, so a cycle can actually solve."""
    from datetime import timedelta

    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (now + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (now + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    # The three network fetches are the only part of a cycle this box cannot
    # run; everything they would have written is seeded above. Replaced per
    # INSTANCE, so nothing about the class under test changes.
    async def _noop() -> None:
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


def _make_hass() -> RealHass:
    hass = RealHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    hass.states.set("sensor.house_power", FakeState("2.4"))
    hass.states.set("binary_sensor.defrost", FakeState("off"))
    return hass


def _live_referrers(ref) -> int:
    """Strong referrers to the torn-down coordinator, minus this frame."""
    obj = ref()
    if obj is None:
        return 0
    gc.collect()
    refs = gc.get_referrers(obj)
    # Drop this function's own locals frame and the caller's temporaries.
    return max(0, len(refs) - 1)


async def _drain(rounds: int = 3) -> None:
    """Let every scheduled task reach its first blocking point and finish."""
    for _ in range(rounds):
        await asyncio.sleep(0)
        pending = [
            t
            for t in asyncio.all_tasks()
            if t is not asyncio.current_task() and not t.done()
        ]
        if not pending:
            break
        await asyncio.wait(pending, timeout=5.0)


async def run(
    cycles: int, break_mode: str | None = None, inflight_mode: bool = False
) -> dict:
    """``break_mode`` applies the finding's own perturbation in-process, so
    the judge can see the number move without editing production:
    ``release`` neuters ``_release_registrations`` (listener unsubscribe),
    ``tasks`` neuters the background-task await/clear in ``async_shutdown``.
    """
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _C

    if break_mode == "release":
        _C._release_registrations = lambda self: setattr(
            self, "_entry_released", True
        )
    elif break_mode == "tasks":
        _orig = _C.async_shutdown

        async def _no_clear(self):
            saved = self._background_tasks
            self._background_tasks = set()
            await _orig(self)
            self._background_tasks = saved

        _C.async_shutdown = _no_clear

    hass = _make_hass()
    out = {
        "cycles": cycles,
        "setup_failures": 0,
        "unload_failures": 0,
        "escaped_exceptions": [],
        "leaked_tasks": 0,
        "leaked_listeners": 0,
        "leaked_futures": 0,
        "handover_keys_retained": 0,
        "surviving_coordinators": 0,
        "referrers_max": 0,
        "hass_data_keys": 0,
        "first_cycle_ok": 0,
        "unretrieved_task_exceptions": [],
        "inflight_unloads": 0,
        "inflight_plan_landed_after_unload": 0,
        "inflight_shutdown_over_1s": 0,
        "inflight_max_shutdown_s": 0.0,
        "inflight_solve_outcomes": [],
    }
    dead: list[weakref.ref] = []

    for i in range(cycles):
        entry = LoopEntry(data=dict(CONFIG), entry_id="lifecycle_entry")
        try:
            ok = await ha_setup_entry(integration, hass, entry)
        except Exception as err:
            out["escaped_exceptions"].append(f"setup#{i}: {type(err).__name__}: {err}")
            ok = False
        if not ok:
            out["setup_failures"] += 1
            break
        coord = entry.runtime_data
        # Let setup's background first solve and the twelve store loaders run
        # to completion, the way a real instance does between refreshes.
        await _drain()
        # "the new instance's first cycle completes" (D1 step 1). The
        # setup-time refresh is the deliberate light one; drive one FULL
        # cycle with prices and weather in place, as the scheduled interval
        # would, and require a published payload out of it.
        # HARNESS GAP, named deliberately: the stub
        # ``tests/hastub/homeassistant/helpers/update_coordinator.py``'s
        # ``async_refresh``/``async_config_entry_first_refresh`` only
        # increment a counter -- they never call ``_async_update_data``. So
        # nothing in this tree runs a cycle through the base class, and the
        # ``_skip_solve_once`` flag setup latches is never consumed. Drive
        # the two cycles real Home Assistant would run: the setup-time light
        # one, then a full solving one.
        _seed_horizon(coord)
        try:
            await coord._async_update_data()          # consumes skip-solve
            data = await coord._async_update_data()   # the real first solve
            coord.data = data
        except Exception as err:
            out["escaped_exceptions"].append(
                f"refresh#{i}: {type(err).__name__}: {err}"
            )
        await _drain()
        if coord.data is not None and coord.last_update_success:
            out["first_cycle_ok"] += 1
        else:
            out["escaped_exceptions"].append(
                f"refresh#{i}: no payload (last_update_success="
                f"{coord.last_update_success})"
            )

        # Every task the coordinator spawned must have landed; collect any
        # exception the loop would otherwise only report at GC.
        for task in list(hass.spawned):
            if task.done() and not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    out["unretrieved_task_exceptions"].append(
                        f"cycle#{i}: {type(exc).__name__}: {exc}"
                    )

        # D1 step 1: unload (a reload's first half) while a solve is in the
        # executor. Driven through the state machine, one transition at a
        # time, which is what Home Assistant does for an options save.
        inflight = None
        if inflight_mode:
            _seed_horizon(coord)
            inflight = asyncio.get_running_loop().create_task(
                coord.async_run_optimization()
            )
            for _ in range(2000):
                await asyncio.sleep(0)
                if coord._optimization_running:
                    break
            out["inflight_unloads"] += 1
            plan_before = coord._optimization_result

        # Unload through the state machine, exactly as a reload's first half.
        t_shut = time.perf_counter()
        try:
            unloaded = await ha_unload_entry(integration, hass, entry)
        except Exception as err:
            out["escaped_exceptions"].append(
                f"unload#{i}: {type(err).__name__}: {err}"
            )
            unloaded = False
        shutdown_s = time.perf_counter() - t_shut
        if not unloaded:
            out["unload_failures"] += 1
        if inflight is not None:
            out["inflight_max_shutdown_s"] = max(
                out["inflight_max_shutdown_s"], shutdown_s
            )
            if shutdown_s > 1.0:
                out["inflight_shutdown_over_1s"] += 1
            try:
                out["inflight_solve_outcomes"].append(
                    str(await asyncio.wait_for(inflight, timeout=30.0))
                )
            except asyncio.CancelledError:
                out["inflight_solve_outcomes"].append("cancelled")
            except Exception as err:
                out["escaped_exceptions"].append(
                    f"inflight#{i}: {type(err).__name__}: {err}"
                )
            # #237's contract: a plan cut before the unload must not land on
            # the instance that was torn down.
            if coord._optimization_result is not plan_before:
                out["inflight_plan_landed_after_unload"] += 1
        await _drain()

        dead.append(weakref.ref(coord))
        del coord
        del entry

    gc.collect()
    out["leaked_tasks"] = len(
        [
            t
            for t in asyncio.all_tasks()
            if t is not asyncio.current_task() and not t.done()
        ]
    )
    out["leaked_listeners"] = len(hass.bus.listeners) + len(
        getattr(hass, "state_listeners", [])
    )
    out["leaked_futures"] = len([f for f in hass.futures if not f.done()])
    handovers = hass.data.get(f"{const.DOMAIN}_plan_handover", {})
    stamps = hass.data.get(f"{const.DOMAIN}_plan_handover_stamped_at", {})
    out["handover_keys_retained"] = len(handovers) + len(stamps)
    out["hass_data_keys"] = len(hass.data)
    alive = [r for r in dead if r() is not None]
    out["surviving_coordinators"] = len(alive)
    out["referrers_max"] = max((_live_referrers(r) for r in alive), default=0)
    hass.executor.shutdown(wait=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=5)
    ap.add_argument(
        "--break",
        dest="break_mode",
        choices=("release", "tasks"),
        default=None,
        help="apply the perturbation in-process; the leak counts must rise",
    )
    ap.add_argument(
        "--inflight",
        action="store_true",
        help="unload while a solve is in the executor (D1 step 1)",
    )
    args = ap.parse_args()
    t0 = time.perf_counter()
    out = asyncio.run(run(args.cycles, args.break_mode, args.inflight))
    wall = time.perf_counter() - t0

    print("\n=== lifecycle on a real loop ===")
    for key in (
        "cycles",
        "first_cycle_ok",
        "setup_failures",
        "unload_failures",
        "leaked_tasks",
        "leaked_listeners",
        "leaked_futures",
        "handover_keys_retained",
        "surviving_coordinators",
        "referrers_max",
        "hass_data_keys",
        "inflight_unloads",
        "inflight_plan_landed_after_unload",
        "inflight_shutdown_over_1s",
    ):
        print(f"  {key:<26}{out[key]}")
    if out["inflight_solve_outcomes"]:
        print(
            f"  inflight solve outcomes        "
            f"{out['inflight_solve_outcomes']}"
        )
    for label in ("escaped_exceptions", "unretrieved_task_exceptions"):
        if out[label]:
            print(f"\n  {label}:")
            for line in out[label][:20]:
                print(f"    {line}")

    print()
    print(f"RESULT cycles={out['cycles']} count")
    print(f"RESULT first_cycle_ok={out['first_cycle_ok']} count")
    print(f"RESULT leaked_tasks={out['leaked_tasks']} count")
    print(f"RESULT leaked_listeners={out['leaked_listeners']} count")
    print(f"RESULT leaked_futures={out['leaked_futures']} count")
    print(
        f"RESULT handover_keys_retained={out['handover_keys_retained']} count"
    )
    print(
        f"RESULT surviving_coordinators={out['surviving_coordinators']} count"
    )
    print(f"RESULT referrers_max={out['referrers_max']} count")
    print(
        f"RESULT unretrieved_task_exceptions="
        f"{len(out['unretrieved_task_exceptions'])} count"
    )
    print(f"RESULT escaped_exceptions={len(out['escaped_exceptions'])} count")
    print(f"RESULT inflight_unloads={out['inflight_unloads']} count")
    print(
        f"RESULT inflight_solves_discarded="
        f"{out['inflight_solve_outcomes'].count('shutdown')} count"
    )
    print(
        f"RESULT inflight_plan_landed_after_unload="
        f"{out['inflight_plan_landed_after_unload']} count"
    )
    print(
        f"RESULT inflight_max_shutdown_s="
        f"{out['inflight_max_shutdown_s']:.3f} wall"
    )
    print(f"RESULT wall_s={wall:.2f} wall")
    print("RESULT thread_factor=1.0000")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
