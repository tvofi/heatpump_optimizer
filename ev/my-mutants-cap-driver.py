import subprocess, sys, pathlib
R="tools/plan/replan.py"
M = [
 ("cap-default-569", R, 'hours * float(durations.get("live_remaining_fraction", 0.7)))', 'hours * float(durations.get("live_remaining_fraction", 0.9)))'),
 ("cap-default-572", R, 'hours *= float(durations.get("live_remaining_fraction", 0.7))', 'hours *= float(durations.get("live_remaining_fraction", 0.9))'),
]
for name, f, old, new in M:
    p = pathlib.Path(f); src = p.read_text()
    n = src.count(old)
    if n != 1: print(f"RESULT mutant={name} NOT-APPLIED count={n}"); continue
    p.write_text(src.replace(old, new))
    try:
        cp = subprocess.run([sys.executable, f, "--self-test"], capture_output=True, text=True, timeout=400)
        out = cp.stdout + cp.stderr
        fails=[l for l in out.splitlines() if "FAIL" in l]
        print(f"RESULT mutant={name} rc={cp.returncode} fails={len(fails)} {'KILLED' if cp.returncode else 'SURVIVED'}", fails[:2])
    finally:
        p.write_text(src)
