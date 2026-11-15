#!/usr/bin/env python3
"""Check the by-hand escapes ledger against the roster and print what it counts.

Usage: python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --roster <REF:PATH> [--ledger escapes_hand.tsv]
Refuses (rc 1) a row whose group is not on the roster, lists no file under custom_components/ or blueprints/, or names an
owner that is neither `none` nor a tracked dimension brief. Prints rows per owner and per window (`in`: an escape; `day0`:
dated the closeout stamp's own day; `unreleased`: injected and caught before a release), the `none` rows of window `in`
(the unowned items), and the rows naming a cause pull request. A proxy for `escapes`, `unowned` and `injected`, never the terms:
the roster records no found-by and no owning dimension, and a brief's cause is the fixer's, not the root-cause seat's.
"""
import argparse, collections, json, subprocess, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--roster", required=True)
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("escapes_hand.tsv")))
    a = ap.parse_args()
    groups = {g["group"]: g for g in json.loads(subprocess.run(["git", "-C", a.repo, "show", a.roster], capture_output=True, text=True).stdout)["groups"]}
    rows = [l.rstrip("\n").split("\t") for l in open(a.ledger) if l.strip() and not l.startswith("#")]
    head, rows = rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]
    bad = []
    for r in rows:
        g = groups.get(r["group"])
        if g is None:
            bad.append(f"{r['group']}: not on the roster")
        elif not any(str(f).startswith(("custom_components/", "blueprints/")) for f in g.get("files") or []):
            bad.append(f"{r['group']}: lists no product file")
        if r["owner"] != "none" and not (Path(a.repo) / f"dev/governance/dimensions/{r['owner']}.md").exists():
            bad.append(f"{r['group']}: owner {r['owner']} is no dimension brief")
    for b in bad:
        print("REFUSED", b)
    for w in ("in", "day0", "unreleased"):
        c = collections.Counter(r["owner"] for r in rows if r["window"] == w)
        print(f"window={w}\trows={sum(c.values())}\t" + " ".join(f"{k}={v}" for k, v in sorted(c.items(), key=lambda kv: (kv[0] == "none", int(kv[0][1:]) if kv[0][1:].isdigit() else 0))))
    print("UNOWNED", ",".join(r["group"] for r in rows if r["owner"] == "none" and r["window"] == "in"))
    print("CAUSE_NAMED", ",".join(f"{r['group']}<-#{r['cause_pr']}" for r in rows if r["cause_pr"] != "-"))
    print("REPORTERS", dict(collections.Counter(r["reporter"] for r in rows if r["window"] == "in")))
    print(f"ROWS {len(rows)} REFUSED {len(bad)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
