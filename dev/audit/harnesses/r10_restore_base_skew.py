#!/usr/bin/env python3
"""R10-HOTFIX-RESTORE-BASE-SKEW (triage P572): replay a pull request's
pr-contract restore and carry check against one restore source.

WHY IT EXISTS. pr-contract on PR 3424 checked out GitHub's merge commit
427c4ca874 (f9c7952b merged into c620ebba96) and restored its check source
from the payload's base.sha d08ed31049, an older main: roster_lib.py came back
without `carry_receivable`, carry_audit.py (not restored) called it, and the
step died with AttributeError. This harness rebuilds that merge commit (same
parents, so the same tree) and replays the two steps for real, from the
workflow text of the tree under test, so the fix and its null control can be
re-taken at any merge base.

Arms (each prints RESULT lines):

  resolve  runs ci.yml's prelude `source` step (the step's own `run:` text,
           read from --workflows-from) in a worktree at the merge commit with
           EVENT=pull_request, GITHUB_SHA=<merge> and EVENT_BASE=<payload
           base>, and prints the restore source it writes to GITHUB_OUTPUT
           (`RESULT source=`), or `none` where the tree has no such step.
  replay   runs pr-contract.yml's "Restore the check source from the base
           commit" step with PINNED=<source>, then the carry check
           (`carry_audit.py check`) on a body carrying one Carry: line to a
           live group, and prints `RESULT exit=` and `RESULT attributeerror=`.

    python3 -I dev/audit/harnesses/r10_restore_base_skew.py \\
        [--base-parent C] [--head H] [--payload-base D] \\
        [--source SHA | --resolve] [--workflows-from REF] [--group G]

Defaults are PR 3424's instance: C=c620ebba96, H=f9c7952b, D=d08ed31049.
`--source D` is the old restore (the payload base); `--resolve` takes the
source the resolver at --workflows-from prints. A null control is a payload
base equal to C: both arms then restore from one commit.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

C_3424 = "c620ebba969b482d3b3e48a38f7477d7031317af"
H_3424 = "f9c7952b3a261ec46c0ecebdde72fa622e2c7d3e"
D_3424 = "d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a"


def git(*args: str, cwd: str | None = None, env: dict | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def ensure(sha: str) -> None:
    if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode:
        git("fetch", "-q", "--no-tags", "origin", sha)


def merge_commit(parent: str, head: str) -> str:
    """GitHub's test merge of head into parent: same parents, so the same tree."""
    tree = git("merge-tree", "--write-tree", parent, head)
    env = {**os.environ, "GIT_AUTHOR_NAME": "replay", "GIT_AUTHOR_EMAIL": "replay@invalid",
           "GIT_COMMITTER_NAME": "replay", "GIT_COMMITTER_EMAIL": "replay@invalid",
           "GIT_AUTHOR_DATE": "2026-11-11T04:00:00Z", "GIT_COMMITTER_DATE": "2026-11-11T04:00:00Z"}
    return git("commit-tree", tree, "-p", parent, "-p", head, "-m", f"Merge {head} into {parent}", env=env)


def step_run(ref: str, wf: str, job: str, pick) -> str | None:
    doc = yaml.safe_load(git("show", f"{ref}:.github/workflows/{wf}"))
    for jid, j in (doc.get("jobs") or {}).items():
        if jid != job:
            continue
        for s in j.get("steps") or []:
            if pick(s):
                return s["run"]
    return None


def bash(script: str, cwd: str, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "-c", script], cwd=cwd, env={**os.environ, **env},
                          capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-parent", default=C_3424)
    ap.add_argument("--head", default=H_3424)
    ap.add_argument("--payload-base", default=D_3424)
    ap.add_argument("--source")
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--workflows-from", default="HEAD")
    ap.add_argument("--group", default="R10-BODY-CONTRACT")
    a = ap.parse_args()
    for sha in (a.base_parent, a.head, a.payload_base):
        ensure(sha)
    wf_ref = git("rev-parse", a.workflows_from)
    merge = merge_commit(a.base_parent, a.head)
    print(f"RESULT merge={merge}")
    with tempfile.TemporaryDirectory() as tmp:
        wt = str(Path(tmp, "wt"))
        git("worktree", "add", "-q", "--detach", wt, merge)
        try:
            source = a.source
            if a.resolve:
                run = step_run(wf_ref, "ci.yml", "prelude", lambda s: s.get("id") == "source")
                if run is None:
                    source = a.payload_base  # a tree with no resolver restores from the payload base
                    print("RESULT source=none")
                else:
                    out = Path(tmp, "out")
                    out.write_text("")
                    r = bash(run, wt, {"EVENT": "pull_request", "EVENT_BASE": a.payload_base,
                                       "GITHUB_SHA": merge, "GITHUB_OUTPUT": str(out)})
                    sys.stdout.write(r.stdout)
                    if r.returncode:
                        print(f"RESULT resolve_exit={r.returncode}")
                        return 1
                    source = dict(ln.split("=", 1) for ln in out.read_text().split() if "=" in ln)["sha"]
                    print(f"RESULT source={source}")
            if not source:
                ap.error("--source or --resolve")
            ensure(source)
            restore = step_run(wf_ref, "pr-contract.yml", "pr-contract",
                               lambda s: s.get("name") == "Restore the check source from the base commit")
            if restore is None:
                print("FAIL pr-contract.yml has no restore step at --workflows-from")
                return 1
            r = bash(restore, wt, {"PINNED": source, "RUNNER_TEMP": tmp})
            sys.stdout.write(r.stdout)
            if r.returncode:
                print(f"RESULT restore_exit={r.returncode}\n{r.stderr}")
                return 1
            body = Path(tmp, "body.md")
            body.write_text(f"## Friction\n\n- replay finding. Carry: {a.group}\n")
            r = subprocess.run([sys.executable, "-I", "tools/audit/carry_audit.py", "check",
                                "--body", str(body), "--branch", "replay"],
                               cwd=wt, capture_output=True, text=True)
            tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
            print("\n".join(f"  | {ln}" for ln in tail))
            print(f"RESULT exit={r.returncode}")
            print(f"RESULT attributeerror={'AttributeError' in r.stderr}")
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", wt], capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
