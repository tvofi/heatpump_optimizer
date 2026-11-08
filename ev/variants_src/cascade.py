"""Finder harness for the roster drain stale lint clone (R10-HOTFIX-ROSTER-LINT-REFRESH).
Usage: python3 -I dev/audit/harnesses/roster_queue_stale_lint.py [roster_queue.py]   (default tools/audit/seat/roster_queue.py)
Pass the pre-fix copy (git show origin/main~:tools/audit/seat/roster_queue.py) to see it FAIL.
Drive roster_queue._run_op (file given as argv[1]) against real git: origin, edit checkout EC, lint clone LC
(alternates to EC's store, origin URL broken after cloning = a fetch that fails). Stub editor refuses as
roster_edit.lint_gate does when LC HEAD != EC origin/main, and leaves a local commit in the worktree when it refuses."""
import argparse, importlib.util, os, subprocess, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tests"))
from throwaway_git import throwaway_git_init, throwaway_git_clone, throwaway_git_environ
from throwaway_git import throwaway_git_env
os.environ.clear(); os.environ.update(throwaway_git_env())  # every git call here, the stub's included, is hermetic
def g(*a, cwd=None): return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
RQ = sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/roster_queue.py"
spec = importlib.util.spec_from_file_location("rq", RQ); rq = importlib.util.module_from_spec(spec); spec.loader.exec_module(rq)
t = pathlib.Path(tempfile.mkdtemp()); O, EC, LC, WT = (t / n for n in ("o.git", "ec", "lc", "wt"))
throwaway_git_init(O, "-q", "--bare", "-b", "main"); throwaway_git_clone(O, EC, "-q")
g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "one"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
throwaway_git_clone(O, LC, "-q", "--reference", str(EC)); g("-C", str(LC), "checkout", "-q", "--detach", "origin/main")
g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "two"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
g("-C", str(LC), "fetch", "-q", "origin"); g("-C", str(LC), "checkout", "-q", "--detach", "origin/main")   # LC's fetch now fails; EC's works
stub = t / "stub.py"
stub.write_text(f"""import subprocess,sys
def g(*a,cwd): return subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True).stdout.strip()
ec,lc,wt={str(EC)!r},{str(LC)!r},{str(WT)!r}
g('fetch','-q','origin','main',cwd=ec)
import os
if os.path.isdir(wt):
    h=g('rev-parse','HEAD',cwd=wt)
    if not g('branch','-r','--contains',h,cwd=ec): print('REFUSED: '+wt+' HEAD '+h[:12]+' is on no origin ref'); sys.exit(2)
else: g('worktree','add','-q','--detach',wt,'origin/main',cwd=ec)
g('commit','-q','--allow-empty','-m','edit',cwd=wt)
head,main=g('rev-parse','HEAD',cwd=lc),g('rev-parse','origin/main',cwd=ec)
if not os.path.exists(wt+'.once'):
    open(wt+'.once','w').close(); print('REFUSED: unrelated'); sys.exit(4)
if head!=main: print('LINT GATE REFUSED the push | --lint-cwd is at '+head[:12]+', not origin/main ('+main[:12]+'): the stale-worktree trap'); sys.exit(3)
g('push','-q','origin','HEAD:refs/heads/handoff/x','-f',cwd=wt); g('fetch','-q','origin',cwd=ec); print('pushed handoff/x at '+main); """)
rep = []
a = argparse.Namespace(edit_checkout=str(EC), worktree=str(WT), lint_clone=str(LC), branch=None)
sh = lambda *c, **k: subprocess.run(c, capture_output=True, text=True, cwd=str(EC))  # the drain runs with cwd=EC
for op in ("op1", "op2"):
    rq._run_op(a, sh, rep.append, sys.executable, str(stub), "set-stage", "G", "", [])
    if op == "op1":  # a healthy tree moves on between ops: null control for the lint refresh
        g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "three"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
print("\n".join(rep)); ok = len(rep) == 2 and " refused " in rep[0] and " pushed " in rep[1]
print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
