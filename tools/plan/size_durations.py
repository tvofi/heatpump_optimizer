#!/usr/bin/env python3
"""Measured group durations by size, kind and review rounds: the plan's size model.

    python3 tools/plan/size_durations.py --csv rows.csv [--prs-cache prs.json] \
        [--out-durations tools/plan/durations.json] [--roster-ref REF]
    python3 tools/plan/replan.py --measure-sizes          # the same, from the planner
    python3 tools/plan/size_durations.py --self-test

What it measures
    Every DONE group of the round's roster (`resume.stage` in
    `roster_lib.DONE_STAGES`) that merged at least one pull request of its own.
    A group's PRs are the union of four reads, each a record the programme
    already keeps: the roster's own pointers (`resume.pr`, `merged in #N` in
    `resume.next_step`/`note`, and `resume.commit` as a merge commit), the
    page renderer's branch-or-title rule (`plan_page.group_of_pr`), and a
    delivery row (`dev/programme/delivery/<N>.md`) naming exactly one group.
    A PR on a shared record branch (`record/...`, `...audit-r<N>-roster...`)
    never answers for a group by branch or title -- a roster batch that names
    a group in its title is a record of that group, not its work -- only by
    a roster pointer.

    start  = the earliest of: a PR's first commit (authored), a PR's creation,
             a `dispatched <ISO>` stamp in the roster's resume text;
    finish = the latest merge among the group's PRs;
    hours  = finish - start, wall clock: work, review rounds, queueing and
             the PR-less handoff wait are all inside it, because the plan's
             slot is all of them.
    rounds = `Fix review: merge|blocked <sha>` verdict comments over the
             group's PRs, one per distinct (verdict, head) pair; blocked counts
             the blocked ones; parts = the number of the group's merged PRs.

    A group with no merged PR (absorbed into another, or closed by a roster
    record) has no duration and is listed under `unmeasured`, never imputed.

The model it writes (`model()`)
    `sizes_hours[size]` is the PERCENTILE (default p75) of the size's measured
    hours over every class; `sizes_by_class_hours[size][class]` the same
    percentile within one class where it has `MIN_CELL` samples, absent
    otherwise (replan.py falls back to the size row). The review rounds are
    modelled explicitly: `review_rounds[size]` holds the mean rounds and
    `round_hours[size]` the median hours one extra round adds, the
    difference between the median of the multi-round groups and of the
    one-round groups divided by their mean extra rounds. `sizes_hours` is
    the measured percentile itself, so the rounds are inside it; the two
    fields say how much of it they are. A size with no sample is absent, and
    replan.py refuses a roster carrying it (a duration is never invented).

The held (carries-open) model
    A carries-open group's main PR has merged; what is left is its unanswered
    carries. `part_rows()` measures every second-or-later part (a group PR
    after its first merge): its hours (first commit to merge) and the roster
    carries its body cites as answered (`cited_carries`). `carry_model()`
    writes `carry_part_hours` (that percentile over the parts) and
    `carries_per_part` (the median cited per part that cites any), so a held
    group's remaining hours are ceil(open / carries_per_part) parts of
    `carry_part_hours`; zero open carries plan zero.

Percentiles are linear between order statistics (numpy's default rule).
The one network read is `fetch()`, GraphQL queries through `gh api graphql`
under `gh_read.retry`'s transient rule; nothing is written to GitHub.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEAT = HERE.parent / "audit" / "seat"
for _p in (str(SEAT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gh_read  # noqa: E402 -- the one read rule
import plan_page  # noqa: E402 -- the one PR-to-group rule (branch, then title)
import replan  # noqa: E402 -- work_class, the plan's class of a group
import roster_lib  # noqa: E402

SIZES = ("XS", "S", "M", "L", "XL")
#: A (size, class) cell below this many samples is not published: its
#: percentile is one or two groups' noise, and replan.py reads the size row.
MIN_CELL = 5
DEFAULT_PERCENTILE = 75
#: The earliest PR creation read: before round 10's first dispatch (the
#: roster's first commit is 2026-10-15), so no round-10 PR is cut off.
SINCE = "2026-10-12"
#: Shared record branches: one branch carries many unrelated PRs.
SHARED_BRANCH = re.compile(r"(^record/|audit-r\d+-roster)")
VERDICT = re.compile(r"^(?:Fix review): (merge|blocked) ([0-9a-f]{7,40})")
MERGED_IN = re.compile(r"merged (?:in |as )?#(\d+)")
DISPATCHED = re.compile(r"dispatched (\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z)")
DELIVERY_ROW = re.compile(r"^- \[#(\d+)\]\([^)]*\) — \*\*[a-z-]+\*\*,? *(.*)$")
#: `carry 3`, `carries 13 and 16`, `carries 6, 7, 14 and 17`, `carries 20-22`,
#: `Carry 11b` (the letter is a sub-item of 11). Never `Carry: R10-X` (a marker).
CARRY_CITE = re.compile(
    r"\bcarr(?:y|ies)\s+\[?(\d+[a-z]?(?:\]?\s*(?:,|and|&|-|–|to)\s*\[?\d+[a-z]?)*)", re.I)
#: A sentence citing a carry as NOT done here. Its numbers are not answered.
NOT_ANSWERED = re.compile(
    r"forward-carr|remainder|not started|not built|still owed|is owed|stands in|"
    r"needs a design|left open|deferred|next part|out of scope|not in this diff|"
    r"stays owed|not this diff|not done|not landed|still open|remains open", re.I)
#: Under `## Forward-carry`, the words of a disposition that closed a carry.
ANSWERED = re.compile(
    r"\bdone\b|built in|landed in|resolved|no (?:code|change) owed|is met|"
    r"already (?:on main|met|built)|closed (?:in|by|here)", re.I)

GRAPHQL = """query($cursor: String) { repository(owner: "%s", name: "%s") {
 pullRequests(states: MERGED, first: 25, after: $cursor,
              orderBy: {field: CREATED_AT, direction: DESC}) {
  pageInfo { hasNextPage endCursor }
  nodes { number title headRefName createdAt mergedAt body mergeCommit { oid }
   commits(first: 1) { nodes { commit { authoredDate } } }
   comments(first: 100) { nodes { author { login } createdAt body } } } } } }"""


def ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------- reads

def fetch(repo_owner: str, since: str) -> list:
    """Merged PRs created since `since`, newest first, flattened. Read only."""
    owner, name = repo_owner.split("/")
    query = GRAPHQL % (owner, name)
    out, cursor = [], None
    while True:
        argv = ["gh", "api", "graphql", "-f", "query=" + query]
        if cursor:
            argv += ["-f", "cursor=" + cursor]

        def attempt():
            r = subprocess.run(argv, capture_output=True, text=True)
            return (r.stdout, None) if r.returncode == 0 else (None, r.stderr)
        text, failure, _, why = gh_read.retry(attempt, gh_read.gh_wait, __import__("time").sleep)
        if failure is not None:
            raise RuntimeError(f"gh api graphql failed {why}: {gh_read.one_line(failure)}")
        page = json.loads(text)["data"]["repository"]["pullRequests"]
        out += [flatten(n) for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"] or page["nodes"][-1]["createdAt"] < since:
            return out
        cursor = page["pageInfo"]["endCursor"]


def flatten(n: dict) -> dict:
    """One PR in the shape every function below reads (and the cache holds)."""
    first = ((n.get("commits") or {}).get("nodes") or [{}])[0].get("commit") or {}
    return {
        "number": n["number"], "title": n.get("title") or "",
        "head_ref": n.get("headRefName") or "", "created_at": n["createdAt"],
        "merged_at": n["mergedAt"], "body": n.get("body") or "",
        "merge_commit": (n.get("mergeCommit") or {}).get("oid") or "",
        "first_commit_at": first.get("authoredDate") or n["createdAt"],
        "verdicts": [{"at": c["createdAt"], "line": (c.get("body") or "").split("\n")[0]}
                     for c in ((n.get("comments") or {}).get("nodes") or [])],
    }


def delivery_groups(repo: str, groups: set) -> dict:
    """{pr: group} for every delivery row naming exactly one roster group."""
    out = {}
    d = Path(repo) / "dev" / "programme" / "delivery"
    for f in sorted(d.glob("*.md")) if d.is_dir() else []:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = DELIVERY_ROW.match(line)
            if not m:
                continue
            named = set(plan_page._GROUP_ID.findall(m.group(2))) & groups
            if len(named) == 1:
                out[int(m.group(1))] = named.pop()
    return out


# ----------------------------------------------------------------- mapping

def pointers(group: dict) -> tuple[set, str]:
    """The roster's own record of a group's PRs: (numbers, merge commit)."""
    r = group.get("resume") or {}
    text = f"{r.get('next_step') or ''} {r.get('note') or ''}"
    nums = {int(n) for n in MERGED_IN.findall(text)}
    if isinstance(r.get("pr"), int):
        nums.add(r["pr"])
    return nums, (r.get("commit") or "")


def prs_of_groups(roster: dict, prs: list, delivery: dict) -> dict:
    """{group: sorted PR numbers}, the four reads the module docstring names."""
    G = roster_lib.groups_of(roster)
    by_num = {p["number"]: p for p in prs}
    out: dict = {g: set() for g in G}
    for g, entry in G.items():
        nums, commit = pointers(entry)
        out[g] |= {n for n in nums if n in by_num}
        if len(commit) >= 7:
            out[g] |= {p["number"] for p in prs if p["merge_commit"].startswith(commit[:12])}
    for p in prs:
        if SHARED_BRANCH.search(p["head_ref"]):
            continue
        g = plan_page.group_of_pr(roster, p["head_ref"], p["title"]) or delivery.get(p["number"])
        if g in out:
            out[g].add(p["number"])
    return {g: sorted(v) for g, v in out.items() if v}


def verdict_rounds(pr: dict) -> tuple[int, int]:
    """(rounds, blocked): distinct (verdict, head) `Fix review:` first lines."""
    seen = []
    for v in pr["verdicts"]:
        m = VERDICT.match(v["line"])
        if m and (m.group(1), m.group(2)[:7]) not in seen:
            seen.append((m.group(1), m.group(2)[:7]))
    return len(seen), sum(1 for k, _ in seen if k == "blocked")


def cited_carries(body: str) -> set:
    """Roster carry numbers (1-based) a body cites as answered. A sentence
    saying the carry is not done here (NOT_ANSWERED) cites nothing. Under
    `## Forward-carry` -- where a body lists what it leaves open, and where a
    per-carry disposition list says which it closed -- only a sentence that
    also says it is done (ANSWERED) counts."""
    out: set = set()
    forward = False
    for line in body.splitlines():
        if line.startswith("## "):
            forward = line[3:].strip().lower().startswith("forward-carry")
        # Under Forward-carry a disposition is its whole bullet ("Carry 1:
        # built. Done."); elsewhere a sentence is the unit.
        for sentence in [line] if forward else re.split(r"(?<=[.;])\s+", line):
            if NOT_ANSWERED.search(sentence) or forward and not ANSWERED.search(sentence):
                continue
            for m in CARRY_CITE.finditer(sentence):
                for a, b in re.findall(r"(\d+)[a-z]?(?:\s*(?:-|–|to)\s*(\d+))?", m.group(1)):
                    lo, hi = int(a), int(b or a)
                    if hi - lo <= 20:
                        out |= set(range(lo, hi + 1))
    return out


# -------------------------------------------------------------------- rows

def active_hours(spans) -> float:
    """Hours covered by the union of [begin, merge] spans: the time some PR
    of the group was being worked or reviewed. A gap with no part in flight
    is a held stage, priced by the carry model, never by the size."""
    total, cur = 0.0, None
    for b, e in sorted(spans):
        if cur is None or b > cur[1]:
            if cur:
                total += (cur[1] - cur[0]).total_seconds()
            cur = [b, e]
        else:
            cur[1] = max(cur[1], e)
    if cur:
        total += (cur[1] - cur[0]).total_seconds()
    return round(total / 3600.0, 2)


def group_rows(roster: dict, prs: list, mapping: dict, stages=None) -> list:
    """One row per group whose stage is in `stages` (default: done) with a
    merged PR. The fields are the CSV's columns."""
    stages = tuple(stages or roster_lib.DONE_STAGES)
    by_num = {p["number"]: p for p in prs}
    rows = []
    for g, entry in roster_lib.groups_of(roster).items():
        r = entry.get("resume") or {}
        if r.get("stage") not in stages or not mapping.get(g):
            continue
        ps = sorted((by_num[n] for n in mapping[g]), key=lambda p: p["merged_at"])
        text = f"{r.get('next_step') or ''} {r.get('note') or ''}"
        stamps = [ts(s) for s in DISPATCHED.findall(text)]
        spans, starts = [], []
        for i, p in enumerate(ps):
            b = min(ts(p["first_commit_at"]), ts(p["created_at"]))
            if i == 0 and stamps:
                b = min([b] + stamps)
            spans.append((b, ts(p["merged_at"])))
            starts += [(ts(p["first_commit_at"]), "first-commit"),
                       (ts(p["created_at"]), "pr-created")]
        start, src = min(starts + [(s, "dispatched") for s in stamps])
        finish = max(e for _, e in spans)
        rounds = [verdict_rounds(p) for p in ps]
        wait = max((ts(p["created_at"]) - ts(p["first_commit_at"])).total_seconds()
                   for p in ps) / 3600.0
        rows.append({
            "group": g, "size": entry.get("size") or "", "kind": entry.get("kind") or "",
            "class": replan.work_class(entry), "stage": r.get("stage"),
            "prs": " ".join(f"#{p['number']}" for p in ps), "parts": len(ps),
            "start": iso(start), "start_source": src, "finish": iso(finish),
            "hours": active_hours(spans),
            "span_hours": round((finish - start).total_seconds() / 3600.0, 2),
            "handoff_wait_hours": round(max(0.0, wait), 2),
            "rounds": sum(k for k, _ in rounds), "blocked": sum(b for _, b in rounds),
            "carries": len(entry.get("carry") or []),
        })
    return sorted(rows, key=lambda x: x["start"])


