# Review packet #3549
head: cde73e8b72fc563d515fd5ab66a6a12eec85698e
base: 3b9749dac55a85c200005352c661198c982e5799

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=131843397075 queued
arm id=131836392520 skipped
budget-raise-gate / budget-raise-gate id=131843397007 queued
cancel-superseded id=131836397547 queued
codeql / Analyze (actions) id=131843396754 queued
codeql / Analyze (javascript-typescript) id=131843396692 queued
codeql / Analyze (python) id=131843396644 queued
governance / delivery-status id=131843396759 queued
governance / delivery-status-publish id=131843399039 skipped
governance / env-matrix id=131843396899 queued
governance / instrument-self-tests id=131843396781 queued
governance / policy-docs id=131843396862 queued
governance / record id=131843398385 skipped
governance / wave-script id=131843397021 queued
hassfest / hassfest id=131843396578 queued
kernel-points id=131843398361 skipped
prelude id=131836397806 queued
refresh id=131836397853 queued
tests / briefs id=131843396705 queued
tests / closure-scope id=131843396715 queued
tests / mutation id=131843396609 queued
tests / nightly-status id=131843396619 queued
validate / validate-hacs id=131843396668 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131843396781: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/open_pr.sh --self-test
             `tools/audit/seat/open_pr.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3549.md b/dev/programme/delivery/3549.md
new file mode 100644
index 0000000000..b2769f696d
--- /dev/null
+++ b/dev/programme/delivery/3549.md
@@ -0,0 +1 @@
+- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **open**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS)
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 7f000786fd..0b14ad5890 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -41,7 +41,13 @@ export PATH=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/venv-ci/bin:$PATH
 M=$(cd "$(git -C "$(dirname -- "$0")" rev-parse --path-format=absolute --git-common-dir)/.." && pwd)
 T=$1; C=$2; TITLE=$3; G=$4; shift 4; ISS="$*"
 D=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/pr/$T; WT=$D/wt; BR=${BR:-fix/$T}; R=tvofi/heatpump_optimizer
-git -C "$M" show-ref -q --verify refs/heads/$BR && [ -z "${BR_FIXED:-}" ] && BR=$BR-pr  # a seat often holds a local branch of the default name
+# A topic's opener worktree $WT is shared by every opener of the topic (a seat's hand run, open_driver.py's), so the
+# branch it holds names the lock of the run holding it. A second opener adopts that branch and meets the first's lock
+# (BUSY) before it writes the shared body.md, not a -pr lock of its own. A detached worktree holds no branch: a
+# finished run's leftover, which takes the -pr name below as a lone run does.
+OP_REG=$(git -C "$M" worktree list --porcelain | awk -v w="worktree $WT" '$0==w{f=1;next} f&&/^branch /{sub("refs/heads/","",$2);print $2;exit} f&&$0==""{exit}')  # mut:opreg
+if [ -n "${OP_REG:-}" ] && [ -z "${BR_FIXED:-}" ]; then BR=$OP_REG
+elif git -C "$M" show-ref -q --verify refs/heads/$BR && [ -z "${BR_FIXED:-}" ]; then BR=$BR-pr; fi  # a seat often holds a local branch of the default name
 mkdir -p "$D"; cd "$M"
 # The branch's lock, update_pr.sh's own, held to the end: cloud_relay's update_pr.sh detached this worktree
 # between the two pushes below and left the PR without its row (#2547, #2548); it now answers BUSY.
@@ -145,7 +151,7 @@ MERGE_OK=; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.git
 PYTHONPATH="$PRT" python3 - $D/body.md $(git rev-parse HEAD) $C $(git rev-parse --short origin/main) <<'E0'
 import sys; from head_note import prefix
 p,H,C,M=sys.argv[1:5]; s=open(p).read()
-if H!=C: s=prefix(s,"`%s` merges origin/main `%s` into the authored code head `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below).\n\n"%(H,M,C))
+if H!=C: s=prefix(s,"`%s` merges origin/main `%s` into the authored code head `%s` (an automatic merge by the orchestrator\'s script; any resolution inside the code head is described below).\n\n"%(H,M,C))  # mut:headnote
 open(p,'w').write(s)
 E0
 # A disposed `## Unpinned sites` key the merge only shifted is re-keyed in place (P70, P125): prepr's
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 51d9fee02d..33a1683bbd 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1293,6 +1293,53 @@ STUB
   ck "  mutant mut:opcollect (its line deleted): open_pr.sh never asks for the collection" $?
   racerun oprowonly; [ "$(sed -n 2p "$t/argv" | cut -d' ' -f1)" = tvofi/heatpump_optimizer ]
   ck "  mutant mut:oprowonly (its line deleted): the row push runs the full prepr" $?
