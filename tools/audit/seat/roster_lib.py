#!/usr/bin/env python3
"""Shared roster parsing and wave logic for the round-9 record tools.

    import roster_lib  # from tools/audit/seat/; the record tools import it

This module is the one place the roster schema is read: the wave computation is
`gen_table_rev3.py`'s (handoff/audit-r9-alt:handoff/round9/state/alt), the
critical path is `tools/audit/round9/fixplan/gen.py`'s `longest_chain()`, and
the open-group rule is its own: a group is OPEN while
`resume.stage not in DONE_STAGES`, so a done group's after-edges count as
satisfied and stop constraining the groups behind them. Nothing here shells out
or touches the network; the roster reaches a tool as a parsed dict.

Roster shape (tools/audit/round9/fixplan/gen.py writes it):
  {"groups": [{"group", "lane", "issues", "fixes", "wave", "after", "brief",
               "fixerModel", "reviewerModel", "owner_gate", "resume": {...},
               ...}], "repo", "session", ...}
"""

from __future__ import annotations

import json
import re
import subprocess

# gen_table_rev3.py's exact open set. A stage the orchestrator records that is
# not in DONE_STAGES keeps the group open (and its after-edges constraining).
DONE_STAGES = ("done", "rca-done")
ROSTER_PATH = ".claude/workflows/wave-r9-groups.json"
# A brief opens with an attribution header ("tvofi, 2026-10-04 (...): ") before
# its first sentence. The one-line description strips it when present.
_ATTRIBUTION = re.compile(r"\A\s*[A-Za-z][\w .-]{0,40},\s*\d{4}-\d{2}-\d{2}"
                          r"(?:\s*\([^)]*\))?\s*[:.]\s*")


def load_roster_file(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def show_roster(repo: str, ref: str) -> dict:
    """The roster at <ref> of <repo>, through `git show <ref>:ROSTER_PATH`."""
    out = subprocess.run(["git", "show", f"{ref}:{ROSTER_PATH}"], check=True,
                         capture_output=True, text=True).stdout
    return json.loads(out)


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


def _norm_branch(s: str) -> str:
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
    tail = _norm_branch(branch.rstrip("/").rsplit("/", 1)[-1])
    for g in roster.get("groups", []):
        gid = _norm_branch(str(g.get("group") or ""))
        if gid and gid == tail:
            return g.get("group")
    return None