def part_rows(roster: dict, prs: list, mapping: dict) -> list:
    """Every PR after a group's first merge: hours and carries it answers."""
    by_num = {p["number"]: p for p in prs}
    out = []
    for g, nums in mapping.items():
        ps = sorted((by_num[n] for n in nums), key=lambda p: p["merged_at"])
        for p in ps[1:]:
            begin = min(ts(p["first_commit_at"]), ts(p["created_at"]))
            out.append({"group": g, "pr": p["number"],
                        "hours": round((ts(p["merged_at"]) - begin).total_seconds() / 3600, 2),
                        "carries": len(cited_carries(p["body"])),
                        "rounds": verdict_rounds(p)[0]})
    return sorted(out, key=lambda x: x["pr"])


def held_rows(roster: dict, prs: list, mapping: dict) -> list:
    """Each carries-open group: its carries and the ones no merged body of
    its own answers (`cited_carries`), 1-based as the bodies cite them."""
    by_num = {p["number"]: p for p in prs}
    out = []
    for g, entry in roster_lib.groups_of(roster).items():
        if (entry.get("resume") or {}).get("stage") != "carries-open":
            continue
        carry = entry.get("carry") or []
        cited: set = set()
        for n in mapping.get(g, []):
            cited |= cited_carries(by_num[n]["body"])
        open_ = [i for i in range(1, len(carry) + 1) if i not in cited]
        out.append({"group": g, "size": entry.get("size") or "", "carries": len(carry),
                    "open": len(open_), "open_index": " ".join(map(str, open_)),
                    "prs": " ".join(f"#{n}" for n in mapping.get(g, []))})
    return out


