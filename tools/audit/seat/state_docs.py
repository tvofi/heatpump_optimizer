#!/usr/bin/env python3
"""The state-doc pusher: regenerate the three handoff state docs in one call.

    python3 tools/audit/seat/state_docs.py [--repo OWNER/REPO] \
        [--roster-ref GITREF | --roster-file PATH] \
        [--checkout DIR] [--state-ref BR] [--pr-state FILE] \
        [--mirror DIR] [--push] [--message M]
    python3 tools/audit/seat/state_docs.py beat [the same flags] \
        [--watch-ref REF] [--interval SECONDS] [--tip-file PATH] [--once]
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

`beat` is the recurring half of tvofi's 2026-10-09 instruction that the state
docs are regenerated continuously rather than at session end. It replaces the
session-local loop an orchestrator kept in its own scratch directory, which is
decision 0013's defect shape: an instrument the programme runs, living outside
the tree where no later session can test it. A pass reads the watched ref at
origin; when it has moved it refreshes the roster ref (so resume fields another
seat wrote are visible), regenerates and pushes, and when it has not moved it
reads the ref and writes nothing else. The tip is recorded ONLY on a
regeneration that returned 0, so a refused push is retried on the next pass
instead of silently losing that merge from the record. It takes no lock and
cancels nothing, so it is safe beside a merge train. `--once` is one pass --
a caller looping that form needs `--tip-file`, the loop's memo kept on disk;
`--interval` is the sleep between passes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SELF = "tools/audit/seat/state_docs.py"
SEAT = Path(__file__).resolve().parent
STATE_REF = "handoff/audit-r9-plan"
STATE_DIR = "handoff/round9/state"
#: The beat's default watched ref and sleep. The tip a pass reads is a full
#: ref name, so a short name that happens to be a prefix matches nothing.
WATCH_REF = "refs/heads/main"
BEAT_INTERVAL = 300.0
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


def remote_tip(checkout: str, refspec: str) -> str | None:
    """The tip of `refspec` at origin, or None when the remote has no such ref.

    `refspec` is a FULL ref name -- `refs/heads/main`,
    `refs/heads/<state-ref>` -- because `ls-remote` treats a shorter one as a
    pattern: a name that is a prefix of another ref answers with the wrong tip
    and the beat would then see a move that never happened.
    """
    r = subprocess.run(["git", "-C", checkout, "ls-remote", "origin", refspec],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise Refuse(f"ls-remote origin {refspec} failed: "
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


# -------------------------------------------------------------------- the beat
def roster_fetch_spec(checkout: str, roster_ref: str) -> list[str] | None:
    """The `git fetch` argv that refreshes a remote-tracking `roster_ref`, or
    None when it is not one.

    Derived, never assumed: the remote is one `git remote` names and the ref
    is `<remote>/<branch>` or its full `refs/remotes/<remote>/<branch>` form.
    A local ref, or a bare sha, returns None -- there is nothing to refresh
    and the caller says so rather than guessing a remote. The refspec is
    spelled out instead of letting `remote.<name>.fetch` decide, so the ref
    the generators read afterwards is exactly the one this fetched.
    """
    name = roster_ref
    if name.startswith("refs/remotes/"):
        name = name[len("refs/remotes/"):]
    for remote in run(["git", "remote"], cwd=checkout).split():
        if name.startswith(remote + "/") and len(name) > len(remote) + 1:
            branch = name[len(remote) + 1:]
            return ["fetch", "-q", remote,
                    f"+{branch}:refs/remotes/{remote}/{branch}"]
    return None


def read_tip(path: str | None) -> str | None:
    """The recorded watch tip, or None -- also with no path, the loop's
    in-memory-only case (`--tip-file` is what carries it between passes)."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip() or None


def beat_main_argv(a) -> list:
    """The `main()` arguments one regeneration runs with: the beat's own
    inputs plus `--push`, because publishing the regeneration is what the
    manual loop this replaces already did. The watch ref, the interval and
    the tip file are the LOOP's and are never passed on."""
    argv = ["--repo", a.repo, "--checkout", a.checkout,
            "--state-ref", a.state_ref, "--push"]
    if a.roster_file:
        argv += ["--roster-file", a.roster_file]
    else:
        argv += ["--roster-ref", a.roster_ref]
    if a.pr_state:
        argv += ["--pr-state", a.pr_state]
    if a.mirror:
        argv += ["--mirror", a.mirror]
    return argv


