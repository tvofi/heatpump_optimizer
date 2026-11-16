import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1])
ST = ["python3", "-I", "tools/ci/selftest_scope.py", "--self-test"]
CP = ["python3", "tools/pr/ci_predict.py", "--self-test"]
FB = ["python3", "tools/pr/figure_block.py", "--self-test"]
M = [
 ("M1 absorb here(): git reads never carried", "tools/ci/selftest_scope.py",
  '        if kind == "git":\n            return True', '        if kind == "git":\n            return False', ST),
 ("M2 absorb: a flag added is not listed", "tools/ci/selftest_scope.py",
  '            added += [f"step {sid}: {k}" for k in FLAG_KINDS if merged[k] and not old.get(k)]\n', '', ST),
 ("M3 base_drift: no mb==HEAD short-circuit", "tools/ci/selftest_scope.py",
  'if not hit or mb == (git("rev-parse", "HEAD") or "").strip():', 'if not hit:', ST),
 ("M4 precheck: ignores a holding tracer", "tools/ci/selftest_scope.py",
  'if shutil.which("strace") is None or _traced():', 'if shutil.which("strace") is None:', ST),
 ("M5 absorb_cli: gone is empty", "tools/ci/selftest_scope.py",
  '    gone = _ignored(root, probes) | {p for p in probes', '    gone = set() & {p for p in probes', ST),
 ("M6 scratch clone: tags not copied", "tools/ci/selftest_scope.py",
  '        "+refs/tags/*:refs/tags/*", check=False)', '        check=False)', ST),
 ("M7 step_commands: bg_run launcher forgotten", "tools/ci/selftest_scope.py",
  r'\bbg_(?:start|run) ', r'\bbg_(?:start) ', ST),
 ("M8 drift only: other steps graded", "tools/ci/selftest_scope.py",
  '        if only is not None and sid not in only:\n            continue\n', '', ST),
 ("M9 ci_predict: rc 3 not a note", "tools/pr/ci_predict.py",
  '    if r.returncode == 3:', '    if r.returncode == 99:', CP),
 ("M10 ci_predict: rc 0 path dropped", "tools/pr/ci_predict.py",
  '    if r.returncode == 0:\n        return []\n', '', CP),
 ("M11 figure_block: no skip-worktree", "tools/pr/figure_block.py",
  '        _git(wt, "update-index", "--skip-worktree", "--", *tracked)', '        pass', FB),
 ("M12 figure_block: index not reset to head", "tools/pr/figure_block.py",
  '    _git(wt, "reset", "-q", head, "--", *files)\n', '', FB),
 ("M13 figure_block: base-only file not excluded", "tools/pr/figure_block.py",
  'for f in files if f not in tracked))', 'for f in files if False))', FB),
 ("M14 figure_block: excludes env not returned", "tools/pr/figure_block.py",
  '    return {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile", "GIT_CONFIG_VALUE_0": exclude}', '    return {}', FB),
 ("M15 scratch clone: origin url not set", "tools/ci/selftest_scope.py",
  '        git("remote", "set-url", "origin", url)', '        pass', ST),
 ("M16 trace_steps: BASH_ENV kept", "tools/ci/selftest_scope.py",
  '        env.pop("BASH_ENV", None)\n', '', ST),
]
for name, f, old, new, cmd in M:
    p = wt / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"NOT-APPLIED {name} (count {src.count(old)})", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
        tail = [l for l in out.splitlines() if l.strip()][-1:] 
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {name} rc={r.returncode} {tail} {fails}", flush=True)
    finally:
        p.write_text(src)
subprocess.run(["git", "status", "--short"], cwd=wt)
