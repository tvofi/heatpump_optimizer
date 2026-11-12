#!/usr/bin/env python3
"""The safe roster edit: JSON load, modify, dump -- never a string splice.

    python3 tools/audit/seat/roster_edit.py set-stage   <group> <stage> [--at-sha SHA]
    python3 tools/audit/seat/roster_edit.py wire-issue  <group> <issue#> [--field fixes|issues]
    python3 tools/audit/seat/roster_edit.py unwire-issue <group> <issue#> [--field fixes|issues]
    python3 tools/audit/seat/roster_edit.py append-group <GROUP> <json-file | @json-file> [--reason TEXT]
    python3 tools/audit/seat/roster_edit.py edit-brief  <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py append-carry <group> <text | @file>
    python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note|pr> <text | @file>
    python3 tools/audit/seat/roster_edit.py set-stage   <group> absorbed --into <host-group>
    python3 tools/audit/seat/roster_edit.py set-after   <group> <G1,G2,... | ->
    python3 tools/audit/seat/roster_edit.py drop-carry  <group> <index | --match TEXT>
    python3 tools/audit/seat/roster_edit.py mark-carry  <group> <index | --match TEXT>
        implemented <sha> | moved <GROUP> | dismissed <reason>
    python3 tools/audit/seat/roster_edit.py set-size    <group> <size> [--cite <ref>@<sha>]
    python3 tools/audit/seat/roster_edit.py set-price   <group> <minutes> --price-cite <the owner's words>
    python3 tools/audit/seat/roster_edit.py set-source  <group> <outside | ->
    python3 tools/audit/seat/roster_edit.py set-files   <group> [--add <path>...] [--set-files <p,p | ->]
        [--set-hot <p,p | ->] [--cite <ref>@<sha>]
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

The write path is a DETACHED worktree of `--checkout` (default: this
directory's repository) at `origin/<--branch>` when that exists, else at
`origin/<--roster-ref>`; the edit is committed there and pushed BY THE COMMIT
IT MADE (`<sha>:refs/heads/<--branch>`), never by a local branch name. Every
worktree of one repository shares its local branches, so a named branch is
one a concurrent run can reset under this one (`checkout -B` at git 2.38
moves a branch another worktree has checked out): on 2026-10-21 a run
printed "pushed ... at b622ec9f1" with rc 0 while the push it made sent a
rival's commit and no ref on origin ever held b622ec9f1.

THE PUSH RACE. A push origin refuses because `origin/<--branch>` moved
since this run's base (a rival landed in the lint window) re-fetches,
re-applies the op on the new tip, re-lints and pushes again, at most
PUSH_ATTEMPTS times; then it refuses with rc 2, saying nothing of the edit
reached origin. Never a force push. A refused push with origin unmoved is no
race and refuses at once. An existing worktree with uncommitted changes, or
whose HEAD is on no origin ref (an unpushed edit), is refused,
never clobbered. `write_roster()` is that path, and `roster_sync.py` writes
through it too.

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

Structural ops (wire-issue, unwire-issue, edit-brief, append-carry, set-after,
drop-carry, set-source) run only through roster_queue.py, which sets
HPO_ROSTER_LANE.

Ops (all group ids must exist, except append-group which must not):
  set-stage    sets resume.stage (and resume.commit with --at-sha); `done`
               over a pending carry is written `carries-open` and printed
               `set-stage <G>: done -> carries-open (<n> pending carries)`,
               rc 0 -- never a refusal (#2733): roster_lib.closing_stage,
               the predicate roster_sync's merge shares (set-resume --field
               stage reads it too); a closed stage (`done`, `rca-done`) --
               here or through set-resume --field stage -- whose group owns
               an open issue nothing else would own is written
               `carries-open` instead and printed HELD (carry_audit's
               `orphaned`, the `sweep --issues` test; issue states from
               `gh`, or `--issue-state FILE`);
  wire-issue   appends an integer issue (to `fixes` with --field fixes),
               refusing a duplicate;
  unwire-issue removes an integer from `issues` (default) or, with
               `--field fixes`, from `fixes`; refuses when it is not there;
  append-group inserts a validated new group (group/lane/after/brief needed,
               `after` naming known groups, resume defaulted). The argument
               is `<GROUP> <json-file>`; a leading `@` on the file is
               stripped, as append-carry and edit-brief read `@file` too.
               A new group whose `files` share a file, other than an index
               file (INDEX_FILES), with a `not-started` group is refused,
               naming each group and file, unless `--reason TEXT` is given;
               the reason is recorded in the new group's resume.note;
  edit-brief   replaces the brief (an @file argument reads the file);
  append-carry appends to the group's carry list, refusing an exact repeat
               and a destination that is closing (a DONE_STAGES stage, or
               `absorbed`, naming `absorbed_into` where it has one); a
               destination with `resume.pr` set takes the carry and prints
               `WARN carry to <G>: PR #<n> is open on it`. No gh call;
  set-resume   sets one resume field -- the free-text state a session
               restarts from. stage and branch are non-null: an empty value
               is refused. commit demands a sha. An empty value for commit,
               last_step, next_step or note clears the field to null.
  set-after    replaces the group's after-edges whole (`-` for none),
               refusing an unknown group, a self-edge, a repeated edge and
               a cycle in the resulting after-graph;
THE PRIVACY GATE. Every text an op adds (the same added_texts the triage gate
judges, plus a set-resume value) is run through ref_privacy.leaks, so a carry
naming a host path is refused at the op with a scrub hint, not at the
landing of the roster on main.

THE TRIAGE GATE (decision 0015). Every process, tooling or instrument proposal
passes dev/governance/roles/proposal-triage.md before it reaches the roster, so
the write path refuses roster text a proposal sourced that cites no ACCEPT
ruling. The text judged is what this write ADDS (a new group's brief and
carries, a changed brief, an appended carry), so every caller of
`write_roster()` -- this file's ops and roster_sync.py's carries -- passes it.
Text is proposal-sourced when it names one (`triage P<n>`, `proposal P<n>`,
any case); a citation is `triage: dev/programme/triage/<file>.md#P<n>`, read
from the edit's base (the roster branch) and else from origin/main, and must
name a `## P<n>:` entry whose `Verdict:` is ACCEPT. A citation that does not
resolve is refused whether or not the text names a proposal.

  drop-carry   removes one carry entry by 0-based index or by the one entry
               containing --match TEXT (or, among several containing it, the
               one equal to it), refusing an absent carry, an index
               out of range, no match and an ambiguous match; dropping the
               last entry leaves the `carry` list empty, never removing the
               key (27 of the 91 live groups carry `"carry": []`, and none
               omits it, so the key's presence is the file's own shape).
  mark-carry   discharges one carry (selected as drop-carry selects) by
               appending `[implemented: <sha>]`, `[moved: <GROUP>]` (an
               existing open group) or `[dismissed: <reason>]`; refuses a
               carry already marked. `implemented` records that the sha is
               on main; it is not a verification. A carry that sat on a
               closed group at roster_lib.CARRY_CUTOVER is legacy and needs
               no mark. A mark that leaves a `carries-open` group owing no
               carry writes `done` as set-stage done would, HELD at
               carries-open while it owns an open issue nothing else owns
               (`close_discharged`, then the done hold);
  set-size     writes the group's own `size`, refusing a size the duration
               model (tools/plan/durations.json) does not key -- the
               `_size_why` check append-group runs -- and, with --cite, a
               cite whose ref does not hold the sha. The old size and the
               cite go to resume.note; the current size writes nothing.
  set-price    writes the group's owner-stated price, the planner's hours for it
               (`replan.group_hours`): `owner_price_minutes` beside
               `owner_price_cite`, the owner's words. Refuses a price without
               a citation and a non-positive one -- `roster_lib.owner_price_why`,
               the definition the planner reads; the old price and the
               citation go to resume.note; the current price writes nothing.
  set-source   writes the group's `source`, a word in roster_lib.SOURCES
               (`outside`: an accepted outside request, which replan.py's
               dispatch_tier ranks in the top tier), or `-` to remove the
               key; the old value goes to resume.note, and the value already
               held writes nothing.
  set-files    writes `files` (--add appends, --set-files replaces whole, `-`
               for none) and `hot_files` (--set-hot, `-` for none) for one
               existing group. A path new to `files` must be in the tree at
               origin/main or at the cited sha; a hot token must be a
               basename of the resulting files or one some group already
               holds. Old values and the cite go to resume.note; a value
               already held writes nothing, and every other field stays
               byte-identical.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SELF = "tools/audit/seat/roster_edit.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import carry_audit  # noqa: E402  the one owned-issue test (`orphaned`)
import roster_lib  # noqa: E402  which roster: roster_lib.roster_path, the one owner
import ref_privacy  # noqa: E402  a ref or message never names this host (#2310)
TOTAL_OK = re.compile(r"TOTAL: 0 error")
SHA_RE = roster_lib.SHA_RE  # the one sha grammar, roster_lib.discharged reads it too
# Historical path first, then the moved one: the same preference as
# `test -f` in the graders. Which of the two exists is read from the
# checkout being linted.
BRIEF_LINT_OLD = ".claude/workflows/brief_lint.mjs"
BRIEF_LINT_NEW = "tools/policy/brief_lint.mjs"


#: A proposal label is `P<digits>` or, from session s4, `P-<A..Q>` (carry 0,
#: #2670): the citation grammar below names both, or a lettered label could be
#: neither refused uncited nor cited.
LABEL = r"P(?:\d+|-[A-Q])\b"
PROPOSAL_RE = re.compile(rf"\b(?:triage|proposal)\s+{LABEL}", re.I)
RULING_CITE_RE = re.compile(
    rf"\btriage:\s*(dev/programme/triage/[A-Za-z0-9_.-]+\.md)#({LABEL})")
VERDICT_LINE_RE = re.compile(r"^Verdict:\s*(ACCEPT|REJECT|DEFER)\b", re.M)


#: One push plus two re-applications on a rival's new tip; past that the
#: branch is contended enough that a person should look.
PUSH_ATTEMPTS = 3


class Refuse(Exception):
    pass


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise Refuse(f"{' '.join(cmd)} (in {cwd or '.'}) failed: "
                     f"{(r.stderr or r.stdout).strip()[:400]}")
    return r.stdout


# ----------------------------------------------------------------- ops
def op_set_stage(roster, group, stage, at_sha, rel="", legacy=None, into=None):
    g = _need(roster, group)
    if into is not None and stage != "absorbed":
        raise Refuse("set-stage: --into is for stage absorbed")
    if stage == "absorbed":
        _absorb_into(roster, group, into)
    if not isinstance(stage, str) or not stage.strip():
        raise Refuse("stage must be a non-empty string")
    why = _stage_why(stage, rel, group)
    if why:
        raise Refuse(why)
    if at_sha and not SHA_RE.match(at_sha):
        raise Refuse(f"--at-sha is not a sha: {at_sha!r}")
    g.setdefault("resume", {})["stage"] = _closing(g, stage, legacy, "set-stage")
    if stage == "absorbed":
        g["resume"]["absorbed_into"] = into
    elif "absorbed_into" in g["resume"]:
        del g["resume"]["absorbed_into"]  # no longer folded: no stale host
    _drop_stale_note(g, g["resume"]["stage"])
    if at_sha:
        g["resume"]["commit"] = at_sha


def _absorb_into(roster, group, into):
    """`set-stage G absorbed --into H`: H must be a live group other than G
    (carry 16), so carry_audit can name where G's carries went."""
    if not into:
        raise Refuse(f"set-stage: {group} absorbed needs --into <host group>")
    host = next((x for x in roster.get("groups", []) if x.get("group") == into),
                None)
    if host is None:
        raise Refuse(f"set-stage: --into {into!r} names no group")
    if into == group:
        raise Refuse(f"set-stage: {group} cannot be absorbed into itself")
    hstage = (host.get("resume") or {}).get("stage")
    if not roster_lib.carry_receivable(host):
        raise Refuse(f"set-stage: --into {into} is {hstage}, not a live group that can take "
                     "its carries (roster_lib.carry_receivable)")


#: The resume fields set-resume may write. stage and branch are the roster's
#: structural non-null fields (gen.py defaults them); commit and the
#: free-text fields are str-or-null across the live roster, so an empty
#: value clears them to null.
RESUME_FIELDS = ("stage", "commit", "branch", "last_step", "next_step",
                 "note", "pr")
NON_NULL_RESUME_FIELDS = ("stage", "branch")
TEXT_RESUME_FIELDS = ("last_step", "next_step", "note")
#: A note naming owed work is stale once the group closes (carry 2, #2559).
OWED_NOTE_RE = re.compile(r"\bOwed\b|has no pull request", re.I)


def op_set_resume(roster, group, field, value, rel="", legacy=None):
    g = _need(roster, group)
    if field not in RESUME_FIELDS:
        # argparse's --field choices refuse it first; this guards direct callers
        raise Refuse(f"unknown resume field: {field!r} "
                     f"(known: {', '.join(RESUME_FIELDS)})")
    if value == "":
        if field in NON_NULL_RESUME_FIELDS:
            raise Refuse(f"resume.{field} is a non-null field; an empty "
                         "value is refused")
        g.setdefault("resume", {})[field] = None  # clearing a nullable field
        return
    if field == "stage":
        why = _stage_why(value, rel, group)
        if why:
            raise Refuse(why)
    if field == "commit" and not SHA_RE.match(value):
        raise Refuse(f"--field commit needs a sha: {value!r}")
    if field == "pr":
        if not value.isdigit() or int(value) < 1:
            raise Refuse(f"--field pr needs a pull request number: {value!r}")
        g.setdefault("resume", {})["pr"] = int(value)
        return
    if field == "stage":
        value = _closing(g, value, legacy, "set-resume")
        _drop_stale_note(g, value)
    resume = g.setdefault("resume", {})
    resume[field] = _text(value) if field in TEXT_RESUME_FIELDS else value


def _drop_stale_note(g, stage):
    """Closing a group clears a resume.note that names owed work, and says so;
    any other note (a set-size record, say) stays (carry 2)."""
    resume = g.get("resume") or {}
    note = resume.get("note")
    if stage in roster_lib.DONE_STAGES and isinstance(note, str) \
            and OWED_NOTE_RE.search(note):
        resume["note"] = None
        print(f"{g.get('group')}: cleared the stale resume.note naming owed work: "
              f"{note[:80]!r}")


def _closing(g, stage, legacy, op):
    """The stage `op` writes for `stage`: roster_lib.closing_stage, the one
    rule roster_sync's merge applies too. A downgrade is printed with the
    issues the group wires, which stay wired; nothing is refused (#2733)."""
    wrote, pending = roster_lib.closing_stage(g, stage, legacy or {})
    if wrote != stage:
        wired = sorted(set(g.get("issues") or []) | set(g.get("fixes") or []))
        print(f"{op} {g.get('group')}: {stage} -> {wrote} "
              f"({len(pending)} pending carries)"
              + (f"; wires {' '.join(f'#{n}' for n in wired)}" if wired else ""))
    return wrote


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


#: Files an overlap does not count (carry 5): the instrument index and the
#: per-instrument notes every instrument group touches.
INDEX_FILES = ("tools/audit/seat/INSTRUMENTS.md",)
INDEX_DIRS = ("tools/audit/seat/instruments/",)


def _is_index(path):
    return path in INDEX_FILES or path.startswith(INDEX_DIRS)


