# Review packet #3455
head: cbf80c6e8b67b016d729b22f73c343b1f3eeaaed
base: cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130481991691 success
arch-score / arch-score id=130512856488 success
arm id=130479267863 skipped
budget-raise-gate / budget-raise-gate id=130512856275 success
cancel-superseded id=130512931247 success
codeql id=130512856656 skipped
codeql / Analyze (actions) id=130481245681 success
codeql / Analyze (javascript-typescript) id=130481245295 success
codeql / Analyze (python) id=130481245624 success
gate id=130512854657 queued
governance id=130512855199 skipped
governance / delivery-status id=130481245382 success
governance / delivery-status-publish id=130481248488 skipped
governance / env-matrix id=130481245167 success
governance / instrument-self-tests id=130481245277 success
governance / policy-docs id=130481245160 success
governance / record id=130481248065 skipped
governance / wave-script id=130481245281 success
hassfest id=130512909025 skipped
hassfest / hassfest id=130481245038 success
kernel-points id=130512858440 skipped
pr-contract id=130512855988 skipped
pr-contract / pr-contract id=130502882238 success
prelude id=130512909201 success
refresh id=130512854467 success
sweep-self id=130509644977 skipped
tests id=130512855655 skipped
tests / arch-instrument id=130482983716 success
tests / briefs id=130481245320 success
tests / browser id=130482983666 success
tests / ci-ratchet id=130502883110 skipped
tests / claims-autofix id=130489535437 skipped
tests / closure-scope id=130481245665 success
tests / closures id=130482983848 success
tests / closures-autofix id=130502883668 skipped
tests / coverage id=130482983610 success
tests / coverage-ratchet id=130495060881 success
tests / fast (3.14) id=130482983980 success
tests / graders-head-copy id=130495061033 success
tests / lane-proofs id=130495061087 success
tests / mutation id=130481245182 success
tests / mutation-autofix id=130482589615 skipped
tests / mutation-pins id=130482587783 skipped
tests / nightly-ha id=130482986330 skipped
tests / nightly-status id=130481245259 failure
tests / replay id=130482986059 skipped
tests / typing id=130482983656 success
validate id=130512919505 skipped
validate / validate-hacs id=130481245123 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item dca51f92: dismissed:landed in this PR's fixer.md sentence.
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r10_mutant_coverage.sh
             `dev/audit/harnesses/r10_mutant_coverage.sh` is in the tree at this head
  unverified git log refs/heads/handoff-body/<topic>
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git show <c>:BODY.md | grep MUTANT_CMD
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:pr MUTANT_CMD'
             gh api: every long flag accepted
  unverified git log --first-parent a7628041
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log 38e3d17e..4a927eed
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         bash tools/pr/prepr.sh <this body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 5 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_mutant_coverage.sh b/dev/audit/harnesses/r10_mutant_coverage.sh
new file mode 100644
index 000000000..2667801d0
--- /dev/null
+++ b/dev/audit/harnesses/r10_mutant_coverage.sh
@@ -0,0 +1,76 @@
+#!/usr/bin/env bash
+# R10-FIXER-MD-SPELLING-CORPUS carries 0 and 1: the measure-first behind
+# fixer.md step 2's "killing the diff's survivors is yours". Reproduces every
+# figure the pull request's body states from git alone (the bus refs) and
+# tools/audit/seat/mutant_run.py:
+#
+#   fetch                         the review/* and verdict/* bus refs, under refs/bus/
+#   blocks FROM UNTIL CLASS_RE    one line per (pr, head) blocked with a class
+#                                 matching CLASS_RE, verdict commit date in [FROM, UNTIL]:
+#                                 "<pr> <head> <first verdict time>"
+#   base HEAD TIME                main's first-parent tip at TIME, merged-based with HEAD:
+#                                 the diff base the fixer's prepr saw
+#   rank BASE HEAD FILE LINE..    the 1-based rank of the first listed mutant on each
+#                                 FILE:LINE in `mutant_run.py --diff --list` (cap 40 = rank <= 40),
+#                                 "none" when diff mode draws no mutant there
+#   repair PR HEAD                hours from the first block at HEAD to the next verdict
+#                                 at a different head (a same-head re-post is not a round)
+#   run BASE REV CMD [in-place]   wall seconds and SURVIVED lines of the capped report-only
+#                                 diff run at REV (in place: in a detached worktree at REV)
+#
+# RESULT window=168h — the coverage window is the 7 days before the merge base.
+# Null control: `run` at a head merged first pass (#3384, c620ebba^1...c620ebba^2)
+# reports survivors only inside orchestrator_tick.py's self_test(), none a
+# reviewer would name.
+set -u
+TOP=$(git rev-parse --show-toplevel) || exit 2
+cd "$TOP" || exit 2
+MR=tools/audit/seat/mutant_run.py
+case "${1:-}" in
+  fetch)
+    git fetch -q origin '+refs/heads/review/*:refs/bus/review/*' '+refs/heads/verdict/*:refs/bus/verdict/*' ;;
+  blocks)
+    from=$2; until=$3; cls=$4
+    for r in $(git for-each-ref --format='%(refname)' refs/bus/review refs/bus/verdict); do
+      git log --format='%H %cI' --since="$from" --until="$until" "$r" | while read -r c d; do
+        l=$(git show "$c:VERDICT.md" 2>/dev/null | head -1)
+        if grep -Eq "^Fix review: blocked [0-9a-f]{40} ($cls):" <<<"$l"; then
+          echo "${r##*/} $(cut -d' ' -f4 <<<"$l") $d"
+        fi
+      done
+    done | sort -k1,1n -k2,2 -k3,3 | awk '!seen[$1" "$2]++' ;;
+  base)
+    git merge-base "$(git rev-list -1 --first-parent --before="$3" origin/main)" "$2" ;;
+  rank)
+    b=$2; h=$3; f=$4; shift 4
+    list=$(python3 -I "$MR" --diff "$b...$h" --cmd true --list --max-mutants 0 2>&1 | grep '^MUTANT ')
+    for l in "$@"; do
+      r=$(grep -n "^MUTANT $f:$l " <<<"$list" | head -1 | cut -d: -f1)
+      echo "$f:$l rank=${r:-none} of $(grep -c . <<<"$list")"
+    done ;;
+  repair)
+    pr=$2; h=$3; bt=""
+    while read -r t c; do
+      l=$(git show "$c:VERDICT.md" | head -1)
+      if [ -z "$bt" ]; then case "$l" in "Fix review: blocked $h "*) bt=$t ;; esac; continue; fi
+      case "$l" in *" $h"*) continue ;; esac
+      echo "$pr ${h:0:8} block=$(date -u -d "@$bt" +%FT%TZ) next=$(date -u -d "@$t" +%FT%TZ) hours=$(awk -v a="$bt" -v b="$t" 'BEGIN{printf "%.2f", (b-a)/3600}')"
+      exit 0
+    done < <(git log --reverse --format='%ct %H' "refs/bus/verdict/$pr")
+    echo "$pr ${h:0:8} block=${bt:+$(date -u -d "@$bt" +%FT%TZ)} next=none" ;;
+  run)
+    b=$2; rev=$3; cmd=$4; mode=${5:-}; W=""
+    if [ "$mode" = in-place ]; then
+      W=$(mktemp -d "${TMPDIR:-/tmp}/mutcov.XXXXXX"); rmdir "$W"
+      git worktree add -q --detach "$W" "$rev" || exit 2
+      cd "$W" || exit 2; rev=HEAD; flag=--in-place
+    else flag=""; fi
+    s=$(date +%s.%N)
+    out=$(python3 -I "$MR" --diff "$b...$rev" --cmd "$cmd" --max-mutants 40 --report-only ${flag:+"$flag"} 2>&1); rc=$?
+    e=$(date +%s.%N)
+    grep -E '^(SURVIVED|BASELINE)' <<<"$out"
+    echo "rc=$rc wall_s=$(awk -v a="$s" -v b="$e" 'BEGIN{printf "%.1f", b-a}') survivors=$(grep -c '^SURVIVED' <<<"$out")"
+    if [ -n "$W" ]; then cd / && git -C "$TOP" worktree remove --force "$W" 2>/dev/null; fi ;;
+  *)
+    sed -n '2,24p' "$0"; exit 2 ;;
+esac
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 78aec355c..7ca0e9d4c 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -12,7 +12,6 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
 1. **Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md`
    heading** (`CLAUDE.md` rule 4). The rule is keyed on the manifest's
    `version` field, not the file; the command is `prepr.sh` step 5's.
-   Compare three-dot (`CLAUDE.md` rule 3).
 2. **Failing test first**, importing the production symbol (a test that
    re-implements a formula pins nothing; `tests/README.md`). Record the
    mutation proof in the PR body: delete the fix's production line(s), run
@@ -23,12 +22,15 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    A guard that classifies text by shape is driven over a generated spelling
    corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
    size named in the body; a spelling the reviewer finds is added to it.
-   A mutant run from a `git archive` copy fails the #363 `recorded_at` check
-   on every mutant, baseline included: the runner's, not the mutant's
-   (#1713, #1723). **When `--pin-killed` runs is `ci-autofix.md`'s.** `prepr.sh` step 6d lists the unpinned sites the diff adds; the body's
-   `## Unpinned sites` gives each its disposition: pinned by
-   `mutation-autofix` (its lane mutates `custom_components/` only; a `tools/`
-   site needs an in-tree mutant harness), a value check, or a triage under
+   A `git archive` copy fails the #363 `recorded_at` check, and a self-test
+   needing a checkout, on every mutant, baseline included (#1713, #1723).
+   **The diff's survivors are yours before the handoff; `--pin-killed` is
+   `ci-autofix.md`'s.** Set `prepr.sh`'s `MUTANT_CMD` to the group's self-test
+   or a `features_block.py` call (`MUTANT_IN_PLACE=1` for a checkout); it draws only
+   the first 40 mutants of added `.py` lines outside `tests/` and `dev/`. Each
+   `SURVIVED` line and step 6d unpinned site gets a killing check or an `## Unpinned
+   sites` disposition: pinned by `mutation-autofix` (its lane mutates `custom_components/`
+   only; a `tools/` site needs an in-tree mutant harness), a value check, or a triage under
    `tests/mutation_ledger/survivor_triage/` (the ratchet reads no body). Run the
    ledger's own mutant before claiming a kill (#2445).
 3. **Re-execute the finding's harness on your branch**: before and after, with
@@ -299,11 +301,8 @@ split part the approved plan names.
 
 ## Before you hand off: answer any check your branch turned red
 
-`defect-root-cause.md`'s second trigger fires on your own PR: name each red in
-`merge_train.py owed-reds`' set, and no other, in the body and answer it there:
-the cheaper detector and its standing cost, or a recorded finding that none exists.
-`UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them
-(`ci-autofix.md`). You name the trigger; analysing it is `root-cause.md`'s seat.
+`defect-root-cause.md`'s second trigger fires on your own PR, as its Enforcement section states.
+`UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them (`ci-autofix.md`).
 
 ## Past three rounds, re-cut rather than repair
 
diff --git a/dev/programme/delivery/3455.md b/dev/programme/delivery/3455.md
new file mode 100644
index 000000000..97fb92e22
--- /dev/null
+++ b/dev/programme/delivery/3455.md
@@ -0,0 +1 @@
+- [#3455](https://github.com/tvofi/heatpump_optimizer/pull/3455) — **open**, R10-FIXER-MD-SPELLING-CORPUS (part 2): r10 fixer md spelling corpus p2 (R10-FIXER-MD-SPELLING-CORPUS)
diff --git a/tests/closures.json b/tests/closures.json
index b8209d1b4..69127efc8 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4178,6 +4178,7 @@
    "dev/audit/harnesses/r10_mermaid_parse.mjs",
    "dev/audit/harnesses/r10_min_power_floor.py",
    "dev/audit/harnesses/r10_month_last_window_billed.py",
+   "dev/audit/harnesses/r10_mutant_coverage.sh",
    "dev/audit/harnesses/r10_mutant_skip/null_drive.py",
    "dev/audit/harnesses/r10_mutant_skip/replay.py",
    "dev/audit/harnesses/r10_night_folds_alternatives.py",
diff --git a/tools/audit/seat/instruments/mutant_run.py.md b/tools/audit/seat/instruments/mutant_run.py.md
index 5fd4ea7a5..9c30f5b07 100644
--- a/tools/audit/seat/instruments/mutant_run.py.md
+++ b/tools/audit/seat/instruments/mutant_run.py.md
@@ -15,7 +15,8 @@
   command's process group and restore. When: a mutation proof over several
   mutants, or a fixer checking that the group's self-test pins the lines the
   diff adds; `tools/pr/prepr.sh` runs the diff arm report-only when
-  `MUTANT_CMD` is set. Refusal, rc 2, before anything runs: a malformed spec, a
+  `MUTANT_CMD` is set (`--in-place` under `MUTANT_IN_PLACE=1`), and refuses a
+  run that measured nothing (rc 2 or 3) rather than reading it as no survivor. Refusal, rc 2, before anything runs: a malformed spec, a
   repeated name, an `old` not occurring exactly once, a target differing from
   HEAD. A survivor is answered in the PR body; an equivalent one still owes a
   `survivor_triage` record. `--self-test` builds throwaway repositories.
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 5df9e4c3a..58b5affda 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -1156,6 +1156,34 @@ moved_line() { # tree root, merge base -> one line; rc 0 clean, 1 refused, 3 ski
   return 1
 }
 
+# THE DIFF'S ADDED LINES MUTATED (R10-MUTANT-RUN-DRIVER, card 4; fixer.md step 2
+# makes running it the fixer's). `mutant_run.py --diff` applies its five
+# operators to each added Python line outside tests/ and dev/, the first
+# MUTANT_MAX (40) in file order, and runs MUTANT_CMD once per mutant. A run that
+# measured nothing -- the command failing on the unedited tree, a killed NULL, a
+# refusal -- is rc 1, never the "no survivor" an empty SURVIVED list would read
+# as: R10-FIXER-MD-SPELLING-CORPUS-P2 measured three of five fixer self-tests
+# failing in the git-archive copy, which `MUTANT_IN_PLACE=1` (`--in-place`) runs.
+mutants_line() { # tree root, base, command -> one line; rc 0 no survivor, 2 survivors (report only), 1 nothing measured, 3 skipped
+  [ -n "$3" ] || { echo "MUTANT_CMD unset -- set it to the group's self-test or features_block.py call (fixer.md step 2)"; return 3; }
+  [ -f "$1/tools/audit/seat/mutant_run.py" ] || { echo "tools/audit/seat/mutant_run.py is not in this tree"; return 3; }
+  local out r n
+  out=$(cd "$1" && python3 -I tools/audit/seat/mutant_run.py --diff "$2...HEAD" --cmd "$3" \
+    --max-mutants "${MUTANT_MAX:-40}" --report-only ${MUTANT_IN_PLACE:+--in-place} 2>&1); r=$?
+  if [ "$r" -ne 0 ]; then
+    echo "mutant_run rc=$r measured nothing: $(grep -v '^SURVIVED ' <<<"$out" | grep . | tail -1 | cut -c1-160) -- fix MUTANT_CMD, or set MUTANT_IN_PLACE=1 for a self-test that needs a git checkout"
+    return 1
+  fi
+  n=$(grep -c '^SURVIVED ' <<<"$out")
+  if [ "$n" -gt 0 ]; then
+    grep '^SURVIVED ' <<<"$out"
+    echo "$n survivor(s) on the diff's added lines -- each owes a killing check or a line under ## Unpinned sites (fixer.md step 2)"
+    return 2
+  fi
+  echo "no survivor among the diff's first ${MUTANT_MAX:-40} mutant(s) under: $3" | cut -c1-200
+  return 0
+}
+
 # --- closure-reachability skips for the heavy steps ---------------------------
 # WHY THIS EXISTS. A pull request whose diff is one delivery row, or one file
 # under tools/ or docs/, paid for prepr's heavy battery -- the mutants drive,
@@ -2344,6 +2372,40 @@ EOS
   st "$r" 3 "a tree with no tests/layout.py skips, never refuses"
   rm -rf "${LR:?}"
 
+  # The diff-mutant step, driven through `mutants_line` over a throwaway repo
+  # holding THIS tree's mutant_run.py: a branch adds lib.py (two mutable lines)
+  # and a check under tests/ (never mutated) that pins both.
+  MR=$(mktemp -d)
+  mkdir -p "$MR/tools/audit/seat" "$MR/dev/audit/harnesses" "$MR/tests" "$MR/custom_components/heatpump_optimizer"
+  echo '{}' > "$MR/custom_components/heatpump_optimizer/manifest.json"  # mutant_guard's repo-root marker
+  cp tools/audit/seat/mutant_run.py "$MR/tools/audit/seat/"
+  cp dev/audit/harnesses/mutant_guard.py "$MR/dev/audit/harnesses/"
+  mg() { git -C "$MR" -c user.name=t -c user.email=t@t -c commit.gpgsign=false "$@"; }
+  (mg init -q && mg checkout -q -b main && mg add -A && mg commit -qm base) >/dev/null 2>&1
+  MB=$(mg rev-parse HEAD)
+  printf 'def f(x):\n    if x > 0:\n        return 1\n    return 0\n' > "$MR/lib.py"
+  printf 'import sys\nsys.path.insert(0, ".")\nfrom lib import f\nsys.exit(0 if [f(v) for v in (-2, 0, 1, 2)] == [0, 0, 1, 1] else 1)\n' > "$MR/tests/check.py"
+  (mg add -A && mg commit -qm branch) >/dev/null 2>&1
+  got=$(mutants_line "$MR" "$MB" "false"); r=$?
+  st "$r" 1 "a MUTANT_CMD failing on the unedited tree is refused, never read as no survivor"
+  case "$got" in *'BASELINE FAILS'*) st 1 1 "and the refusal quotes mutant_run's own reason";; *) st 0 1 "and the refusal quotes mutant_run's own reason";; esac
+  got=$(mutants_line "$MR" "$MB" "python3 tests/check.py"); r=$?
+  st "$r" 0 "a check killing every mutant of the added lines passes (null control)"
+  # A check that needs the checkout (git) fails the archive copy's baseline and
+  # passes in place: the case MUTANT_IN_PLACE exists for, measured on 3379.
+  got=$(mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
+  st "$r" 1 "a check needing a git checkout measures nothing in the archive copy, and is refused"
+  got=$(MUTANT_IN_PLACE=1 mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
+  st "$r" 0 "the same check under MUTANT_IN_PLACE=1 runs in the checkout and passes"
+  st "$(mg status --porcelain | wc -l)" 0 "and the in-place run leaves the work tree clean"
+  got=$(mutants_line "$MR" "$MB" "true"); r=$?
+  st "$r" 2 "a command killing nothing reports its survivors, report only"
+  nl=$(cd "$MR" && python3 -I tools/audit/seat/mutant_run.py --diff "$MB...HEAD" --cmd true --list | grep -c '^MUTANT lib.py:')
+  st "$(grep -c '^SURVIVED lib.py:' <<<"$got"):$(grep -c '^SURVIVED' <<<"$got")" "$nl:$nl" "and names every listed mutant of lib.py, none of tests/check.py"
+  got=$(mutants_line "$MR" "$MB" ""); r=$?
+  st "$r" 3 "MUTANT_CMD unset skips"
+  rm -rf "${MR:?}"
+
   # The raw-git check, driven through `throwaway_line` over a shared clone of
   # THIS tree (so the check's allow-list finds the files it names and no entry
   # reads stale): a raw `git init` committed into an instrument self-test is the
@@ -2375,6 +2437,8 @@ EOS
   st $? 0 "the no-copies step calls copies_line, so a python diff runs closure.py no-copies before the push"
   case "$flow" in *'moved_line "'*) true ;; *) false ;; esac
   st $? 0 "the layout step calls moved_line, so a re-added moved path is refused before the push"
