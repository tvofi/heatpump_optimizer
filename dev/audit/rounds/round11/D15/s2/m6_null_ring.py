#!/usr/bin/env python3
"""D15-s2 harness, D15.M6 null control: does the synthetic bundle exercise the
drift latch D15.M6 re-derives?

D15.md: every step runs on ``tools/replay/dbg_bundle_gen.py``'s synthetic
bundle first. M6 compares ``SnapshotRing.observe_bias`` against the recorded
``accuracy_drift`` latch, so the null control is only a control if the
generator's coordinator ran the latch at all.

Metric (one line): ``observe_bias_calls`` = calls of the production
``heatpump_optimizer.snapshots:SnapshotRing.observe_bias`` while
``dbg_bundle_gen.build_bundle(--days)`` generates the bundle;
``ring_days_counted`` = the distinct calendar days those calls counted;
``stored_last_day_set`` = whether the bundle's snapshots store records one.
Count key: the production method's own calls, not the store text.

Run (from the export root):
    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m6_null_ring.py --days 2
    ... --perturb loads   # the generator's store loads run (debug_replay.enable_store_loads,
                          # which the timeline replay already uses) -> calls > 0
Expected at 92d38ecb: observe_bias_calls=0 shipped; > 0 under --perturb loads.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import dbg_bundle_gen  # noqa: E402
import debug_replay  # noqa: E402
from heatpump_optimizer import snapshots  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--perturb", default="")
    a = ap.parse_args(argv)
    began_cpu, began_thread = time.process_time(), time.thread_time()
    calls: list = []
    real = snapshots.SnapshotRing.observe_bias

    def counting(self, now, bias, healthy):
        calls.append(now.date().isoformat())
        return real(self, now, bias, healthy)

    original = debug_replay.enable_store_loads() if a.perturb == "loads" else None
    try:
        with mock.patch.object(snapshots.SnapshotRing, "observe_bias", counting), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            bundle = dbg_bundle_gen.build_bundle(a.days)
    finally:
        if original is not None:
            debug_replay.restore_store_loads(original)
    ring = next((d for k, d in bundle["stores"].items() if k.endswith("_snapshots")), None)
    print(f"RESULT cycles={bundle['manifest']['cycles']} unit=count")
    print(f"RESULT observe_bias_calls={len(calls)} unit=count")
    print(f"RESULT ring_days_counted={len(set(calls))} unit=count")
    print(f"RESULT stored_last_day_set={int(bool((ring or {}).get('last_day')))} unit=flag")
    cpu, thr = time.process_time() - began_cpu, time.thread_time() - began_thread
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else float('nan'):.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
