#!/usr/bin/env python3
"""The state-doc pusher: regenerate the three handoff state docs in one call.

    python3 tools/audit/seat/state_docs.py [--repo OWNER/REPO] \
        [--roster-ref GITREF | --roster-file PATH] \
        [--checkout DIR] [--state-ref BR] [--pr-state FILE] \
        [--mirror DIR] [--push] [--message M]
    python3 tools/audit/seat/state_docs.py --self-test

The loop the #1946 generators left open: run plan_table.py, resume_doc.py
and handover_prompt.py in order, commit exactly their outputs to the orphan
ref `handoff/audit-r9-plan` at handoff/round9/state/, and mirror the three
files to a local directory. Without --push it is a dry run: nothing remote
is written and it prints what it would push.

The write set is guarded the way record_row.py guards its rows: every path
the commit touches must be one of the three state docs, checked BEFORE any
commit exists to push. Every other path at the state ref's tip is carried
untouched -- the ref holds a round's evidence beside the state docs -- and
a tip whose content is already current is reported and left alone. The
commit is built with git plumbing over a TEMPORARY index (GIT_INDEX_FILE),
so the calling checkout's index is never touched, and the push shape is
body_push.sh's: commit-tree onto the ref's tip, parentless when the ref
does not exist yet, a fast-forward afterwards -- never a force.

Stateless like the other seat tools: every input is a flag, nothing about a
session or a machine is hardcoded, stdlib only, and the three generators
are RUN, never re-implemented -- their logic lives in exactly one place.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SELF = "tools/audit/seat/state_docs.py"
SEAT = Path(__file__).resolve().parent
STATE_REF = "handoff/audit-r9-plan"
STATE_DIR = "handoff/round9/state"
#: The WHOLE write surface. Every other path at the state ref's tip -- a
#: round's evidence, the older state docs -- is carried, never touched.
WRITE_SET = (
    STATE_DIR + "/PLAN-TABLE.md",
    STATE_DIR + "/RESUME-CURRENT.md",
    STATE_DIR + "/NEXT-SESSION-PROMPT.md",
)


class Refuse(Exception):
    """A guard refusal with its reason; the caller prints it, fail-closed."""


def run(cmd, cwd=None, env=None, input_text=None) -> str:
    r = subprocess.run(cmd, cwd=cwd, env=env, input=input_text,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise Refuse(f"{' '.join(cmd)} (in {cwd or '.'}) failed: "
                     f"{(r.stderr or r.stdout).strip()[:400]}")
    return r.stdout


# ----------------------------------------------------------------- generate
def generate(repo: str, roster_args: list, checkout: str, pr_state: str,
             staging: Path) -> dict:
    """Run the three #1946 generators, in order, into staging.

    Returns {repo path: text} keyed by the write-set paths. The generators
    are subprocesses with their own flags -- never copied logic. The
    next-session prompt takes no --resume: ready-next derives from the
    roster, the same hand run that wrote the live state docs (a --resume
    path would embed a scratch path in the committed doc and break the
    already-current check).
    """
    resume_flags = (["--offline", "--pr-state", pr_state]
                    if pr_state else [])
    plan = [
        ("plan_table.py", "PLAN-TABLE.md", []),
        ("resume_doc.py", "RESUME-CURRENT.md", resume_flags),
        ("handover_prompt.py", "NEXT-SESSION-PROMPT.md", []),
    ]
    out: dict = {}
    for script, name, extra in plan:
        target = staging / name
        cmd = [sys.executable, str(SEAT / script), "--repo", repo, *roster_args,
               "--out", str(target), *extra]
        r = subprocess.run(cmd, cwd=checkout, capture_output=True, text=True)
        if r.returncode != 0:
            raise Refuse(f"{script} failed rc {r.returncode}: "
                         f"{(r.stderr or r.stdout).strip()[:400]}")
        if not target.exists() or not target.read_text(encoding="utf-8").strip():
            raise Refuse(f"{script} produced no {name}")
        text = target.read_text(encoding="utf-8")
        out[f"{STATE_DIR}/{name}"] = text
    return out


# ------------------------------------------------------------------ the tree
def check_write_set(staged: dict) -> None:
    """The guarded write set, record_row's shape: anything outside the three
    state docs is refused, never skipped."""
    bad = sorted(p for p in staged if p not in WRITE_SET)
    if bad:
        raise Refuse(
            f"outside the state-doc write set: {', '.join(bad)} -- the write "
            f"set is exactly {', '.join(WRITE_SET)}; every other path at the "
            "state ref is carried untouched, never written")


def write_tree(checkout: str, staged: dict, prev: str | None) -> str:
    """Build the state commit's tree over a TEMP index; returns the tree sha.

    `prev` is the state ref's current tip (None before the ref exists): its
    tree is read first, so every path this commit does not touch is carried
    exactly as it was. The temp index keeps the calling checkout's own index
    untouched. The guard runs before anything is staged.
    """
    check_write_set(staged)
    with tempfile.TemporaryDirectory() as t:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(t) / "index"))
        if prev:
            run(["git", "read-tree", prev], cwd=checkout, env=env)
        else:
            run(["git", "read-tree", "--empty"], cwd=checkout, env=env)
        for path in sorted(staged):
            blob = run(["git", "hash-object", "-w", "--stdin"], cwd=checkout,
                       env=env, input_text=staged[path]).strip()
            run(["git", "update-index", "--add", "--cacheinfo",
                 f"100644,{blob},{path}"], cwd=checkout, env=env)
        return run(["git", "write-tree"], cwd=checkout, env=env).strip()


def remote_tip(checkout: str, state_ref: str) -> str | None:
    """The state ref's tip at origin, or None when the ref does not exist."""
    r = subprocess.run(["git", "-C", checkout, "ls-remote", "origin",
                        f"refs/heads/{state_ref}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise Refuse(f"ls-remote origin {state_ref} failed: "
                     f"{(r.stderr or r.stdout).strip()[:200]}")
    out = r.stdout.strip()
    return out.split()[0] if out else None


def mirror_files(staged: dict, mirror: str | None) -> None:
    if not mirror:
        return
    mdir = Path(mirror)
    mdir.mkdir(parents=True, exist_ok=True)
    for path in sorted(staged):
        (mdir / Path(path).name).write_text(staged[path], encoding="utf-8")
        print(f"mirrored {path} -> {mdir / Path(path).name}")


# --------------------------------------------------------------------- main
def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--repo", default="tvofi/heatpump_optimizer")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--roster-ref", default="origin/handoff/audit-r9-fixplan")
    src.add_argument("--roster-file")
    p.add_argument("--checkout", default=".",
                   help="the clone the git operations and generators run in")
    p.add_argument("--state-ref", default=STATE_REF,
                   help="the orphan ref the state docs are committed to")
    p.add_argument("--pr-state",
                   help="JSON list of open pull requests; passed to "
                        "resume_doc with --offline (no network, no gh)")
    p.add_argument("--mirror", help="directory the three files are copied to")
    p.add_argument("--push", action="store_true",
                   help="push the state ref; without it this is a dry run")
    p.add_argument("--message")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    roster_args = (["--roster-file", a.roster_file] if a.roster_file
                   else ["--roster-ref", a.roster_ref])
    try:
        with tempfile.TemporaryDirectory() as st:
            staged = generate(a.repo, roster_args, a.checkout, a.pr_state,
                              Path(st))
        for path in sorted(staged):
            print(f"generated {path}: "
                  f"{len(staged[path].encode('utf-8'))} bytes")
        prev = remote_tip(a.checkout, a.state_ref)
        tree = write_tree(a.checkout, staged, prev)
        if prev:
            changed = run(["git", "diff-tree", "-r", "--name-only", prev,
                           tree], cwd=a.checkout).split()
            bad = sorted(p for p in changed if p not in WRITE_SET)
            if bad:  # unreachable while write_tree's guard holds; checked
                raise Refuse(  # again here, before any commit exists to push
                    f"the commit would touch paths outside the write set: "
                    f"{', '.join(bad)}")
            if not changed:
                print(f"already current: {a.state_ref} at {prev[:12]} carries "
                      "these bytes; nothing to commit or push")
                mirror_files(staged, a.mirror)
                return 0
        else:
            names = run(["git", "ls-tree", "-r", "--name-only", tree],
                        cwd=a.checkout).split()
            if sorted(names) != sorted(WRITE_SET):
                raise Refuse(f"the first commit on {a.state_ref} would carry "
                             f"{sorted(names)}, not exactly the write set")
        message = a.message or (
            "state: " + ", ".join(Path(p).name for p in sorted(staged))
            + " regenerated (state_docs.py)")
        cargs = ["git", "commit-tree", tree]
        if prev:
            cargs += ["-p", prev]
        commit = run(cargs + ["-m", message], cwd=a.checkout).strip()
        if a.push:
            run(["git", "push", "-q", "origin",
                 f"{commit}:refs/heads/{a.state_ref}"], cwd=a.checkout)
            print(f"pushed {a.state_ref} at {commit}")
        else:
            print(f"ready: would push {a.state_ref} at {commit} (no --push)")
        mirror_files(staged, a.mirror)
        return 0
    except Refuse as e:
        print(f"state_docs: REFUSED: {e}", file=sys.stderr)
        return 2


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    """Offline: tmp dirs and fixture repos, no network in any arm."""
    fails: list[str] = []

    def ok(name: str, cond, got="") -> None:
        if not cond:
            fails.append(f"{name} (got: {got})")

    def git(*args, cwd=None, env=None, input_text=None) -> str:
        return run(["git", *args], cwd=cwd, env=env,
                   input_text=input_text).strip()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # the fixture roster and checkout
        seed = root / "seed"
        (seed / ".claude" / "workflows").mkdir(parents=True)
        roster = {
            "repo": "fixture/state", "session": "r9-fix", "groups": [
                {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
                 "after": [], "brief": "fixture group A does a thing.",
                 "resume": {"stage": "in-flight", "branch": "handoff/a",
                            "commit": "a" * 40,
                            "last_step": "fixer handed off",
                            "next_step": "review"}},
                {"group": "R9-B", "lane": "L1", "issues": [], "fixes": [],
                 "after": ["R9-A"], "brief": "fixture group B waits on A.",
                 "resume": {"stage": "not-started", "branch": "handoff/b"}},
            ]}
        roster_path = seed / ".claude" / "workflows" / "wave-r9-groups.json"
        roster_path.write_text(json.dumps(roster, indent=1) + "\n",
                               encoding="utf-8")
        git("init", "-q", "-b", "main", str(seed))
        git("-C", str(seed), "add", "-A")
        git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
        # a state tip with an unrelated path the tool must carry, never drop
        env = dict(os.environ,
                   GIT_INDEX_FILE=str(root / "seed-index"))
        git("read-tree", "--empty", cwd=str(seed), env=env)
        blob = git("hash-object", "-w", "--stdin", cwd=str(seed), env=env,
                   input_text="keep me\n").strip()
        git("update-index", "--add", "--cacheinfo",
            f"100644,{blob},docs/keep.md", cwd=str(seed), env=env)
        state0 = git("commit-tree", git("write-tree", cwd=str(seed), env=env),
                     "-m", "seed state", cwd=str(seed)).strip()
        bare = root / "origin.git"
        git("clone", "-q", "--bare", str(seed), str(bare))
        git("-C", str(bare), "update-ref",
            f"refs/heads/{STATE_REF}", state0)
        drv = root / "drv"
        git("clone", "-q", str(bare), str(drv))
        prstate = root / "prs.json"
        prstate.write_text(json.dumps(
            [{"number": 1234, "head": "fix/x", "state": "OPEN"}]),
            encoding="utf-8")
        mirror = root / "mirror"
        common = ["--checkout", str(drv), "--roster-file", str(roster_path),
                  "--pr-state", str(prstate), "--mirror", str(mirror)]

        def tip_at_origin() -> str:
            return git("-C", str(bare), "rev-parse",
                       f"refs/heads/{STATE_REF}").strip()

        # the dry run: everything but the push
        rc = main(common)
        ok("dry run rc 0", rc == 0, rc)
        ok("dry run moved nothing", tip_at_origin() == state0)
        # the push: exactly the write set changes, docs/keep.md is carried
        rc = main(common + ["--push"])
        ok("push rc 0", rc == 0, rc)
        tip = tip_at_origin()
        ok("pushed a new commit", tip != state0)
        names = git("-C", str(bare), "ls-tree", "-r", "--name-only",
                    tip).split()
        ok("write set exact, carried path kept",
           sorted(names) == sorted([*WRITE_SET, "docs/keep.md"]), names)
        show = lambda path: git("-C", str(bare), "show", f"{tip}:{path}")
        ok("plan table generated", "Swimlanes" in show(WRITE_SET[0]))
        ok("resume generated", "## Roster" in show(WRITE_SET[1]))
        ok("prompt generated", "Next-session prompt" in show(WRITE_SET[2])
           and "R9-A" in show(WRITE_SET[2]))
        ok("mirror carries exactly the three files",
           sorted(p.name for p in mirror.iterdir())
           == sorted(Path(p).name for p in WRITE_SET))
        ok("parent is the previous tip",
           state0 in git("-C", str(bare), "log", "--format=%P", "-1", tip))
        # THE GUARD: a write outside the three files refuses, in both the
        # direct check and a real write_tree call over the live tip.
        try:
            check_write_set({"dev/programme/HANDOVER.md": "x", WRITE_SET[0]: "ok"})
            ok("guard refuses a path outside the write set", False)
        except Refuse:
            pass
        try:
            write_tree(str(drv), {**{p: "x" for p in WRITE_SET},
                                  "dev/programme/HANDOVER.md": "x"}, tip)
            ok("write_tree refuses an outside path", False)
        except Refuse:
            pass
        ok("guard refused before the tree carried the bad path",
           "dev/programme/HANDOVER.md" not in git("-C", str(drv), "ls-tree", "-r",
                                         "--name-only", "HEAD"))
        # idempotence: a re-run over a current tip moves nothing
        rc = main(common + ["--push"])
        ok("re-run rc 0", rc == 0, rc)
        ok("re-run moved nothing", tip_at_origin() == tip)
        # a roster change regenerates and lands a new commit
        roster["groups"][0]["resume"]["stage"] = "done"
        roster_path.write_text(json.dumps(roster, indent=1) + "\n",
                               encoding="utf-8")
        rc = main(common + ["--push"])
        ok("changed roster pushes", rc == 0 and tip_at_origin() != tip, rc)
        ok("plan table reflects the roster",
           "done" in git("-C", str(bare), "show",
                         f"{tip_at_origin()}:{WRITE_SET[0]}"))

    if fails:
        print(f"{len(fails)} self-test check(s) failed: " + ", ".join(fails))
        return 1
    print("state_docs self-test: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
