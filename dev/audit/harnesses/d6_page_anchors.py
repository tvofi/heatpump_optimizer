#!/usr/bin/env python3
"""D6: every internal `href="#x"` on a web page resolves to an `id="x"`.

    python3 dev/audit/harnesses/d6_page_anchors.py PAGE [PAGE ...]
    python3 dev/audit/harnesses/d6_page_anchors.py docs/index.html \\
        https://tvofi.github.io/heatpump_optimizer/

A PAGE is a file path or an http(s) URL. A HEAD request never sends the
`#fragment`, so it answers 200 for a broken anchor; this fetches each page,
collects every `id` (and `name` on `<a>`), and lists each internal reference
that names none. One line per page: ids, internal hrefs, distinct targets,
unresolved targets. Exit 1 when any page has an unresolved target, or no
internal href at all (a check over an empty set passes nothing). The
sub-pages are the files `tools/site/build_docs.mjs --out DIR` writes, or
their URLs beside the live page.

Perturbation: rename the `id` an internal href names (on docs/index.html,
`id="main"`) and the page reports it unresolved and exits 1.
"""
from __future__ import annotations

import sys
import urllib.request
from html.parser import HTMLParser


class _Anchors(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        a = dict(attrs)
        for key in ("id", "name") if tag == "a" else ("id",):
            if a.get(key):
                self.ids.add(a[key])
        href = a.get("href") or ""
        if href.startswith("#") and len(href) > 1:
            self.refs.append(href[1:])

    handle_startendtag = handle_starttag


def check(page: str) -> bool:
    if page.startswith(("http://", "https://")):
        with urllib.request.urlopen(page, timeout=30) as r:
            text = r.read().decode("utf-8")
    else:
        with open(page, encoding="utf-8") as f:
            text = f.read()
    p = _Anchors()
    p.feed(text)
    bad = sorted({r for r in p.refs if r not in p.ids})
    print(f"{page}: ids={len(p.ids)} internal_hrefs={len(p.refs)} "
          f"distinct={len(set(p.refs))} unresolved={len(bad)} {bad}")
    return bool(p.refs) and not bad


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    results = [check(page) for page in argv]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
