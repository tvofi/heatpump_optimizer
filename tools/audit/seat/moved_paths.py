#!/usr/bin/env python3
"""List every reference a file makes to a path the reorganisation moved.

    python3 tools/audit/seat/moved_paths.py <file>...
    python3 tools/audit/seat/moved_paths.py --self-test

WHY THIS EXISTS (#1990's RCA, dev/audit/rca/R9-RCA-1990.md). The RO moves left
seat instruments invoking paths they had emptied. merge_train.py could not
carry a verdict, and a generated prompt sent seats to tools/audit/briefs/. The
first search matched script paths only, so it missed the directory.

WHAT IT READS: tests/layout.json. A moved path is one of:
  - a `retired` entry's `old` that is no longer tracked;
  - that entry's parent directory, when no tracked file is left under it;
  - a `lifted` prefix.

WHAT IT PRINTS: one line per hit, as `file:line: [TAG] old -> new | text`.
  - FALLBACK: the same line also names the new path, the old-path-first
    convention the moves set.
  - STALE?: anything else. A reader dispositions each one: a fallback split
    across lines, a lifted prefix whose generated copy stays, or a defect.
The run ends with a count line. Exit 0 always: this is an enumeration a
reader dispositions, not a gate.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def moved_paths(layout: dict, tracked: set[str]) -> dict[str, str]:
    dirs = {"/".join(p.split("/")[:i]) + "/" for p in tracked for i in range(1, p.count("/") + 1)}
    moved: dict[str, str] = {}
    for e in layout.get("retired", []):
        old, new = e["old"], e.get("new")
        if old in tracked:
            continue  # planned, not yet done
        moved[old] = new or "(retired)"
        parent = str(Path(old).parent) + "/"
        if parent != "./" and parent not in dirs:
            moved.setdefault(parent, (str(Path(new).parent) + "/") if new else "(retired)")
    for e in layout.get("lifted", []):
        moved[e["old"]] = e["new"]
    return moved


def scan(files: list[str], moved: dict[str, str]) -> list[str]:
    out = []
    order = sorted(moved.items(), key=lambda kv: -len(kv[0]))
    for f in files:
        for n, line in enumerate(Path(f).read_text(encoding="utf-8").splitlines(), 1):
            for old, new in order:
                if old in line:
                    tag = "FALLBACK" if new != "(retired)" and new in line else "STALE?"
                    out.append(f"{f}:{n}: [{tag}] {old} -> {new} | {line.strip()[:150]}")
                    break
    return out


def _self_test() -> int:
    layout = {"retired": [{"old": "a/old/x.sh", "new": "b/x.sh"},
                          {"old": "keep/y.sh", "new": "c/y.sh"}],
              "lifted": [{"old": "r/", "new": "g/r/"}]}
    tracked = {"b/x.sh", "keep/y.sh", "keep/z.sh"}
    m = moved_paths(layout, tracked)
    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        fails += not cond
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    check("a retired file no longer tracked is moved", m.get("a/old/x.sh") == "b/x.sh")
    check("its emptied parent directory is moved", m.get("a/old/") == "b/")
    check("a retired entry still tracked is a planned move, not a moved path", "keep/y.sh" not in m)
    check("a lifted prefix is moved", m.get("r/") == "g/r/")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "s.sh"
        f.write_text("see `a/old/` here\nif test -f a/old/x.sh; then p=a/old/x.sh; else p=b/x.sh; fi\nclean line\n")
        hits = scan([str(f)], m)
    check("a directory reference is found and marked STALE?", len(hits) == 2 and "[STALE?] a/old/ -> b/" in hits[0])
    check("an old-first fallback naming the new path is marked FALLBACK", "[FALLBACK] a/old/x.sh -> b/x.sh" in hits[1])
    print(f"moved_paths self-test: 6 checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    layout = json.loads((ROOT / "tests/layout.json").read_text())
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    m = moved_paths(layout, tracked)
    hits = scan(argv, m)
    print("\n".join(hits) if hits else "", end="\n" if hits else "")
    print(f"moved_paths: {len(m)} moved path(s) from tests/layout.json, {len(hits)} hit(s) in {len(argv)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
