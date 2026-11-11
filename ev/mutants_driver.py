import subprocess, sys, pathlib
muts = [
 ("M1 app_push: push not under gh_read retry", "tools/pr/app_push.sh",
  'GIT_TERMINAL_PROMPT=0 python3 "$(cd "$(dirname -- "$0")/../audit/seat" && pwd)/gh_read.py" --git-retry \\\n    git', 'GIT_TERMINAL_PROMPT=0 git', "bash tools/pr/app_push.sh --self-test"),
 ("M2a shim: worktree admit never sets ok", "tools/audit/seat/shims/seat-gh",
  '[ "$wl" = "worktree $troot" ] && ok=1', ':', "python3 -I tools/audit/seat/gh_calls.py --self-test"),
 ("M2b shim: ls-files tracked check dropped", "tools/audit/seat/shims/seat-gh",
  'git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1', 'true', "python3 -I tools/audit/seat/gh_calls.py --self-test"),
 ("M2c shim: broot!=gcpy guard dropped", "tools/audit/seat/shims/seat-gh",
  '[ "$broot" != "$gcpy" ] && ', '', "python3 -I tools/audit/seat/gh_calls.py --self-test"),
 ("M3a codescan: carried_over False", "tools/ci/codescan_wait.py",
  'return j.get("status") == "completed" and j.get("conclusion") == "success" and "steps" not in j', 'return False', "python3 -I tools/ci/codescan_wait.py --self-test"),
 ("M3b codescan: steps-absent clause dropped", "tools/ci/codescan_wait.py",
  ' and "steps" not in j', '', "python3 -I tools/ci/codescan_wait.py --self-test"),
 ("M3c codescan: conclusion clause dropped", "tools/ci/codescan_wait.py",
  ' and j.get("conclusion") == "success" and "steps"', ' and "steps"', "python3 -I tools/ci/codescan_wait.py --self-test"),
 ("M3d codescan: status clause dropped", "tools/ci/codescan_wait.py",
  'return j.get("status") == "completed" and j.get("conclusion")', 'return j.get("conclusion")', "python3 -I tools/ci/codescan_wait.py --self-test"),
 ("M4a ci_ratchet: single read", "tests/ci_ratchet.py",
  'gh_read.retry(attempt, gh_read.gh_wait, sleep or time.sleep)', '(lambda r: (r[0], r[1], 1, "once"))(attempt())', "PYTHONPATH=tests/hastub python3 -I tests/ci_ratchet.py --self-test"),
 ("M4b ci_ratchet: retry every failure", "tests/ci_ratchet.py",
  'gh_read.retry(attempt, gh_read.gh_wait, sleep or time.sleep)', 'gh_read.retry(attempt, lambda *a, **k: 1, sleep or time.sleep)', "PYTHONPATH=tests/hastub python3 -I tests/ci_ratchet.py --self-test"),
 ("M4c ci_ratchet: empty stdout not a failure", "tests/ci_ratchet.py",
  'if proc.returncode != 0 or not (proc.stdout or "").strip():\n                return proc, (proc.stderr', 'if proc.returncode != 0:\n                return proc, (proc.stderr', "PYTHONPATH=tests/hastub python3 -I tests/ci_ratchet.py --self-test"),
]
for name, f, a, b, cmd in muts:
    p = pathlib.Path(f); orig = p.read_text()
    if orig.count(a) != 1:
        print(f"{name}: ANCHOR-MISS count={orig.count(a)}"); continue
    p.write_text(orig.replace(a, b))
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    p.write_text(orig)
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith(("FAIL", "fail", "BAD", "not ok", "x "))]
    summ = [l for l in out.splitlines() if "failed" in l and "checks" in l]
    print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {summ[-1] if summ else ''} | {fails[:3]}")
