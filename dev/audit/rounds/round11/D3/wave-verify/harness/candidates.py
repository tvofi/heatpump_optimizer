#!/usr/bin/env python3
"""Build the stage's candidate list from the harvested wave REPORT-D3-gNN.json files."""
import json, sys, pathlib
REC = pathlib.Path("<seat-dir>/rec")
S = REC / "dev/audit/rounds/round11/D3/s1"
boxes = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(p.stem.replace("REPORT-", "") for p in S.glob("REPORT-D3-g*.json"))
out = []
for b in boxes:
    d = json.load(open(S / f"REPORT-{b}.json"))
    for c in d.get("gate_survivors", []):
        p = c.get("probe") or {}
        path = p.get("path")
        exists = bool(path) and (REC / path).is_file()
        out.append({"box": b, "key": c["key"], "site": c.get("site"), "patch": c.get("patch"), "function": c.get("function"),
                    "cluster": c.get("cluster"), "gate_verdict": (c.get("gate") or {}).get("verdict"),
                    "gate_command": c.get("gate_command"), "probe_path": path, "probe_exists": exists,
                    "probe_command": p.get("command"), "metric": p.get("metric"),
                    "baseline_value": p.get("baseline_value"), "mutant_value": p.get("mutant_value"),
                    "probe_keys": sorted(p.keys()), "rec_keys": sorted(c.keys())})
json.dump(out, open(REC.parent / "candidates.json", "w"), indent=1)
print(len(out), "candidates;", sum(not c["probe_exists"] for c in out), "probe paths missing")
from collections import Counter
print(Counter(tuple(c["probe_keys"]) for c in out).most_common(3))
print(Counter(tuple(c["rec_keys"]) for c in out).most_common(2))
