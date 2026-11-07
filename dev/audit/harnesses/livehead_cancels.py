"""Cancelled `ci.yml` attempts, attributed to their canceller, and whether each was at the live head.

    python3 dev/audit/harnesses/livehead_cancels.py --cache DIR --fetch --since ISO [--until ISO]
    python3 dev/audit/harnesses/livehead_cancels.py --cache DIR [--since ISO] [--until ISO] [--list]
    python3 dev/audit/harnesses/livehead_cancels.py --selftest

R10-RCA-LIVEHEAD-CANCEL. The runs listing shows only a run's LATEST attempt, so a
cancelled attempt that a rerun replaced is invisible to `gh run list`; --fetch reads
every earlier attempt of a run with `run_attempt > 1` (read-only `gh api`, every exit
status checked), listing runs in 6-hour created= slices and refusing a slice that
reaches GitHub's silent 1000-run cap on a filtered listing, and writes `DIR/attempts.jsonl` (one attempt per line, with the
`gh api .../attempts/<n>` fields) and `DIR/cancellers.jsonl` (per cancelled attempt:
the annotation lines of its earliest- and latest-completed cancelled job).

The rule, per cancelled attempt (conclusion `cancelled`, event `pull_request`,
branch not main):

  CANCELLER is read from the cancelled jobs' check-run annotations, which GitHub
  writes itself: `The run was canceled by @<login>.` names the credential that
  POSTed the cancel; `exceeded the maximum execution time` is a job timeout;
  `Canceling since a higher priority waiting request` is a `concurrency:` cancel;
  none of these is `unattributed`.  The earliest-completed cancelled job decides,
  and a timeout attempt is re-read at its latest-completed cancelled job, so a
  manual cancel after a timeout reads `timeout+@<login>`.
  LIVE is whether the attempt's head_sha is the branch's head at the cancel time
  (the attempt's updated_at): the head_sha of the latest-created pull_request
  `ci.yml` run on that branch created at or before that time.  A push that
  started no run is invisible to this proxy, which can only read a superseded
  attempt as live, never the reverse.

The class this harness measures is `@<login>` other than `github-actions[bot]`
at a LIVE head: a whole-run cancel nobody's superseded-run rule made.
`github-actions[bot]` is `tools/pr/cancel_superseded.py` run inside CI under
`github.token`; an operator `sweep` of the same program runs under the
operator's credential and never cancels a run at the live head.

Null controls, on every invocation: every LIVE attempt's head forced to a newer
sha must print 0 live (NULLCONTROL-HEAD), and every canceller forced to
`github-actions[bot]` must print 0 in the class (NULLCONTROL-BOT).  --selftest
runs both on synthetic attempts with no cache.
"""
from __future__ import annotations

import argparse
import calendar
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
BOT = "github-actions[bot]"
PAGE = 100
TRANSIENT = ("(HTTP 5", "connection reset", "EOF", "timeout", "TLS handshake")
CAP = 1000  # GitHub's ceiling on a filtered runs listing, reached silently


def gh(path: str) -> object:
    """One read; a transient failure (5xx, a reset or dropped connection) is retried after
    2, 4 and 8 s, and any other failure (a 4xx) stops the fetch."""
    for wait in (2, 4, 8, None):
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode == 0:
            return json.loads(p.stdout)
        if wait is None or not any(t in p.stderr for t in TRANSIENT):
            break
        time.sleep(wait)
    raise SystemExit(f"gh api {path}: exit {p.returncode}: {p.stderr.strip()[:200]}")


def kind(title: str) -> str:
    parts = (title or "").split()
    return parts[1] if len(parts) > 1 and parts[0] == "CI" else "?"


def canceller(lines: list[str]) -> str:
    for m in lines:
        if "exceeded the maximum execution time" in m:
            return "timeout"
        if m.startswith("The run was canceled by @"):
            return "@" + m[len("The run was canceled by @"):].rstrip(".")
        if "higher priority waiting request" in m:
            return "concurrency"
    return "unattributed"


def attribute(first: list[str], last: list[str] | None) -> str:
    c = canceller(first)
    if c == "timeout" and last is not None:
        c2 = canceller(last)
        if c2.startswith("@"):
            return f"timeout+{c2}"
    return c


def head_at(runs: list[dict], branch: str, t: str) -> str | None:
    best = None
    for r in runs:
        if r.get("head_branch") == branch and r.get("event") == "pull_request" and r["created_at"] <= t:
            if best is None or (r["created_at"], r["id"]) > (best["created_at"], best["id"]):
                best = r
    return best and best.get("head_sha")


