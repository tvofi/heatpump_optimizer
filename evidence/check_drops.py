#!/usr/bin/env python3
"""Reviewer's own instrument for #2864: re-derive each drop's provenance class."""
import json, re, subprocess, sys

F = "dev/programme/rosters/wave-r10-groups.json"
BASE, TIP = "c8d51c464e84d36732855f21f962287d9b1405f7", "94d14569ea32889e228c54fc082c62d968f254e0"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def norm(s):
    return " ".join((s if isinstance(s, str) else json.dumps(s, sort_keys=True)).split())


cat = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def blob(rev):
    cat.stdin.write(f"{rev}:{F}\n".encode()); cat.stdin.flush()
    hdr = cat.stdout.readline().split()
    if hdr[-1] == b"missing":
        return None
    data = cat.stdout.read(int(hdr[2])); cat.stdout.read(1)
    return json.loads(data)


def groups(d):
    return {g["group"]: g for g in d["groups"]}


# first revision (topo order, oldest first) containing each group
first = {}
for rev in git("log", "--reverse", "--topo-order", "--format=%H", TIP, "--", F).split():
    d = blob(rev)
    if d is None:
        continue
    for name, g in groups(d).items():
        if name not in first:
            first[name] = (rev, {norm(c) for c in g.get("carry", [])})

main_merges = set(re.findall(r"Merge pull request #(\d+)", git("log", "origin/main", "--merges", "--format=%s", "--since=2026-08-01")))

bad = n = 0
grp = set()
rows = []
for c in git("log", "--no-merges", "--reverse", "--format=%H\t%s", f"{BASE}..{TIP}", "--", F).splitlines():
    sha, subj = c.split("\t", 1)
    if "drop" not in subj:
        continue
    before, after = groups(blob(sha + "^")), groups(blob(sha))
    removed = []
    for name in before:
        b = [norm(x) for x in before[name].get("carry", [])]
        a = [norm(x) for x in after.get(name, {}).get("carry", [])]
        for x in b:
            if b.count(x) > a.count(x) and (name, x) not in removed:
                removed.append((name, x))
    m = re.search(r"consumed by #(\d+)", subj)
    pr = m.group(1) if m else None
    for name, x in removed:
        prov = x in first[name][1]
        stage = after[name].get("resume", {}).get("stage")
        merged = pr in main_merges if pr else None
        ok = len(removed) == 1 and prov and stage == "done" and (merged if pr else True)
        rows.append((sha[:10], name, pr, prov, stage, merged, len(removed), x[:160]))
        if pr:
            n += 1; grp.add(name)
            bad += not ok
for r in rows:
    print("ROW", *r, sep="\t")
print(f"RESULT provenance-drops {n} groups {len(grp)} bad {bad}")
