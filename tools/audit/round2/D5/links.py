#!/usr/bin/env python
# D5 harness: link check over every user-facing markdown document.
#
# Metric: number of markdown links (inline, image, reference, autolink, bare
# URL) whose target does not resolve -- an internal path that does not exist
# in the tree, an anchor that matches no heading slug in the target document
# (GitHub slug rules), or an external URL that answers 4xx/5xx or not at all
# to a HEAD request.
#
# Command:
#   PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D5/links.py
#   (from the repository root; add --no-net to skip the external HEAD pass)
#
# Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884), all exact:
#   RESULT internal_links_total=46
#   RESULT broken_internal_paths=3   (all three point at docs/backlog.md, which the
#          audit export removed on purpose; in the repository they resolve)
#   RESULT broken_internal_paths_excluding_export_removed=0
#   RESULT broken_anchors=0
#   RESULT external_links_total=6  external_broken=0  external_inconclusive=0
#          external_unreachable=0   (network-dependent; HEAD only)
#
# Machine: Apple M1 (8 cores, 8 GB), macOS 26.6, Python 3.13.1.
# Instrumented symbol: the documents themselves (README.md, DISCLAIMER.md,
# docs/*.md, tests/README.md); nothing in production is hooked.
# Perturbation: change any link target in README.md to a path that does not
# exist -> broken_internal_paths goes UP by one.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import re
import sys
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = [ROOT / "README.md", ROOT / "DISCLAIMER.md", ROOT / "tests" / "README.md"] + sorted(
    (ROOT / "docs").glob("*.md")
)
# Files the audit export removes on purpose (COMMON.md): a link to one of
# these is broken here but not in the repository.
EXPORT_REMOVED = {"docs/backlog.md", "RELEASE_NOTES.md"}
EXPORT_REMOVED_PATTERNS = ("docs/audit-",)

INLINE_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REF_DEF = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)", re.M)
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
BARE_URL = re.compile(r"(?<![\(<`\[])(https?://[^\s<>\)\]`]+)")


def strip_code(text: str):
    """Return the text with fenced blocks and inline code blanked (same length)."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def headings(path: Path):
    """GitHub-style slugs of every heading outside fenced code."""
    slugs = []
    seen = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        text = m.group(2)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        text = re.sub(r"[*_]", "", text)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        slug = text.strip().lower()
        slug = re.sub(r"[^\w\- ]", "", slug)
        slug = slug.replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        slugs.append(slug if n == 0 else f"{slug}-{n}")
    return set(slugs)


def collect(path: Path):
    raw = path.read_text(encoding="utf-8")
    text = strip_code(raw)
    links = []
    for m in INLINE_LINK.finditer(text):
        links.append((m.group(2), text[: m.start()].count("\n") + 1))
    for m in REF_DEF.finditer(text):
        links.append((m.group(2), text[: m.start()].count("\n") + 1))
    for m in AUTOLINK.finditer(text):
        links.append((m.group(1), text[: m.start()].count("\n") + 1))
    covered = {t for t, _ in links}
    for m in BARE_URL.finditer(text):
        url = m.group(1).rstrip(".,;:")
        if url not in covered:
            links.append((url, text[: m.start()].count("\n") + 1))
    return links


def head(url: str, timeout: float = 20.0):
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (audit link check; HEAD only)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc.reason)
    except Exception as exc:  # noqa: BLE001
        return None, repr(exc)


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
    do_net = "--no-net" not in sys.argv
    internal_total = 0
    broken_paths = []
    broken_paths_real = []
    broken_anchors = []
    external = {}
    slug_cache = {}
    for doc in DOCS:
        for target, line in collect(doc):
            where = f"{doc.relative_to(ROOT)}:{line}"
            if target.startswith(("http://", "https://")):
                external.setdefault(target, []).append(where)
                continue
            if target.startswith("mailto:"):
                continue
            internal_total += 1
            path_part, _, anchor = target.partition("#")
            if path_part:
                resolved = (doc.parent / path_part).resolve()
                rel = os.path.relpath(resolved, ROOT)
                if not resolved.exists():
                    broken_paths.append((where, target))
                    if rel not in EXPORT_REMOVED and not rel.startswith(EXPORT_REMOVED_PATTERNS):
                        broken_paths_real.append((where, target))
                    continue
                if anchor and resolved.suffix == ".md":
                    slugs = slug_cache.setdefault(resolved, headings(resolved))
                    if anchor.lower() not in slugs:
                        broken_anchors.append((where, target))
            elif anchor:
                slugs = slug_cache.setdefault(doc, headings(doc))
                if anchor.lower() not in slugs:
                    broken_anchors.append((where, target))

    print(f"docs checked: {len(DOCS)}")
    for where, t in broken_paths:
        tag = "" if (where, t) in broken_paths_real else "  [removed from the export on purpose]"
        print(f"BROKEN PATH   {where}  -> {t}{tag}")
    for where, t in broken_anchors:
        print(f"BROKEN ANCHOR {where}  -> {t}")

    ext_broken, ext_inconclusive, ext_unreachable = [], [], []
    if do_net:
        for url, wheres in sorted(external.items()):
            status, reason = head(url)
            if status is None:
                ext_unreachable.append((url, reason, wheres))
                verdict = "UNREACHABLE"
            elif 200 <= status < 400:
                verdict = "ok"
            elif status in (403, 405, 429, 999):
                ext_inconclusive.append((url, status, wheres))
                verdict = "INCONCLUSIVE"
            else:
                ext_broken.append((url, status, wheres))
                verdict = "BROKEN"
            print(f"EXT {verdict:12s} {status!s:>5} {url}  ({', '.join(wheres[:3])})")

    print(f"RESULT internal_links_total={internal_total} count")
    print(f"RESULT broken_internal_paths={len(broken_paths)} count")
    print(f"RESULT broken_internal_paths_excluding_export_removed={len(broken_paths_real)} count")
    print(f"RESULT broken_anchors={len(broken_anchors)} count")
    print(f"RESULT external_links_total={len(external)} count")
    print(f"RESULT external_broken={len(ext_broken)} count")
    print(f"RESULT external_inconclusive={len(ext_inconclusive)} count")
    print(f"RESULT external_unreachable={len(ext_unreachable)} count")
    footer(t_proc0, t_thr0)


if __name__ == "__main__":
    main()
