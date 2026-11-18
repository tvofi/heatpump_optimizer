#!/usr/bin/env python3
"""D3-s1 M5(a): the quiet-box gate table -- each closure script alone, as the gate runs it.

Metric (one line): per gate script S whose tests/closures.json closure holds a
D3-s1 cell file (enumerate.py --scripts), the wall seconds and child CPU
seconds (getrusage RUSAGE_CHILDREN delta, user+sys) of ONE unmutated run of S,
alone on the box (GATE_JOBS=1: one script at a time, nothing else running),
invoked as tests/run.sh invokes it in GOLDEN_MODE=drift (env_drift.py --all
<ref>, stress.py with GOLDEN_REF exported, card_drift.mjs <ref>, node for the
.mjs programs, bare otherwise), against closures.json `recorded.seconds`;
ratio = wall / recorded. Count key: the measured run of the script itself
(mutation_table.run_script's own subprocess), never the recorded table.

Instrumented symbol: tests/mutation_table.py:run_script (the gate lane's own
runner) and tests/mutation_table.py:recorded_seconds (closures.json's table).
Perturbation: `--slow S=<n>` re-runs script S with a sitecustomize that sleeps
n seconds at interpreter start (every Python process S starts) -> S's wall
rises by >= n (direction up), its CPU stays flat; the identity run is the null.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_gate_table.py [--scripts a,b] [--ref HEAD^1] [--slow S=n]
Ref: HEAD^1 (2c84a85c, production byte-identical to the baseline; env_drift
refuses ref == HEAD). Writes state/gate_table.jsonl (appends) and a private
temp root (worker tree, HPO_PLANDATA, the node plan payload).
Expected: exact pass/fail per script (rc, failed); seconds are provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
Machine: box D3-m5, Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz, quiet.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import platform
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
RELS = {mt.PKG + c + ".py" for c in CELLS}


def cell_scripts() -> list[str]:
    clos = mt.load_closures()
    # The Node programs read plan_view.py's payload (closure.py's PRODUCERS
    # edge; run.sh runs plan_view.py first): they go last, sharing HPO_PLANDATA.
    return sorted((s for s, fs in clos.items() if any(f in RELS for f in fs)),
                  key=lambda s: (s.endswith(".mjs"), s))


def cpu_model() -> str:
    try:
        for ln in open("/proc/cpuinfo"):
            if ln.startswith("model name"):
                return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def swapins() -> int:
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                return int(ln.split()[1])
    except OSError:
        pass
    return 0


def invocation(s: str, ref: str, root: Path) -> tuple[list[str], dict]:
    env = {"PYTHONPATH": "tests/hastub", "HPO_PLANDATA": str(root / "plandata.json"),
           "GOLDEN_MODE": "drift", "GOLDEN_REF": ref}
    if s.endswith(".mjs"):
        args = [s, ref] if s.endswith("card_drift.mjs") else [s]
        return ["node", *args], env
    a, e = mt.drive_spec(s, ref)
    return [sys.executable, s, *a], {**env, **e}


def tree(root: Path) -> Path:
    t = Path(tempfile.gettempdir()) / "d3s1-workers" / "gt"
    if not (t / ".git").exists():
        t.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(t), "HEAD"],
                       cwd=mt.ROOT, check=True)
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts")
    ap.add_argument("--ref", default="HEAD^1")
    ap.add_argument("--slow", help="S=n: sleep n s at start of every Python process of S")
    ap.add_argument("--out", default=str(HERE / "state" / "gate_table.jsonl"))
    a = ap.parse_args()
    scripts = a.scripts.split(",") if a.scripts else cell_scripts()
    slow_s, slow_n = (a.slow.split("=") + [None])[:2] if a.slow else (None, None)
    rec = mt.recorded_seconds()
    root = Path(tempfile.mkdtemp(prefix="d3s1-gt-"))
    t = tree(root)
    nproc, cpu = os.cpu_count(), cpu_model()
    sw0 = swapins()
    print("script\trc\tfailed\twall_s\tcpu_s\trecorded_s\twall/recorded\tload1_before")
    for s in scripts:
        cmd, env = invocation(s, a.ref, root)
        env = {**os.environ, **env}
        if s == slow_s:
            hook = root / "_slow"
            hook.mkdir(exist_ok=True)
            (hook / "sitecustomize.py").write_text(f"import time\ntime.sleep({float(slow_n)})\n")
            env["PYTHONPATH"] = f"{hook}{os.pathsep}{env['PYTHONPATH']}"
        ld = os.getloadavg()[0]
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, cwd=t, env=env, capture_output=True, text=True,
                               timeout=mt.driver_timeout(1800, 4 * rec.get(s, 600)))
            rc, out, timed = p.returncode, p.stdout, False
        except subprocess.TimeoutExpired:
            rc, out, timed = mt.TIMEOUT_RC, "", True
        wall = time.monotonic() - t0
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu_s = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
        failed = mt.failing_count(mt.ScriptRun(rc, 0, wall, out, ""))
        rs = rec.get(s, 0.0)
        row = {"script": s, "cmd": " ".join(cmd[1:] if cmd[0] == sys.executable else cmd),
               "rc": rc, "failed": failed, "timed_out": timed,
               "wall_s": round(wall, 1), "cpu_s": round(cpu_s, 1), "recorded_s": rs,
               "wall_over_recorded": round(wall / rs, 2) if rs else None,
               "cpu_over_wall": round(cpu_s / wall, 2) if wall else None,
               "nproc": nproc, "cpu_model": cpu, "load1_before": round(ld, 2),
               "load1_after": round(os.getloadavg()[0], 2),
               "slow": a.slow if s == slow_s else None, "provisional": True,
               "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        print(f"{s}\t{rc}\t{failed}\t{wall:.1f}\t{cpu_s:.1f}\t{rs:.1f}\t"
              f"{row['wall_over_recorded']}\t{ld:.2f}", flush=True)
        with open(a.out, "a") as f:
            f.write(json.dumps(row) + "\n")
        key = s.rsplit("/", 1)[-1].replace(".", "_")
        print(f"RESULT {key}_wall_s={wall:.1f} s (provisional)")
        print(f"RESULT {key}_cpu_s={cpu_s:.1f} s (provisional)")
        print("RESULT thread_factor=1.00", flush=True)
    print(f"RESULT scripts={len(scripts)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT swapins={swapins() - sw0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
