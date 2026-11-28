#!/usr/bin/env python3
"""#3885 carry 2: which fork points on main find a warmed drift baseline.

    python3 dev/audit/harnesses/ci3885_drift_fork.py walk [--count 60] [--ref origin/main]
    python3 dev/audit/harnesses/ci3885_drift_fork.py warm HEAVY_SHA CACHE_DIR

`walk` classifies the last COUNT first-parent commits of REF. A commit
RECORDED a baseline when its push ran tests/env_drift.py, which warms the
entry under its own key: its first-parent diff is not light by
tools/ci/prelude.py's `light`, or tests/env_drift.py's `capture_reaches` says
the capture reads it. A pull request forked at a commit hits BEFORE the fix
when that commit recorded (the lookup tried its key alone) and AFTER it when any
commit `baseline_candidates` returns for it recorded (the keys it restores).
Each commit is checked out in one detached scratch worktree so the walk's
closures.json guard reads that commit's file; the closure rule itself is this
checkout's (tests/closure.py and tests/closures.json at the head), and a push
is approximated by its commit's first-parent diff (prelude.push_range reads
the run list, which history does not keep). A nightly warms main's tip as well,
which this count does not see: BEFORE is a lower bound on hits.
Null control: a fork at a commit that recorded resolves to itself first, so
its BEFORE and AFTER agree; `walk` refuses (exit 1) on one that does not.

`warm` stores HEAVY_SHA's capture under the key this checkout's env_drift.py
computes for it, in CACHE_DIR: the entry a recording push leaves, for the
timed before/after run the PR body states.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools" / "ci")]

import env_drift  # noqa: E402
import prelude  # noqa: E402


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def own_diff(sha: str) -> list[str]:
    return [f for f in git("diff", "--no-renames", "--name-only", f"{sha}^1", sha).split("\n") if f]


def recorded(sha: str, memo: dict) -> bool:
    if sha not in memo:
        files = own_diff(sha)
        memo[sha] = (not prelude.light(files)) or env_drift.capture_reaches(
            files, env_drift._closures_at(str(ROOT), f"{sha}^1"))
    return memo[sha]


def walk(count: int, ref: str) -> int:
    shas = git("rev-list", "--first-parent", f"--max-count={count}", ref).split()
    memo: dict = {}
    scratch = Path(tempfile.mkdtemp(prefix="drift_fork_"))
    tree = scratch / "wt"
    git("worktree", "add", "-q", "--detach", str(tree), shas[0])
    before = after = light_forks = 0
    broken = []
    try:
        for sha in shas:
            git("checkout", "-q", "--detach", sha, cwd=tree)
            cands = env_drift.baseline_candidates(str(tree), sha)
            hit_before = recorded(sha, memo)
            first = next((i for i, c in enumerate(cands) if recorded(c, memo)), None)
            hit_after = first is not None
            if hit_before and first != 0:
                broken.append(sha)
            light_forks += not hit_before
            before += hit_before
            after += hit_after
            print(f"{sha[:12]} recorded={'yes' if hit_before else 'no '} "
                  f"candidates={len(cands):2d} resolves_to="
                  f"{cands[first][:12] if hit_after else '-':12s} "
                  f"before={'hit ' if hit_before else 'miss'} after={'hit ' if hit_after else 'miss'}")
    finally:
        git("worktree", "remove", "--force", str(tree))
    print(f"WALK {ref} last {len(shas)} first-parent commits: {light_forks} fork point(s) "
          f"recorded no baseline; hits before {before}, after {after}")
    if broken:
        print(f"NULL CONTROL FAILED: recorded commit(s) not resolved to themselves: {broken}")
        return 1
    print(f"null control: every recorded commit ({before}) resolves to itself first")
    return 0


def warm(sha: str, directory: str) -> int:
    scratch = Path(tempfile.mkdtemp(prefix="drift_warm_"))
    tree = scratch / "wt"
    git("worktree", "add", "-q", "--detach", str(tree), sha)
    try:
        out = scratch / "capture.json"
        env = {**os.environ, "PYTHONPATH": str(tree / "tests" / "hastub")}
        subprocess.run([sys.executable, env_drift.__file__, "--capture", str(tree), str(out), "--all"],
                       check=True, env=env)
        inputs = env_drift.cache_key_inputs(str(ROOT), sha, True)
        key = env_drift.cache_key(inputs)
        env_drift.cache_store(env_drift.cache_entry_path(directory, key), key, inputs, sha,
                              out.read_text())
        print(f"WARMED {sha[:12]} key {key[:16]} in {directory}")
    finally:
        git("worktree", "remove", "--force", str(tree))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="arm", required=True)
    w = sub.add_parser("walk")
    w.add_argument("--count", type=int, default=60)
    w.add_argument("--ref", default="origin/main")
    m = sub.add_parser("warm")
    m.add_argument("sha")
    m.add_argument("directory")
    a = ap.parse_args(argv)
    if a.arm == "walk":
        return walk(a.count, a.ref)
    return warm(git("rev-parse", a.sha), a.directory)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
