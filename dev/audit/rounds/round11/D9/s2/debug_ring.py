#!/usr/bin/env python3
"""D9-s2 retained bytes of the debug collector's in-memory ring over a collection and after it.

METRIC: deep ``sys.getsizeof`` (retained.py:deep_size) of one
``debugger.DebugCollector`` (its ``rows`` and ``snapshots``) after each simulated cycle
at the shortest interval (10 min), fed by ``DebugCollector.record`` with REAL published
payloads (``coordinator.data`` from ``_async_update_data`` cycles of the synthetic replay,
rotated), for --cycles cycles; printed: the peak, the slope over the collection's first
day and over the last --tail cycles. ``COLLECT_SPAN`` (7 days = 1,008 cycles) bounds it: a
bounded ring is flat after cycle 1,008. Count key: bytes of the production object.
PERTURBATION: --span-days N swaps ``debugger.COLLECT_SPAN`` in memory; the plateau cycle
moves to N*144 and the peak scales with N (direction: up for N > 7).
RUN:   HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s2/debug_ring.py \
         [--cycles 1300] [--span-days 7]
EXPECTED: peak 1,681,613 B +-10 % at 7 days (1,008 rows, 7 snapshots); tail slope 0 B/cycle (exact); --span-days 8: 1,921,264 B.
BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: printed.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import platform
import sys
import time
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _drive  # noqa: E402
from retained import deep_size  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=1300)
    ap.add_argument("--payloads", type=int, default=12)
    ap.add_argument("--tail", type=int, default=200)
    ap.add_argument("--span-days", type=float, default=None)
    args = ap.parse_args()
    t0 = time.time()
    drv = _drive.Driver("synthetic")
    payloads = []
    for _ in range(args.payloads):
        payloads.append(drv.cycle())
    from heatpump_optimizer import debugger
    if args.span_days is not None:
        debugger.COLLECT_SPAN = timedelta(days=args.span_days)
    spawned = []

    def spawn(coro):
        spawned.append(getattr(coro, "__name__", "?"))
        coro.close()

    col = debugger.DebugCollector(drv.hass, drv.entry.entry_id, spawn)
    start = drv.now()
    sizes = []
    for c in range(args.cycles):
        now = start + timedelta(minutes=_drive.INTERVAL_MIN * c)
        col.record(drv.coord, payloads[c % len(payloads)], now)
        if c % 10 == 0 or c == args.cycles - 1:
            sizes.append((c, deep_size(col.rows, set()) + deep_size(col.snapshots, set())))
    drv.close()
    peak = max(s for _, s in sizes)
    day = [s for c, s in sizes if c <= 144]
    tail = [(c, s) for c, s in sizes if c >= args.cycles - args.tail]
    print(f"# machine {platform.platform()} py{platform.python_version()}")
    print(f"# span={debugger.COLLECT_SPAN} cycles={args.cycles} rows={len(col.rows)} "
          f"snapshots={len(col.snapshots)} final={col.final} spawned={sorted(set(spawned))}")
    for c, s in sizes[:: max(1, len(sizes) // 14)]:
        print(f"# cycle={c} ring_bytes={s}")
    print(f"RESULT ring_peak_bytes={peak} B")
    print(f"RESULT ring_rows={len(col.rows)} count")
    print(f"RESULT first_day_slope={(day[-1] - day[0]) / 144:.0f} B/cycle")
    print(f"RESULT tail_slope={(tail[-1][1] - tail[0][1]) / max(1, tail[-1][0] - tail[0][0]):.0f} B/cycle "
          f"(cycles {tail[0][0]}..{tail[-1][0]})")
    print(f"RESULT wall_s={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT thread_factor={time.process_time() / max(1e-9, time.thread_time()):.3f}")
    print(f"RESULT load1={_drive.load1()}")
    print(f"RESULT swapins={_drive.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
