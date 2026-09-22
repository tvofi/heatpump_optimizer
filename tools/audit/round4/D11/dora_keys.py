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

THE D13 RE-TAKE: THE CHANGE-FAILURE RATE IS REPORTED AT BOTH KEYINGS. The
D13 brief (#4) re-takes the rate PER CHECK-RUN NAME, "then without the jobs on
an exclusion list of by-design reds" (`.claude/workflows/cfr_exclusions.json`).
A merge is judged at two surfaces and they are not the same population: a check
that is `if: github.event_name != 'pull_request'` is SKIPPED at the pull-request
head and RUNS at the merge commit, and vice versa. D13-03 (#1407) established
that the exclusion list is keyed at the SURFACE THAT CANNOT GATE A MERGE --
`record` fails at 58 of the window's 67 merge commits but is skipped at all 67
pull-request heads -- so dropping it moves the merge-keyed rate and leaves the
head-keyed rate, the surface a merge is actually gated on, exactly where it was.
Reporting one number hides that; the block below prints both, and neither the
list nor its keying changes here. `cfr_merge_keyed` is the excluded rate at the
merge commit, `cfr_head_keyed` the excluded rate at the pull-request head, and
`cfr_merge_unexcluded` / `cfr_head_unexcluded` the same two before the
exclusion, so the delta the exclusion buys is visible on each keying.

   D13 window `v6.6.0..e336cc2c` (67 merges): cfr_merge_keyed=0.09
   cfr_head_keyed=0.134 cfr_merge_unexcluded=0.925 cfr_head_unexcluded=0.134.
   The head keying does not move because neither `nightly-status` (7 of 67
   heads) nor `delivery-status` (2 of 67) is excluded, and must not be.

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
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

W0 = os.environ.get("D11_WINDOW_START", "2026-09-08T00:00:00Z")
W1 = os.environ.get("D11_WINDOW_END", "2026-09-12T10:44:12Z")

# The D13 re-take's window and its registered exclusion artifact. The window is
# pinned to the finding's baseline (D13-03 measured at `e336cc2c`, the round-6
# baseline) the way every audit instrument pins its baseline: the number is a
# statement about the repository at a fixed commit, so a re-run next week
# reproduces it rather than tracking a moving `main`. Override either with
# D13_SINCE / D13_HEAD to re-take at a later head.
D13_SINCE = os.environ.get("D13_SINCE", "v6.6.0")
D13_HEAD = os.environ.get(
    "D13_HEAD", "e336cc2c530882a142ef298de6420706d96a6300")
CFR_EXCLUSIONS = ".claude/workflows/cfr_exclusions.json"


def latest_by_name(runs):
    """{name: run} keeping the LATEST run (by started_at) per check-run name."""
    out = {}
    for r in runs:
        n = r["name"]
        if n not in out or (r.get("started_at") or "") > (
                out[n].get("started_at") or ""):
            out[n] = r
    return out


def load_exclusions(root=None):
    """The `excluded_jobs` map, FAILING CLOSED when the artifact is unreadable.

    A rate reported "minus the by-design reds" must not silently exclude
    nothing when the list it names is missing: that would publish the
    un-excluded rate under the excluded rate's name. A missing, malformed or
    empty artifact raises rather than degrading to `exclude nobody` (the same
    fail-closed read `.claude/workflows/cfr_exclusions.json`'s owning
    instrument, tools/audit/round5/D13/seat-a/dora_cfr.py, performs)."""
    base = root if root is not None else L.git(
        "rev-parse", "--show-toplevel").strip()
    with open(os.path.join(base, CFR_EXCLUSIONS)) as fh:
        payload = json.load(fh)
    excl = payload.get("excluded_jobs")
    if not isinstance(excl, dict) or not excl:
        raise SystemExit(
            f"{os.path.join(base, CFR_EXCLUSIONS)}: no `excluded_jobs` map")
    return excl


def cfr_keyings(merge_fail, head_fail, excluded, n):
    """The change-failure rate at BOTH keyings, and both before the exclusion.

    `merge_fail` / `head_fail` map a pull-request number to the set of
    check-run names whose LATEST run at, respectively, its merge commit and
    its pull-request head concluded `failure`. Both are reported because
    `.claude/workflows/cfr_exclusions.json` narrows ONE of them: the merge
    keying is where the list acts, and the head keying is the surface the
    merge is actually gated on, so a reader can see the narrowing move one
    number and leave the other where it was.

    Returns {merge_keyed, head_keyed, merge_unexcluded, head_unexcluded}."""
    def rate(m, drop):
        return round(
            sum(1 for names in m.values() if names - drop) / n, 3) if n else 0.0
    return {
        "merge_keyed": rate(merge_fail, excluded),
        "head_keyed": rate(head_fail, excluded),
        "merge_unexcluded": rate(merge_fail, set()),
        "head_unexcluded": rate(head_fail, set()),
    }


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

    # ---- D13 re-take: change failure PER CHECK-RUN NAME, both keyings -------
    # See the header. The exclusion artifact is READ (fail-closed), never
    # edited: an excluded name is a narrowing of the metric and this block
    # reports what the narrowing does at each surface rather than widening it.
    root = L.git("rev-parse", "--show-toplevel").strip()
    excl = load_exclusions(root=root)
    cut = set(L.git("log", "--first-parent", "--format=%H",
                    f"{D13_SINCE}..{D13_HEAD}", root=root).split())
    merge_fail, head_fail = {}, {}
    for num, p in L.merged_prs().items():
        mc = (p.get("mergeCommit") or {}).get("oid")
        if mc not in cut:
            continue
        head = p.get("headRefOid")
        merge_fail[num] = {
            r["name"] for r in latest_by_name(L.check_runs(mc) or []).values()
            if r.get("conclusion") == "failure"}
        head_fail[num] = {
            r["name"] for r in latest_by_name(
                L.check_runs(head) or []).values()
            if r.get("conclusion") == "failure"} if head else set()
    n13 = len(merge_fail)
    merge_names = collections.Counter(
        name for names in merge_fail.values() for name in names)
    head_names = collections.Counter(
        name for names in head_fail.values() for name in names)
    print(f"\nD13 window {D13_SINCE}..{D13_HEAD[:10]}: {n13} window merges; "
          f"exclusion list {sorted(excl)}")
    print(f"  failing AT THE MERGE COMMIT: {dict(merge_names)}")
    print(f"  failing AT THE PR HEAD:      {dict(head_names)}")
    L.result("d13_window_merges", n13)
    L.result("d13_window", f"{D13_SINCE}..{D13_HEAD[:10]}")
    L.result("cfr_exclusions", json.dumps(sorted(excl)))
    for key, value in cfr_keyings(
            merge_fail, head_fail, set(excl), n13).items():
        L.result(f"cfr_{key}", value)
    L.footer()


if __name__ == "__main__":
    main()
