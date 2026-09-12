#!/usr/bin/env python3
"""D5 document-structure harness.

METRIC: three structural properties of the documentation corpus.

  orphans            documents under docs/ (and the repository-root .md files a
                     reader meets) that no other document links to, reachability
                     computed as a breadth-first walk of markdown links from
                     README.md
  unreachable        the same set restricted to documents a reader is expected to
                     use (docs/*.md excluding plan-*.md and HANDOVER.md)
  level_skips        headings that jump more than one level below their parent
                     (an h2 followed directly by an h4), per document
  max_depth          deepest heading level used, per document
  h1_extra           documents with more than one level-1 heading

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/structure.py
  ... --list      the orphan list and every level skip with its line
  ... --selftest  positive control: README.md is treated as having no outbound
                  links, so every other document must come back unreachable

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6): see RESULT lines.
Counts over file bytes; contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import re
import sys
from collections import deque
from pathlib import Path

ROOT = Path(".").resolve()
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^()\s]+)\)")

# Removed from the finder export by the round-4 preparation script; they exist
# on main, so they are neither orphans nor broken targets.
EXPORT_ABSENT = {"docs/audit-2026-08.md", "docs/audit-2026-09.md", "docs/backlog.md"}

READER_SET = sorted(
    p.relative_to(ROOT).as_posix()
    for p in ROOT.glob("docs/*.md")
    if not p.name.startswith("plan-") and p.name != "HANDOVER.md"
)


def outlinks(rel, blind=()):
    if rel in blind:
        return []
    p = ROOT / rel
    if not p.exists():
        return []
    out, in_fence = [], False
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in LINK.finditer(line):
            t = m.group(1).split("#")[0]
            if not t or t.startswith(("http://", "https://", "mailto:")):
                continue
            cand = (ROOT / rel).parent / t
            try:
                r = os.path.relpath(cand.resolve(), ROOT)
            except Exception:  # noqa: BLE001
                continue
            if r.endswith(".md"):
                out.append(r)
    return out


def headings(rel):
    out, in_fence = [], False
    for i, line in enumerate(
        (ROOT / rel).read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def main():
    listing = "--list" in sys.argv
    blind = ("README.md",) if "--selftest" in sys.argv else ()

    seen, q = {"README.md"}, deque(["README.md"])
    while q:
        cur = q.popleft()
        for nxt in outlinks(cur, blind):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)

    corpus = sorted(
        set(READER_SET)
        | {p.relative_to(ROOT).as_posix() for p in ROOT.glob("docs/*.md")}
        | {"DISCLAIMER.md", "SECURITY.md", "tests/README.md"}
    )
    orphans = [d for d in corpus if d not in seen and d not in EXPORT_ABSENT]
    unreachable = [d for d in READER_SET if d not in seen]

    skips, depths, h1s = [], {}, []
    docs_for_headings = ["README.md"] + READER_SET + ["tests/README.md"]
    for d in docs_for_headings:
        hs = headings(d)
        if not hs:
            continue
        depths[d] = max(h[1] for h in hs)
        n1 = sum(1 for h in hs if h[1] == 1)
        if n1 != 1:
            h1s.append((d, n1))
        prev = None
        for ln, lvl, txt in hs:
            if prev is not None and lvl > prev + 1:
                skips.append((d, ln, prev, lvl, txt))
            prev = lvl

    if listing:
        print("== documents nothing links to (walk from README.md) ==")
        for d in orphans:
            print(f"  ORPHAN {d}")
        print("== reader documents unreachable from README.md ==")
        for d in unreachable:
            print(f"  UNREACHABLE {d}")
        print("== heading level skips ==")
        for d, ln, a, b, txt in skips:
            print(f"  LEVEL-SKIP {d}:{ln} h{a} -> h{b}  {txt[:70]!r}")
        print("== documents without exactly one h1 ==")
        for d, n in h1s:
            print(f"  H1-COUNT {d} = {n}")
        print("== max heading depth ==")
        for d in sorted(depths):
            print(f"  DEPTH {d} = h{depths[d]}")

    print(f"RESULT documents_walked={len(seen)} count")
    print(f"RESULT corpus={len(corpus)} count")
    print(f"RESULT orphans={len(orphans)} count")
    print(f"RESULT reader_docs={len(READER_SET)} count")
    print(f"RESULT unreachable_reader_docs={len(unreachable)} count")
    print(f"RESULT level_skips={len(skips)} count")
    print(f"RESULT docs_without_single_h1={len(h1s)} count")
    print(f"RESULT max_depth={max(depths.values()) if depths else 0} level")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
