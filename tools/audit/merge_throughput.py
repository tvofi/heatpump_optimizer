#!/usr/bin/env python3
"""#681: merge throughput against the forced-full Tests run on main.

A measurement, then a decision. The question is not whether to turn a merge
queue on — a queue's rebase breaks ## Head, the review's at-this-SHA rule,
and the record enumerator's assumption that the reviewed head is the commit
that lands (docs/HANDOVER.md trap 14). The question is whether merges land
inside the previous merge's gate window often enough that a cheaper wait
is worth having.

THE RULE, in full:

    A Tests workflow run with event=push on branch main is the forced-full
    gate. Consecutive such runs, ordered by created_at, form gaps. A gap
    is an overlap when the later run's created_at is earlier than the
    earlier run's completed_at. The wait predicate is true when the latest
    such run is still queued or in_progress.

Nothing here talks to the network. Live data is a JSON file the caller
already fetched (`gh run list --workflow tests.yml --branch main --event
push --json ...`). The window is still open, so a figure this script
prints is restated only in ## Figures, next to the command that produced
it.

Usage:

    python3 tools/audit/merge_throughput.py --self-test
    python3 tools/audit/merge_throughput.py --from-runs FILE [--since ISO]
    python3 tools/audit/merge_throughput.py --wait --from-runs FILE
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class Run:
    sha: str
    created: datetime
    started: datetime | None
    completed: datetime | None
    status: str
    conclusion: str

    @property
    def duration_s(self) -> float | None:
        if self.started is None or self.completed is None:
            return None
        if self.status != "completed":
            return None
        return (self.completed - self.started).total_seconds()

    @property
    def busy(self) -> bool:
        return self.status in ("queued", "in_progress")


def runs_from_gh(rows: list[dict], since: datetime | None = None) -> list[Run]:
    out: list[Run] = []
    for row in rows:
        created = parse_iso(row.get("createdAt"))
        if created is None:
            continue
        if since is not None and created < since:
            continue
        out.append(
            Run(
                sha=row.get("headSha") or "",
                created=created,
                started=parse_iso(row.get("startedAt")),
                completed=parse_iso(row.get("updatedAt"))
                if row.get("status") == "completed"
                else None,
                status=row.get("status") or "",
                conclusion=row.get("conclusion") or "",
            )
        )
    out.sort(key=lambda r: r.created)
    return out


def analyze(runs: list[Run]) -> dict:
    ordered = sorted(runs, key=lambda r: r.created)
    overlaps = 0
    overlaps_own_failure = 0
    gaps_under_400s = 0
    durations = [d for r in ordered if (d := r.duration_s) is not None]
    for prev, cur in zip(ordered, ordered[1:]):
        gap = (cur.created - prev.created).total_seconds()
        if gap < 400:
            gaps_under_400s += 1
        if prev.completed is not None and cur.created < prev.completed:
            overlaps += 1
            if cur.conclusion == "failure":
                overlaps_own_failure += 1
    return {
        "merges": len(ordered),
        "gaps": max(0, len(ordered) - 1),
        "overlaps": overlaps,
        "overlaps_own_failure": overlaps_own_failure,
        "gaps_under_400s": gaps_under_400s,
        "durations_s": durations,
        "wait_busy": wait_busy(ordered),
    }


def wait_busy(runs: list[Run]) -> bool:
    if not runs:
        return False
    latest = max(runs, key=lambda r: r.created)
    return latest.busy


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("empty")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = int(round((len(ordered) - 1) * p))
    return ordered[idx]


def render_report(report: dict, out) -> None:
    print(f"RESULT merges={report['merges']} count", file=out)
    print(f"RESULT gaps={report['gaps']} count", file=out)
    print(f"RESULT overlaps={report['overlaps']} count", file=out)
    print(f"RESULT overlaps_own_failure={report['overlaps_own_failure']} count", file=out)
    print(f"RESULT gaps_under_400s={report['gaps_under_400s']} count", file=out)
    durs = report["durations_s"]
    if durs:
        print(f"RESULT duration_min_s={min(durs):.0f} s", file=out)
        print(f"RESULT duration_p50_s={percentile(durs, 0.5):.0f} s", file=out)
        print(f"RESULT duration_max_s={max(durs):.0f} s", file=out)
    print(f"RESULT wait_busy={1 if report['wait_busy'] else 0} bool", file=out)


def self_test() -> int:
    failures = 0

    def check(name: str, got, want) -> None:
        nonlocal failures
        if got == want:
            print(f"  ok   {name}")
        else:
            failures += 1
            print(f"  FAIL {name}: got {got!r}, want {want!r}")

    def at(stamp: str) -> datetime:
        return parse_iso(stamp)  # type: ignore[return-value]

    def run(
        sha: str,
        created: str,
        started: str,
        updated: str,
        status: str = "completed",
        conclusion: str = "success",
    ) -> Run:
        completed = parse_iso(updated) if status == "completed" else None
        return Run(
            sha=sha,
            created=at(created),
            started=at(started),
            completed=completed,
            status=status,
            conclusion=conclusion,
        )

    # Two sequential gates: the second starts after the first completed.
    sequential = [
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
        run("bbb", "2026-09-03T00:21:00Z", "2026-09-03T00:21:00Z", "2026-09-03T00:41:00Z"),
    ]
    report = analyze(sequential)
    check("sequential gates are not overlaps", report["overlaps"], 0)
    check("...and the gap count is one", report["gaps"], 1)
    check("...and the later merge is not an own-failure", report["overlaps_own_failure"], 0)

    # The later merge is created while the earlier gate is still running.
    overlap = [
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
        run("bbb", "2026-09-03T00:05:00Z", "2026-09-03T00:05:00Z", "2026-09-03T00:25:00Z"),
    ]
    report = analyze(overlap)
    check("a merge inside the previous gate window is an overlap", report["overlaps"], 1)
    check("...and a successful own gate is not an own-failure", report["overlaps_own_failure"], 0)

    overlap_red = [
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
        run(
            "bbb",
            "2026-09-03T00:05:00Z",
            "2026-09-03T00:05:00Z",
            "2026-09-03T00:25:00Z",
            conclusion="failure",
        ),
    ]
    report = analyze(overlap_red)
    check("an overlapping merge whose own Tests failed is counted", report["overlaps_own_failure"], 1)

    # Null control for own-failure: the same overlap, success, already checked
    # above. A sequential failure is not an overlap-own-failure.
    sequential_red = [
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
        run(
            "bbb",
            "2026-09-03T00:21:00Z",
            "2026-09-03T00:21:00Z",
            "2026-09-03T00:41:00Z",
            conclusion="failure",
        ),
    ]
    report = analyze(sequential_red)
    check("a sequential failure is not an overlap-own-failure", report["overlaps_own_failure"], 0)
    check("...and still not an overlap", report["overlaps"], 0)

    short = [
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:10:00Z"),
        run("bbb", "2026-09-03T00:02:00Z", "2026-09-03T00:02:00Z", "2026-09-03T00:12:00Z"),
        run("ccc", "2026-09-03T00:30:00Z", "2026-09-03T00:30:00Z", "2026-09-03T00:50:00Z"),
    ]
    report = analyze(short)
    check("a gap under 400s is counted", report["gaps_under_400s"], 1)

    empty = analyze([])
    check("no runs means no overlaps", empty["overlaps"], 0)
    check("...and wait is not busy", empty["wait_busy"], False)

    one = analyze([
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
    ])
    check("a single completed run has no gaps", one["gaps"], 0)
    check("...and wait is not busy", one["wait_busy"], False)

    durs = [
        run("a", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:10:00Z"),
        run("b", "2026-09-03T00:20:00Z", "2026-09-03T00:20:00Z", "2026-09-03T00:45:00Z"),
        run("c", "2026-09-03T01:00:00Z", "2026-09-03T01:00:00Z", "2026-09-03T01:10:00Z"),
    ]
    report = analyze(durs)
    check("duration min is the shortest completed run", min(report["durations_s"]), 600.0)
    check("duration max is the longest completed run", max(report["durations_s"]), 1500.0)

    check("latest in_progress is busy", wait_busy([
        run("aaa", "2026-09-03T00:00:00Z", "2026-09-03T00:00:00Z", "2026-09-03T00:20:00Z"),
        Run(
            sha="bbb",
            created=at("2026-09-03T00:21:00Z"),
            started=at("2026-09-03T00:21:00Z"),
            completed=None,
            status="in_progress",
            conclusion="",
        ),
    ]), True)
    check("latest completed is not busy", wait_busy(sequential), False)
    check("latest queued is busy", wait_busy([
        Run(
            sha="aaa",
            created=at("2026-09-03T00:00:00Z"),
            started=None,
            completed=None,
            status="queued",
            conclusion="",
        ),
    ]), True)
    check("empty run list is not busy", wait_busy([]), False)
    # Null control for cancelled: a completed cancelled run is not in progress.
    check("a completed cancelled run is not busy", wait_busy([
        run(
            "aaa",
            "2026-09-03T00:00:00Z",
            "2026-09-03T00:00:00Z",
            "2026-09-03T00:01:00Z",
            conclusion="cancelled",
        ),
    ]), False)

    print(f"{'FAILED' if failures else 'ok'}: merge_throughput.py self-test")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--from-runs", metavar="FILE")
    ap.add_argument("--since", metavar="ISO")
    ap.add_argument("--wait", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.from_runs:
        ap.error("--from-runs FILE is required (fetch with gh run list; this "
                 "script does not call the network)")

    with open(args.from_runs) as fh:
        rows = json.load(fh)
    since = parse_iso(args.since) if args.since else None
    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    runs = runs_from_gh(rows, since)

    if args.wait:
        busy = wait_busy(runs)
        print(f"RESULT wait_busy={1 if busy else 0} bool")
        if busy:
            latest = max(runs, key=lambda r: r.created)
            print(
                f"REFUSED: main's latest forced-full Tests run is {latest.status} "
                f"({latest.sha[:12] or 'unknown'}); wait until it completes",
                file=sys.stderr,
            )
            return 1
        return 0

    report = analyze(runs)
    render_report(report, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
