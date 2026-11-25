import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); f, old, new, tag = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
p = W/"custom_components/heatpump_optimizer"/f; src = p.read_text()
assert src.count(old) == 1, src.count(old)
p.write_text(src.replace(old, new))
try:
    r = subprocess.run([sys.executable, "tests/features.py"], cwd=W, capture_output=True, text=True, timeout=3000,
                       env={**__import__("os").environ, "PYTHONPATH": "tests/hastub:custom_components:tests"})
    out = r.stdout + r.stderr
    (pathlib.Path("/root/scr")/f"full_{tag}.log").write_text(out[-20000:])
    fails = [l.strip()[:200] for l in out.splitlines() if l.lstrip().startswith("FAIL")]
    print(f"{tag}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} fails={len(fails)} | {out.strip().splitlines()[-1][:160]}")
    for l in fails[:6]: print("   ", l)
finally:
    p.write_text(src)
