#!/usr/bin/env python3
"""D10-02 (seat 1 own harness) — 'Known limitations' discoverability in user docs.

METRIC (own, differs from the finder's): over EVERY markdown file a user or a
fresh maintainer can open -- README.md plus ALL of docs/*.md (the finder
restricted to README + six named user docs; this run also reports that
restricted set for comparability, and the full set as the attack) -- count
(a) ATX headings of depth 1-6 whose text matches /known limitation/i,
(b) occurrences of the word 'limitation' (any inflection) anywhere,
(c) near-synonym headings: /caveat|boundary|boundaries|gotcha|known issue|what .*won'?t/i,
(d) total lines scanned.
Prints RESULT lines. A heading count of 0 over the full set is a stronger
statement than over the six-file set: it rules out the finder having scoped
the grep too narrowly.

RUN (from the worktree root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/d10_own_D10-02.py

EXPECTED (if the finding holds): headings_known_limitation_full=0 (tolerance 0)
BASELINE measured at 7dd68dd; this run is at branch head 0855277 (no user-doc
file changed between the two: git diff --stat 7dd68dd..0855277 -- README.md
docs/architecture.md docs/automations.md docs/configuration.md
docs/dashboard-card.md docs/ecl110.md docs/how-it-works.md is empty).
MACHINE: 8-core Apple M1, macOS 25.6.0. Counts, not timings.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PKG_DOC = ROOT / "custom_components" / "heatpump_optimizer" / "README.md"

FINDER_SIX = [
    ROOT / "README.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "automations.md",
    ROOT / "docs" / "configuration.md",
    ROOT / "docs" / "dashboard-card.md",
    ROOT / "docs" / "ecl110.md",
    ROOT / "docs" / "how-it-works.md",
]

HEADING = re.compile(r"^#{1,6}[^\n]*known limitation", re.I | re.M)
WORD = re.compile(r"limitation", re.I)
SYNONYM_HEADING = re.compile(
    r"^#{1,6}[^\n]*(caveat|boundar|gotcha|known issue|will not|won't|cannot do)", re.I | re.M
)


def scan(files: list[Path]) -> dict[str, int]:
    text = "\n".join(f.read_text(encoding="utf-8") for f in files if f.exists())
    return {
        "headings": len(HEADING.findall(text)),
        "word": len(WORD.findall(text)),
        "synonym_headings": len(SYNONYM_HEADING.findall(text)),
        "lines": text.count("\n") + 1,
        "files": sum(1 for f in files if f.exists()),
    }


def main() -> int:
    full = sorted([ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))])
    six = scan(FINDER_SIX)
    ful = scan(full)
    extra = [f.name for f in full if f not in FINDER_SIX]

    pkg = scan([PKG_DOC]) if PKG_DOC.exists() else {"headings": -1, "word": -1}

    print(f"RESULT six_set_headings_known_limitation={six['headings']} headings")
    print(f"RESULT six_set_word_limitation={six['word']} occurrences")
    print(f"RESULT six_set_lines={six['lines']} lines")
    print(f"RESULT full_set_files={ful['files']} markdown_files")
    print(f"RESULT full_set_headings_known_limitation={ful['headings']} headings")
    print(f"RESULT full_set_word_limitation={ful['word']} occurrences")
    print(f"RESULT full_set_synonym_headings={ful['synonym_headings']} headings")
    print(f"RESULT full_set_lines={ful['lines']} lines")
    print(f"RESULT files_beyond_finder_six={len(extra)}: {' '.join(extra)}")
    print(f"RESULT package_readme_headings_known_limitation={pkg['headings']} headings")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=n/a (counts, not timings)")
    ok = ful["headings"] == 0
    print("VERDICT docs-known-limitations=" + ("absent_everywhere" if ok else "PRESENT"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
