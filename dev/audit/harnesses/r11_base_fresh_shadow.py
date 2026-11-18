#!/usr/bin/env python3
"""r11_base_fresh_shadow.py -- base_fresh.py over a window of merged pull requests (R11-RCA-PLAN-OBJECTIVE-MISSING).

For every pull request merged to main by a first-parent merge since ``<since>``
(optionally until ``<until>``), by the root-cause seat's rule (its out-of-tree
``measure_seat_bases.py``):

  F    the branch's oldest own non-merge commit, authored at t;
  B    merge-base(F, main): the main commit the seat's work sits on;
  M_t  main's first-parent tip at t, and at t less one hour;
  H    the head merged, and M_h main's first-parent tip at H's commit date.

``tools/audit/seat/base_fresh.py``'s ``measure`` then judges B against M_t
(would the start have been refused) and H against M_h (what a reviewer at a
worktree of H reads that main had moved). The third line compares the second
count with the root-cause seat's handoff column, which takes the files main
changed since B rather than since H's own merge base: a head that merged main
after its first commit and edits a file main also moved is counted there and
is the branch's own here.

    python3 dev/audit/harnesses/r11_base_fresh_shadow.py <since ISO> [<until ISO>] [--repo DIR] [--main REF]

Reads history only; needs the full history (``git fetch --unshallow``). The
counts are functions of ``--main``'s tip: state it beside them. RESULT lines
carry the counts.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import base_fresh  # noqa: E402

#: The root-cause seat's path list, for its handoff column alone (base_fresh.POLICY is wider).
PROTOTYPE = ["CLAUDE.md", "AGENTS.md", "dev/governance", ".claude/workflows", ".claude/rules",
             ".claude/skills", "tools/audit", "tools/policy", "tools/pr", "tools/plan"]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("since")
    ap.add_argument("until", nargs="?")
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--main", default="origin/main")
    a = ap.parse_args(argv)
    repo = base_fresh._top(a.repo)

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout.strip()

    def at(when: datetime) -> str:
        return git("rev-list", "-1", "--first-parent", f"--before={when.isoformat()}", a.main)

    def names(x: str, y: str) -> set[str]:
        return {n for n in git("diff", "--name-only", x, y, "--", *PROTOTYPE).splitlines() if n}

    log = ["log", "--first-parent", "--merges", "--format=%H %P %cI %s", f"--since={a.since}"]
    if a.until:
        log.append(f"--until={a.until}")
    n = start0 = start1 = head = passed = proto = proto_only = proto_only_own = tool_only = 0
    for line in git(*log, a.main).splitlines():
        parts = line.split(" ", 4)
        if len(parts) < 5 or not parts[4].startswith("Merge pull request"):
            continue
        _merge, p1, p2, _date, _title = parts
        own = [x for x in git("rev-list", "--reverse", "--no-merges", "--format=%H %aI", f"{p1}..{p2}").splitlines()
               if not x.startswith("commit ")]
        if not own:
            continue
        first, authored = own[0].split(" ", 1)
        t = datetime.fromisoformat(authored).astimezone(timezone.utc)
        b = git("merge-base", first, p1)
        n += 1
        for lag in (0, 1):
            mt = at(t - timedelta(hours=lag))
            if mt and subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", b, mt]).returncode == 0 \
                    and base_fresh.measure(repo, mt, b)["stale"]:
                start0, start1 = start0 + (lag == 0), start1 + (lag == 1)
        mh = at(datetime.fromisoformat(git("log", "-1", "--format=%cI", p2)).astimezone(timezone.utc))
        if not mh:
            continue
        m = base_fresh.measure(repo, mh, p2)
        theirs = names(b, mh) & names(p2, mh)
        head, passed, proto = head + bool(m["stale"]), passed + (not m["stale"]), proto + bool(theirs)
        if theirs and not m["stale"]:
            proto_only += 1
            proto_only_own += theirs <= set(m["own"])
        tool_only += bool(m["stale"]) and not theirs
    print(f"window: {n} merged pull request(s) since {a.since}{' until ' + a.until if a.until else ''}, "
          f"{a.main} at {git('rev-parse', '--short=10', a.main)}")
    print(f"RESULT start_refused_lag0={start0} start_refused_lag1h={start1} of={n}")
    print(f"RESULT heads_behind_main_on_policy={head} heads_level={passed} of={n}")
    print(f"RESULT rootcause_handoff_column={proto} of_which_level_here={proto_only} "
          f"of_those_every_file_the_branch_own={proto_only_own} behind_here_only={tool_only}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
