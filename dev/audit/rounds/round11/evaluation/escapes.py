#!/usr/bin/env python3
"""Check the by-hand escapes ledger against the roster and print what it counts.

Usage: python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --roster <SHA:PATH> [--ref <graded sha>] [--ledger escapes_hand.tsv]
The matching rule: a roster group is a candidate when it lists a file under custom_components/ or blueprints/ and its
`source` is outside or user, or its `kind` is owner, bug, hotfix or owner-step, or its id holds HOTFIX or OUTSIDE, or its
brief matches REPORT below. Refuses (rc 1) a candidate with no row, a row that is no candidate, a group rowed twice, an
owner that is neither `none`, `-` nor a tracked dimension brief, and a window outside in, day0, unreleased, out. Prints rows
per owner and per window (`in`: an escape; `day0`: dated the closeout stamp's own day; `unreleased`: injected and caught
before a release; `out`: no escape, with its reason), the `none` rows of window `in` (the unowned items), the rows naming a
cause pull request, and the in-window rows for which a root-cause record is tracked under dev/audit/rca/ at --ref (matched on
the group id less its R10-, HOTFIX- and OUTSIDE- prefixes). A proxy for `escapes`, `unowned` and `injected`, never the terms:
the roster records no found-by and no owning dimension, and a brief's cause is the fixer's unless a root-cause record names it.
"""
import argparse, collections, json, re, subprocess, sys
from pathlib import Path

REPORT = re.compile(r"owner[- ]report|outside report|owner request|owner order|owner question|outside pull request|outside contribution"
                    r"|outside user|live user|live defect|live bug|reported by the owner|owner[- ]reported"
                    r"|the owner's (own )?(install|export|house|live)|from his (own )?install|\(owner, 20"
                    r"|found by (the )?R10-|found by the .{0,40}fixer|defect still in main|latent", re.I)
PRODUCT = ("custom_components/", "blueprints/")


def candidate(g):
    if not any(str(f).startswith(PRODUCT) for f in g.get("files") or []):
        return False
    brief = " ".join(str(g.get("brief")).split())
    return bool(g.get("source") in ("outside", "user") or str(g.get("kind")) in ("owner", "bug", "hotfix", "owner-step")
                or "HOTFIX" in g["group"] or "OUTSIDE" in g["group"] or REPORT.search(brief))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--roster", required=True); ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--ledger", default=str(Path(__file__).with_name("escapes_hand.tsv")))
    a = ap.parse_args()
    git = lambda *x: subprocess.run(["git", "-C", a.repo, *x], capture_output=True, text=True).stdout
    groups = {g["group"]: g for g in json.loads(git("show", a.roster))["groups"]}
    cands = {k for k, g in groups.items() if candidate(g)}
    lines = [l.rstrip("\n").split("\t") for l in open(a.ledger) if l.strip() and not l.startswith("#")]
    rows = [dict(zip(lines[0], r)) for r in lines[1:]]
    bad = []
    seen = collections.Counter(r["group"] for r in rows)
    bad += [f"{k}: rowed {n} times" for k, n in seen.items() if n > 1]
    bad += [f"{k}: a candidate with no row" for k in sorted(cands - set(seen))]
    bad += [f"{k}: a row that is no candidate" for k in sorted(set(seen) - cands)]
    for r in rows:
        if r["window"] not in ("in", "day0", "unreleased", "out"):
            bad.append(f"{r['group']}: window {r['window']}")
        if r["owner"] not in ("none", "-") and not git("ls-tree", "--name-only", a.ref, f"dev/governance/dimensions/{r['owner']}.md").strip():
            bad.append(f"{r['group']}: owner {r['owner']} is no dimension brief")
        if (r["window"] == "out") != (r["owner"] == "-"):
            bad.append(f"{r['group']}: an `out` row carries owner `-`, and no other row does")
    for b in bad:
        print("REFUSED", b)
    order = lambda kv: (kv[0] in ("none", "-"), int(kv[0][1:]) if kv[0][1:].isdigit() else 0)
    for w in ("in", "day0", "unreleased", "out"):
        c = collections.Counter(r["owner"] for r in rows if r["window"] == w)
        print(f"window={w}\trows={sum(c.values())}\t" + " ".join(f"{k}={v}" for k, v in sorted(c.items(), key=order)))
    inw = [r for r in rows if r["window"] == "in"]
    print("UNOWNED", ",".join(r["group"] for r in inw if r["owner"] == "none"))
    print("CAUSE_NAMED", ",".join(f"{r['group']}<-#{r['cause_pr']}({r['window']})" for r in rows if r["cause_pr"] != "-"))
    print("CAUSES", len({c for r in rows if r["cause_pr"] != "-" for c in r["cause_pr"].split(",")}))
    print("REPORTERS", dict(collections.Counter(r["reporter"] for r in inw)))
    rca = [l for l in git("ls-tree", "-r", "--name-only", a.ref, "dev/audit/rca/").split("\n") if l]
    stem = lambda k: re.sub(r"^R1[01]-(HOTFIX-|OUTSIDE-)?", "", k)
    print("RCA_TRACKED", ",".join(r["group"] for r in inw if any(stem(r["group"]) in f for f in rca)))
    print(f"CANDIDATES {len(cands)} ROWS {len(rows)} REFUSED {len(bad)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
