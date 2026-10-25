#!/usr/bin/env python3
"""R10-TRAIN-UPGRADE: one mutant per new arm of merge_train.py, against its own self-test.

    python3 dev/audit/harnesses/r10_train_upgrade_mutants.py            # all, 4 at a time
    python3 dev/audit/harnesses/r10_train_upgrade_mutants.py --list     # enumerate only
    python3 dev/audit/harnesses/r10_train_upgrade_mutants.py M0 M5      # named

Run from the branch's worktree. Each mutant replaces exactly one source span of
tools/audit/seat/merge_train.py (the span must occur exactly once, or the
mutant is reported STALE, never silently skipped), writes the result beside the
original as `_mutant_<id>.py` (so ROOT, gh_read and the tool table resolve as
for the real file), runs its `--self-test`, and prints the FAIL lines. M0 is
the unmutated file and must pass; every other mutant must fail at least one
check, else it SURVIVED. The copies are removed whatever happens.
"""
from __future__ import annotations

import concurrent.futures
import subprocess
import sys
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
SRC = ROOT / "tools/audit/seat/merge_train.py"

# (id, arm, the span, its replacement)
MUTANTS = [
    ("M0", "the unmutated head", "", ""),
    # Part 1: step 5's approval, posted.
    ("M1", "land posts the policy approval",
     "            self.policy_approve(pr, h, item, files)\n            under = self.policy_gate(pr, h, files)  # step 5, re-read",
     "            under = self.policy_gate(pr, h, files)  # step 5, re-read"),
    ("M2", "batch admission posts the policy approval",
     "            self.policy_approve(pr, h, item, files)\n            under = self.policy_gate(pr, h, files)  # early",
     "            under = self.policy_gate(pr, h, files)  # early"),
    ("M3", "the mandate must be in force for policy at the post", "        if not live:\n            self.log(f\"#{pr} no policy approval posted: {why}\")",
     "        if False:\n            self.log(f\"#{pr} no policy approval posted: {why}\")"),
    ("M4", "a budget file beside the policy posts nothing",
     "        if any(f.endswith(g.SUFFIX) for f in files):\n            # A budget",
     "        if False:\n            # A budget"),
    ("M5", "an owner approval at the head is not re-posted",
     "            return  # the owner's approval is at the head already",
     "            pass  # the owner's approval is at the head already"),
    ("M6", "mandate_id reads one cited id from a label",
     "        return cited.pop() if len(cited) == 1 else None", "        return None"),
    # Part 2: several batches.
    ("M7", "every batch of the queue runs", "            batches = queue_batches(queue)\n",
     "            batches = queue_batches(queue)[:1]\n"),
    ("M8", "a stop names the batches not run", "        for b in batches[k:]:\n            self.log(\"NOT RUN \"",
     "        for b in []:\n            self.log(\"NOT RUN \""),
    ("M9", "queue_batches refuses a pull request queued twice", "    if twice:\n", "    if False:\n"),
    # Part 3: the live queue.
    ("M10", "the train drains the spool between batches",
     "            added, bad = spool_read(self.state)\n            (self.state / QUEUE_SPOOL)",
     "            added, bad = [], []\n            (self.state / QUEUE_SPOOL)"),
    ("M11", "a drained entry the train holds is not run twice",
     "                if int(e[\"pr\"]) in seen:", "                if False:"),
    ("M12", "one train per state dir (queue.open)",
     "            if held not in (None, os.getpid(), os.getppid()) and pid_alive(held):",
     "            if False:"),
    ("M13", "add is idempotent", "        if str(pr).isdigit() and int(pr) in pending", "        if False and int(pr) in pending"),
    ("M14", "add runs the admission", "        why = t.admit_add(item)\n", "        why = None\n"),
    ("M15", "add holds the lock", "    with queue_lock(t.state):\n        live = read_pid",
     "    with contextlib.nullcontext():\n        live = read_pid"),
    ("M16", "add waits out a closing train.sh", "        if pid_alive(closing):", "        if False:"),
    ("M17", "admit_add: carry", "                if \"CARRY: yes\" not in o:\n                    return (f\"carry:",
     "                if False:\n                    return (f\"carry:"),
    ("M18", "admit_add: row", "            if f\"{ROW_DIR}/{pr}.md\" not in files:\n                return f\"row:",
     "            if False:\n                return f\"row:"),
    ("M19", "admit_add: budget-raise", "            if raises and not held:", "            if False:"),
    ("M20", "admit_add: policy", "            if pol and not self.mandate_id():", "            if False:"),
    ("M21", "admit_add: open", "            if view.get(\"state\") != \"OPEN\":", "            if False:"),
    ("M22", "admit_add: base", "            if view.get(\"baseRefName\") != self.base:", "            if False:"),
    ("M23", "admit_add: shape", "        if not is_sha(v):\n            return f\"shape:", "        if False:\n            return f\"shape:"),
    # P86, carried in: approve once, at admission, and wait the review run out.
    ("M24", "no second approval at a head this train approved", "        if self.approved.get(pr) == h:\n",
     "        if False:\n"),
    ("M25", "no second approval at a head the approver App approved",
     "               and (r.get(\"user\") or {}).get(\"login\") == APPROVER_LOGIN for r",
     "               and False for r"),
    ("M26", "batch entries are approved at admission",
     "            self.log(f\"#{pr} approved at admission ({self.approve(pr, h, item, files)})\")\n", ""),
    ("M27", "the first attempt waits the review run out", "                self.review_settle(pr, h)\n",
     "                self.sleep(30)\n"),
]


def one(m: tuple[str, str, str, str]) -> tuple[str, str, list[str]]:
    mid, _arm, old, new = m
    text = SRC.read_text()
    if old and text.count(old) != 1:
        return mid, "STALE", [f"span occurs {text.count(old)} times"]
    dst = SRC.parent / f"_mutant_{mid}.py"
    try:
        dst.write_text(text.replace(old, new) if old else text)
        r = subprocess.run([sys.executable, str(dst), "--self-test"], cwd=ROOT, capture_output=True, text=True,
                           timeout=1800)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
        if mid == "M0":
            return mid, "PASS" if r.returncode == 0 and not fails else "BROKEN", fails
        return mid, "KILLED" if fails or r.returncode else "SURVIVED", fails or [f"rc {r.returncode}"]
    finally:
        dst.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    if argv[:1] == ["--list"]:
        for mid, arm, _o, _n in MUTANTS:
            print(f"{mid}\t{arm}")
        return 0
    todo = [m for m in MUTANTS if not argv or m[0] in argv]
    bad = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for mid, state, fails in ex.map(one, todo):
            arm = next(a for i, a, _o, _n in MUTANTS if i == mid)
            print(f"{mid} {state}: {arm}")
            for f in fails[:4]:
                print(f"    {f[:200]}")
            bad += state not in ("PASS", "KILLED")
    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