+  # R10-HOTFIX-OPENER-REFUSALS: two openers on one topic (a seat's hand run, open_driver.py's) share the
+  # topic-keyed state dir and its body.md, but the lock was keyed on the branch, and a second run renamed
+  # itself fix/<topic>-pr whenever the first's worktree add had made a local fix/<topic>: it took another lock,
+  # rewrote body.md from handoff-body without the head note, and refused later, while the first run's prepr
+  # read the overwritten body. dualrun starts open_pr.sh r twice, neither with BR_FIXED, the second while the
+  # first is in its second push; the main merge has moved the head, so the first's body.md carries a head note.
+  # Expected: the second is BUSY (75) and body.md is byte-identical. lonerun is the null control: one run
+  # beside a stale local fix/r and no registered worktree still takes the -pr name.
+  dualcopy() { # <mutant|->: the arm's scripts, with the mutant's line deleted
+    local g
+    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
+      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+    done
+  }
+  dualreset() { # <state dir> <stub dir>: no state, branch or worktree of the topic r survives, main one commit ahead
+    rm -rf "$1" "$2" "$t/s$i"; mkdir -p "$1" "$2"
+    git -C "$m" worktree prune; git -C "$m" branch -qD fix/r fix/r-pr 2>/dev/null; git -C "$o" branch -qD fix/r fix/r-pr 2>/dev/null
+    printf 'y\n' > "$o/yy" && git -C "$o" add yy && git -C "$o" -c user.name=t -c user.email=t@t commit -q -m "main moved"
+  }
+  dualend() { # <state dir>
+    reap; git -C "$m" worktree remove --force "$1/pr/r/wt" 2>/dev/null; git -C "$m" worktree prune; git -C "$o" reset -q --hard "$base"; true
+  }
+  dualrun() { # <mutant|->: rc of the second opener in $t/rc2, body.md before and after it in $t/bd1 and $t/bd2
+    local sd=$t/dual-state sdir=$t/dual-stub k=0 op
+    dualreset "$sd" "$sdir"; sd=$(cd "$sd" && pwd -P); dualcopy "$1"
+    env -u BR -u BR_FIXED HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout1" 2>&1 & op=$!
+    while [ ! -e "$sdir/p2started" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
+    cksum < "$sd/pr/r/body.md" > "$t/bd1"
+    env -u BR -u BR_FIXED HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout2" 2>&1; echo $? > "$t/rc2"
+    cksum < "$sd/pr/r/body.md" > "$t/bd2"
+    touch "$sdir/release"; wait "$op"; echo $? > "$t/rc1"
+    dualend "$sd"
+  }
+  lonerun() { # the null control: a stale local fix/r, no registered worktree, one run
+    local sd=$t/lone-state sdir=$t/lone-stub
+    dualreset "$sd" "$sdir"; sd=$(cd "$sd" && pwd -P); dualcopy -; touch "$sdir/release"
+    git -C "$m" branch -f fix/r "$base"
+    env -u BR -u BR_FIXED HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/dout3" 2>&1; echo $? > "$t/rc3"
+    git -C "$o" cat-file -e fix/r-pr:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/lrow" || echo 0 > "$t/lrow"
+    dualend "$sd"
+  }
+  dualrun -; [ "$(cat "$t/rc2")" = 75 ] && grep -qF "BUSY" "$t/dout2" && [ "$(cat "$t/bd1")" = "$(cat "$t/bd2")" ] && [ "$(cat "$t/rc1")" = 0 ] && grep -q '^PR=5 ' "$t/dout1"
+  ck "open_pr: a second opener on a topic whose opener worktree is registered is BUSY (75), body.md byte-identical, the first opens" $?
+  dualrun opreg; [ "$(cat "$t/rc2")" != 75 ] && [ "$(cat "$t/bd1")" != "$(cat "$t/bd2")" ]
+  ck "  mutant mut:opreg (its line deleted): the second opener takes the -pr lock, is not BUSY, and rewrites body.md (the defect)" $?
+  lonerun; [ "$(cat "$t/rc3")" = 0 ] && [ "$(cat "$t/lrow")" = 1 ]
+  ck "  null control: a lone opener beside a stale local fix/r and no registered worktree still takes fix/r-pr" $?
   # R10-HOTFIX-OPENPR-FIGURE-REFRESH: a figure block names the head it was rendered at, so the body
   # open_pr.sh pushes needs it re-rendered at each head it pushes (p1 when the main merge moved the
   # head, p2 always: the row commit moves it). The stub pusher is lint's figure-block head check; the
@@ -1310,6 +1357,9 @@ if [ -n "$h" ]; then
 else
   [ "$flag" != --row-only ] || echo "app_push: ROW-ONLY: prepr SKIPPED: only the row"
 fi
+if [ "$n" = 1 ] && [ "$(git -C "$wt" rev-list --parents -n1 HEAD | wc -w)" -ge 3 ]; then  # the main merge moved the head: the ## Head section names it
+  sed -n '/^## Head/,/^## Figures/p' "$body" | grep -q "$(git -C "$wt" rev-parse HEAD)" || { echo "app_push: REFUSE: ## Head does not name HEAD"; exit 1; }
+fi
 git -C "$wt" push -q -f origin "$br" || exit 1  # -f: a re-run's merge commit is not the first run's; the real pusher's refusal of that is outside this arm
 [ "$n" != 1 ] || echo "app_push: PUSHED to $br; pull request #5 is open"
 exit 0
@@ -1345,6 +1395,8 @@ STUB
   ck "open_pr: a body with a figure block opens (both pushes land, the row is present), the main merge having moved the head" $?
   figrun opfig2 block; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ] && grep -qF "figure-block scope-line names another head" "$t/fo" "$t/fp2" 2>/dev/null
   ck "  mutant mut:opfig2 (its line deleted): the row push is refused, naming another head, and the PR is closed" $?
