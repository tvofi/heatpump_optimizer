# drive the real audit_dispatch once per hourly cut over cached review_strength --guardrail outputs (ev/sweep_cache.sh)
# argv: <dir holding beat_jobs.py> <repo> <cache dir> <label>; counts DISPATCH lines per arm
import sys, tempfile, collections
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import beat_jobs as bj
cache = Path(sys.argv[3]); label = sys.argv[4]
s = Path(tempfile.mkdtemp()); cur = [None]
def run(argv, cwd, env):
    t = cur[0]
    return (int((cache / f"{t}.rc").read_text()), (cache / f"{t}.out").read_text(), "")
seen, per_arm, trips = set(), collections.Counter(), collections.Counter()
for t in sorted(int(p.stem) for p in cache.glob("*.out")):
    cur[0] = t
    c = bj.Ctx(s, Path(sys.argv[2]), run=run, now=float(t))  # a fresh Ctx per pass: a process restart each cut
    bj.audit_dispatch(c)
    for ln in (cache / f"{t}.out").read_text().splitlines():
        if "-> would-trip" in ln: trips[ln.split()[1]] += 1
    job = bj.read(c.digest / "jobs" / "audit-dispatch").splitlines()
    for ln in job:
        if ln.startswith("DISPATCH:") and ln not in seen:
            seen.add(ln); per_arm[ln.split()[2]] += 1
            print(f"{label} {t} NEW {ln}")
n = len(list(cache.glob("*.out")))
for arm, k in sorted(trips.items()):
    print(f"RESULT {label} {arm} would-trip at {k}/{n} hourly cuts; DISPATCH lines {per_arm.get('arm='+arm, 0)}")
print(f"RESULT {label} total distinct DISPATCH lines: {len(seen)} over {n} cuts")
