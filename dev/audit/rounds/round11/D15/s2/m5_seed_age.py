#!/usr/bin/env python3
"""D15-s2 harness, D15.M5 (timeline replay, stores seeded): how much of the
seeded state postdates the replay window it starts?

The debugger bundle's stores are read at download time (``manifest.age_hours``
after the collection ended); ``debug_replay.run_seeded`` seeds them as the
state the coordinator holds at the replay window's START.

Metrics (one line each):
  future_samples_held: accuracy samples ``HeatPumpOptimizerCoordinator`` holds
      in its tracker (``coordinator._accuracy.samples``) at the replay's first
      cycle whose own ``when`` is later than that cycle's clock.
  bounded_instants: stored instants the production store boundary
      (``heatpump_optimizer.store._bound_instants``) rewrote as "ahead of the
      clock" while the seeded stores loaded.
  window_start_to_store_newest_h: hours from the replay window's start to the
      newest seeded accuracy sample.
Property: the coordinator a timeline replay starts holds no evidence stamped
after the replay's own clock (state as of the window start, not of the download).
Rule enumerating the seams: ``--list`` prints each seeded store holding an
instant later than the window start, with the count.
Count key: ``future_samples_held`` is read off the coordinator's live tracker
after load, not off the store text; ``bounded_instants`` off the production
boundary's own warning records.

Run (from the export root):
    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m5_seed_age.py --bundle B
    ... --list
    ... --start-after-stores   # null/perturbation: start the replay after the newest
                               # seeded sample -> future_samples_held 0
Expected on the owner's 2026-11-16 download at 92d38ecb: future_samples_held
> 100; bounded_instants > 0; --start-after-stores: 0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
Privacy: counts, hours and store names only.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
import debug_replay  # noqa: E402


def instants(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from instants(v)
    elif isinstance(node, list):
        for v in node:
            yield from instants(v)
    elif isinstance(node, str) and len(node) >= 19 and node[10:11] == "T":
        try:
            when = datetime.fromisoformat(node)
        except ValueError:
            return
        if when.tzinfo is not None:
            yield when


class Bounded(logging.Handler):
    def __init__(self):
        super().__init__()
        self.n = 0

    def emit(self, record):
        if "is ahead of the clock" in str(record.msg):
            self.n += 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--start-after-stores", action="store_true")
    a = ap.parse_args(argv)
    began_cpu, began_thread = time.process_time(), time.thread_time()

    bundle = debug_ingest.load_bundle(a.bundle)
    doc = bundle.get("replay") or {}
    stores = bundle.get("stores") or {}
    start = datetime.fromisoformat(doc["window"]["start"])
    acc = next((d for k, d in stores.items() if k.endswith("_accuracy")), {})
    acc_times = [datetime.fromisoformat(s["t"]) for s in
                 ((acc.get("accuracy") or {}).get("samples") or []) if s.get("t")]
    newest = max(acc_times) if acc_times else start
    if a.start_after_stores:
        start = newest + timedelta(minutes=1)
    if a.list:
        from heatpump_optimizer import store as store_mod
        for key, document in sorted(stores.items()):
            n = sum(1 for w in instants(document) if w > start)
            if n:
                print(f"{store_mod.store_name(key)} {n}")
        return 0

    from heatpump_optimizer import coordinator as cm
    seen: dict = {}
    real_tick = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def first_tick(self):
        if "held" not in seen:
            from homeassistant.util import dt as dt_util
            now = dt_util.now()
            seen["held"] = sum(1 for s in self._accuracy.samples if s.when > now)
            seen["total"] = len(self._accuracy.samples)
        return await real_tick(self)

    handler = Bounded()
    logging.getLogger("heatpump_optimizer.store").addHandler(handler)
    window = debug_replay.trim_replay(doc, start, start + timedelta(minutes=15))
    if a.start_after_stores:
        # the replay half ends before the stores' newest sample: keep its last
        # states in force, re-stamped at the new start, so the window has inputs
        for entity_id, rows in list(window["states"].items()):
            last = debug_replay._carry_attrs(doc["states"].get(entity_id) or rows)[-1:]
            window["states"][entity_id] = [[start.isoformat(), r[1], r[2], None] for r in last]
        window["window"] = {"start": start.isoformat(),
                            "end": (start + timedelta(minutes=15)).isoformat()}
    with mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_async_update_data", first_tick), \
            contextlib.redirect_stderr(io.StringIO()):
        verdict = debug_replay.run_seeded(window, stores or None, 15)
    print(f"RESULT replay_cycles={verdict.get('cycles')} unit=count")
    print(f"RESULT future_samples_held={seen.get('held')} unit=count of={seen.get('total')}")
    print(f"RESULT bounded_instants={handler.n} unit=count")
    print(f"RESULT window_start_to_store_newest_h={(newest - start).total_seconds() / 3600:.1f} unit=h")
    cpu, thr = time.process_time() - began_cpu, time.thread_time() - began_thread
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else float('nan'):.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