def beat_pass(a, recorded: str | None) -> tuple[int, str | None]:
    """One pass: `(return code, the tip to record)`.

    An unchanged tip returns at once, having written nothing -- the pass
    costs one `ls-remote` and no generation at all. A moved tip refreshes
    the roster ref and regenerates through `main()`'s own guarded path.

    The tip is recorded on a 0 from `main()` ALONE: a refusal -- a failed
    generation or a push the remote rejected -- returns the tip that was
    already recorded, so the next pass still sees the ref as moved and
    retries, rather than losing that merge from the record.
    """
    tip = remote_tip(a.checkout, a.watch_ref)
    if tip is None:
        raise Refuse(f"origin has no {a.watch_ref}")
    if tip == recorded:
        print(f"beat: {a.watch_ref} at {tip[:12]} unchanged; nothing written")
        return 0, recorded
    if a.roster_file:
        print(f"beat: reading {a.roster_file}; nothing fetched")
    else:
        spec = roster_fetch_spec(a.checkout, a.roster_ref)
        if spec:
            run(["git", *spec], cwd=a.checkout)
            print(f"beat: fetched {a.roster_ref}")
        else:
            print(f"beat: {a.roster_ref} is not a remote-tracking ref; "
                  "nothing fetched")
    rc = main(beat_main_argv(a))
    if rc != 0:
        print(f"beat: {a.watch_ref} at {tip[:12]} not recorded (rc {rc}); "
              "the next pass retries", file=sys.stderr)
        return rc, recorded
    return 0, tip


def beat(a) -> int:
    """The recurring beat: one pass per change of the watched ref, forever --
    or exactly one with `--once`.

    It takes no lock and cancels nothing, so it is safe beside a merge train.
    The only state it keeps is the tip it has recorded, in memory and, when
    `--tip-file` names one, on disk, so a `--once` caller has the loop's memo
    across invocations. A refused pass is printed and retried at the next
    interval rather than ending the beat; `--once` returns that pass's code.
    """
    if a.self_test:
        return run_self_test()
    recorded = read_tip(a.tip_file)
    try:
        while True:
            try:
                rc, tip = beat_pass(a, recorded)
            except Refuse as e:
                print(f"beat: REFUSED: {e}", file=sys.stderr)
                rc, tip = 2, recorded
            if tip != recorded:
                if a.tip_file:
                    Path(a.tip_file).write_text(tip + "\n", encoding="utf-8")
                recorded = tip
            if a.once:
                return rc
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print("beat: stopped")
        return 0


