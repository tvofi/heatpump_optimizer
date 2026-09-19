#!/usr/bin/env python3
"""D3 round 5 -- test-suite resource use: closure overlap, over-approximation,
assertions-per-run, from the committed measurements only.

Metric (one line): per gate script, the recorded closure size, the recorded
seconds, the assertions it makes, and its overlap (Jaccard on closure) with
every other script -- all read from tests/closures.json + the scripts' own
text, no wall clock.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub \
        python3 tools/audit/round5/D3/resource_r5.py

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB.

Every number here is a COUNT or a RATIO derived from committed text, so it is
contention-immune: nothing is timed and nothing solves.
"""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))

raw = json.loads((ROOT / "tests" / "closures.json").read_text())
closures = raw["closures"]
recorded = raw["recorded"]

rows = []
for script, files in closures.items():
    secs = recorded.get(script, {}).get("seconds", 0.0)
    src = (ROOT / script)
    text = src.read_text() if src.exists() else ""
    asserts = len(re.findall(r"\bassert\b", text))
    checks = len(re.findall(r"\bcheck\s*\(|\.check\(", text))
    rows.append({"script": script, "closure": len(set(files)),
                 "seconds": secs, "asserts": asserts, "checks": checks})

rows.sort(key=lambda r: -r["closure"])
print("script                          closure  seconds  assert  check")
for r in rows:
    print("%-30s %7d %8.1f %7d %6d"
          % (r["script"], r["closure"], r["seconds"], r["asserts"], r["checks"]))

# Over-approximation: a script whose closure counts every production module.
prod = {f for f in {f for fs in closures.values() for f in fs}
        if f.startswith("custom_components/heatpump_optimizer/")}
n_prod = len(prod)
print("\nRESULT production_modules_total=%d count" % n_prod)
for r in rows:
    fs = set(closures[r["script"]])
    frac = len(fs & prod) / n_prod if n_prod else 0
    if frac >= 0.9:
        print("  OVER-APPROX %-28s reaches %d/%d production modules (%.0f%%)"
              % (r["script"], len(fs & prod), n_prod, 100 * frac))

# Pairwise overlap: scripts that cover nearly the same production modules.
def prodset(s):
    return set(closures[s]) & prod

pairs = []
names = [r["script"] for r in rows]
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = prodset(names[i]), prodset(names[j])
        if not a or not b:
            continue
        jac = len(a & b) / len(a | b)
        if jac >= 0.8:
            pairs.append((jac, names[i], names[j], len(a & b)))
pairs.sort(reverse=True)
print("\n  duplicate-coverage pairs (Jaccard on production modules >= 0.80):")
for jac, a, b, n in pairs[:25]:
    print("    %.2f  %-26s %-26s shared=%d" % (jac, a, b, n))

print("\nRESULT scripts_total=%d count" % len(rows))
print("RESULT duplicate_pairs_ge_0.80=%d count" % len(pairs))
print("RESULT thread_factor=1.00 ratio")
import os
print("RESULT load1=%.2f ratio" % os.getloadavg()[0])
