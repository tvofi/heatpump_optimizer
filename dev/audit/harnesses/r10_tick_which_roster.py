#!/usr/bin/env python3
"""Which roster the seat tools read and edit, at a tool tree (R10-TICK b, d, j).

Written by the R10-TICK roster-tooling fixer. Round 10's roster
(`dev/programme/rosters/wave-r10-groups.json`) lands in a tree that still
carries round 9's. A tool holding the round-9 path as a constant cannot edit
or read round 10's: `roster_edit.py wire-issue` refuses every round-10 group,
and `orchestrator_tick.py --only PLAN` lists round-9 groups even at the
round-10 ref, because `git show <r10 ref>:<r9 path>` succeeds there.

The harness copies two refs of a real clone (`main` and the roster ref) into a
throwaway bare repository, so nothing it does reaches GitHub, then drives the
tools of `--tree` (a worktree at the commit under test) against it:

  wire_r10       roster_edit.py wire-issue <r10 group> <issue> at the roster
                 ref, without --push: its rc, and which roster file the local
                 commit touched;
  null_r9_main   the null control: the same op on a round-9 group at `main`,
                 where only round 9's roster exists -- it must succeed at the
                 base AND at the head (the fix changes nothing with one roster);
  tick_plan      orchestrator_tick.py --only PLAN at origin/<roster ref>: how
                 many PLAN lines name a round-9 group and how many a round-10
                 group;
  daemonize      daemonize.py --log L -- true: its rc (the documented form).

`--roster-path P` is passed to roster_edit and the tick: the perturbation arm
(at the head, naming the round-9 roster must turn wire_r10 back into a
refusal and the tick back to round-9 groups). The base has no such flag.

    python3 -I dev/audit/harnesses/r10_tick_which_roster.py \\
        --tree <worktree at the commit> --repo <clone with origin/main and the ref> \\
        [--ref handoff/audit-r10-roster] [--group R10-TICK-ORCH] \\
        [--r9-group R9-A] [--issue 99999] [--roster-path P]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "tests"))
from throwaway_git import throwaway_git_clone, throwaway_git_environ, throwaway_git_init  # noqa: E402

R9 = "dev/programme/rosters/wave-r9-groups.json"


def sh(cmd, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", default="handoff/audit-r10-roster")
    ap.add_argument("--group", default="R10-TICK-ORCH")
    ap.add_argument("--r9-group", default=None,
                    help="default: the round-9 roster's first group")
    ap.add_argument("--issue", default="99999")
    ap.add_argument("--roster-path", default=None)
    a = ap.parse_args()
    tree = Path(a.tree).resolve()
    head = sh(["git", "-C", str(tree), "rev-parse", "HEAD"]).stdout.strip()
    print(f"tree {tree} at {head}")
    tmp = Path(tempfile.mkdtemp(prefix="hpo-r10-tick-"))
    try:
        with throwaway_git_environ():
            bare = tmp / "origin.git"
            throwaway_git_init(bare, "-q", "--bare", "-b", "main")
            r = sh(["git", "-C", a.repo, "push", "-q", str(bare),
                    "refs/remotes/origin/main:refs/heads/main",
                    f"refs/remotes/origin/{a.ref}:refs/heads/{a.ref}"])
            if r.returncode:
                print(f"seed push failed: {r.stderr.strip()[:300]}")
                return 2
            drv = tmp / "drv"
            throwaway_git_clone(bare, drv, "-q")
            r9_group = a.r9_group or json.loads(sh(
                ["git", "-C", str(drv), "show", f"origin/main:{R9}"]
            ).stdout)["groups"][0]["group"]
            extra = ["--roster-path", a.roster_path] if a.roster_path else []

            def wire(group, ref, branch, wt):
                r = sh([sys.executable, str(tree / "tools/audit/seat/roster_edit.py"),
                        "wire-issue", group, a.issue, "--checkout", str(drv),
                        "--roster-ref", ref, "--branch", branch,
                        "--worktree", str(tmp / wt), "--lint-cwd", str(drv),
                        *extra])
                touched = sh(["git", "-C", str(tmp / wt), "diff", "--name-only",
                              f"origin/{ref}", "HEAD"]).stdout.split() \
                    if (tmp / wt).exists() else []
                tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                print(f"  {group} at {ref}: rc {r.returncode} "
                      f"touched {touched or '-'} :: {tail[0][:160]}")
                return r.returncode, touched

            print("wire_r10:")
            rc, touched = wire(a.group, a.ref, "probe-r10", "wt-r10")
            print(f"RESULT wire_r10_rc={rc}")
            print(f"RESULT wire_r10_touched_r10_file="
                  f"{int(any('wave-r10-' in t for t in touched))}")
            print("null_r9_main:")
            rc9, _ = wire(r9_group, "main", "probe-r9", "wt-r9")
            print(f"RESULT null_r9_main_rc={rc9}")

            r = sh([sys.executable, str(tree / "tools/audit/seat/orchestrator_tick.py"),
                    "--only", "PLAN", "--checkout", str(drv),
                    "--roster-ref", f"origin/{a.ref}", *extra])
            plan = [ln for ln in r.stdout.splitlines()]
            n9 = sum(1 for ln in plan if re.search(r"\bR9-[A-Z0-9-]+:", ln))
            n10 = sum(1 for ln in plan if re.search(r"\bR10-[A-Z0-9-]+:", ln))
            print(f"tick_plan: rc {r.returncode}; "
                  + "; ".join(ln.strip() for ln in plan
                              if "roster" in ln or "UNREADABLE" in ln)[:300])
            print(f"RESULT tick_plan_r9_lines={n9}")
            print(f"RESULT tick_plan_r10_lines={n10}")

        log = tmp / "d.log"
        r = sh([sys.executable, str(tree / "tools/audit/seat/daemonize.py"),
                "--log", str(log), "--", "true"])
        print(f"RESULT daemonize_dashdash_rc={r.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
