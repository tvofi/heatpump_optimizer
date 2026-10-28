# Reviewer's rebuild of the body's fig.py (not committed in the tree): groups keyed by `group`,
# a group being any object holding both `group` and `resume`.
import json, subprocess, sys, collections
def load(ref):
    d = json.loads(subprocess.check_output(["git","show",f"{ref}:dev/programme/rosters/wave-r10-groups.json"]))
    out = {}
    def walk(x):
        if isinstance(x, dict):
            if "group" in x and "resume" in x: out[x["group"]] = x
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d); return out
m, h = load(sys.argv[1]), load(sys.argv[2])
print("groups main", len(m), "head", len(h), "removed", sorted(set(m)-set(h)), "new", sorted(set(h)-set(m)))
ch = [g for g in sorted(m) if g in h and m[g] != h[g]]
print("changed", len(ch))
def stage(x):
    r = x.get("resume"); return r.get("stage") if isinstance(r, dict) else r
for g in ch:
    keys = sorted(k for k in set(m[g])|set(h[g]) if m[g].get(k) != h[g].get(k))
    parts = []
    if "carry" in keys: parts.append(f"carry {len(m[g].get('carry') or [])}->{len(h[g].get('carry') or [])}")
    if "issues" in keys: parts.append(f"issues {m[g].get('issues')}->{h[g].get('issues')}")
    if "resume" in keys: parts.append(f"stage {stage(m[g])}->{stage(h[g])}")
    print(" ", g, keys, "; ".join(parts))
for n, s in (("main", m), ("head", h)):
    print("stages", n, dict(sorted(collections.Counter(stage(x) for x in s.values()).items())))
