#!/usr/bin/env python3
"""D11.M2 (Scorecard Branch-Protection / required status checks): merges admitted
while the head's own `gate` evaluation, as the repository's production reader
judges it, was not green.

Metric (one line): count of the window's merged pull requests whose merged head,
at `merged_at`, `tools/audit/seat/merge_train.py:platform_gate` reads as not
`green` over the latest `gate` check run of every check suite at that head.

Population: round 11's window (first-parent merges v10.0.0..baseline), the PR set
from `/commits/<sha>/pulls` (api/window.json); gate runs from
`/commits/<head>/check-runs?filter=all&check_name=gate` with their check-suite id
(api/gate_runs.json, fetched by `fetch_window.py --gates`).
Key: the conclusion GitHub delivered for each suite's latest gate run completed
at or before merged_at; a run started before and completed after merged_at is
IN_PROGRESS at the merge.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D11/s2/gate_at_merge.py [--perturb]
       --perturb adds FAILURE to merge_train.PLATFORM_PASS (the reader accepts a red
       gate run): the count must go to 0 for `red` heads.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7): RESULT
merged_not_green as printed, exact (fixed snapshot); counts only.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = ["tools/audit/seat"]
import merge_train  # noqa: E402


def payload_at(runs, head, at):
    latest = {}
    for r in runs:
        if not r["started_at"] or r["started_at"] > at:
            continue
        done = r["completed_at"] and r["completed_at"] <= at
        key = r["suite"]
        stamp = r["started_at"]
        if key not in latest or stamp > latest[key][0]:
            latest[key] = (stamp, r, done)
    nodes = []
    for _, r, done in latest.values():
        nodes.append({"__typename": "CheckRun", "name": merge_train.GATE, "isRequired": True,
                      "status": "COMPLETED" if done else "IN_PROGRESS",
                      "conclusion": (r["conclusion"] or "").upper() if done else None})
    return {"data": {"repository": {"pullRequest": {"commits": {"nodes": [{"commit": {
        "oid": head, "statusCheckRollup": {"contexts": {"nodes": nodes, "pageInfo": {"hasNextPage": False}}}}}]}}}}}


def main(argv):
    w = json.load(open(os.path.join(HERE, "api", "window.json")))
    g = json.load(open(os.path.join(HERE, "api", "gate_runs.json")))
    if "--perturb" in argv:
        merge_train.PLATFORM_PASS = merge_train.PLATFORM_PASS + ("FAILURE",)
    t0, c0 = time.process_time(), time.thread_time()
    bad = []
    states = {}
    for n, p in sorted(w["prs"].items(), key=lambda kv: int(kv[0])):
        head, at = p["pull"]["head_sha"], p["pull"]["merged_at"]
        st, why = merge_train.platform_gate(payload_at(g[n], head, at), head)
        states[st] = states.get(st, 0) + 1
        if st != "green":
            bad.append((int(n), st, why, p["pull"]["merged_by"]))
    for n, st, why, by in bad:
        print(f"#{n}\t{st}\t{why}\tmerged_by={by}")
    print(f"RESULT window_prs={len(w['prs'])} count")
    for k in ("green", "red", "wait", "unread"):
        print(f"RESULT platform_gate_{k}={states.get(k, 0)} count")
    print(f"RESULT merged_not_green={len(bad)} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
