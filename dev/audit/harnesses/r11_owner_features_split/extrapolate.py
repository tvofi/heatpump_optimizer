"""C2 extrapolation from the clean sample: per-rule mean CPU-s per row times the rule's row count."""
import json, sys
from collections import Counter
R = [json.loads(l) for l in open(sys.argv[1])]
N = {1: int(sys.argv[2]), 2: int(sys.argv[3])}
tot = 0
print("rows", len(R), dict(Counter((r["rule"], r["killed"]) for r in R)))
for k in (1, 2):
    s = [r for r in R if r["rule"] == k]
    c = [sum(d["cpu_s"] for d in r["drives"]) for r in s]
    m = sum(c) / len(s)
    tot += m * N[k]
    print(f"rule {k}: sampled {len(s)}, killed {sum(r['killed'] for r in s)}, first candidate killed {sum(r['drives'][0]['killed'] for r in s)}, "
          f"drives/row {sum(len(r['drives']) for r in s)/len(s):.2f}, CPU-s/row mean {m:.0f} min {min(c):.0f} max {max(c):.0f}, "
          f"x {N[k]} rows = {m*N[k]:.0f}")
print(f"extrapolated rules 1+2: {tot:.0f} CPU-s; sample measured {sum(d['cpu_s'] for r in R for d in r['drives']):.0f} CPU-s")
