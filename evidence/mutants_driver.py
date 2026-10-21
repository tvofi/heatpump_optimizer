#!/usr/bin/env python3
"""Re-run the PR's nine claimed mutants against the head, one at a time.

Each mutation is applied in place, the named acceptance/self-test command is
run, its rc and FAIL lines recorded, and the file restored from a pristine
copy. Prints one table. Reviewer-authored (fix-review.md step 1).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

WT = Path("/Users/timmalmstrom/hpo-seats/r10s3/r10-gate-priority-review/wt")
EV = Path("/Users/timmalmstrom/hpo-seats/r10s3/r10-gate-priority-review/evidence")
GL = WT / "tests" / "gate_lock.py"
GP = WT / "tools" / "pr" / "gate_priority.py"
ENV = {"PATH": "/Users/timmalmstrom/.local/state/hpo/bin:" + str(Path.home() / ".local/state/hpo/bin") + ":/usr/bin:/bin:/usr/sbin:/sbin",
       "PYTHONPATH": "tests/hastub", "HOME": str(Path.home())}

MUTANTS = [
    # id, file key, old, new, command, label
    ("a", "gl",
     "            live.append((-waiter.effective(now), path.name, waiter))",
     "            live.append((0, path.name, waiter))",
     "accept", "_queue sort key drops -effective"),
    ("b", "gl",
     "    tmp = _ticket_tmp(lock_dir, label, priority, _ticket_queued_at(ticket))",
     "    tmp = _ticket_tmp(lock_dir, label, PRIORITY_NORMAL, _ticket_queued_at(ticket))",
     "accept", "_enqueue rewrites PRIORITY_NORMAL"),
    ("c", "gl",
     "        if now - self.queued_at >= timedelta(seconds=PRIORITY_AGING_SECONDS):\n"
     "            return PRIORITY_MAX\n"
     "        return self.priority",
     "        return self.priority",
     "accept", "aging removed"),
    ("d", "gl",
     "    try:\n        value = int(str(raw).strip())\n    except ValueError:\n        return PRIORITY_NORMAL\n",
     "    value = int(str(raw).strip())\n",
     "accept", "_read_priority try/except deleted"),
    ("g", "gl",
     "        if _orphaned(pool, owner) or (owner.expired and owner.pid is None):",
     "        if owner.expired or _orphaned(pool, owner):",
     "accept", "_free_slot steals a live holder"),
    ("h", "gl",
     "    holder_pid = owner_pid if owner_pid is not None else os.getpid()",
     "    holder_pid = owner_pid",
     "accept", "no pid when caller names none"),
    ("i", "gl",
     "    past_lease = [\n        f\"{i}:{owner.label}\" for i, owner in enumerate(holders)\n"
     "        if owner is not None and owner.expired\n"
     "        and owner.pid is not None and _pid_alive(owner.pid)\n    ]",
     "    past_lease = []",
     "accept", "witnesses not reported (past_lease)"),
    ("i", "gl",
     '        "unleased": _unleased(pool) if pool.exists() else [],',
     '        "unleased": [],',
     "accept", "witnesses not reported (unleased)"),
    ("e", "gp",
     "        listed = roster_lib.norm_group(str(group)) in critical\n        return CRITICAL_PRIORITY if listed else PRIORITY_NORMAL",
     "        listed = roster_lib.norm_group(str(group)) in critical\n        return CRITICAL_PRIORITY",
     "selftest", "derived default always 1"),
    ("f", "gp",
     "        listed = roster_lib.norm_group(str(group)) in critical\n        return CRITICAL_PRIORITY if listed else PRIORITY_NORMAL",
     "        listed = roster_lib.norm_group(str(group)) in critical\n        return PRIORITY_NORMAL",
     "selftest", "derived default always 0"),
]

RESTORE = {"gl": GL.read_bytes(), "gp": GP.read_bytes()}


def run(cmd):
    if cmd == "accept":
        argv = [sys.executable, "tests/gate_lock.py", "--accept"]
    else:
        argv = [sys.executable, "tools/pr/gate_priority.py", "--self-test"]
    r = subprocess.run(argv, cwd=str(WT), capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout + r.stderr


def restore():
    GL.write_bytes(RESTORE["gl"])
    GP.write_bytes(RESTORE["gp"])


for mid, which, old, new, cmd, label in MUTANTS:
    path = GL if which == "gl" else GP
    s = path.read_text()
    if s.count(old) != 1:
        print(f"MUTANT {mid} SKIP: pattern count {s.count(old)} != 1 ({label})")
        continue
    path.write_text(s.replace(old, new))
    rc, out = run(cmd)
    restore()
    fails = [ln.strip() for ln in out.splitlines()
             if ln.strip().startswith("FAIL") or "FAILED" in ln or "PASSED" in ln]
    print(f"=== MUTANT ({mid}) {label} | rc={rc} ===")
    for ln in fails[:6]:
        print("   ", ln)
    if rc == 0:
        print("    *** rc=0: mutant did NOT redden ***")
    print()

restore()
print("RESTORED: git diff should be empty")
print(subprocess.run(["git", "-C", str(WT), "diff", "--stat"], capture_output=True, text=True).stdout or "(clean)")
