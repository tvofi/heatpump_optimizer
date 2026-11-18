#!/usr/bin/env python3
"""D3-s1 M5(d)/(e): which cell lines a gate script REALLY executes, children included.

Metric (one line): per script S and per D3-s1 cell file F in S's
tests/closures.json closure, the number of F's executable lines that any
Python process of S's gate-shaped run executed (sys.monitoring LINE events,
tests/mutation_table.py:REACH_HOOK), and whether S read F as text; a pair
with 0 executed lines and no read is an over-approximated closure edge.

Why a second tracer: tests/env_drift.py and tests/stress.py start their
production-executing children with PYTHONPATH rebuilt to `<tree>/tests/hastub`,
which drops mutation_table's PYTHONPATH-prepended hook (the processes are
counted but leave no record; D3-s1-01 judged that for env_drift). Here the
hook is written as `tests/hastub/sitecustomize.py` in a fresh worktree of HEAD
(untracked) AND in a synthetic comparison commit = HEAD^1's tree + that file
(production byte-identical to HEAD^1), passed as the script's ref, so every
child on either side records. `--plain` runs the gate's own tracing instead
(hook prepended to PYTHONPATH, ref HEAD^1) for the side-by-side.

Instrumented symbol: tests/mutation_table.py:REACH_HOOK / collect over each
script's processes; tests/closures.json `closures` for the edges.
Perturbation: `--plain` (the gate's own tracing) -> for tests/stress.py and
tests/env_drift.py the executed-line count of every cell file falls (to the
parent's own import-time lines), `recorded < started`; the hastub arm is the
fixed instrument. `--drop FILE` zeroes one file's hits -> over_approx_pairs
up by the number of scripts that executed it (identity = null).

Run (repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_trace_hastub.py --scripts tests/stress.py,tests/env_drift.py,tests/golden.py [--plain] [--drop FILE] [--out FILE]
Writes only under $TMPDIR. Exact counts; seconds provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-m5 (Linux
x86_64, nproc 4, Intel Xeon @ 2.10GHz), alone on the box.
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
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
RELS = [mt.PKG + c + ".py" for c in CELLS]


def synthetic_ref(tree: Path, root: Path, text: str) -> str:
    def g(*c, **k):
        return subprocess.run(["git", *c], cwd=tree, capture_output=True,
                              text=True, check=True, **k).stdout.strip()
    blob = g("hash-object", "-w", "--stdin", input=text)
    env_i = {**os.environ, "GIT_INDEX_FILE": str(root / "idx")}
    subprocess.run(["git", "read-tree", "HEAD^1"], cwd=tree, env=env_i, check=True)
    subprocess.run(["git", "update-index", "--add", "--cacheinfo",
                    f"100644,{blob},tests/hastub/sitecustomize.py"], cwd=tree,
                   env=env_i, check=True)
    t = subprocess.run(["git", "write-tree"], cwd=tree, env=env_i,
                       capture_output=True, text=True, check=True).stdout.strip()
    return subprocess.run(["git", "-c", "user.name=d3s1", "-c", "user.email=d3s1@invalid",
                           "commit-tree", t, "-p", g("rev-parse", "HEAD^1"), "-m",
                           "d3s1 reach ref: HEAD^1 + hastub reach hook"], cwd=tree,
                          capture_output=True, text=True, check=True).stdout.strip()


def gate_spec(s: str, ref: str) -> tuple[list[str], dict]:
    if s == "tests/golden.py":
        return [], {"GOLDEN_MODE": "strict", "GOLDEN_REF": ref}
    return mt.drive_spec(s, ref)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts", required=True)
    ap.add_argument("--plain", action="store_true")
    ap.add_argument("--drop")
    ap.add_argument("--out")
    a = ap.parse_args()
    clos = mt.load_closures()
    exe = {r: mt.executable_lines(mt.ROOT / r) for r in RELS}
    root = Path(tempfile.mkdtemp(prefix="d3s1-tracehs-"))
    tree = root / "tree"
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(tree),
                    "HEAD"], cwd=mt.ROOT, check=True)
    over_total, pairs_total = 0, 0
    try:
        ref = "HEAD^1"
        hookdir = root / "_hook"
        hookdir.mkdir()
        (hookdir / "sitecustomize.py").write_text(mt.REACH_HOOK)
        if not a.plain:
            (tree / "tests" / "hastub" / "sitecustomize.py").write_text(mt.REACH_HOOK)
            ref = synthetic_ref(tree, root, mt.REACH_HOOK)
            print(f"# synthetic ref {ref}")
        for s in a.scripts.split(","):
            out = root / ("rec-" + s.replace("/", "_"))
            out.mkdir()
            args, extra = gate_spec(s, ref)
            pp = "tests/hastub" if not a.plain else f"{hookdir}{os.pathsep}tests/hastub"
            env = {**os.environ, **extra, "PYTHONPATH": pp, "HPO_REACH_OUT": str(out),
                   "HPO_PLANDATA": str(root / "plan.json")}
            t0 = time.monotonic()
            p = subprocess.run([sys.executable, s, *args], cwd=tree, env=env,
                               capture_output=True, text=True, timeout=14400)
            wall = time.monotonic() - t0
            reach = mt.collect(out)
            reach["rc"] = p.returncode
            row = {"script": s, "arm": "plain" if a.plain else "hastub",
                   "rc": p.returncode, "wall_s": round(wall, 1), "provisional": True,
                   "processes": reach["processes"], "foreign": reach["foreign"][:8],
                   "untraced": reach["untraced"][:8],
                   "reach_problems": mt.reach_problems(reach), "files": {},
                   "stdout_tail": p.stdout[-600:], "stderr_tail": p.stderr[-600:]}
            over = []
            for r in RELS:
                if r not in clos.get(s, ()):
                    continue
                pairs_total += 1
                hits = set(reach["hits"].get(r, ())) & exe[r]
                if r == a.drop:
                    hits = set()
                read = r in reach["reads"]
                row["files"][r.rsplit("/", 1)[-1]] = {
                    "executed": len(hits), "executable": len(exe[r]), "read": read}
                if not hits and not read:
                    over.append(r.rsplit("/", 1)[-1])
            row["over_approx"] = over
            over_total += len(over)
            print(json.dumps({k: v for k, v in row.items() if k not in ("stdout_tail", "stderr_tail")}), flush=True)
            if a.out:
                with open(a.out, "a") as f:
                    f.write(json.dumps(row) + "\n")
            key = s.rsplit("/", 1)[-1].replace(".py", "")
            print(f"RESULT {key}_cell_lines_executed={sum(v['executed'] for v in row['files'].values())}")
            print(f"RESULT {key}_procs_started={reach['processes']['started']} recorded={reach['processes']['recorded']}")
            print(f"RESULT {key}_over_approx_pairs={len(over)}")
            print(f"RESULT {key}_wall_s={wall:.1f} s (provisional)")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                       cwd=mt.ROOT, capture_output=True)
        shutil.rmtree(root, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=mt.ROOT, capture_output=True)
    print(f"RESULT closure_pairs={pairs_total}")
    print(f"RESULT over_approx_pairs={over_total}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
