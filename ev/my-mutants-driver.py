import subprocess, sys, pathlib
P="tools/audit/seat/plan_page.py"
M = [
 ("hot-render", P, '           if r["hot"] else "")', '           if False else "")'),
 ("hot-gates", P, "if a in G and roster_lib.gates(G[a])}", "if a in G}"),
 ("hot-notdone", P, '"hot": g in gating_crit and g not in done and', '"hot": g in gating_crit and'),
 ("hot-dis", P, '"hot": g in gating_crit and g not in done and', '"hot": g in gating_crit and g not in (done - discharged) and'),
 ("hot-crit", P, "gating_crit = {a for c in crit if c in G for a", "gating_crit = {a for c in G for a"),
 ("hot-title", P, 'title="hotfix blocking a critical-path group"', 'title="hotfix"'),
 ("hot-allrows", P, '           if r["hot"] else "")', '           if True else "")'),
 ("hot-nothotfix", P, "g not in done and roster_lib.is_hotfix(entry),", "g not in done,"),
]
only = sys.argv[1:]
for name, f, old, new in M:
    if only and name not in only: continue
    if old is None: continue
    p = pathlib.Path(f); src = p.read_text()
    n = src.count(old)
    if n != 1: print(f"RESULT mutant={name} NOT-APPLIED count={n}"); continue
    p.write_text(src.replace(old, new))
    try:
        cp = subprocess.run([sys.executable, f, "--self-test"], capture_output=True, text=True, timeout=200)
        fails=[l for l in cp.stdout.splitlines() if l.startswith("FAIL")]
        print(f"RESULT mutant={name} rc={cp.returncode} fails={len(fails)} {'KILLED' if cp.returncode and fails else 'SURVIVED'}", fails[:2], cp.stderr.strip().splitlines()[-1:])
    finally:
        p.write_text(src)
