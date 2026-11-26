#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/dedup.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Dedup from the cross runs: A 'moves' B when B's probe, run with A's one-line mutant in place of B's,
moves at least one of the non-null arm pairs B's own run moved, with B's null pairs held.
Canonical per same-line cluster: greedily the key that moves the most others (ties: box then keys order)."""
import os, json, re, sys, pathlib, collections
WORK = pathlib.Path(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"))
WT = pathlib.Path.cwd()
sys.path.insert(0, str(WT / "dev/audit/rounds/round11/D3/wave-verify/harness"))
import v1_analyse as va

VOL = re.compile(r"^(thread_factor|load1|swapins|wall|elapsed|rss|time\b|t_)|cpu", re.I)
master = json.load(open(WORK / "master.json"))
order = {m["key"]: i for i, m in enumerate(sorted(master, key=lambda m: (m["box"], m["rec"].get("order", 0))))}
ana = json.load(open(WORK / "analysis.json"))


def res(s):
    return [l[7:].strip() for l in s.splitlines() if l.startswith("RESULT ") and not VOL.search(l[7:].strip().split("=")[0])]


def kv(lines):
    return {m.group(1): m.group(2).strip() for l in lines for m in [re.match(r"^(\S+?)\s*=\s*(.*)$", l)] if m}


def arms_of(runs):
    if "run" in runs:
        return va.arm_pairs(res(runs["run"]["stdout"]))
    b, mu = kv(res(runs["base"]["stdout"])), kv(res(runs["mut"]["stdout"]))
    return {n: [b.get(n), mu.get(n)] for n in set(b) | set(mu)}


def own_moved(k):
    r = json.load(open(WORK / "rerun" / f"{k}.json"))
    runs = {kk: r[kk] for kk in ("run", "base", "mut") if kk in r}
    a = arms_of(runs)
    return {n for n, v in a.items() if "null" not in n.lower() and v[0] is not None and v[1] is not None and not va.same(v[0], v[1])}


moves = {}
detail = {}
for f in sorted((WORK / "cross").glob("*.json")):
    d = json.load(open(f))
    a, b = d["a"], d["b"]
    if d["status"] != "ran":
        detail[(a, b)] = {"status": d["status"]}
        moves[(a, b)] = False
        continue
    arms = arms_of(d["runs"])
    rcs = [r["rc"] for r in d["runs"].values()]
    bm = own_moved(b)
    hit = sorted(n for n in bm if n in arms and arms[n][0] is not None and arms[n][1] is not None and not va.same(*arms[n]))
    null_moved = sorted(n for n, v in arms.items() if "null" in n.lower() and v[0] is not None and v[1] is not None and not va.same(*v))
    if not bm:  # B's own probe reports a count of moved inputs rather than arm pairs: read that count
        lines = [l for r in d["runs"].values() for l in res(r["stdout"])]
        own = ana.get(b, {}).get("moved_lines", [])
        cnt = [l for l in lines if re.search(r"(^|_)(moved|differ\w*|changed|diff\w*)\w*=\s*[1-9]", l) and "null" not in l.lower()]
        nl = [l for l in lines if l.lower().startswith("null") and re.search(r"=\s*[1-9]", l) and ("moved" in l or "delta" in l or "diff" in l)]
        if own:
            hit, null_moved = cnt, nl
            arms = {l.split("=")[0]: ["0", l.split("=", 1)[1]] for l in cnt}
            bm = set(own)
    moves[(a, b)] = bool(hit) and not null_moved and all(rc == 0 for rc in rcs)
    detail[(a, b)] = {"status": "ran", "rc": rcs, "b_moved": len(bm), "hit": hit[:3], "n_hit": len(hit),
                      "null_moved": null_moved[:2], "example": (hit[0], arms.get(hit[0])) if hit else None}

by_site = collections.defaultdict(list)
for m in master:
    by_site[m["site"]].append(m["key"])
merged, canon = [], []
for site, ks in by_site.items():
    if len(ks) < 2:
        canon += ks
        continue
    left = sorted(ks, key=order.get)
    while left:
        best = max(left, key=lambda a: (sum(moves.get((a, b), False) for b in left if b != a), -order[a]))
        canon.append(best)
        took = [b for b in left if b != best and moves.get((best, b), False)]
        for b in took:
            dd = detail[(best, b)]
            merged.append({"id": f"D3-wave-{b}", "into": f"D3-wave-{best}", "site": site,
                           "number": f"probe_{b} run with {best}'s mutant: {dd['n_hit']} of {dd['b_moved']} of its own moved arm pairs move, e.g. {dd['example']}; null pairs held"})
        left = [k for k in left if k != best and k not in took]
out = {"canonical": [f"D3-wave-{k}" for k in sorted(canon, key=order.get)], "merged": merged,
       "pairs": [{"a": a, "b": b, "moves": moves[(a, b)], **detail[(a, b)]} for (a, b) in sorted(detail)]}
json.dump(out, open(WORK / "dedup.json", "w"), indent=1)
st = collections.Counter(d["status"] if d["status"] != "ran" else ("moves" if moves[p] else "no-move") for p, d in detail.items())
print("pairs", len(detail), dict(st), "canonical", len(canon), "merged", len(merged))