def overlap_why(roster, new):
    """The not-started groups sharing a non-index file with `new`, as
    `{group: [files]}` -- the existing-groups-first rule at admission."""
    mine = {f for f in new.get("files") or [] if not _is_index(f)}
    out = {}
    for g in roster.get("groups", []):
        if (g.get("resume") or {}).get("stage") != "not-started":
            continue
        both = sorted(mine & set(g.get("files") or []))
        if both:
            out[g.get("group")] = both
    return out


def op_append_group(roster, json_file, rel="", sizes=(), reason=None):
    if json_file.startswith("@"):
        json_file = json_file[1:]
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
    stage = (new.get("resume") or {}).get("stage")
    if stage is not None:
        why = _stage_why(stage, rel, gid)
        if why:
            raise Refuse(f"append-group: {why}")
    why = _size_why(new.get("size"), sizes, rel, gid)
    if why:
        raise Refuse(f"append-group: {why}")
    after = new.get("after", [])
    if not isinstance(after, list):
        raise Refuse(f"append-group: {gid} after must be a list")
    known = {g.get("group") for g in roster.get("groups", [])}
    bad = [a for a in after if a not in known]
    if bad:
        raise Refuse(f"append-group: {gid} after names no group: {bad}")
    clash = overlap_why(roster, new)
    if clash and not (reason or "").strip():
        raise Refuse(f"append-group: {gid} shares files with not-started "
                     "group(s); fold the scope into them, or pass "
                     "--reason \"<text>\": "
                     + "; ".join(f"{k}: {', '.join(v)}"
                                 for k, v in clash.items()))
    new.setdefault("issues", [])
    new.setdefault("fixes", [])
    new.setdefault("resume", {"stage": "not-started",
                              "branch": new.get("resume", {}).get("branch")})
    if clash:
        note = f"overlap admitted ({', '.join(clash)}): {reason.strip()}"
        new["resume"]["note"] = (f"{new['resume']['note']}; {note}"
                                 if new["resume"].get("note") else note)
    roster.setdefault("groups", []).append(new)


def op_set_source(roster, group, source):
    """Write `source` (roster_lib.SOURCES), or drop it for `-`."""
    g = _need(roster, group)
    new = None if source == "-" else source
    if new is not None and new not in roster_lib.SOURCES:
        raise Refuse(f"set-source: {source!r} is not a source; one of "
                     f"{', '.join(roster_lib.SOURCES)}, or - for none")
    old = g.get("source")
    if old == new:
        return
    if new is None:
        del g["source"]
    else:
        g["source"] = new
    _note_append(g, f"set-source {old or 'unset'} -> {new or 'unset'}")


def op_edit_brief(roster, group, text):
    _need(roster, group)["brief"] = _text(text)


def op_append_carry(roster, group, text):
    g = _need(roster, group)
    resume = g.get("resume") or {}
    stage = resume.get("stage")
    if not roster_lib.carry_receivable(g):
        into = resume.get("absorbed_into")
        raise Refuse(f"append-carry: {group} is {stage}"
                     + (f", absorbed into {into}: carry to {into}"
                        if stage == "absorbed" and into else
                        "" if stage in roster_lib.CARRY_DEST_CLOSED else
                        ", a receiver only (no PR, issue or fix; files [])")
                     + "; a carry goes to the live group owning the seam, else the producing group keeps the fix")
    if resume.get("pr"):
        print(f"WARN carry to {group}: PR #{resume['pr']} is open on it")
    entry = _text(text)
    mark = roster_lib.carry_mark(entry)
    if mark:
        raise Refuse(f"append-carry: the text already ends in a [{mark[0]}: "
                     f"{mark[1]}] mark, which reads as discharged on arrival; "
                     "strip it and let the discharging op write it")
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
    Dropping the last entry leaves `carry` empty and the key in place; a
    group that already carries a list (all 91 live ones do) is therefore
    byte-restored by append-then-drop of the appended entry."""
    g = _need(roster, group)
    del g["carry"][_carry_index(g, index, match, "drop-carry")]


def _carry_index(g, index, match, op):
    """The one carry entry `op` names: by 0-based index or by the one entry
    containing `match`, or the one entry equal to it when several contain it
    (a bare carry kept beside its "From #N, ..." duplicate); absent, out of
    range, unmatched and ambiguous refuse."""
    group, carry = g.get("group"), g.get("carry") or []
    if not carry:
        raise Refuse(f"{op}: {group} carries nothing")
    if match is not None:
        hits = [i for i, c in enumerate(carry) if match in c]
        if not hits:
            raise Refuse(f"{op}: no carry entry matches {match!r} "
                         f"in {group}")
        exact = [i for i in hits if carry[i] == match]
        if len(exact) == 1:
            return exact[0]
        if len(hits) > 1:
            raise Refuse(f"{op}: {match!r} is ambiguous in {group}: "
                         f"entries {hits} match; pass an index")
        return hits[0]
    try:
        i = int(index)
    except ValueError:
        raise Refuse(f"{op}: index must be an integer: {index!r}")
    if not 0 <= i < len(carry):
        raise Refuse(f"{op}: index {i} out of range for {group} "
                     f"({len(carry)} entries)")
    return i


def op_mark_carry(roster, group, index, match, kind, arg):
    """Discharge one carry by appending its mark (roster_lib.carry_mark's
    grammar), so roster_lib.pending_carries stops counting it."""
    g = _need(roster, group)
    i = _carry_index(g, index, match, "mark-carry")
    if roster_lib.carry_mark(g["carry"][i]):
        raise Refuse(f"mark-carry: {group} carry[{i}] is already marked "
                     f"{roster_lib.carry_mark(g['carry'][i])}")
    if kind not in roster_lib.CARRY_MARKS:
        raise Refuse(f"mark-carry: the mark is one of "
                     f"{', '.join(roster_lib.CARRY_MARKS)}, not {kind!r}")
    arg = " ".join((arg or "").split())
    if kind == "implemented" and not SHA_RE.match(arg):
        raise Refuse(f"mark-carry: implemented needs a sha: {arg!r}")
    if kind == "moved":
        dest = next((x for x in roster.get("groups", [])
                     if x.get("group") == arg), None)
        if dest is None:
            raise Refuse(f"mark-carry: moved {arg!r} names no group")
        if arg == group:
            raise Refuse(f"mark-carry: {group} cannot move a carry to itself")
        stage = (dest.get("resume") or {}).get("stage")
        if not roster_lib.carry_receivable(dest):
            raise Refuse(f"mark-carry: moved {arg} is {stage}, not a group that can take "
                         "a carry (roster_lib.carry_receivable); a carry goes to the live group owning the seam, else the producing group keeps the fix")
    if kind == "dismissed" and not arg:
        raise Refuse("mark-carry: dismissed needs a reason")
    if "]" in arg:
        raise Refuse(f"mark-carry: a mark's value holds no ']': {arg!r}")
    g["carry"][i] = f"{g['carry'][i]} [{kind}: {arg}]"


def apply_op(roster, op, group, value, field, at_sha, match=None, rel="",
             sizes=(), legacy=None, rest=(), into=None, reason=None):
    """One op on a loaded roster -- re-run on each attempt of a push race,
    so the edit is applied to the tip it is pushed onto. `rel` is the roster's
    path and `sizes` the duration model's vocabulary, for a refusal to name
    what it refused; only append-group reads `sizes`. `legacy` is the
    roster's cut-over carries (roster_lib.read_legacy), which a stage write
    reads; `rest` is mark-carry's `<kind> <value...>`."""
    if op == "set-stage":
        op_set_stage(roster, group, value, at_sha, rel, legacy, into)
    elif op == "wire-issue":
        op_wire_issue(roster, group, value, field or "issues")
    elif op == "unwire-issue":
        op_unwire_issue(roster, group, value, field or "issues")
    elif op == "append-group":
        op_append_group(roster, value, rel, sizes, reason)
    elif op == "edit-brief":
        op_edit_brief(roster, group, value)
    elif op == "set-resume":
        op_set_resume(roster, group, field, value, rel, legacy)
    elif op == "set-after":
        op_set_after(roster, group, value)
    elif op == "drop-carry":
        op_drop_carry(roster, group, value, match)
    elif op == "set-source":
        op_set_source(roster, group, value)
    elif op == "mark-carry":
        kind, *arg = list(rest) or [""]
        op_mark_carry(roster, group, value, match, kind, " ".join(arg))
    else:
        op_append_carry(roster, group, value)


def close_discharged(roster, group, legacy) -> bool:
    """After a mark: a `carries-open` group the mark left owing no carry is
    written as `set-stage done` writes it (`_closing`; the caller then runs
    `hold_done`, so a group that would orphan an open issue stays held and the
    issues are printed). It closes the record lag `roster_lib.discharged`
    otherwise leaves for a hand `set-stage done` (tvofi 2026-11-07, proposal
    1). Any other stage is untouched: an unmerged group's brief is undone."""
    g = _need(roster, group)
    resume = g.get("resume") or {}
    if resume.get("stage") != HOLD_STAGE or roster_lib.pending_carries(g, legacy or {}):
        return False
    resume["stage"] = _closing(g, "done", legacy, "mark-carry")
    _drop_stale_note(g, resume["stage"])
    print(f"mark-carry {group}: the last pending carry is discharged: "
          f"{HOLD_STAGE} -> {resume['stage']}")
    return True


#: What a closed stage is written as while its group would orphan an issue.
HOLD_STAGE = "carries-open"


def hold_done(roster, group, worktree, read_state) -> list[int]:
    """After a write of a closed stage: when `group` owns an open issue no
    other live owner holds, its stage becomes HOLD_STAGE and the issues are
    returned. The test is carry_audit's (`orphaned`) on the edited roster, so
    the closing group owns nothing there; the carry files are the worktree's
    and the O-briefs $HPO_BRIEFS_DIR's, as carry_audit itself reads them."""
    g = _need(roster, group)
    if (g.get("resume") or {}).get("stage") not in roster_lib.DONE_STAGES:
        return []
    dests = carry_audit.Dests(roster, carry_audit.carry_issues(worktree),
                              os.environ.get("HPO_BRIEFS_DIR"), read_state)
    held = carry_audit.orphaned(dests, g)
    if held:
        g["resume"]["stage"] = HOLD_STAGE
    return held


def _stage_why(stage, rel, group):
    """Why `stage` may not be written for `group`, or None.

    THE VOCABULARY BARRIER (R10-ORCH-ROSTER-SCHEMA). A stage word is legal only
    if `roster_lib.STAGE_KIND` classifies it: every classified derivable word is
    one the reconciler may close (a merge makes it `done`), a live claim is one
    it closes on the merge, and a disposition is one it deliberately leaves
    alone. A word outside the registry is one the writer and the reader would
    have to agree on twice -- the drift that put `in-review` in a roster with no
    rule to close it, and `XS` in a roster the planner could not price.
    """
    if stage in roster_lib.STAGES:
        return None
    return (f"stage {stage!r} for {group} is not a classified roster stage "
            f"(classified: {', '.join(roster_lib.STAGES)}) in "
            f"{rel or 'the roster'}")


def _size_why(size, sizes, rel, group):
    """Why `size` may not be written for `group`, or None. The duration model
    IS the size vocabulary: a size it lacks makes `replan.build_plan` raise
    KeyError at `size_hours[...]`, which no gate reads."""
    if size is None or size in sizes:
        return None
    return (f"size {size!r} for {group} is not in the durations model "
            f"({', '.join(sizes) or 'no sizes'}) at {roster_lib.DURATIONS} in "
            f"{rel or 'the roster'}")


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


# --------------------------------------------- set-size / set-files
# R10-ROSTER-OPS-2 part 1. One op pair for the fields a group owns outright --
# `size` and `files`/`hot_files` -- each in its own functions so the write path
# above is untouched. A change records what it replaced, and the cite it
# rests on, in resume.note; a change to the value already held writes nothing.
CITE_RE = re.compile(r"\A([A-Za-z0-9._/-]+)@([0-9a-f]{7,40})\Z")


def _git_ok(checkout, *args) -> bool:
    return subprocess.run(["git", "-C", str(checkout), *args],
                          capture_output=True).returncode == 0


def cite_why(cite, checkout):
    """Why `cite` (`<ref>@<sha>`) is not a ref that holds that sha, or None."""
    m = CITE_RE.match(cite)
    if not m:
        return f"cite {cite!r} is not <ref>@<sha>"
    ref, sha = m.groups()
    if _git_ok(checkout, "cat-file", "-e", f"{sha}^{{commit}}"):
        for cand in (f"origin/{ref}", ref):
            if _git_ok(checkout, "rev-parse", "--verify", "--quiet",
                       f"{cand}^{{commit}}") \
                    and _git_ok(checkout, "merge-base", "--is-ancestor",
                                sha, cand):
                return None
    return f"cite ref {ref!r} does not hold {sha}"


def path_in_tree(checkout, path, cite=None) -> bool:
    """Whether `path` is in the tree at origin/main or at the cited sha."""
    revs = ["origin/main"] + ([CITE_RE.match(cite).group(2)] if cite else [])
    return any(_git_ok(checkout, "cat-file", "-e", f"{r}:{path}")
               for r in revs)


def _note_append(g, text):
    resume = g.setdefault("resume", {})
    resume["note"] = f"{resume['note']} | {text}" if resume.get("note") else text


def _cited(text, cite):
    return f"{text} (cite {cite})" if cite else text


def op_set_size(roster, group, size, sizes, rel="", cite=None, cite_check=None):
    """Write a group's own `size`, vocabulary-checked against the duration
    model by `_size_why`; the old size and the cite go to resume.note."""
    g = _need(roster, group)
    if not size:
        raise Refuse(f"set-size: {group} needs a size")
    why = _size_why(size, sizes, rel, group)
    if why:
        raise Refuse(f"set-size: {why}")
    if cite is not None and cite_check:
        why = cite_check(cite)
        if why:
            raise Refuse(f"set-size: {why}")
    old = g.get("size")
    if old == size:
        return
    g["size"] = size
    _note_append(g, _cited(f"set-size {old or 'unset'} -> {size}", cite))


def op_set_price(roster, group, minutes, price_cite):
    """Write a group's owner-stated price (`roster_lib.OWNER_PRICE_MINUTES`
    beside `OWNER_PRICE_CITE`), validated by `roster_lib.owner_price_why`."""
    g = _need(roster, group)
    try:
        value = float(minutes)
    except (TypeError, ValueError):
        raise Refuse(f"set-price: {group}: minutes {minutes!r} is not a number")
    if value == value and abs(value) != float("inf") and value == int(value):
        value = int(value)
    why = roster_lib.owner_price_why(value, price_cite)
    if why:
        raise Refuse(f"set-price: {group}: {why}")
    price_cite = price_cite.strip()
    old = g.get(roster_lib.OWNER_PRICE_MINUTES)
    if old == value and g.get(roster_lib.OWNER_PRICE_CITE) == price_cite:
        return
    g[roster_lib.OWNER_PRICE_MINUTES] = value
    g[roster_lib.OWNER_PRICE_CITE] = price_cite
    _note_append(g, f"set-price {old if old is not None else 'unset'} -> {value} min "
                    f"(cite {price_cite})")


