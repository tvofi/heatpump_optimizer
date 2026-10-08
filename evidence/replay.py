#!/usr/bin/env python3
"""Reviewer's own replay (fix-review seat for #2057), not the finder's or the fixer's.
synth.py's population (the last N first-parent merges of a given main tip, every
PR merge that changed tests/closures.json is an edit; all ordered pairs), merged by
`git merge-file` (no driver), in three arms:
  T0     as written (json.dumps indent=1, synth.py's arm)
  NOSEC  canon + seconds removed (synth.py's 14/420 arm)
  PR     the PR head's own writer: closure.stable_seconds vs base + closure.write_closures
Usage: replay.py <git-dir> <main-tip> [N]"""
import sys, json, itertools, subprocess, tempfile, os
from pathlib import Path
WT = "/Users/timmalmstrom/hpo-seats/review-2057/wt"
sys.path.insert(0, WT + "/tests"); import closure
G, TIP = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 120
CJ = "tests/closures.json"
def git(*a): return subprocess.run(["git", "--git-dir", G, *a], capture_output=True, text=True)
def blob(c):
    r = git("show", f"{c}:{CJ}"); return r.stdout if r.returncode == 0 else None
TD = tempfile.mkdtemp()
def m3(b, o, t):
    ps = []
    for n, x in (("b", b), ("o", o), ("t", t)):
        p = os.path.join(TD, n); open(p, "w").write(x); ps.append(p)
    return subprocess.run(["git", "merge-file", "-p", "--quiet", ps[1], ps[0], ps[2]], capture_output=True).returncode != 0
def leaves(d, pre=()):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items(): out.update(leaves(v, pre + (k,)))
    elif isinstance(d, list) and all(isinstance(x, str) for x in d):
        for x in d: out[pre + ("\0", x)] = True
    else: out[pre] = json.dumps(d)
    return out
def build(lv):
    d = {}
    for k, v in lv.items():
        cur = d
        if len(k) >= 2 and k[-2] == "\0":
            for p in k[:-3]: cur = cur.setdefault(p, {})
            cur.setdefault(k[-3], []).append(k[-1])
        else:
            for p in k[:-1]: cur = cur.setdefault(p, {})
            cur[k[-1]] = json.loads(v)
    return d
def apply(base, a, b):
    L, A, B = leaves(base), leaves(a), leaves(b)
    for k in set(A) | set(B):
        if A.get(k) != B.get(k):
            if k in B: L[k] = B[k]
            else: L.pop(k, None)
    return build(L)
def nosec(d):
    d = json.loads(json.dumps(d))
    for v in d.get("recorded", {}).values():
        if isinstance(v, dict): v.pop("seconds", None)
    return d
def canon(x):
    if isinstance(x, dict): return {k: canon(x[k]) for k in sorted(x)}
    if isinstance(x, list) and all(isinstance(i, str) for i in x): return sorted(set(x))
    return x
def dumps(d): return json.dumps(d, indent=1) + "\n"
def pr_written(base, side):
    side = json.loads(json.dumps(side))
    for k, r in side.get("recorded", {}).items():
        if isinstance(r, dict) and "seconds" in r:
            r["seconds"] = closure.stable_seconds(base.get("recorded", {}).get(k, {}).get("seconds"), r["seconds"])
    out = Path(TD) / "c.json"; closure.write_closures(out, side); return out.read_text()
ms = [l.split(" ", 1) for l in git("log", "--first-parent", "--merges", "--format=%H %s", "-n", str(N), TIP).stdout.splitlines()]
eds = []
for h, s in ms:
    if not s.startswith("Merge pull request"): continue
    a, b = blob(h + "^1"), blob(h)
    if a and b and a != b: eds.append((s.split()[3], json.loads(a), json.loads(b)))
print("RESULT tip", TIP, "edits", len(eds), [e[0] for e in eds])
c = {"T0": 0, "NOSEC": 0, "PR": 0}; n = 0; rewrites = [0, 0]
for (pj, aj, bj), (pk, ak, bk) in itertools.permutations(eds, 2):
    n += 1; ours = apply(ak, aj, bj)
    c["T0"] += m3(dumps(ak), dumps(ours), dumps(bk))
    c["NOSEC"] += m3(*(dumps(canon(nosec(x))) for x in (ak, ours, bk)))
    pc = m3(pr_written(ak, ak), pr_written(ak, ours), pr_written(ak, bk)); c["PR"] += pc
    if pc: print("  PR-arm conflict: branch", pj, "main", pk)
# seconds rewrites per real edit, as written vs under the band
for p, a, b in eds:
    for k, r in b.get("recorded", {}).items():
        old = a.get("recorded", {}).get(k, {}).get("seconds"); new = r.get("seconds")
        if old is not None and new != old:
            rewrites[0] += 1; rewrites[1] += closure.stable_seconds(old, new) != old
print(f"RESULT pairs={n} T0={c['T0']} NOSEC={c['NOSEC']} PR={c['PR']} seconds_rewrites_as_written={rewrites[0]} under_band={rewrites[1]}")
