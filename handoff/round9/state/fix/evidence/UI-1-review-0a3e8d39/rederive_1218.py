#!/usr/bin/env python3
"""
Recompute #1218 statistics from closures.json at HEAD and at merge base.
"""
import json
import subprocess
import sys
from pathlib import Path

def get_closures_at(ref):
    """Get closures.json content at a git ref."""
    try:
        output = subprocess.check_output(
            ["git", "show", f"{ref}:tests/closures.json"],
            cwd="/tmp/claude-0/rev",
            text=True
        )
        return json.loads(output)["closures"]
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def compute_prod_files(closures):
    """Compute production files in custom_components/heatpump_optimizer/"""
    prod = {
        f for _fs in closures.values() for f in _fs
        if f.startswith("custom_components/heatpump_optimizer/")
    }
    return prod

def d308_pairs(closures, prod, floor=0.80):
    """Compute pairs with >= floor Jaccard similarity."""
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

def compute_stats(closures, prod):
    """Compute all statistics."""
    pairs = d308_pairs(closures, prod, floor=0.80)
    pairs_1_00 = d308_pairs(closures, prod, floor=1.00)
    
    # Total pairs
    total = len(closures) * (len(closures) - 1) // 2
    
    # Comparable pairs (both scripts have prod files)
    comparable = total - sum(
        1 for i, a in enumerate(sorted(closures))
        for b in sorted(closures)[i + 1:]
        if not ((set(closures[a]) & prod) and (set(closures[b]) & prod))
    )
    
    # Scripts with no production closure
    empty = sorted(
        s for s, fs in closures.items() if not set(fs) & prod
    )
    
    return {
        "num_prod_files": len(prod),
        "num_scripts": len(closures),
        "num_total_pairs": total,
        "num_pairs_gte_080": len(pairs),
        "num_comparable_pairs": comparable,
        "num_pairs_exact_100": len(pairs_1_00),
        "empty_scripts": empty,
        "pairs_gte_080": pairs,
        "pairs_exact_100": pairs_1_00,
    }

def main():
    print("Computing #1218 statistics...")
    print()
    
    # Get closures at HEAD and merge base
    head_closures = get_closures_at("HEAD")
    merge_base_closures = get_closures_at("aac8fb77")
    
    if head_closures is None or merge_base_closures is None:
        print("Error: could not retrieve closures.json", file=sys.stderr)
        return 1
    
    head_prod = compute_prod_files(head_closures)
    merge_base_prod = compute_prod_files(merge_base_closures)
    
    head_stats = compute_stats(head_closures, head_prod)
    merge_base_stats = compute_stats(merge_base_closures, merge_base_prod)
    
    # Also count tracked files
    try:
        head_tracked = subprocess.check_output(
            ["git", "ls-files", "custom_components/heatpump_optimizer"],
            cwd="/tmp/claude-0/rev",
            text=True
        ).strip().split('\n')
        head_tracked_count = len([f for f in head_tracked if f])
    except:
        head_tracked_count = None
    
    # Try using git ls-tree at merge base
    try:
        merge_base_tracked_count = len(
            subprocess.check_output(
                ["git", "ls-tree", "-r", "--name-only", "aac8fb77:custom_components/heatpump_optimizer"],
                cwd="/tmp/claude-0/rev",
                text=True
            ).strip().split('\n')
        )
    except:
        merge_base_tracked_count = None
    
    print("=== HEAD (current branch) ===")
    print(f"Tracked files in custom_components/heatpump_optimizer/: {head_tracked_count}")
    print(f"Production files in closures: {head_stats['num_prod_files']}")
    print(f"Scripts in closures: {head_stats['num_scripts']}")
    print(f"Total pairs: {head_stats['num_total_pairs']}")
    print(f"Comparable pairs (both have prod files): {head_stats['num_comparable_pairs']}")
    print(f"Pairs >= 0.80 Jaccard: {head_stats['num_pairs_gte_080']}")
    print(f"Pairs exactly 1.00 Jaccard: {head_stats['num_pairs_exact_100']}")
    print(f"Empty scripts (no prod files): {head_stats['empty_scripts']}")
    print()
    
    print("Pairs at exactly 1.00:")
    for jac, s1, s2, shared in sorted(head_stats['pairs_exact_100']):
        print(f"  {s1} / {s2}: {shared} shared files")
    print()
    
    print("=== Merge Base (aac8fb77) ===")
    print(f"Tracked files in custom_components/heatpump_optimizer/: {merge_base_tracked_count}")
    print(f"Production files in closures: {merge_base_stats['num_prod_files']}")
    print(f"Scripts in closures: {merge_base_stats['num_scripts']}")
    print(f"Total pairs: {merge_base_stats['num_total_pairs']}")
    print(f"Comparable pairs (both have prod files): {merge_base_stats['num_comparable_pairs']}")
    print(f"Pairs >= 0.80 Jaccard: {merge_base_stats['num_pairs_gte_080']}")
    print(f"Pairs exactly 1.00 Jaccard: {merge_base_stats['num_pairs_exact_100']}")
    print(f"Empty scripts (no prod files): {merge_base_stats['empty_scripts']}")
    print()
    
    print("Pairs at exactly 1.00:")
    for jac, s1, s2, shared in sorted(merge_base_stats['pairs_exact_100']):
        print(f"  {s1} / {s2}: {shared} shared files")
    print()
    
    print("=== Comparison ===")
    print(f"Tracked files changed: {head_tracked_count} vs {merge_base_tracked_count}")
    print(f"Prod files in closures changed: {head_stats['num_prod_files']} vs {merge_base_stats['num_prod_files']}")
    print(f"Pairs >= 0.80 changed: {head_stats['num_pairs_gte_080']} vs {merge_base_stats['num_pairs_gte_080']}")
    print(f"Pairs exactly 1.00 changed: {head_stats['num_pairs_exact_100']} vs {merge_base_stats['num_pairs_exact_100']}")

if __name__ == "__main__":
    sys.exit(main() or 0)