def classify(attempts: list[dict], cancellers: dict[str, str]) -> list[dict]:
    """One row per cancelled pull_request attempt off main; the pure part."""
    out = []
    for a in attempts:
        if a.get("conclusion") != "cancelled" or a.get("event") != "pull_request" or a.get("head_branch") == "main":
            continue
        key = f"{a['id']}/{a['run_attempt']}"
        t = a["updated_at"]
        out.append({"key": key, "pr_kind": kind(a.get("display_title", "")), "branch": a["head_branch"],
                    "sha": a["head_sha"][:12], "start": a.get("run_started_at"), "cancel": t,
                    "minutes": round(minutes(a.get("run_started_at"), t), 1),
                    "by": cancellers.get(key, "unread"),
                    "live": head_at(attempts, a["head_branch"], t) == a["head_sha"]})
    return out


def minutes(a: str | None, b: str) -> float:
    if not a:
        return 0.0
    f = "%Y-%m-%dT%H:%M:%SZ"
    return (time.mktime(time.strptime(b, f)) - time.mktime(time.strptime(a, f))) / 60


def in_class(row: dict) -> bool:
    return row["live"] and row["by"].removeprefix("timeout+").startswith("@") and BOT not in row["by"]


def report(rows: list[dict], show: bool) -> dict:
    tally = Counter((r["by"], "live" if r["live"] else "superseded") for r in rows)
    cls = [r for r in rows if in_class(r)]
    for (by, live), n in sorted(tally.items()):
        print(f"CANCELLED  {n:5d}  by={by:28s} head={live}")
    print(f"CLASS live-head external cancels: {len(cls)}, minutes lost {sum(r['minutes'] for r in cls):.1f} "
          f"(attempt start to cancel)")
    for r in cls if show else []:
        print(f"  {r['key']:16s} {r['pr_kind']:6s} {r['branch'][:34]:34s} {r['sha']} "
              f"{r['start']} -> {r['cancel']} {r['minutes']:5.1f} min {r['by']}")
    nh = [dict(r, live=False) for r in rows]
    nb = [dict(r, by=f"@{BOT}") for r in rows]
    print(f"NULLCONTROL-HEAD live={sum(r['live'] for r in nh)} class={sum(in_class(r) for r in nh)}")
    print(f"NULLCONTROL-BOT class={sum(in_class(r) for r in nb)}")
    return {"rows": len(rows), "class": len(cls)}


def slices(since: str, until: str, hours: int = 6) -> list[tuple[str, str]]:
    """[since, until) cut into `hours`-wide created= windows, each well under the cap."""
    f = "%Y-%m-%dT%H:%M:%SZ"
    lo, hi = calendar.timegm(time.strptime(since, f)), calendar.timegm(time.strptime(until, f))
    out = []
    while lo < hi:
        nx = min(lo + hours * 3600, hi)
        out.append((time.strftime(f, time.gmtime(lo)), time.strftime(f, time.gmtime(nx - 1))))
        lo = nx
    return out


