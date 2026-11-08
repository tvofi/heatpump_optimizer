"""Finder harness for the roster drain stale lint clone (R10-HOTFIX-ROSTER-LINT-REFRESH).
Usage: python3 -I dev/audit/harnesses/roster_queue_stale_lint.py [roster_queue.py]   (default tools/audit/seat/roster_queue.py)
Pass the pre-fix copy (git show origin/main~:tools/audit/seat/roster_queue.py) to see it FAIL.
Drive roster_queue._run_op (file given as argv[1]) against real git: origin, edit checkout EC, lint clone LC
(alternates to EC's store). Stub editor refuses as roster_edit.lint_gate does when LC HEAD != EC origin/main,
and leaves a local commit in the worktree when it refuses. Three scenarios, each one RESULT line:
  stale    LC's origin URL broken after cloning (a fetch that fails): op1 and op2 must both push.
  cascade  LC healthy; the stub refuses op1 once for an unrelated reason: op2 must still push, which needs
           the refused op's worktree removed (the "is on no origin ref" cascade).
  follow   another clone pushes main; refresh_lint alone must detach a clone with its OWN store (no
           alternates) at origin's new main, which needs both the edit checkout's fetch and the clone's."""
import argparse, importlib.util, os, subprocess, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tests"))
from throwaway_git import throwaway_git_init, throwaway_git_clone, throwaway_git_env
os.environ.clear(); os.environ.update(throwaway_git_env())  # every git call here, the stub's included, is hermetic
def g(*a, cwd=None): return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
RQ = sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/roster_queue.py"
spec = importlib.util.spec_from_file_location("rq", RQ); rq = importlib.util.module_from_spec(spec); spec.loader.exec_module(rq)
STUB = """import subprocess,sys,os
def g(*a,cwd): return subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True).stdout.strip()
ec,lc,wt,once={ec!r},{lc!r},{wt!r},{once!r}
g('fetch','-q','origin','main',cwd=ec)
if os.path.isdir(wt):
    h=g('rev-parse','HEAD',cwd=wt)
    if not g('branch','-r','--contains',h,cwd=ec): print('REFUSED: '+wt+' HEAD '+h[:12]+' is on no origin ref'); sys.exit(2)
else: g('worktree','add','-q','--detach',wt,'origin/main',cwd=ec)
g('commit','-q','--allow-empty','-m','edit',cwd=wt)
if once and not os.path.exists(once): open(once,'w').close(); print('REFUSED: unrelated'); sys.exit(4)
head,main=g('rev-parse','HEAD',cwd=lc),g('rev-parse','origin/main',cwd=ec)
if head!=main: print('LINT GATE REFUSED the push | --lint-cwd is at '+head[:12]+', not origin/main ('+main[:12]+'): the stale-worktree trap'); sys.exit(3)
g('push','-q','origin','HEAD:refs/heads/handoff/x','-f',cwd=wt); g('fetch','-q','origin',cwd=ec); print('pushed handoff/x at '+main)
"""
def push_main(repo, msg): g("-C", str(repo), "commit", "-q", "--allow-empty", "-m", msg); g("-C", str(repo), "push", "-q", "origin", "HEAD:main")
def setup():
    t = pathlib.Path(tempfile.mkdtemp()); O, EC, LC = t / "o.git", t / "ec", t / "lc"
    throwaway_git_init(O, "-q", "--bare", "-b", "main"); throwaway_git_clone(O, EC, "-q"); push_main(EC, "one")
    throwaway_git_clone(O, LC, "-q", "--reference", str(EC)); g("-C", str(LC), "checkout", "-q", "--detach", "origin/main")
    push_main(EC, "two"); return t, O, EC, LC
def drain(t, EC, LC, once):
    WT = t / "wt"; stub = t / "stub.py"; stub.write_text(STUB.format(ec=str(EC), lc=str(LC), wt=str(WT), once=once))
    rep = []; a = argparse.Namespace(edit_checkout=str(EC), worktree=str(WT), lint_clone=str(LC), branch=None)
    sh = lambda *c, **k: subprocess.run(c, capture_output=True, text=True, cwd=str(EC))  # the drain runs with cwd=EC
    for op in ("op1", "op2"):
        rq._run_op(a, sh, rep.append, sys.executable, str(stub), "set-stage", "G", "", [])
        if op == "op1": push_main(EC, "three")  # a healthy tree moves on between ops: null control for the lint refresh
    return rep
def stale():
    t, O, EC, LC = setup(); g("-C", str(LC), "remote", "set-url", "origin", str(t / "gone.git"))  # LC's fetch now fails
    rep = drain(t, EC, LC, ""); return rep, len(rep) == 2 and all(" pushed " in r for r in rep)
def cascade():
    t, O, EC, LC = setup(); rep = drain(t, EC, LC, str(t / "once"))
    return rep, len(rep) == 2 and " refused rc=4 " in rep[0] and " pushed " in rep[1]
def follow():
    t, O, EC, LC = setup(); OWN, X = t / "own", t / "x"
    throwaway_git_clone(O, OWN, "-q"); g("-C", str(OWN), "checkout", "-q", "--detach", "origin/main")
    throwaway_git_clone(O, X, "-q"); push_main(X, "other seat")  # EC sees this only by fetching; OWN lacks the object
    if not hasattr(rq, "refresh_lint"): return ["no refresh_lint"], False
    err = rq.refresh_lint(argparse.Namespace(edit_checkout=str(EC), lint_clone=str(OWN)))
    got, want = g("-C", str(OWN), "rev-parse", "HEAD"), g("-C", str(O), "rev-parse", "main")
    return [f"refresh_lint={err!r} head={got[:12]} origin main={want[:12]}"], err == "" and got == want
ok = True
for name, fn in (("stale", stale), ("cascade", cascade), ("follow", follow)):
    rep, good = fn(); ok &= good
    print("\n".join(f"{name}: {r}" for r in rep)); print(f"{name}: RESULT:", "PASS" if good else "FAIL")
print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
