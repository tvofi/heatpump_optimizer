"""Runs that ran to completion after a newer head on the same branch had started.

    python3 dev/audit/harnesses/superseded_runs.py --cache DIR [--since ISO] [--until ISO] [--jobs]
    python3 dev/audit/harnesses/superseded_runs.py --cache DIR --fetch --since 2026-10-14T20:00:00Z
    python3 dev/audit/harnesses/superseded_runs.py --selftest

DIR holds one `<workflow>.jsonl` per workflow file (tests, validate, hassfest,
governance, codeql, pr-contract): one JSON object per run with the fields
`gh api repos/R/actions/workflows/<file>.yml/runs` returns (id, head_branch,
head_sha, event, status, conclusion, created_at, run_started_at, updated_at,
run_attempt, actor, triggering_actor).  --fetch writes them (read-only `gh api`
calls, paced, every exit status checked).  --jobs adds the jobs API (--fetch-jobs reads it) for the
superseded runs and prints billed job-minutes, labelled apart from wall-minutes.

The rule (R10-CI-CONCURRENCY): a run on a branch other than main is SUPERSEDED
when it is completed, its conclusion is not `cancelled`, and some run of the
same workflow on the same head_branch with a different head_sha started after
this run started and no later than this run's last update.  A run that was
superseded and still finished is time a cancel-in-progress group would have
given back.  Its START is `run_started_at` (the attempt's own start: a rerun
keeps the first attempt's `created_at`, so a held run approved days later would
otherwise read as days long); --start created_at prints the older reading.

Two wall figures, never merged: WALL is updated_at - start of the superseded
runs (what the runs cost); TAIL is updated_at - the newer run's start (the part
of the run that began after the verdict on its head was already moot, which is
the saving an immediate cancel buys).  BILLED (--jobs) is the sum of
ceil(job seconds / 60) over the run's jobs; TAILBILLED counts only job time
after the newer run's start.

Classes: `old(event/sender[/rerun]) -> new(event/sender)`.  The sender is the
run's `actor`, which is the pull_request event's sender on an attempt-1 run;
`+rerun` marks attempt > 1 with a different triggering_actor (a held run that
`approve_held_runs.sh` or a rerun re-started).

Null controls, run on every invocation: every superseded run forced to
`cancelled` must print 0 (NULLCONTROL), and a same-SHA twin set must print 0
(SAMESHA).  --selftest runs both on synthetic runs and a pull_request-main
case with no cache.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = "tvofi/heatpump_optimizer"
WORKFLOWS = ["tests", "validate", "hassfest", "governance", "codeql"]
EXTRA = ["pr-contract"]  # cancel-in-progress is false there on purpose
MAIN = "main"


def ts(s: str | None) -> float:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc).timestamp()


def sender(r: dict) -> str:
    who = r.get("actor") or "?"
    trig = r.get("triggering_actor") or who
    rerun = r.get("run_attempt", 1) > 1 and trig != who
    return f"{who}{'+rerun' if rerun else ''}"


def start_of(r: dict, field: str) -> float:
    return ts(r.get(field) or r["created_at"])


def superseded(runs: list[dict], field: str = "run_started_at"):
    """[(old, newer)] where `newer` is the earliest later-SHA run inside old's span."""
    by_branch: dict[str, list[dict]] = collections.defaultdict(list)
    for r in runs:
        if r["head_branch"] != MAIN:
            by_branch[r["head_branch"]].append(r)
    out = []
    for rs in by_branch.values():
        for r in rs:
            if r["status"] != "completed" or r["conclusion"] == "cancelled":
                continue
            lo, hi = start_of(r, field), ts(r["updated_at"])
            later = [n for n in rs if n["head_sha"] != r["head_sha"]
                     and lo < start_of(n, field) <= hi]
            if later:
                out.append((r, min(later, key=lambda n: start_of(n, field))))
    return out


