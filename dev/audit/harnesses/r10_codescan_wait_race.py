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


def pages(get, path, params):
    """Every item, paged by `page=` rather than the Link header (whose
    repositories/<id> form some proxies refuse); ghapi.paginate's one-list rule."""
    out = []
    for n in range(1, ghapi.MAX_PAGES + 1):
        st, _, doc = get(path, dict(params, per_page=100, page=n))
        if st != 200 or not isinstance(doc, dict):
            raise ghapi.ApiError(path, st, "")
        items = next(v for v in doc.values() if isinstance(v, list))
        out += items
        if len(items) < 100:
            return out
    raise ghapi.ApiError(path, 200, "too many pages")


def jobs_all(get, rid):
    return pages(get, f"repos/{REPO}/actions/runs/{rid}/jobs", {"filter": "all"})


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
    print(f"selftest: {len(want) + 1} checks, {len(bad) + (not rows_ok)} failed{' ' + str(bad) if bad else ''}")
    return 1 if bad or not rows_ok else 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--until", default="*")
    ap.add_argument("--rows", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.since:
        ap.error("--since is required")
    runs = pages(ghapi.get, f"repos/{REPO}/actions/workflows/ci.yml/runs",
                 {"created": f"{a.since}..{a.until}", "event": "pull_request"})
    cache = {}

    def jobs_of(i):
        if i not in cache:
            cache[i] = jobs_all(ghapi.get, i)
        return cache[i]
    print(f"ci.yml pull_request runs created {a.since}..{a.until}: {len(runs)}")
    report(measure(runs, jobs_of), a.rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
