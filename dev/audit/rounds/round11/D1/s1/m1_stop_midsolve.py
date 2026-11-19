"""D1.M1 (census line `async_add_executor_job coordinator.py:1958 async_register_worker_shutdown._stop`):
Home Assistant's stop landing while a solve is in the process worker.

Metric: count of `solve_worker_fallback` repair issues still raised after a
simulated restart's first successful process solve, when EVENT_HOMEASSISTANT_STOP
fired while a solve was being read back from the worker; plus whether the
issue was created persistent and how many in-process (GIL) solves ran after stop.
Count key: entries with issue_id "solve_worker_fallback" on `hass.issues`
(the repair registry the production `_create_issue`/`ir.async_delete_issue`
write), read after the restarted instance's first solve completed.

Restart model: Home Assistant does not unload entries at stop; a persistent
issue is restored from storage at start, and module globals start empty. The
harness keeps `hass.issues` (the restored registry) and clears
`coordinator._WORKER_FALLBACK_CAUSES` and the streak bag (fresh interpreter).

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m1_stop_midsolve.py [--arm stop_midsolve|stop_idle] [--perturb]
Expect: --arm stop_midsolve: RESULT stale_fallback_issues_after_restart=1, issue_persistent=1,
        in_process_solves_after_stop=1 (exact). Null control --arm stop_idle: 0, 0, 0.
Perturbation (--perturb): `_clear_worker_fallback` deletes the issue even when this
        process latched no cause (drop the early `return`): 1 -> 0.
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
import logging  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant.const import EVENT_HOMEASSISTANT_STOP  # noqa: E402
from homeassistant.helpers import issue_registry as ir  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import const, coordinator as cm  # noqa: E402

logging.basicConfig(level=logging.ERROR)

READING = threading.Event()
_orig_read = cm._read_reply


def _signal_read(stdout):
    READING.set()
    return _orig_read(stdout)


cm._read_reply = _signal_read

INPROC = {"n": 0, "after_stop": 0, "stopped": False}
CAUSES: list = []
_orig_note = cm._note_worker_fallback


def _note(hass, err, entry_id=None):
    CAUSES.append(f"{type(err).__name__}: {err}")
    return _orig_note(hass, err, entry_id)


cm._note_worker_fallback = _note


class CountingHass(rl.RealHass):
    """Counts the in-process (GIL) solves: the fallback route hands
    ``optimize_in_process`` to the executor directly; the process route
    hands it ``_run_in_process``. ``optimize_in_process`` itself is never
    replaced, since the process route pickles it by name."""

    async def async_add_executor_job(self, func, *args):
        if func is cm.optimize_in_process:
            INPROC["n"] += 1
            if INPROC["stopped"]:
                INPROC["after_stop"] += 1
        return await super().async_add_executor_job(func, *args)


def _solves(co):
    return getattr(co, "_d1s1_solves", 0)


_orig_file = cm.HeatPumpOptimizerCoordinator._file_lead_predictions


def _counted_file(self, *a, **k):
    self._d1s1_solves = _solves(self) + 1
    return _orig_file(self, *a, **k)


cm.HeatPumpOptimizerCoordinator._file_lead_predictions = _counted_file


def _clear_perturbed(hass, entry_id=None):
    cm._reset_worker_fallback_streak(hass, entry_id)
    cm._WORKER_FALLBACK_CAUSES.pop(entry_id, None)
    if not cm._WORKER_FALLBACK_CAUSES:
        ir.async_delete_issue(hass, const.DOMAIN, "solve_worker_fallback")


def price_state():
    t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    rows = [{"start": (t0 + timedelta(hours=h)).isoformat(), "value": 0.5 + 0.4 * ((h % 12) / 12)}
            for h in range(48)]
    return rl.FakeState("0.6", attributes={"raw_today": rows, "unit_of_measurement": "SEK/kWh"})


CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.price",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}


async def wait_solve(co, n0, timeout=120.0):
    t = time.time()
    while time.time() - t < timeout:
        if _solves(co) > n0:
            return True
        await asyncio.sleep(0.05)
    return False


def fallback_issues(hass):
    return [i for i in getattr(hass, "issues", []) if i[1] == "solve_worker_fallback"]


async def run(arm: str):
    hass = CountingHass({"sensor.indoor": rl.FakeState("21.0"), "sensor.outdoor": rl.FakeState("-3.0"),
                        "sensor.price": price_state()})
    entry = rl.RecordingEntry(data=CONFIG)
    assert await rl.harness.ha_setup_entry(integ, hass, entry)
    co = entry.runtime_data
    assert await wait_solve(co, 0), "first solve"
    stop = hass.bus.listeners_for(EVENT_HOMEASSISTANT_STOP)
    n0 = _solves(co)
    if arm == "stop_midsolve":
        READING.clear()
        task = hass.async_create_task(co.async_run_optimization())
        await asyncio.to_thread(READING.wait, 60)  # the job is in the child; its reply is awaited
        INPROC["stopped"] = True
        for fn in stop:
            await fn(None)
        await asyncio.wait([task], timeout=120)
    else:
        INPROC["stopped"] = True
        for fn in stop:
            await fn(None)
        await co.async_run_optimization()
    raised = fallback_issues(hass)
    persistent = int(any(i[2].get("is_persistent") for i in raised))
    # ---- restart: the registry's persistent issues survive, module state does not.
    issues = [i for i in getattr(hass, "issues", []) if i[2].get("is_persistent")]
    cm._WORKER_FALLBACK_CAUSES.clear()
    hass.data.pop(cm._WORKER_FALLBACK_STREAK, None)
    hass2 = rl.RealHass({"sensor.indoor": rl.FakeState("21.0"), "sensor.outdoor": rl.FakeState("-3.0"),
                         "sensor.price": price_state()})
    hass2.issues = list(issues)
    entry2 = rl.RecordingEntry(data=CONFIG)
    assert await rl.harness.ha_setup_entry(integ, hass2, entry2)
    co2 = entry2.runtime_data
    ok = await wait_solve(co2, 0)
    ok2 = (await co2.async_run_optimization()) is None
    stale = len(fallback_issues(hass2))
    await rl.ha_unload_faithful(integ, hass2, entry2)
    cm._shutdown_process_pool()
    hass.executor.shutdown(wait=True)
    hass2.executor.shutdown(wait=True)
    return {"raised": len(raised), "persistent": persistent, "stale": stale,
            "restart_solves_ok": int(ok and ok2), "inproc_after_stop": INPROC["after_stop"],
            "causes": list(CAUSES)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("stop_midsolve", "stop_idle"), default="stop_midsolve")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    if a.perturb:
        cm._clear_worker_fallback = _clear_perturbed
    t0, p0 = time.thread_time(), time.process_time()
    r = asyncio.run(run(a.arm))
    print(f"INFO arm={a.arm} perturb={a.perturb}")
    for c in r["causes"]:
        print(f"INFO fallback cause: {c[:160]}")
    print(f"RESULT fallback_issues_at_stop={r['raised']} count")
    print(f"RESULT issue_persistent={r['persistent']} flag")
    print(f"RESULT in_process_solves_after_stop={r['inproc_after_stop']} count")
    print(f"RESULT restart_two_solves_ok={r['restart_solves_ok']} flag")
    print(f"RESULT stale_fallback_issues_after_restart={r['stale']} count")
    rl.env_results(t0, p0)


if __name__ == "__main__":
    main()