def same_sha_pairs(runs: list[dict]) -> int:
    """Runs a newer run at the SAME head overlapped: not superseded, never counted."""
    n = 0
    for r in runs:
        if r["head_branch"] == MAIN or r["status"] != "completed":
            continue
        lo, hi = start_of(r, "run_started_at"), ts(r["updated_at"])
        n += any(o is not r and o["head_sha"] == r["head_sha"]
                 and lo < start_of(o, "run_started_at") <= hi for o in runs
                 if o["head_branch"] == r["head_branch"])
    return n


def duplicates(runs: list[dict], inwin: set) -> tuple[int, float]:
    """Same-SHA runs of one workflow that overlapped and both finished: not a
    supersession (nothing newer exists), reported apart. Returns (heads with
    more than one such run, minutes of all but the longest run at each head)."""
    by_sha: dict[tuple, list[dict]] = collections.defaultdict(list)
    for r in runs:
        if (r["head_branch"] != MAIN and r["status"] == "completed"
                and r["conclusion"] != "cancelled" and r["id"] in inwin):
            by_sha[(r["head_branch"], r["head_sha"])].append(r)
    heads, mins = 0, 0.0
    for rs in by_sha.values():
        # Overlap: the later-starting run began before the earlier one ended.
        rs = sorted(rs, key=lambda r: start_of(r, "run_started_at"))
        if len(rs) < 2 or start_of(rs[1], "run_started_at") >= ts(rs[0]["updated_at"]):
            continue
        spans = sorted(ts(r["updated_at"]) - start_of(r, "run_started_at") for r in rs)
        heads += 1
        mins += sum(spans[:-1]) / 60
    return heads, mins


def gh_json(args: list[str]) -> str:
    p = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if p.returncode != 0:
        # A refusal (secondary rate limit prints nothing useful) is a failure,
        # never an empty page.
        raise SystemExit(f"superseded_runs: gh api {' '.join(args)[:80]} rc={p.returncode}: "
                         f"{p.stderr.strip()[:200]}")
    return p.stdout


def fetch(cache: str, since: str, names: list[str]) -> None:
    os.makedirs(cache, exist_ok=True)
    keep = ("id,name,head_branch,head_sha,event,status,conclusion,created_at,"
            "run_started_at,updated_at,run_attempt,path").split(",")
    jq = ".workflow_runs[]|{" + ",".join(keep) + \
        ",actor:.actor.login,triggering_actor:.triggering_actor.login}"
    for w in names:
        out = gh_json(["-X", "GET", f"repos/{REPO}/actions/workflows/{w}.yml/runs",
                       "-f", f"created=>={since}", "-f", "per_page=100",
                       "--paginate", "--jq", jq])
        with open(os.path.join(cache, f"{w}.jsonl"), "w") as f:
            f.write(out)
        time.sleep(3)


def load(cache: str, name: str) -> list[dict]:
    path = os.path.join(cache, f"{name}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        rows = [json.loads(line) for line in f if line.strip()]
    # --paginate on a list that grows while it is read repeats a run across two
    # pages (seen: tests 1, validate 1, pr-contract 3 of ~500): keep one per id.
    uniq = list({r["id"]: r for r in rows}.values())
    if len(uniq) != len(rows):
        print(f"RESULT {name} deduped_rows={len(rows) - len(uniq)}")
    return uniq


def jobs_of(cache: str, r: dict, allow_fetch: bool) -> list[dict] | None:
    path = os.path.join(cache, "jobs", f"{r['id']}-{r['run_attempt']}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    if not allow_fetch:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = gh_json([f"repos/{REPO}/actions/runs/{r['id']}/attempts/{r['run_attempt']}/jobs",
                   "-X", "GET", "-f", "per_page=100", "--paginate",
                   "--jq", ".jobs[]|{name,status,conclusion,started_at,completed_at,labels}"])
    js = [json.loads(line) for line in out.splitlines() if line.strip()]
    with open(path, "w") as f:
        json.dump(js, f)
    time.sleep(1)
    return js


