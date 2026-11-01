import subprocess, sys, pathlib, re, os
WT = pathlib.Path(os.environ["HOME"]) / "wt"
PKG = WT / "custom_components/heatpump_optimizer"
SEC = pathlib.Path(os.environ["HOME"]) / "rev/fr_section.py"
def run_sec():
    p = subprocess.run([sys.executable, str(SEC)], cwd=WT, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub:tests:custom_components"}, timeout=600)
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    tail = [l for l in out.splitlines() if "FR CHECKS" in l or "Error" in l][-2:]
    return p.returncode, fails, tail
def mutate(name, fname, old, new, count=1):
    f = PKG / fname; src = f.read_text()
    n = src.count(old)
    if n != count:
        print(f"MUTANT {name}: SKIP old text found {n}x (want {count})"); return
    f.write_text(src.replace(old, new))
    try:
        rc, fails, tail = run_sec()
    finally:
        f.write_text(src)
    verdict = "KILLED" if rc != 0 else "SURVIVED"
    print(f"MUTANT {name}: {verdict} rc={rc} fails={len(fails)} {tail}")
    for l in fails[:4]: print("    ", l[:200])
muts = []
exec(open(sys.argv[1]).read())
for m in muts: mutate(*m)