+  case "$flow" in *'mutants_line "$PWD" "$BASE" "${MUTANT_CMD:-}"'*) true ;; *) false ;; esac
+  st $? 0 "the diff-mutant step calls mutants_line, so a MUTANT_CMD that measures nothing is refused before the push"
   case "$flow" in *'throwaway_line "'*) true ;; *) false ;; esac
   st $? 0 "the repository-build step calls throwaway_line, so a raw build is refused ahead of the handoff"
   case "$flow" in *'"$BASE" HEAD "$UNPINNED_SITES"'*) true ;; *) false ;; esac
@@ -4470,33 +4534,22 @@ if [ -s "$UNPINNED_SITES" ]; then
   say WARN "unpinned sites" "$(grep -c . "$UNPINNED_SITES") site(s) the diff adds with no pin -- the body owes each a line under ## Unpinned sites (step 7d)"
 fi
 
-# --- 6d'. the diff's added lines mutated (R10-MUTANT-RUN-DRIVER, card 4), REPORT
-# ONLY: `mutant_run.py --diff` applies GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL
-# and CONST_SWAP to each added Python line and runs MUTANT_CMD, the group's named
-# self-test or `features_block.py` call, once per mutant. Each survivor is a WARN
-# line the body answers (an equivalent one still owes a survivor_triage record);
-# nothing here refuses, and with MUTANT_CMD unset the step skips. The cap keeps
-# the in-tree tier fast; the heavy pass (MUTANT_MAX=0, all mutants) is a cloud
-# seat's.
+# --- 6d'. the diff's added lines mutated: `mutants_line` above. Survivors are a
+# WARN the body answers; a run that measured nothing refuses; MUTANT_CMD unset
+# skips. The cap keeps the in-tree tier fast; the heavy pass (MUTANT_MAX=0, all
+# mutants) is a cloud seat's.
 if [ -n "$REUSE" ]; then
   say skip "code-keyed steps" "PREPR_SKIP_CODE: diff mutants, no-copies"
 else
