#!/usr/bin/env python3
"""The harvest's disposition of every box-reported kill, one line per anchor.

    summarise.py CANDIDATES.json SPLIT.json DECLINED.json OUT_ROOT BATCHES > DISPOSITIONS.tsv

CANDIDATES.json, DECLINED.json: enumerate.py's outputs. SPLIT.json: collide.py's.
OUT_ROOT holds one pin_harvest.py drive output directory per batch (pins.json,
survivors.txt, status); BATCHES holds <script>.json, the anchors
driven with --scripts tests/<script> (pass2.json: re-driven with the default
drivers after their own drive drove nothing). Prints `<disposition>\t<anchor>\t<detail>` per anchor
and, on stderr, one count per disposition; every count the PR body quotes is
`cut -f1 DISPOSITIONS.tsv | sort | uniq -c`.
"""
import json
import sys
from pathlib import Path

cand, split, declined, root = (json.load(open(sys.argv[1])), json.load(open(sys.argv[2])),
                               json.load(open(sys.argv[3])), Path(sys.argv[4]))
driven = {}
for b in sorted(Path(sys.argv[5]).glob("*.json")):
    status = (root / b.stem / "status")
    st = status.read_text().strip() if status.exists() else "not-run"
    for a in json.loads(b.read_text()):
        driven.setdefault(a, []).append(f"{b.stem}={st}")
pinned, survived = {}, {}
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    pins = d / "pins.json"
    if pins.exists():
        for a, e in json.loads(pins.read_text()).items():
            pinned.setdefault(a, e["killed_by"])
    surv = d / "survivors.txt"
    if surv.exists():
        for line in surv.read_text().splitlines():
            survived.setdefault(line.strip(), d.name)
rows = []
for a in declined["disposed"]:
    rows.append(("declined-already-disposed", a, "a killed_by or survivor_triage row at main"))
for a in declined.get("absent", []):
    rows.append(("dropped-anchor-gone", a, "no inventory site at main"))
for a in declined["nonledger"]:
    rows.append(("declined-not-inventory", a, "a hand mutant id, not an inventory anchor"))
for a, g in split["fold"].items():
    rows.append(("deferred-fold", a, g))
for a, n in split["pr"].items():
    rows.append(("deferred-pr", a, ",".join(f"#{x}" for x in n)))
for a in split["drive"]:
    boxes = ";".join(sorted({f"{r['src']}:{','.join(r['killed_by'] or [])}" for r in cand[a]}))
    if a in pinned:
        rows.append(("pinned", a, pinned[a]))
    else:
        how = ";".join(driven.get(a, ["no-driver: no box killer is a mutation_table driver"]))
        rows.append(("dropped-not-reproduced", a, f"box {boxes} | drive {how}"))
for r in rows:
    print("\t".join(r))
counts = {}
for r in rows:
    counts[r[0]] = counts.get(r[0], 0) + 1
for k in sorted(counts):
    print(f"{counts[k]:5d} {k}", file=sys.stderr)
