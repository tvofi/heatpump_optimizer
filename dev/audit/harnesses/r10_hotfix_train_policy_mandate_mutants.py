#!/usr/bin/env python3
"""R10-HOTFIX-TRAIN-POLICY-MANDATE (#3366): one mutant per arm of the pre-flight's
policy read, against queue_pre_flight.py's own self-test.

    python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py          # all, serially
    python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py --list   # enumerate only
    python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py P0 P3    # named

Run from the branch's worktree, on a committed tree. queue_pre_flight.py imports
merge_train.py as a module, so a `_mutant_*.py` copy beside it would never be
imported: each mutant rewrites its one span IN PLACE (the span must occur
exactly once, else STALE, never skipped), runs the self-test, and is restored
from HEAD -- under `mutant_guard`, which also restores on SIGTERM/SIGINT and
refuses to start on a dirty file. P0 is the unmutated tree and must pass;
every other mutant must fail at least one check, else it SURVIVED (rc 1).
"""
from __future__ import annotations

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
MT = "tools/audit/seat/merge_train.py"
PF = "tools/audit/seat/queue_pre_flight.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402

# (id, arm, file, the span, its replacement)
MUTANTS = [
    ("P0", "the unmutated head", PF, "", ""),
    ("P1", "the pre-flight reads policy_admits, not policy_gate alone (the #3366 defect itself)", PF,
     "            self.t.policy_admits(pr, h, item, files)\n",
     "            self.t.policy_gate(pr, h, files)\n"),
    ("P2", "policy_admits judges the approval the --mandate is due to post", MT,
     "        if cid is not None:\n            g = _mandate_gate()\n            posting = {",
     "        if False:\n            g = _mandate_gate()\n            posting = {"),
    ("P3", "null arm: a mandate not in force for policy merging (revoked, expired, scope) posts nothing", MT,
     "        return (cid if live else None), pol, why\n",
     "        return cid, pol, why\n"),
    ("P4", "null arm: a train with no --mandate posts nothing", MT,
     "        cid = self.mandate_id()\n        pol = self.policy_paths(files) if cid else []\n",
     "        cid = self.mandate_id() or MID\n        pol = self.policy_paths(files) if cid else []\n"),
    ("P5", "a park under a --mandate that posts nothing names the mandate's reason", MT,
     "                s.why = f\"{s.why}; the train posts no approval under its --mandate: {why}\"\n",
     "                pass\n"),
    ("P6", "the unposted approval is judged beside the reviews read, never instead of them", MT,
     "            reviews = [r for page in json.loads(o) for r in page] + ([posting] if posting else [])\n",
     "            reviews = [posting] if posting else [r for page in json.loads(o) for r in page]\n"),
    ("P7", "the pre-flight posts nothing", MT,
     "        try:\n            return self.policy_gate(pr, h, files, posting=posting)\n",
     "        try:\n            self.policy_approve(pr, h, item, files)\n"
     "            return self.policy_gate(pr, h, files, posting=posting)\n"),
]


def one(m: tuple[str, str, str, str, str]) -> tuple[str, str, list[str]]:
    mid, _arm, rel, old, new = m
    path = ROOT / rel
    text = path.read_text()
    if old and text.count(old) != 1:
        return mid, "STALE", [f"span occurs {text.count(old)} times in {rel}"]
    try:
        if old:
            path.write_text(text.replace(old, new))
        r = subprocess.run([sys.executable, str(ROOT / PF), "--self-test"], cwd=ROOT,
                           capture_output=True, text=True, timeout=1200)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
        if mid == "P0":
            return mid, "PASS" if r.returncode == 0 and not fails else "BROKEN", fails
        return mid, "KILLED" if fails or r.returncode else "SURVIVED", fails or [f"rc {r.returncode}"]
    finally:
        path.write_text(text)


def main(argv: list[str]) -> int:
    if argv[:1] == ["--list"]:
        for mid, arm, rel, _o, _n in MUTANTS:
            print(f"{mid}  {rel}: {arm}")
        return 0
    pick = [m for m in MUTANTS if not argv or m[0] in argv]
    mutant_guard.arm([MT, PF])
    bad = 0
    for m in pick:
        mid, verdict, lines = one(m)
        bad += verdict not in ("PASS", "KILLED")
        print(f"{mid} {verdict}: {m[1]}")
        for ln in lines[:4]:
            print(f"    {ln}")
    print(f"{len(pick)} mutant(s), {bad} not as required")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
