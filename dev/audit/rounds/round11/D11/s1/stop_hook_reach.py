#!/usr/bin/env python3
"""D11-s1 round 11: the Stop hook's reach over the policy corpus.

Metric (one line): of the policy-corpus files `policy_lint.mjs --corpus-filter`
prints, how many the production Stop hook `.claude/hooks/stop-selfcheck.sh`
lets a turn end on (exit 0) when the turn's ONLY change is that file and the
corpus linter is red. Count key: the hook's own exit status, end to end.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/stop_hook_reach.py
    ... --perturb    # the one-line production edit: AGENTS.md and dev/audit/ joined to POLICY_PREFIXES
Expected: RESULT missed=2 (AGENTS.md, dev/audit/README.md), exact; under --perturb missed=0.
Null control: a production-only change (custom_components/x.py) exits 0 and a
CLAUDE.md change exits 2 in the same scratch repository.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).

Instrumented symbol: .claude/hooks/stop-selfcheck.sh:POLICY_PREFIXES/touches_policy
(driven through the hook's main path, never re-implemented here).
Perturbation: POLICY_PREFIXES gains `AGENTS\\.md|dev/audit/` -> missed goes to 0 (down).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import shutil
import subprocess
import sys
import tempfile
import time

HOOK = ".claude/hooks/stop-selfcheck.sh"
PERTURB = "--perturb" in sys.argv


def sh(args, cwd, **kw):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kw)


def corpus():
    files = sh(["git", "ls-files"], ".").stdout
    out = subprocess.run(["node", "tools/policy/policy_lint.mjs", "--corpus-filter"], input=files,
                         capture_output=True, text=True, env={**os.environ, "HPO_PLANDATA": os.path.join(ROOT_TMP, "pd")})
    return [l for l in out.stdout.split("\n") if l.strip()]


def hook_text():
    src = open(HOOK).read()
    if PERTURB:
        old = "POLICY_PREFIXES='^(CLAUDE\\.md|"
        assert old in src, "perturbation did not apply"
        src = src.replace(old, "POLICY_PREFIXES='^(AGENTS\\.md|dev/audit/|CLAUDE\\.md|", 1)
    return src


def repo(base, hook):
    t = tempfile.mkdtemp(dir=base)
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    sh(["git", "init", "-q"], t, env=env)
    os.makedirs(os.path.join(t, ".claude/hooks"))
    os.makedirs(os.path.join(t, ".claude/workflows"))
    with open(os.path.join(t, ".git/info/exclude"), "a") as f:
        f.write(".claude/workflows/policy_lint.mjs\n.claude/hooks/stop-selfcheck.sh\n")
    with open(os.path.join(t, "seed.txt"), "w") as f:
        f.write("seed\n")
    sh(["git", "add", "-A"], t, env=env)
    sh(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"], t, env=env)
    sh(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], t, env=env)
    with open(os.path.join(t, HOOK), "w") as f:
        f.write(hook)
    with open(os.path.join(t, ".claude/workflows/policy_lint.mjs"), "w") as f:
        f.write("process.exit(1)\n")              # the corpus is red
    return t, env


def drive(base, hook, rel):
    t, env = repo(base, hook)
    p = os.path.join(t, rel)
    os.makedirs(os.path.dirname(p) or t, exist_ok=True)
    with open(p, "w") as f:
        f.write("changed\n")
    r = subprocess.run(["bash", HOOK], cwd=t, input="{}", capture_output=True, text=True,
                       env={**env, "CLAUDE_PROJECT_DIR": t})
    shutil.rmtree(t, ignore_errors=True)
    return r.returncode


ROOT_TMP = tempfile.mkdtemp(prefix="d11s1-stop-")
c0, t0 = time.process_time(), time.thread_time()
hook = hook_text()
files = corpus()
missed = [f for f in files if drive(ROOT_TMP, hook, f) == 0]
null_prod = drive(ROOT_TMP, hook, "custom_components/x.py")
pos_claude = drive(ROOT_TMP, hook, "CLAUDE.md")
for f in missed:
    print("MISSED", f)
print(f"RESULT corpus={len(files)} files")
print(f"RESULT missed={len(missed)} files")
print(f"RESULT null_control_production_only_rc={null_prod} exit")
print(f"RESULT positive_control_claude_md_rc={pos_claude} exit")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
shutil.rmtree(ROOT_TMP, ignore_errors=True)
