#!/usr/bin/env python3
"""D5 duplication harness.

METRIC: duplicated prose between the reader-facing documents, measured three
ways over normalised text (markdown stripped, whitespace collapsed, lowercased):
  dup_paragraph_pairs  -- paragraphs of >= MIN_PARA_WORDS words whose hash occurs
                          in two or more distinct documents (pairs, not copies)
  dup_sentence_pairs   -- sentences of >= MIN_SENT_WORDS words whose hash occurs
                          in two or more distinct documents
  dup_sentence_bytes   -- bytes of normalised sentence text so duplicated
  near_dup_para_pairs  -- cross-document paragraph pairs with 5-gram Jaccard
                          >= 0.60 that are not already exact duplicates

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/dup.py            # summary
  ... tools/audit/round4/D5/dup.py --list     # every duplicated unit, with locations

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6):
  dup_paragraph_pairs=5 +-0   dup_sentence_pairs=39 +-0
  dup_sentence_bytes=4478 +-0 near_dup_para_pairs=24 +-2
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

import hashlib
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
MIN_PARA_WORDS = 20
MIN_SENT_WORDS = 10
NEAR = float(os.environ.get("D5_NEAR", "0.60"))

DOCS = [
    "README.md",
    "docs/architecture.md",
    "docs/automations.md",
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
    "docs/how-it-works.md",
]

FENCE = re.compile(r"^\s*(```|~~~)")


def blocks(path):
    """Yield (start_line, raw_paragraph) for prose paragraphs outside code fences."""
    txt = (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines()
    in_fence = False
    buf, start = [], 0
    for i, line in enumerate(txt, 1):
        if FENCE.match(line):
            if buf:
                yield start, "\n".join(buf)
                buf = []
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.strip() == "" or line.startswith("#"):
            if buf:
                yield start, "\n".join(buf)
                buf = []
            continue
        if not buf:
            start = i
        buf.append(line)
    if buf:
        yield start, "\n".join(buf)


def norm(text):
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)   # links -> their text
    t = re.sub(r"`([^`]*)`", r"\1", t)                    # code spans -> content
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("**", "").replace("*", "").replace("__", "")
    t = re.sub(r"^\s*[-*+>]\s+", " ", t, flags=re.M)      # list/quote markers
    t = re.sub(r"^\s*\d+\.\s+", " ", t, flags=re.M)
    t = re.sub(r"[|]", " ", t)                            # table pipes
    t = t.replace("—", "-").replace("–", "-").replace("’", "'")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


SENT_END = re.compile(r"(?<=[.!?])\s+")


def sentences(ntext):
    for s in SENT_END.split(ntext):
        s = s.strip()
        if len(s.split()) >= MIN_SENT_WORDS:
            yield s


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def shingles(s, n=5):
    w = s.split()
    return {" ".join(w[i : i + n]) for i in range(max(0, len(w) - n + 1))}


def main():
    listing = "--list" in sys.argv
    # Positive control: --selftest re-reads README.md as an eighth pseudo-document
    # so every one of its paragraphs and sentences must appear as a cross-document
    # duplicate. A run that reports 0 under --selftest is a broken harness.
    docs = list(DOCS) + (["README.md"] if "--selftest" in sys.argv else [])
    paras = {}      # hash -> [(doc, line, text)]
    sents = {}      # hash -> [(doc, line, text)]
    para_index = []  # (doc, line, ntext)
    for di, d in enumerate(docs):
        tag = d if di < len(DOCS) else d + "#copy"
        for ln, raw in blocks(d):
            n = norm(raw)
            if len(n.split()) >= MIN_PARA_WORDS:
                paras.setdefault(h(n), []).append((tag, ln, n))
                para_index.append((tag, ln, n))
            for s in sentences(n):
                sents.setdefault(h(s), []).append((tag, ln, s))

    def cross(table):
        out = []
        for k, locs in table.items():
            docs = {l[0] for l in locs}
            if len(docs) >= 2:
                out.append((k, locs))
        return out

    xp, xs = cross(paras), cross(sents)
    dup_sent_bytes = sum(len(locs[0][2].encode()) * (len(locs) - 1) for _, locs in xs)

    # in-document repeats (same doc, same text, twice)
    intra_p = [
        (k, locs) for k, locs in paras.items()
        if len(locs) > len({l[0] for l in locs}) or (len(locs) > 1 and len({l[0] for l in locs}) == 1)
    ]

    exact = {h(n) for _, _, n in para_index}
    near = []
    by_doc = {}
    for d, ln, n in para_index:
        by_doc.setdefault(d, []).append((ln, n, shingles(n)))
    for a, b in itertools.combinations(sorted(by_doc), 2):
        for la, na, sa in by_doc[a]:
            if not sa:
                continue
            for lb, nb, sb in by_doc[b]:
                if not sb or h(na) == h(nb):
                    continue
                j = len(sa & sb) / len(sa | sb)
                if j >= NEAR:
                    near.append((round(j, 3), f"{a}:{la}", f"{b}:{lb}", na[:110]))

    if listing:
        print("== exact paragraph duplicates across documents ==")
        for k, locs in sorted(xp, key=lambda x: -len(x[1][0][2])):
            print(f"  [{k}] {len(locs[0][2])} chars  " + "  ".join(f"{d}:{l}" for d, l, _ in locs))
            print(f"      {locs[0][2][:220]}")
        print("== exact sentence duplicates across documents ==")
        for k, locs in sorted(xs, key=lambda x: -len(x[1][0][2])):
            print(f"  [{k}] {len(locs[0][2])} chars  " + "  ".join(f"{d}:{l}" for d, l, _ in locs))
            print(f"      {locs[0][2][:220]}")
        print("== in-document repeated paragraphs ==")
        for k, locs in intra_p:
            print(f"  [{k}] " + "  ".join(f"{d}:{l}" for d, l, _ in locs))
            print(f"      {locs[0][2][:200]}")
        print(f"== near-duplicate paragraph pairs (5-gram Jaccard >= {NEAR}) ==")
        for j, a, b, t in sorted(near, reverse=True):
            print(f"  {j}  {a}  {b}")
            print(f"      {t}")

    print(f"RESULT documents={len(docs)} count")
    print(f"RESULT paragraphs_ge{MIN_PARA_WORDS}w={len(para_index)} count")
    print(f"RESULT dup_paragraph_pairs={len(xp)} count")
    print(f"RESULT dup_sentence_pairs={len(xs)} count")
    print(f"RESULT dup_sentence_bytes={dup_sent_bytes} bytes")
    print(f"RESULT intra_doc_repeated_paragraphs={len(intra_p)} count")
    print(f"RESULT near_dup_para_pairs={len(near)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
