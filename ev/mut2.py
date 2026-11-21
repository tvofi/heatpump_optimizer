import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
M = [
 ("F1_absorbed_false", "tools/ci/selftest_scope.py", "absorbed = bool(added) and not remain", "absorbed = False"),
 ("F2_absorbed_added_only", "tools/ci/selftest_scope.py", "absorbed = bool(added) and not remain", "absorbed = bool(added)"),
]
for name, path, old, new in M:
    p = root / path; src = p.read_text()
    assert src.count(old) == 1
    p.write_text(src.replace(old, new, 1))
    try:
        r = subprocess.run(["python3","-I","tools/ci/selftest_scope.py","--self-test"], cwd=root, capture_output=True, text=True, timeout=900)
        fails = [l for l in r.stdout.splitlines() if "FAIL" in l][:3]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} :: {r.stdout.strip().splitlines()[-1]} :: {fails}")
    finally:
        p.write_text(src)
