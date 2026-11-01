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
    within a tier. The priority (tvofi 2026-10-26) is derived at every replan:
    tier 0 is `critical_path()`'s output for the roster graph as it stands
    (never a stored list), tier 1 a production-lane group, tier 2 everything
    else, ranked within tier 2 by the roster's `savings` field (absent sorts
    last). Height breaks ties within a tier. A group holds a slot from its
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

# The owner's dispatch priority (tvofi 2026-10-26): the critical path first,
# then production, then everything else by the savings it carries. The tiers
# are derived from the roster graph at every replan; none is stored.
TIER_CRITICAL, TIER_PRODUCTION, TIER_OTHER = 0, 1, 2

# The kind of the one stamp that closes the programme: the round's major.
ROUND_CLOSE = "round-close"

# A fixer already working. `queued` is not working: the plan dispatches it.
LIVE_STAGES = ("in-progress", "fixing", "review", "in-review")

DEFAULT_CAPS = {
    "slots": 16,             # open pull requests: the owner's cap since 2026-10-31
    "seats": 16,             # fixers working: one per open pull request
    "coordinator_cap": 2,    # open pull requests touching coordinator.py
    "stamp_every": 5,        # production groups per patch stamp
}
#: Where DEFAULT_CAPS' slots and seats come from, recorded in every plan that
#: uses them: a plan drawn at a cap nobody chose must say whose cap it is.
CAPS_PROVENANCE = ("tvofi 2026-10-31 (#201 comment 6544047621): 16 open pull "
                   "requests; replan.py DEFAULT_CAPS")


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


def is_done(group: dict) -> bool:
    return (group.get("resume") or {}).get("stage") in ("done", "rca-done")


def roster_lane(group: dict) -> str:
    """The lane a group is drawn in and counted under for the stamp cadence.

    Ported from the out-of-tree renderer this replaces, which was the only
    definition: `kind` first, then the group's own name.
    """
    g = group["group"]
    k = group.get("kind")
    if g in ("R10-ARCH-DOCS", "R10-I5-DOCS"):
        return "Docs"
    if k in ("instrument", "policy") or g.startswith(
            ("R10-TICK", "R10-TRAIN", "R10-REF", "R10-D15", "R10-PREPR", "R10-GATE",
             "R10-STALE", "R10-PRE-EDIT", "R10-POLICY", "R10-I1", "R10-ARCHSCORE",
             "R10-STRUCTURE", "R10-BRIEFS")):
        return "Instruments"
    if "REPLAY" in g:
        return "Replay"
    if g in ("R10-VENT-DETECTOR", "R10-NIGHT-FOLDS", "R10-TRUST-RELATIVE",
             "R10-RATIO-ANCHOR", "R10-RATIO-SITES", "R10-LEARNER-ETA",
             "R10-HEAT-METER", "R10-COP-GATE"):
        return "Learners"
    if k == "owner" or g in ("R10-UX-HEALTH", "R10-CONFIGFLOW-PAGES", "R10-DEEPLINK-CENSUS"):
        return "Product UX"
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
    if roster_lane(group) in ("Instruments", "Docs") or k in ("rca", "policy", "tooling"):
        return "instrument"
    return "production"


def touches_coordinator(group: dict) -> bool:
    files = list(group.get("hot_files") or []) + list(group.get("files") or [])
    return any(f.endswith("coordinator.py") for f in files)


# ----------------------------------------------------------------------- graph

def dependency_graph(G: dict) -> tuple[dict, set, set]:
    """(open deps per open group, open set, done set).

    An `after` edge to a done group is satisfied and drops out. An `after`
    naming no group in the roster is refused: silently dropping it would make
    a dependency look met when the roster has a typo.
    """
    done = {n for n, g in G.items() if is_done(g)}
    open_ = set(G) - done
    deps = {}
    for n in open_:
        out = []
        for a in G[n].get("after") or []:
            if a not in G:
                raise PlanError(f"{n}: after-edge names no group: {a}")
            if a in open_:
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


