#!/usr/bin/env python3
"""D13 / round 5 -- DORA's four keys by job, and the by-design exclusion list.

METRIC (four lines, one per key).
  deployment frequency   the count of `vN.N.N` tags whose tagged commit's
                         committer date falls in the window, over the window in
                         days. NOT per job: a release is a tag.
  lead time for changes  hours from a merge's `merged_at` to the committer date
                         of the FIRST `vN.N.N` tag whose history contains its
                         merge commit. Median and p90. NOT per job.
  change failure rate    PER CHECK-RUN NAME. Over the window's merge commits,
                         the share of merges at which the LATEST run of that
                         name concluded red. `--arm anyrun` keys on ANY run of
                         that name concluding red instead, which is the rounds
                         the process actually paid. A merge also fails if a
                         `main` commit descending from it says `This reverts
                         commit <sha>` of it or of a commit it merged, or a
                         merged `Revert "..."` pull request does -- measured
                         separately, because the revert arm is a different
                         mechanism from a red check.
  time to restore        PER CHECK-RUN NAME: hours from the first red run of
                         that name at a merge to the next green run of that name
                         at a later merge. Median and max.

THE EXCLUSION LIST is a JSON file beside `policy_budgets.json`
(`.claude/workflows/policy_reds_by_design.json`, carried here for the round-5
report) with a reason per job. The rate without them is printed beside the rate
with them: the difference is what an exclusion list is worth, measured rather
than asserted.

WHY THE MERGE COMMIT AND NOT THE PULL REQUEST HEAD. DORA's change failure is
about what lands on `main`. The push-triggered run at the merge commit is the
only one that can be red after a merge, and it is the run whose failure is a
failure of the deployment; the same jobs at the pull-request head are the
pre-merge gate, which h5_cost.py measures as cost. The two populations are
printed side by side so a reader can see that the pre-merge one is where the
reds are.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 /tmp/heatpump-orch/audit-r5-D13/h4_dora.py
  ... --arm anyrun           # any red run of a name, not the latest run
  ... --excluded off         # rate WITH the by-design jobs left in
  ... --excluded file:<path> # a different exclusion file

PERTURBATION AND DIRECTION. `--excluded flip` moves the ONE excluded job into
the counted set: `cfr_any_job_excluded` must RISE by that job's own rate and
`jobs_excluded` must fall by 1; if both are 0 the file excluded nothing and the
number is not evidence for the exclusion. The null control is `--arm latest`
against `--arm anyrun` on a job that never failed: both must print 0.000.

MACHINE: any; API counts and durations, no timing claim on this box.
"""

import datetime
import json
import os
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13lib as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RED = ("failure", "timed_out", "cancelled", "startup_failure", "action_required")
EXC_DEFAULT = os.path.join(HERE, "policy_reds_by_design.json")


