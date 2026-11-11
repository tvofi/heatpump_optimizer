"""PREPR-SLOT-LIVELOCK (R10-PREPR-RESIDUE carry 6): does a nested prepr queue?

    python3 dev/audit/harnesses/prepr_slot_nested.py

Holds all four heavy slots in a private HPO_GATE_LOCK_DIR with live pids, then
runs `tools/pr/prepr.sh --self-test` (the nested run of step 3h) two ways:

  labelled   HPO_SLOT_LABEL=outer, as an outer prepr that holds a slot exports
             it. Expected: the run completes (rc 0) and never queues.
  bare       no HPO_SLOT_LABEL (the null control). Expected: the run cannot
             finish inside the bound, because it queues for a slot.

A direct `gate_lock.py slot-take` with every slot held is the second control:
it must be still waiting at the bound, so the held pool is genuinely full.

RESULT labelled_rc=0
RESULT labelled_queued=0
RESULT bare_finished=0
RESULT direct_take_finished=0

Last measured: the labelled nested self-test runs to rc 0 without a slot or
queue line, so the livelock is not reproduced with the label inherited.
Reads and writes only a temp lock dir; touches no repository state.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BARE_BOUND_S = 40       # a bare run must still be waiting at this bound
LABELLED_BOUND_S = 900  # the self-test is a few hundred rows


def run(cmd: list[str], env: dict[str, str], bound: int) -> tuple[bool, int | None, str]:
    """(finished, returncode, combined output) for a command bounded in seconds."""
    p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=bound)
        return True, p.returncode, out
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9)
        out, _ = p.communicate()
        return False, None, out or ""


def main() -> int:
    lock = tempfile.mkdtemp(prefix="hpo-slot-nested-")
    holders = [subprocess.Popen(["sleep", "3600"]) for _ in range(4)]
    base = {k: v for k, v in os.environ.items() if k != "HPO_SLOT_LABEL"}
    base["HPO_GATE_LOCK_DIR"] = lock
    try:
        for i, h in enumerate(holders):
            subprocess.run([sys.executable, "tests/gate_lock.py", "slot-take", "--label",
                            f"held-{i}", "--owner-pid", str(h.pid), "--no-wait"],
                           cwd=ROOT, env=base, check=True, capture_output=True)
        status = subprocess.run([sys.executable, "tests/gate_lock.py", "slot-status"],
                                cwd=ROOT, env=base, capture_output=True, text=True).stdout
        print(status.strip())
        t0 = time.time()
        fin, rc, out = run(["bash", "tools/pr/prepr.sh", "--self-test"],
                           {**base, "HPO_SLOT_LABEL": "outer"}, LABELLED_BOUND_S)
        queued = int("queue" in out.lower() or "waiting" in out.lower())
        print(f"RESULT labelled_rc={rc if fin else 'timeout'}")
        print(f"RESULT labelled_queued={queued}  ({time.time() - t0:.0f}s)")
        fin, _, _ = run(["bash", "tools/pr/prepr.sh", "--self-test"], base, BARE_BOUND_S)
        print(f"RESULT bare_finished={int(fin)}")
        fin, _, _ = run([sys.executable, "tests/gate_lock.py", "slot-take", "--label",
                         "bare-direct", "--owner-pid", str(os.getpid())], base, 10)
        print(f"RESULT direct_take_finished={int(fin)}")
    finally:
        for h in holders:
            h.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
