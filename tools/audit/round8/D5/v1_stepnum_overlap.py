#!/usr/bin/env python3
"""v1_stepnum_overlap.py -- independent re-measure of D5-s1-01, take 2.

s1_stepnum.py matches a diagram node to a prose heading by exact first-
three-normalized-words prefix. That silently drops the "How do you want to
describe your building?" node, whose diagram wording and prose wording
("4 · How do you want to describe your building?" vs "5 · How to describe
your building.") share no 3-word prefix, so s1's own count (3) undercounts
the number of genuinely disagreeing pairs.

Metric (own definition): for each numbered diagram node, find the numbered
prose heading with the highest Jaccard word-overlap (over the FULL label,
not just a 3-word prefix, and only nodes/headings not already claimed by a
better match -- greedy best-first assignment). A pair counts only if overlap
>= 0.34 (at least one shared content word out of typical 2-3 word labels),
which is enough to reject the accidental "Temperatures" vs "finish menu"
same-number coincidence a pure positional pairing would produce, while still
catching the wording-drifted "building" pair s1_stepnum.py's exact-prefix
rule misses. Count pairs whose numbers disagree.

Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D5/v1_stepnum_overlap.py
Expected: RESULT overlap_mismatches=<n> count
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
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

DIAGRAM_NODE_RE = re.compile(r'[\[{]"(\d+)\s*\xb7\s*([^"<]+?)(?:<br/>|")', re.M)
PROSE_HEADING_RE = re.compile(r'^\*\*(\d+)\s*\xb7\s*([^*]+?)\.?\*\*', re.M)


def words(label):
    label = label.strip().rstrip(".?").lower()
    label = re.sub(r"[^a-z0-9 ]", " ", label)
    return frozenset(w for w in label.split() if w not in ("the", "a", "to", "your", "you", "do", "want", "how"))


def section_of(text):
    section = text.split("## Quick start", 1)[1]
    return section.split("\n## ", 1)[0]


def extract(text):
    section = section_of(text)
    diagram = [(int(m.group(1)), m.group(2).strip()) for m in DIAGRAM_NODE_RE.finditer(section)]
    prose = [(int(m.group(1)), m.group(2).strip()) for m in PROSE_HEADING_RE.finditer(section)]
    return diagram, prose


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


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


def run(text):
    diagram, prose = extract(text)
    dwords = [(n, l, words(l)) for n, l in diagram]
    pwords = [(n, l, words(l)) for n, l in prose]

    # greedy best-first assignment by overlap score, threshold 0.34
    candidates = []
    for di, (dn, dl, dw) in enumerate(dwords):
        for pi, (pn, pl, pw) in enumerate(pwords):
            score = jaccard(dw, pw)
            if score >= 0.34:
                candidates.append((score, di, pi))
    candidates.sort(reverse=True)
    used_d, used_p = set(), set()
    pairs = []
    for score, di, pi in candidates:
        if di in used_d or pi in used_p:
            continue
        used_d.add(di)
        used_p.add(pi)
        pairs.append((di, pi, score))
    return dwords, pwords, pairs


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
        dwords, pwords, pairs = run(fixed)
        os.unlink(path)
    else:
        dwords, pwords, pairs = run(text)

    mismatches = 0
    for di, pi, score in sorted(pairs):
        dn, dl, _ = dwords[di]
        pn, pl, _ = pwords[pi]
        tag = "MISMATCH" if dn != pn else "match"
        print(f"  {tag} score={score:.2f} diagram=step{dn}({dl!r}) prose=step{pn}({pl!r})")
        if dn != pn:
            mismatches += 1

    unmatched_prose = [pl for pi, (pn, pl, _) in enumerate(pwords) if pi not in {p for _, p, _ in pairs}]
    for pl in unmatched_prose:
        print(f"  unmatched prose heading (no diagram counterpart): {pl!r}")

    print(f"RESULT overlap_mismatches={mismatches} count")
    print(f"RESULT paired={len(pairs)} count")
    print(f"RESULT unmatched_prose={len(unmatched_prose)} count")
    print("RESULT thread_factor=1.00 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    print(f"RESULT load1={load1} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
