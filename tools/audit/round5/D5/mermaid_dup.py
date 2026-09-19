#!/usr/bin/env python3
"""D5 harness: duplication between README and docs/*.md, including code fences.

Metric definition (one line): the number of identical non-trivial lines shared
by the ``mermaid`` block under the heading "How the pieces fit" in README.md
and the one under the same heading in docs/architecture.md, after stripping
whitespace and dropping blank lines, bare fence/CJK-free markers and the
``flowchart LR`` opener; call it ``shared_mermaid_lines``.

Paragraph-hash duplication (``dup_paragraphs.py``) reports 0 because it blanks
````` ``` ````` fences; this harness covers the fenced duplication that method
misses. The two blocks claim the same thing -- the system's pieces and their
flow -- and are maintained by hand in two files.

Run from the repository root:
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D5/mermaid_dup.py

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box)
Expected value: RESULT shared_mermaid_lines=14 lines (of 43 in README, 41 in
  architecture.md); RESULT lines_only_in_readme=16 / lines_only_in_architecture=14
  are the already-drifted remainder.

Perturbation the count must move under: re-word one shared node label in
either diagram (a one-line edit) and ``shared_mermaid_lines`` goes down.

This is a pure text instrument: no BLAS, no timing. thread_factor is 1.0.
"""
import os
import re
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.getcwd()
BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"
HEADING = "How the pieces fit"
TRIVIAL = {"", "end", "direction LR", "flowchart LR", "flowchart TB", "```"}


def mermaid_under_heading(path, heading):
    """First fenced ``mermaid`` block after the first line naming `heading`.

    README carries the heading in ``<summary><b>How the pieces fit</b>…`` and
    docs/architecture.md as ``## How the pieces fit``, so match on substring.
    """
    lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    seen_heading = False
    inblock = False
    block = []
    for line in lines:
        s = line.strip()
        if not seen_heading:
            if heading in s:
                seen_heading = True
            continue
        if not inblock:
            if s.startswith("```mermaid"):
                inblock = True
            continue
        if s.startswith("```"):
            break
        block.append(s)
    return block


def nontrivial(block):
    return {b for b in block if b and b not in TRIVIAL
            and not b.startswith("subgraph")}


def main():
    readme = mermaid_under_heading("README.md", HEADING)
    arch = mermaid_under_heading("docs/architecture.md", HEADING)
    if not readme or not arch:
        print("RESULT shared_mermaid_lines=0 lines (block not found)")
        return
    sr, sa = nontrivial(readme), nontrivial(arch)
    shared = sorted(sr & sa)
    print("RESULT readme_mermaid_lines=%d lines" % len(readme))
    print("RESULT architecture_mermaid_lines=%d lines" % len(arch))
    print("RESULT shared_mermaid_lines=%d lines" % len(shared))
    print("RESULT lines_only_in_readme=%d lines" % len(sr - sa))
    print("RESULT lines_only_in_architecture=%d lines" % len(sa - sr))
    for s in shared:
        print("  SHARED %s" % s)
    print("RESULT thread_factor=1.0")
    try:
        print("RESULT load1=%s" % os.getloadavg()[0])
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
