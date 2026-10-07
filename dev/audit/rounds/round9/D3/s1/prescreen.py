#!/usr/bin/env python3
"""D3.M2 pre-screen: apply one coordinator.py mutant in a private worktree, run its measured closure.

METRIC: per mutant, the number of scripts in coordinator.py's measured closure
  (tests/closures.json via `tests/closure.py select --files`, minus stress/edge/backtest,
  minus golden.py which GOLDEN_MODE=drift replaces by `env_drift.py --all <baseline>`)
  that exit non-zero -- `killed_by`. Key: the child's exit status, nothing else.
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s1/prescreen.py <CID|null> [--stop]
          CID from mutants.py (e.g. C0054); `null` runs the unmutated tree (the control: killed_by=0).
EXPECTED: null -> RESULT killed_by=0 count (exact). A survivor -> killed_by=0; a killed mutant -> >=1.
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (override with HPO_AUDIT_BASELINE)
MACHINE:  box B1 (4 vCPU cloud container, Linux 6.18), CPython 3.14.0rc2, node 22
ROOT:     the git repository of the working directory; the mutant is applied in a fresh
          `git worktree add --detach` under a mkdtemp root (never the tree it is run from),
          on top of an empty commit so env_drift/card_drift do not refuse a HEAD self-comparison.
PERTURBATION: the mutant itself is the one-line production edit; `null` is its control.

Per-script wall and child CPU are printed as RESULT lines too (provisional: box shared);
env_drift.py runs WITHOUT the thread pin in its environment so it keys to the shared
warmed baseline cache (~/.cache/heatpump_optimizer/drift-baseline), as BASELINE.md records.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import json
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path("tools/audit/round9/D3/s1")))
import mutants  # noqa: E402

BASELINE = os.environ.get("HPO_AUDIT_BASELINE", "1936d5ca72a06556eeed4e8e5bf3dea520e517e1")
TARGET = "custom_components/heatpump_optimizer/coordinator.py"
PRESCREEN_SKIP = {"tests/stress.py", "tests/edge.py", "tests/backtest.py", "tests/golden.py"}
PIN = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
       "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def closure_scripts(wt: Path) -> list[str]:
    out = subprocess.run([sys.executable, "tests/closure.py", "select", "--files", TARGET],
                         cwd=wt, capture_output=True, text=True).stdout
    run = re.findall(r"^\s+RUN\s+(\S+)", out, re.M)
    rec = json.loads((wt / "tests/closures.json").read_text())["recorded"]
    run = [s for s in run if s not in PRESCREEN_SKIP]
    run.sort(key=lambda s: (s == "tests/env_drift.py", rec.get(s, {}).get("seconds", 0.0)))
    # card.mjs reads what plan_view.py writes
    if "tests/card.mjs" in run and "tests/plan_view.py" in run:
        run.remove("tests/card.mjs")
        run.insert(run.index("tests/plan_view.py") + 1, "tests/card.mjs")
    return run


def command(script: str) -> list[str]:
    if script.endswith(".mjs"):
        cmd = [shutil.which("node") or "/opt/node22/bin/node", script]
        if script == "tests/card_drift.mjs":
            cmd.append(BASELINE)
        return cmd
    cmd = [sys.executable, script]
    if script == "tests/env_drift.py":
        cmd += ["--all", BASELINE]
    return cmd


def main() -> int:
    cid = sys.argv[1]
    stop = "--stop" in sys.argv
    repo = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                               text=True, check=True).stdout.strip())
    tmp = Path(tempfile.mkdtemp(prefix="d3s1-"))
    wt = tmp / "wt"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(wt), BASELINE], cwd=repo, check=True)
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    killed: list[str] = []
    rows = []
    try:
        subprocess.run(["git", "-c", "user.name=audit", "-c", "user.email=audit@local", "commit",
                        "-q", "--allow-empty", "-m", "d3s1 anchor"], cwd=wt, check=True)
        src = (wt / TARGET).read_text()
        if cid != "null":
            cand = next(c for c in mutants.candidates(src) if c["id"] == cid)
            new = mutants.apply(src, cand)
            assert new != src
            (wt / TARGET).write_text(new)
            diff = subprocess.run(["git", "diff", "--", TARGET], cwd=wt, capture_output=True, text=True).stdout
            print("MUTANT", json.dumps(cand))
            print(diff)
        env = dict(os.environ)
        env["PYTHONPATH"] = "tests/hastub"
        env["HPO_PLANDATA"] = str(tmp / "plandata")
        scripts = closure_scripts(wt)
        print("CLOSURE", " ".join(scripts))
        for s in scripts:
            e = dict(env)
            if s == "tests/env_drift.py":
                for k in PIN:
                    e.pop(k, None)
            r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
            w0 = time.monotonic()
            p = subprocess.run(command(s), cwd=wt, env=e, capture_output=True, text=True)
            wall = time.monotonic() - w0
            r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
            tail = (p.stdout + p.stderr).strip().splitlines()[-6:]
            fails = [ln for ln in (p.stdout + p.stderr).splitlines()
                     if re.search(r"\b(FAIL|FAILED|Traceback|AssertionError|DRIFT)\b", ln)][:8]
            rows.append({"script": s, "rc": p.returncode, "wall_s": round(wall, 1), "cpu_s": round(cpu, 1)})
            print(f"SCRIPT {s} rc={p.returncode} wall={wall:.1f}s cpu={cpu:.1f}s")
            if p.returncode != 0:
                killed.append(s)
                for ln in fails or tail:
                    print("   |", ln[:220])
                if stop:
                    break
            sys.stdout.flush()
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=repo)
        shutil.rmtree(tmp, ignore_errors=True)
    tp, tt = time.process_time() - t_proc0, time.thread_time() - t_thr0
    for r in rows:
        key = r["script"].replace("tests/", "").replace(".", "_")
        print(f"RESULT wall_{key}={r['wall_s']} s")
        print(f"RESULT cpu_{key}={r['cpu_s']} s")
    print(f"RESULT scripts_run={len(rows)} count")
    print(f"RESULT killed_by={len(killed)} count")
    print("KILLERS", ",".join(killed) or "-")
    print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = next((ln.split()[1] for ln in fh if ln.startswith("pswpin ")), "0")
    except OSError:
        sw = "0"
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
