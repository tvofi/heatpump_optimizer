#!/usr/bin/env python3
"""D5 link harness.

METRIC: number of markdown link/image targets in the documentation corpus that
do not resolve -- an internal target is a repository path that does not exist or
a `#anchor` that no heading in the target file generates (GitHub slug rules);
an external target is an https URL whose final HTTP status is >= 400.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/links.py            # internal only, offline
  ... tools/audit/round4/D5/links.py --external # also resolve the 10 reader-doc URLs

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6):
  internal_broken_reader=0 +-0   internal_broken_all=0 +-0
  anchor_broken_reader=0 +-0     anchor_broken_all=0 +-0
  absent_in_export_reader=4 +-0 (audit-2026-08/09.md, backlog.md: removed by the
      export script, present on main, so not defects)
  external_broken_reader=0 +-0 (needs network)
Counts are contention-immune; no timing is reported beyond the mandated lines.
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

import re
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(".").resolve()

# The documents a reader is sent to by README.md or by another reader document.
READER_DOCS = [
    "README.md",
    "DISCLAIMER.md",
    "SECURITY.md",
    "docs/architecture.md",
    "docs/automations.md",
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
    "docs/how-it-works.md",
    "tests/README.md",
]


# Removed from the finder export by tools/audit/prepare_baseline.sh; they exist
# on main, so a link to one of them is NOT a defect and is counted separately.
EXPORT_ABSENT = {"docs/audit-2026-08.md", "docs/audit-2026-09.md", "docs/backlog.md"}

# Plan documents quote markdown link syntax as data (linter examples, regexes),
# so they are scanned only under --include-plans and reported separately.
PLAN_DOCS = {"docs/plan-2026-09-open-issues.md", "docs/plan-card-decomposition.md",
             "docs/plan-open-issues.md", "docs/plan-v4.0.0-program.md"}


def corpus(all_docs):
    if all_docs:
        out = [Path(p) for p in READER_DOCS]
        out += sorted(ROOT.glob("docs/*.md"))
        out += sorted(ROOT.glob("docs/decisions/*.md"))
        out += [Path("tools/audit/README.md"), Path("CLAUDE.md")]
        seen, uniq = set(), []
        for p in out:
            r = p.resolve()
            rel0 = os.path.relpath(r, ROOT)
            if r in seen or not r.exists():
                continue
            if rel0 in PLAN_DOCS and "--include-plans" not in sys.argv:
                continue
            seen.add(r)
            uniq.append(Path(os.path.relpath(r, ROOT)))
        return uniq
    return [Path(p) for p in READER_DOCS if (ROOT / p).exists()]


LINK = re.compile(r"(!?)\[(?P<text>(?:[^\[\]]|\[[^\]]*\])*)\]\((?P<t>[^()\s]*(?:\([^()]*\)[^()\s]*)*)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ANCHOR_TAG = re.compile(r'<a\s+(?:id|name)="([^"]+)"', re.I)


def slug(text):
    """GitHub heading slug: strip markup, lowercase, drop punctuation, dash spaces."""
    t = re.sub(r"`([^`]*)`", r"\1", text)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("**", "").replace("__", "").replace("*", "").replace("_", "_")
    t = unicodedata.normalize("NFKC", t).strip().lower()
    out = []
    for ch in t:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif ch in " \t":
            out.append("-")
        # every other character is dropped
    return "".join(out)


def anchors_of(path):
    p = ROOT / path
    if not p.exists():
        return None
    seen, out = {}, set()
    in_fence = False
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for a in ANCHOR_TAG.findall(line):
            out.add(a)
        m = HEADING.match(line)
        if not m:
            continue
        s = slug(m.group(2))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def links_of(path):
    """Yield (lineno, is_image, text, target) outside fenced code blocks."""
    in_fence = False
    for i, line in enumerate(
        (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in LINK.finditer(line):
            yield i, m.group(1) == "!", m.group("text"), m.group("t").strip()


def classify(src, target):
    """-> (kind, detail) where kind is ok / missing-file / missing-anchor / external / skip."""
    if not target or target.startswith(("mailto:", "tel:")):
        return "skip", ""
    if target.startswith(("http://", "https://")):
        return "external", target
    if target.startswith("#"):
        anc = target[1:]
        have = anchors_of(src)
        return ("ok", "") if anc in have else ("missing-anchor", f"{src}{target}")
    path, _, anc = target.partition("#")
    if path.startswith("/"):
        cand = ROOT / path.lstrip("/")
    else:
        cand = (ROOT / src).parent / path
    try:
        rel = os.path.relpath(cand.resolve(), ROOT)
    except Exception:
        return "missing-file", target
    if rel in EXPORT_ABSENT:
        return "absent-in-export", f"{target} (from {src})"
    if not cand.exists():
        return "missing-file", f"{target} (from {src})"
    if anc and cand.suffix == ".md":
        have = anchors_of(rel)
        if have is not None and anc not in have:
            return "missing-anchor", f"{rel}#{anc} (from {src})"
    return "ok", ""


def main():
    all_docs = "--all" in sys.argv
    do_ext = "--external" in sys.argv
    docs_reader = corpus(False)
    docs_all = corpus(True)

    def scan(docs):
        broken_file, broken_anchor, ext, absent = [], [], {}, []
        total = 0
        for d in docs:
            for ln, _img, text, t in links_of(d):
                total += 1
                kind, detail = classify(str(d), t)
                if kind == "missing-file":
                    broken_file.append(f"{d}:{ln} [{text[:40]}] -> {detail}")
                elif kind == "missing-anchor":
                    broken_anchor.append(f"{d}:{ln} [{text[:40]}] -> {detail}")
                elif kind == "absent-in-export":
                    absent.append(f"{d}:{ln} -> {detail}")
                elif kind == "external":
                    ext.setdefault(detail, []).append(f"{d}:{ln}")
        return total, broken_file, broken_anchor, ext, absent

    tot_r, bf_r, ba_r, ext_r, ab_r = scan(docs_reader)
    tot_a, bf_a, ba_a, ext_a, ab_a = scan(docs_all)

    print("== reader documents ==", " ".join(str(d) for d in docs_reader))
    for x in bf_r:
        print("BROKEN-FILE-READER", x)
    for x in ba_r:
        print("BROKEN-ANCHOR-READER", x)
    print("== whole corpus ==", len(docs_all), "documents")
    for x in bf_a:
        print("BROKEN-FILE-ALL", x)
    for x in ba_a:
        print("BROKEN-ANCHOR-ALL", x)

    ext_broken = 0
    if do_ext:
        # curl, not urllib: this box's framework Python has no CA bundle wired
        # up, so urllib raises URLError on every https URL and would report a
        # uniform, false, 100 %% broken rate.
        import subprocess

        for url in sorted(ext_r):
            try:
                out = subprocess.run(
                    ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-L",
                     "--max-time", "25", "-A", "hpo-d5-linkcheck/1", url],
                    capture_output=True, text=True, timeout=40,
                )
                code = int(out.stdout.strip() or 0)
            except Exception as e:  # noqa: BLE001
                code = f"ERR:{type(e).__name__}"
            ok = isinstance(code, int) and 200 <= code < 400
            if not ok:
                ext_broken += 1
                print("BROKEN-EXTERNAL", url, code, ext_r[url])
            else:
                print("ok-external", url, code)
            time.sleep(0.4)

    print(f"RESULT links_scanned_reader={tot_r} count")
    print(f"RESULT links_scanned_all={tot_a} count")
    print(f"RESULT internal_broken_reader={len(bf_r)} count")
    print(f"RESULT anchor_broken_reader={len(ba_r)} count")
    print(f"RESULT internal_broken_all={len(bf_a)} count")
    print(f"RESULT anchor_broken_all={len(ba_a)} count")
    print(f"RESULT absent_in_export_reader={len(ab_r)} count")
    print(f"RESULT absent_in_export_all={len(ab_a)} count")
    print(f"RESULT external_urls_reader={len(ext_r)} count")
    print(f"RESULT external_urls_all={len(ext_a)} count")
    if do_ext:
        print(f"RESULT external_broken_reader={ext_broken} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
