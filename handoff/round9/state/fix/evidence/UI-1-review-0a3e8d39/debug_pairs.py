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

# Check merge base
mb = get_closures_at("aac8fb77")
mb_prod = compute_prod_files(mb)
mb_pairs = d308_pairs(mb, mb_prod, floor=1.00)

print("=== Merge base: doc_claims pairs at 1.00 ===")
for jac, s1, s2, shared in mb_pairs:
    if "doc_claims" in s1 or "doc_claims" in s2:
        print(f"{s1} / {s2}: {shared}")

print("\n=== Merge base: all pairs at 1.00 (excluding doc_claims) ===")
for jac, s1, s2, shared in mb_pairs:
    if "doc_claims" not in s1 and "doc_claims" not in s2:
        print(f"{s1} / {s2}: {shared}")

# Check HEAD
head = get_closures_at("HEAD")
head_prod = compute_prod_files(head)
head_pairs = d308_pairs(head, head_prod, floor=1.00)

print("\n=== HEAD: doc_claims pairs at 1.00 ===")
for jac, s1, s2, shared in head_pairs:
    if "doc_claims" in s1 or "doc_claims" in s2:
        print(f"{s1} / {s2}: {shared}")

print("\n=== HEAD: all pairs at 1.00 (excluding doc_claims) ===")
for jac, s1, s2, shared in head_pairs:
    if "doc_claims" not in s1 and "doc_claims" not in s2:
        print(f"{s1} / {s2}: {shared}")

# Check doc_claims.py's shared count with finite_boundary, structure, typing_ruler
print("\n=== doc_claims.py at merge base ===")
mb_dc_prod = set(mb["tests/doc_claims.py"]) & mb_prod
print(f"Production files: {len(mb_dc_prod)}")
print(f"Shared with tests/finite_boundary.py: {len(mb_dc_prod & (set(mb['tests/finite_boundary.py']) & mb_prod))}")
print(f"Shared with tests/structure.py: {len(mb_dc_prod & (set(mb['tests/structure.py']) & mb_prod))}")
print(f"Shared with tests/typing_ruler.py: {len(mb_dc_prod & (set(mb['tests/typing_ruler.py']) & mb_prod))}")

print("\n=== doc_claims.py at HEAD ===")
head_dc_prod = set(head["tests/doc_claims.py"]) & head_prod
print(f"Production files: {len(head_dc_prod)}")
print(f"Shared with tests/finite_boundary.py: {len(head_dc_prod & (set(head['tests/finite_boundary.py']) & head_prod))}")
print(f"Shared with tests/structure.py: {len(head_dc_prod & (set(head['tests/structure.py']) & head_prod))}")
print(f"Shared with tests/typing_ruler.py: {len(head_dc_prod & (set(head['tests/typing_ruler.py']) & head_prod))}")

