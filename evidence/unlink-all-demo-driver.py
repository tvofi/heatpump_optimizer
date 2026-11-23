import sys, subprocess, pathlib
src = pathlib.Path("tools/audit/seat/corpus_mirror.py")
orig = src.read_text()
probe_a = '            and rc2 == 0 and mph2.cur["state"] == "complete" and set(mph2.cur["items"]["item batches"].values()) == {"ok"}\n'
probe_b = probe_a.rstrip("\n") + ' \\\n            and len(list((Path(td) / "ghour" / "corpus" / "graphql" / "items").glob("*.json"))) == len(mph2.cur["items"]["item batches"])\n'
mut_a, mut_b = "            if stale.stem not in batches:\n", "            if True:\n"
assert orig.count(probe_a) == 1 and orig.count(mut_a) == 1
try:
  for label, text in (("reviewer probe, production as at head", orig.replace(probe_a, probe_b)),
                      ("reviewer probe, mutant 'unlink all'", orig.replace(probe_a, probe_b).replace(mut_a, mut_b))):
    src.write_text(text)
    p = subprocess.run([sys.executable, "-I", str(src), "--self-test", "--no-mutants"], capture_output=True, text=True, timeout=200)
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    print(f"{label}: rc={p.returncode} fails={len(fails)}")
    for l in fails: print("   ", l[:220])
finally:
  src.write_text(orig)
