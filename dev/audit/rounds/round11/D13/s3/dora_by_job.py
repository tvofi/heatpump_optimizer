#!/usr/bin/env python3
"""D13-s3 / round 11 -- D13.M4: DORA's four keys, by job, at the window's merges.

METRICS over the window's merges (enum_merges.py prints them; d13s3lib.W0/W1):
  deployment frequency  `vN.N.N` tags whose tagged commit's committer date is in
                        the window, per day (dora_keys.py's definition).
  lead time             hours from a pull request's merged_at to the committer
                        date of the FIRST `vN.N.N` tag (version order) whose
                        history holds its merge commit; median, p90, n, and the
                        merges no tag holds yet (censored, counted, not timed).
  change failure rate   share of merges failed, where a merge fails when the
                        LATEST run (dora_keys.latest_by_name) of some check-run
                        name at its merge commit concluded `failure` and that
                        name is not excluded -- or when a commit descending from
                        it on the baseline's history says `This reverts commit
                        <sha>` of it or of a commit it merged. Reported at the
                        merge commit and at the pull-request head, per name, and
                        with the exclusion list keyed two ways:
                          raw  -- `dora_keys.cfr_keyings` as written: the list's
                                  key compared with the full check-run name;
                          job  -- the key compared with the job id the name
                                  carries (`governance / record` -> `record`,
                                  `tests / fast (3.14)` -> `fast`).
                        COUNT KEY: the conclusion the API delivers per check-run
                        name at the commit; never a title or label.
  time to restore       per check-run name, over the window's merge commits in
                        first-parent order: an episode opens at the first merge
                        whose latest run of the name failed (its completed_at)
                        and closes at the next merge whose latest run of it
                        succeeded (its completed_at); hours, median and max,
                        and whether one is still open at the window's end.

INSTRUMENTED SYMBOLS: dev/audit/rounds/round4/D11/dora_keys.py:cfr_keyings,
  :cfr_by_name, :latest_by_name, :load_exclusions (driven on the window's live
  check-run data; the exclusion artifact dev/governance/config/cfr_exclusions.json).

COMMAND (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D13/s3/dora_by_job.py
  options: --exclude NAME (adds a key to the exclusion set, in memory)
           --fixture-revert SHA (injects one `This reverts commit SHA` commit
           descending from every window merge, in memory)

EXPECTED at baseline 92d38ecb (counts exact; API drift on a re-run of an old
run can move a rate by 1/merges): merges=271 releases_in_window=12
cfr_raw_excl_delta_merge=0.0 (dora_keys's exclusion buys nothing) against
cfr_job_excl_delta_merge>0; api_failures=0. See REPORT.md for the full block.
MACHINE: any; network-bound, no CPU claim (load1/thread_factor quoted only).

PERTURBATIONS.
  --exclude record      the job-keyed merge rate falls by exactly the merges
                        whose only failing job is `record`; the raw-keyed rate
                        (dora_keys.cfr_keyings) does not move -- the finding.
  --exclude "governance / record"  the raw-keyed rate now moves too.
  --fixture-revert <a window merge sha>  reverted_merges rises by one.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import collections
import json
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13s3lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "dev/audit/rounds/round4/D11"))
import dora_keys as DK  # noqa: E402


def job_id(name):
    """`governance / record` -> `record`; `tests / fast (3.14)` -> `fast`."""
    return re.sub(r" \(.*\)$", "", name.split(" / ", 1)[-1])


def schedule_only_jobs():
    """Job ids of nightly.yml whose `if:` refuses the push event: a red of one
    of them at a merge commit is a scheduled run attached to main's head."""
    import yaml
    jobs = yaml.safe_load((L.ROOT / ".github/workflows/nightly.yml").read_text())["jobs"]
    return {j for j, v in jobs.items()
            if "event_name != 'push'" in str(v.get("if", ""))}


