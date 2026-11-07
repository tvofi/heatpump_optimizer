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
costs, after, its deferring attempt: prelude and gate at the floor (it runs
no unit and its gate publishes at once), every job other than prelude, gate
and the body units at its recorded minutes. The latest deferred run of each
kind at a head (gate.pending) also costs the re-run the code run's gate makes:
prelude and gate at the floor, its body units at their recorded minutes, a
unit the recording lacks (C3's skipped pr-contract) at the sample's median for
that unit. The code run's gate waits on those re-runs: per head, the largest
re-run's body-unit minutes, summed over its units (an estimate: arch-score and
budget-raise-gate run side by side, which it over-counts, and the re-run's job
pickups, which it does not count).
Only the kinds the predicate module defers are replayed (its BODY_KINDS; a
module without one, the merge base's, defers `edit` alone). --since keeps the
runs created at or after an instant, the rest staying in the state replayed.
NULL CONTROLS, printed beside the result: (1) code runs through the same
predicate (a code run never defers: 0 expected); (2) a run defer_to does not
defer costs the same before and after (by construction, its count printed).
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


def replay(sample: dict, pre, kinds=("edit", "review"), since: float = 0.0) -> dict:
    runs = sample["runs"]
    defers = tuple(getattr(pre, "BODY_KINDS", ("edit",)))
    kind_of = lambda r: (pre.parse_title(r["title"]) or ("",))[0]  # noqa: E731
    floor = statistics.median([m(j) for r in runs if kind_of(r) == "code" for j in r["jobs"]
                               if j["name"] == "prelude" and j.get("completed_at")] or [0.0])
    unit_med = {n: statistics.median([m(j) for r in runs for j in r["jobs"] if j["name"] == n
                                      and j.get("completed_at")] or [0.0]) for n in BODY}
    res = {k: {"runs": 0, "deferred": 0, "before": 0.0, "after": 0.0, "wait_before": 0.0, "wait_after": 0.0,
               "reruns": 0, "code_gate_wait_added": 0.0} for k in kinds}
    res["prelude_floor"] = floor
    latest: dict = {}
    for r in runs:
        t = pre.parse_title(r["title"])
        if t is None or t[0] not in kinds or edit_runs.ts(r["created_at"]) < since:
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
        hit = (defer is not None and t[1] != "" and t[0] in defers
               and defer(ctx, t[1], edit_runs.state_at(runs, r["head_sha"], edit_runs.ts(pj["started_at"]), r["id"]))
               is not None)
        if not hit:
            x["after"] += before
            x["wait_after"] += max(0.0, m(pj) - floor)
            continue
        x["deferred"] += 1
        rec = {j["name"]: m(j) for j in r["jobs"]}
        other = sum(v for n, v in rec.items() if n not in ("prelude", "gate") + BODY)
        x["after"] += 2 * floor + other
        units = sum(rec.get(n, unit_med[n]) for n in OWES.get(t[0], ()))
        key = (r["head_sha"], t[1], t[0])
        if key not in latest or latest[key][0] < r["id"]:
            latest[key] = (r["id"], units)
    gate_wait: dict = {}
    for (head, pr, kind), (_, units) in latest.items():
        res[kind]["reruns"] += 1
        res[kind]["after"] += 2 * floor + units
        if units > gate_wait.get(head, (0.0, kind))[0]:
            gate_wait[head] = (units, kind)
    for units, kind in gate_wait.values():
        res[kind]["after"] += units
        res[kind]["code_gate_wait_added"] += units
    return res


def show(label: str, res: dict) -> None:
    for k, x in res.items():
        if k == "prelude_floor":
            continue
        print(f"{label} {k}: {x['runs']} runs, {x['deferred']} deferred, {x['reruns']} re-run; "
              f"job-minutes {x['before']:.0f} -> "
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
    twin = {**early, "id": 4, "created_at": T(6)}
    s = {"runs": [code, early, late]}
    two = replay({"runs": [code, early, twin]}, pre)["review"]
    r = replay(s, pre)["review"]
    # early: before 38 + 2 + 1 = 41, wait 37; after (1+1+0) + (1+1+2) + 2 = 8. late: 4 both ends, wait 0.
    ok = (r["deferred"], r["before"], r["after"], r["wait_before"], r["wait_after"]) == (1, 45.0, 12.0, 37.0, 0.0)
    # two deferred at one head: the later is re-run once, the earlier costs its deferring attempt alone.
    ok &= (two["deferred"], two["reruns"], two["after"]) == (2, 1, 2.0 + 6.0 + 2.0)
    nul = replay(s, pre, kinds=("code",))["code"]
    ok &= nul["deferred"] == 0 and nul["after"] == nul["before"]
    print(f"body_defer self-test: {'ok' if ok else 'FAIL'} {r} / code control {nul['deferred']} deferred")
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sample", nargs="?")
    ap.add_argument("--prelude", default=str(ROOT / "tools" / "ci" / "prelude.py"))
    ap.add_argument("--since", default="")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    sample = json.loads(Path(a.sample).read_text())
    pre = edit_runs.load_prelude(Path(a.prelude))
    since = edit_runs.ts(a.since) or 0.0
    show(f"[{a.prelude} since {a.since or 'the start'}]", replay(sample, pre, since=since))
    show("[null control: code runs, same predicate]", replay(sample, pre, kinds=("code",), since=since))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
