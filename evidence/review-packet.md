# Review packet #2989
head: 50b1956485ea01e78d97a0619a32cdc9dd923cdd
base: fe709cbd269c7c53eb1c846a0be7f39c7dab06ac

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124035281220 neutral
arch-score / arch-score id=124035014184 success
arm id=124034798246 skipped
budget-raise-gate / budget-raise-gate id=124035013893 success
cancel-superseded id=124034796245 success
codeql / Analyze (actions) id=124035014173 success
codeql / Analyze (javascript-typescript) id=124035014052 success
codeql / Analyze (python) id=124035014059 in_progress
governance / delivery-status id=124035014155 success
governance / delivery-status-publish id=124035016267 skipped
governance / env-matrix id=124035014385 in_progress
governance / instrument-self-tests id=124035014166 in_progress
governance / policy-docs id=124035014308 success
governance / record id=124035015794 skipped
governance / wave-script id=124035014161 success
hassfest / hassfest id=124035013798 success
kernel-points id=124035016398 skipped
prelude id=124034795844 success
refresh id=124034796201 success
tests / arch-instrument id=124035231519 success
tests / briefs id=124035013987 success
tests / browser id=124035231618 in_progress
tests / closure-scope id=124035014096 success
tests / closures id=124035231919 in_progress
tests / coverage id=124035231590 success
tests / coverage-ratchet id=124035550175 success
tests / fast (3.14) id=124035231575 in_progress
tests / graders-head-copy id=124035550241 in_progress
tests / mutation id=124035014260 success
tests / mutation-autofix id=124035317060 skipped
tests / mutation-pins id=124035315460 skipped
tests / nightly-ha id=124035234174 skipped
tests / nightly-status id=124035014061 success
tests / replay id=124035234126 skipped
tests / typing id=124035231630 in_progress
validate / validate-hacs id=124035013733 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/open_pr.sh --self-test
             `tools/audit/seat/open_pr.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2989.md b/dev/programme/delivery/2989.md
new file mode 100644
index 000000000..c8d824057
--- /dev/null
+++ b/dev/programme/delivery/2989.md
@@ -0,0 +1 @@
+- [#2989](https://github.com/tvofi/heatpump_optimizer/pull/2989) — **open**, R10-FLY-OPENPR-ATOMIC: close a PR whose row push is refused, with a read-back comment saying why (R10-FLY-OPENPR-ATOMIC)
diff --git a/tools/audit/seat/instruments/open_pr.sh.md b/tools/audit/seat/instruments/open_pr.sh.md
index c2bc94162..ea430aa46 100644
--- a/tools/audit/seat/instruments/open_pr.sh.md
+++ b/tools/audit/seat/instruments/open_pr.sh.md
@@ -18,5 +18,14 @@
   refused push names its log. It holds the branch's `upd-<branch>.lock` from
   before its worktree to its second push, so a concurrent `update_pr.sh` is BUSY
   (75) and cannot detach the worktree under the PR's row (#2547-#2549).
+  A refused second (row) push returns the worktree to the pushed head and
+  closes the draft with a comment, read back by `gh_comment.py`, quoting the
+  refusal (`open_pr: CLOSED: #N`), so no PR stays open without its row
+  (#2625, #2629); only a close that fails prints `ROWLESS`, for
+  `update_pr.sh`'s `ensure_row`. The PR is created only after the body
+  contract passes: `app_push.sh` runs `prepr.sh` and the `ref_privacy` guard
+  before its push. A main merge that conflicts is aborted and refused
+  (`merging origin/main into <sha> conflicts`), so the clean worktree is
+  released instead of kept as dirty.
   `--self-test` runs `delivery_row.sh`'s, then
   `pr_args.sh`'s.
diff --git a/tools/audit/seat/open_pr.sh b/tools/audit/seat/open_pr.sh
index 440874229..6ad8bada9 100755
--- a/tools/audit/seat/open_pr.sh
+++ b/tools/audit/seat/open_pr.sh
@@ -7,7 +7,8 @@
 # The row push (p2) asks app_push.sh for --row-only, so an open runs one full prepr, not two (P53),
 # and lands seconds after the PR rather than a prepr later, before CI on p1 can report a red the body
 # was never asked to answer (#2625, #2629). A refused row push returns the worktree to the pushed head
-# and says ROWLESS: update_pr.sh's ensure_row adds the row on its next run. Every exit's last act,
+# and closes the PR with a comment saying why, so no PR stays open without its row (CLOSED; a close
+# that fails says ROWLESS, and update_pr.sh's ensure_row adds the row). Every exit's last act,
 # under the branch lock, is pr_release_wt (pr_args.sh): the worktree is detached at the pushed head,
 # removed with its branch when origin never had it, or kept and named (P-D, P64, P72).
 # The tools are refused when origin/main is ahead of their checkout under tools/ (pr_tools_fresh).
@@ -54,7 +55,12 @@ git show "$PR_BT:BODY.md" > $D/body.md
 python3 -I "$SEAT/pr_cap.py" info --repo $R  # mut:openinfo
 git worktree add -q -b $BR $WT $C
 cd $WT
-git fetch -q origin main; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com merge -q --no-edit origin/main
+git fetch -q origin main
+# A conflicted merge is this run's own, not authored work: abort it, so pr_release_wt reads a clean
+# tree and removes the worktree origin never had, rather than keeping it as dirty (carry 8).
+MERGE_OK=; git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com merge -q --no-edit origin/main && MERGE_OK=1
+[ -n "$MERGE_OK" ] || git merge --abort  # mut:mergeabort
+[ -n "$MERGE_OK" ] || pr_refuse "merging origin/main into $C conflicts; merge it into handoff/$T, then re-run"
 PYTHONPATH="$PRT" python3 - $D/body.md $(git rev-parse HEAD) $C $(git rev-parse --short origin/main) <<'E0'
 import sys; from head_note import prefix
 p,H,C,M=sys.argv[1:5]; s=open(p).read()
@@ -85,7 +91,21 @@ RO=--row-only  # mut:oprowonly
 rc=0; wait $! || rc=$?
 if [ "$rc" != 0 ]; then
   git reset -q --hard "$PR_PUSHED"  # mut:rowreset
-  printf '%s: ROWLESS: #%s is open at %s without its row; update_pr.sh %s - <body> adds it (delivery_row.sh ensure_row)\n' "$PR_NAME" "$N" "$PR_PUSHED" "$BR" >&2
+  # A PR the row push left without its row is closed, not left open for the tick to find (#2625,
+  # #2629): its comment, read back by gh_comment.py, says why; re-running open_pr.sh once the body
+  # answers the refusal opens it afresh. Only a close that fails leaves it ROWLESS and open.
+  { grep -E 'REFUSE' $D/p2.log || tail -n 20 $D/p2.log; } > $D/p2.why 2>/dev/null || :
+  printf 'Closed by open_pr.sh: the push of this pull request'\''s own delivery row (`dev/programme/delivery/%s.md`) was refused, so it would stay open without its row. The refusal:\n\n```\n%s\n```\n\nRe-run `open_pr.sh %s` once the handoff body answers it.\n' \
+    "$N" "$(cat $D/p2.why)" "$T" > $D/close.md
+  python3 "$PRT/gh_comment.py" post --repo $R --issue "$N" --body-file $D/close.md >&2 \
+    || echo "$PR_NAME: the closing comment on #$N was not read back; the close goes ahead" >&2
+  closed=0; gh pr close "$N" -R $R >/dev/null && closed=1  # mut:rowclose
+  if [ "$closed" = 1 ]; then
+    PR_ATTEMPT=closed,PR=$N
+    printf '%s: CLOSED: #%s at %s, its row push refused; re-run open_pr.sh once the body answers it\n' "$PR_NAME" "$N" "$PR_PUSHED" >&2
+  else
+    printf '%s: ROWLESS: #%s is open at %s without its row, and closing it failed; update_pr.sh %s - <body> adds it (delivery_row.sh ensure_row)\n' "$PR_NAME" "$N" "$PR_PUSHED" "$BR" >&2
+  fi
   pr_push_failed $D/p2.log
 fi
 PR_PUSHED=$H
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index ba3b2f4c7..29f83d9c6 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1146,8 +1146,30 @@ STUB
   ck "  mutant mut:oprowonly (its line deleted): the row push runs the full prepr" $?
   # A refused row push (#2625, #2629: prepr refused p2 on a red CI reported after p1) left the row
   # commit unpushed in the opener's worktree, on the branch, and update_pr.sh refused it as unpushed
-  # work. The opener now returns its worktree to the pushed head and releases it, so the next
-  # update_pr.sh adds the row (delivery_row.sh's ensure_row) and the PR ends with it.
+  # work; the PR stayed open without its row. The opener now returns its worktree to the pushed head,
+  # releases it, and closes the PR with a read-back comment saying why, so the tick never finds an
+  # open PR without its row. This arm's gh records the close and answers gh_comment.py's post and
+  # read-back; `pr list` finds the PR only while it is open, as the real `--state open` does.
+  cat > "$t/rowless-gh" <<'GH'
+#!/usr/bin/env python3
+import json, os, sys
+d = os.environ["STUB_DIR"]; a = sys.argv[1:]; j = " ".join(a)
+if a[:2] == ["pr", "close"]:
+    open(os.path.join(d, "closed"), "w").write(j + "\n"); sys.exit(0)
+if a[:2] == ["pr", "list"]:
+    print("" if os.path.exists(os.path.join(d, "closed")) else 5); sys.exit(0)
+if a[:2] == ["pr", "view"]: print("a title"); sys.exit(0)
+if a[:2] in (["pr", "edit"], ["pr", "ready"]): sys.exit(0)
+if "--head" in a: print(5); sys.exit(0)
+if a[:1] == ["api"] and "--input" in a:
+    body = json.load(open(a[a.index("--input") + 1]))["body"]
+    open(os.path.join(d, "comment"), "w").write(body); print(json.dumps({"id": 1, "html_url": "u"})); sys.exit(0)
+if a[:1] == ["api"] and a[1].endswith("/issues/comments/1"):
+    print(json.dumps({"id": 1, "body": open(os.path.join(d, "comment")).read()})); sys.exit(0)
+sys.exit(99)
+GH
+  mkdir -p "$t/rowless-bin" && cp "$t/rowless-gh" "$t/rowless-bin/gh" && chmod +x "$t/rowless-bin/gh"
+  cp "$src/../../pr/gh_comment.py" "$m/tools/pr/gh_comment.py"
   rowless() { # <mutant>
     local sd=$t/rowless-$1 sdir=$t/rowless-$1-stub g
     rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
@@ -1156,19 +1178,48 @@ STUB
       if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
     done
     touch "$sdir/p2fail" "$sdir/p3ok"; cp "$t/body.md" "$t/bR.md"
-    HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1; echo $? > "$t/rco"
+    PATH="$t/rowless-bin:$PATH" HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1; echo $? > "$t/rco"
     git -C "$sd/pr/r/wt" symbolic-ref -q HEAD >/dev/null 2>&1 && echo branch > "$t/opwt" || echo detached > "$t/opwt"
-    HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/update_pr.sh" fix/r - "$t/bR.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
+    [ -e "$sdir/closed" ] && echo 1 > "$t/closed" || echo 0 > "$t/closed"
+    grep -qF 'was refused' "$sdir/comment" 2>/dev/null && grep -qF 'did not pass tools/pr/prepr.sh' "$sdir/comment" && echo 1 > "$t/why" || echo 0 > "$t/why"
+    PATH="$t/rowless-bin:$PATH" HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/update_pr.sh" fix/r - "$t/bR.md" > "$t/outu" 2>&1; echo $? > "$t/rcu"
     git -C "$o" cat-file -e fix/r:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/rowpushed" || echo 0 > "$t/rowpushed"
     reap; git -C "$m" worktree remove --force "$sd/pr/r/wt" 2>/dev/null; git -C "$m" worktree remove --force "$sd/pr/upd-fix-r" 2>/dev/null; true
   }
   rowless -
-  [ "$(cat "$t/rco")" != 0 ] && grep -qF "open_pr: ROWLESS: #5 is open" "$t/outo" && [ "$(cat "$t/opwt")" = detached ] \
+  [ "$(cat "$t/rco")" != 0 ] && grep -qF "open_pr: CLOSED: #5 at" "$t/outo" && grep -qF "identical=True" "$t/outo" \
+    && [ "$(cat "$t/closed")" = 1 ] && [ "$(cat "$t/why")" = 1 ] && [ "$(cat "$t/opwt")" = detached ] \
+    && ! grep -qF ROWLESS "$t/outo" && grep -qF "no open pull request at fix/r" "$t/outu" && [ "$(cat "$t/rowpushed")" = 0 ]
+  ck "open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree" $?
+  rowless rowclose
+  [ "$(cat "$t/closed")" = 0 ] && grep -qF "open_pr: ROWLESS: #5 is open" "$t/outo" && [ "$(cat "$t/opwt")" = detached ] \
     && [ "$(cat "$t/rcu")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
-  ck "open_pr: a refused row push leaves no stranded worktree, says the PR is rowless, and the next update_pr.sh lands the row" $?
+  ck "  mutant mut:rowclose (its line deleted): the PR stays open without its row (the defect); the next update_pr.sh lands it" $?
   rowless rowreset
-  [ "$(cat "$t/opwt")" = branch ] && grep -qF "(unpushed work" "$t/outu" && [ "$(cat "$t/rowpushed")" = 0 ]
-  ck "  mutant mut:rowreset (its line deleted): the row commit stays unpushed on the branch and update_pr.sh refuses it (the defect)" $?
+  [ "$(cat "$t/opwt")" = branch ] && [ "$(cat "$t/rowpushed")" = 0 ]
+  ck "  mutant mut:rowreset (its line deleted): the row commit stays unpushed on the branch in the opener's worktree (the defect)" $?
+  # A conflicted main merge was left in the opener's worktree, and pr_release_wt kept it as dirty
+  # work (carry 8); the opener now aborts its own merge and refuses, and the clean worktree, which
+  # origin never had, is removed with its branch. main gains a conflicting `b` for this arm only.
+  git -C "$o" checkout -q main && printf 'main b\n' > "$o/b" && git -C "$o" add b && git -C "$o" commit -q -m "main b" \
+    && git -C "$o" update-ref refs/heads/handoff-body/q "$body" && git -C "$o" branch -f handoff/q "$codeR"
+  mconf() { # <mutant>
+    local sd=$t/mconf-$1 g
+    rm -rf "$sd"; mkdir -p "$sd"; sd=$(cd "$sd" && pwd -P); git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null
+    for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
+      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+    done
+    HPO_STATE_DIR=$sd BR=fix/q BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" q "$codeR" T G > "$t/outq" 2>&1; echo $? > "$t/rcq"
+    [ -d "$sd/pr/q/wt" ] && echo kept > "$t/wtq" || echo gone > "$t/wtq"
+    git -C "$m" worktree remove --force "$sd/pr/q/wt" 2>/dev/null; git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null; true
+  }
+  mconf -
+  [ "$(cat "$t/rcq")" != 0 ] && grep -qF "open_pr: REFUSE: merging origin/main into $codeR conflicts" "$t/outq" && [ "$(cat "$t/wtq")" = gone ]
+  ck "open_pr: a main merge that conflicts is aborted and refused, and its clean worktree is removed" $?
+  mconf mergeabort
+  [ "$(cat "$t/wtq")" = kept ] && grep -qF "it is dirty" "$t/outq"
+  ck "  mutant mut:mergeabort (its line deleted): the conflicted worktree is kept as dirty work (the defect)" $?
+  git -C "$o" reset -q --hard HEAD~1; git -C "$o" branch -qD handoff/q; git -C "$o" update-ref -d refs/heads/handoff-body/q
   racerun oplock; [ "$(cat "$t/rcu")" != 75 ] && ! grep -qF "update_pr: BUSY" "$t/outu" && [ "$(cat "$t/rco")" = 0 ] && [ "$(cat "$t/rowpushed")" = 1 ]
   ck "  mutant mut:oplock (its line deleted): update_pr.sh takes the branch (not BUSY); the unpushed-work refusal alone keeps the row" $?
   racerun oplock+unpushed; [ "$(cat "$t/rco")" != 0 ] && grep -qF "is not the committed tip" "$t/outo" && [ "$(cat "$t/rowpushed")" = 0 ]

