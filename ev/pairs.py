import json, subprocess, sys, itertools
def load(ref):
    return json.loads(subprocess.check_output(["git","show",f"{ref}:tests/closures.json"]))
def prod(d):
    c = d.get("closures", d)
    out = {}
    for k, v in c.items():
        files = v if isinstance(v, list) else (v.get("files") or v.get("reads") or [])
        out[k] = {f for f in files if f.startswith("custom_components/")}
    return out
def pairs(p):
    hit = set(); comp = 0
    for a, b in itertools.combinations(sorted(p), 2):
        if p[a] and p[b]:
            comp += 1
            if len(p[a] & p[b]) / len(p[a] | p[b]) >= 0.80: hit.add((a, b))
    return hit, comp
res = {}
for ref in sys.argv[1:]:
    d = load(ref); p = prod(d); h, comp = pairs(p)
    n = len(p); allp = set().union(*p.values())
    print(f"RESULT {ref[:10]} scripts={n} pairs={n*(n-1)//2} comparable={comp} at_floor={len(h)} prod_files={len(allp)} block_duty={len(p.get('tests/block_duty.py', ()))} empty={sorted(k for k in p if not p[k])}")
    res[ref] = h
a, b = sys.argv[1], sys.argv[-1]
print("joined", sorted(res[b] - res[a])); print("left", sorted(res[a] - res[b]))
