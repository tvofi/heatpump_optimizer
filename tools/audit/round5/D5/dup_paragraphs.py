#!/usr/bin/env python3
"""D5 harness: duplicated body paragraphs across the documentation set.

Metric definition (one line): count of paragraph pairs (>=200 characters each,
after stripping markdown decoration and collapsing whitespace) that appear more
than once in the reader-facing doc set, where the pair is not both inside
RELEASE_NOTES.md or the historical plan/delivery/decisions records.

Run from the repository root:
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D5/dup_paragraphs.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box)

Files considered: README.md, DISCLAIMER.md, docs/*.md (top level only),
tests/README.md. Historical records (RELEASE_NOTES.md, docs/plan-*.md,
docs/delivery/*, docs/decisions/*, docs/superpowers/*, CLAUDE.md, AGENTS.md) are
listed separately, not counted.

Perturbation the count must move under: copy any >=200-char body paragraph from
README.md into docs/how-it-works.md (one-line/one-block edit); the counted
number goes up by one.
"""
import os, re, sys, glob, hashlib
from collections import defaultdict

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.getcwd()
READER = ["README.md", "DISCLAIMER.md", "tests/README.md",
          "docs/how-it-works.md", "docs/configuration.md",
          "docs/dashboard-card.md", "docs/architecture.md",
          "docs/ecl110.md", "docs/automations.md"]
HISTORICAL_GLOBS = ["RELEASE_NOTES.md", "CLAUDE.md", "AGENTS.md",
                    "docs/plan-*.md", "docs/delivery/*.md",
                    "docs/decisions/*.md", "docs/superpowers/**/*.md",
                    "docs/HANDOVER.md"]
MINLEN = 200
FENCE = re.compile(r"^\s*(```|~~~)")
WS = re.compile(r"\s+")


def norm(p):
    p = p.strip()
    p = re.sub(r"[`*_>#\-|]", " ", p)
    return WS.sub(" ", p).strip()


def paragraphs(path):
    try:
        lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    except OSError:
        return []
    out, buf, infence = [], [], False
    for line in lines:
        if FENCE.match(line):
            infence = not infence
            buf.append("")
            continue
        if infence:
            continue
        if line.strip() == "":
            if buf:
                out.append("\n".join(buf))
                buf = []
        else:
            buf.append(line)
    if buf:
        out.append("\n".join(buf))
    return out


def hist_files():
    out = []
    for g in HISTORICAL_GLOBS:
        out += glob.glob(g, recursive=True)
    return out


def main():
    reader = [f for f in READER if os.path.exists(f)]
    seen = defaultdict(list)
    for f in reader + [g for g in hist_files() if g not in reader]:
        for p in paragraphs(f):
            n = norm(p)
            if len(n) >= MINLEN:
                seen[hashlib.sha1(n.encode()).hexdigest()].append((f, n))

    # reader-vs-reader and reader-vs-historical duplicated paragraphs
    dup_reader = 0
    dup_cross = 0
    for h, occ in seen.items():
        if len(occ) < 2:
            continue
        files = sorted(set(f for f, _ in occ))
        r = [f for f in files if f in reader]
        if len(r) >= 2:
            dup_reader += 1
            print("  DUP-READER %s" % " <=> ".join(r))
            print("     %s..." % occ[0][1][:110])
        elif len(r) == 1 and len(files) >= 2:
            dup_cross += 1
    print("RESULT reader_files=%d files" % len(reader))
    print("RESULT duplicated_paragraphs_reader=%d paragraphs" % dup_reader)
    print("RESULT duplicated_paragraphs_reader_vs_record=%d paragraphs"
          % dup_cross)
    print("RESULT thread_factor=1.0")
    try:
        print("RESULT load1=%s" % os.getloadavg()[0])
    except OSError:
        print("RESULT load1=-1")


if __name__ == "__main__":
    main()