P_NUMBER = re.compile(r"\bP\d{2,4}\b")
MARKER = re.compile(r"Carry: (R\d+(?:-[A-Z0-9]+)+)")


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


#: A body cites carries by position, and a carry list is re-numbered when an
#: entry is dropped (#2883's "carry 6" is the token measurement; FLOW-BOARD's
#: carry 6 on 2026-11-01 is a root-cause note), so a forward by number counts
#: only where the line and the carry share this many distinctive words.
FORWARD_OVERLAP = 3


def _words(text: str) -> set:
    return {w for w in _norm(text).split() if len(w) >= 6}


def held_report(roster: dict, prs: list, mapping: dict) -> list:
    """Each still-open carry of each carries-open group, classified:

    a  landed: every P-number it names, or its first 120 normalized
       characters, appears in a carry of a FUTURE group -- open and not
       itself carries-open, so two held groups never discharge into each
       other (`dest`, `entry` 1-based);
    b  forwarded: a merged body of this group cites the carry's number in a
       sentence or bullet whose `Carry: <GROUP>` marker names a future group,
       where it has not landed (`dest`, `pr`);
    c  owned only by this group.
    A text that three or more groups carry is a standing obligation (the
    self-test hygiene paragraph), never evidence that a carry moved.
    """
    G = roster_lib.groups_of(roster)
    by_num = {p["number"]: p for p in prs}
    live = {g for g, e in G.items() if roster_lib.is_open(e)
            and (e.get("resume") or {}).get("stage") != "carries-open"}
    seen: dict = {}
    for e in G.values():
        for c in e.get("carry") or []:
            seen.setdefault(_norm(c)[:120], set()).add(e["group"])
    rows = []
    for h in held_rows(roster, prs, mapping):
        g = h["group"]
        carry = G[g].get("carry") or []
        forwards: dict = {}
        for n in mapping.get(g, []):
            # One line is one item: a disposition bullet ends in its marker
            # ("Carry 4: ... not in this diff. Carry: R10-X").
            for item in by_num[n]["body"].splitlines():
                dests = [d for d in MARKER.findall(item) if d != g and d in live]
                if not dests:
                    continue
                for m in CARRY_CITE.finditer(item):
                    for a, _ in re.findall(r"(\d+)[a-z]?(?:\s*(?:-|–|to)\s*(\d+))?", m.group(1)):
                        i = int(a)
                        if 0 < i <= len(carry) and len(
                                _words(carry[i - 1][:400]) & _words(item)) >= FORWARD_OVERLAP:
                            forwards.setdefault(i, (dests[0], n))
        for i in map(int, h["open_index"].split()):
            text = carry[i - 1]
            pnums = set(P_NUMBER.findall(text))
            key = _norm(text)[:120]
            hit = None
            boiler = len(seen.get(key, ())) >= 3
            for d in sorted(live - {g}):
                for j, other in enumerate(G[d].get("carry") or [], start=1):
                    if boiler:
                        break
                    if (pnums and pnums <= set(P_NUMBER.findall(other))) or (
                            len(key) >= 40 and key in _norm(other)):
                        hit = (d, j)
                        break
                if hit:
                    break
            if hit:
                cls, dest, ref = "a", hit[0], f"entry {hit[1]}"
            elif i in forwards:
                cls, dest, ref = "b", forwards[i][0], f"#{forwards[i][1]}"
            else:
                cls, dest, ref = "c", "", ""
            rows.append({"group": g, "carry": i, "class": cls, "dest": dest, "ref": ref,
                         "pnums": " ".join(sorted(pnums)), "text": " ".join(text.split())[:160]})
    return rows


