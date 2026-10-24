#!/usr/bin/env python3
"""The harness for the `handoff/` INERT classification (friction #1712/#1700).

Run from a checkout whose `tests/closure.py` carries the entry:

    python3 tools/audit/handoff/r9-frictions/handoff_inert_harness.py

Three arms over four file classes:

  head    -- select() with the committed INERT (the fix);
  mutant  -- select() with the `handoff/` entry deleted from the module
             globals, which is the mutation proof: the ONLY behavioural diff
             between the entry's absence and origin/main's INERT is the entry
             itself, so the mutant arm reproduces the base refusal verbatim;
  base    -- the same measurement through `git show origin/main:tests/closure.py`
             executed with its real ROOT (a scratch checkout), recorded here so
             the equivalence claim is a printed line, not an assertion.

Note for the next seat writing a mutation proof against a module-level
constant: `runpy.run_path` returns a COPY of the module globals, so mutating
the returned dict leaves every function reading the original. The mutant arm
must mutate `fn.__globals__`, not the dict `run_path` hands back.
"""
from __future__ import annotations

import os
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CASES = {
    "handoff note": ["handoff/round9/fix/note.md"],
    "unclassified seatnotes (null control)": ["seatnotes/x.md"],
    "docs file (already INERT)": ["docs/foo.md"],
    "production file": ["custom_components/heatpump_optimizer/coordinator.py"],
}


def plan(select_fn, files):
    p = select_fn(files)
    return p["mode"], p["reason"]


def head_and_mutant():
    mod = runpy.run_path(str(ROOT / "tests" / "closure.py"))
    g = mod["select"].__globals__
    for name, files in CASES.items():
        mode, reason = plan(mod["select"], files)
        print(f"  head    {name:38s} {mode:6s} {reason[:56]}")
    g["INERT"] = tuple(x for x in g["INERT"] if x != "handoff/")
    for name, files in CASES.items():
        mode, reason = plan(mod["select"], files)
        print(f"  mutant  {name:38s} {mode:6s} {reason[:56]}")


def base():
    """The real base CLI, not a copy: a detached worktree at origin/main,
    one commit adding a tracked handoff note, select against its parent."""
    tmp = Path(tempfile.mkdtemp(prefix="hpo-inert-base-"))
    wt = tmp / "wt"
    try:
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(wt), "origin/main"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        (wt / "handoff" / "round9" / "fix").mkdir(parents=True)
        (wt / "handoff" / "round9" / "fix" / "note.md").write_text(
            "# resume note (friction fixture)\nseat notes, read by no gate script\n"
        )
        env = dict(os.environ, GIT_AUTHOR_NAME="seat", GIT_AUTHOR_EMAIL="seat@local",
                   GIT_COMMITTER_NAME="seat", GIT_COMMITTER_EMAIL="seat@local")
        subprocess.run(["git", "add", "handoff"], cwd=wt, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "fixture: handoff note"],
                       cwd=wt, env=env, check=True, capture_output=True)
        out = subprocess.run(
            [sys.executable, "tests/closure.py", "select", "--diff", "HEAD~1"],
            cwd=wt, env=env, capture_output=True, text=True, check=True,
        ).stdout
        for line in out.splitlines():
            if line.startswith("  MODE:") or line.startswith("  reason:"):
                print(f"  base    {line.strip()}")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=ROOT, capture_output=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True)


if __name__ == "__main__":
    print("== base (origin/main closure.py, real CLI, tracked handoff note) ==")
    base()
    print("== head and entry-deleted mutant ==")
    head_and_mutant()
    sys.exit(0)
