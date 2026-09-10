#!/usr/bin/env python3
"""Report the last scheduled run of the Tests workflow, as its own red check.

WHY THIS EXISTS
---------------
`nightly-ha` and `slow` run only on `schedule` and `workflow_dispatch`. They
are not among the required contexts on the `main-protect` ruleset, and on every
push- and pull-request-triggered commit they are `skipped`. So a scheduled run's
conclusion attaches to whatever commit was `main`'s head when the cron fired --
beside that same commit's own `skipped` entry from the push -- and the next
merge moves the head and strands it. Nothing notifies anyone. Both `nightly-ha`
matrix arms failed on the 2026-09-09 and 2026-09-10 schedules and were found by
a seat sent looking, two nights later (#533).

The countermeasure the root-cause seat costed and REJECTED was a job that files
an issue: it needs `issues: write` against a `permissions: contents: read` floor
this workflow states as deliberate, plus dedupe-and-close logic, and its
standing false-positive cost is an issue filed for a registry outage. This is
the cheaper shape: a distinct check on every pull request that goes RED, reads
the last scheduled run's conclusion, and blocks nothing.

WHY A RED CHECK AND NOT A WARNING INSIDE A GREEN JOB
----------------------------------------------------
`.cursor/rules/ci-autofix.mdc` says read the summary line and not the tick, and
`.cursor/rules/brief-citations.mdc` names `FIXTURE ok: N error(s)` as a shape
"designed to print beside a clean exit, which is exactly the shape that lets a
real error be waved through". A warning printed inside a passing job is that
shape, and the failure being fixed here is precisely that nobody looked. So
this exits non-zero and shows up in the checks list under its own name.

It must not become one of the required contexts. The property that made
`nightly-ha` unrequired is real -- it can go red for a registry outage or a
Home Assistant release, neither of which is a reason to refuse a merge -- and
required-ness would transfer that to every pull request in the repository. The
report says so on every run so that a reader who sees red knows what it costs.

WHICH RUN "THE LAST NIGHTLY" MEANS
----------------------------------
The most recent `schedule`-triggered run of the workflow **that reached a
conclusion**, never the most recent one outright. The two differ for the ~45
minutes the lane takes. A verdict that flips to "no answer" for those minutes
every night teaches people to re-run the check rather than read it, which is
the same blindness this exists to remove. A newer run still in flight is
reported as an extra line, never as the verdict.

THE FOUR STATES, AND WHY EACH DOES WHAT IT DOES
-----------------------------------------------
FAILED   the run's OWN conclusion is outside {success, skipped, neutral}, or at
         least one job of it is. RED. Names every failing job, the age in
         nights, the run id and its URL: "the nightly failed" trains blindness,
         "nightly-ha (stable) failed 2 nights ago, run 34449494849" does not.
         Both halves are needed and the run's half is authoritative: a run can
         conclude `failure`, `cancelled`, `timed_out`, `action_required`,
         `stale` or `startup_failure` while every job the jobs endpoint lists
         reads `success` or `skipped`, and reading only the jobs printed
         `NIGHTLY PASSED ... run conclusion 'failure'` beside exit 0 -- a
         warning next to a clean exit, which is the shape this file argues
         against three paragraphs down.
PASSED   that run exists, is recent enough, its own conclusion is a passing one
         and no job of it failed. GREEN.
RUNNING  no scheduled run has concluded inside the window, and one is in
         flight. RED, and worded as "no concluded result", because a lane whose
         only answer is "ask again later" is a dark lane. It is a distinct
         state from FAILED and prints as one.
ABSENT   no scheduled run at all; or the newest concluded one is older than
         `--max-age-nights`; or it concluded without running one of
         `REQUIRED_LANES`. RED. The cron is daily, so a gap is either the
         schedule not firing -- GitHub disables schedules on repositories with
         no activity -- or a run that never finished. "No scheduled run found"
         must never read as "passed", which is the whole failure mode of a
         check that treats missing evidence as good evidence; and neither must
         "the run concluded and the lane inside it was skipped", which is the
         same error one level down.

Staleness is decided on the newest concluded run whatever its conclusion, and
it wins over FAILED: a failure from nine nights ago is not "the last nightly
failed", it is "the nightly has not run for nine nights", and the two have
different fixes. The report names the old run and its conclusion regardless.

ITS OWN FAILURE MODE
--------------------
If the API call fails, is rate-limited, or returns something this cannot parse,
the check exits UNREADABLE (2) and says so. It does not pass. A check that goes
green when it could not look is worse than no check, because it converts an
open defect into a closed one -- this repository has produced that shape at
least three times (`.cursor/rules/defect-root-cause.mdc`, "A detector must be
shown to detect"). The cost of failing closed is a red check on a GitHub API
outage; the cost of failing open is the two dark nights above, silently.

PERMISSIONS
-----------
Reading workflow runs is Actions metadata, which `contents: read` cannot see.
The job that runs this declares `actions: read` at JOB level, so the workflow's
floor is unchanged for every other job. That is a widening, and a far narrower
one than the rejected `issues: write`: read-only, one job, no write scope
anywhere.

Stdlib only, on purpose: this job installs nothing, so it cannot be broken by
the dependency set -- which is the failure that made #533's lane dark in the
first place -- and it costs seconds.

USAGE
-----
    python tests/nightly_status.py                 # discover the last nightly
    python tests/nightly_status.py --run 34198521690   # classify one named run

`--run` is an operator affordance and the second demonstration arm; the
workflow passes it never, and `tests/entities.py` pins that it does not. Under
`--run` the words "newest" and "last" in the report mean the named run: the
discovery query is not performed, so nothing here has looked for a newer one.
It still refuses a run whose event is not `schedule`, so it cannot be pointed
at a green pull-request run and read as a nightly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
DEFAULT_REPO = "tvofi/heatpump_optimizer"
DEFAULT_WORKFLOW = "tests.yml"

# The oldest age still ACCEPTED, which is what "max age" says. One missed night
# is timezone slack or a rescheduled cron; two consecutive misses is exactly the
# #533 incident. Three is the first age that cannot be either of those, so the
# window ends at two and `nights > MAX_AGE_NIGHTS` puts three outside it.
#
# It was 3 against the same `>` comparison, which needed FOUR nights of silence
# and read a three-night gap as a pass -- the constant, its comment and the
# comparison disagreed, and the comment was the one defending a boundary. The
# constant moved rather than the comparison: `> max_age_nights` is the reading
# the flag name `--max-age-nights` already promises, and changing the operator
# instead would have left the flag meaning "the first age refused".
MAX_AGE_NIGHTS = 2

# Conclusions that are not this repository saying no. `skipped` matters: a
# scheduled run of this workflow skips `fast`, `browser`, `typing`,
# `closure-scope` and both autofix jobs by design, so treating a skip as a
# failure would report red every single night.
OK_CONCLUSIONS = frozenset({"success", "skipped", "neutral"})

# The lanes that exist only on the schedule, and so are the only ones a pull
# request cannot see for itself. A scheduled run in which one of these was
# skipped -- or renamed out of existence -- told nobody anything about it, and
# reporting that as a pass is the same error as reporting "no run found" as
# one. This couples the reporter to two job names ON PURPOSE and it fails
# closed: a rename makes the lane MISSING, which is red, not invisible.
REQUIRED_LANES = ("nightly-ha", "slow")

FAILED = "FAILED"
PASSED = "PASSED"
RUNNING = "RUNNING"
ABSENT = "ABSENT"
UNREADABLE = "UNREADABLE"

EXIT_GREEN = 0
EXIT_RED = 1
EXIT_UNREADABLE = 2

# Printed on every run, green or red. A reader who finds this check red needs
# to know, in the report itself, that it is not the thing standing between them
# and a merge -- otherwise the first red one teaches everybody to ignore it.
NOT_REQUIRED = (
    "This check is NOT one of the required contexts on `main-protect`; a red "
    "here does not block a merge. The nightly lanes can fail for reasons "
    "outside this repository (a registry outage, a Home Assistant release), "
    "which is why they are unrequired and why this must stay unrequired too."
)


class Unreadable(Exception):
    """The instrument could not look. Distinct from anything it might see."""


def parse_ts(value: str | None) -> dt.datetime:
    """GitHub's ISO-8601 Zulu timestamps, as aware UTC datetimes.

    A run with no `created_at` is the instrument unable to look, not a nightly
    with a verdict: every caller reads the key with `.get`, so an absent one
    arrives here as None and leaves as `Unreadable`. It used to arrive as a
    KeyError from `r["created_at"]`, which is not what `main` catches -- so the
    check exited 1 with a traceback, and exit 1 is this reporter's word for
    "the nightly FAILED". Exit 2 is what "could not look" is for.
    """
    if value is None:
        raise Unreadable(
            "a run carried no 'created_at'; this reporter's whole answer is "
            "which run is newest, so a run with no clock cannot be classified")
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise Unreadable(f"unparseable timestamp {value!r}: {exc}") from exc


def nights_ago(when: dt.datetime, now: dt.datetime) -> int:
    """Whole days between two instants, floored at zero.

    "Nights" rather than "days" because the cron is nightly: 0 is last night,
    2 is the age the #533 incident had reached when a human found it.
    """
    return max(0, int((now - when).total_seconds() // 86400))


def phrase_age(nights: int) -> str:
    if nights == 0:
        return "last night"
    if nights == 1:
        return "1 night ago"
    return f"{nights} nights ago"


def pick_runs(runs: list[dict]) -> tuple[dict | None, dict | None]:
    """(newest concluded, newest in flight), newest first by created_at.

    Sorted here rather than trusting the API's order: the answer of this whole
    check depends on which run is newest, and an order that is documented but
    not asserted is one an API change silently reverses.
    """
    ordered = sorted(runs, key=lambda r: parse_ts(r.get("created_at")), reverse=True)
    concluded = next((r for r in ordered if r.get("status") == "completed"), None)
    in_flight = next((r for r in ordered if r.get("status") != "completed"), None)
    return concluded, in_flight


def failing_jobs(jobs: list[dict]) -> list[dict]:
    """Jobs of a concluded run whose conclusion is not an accepted one.

    Fails CLOSED on an unknown or missing conclusion: a value this does not
    recognise is reported rather than waved through, because the alternative is
    a new GitHub conclusion string silently turning the check green.
    """
    return [j for j in jobs if (j.get("conclusion") or "unknown") not in OK_CONCLUSIONS]


def missing_lanes(jobs: list[dict]) -> list[str]:
    """`REQUIRED_LANES` that did not actually run in this run.

    A matrix arm is `nightly-ha (stable)`, so the lane is the name up to the
    first ` (`. A job that FAILED has run; only a skip, or an absence, counts
    as missing.
    """
    ran = {
        j.get("name", "").split(" (")[0]
        for j in jobs
        if (j.get("conclusion") or "") not in ("skipped", "")
    }
    return [lane for lane in REQUIRED_LANES if lane not in ran]


def verdict(
    concluded: dict | None,
    in_flight: dict | None,
    jobs: list[dict],
    now: dt.datetime,
    max_age_nights: int = MAX_AGE_NIGHTS,
) -> tuple[str, int, list[str]]:
    """Classify. Returns (state, exit code, report lines).

    Pure: every input is data, so the four states are drivable from
    `tests/entities.py` without a network.
    """
    if concluded is None:
        if in_flight is not None:
            started = parse_ts(in_flight.get("created_at"))
            return RUNNING, EXIT_RED, [
                f"NIGHTLY {RUNNING}: no scheduled run has CONCLUDED; run "
                f"{in_flight['id']} started {started.isoformat()} and is still "
                f"{in_flight.get('status', '?')}.",
                f"  {in_flight.get('html_url', '')}",
                "  There is no answer about the nightly yet. This is not a pass.",
            ]
        return ABSENT, EXIT_RED, [
            f"NIGHTLY {ABSENT}: no scheduled run of the workflow was found at "
            "all.",
            "  The cron is daily, so this is the schedule not firing -- GitHub "
            "disables schedules on repositories with no recent activity -- and "
            "not a pass.",
        ]

    started = parse_ts(concluded.get("created_at"))
    nights = nights_ago(started, now)
    where = [
        f"  scheduled run {concluded['id']}, {started.isoformat()}, "
        f"head {str(concluded.get('head_sha', ''))[:7]}, "
        f"run conclusion {concluded.get('conclusion')!r}",
        f"  {concluded.get('html_url', '')}",
    ]
    if in_flight is not None:
        where.append(
            f"  (run {in_flight['id']} is still in flight; this verdict is the "
            "last CONCLUDED one, which is what 'the last nightly' means here)"
        )

    if nights > max_age_nights:
        return ABSENT, EXIT_RED, [
            f"NIGHTLY {ABSENT}: the newest CONCLUDED scheduled run is "
            f"{phrase_age(nights)}, older than the {max_age_nights}-night "
            "window. The cron is daily, so nights are being missed.",
            *where,
            "  Reported as absent rather than by its conclusion: a result this "
            "old does not describe the tree, whatever it said.",
        ]

    # THE RUN'S OWN CONCLUSION IS AUTHORITATIVE; the job list refines it.
    #
    # This block did not exist. `verdict` classified from `failing_jobs(jobs)`
    # alone, so a run GitHub concluded `failure` -- while every job the jobs
    # endpoint listed read `success` or `skipped` -- printed
    # `NIGHTLY PASSED ... run conclusion 'failure'` and exited 0. All nine
    # non-`success` run conclusions did. That is a warning beside a clean exit,
    # the shape this module's docstring argues against by name, printed about
    # itself. A run can conclude non-`success` with no failing job in the
    # listing: a `startup_failure` before any job exists, a cancellation, a
    # required-approval stall, a job the listing does not carry.
    #
    # DESIGN CHOICE, said out loud so a later reader reads it as a tightening
    # rather than a defect: the whole vocabulary is refused, not only what has
    # been observed. Backtests over 15 scheduled and 100 recent runs produced
    # `failure` and nothing else -- `cancelled`, `timed_out`, `action_required`
    # and `stale` are absent from the observed population entirely. Untested is
    # not cleared, and a hole no current input reaches is still a hole in a
    # check whose whole job is to not lie.
    run_conclusion = concluded.get("conclusion")
    run_failed = run_conclusion not in OK_CONCLUSIONS
    bad = failing_jobs(jobs)
    if bad or run_failed:
        if bad:
            names = ", ".join(sorted(j.get("name", "?") for j in bad))
            headline = f"NIGHTLY {FAILED}: {names} failed {phrase_age(nights)}."
        else:
            # "The nightly failed" trains blindness, so when the job list is
            # clean the report has to say what the evidence actually is --
            # otherwise a reader opens the run, sees every job green, and
            # concludes the check is broken.
            headline = (
                f"NIGHTLY {FAILED}: the scheduled run itself concluded "
                f"{run_conclusion!r} {phrase_age(nights)}, and no job of it "
                "reported a failure."
            )
        detail = ["  failing jobs:", *[
            f"    {j.get('name', '?')}  {j.get('conclusion') or 'unknown'}  "
            f"{j.get('html_url', '')}"
            for j in sorted(bad, key=lambda j: j.get("name", ""))
        ]] if bad else [
            "  No job in the listing failed, so the run's own conclusion is "
            "the evidence: a run can conclude outside "
            f"{sorted(OK_CONCLUSIONS)} with no failing job listed -- a "
            "startup failure before any job exists, a cancellation, a "
            "required approval, or a job this listing does not carry.",
            f"  {len(jobs)} job(s) were listed and judged.",
        ]
        return FAILED, EXIT_RED, [headline, *where, *detail]

    gone = missing_lanes(jobs)
    if gone:
        return ABSENT, EXIT_RED, [
            f"NIGHTLY {ABSENT}: nothing failed, but {', '.join(gone)} did not "
            f"run in that scheduled run ({phrase_age(nights)}).",
            *where,
            "  A lane that was skipped or renamed away reported nothing, and "
            "nothing is not a pass. Green here would mean this check had "
            "stopped watching the thing it was written for.",
        ]

    return PASSED, EXIT_GREEN, [
        f"NIGHTLY {PASSED}: every job of the scheduled run below succeeded or "
        f"was skipped, {phrase_age(nights)}.",
        *where,
        f"  {len(jobs)} job(s) in that run, "
        f"{sum(1 for j in jobs if j.get('conclusion') == 'success')} succeeded, "
        f"{sum(1 for j in jobs if j.get('conclusion') == 'skipped')} skipped.",
    ]


def _get(url: str, token: str | None) -> dict:
    """One GET. Every failure raises Unreadable; none returns a green answer."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "heatpump-optimizer-nightly-status",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        remaining = exc.headers.get("x-ratelimit-remaining") if exc.headers else None
        rate = " (rate limit exhausted)" if remaining == "0" else ""
        raise Unreadable(f"HTTP {exc.code} from {url}{rate}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise Unreadable(f"could not reach {url}: {exc}") from exc
    try:
        return json.loads(body)
    except (ValueError, TypeError) as exc:
        raise Unreadable(f"unparseable JSON from {url}: {exc}") from exc


def _jobs(repo: str, run_id: int, token: str | None) -> list[dict]:
    """Every job of one run, or Unreadable. Never a partial list.

    One page of 100 and no `Link` following, and the received `total_count` was
    never compared to what arrived -- so a run with more than 100 jobs would
    have had its overflow dropped in silence, and a dropped failing job is a
    PASS. Comparing the two numbers is cheaper than pagination and removes the
    silent case rather than the limit: the largest run of this workflow has 12
    jobs, so the refusal is unreachable today and the day it becomes reachable
    it says so instead of lying. If that day comes, follow `Link` here.
    """
    payload = _get(f"{API}/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100",
                   token)
    jobs = payload.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise Unreadable(f"run {run_id} reported no jobs")
    total = payload.get("total_count")
    if isinstance(total, int) and total != len(jobs):
        raise Unreadable(
            f"run {run_id} reports {total} job(s) and this page carried "
            f"{len(jobs)}: the listing is not the whole run, and a job this "
            "never saw cannot be judged"
        )
    return jobs


def collect(repo: str, workflow: str, token: str | None,
            run_id: int | None) -> tuple[dict | None, dict | None, list[dict]]:
    """Fetch what `verdict` classifies. Two GETs on the discovery path."""
    if run_id is not None:
        run = _get(f"{API}/repos/{repo}/actions/runs/{run_id}", token)
        if run.get("event") != "schedule":
            raise Unreadable(
                f"run {run_id} was triggered by {run.get('event')!r}, not "
                "'schedule'; this reports on the nightly and refuses to call "
                "any other run one"
            )
        concluded, in_flight = pick_runs([run])
    else:
        payload = _get(
            f"{API}/repos/{repo}/actions/workflows/{workflow}/runs"
            "?event=schedule&per_page=10", token)
        runs = payload.get("workflow_runs")
        if not isinstance(runs, list):
            raise Unreadable("the runs listing carried no 'workflow_runs' array")
        concluded, in_flight = pick_runs(runs)
    jobs = _jobs(repo, concluded["id"], token) if concluded else []
    return concluded, in_flight, jobs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY")
                    or DEFAULT_REPO)
    ap.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    ap.add_argument("--run", type=int, default=None,
                    help="classify this scheduled run instead of discovering "
                         "the last one (operator affordance; the workflow "
                         "passes it never)")
    ap.add_argument("--max-age-nights", type=int, default=MAX_AGE_NIGHTS)
    args = ap.parse_args(argv)

    now = dt.datetime.now(dt.timezone.utc)
    try:
        concluded, in_flight, jobs = collect(
            args.repo, args.workflow, os.environ.get("GITHUB_TOKEN"), args.run)
        state, code, lines = verdict(
            concluded, in_flight, jobs, now, args.max_age_nights)
    except Unreadable as exc:
        state, code = UNREADABLE, EXIT_UNREADABLE
        lines = [
            f"NIGHTLY {UNREADABLE}: this check could not read the last "
            f"scheduled run -- {exc}",
            "  Failing closed on purpose. A check that goes green when it "
            "could not look converts an open defect into a closed one.",
        ]

    report = "\n".join([*lines, "", NOT_REQUIRED])
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"### nightly-status: {state}\n\n```\n{report}\n```\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
