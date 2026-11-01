# Finder's ev/run.py (probe/rev-3047-30905b88), extended to multi-site mutants: (name, [(file, old, new), ...]).
import subprocess, sys, pathlib, os
WT = pathlib.Path("/home/user/rev"); PKG = WT / "custom_components/heatpump_optimizer"
SEC = pathlib.Path("/root/rev/fr_section.py")
def run_sec():
    p = subprocess.run([sys.executable, str(SEC)], cwd=WT, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub:tests:custom_components"}, timeout=600)
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    tail = [l for l in out.splitlines() if "FR CHECKS" in l or "Error" in l][-2:]
    return p.returncode, fails, tail
def mutate(name, sites):
    saved = {}
    try:
        for fname, old, new in sites:
            f = PKG / fname; src = saved.get(f) or f.read_text(); saved.setdefault(f, src)
            cur = f.read_text(); n = cur.count(old)
            if n != 1:
                print(f"MUTANT {name}: SKIP old text found {n}x in {fname}: {old[:60]!r}"); return
            f.write_text(cur.replace(old, new))
        rc, fails, tail = run_sec()
    finally:
        for f, src in saved.items(): f.write_text(src)
    print(f"MUTANT {name}: {'KILLED' if rc != 0 else 'SURVIVED'} rc={rc} fails={len(fails)} {tail}")
    for l in fails[:3]: print("    ", l[:220])
    sys.stdout.flush()
muts = []
for a in sys.argv[1:]: exec(open(a).read())
for m in muts: mutate(*m)
