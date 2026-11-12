#!/usr/bin/env python3
"""R10-GATE-DEFER-BARRIER: the finder's harness for two readers of a deferral gate red.

    python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py [--tree DIR]

DIR is a tree root holding tools/audit/seat/ (merge_train.py, gh_read.py) and tools/ci/gate.py (default:
this tree). To measure a baseline, export it first:

    git archive <sha> tools/audit/seat tools/ci | tar -x -C "$D" && python3 -I ... --tree "$D"

Arms, each driving the tree's own Train with a fake `gh` (no network):
  policy   #3264's review instance: the rollup holds a passing `gate` (a CI review
           run's) and a failing `gate` (the edit run's deferral). policy_refusal
           must be a wait (second field True), not the park "the missing requirement
           is a review". Null: a rollup of the passing gate alone is the park as before.
  under    #3398's shape: a deferral red whose code run is in_progress, started and
           inside its deadline, outlives `polls`; wait_ci must return [] once the run
           ends, not ["TIMEOUT"]. Null: a QUEUED run keeps the polls bound (TIMEOUT).
A line `DEFECT <arm>` is printed per arm that reads the defect, then RESULT lines;
the exit code is 1 when any DEFECT stands, 0 otherwise.
"""
import argparse
import datetime
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def load(tree: Path):
    seat = tree / "tools/audit/seat"
    sys.path.insert(0, str(seat))
    spec = importlib.util.spec_from_file_location("mt_under_test", str(seat / "merge_train.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mt_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def policy(mt, rollup):
    H, NOW = "b" * 40, 1_000_000.0

    def run(argv, cwd=None, stdin=None):
        a = " ".join(argv)
        if "actions/runs?event=pull_request_review" in a:
            return 0, ""
        if "statusCheckRollup" in a:
            return 0, json.dumps({"mergeStateStatus": "BLOCKED", "reviewDecision": "APPROVED",
                                  "statusCheckRollup": [{"name": "gate", "conclusion": r} for r in rollup]})
        if "/reviews" in a:
            return 0, json.dumps([[]])
        return 0, ""
    t = mt.Train("o/r", Path("."), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None,
                 polls=3, wall=lambda: NOW)
    t.required = lambda pr_head=False: ["gate"]
    return t.policy_refusal(3264, H)


def under(mt, status, polls=3):
    NOW = 1_800_000_000.0
    started = datetime.datetime.fromtimestamp(NOW - 5000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gate = {"name": "gate", "status": "completed", "conclusion": "failure", "started_at": "2026-11-06T14:55:00Z",
            "id": 1, "check_suite": {"id": 11}}
    green = dict(gate, conclusion="success", started_at="2026-11-06T15:26:00Z", id=3)
    seen = [0, 0]

    def run(argv, cwd=None, stdin=None):
        a = " ".join(argv)
        if "check-runs" in a:
            cur = [gate] if seen[0] < 8 else [green]
            seen[0] += 1
            return 0, "\n".join(json.dumps(c) for c in cur)
        if "actions/runs?head_sha=" in a:
            seen[1] += 1
            return 0, (f"42237558473\t{status}\t{started}\n" if seen[1] <= 7 else "42237558473\tcompleted\t\n")
        return 0, ""
    with tempfile.TemporaryDirectory() as d:
        t = mt.Train("o/r", Path(d), None, "", (), 1, run=run, sleep=lambda s: None, log=lambda s: None,
                     polls=polls, wall=lambda: NOW)
        return t.wait_ci("e" * 40, only=["gate"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=str(Path(__file__).resolve().parents[3]))
    mt = load(Path(ap.parse_args().tree))
    defects = 0
    got = policy(mt, ["SUCCESS", "FAILURE"])
    bad = not (got[1] is True and "review" not in got[0].split("(")[0])
    got0 = policy(mt, ["SUCCESS"])
    print(f"RESULT policy_wait={got[1]} policy_text_names_review={'review' in got[0].split('(')[0]}")
    print(f"RESULT policy_null_waits={got0[1]} (the passing gate alone must not wait)")
    print(f"RESULT policy_null_ok={got0[1] is False}")
    if bad:
        print("DEFECT policy"); defects += 1
    if got0[1] is not False:
        print("DEFECT policy-null"); defects += 1
    r = under(mt, "in_progress")
    q = under(mt, "queued")
    print(f"RESULT under_started={r} under_queued_null={q}")
    if r != []:
        print("DEFECT under"); defects += 1
    if q != ["TIMEOUT"]:
        print("DEFECT under-null"); defects += 1
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
