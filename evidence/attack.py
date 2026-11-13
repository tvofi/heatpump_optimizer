import json, sys
sys.path.insert(0, "tools/ci")
from prelude import judging, prior_jobs
from gate import busy
d = json.load(open("tools/ci/fixtures/gate_requeued_needs_runs.json"))
def lst(a): return {j["name"]: (j["status"], j["conclusion"]) for j in a}
a1 = lst(d["attempts"]["1"]); a2 = lst(d["attempts"]["1"])
# attack: attempt 1 tests / mutation FAILED, gate failed; user clicks "re-run failed jobs":
a1["tests / mutation"] = ("completed", "failure"); a1["gate"] = ("completed", "failure")
a2["tests / mutation"] = ("queued", None); a2["gate"] = ("queued", None)
run = {"id": 1, "title": d["run"]["display_title"], "status": "in_progress", "jobs": a2, "starts": {}}
reads = []
def get(p, params=None): reads.append(p); return 200, {}, {"jobs": [{"name": k, "status": v[0], "conclusion": v[1]} for k, v in a1.items()]}
run["prior"] = prior_jobs(get, "o/r", run, 2)
ctx = {"run_id": 2}
print("RESULT attack: failed-unit re-run (tests / mutation queued in attempt 2, failure in attempt 1): judging=%s busy=%s reads=%d" % (judging(run), busy(ctx, [run]), len(reads)))
run2 = dict(run); run2.pop("prior")
print("RESULT attack-control (no prior, base behaviour): judging=%s busy=%s" % (judging(run2), busy(ctx, [run2])))
