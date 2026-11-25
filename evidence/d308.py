import json, subprocess, sys
W = "/Users/timmalmstrom/hpo-seats/r10s6/rev-3866-delta"
for ref in sys.argv[1:]:
    c = json.loads(subprocess.check_output(["git", "-C", W, "show", f"{ref}:tests/closures.json"]))["closures"]
    prod = {f for fs in c.values() for f in fs if f.startswith("custom_components/heatpump_optimizer/")}
    names = sorted(c)
    n = 0
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = set(c[names[i]]) & prod
            b = set(c[names[j]]) & prod
            if a and b and len(a & b) / len(a | b) >= 0.80:
                pairs.append((names[i], names[j]))
    tot = len(c) * (len(c) - 1) // 2
    ds = subprocess.check_output(["git", "-C", W, "show", f"{ref}:tests/deployment_shape.py"]).decode()
    ds = " ".join(ds.split())
    m = f"{len(pairs)} of the {tot}"
    print(ref, len(prod), m, "in note:", m in ds)
    if ref != sys.argv[1]:
        print("  new pairs vs", sys.argv[1], sorted(set(pairs) - base), "gone", sorted(base - set(pairs)))
    else:
        base = set(pairs)
