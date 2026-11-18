#!/usr/bin/env python3
"""D3-s1 M5 (resume run): the quiet-box gate table and the traced reach of the
four scripts the local run left unmeasured.

Metric (one line per script): CPU seconds (RUSAGE_CHILDREN delta) and wall
seconds of one solo, gate-shaped run on the unmutated baseline tree, against
tests/closures.json `recorded.seconds`; with `--trace`, the run carries the
gate's own reach hook (tests/mutation_table.py:REACH_HOOK) and the row adds,
per cell file in the script's closure, the executed-line count, whether it was
read as text, and the processes started/recorded -- the closure-over-
approximation test (D3.M5 (d)/(e)): a closure edge to a cell file the traced
run neither executes nor reads is an edge that forces the script for nothing.

Invocation per script mirrors tests/run.sh: python scripts bare,
env_drift.py --all <ref>, stress.py with GOLDEN_REF=<ref>, card.mjs under node,
card_drift.mjs <ref>; <ref> = HEAD^1 of the worker tree (its custom_components/
is byte-identical to the baseline).

Instrumented symbol: tests/closures.json `closures`/`recorded` against
mutation_table.collect() of each traced run.
Perturbation: `--drop-closure FILE` adds FILE (a cell file the script does not
list) to the compared closure: its over-approximated-edge count rises by 1 for
every script that neither executes nor reads FILE (direction up); the identity
run is the null control.

Run (seat worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/r2/m5_gate_table.py [--scripts a,b] [--trace] [--out FILE]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64 (8 cores), shared box.
Every seconds figure is provisional: true (shared machine, load1 recorded per row).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import resource
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
REF = "HEAD^1"


def command(s: str) -> tuple[list[str], dict[str, str]]:
    node = shutil.which("node") or "node"
    if s == "tests/env_drift.py":
        return [sys.executable, s, "--all", REF], {}
    if s in ("tests/stress.py", "tests/golden.py"):
        return [sys.executable, s], {"GOLDEN_REF": REF}
    if s == "tests/card_drift.mjs":
        return [node, s, REF], {}
    if s.endswith(".mjs"):
        return [node, s], {}
    return [sys.executable, s], {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--drop-closure")
    ap.add_argument("--tree", default=str(Path(tempfile.gettempdir()) / "d3s1-workers" / "w5"))
    ap.add_argument("--out")
    ap.add_argument("--timeout", type=int, default=14400)
    a = ap.parse_args()
    clos = mt.load_closures()
    rec = mt.recorded_seconds()
    scripts = a.scripts.split(",") if a.scripts else sorted(rec)
    # run.sh order: plan_view.py writes the payload card.mjs/card_drift.mjs read.
    scripts.sort(key=lambda s: (s.endswith(".mjs"), s != "tests/plan_view.py"))
    t = Path(a.tree)
    if not (t / ".git").exists():
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(t), "HEAD"],
                       cwd=mt.ROOT, check=True)
    exe = {r: mt.executable_lines(mt.ROOT / r) for r in RELS}
    over_total = 0
    for s in scripts:
        cmd, extra = command(s)
        env = {**os.environ, "PYTHONPATH": "tests/hastub", **extra}
        d = Path(tempfile.mkdtemp(prefix="d3s1-gt-"))
        if a.trace:
            henv = mt.hook_env(d)
            env.update(henv)
            env["PYTHONPATH"] = mt.traced_pythonpath(henv, "tests/hastub")
        l0 = os.getloadavg()[0]
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, cwd=t, env=env, capture_output=True, text=True,
                               timeout=a.timeout)
            rc, out = p.returncode, p.stdout + p.stderr
        except subprocess.TimeoutExpired:
            rc, out = "TIMEOUT", ""
        wall = time.monotonic() - t0
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
        row = {"script": s, "rc": rc, "cpu_s": round(cpu, 1), "wall_s": round(wall, 1),
               "recorded_s": rec.get(s), "cpu_over_recorded": (round(cpu / rec[s], 2) if rec.get(s) else None),
               "load1_start": round(l0, 1), "load1_end": round(os.getloadavg()[0], 1),
               "nproc": os.cpu_count(), "provisional": True,
               "tail": out[-400:]}
        if a.trace:
            reach = mt.collect(d)
            reach["rc"] = rc if isinstance(rc, int) else None
            row["reach_problems"] = mt.reach_problems(reach)[:3]
            row["processes"] = reach["processes"]
            cells = {}
            listed = [r for r in RELS if r in clos.get(s, ())]
            if a.drop_closure and a.drop_closure not in listed:
                listed.append(a.drop_closure)
            over = []
            for r in listed:
                hit = len(set(reach["hits"].get(r, ())) & exe[r])
                read = r in reach["reads"]
                cells[r.rsplit("/", 1)[-1]] = {"hit_lines": hit, "executable": len(exe[r]), "read": read}
                if not hit and not read:
                    over.append(r.rsplit("/", 1)[-1])
            row["cells"] = cells
            row["over_approx"] = over
            row["closure_files"] = len(clos.get(s, ()))
            allhit = {f for f, v in reach["hits"].items() if v}
            row["closure_files_executed_or_read"] = sum(
                1 for f in clos.get(s, ()) if f in allhit or f in reach["reads"])
            over_total += len(over)
        shutil.rmtree(d, ignore_errors=True)
        print(json.dumps(row), flush=True)
        if a.out:
            with open(a.out, "a") as f:
                f.write(json.dumps(row) + "\n")
        k = s.rsplit("/", 1)[-1]
        print(f"RESULT {k}_cpu_s={cpu:.1f} (provisional) wall_s={wall:.1f} recorded_s={rec.get(s)}", flush=True)
    if a.trace:
        print(f"RESULT over_approx_cell_edges={over_total}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
