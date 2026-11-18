#!/usr/bin/env python3
"""Assemble seat D3-s3's REPORT.json (finding.schema.json) from the committed
records of the local relaunch. Source-only: runs the enumerators, reads
findings/*.json, prescreen_table.py --json, m4.json and m5_table.out.

Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
         dev/audit/rounds/round11/D3/s3/build_report_local.py
Writes dev/audit/rounds/round11/D3/s3/REPORT.json.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "dev/audit/rounds/round11/D3/s3"
PY = sys.executable
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def run(*a):
    return subprocess.run([PY, *a], capture_output=True, text=True,
                          check=True).stdout


def main() -> int:
    extra = json.loads((HERE / "report_text.json").read_text())
    uni = [ln.split("\t") for ln in run(f"{REL}/enumerate.py").splitlines() if ln]
    keys = [f"{p[1].rsplit('/', 1)[-1]}" for p in uni]          # file:line
    kinds = {}
    for p in uni:
        kinds.setdefault(p[1], []).append(p[0].split()[1])
    table = json.loads(run(f"{REL}/prescreen_table.py", "--json"))
    done = [r for r in table if r["state"] == "KILLED" or r["state"].startswith("LIVES")]
    done_keys = Counter(r["site"].split()[0] for r in done
                        if r["state"] == "KILLED" or r["state"].startswith("LIVES"))
    left = Counter()
    seen = Counter()
    for k in keys:
        seen[k] += 1
        if seen[k] > done_keys.get(k, 0):
            left[k.split(":")[0]] += 1
    m2_exam = sum(done_keys.values())
    survivors = [r["site"] for r in table if r["state"].startswith("LIVES")]
    m4all = json.loads((HERE / "m4_answers.json").read_text())
    m4 = {k: v for k, v in m4all.items() if k in survivors}
    m5 = (HERE / "m5_table.out").read_text().splitlines()
    m5_uni = [ln.split("\t")[0] for ln in run(f"{REL}/enumerate_m5.py").splitlines() if ln]
    m5_missing = [ln.split("\t")[1] for ln in m5 if ln.startswith("NOT-MEASURED")]
    red = extra["redispatched"]
    cov = [
        {"step": "D3.M1",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --weights",
         "universe": len(uni), "examined": len(uni), "not_reached": [],
         "redispatched": red["D3.M1"],
         "evidence": extra["evidence"]["D3.M1"]},
        {"step": "D3.M2",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py",
         "universe": len(uni), "examined": m2_exam,
         "not_reached": [f"{f} ({n} site(s))" for f, n in sorted(left.items())],
         "redispatched": red["D3.M2"],
         "evidence": extra["evidence"]["D3.M2"]},
        {"step": "D3.M3",
         "enumerator": f"python3 {REL}/prescreen_table.py --survivors",
         "universe": len(survivors), "examined": len(survivors),
         "not_reached": [],
         "redispatched": red["D3.M3"],
         "evidence": extra["evidence"]["D3.M3"]},
        {"step": "D3.M4",
         "enumerator": f"python3 {REL}/prescreen_table.py --survivors",
         "universe": len(survivors),
         "examined": sum(1 for s in survivors if s in m4),
         "not_reached": [s for s in survivors if s not in m4],
         "redispatched": red["D3.M4"],
         "evidence": extra["evidence"]["D3.M4"]},
        {"step": "D3.M5",
         "enumerator": f"python3 {REL}/enumerate_m5.py",
         "universe": len(m5_uni), "examined": len(m5_uni) - len(m5_missing),
         "not_reached": m5_missing,
         "redispatched": red["D3.M5"],
         "evidence": extra["evidence"]["D3.M5"]},
    ]
    findings = [json.loads(p.read_text())
                for p in sorted((HERE / "findings").glob("D3-s3-*.json"))]
    rep = {"dimension": "D3", "baseline_sha": BASE,
           "report_path": f"{REL}/REPORT.md", "exposure": "",
           "coverage": cov, "unfinished": extra["unfinished"],
           "findings": findings, "non_findings": extra["non_findings"],
           "harnesses": sorted(f"{REL}/{p.name}" for p in HERE.glob("*.py")),
           "leads": extra["leads"],
           "prescreened": table, "m4_answers": m4}
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1))
    print(f"RESULT findings={len(findings)} m2_examined={m2_exam} "
          f"survivors={len(survivors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
