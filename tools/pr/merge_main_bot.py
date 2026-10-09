#!/usr/bin/env python3
"""The merge-main bot: un-DIRTY a pull request whose only conflicts the merge
drivers resolve (R9-CI-2b; tvofi, 2026-10-08).

    python3 tools/pr/merge_main_bot.py run --repo OWNER/REPO --main SHA
        [--pushed-file PATH] [--dry-run]
    python3 tools/pr/merge_main_bot.py --self-test

WHY. GitHub computes `mergeStateStatus` with no merge driver, so a merge to
`main` that touched a driver file (`.gitattributes`' `merge=` lines:
tests/closures.json and the other ledgers, the two claim files) turns every
open pull request that touched it too DIRTY, and a DIRTY pull request runs no
CI at all (`claim-files.md`). Locally the drivers resolve those conflicts;
this does the same merge on GitHub's behalf, once per pull request per push
to `main`, and pushes it as `ci: merge main`.

IT PUSHES ONLY WHEN ALL OF THESE HOLD, and says which one failed otherwise:
  - the pull request is open, from this repository, and GitHub reports it
    unmergeable (`mergeable: false`) -- never a clean, behind or unknown one;
  - its head does not already contain the `main` it would merge;
  - git's own text merge (every driver replaced by `git merge-file`, which is
    what GitHub runs) conflicts, and ONLY on paths `main`'s .gitattributes
    routes to a driver -- any other conflicting path is a human's;
  - the real drivers then resolve every one of them: no conflict left, no
    `refused` marker on stderr;
  - the push is a fast-forward of the head it read (never forced): a head that
    moved since is left for the next push to `main`.

WHAT RUNS. Only `main`'s copies: the merge is `git merge-tree` in a checkout of
`main`, so the drivers it calls and the .gitattributes it reads are `main`'s,
and nothing from the pull request's tree executes in a job that can push. The
commit is `git commit-tree <tree> -p <head> -p <main>`, the same first-parent
shape as a seat's `git merge origin/main`, so `app_approve.sh --carry` judges
it as an automatic merge: a verdict carries over it without a re-review.

LOOP GUARD. It runs on a push to `main` only. Its own push lands on a pull
request branch, which no `push: main` trigger sees, and the head it pushes
contains `main`, so a second run on the same `main` finds nothing to do. The
other bots key their guards on their own subjects (`ci-autofix.md`); after
this commit they run as they would after a seat's merge.

--dry-run decides and prints every pull request's status, and pushes nothing.
`--pushed-file` gets one `<branch> <sha>` line per push, for the workflow's
dispatch and held-run approval steps.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = "ci: merge main"
BOT = ("github-actions[bot]", "41898282+github-actions[bot]@users.noreply.github.com")
#: What GitHub runs in a driver's place: git's own three-way text merge.
TEXT_MERGE = "git merge-file --quiet %A %O %B"
#: A branch name this job will write into a ref, a URL and a dispatch: the
#: pull request chose it, so anything else is skipped, never quoted.
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")


def git(repo: str, *args: str, env: dict | None = None,
        check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       env={**os.environ, **(env or {})})
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: rc={r.returncode} {r.stderr.strip()}")
    return r


def driver_paths(repo: str, ref: str) -> dict[str, str]:
    """`main`'s .gitattributes: path -> merge driver name."""
    r = git(repo, "show", f"{ref}:.gitattributes", check=False)
    out = {}
    for line in r.stdout.splitlines() if r.returncode == 0 else ():
        parts = line.split()
        if parts and not parts[0].startswith("#"):
            for a in parts[1:]:
                if a.startswith("merge="):
                    out[parts[0]] = a.split("=", 1)[1]
    return out


def merge_tree(repo: str, head: str, main: str,
               text_only: list[str] | None = None) -> tuple[int, str, list[str], str]:
    """(rc, tree, conflicting paths, stderr). `text_only` names the drivers to
    replace by git's text merge, which is the merge GitHub computes."""
    cfg = []
    for name in text_only or ():
        cfg += ["-c", f"merge.{name}.driver={TEXT_MERGE}"]
    r = git(repo, *cfg, "merge-tree", "--write-tree", "--name-only", "--no-messages",
            head, main, check=False)
    lines = r.stdout.splitlines()
    tree = lines[0] if lines else ""
    files = [l for l in lines[1:] if l.strip()] if r.returncode == 1 else []
    return r.returncode, tree, files, r.stderr


