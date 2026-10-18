"""Compute CI job/run durations for tests.yml from saved raw JSON.

Usage: python3 -I measure.py <measure_dir>
Reads <dir>/raw/runs_{pull_request,push_main,schedule}.json and raw/jobs_<run_id>.json
(fetched by fetch.sh: GET .../actions/workflows/tests.yml/runs and
.../actions/runs/<id>/jobs?filter=latest&per_page=100), writes jobs.tsv and summary.md.

Selection: per event, take runs newest-first (API order); skip a run whose
conclusion is 'cancelled' AND which has no job concluded success/failure
(nothing completed to measure); stop at N (pull_request 20, push/main 5,
schedule 5). A job is 'executed' when its conclusion != 'skipped'; skipped jobs
count 0 s. Run wall clock = max(job.completed_at) - run.run_started_at
(fallback created_at).
"""
import json, os, sys, math
from datetime import datetime
from collections import defaultdict, Counter

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(D, "raw")

def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") if s else None

def pct(xs, p):
    # nearest-rank percentile
    xs = sorted(xs)
    if not xs: return None
    k = max(1, math.ceil(p / 100 * len(xs)))
    return xs[k - 1]

def median(xs):
    xs = sorted(xs); n = len(xs)
    if not n: return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

def load(name):
    with open(os.path.join(RAW, name)) as f:
        return json.load(f)

def select(runsfile, n):
    used, skipped = [], []
    for r in load(runsfile)["workflow_runs"]:
        if len(used) >= n: break
        jobs = load("jobs_%d.json" % r["id"])["jobs"]
        if r["conclusion"] == "cancelled" and not any(j["conclusion"] in ("success", "failure") for j in jobs):
            skipped.append(r["id"]); continue
        used.append((r, jobs))
    return used, skipped

def rows_for(used):
    rows, runs = [], []
    for r, jobs in used:
        start = ts(r.get("run_started_at") or r["created_at"])
        ends = []
        for j in jobs:
            s, c = ts(j["started_at"]), ts(j["completed_at"])
            sec = 0 if j["conclusion"] == "skipped" or not (s and c) else max(0, int((c - s).total_seconds()))
            if c: ends.append(c)
            rows.append(dict(run_id=r["id"], head_sha=r["head_sha"], job_name=j["name"],
                             conclusion=j["conclusion"], started_at=j["started_at"],
                             completed_at=j["completed_at"], seconds=sec,
                             pr=",".join(str(p if isinstance(p, int) else p.get("number")) for p in r.get("pull_requests") or [])))
        wall = int((max(ends) - start).total_seconds()) if ends else 0
        runs.append(dict(id=r["id"], sha=r["head_sha"][:10], conclusion=r["conclusion"], attempt=r["run_attempt"],
                         created=r["created_at"], wall=wall,
                         pr=",".join(str(p if isinstance(p, int) else p.get("number")) for p in r.get("pull_requests") or [])))
    return rows, runs

def fmt(x):
    return "-" if x is None else ("%d" % x if float(x).is_integer() else "%.1f" % x)

