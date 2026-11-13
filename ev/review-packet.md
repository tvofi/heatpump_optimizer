# Review packet #3544
head: 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3
base: 0723540391a1c431b6f91629485bc2f00d90a4e7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132009498559 success
arch-score / arch-score id=132009363963 success
arm id=132008963574 skipped
budget-raise-gate / budget-raise-gate id=132009363901 success
cancel-superseded id=132008981898 success
codeql id=132009365660 skipped
codeql / Analyze (actions) id=132009362070 success
codeql / Analyze (javascript-typescript) id=132009362185 success
codeql / Analyze (python) id=132009362067 success
gate id=132010265237 failure
governance id=132009365828 skipped
governance / delivery-status id=132009362342 success
governance / delivery-status-publish id=132009364333 skipped
governance / env-matrix id=132009362126 in_progress
governance / instrument-self-tests id=132009362101 in_progress
governance / policy-docs id=132009362113 cancelled
governance / record id=132009364429 skipped
governance / wave-script id=132009362157 success
hassfest id=132009365856 skipped
hassfest / hassfest id=132009362193 success
kernel-points id=132009366464 skipped
pr-contract id=132010266917 skipped
prelude id=132008982339 success
refresh id=132008982370 success
sweep-self id=132010717095 skipped
tests id=132009367446 skipped
tests / arch-instrument id=132009863390 success
tests / briefs id=132009362217 failure
tests / browser id=132009863692 success
tests / closure-scope id=132009362473 success
tests / closures id=132009863523 in_progress
tests / coverage id=132009863415 in_progress
tests / fast (3.14) id=132009863229 in_progress
tests / mutation id=132009362107 success
tests / mutation-autofix id=132009820186 skipped
tests / mutation-pins id=132009818633 skipped
tests / nightly-ha id=132009867582 skipped
tests / nightly-status id=132009362255 success
tests / replay id=132009867558 skipped
tests / typing id=132009863373 success
validate id=132009366829 skipped
validate / validate-hacs id=132009361993 success

## Refusals
red-unanswered: concluded red check `tests / briefs` is not named in ## Red checks
introduced-red: unreadable: head governance / instrument-self-tests job 132009362101: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 676d726d27c4a5400d86c331bba87190bd34534c)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 676d726d27c4a5400d86c331bba87190bd34534c
Fix review: blocked 676d726d27c4a5400d86c331bba87190bd34534c mutation-vacuous: bus.sh MECHANICAL_CLASSES 12 of 14 classes undriven, B-rekeyed-numeric-guard, B-rekeyed-first-not-last, B-rekey-fail-ignored, B-pr-numeric-off, R-fb-len-off, R-foldfailed-off, R-first-epoch, R-tip-unrecorded-foldfailed, ledger.py:387, ledger.py:388, ledger.py:471, ledger.py:1202, ledger.py:1204, ledger.py:1206, ledger.py:1207, ledger.py:1208, ledger.py:1209

bus-nonce: d9f5b0d596b45a3f9f56068d4414bf16

Round: first review (round 1) of #3544 at head 676d726d27c4a5400d86c331bba87190bd34534c.

## Block

