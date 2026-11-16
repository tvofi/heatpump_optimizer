"""D1.M1 / C3, round 11, seat D1-s1: the setup-failure half of the unload divergence.

Metric: after N failed setups (the first refresh raises ConfigEntryNotReady
because the price entity is missing) and one successful retry, the count of
live registrations (loop-backed timers/intervals, state listeners, bus
listeners, pending tasks) that reach a coordinator of a FAILED attempt, and
how many failed-attempt coordinators are still alive after gc.collect().
Count key: each live `rl.REGISTRY` entry (timers, intervals, state listeners),
`hass.bus.listeners` entry and pending `hass.tasks` task, counted once, whose gc
referents (not traversing the hass or the entry) reach any failed attempt's
`HeatPumpOptimizerCoordinator` (production registers through its own calls;
nothing here registers for it); `alive` = weakrefs to failed attempts not cleared.

Arms (--setup):
  faithful  Home Assistant's ConfigEntry.async_setup on ConfigEntryNotReady:
            `_async_process_on_unload` (callbacks popped LIFO, a returned
            coroutine scheduled and awaited), then a retry.
  harness   tests/harness.py:ha_setup_entry, which lets the exception escape
            and runs no unload callback (the suite's instrument).
Run:    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m1_notready.py --setup faithful|harness [--retries 3]
Expect: faithful: RESULT failed_attempt_leaks=0, failed_attempts_alive=0, retry_ok=1 (exact).
        harness:  failed_attempt_leaks>0 and failed_attempts_alive=3 (one per failed attempt).
Perturbation: --setup harness is the faithful arm with the one step removed
        (`_async_process_on_unload` not run on failure): leaks 0 -> >0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B4 container, linux x86_64.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rl  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import gc  # noqa: E402
import inspect  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402
import weakref  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant.exceptions import ConfigEntryNotReady  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    away, const, coordinator as cm, early_cutoff, pump_arbiter, running_signal,
)

rl.patch_imported(cm, pump_arbiter, running_signal, away, early_cutoff)
logging.basicConfig(level=logging.CRITICAL)

CREATED: list = []
_orig_init = cm.HeatPumpOptimizerCoordinator.__init__


def _tracking_init(self, *a, **k):
    _orig_init(self, *a, **k)
    CREATED.append(weakref.ref(self))


cm.HeatPumpOptimizerCoordinator.__init__ = _tracking_init

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.price",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp",
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    const.CONF_PEAK_GUARD_ENABLED: True,
    const.CONF_AWAY_PRESENCE_ENTITY: "person.me",
    "heat_pump_power_entity": "sensor.hp_power",
}


def price_state():
    t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    rows = [{"start": (t0 + timedelta(hours=h)).isoformat(), "value": 0.5 + 0.4 * ((h % 12) / 12)}
            for h in range(48)]
    return rl.FakeState("0.6", attributes={"raw_today": rows, "unit_of_measurement": "SEK/kWh"})


async def process_on_unload(hass, entry):
    """homeassistant/config_entries.py ConfigEntry._async_process_on_unload."""
    tasks = []
    while entry._on_unload:
        job = entry._on_unload.pop()()
        if job is not None and inspect.isawaitable(job):
            tasks.append(hass.async_create_task(job))
    if tasks:
        await asyncio.wait(tasks, timeout=10)


async def setup_once(hass, entry, mode):
    try:
        return await rl.harness.ha_setup_entry(integ, hass, entry)
    except ConfigEntryNotReady:
        if mode == "faithful":
            await process_on_unload(hass, entry)
        entry.state = rl.harness.ConfigEntryState.SETUP_RETRY
        return False


async def run(mode, retries):
    hass = rl.RealHass({
        "sensor.indoor": rl.FakeState("21.0"), "sensor.outdoor": rl.FakeState("-3.0"),
        "switch.hp": rl.FakeState("on"), "person.me": rl.FakeState("home"),
        "sensor.house_power": rl.FakeState("1.5", attributes={"unit_of_measurement": "kW"}),
        "sensor.hp_power": rl.FakeState("0.8", attributes={"unit_of_measurement": "kW"}),
    })
    entry = rl.RecordingEntry(data=CONFIG)
    failed = 0
    for _ in range(retries):
        ok = await setup_once(hass, entry, mode)
        failed += int(not ok)
        await asyncio.sleep(0.3)
    failed_refs = list(CREATED)
    hass.states.set("sensor.price", price_state())
    retry_ok = await setup_once(hass, entry, mode)
    await asyncio.sleep(0.5)
    live = entry.runtime_data if retry_ok else None
    gc.collect()
    olds = [r() for r in failed_refs]
    olds = [o for o in olds if o is not None and o is not live]
    skip = (id(hass), id(entry))
    holders = [(rec["kind"], rec["site"], rec["obj"]) for rec in list(rl.REGISTRY.values())]
    holders += [("bus", kind, fn) for kind, fn in list(hass.bus.listeners)]
    holders += [("task", t.get_name(), t) for t in list(hass.tasks) if not t.done()]
    leaks = [(k, s) for k, s, o in holders if any(rl.reaches(o, old, skip_ids=skip) for old in olds)]
    del olds, holders
    gc.collect()
    alive = sum(1 for r in failed_refs if r() is not None and r() is not live)
    if retry_ok:
        await rl.ha_unload_faithful(integ, hass, entry)
    hass.executor.shutdown(wait=True)
    return failed, retry_ok, leaks, alive


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", choices=("faithful", "harness"), default="faithful")
    ap.add_argument("--retries", type=int, default=3)
    a = ap.parse_args()
    t0, p0 = time.thread_time(), time.process_time()
    failed, retry_ok, leaks, alive = asyncio.run(run(a.setup, a.retries))
    for k in leaks:
        print(f"LEAK {k}")
    print(f"INFO setup={a.setup} failed_setups={failed}")
    print(f"RESULT failed_attempt_leaks={len(leaks)} registrations")
    print(f"RESULT failed_attempts_alive={alive} coordinators")
    print(f"RESULT retry_ok={int(bool(retry_ok))} flag")
    cm._shutdown_process_pool()
    rl.env_results(t0, p0)


if __name__ == "__main__":
    main()
