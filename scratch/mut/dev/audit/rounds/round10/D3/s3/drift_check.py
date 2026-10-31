#!/usr/bin/env python3
"""D3-s3 differential arm of the pre-screen (D3.M2): env_drift --all against the baseline for a
mutant that the closure's assertion scripts did not kill. env_drift refuses a ref resolving to HEAD,
so the mutant is committed (detached, local object only) on top of the baseline in a clean lane
worktree, then the lane is reset to the baseline.
Metric: env_drift.py --all <baseline> exit code with the mutant committed (0 = no golden moved).
Command (repo root of a clean detached worktree at the baseline):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D3/s3/drift_check.py . CTRL M04 ...
Control: CTRL commits nothing but an empty commit and must exit 0. Baseline 17f1c55fad1b."""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import json, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutants import MUTANTS, P
BASE = "17f1c55fad1bc97daf27174f2fbd6a18210d1fb7"
lane = os.path.abspath(sys.argv[1])
env = dict(os.environ, PYTHONPATH="tests/hastub", GIT_AUTHOR_NAME="d3s3", GIT_AUTHOR_EMAIL="d3s3@invalid", GIT_COMMITTER_NAME="d3s3", GIT_COMMITTER_EMAIL="d3s3@invalid")
g = lambda *a: subprocess.run(["git", *a], cwd=lane, env=env, check=True, capture_output=True)
for mid in sys.argv[2:]:
    g("reset", "-q", "--hard", BASE)
    if mid == "CTRL":
        g("commit", "-q", "--allow-empty", "--no-verify", "-m", "ctrl")
    else:
        m = [x for x in MUTANTS if x[0] == mid][0]; f = os.path.join(lane, P + m[2]); s = open(f).read()
        assert s.count(m[3]) == 1; open(f, "w").write(s.replace(m[3], m[4]))
        g("commit", "-q", "-a", "--no-verify", "-m", mid)
    t = time.time()
    r = subprocess.run([sys.executable, "tests/env_drift.py", "--all", BASE], cwd=lane, env=env, capture_output=True, text=True)
    g("reset", "-q", "--hard", BASE)
    out = r.stdout + r.stderr
    moved = [l.strip()[:160] for l in out.splitlines() if "DRIFT" in l or "moved" in l.lower()][:6]
    print(json.dumps({"id": mid, "rc": r.returncode, "sec": round(time.time()-t, 1), "moved": moved, "tail": out[-300:]}), flush=True)
    print(f"RESULT {mid}_drift_rc={r.returncode} exitcode", flush=True)
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT thread_factor=1.00  (subprocess-only harness)")
