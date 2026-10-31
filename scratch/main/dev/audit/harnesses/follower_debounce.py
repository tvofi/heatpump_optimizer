#!/usr/bin/env python3
"""follower_debounce.py -- drive pr-contract-rerun.yml's deferral step (R10-FOLLOWER-DEBOUNCE).

Extracts the workflow's first step (`id: last`) and runs it under bash with a
stub `gh` that prints a fixture runs list, so the decision -- DEFER, NONE, or
LAST with the red handed on -- is the file's own script, not a copy. Then
prints the per-head call model the PR body cites, from the rule each workflow
version follows (no live API call).

    python3 dev/audit/harnesses/follower_debounce.py [workflow.yml]

Needs bash and jq on PATH (both are on GitHub's ubuntu runners).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HEAD = "a" * 40
RED = ("failure", "timed_out", "cancelled")


def _run(i, name, status, concl=None, upd="2026-10-19T10:00:00Z"):
    return {"id": i, "name": name, "status": status, "conclusion": concl, "updated_at": upd}


CASES = {
    # name: (runs at the head, triggering run id, verdict prefix, red handed on)
    "another watched run in progress defers": (
        [_run(1, "Tests", "completed", "failure"), _run(2, "Governance", "in_progress")], 1, "DEFER", ""),
    "a green last completion after a deferred red hands that red on": (
        [_run(1, "Tests", "completed", "failure", "2026-10-19T10:05:00Z"),
         _run(2, "Governance", "completed", "success", "2026-10-19T10:09:00Z")], 2, "LAST", "1"),
    "the newest red is the one handed on": (
        [_run(1, "Tests", "completed", "failure", "2026-10-19T10:05:00Z"),
         _run(3, "Validate", "completed", "timed_out", "2026-10-19T10:07:00Z"),
         _run(2, "Governance", "completed", "success")], 2, "LAST", "3"),
    "no red at the head re-runs nothing (null control)": (
        [_run(1, "Tests", "completed", "success"), _run(2, "Governance", "completed", "success")],
        2, "NONE", ""),
    "a head with one watched run still re-runs": (
        [_run(1, "Tests", "completed", "failure")], 1, "LAST", "1"),
    "an unwatched run in progress does not defer": (
        [_run(1, "Tests", "completed", "failure"), _run(4, "PR contract", "in_progress"),
         _run(5, "Pages", "queued")], 1, "LAST", "1"),
    "the trigger listed stale as in progress does not defer itself": (
        [_run(1, "Tests", "in_progress")], 1, "NONE", ""),
    "a run waiting on an environment does not defer": (
        [_run(1, "Tests", "completed", "cancelled"), _run(2, "CodeQL", "waiting")], 1, "LAST", "1"),
}


def drive(wf: Path) -> int:
    step = (yaml.safe_load(wf.read_text())["jobs"]["rerun-stale-contract"]["steps"] or [{}])[0]
    if step.get("id") != "last":
        print(f"REFUSED: first step of {wf} is {step.get('id')!r}, not the deferral")
        return 1
    fails = n = 0
    with tempfile.TemporaryDirectory() as d:
        dd = Path(d)
        (dd / "step.sh").write_text(step["run"])
        (dd / "bin").mkdir()
        (dd / "bin" / "gh").write_text('#!/bin/bash\ncat "$FIXTURE"\n')
        (dd / "bin" / "gh").chmod(0o755)

        def go(runs, me, head=HEAD):
            fx, out = dd / "fx.json", dd / "out"
            fx.write_text(json.dumps({"workflow_runs": runs}))
            out.write_text("")
            env = dict(os.environ, PATH=f"{dd / 'bin'}:{os.environ['PATH']}", FIXTURE=str(fx),
                       RUN_ID=str(me), HEAD_SHA=head, REPO="o/r", WATCHED=step["env"]["WATCHED"],
                       RUNNER_TEMP=str(dd), GITHUB_OUTPUT=str(out))
            p = subprocess.run(["bash", str(dd / "step.sh")], env=env, capture_output=True, text=True)
            return p.returncode, p.stdout.strip(), out.read_text().strip().removeprefix("red=")

        for name, (runs, me, want, red) in CASES.items():
            n += 1
            rc, said, got = go(runs, me)
            ok = rc == 0 and said.startswith(want) and got == red
            fails += not ok
            print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": rc={rc} {said!r} red={got!r}"))
        n += 1
        rc, said, _ = go([], 1, head="main")
        fails += rc != 1
        print(f"  {'ok  ' if rc == 1 else 'FAIL'} a head that is not 40 hex is refused")
    print(f"follower_debounce: {n} cases, {fails} failed")
    return 1 if fails else 0


def model() -> None:
    """Calls per head on GITHUB_TOKEN's shared quota, contract run already finished.

    Before: each red completion ran the program -- GET the trigger, list the
    contract's runs (1 or more), POST a re-run when stale -- and each POST
    re-ran pr-contract (C calls, C >= 6 by its gh api lines). Green: no job.
    After: each completion runs one list call (fewer when a newer one cancels
    it first); only the last runs the program, once, and only with a red.
    """
    print("per-head model: N watched completions, R red, every red stale (worst case before)")
    C = 6
    for N, R in ((8, 0), (8, 1), (8, 2), (8, 3), (8, 8), (1, 1)):
        before_prog, before_contract = R, R
        before = R * (3 + C)
        after_prog = 1 if R else 0
        after = N + after_prog * (3 + C)
        print(f"  N={N} R={R}: program runs {before_prog} -> {after_prog}, contract re-runs "
              f"{before_contract} -> {after_prog}, API calls <= {before} -> <= {after}")


if __name__ == "__main__":
    wf = Path(sys.argv[1] if len(sys.argv) > 1 else ".github/workflows/pr-contract-rerun.yml")
    rc = drive(wf)
    model()
    sys.exit(rc)
