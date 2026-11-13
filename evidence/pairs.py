# The #1218 rule (tests/entities.py _d308_pairs: Jaccard >= 0.80 over each
# closure's custom_components/heatpump_optimizer/ files), over `git show <ref>:tests/closures.json`.
import json, subprocess, sys
def load(ref):
    return json.loads(subprocess.check_output(["git", "show", f"{ref}:tests/closures.json"]))["closures"]
def pairs(c):
    prod = {f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    n = sorted(c); out = set(); comp = 0
    for i in range(len(n)):
        for j in range(i + 1, len(n)):
            a, b = set(c[n[i]]) & prod, set(c[n[j]]) & prod
            if not a or not b: continue
            comp += 1
            if len(a & b) / len(a | b) >= 0.80: out.add((n[i], n[j]))
    total = len(c) * (len(c) - 1) // 2
    bd = len(set(c.get("tests/block_duty.py", [])) & prod)
    return out, total, comp, len(prod), bd
res = {}
for ref in sys.argv[1:]:
    p, t, comp, nprod, bd = pairs(load(ref)); res[ref] = p
    print(f"RESULT {ref} at_floor={len(p)} of {t} comparable={comp} prod_files={nprod} block_duty={bd}")
a, b = sys.argv[1], sys.argv[-1]
print("joined", sorted(res[b] - res[a])); print("left", sorted(res[a] - res[b]))
