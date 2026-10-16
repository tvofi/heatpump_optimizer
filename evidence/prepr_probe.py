#!/usr/bin/env python3
"""REVIEWER-BUILT probe (fix-review.md steps 2 and 14) for PR #2341.

The forward-carried constraint is "Measure before fixing" and the fix's cost
claim is the nested `--self-test` chain a `prepr.sh` run spawns. The finding's
own committed instrument (tools/audit/seat/orchestrator_tick.py) counts prepr
PROCESSES, not cost, and the pool did not exist when the finding was taken, so
this probe is mine and is disclosed as mine in the verdict.

COST   Run one command in its own session and sample its process group's member
       count every 0.2 s: peak descendant processes (attributable to this
       command alone, on a box other seats share) and wall seconds.
       `prepr.sh --self-test` is the nested chain; `prepr.sh <body that refuses
       at step 1>` is the null control.

BLOCK  Hold every slot, then start a real `prepr.sh`: does it stop at step 1b
       (no step-2 MODE line) until a slot frees, and proceed once one does?

    prepr_probe.py cost <worktree> <argv...>
    prepr_probe.py block <worktree> <slots> <seconds>
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GATE_REL = Path("tests") / "gate_lock.py"


def cost(worktree: str, argv: list[str]) -> int:
    t0 = time.monotonic()
    dest = os.environ.get("PROBE_OUT")
    fh = open(dest, "w") if dest else subprocess.DEVNULL
    p = subprocess.Popen(argv, cwd=worktree, start_new_session=True,
                         stdout=fh, stderr=subprocess.STDOUT if dest else subprocess.DEVNULL)
    pgid = os.getpgid(p.pid)
    peak, samples = 0, 0
    while p.poll() is None:
        out = subprocess.run(["ps", "-Ao", "pgid="], capture_output=True, text=True).stdout
        n = sum(1 for line in out.splitlines() if line.strip() == str(pgid))
        peak = max(peak, n)
        samples += 1
        time.sleep(0.2)
    rc = p.wait()
    if dest:
        fh.close()
    print(f"RESULT COST argv={' '.join(argv[1:])} rc={rc} "
          f"wall={time.monotonic() - t0:.1f}s peak_pg_procs={peak} samples={samples}")
    return 0


def block(worktree: str, slots: int, seconds: float) -> int:
    gate, py = str(Path(worktree) / GATE_REL), sys.executable
    body = Path(tempfile.mkdtemp()) / "seat" / "body.md"
    body.parent.mkdir(parents=True, exist_ok=True)
    body.write_text("# probe body\n\nNo headings a check needs.\n")
    with tempfile.TemporaryDirectory() as td:
        lock = str(Path(td) / "lock")
        holders = [subprocess.Popen(
            [py, gate, "--lock-dir", lock, "slot-take", "--label", f"hold{i}",
             "--slots", str(slots)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(slots)]
        time.sleep(1.5)
        out = Path(td) / "prepr.out"
        fh = out.open("w")
        # The child must use the SAME pool as the holders; HPO_GATE_LOCK_DIR
        # (read by gate_lock.py's DEFAULT_LOCK_DIR) points both at a private
        # dir, so this probe never holds the box's real /tmp/hpo-gate.lock.
        env = {**os.environ, "HPO_GATE_LOCK_DIR": lock}
        run = subprocess.Popen(["bash", "tools/pr/prepr.sh", str(body)], cwd=worktree,
                               env=env, stdout=fh, stderr=subprocess.STDOUT,
                               start_new_session=True)
        mode = re.compile(r"MODE:")
        waited = False
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            fh.flush()
            text = out.read_text(errors="replace")
            waited = waited or "waiting for a heavy slot" in text
            if mode.search(text):
                break
            time.sleep(0.5)
        fh.flush()
        text = out.read_text(errors="replace")
        reached = bool(mode.search(text))
        print(f"RESULT BLOCK while-pool-full waited_line={waited} "
              f"reached_step2={reached} after={seconds}s")
        subprocess.run([py, gate, "--lock-dir", lock, "slot-release", "--label", "hold0",
                        "--slots", str(slots)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        free_deadline = time.monotonic() + 60
        reached_after = reached
        while time.monotonic() < free_deadline and not reached_after:
            fh.flush()
            reached_after = bool(mode.search(out.read_text(errors="replace")))
            if not reached_after:
                time.sleep(0.5)
        print(f"RESULT BLOCK after_release reached_step2={reached_after}")
        print(f"RESULT BLOCK tail={text.strip().splitlines()[-1] if text.strip() else '(no output)'}")
        fh.close()
        for h in holders:
            h.kill()
        if run.poll() is None:
            try:
                os.killpg(os.getpgid(run.pid), 15)
            except ProcessLookupError:
                pass
            try:
                run.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(run.pid), 9)
    return 0


def main() -> int:
    if sys.argv[1] == "cost":
        return cost(sys.argv[2], sys.argv[2:][1:])
    return block(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))


if __name__ == "__main__":
    raise SystemExit(main())
