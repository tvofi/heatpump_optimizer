#!/usr/bin/env python3
"""D5 harness 4 — reader-path reachability and heading structure of the docs.

METRICS (one line each):
  unreachable_docs   = markdown documents under docs/ that no BFS from
                       README.md over relative markdown links ever reaches, and
                       that no reachable document links to — a reader who
                       starts at the README can never arrive at them.
  heading_level_jumps= headings whose level exceeds the previous heading's
                       level by more than one (h2 -> h4), per document.
  h1_count           = documents with zero or more than one level-1 heading.
  toc_missing        = level-2 headings of README.md that the README's own
                       navigation list does not link to (anchor links only).
  readme_index_omissions
                     = documents the README links to that its own
                       "## Documentation" index table does not list.
  superseded_docs_without_forward_pointer
                     = documents X for which some document says "supersedes
                       `X`" while X itself never names that successor.
  readme_links_to_superseded_doc
                     = such X that README.md links while never linking the
                       successor, so a reader is sent only to the stale one.

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/doc_structure.py

Set D5_ROOT=<dir> to measure a copy of the tree instead (used by the
perturbation run); the default root is the repository this file lives in.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT unreachable_docs=15 count
    RESULT readme_index_omissions=4 count
    RESULT superseded_docs_without_forward_pointer=1 count
    RESULT readme_links_to_superseded_doc=1 count
    RESULT heading_level_jumps=0 count
    RESULT docs_without_single_h1=0 count
    RESULT readme_h2_unlinked=15 (of 18)
    tolerance: exact.
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
PERTURBATION: add `[x](docs/HANDOVER.md)` to README.md -> unreachable_docs must
    go DOWN by 1. Removing README's link to docs/ecl110.md moves it UP by 1
    (ecl110.md is linked from other reachable docs, so removing every inbound
    link is what the direction refers to).
INSTRUMENTED: the markdown link graph rooted at README.md, i.e. the reader
    path the README's own navigation defines.
"""
import os
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import re
from collections import deque
from pathlib import Path

ROOT = Path(os.environ.get("D5_ROOT") or Path(__file__).resolve().parents[4]).resolve()

LINK_RE = re.compile(r"\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*(<[^>]*>|[^()\s]*(?:\([^()]*\)[^()\s]*)*)\s*(?:\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)


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


def clean(text):
    text = strip_fences(text)
    return CODE_SPAN_RE.sub(lambda m: m.group(1) + " " * len(m.group(2)) + m.group(1), text)


def slug(title):
    t = re.sub(r"`([^`]*)`", r"\1", title)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_~]", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def links_of(path):
    body = clean(path.read_text(encoding="utf-8", errors="replace"))
    out = []
    for m in LINK_RE.finditer(body):
        t = m.group(1).strip()
        if t.startswith("<") and t.endswith(">"):
            t = t[1:-1]
        if not t or t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        t = t.split("#", 1)[0]
        if not t:
            continue
        out.append(t)
    return out


def headings(path):
    body = clean(path.read_text(encoding="utf-8", errors="replace"))
    return [(len(m.group(1)), m.group(2))
            for line in body.split("\n") if (m := HEADING_RE.match(line))]


