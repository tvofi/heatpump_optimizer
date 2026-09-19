#!/usr/bin/env python3
"""D3 round 5 -- pre-screen the seeded mutant pool against the fast closure
drivers plus the differential golden gate (env_drift.py --all <baseline>).

Metric (one line): the number of seeded single-line production mutants that
the suite FAILS TO NOTICE -- i.e. every fast script in the mutant's measured
closure keeps its baseline exit status and failed-check count, AND the
differential golden gate (env_drift.py --all eaa2a06) keeps its baseline exit
status.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub \
        python3 tools/audit/round5/D3/prescreen.py [--jobs N] [--max K] \
        [--no-drift] [--only FILE:LINE]

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB, numpy 2.4.6 / OpenBLAS.

Kill rule (mutation_table.py's, reused not re-implemented): a driver kills a
mutant when its exit status changes, or when its `N of M ... FAILED` count
rises above the baseline's. The differential kills when env_drift --all's exit
status changes from the baseline's. Drivers run cheapest-measured-first and the
loop stops at the first kill; the differential runs only for mutants the fast
scripts did NOT kill (a mutant they killed is already dead, so the differential
cannot change its verdict).

Nothing is mutated in the working tree: every mutant edits its own clone tree
(tests/mutation_table.py:clone_tree), so a SIGKILL cannot leave production
edited. Writes only under this directory and a temp dir.
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
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as MT                          # noqa: E402

HERE = Path(__file__).resolve().parent
BASE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"


def empty_claims(tree):
    """Empty the differential gate's claim list (comments + stamp kept).

    Call this ONLY on a MUTANT tree, never on the baseline. The gate asks, per
    claim file, whether the three-dot could have moved what that file excuses
    (env_drift.py:claim_kinds, over three_dot_files -- which includes uncommitted
    work). A mutant edits integration Python, so the solver file is the branch's
    own and rule 2 requires its list to DIFFER from the baseline's; the baseline
    carries one inherited config_flow claim, so the honest, differing list for a
    mutant that claims nothing is empty. Any golden the mutant moves is then
    reported as UNCLAIMED DRIFT and the run exits 1.

    On the UNMUTATED baseline tree the three-dot is empty, the file must be left
    exactly as found, and emptying it fails the run on claim bookkeeping
    (measured: rc=1 in 0.8s). Returns (claim_path, original_text).
    """
    claim = tree / "tests" / "golden" / "claimed_drift.txt"
    orig = claim.read_text()
    claim.write_text("".join(ln for ln in orig.splitlines(True)
                             if ln.lstrip().startswith("#") or not ln.strip()))
    return claim, orig


def run_args(script, cwd, timeout, extra=()):
    """Like mutation_table.run_script but able to pass argv (env_drift --all)."""
    started = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, script, *extra], cwd=cwd, capture_output=True,
            text=True, timeout=timeout,
            env={**os.environ, "PYTHONPATH": "tests/hastub"},
        )
    except subprocess.TimeoutExpired:
        return MT.ScriptRun(124, 0, time.monotonic() - started)
    hits = MT._FAILED.findall(proc.stdout)
    return MT.ScriptRun(proc.returncode,
                        int(hits[-1][0]) if hits else 0,
                        time.monotonic() - started, proc.stdout, proc.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--no-drift", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--drop", default="",
                    help="comma-separated drivers to drop from the pre-screen "
                         "(a bounded fan-out window; report as a deviation)")
    args = ap.parse_args()

    pool = json.loads((HERE / "pool.json").read_text())["pool"]
    if args.only:
        want = set(args.only.split(","))
        pool = [m for m in pool
                if f"{Path(m['file']).name}:{m['line']}" in want]
    pool = pool[:args.max]
    if args.drop:
        dropset = set(args.drop.split(","))
        for m in pool:
            m["drivers"] = [s for s in m["drivers"] if s not in dropset]
        pool = [m for m in pool if m["drivers"]]
    needed = sorted({s for m in pool for s in m["drivers"]})

    work = Path(tempfile.mkdtemp(prefix="d3-prescreen-"))
    made = []
    try:
        base_tree = MT.clone_tree(work / "baseline")
        made.append(base_tree)
        baseline = {}
        for s in needed:
            r = MT.run_script(s, base_tree, args.timeout)
            baseline[s] = r
            print(f"  baseline {s}: rc={r.rc} failed={r.failed} {r.seconds:.1f}s")
        # drift baseline (must be green; the warm cache makes the baseline half
        # a cache hit and this times only the working-tree capture)
        drift_base = None
        if not args.no_drift:
            # The BASELINE tree is unmutated, so its three-dot is empty and the
            # gate requires tests/golden/claimed_drift.txt be left EXACTLY as
            # found. It then exits 0: the one inherited config_flow claim is
            # stale, but a stale claim on a branch that cannot own the file is
            # "reported, not judged". Emptying it here would trip the
            # record-PR-claims rule and turn the control red (measured: rc=1 in
            # 0.8s, "RECORD PR CLAIMS: three-dot touches neither card nor
            # solver fixtures"). So: no emptying for the baseline.
            drift_base = run_args("tests/env_drift.py", base_tree, args.timeout,
                                  ("--all", BASE))
            print(f"  baseline drift --all: rc={drift_base.rc} "
                  f"failed={drift_base.failed} {drift_base.seconds:.1f}s")
            if drift_base.rc != 0:
                print("PRESCREEN ABORTED: baseline drift is red")
                print(drift_base.stdout[-2000:])
                return 3

        red = [s for s, r in baseline.items() if r.rc != 0]
        if red:
            print("PRESCREEN ABORTED: baseline red in " + ", ".join(red))
            return 2

        jobs = max(1, min(args.jobs, len(pool)))
        trees = [MT.clone_tree(work / f"w{i}") for i in range(jobs)]
        made.extend(trees)
        results = []

        def drive(job):
            idx, mut = job
            tree = trees[idx % jobs]
            path = tree / mut["file"]
            lines = path.read_text().splitlines(True)
            i = mut["line"] - 1
            if i >= len(lines) or lines[i].rstrip("\n") != mut["old"]:
                results.append((mut, "SKIP-MOVED", ""))
                return
            lines[i] = mut["new"] + "\n"
            mutated = "".join(lines)
            try:
                import ast
                ast.parse(mutated)
            except SyntaxError:
                results.append((mut, "SKIP-UNPARSEABLE", ""))
                return
            original = path.read_text()
            path.write_text(mutated)
            verdict, by = "LIVES", ""
            try:
                for s in sorted(mut["drivers"], key=lambda s: baseline[s].seconds):
                    r = MT.run_script(s, tree, args.timeout)
                    if r.rc != baseline[s].rc or r.failed > baseline[s].failed:
                        verdict, by = "killed", s
                        break
                if verdict == "LIVES" and not args.no_drift:
                    claim, claim_orig = empty_claims(tree)
                    try:
                        d = run_args("tests/env_drift.py", tree, args.timeout,
                                     ("--all", BASE))
                    finally:
                        claim.write_text(claim_orig)
                    if d.rc != drift_base.rc:
                        verdict, by = "killed", "tests/env_drift.py --all"
            finally:
                path.write_text(original)
            print(f"  VERDICT {verdict:6s} {mut['file']}:{mut['line']} "
                  f"{mut['kind']}" + (f"  -- {by}" if by else ""), flush=True)
            results.append((mut, verdict, by))

        with __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]) \
                .ThreadPoolExecutor(max_workers=jobs) as ex:
            for i in range(jobs):
                ex.submit(lambda i=i: [drive((i, m)) for m in pool[i::jobs]])
    finally:
        for t in made:
            MT.drop_tree(t)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                       capture_output=True)
        shutil.rmtree(work, ignore_errors=True)

    rows = []
    for mut, verdict, by in sorted(results, key=lambda r: (r[0]["file"], r[0]["line"])):
        rows.append({"file": mut["file"], "line": mut["line"], "kind": mut["kind"],
                     "old": mut["old"], "new": mut["new"], "verdict": verdict,
                     "killed_by": by})
        mark = "LIVES" if verdict == "LIVES" else ("SKIP " if verdict.startswith("SKIP") else "ok   ")
        print(f"  {mark} {mut['file']}:{mut['line']} {mut['kind']}"
              + (f"  -- {by}" if by else ""))
    evaluated = sum(1 for r in rows if r["verdict"] != "SKIP " and not r["verdict"].startswith("SKIP"))
    killed = sum(1 for r in rows if r["verdict"] == "killed")
    survived = sum(1 for r in rows if r["verdict"] == "LIVES")
    out = {"baseline_sha": BASE, "drivers": needed, "rows": rows}
    (HERE / "prescreen.json").write_text(json.dumps(out, indent=1))
    print(f"RESULT mutants_evaluated={evaluated} count")
    print(f"RESULT mutants_killed={killed} count")
    print(f"RESULT mutants_survived={survived} count")
    print("RESULT survivor_fraction=%.3f ratio" % (survived / evaluated if evaluated else 0))
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT load1=%.2f ratio" % os.getloadavg()[0])
    print("RESULT prescreen_json=%s n/a" % (HERE / "prescreen.json"))


if __name__ == "__main__":
    sys.exit(main())
