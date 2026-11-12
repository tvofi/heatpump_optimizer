#!/usr/bin/env python3
"""The round's schedule model: one mechanical replan, run at a wave edge.

    python3 tools/plan/replan.py --out plan.json
    python3 tools/plan/replan.py --check --plan plan.json
    python3 tools/plan/replan.py --self-test
    python3 tools/plan/replan.py --measure-ci

What it reads
    `--roster-ref` (default `origin/handoff/audit-r10-roster`) and the newest
    `dev/programme/rosters/wave-r<N>-groups.json` in that ref's tree, read with
    `git show`; `tools/plan/durations.json` (the measured, cached durations);
    `VERSION` from the checkout. No network and no GitHub state: the same
    inputs produce byte-identical output. `--measure-ci` is the one network
    path and it only rewrites the durations file, never a plan. A roster size
    `sizes_hours` does not carry is refused, naming the roster, the group and
    the size: a duration is never invented (the live roster's `XS` has no
    measured sample).

The schedule
    List scheduling over the roster's `after` edges with six pull-request
    slots, the owner's dispatch priority first and longest-remaining-path
    within a tier. The priority is `dispatch_tier`'s, derived at every replan
    from the roster alone: main, then hotfixes, then the top tier (an
    outside request or `critical_path()`'s output for the graph as it
    stands, unordered between them), then production, and the other
    instruments ranked by the roster's `savings` field (absent sorts last);
    `TIER_LEGEND` names them. Height breaks ties within a tier. A group holds a slot from its
    start (the PR opens) to its finish (the PR merges). Groups whose fixer is
    already working (stage `in-progress`) were dispatched before the replan:
    up to six start at the replan instant in the same priority order, whatever
    their dependency state, and the rest wait for a slot like any pending
    group.

    The coordinator cap is enforced on the groups the PLAN dispatches. The
    inherited in-progress set can itself exceed it -- on 2026-10-20 three of
    the six running fixers touch `coordinator.py`, against a cap of two, while
    no coordinator pull request was measured open. The plan records that set
    in `generated.inherited_coordinator` (cap, groups, whether it exceeds the
    cap) and `--check` refuses a plan whose record is missing or disagrees
    with its groups: the excess is stated, not hidden, and never counted as a
    cap the plan chose to breach.

    Merges are batched. A finished group waits up to `batch_window_minutes`
    for a partner; then the batch lands and its slots free. One batch pays one
    gate run (`fast (3.14)` + `closures` + `Analyze (python)`), so a batch of k
    shares that cost where k separate merges pay it k times. The window is the
    wall-time price of that sharing and the summary reports it.

    A patch stamp is cut once `stamp_every` production groups have merged
    since the last one. A stamp never blocks a dispatch; it pays its own gate
    run, because `stamp.py` pushes to main. The programme closes with one
    `round-close` stamp: round N's major, vN.0.0 (decision 0016), assigned by
    `stamp.next_version` -- the rule `stamp.py --round-close N` runs -- from
    the round the roster's path names, so the plan and the stamp cannot
    disagree on it; a roster naming no round refuses, never defaults.

Why it checks what it checks
    A schedule that violates a cap is not a plan. `--check` refuses (exit 1)
    on: more than `slots` in flight at any instant; more than `seats` working
    at any instant; more than `coordinator_cap` PLANNED groups in flight
    touching `coordinator.py`, or an inherited coordinator record that is
    missing or disagrees with the groups; a dependency that finishes after its
    dependent starts (an inherited in-progress group that started before its
    dependency is recorded in `generated.inherited_dependency_violations`, not
    refused -- the replan cannot undo it); a stamp cadence breach; a wave
    opening while the open-PR cap is full; a summary that disagrees with the
    groups it summarises; a STALE plan -- one whose `generated.roster_blob`
    is not the roster's blob at its `roster_ref` now (`stale_reason`, the
    rule the page renderer `tools/audit/seat/plan_page.py` refuses on too).
    A schedule computed from a roster that has since moved is not the plan
    either, and before this rule `--check` printed PLAN OK on one.
    `--self-test` plants each violation and proves the refusal fires.

plan.json shape
    schema; generated {roster_ref, roster_blob, start, version, round, durations,
    model {sizes_hours, live_remaining_fraction, sizes_provenance}, caps,
    inherited_coordinator, inherited_dependency_violations}; summary {closure,
    wall_hours, ci_minutes, batches, stamps, ...}; critical_path [group...];
    groups {name: {wave, start, finish, slot, duration_minutes, size, lane,
    tier, level, live, inherited, coordinator, batch, stamp, after}}; waves [{wave,
    opens, drains, stamp, batch, groups}]; batches [{id, at, groups}]; stamps
    [{version, at, kind, batch, carries}].
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get("REPLAN_SEAT_DIR")
               or str(Path(__file__).resolve().parent.parent / "audit" / "seat"))
import roster_lib  # noqa: E402 -- the one owner of which roster a tool reads

sys.path.insert(0, str(Path(roster_lib.__file__).resolve().parents[2] / "release"))
import stamp  # noqa: E402 -- the one owner of the version a stamp assigns

SELF = "tools/plan/replan.py"

# Production lanes cut a stamp. Instrument, Replay and Docs work does not, on
# the owner's cadence ("a patch stamp after roughly five production groups").
LANES = ("Learners", "Core model", "Product UX", "Replay", "Instruments", "Docs")
PRODUCTION = ("Learners", "Core model", "Product UX")

# The kind of the one stamp that closes the programme: the round's major.
ROUND_CLOSE = "round-close"

# A fixer already working. `queued` is not working: the plan dispatches it.
LIVE_STAGES = ("in-progress", "fixing", "review", "in-review")
#: The live stages whose build is finished: a group here starts from its
#: review rounds, not from a fresh fixer start.
REVIEW_STAGES = ("review", "in-review")

DEFAULT_CAPS = {
    "slots": 20,             # open pull requests: the owner's cap since 2026-11-07
    "seats": 20,             # fixers working: one per open pull request
    "coordinator_cap": 2,    # open pull requests touching coordinator.py
    "stamp_every": 3,        # production groups per patch stamp (tvofi 2026-10-26)
}
#: Where DEFAULT_CAPS' slots and seats come from, recorded in every plan that
#: uses them: a plan drawn at a cap nobody chose must say whose cap it is.
CAPS_PROVENANCE = ("tvofi 2026-11-07 (#201 comment 6707334933, superseding 6544047621): "
                   "20 open pull requests; replan.py DEFAULT_CAPS")


#: What "the programme is closed" means beyond the plan's last finish (tvofi
#: 2026-11-07, #201): the plan states it beside `summary.closure`, which is only
#: the schedule's own end.
CLOSURE_CONDITIONS = ("no open pull requests", "no handoffs", "no carries", "no findings",
                      "no leads", "only the coordination issue open")


class PlanError(Exception):
    """An input the model refuses: a cycle, an unknown edge, a bad roster."""


# --------------------------------------------------------------------- roster

def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def load_roster(repo: str, ref: str | None = None, path: str | None = None,
                file: str | None = None) -> tuple[dict, str, str]:
    """(roster, roster_ref, blob) -- `file` wins for a self-test fixture;
    otherwise the roster is read at `ref` with `git show`, never from disk.

    WHICH roster and its filename grammar are `tools/audit/seat/roster_lib.py`'s
    to own (`roster_path`, `show_roster`); re-declaring the
    `wave-r<N>-groups.json` pattern here gave the tree a second reader of the
    same convention, which `tools/policy/agreement.mjs` refuses.
    """
    if file:
        return json.loads(Path(file).read_text(encoding="utf-8")), file, ""
    if not ref:
        ref = "origin/handoff/audit-r10-roster"
    try:
        path = roster_lib.roster_path(repo, ref, path)
        roster = roster_lib.show_roster(repo, ref, path)
    except roster_lib.RosterNotFound as exc:
        raise PlanError(str(exc)) from exc
    return roster, ref, roster_blob(repo, ref, path)


def roster_blob(repo: str, ref: str, path: str) -> str:
    """The blob id of `ref:path`; "" when git cannot name it."""
    blob = _git(repo, "rev-parse", f"{ref}:{path}")
    return blob.stdout.strip() if blob.returncode == 0 else ""


def stale_reason(plan: dict, repo: str, ref: str | None = None,
                 path: str | None = None) -> str | None:
    """Why `plan` no longer describes the roster, or None when it does.

    THE freshness rule, for `--check` and for the page renderer alike: the
    roster blob the plan was built from must be the blob at `ref` (default:
    the plan's own `generated.roster_ref`) now. A plan that pins no blob (a
    `--roster-file` fixture) is refused too: its freshness is unknowable.
    The ref is read as this clone has it; fetch it first.
    """
    gen = plan.get("generated") or {}
    want = gen.get("roster_blob") or ""
    ref = ref or gen.get("roster_ref") or ""
    if not want:
        return ("plan.json pins no roster blob (built from a --roster-file "
                "fixture?), so its freshness is unknowable; replan from a ref")
    try:
        path = roster_lib.roster_path(repo, ref, path)
    except roster_lib.RosterNotFound as exc:
        return f"cannot read the roster the plan claims: {exc}"
    have = roster_blob(repo, ref, path)
    if have != want:
        return (f"plan.json is stale: built from roster blob {want[:12]}, but "
                f"{ref}:{path} is now {have[:12] or 'unreadable'}; re-run "
                f"{SELF} --out <plan.json>")
    return None


def groups_of(roster: dict) -> dict:
    return {g["group"]: g for g in roster.get("groups", [])}


#: A group in a closed stage (`roster_lib.CLOSED_STAGES`, `absorbed` included:
#: R10-FLOW-TOOLKIT-MODEL carry 2) is not scheduled as open work; its remaining
#: work lives in the group its resume note names.
ABSORBED_RE = re.compile(r"absorbed into ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)")


def is_done(group: dict) -> bool:
    return not roster_lib.is_open(group)


def absorbers(G: dict) -> dict:
    """{absorbed group: (absorber or None, advisory or None)}: the group the
    resume note names ("absorbed into <G>"), and an advisory -- never a
    refusal -- for a note that names no group in the roster."""
    out = {}
    for n in sorted(G):
        res = G[n].get("resume") or {}
        if res.get("stage") != "absorbed":
            continue
        m = ABSORBED_RE.search(" ".join(str(res.get(k) or "") for k in ("note", "next_step")))
        into = m.group(1) if m and m.group(1) in G else None
        out[n] = (into, None if into else
                  f"ADVISORY: {n} is absorbed but its resume note names no existing group")
    return out


#: Paths that are instruments, CI or records, never the integration (tvofi
#: 2026-11-06: the plan placed instrument and CI fixes in the core lane).
_NON_PRODUCT_PREFIXES = ("tools/", "tests/", ".github/", ".claude/", "dev/", "docs/")
_NON_PRODUCT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md", "RELEASE_NOTES.md")
#: A group touching any of these lands a tool, so it is not user docs.
_TOOLING_PREFIXES = ("tools/", ".github/", ".claude/")
#: Kinds that land tools: a group the name rules leave unplaced and whose
#: files do not place it is drawn as Instruments when its kind is one of these.
INSTRUMENT_KINDS = ("instrument", "policy", "rca", "tooling")


def _owned_lane(group: dict) -> str | None:
    """Instruments (or Docs, for a doc group) when every file the group owns
    is an instrument, CI or record path; None when it owns no file, a bare
    filename, or any file outside those paths (the integration stays core)."""
    files = list(group.get("files") or []) + list(group.get("hot_files") or [])
    if not files or not all(f.startswith(_NON_PRODUCT_PREFIXES) or f in _NON_PRODUCT_FILES
                            for f in files):
        return None
    user_docs = (any(f.startswith("docs/") or f == "README.md" for f in files)
                 and not any(f.startswith(_TOOLING_PREFIXES) for f in files))
    return "Docs" if group.get("kind") == "doc" or user_docs else "Instruments"


#: Group-name stems drawn as Instruments. A stem matches the group of that exact
#: name or one named `<stem>-...`: a bare string prefix also took a stem's
#: look-alikes (`R10-I1` priced `R10-I18N-DE`, an integration group, as an
#: instrument).
INSTRUMENT_NAME_STEMS = (
    "R10-TICK", "R10-TRAIN", "R10-REF", "R10-D15", "R10-PREPR", "R10-GATE",
    "R10-STALE", "R10-PRE-EDIT", "R10-POLICY", "R10-I1", "R10-ARCHSCORE",
    "R10-STRUCTURE", "R10-BRIEFS")


def roster_lane(group: dict) -> str:
    """The lane a group is drawn in and counted under for the stamp cadence.

    Ported from the out-of-tree renderer this replaces, which was the only
    definition: `kind` first, then the group's own name, then the files it
    owns, then a tool-landing kind or roster `class` (the signal `work_class`
    prices); only a group none of these places is core
    model work (tvofi 2026-11-06: instrument and CI fixes were drawn there).
    """
    g = group["group"]
    k = group.get("kind")
    if g in ("R10-ARCH-DOCS", "R10-I5-DOCS"):
        return "Docs"
    if k in ("instrument", "policy") or any(
            g == p or g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS):
        return "Instruments"
    if "REPLAY" in g:
        return "Replay"
    if g in ("R10-VENT-DETECTOR", "R10-NIGHT-FOLDS", "R10-TRUST-RELATIVE",
             "R10-RATIO-ANCHOR", "R10-RATIO-SITES", "R10-LEARNER-ETA",
             "R10-HEAT-METER", "R10-COP-GATE"):
        return "Learners"
    if k == "owner" or g in ("R10-UX-HEALTH", "R10-CONFIGFLOW-PAGES", "R10-DEEPLINK-CENSUS"):
        return "Product UX"
    if owned := _owned_lane(group):
        return owned
    if k in INSTRUMENT_KINDS or group.get("class") == "instrument":
        return "Instruments"
    return "Core model"


#: The work classes the size model is measured and priced in
#: (`tools/plan/size_durations.py`).
WORK_CLASSES = ("production", "instrument", "record", "triage")


def work_class(group: dict) -> str:
    """What kind of work a group is, for its duration: a triage batch, a
    roster or handover record, an instrument (its lane, or an RCA, policy or
    tooling kind, which land tools), else production."""
    g, k = group["group"], group.get("kind")
    if "TRIAGE" in g:
        return "triage"
    branch = (group.get("resume") or {}).get("branch") or ""
    if k == "record" or "audit-r" in branch and "-roster" in branch:
        return "record"
    if roster_lane(group) in ("Instruments", "Docs") or k in INSTRUMENT_KINDS:
        return "instrument"
    return "production"


def touches_coordinator(group: dict) -> bool:
    files = list(group.get("hot_files") or []) + list(group.get("files") or [])
    return any(f.endswith("coordinator.py") for f in files)


# ----------------------------------------------------------------------- graph

def dependency_graph(G: dict, legacy: dict | None = None) -> tuple[dict, set, set]:
    """(open deps per open group, open set, done set).

    An `after` edge to a done group is satisfied and drops out. An `after`
    naming no group in the roster is refused: silently dropping it would make
    a dependency look met when the roster has a typo. A discharged group
    (`roster_lib.discharged` over `legacy`, the roster's cut-over carries: a
    merged `carries-open` group every carry of which is marked) is done here:
    no fixer work is left, so it takes no slot and clears its after-edges
    (tvofi 2026-11-07, proposal 1).
    """
    done = {n for n, g in G.items()
            if is_done(g) or roster_lib.discharged(g, legacy or {})}
    open_ = set(G) - done
    deps = {}
    for n in open_:
        out = []
        for a in G[n].get("after") or []:
            if a not in G:
                raise PlanError(f"{n}: after-edge names no group: {a}")
            if a in open_ and roster_lib.gates(G[a]):
                out.append(a)
        deps[n] = out
    return deps, open_, done


def topo_order(deps: dict) -> list:
    """Open groups in dependency order; a cycle is refused, never parked."""
    state: dict = {}
    order: list = []

    def visit(n: str, stack: tuple):
        if state.get(n) == 2:
            return
        if state.get(n) == 1:
            raise PlanError("roster cycle through " + " -> ".join(stack + (n,)))
        state[n] = 1
        for a in deps[n]:
            visit(a, stack + (n,))
        state[n] = 2
        order.append(n)

    for n in sorted(deps):
        visit(n, ())
    return order


def levels(deps: dict, order: list) -> dict:
    """Dependency depth: 1 for a group with no open dependency."""
    lvl: dict = {}
    for n in order:
        lvl[n] = 1 + max((lvl[a] for a in deps[n]), default=0)
    return lvl


def children_of(deps: dict) -> dict:
    children: dict = {n: [] for n in deps}
    for n in deps:
        for a in deps[n]:
            children[a].append(n)
    return children


def heights(deps: dict, dur: dict, order: list) -> dict:
    """Remaining longest path in hours, own duration included.

    The dispatch rule is longest-remaining-path-first: shortest-job-first
    maximises throughput and wrecks the critical path (nine short groups once
    took slots ahead of a direct dependency of a live group).
    """
    children = children_of(deps)
    h: dict = {}
    for n in reversed(order):
        h[n] = dur[n] + max((h[c] for c in children[n]), default=0)
    return h


def critical_path(deps: dict, dur: dict, order: list) -> list:
    """The longest dependency chain by duration, source first.

    A property of the graph, not of the dispatch order: walking back from the
    last finisher picked whichever small group happened to be scheduled last,
    so the path jumped between waves for no reason a reader could see.
    """
    if not deps:
        return []
    height = heights(deps, dur, order)
    children = children_of(deps)
    node = max(deps, key=lambda n: (height[n], n))
    chain = [node]
    while children[chain[-1]]:
        node = max(children[chain[-1]], key=lambda c: (height[c], c))
        chain.append(node)
    return chain


#: The owner's priority order, as tiers. 1 main (a red main or a main fix):
#: it blocks every merge, the top tier's included. 2 hotfixes (user-reported
#: production findings): "all accepted outside issues or contributions should
#: be prioritized higher than audit or owner submitted ones unless i call the
#: owner one a hotfix" (tvofi 2026-11-07, triage P420). 3 the top tier (tvofi
#: 2026-11-08: "landing the outside requests, and landing the critical path
#: ... All of them have top priority ... in no particular order"): an
#: outside request (`roster_lib.is_outside`) or the critical path, ordered
#: among themselves by height alone; 11-08 keeps the 11-07 hotfix exception
#: (mandate 6715477401). Below it the standing order (2026-10-30) continues:
#: 4 production work and instruments saving SAVING_TIER_HOURS or more, 5
#: every other instrument, ranked by its savings.
TIER_MAIN, TIER_HOTFIX, TIER_TOP, TIER_PRODUCTION_WORK, TIER_INSTRUMENT = 1, 2, 3, 4, 5
SAVING_TIER_HOURS = 12.0
#: Each tier in words, for a reader of `tier` (the plan page's legend).
TIER_LEGEND = {
    TIER_MAIN: "main",
    TIER_HOTFIX: "hotfixes",
    TIER_TOP: "outside requests and the critical path, unordered",
    TIER_PRODUCTION_WORK: f"production and instruments saving {SAVING_TIER_HOURS:g} h or more",
    TIER_INSTRUMENT: "other instruments by savings",
}


def dispatch_tier(group: dict, on_cp: bool, savings: float | None) -> tuple[int, str]:
    """(tier, the roster fields that decided it) for one open group.

    Read from the roster alone: `kind` "main" or a `-MAIN-FIX`/`-MAIN-RED`
    name is main; `roster_lib.is_hotfix` (a `kind` "bug" or a HOTFIX name, of
    any work class) is a hotfix; `on_cp` (`critical_path()`'s output, never a
    stored list) or a `source` of outside (`roster_lib.is_outside`, never a
    list of names) is the top tier; `work_class` production, or an
    instrument whose `savings` is at least SAVING_TIER_HOURS, is the
    production tier; else the instrument tier.
    """
    g, k = group["group"], group.get("kind")
    if k == "main" or "-MAIN-FIX" in g or "-MAIN-RED" in g:
        return TIER_MAIN, f"main (kind {k!r}, name)"
    cls = work_class(group)
    if roster_lib.is_hotfix(group):
        return TIER_HOTFIX, f"hotfix (kind {k!r}, name)"
    outside = "outside request (source)"
    if on_cp:
        return TIER_TOP, "critical path" + (f"; {outside}" if roster_lib.is_outside(group) else "")
    if roster_lib.is_outside(group):
        return TIER_TOP, outside
    if cls == "production":
        return TIER_PRODUCTION_WORK, "production (work_class)"
    if savings is not None and savings >= SAVING_TIER_HOURS:
        return TIER_PRODUCTION_WORK, f"instrument saving {savings:g} h >= {SAVING_TIER_HOURS:g}"
    if savings is None:
        return TIER_INSTRUMENT, f"{cls}; savings not recorded on the roster, ranked last"
    return TIER_INSTRUMENT, f"{cls} saving {savings:g} h"


def dispatch_key(n: str, tier: dict, savings: dict, height: dict,
                 dur_min: dict) -> tuple:
    """The dispatch order, lowest first: tier, then (tier 5 only) savings
    descending with an unrecorded savings last, then the tie-break that
    predates the tiers: height, duration, name. Nothing ranks the critical
    path within a tier: it holds the top tier with the outside requests, in
    no particular order (tvofi 2026-11-08), so height decides. It is a pure
    function of the plan's own fields (`plan.json` records it per group as
    `sort_key`), so a reader can re-derive the order from the plan.
    """
    t = tier[n]
    sav = (-savings[n] if n in savings else float("inf")) if t == TIER_INSTRUMENT else 0.0
    return (t, sav, -height[n], -dur_min[n], n)


# ------------------------------------------------------------- duration model

HELD_STAGE = "carries-open"


def held_open(group: dict, durations: dict, pending: list) -> tuple[int, str]:
    """(open carries, how known) for a carries-open group, counting only
    `pending` (`roster_lib.pending_carries`: unmarked and not legacy). The
    measured count (`held_open_carries`, `tools/plan/size_durations.py`),
    never above the carries then held that are still pending, plus every
    pending carry appended since; a group it never measured counts every
    pending carry."""
    rec = (durations.get("held_open_carries") or {}).get(group["group"])
    if rec is None:
        return len(pending), f"{len(pending)} carries, none measured as answered"
    cut = int(rec["carries"])
    added = sum(1 for i in pending if i >= cut)
    then = min(int(rec["open"]), sum(1 for i in pending if i < cut))
    return then + added, (f"{then} open carries at measurement"
                          + (f" + {added} appended since" if added else ""))


def group_hours(group: dict, durations: dict, is_live: bool, where: str,
                legacy: dict | None = None) -> tuple[float, str]:
    """(hours of work left, the basis in words) for one open group.

    carries-open: ceil(open carries / carries_per_part) parts of
        carry_part_hours -- zero open carries plan zero (the record step);
    otherwise: first_round_hours (by class where measured, else the size)
        + (review_rounds - 1) * round_hours, + carry_hours per carry above
        the size's carry_baseline (a carry absorbed after sizing is work the
        size did not price), times live_remaining_fraction for a working
        fixer. A durations file without the measured fields falls back to
        sizes_hours alone. An unmeasured size is refused: a hand-written
        duration would be a fabricated measurement, and a KeyError from
        inside the schedule names neither the group nor the roster.
    Both carry counts are `roster_lib.pending_carries` (`legacy`: the
    roster's cut-over, `roster_lib.read_legacy`): a carry marked implemented,
    moved or dismissed is not work left, and the basis says how many were
    left out.
    """
    n, size, cls = group["group"], group.get("size") or "M", work_class(group)
    stage = (group.get("resume") or {}).get("stage")
    pending = roster_lib.pending_carries(group, legacy or {})
    left = len(group.get("carry") or []) - len(pending)
    left_out = f", {left} marked carries left out" if left else ""
    if stage == HELD_STAGE and durations.get("carries_per_part"):
        k, how = held_open(group, durations, pending)
        parts = math.ceil(k / float(durations["carries_per_part"]))
        return (parts * float(durations["carry_part_hours"]),
                f"{how}: {parts} part(s){left_out}")
    sizes = durations["sizes_hours"]
    if size not in sizes:
        raise PlanError(f"{n}: size {size!r} has no measured duration in sizes_hours "
                        f"({', '.join(sorted(sizes))}) -- roster {where}")
    first = durations.get("first_round_hours") or {}
    if size in first:
        cell = (durations.get("first_round_by_class_hours") or {}).get(size, {})
        rcell = (durations.get("review_rounds_by_class") or {}).get(size, {})
        work = float(cell.get(cls, first[size]))
        rounds = float(rcell.get(cls, durations["review_rounds"][size]))
        hours = work + (rounds - 1) * float(durations["round_hours"])
        why = f"{size}/{cls if cls in cell else 'all'}: {work:g} h + {rounds - 1:.2f} extra rounds"
        extra = len(pending) - float((durations.get("carry_baseline") or {}).get(size, 0))
        if extra > 0 and durations.get("carry_hours"):
            hours += extra * float(durations["carry_hours"])
            why += f" + {extra:g} absorbed carries"
        why += left_out
    else:
        hours, why = float(sizes[size]), f"{size}: sizes_hours"
    if is_live and stage in REVIEW_STAGES and size in first:
        # The build is done: what is left is the review rounds still to run, at
        # least one, never more than a fresh fixer's remaining share.
        left_rounds = max(rounds - 1, 1.0)
        in_review = min(left_rounds * float(durations["round_hours"]),
                        hours * float(durations.get("live_remaining_fraction", 0.7)))
        return in_review, why + f", in {stage}: {left_rounds:.2f} review round(s) left"
    if is_live:
        hours *= float(durations.get("live_remaining_fraction", 0.7))
        why += ", working (live_remaining_fraction)"
    return hours, why


#: The measured fields (`tools/plan/size_durations.py`) a plan records and
#: `--check` requires: the rounds model and the held-stage model.
MODEL_FIELDS = ("first_round_hours", "first_round_by_class_hours", "review_rounds",
                "review_rounds_by_class", "round_hours", "carry_baseline", "carry_hours",
                "carry_part_hours", "carries_per_part", "sizes_percentile",
                "carry_provenance")
SIZE_ORDER = ("XS", "S", "M", "L", "XL")


def model_refusals(model: dict) -> list:
    """Why a duration model is not the measured one, or [] if it is: the
    review rounds and the held stage are modelled explicitly, and no larger
    size plans shorter than a smaller one (the 2026-10-18 model planned S at
    13.1 h above M at 11.4 h)."""
    bad = [f"model: {k} is not recorded (re-derive with --measure-sizes)"
           for k in ("first_round_hours", "review_rounds", "round_hours",
                     "carries_per_part", "carry_part_hours") if k not in model]
    sizes = [(s, float(model["sizes_hours"][s])) for s in SIZE_ORDER
             if s in (model.get("sizes_hours") or {})]
    for (a, ha), (b, hb) in zip(sizes, sizes[1:]):
        if hb < ha:
            bad.append(f"model: {b} plans {hb:g} h, under {a}'s {ha:g} h")
    return bad


#: The 2026-10-18 model, kept as the self-test's old-model plant.
OLD_MODEL = {"sizes_hours": {"S": 13.1, "M": 11.4, "L": 20.1, "XL": 30.2},
             "live_remaining_fraction": 0.7}
#: A measured-shape fixture (round numbers, so every expectation is exact).
MEASURED_FIXTURE = {
    "sizes_hours": {"S": 18.0, "M": 24.0, "L": 32.0, "XL": 32.0},
    "first_round_hours": {"S": 10.0, "M": 16.0, "L": 20.0, "XL": 20.0},
    "first_round_by_class_hours": {"S": {"instrument": 8.0}},
    "review_rounds": {"S": 3.0, "M": 3.0, "L": 4.0, "XL": 4.0},
    "review_rounds_by_class": {"S": {"instrument": 2.0}},
    "round_hours": 4.0, "carry_baseline": {"S": 2, "M": 4, "L": 6, "XL": 6},
    "carry_hours": 4.0, "carry_part_hours": 20.0, "carries_per_part": 5.0,
    "held_open_carries": {"H1": {"open": 1, "carries": 8}, "H0": {"open": 0, "carries": 3}},
    "live_remaining_fraction": 0.5, "batch_window_minutes": 0,
    "ci": {"fast (3.14)": {"median_minutes": 1.0}, "closures": {"median_minutes": 1.0},
           "Analyze (python)": {"median_minutes": 1.0}},
}


def selftest_model() -> int:
    """The measured duration model, the started-group admission and the
    owner's priority order: each arm names what the old code did instead."""
    fails = []

    def expect(name, cond, detail=""):
        print(("ok   " if cond else "FAIL ") + name + ("" if cond else f": {detail}"))
        if not cond:
            fails.append(name)

    M = MEASURED_FIXTURE

    def grp(n, size="S", kind="defect", stage="not-started", after=(), **kw):
        return {"group": n, "size": size, "kind": kind, "after": list(after),
                "resume": {"stage": stage}, **kw}

    # 1. the size model. The old model is refused, the measured one is not.
    old = model_refusals(OLD_MODEL)
    expect("the 2026-10-18 model is refused: no rounds model, no held model, M under S",
           any("round_hours" in b for b in old) and any("carries_per_part" in b for b in old)
           and any("M plans 11.4 h, under S's 13.1 h" in b for b in old), str(old))
    expect("the measured fixture model is accepted (null control)", model_refusals(M) == [],
           str(model_refusals(M)))
    h, why = group_hours(grp("P", "S"), M, False, "fx")
    expect("a production S plans first-round 10 + 2 extra rounds x 4 = 18 h", h == 18.0, f"{h} {why}")
    h, _ = group_hours(grp("I", "S", "instrument"), M, False, "fx")
    expect("an instrument S plans its class cell: 8 + 1 x 4 = 12 h", h == 12.0, h)
    h, _ = group_hours(grp("P", "S", carry=["x"] * 5), M, False, "fx")
    expect("three carries absorbed past the S baseline add 3 x 4 h (30 h)", h == 30.0, h)
    h, _ = group_hours(grp("W", "S", stage="in-progress"), M, True, "fx")
    expect("a working fixer plans live_remaining_fraction of its hours (9 h)", h == 9.0, h)
    h, _ = group_hours(grp("O", "S"), OLD_MODEL, False, "fx")
    expect("a durations file without the measured fields falls back to sizes_hours",
           h == 13.1, h)
    try:
        group_hours(grp("X", "XS"), M, False, "fx")
        expect("an unmeasured size is refused", False, "no refusal")
    except PlanError as exc:
        expect("an unmeasured size is refused, naming the group and the size",
               "X: size 'XS'" in str(exc), str(exc))

    # 2. the held stage: priced by open carries, never by the original size.
    h, why = group_hours(grp("H1", "L", stage="carries-open", carry=["c"] * 8), M, False, "fx")
    expect("a held L with one open carry plans one part (20 h), not its L size", h == 20.0, why)
    h, why = group_hours(grp("H1", "L", stage="carries-open", carry=["c"] * 14), M, False, "fx")
    expect("six carries appended since measurement count open: 7 -> two parts (40 h)",
           h == 40.0, why)
    h, why = group_hours(grp("H0", "M", stage="carries-open", carry=["c"] * 3), M, False, "fx")
    expect("a held group with zero open carries plans zero (null control)", h == 0.0, why)

    caps1 = dict(DEFAULT_CAPS, slots=2, seats=8)
    start = dt.datetime(2026, 1, 5)
    ros = {"groups": [grp("H0", "M", stage="carries-open", carry=["c"] * 3),
                      grp("A"), grp("B")]}
    pl = build_plan(ros, M, caps1, start, "v1.0.0", round_n=2)
    g0 = pl["groups"]["H0"]
    expect("the zero-open held group starts and finishes at the replan instant",
           g0["start"] == g0["finish"] == iso(start, 0) and g0["duration_minutes"] == 0
           and "record step" in g0["start_reason"], str(g0))

    # 2b. a carry `roster_edit.py mark-carry` discharged is not open work
    # (carry 15): both carry counts read `roster_lib.pending_carries`.
    def marked(i):
        return f"c{i} [implemented: {i:040x}]"

    owed = (0, 1, 5, 6, 8, 9, 42, 43)
    body = [f"c{i}" if i in owed else marked(i) for i in range(44)]
    m11 = dict(M, carries_per_part=11.0, carry_part_hours=19.8)
    h, why = group_hours(grp("BC", "M", stage="carries-open", carry=body), m11, False, "fx")
    expect("R10-BODY-CONTRACT's shape: 8 unmarked of 44 plan one part (19.8 h), not four",
           abs(h - 19.8) < 1e-9 and "36 marked carries left out" in why, f"{h} {why}")
    two = ["c"] * 5 + [marked(i) for i in range(4)]
    h, why = group_hours(grp("T", "L", stage="carries-open", carry=two), M, False, "fx")
    expect("carries filling two parts, four marked and left out, plan one part (20 h)",
           h == 20.0 and "4 marked carries left out" in why, f"{h} {why}")
    h, why = group_hours(grp("T", "L", stage="carries-open", carry=["c"] * 9), M, False, "fx")
    expect("the same carries with none marked plan two parts as before (null control)",
           h == 40.0 and "left out" not in why, f"{h} {why}")
    h1 = ["c"] * 9 + [marked(9)] * 3 + ["c"] * 2
    h, why = group_hours(grp("H1", "L", stage="carries-open", carry=h1), M, False, "fx")
    expect("a measured held group counts only the unmarked carries appended since: 1 + 3 -> one part",
           h == 20.0 and "3 appended since" in why, f"{h} {why}")
    h, why = group_hours(grp("H1", "L", stage="carries-open", carry=[marked(0)] * 8), M, False, "fx")
    expect("a measured held group whose carries were all marked since plans zero, not one part",
           h == 0.0 and "0 open carries at measurement" in why, f"{h} {why}")
    h, why = group_hours(grp("H1", "L", stage="carries-open", carry=[marked(0)] * 8 + ["c"]),
                         M, False, "fx")
    expect("the measured open count never exceeds the carries then held still pending: 0 + 1",
           h == 20.0 and "0 open carries at measurement + 1 appended since" in why, f"{h} {why}")
    m5 = dict(M, held_open_carries={"H5": {"open": 5, "carries": 8}})
    h, why = group_hours(grp("H5", "L", stage="carries-open", carry=["c"] + [marked(0)] * 7),
                         m5, False, "fx")
    expect("five open at measurement, seven of the eight since marked: one open carry",
           h == 20.0 and why.startswith("1 open carries at measurement:"), f"{h} {why}")
    h, why = group_hours(grp("P", "S", carry=["x"] + [marked(0)] * 3),
                         dict(M, carry_baseline={}), False, "fx")
    expect("a size with no carry baseline prices every unmarked carry as absorbed: 18 + 4 h",
           h == 22.0 and "+ 1 absorbed carries, 3 marked carries left out" in why, f"{h} {why}")
    h, why = group_hours(grp("P", "S", carry=["x"] * 2 + [marked(0)] * 3), M, False, "fx")
    expect("marked carries are not absorbed work: 2 unmarked at the S baseline plan 18 h",
           h == 18.0 and "absorbed" not in why, f"{h} {why}")
    held = {"groups": [grp("H", "L", stage="carries-open", carry=["old"] * 5 + ["c"])]}
    pl = build_plan(held, M, dict(DEFAULT_CAPS), dt.datetime(2026, 1, 5), "v1.0.0",
                    round_n=2, legacy={"H": frozenset({"old"})})
    gh = pl["groups"]["H"]
    expect("a legacy carry (held while closed at the cut-over) is not open work: one part",
           gh["duration_minutes"] == 1200 and "5 marked carries left out" in gh["duration_basis"],
           str(gh))

    # 3. started work keeps its place: in flight from now, past the slot cap.
    many = {"groups": [grp(f"L{i}", stage="in-progress") for i in range(4)]
            + [grp("NEW"), grp("DEP", after=["NEW"], stage="in-progress")]}
    pm = build_plan(many, M, caps1, start, "v1.0.0", round_n=2)
    G = pm["groups"]
    expect("every started group with no open dependency starts now, past a cap of 2",
           all(G[f"L{i}"]["start"] == iso(start, 0) for i in range(4)),
           {n: G[n]["start"] for n in G})
    expect("a started group says why it starts: its fixer is working",
           G["L0"]["start_reason"] == "started: its fixer is working", G["L0"]["start_reason"])
    # NEW heads DEP's chain, so it is on the critical path: it starts at once
    # on an overflow slot, exempt from the cap (carry 8). A group off the path
    # still waits (the null control below).
    expect("a critical-path group starts past a full cap, flagged exempt",
           G["NEW"]["start"] == iso(start, 0) and G["NEW"].get("exempt") is True,
           G["NEW"])
    off = {"groups": many["groups"] + [grp("OFF")]}
    poff = build_plan(off, M, caps1, start, "v1.0.0", round_n=2)
    expect("null: a non-critical group in the same position still waits, and names it",
           poff["groups"]["OFF"]["start"] > iso(start, 0)
           and poff["groups"]["OFF"]["start_reason"].startswith("slot cap 2"),
           poff["groups"]["OFF"])
    expect("a started group waits only for its unmerged after-group, and names it",
           G["DEP"]["start"] == G["NEW"]["finish"]
           and G["DEP"]["start_reason"].startswith("started: its fixer is working; after NEW"),
           G["DEP"])
    expect("the plan with started groups past the cap passes --check", check_plan(pm) == [],
           check_plan(pm))
    bad = json.loads(json.dumps(pm))
    bad["groups"]["NEW"]["start"] = iso(start, 0)
    bad["groups"]["NEW"].pop("exempt", None)
    expect("a PLANNED dispatch into a full cap is still refused",
           any(b.startswith("in flight: NEW dispatched") for b in check_plan(bad)),
           check_plan(bad))
    nul = build_plan({"groups": [grp("TALL", "M"), grp("SHORT", "S")]}, M,
                     dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    expect("null control: two not-started ready groups are still ordered by priority",
           nul["groups"]["TALL"]["start"] < nul["groups"]["SHORT"]["start"],
           {n: nul["groups"][n]["start"] for n in nul["groups"]})

    # 4. the owner's priority order (2026-10-30).
    def tier_of(g, cp=False, sav=None):
        return dispatch_tier(g, cp, sav)[0]
    expect("main work is tier 1", tier_of(grp("R10-MAIN-FIX-X", kind="main")) == TIER_MAIN)
    expect("main outranks the top tier, even an outside main fix",
           tier_of(grp("R10-MAIN-FIX-X", kind="main", source="outside"), cp=True) == TIER_MAIN)
    expect("the critical path is the top tier", tier_of(grp("I", kind="instrument"), cp=True) == TIER_TOP)
    expect("an outside instrument is the top tier, off the critical path",
           tier_of(grp("I", kind="instrument", source="outside")) == TIER_TOP)
    expect("a user-reported bug (hotfix) is the hotfix tier, off the critical path",
           tier_of(grp("R10-HOTFIX-X", kind="bug")) == TIER_HOTFIX)
    # Owner rulings tvofi 2026-11-07 (triage P420) and 2026-11-08 (mandate
    # 6715477401): main, hotfix, then outside and the critical path as one
    # tier, then the rest in today's order.
    expect("a hotfix ranks ahead of an outside group, which shares a tier with the critical path",
           TIER_MAIN < tier_of(grp("R10-HOTFIX-X", kind="bug")) < tier_of(grp("OUT", source="outside"))
           == tier_of(grp("I", kind="instrument"), cp=True) < TIER_PRODUCTION_WORK,
           [tier_of(grp("R10-HOTFIX-X", kind="bug")), tier_of(grp("OUT", source="outside"))])
    expect("an outside group that is also a hotfix is a hotfix",
           tier_of(grp("R10-HOTFIX-O", kind="bug", source="outside")) == TIER_HOTFIX)
    # A HOTFIX name is a hotfix of any work class, the order roster_lib.dispatch_rank
    # gives every other reader (#3304 round 2: the base's production-only arm
    # ranked an instrument-class hotfix below outside in the plan alone).
    hx = build_plan({"groups": [grp("R10-HOTFIX-X", "S", "instrument"), grp("OUT", "S", source="outside")]},
                    M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    HX = hx["groups"]  # OUT, the critical path by name, starts beside it exempt
    expect("an instrument-class R10-HOTFIX group is the hotfix tier and holds the one real slot at t0 "
           "ahead of an outside group, the order dispatch_rank gives",
           tier_of(grp("R10-HOTFIX-X", kind="instrument")) == TIER_HOTFIX
           and HX["R10-HOTFIX-X"]["slot"] == 0 and HX["R10-HOTFIX-X"]["start"] == iso(start, 0)
           and not HX["R10-HOTFIX-X"].get("exempt") and HX["OUT"].get("exempt") is True
           and [roster_lib.dispatch_rank({"groups": [grp("R10-HOTFIX-X", "S", "instrument"),
                                                     grp("OUT", "S", source="outside")]}, n, set())
                for n in ("R10-HOTFIX-X", "OUT")] == [roster_lib.RANK_HOTFIX, roster_lib.RANK_TOP],
           {n: (HX[n]["start"], HX[n]["slot"], HX[n].get("exempt"), HX[n]["sort_key"][0]) for n in HX})
    expect("null control: the same instrument without a HOTFIX name stays the instrument tier",
           tier_of(grp("R10-FIX-X", kind="instrument")) == TIER_INSTRUMENT)
    expect("production work is the production tier", tier_of(grp("P")) == TIER_PRODUCTION_WORK)
    expect("a source other than outside is no top tier (null control)",
           tier_of(grp("P", source="audit")) == tier_of(grp("P")) == TIER_PRODUCTION_WORK)
    expect("an instrument saving 12 h is the production tier, one saving 11 h the instrument tier",
           tier_of(grp("I", kind="instrument"), sav=12) == TIER_PRODUCTION_WORK
           and tier_of(grp("I", kind="instrument"), sav=11) == TIER_INSTRUMENT)
    why = dispatch_tier(grp("I", kind="instrument"), False, None)[1]
    expect("an instrument with no recorded savings says so", "savings not recorded" in why, why)
    order = {"groups": [
        grp("CPA", "S", "instrument"), grp("CPB", "S", "instrument", after=["CPA"]),
        grp("CPC", "L", "instrument", after=["CPB"]),
        grp("R10-HOTFIX-H", "L", "bug"), grp("OUT", "S", source="outside"), grp("PROD", "M"),
        grp("HI", "S", "instrument", savings=9), grp("LO", "S", "instrument", savings=2),
        grp("NONE", "S", "instrument")]}
    po = build_plan(order, M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    # A ready critical-path group starts past a full cap (orchestrator.md
    # section 5), so the owner's order reads off the real slots: the capped
    # groups in start order, the critical path exempt beside them. OUT, an S
    # outside group, is shorter than every critical-path tail, so height
    # gives it the slot after the hotfix's.
    P = po["groups"]
    seq = sorted((n for n in P if not P[n].get("exempt")), key=lambda n: (P[n]["start"], n))
    expect("dispatch follows the owner's order (tvofi 2026-11-07, 2026-11-08): hotfix, then "
           "outside with the critical path, production, instruments by savings, unrecorded last",
           seq == ["R10-HOTFIX-H", "OUT", "PROD", "HI", "LO", "NONE"], seq)
    expect("the hotfix takes the free slot at t0 and the ready critical-path group starts "
           "beside it past the cap, never ahead of it on the real slot",
           P["R10-HOTFIX-H"]["start"] == iso(start, 0) and P["R10-HOTFIX-H"]["slot"] == 0
           and P["CPA"]["start"] == iso(start, 0) and P["CPA"].get("exempt") is True
           and all(P[n].get("exempt") is True for n in ("CPA", "CPB", "CPC")),
           {n: (P[n]["start"], P[n]["slot"], P[n].get("exempt")) for n in P})
    keys = {n: po["groups"][n]["sort_key"] for n in po["groups"]}
    expect("each group's sort_key is in the plan and orders it the same way",
           sorted(keys, key=lambda n: [float("inf") if k is None else k for k in keys[n]])[0] == "R10-HOTFIX-H"
           and all(po["groups"][n]["tier_reason"] for n in keys), keys)
    # A critical-path tail (B, 18 h left) against a taller hotfix (H, 24 h):
    # the hotfix outranks the critical path, so H takes the one free slot at
    # once, and A, the path's head, still starts with it, exempt from the cap.
    tail = build_plan({"groups": [grp("A", "L", "instrument"),
                                  grp("B", "S", "instrument", after=["A"]),
                                  grp("H", "M", "bug")]}, M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    T = tail["groups"]
    expect("a hotfix outranks the critical path, which still starts past the cap",
           tail["critical_path"] == ["A", "B"] and T["H"]["sort_key"] < T["A"]["sort_key"]
           and T["H"]["start"] == T["A"]["start"] == iso(start, 0)
           and T["A"].get("exempt") is True and not T["H"].get("exempt"),
           {n: (T[n]["start"], T[n]["sort_key"], T[n].get("exempt")) for n in T})
    # The owner's top tier (tvofi 2026-11-07, 2026-11-08): an accepted outside
    # request ranks with the critical path, unordered among them, ahead of a
    # production group that is taller than it. The outside group (S) is
    # shorter than PRODX (M) and on no critical path (CPX, L, is the path);
    # PRODY is the same production group with no outside source: tier 4.
    out = build_plan({"groups": [grp("CPX", "L"), grp("PRODX", "M"),
                                 grp("OUTX", "S", source="outside"), grp("PRODY", "S")]},
                     M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    O = out["groups"]
    expect("an outside request is the top tier off the critical path, and dispatches "
           "before a taller production group",
           out["critical_path"] == ["CPX"] and O["OUTX"]["tier"] == TIER_TOP
           and "outside request" in O["OUTX"]["tier_reason"]
           and O["OUTX"]["start"] < O["PRODX"]["start"],
           {n: (O[n]["tier"], O[n]["start"], O[n]["tier_reason"]) for n in O})
    expect("null control: the same production group with no outside source stays below",
           O["PRODY"]["tier"] == TIER_PRODUCTION_WORK and "outside" not in O["PRODY"]["tier_reason"]
           and O["PRODX"]["start"] < O["PRODY"]["start"],
           {n: (O[n]["tier"], O[n]["start"]) for n in O})
    # Unordered within the top tier: height decides between an outside group
    # and the critical path. CPA -> CPB is the path; once CPA merges, OUTT
    # (M) is taller than the path's tail CPB (S), so OUTT takes the one free
    # slot and CPB still starts at the same instant, past the cap.
    unord = build_plan({"groups": [grp("CPA", "L"), grp("CPB", "S", after=["CPA"]),
                                   grp("OUTT", "M", source="outside")]},
                       M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    U = unord["groups"]
    expect("within the top tier height orders an outside group and the critical path, "
           "and the critical path is still exempt from the cap",
           unord["critical_path"] == ["CPA", "CPB"]
           and U["OUTT"]["tier"] == U["CPB"]["tier"] == TIER_TOP
           and U["OUTT"]["sort_key"] < U["CPB"]["sort_key"]
           and U["OUTT"]["start"] == U["CPB"]["start"] and U["CPB"].get("exempt") is True
           and not U["OUTT"].get("exempt"),
           {n: (U[n]["sort_key"], U[n]["start"], U[n].get("exempt")) for n in U})
    tie = build_plan({"groups": [grp("A1", "M"), grp("A2", "S")]}, M,
                     dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    expect("null control: two groups in one tier keep the height tie-break",
           tie["groups"]["A1"]["start"] < tie["groups"]["A2"]["start"],
           {n: tie["groups"][n]["sort_key"] for n in tie["groups"]})

    # 5. caps: a call naming none draws at the owner's, and says so.
    nocaps = cli_caps(parse_args([]))
    expect("a replan given no caps does not draw a 6-slot plan: the owner's 20, with provenance",
           nocaps["slots"] == 20 and nocaps["seats"] == 20
           and nocaps["provenance"] == CAPS_PROVENANCE, nocaps)
    given = cli_caps(parse_args(["--slots", "4"]))
    expect("null control: a cap given on the command line is used and named as given",
           given["slots"] == 4 and given["provenance"].startswith("--slots given"), given)
    pc = build_plan({"groups": [grp("A")]}, M, nocaps, start, "v1.0.0", round_n=2)
    expect("the plan records whose caps it drew at",
           pc["generated"]["caps"]["provenance"] == CAPS_PROVENANCE, pc["generated"]["caps"])

    print(f"model self-test: {len(fails)} failed")
    return 1 if fails else 0


# ------------------------------------------------------------------- schedule

WORK_REF_PREFIXES = ("fixer/", "handoff/", "handoff-wip/", "dispatch/")
DESIGN_REF_PREFIX = "design/"


def parse_live_refs(text: str) -> set:
    """Branch names from a saved `git ls-remote` listing (sha, tab, ref)."""
    out = set()
    for line in text.splitlines():
        ref = line.split()[-1] if line.split() else ""
        if ref.startswith("refs/heads/"):
            out.add(ref[len("refs/heads/"):])
    return out


def topics_of(group: dict) -> set:
    t = {group["group"].lower()}
    branch = (group.get("resume") or {}).get("branch") or ""
    if branch:
        t.add(branch.rsplit("/", 1)[-1])
    return t


def topic_evidence(group: dict, evidence: dict) -> str | None:
    """'pr' (an open pull request), 'work' (a fixer, handoff or dispatch ref),
    'design' (a design ref and nothing built), or None, from the offline
    listing and the in-flight file."""
    topics = topics_of(group)
    for pr in evidence.get("prs") or []:
        head = str(pr.get("headRefName") or "")
        if head.rsplit("/", 1)[-1] in topics:
            return "pr"
    refs = evidence.get("refs") or set()
    if any(p + t in refs for p in WORK_REF_PREFIXES for t in topics):
        return "work"
    if any(DESIGN_REF_PREFIX + t in refs for t in topics):
        return "design"
    return None


def substantive(diff: str) -> bool:
    """True when a unified diff changes a line that is neither blank nor a
    `#` comment: a comment-only or whitespace-only change ships no behaviour."""
    for line in diff.splitlines():
        if line[:1] in "+-" and not line.startswith(("+++", "---")):
            body = line[1:].strip()
            if body and not body.startswith("#"):
                return True
    return False


MERGE_BRANCH_RE = re.compile(r"^Merge pull request #\d+ from \S+/(\S+)\s*$")


def merge_topic(subject: str) -> str | None:
    """The topic of a "Merge pull request #N from <owner>/<type>/<topic>"
    subject: the last path segment of the merged branch, lower-cased."""
    m = MERGE_BRANCH_RE.match(subject)
    return m.group(1).rsplit("/", 1)[-1].lower() if m else None


def production_groups_since(commits: list, G: dict) -> list:
    """Production groups with a substantive `custom_components` change since
    the last tag, once each however many pull requests they took.
    `commits`: [{"subject": str, "diff": the change against the first parent
    of custom_components}]. A group is named by a merge's topic branch, as
    `topic_evidence` matches one (main's merges read "Merge pull request #N
    from tvofi/fix/<topic>"; a part branch `<topic>-p2` extends its group's
    topic at a `-` boundary), else by the longest roster group name in the
    subject (a squash)."""
    by_topic = {t: n for n in G for t in topics_of(G[n])}
    out: dict = {}
    for c in commits:
        topic = merge_topic(c["subject"])
        n = None
        if topic:
            # a part branch (`<topic>-p2`) belongs to the longest roster topic it
            # equals or extends at a `-` boundary
            hit = [t for t in by_topic if topic == t or topic.startswith(t + "-")]
            n = by_topic[max(hit, key=len)] if hit else None
        if n is None:
            named = [g for g in G if g in c["subject"]]
            n = max(named, key=len) if named else None
        if n and roster_lane(G[n]) in PRODUCTION and substantive(c.get("diff") or ""):
            out[n] = True
    return list(out)


def git_commits_since_tag(repo: str) -> list:
    """The `production_groups_since` input from git: first-parent commits
    since the last tag, each with its custom_components diff against its
    FIRST PARENT (`git show` prints a merge's combined diff, empty for a
    clean merge)."""
    tag = _git(repo, "describe", "--tags", "--abbrev=0")
    if tag.returncode != 0:
        raise PlanError("--since-tag: the repository has no tag")
    log = _git(repo, "log", "--first-parent", "--format=%H%x1f%s", f"{tag.stdout.strip()}..HEAD")
    out = []
    for line in log.stdout.splitlines():
        sha, _, subject = line.partition("\x1f")
        diff = _git(repo, "diff", "-U0", f"{sha}^1", sha, "--", "custom_components").stdout
        out.append({"subject": subject, "diff": diff})
    return out


def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
               version: str, roster_ref: str = "", roster_blob: str = "",
               roster_path: str = "", *, round_n: int, since_tag: list | None = None,
               evidence: dict | None = None, legacy: dict | None = None) -> dict:
    closing, why = closure_version(version, round_n)
    if why:
        raise PlanError(f"the round-close stamp: {why}")
    G = groups_of(roster)
    deps, open_, done = dependency_graph(G, legacy)
    discharged = {n for n in done if not is_done(G[n])}
    # A group `after` a deferred one stays held behind it, unscheduled. A
    # discharged group is closed work here as in `dependency_graph`: it is
    # neither held nor holds, so it is left out of the view the hold reads.
    live = {n: g for n, g in G.items() if n not in discharged}
    held = roster_lib.held_behind_deferred(live)
    open_ = open_ - set(held)
    # Groups after the round's closing stamp are scheduled after it and are
    # neither inside closure nor in any stamp's carries (carries 10, 11).
    post = roster_lib.post_closure_groups(G, open_)
    open_all = open_
    open_ = open_all - post
    deps_post = {n: deps[n] for n in post}
    deps = {n: deps[n] for n in open_}
    order = topo_order(deps)
    children = children_of(deps)
    size_hours = durations["sizes_hours"]
    live_fraction = float(durations.get("live_remaining_fraction", 0.7))
    batch_window = int(durations.get("batch_window_minutes", 20))
    stamp_lead = int(durations.get("stamp_lead_minutes", 60))
    closure_lead = int(durations.get("closure_lead_minutes", 120))

    lane = {n: roster_lane(G[n]) for n in G}
    coord = {n: touches_coordinator(G[n]) for n in open_}
    live = {n for n in open_ if (G[n].get("resume") or {}).get("stage") in LIVE_STAGES}
    design_only: set = set()
    demoted: set = set()
    if evidence is not None:
        # Liveness by evidence, not by the stage word (carries 0, 3): an open
        # pull request is live (credit); a design ref with no build starts at
        # t=0 without credit; a stage-word live group with neither a work ref
        # nor a pull request is pending. Offline: the listing is a saved file.
        ev_live, ev_design = set(), set()
        for n in open_:
            if topic_evidence(G[n], evidence) == "pr":
                ev_live.add(n)
            elif topic_evidence(G[n], evidence) == "design":
                ev_design.add(n)
        demoted = {n for n in live if topic_evidence(G[n], evidence) is None}
        # A stage-word live group whose only evidence is a design ref has
        # built nothing: it is design-only, uncredited (carry 3).
        live = (live - demoted - ev_design) | ev_live
        design_only = ev_design - live
    dur_h, basis = {}, {}
    for n in open_:
        dur_h[n], basis[n] = group_hours(G[n], durations, n in live,
                                         roster_path or roster_ref or "<fixture>", legacy)
    # A held group with nothing left owes only its record step: it is
    # started at the replan instant like a working one and holds no slot wait.
    settled = {n for n in open_ if n not in live and dur_h[n] == 0}
    dur_min = {n: 0 if n in settled else max(1, int(round(dur_h[n] * 60))) for n in open_}
    height = heights(deps, dur_h, order)
    lvl = levels(deps, order)

    # The owner's dispatch priority, derived from this replan's graph. `crit`
    # is `critical_path()`'s output, never a stored list. `savings` is a
    # roster field; a value that is not a number is refused rather than
    # silently treated as absent.
    cp = critical_path(deps, dur_h, order)
    crit = set(cp)
    savings: dict = {}
    for n in open_:
        s = G[n].get("savings")
        if s is None:
            continue
        if isinstance(s, bool) or not isinstance(s, (int, float)):
            raise PlanError(f"{n}: savings is not a number: {s!r}")
        savings[n] = float(s)
    tier, tier_why = {}, {}
    for n in open_:
        tier[n], tier_why[n] = dispatch_tier(G[n], n in crit, savings.get(n))

    def priority(n: str):
        return dispatch_key(n, tier, savings, height, dur_min)

    slots = int(caps["slots"])
    seats = int(caps["seats"])
    coord_cap = int(caps["coordinator_cap"])
    every = int(caps["stamp_every"])

    slot_of = {n: None for n in open_}
    start_t: dict = {}
    merged_t: dict = {}
    work_end: dict = {}
    running: dict = {}          # n -> (slot, work_end)
    finished: dict = {}         # n -> work_end, waiting for its batch
    inherited = set()           # started groups in flight at the replan instant
    # A started group -- a working fixer, or a held group with nothing left
    # but its record step -- already holds its pull request: it starts the
    # moment its `after` groups have merged, past the slot and coordinator
    # caps (which bind new dispatches), and is never queued behind them.
    started = live | settled | design_only
    released = {n: 0 for n in open_ if not deps[n]}   # n -> when it became ready
    coord_held: set = set()     # ready groups the coordinator cap passed over
    ready = {n for n in open_ if not deps[n]}
    pending = set(open_)
    batch_rows: list = []
    stamps: list = []
    # Production groups already merged since the last tag count toward the
    # next patch stamp, once each however many pull requests they took.
    # Only a DONE group is credit: one still open merges inside this plan and
    # is counted there, so crediting it too would count it twice (carry 9).
    credit = [n for n in dict.fromkeys(since_tag or [])
              if n in G and lane[n] in PRODUCTION and n in done]
    carry: list = list(credit)
    stamp_by_group: dict = {}
    patch = 0
    overflow_base = slots + 100
    exempt: set = set()         # critical-path groups started past the slots cap
    exempt_coord: set = set()   # ... or past the coordinator cap

    def free_slot() -> int | None:
        # A slot is held from the start to the merge, not to the end of the
        # work: a finished group waiting for its batch still has its PR open.
        used = ({s for s, _ in running.values()} | {slot_of[n] for n in finished})
        used = {s for s in used if s < overflow_base}
        if len(used) >= slots:
            return None
        return next((s for s in range(slots) if s not in used), None)

    def held_slot() -> int:
        # A started group's slot: the lowest free index, past the cap if the
        # started set alone exceeds it.
        used = ({s for s, _ in running.values()} | {slot_of[n] for n in finished})
        used = {s for s in used if s < overflow_base}
        return next(s for s in range(len(used) + 1) if s not in used)

    def in_flight_coord() -> int:
        return sum(1 for n in list(running) + list(finished) if coord[n])

    def pick(candidates, now: int, cap_exempt: bool = False):
        """The owner's dispatch priority; coordinator cap on planned starts,
        which a critical-path candidate (`cap_exempt`) is not held by."""
        cc = in_flight_coord()
        best = None
        for n in candidates:
            if coord[n] and n not in started and cc >= coord_cap and not cap_exempt:
                coord_held.add(n)
                continue
            key = priority(n)
            if best is None or key < best[0]:
                best = (key, n)
        return None if best is None else best[1]

    t = 0
    guard = 0
    while pending or running or finished or ready:
        guard += 1
        if guard > 20000:
            raise PlanError("scheduler did not terminate; the graph is unsound")

        # 1. Every started group whose `after` groups have merged starts now,
        #    in the priority order, holding a slot past the cap if it must. At
        #    the replan instant that is every working fixer with no open
        #    dependency; one waiting on a dependency starts when it merges --
        #    the only reason a started group is deferred.
        for n in sorted((n for n in ready if n in started), key=priority):
            s = held_slot()
            start_t[n] = t
            slot_of[n] = s
            work_end[n] = t + (0 if n in settled else dur_min[n])
            running[n] = (s, work_end[n])
            if t == 0:
                inherited.add(n)
            ready.discard(n)
            pending.discard(n)
        # The real slots go in the dispatch order over every ready group, so a
        # tier above the critical path (main, hotfix) takes a free slot ahead
        # of it, and an outside group, which shares the critical path's top
        # tier unordered (tvofi 2026-11-08), wins one by height.
        while ready and free_slot() is not None:
            n = pick(sorted(ready), t)
            if n is None:
                break
            s = free_slot()
            start_t[n] = t
            slot_of[n] = s
            work_end[n] = t + dur_min[n]
            running[n] = (s, work_end[n])
            ready.discard(n)
            pending.discard(n)
        # A ready critical-path group the slots left waiting starts now
        # whatever the cap, as dispatch does (orchestrator.md section 5), on an
        # overflow slot (a free one only when the coordinator cap held the
        # pick above), and is exempt from the cap.
        while True:
            n = pick(sorted(x for x in ready if x in crit), t, cap_exempt=True)
            if n is None:
                break
            if coord[n] and in_flight_coord() >= coord_cap:
                exempt_coord.add(n)
            s = free_slot()
            if s is None:
                s = overflow_base + len(start_t)
                exempt.add(n)
            start_t[n] = t
            slot_of[n] = s
            work_end[n] = t + dur_min[n]
            running[n] = (s, work_end[n])
            ready.discard(n)
            pending.discard(n)

        if not running and not finished:
            break

        # 2. Advance to the next event: a finish, or the end of a batch window.
        events = [we for _, we in running.values()]
        if finished:
            events.append(min(finished.values()) + batch_window)
        t = max(t, min(events))

        # 3. Move finished work into the merge pool.
        for n in [n for n, (_, we) in running.items() if we <= t]:
            del running[n]
            finished[n] = work_end[n]

        # 4. Close the batch when its window has elapsed, when a group is
        #    waiting for a slot it would free, or when nothing else can happen.
        #    Only the first of those costs wall time; a batch that is held
        #    while every slot is busy with work and no ready group waits is
        #    sharing a gate run for free. Slots free and dependents release at
        #    this instant.
        waiting = bool(ready) and (free_slot() is None or pick(sorted(ready), t) is None)
        if finished and (waiting or t >= min(finished.values()) + batch_window
                         or (not running and not ready and not pending)):
            batch = sorted(finished, key=lambda n: (work_end[n], n))
            for n in batch:
                merged_t[n] = t
                finished.pop(n)
            bid = len(batch_rows) + 1
            batch_rows.append({"id": bid, "at": t, "groups": batch})
            # carries are recorded in the order `check_plan` reads merges:
            # by merge instant, then name -- a batch's members share the
            # instant, so their order inside it is the name order
            for n in sorted(batch):
                if lane[n] in PRODUCTION:
                    carry.append(n)
                    while len(carry) >= every:
                        patch += 1
                        v = bump(version, patch)
                        cut, carry = carry[:every], carry[every:]
                        stamps.append({"version": v, "at": t + stamp_lead,
                                       "carries": cut, "kind": "patch",
                                       "batch": bid})
                        for c in cut:
                            stamp_by_group[c] = v
            for n in batch:
                for c in children[n]:
                    # THE invariant that keeps a started group out of `ready`:
                    # an inherited fixer admitted ahead of its dependency must
                    # not be released a second time when that dependency later
                    # merges (it would start, stamp and merge twice).
                    if c not in start_t and all(a in merged_t for a in deps[c]):
                        ready.add(c)
                        released.setdefault(c, t)

    if pending or ready or running or finished:
        raise PlanError(f"scheduled {len(merged_t)} of {len(open_)} open groups")

    closure = max(merged_t.values(), default=0)
    # The last fewer-than-`every` production groups are not a patch stamp of
    # their own: the round-close stamp closes the programme and carries them.
    # A second push there would pay a gate run to bump a version the round's
    # major replaces hours later.
    for c in carry:
        stamp_by_group[c] = closing
    stamps.append({"version": closing, "at": closure + closure_lead,
                   "carries": list(carry), "kind": ROUND_CLOSE, "batch": None})

    # Post-closure groups (owner steps after the closing stamp, and what
    # follows them) start once the stamp is cut and every dependency has
    # finished; they hold no slot, join no batch and are in no stamp.
    post_dur = {}
    for n in post:
        h, _ = group_hours(G[n], durations, False, roster_path or roster_ref or "<fixture>")
        post_dur[n] = max(1, int(round(h * 60)))
    post_start: dict = {}
    post_end: dict = {}
    for n in topo_order({n: [a for a in deps_post[n] if a in post] for n in post}):
        ready_at = max([stamps[-1]["at"]] + [post_end[a] for a in deps_post[n] if a in post_end]
                       + [merged_t[a] for a in deps_post[n] if a in merged_t])
        post_start[n] = ready_at
        post_end[n] = ready_at + post_dur[n]

    # The programme closes at the LATER of the round-close stamp and the last
    # post-closure step (the catalog PR): tvofi 2026-11-07, "not considered
    # closed until both v.10.0.0 and the catalog PR has landed".
    closure_at = max([stamps[-1]["at"]] + list(post_end.values()))

    # a wave is the set of groups the replan dispatches at one instant
    by_open: dict = {}
    for n in open_:
        by_open.setdefault(start_t[n], []).append(n)
    batch_of = {n: b["id"] for b in batch_rows for n in b["groups"]}
    waves = []
    for i, t0 in enumerate(sorted(by_open), start=1):
        gs = sorted(by_open[t0])
        bids = sorted({batch_of[g] for g in gs})
        stamped = next((s["version"] for s in stamps if s.get("batch") in bids), None)
        waves.append({
            "wave": i,
            "opens": iso(start, t0),
            "drains": iso(start, max(merged_t[g] for g in gs)),
            "stamp": stamped,
            "batch": bids,
            "groups": gs,
        })

    inflow = float(durations.get("inflow_groups_per_hour") or 0)
    gate = gate_minutes(durations)
    # The published gate is rounded; the CI minutes are the product of the
    # published pair, so a reader who multiplies the summary's own numbers
    # gets the summary's own total (a self-test arm recomputes exactly this).
    gate_report = round(gate, 1)
    ci = round((len(batch_rows) + len(stamps)) * gate_report, 1)

    def start_reason(n: str) -> str:
        """Why the group starts when it does, in the plan's own terms."""
        last = max(deps[n], key=lambda a: (merged_t[a], a)) if deps[n] else None
        if n in settled:
            head = "held, no open carry: owes only its record step"
        elif n in started:
            head = "started: its fixer is working"
        else:
            head = None
        if start_t[n] == released.get(n, 0):
            if last is not None:
                return f"{head + '; ' if head else ''}after {last} (merges {iso(start, merged_t[last])})"
            return head or "dispatched at the replan instant (priority)"
        if n in coord_held:
            return f"coordinator cap {coord_cap}: waited for a coordinator slot"
        return f"slot cap {slots}: waited behind higher-priority groups"

    def plain(key: tuple) -> list:
        return [None if isinstance(k, float) and math.isinf(k) else k for k in key]

    groups_out = {}
    absorbed_by = absorbers(G)
    for n in sorted(G):
        if n in post:
            groups_out[n] = {
                "wave": None, "start": iso(start, post_start[n]),
                "finish": iso(start, post_end[n]), "slot": None,
                "duration_minutes": post_dur[n], "size": G[n].get("size"),
                "lane": lane[n], "tier": None, "level": None, "live": False,
                "inherited": False, "started": False,
                "start_reason": "post-closure: after the round-close stamp",
                "coordinator": touches_coordinator(G[n]), "batch": None,
                "stamp": None, "after": sorted(deps_post[n]), "done": False,
                "post_closure": True,
            }
            continue
        if n in held:
            groups_out[n] = {
                "wave": None, "start": None, "finish": None, "slot": None,
                "duration_minutes": 0, "size": G[n].get("size"), "lane": lane[n],
                "tier": None, "level": None, "live": False, "inherited": False,
                "coordinator": touches_coordinator(G[n]), "batch": None,
                "stamp": None, "after": [], "done": True,
                "held_behind": held[n],
            }
            continue
        if n in done:
            groups_out[n] = {
                "wave": None, "start": None, "finish": None, "slot": None,
                "duration_minutes": 0, "size": G[n].get("size"), "lane": lane[n],
                # A done group is not dispatched, so it carries no tier.
                "tier": None,
                "level": None, "live": False, "inherited": False,
                "coordinator": touches_coordinator(G[n]), "batch": None,
                "stamp": None, "after": [], "done": True,
                **({"discharged": True} if n in discharged else {}),
            }
            if n in absorbed_by:
                groups_out[n]["absorbed_into"] = absorbed_by[n][0]
            continue
        groups_out[n] = {
            "wave": next(w["wave"] for w in waves if n in w["groups"]),
            "start": iso(start, start_t[n]),
            "finish": iso(start, merged_t[n]),
            "slot": slot_of[n],
            "duration_minutes": dur_min[n],
            "size": G[n].get("size"),
            "lane": lane[n],
            "tier": tier[n],
            "level": lvl[n],
            "live": n in live,
            "inherited": n in inherited,
            "started": n in started,
            "start_reason": start_reason(n),
            "tier_reason": tier_why[n],
            "sort_key": plain(priority(n)),
            "duration_basis": basis[n],
            "coordinator": coord[n],
            "batch": batch_of[n],
            "stamp": stamp_by_group.get(n),
            "after": sorted(deps[n]),
            "done": False,
        }
        if n in exempt:
            groups_out[n]["exempt"] = True
        if n in exempt_coord:
            groups_out[n]["exempt_coordinator"] = True
        if n in design_only:
            groups_out[n]["design_only"] = True

    arrivals = None
    if inflow > 0:
        # Expected arrivals over the plan's wall time, priced at the median
        # size: reported, not scheduled -- they are not groups yet.
        sz = sorted(float(v) for v in size_hours.values())
        n_exp = inflow * closure_at / 60.0
        arrivals = {"groups": round(n_exp, 2),
                    "work_hours": round(n_exp * sz[len(sz) // 2], 2)}
    peak_flight, peak_coord = peak_concurrency(groups_out, start)
    peak_working = peak_seats(groups_out, start)
    inherited_deps = [
        {"group": n, "after": g, "dependent_start": iso(start, start_t[n]),
         "dependency_finish": iso(start, merged_t[g])}
        for n in sorted(inherited) for g in deps[n]
        if merged_t[g] > start_t[n]
    ]
    inherited_coord = sorted(n for n in inherited if coord[n])
    # The binding chain: from the closing group, back through each group's
    # last-finishing predecessor in the SCHEDULE. It differs from the
    # unconstrained critical path whenever slots bind; the gap is its slack.
    chain = []
    if merged_t:
        node = max(merged_t, key=lambda n: (merged_t[n], n))
        while node is not None:
            chain.append(node)
            node = (max(deps[node], key=lambda a: (merged_t[a], a)) if deps[node] else None)
        chain.reverse()
    cp_hours = height[cp[0]] if cp else 0.0
    binding = {
        "chain": chain,
        "links": [{"group": n, "start": iso(start, start_t[n]),
                   "finish": iso(start, merged_t[n])} for n in chain],
        "critical_path_hours": round(cp_hours, 2),
        "critical_path_slack_hours": round(closure / 60.0 - cp_hours, 2),
        "slot_sensitivity": "uncalibrated: 7-day roster history (27 snapshots 6 h "
                            "apart) gave r=0.045 between live groups and completions 12 h later",
    }
    plan = {
        "schema": 1,
        "generated": {
            "stamp_credit": credit,
            "liveness": ("evidence" if evidence is not None else "stage word"),
            "demoted_live": sorted(demoted),
            "roster_ref": roster_ref,
            "roster_blob": roster_blob,
            "start": iso(start, 0),
            "version": version,
            "round": round_n,
            "durations": durations.get("provenance") or {},
            # The duration model this plan was computed with, so a reader of
            # the plan states the figures it used rather than today's file's.
            "model": {
                "sizes_hours": dict(size_hours),
                "live_remaining_fraction": live_fraction,
                "sizes_provenance": durations.get("sizes_provenance") or "",
                **{k: durations[k] for k in MODEL_FIELDS if k in durations},
            },
            "caps": {
                "slots": slots, "seats": seats, "coordinator_cap": coord_cap,
                "stamp_every": every, "batch_window_minutes": batch_window,
                "provenance": caps.get("provenance") or "passed by the caller",
            },
            # The inherited in-progress set, recorded so the coordinator cap's
            # state at t=0 is a fact in the plan rather than a claim in prose.
            # `--check` refuses a plan whose record is missing or disagrees.
            "inherited_coordinator": {
                "cap": coord_cap,
                "groups": inherited_coord,
                "exceeds_cap": len(inherited_coord) > coord_cap,
            },
            "inherited_dependency_violations": inherited_deps,
        },
        "summary": {
            "closure": iso(start, closure_at),
            "closure_stamp": stamps[-1]["version"],
            "closure_conditions": list(CLOSURE_CONDITIONS),
            "wall_hours": round(closure_at / 60.0, 2),
            "ci_minutes": ci,
            "gate_minutes": gate_report,
            "batches": len(batch_rows),
            "stamps": len(stamps),
            "groups_total": len(G),
            "groups_done": len(done),
            "groups_discharged": len(discharged),
            "groups_open": len(open_all),
            "post_closure": sorted(post),
            "post_closure_finish": (iso(start, max(post_end.values())) if post_end else None),
            "production_since_tag": len(credit),
            "exempt_started": len(exempt),
            **({"expected_arrivals": arrivals} if arrivals else {}),
            "inherited_in_progress": len(inherited),
            "inherited_coordinator": sum(1 for n in inherited if coord[n]),
            "peak_in_flight": peak_flight,
            "peak_working": peak_working,
            "peak_coordinator_in_flight": peak_coord,
        },
        "critical_path": cp,
        "binding": binding,
        "absorbed": {n: {"into": a, "advisory": adv} for n, (a, adv) in absorbed_by.items()},
        "groups": groups_out,
        "waves": waves,
        "batches": [{"id": b["id"], "at": iso(start, b["at"]), "groups": b["groups"]}
                    for b in batch_rows],
        "stamps": [{"version": s["version"], "at": iso(start, s["at"]),
                    "carries": s["carries"], "kind": s["kind"],
                    "batch": s["batch"]} for s in stamps],
    }
    return plan


def bump(version: str, n: int) -> str:
    """The `n`th interim patch stamp after `version`."""
    maj, mi, pa = (int(x) for x in version.lstrip("v").split(".")[:3])
    return f"v{maj}.{mi}.{pa + n}"


def closure_version(version: str, round_n) -> tuple[str | None, str | None]:
    """`(vN.0.0, None)` for the stamp closing round `round_n`, or `(None, why)`.

    The rule is `stamp.next_version`'s, the one `stamp.py --round-close N`
    runs, given the round as both the asked and the roster's round: the plan
    states the version that command will assign, and refuses where it would.
    """
    if isinstance(round_n, bool) or not isinstance(round_n, int):
        return None, f"no round to close (round {round_n!r})"
    nxt, why = stamp.next_version(version.lstrip("v"), None, round_n, round_n)
    return (f"v{nxt}", None) if nxt else (None, why)


def gate_minutes(durations: dict) -> float:
    """One gate run's machine minutes, with the cancelled-leg risk priced in.

    `Analyze (python)` was cancelled at its 30-minute cap in the sample; a
    cancelled leg is run again, so its expected cost is one more leg, weighted
    by the measured cancellation rate. `fast` and `closures` do not cancel in
    the sample and are taken at their medians.
    """
    ci = durations["ci"]
    fast = float(ci["fast (3.14)"]["median_minutes"])
    clo = float(ci["closures"]["median_minutes"])
    ana = float(ci["Analyze (python)"]["median_minutes"])
    p_cancel = float(ci["Analyze (python)"].get("cancelled_rate", 0.0))
    return fast + clo + ana * (1.0 + p_cancel)


def _sweep(groups_out: dict, start: dt.datetime, coord_only: bool = False,
           durations_only: bool = False, planned_only: bool = False) -> int:
    """Peak concurrent groups: (start, +1), (end, -1), -1 ordered first.

    `durations_only` ends a group at start+duration (the fixer working);
    otherwise at its merge (the pull request open), which is what the slot
    and coordinator caps count. `planned_only` leaves out the groups already
    in progress when the replan ran: their state predates the plan.
    """
    def mins(s: str) -> int:
        return int((dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") - start).total_seconds() // 60)

    events = []
    for g in groups_out.values():
        if g.get("done") or g.get("post_closure"):
            continue
        if coord_only and not g.get("coordinator"):
            continue
        if planned_only and g.get("started"):
            continue
        begin = mins(g["start"])
        end = begin + g["duration_minutes"] if durations_only else mins(g["finish"])
        events.append((begin, 1))
        events.append((end, -1))
    events.sort(key=lambda e: (e[0], e[1]))
    cur = peak = 0
    for _, delta in events:
        cur += delta
        peak = max(peak, cur)
    return peak


def peak_concurrency(groups_out: dict, start: dt.datetime) -> tuple[int, int]:
    """(peak in flight, peak coordinator-touching in flight the plan created)."""
    return (_sweep(groups_out, start),
            _sweep(groups_out, start, coord_only=True, planned_only=True))


def peak_seats(groups_out: dict, start: dt.datetime) -> int:
    """Peak groups working (start to start+duration), independent of merge wait."""
    return _sweep(groups_out, start, durations_only=True)


def iso(start: dt.datetime, minutes: int) -> str:
    return (start + dt.timedelta(minutes=int(round(minutes)))).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------- check

def check_plan(plan: dict) -> list:
    """Every constraint the brief names, refused rather than warned.

    Returns a list of human-readable violations; empty means the plan holds.
    """
    bad: list = []
    caps = plan["generated"]["caps"]
    slots = caps["slots"]
    seats = caps["seats"]
    coord_cap = caps["coordinator_cap"]
    every = caps["stamp_every"]
    groups = {n: g for n, g in plan["groups"].items() if not g.get("done")}
    # What the caps count: not the critical-path groups started past the
    # slots cap (exempt by rule, never filtered out of the report), and not
    # post-closure owner steps, which hold no slot.
    counted = {n: g for n, g in groups.items()
               if not g.get("exempt") and not g.get("post_closure")}
    in_round = {n: g for n, g in groups.items() if not g.get("post_closure")}
    start = dt.datetime.strptime(plan["generated"]["start"], "%Y-%m-%dT%H:%M:%SZ")

    def mins(s: str) -> int:
        return int((dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") - start).total_seconds() // 60)

    # 1. dependency: a dependency finishes before its dependent starts. An
    #    inherited (already running) dependent is recorded, not refused, and
    #    the record must equal the state -- an unrecorded inversion is refused.
    inherited_deps = set()
    for n, g in groups.items():
        for a in g.get("after") or []:
            if a not in groups or mins(groups[a]["finish"]) <= mins(g["start"]):
                continue
            if g.get("inherited"):
                inherited_deps.add((n, a))
            else:
                bad.append(f"dependency: {a} finishes {groups[a]['finish']} "
                           f"after {n} starts {g['start']}")
    recorded_deps = {(d["group"], d["after"]) for d in
                     plan["generated"].get("inherited_dependency_violations") or []}
    if recorded_deps != inherited_deps:
        bad.append("dependency: generated.inherited_dependency_violations "
                   f"{sorted(recorded_deps)} does not equal the inherited "
                   f"inversions {sorted(inherited_deps)}")

    # 2. six in flight at any instant (open pull requests), and eight working
    events = []
    for n, g in groups.items():
        events.append((mins(g["start"]), 1, n))
        events.append((mins(g["finish"]), -1, n))
    events.sort(key=lambda e: (e[0], e[1]))
    # The caps bind what the plan DISPATCHES: a started group (a working
    # fixer, its PR already open) is never refused for the state it inherited,
    # but no planned group may start while the cap is already full.
    for n, g in counted.items():
        if g.get("started"):
            continue
        t0 = mins(g["start"])
        cur = sum(1 for m, h in counted.items() if m != n
                  and mins(h["start"]) <= t0 < mins(h["finish"]))
        if cur >= slots:
            bad.append(f"in flight: {n} dispatched at {g['start']} with {cur} "
                       f"groups in flight (cap {slots})")
        curw = sum(1 for m, h in counted.items() if m != n
                   and mins(h["start"]) <= t0 < mins(h["start"]) + h["duration_minutes"])
        if curw >= seats:
            bad.append(f"seats: {n} dispatched at {g['start']} with {curw} "
                       f"groups working (cap {seats})")

    # 3. coordinator cap: at most `coord_cap` PLANNED groups in flight; the
    #    inherited in-progress set is recorded and must match the groups.
    coord = [(n, g) for n, g in in_round.items()
             if g.get("coordinator") and not g.get("exempt_coordinator")]
    for t, _, _ in events:
        curc = sum(1 for n, g in coord
                   if not g.get("started")
                   and mins(g["start"]) <= t < mins(g["finish"]))
        if curc > coord_cap:
            bad.append(f"coordinator cap: {curc} planned groups touching "
                       f"coordinator.py at {iso(start, t)} (cap {coord_cap})")
            break
    inherited_coord = sorted(n for n, g in coord if g.get("inherited"))
    rec = plan["generated"].get("inherited_coordinator")
    if rec is None:
        bad.append("coordinator cap: the inherited in-progress set is not "
                   "recorded in generated.inherited_coordinator")
    else:
        if rec.get("cap") != coord_cap:
            bad.append(f"coordinator cap: the inherited record says cap "
                       f"{rec.get('cap')}, the plan's is {coord_cap}")
        if sorted(rec.get("groups") or []) != inherited_coord:
            bad.append(f"coordinator cap: the inherited record "
                       f"{sorted(rec.get('groups') or [])} does not equal "
                       f"{inherited_coord}")
        if bool(rec.get("exceeds_cap")) != (len(inherited_coord) > coord_cap):
            bad.append("coordinator cap: the inherited record's exceeds_cap "
                       "flag disagrees with the groups")

    # 4. a wave opens only while the open-PR cap has room
    for w in plan.get("waves", []):
        t = mins(w["opens"])
        cur = sum(1 for g in counted.values() if not g.get("started")
                  and mins(g["start"]) <= t < mins(g["finish"]))
        if cur > slots:
            bad.append(f"wave {w['wave']} opens at {w['opens']} with {cur} in "
                       f"flight (cap {slots})")

    # 5. stamp cadence: every `every` production merges cuts one patch stamp;
    #    the last fewer-than-`every` ride the one round-close stamp that closes
    #    the programme, last, at the version `closure_version` assigns
    produced = [n for n, g in sorted(
        ((n, g) for n, g in in_round.items() if g.get("lane") in PRODUCTION),
        key=lambda x: (mins(x[1]["finish"]), x[0]))]
    credit = list((plan.get("generated") or {}).get("stamp_credit") or [])
    produced = credit + produced
    patch_stamps = [s for s in plan.get("stamps", []) if s["kind"] == "patch"]
    closes = [s for s in plan.get("stamps", []) if s["kind"] == ROUND_CLOSE]
    gen = plan.get("generated") or {}
    want, why = closure_version(str(gen.get("version") or ""), gen.get("round"))
    if len(closes) != 1 or plan["stamps"][-1] is not closes[0]:
        bad.append(f"round close: {len(closes)} {ROUND_CLOSE} stamps, expected "
                   "one, and last")
    elif why:
        bad.append(f"round close: {why}")
    elif closes[0]["version"] != want:
        bad.append(f"round close: the closure stamp is {closes[0]['version']}, "
                   f"round {gen.get('round')} closes as {want}")
    stray = [s["kind"] for s in plan.get("stamps", [])
             if s["kind"] not in ("patch", ROUND_CLOSE)]
    if stray:
        bad.append(f"stamp cadence: unknown stamp kind(s) {stray}")
    for n in plan.get("summary", {}).get("post_closure") or []:
        if any(n in s["carries"] for s in plan.get("stamps", [])):
            bad.append(f"post-closure: {n} is in a stamp's carries")
        if closes and mins(groups[n]["start"]) < mins(closes[0]["at"]):
            bad.append(f"post-closure: {n} starts before the round-close stamp")
    if len(patch_stamps) != len(produced) // every:
        bad.append(f"stamp cadence: {len(patch_stamps)} patch stamps for "
                   f"{len(produced)} production merges at a cadence of {every}")
    covered: list = []
    for s in patch_stamps:
        covered.extend(s["carries"])
        if len(s["carries"]) != every:
            bad.append(f"stamp cadence: {s['version']} carries "
                       f"{len(s['carries'])} production groups, not {every}")
    if closes:
        covered.extend(closes[0]["carries"])
        if len(closes[0]["carries"]) > every:
            bad.append(f"stamp cadence: the round-close stamp carries "
                       f"{len(closes[0]['carries'])} production groups")
    if covered != produced:
        bad.append("stamp cadence: stamped production groups do not equal the "
                   "merged production groups, in merge order")

    # 6. the summary agrees with the groups it summarises
    s = plan["summary"]
    if s["batches"] != len(plan.get("batches", [])):
        bad.append("summary: batch count disagrees with the batches list")
    if s["stamps"] != len(plan.get("stamps", [])):
        bad.append("summary: stamp count disagrees with the stamps list")
    if s["groups_open"] != len(groups):
        bad.append("summary: open-group count disagrees with the groups list")
    close_stamps = [x for x in plan.get("stamps", []) if x.get("kind") == ROUND_CLOSE]
    post_fin = [mins(plan["groups"][n]["finish"]) for n in s.get("post_closure") or []
                if n in plan["groups"]]
    closure = max([mins(x["at"]) for x in close_stamps] + post_fin
                  or [max((mins(g["finish"]) for g in in_round.values()), default=0)])
    if s.get("closure_conditions") != list(CLOSURE_CONDITIONS):
        bad.append("summary: closure_conditions is not the owner's closure conditions")
    if mins(s["closure"]) != closure:
        bad.append("summary: closure is not the later of the round-close stamp and the "
                   "last post-closure group finish")
    if "model" in plan["generated"]:
        bad += model_refusals(plan["generated"]["model"])
    else:
        bad.append("model: the plan records no duration model (generated.model)")
    return bad


# ------------------------------------------------------------------ self-test

def selftest() -> int:
    caps = dict(DEFAULT_CAPS, slots=6, seats=8)   # the fixture's caps, not the owner's
    FIXTURE_ROUND = 2  # the fixture plans close round 2 from v1.0.0
    durations = {
        "sizes_hours": {"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0},
        "live_remaining_fraction": 0.7,
        "batch_window_minutes": 20,
        "stamp_lead_minutes": 60,
        "closure_lead_minutes": 120,
        "ci": {
            "fast (3.14)": {"median_minutes": 50.0},
            "closures": {"median_minutes": 22.0},
            "Analyze (python)": {"median_minutes": 27.0, "cancelled_rate": 0.04},
        },
        "provenance": {},
    }
    # The measured fields `check_plan` requires, composing to sizes_hours
    # exactly (one round, no round cost), so every timing below is unchanged.
    durations.update(first_round_hours=dict(durations["sizes_hours"]),
                     review_rounds={k: 1.0 for k in durations["sizes_hours"]},
                     round_hours=0.0, carry_part_hours=1.0, carries_per_part=1.0)
    roster = {"groups": [
        {"group": "A", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "B", "size": "M", "lane": "Core model", "kind": "defect",
         "after": ["A"], "resume": {"stage": "not-started"}},
        {"group": "C", "size": "S", "lane": "Instruments", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "D", "size": "L", "lane": "Learners", "kind": "owner",
         "after": ["B"], "resume": {"stage": "not-started"}},
        {"group": "E", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "done"}},
    ]}
    start = dt.datetime(2026, 1, 5, 0, 0)
    failures = []

    def expect(name, cond, detail=""):
        print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else ': ' + detail}")
        if not cond:
            failures.append(name)

    # The lane follows the files a group owns (tvofi 2026-11-06): a group whose
    # every file is an instrument or CI path is not core-model work, whatever
    # its name; a group touching the integration stays in the core lane.
    def _lane(files, kind="fix", name="X-LANE-PROBE"):
        return roster_lane({"group": name, "kind": kind, "files": files})

    expect("lane: a CI-only group is Instruments",
           _lane([".github/workflows/ci.yml", "tools/ci/gate.py"]) == "Instruments",
           _lane([".github/workflows/ci.yml", "tools/ci/gate.py"]))
    expect("lane: a tests-and-tools group is Instruments",
           _lane(["tests/ci_ratchet.py", "tests/ci_budgets.json"]) == "Instruments")
    expect("lane: a docs-only doc group is Docs",
           _lane(["dev/audit/README.md", "CLAUDE.md"], kind="doc") == "Docs")
    expect("lane: a user-docs group is Docs",
           _lane(["README.md", "docs/setup.md", "tests/doc_claims.py"],
                 kind="feature") == "Docs")
    expect("lane null control: docs plus a tool is Instruments, not Docs",
           _lane(["docs/setup.md", "tools/x.py"], kind="feature") == "Instruments")
    expect("lane null control: a core-model group stays Core model",
           _lane(["custom_components/heatpump_optimizer/optimizer.py"]) == "Core model")
    expect("lane null control: a mixed group stays Core model",
           _lane(["tools/audit/seat/x.py",
                  "custom_components/heatpump_optimizer/ledger.py"]) == "Core model")
    expect("lane null control: a group with no files stays Core model",
           _lane([]) == "Core model")
    expect("lane null control: a bare filename is not proof of an instrument",
           _lane(["coordinator.py"]) == "Core model")
    expect("lane: an RCA group with no files is Instruments",
           _lane([], kind="rca") == "Instruments")
    expect("lane: a tooling group with no files is Instruments",
           _lane([], kind="tooling") == "Instruments")
    expect("lane: a stem names its exact group and its `<stem>-...` groups, "
           "never a look-alike (R10-I18N-DE is not R10-I1's)",
           roster_lane({"group": "R10-I1"}) == "Instruments"
           and roster_lane({"group": "R10-TICK-GROUP-LINES"}) == "Instruments"
           and roster_lane({"group": "R10-I18N-DE",
                            "files": ["custom_components/heatpump_optimizer/translations/de.json"]})
           == "Core model"
           and roster_lane({"group": "R10-GATEWAY"}) == "Core model",
           str([roster_lane({"group": g}) for g in
                ("R10-I1", "R10-TICK-GROUP-LINES", "R10-I18N-DE", "R10-GATEWAY")]))
    expect("lane: a roster class instrument with no files is Instruments",
           roster_lane({"group": "X-LANE-PROBE", "kind": "fix",
                        "class": "instrument"}) == "Instruments")
    expect("lane: user docs with a dev harness are Docs",
           _lane(["README.md", "docs/img/x.png", "dev/audit/harnesses/h.mjs",
                  "tests/doc_claims.py"], kind="production") == "Docs")
    expect("lane null control: a production group with no files stays Core model",
           roster_lane({"group": "X-LANE-PROBE", "kind": "production",
                        "class": "production"}) == "Core model")
    expect("lane null control: a named UX group keeps its lane over its kind",
           _lane([], kind="rca", name="R10-DEEPLINK-CENSUS") == "Product UX")
    expect("lane null control: a learner keeps its lane over its files",
           _lane(["tools/x.py"], name="R10-COP-GATE") == "Learners")
    # hot_files are owned files too: a tool group whose hot file is in the
    # integration, or is a bare filename, stays core (a bare basename, even a
    # tool's, is not proof of an instrument: the roster writes coordinator.py
    # and merge_train.py alike).
    def _hot(hot_files):
        return roster_lane({"group": "X-LANE-PROBE", "kind": "fix",
                            "files": ["tools/x.py"], "hot_files": hot_files})

    expect("lane null control: an integration hot file keeps a tool group Core model",
           _hot(["custom_components/heatpump_optimizer/x.py"]) == "Core model")
    expect("lane null control: a bare hot filename keeps a tool group Core model",
           _hot(["coordinator.py"]) == "Core model")
    expect("lane null control: a bare tool basename in hot_files stays Core model",
           _hot(["merge_train.py"]) == "Core model")
    expect("lane: an instrument-path hot file keeps a tool group Instruments",
           _hot([".github/workflows/ci.yml"]) == "Instruments")

    plan = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    absorbed = dict(roster, groups=roster["groups"] + [
        {"group": "X", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "absorbed", "absorbed_into": "A"}}])
    pa = build_plan(absorbed, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("an absorbed group is closed work, not scheduled", pa["groups"]["X"].get("done") is True,
           str(pa["groups"].get("X")))
    # Proposal 1 (tvofi 2026-11-07): a merged carries-open group whose every
    # carry is marked is closed work, and its dependent no longer waits on it.
    def carrying(carry):
        return dict(roster, groups=roster["groups"] + [
            {"group": "HD", "size": "L", "lane": "Core model", "kind": "defect", "after": [],
             "carry": carry, "resume": {"stage": "carries-open", "commit": "0123abcd"}},
            {"group": "HN", "size": "S", "lane": "Core model", "kind": "defect",
             "after": ["HD"], "resume": {"stage": "not-started"}}])
    marked = ["x [moved: A]", "y [implemented: 0123abcd]", "z [dismissed: a duplicate]"]
    pd = build_plan(carrying(marked), durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("discharged: a merged carries-open group with every carry marked is closed, "
           "takes no slot and clears its dependent's edge",
           pd["groups"]["HD"].get("done") is True and pd["groups"]["HD"].get("discharged") is True
           and pd["groups"]["HN"]["after"] == [] and pd["summary"]["groups_discharged"] == 1
           and check_plan(pd) == [], str(pd["groups"]["HD"]))
    po = build_plan(carrying(marked + ["w"]), durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("discharged (null): one unmarked carry keeps it scheduled and its dependent waiting",
           po["groups"]["HD"].get("done") is False and po["groups"]["HN"]["after"] == ["HD"]
           and po["summary"]["groups_discharged"] == 0, str(po["groups"]["HD"]))
    pl = build_plan(carrying(marked + ["w"]), durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND,
                    legacy={"HD": frozenset({"w"})})
    expect("discharged: a legacy carry is not owed (the cut-over is read)",
           pl["groups"]["HD"].get("done") is True, str(pl["groups"]["HD"]))
    again = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("deterministic: two runs are byte-identical",
           json.dumps(plan, sort_keys=True) == json.dumps(again, sort_keys=True))
    bad = check_plan(plan)
    expect("the clean plan passes --check", bad == [], str(bad))
    expect("the critical path runs A -> B -> D",
           plan["critical_path"] == ["A", "B", "D"], str(plan["critical_path"]))

    # planted: dependency cycle
    cyc = json.loads(json.dumps(roster))
    for g in cyc["groups"]:
        if g["group"] == "A":
            g["after"] = ["D"]
    try:
        build_plan(cyc, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
        expect("cycle: build refuses", False, "it scheduled a cycle")
    except PlanError as exc:
        expect("cycle: build refuses", "cycle" in str(exc), str(exc))

    # planted: over-cap wave (eight groups in flight at one instant)
    over = json.loads(json.dumps(plan))
    over["groups"].update({
        f"X{i}": dict(over["groups"]["A"], after=[], coordinator=False,
                      start=over["groups"]["A"]["start"],
                      finish=over["groups"]["A"]["finish"])
        for i in range(7)
    })
    over["summary"]["groups_open"] += 7
    bad = check_plan(over)
    expect("over-cap wave refuses", any("in flight" in b for b in bad), str(bad))

    # planted: dependency finishing after its dependent starts
    dep = json.loads(json.dumps(plan))
    dep["groups"]["A"]["finish"] = dep["groups"]["D"]["finish"]
    bad = check_plan(dep)
    expect("dependency inversion refuses", any("dependency:" in b for b in bad), str(bad))

    # planted: a stamp cadence breach (a production merge no stamp carries)
    st = json.loads(json.dumps(plan))
    for s in st["stamps"]:
        s["carries"] = []
    bad = check_plan(st)
    expect("stamp cadence breach refuses",
           any("stamp cadence" in b for b in bad), str(bad))

    # planted: a patch stamp cut for fewer than `every` production groups
    st2 = json.loads(json.dumps(plan))
    st2["stamps"].insert(0, {"version": "v1.0.1",
                             "at": st2["stamps"][-1]["at"], "kind": "patch",
                             "batch": 1, "carries": ["A"]})
    st2["summary"]["stamps"] = len(st2["stamps"])
    bad = check_plan(st2)
    expect("short patch stamp refuses",
           any("not " + str(DEFAULT_CAPS["stamp_every"]) in b for b in bad), str(bad))

    # planted: a summary that does not agree with the groups
    sm = json.loads(json.dumps(plan))
    sm["summary"]["closure"] = "2000-01-01T00:00:00Z"
    bad = check_plan(sm)
    expect("summary mismatch refuses", any("closure" in b for b in bad), str(bad))

    # The refusals above are the function's; these prove the COMMAND exits
    # non-zero, which is the property a wave edge depends on.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        badp = Path(td) / "bad.json"
        badp.write_text(json.dumps(over), encoding="utf-8")
        rc = subprocess.run([sys.executable, "-I", __file__, "--check",
                             "--plan", str(badp)], capture_output=True).returncode
        expect("--check exits 1 on a planted over-cap wave", rc == 1, f"rc={rc}")
        # The fixture is named as a roster, so the command reads its round and
        # the exit is the cycle's; the unnamed copy has no round to close.
        # `--repo td` holds no VERSION, so the fixture closes round 1 from 0.0.0
        # whatever the checkout's own version is.
        cycf = Path(td) / "wave-r1-groups.json"
        cycf.write_text(json.dumps(cyc), encoding="utf-8")
        out = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(cycf),
                              "--out", str(Path(td) / "p.json"), "--repo", td,
                              "--start", "2026-01-05T00:00:00Z"],
                             capture_output=True, text=True)
        expect("the command exits 2 on a dependency cycle",
               out.returncode == 2 and "cycle" in out.stderr,
               f"rc={out.returncode} {out.stderr[-200:]}")
        unnamed = Path(td) / "groups.json"
        unnamed.write_text(json.dumps(roster), encoding="utf-8")
        out = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(unnamed),
                              "--out", str(Path(td) / "p.json"), "--repo", td,
                              "--start", "2026-01-05T00:00:00Z"],
                             capture_output=True, text=True)
        expect("a roster naming no round refuses, never defaults (exit 2)",
               out.returncode == 2 and "round" in out.stderr,
               f"rc={out.returncode} {out.stderr[-200:]}")

    # planted: an over-cap model input (7 slots' worth of live groups at t=0)
    many = {"groups": [
        {"group": f"L{i}", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "in-progress"}} for i in range(7)
    ]}
    p2 = build_plan(many, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    # (Before 2026-11-01 the seventh was queued behind every new dispatch:
    # started work fell to the back of the plan, the owner's report.)
    expect("every started group starts at the replan instant, past the slot cap",
           p2["summary"]["inherited_in_progress"] == 7 and check_plan(p2) == [],
           str((p2["summary"]["inherited_in_progress"], check_plan(p2))))

    # The inherited state the docstring promises to RECORD: a fixer ahead of
    # the roster's serialisation, and a coordinator-touching live group.
    ahead = {"groups": [
        {"group": "B", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "A", "size": "S", "lane": "Core model", "kind": "defect",
         "after": ["B"], "hot_files": ["coordinator.py"],
         "resume": {"stage": "in-progress"}},
        {"group": "C", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "hot_files": ["coordinator.py"],
         "resume": {"stage": "in-progress"}},
    ]}
    p3 = build_plan(ahead, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    inv = p3["generated"]["inherited_dependency_violations"]
    expect("a started group waits for its unmerged dependency: no inversion to inherit",
           inv == [] and p3["groups"]["A"]["start"] == p3["groups"]["B"]["finish"],
           str((inv, p3["groups"]["A"]["start"])))
    expect("the plan with a recorded inversion passes --check",
           check_plan(p3) == [], str(check_plan(p3)))
    deleted = json.loads(json.dumps(p3))
    deleted["groups"]["A"].update(start=p3["generated"]["start"], inherited=True)
    expect("an unrecorded inherited inversion refuses",
           any("inherited_dependency_violations" in b
               for b in check_plan(deleted)), str(check_plan(deleted)))

    rec = p3["generated"]["inherited_coordinator"]
    expect("the inherited coordinator set is recorded",
           rec["groups"] == ["C"] and rec["cap"] == caps["coordinator_cap"]
           and rec["exceeds_cap"] is False, str(rec))
    norec = json.loads(json.dumps(p3))
    del norec["generated"]["inherited_coordinator"]
    expect("a missing inherited-coordinator record refuses",
           any("inherited in-progress set is not recorded" in b
               for b in check_plan(norec)), str(check_plan(norec)))
    oversized = json.loads(json.dumps(p3))
    oversized["generated"]["inherited_coordinator"]["exceeds_cap"] = True
    expect("a disagreeing inherited-coordinator record refuses",
           any("exceeds_cap" in b for b in check_plan(oversized)),
           str(check_plan(oversized)))

    # Freshness (`stale_reason`): a plan describes the roster blob it was
    # built from, so a roster commit after the replan makes it stale -- the
    # function and the `--check` command both refuse, and both pass it fresh.
    sys.path.insert(0, str(Path(roster_lib.__file__).resolve().parents[3] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        rpath = repo / roster_lib.ROSTERS_DIR / "wave-r9-groups.json"
        rpath.parent.mkdir(parents=True)
        throwaway_git_init(repo, "-q", "-b", "main")

        def commit(r: dict) -> None:
            rpath.write_text(json.dumps(r), encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "r"], check=True)
        commit(roster)
        r_, ref_, blob_ = load_roster(str(repo), "main")
        fresh = build_plan(r_, durations, caps, start, "v1.0.0", ref_, blob_,
                           round_n=roster_lib.roster_round(str(rpath)))
        expect("a plan pins the roster blob it was built from", len(blob_) == 40, blob_)
        expect("a fresh plan is not stale",
               stale_reason(fresh, str(repo)) is None, str(stale_reason(fresh, str(repo))))
        planf = Path(td) / "plan.json"
        planf.write_text(json.dumps(fresh), encoding="utf-8")
        cmd = [sys.executable, "-I", __file__, "--check", "--plan", str(planf),
               "--repo", str(repo)]
        rc = subprocess.run(cmd, capture_output=True).returncode
        expect("--check passes a fresh plan (null control)", rc == 0, f"rc={rc}")
        moved = json.loads(json.dumps(roster))
        moved["groups"][0]["resume"] = {"stage": "done"}
        commit(moved)
        why = stale_reason(fresh, str(repo)) or ""
        expect("a roster commit after the replan makes the plan stale",
               "stale" in why, why)
        out = subprocess.run(cmd, capture_output=True, text=True)
        expect("--check exits 1 on a stale plan",
               out.returncode == 1 and "freshness" in out.stderr,
               f"rc={out.returncode} {out.stderr[-200:]}")
        # An explicit ref outranks the plan's own: main~1 still holds the
        # blob the plan pins, while generated.roster_ref (main) has moved.
        expect("an explicit ref is read instead of generated.roster_ref",
               fresh["generated"]["roster_ref"] == "main"
               and stale_reason(fresh, str(repo), "main~1") is None,
               str(stale_reason(fresh, str(repo), "main~1")))
        rc = subprocess.run(cmd + ["--roster-ref", "main~1"], capture_output=True).returncode
        expect("--check --roster-ref passes the plan at the ref it names", rc == 0, f"rc={rc}")
        why = stale_reason(plan, str(repo)) or ""
        expect("a plan pinning no roster blob is refused as unknowable",
               "unknowable" in why, why)

    # The six behaviours whose deletion the reviewer will attempt: each gets
    # an arm that names it, and the mutation harness below proves the arm goes
    # red when the line is removed.
    rerun = [  # the API lists newest first; the second line is the first attempt
        "closures\t2\t2026-01-05T01:00:00Z\t2026-01-05T01:30:00Z\tsuccess",
        "closures\t1\t2026-01-05T00:00:00Z\t2026-01-05T00:20:00Z\tfailure",
    ]
    ing = _ingest_check_runs(rerun, {"closures"})
    expect("a rerun does not replace the first attempt (earliest started_at)",
           ing.get("closures", {}).get("job") == 1
           and ing["closures"]["minutes"] == 20.0, str(ing))

    coord3 = {"groups": [
        {"group": f"K{i}", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "hot_files": ["coordinator.py"],
         "resume": {"stage": "not-started"}} for i in range(3)]}
    p4 = build_plan(coord3, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("the coordinator cap limits planned groups in flight",
           p4["summary"]["peak_coordinator_in_flight"] <= caps["coordinator_cap"],
           str(p4["summary"]["peak_coordinator_in_flight"]))

    one = dict(caps)
    one["slots"] = 1
    order = {"groups": [
        {"group": "A", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "B", "size": "L", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "C", "size": "XL", "lane": "Core model", "kind": "defect",
         "after": ["B"], "resume": {"stage": "not-started"}}]}
    p5 = build_plan(order, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("dispatch takes the longest remaining path first, not the shortest job",
           p5["groups"]["A"]["start"] > p5["groups"]["B"]["start"],
           f"A starts {p5['groups']['A']['start']}, B {p5['groups']['B']['start']}")

    # The owner's dispatch priority (`dispatch_tier`): the critical path
    # computed from the graph, then production, then the rest by the roster's
    # `savings`. The fixtures below fail on a key that sees remaining height
    # alone; the tiers are derived at each replan, never stored.
    prio = {"groups": [
        # CP -> CP2 is the 10 h chain, so it is `critical_path()`
        {"group": "CP", "size": "L", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "CP2", "size": "M", "lane": "IN", "kind": "instrument",
         "after": ["CP"], "resume": {"stage": "not-started"}},
        # a SHORT production group (Core model, 2 h) beside a TALLER
        # non-production one (Instruments, 8 h): priority puts production
        # second; height alone puts the taller group second
        {"group": "PROD", "size": "S", "lane": "CO", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "TALL", "size": "XL", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
    ]}
    p7 = build_plan(prio, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
    starts7 = {g: p7["groups"][g]["start"] for g in ("CP", "CP2", "PROD", "TALL")}
    expect("the computed critical path is CP -> CP2",
           p7["critical_path"] == ["CP", "CP2"], str(p7["critical_path"]))
    expect("the critical path is dispatched before the shorter work",
           p7["groups"]["CP"]["start"] == iso(start, 0)
           and p7["groups"]["CP2"]["start"] < p7["groups"]["PROD"]["start"],
           str(starts7))
    expect("a short production group outranks a taller non-production one",
           p7["groups"]["PROD"]["start"] < p7["groups"]["TALL"]["start"], str(starts7))

    # The t==0 live admission must use the SAME key: under height alone TALL
    # (8 h) is admitted and the short production group is queued.
    liveprio = {"groups": [
        {"group": "CP", "size": "L", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "CP2", "size": "M", "lane": "IN", "kind": "instrument",
         "after": ["CP"], "resume": {"stage": "not-started"}},
        {"group": "PROD", "size": "S", "lane": "CO", "kind": "defect",
         "after": [], "resume": {"stage": "in-progress"}},
        {"group": "TALL", "size": "XL", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "in-progress"}},
    ]}
    p8 = build_plan(liveprio, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("the t==0 started admission keeps both, in the same priority key",
           p8["groups"]["PROD"]["inherited"] is True
           and p8["groups"]["TALL"]["inherited"] is True
           and p8["groups"]["PROD"]["sort_key"] < p8["groups"]["TALL"]["sort_key"],
           str({g: p8["groups"][g]["sort_key"] for g in ("PROD", "TALL")}))

    # Within the instrument tier the roster's `savings` ranks; absent sorts
    # last. CP owns the critical path so HI/LO/NONE all share that tier. The
    # size order (L, M, S) is the opposite of the savings order, so height
    # alone would invert it.
    save = {"groups": [
        {"group": "CP", "size": "XL", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "HI", "size": "S", "lane": "IN", "kind": "instrument",
         "savings": 9, "after": [], "resume": {"stage": "not-started"}},
        {"group": "LO", "size": "L", "lane": "IN", "kind": "instrument",
         "savings": 1, "after": [], "resume": {"stage": "not-started"}},
        {"group": "NONE", "size": "M", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
    ]}
    p9 = build_plan(save, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("the instrument tier ranks by savings, and absent savings sorts last",
           p9["groups"]["HI"]["start"] < p9["groups"]["LO"]["start"]
           < p9["groups"]["NONE"]["start"],
           str({g: p9["groups"][g]["start"] for g in ("HI", "LO", "NONE")}))

    # Height breaks ties within a tier, ahead of the name (AAA would win on
    # the name alone).
    tie = {"groups": [
        {"group": "CP", "size": "XL", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "AAA", "size": "S", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
        {"group": "ZZZ", "size": "L", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
    ]}
    p10 = build_plan(tie, durations, one, start, "v1.0.0", round_n=FIXTURE_ROUND)
    expect("height breaks ties within a tier, ahead of the name",
           p10["groups"]["ZZZ"]["start"] < p10["groups"]["AAA"]["start"],
           str({g: p10["groups"][g]["start"] for g in ("AAA", "ZZZ")}))

    # A size the durations table does not measure is refused at the roster
    # boundary, naming the roster, the group and the size -- never a KeyError
    # from inside the schedule and never an invented duration (the live roster
    # carries `XS`; sizes_hours records no XS sample).
    unmeasured = {"groups": [
        {"group": "XS-GROUP", "size": "XS", "lane": "IN", "kind": "instrument",
         "after": [], "resume": {"stage": "not-started"}},
    ]}
    try:
        build_plan(unmeasured, durations, caps, start, "v1.0.0",
                   roster_path="dev/programme/rosters/wave-r10-groups.json", round_n=10)
        expect("an unmeasured size is refused, naming roster, group and size",
               False, "it scheduled an XS group")
    except Exception as exc:  # noqa: BLE001 -- any other failure is a crash, not this refusal
        msg = str(exc)
        expect("an unmeasured size is refused, naming roster, group and size",
               "XS-GROUP" in msg and "XS" in msg
               and "wave-r10-groups.json" in msg, msg)
    measured = {"groups": [
        {"group": f"MX{k}", "size": s, "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}}
        for k, s in enumerate(("S", "M", "L", "XL"))]}
    try:
        build_plan(measured, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
        expect("a roster of only measured sizes plans", True)
    except PlanError as exc:
        expect("a roster of only measured sizes plans", False, str(exc))

    # A non-numeric savings is refused, never silently treated as absent (it
    # would otherwise reach float() and crash, or worse, sort last unnoticed).
    badsav = {"groups": [
        {"group": "BADSAV", "size": "S", "lane": "IN", "kind": "instrument",
         "savings": "lots", "after": [], "resume": {"stage": "not-started"}},
    ]}
    try:
        build_plan(badsav, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
        expect("a non-numeric savings is refused", False, "it scheduled")
    except Exception as exc:  # noqa: BLE001 -- any other failure is a crash, not this refusal
        expect("a non-numeric savings is refused", "savings" in str(exc), str(exc))

    prod = {"groups": [
        {"group": f"P{i}", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "not-started"}} for i in range(6)]}
    caps = dict(caps, stamp_every=5)
    p6 = build_plan(prod, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
    pat = [s for s in p6["stamps"] if s["kind"] == "patch"]
    expect("five production merges cut one patch stamp",
           len(pat) == 1 and len(pat[0]["carries"]) == caps["stamp_every"],
           str(p6["stamps"]))
    s6 = p6["summary"]
    expect("CI minutes price every gate run (batches + stamps)",
           s6["batches"] > 0 and s6["stamps"] > 0
           and s6["ci_minutes"] == round((s6["batches"] + s6["stamps"])
                                         * s6["gate_minutes"], 1),
           str({k: s6[k] for k in ("ci_minutes", "batches", "stamps", "gate_minutes")}))
    # The closure stamp is the round's major (decision 0016, tvofi
    # 2026-10-29): round N closes as vN.0.0, the version `stamp.py
    # --round-close N` assigns, and the interim stamps stay patch bumps.
    close = p6["stamps"][-1]
    expect("the closure stamp is the round-close major of the plan's round",
           close["kind"] == "round-close" and close["version"] == "v2.0.0"
           and p6["summary"]["closure_stamp"] == "v2.0.0"
           and p6["generated"]["round"] == 2, str(close))
    expect("an interim stamp stays a patch bump of the current version",
           [s["version"] for s in pat] == ["v1.0.1"], str(pat))
    p6r3 = build_plan(prod, durations, caps, start, "v1.0.0", round_n=3)
    expect("the closure major follows the round, not a constant",
           p6r3["stamps"][-1]["version"] == "v3.0.0", str(p6r3["stamps"][-1]))
    try:
        build_plan(prod, durations, caps, start, "v2.4.0", round_n=2)
        expect("a round not above the current major refuses", False, "it planned one")
    except PlanError as exc:
        expect("a round not above the current major refuses",
               "not above the current major" in str(exc), str(exc))
    for kind, version in (("minor", "v1.1.0"), ("round-close", "v1.1.0"),
                          ("round-close", "v3.0.0")):
        wrong = json.loads(json.dumps(p6))
        wrong["stamps"][-1].update(kind=kind, version=version)
        bad = check_plan(wrong)
        expect(f"--check refuses a {kind} closure stamp {version} in round 2",
               any("round close" in b for b in bad), str(bad))
    # The closure arms the wrong-closure rows above never reach: a correct
    # round-close stamp that is not last, and a stray kind beside a correct one.
    notlast = json.loads(json.dumps(p6))
    notlast["stamps"].append(dict(notlast["stamps"][0], carries=[]))
    notlast["summary"]["stamps"] = len(notlast["stamps"])
    bad = check_plan(notlast)
    expect("--check refuses a round-close stamp that is not the last stamp",
           any("expected one, and last" in b for b in bad), str(bad))
    stray = json.loads(json.dumps(p6))
    stray["stamps"].insert(0, dict(stray["stamps"][0], kind="minor", carries=[],
                                   version="v1.1.0"))
    stray["summary"]["stamps"] = len(stray["stamps"])
    bad = check_plan(stray)
    expect("--check refuses a minor stamp beside a correct round close",
           any("unknown stamp kind(s) ['minor']" in b for b in bad)
           and not any("round close" in b for b in bad), str(bad))
    # `round_n` has no default: a caller that omits it is a TypeError, never a
    # round silently assumed (the stance next_version takes on no roster).
    try:
        build_plan(prod, durations, caps, start, "v1.0.0")
        expect("build_plan without round_n refuses", False, "it planned a closure")
    except TypeError as exc:
        expect("build_plan without round_n refuses", "round_n" in str(exc), str(exc))
    unround = json.loads(json.dumps(p6))
    del unround["generated"]["round"]
    bad = check_plan(unround)
    expect("--check refuses a plan recording no round",
           any("round close" in b for b in bad), str(bad))

    # ---- the round-10 flow-toolkit carries: one arm each, with a null control
    def fx(n, size="S", kind="defect", lane="Core model", stage="not-started",
           after=(), **kw):
        return {"group": n, "size": size, "lane": lane, "kind": kind,
                "after": list(after), "resume": {"stage": stage, **kw.pop("res", {})}, **kw}

    def sched(p, drop=()):
        return json.dumps({"g": {n: v for n, v in p["groups"].items() if n not in drop},
                           "w": p["waves"], "s": p["stamps"], "b": p["batches"]},
                          sort_keys=True)

    def mk(groups, **kw):
        c = kw.pop("caps_", dict(caps, stamp_every=DEFAULT_CAPS["stamp_every"]))
        return build_plan({"groups": groups}, kw.pop("dur", durations), c, start,
                          "v1.0.0", round_n=FIXTURE_ROUND, **kw)

    # 1. absorbed counts as done (carry 2)
    base_g = [fx("R10-A"), fx("R10-B", after=["R10-A"])]
    ab = mk(base_g + [fx("R10-AB", stage="absorbed", res={"note": "absorbed into R10-A"})])
    expect("absorbed: the group is done, names its absorber, is not scheduled",
           ab["groups"]["R10-AB"]["done"] and ab["groups"]["R10-AB"]["start"] is None
           and ab["groups"]["R10-AB"]["absorbed_into"] == "R10-A"
           and ab["absorbed"]["R10-AB"] == {"into": "R10-A", "advisory": None}, str(ab["absorbed"]))
    nb = mk(base_g + [fx("R10-AB", stage="absorbed", res={"note": "folded away"})])
    expect("absorbed: a note naming no group records the ADVISORY, never a refusal",
           nb["absorbed"]["R10-AB"]["into"] is None
           and nb["absorbed"]["R10-AB"]["advisory"].startswith("ADVISORY: R10-AB"), str(nb["absorbed"]))
    expect("absorbed (null): the roster minus the absorbed group reproduces the schedule",
           sched(ab, drop=("R10-AB",)) == sched(mk(base_g)), "schedules differ")

    # 2. post-closure groups (carries 10, 11)
    cat = fx("R10-CATALOG-PR", kind="owner-step", lane="Docs", after=["R10-B"],
             res={"next_step": "after the round-close stamp"})
    pc = mk(base_g + [cat])
    p0 = mk(base_g)
    close_at = pc["stamps"][-1]["at"]
    expect("post-closure: the owner step starts at or after the closing stamp, flagged",
           pc["groups"]["R10-CATALOG-PR"].get("post_closure") is True
           and pc["groups"]["R10-CATALOG-PR"]["start"] >= close_at
           and pc["summary"]["post_closure"] == ["R10-CATALOG-PR"], str(pc["groups"]["R10-CATALOG-PR"]))
    expect("post-closure: in no stamp's carries, and summary.closure is the later of the "
           "stamp and the catalog step's finish (tvofi 2026-11-07), which starts no earlier "
           "than the stamp",
           all("R10-CATALOG-PR" not in s["carries"] for s in pc["stamps"])
           and pc["summary"]["closure"] == pc["groups"]["R10-CATALOG-PR"]["finish"]
           and pc["summary"]["closure"] > close_at
           and pc["groups"]["R10-CATALOG-PR"]["start"] >= close_at
           and pc["stamps"] == p0["stamps"], str((pc["summary"]["closure"], pc["stamps"])))
    # The fixture prices a round at 0 h, which would make every review price 0:
    # these arms use a round of 1 h and S at the named expected rounds.
    def rv(st, rounds=3.0, drop=()):
        d = dict(durations, round_hours=1.0, review_rounds={**durations["review_rounds"], "S": rounds})
        return group_hours(fx("RV", "S", stage=st), {k: v for k, v in d.items() if k not in drop},
                           True, "<t>")[0]
    expect("live stage: a group in review is priced by its review rounds left, below a fresh "
           "fixer's remaining share; one in progress is not",
           abs(rv("in-review") - 2.0) < 1e-9 and rv("in-review") == rv("review")
           and rv("in-review") < rv("in-progress"),
           str([rv(x) for x in ("in-review", "review", "in-progress")]))
    expect("live stage (floor): fewer than two expected rounds still price one review round, "
           "not the rounds themselves (max(rounds - 1, 1))",
           abs(rv("in-review", 1.4) - 1.0) < 1e-9 and 1.4 < rv("in-progress", 1.4),
           str((rv("in-review", 1.4), rv("in-progress", 1.4))))
    unset = ("live_remaining_fraction",)
    expect("live stage (cap): with no live_remaining_fraction recorded, review and progress "
           "share the one 0.7 default, so many rounds left price as in progress",
           rv("in-review", 99.0, unset) == rv("in-progress", 99.0, unset) < 98.0,
           str((rv("in-review", 99.0, unset), rv("in-progress", 99.0, unset))))
    gen_start = dt.datetime.strptime(pc["generated"]["start"], "%Y-%m-%dT%H:%M:%SZ")
    expect("post-closure: wall_hours runs to summary.closure (the catalog finish), not the stamp",
           abs(pc["summary"]["wall_hours"] * 60 - (
               dt.datetime.strptime(pc["summary"]["closure"], "%Y-%m-%dT%H:%M:%SZ")
               - gen_start).total_seconds() / 60) < 1.0
           and pc["summary"]["wall_hours"] > p0["summary"]["wall_hours"],
           str((pc["summary"]["wall_hours"], p0["summary"]["wall_hours"])))
    expect("closure conditions: the plan states the owner's six (tvofi 2026-11-07), and --check "
           "refuses a plan that drops them",
           pc["summary"]["closure_conditions"] == [
               "no open pull requests", "no handoffs", "no carries", "no findings",
               "no leads", "only the coordination issue open"]
           and any("closure_conditions" in b for b in check_plan(
               dict(pc, summary=dict(pc["summary"], closure_conditions=[])))), "")
    expect("post-closure (null): with no post-stamp group, closure is the stamp's at",
           p0["summary"]["closure"] == p0["stamps"][-1]["at"], str(p0["summary"]["closure"]))
    expect("post-closure (a): a plan whose closure drops the catalog step is refused by --check",
           any("closure" in b for b in check_plan(
               dict(pc, summary=dict(pc["summary"], closure=p0["summary"]["closure"])))), "")
    ex = cli_caps(parse_args(["--slots", "7"]))
    expect("slots 20 (null): an explicit --slots keeps its value, the seats stay the default",
           ex["slots"] == 7 and ex["seats"] == DEFAULT_CAPS["seats"] == 20, str(ex))
    expect("post-closure (null): a production group with no stamp dependency is in the "
           "closing stamp's carries",
           pc["stamps"][-1]["carries"] == ["R10-A", "R10-B"], str(pc["stamps"][-1]))
    expect("post-closure: the plan passes --check", check_plan(pc) == [], str(check_plan(pc)))

    # 3. overflow start (carry 8): a critical-path group starts past a full cap
    ov = mk([fx("L1", stage="in-progress"), fx("L2", stage="in-progress"), fx("X3", "L"),
             fx("CP1", "XL"), fx("CP2", after=["CP1"])], caps_=dict(caps, slots=2))
    expect("overflow: a ready critical-path group starts at t=0, flagged exempt",
           ov["groups"]["CP1"]["start"] == iso(start, 0) and ov["groups"]["CP1"].get("exempt") is True
           and check_plan(ov) == [], str({n: g["start"] for n, g in ov["groups"].items()}))
    expect("overflow (null): the non-critical group past the cap waits and is not exempt",
           any(g["start"] > iso(start, 0) and not g.get("exempt")
               for n, g in ov["groups"].items() if n == "X3"), "none waited")

    # 3b. the exemption holds against the coordinator cap too (orchestrator.md
    # section 5: "regardless of every cap"); the slots cap alone is not enough.
    def cfx(n, size="S", **kw):
        return fx(n, size, files=["custom_components/heatpump_optimizer/coordinator.py"], **kw)
    cc = mk([cfx("K1", stage="in-progress"), cfx("K2", stage="in-progress"),
             cfx("X3", "L"), cfx("CP1", "XL"), fx("CP2", after=["CP1"])],
            caps_=dict(caps, coordinator_cap=1))
    expect("coordinator: a ready critical-path group starts at t=0 past a full "
           "coordinator cap, flagged, and the plan passes --check",
           cc["groups"]["CP1"]["start"] == iso(start, 0)
           and cc["groups"]["CP1"].get("exempt_coordinator") is True
           and check_plan(cc) == [],
           str({n: g["start"] for n, g in cc["groups"].items()}) + str(check_plan(cc)))
    expect("coordinator (null): the non-critical coordinator group still waits and "
           "is not flagged",
           cc["groups"]["X3"]["start"] > iso(start, 0)
           and not cc["groups"]["X3"].get("exempt_coordinator")
           and cc["groups"]["X3"]["start_reason"].startswith("coordinator cap 1"),
           str(cc["groups"]["X3"]))
    cq = mk([cfx("K1", stage="in-progress"), cfx("CP1", "XL"), fx("CP2", after=["CP1"])],
            caps_=dict(caps, coordinator_cap=2))
    expect("coordinator (null): inside the cap the critical-path group is not flagged",
           not cq["groups"]["CP1"].get("exempt_coordinator"), str(cq["groups"]["CP1"]))
    ce = mk([cfx("K1", stage="in-progress"), cfx("CP1", "XL"), fx("CP2", after=["CP1"])],
            caps_=dict(caps, coordinator_cap=1))
    expect("coordinator: a critical-path group is flagged exactly when the cap is "
           "full (one in flight, cap 1), not only when it is exceeded",
           ce["groups"]["CP1"].get("exempt_coordinator") is True
           and ce["groups"]["CP1"]["start"] == iso(start, 0), str(ce["groups"]["CP1"]))
    nocp = json.loads(json.dumps(cc))
    nocp["groups"]["CP1"].pop("exempt_coordinator")
    nocp["groups"]["X3"].update(start=nocp["groups"]["CP1"]["start"],
                                finish=nocp["groups"]["CP1"]["finish"])
    expect("coordinator: --check still refuses two planned coordinator groups in "
           "flight when the critical-path one is unflagged",
           any("coordinator cap" in b for b in check_plan(nocp)), str(check_plan(nocp)))

    # 3b'. the flagged group overlaps a running one: --check must exclude it from
    # the coordinator count (X3 runs while CP1, fed by D, starts flagged).
    ov2 = mk([fx("D"), cfx("CP1", "XL", after=["D"]), fx("CP2", "XL", after=["CP1"]),
              cfx("X3", "L")], caps_=dict(caps, coordinator_cap=1))
    c1, x3 = ov2["groups"]["CP1"], ov2["groups"]["X3"]
    expect("coordinator: --check passes a flagged critical-path start that overlaps "
           "a running coordinator group (the flag is read)",
           c1.get("exempt_coordinator") is True and x3["start"] < c1["start"] < x3["finish"]
           and check_plan(ov2) == [], str((c1, x3, check_plan(ov2))))
    ov3 = json.loads(json.dumps(ov2))
    ov3["groups"]["CP1"].pop("exempt_coordinator")
    expect("coordinator (null): the same overlap unflagged is refused",
           any("coordinator cap" in b for b in check_plan(ov3)), str(check_plan(ov3)))

    # 3c. after-edges by predecessor stage (owner ruling, mandate 6715477401): a
    # refused or refuted predecessor never lands, so its dependent is released;
    # a deferred one is postponed, not done, so its dependent (and that one's
    # own) stays held behind it, unscheduled. refused and deferred are closed
    # groups (roster_lib.CLOSED_STAGES), never scheduled; refuted stays open.
    for st in ("refused", "deferred"):
        rf = mk([fx("R10-A"), fx("R10-X", stage=st), fx("R10-Y", after=["R10-X"]),
                 fx("R10-Z", after=["R10-Y"])])
        held = st == "deferred"
        expect(f"{st}: the group is closed and not scheduled",
               rf["groups"]["R10-X"]["done"] and rf["groups"]["R10-X"]["start"] is None,
               str(rf["groups"]["R10-X"]))
        expect(f"{st}: its dependent is " + ("held behind it, with its own dependent"
                                             if held else "released, not held"),
               (rf["groups"]["R10-Y"]["start"] is None
                and rf["groups"]["R10-Y"].get("held_behind") == "R10-X"
                and rf["groups"]["R10-Z"].get("held_behind") == "R10-X") if held
               else (rf["groups"]["R10-Y"]["start"] == iso(start, 0)
                     and not rf["groups"]["R10-Y"].get("held_behind")),
               str({n: (g["start"], g.get("held_behind")) for n, g in rf["groups"].items()}))
        in_plan = {g for w in rf["waves"] for g in w["groups"]}
        in_plan |= {g for b in rf["batches"] for g in b["groups"]}
        expect(f"{st}: a held dependent is in no wave and no batch (build_plan drops "
               "`held` from the open set; null: the released set is scheduled)",
               ("R10-Y" in in_plan and "R10-Z" in in_plan) if not held
               else not ({"R10-Y", "R10-Z"} & in_plan) and "R10-A" in in_plan,
               str(sorted(in_plan)))
    rt = mk([fx("R10-A"), fx("R10-X", stage="refuted"), fx("R10-Y", after=["R10-X"])])
    expect("refuted: the group is still scheduled and its dependent is released",
           not rt["groups"]["R10-X"]["done"] and rt["groups"]["R10-X"]["start"] is not None
           and rt["groups"]["R10-Y"]["start"] == iso(start, 0)
           and rt["groups"]["R10-Y"]["after"] == [], str(rt["groups"]))
    rq = mk([fx("R10-A", after=["R10-Q"]), fx("R10-Q", stage="queued")])
    expect("after (null): a queued predecessor still gates its dependent",
           rq["groups"]["R10-A"]["after"] == ["R10-Q"]
           and rq["groups"]["R10-A"]["start"] > rq["groups"]["R10-Q"]["start"],
           str(rq["groups"]))
    # 3d. merge resolution of the two rulings: a discharged group (proposal 1)
    # behind a deferred one is closed work, so it is neither held nor holds its
    # own dependent; one unmarked carry (null) leaves it open and held, and
    # its dependent held in turn.
    co = {"res": {"commit": "0123abcd"}, "carry": ["x [moved: A]"]}
    dh = mk([fx("R10-A"), fx("R10-X", stage="deferred"),
             fx("R10-D", stage="carries-open", after=["R10-X"], **co),
             fx("R10-N", after=["R10-D"])])
    expect("discharged behind deferred: closed and not held; its dependent released",
           dh["groups"]["R10-D"].get("discharged") is True
           and not dh["groups"]["R10-D"].get("held_behind")
           and not dh["groups"]["R10-N"].get("held_behind")
           and dh["groups"]["R10-N"]["start"] == iso(start, 0)
           and dh["summary"]["groups_discharged"] == 1 and check_plan(dh) == [],
           str({n: (g["start"], g.get("held_behind"), g.get("discharged"))
                for n, g in dh["groups"].items()}))
    co["carry"] = co["carry"] + ["w"]
    dn = mk([fx("R10-A"), fx("R10-X", stage="deferred"),
             fx("R10-D", stage="carries-open", after=["R10-X"], **co),
             fx("R10-N", after=["R10-D"])])
    expect("discharged behind deferred (null): one unmarked carry keeps it held, "
           "and its dependent held behind the deferral",
           dn["groups"]["R10-D"].get("held_behind") == "R10-X"
           and dn["groups"]["R10-N"].get("held_behind") == "R10-X"
           and dn["summary"]["groups_discharged"] == 0,
           str({n: (g["start"], g.get("held_behind")) for n, g in dn["groups"].items()}))


    # 4. stamp cadence counts groups, not pull requests (carry 9)
    cad = [fx("P1", stage="done"), fx("P2", stage="done"), fx("Q1"), fx("Q2")]
    ck = mk(cad, since_tag=["P1", "P1", "P2"])    # P1 took two pull requests
    expect("cadence: the patch stamp lands at the 3rd GROUP, carrying it, not the 3rd PR",
           [s["carries"] for s in ck["stamps"]] == [["P1", "P2", "Q1"], ["Q2"]]
           and ck["summary"]["production_since_tag"] == 2, str(ck["stamps"]))
    expect("cadence (null): no credit leaves two groups and no patch stamp",
           [s["carries"] for s in mk(cad)["stamps"]] == [["Q1", "Q2"]], "")
    G4 = groups_of({"groups": [fx("R10-X"), fx("R10-Y"), fx("R10-Z"), fx("R10-W", kind="instrument")]})
    code, note = "+x = 1\n-x = 0\n", "+# a new note\n-\n+   \n"
    got = production_groups_since([
        {"subject": "R10-X (#1)", "diff": code}, {"subject": "R10-X part 2 (#2)", "diff": code},
        {"subject": "R10-Y (#3)", "diff": note}, {"subject": "R10-Z (#4)", "diff": code},
        {"subject": "R10-W (#5)", "diff": code}], G4)
    expect("cadence: production groups since the tag, once each; comment-only and "
           "instrument groups do not count", got == ["R10-X", "R10-Z"], str(got))

    # 5. evidence liveness (carries 0, 3)
    wip = [fx("W", stage="in-progress"), fx("O")]
    nev = mk(wip, evidence={"refs": set(), "prs": []})
    lev = mk(wip, evidence={"refs": {"handoff/w"}, "prs": []})
    expect("evidence: an in-progress group with no ref is pending",
           nev["groups"]["W"]["live"] is False and nev["generated"]["demoted_live"] == ["W"],
           str(nev["groups"]["W"]))
    expect("evidence (null): with a handoff ref it is live",
           lev["groups"]["W"]["live"] is True and lev["generated"]["demoted_live"] == [],
           str(lev["groups"]["W"]))
    def strip_g(p):
        q = json.loads(json.dumps(p))
        q["generated"].pop("liveness"), q["generated"].pop("demoted_live")
        return json.dumps(q, sort_keys=True)
    expect("evidence (null): no-evidence reproduces the stage-word plan byte-for-byte",
           strip_g(mk(wip)) == strip_g(lev) and mk(wip) == mk(wip, evidence=None), "plans differ")
    one = dict(caps, slots=1)
    held = [fx("H", "L", stage="carries-open", carry=["c"] * 3), fx("F", "XL")]
    hp = mk(held, caps_=one, evidence={"refs": set(), "prs": [{"headRefName": "fixer/h"}]})
    hn = mk(held, caps_=one, evidence={"refs": set(), "prs": []})
    expect("evidence: a carries-open group with an open PR starts at t=0 as live",
           hp["groups"]["H"]["start"] == iso(start, 0) and hp["groups"]["H"]["live"] is True,
           str(hp["groups"]["H"]))
    expect("evidence (null): the same group with no PR waits behind the full slot",
           hn["groups"]["H"]["live"] is False, str(hn["groups"]["H"]))
    pr_ = mk([fx("N", "M")], evidence={"refs": set(), "prs": [{"headRefName": "fixer/n"}]})
    expect("evidence: an open PR credits the live fraction (0.7 x 4 h)",
           pr_["groups"]["N"]["duration_minutes"] == 168, str(pr_["groups"]["N"]))
    ds = mk([fx("F", "XL"), fx("D", "M")], caps_=one,
            evidence={"refs": {"design/d"}, "prs": []})
    expect("evidence: a design-only group starts at t=0 at its full duration, no credit",
           ds["groups"]["D"]["start"] == iso(start, 0) and ds["groups"]["D"]["live"] is False
           and ds["groups"]["D"]["duration_minutes"] == 240
           and ds["groups"]["D"].get("design_only") is True, str(ds["groups"]["D"]))

    # 6. the binding chain beside the critical path
    bind = mk([fx("C", "L"), fx("BA"), fx("BB", after=["BA"])], caps_=one)
    bw = mk([fx("C", "L"), fx("BA"), fx("BB", after=["BA"])])
    expect("binding: the slot-delayed predecessor is a link, with the critical-path slack",
           bind["critical_path"] == ["C"] and bind["binding"]["chain"] == ["BA", "BB"]
           and bind["groups"]["BA"]["start"] > iso(start, 0)
           and bind["binding"]["critical_path_slack_hours"] > 0
           and "uncalibrated" in bind["binding"]["slot_sensitivity"], str(bind["binding"]))
    expect("binding (null): with a slot for each the chain is the critical path",
           bw["binding"]["chain"] == bw["critical_path"], str(bw["binding"]))

    # 7. inflow
    infl = [fx("A"), fx("B", after=["A"])]
    i0 = mk(infl, dur=dict(durations, inflow_groups_per_hour=0))
    expect("inflow: 0 reproduces the plan byte-for-byte, no arrivals",
           i0 == mk(infl) and "expected_arrivals" not in i0["summary"], "")
    i4 = mk(infl, dur=dict(durations, inflow_groups_per_hour=0.4))
    want = round(0.4 * i4["summary"]["wall_hours"], 2)
    expect("inflow: above 0 adds expected_arrivals and changes nothing scheduled",
           abs(i4["summary"]["expected_arrivals"]["groups"] - want) <= 0.01
           and sched(i4) == sched(mk(infl)), str(i4["summary"].get("expected_arrivals")))

    # 8. repair round 4: one pin per reviewer mutant, each with its null control
    ovs = mk([fx("L1", stage="in-progress"), fx("L2", "XL", stage="in-progress"), fx("X3"),
              fx("CP1", "XL"), fx("CP2", after=["CP1"])], caps_=dict(caps, slots=2))
    expect("overflow slots do not hold a real slot: the waiting group takes the slot a "
           "finished group frees while the exempt one still runs",
           ovs["groups"]["CP1"].get("exempt") is True
           and ovs["groups"]["X3"]["start"] == ovs["groups"]["L1"]["finish"]
           and ovs["groups"]["X3"]["start"] < ovs["groups"]["CP1"]["finish"],
           str({n: (g["start"], g["finish"]) for n, g in ovs["groups"].items()}))
    expect("overflow (null): no exempt group, the waiter also starts at the freed slot",
           mk([fx("L1", stage="in-progress"), fx("L2", "XL", stage="in-progress"), fx("X3")],
              caps_=dict(caps, slots=2))["groups"]["X3"]["start"]
           == ovs["groups"]["L1"]["finish"], "")
    pcs = mk(base_g + [cat, fx("R10-AFTER", after=["R10-CATALOG-PR"]),
                       fx("STAMP-ROUND-MAJOR"), fx("R10-ZED", after=["STAMP-ROUND-MAJOR"])])
    expect("post-closure: what follows an owner step, and what follows the closing-stamp "
           "group, is post-closure too",
           pcs["summary"]["post_closure"] == ["R10-AFTER", "R10-CATALOG-PR", "R10-ZED"]
           and check_plan(pcs) == [], str(pcs["summary"]["post_closure"]) + str(check_plan(pcs)))
    expect("post-closure (null): a group after nothing post-closure is in the round",
           "R10-B" not in pcs["summary"]["post_closure"]
           and "STAMP-ROUND-MAJOR" not in pcs["summary"]["post_closure"], "")
    early = json.loads(json.dumps(pc))
    early["groups"]["R10-CATALOG-PR"]["start"] = iso(start, 0)
    expect("--check refuses a post-closure group starting before the round-close stamp",
           any("starts before the round-close stamp" in b for b in check_plan(early)),
           str(check_plan(early)))
    carried = json.loads(json.dumps(pc))
    carried["stamps"][0]["carries"] = carried["stamps"][0]["carries"] + ["R10-CATALOG-PR"]
    expect("--check refuses a post-closure group named in a stamp's carries",
           any("is in a stamp's carries" in b for b in check_plan(carried)),
           str(check_plan(carried)))
    expect("--check counts the credited groups among the merges (null: plan holds)",
           check_plan(ck) == [], str(check_plan(ck)))
    nonprod = mk(cad + [fx("R10-W", kind="instrument", stage="done")],
                 since_tag=["R10-W", "P1", "P1", "P2"])
    expect("cadence: a non-production done group in the tag range earns no credit",
           nonprod["summary"]["production_since_tag"] == 2
           and [s["carries"] for s in nonprod["stamps"]] == [["P1", "P2", "Q1"], ["Q2"]],
           str(nonprod["stamps"]))
    open_c = mk(cad, since_tag=["Q1"])
    expect("cadence: a credited group still open is counted once, in the plan",
           open_c["summary"]["production_since_tag"] == 0
           and [s["carries"] for s in open_c["stamps"]] == [["Q1", "Q2"]], str(open_c["stamps"]))
    pd = [fx("P%d" % i, stage="done") for i in range(1, 5)] + [fx("Q1"), fx("Q2")]
    cutd = mk(pd, since_tag=["P1", "P2", "P3", "P4"])
    expect("cadence: a patch stamp cuts `every` groups and keeps the rest for the next",
           [s["carries"] for s in cutd["stamps"]] == [["P1", "P2", "P3"], ["P4", "Q1", "Q2"], []],
           str([s["carries"] for s in cutd["stamps"]]))
    bj = mk([fx("A"), fx("B", "XL"), fx("C", after=["A", "B"])])
    expect("binding: the chain walks back through the LAST-finishing predecessor",
           bj["binding"]["chain"] == ["B", "C"], str(bj["binding"]["chain"]))
    expect("binding (null): the early predecessor is not the link",
           "A" not in bj["binding"]["chain"], "")
    szs = sorted(float(v) for v in durations["sizes_hours"].values())
    ea = i4["summary"]["expected_arrivals"]
    expect("inflow: arrivals are priced at the median size",
           abs(ea["work_hours"] - ea["groups"] * szs[len(szs) // 2]) <= 0.05
           and szs[0] != szs[len(szs) // 2], str(ea))
    expect("live refs: a ls-remote listing yields branch names without refs/heads/, tags dropped",
           parse_live_refs("abc\trefs/heads/fixer/w\nabc\trefs/tags/v1\n\n") == {"fixer/w"},
           str(parse_live_refs("abc\trefs/heads/fixer/w\nabc\trefs/tags/v1\n")))
    pp = mk(base_g + [cat, fx("R10-CAT2", kind="owner-step", lane="Docs", after=["R10-B"],
                              res={"next_step": "after the round-close stamp"})])
    expect("post-closure groups are outside the in-flight peak (null: none, same peak)",
           pp["summary"]["peak_in_flight"] == p0["summary"]["peak_in_flight"]
           and pp["summary"]["peak_working"] == p0["summary"]["peak_working"],
           str((pp["summary"]["peak_in_flight"], p0["summary"]["peak_in_flight"])))
    # liveness: a stage-word live group with a design ref only is design-only, uncredited
    wd = mk([fx("W", "M", stage="in-progress"), fx("O")],
            evidence={"refs": {"design/w"}, "prs": []})
    wn = mk([fx("W", "M"), fx("O")], evidence={"refs": {"design/w"}, "prs": []})
    expect("evidence: a stage-live group with only a design ref gets no live credit",
           wd["groups"]["W"]["live"] is False and wd["groups"]["W"].get("design_only") is True
           and wd["groups"]["W"]["duration_minutes"] == wn["groups"]["W"]["duration_minutes"],
           str(wd["groups"]["W"]))
    # --since-tag on main's real merge subjects and merge diffs (carry 9)
    G9 = groups_of({"groups": [fx("R10-STORE"), fx("R10-STORE-RACES", res={}, branch="fix/r10-store-races"),
                               fx("R10-W", kind="instrument")]})
    real = [{"subject": "Merge pull request #12 from tvofi/fix/r10-store-races", "diff": code},
            {"subject": "Merge pull request #13 from tvofi/fix/r10-w", "diff": code},
            {"subject": "Merge pull request #14 from tvofi/fix/unrelated", "diff": code}]
    expect("since-tag: a real-shaped merge subject names its group by the topic branch",
           production_groups_since(real, G9) == ["R10-STORE-RACES"],
           str(production_groups_since(real, G9)))
    expect("since-tag (null): the same merges with no code change credit nothing",
           production_groups_since([dict(c, diff=note) for c in real], G9) == [], "")
    parts = [{"subject": "Merge pull request #15 from tvofi/fix/r10-store-p2", "diff": code},
             {"subject": "Merge pull request #16 from tvofi/fix/r10-store-p3", "diff": code},
             {"subject": "Merge pull request #17 from tvofi/fix/r10-store-races-p2", "diff": code},
             {"subject": "Merge pull request #18 from tvofi/fix/r10-storey", "diff": code},
             {"subject": "Merge pull request #19 from tvofi/fix/unrelated-p2", "diff": code}]
    expect("since-tag: part branches credit their group by the longest roster topic they extend, once each",
           production_groups_since(parts, G9) == ["R10-STORE", "R10-STORE-RACES"],
           str(production_groups_since(parts, G9)))
    expect("since-tag (null): an unrelated topic and a non-boundary prefix (r10-storey) credit nothing",
           production_groups_since(parts[3:], G9) == [], str(production_groups_since(parts[3:], G9)))
    sq = production_groups_since([{"subject": "R10-STORE-RACES (#20)", "diff": code}], G9)
    expect("since-tag: a squash subject naming R10-STORE-RACES credits it, not the shorter R10-STORE",
           sq == ["R10-STORE-RACES"], str(sq))
    with throwaway_git_environ(), tempfile.TemporaryDirectory() as gd:
        def g(*a):
            return subprocess.run(["git", "-C", gd, *a], capture_output=True, text=True)
        throwaway_git_init(gd, "-q", "-b", "main")
        (Path(gd) / "custom_components").mkdir()
        (Path(gd) / "custom_components" / "a.py").write_text("x = 0\n")
        g("add", "-A"), g("commit", "-q", "-m", "base"), g("tag", "v0")
        g("checkout", "-q", "-b", "fix/r10-store-races")
        (Path(gd) / "custom_components" / "a.py").write_text("x = 1\n")
        g("commit", "-q", "-am", "work")
        g("checkout", "-q", "main")
        (Path(gd) / "other.txt").write_text("m\n")
        g("add", "-A"), g("commit", "-q", "-m", "mainline")
        g("merge", "-q", "--no-ff", "-m", "Merge pull request #12 from tvofi/fix/r10-store-races",
          "fix/r10-store-races")
        got = production_groups_since(git_commits_since_tag(gd), G9)
        expect("since-tag: a clean merge's change is read against its first parent",
               got == ["R10-STORE-RACES"], str(got))

    # --measure-sizes hands --sizes-via to size_durations.run: the module is a
    # stub in sys.modules, so the mutation copies (no size_durations.py beside
    # them) run this arm too, and no read reaches the network.
    import types
    from unittest import mock
    vias = []
    stub = types.SimpleNamespace(
        SINCE="2026-10-12", DEFAULT_PERCENTILE=0.5,
        run=lambda *a, **k: vias.append((a[7:8] or [k.get("via", "graphql")])[0])
        or {"sizes_hours": {}})
    with mock.patch.dict(sys.modules, {"size_durations": stub}), \
            tempfile.TemporaryDirectory() as td:
        for via in ("rest", "graphql"):
            main(["--measure-sizes", "--sizes-via", via,
                  "--out-durations", os.path.join(td, "d.json")])
    expect("--measure-sizes --sizes-via rest reaches size_durations.run as via=rest "
           "(null: graphql)", vias == ["rest", "graphql"], str(vias))

    gate = gate_minutes(durations)
    want_gate = 50.0 + 22.0 + 27.0 * (1.0 + 0.04)
    expect("the gate price includes the cancelled-leg rerun",
           abs(gate - want_gate) < 1e-6, f"{gate} != {want_gate}")

    # Each arm above must go red when its subject is deleted. A self-test that
    # survives its own removal is the defect the arms exist to catch. The
    # harness first proves the copy is sound UNMUTATED -- with durations.json
    # beside it, because the self-test's cycle arm runs the command and would
    # otherwise exit 1 on a missing file and make every mutant pass for free --
    # then applies one deletion inside the named function and requires the
    # copy's own --self-test to exit non-zero.
    if not os.environ.get("REPLAN_MUTATION_CHILD"):
        import shutil

        def _def_span(src: str, marker: str) -> tuple[int, int]:
            """[start, end) of the def/class at `marker`, by indentation."""
            start = src.index(marker)
            line_start = src.rfind("\n", 0, start) + 1
            indent = start - line_start
            pos = src.find("\n", start) + 1
            while pos < len(src):
                nxt = src.find("\n", pos)
                line = src[pos:nxt if nxt >= 0 else len(src)]
                if line.strip().startswith(("def ", "class ")) and (
                        len(line) - len(line.lstrip())) <= indent:
                    return start, pos
                if nxt < 0:
                    break
                pos = nxt + 1
            return start, len(src)

        def _m(*parts: str) -> str:
            """A target assembled at run time.

            The table must not contain the literal it searches for: with the
            whole string written here, `str.index` found this list (which sits
            before `_ingest_check_runs` in the file) instead of the production
            line, and the earliest-attempt mutation changed nothing (2026-10-20
            review, mutation target).
            """
            return "".join(parts)

        mutations = [
            ("earliest-attempt",
             _m("def _ingest_check_runs(", "lines, want) -> dict:"),
             _m("if prev is None or started ", '< prev["started"]:'), "if prev is None:"),
            ("coordinator-cap",
             _m("def pick(candidates, ", "now: int, cap_exempt: bool = False):"),
             _m("if coord[n] and n not in started ", "and cc >= coord_cap and not cap_exempt:"),
             "if False:"),
            ("tier-critical-path",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             "    if on_cp:", "    if False:"),
            ("top-tier-unordered",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("n = pick(sorted(ready", "), t)"), "n = pick(sorted(ready & crit or ready), t)"),
            ("tier-production",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m('return TIER_PRODUCTION_WORK, "production ', '(work_class)"'),
             'return TIER_INSTRUMENT, "x"'),
            ("tier-hotfix",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             "    if roster_lib.is_hotfix(group):", "    if False:"),
            ("tier-outside",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             "    if roster_lib.is_outside(group):", "    if False:"),
            ("tier-main",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m('if k == "main" or "-MAIN-FIX" in g ', 'or "-MAIN-RED" in g:'), "if False:"),
            ("tier-saving-instrument",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m("if savings is not None and savings >= ", "SAVING_TIER_HOURS:"), "if False:"),
            ("tier-savings",
             _m("def dispatch_key(n: str, ", "tier: dict, savings: dict,"),
             _m('sav = (-savings[n] if n in savings ', 'else float("inf"))'), "sav = (0.0)"),
            ("cp-overflow-start",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("n = pick(sorted(x for x in ready ", "if x in crit), t, cap_exempt=True)"),
             "n = pick(sorted(x for x in ready if False), t, cap_exempt=True)"),
            ("lane-stem-boundary",
             _m("def roster_lane(group: ", "dict) -> str:"),
             'g == p or g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS',
             "g.startswith(p) for p in INSTRUMENT_NAME_STEMS"),
            ("coordinator-cp-exempt",
             _m("def pick(candidates, ", "now: int, cap_exempt: bool = False):"),
             _m("and cc >= coord_cap ", "and not cap_exempt:"), "and cc >= coord_cap:"),
            ("coordinator-cp-flag",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "exempt_coord.add(n)", "pass"),
            ("check-ignores-flag",
             _m("def check_plan(plan: ", "dict) -> list:"),
             'g.get("coordinator") and not g.get("exempt_coordinator")]',
             'g.get("coordinator")]'),
            ("edge-releases-ruled",
             _m("def dependency_graph(G: ", "dict, legacy: dict | None = None) -> tuple[dict, set, set]:"),
             "if a in open_ and roster_lib.gates(G[a]):", "if a in open_:"),
            ("deferred-holds-dependent",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "held = roster_lib.held_behind_deferred(live)", "held = {}"),
            ("discharged-not-held",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("held = roster_lib.held_behind_deferred(", "live)"),
             "held = roster_lib.held_behind_deferred(G)"),
            ("overflow-exempt",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "exempt.add(n)", "pass"),
            ("absorbed-done",
             _m("def is_done(group: ", "dict) -> bool:"),
             "return not roster_lib.is_open(group)",
             'return (group.get("resume") or {}).get("stage") in ("done", "rca-done")'),
            ("absorbed-advisory",
             _m("def absorbers(G: ", "dict) -> dict:"),
             _m('out[n] = (into, None if into else', ''), 'out[n] = (into, None if True else'),
            ("post-closure-excluded",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "open_ = open_all - post", "open_ = open_all"),
            ("post-closure-after-stamp",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             'max([stamps[-1]["at"]] + [', "max([0] + ["),
            ("stamp-credit-groups",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "dict.fromkeys(since_tag or [])", "(since_tag or [])"),
            ("comment-only-diff",
             _m("def substantive(diff: ", "str) -> bool:"),
             'not body.startswith("#")', "True"),
            ("stamp-credit-lane",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "lane[n] in PRODUCTION and n in done]", "n in done]"),
            ("stamp-credit-done",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "lane[n] in PRODUCTION and n in done]", "lane[n] in PRODUCTION]"),
            ("since-tag-merge-topic",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             "n = by_topic[max(hit, key=len)] if hit else None", "n = None"),
            ("since-tag-first-parent",
             _m("def git_commits_since_tag(", "repo: str) -> list:"),
             '"diff", "-U0", f"{sha}^1", sha,', '"show", "-U0", sha, "--format=",'),
            ("since-tag-part-branch",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             'topic == t or topic.startswith(t + "-")]', 'topic == t]'),
            ("since-tag-part-boundary",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             'topic.startswith(t + "-")]', 'topic.startswith(t)]'),
            ("since-tag-part-longest",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             "n = by_topic[max(hit, key=len)] if hit else None", "n = by_topic[min(hit, key=len)] if hit else None"),
            ("since-tag-squash-longest",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             "n = max(named, key=len) if named else None", "n = min(named, key=len) if named else None"),
            ("since-tag-once",
             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
             "return list(out)", "return [n for n in out] + list(out)"),
            ("evidence-design-uncredited",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "live = (live - demoted - ev_design) | ev_live\n",
             "live = (live - demoted) | ev_live | ev_design\n"),
            ("evidence-demotes",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "demoted = {n for n in live if topic_evidence", "demoted = {n for n in set() if topic_evidence"),
            ("evidence-pr-live",
             _m("def topic_evidence(group: ", "dict, evidence: dict) -> str | None:"),
             'return "pr"', 'return "work"'),
            ("binding-start",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "node = max(merged_t, key=", "node = min(merged_t, key="),
            ("binding-slack",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "closure / 60.0 - cp_hours", "0.0"),
            ("inflow-zero",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "if inflow > 0:", "if inflow >= 0:"),
            ("inflow-rate",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             "n_exp = inflow * closure_at / 60.0", "n_exp = 1.0"),
            ("height-tiebreak",
             _m("def dispatch_key(n: str, ", "tier: dict, savings: dict,"),
             _m("sav, -height[n], ", "-dur_min[n], n)"), "sav, n)"),
            ("started-past-cap",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("for n in sorted((n for n in ready ", "if n in started), key=priority):"),
             "for n in []:"),
            ("settled-held",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("settled = {n for n in open_ if n not in live ", "and dur_h[n] == 0}"),
             "settled = set()"),
            ("start-reason-slot",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m('return f"slot cap {slots}: ', 'waited behind higher-priority groups"'),
             'return "ready"'),
            ("planned-dispatch-cap",
             _m("def check_plan(plan: dict) ", "-> list:"),
             "        if cur >= slots:", "        if False:"),
            ("held-carry-model",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m('if stage == HELD_STAGE and ', 'durations.get("carries_per_part"):'), "if False:"),
            ("live-review-stage",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m("if is_live and stage in REVIEW_STAGES ", "and size in first:"), "if False:"),
            ("rounds-explicit",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m("hours = work + (rounds - 1) * ", 'float(durations["round_hours"])'),
             "hours = work"),
            ("absorbed-carries",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m('if extra > 0 and ', 'durations.get("carry_hours"):'), "if False:"),
            ("class-cell",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m("work = float(cell.get(cls, ", "first[size]))"), "work = float(first[size])"),
            ("appended-carries-open",
             _m("def held_open(group: dict, ", "durations: dict, pending: list)"),
             _m("added = sum(1 for i in pending ", "if i >= cut)"), "added = 0"),
            ("held-open-pending",
             _m("def held_open(group: dict, ", "durations: dict, pending: list)"),
             _m("return len(pending), ", 'f"{len(pending)} carries'),
             'return len(group.get("carry") or []), f"{len(pending)} carries'),
            ("held-measured-pending",
             _m("def held_open(group: dict, ", "durations: dict, pending: list)"),
             _m('then = min(int(rec["open"]), ', "sum(1 for i in pending if i < cut))"),
             'then = int(rec["open"])'),
            ("absorbed-pending",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m("extra = len(pending) ", "- float("), 'extra = len(group.get("carry") or []) - float('),
            ("pending-left-out",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m('left_out = f", {left} marked carries ', 'left out" if left else ""'), 'left_out = ""'),
            ("legacy-threaded",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m('roster_path or roster_ref or "<fixture>", ', "legacy)"),
             'roster_path or roster_ref or "<fixture>")'),
            ("caps-owner-default",
             _m("def cli_caps(", "args) -> dict:"),
             _m('"slots": DEFAULT_CAPS["slots"] if args.slots ', 'is None else args.slots,'),
             '"slots": 6 if args.slots is None else args.slots,'),
            ("model-monotone",
             _m("def model_refusals(model: ", "dict) -> list:"),
             "        if hb < ha:", "        if False:"),
            # (`live-same-key` retired 2026-11-01: every started group now
            # starts at once, so the order of the t==0 admission picks only a
            # slot index; `started-past-cap` pins the admission itself.)
            ("savings-validated",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("if isinstance(s, bool) or not isinstance(s, ", "(int, float)):"), "if False:"),
            ("size-refusal",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             "if size not in sizes:", "if False:"),
            ("stamp-cadence",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("while len(carry) >= ", "every:"), "while False:"),
            ("review-min",
             _m("def group_hours(group: dict, ", "durations: dict,"),
             _m("left_rounds = max(rounds - 1, ", "1.0)"), "left_rounds = rounds"),
            ("wall-hours",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m('"wall_hours": round(closure_at ', "/ 60.0, 2),"),
             '"wall_hours": round(closure / 60.0, 2),'),
            ("closure-conditions",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m('"closure_conditions": list(', 'CLOSURE_CONDITIONS),'),
             '"closure_conditions": [],'),
            ("closure-later-of",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("closure_at = max([stamps[-1][\"at\"]] + ", "list(post_end.values()))"),
             "closure_at = max([stamps[-1][\"at\"]] + [])"),
            ("closure-check-later-of",
             _m("def check_plan(plan: dict", ") -> list:"),
             _m("closure = max([mins(x[\"at\"]) for x in close_stamps] + ", "post_fin"),
             "closure = max([mins(x[\"at\"]) for x in close_stamps] + []"),
            ("round-close-version",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("stamps.append({\"version\": closing, ", "\"at\": closure + closure_lead,"),
             _m("stamps.append({\"version\": bump(version, ", "patch), \"at\": closure + closure_lead,")),
            ("round-close-check",
             _m("def check_plan(plan: dict", ") -> list:"),
             _m("elif closes[0][\"version\"] != ", "want:"), "elif False:"),
            ("round-close-last",
             _m("def check_plan(plan: dict", ") -> list:"),
             _m(" or plan[\"stamps\"][-1] is not ", "closes[0]:"), ":"),
            ("round-close-stray-kind",
             _m("def check_plan(plan: dict", ") -> list:"),
             _m("if s[\"kind\"] not in (\"patch\", ", "ROUND_CLOSE)]"),
             _m("if s[\"kind\"] not in (\"patch\", ", "\"minor\", ROUND_CLOSE)]")),
            ("round-n-required",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("roster_path: str = \"\", *, ", "round_n: int, since_tag"),
             _m("roster_path: str = \"\", *, ", "round_n: int = 10, since_tag")),
            ("round-from-roster",
             _m("def main(argv=", "None) -> int:"),
             _m("round_n = roster_lib.roster_round(", "src)"), "round_n = 99"),
            ("ci-formula",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("ci = round((len(batch_rows) + len(stamps)) ", "* gate_report, 1)"),
             "ci = round(len(batch_rows) * gate_report, 1)"),
            ("freshness",
             _m("def stale_reason(plan: dict, ", "repo: str, ref: str | None = None,"),
             _m("if have != ", "want:"), "if False:"),
            ("held-subtraction",
             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
             _m("open_ = open_ ", "- set(held)"), "open_ = open_"),
            ("gate-cancellation",
             _m("def gate_minutes(durations: ", "dict) -> float:"),
             _m("return fast + clo + ana * ", "(1.0 + p_cancel)"), "return fast + clo + ana"),
        ]
        source = Path(__file__).read_text(encoding="utf-8")
        seat = str(Path(__file__).resolve().parent.parent / "audit" / "seat")
        env = {**os.environ, "REPLAN_MUTATION_CHILD": "1", "REPLAN_SEAT_DIR": seat}
        with tempfile.TemporaryDirectory() as td:
            shutil.copy2(Path(__file__).resolve().parent / "durations.json",
                         Path(td) / "durations.json")
            base = Path(td) / "unmutated.py"
            base.write_text(source, encoding="utf-8")
            rc = subprocess.run([sys.executable, "-I", str(base), "--self-test"],
                                capture_output=True, text=True, env=env).returncode
            print(f"  null control: unmutated copy rc={rc}")
            expect("the unmutated copy's self-test exits 0 (null control)",
                   rc == 0, f"rc={rc}")
            for name, marker, old, new in mutations:
                copy = Path(td) / f"{name.replace('-', '_')}.py"
                start, end = _def_span(source, marker)
                chunk = source[start:end]
                if chunk.count(old) != 1:
                    expect(f"self-test fails when {name} is deleted", False,
                           f"anchor {old!r} occurs {chunk.count(old)} times in "
                           f"{marker!r}")
                    continue
                copy.write_text(source[:start] + chunk.replace(old, new, 1)
                                + source[end:], encoding="utf-8")
                rc = subprocess.run([sys.executable, "-I", str(copy), "--self-test"],
                                    capture_output=True, text=True, env=env).returncode
                print(f"  mutation {name}: {old!r} -> rc={rc}")
                expect(f"self-test fails when {name} is deleted", rc != 0, f"rc={rc}")

    print(f"self-test: {len(failures)} failed")
    return 1 if failures else 0


# ------------------------------------------------------------------ durations

def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def _ingest_check_runs(lines, want) -> dict:
    """The EARLIEST completed attempt per context name on one commit.

    `gh api ... --paginate` lists check runs newest first, so the first line
    for a name is usually the RERUN, not the first attempt. Keeping the
    earliest `started_at` is the invariant: a median over gates counts each
    tree's first attempt once, and a cancelled first attempt stays cancelled
    (its rerun is what `cancelled_rate` prices, not a replacement result).
    """
    best = {}
    for line in lines:
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        name, job, began, ended, concl = parts
        if name not in want or began in ("", "null") or ended in ("", "null"):
            continue
        started = dt.datetime.fromisoformat(began.replace("Z", "+00:00"))
        finished = dt.datetime.fromisoformat(ended.replace("Z", "+00:00"))
        prev = best.get(name)
        if prev is None or started < prev["started"]:
            best[name] = {
                "job": int(job),
                "minutes": round((finished - started).total_seconds() / 60.0, 1),
                "conclusion": concl,
                "started": started,
            }
    return best


def measure_ci(repo: str, repo_owner: str, merges: int) -> dict:
    """Measure the three contexts over the last `merges` main merges.

    The one network path. Paginated `gh api` output is JSON per page, so the
    pages are projected with `-q` rather than concatenated and parsed -- a
    commit with more than 100 check runs made the concatenated read invalid.
    """
    log = subprocess.run(
        ["git", "-C", repo, "log", "origin/main", "--first-parent", "--merges",
         f"-{merges}", "--format=%H"],
        capture_output=True, text=True, check=True).stdout.split()
    want = ("fast (3.14)", "closures", "Analyze (python)")
    # One row per (commit, context), its FIRST attempt, kept with its
    # conclusion. The cancelled rate's denominator is the Analyze population,
    # never the complete-sample population: a commit whose Analyze leg was
    # cancelled at its cap and whose fast leg had not finished at measurement
    # time is a cancelled Analyze run, and sampling only complete triples drops
    # it -- the rate that did so under-priced one cancelled leg per 26 runs
    # instead of per 29 (2026-10-20 review, measurement-defect).
    rows: dict = {w: [] for w in want}
    samples = []
    for sha in log:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo_owner}/commits/{sha}/check-runs", "--paginate",
             "-q", ".check_runs[] | [.name,.id,.started_at,.completed_at,.conclusion] | @tsv"],
            capture_output=True, text=True)
        if out.returncode:
            continue
        got = _ingest_check_runs(out.stdout.strip().split("\n"), want)
        for name, row in got.items():
            rows[name].append((row["minutes"], row["conclusion"]))
        if len(got) == 3:
            samples.append({"sha": sha, **{
                n: {k: v for k, v in r.items() if k != "started"}
                for n, r in got.items()}})

    def stat(xs):
        xs = sorted(m for m, _ in xs)
        q = lambda p: xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]
        return {"median_minutes": round(median(xs), 1), "iqr": [q(.25), q(.75)],
                "min_minutes": min(xs), "max_minutes": max(xs), "n": len(xs)}

    ci = {w: stat(rows[w]) for w in want}
    ana_rows = rows["Analyze (python)"]
    cancelled = sum(1 for _, concl in ana_rows if concl == "cancelled")
    ci["Analyze (python)"]["cancelled_rate"] = round(cancelled / max(1, len(ana_rows)), 3)
    ci["Analyze (python)"]["cancelled"] = cancelled
    ci["Analyze (python)"]["cap_minutes"] = 30
    return {
        "provenance": {
            "instrument": (f"gh api repos/{repo_owner}/commits/<sha>/check-runs "
                           "over the last main merges"),
            "merges": len(samples),
            "measured_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "ci": ci,
        "samples": samples[:12],
    }


# ----------------------------------------------------------------------- main

def cli_caps(args) -> dict:
    """The caps a command-line replan draws at, and whose they are."""
    given = [k for k in ("slots", "seats") if getattr(args, k) is not None]
    return {
        "slots": DEFAULT_CAPS["slots"] if args.slots is None else args.slots,
        "seats": DEFAULT_CAPS["seats"] if args.seats is None else args.seats,
        "coordinator_cap": args.coordinator_cap, "stamp_every": args.stamp_every,
        "provenance": (f"--{' --'.join(given)} given on the command line" if given
                       else CAPS_PROVENANCE),
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Mechanical replanner for the wave roster.")
    p.add_argument("--repo", default=".", help="repository to read the roster from")
    p.add_argument("--roster-ref", default=None,
                   help="default: origin/handoff/audit-r10-roster to build; "
                        "the plan's own generated.roster_ref to --check")
    p.add_argument("--roster-path", default=None)
    p.add_argument("--roster-file", default=None, help="a fixture roster (self-tests)")
    p.add_argument("--durations", default=None,
                   help="default: tools/plan/durations.json beside this script")
    p.add_argument("--start", default=None, help="ISO 8601 UTC; default: now, to the minute")
    p.add_argument("--out", default="plan.json")
    p.add_argument("--check", action="store_true", help="validate a plan; exit 1 on a violation")
    p.add_argument("--plan", default=None, help="plan to check (default: --out)")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--measure-ci", action="store_true", help="re-measure durations from CI")
    p.add_argument("--measure-sizes", action="store_true",
                   help="re-measure the size, rounds and held-stage model from merged PRs "
                        "(tools/plan/size_durations.py) into --out-durations")
    p.add_argument("--sizes-csv", default=None, help="--measure-sizes: write the raw rows here")
    p.add_argument("--prs-cache", default=None, help="--measure-sizes: read or write the fetch")
    p.add_argument("--sizes-via", choices=("graphql", "rest"), default="graphql",
                   help="--measure-sizes: the PR read (size_durations.READS)")
    p.add_argument("--out-durations", default=None)
    p.add_argument("--live-refs", default=None,
                   help="a saved `git ls-remote --heads` listing: liveness by evidence")
    p.add_argument("--in-flight", default=None,
                   help="JSON list of open pull requests (number, headRefOid, headRefName, isDraft)")
    p.add_argument("--since-tag", action="store_true",
                   help="credit the stamp cadence with production groups merged since the last tag "
                        "(comment-only diffs ignored)")
    p.add_argument("--repo-owner", default="tvofi/heatpump_optimizer")
    p.add_argument("--merges", type=int, default=30)
    p.add_argument("--slots", type=int, default=None,
                   help=f"default {DEFAULT_CAPS['slots']}, the owner's cap (CAPS_PROVENANCE)")
    p.add_argument("--seats", type=int, default=None,
                   help=f"default {DEFAULT_CAPS['seats']} (CAPS_PROVENANCE)")
    p.add_argument("--coordinator-cap", type=int, default=DEFAULT_CAPS["coordinator_cap"])
    p.add_argument("--stamp-every", type=int, default=DEFAULT_CAPS["stamp_every"])
    p.add_argument("--batch-window-minutes", type=int, default=None)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return max(selftest_model(), selftest())

    here = Path(__file__).resolve().parent
    durations_path = Path(args.durations) if args.durations else here / "durations.json"

    if args.measure_sizes:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import size_durations  # the one network edge of the size model, loaded only here
        target = Path(args.out_durations) if args.out_durations else durations_path
        old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
        got = size_durations.run(args.repo, args.roster_ref, args.repo_owner, size_durations.SINCE,
                                 args.prs_cache, args.sizes_csv,
                                 size_durations.DEFAULT_PERCENTILE, args.sizes_via)
        target.write_text(json.dumps({**old, **got}, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
        print(f"measured sizes {got['sizes_hours']} -> {target}")
        return 0

    if args.measure_ci:
        measured = measure_ci(args.repo, args.repo_owner, args.merges)
        target = Path(args.out_durations) if args.out_durations else durations_path
        old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
        merged = {**old, **measured}
        for k, v in (("sizes_hours", {}), ("live_remaining_fraction", 0.7),
                     ("batch_window_minutes", 20), ("stamp_lead_minutes", 60),
                     ("closure_lead_minutes", 120)):
            merged.setdefault(k, old.get(k, v))
        target.write_text(json.dumps(merged, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"measured {measured['provenance']['merges']} merged trees -> {target}")
        return 0

    if args.check:
        plan_path = Path(args.plan or args.out)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        bad = check_plan(plan)
        stale = stale_reason(plan, args.repo, args.roster_ref, args.roster_path)
        if stale:
            bad.append(f"freshness: {stale}")
        if bad:
            print(f"REFUSED: {len(bad)} violation(s) in {plan_path}", file=sys.stderr)
            for b in bad:
                print(f"  {b}", file=sys.stderr)
            return 1
        print(f"PLAN OK: {plan_path}")
        return 0

    durations = json.loads(durations_path.read_text(encoding="utf-8"))
    caps = cli_caps(args)
    if args.batch_window_minutes is not None:
        durations["batch_window_minutes"] = args.batch_window_minutes
    if args.start:
        start = dt.datetime.strptime(args.start.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
    else:
        start = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0, tzinfo=None)
    try:
        version = (Path(args.repo) / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        version = "0.0.0"
    roster, ref, blob = load_roster(args.repo, args.roster_ref, args.roster_path,
                                    args.roster_file)
    # The roster's own path, so a refusal can name the file it read rather
    # than the ref it came through (`load_roster` resolves it but returns only
    # the blob). A fixture names itself.
    src = args.roster_file
    if not src:
        try:
            src = roster_lib.roster_path(args.repo, ref, args.roster_path)
        except roster_lib.RosterNotFound:
            src = args.roster_path or ""
    # The round the closure stamp closes is the one the roster's path names,
    # read as `stamp.py --round-close` reads it (`roster_lib.roster_round`).
    try:
        round_n = roster_lib.roster_round(src)
    except roster_lib.RosterNotFound as exc:
        raise PlanError(f"no round for the round-close stamp: {exc}") from exc
    evidence = None
    if args.live_refs or args.in_flight:
        evidence = {
            "refs": (parse_live_refs(Path(args.live_refs).read_text(encoding="utf-8"))
                     if args.live_refs else set()),
            "prs": (json.loads(Path(args.in_flight).read_text(encoding="utf-8"))
                    if args.in_flight else []),
        }
    since_tag = (production_groups_since(git_commits_since_tag(args.repo), groups_of(roster))
                 if args.since_tag else None)
    # The carries a group still owes are `roster_lib.pending_carries`, which
    # needs the round's cut-over (a `--roster-file` copy keeps its round's).
    try:
        legacy = roster_lib.read_legacy(
            args.repo, f"{roster_lib.ROSTERS_DIR}/{src.rsplit('/', 1)[-1]}")
    except roster_lib.RosterNotFound as exc:
        raise PlanError(f"the carry cut-over: {exc}") from exc
    plan = build_plan(roster, durations, caps, start, version, ref, blob,
                      roster_path=src, round_n=round_n, since_tag=since_tag, evidence=evidence,
                      legacy=legacy)
    bad = check_plan(plan)
    if bad:
        print("the model produced a violating plan; refusing to write it", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        return 1
    Path(args.out).write_text(json.dumps(plan, indent=1, sort_keys=True) + "\n",
                              encoding="utf-8")
    print_waves(plan)
    return 0


def print_waves(plan: dict) -> None:
    print(f"{'wave':>4}  {'opens (UTC)':<17} {'drains (UTC)':<17} {'stamp':<9} groups")
    for w in plan["waves"]:
        print(f"{w['wave']:>4}  {w['opens']:<17} {w['drains']:<17} "
              f"{(w['stamp'] or '—'):<9} {', '.join(g[4:] for g in w['groups'])}")
    s = plan["summary"]
    g = plan["generated"]
    ic = g.get("inherited_coordinator") or {}
    print(f"summary: closure {s['closure']} | wall {s['wall_hours']} h | "
          f"CI {s['ci_minutes']} min | batches {s['batches']} | stamps {s['stamps']} "
          f"| roster {g.get('roster_blob', '')[:12] or 'unpinned'} "
          f"| inherited coordinator {len(ic.get('groups') or [])}/{ic.get('cap')} "
          f"({len(g.get('inherited_dependency_violations') or [])} inherited "
          f"dependency inversion(s))")
    for n, a in (plan.get("absorbed") or {}).items():
        print(f"absorbed: {n} -> {a['into'] or '?'}" + (f"  {a['advisory']}" if a["advisory"] else ""))
    if s.get("post_closure"):
        print(f"post-closure (after the round-close stamp, in no stamp): "
              f"{', '.join(s['post_closure'])} until {s['post_closure_finish']}")
    b = plan.get("binding") or {}
    print(f"binding chain: {' -> '.join(b.get('chain') or [])} | critical path "
          f"{b.get('critical_path_hours')} h, slack {b.get('critical_path_slack_hours')} h | "
          f"slot sensitivity {b.get('slot_sensitivity')}")
    print(f"production groups since the last tag: {s.get('production_since_tag', 0)}")
    if s.get("expected_arrivals"):
        print(f"expected arrivals: {s['expected_arrivals']['groups']} groups, "
              f"{s['expected_arrivals']['work_hours']} work-hours")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PlanError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        sys.exit(2)
