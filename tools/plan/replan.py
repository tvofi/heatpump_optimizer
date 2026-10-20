#!/usr/bin/env python3
"""The round's schedule model: one mechanical replan, run at a wave edge.

    python3 tools/plan/replan.py --out /tmp/plan.json
    python3 tools/plan/replan.py --check --plan /tmp/plan.json
    python3 tools/plan/replan.py --self-test
    python3 tools/plan/replan.py --measure-ci

What it reads
    `--roster-ref` (default `origin/handoff/audit-r10-roster`) and the newest
    `dev/programme/rosters/wave-r<N>-groups.json` in that ref's tree, read with
    `git show`; `tools/plan/durations.json` (the measured, cached durations);
    `VERSION` from the checkout. No network and no GitHub state: the same
    inputs produce byte-identical output. `--measure-ci` is the one network
    path and it only rewrites the durations file, never a plan.

The schedule
    List scheduling over the roster's `after` edges with six pull-request
    slots, longest-remaining-path first. A group holds a slot from its start
    (the PR opens) to its finish (the PR merges); at most two in-flight groups
    may touch `coordinator.py`. Groups whose fixer is already working (stage
    `in-progress`) were dispatched before the replan: up to six start at the
    replan instant in height order, and the rest wait for a slot like any
    pending group.

    Merges are batched. A finished group waits up to `batch_window_minutes`
    for a partner; then the batch lands and its slots free. One batch pays one
    gate run (`fast (3.14)` + `closures` + `Analyze (python)`), so a batch of k
    shares that cost where k separate merges pay it k times. The window is the
    wall-time price of that sharing and the summary reports it.

    A patch stamp is cut once `stamp_every` production groups have merged
    since the last one. A stamp never blocks a dispatch; it pays its own gate
    run, because `stamp.py` pushes to main.

Why it checks what it checks
    A schedule that violates a cap is not a plan. `--check` refuses (exit 1)
    on: more than `slots` in flight at any instant; more than `seats` working
    at any instant; more than `coordinator_cap` in flight touching
    `coordinator.py`; a dependency that finishes after its dependent starts
    (an inherited in-progress group that started before its dependency is
    recorded in `generated.inherited_dependency_violations`, not refused --
    the replan cannot undo it); a stamp cadence breach; a wave opening while
    the open-PR cap is full; a summary that disagrees with the groups it
    summarises. `--self-test` plants each violation and proves the refusal
    fires.

plan.json shape
    schema; generated {roster_ref, roster_blob, start, version, caps,
    inherited_dependency_violations}; summary {closure, wall_hours, ci_minutes,
    batches, stamps, ...}; critical_path [group...]; groups {name: {wave,
    start, finish, slot, duration_minutes, size, lane, level, live, inherited,
    coordinator, batch, stamp, after}}; waves [{wave, opens, drains, stamp,
    batch, groups}]; batches [{id, at, groups}]; stamps [{version, at, kind,
    batch, carries}].
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

SELF = "tools/plan/replan.py"

# Production lanes cut a stamp. Instrument, Replay and Docs work does not, on
# the owner's cadence ("a patch stamp after roughly five production groups").
LANES = ("Learners", "Core model", "Product UX", "Replay", "Instruments", "Docs")
PRODUCTION = ("Learners", "Core model", "Product UX")

# A fixer already working. `queued` is not working: the plan dispatches it.
LIVE_STAGES = ("in-progress", "fixing", "review", "in-review")

DEFAULT_CAPS = {
    "slots": 6,              # open pull requests; the owner's cap
    "seats": 8,              # fixers working; never binds while slots < seats
    "coordinator_cap": 2,    # open pull requests touching coordinator.py
    "stamp_every": 5,        # production groups per patch stamp
}


class PlanError(Exception):
    """An input the model refuses: a cycle, an unknown edge, a bad roster."""


# --------------------------------------------------------------------- roster

def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


_ROSTER_NAME = re.compile(r"\Awave-r(\d+)-groups\.json\Z")


def newest_roster(paths) -> str | None:
    found = [(int(m.group(1)), p) for p in paths
             if (m := _ROSTER_NAME.match(p.rsplit("/", 1)[-1]))]
    return max(found)[1] if found else None


def load_roster(repo: str, ref: str | None = None, path: str | None = None,
                file: str | None = None) -> tuple[dict, str, str]:
    """(roster, roster_ref, blob) -- `file` wins for a self-test fixture;
    otherwise the roster is read at `ref` with `git show`, never from disk."""
    if file:
        return json.loads(Path(file).read_text(encoding="utf-8")), file, ""
    if not ref:
        ref = "origin/handoff/audit-r10-roster"
    if not path:
        listing = _git(repo, "ls-tree", "--name-only", ref, "dev/programme/rosters/")
        if listing.returncode:
            raise PlanError(f"cannot list dev/programme/rosters/ at {ref}: "
                            f"{(listing.stderr or listing.stdout).strip()[:200]}")
        path = newest_roster(listing.stdout.split())
        if not path:
            raise PlanError(f"no dev/programme/rosters/wave-r<N>-groups.json at {ref}")
    shown = _git(repo, "show", f"{ref}:{path}")
    if shown.returncode:
        raise PlanError(f"no roster at {ref}:{path}: "
                        f"{(shown.stderr or shown.stdout).strip()[:200]}")
    blob = _git(repo, "rev-parse", f"{ref}:{path}")
    return json.loads(shown.stdout), ref, (blob.stdout.strip() if blob.returncode == 0 else "")


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


# ------------------------------------------------------------------- schedule

def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
               version: str, roster_ref: str = "", roster_blob: str = "") -> dict:
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
    live = set()
    dur_h = {}
    for n in open_:
        stage = (G[n].get("resume") or {}).get("stage")
        is_live = stage in LIVE_STAGES
        if is_live:
            live.add(n)
        base = float(size_hours[G[n].get("size") or "M"])
        dur_h[n] = base * live_fraction if is_live else base
    dur_min = {n: max(1, int(round(dur_h[n] * 60))) for n in open_}
    height = heights(deps, dur_h, order)
    lvl = levels(deps, order)

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
    inherited = set()           # live groups dispatched before the replan instant
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
        return next((s for s in range(slots) if s not in used), None)

    def in_flight_coord() -> int:
        return sum(1 for n in list(running) + list(finished) if coord[n])

    def pick(candidates, now: int):
        """Highest remaining path first; coordinator cap on planned starts."""
        cc = in_flight_coord()
        best = None
        for n in candidates:
            if coord[n] and n not in inherited and cc >= coord_cap:
                continue
            key = (-height[n], -dur_min[n], n)
            if best is None or key < best[0]:
                best = (key, n)
        return None if best is None else best[1]

    t = 0
    guard = 0
    while pending or running or finished or ready:
        guard += 1
        if guard > 20000:
            raise PlanError("scheduler did not terminate; the graph is unsound")

        # 1. Admit live groups first (they were dispatched before the replan),
        #    then fill every free slot with the best ready group.
        live_ready = sorted((n for n in ready if n in live), key=lambda n: (-height[n], n))
        while live_ready and free_slot() is not None:
            n = live_ready.pop(0)
            s = free_slot()
            start_t[n] = t
            slot_of[n] = s
            work_end[n] = t + dur_min[n]
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
                    if all(a in merged_t for a in deps[c]):
                        ready.add(c)

    if pending or ready or running or finished:
        raise PlanError(f"scheduled {len(merged_t)} of {len(open_)} open groups")

    closure = max(merged_t.values(), default=0)
    # The last fewer-than-`every` production groups are not a patch stamp of
    # their own: the minor stamp closes the programme and carries them. A
    # second push there would pay a gate run to bump a version the minor bump
    # replaces hours later.
    minor = bump(version, patch, minor=True)
    for c in carry:
        stamp_by_group[c] = minor
    stamps.append({"version": minor, "at": closure + closure_lead,
                   "carries": list(carry), "kind": "minor", "batch": None})

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
    ci = round((len(batch_rows) + len(stamps)) * gate, 1)

    groups_out = {}
    for n in sorted(G):
        if n in done:
            groups_out[n] = {
                "wave": None, "start": None, "finish": None, "slot": None,
                "duration_minutes": 0, "size": G[n].get("size"), "lane": lane[n],
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
            "level": lvl[n],
            "live": n in live,
            "inherited": n in inherited,
            "coordinator": coord[n],
            "batch": batch_of[n],
            "stamp": stamp_by_group.get(n),
            "after": sorted(deps[n]),
            "done": False,
        }

    peak_flight, peak_coord = peak_concurrency(groups_out, start)
    peak_working = peak_seats(groups_out, start)
    cp = critical_path(deps, dur_h, order)
    inherited_deps = [
        {"group": n, "after": g, "dependent_start": iso(start, start_t[n]),
         "dependency_finish": iso(start, merged_t[g])}
        for n in sorted(inherited) for g in deps[n]
        if merged_t[g] > start_t[n]
    ]
    plan = {
        "schema": 1,
        "generated": {
            "roster_ref": roster_ref,
            "roster_blob": roster_blob,
            "start": iso(start, 0),
            "version": version,
            "durations": durations.get("provenance") or {},
            "caps": {
                "slots": slots, "seats": seats, "coordinator_cap": coord_cap,
                "stamp_every": every, "batch_window_minutes": batch_window,
            },
            "inherited_dependency_violations": inherited_deps,
        },
        "summary": {
            "closure": iso(start, closure),
            "closure_stamp": stamps[-1]["version"],
            "wall_hours": round(closure / 60.0, 2),
            "ci_minutes": ci,
            "gate_minutes": round(gate, 1),
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


def bump(version: str, n: int, minor: bool = False) -> str:
    maj, mi, pa = (int(x) for x in version.lstrip("v").split(".")[:3])
    return f"v{maj}.{mi + 1}.0" if minor else f"v{maj}.{mi}.{pa + n}"


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
        if planned_only and g.get("inherited"):
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
    #    inherited (already running) dependent is recorded, not refused.
    for n, g in groups.items():
        for a in g.get("after") or []:
            if a in groups and mins(groups[a]["finish"]) > mins(g["start"]) \
                    and not g.get("inherited"):
                bad.append(f"dependency: {a} finishes {groups[a]['finish']} "
                           f"after {n} starts {g['start']}")

    # 2. six in flight at any instant (open pull requests), and eight working
    events = []
    for n, g in groups.items():
        events.append((mins(g["start"]), 1, n))
        events.append((mins(g["finish"]), -1, n))
    events.sort(key=lambda e: (e[0], e[1]))
    cur = 0
    for t, delta, _ in events:
        cur += delta
        if cur > slots:
            bad.append(f"in flight: {cur} groups at {iso(start, t)} (cap {slots})")
    work = []
    for n, g in groups.items():
        work.append((mins(g["start"]), 1, n))
        work.append((mins(g["start"]) + g["duration_minutes"], -1, n))
    work.sort(key=lambda e: (e[0], e[1]))
    curw = 0
    for t, delta, _ in work:
        curw += delta
        if curw > seats:
            bad.append(f"seats: {curw} groups working at {iso(start, t)} (cap {seats})")

    # 3. coordinator cap: at most two in flight, counting planned starts.
    coord = [(n, g) for n, g in groups.items() if g.get("coordinator")]
    for t, _, _ in events:
        curc = sum(1 for n, g in coord
                   if not g.get("inherited")
                   and mins(g["start"]) <= t < mins(g["finish"]))
        if curc > coord_cap:
            bad.append(f"coordinator cap: {curc} touching coordinator.py at "
                       f"{iso(start, t)} (cap {coord_cap})")
            break

    # 4. a wave opens only while the open-PR cap has room
    for w in plan.get("waves", []):
        t = mins(w["opens"])
        cur = sum(1 for g in groups.values()
                  if mins(g["start"]) <= t < mins(g["finish"]))
        if cur > slots:
            bad.append(f"wave {w['wave']} opens at {w['opens']} with {cur} in "
                       f"flight (cap {slots})")

    # 5. stamp cadence: every `every` production merges cuts one patch stamp;
    #    the last fewer-than-`every` ride the one minor stamp that closes the
    #    programme
    produced = [n for n, g in sorted(
        ((n, g) for n, g in groups.items() if g.get("lane") in PRODUCTION),
        key=lambda x: (mins(x[1]["finish"]), x[0]))]
    patch_stamps = [s for s in plan.get("stamps", []) if s["kind"] == "patch"]
    minor = [s for s in plan.get("stamps", []) if s["kind"] == "minor"]
    if len(minor) != 1:
        bad.append(f"stamp cadence: {len(minor)} minor stamps, expected one")
    if len(patch_stamps) != len(produced) // every:
        bad.append(f"stamp cadence: {len(patch_stamps)} patch stamps for "
                   f"{len(produced)} production merges at a cadence of {every}")
    covered: list = []
    for s in patch_stamps:
        covered.extend(s["carries"])
        if len(s["carries"]) != every:
            bad.append(f"stamp cadence: {s['version']} carries "
                       f"{len(s['carries'])} production groups, not {every}")
    if minor:
        covered.extend(minor[0]["carries"])
        if len(minor[0]["carries"]) > every:
            bad.append(f"stamp cadence: the minor stamp carries "
                       f"{len(minor[0]['carries'])} production groups")
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
    return bad


# ------------------------------------------------------------------ self-test

def selftest() -> int:
    caps = dict(DEFAULT_CAPS)
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

    plan = build_plan(roster, durations, caps, start, "v1.0.0")
    again = build_plan(roster, durations, caps, start, "v1.0.0")
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
        build_plan(cyc, durations, caps, start, "v1.0.0")
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
        cycf = Path(td) / "cyc.json"
        cycf.write_text(json.dumps(cyc), encoding="utf-8")
        rc = subprocess.run([sys.executable, "-I", __file__, "--roster-file", str(cycf),
                             "--out", str(Path(td) / "p.json"),
                             "--start", "2026-01-05T00:00:00Z"],
                            capture_output=True).returncode
        expect("the command exits 2 on a dependency cycle", rc == 2, f"rc={rc}")

    # planted: an over-cap model input (7 slots' worth of live groups at t=0)
    many = {"groups": [
        {"group": f"L{i}", "size": "S", "lane": "Core model", "kind": "defect",
         "after": [], "resume": {"stage": "in-progress"}} for i in range(7)
    ]}
    p2 = build_plan(many, durations, caps, start, "v1.0.0")
    expect("live admission never exceeds the slot cap",
           p2["summary"]["peak_in_flight"] <= caps["slots"],
           str(p2["summary"]["peak_in_flight"]))
    expect("the excess live group is queued, not invented",
           p2["summary"]["inherited_in_progress"] == caps["slots"],
           str(p2["summary"]["inherited_in_progress"]))

    print(f"self-test: {len(failures)} failed")
    return 1 if failures else 0


# ------------------------------------------------------------------ durations

def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


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
    rows: dict = {w: [] for w in want}
    samples = []
    for sha in log:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo_owner}/commits/{sha}/check-runs", "--paginate",
             "-q", ".check_runs[] | [.name,.id,.started_at,.completed_at,.conclusion] | @tsv"],
            capture_output=True, text=True)
        if out.returncode:
            continue
        got = {}
        for line in out.stdout.strip().split("\n"):
            if not line:
                continue
            name, job, began, ended, concl = line.split("\t")
            if name in want and began not in ("", "null") and ended not in ("", "null"):
                a = dt.datetime.fromisoformat(began.replace("Z", "+00:00"))
                b = dt.datetime.fromisoformat(ended.replace("Z", "+00:00"))
                mins = round((b - a).total_seconds() / 60.0, 1)
                rows[name].append(mins)
                got[name] = {"job": int(job), "minutes": mins, "conclusion": concl}
        if len(got) == 3:
            samples.append({"sha": sha, **got})

    def stat(xs):
        xs = sorted(xs)
        q = lambda p: xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]
        return {"median_minutes": round(median(xs), 1), "iqr": [q(.25), q(.75)],
                "min_minutes": min(xs), "max_minutes": max(xs), "n": len(xs)}

    ci = {w: stat(rows[w]) for w in want}
    ana = [s["Analyze (python)"] for s in samples]
    cancelled = sum(1 for s in ana if s["conclusion"] == "cancelled")
    ci["Analyze (python)"]["cancelled_rate"] = round(cancelled / max(1, len(ana)), 3)
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

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Mechanical replanner for the wave roster.")
    p.add_argument("--repo", default=".", help="repository to read the roster from")
    p.add_argument("--roster-ref", default="origin/handoff/audit-r10-roster")
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
    p.add_argument("--out-durations", default=None)
    p.add_argument("--repo-owner", default="tvofi/heatpump_optimizer")
    p.add_argument("--merges", type=int, default=30)
    p.add_argument("--slots", type=int, default=DEFAULT_CAPS["slots"])
    p.add_argument("--seats", type=int, default=DEFAULT_CAPS["seats"])
    p.add_argument("--coordinator-cap", type=int, default=DEFAULT_CAPS["coordinator_cap"])
    p.add_argument("--stamp-every", type=int, default=DEFAULT_CAPS["stamp_every"])
    p.add_argument("--batch-window-minutes", type=int, default=None)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return selftest()

    here = Path(__file__).resolve().parent
    durations_path = Path(args.durations) if args.durations else here / "durations.json"

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
        if bad:
            print(f"REFUSED: {len(bad)} violation(s) in {plan_path}", file=sys.stderr)
            for b in bad:
                print(f"  {b}", file=sys.stderr)
            return 1
        print(f"PLAN OK: {plan_path}")
        return 0

    durations = json.loads(durations_path.read_text(encoding="utf-8"))
    caps = {
        "slots": args.slots, "seats": args.seats,
        "coordinator_cap": args.coordinator_cap, "stamp_every": args.stamp_every,
    }
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
    plan = build_plan(roster, durations, caps, start, version, ref, blob)
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
    print(f"summary: closure {s['closure']} | wall {s['wall_hours']} h | "
          f"CI {s['ci_minutes']} min | batches {s['batches']} | stamps {s['stamps']}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PlanError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        sys.exit(2)
