#!/usr/bin/env python3
"""The fast-job-name readers' proof (#3902 review, R11-CI-CASE-SELECT P2, #3885).

    python3 dev/audit/harnesses/r11_fast_shards_readers.py WORKTREE

WORKTREE is a scratch checkout of the head under test, which this harness edits: each mutant puts
back one reader's pre-#3902 reading of the job name (or plants the review's run.sh mutant), runs
that reader's own self-test, and restores the file. EXPECTED RESULT: the baseline line reads green
for every self-test, and every mutant line reads KILLED: the check the fix added goes red without
the fix. A SURVIVED line is a check that does not pin its reader.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SELF = {
    "prelude": ["python3", "-I", "tools/ci/prelude.py", "--self-test"],
    "gate": ["python3", "-I", "tools/ci/gate.py", "--self-test"],
    "sweep": ["python3", "-I", "tools/ci/sweep.py", "--self-test"],
    "shards": ["python3", "-I", "tools/ci/shards.py", "--self-test"],
    "probe": ["python3", "tools/audit/seat/probe_bridge.py", "--self-test"],
    "replan": ["python3", "-I", "tools/plan/replan.py", "--self-test"],
}
MUTANTS = [
    ("review: run.sh compares the shard count, not the index", "shards", "tests/run.sh",
     '[ "$owner" != "${FAST_SHARD%/*}" ]', '[ "$owner" != "${FAST_SHARD#*/}" ]'),
    ("prelude: the fast lane owes the unsharded name only", "prelude", "tools/ci/prelude.py",
     'for k in (shards.owed_fast(listed) if (u, n) == ("tests", shards.FAST) else [f"{u} / {n}"])]',
     'for k in [f"{u} / {n}"]]'),
    ("gate.status: the listed shards only, whatever their count", "gate", "tools/ci/gate.py",
     'for m in (shards.owed_fast(jobs) if n == f"tests / {FAST}" else [n])]',
     'for m in ((sorted(x for x in jobs if x.startswith(f"tests / {FAST[:-1]}, ")) or [n]) '
     'if n == f"tests / {FAST}" else [n])]'),
    ("sweep.code_red: the required names only", "sweep", "tools/ci/sweep.py",
     '(n in REQUIRED["no-pr"] or shards.is_fast(n))', 'n in REQUIRED["no-pr"]'),
    ("probe_bridge: the unsharded lane only", "probe", "tools/audit/seat/probe_bridge.py",
     'if not (name.startswith("tests / ") and shards.is_fast(name)) or', 'if name != LANE or'),
    ("replan: the shards are not folded", "replan", "tools/plan/replan.py",
     "    return _fold_fast(best)\n",
     '    return {n: {k: v for k, v in r.items() if k != "finished"} for n, r in best.items()}\n'),
    ("census: a reader dropped from READERS", "shards", "tools/ci/shards.py",
     '    "tools/plan/replan.py": "sharded",\n', ""),
]


def green(root: Path, key: str) -> bool:
    r = subprocess.run(SELF[key], cwd=root, capture_output=True, text=True, timeout=1800)
    return r.returncode == 0


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    root = Path(argv[0]).resolve()
    base = {k: green(root, k) for k in sorted({m[1] for m in MUTANTS})}
    print("BASELINE " + " ".join(f"{k}={'green' if v else 'RED'}" for k, v in base.items()))
    if not all(base.values()):
        return 1
    survived = 0
    for name, key, rel, old, new in MUTANTS:
        p = root / rel
        text = p.read_text()
        if text.count(old) != 1:
            print(f"UNPLANTED {name}: the site occurs {text.count(old)} times in {rel}")
            survived += 1
            continue
        p.write_text(text.replace(old, new))
        try:
            killed = not green(root, key)
        finally:
            p.write_text(text)
        survived += not killed
        print(f"{'KILLED  ' if killed else 'SURVIVED'} {name}")
    print(f"READERS MUTANTS: {len(MUTANTS) - survived} of {len(MUTANTS)} killed")
    return 1 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
