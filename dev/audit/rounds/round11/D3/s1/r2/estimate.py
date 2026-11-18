"""Estimate fast-net cost of every not-yet-driven unpinned site (resume planning).

Run from the seat worktree root: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/r2/estimate.py
"""
import sys
from collections import Counter

sys.path.insert(0, "dev/audit/rounds/round11/D3/s1")
import prescreen as p  # noqa: E402

mt = p.mt
base = p.load_base()
done = set()
for sub in ("pre", "c2", "c3c6", "u1"):
    d = p.RESULTS / sub
    if d.exists():
        done |= {x.stem for x in d.glob("*.json")}
pool = [m for m in p.unpinned() if p.key(m) not in done]
tot = 0.0
per = Counter()
zero = 0
for m in pool:
    c = 0.0
    for s in base:
        if m["file"] not in mt.load_closures().get(s, ()):
            continue
        if not p.fast(s):
            continue
        if mt.reach_skip(base[s]["reach"], m):
            continue
        if p.relaxed_skip(base[s].get("capture_reach") or base[s]["reach"], m):
            continue
        c += base[s]["run"]["seconds"]
        per[s] += 1
    tot += c
    zero += (c == 0)
print("remaining", len(pool), "unique_keys", len({p.key(m) for m in pool}),
      "zero-cost", zero, "est_serial_hours", round(tot / 3600, 1))
for s, n in per.most_common():
    print(" ", s, n, base[s]["run"]["seconds"])
