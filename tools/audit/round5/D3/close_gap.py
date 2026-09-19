#!/usr/bin/env python3
"""D3 round 5 -- close the pre-screen's driver gap on the survivors.

Metric (one line): of the mutants that survived the pre-screen (the 14 fast
closure scripts plus tests/env_drift.py --all), how many are killed by one of
the CI scripts the pre-screen did NOT run -- so that the reported survivor list
is faithful against every script tests/run.sh can select, not just the fast set.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub \
        python3 -u tools/audit/round5/D3/close_gap.py [--jobs N] [--only F:L,...]

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB.

The omitted set is every script in tests/closures.json minus the pre-screen's
FAST list minus tests/env_drift.py (driven separately by prescreen.py). The
brief forbids tests/stress.py outside a quiet window, so it is listed and
skipped, not run. Kill rule is mutation_table.py's, reused: a driver kills when
its exit status changes or its `N of M ... FAILED` count rises.
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

#: Every gate script the pre-screen did not run. src/ is JS (card.mjs) and is
#: driven by node, so it is handled by name below.
CLOSURES = json.loads((ROOT / "tests" / "closures.json").read_text())["closures"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    pool = {f"{r['file']}:{r['line']}": r
            for r in json.loads((HERE / "pool.json").read_text())["pool"]}
    pre = json.loads((HERE / "prescreen.json").read_text())
    survivors = [dict(pool.get(f"{r['file']}:{r['line']}", {}), **r)
                 for r in pre["rows"] if r["verdict"] == "LIVES"]
    if args.only:
        want = set(args.only.split(","))
        survivors = [r for r in survivors
                     if f"{Path(r['file']).name}:{r['line']}" in want]
    if not survivors:
        print("no survivors to close the gap on")
        return 0

    fast = set(json.loads((HERE / "pool.json").read_text())["fast_drivers"])
    omitted_all = [s for s in sorted(CLOSURES)
                   if s not in fast and s not in ("tests/env_drift.py", "tests/stress.py")]
    # mutation_table.run_script drives `sys.executable <script>`; only Python
    # scripts can be driven that way here. The JS goldens are named, not run.
    # tests/golden.py is excluded because in its default mode it is a shim for
    # `tests/env_drift.py --all origin/main` (measured: its whole output is that
    # one command line) and it exits 1 on the unmutated baseline for the same
    # claim-bootstrap reason env_drift reports as "reported, not judged"; the
    # env_drift --all run in prescreen.py already covers it.
    omitted = [s for s in omitted_all
               if s.endswith(".py") and s != "tests/golden.py"]
    not_run = ([s for s in omitted_all if not s.endswith(".py")]
               + ["tests/golden.py (shim for env_drift.py --all; covered there)"]
               + ["tests/stress.py (quiet-window only, per the brief)"])
    print(f"survivors: {len(survivors)}; omitted scripts to run: {omitted}")
    print(f"NOT run (not Python / quiet-window only): {not_run}")

    work = Path(tempfile.mkdtemp(prefix="d3-closegap-"))
    made = []
    try:
        base_tree = MT.clone_tree(work / "baseline")
        made.append(base_tree)
        baseline = {}
        for s in omitted:
            r = MT.run_script(s, base_tree, args.timeout)
            baseline[s] = r
            print(f"  baseline {s}: rc={r.rc} failed={r.failed} {r.seconds:.1f}s")
        red = [s for s, r in baseline.items() if r.rc != 0]
        if red:
            print("CLOSE-GAP ABORTED: baseline red in " + ", ".join(red))
            return 2
        jobs = max(1, min(args.jobs, len(survivors)))
        trees = [MT.clone_tree(work / f"w{i}") for i in range(jobs)]
        made.extend(trees)
        rows = []

        def one(job):
            idx, r = job
            tree = trees[idx % jobs]
            path = tree / r["file"]
            lines = path.read_text().splitlines(True)
            i = r["line"] - 1
            if lines[i].rstrip("\n") != r["old"]:
                rows.append({**r, "gap_verdict": "SKIP-MOVED"})
                return
            lines[i] = r["new"] + "\n"
            original = path.read_text()
            path.write_text("".join(lines))
            verdict, by = "LIVES", ""
            try:
                for s in sorted(omitted, key=lambda s: baseline[s].seconds):
                    rr = MT.run_script(s, tree, args.timeout)
                    if rr.rc != baseline[s].rc or rr.failed > baseline[s].failed:
                        verdict, by = "killed", s
                        break
            finally:
                path.write_text(original)
            rows.append({**r, "gap_verdict": verdict, "gap_killed_by": by})
            print(f"  {verdict:6s} {r['file']}:{r['line']} {r['kind']}"
                  + (f"  -- {by}" if by else ""), flush=True)

        with ThreadPoolExecutor(max_workers=jobs) as ex:
            list(ex.map(one, list(enumerate(survivors))))
    finally:
        for t in made:
            MT.drop_tree(t)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True)
        shutil.rmtree(work, ignore_errors=True)

    killed = [r for r in rows if r["gap_verdict"] == "killed"]
    lives = [r for r in rows if r["gap_verdict"] == "LIVES"]
    (HERE / "close_gap.json").write_text(json.dumps(
        {"omitted_scripts": omitted, "rows": rows}, indent=1))
    print(f"RESULT survivors_checked={len(rows)} count")
    print(f"RESULT killed_by_omitted_scripts={len(killed)} count")
    print(f"RESULT survived_every_gate_script={len(lives)} count")
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT load1=%.2f ratio" % os.getloadavg()[0])
    print("RESULT script_seconds=%s n/a" % time.strftime("%H:%M:%S"))


if __name__ == "__main__":
    sys.exit(main())