def fetch(cache: Path, since: str, until: str | None) -> None:
    """GitHub returns at most CAP runs for a filtered listing and says nothing when it
    stops, so the window is read in slices and a slice that reaches CAP is refused."""
    cache.mkdir(parents=True, exist_ok=True)
    if (cache / "attempts.jsonl").exists():
        print(f"fetch: reusing {cache / 'attempts.jsonl'}; delete it to re-list")
        return fetch_cancellers(cache, [json.loads(x) for x in open(cache / "attempts.jsonl")])
    until = until or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    attempts: list[dict] = []
    for lo, hi in slices(since, until):
        got_n = 0
        for pg in range(1, CAP // PAGE + 1):
            got = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?per_page={PAGE}&page={pg}&created={lo}..{hi}")
            rs = got["workflow_runs"]
            got_n += len(rs)
            for r in rs:
                attempts.append(r)
                for n in range(1, int(r.get("run_attempt") or 1)):
                    attempts.append(gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}"))
            if len(rs) < PAGE:
                break
        if got_n >= CAP or got.get("total_count", 0) > got_n:
            raise SystemExit(f"slice {lo}..{hi}: {got_n} of {got.get('total_count')} runs read "
                             f"(listing cap {CAP}); narrow the slice")
    keep = ("id", "run_attempt", "event", "status", "conclusion", "head_branch", "head_sha", "created_at",
            "run_started_at", "updated_at", "display_title")
    with open(cache / "attempts.jsonl", "w") as f:
        for a in attempts:
            f.write(json.dumps({k: a.get(k) for k in keep}) + "\n")
    fetch_cancellers(cache, attempts)


def fetch_cancellers(cache: Path, attempts: list[dict]) -> None:
    """One record per cancelled attempt, appended, so a stopped fetch resumes where it stopped."""
    path = cache / "cancellers.jsonl"
    done = {json.loads(x)["key"] for x in open(path)} if path.exists() else set()
    with open(path, "a") as f:
        for a in attempts:
            if f"{a['id']}/{a['run_attempt']}" in done:
                continue
            if a.get("conclusion") != "cancelled" or a.get("event") != "pull_request" or a.get("head_branch") == "main":
                continue
            jobs = gh(f"repos/{REPO}/actions/runs/{a['id']}/attempts/{a['run_attempt']}/jobs?per_page=100")["jobs"]
            cj = sorted((j for j in jobs if j.get("conclusion") == "cancelled" and j.get("completed_at")),
                        key=lambda j: j["completed_at"])
            rec = {"key": f"{a['id']}/{a['run_attempt']}", "first": [], "last": None}
            if cj:
                rec["first"] = [x["message"] for x in gh(f"repos/{REPO}/check-runs/{cj[0]['id']}/annotations")]
                if canceller(rec["first"]) == "timeout" and len(cj) > 1:
                    rec["last"] = [x["message"] for x in gh(f"repos/{REPO}/check-runs/{cj[-1]['id']}/annotations")]
            f.write(json.dumps(rec) + "\n")
            f.flush()


def load(cache: Path, since: str | None, until: str | None) -> list[dict]:
    attempts = [json.loads(x) for x in open(cache / "attempts.jsonl")]
    cancellers = {}
    for x in open(cache / "cancellers.jsonl"):
        r = json.loads(x)
        cancellers[r["key"]] = attribute(r["first"], r["last"])
    rows = classify(attempts, cancellers)
    return [r for r in rows if (not since or r["cancel"] >= since) and (not until or r["cancel"] <= until)]


def selftest() -> int:
    def att(i, n, sha, created, upd, concl="cancelled", br="fix/a", ev="pull_request"):
        return {"id": i, "run_attempt": n, "event": ev, "conclusion": concl, "head_branch": br,
                "head_sha": sha * 40, "created_at": created, "run_started_at": created, "updated_at": upd,
                "display_title": "CI code pr=1"}
    atts = [att(1, 1, "a", "2026-11-07T03:00:00Z", "2026-11-07T03:10:00Z"),          # live, @owner
            att(2, 1, "b", "2026-11-07T03:20:00Z", "2026-11-07T03:30:00Z"),          # superseded by sha c
            att(3, 1, "c", "2026-11-07T03:25:00Z", "2026-11-07T03:40:00Z", "success"),
            att(4, 1, "d", "2026-11-07T03:00:00Z", "2026-11-07T03:30:00Z", br="fix/b"),  # timeout only
            att(5, 1, "e", "2026-11-07T03:00:00Z", "2026-11-07T03:20:00Z", br="main")]
    canc = {"1/1": attribute(["The run was canceled by @owner.", "The operation was canceled."], None),
            "2/1": attribute(["The run was canceled by @github-actions[bot]."], None),
            "4/1": attribute(["The job has exceeded the maximum execution time of 30m0s"], None)}
    rows = classify(atts, canc)
    got = {r["key"]: (r["by"], r["live"]) for r in rows}
    want = {"1/1": ("@owner", True), "2/1": ("@github-actions[bot]", False), "4/1": ("timeout", True)}
    ok = got == want
    ok &= [r["key"] for r in rows if in_class(r)] == ["1/1"]
    ok &= attribute(["The job has exceeded the maximum execution time of 30m0s"],
                    ["The run was canceled by @owner."]) == "timeout+@owner"
    ok &= not any(in_class(dict(r, live=False)) for r in rows)
    ok &= not any(in_class(dict(r, by=f"@{BOT}")) for r in rows)
    sl = slices("2026-11-04T00:00:00Z", "2026-11-04T13:00:00Z")
    ok &= sl == [("2026-11-04T00:00:00Z", "2026-11-04T05:59:59Z"), ("2026-11-04T06:00:00Z", "2026-11-04T11:59:59Z"),
                 ("2026-11-04T12:00:00Z", "2026-11-04T12:59:59Z")]
    print(f"selftest: {'ok' if ok else 'FAILED'} {got} slices={len(sl)}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cache:
        ap.error("--cache is required")
    if a.fetch:
        if not a.since:
            ap.error("--fetch needs --since")
        fetch(a.cache, a.since, a.until)
    report(load(a.cache, a.since, a.until), a.list)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
