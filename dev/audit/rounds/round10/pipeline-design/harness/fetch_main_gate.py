#!/usr/bin/env python3
"""Read-only GraphQL: the `gate` check runs at each first-parent commit of main in a window."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, sys, time
REPO = PD_REPO; D = PD_DATA
log = subprocess.run(["git", "-C", REPO, "log", "--first-parent", "--format=%H %ct %s", "--since=2026-11-07T00:00:00Z", "--until=2026-11-14T10:00:00Z", "origin/main"], capture_output=True, text=True).stdout.strip().splitlines()
shas = [l.split()[0] for l in log]; out = {}
F = 'checkSuites(first:15,filterBy:{appId:15368}){nodes{conclusion status workflowRun{event databaseId runNumber workflow{name}} checkRuns(first:3,filterBy:{checkName:"gate"}){nodes{name conclusion status startedAt completedAt}}}}'
for i in range(0, len(shas), 6):
    chunk = shas[i:i+6]
    q = 'query{repository(owner:"tvofi",name:"heatpump_optimizer"){' + " ".join(f'c{j}:object(oid:"{s}"){{... on Commit{{oid {F}}}}}' for j, s in enumerate(chunk)) + "} rateLimit{remaining cost}}"
    r = subprocess.run(["gh", "api", "graphql", "-f", "query=" + q], capture_output=True, text=True)
    if r.returncode: print("FAIL", r.stderr[:300], file=sys.stderr); sys.exit(1)
    j = json.loads(r.stdout)
    for v in j["data"]["repository"].values():
        if v: out[v["oid"]] = v["checkSuites"]["nodes"]
    print(i, j["data"]["rateLimit"], file=sys.stderr); time.sleep(1)
json.dump({"log": log, "suites": out}, open(D + "main_gate.json", "w"))
