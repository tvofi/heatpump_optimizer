#!/usr/bin/env python3
"""Shared roster parsing and wave logic for the record tools.

    import roster_lib  # from tools/audit/seat/; the record tools import it
    python3 tools/audit/seat/roster_lib.py --self-test

This module is the one place the roster schema is read, and the one owner of
which roster a tool reads (`roster_path`). The wave computation is
`gen_table_rev3.py`'s (the round-9 alt archive tag `archive/handoff/audit-r9-alt`), the
critical path is `dev/audit/rounds/round9/fixplan/gen.py`'s `longest_chain()`, and
the open-group rule is its own: a group is OPEN while
`resume.stage not in DONE_STAGES`, so a done group's after-edges count as
satisfied and stop constraining the groups behind them. `roster_path`,
`show_roster` and `critical_path_groups` shell out (to git); nothing touches
the network, and the roster reaches a tool as a parsed dict.

Roster shape (dev/audit/rounds/round9/fixplan/gen.py writes it):
  {"groups": [{"group", "lane", "issues", "fixes", "wave", "after", "brief",
               "fixerModel", "reviewerModel", "owner_gate", "source",
               "resume": {...}, ...}], "repo", "session", ...}
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# ------------------------------------------------------------- the stage set
#
# ONE registry, so the roster's stage vocabulary cannot drift between the
# writer that accepts a word and the readers that act on it. The class this
# closes (dev/audit/rca/R10-N-vocabulary-drift.md): `in-review` was written by
# `roster_edit` while `roster_sync` had no rule for it, and `XS` was appended
# while the duration model had no such size, so `replan.build_plan` raised
# KeyError with no gate to see it. A word is legal only if it is in this tuple;
# `roster_edit` refuses anything else and `roster_sync` imports the views.
#
# `kind` says what may MOVE the word:
#   derivable   the reconciler may set or rewrite it from a repository read;
#   live-claim  a seat's claim that the work is live; the reconciler may CLOSE
#               it (a merge makes it `done`) but never rewrite it while the
#               pull request is open;
#   done        closed: a settled record, read and not rewritten;
#   disposition a human disposition; no read derives, clears or overwrites it.
STAGE_KIND = (
    ("not-started", "derivable"),
    ("planned", "derivable"),
    ("queued", "derivable"),
    # The two design steps (decision 0014): a designer or design reviewer is
    # working the group. Derivable, not a live claim: no pull request exists
    # at either, so no read rewrites them, and the planner's LIVE view stays
    # its own four words.
    ("design", "derivable"),
    ("design-review", "derivable"),
    ("in-progress", "derivable"),
    ("in-flight", "derivable"),
    ("fixing", "derivable"),
    ("handoff", "derivable"),
    ("review", "live-claim"),
    ("in-review", "live-claim"),
    ("done", "done"),
    ("rca-done", "done"),
    ("deferred", "disposition"),
    ("refused", "disposition"),
    ("refuted", "disposition"),
    ("absorbed", "disposition"),
    ("carries-open", "disposition"),
)
#: Every classified word, in the registry's order: the writer's vocabulary.
STAGES = tuple(w for w, _ in STAGE_KIND)
#: The words a repository read may touch -- every kind but a disposition. This
#: is the reconciler's guard: a stage outside it is left alone and printed.
DERIVABLE = tuple(w for w, k in STAGE_KIND if k != "disposition")
#: The live claims: a measurement may close one, never rewrite it.
LIVE_CLAIM = tuple(w for w, k in STAGE_KIND if k == "live-claim")
#: Closed stages -- gen_table_rev3.py's exact open set. A stage the orchestrator
#: records that is not here keeps the group open (and its after-edges
#: constraining).
DONE_STAGES = tuple(w for w, k in STAGE_KIND if k == "done")
#: The stages that end a group's work: the done ones, `absorbed`, whose work
#: lives in its fold destination, and the two dispositions that decide the work
#: will not be done, `refused` and `deferred`. `is_open`, the after-edge closure
#: and the carry destination check read this one set; each stays a disposition
#: (roster_sync never rewrites it), so DONE_STAGES keeps meaning "merged".
#: `refuted` stays open: it names a finding, not a group's work.
FINISHED_STAGES = DONE_STAGES + ("absorbed",)
CLOSED_STAGES = FINISHED_STAGES + ("refused", "deferred")
#: Human dispositions: nothing derives, clears or overwrites one.
DISPOSITION = tuple(w for w, k in STAGE_KIND if k == "disposition")
#: The stages in which a group's work is under way, for the planner's live
#: fraction: each live claim, plus the two repository-owned working states the
#: reconciler records. These four are exactly the tuple `tools/plan/replan.py`
#: carries as `LIVE_STAGES`, so that module converging on this view changes no
#: figure; `handoff` and `in-flight` stay out because the planner never priced
#: them live, and widening the fraction is its owner's measurement.
LIVE = ("in-progress", "fixing") + LIVE_CLAIM

# --------------------------------------------------------------- the size model
#
# The size vocabulary is the duration model's own keys; there is no second list
# to drift. A size the planner has no hours for breaks it at `size_hours[...]`
# with a KeyError no gate reads (`tools/plan/` is INERT at tests/closure.py).
DURATIONS = "tools/plan/durations.json"


class SchemaError(Exception):
    """A tree whose size model is missing or unreadable. A refusal, never a
    guessed vocabulary: `fixer.md`'s invalid input refuses, it does not guess."""


def read_durations(root=".") -> dict:
    """The measured size model at `root`: the tree whose roster is being
    written, so the vocabulary checked is the one the planner will read."""
    try:
        return json.loads((Path(root) / DURATIONS).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SchemaError(f"{DURATIONS} under {Path(root).resolve()} is "
                          f"unreadable: {e}")


def sizes(durations: dict) -> tuple:
    """The size vocabulary: the keys of the model's `sizes_hours` table."""
    try:
        return tuple(durations["sizes_hours"])
    except (KeyError, TypeError) as e:
        raise SchemaError(f"{DURATIONS} carries no sizes_hours table: {e}")

#: A group's owner-stated price (R10-HOTFIX-PLAN-OWNER-PRICE): minutes the
#: owner ruled for the group, and the text of the ruling. The planner reads
#: them (`replan.group_hours`), the editor writes them (`roster_edit set-price`),
#: and both ask `owner_price_why` -- one definition of a writable price.
OWNER_PRICE_MINUTES = "owner_price_minutes"
OWNER_PRICE_CITE = "owner_price_cite"


def owner_price_why(minutes, cite) -> str | None:
    """Why (`minutes`, `cite`) is not an owner-stated price, or None. A price
    is a positive number of minutes (a bool is no number) beside a non-blank
    citation text: a price nobody can trace to the owner is a fabricated
    measurement."""
    if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) \
            or not minutes > 0 or minutes == float("inf"):
        return f"an owner price is a positive number of minutes, not {minutes!r}"
    if not isinstance(cite, str) or not cite.strip():
        return "an owner price needs a citation text naming the owner's words"
    return None


def owner_price(group: dict) -> tuple[float, str] | None:
    """(minutes, citation) of a group's owner-stated price, None when it has
    none. One field without the other, or an invalid pair, is a SchemaError:
    a half-written price is never read as no price."""
    m, c = group.get(OWNER_PRICE_MINUTES), group.get(OWNER_PRICE_CITE)
    if m is None and c is None:
        return None
    why = owner_price_why(m, c)
    if why:
        raise SchemaError(f"{group.get('group')}: {why}")
    return float(m), c.strip()


# WHICH ROSTER -- the one owner (R10-TICK b, d). Every seat tool that reads or
# edits a roster asks `roster_path()`; none carries a path of its own. A round's
# roster is `dev/programme/rosters/wave-r<N>-groups.json`, the programme-record
# directory tests/layout.json reserves for rosters -- NOT `.claude/workflows/`,
# where the basename `wave-*-groups.json` is scanned as a LIVE web-fix-wave
# roster by `brief_lint.mjs` and `check-wave-script.mjs`, whose vocabulary the
# orchestrator's rosters do not use. The default is the NEWEST round present,
# compared as an integer (`wave-r10` sorts before `wave-r9` as text); a
# `--roster-path` override wins; no roster at all refuses loudly. A constant
# path is what kept every tool on the closed round-9 roster after round 10's
# landed beside it: `git show <r10 ref>:<r9 path>` still succeeds there, since
# the round-10 tree carries the round-9 file too.
ROSTERS_DIR = "dev/programme/rosters"
_ROSTER_NAME = re.compile(r"\Awave-r(\d+)-groups\.json\Z")
#: Where a roster lands once its pull request merges, and the fallback reader.
MAIN_REF = "origin/main"
# THE DEFAULT READER REF (O17, tvofi 2026-10-18) is `default_roster_ref`, no
# longer a constant: the round's roster branch, where the orchestrator's edits
# live between landings on main. A constant `origin/main` left the tick and
# the state docs reading four stale stages and missing one group while the
# branch was 21 commits ahead.


