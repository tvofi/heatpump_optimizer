# Same mutants as list4, through the whole tests/features.py (the body's claim for the humidity and probe mutants).
import subprocess, sys, pathlib, os, time
WT = pathlib.Path(sys.argv[2]); PKG = WT / "custom_components/heatpump_optimizer"
muts = []
exec(open("/tmp/claude-0/w/list45.py").read())
want = sys.argv[1].split(",")
sel = [m for m in muts if m[0] in want]
pass
for name, sites in sel:
    saved = {}
    try:
        for fname, old, new in sites:
            f = PKG / fname; cur = f.read_text(); saved.setdefault(f, cur)
            assert cur.count(old) == 1, name
            f.write_text(cur.replace(old, new))
        t = time.time()
        p = subprocess.run([sys.executable, "tests/features.py"], cwd=WT, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=3000)
    finally:
        for f, src in saved.items(): f.write_text(src)
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    tail = [l for l in out.splitlines() if "FEATURE CHECKS" in l][-1:]
    print(f"FULL {name}: {'KILLED' if p.returncode else 'SURVIVED'} rc={p.returncode} {tail} {time.time()-t:.0f}s")
    for l in fails[:4]: print("    ", l[:240])
    sys.stdout.flush()
