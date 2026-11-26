#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/rerun.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Judge re-run of every D3 wave probe, as its record's command says, in the baseline tree + D3 evidence."""
import json, os, sys, subprocess, tempfile, time, pathlib, concurrent.futures as cf
WORK = pathlib.Path(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"))
WT = pathlib.Path.cwd()
OUT = WORK / "rerun"; OUT.mkdir(exist_ok=True)
master = json.load(open(WORK / "master.json"))
only = set(sys.argv[2:]) if len(sys.argv) > 2 else None
jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4

def run1(args, env):
    t = time.time()
    try:
        p = subprocess.run(args, cwd=WT, env=env, capture_output=True, text=True, timeout=2400)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, so, se = "timeout", (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    return {"rc": rc, "stdout": so, "stderr": se[-4000:], "wall_s": round(time.time() - t, 1), "load1": os.getloadavg()[0]}

def one(m):
    k = m["key"]; f = OUT / f"{k}.json"
    if f.exists() and not only: return k, "cached"
    probe = m["rec"]["probe"]; path = probe["path"]; cmd = probe["command"]
    tmp = tempfile.mkdtemp(prefix=f"d3j-{k}-")
    env = dict(os.environ, PYTHONPATH="tests/hastub", TMPDIR=tmp + "/", HPO_PLANDATA=tmp + "/plandata",
               HPO_PROBE_ROOT=str(WT), PROBE_ROOT=str(WT))
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[v] = "1"
    rec = {"key": k, "box": m["box"], "command": cmd}
    if "[--mutant]" in cmd:
        rec["base"] = run1(["python3", path], env)
        rec["mut"] = run1(["python3", path, "--mutant"], env)
    else:
        rec["run"] = run1(["python3", path], env)
    json.dump(rec, open(f, "w"), indent=1)
    subprocess.run(["rm", "-rf", tmp])
    return k, (rec.get("run") or rec["mut"])["rc"]

todo = [m for m in master if (only is None or m["key"] in only)]
if os.environ.get("REVERSE"): todo = todo[::-1]
with cf.ThreadPoolExecutor(jobs) as ex:
    for i, (k, rc) in enumerate(ex.map(one, todo)):
        print(f"{i+1}/{len(todo)} {k} rc={rc} load1={os.getloadavg()[0]:.1f}", flush=True)
print("DONE", flush=True)
