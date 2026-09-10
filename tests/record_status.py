#!/usr/bin/env python3
"""Report `main`'s current `record` conclusion, as its own red check on every PR.

WHY THIS EXISTS
---------------
`record` (in `.github/workflows/governance.yml`) is the job that refuses a
merged pull request with no disposition row in the plan of record or the living
handover. It carries `if: github.event_name != 'pull_request'`, and that gate is
CORRECT: all three of its modes read `<ref>..origin/main`, and on a
`pull_request` checkout the branch's own commits are not in main's history, so
the window would describe a history the branch is not part of.

The defect is one level out. `record` is one of `main-protect`'s 18 required
status contexts while reporting `skipped` on the only event a seat reads it at.
At #734's head `b63470b`, 17 of the 18 required contexts were `success` and
`record` alone was `skipped` -- a required context that cannot run, which reads
as a guarantee and is not one. So the disposition rule is enforced only AFTER a
merge, and the red lands on whoever pushes next rather than on the branch that
skipped the row. `record` has been red on `main` on seven commits in the five
days 2026-09-06..2026-09-10; #734 merged with no row at `15:53:41Z` and `main`
went red at `15:54:32Z`, nine hours after #708 landed the protocol saying the
row precedes the merge.

The root-cause seat on #541 costed two other countermeasures and refused both
with numbers: a pre-merge own-row check in `pr-contract` measured 5 false
refusals per true one, because 5 of 6 rowless heads were dispositioned by a
COMPANION record pull request and that batch pattern is the protocol working;
and a standing check for "the invocation has no acceptance" faces a population
of one. Its home for the record is #678, which already carries (c) for the
identical cause on a different surface. This file is that seat's CM-2.

WHAT IT DOES AND DOES NOT DO, STATED RATHER THAN IMPLIED
--------------------------------------------------------
It does NOT prevent a merge with no disposition row. It converts "`main` is red
and nobody looks for two hours" into "every open pull request says so". It
addresses the HARM -- the cost landing on whoever merges next, who currently has
no signal -- and it does not address the cause.

It is #713's construction (`tests/nightly_status.py`, the `nightly-status` job)
pointed at `record` instead of the nightly, because #533 and this are the same
shape: a conclusion that lands on a commit nobody re-reads. What differs is the
unit of staleness -- see WHICH COMMIT below.

WHY A RED CHECK AND NOT A WARNING INSIDE A GREEN JOB
----------------------------------------------------
`.cursor/rules/ci-autofix.mdc` says read the summary line and not the tick, and
`.cursor/rules/brief-citations.mdc` names `FIXTURE ok: N error(s)` as a shape
"designed to print beside a clean exit, which is exactly the shape that lets a
real error be waved through". A warning printed inside a passing job is that
shape, and the failure being addressed is precisely that nobody looked.

IT MUST NOT BECOME A REQUIRED CONTEXT
-------------------------------------
That is a ruleset change and a separate owner decision, and this file does not
assume it. Requiring it would make one lane's unfixed red refuse every unrelated
merge in the repository -- which is the same transfer that keeps `nightly-ha`
unrequired -- and it would do so for a condition the PR author did not cause and
often cannot fix. The report says so on every run, green as well as red, so a
reader meeting the first red one learns it from the report rather than from a
policy file they have not opened.

WHICH COMMIT "MAIN'S CURRENT RECORD CONCLUSION" MEANS
-----------------------------------------------------
The newest commit on `main`, within a bounded window, that has a CONCLUDED
`record` check run -- never the tip outright. The two differ for the ~1 minute
`record` takes after each merge. At the merge rate this repository ran while the
defect was live (88 pull requests over 2.39 days), a verdict that flips to "no
answer" for that minute after every merge would teach people to re-run the check
rather than read it, which is the same blindness this exists to remove. A tip
whose run is still in flight is reported as an extra line, never as the verdict.

The window is measured in COMMITS, not in nights, and that is the one place this
departs from `nightly_status.py`. There the cron is nightly, so an old verdict
is evidence the schedule stopped firing. Here `record` runs on every push to
`main`, so a verdict from a week ago on a quiet week still describes `main`'s tip
exactly and is not stale. What IS stale is a verdict from before commits that
have their own unread verdicts, and commits are the unit that measures that.

THE FOUR STATES, AND WHY EACH DOES WHAT IT DOES
-----------------------------------------------
FAILED   the newest concluded `record` on `main` concluded outside
         `PASSING_CONCLUSIONS` and outside `VACUOUS_CONCLUSIONS`. RED. Names the
         conclusion, the commit, the instant and the run URL: "record is red"
         trains blindness, "record concluded 'failure' on a94bbaf at
         2026-09-10T15:54:32Z" does not.
PASSED   it concluded `success`. GREEN.
RUNNING  no `record` run has concluded anywhere in the window and one is in
         flight. RED, and worded as "no concluded result", because a lane whose
         only answer is "ask again later" is a dark lane.
ABSENT   no `record` check run in the window at all; OR the newest concluded one
         concluded `skipped` or `neutral`. RED, both of them. The second case is
         the one that matters and is why this file exists at all: `record`
         reports `skipped` at a pull-request head, so a version of this check
         that accepted a skip as a pass would go green by finding exactly the
         vacuum it was built to report. "No run found" must never read as
         "passed", and neither must "the run concluded and judged nothing".

ITS OWN FAILURE MODE
--------------------
If the API call fails, is rate-limited, or returns something this cannot parse,
the check exits UNREADABLE (2) and says so. It does not pass. A check that goes
green when it could not look is worse than no check, because it converts an open
defect into a closed one (`.cursor/rules/defect-root-cause.mdc`, "A detector
must be shown to detect"). The cost of failing closed is a red check on a GitHub
API outage, on a check that blocks nothing; the cost of failing open is the
seven red-main events above, silently.

PERMISSIONS
-----------
Check runs are Actions/Checks metadata, which `contents: read` cannot see. The
job that runs this declares `checks: read` at JOB level, so the workflow's floor
is unchanged for every other job in `governance.yml`. That is a widening and is
written down as one: read-only, one job, no write scope anywhere.

Stdlib only, on purpose: this job installs nothing, so a dependency set cannot
break the check whose job is to notice that something went dark, and it costs
seconds beside a gate that takes about forty minutes.

USAGE
-----
    python tests/record_status.py                  # discover main's verdict
    python tests/record_status.py --sha a94bbaf    # classify one named commit

`--sha` is an operator affordance and the demonstration arm; the workflow passes
it never, and `tests/entities.py` pins that it does not -- pointed at a commit
that passed, it would report PASSED forever, which is the always-green shape
this repository keeps catching. Under `--sha` no discovery query runs and no
walk back happens: the answer is about that one commit and nothing here has
looked for a newer one.
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
DEFAULT_BRANCH = "main"

# The job this reports on. Coupled to one job name ON PURPOSE, and it fails
# closed: a rename makes the job MISSING, which is ABSENT, which is red -- not
# invisible. `tests/entities.py` derives the coupling rather than restating it,
# by asking governance.yml which of its jobs a pull request cannot see for
# itself, so a rename is refused on the pull request that makes it.
WATCHED_JOB = "record"
WATCHED_WORKFLOW = ".github/workflows/governance.yml"

# How far back down `main` a concluded verdict may be and still be called
# "current". The tip's own run takes about a minute, and merges have landed in
# bursts of two here, so a window of one would report RUNNING routinely. Five is
# the first size that covers a burst plus slack while still being small enough
# that a verdict from outside it is genuinely not about `main` as it stands.
# Commits, not nights: see WHICH COMMIT in the docstring.
DEFAULT_DEPTH = 5

# The whitelist, not a blacklist of known-bad values. A conclusion string GitHub
# has not invented yet arrives as FAILED rather than as a silent pass, which is
# this reader's own null control: the set cannot grow a hole by GitHub adding a
# word.
PASSING_CONCLUSIONS = frozenset({"success"})

# Concluded, and judged nothing. `skipped` is what `record` reports at a
# pull-request head -- the vacuum this whole check exists to report -- and
# `neutral` is the same amount of evidence. Kept SEPARATE from the failing set
# rather than merged into it because the two have different fixes: a failure
# wants a disposition row, a skip wants someone to ask why the job did not run
# on a push to `main`.
VACUOUS_CONCLUSIONS = frozenset({"skipped", "neutral"})

FAILED = "FAILED"
PASSED = "PASSED"
RUNNING = "RUNNING"
ABSENT = "ABSENT"
UNREADABLE = "UNREADABLE"

EXIT_GREEN = 0
EXIT_RED = 1
EXIT_UNREADABLE = 2

# Printed on every run, green or red. A reader who finds this check red needs to
# know, in the report itself, that it is not the thing standing between them and
# a merge -- and that the repair is a row, not a re-run.
NOT_REQUIRED = (
    "This check is NOT one of the required contexts on `main-protect`; a red "
    "here does not block this merge. It reports the state of `main`, which this "
    "pull request will inherit. The repair for a red `record` is a "
    "Delivery-status row in `docs/plan-2026-09-open-issues.md` (or "
    "`docs/HANDOVER.md`) for the merge that landed without one -- never a "
    "re-run of this check."
)


class Unreadable(Exception):
    """The instrument could not look. Distinct from anything it might see."""


def parse_ts(value: str | None) -> dt.datetime:
    """GitHub's ISO-8601 Zulu timestamps, as aware UTC datetimes.

    A completed check run with no `completed_at` is the instrument unable to
    look, not a verdict: this module's answer is which run is newest, so a run
    with no clock cannot be ordered against another. It leaves as `Unreadable`
    (exit 2) rather than as a KeyError, because exit 1 is this reporter's word
    for "`record` is red" and a traceback must not be able to say that.
    """
    if value is None:
        raise Unreadable(
            f"a completed `{WATCHED_JOB}` check run carried no 'completed_at'; "
            "this reporter's answer is which run is newest, so a run with no "
            "clock cannot be classified")
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise Unreadable(f"unparseable timestamp {value!r}: {exc}") from exc


def watched_runs(check_runs: list[dict]) -> tuple[list[dict], list[dict]]:
    """(concluded, in flight) check runs named `WATCHED_JOB`, for one commit.

    Split by `status` rather than by `conclusion`: a queued or in-progress run
    carries `conclusion: null`, and reading that as a conclusion would classify
    a run that has not finished.
    """
    mine = [c for c in check_runs if c.get("name") == WATCHED_JOB]
    done = [c for c in mine if c.get("status") == "completed"]
    return done, [c for c in mine if c.get("status") != "completed"]


def newest(runs: list[dict]) -> dict:
    """The most recently completed of several runs of the same job.

    A re-run leaves both attempts on the commit under `filter=all`, so there can
    be more than one and the newest is the answer. Sorted here rather than
    trusting the API's order: the verdict depends on which is newest, and an
    order that is documented but not asserted is one an API change reverses in
    silence.
    """
    return max(runs, key=lambda c: parse_ts(c.get("completed_at")))


def _where(sha: str, run: dict, behind: int,
           in_flight: tuple[str, dict] | None) -> list[str]:
    lines = [f"  {run.get('html_url', '')}"]
    if behind:
        lines.append(
            f"  `main` has moved {behind} commit(s) since {sha[:7]}; this is "
            "the newest CONCLUDED verdict, which is what 'current' means here.")
    if in_flight is not None:
        lines.append(
            f"  (a `{WATCHED_JOB}` run at {str(in_flight[0])[:7]} is still "
            f"{in_flight[1].get('status', '?')}; this verdict is the last "
            "concluded one.)")
    return lines


def verdict(
    candidates: list[tuple[str, list[dict]]],
    depth: int = DEFAULT_DEPTH,
) -> tuple[str, int, list[str]]:
    """Classify. Returns (state, exit code, report lines).

    `candidates` is (commit sha, that commit's check runs), newest first --
    already fetched. Pure, so every state below is drivable from
    `tests/entities.py` against real captured API payloads and no network.
    """
    head = candidates[0][0] if candidates else "(unknown)"
    flight: tuple[str, dict] | None = None

    for behind, (sha, runs) in enumerate(candidates):
        done, pending = watched_runs(runs)
        if pending and flight is None:
            flight = (sha, pending[0])
        if not done:
            continue

        run = newest(done)
        conclusion = run.get("conclusion")
        at = run.get("completed_at")
        where = _where(sha, run, behind, flight)

        if conclusion in VACUOUS_CONCLUSIONS:
            # The state this file exists for, one level down from "no run".
            return ABSENT, EXIT_RED, [
                f"RECORD {ABSENT} on {DEFAULT_BRANCH} {sha[:7]}: the "
                f"`{WATCHED_JOB}` run concluded {conclusion!r} at {at}, so it "
                "judged nothing. Absence is not a pass.",
                *where,
                f"  `{WATCHED_JOB}` reports {conclusion!r} at a pull-request "
                "head by design; on a push to `main` it should not, so this is "
                "a job that did not run where the rule applies.",
            ]
        if conclusion in PASSING_CONCLUSIONS:
            return PASSED, EXIT_GREEN, [
                f"RECORD {PASSED} on {DEFAULT_BRANCH} {sha[:7]}: conclusion "
                f"{conclusion!r} at {at}",
                *where,
                "  Every merge in that run's window carried a disposition. "
                "Yours must too, before you merge and not after.",
            ]
        return FAILED, EXIT_RED, [
            f"RECORD {FAILED} on {DEFAULT_BRANCH} {sha[:7]}: conclusion "
            f"{conclusion or 'unknown'!r} at {at}",
            *where,
            f"  `{DEFAULT_BRANCH}` is red on the disposition gate now, and "
            "merging into it inherits that red. The repair is the missing "
            "Delivery-status row for the merge that skipped one; open the run "
            "above to see which pull request it names.",
        ]

    if flight is not None:
        return RUNNING, EXIT_RED, [
            f"RECORD {RUNNING} on {DEFAULT_BRANCH} {head[:7]}: no "
            f"`{WATCHED_JOB}` run has CONCLUDED in the last {depth} commit(s) "
            f"of `{DEFAULT_BRANCH}`; the run at {flight[0][:7]} is still "
            f"{flight[1].get('status', '?')}.",
            f"  {flight[1].get('html_url', '')}",
            "  There is no answer about the disposition gate yet. This is not "
            "a pass.",
        ]
    return ABSENT, EXIT_RED, [
        f"RECORD {ABSENT} on {DEFAULT_BRANCH} {head[:7]}: no completed "
        f"`{WATCHED_JOB}` run. Absence is not a pass.",
        f"  Looked at the last {len(candidates)} commit(s) of "
        f"`{DEFAULT_BRANCH}` and found no `{WATCHED_JOB}` check run at any of "
        f"them. `{WATCHED_JOB}` runs on every push to `{DEFAULT_BRANCH}`, so "
        f"either it was renamed -- see {WATCHED_WORKFLOW} -- or the workflow "
        "stopped firing. Neither is a pass.",
    ]


def _get(url: str, token: str | None) -> dict | list:
    """One GET. Every failure raises Unreadable; none returns a green answer."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "heatpump-optimizer-record-status",
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


def check_runs(repo: str, sha: str, token: str | None) -> list[dict]:
    """Every check run on one commit, or Unreadable. Never a partial list.

    `filter=all` keeps earlier attempts of a re-run, which `newest` then orders;
    `filter=latest` would hide an attempt and this reader would not know it had.

    The received `total_count` is compared against what arrived rather than the
    `Link` header being followed. A dropped page is a dropped check run, and a
    dropped `record` check run is an ABSENT that reads as a merge nobody
    dispositioned -- or, worse, a dropped failing one that reads as a PASS. The
    property that makes the refusal unreachable today is that no commit of this
    repository comes near a hundred check runs, not a specific count, which
    moves whenever a job is added. The rule, so a later reader re-derives rather
    than trusts: read `.total_count` from
    `/repos/<repo>/commits/<sha>/check-runs?filter=all` over the N most recent
    commits of `main`; the maximum is what matters. The day it approaches 100,
    this raises `Unreadable` instead of lying, and that is the day to paginate.
    """
    payload = _get(
        f"{API}/repos/{repo}/commits/{sha}/check-runs?filter=all&per_page=100",
        token)
    if not isinstance(payload, dict):
        raise Unreadable(f"check-runs for {sha} was not an object")
    runs = payload.get("check_runs")
    if not isinstance(runs, list):
        raise Unreadable(f"check-runs for {sha} carried no 'check_runs' array")
    total = payload.get("total_count")
    if isinstance(total, int) and total != len(runs):
        raise Unreadable(
            f"commit {sha} reports {total} check run(s) and this page carried "
            f"{len(runs)}: the listing is not the whole commit, and a check "
            "run this never saw cannot be judged")
    return runs


def collect(repo: str, branch: str, token: str | None, sha: str | None,
            depth: int) -> list[tuple[str, list[dict]]]:
    """Fetch what `verdict` classifies, newest commit first.

    The walk STOPS at the first commit carrying a concluded `WATCHED_JOB` run,
    so the ordinary case costs two GETs (the listing, then the tip) rather than
    `depth` + 1. The remaining commits are fetched only when the tip has no
    answer yet, which is the ~1 minute after each merge that the walk exists
    for. This is why `verdict` is handed a list that is usually one long: it
    classifies what was fetched, and what is fetched is what it needed.

    `--sha` classifies that one commit and performs no discovery query, so
    nothing here has looked for a newer one and the report cannot imply it has.
    """
    if sha is not None:
        return [(sha, check_runs(repo, sha, token))]
    listing = _get(
        f"{API}/repos/{repo}/commits?sha={branch}&per_page={depth}", token)
    if not isinstance(listing, list) or not listing:
        raise Unreadable(
            f"the commit listing for `{branch}` was empty or not an array; "
            "without it there is no commit to ask about")
    out = []
    for commit in listing:
        commit_sha = commit.get("sha")
        if not isinstance(commit_sha, str):
            raise Unreadable("a commit in the listing carried no 'sha'")
        runs = check_runs(repo, commit_sha, token)
        out.append((commit_sha, runs))
        if watched_runs(runs)[0]:
            break
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY")
                    or DEFAULT_REPO)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--sha", default=None,
                    help="classify this one commit instead of discovering "
                         "main's newest concluded verdict (operator "
                         "affordance; the workflow passes it never)")
    ap.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
    args = ap.parse_args(argv)

    try:
        candidates = collect(args.repo, args.branch,
                             os.environ.get("GITHUB_TOKEN"), args.sha,
                             args.depth)
        state, code, lines = verdict(candidates, args.depth)
    except Unreadable as exc:
        state, code = UNREADABLE, EXIT_UNREADABLE
        lines = [
            f"RECORD {UNREADABLE}: this check could not read "
            f"`{DEFAULT_BRANCH}`'s `{WATCHED_JOB}` conclusion -- {exc}",
            "  Failing closed on purpose. A check that goes green when it "
            "could not look converts an open defect into a closed one.",
        ]

    report = "\n".join([*lines, "", NOT_REQUIRED])
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"### record-status: {state}\n\n```\n{report}\n```\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
