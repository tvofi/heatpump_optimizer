"""Per measured head: workflow runs by workflow and event, and check rows.

    python3 -I measure/heads.py measure/raw > measure/heads.txt

raw/runsat_<sha>.json = GET actions/runs?head_sha=<sha>. Shows how many separate
workflow runs one head costs today (the umbrella makes the PR-event ones one run
per event), and how many extra runs body edits and reviews add (the runs of the
body readers beyond each head's first: edited / pull_request_review events).
"""
import json, sys, statistics
from collections import Counter
from pathlib import Path

raw = Path(sys.argv[1]); per_head = []; extra = Counter(); events = Counter(); distinct = []
for f in sorted(raw.glob("runsat_*.json")):
    runs = json.loads(f.read_text())["workflow_runs"]
    c = Counter((r["name"], r["event"]) for r in runs)
    per_head.append(len(runs)); events.update(r["event"] for r in runs)
    for (n, e), k in c.items():
        if e in ("pull_request", "pull_request_review") and k > 1: extra[(n, e)] += k - 1
    checks = json.loads((raw / f"checks_{f.stem[7:]}.json").read_text())["check_runs"]
    distinct.append(len({x["name"] for x in checks}))
print(f"heads {len(per_head)}; workflow runs per head: median {statistics.median(per_head)}, max {max(per_head)}")
print(f"distinct check names per head: median {statistics.median(distinct)}, max {max(distinct)}")
print("runs by event, all heads:", dict(events))
print("extra runs beyond one per head (same workflow, same event):")
for (n, e), k in sorted(extra.items()): print(f"  {n:28s} {e:20s} {k}")
