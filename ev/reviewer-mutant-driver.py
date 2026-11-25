import subprocess, sys, pathlib, shutil
wt = pathlib.Path(sys.argv[1]); f = wt / "tools/audit/seat/corpus_mirror.py"
orig = f.read_text()
M = {
 "keep predicate inverted": ("            if stale.stem not in batches:\n", "            if stale.stem in batches:\n"),
 "max ignores new cost": ('max(seen["max"], cost) if "max" in seen else cost', 'seen["max"] if "max" in seen else cost'),
 "keep predicate True (prior round)": ("            if stale.stem not in batches:\n", "            if True:\n"),
}
try:
    for name, (a, b) in M.items():
        assert orig.count(a) >= 1, name
        f.write_text(orig.replace(a, b, 1))
        p = subprocess.run([sys.executable, "-I", str(f), "--self-test", "--no-mutants"], capture_output=True, text=True, cwd=wt)
        fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
        print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} fails={fails[:3]}")
finally:
    f.write_text(orig)
