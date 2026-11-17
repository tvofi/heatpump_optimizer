import subprocess, sys, pathlib
WT = pathlib.Path(sys.argv[1])
M = [
 ("M9", "tools/audit/seat/carry_fold.py", "leased(a.state_dir, LEASE_WAIT_S, lambda: fold(", "(lambda: fold("),
 ("M10", "tools/audit/seat/record_beat.py", '"body": d.get("body") or ""', None),
 ("M11", "tools/audit/seat/record_beat.py", ",body", ""),
 ("M16-empty-queue", "tools/audit/seat/postmerge.py", "            if not queued:\n                continue", "            if False:\n                continue"),
]
for name, f, old, new in M:
    p = WT / f; src = p.read_text()
    n = src.count(old)
    if new is None:
        # drop the dict entry and its separator
        line = [l for l in src.splitlines(True) if old in l]
        print(name, "anchor lines:", [l.strip() for l in line])
        mutated = src.replace('"body": d.get("body") or ""', '"_nobody": 0', 1)
    else:
        mutated = src.replace(old, new, 1)
    if n == 0 or mutated == src:
        print(f"{name}: ANCHOR-MISSING ({n})"); continue
    p.write_text(mutated)
    try:
        r = subprocess.run([sys.executable, "-I", f, "--self-test"], cwd=WT, capture_output=True, text=True, timeout=200)
        out = (r.stdout + r.stderr).splitlines()
        fails = [l for l in out if "FAIL" in l]
        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} anchors={n} :: {out[-1] if out else ''}")
        for l in fails[:4]: print("   ", l.strip()[:200])
    finally:
        p.write_text(src)
