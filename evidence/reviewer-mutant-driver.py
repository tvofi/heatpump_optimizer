import sys, subprocess, pathlib, shutil
src = pathlib.Path("tools/audit/seat/corpus_mirror.py")
orig = src.read_text()
muts = [
 #("unlink all", "            if stale.stem not in batches:\n", "            if True:\n"),
 #("unlink none glob", '(self.dir / "graphql" / "items").glob("*.json")', '(self.dir / "graphql" / "items").glob("*.none")'),
 ("max default 0", 'max(seen.get("max", cost), cost)', 'max(seen.get("max", 0), cost)'),
 ("max keeps first", 'max(seen.get("max", cost), cost)', 'seen.get("max", cost)'),
 ("secondary cap strict", "int(after) <= SECONDARY_WAIT_CAP_S", "int(after) < SECONDARY_WAIT_CAP_S"),
 #("secondary no digit check", "and after.isdigit() and int(after)", "and int(after or 0)"),
]
try:
  for name, a, b in muts:
    n = orig.count(a)
    src.write_text(orig.replace(a, b, 1))
    print(f"{name}: first of {n} occurrence(s), production line {orig[:orig.index(a)].count(chr(10))+1}")
    p = subprocess.run([sys.executable, "-I", str(src), "--self-test", "--no-mutants"], capture_output=True, text=True, timeout=200)
    fails = [l for l in p.stdout.splitlines()+p.stderr.splitlines() if l.startswith("FAIL")]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode or fails else 'SURVIVED'} fails={len(fails)}")
    for l in fails[:3]: print("   ", l[:200])
finally:
  src.write_text(orig)
