# Review packet #3337
head: d0db3e30b84652af833d13f7f708a45704fdd6c8
base: 8a4974d1522f979f5b1c837df8e3a76b535bf35e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128788183477 success
arch-score / arch-score id=128788143016 success
arm id=128787999909 skipped
budget-raise-gate / budget-raise-gate id=128788143062 success
cancel-superseded id=128788003745 success
codeql id=128788142683 skipped
codeql / Analyze (actions) id=128788143174 success
codeql / Analyze (javascript-typescript) id=128788143045 success
codeql / Analyze (python) id=128788143178 success
gate id=128788451757 failure
governance id=128788142432 skipped
governance / delivery-status id=128788143195 success
governance / delivery-status-publish id=128788145194 skipped
governance / env-matrix id=128788143134 in_progress
governance / instrument-self-tests id=128788143112 in_progress
governance / policy-docs id=128788143172 success
governance / record id=128788144720 skipped
governance / wave-script id=128788143150 success
hassfest id=128788142828 skipped
hassfest / hassfest id=128788142911 success
kernel-points id=128788144339 skipped
pr-contract id=128788452557 skipped
prelude id=128788003801 success
refresh id=128788003502 success
tests id=128788142358 skipped
tests / arch-instrument id=128788262058 success
tests / briefs id=128788143235 success
tests / browser id=128788262113 success
tests / closure-scope id=128788143054 success
tests / closures id=128788262150 in_progress
tests / coverage id=128788262007 in_progress
tests / fast (3.14) id=128788262286 in_progress
tests / mutation id=128788143092 success
tests / mutation-autofix id=128788307340 skipped
tests / mutation-pins id=128788306577 skipped
tests / nightly-ha id=128788263083 skipped
tests / nightly-status id=128788143157 success
tests / replay id=128788264165 skipped
tests / typing id=128788262035 success
validate id=128788142446 skipped
validate / validate-hacs id=128788143060 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at d0db3e30b84652af833d13f7f708a45704fdd6c8

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/roster_queue_stale_lint.py b/dev/audit/harnesses/roster_queue_stale_lint.py
new file mode 100644
index 000000000..6fe600a83
--- /dev/null
+++ b/dev/audit/harnesses/roster_queue_stale_lint.py
@@ -0,0 +1,43 @@
+"""Finder harness for the roster drain stale lint clone (R10-HOTFIX-ROSTER-LINT-REFRESH).
+Usage: python3 -I dev/audit/harnesses/roster_queue_stale_lint.py [roster_queue.py]   (default tools/audit/seat/roster_queue.py)
+Pass the pre-fix copy (git show origin/main~:tools/audit/seat/roster_queue.py) to see it FAIL.
+Drive roster_queue._run_op (file given as argv[1]) against real git: origin, edit checkout EC, lint clone LC
+(alternates to EC's store, origin URL broken after cloning = a fetch that fails). Stub editor refuses as
+roster_edit.lint_gate does when LC HEAD != EC origin/main, and leaves a local commit in the worktree when it refuses."""
+import argparse, importlib.util, os, subprocess, sys, tempfile, pathlib
+sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tests"))
+from throwaway_git import throwaway_git_init, throwaway_git_clone, throwaway_git_environ
+from throwaway_git import throwaway_git_env
+os.environ.clear(); os.environ.update(throwaway_git_env())  # every git call here, the stub's included, is hermetic
+def g(*a, cwd=None): return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
+RQ = sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/roster_queue.py"
+spec = importlib.util.spec_from_file_location("rq", RQ); rq = importlib.util.module_from_spec(spec); spec.loader.exec_module(rq)
+t = pathlib.Path(tempfile.mkdtemp()); O, EC, LC, WT = (t / n for n in ("o.git", "ec", "lc", "wt"))
+throwaway_git_init(O, "-q", "--bare", "-b", "main"); throwaway_git_clone(O, EC, "-q")
+g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "one"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
+throwaway_git_clone(O, LC, "-q", "--reference", str(EC)); g("-C", str(LC), "checkout", "-q", "--detach", "origin/main")
+g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "two"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
+g("-C", str(LC), "remote", "set-url", "origin", str(t / "gone.git"))   # LC's fetch now fails; EC's works
+stub = t / "stub.py"
+stub.write_text(f"""import subprocess,sys
+def g(*a,cwd): return subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True).stdout.strip()
+ec,lc,wt={str(EC)!r},{str(LC)!r},{str(WT)!r}
+g('fetch','-q','origin','main',cwd=ec)
+import os
+if os.path.isdir(wt):
+    h=g('rev-parse','HEAD',cwd=wt)
+    if not g('branch','-r','--contains',h,cwd=ec): print('REFUSED: '+wt+' HEAD '+h[:12]+' is on no origin ref'); sys.exit(2)
+else: g('worktree','add','-q','--detach',wt,'origin/main',cwd=ec)
+g('commit','-q','--allow-empty','-m','edit',cwd=wt)
+head,main=g('rev-parse','HEAD',cwd=lc),g('rev-parse','origin/main',cwd=ec)
+if head!=main: print('LINT GATE REFUSED the push | --lint-cwd is at '+head[:12]+', not origin/main ('+main[:12]+'): the stale-worktree trap'); sys.exit(3)
+g('push','-q','origin','HEAD:refs/heads/handoff/x','-f',cwd=wt); g('fetch','-q','origin',cwd=ec); print('pushed handoff/x at '+main); """)
+rep = []
+a = argparse.Namespace(edit_checkout=str(EC), worktree=str(WT), lint_clone=str(LC), branch=None)
+sh = lambda *c, **k: subprocess.run(c, capture_output=True, text=True, cwd=str(EC))  # the drain runs with cwd=EC
+for op in ("op1", "op2"):
+    rq._run_op(a, sh, rep.append, sys.executable, str(stub), "set-stage", "G", "", [])
+    if op == "op1":  # a healthy tree moves on between ops: null control for the lint refresh
+        g("-C", str(EC), "commit", "-q", "--allow-empty", "-m", "three"); g("-C", str(EC), "push", "-q", "origin", "HEAD:main")
+print("\n".join(rep)); ok = len(rep) == 2 and all(" pushed " in r for r in rep)
+print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
diff --git a/dev/programme/delivery/3337.md b/dev/programme/delivery/3337.md
new file mode 100644
index 000000000..ad7c3b703
--- /dev/null
+++ b/dev/programme/delivery/3337.md
@@ -0,0 +1 @@
+- [#3337](https://github.com/tvofi/heatpump_optimizer/pull/3337) — **open**, R10-HOTFIX-ROSTER-LINT-REFRESH: roster lint refresh (R10-HOTFIX-ROSTER-LINT-REFRESH)
diff --git a/tests/closures.json b/tests/closures.json
index 8bf6a1317..e3c1cd595 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4193,6 +4193,7 @@
    "dev/audit/harnesses/record_api_calls.sh",
    "dev/audit/harnesses/record_batch_measure.py",
    "dev/audit/harnesses/record_burst_replay.py",
+   "dev/audit/harnesses/roster_queue_stale_lint.py",
    "dev/audit/harnesses/sav_reasons_booking.py",
    "dev/audit/harnesses/scale_writer_seams.py",
    "dev/audit/harnesses/silent_peer_waits.py",
diff --git a/tools/audit/seat/roster_queue.py b/tools/audit/seat/roster_queue.py
index 2dc796f52..9833d2603 100644
--- a/tools/audit/seat/roster_queue.py
+++ b/tools/audit/seat/roster_queue.py
@@ -317,6 +317,26 @@ def _run_batch(a, sh, rep, py, editor, lines, mark):
     return 0
 
 
+def refresh_lint(a):
+    """Detach --lint-clone at the SHA roster_edit's lint gate will compare it with: the edit checkout's
+    origin/main after a fetch. Returns "" or why not. The checks of the old pair (fetch, detach, both
+    unchecked) failed silently for four attempts in a row and the gate then refused as the stale-worktree trap."""
+    f = _git("fetch", "-q", "origin", "main", cwd=a.edit_checkout)
+    sha = _git("rev-parse", "origin/main", cwd=a.edit_checkout).stdout.strip()
+    if not sha:
+        return f"edit checkout has no origin/main ({f.stderr.strip()[-120:]})"
+    if not Path(a.lint_clone).is_dir():
+        return f"{a.lint_clone} is not a directory, wanted {sha[:12]}"
+    c = _git("checkout", "-q", "--detach", sha, cwd=a.lint_clone)
+    if c.returncode != 0:  # the object is not in the clone's store yet: fetch it, then retry once
+        _git("fetch", "-q", "origin", "main", cwd=a.lint_clone)
+        c = _git("checkout", "-q", "--detach", sha, cwd=a.lint_clone)
+    head = _git("rev-parse", "HEAD", cwd=a.lint_clone).stdout.strip()
+    if c.returncode != 0 or head != sha:
+        return f"{a.lint_clone} at {head[:12]}, wanted {sha[:12]}: {c.stderr.strip()[-120:]}"
+    return ""
+
+
 def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
     """One op: exactly one report line, or an exception for the caller to report."""
     cmd = [py, editor, op, g] + ([arg] if arg else []) + extra + [
@@ -325,8 +345,10 @@ def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
     if a.branch:
         cmd += ["--branch", a.branch]
     for attempt in (1, 2, 3, 4):
-        _git("fetch", "-q", "origin", cwd=a.lint_clone)
-        _git("checkout", "-q", "--detach", "origin/main", cwd=a.lint_clone)
+        err = refresh_lint(a)
+        if err:
+            rep(f"roster: {op} {g} refused rc=2 lint clone not refreshed: {err}"[:400])
+            return False
         r = sh(*cmd)
         out = r.stdout + r.stderr
         m = re.search(r"pushed handoff\S* at ([0-9a-f]+)", out)
@@ -349,6 +371,9 @@ def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
             sh("git", "worktree", "remove", "--force", a.worktree)
             continue
         rep(f"roster: {op} {g} refused rc={r.returncode} " + " | ".join(out.strip().split("\n")[-3:])[:400])
+        # A refusal leaves the edit as a local commit in the worktree; the next op would meet it as
+        # "HEAD is on no origin ref" and be refused for this op's fault (172 such lines in one drain log).
+        sh("git", "-C", a.edit_checkout, "worktree", "remove", "--force", a.worktree)
         return False
 
 
@@ -536,6 +561,16 @@ def _self_test():
             ck("readback: unknown group raises", True)
 
         # run_queue against a stub editor and a stub origin
+        _git("update-ref", "refs/remotes/origin/main", sha, cwd=repo, env=env)  # refresh_lint compares with it
+        _git("-c", "user.name=x", "-c", "user.email=x@x", "commit", "-q", "--allow-empty", "-m", "ahead",
+             cwd=repo, env=env)
+        ahead = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
+        _git("update-ref", "refs/remotes/origin/main", ahead, cwd=repo, env=env)
+        ck("refresh_lint: detaches the lint clone at the edit checkout's origin/main, with no network",
+           refresh_lint(argparse.Namespace(edit_checkout=str(repo), lint_clone=str(repo))) == ""
+           and _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip() == ahead)
+        ck("refresh_lint: names the clone that did not move (null control: a missing clone is refused)",
+           "wanted" in refresh_lint(argparse.Namespace(edit_checkout=str(repo), lint_clone=str(t / "nowhere"))))
         stub = t / "stub.py"
         (t / "calls").write_text("")
         (t / "mode").write_text("moved1")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
