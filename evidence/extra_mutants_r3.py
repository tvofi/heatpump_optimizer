"""Reviewer's own round-3 mutants on the harness_headers run-alone pin (not the fixer's harness).
Each mutant: detached worktree of HEAD, exact-once substitution in tests/run.sh, full entities.py,
report whether the aimed check FAILs."""
import subprocess, sys, tempfile, os, re
from pathlib import Path
HEAD = sys.argv[1]
ROOT = Path(subprocess.check_output(["git","rev-parse","--show-toplevel"],text=True).strip())
AIM = "the CPU-bounded harness check runs alone"
HH = '  run_always "$PYTHON" tests/harness_headers.py\n}\n\nLANES='
M = {
 # harness_headers into lane_golden (end) and out of lane_stress
 "X6_into_golden": [(HH, '}\n\nLANES='),
                    ('  run "$PYTHON" tests/arch_score_head.py\n', '  run "$PYTHON" tests/arch_score_head.py\n  run_always "$PYTHON" tests/harness_headers.py\n')],
 # before stress.py inside lane_stress
 "X7_before_stress": [(HH, '}\n\nLANES='),
                      ('lane_stress() {\n  run "$PYTHON" tests/stress.py\n', 'lane_stress() {\n  run_always "$PYTHON" tests/harness_headers.py\n  run "$PYTHON" tests/stress.py\n')],
 # stress lane added to the parallel set
 "X8_stress_in_LANES": [('LANES="units golden e2e"\n', 'LANES="units golden e2e stress"\n')],
 # parallel loop iterates stress too, LANES string untouched
 "X9_parallel_loop": [('  pids=""\n  for lane in $LANES; do\n', '  pids=""\n  for lane in $LANES stress; do\n')],
 # alone phase backgrounded without wait, i.e. overlapping nothing changes? run lane_stress before waiting for the lanes
 "X10_no_wait": [('  for pid in $pids; do wait "$pid"; done\n  echo\n  echo "########## alone', '  echo\n  echo "########## alone'),
                 ('  wait $!\nfi\n', '  wait $!\n  for pid in $pids; do wait "$pid"; done\nfi\n')],
}
only = sys.argv[2:] or list(M)
for name in only:
    with tempfile.TemporaryDirectory() as td:
        wt = Path(td)/"wt"
        subprocess.run(["git","-C",str(ROOT),"worktree","add","-q","--detach",str(wt),HEAD],check=True)
        try:
            p = wt/"tests/run.sh"; s = p.read_text()
            for a,b in M[name]:
                n = s.count(a)
                if n != 1: print(f"{name} SUBST-COUNT {n} for {a[:50]!r}"); raise SystemExit(2)
                s = s.replace(a,b)
            p.write_text(s)
            env = dict(os.environ, PYTHONPATH="tests/hastub")
            r = subprocess.run([sys.executable,"tests/entities.py"],cwd=wt,env=env,capture_output=True,text=True)
            out = r.stdout + r.stderr
            fails = [l for l in out.splitlines() if l.lstrip().startswith("FAIL ")]
            summ = [l for l in out.splitlines() if "ENTITY CHECKS" in l]
            aimed = [l for l in fails if AIM in l]
            print(f"{name} {'KILLED' if aimed and r.returncode else 'SURVIVED'} rc={r.returncode} | {summ[-1] if summ else '?'} | aimed={len(aimed)} | counted_other={[l.strip()[:90] for l in fails if AIM not in l and "graders-head-copy" in l]}", flush=True)
        finally:
            subprocess.run(["git","-C",str(ROOT),"worktree","remove","--force",str(wt)])
