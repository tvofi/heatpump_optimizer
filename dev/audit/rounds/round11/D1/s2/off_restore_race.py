"""D1-s2 round 11, D1.M2 perturbation: a save during the load -- the off-restore record.

Metric (one line): with the persisted off-restore record holding one armed
baseline (the heat curve's, number.curve = 3.0) and the store read in flight
(each stub read suspends 10 ms, as a real executor read does), the number of
the 2 consequences that occur when a second caller of
``off_restore._armed_record`` runs while the first caller's load is pending --
here ``async_armed_entry`` (heat_curve.publish's first call) and
``async_restore`` (entering MODE_OFF, or unload) on one entry:
  (1) ``async_restore`` sends no restore write (the hold is not released), and
  (2) the store document after both is missing the armed baseline (the next
      restart cannot release it either).
Count key: the service calls ``async_restore`` makes (FakeServices.calls) and the
stub disk document, never the planted record.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/off_restore_race.py [--serial] [--fix]
Expected at baseline: RESULT consequences=2. --serial (null control: the same
two calls, the second after the first returns) -> 0. --fix (perturbation, in
memory: ``_armed_record`` marks the record loaded only after its read, and a
concurrent caller awaits that read) -> 0.
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
from unittest import mock  # noqa: E402

from heatpump_optimizer import off_restore  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

C = L.const
KEY = f"{C.DOMAIN}_{L.ENTRY_ID}_off_restore"
CURVE = "number.curve"
RECORD = {"armed": {"heat_curve": {"entity_id": CURVE, "value": 3.0}}}


def fixed_armed_record(real):
    """The perturbation: one read per record, awaited by every caller."""
    pending: dict = {}

    async def armed_record(hass, entry):
        held = off_restore._RECORDS.get(entry)
        if held is not None and held.loaded and entry not in pending:
            return held
        fut = pending.get(entry)
        if fut is None:
            fut = pending[entry] = asyncio.ensure_future(real(hass, entry))
        try:
            return await asyncio.shield(fut)
        finally:
            if fut.done():
                pending.pop(entry, None)
    return armed_record


async def scenario(serial):
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    L.storage_stub._DISK[KEY] = json.dumps(RECORD)
    L.storage_stub._VERSIONS[KEY] = 1
    hass = L.SchedHass({CURVE: L.FakeState("5.0", attributes={"min": -10, "max": 10, "step": 1},
                                           last_updated=L.T0, last_reported=L.T0)})
    entry = L.FakeEntry(data=L.base_config({C.CONF_HEAT_CURVE_DISPLACE_ENTITY: CURVE,
                                            C.CONF_HEAT_CURVE_TARGET_KIND: C.HEAT_CURVE_KIND_PERSISTENT}))
    config = EntryConfig.from_mapping(dict(entry.data))
    if serial:
        await off_restore.async_armed_entry(hass, entry, "heat_curve")
        sent = await off_restore.async_restore(hass, entry, config, "mode_off")
    else:
        first = asyncio.ensure_future(off_restore.async_armed_entry(hass, entry, "heat_curve"))
        await asyncio.sleep(0)  # the first caller's read is in flight
        sent = await off_restore.async_restore(hass, entry, config, "mode_off")
        await first
    writes = [c for c in hass.services.calls if (c[2] or {}).get("entity_id") == CURVE]
    doc = json.loads(L.storage_stub._DISK.get(KEY, "null"))
    return sent, writes, doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    real_load = L.storage_stub.Store.async_load

    async def slow_load(self):
        await asyncio.sleep(0.01)
        return await real_load(self)
    ps = [mock.patch.object(L.storage_stub.Store, "async_load", slow_load)]
    if a.fix:
        ps.append(mock.patch.object(off_restore, "_armed_record", fixed_armed_record(off_restore._armed_record)))
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    try:
        sent, writes, doc = asyncio.run(scenario(a.serial))
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()
    # In the serial arm the restore legitimately releases the hold: the document then
    # loses the entry because it was restored, which is the release, not a loss.
    released = sent >= 1
    lost = (not released) and "heat_curve" not in (doc or {}).get("armed", {})
    print(f"RACE serial={a.serial} fix={a.fix}: restore_writes_sent={sent} curve_writes={[(c[1], (c[2] or {}).get('value')) for c in writes]} doc_after={json.dumps(doc)}")
    print(f"RESULT hold_not_released={int(not released)} count")
    print(f"RESULT baseline_lost_on_disk={int(lost)} count")
    print(f"RESULT consequences={int(not released) + int(lost)} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
