#!/usr/bin/env python3
"""R11-PRE-PLAN-RENDER: what a plan page carries, as a set of structural items.

    python3 dev/audit/harnesses/r11_plan_page_inventory.py BASE.html [OTHER.html ...]

Prints the inventory of BASE: one line per item, kind and value, every digit
run read as `#` so a figure that moved between two snapshots is the same item.
The kinds: heading, table header row, legend entry, filter control, element
id, class name, data attribute, event listener, link target shape, and a
tooltip on a chart bar. For each OTHER it then prints `MISSING <item>` for
every BASE item OTHER lacks, `ADDED <item>` for every item only OTHER has,
and `RESULT other=<path> missing=<n> added=<n>`. Exit 1 when any OTHER misses
an item. Null control: a page against itself prints missing=0 added=0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _n(s: str) -> str:
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", s)).strip()


def inventory(text: str) -> set:
    items = set()
    for lvl, h in re.findall(r"<h([123])[^>]*>(.*?)</h\1>", text, re.S):
        items.add(f"heading h{lvl}: {_n(re.sub(r'<[^>]+>', '', h))}")
    for head in re.findall(r"<thead>(.*?)</thead>", text, re.S):
        items.add("table: " + " | ".join(_n(re.sub(r"<[^>]+>", "", c))
                                         for c in re.findall(r"<th[^>]*>(.*?)</th>", head, re.S)))
    for leg in re.findall(r'<div class="legend">(.*?)</div>', text, re.S):
        for span in re.findall(r"<span>(.*?)</span>", leg, re.S):
            items.add(f"legend: {_n(re.sub(r'<[^>]+>', '', span))}")
    items |= {f"filter: {f}" for f in re.findall(r'data-f="([^"]+)"', text)}
    items |= {f"id: {i}" for i in re.findall(r'<\w+[^>]*?\sid="([^"]+)"', text)}
    items |= {f"class: {c}" for cs in re.findall(r'\sclass="([^"]+)"', text) for c in cs.split()}
    items |= {f"data attribute: {d}" for d in re.findall(r"\s(data-[a-z-]+)=", text)}
    items |= {f"listener: {ev}" for ev in re.findall(r"addEventListener\('([a-z]+)'", text)}
    items |= {f"link: {_n(h)}" for h in re.findall(r'href="([^"]+)"', text)}
    if re.search(r'<g class="grp"[^>]*>\s*<title>', text):
        items.add("tooltip: chart bar title")
    return items


def main(argv: list) -> int:
    if not argv:
        print(__doc__)
        return 2
    base = inventory(Path(argv[0]).read_text(encoding="utf-8"))
    for item in sorted(base):
        print(item)
    lost = 0
    for other in argv[1:]:
        inv = inventory(Path(other).read_text(encoding="utf-8"))
        for item in sorted(base - inv):
            print(f"MISSING {item}")
        for item in sorted(inv - base):
            print(f"ADDED {item}")
        print(f"RESULT other={Path(other).name} missing={len(base - inv)} added={len(inv - base)}")
        lost += len(base - inv)
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
