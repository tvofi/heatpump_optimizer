"""Spike: phase C's floor -- each row killed inside its cheapest reaching part's first reaching span."""
import json
import os
import sys

sys.path[:0] = ["tests", os.environ["SPIKE"], os.path.dirname(os.path.abspath(__file__))]
import case_select as cs  # noqa: E402
import forkdrive  # noqa: E402

parts = json.load(open(sys.argv[2]))
rows, spans = forkdrive.rows_for(sys.argv[1], parts, sys.argv[3])
ent = cs.entry(cs.load(), "tests/features.py")["spans"]
sec = {s.id: ent.get(s.id, {}).get("seconds", 0.0) for s in spans}
order = {s.id: i for i, s in enumerate(spans)}
head = float(os.environ.get("HEAD_S", "6.9"))
tot = 0.0
for r in rows:
    if not r["reach"]:
        continue
    best = min(sec[min((s for s in r["reach"] if parts.get(s) == x and s in order), key=order.get)]
               for x in r["reach_parts"])
    tot += best + (head if r["module_level"] else 0)
print(f"phase C floor CPU-s {tot:.0f} over {len(rows)} rows")
