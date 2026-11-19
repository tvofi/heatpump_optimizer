#!/usr/bin/env python3
"""D13-s3 / round 11 -- D13.M5: CI seconds per merge, governance against the gate.

METRICS over the window's merges (enum_merges.py; d13s3lib.W0/W1). Seconds are
(completed_at - started_at) of CONCLUDED check runs as GitHub reports them,
split by tools/audit/round4/D11/governance_cost.py's own `GOV` set and `bare`
(a check run is governance when bare(name) is in GOV, else gate):

  head_*    governance_cost.py's surface: the check-runs listing at the pull
            request's FINAL head only, default listing (latest attempt).
  full_*    every CI second the merge paid: the listing with `filter=all`
            (re-run attempts too) at EVERY commit of the pull request
            (`pulls/<n>/commits`) plus its merge commit on main.
  omitted_share  1 - sum(head seconds) / sum(full seconds): the share of a
            merge's CI seconds governance_cost.py's surface does not read.
  gov_rederived  the GOV rule re-derived from the workflow files at the
            baseline: every job id in governance.yml, pr-contract.yml,
            budget-raise-gate.yml and gate-sweep.yml, plus tests.yml's
            `briefs` (governance_cost.py's own comment states this rule);
            printed beside GOV with both set differences.
  COUNT KEY: the seconds GitHub delivers per check run; never a job title.

INSTRUMENTED SYMBOLS: tools/audit/round4/D11/governance_cost.py:GOV, :bare,
  :dur (each reading is computed with the instrument's own symbols on the
  window's live check-run data).

COMMAND (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D13/s3/ci_seconds.py
  options: --surface head|full (default both), --gov-drop NAME (in memory)

EXPECTED at baseline 92d38ecb: merges=271; see REPORT.md for the block
(tolerance: exact for counts; a re-run of an old workflow on GitHub can add
seconds to `full_*` only). api_failures=0.
MACHINE: any; network-bound; durations are GitHub's, contention-immune.

PERTURBATIONS.
  --gov-drop pr-contract   governance share falls on both surfaces (the
                           instrument's own control).
  D13S3_HEAD_ONLY=1        full_* collapses onto head_* and omitted_share -> 0
                           (the surface is what moves the number).
NULL CONTROL: merges whose PR has one commit and whose runs had no re-run
attempt: their omitted share is the merge-commit runs alone.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import statistics
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13s3lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "tools/audit/round4/D11"))
import governance_cost as GC  # noqa: E402


def gov_rederived():
    wf = L.ROOT / ".github/workflows"
    out = set()
    for f in ("governance.yml", "pr-contract.yml", "budget-raise-gate.yml", "gate-sweep.yml"):
        out |= set((yaml.safe_load((wf / f).read_text()).get("jobs") or {}))
    tests_jobs = set(yaml.safe_load((wf / "tests.yml").read_text())["jobs"])
    if "briefs" in tests_jobs:
        out.add("briefs")
    return out


def split(runs, gov):
    g = sum(GC.dur(c) for c in runs if GC.bare(c["name"]) in gov)
    t = sum(GC.dur(c) for c in runs
            if GC.bare(c["name"]) not in gov and c.get("conclusion") != "skipped")
    return g, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gov-drop", action="append", default=[])
    a = ap.parse_args()
    gov = set(GC.GOV) - set(a.gov_drop)
    head_only = os.environ.get("D13S3_HEAD_ONLY") == "1"

    merges = L.window_merges()
    shas = [s for s, _ in merges]
    prs = dict(zip(shas, L.pmap(L.pr_of, shas)))
    heads = {s: prs[s]["head"]["sha"] for s in shas}
    commits = dict(zip(shas, L.pmap(lambda s: L.pr_commits(prs[s]["number"]), shas)))
    hruns = dict(zip(shas, L.pmap(lambda s: L.check_runs(heads[s]), shas)))

    def full_runs(s):
        cs = [heads[s]] if head_only else sorted(set((commits[s] or []) + [heads[s], s]))
        rs = []
        for c in cs:
            rs += (L.check_runs(c) if head_only else L.check_runs(c, all_attempts=True)) or []
        uniq = {r["id"]: r for r in rs}
        return list(uniq.values()), len(cs)

    full = dict(zip(shas, L.pmap(full_runs, shas)))

    hg, ht, fg, ft, ncommits, reruns, rerun_s = [], [], [], [], [], 0, 0.0
    seen = {}
    null_h, null_f = 0.0, 0.0
    for s in shas:
        g, t = split(hruns[s] or [], gov)
        hg.append(g); ht.append(t)
        rs, nc = full[s]
        g2, t2 = split(rs, gov)
        fg.append(g2); ft.append(t2)
        for r in rs:
            seen[r["id"]] = GC.dur(r)
        ncommits.append(nc)
        if not head_only:
            hall = L.check_runs(heads[s], all_attempts=True) or []
            dflt = {r["id"] for r in (hruns[s] or [])}
            extra = sum(1 for r in hall if r["id"] not in dflt)
            reruns += extra
            rerun_s += sum(GC.dur(r) for r in hall if r["id"] not in dflt)
            if len(commits[s] or []) == 1 and extra == 0:
                null_h += g + t
                null_f += g2 + t2

    H, F = sum(hg) + sum(ht), sum(fg) + sum(ft)
    rd = gov_rederived()
    print(f"window {L.W0}..{L.W1}: {len(shas)} merges; commits per PR median "
          f"{statistics.median(ncommits)} max {max(ncommits)}")
    print(f"GOV (governance_cost.py) = {sorted(GC.GOV)}")
    print(f"GOV re-derived at baseline = {sorted(rd)}")
    L.result("merges", len(shas))
    L.result("gov_missing_from_GOV", ",".join(sorted(rd - set(GC.GOV))) or "none")
    L.result("gov_extra_in_GOV", ",".join(sorted(set(GC.GOV) - rd)) or "none")
    for tag, g, t in (("head", hg, ht), ("full", fg, ft)):
        tot = [x + y for x, y in zip(g, t)]
        L.result(f"{tag}_governance_seconds_median", round(statistics.median(g)), "s/merge")
        L.result(f"{tag}_gate_seconds_median", round(statistics.median(t)), "s/merge")
        L.result(f"{tag}_total_seconds_mean", round(statistics.mean(tot)), "s/merge")
        L.result(f"{tag}_governance_share", round(sum(g) / (sum(g) + sum(t)), 3))
    L.result("head_total_seconds", round(H), "s")
    L.result("full_total_seconds", round(F), "s")
    L.result("omitted_share", round(1 - H / F, 3) if F else 0.0)
    L.result("full_total_seconds_unique_runs", round(sum(seen.values())), "s")
    L.result("omitted_share_unique_runs", round(1 - H / sum(seen.values()), 3) if seen else 0.0)
    L.result("rerun_attempts_hidden_at_final_heads", reruns)
    L.result("rerun_seconds_hidden_at_final_heads", round(rerun_s), "s")
    L.result("null_control_single_commit_merges_omitted_share",
             round(1 - null_h / null_f, 3) if null_f else "n/a")
    # leave-one-day-out of omitted_share (the window's seven days as cells)
    days = sorted({c[:10] for _, c in merges})
    cells = {}
    for d in days:
        idx = [i for i, (_, c) in enumerate(merges) if c[:10] == d]
        h = sum(hg[i] + ht[i] for i in idx)
        f = sum(fg[i] + ft[i] for i in idx)
        if f:
            cells[d] = round(1 - h / f, 3)
    L.result("omitted_share_by_day", ",".join(f"{k}:{v}" for k, v in cells.items()))
    if cells:
        lo = min(cells, key=cells.get)
        idx = [i for i, (_, c) in enumerate(merges) if c[:10] != lo]
        h = sum(hg[i] + ht[i] for i in idx)
        f = sum(fg[i] + ft[i] for i in idx)
        L.result("omitted_share_range", f"{min(cells.values())}..{max(cells.values())}")
        L.result("omitted_share_drop_lowest_day", round(1 - h / f, 3) if f else "n/a")
    L.footer()


if __name__ == "__main__":
    main()