# ------------------------------------------------------------------- stats

def pctl(xs, p: float) -> float:
    xs = sorted(xs)
    if not xs:
        raise ValueError("percentile of no samples")
    k = (len(xs) - 1) * p / 100.0
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def dist(xs) -> dict:
    return {"n": len(xs), "median": round(pctl(xs, 50), 1), "p75": round(pctl(xs, 75), 1),
            "p90": round(pctl(xs, 90), 1)} if xs else {"n": 0}


def round_slope(rows: list, x: str = "rounds") -> float:
    """Hours one more `x` (review round, or carry) adds: the Theil-Sen slope
    of hours on `x` over every row (the median of the pairwise slopes),
    robust to the long tail a mean-based fit would follow."""
    pts = [(r[x], r["hours"]) for r in rows]
    slopes = [(h2 - h1) / (k2 - k1) for i, (k1, h1) in enumerate(pts)
              for k2, h2 in pts[i + 1:] if k2 != k1]
    return round(max(0.0, pctl(slopes, 50)), 2) if slopes else 0.0


def _cells(rows, value) -> tuple[dict, dict]:
    """({size: value over the size}, {size: {class: value}} for n>=MIN_CELL)."""
    by_size, by_class = {}, {}
    for s in SIZES:
        rs = [r for r in rows if r["size"] == s]
        if not rs:
            continue
        by_size[s] = value(rs)
        cells = {c: value([r for r in rs if r["class"] == c])
                 for c in sorted({r["class"] for r in rs})
                 if sum(1 for r in rs if r["class"] == c) >= MIN_CELL}
        if cells:
            by_class[s] = cells
    return by_size, by_class


