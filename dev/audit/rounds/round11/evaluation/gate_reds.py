#!/usr/bin/env python3
"""Main's push runs of the CI workflow over a window: the `gate` share and the failed jobs per called workflow.

Usage:
  python3 dev/audit/rounds/round11/evaluation/gate_reds.py fetch --dir D --slug OWNER/REPO --from YYYY-MM-DD --to YYYY-MM-DD
  python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir D --window FROM..UNTIL (ISO instants, UTC)
`fetch` reads GitHub with `gh api` (GET only): the workflow's push runs on main in three-day ranges, each listing's
total_count beside the rows fetched so the 1000-result cap shows, then, for each run that concluded `failure`, its jobs that
failed or timed out and its `gate` job. It appends, so an interrupted fetch resumes. `report` prints: runs in the window by
conclusion; the `gate` share (runs whose `gate` job succeeded over concluded runs, a successful run counted as a succeeded
gate, a failed run with no job listing fetched counted `unread`), with the cancelled count beside it; failed jobs per job
name and per called workflow (the job-name prefix before ` / `), the failed jobs of the runs whose `gate` did not
succeed, the job that failed alone on such a run, and those runs per called workflow. A run's cause is not printed: no red carries one.
"""
import argparse, collections, datetime, json, subprocess, sys, time
from pathlib import Path


def gh(path, jq, paginate=True):
    r = subprocess.run(["gh", "api", path, *(["--paginate"] if paginate else []), "--jq", jq], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh api {path}: {r.stderr.strip()[:200]}")
    return [json.loads(l) for l in r.stdout.split("\n") if l.strip()]


def fetch(a):
    d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
    runs_f, jobs_f = d / "ci_runs.jsonl", d / "ci_failed_jobs.jsonl"
    have = {json.loads(l)["id"] for l in open(runs_f)} if runs_f.exists() else set()
    day, end = datetime.date.fromisoformat(getattr(a, "from")), datetime.date.fromisoformat(a.to)
    base = f"repos/{a.slug}/actions/workflows/ci.yml/runs?branch=main&event=push"
    with open(runs_f, "a") as out, open(d / "ci_runs.counts", "a") as counts:
        while day <= end:
            rng = f"{day}..{min(day + datetime.timedelta(days=2), end)}"
            total = gh(f"{base}&created={rng}&per_page=1", ".total_count", paginate=False)[0]
            rows = gh(f"{base}&created={rng}&per_page=100", ".workflow_runs[] | {id, name, run_number, run_attempt, head_sha, created_at, updated_at, status, conclusion}")
            for r in rows:
                if r["id"] not in have:
                    out.write(json.dumps(r) + "\n"); have.add(r["id"])
            counts.write(f"{rng} total_count={total} fetched={len(rows)}\n")
            day += datetime.timedelta(days=3)
    done = {json.loads(l)["run"] for l in open(jobs_f)} if jobs_f.exists() else set()
    with open(jobs_f, "a") as out:
        for l in open(runs_f):
            r = json.loads(l)
            if r["conclusion"] == "failure" and r["id"] not in done:
                pages = gh(f"repos/{a.slug}/actions/runs/{r['id']}/jobs?filter=latest&per_page=100",
                           '[.jobs[] | select(.conclusion=="failure" or .conclusion=="timed_out" or .name=="gate") | {name, conclusion}]')
                out.write(json.dumps({"run": r["id"], "jobs": [j for p in pages for j in p]}) + "\n"); out.flush()
                time.sleep(0.5)


def report(a):
    d = Path(a.dir)
    lo, hi = a.window.split("..", 1)
    runs = {}
    for l in open(d / "ci_runs.jsonl"):
        r = json.loads(l)
        if lo <= r["created_at"] <= hi:
            runs[r["id"]] = r
    jobs = {}
    if (d / "ci_failed_jobs.jsonl").exists():
        for l in open(d / "ci_failed_jobs.jsonl"):
            j = json.loads(l); jobs[j["run"]] = j["jobs"]
    by = collections.Counter(r["conclusion"] for r in runs.values())
    first = min((r["created_at"] for r in runs.values()), default="-")
    print(f"window {a.window}: runs {len(runs)} first {first} " + " ".join(f"{k}={v}" for k, v in sorted(by.items(), key=str)))
    ok = by.get("success", 0); bad = unread = nongate = 0
    names, wf, gate_names = collections.Counter(), collections.Counter(), collections.Counter()
    sole, wf_gate, wf_sole = collections.Counter(), collections.Counter(), collections.Counter()
    runs_wf = collections.Counter()
    for i, r in runs.items():
        if r["conclusion"] != "failure":
            continue
        if i not in jobs:
            unread += 1; continue
        g = [j for j in jobs[i] if j["name"] == "gate"]
        if g and g[0]["conclusion"] == "success":
            ok += 1; nongate += 1
        else:
            bad += 1
            for j in jobs[i]:
                if j["name"] != "gate":
                    gate_names[j["name"]] += 1
            failed = sorted({j["name"] for j in jobs[i] if j["name"] != "gate"})
            wfs = {n.split(" / ")[0] if " / " in n else "(ci.yml's own job)" for n in failed}
            sole[failed[0] if len(failed) == 1 else "none" if not failed else "several"] += 1
            for w in wfs:
                wf_gate[w] += 1
            if len(wfs) == 1:
                wf_sole[next(iter(wfs))] += 1
        seen = set()
        for j in jobs[i]:
            if j["name"] == "gate":
                continue
            names[j["name"]] += 1
            w = j["name"].split(" / ")[0] if " / " in j["name"] else "(ci.yml's own job)"
            wf[w] += 1; seen.add(w)
        for w in seen:
            runs_wf[w] += 1
    concluded = ok + bad
    share = f"{ok}/{concluded} ({ok / concluded:.3f})" if concluded and not unread else f"{ok}/{concluded} with {unread} failed run(s) unread: no share"
    print(f"gate share: {share}; cancelled beside it: {by.get('cancelled', 0)}; failed runs whose gate job succeeded: {nongate}; failed runs read: {bad + nongate}; unread: {unread}")
    print("failed jobs per called workflow (jobs; runs with at least one):")
    for w, n in wf.most_common():
        print(f"  {w}\t{n}\t{runs_wf[w]}")
    print("failed jobs per job name:")
    for n, c in names.most_common(25):
        print(f"  {c}\t{n}")
    print(f"failed jobs on the {bad} run(s) whose gate job did not succeed:")
    for n, c in gate_names.most_common(25):
        print(f"  gate-red {c}\t{n}")
    print("the only failed job on a gate-red run:")
    for n, c in sole.most_common():
        print(f"  sole {c}\t{n}")
    print("gate-red runs per called workflow (runs with a failed job of it; runs where only its jobs failed):")
    for w, c in wf_gate.most_common():
        print(f"  wf-gate {w}\t{c}\t{wf_sole[w]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--dir", required=True); f.add_argument("--slug", required=True); f.add_argument("--from", required=True); f.add_argument("--to", required=True)
    r = sub.add_parser("report"); r.add_argument("--dir", required=True); r.add_argument("--window", required=True)
    a = ap.parse_args()
    (fetch if a.cmd == "fetch" else report)(a)


if __name__ == "__main__":
    main()
