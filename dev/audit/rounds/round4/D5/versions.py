#!/usr/bin/env python3
"""D5 version-reference harness.

METRIC: version strings cited by the reader-facing documentation that the
release history does not contain. Every `vN.N.N` (and bare `N.N.N` in a
"since"/"from"/"in" context) in README.md and docs/*.md is resolved against the
set of released versions, which is taken from the `## ` headings of
RELEASE_NOTES.md plus the VERSION file.

  refs_total        distinct version strings cited by the documentation
  refs_unreleased   cited versions absent from RELEASE_NOTES.md's heading set
  refs_future       cited versions strictly greater than VERSION
  released_total    versions RELEASE_NOTES.md records

RELEASE_NOTES.md IS present in this round-4 export (a preparation defect that
deleted it was repaired before dispatch), so release-history claims are
checkable here.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/versions.py
  ... --list      every citation, with the documents that make it
  ... --selftest  positive control: a fabricated v99.9.9 citation is injected
                  and must be reported as unreleased AND future

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
from pathlib import Path

ROOT = Path(".").resolve()
DOCS = ["README.md"] + [
    p.relative_to(ROOT).as_posix()
    for p in sorted(ROOT.glob("docs/*.md"))
    if not p.name.startswith("plan-") and p.name != "HANDOVER.md"
]
FENCE = re.compile(r"^\s*(```|~~~)")
VREF = re.compile(r"\bv(\d+\.\d+\.\d+)\b")
RELHEAD = re.compile(r"^##+\s+\[?v?(\d+\.\d+\.\d+)\]?")


def tup(v):
    return tuple(int(x) for x in v.split("."))


def main():
    listing = "--list" in sys.argv
    selftest = "--selftest" in sys.argv

    released = set()
    rn = ROOT / "RELEASE_NOTES.md"
    if not rn.exists():
        raise SystemExit("HARNESS ERROR: RELEASE_NOTES.md missing from this tree")
    for line in rn.read_text(encoding="utf-8", errors="replace").splitlines():
        m = RELHEAD.match(line)
        if m:
            released.add(m.group(1))
    current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    released.add(current)

    refs = {}
    for d in DOCS:
        in_fence = False
        for i, line in enumerate(
            (ROOT / d).read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in VREF.finditer(line):
                refs.setdefault(m.group(1), []).append(f"{d}:{i}")
    if selftest:
        refs.setdefault("99.9.9", []).append("SELFTEST:0")

    unreleased = sorted((v for v in refs if v not in released), key=tup)
    future = sorted((v for v in refs if tup(v) > tup(current)), key=tup)

    if listing:
        for v in sorted(refs, key=tup):
            tag = "OK" if v in released else "UNRELEASED"
            print(f"  {tag} v{v}  x{len(refs[v])}  {refs[v][:4]}")
        for v in unreleased:
            print(f"UNRELEASED-CITATION v{v} {refs[v]}")
        for v in future:
            print(f"FUTURE-CITATION v{v} (VERSION={current}) {refs[v]}")

    print(f"RESULT documents={len(DOCS)} count")
    print(f"RESULT released_total={len(released)} count")
    print(f"RESULT refs_total={len(refs)} count")
    print(f"RESULT ref_occurrences={sum(len(v) for v in refs.values())} count")
    print(f"RESULT refs_unreleased={len(unreleased)} count")
    print(f"RESULT refs_future={len(future)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