class RosterNotFound(Exception):
    """No roster where one was asked for: a refusal, never a silent fallback
    to some other round's roster."""


def roster_round(path: str) -> int:
    """The round number a roster path names (`.../wave-r10-groups.json` -> 10)."""
    m = _ROSTER_NAME.match(path.rsplit("/", 1)[-1])
    if not m:
        raise RosterNotFound(f"{path!r} is not a wave-r<N>-groups.json roster")
    return int(m.group(1))


def newest_roster(names) -> str | None:
    """Of the paths or basenames given, the roster with the highest round, as
    a `ROSTERS_DIR` path; None when none of them is a roster."""
    found = [(int(m.group(1)), m.group(0)) for n in names
             if (m := _ROSTER_NAME.match(str(n).rsplit("/", 1)[-1]))]
    return f"{ROSTERS_DIR}/{max(found)[1]}" if found else None


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True)


def blob_at(repo: str, ref: str, path: str) -> tuple[bool | None, str]:
    """Whether `path` is a file in `ref`'s tree: `(True, "")`, `(False, "")`
    when nothing is at that path, `(None, why)` when git cannot say.

    Read with `git ls-tree`, which reads the trees on the way to `path` and
    never the blob, so absent (an empty listing) and unreadable (git's own
    failure) are different answers. `cat-file -e` fails alike for an absent
    path and an unreadable blob, and `rev-parse --verify --quiet` exits 1
    alike for an absent path and an unreadable tree on the way to it (#2883).
    A present blob git cannot read is True here; its reader reports that.
    """
    r = _git(repo, "ls-tree", "-z", "--full-tree", ref, "--", path)
    if r.returncode:
        return None, (f"cannot read {path} at {ref}: "
                      f"{(r.stderr or r.stdout).strip()[:140]}")
    for entry in filter(None, r.stdout.split("\0")):
        meta, _, name = entry.partition("\t")
        if name == path:
            kind = meta.split()[1]
            return (True, "") if kind == "blob" else (
                None, f"{path} at {ref} is a {kind}, not a file")
    return False, ""


def roster_path(repo: str = ".", ref: str | None = None,
                override: str | None = None) -> str:
    """THE answer to "which roster", relative to the repository root.

    `override` (a tool's `--roster-path`) wins, once it is shown to exist.
    Otherwise the newest `ROSTERS_DIR/wave-r<N>-groups.json` -- in the tree of
    `ref` when one is given (read with `git ls-tree`, so a ref need not be
    checked out), else on disk under `repo`, the checkout. A missing override
    and an absent roster both raise RosterNotFound.
    """
    if override:
        there, why = (blob_at(repo, ref, override) if ref
                      else ((Path(repo) / override).is_file(), ""))
        if not there:
            raise RosterNotFound(why or f"--roster-path {override} is not a "
                                 f"file at {ref or Path(repo).resolve()}")
        return override
    if ref:
        r = _git(repo, "ls-tree", "--name-only", ref, ROSTERS_DIR + "/")
        if r.returncode:
            raise RosterNotFound(f"cannot list {ROSTERS_DIR}/ at {ref} in "
                                 f"{repo}: {(r.stderr or r.stdout).strip()[:200]}")
        names, where = r.stdout.split(), f"{ref} in {repo}"
    else:
        d = Path(repo) / ROSTERS_DIR
        names = sorted(p.name for p in d.iterdir()) if d.is_dir() else []
        where = str(Path(repo).resolve())
    path = newest_roster(names)
    if path is None:
        raise RosterNotFound(f"no {ROSTERS_DIR}/wave-r<N>-groups.json at "
                             f"{where}; pass --roster-path or --roster-ref")
    return path


