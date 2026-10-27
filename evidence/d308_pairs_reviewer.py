#!/usr/bin/env python3
"""Reviewer's re-derivation of the #1218 selection-cost pair count.

My own instrument (fix-review, PR #2819). It reproduces tests/entities.py's
_d308_pairs rule verbatim: Jaccard over each script's closure intersected with
the production package, empty sets skipped, floor 0.80 inclusive.
Usage: python3 -I d308_pairs_reviewer.py <closures.json> [label]
"""
import json, sys

PROD_PREFIX = "custom_components/heatpump_optimizer/"

def pairs(closures, floor=0.80):
    names = sorted(closures)
    prod = {f for fs in closures.values() for f in fs if f.startswith(PROD_PREFIX)}
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = set(closures[names[i]]) & prod
            b = set(closures[names[j]]) & prod
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            if jac >= floor:
                out.append((jac, names[i], names[j], len(a & b)))
    return out, sorted(prod), names

closures = json.load(open(sys.argv[1]))["closures"]
label = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
p, prod, names = pairs(closures)
total = len(names) * (len(names) - 1) // 2
comparable = total - sum(
    1 for i, a in enumerate(names) for b in names[i+1:]
    if not ((set(closures[a]) & set(prod)) and (set(closures[b]) & set(prod))))
full = sorted(s for s, fs in closures.items() if set(prod) <= set(fs))
gp = [x for x in p if "tests/guard_pins.py" in (x[1], x[2])]
print(f"RESULT label={label}")
print(f"RESULT scripts={len(names)} total_pairs={total} prod_files={len(prod)}")
print(f"RESULT pairs_at_080={len(p)} comparable_pairs={comparable}")
print(f"RESULT full_coverage_closures={full}")
print(f"RESULT guard_pins_pairs={len(gp)}")
for jac, a, b, sh in sorted(gp):
    print(f"RESULT guard_pins_pair={a} | {b} jaccard={jac:.6f} shared={sh}")
print(f"RESULT guard_pins_closure_reaches={sorted(f for f in set(closures.get('tests/guard_pins.py', [])) if f.startswith(PROD_PREFIX))}")
