# Review packet #3546
head: 5d2c0a30ec65f2d4d4f5976ee50937737e19c089
base: 7eadd75f3c420404aabc83d4b05f9691f3e49136

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131858785113 success
arch-score / arch-score id=131883569773 success
arm id=131855554254 skipped
budget-raise-gate / budget-raise-gate id=131883569894 success
cancel-superseded id=131883634817 success
codeql id=131883569415 skipped
codeql / Analyze (actions) id=131858573323 success
codeql / Analyze (javascript-typescript) id=131858573423 success
codeql / Analyze (python) id=131858573466 success
gate id=131883570107 success
governance id=131883648026 skipped
governance / delivery-status id=131858573336 success
governance / delivery-status-publish id=131858575192 skipped
governance / env-matrix id=131858573371 success
governance / instrument-self-tests id=131858573499 failure
governance / policy-docs id=131858573614 success
governance / record id=131858575959 skipped
governance / wave-script id=131858573619 success
hassfest id=131883569176 skipped
hassfest / hassfest id=131858573643 success
kernel-points id=131883569972 skipped
pr-contract id=131883572047 skipped
pr-contract / pr-contract id=131882682147 success
prelude id=131883569122 success
refresh id=131883568352 success
sweep-self id=131883957416 skipped
tests id=131883570959 skipped
tests / arch-instrument id=131859142827 success
tests / briefs id=131858574027 success
tests / browser id=131859142761 success
tests / ci-ratchet id=131880279678 skipped
tests / claims-autofix id=131873750437 skipped
tests / closure-scope id=131858574006 success
tests / closures id=131859142943 success
tests / closures-autofix id=131880279328 skipped
tests / coverage id=131859142777 success
tests / coverage-ratchet id=131879539360 success
tests / fast (3.14) id=131859143018 success
tests / graders-head-copy id=131879539410 success
tests / lane-proofs id=131879539425 success
tests / mutation id=131858573889 success
tests / mutation-autofix id=131862792394 skipped
tests / mutation-pins id=131862792286 skipped
tests / nightly-ha id=131859144406 skipped
tests / nightly-status id=131858573920 success
tests / replay id=131859144912 skipped
tests / typing id=131859143044 success
validate id=131883634511 skipped
validate / validate-hacs id=131858573676 success

## Refusals
introduced-red: INTRODUCED `Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures`: a step of the non-required instrument-self-tests job red at 5d2c0a30ec65f2d4d4f5976ee50937737e19c089 and not at the base (head job 131858573499 failure base job 131807475579 failure), a finding of this pull request (fix-review.md)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step update-pr
             `tools/ci/selftest_scope.py` is in the tree at this head
  unverified git show HEAD:tools/ci/selftest_closures.json
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3546.md b/dev/programme/delivery/3546.md
new file mode 100644
index 0000000000..375ea41b10
--- /dev/null
+++ b/dev/programme/delivery/3546.md
@@ -0,0 +1 @@
+- [#3546](https://github.com/tvofi/heatpump_optimizer/pull/3546) — **open**, R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: r10 hotfix updatepr figure refresh (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH)
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
index f964bc717c..eac78f7f29 100644
--- a/tools/audit/seat/instruments/update_pr.sh.md
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -17,6 +17,7 @@
   body move of a PR whose head holds its handoff, with `HPO_UPDATE_BODY_ONLY=1`:
   a run that would then move the head (a DIRTY PR's clean main merge, an added
   row) refuses and pushes nothing, since that move skipped the review freeze.
+  A body carrying a generated figure block has it re-rendered (`figure_block.py refresh`, as `open_pr.sh` does) at the head the run pushes or patches, on both paths, before app_push.sh or body_patch.sh; a failed refresh refuses, pushing and patching nothing; a body with no block is untouched.
   When: updating a PR after review prep or a main merge, or re-bodying it.
   Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
   silently; no open PR at the branch stops before any push. Up front, each an
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 51d9fee02d..4204ada93d 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -1355,6 +1355,59 @@ STUB
   ck "open_pr: a re-run after an open closed at its row push clears the left-over branch and worktree and opens" $?
   figrun opfig2 block; figrun opclear block keep; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ]
   ck "  mutant mut:opclear (its line deleted): the re-run fails at git worktree add -b on the left-over branch (the defect)" $?
