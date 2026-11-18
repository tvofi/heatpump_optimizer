#!/usr/bin/env python3
"""D3-s1 M5(d)(e): trace the closure scripts the pre-screen never drove, and test their closures.

Metric (one line): for each script S (default tests/stress.py, tests/golden.py,
tests/card.mjs, tests/card_drift.mjs, plus tests/boost_drift_replay.py read
from state/baselines.json), and each D3-s1 cell file F in S's
tests/closures.json closure: the number of F's executable lines S's unmutated
run executes (sys.monitoring LINE events of mutation_table:REACH_HOOK, every
Python process S starts) and whether S reads F as text; a pair (S, F) with
0 executed lines, no text read and a usable reach row (reach_problems empty)
is an OVER-APPROXIMATED closure edge: a diff touching F forces S, S cannot
see F. A Node program (card.mjs, card_drift.mjs) starts no Python process; it
renders the payload tests/plan_view.py writes (tests/closure.py PRODUCERS), so
its cell edges are judged by plan_view.py's traced reach (`via-producer`). Count key: the hits the traced run delivers, never the closure list.

Instrumented symbols: tests/mutation_table.py:REACH_HOOK / collect /
reach_problems on each traced run; tests/closures.json `closures` (the
measured closure tests/closure.py selects from).
Perturbation: `--drop FILE` zeroes FILE's hits in every row -> over_approx
pairs rise by the number of rows that executed FILE (direction up); the
identity run is the null control.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_trace_extra.py trace [--scripts a,b]   # runs, writes state/extra_reach.json
     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_trace_extra.py table [--drop FILE]    # reads it
Invocation as tests/run.sh: stress.py with GOLDEN_REF=HEAD^1 exported,
card_drift.mjs HEAD^1, card.mjs bare (all after plan_view.py wrote the
payload to a private HPO_PLANDATA), golden.py under GOLDEN_MODE=strict (the
mode in which run.sh runs it; under drift run.sh skips it).
Expected: exact counts; wall/CPU provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
Machine: box D3-m5, Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "state" / "extra_reach.json"
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
RELS = [mt.PKG + c + ".py" for c in CELLS]
DEFAULT = ["tests/plan_view.py", "tests/card.mjs", "tests/card_drift.mjs",
           "tests/golden.py", "tests/stress.py"]
REF = "HEAD^1"


def invocation(s: str, plan: Path):
    env = {"HPO_PLANDATA": str(plan), "GOLDEN_REF": REF}
    if s == "tests/card.mjs":
        return ["node", s], env
    if s == "tests/card_drift.mjs":
        return ["node", s, REF], env
    if s == "tests/golden.py":
        return [sys.executable, s], {**env, "GOLDEN_MODE": "strict"}
    a, e = mt.drive_spec(s, REF)
    return [sys.executable, s, *a], {**env, **e}


def trace(scripts: list[str]) -> int:
    t = Path(tempfile.gettempdir()) / "d3s1-workers" / "tx"
    if not (t / ".git").exists():
        t.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(t), "HEAD"],
                       cwd=mt.ROOT, check=True)
    root = Path(tempfile.mkdtemp(prefix="d3s1-tx-"))
    plan = root / "plandata.json"
    cur = json.loads(OUT.read_text()) if OUT.exists() else {}
    for s in scripts:
        out = root / ("reach-" + s.replace("/", "_"))
        out.mkdir()
        env = mt.hook_env(out)
        cmd, extra = invocation(s, plan)
        full = {**os.environ, **extra, **env,
                "PYTHONPATH": mt.traced_pythonpath(env, "tests/hastub")}
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.monotonic()
        p = subprocess.run(cmd, cwd=t, env=full, capture_output=True, text=True,
                           timeout=7200)
        wall = time.monotonic() - t0
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
        reach = mt.collect(out)
        if cmd[0] == "node":
            # collect() counts the root as one started Python process; a Node
            # root is not one, so the started count is one too high.
            reach["processes"]["started"] -= 1
            reach["root"] = "node"
        reach["rc"] = p.returncode
        run = mt.ScriptRun(p.returncode, 0, wall, p.stdout, p.stderr)
        cur[s] = {"rc": p.returncode, "failed": mt.failing_count(run),
                  "wall_s": round(wall, 1), "cpu_s": round(cpu, 1),
                  "traced": True, "provisional": True,
                  "load1": round(os.getloadavg()[0], 2),
                  "stdout_tail": p.stdout[-1200:], "stderr_tail": p.stderr[-800:],
                  "reach": reach, "reach_problems": mt.reach_problems(reach)}
        OUT.write_text(json.dumps(cur))
        print(f"TRACED {s} rc={p.returncode} wall={wall:.1f}s cpu={cpu:.1f}s "
              f"procs={reach['processes']} problems={cur[s]['reach_problems']}", flush=True)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


def table(drop: str | None) -> int:
    cur = json.loads(OUT.read_text())
    base = json.loads((HERE / "state" / "baselines.json").read_text())
    if "tests/boost_drift_replay.py" in base:
        b = base["tests/boost_drift_replay.py"]
        cur["tests/boost_drift_replay.py"] = {
            "rc": b["run"]["rc"], "wall_s": b["run"]["seconds"], "cpu_s": None,
            "reach": b["reach"], "reach_problems": mt.reach_problems(b["reach"])}
    clos = mt.load_closures()
    rec = mt.recorded_seconds()
    exe = {r: mt.executable_lines(mt.ROOT / r) for r in RELS}
    over = pairs = 0
    print("script\tcell\tin_closure\texec_lines\tof_executable\tread_as_text\tverdict")
    for s in sorted(cur):
        if s == "tests/plan_view.py":
            continue
        row = cur[s]
        reach = row["reach"]
        probs = row["reach_problems"]
        via = ""
        if s.endswith(".mjs") and "tests/plan_view.py" in cur:
            # A Node program starts no Python: it renders the payload
            # plan_view.py writes (closure.py PRODUCERS). Its cell edges are
            # judged by what its producer's traced run executes.
            reach = cur["tests/plan_view.py"]["reach"]
            probs = cur["tests/plan_view.py"]["reach_problems"]
            via = "via-producer:plan_view.py:"
        for r in RELS:
            if r not in clos.get(s, ()):
                continue
            pairs += 1
            hits = set((reach or {}).get("hits", {}).get(r, ())) & exe[r]
            if r == drop:
                hits = set()
            read = r in (reach or {}).get("reads", ())
            if probs:
                v = "refused:" + probs[0]
            elif not hits and not read:
                v = "OVER-APPROX"
                over += 1
            else:
                v = "reached"
            v = via + v
            print(f"{s}\t{r.rsplit('/', 1)[-1]}\t1\t{len(hits)}\t{len(exe[r])}\t{read}\t{v}")
        print(f"COST {s} rc={row['rc']} wall_s={row['wall_s']} cpu_s={row['cpu_s']} "
              f"recorded_s={rec.get(s)} (provisional)")
    print(f"RESULT closure_pairs={pairs}")
    print(f"RESULT over_approx_pairs={over}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("trace", "table"))
    ap.add_argument("--scripts")
    ap.add_argument("--drop")
    a = ap.parse_args()
    if a.cmd == "trace":
        return trace(a.scripts.split(",") if a.scripts else DEFAULT)
    return table(a.drop)


if __name__ == "__main__":
    sys.exit(main())
