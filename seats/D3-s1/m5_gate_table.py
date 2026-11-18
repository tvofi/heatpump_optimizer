#!/usr/bin/env python3
"""D3-s1 M5(a)/(e): the quiet-box gate table -- per closure script, CPU and wall.

Metric (one line): for each gate script whose tests/closures.json closure holds
a D3-s1 cell file, the wall seconds (time.monotonic) and CPU seconds (the
child's os.wait4 rusage, utime+stime, which includes every descendant it
waited for) of ONE gate-shaped invocation, run strictly one at a time
(GATE_JOBS=1 semantics) in a fresh detached worktree of HEAD, against
tests/closures.json `recorded.seconds`; ratio = wall / recorded.

Gate shape (tests/run.sh, GOLDEN_MODE unset = strict, GOLDEN_REF=HEAD^1):
`tests/mutation_table.py:drive_spec` arguments for every .py script
(env_drift.py `--all HEAD^1`, the drift/mutation-lane form; stress.py with
GOLDEN_REF in the environment); golden.py with GOLDEN_MODE=strict exported as
run.sh exports it; the two .mjs run under `node` AFTER their producer
tests/plan_view.py (closure.py PRODUCERS), which is timed as its own
`producer:` row and not added to theirs; card_drift.mjs gets HEAD^1. Extra
arms: `tests/env_drift.py[strict]` = `env_drift.py HEAD^1` (run.sh's strict
lane form, five fixtures) and `tests/env_drift.py[nocache]` = `--all HEAD^1`
with DRIFT_NO_CACHE=1 (both captures paid).

Instrumented symbol: tests/closures.json `recorded` (read through
tests/mutation_table.py:recorded_seconds) against the measured invocation of
each script; the scripts' own process trees are what is timed.
Perturbation: `--cpu-burn S` adds a deterministic S-second busy loop to the
harness's own PYTHONSTARTUP-free wrapper of every .py row (a `-c` prelude
before runpy), so every .py row's cpu_s and wall_s go UP by about S and the
.mjs rows stay flat -- the instrument sees cost it is handed. The identity run
(no flag) is the null control.

Run (repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_gate_table.py [--scripts a,b] [--out FILE] [--cpu-burn S]
Writes only under $TMPDIR (worktree, HPO_PLANDATA, logs).
Expected: every wall/CPU figure is PROVISIONAL (judge re-takes it on a quiet
container); counts of rows and rc values are exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-m5 (Linux
x86_64, nproc 4, Intel Xeon @ 2.10GHz, venv-ci CPython), alone on the box.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import platform
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
RELS = {mt.PKG + c + ".py" for c in CELLS}
REF = "HEAD^1"


def cell_scripts() -> list[str]:
    clos = mt.load_closures()
    return sorted(s for s, fs in clos.items() if any(f in RELS for f in fs))


def swapins() -> int:
    try:
        for ln in Path("/proc/vmstat").read_text().splitlines():
            if ln.startswith("pswpin "):
                return int(ln.split()[1])
    except OSError:
        pass
    return 0


def cpu_model() -> str:
    try:
        for ln in Path("/proc/cpuinfo").read_text().splitlines():
            if ln.startswith("model name"):
                return ln.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def spec(row: str, burn: float) -> list[tuple[str, list[str], dict]]:
    """[(label, argv, extra_env)] for one table row (producer first)."""
    py = sys.executable
    pre = []
    if row.endswith(".mjs"):
        pre.append(("producer:tests/plan_view.py", [py, "tests/plan_view.py"], {}))
        args = [REF] if row == "tests/card_drift.mjs" else []
        return pre + [(row, ["node", row, *args], {})]
    script, arm = row, ""
    if "[" in row:
        script, arm = row[:-1].split("[")
    args, env = mt.drive_spec(script, REF)
    env = dict(env)
    if script == "tests/golden.py":
        env.update(GOLDEN_MODE="strict", GOLDEN_REF=REF)
    if arm == "strict":
        args = [REF]
    if arm == "nocache":
        env["DRIFT_NO_CACHE"] = "1"
    argv = [py, script, *args]
    if burn:
        prelude = (f"import time,runpy,sys;t=time.process_time()\n"
                   f"while time.process_time()-t<{burn}: pass\n"
                   f"sys.argv={[script, *args]!r};runpy.run_path({script!r},run_name='__main__')")
        argv = [py, "-c", prelude]
    return [(row, argv, env)]


def run_one(argv, env, cwd: Path, log: Path) -> dict:
    with open(log, "w") as fo:
        t0 = time.monotonic()
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=fo,
                             stderr=subprocess.STDOUT)
        _, status, ru = os.wait4(p.pid, 0)
        wall = time.monotonic() - t0
    p.returncode = os.waitstatus_to_exitcode(status)
    return {"rc": p.returncode, "wall_s": round(wall, 1),
            "cpu_s": round(ru.ru_utime + ru.ru_stime, 1),
            "maxrss_mb": round(ru.ru_maxrss / 1024, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts")
    ap.add_argument("--out")
    ap.add_argument("--cpu-burn", type=float, default=0.0)
    ap.add_argument("--keep-tree", action="store_true")
    a = ap.parse_args()
    rows = (a.scripts.split(",") if a.scripts else
            cell_scripts() + ["tests/env_drift.py[strict]",
                              "tests/env_drift.py[nocache]"])
    root = Path(tempfile.mkdtemp(prefix="d3s1-gatetable-"))
    tree = root / "tree"
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(tree),
                    "HEAD"], cwd=mt.ROOT, check=True)
    rec = mt.recorded_seconds()
    base_env = {**os.environ,
                "PYTHONPATH": str(tree / "tests" / "hastub"),
                "HPO_PLANDATA": str(root / "plandata"),
                "GOLDEN_REF": REF}
    base_env.pop("HPO_REACH_HOOK", None)
    nproc = os.cpu_count()
    cpu = cpu_model()
    print(f"# nproc={nproc} cpu={cpu!r} python={platform.python_version()} "
          f"tree={tree}")
    print("script\trc\twall_s\tcpu_s\tcpu/wall\tmaxrss_mb\trecorded_s\t"
          "wall/recorded\tload1_before\tload1_after")
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    sw0 = swapins()
    try:
        for row in rows:
            for label, argv, extra in spec(row, a.cpu_burn):
                env = {**base_env, **extra}
                l0 = os.getloadavg()[0]
                r = run_one(argv, env, tree,
                            root / (label.replace("/", "_").replace(":", "_") + ".log"))
                l1 = os.getloadavg()[0]
                script = label.split("[")[0].split(":")[-1]
                rs = rec.get(script) if not label.startswith("producer:") else rec.get(script)
                ratio = (r["wall_s"] / rs) if rs else None
                rowd = {"script": label, **r, "recorded_s": rs,
                        "wall_over_recorded": round(ratio, 2) if ratio else None,
                        "cpu_over_wall": round(r["cpu_s"] / r["wall_s"], 2) if r["wall_s"] else None,
                        "load1_before": round(l0, 2), "load1_after": round(l1, 2),
                        "nproc": nproc, "cpu_model": cpu,
                        "cpu_burn": a.cpu_burn, "provisional": True,
                        "log_tail": (root / (label.replace("/", "_").replace(":", "_") + ".log")).read_text(errors="replace")[-600:]}
                print(f"{label}\t{r['rc']}\t{r['wall_s']}\t{r['cpu_s']}\t"
                      f"{rowd['cpu_over_wall']}\t{r['maxrss_mb']}\t{rs}\t"
                      f"{rowd['wall_over_recorded']}\t{l0:.2f}\t{l1:.2f}", flush=True)
                if a.out:
                    with open(a.out, "a") as f:
                        f.write(json.dumps(rowd) + "\n")
                key = label.replace("producer:", "producer_").rsplit("/", 1)[-1]
                key = key.replace(".py", "").replace(".mjs", "_mjs").replace("[", "_").replace("]", "")
                print(f"RESULT {key}_wall_s={r['wall_s']} s (provisional)")
                print(f"RESULT {key}_cpu_s={r['cpu_s']} s (provisional)")
                print(f"RESULT {key}_rc={r['rc']}")
    finally:
        if not a.keep_tree:
            subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                           cwd=mt.ROOT, capture_output=True)
            shutil.rmtree(root, ignore_errors=True)
            subprocess.run(["git", "worktree", "prune"], cwd=mt.ROOT,
                           capture_output=True)
    tf = (time.process_time() - t_proc0) / max(time.thread_time() - t_thr0, 1e-9)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={tf:.2f}")
    print(f"RESULT swapins={swapins() - sw0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
