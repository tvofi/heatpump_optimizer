#!/usr/bin/env python3
"""D3 round 5 -- run the differential golden gate (env_drift.py --all <baseline>)
against the mutants the fast-script pre-screen did NOT kill.

Metric (one line): the number of seeded mutants that survive the differential
golden gate as well as every fast script in their measured closure -- each a
production line the whole PR gate (GATE_SCOPE=auto GOLDEN_MODE=drift) cannot
fail on.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub \
        python3 -u tools/audit/round5/D3/drift_survivors.py [--jobs N] [--only F:L,...]

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB. The baseline half of each env_drift --all run is a
cache hit (~/.cache/heatpump_optimizer/drift-baseline/), so each mutant costs
one working-tree capture of the 56 scenarios.

A mutant is killed by the differential when its env_drift --all exit status
differs from the baseline's (baseline = rc 0, "NO UNCLAIMED DRIFT").
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as MT                          # noqa: E402

HERE = Path(__file__).resolve().parent
BASE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"


def run_drift(tree, timeout):
    started = time.monotonic()
    proc = subprocess.run(
        [sys.executable, "tests/env_drift.py", "--all", BASE],
        cwd=tree, capture_output=True, text=True, timeout=timeout,
        env={**os.environ, "PYTHONPATH": "tests/hastub"},
    )
    drift = [ln.strip() for ln in proc.stdout.splitlines()
             if "drift" in ln.lower() and ("moved" in ln.lower()
                                           or "UNCLAIMED" in ln or "DIFF" in ln)]
    return proc.returncode, time.monotonic() - started, drift, proc.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--only", default="")
    ap.add_argument("--assume-baseline-green", action="store_true",
                    help="skip the ~220 s baseline drift run; use rc=0 as the "
                         "control (the baseline run is recorded in "
                         "drift_cached.out as rc=0)")
    args = ap.parse_args()

    pool = {f"{r['file']}:{r['line']}": r
            for r in json.loads((HERE / "pool.json").read_text())["pool"]}
    pre_path = HERE / "prescreen.json"
    if pre_path.exists():
        rows = json.loads(pre_path.read_text())["rows"]
        survivors = [dict(pool.get(f"{r['file']}:{r['line']}", {}), **r)
                     for r in rows if r["verdict"] == "LIVES"]
    else:
        survivors = list(pool.values())
    if args.only:
        want = set(args.only.split(","))
        survivors = [r for r in survivors
                     if f"{Path(r['file']).name}:{r['line']}" in want]
    if not survivors:
        print("no survivors to test")
        return 0
    print(f"driving {len(survivors)} survivors through the differential gate")

    work = Path(tempfile.mkdtemp(prefix="d3-drift-"))
    made = []
    try:
        baseline_tree = MT.clone_tree(work / "base")
        made.append(baseline_tree)
        if not args.assume_baseline_green:
            brc, bsec, bdrift, bout = run_drift(baseline_tree, args.timeout)
            print(f"  baseline drift: rc={brc} {bsec:.0f}s")
            assert brc == 0, "baseline drift is red; aborting"
        else:
            brc = 0
            print("  baseline drift rc=0 (from drift_cached.out; not re-run)")
        jobs = max(1, min(args.jobs, len(survivors)))
        trees = [MT.clone_tree(work / f"w{i}") for i in range(jobs)]
        made.extend(trees)
        out_rows = []

        def one(job):
            idx, r = job
            tree = trees[idx % jobs]
            path = tree / r["file"]
            lines = path.read_text().splitlines(True)
            i = r["line"] - 1
            if lines[i].rstrip("\n") != r["old"]:
                out_rows.append({**r, "drift_verdict": "SKIP-MOVED"})
                return
            lines[i] = r["new"] + "\n"
            original = path.read_text()
            path.write_text("".join(lines))
            # The differential gate requires that a branch touching
            # integration Python restate its own claim footprint; the
            # baseline's tests/golden/claimed_drift.txt carries one inherited
            # config_flow claim (stale), so leaving it in place fails the run
            # on bookkeeping, not on drift. Emptying the list is the honest
            # statement for a mutant that claims nothing, and then any golden
            # the mutant moves is reported as UNCLAIMED DRIFT and fails.
            claim = tree / "tests" / "golden" / "claimed_drift.txt"
            claim_orig = claim.read_text()
            claim.write_text("".join(
                ln for ln in claim_orig.splitlines(True)
                if ln.lstrip().startswith("#") or not ln.strip()))
            feat_rc = None
            try:
                if "tests/features.py" in r.get("drivers", []):
                    feat_rc = MT.run_script("tests/features.py", tree,
                                            args.timeout).rc
                if feat_rc not in (None, 0):
                    verdict, rc, sec, drift = "killed", feat_rc, 0.0, \
                        ["features.py red"]
                else:
                    rc, sec, drift, out = run_drift(tree, args.timeout)
                    verdict = "killed" if rc != brc else "LIVES"
            finally:
                path.write_text(original)
                claim.write_text(claim_orig)
            out_rows.append({**r, "drift_verdict": verdict, "features_rc": feat_rc,
                             "drift_rc": rc, "drift_seconds": round(sec, 1),
                             "drift_lines": drift[:6]})
            print(f"  {verdict:6s} {r['file']}:{r['line']} {r['kind']} "
                  f"features_rc={feat_rc} rc={rc} {sec:.0f}s", flush=True)

        with ThreadPoolExecutor(max_workers=jobs) as ex:
            list(ex.map(one, list(enumerate(survivors))))
    finally:
        for t in made:
            MT.drop_tree(t)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True)
        shutil.rmtree(work, ignore_errors=True)

    killed = [r for r in out_rows if r["drift_verdict"] == "killed"]
    lives = [r for r in out_rows if r["drift_verdict"] == "LIVES"]
    (HERE / "drift_survivors.json").write_text(json.dumps(out_rows, indent=1))
    print(f"RESULT survivors_through_drift={len(out_rows)} count")
    print(f"RESULT killed_by_drift={len(killed)} count")
    print(f"RESULT survived_drift={len(lives)} count")
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT load1=%.2f ratio" % os.getloadavg()[0])


if __name__ == "__main__":
    sys.exit(main())
