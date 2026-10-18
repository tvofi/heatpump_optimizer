"""Item 1 cost: how long a verdict run's prelude would wait under revision 1.

    python3 -I measure/rev/verdict_wait.py measure/p2/raw > measure/rev/verdict_wait.txt

Revision 1 puts verdict events (a body edit, a review) in run-id concurrency
groups, so no verdict run ever replaces a pending code run, and its prelude waits
until every EARLIER ci.yml run at the same head has completed. Replayed over the
22 saved heads (raw/runsat_<sha>.json = GET actions/runs?head_sha=<sha>):
  a verdict event = a `PR contract` pull_request run that is not the head's first
  (an `edited`), or a `Budget raise gate` pull_request_review run;
  an earlier code run = any Tests/CodeQL/Governance/Hassfest/Validate run at the
  head created at or before the verdict (pull_request or workflow_dispatch),
  standing in for the one ci.yml run that would carry them.
WAIT = max(0, the newest such run's updated_at - the verdict's created_at): the
runner-seconds the prelude holds while it polls. GROUPED is the same with
revision 1's verdict groups (`CI-edit-<pr>`, `CI-review-<pr>`, cancel-in-progress):
a newer verdict of the same type at the head cancels the waiting one, so its wait
ends at the newer one's creation. Prints per event and totals.
"""
import json, statistics, sys
from datetime import datetime
from pathlib import Path

CODE = {"Tests", "CodeQL", "Governance", "Hassfest", "Validate"}
def t(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp()
raw = Path(sys.argv[1]); waits = []
for f in sorted(raw.glob("runsat_*.json")):
    runs = sorted(json.loads(f.read_text())["workflow_runs"], key=lambda r: (r["created_at"], r["id"]))
    pc = [r for r in runs if r["name"] == "PR contract" and r["event"] == "pull_request"]
    verdicts = [("edited", r) for r in pc[1:]] + \
               [("review", r) for r in runs if r["name"] == "Budget raise gate" and r["event"] == "pull_request_review"]
    vs = sorted(verdicts, key=lambda x: x[1]["created_at"])
    for i, (kind, v) in enumerate(vs):
        code = [r for r in runs if r["name"] in CODE and r["event"] in ("pull_request", "workflow_dispatch")
                and t(r["created_at"]) <= t(v["created_at"])]
        w = max([0.0] + [t(r["updated_at"]) - t(v["created_at"]) for r in code])
        nxt = [t(o["created_at"]) for k2, o in vs[i + 1:] if k2 == kind]
        g = min([w] + [n - t(v["created_at"]) for n in nxt])
        waits.append((kind, w, g))
        print(f"{f.stem[7:17]} {kind:7s} created {v['created_at']}  waits {w:6.0f} s  grouped {g:6.0f} s")
nh = len(list(raw.glob("runsat_*.json")))
for col, lab in ((1, "naive  "), (2, "grouped")):
    for k in ("edited", "review", None):
        ws = sorted(x[col] for x in waits if k is None or x[0] == k)
        if ws: print(f"{lab} {k or 'all':7s} n {len(ws):2d}  wait median {statistics.median(ws):5.0f} s  max {ws[-1]:5.0f} s  "
                     f"sum {sum(ws)/3600:5.2f} runner-hours over {nh} heads; waited >0: {sum(w > 0 for w in ws)}")
