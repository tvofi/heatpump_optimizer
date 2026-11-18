"""Verifier D1#1, V2 for D1-s1-51: tie-broken slot reason across hash seeds.

Metric: over PYTHONHASHSEED=0..39 and four tie shapes ([a,b], [a,a,b,b], [b,b,a,a],
[a,b,b,a]), the number of shapes whose published slot['reason'] takes more than one
value across seeds; plus the seeds (of 40) disagreeing with seed 0 on [a,a,b,b].
Null: [a,a,a,b] (no tie) must give exactly 1 value.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s1_51_tie.py [codeA codeB]
"""
import os
import subprocess
import sys

A, B = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("cheap", "preheat")
CHILD = r'''
import sys
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone
from heatpump_optimizer.plan_slots import plan_slots
out = []
for shape in sys.argv[1:]:
    r = shape.split(",")
    t0 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    ts = [t0 + timedelta(minutes=15 * i) for i in range(len(r) + 1)]
    s = plan_slots(ts, [3.0] * len(r) + [0.0], [0.5] * (len(r) + 1), 0.25, reasons=r + ["idle"])
    out.append(s[0]["reason"])
print("|".join(out))
'''
shapes = [f"{A},{B}", f"{A},{A},{B},{B}", f"{B},{B},{A},{A}", f"{A},{B},{B},{A}", f"{A},{A},{A},{B}"]
rows = []
for seed in range(40):
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    r = subprocess.run([sys.executable, "-c", CHILD, *shapes], capture_output=True, text=True, env=env, check=True)
    rows.append(r.stdout.strip().split("|"))
vals = [set(r[k] for r in rows) for k in range(len(shapes))]
for s, v in zip(shapes, vals):
    print(s, sorted(v))
print(f"RESULT tie_shapes_multivalued={sum(len(v) > 1 for v in vals[:4])} of 4")
print(f"RESULT seeds_disagree_seed0_aabb={sum(r[1] != rows[0][1] for r in rows)} of 40")
print(f"RESULT null_values={len(vals[4])}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