def model(rows: list, percentile: float = DEFAULT_PERCENTILE) -> dict:
    """The durations.json keys the planner reads, from the measured rows.

    A group's hours = first_round_hours + (review_rounds - 1) * round_hours
    (+ carry_hours per carry above carry_baseline[size], `carry_model`).
    first_round_hours is the percentile of each row's hours with its extra
    rounds priced out at the pooled slope, so the percentile is taken over
    the work, and the rounds a cell expects are added back explicitly."""
    rows = [r for r in rows if r["size"] in SIZES]  # an unsized group prices nothing
    slope = round_slope(rows)
    adj = [dict(r, hours=max(0.0, r["hours"] - slope * (r["rounds"] - 1))) for r in rows]
    first, first_c = _cells(adj, lambda rs: round(pctl([r["hours"] for r in rs], percentile), 1),
                            )
    mean_r, mean_rc = _cells(rows, lambda rs: round(sum(r["rounds"] for r in rs) / len(rs), 2),
                             )
    base, _ = _cells(rows, lambda rs: pctl([r["carries"] for r in rs], 50))
    per_carry = round_slope(adj, "carries")
    sizes, lifted, prev = {}, [], None
    for s in (s for s in SIZES if s in first):
        h = round(first[s] + (mean_r[s] - 1) * slope, 1)
        if prev is not None and h < prev[1]:
            # A larger size never plans shorter than a smaller one: the cell
            # is a small sample (XL n=6 at 2026-11-01), not evidence that
            # larger work is faster. Its work term is lifted to the floor.
            first[s] = round(first[s] + prev[1] - h, 1)
            lifted.append(f"{s} {h:g} h lifted to {prev[0]}'s {prev[1]:g} h")
            h = prev[1]
        sizes[s] = h
        prev = (s, h)
    counts = ", ".join(f"{s} n={sum(1 for r in rows if r['size'] == s)}" for s in sizes)
    return {
        "sizes_hours": sizes, "first_round_hours": first, "first_round_by_class_hours": first_c,
        "review_rounds": mean_r, "review_rounds_by_class": mean_rc, "round_hours": slope,
        "carry_baseline": base, "carry_hours": per_carry, "sizes_percentile": percentile,
        "sizes_provenance": (
            f"p{percentile:g} over {len(rows)} done groups with a merged PR ({counts}): "
            "active hours (the union of each part's first commit or creation, or the "
            "roster's dispatch stamp, to its merge) with extra review rounds priced out "
            f"at the pooled Theil-Sen slope ({slope} h/round), then the cell's mean "
            "rounds added back; per class where a cell has n>=" + str(MIN_CELL) +
            ". Wall clock: review, queueing and the PR-less handoff wait are inside "
            f"it. carry_hours ({per_carry} h) is the Theil-Sen slope of the "
            "round-adjusted hours on the group's carry count, priced per carry "
            "above the size's median (carry_baseline)." + (f" Monotone in size: {'; '.join(lifted)}." if lifted else "") +
            " Measured by tools/plan/size_durations.py; re-derive, never edit."),
    }


