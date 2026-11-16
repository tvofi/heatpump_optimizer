#!/usr/bin/env python3
"""Count a start evaluation's verdicts, its unscored share and its cards.

Usage: python3 dev/audit/rounds/round11/evaluation/tally.py [EVALUATION.json]
Prints `keep`, `change` and `remove` per object class and in total; `NO-READ`, the kept objects whose evidence says NO-READ
as words of its own (check_scopes.is_no_read's rule), with the unscored share 0018 section 3 asks for; the terms read and
NO-READ; and the cards by what each answers. Exit 1 if an object of objective.json has no row or a non-keep row no card.
"""
import collections, json, re, subprocess, sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


repo = repo_root(__file__)
path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "dev/audit/yardstick/round11/EVALUATION.json"
ev = json.loads(path.read_text())
sys.path.insert(0, str(repo / "tools/audit"))
import check_scopes as cs

tree = [t for t in subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True).stdout.split("\n") if t]
spec = json.loads((repo / "dev/audit/config/objective.json").read_text())
rows, cards, bad = ev["objects"], ev["cards"], []
tot = collections.Counter()
print("class\tobjects\tkeep\tchange\tremove\tNO-READ")
for cls, globs in spec["objects"].items():
    c = collections.Counter()
    objs = sorted(cs.match(tree, globs))
    for f in objs:
        r = rows.get(f)
        if not r:
            bad.append(f"{f}: no row"); continue
        c[r["verdict"]] += 1
        c["NO-READ"] += r["verdict"] == "keep" and cs.is_no_read(r["evidence"])
        if r["verdict"] != "keep" and r.get("card") not in cards:
            bad.append(f"{f}: {r['verdict']} names no card")
    tot.update(c); tot["objects"] += len(objs)
    print(f"{cls}\t{len(objs)}\t{c['keep']}\t{c['change']}\t{c['remove']}\t{c['NO-READ']}")
print(f"TOTAL\t{tot['objects']}\tkeep={tot['keep']}\tchange={tot['change']}\tremove={tot['remove']}\tNO-READ={tot['NO-READ']}\tunscored share {tot['NO-READ']}/{tot['objects']} ({tot['NO-READ'] / max(tot['objects'], 1):.2f})")
t = ev.get("terms", {})
print(f"TERMS\t{len(t)}\tread={sum('value' in v for v in t.values())}\tNO-READ={sum('no_read' in v for v in t.values())}")
kinds = collections.Counter()
for cid, c in cards.items():
    kinds["threshold" if c.get("threshold") else "criterion" if c.get("criterion") else "unowned" if c.get("unowned") else
          "object" if any(r.get("card") == cid for r in rows.values()) else "no-read or other"] += 1
print(f"CARDS\t{len(cards)}\t" + "\t".join(f"{k}={v}" for k, v in sorted(kinds.items())) + f"\tdecided={sum(1 for c in cards.values() if c.get('decision'))}")
for b in bad:
    print("REFUSED", b)
sys.exit(1 if bad else 0)
