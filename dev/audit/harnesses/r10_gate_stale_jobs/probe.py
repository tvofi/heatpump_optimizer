#!/usr/bin/env python3
"""Catch a stale jobs listing live, and read the same job by the other endpoints.

A job is provably stale in a listing when the listing itself shows a job that
`needs` it already created: the orchestrator has seen its result. Each hit reads
GET /actions/jobs/<id> and the head's check run. Bounded: python3 probe.py <minutes>.
"""
import json
import subprocess
import sys
import time

R = "tvofi/heatpump_optimizer"
PAIRS = {"tests / mutation-autofix": "tests / mutation", "tests / closures-autofix": "tests / closures",
         "tests / graders-head-copy": "tests / coverage", "tests / claims-autofix": "tests / fast (3.14)",
         "tests / lane-proofs": "tests / arch-instrument", "gate": "prelude"}


def api(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 else None


end = time.time() + 60 * float(sys.argv[1])
polls = looks = hits = 0
while time.time() < end:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    doc = api(f"repos/{R}/actions/workflows/ci.yml/runs?status=in_progress&per_page=8") or {"workflow_runs": []}
    polls += 1
    for r in doc["workflow_runs"]:
        d = api(f"repos/{R}/actions/runs/{r['id']}/jobs?filter=latest&per_page=100")
        if not d:
            continue
        looks += 1
        by = {j["name"]: j for j in d["jobs"]}
        for down, up in PAIRS.items():
            u, v = by.get(up), by.get(down)
            if u and v and u["status"] != "completed":
                hits += 1
                one = api(f"repos/{R}/actions/jobs/{u['id']}") or {}
                cr = api(f"repos/{R}/check-runs/{u['id']}") or {}
                print(json.dumps({"at": now, "run": r["id"], "stale_in_listing": up, "listing": u["status"],
                                  "listing_completed_at": u["completed_at"], "downstream": down,
                                  "downstream_created": v["created_at"], "job_endpoint": one.get("status"),
                                  "job_completed_at": one.get("completed_at"), "check_run": cr.get("status"),
                                  "job": u["id"]}), flush=True)
    print(f"# {now} polls={polls} listings={looks} hits={hits}", flush=True)
    time.sleep(60)
print(f"END polls={polls} listings={looks} hits={hits}", flush=True)