def carry_model(parts: list, held: list, percentile: float = DEFAULT_PERCENTILE) -> dict:
    """The held-stage model: hours per later part, the carries one part can
    answer, and each carries-open group's open count at measurement.

    A part's hours do not grow with the carries it answers (measured
    2026-11-01: Theil-Sen slope -0.2 h/carry over the parts citing any, one
    part answering 22), so a part's capacity is the p90 of carries a citing
    part answered, not the median, and every part costs carry_part_hours."""
    citing = [p["carries"] for p in parts if p["carries"]]
    if not parts or not citing:
        return {}
    hours, per = round(pctl([p["hours"] for p in parts], percentile), 1), round(pctl(citing, 90), 1)
    return {"carry_part_hours": hours, "carries_per_part": per,
            "held_open_carries": {h["group"]: {"open": h["open"], "carries": h["carries"]}
                                  for h in held},
            "carry_provenance": (
                f"p{percentile:g} hours over {len(parts)} second-or-later part PRs "
                f"(first commit or creation to merge); carries_per_part is the p90 of "
                f"roster carries a part body cites as answered over the {len(citing)} "
                "that cite any (size_durations.cited_carries): a part's capacity, "
                "since a part's hours do not grow with its carries. held_open_carries: each carries-open group's carries no merged "
                "body of its own cites, at measurement; replan.py counts any carry "
                "appended since as open")}


def write_csv(rows: list, path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["group"])
        w.writeheader()
        w.writerows(rows)


def measure(repo: str, roster: dict, prs: list) -> tuple[list, list, list, dict]:
    mapping = prs_of_groups(roster, prs, delivery_groups(repo, set(roster_lib.groups_of(roster))))
    return (group_rows(roster, prs, mapping), part_rows(roster, prs, mapping),
            held_rows(roster, prs, mapping), mapping)


# -------------------------------------------------------------- self-test

def _fixture():
    def pr(n, head, title, t0, merged, verdicts=(), body="", commit=""):
        return {"number": n, "title": title, "head_ref": head, "created_at": t0,
                "merged_at": merged, "body": body, "merge_commit": commit,
                "first_commit_at": t0,
                "verdicts": [{"at": merged, "line": v} for v in verdicts]}
    roster = {"groups": [
        {"group": "R9-A", "size": "S", "kind": "defect", "resume": {"stage": "done"}},
        {"group": "R9-B", "size": "S", "kind": "defect",
         "resume": {"stage": "done", "next_step": "done: merged in #12",
                    "note": "fixer dispatched 2026-10-01T00:00Z"}},
        {"group": "R9-C", "size": "M", "kind": "instrument",
         "resume": {"stage": "done", "commit": "abcdef1234567"}},
        {"group": "R9-D", "size": "M", "kind": "instrument", "resume": {"stage": "done"}},
        {"group": "R9-OPEN", "size": "L", "kind": "defect", "resume": {"stage": "queued"}},
    ]}
    prs = [
        pr(11, "fix/r9-a", "R9-A: one", "2026-10-01T00:00:00Z", "2026-10-01T10:00:00Z",
           ["Fix review: merge aaaaaaa"]),
        pr(12, "fix/elsewhere", "no group named", "2026-10-01T04:00:00Z",
           "2026-10-01T20:00:00Z",
           ["Fix review: blocked bbbbbbb claims: x", "Fix review: blocked bbbbbbb claims: x",
            "Fix review: merge ccccccc"]),
        pr(13, "fix/other", "unrelated", "2026-10-02T00:00:00Z", "2026-10-02T06:00:00Z",
           commit="abcdef1234567890"),
        pr(14, "fix/r9-c-p2", "R9-C part 2: carries 2-4", "2026-10-02T08:00:00Z",
           "2026-10-02T12:00:00Z", body="Answers carries 2-4 and carry 6.\n"
           "Carry 7 is the remainder.\n## Forward-carry\n- carry 9. Carry: R9-C"),
        pr(15, "fix/audit-r9-roster-pr", "roster: R9-D done", "2026-10-02T00:00:00Z",
           "2026-10-02T01:00:00Z"),
    ]
    return roster, prs


