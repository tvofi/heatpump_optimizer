#!/usr/bin/env python3
"""R10-FLY-GH-READ-RETRY carries 8/10: a red still running when pr-contract lists the reds at its head.

    python3 -I dev/audit/harnesses/r10_red_list_lag.py --since 2026-11-07T00:00:00Z [--until ISO] [--rows]
    python3 -I dev/audit/harnesses/r10_red_list_lag.py --selftest

Read-only GitHub API (tools/ci/ghapi.py; GITHUB_TOKEN or GH_TOKEN). pr-contract's
step "List the red checks at this head" keeps only check runs that are
`completed` with conclusion `failure`, so a check run still in progress when the
step reads the list, and red later, is a red the body never had to answer. Over
every `pr-contract / pr-contract` job of the `ci.yml` pull_request runs created in
the window, it counts:

  LISTS: the jobs whose list step completed;
  REDS: the check runs at those heads concluded `failure` (pr-contract and gate
  excluded, as the step excludes them) -- the null control: what the count below
  would be if no red had finished before the list was read;
  LAGGING: of those, the ones started at or before the step's completion and
  completed after it -- the fail-open the carry asks about.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
import ghapi  # noqa: E402
from r10_codescan_wait_race import pages  # noqa: E402  the 30-per-page reader (carry 5)

REPO = "tvofi/heatpump_optimizer"
PC = "pr-contract / pr-contract"
STEP = "List the red checks at this head"
SKIP = (PC, "gate")  # the step's own two exclusions


def lagging(listed_at: str, checks: list[dict]) -> tuple[list[dict], list[dict]]:
    """(reds, lagging): the failed check runs the step's filter keys on, and those
    of them still running at `listed_at` (started at or before it, completed after)."""
    reds = [c for c in checks if c.get("conclusion") == "failure" and c["name"] not in SKIP]
    late = [c for c in reds if (c.get("started_at") or "") <= listed_at < (c.get("completed_at") or "~")]
    return reds, late


def measure(runs, jobs_of, checks_of):
    out = dict(lists=0, reds=0, lagging=0, rows=[])
    for r in runs:
        for j in jobs_of(r["id"]):
            if j["name"] != PC:
                continue
            step = [s for s in j.get("steps") or [] if s["name"] == STEP and s.get("completed_at")]
            if not step:
                continue
            at = step[0]["completed_at"]
            reds, late = lagging(at, checks_of(r["head_sha"]))
            out["lists"] += 1
            out["reds"] += len(reds)
            out["lagging"] += len(late)
            out["rows"] += [(r["id"], j.get("run_attempt", 1), r["head_sha"][:8], c["name"], c.get("started_at"),
                             at, c.get("completed_at")) for c in late]
    return out


def selftest() -> int:
    bad = []
    checks = [dict(name="tests / fast", conclusion="failure", started_at="T05", completed_at="T20"),   # lagging
              dict(name="lint", conclusion="failure", started_at="T01", completed_at="T09"),           # listed
              dict(name="docs", conclusion="success", started_at="T05", completed_at="T20"),           # green
              dict(name="late", conclusion="failure", started_at="T11", completed_at="T30"),           # started after
              dict(name=PC, conclusion="failure", started_at="T05", completed_at="T20"),               # excluded
              dict(name="gate", conclusion="failure", started_at="T05", completed_at="T20")]           # excluded
    reds, late = lagging("T10", checks)
    if sorted(c["name"] for c in reds) != ["late", "lint", "tests / fast"]:
        bad.append(f"reds {[c['name'] for c in reds]}")
    if [c["name"] for c in late] != ["tests / fast"]:
        bad.append(f"lagging {[c['name'] for c in late]}")
    if lagging("T10", [dict(name="x", conclusion="failure", started_at="T05", completed_at="T10")])[1]:
        bad.append("a red completed exactly as the list was read was listed: not lagging")
    job = dict(name=PC, run_attempt=1, steps=[dict(name=STEP, completed_at="T10")])
    o = measure([dict(id=1, head_sha="a" * 40)], lambda i: [job, dict(name="other")], lambda sha: checks)
    if (o["lists"], o["reds"], o["lagging"]) != (1, 3, 1):
        bad.append(f"measure {o['lists'], o['reds'], o['lagging']}")
    print(f"selftest: 5 checks, {len(bad)} failed{' ' + str(bad) if bad else ''}")
    return 1 if bad else 0


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
    heads = {}

    def checks_of(sha):
        if sha not in heads:
            heads[sha] = pages(ghapi.get, f"repos/{REPO}/commits/{sha}/check-runs", {"filter": "all"})
        return heads[sha]
    o = measure(runs, lambda i: pages(ghapi.get, f"repos/{REPO}/actions/runs/{i}/jobs", {"filter": "all"}), checks_of)
    print(f"ci.yml pull_request runs created {a.since}..{a.until}: {len(runs)}; red lists read: {o['lists']}; "
          f"heads: {len(heads)}")
    print(f"REDS at those heads (the null control): {o['reds']}; LAGGING when the list was read: {o['lagging']}")
    if a.rows:
        for row in o["rows"]:
            print(*row)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