def decide(*, mergeable, same_repo: bool, contains_main: bool,
           text_conflicts: list[str], drivers: dict[str, str],
           driver_rc: int, driver_conflicts: list[str], driver_err: str) -> str:
    """One pull request's status; only `merge` pushes."""
    if not same_repo:
        return "skip-fork"
    if mergeable is not False:
        return "skip-not-dirty"
    if contains_main:
        return "skip-contains-main"
    if not text_conflicts:
        return "skip-no-text-conflict"
    other = sorted(set(text_conflicts) - set(drivers))
    if other:
        return "skip-other-conflict " + ",".join(other)
    if driver_rc != 0 or driver_conflicts or "refused" in driver_err.lower():
        return "skip-driver-refused " + ",".join(driver_conflicts or text_conflicts)
    return "merge"


def plan_one(repo: str, head: str, main: str, *, mergeable, same_repo: bool) -> tuple[str, str]:
    """(status, merge tree) for one head against `main`, in a checkout of `main`."""
    drivers = driver_paths(repo, main)
    contains = git(repo, "merge-base", "--is-ancestor", main, head, check=False).returncode == 0
    rc0, _, c0, _ = merge_tree(repo, head, main, text_only=sorted(set(drivers.values())))
    rc1, tree, c1, err1 = (1, "", [], "") if not c0 else merge_tree(repo, head, main)
    status = decide(mergeable=mergeable, same_repo=same_repo, contains_main=contains,
                    text_conflicts=c0, drivers=drivers, driver_rc=rc1,
                    driver_conflicts=c1, driver_err=err1)
    return status, tree


def commit_merge(repo: str, tree: str, head: str, main: str) -> str:
    env = {"GIT_AUTHOR_NAME": BOT[0], "GIT_AUTHOR_EMAIL": BOT[1],
           "GIT_COMMITTER_NAME": BOT[0], "GIT_COMMITTER_EMAIL": BOT[1]}
    # The message is the subject alone: pr-contract accepts a bot commit by its
    # exact message (policy_lint.mjs AUTOFIX_BOT_COMMITS).
    return git(repo, "commit-tree", tree, "-p", head, "-p", main, "-m", SUBJECT,
               env=env).stdout.strip()


def gh_json(path: str):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def mergeable_of(repo_slug: str, n: int, tries: int = 6, wait: float = 10.0):
    """GitHub computes `mergeable` lazily after a push to the base: None until it has."""
    for i in range(tries):
        pr = gh_json(f"repos/{repo_slug}/pulls/{n}")
        if pr.get("mergeable") is not None:
            return pr
        if i + 1 < tries:
            time.sleep(wait)
    return pr


def run(repo_slug: str, main: str, *, dry_run: bool, pushed_file: str | None,
        repo: str = ".") -> int:
    pushed = []
    prs = gh_json(f"repos/{repo_slug}/pulls?state=open&per_page=100")
    print(f"MERGE-MAIN: main {main}, {len(prs)} open pull request(s)")
    for p in prs:
        n, branch = p["number"], p["head"]["ref"]
        same = (p["head"].get("repo") or {}).get("full_name") == repo_slug
        if same and (not BRANCH.match(branch) or ".." in branch):
            print(f"MERGE-MAIN: #{n} skip-branch-name")
            continue
        try:
            pr = mergeable_of(repo_slug, n) if same else p
            head = pr["head"]["sha"]
            if same:
                git(repo, "fetch", "-q", "--no-tags", "origin", f"+refs/pull/{n}/head:refs/merge-main/{n}")
            status, tree = plan_one(repo, head, main, mergeable=pr.get("mergeable"),
                                    same_repo=same) if same else ("skip-fork", "")
        except (RuntimeError, KeyError) as why:
            print(f"MERGE-MAIN: #{n} skip-error {why}")
            continue
        if status != "merge":
            print(f"MERGE-MAIN: #{n} {status}")
            continue
        sha = commit_merge(repo, tree, head, main)
        if dry_run:
            print(f"MERGE-MAIN: #{n} merge (dry run, not pushed) {head[:12]} -> {sha[:12]}")
            continue
        auth = os.environ.get("PUSH_AUTH", "")
        cfg = ["-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}"] if auth else []
        r = git(repo, *cfg, "push", "-q", "origin", f"{sha}:refs/heads/{branch}", check=False)
        if r.returncode != 0:
            print(f"MERGE-MAIN: #{n} skip-push-refused (the head moved?) {r.stderr.strip()[-200:]}")
            continue
        print(f"MERGE-MAIN: #{n} pushed {head[:12]} -> {sha}")
        pushed.append(f"{branch} {sha}")
    if pushed_file:
        Path(pushed_file).write_text("".join(f"{l}\n" for l in pushed))
    print(f"MERGE-MAIN: {len(pushed)} pushed")
    return 0


