"""Spike: the optimistic floor -- every row killed inside its first reaching span (fork drive, prefix shared)."""
import json, os, sys
sys.path[:0] = ["tests", os.environ["SPIKE"], os.path.dirname(os.path.abspath(__file__))]
import case_select as cs, forkdrive
rows, spans = forkdrive.rows_for(*sys.argv[1:4]) if False else forkdrive.rows_for(sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3])
ent = cs.entry(cs.load(), "tests/features.py")["spans"]
sec = [ent.get(s.id, {}).get("seconds", 0.0) for s in spans]
head = float(os.environ.get("HEAD_S", "6.9"))
f = sum(sec[r["first"]] for r in rows if r["first"] is not None and not r["module_level"])
m = sum(head + sec[r["first"]] for r in rows if r["first"] is not None and r["module_level"])
print(f"floor CPU-s: function rows {f:.0f}, module rows {m:.0f}, total {f + m:.0f}; per row {(f + m) / len(rows):.1f}")
