"""Reviewer's own reader (not the finder's): the carries of four groups in the round-10 roster at a ref."""
import json, subprocess, sys, re
ref = sys.argv[1]
raw = subprocess.check_output(["git", "show", f"{ref}:dev/programme/rosters/wave-r10-groups.json"])
d = json.loads(raw)
groups = d["groups"] if isinstance(d, dict) and "groups" in d else d
print("ref", ref, "groups", len(groups), "top keys", list(d.keys()) if isinstance(d, dict) else "list")
by = {g.get("group"): g for g in groups}
def txt(c):
    return c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
want = {"R11-PRE-ROUND-METRICS": [0, 1], "R11-PRE-TOKEN-LEDGER": [1], "R11-INTAKE-R10-RESIDUE": [114, 115, 173, 174, 175], "R10-D5-D6-FULL-SCOPE": [2, 3], "R11-PRE-OBJECTIVE-FUNCTION": None}
for gid, idx in want.items():
    g = by.get(gid)
    if g is None:
        print("MISSING GROUP", gid); continue
    cs = g.get("carry") or []
    print(f"\n== {gid} stage={(g.get('resume') or {}).get('stage')} files={len(g.get('files') or [])} carries={len(cs)}")
    for i in (idx if idx is not None else range(len(cs))):
        if i < len(cs):
            print(f"-- carry {i}: {txt(cs[i])}")
        else:
            print(f"-- carry {i}: ABSENT")
print("\n== every carry in the roster naming 0017 or 0018")
for g in groups:
    gid = g.get("group")
    for i, c in enumerate(g.get("carry") or []):
        t = txt(c)
        for n in ("0017", "0018"):
            if n in t:
                ctx = [t[max(0, m.start()-60):m.end()+70].replace("\n", " ") for m in re.finditer(n, t)]
                print(f"{gid} [{(g.get('resume') or {}).get('stage')}] carry {i} {n} x{len(ctx)}: {ctx[0]}")
    b = g.get("brief") or ""
    for n in ("0017", "0018"):
        if n in b:
            print(f"{gid} [{(g.get('resume') or {}).get('stage')}] BRIEF mentions {n}")
