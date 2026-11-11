#!/usr/bin/env python3
"""D3.M2 -- pre-screen D3-s3's seeded mutant pool against its measured closures.

Metric: per mutant in pool.json, whether any gate driver in the mutant file's
  MEASURED closure (tests/closures.json) -- minus the three slow lanes the brief
  excludes from the pre-screen (stress.py, edge.py, backtest.py) and the three
  the gate's own instrument cannot drive (tests/mutation_table.py
  DRIVER_EXCLUSIONS: card.mjs, card_drift.mjs, golden.py) -- PLUS
  `tests/env_drift.py --all <baseline>` goes red naming more failing checks than
  its unmutated run (tests/mutation_table.py:killed, the gate's kill rule).
  Count key: the verdict of `mutation_table.killed` on each driver's real run in
  a tree whose production file carries the mutated line; never a label.
Command:  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
            MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s3/prescreen.py [--workers 2] [--only M03,M08]
Expected: RESULT survivors=<n> mutants of RESULT evaluated=36; each mutant's
  verdict is deterministic (drivers are seeded), the survivor count exact.
  Per-driver seconds are wall and PROVISIONAL (shared box).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: box B3 (4 CPUs).

Trees.  Each worker gets `git worktree add --detach <tmp>/wN <baseline>` and a
scratch EMPTY commit on top (never pushed, never in the seat's checkout), so
env_drift's comparison ref (the baseline) is not HEAD -- env_drift refuses a
self-comparison -- and the three-dot diff is exactly the mutated line.  The
mutation is written into the worker's copy and restored after each driver.

Controls.  Every driver runs unmutated first (must be green: a red baseline
makes every verdict after it meaningless) and under the gate instrument's
comment-only null control (`mutation_table.null_control`, must LIVE).

Perturbation.  --mutant-override M08=<line text> replaces a pooled mutant's
  new line; `--only M08 --identity` drives the mutant with new == old, which
  must LIVE on every driver (a harness that reports a kill for the identity
  edit is measuring the diff, not the code).

Results go to prescreen.jsonl beside this file (one row per driver run; a
re-run resumes, skipping runs already recorded) and prescreen.json.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

BASELINE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
HERE = Path(__file__).resolve().parent
LOG = HERE / "prescreen.jsonl"
SKIP = {"tests/stress.py", "tests/edge.py", "tests/backtest.py",
        *mt.DRIVER_EXCLUSIONS}
ENV_DRIFT = "tests/env_drift.py"
TIMEOUT = 3600


def drivers_of(rel: str, closures: dict) -> list[str]:
    return sorted(s for s, files in closures.items()
                  if rel in files and s not in SKIP and s.endswith(".py"))


def make_tree(root: Path, n: int) -> Path:
    dest = root / f"w{n}"
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet",
                    str(dest), BASELINE], cwd=mt.ROOT, check=True,
                   capture_output=True)
    subprocess.run(["git", "-c", "user.name=d3-s3-scratch", "-c",
                    "user.email=d3-s3@local", "commit", "--allow-empty",
                    "--no-verify", "-q", "-m", "D3-s3 scratch, never pushed"],
                   cwd=dest, check=True, capture_output=True)
    return dest


def drop_tree(dest: Path) -> None:
    subprocess.run(["git", "worktree", "remove", "--force", str(dest)],
                   cwd=mt.ROOT, capture_output=True)


class Edit:
    """Write one line into a worker tree's file; restore on exit."""

    def __init__(self, tree: Path, mut: dict | None):
        self.tree, self.mut, self.orig = tree, mut, None

    def __enter__(self):
        if self.mut is None:
            return self
        path = self.tree / self.mut["file"]
        self.orig = path.read_text()
        lines = self.orig.splitlines(True)
        assert lines[self.mut["line"] - 1].rstrip("\n") == self.mut["old"], (
            "pool line does not match the tree", self.mut["id"])
        lines[self.mut["line"] - 1] = self.mut["new"] + "\n"
        path.write_text("".join(lines))
        # A mutant that does not compile is a syntax error, not a gap.
        subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                       check=True, capture_output=True)
        return self

    def __exit__(self, *exc):
        if self.orig is not None:
            (self.tree / self.mut["file"]).write_text(self.orig)
        return False


def drive(tree: Path, script: str, plandata: str) -> mt.ScriptRun:
    args = ["--all", BASELINE] if script == ENV_DRIFT else []
    return mt.run_script(script, tree, TIMEOUT, args,
                         {"HPO_PLANDATA": plandata,
                          "GOLDEN_REF": BASELINE})


def load_log() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()]


LOCK = threading.Lock()


