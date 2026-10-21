import sys, subprocess, importlib.util
mod_path, repo = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("mt", mod_path); mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)
def run(argv, cwd=repo):  # Tick.git's shape: stdout + stderr
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True); return r.returncode, r.stdout + r.stderr
for br in ("claims", "content", "m", "nope"):
    c = mt.conflicts(run, "m", br)
    files = c if c is not None else None
    rep = mt.dirty_repair(c, ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt")) if c else None
    print(f"RESULT {sys.argv[3]} conflicts(m,{br}) -> {c!r} ; dirty_repair -> {rep!r}")
r = subprocess.run(["git","merge-tree","--write-tree","--name-only","--no-messages","m","claims"], cwd=repo, capture_output=True, text=True)
print(f"control bare merge-tree m claims: rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
