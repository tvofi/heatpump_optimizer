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

def d308_pairs_detailed(closures, prod):
    names = sorted(closures)
    out = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = set(closures[names[i]]) & prod
            b = set(closures[names[j]]) & prod
            if not a or not b:
                continue
            jac = len(a & b) / len(a | b)
            key = (names[i], names[j])
            out[key] = (jac, len(a & b))
    return out

mb = get_closures_at("aac8fb77")
head = get_closures_at("HEAD")
mb_prod = compute_prod_files(mb)
head_prod = compute_prod_files(head)

mb_pairs = d308_pairs_detailed(mb, mb_prod)
head_pairs = d308_pairs_detailed(head, head_prod)

# Find pairs that were >= 0.80 at mb but < 0.80 at head
print("=== Pairs that dropped below 0.80 ===")
for key, (jac_mb, shared_mb) in mb_pairs.items():
    if jac_mb >= 0.80:
        jac_head, shared_head = head_pairs.get(key, (None, None))
        if jac_head is None:
            print(f"{key[0].split('/')[-1]} / {key[1].split('/')[-1]}: was {jac_mb:.4f}, now missing")
        elif jac_head < 0.80:
            print(f"{key[0].split('/')[-1]} / {key[1].split('/')[-1]}: {jac_mb:.4f} → {jac_head:.4f} ({shared_mb} → {shared_head})")

# Find pairs that gained >= 0.80 at head
print("\n=== Pairs that gained >= 0.80 ===")
for key, (jac_head, shared_head) in head_pairs.items():
    if jac_head >= 0.80:
        jac_mb, shared_mb = mb_pairs.get(key, (None, None))
        if jac_mb is None:
            print(f"{key[0].split('/')[-1]} / {key[1].split('/')[-1]}: was missing, now {jac_head:.4f}")
        elif jac_mb < 0.80:
            print(f"{key[0].split('/')[-1]} / {key[1].split('/')[-1]}: {jac_mb:.4f} → {jac_head:.4f} ({shared_mb} → {shared_head})")

