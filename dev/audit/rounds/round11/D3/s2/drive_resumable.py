#!/usr/bin/env python3
"""D3-s2 pre-screen (D3.M2), resumable at the (mutant, driver) pair.

The same verdict rule as tests/mutation_table.py's --scope full drive
(prescreen.py drives that instrument whole), split so a container restart
loses at most the runs in flight: every finished driver run is appended to
OUT/pairs.jsonl and a restart skips it.

Metric: per universe mutant (enumerate.py), its verdict -- "killed by S"
(first driver, in mutation_table.driver_order, whose run is red and names a
failing check: mutation_table.killed against the green baseline), "LIVES"
(every driver ran or was reach-skipped, none killed), SKIP-TIMED-OUT, or
SKIP-UNPARSEABLE / SKIP-MOVED.
Count key: verdict string per enumerator item name.
Inputs reused from prescreen.py's run (same tree = HEAD marker commit):
  OUT_PREV/progress.jsonl  -> every driver's GREEN unmutated baseline and its seconds
  OUT_PREV/reach/*.json    -> traced baselines; a pair mutation_table.reach_skip
                              calls unkillable is skipped (never_reaches), as the
                              instrument does
Drivers: the cell file's measured closure (mutation_table.drivers_for over
DEFAULT_SCRIPTS) minus stress.py, edge.py, backtest.py (D3.M2) and
harness_headers.py (EXCLUSIVE, --scope full defers it); env_drift.py runs as
`--all HEAD^1` (HEAD^1 = baseline 92d38ecb).  A ledger row the mutant itself
makes stale is hidden from the mutant's tree (mutation_table.invalidated_rows).
Instrumented symbols: tests/mutation_table.py:run_script/killed/reach_skip/
driver_order/invalidated_rows driving custom_components/heatpump_optimizer/<cell>.py.
Perturbation: --null drives mutation_table.null_control's comment-only edit
through every driver instead: its verdict must read LIVES (a kill there means
the rule, not the code, killed). Deleting the killing check of a listed kill
moves that mutant to LIVES.
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
       dev/audit/rounds/round11/D3/s2/drive_resumable.py OUT OUT_PREV [--jobs 2] [--null]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; box B2 (4 cores, shared).
Verdicts are deterministic; seconds are provisional.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import ast
import json
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "tests")
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402

SKIP = ("tests/stress.py", "tests/edge.py", "tests/backtest.py",
        "tests/harness_headers.py")
KIND_WEIGHT = {"RAISE_DEL": 0, "GUARD_OFF": 1, "CONST": 2, "CMP_BOUND": 3,
               "BOOLOP": 4, "CLAMP_DROP": 5, "RETURN_DEL": 6}
REF = "HEAD^1"


def clone_tree(dest, exclude):
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet",
                    str(dest), "HEAD"], cwd=mt.ROOT, check=True,
                   capture_output=True)
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=mt.ROOT, check=True, capture_output=True).stdout
    keep = [x for x in listing.split(b"\0")
            if x and (mt.ROOT / x.decode()).is_file()
            and not x.decode().startswith(exclude)]
    tar = subprocess.run(["tar", "-c", "--null", "-T", "-", "-f", "-"],
                         cwd=mt.ROOT, check=True,
                         input=b"\0".join(keep) + b"\0",
                         stdout=subprocess.PIPE).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("prev")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    prev = Path(a.prev)
    base = {}
    for ln in open(prev / "progress.jsonl"):
        d = json.loads(ln)
        if d["ev"] == "baseline":
            base[d["script"]] = d
    assert all(b["rc"] == 0 and b["failed"] == 0 for b in base.values()), \
        "a baseline is not green"
    secs = {s: b["seconds"] for s, b in base.items()}
    reaches = {}
    for f in (prev / "reach").glob("*.json"):
        reaches[f.name[:-5].replace("tests_", "tests/", 1)] = json.loads(f.read_text())
    closures = mt.load_closures()
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",") if s and s not in SKIP]
    budgets = mt.load_budgets()
    killed_by = budgets.get("killed_by", {})

    if a.null:
        nul = mt.null_control(mt.PRODUCTION / "__init__.py")
        universe = [dict(nul, status="null")]
    else:
        universe, _ = en.universe()
        universe.sort(key=lambda s: (s["status"] == "gap",
                                     KIND_WEIGHT.get(s["kind"], 9),
                                     s["file"], s["line"]))
    pairs_path = out / "pairs.jsonl"
    done = {}
    if pairs_path.exists():
        for ln in open(pairs_path):
            d = json.loads(ln)
            done[(d["item"], d["script"])] = d
    lock = threading.Lock()
    pf = open(pairs_path, "a", buffering=1)

    def log(**kw):
        with lock:
            pf.write(json.dumps(dict(kw, t=round(time.time(), 1))) + "\n")

    rows_at = mt.ledger_dir().relative_to(mt.ROOT)
    work = []
    for s in universe:
        name = en.item_name(s)
        drivers = [d for d in mt.drivers_for(s["file"], closures, allow)
                   if d in base]
        drivers = mt.driver_order(s["file"], drivers, secs, killed_by)
        work.append((name, s, drivers))
    queue = list(range(len(work)))
    trees_root = Path(tempfile.mkdtemp(prefix="d3s2-drive-"))
    excl = str(HERE.relative_to(mt.ROOT))

    def worker(w):
        tree = trees_root / f"w{w}"
        clone_tree(tree, excl)
        try:
            while True:
                with lock:
                    if not queue:
                        return
                    i = queue.pop(0)
                name, mut, drivers = work[i]
                # resume: a recorded kill or timeout decides the mutant
                prior = [done.get((name, d)) for d in drivers]
                if any(p and (p["hit"] or p["hit"] is None) for p in prior):
                    continue
                src = (tree / mut["file"]).read_text()
                lines = src.splitlines(True)
                k = mut["line"] - 1
                if k >= len(lines) or lines[k].rstrip("\n") != mut["old"]:
                    log(item=name, script="-", hit=False, verdict="SKIP-MOVED")
                    continue
                lines[k] = mut["new"] + "\n"
                new_src = "".join(lines)
                try:
                    ast.parse(new_src)
                except SyntaxError:
                    log(item=name, script="-", hit=False,
                        verdict="SKIP-UNPARSEABLE")
                    continue
                hidden = mt.invalidated_rows(budgets, mut["file"], src, new_src)
                for d in drivers:
                    if (name, d) in done:
                        continue
                    if mt.reach_skip(reaches.get(d), mut):
                        log(item=name, script=d, hit=False, reach_skip=True)
                        continue
                    path = tree / mut["file"]
                    rows = {p: p.read_text() for p in
                            (tree / rows_at / r for r in hidden) if p.is_file()}
                    path.write_text(new_src)
                    for p in rows:
                        p.unlink()
                    try:
                        args, env = mt.drive_spec(d, REF)
                        limit = max(a.timeout, int(3 * secs.get(d, 0)))
                        run = mt.run_script(d, tree, limit, args, env)
                    finally:
                        path.write_text(src)
                        for p, t in rows.items():
                            p.write_text(t)
                    hit = None if run.timed_out else bool(
                        run.rc != 0 and mt.failing_count(run) > 0)
                    log(item=name, anchor=mut["anchor"], script=d, hit=hit,
                        rc=run.rc, failed=run.failed,
                        checks=mt.failed_checks(run)[:6] if hit else [],
                        seconds=round(run.seconds, 1), hidden=len(hidden),
                        load1=round(os.getloadavg()[0], 2))
                    if hit or hit is None:
                        break
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                           cwd=mt.ROOT, capture_output=True)

    ts = [threading.Thread(target=worker, args=(w,)) for w in range(a.jobs)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00 (parent waits on children; no BLAS work)")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
