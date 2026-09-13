#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-05 (round 4, verifier seat 1).

METRIC (my own definition; same CLOSED window as the finder
2026-09-08T00:00:00Z..2026-09-12T10:44:12Z, but computed by my own code over a
FRESH fetch, and with a CENSUS of failing jobs rather than the finder's sample
of 60):
  main_heads              -- distinct main head SHAs with >=1 push-event
                             workflow run in the window.
  heads_governance_red    -- heads whose LATEST Governance push run failed.
  heads_record_red        -- heads whose latest Governance push run failed IN A
                             JOB NAMED `record` (census: every failing
                             Governance run's jobs enumerated, not sampled).
  cfr_governance          -- heads_governance_red / main_heads.
  cfr_record              -- heads_record_red / main_heads.
  record_excludes_pr      -- static: the `record` job's `if:` in governance.yml
                             excludes pull_request events.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/d11_own_D11-05.py

EXPECTED (tolerance: exact; the window is closed):
  main_heads=222 cfr_governance=0.441 cfr_record~=0.40 (finder: 58 of 60
  sampled failing jobs were `record`) record_excludes_pr=1
MACHINE: verifier seat 1 worktree audit-r4-verify-D11-1, 2026-09-12;
network-bound, no timing claim.

PERTURBATION. Shift the window start to 2026-09-11 (busiest day) and
cfr_record must move; a constant would mean the harness reads cache, not
history.
"""

import collections
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = "tvofi/heatpump_optimizer"
W0 = os.environ.get("D11_OWN_W0", "2026-09-08T00:00:00Z")
W1 = "2026-09-12T10:44:12Z"
CACHE = os.path.join(tempfile.gettempdir(), "d11-own-verify1-cache")
FAILS = []


def gh(path):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, path.replace("/", "_").replace("?", "~").replace("&", "~") + ".json")
    if os.path.exists(f) and os.path.getsize(f):
        return json.loads(open(f).read())
    p = subprocess.run(["gh", "api", "--paginate", "--slurp", path],
                       capture_output=True, text=True)
    if p.returncode != 0:
        FAILS.append(path)
        return None
    open(f, "w").write(p.stdout)
    return json.loads(p.stdout)


def main():
    pages = gh(f"repos/{REPO}/actions/runs?branch=main&event=push&per_page=100")
    runs = [r for p in (pages or []) for r in p.get("workflow_runs", [])]
    print(f"push-event runs fetched: {len(runs)}")
    runs = [r for r in runs if W0 <= r["created_at"] <= W1]
    heads = collections.defaultdict(list)
    for r in sorted(runs, key=lambda x: x["created_at"]):
        heads[r["head_sha"]].append(r)

    gov_red, tests_red, any_red = 0, 0, 0
    gov_red_runs = []
    for sha, rs in heads.items():
        latest = {}
        for r in rs:
            latest[r["name"]] = r
        bad = [n for n, r in latest.items() if r["conclusion"] == "failure"]
        if bad:
            any_red += 1
        if "Governance" in bad:
            gov_red += 1
            gov_red_runs.append(latest["Governance"])
        if "Tests" in bad:
            tests_red += 1
    print(f"main heads in window: {len(heads)}; any-red {any_red}; "
          f"Governance-red {gov_red}; Tests-red {tests_red}")

    # CENSUS of failing jobs over every red Governance run (finder sampled 60)
    jobc = collections.Counter()
    record_red_heads = set()
    censused = 0
    for r in gov_red_runs:
        d = gh(f"repos/{REPO}/actions/runs/{r['id']}/jobs")
        if not d:
            continue
        censused += 1
        pages_jobs = d if isinstance(d, list) else [d]
        jobs = [j for p in pages_jobs if isinstance(p, dict) for j in p.get("jobs", [])]
        names = {j["name"] for j in jobs if j["conclusion"] == "failure"}
        jobc.update(names)
        if "record" in names:
            record_red_heads.add(r["head_sha"])
    print(f"Governance red runs censused: {censused}/{len(gov_red_runs)}; "
          f"failing-job census: {dict(jobc)}")

    gov = open(".github/workflows/governance.yml", encoding="utf-8").read()
    m = re.search(r"\n  record:\n(.*?)(?=\n  \w)", gov, re.S)
    cond = re.search(r"if: (.+)", m.group(1)).group(1) if m and re.search(r"if: (.+)", m.group(1)) else ""
    excludes = "pull_request" in cond and "!=" in cond
    print(f"record job if: {cond.strip()!r} -> excludes pull_request: {excludes}")

    n = len(heads) or 1
    print()
    print(f"RESULT main_heads={len(heads)}")
    print(f"RESULT heads_any_red={any_red}")
    print(f"RESULT heads_governance_red={gov_red}")
    print(f"RESULT heads_tests_red={tests_red}")
    print(f"RESULT cfr_any={round(any_red / n, 3)}")
    print(f"RESULT cfr_governance={round(gov_red / n, 3)}")
    print(f"RESULT cfr_tests={round(tests_red / n, 3)}")
    print(f"RESULT census_governance_red_runs={censused}")
    print(f"RESULT failing_job_record={jobc.get('record', 0)}")
    print(f"RESULT failing_job_other={dict((k, v) for k, v in jobc.items() if k != 'record')}")
    print(f"RESULT cfr_record={round(len(record_red_heads) / n, 3)}")
    print(f"RESULT record_excludes_pr={int(excludes)}")
    print(f"RESULT api_failures={len(FAILS)}")


if __name__ == "__main__":
    main()
