#!/usr/bin/env python3
"""s1_stop_hook_states.py -- worktree states in which the Stop hook lets a red policy corpus end the turn.

METRIC. `blind_states`: of four ways a turn can leave a POLICY path changed
(committed on the branch; modified unstaged; modified and staged with
`git add`; a new policy file staged), the number for which the REAL
`.claude/hooks/stop-selfcheck.sh` exits 0 while the linter it consults exits 1.
Every state is a policy-touching turn with a red corpus, so the hook's own
header ("refuses to let a seat end its turn with the policy corpus red, when the
turn touched the policy corpus") wants exit 2 for all four. Key: the hook
process's exit status, driven end to end over stdin as the harness runs it.

Production symbol: `.claude/hooks/stop-selfcheck.sh` -- the `CHANGED=` line,
which unions `git diff BASE...HEAD` and `git diff --name-only` (worktree vs
INDEX), so a change sitting in the index is in neither.

Method: the hook's own self-test fixture shape (a scratch repository, an
`origin/main` ref at the seed, a stub `.claude/workflows/policy_lint.mjs` whose
exit status the harness chooses). NULL CONTROL: the same four states with a
green stub must all exit 0 (`null_red_exits`=0).

PERTURBATION (--perturb): a temp copy of the hook whose CHANGED line also
unions `git diff --cached --name-only` (one-line edit). Expected: blind_states
2 -> 0.

RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_stop_hook_states.py [--perturb]
EXPECTED at baseline cdf82da: blind_states=2 (staged-modified, staged-new), exact.
MACHINE: 4-vCPU cloud container (round 8); needs git, bash, python3; no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK = Path(".claude/hooks/stop-selfcheck.sh").resolve()
OLD = 'CHANGED=$(git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only 2>/dev/null)'
NEW = 'CHANGED=$(git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null)'


def g(t, *a):
    subprocess.run(["git", "-C", str(t), "-c", "user.email=t@t", "-c", "user.name=t", *a],
                   check=True, capture_output=True)


def scratch(red):
    t = Path(tempfile.mkdtemp(prefix="s1stop-"))
    g(t, "init", "-q")
    (t / ".claude/workflows").mkdir(parents=True)
    (t / ".claude/rules").mkdir(parents=True)
    (t / "CLAUDE.md").write_text("seed\n")
    (t / "prod.py").write_text("seed\n")
    (t / ".claude/workflows/policy_lint.mjs").write_text("process.exit(0)\n")
    g(t, "add", "-A"); g(t, "commit", "-qm", "seed")
    g(t, "update-ref", "refs/remotes/origin/main", "HEAD")
    g(t, "checkout", "-qb", "feature")
    (t / ".claude/workflows/policy_lint.mjs").write_text("process.exit(1)\n" if red else "process.exit(0)\n")
    g(t, "update-index", "--assume-unchanged", ".claude/workflows/policy_lint.mjs")
    return t


def state(t, name):
    if name == "committed":
        (t / "CLAUDE.md").write_text("changed\n"); g(t, "add", "CLAUDE.md"); g(t, "commit", "-qm", "x")
    elif name == "unstaged":
        (t / "CLAUDE.md").write_text("changed\n")
    elif name == "staged":
        (t / "CLAUDE.md").write_text("changed\n"); g(t, "add", "CLAUDE.md")
    elif name == "staged_new":
        (t / ".claude/rules/new-rule.md").write_text("a new rule\n"); g(t, "add", ".claude/rules/new-rule.md")


def run_hook(hook, t):
    p = subprocess.run(["bash", str(hook)], input="{}", text=True, capture_output=True,
                       env={**os.environ, "CLAUDE_PROJECT_DIR": str(t)})
    return p.returncode


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    hook = HOOK
    if "--perturb" in sys.argv:
        src = HOOK.read_text()
        assert src.count(OLD) == 1, "perturbation anchor not found"
        d = Path(tempfile.mkdtemp(prefix="s1hook-"))
        hook = d / "stop-selfcheck.sh"
        hook.write_text(src.replace(OLD, NEW))
        print(f"# perturbation: CHANGED also unions the index, in a temp copy {hook}")
    states = ["committed", "unstaged", "staged", "staged_new"]
    blind, null_red = [], 0
    for s in states:
        t = scratch(red=True); state(t, s); rc = run_hook(hook, t); shutil.rmtree(t)
        tn = scratch(red=False); state(tn, s); rcn = run_hook(hook, tn); shutil.rmtree(tn)
        print(f"# {s:11s} red-corpus rc={rc} (want 2)   green-corpus rc={rcn} (want 0)")
        if rc == 0:
            blind.append(s)
        if rcn != 0:
            null_red += 1
    print(f"# blind: {blind}")
    print(f"RESULT states={len(states)} count")
    print(f"RESULT blind_states={len(blind)} count")
    print(f"RESULT null_red_exits={null_red} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
