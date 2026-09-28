"""D1 lifecycle on a REAL loop: setup -> refresh -> unload mid-solve -> setup again.

METRIC (one line): after N complete entry lifecycles (setup, first refresh,
a refresh whose solve is still parked in the executor when the entry unloads,
setup again), how many of each of these are left behind — live asyncio tasks
holding the torn-down coordinator, `hass` state listeners, bus listeners,
entries in the plan-handover dict, and escaped exceptions.

WHY A REAL LOOP: `tests/harness.py:FakeHass.async_add_executor_job` runs the
job INLINE on the calling thread, so a solve is never "in flight" and the race
this measures cannot exist; and `FakeHass.async_create_task` CLOSES the
coroutine, so none of the 13 store loaders the constructor spawns ever runs.
`d1lib.RealLoopHass` gives both a real `ThreadPoolExecutor` and real
`loop.create_task`. Every lifecycle transition below goes through
`tests/harness.py:ha_setup_entry` / `ha_unload_entry`, which are the
config-entry state machine's own order (state -> SETUP_IN_PROGRESS ->
async_setup_entry -> LOADED; unload -> async_unload_entry -> on_unload
callbacks -> runtime_data deleted -> NOT_LOADED). Nothing here calls a
lifecycle method outside that order.

THE IN-FLIGHT SOLVE is produced by monkeypatching
`heatpump_optimizer.coordinator:_run_in_process` — the function that runs on the
executor thread — to block for `--solve-seconds`. The loop stays free, which is
exactly the real shape: the solve holds a worker while an options save reloads
the entry (the case `coordinator.py`'s #237 comments name).

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/lifecycle_realloop.py

EXPECTED (baseline ae36eff, 8-core M1, python 3.11.5):
  RESULT lifecycles=3
  RESULT escaped_exceptions=0                     tolerance: exact
  RESULT state_listeners_after=0                  tolerance: exact
  RESULT bus_listeners_after=0                    tolerance: exact
  RESULT live_tasks_referencing_dead_coord=0      tolerance: exact
  RESULT dead_coordinators_alive=0                tolerance: exact
  RESULT actuations_after_release=0               tolerance: exact
  RESULT plan_handover_entries_after_plain_unload=1   <-- the leak, see report
  RESULT new_instance_first_cycle_ok=1            tolerance: exact
  Counts only; no wall/CPU number is claimed.

PERTURBATION (built in): `--no-latch` monkeypatches `_entry_released` to stay
False (it removes the #237 latch), so `actuations_after_release` must move
0 -> >=1 (up). That is the guard this harness proves is load-bearing.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6, python 3.11.5
"""
from __future__ import annotations

import argparse
import asyncio
import gc
import os
import sys
import time

