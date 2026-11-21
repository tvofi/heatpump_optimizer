import json, sys, copy
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root / "tools/ci"))
import selftest_scope as s
table = s.load_table(Path(sys.argv[2])); meas = s.load_table(Path(sys.argv[3]))
mode = sys.argv[4] if len(sys.argv) > 4 else "none"
if mode == "drop-file":   # remove one regret-oracle file read
    e = table["steps"]["regret-oracle"]; e["files"] = [f for f in e["files"] if not f.endswith("room_record.py")]
elif mode == "drop-dir":  # remove one prepr round11 dir
    e = table["steps"]["prepr"]; e["dirs"] = [d for d in e["dirs"] if d != "dev/audit/rounds/round11/D0/s3/race_out"]
elif mode == "drop-probe":
    e = table["steps"]["temp-or-machine-path"]; e["probes"] = [p for p in e.get("probes", []) if "room_record.py" not in p]
measured = {k: {"files": v.get("files", []), "probes": v.get("probes", []), "dirs": v.get("dirs", []),
                "index": v.get("index", False), "objects": v.get("objects", False), "run_sha": v.get("run_sha")}
            for k, v in meas["steps"].items()}
refuse, notes = s.drift(table, measured, s.workflow_steps(root))
for r in refuse: print(" ", r)
print(f"mode={mode} refusals={len(refuse)}")
sys.exit(1 if refuse else 0)