#: The owner's priority order (standing directive, 2026-10-30), as tiers:
#: 1 main (a red main or a main fix), 2 the critical path and hotfixes (user-
#: reported production findings), 3 production work and instruments saving
#: SAVING_TIER_HOURS or more, 4 every other instrument, ranked by its savings.
TIER_MAIN, TIER_URGENT, TIER_PRODUCTION_WORK, TIER_INSTRUMENT = 1, 2, 3, 4
SAVING_TIER_HOURS = 12.0


def dispatch_tier(group: dict, on_cp: bool, savings: float | None) -> tuple[int, str]:
    """(tier, the roster fields that decided it) for one open group.

    Read from the roster alone: `kind` "main" or a `-MAIN-FIX`/`-MAIN-RED`
    name is main; `on_cp` (`critical_path()`'s output, never a stored list),
    a `kind` "bug" (the user-reported finding) or a HOTFIX-named production
    group is urgent; `work_class` production, or an instrument whose
    `savings` is at least SAVING_TIER_HOURS, is tier 3; else tier 4.
    """
    g, k = group["group"], group.get("kind")
    if k == "main" or "-MAIN-FIX" in g or "-MAIN-RED" in g:
        return TIER_MAIN, f"main (kind {k!r}, name)"
    cls = work_class(group)
    if on_cp:
        return TIER_URGENT, "critical path"
    if k == "bug" or "HOTFIX" in g and cls == "production":
        return TIER_URGENT, f"hotfix (kind {k!r}, name)"
    if cls == "production":
        return TIER_PRODUCTION_WORK, "production (work_class)"
    if savings is not None and savings >= SAVING_TIER_HOURS:
        return TIER_PRODUCTION_WORK, f"instrument saving {savings:g} h >= {SAVING_TIER_HOURS:g}"
    if savings is None:
        return TIER_INSTRUMENT, f"{cls}; savings not recorded on the roster, ranked last"
    return TIER_INSTRUMENT, f"{cls} saving {savings:g} h"


def dispatch_key(n: str, tier: dict, crit: set, savings: dict, height: dict,
                 dur_min: dict) -> tuple:
    """The dispatch order, lowest first: tier, the critical path first within
    it, then (tier 4 only) savings descending with an unrecorded savings last,
    then the tie-break that predates the tiers: height, duration, name. It is
    a pure function of the plan's own fields (`plan.json` records it per
    group as `sort_key`), so a reader can re-derive the order from the plan.
    """
    t = tier[n]
    sav = (-savings[n] if n in savings else float("inf")) if t == TIER_INSTRUMENT else 0.0
    return (t, 0 if n in crit else 1, sav, -height[n], -dur_min[n], n)


# ------------------------------------------------------------- duration model

HELD_STAGE = "carries-open"


def held_open(group: dict, durations: dict) -> tuple[int, str]:
    """(open carries, how known) for a carries-open group. The measured
    count (`held_open_carries`, `tools/plan/size_durations.py`) plus every
    carry appended since; a group it never measured counts every carry."""
    carry = len(group.get("carry") or [])
    rec = (durations.get("held_open_carries") or {}).get(group["group"])
    if rec is None:
        return carry, f"{carry} carries, none measured as answered"
    added = max(0, carry - int(rec["carries"]))
    return int(rec["open"]) + added, (f"{rec['open']} open carries at measurement"
                                      + (f" + {added} appended since" if added else ""))


