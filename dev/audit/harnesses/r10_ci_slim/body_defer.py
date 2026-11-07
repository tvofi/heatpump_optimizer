#!/usr/bin/env python3
"""R10-CI-EDIT-RUNNER: what CI 'edit' and 'review' runs cost, before and after a
body run beside an unfinished code run stops holding a runner.

    python3 dev/audit/harnesses/r10_ci_slim/body_defer.py SAMPLE.json [--prelude PATH]
    python3 dev/audit/harnesses/r10_ci_slim/body_defer.py --self-test

SAMPLE.json is edit_runs.py's recording (`edit_runs.py --fetch`): every ci.yml
run created in a window, with its latest jobs.

THE RULE. A job costs completed_at - started_at (job-minutes; queueing is not
counted). A body run is a run whose title parses to kind `edit` or `review`
(prelude.parse_title). The prelude WAIT of a body run is its prelude's minutes
above the PRELUDE FLOOR, the median prelude of the sample's code runs (a
prelude that never waits). For each body run the replay rebuilds the Actions
state its prelude read at the prelude's started_at (edit_runs.state_at) and
hands it to the PRODUCTION predicate prelude.defer_to of --prelude (default:
this tree's copy). A run it does not defer costs what it cost. A run it defers
costs, after, two attempts and one wait:
  - the deferring attempt: prelude and gate at the floor (it runs no unit and
    its gate publishes at once), every job other than prelude, gate and the
    body units at its recorded minutes;
  - the re-run the code run's gate makes: prelude and gate at the floor, its
    body units at their recorded minutes, a unit the recording lacks (C3's
    skipped pr-contract) at the sample's median for that unit;
  - the code run's gate waiting on that re-run: the re-run's body-unit
    minutes, summed (an upper bound: arch-score and budget-raise-gate run
    side by side before pr-contract).
NULL CONTROLS, printed beside the result: (1) code runs through the same
predicate (a code run never defers: 0 expected); (2) the merge base's
prelude, given as --prelude, defers no review run (its outputs() never asked).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edit_runs  # noqa: E402

ROOT = edit_runs.ROOT
BODY = ("arch-score / arch-score", "budget-raise-gate / budget-raise-gate", "pr-contract / pr-contract")
OWES = {"edit": BODY, "review": ("budget-raise-gate / budget-raise-gate",)}
m = edit_runs.minutes


def replay(sample: dict, pre, kinds=("edit", "review")) -> dict:
    runs = sample["runs"]
    kind_of = lambda r: (pre.parse_title(r["title"]) or ("",))[0]  # noqa: E731
    floor = statistics.median([m(j) for r in runs if kind_of(r) == "code" for j in r["jobs"]
                               if j["name"] == "prelude" and j.get("completed_at")] or [0.0])
    unit_med = {n: statistics.median([m(j) for r in runs for j in r["jobs"] if j["name"] == n
                                      and j.get("completed_at")] or [0.0]) for n in BODY}
    res = {k: {"runs": 0, "deferred": 0, "before": 0.0, "after": 0.0, "wait_before": 0.0, "wait_after": 0.0,
               "code_gate_wait_added": 0.0} for k in kinds}
    res["prelude_floor"] = floor
    for r in runs:
        t = pre.parse_title(r["title"])
        if t is None or t[0] not in kinds:
            continue
        pj = next((j for j in r["jobs"] if j["name"] == "prelude" and j.get("started_at")), None)
        if pj is None:
            continue
        x = res[t[0]]
        x["runs"] += 1
        before = sum(m(j) for j in r["jobs"])
        x["before"] += before
        x["wait_before"] += max(0.0, m(pj) - floor)
        defer = getattr(pre, "defer_to", None)
        ctx = {"repo": "o/r", "head": r["head_sha"], "run_id": r["id"]}
        hit = (defer is not None and t[1] != ""
               and defer(ctx, t[1], edit_runs.state_at(runs, r["head_sha"], edit_runs.ts(pj["started_at"]), r["id"]))
               is not None)
        if not hit:
            x["after"] += before
            x["wait_after"] += max(0.0, m(pj) - floor)
            continue
        x["deferred"] += 1
        rec = {j["name"]: m(j) for j in r["jobs"]}
        other = sum(v for n, v in rec.items() if n not in ("prelude", "gate") + BODY)
        units = sum(rec.get(n, unit_med[n]) for n in OWES[t[0]])
        x["after"] += (2 * floor + other) + (2 * floor + units) + units
        x["code_gate_wait_added"] += units
    return res


def show(label: str, res: dict) -> None:
    for k, x in res.items():
        if k == "prelude_floor":
            continue
        print(f"{label} {k}: {x['runs']} runs, {x['deferred']} deferred; job-minutes {x['before']:.0f} -> "
              f"{x['after']:.0f}; prelude wait above the floor {x['wait_before']:.0f} -> {x['wait_after']:.0f}; "
              f"code-gate wait added {x['code_gate_wait_added']:.0f}")
    print(f"{label} prelude floor {res['prelude_floor']:.2f} min")


def self_test() -> int:
    pre = edit_runs.load_prelude(ROOT / "tools" / "ci" / "prelude.py")
    T = lambda mm: f"2026-11-05T10:{mm:02d}:00Z"  # noqa: E731

    def job(n, a, b, c="success"):
        return {"name": n, "status": "completed", "conclusion": c, "started_at": T(a), "completed_at": T(b)}
    code = {"id": 1, "title": pre.title("code", "7", "main", "H"), "head_sha": "H", "event": "pull_request",
            "created_at": T(0), "status": "completed",
            "jobs": [job("prelude", 0, 1), job("tests / fast (3.14)", 1, 40), job("pr-contract / pr-contract", 41, 42),
                     job("gate", 42, 43)]}
    early = {"id": 2, "title": pre.title("review", "7", "main", "H"), "head_sha": "H", "event": "pull_request_review",
             "created_at": T(5), "status": "completed",
             "jobs": [job("prelude", 5, 43), job("budget-raise-gate / budget-raise-gate", 43, 45), job("gate", 45, 46)]}
    late = {**early, "id": 3, "created_at": T(50),
            "jobs": [job("prelude", 50, 51), job("budget-raise-gate / budget-raise-gate", 51, 53), job("gate", 53, 54)]}
    s = {"runs": [code, early, late]}
    r = replay(s, pre)["review"]
    # early: before 38 + 2 + 1 = 41, wait 37; after (1+1+0) + (1+1+2) + 2 = 8. late: 4 both ends, wait 0.
    ok = (r["deferred"], r["before"], r["after"], r["wait_before"], r["wait_after"]) == (1, 45.0, 12.0, 37.0, 0.0)
    nul = replay(s, pre, kinds=("code",))["code"]
    ok &= nul["deferred"] == 0 and nul["after"] == nul["before"]
    print(f"body_defer self-test: {'ok' if ok else 'FAIL'} {r} / code control {nul['deferred']} deferred")
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sample", nargs="?")
    ap.add_argument("--prelude", default=str(ROOT / "tools" / "ci" / "prelude.py"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    sample = json.loads(Path(a.sample).read_text())
    pre = edit_runs.load_prelude(Path(a.prelude))
    show(f"[{a.prelude}]", replay(sample, pre))
    show("[null control: code runs, same predicate]", replay(sample, pre, kinds=("code",)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
