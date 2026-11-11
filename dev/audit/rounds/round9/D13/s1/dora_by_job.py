#!/usr/bin/env python3
"""D13 / round 9 / seat s1 -- D13.M4: DORA's four keys, by job.

METRICS (window v6.6.0..1936d5ca, merges = the API-mode population of
yield_rounds.mjs; count key is the PR number set):
  cfr[name]@merge / @head  share of window merges whose LATEST check run named
      `name` (full check-run name, matrix leg included) concluded `failure`,
      at the merge commit / at the PR head. Keyed through the production
      tools/audit/round4/D11/dora_keys.py:latest_by_name and cfr_by_name.
  cfr_merge_keyed / cfr_head_keyed  dora_keys.py:cfr_keyings with the
      .claude/workflows/cfr_exclusions.json list (dora_keys.py:load_exclusions).
  cfr_with_reverts  the brief's full rule: a merge ALSO fails if a commit that
      DESCENDS from it (in <merge>..HEAD, any parent) says `This reverts commit
      <sha>` of the merge or of a commit it merged (<merge>^1..<merge>), or a
      merged `Revert "..."` pull request does.
  merge_surface_only_failures = merges failing a non-excluded name at the
      merge commit whose PR head did NOT fail that name; _batched_10min = those
      merged <=600 s after another window merge (control: all merges so batched).
  deploy_per_day = vX.Y.Z tags dated in the window / window days;
  lead_time = merged_at -> committer date of the first tag containing it;
  ttr[name] = hours from the first merge commit where `name` fails to the
      completion of its next succeeding run at a later merge commit.
COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D13/s1/dora_by_job.py
PERTURBATION: D13_ADD_EXCLUDE=<check-run name> adds one name to the exclusion
  set in memory; cfr_merge_keyed must fall by exactly RESULT
  sole_failure_count_<name> / merges (merges failing on that name alone).
EXPECTED at 1936d5ca: exact (closed window, snapshotted). MACHINE: any.
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import collections  # noqa: E402
import datetime  # noqa: E402
import re  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "round4", "D11"))
import r9lib as L  # noqa: E402
import dora_keys as DK  # noqa: E402  production instrument under test


def t(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def population(snap):
    seen, out = set(), []
    for c in snap["commits"]:
        if not c.get("pulls"):
            continue
        n = str(c["pulls"][0]["number"])
        if n in seen:
            continue
        seen.add(n)
        out.append((n, c))
    return out


def failing(runs):
    return {r["name"] for r in DK.latest_by_name(runs or []).values()
            if r.get("conclusion") == "failure"}


def revert_hits(merges):
    """{pr: [reverting sha]} by the brief's descendant rule, from git."""
    msgs = L.git("log", "--format=%H%x00%B%x01", f"{L.WINDOW_SINCE}..{L.WINDOW_HEAD}")
    reverts = []
    for rec in msgs.split("\x01"):
        rec = rec.strip()
        if not rec:
            continue
        sha, body = rec.split("\x00", 1)
        for m in re.finditer(r"This reverts commit ([0-9a-f]{7,40})", body):
            reverts.append((sha, m.group(1)))
    hits = collections.defaultdict(list)
    for pr, c in merges:
        m = c["sha"]
        merged = set(L.git("rev-list", f"{m}^1..{m}").split())
        desc = set(L.git("rev-list", "--ancestry-path", f"{m}..{L.WINDOW_HEAD}").split())
        for rsha, target in reverts:
            if rsha in desc and any(x.startswith(target) for x in merged):
                hits[pr].append(rsha[:10])
    return hits, reverts