def _paths(spec, what):
    if spec == "-":
        return []
    out = [p.strip() for p in spec.split(",") if p.strip()]
    repeated = sorted({p for p in out if out.count(p) > 1})
    if repeated:
        raise Refuse(f"set-files: duplicate {what}: {repeated}")
    return out


def op_set_files(roster, group, add=(), set_files=None, set_hot=None,
                 cite=None, cite_check=None, in_tree=None):
    """Write a group's `files` (`--add` appends, `--set-files` replaces whole,
    `-` for none) and `hot_files` (`--set-hot`, `-` for none). A path new to
    `files` must be in the tree (`in_tree`); a hot token must be a basename of
    the group's resulting files or one some group already holds."""
    g = _need(roster, group)
    if not add and set_files is None and set_hot is None:
        raise Refuse("set-files needs --add, --set-files or --set-hot")
    if cite is not None and cite_check:
        why = cite_check(cite)
        if why:
            raise Refuse(f"set-files: {why}")
    old_files, old_hot = list(g.get("files") or []), list(g.get("hot_files") or [])
    files = list(old_files)
    if set_files is not None:
        files = _paths(set_files, "path")
    files += [p for p in dict.fromkeys(add) if p not in files]
    for p in files:
        if p not in old_files and in_tree and not in_tree(p, cite):
            raise Refuse(f"set-files: {p!r} is not in the tree at origin/main"
                         + (f" or at {cite}" if cite else ""))
    hot = old_hot
    if set_hot is not None:
        hot = _paths(set_hot, "hot token")
        known = {t for x in roster.get("groups", [])
                 for t in x.get("hot_files") or []}
        base = {f.rstrip("/").rsplit("/", 1)[-1] for f in files} | set(files)
        bad = [t for t in hot if t not in base and t not in known]
        if bad:
            raise Refuse(f"set-files: hot_files token {bad} is neither a files "
                         f"basename of {group} nor a known hot-file token")
    notes = []
    if files != old_files:
        g["files"] = files
        notes.append(f"files {old_files} -> {files}")
    if hot != old_hot:
        g["hot_files"] = hot
        notes.append(f"hot_files {old_hot} -> {hot}")
    if notes:
        _note_append(g, _cited("set-files " + "; ".join(notes), cite))


def apply_files_op(roster, a, value, rel, checkout, worktree):
    """The set-size / set-files dispatch `main` calls beside `apply_op`."""
    cite_check = lambda c: cite_why(c, checkout)
    if a.op == "set-size":
        try:
            sizes = roster_lib.sizes(roster_lib.read_durations(worktree))
        except roster_lib.SchemaError as e:
            raise Refuse(str(e))
        op_set_size(roster, a.group, value, sizes, rel, a.cite, cite_check)
    else:
        op_set_files(roster, a.group, a.add or (), a.set_files, a.set_hot,
                     a.cite, cite_check,
                     lambda p, c: path_in_tree(checkout, p, c))


def added_texts(before, after):
    """The roster text `after` adds over `before`: a new group's brief and
    carries, a changed brief, and carry entries `before` did not hold."""
    old = {g.get("group"): g for g in before.get("groups", [])}
    out = []
    for g in after.get("groups", []):
        o = old.get(g.get("group"))
        carry = g.get("carry") or []
        if o is None:
            out += [g.get("brief") or "", *carry]
            continue
        if g.get("brief") != o.get("brief"):
            out.append(g.get("brief") or "")
        held = o.get("carry") or []
        out += [c for c in carry if c not in held]
    return [x for x in out if isinstance(x, str) and x]


def added_resume(before, after):
    """The resume free text `after` sets over `before`: set-resume's values and
    an append-group's resume.note, the other texts an op writes."""
    old = {g.get("group"): (g.get("resume") or {}) for g in before.get("groups", [])}
    out = []
    for g in after.get("groups", []):
        o = old.get(g.get("group"), {})
        for f in TEXT_RESUME_FIELDS:
            v = (g.get("resume") or {}).get(f)
            if isinstance(v, str) and v and v != o.get(f):
                out.append(v)
    return out


def privacy_refusal(texts):
    """Why the added `texts` may not land, or None: ref_privacy's leak classes,
    the check prepr.sh runs when the roster lands on main (carry 7)."""
    ident = ref_privacy.Identity.of_host()
    for text in texts:
        why = ref_privacy.leaks(text, ident)
        if why:
            return (f"{', '.join(why)} in {text[:80]!r}; scrub the path "
                    "(name the file repo-relative, or cite its sha)")
    return None


def ruling_verdict(src, pid):
    """The `Verdict:` of the `## <pid>:` entry in a triage batch file: ACCEPT,
    REJECT or DEFER; None when no such entry; "unreadable" when it has no
    verdict line."""
    m = re.search(rf"^## {re.escape(pid)}:.*?$(.*?)(?=^## |\Z)", src, re.M | re.S)
    if not m:
        return None
    v = VERDICT_LINE_RE.search(m.group(1))
    return v.group(1) if v else "unreadable"


def triage_refusal(texts, read_ruling):
    """Why the added `texts` may not land, or None. `read_ruling(path)` is the
    batch file's source, or None when it does not exist."""
    for text in texts:
        cites = RULING_CITE_RE.findall(text)
        if PROPOSAL_RE.search(text) and not cites:
            return (f"proposal-sourced text cites no triage ruling "
                    f"(`triage: dev/programme/triage/<file>.md#P<n>`): {text[:120]!r}")
        for path, pid in cites:
            src = read_ruling(path)
            if src is None:
                return f"the triage ruling {path} is not on the roster branch or origin/main"
            verdict = ruling_verdict(src, pid)
            if verdict != "ACCEPT":
                return (f"{path}#{pid} is not an ACCEPT ruling "
                        f"({'no such entry' if verdict is None else verdict})")
    return None


def ruling_reader(worktree, checkout):
    """A triage batch file from the edit's base, else from origin/main."""
    def read(rel):
        f = Path(worktree) / rel
        if f.is_file():
            return f.read_text(encoding="utf-8")
        r = subprocess.run(["git", "-C", str(checkout), "show", f"origin/main:{rel}"],
                           capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    return read


# ----------------------------------------------------------------- flow
def _on_origin(checkout, wt, sha, branch) -> bool:
    """Whether some origin ref holds `sha`. The local tracking refs go stale
    when a rival writer pushes the roster branch, so a miss fetches the
    branch once and asks again before an unpushed edit is declared."""
    def held():
        return bool(run(["git", "-C", str(wt), "for-each-ref", "--contains",
                         sha, "--format=%(refname)",
                         "refs/remotes/origin/"]).strip())
    if held():
        return True
    subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "origin",
                    f"+refs/heads/{branch}:refs/remotes/origin/{branch}"],
                   capture_output=True)
    return held()


def prepare_worktree(checkout, ref, branch, wt, discard=None) -> str:
    """A throwaway DETACHED worktree at the branch's remote tip when one
    exists (so sequential edits accumulate), else at origin/<ref>; returns
    that base sha. No local branch is made or moved: the repository's
    branches are shared by every worktree of it, so one a concurrent run can
    reset (the module docstring's push race). The guards refuse anything
    that would clobber work: uncommitted changes, and a HEAD the base does
    no origin ref contains (an unpushed edit) -- except `discard`, this run's own
    commit that lost a race and is being re-applied. The caller fetches
    first (`fetch_origin`)."""
    base = f"origin/{ref}"
    has_branch = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "--verify", "--quiet",
         f"origin/{branch}"], capture_output=True)
    if has_branch.returncode == 0:
        base = f"origin/{branch}"
    base_sha = run(["git", "-C", str(checkout), "rev-parse",
                    f"{base}^{{commit}}"]).strip()
    if Path(wt).exists():
        if run(["git", "-C", str(wt), "status", "--porcelain"]).strip():
            raise Refuse(f"{wt} has uncommitted changes; refusing to reuse it")
        old = run(["git", "-C", str(wt), "rev-parse", "HEAD"]).strip()
        if old != discard and not _on_origin(checkout, wt, old, branch):
            raise Refuse(f"{wt} HEAD {old[:12]} is on no origin ref; an "
                         "unpushed edit would be lost")
        run(["git", "-C", str(wt), "checkout", "-q", "--detach", base_sha])
    else:
        run(["git", "-C", str(checkout), "worktree", "add", "-q", "--detach",
             str(wt), base_sha])
    return base_sha


#: Four attempts, sleeping between them. A ref-lock race lasts the
#: milliseconds between another process's read and write of one
#: remote-tracking ref, so the first sleep is already longer than the window;
#: the measured rate (about 1 pass in 100, the beat log) puts four
#: independent attempts near 1e-8. Past the bound the refusal stands.
FETCH_ATTEMPTS = 4
FETCH_BACKOFF = (0.25, 0.5, 1.0)
#: One line git prints when another process moved a ref between the fetch's
#: read and its write.
LOCK_RACE_RE = re.compile(
    r"\Aerror: cannot lock ref '[^']+': is at [0-9a-f]+ but expected [0-9a-f]+\Z")


def _fetch_once(checkout):
    r = subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "origin",
                        "+refs/heads/*:refs/remotes/origin/*"],
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _is_lock_race(rc, out, err) -> bool:
    """True only when git failed and every line it printed is the lock race:
    any other line is a real failure and is never retried."""
    lines = [x.strip() for x in (err + out).splitlines() if x.strip()]
    return rc != 0 and bool(lines) and all(LOCK_RACE_RE.match(x) for x in lines)


def fetch_origin(checkout) -> None:
    """Fetch every origin head. A ref-lock race (another process sharing the
    repository moved a remote-tracking ref mid-fetch) is transient: retried
    with a short backoff, `FETCH_ATTEMPTS` at most. Any other failure, and a
    race outlasting the bound, refuses as before."""
    for attempt in range(FETCH_ATTEMPTS):
        rc, out, err = _fetch_once(checkout)
        if rc == 0:
            return
        if attempt + 1 == FETCH_ATTEMPTS or not _is_lock_race(rc, out, err):
            break
        time.sleep(FETCH_BACKOFF[attempt])
    raise Refuse(f"git -C {checkout} fetch -q origin "
                 f"+refs/heads/*:refs/remotes/origin/* (in .) failed: "
                 f"{(err or out).strip()[:400]}")


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


ERROR_LINE = re.compile(r"^\s*ERROR\b.*$", re.M)
TOTAL_N = re.compile(r"TOTAL: (\d+) error")


def _lint_errors(out):
    """(the ERROR lines of one lint run, whether they account for its TOTAL).
    A failure the lines do not account for (a problem printed in another
    shape) cannot be attributed to a write, so the gate refuses it whole."""
    errs = [m.group(0).strip() for m in ERROR_LINE.finditer(out)]
    m = TOTAL_N.search(out)
    return errs, bool(m) and int(m.group(1)) == len(errs)


def lint_gate(checkout, lint_cwd, roster_path, base_text=None):
    """brief_lint from a fresh origin/main checkout. Returns (ok, detail).

    With `base_text` (the roster as the write found it) the gate refuses only
    the ERROR lines the same lint over that base does not print: a merge to
    main that moves a line one brief cites must not stop a write that never
    touches that brief (P435). Each pre-existing error is returned in `detail`
    as a WARN naming its group, for the owner to re-pin."""
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
        if ok or base_text is None:
            return ok, tail
        errs, whole = _lint_errors(out)
        if not whole:
            return False, tail
        bdir = tempfile.mkdtemp(prefix="hpo-lint-base-")
        try:
            bpath = Path(bdir) / Path(roster_path).name
            bpath.write_text(base_text, encoding="utf-8")
            br = subprocess.run(["node", script, str(bpath)], cwd=lint_cwd,
                                capture_output=True, text=True)
            base_errs, _ = _lint_errors(br.stdout + br.stderr)
        finally:
            shutil.rmtree(bdir, ignore_errors=True)
        new = [e for e in errs if e not in base_errs]
        if new:
            return False, "\n".join(new + [tail])
        warn = "\n".join(f"WARN pre-existing, re-pin owed: {e}" for e in errs)
        return True, warn
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


def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                 lint_cwd, label, edit) -> int:
    """THE write path: worktree, edit, dump, commit, lint-gate, push -- shared
    by every caller, so `main()` and `roster_sync.py` cannot drift apart in
    formatting, the no-op rule, the gate or the push race.

    `edit(roster, rel)` applies the caller's ops to the roster loaded at the
    base, `rel` being that roster's path (so a refusal names it), and returns
    whether there is anything to write; it is re-run on every attempt of a push
    race, so the edit lands on the tip it is pushed onto.
    Returns 0 or 3 (the lint gate refused); a failed git command, or a race
    lost PUSH_ATTEMPTS times, raises Refuse, which each caller prints.

    The round-trip rule: a write that reproduces the roster's own bytes
    commits and pushes nothing and is still a success, so a re-run of an op
    -- or a sync pass with nothing to derive -- is idempotent.
    """
    discard = None
    for attempt in range(1, PUSH_ATTEMPTS + 1):
        base_sha = prepare_worktree(checkout, ref, branch, worktree, discard)
        try:
            rel = roster_lib.roster_path(str(worktree), None, roster_path)
        except roster_lib.RosterNotFound as e:
            raise Refuse(str(e))
        path = Path(worktree) / rel
        print(f"roster: {rel} on {branch}")
        base_text = path.read_text(encoding="utf-8")
        roster = json.loads(base_text)
        before = json.loads(base_text)
        if not edit(roster, rel):
            return 0
        why = triage_refusal(added_texts(before, roster),
                             ruling_reader(worktree, checkout))
        if why:
            raise Refuse(f"triage gate: {why}; nothing written")
        why = privacy_refusal(added_texts(before, roster) + added_resume(before, roster))
        if why:
            raise Refuse(f"privacy gate: {why}; nothing written")
        path.write_text(dump(roster), encoding="utf-8")
        if not run(["git", "-C", str(worktree), "status", "--porcelain"]).strip():
            print(f"no change: {label} wrote the roster's own bytes "
                  "(byte-identical); nothing to commit or push")
            return 0
        run(["git", "-C", str(worktree), "commit", "-q", "-am", msg])
        head = run(["git", "-C", str(worktree), "rev-parse", "HEAD"]).strip()
        refspec = f"{head}:refs/heads/{branch}"
        ok, detail = lint_gate(checkout, lint_cwd, path, base_text)
        if ok and detail:
            print(detail, file=sys.stderr)
        if not ok:
            print(f"roster_edit: LINT GATE REFUSED the push\n{detail}\n"
                  f"the commit is local at {head[:12]} in {worktree} "
                  "(detached); nothing pushed", file=sys.stderr)
            return 3
        print("lint gate: TOTAL: 0 error(s) from a fresh origin/main checkout")
        if not push:
            print(f"ready: {branch} at {head} (no --push): "
                  f"git -C {worktree} push origin {refspec}")
            return 0
        r = subprocess.run(["git", "-C", str(worktree), "push", "-q",
                            "origin", refspec],
                           capture_output=True, text=True)
        if r.returncode == 0:
            # our own push: the tracking ref must follow it, or the next op
            # in this run finds HEAD on no origin ref
            subprocess.run(["git", "-C", str(checkout), "update-ref",
                            f"refs/remotes/origin/{branch}", head],
                           capture_output=True)
            print(f"pushed {branch} at {head}")
            return 0
        why = (r.stderr or r.stdout).strip()[:400]
        fetch_origin(checkout)
        tip = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "--verify",
             "--quiet", f"origin/{branch}"],
            capture_output=True, text=True).stdout.strip()
        if not tip or tip == base_sha:
            raise Refuse(f"push of {head[:12]} to {branch} failed with "
                         f"origin unmoved (no race); nothing of this edit "
                         f"reached origin: {why}")
        print(f"roster_edit: lost a race: origin/{branch} moved "
              f"{base_sha[:12]} -> {tip[:12]} under this edit; "
              f"re-applying {label} on the new tip "
              f"(attempt {attempt + 1} of {PUSH_ATTEMPTS})",
              file=sys.stderr)
        discard = head
    raise Refuse(f"lost the race for {branch} {PUSH_ATTEMPTS} times; "
                 "nothing of this edit reached origin")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                  "edit-brief", "append-carry", "set-resume",
                                  "set-after", "drop-carry", "mark-carry",
                                  "set-size", "set-files", "set-source", "set-price"))
    p.add_argument("group")
    p.add_argument("value", nargs="?")
    p.add_argument("rest", nargs="*",
                   help="mark-carry: implemented <sha> | moved <GROUP> | "
                        "dismissed <reason>")
    p.add_argument("--at-sha")
    p.add_argument("--field", choices=RESUME_FIELDS + WIRE_FIELDS,
                   help="set-resume: which resume field to write; "
                        "unwire-issue: issues (default) or fixes")
    p.add_argument("--into", help="set-stage absorbed: the live host group")
    p.add_argument("--reason", help="append-group: why the new group shares "
                   "files with a not-started group; recorded in resume.note")
    p.add_argument("--value", dest="value_opt",
                   help="the value, for when a positional value does not fit")
    p.add_argument("--match",
                   help="drop-carry, mark-carry: the one carry entry "
                        "containing it")
    p.add_argument("--cite", help="set-size / set-files: <ref>@<sha>, a ref "
                   "that must hold the sha; recorded in resume.note")
    p.add_argument("--price-cite", help="set-price: the owner's words the "
                   "price rests on; required")
    p.add_argument("--add", nargs="+", action="extend",
                   help="set-files: paths appended to files; repeatable "
                        "(the default store action kept only the last list)")
    p.add_argument("--set-files", help="set-files: replace files whole "
                   "(comma list, - for none)")
    p.add_argument("--set-hot", help="set-files: replace hot_files whole "
                   "(comma list, - for none)")
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
    p.add_argument("--issue-state",
                   help="JSON object issue -> open|closed: the states the done "
                        "hold reads instead of gh (no network)")
    return p


