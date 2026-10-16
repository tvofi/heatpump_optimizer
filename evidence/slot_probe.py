#!/usr/bin/env python3
"""REVIEWER-BUILT probe (fix-review.md step 2/8/14) for PR #2341, R10-PREPR-CAP.

Not the finder's harness and not the fixer's: I wrote this. The finding's own
committed instrument is tools/audit/seat/orchestrator_tick.py (it counts prepr
processes); the pool did not exist when the finding was taken, so its capacity
is measured here against the head's own `gate_lock.py` CLI, driven the way
run.sh and prepr.sh drive it.

R1 CAPACITY   slots+1 concurrent `slot-take --no-wait` against one lock dir ->
              exactly `slots` acquire. Null controls at slots=6 (all five
              acquire) and slots=1 (the second refuses), so the number is the
              pool's parameter, not a hard-coded four.
R2 QUEUE      with every slot held, a fifth `slot-take` (waiting) is still
              blocked, appears in `slot-status`'s queue, and acquires when a
              holder releases.

    slot_probe.py <worktree> [slots]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path


def race(gate: str, py: str, lock: str, slots: int, takers: int) -> tuple[int, int]:
    kids = [subprocess.Popen(
        [py, gate, "--lock-dir", lock, "slot-take", "--label", f"t{i}",
         "--slots", str(slots), "--no-wait"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(takers)]
    rcs = [k.wait(timeout=90) for k in kids]
    return rcs.count(0), sum(1 for r in rcs if r != 0)


def main() -> int:
    wt, slots = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4
    gate, py = str(Path(wt) / "tests" / "gate_lock.py"), sys.executable
    with tempfile.TemporaryDirectory() as td:
        acq, ref = race(gate, py, str(Path(td) / "l1"), slots, slots + 1)
        print(f"RESULT CAPACITY slots={slots} n={slots + 1}: acquired={acq} refused={ref}")
        a2, r2 = race(gate, py, str(Path(td) / "l2"), slots + 2, slots + 1)
        print(f"RESULT CAPACITY null control slots={slots + 2} n={slots + 1}: "
              f"acquired={a2} refused={r2}")
        a3, r3 = race(gate, py, str(Path(td) / "l3"), 1, 2)
        print(f"RESULT CAPACITY null control slots=1 n=2: acquired={a3} refused={r3}")

        lock = str(Path(td) / "l4")
        holders = [subprocess.Popen(
            [py, gate, "--lock-dir", lock, "slot-take", "--label", f"hold{i}",
             "--slots", str(slots)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(slots)]
        time.sleep(1.5)
        waiter = subprocess.Popen(
            [py, gate, "--lock-dir", lock, "slot-take", "--label", "fifth",
             "--slots", str(slots)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        time.sleep(2.5)
        waiting = waiter.poll() is None
        st = subprocess.run([py, gate, "--lock-dir", lock, "slot-status",
                             "--slots", str(slots)], capture_output=True, text=True).stdout.strip()
        subprocess.run([py, gate, "--lock-dir", lock, "slot-release", "--label", "hold0",
                        "--slots", str(slots)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            rc = waiter.wait(timeout=30)
        except subprocess.TimeoutExpired:
            waiter.kill()
            rc = -1
        for h in holders:
            h.kill()
        print(f"RESULT QUEUE waiting={waiting} rc={rc} queued_line={'fifth' in st}")
        print(f"RESULT QUEUE status={st}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
