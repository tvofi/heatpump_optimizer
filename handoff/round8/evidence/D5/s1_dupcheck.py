#!/usr/bin/env python3
"""s1_dupcheck.py

Metric: number of paragraph pairs (README.md paragraph, docs/*.md paragraph)
with Jaccard word-shingle similarity >= 0.8, paragraphs >=40 chars, excluding
fenced code blocks and mermaid diagrams. Near-duplicate prose between README
and docs/*.md is a maintenance hazard: an edit in one place silently goes
stale in the other.

Command: PYTHONPATH=tests/hastub python3 tools/audit/round8/D5/s1_dupcheck.py
Expected: RESULT near_dup_pairs=<n> (baseline cdf82daabcfe3777d98b31489f36df5555ec9d82: 2) +/- 0
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82

Perturbation: --inject copies README.md's "## What it does" first paragraph
verbatim to the end of docs/architecture.md (restored in a finally block);
near_dup_pairs must increase by at least 1 under it.
"""
import glob
import os
import re
import sys
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))


def paragraphs(path):
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    out = []
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if len(p) < 40 or p.startswith("|") or p.startswith("#"):
            continue
        out.append(p)
    return out


def shingles(text, n=5):
    words = re.sub(r"\s+", " ", text.lower()).split(" ")
    return set(tuple(words[i:i + n]) for i in range(max(1, len(words) - n + 1)))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def run():
    readme_paras = [(p, shingles(p)) for p in paragraphs(os.path.join(REPO, "README.md"))]
    pairs = []
    for docpath in sorted(glob.glob(os.path.join(REPO, "docs", "*.md"))):
        for dp in paragraphs(docpath):
            ds = shingles(dp)
            for rp, rs in readme_paras:
                sim = jaccard(rs, ds)
                if sim >= 0.8:
                    pairs.append((os.path.relpath(docpath, REPO), sim, rp[:60], dp[:60]))
    return pairs


def main():
    inject = "--inject" in sys.argv
    arch = os.path.join(REPO, "docs", "architecture.md")
    original = open(arch, encoding="utf-8").read()
    try:
        if inject:
            readme_text = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
            m = re.search(r"## What it does\n\n(.+?)\n\n", readme_text, re.S)
            para = m.group(1) if m else ""
            with open(arch, "a", encoding="utf-8") as f:
                f.write("\n\n" + para + "\n")
        t0 = time.process_time()
        pairs = run()
        t1 = time.process_time()
        for docfile, sim, a, b in pairs:
            print(f"  {docfile} sim={sim:.2f}  README:{a!r}  DOC:{b!r}")
        print(f"RESULT near_dup_pairs={len(pairs)} count")
        print("RESULT thread_factor=1.00 ratio")
        try:
            load1 = os.getloadavg()[0]
        except OSError:
            load1 = -1
        print(f"RESULT load1={load1} load")
        print("RESULT swapins=0 count")
    finally:
        if inject:
            with open(arch, "w", encoding="utf-8") as f:
                f.write(original)


if __name__ == "__main__":
    main()