+  # R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: update_pr.sh re-renders the body's figure blocks at the head it
+  # pushes (moved-head path, before app_push) or patches (body-only path, before body_patch.sh), as
+  # open_pr.sh's op_figures does. fix/g starts at $base; handoff/f's pusher stub is lint's figure-block
+  # head check; the stub figure_block.py rewrites head= to HEAD, notes each call and fails while $t/figfail exists.
+  cat > "$m/tools/pr/figure_block.py" <<STUBF
+import os, re, subprocess, sys
+open("$t/figcalled", "a").close()
+if os.path.exists("$t/figfail"): sys.exit(1)
+f = sys.argv[sys.argv.index("refresh") + 1]
+h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
+t = re.sub(r"head=[0-9a-f]{40}", "head=" + h, open(f).read())
+open(f, "w").write(t)
+STUBF
+  cp "$t/bin/gh" "$t/gh.orig"
+  printf '#!/bin/sh\ncase "$*" in *--head*) echo 5 ;; *mergeStateStatus*) echo CLEAN ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' > "$t/bin/gh"
+  printf '#!/bin/bash\necho called >> "%s/ubp.log"\nh=$(grep -o "^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*" "$5" | grep -o "head=.*" | cut -c6-)\n[ -z "$h" ] || [ "$h" = "$4" ] || { echo "body_patch: REFUSE: figure-block scope-line names another head ($h)"; exit 1; }\necho "body_patch: OK"\n' "$t" > "$t/ubp.sh"
+  ufig() { # <mutant|-> <code sha|-> <block|none>: update_pr.sh fix/g over a body with (or without) a figure block naming the code head
+    rm -f "$t/figcalled"
+    if [ "$3" = block ]; then printf '## Head\n\nthe body\n\n## Figures\n\n<!-- figure-block: scope-line mb=%s head=%s -->\n~~~text\nx\n~~~\n<!-- /figure-block -->\n' "$base" "$codeF" > "$t/bu.md"
+    else printf '## Head\n\nthe body\n' > "$t/bu.md"; fi
+    git -C "$o" rev-parse fix/g > "$t/ubefore" 2>/dev/null || echo none > "$t/ubefore"
+    HANDOFF_TOPIC=f HPO_BODY_PATCH=$t/ubp.sh run "$1" update_pr.sh fix/g "$2" "$t/bu.md"
+    git -C "$o" rev-parse fix/g > "$t/uafter"
+  }
+  ufresh() { git -C "$o" branch -f fix/g "$base"; rm -f "$t/figfail" "$t/ubp.log"; }
+  ubody() { grep -o '^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*' "$t/bu.md" | grep -o 'head=.*' | cut -c6-; }
+  ufresh; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(cat "$t/uafter")" != "$(cat "$t/ubefore")" ]
+  ck "update_pr: a moved head with a figure block pushes a body whose block names the new head" $?
+  ufresh; ufig updfig1 "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig1 (its line deleted): the push carries a block naming another head and is refused" $?
+  ufresh; touch "$t/figfail"; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the head to push failed" "$t/out" && [ "$(cat "$t/uafter")" = "$base" ]
+  ck "update_pr: a failing refresh at the head to push refuses and pushes nothing" $?
+  ufresh; ufig - "$codeF" block; rm -f "$t/ubp.log"
+  ufig - - block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ] && grep -qF "update_pr: BODY-ONLY" "$t/out" && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(wc -l < "$t/ubp.log")" = 1 ]
+  ck "update_pr: a body-only run over a block naming the code head patches a body naming the live head" $?
+  ufig updfig2 - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "body_patch: REFUSE: figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig2 (its line deleted): body_patch.sh is handed a block naming another head and refuses" $?
+  rm -f "$t/ubp.log"; touch "$t/figfail"; ufig - - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the unmoved head failed" "$t/out" && [ ! -e "$t/ubp.log" ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ]
+  ck "update_pr: a failing refresh on the body-only path refuses and patches nothing" $?
+  ufresh; ufig - "$codeF" none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && ! grep -q 'figure-block' "$t/bu.md"
+  ck "null control: a body with no figure block never reaches the refresh and is pushed as before" $?
+  ufresh; ufig - "$codeF" none; ufig - - none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && grep -qF "update_pr: BODY-ONLY" "$t/out"
+  ck "null control: a body-only run over a body with no figure block never reaches the refresh" $?
+  git -C "$o" branch -qD fix/g; git -C "$o" reset -q --hard "$base"; cp "$t/gh.orig" "$t/bin/gh"
+  git -C "$m" worktree prune; git -C "$m" branch -qD fix/g 2>/dev/null; git -C "$m" update-ref -d refs/remotes/origin/fix/g; true
   # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
   # is DIRTY or the merge would conflict, and a head the run leaves unmoved is re-bodied by
   # body_patch.sh (here a stub, HPO_BODY_PATCH) with no push. handoff/v carries a push stub that
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 60a11a9b94..7eb760edd7 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -97,6 +97,15 @@ TTL=$(gh pr view "$N" -R $R --json title -q .title)
 _added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
 ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
 M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
