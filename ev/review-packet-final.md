# Review packet #3546
head: 10173609c4ac5cebfa00d96c9d5a609f2bb443a6
base: 7eadd75f3c420404aabc83d4b05f9691f3e49136

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=131995219620 success
arch-score / arch-score id=132019515192 success
arm id=131994792487 skipped
budget-raise-gate / budget-raise-gate id=132019573178 success
cancel-superseded id=132019590181 success
codeql id=132019514943 skipped
codeql / Analyze (actions) id=131995101603 success
codeql / Analyze (javascript-typescript) id=131995101554 success
codeql / Analyze (python) id=131995101572 success
gate id=132019513551 success
governance id=132019616368 skipped
governance / delivery-status id=131995101652 success
governance / delivery-status-publish id=131995104519 skipped
governance / env-matrix id=131995101685 success
governance / instrument-self-tests id=131995101638 success
governance / policy-docs id=131995101646 success
governance / record id=131995104147 skipped
governance / wave-script id=131995101709 success
hassfest id=132019610775 skipped
hassfest / hassfest id=131995101206 success
kernel-points id=132019568758 skipped
pr-contract id=132019514939 skipped
pr-contract / pr-contract id=132018438538 success
prelude id=132019513652 success
refresh id=132019514410 success
sweep-self id=132020027625 skipped
tests id=132019514651 skipped
tests / arch-instrument id=131995566003 success
tests / briefs id=131995101592 success
tests / browser id=131995566027 success
tests / ci-ratchet id=132015852115 skipped
tests / claims-autofix id=132011907378 skipped
tests / closure-scope id=131995101706 success
tests / closures id=131995566009 success
tests / closures-autofix id=132012136413 skipped
tests / coverage id=131995566032 success
tests / coverage-ratchet id=132015849594 success
tests / fast (3.14) id=131995565916 success
tests / graders-head-copy id=132015849593 success
tests / lane-proofs id=132015849668 success
tests / mutation id=131995101565 success
tests / mutation-autofix id=131995526250 skipped
tests / mutation-pins id=131995525526 skipped
tests / nightly-ha id=131995568473 skipped
tests / nightly-status id=131995101823 success
tests / replay id=131995568994 skipped
tests / typing id=131995565960 success
validate id=132019575908 skipped
validate / validate-hacs id=131995101416 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/update_pr.sh --self-test
             `tools/audit/seat/update_pr.sh` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step update-pr
             `tools/ci/selftest_scope.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 5d2c0a30ec65f2d4d4f5976ee50937737e19c089)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 5d2c0a30ec65f2d4d4f5976ee50937737e19c089
Fix review: blocked 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 introduced-red: instrument-self-tests step "Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures" is red at the head and not at the base; the 5 FAIL rows are this PR's own update_pr figure-refresh arms

bus-nonce: a64ab4024544a06f2b66e10d48d5f750

## Block

- Round 1 (re-fire of the first review: same nonce, same head; no earlier verdict on probe/rev-3546-*).
- `merge_train.py classify 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 --pr 3546` exits 1: `RED 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 pending: none red: none introduced: 1` / `INTRODUCED Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures`. `review_packet.py` refuses on the same signal (`introduced-red`, head job 131858573499 against base job 131807475579). Under fix-review.md step 11 an INTRODUCED instrument-self-tests step is the PR's own finding and a block.
- Job 131858573499's log (ev/ci-job-131858573499-excerpt.txt) reads `pr_args self-test: 251 checks, 5 failed`. All five FAIL rows are arms this diff adds to tools/audit/seat/pr_args.sh (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH): the moved-head arm, the failing-refresh-at-push arm, the body-only arm, the mut:updfig2 mutant arm and the failing-refresh-on-body-only arm. The mut:updfig1 arm and both no-block null controls pass. A FAIL on the positive arm means the main path is not proven in CI, and the mut:updfig2 arm failing means that mutant's kill is not shown either.
- My own run at this head in a cloud container, `bash tools/audit/seat/pr_args.sh --self-test`, gives `251 checks, 0 failed` (rc 0, 4m55s; ev/selftest-head-local.tail.txt). So the new arms depend on the host: they pass here and fail on the CI runner. Every arm that fails in CI writes a figure block into the body, and both arms with no block pass. That points at the stubbed `tools/pr/figure_block.py` / `$PRT` resolution or at the `ubp.sh` body_patch stub as they behave on the runner. I did not establish the cause: CI keeps none of the arm's `$t/out`. The fixer owes a diagnosis and a fix that turns the step green on the runner, plus the body's `## Red checks` answer (defect-root-cause.md: the cheaper detector, which is this self-test run locally and which passed, so the gap is host parity).

## Evidence

