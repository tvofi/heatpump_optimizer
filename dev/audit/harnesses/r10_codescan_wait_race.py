#!/usr/bin/env python3
"""R10-RCA-CODESCAN-WAIT: an edit run whose run id is below its code run's meets an unfinished codeql unit.

    python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --since 2026-10-22 [--until ISO] [--rows]
    python3 -I dev/audit/harnesses/r10_codescan_wait_race.py --selftest

Read-only GitHub API (tools/ci/ghapi.py; GITHUB_TOKEN or GH_TOKEN). Over every
`ci.yml` pull_request run created in the window, grouped by head SHA, it counts:

  edit runs at a head that also has a code run, split INVERTED (the edit run's
  id is below the lowest code run id, so prelude.wait_earlier waits for nothing)
  and ORDERED (it is above, so the prelude waits for the code run);
  RED: the edit run's `pr-contract / pr-contract` attempts whose failing step is
  "Wait for code scanning and list its open alerts" (codescan_wait.py exit 1),
  by run, head and PR;
  RERUN: those attempts with run_attempt > 1, and of them FRESH (a start time
  no earlier attempt had: the job ran again) against CARRIED (GitHub copied an
  earlier attempt's job into a re-run of other jobs).

The cause the document names predicts RED only at INVERTED heads, and only where
a codeql leg of the code run had not completed when the edit run's pr-contract
started; --rows prints each INVERTED head with that comparison.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
import ghapi  # noqa: E402

REPO = "tvofi/heatpump_optimizer"
STEP = "Wait for code scanning and list its open alerts"
PC = "pr-contract / pr-contract"


def kind(run):
    parts = (run.get("display_title") or "").split()
    return parts[1] if len(parts) > 1 else ""


def pr_of(run):
    parts = (run.get("display_title") or "").split()
    return parts[2] if len(parts) > 2 else ""


#: The item ceiling ghapi.MAX_PAGES gives at 100 a page, kept at every page size.
MAX_ITEMS = ghapi.MAX_PAGES * 100


def pages(get, path, params):
    """Every item, paged by `page=` rather than the Link header (whose
    repositories/<id> form some proxies refuse); ghapi.paginate's one-list rule.
    ghapi.get already retries a 5xx twice with backoff; one that persists
    (run 40126133450: page 2 of per_page=100 answered 502, per_page=30 answered
    200) restarts the listing at the next smaller page size; a 4xx raises.
    Each size is bounded by MAX_ITEMS items, not MAX_PAGES pages: at 30 a page
    MAX_PAGES is 1500 items, and a re-run run lists every attempt's jobs (run
    42454528717: 1760)."""
    for size in (100, 30):
        out = []
        for n in range(1, -(-MAX_ITEMS // size) + 1):
            st, _, doc = get(path, dict(params, per_page=size, page=n))
            if st >= 500 and size != 30:
                break
            if st != 200 or not isinstance(doc, dict):
                raise ghapi.ApiError(path, st, "")
            items = next(v for v in doc.values() if isinstance(v, list))
            out += items
            if len(items) < size:
                return out
        else:
            raise ghapi.ApiError(path, 200, "too many pages")
    raise AssertionError("unreachable")


def jobs_all(get, rid, attempts=1):
    """Every attempt's jobs. A run whose `filter=all` listing GitHub cannot page (run
    42425147012, 16 attempts and 640 jobs: pages 2-6 answer HTTP 502 on every read) is read
    one attempt at a time instead."""
    try:
        return pages(get, f"repos/{REPO}/actions/runs/{rid}/jobs", {"filter": "all"})
    except ghapi.ApiError as e:
        if e.status < 500:
            raise
        return [j for n in range(1, attempts + 1)
                for j in pages(get, f"repos/{REPO}/actions/runs/{rid}/attempts/{n}/jobs", {})]


CAP = 1000      # GitHub lists at most 1000 runs for a filtered query, silently


def windows(since, until, days=1):
    """[since, until) cut into `days`-long windows, so no listing reaches CAP unseen."""
    def utc(x):
        d = datetime.fromisoformat(x.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)      # a bare date (--since 2026-10-22) is UTC
    t, end = utc(since), utc(until)
    while t < end:
        nxt = min(t + timedelta(days=days), end)
        yield t.strftime("%Y-%m-%dT%H:%M:%SZ"), nxt.strftime("%Y-%m-%dT%H:%M:%SZ")
        t = nxt


def measure(runs, jobs_of):
    """The counts over `runs` (the listing's run objects); `jobs_of(id)` returns a run's jobs, every attempt."""
    heads = defaultdict(list)
    for r in runs:
        if r.get("event") == "pull_request":
            heads[r["head_sha"]].append(r)
    out = dict(inverted=0, ordered=0, red_inverted=0, red_ordered=0, red_attempts=0,
               rerun=0, fresh=0, carried=0, red_heads=set(), red_prs=set(), rows=[])
    for sha, rs in heads.items():
        code = [r for r in rs if kind(r) == "code"]
        if not code:
            continue
        low = min(r["id"] for r in code)
        for e in (r for r in rs if kind(r) == "edit"):
            inv = e["id"] < low
            out["inverted" if inv else "ordered"] += 1
            pcs = sorted((j for j in jobs_of(e["id"]) if j["name"] == PC), key=lambda j: j.get("run_attempt", 1))
            red = [j for j in pcs if j.get("conclusion") == "failure"
                   and any(s["name"] == STEP and s.get("conclusion") == "failure" for s in j.get("steps") or [])]
            seen = set()
            for j in pcs:
                if j in red and j.get("run_attempt", 1) > 1:
                    out["rerun"] += 1
                    out["carried" if j.get("started_at") in seen else "fresh"] += 1
                seen.add(j.get("started_at"))
            if red:
                out["red_inverted" if inv else "red_ordered"] += 1
                out["red_attempts"] += len(red)
                out["red_heads"].add(sha)
                out["red_prs"].add(pr_of(e))
            if inv:
                legs = [j for c in code for j in jobs_of(c["id"]) if j["name"].startswith("codeql / Analyze")]
                last = max((j.get("completed_at") or "9999") for j in legs) if legs else ""
                first = pcs[0].get("started_at") if pcs else ""
                out["rows"].append((sha[:8], pr_of(e), e["id"], low, first or "-", last or "-",
                                    bool(first and last and last > first), len(red)))
    return out


def report(o, rows=False):
    print(f"edit runs at a head with a code run: INVERTED {o['inverted']}, ORDERED {o['ordered']}")
    print(f"RED edit runs: {o['red_inverted']} INVERTED, {o['red_ordered']} ORDERED; "
          f"{o['red_attempts']} job attempts, {len(o['red_heads'])} heads, {len(o['red_prs'])} PRs ({' '.join(sorted(o['red_prs']))})")
    print(f"RERUN attempts among the red: {o['rerun']} (FRESH {o['fresh']}, CARRIED {o['carried']})")
    if rows:
        print("head     pr        edit_run    code_run    edit_pr_contract_start  last_codeql_leg_done  leg_unfinished  red_attempts")
        for r in o["rows"]:
            print(*r)


def selftest():
    def run(i, k, sha):
        return dict(id=i, event="pull_request", head_sha=sha, display_title=f"CI {k} pr=9 base=main sha=m")

    def pc(att, ok, t):
        return dict(name=PC, run_attempt=att, started_at=t, conclusion="success" if ok else "failure",
                    steps=[dict(name=STEP, conclusion="success" if ok else "failure")])

    leg = dict(name="codeql / Analyze (python)", completed_at="T30")
    runs = [run(1, "edit", "A"), run(2, "code", "A"),        # inverted, leg late: red, one fresh rerun, one carried
            run(3, "code", "B"), run(4, "edit", "B"),        # ordered: green
            run(5, "edit", "C"), run(6, "code", "C")]        # inverted, legs stood down early: green
    jobs = {1: [pc(1, False, "T10"), pc(2, False, "T20"), pc(3, False, "T20")], 2: [leg],
            3: [leg], 4: [pc(1, True, "T40")],
            5: [pc(1, True, "T10")], 6: [dict(leg, completed_at="T05")]}
    o = measure(runs, lambda i: jobs.get(i, []))
    want = dict(inverted=2, ordered=1, red_inverted=1, red_ordered=0, red_attempts=3, rerun=2, fresh=1, carried=1)
    bad = [k for k, v in want.items() if o[k] != v]
    rows_ok = [r[6] for r in o["rows"]] == [True, False]
    w = list(windows("2026-11-01", "2026-11-03T12:00:00Z"))
    want_w = [("2026-11-01T00:00:00Z", "2026-11-02T00:00:00Z"), ("2026-11-02T00:00:00Z", "2026-11-03T00:00:00Z"),
              ("2026-11-03T00:00:00Z", "2026-11-03T12:00:00Z")]
    if w != want_w:
        bad.append(f"windows: {w}")

    def flaky(path, params):              # the 42425147012 shape: filter=all cannot page, per attempt can
        if path.endswith("/runs/5/jobs"):
            return (200, {}, {"jobs": [{}] * 100}) if params.get("page") == 1 else (502, {}, {})
        if "/runs/5/attempts/" in path:
            return 200, {}, {"jobs": [{"name": path.split("/")[-2]}]}
        return 404, {}, {}

    def caught(f):                         # a check whose call raises fails, it does not end the selftest
        try:
            return f()
        except ghapi.ApiError as e:
            return e
    if caught(lambda: [j["name"] for j in jobs_all(flaky, 5, 3)]) != ["1", "2", "3"]:
        bad.append("jobs_all: no per-attempt read after a 5xx")
    try:
        jobs_all(lambda path, params: (200, {}, {"jobs": []}) if "/attempts/" in path else (404, {}, {}), 5, 3)
        bad.append("jobs_all: a 4xx was read around")
    except ghapi.ApiError:
        pass
    calls = []

    def fake(fail_p2_at):
        def get(path, params):
            calls.append((params["per_page"], params["page"]))
            n, size = params["page"], params["per_page"]
            if size == fail_p2_at and n == 2:
                return 502, {}, {}
            if path == "404":
                return 404, {}, {}
            total = 150
            return 200, {}, {"jobs": list(range((n - 1) * size, min(n * size, total)))}
        return get
    got = caught(lambda: pages(fake(100), "x", {}))
    pages_ok = got == list(range(150)) and calls == [(100, 1), (100, 2)] + [(30, i) for i in range(1, 7)]
    calls.clear()
    clean_ok = caught(lambda: pages(fake(0), "x", {})) == list(range(150)) and calls == [(100, 1), (100, 2)]
    calls.clear()
    try:
        pages(fake(0), "404", {})
        null_ok = False
    except ghapi.ApiError as e:
        null_ok = e.status == 404 and len(calls) == 1
    # carry 5: the measured server, a 502 for any page over 50 jobs, serving 70 jobs.
    asked = []

    def server(total):
        def get(path, params):
            asked.append(params["per_page"])
            if params["per_page"] > 50:
                return 502, {}, None
            lo = (params["page"] - 1) * params["per_page"]
            return 200, {}, {"jobs": list(range(total))[lo:lo + params["per_page"]]}
        return get

    def paged(total):
        asked.clear()
        return caught(lambda: pages(server(total), "repos/o/r/actions/runs/1/jobs", {"filter": "all"}))
    over50_ok = paged(70) == list(range(70)) and asked == [100, 30, 30, 30]
    # run 42454528717's 1760 jobs, every attempt listed, behind the same 502 at 100 a page.
    many_ok = paged(1760) == list(range(1760)) and asked == [100] + [30] * 59
    pg = dict(fallback=pages_ok, clean=clean_ok, **{"4xx": null_ok}, over50=over50_ok, many1760=many_ok)
    pbad = [k for k, v in pg.items() if not v]
    print(f"selftest: {len(want) + 4 + len(pg)} checks, {len(bad) + (not rows_ok) + len(pbad)} failed"
          f"{' ' + str(bad) if bad else ''}{'' if rows_ok else ' rows'}{' pages' + str(pbad) if pbad else ''}")
    return 1 if bad or not rows_ok or pbad else 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--rows", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.since:
        ap.error("--since is required")
    until = a.until or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    runs = []
    for lo, hi in windows(a.since, until):
        got = pages(ghapi.get, f"repos/{REPO}/actions/workflows/ci.yml/runs",
                    {"created": f"{lo}..{hi}", "event": "pull_request"})
        if len(got) >= CAP:
            raise SystemExit(f"REFUSE {lo}..{hi} lists {len(got)} runs, GitHub's cap: a narrower window is owed")
        runs += [r for r in got if r["id"] not in {x["id"] for x in runs}]   # a boundary second is in both
    attempts = {r["id"]: r.get("run_attempt", 1) for r in runs}
    cache = {}

    def jobs_of(i):
        if i not in cache:
            cache[i] = jobs_all(ghapi.get, i, attempts.get(i, 1))
        return cache[i]
    print(f"ci.yml pull_request runs created {a.since}..{until}: {len(runs)}")
    report(measure(runs, jobs_of), a.rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
