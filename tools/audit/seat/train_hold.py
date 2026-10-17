#!/usr/bin/env python3
"""The merge train's hold: the ref the record beat reads while a train is live.

    python3 tools/audit/seat/train_hold.py --check [--repo OWNER/REPO]
        [--max-age-seconds N] [--token-env GH_TOKEN]
    python3 tools/audit/seat/train_hold.py --self-test

WHY (R10-TRAIN-HOLD, issue #2302). The record beat in
`.github/workflows/tests.yml` auto-merges a row-only record pull request on its
own schedule. A record pull request merged while a merge train waits on CI
moves `main` under a head the train has settled: on 2026-10-15 #2291, #2295 and
#2299 each landed mid-train, stopping or re-carrying #2284 and #2290. CI cannot
see the train's local pidfile -- the train runs on the orchestrator's machine --
so the train publishes a ref instead: `refs/heads/train-hold`, a commit whose
committer date is the freshness clock. This module is the one reader of it,
called by the record beat before it merges, and the one definition of the ref
name the train publishes.

THE BOUND. A live train refreshes the hold at every CI poll and before every
recarry, so its longest silent stretch is one `app_push.sh --recarry` (5-15
minutes, `tools/audit/seat/merge_train.py`'s own line). MAX_AGE_SECONDS is
three times that worst case: a live train's hold never reads stale, and a
crashed train's hold stops blocking the record beat within one bound. The
bound belongs to the beat, not the train: a stale hold is a crash, and the
beat's ordinary behaviour is the fallback.

AN AGE AHEAD OF THE READING CLOCK IS UNKNOWABLE, NEVER ZERO. A commit dated
after `now` (clock skew between GitHub's API and the runner) is not evidence
that the hold is old; it is evidence that the age cannot be read, and the
conservative answer is to respect the hold until the clocks agree. Reading it
as stale would merge a record under a train exactly when the timestamps
disagree.

EXIT. `--check` exits 0 with one line on stdout -- `fresh ...`, `stale ...` or
`absent ...` -- which `tests.yml`'s `case` keys on; 2 when the ref could not
be read, which the beat reddens the report on rather than merging blind.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_REPO = "tvofi/heatpump_optimizer"
BRANCH = "train-hold"
# Three times the worst silent stretch of a LIVE train: one
# app_push.sh --recarry (5-15 min, merge_train.py's own comment). The train
# refreshes the hold more often than that (every CI poll, and before every
# recarry), so this is a crash bound, not the train's liveness window.
MAX_AGE_SECONDS = 3 * 15 * 60


def _api(repo: str, path: str, token: str) -> object:
    url = f"https://api.github.com/repos/{repo}{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "hpo-train-hold",
    })
    with urllib.request.urlopen(req) as resp:  # nosec - fixed https host
        return json.load(resp)


def verdict(age_seconds: float, bound: int = MAX_AGE_SECONDS) -> str:
    """`fresh` while the hold is younger than the bound, else `stale`.

    A negative age (a stamp ahead of the reading clock) is FRESH: an
    unknowable age is never evidence that the hold is old (fixer.md step 16)."""
    return "fresh" if age_seconds < bound else "stale"


def _stamp(iso: str) -> datetime.datetime:
    when = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if when.tzinfo is None:  # GitHub always sends Z; a bare stamp reads as UTC
        when = when.replace(tzinfo=datetime.timezone.utc)
    return when


def check(repo: str, token: str, now: datetime.datetime | None = None,
          bound: int = MAX_AGE_SECONDS) -> tuple[str, str]:
    """(state, detail): `absent`, `fresh` or `stale` from the live ref.

    The ref's tip commit's committer date is the freshness clock: one API read
    for the ref and one for the commit. A 404 is `absent`; every other failure
    propagates, so the CLI can map it to exit 2 and the beat can redden rather
    than merge blind."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        ref = _api(repo, f"/git/ref/heads/{BRANCH}", token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "absent", f"no refs/heads/{BRANCH}"
        raise
    sha = str((ref.get("object") or {}).get("sha") or "")
    if len(sha) != 40:
        raise ValueError(f"refs/heads/{BRANCH} has no 40-hex object sha: {sha[:80]!r}")
    commit = _api(repo, f"/git/commits/{sha}", token)
    when = _stamp(str((commit.get("committer") or {}).get("date") or ""))
    age = (now - when).total_seconds()
    if age < 0:
        return verdict(age, bound), (
            f"{sha[:8]} is dated {-age:.0f}s ahead of the reading clock; the age is "
            "unknowable, so the hold stands until the clocks agree")
    return verdict(age, bound), f"{sha[:8]} age {age:.0f}s bound {bound}s"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="train_hold.py")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--max-age-seconds", type=int, default=MAX_AGE_SECONDS)
    ap.add_argument("--token-env", default="GH_TOKEN")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.check:
        ap.error("one of --check or --self-test")
    token = os.environ.get(a.token_env, "")
    if not token:
        print(f"unreadable: ${a.token_env} is not set", file=sys.stderr)
        return 2
    try:
        state, detail = check(a.repo, token, bound=a.max_age_seconds)
    except Exception as e:  # noqa: BLE001 -- the beat must redden, never guess
        print(f"unreadable: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print(f"{state} {detail}")
    return 0


def self_test() -> int:
    passed = failed = 0

    def ok(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    now = datetime.datetime(2026, 10, 17, 12, 0, 0, tzinfo=datetime.timezone.utc)
    sha = "a" * 40
    world: dict = {"date": "2026-10-17T11:59:00Z"}
    seen: list[str] = []
    real = globals()["_api"]

    def api(repo, path, token):
        seen.append(path)
        if path == f"/git/ref/heads/{BRANCH}":
            if world.get("absent"):
                raise urllib.error.HTTPError(path, 404, "Not Found", None, None)
            if world.get("unreadable"):
                raise urllib.error.URLError("connection refused")
            return {"object": {"sha": sha}}
        if path == f"/git/commits/{sha}":
            return {"committer": {"date": world["date"]}}
        raise AssertionError(path)

    globals()["_api"] = api
    try:
        state, _ = check("o/r", "t", now=now)
        ok("a hold one minute old is fresh: the beat skips its merge",
           state == "fresh")
        ok("the reader reads the ref and then its commit, the two API paths "
           "GitHub serves",
           seen == [f"/git/ref/heads/{BRANCH}", f"/git/commits/{sha}"])
        world["date"] = "2026-10-17T11:00:00Z"  # 3600s > the 2700s bound
        ok("a hold older than the bound is stale: a crashed train's block expires "
           "and the beat resumes",
           check("o/r", "t", now=now)[0] == "stale")
        world["date"] = "2026-10-17T13:00:00Z"  # ahead of `now`
        state, detail = check("o/r", "t", now=now)
        ok("a stamp ahead of the reading clock is respected, not read as stale "
           "and not read as zero",
           state == "fresh" and "ahead" in detail and "unknowable" in detail)
        world["absent"] = True
        ok("no ref is absent, never fresh (null control: a missing hold must "
           "not block the beat)",
           check("o/r", "t", now=now)[0] == "absent")
        world["absent"] = False
        world["unreadable"] = True
        raised = False
        try:
            check("o/r", "t", now=now)
        except urllib.error.URLError:
            raised = True
        ok("an unreadable ref raises, so the beat reddens instead of merging blind",
           raised)
    finally:
        globals()["_api"] = real

    ok("the boundary is stale-side inclusive: age == bound is stale, bound - 1 is fresh",
       verdict(MAX_AGE_SECONDS) == "stale" and verdict(MAX_AGE_SECONDS - 1) == "fresh")
    ok("a negative age is fresh, never 0: an unknowable age is not evidence of staleness",
       verdict(-1) == "fresh" and verdict(-10 ** 6) == "fresh")
    ok(f"the bound is 3x a recarry's 15-minute worst case ({MAX_AGE_SECONDS}s), so a "
       "live train's hold never expires between its refreshes",
       MAX_AGE_SECONDS >= 3 * 15 * 60)
    ok(f"the ref name is the one both readers use ({BRANCH})",
       BRANCH == "train-hold")
    print(f"train_hold self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
