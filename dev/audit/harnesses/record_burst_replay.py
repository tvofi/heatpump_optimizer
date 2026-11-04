#!/usr/bin/env python3
"""record_burst_replay.py -- replay a burst of pushes to main against the two
O(window) readers of the GITHUB_TOKEN bucket, offline, and count the bucket's
demand as record + enumerate + rest (dev/audit/rca/install-ratelimit.md, M1
and M2; dev/audit/rca/ratelimit-recur.md, M4 and O-1).

    python3 dev/audit/harnesses/record_burst_replay.py v7.0.2 \\
        2026-10-22T08:00:00Z 2026-10-22T09:00:00Z \\
        --rest-per-min <R> --limit <L>

record   Governance's `record` job, under four shapes:
  before   one run per push, three window walks each:      3W + 6P per run
  M1       one run per push, one shared walk:                W + 3P per run
  M1+M2    one walk, and the job's fixed concurrency group (`cancel-in-progress:
           false`): one run going, one pending, a newer push replaces the pending
           one, and a run that starts measures main's tip at its start.
  O-1      M1+M2, with the push arm reading `--record` alone:       W per run
           (`--stats`, `--sunset` and the filer on the schedule, a dispatch and
           the stamp; a stamp push inside the burst is not modelled).
enumerate  Nightly record-autofix's "Enumerate the window's merges", on every
           push: Nightly's concurrency group is the run id, so no push is
           dropped. Counted by enumerate_api_calls.count at each push's tip,
           the production `record_row.enumerate_merges` under a logging stub.
rest       every other reader together, which M0's lines cannot split: R calls
           a minute over the replayed interval. R and the bucket's limit L are
           read from the `RATE_LIMIT before:`/`after:` lines of the hour being
           sized (ratelimit-recur.md section 1.2), so neither has a default.

The record job replayed alone underreads the hour by the enumerate's share;
each `DEMAND` line is the sum the bucket has to hold.

A push is a first-parent commit of origin/main, timed by its committer date. W is
the first-parent commit count of `<since>..<tip>` and P the distinct `Merge pull
request #N` subjects in it, the population record_api_calls.sh's stub resolves,
so W + 3P here equals that harness's total at the same tip. A run lasts
`overhead + per_call * calls` seconds: the 0.42 s per call is the RCA's reading
of run 39755501453's step times; the overhead (checkout, node, filer) is not
measured offline, so it is swept rather than chosen.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enumerate_api_calls  # noqa: E402

MERGE_RE = re.compile(r"^Merge pull request #(\d+)")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def window_cost(since, tip):
    rows = [ln.split("\t", 1) for ln in git("log", "--first-parent", "--format=%H\t%s", f"{since}..{tip}").splitlines() if ln]
    prs = {m.group(1) for _, s in rows if (m := MERGE_RE.match(s))}
    return len(rows), len(prs)


def enumerate_cost(since, tip):
    """The enumerate step's calls at `tip`, read at that tip's own HEAD."""
    with tempfile.TemporaryDirectory() as td:
        wt = str(Path(td) / "tip")
        git("worktree", "add", "-q", "--no-checkout", "--detach", wt, tip)
        try:
            return enumerate_api_calls.count(since, wt)[0]
        finally:
            git("worktree", "remove", "--force", wt)


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


def replay_grouped(burst, timeline, since, overhead, per_call, cost):
    """GitHub's concurrency group: at most one running and one pending."""
    runs, free_at, pending = [], None, None
    events = list(burst)
    while events or pending is not None:
        nxt = events[0][0] if events else None
        if pending is not None and (nxt is None or free_at <= nxt):
            start = max(free_at, pending)
            calls = cost(*window_cost(since, tip_at(start, timeline)))
            runs.append((start, calls))
            free_at, pending = start + overhead + per_call * calls, None
            continue
        t, _ = events.pop(0)
        if free_at is None or t >= free_at:
            calls = cost(*window_cost(since, tip_at(t, timeline)))
            runs.append((t, calls))
            free_at = t + overhead + per_call * calls
        else:
            pending = t
    return runs


def demand(shape, runs, record, enum, rest, limit, note=""):
    total = record + enum + rest
    return (f"DEMAND {shape:<6} {runs} run(s): record {record} + enumerate {enum} + rest {rest} "
            f"= {total} of {limit} ({100 * total // limit} %){note}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("since")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--rest-per-min", type=float, required=True,
                    help="every other reader's calls a minute, from the hour's M0 lines")
    ap.add_argument("--limit", type=int, required=True,
                    help="the bucket's size, the `limit` of the hour's M0 lines")
    a = ap.parse_args()
    since = a.since
    start = datetime.fromisoformat(a.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(a.end.replace("Z", "+00:00"))
    timeline = pushes(since, datetime.min.replace(tzinfo=timezone.utc), datetime.max.replace(tzinfo=timezone.utc))
    burst = pushes(since, start, end)
    if not burst:
        sys.exit(f"record_burst_replay: no push to main in [{a.start}, {a.end}); nothing to replay")
    costs = [window_cost(since, sha) for _, sha in burst]
    enum = sum(enumerate_cost(since, sha) for _, sha in burst)
    rest = round(a.rest_per_min * (end - start).total_seconds() / 60)
    n = len(burst)
    print(f"{n} push(es) to main in [{a.start}, {a.end}) over {since}..<tip>; "
          f"enumerate {enum} call(s), rest {rest} call(s) at {a.rest_per_min:g}/min")
    print(demand("before", n, sum(3 * w + 6 * p for w, p in costs), enum, rest, a.limit))
    print(demand("M1", n, sum(w + 3 * p for w, p in costs), enum, rest, a.limit))
    for shape, cost in (("M1+M2", lambda w, p: w + 3 * p), ("O-1", lambda w, p: w)):
        for overhead in (30, 60, 120, 240):
            runs = replay_grouped(burst, timeline, since, overhead, 0.42, cost)
            print(demand(shape, len(runs), sum(c for _, c in runs), enum, rest, a.limit,
                         f"  [overhead {overhead} s, 0.42 s/call]"))


if __name__ == "__main__":
    main()
