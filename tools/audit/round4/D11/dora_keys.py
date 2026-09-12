#!/usr/bin/env python3
"""D11 / round 4 -- DORA's four keys, measured from `main`'s history and the API.

METRIC, over the window 2026-09-08T00:00:00Z .. 2026-09-12T10:44:12Z (4.45 days,
closed at the baseline commit):

  deployment frequency   releases per day = the count of `vN.N.N` tags whose
                         tagged commit date falls in the window, over the window
                         in days. A release here is a GitHub Release created by
                         `.github/workflows/release.yml` from a version tag.
  lead time for changes  hours from a pull request's merged_at to the committer
                         date of the FIRST `vN.N.N` tag whose history contains
                         its merge commit. Median and p90.
  change failure rate    distinct `main` head SHAs for which the LATEST
                         push-event workflow run of some workflow concluded
                         `failure`, over all distinct `main` head SHAs with a
                         push-event run in the window. Reported three ways --
                         any workflow, Tests only, Governance only -- because a
                         single figure here hides which loop is failing.
  time to restore        per workflow, hours from the first failing push-event
                         run to the `updated_at` of the next succeeding one.
                         Median and max.

WHY THE WINDOW IS THAT WINDOW. `actions/runs` caps at 1000 results and this
repository produced 1000 push-event runs on `main` in five days, so anything
older is truncated and a longer window would silently under-count reds. The
window starts one day inside the truncation boundary.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/dora_keys.py

EXPECTED at baseline 7dd68dd (tolerance: exact; counts and date arithmetic):
  releases_per_day=1.12  lead_time_median_h=7.41  cfr_any=0.477
  cfr_tests=0.117  cfr_governance=0.441  ttr_median_h_Governance=0.61
  api_failures=0
MACHINE: any; network-bound, no CPU claim.

PERTURBATION. Set D11_WINDOW_START=2026-09-11T00:00:00Z (the busiest day, 86
merges) and `cfr_governance` must move; if it does not, the harness is reading
a constant rather than the run history.
"""

import collections
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

W0 = os.environ.get("D11_WINDOW_START", "2026-09-08T00:00:00Z")
W1 = os.environ.get("D11_WINDOW_END", "2026-09-12T10:44:12Z")


