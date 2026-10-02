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

def check_pair_similarity(closures, prod, s1, s2):
    a = set(closures.get(s1, [])) & prod
    b = set(closures.get(s2, [])) & prod
    if not a or not b:
        return None
    union = len(a | b)
    inter = len(a & b)
    return inter / union if union else None, inter

# Test both refs
for ref in ["aac8fb77", "HEAD"]:
    cl = get_closures_at(ref)
    pr = compute_prod_files(cl)
    
    print(f"\n=== {ref} ===")
    print(f"Tracked files: {len(pr)}")
    
    # Check specific pairs from docstring
    pairs_to_check = [
        ("tests/structure.py", "tests/typing_ruler.py"),
        ("tests/finite_boundary.py", "tests/structure.py"),
        ("tests/finite_boundary.py", "tests/typing_ruler.py"),
        ("tests/plan_view.py", "tests/solar_alignment.py"),
        ("tests/optimality.py", "tests/validate.py"),
        ("tests/optimality.py", "tests/edge.py"),
        ("tests/optimality.py", "tests/backtest.py"),
        ("tests/validate.py", "tests/edge.py"),
        ("tests/validate.py", "tests/backtest.py"),
        ("tests/edge.py", "tests/backtest.py"),
        ("tests/golden.py", "tests/env_drift.py"),
        ("tests/card.mjs", "tests/card_drift.mjs"),
    ]
    
    for s1, s2 in pairs_to_check:
        sim, inter = check_pair_similarity(cl, pr, s1, s2)
        if sim is not None:
            print(f"{s1.split('/')[-1]} / {s2.split('/')[-1]}: {sim:.4f} (shared: {inter})")