def parse_op(argv):
    """The parsed `argv` of one op: (args, value, rest). The one
    grammar `main` and a batch (roster_queue.py run --batch) share."""
    p = build_parser()
    a = p.parse_intermixed_args(argv)
    rest = list(a.rest)
    if a.op == "mark-carry" and a.match is not None and a.value is not None:
        # with --match there is no index: the first positional is the kind
        rest, a.value = [a.value] + rest, None
    if rest and a.op != "mark-carry":
        p.error(f"{a.op} takes one value; extra arguments: {rest}")
    if a.op == "mark-carry" and not rest:
        p.error("mark-carry needs implemented <sha>, moved <GROUP> or "
                "dismissed <reason>")
    if a.value is not None and a.value_opt is not None:
        p.error("give the value positionally or with --value, not both")
    value = a.value_opt if a.value is None else a.value
    if a.match is not None and a.op not in ("drop-carry", "mark-carry"):
        p.error("--match is a drop-carry flag")
    if a.op == "drop-carry" and value is not None and a.match is not None:
        p.error("drop-carry takes an index or --match, not both")
    if a.op in ("drop-carry", "mark-carry") and value is None and a.match is None:
        p.error(f"{a.op} needs an index or --match")
    if a.op == "set-files" and value is not None:
        p.error("set-files takes --add, --set-files or --set-hot, no value")
    if a.into is not None and a.op != "set-stage":
        p.error("--into is a set-stage flag")
    if a.reason is not None and a.op != "append-group":
        p.error("--reason is an append-group flag")
    if a.op != "set-price" and a.price_cite is not None:
        p.error("--price-cite is a set-price flag")
    if a.op not in ("set-size", "set-files") and a.cite:
        p.error("--cite is a set-size / set-files flag")
    if a.op != "set-files" and (a.add or a.set_files is not None
                                or a.set_hot is not None):
        p.error("--add, --set-files and --set-hot are set-files flags")
    if a.op != "set-files" and a.match is None and (
            value is None or (value == "" and a.op not in ("set-resume",
                                                           "set-size"))):
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
    return a, value, rest


def make_edit(a, value, rest):
    """The `edit(roster, rel)` callback of one parsed op, for write_roster."""
    def edit(roster, rel) -> bool:
        sizes = ()
        if a.op == "append-group":
            # The size vocabulary comes from the tree the roster lands in,
            # not from this tool's: an XS appended while durations.json
            # lacked it is the second half of this class.
            try:
                sizes = roster_lib.sizes(
                    roster_lib.read_durations(a.worktree))
            except roster_lib.SchemaError as e:
                raise Refuse(str(e))
        if a.op == "set-price":
            op_set_price(roster, a.group, value, a.price_cite)
            return True
        if a.op in ("set-size", "set-files"):
            apply_files_op(roster, a, value, rel, a.checkout, a.worktree)
            return True
        legacy = None
        if a.op in ("set-stage", "set-resume", "mark-carry"):
            try:
                legacy = roster_lib.read_legacy(a.worktree, rel)
            except roster_lib.RosterNotFound as e:
                raise Refuse(f"the carry cut-over is unreadable, so no "
                             f"stage is written: {e}")
        apply_op(roster, a.op, a.group, value, a.field, a.at_sha, a.match,
                 rel, sizes, legacy, rest, a.into, a.reason)
        closed = a.op == "mark-carry" and close_discharged(roster, a.group, legacy)
        if closed or a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):
            try:
                held = hold_done(roster, a.group, a.worktree, carry_audit.issue_reader(
                    roster.get("repo") or carry_audit.REPO, a.issue_state))
            except (ValueError, SystemExit) as e:  # carry_audit's refusals
                raise Refuse(f"the done hold cannot read issue state: {e}")
            if held:
                print(f"roster_edit: HELD {a.group} at {HOLD_STAGE}, not "
                      f"{'done' if closed else value}: "
                      f"it owns open {', '.join(f'#{n}' for n in held)} with no other "
                      "live owner; wire each to its next owner or close it, then "
                      "set the stage again", file=sys.stderr)
        return True
    return edit


def batch_edit(edits):
    """One `edit(roster, rel)` for write_roster that applies several parsed
    ops (make_edit callbacks) in order, so a batch costs one lint and one
    push (roster_queue.py run --batch). An op that refuses is rolled back and
    skipped, its reason in `results[i]` (None: applied); the batch writes when
    any applied. Re-run on a push race, `results` is rewritten each time."""
    results = [None] * len(edits)

    def edit(roster, rel) -> bool:
        for i, one in enumerate(edits):
            snap = copy.deepcopy(roster)
            try:
                one(roster, rel)
                results[i] = None
            except Refuse as e:
                roster.clear()
                roster.update(snap)
                results[i] = str(e)
        return any(r is None for r in results)
    return edit, results


# The roster seat's lane (P215): the queue runner sets LANE_ENV in the child's
# environment; the structural ops refuse any caller that does not carry it.
LANE_ENV, LANE_VALUE = "HPO_ROSTER_LANE", "queue-runner"
STRUCTURAL_OPS = ("wire-issue", "unwire-issue", "edit-brief", "append-carry",
                  "set-after", "drop-carry", "set-source")