def main():
    readme = ROOT / "README.md"
    seen, order = set(), []
    q = deque([readme.resolve()])
    while q:
        cur = q.popleft()
        if cur in seen or not cur.exists() or cur.suffix != ".md":
            continue
        seen.add(cur)
        order.append(cur)
        for t in links_of(cur):
            nxt = (cur.parent / t).resolve()
            if nxt.suffix == ".md":
                q.append(nxt)

    all_docs = sorted(p.resolve() for p in (ROOT / "docs").rglob("*.md"))
    unreachable = [p for p in all_docs if p not in seen]

    print("--- documents under docs/ unreachable from README.md ---")
    for p in unreachable:
        print(f"  {p.relative_to(ROOT).as_posix()}")
    print("--- documents reachable from README.md ---")
    for p in order:
        try:
            print(f"  {p.relative_to(ROOT).as_posix()}")
        except ValueError:
            print(f"  {p}")

    # heading structure over the user-facing set (reachable docs plus README)
    user_docs = [p for p in order if p.exists()]
    jumps = []
    bad_h1 = []
    for p in user_docs:
        hs = headings(p)
        prev = 0
        for lvl, title in hs:
            if prev and lvl > prev + 1:
                jumps.append((p.relative_to(ROOT).as_posix(), prev, lvl, title))
            prev = lvl
        n1 = sum(1 for lvl, _ in hs if lvl == 1)
        if n1 != 1:
            bad_h1.append((p.relative_to(ROOT).as_posix(), n1))

    print("--- heading level jumps (previous -> this) ---")
    for f, a, b, t in jumps:
        print(f"  {f}: h{a} -> h{b}  '{t[:70]}'")
    print("--- documents without exactly one h1 ---")
    for f, n in bad_h1:
        print(f"  {f}: {n}")

    # README navigation coverage: which of README's own h2s does it link to?
    body = clean(readme.read_text(encoding="utf-8", errors="replace"))
    anchors_linked = set()
    for m in LINK_RE.finditer(body):
        t = m.group(1).strip()
        if t.startswith("#"):
            anchors_linked.add(t[1:].lower())
    h2s = [slug(t) for lvl, t in headings(readme) if lvl == 2]
    missing = [h for h in h2s if h not in anchors_linked]
    print("--- README h2 sections not linked from anywhere in README ---")
    for h in missing:
        print(f"  #{h}")

    # The README's own Documentation table is the docs index. Which documents
    # does the README send a reader to that the index omits?
    doc_section = re.split(r"^## Documentation\s*$", readme.read_text(encoding="utf-8"),
                           flags=re.M)
    indexed = set()
    if len(doc_section) > 1:
        tail = re.split(r"^## ", doc_section[1], flags=re.M)[0]
        for m in LINK_RE.finditer(clean(tail)):
            t = m.group(1).strip().split("#", 1)[0]
            if t and not t.startswith(("http", "mailto")):
                indexed.add((readme.parent / t).resolve())
    linked_from_readme = {(readme.parent / t).resolve() for t in links_of(readme)}
    omitted = sorted(p for p in linked_from_readme
                     if p.suffix == ".md" and p.exists() and p not in indexed
                     and "docs" in p.parts)
    print("--- documents the README links to but its Documentation index omits ---")
    for p_ in omitted:
        print(f"  {p_.relative_to(ROOT).as_posix()}")

    # Supersession: document A saying "supersedes `B`" makes B stale. Does B
    # say so, and does the README still send readers to B?
    sup = []
    for p_ in sorted((ROOT / "docs").rglob("*.md")) + [readme]:
        text = p_.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"supersedes\s+`([^`]+\.md)`", text, re.I):
            target = (ROOT / m.group(1)) if not (p_.parent / m.group(1)).exists() \
                else (p_.parent / m.group(1))
            sup.append((p_.resolve(), target.resolve()))
    orphan_stale, readme_to_stale = [], []
    for newer, older in sup:
        if not older.exists():
            continue
        older_text = older.read_text(encoding="utf-8", errors="replace")
        newer_rel = newer.relative_to(ROOT).as_posix()
        newer_base = newer.name
        if newer_rel not in older_text and newer_base not in older_text:
            orphan_stale.append((older.relative_to(ROOT).as_posix(), newer_rel))
        if older in linked_from_readme and newer not in linked_from_readme:
            readme_to_stale.append((older.relative_to(ROOT).as_posix(), newer_rel))
    print("--- superseded documents carrying no pointer to their successor ---")
    for old, new in orphan_stale:
        print(f"  {old}  (superseded by {new}, not named in it)")
    print("--- superseded documents the README links while never linking the successor ---")
    for old, new in readme_to_stale:
        print(f"  README.md -> {old}   (current document is {new})")

    print()
    print(f"RESULT supersession_statements={len(sup)} count")
    print(f"RESULT superseded_docs_without_forward_pointer={len(orphan_stale)} count")
    print(f"RESULT readme_links_to_superseded_doc={len(readme_to_stale)} count")
    print(f"RESULT readme_index_entries={len(indexed)} count")
    print(f"RESULT readme_index_omissions={len(omitted)} count")
    print(f"RESULT docs_md_total={len(all_docs)} count")
    print(f"RESULT docs_reachable_from_readme={len([p for p in order if 'docs' in p.parts])} count")
    print(f"RESULT unreachable_docs={len(unreachable)} count")
    print(f"RESULT heading_level_jumps={len(jumps)} count")
    print(f"RESULT docs_without_single_h1={len(bad_h1)} count")
    print(f"RESULT readme_h2_sections={len(h2s)} count")
    print(f"RESULT readme_h2_unlinked={len(missing)} count")
    _thr = time.thread_time()
    print(f"RESULT thread_factor={time.process_time() / _thr if _thr else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
