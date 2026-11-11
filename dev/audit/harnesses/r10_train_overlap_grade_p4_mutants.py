#!/usr/bin/env python3
"""R10-TRAIN-OVERLAP-GRADE part 4: one mutant per arm of merge_train.py's batch
admission required set (P34's sibling seam), `add --front` / `add --remove`
(P112), and the four #2992 review survivors (R3, R5, R8, R9), against its own
self-test.

    python3 dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py            # all, 4 at a time
    python3 dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py --list     # enumerate only
    python3 dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py M0 M5      # named

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
    ("M1", "batch admission waits a head on the PR-head required set",
     '            head_req = self.required(pr_head=True)', '            head_req = self.required()'),
    ("M2", "--front puts the spooled entry first",
     'spool_rewrite(t.state, (mine + rest) if op == "front" else rest)',
     'spool_rewrite(t.state, (rest + mine) if op == "front" else rest)'),
    ("M3", "--remove drops the entry's line",
     'spool_rewrite(t.state, (mine + rest) if op == "front" else rest)',
     'spool_rewrite(t.state, (mine + rest) if op == "front" else raw)'),
    ("M4", "an absent PR is refused and nothing written",
     '    if not mine:\n        t.log(f"{op.upper()} REFUSED', '    if False:\n        t.log(f"{op.upper()} REFUSED'),
    ("M5", "the spool edit holds QUEUE_LOCK",
     '    with queue_lock(t.state):\n        return spool_edit_locked(t, pr, op)',
     '    if True:\n        return spool_edit_locked(t, pr, op)'),
    ("M6", "--front on a new entry into a live train spools it first",
     '                spool_rewrite(t.state, raw[-1:] + raw[:-1])', '                pass'),
    ("M7", "--front with no live train queues the entry first",
     '        queue = [entry] + spooled if front else spooled + [entry]', '        queue = spooled + [entry]'),
    ("M8", "R3: a critical-path entry that stops still sweeps the record PR",
     '                    self.sweep_bots()  # the entry stopped: the record PR waits no longer',
     '                    pass  # the entry stopped: the record PR waits no longer'),
    ("M9", "R5: CHANGES_REQUESTED is no approval-class refusal",
     'f"at {h[:8]}"), False, rd != "CHANGES_REQUESTED"', 'f"at {h[:8]}"), False, True'),
    ("M10", "R9: BLOCKED with every required context green is a review refusal",
     '        if rd in ("REVIEW_REQUIRED", "CHANGES_REQUESTED") or ms == "BLOCKED":',
     '        if rd in ("REVIEW_REQUIRED", "CHANGES_REQUESTED"):'),
    ("M11", "R8: _critical maps the branch's group against the critical path",
     '            return bool(gid) and roster_lib.norm_group(gid) in crit', '            return False'),
    ("M12", "R8: a roster read that raises is not retried per entry",
     '                self.cp_read = ({}, set())  # first: a read that raises is not retried per entry',
     '                pass  # first: a read that raises is not retried per entry'),
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
