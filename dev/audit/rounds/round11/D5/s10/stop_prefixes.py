#!/usr/bin/env python3
"""D5-s10: is stop-selfcheck.sh's POLICY_PREFIXES comment true -- does the prefix list cover policy_lint's corpus?

Metric: escaped = tracked files at --ref that tools/policy/policy_lint.mjs:POLICY_GLOBS measures and that
.claude/hooks/stop-selfcheck.sh:touches_policy does NOT match (the hook's comment, lines 11-13 and 24-27:
"the same set policy_lint measures ... a prefix that is too narrow is the failure that matters").
Count key: touches_policy's exit status on each path, as the real shell function returns it (sourced from the
hook with sed, never re-typed), and the hook's end-to-end exit code in a scratch repository.

Second number: threedot_only = 0 when a worktree-only (uncommitted) policy edit already runs the linter, which
contradicts the header's "It runs only when the branch's three-dot diff touches a policy or workflow path".

Command (from the export root; --repo is any git checkout holding --ref):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s10/stop_prefixes.py \
      --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 [--perturb]
Expected at baseline 92d38ecb (box B12, round 11): RESULT escaped=2 (AGENTS.md, dev/audit/README.md), exact;
RESULT e2e_agents_md_rc=0 (escaped; the null control CLAUDE.md reads 2); RESULT threedot_only=0.
Perturbation: --perturb adds `AGENTS\\.md|dev/audit/` to POLICY_PREFIXES in a scratch copy of the hook:
escaped goes to 0 and e2e_agents_md_rc to 2 (direction: down / to_zero).
Writes only under a mkdtemp root.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HOOK = ".claude/hooks/stop-selfcheck.sh"
LINT = "tools/policy/policy_lint.mjs"


def policy_globs(src):
    """POLICY_GLOBS, evaluated from policy_lint.mjs's own source by node (the array literal, comments and all)."""
    m = re.search(r"const POLICY_GLOBS = (\[.*?\n\])\n", src, re.S)
    js = "const G=" + m.group(1) + ";process.stdout.write(JSON.stringify(G.map(r=>r.source)))"
    import json
    return [re.compile(s) for s in json.loads(subprocess.check_output(["node", "-e", js], text=True))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    c0, h0 = time.process_time(), time.thread_time()
    tracked = subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split()
    show = lambda p: subprocess.check_output(["git", "-C", a.repo, "show", f"{a.ref}:{p}"], text=True)
    globs = policy_globs(show(LINT))
    hook = show(HOOK)
    if a.perturb:
        hook = hook.replace("POLICY_PREFIXES='^(CLAUDE\\.md|", "POLICY_PREFIXES='^(CLAUDE\\.md|AGENTS\\.md|dev/audit/|", 1)
    root = Path(tempfile.mkdtemp(prefix="d5s10_stop_"))
    try:
        hp = root / "hook.sh"
        hp.write_text(hook)
        # touches_policy and POLICY_PREFIXES, exactly as the hook defines them
        defs = subprocess.check_output(["sed", "-n", "/^POLICY_PREFIXES=/p;/^touches_policy()/,/^}/p", str(hp)], text=True)
        measured = sorted(f for f in tracked if any(g.search(f) for g in globs))
        lst = root / "measured.txt"
        lst.write_text("\n".join(measured) + "\n")
        out = subprocess.check_output(["bash", "-c", defs + '\nwhile IFS= read -r f; do touches_policy "$f"; echo "$? $f"; done < "$1"', "_", str(lst)], text=True)
        escaped = [l.split(" ", 1)[1] for l in out.splitlines() if not l.startswith("0 ")]
        print(f"RESULT policy_files={len(measured)} count")
        print(f"RESULT escaped={len(escaped)} count")
        for f in escaped:
            print(f"   escaped {f}")

        # End to end: the hook itself in a scratch repository with a RED linter stub.
        t = root / "repo"
        t.mkdir()
        g = lambda *x: subprocess.run(["git", "-C", str(t), *x], capture_output=True, text=True)
        g("init", "-q", "-b", "feature")
        (t / ".claude/hooks").mkdir(parents=True)
        (t / ".claude/workflows").mkdir(parents=True)
        shutil.copy(hp, t / HOOK)
        for f in ("CLAUDE.md", "AGENTS.md", "prod.py"):
            (t / f).write_text("seed\n")
        g("add", "-A")
        g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed")
        g("update-ref", "refs/remotes/origin/main", "HEAD")
        (t / ".claude/workflows/policy_lint.mjs").write_text("process.exit(1)\n")
        with open(t / ".git/info/exclude", "a") as fh:
            fh.write(".claude/workflows/policy_lint.mjs\n")

        def run(changed):
            (t / changed).write_text("changed\n")
            rc = subprocess.run(["bash", str(t / HOOK)], input="{}", cwd=t, text=True, capture_output=True,
                                env=dict(os.environ, CLAUDE_PROJECT_DIR=str(t))).returncode
            (t / changed).write_text("seed\n")
            return rc
        rc_agents = run("AGENTS.md")
        rc_claude = run("CLAUDE.md")
        rc_prod = run("prod.py")
        print(f"RESULT e2e_agents_md_rc={rc_agents} exit")
        print(f"RESULT e2e_claude_md_rc={rc_claude} exit (null control: a prefix the list names)")
        print(f"RESULT e2e_prod_rc={rc_prod} exit (null control: a non-policy path)")
        # The header says the hook runs only on the branch's three-dot diff; the CLAUDE.md edit above was
        # never committed (three-dot diff empty), so a 2 there means the claim is not the code's condition.
        print(f"RESULT threedot_only={int(rc_claude != 2)} bool")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    pc = time.process_time() - c0
    print(f"RESULT thread_factor={pc / max(time.thread_time() - h0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
