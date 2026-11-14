import subprocess, sys, pathlib
p = pathlib.Path("tests/ci_ratchet.py"); orig = p.read_text()
M = {
 "M1 drop _cut_at_prelude term": (' or (kind == "CI" and _cut_at_prelude(jobs))', ''),
 "M2 prelude conjunct -> True": ('any(j.get("name") == PRELUDE_JOB and j.get("conclusion") == "cancelled" for j in jobs)', 'True'),
 "M3 drop bool(tests)": ('and bool(tests) and', 'and'),
 "M4 drop all-skipped": (' and all(j.get("conclusion") == "skipped" for j in tests))', ')'),
 "M5 TESTS_CALLER match disabled": ('str(j.get("name") or "") == TESTS_CALLER\n', 'False\n'),
 "M6 kind CI -> Tests": ('(kind == "CI" and _cut_at_prelude', '(kind == "Tests" and _cut_at_prelude'),
 "R1 prelude name check dropped (any cancelled job)": ('j.get("name") == PRELUDE_JOB and j.get("conclusion") == "cancelled"', 'j.get("conclusion") == "cancelled"'),
 "R2 all-skipped -> any-skipped": ('and all(j.get("conclusion") == "skipped" for j in tests)', 'and any(j.get("conclusion") == "skipped" for j in tests)'),
 "R3 tests/* prefix match disabled": ('or str(j.get("name") or "").startswith(TESTS_JOB_PREFIX)]', 'or False]'),
 "R4 kind guard dropped": ('(kind == "CI" and _cut_at_prelude(jobs))', '(_cut_at_prelude(jobs))'),
 "R5 skipped -> in (skipped, cancelled)": ('j.get("conclusion") == "skipped" for j in tests', 'j.get("conclusion") in ("skipped", "cancelled") for j in tests'),
}
killed = 0
for k, (a, b) in M.items():
    if orig.count(a) != 1: print(f"{k}: PATTERN COUNT {orig.count(a)}"); continue
    p.write_text(orig.replace(a, b))
    out = subprocess.run([sys.executable, "-I", "tests/ci_ratchet.py", "--self-test"], capture_output=True, text=True).stdout
    p.write_text(orig)
    fails = [l.strip()[:140] for l in out.splitlines() if "FAIL" in l]
    summ = [l for l in out.splitlines() if "self-test:" in l]
    st = "KILLED" if fails else "SURVIVED"; killed += bool(fails)
    print(f"{k}: {st} {summ}"); [print("   ", f) for f in fails]
print(f"RESULT mutants killed {killed} of {len(M)}")