def failing(runs):
    return {n for n, r in DK.latest_by_name(runs or []).items()
            if r.get("conclusion") == "failure"}


def rate(m, keep, n):
    return round(sum(1 for names in m.values() if keep(names)) / n, 3) if n else 0.0


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def reverted_merges(merges, fixture_shas=()):
    """{merge sha: reverting sha} for merges a descending commit reverts."""
    log = L.git("log", "--format=%H%x00%B%x01", L.BASELINE)
    reverts = []
    for rec in log.split("\x01"):
        if "\x00" not in rec:
            continue
        h, body = rec.strip().split("\x00", 1)
        for s in re.findall(r"This reverts commit ([0-9a-f]{7,40})", body):
            reverts.append((h, s))
    for fx in fixture_shas:
        reverts.append(("FIXTURE", fx))
    out = {}
    for m, _ in merges:
        merged = set(L.git("rev-list", f"{m}^1..{m}").split())
        for h, s in reverts:
            full = L.git("rev-parse", "--verify", "-q", s + "^{commit}").strip() or s
            if full not in merged:
                continue
            if h == "FIXTURE" or (h != m and _is_anc(m, h)):
                out[m] = h
    return out


def _is_anc(a, b):
    """True when commit a is an ancestor of (or is) b."""
    import subprocess
    return subprocess.run(["git", "-C", str(L.ROOT), "merge-base", "--is-ancestor",
                           a, b]).returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--fixture-revert", action="append", default=[])
    a = ap.parse_args()

    merges = L.window_merges()
    shas = [s for s, _ in merges]
    prs = dict(zip(shas, L.pmap(L.pr_of, shas)))
    heads = {s: (prs[s] or {}).get("head", {}).get("sha") for s in shas}
    mruns = dict(zip(shas, L.pmap(L.check_runs, shas)))
    hruns = dict(zip(shas, L.pmap(lambda s: L.check_runs(heads[s]) if heads[s] else [], shas)))
    n = len(shas)
    print(f"window {L.W0}..{L.W1}: {n} merges")

    # ---- deployment frequency and lead time ----------------------------
    tags = [x for x in L.git("tag", "--list", "v*").split()
            if re.fullmatch(r"v\d+\.\d+\.\d+", x)]
    tags.sort(key=lambda x: [int(v) for v in x[1:].split(".")])
    ttime = {x: L.utc(L.git("log", "-1", "--format=%cI", x).strip()) for x in tags}
    inwin = [x for x in tags if L.W0 <= ttime[x] <= L.W1]
    days = (L.t(L.W1) - L.t(L.W0)).total_seconds() / 86400
    print(f"version tags in window: {inwin}")
    later = [x for x in tags if ttime[x] >= L.W0]
    lead, unreleased = [], 0
    for s in shas:
        first = next((x for x in later if _is_anc(s, x)), None)
        if first is None:
            unreleased += 1
            continue
        lead.append((L.t(ttime[first]) - L.t(prs[s]["merged_at"])).total_seconds() / 3600)

    # ---- change failure, per name, both surfaces ----------------------
    mfail = {s: failing(mruns[s]) for s in shas}
    hfail = {s: failing(hruns[s]) for s in shas}
    excl = set(DK.load_exclusions(root=str(L.ROOT))) | set(a.exclude)
    raw = DK.cfr_keyings(mfail, hfail, excl, n)
    job_keep = lambda names: {x for x in names if job_id(x) not in excl and x not in excl}
    rev = reverted_merges(merges, a.fixture_revert)
    by_name = DK.cfr_by_name(mfail, hfail, n)
    for name, (mr, hr) in sorted(by_name.items(), key=lambda kv: -kv[1][0]):
        print(f"  per name {name!r}: merge={mr} ({round(mr*n)}) head={hr} ({round(hr*n)})")
    print(f"  reverted merges: {rev}")

    # ---- time to restore, per name -------------------------------------
    names = sorted({r["name"] for s in shas for r in (mruns[s] or [])})
    ttr = {}
    for name in names:
        open_at, eps = None, []
        for s in shas:
            r = DK.latest_by_name(mruns[s] or []).get(name)
            if not r or not r.get("completed_at"):
                continue
            if r["conclusion"] == "failure" and open_at is None:
                open_at = r["completed_at"]
            elif r["conclusion"] == "success" and open_at is not None:
                eps.append((L.t(r["completed_at"]) - L.t(open_at)).total_seconds() / 3600)
                open_at = None
        if eps or open_at:
            ttr[name] = (sorted(eps), open_at is not None)
    for name, (eps, op) in ttr.items():
        print(f"  ttr {name!r}: episodes={len(eps)} median_h="
              f"{round(statistics.median(eps), 2) if eps else '-'} max_h="
              f"{round(max(eps), 2) if eps else '-'} still_open={op}")

    print()
    L.result("merges", n)
    L.result("window_days", round(days, 2), "d")
    L.result("releases_in_window", len(inwin))
    L.result("releases_per_day", round(len(inwin) / days, 2), "releases/day")
    L.result("merges_per_release", round(n / len(inwin), 1) if inwin else "inf")
    L.result("lead_time_n", len(lead))
    L.result("lead_time_median_h", round(statistics.median(lead), 2) if lead else "-", "h")
    L.result("lead_time_p90_h", round(pct(lead, 0.9), 2) if lead else "-", "h")
    L.result("unreleased_merges", unreleased)
    L.result("exclusions", json.dumps(sorted(excl)))
    for k, v in raw.items():
        L.result(f"cfr_raw_{k}", v)
    L.result("cfr_raw_excl_delta_merge", round(raw["merge_unexcluded"] - raw["merge_keyed"], 3))
    jm = rate(mfail, lambda x: bool(job_keep(x)), n)
    jh = rate(hfail, lambda x: bool(job_keep(x)), n)
    L.result("cfr_job_merge_keyed", jm)
    L.result("cfr_job_head_keyed", jh)
    L.result("cfr_job_excl_delta_merge", round(raw["merge_unexcluded"] - jm, 3))
    L.result("merges_failing_only_excluded_jobs_merge",
             sum(1 for x in mfail.values() if x and not job_keep(x)))
    sched = schedule_only_jobs()
    L.result("schedule_only_jobs", ",".join(sorted(sched)))
    L.result("merges_failing_only_schedule_jobs_merge", sum(
        1 for x in mfail.values() if job_keep(x) and all(
            " / " not in y and job_id(y) in sched for y in job_keep(x))))
    ist = "governance / instrument-self-tests"
    L.result("ist_fail_merge", sum(1 for x in mfail.values() if ist in x))
    L.result("ist_fail_head", sum(1 for x in hfail.values() if ist in x))
    L.result("ist_fail_merge_pass_head", sum(
        1 for s in shas if ist in mfail[s] and DK.latest_by_name(hruns[s] or [])
        .get(ist, {}).get("conclusion") == "success"))
    L.result("merges_failing_only_ist_merge", sum(
        1 for x in mfail.values() if job_keep(x) == {ist}))
    L.result("reverted_merges", len(rev))
    L.result("cfr_job_merge_keyed_with_reverts",
             round(sum(1 for s in shas if job_keep(mfail[s]) or s in rev) / n, 3))
    L.result("merges_without_head_runs", sum(1 for s in shas if not hruns[s]))
    L.result("cfr_by_name", json.dumps(by_name, separators=(",", ":")))
    L.result("ttr_names", len(ttr))
    L.result("ttr_by_name", json.dumps(
        {k: [len(e), round(statistics.median(e), 2) if e else None,
             round(max(e), 2) if e else None, o] for k, (e, o) in ttr.items()},
        separators=(",", ":")))
    L.footer()


if __name__ == "__main__":
    main()