def lane_refusal(op, group):
    """The refusal text for a structural op called outside the roster queue
    runner, else None. set-stage, append-group and set-resume stay directly
    callable (nudge.md and sweep_template.md run them by hand). A caller that
    sets the variable by hand is out of scope: the guard stops a caller that
    does not know the lane, not one that forges it."""
    if op in STRUCTURAL_OPS and os.environ.get(LANE_ENV) != LANE_VALUE:
        return (f"{op} {group} is the roster seat's lane: queue it and run "
                f"tools/audit/seat/roster_queue.py (it sets {LANE_ENV}); "
                f"nothing written")
    return None


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if "--self-test" in argv:
        # Every git call in the self-test, the runner's and the ops' under
        # test, runs in a throwaway repository: all of them take the env.
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_environ
        with throwaway_git_environ():
            # the fixtures call the ops directly as the queue runner would
            keep = os.environ.get(LANE_ENV)
            os.environ[LANE_ENV] = LANE_VALUE
            try:
                return _self_test()
            finally:
                if keep is None:
                    os.environ.pop(LANE_ENV, None)
                else:
                    os.environ[LANE_ENV] = keep
    a, value, rest = parse_op(argv)
    try:
        why = lane_refusal(a.op, a.group)
        if why:
            raise Refuse(why)
        fetch_origin(a.checkout)
        ref, branch = roster_target(a.checkout, a.roster_ref, a.branch,
                                    a.roster_path)
        msg = a.message or f"roster_edit {a.op} {a.group} ({SELF})"
        why = ref_privacy.refusal(branch, (("the message", msg),))
        if why:
            raise Refuse(f"{why} would publish this host (#2310); nothing written")
        edit = make_edit(a, value, rest)
        return write_roster(a.checkout, ref, branch, a.worktree, a.roster_path,
                            msg, a.push, a.lint_cwd, f"{a.op} {a.group}", edit)
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

    # --- the gate refuses only errors the base roster does not already carry (P435)
    errlint = (
        "import {readFileSync} from 'node:fs';\n"
        "const t=readFileSync(process.argv[2],'utf8');\n"
        "const e=[...t.matchAll(/__bad_(\\w+)__/g)].map(m=>m[1]);\n"
        "for (const x of e) console.log(`  ERROR   [G-${x}] cite: a.py:${x} moved`);\n"
        "console.log(`TOTAL: ${e.length} error(s) across 1 file(s)`);\n")
    drv_e, lint_e = planted("gate-base", {new_rel: errlint})
    rpath = lint_e / "roster-under-lint.json"
    cur = "{}\n__bad_one__\n"
    def base_gate(text, base):
        rpath.write_text(text, encoding="utf-8")
        return lint_gate(drv_e, str(lint_e), rpath, base)
    ok, why = base_gate(cur + "other edit\n", cur)
    check("lint gate: an unrelated write passes beside a pre-existing error, warning it",
          ok and "WARN pre-existing" in why and "G-one" in why, why[:200])
    ok, why = base_gate(cur + "__bad_two__\n", cur)
    check("lint gate: the same write adding a bad citation is refused, naming it",
          not ok and "G-two" in why.splitlines()[0], why[:200])
    ok, why = base_gate("{}\nclean\n", "{}\nclean\n")
    check("lint gate: a clean roster writes as before (null control)",
          ok and why.startswith("TOTAL: 0"), why[:200])
    ok, why = base_gate(cur, None)
    check("lint gate: with no base text every error refuses (the old gate)",
          not ok and "G-one" in why, why[:200])
    ok, why = base_gate(cur, "{}\n")
    check("lint gate: an error the base lacks refuses (an empty base set would pass it)",
          not ok and "G-one" in why, why[:200])

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
    # The duration model this fixture tree carries: append-group validates a
    # size against it, so without it every size would be refused. Deliberately
    # NOT the live model's numbers -- this pins the mechanism ("a size is legal
    # iff the model keys it"), and roster_sync's self-test is the one that
    # measures the tree's real rosters against the real model.
    (seed / roster_lib.DURATIONS).parent.mkdir(parents=True, exist_ok=True)
    (seed / roster_lib.DURATIONS).write_text(
        json.dumps({"sizes_hours": {"S": 1.0, "M": 2.0, "L": 3.0}}, indent=1),
        encoding="utf-8")
    roster = {"repo": "fixture/roster", "groups": [
        {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
         "after": [], "brief": "fixture group A",
         "resume": {"stage": "not-started", "branch": "handoff/a"}},
        {"group": "R9-B", "lane": "L1", "issues": [], "fixes": [],
         "after": ["R9-A"], "brief": "fixture group B", "carry": [],
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

    # The issue states the done hold reads: #10 (R9-A's) closed unless a
    # check says otherwise, so every other arm's `done` lands as written.
    ISSUES = {}
    for word in ("open", "closed"):
        ISSUES[word] = Path(tmp, f"issues-{word}.json")
        ISSUES[word].write_text(json.dumps({"10": word}), encoding="utf-8")

    def edit(op, group, value, push=True, branch="edit-1", lint_cwd=None,
             at_sha=None, field=None, value_opt=None, match=None, wt="wt",
             rest=(), issues="closed", into=None, reason=None):
        args = [op, group, "--issue-state", str(ISSUES[issues])]
        if value is not None:
            args += [value]
        args += list(rest)
        if field:
            args += ["--field", field]
        if match is not None:
            args += ["--match", match]
        if value_opt is not None:
            args += ["--value", value_opt]
        if at_sha:
            args += ["--at-sha", at_sha]
        if into:
            args += ["--into", into]
        if reason is not None:
            args += ["--reason", reason]
        try:
            return main(args
                        + ["--checkout", str(drv), "--roster-ref", "main",
                           "--branch", branch, "--worktree",
                           str(Path(tmp, wt)),
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
        try:
            with contextlib.redirect_stderr(err):
                rc = sysrc(lambda: edit(*args, **kw))
        except Exception:  # a crash is no refusal: a FAIL line, not a traceback that ends the run (C6)
            return False
        return rc not in (0, None) and why in err.getvalue()

    def refusal(*args, **kw):
        """(rc, stderr) of one refused call: the message a seat reads."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = sysrc(lambda: edit(*args, **kw))
        return rc, err.getvalue()

    def branch_roster(name="edit-1"):
        sha = run(["git", "-C", str(origin), "rev-parse",
                   f"refs/heads/{name}"]).strip()
        return json.loads(run(["git", "-C", str(origin), "show",
                               f"{sha}:{FIXTURE_ROSTER}"]))

    # round-trips: each op lands in the dumped JSON, never a string splice.
    # R10-ORCH-ROSTER-SCHEMA: the round-trip runs on a stage the registry
    # classifies. It used to pin `in-review`, a word the writer accepted while
    # roster_sync's self-test refused to classify it -- the writer's own test
    # pinning the drift the class is about.
    check("set-stage rc", edit("set-stage", "R9-A", "in-progress") == 0)
    r = branch_roster()
    check("set-stage round-trip",
          r["groups"][0]["resume"]["stage"] == "in-progress")
    # THE VOCABULARY BARRIER. A stage the registry does not classify is refused
    # at the writer, naming the roster, the group and the offending value; a
    # classified stage still lands, or the refusal would be a blanket one that
    # no roster could satisfy.
    rc, said = refusal("set-stage", "R9-B", "reviewed")
    check("set-stage refuses an unclassified stage", rc == 2
          and "not a classified roster stage" in said and "R9-B" in said
          and "reviewed" in said and FIXTURE_ROSTER in said, (rc, said[-300:]))
    check("set-stage accepts a classified live-claim stage (null control)",
          edit("set-stage", "R9-B", "review") == 0
          and branch_roster()["groups"][1]["resume"]["stage"] == "review")
    check("set-stage accepts the design steps' stages (decision 0014)",
          edit("set-stage", "R9-B", "design") == 0
          and branch_roster()["groups"][1]["resume"]["stage"] == "design"
          and edit("set-stage", "R9-B", "design-review") == 0
          and branch_roster()["groups"][1]["resume"]["stage"] == "design-review")
    check("set-stage --at-sha",
          edit("set-stage", "R9-A", "done", at_sha="a" * 40) == 0
          and branch_roster()["groups"][0]["resume"]["commit"] == "a" * 40)
    # THE DONE HOLD (R10-RCA-ROSTER-SYNC-ORPHANS): a closed stage whose group
    # owns an open issue nothing else owns is written carries-open, HELD.
    def a_stage():
        return branch_roster()["groups"][0]["resume"]["stage"]
    edit("set-stage", "R9-A", "in-progress")
    rc, said = refusal("set-stage", "R9-A", "done", issues="open")
    check("set-stage done holds a group owning an open issue nothing else owns",
          rc == 0 and a_stage() == "carries-open" and "HELD R9-A" in said
          and "#10" in said, (rc, a_stage(), said[-200:]))
    edit("set-stage", "R9-A", "in-progress")
    rc, said = refusal("set-resume", "R9-A", "rca-done", field="stage", issues="open")
    check("... and so does set-resume --field stage, with any closed stage",
          rc == 0 and a_stage() == "carries-open" and "HELD R9-A" in said,
          (rc, a_stage(), said[-200:]))
    edit("set-stage", "R9-A", "in-progress")
    edit("wire-issue", "R9-B", "10")
    rc, said = refusal("set-stage", "R9-A", "done", issues="open")
    check("... a group whose open issue a live group also lists is done (null control)",
          rc == 0 and a_stage() == "done" and "HELD" not in said, (rc, a_stage()))
    edit("unwire-issue", "R9-B", "10")
    check("... and a closed issue holds nothing (null control)",
          edit("set-stage", "R9-A", "done", at_sha="a" * 40) == 0
          and a_stage() == "done")
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
    # A new group carries a stage and a size like any other entry, so
    # append-group validates both against the registry and the duration model.
    badstage = Path(tmp, "bad-stage.json")
    badstage.write_text(json.dumps({"group": "R9-G", "lane": "L2", "after": [],
                                    "brief": "fixture G",
                                    "resume": {"stage": "shipped"}}),
                        encoding="utf-8")
    rc, said = refusal("append-group", "R9-G", str(badstage))
    check("append-group refuses an unclassified stage", rc == 2
          and "not a classified roster stage" in said and "R9-G" in said
          and "shipped" in said, (rc, said[-300:]))
    badsize = Path(tmp, "bad-size.json")
    badsize.write_text(json.dumps({"group": "R9-H", "lane": "L2", "after": [],
                                   "brief": "fixture H", "size": "XS"}),
                       encoding="utf-8")
    rc, said = refusal("append-group", "R9-H", str(badsize))
    check("append-group refuses a size the duration model lacks", rc == 2
          and "not in the durations model" in said and "R9-H" in said
          and "XS" in said and FIXTURE_ROSTER in said, (rc, said[-300:]))
    goodsize = Path(tmp, "good-size.json")
    goodsize.write_text(json.dumps({"group": "R9-I", "lane": "L2", "after": [],
                                    "brief": "fixture I", "size": "S"}),
                        encoding="utf-8")
    check("append-group accepts a modelled size (null control)",
          edit("append-group", "R9-I", str(goodsize)) == 0
          and branch_roster()["groups"][-1].get("size") == "S")
    check("edit-brief rc",
          edit("edit-brief", "R9-B", "rewritten brief") == 0
          and branch_roster()["groups"][1]["brief"] == "rewritten brief")
    # append-carry refuses a closing destination (carry 3): reopen R9-A first.
    edit("set-stage", "R9-A", "in-progress")
    check("append-carry rc",
          edit("append-carry", "R9-A", "carry text one") == 0
          and branch_roster()["groups"][0]["carry"] == ["carry text one"])
    check("dup carry refused",
          edit("append-carry", "R9-A", "carry text one") == 2)
    check("append-carry refuses text ending in a mark-shaped suffix",
          edit("append-carry", "R9-A", "fresh text [implemented: abc123]") == 2
          and branch_roster()["groups"][0]["carry"] == ["carry text one"])
    check("unknown group refused", edit("set-stage", "R9-ZZ", "done") == 2)

    # The triage gate (decision 0015). The ruling batch lands on origin/main;
    # the edit branch does not carry it, so the reader's main fallback is
    # what finds it. Null control: the same op with an ACCEPT ruling passes.
    ruling = "dev/programme/triage/s9-batch1.md"
    (seed / ruling).parent.mkdir(parents=True, exist_ok=True)
    (seed / ruling).write_text(
        "# s9 batch 1\n\n## P1: fold the orphan discharge arm\n"
        "Verdict: ACCEPT -> R9-B (carry)\nSource: sweep\n\n"
        "## P2: a second watcher\nVerdict: REJECT\nBinding: standing CPU\n\n"
        "## P3: no verdict line\nSource: sweep\n\n"
        "## P4: a later watcher\nVerdict: DEFER\nSource: sweep\n\n"
        "## P-C: a lettered proposal\nVerdict: ACCEPT -> R9-B (carry)\n\n"
        "## P-D: a lettered reject\nVerdict: REJECT\n", encoding="utf-8")
    run(["git", "-C", str(seed), "add", "-A"])
    run(["git", "-C", str(seed), "commit", "-q", "-m", "fixture triage ruling"])
    run(["git", "-C", str(seed), "push", "-q", str(origin), "main:refs/heads/main"])
    bare = "Triage P1 (s9): fold the orphan discharge arm."
    cited = bare + f" triage: {ruling}#P1"
    check("triage gate: a proposal-sourced carry citing no ruling is refused",
          refuses("cites no triage ruling", "append-carry", "R9-B", bare)
          and bare not in branch_roster()["groups"][1]["carry"])
    check("triage gate null control: the same carry citing its ACCEPT ruling lands",
          edit("append-carry", "R9-B", cited) == 0
          and cited in branch_roster()["groups"][1]["carry"])
    check("triage gate: a REJECT ruling is refused",
          refuses("REJECT", "append-carry", "R9-B", f"proposal P2: a watcher. triage: {ruling}#P2"))
    check("triage gate: a DEFER ruling is refused: only an ACCEPT is routed",
          refuses("DEFER", "append-carry", "R9-B", f"proposal P4: a watcher. triage: {ruling}#P4"))
    check("triage gate: an entry with no verdict line is refused",
          refuses("unreadable", "append-carry", "R9-B", f"proposal P3. triage: {ruling}#P3"))
    check("triage gate: a cited entry the batch lacks is refused",
          refuses("no such entry", "append-carry", "R9-B", f"proposal P7. triage: {ruling}#P7"))
    check("triage gate: a citation to a missing batch is refused, proposal named or not",
          refuses("not on the roster branch", "append-carry", "R9-B",
                  "plain text. triage: dev/programme/triage/nope.md#P1"))
    # Carry 0 (#2670): session s4 labelled later proposals with letters
    # (`P-A`..`P-Q`); the numbered-only grammar never fired on them.
    lettered = "Triage P-C (s4): fold a lettered proposal."
    check("triage gate: a lettered label citing no ruling is refused",
          refuses("cites no triage ruling", "append-carry", "R9-B", lettered)
          and lettered not in branch_roster()["groups"][1]["carry"])
    check("triage gate: a lettered label citing its ACCEPT ruling lands",
          edit("append-carry", "R9-B", lettered + f" triage: {ruling}#P-C") == 0
          and lettered + f" triage: {ruling}#P-C" in branch_roster()["groups"][1]["carry"])
    check("triage gate: a lettered label citing a REJECT ruling is refused",
          refuses("REJECT", "append-carry", "R9-B",
                  f"proposal P-D: a thing. triage: {ruling}#P-D"))
    check("triage gate: a lettered label citing no such entry is refused",
          refuses("no such entry", "append-carry", "R9-B",
                  f"proposal P-E: a thing. triage: {ruling}#P-E"))
    check("triage gate null control: a hyphenated word that is no label lands",
          edit("append-carry", "R9-B", "the P-value of a triage Pareto plot") == 0)
    check("triage gate: a new group's brief is judged",
          refuses("cites no triage ruling", "edit-brief", "R9-A", "brief from proposal P4"))
    check("triage gate: text naming no proposal passes untouched",
          edit("append-carry", "R9-B", "a forward-carried finding, no proposal") == 0)
    check("added_texts: only what the write adds is judged",
          added_texts({"groups": [{"group": "A", "brief": "b", "carry": ["old"]}]},
                      {"groups": [{"group": "A", "brief": "b", "carry": ["old", "new"]},
                                  {"group": "N", "brief": "nb", "carry": ["nc"]}]})
          == ["new", "nb", "nc"])
    # Leave R9-B's carry as the drop-carry arms below expect it: empty.
    check("triage gate fixture restored",
          edit("drop-carry", "R9-B", None, match="orphan discharge") == 0
          and edit("drop-carry", "R9-B", None, match="no proposal") == 0
          and edit("drop-carry", "R9-B", None, match="lettered proposal") == 0
          and edit("drop-carry", "R9-B", None, match="P-value") == 0
          and branch_roster()["groups"][1].get("carry") == [])  # .get: a dropped key is a FAIL line, never a KeyError crash (C6)

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
    # set-resume --field stage is the second way a stage word reaches the file.
    rc, said = refusal("set-resume", "R9-B", "shipped", field="stage")
    check("set-resume --field stage refuses an unclassified stage", rc == 2
          and "not a classified roster stage" in said and "R9-B" in said
          and "shipped" in said, (rc, said[-300:]))
    check("set-resume --field stage accepts a classified stage (null control)",
          edit("set-resume", "R9-B", "fixing", field="stage") == 0
          and branch_roster()["groups"][1]["resume"]["stage"] == "fixing")

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

    # set-source: the roster field replan.py's top tier reads
    # (roster_lib.is_outside). Written, read back, cleared; an unknown word
    # and an unknown group refused with nothing moved; a held value no-op.
    def source_of(group):
        return next(g for g in branch_roster()["groups"]
                    if g["group"] == group).get("source", "absent")

    check("set-source writes outside, read back from the pushed roster",
          edit("set-source", "R9-B", "outside") == 0 and source_of("R9-B") == "outside"
          and roster_lib.is_outside(next(g for g in branch_roster()["groups"]
                                         if g["group"] == "R9-B")))
    t0 = tip()
    check("no-op set-source commits nothing",
          edit("set-source", "R9-B", "outside") == 0 and tip() == t0)
    check("set-source refuses a word outside roster_lib.SOURCES, moving nothing",
          refuses("is not a source", "set-source", "R9-B", "audit") and tip() == t0)
    check("set-source refuses an unknown group",
          refuses("no roster group", "set-source", "R9-ZZ", "outside"))
    check("set-source - removes the key, and the old value is in resume.note",
          edit("set-source", "R9-B", "-") == 0 and source_of("R9-B") == "absent"
          and "set-source outside -> unset" in (
              next(g for g in branch_roster()["groups"]
                   if g["group"] == "R9-B")["resume"].get("note") or ""))

    # set-size / set-files (R10-ROSTER-OPS-2 part 1): one op pair for the
    # carries that asked for set-size (with and without a cite), set-files
    # --add, --set-hot and a whole-field replace. Every refusal leaves the
    # remote branch where it was; every null control is byte-identical.
    sf_main = run(["git", "-C", str(drv), "rev-parse", "origin/main"]).strip()
    run(["git", "-C", str(drv), "checkout", "-q", "-b", "cited", "origin/main"])
    (drv / "NEW.md").write_text("added by the cited ref\n", encoding="utf-8")
    (drv / "__bad__.md").write_text("lint plant\n", encoding="utf-8")
    run(["git", "-C", str(drv), "add", "-A"])
    run(["git", "-C", str(drv), "commit", "-q", "-m", "cited ref adds files"])
    sf_cited = run(["git", "-C", str(drv), "rev-parse", "HEAD"]).strip()
    run(["git", "-C", str(drv), "push", "-q", "origin", "cited"])
    run(["git", "-C", str(drv), "checkout", "-q", "--detach", "origin/main"])

    def more(op, group, *extra, value=None, wt="wt"):
        args = [op, group] + ([value] if value is not None else []) + list(extra)
        try:
            return main(args + ["--checkout", str(drv), "--roster-ref", "main",
                                "--branch", "edit-1", "--worktree",
                                str(Path(tmp, wt)), "--lint-cwd", str(seed),
                                "--issue-state", str(ISSUES["closed"]),
                                "--push"])
        except SystemExit as e:
            return e.code

    def more_refusal(*args, **kw):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = sysrc(lambda: more(*args, **kw))
        return rc, err.getvalue()

    def grp(group):
        return next(g for g in branch_roster()["groups"] if g["group"] == group)

    def sans(g, *keys):
        """A group minus some top-level keys and resume.note: what an op that
        owns those must leave of everything else."""
        out = json.loads(json.dumps(g))
        for k in keys:
            out.pop(k, None)
        out.get("resume", {}).pop("note", None)
        return out

    t_sf = tip()
    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{sf_main}",
                            value="XL")
    check("set-size refuses a size the durations model lacks, naming it",
          rc == 2 and "not in the durations model" in said and "'XL'" in said
          and tip() == t_sf, (rc, said[-200:]))
    check("set-size refuses an empty size",
          more_refusal("set-size", "R9-A", value="")[0] == 2 and tip() == t_sf)
    check("set-size refuses an unknown group",
          more_refusal("set-size", "R9-ZZ", value="L")[0] == 2
          and "no roster group" in more_refusal("set-size", "R9-ZZ", value="L")[1])
    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{'f' * 40}",
                            value="L")
    check("set-size refuses a cite whose ref lacks the sha",
          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{sf_cited}",
                            value="L")
    check("set-size refuses a cite whose sha exists but main does not hold it",
          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-size", "R9-A", "--cite", "no-such-ref@" + sf_main,
                            value="L")
    check("set-size refuses a cite whose ref does not exist",
          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-size", "R9-A", "--cite", "mainish", value="L")
    check("set-size refuses a cite that is not <ref>@<sha>",
          rc == 2 and "<ref>@<sha>" in said and tip() == t_sf, (rc, said[-200:]))
    before_a = grp("R9-A")
    check("set-size with a valid cite lands",
          more("set-size", "R9-A", "--cite", f"main@{sf_main}", value="L") == 0
          and grp("R9-A").get("size") == "L")
    note = (grp("R9-A").get("resume") or {}).get("note") or ""
    check("... recording the old size and the cite in resume.note",
          "set-size" in note and "unset" in note and "L" in note
          and f"main@{sf_main}" in note, note)
    check("... and touching no other field",
          sans(grp("R9-A"), "size") == sans(before_a, "size"))
    t_sf = tip()
    check("set-size to the current size is byte-identical (null control)",
          more("set-size", "R9-A", "--cite", f"main@{sf_main}", value="L") == 0
          and tip() == t_sf)
    check("set-size without a cite lands (the cite is optional)",
          more("set-size", "R9-B", value="M") == 0
          and grp("R9-B").get("size") == "M")
    check("set-size from a recorded size names the old one",
          more("set-size", "R9-B", value="S") == 0
          and "M -> S" in grp("R9-B")["resume"]["note"])

    # set-price: the owner-stated price the planner reads (group_hours).
    words = 'owner-stated price, test 2026-11-12: "Price it at 4h"'
    t_sf = tip()
    rc, said = more_refusal("set-price", "R9-A", "240")
    check("set-price refuses a price with no citation, moving nothing",
          rc == 2 and "citation" in said and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-price", "R9-A", "240", "--price-cite", "  ")
    check("set-price refuses a blank citation",
          rc == 2 and "citation" in said and tip() == t_sf, (rc, said[-200:]))
    for bad in ("0", "-30", "abc", "inf"):
        rc, said = more_refusal("set-price", "R9-A", bad, "--price-cite", words)
        check(f"set-price refuses minutes {bad!r}, moving nothing",
              rc == 2 and "minutes" in said and tip() == t_sf, (rc, said[-200:]))
    check("set-price refuses an unknown group",
          more_refusal("set-price", "R9-ZZ", "240", "--price-cite", words)[0] == 2
          and "no roster group" in more_refusal(
              "set-price", "R9-ZZ", "240", "--price-cite", words)[1])
    before_p = grp("R9-A")
    check("set-price with a citation lands both fields",
          more("set-price", "R9-A", "--price-cite", words, value="240") == 0
          and grp("R9-A").get("owner_price_minutes") == 240
          and grp("R9-A").get("owner_price_cite") == words)
    check("... recording it in resume.note and touching no other field",
          "set-price unset -> 240 min" in grp("R9-A")["resume"]["note"]
          and sans(grp("R9-A"), "owner_price_minutes", "owner_price_cite")
          == sans(before_p, "owner_price_minutes", "owner_price_cite"))
    check("what it wrote is a price the planner's reader accepts",
          roster_lib.owner_price(grp("R9-A")) == (240.0, words))
    t_sf = tip()
    check("set-price to the price already held is byte-identical (null control)",
          more("set-price", "R9-A", "--price-cite", words, value="240") == 0
          and tip() == t_sf)
    check("an unpriced group carries neither field (null control)",
          "owner_price_minutes" not in grp("R9-B")
          and roster_lib.owner_price(grp("R9-B")) is None)
    check("set-price stores the citation stripped, and the stored text re-reads equal",
          more("set-price", "R9-B", "--price-cite", f"  {words}\n", value="90") == 0
          and grp("R9-B").get("owner_price_cite") == words
          and roster_lib.owner_price(grp("R9-B")) == (90.0, words))

    t_sf = tip()
    rc, said = more_refusal("set-files", "R9-A", "--add", "no/such/path.py")
    check("set-files --add refuses a path not in the tree at origin/main",
          rc == 2 and "not in the tree" in said and "no/such/path.py" in said
          and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-files", "R9-A", "--add", "NEW.md")
    check("... even one a branch outside origin/main adds, when uncited",
          rc == 2 and "not in the tree" in said and tip() == t_sf)
    check("set-files unknown group refused",
          more_refusal("set-files", "R9-ZZ", "--add", "README.md")[0] == 2
          and "no roster group" in more_refusal("set-files", "R9-ZZ",
                                                "--add", "README.md")[1])
    rc, said = more_refusal("set-files", "R9-A")
    check("set-files with nothing to write refused",
          rc == 2 and "needs --add" in said and tip() == t_sf, (rc, said[-200:]))
    rc, said = more_refusal("set-files", "R9-A", "--add", "README.md",
                            "--cite", f"main@{'f' * 40}")
    check("set-files refuses a cite whose ref lacks the sha",
          rc == 2 and "does not hold" in said and tip() == t_sf)
    rc, said = more_refusal("set-files", "R9-A", "--add", "README.md",
                            "--cite", f"main@{sf_cited}")
    check("set-files refuses a cite whose sha exists but main does not hold it",
          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
    before_a = grp("R9-A")
    check("set-files --add lands a path in the tree",
          more("set-files", "R9-A", "--add", "README.md") == 0
          and grp("R9-A").get("files") == ["README.md"])
    check("... and touches no other field",
          sans(grp("R9-A"), "files") == sans(before_a, "files"))
    t_sf = tip()
    check("set-files --add of a path already held is byte-identical (null control)",
          more("set-files", "R9-A", "--add", "README.md") == 0 and tip() == t_sf)
    check("set-files --add accepts a path the cited ref adds",
          more("set-files", "R9-A", "--add", "NEW.md",
               "--cite", f"cited@{sf_cited}") == 0
          and grp("R9-A").get("files") == ["README.md", "NEW.md"]
          and f"cited@{sf_cited}" in grp("R9-A")["resume"]["note"])
    t_sf = tip()
    rc, said = more_refusal("set-files", "R9-B", "--add", "__bad__.md",
                            "--cite", f"cited@{sf_cited}", wt="wt-sflint")
    check("set-files lints like every other op (the planted text is refused rc 3)",
          rc == 3 and tip() == t_sf, (rc, said[-200:]))

    rc, said = more_refusal("set-files", "R9-A", "--set-hot", "nowhere.py")
    check("set-files --set-hot refuses a path that is neither a files basename "
          "nor a known token",
          rc == 2 and "nowhere.py" in said and "hot" in said and tip() == t_sf,
          (rc, said[-200:]))
    before_a = grp("R9-A")
    check("set-files --set-hot lands a files basename",
          more("set-files", "R9-A", "--set-hot", "NEW.md,README.md",
               "--cite", f"cited@{sf_cited}") == 0
          and grp("R9-A").get("hot_files") == ["NEW.md", "README.md"])
    check("... recording the old value in resume.note, other fields untouched",
          "hot_files" in grp("R9-A")["resume"]["note"]
          and sans(grp("R9-A"), "hot_files") == sans(before_a, "hot_files"))
    t_sf = tip()
    check("set-files --set-hot with the current value is byte-identical (null control)",
          more("set-files", "R9-A", "--set-hot", "NEW.md,README.md") == 0
          and tip() == t_sf)
    check("set-files --set-hot accepts a token another group already holds",
          more("set-files", "R9-B", "--set-hot", "README.md") == 0
          and grp("R9-B").get("hot_files") == ["README.md"])
    check("set-files --set-hot - clears the field, keeping the key",
          more("set-files", "R9-A", "--set-hot", "-") == 0
          and grp("R9-A").get("hot_files") == []
          and "[]" in grp("R9-A")["resume"]["note"])
    t_sf = tip()
    check("set-files --set-hot - on an already-empty field is byte-identical (null control)",
          more("set-files", "R9-A", "--set-hot", "-") == 0 and tip() == t_sf)
    before_a = grp("R9-A")
    check("set-files --set-files replaces files whole, `-` for none",
          more("set-files", "R9-A", "--set-files", "-") == 0
          and grp("R9-A").get("files") == []
          and sans(grp("R9-A"), "files") == sans(before_a, "files"))
    check("... and takes a comma list, refusing a path not in the tree",
          more("set-files", "R9-A", "--set-files", "README.md") == 0
          and grp("R9-A").get("files") == ["README.md"]
          and more_refusal("set-files", "R9-A", "--set-files",
                           "README.md,no/such.py")[0] == 2)
    check("set-files names no op flag on another op",
          more_refusal("set-after", "R9-B", "--add", "README.md",
                       value="R9-A")[0] == 2)

    # drop-carry: the inverse of append-carry, by index or by a unique match.
    # R9-B carries `"carry": []`, the live roster's empty shape (27 of 91
    # groups; none omits the key), so the round-trip below is pinned on the
    # shape the roster actually has. Dropping the last entry leaves the list
    # empty, keeping the key: append-then-drop restores the bytes exactly.
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
    check("drop-carry of the last entry leaves the key empty",
          edit("drop-carry", "R9-B", None, match="alpha one") == 0
          and carry_of("R9-B") == [])
    check("append-carry then drop-carry is byte-identical",
          bytes_at() == before_carry)
    # CARRY-EXACT-MATCH: a bare carry whose text sits inside a sibling.
    for text in ("From #7, body item X: item X", "item X",
                 "zeta one", "zeta two"):
        edit("append-carry", "R9-B", text)
    check("drop-carry --match equal to a carry inside a sibling is that carry",
          edit("drop-carry", "R9-B", None, match="item X") == 0
          and carry_of("R9-B") == ["From #7, body item X: item X",
                                   "zeta one", "zeta two"])
    check("drop-carry --match equal to no carry and hitting two still refuses",
          refuses("ambiguous", "drop-carry", "R9-B", None, match="zeta"))
    check("drop-carry --match unique substring still resolves",
          edit("drop-carry", "R9-B", None, match="body item") == 0
          and carry_of("R9-B") == ["zeta one", "zeta two"])

    # THE CARRY LEDGER (#2733, carries 10 and 31). mark-carry discharges one
    # carry with a mark; set-stage done over a pending carry writes
    # carries-open through roster_lib.closing_stage, the predicate roster_sync
    # shares. On a branch of its own, so the byte pins above are untouched.
    def said(call):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sysrc(call)
        return rc, out.getvalue() + err.getvalue()

    def mark(*rest, match=None):
        return said(lambda: edit("mark-carry", "R9-B",
                                 None if match is not None else rest[0],
                                 branch="mark-1", match=match,
                                 rest=rest if match is not None else rest[1:]))

    def at_mark(group):
        return next(g for g in branch_roster("mark-1")["groups"]
                    if g["group"] == group)

    for text in ("carry one", "carry two", "carry three"):
        edit("append-carry", "R9-B", text, branch="mark-1")
    rc, out = mark("0", "implemented", "0123abcd")
    check("mark-carry by index appends the implemented mark",
          rc == 0 and at_mark("R9-B")["carry"][0]
          == "carry one [implemented: 0123abcd]", (rc, out[-300:]))
    rc, out = mark("moved", "R9-A", match="carry two")
    check("mark-carry by --match appends the moved mark",
          rc == 0 and at_mark("R9-B")["carry"][1] == "carry two [moved: R9-A]",
          (rc, out[-300:]))
    t0 = tip("mark-1")
    for name, args, why in (
            ("a carry already marked", ("0", "dismissed", "again"), "already marked"),
            ("an unknown mark", ("2", "shipped", "0123abcd"), "mark is one of"),
            ("implemented without a sha", ("2", "implemented", "main"), "needs a sha"),
            ("moved to no group", ("2", "moved", "R9-ZZ"), "names no group"),
            ("moved to itself", ("2", "moved", "R9-B"), "to itself"),
            ("dismissed with no reason", ("2", "dismissed"), "needs a reason")):
        rc, out = mark(*args)
        check(f"mark-carry refuses {name}", rc not in (0, None) and why in out,
              (rc, out[-300:]))
    check("refused mark-carry moved nothing", tip("mark-1") == t0)
    rc, out = said(lambda: edit("set-stage", "R9-B", "done", branch="mark-1"))
    check("set-stage done over a pending carry writes carries-open and says so",
          rc == 0 and at_mark("R9-B")["resume"]["stage"] == "carries-open"
          and "set-stage R9-B: done -> carries-open (1 pending carries)" in out,
          (rc, at_mark("R9-B")["resume"], out[-300:]))
    mark("2", "dismissed", "a duplicate of carry two")
    rc, out = said(lambda: edit("set-stage", "R9-B", "done", branch="mark-1"))
    check("set-stage done with every carry marked writes done (null control)",
          rc == 0 and at_mark("R9-B")["resume"]["stage"] == "done",
          (rc, at_mark("R9-B")["resume"], out[-300:]))
    # A carry moves only to an open group, and a mark's value never holds the
    # `]` that would end carry_mark's grammar early (review X7, X8). R9-A is
    # put in each closed stage in turn; each refusal leaves the branch where it
    # was, and the null controls -- an open destination, a plain value -- land.
    edit("set-stage", "R9-B", "in-progress", branch="mark-1")
    edit("append-carry", "R9-B", "carry four", branch="mark-1")
    edit("append-carry", "R9-B", "carry five", branch="mark-1")
    for closed in roster_lib.CARRY_DEST_CLOSED:  # the sink barrier: carries-open and refuted too
        edit("set-stage", "R9-A", closed, branch="mark-1",
             into="R9-B" if closed == "absorbed" else None)
        t1 = tip("mark-1")
        rc, out = mark("3", "moved", "R9-A")
        check(f"mark-carry refuses moved to a {closed} group",
              rc not in (0, None) and f"moved R9-A is {closed}" in out
              and tip("mark-1") == t1, (rc, out[-300:]))
    t1 = tip("mark-1")
    rc, out = mark("3", "dismissed", "a]b")
    check("mark-carry refuses a value holding ']'",
          rc not in (0, None) and "holds no ']'" in out
          and tip("mark-1") == t1, (rc, out[-300:]))
    edit("set-stage", "R9-A", "in-progress", branch="mark-1")
    rc, out = mark("3", "moved", "R9-A")
    check("mark-carry moved to an open group lands (null control)",
          rc == 0 and at_mark("R9-B")["carry"][3] == "carry four [moved: R9-A]",
          (rc, out[-300:]))
    rc, out = mark("4", "dismissed", "ab")
    check("mark-carry with a plain value lands (null control)",
          rc == 0 and at_mark("R9-B")["carry"][4] == "carry five [dismissed: ab]",
          (rc, out[-300:]))
    # THE CLOSING ARM (tvofi 2026-11-07, proposal 1): a mark that discharges
    # the last pending carry of a carries-open group writes what set-stage done
    # writes -- done, or carries-open HELD while it owns an orphaned open issue.
    check("mark-carry's last mark on an in-progress group leaves its stage (null control)",
          at_mark("R9-B")["resume"]["stage"] == "in-progress"
          and "last pending carry" not in out, (at_mark("R9-B")["resume"], out[-300:]))

    def mark_a(text, issues="closed"):
        return said(lambda: edit("mark-carry", "R9-A", None, branch="mark-1", match=text,
                                 rest=("dismissed", "a fixture"), issues=issues))
    for text in ("a one", "a two"):
        edit("append-carry", "R9-A", text, branch="mark-1")
    edit("set-stage", "R9-A", "done", branch="mark-1", at_sha="a" * 40)
    rc, out = mark_a("a one")
    check("mark-carry leaving one pending carry keeps carries-open (null control)",
          rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
          and "last pending carry" not in out, (rc, at_mark("R9-A")["resume"], out[-300:]))
    rc, out = mark_a("a two")
    check("mark-carry discharging the last pending carry of a carries-open group writes done",
          rc == 0 and at_mark("R9-A")["resume"]["stage"] == "done"
          and "carries-open -> done" in out, (rc, at_mark("R9-A")["resume"], out[-300:]))
    edit("set-stage", "R9-A", "in-progress", branch="mark-1")
    edit("append-carry", "R9-A", "a three", branch="mark-1")
    edit("set-stage", "R9-A", "done", branch="mark-1")
    rc, out = mark_a("a three", issues="open")
    check("... and holds it carries-open, naming the issue, while it owns an orphaned open issue",
          rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
          and "HELD R9-A" in out and "#10" in out, (rc, at_mark("R9-A")["resume"], out[-300:]))
    edit("set-stage", "R9-A", "in-progress", branch="mark-1")
    # The cut-over: a carry on a closed group at the cut-over commit is legacy
    # and never pending; one appended after it is.
    # A closed group that holds a carry can only be admitted whole (append-group
    # with a done stage), since append-carry now refuses a closed destination.
    legacyg = Path(tmp, "legacy-group.json")
    legacyg.write_text(json.dumps({
        "group": "R9-L", "lane": "L2", "after": [], "brief": "fixture L",
        "carry": ["legacy carry"], "resume": {"stage": "done", "branch": "handoff/l"}}),
        encoding="utf-8")
    edit("append-group", "R9-L", str(legacyg), branch="mark-1")
    saved = dict(roster_lib.CARRY_CUTOVER)
    roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = tip("mark-1")
    try:
        rc, out = said(lambda: edit("set-stage", "R9-L", "done", branch="mark-1"))
        check("a legacy carry alone leaves set-stage done as done (null control)",
              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "done",
              (rc, out[-300:]))
        edit("set-stage", "R9-L", "in-progress", branch="mark-1")  # a carries-open group takes no carry
        edit("append-carry", "R9-L", "post-cut-over carry", branch="mark-1")
        rc, out = said(lambda: edit("set-stage", "R9-L", "done", branch="mark-1"))
        check("a carry after the cut-over is pending beside a legacy one",
              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "carries-open"
              and "(1 pending carries)" in out, (rc, out[-300:]))
        rc, out = said(lambda: edit("set-resume", "R9-L", "done", field="stage",
                                    branch="mark-1"))
        check("set-resume --field stage done reads the same rule",
              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "carries-open"
              and "set-resume R9-L: done -> carries-open" in out, (rc, out[-300:]))
        # mark-carry reads the cut-over too (review 3350): marking the one
        # post-cut-over carry leaves only the legacy one, which is not
        # pending, so the group closes. The null control is the check above:
        # the same group with that carry unmarked stays carries-open.
        rc, out = said(lambda: edit("mark-carry", "R9-L", None, branch="mark-1",
                                    match="post-cut-over carry",
                                    rest=("dismissed", "a fixture")))
        check("mark-carry whose only unmarked carry left is legacy writes done",
              rc == 0 and at_mark("R9-L")["resume"]["stage"] == "done"
              and "carries-open -> done" in out, (rc, at_mark("R9-L")["resume"], out[-300:]))
        # An unreadable cut-over refuses the stage write and writes nothing
        # (review X6): read as "no legacy", the legacy carry would be pending.
        # The readable null is the "legacy carry alone" check above.
        roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = "f" * 40
        t1 = tip("mark-1")
        for op, kw in (("set-stage", {}), ("set-resume", {"field": "stage"})):
            rc, out = said(lambda: edit(op, "R9-L", "done", branch="mark-1",
                                        **kw))
            check(f"{op} refuses an unreadable cut-over and writes nothing",
                  rc == 2 and "the carry cut-over is unreadable" in out
                  and tip("mark-1") == t1, (rc, out[-300:]))
    finally:
        roster_lib.CARRY_CUTOVER.clear()
        roster_lib.CARRY_CUTOVER.update(saved)

    # R10-ROSTER-WRITE-SWEEP: carries 2, 3, 4, 5, 6, 7 and 16, each with the
    # null control that keeps the refusal from being a blanket one.
    W = "wsw-1"

    def wedit(*a, **k):
        return edit(*a, branch=W, **k)

    def at_w(g):
        return next(x for x in branch_roster(W)["groups"] if x["group"] == g)

    def said_w(*a, **k):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sysrc(lambda: wedit(*a, **k))
        return rc, out.getvalue() + err.getvalue()

    def jgroup(name, **kw):
        f = Path(tmp, f"{name}.json")
        f.write_text(json.dumps({"group": name, "lane": "L2", "after": [],
                                 "brief": f"fixture {name}", **kw}),
                     encoding="utf-8")
        return str(f)

    # carry 6: append-group reads @file like append-carry and edit-brief.
    f1 = jgroup("R9-W1", files=["tools/x.py", "tools/audit/seat/INSTRUMENTS.md"])
    check("append-group @file lands (carry 6)",
          wedit("append-group", "R9-W1", "@" + f1) == 0
          and at_w("R9-W1")["lane"] == "L2")
    check("append-group bare path still lands (null control)",
          wedit("append-group", "R9-W2", jgroup("R9-W2")) == 0
          and at_w("R9-W2")["lane"] == "L2")
    check("append-group @missing is still refused",
          refuses("unreadable JSON", "append-group", "R9-W0",
                  "@" + str(Path(tmp, "no-such.json")), branch=W))
    # carry 5: existing-groups-first at admission.
    f3 = jgroup("R9-W3", files=["tools/x.py"])
    rc, out = said_w("append-group", "R9-W3", f3)
    check("append-group overlapping a not-started group refuses, naming both (carry 5)",
          rc == 2 and "R9-W1" in out and "tools/x.py" in out
          and "--reason" in out, (rc, out[-300:]))
    check("append-group --reason admits the overlap and records it",
          wedit("append-group", "R9-W3", f3, reason="needs the same seam") == 0
          and "needs the same seam" in at_w("R9-W3")["resume"]["note"]
          and "R9-W1" in at_w("R9-W3")["resume"]["note"])
    check("an empty --reason does not admit the overlap",
          wedit("append-group", "R9-W3b",
                jgroup("R9-W3b", files=["tools/x.py"]), reason=" ") == 2)
    check("overlap on the index file alone passes (null control)",
          wedit("append-group", "R9-W4",
                jgroup("R9-W4", files=["tools/audit/seat/INSTRUMENTS.md",
                                       "tools/audit/seat/instruments/a.md"])) == 0)
    wedit("append-group", "R9-W5", jgroup(
        "R9-W5", files=["tools/y.py"], resume={"stage": "in-progress", "branch": "handoff/w5"}))
    wedit("append-group", "R9-W6", jgroup(
        "R9-W6", files=["tools/z.py"], resume={"stage": "done", "branch": "handoff/w6"}))
    check("overlap with an in-progress group passes (null control)",
          wedit("append-group", "R9-W7", jgroup("R9-W7", files=["tools/y.py"])) == 0)
    check("overlap with a done group passes (null control)",
          wedit("append-group", "R9-W8", jgroup("R9-W8", files=["tools/z.py"])) == 0)
    # carry 3: a carry to a closing group is refused at write time.
    wedit("append-group", "R9-WD", jgroup(
        "R9-WD", resume={"stage": "done", "branch": "handoff/wd"}))
    wedit("append-group", "R9-WA", jgroup(
        "R9-WA", resume={"stage": "absorbed", "branch": "handoff/wa",
                         "absorbed_into": "R9-A"}))
    wedit("append-group", "R9-WN", jgroup(
        "R9-WN", resume={"stage": "absorbed", "branch": "handoff/wn"}))
    wedit("append-group", "R9-WP", jgroup(
        "R9-WP", resume={"stage": "in-progress", "branch": "handoff/wp", "pr": 123}))
    t_w = branch_roster(W)
    rc, out = said_w("append-carry", "R9-WD", "late carry")
    check("append-carry to a done group refuses and writes nothing (carry 3)",
          rc == 2 and "R9-WD is done" in out
          and branch_roster(W) == t_w, (rc, out[-300:]))
    rc, out = said_w("append-carry", "R9-WA", "late carry")
    check("append-carry to an absorbed group names absorbed_into",
          rc == 2 and "absorbed into R9-A" in out, (rc, out[-300:]))
    rc, out = said_w("append-carry", "R9-WN", "late carry")
    check("append-carry to an absorbed group with no host still refuses",
          rc == 2 and "R9-WN is absorbed" in out, (rc, out[-300:]))
    # THE SINK BARRIER (R10-CARRY-SINK-BARRIER, tvofi 2026-11-10): a group whose PR
    # merged (carries-open), a refuted one and a receiver-only one (no PR, brief,
    # issue or fix) take no carry; the refusal names the rule.
    wedit("append-group", "R9-WC", jgroup(
        "R9-WC", resume={"stage": "carries-open", "branch": "handoff/wc", "pr": 77}))
    wedit("append-group", "R9-WR", jgroup(
        "R9-WR", resume={"stage": "refuted", "branch": "handoff/wr"}))
    wedit("append-group", "R9-WS", jgroup(
        "R9-WS", files=[], resume={"stage": "not-started", "branch": "handoff/ws"}))
    for gid, said_as in (("R9-WC", "R9-WC is carries-open"), ("R9-WR", "R9-WR is refuted"),
                         ("R9-WS", "R9-WS is not-started, a receiver only")):
        t_w = branch_roster(W)
        rc, out = said_w("append-carry", gid, "parked carry")
        check(f"sink barrier: append-carry to {gid} refuses naming the rule and writes nothing",
              rc == 2 and said_as in out and "live group owning the seam" in out
              and branch_roster(W) == t_w, (rc, out[-300:]))
    rc, out = said_w("append-carry", "R9-WP", "pr carry")
    check("append-carry to a group with resume.pr appends and WARNs",
          rc == 0 and "WARN carry to R9-WP: PR #123 is open on it" in out
          and at_w("R9-WP")["carry"] == ["pr carry"], (rc, out[-300:]))
    rc, out = said_w("append-carry", "R9-A", "open carry")
    check("append-carry to an open group with no PR appends without a WARN",
          rc == 0 and "WARN" not in out
          and at_w("R9-A")["carry"] == ["open carry"], (rc, out[-300:]))
    # carry 4: resume.pr round-trips through set-resume.
    check("set-resume --field pr round-trips an integer (carry 4)",
          wedit("set-resume", "R9-A", "2836", field="pr") == 0
          and at_w("R9-A")["resume"]["pr"] == 2836)
    check("set-resume --field pr refuses a non-number",
          refuses("pull request number", "set-resume", "R9-A", "#x",
                  field="pr", branch=W))
    # carry 2: closing a group clears a note naming owed work.
    wedit("append-group", "R9-WO", jgroup(
        "R9-WO", resume={"stage": "in-progress", "branch": "handoff/wo",
                         "note": "has no pull request. Owed: recarry and open"}))
    wedit("append-group", "R9-WK", jgroup(
        "R9-WK", resume={"stage": "in-progress", "branch": "handoff/wk",
                         "note": "size was M (cite)"}))
    rc, out = said_w("set-stage", "R9-WO", "done")
    check("set-stage done clears a note naming owed work and says so (carry 2)",
          rc == 0 and at_w("R9-WO")["resume"]["note"] is None
          and "cleared the stale resume.note" in out, (rc, out[-300:]))
    check("set-stage done keeps a note that owes nothing (null control)",
          wedit("set-stage", "R9-WK", "done") == 0
          and at_w("R9-WK")["resume"]["note"] == "size was M (cite)")
    check("set-stage to an open stage keeps an owed note (null control)",
          wedit("set-stage", "R9-WO", "in-progress") == 0
          and wedit("set-resume", "R9-WO", "Owed: x", field="note") == 0
          and wedit("set-stage", "R9-WO", "review") == 0
          and at_w("R9-WO")["resume"]["note"] == "Owed: x")
    # carry 7: a host path in an added text is refused at the op.
    hostpath = "evidence in /" + "Users/someone/sweep/run.log"  # built, not spelled
    for op, args, kw in (
            ("append-carry", ("R9-A", hostpath), {}),
            ("edit-brief", ("R9-A", hostpath), {}),
            ("set-resume", ("R9-A", hostpath), {"field": "note"}),
            ("append-group", ("R9-WH", jgroup("R9-WH", brief=hostpath)), {})):
        rc, out = said_w(op, *args, **kw)
        check(f"{op} naming a host path is refused with the scrub hint (carry 7)",
              rc == 2 and "privacy gate" in out and "scrub" in out, (rc, out[-300:]))
    check("the same carry scrubbed passes (null control)",
          wedit("append-carry", "R9-A", "evidence in the sweep's run.log") == 0)
    # carry 16: set-stage absorbed --into.
    wedit("append-group", "R9-WX", jgroup("R9-WX"))
    check("set-stage absorbed without --into is refused (carry 16)",
          refuses("needs --into", "set-stage", "R9-WX", "absorbed", branch=W))
    check("set-stage absorbed --into an unknown group is refused",
          refuses("names no group", "set-stage", "R9-WX", "absorbed",
                  into="R9-NOPE", branch=W))
    check("set-stage absorbed --into itself is refused",
          refuses("into itself", "set-stage", "R9-WX", "absorbed",
                  into="R9-WX", branch=W))
    check("set-stage absorbed --into a done group is refused",
          refuses("not a live group", "set-stage", "R9-WX", "absorbed",
                  into="R9-WD", branch=W))
    for host in ("R9-WC", "R9-WS"):
        check(f"sink barrier: set-stage absorbed --into {host} is refused",
              refuses("not a live group", "set-stage", "R9-WX", "absorbed",
                      into=host, branch=W))
    check("--into on another stage is refused",
          refuses("--into is for stage absorbed", "set-stage", "R9-WX",
                  "done", into="R9-A", branch=W))
    check("set-stage absorbed --into a live group records absorbed_into",
          wedit("set-stage", "R9-WX", "absorbed", into="R9-A") == 0
          and at_w("R9-WX")["resume"]["stage"] == "absorbed"
          and at_w("R9-WX")["resume"]["absorbed_into"] == "R9-A")
    check("a later open stage drops the stale absorbed_into",
          wedit("set-stage", "R9-WX", "in-progress") == 0
          and "absorbed_into" not in at_w("R9-WX")["resume"])

    # run --batch (carry 13): a batch of one is byte-identical to the single
    # path; a refused op is skipped and rolled back; one push carries the rest.
    def batch_bytes(branch, ops):
        edits = []
        for op in ops:
            a, v, r = parse_op(op + ["--checkout", str(drv), "--worktree",
                                      str(Path(tmp, "wtb")), "--issue-state",
                                      str(ISSUES["closed"])])
            edits.append(make_edit(a, v, r))
        bedit, results = batch_edit(edits)
        rc = write_roster(str(drv), "main", branch, str(Path(tmp, "wtb")), None,
                          "batch", True, str(seed), "batch", bedit)
        pushed = run(["git", "-C", str(origin), "branch", "--list", branch]).strip()
        return rc, results, (json.dumps(branch_roster(branch), sort_keys=True)
                             if pushed else None)

    rc1, res1, one = batch_bytes("batch-1", [["wire-issue", "R9-A", "41"]])
    check("batch of one lands and reports it applied", rc1 == 0 and res1 == [None])
    check("run via the single-op path first (control)",
          edit("wire-issue", "R9-A", "41", branch="single-1") == 0)
    check("a batch of one is byte-identical to the single-op path",
          one == json.dumps(branch_roster("single-1"), sort_keys=True))
    rc2, res2, two = batch_bytes("batch-2", [["wire-issue", "R9-A", "41"],
                                              ["set-stage", "R9-ZZ", "done"],
                                              ["wire-issue", "R9-A", "42"]])
    got = branch_roster("batch-2")["groups"][0]["issues"]
    check("a batch skips a refused op and applies the others in one push",
          rc2 == 0 and res2[0] is None and res2[1] and "R9-ZZ" in res2[1]
          and res2[2] is None and got == [10, 41, 42], (res2, got))
    check("a batch of only refused ops writes nothing",
          batch_bytes("batch-3", [["set-stage", "R9-ZZ", "done"]])[0] == 0
          and batch_bytes("batch-3", [["set-stage", "R9-ZZ", "done"]])[2] is None)

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

    def captured(call):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = call()
        return rc, out.getvalue()

    # the lint gate: a bad brief is refused BEFORE the push; the branch on the
    # remote stays where it was.
    before = run(["git", "-C", str(origin), "rev-parse", "refs/heads/edit-1"]).strip()
    badb = Path(tmp, "bad-brief.json")
    badb.write_text(json.dumps({"group": "R9-E", "lane": "L2", "after": [],
                                "brief": "a brief with __bad__ in it"}),
                    encoding="utf-8")
    rc = edit("append-group", "R9-E", str(badb), push=True, wt="wt-lint")
    check("lint gate refuses a bad brief", rc == 3, rc)
    after = run(["git", "-C", str(origin), "rev-parse", "refs/heads/edit-1"]).strip()
    check("refused push moved nothing", before == after)
    # that refused commit is the worktree's detached HEAD and on no ref:
    # reusing the worktree would drop it, so reuse is refused.
    rc, out = captured(lambda: edit("set-stage", "R9-A", "x", wt="wt-lint"))
    check("a worktree holding an unpushed edit is not reused",
          rc == 2 and "unpushed edit would be lost" in out, out[-200:])

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
              lint_cwd=str(stale), wt="wt-stale")
    check("stale lint-cwd refused", rc == 3, rc)
    ok, why = lint_gate(drv, str(stale), seed / FIXTURE_ROSTER)
    check("stale refusal named the trap",
          not ok and "stale-worktree" in why, why[:80])
    # and the good path pushes: fresh lint checkout (the seed is main's tip).
    check("fresh lint-cwd pushes",
          edit("set-stage", "R9-A", "done", push=True, branch="edit-3") == 0)
    check("pushed roster carries the edit",
          branch_roster("edit-3")["groups"][0]["resume"]["stage"] == "done")

    # THE PUSH RACE (R10-ROSTER-PUSH-RACE). Two seats edit one branch through
    # one --checkout repository, whose local branches every worktree of it
    # shares. On 2026-10-21 one run printed "pushed ... at b622ec9f1" with rc
    # 0 while no ref on origin ever held that commit: the rival's checkout -B
    # had reset the shared local branch, and the push by branch NAME sent the
    # rival's commit. The rival lands here inside this run's lint window --
    # the real one takes ~40 s -- through the same checkout (drv).
    real_lint = lint_gate
    rivals = []
    serial = iter(range(1, 100))

    def racing(times):
        busy = []

        def hooked(checkout, lint_cwd, roster_path, *rest):
            if not busy and len(rivals) < times:
                rivals.append(f"rival carry {next(serial)}")
                busy.append(1)
                try:
                    with contextlib.redirect_stdout(io.StringIO()), \
                            contextlib.redirect_stderr(io.StringIO()):
                        rc_r = edit("append-carry", "R9-B", rivals[-1],
                                    branch="edit-race", wt="wt-rival")
                finally:
                    busy.clear()
                if rc_r != 0:
                    raise Refuse(f"self-test rival edit failed rc={rc_r}")
            return real_lint(checkout, lint_cwd, roster_path, *rest)
        return hooked

    def race_tip():
        return run(["git", "-C", str(origin), "rev-parse",
                    "refs/heads/edit-race"]).strip()

    pushed_at = re.compile(r"^pushed \S+ at ([0-9a-f]{40})$", re.M)
    try:
        # the null control first: a solo edit pushes once, says no race, and
        # adds exactly one commit -- the one it reports. The stage values are
        # classified ones (R10-ORCH-ROSTER-SCHEMA): a placeholder like `solo-1`
        # is now refused at the writer, before the push these arms measure.
        rc, out = captured(lambda: edit("set-stage", "R9-A", "in-progress",
                                        branch="edit-race", wt="wt-race"))
        tip0 = race_tip()
        rc, out = captured(lambda: edit("set-stage", "R9-A", "fixing",
                                        branch="edit-race", wt="wt-race"))
        tip1 = race_tip()
        rep = pushed_at.findall(out)
        check("solo edit: rc 0, one push, no race said",
              rc == 0 and len(rep) == 1 and "lost a race" not in out, out[-300:])
        check("solo edit: exactly one commit added, the one reported",
              run(["git", "-C", str(origin), "rev-list", "--count",
                   f"{tip0}..{tip1}"]).strip() == "1" and rep == [tip1],
              (tip0, tip1, rep))

        # one rival inside the lint window: both edits reach origin, and the
        # sha this run reports is origin's tip.
        globals()["lint_gate"] = racing(1)
        rc, out = captured(lambda: edit("set-stage", "R9-A", "in-flight",
                                        branch="edit-race", wt="wt-race"))
        r = branch_roster("edit-race")
        rep = pushed_at.findall(out)
        check("race: rc 0 after re-applying on the rival's tip", rc == 0, out[-400:])
        check("race: the rival's edit survives",
              r["groups"][1].get("carry") == ["rival carry 1"], r["groups"][1].get("carry"))
        check("race: the loser's edit reaches origin",
              r["groups"][0]["resume"]["stage"] == "in-flight",
              r["groups"][0]["resume"]["stage"])
        check("race: the sha reported pushed is origin's tip",
              rep == [race_tip()], (rep, race_tip()))
        check("race: the lost race is said", "lost a race" in out, out[-300:])

        # a rival on every attempt: bounded, refused loudly, nothing of this
        # edit on origin, every rival's edit kept.
        rivals.clear()
        globals()["lint_gate"] = racing(PUSH_ATTEMPTS)
        rc, out = captured(lambda: edit("set-stage", "R9-A", "handoff",
                                        branch="edit-race", wt="wt-race-x"))
        r = branch_roster("edit-race")
        check("race on every attempt: refused (rc 2), said loudly",
              rc == 2 and "nothing of this edit reached origin" in out
              and not pushed_at.findall(out), out[-400:])
        check("race on every attempt: bounded at PUSH_ATTEMPTS rivals",
              len(rivals) == PUSH_ATTEMPTS, rivals)
        check("race on every attempt: origin holds every rival, not this edit",
              r["groups"][0]["resume"]["stage"] == "in-flight"
              and r["groups"][1]["carry"] == ["rival carry 1"] + rivals
              and "rival carry 1" not in rivals,
              (r["groups"][0]["resume"]["stage"], r["groups"][1]["carry"]))
    finally:
        globals()["lint_gate"] = real_lint

    # a push refused for another reason (here a pre-receive hook) with origin
    # unmoved is no race: refused at once, no retry, nothing reported pushed.
    hook = origin / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho 'hook says no' >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    try:
        before = race_tip()
        rc, out = captured(lambda: edit("set-stage", "R9-A", "queued",
                                        branch="edit-race", wt="wt-race"))
        check("a non-race push failure refuses at once (rc 2), no retry",
              rc == 2 and "hook says no" in out and "lost a race" not in out
              and not pushed_at.findall(out) and race_tip() == before, out[-400:])
    finally:
        hook.unlink()

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

    # fetch_origin: a ref-lock race is retried; nothing else is.
    lock = ("error: cannot lock ref 'refs/remotes/origin/train-hold': is at "
            + "a" * 40 + " but expected " + "b" * 40 + "\n")
    real_once, real_sleep = _fetch_once, time.sleep
    napped = []

    def fetch_with(script):
        """fetch_origin against scripted (rc, out, err) results; returns
        (outcome, attempts, sleeps)."""
        global _fetch_once
        seq, napped[:] = list(script), []
        calls = []

        def once(checkout):
            calls.append(1)
            return seq[min(len(calls), len(seq)) - 1]
        _fetch_once, time.sleep = once, napped.append
        try:
            fetch_origin("x")
            return "ok", len(calls), list(napped)
        except Refuse as e:
            return str(e), len(calls), list(napped)
        finally:
            _fetch_once, time.sleep = real_once, real_sleep

    got = fetch_with([(1, "", lock), (0, "", "")])
    check("fetch_origin: one lock race is retried and succeeds",
          got[0] == "ok" and got[1] == 2 and len(got[2]) == 1, got)
    got = fetch_with([(0, "", "")])
    check("fetch_origin: a clean fetch is one attempt, no sleep (null control)",
          got == ("ok", 1, []), got)
    got = fetch_with([(1, "", "fatal: could not read from remote\n")])
    check("fetch_origin: a non-race failure refuses at once, unretried",
          got[0].startswith("git -C x fetch") and "could not read" in got[0]
          and got[1] == 1 and got[2] == [], got)
    got = fetch_with([(1, "", lock + "fatal: also broken\n")])
    check("fetch_origin: a race line beside another failure is not a race",
          got[1] == 1 and "also broken" in got[0], got)
    got = fetch_with([(1, "", lock)])
    check("fetch_origin: a race past the bound still refuses, bounded",
          "cannot lock ref" in got[0] and got[1] == FETCH_ATTEMPTS
          and len(got[2]) == FETCH_ATTEMPTS - 1, got)
    got = fetch_with([(1, "", lock + lock.replace("train-hold", "other")),
                      (0, "", "")])
    check("fetch_origin: several raced refs in one fetch are one race",
          got[0] == "ok" and got[1] == 2, got)

    # --- a stale tracking ref is not an unpushed edit (P409)
    wt_ = Path(tmp, "wt")
    run(["git", "-C", str(drv), "fetch", "-q", "origin"])
    head_ = tip()
    run(["git", "-C", str(wt_), "checkout", "-q", "--detach", head_])
    check("P409: the worktree head is on origin before the tracking ref goes stale",
          _on_origin(drv, wt_, head_, "edit-1"))
    for ref_ in run(["git", "-C", str(drv), "for-each-ref", "--format=%(refname)",
                     "refs/remotes/origin/"]).split():
        run(["git", "-C", str(drv), "update-ref", "-d", ref_])
    check("P409: a stale tracking ref (a rival's push) passes after the one fetch",
          _on_origin(drv, wt_, head_, "edit-1"))
    run(["git", "-C", str(wt_), "commit", "-q", "--allow-empty", "-m", "unpushed"])
    check("P409: a real unpushed commit still refuses (null control)",
          not _on_origin(drv, wt_, run(["git", "-C", str(wt_), "rev-parse",
                                        "HEAD"]).strip(), "edit-1"))
    run(["git", "-C", str(wt_), "reset", "-q", "--hard", head_])
    run(["git", "-C", str(drv), "update-ref", "-d", "refs/remotes/origin/edit-1"])
    check("P409: two ops in one run both land after our own push",
          more("set-resume", "R9-A", "first", "--field", "note") == 0
          and more("set-resume", "R9-A", "second", "--field", "note") == 0
          and "second" in (grp("R9-A").get("resume") or {}).get("note", "")
          and subprocess.run(["git", "-C", str(drv), "rev-parse",
                              "refs/remotes/origin/edit-1"],
                             capture_output=True, text=True).stdout.strip() == tip())

    # --- P435 through an op: write_roster hands the gate the roster it found,
    # so a not-done brief already failing the lint (a merge moved the line it
    # cites) does not stop an unrelated write; the same op adding a new bad
    # citation still refuses. The lint is `errlint` (one ERROR per plant).
    seed4 = Path(tmp, "seed4")
    seed4.mkdir()
    throwaway_git_init(seed4, "-q", "-b", "main")
    (seed4 / BRIEF_LINT_NEW).parent.mkdir(parents=True)
    (seed4 / BRIEF_LINT_NEW).write_text(errlint, encoding="utf-8")
    r4 = {"groups": [{"group": "R9-A", "lane": "L1", "issues": [], "after": [],
                      "brief": "cites __bad_one__", "resume": {}}]}
    (seed4 / FIXTURE_ROSTER).parent.mkdir(parents=True, exist_ok=True)
    (seed4 / FIXTURE_ROSTER).write_text(dump(r4), encoding="utf-8")
    run(["git", "-C", str(seed4), "add", "-A"])
    run(["git", "-C", str(seed4), "commit", "-q", "-m", "a pre-existing lint error"])
    origin4 = Path(tmp, "origin4.git")
    throwaway_git_clone(seed4, origin4, "-q", "--bare")
    drv4 = Path(tmp, "drv4")
    throwaway_git_clone(origin4, drv4, "-q")

    def resume4(value, wt):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = sysrc(lambda: main(
                ["set-resume", "R9-A", value, "--field", "note",
                 "--checkout", str(drv4), "--roster-ref", "main",
                 "--branch", "edit-4", "--worktree", str(Path(tmp, wt)),
                 "--lint-cwd", str(seed4), "--push"]))
        return rc, err.getvalue()

    def at4():
        return subprocess.run(["git", "-C", str(origin4), "rev-parse", "-q", "--verify",
                               "refs/heads/edit-4"], capture_output=True,
                              text=True).stdout.strip()

    rc, said = resume4("an unrelated note", "wt-p435")
    landed = at4()
    check("P435 op: set-resume beside a pre-existing lint error lands rc 0, warning it",
          rc == 0 and bool(landed) and "WARN pre-existing" in said and "G-one" in said,
          (rc, said[-300:]))
    rc, said = resume4("adds __bad_two__", "wt-p435b")
    named = said.split("LINT GATE REFUSED the push\n", 1)[-1].splitlines()[:1]
    check("P435 op: the same op adding a new bad citation refuses rc 3, naming it first (null)",
          rc == 3 and at4() == landed and named and "G-two" in named[0],
          (rc, said[-300:]))
    shutil.rmtree(tmp, ignore_errors=True)
    # --- repeated --add (P418): extend, never keep only the last list
    for argv_, want_ in ((["--add", "a", "--add", "b"], ["a", "b"]),
                         (["--add", "a", "b", "--add", "c"], ["a", "b", "c"]),
                         (["--add", "a"], ["a"])):
        check(f"set-files {' '.join(argv_)} parses to {want_}",
              parse_op(["set-files", "G", "--worktree", "w"] + argv_)[0].add == want_)
    # --- the roster seat's lane (P215): structural ops need the queue runner's marker
    saved_lane = os.environ.pop(LANE_ENV, None)
    try:
        for op_, extra_ in (("append-carry", "lane text"), ("drop-carry", "0"),
                            ("wire-issue", "1"), ("unwire-issue", "1"),
                            ("set-after", "[]"), ("edit-brief", "b"),
                            ("set-source", "outside")):
            rc_, err_ = refusal(op_, "R9-A", extra_)
            check(f"lane: {op_} without the marker is refused, naming the queue runner",
                  rc_ == 2 and "roster_queue.py" in err_ and "R9-A" in err_, (rc_, err_[-120:]))
        check("lane: lane_refusal names a structural op called without the marker",
              lane_refusal("append-carry", "G") is not None)
        check("lane: set-stage, append-group and set-resume stay directly callable (null)",
              all(lane_refusal(o, "G") is None
                  for o in ("set-stage", "append-group", "set-resume", "mark-carry")))
        os.environ[LANE_ENV] = LANE_VALUE
        check("lane: the same structural op with the marker is accepted (null)",
              lane_refusal("append-carry", "G") is None)
        os.environ[LANE_ENV] = "something-else"
        check("lane: a marker with another value is not the lane",
              lane_refusal("drop-carry", "G") is not None)
    finally:
        if saved_lane is None:
            os.environ.pop(LANE_ENV, None)
        else:
            os.environ[LANE_ENV] = saved_lane
    print(f"roster_edit self-test: {passed} checks, "
          f"{len(failed)} failed")
    for f in failed:
        print("FAIL", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