def mmss(x):
    return "-" if x is None else "%d:%02d" % (int(x) // 60, int(x) % 60)

def job_table(rows, only=None):
    by = defaultdict(list)
    for r in rows: by[r["job_name"]].append(r)
    out = ["| job | executed | skipped | conclusions (executed) | median s | p90 s | max s |", "|---|---|---|---|---|---|---|"]
    for name in sorted(by):
        if only and not any(name == o or name.startswith(o + " ") for o in only): continue
        ex = [r for r in by[name] if r["conclusion"] != "skipped"]
        secs = [r["seconds"] for r in ex if r["conclusion"] in ("success", "failure")]
        cc = Counter(r["conclusion"] for r in ex)
        out.append("| `%s` | %d | %d | %s | %s | %s | %s |" % (
            name, len(ex), len(by[name]) - len(ex),
            ", ".join("%s %d" % kv for kv in sorted(cc.items())) or "-",
            fmt(median(secs)), fmt(pct(secs, 90)), fmt(max(secs) if secs else None)))
    return out

def run_section(title, runsfile, n, rows_acc, only=None, note=""):
    used, skipped = select(runsfile, n)
    rows, runs = rows_for(used)
    rows_acc.extend(rows)
    walls = [r["wall"] for r in runs]
    dates = sorted(r["created"] for r in runs)
    total = load(runsfile)["total_count"]
    L = ["## %s" % title, ""]
    if note: L += [note, ""]
    L += ["- runs used: %d (of %d listed on the first page; API total_count %d)" % (len(runs), len(load(runsfile)["workflow_runs"]), total),
          "- date range (created_at): %s .. %s" % (dates[0], dates[-1]) if dates else "- no runs",
          "- skipped as cancelled-with-no-completed-jobs: %s" % (", ".join(map(str, skipped)) or "none"),
          "- run conclusions: %s" % ", ".join("%s %d" % kv for kv in sorted(Counter(r["conclusion"] for r in runs).items())),
          "- per-run wall clock, all runs used incl. cancelled (max job completed_at - run_started_at): median %s s (%s), p90 %s s (%s), max %s s (%s)" % (
              fmt(median(walls)), mmss(median(walls)), fmt(pct(walls, 90)), mmss(pct(walls, 90)), fmt(max(walls)), mmss(max(walls))),
          "", "### Per job name", ""]
    L += job_table(rows, only)
    L += ["", "### Runs used", "", "| run id | PR | head sha | attempt | conclusion | created_at | wall s |", "|---|---|---|---|---|---|---|"]
    L += ["| %d | %s | %s | %d | %s | %s | %d |" % (r["id"], r["pr"] or "-", r["sha"], r["attempt"], r["conclusion"], r["created"], r["wall"]) for r in runs]
    return L + [""]

def main():
    rows = []
    S = ["# tests.yml CI duration measurement", "",
         "Source (fetched read-only by `fetch.sh`, the same REST endpoints the GitHub MCP `actions_list` tool wraps): GitHub REST `actions/workflows/tests.yml/runs` and `actions/runs/<id>/jobs?filter=latest`, saved under `raw/`; computed by `measure.py`.",
         "Percentiles are nearest-rank; median is the usual midpoint median. 'executed' = job conclusion is not `skipped` (includes success, failure, cancelled). Skipped jobs count 0 s. Duration stats (median/p90/max) are over executed jobs that concluded success or failure only; cancelled jobs are counted but excluded, since a superseded run's cancel truncates them (some never started: completed_at precedes started_at, clamped to 0 s in jobs.tsv). jobs.tsv holds every job row of every run used in all three sections.",
         "Job names are taken verbatim: a matrix job that was skipped appears under its unexpanded name (`nightly-ha`, `mutation-pins`), an executed one under its expanded name (`nightly-ha (2025.2.0)`, `mutation-pins (1)`); some older runs name the fast lane `fast` instead of `fast (3.14)`.", ""]
    S += run_section("Pull-request runs (20 most recent completed)", "runs_pull_request.json", 20, rows)
    sched = ["mutation-nightly", "slow", "nightly-ha", "mutation-ledger", "coverage", "composed-proof", "record-autofix"]
    S += run_section("Push to main (5 most recent completed)", "runs_push_main.json", 5, rows)
    S += run_section("Schedule (5 most recent completed)", "runs_schedule.json", 5, rows)
    # scheduled-only job focus across push+schedule
    sel = [r for r in rows if r["run_id"] in {u[0]["id"] for u in select("runs_schedule.json", 5)[0] + select("runs_push_main.json", 5)[0]}]
    S += ["## Scheduled-lane jobs only, push/main + schedule runs combined", ""] + job_table(sel, sched) + [""]
    with open(os.path.join(D, "jobs.tsv"), "w") as f:
        cols = ["run_id", "head_sha", "job_name", "conclusion", "started_at", "completed_at", "seconds"]
        f.write("\t".join(cols) + "\n")
        for r in rows: f.write("\t".join(str(r[c]) if r[c] is not None else "" for c in cols) + "\n")
    with open(os.path.join(D, "summary.md"), "w") as f:
        f.write("\n".join(S))

main()
