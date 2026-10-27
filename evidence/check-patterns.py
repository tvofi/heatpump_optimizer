import importlib.util, sys
from pathlib import Path
hpath, root = sys.argv[1], Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("h", hpath)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.ROOT = root  # force ROOT to the head worktree
bad = 0
for m in h.MUTANTS:
    name, file, old, new = m[0], m[1], m[2], m[3]
    if not name.startswith("prepr-"):
        continue
    p = root / h.rel(file)
    if not p.is_file():
        print(f"{name}: MISSING FILE {p}"); bad += 1; continue
    n = p.read_text().count(old)
    ok = "OK" if n == 1 else "BAD"
    if n != 1: bad += 1
    print(f"{name}: {ok} match={n} file={h.rel(file)}")
print(f"RESULT bad={bad}")
sys.exit(1 if bad else 0)
