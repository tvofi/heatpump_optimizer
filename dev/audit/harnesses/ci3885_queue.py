#!/usr/bin/env python3
"""#3885 queue group (R11-CI-3885-QUEUE): where the account's concurrent-job slots go.

    python3 dev/audit/harnesses/ci3885_queue.py fetch DAY [--cache DIR]
    python3 dev/audit/harnesses/ci3885_queue.py report DAY [--cache DIR] [--keep-copies]

`fetch` lists every workflow run created on DAY (UTC) and every job of every
attempt of each (`/actions/runs/{id}/jobs?filter=all`), and caches both as
JSON under DIR (default $TMPDIR/ci3885_queue). `report` reads the cache only,
so a re-read costs no API call, and prints one JSON object, a key per arm:

  census      per workflow: runs, runs that held a runner (a job with a
              started_at and conclusion other than skipped), runner-minutes
              (started_at..completed_at over every non-skipped job, every
              attempt), and the day's peak concurrent jobs (the cap as seen).
  queue       per job: started_at - created_at, p50/p90/max, all jobs and
              by hour; and for CI runs, run created -> first job started.
  e2e         CI runs whose latest `gate` concluded: created -> gate completed.
  sweep       Gate sweep runs: how many held a runner, their minutes and queue
              wait; the triggering CI attempt is not on the run object, so a
              sweep is attributed to the CI run that completed at its head
              closest before it (same head_sha).
  supersede   CI pull_request/dispatch runs on a branch: minutes their jobs ran
              after a NEWER head's CI run on the same branch was created (waste
              a cancel at creation saves), and minutes of jobs that never
              started before that moment (queue slots a cancel frees).
  rerun       jobs of attempt >= 2 whose same-named job concluded success in
              the previous attempt (a whole-run re-run), minutes; excluding
              `gate` and `sweep-self`, which sweep/refresh re-run on purpose.
  record      CI runs on record/* (and other non-fix) branches, minutes.
  prelude     prelude job minutes by run kind (title), the wait_sources share.

NULL CONTROLS (each arm's predicate applied where it must read ~0):
  supersede-null  the same arm with "newer head" replaced by "same head_sha"
                  restricted to code runs: twins are never superseded, so the
                  arm must not count a run against its own head.
  rerun-null      attempt-1 jobs read as re-runs: must be 0 by construction of
                  the previous-attempt lookup.
  queue-null      the queue arm on a quiet day (pass that day): waits near 0.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def gh(path):
    for attempt in range(4):                       # a 502 from the API is retried, never counted
        out = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True)
        if out.returncode == 0:
            break
        time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit(f"gh api {path}: {out.stderr.strip()}")
    # --paginate concatenates JSON objects; split them
    dec, i, docs, s = json.JSONDecoder(), 0, [], out.stdout
    while i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1
        if i >= len(s):
            break
        d, i = dec.raw_decode(s, i)
        docs.append(d)
    return docs


def cache_dir(a):
    d = Path(a.cache or os.path.join(os.environ.get("TMPDIR", "/tmp"), "ci3885_queue"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch(a):
    d = cache_dir(a)
    runs = []
    for doc in gh(f"repos/{REPO}/actions/runs?created={a.day}&per_page=100"):
        runs += doc["workflow_runs"]
    keep = [{k: r.get(k) for k in ("id", "name", "event", "head_branch", "head_sha", "status",
                                   "conclusion", "created_at", "run_started_at", "updated_at",
                                   "run_attempt", "display_title")} | {"actor": r["actor"]["login"]}
            for r in runs]
    jobs = {}
    for r in keep:
        js = []
        for doc in gh(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=all&per_page=100"):
            js += [{k: j.get(k) for k in ("id", "name", "run_attempt", "status", "conclusion",
                                          "created_at", "started_at", "completed_at")}
                   for j in doc["jobs"]]
        jobs[str(r["id"])] = js
    (d / f"{a.day}.json").write_text(json.dumps({"runs": keep, "jobs": jobs}))
    print(f"cached {len(keep)} runs, {sum(map(len, jobs.values()))} jobs -> {d / (a.day + '.json')}")


def ran(j):
    return j["conclusion"] not in (None, "skipped") and j["started_at"] and j["completed_at"] \
        and ts(j["completed_at"]) > ts(j["started_at"])


def mins(j):
    return (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds() / 60


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else 0


def kind(r):
    t = (r.get("display_title") or "").split()
    return t[1] if r["name"] .startswith("CI") and len(t) > 1 else r["name"]


def wf(r):
    return "CI" if r["name"].startswith("CI ") else r["name"]


def report(a):
    data = json.loads((cache_dir(a) / f"{a.day}.json").read_text())
    runs, jobs = data["runs"], {int(k): v for k, v in data["jobs"].items()}
    # A re-run of one job lists EVERY job again under the new attempt, the untouched ones as
    # copies carrying the earlier attempt's timestamps: counted, they read 1,303 copied jobs
    # (2026-11-25) as executed re-runs. A job executed once is kept at its first attempt only.
    out = {}
    copies = 0
    for rid, js in jobs.items():
        seen, keep = set(), []
        for j in sorted(js, key=lambda j: j["run_attempt"]):
            key = (j["name"], j["started_at"], j["completed_at"])
            if j["run_attempt"] > 1 and key in seen and not a.keep_copies:
                copies += 1
                continue
            seen.add(key)
            keep.append(j)
        jobs[rid] = keep
    out["copied_jobs_dropped"] = copies

    # census
    c = collections.defaultdict(lambda: [0, 0, 0.0, 0])
    edges = []
    for r in runs:
        js = [j for j in jobs[r["id"]] if ran(j)]
        e = c[wf(r)]
        e[0] += 1
        e[1] += bool(js)
        e[2] += sum(map(mins, js))
        e[3] += len(js)
        for j in js:
            edges += [(ts(j["started_at"]), 1), (ts(j["completed_at"]), -1)]
    peak = cur = 0
    for _, s in sorted(edges, key=lambda x: (x[0], x[1])):
        cur += s
        peak = max(peak, cur)
    out["census"] = {k: {"runs": v[0], "held_runner": v[1], "runner_min": round(v[2]), "jobs": v[3]}
                     for k, v in sorted(c.items(), key=lambda x: -x[1][2])}
    out["peak_concurrent_jobs"] = peak

    # queue
    waits, byhour = [], collections.defaultdict(list)
    for r in runs:
        for j in jobs[r["id"]]:
            if ran(j):
                w = (ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60
                waits.append(w)
                byhour[j["created_at"][11:13]].append(w)
    out["queue"] = {"jobs": len(waits), "p50_min": round(pct(waits, .5), 1), "p90_min": round(pct(waits, .9), 1),
                    "max_min": round(max(waits or [0]), 1),
                    "by_hour_p90": {h: round(pct(v, .9)) for h, v in sorted(byhour.items())}}

    # e2e
    e2e, first = [], []
    for r in runs:
        if wf(r) != "CI":
            continue
        js = jobs[r["id"]]
        st = [ts(j["started_at"]) for j in js if j["run_attempt"] == 1 and ran(j)]
        if st:
            first.append((min(st) - ts(r["created_at"])).total_seconds() / 60)
        g = [j for j in js if j["name"] == "gate" and j["run_attempt"] == 1 and j["completed_at"]
             and j["conclusion"] not in ("skipped", "cancelled")]
        if g:
            e2e.append(((ts(g[0]["completed_at"]) - ts(r["created_at"])).total_seconds() / 60, kind(r)))
    # decompose: where a run's wall clock goes. pending = run created -> first job CREATED
    # (a concurrency group holding the run; no runner involved); queue = the run's longest
    # job created -> started (the account's runner cap); longest = its longest job's run time.
    dec = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in runs:
        if wf(r) != "CI":
            continue
        js = [j for j in jobs[r["id"]] if j["run_attempt"] == 1]
        g = [j for j in js if j["name"] == "gate" and j["completed_at"] and j["conclusion"] not in ("skipped", "cancelled")]
        if not js or not g:
            continue
        k = f"{r['event']}:{kind(r)}"
        dec[k]["pending"].append((min(ts(j["created_at"]) for j in js) - ts(r["created_at"])).total_seconds() / 60)
        q = [(ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60 for j in js if ran(j)]
        dec[k]["queue_max"].append(max(q or [0]))
        dec[k]["longest_job"].append(max([mins(j) for j in js if ran(j) and j["name"] != "prelude"] or [0]))
        dec[k]["prelude"].append(max([mins(j) for j in js if j["name"] == "prelude" and ran(j)] or [0]))
        dec[k]["e2e"].append((ts(g[0]["completed_at"]) - ts(r["created_at"])).total_seconds() / 60)
    out["decompose_p50_p90"] = {k: {m: [round(pct(v, .5)), round(pct(v, .9)), len(v)] for m, v in d.items()}
                                for k, d in sorted(dec.items())}
    for k in sorted({x[1] for x in e2e}):
        v = [x[0] for x in e2e if x[1] == k]
        out.setdefault("e2e_by_kind", {})[k] = {"n": len(v), "p50_min": round(pct(v, .5)), "p90_min": round(pct(v, .9))}
    out["ci_first_job_wait"] = {"n": len(first), "p50_min": round(pct(first, .5)), "p90_min": round(pct(first, .9)),
                                "max_min": round(max(first or [0]))}

    # sweep
    sw = [r for r in runs if r["name"] == "Gate sweep"]
    held = [j for r in sw for j in jobs[r["id"]] if ran(j)]
    ci_runs = [r for r in runs if wf(r) == "CI"]
    attempt2 = 0
    for r in sw:
        cands = [x for x in ci_runs if x["head_sha"] == r["head_sha"] and ts(x["updated_at"]) <= ts(r["created_at"])]
        if cands and max(cands, key=lambda x: x["updated_at"])["run_attempt"] > 1:
            attempt2 += 1
    out["sweep"] = {"runs": len(sw), "held_runner": len(held), "runner_min": round(sum(map(mins, held))),
                    "p50_job_min": round(pct([mins(j) for j in held], .5), 1),
                    "p90_job_min": round(pct([mins(j) for j in held], .9), 1),
                    "after_ci_attempt_ge2": attempt2,
                    "queue_p90_min": round(pct([(ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60
                                                for j in held], .9))}

    # supersede (and its null)
    def supersede(same):
        waste = slot = 0.0
        n = 0
        pr = [r for r in ci_runs if r["event"] in ("pull_request", "workflow_dispatch") and r["head_branch"] != "main"]
        for r in pr:
            newer = [x for x in pr if x["head_branch"] == r["head_branch"] and x["id"] > r["id"]
                     and ((x["head_sha"] == r["head_sha"] and kind(x) == "code" and kind(r) == "code") if same
                          else x["head_sha"] != r["head_sha"])]
            if not newer:
                continue
            t = min(ts(x["created_at"]) for x in newer)
            hit = False
            for j in jobs[r["id"]]:
                if not ran(j):
                    continue
                s, e = ts(j["started_at"]), ts(j["completed_at"])
                if e > t:
                    waste += (e - max(s, t)).total_seconds() / 60
                    hit = True
                    if s > t:
                        slot += 1
            n += hit
        return {"runs": n, "runner_min_after_newer_head": round(waste), "jobs_started_after_newer_head": int(slot)}
    out["supersede"] = supersede(False)
    out["supersede_null_same_head_code"] = supersede(True)

    # rerun (and its null)
    def rerun(null):
        m, n, gate_m = 0.0, 0, 0.0
        for r in runs:
            js = jobs[r["id"]]
            prev = {(j["name"], j["run_attempt"]): j for j in js}
            for j in js:
                if not ran(j) or (j["run_attempt"] != 1 if null else j["run_attempt"] < 2):
                    continue
                p = prev.get((j["name"], j["run_attempt"] - 1))
                if p and p["conclusion"] == "success":
                    if j["name"] in ("gate", "sweep-self"):
                        gate_m += mins(j)
                    else:
                        m += mins(j)
                        n += 1
        return {"jobs": n, "runner_min": round(m), "gate_rejudge_min": round(gate_m)}
    out["rerun_of_success"] = rerun(False)
    out["rerun_null_attempt1"] = rerun(True)
    att = collections.Counter(r["run_attempt"] for r in ci_runs)
    out["ci_attempts"] = dict(sorted(att.items()))

    # record
    rec = collections.defaultdict(lambda: [0, 0.0])
    for r in ci_runs:
        b = (r["head_branch"] or "").split("/")[0]
        rec[b][0] += 1
        rec[b][1] += sum(mins(j) for j in jobs[r["id"]] if ran(j))
    out["ci_by_branch_prefix"] = {k: {"runs": v[0], "runner_min": round(v[1])} for k, v in rec.items()}

    # prelude
    pre = collections.defaultdict(list)
    for r in ci_runs:
        for j in jobs[r["id"]]:
            if j["name"] == "prelude" and ran(j):
                pre[kind(r)].append(mins(j))
    out["prelude"] = {k: {"n": len(v), "runner_min": round(sum(v)), "p50_min": round(pct(v, .5), 1),
                          "p90_min": round(pct(v, .9), 1), "max_min": round(max(v), 1)} for k, v in pre.items()}
    # job-name totals for CI
    jn = collections.Counter()
    for r in ci_runs:
        for j in jobs[r["id"]]:
            if ran(j):
                jn[j["name"].split(" / ")[0]] += mins(j)
    out["ci_minutes_by_unit"] = {k: round(v) for k, v in jn.most_common(15)}

    # waits: runner-minutes a job held beyond its own no-wait floor (the day's p10 of that
    # job's duration): the in-job polls and sleeps. The NULL rows are jobs with no wait in
    # them (a compile/lint step): their excess is run-time spread, the arm's noise floor.
    WAITERS = {"prelude": "prelude wait_sources (edit) / review", "gate": "gate judge lag wait",
               "sweep": "Gate sweep poll/settle", "sweep-self": "sweep-self poll/settle",
               "pr-contract / pr-contract": "pr-contract codescan_wait", "refresh": "refresh (no wait)",
               "hassfest / hassfest": "NULL hassfest", "tests / typing": "NULL typing",
               "validate / validate-hacs": "NULL validate"}
    w = collections.defaultdict(list)
    for r in runs:
        for j in jobs[r["id"]]:
            if ran(j) and j["name"] in WAITERS:
                w[j["name"]].append((mins(j), kind(r)))
    out["waits"] = {}
    for name, v in w.items():
        floor = pct([m for m, _ in v], .1)
        excess = [max(0.0, m - floor) for m, _ in v]
        out["waits"][WAITERS[name]] = {"n": len(v), "runner_min": round(sum(m for m, _ in v)), "floor_min": round(floor, 2),
                                       "excess_min": round(sum(excess)), "jobs_over_5min_excess": sum(e > 5 for e in excess)}
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("fetch", "report"))
    ap.add_argument("day")
    ap.add_argument("--cache")
    ap.add_argument("--keep-copies", action="store_true",
                    help="the perturbation: count re-run listings' copied jobs as executed")
    a = ap.parse_args()
    (fetch if a.cmd == "fetch" else report)(a)


if __name__ == "__main__":
    main()
