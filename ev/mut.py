import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1])
M = [
 ("M1 band dropped", "tools/audit/machinery_ratchet.py", "past = m[c] > t + doc[c + BAND_SUFFIX]", "past = m[c] > t"),
 ("M2 merge filter ==3 -> >=2", "tools/audit/machinery_ratchet.py", "if len(line.split()) == 3)", "if len(line.split()) >= 2)"),
 ("M3 base or head -> head", "tools/audit/machinery_ratchet.py", "scheduled_target(repo, base or head,", "scheduled_target(repo, head,"),
 ("M4 max(0,...) removed", "tools/audit/machinery_ratchet.py", "return max(0, cap - tdoc[\"step\"] * (n // tdoc[\"every_merges\"])), n", "return cap - tdoc[\"step\"] * (n // tdoc[\"every_merges\"]), n"),
 ("M5 slots > PRODUCTION_SLOTS removed", "tools/audit/seat/pr_cap.py", "isinstance(v, int) and v > PRODUCTION_SLOTS else None", "isinstance(v, int) else None"),
 ("M6 dispatch-gate machinery wiring off", "tools/audit/seat/pr_cap.py", "if rc == 0 and slug is not None:", "if False:"),
]
cmd = {"tools/audit/machinery_ratchet.py": ["python3", "tools/audit/machinery_ratchet.py", "--self-test"],
       "tools/audit/seat/pr_cap.py": ["python3", "tools/audit/seat/pr_cap.py", "--self-test"]}
for name, f, old, new in M:
    p = wt / f; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd[f], cwd=wt, capture_output=True, text=True)
    finally:
        p.write_text(src)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l or "self-test" in l][-4:]
    print(f"RESULT {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVES'}")
    for l in tail: print("   ", l)
for f, c in cmd.items():
    r = subprocess.run(c, cwd=wt, capture_output=True, text=True)
    print(f"RESULT unmutated {f}: rc={r.returncode}", (r.stdout + r.stderr).strip().splitlines()[-1])
