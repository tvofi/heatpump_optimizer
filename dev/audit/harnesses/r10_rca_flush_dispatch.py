#!/usr/bin/env python3
"""R10-RCA-FLUSH-DISPATCH: what a workflow_dispatch of nightly.yml cost.

For each Nightly run, the jobs API (`actions/runs/<id>/jobs`, latest attempt)
gives each job's started_at and completed_at. A run's runner-minutes is the sum
of completed-minus-started over its jobs, so a cancelled job counts to its
cancel. `lost` is the runner-minutes of `mutation-ledger` shards that concluded
`success` in a run whose `mutation-ledger-push` did not: finished ledger work
that never landed.

    python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs <id>...
    python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py since <iso> [event]

`since` lists nightly.yml runs created at or after <iso> (event default
workflow_dispatch). GH_TOKEN is read if set; the repository is public, so
reads also work without it. Read-only: it makes GET requests only.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

API = "https://api.github.com/repos/tvofi/heatpump_optimizer"


def get(url):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)


def minutes(job):
    if not job.get("started_at") or not job.get("completed_at"):
        return 0.0
    t = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return max(0.0, (t(job["completed_at"]) - t(job["started_at"])).total_seconds() / 60)


def lane(job):
    return job["name"].split(" (")[0]


def measure(run_id):
    run = get(f"{API}/actions/runs/{run_id}")
    jobs, page = [], 1
    while True:
        body = get(f"{API}/actions/runs/{run_id}/jobs?per_page=100&page={page}&filter=latest")
        jobs += body["jobs"]
        if len(jobs) >= body["total_count"] or not body["jobs"]:
            break
        page += 1
    per = {}
    for j in jobs:
        per[lane(j)] = per.get(lane(j), 0.0) + minutes(j)
    push = [j["conclusion"] for j in jobs if lane(j) == "mutation-ledger-push"]
    shards = [j for j in jobs if lane(j) == "mutation-ledger"]
    landed = push == ["success"]
    lost = 0.0 if landed else sum(minutes(j) for j in shards if j["conclusion"] == "success")
    return {
        "id": run_id, "event": run["event"], "created": run["created_at"],
        "conclusion": run["conclusion"], "sha": run["head_sha"][:8],
        "total": sum(per.values()), "record": per.get("record-autofix", 0.0),
        "shards_ok": sum(j["conclusion"] == "success" for j in shards),
        "push": ",".join(str(p) for p in push) or "-", "lost": lost, "lanes": per,
    }


def since(iso, event="workflow_dispatch"):
    q = urllib.parse.urlencode({"event": event, "created": f">={iso}", "per_page": 100})
    return [r["id"] for r in get(f"{API}/actions/workflows/nightly.yml/runs?{q}")["workflow_runs"]]


def main(argv):
    if len(argv) < 2 or argv[0] not in ("runs", "since"):
        print(__doc__)
        return 2
    ids = argv[1:] if argv[0] == "runs" else since(*argv[1:3])
    rows = [measure(i) for i in ids]
    for r in rows:
        print(f"{r['id']} {r['event']} {r['created']} {r['conclusion']} {r['sha']} "
              f"total={r['total']:.0f} record-autofix={r['record']:.0f} "
              f"shards_ok={r['shards_ok']} ledger-push={r['push']} lost={r['lost']:.0f}")
    tot = sum(r["total"] for r in rows)
    print(f"RESULT runs={len(rows)} runner_min={tot:.0f} "
          f"record_autofix_min={sum(r['record'] for r in rows):.0f} "
          f"cancelled={sum(r['conclusion'] == 'cancelled' for r in rows)} "
          f"lost_ledger_min={sum(r['lost'] for r in rows):.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