def load_roster_file(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def show_roster(repo: str, ref: str, path: str | None = None) -> dict:
    """The roster at <ref> of <repo>: `git show <ref>:<roster_path()>`.

    `path` is the `--roster-path` override; without it the newest roster in
    the ref's tree is read. A path the ref does not carry refuses loudly.
    """
    path = roster_path(repo, ref, path)
    r = _git(repo, "show", f"{ref}:{path}")
    if r.returncode:
        raise RosterNotFound(f"no roster at {ref}:{path} in {repo}: "
                             f"{(r.stderr or r.stdout).strip()[:200]}")
    return json.loads(r.stdout)


# A brief opens with an attribution header ("tvofi, 2026-10-04 (...): ") before
# its first sentence. The one-line description strips it when present.
_ATTRIBUTION = re.compile(r"\A\s*[A-Za-z][\w .-]{0,40},\s*\d{4}-\d{2}-\d{2}"
                          r"(?:\s*\([^)]*\))?\s*[:.]\s*")


def round_branch(path: str) -> str:
    """The branch a round's roster edits ride to main on:
    `handoff/audit-r<N>-roster`, round-10's roster pull request's own."""
    return f"handoff/audit-r{roster_round(path)}-roster"


def git_in(repo: str):
    """A `git(argv) -> (returncode, output)` runner in `repo`, the shape
    `default_roster_ref` takes so a caller with its own (stubbed) git can
    pass that instead."""
    def run(argv):
        r = _git(repo, *argv)
        return r.returncode, r.stdout + r.stderr
    return run


def round_ref(git) -> str | None:
    """`origin/handoff/audit-r<N>-roster`, N the newest round at `MAIN_REF`;
    None when no roster is readable there. Names the ref; never checks it."""
    code, o = git(["ls-tree", "--name-only", MAIN_REF, ROSTERS_DIR + "/"])
    path = None if code else newest_roster(o.split())
    return None if path is None else "origin/" + round_branch(path)


def default_roster_ref(git) -> tuple[str, str]:
    """`(ref, note)`: the ref a reader reads the roster at when none is given.

    `origin/handoff/audit-r<N>-roster`, N the newest round at `MAIN_REF`,
    when this clone has that remote-tracking ref; else `MAIN_REF`. The note
    is empty when the answer is current and otherwise says why it may not be:
    the branch is absent here (so main, which lags the round's edits, is
    read), or main carries roster changes the branch has not merged (a fix
    pull request that edited the roster directly). The caller prints it; a
    reader never silently reads a stale roster.
    """
    ref = round_ref(git)
    if ref is None:
        return MAIN_REF, f"no roster readable at {MAIN_REF}; reading {MAIN_REF}"
    if git(["rev-parse", "--verify", "--quiet", ref + "^{commit}"])[0]:
        return MAIN_REF, (f"{ref} is absent in this clone (fetch it); reading "
                          f"{MAIN_REF}, which lags the round's roster edits")
    if git(["diff", "--quiet", f"{ref}...{MAIN_REF}", "--", ROSTERS_DIR + "/"])[0]:
        return ref, (f"WARNING: {MAIN_REF} carries roster changes {ref} has "
                     "not merged; merge main into it")
    return ref, ""


def reader_ref(repo: str, ref: str | None) -> str:
    """A reader's `--roster-ref`: the one given, else `default_roster_ref`'s
    answer in `repo`, its note printed to stderr."""
    if ref:
        return ref
    ref, note = default_roster_ref(git_in(repo))
    if note:
        print(f"roster_lib: {note}", file=sys.stderr)
    return ref


def roster_shape(roster) -> str:
    """Why `roster` is not a roster ("" when it is one).

    JSON that parses is not yet a source this module can read: every reader
    below indexes `groups` and each entry's `group`, so a list, a `groups`
    that is not one, or an entry without a string `group` is an unreadable
    source -- UNAVAILABLE to a caller that must tell it from a measurement
    (#2883) -- and not an empty roster. A missing `groups` key is still an
    empty roster: `groups_of` has always read that as no groups, and a
    roster of none is a measurement.
    """
    if not isinstance(roster, dict):
        return f"not a JSON object ({type(roster).__name__})"
    groups = roster.get("groups", [])
    if not isinstance(groups, list):
        return f"`groups` is a {type(groups).__name__}, not a list"
    for i, g in enumerate(groups):
        if not isinstance(g, dict):
            return f"groups[{i}] is a {type(g).__name__}, not an object"
        if not isinstance(g.get("group"), str):
            return f"groups[{i}] carries no string `group`"
    return ""


def groups_of(roster: dict) -> dict:
    """group id -> entry, preserving roster order."""
    return {g["group"]: g for g in roster.get("groups", [])}


def is_open(group: dict) -> bool:
    return (group.get("resume") or {}).get("stage") not in CLOSED_STAGES


def open_groups(roster: dict) -> dict:
    return {k: g for k, g in groups_of(roster).items() if is_open(g)}


def unfinished_groups(roster: dict) -> dict:
    """Every group whose work did not finish: `open_groups` plus the `refused`
    and `deferred` ones it drops. The closeout run reads this set, because a
    ruled or postponed group naming a still-open `resume.host` keeps the round
    open (`closeout_exempt`)."""
    return {k: g for k, g in groups_of(roster).items()
            if (g.get("resume") or {}).get("stage") not in FINISHED_STAGES}


#: The group that cuts the round's closing stamp; a group after it is post-closure.
CLOSE_STAMP_MARK = "STAMP-ROUND-MAJOR"
POST_CLOSE_STEP_RE = re.compile(r"after the .*\b(stamp|closeout)\b", re.I)
#: A disposition that ends a group's claim on the round: a ruling closed it.
#: `deferred` and `carries-open` still owe work and are not in it.
RULED_STAGES = ("refused", "refuted")
#: The stages in which a group's `after`-edge no longer gates a dependent: the
#: finished ones, and the ruled ones, whose work never lands (owner ruling,
#: mandate 6715477401). `deferred` is not here: postponed is not done, so a
#: dependent stays held behind it.
RELEASING_STAGES = FINISHED_STAGES + RULED_STAGES


def gates(group: dict) -> bool:
    """True when `group` holds back a group that is `after` it."""
    return (group.get("resume") or {}).get("stage") not in RELEASING_STAGES


def held_behind_deferred(G: dict) -> dict:
    """{open group: the deferred group it waits on}: a group whose `after`
    names a `deferred` group, or a group held in turn, stays unscheduled until
    the deferral is lifted. The edge to a refused or refuted group is released
    (`gates`)."""
    held: dict = {}
    grew = True
    while grew:
        grew = False
        for n, g in G.items():
            if n in held or not is_open(g):
                continue
            for a in g.get("after") or []:
                if a not in G:
                    continue
                if (G[a].get("resume") or {}).get("stage") == "deferred":
                    held[n] = a
                elif a in held and gates(G[a]):
                    held[n] = held[a]
                else:
                    continue
                grew = True
                break
    return held


def post_closure_groups(G: dict, open_: set) -> set:
    """Open groups that run after the round's closing stamp: an owner-step
    whose next step is "after the ... stamp", a group whose `after` names the
    closing-stamp group, and every group after one of those. The one owner of
    the rule: the planner and the closeout instrument both read it."""
    post = {n for n in open_
            if (G[n].get("kind") == "owner-step"
                and POST_CLOSE_STEP_RE.search(str((G[n].get("resume") or {}).get("next_step") or "")))
            or any(CLOSE_STAMP_MARK in a for a in G[n].get("after") or [])}
    grew = True
    while grew:
        grew = False
        for n in open_ - post:
            if any(a in post for a in G[n].get("after") or []):
                post.add(n)
                grew = True
    return post


def closeout_exempt(roster: dict) -> tuple:
    """(groups, issues) the round's closeout run does not wait for: the open
    post-closure groups and the issues wired to them, and every group whose
    stage is a ruled disposition (`RULED_STAGES`) unless its `resume.host`
    names a group still open. The roster keeps a ruled group open by design."""
    G, open_ = groups_of(roster), set(unfinished_groups(roster))
    post = post_closure_groups(G, open_)
    ruled = {n for n in open_
             if (G[n].get("resume") or {}).get("stage") in RULED_STAGES
             and (G[n]["resume"].get("host") not in open_)}
    return post | ruled, {i for n in post for i in G[n].get("issues") or []}


def run_refusing(tool: str, main, argv=None) -> int:
    """`main(argv)`, a missing roster printed as the one `<tool>: REFUSED ...`
    line and exit 2, never a traceback: the shared refusal of every reader
    (carry_audit's own contract)."""
    try:
        return main(argv)
    except RosterNotFound as e:
        print(f"{tool}: REFUSED {e}")
        return 2


def missing_ref_probe(script: str) -> tuple[int, int, bool]:
    """(rc, REFUSED lines, traceback seen) of `script` run against a roster ref
    that does not exist: the self-test row every roster reader owes."""
    r = subprocess.run([sys.executable, "-I", script, "--roster-ref",
                        "origin/no-such-ref-xyz"], capture_output=True, text=True)
    out = r.stdout + r.stderr
    return r.returncode, out.count("REFUSED"), "Traceback" in out


#: Owner-gate classes. A gate is `covered` when it names a mandate id or begins
#: with a prefix the mandate in force covers (0013); `owner` when it states a
#: decision still to be taken. The gate's meaning is the roster schema's, so the
#: tick calls this and holds no pattern of its own.
_GATE_COVERED = re.compile(r"\bmandate[ds]?\b|\A\s*(?:code-owned|policy|budget):", re.I)
#: A gate stating a decision still to be taken (today only "owner decision after the probe").
_GATE_OWNER = re.compile(r"\bowner decision\b", re.I)


def gate_kind(text) -> str | None:
    """None for no gate, `covered` for one the mandate in force covers, `owner`
    for one stating a decision not yet taken (a mandate or covered prefix wins)."""
    if not isinstance(text, str) or not text.strip():
        return None
    if _GATE_OWNER.search(text) and not _GATE_COVERED.search(text):
        return "owner"
    return "covered"


# ------------------------------------------------------------ the carry ledger
#
# #2733's first invariant: a carry not yet implemented routes to a group that
# is not done. ONE predicate (`pending_carries`) says which carries a group
# still owes; `roster_edit.py set-stage`, `roster_sync.py`'s merge transition
# and `carry_audit.py roster` all read it, so the writer that closes a group,
# the reconciler that closes it on a merge and the audit that reports a
# stranded carry cannot disagree.
#
# A carry is discharged by a mark `roster_edit.py mark-carry` appends to its
# text, `[implemented: <sha>]`, `[moved: <GROUP>]` or `[dismissed: <reason>]`.
# `implemented` records that the sha is on main; it is not a verification.
CARRY_MARKS = ("implemented", "moved", "dismissed")
_CARRY_MARK = re.compile(r" \[(implemented|moved|dismissed): ([^\]\n]+)\]\Z")
#: The stages in which a group can no longer receive or discharge a carry.
CARRY_CLOSED = CLOSED_STAGES
#: The stages a carry may not be routed TO (R10-CARRY-SINK-BARRIER, tvofi
#: 2026-11-10): every CARRY_CLOSED stage, plus `carries-open`, whose pull
#: request merged so no seat is left to build a carry parked there, and
#: `refuted`, which names a finding, not work. Not CARRY_CLOSED itself: a
#: carries-open group still holds and discharges the carries it owes.
CARRY_DEST_CLOSED = CARRY_CLOSED + ("carries-open", "refuted")


def carry_receivable(group: dict) -> bool:
    """THE carry-destination test: a group a carry may be routed or moved to.
    Its stage is outside CARRY_DEST_CLOSED, and it is no receiver-only sink:
    a group with no pull request, issue or fix and a recorded `files` list
    that is empty owns no seam to build the carry in. A brief does not count:
    every group has one (append-group requires it), a sink's included; a group
    with no `files` key has an unrecorded seam, not an empty one.
    carry_audit.py's destination check and roster_edit.py's append-carry,
    mark-carry moved and absorb --into all read it."""
    res = group.get("resume") or {}
    sink = (group.get("files") == [] and not res.get("pr")
            and not group.get("issues") and not group.get("fixes"))
    return res.get("stage") not in CARRY_DEST_CLOSED and not sink
#: THE CUT-OVER, per roster path: a carry that sat on a closed group at this
#: roster-branch commit is LEGACY and is never reported, so the invariant
#: starts at the cut-over with no blanket migration and nothing marked
#: implemented by default (#2733's design, carry 10(a)). A roster with no entry
#: has no legacy carries. Changing the cut-over is a change to this line.
CARRY_CUTOVER = {
    f"{ROSTERS_DIR}/wave-r10-groups.json":
        "a4c9fa3d629017fb1a0e5394bbae79cdbdfa4f9b",
}


def carry_mark(text: str) -> tuple[str, str] | None:
    """(kind, value) of the mark ending `text`, or None when it carries none."""
    m = _CARRY_MARK.search(text) if isinstance(text, str) else None
    return (m.group(1), m.group(2)) if m else None


def legacy_carries(cutover_roster: dict | None) -> dict:
    """group -> the carry texts it held while closed at the cut-over."""
    return {g["group"]: frozenset(c for c in g.get("carry") or []
                                  if isinstance(c, str))
            for g in (cutover_roster or {}).get("groups", [])
            if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}


def read_legacy(repo: str, path: str) -> dict:
    """The legacy carries of the roster at `path`, read at its cut-over commit
    in `repo`; {} for a roster with no cut-over. A cut-over the clone cannot
    read raises RosterNotFound: unknowable is a refusal, never 'no legacy',
    which would report every old carry as stranded."""
    sha = CARRY_CUTOVER.get(path)
    return legacy_carries(show_roster(repo, sha, path)) if sha else {}


def pending_carries(group: dict, legacy: dict) -> list:
    """Indices of the carries `group` still owes: unmarked and not legacy."""
    held = legacy.get(group.get("group"), frozenset())
    return [i for i, c in enumerate(group.get("carry") or [])
            if carry_mark(c) is None and c not in held]


def closing_stage(group: dict, stage: str, legacy: dict) -> tuple[str, list]:
    """The stage to write when `stage` is asked for, and the pending carries
    that decided it: `done` over a pending carry is written `carries-open`,
    which keeps the group in replan and dispatch. Never a refusal (#2733)."""
    if stage != "done":
        return stage, []
    pending = pending_carries(group, legacy)
    return ("carries-open" if pending else "done"), pending


#: A commit sha as the roster records one (7 to 40 hex); roster_edit.py writes by it.
SHA_RE = re.compile(r"\A[0-9a-f]{7,40}\Z")


def discharged(group: dict, legacy: dict) -> bool:
    """A `carries-open` group whose merge is recorded and that owes no carry:
    every carry is marked (implemented, moved or dismissed) or legacy.

    Its own deliverable merged -- `closing_stage` writes `carries-open` only
    where `done` was asked, and `resume.commit` is that merge -- and the carries
    it held are on main or live in their destinations, so no fixer work is
    left: the planner counts it closed (tvofi 2026-11-07, proposal 1). The
    roster stage is NOT rewritten by this predicate: a group the merge held
    because it owns an open issue nothing else owns (`roster_sync.hold_open`)
    still owes that record step, and `set-stage done` stays its writer. A
    group not yet merged (`not-started`, `in-progress`, ...) is never
    discharged, whatever its carries say: its own brief is undone."""
    resume = group.get("resume") or {}
    return (resume.get("stage") == "carries-open"
            and isinstance(resume.get("commit"), str)
            and bool(SHA_RE.match(resume["commit"]))
            and not pending_carries(group, legacy))


def stranded(roster: dict, legacy: dict) -> list:
    """(group, stage, index, text) of every pending carry on a closed group."""
    out = []
    for g in roster.get("groups", []):
        stage = (g.get("resume") or {}).get("stage")
        if stage in CARRY_CLOSED:
            out += [(g["group"], stage, i, g["carry"][i])
                    for i in pending_carries(g, legacy)]
    return out


def depth_of(roster: dict) -> dict:
    """Wave (dependency depth) per group, over the open groups only.

    gen_table_rev3.py's recurrence: depth = 1 + max(depth of the open
    after-edges), 1 for none. Edges to done groups are satisfied and drop out.
    A cycle is refused (gen.py refuses it at generation time; a hand-edited
    roster must not hang here).
    """
    G = groups_of(roster)
    memo: dict = {}

    def d(k, stack):
        if k in memo:
            return memo[k]
        if k in stack:
            raise ValueError(f"roster cycle through {k}: {stack + (k,)}")
        g = G.get(k)
        if g is None:
            raise ValueError(f"after-edge names no group: {k}")
        oa = [a for a in g.get("after") or [] if gates(G[a])]
        memo[k] = 1 + max((d(a, stack + (k,)) for a in oa), default=0)
        return memo[k]

    return {k: d(k, ()) for k in G}


def critical_path(roster: dict) -> list:
    """The longest after-edge chain through the OPEN groups, gen.py's
    longest_chain() restricted to them. Returns group ids, source first."""
    G = open_groups(roster)
    best: dict = {}
    order = sorted(G, key=lambda k: depth_of(roster)[k])
    for n in order:
        deps = [a for a in G[n].get("after") or [] if a in G and gates(G[a])]
        prev = max(deps, key=lambda a: best[a][0], default=None)
        best[n] = (1 + (best[prev][0] if prev else 0),
                   (best[prev][1] if prev else []) + [n])
    if not best:
        return []
    return max(best.values(), key=lambda x: x[0])[1]


def waves_of(roster: dict) -> dict:
    """wave number -> [group ids], roster order within a wave."""
    depth = depth_of(roster)
    out: dict = {}
    for k in groups_of(roster):
        out.setdefault(depth[k], []).append(k)
    return out


def one_line_brief(group: dict, limit: int = 160) -> str:
    """The brief's first sentence, attribution header stripped, pipe-safe.

    The attribution ("tvofi, 2026-10-04 (...): ") is scaffolding a seat reads
    in context; the one-line row keeps the work description only. A sentence
    longer than `limit` is cut with an ellipsis.
    """
    text = (group.get("brief") or "").strip()
    # A brief written as a markdown document opens with a heading marker; the
    # row is plain text, so the marker goes and the lines join.
    text = re.sub(r"\A\s*#{1,6}[ \t]*", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = _ATTRIBUTION.sub("", text)
    cut = re.split(r"(?<=\.)\s", text, maxsplit=1)[0]
    cut = cut.replace("|", "/")
    if len(cut) > limit:
        cut = cut[: limit - 3].rstrip() + "..."
    return cut


# ------------------------------------------------- the branch-to-group lookup
#
# A merged pull request's head branch answers for the roster group its work
# rode, so the record beat can suffix its `dev/programme/delivery/<N>.md` row with the
# group id. This is the ONE derivation of that mapping; the record-autofix
# generator (record_row.py) imports it rather than re-deriving it (#1948's
# product carrying its own consumer).

def branch_of(group: dict) -> str:
    """The branch a group's work rides: `resume.branch`, else
    `handoff/<group id lowercased>`."""
    return ((group.get("resume") or {}).get("branch")
            or "handoff/" + str(group.get("group") or "").lower())


#: The sizes whose fixer waits for an approved design (decision 0014).
DESIGN_SIZES = ("L", "XL")


def needs_design(group: dict) -> bool:
    """Whether the group is eligible for the designer and design reviewer: size
    L or XL. A group with an approved design, pre-study or prototype already on
    record is exempt at the dispatch (`cloud_dispatch --design-exempt`), where the
    orchestrator states the reason; the roster carries no such marker."""
    return group.get("size") in DESIGN_SIZES


def consumers_of(roster: dict, group_id: str) -> list[str]:
    """The live groups a `Carry:` from `group_id` may name (finding-propagation.md): the
    reverse after-edges, then the groups sharing a file in `files`, in roster order, never
    the group itself and never a group `CARRY_CLOSED` (done or absorbed)."""
    groups = groups_of(roster)
    me = groups.get(group_id) or {}
    mine = set(me.get("files") or [])
    return [n for n, g in groups.items()
            if n != group_id and (g.get("resume") or {}).get("stage") not in CARRY_CLOSED
            and (group_id in (g.get("after") or []) or mine & set(g.get("files") or []))]


def brief_lines(roster: dict, group_id: str) -> list[str]:
    """The two generated lines a fixer's brief and `prepr.sh` print (Carry 4, tvofi 2026-11-01
    card 2): the live consumer groups, the only valid `Carry:` targets, and the finding's
    class-enumeration command (the group's optional `enumeration` field). A group with
    neither yields no lines, so its brief stays byte-identical."""
    out = []
    live = consumers_of(roster, group_id)
    if live:
        out.append(f"Valid `Carry:` targets (live consumers of {group_id}: groups after it or sharing its files): "
                   + ", ".join(live))
    enum = ((groups_of(roster).get(group_id) or {}).get("enumeration") or "").strip()
    if enum:
        out.append(f"Class-enumeration command (step 8 of the fixer's contract; run it and disposition every seam it returns): {enum}")
    return out


def norm_group(s: str) -> str:
    """A roster group id or branch tail normalized for comparison:
    lowercased with ``_`` written as ``-``. `group_for_branch` and the
    critical-path reader both match on this rule, so a hand-edited case or an
    underscore in either file cannot silently stop a group matching."""
    return s.replace("_", "-").lower()


def group_for_branch(roster: dict, branch: str) -> str | None:
    """The roster group id `branch` answers for, or None.

    Two passes. First an exact `resume.branch` match (the roster's own
    record of where the group's work rides). Then the branch's LAST path
    segment, normalized (lowercased, `_` -> `-`), against each group id
    normalized the same way: `fix/r9-fr-4` answers for `R9-FR-4` without the
    roster having to name every branch spelling a seat used. Equality, never
    a prefix -- `fix/r9-fr-1` must not answer for `R9-FR-10`. None for a
    branch no group claims: the caller rows it in the neutral phrasing. A
    phase branch `<group>-pN` (handoff/r10-x-p2) answers for its group when
    no group is itself named `<group>-pN`.
    """
    if not branch:
        return None
    for g in roster.get("groups", []):
        if branch_of(g) == branch:
            return g.get("group")
    tail = norm_group(branch.rstrip("/").rsplit("/", 1)[-1])
    for g in roster.get("groups", []):
        gid = norm_group(str(g.get("group") or ""))
        if gid and gid == tail:
            return g.get("group")
    phase = re.sub(r"-p\d+\Z", "", tail)
    if phase != tail:  # handoff/<group>-pN: a phase branch of the group
        for g in roster.get("groups", []):
            if norm_group(str(g.get("group") or "")) == phase:
                return g.get("group")
    return None


#: A group's `source`: where its work came from. One value is read: OUTSIDE,
#: an accepted submission by a user outside the project (`outside_intake.py`
#: lists them). `roster_edit.py set-source` writes a word of SOURCES; absent
#: means the programme's own audit or owner work.
OUTSIDE = "outside"
SOURCES = (OUTSIDE,)


def is_outside(group: dict) -> bool:
    """Whether the group serves an accepted outside issue or contribution: its
    `source` field is OUTSIDE. An absent or any other value is internal, so a
    roster with no `source` field orders as it always did. Read from the
    roster alone, never a list of names or a GitHub read. Owner rulings tvofi
    2026-11-07 (triage P420) and 2026-11-08: outside work ranks with the
    critical path, ahead of other audit or owner work, behind a hotfix."""
    return isinstance(group, dict) and group.get("source") == OUTSIDE


def is_hotfix(group: dict) -> bool:
    """Whether the group is a hotfix: `kind` "bug" (the user-reported finding) or
    a `HOTFIX` in its name. A hotfix outranks an outside group (owner ruling
    tvofi 2026-11-07, triage P420: "unless i call the owner one a hotfix")."""
    return isinstance(group, dict) and (
        group.get("kind") == "bug" or "HOTFIX" in str(group.get("group") or "").upper())


#: dispatch_rank's answers, best first.
RANK_HOTFIX, RANK_TOP, RANK_OTHER = 0, 1, 2


def dispatch_rank(roster: dict, gid: str | None, critical) -> int:
    """RANK_HOTFIX, then RANK_TOP (an outside group or one on the critical
    path, unordered between them), then RANK_OTHER (any other group, or
    none): the one order every queue reader applies, replan.py's tiers
    without the production split (owner rulings tvofi 2026-11-07, triage
    P420, and 2026-11-08: "landing the outside requests, and landing the
    critical path ... in no particular order"). `critical` is a set of
    `norm_group` ids; a group the roster does not hold is RANK_OTHER."""
    if not gid:
        return RANK_OTHER
    g = next((x for x in roster.get("groups", []) if x.get("group") == gid), None)
    if g is not None and is_hotfix(g):
        return RANK_HOTFIX
    if g is not None and is_outside(g):
        return RANK_TOP
    return RANK_TOP if norm_group(str(gid)) in critical else RANK_OTHER


def group_for_pr(roster: dict, pr) -> str | None:
    """The roster group id whose `resume.pr` is `pr`, or None. A fork head
    carries no branch of ours, so `group_for_branch` cannot map it; the
    roster's own record of the pull request does. `pr` may be an int or a
    digit string; a bool, a non-number or an unrecorded pull request is None."""
    try:
        if isinstance(pr, bool):
            return None
        want = int(pr)
    except (TypeError, ValueError):
        return None
    for g in roster.get("groups", []):
        v = (g.get("resume") or {}).get("pr")
        if isinstance(v, bool) or v is None:
            continue
        try:
            if int(v) == want:
                return g.get("group")
        except (TypeError, ValueError):
            continue
    return None


# ------------------------------------------------------- the critical-path set
#
# Which groups a wave must drain first is the orchestrator's policy, re-cut at
# each wave edge and published beside the roster so a caller reads it without
# the out-of-tree plan. The schema is two keys and nothing else:
#
#     {"at": "<iso8601>", "critical": ["R10-GROUP", ...]}
#
# `at` records when the set was published and is not read; `critical` is the
# list of roster group ids. A ref that publishes no file means no group is
# critical -- a measurement, `set()`; a file that is there and cannot be read
# (git's own failure, invalid JSON, a non-object, a `critical` that is not a
# list of strings) is UNAVAILABLE with its reason, never a zero and never "all
# are" (#2883). `critical_path_groups` keeps the lossy None for callers whose
# contract is to fail toward "nothing critical"; `critical_path_read` is the
# reason-bearing form a board that must print the difference reads.
CRITICAL_PATH_NAME = f"{ROSTERS_DIR}/critical-path.json"


def critical_path_read(repo: str, ref: str) -> tuple[set[str] | None, str]:
    """`(set, "")` when `ref` answered; `(None, why)` when it could not be read.

    Read at `ref` (`git show`), so a caller needs no checkout of the roster
    branch. An unresolvable REF and a file that will not parse are both
    unreadable; only a ref that resolves and carries no
    `CRITICAL_PATH_NAME` at all is the measurement "none published".
    """
    if _git(repo, "rev-parse", "--verify", "--quiet",
            f"{ref}^{{commit}}").returncode:
        return None, f"cannot read {ref}: not a resolvable commit"
    there, why = blob_at(repo, ref, CRITICAL_PATH_NAME)
    if there is None:
        return None, why
    if not there:
        return set(), ""
    r = _git(repo, "show", f"{ref}:{CRITICAL_PATH_NAME}")
    if r.returncode:
        return None, (f"cannot read {CRITICAL_PATH_NAME} at {ref}: "
                      f"{(r.stderr or r.stdout).strip()[:140]}")
    try:
        data = json.loads(r.stdout)
    except ValueError as e:
        return None, f"{CRITICAL_PATH_NAME} at {ref} is not JSON: {e}"
    if not isinstance(data, dict):
        return None, (f"{CRITICAL_PATH_NAME} at {ref} is not a JSON object "
                      f"({type(data).__name__})")
    ids = data.get("critical")
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return None, (f"{CRITICAL_PATH_NAME} at {ref} carries no `critical` "
                      "list of ids")
    return {norm_group(i) for i in ids}, ""


def critical_path_groups(repo: str, ref: str) -> set[str] | None:
    """The normalized group ids `CRITICAL_PATH_NAME` lists at `ref`, or None.

    The lossy convenience form of `critical_path_read`: None covers every
    outcome a caller must treat as "nothing is critical" -- the file absent at
    this ref, git unreadable, invalid JSON, a non-object, or a `critical` that
    is not a list of strings. `gate_priority.py`'s pre-pr helper is that
    caller: it must never crash a run. A reader that has to *print* the
    difference reads `critical_path_read`.
    """
    groups, _ = critical_path_read(repo, ref)
    return groups or None


# ------------------------------------------------------------------ self-test
def _self_test() -> int:
    """Which roster, offline in a throwaway repository: the newest of two
    wins (as an integer, not as text), at a ref and on disk; an override
    wins; no roster refuses loudly. The ref arm is the R10-TICK defect: a
    round-10 tree carries the round-9 roster too, and a fixed path read it."""
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    fails: list[str] = []
    n = [0]

    def check(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")

    def refuses(call) -> str:
        """The refusal's text; "" when the call returned, and the crash
        named when it raised anything else -- a refusal is RosterNotFound."""
        try:
            call()
        except RosterNotFound as e:
            return str(e)
        except Exception as e:  # noqa: BLE001 -- a crash is not a refusal
            return f"CRASH, not a refusal: {type(e).__name__}"
        return ""

    def schema_refuses(call) -> bool:
        """True when `call` raises SchemaError naming the size model."""
        try:
            call()
        except SchemaError as e:
            return DURATIONS in str(e)
        return False

    check("round of a path", roster_round(f"{ROSTERS_DIR}/wave-r10-groups.json") == 10)
    check("newest is numeric, not textual",
          newest_roster(["wave-r9-groups.json", "wave-r10-groups.json"])
          == f"{ROSTERS_DIR}/wave-r10-groups.json")
    # THE REGISTRY (R10-ORCH-ROSTER-SCHEMA). The three views are drawn from
    # the one tuple, so a word cannot be classified for the writer's check and
    # unknown to the reader's.
    check("the views partition the registry (derivable + disposition)",
          set(DERIVABLE) | set(DISPOSITION) == set(STAGES)
          and not set(DERIVABLE) & set(DISPOSITION), STAGE_KIND)
    check("live claims are derivable (a merge can close them) and live",
          set(LIVE_CLAIM) <= set(DERIVABLE) and set(LIVE_CLAIM) <= set(LIVE),
          (LIVE_CLAIM, LIVE))
    check("a done stage is neither live nor a disposition",
          not set(DONE_STAGES) & set(LIVE) and not set(DONE_STAGES) & set(DISPOSITION),
          (DONE_STAGES, LIVE, DISPOSITION))
    check("the design steps' stages are derivable and not live (decision 0014)",
          {"design", "design-review"} <= set(DERIVABLE) and not {"design", "design-review"} & set(LIVE),
          (DERIVABLE, LIVE))
    check("the live view is the planner's own four words (no figure moves)",
          LIVE == ("in-progress", "fixing", "review", "in-review"), LIVE)
    check("the size vocabulary is the model's own keys",
          sizes({"sizes_hours": {"S": 1.0, "XL": 2.0}}) == ("S", "XL"))
    check("a model with no sizes_hours refuses, never an empty vocabulary",
          schema_refuses(lambda: sizes({"sizes_hours": None}))
          and schema_refuses(lambda: sizes({})))
    check("an absent size model refuses, never an empty vocabulary",
          schema_refuses(lambda: read_durations("/nonexistent-hpo-root")),
          "read_durations returned on a missing file")

    # THE CARRY LEDGER (#2733). One predicate decides whether a group still
    # holds a carry; set-stage, the reconciler and carry_audit's STRANDED arm
    # all read it.
    cg = {"group": "G", "resume": {"stage": "done"},
          "carry": ["old one", "new one",
                    "done one [implemented: 0123abcd]",
                    "gone one [moved: R10-X]", "nope [dismissed: a duplicate]"]}
    legacy = legacy_carries({"groups": [
        cg | {"carry": ["old one"]},
        {"group": "OPEN", "resume": {"stage": "in-progress"}, "carry": ["new one"]}]})
    check("legacy: a carry on a closed group at the cut-over is legacy; an "
          "open group's carry at the cut-over is not",
          legacy == {"G": frozenset({"old one"})}, legacy)
    check("pending: unmarked and not legacy is pending; each of the three "
          "marks discharges a carry", pending_carries(cg, legacy) == [1],
          pending_carries(cg, legacy))
    check("pending: with no cut-over every unmarked carry is pending",
          pending_carries(cg, {}) == [0, 1], pending_carries(cg, {}))
    check("a mark is read only at the end of the carry, in its own grammar",
          carry_mark("x [implemented: 0123abcd]") == ("implemented", "0123abcd")
          and carry_mark("x [implemented: 0123abcd] and more") is None
          and carry_mark("x [shipped: 0123abcd]") is None)
    check("closing: done with a pending carry is written carries-open",
          closing_stage(cg, "done", legacy) == ("carries-open", [1]),
          closing_stage(cg, "done", legacy))
    check("closing (null): done with every carry marked or legacy stays done",
          closing_stage(cg | {"carry": cg["carry"][:1] + cg["carry"][2:]},
                        "done", legacy) == ("done", []))
    check("closing (null): a stage other than done is never rewritten",
          closing_stage(cg, "in-progress", legacy) == ("in-progress", []))
    # discharged (proposal 1): merged, carries-open, nothing pending.
    co = {"group": "CO", "carry": ["a [moved: R10-X]", "b [implemented: 0123abcd]",
                                   "c [dismissed: a duplicate]"],
          "resume": {"stage": "carries-open", "commit": "0123abcd"}}
    check("discharged: carries-open, a merge commit, every carry marked",
          discharged(co, {}))
    check("discharged (null): one unmarked carry keeps it owed",
          not discharged(co | {"carry": co["carry"] + ["d"]}, {}))
    check("discharged: a legacy carry is not owed",
          discharged(co | {"carry": co["carry"] + ["old"]}, {"CO": frozenset({"old"})}))
    check("discharged (null): an unmerged group's own work is undone, whatever "
          "its carries say",
          not any(discharged(co | {"resume": {"stage": s, "commit": "0123abcd"}}, {})
                  for s in ("not-started", "in-progress", "review", "queued")))
    check("discharged (null): carries-open with no recorded merge is not",
          not discharged(co | {"resume": {"stage": "carries-open"}}, {})
          and not discharged(co | {"resume": {"stage": "carries-open",
                                              "commit": "not a sha"}}, {}))
    got = [(s[0], s[2]) for s in stranded({"groups": [
        cg, cg | {"group": "AB", "resume": {"stage": "absorbed"}},
        cg | {"group": "CO", "resume": {"stage": "carries-open"}}]}, legacy)]
    check("absorbed is closed: not open, and an after-edge on it clears",
          not is_open({"resume": {"stage": "absorbed"}})
          and is_open({"resume": {"stage": "queued"}})
          and "absorbed" not in DONE_STAGES and CARRY_CLOSED == CLOSED_STAGES,
          (CLOSED_STAGES, CARRY_CLOSED))
    check("refused and deferred are closed: not open, a carry has no destination "
          "there; refuted stays open (null)",
          not is_open({"resume": {"stage": "refused"}})
          and not is_open({"resume": {"stage": "deferred"}})
          and is_open({"resume": {"stage": "refuted"}})
          and "refused" in CARRY_CLOSED and "deferred" not in DONE_STAGES,
          CLOSED_STAGES)
    # THE SINK BARRIER (R10-CARRY-SINK-BARRIER): the carry-destination test.
    def cr(st, **kw):
        return carry_receivable(dict({"group": "G", "files": ["x.py"], "resume": {"stage": st}}, **kw))
    check("carry_receivable: carries-open, refuted and every CARRY_CLOSED stage take no carry",
          not any(cr(st) for st in ("carries-open", "refuted") + CARRY_CLOSED))
    check("carry_receivable: a receiver-only sink (no PR, issue or fix; files []) takes none",
          not cr("not-started", files=[], brief="Receives carries."))
    check("carry_receivable (null): live stages take a carry, and so does a group with an "
          "empty files list but a PR, an issue or a fix, or no files key",
          all(cr(st) for st in ("not-started", "in-progress", "queued", "review"))
          and cr("not-started", files=[], issues=[1]) and cr("not-started", files=[], fixes=[2])
          and carry_receivable({"group": "G", "files": [], "resume": {"stage": "in-progress", "pr": 3}})
          and carry_receivable({"group": "G", "resume": {"stage": "in-progress"}}))
    def rg(n, st, **kw):
        return {"group": n, "resume": {"stage": st, **kw.pop("res", {})}, **kw}
    chain = {"groups": [rg("P", "deferred"), rg("Q", "queued", after=["P"]),
                        rg("S", "queued", after=["Q"]), rg("U", "queued")]}
    check("an after-edge to a deferred group holds its dependent, and that one's own",
          held_behind_deferred(groups_of(chain)) == {"Q": "P", "S": "P"}
          and gates(groups_of(chain)["P"]) and depth_of(chain)["Q"] == 2,
          held_behind_deferred(groups_of(chain)))
    mid = {"groups": [rg("P", "deferred"), rg("Q", "refuted", after=["P"]),
                      rg("S", "queued", after=["Q"])]}
    check("a held group that is itself released (refuted) does not hold its dependent "
          "(null: the queued Q, in `chain`, does)",
          held_behind_deferred(groups_of(mid)) == {"Q": "P"}
          and not gates(groups_of(mid)["Q"]),
          held_behind_deferred(groups_of(mid)))
    for st in ("refused", "refuted", "done", "absorbed"):
        rel = {"groups": [rg("P", st), rg("Q", "queued", after=["P"])]}
        check(f"an after-edge to a {st} group is released (null: deferred holds, above)",
              not gates(rel["groups"][0]) and held_behind_deferred(groups_of(rel)) == {}
              and depth_of(rel)["Q"] == 1, depth_of(rel))
    check("a refused or deferred group stays unfinished: closeout still waits for it, "
          "and closeout_exempt exempts it only when its host is not open",
          set(unfinished_groups({"groups": [rg("R", "refused"), rg("D", "deferred"),
                                            rg("X", "done"), rg("A", "absorbed")]})) == {"R", "D"}
          and closeout_exempt({"groups": [rg("R", "refused", res={"host": "H"}),
                                          rg("H", "in-progress")]})[0] == set()
          and closeout_exempt({"groups": [rg("R", "refused"), rg("H", "in-progress")]})[0] == {"R"},
          closeout_exempt({"groups": [rg("R", "refused", res={"host": "H"}),
                                      rg("H", "in-progress")]}))
    cp = {"groups": [rg("A", "refuted"), rg("B", "queued", after=["A"]),
                     rg("F", "queued", after=["B"]), rg("G", "queued", after=["F"])]}
    check("critical_path: an edge to a refuted group is released, so the chain starts at B "
          "(null: a queued A leads it)",
          critical_path(cp) == ["B", "F", "G"]
          and critical_path({"groups": [rg("A", "queued")] + cp["groups"][1:]}) == ["A", "B", "F", "G"],
          critical_path(cp))
    ab = {"groups": [{"group": "A", "resume": {"stage": "absorbed"}},
                     {"group": "B", "after": ["A"], "resume": {"stage": "queued"}}]}
    check("an absorbed group is not in the open set or the dependency depth",
          list(open_groups(ab)) == ["B"] and depth_of(ab)["B"] == 1 and depth_of(ab)["A"] == 1, depth_of(ab))
    covered_gates = [
        "code-owned CI: mandated approval under 6329234399",
        "Policy: tvofi approves or mandate 6329234399",
        "code-owned: .claude/hooks/",
        "budget: a measurement change may move a ratchet metric",
        "D10.md is policy; .github/workflows code-owned (approve under mandate 6329234399)"]
    check("gate_kind: every gate shape on the roster is covered",
          all(gate_kind(t) == "covered" for t in covered_gates),
          [gate_kind(t) for t in covered_gates])
    check("gate_kind: a pending decision is owner; no gate is None",
          gate_kind("owner decision after the probe") == "owner"
          and gate_kind("") is None and gate_kind(None) is None)
    check("stranded: a pending carry on a done or absorbed group, never on an "
          "open one", got == [("G", 1), ("AB", 0), ("AB", 1)], got)

    check("non-rosters are ignored",
          newest_roster(["README.md", "wave-r9-groups.json.bak"]) is None)
    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        (repo / ROSTERS_DIR).mkdir(parents=True)
        throwaway_git_init(repo, "-q", "-b", "main")

        def put(rnd: int, gid: str) -> None:
            (repo / ROSTERS_DIR / f"wave-r{rnd}-groups.json").write_text(
                json.dumps({"groups": [{"group": gid}]}), encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m",
                            f"r{rnd}"], check=True)

        (repo / "README.md").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "0"],
                       check=True)
        why = refuses(lambda: roster_path(str(repo), "HEAD"))
        check("no roster at a ref refuses loudly",
              "no dev/programme/rosters/wave-r<N>-groups.json" in why, why)
        why = refuses(lambda: show_roster(str(repo), "HEAD"))
        check("show_roster with no roster refuses, never falls back",
              why and not why.startswith("CRASH"), why)
        why = refuses(lambda: roster_path(str(Path(td) / "empty")))
        check("no roster on disk refuses loudly", "--roster-path" in why, why)
        put(9, "R9-A")
        put(10, "R10-A")
        # The critical-path set: read at a ref and normalized; None for every
        # failure shape, so a caller fails to FIFO rather than crashing.
        check("a group id normalizes case and underscore", norm_group("R10_A") == "r10-a")
        # Phase branches (handoff/<group>-pN) answer for their group (carry 5).
        rg = {"groups": [{"group": "R10-PH", "resume": {"branch": "handoff/other"}},
                         {"group": "R10-PH-P2", "resume": {"branch": "handoff/x"}}]}
        check("group_for_branch: handoff/<group>-p2 resolves to the group",
              group_for_branch(rg, "handoff/r10-ph-p2") == "R10-PH-P2"
              and group_for_branch({"groups": rg["groups"][:1]},
                                   "handoff/r10-ph-p2") == "R10-PH")
        check("group_for_branch: a phase branch of no group is None (null control)",
              group_for_branch(rg, "handoff/r10-zz-p2") is None
              and group_for_branch(rg, "handoff/r10-ph-px") is None)
        check("is_outside: source `outside` only; absent or other is internal",
              is_outside({"group": "G", "source": "outside"})
              and not is_outside({"group": "G"}) and not is_outside({"group": "G", "source": "Outside"})
              and not is_outside({"group": "G", "source": True}) and not is_outside({"group": "G", "source": ["outside"]}))
        rp = {"groups": [{"group": "R10-F", "resume": {"pr": 7}}, {"group": "R10-G", "resume": {"pr": "8"}},
                         {"group": "R10-H", "resume": {"pr": None}}, {"group": "R10-I"},
                         {"group": "R10-BOOL", "resume": {"pr": True}}, {"group": "R10-ONE", "resume": {"pr": 1}}]}
        rk = {"groups": [{"group": "H1", "kind": "bug"}, {"group": "R10-HOTFIX-N"},
                         {"group": "O1", "source": "outside"}, {"group": "O2", "source": "outside", "kind": "bug"},
                         {"group": "C1"}, {"group": "P1"}]}
        check("dispatch_rank: hotfix, then outside and critical as one rank, then other, unknown "
              "or none; a hotfix beats outside",
              [dispatch_rank(rk, g, {"c1", "o1"}) for g in ("H1", "R10-HOTFIX-N", "O1", "O2", "C1", "P1", "ZZ", None)]
              == [RANK_HOTFIX, RANK_HOTFIX, RANK_TOP, RANK_HOTFIX, RANK_TOP, RANK_OTHER, RANK_OTHER, RANK_OTHER]
              and RANK_HOTFIX < RANK_TOP < RANK_OTHER
              and dispatch_rank(rk, "C1", set()) == RANK_OTHER
              and dispatch_rank(rk, "O1", set()) == RANK_TOP
              # no group id is RANK_OTHER even where a roster row carries no id and is a hotfix
              and dispatch_rank({"groups": [{"group": None, "kind": "bug"}]}, None, set()) == RANK_OTHER)
        check("is_hotfix: kind bug or HOTFIX in the name only",
              is_hotfix({"group": "X", "kind": "bug"}) and is_hotfix({"group": "r10-hotfix-x"})
              and not is_hotfix({"group": "X"}) and not is_hotfix(None))
        check("group_for_pr: resume.pr maps int or digit string; unrecorded, bool, junk are None",
              group_for_pr(rp, 7) == "R10-F" and group_for_pr(rp, "7") == "R10-F"
              and group_for_pr(rp, 8) == "R10-G" and group_for_pr(rp, 9) is None
              and group_for_pr(rp, None) is None and group_for_pr(rp, True) is None and group_for_pr(rp, 1) == "R10-ONE"
              and group_for_pr(rp, "x") is None and group_for_pr({}, 7) is None)
        check("group_for_branch: -p2 never answers a longer id by prefix",
              group_for_branch({"groups": [{"group": "R10-PH-1"}]},
                               "handoff/r10-ph-p2") is None)
        check("no critical-path file at a ref is None",
              critical_path_groups(str(repo), "HEAD") is None)
        check("critical_path_read: a ref publishing no file is (set(), ''), a "
              "measurement not a failure",
              critical_path_read(str(repo), "HEAD") == (set(), ""),
              critical_path_read(str(repo), "HEAD"))
        check("critical_path_read: an unresolvable ref is UNAVAILABLE",
              critical_path_read(str(repo), "refs/heads/nope")[0] is None
              and bool(critical_path_read(str(repo), "refs/heads/nope")[1]))
        check("roster_shape: an absent groups key is an empty roster",
              roster_shape({}) == "", roster_shape({}))
        check("roster_shape: a list is not a roster",
              "not a JSON object" in roster_shape([]), roster_shape([]))
        check("roster_shape: an entry without a string group is not a roster",
              "groups[0]" in roster_shape({"groups": [{"lane": "IN"}]}),
              roster_shape({"groups": [{"lane": "IN"}]}))
        (repo / CRITICAL_PATH_NAME).write_text(
            json.dumps({"at": "2026-10-20T00:00:00Z", "critical": ["R10_A", "R10-B"]}),
            encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "critical"],
                       check=True)
        check("the critical-path set reads at a ref, normalized",
              critical_path_groups(str(repo), "HEAD") == {"r10-a", "r10-b"},
              critical_path_groups(str(repo), "HEAD"))
        for bad in ('{"critical": "R10-A"}', '{"critical": [1]}', "not json"):
            (repo / CRITICAL_PATH_NAME).write_text(bad, encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "bad"],
                           check=True)
            check(f"a malformed critical-path file is None: {bad}",
                  critical_path_groups(str(repo), "HEAD") is None,
                  critical_path_groups(str(repo), "HEAD"))
            check(f"critical_path_read: a malformed file is UNAVAILABLE, not "
                  f"empty: {bad}",
                  critical_path_read(str(repo), "HEAD")[0] is None
                  and bool(critical_path_read(str(repo), "HEAD")[1]),
                  critical_path_read(str(repo), "HEAD"))
        check("two rosters at a ref: the newest",
              roster_path(str(repo), "HEAD")
              == f"{ROSTERS_DIR}/wave-r10-groups.json")
        check("two rosters on disk: the newest",
              roster_path(str(repo)) == f"{ROSTERS_DIR}/wave-r10-groups.json")
        got = show_roster(str(repo), "HEAD")
        check("show_roster reads the newest round's groups",
              list(groups_of(got)) == ["R10-A"], list(groups_of(got)))
        got = show_roster(str(repo), "HEAD",
                          f"{ROSTERS_DIR}/wave-r9-groups.json")
        check("an override wins over the newest",
              list(groups_of(got)) == ["R9-A"], list(groups_of(got)))
        check("an override wins on disk too",
              roster_path(str(repo), None, "README.md") == "README.md")
        why = refuses(lambda: show_roster(str(repo), "HEAD", "nope.json"))
        check("an override the ref lacks refuses loudly", "nope.json" in why, why)
        why = refuses(lambda: roster_path(str(repo), None, "nope.json"))
        check("an override the checkout lacks refuses loudly",
              "nope.json" in why, why)
        check("the round's roster branch",
              round_branch(roster_path(str(repo))) == "handoff/audit-r10-roster")

        # WHICH REF (O17): the round's roster branch when this clone has it,
        # main otherwise, and either answer says why when it is not current.
        g = git_in(str(repo))
        main_sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()

        def ref(name: str, sha: str) -> None:
            subprocess.run(["git", "-C", str(repo), "update-ref",
                            f"refs/remotes/origin/{name}", sha], check=True)
        ref("main", main_sha)
        got = default_roster_ref(g)
        check("no round branch here: main, and the note says the branch is absent",
              got[0] == MAIN_REF and "handoff/audit-r10-roster" in got[1]
              and "absent" in got[1], got)
        ref("handoff/audit-r10-roster", main_sha)
        got = default_roster_ref(g)
        check("the round branch present and carrying main: it, with no note",
              got == ("origin/handoff/audit-r10-roster", ""), got)
        put(10, "R10-B")
        ref("main", subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip())
        got = default_roster_ref(g)
        check("main moved the roster past the branch: the branch, with a warning",
              got[0] == "origin/handoff/audit-r10-roster"
              and got[1].startswith("WARNING") and MAIN_REF in got[1], got)
        ref("handoff/audit-r10-roster", main_sha)
        subprocess.run(["git", "-C", str(repo), "update-ref", "-d",
                        "refs/remotes/origin/main"], check=True)
        got = default_roster_ref(g)
        check("no roster readable at main: main, with a note (null control)",
              got[0] == MAIN_REF and got[1], got)

        # AN OBJECT GIT CANNOT READ (#2883 review 2). Absent and unreadable
        # are different answers: `cat-file -e` fails alike for an absent path
        # and an unreadable blob, and `rev-parse --verify --quiet` exits 1
        # alike for an absent path and an unreadable tree on the way to it.
        # Last in the test: the drops below leave HEAD unreadable. Each
        # dropped object is unique to its commit and asserted loose first.
        def drop(sha: str) -> bool:
            p = repo / ".git" / "objects" / sha[:2] / sha[2:]
            had = p.is_file()
            p.unlink(missing_ok=True)
            return had

        def commit_crit(at: str) -> str:
            (repo / CRITICAL_PATH_NAME).write_text(
                json.dumps({"at": at, "critical": ["R10-A"]}), encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", at],
                           check=True)
            return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
        intact = commit_crit("2026-10-28T00:00:00Z")
        check("blob_at: a file present is (True, '')",
              blob_at(str(repo), intact, CRITICAL_PATH_NAME) == (True, ""),
              blob_at(str(repo), intact, CRITICAL_PATH_NAME))
        check("blob_at: an absent path is (False, ''), a measurement",
              blob_at(str(repo), intact, f"{ROSTERS_DIR}/nope.json") == (False, ""),
              blob_at(str(repo), intact, f"{ROSTERS_DIR}/nope.json"))
        check("blob_at: an absent directory is (False, '')",
              blob_at(str(repo), intact, "zz/nope.json") == (False, ""),
              blob_at(str(repo), intact, "zz/nope.json"))
        got = blob_at(str(repo), intact, ROSTERS_DIR)
        check("blob_at: a directory is not a file, and says so",
              got[0] is None and "tree" in got[1], got)
        blob_gone = commit_crit("2026-10-28T01:00:00Z")
        check("fixture: the critical-path blob was loose and is dropped",
              drop(subprocess.run(["git", "-C", str(repo), "rev-parse",
                                   f"{blob_gone}:{CRITICAL_PATH_NAME}"],
                                  capture_output=True, text=True).stdout.strip()))
        check("blob_at: an unreadable blob is still present -- its entry is "
              "read, not its bytes",
              blob_at(str(repo), blob_gone, CRITICAL_PATH_NAME) == (True, ""),
              blob_at(str(repo), blob_gone, CRITICAL_PATH_NAME))
        got = critical_path_read(str(repo), blob_gone)
        check("critical_path_read: an unreadable blob is UNAVAILABLE with "
              "git's reason, never set()",
              got[0] is None and "cannot read" in got[1], got)
        tree_gone = commit_crit("2026-10-28T02:00:00Z")
        check("fixture: the rosters tree was loose and is dropped",
              drop(subprocess.run(["git", "-C", str(repo), "rev-parse",
                                   f"{tree_gone}:{ROSTERS_DIR}"],
                                  capture_output=True, text=True).stdout.strip()))
        got = blob_at(str(repo), tree_gone, CRITICAL_PATH_NAME)
        check("blob_at: an unreadable tree on the way is (None, why), never "
              "absent", got[0] is None and "cannot read" in got[1], got)
        got = blob_at(str(repo), tree_gone, "zz/nope.json")
        check("blob_at: a path outside the unreadable tree is still absent "
              "(null control)", got == (False, ""), got)
        got = critical_path_read(str(repo), tree_gone)
        check("critical_path_read: an unreadable tree is UNAVAILABLE, never "
              "set()", got[0] is None and "cannot read" in got[1], got)
        why = refuses(lambda: roster_path(str(repo), tree_gone, CRITICAL_PATH_NAME))
        check("an override behind an unreadable tree refuses with git's read, "
              "not 'is not a file'",
              "cannot read" in why and "is not a file" not in why, why)
    print(f"roster_lib self-test: {n[0]} checks, {len(fails)} failed")
    for f in fails:
        print("FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(_self_test())
    if sys.argv[1:2] == ["brief-lines"] and len(sys.argv) == 4:
        # brief-lines <roster-ref> <branch>: what `prepr.sh` prints; always rc 0 (informational)
        try:
            _r = show_roster(".", sys.argv[2])
            _g = group_for_branch(_r, sys.argv[3])
            print("\n".join(brief_lines(_r, _g)) if _g else f"no roster group answers for branch {sys.argv[3]}")
        except Exception as e:  # a missing ref is a note, never a refusal
            print(f"unreadable: {e.__class__.__name__}")
        sys.exit(0)
    sys.exit(__doc__)
