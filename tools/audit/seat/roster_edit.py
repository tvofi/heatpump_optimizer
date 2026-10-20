#!/usr/bin/env python3
"""The safe roster edit: JSON load, modify, dump -- never a string splice.

    python3 tools/audit/seat/roster_edit.py set-stage   <group> <stage> [--at-sha SHA]
    python3 tools/audit/seat/roster_edit.py wire-issue  <group> <issue#> [--field fixes|issues]
    python3 tools/audit/seat/roster_edit.py unwire-issue <group> <issue#> [--field fixes|issues]
    python3 tools/audit/seat/roster_edit.py append-group <json-file>
    python3 tools/audit/seat/roster_edit.py edit-brief  <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py append-carry <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note> <text | @file>
    python3 tools/audit/seat/roster_edit.py set-after   <group> <G1,G2,... | ->
    python3 tools/audit/seat/roster_edit.py drop-carry  <group> <index | --match TEXT>
        [--at-sha SHA] [--checkout DIR] [--roster-ref BR] [--branch OUT]
        [--roster-path PATH] [--worktree DIR] [--lint-cwd DIR] [--push]
        [--message MSG]
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
`origin/<--branch>` when that exists, else at `origin/<--roster-ref>`, and
`checkout -B <--branch>` resets the branch there, so a re-run is idempotent.
An existing worktree with uncommitted changes is refused, never clobbered.

WHICH ROSTER is `roster_lib.roster_path`'s answer, never a path of this
file's: the newest `dev/programme/rosters/wave-r<N>-groups.json` in the
worktree, or `--roster-path`. `--roster-ref` defaults to `main`, and
`--branch` to `--roster-ref` when that is given, else to the round's roster
branch (`roster_lib.round_branch`: `handoff/audit-r<N>-roster`, N the newest
round at `origin/<--roster-ref>`) -- never to main itself.

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
  wire-issue   appends an integer issue (to `fixes` with --field fixes),
               refusing a duplicate;
  unwire-issue removes an integer from `issues` (default) or, with
               `--field fixes`, from `fixes`; refuses when it is not there;
  append-group inserts a validated new group (group/lane/after/brief needed,
               `after` naming known groups, resume defaulted);
  edit-brief   replaces the brief (an @file argument reads the file);
  append-carry appends to the group's carry list, refusing an exact repeat;
  set-resume   sets one resume field -- the free-text state a session
               restarts from. stage and branch are non-null: an empty value
               is refused. commit demands a sha. An empty value for commit,
               last_step, next_step or note clears the field to null.
  set-after    replaces the group's after-edges whole (`-` for none),
               refusing an unknown group, a self-edge, a repeated edge and
               a cycle in the resulting after-graph;
  drop-carry   removes one carry entry by 0-based index or by the one entry
               containing --match TEXT, refusing an absent carry, an index
               out of range, no match and an ambiguous match; dropping the
               last entry removes the key.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SELF = "tools/audit/seat/roster_edit.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_lib  # noqa: E402  which roster: roster_lib.roster_path, the one owner
import ref_privacy  # noqa: E402  a ref or message never names this host (#2310)
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


WIRE_FIELDS = ("issues", "fixes")


def op_wire_issue(roster, group, issue, field="issues"):
    """Append an integer to `issues` (default) or, with `--field fixes`, to
    `fixes` (the issues the group's PR closes)."""
    g = _need(roster, group)
    if field not in WIRE_FIELDS:
        raise Refuse(f"--field for wire-issue is one of "
                     f"{', '.join(WIRE_FIELDS)}, not {field!r}")
    try:
        n = int(issue)
    except ValueError:
        raise Refuse(f"issue must be an integer: {issue!r}")
    if n in (g.get(field) or []):
        raise Refuse(f"{group} already wires #{n} in {field}")
    g.setdefault(field, []).append(n)
    g[field].sort()


def op_unwire_issue(roster, group, issue, field="issues"):
    """The inverse of wire-issue: drop one integer from `issues` or `fixes`."""
    g = _need(roster, group)
    if field not in WIRE_FIELDS:
        raise Refuse(f"--field for unwire-issue is one of "
                     f"{', '.join(WIRE_FIELDS)}, not {field!r}")
    try:
        n = int(issue)
    except ValueError:
        raise Refuse(f"issue must be an integer: {issue!r}")
    held = g.get(field) or []
    if n not in held:
        raise Refuse(f"{group} does not hold #{n} in {field} "
                     f"(holds: {held})")
    g[field] = [i for i in held if i != n]


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


def op_set_after(roster, group, spec):
    """Replace a group's after-edges whole: `G1,G2,...`, or `-` for none.
    Each named group must exist, none may be the group itself or repeat, and
    the resulting after-graph must stay acyclic -- the dispatch order a
    replan rests on."""
    g = _need(roster, group)
    after = [] if spec == "-" else [a.strip() for a in spec.split(",")]
    known = {x.get("group") for x in roster.get("groups", [])}
    bad = [a for a in after if a not in known]
    if bad:
        raise Refuse(f"set-after: {group} after names no group: {bad}")
    if group in after:
        raise Refuse(f"set-after: {group} after itself is a self-edge")
    dup = sorted({a for a in after if after.count(a) > 1})
    if dup:
        raise Refuse(f"set-after: duplicate edge in {group} after: {dup}")
    edges = {x.get("group"): list(x.get("after") or [])
             for x in roster.get("groups", [])}
    edges[group] = after
    cycle = _cycle(edges)
    if cycle:
        raise Refuse(f"set-after: {group} after {after} closes a cycle: "
                     f"{' -> '.join(cycle)}")
    g["after"] = after


def _cycle(edges):
    """One cycle of the after-graph as a node path (first node repeated at
    the end), or None when the graph is a DAG."""
    state = {}  # absent: unvisited; 1: on the DFS stack; 2: finished
    for root in edges:
        if root in state:
            continue
        stack, path = [(root, iter(edges.get(root, ())))], [root]
        state[root] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                path.pop()
            elif state.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            elif nxt not in state:
                state[nxt] = 1
                stack.append((nxt, iter(edges.get(nxt, ()))))
                path.append(nxt)
    return None


def op_drop_carry(roster, group, index=None, match=None):
    """The inverse of append-carry: drop one carry entry, by its 0-based
    index (`jq '.carry[N]'`) or by the one entry containing `match`.
    Dropping the last entry removes the key, so append-then-drop restores
    the roster's bytes."""
    g = _need(roster, group)
    carry = g.get("carry") or []
    if not carry:
        raise Refuse(f"drop-carry: {group} carries nothing")
    if match is not None:
        hits = [i for i, c in enumerate(carry) if match in c]
        if not hits:
            raise Refuse(f"drop-carry: no carry entry matches {match!r} "
                         f"in {group}")
        if len(hits) > 1:
            raise Refuse(f"drop-carry: {match!r} is ambiguous in {group}: "
                         f"entries {hits} match; pass an index")
        i = hits[0]
    else:
        try:
            i = int(index)
        except ValueError:
            raise Refuse(f"drop-carry: index must be an integer: {index!r}")
        if not 0 <= i < len(carry):
            raise Refuse(f"drop-carry: index {i} out of range for {group} "
                         f"({len(carry)} entries)")
    del carry[i]
    if not carry:
        del g["carry"]


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
    local branch tip the base does not contain (unpushed commits). The
    caller fetches first (`fetch_origin`)."""
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


def fetch_origin(checkout) -> None:
    run(["git", "-C", str(checkout), "fetch", "-q", "origin",
         "+refs/heads/*:refs/remotes/origin/*"])


def roster_target(checkout, roster_ref, branch, roster_path):
    """(ref, branch): `--roster-ref` defaults to main; `--branch` to the
    given `--roster-ref`, else to the round's roster branch -- the newest
    roster at origin/<ref> names the round -- so a default edit never lands
    on main itself."""
    ref = roster_ref or "main"
    if branch or roster_ref:
        return ref, branch or roster_ref
    try:
        path = roster_lib.roster_path(str(checkout), f"origin/{ref}",
                                      roster_path)
        return ref, roster_lib.round_branch(path)
    except roster_lib.RosterNotFound as e:
        raise Refuse(str(e))


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
    p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                  "edit-brief", "append-carry", "set-resume",
                                  "set-after", "drop-carry"))
    p.add_argument("group")
    p.add_argument("value", nargs="?")
    p.add_argument("--at-sha")
    p.add_argument("--field", choices=RESUME_FIELDS + WIRE_FIELDS,
                   help="set-resume: which resume field to write; "
                        "unwire-issue: issues (default) or fixes")
    p.add_argument("--value", dest="value_opt",
                   help="the value, for when a positional value does not fit")
    p.add_argument("--match",
                   help="drop-carry: drop the one carry entry containing it")
    p.add_argument("--checkout", default=".")
    p.add_argument("--roster-ref", default=None,
                   help="the base ref (default main)")
    p.add_argument("--branch", default=None,
                   help="the branch the edit lands on (default --roster-ref, "
                        "else handoff/audit-r<N>-roster)")
    p.add_argument("--roster-path", default=None,
                   help="the roster file, repo-relative (default: the newest "
                        "dev/programme/rosters/wave-r<N>-groups.json)")
    p.add_argument("--worktree", required=True)
    p.add_argument("--lint-cwd")
    p.add_argument("--push", action="store_true")
    p.add_argument("--message")
    a = p.parse_args(argv)
    if a.value is not None and a.value_opt is not None:
        p.error("give the value positionally or with --value, not both")
    value = a.value_opt if a.value is None else a.value
    if a.match is not None and a.op != "drop-carry":
        p.error("--match is a drop-carry flag")
    if a.op == "drop-carry" and value is not None and a.match is not None:
        pass
    if a.op == "drop-carry" and value is None and a.match is None:
        p.error("drop-carry needs an index or --match")
    if a.match is None and (value is None
                            or (value == "" and a.op != "set-resume")):
        p.error(f"{a.op} needs a value argument")
    if a.op == "set-resume" and not a.field:
        p.error("set-resume needs --field")
    if a.op == "set-resume" and a.field not in RESUME_FIELDS:
        p.error(f"set-resume --field is one of {', '.join(RESUME_FIELDS)}")
    if a.op in ("wire-issue", "unwire-issue") and a.field \
            and a.field not in WIRE_FIELDS:
        p.error(f"{a.op} --field is one of {', '.join(WIRE_FIELDS)}")
    if a.op not in ("set-resume", "wire-issue", "unwire-issue") and a.field:
        p.error("--field is a set-resume / wire-issue / unwire-issue flag")
    try:
        fetch_origin(a.checkout)
        ref, branch = roster_target(a.checkout, a.roster_ref, a.branch,
                                    a.roster_path)
        msg = a.message or f"roster_edit {a.op} {a.group} ({SELF})"
        why = ref_privacy.refusal(branch, (("the message", msg),))
        if why:
            raise Refuse(f"{why} would publish this host (#2310); nothing written")
        prepare_worktree(a.checkout, ref, branch, a.worktree)
        try:
            rel = roster_lib.roster_path(str(a.worktree), None, a.roster_path)
        except roster_lib.RosterNotFound as e:
            raise Refuse(str(e))
        path = Path(a.worktree) / rel
        print(f"roster: {rel} on {branch}")
        roster = json.loads(path.read_text(encoding="utf-8"))
        if a.op == "set-stage":
            op_set_stage(roster, a.group, value, a.at_sha)
        elif a.op == "wire-issue":
            op_wire_issue(roster, a.group, value, a.field or "issues")
        elif a.op == "unwire-issue":
            op_unwire_issue(roster, a.group, value, a.field or "issues")
        elif a.op == "append-group":
            op_append_group(roster, value)
        elif a.op == "edit-brief":
            op_edit_brief(roster, a.group, value)
        elif a.op == "set-resume":
            op_set_resume(roster, a.group, a.field, value)
        elif a.op == "set-after":
            op_set_after(roster, a.group, value)
        elif a.op == "drop-carry":
            op_drop_carry(roster, a.group, value, a.match)
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

    # The fixture's roster: one round, so the newest IS this path.
    FIXTURE_ROSTER = f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"
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
    (seed / FIXTURE_ROSTER).parent.mkdir(parents=True, exist_ok=True)
    (seed / FIXTURE_ROSTER).write_text(dump(roster), encoding="utf-8")
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
             at_sha=None, field=None, value_opt=None, match=None):
        args = [op, group]
        if value is not None:
            args += [value]
        if field:
            args += ["--field", field]
        if match is not None:
            args += ["--match", match]
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

    def refuses(why, *args, **kw):
        """rc 2 (or argparse's exit) AND the refusal names `why`: a bare rc
        cannot tell this op's refusal from argparse refusing the op itself,
        or one refusal from another that happens to fire first."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = sysrc(lambda: edit(*args, **kw))
        return rc not in (0, None) and why in err.getvalue()

    def branch_roster(name="edit-1"):
        sha = run(["git", "-C", str(origin), "rev-parse",
                   f"refs/heads/{name}"]).strip()
        return json.loads(run(["git", "-C", str(origin), "show",
                               f"{sha}:{FIXTURE_ROSTER}"]))

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
    check("unwire-issue rc", edit("unwire-issue", "R9-B", "1946") == 0)
    check("unwire-issue round-trip",
          branch_roster()["groups"][1]["issues"] == [])
    check("unwire-issue absent refused",
          edit("unwire-issue", "R9-B", "1946") == 2)
    check("unwire-issue default field is issues, not fixes",
          edit("unwire-issue", "R9-A", "10", field="fixes") == 2
          and edit("unwire-issue", "R9-A", "10", field="issues") == 0
          and branch_roster()["groups"][0]["issues"] == [])
    check("unwire-issue non-integer refused",
          edit("unwire-issue", "R9-A", "abc") == 2)
    check("unwire-issue unknown group refused",
          edit("unwire-issue", "R9-NOPE", "10") == 2)
    check("wire-issue --field fixes rc",
          edit("wire-issue", "R9-B", "5", field="fixes") == 0)
    rb = branch_roster()["groups"][1]
    check("wire-issue --field fixes writes fixes only",
          rb["fixes"] == [5] and rb["issues"] == [])
    check("dup wire-issue --field fixes refused",
          edit("wire-issue", "R9-B", "5", field="fixes") == 2)
    check("wire-issue --field issues still defaults and sorts",
          edit("wire-issue", "R9-B", "5") == 0
          and branch_roster()["groups"][1]["issues"] == [5])
    check("--field stage refused on wire-issue",
          sysrc(lambda: edit("wire-issue", "R9-B", "6", field="stage")) != 0)
    check("unwire-issue cleans the wire-issue arm",
          edit("unwire-issue", "R9-B", "5") == 0
          and edit("unwire-issue", "R9-B", "5", field="fixes") == 0)
    check("--field stage refused on unwire-issue",
          sysrc(lambda: edit("unwire-issue", "R9-A", "10", field="stage"))
          != 0)
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
    fxg = Path(tmp, "fx.json")
    fxg.write_text(json.dumps({"group": "R9-F", "lane": "L2", "after": [],
                               "brief": "fixture F", "issues": [8],
                               "fixes": [7, 8]}), encoding="utf-8")
    check("append-group with fixes rc", edit("append-group", "R9-F", str(fxg)) == 0)
    check("unwire-issue --field fixes rc",
          edit("unwire-issue", "R9-F", "7", field="fixes") == 0)
    rf = branch_roster()["groups"][-1]
    check("unwire-issue --field fixes removes only that field's entry",
          rf["fixes"] == [8] and rf["issues"] == [8])
    check("unwire-issue --field fixes absent refused",
          edit("unwire-issue", "R9-F", "7", field="fixes") == 2)
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

    # set-after: a group's after-edges replaced whole, through the same
    # load/modify/dump flow; every refusal leaves the remote branch where it
    # was, and the resulting graph stays a DAG.
    def tip(name="edit-1"):
        return run(["git", "-C", str(origin), "rev-parse",
                    f"refs/heads/{name}"]).strip()

    def after_of(group):
        return next(g for g in branch_roster()["groups"]
                    if g["group"] == group).get("after")

    check("set-after rc", edit("set-after", "R9-C", "R9-B,R9-F") == 0)
    check("set-after round-trip", after_of("R9-C") == ["R9-B", "R9-F"])
    check("set-after - clears the edges",
          edit("set-after", "R9-C", "-") == 0 and after_of("R9-C") == [])
    t0 = tip()
    check("no-op set-after reports no change and commits nothing",
          edit("set-after", "R9-B", "R9-A") == 0 and tip() == t0)
    check("set-after unknown group refused",
          refuses("no roster group", "set-after", "R9-ZZ", "R9-A"))
    check("set-after unknown after-group refused",
          refuses("after names no group", "set-after", "R9-B",
                  "R9-A,R9-NOPE"))
    check("set-after self-edge refused",
          refuses("self-edge", "set-after", "R9-B", "R9-B"))
    check("set-after duplicate edge refused",
          refuses("duplicate edge", "set-after", "R9-C", "R9-A,R9-A"))
    check("set-after direct cycle refused",
          refuses("cycle", "set-after", "R9-A", "R9-B"))
    check("set-after indirect cycle refused",
          edit("set-after", "R9-C", "R9-B") == 0
          and refuses("cycle", "set-after", "R9-A", "R9-C")
          and after_of("R9-A") == [])
    t0 = tip()
    check("refused set-after moved nothing",
          refuses("cycle", "set-after", "R9-A", "R9-B") and tip() == t0)
    check("set-after names no op flag",
          refuses("--match is a drop-carry flag", "set-after", "R9-B",
                  "R9-A", match="x"))

    # drop-carry: the inverse of append-carry, by index or by a unique match;
    # dropping the last entry removes the key, so append-then-drop restores
    # the roster's bytes exactly.
    def carry_of(group):
        return next(g for g in branch_roster()["groups"]
                    if g["group"] == group).get("carry")

    def bytes_at(name="edit-1"):
        return run(["git", "-C", str(origin), "show",
                    f"{tip(name)}:{FIXTURE_ROSTER}"])

    check("drop-carry with no carry refused",
          refuses("carries nothing", "drop-carry", "R9-B", "0")
          and refuses("carries nothing", "drop-carry", "R9-B", None,
                      match="alpha"))
    check("drop-carry unknown group refused",
          refuses("no roster group", "drop-carry", "R9-ZZ", "0"))
    before_carry = bytes_at()
    for text in ("alpha one", "alpha two", "beta"):
        edit("append-carry", "R9-B", text)
    check("drop-carry fixture carries three",
          carry_of("R9-B") == ["alpha one", "alpha two", "beta"])
    t0 = tip()
    check("drop-carry ambiguous match refused",
          refuses("ambiguous", "drop-carry", "R9-B", None, match="alpha"))
    check("drop-carry absent match refused",
          refuses("no carry entry matches", "drop-carry", "R9-B", None,
                  match="gamma"))
    check("drop-carry index past the end refused",
          refuses("out of range", "drop-carry", "R9-B", "3"))
    check("drop-carry negative index refused",
          refuses("out of range", "drop-carry", "R9-B", "-1"))
    check("drop-carry non-integer index refused",
          refuses("index must be an integer", "drop-carry", "R9-B", "x"))
    check("drop-carry index and --match together refused",
          refuses("not both", "drop-carry", "R9-B", "0", match="beta"))
    check("drop-carry neither index nor --match refused",
          refuses("drop-carry needs an index or --match", "drop-carry",
                  "R9-B", None))
    check("--match on another op refused",
          refuses("--match is a drop-carry flag", "set-stage", "R9-B",
                  "done", match="x"))
    check("refused drop-carry moved nothing", tip() == t0)
    check("drop-carry by index drops that entry",
          edit("drop-carry", "R9-B", "1") == 0
          and carry_of("R9-B") == ["alpha one", "beta"])
    check("drop-carry by match drops that entry",
          edit("drop-carry", "R9-B", None, match="beta") == 0
          and carry_of("R9-B") == ["alpha one"])
    check("drop-carry of the last entry removes the key",
          edit("drop-carry", "R9-B", None, match="alpha one") == 0
          and carry_of("R9-B") is None)
    check("append-carry then drop-carry is byte-identical",
          bytes_at() == before_carry)

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
    (seed2 / FIXTURE_ROSTER).parent.mkdir(parents=True, exist_ok=True)
    (seed2 / FIXTURE_ROSTER).write_text(canon, encoding="utf-8")
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
    wt2_bytes = (Path(tmp, "wt2") / FIXTURE_ROSTER).read_text(encoding="utf-8")
    check("no-op set-resume is byte-identical", wt2_bytes == canon)
    check("no-op set-after rc",
          sysrc(lambda: main(["set-after", "R9-A", "-",
                           "--checkout", str(drv2), "--roster-ref", "main",
                           "--branch", "edit-byte",
                           "--worktree", str(Path(tmp, "wt2")),
                           "--lint-cwd", str(seed2), "--push"])) == 0)
    wt2_bytes = (Path(tmp, "wt2") / FIXTURE_ROSTER).read_text(encoding="utf-8")
    check("no-op set-after is byte-identical", wt2_bytes == canon)

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

    # a branch name naming a host path refuses before anything is committed (#2310)
    leaky = "edit/Users-" + "exampleuser-x"
    rc = edit("set-stage", "R9-A", "review", push=True, branch=leaky)
    check("a branch naming a host path refuses", rc == 2, rc)
    check("and pushes nothing", not run(["git", "-C", str(origin), "for-each-ref",
                                         f"refs/heads/{leaky}"]).strip())

    # the stale-worktree trap: a lint checkout main has moved past is refused
    # even when the roster itself is fine.
    stale = Path(tmp, "stale")
    throwaway_git_clone(origin, stale, "-q")
    old = run(["git", "-C", str(stale), "rev-parse", "HEAD~1"]).strip()
    run(["git", "-C", str(stale), "checkout", "-q", "--detach", old])
    rc = edit("set-stage", "R9-A", "done", push=True, branch="edit-2",
              lint_cwd=str(stale))
    check("stale lint-cwd refused", rc == 3, rc)
    ok, why = lint_gate(drv, str(stale), seed / FIXTURE_ROSTER)
    check("stale refusal named the trap",
          not ok and "stale-worktree" in why, why[:80])
    # and the good path pushes: fresh lint checkout (the seed is main's tip).
    check("fresh lint-cwd pushes",
          edit("set-stage", "R9-A", "done", push=True, branch="edit-3") == 0)
    check("pushed roster carries the edit",
          branch_roster("edit-3")["groups"][0]["resume"]["stage"] == "done")

    # WHICH ROSTER (R10-TICK b): a tree carrying round 9's roster AND round
    # 10's. The edit lands in the newest unless --roster-path names another;
    # a fixed round-9 path refused every round-10 group ("no roster group").
    seed3 = Path(tmp, "seed3")
    seed3.mkdir()
    throwaway_git_init(seed3, "-q", "-b", "main")
    (seed3 / BRIEF_LINT_NEW).parent.mkdir(parents=True)
    (seed3 / BRIEF_LINT_NEW).write_text(
        "console.log('TOTAL: 0 error(s) across 1 file(s)');\n",
        encoding="utf-8")
    r9_path = FIXTURE_ROSTER
    r10_path = f"{roster_lib.ROSTERS_DIR}/wave-r10-groups.json"
    r9 = {"groups": [{"group": "R9-A", "lane": "L1", "issues": [],
                      "after": [], "brief": "r9", "resume": {}}]}
    r10 = {"groups": [{"group": "R10-A", "lane": "L1", "issues": [],
                       "after": [], "brief": "r10", "resume": {}}]}
    (seed3 / r9_path).parent.mkdir(parents=True, exist_ok=True)
    (seed3 / r9_path).write_text(dump(r9), encoding="utf-8")
    (seed3 / r10_path).write_text(dump(r10), encoding="utf-8")
    run(["git", "-C", str(seed3), "add", "-A"])
    run(["git", "-C", str(seed3), "commit", "-q", "-m", "two rounds"])
    origin3 = Path(tmp, "origin3.git")
    throwaway_git_clone(seed3, origin3, "-q", "--bare")
    drv3 = Path(tmp, "drv3")
    throwaway_git_clone(origin3, drv3, "-q")

    def edit3(*extra, wt):
        return sysrc(lambda: main(
            ["wire-issue", *extra, "--checkout", str(drv3),
             "--worktree", str(Path(tmp, wt)), "--lint-cwd", str(seed3),
             "--push"]))

    def at3(branch, path):
        return json.loads(run(["git", "-C", str(origin3), "show",
                               f"refs/heads/{branch}:{path}"]))

    main_before = run(["git", "-C", str(origin3), "rev-parse",
                       "refs/heads/main"]).strip()
    check("two rosters: a round-10 group is editable (the newest)",
          edit3("R10-A", "2300", wt="wt3") == 0)
    check("two rosters: the edit lands in the round-10 roster",
          at3("handoff/audit-r10-roster", r10_path)["groups"][0]["issues"]
          == [2300])
    check("two rosters: the round-9 roster is untouched",
          at3("handoff/audit-r10-roster", r9_path) == r9)
    check("the default branch is the round's roster branch, never main",
          run(["git", "-C", str(origin3), "rev-parse",
               "refs/heads/main"]).strip() == main_before)
    check("--roster-path wins over the newest",
          edit3("R9-A", "2301", "--roster-path", r9_path, "--branch",
                "edit-r9", wt="wt4") == 0
          and at3("edit-r9", r9_path)["groups"][0]["issues"] == [2301])
    check("--roster-path naming a missing file refuses",
          edit3("R10-A", "2302", "--roster-path", "nope.json", "--branch",
                "edit-nope", wt="wt5") == 2)
    run(["git", "-C", str(seed3), "rm", "-q", r9_path, r10_path])
    run(["git", "-C", str(seed3), "commit", "-q", "-m", "no rosters"])
    run(["git", "-C", str(seed3), "push", "-q", str(origin3),
         "main:refs/heads/main"])
    check("no roster at all refuses (no silent fallback)",
          edit3("R10-A", "2303", "--roster-ref", "main", "--branch",
                "edit-none", wt="wt6") == 2)
    check("no roster: the default branch refuses before any worktree",
          edit3("R10-A", "2303", wt="wt7") == 2
          and not Path(tmp, "wt7").exists())

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"roster_edit self-test: {passed + len(failed)} checks, "
          f"{len(failed)} failed")
    for f in failed:
        print("FAIL", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
