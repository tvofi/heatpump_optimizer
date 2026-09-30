#!/usr/bin/env python3
"""Prototype of the product-page pin (R9-WEB-1 ports it into tests/doc_claims.py as one arm).

Claim set: derived from the page. Every element carrying data-src="<doc>#<github-slug>" is a claim, in one of two modes:
  * verbatim (the default): every text node inside it, split on the ellipsis, must appear in that doc section
    (after the markdown is reduced to its reader text: emphasis, code ticks, links, images and HTML tags dropped);
  * key phrase (data-q present): data-q must appear in the section, and every number in the element must be a number
    the section states. For short tiles whose label is page copy.
Fact set: derived from the reader documents at a git ref (never a hand list).
Two-sided arms: every README "What it does" lead is a data-feature heading on the page, and the page's data-doc set
equals the README Documentation table's link targets, both ways.
Also refused: a digit in text outside any claim or data-copy element; a data-repo image absent from the tree (unless a
named later group lands it); a GitHub doc link whose path or heading slug does not resolve; a version literal; and, in
the impl profile, any third-party script, stylesheet, font or image.
Anchor (null control): no page, zero claims, zero features or zero docs rows is red.

RUN: python3 check_site.py PAGE [--ref 5dfa6684] [--repo CHECKOUT] [--profile design|impl]; controls: HPO_REPO=CHECKOUT python3 controls.py
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from html.parser import HTMLParser

# Files the page references that a named, earlier-ordered group lands. The implementation carries no such list: by the
# time R9-WEB-1 runs, its after-edges have merged and every reference must resolve in the tree.
PENDING = {
    "docs/img/readme/how-it-works.png": "R9-UI-2",
    "docs/img/readme/how-it-works-dark.png": "R9-UI-2",
}
REPO_URL = "https://github.com/tvofi/heatpump_optimizer/blob/main/"
DESIGN_HOSTS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")
NUM = re.compile(r"\d+(?:[.,]\d+)*")


class Doc:
    def __init__(self, repo: str, ref: str):
        self.repo, self.ref, self.cache = repo, ref, {}

    def text(self, path: str) -> str | None:
        if path not in self.cache:
            r = subprocess.run(["git", "-C", self.repo, "show", f"{self.ref}:{path}"], capture_output=True, text=True)
            self.cache[path] = r.stdout if r.returncode == 0 else None
        return self.cache[path]

    def exists(self, path: str) -> bool:
        r = subprocess.run(["git", "-C", self.repo, "cat-file", "-e", f"{self.ref}:{path}"], capture_output=True)
        return r.returncode == 0


def slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def sections(md: str) -> dict[str, str]:
    """GitHub heading slugs -> section text. A section runs to the next heading of level <= max(own, 2), so the
    title's section is the intro, and a ## section includes its ### subsections."""
    lines, heads, fence = md.splitlines(), [], False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            fence = not fence
            continue
        m = None if fence else re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    out, seen = {}, {}
    for k, (i, lvl, title) in enumerate(heads):
        stop = len(lines)
        for j, l2, _ in heads[k + 1:]:
            if l2 <= max(lvl, 2):
                stop = j
                break
        s = slug(title)
        n = seen.get(s, 0)
        seen[s] = n + 1
        out[s if n == 0 else f"{s}-{n}"] = "\n".join(lines[i:stop])
    return out


def reader_text(md: str) -> str:
    t = re.sub(r"<!--.*?-->", " ", md, flags=re.S)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("**", "").replace("*", "").replace("`", "")
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return norm(html.unescape(t))


def norm(s: str) -> str:
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