def t(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def main():
    pages = L.api(
        f"repos/{L.REPO}/actions/runs?branch=main&event=push&per_page=100",
        paginate=True,
    )
    runs = [r for p in (pages or []) for r in p.get("workflow_runs", [])]
    span = (min(r["created_at"] for r in runs), max(r["created_at"] for r in runs))
    print(f"push-event runs on main returned: {len(runs)}  span {span[0]} .. {span[1]}")
    if len(runs) >= 1000:
        print("NOTE: the listing is at the API's 1000-result cap; the window starts "
              "inside it so nothing older is counted.")
    runs = [r for r in runs if W0 <= r["created_at"] <= W1]

    heads = collections.OrderedDict()
    for r in sorted(runs, key=lambda x: x["created_at"]):
        heads.setdefault(r["head_sha"], []).append(r)

    failed_by_wf = collections.Counter()
    any_failed = 0
    for sha, rs in heads.items():
        latest = {}
        for r in sorted(rs, key=lambda x: x["created_at"]):
            latest[r["name"]] = r
        bad = [n for n, r in latest.items() if r["conclusion"] == "failure"]
        for n in bad:
            failed_by_wf[n] += 1
        if bad:
            any_failed += 1
    nheads = len(heads) or 1
    print(f"distinct main heads with a push-event run in window: {len(heads)}")
    print(f"heads whose latest run of a workflow failed, by workflow: {dict(failed_by_wf)}")

    # which JOB inside Governance -- sampled, because jobs need one call per run
    # The LAST GOVERNANCE run at each head whose latest Governance run failed.
    # Taking `rs[-1]` instead picks whatever workflow ran last at that head and
    # reports Tests's job names as Governance's -- it did, on the first draft.
    govfail = []
    for sha, rs in heads.items():
        g = [r for r in sorted(rs, key=lambda x: x["created_at"]) if r["name"] == "Governance"]
        if g and g[-1]["conclusion"] == "failure":
            govfail.append(g[-1])
    jobc = collections.Counter()
    sampled = 0
    for r in govfail[: int(os.environ.get("D11_JOB_SAMPLE", "60"))]:
        d = L.api(f"repos/{L.REPO}/actions/runs/{r['id']}/jobs")
        if not d:
            continue
        sampled += 1
        for j in d.get("jobs", []):
            if j["conclusion"] == "failure":
                jobc[j["name"]] += 1
    print(f"Governance failures, failing job (sample of {sampled} of {len(govfail)}): {dict(jobc)}")

    # time to restore
    ttr = {}
    for wf in sorted({r["name"] for r in runs}):
        seq = [r for r in sorted(runs, key=lambda x: x["created_at"]) if r["name"] == wf]
        durs = []
        open_red = None
        for r in seq:
            if r["conclusion"] == "failure" and open_red is None:
                open_red = r
            elif r["conclusion"] == "success" and open_red is not None:
                durs.append((t(r["updated_at"]) - t(open_red["created_at"])).total_seconds() / 3600)
                open_red = None
        durs.sort()
        ttr[wf] = durs
        if durs:
            print(f"  {wf:<11} red episodes={len(durs)} median={durs[len(durs)//2]:.2f} h "
                  f"max={durs[-1]:.2f} h still_open={open_red is not None}")
        else:
            print(f"  {wf:<11} red episodes=0 still_open={open_red is not None}")

    # releases and lead time
    root = L.git("rev-parse", "--show-toplevel").strip()
    tags = [
        x for x in L.git("tag", "--list", "v*", root=root).split()
        if re.fullmatch(r"v\d+\.\d+\.\d+", x)
    ]
    tags.sort(key=lambda x: [int(v) for v in x[1:].split(".")])
    tagtime = {x: L.git("log", "-1", "--format=%cI", x, root=root).strip() for x in tags}
    inwin = [x for x in tags if W0 <= L.utc(tagtime[x]) <= W1]
    days = (t(W1) - t(W0)).total_seconds() / 86400
    print(f"version tags in window: {len(inwin)} {inwin}")

    tagcommits = {x: set(L.git("rev-list", x, root=root).split()) for x in tags}
    prs = L.merged_prs()
    lead = []
    unreleased = 0
    for n, p in prs.items():
        mc = (p["mergeCommit"] or {}).get("oid")
        if not mc or not (W0 <= p["mergedAt"] <= W1):
            continue
        first = next((x for x in tags if mc in tagcommits[x]), None)
        if first is None:
            unreleased += 1
            continue
        lead.append((t(tagtime[first]) - t(p["mergedAt"])).total_seconds() / 3600)
    lead.sort()

    print()
    L.result("window_start", W0)
    L.result("window_end", W1)
    L.result("window_days", round(days, 2), "d")
    L.result("releases_in_window", len(inwin))
    L.result("releases_per_day", round(len(inwin) / days, 2), "releases/day")
    if lead:
        L.result("lead_time_median_h", round(lead[len(lead) // 2], 2), "h")
        L.result("lead_time_p90_h", round(lead[int(0.9 * len(lead))], 2), "h")
        L.result("lead_time_n", len(lead))
    L.result("unreleased_merges_at_baseline", unreleased)
    L.result("main_heads", len(heads))
    L.result("cfr_any", round(any_failed / nheads, 3))
    L.result("cfr_tests", round(failed_by_wf.get("Tests", 0) / nheads, 3))
    L.result("cfr_governance", round(failed_by_wf.get("Governance", 0) / nheads, 3))
    for wf, durs in ttr.items():
        if durs:
            L.result(f"ttr_median_h_{wf}", round(durs[len(durs) // 2], 2), "h")
            L.result(f"ttr_max_h_{wf}", round(durs[-1], 2), "h")
    L.result("governance_failing_job_record", jobc.get("record", 0))
    L.result("governance_failing_job_sample", sampled)
    L.footer()


if __name__ == "__main__":
    main()
