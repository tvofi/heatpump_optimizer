#!/usr/bin/env python3
"""Reviewer-built: run `merge_throughput.py flow` as the state beat does
(--roster-ref, no --until) against a ref whose roster JSON is unreadable.

Expectation under the PR's stated rule ("a source that cannot be read prints
UNAVAILABLE with its reason"): UNAVAILABLE. What it does instead is measured.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path("/private/tmp/rev-2883-r2/wt").expanduser()
sys.path.insert(0, str(WT / "tests"))
from throwaway_git import throwaway_git_env, throwaway_git_init  # noqa: E402

env = throwaway_git_env()
with tempfile.TemporaryDirectory() as d:
    R = Path(d)
    throwaway_git_init(R, "-q", "-b", "main")

    def g(*args, e=None):
        return subprocess.run(["git", "-C", d, *args], capture_output=True,
                              text=True, check=True,
                              env={**env, **(e or {})}).stdout.strip()

    (R / "roster.json").write_text('{"groups": [')      # unreadable JSON
    (R / "ok").write_text("x\n")
    g("add", "-A")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "root",
      e={"GIT_COMMITTER_DATE": "2026-10-01T00:00:00Z",
         "GIT_AUTHOR_DATE": "2026-10-01T00:00:00Z"})
    roster_path = "dev/programme/rosters/wave-r1-groups.json"
    (R / roster_path).parent.mkdir(parents=True)
    (R / roster_path).write_text('{"groups": [')        # malformed at the ref
    g("add", "-A")
    g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "roster",
      e={"GIT_COMMITTER_DATE": "2026-10-01T00:01:00Z",
         "GIT_AUTHOR_DATE": "2026-10-01T00:01:00Z"})
    g("update-ref", "refs/remotes/origin/main", "HEAD")
    g("update-ref", "refs/remotes/origin/roster", "HEAD")

    r = subprocess.run(
        [sys.executable, "-I", str(WT / "tools/audit/merge_throughput.py"),
         "flow", "--repo", d, "--tree", "refs/remotes/origin/main",
         "--roster-ref", "refs/remotes/origin/roster"],
        capture_output=True, text=True)
    print("RESULT rc =", r.returncode)
    print("RESULT stdout_has_UNAVAILABLE =", "UNAVAILABLE" in r.stdout)
    print("RESULT stderr_tail =", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
    print("RESULT stdout_head =", r.stdout.strip().splitlines()[0] if r.stdout.strip() else "")