class Page(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "use",
            "path", "circle", "rect"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.texts, self.elems, self.tags = [], [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag in self.VOID:
            return
        rec = {"tag": tag, "a": a, "text": []}
        self.stack.append(rec)
        self.elems.append(rec)

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k]["tag"] == tag:
                del self.stack[k:]
                return

    def handle_data(self, data):
        if not data.strip():
            return
        for r in self.stack:
            r["text"].append(data)
        owner = next((r for r in reversed(self.stack) if "data-src" in r["a"] or "data-copy" in r["a"]), None)
        inert = any(r["tag"] in ("script", "style", "svg", "title") for r in self.stack)
        self.texts.append((data, owner, inert))


def run(page_path: str, repo: str, ref: str, profile: str) -> tuple[list[str], dict]:
    errs, stats = [], {"claims": 0, "fragments": 0, "numbers": 0, "copy": 0, "features": 0, "docs": 0, "images": 0,
                       "links": 0}
    try:
        src = open(page_path, encoding="utf-8").read()
    except OSError:
        return [f"ANCHOR: page {page_path} absent"], stats
    d = Doc(repo, ref)
    p = Page()
    p.feed(src)
    secs: dict[str, dict[str, str]] = {}

    def section(ds: str) -> str | None:
        path, _, frag = ds.partition("#")
        if path not in secs:
            md = d.text(path)
            secs[path] = {k: reader_text(v) for k, v in sections(md).items()} if md is not None else None
        if secs[path] is None:
            errs.append(f"data-src {ds}: {path} is not in the tree at {ref}")
            return None
        if frag not in secs[path]:
            errs.append(f"data-src {ds}: no heading with slug #{frag} in {path}")
            return None
        return secs[path][frag]

    # claims
    for e in p.elems:
        if "data-copy" in e["a"]:
            stats["copy"] += 1
        ds = e["a"].get("data-src")
        if not ds:
            continue
        stats["claims"] += 1
        sec = section(ds)
        if sec is None:
            continue
        if "data-q" in e["a"]:
            q = norm(e["a"]["data-q"])
            if q not in sec:
                errs.append(f"{ds}: key phrase not in section: {e['a']['data-q']!r}")
            have = set(NUM.findall(sec))
            for n in NUM.findall(" ".join(e["text"])):
                stats["numbers"] += 1
                if n not in have:
                    errs.append(f"{ds}: number {n} is not stated in the section")
    for data, owner, inert in p.texts:
        if inert:
            continue
        if owner is None:
            if NUM.search(data):
                errs.append(f"a number outside any claim: {norm(data)[:80]!r}")
            continue
        if "data-copy" in owner["a"] or "data-q" in owner["a"]:
            continue
        sec = section(owner["a"]["data-src"])
        if sec is None:
            continue
        for frag in re.split(r"…|\.\.\.", data):
            f = norm(frag).strip(" .,;:")
            if not f:
                continue
            stats["fragments"] += 1
            if f not in sec:
                errs.append(f"{owner['a']['data-src']}: not in the section: {f[:90]!r}")

    # two-sided: features
    readme = d.text("README.md") or ""
    wid = sections(readme).get("what-it-does", "")
    leads = {norm(m).rstrip(".") for m in re.findall(r"^\*\*(.+?)\*\*", wid, flags=re.M)}
    feats = {norm(" ".join(e["text"])).rstrip(".") for e in p.elems if "data-feature" in e["a"]}
    stats["features"] = len(feats)
    for x in sorted(leads - feats):
        errs.append(f"README 'What it does' lead missing from the page: {x!r}")
    for x in sorted(feats - leads):
        errs.append(f"page feature that README 'What it does' does not lead with: {x!r}")

    # two-sided: documentation index
    dsec = sections(readme).get("documentation", "")
    rows = set(re.findall(r"^\|\s*\[[^\]]+\]\(([^)]+)\)", dsec, flags=re.M))
    docs = {a.get("data-doc") for t, a in p.tags if a.get("data-doc")}
    stats["docs"] = len(docs)
    for x in sorted(rows - docs):
        errs.append(f"README Documentation row missing from the page: {x}")
    for x in sorted(docs - rows):
        errs.append(f"page docs entry the README Documentation table does not list: {x}")

    # images, links, third parties
    for t, a in p.tags:
        if t in ("img", "source"):
            stats["images"] += 1
            rp = a.get("data-repo")
            if t == "img" and not (a.get("alt") or "").strip():
                errs.append(f"image without alt text: {a.get('src')}")
            if not rp:
                errs.append(f"image without data-repo: {a.get('src') or a.get('srcset')}")
            elif not d.exists(rp) and rp not in PENDING:
                errs.append(f"image {rp} is not in the tree at {ref} and no earlier group lands it")
            for u in (a.get("src"), a.get("srcset")):
                if u and u.startswith("http"):
                    errs.append(f"third-party image: {u}")
        if t == "a" and (a.get("href") or "").startswith(REPO_URL):
            stats["links"] += 1
            path, _, frag = a["href"][len(REPO_URL):].partition("#")
            if not d.exists(path):
                errs.append(f"link to {path}: not in the tree at {ref}")
            elif frag and path.endswith(".md") and frag not in sections(d.text(path) or ""):
                errs.append(f"link to {path}#{frag}: no such heading")
        if t == "script" and a.get("src"):
            errs.append(f"external script: {a['src']}")
        if t == "link" and "stylesheet" in (a.get("rel") or "") and a.get("href", "").startswith("http"):
            if profile == "impl" or not a["href"].startswith(DESIGN_HOSTS):
                errs.append(f"third-party stylesheet: {a['href']}")
    for m in re.finditer(r"(?:@import|url\()\s*['\"]?(https?://[^'\")\s]+)", src):
        errs.append(f"third-party resource in CSS: {m.group(1)}")

    # version literal
    visible = " ".join(t for t, _, inert in p.texts if not inert)
    version = (d.text("VERSION") or "").strip()
    if version and version in visible:
        errs.append(f"the page states the version {version} (CLAUDE.md rule 4: versions are stamped after merge)")
    for m in re.finditer(r"\bv\d+\.\d+(?:\.\d+)?\b", visible):
        errs.append(f"a version literal on the page: {m.group(0)}")

    # anchors
    for k in ("claims", "features", "docs"):
        if stats[k] == 0:
            errs.append(f"ANCHOR: zero {k} found; the check cannot pass by finding nothing")
    return errs, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--ref", default="5dfa6684")
    ap.add_argument("--repo", default="/home/user/heatpump_optimizer")
    ap.add_argument("--profile", choices=("design", "impl"), default="design")
    a = ap.parse_args()
    errs, st = run(a.page, a.repo, a.ref, a.profile)
    print(f"page {a.page} at {a.ref} ({a.profile}): " + ", ".join(f"{k} {v}" for k, v in st.items()))
    for e in errs:
        print("FAIL", e)
    print("RESULT:", "PASS" if not errs else f"{len(errs)} failure(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
