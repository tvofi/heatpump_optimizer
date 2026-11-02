import sys, shutil, subprocess, tempfile
from pathlib import Path
src = Path(sys.argv[1])
P = {"M0": None,
 "M-open-stem": ('        rc = d / f"{stem(topic)}.rc"\n', '        rc = d / f"{topic}.rc"\n'),
 "M-reap-stem": ('        rcf = d / f"{stem(t)}.rc"\n', '        rcf = d / f"{t}.rc"\n'),
 "M-reap-log": ("reason(d / (stem(t) + '.log'))", "reason(d / (t + '.log'))")}
for n, pl in P.items():
    with tempfile.TemporaryDirectory() as x:
        x = Path(x); shutil.copytree(src/"tools/audit/seat", x/"tools/audit/seat"); (x/"tests").mkdir(); shutil.copy(src/"tests/throwaway_git.py", x/"tests")
        p = x/"tools/audit/seat/open_driver.py"; s = p.read_text()
        if pl: assert s.count(pl[0]) == 1; p.write_text(s.replace(*pl))
        r = subprocess.run([sys.executable, "-I", str(p), "--self-test"], capture_output=True, text=True)
        o = r.stdout + r.stderr
        print(f"RESULT prev-head mutant={n} rc={r.returncode} {[l for l in o.splitlines() if 'self-test:' in l]} {[l for l in o.splitlines() if l.startswith('FAIL ')]}")
