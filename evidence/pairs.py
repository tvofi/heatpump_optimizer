"""Re-derive tests/entities.py's #1218 pair count from a closures.json read on stdin."""
import json, sys
c = json.load(sys.stdin)["closures"]
prod = {f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
n = sorted(c); p = 0; comp = 0
for i in range(len(n)):
    for j in range(i + 1, len(n)):
        a = set(c[n[i]]) & prod; b = set(c[n[j]]) & prod
        if not a or not b: continue
        comp += 1
        if len(a & b) / len(a | b) >= 0.80: p += 1
print(f"prod={len(prod)} scripts={len(n)} pairs>=0.80={p} of {len(n)*(len(n)-1)//2} comparable={comp}")
