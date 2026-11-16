#!/usr/bin/env python3
"""D11-s1 round 11: rules_sync.mjs --check is a refusal with no positive control.

Metric (one line): whether the control D11.md M1 names for a non-policy_lint
instrument -- its `--self-test` -- goes red on a tree whose generated rule has
drifted (1 = red, 0 = exits 0); beside it, whether `--check` refuses the same
tree (the refusal is alive) and how many files the `--self-test` call rewrote.
Count key: the production script's own exit status and the drifted file's bytes.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/rules_sync_control.py
    ... --perturb   # one-line edit: `const check = ... || process.argv.includes('--self-test')`
Expected: RESULT control_red_on_drift=0, check_refuses_drift=1, selftest_rewrote=1 (exact);
under --perturb control_red_on_drift=1 (up) and selftest_rewrote=0.
Null control: the in-sync copy -- `--check` exits 0 and `--self-test` writes nothing.
Every run is on a temp copy (tools/policy, dev/governance/rules, .claude/rules,
.cursor/rules, tests/layout.json): the export's rules are never written.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: tools/policy/rules_sync.mjs:main.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import shutil
import subprocess
import sys
import tempfile
import time

PERTURB = "--perturb" in sys.argv
COPY = ["tools/policy", "dev/governance/rules", ".claude/rules", ".cursor/rules", "tests/layout.json"]


def tree(base):
    t = tempfile.mkdtemp(dir=base)
    for rel in COPY:
        dst = os.path.join(t, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        (shutil.copytree if os.path.isdir(rel) else shutil.copy2)(rel, dst)
    p = os.path.join(t, "tools/policy/rules_sync.mjs")
    src = open(p).read()
    if PERTURB:
        old = "const check = process.argv.includes('--check')"
        assert src.count(old) == 1, "perturbation did not apply"
        src = src.replace(old, old + " || process.argv.includes('--self-test')")
        open(p, "w").write(src)
    return t


def run(t, flag):
    r = subprocess.run(["node", "tools/policy/rules_sync.mjs", flag], cwd=t, capture_output=True, text=True,
                       env={**os.environ, "HPO_PLANDATA": os.path.join(t, "pd")})
    return r.returncode, r.stdout


def snapshot(t):
    return {p: open(p, "rb").read() for p in glob.glob(os.path.join(t, ".cursor/rules/*.mdc"))
            + glob.glob(os.path.join(t, ".claude/rules/*.md"))}


TMP = tempfile.mkdtemp(prefix="d11s1-rs-")
c0, t0 = time.process_time(), time.thread_time()
# Null control: in sync.
t = tree(TMP)
null_check, _ = run(t, "--check")
before = snapshot(t)
null_st, _ = run(t, "--self-test")
null_wrote = sum(1 for p, b in snapshot(t).items() if before.get(p) != b)
# Drift one generated rule.
t = tree(TMP)
victim = sorted(glob.glob(os.path.join(t, ".cursor/rules/*.mdc")))[0]
with open(victim, "a") as f:
    f.write("\nhand edit the generator does not make\n")
chk_rc, chk_out = run(t, "--check")
t2 = tree(TMP)
shutil.copy2(victim, os.path.join(t2, os.path.relpath(victim, t)))
before = snapshot(t2)
st_rc, st_out = run(t2, "--self-test")
wrote = sum(1 for p, b in snapshot(t2).items() if before.get(p) != b)
print(f"drifted: {os.path.relpath(victim, t)}")
print(f"--check on drift: rc={chk_rc}  {chk_out.strip().splitlines()[-1] if chk_out.strip() else ''}")
print(f"--self-test on drift: rc={st_rc}  {st_out.strip().splitlines()[-1] if st_out.strip() else ''}")
print(f"RESULT control_red_on_drift={1 if st_rc else 0} bool")
print(f"RESULT check_refuses_drift={1 if chk_rc else 0} bool")
print(f"RESULT selftest_rewrote={wrote} files")
print(f"RESULT null_check_rc={null_check} rc")
print(f"RESULT null_selftest_rewrote={null_wrote} files")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
shutil.rmtree(TMP, ignore_errors=True)
