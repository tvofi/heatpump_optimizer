"""Verifier D1#1, V2 for D1-s2-04: off_restore._armed_record under three orderings and three read delays.

Metric: over orderings {armed_entry || restore, restore || armed_entry, armed_entry || armed_entry}
and store-read delays {sleep(0), 1 ms, 10 ms}, the number of (ordering, delay) cells in which the
SECOND caller observes an empty armed map although the persisted record holds the heat-curve
baseline (it returns None from async_armed_entry, or async_restore sends 0 writes).
Null: the same pairs run serially. The (restore, armed) ordering is uninformative: serially the
restore legitimately releases the hold first, so its null reads 1 by design; judge on the other 6 cells.
Rig: d1s2_lib (stub disk, FakeEntry); orderings, delays and count key are mine.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_04_race_orders.py
"""
import asyncio
import json
import os
import sys
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s2"))
import d1s2_lib as L  # noqa: E402
from heatpump_optimizer import off_restore  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

C = L.const
KEY = f"{C.DOMAIN}_{L.ENTRY_ID}_off_restore"
CURVE = "number.curve"


async def one(order, serial):
    off_restore._RECORDS.clear()
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    L.storage_stub._DISK[KEY] = json.dumps({"armed": {"heat_curve": {"entity_id": CURVE, "value": 3.0}}})
    L.storage_stub._VERSIONS[KEY] = 1
    hass = L.SchedHass({CURVE: L.FakeState("5.0", attributes={"min": -10, "max": 10, "step": 1},
                                           last_updated=L.T0, last_reported=L.T0)})
    entry = L.FakeEntry(data=L.base_config({C.CONF_HEAT_CURVE_DISPLACE_ENTITY: CURVE,
                                            C.CONF_HEAT_CURVE_TARGET_KIND: C.HEAT_CURVE_KIND_PERSISTENT}))
    cfg = EntryConfig.from_mapping(dict(entry.data))

    def mk(kind):
        if kind == "armed":
            return off_restore.async_armed_entry(hass, entry, "heat_curve")
        return off_restore.async_restore(hass, entry, cfg, "mode_off")

    def empty(kind, res):
        return res is None if kind == "armed" else res == 0

    a, b = order
    if serial:
        await mk(a)
        rb = await mk(b)
    else:
        fa = asyncio.ensure_future(mk(a))
        await asyncio.sleep(0)
        rb = await mk(b)
        await fa
    return int(empty(b, rb))


async def main():
    real_load = L.storage_stub.Store.async_load
    orders = [("armed", "restore"), ("restore", "armed"), ("armed", "armed")]
    hits = nulls = 0
    for delay in (0.0, 0.001, 0.01):
        async def slow(self, _d=delay):
            await asyncio.sleep(_d)
            return await real_load(self)
        with mock.patch.object(L.storage_stub.Store, "async_load", slow):
            for o in orders:
                h = await one(o, False)
                n = await one(o, True)
                print(f"delay={delay} order={o} concurrent_second_empty={h} serial_second_empty={n}")
                hits += h
                nulls += n
    print(f"RESULT cells_second_caller_empty={hits} of 9")
    print(f"RESULT null_serial_empty={nulls} of 9")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


L.reset_globals()
L.dtu.freeze(L.T0)
try:
    asyncio.run(main())
finally:
    L.dtu.freeze(None)