def group_hours(group: dict, durations: dict, is_live: bool, where: str) -> tuple[float, str]:
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
    """
    n, size, cls = group["group"], group.get("size") or "M", work_class(group)
    stage = (group.get("resume") or {}).get("stage")
    if stage == HELD_STAGE and durations.get("carries_per_part"):
        k, how = held_open(group, durations)
        parts = math.ceil(k / float(durations["carries_per_part"]))
        return parts * float(durations["carry_part_hours"]), f"{how}: {parts} part(s)"
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
        extra = len(group.get("carry") or []) - float((durations.get("carry_baseline") or {}).get(size, 0))
        if extra > 0 and durations.get("carry_hours"):
            hours += extra * float(durations["carry_hours"])
            why += f" + {extra:g} absorbed carries"
    else:
        hours, why = float(sizes[size]), f"{size}: sizes_hours"
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
    expect("a planned group waits while started groups fill the cap, and names it",
           G["NEW"]["start"] > iso(start, 0) and G["NEW"]["start_reason"].startswith("slot cap 2"),
           G["NEW"])
    expect("a started group waits only for its unmerged after-group, and names it",
           G["DEP"]["start"] == G["NEW"]["finish"]
           and G["DEP"]["start_reason"].startswith("started: its fixer is working; after NEW"),
           G["DEP"])
    expect("the plan with started groups past the cap passes --check", check_plan(pm) == [],
           check_plan(pm))
    bad = json.loads(json.dumps(pm))
    bad["groups"]["NEW"]["start"] = iso(start, 0)
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
    expect("the critical path is tier 2", tier_of(grp("I", kind="instrument"), cp=True) == TIER_URGENT)
    expect("a user-reported bug (hotfix) is tier 2, off the critical path",
           tier_of(grp("R10-HOTFIX-X", kind="bug")) == TIER_URGENT)
    expect("production work is tier 3", tier_of(grp("P")) == TIER_PRODUCTION_WORK)
    expect("an instrument saving 12 h is tier 3, one saving 11 h tier 4",
           tier_of(grp("I", kind="instrument"), sav=12) == TIER_PRODUCTION_WORK
           and tier_of(grp("I", kind="instrument"), sav=11) == TIER_INSTRUMENT)
    why = dispatch_tier(grp("I", kind="instrument"), False, None)[1]
    expect("an instrument with no recorded savings says so", "savings not recorded" in why, why)
    order = {"groups": [
        grp("CPA", "S", "instrument"), grp("CPB", "S", "instrument", after=["CPA"]),
        grp("CPC", "L", "instrument", after=["CPB"]),
        grp("R10-HOTFIX-H", "L", "bug"), grp("PROD", "M"),
        grp("HI", "S", "instrument", savings=9), grp("LO", "S", "instrument", savings=2),
        grp("NONE", "S", "instrument")]}
    po = build_plan(order, M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    seq = sorted((g for g in po["groups"]), key=lambda n: po["groups"][n]["start"])
    expect("dispatch follows the owner's order: critical path, hotfix, production, "
           "instruments by savings, unrecorded savings last",
           seq == ["CPA", "CPB", "CPC", "R10-HOTFIX-H", "PROD", "HI", "LO", "NONE"], seq)
    keys = {n: po["groups"][n]["sort_key"] for n in po["groups"]}
    expect("each group's sort_key is in the plan and orders it the same way",
           sorted(keys, key=lambda n: [float("inf") if k is None else k for k in keys[n]])[0] == "CPA"
           and all(po["groups"][n]["tier_reason"] for n in keys), keys)
    # A critical-path tail (B, 18 h left) against a taller hotfix (H, 24 h):
    # height alone dispatches H first; the owner's order puts B first.
    tail = build_plan({"groups": [grp("A", "L", "instrument"),
                                  grp("B", "S", "instrument", after=["A"]),
                                  grp("H", "M", "bug")]}, M, dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    T = tail["groups"]
    expect("within tier 2 the critical path goes first, even its shorter tail",
           tail["critical_path"] == ["A", "B"] and T["B"]["start"] < T["H"]["start"],
           {n: (T[n]["start"], T[n]["sort_key"]) for n in T})
    tie = build_plan({"groups": [grp("A1", "M"), grp("A2", "S")]}, M,
                     dict(caps1, slots=1), start, "v1.0.0", round_n=2)
    expect("null control: two groups in one tier keep the height tie-break",
           tie["groups"]["A1"]["start"] < tie["groups"]["A2"]["start"],
           {n: tie["groups"][n]["sort_key"] for n in tie["groups"]})

    # 5. caps: a call naming none draws at the owner's, and says so.
    nocaps = cli_caps(parse_args([]))
    expect("a replan given no caps does not draw a 6-slot plan: the owner's 16, with provenance",
           nocaps["slots"] == 16 and nocaps["seats"] == 16
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

def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
               version: str, roster_ref: str = "", roster_blob: str = "",
               roster_path: str = "", *, round_n: int) -> dict:
    closing, why = closure_version(version, round_n)
    if why:
        raise PlanError(f"the round-close stamp: {why}")
    G = groups_of(roster)
    deps, open_, done = dependency_graph(G)
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
    dur_h, basis = {}, {}
    for n in open_:
        dur_h[n], basis[n] = group_hours(G[n], durations, n in live,
                                         roster_path or roster_ref or "<fixture>")
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
        return dispatch_key(n, tier, crit, savings, height, dur_min)

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
    started = live | settled
    released = {n: 0 for n in open_ if not deps[n]}   # n -> when it became ready
    coord_held: set = set()     # ready groups the coordinator cap passed over
    ready = {n for n in open_ if not deps[n]}
    pending = set(open_)
    batch_rows: list = []
    stamps: list = []
    carry: list = []
    stamp_by_group: dict = {}
    patch = 0

    def free_slot() -> int | None:
        # A slot is held from the start to the merge, not to the end of the
        # work: a finished group waiting for its batch still has its PR open.
        used = {s for s, _ in running.values()} | {slot_of[n] for n in finished}
        if len(used) >= slots:
            return None
        return next((s for s in range(slots) if s not in used), None)

    def held_slot() -> int:
        # A started group's slot: the lowest free index, past the cap if the
        # started set alone exceeds it.
        used = {s for s, _ in running.values()} | {slot_of[n] for n in finished}
        return next(s for s in range(len(used) + 1) if s not in used)

    def in_flight_coord() -> int:
        return sum(1 for n in list(running) + list(finished) if coord[n])

    def pick(candidates, now: int):
        """The owner's dispatch priority; coordinator cap on planned starts."""
        cc = in_flight_coord()
        best = None
        for n in candidates:
            if coord[n] and n not in started and cc >= coord_cap:
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
                    if len(carry) >= every:
                        patch += 1
                        v = bump(version, patch)
                        stamps.append({"version": v, "at": t + stamp_lead,
                                       "carries": list(carry), "kind": "patch",
                                       "batch": bid})
                        for c in carry:
                            stamp_by_group[c] = v
                        carry = []
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
    for n in sorted(G):
        if n in done:
            groups_out[n] = {
                "wave": None, "start": None, "finish": None, "slot": None,
                "duration_minutes": 0, "size": G[n].get("size"), "lane": lane[n],
                # A done group is not dispatched, so it carries no tier.
                "tier": None,
                "level": None, "live": False, "inherited": False,
                "coordinator": touches_coordinator(G[n]), "batch": None,
                "stamp": None, "after": [], "done": True,
            }
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

    peak_flight, peak_coord = peak_concurrency(groups_out, start)
    peak_working = peak_seats(groups_out, start)
    inherited_deps = [
        {"group": n, "after": g, "dependent_start": iso(start, start_t[n]),
         "dependency_finish": iso(start, merged_t[g])}
        for n in sorted(inherited) for g in deps[n]
        if merged_t[g] > start_t[n]
    ]
    inherited_coord = sorted(n for n in inherited if coord[n])
    plan = {
        "schema": 1,
        "generated": {
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
            "closure": iso(start, closure),
            "closure_stamp": stamps[-1]["version"],
            "wall_hours": round(closure / 60.0, 2),
            "ci_minutes": ci,
            "gate_minutes": gate_report,
            "batches": len(batch_rows),
            "stamps": len(stamps),
            "groups_total": len(G),
            "groups_done": len(done),
            "groups_open": len(open_),
            "inherited_in_progress": len(inherited),
            "inherited_coordinator": sum(1 for n in inherited if coord[n]),
            "peak_in_flight": peak_flight,
            "peak_working": peak_working,
            "peak_coordinator_in_flight": peak_coord,
        },
        "critical_path": cp,
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
        if g.get("done"):
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
    for n, g in groups.items():
        if g.get("started"):
            continue
        t0 = mins(g["start"])
        cur = sum(1 for m, h in groups.items() if m != n
                  and mins(h["start"]) <= t0 < mins(h["finish"]))
        if cur >= slots:
            bad.append(f"in flight: {n} dispatched at {g['start']} with {cur} "
                       f"groups in flight (cap {slots})")
        curw = sum(1 for m, h in groups.items() if m != n
                   and mins(h["start"]) <= t0 < mins(h["start"]) + h["duration_minutes"])
        if curw >= seats:
            bad.append(f"seats: {n} dispatched at {g['start']} with {curw} "
                       f"groups working (cap {seats})")

    # 3. coordinator cap: at most `coord_cap` PLANNED groups in flight; the
    #    inherited in-progress set is recorded and must match the groups.
    coord = [(n, g) for n, g in groups.items() if g.get("coordinator")]
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
        cur = sum(1 for g in groups.values() if not g.get("started")
                  and mins(g["start"]) <= t < mins(g["finish"]))
        if cur > slots:
            bad.append(f"wave {w['wave']} opens at {w['opens']} with {cur} in "
                       f"flight (cap {slots})")

    # 5. stamp cadence: every `every` production merges cuts one patch stamp;
    #    the last fewer-than-`every` ride the one round-close stamp that closes
    #    the programme, last, at the version `closure_version` assigns
    produced = [n for n, g in sorted(
        ((n, g) for n, g in groups.items() if g.get("lane") in PRODUCTION),
        key=lambda x: (mins(x[1]["finish"]), x[0]))]
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
    closure = max((mins(g["finish"]) for g in groups.values()), default=0)
    if mins(s["closure"]) != closure:
        bad.append("summary: closure is not the last group finish")
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

    plan = build_plan(roster, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
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

    # The owner's dispatch priority (tvofi 2026-10-26): the critical path
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

    # Within tier 2 the roster's `savings` ranks; absent sorts last. CP owns
    # the critical path so HI/LO/NONE are all tier 2. The size order (L, M, S)
    # is the opposite of the savings order, so height alone would invert it.
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
    expect("tier 2 ranks by savings, and absent savings sorts last",
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
            ("coordinator-cap", _m("def pick(candidates, ", "now: int):"),
             _m("if coord[n] and n not in started ", "and cc >= coord_cap:"), "if False:"),
            ("tier-critical-path",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             "    if on_cp:", "    if False:"),
            ("tier-production",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m('return TIER_PRODUCTION_WORK, "production ', '(work_class)"'),
             'return TIER_INSTRUMENT, "x"'),
            ("tier-hotfix",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m('if k == "bug" or "HOTFIX" in g ', 'and cls == "production":'), "if False:"),
            ("tier-main",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m('if k == "main" or "-MAIN-FIX" in g ', 'or "-MAIN-RED" in g:'), "if False:"),
            ("tier-saving-instrument",
             _m("def dispatch_tier(group: dict, ", "on_cp: bool,"),
             _m("if savings is not None and savings >= ", "SAVING_TIER_HOURS:"), "if False:"),
            ("tier-savings",
             _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
             _m('sav = (-savings[n] if n in savings ', 'else float("inf"))'), "sav = (0.0)"),
            ("cp-first-in-tier",
             _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
             _m("(t, 0 if n in crit ", "else 1, sav,"), "(t, 0, sav,"),
            ("height-tiebreak",
             _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
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
             _m("def held_open(group: dict, ", "durations: dict)"),
             _m('added = max(0, carry - int(rec', '["carries"]))'), "added = 0"),
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
             _m("if len(carry) >= ", "every:"), "if False:"),
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
             _m("roster_path: str = \"\", *, ", "round_n: int) -> dict:"),
             _m("roster_path: str = \"\", *, ", "round_n: int = 10) -> dict:")),
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
    p.add_argument("--out-durations", default=None)
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
                                 size_durations.DEFAULT_PERCENTILE)
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
    plan = build_plan(roster, durations, caps, start, version, ref, blob,
                      roster_path=src, round_n=round_n)
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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PlanError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        sys.exit(2)
