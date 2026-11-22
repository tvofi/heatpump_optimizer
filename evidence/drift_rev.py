# Reviewer-built replay (not the finder's): selftest_scope.drift(table, measured, workflow_steps)
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
table = s.load_table(Path(sys.argv[2])); meas = s.load_table(Path(sys.argv[3]))
mode = sys.argv[4] if len(sys.argv) > 4 else "none"
R11 = "dev/programme/rosters/wave-r11-groups.json"
def drop(step, key, pred):
    e = table["steps"][step]; e[key] = [x for x in e.get(key, []) if not pred(x)]
if mode == "drop-verdict-bus":   drop("verdict-bus", "files", lambda x: x == R11)
elif mode == "drop-ci-predictor": drop("ci-predictor", "files", lambda x: x == R11)
elif mode == "drop-regret-oracle": drop("regret-oracle", "files", lambda x: x.endswith("room_record.py"))
measured = {k: {"files": v.get("files", []), "probes": v.get("probes", []), "dirs": v.get("dirs", []),
                "index": v.get("index", False), "objects": v.get("objects", False), "run_sha": v.get("run_sha")}
            for k, v in meas["steps"].items()}
refuse, notes = s.drift(table, measured, s.workflow_steps(root))
for r in refuse: print(" ", r)
print(f"mode={mode} refusals={len(refuse)}")
sys.exit(1 if refuse else 0)
