#!/usr/bin/env python3
"""The stable tools ref: the one place its name, its seat paths, `behind` and `promote` exist.

    python3 -I tools/audit/seat/toolchain.py behind [<dir>] [--from <sha>] [--all] [--fetch]
    python3 -I tools/audit/seat/toolchain.py promote [<sha>] [--init] --repo <owner/name> [--dir <checkout>]
    python3 -I tools/audit/seat/toolchain.py --self-test

Owner ruling 2026-11-13 (card P1): seats and the beat run their tools from a
promoted stable ref, never the tip of main. The ref is the branch
`toolchain/stable`, always a commit of main, moved only by `promote`.

`behind` prints the count of commits in `<from or HEAD>..origin/toolchain/stable`
touching SEAT_PATHS (`--all`: every commit). A checkout level with or ahead of
the ref counts 0, so no caller is ever told to move backwards. `--fetch` reads
the ref from origin first. An absent ref refuses with the init command and is
never read as main.

`promote` moves the ref to the newest main commit whose `ci.yml` push run reads
MACHINERY green (`tools/ci/gate.py` `status`, the one owner of that verdict),
or to <sha> when given. It refuses a commit not on origin/main, a move that is
not a fast-forward, and a verdict that is not green; it pushes without force,
reads the ref back and prints

    PROMOTE <utc> <old> -> <new> run=<id>

`PROMOTE-CURRENT` when nothing newer is green, and `PROMOTE-HELD` with exit 3
when the newest HELD_RUNS concluded main runs past the ref are all machinery
red or unread. `--init` creates the ref, and only while it is absent.

Exit: 0 promoted, current or a count printed; 1 refused; 2 a read failed; 3 held.
"""
from __future__ import annotations

import argparse
import functools
import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                      # -I drops the script's directory
import gh_read_run  # noqa: E402  the seat's one retried GitHub read

REF_PREFIX = "toolchain/"                          # prune_refs.py keeps the family
REF = REF_PREFIX + "stable"
TRACKING = f"refs/remotes/origin/{REF}"
BASE = "main"
WORKFLOW = "ci.yml"
#: What a seat runs from its tools checkout: the union of the lists the freshness sites held
#: (beatd.py SEAT_PATHS, pr_args.sh PR_FRESH_PATHS, tick_loop.sh CODE_PATHS).
SEAT_PATHS = ("tools/audit/seat", "tools/pr", "tools/audit/carry_audit.py")
HELD_RUNS = 3      # this many newest concluded main runs past the ref, none machinery green: PROMOTE-HELD
SCAN_RUNS = 10     # the walk's bound: concluded runs read for a green one before giving up
LIST_RUNS = 30     # one listing page of main's push runs
INIT = "python3 -I tools/audit/seat/toolchain.py promote --init --repo <owner/name>"
SHA = re.compile(r"[0-9a-f]{40}")
_GATE_PY = HERE.parents[1] / "ci" / "gate.py"


class Refused(Exception):
    """The rule says no (exit 1)."""


class Unreadable(Exception):
    """A read failed, so nothing is concluded (exit 2)."""


@functools.lru_cache(maxsize=1)
def gate_py():
    """tools/ci/gate.py from its tree path: its `status` is THE verdict, never a copy."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("hpo_ci_gate", str(_GATE_PY))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_in(d: str):
    def git(*args: str) -> tuple[int, str]:
        p = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True)
        return p.returncode, (p.stdout if p.returncode == 0 else p.stderr).strip()
    return git


def gh(argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    rc = gh_read_run.read(argv, out=out, err=err)
    return rc, (out.getvalue() if rc == 0 else " ".join(err.getvalue().split()))


def absent() -> Refused:
    return Refused(f"origin/{REF} is absent: it is never read as {BASE}; create it once with `{INIT}`")


def behind(git, frm: str = "HEAD", every: bool = False, fetch: bool = False) -> int:
    """Commits the stable ref holds that <frm> lacks, over SEAT_PATHS unless `every`."""
    if fetch:
        rc, out = git("fetch", "-q", "origin", f"+refs/heads/{REF}:{TRACKING}")
        if rc and "couldn't find remote ref" in out:
            raise absent()
        if rc:
            raise Unreadable(f"could not fetch origin {REF}: {out[-200:]}")
    if git("rev-parse", "-q", "--verify", f"{TRACKING}^{{commit}}")[0]:
        raise absent()
    rc, out = git("rev-list", "--count", f"{frm}..{TRACKING}", *(() if every else ("--", *SEAT_PATHS)))
    if rc or not out.isdigit():
        raise Unreadable(f"could not count {frm}..origin/{REF}: {out[-200:]}")
    return int(out)


def main_runs(api, repo: str, sha: str = "") -> list[dict]:
    """Main's `ci.yml` push runs, newest first (those at <sha> when given)."""
    rc, out = api(["gh", "api", f"repos/{repo}/actions/workflows/{WORKFLOW}/runs?branch={BASE}&event=push"
                   f"&per_page={LIST_RUNS}" + (f"&head_sha={sha}" if sha else ""), "--jq", ".workflow_runs"])
    try:
        runs = None if rc else json.loads(out)
    except ValueError:
        runs = None
    if not isinstance(runs, list):
        raise Unreadable(f"could not list {BASE}'s {WORKFLOW} push runs: {out[-200:]}")
    return sorted(runs, key=lambda r: r.get("id") or 0, reverse=True)


