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
               "fixerModel", "reviewerModel", "owner_gate", "resume": {...},
               ...}], "repo", "session", ...}
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
    return (group.get("resume") or {}).get("stage") not in DONE_STAGES


def open_groups(roster: dict) -> dict:
    return {k: g for k, g in groups_of(roster).items() if is_open(g)}


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
        oa = [a for a in g.get("after") or [] if is_open(G[a])]
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
        deps = [a for a in G[n].get("after") or [] if a in G]
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
    branch no group claims: the caller rows it in the neutral phrasing.
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
    sys.exit(__doc__)