def self_test() -> int:
    fails = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    roster, prs = _fixture()
    mapping = prs_of_groups(roster, prs, {})
    check("branch maps R9-A to #11", mapping.get("R9-A") == [11])
    check("a roster `merged in #N` pointer maps R9-B to #12", mapping.get("R9-B") == [12])
    check("resume.commit as a merge commit maps R9-C to #13, its branch adds #14",
          mapping.get("R9-C") == [13, 14])
    check("a shared roster branch naming a group in its title maps nothing",
          "R9-D" not in mapping)
    rows = {r["group"]: r for r in group_rows(roster, prs, mapping)}
    check("start is the dispatch stamp when it is earliest (R9-B 20.0 h)",
          rows["R9-B"]["hours"] == 20.0 and rows["R9-B"]["start_source"] == "dispatched")
    check("a repeated (verdict, head) counts once: R9-B rounds 2, blocked 1",
          (rows["R9-B"]["rounds"], rows["R9-B"]["blocked"]) == (2, 1))
    check("a group with no merged PR is not a row", "R9-D" not in rows and "R9-OPEN" not in rows)
    check("R9-C's hours are its two parts' 6 h + 4 h, not the 12 h span with the gap",
          (rows["R9-C"]["hours"], rows["R9-C"]["span_hours"], rows["R9-C"]["parts"]) == (10.0, 12.0, 2))
    check("cited_carries: ranges and lists, not the remainder, not forward-carry",
          cited_carries(prs[3]["body"]) == {2, 3, 4, 6})
    check("cited_carries: a `Carry: R9-X` marker cites nothing", cited_carries("Carry: R9-C") == set())
    check("cited_carries: a forward-carry disposition saying Done counts, one not in this diff does not",
          cited_carries("## Forward-carry\n- Carry 1: built. Done.\n- Carry 2: not in this diff.")
          == {1})
    check("cited_carries: `not done here` cites nothing",
          cited_carries("- **Carry 2** (x): **not done here.**") == set())
    check("pctl is linear: p75 of 1..4 is 3.25", pctl([4, 1, 3, 2], 75) == 3.25)
    rs = [{"size": "S", "class": "production", "hours": h, "rounds": k, "carries": c}
          for h, k, c in ((10, 1, 1), (12, 1, 2), (14, 1, 3), (30, 3, 4), (40, 3, 5))]
    m = model(rs)
    check("model: the round cost is the Theil-Sen slope, median of 8..15 = 11.5 h",
          m["round_hours"] == 11.5)
    check("model: first_round_hours is the p75 of the round-adjusted hours (14.0)",
          m["first_round_hours"]["S"] == 14.0)
    check("model: sizes_hours composes it with the mean rounds: 14 + 0.8 x 11.5 = 23.2",
          m["sizes_hours"]["S"] == 23.2 and m["review_rounds"]["S"] == 1.8)
    check("model: a cell of n>=5 is published per class, one under MIN_CELL is not",
          m["first_round_by_class_hours"] == {"S": {"production": 14.0}}
          and model(rs + [dict(rs[0], **{"class": "instrument"})])
          ["first_round_by_class_hours"]["S"].keys() == {"production"})
    check("round_slope is the median pairwise slope, not the mean (5.5, not 9.25)",
          round_slope([{"rounds": k, "hours": h} for k, h in ((1, 0), (2, 1), (3, 2), (4, 30))])
          == 5.5)
    ordered = ((1, 0), (2, 1), (3, 2), (4, 30))
    check("round_slope does not depend on row order: ascending, reversed and shuffled rows agree (5.5)",
          {round_slope([{"rounds": k, "hours": h} for k, h in rows])
           for rows in (ordered, ordered[::-1], (ordered[2], ordered[0], ordered[3], ordered[1]))}
          == {5.5})
    m2 = model([dict(r, rounds=1) for r in rs]
               + [{"size": "M", "class": "production", "hours": 5, "rounds": 1, "carries": 0}])
    check("model: a larger size planning shorter is lifted to the smaller's hours, and says so",
          m2["sizes_hours"] == {"S": 30.0, "M": 30.0}
          and "M 5 h lifted to S's 30 h" in m2["sizes_provenance"])
    check("model: carry_baseline is the median carries per size", m["carry_baseline"]["S"] == 3)
    check("model: carry_hours is the slope of round-adjusted hours on carries",
          m["carry_hours"] == round_slope([dict(r, hours=r["hours"] - 11.5 * (r["rounds"] - 1))
                                           for r in rs], "carries"))
    check("model: an unmeasured size is absent, never imputed", "XS" not in m["sizes_hours"])
    parts = part_rows(roster, prs, mapping)
    check("part_rows: R9-C's part 2, 4.0 h, 4 carries",
          [(p["pr"], p["hours"], p["carries"]) for p in parts] == [(14, 4.0, 4)])
    cm = carry_model(parts, [])
    check("carry_model: hours per part and a part's carry capacity (p90)",
          (cm["carry_part_hours"], cm["carries_per_part"]) == (4.0, 4.0))
    cap = carry_model([dict(parts[0], carries=c) for c in (1, 1, 2, 10, 20)], [])
    check("carry_model: the capacity is the p90 of carries per part, not the median (16.0)",
          cap["carries_per_part"] == 16.0)
    check("carry_model null: no part cites a carry -> no model", carry_model([dict(parts[0], carries=0)], []) == {})
    held = {"groups": [
        {"group": "R9-H", "size": "M", "kind": "instrument",
         "resume": {"stage": "carries-open", "pr": 21},
         "carry": ["answered here", "P123 the gate's retry, owed",
                   "a forwarded lead about the session cache eviction",
                   "owned only here: the held twin carries the same words, nothing else does",
                   "Self-test hygiene paragraph: no new mutant, no hand-built repository, no new writer",
                   "P200 and P201 are both owed here"]},
        {"group": "R9-F", "size": "S", "kind": "instrument", "resume": {"stage": "queued"},
         "carry": ["From R9-H: P123 the gate's retry", "Self-test hygiene paragraph: no new mutant, no hand-built repository, no new writer", "P200 alone moved here"]},
        {"group": "R9-G", "size": "S", "kind": "instrument", "resume": {"stage": "not-started"},
         "carry": ["Self-test hygiene paragraph: no new mutant, no hand-built repository, no new writer"]},
        {"group": "R9-K", "size": "S", "kind": "instrument", "resume": {"stage": "carries-open"},
         "carry": ["owned only here: the held twin carries the same words, nothing else does"]},
    ]}
    hp = [{"number": 21, "title": "R9-H: part 1", "head_ref": "fix/r9-h", "body":
           "Carry 1 answered.\n## Forward-carry\n- Carry 3 (the forwarded session cache eviction "
           "lead): not in this diff. Carry: R9-G\n- Carry 4 (the token counter): not "
           "in this diff. Carry: R9-G",
           "created_at": "2026-10-01T00:00:00Z", "merged_at": "2026-10-01T05:00:00Z",
           "merge_commit": "", "first_commit_at": "2026-10-01T00:00:00Z", "verdicts": []}]
    hm = prs_of_groups(held, hp, {})
    rep = {(r["group"], r["carry"]): r for r in held_report(held, hp, hm)}
    check("held_rows: carry 1 answered, five open", [h["open"] for h in held_rows(held, hp, hm)
                                                     if h["group"] == "R9-H"] == [5])
    check("held_report a: a carry whose P-number landed in a future group's carry",
          (rep[("R9-H", 2)]["class"], rep[("R9-H", 2)]["dest"], rep[("R9-H", 2)]["ref"])
          == ("a", "R9-F", "entry 1"))
    check("held_report b: a carry a merged body forward-carried by number to a future group",
          (rep[("R9-H", 3)]["class"], rep[("R9-H", 3)]["dest"], rep[("R9-H", 3)]["ref"])
          == ("b", "R9-G", "#21"))
    check("held_report c: text only another HELD group carries is owned here, and a "
          "forward by number whose words do not match the carry is not a forward (null control)",
          rep[("R9-H", 4)]["class"] == "c")
    check("held_report c: text three groups carry is boilerplate, not a landing",
          rep[("R9-H", 5)]["class"] == "c")
    check("held_report c: a carry naming P200 and P201 has not landed where only P200 did",
          rep[("R9-H", 6)]["class"] == "c")
    print(f"size_durations self-test: {len(fails)} failed")
    return 1 if fails else 0


