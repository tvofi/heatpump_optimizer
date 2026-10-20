#!/usr/bin/env python3
"""Reviewer's own mutants beyond the fixer's M1-M7 (disclosed as the reviewer's instrument).
Each: detached worktree of HEAD, one exact-once substitution, full entities run."""
import subprocess, sys, tempfile, shutil, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2])
LOOP_A='    for _f in "$OUT/scripts.tsv" "$OUT/per/provenance.tsv"; do\n'
X={
 # R(b) ledger, half-filter: only scripts.tsv is filtered, provenance.tsv keeps the stale reused row
 "X1":[("tools/coverage/coverage_tree.sh",LOOP_A,'    for _f in "$OUT/scripts.tsv"; do\n')],
 # the other half: only provenance.tsv filtered
 "X2":[("tools/coverage/coverage_tree.sh",LOOP_A,'    for _f in "$OUT/per/provenance.tsv"; do\n')],
 # R(b): the reused list comes out empty, so the reused script is never re-measured
 "X3":[("tools/coverage/coverage_tree.sh","_reused=$(awk -F'\\t' '$2==\"reused\" {print $1}'","_reused=$(awk -F'\\t' '$2==\"reusedX\" {print $1}'")],
 # R(a): arch_score.py (not _head) back into lane_units
 "X4":[("tests/run.sh",'  run "$PYTHON" tests/structure.py\n','  run "$PYTHON" tests/structure.py\n  run "$PYTHON" tests/arch_score.py\n')],
 # R(c): reused exclusion spelled on the wrong field (lane instead of class)
 "X5":[("tests/ci_ratchet.py",' and r["class"] != "reused")',' and r["lane"] != "reused")')],
}
def one(name):
    wt=Path(tempfile.mkdtemp())/name
    subprocess.run(["git","-C",str(ROOT),"worktree","add","-q","--detach",str(wt),"HEAD"],check=True)
    try:
        for f,a,b in X[name]:
            p=wt/f; t=p.read_text(); n=t.count(a)
            if n!=1: return f"{name} NOT-APPLIED count={n} in {f}"
            p.write_text(t.replace(a,b))
        r=subprocess.run([sys.executable,"tests/entities.py"],cwd=wt,env={**os.environ,"PYTHONPATH":"tests/hastub"},capture_output=True,text=True)
        fails=[l.strip() for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        summ=[l for l in r.stdout.splitlines() if "ENTITY CHECKS" in l]
        return f"{name} rc={r.returncode} | {summ[-1] if summ else '?'} | FAIL lines: {[f[:140] for f in fails]}"
    finally:
        subprocess.run(["git","-C",str(ROOT),"worktree","remove","--force",str(wt)])
names=sys.argv[3:] or list(X)
with ThreadPoolExecutor(int(os.environ.get("J","3"))) as ex:
    for line in ex.map(one,names):
        print(line,flush=True); OUT.open("a").write(line+"\n")