+  figrun headnote block; [ "$(cat "$t/frc")" != 0 ] && ! grep -q 'pull request #5' "$t/fo" && grep -qF "## Head does not name HEAD" "$t/fo"
+  ck "  mutant mut:headnote (its line deleted): the head note is missing, so the code push is refused for a ## Head that does not name HEAD" $?
   figrun opfig1 block; [ "$(cat "$t/frc")" != 0 ] && ! grep -q 'pull request #5' "$t/fo" && grep -qF "figure-block scope-line names another head" "$t/fo"
   ck "  mutant mut:opfig1 (its line deleted): the code push is refused at the merged head, with nothing pushed" $?
   figrun - none; [ "$(cat "$t/frc")" = 0 ] && [ "$(cat "$t/frow")" = 1 ] && grep -qF "ROW-ONLY: prepr SKIPPED" "$t/fp2"
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index 73c05f6815..d0c6b0cf8f 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -661,6 +661,14 @@ def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
     return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))
 
 
+def fetch_round_rosters(run) -> None:
+    """CI's pr-contract fetches the round rosters' remote-tracking refs; a
+    --shared clone's own origin/handoff/* are root's local branches, so take
+    root's refs/remotes/origin ones. A glob matching nothing is harmless."""
+    run("git", "fetch", "-q", "--no-tags", "origin",
+        "+refs/remotes/origin/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster")
+
+
 def ci_tree_run(root: Path, tip: str, job: str, steps, workflow: str | None = None) -> tuple[str, subprocess.CompletedProcess | None]:
     """Run `steps` (each a function of the tree, its runner and a scratch
     directory) where CI's pull-request run of `job` runs them: the merge of
@@ -683,6 +691,7 @@ def ci_tree_run(root: Path, tip: str, job: str, steps, workflow: str | None = No
             return subprocess.run(a, cwd=r, env=env, input=input, capture_output=True, text=True)
 
         run("git", "update-ref", "refs/remotes/origin/main", tip)
+        fetch_round_rosters(run)  # mut:roundrefs
         run("git", "checkout", "-q", "--detach", tip)
         if run("git", "merge", "-q", "--no-ff", "-m", f"Merge {head} into {tip}", head).returncode:
             return "unmerged", None
@@ -1400,6 +1409,7 @@ def self_test() -> int:
     bad += mutant_self_test(root)
     bad += null_control_self_test(root)
     bad += graders_self_test(root)
+    bad += roundref_self_test(root)
     gate = root / "tools" / "ci" / "gate.py"
     if gate.exists():
         sys.path.insert(0, str(root / "tools" / "ci"))
@@ -1414,6 +1424,60 @@ def self_test() -> int:
     return 1 if bad else 0
 
 
+def roundref_self_test(root: Path) -> int:
+    """ci_tree_run's clone gets root's refs/remotes/origin round-roster refs,
+    not root's stale local branch (fail-before / pass-after), a null with the
+    remote-tracking ref absent, and the call line itself pinned."""
+    import inspect
+    import shutil
+    import tempfile
+    sys.path.insert(0, str(root / "tests"))
+    from throwaway_git import throwaway_git_clone, throwaway_git_init
+    ref = "refs/remotes/origin/handoff/audit-r10-roster"
+    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-roundref-"))
+    bad = 0
+
+    def check(label, ok):
+        nonlocal bad
+        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
+        bad += not ok
+    try:
+        for tracking in (True, False):
+            src = tmp / f"src{tracking}"
+            senv = throwaway_git_init(src, "-q", "-b", "main")
+
+            def sgit(*a):
+                return subprocess.run(a, cwd=src, env=senv, capture_output=True, text=True, check=True).stdout.strip()
+            sgit("git", "commit", "-q", "--allow-empty", "-m", "stale")
+            stale = sgit("git", "rev-parse", "HEAD")
+            sgit("git", "branch", "handoff/audit-r10-roster")
+            sgit("git", "commit", "-q", "--allow-empty", "-m", "newer")
+            newer = sgit("git", "rev-parse", "HEAD")
+            if tracking:
+                sgit("git", "update-ref", ref, newer)
+            r = tmp / f"clone{tracking}"
+            env = throwaway_git_clone(src, r, "-q", "--shared", "--no-checkout")
+
+            def run(*a, input=None):
+                return subprocess.run(a, cwd=r, env=env, input=input, capture_output=True, text=True)
+
+            def got():
+                return run("git", "rev-parse", "-q", "--verify", ref).stdout.strip()
+            check(f"clone's round ref is the stale local branch before the fetch (tracking={tracking})", got() == stale)
+            try:
+                fetch_round_rosters(run)
+                raised = False
+            except Exception:
+                raised = True
+            check(f"fetch_round_rosters {'takes root' + chr(39) + 's remote-tracking ref' if tracking else 'leaves the ref and does not raise'}",
+                  not raised and got() == (newer if tracking else stale))
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    line = [l for l in inspect.getsource(ci_tree_run).splitlines() if "fetch_round_rosters" in l]
+    check("ci_tree_run calls fetch_round_rosters on one `# mut:roundrefs` line", len(line) == 1 and "# mut:roundrefs" in line[0])
+    return bad
+
+
 def graders_self_test(root: Path) -> int:
     """The graders arm's key, population and run, with no load grammar to test.
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