def billed(js: list[dict], after: float | None = None) -> int:
    """Linux job-minutes: each job's seconds (from `after` if given) rounded up."""
    m = 0
    for j in js:
        if not j.get("started_at") or not j.get("completed_at"):
            continue  # skipped jobs have no runner time
        a, b = ts(j["started_at"]), ts(j["completed_at"])
        if after is not None:
            a = max(a, after)
        if b > a:
            m += math.ceil((b - a) / 60)
    return m


def report(name: str, runs: list[dict], args, cache: str | None) -> dict:
    window = [r for r in runs
              if (not args.since or r["created_at"] >= args.since)
              and (not args.until or r["created_at"] <= args.until)]
    nonmain = [r for r in window if r["head_branch"] != MAIN]
    done = [r for r in nonmain if r["status"] == "completed"
            and r["conclusion"] != "cancelled"]
    # The window selects the OLD run; the newer run may fall after it.
    inwin = {r["id"] for r in window}
    pairs = [p for p in superseded(runs, args.start) if p[0]["id"] in inwin]
    wall = sum(ts(o["updated_at"]) - start_of(o, args.start) for o, _ in pairs) / 60
    tail = sum(ts(o["updated_at"]) - start_of(n, args.start) for o, n in pairs) / 60
    line = (f"RESULT {name} nonmain_runs={len(nonmain)} completed_not_cancelled={len(done)} "
            f"superseded={len(pairs)} wall_min={wall:.0f} tail_min={tail:.0f} "
            f"tail_ge_5min={sum(1 for o, n in pairs if ts(o['updated_at']) - start_of(n, args.start) >= 300)}")
    dh, dm = duplicates(runs, inwin)
    line += f" same_sha_dup_heads={dh} same_sha_dup_min={dm:.0f}"
    bm = tb = unread = 0
    if args.jobs and cache:
        for o, n in pairs:
            js = jobs_of(cache, o, args.fetch_jobs)
            if js is None:
                unread += 1
                continue
            bm += billed(js)
            tb += billed(js, start_of(n, args.start))
        line += f" billed_min={bm} tail_billed_min={tb} jobs_unread={unread}"
    print(line)
    # Null controls: the same set with every superseded run cancelled.
    forced = copy.deepcopy(runs)
    ids = {o["id"] for o, _ in pairs}
    for r in forced:
        if r["id"] in ids:
            r["conclusion"] = "cancelled"
    nc = len([p for p in superseded(forced, args.start) if p[0]["id"] in inwin])
    # SAMESHA: the identical runs re-labelled onto one SHA per branch is not superseded.
    one = copy.deepcopy(runs)
    first: dict[str, str] = {}
    for r in one:
        r["head_sha"] = first.setdefault(r["head_branch"], r["head_sha"])
    ss = len([p for p in superseded(one, args.start) if p[0]["id"] in inwin])
    uniq = copy.deepcopy(runs)
    for r in uniq:
        r["head_sha"] = f"{r['head_sha']}-{r['id']}"
    dn = duplicates(uniq, inwin)[0]
    print(f"RESULT {name} NULLCONTROL all_cancelled_superseded={nc} same_sha_superseded={ss}"
          f" unique_sha_dup_heads={dn} (all must be 0)")
    if nc or ss or dn:
        raise SystemExit(f"superseded_runs: null control failed for {name}")
    return {"pairs": pairs, "name": name}


