#!/usr/bin/env python3
"""R10-TRAIN-OVERLAP-GRADE part 2: one mutant per arm of merge_train.py's one
admission rule (`already_held`, P129 as amended by P189 and P291), against its
own self-test.

    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py            # all, 4 at a time
    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py --list     # enumerate only
    python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py M0 M5      # named

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
    ("M1", "the drain applies the shared rule, not the any-seen rule",
     '                held = already_held(int(e["pr"]), e.get("verdict"), self._seen, set())',
     '                held = "in this train already" if str(int(e["pr"])) in self._seen else None'),
    ("M2", "a skip takes the entry out of the pending layer",
     '        self.seen_mark(pr, "skipped", cls)  # out of the pending layer',
     '        pass  # out of the pending layer'),
    ("M3", "a BRANCH-POLICY skip is re-admitted at the same verdict",
     'READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)', 'READMIT_SAME_VERDICT = (HOLDER,)'),
    ("M4", "a HOLDER skip is re-admitted at the same verdict",
     'READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)', 'READMIT_SAME_VERDICT = (BRANCH_POLICY,)'),
    ("M5", "the same-verdict exception holds in the drain too, not in add only",
     '                held = already_held(int(e["pr"]), e.get("verdict"), self._seen, set())',
     '                held = already_held(int(e["pr"]), e.get("verdict"), {n: {k: v for k, v in r.items() '
     'if k != "class"} for n, r in self._seen.items()}, set())'),
    ("M6", "every merge attempt refused by the branch policy is classed BRANCH-POLICY",
     'cls=BRANCH_POLICY if BRANCH_POLICY_SAID.search(said) else None)', 'cls=None)'),
    ("M7", "a skipped entry at a new verdict is admitted",
     '        if str(verdict or "") != str(rec.get("verdict") or ""):\n            return None',
     '        if False:\n            return None'),
    ("M8", "an earlier batch's skip never drops a re-added serial entry",
     '            bad = {s["pr"] for s in self.skipped[mine:]}', '            bad = {s["pr"] for s in self.skipped}'),
    ("M9", "a merge is recorded merged", '                self.seen_mark(pr, "merged")\n', ''),
    ("M10", "null control: an entry still to run is ALREADY",
     '    if state == "pending":\n        return "still to run in this train"',
     '    if state == "pending":\n        return None'),
    ("M11", "add reads the live train's record",
     'queue_seen_read(t.state) if live else {}', '{}'),
    ("M12", "a spooled entry is ALREADY", '    if pr in spooled:\n        return', '    if False:\n        return'),
    ("M13", "a pre-flight PARK at recarry is a HOLDER skip",
     '            cls = HOLDER if step == "recarry" else None', '            cls = None'),
    ("M14", "the drain writes a drained entry's record (X7)",
     '                self._seen[str(int(e["pr"]))] = {"verdict": e.get("verdict"), "state": "pending"}',
     '                pass'),
    ("M15", "an old-code train's queue.pending.json reads as pending (X1)",
     '        return {str(int(n)): {"state": "pending"} for n in json.loads((state / QUEUE_PENDING).read_text())}',
     '        return {}'),
    ("M16", "the overlap up-front recarry filters by this batch's skips only (X2)",
     '                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped[mine:]}',
     '                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped}'),
    ("M17", "queue.pending.json lists pending entries only (X5)",
     'for n, r in seen.items() if r.get("state") == "pending")', 'for n, r in seen.items())'),
    ("M18", "a completed batch's unmerged, unskipped entry is marked ran (X3)",
     '                        self.seen_mark(int(e["pr"]), "ran")', '                        pass'),
    ("M19", "a skipped-then-merged entry is cured from the skip report",
     '            self.skipped = [s for s in self.skipped if int(s["pr"]) not in cured]', '            pass'),
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
