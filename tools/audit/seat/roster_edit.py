#!/usr/bin/env python3
"""The safe roster edit: JSON load, modify, dump -- never a string splice.

    python3 tools/audit/seat/roster_edit.py set-stage   <group> <stage> [--at-sha SHA]
    python3 tools/audit/seat/roster_edit.py wire-issue  <group> <issue#>
    python3 tools/audit/seat/roster_edit.py append-group <json-file>
    python3 tools/audit/seat/roster_edit.py edit-brief  <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py append-carry <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note> <text | @file>
        [--at-sha SHA] [--checkout DIR] [--roster-ref BR] [--branch OUT]
        [--worktree DIR] [--lint-cwd DIR] [--push] [--message MSG]
    python3 tools/audit/seat/roster_edit.py --self-test

Two recorded JSON breakages came from editing the roster as text; every op
here loads the whole roster, validates the change, and dumps it again with
the file's own formatting (indent=1, ASCII-escaped, no trailing newline --
`dump` below), so an edit cannot unbalance the file. THE ROUND-TRIP RULE: a
no-op edit must reproduce the roster's bytes exactly; the self-test pins it
with hand-written fixture bytes, because a dump that does not match the
file's live formatting rewrites every one of its 7503 lines on ANY edit (a
naive `json.dump(..., indent=2)` did exactly that).

The write path is the checkout -B worktree pattern: a throwaway worktree of
`--checkout` (default: this directory's repository) is created detached at
`origin/<--roster-ref>` and `checkout -B <--branch>` resets the branch there,
so a re-run is idempotent. An existing worktree with uncommitted changes is
refused, never clobbered.

THE LINT GATE. `--push` refuses unless the brief_lint the fresh origin/main
checkout contains, run in that checkout on the modified roster, prints
`TOTAL: 0 error(s)`. That is `.claude/workflows/brief_lint.mjs` when the
checkout has that file, otherwise `tools/policy/brief_lint.mjs`. The probe
is the checkout, not the process cwd: a branch that has moved the script
still lints with the copy main holds. Without `--lint-cwd`, the tool checks
out one itself; with it, the tool verifies the directory's HEAD still equals
origin/main and refuses otherwise -- the stale-worktree phantom-error trap:
a checkout main has moved past is a lint the tree no longer runs. An edit
whose brief text the linter refuses is refused at the same gate, before
anything reaches GitHub.

Ops (all group ids must exist, except append-group which must not):
  set-stage    sets resume.stage (and resume.commit with --at-sha);
  wire-issue   appends an integer issue, refusing a duplicate;
  append-group inserts a validated new group (group/lane/after/brief needed,
               `after` naming known groups, resume defaulted);
  edit-brief   replaces the brief (an @file argument reads the file);
  append-carry appends to the group's carry list, refusing an exact repeat;
  set-resume   sets one resume field -- the free-text state a session
               restarts from. stage and branch are non-null: an empty value
               is refused. commit demands a sha. An empty value for commit,
               last_step, next_step or note clears the field to null.
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
from pathlib import Path

SELF = "tools/audit/seat/roster_edit.py"
ROSTER_PATH = ".claude/workflows/wave-r9-groups.json"
TOTAL_OK = re.compile(r"TOTAL: 0 error")
SHA_RE = re.compile(r"\A[0-9a-f]{7,40}\Z")
# Historical path first, then the moved one: the same preference as
# `test -f` in the graders. Which of the two exists is read from the
# checkout being linted.
BRIEF_LINT_OLD = ".claude/workflows/brief_lint.mjs"
BRIEF_LINT_NEW = "tools/policy/brief_lint.mjs"


class Refuse(Exception):
    pass


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise Refuse(f"{' '.join(cmd)} (in {cwd or '.'}) failed: "
                     f"{(r.stderr or r.stdout).strip()[:400]}")
    return r.stdout


# ----------------------------------------------------------------- ops
def op_set_stage(roster, group, stage, at_sha):
    g = _need(roster, group)
    if not isinstance(stage, str) or not stage.strip():
        raise Refuse("stage must be a non-empty string")
    if at_sha and not SHA_RE.match(at_sha):
        raise Refuse(f"--at-sha is not a sha: {at_sha!r}")
    g.setdefault("resume", {})["stage"] = stage
    if at_sha:
        g["resume"]["commit"] = at_sha


#: The resume fields set-resume may write. stage and branch are the roster's
#: structural non-null fields (gen.py defaults them); commit and the
#: free-text fields are str-or-null across the live roster, so an empty
#: value clears them to null.
RESUME_FIELDS = ("stage", "commit", "branch", "last_step", "next_step",
                 "note")
NON_NULL_RESUME_FIELDS = ("stage", "branch")
TEXT_RESUME_FIELDS = ("last_step", "next_step", "note")


def op_set_resume(roster, group, field, value):
    g = _need(roster, group)
    if field not in RESUME_FIELDS:
        # argparse's --field choices refuse it first; this guards direct callers
        raise Refuse(f"unknown resume field: {field!r} "
                     f"(known: {', '.join(RESUME_FIELDS)})")
    resume = g.setdefault("resume", {})
    if value == "":
        if field in NON_NULL_RESUME_FIELDS:
            raise Refuse(f"resume.{field} is a non-null field; an empty "
                         "value is refused")
        resume[field] = None  # clearing a nullable field
        return
    if field == "commit" and not SHA_RE.match(value):
        raise Refuse(f"--field commit needs a sha: {value!r}")
    resume[field] = _text(value) if field in TEXT_RESUME_FIELDS else value


def op_wire_issue(roster, group, issue):
    g = _need(roster, group)
    try:
        n = int(issue)
    except ValueError:
        raise Refuse(f"issue must be an integer: {issue!r}")
    if n in (g.get("issues") or []):
        raise Refuse(f"{group} already wires #{n}")
    g.setdefault("issues", []).append(n)
    g["issues"].sort()


def op_append_group(roster, json_file):
    try:
        new = json.loads(Path(json_file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refuse(f"append-group: unreadable JSON: {e}")
    gid = new.get("group")
    if not gid:
        raise Refuse("append-group: the entry needs a group id")
    if gid in {g.get("group") for g in roster.get("groups", [])}:
        raise Refuse(f"append-group: {gid} already in the roster")
    for field in ("lane", "brief"):
        if not new.get(field):
            raise Refuse(f"append-group: {gid} needs a {field}")
    after = new.get("after", [])
    if not isinstance(after, list):
        raise Refuse(f"append-group: {gid} after must be a list")
    known = {g.get("group") for g in roster.get("groups", [])}
    bad = [a for a in after if a not in known]
    if bad:
        raise Refuse(f"append-group: {gid} after names no group: {bad}")
    new.setdefault("issues", [])
    new.setdefault("fixes", [])
    new.setdefault("resume", {"stage": "not-started",
                              "branch": new.get("resume", {}).get("branch")})
    roster.setdefault("groups", []).append(new)


def op_edit_brief(roster, group, text):
    _need(roster, group)["brief"] = _text(text)


def op_append_carry(roster, group, text):
    g = _need(roster, group)
    entry = _text(text)
    carry = g.setdefault("carry", [])
    if entry in carry:
        raise Refuse(f"{group} already carries that entry")
    carry.append(entry)


def _need(roster, group):
    for g in roster.get("groups", []):
        if g.get("group") == group:
            return g
    raise Refuse(f"no roster group {group!r} "
                 f"(known: {len(roster.get('groups', []))} groups)")


def _text(arg):
    if arg.startswith("@"):
        try:
            return Path(arg[1:]).read_text(encoding="utf-8").strip()
        except OSError as e:
            raise Refuse(f"unreadable text file: {e}")
    return arg


# ----------------------------------------------------------------- flow
def prepare_worktree(checkout, ref, branch, wt) -> None:
    """A throwaway worktree on <branch>, reset to the branch's remote tip when
    one exists (so sequential edits accumulate) and to origin/<ref> otherwise.
    checkout -B makes the reset idempotent; the guards refuse anything that
    would clobber work: uncommitted changes in an existing worktree, and a
    local branch tip the base does not contain (unpushed commits)."""
    run(["git", "-C", str(checkout), "fetch", "-q", "origin",
         "+refs/heads/*:refs/remotes/origin/*"])
    base = f"origin/{ref}"
    has_branch = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "--verify", "--quiet",
         f"origin/{branch}"], capture_output=True)
    if has_branch.returncode == 0:
        base = f"origin/{branch}"
    if Path(wt).exists():
        if run(["git", "-C", str(wt), "status", "--porcelain"]).strip():
            raise Refuse(f"{wt} has uncommitted changes; refusing to reuse it")
        old = subprocess.run(
            ["git", "-C", str(wt), "rev-parse", "--verify", "--quiet",
             branch], capture_output=True, text=True).stdout.strip()
        if old and old != run(["git", "-C", str(wt), "rev-parse",
                               base]).strip():
            anc = subprocess.run(
                ["git", "-C", str(wt), "merge-base", "--is-ancestor",
                 old, base], capture_output=True)
            if anc.returncode != 0:
                raise Refuse(f"branch {branch} at {old[:12]} is not contained "
                             f"in {base}; unpushed commits would be lost")
        run(["git", "-C", str(wt), "checkout", "-B", branch, base])
    else:
        run(["git", "-C", str(checkout), "worktree", "add", "-q", "--detach",
             str(wt), base])
        run(["git", "-C", str(wt), "checkout", "-B", branch, base])


def brief_lint_script(lint_cwd) -> str | None:
    """Relative path of the brief_lint that directory contains.

    Prefer the historical path when that file is present, otherwise the
    moved path. None when the checkout has neither. The process cwd is a
    different tree and is not consulted: probing it and then running that
    relative path with `cwd=lint_cwd` executes a file the checkout does
    not contain.
    """
    root = Path(lint_cwd)
    for rel in (BRIEF_LINT_OLD, BRIEF_LINT_NEW):
        if (root / rel).is_file():
            return rel
    return None


def lint_gate(checkout, lint_cwd, roster_path):
    """brief_lint from a fresh origin/main checkout. Returns (ok, detail)."""
    run(["git", "-C", str(checkout), "fetch", "-q", "origin", "main"])
    main_sha = run(["git", "-C", str(checkout), "rev-parse", "origin/main"]).strip()
    made = None
    if lint_cwd:
        head = run(["git", "-C", str(lint_cwd), "rev-parse", "HEAD"]).strip()
        if head != main_sha:
            return False, (f"--lint-cwd {lint_cwd} is at {head[:12]}, not "
                           f"origin/main ({main_sha[:12]}): the stale-worktree "
                           "trap; lint from a fresh main checkout")
    else:
        made = tempfile.mkdtemp(prefix="hpo-lint-")
        run(["git", "-C", str(checkout), "worktree", "add", "-q", "--detach",
             made, main_sha])
        lint_cwd = made
    try:
        script = brief_lint_script(lint_cwd)
        if script is None:
            return False, (f"neither brief_lint path is a file in {lint_cwd}: "
                           f"{BRIEF_LINT_OLD} or {BRIEF_LINT_NEW}")
        r = subprocess.run(["node", script, str(Path(roster_path).resolve())],
                           cwd=lint_cwd, capture_output=True, text=True)
        out = r.stdout + r.stderr
        ok = bool(TOTAL_OK.search(out))
        tail = "\n".join(out.strip().splitlines()[-3:])
        return ok, tail
    finally:
        if made:
            run(["git", "-C", str(checkout), "worktree", "remove",
                 "--force", made])
            shutil.rmtree(made, ignore_errors=True)


def dump(roster) -> str:
    """The roster's canonical bytes: indent=1, ASCII-escaped, no trailing
    newline -- what the file at the roster ref carries. Anything else
    rewrites every line of the file on ANY edit (a naive
    `json.dump(..., indent=2)` rewrote 7503 of 7503); the self-test pins
    the round-trip with hand-written fixture bytes, so a drifting dump
    cannot pass by writing its own output back."""
    return json.dumps(roster, indent=1)


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if "--self-test" in argv:
        # Every git call in the self-test, the runner's and the ops' under
        # test, runs in a throwaway repository: all of them take the env.
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_environ
        with throwaway_git_environ():
            return _self_test()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("op", choices=("set-stage", "wire-issue", "append-group",
                                  "edit-brief", "append-carry", "set-resume"))
    p.add_argument("group")
    p.add_argument("value", nargs="?")
    p.add_argument("--at-sha")
    p.add_argument("--field", choices=RESUME_FIELDS,
                   help="set-resume only: which resume field to write")
    p.add_argument("--value", dest="value_opt",
                   help="the value, for when a positional value does not fit")
    p.add_argument("--checkout", default=".")
    p.add_argument("--roster-ref", default="handoff/audit-r9-fixplan")
    p.add_argument("--branch", default=None)
    p.add_argument("--worktree", required=True)
    p.add_argument("--lint-cwd")
    p.add_argument("--push", action="store_true")
    p.add_argument("--message")
    a = p.parse_args(argv)
    if a.value is not None and a.value_opt is not None:
        p.error("give the value positionally or with --value, not both")
    value = a.value_opt if a.value is None else a.value
    if value is None or (value == "" and a.op != "set-resume"):
        p.error(f"{a.op} needs a value argument")
    if a.op == "set-resume" and not a.field:
        p.error("set-resume needs --field")
    if a.op != "set-resume" and a.field:
        p.error("--field is a set-resume flag")
    branch = a.branch or a.roster_ref
    try:
        prepare_worktree(a.checkout, a.roster_ref, branch, a.worktree)
        path = Path(a.worktree) / ROSTER_PATH
        roster = json.loads(path.read_text(encoding="utf-8"))
        if a.op == "set-stage":
            op_set_stage(roster, a.group, value, a.at_sha)
        elif a.op == "wire-issue":
            op_wire_issue(roster, a.group, value)
        elif a.op == "append-group":
            op_append_group(roster, value)
        elif a.op == "edit-brief":
            op_edit_brief(roster, a.group, value)
        elif a.op == "set-resume":
            op_set_resume(roster, a.group, a.field, value)
        else:
            op_append_carry(roster, a.group, value)
        path.write_text(dump(roster), encoding="utf-8")
        if not run(["git", "-C", str(a.worktree),
                    "status", "--porcelain"]).strip():
            # A no-op edit reproduces the roster's own bytes (the round-trip
            # rule): nothing to commit, nothing to push, still a success --
            # re-running an op is idempotent.
            print(f"no change: {a.op} {a.group} wrote the roster's own "
                  "bytes (byte-identical); nothing to commit or push")
            return 0
        msg = a.message or f"roster_edit {a.op} {a.group} ({SELF})"
        run(["git", "-C", str(a.worktree), "commit", "-q", "-am", msg])
        head = run(["git", "-C", str(a.worktree), "rev-parse", "HEAD"]).strip()
        ok, detail = lint_gate(a.checkout, a.lint_cwd, path)
        if not ok:
            print(f"roster_edit: LINT GATE REFUSED the push\n{detail}\n"
                  f"the commit is local at {branch} {head[:12]}; nothing pushed",
                  file=sys.stderr)
            return 3
        print("lint gate: TOTAL: 0 error(s) from a fresh origin/main checkout")
        if a.push:
            run(["git", "-C", str(a.worktree), "push", "-q", "origin", branch])
            print(f"pushed {branch} at {head}")
        else:
            print(f"ready: {branch} at {head} (no --push)")
        return 0
    except Refuse as e:
        print(f"roster_edit: REFUSED: {e}", file=sys.stderr)
        return 2


# ----------------------------------------------------------------- self-test
def _self_test() -> int:
    failed = []
    passed = 0

    def check(name, ok, got=""):
        nonlocal passed
        passed += 1
        if not ok:
            failed.append(f"{name} (got: {got})")

    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_init
    tmp = tempfile.mkdtemp(prefix="hpo-fr8-selftest-")

    # The script node runs is the one lint_cwd contains. The process cwd is a
    # different tree: this branch has moved brief_lint, and a fresh main
    # checkout still has it at the historical path. A stub in the process cwd
    # that prints the other verdict must not be the one that runs.
    old_rel = BRIEF_LINT_OLD
    new_rel = BRIEF_LINT_NEW

    def lint_src(mark, total):
        return (f"console.log('{mark}');\n"
                f"console.log('TOTAL: {total} error(s) across 1 file(s)');\n")

    def planted(name, files):
        seed_n = Path(tmp, name)
        seed_n.mkdir()
        throwaway_git_init(seed_n, "-q", "-b", "main")
        for rel, source in files.items():
            dest = seed_n / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(source, encoding="utf-8")
        (seed_n / "README.md").write_text("fixture\n", encoding="utf-8")
        run(["git", "-C", str(seed_n), "add", "-A"])
        run(["git", "-C", str(seed_n), "commit", "-q", "-m", "fixture lint"])
        origin_n = Path(tmp, name + ".git")
        throwaway_git_clone(seed_n, origin_n, "-q", "--bare")
        drv_n = Path(tmp, name + "-drv")
        throwaway_git_clone(origin_n, drv_n, "-q")
        return drv_n, seed_n

    def decoy(name, rel, source):
        d = Path(tmp, name)
        dest = d / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source, encoding="utf-8")
        return d

    def gate_at(drv_n, lint_n, cwd_n):
        os.chdir(cwd_n)
        return lint_gate(drv_n, str(lint_n), lint_n / "README.md")

    here = os.getcwd()
    try:
        drv_n, lint_n = planted("gate-old", {old_rel: lint_src("LINTCWD", 0)})
        ok, why = gate_at(drv_n, lint_n, decoy("decoy-new", new_rel, lint_src("PROCESS", 1)))
        check("lint_cwd historical script runs",
              ok and "LINTCWD" in why and "PROCESS" not in why, why[:160])
        drv_n, lint_n = planted("gate-new", {new_rel: lint_src("LINTCWD", 0)})
        ok, why = gate_at(drv_n, lint_n, decoy("decoy-old", old_rel, lint_src("PROCESS", 1)))
        check("lint_cwd moved script runs",
              ok and "LINTCWD" in why and "PROCESS" not in why, why[:160])
        drv_n, lint_n = planted("gate-refuse", {new_rel: lint_src("LINTCWD", 1)})
        ok, why = gate_at(drv_n, lint_n, decoy("decoy-accept", old_rel, lint_src("PROCESS", 0)))
        check("lint_cwd refusal stands",
              not ok and "LINTCWD" in why and "PROCESS" not in why, why[:160])
        drv_n, lint_n = planted("gate-both", {
            old_rel: lint_src("LINTOLD", 0), new_rel: lint_src("LINTNEW", 1)})
        ok, why = gate_at(drv_n, lint_n, decoy("decoy-both", new_rel, lint_src("PROCESS", 1)))
        check("both paths prefer the historical file",
              ok and "LINTOLD" in why and "LINTNEW" not in why and "PROCESS" not in why,
              why[:160])
        drv_n, lint_n = planted("gate-none", {})
        ok, why = gate_at(drv_n, lint_n, decoy("decoy-none", old_rel, lint_src("PROCESS", 0)))
        check("lint_cwd without brief_lint refuses",
              not ok and "neither brief_lint path" in why, why[:160])
    finally:
        os.chdir(here)

    seed = Path(tmp, "seed")
    seed.mkdir()
    throwaway_git_init(seed, "-q", "-b", "main")
    (seed / ".claude/workflows").mkdir(parents=True)
    (seed / ".claude/workflows/brief_lint.mjs").write_text(
        "import {readFileSync} from 'node:fs';\n"
        "const t=readFileSync(process.argv[2],'utf8');\n"
        "const bad=t.includes('__bad__');\n"
        "console.log(bad ? 'TOTAL: 1 error(s) across 1 file(s)'\n"
        "               : 'TOTAL: 0 error(s) across 1 file(s)');\n",
        encoding="utf-8")
    roster = {"repo": "fixture/roster", "groups": [
        {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
         "after": [], "brief": "fixture group A",
         "resume": {"stage": "not-started", "branch": "handoff/a"}},
        {"group": "R9-B", "lane": "L1", "issues": [], "fixes": [],
         "after": ["R9-A"], "brief": "fixture group B",
         "resume": {"stage": "not-started", "branch": "handoff/b"}},
    ]}
    (seed / ROSTER_PATH).parent.mkdir(parents=True, exist_ok=True)
    (seed / ROSTER_PATH).write_text(dump(roster), encoding="utf-8")
    run(["git", "-C", str(seed), "add", "-A"])
    run(["git", "-C", str(seed), "commit", "-q", "-m", "fixture roster"])
    # a second commit, so the stale-checkout arm can detach to HEAD~1
    (seed / "README.md").write_text("fixture\n", encoding="utf-8")
    run(["git", "-C", str(seed), "add", "-A"])
    run(["git", "-C", str(seed), "commit", "-q", "-m", "fixture readme"])
    origin = Path(tmp, "origin.git")
    throwaway_git_clone(seed, origin, "-q", "--bare")
    drv = Path(tmp, "drv")
    throwaway_git_clone(origin, drv, "-q")

    def edit(op, group, value, push=True, branch="edit-1", lint_cwd=None,
             at_sha=None, field=None, value_opt=None):
        args = [op, group]
        if value is not None:
            args += [value]
        if field:
            args += ["--field", field]
        if value_opt is not None:
            args += ["--value", value_opt]
        if at_sha:
            args += ["--at-sha", at_sha]
        try:
            return main(args
                        + ["--checkout", str(drv), "--roster-ref", "main",
                           "--branch", branch, "--worktree",
                           str(Path(tmp, "wt")),
                           "--lint-cwd", lint_cwd or str(seed)]
                        + (["--push"] if push else []))
        except SystemExit as e:
            return e.code  # argparse refuses (unknown op/field) as SystemExit

    def sysrc(call):
        """The exit code of a call that may refuse through argparse's
        SystemExit -- an unknown --field choice dies there, not at rc 2."""
        try:
            return call()
        except SystemExit as e:
            return e.code

    def branch_roster(name="edit-1"):
        sha = run(["git", "-C", str(origin), "rev-parse",
                   f"refs/heads/{name}"]).strip()
        return json.loads(run(["git", "-C", str(origin), "show",
                               f"{sha}:{ROSTER_PATH}"]))

    # round-trips: each op lands in the dumped JSON, never a string splice.
    check("set-stage rc", edit("set-stage", "R9-A", "in-review") == 0)
    r = branch_roster()
    check("set-stage round-trip",
          r["groups"][0]["resume"]["stage"] == "in-review")
    check("set-stage --at-sha",
          edit("set-stage", "R9-A", "done", at_sha="a" * 40) == 0
          and branch_roster()["groups"][0]["resume"]["commit"] == "a" * 40)
    check("wire-issue rc", edit("wire-issue", "R9-B", "1946") == 0)
    check("wire-issue round-trip",
          branch_roster()["groups"][1]["issues"] == [1946])
    check("dup wire-issue refused",
          edit("wire-issue", "R9-B", "1946") == 2)
    newg = Path(tmp, "new.json")
    newg.write_text(json.dumps({"group": "R9-C", "lane": "L2",
                                "after": ["R9-A"], "brief": "fixture C"}),
                    encoding="utf-8")
    check("append-group rc", edit("append-group", "R9-C", str(newg)) == 0)
    rc = branch_roster()["groups"]
    check("append-group round-trip",
          rc[-1]["group"] == "R9-C" and rc[-1]["after"] == ["R9-A"]
          and rc[-1]["resume"]["stage"] == "not-started")
    check("dup append-group refused",
          edit("append-group", "R9-C", str(newg)) == 2)
    badg = Path(tmp, "bad.json")
    badg.write_text(json.dumps({"group": "R9-D", "after": ["R9-NOPE"],
                                "lane": "L2", "brief": "x"}), encoding="utf-8")
    check("dangling after refused",
          edit("append-group", "R9-D", str(badg)) == 2)
    check("edit-brief rc",
          edit("edit-brief", "R9-B", "rewritten brief") == 0
          and branch_roster()["groups"][1]["brief"] == "rewritten brief")
    check("append-carry rc",
          edit("append-carry", "R9-A", "carry text one") == 0
          and branch_roster()["groups"][0]["carry"] == ["carry text one"])
    check("dup carry refused",
          edit("append-carry", "R9-A", "carry text one") == 2)
    check("unknown group refused", edit("set-stage", "R9-ZZ", "done") == 2)

    # set-resume: the resume free-text fields a session restarts from, through
    # the same load/modify/dump flow -- never a string splice.
    check("set-resume rc",
          edit("set-resume", "R9-A", "merged as #9 at a1b2c3d",
               field="last_step") == 0)
    check("set-resume round-trip",
          branch_roster()["groups"][0]["resume"].get("last_step")
          == "merged as #9 at a1b2c3d")
    check("set-resume --value flag",
          edit("set-resume", "R9-A", None, field="next_step",
               value_opt="claim the next ready group") == 0
          and branch_roster()["groups"][0]["resume"].get("next_step")
          == "claim the next ready group")
    check("set-resume commit needs a sha",
          edit("set-resume", "R9-A", "nothex", field="commit") == 2)
    check("set-resume commit accepts a sha",
          edit("set-resume", "R9-A", "b" * 40, field="commit") == 0
          and branch_roster()["groups"][0]["resume"].get("commit") == "b" * 40)
    check("set-resume empty on a non-null field refused",
          edit("set-resume", "R9-A", "", field="stage") == 2
          and edit("set-resume", "R9-A", "", field="branch") == 2)
    check("set-resume empty on a nullable field clears it",
          edit("set-resume", "R9-A", "", field="last_step") == 0
          and branch_roster()["groups"][0]["resume"].get("last_step") is None)
    check("set-resume unknown group refused",
          edit("set-resume", "R9-ZZ", "x", field="last_step") == 2)
    check("set-resume unknown field refused",
          sysrc(lambda: edit("set-resume", "R9-A", "x", field="log")) == 2)

    # THE ROUND-TRIP REGRESSION. The roster's canonical bytes are indent=1,
    # ASCII-escaped, no trailing newline (the file at the fixplan ref). A dump
    # that does not reproduce them rewrites every line of the file on ANY edit
    # -- the 7503-of-7503-line rewrite a naive json.dump(..., indent=2)
    # produced. The fixture bytes below are hand-written, never dumped, so a
    # drifting dump cannot pass this by writing its own output back.
    canon = (
        '{\n'
        ' "repo": "fixture/roster",\n'
        ' "groups": [\n'
        '  {\n'
        '   "group": "R9-A",\n'
        '   "lane": "L1",\n'
        '   "issues": [\n'
        '    10\n'
        '   ],\n'
        '   "fixes": [],\n'
        '   "after": [],\n'
        '   "brief": "fixture group A at 21 \\u00b0C",\n'
        '   "resume": {\n'
        '    "stage": "in-flight",\n'
        '    "branch": "handoff/a",\n'
        '    "commit": "' + "a" * 40 + '",\n'
        '    "last_step": "reviewer handed off at \\u00b0",\n'
        '    "next_step": null,\n'
        '    "note": null\n'
        '   }\n'
        '  }\n'
        ' ]\n'
        '}')
    check("dump round-trips the canonical bytes",
          dump(json.loads(canon)) == canon)
    seed2 = Path(tmp, "seed2")
    seed2.mkdir()
    throwaway_git_init(seed2, "-q", "-b", "main")
    (seed2 / ".claude/workflows").mkdir(parents=True)
    (seed2 / ".claude/workflows/brief_lint.mjs").write_text(
        "console.log('TOTAL: 0 error(s) across 1 file(s)');\n",
        encoding="utf-8")
    (seed2 / ROSTER_PATH).parent.mkdir(parents=True, exist_ok=True)
    (seed2 / ROSTER_PATH).write_text(canon, encoding="utf-8")
    run(["git", "-C", str(seed2), "add", "-A"])
    run(["git", "-C", str(seed2), "commit", "-q", "-m", "fixture roster"])
    origin2 = Path(tmp, "origin2.git")
    throwaway_git_clone(seed2, origin2, "-q", "--bare")
    drv2 = Path(tmp, "drv2")
    throwaway_git_clone(origin2, drv2, "-q")
    check("no-op set-resume rc",
          sysrc(lambda: main(["set-resume", "R9-A", "reviewer handed off at \u00b0",
                           "--field", "last_step",
                           "--checkout", str(drv2), "--roster-ref", "main",
                           "--branch", "edit-byte",
                           "--worktree", str(Path(tmp, "wt2")),
                           "--lint-cwd", str(seed2), "--push"])) == 0)
    # The no-op path commits and pushes nothing, so the bytes are read from
    # the worktree the op wrote: they must be the roster's own, unchanged.
    tip = (Path(tmp, "wt2") / ROSTER_PATH).read_text(encoding="utf-8")
    check("no-op set-resume is byte-identical", tip == canon)

    # the lint gate: a bad brief is refused BEFORE the push; the branch on the
    # remote stays where it was.
    before = run(["git", "-C", str(origin), "rev-parse", "refs/heads/edit-1"]).strip()
    badb = Path(tmp, "bad-brief.json")
    badb.write_text(json.dumps({"group": "R9-E", "lane": "L2", "after": [],
                                "brief": "a brief with __bad__ in it"}),
                    encoding="utf-8")
    rc = edit("append-group", "R9-E", str(badb), push=True)
    check("lint gate refuses a bad brief", rc == 3, rc)
    after = run(["git", "-C", str(origin), "rev-parse", "refs/heads/edit-1"]).strip()
    check("refused push moved nothing", before == after)

    # the stale-worktree trap: a lint checkout main has moved past is refused
    # even when the roster itself is fine.
    stale = Path(tmp, "stale")
    throwaway_git_clone(origin, stale, "-q")
    old = run(["git", "-C", str(stale), "rev-parse", "HEAD~1"]).strip()
    run(["git", "-C", str(stale), "checkout", "-q", "--detach", old])
    rc = edit("set-stage", "R9-A", "done", push=True, branch="edit-2",
              lint_cwd=str(stale))
    check("stale lint-cwd refused", rc == 3, rc)
    ok, why = lint_gate(drv, str(stale), seed / ROSTER_PATH)
    check("stale refusal named the trap",
          not ok and "stale-worktree" in why, why[:80])
    # and the good path pushes: fresh lint checkout (the seed is main's tip).
    check("fresh lint-cwd pushes",
          edit("set-stage", "R9-A", "done", push=True, branch="edit-3") == 0)
    check("pushed roster carries the edit",
          branch_roster("edit-3")["groups"][0]["resume"]["stage"] == "done")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"roster_edit self-test: {passed + len(failed)} checks, "
          f"{len(failed)} failed")
    for f in failed:
        print("FAIL", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
