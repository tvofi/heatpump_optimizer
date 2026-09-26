#!/usr/bin/env python3
"""contract_rerun.py -- re-run `pr-contract` when a red it could not see lands.

D13-s1-03, as the judge narrowed it. `pr-contract` lists the failing check runs
at the head and refuses a body that does not answer them (#956), but it runs
about fifteen seconds after a push or a body edit, and the checks it must list
-- typing, fast, mutation -- finish minutes later. Nothing re-ran it when they
did, so a contract that went green before a red existed stayed green, and the
red reached review as a blocked verdict instead of a refused body.

WHAT IT DOES. `.github/workflows/pr-contract-rerun.yml` runs this on
`workflow_run` when a run of any workflow that reports at a pull request's head
concludes `failure`. It reads that run, lists `pr-contract.yml`'s
`pull_request` runs at the same head, and asks GitHub to re-run the NEWEST one
if that run's latest attempt STARTED before the red run finished -- the only
case in which its red list can have missed it. A re-run re-grades from nothing
(the body and the check runs are read live), so this writes no verdict; and a
contract run is never a trigger, so a re-run cannot start another.

    python3 -I .claude/workflows/contract_rerun.py --rerun RUN_ID [--repo O/R]
    python3 .claude/workflows/contract_rerun.py --self-test
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

CONTRACT_WORKFLOW = ".github/workflows/pr-contract.yml"
DEFAULT_REPO = "tvofi/heatpump_optimizer"


def stale_contract(trigger: dict, runs: list[dict]) -> tuple[str, int | None, str]:
    """(action, run id, why): "rerun", "wait" or "none" for one completed run.

    `trigger` is the completed run `workflow_run` names; `runs` the contract's
    runs at its head. Only the NEWEST `pull_request` run of the contract
    matters -- it is the one the pull request shows. A timestamp either side
    cannot supply is read as "may have missed it": a re-run costs one short
    job, a missed red costs a review round.
    """
    head = str(trigger.get("head_sha") or "")
    if trigger.get("path") == CONTRACT_WORKFLOW:
        return "none", None, "the completed run is the contract itself"
    if trigger.get("conclusion") != "failure":
        return "none", None, f"the completed run concluded {trigger.get('conclusion')!r}; no new red"
    same = [r for r in runs
            if r.get("path") == CONTRACT_WORKFLOW and r.get("event") == "pull_request"
            and r.get("head_sha") == head]
    if not same:
        return "none", None, f"no pull_request run of the contract at {head[:12]}"
    newest = max(same, key=lambda r: (str(r.get("created_at") or ""), r.get("id") or 0))
    if newest.get("status") != "completed":
        return "wait", newest.get("id"), f"contract run {newest.get('id')} at {head[:12]} is {newest.get('status')}"
    started, red_done = str(newest.get("run_started_at") or ""), str(trigger.get("updated_at") or "")
    if started and red_done and started >= red_done:
        return "none", None, (f"contract run {newest.get('id')} started {started}, after the red "
                              f"finished {red_done}; it listed it")
    return "rerun", newest.get("id"), (f"contract run {newest.get('id')} started {started or '?'}, "
                                       f"before the red run {trigger.get('id')} finished {red_done or '?'}")


def _gh_json(*args: str):
    out = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api {args[-1]} exited {out.returncode}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout) if out.stdout.strip() else {}


def rerun_contract(run_id: str, repo: str, api=_gh_json, sleep=None, polls: int = 30) -> int:
    """Exit 0 when a re-run was requested or nothing is stale; 1 when the API
    could not be read or refused, so the job is red and the stale contract is
    named rather than silently left. It is never a required context."""
    import time
    sleep = sleep or time.sleep
    try:
        trigger = api(f"repos/{repo}/actions/runs/{int(run_id)}")
        for _ in range(polls):
            runs = api(f"repos/{repo}/actions/workflows/pr-contract.yml/runs"
                       f"?event=pull_request&head_sha={trigger.get('head_sha')}&per_page=100")
            action, rid, why = stale_contract(trigger, runs.get("workflow_runs", []))
            if action != "wait":
                break
            print(f"WAIT: {why}")
            sleep(20)
        print(f"{action.upper()}: {why}")
        if action == "rerun":
            api("-X", "POST", f"repos/{repo}/actions/runs/{int(rid)}/rerun")
            print(f"RESULT rerun_requested={rid}")
        elif action == "wait":
            print("REFUSED: the contract run did not finish in time; re-run it by hand")
            return 1
        return 0
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"REFUSED: {str(e).splitlines()[0][:200] if str(e) else type(e).__name__}")
        return 1


def self_test() -> int:
    fails = n = 0

    def check(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    H, OLD = "h" * 40, "o" * 40
    T0 = {"id": 9, "path": ".github/workflows/tests.yml", "event": "pull_request",
          "conclusion": "failure", "head_sha": H, "updated_at": "2026-09-26T10:20:00Z"}

    def pc(i, started="2026-09-26T10:01:00Z", status="completed", sha=H, event="pull_request",
           path=CONTRACT_WORKFLOW, created=None):
        return {"id": i, "path": path, "event": event, "status": status, "head_sha": sha,
                "run_started_at": started, "created_at": created or f"2026-09-26T10:0{i}:00Z",
                "conclusion": "success" if status == "completed" else None}

    check("a red that finished after the contract started re-runs the contract",
          stale_contract(T0, [pc(3)])[:2], ("rerun", 3))
    check("a contract that started after the red finished is left alone (null control)",
          stale_contract(T0, [pc(3, started="2026-09-26T10:21:00Z")])[:2], ("none", None))
    check("only the newest contract run counts",
          stale_contract(T0, [pc(3), pc(4, started="2026-09-26T10:22:00Z")])[:2], ("none", None))
    check("... and it is the one re-run when it is stale",
          stale_contract(T0, [pc(3, started="2026-09-26T10:22:00Z", created="2026-09-26T10:00:00Z"),
                              pc(4)])[:2], ("rerun", 4))
    check("a green run is no new red", stale_contract({**T0, "conclusion": "success"}, [pc(3)])[:2],
          ("none", None))
    check("a cancelled run is no new red", stale_contract({**T0, "conclusion": "cancelled"}, [pc(3)])[:2],
          ("none", None))
    check("the contract's own completion re-runs nothing (no loop)",
          stale_contract({**T0, "path": CONTRACT_WORKFLOW}, [pc(3)])[:2], ("none", None))
    check("a contract run at another head is left alone", stale_contract(T0, [pc(3, sha=OLD)])[:2],
          ("none", None))
    check("another workflow's run is not the contract",
          stale_contract(T0, [pc(3, path=".github/workflows/governance.yml")])[:2], ("none", None))
    check("a push run at the head is not the contract the pull request shows",
          stale_contract(T0, [pc(3, event="push")])[:2], ("none", None))
    check("a contract still running is waited for",
          stale_contract(T0, [pc(3, status="in_progress")])[:2], ("wait", 3))
    check("a missing start time is read as stale",
          stale_contract(T0, [pc(3, started=None)])[:2], ("rerun", 3))
    check("a missing finish time is read as stale",
          stale_contract({**T0, "updated_at": None}, [pc(3, started="2026-09-26T10:21:00Z")])[:2],
          ("rerun", 3))
    check("a red from any other watched workflow counts",
          stale_contract({**T0, "path": ".github/workflows/governance.yml"}, [pc(3)])[:2], ("rerun", 3))

    def fake(pages, fail_post=False, trigger=T0):
        calls = []

        def api(*a):
            calls.append(a)
            if a[0] == "-X":
                if fail_post:
                    raise RuntimeError("HTTP 403")
                return {}
            if "/workflows/" in a[-1]:
                return {"workflow_runs": pages.pop(0) if len(pages) > 1 else pages[0]}
            return trigger
        return api, calls

    api, calls = fake([[pc(3, status="in_progress")], [pc(3)]])
    check("end to end: waits for the contract, then re-runs it",
          (rerun_contract("9", "o/r", api, sleep=lambda s: None), [c for c in calls if c[0] == "-X"]),
          (0, [("-X", "POST", "repos/o/r/actions/runs/3/rerun")]))
    check("end to end: lists the contract's runs at the red run's head",
          [c[-1] for c in calls if "/workflows/" in c[-1]][:1],
          [f"repos/o/r/actions/workflows/pr-contract.yml/runs?event=pull_request&head_sha={H}&per_page=100"])
    api, calls = fake([[pc(3, status="in_progress")]])
    check("end to end: a contract that never finishes is a red job, not a silent pass",
          rerun_contract("9", "o/r", api, sleep=lambda s: None, polls=3), 1)
    api, calls = fake([[pc(3)]], fail_post=True)
    check("end to end: a refused re-run request is a red job", rerun_contract("9", "o/r", api), 1)
    api, calls = fake([[pc(3, started="2026-09-26T10:21:00Z")]])
    check("end to end: nothing stale posts nothing (null control)",
          (rerun_contract("9", "o/r", api), [c for c in calls if c[0] == "-X"]), (0, []))

    def broken(*a):
        raise RuntimeError("HTTP 502")
    check("end to end: an unreadable run fails closed", rerun_contract("9", "o/r", broken), 1)

    print(f"contract_rerun self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    rest = dict(zip(argv[2::2], argv[3::2]))
    if argv[:1] != ["--rerun"] or len(argv) < 2 or len(argv) % 2 or set(rest) - {"--repo"}:
        print("usage: contract_rerun.py --rerun RUN_ID [--repo O/R] | --self-test", file=sys.stderr)
        return 2
    return rerun_contract(argv[1], rest.get("--repo") or os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