# -------------------------------------------------------------------- main

def run(repo: str, roster_ref: str | None, repo_owner: str, since: str,
        cache: str | None, csv_path: str | None, percentile: float) -> dict:
    roster, _, _ = replan.load_roster(repo, roster_ref)
    if cache and Path(cache).is_file():
        prs = json.loads(Path(cache).read_text(encoding="utf-8"))
    else:
        prs = fetch(repo_owner, since)
        if cache:
            Path(cache).write_text(json.dumps(prs), encoding="utf-8")
    rows, parts, held, _mapping = measure(repo, roster, prs)
    if csv_path:
        write_csv(rows, csv_path)
        stem = str(Path(csv_path).with_suffix(""))
        write_csv(parts, stem + "-parts.csv")
        write_csv(held, stem + "-held.csv")
        write_csv(held_report(roster, prs, _mapping), stem + "-held-carries.csv")
    out = model(rows, percentile)
    out.update(carry_model(parts, held, percentile))
    out["sizes_measured_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--repo", default=".")
    p.add_argument("--roster-ref", default=None)
    p.add_argument("--repo-owner", default="tvofi/heatpump_optimizer")
    p.add_argument("--since", default=SINCE, help="earliest PR creation read")
    p.add_argument("--prs-cache", default=None, help="read (or write) the fetched PRs here")
    p.add_argument("--csv", default=None)
    p.add_argument("--percentile", type=float, default=DEFAULT_PERCENTILE)
    p.add_argument("--out-durations", default=None, help="merge the model into this file")
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    out = run(a.repo, a.roster_ref, a.repo_owner, a.since, a.prs_cache, a.csv, a.percentile)
    if a.out_durations:
        target = Path(a.out_durations)
        old = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
        target.write_text(json.dumps({**old, **out}, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
