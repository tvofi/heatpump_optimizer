import os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__)); from muts import M
wt, out = sys.argv[1], sys.argv[2]
src = open(f"{wt}/tools/audit/seat/review_strength.py").read()
args = open(f"{os.path.dirname(__file__)}/bundle_args").read().split()
base = open(f"{os.path.dirname(__file__)}/bundle_head.txt").read()
res = []
for k, (old, new) in M.items():
    n = src.count(old)
    if n != 1:
        res.append(f"{k} SKIPPED (old string occurs {n} times)"); continue
    r = tempfile.mkdtemp()
    os.makedirs(f"{r}/tools/audit/seat"); os.makedirs(f"{r}/tests"); os.makedirs(f"{r}/dev/audit/rounds/round10/D13")
    shutil.copy(f"{wt}/tests/throwaway_git.py", f"{r}/tests/")
    shutil.copy(f"{wt}/dev/audit/rounds/round10/D13/yield-probe.md", f"{r}/dev/audit/rounds/round10/D13/")
    open(f"{r}/tools/audit/seat/review_strength.py", "w").write(src.replace(old, new))
    p = subprocess.run([sys.executable, "-I", f"{r}/tools/audit/seat/review_strength.py", "--self-test"], capture_output=True, text=True, timeout=300)
    last = (p.stdout.strip().splitlines() or [""])[-1]
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    if p.returncode == 0:
        b = subprocess.run([sys.executable, f"{r}/tools/audit/seat/review_strength.py", "--repo", wt, *args], capture_output=True, text=True)
        open(f"{out}/hand_bundle_{k}.txt", "w").write(b.stdout + b.stderr)
        d = subprocess.run(["diff", f"{out}/bundle_head.txt", f"{out}/hand_bundle_{k}.txt"], capture_output=True, text=True).stdout
        open(f"{out}/hand_bundle_diff_{k}.txt", "w").write(d)
        res.append(f"{k} SURVIVED ({last}); bundle diff lines: {len(d.splitlines())}")
    else:
        res.append(f"{k} KILLED rc={p.returncode} {fails[0] if fails else last[:160]}")
    shutil.rmtree(r)
assert open(f"{wt}/tools/audit/seat/review_strength.py").read() == src
print("\n".join(res)); print("source restored identical")
