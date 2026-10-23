#!/usr/bin/env python3
"""record_burst_replay.py -- replay a burst of pushes to main against Governance's
`record` job, offline, and count its runs and GITHUB_TOKEN calls under three
shapes (dev/audit/rca/install-ratelimit.md, M1 and M2):

  before   one run per push, three window walks each:      3W + 6P per run
  M1       one run per push, one shared walk:                W + 3P per run
  M1+M2    one walk, and the job's fixed concurrency group (`cancel-in-progress:
           false`): one run going, one pending, a newer push replaces the pending
           one, and a run that starts measures main's tip at its start.

    python3 dev/audit/harnesses/record_burst_replay.py v7.0.2 \\
        2026-10-22T08:00:00Z 2026-10-22T09:00:00Z

A push is a first-parent commit of origin/main, timed by its committer date. W is
the first-parent commit count of `<since>..<tip>` and P the distinct `Merge pull
request #N` subjects in it, the population record_api_calls.sh's stub resolves,
so W + 3P here equals that harness's total at the same tip. A run lasts
`overhead + per_call * calls` seconds: the 0.42 s per call is the RCA's reading
of run 39755501453's step times; the overhead (checkout, node, filer) is not
measured offline, so it is swept rather than chosen.
"""
import re
import subprocess
import sys
from datetime import datetime, timezone

MERGE_RE = re.compile(r"^Merge pull request #(\d+)")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def window_cost(since, tip):
    rows = [ln.split("\t", 1) for ln in git("log", "--first-parent", "--format=%H\t%s", f"{since}..{tip}").splitlines() if ln]
    prs = {m.group(1) for _, s in rows if (m := MERGE_RE.match(s))}
    return len(rows), len(prs)


def pushes(since, start, end):
    out = []
    for ln in git("log", "--first-parent", "--format=%H\t%cI", f"{since}..origin/main").splitlines():
        sha, when = ln.split("\t")
        t = datetime.fromisoformat(when).astimezone(timezone.utc)
        if start <= t < end:
            out.append((t.timestamp(), sha))
    return sorted(out)


def tip_at(ts, timeline):
    return [sha for t, sha in timeline if t <= ts][-1]


def replay_grouped(burst, timeline, since, overhead, per_call):
    """GitHub's concurrency group: at most one running and one pending."""
    runs, free_at, pending = [], None, None
    events = list(burst)
    while events or pending is not None:
        nxt = events[0][0] if events else None
        if pending is not None and (nxt is None or free_at <= nxt):
            start = max(free_at, pending)
            w, p = window_cost(since, tip_at(start, timeline))
            calls = w + 3 * p
            runs.append((start, calls))
            free_at, pending = start + overhead + per_call * calls, None
            continue
        t, _ = events.pop(0)
        if free_at is None or t >= free_at:
            w, p = window_cost(since, tip_at(t, timeline))
            calls = w + 3 * p
            runs.append((t, calls))
            free_at = t + overhead + per_call * calls
        else:
            pending = t
    return runs


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    since = sys.argv[1]
    start = datetime.fromisoformat(sys.argv[2].replace("Z", "+00:00"))
    end = datetime.fromisoformat(sys.argv[3].replace("Z", "+00:00"))
    timeline = pushes(since, datetime.min.replace(tzinfo=timezone.utc), datetime.max.replace(tzinfo=timezone.utc))
    burst = pushes(since, start, end)
    if not burst:
        sys.exit(f"record_burst_replay: no push to main in [{sys.argv[2]}, {sys.argv[3]}); nothing to replay")
    costs = [window_cost(since, sha) for _, sha in burst]
    print(f"{len(burst)} push(es) to main in [{sys.argv[2]}, {sys.argv[3]}) over {since}..<tip>")
    print(f"before  {len(burst)} run(s), {sum(3 * w + 6 * p for w, p in costs)} call(s)")
    print(f"M1      {len(burst)} run(s), {sum(w + 3 * p for w, p in costs)} call(s)")
    for overhead in (30, 60, 120, 240):
        runs = replay_grouped(burst, timeline, since, overhead, 0.42)
        print(f"M1+M2   {len(runs)} run(s), {sum(c for _, c in runs)} call(s)  [overhead {overhead} s, 0.42 s/call]")


if __name__ == "__main__":
    main()
