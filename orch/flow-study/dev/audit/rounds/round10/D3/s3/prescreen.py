#!/usr/bin/env python3
"""D3-s3 pre-screen (D3.M2): apply one mutant in a git worktree lane, run its measured closure's
fast scripts cheapest-first, stop at the first non-zero exit, then env_drift --all <baseline>.
Metric: per mutant, the first closure script whose exit code goes non-zero ("killed_by"), or SURVIVED.
Count key: exit code of each tests/*.py the closure names (the gate's own verdict), never output text.
Command (from repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D3/s3/prescreen.py <lane_dir> M01 M02 ...
Expected: per-mutant killed_by is deterministic (tolerance: exact). Baseline 17f1c55fad1b, machine: Mac (B3), load1 quoted.
Perturbation: an unmutated control (id CTRL) must SURVIVE every script; a mutant that survives here is a gap candidate."""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import json, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutants import MUTANTS, P
BASE = "17f1c55fad1bc97daf27174f2fbd6a18210d1fb7"
SKIP = {"tests/stress.py","tests/edge.py","tests/backtest.py","tests/boost_drift_replay.py","tests/arch_score.py",
        "tests/arch_score_head.py","tests/harness_headers.py","tests/structure.py","tests/doc_claims.py",
        "tests/card.mjs","tests/card_drift.mjs","tests/typing_ruler.py","tests/deployment_shape.py","tests/env_drift.py",
        "tests/optimality.py","tests/validate.py"}
lane = os.path.abspath(sys.argv[1]); ids = sys.argv[2:]
clos = json.load(open(os.path.join(lane, "tests/closures.json")))
rec, cl = clos["recorded"], clos["closures"]
py = sys.executable
env = dict(os.environ, PYTHONPATH="tests/hastub", GATE_JOBS="1", HPO_PLANDATA=os.path.join(os.environ.get("TMPDIR","/tmp"), "d3s3plan-"+os.path.basename(lane)))
def run(cmd, to=2400):
    t = time.time()
    try:
        r = subprocess.run(cmd, cwd=lane, env=env, capture_output=True, text=True, timeout=to); rc = r.returncode; tail = (r.stdout+r.stderr)[-400:]
    except subprocess.TimeoutExpired:
        rc, tail = "timeout", ""
    return rc, round(time.time()-t, 1), tail
for mid in ids:
    if mid == "CTRL":
        f = P+"power_guard.py"; old = new = None
    else:
        m = [x for x in MUTANTS if x[0] == mid][0]; f = P+m[2]; old, new = m[3], m[4]
    path = os.path.join(lane, f); src = open(path).read()
    if old is not None:
        assert src.count(old) == 1, (mid, src.count(old)); open(path, "w").write(src.replace(old, new))
    scripts = sorted([s for s, v in cl.items() if f in v and s not in SKIP and s.endswith(".py")], key=lambda s: rec.get(s, {}).get("seconds", 1e9))
    ran, killed = [], None
    try:
        for s in scripts:
            rc, sec, tail = run([py, s] if s != "tests/golden.py" else [py, s])
            ran.append([s, rc, sec])
            if rc != 0:
                killed = s; break
        if killed is None:
            rc, sec, tail = run([py, "tests/env_drift.py", "--all", BASE])
            ran.append(["tests/env_drift.py --all", rc, sec])
            if rc != 0: killed = "tests/env_drift.py --all"
    finally:
        open(path, "w").write(src)
    print(json.dumps({"id": mid, "file": f, "ran": ran, "killed_by": killed, "tail": tail if killed else ""}), flush=True)
    print(f"RESULT {mid}_killed={0 if killed is None else 1} bool", flush=True)
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT thread_factor=1.00  (subprocess-only harness: no in-process numeric work)")
