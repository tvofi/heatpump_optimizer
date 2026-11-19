"""D1-s2 round 11, D1.M2: a large stored ``boosted_h`` kills the boost restore task on every restart.

Metric (one line): over 5 cells of a stored boost record whose
``space_settle.boosted_h`` is a finite number below ``store.ABSURD`` but past
``timedelta``'s range (1e10, 3e10, 1e11, 1e12, 1e14 h), the number of restarts
(two per cell, the document unchanged between them) in which the restore task
spawned by the coordinator (``boost.restore_session`` -> ``_restore_settle``)
raises, leaving the running space overlay's start unrestored and the boosted
time at 0 rather than "unknown" (None).
Count key: the spawned task's exception, ``boost.held_for(coord).space_since`` and
``.space_boosted`` -- what the loader installed -- never the planted value.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/boost_settle.py [--fix]
Expected at baseline: RESULT restarts_raising=8 (of 10; 1e10 h still fits timedelta and installs ~47 000 years); control boosted_h=1.5 -> 0.
--fix (perturbation, in memory: ``_restore_settle`` treats a boosted_h past
``timedelta``'s range as unreadable, the docstring's own rule) -> 0.
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
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import boost  # noqa: E402

C = L.const
KEY = f"{C.DOMAIN}_{L.ENTRY_ID}_boost"
CELLS = [1e10, 3e10, 1e11, 1e12, 1e14]


def record(boosted_h):
    iso = lambda h: (L.T0 + timedelta(hours=h)).isoformat()  # noqa: E731
    return {"space": {"until": iso(1), "since": iso(-1)}, "dhw": {"until": iso(2)},
            "space_settle": {"until": iso(3), "boosted_h": boosted_h}}


def fixed_settle(real):
    def settle(held, raw, now):
        tail = raw.get("space_settle") if isinstance(raw, dict) else None
        if isinstance(tail, dict):
            h = tail.get("boosted_h")
            if isinstance(h, (int, float)) and not isinstance(h, bool) and h >= timedelta.max.total_seconds() / 3600:
                raw = {**raw, "space_settle": {**tail, "boosted_h": None}}
        return real(held, raw, now)
    return settle


async def restart_once(text):
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    L.storage_stub._DISK[KEY] = text
    L.storage_stub._VERSIONS[KEY] = 1
    hass = L.SchedHass(L.base_states())
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config()))
    excs = await L.drain(hass)
    held = boost.held_for(coord)
    after = L.storage_stub._DISK.get(KEY)
    out = {"raised": [e for e in excs if "Error" in e], "space_since": held.space_since,
           "space_boosted": held.space_boosted, "dhw": "dhw" in held.until, "doc_after": after}
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    ps = L.patches()
    if a.fix:
        ps.append(mock.patch.object(boost, "_restore_settle", fixed_settle(boost._restore_settle)))
    for p in ps:
        p.start()
    raising = 0
    per_cell = []
    try:
        for h in [1.5] + CELLS:
            n = 0
            text = json.dumps(record(h))
            for r in range(2):  # the same document across two restarts
                L.reset_globals()
                L.dtu.freeze(L.T0)
                res = asyncio.run(restart_once(text))
                text = res["doc_after"] or text
                n += bool(res["raised"])
                print(f"CELL boosted_h={h:g} restart={r + 1}: raised={res['raised'][:1]} space_since={res['space_since']} "
                      f"space_boosted={res['space_boosted']} dhw_boost_restored={res['dhw']}")
            if h != 1.5:
                raising += n
                per_cell.append(n)
            else:
                print(f"RESULT control_restarts_raising={n} count")
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()
    print(f"RESULT cells={len(CELLS)} count")
    print(f"RESULT restarts_raising={raising} count")
    print(f"RESULT per_cell={per_cell}")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