def classes(all_pairs: list[tuple[str, dict, dict]]) -> None:
    c: dict[str, list] = collections.defaultdict(lambda: [0, 0.0, 0.0, [], 0, 0])
    for name, o, n in all_pairs:
        k = f"{name}: {o['event']}/{sender(o)} -> {n['event']}/{sender(n)}"
        row = c[k]
        row[0] += 1
        row[1] += (ts(o["updated_at"]) - start_of(o, ARGS.start)) / 60
        row[2] += (ts(o["updated_at"]) - start_of(n, ARGS.start)) / 60
        row[3].append(f"{name}:{o['id']}")
        row[4] += ts(o["updated_at"]) - start_of(n, ARGS.start) >= 300
        if ARGS.jobs:
            js = jobs_of(ARGS.cache, o, False)
            if js is not None:
                row[5] += billed(js, start_of(n, ARGS.start))
    for k, (cnt, w, t, ids, ge5, tb) in sorted(c.items(), key=lambda kv: -kv[1][1]):
        print(f"RESULT CLASS {k} superseded={cnt} wall_min={w:.0f} tail_min={t:.0f} tail_ge_5min={ge5} "
              f"tail_billed_min={tb if ARGS.jobs else 'n/a'} "
              f"example={ids[0]}")


def selftest() -> int:
    def run(i, sha, event="pull_request", start=0, end=600, branch="b",
            concl="success", actor="u", att=1):
        base = 1_700_000_000
        f = lambda t: datetime.fromtimestamp(base + t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"id": i, "head_branch": branch, "head_sha": sha, "event": event,
                "status": "completed", "conclusion": concl, "created_at": f(start),
                "run_started_at": f(start), "updated_at": f(end), "run_attempt": att,
                "actor": actor, "triggering_actor": actor}
    ok = True

    def check(label, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"SELFTEST {label} got={got} want={want} {'ok' if good else 'FAIL'}")
    # old run outlives a newer-SHA start: 1.
    check("superseded", len(superseded([run(1, "a", end=900), run(2, "b", start=300, end=900)])), 1)
    # the same set, old one cancelled: 0 (the null control).
    check("cancelled", len(superseded([run(1, "a", end=900, concl="cancelled"),
                                       run(2, "b", start=300, end=900)])), 0)
    # same SHA twin: 0.
    check("same-sha", len(superseded([run(1, "a", end=900), run(2, "a", start=300, end=900)])), 0)
    # newer run starts after the old one finished: 0.
    check("sequential", len(superseded([run(1, "a", end=200), run(2, "b", start=300)])), 0)
    # main runs are never counted, either side.
    check("main-old", len(superseded([run(1, "a", branch="main", end=900),
                                      run(2, "b", branch="main", start=300)])), 0)
    # a different branch is not a supersession.
    check("other-branch", len(superseded([run(1, "a", end=900),
                                          run(2, "b", start=300, branch="c")])), 0)
    # bot-sent: counted like any other (the rule is the outcome, not the sender).
    check("bot", len(superseded([run(1, "a", end=900, actor="github-actions[bot]"),
                                 run(2, "b", start=300)])), 1)
    return 0 if ok else 1


ARGS: argparse.Namespace


def main() -> int:
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--jobs", action="store_true",
                    help="add billed job-minutes from cached jobs pages")
    ap.add_argument("--fetch-jobs", action="store_true",
                    help="with --jobs: read the jobs API for pages not yet cached")
    ap.add_argument("--start", default="run_started_at",
                    choices=["run_started_at", "created_at"])
    ap.add_argument("--workflows", default=",".join(WORKFLOWS + EXTRA))
    ap.add_argument("--selftest", action="store_true")
    ARGS = ap.parse_args()
    if ARGS.selftest:
        return selftest()
    if not ARGS.cache:
        ap.error("--cache is required")
    names = ARGS.workflows.split(",")
    if ARGS.fetch:
        fetch(ARGS.cache, ARGS.since or "2026-10-14T20:00:00Z", names)
    allp: list[tuple[str, dict, dict]] = []
    total_runs = 0
    for w in names:
        runs = load(ARGS.cache, w)
        if not runs:
            print(f"RESULT {w} EMPTY (no cached runs; a missing page is not a zero)")
            return 2
        total_runs += len(runs)
        rep = report(w, runs, ARGS, ARGS.cache)
        allp += [(w, o, n) for o, n in rep["pairs"]]
    print(f"RESULT cached_runs={total_runs} workflows={len(names)}")
    classes(allp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
