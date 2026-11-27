#!/usr/bin/env python3
"""Replay PR-side main merges and count conflicts per file, before and after (R11-OWNER-HOTFILE-COUNTS).

    python3 dev/audit/harnesses/hotfile_conflicts.py [--main <sha>] [--days 10]

The window: every pull request merged into ``--main``'s first-parent history in
the ``--days`` before ``--main``'s commit time. For each, every merge commit on
the pull request's side whose subject merges main (``origin/main``, ``branch
'main'``) is re-merged with ``git merge-tree --write-tree`` three ways:

  * ``before`` -- under the merge's own first parent's ``.gitattributes``
    (``--attr-source``), the routing the merge actually had;
  * ``driver`` -- under this checkout's ``.gitattributes``, so the D6 register
    goes to ``tools/merge/ledger_merge.py``'s row arm;
  * ``after`` -- the ``driver`` merge, and each hot text file re-merged with
    ``git merge-file`` after the passages main has stopped storing are replaced,
    on all three sides, by main's current text of that passage (ANCHORS): what
    the merge would have met had the file carried main's form.

A file absent from ANCHORS is never rewritten, so its ``after`` count is its
``driver`` count; ``other files`` is the null control that the routing moves
nothing it does not route. The merge driver must be installed
(``python3 tools/merge/ledger_merge.py --install``) and git must be 2.40 or
later; anything but merge-tree's exit 0 or 1 refuses (exit 2).
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOT = (
    "tests/deployment_shape.py",
    "docs/architecture.md",
    "dev/audit/rounds/round4/D6/claims.json",
    "dev/audit/rounds/round4/D6/claims.md",
    "dev/audit/rounds/round4/D6/claims.py",
)
#: Per hot text file, the passages (start anchor, end anchor) main no longer
#: stores a derived value in: everything from the start line up to, not
#: including, the end line is replaced by main's current text of it.
ANCHORS = {
    "tests/deployment_shape.py": [("COST OF THE SHAPE", "    python tests/deployment_shape.py")],
    "dev/audit/rounds/round4/D6/claims.py": [
        ("    RESULT arch_", "INSTRUMENTED SYMBOLS"),
        ("_disk = sorted(", 'claim("C35"'),
    ],
    "docs/architecture.md": [
        ("knows nothing about Home Assistant:", "function, and the rest take numbers"),
        ("## The Home Assistant boundary", "`config_flow`, `coordinator`"),
        ("clock function was injected.", "directly by `tests/features.py`"),
    ],
}
MAIN_MERGE = re.compile(r"origin/main|branch 'main'")


def git(*a: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"REFUSED: git {' '.join(a[:3])} exited {r.returncode}: {r.stderr.strip()[:200]}")
    return r


def passage(text: str, start: str, end: str) -> tuple[int, int] | None:
    lines = text.split("\n")
    s = next((i for i, ln in enumerate(lines) if ln.startswith(start)), None)
    if s is None:
        return None
    e = next((i for i in range(s + 1, len(lines)) if lines[i].startswith(end)), None)
    return None if e is None else (s, e)


def normalise(text: str, path: str, main_text: str) -> str:
    for start, end in ANCHORS.get(path, ()):
        here, there = passage(text, start, end), passage(main_text, start, end)
        if here is None or there is None:
            continue
        lines, mlines = text.split("\n"), main_text.split("\n")
        text = "\n".join(lines[:here[0]] + mlines[there[0]:there[1]] + lines[here[1]:])
    return text


def conflicted(attr: str, p1: str, p2: str) -> list[str]:
    r = git(f"--attr-source={attr}", "merge-tree", "--write-tree", "--name-only",
            "--no-messages", p1, p2, check=False)
    if r.returncode not in (0, 1):
        sys.exit(f"REFUSED: merge-tree exited {r.returncode} on {p1[:12]} {p2[:12]}: "
                 f"{r.stderr.strip()[:200]} (git 2.40+ for --attr-source)")
    return r.stdout.splitlines()[1:] if r.returncode == 1 else []


def blob(rev: str, path: str) -> str:
    r = git("show", f"{rev}:{path}", check=False)
    return r.stdout if r.returncode == 0 else ""


def text_conflicts(path: str, base: str, p1: str, p2: str, main: str) -> bool:
    m = blob(main, path)
    with tempfile.TemporaryDirectory() as td:
        files = []
        for name, rev in (("ours", p1), ("base", base), ("theirs", p2)):
            f = Path(td, name)
            f.write_text(normalise(blob(rev, path), path, m))
            files.append(str(f))
        r = subprocess.run(["git", "merge-file", "-q", "-p", *files], capture_output=True)
    if r.returncode < 0 or r.returncode > 127:
        sys.exit(f"REFUSED: merge-file exited {r.returncode} on {path}")
    return r.returncode != 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="ef797d794017c98f7fb2d8a168d7de63d435ef3b")
    ap.add_argument("--days", type=int, default=10)
    a = ap.parse_args()
    main_sha = git("rev-parse", a.main).stdout.strip()
    end = int(git("log", "-1", "--format=%ct", main_sha).stdout)
    since = end - a.days * 86400
    prs = [ln.split()[0] for ln in git("log", "--merges", "--first-parent", "--format=%H %ct",
                                       main_sha).stdout.splitlines()
           if int(ln.split()[1]) >= since]
    merges = []
    for pr in prs:
        side = git("rev-list", "--merges", "--format=%H %P%n%s", f"{pr}^1..{pr}^2").stdout
        lines = [ln for ln in side.splitlines() if not ln.startswith("commit ")]
        for head, subj in zip(lines[::2], lines[1::2]):
            if MAIN_MERGE.search(subj):
                merges.append(head.split()[:3])
    count = {k: collections.Counter() for k in ("before", "driver", "after")}
    with_any = collections.Counter()
    for m, p1, p2 in merges:
        before = set(conflicted(p1, p1, p2))
        driver = set(conflicted("HEAD", p1, p2))
        base = git("merge-base", p1, p2).stdout.split()[0]
        after = {f for f in driver
                 if f not in ANCHORS or text_conflicts(f, base, p1, p2, main_sha)}
        for k, s in (("before", before), ("driver", driver), ("after", after)):
            count[k].update(s)
            with_any[k] += bool(s)
    print(f"window: {len(prs)} pull requests merged into {main_sha[:10]}'s first parent "
          f"in {a.days} days; {len(merges)} main merges on their branches")
    print(f"{'file':44} {'before':>6} {'driver':>6} {'after':>6}")
    for f in HOT:
        print(f"{f:44} {count['before'][f]:>6} {count['driver'][f]:>6} {count['after'][f]:>6}")
    other = {k: sum(n for f, n in c.items() if f not in HOT) for k, c in count.items()}
    print(f"{'other files':44} {other['before']:>6} {other['driver']:>6} {other['after']:>6}")
    print(f"{'merges with any conflict':44} {with_any['before']:>6} {with_any['driver']:>6} "
          f"{with_any['after']:>6}")
    for f in sorted({f for c in count.values() for f in c if f not in HOT}):
        if len({count[k][f] for k in count}) > 1:
            print(f"OTHER-FILE-MOVED {f}: " + " ".join(f"{k}={count[k][f]}" for k in count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
