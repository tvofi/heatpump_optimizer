#!/usr/bin/env python3
"""D13 / round 8 / seat s1 -- required outputs 4 (DORA's four keys, by job) and 5 (CI seconds per merge).

METRICS (one line each), over the window JSON s1_window.py writes (c310541..cdf82da):
  releases_per_day      version-stamp commits (first-parent, no pull request, subject `vN.N.N: stamp`)
                        in the window over the window's span in days (first to last first-parent commit).
  lead_time_median_h    hours from a PR's merged_at to the committer date of the first later stamp on
                        the first-parent line; merges after the last stamp are `unreleased`.
  cfr_by_name           per check-run name, the share of window merges whose LATEST run of that name
                        (dora_keys.latest_by_name) concluded `failure`, at the merge commit and at the head
                        (dora_keys.cfr_by_name); cfr_* aggregates by dora_keys.cfr_keyings, minus the
                        names in .claude/workflows/cfr_exclusions.json (dora_keys.load_exclusions).
  reverts               window merges named by a later main commit `This reverts commit <sha>` (of the
                        merge or of a commit it merged) or by a merged PR titled `Revert "..."`.
  ttr_median_h[name]    per check-run name, over merge commits in first-parent order: hours from the first
                        merge commit whose latest run of the name failed to the next one where it succeeded.
  gov_seconds / gate_seconds per merge
                        governance_cost.dur summed over the check runs AT THE PR HEAD (d11lib.check_runs)
                        whose name is in GOV (re-derived below from .github/workflows/governance.yml's job
                        ids plus `briefs`, the rule governance_cost.py states) vs every other concluded run;
                        also the same at the merge commit. Durations are GitHub's, contention-immune.
  runs_per_name_at_head the count of check runs per name at the head (re-runs included), whose excess over
                        one is the number of re-executions the merge paid for.

INSTRUMENTED SYMBOLS: tools/audit/round4/D11/dora_keys.py:latest_by_name, cfr_keyings, cfr_by_name,
  load_exclusions; tools/audit/round4/D11/governance_cost.py:dur, GOV; tools/audit/round4/D11/d11lib.py:check_runs
  (through s1_gh's REST transport).

COMMAND (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_dora.py [--exclude name,...] [--gov-drop name]
PERTURBATIONS: --exclude <name> moves cfr_merge_keyed down by exactly that name's merge-only count
  (merges failing on that name and on no other non-excluded name); --gov-drop pr-contract moves
  governance_share down.
EXPECTED at baseline cdf82da: see REPORT-s1.md (exact, closed window; api_failures=0).
MACHINE: any; GitHub-reported durations and counts only, no timing on this box, so no load1/thread_factor.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import collections
import datetime
import json
import re
import statistics
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s1_gh as G  # noqa: E402
L = G.L
import dora_keys as D  # noqa: E402
import governance_cost as GC  # noqa: E402

TMP = os.environ.get("D13S1_TMP", "/home/claude/audit-r8/tmp/D13-s1")


def t(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True, check=True).stdout


def gov_from_workflows():
    """The rule governance_cost.py states: every job id in governance.yml, plus `briefs`."""
    with open(".github/workflows/governance.yml") as fh:
        jobs = set((yaml.safe_load(fh).get("jobs") or {}).keys())
    return jobs | {"briefs"}, jobs


def loo(values):
    """Leave-one-out for a mean: range, and the mean with the single largest cell dropped."""
    v = sorted(values)
    if len(v) < 5:
        return {"n": len(v)}
    return {"n": len(v), "min": round(v[0], 1), "max": round(v[-1], 1),
            "mean": round(statistics.mean(v), 1),
            "mean_drop_max": round(statistics.mean(v[:-1]), 1),
            "median": round(statistics.median(v), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default=os.path.join(TMP, "window.json"))
    ap.add_argument("--exclude", default="")
    ap.add_argument("--gov-drop", default="")
    a = ap.parse_args()
    w = json.load(open(a.window))
    prs = w["prs"]
    n = len(prs)

    # ---- deployment frequency and lead time -------------------------------------------------
    commits = list(reversed(w["commits"]))  # oldest first
    stamp_shas = {s["sha"] for s in w["stamps"]}
    stamps = [c for c in commits if c["sha"] in stamp_shas and re.match(r"v\d+\.\d+\.\d+: stamp", c["subject"])]
    span_days = (t(commits[-1]["date"]) - t(commits[0]["date"])).total_seconds() / 86400
    order = {c["sha"]: i for i, c in enumerate(commits)}
    lead, unreleased = [], []
    for p in prs:
        i = order[p["sha"]]
        nxt = next((c for c in commits[i + 1:] if c in stamps), None)
        if nxt is None:
            unreleased.append(p["pr"])
            continue
        lead.append((t(nxt["date"]) - t(p["merged_at"])).total_seconds() / 3600)
    lead.sort()
    L.result("window_days", round(span_days, 2), "d")
    L.result("stamps_in_window", len(stamps))
    L.result("releases_per_day", round(len(stamps) / span_days, 2), "releases/day")
    if lead:
        L.result("lead_time_median_h", round(statistics.median(lead), 2), "h")
        L.result("lead_time_p90_h", round(lead[int(0.9 * len(lead))], 2), "h")
    L.result("lead_time_n", len(lead))
    L.result("unreleased_merges", len(unreleased))

    # ---- change failure by check-run name, both keyings ------------------------------------
    excl = dict(D.load_exclusions(root="."))
    for x in filter(None, a.exclude.split(",")):
        excl[x] = {"reason": "perturbation"}
    merge_fail, head_fail = {}, {}
    for p in prs:
        merge_fail[p["pr"]] = {r["name"] for r in D.latest_by_name(p["runs_merge"]).values()
                               if r.get("conclusion") == "failure"}
        head_fail[p["pr"]] = {r["name"] for r in D.latest_by_name(p["runs_head"]).values()
                              if r.get("conclusion") == "failure"}
    # reverts: `This reverts commit <sha>` in any main commit (full history in the clone is the window)
    reverted = set()
    log = git("log", "--format=%H%x1f%B%x1e", f"{w['since']}..{w['head']}")
    rev_shas = set(re.findall(r"This reverts commit ([0-9a-f]{7,40})", log))
    for p in prs:
        merged = set(git("rev-list", f"{p['sha']}^1..{p['sha']}").split())
        if any(any(m.startswith(r) for m in merged) for r in rev_shas):
            reverted.add(p["pr"])
    revert_prs = [p["pr"] for p in prs if str(p.get("title") or "").startswith('Revert "')]
    L.result("revert_commits_in_window", len(rev_shas))
    L.result("revert_prs_in_window", len(revert_prs))
    L.result("reverted_merges", len(reverted))
    for num in reverted:
        merge_fail[num] = merge_fail[num] | {"(reverted)"}
        head_fail[num] = head_fail[num] | {"(reverted)"}
    L.result("window_merges", n)
    L.result("cfr_exclusions", json.dumps(sorted(excl)))
    for key, value in D.cfr_keyings(merge_fail, head_fail, set(excl), n).items():
        L.result(f"cfr_{key}", value)
    by_name = D.cfr_by_name(merge_fail, head_fail, n)
    counts = {}
    for name in by_name:
        mc = sum(1 for s in merge_fail.values() if name in s)
        hc = sum(1 for s in head_fail.values() if name in s)
        only = sum(1 for s in merge_fail.values() if name in s and not (s - set(excl) - {name}))
        counts[name] = [mc, hc, only]
        print(f"  per name {name!r}: merge {mc}/{n}  head {hc}/{n}  sole-nonexcluded-merge-red {only}")
    L.result("cfr_by_name", json.dumps(by_name, separators=(",", ":")))
    L.result("cfr_counts_by_name", json.dumps(counts, separators=(",", ":")))

    # ---- time to restore per name, over merge commits in first-parent order ------------------
    seq = sorted(prs, key=lambda p: order[p["sha"]])
    ttr = collections.defaultdict(list)
    open_red = {}
    for p in seq:
        latest = D.latest_by_name(p["runs_merge"])
        for name, r in latest.items():
            c = r.get("conclusion")
            if c == "failure" and name not in open_red:
                open_red[name] = p["committed"]
            elif c == "success" and name in open_red:
                ttr[name].append((t(p["committed"]) - t(open_red.pop(name))).total_seconds() / 3600)
    for name in sorted(ttr):
        d = sorted(ttr[name])
        L.result(f"ttr_h[{name}]", json.dumps({"episodes": len(d), "median": round(statistics.median(d), 2),
                                                 "max": round(d[-1], 2)}, separators=(",", ":")))
    L.result("ttr_still_open", json.dumps(sorted(open_red)))

    # ---- 5. CI seconds per merge -----------------------------------------------------------
    gov, gov_yml = gov_from_workflows()
    L.result("gov_rederived_equals_carried", gov == GC.GOV)
    L.result("gov_rederived", json.dumps(sorted(gov)))
    if a.gov_drop:
        gov = gov - {a.gov_drop}
    wf_jobs = set()
    for f in os.listdir(".github/workflows"):
        with open(os.path.join(".github/workflows", f)) as fh:
            for jid, job in (yaml.safe_load(fh).get("jobs") or {}).items():
                wf_jobs.add(jid)
                wf_jobs.add(re.sub(r" \(.*\)$", "", str(job.get("name", jid))))
    g_head, t_head, g_merge, t_merge = [], [], [], []
    runs_per_name = collections.Counter()
    reruns_per_name = collections.Counter()
    sec_per_name = collections.Counter()
    unknown = collections.Counter()
    for p in prs:
        rs = p["runs_head"]
        g_head.append(sum(GC.dur(c) for c in rs if c["name"] in gov))
        t_head.append(sum(GC.dur(c) for c in rs if c["name"] not in gov and c["conclusion"] != "skipped"))
        g_merge.append(sum(GC.dur(c) for c in p["runs_merge"] if c["name"] in gov))
        t_merge.append(sum(GC.dur(c) for c in p["runs_merge"]
                           if c["name"] not in gov and c["conclusion"] != "skipped"))
        per = collections.Counter(c["name"] for c in rs if c["conclusion"] != "skipped")
        for name, k in per.items():
            runs_per_name[name] += k
            reruns_per_name[name] += k - 1
        for c in rs:
            if c["conclusion"] != "skipped":
                sec_per_name[c["name"]] += GC.dur(c)
            base = re.sub(r" \(.*\)$", "", c["name"])
            if base not in wf_jobs:
                unknown[c["name"]] += 1
    tot = sum(g_head) + sum(t_head)
    L.result("gov_seconds_head", json.dumps(loo(g_head)))
    L.result("gate_seconds_head", json.dumps(loo(t_head)))
    L.result("governance_share_head", round(sum(g_head) / tot, 3) if tot else 0)
    totm = sum(g_merge) + sum(t_merge)
    L.result("gov_seconds_merge", json.dumps(loo(g_merge)))
    L.result("gate_seconds_merge", json.dumps(loo(t_merge)))
    L.result("governance_share_merge", round(sum(g_merge) / totm, 3) if totm else 0)
    L.result("governance_share_head_plus_merge",
             round((sum(g_head) + sum(g_merge)) / (tot + totm), 3) if tot + totm else 0)
    top = sorted(sec_per_name.items(), key=lambda x: -x[1])
    L.result("head_seconds_by_name", json.dumps({k: round(v) for k, v in top}, separators=(",", ":")))
    L.result("head_reruns_by_name", json.dumps({k: v for k, v in reruns_per_name.most_common() if v},
                                               separators=(",", ":")))
    L.result("head_names_in_no_workflow", json.dumps(dict(unknown), separators=(",", ":")))
    L.result("body_rounds", json.dumps(loo([sum(1 for c in p["runs_head"] if c["name"] == "pr-contract")
                                            for p in prs])))
    L.footer()


if __name__ == "__main__":
    main()
