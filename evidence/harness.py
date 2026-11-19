# Finder's harness: CI's drift() over the red run's measured artifact, against a given table.
import json, sys
sys.path.insert(0, "tools/ci")
import selftest_scope as s
table = json.load(open(sys.argv[1]))
art = json.load(open(sys.argv[2]))
measured = art.get("steps", art) if isinstance(art, dict) else art
steps = s.workflow_steps()
out = s.drift(table, measured, steps)
for part in out:
    for l in part: print(l)
print("UNDER-SCOPED:", sum(1 for p in out for l in p if "UNDER-SCOPED" in l))
