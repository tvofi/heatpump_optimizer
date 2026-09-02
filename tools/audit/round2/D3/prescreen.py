#!/usr/bin/env python3
"""D3 round 2 -- pre-screen deletion mutants against their measured closures.

Metric: per mutant, which script of its measured fast closure (plus
`tests/env_drift.py --all <baseline>`) fails first, in cost order; a mutant
nothing fails is a PRESCREENED SURVIVOR (a candidate, not a finding -- the
quiet window confirms it with the full gate).

Run from the D3 worktree root (it must have .git; HEAD must be a throwaway
branch at the baseline):

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    .venv/bin/python tools/audit/round2/D3/prescreen.py --scratch <tmpdir> [--ids M01 M02 ...] [--jobs 2]

Expected: `RESULT survivors=<n> count` -- 5 +- 3 of 36 on baseline
c398fc84eec25fc44b60d74aae05b9a2da205884 (8-core Apple M1); the null mutant
(a comment-only change, id NULL) must survive everything.

Instrumented symbols: the whole suite -- each script is run as the gate runs
it; the mutant is the perturbation (revert the patch and every script
passes; that is the null control, run as id NULL).

Mechanics: the mutant is applied and committed in this worktree (so HEAD
differs from the baseline, which env_drift.py insists on), env_drift.py
--all runs here, serially (it adds a worktree of its own); the tree is then
rsynced to a private scratch copy where the other closure scripts run from
a thread pool while the next mutant's env_drift runs. Scripts of the
closure that are the quiet window's (stress.py, edge.py, backtest.py) are
not run; golden.py's strict comparison does not reproduce on this machine
(tests/README.md) and env_drift --all stands in for it as in CI;
card_drift.mjs compares the card's JavaScript at two refs and no Python
mutant changes that file. Cheap scripts (<= 10 s recorded) always run, for
the coverage-overlap census; the expensive ones run only while the mutant is
still alive. features.py is stopped at its first FAIL line (a kill is a
kill); validate.py collects issues until its end and runs to completion.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

BASE = "c398fc84eec25fc44b60d74aae05b9a2da205884"
HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
PY = sys.executable
PIN = {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                        "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}
QUIET_ONLY = {"tests/stress.py", "tests/edge.py", "tests/backtest.py"}
NOT_RUN = {
    "tests/golden.py": "strict fixture comparison does not reproduce on this machine; env_drift --all stands in (as in CI drift mode)",
    "tests/card_drift.mjs": "compares the card JavaScript at two git refs; identical for every Python mutant",
}
CHEAP_SECONDS = 10.0
TIMEOUT = 1800
LOCK = threading.Lock()
RESULTS: dict = {}
RESULTS_PATH = HERE / "prescreen_results.json"


def log(msg: str) -> None:
    with LOCK:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def save() -> None:
    with LOCK:
        RESULTS_PATH.write_text(json.dumps(RESULTS, indent=1, sort_keys=True))


def closure_for(module_rel: str) -> list[str]:
    out = subprocess.run([PY, "tests/closure.py", "select", "--files", module_rel],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ln.split()[1] for ln in out.splitlines() if ln.strip().startswith("RUN ")]


def recorded_seconds() -> dict[str, float]:
    d = json.loads((ROOT / "tests" / "closures.json").read_text())
    return {k: v["seconds"] for k, v in d["recorded"].items()}


def run_script(tree: Path, script: str, env: dict, log_path: Path, stop_on_fail: bool) -> dict:
    """Run one script from `tree`; return rc, wall, cpu, first FAIL lines."""
    if script.endswith(".mjs"):
        cmd = ["node", script]
    else:
        cmd = [PY, script]
    t0 = time.time()
    fails: list[str] = []
    early = False
    with open(log_path, "w") as lf:
        proc = subprocess.Popen(cmd, cwd=tree, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                lf.write(line)
                s = line.rstrip("\n")
                if s.startswith("  FAIL") or s.startswith("FAIL") or "Traceback" in s \
                        or s.startswith("  DRIFT") or s.startswith("  - ") or "ISSUES:" in s:
                    if len(fails) < 12:
                        fails.append(s[:200])
                    if stop_on_fail and s.startswith("  FAIL"):
                        early = True
                        proc.terminate()
                        break
                if time.time() - t0 > TIMEOUT:
                    fails.append(f"TIMEOUT after {TIMEOUT}s")
                    proc.kill()
                    break
        finally:
            proc.stdout.close()
    _, status, ru = os.wait4(proc.pid, 0)
    rc = os.waitstatus_to_exitcode(status) if not early else 1
    wall = time.time() - t0
    cpu = ru.ru_utime + ru.ru_stime
    tail = ""
    try:
        tail = "".join(open(log_path).readlines()[-6:])[-600:]
    except OSError:
        pass
    return {"rc": rc, "wall_s": round(wall, 1), "cpu_s": round(cpu, 1), "early_stop": early,
            "fails": fails, "tail": tail, "load1": round(os.getloadavg()[0], 2)}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def apply_and_commit(mid: str, patch: Path | None) -> str:
    git("reset", "-q", "--hard", BASE)
    if patch is None:  # the null mutant: a comment only
        with open(ROOT / "custom_components/heatpump_optimizer/optimizer.py", "a") as f:
            f.write("# D3 null mutant: comment only\n")
    else:
        git("apply", str(patch))
    git("commit", "-qam", f"D3 mutant {mid}")
    return git("rev-parse", "--short", "HEAD").strip()


def env_drift(scratch: Path, mid: str) -> dict:
    env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"],
           "PYTHONPATH": str(ROOT / "tests" / "hastub"), **PIN}
    logs = scratch / "logs" / mid
    logs.mkdir(parents=True, exist_ok=True)
    r = run_script(ROOT, "tests/env_drift.py", env | {"_ARGS": ""}, logs / "env_drift.log", False) \
        if False else None
    # env_drift takes arguments; run it explicitly.
    t0 = time.time()
    with open(logs / "env_drift.log", "w") as lf:
        proc = subprocess.Popen([PY, "tests/env_drift.py", "--all", BASE], cwd=ROOT, env=env,
                                stdout=lf, stderr=subprocess.STDOUT)
    _, status, ru = os.wait4(proc.pid, 0)
    rc = os.waitstatus_to_exitcode(status)
    text = open(logs / "env_drift.log").read()
    drift = [ln.strip()[:200] for ln in text.splitlines() if ln.startswith("  DRIFT") or ln.startswith("  MAY-DRIFT")]
    hit = "CACHE HIT" in text
    return {"rc": rc, "wall_s": round(time.time() - t0, 1), "cpu_s": round(ru.ru_utime + ru.ru_stime, 1),
            "cache_hit": hit, "drift": drift[:12], "n_drift": sum(1 for d in drift if d.startswith("DRIFT")),
            "tail": text[-400:], "load1": round(os.getloadavg()[0], 2)}


def scratch_job(mid: str, tree: Path, closure: list[str], secs: dict, scratch: Path, alive: bool) -> None:
    logs = scratch / "logs" / mid
    logs.mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"],
           "PYTHONPATH": str(tree / "tests" / "hastub"), **PIN,
           "HPO_PLANDATA": str(scratch / f"plandata-{mid}.json")}
    runnable = [s for s in closure if s not in QUIET_ONLY and s not in NOT_RUN and s != "tests/env_drift.py"]
    cheap = sorted([s for s in runnable if secs.get(s, 999) <= CHEAP_SECONDS], key=lambda s: secs.get(s, 0))
    dear = sorted([s for s in runnable if secs.get(s, 999) > CHEAP_SECONDS], key=lambda s: secs.get(s, 0))
    # plan_view.py must precede card.mjs (it writes the payload the card reads)
    if "tests/card.mjs" in cheap and "tests/plan_view.py" in cheap:
        cheap.remove("tests/plan_view.py")
        cheap.insert(cheap.index("tests/card.mjs"), "tests/plan_view.py")
    rec = RESULTS[mid]
    rec["scripts_not_run"] = {s: NOT_RUN[s] for s in closure if s in NOT_RUN}
    rec["scripts_quiet_window"] = [s for s in closure if s in QUIET_ONLY]
    for s in cheap:
        r = run_script(tree, s, env, logs / (Path(s).name + ".log"), False)
        rec["scripts"][s] = r
        if r["rc"] != 0:
            alive = False
            rec["killed_by"].append(s)
        log(f"{mid} {s} rc={r['rc']} {r['wall_s']}s")
        save()
    if alive:
        heavy = [s for s in dear if s in ("tests/validate.py", "tests/features.py")]
        for s in [s for s in dear if s not in heavy]:
            r = run_script(tree, s, env, logs / (Path(s).name + ".log"), False)
            rec["scripts"][s] = r
            log(f"{mid} {s} rc={r['rc']} {r['wall_s']}s")
            save()
            if r["rc"] != 0:
                alive = False
                rec["killed_by"].append(s)
                break
    if alive and heavy:
        threads = []
        outs: dict[str, dict] = {}

        def _go(s: str) -> None:
            outs[s] = run_script(tree, s, env, logs / (Path(s).name + ".log"), s == "tests/features.py")

        for s in heavy:
            t = threading.Thread(target=_go, args=(s,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        for s in heavy:
            rec["scripts"][s] = outs[s]
            log(f"{mid} {s} rc={outs[s]['rc']} {outs[s]['wall_s']}s early={outs[s]['early_stop']}")
            if outs[s]["rc"] != 0:
                alive = False
                rec["killed_by"].append(s)
    else:
        for s in dear:
            if s not in rec["scripts"]:
                rec["scripts"][s] = {"skipped": "mutant already killed" if not alive else "not reached"}
    rec["survived"] = alive and not rec["killed_by"]
    rec["done"] = True
    save()
    log(f"{mid} DONE survived={rec['survived']} killed_by={rec['killed_by']}")
    shutil.rmtree(tree, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    head_branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    if head_branch in ("HEAD", "main"):
        print("refusing: check out a throwaway branch first", file=sys.stderr)
        return 2
    sample = {m["id"]: m for m in json.loads((HERE / "sample.json").read_text())}
    sample["NULL"] = {"id": "NULL", "module": "optimizer.py", "kind": "null", "line": 0,
                      "func": "-", "text": "comment only", "weight": 0}
    ids = args.ids or ["NULL"] + sorted(m for m in sample if m != "NULL")
    if args.resume and RESULTS_PATH.exists():
        RESULTS.update(json.loads(RESULTS_PATH.read_text()))
    secs = recorded_seconds()
    closures: dict[str, list[str]] = {}
    pool = ThreadPoolExecutor(max_workers=args.jobs)
    futures = []
    for mid in ids:
        if args.resume and RESULTS.get(mid, {}).get("done"):
            continue
        m = sample[mid]
        rel = "custom_components/heatpump_optimizer/" + m["module"]
        if rel not in closures:
            closures[rel] = closure_for(rel)
        closure = closures[rel]
        patch = None if mid == "NULL" else HERE / "mutants" / f"{mid}.patch"
        sha = apply_and_commit(mid, patch)
        RESULTS[mid] = {"id": mid, "module": m["module"], "line": m["line"], "kind": m["kind"],
                        "func": m["func"], "site": m["text"], "weight": m.get("weight"),
                        "commit": sha, "closure": closure, "scripts": {}, "killed_by": [],
                        "survived": None, "done": False}
        tree = scratch / f"tree-{mid}"
        if tree.exists():
            shutil.rmtree(tree)
        subprocess.run(["rsync", "-a", "--exclude", ".git", "--exclude", "tools", "--exclude", "docs",
                        "--exclude", "__pycache__", f"{ROOT}/", f"{tree}/"], check=True)
        log(f"{mid} committed {sha}; env_drift --all {BASE[:12]} ...")
        ed = env_drift(scratch, mid)
        RESULTS[mid]["scripts"]["tests/env_drift.py"] = ed
        alive = ed["rc"] == 0
        if not alive:
            RESULTS[mid]["killed_by"].append("tests/env_drift.py")
        log(f"{mid} env_drift rc={ed['rc']} {ed['wall_s']}s hit={ed['cache_hit']} drift={ed['n_drift']}")
        git("reset", "-q", "--hard", BASE)
        save()
        futures.append(pool.submit(scratch_job, mid, tree, closure, secs, scratch, alive))
    for f in futures:
        f.result()
    pool.shutdown()
    git("reset", "-q", "--hard", BASE)
    survivors = [m for m, r in RESULTS.items() if r.get("survived")]
    print(f"RESULT survivors={len(survivors)} count")
    print(f"RESULT mutants={len([m for m in RESULTS if m != 'NULL'])} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("survivors:", " ".join(sorted(survivors)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
