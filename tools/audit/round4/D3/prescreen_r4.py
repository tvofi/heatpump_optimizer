#!/usr/bin/env python3
"""D3 round 4 -- the pre-screen: does the measured closure NOTICE a deleted line?

METRIC: per mutant, the first script in its measured closure (tests/closures.json,
fast scripts only -- stress.py, edge.py and backtest.py excluded by the brief)
whose exit status changes or whose `N of M ... FAILED` count rises above the
baseline's; `survived` when no fast script and no `env_drift.py --all <baseline>`
run reports a change.

RUN (from the repository root, one at a time -- env_drift adds a worktree):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/prescreen_r4.py --baseline
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/prescreen_r4.py --run

EXPECTED: 36 mutants pre-screened; the state file
tools/audit/round4/D3/prescreen.json carries one record per mutant.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (the comparison ref, never HEAD)
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11, OpenBLAS

Threads are pinned the way tests/stress.py pins them, before anything imports
numpy, because the drivers this spawns are timed and a threaded BLAS inflates
process_time() by the thread factor.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE_SHA = "7dd68dd327fe3dbfb09f3bd0fe38910c58877697"
PY = sys.executable
NODE = "/Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node"
_FAILED = re.compile(r"^\s*(\d+) of (\d+) .*FAILED\s*$", re.M)

# The fast scripts of a closure. stress.py, edge.py and backtest.py are the
# three the brief excludes from a pre-screen; rolling.py is SLOW-gated and has
# no recorded closure; card_drift.mjs renders the WORKING TREE's card against
# the ref's card, so a mutant in Python moves neither side's markup and it
# cannot kill one (checked -- see REPORT.md); golden.py is skipped by
# tests/run.sh whenever GOLDEN_MODE=drift, which is what CI runs, so it is
# driven but reported apart.
EXCLUDED_DRIVERS = {"tests/stress.py", "tests/edge.py", "tests/backtest.py",
                    "tests/card_drift.mjs", "tests/env_drift.py",
                    # MEASURED, not assumed: a plain `python3 tests/golden.py`
                    # resolves GOLDEN_MODE to `drift` and then EXECS
                    # `tests/env_drift.py --all origin/main` -- the same 190 s
                    # differential run this pre-screen already makes against the
                    # baseline SHA, against a different ref. tests/run.sh skips
                    # golden.py outright whenever GOLDEN_MODE=drift, which is
                    # what CI runs. Driving it would double the dearest step in
                    # the pre-screen and add a second `git worktree add`.
                    "tests/golden.py"}
PRODUCERS = {"tests/card.mjs": ["tests/plan_view.py"]}

STATE = HERE / "prescreen.json"
POOL = HERE / "pool.json"


def _sh(cmd, cwd=ROOT, env=None, timeout=2400):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, p.stdout + p.stderr, time.monotonic() - started
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT", time.monotonic() - started


def driver_env(plandata: Path):
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"
    env["HPO_PLANDATA"] = str(plandata)
    env["NODE_PATH"] = "/private/tmp/hpo-pw/node_modules"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(Path.home() / ".cache" / "pw-browsers")
    return env


def run_driver(script: str, env) -> tuple[int, int, float]:
    cmd = [NODE, script] if script.endswith(".mjs") else [PY, script]
    rc, out, secs = _sh(cmd, env=env)
    hits = _FAILED.findall(out)
    return rc, (int(hits[-1][0]) if hits else 0), secs


def run_env_drift(env) -> tuple[int, int, float]:
    rc, out, secs = _sh([PY, "tests/env_drift.py", "--all", BASE_SHA], env=env)
    if "SELF-COMPARISON" in out:
        raise SystemExit("env_drift refused: the ref resolves to HEAD")
    return rc, 0, secs


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"baseline": {}, "mutants": {}, "load1": [], "notes": []}


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1) + "\n")


def load1() -> float:
    return os.getloadavg()[0]


def closures() -> dict:
    return json.loads((ROOT / "tests" / "closures.json").read_text())["closures"]


def fast_drivers_for(rel: str, cl: dict) -> list[str]:
    got = [s for s in cl if rel in cl.get(s, ()) and s not in EXCLUDED_DRIVERS]
    for s in list(got):
        for prod in PRODUCERS.get(s, []):
            if prod not in got:
                got.append(prod)
    return got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--plandata", default="/private/tmp/claude-501/d3r4-plandata.json")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)

    plandata = Path(args.plandata)
    plandata.parent.mkdir(parents=True, exist_ok=True)
    env = driver_env(plandata)
    cl = closures()
    pool = json.loads(POOL.read_text())
    state = load_state()

    needed = sorted({s for m in pool["mutants"] for s in fast_drivers_for(m["file"], cl)})

    if args.baseline:
        print(f"BASELINE DRIVERS ({len(needed)}): load1={load1():.2f}")
        # plan_view.py writes the payload card.mjs reads: it must go first.
        order = ["tests/plan_view.py"] + [s for s in needed if s != "tests/plan_view.py"]
        for s in order:
            rc, failed, secs = run_driver(s, env)
            state["baseline"][s] = {"rc": rc, "failed": failed, "seconds": round(secs, 1)}
            print(f"  {s:32s} rc={rc} failed={failed} {secs:7.1f}s")
            save(state)
        rc, _, secs = run_env_drift(env)
        state["baseline"]["tests/env_drift.py --all"] = {
            "rc": rc, "failed": 0, "seconds": round(secs, 1)}
        print(f"  {'tests/env_drift.py --all':32s} rc={rc} {secs:7.1f}s")
        state["load1"].append(round(load1(), 2))
        save(state)
        red = [s for s, v in state["baseline"].items() if v["rc"] != 0]
        print(f"RESULT baseline_red_scripts={len(red)} count {red}")
        return 0

    if not args.run:
        ap.error("pass --baseline or --run")

    base = state["baseline"]
    if not base:
        ap.error("run --baseline first")
    # Cheapest measured first, so a kill costs the cheapest driver that sees it.
    def cost(s: str) -> float:
        return base.get(s, {}).get("seconds", 9e9)

    only = set(args.only.split(",")) if args.only else None
    for mut in pool["mutants"]:
        if only and mut["id"] not in only:
            continue
        if mut["id"] in state["mutants"]:
            continue
        path = ROOT / mut["file"]
        original = path.read_text()
        orig_hash = hashlib.sha256(original.encode()).hexdigest()
        lines = original.splitlines(True)
        idx = mut["line"] - 1
        assert lines[idx].rstrip("\n") == mut["old"], (
            f"{mut['id']}: line {mut['line']} is not what the pool recorded")
        nl = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = mut["new"] + nl
        rec = {"id": mut["id"], "file": mut["file"], "line": mut["line"],
               "op": mut["op"], "weight": mut["weight"], "old": mut["old"],
               "new": mut["new"], "what": mut["what"],
               "closure": fast_drivers_for(mut["file"], cl),
               "scripts_run": [], "killed_by": None, "survived": False,
               "load1_start": round(load1(), 2)}
        drivers = sorted(rec["closure"], key=cost)
        if "tests/card.mjs" in drivers:
            drivers = ["tests/plan_view.py"] + [d for d in drivers if d != "tests/plan_view.py"]
        t0 = time.monotonic()
        try:
            path.write_text("".join(lines))
            for s in drivers:
                if s not in base or base[s]["rc"] != 0:
                    continue
                rc, failed, secs = run_driver(s, env)
                rec["scripts_run"].append(
                    {"script": s, "rc": rc, "failed": failed, "seconds": round(secs, 1)})
                if rc != base[s]["rc"] or failed > base[s]["failed"]:
                    rec["killed_by"] = s
                    break
            if rec["killed_by"] is None:
                rc, _, secs = run_env_drift(env)
                rec["scripts_run"].append(
                    {"script": "tests/env_drift.py --all", "rc": rc,
                     "failed": 0, "seconds": round(secs, 1)})
                if rc != base["tests/env_drift.py --all"]["rc"]:
                    rec["killed_by"] = "tests/env_drift.py --all"
                else:
                    rec["survived"] = True
        finally:
            path.write_text(original)
            back = hashlib.sha256(path.read_text().encode()).hexdigest()
            rec["restored"] = back == orig_hash
            assert rec["restored"], f"{mut['id']}: FAILED TO RESTORE {mut['file']}"
        rec["seconds"] = round(time.monotonic() - t0, 1)
        state["mutants"][mut["id"]] = rec
        save(state)
        verdict = rec["killed_by"] or "SURVIVED"
        print(f"{mut['id']} w={mut['weight']} {mut['op']:10s} "
              f"{mut['file'].split('/')[-1]}:{mut['line']}  -> {verdict}  "
              f"({len(rec['scripts_run'])} script(s), {rec['seconds']:.0f}s, "
              f"load1={rec['load1_start']})")

    done = state["mutants"]
    surv = [r for r in done.values() if r["survived"]]
    print(f"RESULT prescreened={len(done)} count")
    print(f"RESULT survivors={len(surv)} count")
    print(f"RESULT load1={load1():.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
