#!/usr/bin/env python3
"""D5 harness: markdown link and anchor integrity across the documentation set.

Metric definition (one line): count of markdown links whose relative target
file does not exist, plus count of same-file (#fragment) and cross-file
(.md#fragment) anchors that match no heading slug in the target file.

Run from the repository root:
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D5/doc_links.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box)

Fresh-eyes note: this export deliberately omits docs/audit-*.md,
docs/backlog.md, tools/audit/round3 and tools/audit/round4. Links that point at
those exact paths are counted in RESULT removed_path_links and NOT in
broken_internal_links; they are not defects of the baseline.

Fences (``` ... ```) and raw `-quoted example spans are skipped: the plan docs
quote link syntax as data.

Perturbation the count must move under: re-point a working relative link at a
missing file (one-line edit); broken_internal_links goes up by one.
"""
import os, re, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.getcwd()
REMOVED = {"docs/audit-2026-08.md", "docs/audit-2026-09.md", "docs/backlog.md"}
MD_GLOBS = ["*.md", "docs/**/*.md", "tests/**/*.md", "tools/**/*.md",
            ".github/**/*.md", ".claude/**/*.md", "blueprints/**/*.md"]

LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def md_files():
    import glob
    out = []
    for g in MD_GLOBS:
        out += glob.glob(g, recursive=True)
    return sorted(set(p for p in out
                      if os.path.relpath(p, ".") not in REMOVED))


CODE_SPAN = re.compile(r"`[^`]*`")


def strip_fences(text):
    out, infence = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            infence = not infence
            out.append("")
            continue
        out.append("" if infence else line)
    return "\n".join(out)


def strip_code_spans(text):
    """Blank out inline `code spans` so link syntax quoted as data is not read
    as a link.

    The plan docs quote example markdown -- e.g. an image link written inside
    single backticks -- precisely so a reader sees the syntax rather than a
    rendered link. A bare ``finditer`` over the line counts those as broken
    targets; blanking the span first leaves only real links.
    """
    return CODE_SPAN.sub(" ", text)


def slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[`*]", "", s)
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def headings(text):
    h = set()
    infence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            infence = not infence
            continue
        if infence:
            continue
        m = re.match(r"#{1,6}\s+(.*)$", line)
        if m:
            h.add(slug(m.group(1)))
    return h


def main():
    files = md_files()
    texts = {f: open(f, encoding="utf-8", errors="ignore").read() for f in files}
    heads = {f: headings(t) for f, t in texts.items()}
    broken, removed_links, anchors_bad = [], [], []
    total = 0
    for f in files:
        body = strip_code_spans(strip_fences(texts[f]))
        for m in LINK.finditer(body):
            url = m.group(2).strip()
            total += 1
            if url.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            # placeholders used as examples / templates
            if any(ch in url for ch in ("…", "…")) or url in ("src",) \
                    or url.endswith("/N") or url == "…":
                continue
            path, _, frag = url.partition("#")
            path = path.split("?")[0]
            if path == "":
                tgt = f
                rel = os.path.relpath(f, ".").replace(os.sep, "/")
            else:
                tgt = os.path.normpath(os.path.join(os.path.dirname(f), path))
                rel = os.path.relpath(tgt, ".").replace(os.sep, "/")
            if not os.path.exists(tgt):
                if rel in REMOVED:
                    removed_links.append((f, url))
                else:
                    broken.append((f, url, rel))
                continue
            if frag and tgt.endswith(".md"):
                want = frag.lower()
                if want not in heads.get(tgt, set()):
                    anchors_bad.append((f, url, tgt))
    print("RESULT md_files=%d files" % len(files))
    print("RESULT links_total=%d links" % total)
    print("RESULT broken_internal_links=%d links" % len(broken))
    for b in broken:
        print("  BROKEN %s -> %s (%s)" % b)
    print("RESULT broken_anchors=%d anchors" % len(anchors_bad))
    for b in anchors_bad:
        print("  ANCHOR %s -> %s (no slug in %s)" % b)
    print("RESULT removed_path_links=%d links (fresh-eyes paths; not defects)"
          % len(removed_links))
    for r in removed_links:
        print("  REMOVED-PATH %s -> %s" % r)
    print("RESULT thread_factor=1.0")
    try:
        print("RESULT load1=%s" % os.getloadavg()[0])
    except OSError:
        print("RESULT load1=-1")


if __name__ == "__main__":
    main()