-if [ -z "${MUTANT_CMD:-}" ]; then
-  say skip "diff mutants" "MUTANT_CMD unset -- set it to the group's self-test or features_block.py call to mutate the diff's added lines (report only)"
-elif [ ! -f tools/audit/seat/mutant_run.py ]; then
-  say skip "diff mutants" "tools/audit/seat/mutant_run.py is not in this tree"
-else
-  take_slot
-  MUT_OUT=$(python3 -I tools/audit/seat/mutant_run.py --diff "$BASE...HEAD" --cmd "$MUTANT_CMD" \
-    --max-mutants "${MUTANT_MAX:-40}" --report-only 2>&1)
-  MUT_N=$(printf '%s\n' "$MUT_OUT" | grep -c '^SURVIVED ')
-  if [ "$MUT_N" -gt 0 ]; then
-    printf '%s\n' "$MUT_OUT" | grep '^SURVIVED ' | sed 's/^/           /' >&2
-    say WARN "diff mutants" "$MUT_N survivor(s) on the diff's added lines -- the body answers each (report only)"
-  else
-    say ok "diff mutants" "no survivor: $(printf '%s\n' "$MUT_OUT" | tail -1 | cut -c1-120)"
-  fi
-fi
+[ -n "${MUTANT_CMD:-}" ] && take_slot
+MUT_OUT=$(mutants_line "$PWD" "$BASE" "${MUTANT_CMD:-}")
+case $? in
+  3) say skip "diff mutants" "$MUT_OUT" ;;
+  0) step "diff mutants" 0 "$MUT_OUT" ;;
+  2) grep '^SURVIVED ' <<<"$MUT_OUT" | sed 's/^/           /' >&2
+     say WARN "diff mutants" "$(tail -1 <<<"$MUT_OUT")" ;;
+  *) step "diff mutants" 1 "$MUT_OUT" ;;
+esac
 
 # --- 6c. a test must import the production symbol: tests.yml's `no-copies`,
 # before the push. `copies_line` above. The scan reads the whole tree, so it

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