def main():
    snap = L.load_snapshot()
    merges = population(snap)
    n = len(merges)
    excl = set(DK.load_exclusions(root=os.getcwd()))
    add = os.environ.get("D13_ADD_EXCLUDE")
    if add:
        excl.add(add)
    merge_fail, head_fail = {}, {}
    missing = 0
    for pr, c in merges:
        p = snap["prs"].get(pr) or {}
        if c.get("runs") is None or p.get("runs_head") is None:
            missing += 1
        merge_fail[pr] = failing(c.get("runs"))
        head_fail[pr] = failing(p.get("runs_head"))
    keyed = DK.cfr_keyings(merge_fail, head_fail, excl, n)
    by_name = DK.cfr_by_name(merge_fail, head_fail, n)
    L.result("window", f"{L.WINDOW_SINCE}..{L.WINDOW_HEAD[:10]}")
    L.result("merges", n)
    L.result("exclusions", ",".join(sorted(excl)))
    for k, v in keyed.items():
        L.result(f"cfr_{k}", v)
    for name, (mr, hr) in sorted(by_name.items(), key=lambda x: -x[1][0]):
        mc = sum(1 for s in merge_fail.values() if name in s)
        hc = sum(1 for s in head_fail.values() if name in s)
        sole = sum(1 for s in merge_fail.values() if s - (excl - {name}) == {name})
        print(f"  name {name!r}: merge {mc}/{n}={mr}  head {hc}/{n}={hr}  sole_at_merge={sole}")
        L.result(f"sole_failure_count_{name.replace(' ', '_')}", sole)
    hits, reverts = revert_hits(merges)
    rev_prs = [pr for pr, _ in merges
               if (snap["prs"].get(pr) or {}).get("title", "").startswith('Revert "')]
    L.result("revert_messages_in_window", len(reverts))
    L.result("merges_reverted_by_descendant", len(hits))
    L.result("merged_revert_prs", len(rev_prs))
    for pr, shas in hits.items():
        print(f"  reverted: #{pr} by {shas}")
    fail_merge_ex = {pr for pr, s in merge_fail.items() if s - excl}
    fail_head_ex = {pr for pr, s in head_fail.items() if s - excl}
    L.result("cfr_merge_keyed_with_reverts",
             round(len(fail_merge_ex | set(hits)) / n, 3) if n else 0)
    L.result("cfr_head_keyed_with_reverts",
             round(len(fail_head_ex | set(hits)) / n, 3) if n else 0)
    # deployment frequency + lead time
    tags = [x for x in L.git("tag", "--list", "v*").split()
            if re.fullmatch(r"v\d+\.\d+\.\d+", x)]
    tags.sort(key=lambda x: [int(v) for v in x[1:].split(".")])
    ttime = {x: L.git("log", "-1", "--format=%cI", x).strip() for x in tags}
    w0 = t(L.git("log", "-1", "--format=%cI", L.WINDOW_SINCE).strip())
    w1 = t(L.git("log", "-1", "--format=%cI", L.WINDOW_HEAD).strip())
    days = (w1 - w0).total_seconds() / 86400
    inwin = [x for x in tags if w0 < t(ttime[x]) <= w1]
    L.result("window_days", round(days, 2), "d")
    L.result("deploys_in_window", len(inwin))
    L.result("deploys_per_day", round(len(inwin) / days, 2), "releases/day")
    contains = {x: set(L.git("rev-list", x).split()) for x in inwin}
    lead = []
    for pr, c in merges:
        first = next((x for x in inwin if c["sha"] in contains[x]), None)
        ma = (snap["prs"].get(pr) or {}).get("merged_at")
        if first and ma:
            lead.append((t(ttime[first]) - t(ma)).total_seconds() / 3600)
    lead.sort()
    if lead:
        L.result("lead_time_median_h", round(statistics.median(lead), 2), "h")
        L.result("lead_time_p90_h", round(lead[int(0.9 * (len(lead) - 1))], 2), "h")
    # time to restore per name, over merge commits in order
    order = sorted(merges, key=lambda x: x[1]["date"])
    ttr = collections.defaultdict(list)
    for name in by_name:
        red = None
        for pr, c in order:
            latest = DK.latest_by_name(c.get("runs") or []).get(name)
            if not latest:
                continue
            if latest.get("conclusion") == "failure" and red is None:
                red = latest.get("started_at") or c["date"]
            elif latest.get("conclusion") == "success" and red is not None:
                ttr[name].append((t(latest["completed_at"]) - t(red)).total_seconds() / 3600)
                red = None
        if ttr[name]:
            print(f"  ttr {name!r}: episodes={len(ttr[name])} median={statistics.median(ttr[name]):.2f} h max={max(ttr[name]):.2f} h open={red is not None}")
    # merge-surface-only failures, and whether they follow another merge closely
    order_t = [(t(c["date"]), pr) for pr, c in order]
    def batched(pr, win=600):
        me = next(x for x, q in order_t if q == pr)
        return any(q != pr and 0 <= (me - x).total_seconds() <= win for x, q in order_t)
    only = [pr for pr in fail_merge_ex if not ((merge_fail[pr] - excl) & head_fail[pr])]
    L.result("merge_surface_only_failures", len(only))
    L.result("merge_surface_only_failures_batched_10min", sum(1 for pr in only if batched(pr)))
    L.result("all_merges_batched_10min", sum(1 for _, pr in order_t if batched(pr)))
    L.result("merges_missing_runs", missing)
    L.footer(snap["api_failures"])


if __name__ == "__main__":
    main()