def machinery(api, repo: str, run: dict) -> str:
    """One concluded run's MACHINERY verdict, from its latest jobs."""
    import gh_read
    rc, jobs, why = gh_read.read_pages(api, f"repos/{repo}/actions/runs/{run.get('id')}/jobs?filter=latest", "jobs")
    if rc or jobs is None:
        raise Unreadable(f"could not list the jobs of run {run.get('id')}: {why[-200:]}")
    return gate_py().status({j.get("name"): (j.get("status"), j.get("conclusion")) for j in jobs}, "push")[1]


def choose(runs: list[dict], verdict, at_or_behind) -> tuple[dict | None, list[tuple]]:
    """(the newest machinery-green concluded run past the ref or None, the (id, verdict) pairs read).
    The walk stops at the first run the ref already holds: nothing older moves it."""
    read: list[tuple] = []
    for run in [r for r in runs if r.get("status") == "completed"][:SCAN_RUNS]:
        if at_or_behind(run.get("head_sha") or ""):
            break
        v = verdict(run)
        read.append((run.get("id"), v))
        if v == gate_py().GREEN:
            return run, read
    return None, read


def held(read: list[tuple]) -> bool:
    return len(read) >= HELD_RUNS and all(v != gate_py().GREEN for _, v in read[:HELD_RUNS])


def promote(git, api, repo: str, sha: str = "", create: bool = False, now=time.time, out=print) -> int:
    def ok(*args: str) -> bool:
        return git(*args)[0] == 0
    rc, listed = git("ls-remote", "origin", f"refs/heads/{REF}")
    if rc:
        raise Unreadable(f"could not read origin's {REF}: {listed[-200:]}")
    old = listed.split()[0] if listed else ""
    if not old and not create:
        raise absent()
    if old and create:
        raise Refused(f"--init only while {REF} is absent; it is at {old[:12]}")
    rc, why = git("fetch", "-q", "origin", BASE, *((f"+refs/heads/{REF}:{TRACKING}",) if old else ()))
    if rc:
        raise Unreadable(f"could not fetch origin {BASE}: {why[-200:]}")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now()))

    def holds(commit: str) -> bool:                 # the ref is at or past <commit>
        return bool(old) and ok("merge-base", "--is-ancestor", commit, old)

    def movable(new: str, what: str) -> None:
        if not SHA.fullmatch(new) or not ok("merge-base", "--is-ancestor", new, f"origin/{BASE}"):
            raise Refused(f"{what} is not a commit of origin/{BASE}")
        if old and not ok("merge-base", "--is-ancestor", old, new):
            raise Refused(f"{old[:12]} -> {new[:12]} is not a fast-forward: the ref never moves backwards")
    read: list[tuple] = []
    if sha == old and sha:
        run = None
    elif sha:
        movable(sha, sha[:12])
        done = [r for r in main_runs(api, repo, sha) if r.get("status") == "completed" and r.get("head_sha") == sha]
        v = machinery(api, repo, done[0]) if done else gate_py().UNREAD
        if v != gate_py().GREEN:
            raise Refused(f"{sha[:12]} reads MACHINERY {v}" + (f" (run {done[0].get('id')})" if done else
                                                              f" (no concluded {WORKFLOW} push run)"))
        run = done[0]
    else:
        run, read = choose(main_runs(api, repo), lambda r: machinery(api, repo, r), holds)
        if run is not None:
            movable(run.get("head_sha") or "", f"run {run.get('id')}'s head {(run.get('head_sha') or '')[:12]}")
    if run is not None:
        new = run["head_sha"]
        rc, why = git("push", "-q", "origin", f"{new}:refs/heads/{REF}")
        if rc:
            raise Refused(f"origin refused the push of {new[:12]} to {REF}: {why[-200:]}")
        rc, listed = git("ls-remote", "origin", f"refs/heads/{REF}")
        if rc or listed.split()[:1] != [new]:
            raise Refused(f"pushed {new[:12]} to {REF} and read back {(listed.split() or ['nothing'])[0][:12]}")
        out(f"PROMOTE {stamp} {old[:12] or 'absent'} -> {new[:12]} run={run.get('id')}")
    if held(read):
        out(f"PROMOTE-HELD {stamp} {old[:12] or 'absent'}: the newest {HELD_RUNS} concluded {BASE} runs past it read "
            "MACHINERY " + ", ".join(f"{i}={v}" for i, v in read[:HELD_RUNS]))
        return 3
    if run is None:
        out(f"PROMOTE-CURRENT {stamp} {old[:12] or 'absent'}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        import toolchain_selftest  # the cases live beside this file
        return toolchain_selftest.run()
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    b = sub.add_parser("behind")
    b.add_argument("dir", nargs="?", default=".")
    b.add_argument("--from", dest="frm", default="HEAD")
    b.add_argument("--all", dest="every", action="store_true")
    b.add_argument("--fetch", action="store_true")
    p = sub.add_parser("promote")
    p.add_argument("sha", nargs="?", default="")
    p.add_argument("--init", action="store_true")
    p.add_argument("--repo", required=True)
    p.add_argument("--dir", default=".")
    a = ap.parse_args(argv)
    try:
        if a.verb == "behind":
            print(behind(git_in(a.dir), a.frm, a.every, a.fetch))
            return 0
        return promote(git_in(a.dir), gh, a.repo, a.sha, create=a.init)
    except Refused as e:
        print(f"toolchain: REFUSED {e}", file=sys.stderr)
        return 1
    except Unreadable as e:
        print(f"toolchain: UNREADABLE {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
