#!/usr/bin/env python3
"""The state-doc pusher: regenerate the three handoff state docs in one call.

    python3 tools/audit/seat/state_docs.py [--repo OWNER/REPO] \
        [--roster-ref GITREF [--roster-path PATH] | --roster-file PATH] \
        [--checkout DIR] [--state-ref BR] [--pr-state FILE] \
        [--mirror DIR] [--push] [--message M]
    python3 tools/audit/seat/state_docs.py beat [the same flags] \
        [--watch-ref REF] [--interval SECONDS] [--tip-file PATH] [--once]
    python3 tools/audit/seat/state_docs.py --self-test

The loop the #1946 generators left open: run plan_table.py, resume_doc.py
and handover_prompt.py in order, commit exactly their outputs to the orphan
ref `handoff/audit-r<N>-plan` at handoff/round<N>/state/, and mirror the three
files to a local directory. Without --push it is a dry run: nothing remote
is written and it prints what it would push. N is the ROSTER's round, never a
constant here: the round `roster_lib.roster_path` picks (the newest
`dev/programme/rosters/wave-r<N>-groups.json` at --roster-ref, or
--roster-path) or the one --roster-file's name carries. A roster whose round
cannot be read is refused, so a round-10 beat cannot write round 9's state.

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
the tree where no later session can test it. A pass reads the watched ref and
the roster ref at origin; when either has moved it refreshes the roster ref (so
resume fields another seat wrote are visible), regenerates and pushes, and when
neither has it writes nothing. With no --roster-ref the roster ref is
`roster_lib.default_roster_ref`'s: the round's roster branch, else main. The tip is recorded ONLY on a
regeneration that returned 0, so a refused push is retried on the next pass
instead of silently losing that merge from the record. It takes no lock and
cancels nothing, so it is safe beside a merge train. `--once` is one pass --
a caller looping that form needs `--tip-file`, the loop's memo kept on disk;
`--interval` is the sleep between passes.

`beat --apply` runs the roster-sync step (`roster_sync.py`) at the START of
every pass, before the memo check, so an open pull request that moved no ref
is still recorded: the repository-measured half of `resume.stage` is derived
(MERGED -> done at the merge commit, OPEN -> in-progress) and written through
`roster_edit.py`'s lint gate. Without `--apply` the beat derives nothing; a
dry run per interval would print the same lines forever, so the dry-run form
is `roster_sync.py`'s own. A sync that writes moves the roster ref, and the
pass then regenerates the docs for it; a sync that refuses (an unreadable
`gh` read) is not recorded, so the next pass retries it.
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
from typing import NamedTuple

SELF = "tools/audit/seat/state_docs.py"
SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(SEAT))
import roster_lib  # noqa: E402  which roster, hence which round
import ref_privacy  # noqa: E402  a ref or message never names this host (#2310)
import roster_sync  # noqa: E402  the roster-sync step `beat --apply` runs
#: The beat's default watched ref and sleep. The tip a pass reads is a full
#: ref name, so a short name that happens to be a prefix matches nothing.
WATCH_REF = "refs/heads/main"
BEAT_INTERVAL = 300.0
#: The three docs, one per generator. Under a round's state dir they are the
#: WHOLE write surface: every other path at the state ref's tip -- a round's
#: evidence, the older state docs -- is carried, never touched.
DOC_NAMES = ("PLAN-TABLE.md", "RESUME-CURRENT.md", "NEXT-SESSION-PROMPT.md")


class State(NamedTuple):
    ref: str
    dir: str
    write_set: tuple


def state_of(round_n: int) -> State:
    """A round's state ref, dir and write set, derived from its number."""
    d = f"handoff/round{round_n}/state"
    return State(f"handoff/audit-r{round_n}-plan", d,
                 tuple(f"{d}/{n}" for n in DOC_NAMES))


