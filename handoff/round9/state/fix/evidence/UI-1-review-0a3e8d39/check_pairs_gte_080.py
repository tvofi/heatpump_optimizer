#!/usr/bin/env python3
import json
import subprocess

def get_closures_at(ref):
    output = subprocess.check_output(
        ["git", "show", f"{ref}:tests/closures.json"],
        cwd="/tmp/claude-0/rev", text=True
    )
    return json.loads(output)["closures"]

def compute_prod_files(closures):
    prod = {
        f for _fs in closures.values() for f in _fs
        if f.startswith("custom_components/heatpump_optimizer/")
    }
    return prod

def d308_pairs(closures, prod, floor=0.80):
    names = sorted(closures)
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
    return out

for ref in ["aac8fb77", "HEAD"]:
    cl = get_closures_at(ref)
    pr = compute_prod_files(cl)
    pairs = d308_pairs(cl, pr, floor=0.80)
    
    print(f"\n=== {ref}: pairs >= 0.80 ({len(pairs)} total) ===")
    
    # Show pairs with doc_claims
    doc_claims_pairs = [(j, s1, s2, sh) for j, s1, s2, sh in pairs if "doc_claims" in s1 or "doc_claims" in s2]
    if doc_claims_pairs:
        print(f"Pairs with doc_claims ({len(doc_claims_pairs)}):")
        for jac, s1, s2, shared in sorted(doc_claims_pairs):
            print(f"  {s1.split('/')[-1]} / {s2.split('/')[-1]}: {jac:.4f} ({shared})")
    else:
        print("No pairs with doc_claims")

