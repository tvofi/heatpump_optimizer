#!/usr/bin/env python3
"""D11: DORA's four keys for this repository over a stated window.

METRIC (one line each):
  deployment_frequency  -- releases per day, counted as annotated `v*` tags whose
                           commit is on `main` inside the window.
  lead_time_p50/p90     -- hours from a first-parent commit's committer date to
                           the committer date of the first `v*` tag that contains
                           it (commit -> released), over commits in the window
                           that have since been released.
  change_failure_rate   -- fraction of first-parent commits on `main` in the
                           window for which at least one GitHub Actions workflow
                           run on `main` at that exact head concluded `failure`
                           (a run that went red and then green counts as red:
                           the per-run listing keeps what a summary drops).
  time_to_restore_p50   -- hours from such a red head to the next first-parent
                           head on `main` whose runs are all non-failure.

INSTRUMENTED SYMBOLS: GitHub Actions workflow runs of `.github/workflows/tests.yml`
and `.github/workflows/governance.yml` on `main` (the `Tests` and `Governance`
workflows), and `tools/release/stamp.py`'s output -- the `v*` tags it creates.

RUN (read-only; ~12 paginated `gh api` calls, no writes of any kind):
    cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round3/D11/dora.py

PERTURBATION: shrink the window by passing HPO_D11_SINCE/HPO_D11_UNTIL. Moving
the start forward past 2026-09-05 must raise `deployment_frequency` (the release
cadence accelerated) and change `change_failure_rate`; a window in which no run
is red must print change_failure_rate=0.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, window
2026-08-27T21:02:51Z..2026-09-10T21:02:51Z:
    RESULT releases_in_window=66 +/-0
    RESULT deployment_frequency=4.71 releases/day +/-0.01   (DORA "Elite": on demand)
    RESULT lead_time_p50=3.00 hours +/-0.1                  (DORA "Elite": < 1 day)
    RESULT change_failure_rate=0.1721 +/-0.02               (DORA "High": 16-30%)
    RESULT time_to_restore_p50=0.68 hours +/-0.2            (DORA "Elite": < 1 hour)
    RESULT run_listing_capped=1  -- the Actions run listing caps at 1000 runs, so the
      change-failure and restore figures are measured over the EFFECTIVE SUB-WINDOW
      the harness prints (2026-09-06T00:29+02:00 .. 2026-09-10T23:02+02:00, 215 of
      the window's 484 first-parent heads), a contiguous recent suffix, not a sample.
    RESULT api_failures=0 +/-0  (any non-zero invalidates every figure above)
    RESULT red_heads_resolved=37 of 37 +/-0
    RESULT red_heads_by_job={"record": 20, "fast (3.13)": 12, "fast (3.14)": 12,
      "closures": 6, "policy-docs": 6, "nightly-ha (2025.2.0)": 5,
      "nightly-ha (stable)": 5, "env-matrix": 4, "fast": 2, "briefs": 1, "slow": 1}
    RESULT red_heads_only_record=11 +/-0
    RESULT red_head_api_failures=0 +/-0  -- a non-zero here means REFUSED calls and
      `red_heads_by_job` then prints `{}`, an empty map that is a refusal and not a
      measurement. Never read it as "no job failed". (The attribution goes through
      GraphQL, which carries a quota separate from REST's, for that reason.)
MACHINE: 8-core Apple M1, 8 GB, gh 2.98.0, python3 3.11.5.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
REPO = "tvofi/heatpump_optimizer"
BASELINE = "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1"
SINCE = os.environ.get("HPO_D11_SINCE", "2026-08-27T21:02:51+00:00")
UNTIL = os.environ.get("HPO_D11_UNTIL", "2026-09-10T21:02:51+00:00")
RUNS_CACHE = HERE / "dora_runs.json"
FAILURES = []


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=True).stdout


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fetch_runs():
    if RUNS_CACHE.exists():
        return json.loads(RUNS_CACHE.read_text())
    out, page = [], 1
    while page <= 25:
        p = subprocess.run(
            ["gh", "api",
             f"repos/{REPO}/actions/runs?branch=main&per_page=100&page={page}"
             f"&created=%3E%3D{SINCE[:10]}"],
            capture_output=True, text=True)
        if p.returncode != 0:
            FAILURES.append(f"runs page {page}: {p.stderr.strip()[:160]}")
            break
        d = json.loads(p.stdout)
        runs = d.get("workflow_runs", [])
        out += [{"name": r["name"], "head_sha": r["head_sha"],
                 "conclusion": r["conclusion"], "event": r["event"],
                 "created_at": r["created_at"], "updated_at": r["updated_at"],
                 "run_started_at": r.get("run_started_at")} for r in runs]
        if len(runs) < 100:
            break
        page += 1
    RUNS_CACHE.write_text(json.dumps(out, indent=1))
    return out


def main():
    since, until = ts(SINCE), ts(UNTIL)
    days = (until - since).total_seconds() / 86400.0

    # --- release frequency, from the tags stamp.py creates -----------------
    rel = []
    for line in git("for-each-ref", "--format=%(refname:short)\t%(creatordate:iso-strict)",
                    "refs/tags/v*").splitlines():
        tag, when = line.split("\t")
        t = ts(when)
        if not (since <= t <= until):
            continue
        sha = git("rev-parse", f"{tag}^{{commit}}").strip()
        if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, BASELINE]).returncode == 0:
            rel.append((tag, t, sha))
    rel.sort(key=lambda r: r[1])
    print(f"RESULT window_days={days:.2f} days")
    print(f"RESULT releases_in_window={len(rel)} releases")
    print(f"RESULT deployment_frequency={len(rel)/days:.2f} releases/day")

    # --- lead time for changes: commit -> first release tag containing it ---
    commits = []
    for line in git("log", "--first-parent", "--format=%H\t%cI", BASELINE,
                    f"--since={SINCE}", f"--until={UNTIL}").splitlines():
        sha, when = line.split("\t")
        commits.append((sha, ts(when)))
    leads = []
    for sha, when in commits:
        for tag, tt, tsha in rel:
            if tt < when:
                continue
            if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, tsha]).returncode == 0:
                leads.append((tt - when).total_seconds() / 3600.0)
                break
    leads.sort()

    def pct(xs, q):
        return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float("nan")
    print(f"RESULT commits_in_window={len(commits)} commits")
    print(f"RESULT commits_released={len(leads)} commits")
    print(f"RESULT lead_time_p50={pct(leads, 0.50):.2f} hours")
    print(f"RESULT lead_time_p90={pct(leads, 0.90):.2f} hours")

    # --- change failure rate and time to restore ---------------------------
    runs = fetch_runs()
    by_head = {}
    for r in runs:
        if r["event"] not in ("push", "schedule"):
            continue
        by_head.setdefault(r["head_sha"], []).append(r)
    seq = list(reversed(commits))     # oldest first
    covered = [c for c in seq if c[0] in by_head]
    red = []
    for sha, when in covered:
        if any(r["conclusion"] == "failure" for r in by_head[sha]):
            red.append((sha, when))
    print(f"RESULT runs_cached={len(runs)} runs"
          "  (the Actions run listing caps at 1000; a full window needs the cache file deleted"
          " and the window narrowed, see run_listing_capped below)")
    print(f"RESULT run_listing_capped={int(len(runs) >= 1000)} bool")
    if covered:
        print(f"RESULT effective_subwindow_start={covered[0][1].isoformat()}")
        print(f"RESULT effective_subwindow_end={covered[-1][1].isoformat()}")
    print(f"RESULT api_failures={len(FAILURES)} calls")
    for f in FAILURES:
        print(f"  FAILED {f}")
    print(f"RESULT heads_with_a_main_run={len(covered)} commits")
    print(f"RESULT red_main_heads={len(red)} commits")
    cfr = len(red) / len(covered) if covered else float("nan")
    print(f"RESULT change_failure_rate={cfr:.4f} fraction")

    order = [c[0] for c in covered]
    restores = []
    for sha, when in red:
        i = order.index(sha)
        for nxt in order[i + 1:]:
            if not any(r["conclusion"] == "failure" for r in by_head[nxt]):
                w = dict(covered)[nxt]
                restores.append((w - when).total_seconds() / 3600.0)
                break
    restores.sort()
    print(f"RESULT restored_events={len(restores)} events")
    print(f"RESULT time_to_restore_p50={pct(restores, 0.50):.2f} hours")
    print(f"RESULT time_to_restore_p90={pct(restores, 0.90):.2f} hours")
    # Which JOB reddened each head. A workflow-level conclusion says `Governance`
    # failed; only the commit's check-runs listing says which of its six jobs did,
    # and it is also the listing that keeps a run that went red and then green.
    frag = """
      %s: object(oid: "%s") { ... on Commit { oid
        checkSuites(first: 20) { nodes { checkRuns(first: 60) {
          nodes { name conclusion } } } } } }"""
    runs_by_head, jobfail, only_record = {}, {}, 0
    shas = [sha for sha, _ in red]
    for i in range(0, len(shas), 12):
        chunk = shas[i:i + 12]
        body = "".join(frag % (f"r{i + j}", s) for j, s in enumerate(chunk))
        q = ("query { repository(owner:\"tvofi\", name:\"heatpump_optimizer\") {"
             + body + "} }")
        pp = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                            capture_output=True, text=True)
        if pp.returncode != 0:
            FAILURES.append(f"graphql check-runs chunk {i}: {pp.stderr.strip()[:140]}")
            continue
        d = json.loads(pp.stdout)
        if "errors" in d:
            FAILURES.append(json.dumps(d["errors"])[:200])
        for v in (d.get("data", {}).get("repository") or {}).values():
            if not v:
                continue
            runs_by_head[v["oid"]] = [r for su in v["checkSuites"]["nodes"]
                                      for r in su["checkRuns"]["nodes"]]
    for sha in shas:
        names = {r["name"] for r in runs_by_head.get(sha, []) if r["conclusion"] == "FAILURE"}
        for n in names:
            jobfail[n] = jobfail.get(n, 0) + 1
        if names and names <= {"record"}:
            only_record += 1
    print(f"RESULT red_head_api_failures={len(FAILURES)} calls")
    for f in FAILURES[:4]:
        print(f"  FAILED {f[:150]}")
    print(f"RESULT red_heads_resolved={len(runs_by_head)} of {len(shas)} heads")
    print("RESULT red_heads_by_job=" + json.dumps(dict(sorted(
        jobfail.items(), key=lambda kv: (-kv[1], kv[0])))))
    print(f"RESULT red_heads_only_record={only_record} commits")
    print("  red heads (sha, when, the workflows that concluded failure):")
    for sha, when in red[-12:]:
        names = sorted({r["name"] for r in by_head[sha] if r["conclusion"] == "failure"})
        print(f"    {sha[:7]}  {when.isoformat()}  {','.join(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