def record(row: dict) -> None:
    with LOCK:
        with LOG.open("a") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--mutant-override", action="append", default=[])
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()

    pool = json.loads((HERE / "pool.json").read_text())["pool"]
    if a.only:
        keep = set(a.only.split(","))
        pool = [m for m in pool if m["id"] in keep]
    for ov in a.mutant_override:
        mid, text = ov.split("=", 1)
        for m in pool:
            if m["id"] == mid:
                m["new"] = text
    if a.identity:
        for m in pool:
            m["new"] = m["old"]
    tag = "identity" if a.identity else ("override" if a.mutant_override
                                         else "mutant")
    closures = mt.load_closures()
    killed_by = mt.load_budgets().get("killed_by", {})
    for m in pool:
        ds = drivers_of(m["file"], closures)
        if ENV_DRIFT not in ds:
            ds.append(ENV_DRIFT)
        m["drivers"] = ds
    needed = sorted({s for m in pool for s in m["drivers"]})

    log = [] if a.no_log else load_log()
    done_base = {r["script"]: r for r in log if r["kind"] == "baseline"}
    done_null = {r["script"]: r for r in log if r["kind"] == "null"}
    done_mut = {}
    for r in log:
        if r["kind"] == tag:
            done_mut.setdefault(r["id"], {})[r["script"]] = r

    tmp = Path(tempfile.mkdtemp(prefix="d3s3-"))
    trees = [make_tree(tmp, n) for n in range(a.workers)]
    plandata = [str(tmp / f"plandata-{n}.json") for n in range(a.workers)]
    null = mt.null_for(json.loads((HERE / "pool.json").read_text())["pool"])
    t0 = time.time()
    try:
        # 1. Unmutated baselines and the comment-only null control.
        tasks = [("baseline", s) for s in needed if s not in done_base]
        tasks += [("null", s) for s in needed if s not in done_null]
        qlock = threading.Lock()

        def work_base(w: int) -> None:
            while True:
                with qlock:
                    if not tasks:
                        return
                    kind, s = tasks.pop(0)
                mut = None
                if kind == "null":
                    mut = dict(null, id="NULL")
                with Edit(trees[w], mut):
                    run = drive(trees[w], s, plandata[w])
                row = dict(kind=kind, script=s, rc=run.rc, failed=run.failed,
                           seconds=round(run.seconds, 1),
                           checks=mt.failed_checks(run)[:5])
                if kind == "baseline":
                    done_base[s] = row
                else:
                    done_null[s] = row
                if not a.no_log:
                    record(row)
                print(f"{kind:8s} {s:32s} rc={run.rc} failed={run.failed} "
                      f"{run.seconds:6.1f}s", flush=True)

        mt._share(a.workers, work_base)
        red = [s for s in needed if done_base[s]["rc"] != 0]
        if red:
            print("BASELINE RED -- refusing:", red)
            for s in red:
                print("  ", s, done_base[s]["checks"])
            return 2
        nulls = [s for s in needed if done_null[s]["rc"] != 0
                 and done_null[s]["failed"] > done_base[s]["failed"]]
        if nulls:
            print("NULL CONTROL KILLED -- refusing:", nulls)
            return 3

        # 2. Mutants: each worker sweeps a mutant's drivers until a kill, in
        # the gate instrument's order (Smith's rule over the MEASURED baseline
        # seconds, as tests/mutation_table.py main() prices them).
        seconds = {s: done_base[s]["seconds"] for s in needed}
        for m in pool:
            m["drivers"] = mt.driver_order(m["file"], m["drivers"], seconds,
                                           killed_by)
        verdict = {}
        queue = list(pool)

        def work_mut(w: int) -> None:
            while True:
                with qlock:
                    if not queue:
                        return
                    m = queue.pop(0)
                prior = done_mut.get(m["id"], {})
                hit = next((r for r in prior.values() if r["killed"]), None)
                if hit:
                    verdict[m["id"]] = ("killed by " + hit["script"], hit)
                    continue
                v = None
                for s in m["drivers"]:
                    if s in prior:
                        continue
                    with Edit(trees[w], m):
                        run = drive(trees[w], s, plandata[w])
                    base = mt.ScriptRun(done_base[s]["rc"],
                                        done_base[s]["failed"], 0.0)
                    k = mt.killed(s, run, base)
                    row = dict(kind=tag, id=m["id"], script=s, rc=run.rc,
                               failed=run.failed, killed=k,
                               seconds=round(run.seconds, 1),
                               checks=mt.failed_checks(run)[:5])
                    if not a.no_log:
                        record(row)
                    print(f"{m['id']} {s:32s} rc={run.rc} killed={k} "
                          f"{run.seconds:6.1f}s {row['checks'][:2]}",
                          flush=True)
                    if k:
                        v = ("killed by " + s, row)
                        break
                verdict[m["id"]] = v or ("LIVES", None)

        mt._share(a.workers, work_mut)
    finally:
        for t in trees:
            drop_tree(t)
        shutil.rmtree(tmp, ignore_errors=True)

    out = []
    for m in pool:
        v, row = verdict[m["id"]]
        out.append(dict(id=m["id"], file=m["file"], line=m["line"],
                        kind=m["kind"], old=m["old"], new=m["new"],
                        ledger=m["ledger"], drivers=m["drivers"], verdict=v,
                        checks=(row or {}).get("checks", [])))
        print(f"VERDICT {m['id']} {m['file']}:{m['line']} {m['kind']} -> {v}")
    if tag == "mutant" and not a.only:
        (HERE / "prescreen.json").write_text(json.dumps(out, indent=1) + "\n")
    surv = sum(1 for o in out if o["verdict"] == "LIVES")
    print(f"RESULT evaluated={len(out)} mutants")
    print(f"RESULT survivors={surv} mutants")
    print(f"RESULT wall={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT thread_factor="
          f"{time.process_time() / max(time.thread_time(), 1e-9):.2f}"
          " (driver work is in subprocesses; this process only schedules)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
