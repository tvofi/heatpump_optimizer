#!/usr/bin/env python3
"""Upsert one finding (JSON file argument) into findings.json, findings/<id>.json and
REPORT.json's findings, then copy REPORT.json to the local-reports copy."""
import json
import shutil
import sys
from pathlib import Path

S1 = Path(__file__).resolve().parent.parent
LOCAL = Path("/Users/timmalmstrom/hpo-orch/r10s6/r11/local-reports/D3-s1.REPORT.json")
f = json.loads(Path(sys.argv[1]).read_text())
(S1 / "findings").mkdir(exist_ok=True)
(S1 / "findings" / (f["id"] + ".json")).write_text(json.dumps(f, indent=1) + "\n")
for name in ("findings.json",):
    p = S1 / name
    fs = json.loads(p.read_text())
    fs = [x for x in fs if x["id"] != f["id"]] + [f]
    fs.sort(key=lambda x: x["id"])
    p.write_text(json.dumps(fs, indent=1) + "\n")
r = json.loads((S1 / "REPORT.json").read_text())
r["findings"] = sorted([x for x in r["findings"] if x["id"] != f["id"]] + [f], key=lambda x: x["id"])
(S1 / "REPORT.json").write_text(json.dumps(r, indent=1) + "\n")
shutil.copy(S1 / "REPORT.json", LOCAL)
print("ok", f["id"], len(r["findings"]))
