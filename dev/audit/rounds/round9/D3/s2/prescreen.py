#!/usr/bin/env python3
"""D3-s2 round 9, steps D3.M2/M3/M5: pre-screen pool.json's mutants against their measured closures.

Metric: per mutant, which closure driver KILLS it (tests/mutation_table.py:killed -- red AND more
  failing checks than the unmutated baseline run of the same driver), or SURVIVED when none does.
  Per driver on the unmutated baseline: wall s, child CPU s (os.wait4 rusage), checks asserted
  (ok+FAIL lines / ALL N PASSED), and HeatPumpOptimizer.optimize calls (solves) counted by a
  sitecustomize hook -> assertions per solve.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/prescreen.py
          [--only M03,M07] [--jobs 2] [--all-drivers]
          env: D3S2_POOL=<pool file> (default pool.json), D3S2_ORDER=measured (cheapest measured first)
Expected: RESULT survivors=<k> of 32 (count, exact given the same drivers and ref); every
  baseline driver green; RESULT null_control=LIVES. Wall/CPU numbers are provisional.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B2 (4-CPU Linux container).
Drivers: tests/closures.json closure of the mutant's file, minus stress.py/edge.py/backtest.py
  (brief D3.M2), card_drift.mjs (reads card source + ref only; no production input) and golden.py
  (its default mode IS the env_drift step: tests/mutation_table.py:DRIVER_EXCLUSIONS); card.mjs is
  run after plan_view.py with a private HPO_PLANDATA; env_drift.py runs `--all <REF>`.
REF: the baseline SHA is this worktree's HEAD and env_drift.py refuses a ref resolving to HEAD
  (SELF-COMPARISON), so REF defaults to HEAD^1 (8cca77bc), which differs from the baseline only
  in the release stamp (VERSION, manifest version, card version string, claim headers, D6 claims);
  the unmutated baseline run of env_drift against it must be green, which this harness requires.
Instrumented symbol: tests/mutation_table.py:killed over the production line each mutant edits.
Perturbation: a mutant is a one-line production edit; the null control (a comment-only edit,
  tests/mutation_table.py:null_control on optimizer.py) must LIVE under every driver.
Kill key: the driver's failing-check count (mutation_table.failing_count), not its exit status.
Writes: results.jsonl / baseline.json beside this file; worker trees under a mkdtemp root.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
REL = HERE.relative_to(ROOT)
PY = sys.executable
SKIP = {"tests/stress.py": "brief D3.M2 pre-screen skip", "tests/edge.py": "brief D3.M2 pre-screen skip",
        "tests/backtest.py": "brief D3.M2 pre-screen skip",
        "tests/golden.py": "default mode IS the env_drift step (mutation_table.DRIVER_EXCLUSIONS)",
        "tests/card_drift.mjs": "compares card source against a ref; no production input"}
CHEAP = 20.0  # after a kill, keep running only drivers recorded under this many seconds
TIMEOUT = int(os.environ.get("D3S2_TIMEOUT", "1500"))
ENV_LOCK = threading.Lock()
_OK = re.compile(r"^\s*ok\s+\S", re.M)
_ALL = re.compile(r"^ALL (\d+) .*PASSED\s*$", re.M)

SITECUSTOMIZE = r'''
import os, sys, atexit, importlib.abc, importlib.util, functools
_LOG = os.environ.get("D3S2_SOLVE_LOG")
_N = [0]
_T = ("heatpump_optimizer.optimizer", "custom_components.heatpump_optimizer.optimizer")
class _F(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name not in _T:
            return None
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(name)
        finally:
            sys.meta_path.insert(0, self)
        if spec is None or spec.loader is None:
            return spec
        orig = spec.loader.exec_module
        def exec_module(module, _o=orig):
            _o(module)
            cls = getattr(module, "HeatPumpOptimizer", None)
            if cls is not None and not getattr(cls.optimize, "_d3s2", False):
                f = cls.optimize
                @functools.wraps(f)
                def optimize(*a, **k):
                    _N[0] += 1
                    return f(*a, **k)
                optimize._d3s2 = True
                cls.optimize = optimize
        spec.loader.exec_module = exec_module
        return spec
if _LOG:
    sys.meta_path.insert(0, _F())
    def _dump():
        try:
            with open(_LOG, "a") as fh:
                fh.write(f"{os.getpid()} {_N[0]}\n")
        except OSError:
            pass
    atexit.register(_dump)
'''


def closures():
    d = json.loads((ROOT / "tests/closures.json").read_text())
    return d["closures"], d["recorded"]


def drivers_for(rel: str) -> list[str]:
    cl, rec = closures()
    ds = [s for s, fs in cl.items() if rel in fs and s not in SKIP]
    if "tests/card.mjs" in ds and "tests/plan_view.py" not in ds:
        ds.append("tests/plan_view.py")
    sec = lambda s: rec.get(s, {}).get("seconds", 999.0)
    if os.environ.get("D3S2_ORDER") == "measured":
        # Cost order from this box's own unmutated baseline walls (baseline.json), which puts
        # env_drift.py (a real --all run, not the 0.3 s stub closures.json records) last. The
        # verdict is order-independent: a survivor runs every driver either way.
        try:
            walls = {k: v["wall"] for k, v in json.loads((HERE / "baseline.json").read_text()).items()}
            sec = lambda s: walls.get(s, 999.0)  # noqa: E731
            return sorted(ds, key=lambda s: (sec("tests/plan_view.py") + 0.001) if s == "tests/card.mjs" else sec(s))
        except (OSError, ValueError, KeyError):
            pass
    # cheapest first, but env_drift (the differential) right after the sub-20 s scripts
    def order(s):
        if s == "tests/env_drift.py":
            return (0, CHEAP)
        if s == "tests/card.mjs":  # must follow plan_view.py
            return (0, sec("tests/plan_view.py") + 0.001)
        return (0, sec(s))
    return sorted(ds, key=order)


def run_driver(script: str, tree: Path, work: Path, ref: str) -> dict:
    env = {**os.environ, "PYTHONPATH": f"{work / 'site'}:tests/hastub",
           "HPO_PLANDATA": str(work / "plandata.json"), "TMPDIR": str(work / "tmp"),
           "D3S2_SOLVE_LOG": str(work / "solves.log")}
    (work / "tmp").mkdir(exist_ok=True)
    try:
        (work / "solves.log").unlink()
    except FileNotFoundError:
        pass
    if script.endswith(".mjs"):
        cmd = ["node", script]
    elif script == "tests/env_drift.py":
        cmd = [PY, script, "--all", ref]
    else:
        cmd = [PY, script]
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=tree, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    bufs = {"out": "", "err": ""}
    def _rd(k, fh):
        bufs[k] = fh.read()
    th = [threading.Thread(target=_rd, args=("out", proc.stdout)),
          threading.Thread(target=_rd, args=("err", proc.stderr))]
    for x in th:
        x.start()
    timer = threading.Timer(TIMEOUT, proc.kill)
    timer.start()
    _pid, status, ru = os.wait4(proc.pid, 0)
    timer.cancel()
    for x in th:
        x.join()
    proc.returncode = os.waitstatus_to_exitcode(status)
    wall = time.monotonic() - t0
    out, err, rc = bufs["out"], bufs["err"], proc.returncode
    cpu = ru.ru_utime + ru.ru_stime
    if rc < 0 and wall >= TIMEOUT - 1:
        rc, out = mt.TIMEOUT_RC, ""
        err += f"\n{script}: timed out after {TIMEOUT}s"
    run = mt.ScriptRun(rc, 0, wall, out, err)
    run = run._replace(failed=mt.failing_count(run))
    solves = 0
    try:
        solves = sum(int(l.split()[1]) for l in (work / "solves.log").read_text().splitlines() if l.strip())
    except (FileNotFoundError, ValueError, IndexError):
        pass
    checks = len(_OK.findall(out)) + len(mt._CHECK_FAIL.findall(out))
    alls = _ALL.findall(out)
    if alls:
        checks = max(checks, int(alls[-1]))
    return {"script": script, "rc": rc, "failed": run.failed, "wall": round(wall, 2),
            "cpu": round(cpu, 2),
            "checks": checks, "solves": solves, "fail_names": mt.failed_checks(run)[:5],
            "_run": run}


def run_driver_cpu(script, tree, work, ref):
    """run_driver; D3S2_ENV_SERIAL=1 serialises env_drift.py (it adds a git worktree, README trap;
    each run uses its own mkdtemp path, so the default run leaves it concurrent)."""
    if script == "tests/env_drift.py" and os.environ.get("D3S2_ENV_SERIAL", "0") == "1":
        with ENV_LOCK:
            return run_driver(script, tree, work, ref)
    return run_driver(script, tree, work, ref)


def apply(tree: Path, m: dict) -> str:
    p = tree / m["file"]
    orig = p.read_text()
    lines = orig.splitlines(True)
    assert lines[m["line"] - 1].rstrip("\n") == m["old"], (m["id"], "line moved")
    lines[m["line"] - 1] = m["new"] + "\n"
    p.write_text("".join(lines))
    return orig


def make_tree(root: Path, name: str) -> Path:
    dest = root / name
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(dest), "HEAD"],
                   cwd=ROOT, check=True, capture_output=True)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=int(os.environ.get("D3S2_JOBS", "2")))
    ap.add_argument("--all-drivers", action="store_true",
                    help="do not stop after a kill (duplicated-coverage measurement, M5)")
    ap.add_argument("--ref", default=os.environ.get("D3S2_REF", "HEAD^1"))
    ap.add_argument("--results", default="results.jsonl")
    a = ap.parse_args()
    ref = subprocess.run(["git", "rev-parse", a.ref], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip()
    pool = json.loads((HERE / os.environ.get("D3S2_POOL", "pool.json")).read_text())["pool"]
    if a.only:
        want = set(a.only.split(","))
        pool = [m for m in pool if m["id"] in want]
    _cl, rec = closures()
    root = Path(tempfile.mkdtemp(prefix="d3s2-"))
    trees = []
    for w in range(a.jobs):
        t = make_tree(root, f"w{w}")
        wk = root / f"work{w}"
        (wk / "site").mkdir(parents=True)
        (wk / "site" / "sitecustomize.py").write_text(SITECUSTOMIZE)
        trees.append((t, wk))
    free = list(range(a.jobs))
    flock = threading.Lock()

    def take():
        while True:
            with flock:
                if free:
                    return free.pop()
            time.sleep(0.5)

    def give(w):
        with flock:
            free.append(w)

    # ---- baseline: every driver any mutant's closure names, unmutated -----------
    base_path = HERE / "baseline.json"
    baseline = json.loads(base_path.read_text()) if base_path.exists() else {}
    need = sorted({d for m in pool for d in drivers_for(m["file"])} - set(baseline))
    def base_one(d):
        w = take()
        try:
            t, wk = trees[w]
            if d == "tests/card.mjs":  # needs a payload: plan_view first on the same worker
                run_driver_cpu("tests/plan_view.py", t, wk, ref)
            r = run_driver_cpu(d, t, wk, ref)
            r.pop("_run")
            r["recorded_seconds"] = rec.get(d, {}).get("seconds")
            print(f"BASE {d}: rc={r['rc']} failed={r['failed']} wall={r['wall']}s "
                  f"checks={r['checks']} solves={r['solves']}", flush=True)
            return d, r
        finally:
            give(w)
    with ThreadPoolExecutor(a.jobs) as ex:
        for d, r in ex.map(base_one, need):
            baseline[d] = r
    base_path.write_text(json.dumps(baseline, indent=1, sort_keys=True) + "\n")
    red = [d for d, r in baseline.items() if r["rc"] != 0]
    if red:
        print("BASELINE RED:", red, "-- verdicts from these drivers are void")

    def base_run(d):
        b = baseline[d]
        return mt.ScriptRun(b["rc"], b["failed"], b["wall"], "", "")

    # ---- mutants (and the null control) ------------------------------------------
    res_path = HERE / a.results
    done = set()
    if res_path.exists():
        done = {json.loads(l)["id"] for l in res_path.read_text().splitlines() if l.strip()}
    null = mt.null_control(ROOT / "custom_components/heatpump_optimizer/optimizer.py")
    null.update(id="NULL", file="custom_components/heatpump_optimizer/optimizer.py")
    todo = ([null] if "NULL" not in done and not a.only else []) + [m for m in pool if m["id"] not in done]
    wlock = threading.Lock()

    def one(m):
        w = take()
        t, wk = trees[w]
        orig = apply(t, m)
        runs, killers = [], []
        try:
            for d in drivers_for(m["file"]):
                if killers and not a.all_drivers and m["id"] != "NULL" and (
                        d == "tests/env_drift.py" or rec.get(d, {}).get("seconds", 999) >= CHEAP):
                    runs.append({"script": d, "skipped": "already killed; expensive"})
                    continue
                if baseline.get(d, {}).get("rc", 1) != 0:
                    runs.append({"script": d, "skipped": "baseline red"})
                    continue
                r = run_driver_cpu(d, t, wk, ref)
                run = r.pop("_run")
                r["killed"] = mt.killed(d, run, base_run(d))
                if r["killed"]:
                    killers.append(d)
                runs.append(r)
        finally:
            (t / m["file"]).write_text(orig)
            give(w)
        out = {"id": m["id"], "kind": m["kind"], "file": m["file"], "line": m["line"],
               "old": m["old"], "new": m["new"], "killers": killers,
               "verdict": "KILLED" if killers else "SURVIVED", "runs": runs,
               "ref": ref, "all_drivers": a.all_drivers}
        with wlock:
            with res_path.open("a") as fh:
                fh.write(json.dumps(out) + "\n")
        print(f"{m['id']} {out['verdict']} by {killers}", flush=True)
        return out

    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(one, todo))
    for t, _wk in trees:
        mt.drop_tree(t)

    rows = [json.loads(l) for l in res_path.read_text().splitlines() if l.strip()]
    muts = [r for r in rows if r["id"] != "NULL"]
    nul = [r for r in rows if r["id"] == "NULL"]
    print(f"RESULT null_control={'LIVES' if nul and not nul[-1]['killers'] else ('KILLED' if nul else 'NOT RUN')}")
    print(f"RESULT mutants_screened={len(muts)} mutants")
    print(f"RESULT survivors={sum(r['verdict']=='SURVIVED' for r in muts)} mutants")
    print(f"RESULT baseline_red_drivers={len(red)} drivers")
    load1 = os.getloadavg()[0]
    pt, tt = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={load1:.2f}")
    sw = 0
    try:
        for l in Path("/proc/vmstat").read_text().splitlines():
            if l.startswith("pswpin "):
                sw = int(l.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