sys.path.insert(0, "tools/audit/round3/D1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import d1lib  # noqa: E402
from datetime import timedelta  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402


def _in_past(stamp, when) -> bool:
    from homeassistant.util import dt as dt_util

    parsed = dt_util.parse_datetime(stamp) if isinstance(stamp, str) else stamp
    return parsed is not None and parsed < when


class SlowSolve:
    """Stands in for `coordinator._run_in_process`: blocks a real executor
    thread for `seconds`, then answers with what the real route would."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self.started = 0
        self.finished = 0

    def __call__(self, fn, args):
        self.started += 1
        time.sleep(self.seconds)
        try:
            return fn(*args)
        finally:
            self.finished += 1


async def one_lifecycle(
    hass, entry, slow, actuations, report: dict, no_plan: bool = False,
    complete_solve: bool = False,
) -> None:
    ok = await ha_setup_entry(integration, hass, entry)
    report["setup_ok"] = report.get("setup_ok", 0) + (1 if ok else 0)
    coord = entry.runtime_data
    d1lib.inject_inputs(coord, hours=12)
    d1lib.stub_fetches(coord)

    # `tests/hastub`'s DataUpdateCoordinator counts `async_config_entry_first_refresh`
    # instead of running it, so the light first refresh is driven here — and its
    # result assigned to `.data`, which is what the real base class does and what
    # `async_unload_entry` reads for the plan handover.
    coord.data = None if no_plan else await coord._async_update_data()

    # A scheduled refresh, started as its own task the way Home Assistant's
    # update-interval timer starts one, then left parked in the executor.
    async def _refresh():
        result = await coord._async_update_data()
        if not no_plan:
            coord.data = result

    refresh = asyncio.get_running_loop().create_task(_refresh())
    for _ in range(400):
        await asyncio.sleep(0.02)
        if slow.started > report.get("_solves_seen", 0):
            break
    report["_solves_seen"] = slow.started
    if complete_solve:
        await refresh

    # ... and the options save lands here, mid-solve.
    unloaded = await ha_unload_entry(integration, hass, entry)
    report["unload_ok"] = report.get("unload_ok", 0) + (1 if unloaded else 0)
    at_unload = actuations["n"]

    try:
        await asyncio.wait_for(asyncio.shield(refresh), timeout=30)
    except asyncio.CancelledError:
        report["refresh_cancelled"] = report.get("refresh_cancelled", 0) + 1
    except asyncio.TimeoutError:
        report["refresh_timeout"] = report.get("refresh_timeout", 0) + 1
    except Exception as err:  # noqa: BLE001
        report.setdefault("escaped", []).append(f"{type(err).__name__}: {err}")
    # Every service call the in-flight refresh made AFTER the entry was
    # unloaded. This is the #237 latch's whole job, on the path that reaches
    # it: the solve returns into a coordinator whose entry is gone.
    report["after_release"] = report.get("after_release", 0) + (
        actuations["n"] - at_unload
    )

    # Anything the coordinator spawned, given a chance to land.
    pending = [t for t in hass.created_tasks if not t.done()]
    if pending:
        done, still = await asyncio.wait(pending, timeout=10)
        for task in done:
            exc = task.exception() if not task.cancelled() else None
            if exc is not None:
                report.setdefault("escaped", []).append(
                    f"task {type(exc).__name__}: {exc}"
                )
    report.setdefault("dead", []).append(coord)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lifecycles", type=int, default=3)
    ap.add_argument("--solve-seconds", type=float, default=1.5)
    ap.add_argument("--no-latch", action="store_true")
    ap.add_argument(
        "--no-plan",
        action="store_true",
        help="perturbation: the coordinator publishes nothing, so "
        "async_unload_entry has no payload to stash; the handover counts "
        "must go to zero",
    )
    ap.add_argument("--gap-days", type=float, default=7.0)
    ap.add_argument(
        "--complete-solve",
        action="store_true",
        help="let the refresh finish before the unload, so the stashed "
        "handover carries a real solved plan (this is what makes the "
        "republished-after-a-gap numbers meaningful)",
    )
    args = ap.parse_args()

    slow = SlowSolve(args.solve_seconds)
    coord_mod._run_in_process = slow
    if args.no_latch:
        # The #237 latch, removed: every actuation point stops declining.
        coord_mod.HeatPumpOptimizerCoordinator._entry_released = property(
            lambda self: False, lambda self, value: None
        )
        print("MODE no-latch (the #237 shutdown latch is disabled)")
    else:
        print("MODE baseline")

    hass = d1lib.make_hass(workers=6)
    config = dict(d1lib.BASE_CONFIG)
    # A configured supply switch is what makes `_apply_action` reach
    # `hass.services.async_call`; without one the actuation count is vacuous.
    config["heat_pump_switch_entity"] = "switch.heat_pump"
    entry = FakeEntry(data=config)
    report: dict = {}

    # Every write to the world an actuation makes, counted.
    actuations = {"n": 0}
    original_call = hass.services.async_call

    async def _counting_call(domain, service, data=None, **kw):
        actuations["n"] += 1
        return await original_call(domain, service, data=data, **kw)

    hass.services.async_call = _counting_call

    if args.no_plan:
        print("MODE no-plan (the coordinator publishes nothing to stash)")
    for _ in range(args.lifecycles):
        await one_lifecycle(
            hass, entry, slow, actuations, report, args.no_plan,
            args.complete_solve,
        )
    actuations_during = actuations["n"]

    # A plain unload with no setup after it: the entry was disabled or
    # removed. Nothing pops the handover the unload stashed.
    handover_key = integration._PLAN_HANDOVER_KEY
    handover_after = len(hass.data.get(handover_key, {}))
    handover_bytes = sum(
        len(repr(v)) for v in hass.data.get(handover_key, {}).values()
    )

    actuations_after_release = report.get("after_release", 0)

    # The entry was disabled, or its setup kept failing, and comes back
    # `--gap-days` later. `async_setup_entry` pops the handover unconditionally
    # and `_async_first_refresh_light` returns it "as-is, with no fetches at
    # all" — so what is republished is the plan from before the gap.
    from homeassistant.util import dt as dt_util

    gap_hours = None
    stashed = dict(hass.data.get(handover_key, {}))
    if stashed:
        payload = next(iter(stashed.values()))
        last_opt = payload.get("last_optimization")
        print(f"RESULT stashed_plan_stale_flag={payload.get('plan_stale')}")
        print(
            "RESULT stashed_plan_age_minutes="
            f"{payload.get('plan_age_minutes')}"
        )
        far = dt_util.now() + timedelta(days=args.gap_days)
        dt_util.freeze(far)
        ok_gap = await ha_setup_entry(integration, hass, entry)
        gap_coord = entry.runtime_data if ok_gap else None
        republished = None
        if gap_coord is not None:
            d1lib.stub_fetches(gap_coord)
            republished = await gap_coord._async_update_data()
        dt_util.freeze(None)
        if republished is not None:
            same = republished.get("last_optimization") == last_opt
            stamp = republished.get("last_optimization")
            parsed = (
                dt_util.parse_datetime(stamp) if isinstance(stamp, str) else stamp
            )
            if parsed is not None:
                gap_hours = round((far - parsed).total_seconds() / 3600.0, 1)
            print(
                f"RESULT republished_plan_is_the_prereload_one="
                f"{1 if same else 0}"
            )
            print(f"RESULT republished_plan_age_hours={gap_hours}")
            print(
                "RESULT republished_plan_optimization_status="
                f"{republished.get('optimization_status')!r}"
            )
            print(
                "RESULT republished_plan_next_optimization_in_past="
                f"{1 if _in_past(republished.get('next_optimization'), far) else 0}"
            )
            print(
                "RESULT republished_plan_stale_flag="
                f"{republished.get('plan_stale')}"
            )
            print(
                "RESULT republished_plan_age_minutes_published="
                f"{republished.get('plan_age_minutes')}"
            )
            print(
                "RESULT republished_plan_true_age_minutes="
                f"{round(gap_hours * 60.0, 1) if gap_hours is not None else None}"
            )
        await ha_unload_entry(integration, hass, entry)
        hass.data.get(handover_key, {}).clear()

    # A fresh instance must still come up and complete a cycle.
    ok = await ha_setup_entry(integration, hass, entry)
    fresh = entry.runtime_data if ok else None
    first_cycle_ok = 0
    if fresh is not None:
        d1lib.inject_inputs(fresh, hours=12)
        d1lib.stub_fetches(fresh)
        try:
            data = await fresh._async_update_data()
            first_cycle_ok = 1 if isinstance(data, dict) and data else 0
        except Exception as err:  # noqa: BLE001
            report.setdefault("escaped", []).append(
                f"fresh cycle {type(err).__name__}: {err}"
            )
    await ha_unload_entry(integration, hass, entry)

    # What is still alive and still points at a torn-down coordinator.
    await asyncio.sleep(0.2)
    gc.collect()
    live = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    dead_coords = report["dead"]
    live_holding = 0
    for task in live:
        for referent in gc.get_referents(task):
            if any(referent is c for c in dead_coords):
                live_holding += 1
    alive = 0
    for coord in dead_coords:
        refs = [
            r
            for r in gc.get_referrers(coord)
            if isinstance(r, (asyncio.Task, asyncio.Handle))
        ]
        alive += len(refs)

    print(f"RESULT lifecycles={args.lifecycles}")
    print(f"RESULT setups_ok={report.get('setup_ok', 0)}")
    print(f"RESULT unloads_ok={report.get('unload_ok', 0)}")
    print(f"RESULT solves_started={slow.started} solves_finished={slow.finished}")
    print(f"RESULT escaped_exceptions={len(report.get('escaped', []))}")
    print(f"RESULT refresh_cancelled={report.get('refresh_cancelled', 0)}")
    print(f"RESULT refresh_timeout={report.get('refresh_timeout', 0)}")
    print(f"RESULT state_listeners_after={len(getattr(hass, 'state_listeners', []))}")
    print(f"RESULT bus_listeners_after={len(hass.bus.listeners)}")
    print(f"RESULT live_tasks_referencing_dead_coord={live_holding}")
    print(f"RESULT dead_coordinators_held_by_tasks={alive}")
    print(f"RESULT actuations_during_lifecycles={actuations_during}")
    print(f"RESULT actuations_after_release={actuations_after_release}")
    print(f"RESULT plan_handover_entries_after_plain_unload={handover_after}")
    print(f"RESULT plan_handover_bytes_retained={handover_bytes}")
    print(f"RESULT new_instance_first_cycle_ok={first_cycle_ok}")
    for line in report.get("escaped", []):
        print(f"  ESCAPED {line}")
    for line in report.get("escaped_after_release", []):
        print(f"  ESCAPED-AFTER-RELEASE {line}")
    hass.shutdown()
    d1lib.emit_conditions()


if __name__ == "__main__":
    asyncio.run(main())