def roster_round_of(a) -> int:
    """The round of the roster this run reads: --roster-file's name, else
    roster_lib's pick at --roster-ref (or --roster-path). Refuses when there
    is none, rather than defaulting to some round."""
    try:
        if a.roster_file:
            return roster_lib.roster_round(a.roster_file)
        return roster_lib.roster_round(roster_lib.roster_path(
            a.checkout, a.roster_ref, a.roster_path))
    except roster_lib.RosterNotFound as e:
        raise Refuse(f"which round: {e}")


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
             staging: Path, state_dir: str) -> dict:
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
        out[f"{state_dir}/{name}"] = text
    return out


# ------------------------------------------------------------------ the tree
def check_write_set(staged: dict, write_set: tuple) -> None:
    """The guarded write set, record_row's shape: anything outside the three
    state docs is refused, never skipped."""
    bad = sorted(p for p in staged if p not in write_set)
    if bad:
        raise Refuse(
            f"outside the state-doc write set: {', '.join(bad)} -- the write "
            f"set is exactly {', '.join(write_set)}; every other path at the "
            "state ref is carried untouched, never written")


def write_tree(checkout: str, staged: dict, prev: str | None,
               write_set: tuple) -> str:
    """Build the state commit's tree over a TEMP index; returns the tree sha.

    `prev` is the state ref's current tip (None before the ref exists): its
    tree is read first, so every path this commit does not touch is carried
    exactly as it was. The temp index keeps the calling checkout's own index
    untouched. The guard runs before anything is staged.
    """
    check_write_set(staged, write_set)
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
    argv = ["--repo", a.repo, "--checkout", a.checkout, "--push"]
    if a.state_ref:
        argv += ["--state-ref", a.state_ref]
    if a.roster_file:
        argv += ["--roster-file", a.roster_file]
    else:
        if a.roster_ref:  # else main() resolves roster_lib's default
            argv += ["--roster-ref", a.roster_ref]
        if a.roster_path:
            argv += ["--roster-path", a.roster_path]
    if a.pr_state:
        argv += ["--pr-state", a.pr_state]
    if a.mirror:
        argv += ["--mirror", a.mirror]
    return argv


def sync_pass(a) -> int:
    """The roster-sync step a `--apply` beat runs each pass.

    Only the repository-measured half of the roster: merged -> done at the
    merge commit, open -> in-progress, a merged body's `Carry: <group>` items
    appended. It goes through roster_sync's own write path -- roster_edit's
    ops, dump and lint gate -- so the beat owns the cadence, never a second
    derivation. Without `--apply` the beat derives nothing: a dry run per
    interval would print the same lines forever, so the dry-run form is
    roster_sync.py's own.
    """
    argv = ["--repo", a.repo, "--checkout", a.checkout, "--apply"]
    if a.roster_file:
        argv += ["--roster-file", a.roster_file]
    else:
        if a.roster_ref:  # else roster_sync's default: main, round branch
            argv += ["--roster-ref", a.roster_ref]
        if a.roster_path:
            argv += ["--roster-path", a.roster_path]
    if a.pr_state:
        argv += ["--pr-state", a.pr_state]
    return roster_sync.main(argv)


