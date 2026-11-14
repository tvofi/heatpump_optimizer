#!/usr/bin/env python3
"""Read-only GraphQL: createdAt/mergedAt/reviews for the PRs in merges.json, 40 per query."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, sys, time
d = PD_DATA
prs = sorted({x["pr"] for x in json.load(open(d + "merges.json")) if x["pr"] and x["kind"] != "record"})
out = {}
F = "number createdAt mergedAt additions deletions changedFiles baseRefName commits{totalCount} reviews(first:40){nodes{submittedAt state author{login}}} timelineItems(first:60,itemTypes:[READY_FOR_REVIEW_EVENT,CONVERT_TO_DRAFT_EVENT,HEAD_REF_FORCE_PUSHED_EVENT]){nodes{__typename ... on ReadyForReviewEvent{createdAt} ... on ConvertToDraftEvent{createdAt} ... on HeadRefForcePushedEvent{createdAt}}}"
for i in range(0, len(prs), 40):
    chunk = prs[i:i+40]
    q = "query{repository(owner:\"tvofi\",name:\"heatpump_optimizer\"){" + " ".join(f"p{n}:pullRequest(number:{n}){{{F}}}" for n in chunk) + "} rateLimit{remaining cost}}"
    r = subprocess.run(["gh", "api", "graphql", "-f", "query=" + q], capture_output=True, text=True)
    if r.returncode: print("FAIL", r.stderr[:300], file=sys.stderr); sys.exit(1)
    j = json.loads(r.stdout)
    for k, v in j["data"]["repository"].items():
        if v: out[v["number"]] = v
    print(i, j["data"]["rateLimit"], file=sys.stderr); time.sleep(1)
json.dump(out, open(d + "prs.json", "w"))
