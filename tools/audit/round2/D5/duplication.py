#!/usr/bin/env python
# D5 harness: duplication between README.md and docs/*.md, by paragraph hashing.
#
# Metric: every document is split into units (prose paragraphs, list runs,
# tables, fenced code blocks); a unit is normalised (lower-case, markdown
# emphasis stripped, whitespace collapsed).  Counted:
#   exact_duplicate_units_cross_file  -- units of >= 8 words whose normalised
#                                        text appears in more than one document
#   near_duplicate_pairs              -- pairs of units of >= 25 words from
#                                        different documents whose word
#                                        5-shingle Jaccard is >= 0.5
#   duplicated_words                  -- words a reader of the whole set reads
#                                        twice (sum over the second and later
#                                        copies of exact and near duplicates)
#
# Command:
#   PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D5/duplication.py
#
# Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884), all exact:
#   RESULT units_total=538  words_total=37454
#   RESULT exact_duplicate_units_cross_file=0
#   RESULT near_duplicate_pairs=1   (README.md:420 sequenceDiagram <-> docs/how-it-works.md:54)
#   RESULT duplicated_words=237
#   RESULT readme_words_with_a_twin=237  readme_twin_share=0.043
#
# Machine: Apple M1 (8 cores, 8 GB), macOS 26.6, Python 3.13.1.
# Instrumented symbol: the documents (README.md, DISCLAIMER.md, docs/*.md
# except the three plan-*.md program plans, tests/README.md).
# Perturbation: delete the sequenceDiagram block under "## How it works" in
# README.md -> near_duplicate_pairs goes DOWN by one and duplicated_words
# drops by that block's word count.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import hashlib
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = [ROOT / "README.md", ROOT / "DISCLAIMER.md", ROOT / "tests" / "README.md"] + sorted(
    p for p in (ROOT / "docs").glob("*.md") if not p.name.startswith("plan-")
)
MIN_EXACT_WORDS = 8
MIN_NEAR_WORDS = 25
SHINGLE = 5
JACCARD = 0.5


def units(path: Path):
    """Yield (kind, start_line, text) units from a markdown file."""
    lines = path.read_text(encoding="utf-8").split("\n")
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            start = i
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                i += 1
            i += 1
            yield ("code", start + 1, "\n".join(lines[start + 1 : i - 1]))
            continue
        if line.startswith("|"):
            start = i
            while i < n and lines[i].startswith("|"):
                i += 1
            yield ("table", start + 1, "\n".join(lines[start:i]))
            continue
        if re.match(r"^#{1,6}\s", line):
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        start = i
        while i < n and lines[i].strip() and not lines[i].startswith("|") and not lines[i].strip().startswith("```") and not re.match(r"^#{1,6}\s", lines[i]):
            i += 1
        yield ("prose", start + 1, "\n".join(lines[start:i]))


def normalise(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[*_`]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def words(text: str):
    return re.findall(r"[a-z0-9]+(?:[.'-][a-z0-9]+)*", text)


def shingles(ws, k=SHINGLE):
    return {" ".join(ws[i : i + k]) for i in range(len(ws) - k + 1)}


def footer(t_proc0, t_thr0):
    proc = time.process_time() - t_proc0
    thr = time.thread_time() - t_thr0
    tf = proc / thr if thr > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    swapins = -1
    try:
        vm = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5).stdout
        m = re.search(r"Swapins:\s+(\d+)", vm)
        if m:
            swapins = int(m.group(1))
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={swapins}")


def main():
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    all_units = []
    for doc in DOCS:
        rel = str(doc.relative_to(ROOT))
        for kind, line, text in units(doc):
            norm = normalise(text)
            ws = words(norm)
            all_units.append({
                "doc": rel, "kind": kind, "line": line, "norm": norm, "words": ws,
                "hash": hashlib.sha1(norm.encode()).hexdigest(),
            })
    total_words = sum(len(u["words"]) for u in all_units)
    print(f"documents: {len(DOCS)}  units: {len(all_units)}  words: {total_words}")

    # exact duplicates across files
    by_hash = {}
    for u in all_units:
        if len(u["words"]) >= MIN_EXACT_WORDS:
            by_hash.setdefault(u["hash"], []).append(u)
    exact_cross = 0
    dup_words = 0
    exact_pairs = set()
    for h, us in by_hash.items():
        docs = {u["doc"] for u in us}
        if len(docs) > 1:
            exact_cross += 1
            dup_words += len(us[0]["words"]) * (len(us) - 1)
            locs = ", ".join(f"{u['doc']}:{u['line']}" for u in us)
            print(f"EXACT   {len(us[0]['words']):4d} words  {us[0]['kind']:5s}  {locs}")
            for a in us:
                for b in us:
                    if a is not b:
                        exact_pairs.add((id(a), id(b)))

    # near duplicates across files
    big = [u for u in all_units if len(u["words"]) >= MIN_NEAR_WORDS]
    for u in big:
        u["sh"] = shingles(u["words"])
    near = []
    for i, a in enumerate(big):
        for b in big[i + 1 :]:
            if a["doc"] == b["doc"] or (id(a), id(b)) in exact_pairs:
                continue
            if not a["sh"] or not b["sh"]:
                continue
            inter = len(a["sh"] & b["sh"])
            if inter == 0:
                continue
            jac = inter / len(a["sh"] | b["sh"])
            cont = inter / min(len(a["sh"]), len(b["sh"]))
            if jac >= JACCARD:
                near.append((jac, cont, a, b))
    near.sort(key=lambda r: -r[0])
    for jac, cont, a, b in near:
        dup_words += min(len(a["words"]), len(b["words"]))
        print(
            f"NEAR    J={jac:.2f} C={cont:.2f}  {a['kind']:5s} {len(a['words']):4d}w {a['doc']}:{a['line']}"
            f"  <->  {b['kind']:5s} {len(b['words']):4d}w {b['doc']}:{b['line']}"
        )
    # README share: words of README units that have an exact or near twin elsewhere
    readme_twinned = set()
    for jac, cont, a, b in near:
        for u in (a, b):
            if u["doc"] == "README.md":
                readme_twinned.add(id(u))
    for h, us in by_hash.items():
        if len({u["doc"] for u in us}) > 1:
            for u in us:
                if u["doc"] == "README.md":
                    readme_twinned.add(id(u))
    readme_words = sum(len(u["words"]) for u in all_units if u["doc"] == "README.md")
    readme_dup = sum(len(u["words"]) for u in all_units if id(u) in readme_twinned)
    print(f"RESULT units_total={len(all_units)} count")
    print(f"RESULT words_total={total_words} count")
    print(f"RESULT exact_duplicate_units_cross_file={exact_cross} count")
    print(f"RESULT near_duplicate_pairs={len(near)} count")
    print(f"RESULT duplicated_words={dup_words} count")
    print(f"RESULT readme_words_with_a_twin={readme_dup} count")
    print(f"RESULT readme_twin_share={(readme_dup / readme_words if readme_words else 0):.3f} ratio")
    footer(t_proc0, t_thr0)


if __name__ == "__main__":
    main()
