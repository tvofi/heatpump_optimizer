# Review packet #3544
head: 676d726d27c4a5400d86c331bba87190bd34534c
base: 0723540391a1c431b6f91629485bc2f00d90a4e7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131785853216 success
arch-score / arch-score id=131785833889 success
arm id=131785505772 skipped
budget-raise-gate / budget-raise-gate id=131785833995 success
cancel-superseded id=131785510632 success
codeql id=131785835674 skipped
codeql / Analyze (actions) id=131785774703 success
codeql / Analyze (javascript-typescript) id=131785774754 success
codeql / Analyze (python) id=131785774770 success
gate id=131786377265 failure
governance id=131785835988 skipped
governance / delivery-status id=131785775165 success
governance / delivery-status-publish id=131785777829 skipped
governance / env-matrix id=131785775213 failure
governance / instrument-self-tests id=131785774796 failure
governance / policy-docs id=131785774647 failure
governance / record id=131785777120 skipped
governance / wave-script id=131785774992 success
hassfest id=131785835745 skipped
hassfest / hassfest id=131785774938 success
kernel-points id=131785837000 skipped
pr-contract id=131786378198 skipped
prelude id=131785510295 success
refresh id=131785510584 success
sweep-self id=131786683117 skipped
tests id=131785836808 skipped
tests / arch-instrument id=131786078616 success
tests / briefs id=131785775278 success
tests / browser id=131786078539 success
tests / claims-autofix id=131791587466 success
tests / closure-scope id=131785775439 success
tests / closures id=131786078658 in_progress
tests / coverage id=131786078627 in_progress
tests / fast (3.14) id=131786078626 failure
tests / mutation id=131785775530 success
tests / mutation-autofix id=131786194697 skipped
tests / mutation-pins id=131786194022 skipped
tests / nightly-ha id=131786080888 skipped
tests / nightly-status id=131785775379 failure
tests / replay id=131786081006 skipped
tests / typing id=131786078618 success
validate id=131785835617 skipped
validate / validate-hacs id=131785775076 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `governance / env-matrix` is not named in ## Red checks
red-unanswered: concluded red check `governance / policy-docs` is not named in ## Red checks
red-unanswered: concluded red check `tests / fast (3.14)` is not named in ## Red checks
required-red: required context `gate` concluded failure at 676d726d27c4a5400d86c331bba87190bd34534c (merge_train.py classify --pr reads RED classify unreadable (rc 2): REFUSE selftests: the base's governance / instrument-self-tests job 131782096598 is in_progress, which reads no step: an introduced red cannot be ruled out (fail closed))
introduced-red: unreadable: the base's governance / instrument-self-tests job 131782096598 is in_progress, which reads no step: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/governance/roles/fixer.md b/dev/governance/roles/fixer.md
index 64f01557a8..49d9398cef 100644
--- a/dev/governance/roles/fixer.md
+++ b/dev/governance/roles/fixer.md
@@ -23,7 +23,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
    size named in the body; a spelling the reviewer finds is added to it.
    A `git archive` copy fails the #363 `recorded_at` check, and a self-test
-   needing a checkout, on every mutant, baseline included (#1713, #1723).
+   needing a checkout, on every mutant, baseline included.
    **The diff's survivors are yours before the handoff; `--pin-killed` is
    `ci-autofix.md`'s.** Set `prepr.sh`'s `MUTANT_CMD` to the group's self-test
    or a `features_block.py` call (`MUTANT_IN_PLACE=1` for a checkout); it draws only
@@ -41,8 +41,8 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    reports unverified, not refused. A harness measuring what the fix rightly
    leaves alone reads flat at both ends: say so, and add a sha1-cited companion
    applying the tree's own rule to the same inputs, reading the defect at the
-   baseline and not at the head (#1506, #1561, #1571). A fold deleting a name
-   the harness drives leaves only its count arm readable at the head;
+   baseline and not at the head. A fold deleting a name the harness drives
+   leaves only its count arm readable at the head;
    the fixer ports the rest, as its own (`fix-review.md` step 9; #2365).
    **Every quantified claim carries a null control, not only cost, gain and
    time**: a count, a percentage, an "every" or a "none" is a measurement, owed
@@ -116,8 +116,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
    (a `--carry` head: no re-take; name bot reds), and carries every executed
    number in `## Figures` with its command.
 8. **A quoted number states the rule that produced it, not just its value.**
-   Only a count whose rule is written down is re-derivable (#373: one census,
-   three counts). **Name the instrument you re-ran, and its scope.** If the
+   Only a count whose rule is written down is re-derivable. **Name the instrument you re-ran, and its scope.** If the
    block you are clearing was demonstrated with an *instance*, your verification
    may not be a search for that instance — it must check the property the
    phenomenon states, not the property the block's text states: name a rule that enumerates the class's seams (a command,
@@ -139,12 +138,11 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
 9. **A claim should be true; if wrong, correct it — anchored to a lane,
    function, marker or SHA, never a bare line number — and delete only when
    no such correction exists.** Delete on sight, not as a last resort, when
-   the claim is only motivation or scaffolding the finished text doesn't
-   need (#386).
+   the claim is only motivation or scaffolding the finished text doesn't need.
 10. **If the wrong text is generated, fix the generator first, and run it.**
     Correcting prose a script emits leaves the script emitting the old text on
-    its next run, so the correction is undone rather than kept (#539). Grep for
-    the wrong form across the whole tree before deciding what to edit.
+    its next run, so the correction is undone rather than kept. Grep for the
+    wrong form across the whole tree before deciding what to edit.
     **A generator fixed without being run is a claim, not a fix**: run it,
     paste what it now emits, and run it at the merge base as the control.
     Text that *instructs* differs from a record that *recounts*: a measurement
@@ -196,8 +194,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     `np.sum(matrix, axis=1)` is not `np.sum(matrix[b])`, and neither is a
     reduction over a row VIEW of a batched array one over the fresh array the
     scalar expression builds: numpy's pairwise loop takes alignment and stride
-    as inputs, per backend (#948: arm64 parity, x86_64 drift, at the 96-step
-    production width only). Where the contract is bitwise, run the SCALAR
+    as inputs, per backend. Where the contract is bitwise, run the SCALAR
     EXPRESSION per row, on the fresh per-row arrays that expression's own
     elementwise ops allocate — batch only what is elementwise end to end — and
     drive the parity grid at the production width.
@@ -205,11 +202,9 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     The same rule holds one level up and across interpreter versions: a
     reduction whose scalar form is a PYTHON BUILTIN is compensated arithmetic
     on CPython 3.12+ — builtin `sum` is Neumaier — and no vectorized
-    accumulation reproduces it (#948: 1-2 ulp, red on CI's 3.14 runner, green
-    on 3.11, whose `sum` is plain). Make the twin call the scalar closure's own
+    accumulation reproduces it. Make the twin call the scalar closure's own
     function per row, and put detector rows on the parity grid that separate
-    the two summations (measured: ~12% of random three-term sums), so the
-    interpreter class that diverges — CI's — runs the detector.
+    the two summations, so the interpreter class that diverges — CI's — runs the detector.
 
     A per-row twin removes re-entry, not work; when it is the fix for a
     recomputation finding, re-measure the finding's cost on the fixed tree and
@@ -250,9 +245,7 @@ fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L,
     improvement claim names its mechanism, which the reviewer removes as the
     null control (`fix-review.md` step 14). Never move a metric by a change
     that does not improve the code: a mechanical split, code moved to an
-    unmeasured path, a triage on a killable mutant, or cases enumerated where a
-    structural fix exists (#1874, #2345: a spelling list, three review rounds,
-    class still open).
+    unmeasured path, a triage on a killable mutant, or cases enumerated where a structural fix exists.
 18. **What a later round or seat reruns, or a body figure needs reproduced,
     lands in the same pull request** (tvofi, 2026-10-03): a harness in
     `dev/audit/harnesses/`, a driver or env recipe in `tools/audit/seat/`,
@@ -313,3 +306,10 @@ requires, the arms that fire, and only figures re-taken in that pass. Round
 history is deleted, not restated — except a **disclosed self-correction** (`dev/programme/HANDOVER.md`'s #1058
 tie-break). **A re-cut body blocked on `claims` again is a signal about the fix**:
 the orchestrator splits or closes it.
+
+**Never for a mechanical-only gap** (tvofi, 2026-11-09): `bus.sh dispatch` reads the
+latest block's class and dispatches with no `## Re-cut` when it is `ci-red`,
+`red-unanswered`, body or contract, `conflict`, `head-moved`, a carry or an ungated
+step. A CI-only block (`ci-red`, `ci-wait`, `ci-pending`, a cancelled run) is
+mechanical and does not count toward the three-round rule; a judgement class, an
+unknown one or an unreadable log refuses.
diff --git a/dev/programme/delivery/3544.md b/dev/programme/delivery/3544.md
new file mode 100644
index 0000000000..e8df5be62b
--- /dev/null
+++ b/dev/programme/delivery/3544.md
@@ -0,0 +1 @@
+- [#3544](https://github.com/tvofi/heatpump_optimizer/pull/3544) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 5): r10 review dispatch residue p5 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 2739429f15..d72cf9533b 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -521,10 +521,24 @@ verdict_at() { # pr sha -> the latest verdict word naming <sha> on verdict/<pr>
 # a dispatch needs the body's `## Re-cut` note (read only then, through $HPO_BUS_GH) or
 # `--past-three <reason>`, logged in $S/past-three; after a fourth -- a re-cut blocked again --
 # only `--past-three`: the split-or-close is the orchestrator's, never a silent re-dispatch.
+# The classes whose block names a gap a script or a rebase closes (review_strength.py's vocabulary, web-fix-wave.js
+# VERDICT_CLASSES): a red or pending CI, an unanswered red, the body or contract, a conflict or moved head, a missing
+# carry, an ungated step. Judgement classes (harness, null-control, mutation-*, class-open, defect, claims, ...) are absent.
+MECHANICAL_CLASSES=" ci-red ci-wait ci-pending ci-cancelled red-unanswered root-cause-unanswered body contract preflight-mismatch conflict head-moved carry-missing carry ungated "
+mechanical_block() { # pr -> rc 0 when the latest blocked verdict on verdict/<pr> names a mechanical class; rc 1 otherwise or unreadable
+  local subj cls
+  subj=$(verdict_log "$1") || return 1
+  cls=$(printf '%s\n' "$subj" | sed -n "s/^verdict: #$1 Fix review: blocked [0-9a-f]\{7,40\} \([^ :]*\):.*\$/\1/p" | head -n 1)
+  [ -n "$cls" ] && case $MECHANICAL_CLASSES in *" $cls "*) return 0;; esac
+  return 1
+}
 three_rounds() { # pr past-three-reason -> 0 to dispatch; else why
   local k body
   k=$(blocked_rounds "$1") || { printf 'cannot read verdict/%s to count its review rounds' "$1"; return 1; }
   [ "$k" -ge 3 ] && [ -z "$2" ] || return 0
+  # A latest block of a mechanical class (tvofi, 2026-11-09: "the split should never apply when the gap is
+  # mechanical only") is no round to re-cut over; a judgement class, an unknown one or an unreadable log refuses as before.
+  mechanical_block "$1" && return 0  # mut:mechclass
   [ "$k" -lt 4 ] || { printf '#%s has %s blocked rounds: its re-cut was blocked again, so split or close it (the orchestrator), or pass --past-three <reason>' "$1" "$k"; return 1; }
   body=$(${HPO_BUS_GH:-gh} api "repos/$REPO/pulls/$1" --jq .body) \
     || { printf 'cannot read #%s'"'"'s body to find its ## Re-cut note' "$1"; return 1; }
@@ -733,11 +747,12 @@ dispatch() { # pr head reviewer [--reviewed-head <sha>] [--nonce N] [--model M]
 # for handoff-head..PR-head (the merge of main and the row commit), else it reports
 # HELD-STALE and the PR is re-dispatched at its head. Nothing here reads CI, a row or a packet:
 # none exists before the PR does.
-dispatch_handoff() { # topic sha reviewer [--model M] -> records `topic:<topic> <sha> ...`, prints the nonce
-  local t=${1:-} h=${2:-} r=${3:-} m=- n tip
+dispatch_handoff() { # topic sha reviewer [--model M] [--pr N] -> records `topic:<topic> <sha> ...`, prints the nonce
+  local t=${1:-} h=${2:-} r=${3:-} m=- n tip pr=
   shift 3 2>/dev/null || shift $#
   while [ $# -gt 0 ]; do
     case $1 in
+      --pr) numeric "${2:-}" || die "dispatch-handoff: --pr takes a pull-request number"; pr=$2; shift 2 ;;
       --model) [[ ${2:-} =~ ^[A-Za-z0-9._-]+$ ]] || die "dispatch-handoff: --model takes one token"; m=$2; shift 2 ;;
       *) die "dispatch-handoff: unknown argument '$1'" ;;
     esac
@@ -756,6 +771,10 @@ dispatch_handoff() { # topic sha reviewer [--model M] -> records `topic:<topic>
   [[ $n =~ ^[0-9a-f]{32}$ ]] || die "dispatch-handoff: could not mint a nonce"
   mkdir -p "$S" && printf 'topic:%s %s %s %s %s %s\n' "$t" "$h" "$r" "$n" "$(date -u +%FT%TZ)" "$m" >> "$S/dispatched" \
     || die "dispatch-handoff: cannot record in $S"
+  # The PR is known from --pr or a `<topic> <sha> <pr>` line in rekeyed (a local read, no API call): key the
+  # new record at once, else a reviewer dispatched after the PR opened stays HELD-NOPR (open_pr.sh ran rekey before it existed).
+  [ -n "$pr" ] || pr=$(awk -v t="$t" '$1 == t && $3 ~ /^[0-9]+$/ { p = $3 } END { print p }' "$S/rekeyed" 2>/dev/null)  # mut:rekeyknown
+  [ -z "$pr" ] || rekey "$t" "$pr" >&2 || die "dispatch-handoff: recorded, but could not re-key $t to #$pr"
   printf 'bus-nonce: %s\n' "$n"
 }
 
@@ -1046,7 +1065,7 @@ self_test() {
   # 7, 9, 12, 21, 22 and 24 (21-24 are the FETCHHEAD/poster arms' pull
   # requests); h2 (a child) inherits them; norow is the base, with none.
   mkdir -p "$W/seat/$ROW_DIR"
-  for n in 7 9 12 21 22 24 30 31 32 33 34 35; do
+  for n in 7 9 12 21 22 24 30 31 32 33 34 35 36 37 38 39 40; do
     printf -- '- [#%s](https://github.com/o/r/pull/%s) — **open**\n' "$n" "$n" > "$W/seat/$ROW_DIR/$n.md"
   done
   git -C "$W/seat" -c user.name=t -c user.email=t@t add -A
@@ -1328,6 +1347,24 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   out=$(seat push-verdict 55 "$W/hmerge.md" "$W/ev1"); rc=$?
   [ $rc = 0 ]; expect "after the re-key the handoff-dispatched verdict proposes on #55 at the handoff head" $?
   git -C "$W/seat" push -q origin :refs/heads/review/55
+  # Carry 28: dispatch-handoff re-keys the new record itself whenever the PR is known (a rekeyed line, or --pr N).
+  git -C "$W/seat" push -q origin "$h2:refs/heads/handoff/ht1"
+  out=$(seat dispatch-handoff ht1 "$h2" cmsg_H5); rc=$?
+  hn2=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^55 $h2 cmsg_H5 $hn2 " "$W/state/dispatched" && grep -qx "ht1 $h2 55" "$W/state/rekeyed"
+  expect "a second dispatch-handoff for a topic already re-keyed to #55 adds a 55 record and a rekeyed line (carry 28)" $?
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht3" "$h1:refs/heads/handoff-body/ht3"
+  out=$(seat dispatch-handoff ht3 "$h1" cmsg_H6 --pr 57); rc=$?
+  hn3=$(echo "$out" | sed -n 's/^bus-nonce: //p')
+  [ $rc = 0 ] && grep -q "^57 $h1 cmsg_H6 $hn3 " "$W/state/dispatched" && grep -qx "ht3 $h1 57" "$W/state/rekeyed"
+  expect "--pr 57 keys a fresh topic at dispatch (carry 28)" $?
+  git -C "$W/seat" push -q origin "$h1:refs/heads/handoff/ht4" "$h1:refs/heads/handoff-body/ht4"
+  out=$(seat dispatch-handoff ht4 "$h1" cmsg_H7); rc=$?
+  [ $rc = 0 ] && grep -q "^topic:ht4 $h1 " "$W/state/dispatched" && ! grep -q "^[0-9]* $h1 cmsg_H7 " "$W/state/dispatched" && ! grep -q "^ht4 " "$W/state/rekeyed"
+  expect "null control: a topic with no PR and no --pr stays topic:-only, so HELD-NOPR is unchanged (carry 28)" $?
+  out=$(seat dispatch-handoff ht4 "$h2" cmsg_H8 --pr x); rc=$?
+  [ $rc != 0 ]; expect "--pr takes a number (carry 28)" $?
+  git -C "$W/seat" push -q origin :refs/heads/handoff/ht3 :refs/heads/handoff-body/ht3 :refs/heads/handoff/ht4 :refs/heads/handoff-body/ht4
   out=$(seat rekey never 56); rc=$?
   [ $rc = 3 ] && echo "$out" | grep -q "never has no handoff dispatch" && ! grep -q "^56 " "$W/state/dispatched"
   expect "null control: a topic with no handoff dispatch re-keys nothing (rc 3), so open_pr.sh stays quiet" $?
@@ -2024,6 +2061,26 @@ B
   printf "## Summary\nno note\n" > "$W/body31"
   out=$(run dispatch 35 "$h1" cmsg_T); rc=$?
   [ $rc != 0 ] && echo "$out" | grep -q "3 blocked round(s).*## Re-cut"; expect "null control: three distinct blocked heads are three rounds and refuse without a note" $?
+  # Carry 11 (owner directive, tvofi 2026-11-09): a latest block of a mechanical class never counts toward the rule.
+  blkc() { git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$h1^{tree}")" ${2:+-p "$2"} \
+             -m "verdict: #$3 Fix review: blocked $(printf '%040d' "$1") $4: round $1"; }
+  for c in ci-red:36 proof:37 nosuchclass:38 ci-wait:39; do
+    rp=$(blkc 1 "" "${c#*:}" harness); rp=$(blkc 2 "$rp" "${c#*:}" harness); rp=$(blkc 3 "$rp" "${c#*:}" "${c%:*}")
+    rp=$(blkc 4 "$rp" "${c#*:}" "${c%:*}"); git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/${c#*:}"
+  done
+  printf "## Summary\nno note\n" > "$W/body31"
+  out=$(run dispatch 36 "$h1" cmsg_T); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "a fourth round after a mechanical (ci-red) block dispatches with no note (carry 11)" $?
+  out=$(run dispatch 39 "$h1" cmsg_T); rc=$?
+  [ $rc = 0 ] && echo "$out" | grep -q '^bus-nonce: '; expect "... a CI-only wait block (ci-wait) is mechanical too (carry 11)" $?
+  out=$(run dispatch 37 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: a fourth round after a proof-class block still refuses (carry 11)" $?
+  out=$(run dispatch 38 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ] && echo "$out" | grep -q "blocked round"; expect "null control: an unknown class refuses as before (carry 11)" $?
+  rp=$(blkc 1 "" 40 ci-red); rp=$(blkc 2 "$rp" 40 ci-red); rp=$(blkc 3 "$rp" 40 ci-red); rp=$(blkc 4 "$rp" 40 harness)
+  git -C "$W/seat" push -q origin "$rp:refs/heads/verdict/40"
+  out=$(run dispatch 40 "$h1" cmsg_T); rc=$?
+  [ $rc != 0 ]; expect "only the LATEST block's class is read: mechanical rounds then a harness block refuses (carry 11)" $?
 
   # THE REVIEW PACKET: dispatch names the packet rendered at its head and passes the
   # finder's harness through; a REFUSED head records nothing; a seat that cannot render
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index c41821c16f..a5ce507039 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -805,8 +805,8 @@ noreturn_arm() {
   rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
 }
 
-fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> [<OWED level line>]: one judged topic, its level line set
-  printf '%s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "${8:+ $8}" >> "$1"; [ -z "${8:-}" ] || printf '%s\n' "$8" >> "$2"; }
+fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> <BODY.md blob|-> <handoff tip|-> [<OWED level line>]: one judged topic, its level line set
+  printf '%s %s %s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "$8" "$9" "${10:+ ${10}}" >> "$1"; [ -z "${10:-}" ] || printf '%s\n' "${10}" >> "$2"; }
 fold_memo_stands() { # <outcome> <epoch> <now>: rc 0 while a judged outcome stands; a failure after the fold expires after 3600 s
   case $1:$2 in blocked:*|folded:*) return 0;; fold-failed:[0-9]*|push-failed:[0-9]*) [ $(($3 - $2)) -lt 3600 ];; *) return 1;; esac; }  # mut:foldttl
 carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md names CARRY-LANDED alone: fold the kept body's carries, re-run body_push.sh
@@ -815,13 +815,15 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
   # by hand (4 times on 2026-11-06, twice more on 11-07). The refusal is folded only when it is the ONLY kind the
   # BLOCKED.md names and the refused body is kept on handoff-wip/<topic>-body; any other BLOCKED.md prints a tick
   # line and folds nothing. carry_fold.py is the designated roster writer; HPO_RELAY_FOLD / HPO_RELAY_BODYPUSH replace the two steps.
-  # Every judged (wip sha, body sha) is memoed in cloud-fold-judged, `<topic> <wip> <body|-> <outcome> <epoch> [<OWED line>]`
-  # (P580); a (topic, body) cloud-folded holds is skipped unmemoed. A memoed pair is neither fetched nor shown, and its
+  # Every judged (wip sha, body sha) is memoed in cloud-fold-judged, `<topic> <wip> <body|-> <outcome> <epoch> <blob|-> <handoff tip|-> [<OWED line>]`
+  # (P580); a (topic, body) cloud-folded holds is skipped unmemoed. body_push.sh keeps every refused body as a NEW parentless
+  # commit, so a failure memoed under the kept commit never hits again (r10-train-residue: four kept commits in an hour,
+  # one BODY.md blob): a failed fold or push also stands for a later kept body with the same stop, BODY.md blob and handoff tip. A memoed pair is neither fetched nor shown, and its
   # stored line is set again, because level_set replaces the whole carry-fold level. A failure after the fold is judged
   # again once fold_memo_stands expires it: an ancestry red can clear with no ref moving. The body is pushed from a
   # worktree at a private ref fetched from handoff/<topic>, deleted after the push, never FETCH_HEAD, which a concurrent
   # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556).
-  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head mb mh blob fo fe fb fh fl
   git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' > "$state/cloud-wip.$$" \
     || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
   memo=$state/cloud-fold-judged; now=$(date +%s)
@@ -830,28 +832,40 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     case $ref in refs/heads/handoff-wip/*) topic=${ref#refs/heads/handoff-wip/};; *) continue;; esac
     case $topic in ''|*/*|*-body|*-carries|*-body-*) continue;; esac
     bsha=$(awk -v r="refs/heads/handoff-wip/$topic-body" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
-    mo= me= ml=; [ -f "$memo" ] && read -r _ _ _ mo me ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
+    htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$"); blob=-
+    mo= me= ml= mb= mh=; [ -f "$memo" ] && read -r _ _ _ mo me mb mh ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
+    [ "${#mb}" = 40 ] || [ "$mb" = - ] || mo=  # a record from before the blob and tip fields is judged again
     if [ -n "$mo" ] && fold_memo_stands "$mo" "$me" "$now"; then
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$mo" "$me" "$ml"; continue  # mut:foldmemo
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$mo" "$me" "$mb" "$mh" "$ml"; continue  # mut:foldmemo
     fi
+    # A failed fold or push stands over a moved kept body when its BODY.md blob, the stop and handoff/<topic>'s tip all
+    # equal the record's; the record keeps its first epoch, so the retry bound runs from the first failure.
+    fo= fe= fb= fh= fl=; [ -n "$bsha" ] && [ -n "$htip" ] && [ -f "$memo" ] \
+      && read -r _ _ _ fo fe fb fh fl < <(awk -v t="$topic" -v w="$sha" -v h="$htip" '$1 == t && $2 == w && ($4 == "fold-failed" || $4 == "push-failed") && $7 == h { print; exit }' "$memo")
+    if [ -n "$fo" ] && fold_memo_stands "$fo" "$fe" "$now" && [ "${#fb}" = 40 ] \
+      && git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null) && [ "$blob" = "$fb" ]; then  # mut:foldblob
+      echo "cloud_relay: OWED carry-fold $topic unchanged since $(date -u -d "@$fe" +%FT%TZ): ${fl#*"$sha "}"
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$fo" "$fe" "$fb" "$fh" "$fl"; continue
+    fi
+    blob=-
     [ -f "$state/cloud-folded" ] && grep -qxF "$topic $bsha" "$state/cloud-folded" && continue
     git fetch -q origin "$ref" 2>/dev/null && bw=$(git show "$sha:BLOCKED.md" 2>/dev/null) || continue
     kinds=$(printf '%s\n' "$bw" | sed -n 's/^body_push: REFUSED \([A-Z-]*\)[[:space:]]*$/\1/p' | sort -u | tr '\n' ' ')
     if [ "$kinds" != "CARRY-LANDED " ] || [ -z "$bsha" ]; then  # mut:foldonly
       why="BLOCKED.md names ${kinds:-no refusal line}${bsha:+; }${bsha:-and no kept body}: not CARRY-LANDED alone, nothing folded"
       echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" - "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
     fi
     body=$state/cloud-fold-$topic.md
     git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && git show "$bsha:BODY.md" > "$body" 2>/dev/null \
       || { echo "cloud_relay: no BODY.md at handoff-wip/$topic-body; nothing folded" >&2; continue; }
+    blob=$(git rev-parse "$bsha:BODY.md" 2>/dev/null || echo -)
     rc=0; why=$(${HPO_RELAY_FOLD:-python3 -I "$HERE/carry_fold.py"} --body "$body" --topic "$topic" --worktree "$state/cloud-fold-wt" 2>&1) || rc=$?
     if [ $rc != 0 ]; then
       why=$(last_line "$why"); echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} carry_fold rc=$rc: $why"
-      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" fold-failed "$now" "$(level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why")"; continue
+      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" fold-failed "$now" "$blob" "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why")"; continue
     fi
     wt=$state/cloud-fold-code; rm -rf "$wt"; git worktree prune; rc=1
-    htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
     if [ -z "$htip" ] || ! git fetch -q origin "+refs/heads/handoff/$topic:refs/hpo-relay/fold/$topic" 2>/dev/null \
       || ! git worktree add -q --detach "$wt" "refs/hpo-relay/fold/$topic" 2>/dev/null; then  # mut:foldref
       why="no handoff/$topic to push the body from"; echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
@@ -865,8 +879,8 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     fi
     git worktree remove --force "$wt" 2>/dev/null; git update-ref -d "refs/hpo-relay/fold/$topic" 2>/dev/null
     if [ $rc = 0 ]; then echo "$topic $bsha" >> "$state/cloud-folded"; echo "cloud_relay: FOLDED $topic: carries landed, body_push.sh pushed handoff-body/$topic"
-      fold_judge "$memo.$$" /dev/null "$topic" "$sha" "$bsha" folded "$now"
-    else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"
+      fold_judge "$memo.$$" /dev/null "$topic" "$sha" "$bsha" folded "$now" "$blob" "${htip:--}"
+    else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$blob" "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"
     fi
   done < "$state/cloud-wip.$$"
   mv -f "$memo.$$" "$memo"; level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$"
@@ -1964,6 +1978,34 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   chk "... with no cloud-folded entry" 1 grep -q "^cf-h " "$t/state/cloud-folded"
   chk "... no FOLDED announcement" 1 grep -q "FOLDED cf-h" <<< "$cfo"
   chk "... and no body_push.sh run" 1 grep -q "^cf-h " "$t/bps"
+  # Carry 17 (P566): body_push.sh keeps each refused body as a NEW parentless commit; a failed fold stands for a later kept
+  # body with the same stop, BODY.md blob and handoff tip, and runs again when any of the three moves.
+  printf '#!/bin/bash\necho "$@" >> %s/bpk\nexit 1\n' "$t" > "$t/bpfail"; chmod +x "$t/bpfail"; export HPO_RELAY_BODYPUSH=$t/bpfail
+  : > "$t/bpk"; cfref handoff/cf-k code.txt "code K"; cfref handoff-wip/cf-k BLOCKED.md "body_push: REFUSED CARRY-LANDED"
+  cfref handoff-wip/cf-k-body BODY.md "the body K"
+  cfo=$(carry_fold_arm 2>&1); kb1=$(cftip handoff-wip/cf-k-body)
+  chk "null control (carry 17): a stop with no record runs body_push.sh as today" 1 test "$(grep -c '^cf-k ' "$t/bpk")" != 1
+  GIT_AUTHOR_DATE="2001-01-01T00:00:00Z" GIT_COMMITTER_DATE="2001-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K"
+  chk "the train-residue shape: the refused body is kept again as a new commit with the same BODY.md blob" 1 test "$(cftip handoff-wip/cf-k-body)" = "$kb1"
+  cfo=$(carry_fold_arm 2>&1)
+  chk "... and is not pushed again (same stop, blob and handoff tip)" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 1
+  chk "... the tick line says OWED, unchanged since the first failure" 0 grep -q "OWED carry-fold cf-k unchanged since 20[0-9-]*T[0-9:]*Z: body_push rc=1" <<< "$cfo"
+  chk "... and its OWED level line still stands" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-k .*body_push rc=1" "$LOG.level"
+  cfref handoff-wip/cf-k-body BODY.md "the body K, edited"; carry_fold_arm >/dev/null 2>&1
+  chk "a changed BODY.md blob runs body_push.sh again" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 2
+  GIT_AUTHOR_DATE="2002-01-01T00:00:00Z" GIT_COMMITTER_DATE="2002-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"; carry_fold_arm >/dev/null 2>&1
+  chk "null control: the edited body kept again as a new commit is skipped" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 2
+  GIT_AUTHOR_DATE="2003-01-01T00:00:00Z" GIT_COMMITTER_DATE="2003-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"
+  cfref handoff/cf-k code.txt "code K, moved"; carry_fold_arm >/dev/null 2>&1
+  chk "a moved handoff/<topic> tip with the same blob runs body_push.sh again" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 3
+  GIT_AUTHOR_DATE="2004-01-01T00:00:00Z" GIT_COMMITTER_DATE="2004-01-01T00:00:00Z" cfref handoff-wip/cf-k-body BODY.md "the body K, edited"
+  awk -v e=$(( $(date +%s) - 3601 )) '$1 == "cf-k" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  carry_fold_arm >/dev/null 2>&1
+  chk "a record an hour old no longer stands over a new kept commit" 0 test "$(grep -c '^cf-k ' "$t/bpk")" = 4
+  cfref handoff-wip/cf-l BLOCKED.md "the fixer is stuck, again"; carry_fold_arm >/dev/null 2>&1
+  awk '$1 == "cf-l" { $6 = ""; $7 = ""; gsub(/  +/, " ") } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
+  : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
+  chk "a memo record from before the blob and tip fields is judged again, not read with shifted fields" 0 grep -q "handoff-wip/cf-l\$" "$t/fetches"
   unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
   cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index fbf4c39884..4ff47e29b2 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -380,6 +380,16 @@ def attempts(rows: list) -> dict:
 
 
 # ------------------------------------------------------------------- level
+def empty_net(git, main: str, tip: str) -> bool:
+    """tip's change against its merge-base with main is nothing, read cleanly: an add-then-remove pair
+    leaves no diff to carry. An unreadable merge-base or diff is not empty."""
+    rc, mb = git(["merge-base", main, tip])
+    if rc:
+        return False
+    rc, names = git(["diff", "--name-status", "--no-renames", mb.strip(), tip])
+    return rc == 0 and not names.strip()
+
+
 def covered(git, main: str, tip: str) -> bool:
     """Main carries every file tip's uncovered commits touch: the same bytes at
     the path; an added file's bytes elsewhere (a recovery moved it); a deletion
@@ -458,7 +468,7 @@ def reverse_applies(git, main: str, tip: str) -> bool:
                 and git(["apply", "--cached", "--check", patch], env)[0] != 0)
 
 
-ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "content")
+ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "empty", "content")
 
 
 def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: bool = True) -> "str | None":
@@ -469,6 +479,7 @@ def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: b
       merges-only    the only commits outside them are merges whose combined
                      diff is empty (no resolution of their own)
       reverse-apply  reverse_applies: the patch is on main, context and all
+      empty          the net change against the merge-base is nothing (an add-then-remove pair)
       content        covered: the change is on main under another commit"""
     if ancestry:
         rc, out = git(["rev-list", "--count", tip, "--not", main, *heads])
@@ -483,6 +494,8 @@ def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: b
     if content:
         if reverse_applies(git, main, tip):
             return "reverse-apply"
+        if empty_net(git, main, tip):  # mut:emptynet
+            return "empty"
         if covered(git, main, tip):
             return "content"
     return None
@@ -1181,6 +1194,19 @@ def self_test() -> int:
         check("landed: a tip inside main reads ancestor, not merges-only", landed(gw, mn, anc) == "ancestor")
         check("landed: the re-applied hunk is content (reverse-apply cannot: forward applies too)",
               landed(gw, mn, cov) == "content" and not reverse_applies(gw, mn, cov))
+        g("checkout", "-qb", "work18", mn)
+        put("tmp_add.txt", "added then removed\n", "add a file")
+        g("rm", "-q", "tmp_add.txt")
+        g("commit", "-qm", "remove it again")
+        emt = g("rev-parse", "HEAD")
+        check("landed: an add-then-remove tip with an empty net diff lands as empty (carry 20)",
+              landed(gw, mn, emt) == "empty" and not covered(gw, mn, emt))
+        g("checkout", "-qb", "work19", mn)
+        rl = put("real_new.txt", "one real uncovered line\n", "a real uncovered add")
+        check("null control: a tip with one real uncovered line stays None (carry 20)", landed(gw, mn, rl) is None)
+        check("null control: a failing diff read (rc != 0) is not empty (carry 20)",
+              not empty_net(lambda a: (1, "") if a[0] == "diff" else gw(a), mn, emt))
+        g("checkout", "-q", "main")
         g("checkout", "-qb", "work7", gb)
         mv = put("moved.txt", "same bytes\n", "add a file")
         g("checkout", "-qb", "work8", gb)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
