#!/usr/bin/env python3
"""D13 / round 10 / seat s3 -- steps M4 (DORA per check-run name) and M5 (CI
seconds per merge, governance against the gate), plus the instrument check on
the DORA base the brief names.

METRIC (one line each):
  M4-instrument  dora_keys_loads: 1 if `dev/audit/rounds/round4/D11/dora_keys.py`
                 imports AND its `load_exclusions(root)` returns the registered
                 exclusion map at this tree, else 0 (the reason is printed).
  M4 cfr         over the merges whose merge commit is first-parent in
                 WINDOW (default v6.7.17..17f1c55fad1b), PR found by
                 /commits/<sha>/pulls: a merge fails if the LATEST run (by
                 started_at) of some check-run name at its merge commit
                 concluded `failure` (cfr_merge_*), or at its PR head
                 (cfr_head_*), raw and minus `excluded_jobs` of
                 dev/governance/config/cfr_exclusions.json; or by the revert
                 rule (a first-parent main commit after it saying `This reverts
                 commit <sha>` of it or a commit it merged). Per-name rates too.
  M5             per merge, sum over concluded check-runs at the PR head of
                 (completed_at-started_at): governance = names in the GOV set
                 re-derived from the workflow files (every job of
                 governance.yml, pr-contract.yml, pr-contract-rerun.yml,
                 budget-raise-gate.yml, budget-raise-gate-rerun.yml, plus
                 tests.yml `briefs`); gate = every other concluded run.
                 Count key: the check-run `name` GitHub delivered.

COMMAND (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python \
      dev/audit/rounds/round10/D13/s3/d13_s3.py
EXPECTED at baseline 17f1c55fad1b (tolerance exact; counts and GitHub-reported
durations over a closed window; see REPORT.md for the figures).
MACHINE: any; network-bound via `gh api` (cached under this directory's
cache/ so a re-run reproduces the numbers). Durations are GitHub-reported,
contention-immune.

PERTURBATIONS:
  D13S3_DORA_EXCL=dev/governance/config/cfr_exclusions.json  -> the instrument
      check's path patched to the registered artifact: dora_keys_loads 0 -> 1
      (only once the import is also fixed: D13S3_FIX_IMPORT=1).
  D13S3_EXCLUDE_EXTRA=<name>  -> adds one name to the exclusion set in memory;
      cfr_merge_excluded falls by exactly the merges failing ONLY on that name.
  D13S3_GOV_DROP=pr-contract -> governance_share falls.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import datetime  # noqa: E402
import importlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
os.environ.setdefault("D11_CACHE", os.path.join(HERE, "cache"))
sys.path.insert(0, os.path.join(ROOT, "tools/audit/round4/D11"))
import d11lib as L  # noqa: E402  (production instrument: cached gh api)

REPO = L.REPO
WINDOW = os.environ.get("D13S3_WINDOW", "v6.7.17..17f1c55fad1b")
EXCL_ARTIFACT = "dev/governance/config/cfr_exclusions.json"
GOV_FILES = ("governance.yml", "pr-contract.yml", "pr-contract-rerun.yml",
             "budget-raise-gate.yml", "budget-raise-gate-rerun.yml")


def res(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a),
                          capture_output=True, text=True).stdout


# ---------------------------------------------------------------- instrument
def dora_instrument_check():
    """Hook dora_keys.load_exclusions exactly as dora_keys.main() calls it."""
    dk_dir = os.path.join(ROOT, "dev/audit/rounds/round4/D11")
    saved = list(sys.path)
    try:
        sys.path.insert(0, dk_dir)
        if os.environ.get("D13S3_FIX_IMPORT") != "1":
            # as `python3 dora_keys.py` runs it: only its own dir is on path
            sys.modules.pop("d11lib", None)
            sys.path = [p for p in sys.path
                        if not p.endswith("tools/audit/round4/D11")]
        sys.modules.pop("dora_keys", None)
        try:
            dk = importlib.import_module("dora_keys")
        except ImportError as e:
            print(f"dora_keys import: {e!r}")
            return 0
        if os.environ.get("D13S3_DORA_EXCL"):
            dk.CFR_EXCLUSIONS = os.environ["D13S3_DORA_EXCL"]
        print(f"dora_keys.CFR_EXCLUSIONS = {dk.CFR_EXCLUSIONS}")
        try:
            excl = dk.load_exclusions(root=ROOT)
        except (OSError, SystemExit) as e:
            print(f"dora_keys.load_exclusions: {e!r}")
            return 0
        print(f"dora_keys.load_exclusions -> {sorted(excl)}")
        return 1
    finally:
        sys.path = saved
        sys.modules["d11lib"] = L


# ---------------------------------------------------------------- data
def window_merges():
    lo, hi = WINDOW.split("..")
    shas = git("log", "--first-parent", "--merges", "--format=%H",
               f"{lo}..{hi}").split()
    return list(reversed(shas))


def pr_for(sha):
    d = L.api(f"repos/{REPO}/commits/{sha}/pulls")
    if not d:
        return None
    for p in d:
        if p.get("merge_commit_sha") == sha:
            return p
    return d[0] if len(d) == 1 else None


def latest_failing(runs):
    last = {}
    for r in runs:
        n = r["name"]
        if n not in last or (r.get("started_at") or "") > (
                last[n].get("started_at") or ""):
            last[n] = r
    return {n for n, r in last.items() if r.get("conclusion") == "failure"}


def dur(c):
    if c.get("conclusion") in (None, "skipped") or not c.get(
            "started_at") or not c.get("completed_at"):
        return 0.0
    a = datetime.datetime.fromisoformat(c["started_at"].replace("Z", "+00:00"))
    b = datetime.datetime.fromisoformat(
        c["completed_at"].replace("Z", "+00:00"))
    return max(0.0, (b - a).total_seconds())


def gov_set():
    names = set()
    for f in GOV_FILES:
        p = os.path.join(ROOT, ".github/workflows", f)
        if not os.path.exists(p):
            continue
        t = open(p).read()
        m = re.search(r"^jobs:\n(.*)", t, re.S | re.M)
        names |= set(re.findall(r"^  ([A-Za-z0-9_-]+):", m.group(1), re.M))
    names.add("briefs")
    drop = os.environ.get("D13S3_GOV_DROP")
    if drop:
        names.discard(drop)
    return names


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    res("dora_keys_loads", dora_instrument_check())

    gm = importlib.import_module("governance_cost")
    carried = set(gm.GOV)
    derived = gov_set()
    print(f"GOV derived={sorted(derived)}")
    res("gov_derived_minus_carried",
        json.dumps(sorted(derived - carried), separators=(",", ":")))
    res("gov_carried_minus_derived",
        json.dumps(sorted(carried - derived), separators=(",", ":")))

    excl = set(json.load(open(os.path.join(ROOT, EXCL_ARTIFACT)))
               ["excluded_jobs"])
    if os.environ.get("D13S3_EXCLUDE_EXTRA"):
        excl.add(os.environ["D13S3_EXCLUDE_EXTRA"])
    merges = window_merges()
    print(f"window {WINDOW}: {len(merges)} first-parent merges")
    rows = []
    for sha in merges:
        pr = pr_for(sha)
        if pr is None:
            continue
        mruns = L.check_runs(sha)
        hruns = L.check_runs(pr["head"]["sha"])
        if mruns is None or hruns is None:
            continue
        rows.append({"sha": sha, "n": pr["number"], "title": pr["title"],
                     "mfail": latest_failing(mruns),
                     "hfail": latest_failing(hruns), "hruns": hruns})
    n = len(rows)
    res("merges", n)
    res("merges_unmapped", len(merges) - n)

    # revert rule
    reverted = set()
    allsha = {r["sha"]: r for r in rows}
    log = git("log", "--first-parent", "--format=%H%x00%B%x01",
              WINDOW.split("..")[1])
    for rec in log.split("\x01"):
        for target in re.findall(r"This reverts commit ([0-9a-f]{7,40})", rec):
            for r in rows:
                merged = git("rev-list", f"{r['sha']}^1..{r['sha']}").split()
                if any(m.startswith(target) for m in merged):
                    reverted.add(r["n"])
    res("revert_rule_merges", len(reverted))

    def rate(key, drop):
        return round(sum(1 for r in rows if (r[key] - drop) or (
            r["n"] in reverted)) / n, 3) if n else 0.0
    res("cfr_merge_raw", rate("mfail", set()))
    res("cfr_merge_excluded", rate("mfail", excl))
    res("cfr_head_raw", rate("hfail", set()))
    res("cfr_head_excluded", rate("hfail", excl))
    names = collections.Counter()
    hnames = collections.Counter()
    for r in rows:
        names.update(r["mfail"])
        hnames.update(r["hfail"])
    by = {k: [names[k], hnames[k]] for k in sorted(set(names) | set(hnames))}
    res("cfr_by_name_counts", json.dumps(by, separators=(",", ":")))
    for k, (a, b) in sorted(by.items(), key=lambda x: -x[1][0]):
        print(f"  {k!r}: merge {a}/{n}  head {b}/{n}")

    # M5
    g, t, gov_named = [], [], collections.Counter()
    for r in rows:
        gs = sum(dur(c) for c in r["hruns"] if c["name"] in derived)
        ts = sum(dur(c) for c in r["hruns"] if c["name"] not in derived)
        g.append(gs)
        t.append(ts)
        for c in r["hruns"]:
            if c["name"] in derived and dur(c) > 0:
                gov_named[c["name"]] += dur(c)
    if n:
        res("gov_seconds_median", round(statistics.median(g)), "s/merge")
        res("gov_seconds_mean", round(statistics.mean(g)), "s/merge")
        res("gate_seconds_median", round(statistics.median(t)), "s/merge")
        res("gate_seconds_mean", round(statistics.mean(t)), "s/merge")
        res("governance_share", round(sum(g) / ((sum(g) + sum(t)) or 1), 3))
        res("gov_seconds_by_name",
            json.dumps({k: round(v) for k, v in gov_named.most_common()},
                       separators=(",", ":")))
    tf = (time.process_time() - t0p) / max(1e-9, time.thread_time() - t0t)
    res("thread_factor", round(tf, 3))
    res("load1", round(os.getloadavg()[0], 2))
    res("swapins", 0)
    res("api_failures", len(L.FAILURES))
    for p, e in L.FAILURES:
        print(f"  API FAILURE {p}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