- Head reviewed: 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 (ev/HEAD.txt). `git ls-remote origin refs/pull/3546/head` returned the same SHA just before the push (ev/live-head.txt).
- Merge base 7eadd75f3c420404aabc83d4b05f9691f3e49136. `git merge-tree --write-tree origin/main <head>` with the claimnotes driver installed exits 0, so no conflict (ev/merge-tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched in the three-dot diff (ev/version-untouched.txt).
- The diff covers update_pr.sh (`upd_figures`, called before body_patch.sh on the body-only path and before app_push.sh on the push path), its instrument note, the pr_args.sh arms, tools/ci/selftest_closures.json (entries collapsed to `D/**` globs, which only widen the closure, plus `dev/programme/delivery/5.md`) and the delivery row. An extractor read confirmed that app_push.sh pushes the local commit objects unchanged (HEAD==tip guard and read-back), and that no commit or HEAD move follows `upd_figures "at the head to push"` in update_pr.sh. So the block is rendered at the head actually pushed, matching open_pr.sh's op_figures (which also passes `--head HEAD`). That part of the design is sound and is not what blocks.
- Required checks: classify reports `pending: none red: none`. `merge_train.py owed-reds` does not list instrument-self-tests, so the block rests only on step 11's INTRODUCED clause.
- Mutation proof: not re-run independently at this round. The block is decided by CI, and the PR's own mutant arms are among the reds on the runner.

## Delta diff: git diff 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 10173609c4ac5cebfa00d96c9d5a609f2bb443a6
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 4204ada93d..3f6ec3c8fa 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -475,9 +475,17 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
 # copyin carries ref_privacy.py for the same reason: handoff_push.sh's guard
 # fails closed without it, so its reap arms never reached a push (#2668's CI).
 pr_args_self_test() (
-  local src t f=0 n=0 o m base code side body i reapsha UNREL
+  local src seat t f=0 n=0 o m base code side body i reapsha UNREL
   src=$PR_ARGS_DIR
   t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
+  # The programs under test are copied from a snapshot of them taken here, never from the live
+  # checkout: a job step that moves the checkout mid-run (tick_loop.sh's restart onto origin/main)
+  # would otherwise hand the later arms the base's copies (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH).
+  # Only the files the arms copy in, and roster_lib.py, which pr_cap.py loads from beside itself: an arm
+  # naming one not listed fails at its cp, never reads the tree.
+  seat=$t/seat; mkdir "$seat" && (cd "$src" && cp -p delivery_row.sh gh_read.py handoff_push.sh open_pr.sh \
+    pr_args.sh pr_cap.py ref_privacy.py remerge_main.sh roster_lib.py update_pr.sh "$seat/") \
+    || { echo "pr_args self-test: no snapshot of the programs under test"; rm -rf "$t"; return 1; }
   # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
   REAP_DIR=$t; export REAP_DIR
   # A stopped pusher's stub app_push: it records itself and a two-level sleep
@@ -532,8 +540,8 @@ STUB
   copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
     local g
     for g in open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh pr_cap.py ref_privacy.py gh_read.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
   }
   i=0
@@ -682,8 +690,8 @@ STUB
   git -C "$o" reset -q --hard "$base"
   relsrc() { # <mutant|-> <fresh clone> <sibling>: source by a relative path, cd to the sibling, ask
     mkdir -p "$2/tools/audit/seat"
-    if [ "$1" = - ]; then cp "$src/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
-    else grep -v "# mut:$1\$" "$src/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
+    if [ "$1" = - ]; then cp "$seat/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
+    else grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
     ( unset PR_ARGS_DIR; cd "$2" && . ./tools/audit/seat/pr_args.sh && cd "$3" && PR_NAME=fresh pr_tools_fresh ) > "$t/out" 2>&1
   }
   relsrc - "$t/fr" "$t/st"; ck "pr_args: sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" $?
@@ -1249,8 +1257,8 @@ STUB
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null
     git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
     done
     cp "$t/body.md" "$t/bR.md"
     HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
@@ -1334,7 +1342,7 @@ STUB
     sd=$(cd "$sd" && pwd -P); rm -rf "$sdir"; mkdir -p "$sdir"; figbody "$2"
     printf 'z\n' > "$o/zz" && git -C "$o" add zz && git -C "$o" -c user.name=t -c user.email=t@t commit -q -m "main file"
     for g in open_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" f "$codeF" T G > "$t/fo" 2>&1; echo $? > "$t/frc"
     git -C "$o" cat-file -e fix/f-pr:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/frow" || echo 0 > "$t/frow"
@@ -1531,7 +1539,7 @@ GH
     rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null; git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     case ${2:-} in edit) touch "$sdir/editfail" ;; postpush) touch "$sdir/p2postfail" ;; selftest) touch "$sdir/p2selftest" ;; host) touch "$sdir/p2selftest" "$sdir/hostfail" ;; stmix|body) touch "$sdir/p2$2" "$sdir/hostfail" ;;
       stalefig) touch "$sdir/hostfail" "$sdir/figfail"; mkdir -p "$sd/pr/r" && printf '  REFUSE   self-test             FAIL x\n' > "$sd/pr/r/p2.log" ;; *) touch "$sdir/p2fail" ;; esac
