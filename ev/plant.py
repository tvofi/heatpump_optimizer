# plant one hand mutant in tools/audit/seat/beat_jobs.py of a detached head worktree (cwd), run --self-test --no-mutants, restore
import sys, subprocess
from pathlib import Path
f = Path("tools/audit/seat/beat_jobs.py")
name, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
orig = f.read_text()
assert orig.count(old) == 1, f"{name}: anchor count {orig.count(old)}"
f.write_text(orig.replace(old, new))
try:
    p = subprocess.run([sys.executable, "-I", str(f), "--self-test", "--no-mutants"], capture_output=True, text=True)
finally:
    f.write_text(orig)
out = (p.stdout + p.stderr).splitlines()
print(f"MUTANT {name} rc={p.returncode}")
for l in out:
    if "FAIL" in l or "checks" in l or "Error" in l: print("  ", l)
