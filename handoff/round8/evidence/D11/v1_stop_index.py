#!/usr/bin/env python3
"""v1_stop_index.py -- D11-v1 (verifier) own measurement for D11-s1-03.

METRIC (one line): of six end-of-turn working-copy states that each carry a
change to a policy path (CLAUDE.md or a new .claude/rules file) not yet on the
branch's committed diff -- or on it -- the number in which the REAL
`.claude/hooks/stop-selfcheck.sh`, run as a process with CLAUDE_PROJECT_DIR at a
scratch repository whose `.claude/workflows/policy_lint.mjs` is a stub that
exits 1, exits 0 (lets the turn end over a red corpus).

States: committed | unstaged | staged | staged_new | untracked_new |
staged_then_reverted_worktree (staged edit, worktree restored to HEAD).
The finder's four are the first four; the last two are mine.

NULL CONTROL: the same six states with a stub linter exiting 0 -> every state
exits 0 (null_red_blocks=0 means nothing refuses a green corpus); and a
production-only change (custom_components/x.py, staged) with a red stub exits 0
by design (not counted).

PERTURBATION (--perturb): the hook's CHANGED line gets `; git diff --cached
--name-only 2>/dev/null` appended, in a temp copy. Expected: blind states drop
by the staged-index states (staged, staged_new) -> the
untracked_new state remains (direction: down).

RUN (tree root): PYTHONPATH=tests/hastub TMPDIR=/home/claude/audit-r8/tmp/D11-v1 \
   python3 tools/audit/round8/D11/v1_stop_index.py [--perturb]
EXPECTED at cdf82da: blind_states=3 of 6 (staged, staged_new, untracked_new;
  staged_then_reverted_worktree is caught by the unstaged diff), blind_finder_four=2,
  perturbed 1 (untracked_new) / 0.
BASELINE: cdf82daabcfe3777d98b31489f36df5555ec9d82. MACHINE: 4-vCPU cloud container; no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import shutil, subprocess, sys, tempfile, time
from pathlib import Path

HOOK = Path(".claude/hooks/stop-selfcheck.sh").resolve()
LINE = 'CHANGED=$(git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only 2>/dev/null)'


def sh(cwd, *a):
    subprocess.run(a, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def scratch(root, lint_rc):
    origin = root / "origin.git"; w = root / "w"
    sh(root, "git", "init", "-q", "--bare", str(origin))
    sh(root, "git", "init", "-q", "-b", "main", str(w))
    for k, v in (("user.email", "v@x"), ("user.name", "v"), ("commit.gpgsign", "false")):
        sh(w, "git", "config", k, v)
    (w / "CLAUDE.md").write_text("policy\n")
    (w / ".claude/workflows").mkdir(parents=True)
    (w / ".claude/rules").mkdir(parents=True)
    (w / ".claude/workflows/policy_lint.mjs").write_text(f"process.exit({lint_rc})\n")
    (w / "custom_components").mkdir()
    (w / "custom_components/x.py").write_text("x = 1\n")
    sh(w, "git", "add", "-A"); sh(w, "git", "commit", "-qm", "base")
    sh(w, "git", "remote", "add", "origin", str(origin)); sh(w, "git", "push", "-q", "origin", "main")
    sh(w, "git", "fetch", "-q", "origin")
    sh(w, "git", "checkout", "-q", "-b", "feature")
    return w


def apply(w, state):
    if state == "committed":
        (w / "CLAUDE.md").write_text("policy\nmore\n"); sh(w, "git", "commit", "-qam", "c")
    elif state == "unstaged":
        (w / "CLAUDE.md").write_text("policy\nmore\n")
    elif state == "staged":
        (w / "CLAUDE.md").write_text("policy\nmore\n"); sh(w, "git", "add", "CLAUDE.md")
    elif state == "staged_new":
        (w / ".claude/rules/new.md").write_text("rule\n"); sh(w, "git", "add", ".claude/rules/new.md")
    elif state == "untracked_new":
        (w / ".claude/rules/new.md").write_text("rule\n")
    elif state == "staged_then_reverted_worktree":
        (w / "CLAUDE.md").write_text("policy\nmore\n"); sh(w, "git", "add", "CLAUDE.md")
        (w / "CLAUDE.md").write_text("policy\n")
    elif state == "prod_staged":
        (w / "custom_components/x.py").write_text("x = 2\n"); sh(w, "git", "add", "-A")


STATES = ["committed", "unstaged", "staged", "staged_new", "untracked_new", "staged_then_reverted_worktree"]


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    base = Path(tempfile.mkdtemp(prefix="v1stop-"))
    hook = base / "hook.sh"
    text = HOOK.read_text()
    assert text.count(LINE) == 1, "CHANGED line moved"
    if perturb:
        text = text.replace(LINE, LINE[:-1] + "; git diff --cached --name-only 2>/dev/null)")
    hook.write_text(text)
    res = {}
    try:
        for lint_rc in (1, 0):
            for st in STATES + ["prod_staged"]:
                root = base / f"{lint_rc}-{st}"; root.mkdir()
                w = scratch(root, lint_rc); apply(w, st)
                rc = subprocess.run(["bash", str(hook)], input=b"{}", cwd=w,
                                    env=dict(os.environ, CLAUDE_PROJECT_DIR=str(w)),
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
                res[(lint_rc, st)] = rc
                print(f"# lint_rc={lint_rc} {st:30} hook rc={rc}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    blind = [s for s in STATES if res[(1, s)] == 0]
    print(f"# blind (red corpus, hook exits 0): {blind}")
    print(f"RESULT states={len(STATES)} count")
    print(f"RESULT blind_states={len(blind)} count")
    print(f"RESULT blind_finder_four={len([s for s in blind if s in STATES[:4]])} count")
    print(f"RESULT null_red_blocks={sum(1 for s in STATES if res[(0, s)] != 0)} count")
    print(f"RESULT prod_staged_red_rc={res[(1, 'prod_staged')]}")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