@@ -1623,11 +1631,11 @@ STUB
   }
   hrlib() { # <-|mutant|ret:tag|shared>: the library the next hrrun sources; ret:<tag> turns that line's `|| return 1` into `|| return 0`
     case $1 in
-      -) cp "$src/pr_args.sh" "$t/hr/lib.sh" ;;
-      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      -) cp "$seat/pr_args.sh" "$t/hr/lib.sh" ;;
+      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
       # one tree for every measurement, replaced by whichever run starts next: the blocked head's pr_step_sig
-      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
-      *) grep -v "# mut:$1\$" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
+      *) grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
     esac
   }
   hrrun() { # <head sha> [main sha] [log] -> pr_host_refusal's status
@@ -1796,7 +1804,7 @@ STUB
     local sd=$t/mconf-$1 g
     rm -rf "$sd"; mkdir -p "$sd"; sd=$(cd "$sd" && pwd -P); git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd BR=fix/q BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" q "$codeR" T G > "$t/outq" 2>&1; echo $? > "$t/rcq"
     [ -d "$sd/pr/q/wt" ] && echo kept > "$t/wtq" || echo gone > "$t/wtq"
@@ -1819,8 +1827,8 @@ STUB
     local sd=$t/unp-$1-$2 g
     rm -rf "$sd" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
     [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
@@ -1914,7 +1922,7 @@ STUB
   fi
   rmrun() { # <mutant|-> <branch>: remerge_main.sh on <branch> in worktree $t/rmw; the output in $t/out
     local g; git -C "$t/rmm" worktree remove --force "$t/rmw" 2>/dev/null; rm -rf "$t/rmw"; git -C "$t/rmm" worktree prune
-    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$src/$g" > "$t/rmm/tools/audit/seat/$g"; done
+    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$seat/$g" > "$t/rmm/tools/audit/seat/$g"; done
     git -C "$t/rmm" fetch -q origin "$2" && git -C "$t/rmm" worktree add -q -B "$2" "$t/rmw" "origin/$2" \
       && PATH="$t/rmgit:$PATH" bash "$t/rmm/tools/audit/seat/remerge_main.sh" 7 "$t/rmw" "$2" "$t/body.md" > "$t/out" 2>&1
     echo $? > "$t/rc"
@@ -2079,7 +2087,7 @@ print(n)' "$1"
   # line above leaves that line running on into the next (round 2's first mut:fggc did, and its arm
   # read the broken copy as a pass). mutshape <files...>: exit 1 naming each such line.
   mutshape() { awk 'prev ~ /\\$/ && /# mut:[A-Za-z0-9]+$/ { print FILENAME ":" FNR; bad = 1 } { prev = $0 } END { exit bad }' "$@"; }
-  (cd "$src" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
+  (cd "$seat" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
   ck "every # mut: line is a whole statement, never one continued from the line above" $?
   printf 'a \\\n  b  # mut:x\n' > "$t/mutshape.sh"; ! mutshape "$t/mutshape.sh" >/dev/null
   ck "null control: a # mut: line continued from the line above is named" $?
@@ -2091,7 +2099,7 @@ print(n)' "$1"
   rkrun() { # <mutant|-> <stub rc> -> $t/rk.argv: what the stub saw; $t/rk.err: the statement's stderr
     : > "$t/rk.argv"
     printf '#!/bin/bash\necho "$*" >> "%s/rk.argv"\nexit %s\n' "$t" "$2" > "$t/rkseat/bus.sh"
-    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$src/open_pr.sh"; else grep -h '# mut:rekey$' "$src/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
+    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$seat/open_pr.sh"; else grep -h '# mut:rekey$' "$seat/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
     SEAT=$t/rkseat PR_NAME=open_pr T=ht N=77 bash "$t/rk.line" 2> "$t/rk.err"
     echo $? > "$t/rk.rc"
   }
@@ -2104,7 +2112,7 @@ print(n)' "$1"
   rkrun rekey 0; [ ! -s "$t/rk.argv" ]
   ck "  mutant mut:rekey (its line deleted) re-keys nothing" $?
   # The cap's own counting rule, which orchestrator_tick.py imports too.
-  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
+  python3 -I "$seat/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
   ck "pr_cap.py --self-test: its tally says 0 failed" $?
   reap
   kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
