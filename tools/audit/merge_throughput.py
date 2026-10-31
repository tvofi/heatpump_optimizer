#!/usr/bin/env python3
"""#681: merge throughput against the forced-full Tests run on main.

A measurement, then a decision. The question is not whether to turn a merge
queue on — a queue's rebase breaks ## Head, the review's at-this-SHA rule,
and the record enumerator's assumption that the reviewed head is the commit
that lands (dev/programme/HANDOVER.md trap 14). The question is whether merges land
inside the previous merge's gate window often enough that a cheaper wait
is worth having.

THE RULE, in full:

    A `CI` workflow run (ci.yml; `Tests`, tests.yml, before the layout
    cut-over) with event=push on branch main is the forced-full gate. Consecutive such runs, ordered by created_at, form gaps. A gap
    is an overlap when the later run's created_at is earlier than the
    earlier run's completed_at. The wait predicate is true when the latest
    such run is still queued or in_progress.

Nothing here talks to the network. Live data is a JSON file the caller
already fetched (`gh run list --workflow ci.yml --branch main --event
push --json ...`, and `--workflow tests.yml` for the runs before the
cut-over: `--from-runs` repeats and the files are one series). The window is still open, so a figure this script
prints is restated only in ## Figures, next to the command that produced
it.

The `flow` subcommand is the flow board (Lean study K1): throughput against
the owner's demand of one roster group merged per hour, read from git alone --
the first-parent log of the tree, the review/verdict bus refs (through
`review_strength`'s grammar) and the roster (through `roster_lib`). It
publishes per rolling hour and per 24 h: groups closed against takt 1.0,
fly-ins closed, main moves split by kind, WIP by flow lane, first-pass review
yield with its blocked-class mix, and lead time per size. `state_docs.py`'s
generator list runs it as the FLOW-BOARD.md state doc, so it publishes beside
the plan table. A source it cannot read prints UNAVAILABLE with its reason,
never a zero.

Usage:

    python3 tools/audit/merge_throughput.py --self-test
    python3 tools/audit/merge_throughput.py --from-runs FILE [--since ISO]
    python3 tools/audit/merge_throughput.py --wait --from-runs FILE
    python3 tools/audit/merge_throughput.py flow [--repo DIR] [--tree REF] \\
        [--roster-ref REF | --roster-file PATH] [--until ISO] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

#: The bus and roster readers are the instruments that already own those
#: reads: `review_strength.py` parses the verdict grammar the bus publishes,
#: and `roster_lib.py` is the one owner of the roster schema. Imported, never
#: copied -- a second parser of either would drift from the first.
sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
import review_strength as rs  # noqa: E402
import roster_lib  # noqa: E402


def load_rows(paths: list[str]) -> list[dict]:
    """One series from one or more run listings (ci.yml's, and tests.yml's before it)."""
    rows: list[dict] = []
    for path in paths:
        with open(path) as fh:
            rows += json.load(fh)
    return rows


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

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for i, (sha, t) in enumerate((("aaa", "2026-10-01T00:00:00Z"), ("bbb", "2026-10-02T00:00:00Z"))):
            paths.append(f"{d}/{i}.json")
            with open(paths[-1], "w") as fh:
                json.dump([{"headSha": sha, "createdAt": t, "status": "completed"}], fh)
        check("two listings (tests.yml's, then ci.yml's) are one series of two merges",
              analyze(runs_from_gh(load_rows(paths)))["merges"], 2)
        check("one listing is one merge (null)", analyze(runs_from_gh(load_rows(paths[:1])))["merges"], 1)

    failures += flow_self_test()

    print(f"{'FAILED' if failures else 'ok'}: merge_throughput.py self-test")
    return 1 if failures else 0


def flow_self_test() -> int:
    """The flow board's arms, offline over a throwaway repository.

    THE FIXTURE (one of each thing the board must tell apart): a roster edit
    merged on main that closes R1-A, one group-carrying merge (#1 from
    fix/r1-a), one record merge (#9 from record/autofix), one fly-in (#5 from
    hotfix/urgent), and #1's two bus verdicts -- blocked on harness, then
    merge. Every exact count below is a function of that fixture.

    THE CONTROLS. A null control reads the unchanged fixture twice and
    demands byte-identical boards; its companion moves `--until` past the
    events and demands they leave the board. The perturbations are keyed to
    the line each pins: `--record-prefix fix/` reclassifies the group and
    roster merges (the record predicate), a window starting after the events
    zeroes every count (the window predicate), a missing roster and a
    repository with no review refs each read UNAVAILABLE rather than 0
    (the source predicate).
    """
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init

    failures = 0

    def check(name: str, got, want) -> None:
        nonlocal failures
        if got == want:
            print(f"  ok   {name}")
        else:
            failures += 1
            print(f"  FAIL {name}: got {got!r}, want {want!r}")

    def check_true(name: str, cond: bool, got="") -> None:
        nonlocal failures
        if cond:
            print(f"  ok   {name}")
        else:
            failures += 1
            print(f"  FAIL {name}: {got!r}")

    env = throwaway_git_env()
    with tempfile.TemporaryDirectory() as d:
        R = Path(d)
        throwaway_git_init(R, "-q", "-b", "main")

        def g(*args, e=None) -> str:
            return subprocess.run(
                ["git", "-C", d, *args], capture_output=True, text=True,
                check=True, env={**env, **(e or {})}).stdout.strip()

        ix = {"GIT_INDEX_FILE": str(R / ".git" / "fixture-index")}

        def mk(parents: str, files: dict, msg: str, t: str) -> str:
            g("read-tree", *([parents.split()[0]] if parents else ["--empty"]),
              e=ix)
            for path, text in files.items():
                (R / "blob").write_text(text)
                blob = g("hash-object", "-w", str(R / "blob"), e=ix)
                g("update-index", "--add", "--cacheinfo",
                  f"100644,{blob},{path}", e=ix)
            return g("commit-tree", g("write-tree", e=ix),
                     *[x for p in parents.split() for x in ("-p", p)],
                     "-m", msg, e={**ix, "GIT_COMMITTER_DATE": t,
                                   "GIT_AUTHOR_DATE": t})

        ROSTER = roster_lib.ROSTERS_DIR + "/wave-r1-groups.json"
        CRIT = roster_lib.CRITICAL_PATH_NAME

        def ros(a="fixing") -> str:
            return json.dumps({"groups": [
                {"group": "R1-A", "lane": "IN", "size": "M",
                 "resume": {"stage": a}},
                {"group": "R1-B", "lane": "F", "size": "S",
                 "resume": {"stage": "not-started"}},
                {"group": "R1-C", "lane": "IN", "size": "L",
                 "resume": {"stage": "fixing"}}]})

        T = lambda h, m=0: f"2026-10-01T{h:02d}:{m:02d}:00Z"
        crit = json.dumps({"critical": ["R1-C"]})
        m0 = mk("", {ROSTER: ros(), CRIT: crit}, "root", T(0))
        rb = mk(m0, {ROSTER: ros("done")}, "roster: R1-A done", T(1))
        m1 = mk(f"{m0} {rb}", {ROSTER: ros("done")},
                "Merge pull request #7 from o/fix/audit-r1-roster", T(1, 15))
        b1 = mk(m0, {"f1": "1\n"}, "pr1 work", T(0, 30))
        m2 = mk(f"{m1} {b1}", {"f1": "1\n"},
                "Merge pull request #1 from o/fix/r1-a", T(2))
        rc = mk(m2, {"dev/programme/delivery/9.md": "row\n"}, "record row",
                T(2, 20))
        m3 = mk(f"{m2} {rc}", {"dev/programme/delivery/9.md": "row\n"},
                "Merge pull request #9 from o/record/autofix", T(2, 30))
        fb = mk(m3, {"hot": "x\n"}, "flyin", T(3))
        m4 = mk(f"{m3} {fb}", {"hot": "x\n"},
                "Merge pull request #5 from o/hotfix/urgent", T(3, 10))
        g("update-ref", "refs/remotes/origin/main", m4)
        g("update-ref", "refs/remotes/origin/roster", m1)

        roster = json.loads(ros("done"))
        ctx = FlowCtx(repo=R, tree="refs/remotes/origin/main", remote="origin",
                      roster=roster, roster_unavailable="",
                      roster_ref="refs/remotes/origin/roster",
                      roster_path=ROSTER, prefix="", record_prefix="record/",
                      critical=roster_lib.critical_path_groups(
                          R, "refs/remotes/origin/roster"))
        a, b = rs.when(T(0)), rs.when(T(5))

        # The bus refs do not exist yet: the yield rows are UNAVAILABLE, never
        # 0 -- the source predicate's first arm.
        r = period(ctx, a, b)
        check("flow: no review refs reads UNAVAILABLE, not zero",
              (r["yield"][0], bool(r["yield"][1])), (None, True))
        check_true("flow: ...and the reason names the bus",
                   "bus" in r["yield"][1] or "review" in r["yield"][1],
                   r["yield"][1])

        empty = g("hash-object", "-t", "tree", "-w", "/dev/null")

        def verdict(pr: int, kind: str, head: str, t: str, cls: str = "") -> None:
            ref = f"refs/remotes/origin/review/{pr}"
            par = subprocess.run(["git", "-C", d, "rev-parse", "-q",
                                  "--verify", ref], capture_output=True,
                                 text=True)
            subj = (f"verdict: #{pr} Fix review: {kind} {head}"
                    + (f" {cls}:" if cls else ""))
            sha = g("commit-tree", empty,
                    *(["-p", par.stdout.strip()] if par.returncode == 0 else []),
                    "-m", subj, e={"GIT_COMMITTER_DATE": t,
                                   "GIT_AUTHOR_DATE": t})
            g("update-ref", ref, sha)

        verdict(1, "blocked", b1, T(1, 10), "harness")
        verdict(1, "merge", b1, T(1, 50))

        r = period(ctx, a, b)
        # 1 -- the two predicates each main move is classified by.
        check("flow: main moves split group/record/roster/fly-in",
              (r["moves"][0]["counts"]["group"], r["moves"][0]["counts"]["record"],
               r["moves"][0]["counts"]["roster"], r["moves"][0]["counts"]["flyin"]),
              (1, 1, 1, 1))
        check("flow: fly-ins closed is the fly-in merge count", r["flyins"][0], 1)
        # 2 -- the roster predicate: a stage entering DONE_STAGES closes once.
        check("flow: roster groups closed", r["closed"][0], 1)
        # 3 -- the verdict predicate: #1's first verdict is blocked.
        check("flow: first-pass yield is the first verdict's kind",
              r["yield"][0], (0, 1))
        check("flow: the blocked-class mix counts the class",
              dict(r["classes"][0]), {"harness": 1})
        # 4 -- the lead-time rule: merge time minus the branch's first commit.
        check("flow: lead time per size (h)", r["lead"][0], ({"M": [1.5]}, 0))
        # 5 -- the lane rule: A from the published critical set, F/FLY and
        # C/tooling from the roster's own lane, everything else B.
        check("flow: WIP by flow lane", flow_wip(roster, ctx.critical),
              {"A": 1, "B": 0, "C": 0, "F": 1})

        # PERTURBATION 1 -- the record key is `record_prefix`, not a name.
        ctx_fix = replace(ctx, record_prefix="fix/")
        r = period(ctx_fix, a, b)
        check("flow: --record-prefix fix/ reclassifies the group and roster merges",
              (r["moves"][0]["counts"]["group"], r["moves"][0]["counts"]["record"],
               r["moves"][0]["counts"]["flyin"]), (0, 2, 2))
        # PERTURBATION 2 -- the window predicate: an empty hour moves nothing.
        r = period(ctx, rs.when(T(3, 30)), rs.when(T(5)))
        check("flow: a window after the events counts nothing",
              (r["moves"][0]["counts"]["group"], r["closed"][0], r["yield"][0]), (0, 0, (0, 0)))

        # THE NULL CONTROL and its companion: identical input, identical
        # board; a moved `--until` changes it (the board is a function of the
        # refs, not of when it ran).
        until = rs.when(T(5))
        first, second = board(ctx, until), board(ctx, until)
        check_true("flow null control: an unchanged fixture reads identical",
                   render_board(first) == render_board(second))
        check_true("flow null control is not vacuous: a moved until changes it",
                   render_board(first) != render_board(board(ctx, rs.when(T(4)))))
        text = render_board(first)
        for frag in ("# Flow board", "last 1 h", "last 24 h", "Takt 1.0",
                     "0 / 1.0", "1 / 24.0", "harness:1"):
            check_true(f"flow board renders {frag!r}", frag in text,
                       text[:400])

        # UNAVAILABLE, never zeros, for each unreadable source.
        r = period(replace(ctx, roster=None,
                           roster_unavailable="no roster at refs/remotes/origin/roster"),
                   a, b)
        text = render_board(board(replace(
            ctx, roster=None,
            roster_unavailable="no roster at refs/remotes/origin/roster"), until))
        check_true("flow: an unreadable roster is UNAVAILABLE, never zero",
                   r["closed"][0] is None and "UNAVAILABLE" in text
                   and "0 / 24.0" not in text, text[:400])
        text = render_board(board(replace(ctx, tree="refs/heads/absent"), until))
        check_true("flow: an unreadable tree is UNAVAILABLE, never zero",
                   "UNAVAILABLE" in text, text[:400])

        # --- #2883: every way a source can fail to be read -------------------
        # The rule is the module's last line. Each arm below failed at the
        # reviewed head: a crash, or a numeric zero where a reader had nothing.
        import contextlib
        import io

        def run_flow(argv: list) -> tuple:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = flow_main(argv)
            return rc, out.getvalue(), err.getvalue()

        # B1: the CLI shape `state_docs` runs. A ref whose roster is malformed
        # JSON raised json.JSONDecodeError out of flow_main: rc 1, no
        # UNAVAILABLE, and state_docs' Refuse then dropped the plan table.
        bad = mk(m0, {ROSTER: "{not json"}, "roster: broken", T(3, 40))
        g("update-ref", "refs/remotes/origin/roster-bad", bad)
        rc, out, err = run_flow(["--repo", d,
                                 "--tree", "refs/remotes/origin/main",
                                 "--roster-ref", "refs/remotes/origin/roster-bad",
                                 "--until", T(5)])
        check("flow: an unparseable roster at --roster-ref exits 0 with "
              "UNAVAILABLE, never a traceback",
              (rc, "UNAVAILABLE" in out), (0, True))
        check_true("flow: ...and the reason names the JSON",
                   "JSON" in out, out[:300])

        # B1b: a roster that parses but is not a roster. `groups_of` indexed
        # it and raised AttributeError out of the same CLI.
        shaped = mk(m0, {ROSTER: json.dumps([])}, "roster: a list", T(3, 45))
        g("update-ref", "refs/remotes/origin/roster-shaped", shaped)
        rc, out, err = run_flow(["--repo", d,
                                 "--tree", "refs/remotes/origin/main",
                                 "--roster-ref", "refs/remotes/origin/roster-shaped",
                                 "--until", T(5)])
        check("flow: a roster that parses but is not one reads UNAVAILABLE",
              (rc, "UNAVAILABLE" in out), (0, True))

        # B1c: no window end at all -- the second way the board refused before
        # reading anything, and took the plan table down with it.
        roster_file = R / "roster-on-disk.json"
        roster_file.write_text(ros("done"), encoding="utf-8")
        rc, out, err = run_flow(["--repo", d,
                                 "--tree", "refs/heads/absent",
                                 "--roster-file", str(roster_file)])
        check("flow: no readable window end renders UNAVAILABLE, never a "
              "refusal", (rc, "UNAVAILABLE" in out), (0, True))

        # B2: a roster commit that will not parse is UNAVAILABLE, not a zero
        # with an empty reason on the takt headline.
        bad_ctx = replace(ctx, roster_ref="refs/remotes/origin/roster-bad",
                          roster_path=ROSTER)
        r = period(bad_ctx, rs.when(T(3, 30)), rs.when(T(4)))
        check_true("flow: a malformed roster commit is UNAVAILABLE, never a "
                   "zero with an empty reason",
                   r["closed"][0] is None and bool(r["closed"][1]),
                   r["closed"])

        # B3: the critical-path source. A ref that publishes no file puts no
        # group on the critical path (a measurement); a file that is there and
        # cannot be read is UNAVAILABLE, or lane A reads 0 and lane B absorbs
        # its groups.
        nc = mk("", {ROSTER: ros("done")}, "roster only", T(0))
        bc = mk("", {ROSTER: ros("done"), CRIT: "{not json"}, "broken", T(0))
        g("update-ref", "refs/remotes/origin/roster-nocrit", nc)
        g("update-ref", "refs/remotes/origin/roster-badcrit", bc)
        crit_nc, why_nc = critical_read(R, "refs/remotes/origin/roster-nocrit",
                                        roster)
        check("flow: a ref publishing no critical path reads (set, '')",
              (crit_nc, why_nc), (set(), ""))
        crit_bc, why_bc = critical_read(R, "refs/remotes/origin/roster-badcrit",
                                        roster)
        check_true("flow: an unreadable critical path is UNAVAILABLE with its "
                   "reason", crit_bc is None and "not JSON" in why_bc, why_bc)
        # `critical_of` is the lossy accessor (the reviewer's harness and any
        # caller that only needs the membership test): a file source has no
        # reason to carry, so it reads the computed chain as a plain set. The
        # fixture's open groups have no after-edges, so the chain is its first
        # open group.
        check("flow: critical_of reads a file source's computed chain",
              critical_of(R, None, json.loads(ros())), {"r1-a"})
        b_nc = board(replace(ctx, roster_ref="refs/remotes/origin/roster-nocrit",
                             critical=crit_nc, critical_unavailable=why_nc), until)
        b_bc = board(replace(ctx, roster_ref="refs/remotes/origin/roster-badcrit",
                             critical=crit_bc, critical_unavailable=why_bc), until)
        check("flow: no published critical path puts every open group in B",
              b_nc["wip"], ({"A": 0, "B": 1, "C": 0, "F": 1}, ""),
              )
        check("flow: WIP refuses to answer without a readable critical set, "
              "never guesses lane A 0", flow_wip(roster, None), None)
        check_true("flow: an unreadable critical path makes the WIP row "
                   "UNAVAILABLE, never A 0",
                   b_bc["wip"][0] is None
                   and "UNAVAILABLE" in render_board(b_bc).split("### WIP")[1],
                   b_bc["wip"])

        # B4: the window is closed at both ends, so the default window -- whose
        # end is a ref tip's own committer time -- counts the tip's merge.
        r = period(ctx, a, rs.when(T(2, 30)))
        check("flow: a record merge exactly at the window's end is counted",
              r["moves"][0]["counts"]["record"], 1)
        u = flow_default_until(R, "refs/remotes/origin/main",
                               "refs/remotes/origin/roster")
        r = period(ctx, u - timedelta(hours=24), u)
        check("flow: the default window counts the tip merge at exactly its "
              "end", (r["moves"][0]["counts"]["flyin"],
                      r["moves"][0]["counts"]["record"]), (1, 1))
        # B4b: the third measure's window. #1's first verdict -- the blocked
        # one -- is committed at 01:10; a window ending exactly there must
        # count it, or the 1 h row's yield is a zero for the verdict that
        # opened the window's last event.
        r = period(ctx, a, rs.when(T(1, 10)))
        check("flow: a verdict at exactly the window's end is counted",
              (r["yield"][0], dict(r["classes"][0])), ((0, 1), {"harness": 1}))
        # ...and the roster measure's: the roster ref's tip is the merge that
        # carries the closing stage at 01:15 (the first-parent walk sees the
        # closing when it lands on the roster branch, not on the work commit
        # it came from). A window ending exactly at that tip is the shape the
        # default window takes when the roster is the later ref -- the closing
        # commit must be in it.
        r = period(ctx, a, rs.when(T(1, 15)))
        check("flow: a roster commit at exactly the window's end closes in it",
              r["closed"][0], 1)

        # B5: an object git cannot read. A path probe that fails alike for an
        # absent path and an unreadable object (`cat-file -e` reads the blob;
        # `rev-parse --verify --quiet` answers rc 1 for an absent path and for
        # an unreadable tree on the way to it) turned each into "nothing here"
        # -- a zero on the takt headline, lane A 0 (#2883 review 2). Each
        # fixture's content is unique, so dropping its object breaks no other
        # arm; the drop asserts the object was a loose file first.
        def drop(sha: str) -> bool:
            p = R / ".git" / "objects" / sha[:2] / sha[2:]
            had = p.is_file()
            p.unlink(missing_ok=True)
            return had
        gone = mk(m0, {ROSTER: ros("done") + " " * 7}, "roster: blob gone",
                  T(3, 40))
        g("update-ref", "refs/remotes/origin/roster-gone", gone)
        check_true("flow: fixture -- the in-window roster blob was loose and "
                   "is dropped", drop(g("rev-parse", f"{gone}:{ROSTER}")))
        r = period(replace(ctx, roster_ref="refs/remotes/origin/roster-gone",
                           roster_path=ROSTER), rs.when(T(3, 30)), rs.when(T(4)))
        check_true("flow: a roster commit whose blob git cannot read is "
                   "UNAVAILABLE, never a zero with an empty reason",
                   r["closed"][0] is None and "cannot read" in r["closed"][1],
                   r["closed"])
        cg = mk("", {ROSTER: ros("done"), CRIT: crit + " " * 7}, "crit gone",
                T(0))
        g("update-ref", "refs/remotes/origin/roster-critgone", cg)
        check_true("flow: fixture -- the critical-path blob was loose and is "
                   "dropped", drop(g("rev-parse", f"{cg}:{CRIT}")))
        crit_cg, why_cg = critical_read(R, "refs/remotes/origin/roster-critgone",
                                        roster)
        check_true("flow: a critical-path blob git cannot read is UNAVAILABLE "
                   "with git's reason", crit_cg is None and "cannot read" in why_cg,
                   (crit_cg, why_cg))
        b_cg = board(replace(ctx, roster_ref="refs/remotes/origin/roster-critgone",
                             critical=crit_cg, critical_unavailable=why_cg), until)
        check_true("flow: ...and the WIP row is UNAVAILABLE, never A 0",
                   b_cg["wip"][0] is None
                   and "UNAVAILABLE" in render_board(b_cg).split("### WIP")[1],
                   b_cg["wip"])
        # The probe's third answer, consumed. A tree git cannot read fails the
        # first-parent `log -- path` before `state()` is reached, so no fixture
        # drives `blob_at`'s None into it; the stub does, and pins that the
        # walk never reads it as "no roster yet".
        real_blob_at = roster_lib.blob_at
        roster_lib.blob_at = lambda *_: (None, "cannot read (stubbed probe)")
        try:
            r = period(bad_ctx, rs.when(T(3, 30)), rs.when(T(4)))
        finally:
            roster_lib.blob_at = real_blob_at
        check("flow: a path probe that cannot answer is UNAVAILABLE in the "
              "roster walk, never {}", r["closed"],
              (None, "roster unreadable before the window: cannot read "
                     "(stubbed probe)"))
        # Null control: the same shape with every object intact reads its
        # measurement, so the arms above are the drop, not the fixture.
        intact = mk(m0, {ROSTER: ros("done")}, "roster: intact", T(3, 40))
        g("update-ref", "refs/remotes/origin/roster-intact", intact)
        r = period(replace(ctx, roster_ref="refs/remotes/origin/roster-intact",
                           roster_path=ROSTER), rs.when(T(3, 30)), rs.when(T(4)))
        check("flow: null control -- the intact roster commit closes its group",
              r["closed"], (1, ""))
    return failures


# ---------------------------------------------------------------- the flow board
#
# Flow board (Lean study K1). The owner's demand is one roster group merged per
# hour; this board is how a flow change can show it worked. Every measure below
# has one rule, stated in `render_board`'s Rules section, and every source is
# read through the instrument that owns it: the first-parent log of the tree,
# the review bus through `review_strength`, the roster through `roster_lib`.
# An unreadable source prints UNAVAILABLE with its reason -- never a zero,
# which would read as a measured "nothing happened".
TAKT_PER_HOUR = 1.0
FLOW_PERIODS = (("last 1 h", 1.0), ("last 24 h", 24.0))
FLY_LANES = frozenset({"F", "FLY"})
PROCESS_LANES = frozenset({"C", "tooling"})


@dataclass(frozen=True)
class FlowCtx:
    """One run's inputs. `roster` is None exactly when `roster_unavailable`
    says why -- the two are set together, so a caller cannot forget one. The
    same holds for `critical` and `critical_unavailable`: None is UNAVAILABLE,
    never "nothing is critical" (which is the empty set)."""
    repo: Path
    tree: str
    remote: str
    roster: dict | None
    roster_unavailable: str
    roster_ref: str | None
    roster_path: str | None
    prefix: str
    record_prefix: str
    critical: set | None
    critical_unavailable: str = ""


def _ok(value):
    return (value, "")


def _na(why: str):
    return (None, why)


def _git_ro(repo: Path, *args: str):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def flow_tip_time(repo: Path, ref: str) -> datetime | None:
    """The ref tip's committer time, or None when the ref is unreadable."""
    r = _git_ro(repo, "log", "-1", "--format=%cI", ref)
    return parse_iso(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def flow_default_until(repo: Path, tree: str, roster_ref: str | None) -> datetime | None:
    """The window's end when `--until` is not given: the later of the tree
    tip and the roster ref tip. Both are refs the state beat watches, so a
    rerun over unchanged refs renders the same bytes -- the property the
    beat's already-current check depends on."""
    times = [t for t in (flow_tip_time(repo, tree),
                         flow_tip_time(repo, roster_ref) if roster_ref else None)
             if t is not None]
    return max(times) if times else None


def _merge_files(repo: Path, first_parent: str, sha: str) -> list[str] | None:
    """The paths a merge changed against its first parent; None when git
    cannot answer (the classifier then falls back to the branch name)."""
    r = _git_ro(repo, "diff-tree", "-r", "--name-only", "--no-commit-id",
                first_parent, sha)
    return r.stdout.split() if r.returncode == 0 else None


def move_kind(branch: str, files: list[str] | None, roster: dict | None,
              record_prefix: str) -> str:
    """One main move's kind, by this order: record, roster-edit, group, fly-in.

    `record` is the branch prefix the record tooling publishes; `roster-edit`
    is a merge whose diff touches the roster directory (or, when the diff is
    unreadable, a branch naming a roster), because the path is the property
    and the branch name is its fallback; `group` is `roster_lib`'s own
    branch-to-group answer; everything else is a fly-in.
    """
    if branch.startswith(record_prefix):
        return "record"
    if files is not None:
        if any(f.startswith(roster_lib.ROSTERS_DIR + "/") for f in files):
            return "roster"
    elif "roster" in branch:
        return "roster"
    if roster is not None and roster_lib.group_for_branch(roster, branch):
        return "group"
    return "flyin"


def flow_moves(ctx: FlowCtx, a: datetime, b: datetime):
    """The first-parent PR merges of the tree in [a, b], classified.

    The window is CLOSED at both ends. Its end is a ref tip's own committer
    time (`flow_default_until`), so a half-open window would drop the newest
    merge -- the tip of whichever ref is later -- from every column, including
    the 1 h column whose whole job is the last hour (#2883).
    """
    r = _git_ro(ctx.repo, "log", "--first-parent",
                "--format=%H%x09%P%x09%cI%x09%s", ctx.tree)
    if r.returncode:
        return _na(f"cannot read {ctx.tree}: {(r.stderr or r.stdout).strip()[:120]}")
    counts = {"group": 0, "record": 0, "roster": 0, "flyin": 0}
    moves = []
    for line in r.stdout.splitlines():
        parts = line.split("\t", 3)
        if len(parts) != 4:
            continue
        sha, parents, stamp, subject = parts
        ps = parents.split()
        m = rs.MERGE_RE.match(subject)
        if not m or len(ps) != 2:
            continue
        when = rs.when(stamp)
        if not a <= when <= b:
            continue
        kind = move_kind(m.group(2), _merge_files(ctx.repo, ps[0], sha),
                         ctx.roster, ctx.record_prefix)
        counts[kind] += 1
        moves.append({"sha": sha, "head": ps[1], "t": when,
                      "branch": m.group(2), "pr": int(m.group(1)),
                      "kind": kind})
    return _ok({"counts": counts, "moves": moves})


def flow_closed(ctx: FlowCtx, a: datetime, b: datetime):
    """Prefix roster groups whose stage enters DONE_STAGES in [a, b].

    Every first-parent commit of the roster ref touching the roster path is
    compared with the one before it, so a group re-opened and re-closed counts
    twice. A file source has no history to walk and is UNAVAILABLE. A commit
    whose roster cannot be read -- git's own failure, invalid JSON, or JSON
    that is not a roster -- is UNAVAILABLE too: `{}` would read as a commit
    that closed nothing (#2883). A commit that carries no roster yet closes
    nothing, and is that measurement.
    """
    if ctx.roster is None:
        return _na(ctx.roster_unavailable or "roster unreadable")
    if not ctx.roster_ref:
        return _na("a --roster-file carries no first-parent history")
    path = ctx.roster_path
    if not path:
        try:
            path = roster_lib.roster_path(str(ctx.repo), ctx.roster_ref)
        except roster_lib.RosterNotFound as e:
            return _na(f"roster path unreadable: {e}")

    def state(sha: str) -> tuple[dict | None, str]:
        """The done-flag map at one commit, or None and why it is unreadable."""
        there, why = roster_lib.blob_at(str(ctx.repo), sha, path)
        if there is None:
            return None, why
        if not there:
            return {}, ""                      # no roster at this commit yet
        rr = _git_ro(ctx.repo, "show", f"{sha}:{path}")
        if rr.returncode:
            return None, (f"cannot read {path} at {sha[:12]}: "
                          f"{(rr.stderr or rr.stdout).strip()[:120]}")
        try:
            roster = json.loads(rr.stdout)
        except ValueError as e:
            return None, f"{path} at {sha[:12]} is not JSON: {e}"
        why = roster_lib.roster_shape(roster)
        if why:
            return None, f"{path} at {sha[:12]} is not a roster: {why}"
        groups = roster_lib.groups_of(roster)
        return {k: (v.get("resume") or {}).get("stage") in roster_lib.DONE_STAGES
                for k, v in groups.items() if k.startswith(ctx.prefix)}, ""

    log = _git_ro(ctx.repo, "log", "--first-parent", "--format=%H%x09%cI",
                  ctx.roster_ref, "--", path)
    if log.returncode:
        return _na(f"cannot read {ctx.roster_ref}: "
                   f"{(log.stderr or log.stdout).strip()[:120]}")
    before = _git_ro(ctx.repo, "rev-list", "-1", "--first-parent",
                     f"--before={a.isoformat()}", ctx.roster_ref).stdout.strip()
    prev, why = state(before) if before else ({}, "")
    if prev is None:
        return _na(f"roster unreadable before the window: {why}")
    closed = 0
    for line in reversed(log.stdout.splitlines()):
        sha, stamp = line.split("\t")
        if not a <= rs.when(stamp) <= b:
            continue
        cur, why = state(sha)
        if cur is None:
            return _na(why)
        closed += sum(done and not prev.get(k, False)
                      for k, done in cur.items())
        prev = cur
    return _ok(closed)


def _bus_verdicts(ctx: FlowCtx):
    """(pr, time, kind, class) for every verdict on the bus, oldest first.

    The grammar is `review_strength`'s -- its ref patterns and its
    PREFIX_RE/VERDICT_RE, imported, never copied. Its `load()` is not used
    because it reads `VERDICT.md` per verdict (the nonce, cloud family and
    model this board does not measure); that is ~900 `git show` calls and
    takes minutes on this repository, which a beat cannot pay per pass. None
    of the review refs at all is None (UNAVAILABLE); refs with no subject in
    the window is a real empty list.
    """
    refs_ = []
    for pattern in (f"refs/remotes/{ctx.remote}/review/",
                    "refs/tags/archive/review/"):
        r = _git_ro(ctx.repo, "for-each-ref", "--format=%(refname)", pattern)
        if r.returncode:
            raise OSError(f"cannot list {pattern}: "
                          f"{(r.stderr or r.stdout).strip()[:120]}")
        refs_ += r.stdout.split()
    if not refs_:
        return None
    # ONE `git log` over every review ref: they share history (each verdict
    # commit's parent is the previous verdict on the ref), so git dedups the
    # walk and a process per ref would be ~400 spawns for the same commits.
    r = _git_ro(ctx.repo, "log", "--format=%H%x09%cI%x09%s", *refs_)
    if r.returncode:
        raise OSError(f"cannot read the review refs: "
                      f"{(r.stderr or r.stdout).strip()[:120]}")
    seen, out = set(), []
    for line in r.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        sha, stamp, subject = parts
        if sha in seen or not rs.PREFIX_RE.match(subject):
            continue
        seen.add(sha)
        m = rs.VERDICT_RE.match(subject)
        if not m:
            continue
        out.append((int(m.group(1)), rs.when(stamp), m.group(2),
                    m.group(4) or ""))
    out.sort(key=lambda v: v[1])
    return out


def flow_verdicts(ctx: FlowCtx, a: datetime, b: datetime):
    """(first-pass yield, blocked-class mix) over the period's bus verdicts.

    Yield counts only PRs whose FIRST verdict falls in the period, so a PR
    reviewed earlier and re-reviewed now is not counted as a first pass. No
    review ref at all is UNAVAILABLE; refs present with no verdict in the
    window is a real 0/0. The window is CLOSED at both ends, like the other
    two measures: a verdict committed at exactly the window's end is in it,
    which matters because the default end is a ref tip's own committer time
    (#2883).
    """
    try:
        verdicts = _bus_verdicts(ctx)
    except OSError as e:  # a broken bus, not a zero
        why = f"bus unreadable: {e}"
        return _na(why), _na(why)
    if verdicts is None:
        return _na("no review/verdict bus refs"), _na("no review/verdict bus refs")
    window = [v for v in verdicts if a <= v[1] <= b]
    first = {}
    for v in verdicts:
        first.setdefault(v[0], v)
    judged = [v for v in window if first[v[0]] is v]
    yield_ = (sum(v[2] == "merge" for v in judged), len(judged))
    classes = Counter(v[3] for v in window if v[2] == "blocked")
    return _ok(yield_), _ok(classes)


def _lead_hours(repo: Path, move: dict) -> float | None:
    """Merge time minus the earliest commit the branch carries.

    The branch's own commits are `<merge>^1..<head>`; a head git does not hold
    falls back to the head commit itself, and an unreadable one is unresolved.
    """
    r = _git_ro(repo, "log", "--format=%cI",
                f"{move['sha']}^1..{move['head']}")
    stamps = [rs.when(x) for x in r.stdout.split()] if r.returncode == 0 else []
    if not stamps:
        r = _git_ro(repo, "log", "-1", "--format=%cI", move["head"])
        if r.returncode or not r.stdout.strip():
            return None
        stamps = [rs.when(r.stdout.strip())]
    return round((move["t"] - min(stamps)).total_seconds() / 3600, 2)


def flow_lead(ctx: FlowCtx, moves: list[dict]):
    """Lead time (hours) per roster size, over the period's group merges."""
    if ctx.roster is None:
        return _na(ctx.roster_unavailable or "roster unreadable")
    groups = roster_lib.groups_of(ctx.roster)
    by_size: dict = {}
    unresolved = 0
    for move in moves:
        if move["kind"] != "group":
            continue
        gid = roster_lib.group_for_branch(ctx.roster, move["branch"])
        size = (groups.get(gid) or {}).get("size")
        hours = _lead_hours(ctx.repo, move)
        if hours is None or not size:
            unresolved += 1
            continue
        by_size.setdefault(size, []).append(hours)
    return _ok((by_size, unresolved))


def _lane_of(gid: str, group: dict, critical: set | None) -> str:
    """The flow lane of one open group. The published critical-path set is A;
    the roster's own `lane` names F (F, FLY) and C (C, tooling); the rest is
    B product. A group in the critical set is A whatever its lane says."""
    if critical and roster_lib.norm_group(gid) in critical:
        return "A"
    lane = str(group.get("lane") or "")
    if lane in FLY_LANES:
        return "F"
    if lane in PROCESS_LANES:
        return "C"
    return "B"


def flow_wip(roster: dict | None, critical: set | None) -> dict | None:
    """Open groups by flow lane, a snapshot at the window's end.

    None when the roster cannot be read, and None when the critical-path set
    could not be either: a None `critical` is UNAVAILABLE, not an empty set,
    and answering it as one would print lane A 0 while lane B swallowed A's
    groups (#2883). "No group is critical" is `set()`.
    """
    if roster is None or critical is None:
        return None
    out = {"A": 0, "B": 0, "C": 0, "F": 0}
    for gid, group in roster_lib.groups_of(roster).items():
        if roster_lib.is_open(group):
            out[_lane_of(gid, group, critical)] += 1
    return out


def critical_read(repo: Path, roster_ref: str | None,
                  roster: dict | None) -> tuple[set | None, str]:
    """The critical-path set and, when it cannot be read, the reason.

    `(set, "")` when the source answered -- `set()` is the measurement "the
    ref publishes no critical path, so no group is on it". `(None, why)` when
    a file is there and cannot be read: a board must print that, because lane
    A would otherwise read 0 and lane B absorb the groups that belong to it
    (#2883). A roster that is already UNAVAILABLE is None with no reason of
    its own; the roster carries the reason.
    """
    if roster is None:
        return None, ""
    if roster_ref:
        return roster_lib.critical_path_read(str(repo), roster_ref)
    return {roster_lib.norm_group(g) for g in roster_lib.critical_path(roster)}, ""


def critical_of(repo: Path, roster_ref: str | None, roster: dict | None) -> set | None:
    """The critical-path set alone, or None.

    The lossy accessor of `critical_read`, for callers that only need the
    membership test. It keeps the reviewed head's contract exactly -- None is
    both "unreadable" and "no file", and an empty set reads as None too --
    so the control that distinguishes them is the board's, which reads
    `critical_read`.
    """
    return critical_read(repo, roster_ref, roster)[0] or None


def period(ctx: FlowCtx, a: datetime, b: datetime) -> dict:
    """Every per-period measure over [a, b]; each value is `(value, reason)`."""
    if ctx.roster is None:
        # group vs fly-in is not answerable without the roster, so the split
        # is unavailable rather than a wrong fly-in count.
        why = ctx.roster_unavailable or "roster unreadable"
        moves, flyins, lead = _na(why), _na(why), _na(why)
    else:
        moves = flow_moves(ctx, a, b)
        if moves[0] is None:
            flyins, lead = _na(moves[1]), _na(moves[1])
        else:
            counts = moves[0]["counts"]
            flyins = _ok(counts["flyin"])
            lead = flow_lead(ctx, moves[0]["moves"])
    yield_, classes = flow_verdicts(ctx, a, b)
    return {"moves": moves, "flyins": flyins, "lead": lead,
            "closed": flow_closed(ctx, a, b),
            "yield": yield_, "classes": classes}


def board(ctx: FlowCtx, until: datetime | None) -> dict:
    """The whole board: both rolling periods plus the WIP snapshot.

    `until` is None when neither watched ref yields a commit time. There is
    then no window, so every per-period measure is UNAVAILABLE with that
    reason rather than a zero -- the board's own last rule -- and the board is
    still rendered, so a state beat that cannot read a ref publishes the
    reason instead of refusing and dropping the documents generated before it
    (#2883).
    """
    if until is None:
        why = (f"no window end: neither {ctx.tree} nor "
               f"{ctx.roster_ref or 'the roster file'} has a readable "
               "commit time")
        blank = {key: (None, why) for key in
                 ("moves", "flyins", "lead", "closed", "yield", "classes")}
        periods = [(label, hours, dict(blank)) for label, hours in FLOW_PERIODS]
    else:
        periods = [(label, hours, period(
            ctx, until - timedelta(hours=hours), until))
            for label, hours in FLOW_PERIODS]
    if ctx.roster is None:
        wip = _na(ctx.roster_unavailable or "roster unreadable")
    elif ctx.critical is None:
        wip = _na(ctx.critical_unavailable or "critical path unreadable")
    else:
        wip = _ok(flow_wip(ctx.roster, ctx.critical))
    return {"until": until, "periods": periods, "wip": wip, "ctx": ctx}


def _cell(measure) -> str:
    value, why = measure
    return f"UNAVAILABLE ({why})" if value is None else ""


def _closed_cell(measure, hours: float) -> str:
    value, why = measure
    if value is None:
        return _cell(measure)
    return f"{value} / {hours * TAKT_PER_HOUR:.1f}"


def _count_cell(measure) -> str:
    value, why = measure
    return str(value) if value is not None else _cell(measure)


def _moves_cell(measure) -> str:
    value, why = measure
    if value is None:
        return _cell(measure)
    counts = value["counts"]
    return (f"{counts['group']} / {counts['record']} / "
            f"{counts['roster']} / {counts['flyin']}")


def _yield_cell(measure) -> str:
    value, why = measure
    if value is None:
        return _cell(measure)
    first_pass, judged = value
    return f"{first_pass}/{judged} ({first_pass / judged:.2f})" if judged else "0/0 (-)"


def _classes_cell(measure) -> str:
    value, why = measure
    if value is None:
        return _cell(measure)
    return ", ".join(f"{k}:{v}" for k, v in sorted(value.items())) or "none"


def _lead_cell(measure) -> str:
    value, why = measure
    if value is None:
        return _cell(measure)
    by_size, unresolved = value
    parts = []
    for size in sorted(by_size):
        values = sorted(by_size[size])
        parts.append(f"{size} n={len(values)} p50={percentile(values, 0.5):.2f} "
                     f"max={max(values):.2f}")
    if unresolved:
        parts.append(f"unresolved {unresolved}")
    return "; ".join(parts) or "none"


FLOW_RULES = (
    "every period is CLOSED at both ends: an event at exactly the window's "
    "start or end is counted, so the default window -- which ends at a ref "
    "tip's own committer time -- includes the tip's merge.",
    "roster groups closed: a group whose resume.stage enters roster_lib's "
    "DONE_STAGES in the period, counted per first-parent commit of the roster "
    "ref; takt is 1.0 group per hour, so the period's demand is its hours.",
    "fly-ins closed: a first-parent PR merge of the tree in the period whose "
    "branch maps to no roster group and is neither a record nor a roster edit.",
    "main moves: each first-parent PR merge of the tree in the period, by "
    "kind -- group-carrying (roster_lib's branch-to-group answer), record "
    "(--record-prefix), roster-edit (the merge's diff touches the roster "
    "directory), fly-in (the rest).",
    "first-pass yield: of the PRs whose FIRST bus verdict falls in the "
    "period, the share whose first verdict is `merge`; a PR whose first "
    "verdict predates the period is not judged in it.",
    "blocked-class mix: every blocked verdict in the period, by the class "
    "word its subject carries.",
    "lead time per size: merge time minus the earliest commit the group's "
    "branch carries, over group-carrying merges whose roster group names a "
    "size; n, p50 and max hours.",
    "WIP by lane: open roster groups at the window's end -- A when in the "
    "published critical-path set, F for roster lanes F/FLY, C for C/tooling, "
    "B otherwise. A ref that publishes no critical-path file puts no group on "
    "it; a file that is there and cannot be read is UNAVAILABLE.",
    "A source that cannot be read prints UNAVAILABLE with its reason; it is "
    "never a zero.",
)


def render_board(b: dict) -> str:
    """The markdown document the state beat publishes beside the plan table."""
    ctx: FlowCtx = b["ctx"]
    labels = [label for label, _, _ in b["periods"]]
    if b["until"] is None:
        ends = ("Window ends UNAVAILABLE (no readable ref time; each measure "
                "below carries its reason)")
    else:
        ends = (f"Window ends {b['until'].isoformat()} (a function of the "
                "refs, not of when this ran)")
    lines = ["# Flow board", "", f"{ends}. Takt 1.0 roster group per hour.",
             "", "Sources: tree `" + ctx.tree + "`, roster "
             + (f"`{ctx.roster_ref}`" if ctx.roster_ref else "`--roster-file`")
             + f", bus `{ctx.remote}/review/*`"
             + (f", group prefix `{ctx.prefix}`" if ctx.prefix else ""),
             "",
             "| measure | " + " | ".join(labels) + " |",
             "|---" * (len(labels) + 1) + "|"]

    def row(name: str, cells: list[str]) -> None:
        lines.append(f"| {name} | " + " | ".join(cells) + " |")

    row("roster groups closed vs takt",
        [_closed_cell(m["closed"], h) for _, h, m in b["periods"]])
    row("fly-ins closed", [_count_cell(m["flyins"])
                           for _, _, m in b["periods"]])
    row("main moves: group-carrying / record / roster-edit / fly-in",
        [_moves_cell(m["moves"]) for _, _, m in b["periods"]])
    row("first-pass fix-review yield",
        [_yield_cell(m["yield"]) for _, _, m in b["periods"]])
    row("blocked-class mix",
        [_classes_cell(m["classes"]) for _, _, m in b["periods"]])
    row("lead time per size (h, n/p50/max)",
        [_lead_cell(m["lead"]) for _, _, m in b["periods"]])

    lines += ["", "### WIP by flow lane (snapshot at the window's end)", ""]
    value, why = b["wip"]
    if value is None:
        lines.append(f"UNAVAILABLE ({why})")
    else:
        lines += ["| A critical path | B product | C process | F fly-in |",
                  "|---|---|---|---|",
                  f"| {value['A']} | {value['B']} | {value['C']} | {value['F']} |"]

    lines += ["", "## Rules", ""]
    lines += [f"- {rule}" for rule in FLOW_RULES]
    return "\n".join(lines) + "\n"


def flow_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="merge_throughput.py flow",
        description="the flow board: throughput against takt 1.0")
    ap.add_argument("--repo", default=".",
                    help="the git checkout to read (default .)")
    ap.add_argument("--tree", default="origin/main")
    ap.add_argument("--remote", default="origin")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--roster-ref", default=None,
                     help="default: roster_lib.default_roster_ref's answer")
    src.add_argument("--roster-file")
    ap.add_argument("--roster-path")
    ap.add_argument("--prefix", default="",
                    help="count only group ids with this prefix")
    ap.add_argument("--record-prefix", default="record/")
    ap.add_argument("--until", metavar="ISO",
                    help="window end (default: the later of the tree tip and "
                         "the roster ref tip)")
    ap.add_argument("--fetch", action="store_true",
                    help="fetch the review/verdict/probe refs and tags first")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()

    repo = Path(a.repo)
    if a.fetch:
        for heads in ("review", "verdict", "probe"):
            r = _git_ro(repo, "fetch", "-q", "--tags", a.remote,
                        f"+refs/heads/{heads}/*:refs/remotes/{a.remote}/{heads}/*")
            if r.returncode:
                print(f"flow: fetch of {heads}/ failed, reading what is local: "
                      f"{(r.stderr or r.stdout).strip()[:160]}", file=sys.stderr)

    if a.roster_file:
        roster_ref = None
        try:
            roster = roster_lib.load_roster_file(a.roster_file)
        except (OSError, ValueError) as e:
            roster, why = None, f"cannot read {a.roster_file}: {type(e).__name__}"
        else:
            why = roster_lib.roster_shape(roster)
            if why:                     # parses, but not a roster (#2883)
                roster, why = None, f"cannot read {a.roster_file}: {why}"
        roster_path = None
    else:
        roster_ref = roster_lib.reader_ref(str(repo), a.roster_ref)
        try:
            roster = roster_lib.show_roster(str(repo), roster_ref, a.roster_path)
        except roster_lib.RosterNotFound as e:
            roster, why = None, f"roster unreadable: {e}"
        except ValueError as e:         # json.loads: malformed JSON, not a crash
            roster, why = None, (f"roster unreadable: {roster_ref} is not "
                                 f"JSON: {e}")
        else:
            why = roster_lib.roster_shape(roster)
            if why:                     # parses, but not a roster (#2883)
                roster, why = None, (f"roster unreadable: {roster_ref} is not "
                                     f"a roster: {why}")
        roster_path = a.roster_path
        if roster is not None and not roster_path:
            try:
                roster_path = roster_lib.roster_path(str(repo), roster_ref)
            except roster_lib.RosterNotFound:
                roster_path = None

    critical, critical_why = critical_read(repo, roster_ref, roster)
    ctx = FlowCtx(repo=repo, tree=a.tree, remote=a.remote, roster=roster,
                  roster_unavailable=why, roster_ref=roster_ref,
                  roster_path=roster_path, prefix=a.prefix,
                  record_prefix=a.record_prefix, critical=critical,
                  critical_unavailable=critical_why)
    until = parse_iso(a.until) if a.until else flow_default_until(
        repo, a.tree, roster_ref)
    if until is not None and until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)

    text = render_board(board(ctx, until))
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(text.encode('utf-8'))} bytes)")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["flow"]:
        return flow_main(argv[1:])

    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--from-runs", metavar="FILE", action="append", default=[])
    ap.add_argument("--since", metavar="ISO")
    ap.add_argument("--wait", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.from_runs:
        ap.error("--from-runs FILE is required (fetch with gh run list; this "
                 "script does not call the network)")

    rows = load_rows(args.from_runs)
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
                f"REFUSED: main's latest forced-full CI run is {latest.status} "
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