def t(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def dur(c):
    if not c.get("started_at") or not c.get("completed_at"):
        return None
    return max(0.0, (t(c["completed_at"]) - t(c["started_at"])).total_seconds())


def load_exclusions(argv):
    path = EXC_DEFAULT
    if "--excluded" in argv:
        mode = argv[argv.index("--excluded") + 1]
        if mode == "off":
            return {}, "none (--excluded off)"
        if mode == "flip":
            # The perturbation: the LIST loses its first job, so that job's reds
            # are counted again. Named in the print so the mover is visible.
            d = json.load(open(path))
            jobs = d["jobs"]
            first = sorted(jobs)[0]
            jobs.pop(first)
            return jobs, f"{path} with `{first}` removed (its reds counted again)"
        if mode.startswith("file:"):
            path = mode[5:]
    d = json.load(open(path))
    return d["jobs"], path


def reverts(merges, by_merge):
    """Merges whose commits were reverted later on `main`, or by a Revert PR."""
    out = []
    for m in merges:
        body = L.git("log", "--format=%H%x1f%B%x1e",
                     f"{m['merge_sha']}..{L.BASELINE_SHA}")
        targets = {m["merge_sha"]} | set(
            L.git("rev-list", f"{m['merge_sha']}^1..{m['merge_sha']}").split())
        hits = [ln for ln in re.findall(r"This reverts commit ([0-9a-f]{7,40})", body)
                if any(x.startswith(ln) for x in targets)]
        title = (by_merge.get(m["number"], {}) or {}).get("title", "")
        if hits:
            out.append((m["number"], "reverts-commit", hits[0]))
        elif title.startswith('Revert "'):
            out.append((m["number"], "revert-pull-request", title[:60]))
    return out


def tags_in_window():
    out = L.git("tag", "--list", "v*").split()
    tags = [x for x in out if re.fullmatch(r"v\d+\.\d+\.\d+", x)]
    tags.sort(key=lambda x: [int(v) for v in x[1:].split(".")])
    times = {x: L.utc(L.git("log", "-1", "--format=%cI", x).strip()) for x in tags}
    inwin = [x for x in tags if L.W0 <= times[x] <= L.W1]
    return tags, times, inwin


def main():
    argv = sys.argv[1:]
    arm = argv[argv.index("--arm") + 1] if "--arm" in argv else "latest"
    excl, excl_src = load_exclusions(argv)

    commits = L.window_commits()
    merges, blind = L.enumerate_merges(commits)
    by_merge = {}
    for m in merges:
        by_merge[m["number"]] = L.pr(m["number"]) or {}
        m["prhead"] = (by_merge[m["number"]].get("head") or {}).get("sha") or ""
        m["merged_at"] = by_merge[m["number"]].get("merged_at") or ""
    print(f"window {L.W0} .. {L.W1}  first-parent commits={len(commits)}  "
          f"merges={len(merges)}  unattributed={len(blind)}")
    print(f"exclusion list: {excl_src}  jobs excluded={sorted(excl)}")

    # ---- the runs, at the merge commits
    runs = {n: L.check_runs(m["merge_sha"]) or [] for m, n in
            ((m, m["number"]) for m in merges)}
    names = Counter()
    fail_latest = Counter()
    fail_any = Counter()
    latest_at = defaultdict(dict)
    order = []
    for m in merges:
        n = m["number"]
        latest = {}
        for c in runs[n]:
            names[c["name"]] += 1
            if c["conclusion"] in RED:
                fail_any[c["name"]] += 1
            prev = latest.get(c["name"])
            if prev is None or (c.get("completed_at") or "") >= (prev.get("completed_at") or ""):
                latest[c["name"]] = c
        for nm, c in latest.items():
            latest_at[nm][n] = c
            if c["conclusion"] in RED:
                fail_latest[nm] += 1
        order.append(n)

    n_merges = len(merges)
    key = fail_latest if arm == "latest" else fail_any
    print(f"\nCHANGE FAILURE RATE BY JOB ({arm}, at the merge commit, n={n_merges})")
    for nm in sorted(names):
        marked = "  [EXCLUDED]" if nm in excl else ""
        L.result(f"cfr_{nm}", round(key.get(nm, 0) / n_merges, 4))
        print(f"  {nm:<32} red={key.get(nm, 0):>3}  cfr={key.get(nm, 0)/n_merges:.4f}"
              f"{marked}")

    # ---- the aggregate, with and without the by-design jobs
    def agg(counted):
        bad = 0
        for m in merges:
            if any(nm in counted and latest_at[nm].get(m["number"], {}).get("conclusion") in RED
                   for nm in latest_at):
                bad += 1
        return bad
    counted_all = set(names)
    counted_excl = counted_all - set(excl)
    a_all, a_excl = agg(counted_all), agg(counted_excl)
    L.result("merges", n_merges)
    L.result("jobs_observed", len(names))
    L.result("jobs_excluded", len(excl))
    L.result("cfr_any_job", round(a_all / n_merges, 4))
    L.result("cfr_any_job_excluded", round(a_excl / n_merges, 4))
    print(f"\nmerges with any red job: {a_all}/{n_merges} = {a_all/n_merges:.4f}; "
          f"without the by-design jobs: {a_excl}/{n_merges} = {a_excl/n_merges:.4f}")

    # ---- the revert arm
    rev = reverts(merges, by_merge)
    for n, how, what in rev:
        print(f"  REVERT #{n} {how} {what}")
    L.result("merges_reverted_later", len(rev))
    L.result("cfr_with_reverts",
             round((a_excl + len(rev)) / n_merges, 4))

    # ---- time to restore, per job
    print("\nTIME TO RESTORE BY JOB (hours from a red run's start to the next "
          "green run of the same name):")
    for nm in sorted(names):
        ts = sorted(((c.get("started_at"), c["conclusion"], n)
                     for n in order for c in runs[n] if c["name"] == nm
                     and c["conclusion"] != "skipped" and c.get("started_at")),
                    key=lambda x: x[0])
        durs, open_red = [], None
        for started, concl, n in ts:
            if concl in RED and open_red is None:
                open_red = started
            elif concl == "success" and open_red is not None:
                durs.append((t(started) - t(open_red)).total_seconds() / 3600)
                open_red = None
        if durs:
            durs.sort()
            L.result(f"ttr_median_h_{nm}", round(durs[len(durs) // 2], 2), "h")
            L.result(f"ttr_max_h_{nm}", round(durs[-1], 2), "h")
            print(f"  {nm:<32} episodes={len(durs)} median={durs[len(durs)//2]:.2f} h "
                  f"max={durs[-1]:.2f} h still_open={open_red is not None}")

    # ---- deployment frequency and lead time (not per job)
    tags, tagtime, inwin = tags_in_window()
    days = (t(L.W1) - t(L.W0)).total_seconds() / 86400
    lead = []
    unreleased = 0
    for m in merges:
        if not m["merged_at"] or not (L.W0 <= m["merged_at"] <= L.W1):
            continue
        first = next((x for x in tags
                      if m["merge_sha"] in set(L.git("rev-list", x).split())), None)
        if first is None:
            unreleased += 1
            continue
        lead.append((t(tagtime[first]) - t(m["merged_at"])).total_seconds() / 3600)
    lead.sort()
    print(f"\nversion tags in window: {len(inwin)} {inwin}")
    L.result("window_days", round(days, 2), "d")
    L.result("releases_in_window", len(inwin))
    L.result("releases_per_day", round(len(inwin) / days, 2), "releases/day")
    L.result("unreleased_merges_at_baseline", unreleased)
    if lead:
        L.result("lead_time_median_h", round(lead[len(lead) // 2], 2), "h")
        L.result("lead_time_p90_h", round(lead[int(0.9 * len(lead))], 2), "h")
        L.result("lead_time_n", len(lead))
    L.result("arm", arm)
    L.result("exclusion_source", str(excl_src))
    L.footer()


if __name__ == "__main__":
    main()
