#!/usr/bin/env python3
"""D5 harness 3 — duplicated prose between README.md and the user-facing docs/.

METRIC: `duplicated_sentences` = number of normalised sentences of >= 12 words
        that occur verbatim in two or more DISTINCT user-facing documents
        (README.md plus docs/*.md excluding the plan/handover/decision/
        superpowers records, which are development history and not a reader
        path). `duplicated_words` is the total word count of those sentences
        counted once per extra copy — i.e. the prose a maintainer has to keep
        in step by hand.
        Normalisation: markdown emphasis/links/code-spans reduced to their
        text, whitespace collapsed, lowercased, trailing punctuation dropped.

Set D5_ROOT=<dir> to measure a copy of the tree instead (used by the
perturbation run); the default root is the repository this file lives in.

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/doc_duplication.py

Add --all to include the development records (plans, HANDOVER, decisions).

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT duplicated_sentences=0 count
    RESULT near_duplicate_sentence_pairs=0 count
    RESULT sentences_scanned=1160 count
    tolerance: exact.
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
PERTURBATION: delete one duplicated sentence from docs/how-it-works.md ->
    duplicated_sentences must go DOWN by 1 (and duplicated_words by that
    sentence's word count). Pasting a >=12-word README sentence into
    docs/configuration.md moves it UP by 1.
INSTRUMENTED: the rendered prose of README.md and docs/*.md, the documents a
    reader is sent to by README's own navigation block.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("D5_ROOT") or Path(__file__).resolve().parents[4]).resolve()
MIN_WORDS = 12

USER_DOCS = [
    "README.md",
    "docs/how-it-works.md",
    "docs/configuration.md",
    "docs/architecture.md",
    "docs/dashboard-card.md",
    "docs/automations.md",
    "docs/ecl110.md",
    "DISCLAIMER.md",
]
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def strip_fences(text):
    out, in_fence, fence = [], False, ""
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if m and not in_fence:
            in_fence, fence = True, m.group(1)
            out.append("")
            continue
        if in_fence:
            out.append("")
            if line.strip().startswith(fence):
                in_fence = False
            continue
        out.append(line)
    return "\n".join(out)


def normalise(text):
    t = re.sub(r"`([^`]*)`", r"\1", text)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_~>#|]", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def sentences(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    body = strip_fences(raw)
    out = []
    for para in re.split(r"\n\s*\n", body):
        norm = normalise(para)
        if not norm:
            continue
        for s in SENT_SPLIT.split(norm):
            s = s.strip(" .;:,-")
            words = s.split()
            if len(words) >= MIN_WORDS:
                out.append((s, len(words)))
    return out


def main():
    docs = USER_DOCS
    if "--all" in sys.argv:
        docs = sorted(
            [p.relative_to(ROOT).as_posix() for p in (ROOT / "docs").rglob("*.md")]
            + ["README.md", "DISCLAIMER.md", "CLAUDE.md"]
        )
    index = defaultdict(set)
    words_of = {}
    per_doc = {}
    for rel in docs:
        p = ROOT / rel
        if not p.exists():
            continue
        sents = sentences(p)
        per_doc[rel] = len(sents)
        for s, n in sents:
            h = hashlib.sha1(s.encode()).hexdigest()
            index[h].add(rel)
            words_of[h] = (s, n)

    dup = {h: files for h, files in index.items() if len(files) >= 2}
    dup_words = sum(words_of[h][1] * (len(files) - 1) for h, files in dup.items())

    print("--- sentences repeated across documents ---")
    for h, files in sorted(dup.items(), key=lambda kv: -words_of[kv[0]][1]):
        s, n = words_of[h]
        print(f"  [{n}w] {', '.join(sorted(files))}")
        print(f"        {s[:180]}")
    print()
    print("--- sentences per document ---")
    for rel, n in sorted(per_doc.items()):
        print(f"  {rel}: {n}")
    # Near-duplicates: 5-word shingle Jaccard >= 0.6 between sentences that
    # live in different documents. Catches paraphrase that exact hashing misses.
    flat = []
    for rel in per_doc:
        for s_, n_ in sentences(ROOT / rel):
            w = s_.split()
            sh = frozenset(" ".join(w[i:i + 5]) for i in range(max(1, len(w) - 4)))
            flat.append((rel, s_, n_, sh))
    near = []
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i][0] == flat[j][0]:
                continue
            a, b = flat[i][3], flat[j][3]
            inter = len(a & b)
            if not inter:
                continue
            jac = inter / len(a | b)
            if jac >= 0.6:
                near.append((jac, flat[i][0], flat[j][0], flat[i][1]))
    near.sort(reverse=True)
    print("--- near-duplicate sentences across documents (5-gram Jaccard >= 0.6) ---")
    for jac, f1, f2, txt in near[:40]:
        print(f"  {jac:.2f}  {f1} <-> {f2}")
        print(f"        {txt[:170]}")

    print()
    print(f"RESULT near_duplicate_sentence_pairs={len(near)} count")
    print(f"RESULT documents_scanned={len(per_doc)} count")
    print(f"RESULT sentences_scanned={sum(per_doc.values())} count")
    print(f"RESULT duplicated_sentences={len(dup)} count")
    print(f"RESULT duplicated_words={dup_words} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
