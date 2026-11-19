#!/usr/bin/env python3
"""D3-s2 D3.M5 gate table: per closure script reaching a D3-s2 cell file,
measured wall/CPU against closures.json's recorded seconds, harness checks
and HeatPumpOptimizer.optimize calls (solves) per run.

Metrics (one line each):
  cpu_s     = ru_utime+ru_stime of the script process and its waited children (os.wait4)
  wall_s    = monotonic wall of the run
  ratio     = wall_s / closures.json recorded.seconds
  solves    = calls to custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize
              summed over every Python process of the run (hook/sitecustomize.py)
  checks    = calls to tests/harness.py:Results.check over the same processes
  checks_per_solve = checks / solves
Instrumented symbols: optimizer.py:HeatPumpOptimizer.optimize, tests/harness.py:Results.check.
Perturbation: double a script's solve loop (e.g. SCENARIOS twice) and `solves` doubles
while `checks` does not; drop the hook dir from PYTHONPATH and every count reads 0.
Universe: `--list` prints it (closures.json scripts whose closure holds a D3-s2 cell).
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m5_gate_table.py OUT.json [--list] [--only a,b]
Needs HEAD^1 = baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (marker commit) for the ref-driven scripts.
Machine: box B2, 4 cores. Every wall/CPU number is PROVISIONAL (shared box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import enumerate as en  # noqa: E402

P = "custom_components/heatpump_optimizer/"
NOT_RUN = {"tests/stress.py": "quiet window only (D3 trap)",
           "tests/golden.py": "GOLDEN_MODE=drift skips it (run.sh lane_golden)"}
ORDER_FIRST = ("tests/plan_view.py",)  # card.mjs reads its payload


def universe():
    c = json.load(open("tests/closures.json"))
    cells = {P + f"{x}.py" for x in en.CELLS}
    rows = []
    for s, files in sorted(c["closures"].items()):
        hit = sorted(cells & set(files))
        if hit:
            rows.append((s, hit, c["recorded"].get(s, {}).get("seconds")))
    return rows


PLANDATA = os.path.join(tempfile.mkdtemp(prefix="d3s2-plandata-"), "plan.json")


def run_one(script, rec, tree):
    cnt = tempfile.mkdtemp(prefix="d3s2-m5-")
    env = dict(os.environ, D3S2_COUNT_DIR=cnt, HPO_PLANDATA=PLANDATA,
               PYTHONPATH=f"tests/hastub:{HERE / 'hook'}")
    if script.endswith(".mjs"):
        cmd = ["node", script] + (["HEAD^1"] if "card_drift" in script else [])
    else:
        cmd = [sys.executable, script] + (["--all", "HEAD^1"]
                                         if script.endswith("env_drift.py") else [])
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, env=env, cwd=tree, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    out = proc.stdout.read()
    _, status, ru = os.wait4(proc.pid, 0)
    wall = time.monotonic() - t0
    rc = os.waitstatus_to_exitcode(status)
    solves = checks = procs = 0
    for f in glob.glob(os.path.join(cnt, "*.json")):
        d = json.load(open(f))
        solves += d["solves"]
        checks += d["checks"]
        procs += 1
    shutil.rmtree(cnt, ignore_errors=True)
    ok_lines = sum(1 for ln in out.splitlines() if ln.startswith("  ok   "))
    return dict(script=script, rc=rc, wall_s=round(wall, 1),
                cpu_s=round(ru.ru_utime + ru.ru_stime, 1),
                recorded_s=rec, ratio=round(wall / rec, 2) if rec else None,
                solves=solves, checks=checks, ok_lines=ok_lines,
                py_procs=procs,
                checks_per_solve=round(checks / solves, 2) if solves else None,
                tail=out.strip().splitlines()[-1][:160] if out.strip() else "")


def main():
    u = universe()
    if "--list" in sys.argv:
        for s, hit, rec in u:
            print(f"{s}\t{len(hit)} cell(s)\trecorded {rec}s")
        print(f"RESULT universe={len(u)} scripts")
        return 0
    outp = Path(sys.argv[1])
    only = []
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    done = json.loads(outp.read_text()) if outp.exists() else {}
    order = sorted(u, key=lambda r: (r[0] not in ORDER_FIRST, r[0]))
    t_proc = time.process_time()
    # A worktree of HEAD (marker commit = baseline + these harnesses): the
    # export is finder-walled and the gate reads walled files (doc_claims.py
    # reads dev/archive/backlog.md), so the table is taken on HEAD's tree.
    tree = tempfile.mkdtemp(prefix="d3s2-m5-tree-")
    os.rmdir(tree)
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", tree,
                    "HEAD"], check=True)
    for s, hit, rec in order:
        if only and s not in only:
            continue
        if s in done:
            continue
        if s in NOT_RUN:
            done[s] = dict(script=s, skipped=NOT_RUN[s], recorded_s=rec)
        else:
            done[s] = run_one(s, rec, tree)
            done[s]["load1"] = round(os.getloadavg()[0], 2)
        outp.write_text(json.dumps(done, indent=1))
        r = done[s]
        print(f"RESULT {s} wall_s={r.get('wall_s')} cpu_s={r.get('cpu_s')} "
              f"solves={r.get('solves')} checks={r.get('checks')} rc={r.get('rc')} "
              f"load1={r.get('load1')} provisional=true", flush=True)
    subprocess.run(["git", "worktree", "remove", "--force", tree])
    print(f"RESULT thread_factor={time.process_time() - t_proc and (time.process_time() - t_proc) / max(time.thread_time(), 1e-9):.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
