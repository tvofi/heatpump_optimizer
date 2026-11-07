#!/usr/bin/env python3
"""Classify every red `gate` attempt, newest run first, from its own log.

    python3 scan.py <runs.tsv> <out.jsonl> <max_calls> <quota_floor>

Candidates: runs.tsv rows whose latest conclusion is failure or whose run_attempt
exceeds 1 (a first-attempt green run has no red gate attempt). Stops at max_calls
or when core quota falls under quota_floor, and prints how far it got.
"""
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import threading
from datetime import datetime

R = "tvofi/heatpump_optimizer"
runs_tsv, out_path, max_calls, floor = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
lock, calls, stop = threading.Lock(), [0], threading.Event()
STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z (.*)$")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def api(path, *extra):
    with lock:
        calls[0] += 1
        n = calls[0]
    if n >= max_calls:
        stop.set()
    p = subprocess.run(["gh", "api", *extra, path], capture_output=True, text=True, errors="replace")
    return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


def job_log(job_id) -> "str | None":
    """A job's log through merge_train.job_log, the one reader (gh's escape flag
    where gh knows it), each gh call counted by `api`; None when unreadable."""
    sys.path.insert(0, str(repo_root(__file__) / "tools" / "audit" / "seat"))
    import merge_train
    return merge_train.job_log(lambda argv, **_k: api(argv[-1], *argv[2:-1]), R, job_id)


def quota():
    p = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core.remaining"], capture_output=True, text=True)
    return int(p.stdout.strip() or 0)


def iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def reasons(log):
    """The Judge step's stdout: the lines after its group end, before the exit-code error."""
    lines = [ANSI.sub("", x) for x in log.splitlines()]
    start = max((i for i, x in enumerate(lines) if "##[group]Run python3 -I tools/ci/gate.py" in x), default=None)
    if start is None:
        return None, []
    end = next((i for i in range(start + 1, len(lines)) if "##[endgroup]" in lines[i]), None)
    out, at = [], None
    for x in lines[(end or start) + 1:]:
        m = STAMP.match(x)
        if not m:
            continue
        if "##[error]" in m[2] or "Post job cleanup" in m[2] or "##[group]" in m[2]:
            break
        at = at or m[1]
        out.append(m[2])
    return at, out


def one(row):
    if stop.is_set():
        return None
    rid, event, status, concl, attempt, created = row[:6]
    jobs, page = [], 1
    while True:
        rc, body = api(f"repos/{R}/actions/runs/{rid}/jobs?filter=all&per_page=100&page={page}")
        if rc:
            return [{"run": rid, "error": "jobs read", "body": body[:200]}]
        got = json.loads(body)["jobs"]
        jobs += got
        if len(got) < 100:
            break
        page += 1
    res = []
    for g in jobs:
        if g["name"] != "gate" or g["conclusion"] != "failure":
            continue
        log = job_log(g["id"])
        if log is None:
            res.append({"run": rid, "job": g["id"], "error": "log read"})
            continue
        at, why = reasons(log)
        rec = {"run": rid, "event": event, "created": created, "job": g["id"], "attempt": g["run_attempt"],
               "gate_end": g["completed_at"], "read_at": at, "why": why, "lags": {}}
        for w in why:
            m = re.match(r"(?:FAIL )?(.+?): (?:PENDING|ABSENT) \(this run\)$", w) or re.match(r"FAIL (prelude): None$", w)
            if not m or not at:
                continue
            same = [j for j in jobs if j["name"] == m[1] and j["run_attempt"] == g["run_attempt"]]
            if same and same[0]["completed_at"] and same[0]["status"] == "completed":
                rec["lags"][m[1]] = {"s": int((iso(at + "Z") - iso(same[0]["completed_at"])).total_seconds()),
                                     "conclusion": same[0]["conclusion"]}
            else:
                rec["lags"][m[1]] = {"s": None, "conclusion": same[0]["conclusion"] if same else None}
        res.append(rec)
    res.append({"run": rid, "scanned": True, "created": created})
    return res


rows = [r.rstrip("\n").split("\t") for r in open(runs_tsv)]
cand = [r for r in rows if r[3] == "failure" or int(r[4]) > 1]
cand.sort(key=lambda r: r[5], reverse=True)
try:
    seen = {json.loads(x)["run"] for x in open(out_path) if '"scanned"' in x}
except OSError:
    seen = set()
cand = [r for r in cand if r[0] not in seen]
print(f"candidates {len(cand)} of {len(rows)}", flush=True)
done = 0
with open(out_path, "a") as fh, cf.ThreadPoolExecutor(3) as ex:
    for i in range(0, len(cand), 64):
        if stop.is_set() or quota() < floor:
            print(f"STOP calls={calls[0]} quota_floor_or_cap", flush=True)
            break
        for res in ex.map(one, cand[i:i + 64]):
            for rec in res or []:
                fh.write(json.dumps(rec) + "\n")
            done += 1 if res else 0
        fh.flush()
        print(f"scanned {done}/{len(cand)} calls={calls[0]} oldest={cand[min(i + 63, len(cand) - 1)][5]}", flush=True)
print(f"END scanned={done} calls={calls[0]}", flush=True)