+# A generated figure block names the head it was rendered at (figure_block.py refresh, as open_pr.sh's
+# op_figures), and the merges and the row above moved it: re-render at the head this run pushes or patches,
+# before either. A body with no block is untouched; a failed refresh refuses, pushing and patching nothing.
+upd_figures() { # <where>
+  grep -q '^<!-- figure-block: ' "$B" || return 0
+  python3 -I "$PRT/figure_block.py" refresh "$B" --base origin/main --head HEAD > $WT.fig.log 2>&1 && return 0
+  pr_refuse "the figure-block refresh $1 failed; nothing is pushed or patched:
+$(tail -n 20 $WT.fig.log)"
+}
 # HPO_UPDATE_BODY_ONLY (cloud_relay.sh's handoff_arm, on a body-only move it does not review-freeze):
 # the head must stay the live head, so a DIRTY merge of main or an added row refuses, pushing nothing
 # (#3089 review round 2): only the orchestrator, past the freeze, moves a head under review.
@@ -117,6 +126,7 @@ import sys; from head_note import prefix
 p,H=sys.argv[1:3]; s=open(p).read()
 s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
 E
+  upd_figures "at the unmoved head"  # mut:updfig2
   rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
   cat $WT.log
   [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
@@ -131,6 +141,7 @@ if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s
 else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
 s=prefix(s,pre); open(p,'w').write(s)
 E
+upd_figures "at the head to push"  # mut:updfig1
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
 [ -n "$RO" ] || RO=--reuse  # mut:updreuse
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index d56ec9a60d..f5a326bae7 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -1387,22 +1387,7 @@
     "dev/audit/rounds/round4/D1/verify2_d102.py",
     "dev/audit/rounds/round4/D1/verify2_d1inst.py",
     "dev/audit/rounds/round4/D10",
-    "dev/audit/rounds/round4/D10/coverage_measure.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-02.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-03.py",
-    "dev/audit/rounds/round4/D10/log_when_unavailable.py",
-    "dev/audit/rounds/round4/D10/mypy_arms.sh",
-    "dev/audit/rounds/round4/D10/qs_rules.out.txt",
-    "dev/audit/rounds/round4/D10/qs_rules.py",
-    "dev/audit/rounds/round4/D10/quality_scale.draft.yaml",
-    "dev/audit/rounds/round4/D10/reports",
-    "dev/audit/rounds/round4/D10/reports/FINDER.md",
-    "dev/audit/rounds/round4/D10/verify-0-1.md",
-    "dev/audit/rounds/round4/D10/verify-0-2.md",
-    "dev/audit/rounds/round4/D10/verify-0-3.md",
-    "dev/audit/rounds/round4/D10/verify3",
+    "dev/audit/rounds/round4/D10/**",
     "dev/audit/rounds/round4/D10/verify3/**",
     "dev/audit/rounds/round4/D11",
     "dev/audit/rounds/round4/D11/d11_own_D11-01.py",
@@ -1664,9 +1649,7 @@
     "dev/audit/rounds/round4/resume_row.py",
     "dev/audit/rounds/round5",
     "dev/audit/rounds/round5-fix",
-    "dev/audit/rounds/round5-fix/R5-D7",
-    "dev/audit/rounds/round5-fix/R5-D7/learner_guard_ends.py",
-    "dev/audit/rounds/round5-fix/R5-INST-01",
+    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5-fix/R5-INST-01/**",
     "dev/audit/rounds/round5/D0",
     "dev/audit/rounds/round5/D0/seat-a",
@@ -1709,9 +1692,7 @@
     "dev/audit/rounds/round5/D4/seat-a",
     "dev/audit/rounds/round5/D4/seat-a/sweep.mjs",
     "dev/audit/rounds/round5/D7",
-    "dev/audit/rounds/round5/D7/seat-a",
-    "dev/audit/rounds/round5/D7/seat-a/sysid_step_bias.py",
-    "dev/audit/rounds/round5/D7/seat-b",
+    "dev/audit/rounds/round5/D7/**",
     "dev/audit/rounds/round5/D7/seat-b/**",
     "dev/audit/rounds/round5/D8",
     "dev/audit/rounds/round5/D8/seat-b",
@@ -2419,23 +2400,8 @@
     "tools/audit/seat/wt_sync.sh",
     "tools/audit/worktree_gc.sh",
     "tools/ci",
-    "tools/ci/alert_list.py",
-    "tools/ci/alert_list_mutants.sh",
-    "tools/ci/codescan_wait.py",
-    "tools/ci/fixtures",
-    "tools/ci/fixtures/gate_busy_defer_runs.json",
-    "tools/ci/fixtures/ruleset",
+    "tools/ci/**",
     "tools/ci/fixtures/ruleset/**",
-    "tools/ci/gate.py",
-    "tools/ci/ghapi.py",
-    "tools/ci/prelude.py",
-    "tools/ci/ruleset_cutover.py",
-    "tools/ci/selftest_closures.json",
-    "tools/ci/selftest_scope.py",
-    "tools/ci/selftest_scope_mutants.sh",
-    "tools/ci/selftest_step.sh",
-    "tools/ci/sweep.py",
-    "tools/ci/sweep_selftest.py",
     "tools/coverage",
     "tools/coverage/**",
     "tools/devices",
@@ -9159,6 +9125,7 @@
     "-",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
