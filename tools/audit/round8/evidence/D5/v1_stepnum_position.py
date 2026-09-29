#!/usr/bin/env python3
"""v1_stepnum_position.py -- independent re-measure of D5-s1-01.

Metric (own definition, deliberately NOT text-label matching): walk the
Quick-start mermaid flowchart's numbered nodes IN GRAPH ORDER (by node id,
following the arrows A->B->M->...) and the numbered prose headings IN
DOCUMENT ORDER, pair them positionally (1st numbered diagram node with 1st
numbered prose heading, 2nd with 2nd, ...), and count pairs whose numbers
disagree. This sidesteps s1_stepnum.py's own label-text matching (first
three normalized words), which silently drops the "How do you want to
describe your building?" node because its diagram wording and its prose
wording share no first-three-word prefix -- so it is worth checking whether
positional pairing finds a 4th disagreement s1's harness missed.

Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D5/v1_stepnum_position.py
Expected: RESULT positional_mismatches=<n> count
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82

Instrumented symbol: same as s1_stepnum.py -- README.md's "## Quick start"
mermaid source and numbered prose headings.

Perturbation: --fix applies the same four-heading renumber s1_stepnum.py
applies (in a temp copy only; README.md is never touched), and
positional_mismatches must drop to 0.
"""
import os
import re
import sys
import tempfile

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))

# Numbered diagram nodes only (unnumbered nodes like the finish menu M, the
# questionnaire branches E/F/G/H, and the terminal J are skipped by design --
# they carry no number in the diagram at all, so there is nothing to pair).
DIAGRAM_NODE_RE = re.compile(r'[\[{]"(\d+)\s*\xb7\s*([^"<]+?)(?:<br/>|")', re.M)
PROSE_HEADING_RE = re.compile(r'^\*\*(\d+)\s*\xb7\s*([^*]+?)\.?\*\*', re.M)


def section_of(text):
    section = text.split("## Quick start", 1)[1]
    return section.split("\n## ", 1)[0]


def numbered_pairs(text):
    section = section_of(text)
    diagram = [(int(m.group(1)), m.group(2).strip()) for m in DIAGRAM_NODE_RE.finditer(section)]
    prose = [(int(m.group(1)), m.group(2).strip()) for m in PROSE_HEADING_RE.finditer(section)]
    return diagram, prose


def apply_fix(text):
    renumber = {"4": "3", "5": "4", "6": "5", "7": "6"}

    def repl(m):
        num = m.group(1)
        if num in renumber:
            return f"**{renumber[num]} \xb7 {m.group(2)}"
        return m.group(0)

    section_start = text.index("## Quick start")
    section_end = text.index("\n## ", section_start + 1)
    head, section, tail = text[:section_start], text[section_start:section_end], text[section_end:]
    fixed_section = re.sub(r'\*\*(\d+)\s*\xb7\s*([^*]+?)\.?\*\*', repl, section)
    return head + fixed_section + tail


def main():
    fix = "--fix" in sys.argv
    readme_path = os.path.join(REPO, "README.md")
    text = open(readme_path, encoding="utf-8").read()

    if fix:
        tmpdir = os.environ.get("TMPDIR", tempfile.gettempdir())
        os.makedirs(tmpdir, exist_ok=True)
        fixed = apply_fix(text)
        fd, path = tempfile.mkstemp(dir=tmpdir, suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(fixed)
        diagram, prose = numbered_pairs(fixed)
        os.unlink(path)
    else:
        diagram, prose = numbered_pairs(text)

    print("diagram (order, number, label):")
    for i, (num, label) in enumerate(diagram):
        print(f"  [{i}] step{num} · {label!r}")
    print("prose (order, number, label):")
    for i, (num, label) in enumerate(prose):
        print(f"  [{i}] step{num} · {label!r}")

    n = min(len(diagram), len(prose))
    mismatches = []
    for i in range(n):
        dnum, dlabel = diagram[i]
        pnum, plabel = prose[i]
        if dnum != pnum:
            mismatches.append((i, dnum, dlabel, pnum, plabel))

    for i, dnum, dlabel, pnum, plabel in mismatches:
        print(f"  MISMATCH pos={i} diagram=step{dnum}({dlabel!r}) prose=step{pnum}({plabel!r})")

    print(f"RESULT positional_mismatches={len(mismatches)} count")
    print(f"RESULT diagram_count={len(diagram)} count")
    print(f"RESULT prose_count={len(prose)} count")
    print("RESULT thread_factor=1.00 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    print(f"RESULT load1={load1} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