def run_self_test() -> int:
    """The self-test under the throwaway-git environment.

    Every entry point goes through here, so a caller that is not `main()` --
    tests/entities.py loads this module by path and runs this -- gets the same
    guard against an inherited GIT_DIR or GIT_CONFIG_PARAMETERS that the
    command line gets.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_environ
    with throwaway_git_environ():
        return self_test()


# --------------------------------------------------------------------- main
def parser(beat_mode: bool = False) -> argparse.ArgumentParser:
    """One flag surface for both forms: `beat` adds only the loop's own
    inputs, so a flag the plain form has cannot drift out of the beat's."""
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
    if beat_mode:
        p.add_argument("--watch-ref", default=WATCH_REF,
                       help="the full ref name a pass reads at origin")
        p.add_argument("--interval", type=float, default=BEAT_INTERVAL,
                       help="seconds between passes (default 300)")
        p.add_argument("--tip-file",
                       help="file the recorded tip is kept in, so a --once "
                            "caller has the loop's memo across invocations")
        p.add_argument("--once", action="store_true",
                       help="one pass, then exit; the beat always pushes")
    return p


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["beat"]:
        return beat(parser(beat_mode=True).parse_args(argv[1:]))
    a = parser().parse_args(argv)
    if a.self_test:
        return run_self_test()
    roster_args = (["--roster-file", a.roster_file] if a.roster_file
                   else ["--roster-ref", a.roster_ref])
    try:
        with tempfile.TemporaryDirectory() as st:
            staged = generate(a.repo, roster_args, a.checkout, a.pr_state,
                              Path(st))
        for path in sorted(staged):
            print(f"generated {path}: "
                  f"{len(staged[path].encode('utf-8'))} bytes")
        prev = remote_tip(a.checkout, f"refs/heads/{a.state_ref}")
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
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_init
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
        throwaway_git_init(seed, "-q", "-b", "main")
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
        throwaway_git_clone(seed, bare, "-q", "--bare")
        git("-C", str(bare), "update-ref",
            f"refs/heads/{STATE_REF}", state0)
        drv = root / "drv"
        throwaway_git_clone(bare, drv, "-q")
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

    # --- the beat (R9-RO-14) -----------------------------------------------
    # The three arms the issue names, each driven through `beat --once` with
    # the tip file the loop keeps its memo in: a moved tip regenerates and
    # pushes exactly once, an unchanged tip writes nothing at all, and a
    # refused push leaves the tip unrecorded so the next pass retries. The
    # loop is `while True` around this same pass, so a mutation of the memo
    # check or of the record-on-zero rule turns one of them red.
    import shutil
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed = root / "seed"
        (seed / ".claude" / "workflows").mkdir(parents=True)
        roster = {
            "repo": "fixture/state", "session": "r9-fix", "groups": [
                {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
                 "after": [], "brief": "fixture group A does a thing.",
                 "resume": {"stage": "in-flight", "branch": "handoff/a",
                            "commit": "a" * 40}}]}
        roster_path = seed / ".claude" / "workflows" / "wave-r9-groups.json"

        def write_roster() -> None:
            roster_path.write_text(json.dumps(roster, indent=1) + "\n",
                                   encoding="utf-8")

        write_roster()
        throwaway_git_init(seed, "-q", "-b", "main")
        git("-C", str(seed), "add", "-A")
        git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
        # the roster's own branch: the ref the beat re-fetches
        git("-C", str(seed), "branch", "handoff/audit-r9-fixplan")
        # a state tip carrying a path the tool must carry, never drop
        env = dict(os.environ, GIT_INDEX_FILE=str(root / "beat-index"))
        git("read-tree", "--empty", cwd=str(seed), env=env)
        blob = git("hash-object", "-w", "--stdin", cwd=str(seed), env=env,
                   input_text="keep me\n").strip()
        git("update-index", "--add", "--cacheinfo",
            f"100644,{blob},docs/keep.md", cwd=str(seed), env=env)
        state0 = git("commit-tree", git("write-tree", cwd=str(seed), env=env),
                     "-m", "seed state", cwd=str(seed)).strip()
        bare = root / "origin.git"
        throwaway_git_clone(seed, bare, "-q", "--bare")
        git("-C", str(bare), "update-ref", f"refs/heads/{STATE_REF}", state0)
        drv = root / "beat-drv"
        throwaway_git_clone(bare, drv, "-q")
        prstate = root / "beat-prs.json"
        prstate.write_text(json.dumps(
            [{"number": 7, "head": "fix/y", "state": "OPEN"}]), encoding="utf-8")
        mirror = root / "beat-mirror"
        tipfile = root / "beat-tip"
        beat_argv = ["beat", "--checkout", str(drv), "--repo", "fixture/state",
                     "--roster-ref", "origin/handoff/audit-r9-fixplan",
                     "--state-ref", STATE_REF, "--pr-state", str(prstate),
                     "--mirror", str(mirror), "--tip-file", str(tipfile),
                     "--once"]

        def on_branch(branch: str) -> None:
            git("-C", str(seed), "checkout", "-q", branch)

        def commit_main(name: str) -> None:
            on_branch("main")
            (seed / "docs").mkdir(exist_ok=True)
            (seed / "docs" / name).write_text(f"{name}\n", encoding="utf-8")
            git("-C", str(seed), "add", "-A")
            git("-C", str(seed), "commit", "-q", "-m", name)
            git("-C", str(seed), "push", "-q", str(bare),
                "main:refs/heads/main")

        def commit_roster(stage: str) -> str:
            on_branch("handoff/audit-r9-fixplan")
            roster["groups"][0]["resume"]["stage"] = stage
            write_roster()
            git("-C", str(seed), "add", "-A")
            git("-C", str(seed), "commit", "-q", "-m", f"roster: {stage}")
            git("-C", str(seed), "push", "-q", str(bare),
                "handoff/audit-r9-fixplan:refs/heads/handoff/audit-r9-fixplan")
            return git("-C", str(seed), "rev-parse", "HEAD").strip()

        def main_tip() -> str:
            return git("-C", str(bare), "rev-parse", "refs/heads/main").strip()

        def state_tip() -> str:
            return git("-C", str(bare), "rev-parse",
                       f"refs/heads/{STATE_REF}").strip()

        def state_count() -> int:
            return len(git("-C", str(bare), "rev-list",
                           f"refs/heads/{STATE_REF}").split())

        # the fetch refresher, and the null controls that make its two
        # positives mean something: a local ref and a bare sha name no
        # remote, so neither fetches anything.
        fetched = ["fetch", "-q", "origin",
                   "+handoff/audit-r9-fixplan:"
                   "refs/remotes/origin/handoff/audit-r9-fixplan"]
        ok("the roster ref's fetch spec is derived from `git remote`",
           roster_fetch_spec(str(drv), "origin/handoff/audit-r9-fixplan")
           == fetched,
           roster_fetch_spec(str(drv), "origin/handoff/audit-r9-fixplan"))
        ok("and from the refs/remotes/ form of the same ref",
           roster_fetch_spec(str(drv),
                             "refs/remotes/origin/handoff/audit-r9-fixplan")
           == fetched)
        ok("null control: a local ref and a sha fetch nothing",
           roster_fetch_spec(str(drv), "main") is None
           and roster_fetch_spec(str(drv), "b" * 40) is None)

        # ARM 1 -- a moved tip regenerates and pushes exactly once, and the
        # push carries the roster edit only the RE-FETCH can deliver (drv's
        # copy of the roster ref is stale; the edit is on the remote alone).
        roster_sha = commit_roster("done")
        commit_main("main-1.md")
        ok("the driver's roster ref is stale before the pass",
           git("-C", str(drv), "rev-parse",
               "refs/remotes/origin/handoff/audit-r9-fixplan") != roster_sha)
        rc = main(beat_argv)
        ok("arm 1: a moved tip returns 0", rc == 0, rc)
        ok("arm 1: exactly one push, on the seed state tip",
           state_count() == 2, state_count())
        ok("arm 1: the pass re-fetched the roster ref",
           git("-C", str(drv), "rev-parse",
               "refs/remotes/origin/handoff/audit-r9-fixplan") == roster_sha)
        ok("arm 1: the pushed plan table carries the re-fetched roster",
           "done" in git("-C", str(bare), "show",
                         f"{state_tip()}:{WRITE_SET[0]}"))
        ok("arm 1: the carried path is still there",
           "docs/keep.md" in git("-C", str(bare), "ls-tree", "-r",
                                 "--name-only", state_tip()).split())
        ok("arm 1: the tip is recorded",
           tipfile.read_text(encoding="utf-8").strip() == main_tip())

        # ARM 2 -- an unchanged tip writes NOTHING. The roster moves on both
        # the remote and in the driver, so the bytes a regeneration would
        # produce differ from the tip's: a beat without the memo check
        # fetches, regenerates and pushes, and every assertion here fires.
        roster_sha = commit_roster("in-flight")
        git("-C", str(drv), "fetch", "-q", "origin", "handoff/audit-r9-fixplan")
        before = state_count()
        shutil.rmtree(mirror, ignore_errors=True)
        rc = main(beat_argv)
        ok("arm 2: an unchanged tip returns 0", rc == 0, rc)
        ok("arm 2: no push", state_count() == before, state_count())
        ok("arm 2: the tip stays what it was",
           tipfile.read_text(encoding="utf-8").strip() == main_tip())
        ok("arm 2: and nothing at all is written (the mirror is not made)",
           not mirror.exists())

        # ARM 3 -- a REFUSED push leaves the tip unrecorded, so the next pass
        # (same tip, nothing else moved) retries and lands it. The refusal is
        # the remote's own pre-receive hook, which rejects everything.
        commit_main("main-2.md")
        refused_tip = main_tip()
        hook = bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        before = state_count()
        rc = main(beat_argv)
        ok("arm 3: the refused push returns non-zero", rc == 2, rc)
        ok("arm 3: nothing landed", state_count() == before, state_count())
        ok("arm 3: the tip was NOT recorded",
           tipfile.read_text(encoding="utf-8").strip() != refused_tip)
        hook.unlink()
        rc = main(beat_argv)
        ok("arm 3: the retry lands, with nothing but the tip file changed",
           rc == 0, rc)
        ok("arm 3: exactly one push, on the retry",
           state_count() == before + 1, state_count())
        ok("arm 3: and only now is the tip recorded",
           tipfile.read_text(encoding="utf-8").strip() == refused_tip)

        # ARM 4 -- the LOOP, not a pass: `beat` with no --once, in a child, as
        # the orchestrator runs it. Two changes, each landed by the pass that
        # saw it, is what "continuously" means; a beat that exited after one
        # pass, or that never re-read the ref, fails the second wait. The
        # deadline is generous (a pass runs three generators) and the process
        # is terminated by the test, which is how this instrument is stopped.
        def wait_tip(want: str, seconds: float = 120.0) -> bool:
            end = time.time() + seconds
            while time.time() < end:
                if (tipfile.exists()
                        and tipfile.read_text(encoding="utf-8").strip() == want):
                    return True
                time.sleep(0.1)
            return False

        commit_main("main-3.md")
        loop = subprocess.Popen(
            [sys.executable, str(SEAT / "state_docs.py"),
             *beat_argv[:-1], "--interval", "0.05"],
            cwd=str(drv), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        try:
            ok("arm 4: the loop lands the first change it sees",
               wait_tip(main_tip()))
            commit_main("main-4.md")
            ok("arm 4: and beats again for the next one",
               wait_tip(main_tip()))
            ok("arm 4: and is still running, not one pass and out",
               loop.poll() is None)
        finally:
            loop.terminate()
            try:
                loop.wait(timeout=30)
            except subprocess.TimeoutExpired:
                loop.kill()
                loop.wait(timeout=30)

    if fails:
        print(f"{len(fails)} self-test check(s) failed: " + ", ".join(fails))
        return 1
    print("state_docs self-test: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