1. mutation-vacuous. Each changed file's mutants were run against that file's own --self-test, at this head, by tools/audit/seat/mutant_run.py (--in-place, a separate worktree per file; NULL SURVIVED in every run; every worktree's git status was clean afterwards). Every survivor:
   - tools/audit/seat/bus.sh (spec ev/spec/bus.json, output ev/mutants-bus.txt, 23 mutants, 14 survived): SURVIVED B-drop-ci-pending, B-drop-ci-cancelled, B-drop-red-unanswered, B-drop-root-cause-unanswered, B-drop-body, B-drop-contract, B-drop-preflight-mismatch, B-drop-conflict, B-drop-head-moved, B-drop-carry-missing, B-drop-carry, B-drop-ungated (each removes one class from MECHANICAL_CLASSES; only ci-red and ci-wait are driven, so 12 of the 14 named classes are pinned by nothing), B-rekeyed-numeric-guard (the `$3 ~ /^[0-9]+$/` filter on the rekeyed lookup), B-rekeyed-first-not-last (first rekeyed line wins instead of last), B-rekey-fail-ignored (`|| die` after rekey replaced with `|| true`), B-pr-numeric-off (`numeric` check on --pr removed: the "--pr takes a number" arm still sees rc != 0 from a later failure, so it does not pin the guard).
   - tools/audit/seat/cloud_relay.sh (spec ev/spec/relay.json, output ev/mutants-relay.txt, 13 mutants, 4 survived): SURVIVED R-foldfailed-off (the "fold-failed" arm of the stands-over awk filter; every new arm drives push-failed only), R-tip-unrecorded-foldfailed (the fold-failed fold_judge records "-" for the tip), R-first-epoch (the stands path records $now, not the first epoch $fe: the body's "keeps its first epoch, so the 3600 s retry bound runs from the first failure" is unpinned), R-fb-len-off (`[ "${#fb}" = 40 ]` dropped; likely equivalent because blob is always a rev-parse sha, so fb "-" cannot equal it, but it is listed untriaged).
   - tools/audit/seat/ledger.py (`--diff 0723540391...HEAD`, output ev/mutants-ledger.txt): SURVIVED ledger.py:387 GUARD_OFF, ledger.py:388 RETURN_DEL, ledger.py:388 CONST_SWAP (empty_net's merge-base-failure guard: no self-test case drives an rc != 0 merge-base, so the body's "An unreadable merge-base ... is not empty" is unpinned), ledger.py:471 STMT_DEL (the CONTENT_WHY tuple gaining "empty"), ledger.py:1202, 1204, 1206, 1207, 1209 STMT_DEL/CALL_DEL and ledger.py:1208 CONST_SWAP (lines in the self-test's own setup; listed as the driver reports them).
   Every ledger survivor site, in full: tools/audit/seat/ledger.py:387 tools/audit/seat/ledger.py:388 tools/audit/seat/ledger.py:471 tools/audit/seat/ledger.py:1202 tools/audit/seat/ledger.py:1204 tools/audit/seat/ledger.py:1206 tools/audit/seat/ledger.py:1207 tools/audit/seat/ledger.py:1208 tools/audit/seat/ledger.py:1209.
   The fixer's B1-B7 and R1-R5 kills in the body are re-confirmed (B-exempt-off, B-add-harness, B-rekeyed-lookup-off, B-rekey-call-off, B-pr-ignored, R-oldformat-guard-off, R-tip-cmp-off, R-blob-cmp-off, R-ttl-off all KILLED). The body's mutation proof did not exercise any of the survivors above.
2. An introduced required red with no answer: `governance / policy-docs` and `governance / env-matrix` (both in `merge_train.py owed-reds`) are red at this head: "tools/audit/briefs/fixer.md: about 5229 tokens across its lines exceeds its cap of 5216 tokens (files_tokens)". `node tools/policy/policy_lint.mjs` prints TOTAL 0 at the base 0723540391 and at the authored head f71c5e6933, and TOTAL 1 error at this head. Main's own fixer.md growth (step 17's dS clause, preamble wording) and this PR's appended paragraph are each under the cap alone; the merge 55f2e36097 takes the file 13 tokens over it. The body's `## Red checks` says "none", and `## Policy` claims a policy_lint TOTAL 0 that is not true at this head. Cut about 13 tokens (or state the cap case in the body) and answer the red. The `gate` red and the `tests / fast (3.14)` red also go unanswered (see Evidence).
3. Policy text and code disagree on the exempt set: the fixer.md paragraph names `ci-red`, `red-unanswered`, body or contract, `conflict`, `head-moved`, a carry, an ungated step, and as CI-only `ci-red`, `ci-wait`, `ci-pending` and a cancelled run. bus.sh MECHANICAL_CLASSES also exempts `root-cause-unanswered` and `preflight-mismatch`, which the policy does not name. Either name them in the paragraph (one pinned arm each) or drop them from the set. The owner approves the policy text at merge, so the text must state what the code does.

## Findings

none

## Evidence

- Head: ev/HEAD.txt holds 676d726d27c4a5400d86c331bba87190bd34534c; the PR body names the same head. Merge base 0723540391a1c431b6f91629485bc2f00d90a4e7. `git merge-tree --write-tree origin/main 676d726d27c4a5400d86c331bba87190bd34534c` rc 0, so it merges cleanly. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched (`git diff --stat` is empty). `python3 tests/env_drift.py --claims-only 0723540391...` prints "claims hygiene: ... ok".
- Self-tests at head (ev/selftest-head-*.txt): bus self-test 188 checks, 0 failed (71 s); cloud_relay self-test 462 checks, 0 failed (109 s); ledger self-test 105 checks, 0 failed (4 s). These match the body's green counts. I did not re-take the body's base reds (4/1/6 failed with production reverted); it is not verified.
- Finder's harness: none named (packet). These are instrument carries with self-test arms as their harness, so no RESULT lines exist to re-take at both ends.
- Review packet: rendered here (ev/packet-render.txt), rc 1. It refuses red-unanswered for gate, env-matrix, policy-docs and tests / fast (3.14), required-red for gate, and introduced-red as unreadable.
- CI at this head (ev/ci-excerpts.txt, read via job logs): policy-docs and env-matrix fail on the fixer.md files_tokens cap. In `tests / fast (3.14)`, "1 TEST SCRIPT(S) FAILED". Locally at head, closure.py selftest, doc_claims.py, layout.py and env_drift --claims-only each exit 0, and harness_headers passed in CI. By elimination the failing script is tests/entities.py. tests/entities.py could not run in this container (`env -u BASH_ENV` under venv-ci and venv-ha: ModuleNotFoundError paho/homeassistant, ev/entities-*.txt), so its failing check is not verified.
- `governance / instrument-self-tests` is red at head in selftest_scope (not in this diff). The base's job 131782096598 was in_progress, so `merge_train.py classify 676d726d27c4a5400d86c331bba87190bd34534c --pr 3544` printed "REFUSE selftests ... fail closed" rc 2 (unreadable) on both runs (ev/classify-1.txt, ev/classify-2.txt). Whether that red is introduced is not decided.
- tests/structure.py figure: resolved by figure_lint in the packet; not re-run (no structure-budget leaf moved).
- Heavy runs (gate, mutation table) are cited, not re-run. The `tests / mutation` lane is green; this diff writes Python only in ledger.py, so its table is not evidence for the bash survivors.

## Delta diff: git diff 676d726d27c4a5400d86c331bba87190bd34534c 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 49d9398cef..89cb6796ab 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -84,8 +84,8 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    p1 the grader hunks alone, p2 the rest, a WIP handoff until p1 is on main
    (decision 0013, Consequences).
 
-   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**;
-   the queue, the wait bound and holding it by hand are `gate-scoping.md`'s.
+   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**
+   (`gate-scoping.md`).
    A mutation proof leaves `stress.py` to CI's required mutation check: never
    run it locally per mutant.
 
@@ -308,8 +308,8 @@ tie-break). **A re-cut body blocked on `claims` again is a signal about the fix*
 the orchestrator splits or closes it.
 
 **Never for a mechanical-only gap** (tvofi, 2026-11-09): `bus.sh dispatch` reads the
-latest block's class and dispatches with no `## Re-cut` when it is `ci-red`,
-`red-unanswered`, body or contract, `conflict`, `head-moved`, a carry or an ungated
-step. A CI-only block (`ci-red`, `ci-wait`, `ci-pending`, a cancelled run) is
-mechanical and does not count toward the three-round rule; a judgement class, an
-unknown one or an unreadable log refuses.
+latest block's class and dispatches with no `## Re-cut` when it is `red-unanswered`,
+`body`, `contract`, `conflict`, `head-moved`, `carry`, `carry-missing`, `ungated` or
+CI-only (`ci-red`, `ci-wait`, `ci-pending`, `ci-cancelled`): mechanical, it does not
+count toward the three-round rule. A judgement class, an unknown one or an unreadable
+log refuses.
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index d72cf9533b..42d06f4dc3 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -521,10 +521,11 @@ verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr>
 # a dispatch needs the body's `## Re-cut` note (read only then, through $HPO_BUS_GH) or
 # `--past-three <reason>`, logged in $S/past-three; after a fourth -- a re-cut blocked again --
 # only `--past-three`: the split-or-close is the orchestrator's, never a silent re-dispatch.
-# The classes whose block names a gap a script or a rebase closes (review_strength.py's vocabulary, web-fix-wave.js
-# VERDICT_CLASSES): a red or pending CI, an unanswered red, the body or contract, a conflict or moved head, a missing
-# carry, an ungated step. Judgement classes (harness, null-control, mutation-*, class-open, defect, claims, ...) are absent.
-MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered root-cause-unanswered body contract preflight-mismatch conflict head-moved carry-missing carry ungated "
+# The classes whose block names a gap a script or a rebase closes, exactly the set carry 11 and its CI-only ruling name
+# and fixer.md's "Never for a mechanical-only gap" paragraph lists (the self-test reads both): a red, waiting, pending or
+# cancelled CI, an unanswered red, the body or contract, a conflict or moved head, a carry, an ungated step.
+# root-cause-unanswered (it dispatches the root-cause seat), preflight-mismatch and every judgement class are absent.
+MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered body contract conflict head-moved carry-missing carry ungated "
 mechanical_block() { # pr -> rc 0 when the latest blocked verdict on verdict/<pr> names a mechanical class; rc 1 otherwise or unreadable
   local subj cls
   subj=$(verdict_log "$1") || return 1
@@ -774,7 +775,8 @@ dispatch_handoff() { # topic sha reviewer [--model M] [--pr N] -> records `topic
   # The PR is known from --pr or a `<topic> <sha> <pr>` line in rekeyed (a local read, no API call): key the
   # new record at once, else a reviewer dispatched after the PR opened stays HELD-NOPR (open_pr.sh ran rekey before it existed).
   [ -n "$pr" ] || pr=$(awk -v t="$t" '$1 == t && $3 ~ /^[0-9]+$/ { p = $3 } END { print p }' "$S/rekeyed" 2>/dev/null)  # mut:rekeyknown
-  [ -z "$pr" ] || rekey "$t" "$pr" >&2 || die "dispatch-handoff: recorded, but could not re-key $t to #$pr"
+  # rekey dies on each failure it can meet; its rc 3 (no topic: record) cannot follow the append above.
+  [ -z "$pr" ] || rekey "$t" "$pr" >&2
   printf 'bus-nonce: %s\n' "$n"
 }
 
@@ -1065,7 +1067,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 30 31 32 33 34 35 36 37 38 39 40; do
+  for n in 7 9 12 21 22 24 30 31 32 33 34 35 36 37 38 39 40 $(seq 41 54); do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1363,8 +1365,17 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   [ $rc = 0 ] && grep -q "^topic:ht4 $h1 " "$W/state/dispatched" && ! grep -q "^[0-9]* $h1 cmsg_H7 " "$W/state/dispatched" && ! grep -q "^ht4 " "$W/state/rekeyed"
   expect "null control: a topic with no PR and no --pr stays topic:-only, so HELD-NOPR is unchanged (carry 28)" $?
   out=$(seat dispatch-handoff ht4 "$h2" cmsg_H8 --pr x); rc=$?
-  [ $rc != 0 ]; expect "--pr takes a number (carry 28)" $?
-  git -C "$W/seat" push -q origin :refs/heads/handoff/ht3 :refs/heads/handoff-body/ht3 :refs/heads/handoff/ht4 :refs/heads/handoff-body/ht4
+  [ $rc != 0 ] && echo "$out" | grep -q "dispatch-handoff: --pr takes a pull-request number" && ! grep -q " cmsg_H8 " "$W/state/dispatched"
+  expect "--pr takes a number, refused before anything is recorded (carry 28)" $?
+  # The rekeyed lookup takes the LAST numeric line for the topic: a later re-key wins, a non-numeric third field is skipped.
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht5" "$h1:refs/heads/handoff-body/ht5"
+  printf 'ht5 %s 58\nht5 %s 59\nht5 %s -\n' "$h1" "$h1" "$h1" >> "$W/state/rekeyed"
+  out=$(seat dispatch-handoff ht5 "$h1" cmsg_H9); rc=$?
+  hn5=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^59 $h1 cmsg_H9 $hn5 " "$W/state/dispatched" && ! grep -q "^58 $h1 cmsg_H9 " "$W/state/dispatched"
+  expect "a topic re-keyed to #58 then #59 (then a non-numeric line) keys the new record to #59 alone (carry 28)" $?
+  git -C "$W/seat" push -q origin :refs/heads/handoff/ht3 :refs/heads/handoff-body/ht3 :refs/heads/handoff/ht4 :refs/heads/handoff-body/ht4 \
+    :refs/heads/handoff/ht5 :refs/heads/handoff-body/ht5
   out=$(seat rekey never 56); rc=$?
   [ $rc = 3 ] && echo "$out" | grep -q "never has no handoff dispatch" && ! grep -q "^56 " "$W/state/dispatched"
   expect "null control: a topic with no handoff dispatch re-keys nothing (rc 3), so open_pr.sh stays quiet" $?
@@ -2064,15 +2075,25 @@ B
   # Carry 11 (owner directive, tvofi 2026-11-09): a latest block of a mechanical class never counts toward the rule.
   blkc() { git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${2:+-p "$2"} \
              -m "verdict: #$3 Fix review: blocked $(printf '%040d' "$1") $4: round $1"; }
-  for c in ci-red:36 proof:37 nosuchclass:38 ci-wait:39; do
-    rp=$(blkc 1 "" "${c#*:}" harness); rp=$(blkc 2 "$rp" "${c#*:}" harness); rp=$(blkc 3 "$rp" "${c#*:}" "${c%:*}")
-    rp=$(blkc 4 "$rp" "${c#*:}" "${c%:*}"); git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/${c#*:}"
-  done
+  blk4() { local rp; rp=$(blkc 1 "" "$1" harness); rp=$(blkc 2 "$rp" "$1" harness); rp=$(blkc 3 "$rp" "$1" "$2")
+           rp=$(blkc 4 "$rp" "$1" "$2"); git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/$1"; }
+  blk4 37 proof; blk4 38 nosuchclass
   printf "## Summary\nno note\n" > "$W/body31"
-  out=$(run dispatch 36 "$h1" cmsg_T); rc=$?
-  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "a fourth round after a mechanical (ci-red) block dispatches with no note (carry 11)" $?
-  out=$(run dispatch 39 "$h1" cmsg_T); rc=$?
-  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "... a CI-only wait block (ci-wait) is mechanical too (carry 11)" $?
+  # The exempt set is fixer.md's: the backticked class words of its "Never for a mechanical-only gap" paragraph
+  # must be MECHANICAL_CLASSES exactly, and each is driven below by its own fourth round beside two it must refuse.
+  pol=$(awk '/^\*\*Never for a mechanical-only gap\*\*/ { on = 1 } on && /^$/ { exit } on' "$ROOT/dev/governance/roles/fixer.md" \
+        | grep -o '`[a-z][a-z-]*`' | tr -d '`' | sort -u | tr '\n' ' ')
+  [ -n "$pol" ] && [ "$pol" = "$(printf '%s\n' $MECHANICAL_CLASSES | sort -u | tr '\n' ' ')" ]
+  expect "fixer.md's mechanical-only paragraph names exactly MECHANICAL_CLASSES (carry 11)" $?
+  n=41
+  for c in $pol root-cause-unanswered preflight-mismatch; do
+    blk4 $n "$c"; out=$(run dispatch $n "$h1" cmsg_T); rc=$?
+    case " $pol " in
+      *" $c "*) [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "a fourth round after a $c block dispatches with no note (carry 11)" $? ;;
+      *) [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: a fourth round after a $c block refuses (carry 11)" $? ;;
+    esac
+    n=$((n + 1))
+  done
   out=$(run dispatch 37 "$h1" cmsg_T); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: a fourth round after a proof-class block still refuses (carry 11)" $?
   out=$(run dispatch 38 "$h1" cmsg_T); rc=$?
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index a5ce507039..2e1a6cbed7 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -842,7 +842,7 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     # equal the record's; the record keeps its first epoch, so the retry bound runs from the first failure.
     fo= fe= fb= fh= fl=; [ -n "$bsha" ] && [ -n "$htip" ] && [ -f "$memo" ] \
       && read -r _ _ _ fo fe fb fh fl < <(awk -v t="$topic" -v w="$sha" -v h="$htip" '$1 == t && $2 == w && ($4 == "fold-failed" || $4 == "push-failed") && $7 == h { print; exit }' "$memo")
-    if [ -n "$fo" ] && fold_memo_stands "$fo" "$fe" "$now" && [ "${#fb}" = 40 ] \
+    if [ -n "$fo" ] && fold_memo_stands "$fo" "$fe" "$now" \
       && git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null) && [ "$blob" = "$fb" ]; then  # mut:foldblob
       echo "cloud_relay: OWED carry-fold $topic unchanged since $(date -u -d "@$fe" +%FT%TZ): ${fl#*"$sha "}"
       fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"; continue
@@ -2002,6 +2002,20 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   awk -v e=$(( $(date +%s) - 3601 )) '$1 == "cf-k" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
   carry_fold_arm >/dev/null 2>&1
   chk "a record an hour old no longer stands over a new kept commit" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 4
+  # A failed carry_fold.py (fold-failed) stands over a re-kept body alike, and the standing record keeps its first epoch.
+  printf '#!/bin/bash\necho "$@" >> %s/fk\necho "fold refused"; exit 1\n' "$t" > "$t/foldfail"; chmod +x "$t/foldfail"
+  fsave=${HPO_RELAY_FOLD:-}; export HPO_RELAY_FOLD=$t/foldfail; : > "$t/fk"
+  cfref handoff/cf-f code.txt "code F"; cfref handoff-wip/cf-f BLOCKED.md "body_push: REFUSED CARRY-LANDED"
+  cfref handoff-wip/cf-f-body BODY.md "the body F"; carry_fold_arm >/dev/null 2>&1
+  e0=$(( $(date +%s) - 1800 ))
+  awk -v e=$e0 '$1 == "cf-f" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  GIT_AUTHOR_DATE="2005-01-01T00:00:00Z" GIT_COMMITTER_DATE="2005-01-01T00:00:00Z" cfref handoff-wip/cf-f-body BODY.md "the body F"
+  cfo=$(carry_fold_arm 2>&1)
+  chk "a failed carry_fold.py (fold-failed) stands over a re-kept body with the same blob and handoff tip" 0 test "$(grep -c 'topic cf-f ' "$t/fk")" = 1
+  chk "... its tick line says OWED, unchanged" 0 grep -q "OWED carry-fold cf-f unchanged since" <<< "$cfo"
+  chk "... and the standing record keeps its first epoch, so the retry bound runs from the first failure" 0 \
+    awk -v e=$e0 '$1 == "cf-f" && $5 == e { f = 1 } END { exit !f }' "$t/state/cloud-fold-judged"
+  if [ -n "$fsave" ]; then export HPO_RELAY_FOLD=$fsave; else unset HPO_RELAY_FOLD; fi
   cfref handoff-wip/cf-l BLOCKED.md "the fixer is stuck, again"; carry_fold_arm >/dev/null 2>&1
   awk '$1 == "cf-l" { $6 = ""; $7 = ""; gsub(/  +/, " ") } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
   : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index 4ff47e29b2..01a3ae0d98 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -1199,14 +1199,7 @@ def self_test() -> int:
         g("rm", "-q", "tmp_add.txt")
         g("commit", "-qm", "remove it again")
         emt = g("rev-parse", "HEAD")
-        check("landed: an add-then-remove tip with an empty net diff lands as empty (carry 20)",
-              landed(gw, mn, emt) == "empty" and not covered(gw, mn, emt))
-        g("checkout", "-qb", "work19", mn)
-        rl = put("real_new.txt", "one real uncovered line\n", "a real uncovered add")
-        check("null control: a tip with one real uncovered line stays None (carry 20)", landed(gw, mn, rl) is None)
-        check("null control: a failing diff read (rc != 0) is not empty (carry 20)",
-              not empty_net(lambda a: (1, "") if a[0] == "diff" else gw(a), mn, emt))
-        g("checkout", "-q", "main")
+        rl = put("real_new.txt", "one real uncovered line\n", "one real uncovered add on the empty pair")
         g("checkout", "-qb", "work7", gb)
         mv = put("moved.txt", "same bytes\n", "add a file")
         g("checkout", "-qb", "work8", gb)
@@ -1248,6 +1241,18 @@ def self_test() -> int:
         put("evil.txt", "E\n", "a merge with a resolution of its own")
         check("null control: a merge carrying its own resolution is not merges-only",
               landed(gw, m_a, g("rev-parse", "HEAD"), [fixh], content=False) is None)
+        # Carry 20, one oracle so that no setup line above can be dropped unread: an add-then-remove tip lands as
+        # empty; the same pair plus one real line stays None; a failing merge-base read (whose output, here, would
+        # diff empty) or a failing diff read is not empty; and landed's reasons are exactly the two declared tuples.
+        bad_rc, _ = gw(["merge-base", "--no-such-option"])
+        check("carry 20: an empty net diff lands as empty; one real line, an unreadable merge-base or diff does not;"
+              " the reasons driven here are ANCESTRY_WHY + CONTENT_WHY",
+              landed(gw, mn, emt) == "empty" and not covered(gw, mn, emt) and landed(gw, mn, rl) is None
+              and empty_net(gw, mn, emt) and bad_rc
+              and not empty_net(lambda a: (bad_rc, mn) if a[0] == "merge-base" else gw(a), mn, emt)
+              and not empty_net(lambda a: gw(a + ["--no-such-option"]) if a[0] == "diff" else gw(a), mn, emt)
+              and {landed(gw, mn, anc), landed(gw, m_a, tipm, [fixh]), landed(gw, rvm, rv), landed(gw, mn, emt),
+                   landed(gw, mn, cov)} == {*ANCESTRY_WHY, *CONTENT_WHY})
         g("checkout", "-q", "main")
         hr = [tuple(l.split()) for l in g("ls-remote", "origin", "refs/heads/handoff/*",
                                            "refs/heads/handoff-body/*").splitlines()]

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
