import subprocess, sys, pathlib, runpy
sys.argv = [sys.argv[0], sys.argv[1]]
ST = ["python3", "-I", "tools/ci/selftest_scope.py", "--self-test"]
src = open(pathlib.Path(__file__).with_name("drive.py")).read()
M2 = [
 ("M4b precheck: ignores a holding tracer", "tools/ci/selftest_scope.py",
  '    if shutil.which("strace") is None or _traced():\n        print(f"selftest_scope precheck: skip',
  '    if shutil.which("strace") is None:\n        print(f"selftest_scope precheck: skip', ST),
 ("M7b step_commands: bg_run launcher forgotten", "tools/ci/selftest_scope.py",
  r'        if re.search(rf"\bbg_(?:start|run) {re.escape(n)}\b", line)) for s in steps if s.gated}',
  r'        if re.search(rf"\bbg_(?:start) {re.escape(n)}\b", line)) for s in steps if s.gated}', ST),
 ("M5a absorb_cli: ignored probes not gone", "tools/ci/selftest_scope.py",
  '    gone = _ignored(root, probes) | {p for p in probes', '    gone = set() | {p for p in probes', ST),
 ("M5b absorb_cli: retired probes not gone", "tools/ci/selftest_scope.py",
  '    retired = [r.rstrip("/") for r in retired_paths(root)]\n', '    retired = []\n', ST),
]
src = src.replace("M = [", "M = M2 + [][:0] + [", 1).replace("for name, f, old, new, cmd in M:", "for name, f, old, new, cmd in M2:")
exec(compile(src, "drive", "exec"), {"M2": M2, "__name__": "__main__"})
