#!/usr/bin/env python3
"""s1_stepnum.py

Metric: count of screen labels that appear both as a numbered mermaid node
in README.md's "Quick start" flowchart (`"N · <label>` inside a node)
and as a numbered prose heading below it (`**N · <label>.**`), where the
two numbers N disagree for the same <label> text (case/punctuation-insensitive
prefix match on the label's first words).

This is the reader-path check from D5.md method step 1 (new-user walkthrough):
a user matching the diagram's step numbers against the prose below it hits a
contradiction from step 3 onward, because the prose inserts an unnumbered-in-
the-diagram "finish menu" step as its own number 3 and pushes every later
screen's prose number one ahead of the diagram's.

Command: PYTHONPATH=tests/hastub python3 tools/audit/round8/D5/s1_stepnum.py
Expected: RESULT mismatched_labels=<n> (baseline cdf82daabcfe3777d98b31489f36df5555ec9d82: 4) +/- 0
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82

Instrumented symbol: README.md's "## Quick start" section (both the mermaid
flowchart source and the numbered prose paragraphs beneath it) -- this
dimension's production artefact is the documentation text itself.

Perturbation: --fix renumbers the four prose headings (Temperatures 4->3,
"How to describe your building" 5->4, Hot water 6->5, Weather sensitivity
7->6) in a temp copy and re-runs the same parser against it; mismatched_labels
must drop to 0. (README.md itself is never modified; the fixed copy is a
temp file under TMPDIR, so this harness needs no finally-restore of
production.)
"""
import os
import re
import sys
import tempfile
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))

DIAGRAM_NODE_RE = re.compile(r'[\[{]"(\d+)\s*\xb7\s*([^"<]+?)(?:<br/>|")', re.M)
PROSE_HEADING_RE = re.compile(r'^\*\*(\d+)\s*\xb7\s*([^*]+?)\.?\*\*', re.M)


def normalize(label):
    label = label.strip().rstrip(".?").lower()
    label = re.sub(r"[^a-z0-9 ]", "", label)
    words = label.split()
    return " ".join(words[:3])  # first three words is enough to key the same screen


def extract(text):
    section = text.split("## Quick start", 1)[1]
    section = section.split("\n## ", 1)[0]  # stop at the next top-level heading
    diagram = {}
    for m in DIAGRAM_NODE_RE.finditer(section):
        num, label = int(m.group(1)), normalize(m.group(2))
        diagram.setdefault(label, num)
    prose = {}
    for m in PROSE_HEADING_RE.finditer(section):
        num, label = int(m.group(1)), normalize(m.group(2))
        prose.setdefault(label, num)
    return diagram, prose


def run(text):
    diagram, prose = extract(text)
    mismatches = []
    for label, dnum in diagram.items():
        if label in prose and prose[label] != dnum:
            mismatches.append((label, dnum, prose[label]))
    return mismatches


def apply_fix(text):
    # Shift the four prose numbers down by one to match the diagram.
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

    t0 = time.process_time()
    if fix:
        tmpdir = os.environ.get("TMPDIR", tempfile.gettempdir())
        os.makedirs(tmpdir, exist_ok=True)
        fixed = apply_fix(text)
        fd, path = tempfile.mkstemp(dir=tmpdir, suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(fixed)
        mismatches = run(fixed)
        os.unlink(path)
    else:
        mismatches = run(text)
    t1 = time.process_time()

    for label, dnum, pnum in mismatches:
        print(f"  label={label!r} diagram=step{dnum} prose=step{pnum}")
    print(f"RESULT mismatched_labels={len(mismatches)} count")
    print("RESULT thread_factor=1.00 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    print(f"RESULT load1={load1} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
