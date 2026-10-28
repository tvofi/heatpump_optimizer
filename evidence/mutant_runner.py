import sys, subprocess, pathlib, filecmp, shutil
root = pathlib.Path(sys.argv[1]); f = root/"tools/audit/seat/review_strength.py"
orig = f.read_text(); bak = f.with_suffix(".bak"); shutil.copy(f, bak)
exec(open(sys.argv[2]).read()); muts = M
for name, a, b in muts:
    n = orig.count(a)
    if n != 1:
        print(f"{name}: SKIP occurrences={n}"); continue
    f.write_text(orig.replace(a, b))
    p = subprocess.run([sys.executable, "-I", str(f), "--self-test"], capture_output=True, text=True, timeout=600)
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    last = (p.stdout.strip().splitlines() or [p.stderr.strip()[-200:]])[-1]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} | {last[:120]}")
    for l in fails[:4]: print("    ", l[:150])
f.write_text(orig); print("restored identical:", filecmp.cmp(f, bak, shallow=False)); bak.unlink()