def self_test() -> int:
    from throwaway_git import throwaway_git_init  # on sys.path: the --self-test arm
    fails, n = 0, 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal fails, n
        n += 1
        print(f"  {'ok  ' if cond else 'FAIL'} {name}" + ("" if cond else f"  [{detail}]"))
        fails += not cond

    base = dict(mergeable=False, same_repo=True, contains_main=False,
                text_conflicts=["led.json"], drivers={"led.json": "fake"},
                driver_rc=0, driver_conflicts=[], driver_err="")
    check("decide: a DIRTY head conflicting only on a driver file the driver resolves merges",
          decide(**base) == "merge")
    for name, change, want in (
            ("a clean head", {"mergeable": True}, "skip-not-dirty"),
            ("a head GitHub has not computed", {"mergeable": None}, "skip-not-dirty"),
            ("a fork", {"same_repo": False}, "skip-fork"),
            ("a head already containing main", {"contains_main": True}, "skip-contains-main"),
            ("a DIRTY head git's text merge does not conflict on", {"text_conflicts": []},
             "skip-no-text-conflict"),
            ("a conflict on a file no driver owns", {"text_conflicts": ["led.json", "a.py"]},
             "skip-other-conflict a.py"),
            ("a driver that refused", {"driver_err": "LEDGER-MERGE: refused led.json: x"},
             "skip-driver-refused led.json"),
            ("a driver that left a conflict", {"driver_rc": 1, "driver_conflicts": ["led.json"]},
             "skip-driver-refused led.json")):
        got = decide(**{**base, **change})
        check(f"decide: {name} is not pushed ({want})", got == want, got)

    with tempfile.TemporaryDirectory() as td:
        r = os.path.join(td, "r")
        # The shared helper, not a hand-rolled init: it drops the inherited
        # local layer, and writes maintenance.auto/gc.auto into the repository's
        # own config so a git call made without this env still reads them off.
        throwaway_git_init(r, "-q", "-b", "main")
        g = lambda *a, **k: git(r, *a, **k)
        # A driver that keeps both sides' lines, sorted: a stand-in for a ledger
        # driver that resolves what the text merge cannot.
        drv = os.path.join(td, "union.sh")
        Path(drv).write_text('#!/bin/sh\nsort -u "$2" "$3" -o "$2"\n')
        os.chmod(drv, 0o700)
        g("config", "merge.fake.driver", f"{drv} %O %A %B")
        Path(r, ".gitattributes").write_text("led.json merge=fake\n")
        Path(r, "led.json").write_text("a\nz\n")
        Path(r, "code.py").write_text("x = 1\n")
        g("add", "-A"); g("commit", "-qm", "m0")
        g("checkout", "-qb", "fix")
        Path(r, "led.json").write_text("a\nb\nz\n"); Path(r, "own.py").write_text("y\n")
        g("add", "-A"); g("commit", "-qm", "fix: own")
        fix = g("rev-parse", "HEAD").stdout.strip()
        g("checkout", "-q", "main")
        Path(r, "led.json").write_text("a\nc\nz\n"); g("commit", "-qam", "m1")
        m1 = g("rev-parse", "HEAD").stdout.strip()
        status, tree = plan_one(r, fix, m1, mergeable=False, same_repo=True)
        check("a ledger-only conflict the driver resolves is planned for a merge",
              status == "merge", status)
        sha = commit_merge(r, tree, fix, m1)
        parents = g("rev-list", "--parents", "-n1", sha).stdout.split()[1:]
        check("the commit is a merge of main into the head, first parent the head",
              parents == [fix, m1], repr(parents))
        check("its whole message is the subject pr-contract accepts",
              g("log", "-1", "--format=%B", sha).stdout.strip() == SUBJECT)
        check("its tree holds both sides' ledger lines and the branch's own file",
              g("show", f"{sha}:led.json").stdout == "a\nb\nc\nz\n"
              and g("show", f"{sha}:own.py").stdout == "y\n")
        check("its author is the Actions bot",
              g("log", "-1", "--format=%an", sha).stdout.strip() == BOT[0])
        # Null control: the same history with a code conflict beside it.
        g("checkout", "-q", "fix"); Path(r, "code.py").write_text("x = 2\n")
        g("commit", "-qam", "fix: code"); fix2 = g("rev-parse", "HEAD").stdout.strip()
        g("checkout", "-q", "main"); Path(r, "code.py").write_text("x = 3\n")
        g("commit", "-qam", "m2"); m2 = g("rev-parse", "HEAD").stdout.strip()
        status, _ = plan_one(r, fix2, m2, mergeable=False, same_repo=True)
        check("a code conflict beside the ledger one is left for a human (null control)",
              status == "skip-other-conflict code.py", status)
        # A driver that refuses: the text merge conflicts and so does the driver.
        Path(drv).write_text('#!/bin/sh\necho "LEDGER-MERGE: refused led.json: test" >&2\nexit 1\n')
        status, _ = plan_one(r, fix, m1, mergeable=False, same_repo=True)
        check("a ledger conflict its driver refuses is left for a human",
              status == "skip-driver-refused led.json", status)
        status, _ = plan_one(r, m1, m1, mergeable=False, same_repo=True)
        check("a head that already contains main is left alone",
              status == "skip-contains-main", status)
    # pr-contract accepts this commit by identity and exact message, held as
    # constants in policy_lint.mjs; drift between the two would turn every
    # bot merge into a red contract.
    pl = ROOT / "tools" / "policy" / "policy_lint.mjs"
    r = subprocess.run(["node", "--input-type=module", "-e",
                        f"import({json.dumps(pl.as_uri())}).then((m) => "
                        "console.log(JSON.stringify(m.AUTOFIX_BOT_COMMITS)))"],
                       capture_output=True, text=True)
    try:
        const = json.loads(r.stdout)
    except ValueError:
        const = {}
    check("pr-contract accepts this bot's identity and message as a merge",
          (const.get("name"), const.get("email")) == BOT
          and (const.get("messages", {}).get(SUBJECT) or {}).get("merge") is True,
          f"rc={r.returncode} {r.stderr.strip()[-200:]} {const}")
    for name, ok in (("fix/r9-ci-2b-pr", True), ("handoff/x.y_z", True), ("a;rm -rf", False),
                     ("$(id)", False), ("-x", False), ("a b", False)):
        check(f"branch {name!r} is {'accepted' if ok else 'skipped'}", bool(BRANCH.match(name)) == ok)
    print(f"merge_main_bot self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        # Every git call in the self-test, this runner's and the production
        # wrapper's under test, works in a throwaway repository: all of them
        # take the env layer, which a per-call env= cannot give the wrapper's
        # calls that pass none (tests/throwaway_git.py's docstring).
        sys.path.insert(0, str(ROOT / "tests"))
        from throwaway_git import throwaway_git_environ
        with throwaway_git_environ():
            return self_test()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--repo", required=True)
    r.add_argument("--main", required=True)
    r.add_argument("--pushed-file")
    r.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv[1:])
    if shutil.which("gh") is None:
        print("merge_main_bot: gh is not on PATH", file=sys.stderr)
        return 1
    return run(a.repo, a.main, dry_run=a.dry_run, pushed_file=a.pushed_file)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
