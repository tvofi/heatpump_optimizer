import sys, subprocess, pathlib
W = pathlib.Path(sys.argv[1]); f = W/"mt/tools/audit/seat/review_strength.py"
exec(open(W/sys.argv[2]).read())
orig = f.read_text(); args = open(W/"bundle_args").read().split()
R = "/home/user/heatpump_optimizer"; out = []
for name, a, b in M:
    n = orig.count(a)
    if n != 1: print(f"{name}: SKIP occurrences={n}", flush=True); continue
    f.write_text(orig.replace(a, b))
    p = subprocess.run([sys.executable, "-I", str(f), "--self-test"], capture_output=True, text=True, timeout=900)
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    last = (p.stdout.strip().splitlines() or [p.stderr.strip()[-200:]])[-1]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} | {last[:110]}", flush=True)
    for l in fails[:3]: print("    ", l[:160])
    if p.returncode == 0:
        key = name.split()[0]
        b1 = subprocess.run([sys.executable, "-I", str(f), "--repo", R, *args], capture_output=True, text=True).stdout
        (W/f"ev/bundle_{key}.txt").write_text(b1)
        d = subprocess.run(["diff", str(W/"ev/bundle_head.txt"), str(W/f"ev/bundle_{key}.txt")], capture_output=True, text=True).stdout
        x = subprocess.run([sys.executable, "-I", str(f), "--repo", R, "--window", "A=2026-10-15T12:37Z..2026-10-21T11:00Z", "--window", "L35=2026-10-19T11:00Z..2026-10-21T11:00Z", "--window", "L13=2026-10-21T13:00Z..2026-10-21T14:50Z"], capture_output=True, text=True).stdout
        d2 = subprocess.run(["diff", str(W/"ev/figures_extra.txt"), "-"], input=x, capture_output=True, text=True).stdout
        (W/f"ev/bundle_diff_{key}.txt").write_text(d + d2)
        print(f"    bundle diff lines: {sum(1 for l in (d+d2).splitlines() if l[:1] in '<>')}", flush=True)
f.write_text(orig); print("restored identical:", f.read_text() == orig)
