import subprocess, sys, pathlib
M = [
 ("M1", "tools/ci/selftest_scope.py", "and not gaps and not broken and table", "and not gaps and table", ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M2", "tools/ci/selftest_scope.py", "and not gaps and not broken and table", "and not broken and table", ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M5", "tools/audit/seat/orchestrator_tick.py", "int(ahead) > 0", "int(ahead) >= 0", ["python3","tools/audit/seat/orchestrator_tick.py","--self-test"]),
 ("M6", "tools/audit/seat/orchestrator_tick.py", "if not cid or not name.endswith(SELFTEST_JOB):", "if not cid:", ["python3","tools/audit/seat/orchestrator_tick.py","--self-test"]),
 ("M9", "tools/audit/seat/selftest_absorb.py", 'if jobs.get("total_count", 0) > len(jobs.get("jobs", [])):', "if False:", ["python3","-I","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M8", "tools/audit/seat/selftest_absorb.py", "    if rc != 0 or not added:", "    if not added:", ["python3","-I","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M7", "tools/audit/seat/selftest_absorb.py", "    if rc != 1:", "    if rc == 2:", ["python3","-I","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M10", "tools/audit/seat/selftest_absorb.py", '"--no-renames", ', "", ["python3","-I","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M11", "tools/audit/seat/selftest_absorb.py", "    stop_on_signal()\n    repo_dir", "    repo_dir", ["python3","-I","tools/audit/seat/selftest_absorb.py","--self-test"]),
]
for mid, f, old, new, cmd in M:
    p = pathlib.Path(f); src = p.read_text()
    if new is None:
        print(mid, "context:"); continue
    n = src.count(old)
    if n != 1: print(mid, "pattern count", n); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        tail = (r.stdout.strip().splitlines() or [""])[-1]
        print(mid, f, repr(old), "->", repr(new), "rc", r.returncode, "KILLED" if r.returncode else "SURVIVED", "|", tail, flush=True)
    finally:
        p.write_text(src)
