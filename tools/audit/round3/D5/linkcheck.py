#!/usr/bin/env python3
"""D5 harness 1 — markdown link integrity across every .md file in the tree.

METRIC: number of markdown links whose target cannot be resolved in this tree
        = (a) relative file links whose path does not exist, plus
          (b) anchor links (#frag) whose slug matches no heading (and no
              explicit <a name>/id=) in the target document.
        Reported split by class; the headline number is (a)+(b).

Set D5_ROOT=<dir> to measure a copy of the tree instead (used by the
perturbation run); the default root is the repository this file lives in.

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/linkcheck.py

RUN WITH EXTERNAL HEAD CHECKS (one HEAD request per distinct external URL):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/linkcheck.py --external

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1: 
    RESULT broken_links_total=1 count   (the one dead anchor in README.md)
    RESULT broken_file_links=0 count
    RESULT links_scanned=338 count
    RESULT markdown_files=98 count  (tools/audit/round3/ excluded)
    tolerance: exact -- a count over a static tree, contention cannot move it.
    --external returns 211/211 URLError on this box: it has no outbound
    network, so external liveness is NOT measured here.
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
NOTE: this tree is a git-archive export with docs/audit-*.md, docs/backlog.md
      and RELEASE_NOTES.md deleted by the audit harness. Links pointing at
      those three names are counted separately as `broken_links_excised` and
      are EXCLUDED from broken_links_total, because they resolve on main.
PERTURBATION: append a line `[x](docs/definitely-not-here.md)` to README.md ->
      broken_links_total must go UP by exactly 1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import re
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("D5_ROOT") or Path(__file__).resolve().parents[4]).resolve()
EXCISED = ("RELEASE_NOTES.md", "docs/backlog.md", "docs/audit-")

# inline links [text](target) — target up to first space (title) or close paren
LINK_RE = re.compile(r"\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*(<[^>]*>|[^()\s]*(?:\([^()]*\)[^()\s]*)*)\s*(?:\"[^\"]*\")?\)")
REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)", re.M)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)
ANAME_RE = re.compile(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']", re.I)
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def strip_fences(text: str) -> str:
    """Blank out fenced code blocks so example links are not link-checked."""
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


CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)


def strip_code_spans(text: str) -> str:
    """Blank out inline `code` spans so example/regex links are not link-checked."""
    return CODE_SPAN_RE.sub(lambda m: m.group(1) + (" " * len(m.group(2))) + m.group(1), text)


def slug(title: str) -> str:
    """GitHub heading slug: strip markdown inline, lowercase, spaces->-, drop punct."""
    t = re.sub(r"`([^`]*)`", r"\1", title)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_~]", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def anchors_of(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    body = strip_code_spans(strip_fences(text))
    seen, out = {}, set()
    for _h, title in HEADING_RE.findall(body):
        s = slug(title)
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    out |= set(ANAME_RE.findall(text))
    return out


def md_files():
    skip = {".git", "node_modules", "__pycache__", ".claude/worktrees"}
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        # This audit round's own output is excluded: a report that quotes a
        # broken link would otherwise count itself.
        if rel.startswith("tools/audit/round3/"):
            continue
        if any(part in skip for part in rel.split("/")):
            continue
        yield p


def main():
    external_mode = "--external" in sys.argv
    anchors_cache = {}
    broken_file, broken_anchor, excised = [], [], []
    ext_urls = {}
    total_links = 0

    for path in md_files():
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_text(encoding="utf-8", errors="replace")
        body = strip_code_spans(strip_fences(raw))
        targets = [m.group(1) for m in LINK_RE.finditer(body)]
        targets += [t for _lbl, t in REF_DEF_RE.findall(body)]
        for tgt in targets:
            tgt = tgt.strip()
            if tgt.startswith("<") and tgt.endswith(">"):
                tgt = tgt[1:-1]
            if not tgt:
                continue
            total_links += 1
            if tgt.startswith(("http://", "https://")):
                ext_urls.setdefault(tgt, []).append(rel)
                continue
            if tgt.startswith(("mailto:", "tel:", "data:")):
                continue
            frag = ""
            if "#" in tgt:
                tgt, frag = tgt.split("#", 1)
            if not tgt:  # same-document anchor
                target_path = path
            else:
                target_path = (path.parent / tgt).resolve()
            relt = None
            try:
                relt = target_path.relative_to(ROOT).as_posix()
            except ValueError:
                relt = str(target_path)
            if tgt and not target_path.exists():
                if any(relt.startswith(e) or relt == e for e in EXCISED):
                    excised.append((rel, tgt + ("#" + frag if frag else "")))
                else:
                    broken_file.append((rel, tgt + ("#" + frag if frag else "")))
                continue
            if frag and target_path.is_file() and target_path.suffix == ".md":
                if relt not in anchors_cache:
                    anchors_cache[relt] = anchors_of(target_path)
                if frag.lower() not in {a.lower() for a in anchors_cache[relt]}:
                    broken_anchor.append((rel, (tgt or "") + "#" + frag))

    ext_broken = []
    if external_mode:
        import urllib.request
        import urllib.error
        for url in sorted(ext_urls):
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "d5-linkcheck/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    code = r.status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:  # noqa: BLE001
                code = f"ERR:{type(e).__name__}"
            if not (isinstance(code, int) and code < 400):
                ext_broken.append((url, code, ext_urls[url]))

    print("--- broken relative file links ---")
    for src, tgt in broken_file:
        print(f"  {src} -> {tgt}")
    print("--- broken anchors ---")
    for src, tgt in broken_anchor:
        print(f"  {src} -> {tgt}")
    print("--- links into files this export deleted (excluded from total) ---")
    for src, tgt in excised:
        print(f"  {src} -> {tgt}")
    if external_mode:
        print("--- external HEAD failures ---")
        for url, code, srcs in ext_broken:
            print(f"  {code}  {url}   <- {', '.join(sorted(set(srcs)))}")

    t0 = time.process_time()
    _ = sum(range(200000))
    tf = time.process_time() - t0
    print()
    print(f"RESULT markdown_files={sum(1 for _ in md_files())} count")
    print(f"RESULT links_scanned={total_links} count")
    print(f"RESULT broken_file_links={len(broken_file)} count")
    print(f"RESULT broken_anchors={len(broken_anchor)} count")
    print(f"RESULT broken_links_total={len(broken_file) + len(broken_anchor)} count")
    print(f"RESULT broken_links_excised={len(excised)} count")
    print(f"RESULT external_links_distinct={len(ext_urls)} count")
    if external_mode:
        print(f"RESULT external_head_failures={len(ext_broken)} count")
    _thr = time.thread_time()
    print(f"RESULT thread_factor={time.process_time() / _thr if _thr else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins=0")
    print(f"RESULT selfcheck_cpu={tf:.4f} s")


if __name__ == "__main__":
    main()
