import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
M = [
 ("M1_broken_guard_dropped", "tools/ci/selftest_scope.py", "and refuse and not gaps and not broken and table", "and refuse and not gaps and table", ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M2_gaps_guard_dropped", "tools/ci/selftest_scope.py", "and refuse and not gaps and not broken and table", "and refuse and not broken and table", ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M3_missing_step_not_drop", "tools/ci/selftest_scope.py", 'gone = sorted(f"MISSING step', 'gone = [] and sorted(f"MISSING step', ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M4_remain_not_printed", "tools/ci/selftest_scope.py", 'print(f"selftest_scope absorb: {len(remain)} refusal(s)', 'print(f"selftest_scope absorb: {0} refusal(s)', ["python3","-I","tools/ci/selftest_scope.py","--self-test"]),
 ("M5_hold_ahead_zero", "tools/audit/seat/orchestrator_tick.py", "ahead.isdigit() and int(ahead) > 0", "ahead.isdigit() and int(ahead) >= 0", ["python3","tools/audit/seat/orchestrator_tick.py","--self-test"]),
 ("M6_hold_any_lane", "tools/audit/seat/orchestrator_tick.py", "if not cid or not name.endswith(SELFTEST_JOB):", "if not cid:", ["python3","tools/audit/seat/orchestrator_tick.py","--self-test"]),
 ("M7_verify_regen_clean_ok", "tools/audit/seat/selftest_absorb.py", "    if rc != 1:\n        return 1, [f\"SELFTEST-ABSORB VERIFY-REFUSED regeneration", "    if rc == 2:\n        return 1, [f\"SELFTEST-ABSORB VERIFY-REFUSED regeneration", ["python3","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M8_absorb_rc_ignored", "tools/audit/seat/selftest_absorb.py", "    if rc != 0 or not added:\n", "    if not added:\n", ["python3","tools/audit/seat/selftest_absorb.py","--self-test"]),
 ("M9_jobs_total_unchecked", "tools/audit/seat/selftest_absorb.py", 'if jobs.get("total_count", 0) > len(jobs.get("jobs", [])):', 'if False:', ["python3","tools/audit/seat/selftest_absorb.py","--self-test"]),
]
for name, path, old, new, cmd in M:
    p = root / path; src = p.read_text()
    if src.count(old) != 1:
        print(f"{name}: SITE COUNT {src.count(old)}"); continue
    p.write_text(src.replace(old, new, 1))
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=900)
        fails = [l for l in r.stdout.splitlines() if "FAIL" in l][:3]
        last = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} :: {last} :: {fails}")
    finally:
        p.write_text(src)
