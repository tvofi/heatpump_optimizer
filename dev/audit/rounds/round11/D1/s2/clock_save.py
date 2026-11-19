"""D1-s2 round 11, D1.M2 perturbations: a writer clock ahead across a restart; a save during the load.

Metric (one line): (a) every d1-stores record written with the clock 48 h
ahead and read back at the true time by a full restart (all stores at once,
the constructor's spawned loads and the late loaders) and two real cycles:
cycle failures, and published instants more than 1 h ahead of now that the
same restart from a record written at the true time does not publish;
(b) every saver invoked while the startup reads are in flight (each stub read
suspends 10 ms, as a real executor read does): the number of stores whose
persisted document after the race differs from the race-free control (the
same savers run after the reads land) -- a save that clobbered its own read.
Count key: the published payload, the cycle outcome and the stub disk's
documents, never the planted records.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/clock_save.py [--no-wait]
--no-wait (perturbation for arm b): ``QuarantiningStore.async_wait_for_read``
returns at once, so a save no longer waits for its read -> the clobber count
must rise from its baseline.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from unittest import mock  # noqa: E402

import store_fuzz as SF  # noqa: E402

FB = SF.FB
AHEAD = timedelta(hours=48)


def healthy_at(when):
    L.dtu.freeze(when)
    try:
        L.storage_stub._VERSIONS.clear()
        disk = FB._healthy_payloads()
        vers = dict(L.storage_stub._VERSIONS)
    finally:
        L.dtu.freeze(None)
    return disk, vers


def future_instants(obj, now, path="data", out=None):
    out = [] if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            future_instants(v, now, f"{path}.{k}", out)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj[:50]):
            future_instants(v, now, f"{path}[]", out)
    else:
        when = None
        if isinstance(obj, datetime):
            when = obj
        elif isinstance(obj, str) and len(obj) >= 16 and obj[10:11] in ("T", " "):
            when = L.dtu.parse_datetime(obj)
        if when is not None:
            if when.tzinfo is None:
                when = when.replace(tzinfo=L.dtu.DEFAULT_TIME_ZONE)
            if when > now + timedelta(hours=1):
                out.append(path)
    return out


async def restart(disk, vers, savers_early=False):
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    for k, v in disk.items():
        L.storage_stub._DISK[k] = json.dumps(v)
        L.storage_stub._VERSIONS[k] = vers.get(k, 1)
    hass = L.SchedHass(L.base_states())
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config()))
    late = [asyncio.ensure_future(FB.LOADERS[n](coord)) for n in SF.LATE]
    if savers_early:
        await asyncio.sleep(0)  # the reads are in flight
        await savers(coord)
    await asyncio.gather(*late, return_exceptions=True)
    await L.drain(hass)
    if not savers_early:
        await savers(coord)
    await L.drain(hass)
    return hass, coord


async def savers(coord):
    from heatpump_optimizer import boost, away, pump_arbiter, duty_switch, off_restore
    calls = [coord._async_save_thermal_learning(), coord._async_save_price_model(), coord._async_save_accuracy(),
             coord._async_save_energy_totals(), coord._async_save_manual_plan(), coord._async_save_snapshots(),
             coord._async_save_ledger(), coord._dhw_learner.async_save_profile(), coord._dhw_learner.async_save_draws(),
             coord._legionella.async_save(), boost.persist(coord), away.persist_override(coord, coord._away_state),
             pump_arbiter._persist(coord), duty_switch._persist(duty_switch.record_for(coord)),
             FB._save_notifier(coord), FB._save_debug(coord)]
    held = await off_restore._armed_record(coord.hass, coord.entry)
    calls.append(off_restore._save(held))
    await asyncio.gather(*calls, return_exceptions=True)


async def arm_clock(out, disks):
    now = L.T0
    res = {}
    for tag in ("control", "ahead"):
        disk, vers = disks[tag]
        L.reset_globals()
        L.dtu.freeze(now)
        hass, coord = await restart(disk, vers)
        L.price_stub(coord)
        fails, fut = [], set()
        for i in range(2):
            L.dtu.freeze(now + timedelta(minutes=15 * i))
            try:
                d = await coord._async_update_data()
                fut |= set(future_instants(d, L.dtu.now()))
            except Exception as e:  # noqa: BLE001
                fails.append(repr(e)[:120])
            fails += await L.drain(hass)
        res[tag] = (fails, fut)
        await coord.async_shutdown()
        await L.drain(hass, 5)
    extra = sorted(res["ahead"][1] - res["control"][1])
    print(f"CLOCK control fails={res['control'][0]} future_paths={len(res['control'][1])}")
    print(f"CLOCK ahead   fails={res['ahead'][0]} extra_future_paths={extra[:12]}")
    out["clock_ahead_cycle_fail"] = len(res["ahead"][0])
    out["clock_ahead_extra_future_published"] = len(extra)


async def arm_save(out, no_wait, disks):
    disk, vers = disks["control"]
    docs = {}
    for tag, early in (("control", False), ("race", True)):
        L.reset_globals()
        L.dtu.freeze(L.T0)
        hass, coord = await restart(disk, vers, savers_early=early)
        docs[tag] = {k: json.loads(v) for k, v in L.storage_stub._DISK.items()}
        await coord.async_shutdown()
        await L.drain(hass, 5)
    diff = sorted(k[len(SF.KEYPFX):] for k in set(docs["control"]) | set(docs["race"])
                  if docs["control"].get(k) != docs["race"].get(k))
    print(f"SAVE no_wait={no_wait} stores_clobbered={diff}")
    out["save_during_load_clobbered"] = len(diff)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-wait", action="store_true")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    real_load = L.storage_stub.Store.async_load

    async def slow_load(self):
        await asyncio.sleep(0.01)
        return await real_load(self)

    async def no_wait(self):
        return None
    ps = L.patches() + [mock.patch.object(L.storage_stub.Store, "async_load", slow_load)]
    if a.no_wait:
        ps.append(mock.patch.object(L.store_mod.QuarantiningStore, "async_wait_for_read", no_wait))
    out = {}
    disks = {"control": healthy_at(L.T0), "ahead": healthy_at(L.T0 + AHEAD)}
    for p in ps:
        p.start()
    try:
        if not a.no_wait:
            asyncio.run(arm_clock(out, disks))
        asyncio.run(arm_save(out, a.no_wait, disks))
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
