import subprocess, sys, pathlib
M = [
 ("check-cc", "tools/plan/replan.py", 'if s.get("closure_conditions") != list(CLOSURE_CONDITIONS):', 'if False:', ["tools/plan/replan.py"]),
 ("hot-notdone", "tools/audit/seat/plan_page.py", '"hot": g in gating_crit and g not in done and', '"hot": g in gating_crit and', ["tools/audit/seat/plan_page.py"]),
 ("hot-discharged", "tools/audit/seat/plan_page.py", "if a in G and a not in discharged and roster_lib.gates(G[a])}", "if a in G and roster_lib.gates(G[a])}", ["tools/audit/seat/plan_page.py"]),
 ("hot-gates", "tools/audit/seat/plan_page.py", "if a in G and a not in discharged and roster_lib.gates(G[a])}", "if a in G and a not in discharged}", ["tools/audit/seat/plan_page.py"]),
 ("hot-render", "tools/audit/seat/plan_page.py", "           if r[\"hot\"] else \"\")", "           if False else \"\")", ["tools/audit/seat/plan_page.py"]),
 ("zero-other", "tools/audit/seat/plan_page.py", None, None, ["tools/audit/seat/plan_page.py"]),
]
only = sys.argv[1:]
for name, f, old, new, runs in M:
    if only and name not in only: continue
    p = pathlib.Path(f); src = p.read_text()
    if old is None: continue
    n = src.count(old)
    if n != 1: print(f"RESULT mutant={name} NOT-APPLIED count={n}"); continue
    p.write_text(src.replace(old, new))
    try:
        rcs=[]
        for r in runs:
            cp = subprocess.run([sys.executable, r, "--self-test"], capture_output=True, text=True, timeout=200)
            fails=[l for l in cp.stdout.splitlines() if l.startswith("FAIL")]
            rcs.append((r, cp.returncode, len(fails), fails[:2], cp.stderr.strip().splitlines()[-1:] ))
        print(f"RESULT mutant={name}", rcs)
    finally:
        p.write_text(src)
