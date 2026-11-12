#!/usr/bin/env python3
"""Rows for the main-push side of the census: one row per red job per ci.yml
push run in runs_red4.json. A run with no red job yields no row (null control).
    python3 -I dev/audit/rounds/round10/protection-census/main_reds.py
"""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[3] / "harnesses/r10_rca_ci_critpath_3/runs_red4.json"
for r in json.load(open(p))["workflow_runs"]:
    for j in r["jobs"]:
        if j["conclusion"] == "failure":
            print(r["run_number"], r["head_sha"][:9], r["conclusion"], j["name"], sep="\t")
