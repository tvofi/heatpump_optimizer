import sys, os, subprocess, re
sys.path.insert(0, "/home/user/mut"); import spec
from score import fails
slot, which = sys.argv[1], sys.argv[2:]
items = {m[0]: m for m in spec.CALLER + spec.OWNER}
env = dict(os.environ, PYTHONPATH=f"{slot}/tests/hastub")
for mid in which:
    _, f, old, new, scripts, expect = items[mid]
    order = [s for s in ("dst_checks", "entities", "features") if s in scripts]
    if mid.startswith("O-P6"): order = ["entities"] + [s for s in order if s != "entities"]
    p = os.path.join(slot, f); orig = open(p).read()
    if orig.count(old) != 1: print(f"MUTANT {mid} NOT-APPLIED", flush=True); continue
    open(p, "w").write(orig.replace(old, new))
    try:
        for s in order:
            r = subprocess.run([sys.executable, f"tests/{s}.py"], cwd=slot, env=env, capture_output=True, text=True)
            lp = f"/home/user/mut/log_{mid}_{s}.txt"; open(lp, "w").write(r.stdout + r.stderr)
            fset, summ, _ = fails(lp); b = fails(f"/home/user/base_{s}.log")[0]
            if (fset - b) or summ.startswith("NO-SUMMARY"):
                print(f"MUTANT {mid} killed in {s}", flush=True); break
        else:
            print(f"MUTANT {mid} survived all", flush=True)
    finally:
        open(p, "w").write(orig)