def beat_pass(a, recorded: str | None) -> tuple[int, str | None]:
    """One pass: `(return code, the tip to record)`.

    An unchanged tip returns at once, having written nothing -- the pass
    costs one `ls-remote` and no generation at all. A moved tip refreshes
    the roster ref and regenerates through `main()`'s own guarded path.

    With `--apply` the roster-sync step runs FIRST, every pass, because a
    pull request can be opened or merged without moving a ref the pass reads:
    the memo check below would never see it. A sync that wrote moves the
    roster ref, so this pass regenerates the docs for it; a sync refusal is
    not recorded, and the next pass retries it.

    The tip is recorded on a 0 from `main()` ALONE: a refusal -- a failed
    generation or a push the remote rejected -- returns the tip that was
    already recorded, so the next pass still sees the ref as moved and
    retries, rather than losing that merge from the record.
    """
    if a.apply:
        rc = sync_pass(a)
        if rc != 0:
            print(f"beat: roster-sync returned {rc}; nothing recorded, the "
                  "next pass retries", file=sys.stderr)
            return rc, recorded
    tip = remote_tip(a.checkout, a.watch_ref)
    if tip is None:
        raise Refuse(f"origin has no {a.watch_ref}")
    # The roster ref is watched too (O17): its edits move the state docs as
    # main's merges do. With no --roster-ref it is the round's roster branch
    # (roster_lib), named from main's newest roster; the memo is both tips.
    roster_ref = None if a.roster_file else (
        a.roster_ref or roster_lib.round_ref(roster_lib.git_in(a.checkout)))
    spec = roster_fetch_spec(a.checkout, roster_ref) if roster_ref else None
    # spec[3] is fetch's `+<branch>:refs/remotes/<remote>/<branch>` refspec.
    rtip = remote_tip(a.checkout,
                      "refs/heads/" + spec[3].split(":", 1)[0].lstrip("+")) \
        if spec else None
    memo = f"{tip} {rtip}" if rtip else tip
    if memo == recorded:
        print(f"beat: {a.watch_ref} at {tip[:12]}"
              + (f" and {roster_ref} at {rtip[:12]}" if rtip else "")
              + " unchanged; nothing written")
        return 0, recorded
    if a.roster_file:
        print(f"beat: reading {a.roster_file}; nothing fetched")
    elif rtip:
        run(["git", *spec], cwd=a.checkout)
        print(f"beat: fetched {roster_ref}")
    else:
        print(f"beat: {roster_ref} is not a remote-tracking ref origin has; "
              "nothing fetched")
    rc = main(beat_main_argv(a))
    if rc != 0:
        print(f"beat: {a.watch_ref} at {tip[:12]} not recorded (rc {rc}); "
              "the next pass retries", file=sys.stderr)
        return rc, recorded
    return 0, memo


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
    if a.apply and a.roster_file:
        print("state_docs: REFUSED: --apply needs a branch to write; "
              "--roster-file is a read-only source", file=sys.stderr)
        return 2
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
    src.add_argument("--roster-ref", default=None,
                     help="default: the round roster branch, else origin/main "
                          "(roster_lib.default_roster_ref)")
    src.add_argument("--roster-file")
    p.add_argument("--roster-path",
                   help="the roster at --roster-ref (default: the newest "
                        "dev/programme/rosters/wave-r<N>-groups.json there)")
    p.add_argument("--checkout", default=".",
                   help="the clone the git operations and generators run in")
    p.add_argument("--state-ref", default=None,
                   help="the orphan ref the state docs are committed to "
                        "(default handoff/audit-r<N>-plan, N the roster's "
                        "round)")
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
        p.add_argument("--apply", action="store_true",
                       help="run the roster-sync step each pass and write its "
                            "derived changes (roster_sync.py owns the dry run)")
    return p


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["beat"]:
        return beat(parser(beat_mode=True).parse_args(argv[1:]))
    a = parser().parse_args(argv)
    if a.self_test:
        return run_self_test()
    if a.roster_file and a.roster_path:
        print("state_docs: REFUSED: --roster-path reads at --roster-ref; "
              "give --roster-file alone", file=sys.stderr)
        return 2
    if not a.roster_file:
        a.roster_ref = roster_lib.reader_ref(a.checkout, a.roster_ref)
    roster_args = (["--roster-file", a.roster_file] if a.roster_file
                   else ["--roster-ref", a.roster_ref]
                   + (["--roster-path", a.roster_path] if a.roster_path
                      else []))
    try:
        st8 = state_of(roster_round_of(a))
        state_ref = a.state_ref or st8.ref
        print(f"round state: {state_ref} at {st8.dir}/")
        with tempfile.TemporaryDirectory() as st:
            staged = generate(a.repo, roster_args, a.checkout, a.pr_state,
                              Path(st), st8.dir)
        for path in sorted(staged):
            print(f"generated {path}: "
                  f"{len(staged[path].encode('utf-8'))} bytes")
        prev = remote_tip(a.checkout, f"refs/heads/{state_ref}")
        tree = write_tree(a.checkout, staged, prev, st8.write_set)
        if prev:
            changed = run(["git", "diff-tree", "-r", "--name-only", prev,
                           tree], cwd=a.checkout).split()
            bad = sorted(p for p in changed if p not in st8.write_set)
            if bad:  # unreachable while write_tree's guard holds; checked
                raise Refuse(  # again here, before any commit exists to push
                    f"the commit would touch paths outside the write set: "
                    f"{', '.join(bad)}")
            if not changed:
                print(f"already current: {state_ref} at {prev[:12]} carries "
                      "these bytes; nothing to commit or push")
                mirror_files(staged, a.mirror)
                return 0
        else:
            names = run(["git", "ls-tree", "-r", "--name-only", tree],
                        cwd=a.checkout).split()
            if sorted(names) != sorted(st8.write_set):
                raise Refuse(f"the first commit on {state_ref} would carry "
                             f"{sorted(names)}, not exactly the write set")
        message = a.message or (
            "state: " + ", ".join(Path(p).name for p in sorted(staged))
            + " regenerated (state_docs.py)")
        why = ref_privacy.refusal(state_ref, (("the message", message),))
        if why:
            raise Refuse(f"{why} would publish this host (#2310); nothing committed")
        cargs = ["git", "commit-tree", tree]
        if prev:
            cargs += ["-p", prev]
        commit = run(cargs + ["-m", message], cwd=a.checkout).strip()
        if a.push:
            run(["git", "push", "-q", "origin",
                 f"{commit}:refs/heads/{state_ref}"], cwd=a.checkout)
            print(f"pushed {state_ref} at {commit}")
        else:
            print(f"ready: would push {state_ref} at {commit} (no --push)")
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
    # The fixtures are round 9's: the roster files below are named
    # wave-r9-groups.json, so the derived state is round 9's.
    STATE_REF, _, WRITE_SET = state_of(9)

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
            check_write_set({"dev/programme/HANDOVER.md": "x", WRITE_SET[0]: "ok"},
                            WRITE_SET)
            ok("guard refuses a path outside the write set", False)
        except Refuse:
            pass
        try:
            write_tree(str(drv), {**{p: "x" for p in WRITE_SET},
                                  "dev/programme/HANDOVER.md": "x"}, tip,
                       WRITE_SET)
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
        # a message naming a host path refuses (#2310); the push below is its null
        rc = main(common + ["--push", "--message", "state: from /Users/" + "exampleuser/x"])
        ok("a message naming a host path refuses and pushes nothing",
           rc != 0 and tip_at_origin() == tip, rc)
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
        (seed / roster_lib.ROSTERS_DIR).mkdir(parents=True)
        roster = {
            "repo": "fixture/state", "session": "r9-fix", "groups": [
                {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
                 "after": [], "brief": "fixture group A does a thing.",
                 "resume": {"stage": "in-flight", "branch": "handoff/a",
                            "commit": "a" * 40}}]}
        roster_path = seed / roster_lib.ROSTERS_DIR / "wave-r9-groups.json"

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

        def memo() -> str:
            """What the beat records: main's tip and the roster ref's (O17)."""
            return main_tip() + " " + git(
                "-C", str(bare), "rev-parse",
                "refs/heads/handoff/audit-r9-fixplan").strip()

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
        ok("arm 1: the tip is recorded, main's and the roster ref's",
           tipfile.read_text(encoding="utf-8").strip() == memo(),
           tipfile.read_text(encoding="utf-8").strip())

        # ARM 2 -- an unchanged tip writes NOTHING. Neither main nor the
        # roster ref moved, and the mirror is removed, so a beat without the
        # memo check regenerates, re-mirrors and every assertion here fires.
        before = state_count()
        shutil.rmtree(mirror, ignore_errors=True)
        rc = main(beat_argv)
        ok("arm 2: an unchanged tip returns 0", rc == 0, rc)
        ok("arm 2: no push", state_count() == before, state_count())
        ok("arm 2: the tip stays what it was",
           tipfile.read_text(encoding="utf-8").strip() == memo())
        ok("arm 2: and nothing at all is written (the mirror is not made)",
           not mirror.exists())

        # ARM 2b (O17) -- the ROSTER REF moving alone regenerates: main is
        # unchanged, so a beat that watched main only (before O17) writes
        # nothing and the published plan keeps the old stage.
        roster_sha = commit_roster("in-flight")
        before = state_count()
        rc = main(beat_argv)
        ok("arm 2b: a roster-only move returns 0", rc == 0, rc)
        ok("arm 2b: exactly one push", state_count() == before + 1,
           state_count())
        ok("arm 2b: the pushed plan carries the roster's new stage",
           "in-flight" in git("-C", str(bare), "show",
                              f"{state_tip()}:{WRITE_SET[0]}"))
        ok("arm 2b: and the memo now names the roster's new tip",
           tipfile.read_text(encoding="utf-8").strip() == memo())

        # ARM 3 -- a REFUSED push leaves the tip unrecorded, so the next pass
        # (same tip, nothing else moved) retries and lands it. The refusal is
        # the remote's own pre-receive hook, which rejects everything.
        commit_main("main-2.md")
        # A roster edit too, so the regeneration differs from arm 2b's
        # published bytes and a push is really attempted.
        commit_roster("refused-then-landed")
        refused_memo = memo()
        hook = bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        before = state_count()
        rc = main(beat_argv)
        ok("arm 3: the refused push returns non-zero", rc == 2, rc)
        ok("arm 3: nothing landed", state_count() == before, state_count())
        ok("arm 3: the tip was NOT recorded",
           tipfile.read_text(encoding="utf-8").strip() != refused_memo)
        hook.unlink()
        rc = main(beat_argv)
        ok("arm 3: the retry lands, with nothing but the tip file changed",
           rc == 0, rc)
        ok("arm 3: exactly one push, on the retry",
           state_count() == before + 1, state_count())
        ok("arm 3: and only now is the tip recorded",
           tipfile.read_text(encoding="utf-8").strip() == refused_memo)

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
               wait_tip(memo()))
            commit_main("main-4.md")
            ok("arm 4: and beats again for the next one",
               wait_tip(memo()))
            ok("arm 4: and is still running, not one pass and out",
               loop.poll() is None)
        finally:
            loop.terminate()
            try:
                loop.wait(timeout=30)
            except subprocess.TimeoutExpired:
                loop.kill()
                loop.wait(timeout=30)

        # ARM 5 (O17) -- no --roster-ref: every generator, run standalone in
        # the driver, reads the ROUND's roster branch (handoff/audit-r9-roster
        # here, set at the fixplan tip, whose stage main never got); with that
        # ref absent each reads main's stage and says why on stderr.
        git("-C", str(bare), "update-ref", "refs/heads/handoff/audit-r9-roster",
            git("-C", str(bare), "rev-parse",
                "refs/heads/handoff/audit-r9-fixplan").strip())
        git("-C", str(drv), "fetch", "-q", "origin",
            "+handoff/audit-r9-roster:refs/remotes/origin/handoff/audit-r9-roster")
        git("-C", str(drv), "fetch", "-q", "origin",
            "+main:refs/remotes/origin/main")

        def standalone(script: str) -> tuple[str, str]:
            out = root / f"arm5-{script}.md"
            extra = (["--offline", "--pr-state", str(prstate)]
                     if script == "resume_doc.py" else [])
            r = subprocess.run([sys.executable, str(SEAT / script), "--repo",
                                "fixture/state", "--out", str(out), *extra],
                               cwd=str(drv), capture_output=True, text=True)
            return (out.read_text(encoding="utf-8") if out.exists() else
                    f"rc {r.returncode}"), r.stderr
        gens = ("plan_table.py", "resume_doc.py", "handover_prompt.py")
        for script in gens:
            text, err = standalone(script)
            ok(f"arm 5: {script} with no --roster-ref reads the round branch",
               "refused-then-landed" in text and "roster_lib:" not in err,
               (text[:200], err[-200:]))
        git("-C", str(drv), "update-ref", "-d",
            "refs/remotes/origin/handoff/audit-r9-roster")
        for script in gens:
            text, err = standalone(script)
            ok(f"arm 5: {script} with the branch absent reads main, and says so",
               "refused-then-landed" not in text and "absent" in err,
               (text[:200], err[-200:]))

    # --- the roster-sync step (--apply) ------------------------------------
    # A beat --apply derives the factual half of resume.stage from a pull
    # request read: a merged PR makes its group done at the merge commit, an
    # open one makes it in-progress, a deferred stage is left alone. Without
    # --apply the roster branch is not written at all (the null control), and
    # a second applying pass rewrites nothing (the round-trip rule).
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed = root / "seed"
        (seed / roster_lib.ROSTERS_DIR).mkdir(parents=True)
        (seed / ".claude" / "workflows").mkdir(parents=True)
        (seed / ".claude/workflows/brief_lint.mjs").write_text(
            "console.log('TOTAL: 0 error(s) across 1 file(s)');\n",
            encoding="utf-8")
        roster = {"repo": "fixture/state", "session": "r9-sync", "groups": [
            {"group": "R9-MERGED", "lane": "L1", "issues": [], "fixes": [],
             "after": [], "brief": "fixture merged.",
             "resume": {"stage": "not-started", "branch": "handoff/r9-merged"}},
            {"group": "R9-OPEN", "lane": "L1", "issues": [], "fixes": [],
             "after": [], "brief": "fixture open.",
             "resume": {"stage": "queued", "branch": "handoff/r9-open"}},
            {"group": "R9-DEFER", "lane": "L1", "issues": [], "fixes": [],
             "after": [], "brief": "fixture deferred.",
             "resume": {"stage": "deferred", "branch": "handoff/r9-defer"}}]}
        (seed / roster_lib.ROSTERS_DIR / "wave-r9-groups.json").write_text(
            json.dumps(roster, indent=1) + "\n", encoding="utf-8")
        throwaway_git_init(seed, "-q", "-b", "main")
        git("-C", str(seed), "add", "-A")
        git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
        # the round's roster branch: the ref the sync writes and the beat reads
        git("-C", str(seed), "branch", "handoff/audit-r9-roster")
        env = dict(os.environ, GIT_INDEX_FILE=str(root / "sync-index"))
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
        drv = root / "sync-drv"
        throwaway_git_clone(bare, drv, "-q")
        prstate = root / "sync-prs.json"
        prstate.write_text(json.dumps([
            {"number": 41, "state": "MERGED", "head": "handoff/r9-merged",
             "mergeCommit": {"oid": "f" * 40}, "body": "## Friction\n\n- none\n"},
            {"number": 42, "state": "OPEN", "head": "handoff/r9-open"},
            {"number": 43, "state": "MERGED", "head": "handoff/r9-defer",
             "mergeCommit": {"oid": "0" * 40}}]), encoding="utf-8")
        mirror = root / "sync-mirror"
        tipfile = root / "sync-tip"
        sync_argv = ["beat", "--checkout", str(drv), "--repo", "fixture/state",
                     "--roster-ref", "origin/handoff/audit-r9-roster",
                     "--state-ref", STATE_REF, "--pr-state", str(prstate),
                     "--mirror", str(mirror), "--tip-file", str(tipfile),
                     "--once"]
        roster_ref = "refs/heads/handoff/audit-r9-roster"
        sync_roster = f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"

        def roster_bytes() -> str:
            return git("-C", str(bare), "show", f"{roster_ref}:{sync_roster}")

        def roster_tip() -> str:
            return git("-C", str(bare), "rev-parse", roster_ref)

        seed_bytes = roster_bytes()
        # ARM 1 -- the null control: a beat WITHOUT --apply derives nothing.
        rc = main(sync_argv)
        ok("sync arm 1: a beat without --apply returns 0", rc == 0, rc)
        ok("sync arm 1: and leaves the roster branch byte-identical",
           roster_bytes() == seed_bytes)
        # ARM 2 -- with --apply the derived stages land, through the lint gate.
        tipfile.unlink(missing_ok=True)
        rc = main(sync_argv + ["--apply"])
        ok("sync arm 2: a beat --apply returns 0", rc == 0, rc)
        synced = roster_lib.groups_of(json.loads(roster_bytes()))
        ok("sync arm 2: merged -> done at the merge commit",
           synced["R9-MERGED"]["resume"]["stage"] == "done"
           and synced["R9-MERGED"]["resume"]["commit"] == "f" * 40,
           synced["R9-MERGED"]["resume"])
        ok("sync arm 2: open -> in-progress with its number",
           synced["R9-OPEN"]["resume"]["stage"] == "in-progress"
           and synced["R9-OPEN"]["resume"].get("pr") == 42,
           synced["R9-OPEN"]["resume"])
        ok("sync arm 2: a deferred stage is left alone",
           synced["R9-DEFER"]["resume"]["stage"] == "deferred",
           synced["R9-DEFER"]["resume"])
        ok("sync arm 2: the pushed plan table carries the derived stage",
           "| R9-MERGED | L1 | 1 | done |" in git(
               "-C", str(bare), "show", f"{STATE_REF}:{WRITE_SET[0]}"))
        # ARM 3 -- the round-trip rule: the next pass derives the same set and
        # writes nothing, so the branch tip and the bytes do not move.
        tip, before = roster_tip(), roster_bytes()
        tipfile.unlink(missing_ok=True)
        rc = main(sync_argv + ["--apply"])
        ok("sync arm 3: a second --apply pass returns 0", rc == 0, rc)
        ok("sync arm 3: and moves nothing (byte-identical roster)",
           roster_tip() == tip and roster_bytes() == before)

    # --- which round (R10-TICK d) ------------------------------------------
    # The state ref and dir follow the roster's round. A ref carrying round
    # 9's roster AND round 10's derives round 10; --roster-path picks the
    # other; a ref with no roster refuses before anything is generated.
    ok("round 10's state", state_of(10) == (
        "handoff/audit-r10-plan", "handoff/round10/state",
        tuple(f"handoff/round10/state/{n}" for n in DOC_NAMES)))
    with tempfile.TemporaryDirectory() as td:
        seed = Path(td) / "two"
        (seed / roster_lib.ROSTERS_DIR).mkdir(parents=True)
        throwaway_git_init(seed, "-q", "-b", "main")
        for n in (9, 10):
            (seed / roster_lib.ROSTERS_DIR / f"wave-r{n}-groups.json").write_text(
                json.dumps({"groups": []}), encoding="utf-8")
        git("-C", str(seed), "add", "-A")
        git("-C", str(seed), "commit", "-q", "-m", "two rounds")

        def round_for(*argv) -> int | str:
            try:
                return roster_round_of(parser().parse_args(
                    ["--checkout", str(seed), *argv]))
            except Refuse as e:
                return str(e)

        ok("two rosters at the ref: round 10", round_for("--roster-ref",
                                                         "main") == 10,
           round_for("--roster-ref", "main"))
        ok("--roster-path picks round 9", round_for(
            "--roster-ref", "main", "--roster-path",
            f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json") == 9)
        ok("--roster-file's name carries its round", round_for(
            "--roster-file", "/x/wave-r10-groups.json") == 10)
        git("-C", str(seed), "rm", "-q", "-r", roster_lib.ROSTERS_DIR)
        git("-C", str(seed), "commit", "-q", "-m", "none")
        got = round_for("--roster-ref", "main")
        ok("no roster refuses, naming the round question",
           isinstance(got, str) and "which round" in got, got)
        rc = main(["--checkout", str(seed), "--roster-ref", "main"])
        ok("main refuses rc 2 with no roster to take a round from", rc == 2, rc)

    if fails:
        print(f"{len(fails)} self-test check(s) failed: " + ", ".join(fails))
        return 1
    print("state_docs self-test: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
