# Review packet #3229
head: 189fdb8893334dba36f5841ee62ddbb160e43659
base: 2dc960f4a92b1ebf56ed5aa33f55400d8e269a10

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127523432126 success
arch-score / arch-score id=127547762487 success
arm id=127522646843 skipped
budget-raise-gate / budget-raise-gate id=127547762875 success
cancel-superseded id=127546628249 success
codeql id=127547764676 skipped
codeql / Analyze (actions) id=127522986498 success
codeql / Analyze (javascript-typescript) id=127522986611 success
codeql / Analyze (python) id=127522986604 success
gate id=127548709421 in_progress
governance id=127547766264 skipped
governance / delivery-status id=127522986842 failure
governance / delivery-status-publish id=127522989349 skipped
governance / env-matrix id=127522986804 success
governance / instrument-self-tests id=127522986730 cancelled
governance / policy-docs id=127522986811 success
governance / record id=127522989493 skipped
governance / wave-script id=127522986728 success
hassfest id=127547764190 skipped
hassfest / hassfest id=127522986538 success
kernel-points id=127547764807 skipped
pr-contract / pr-contract id=127548391095 success
prelude id=127546628320 in_progress
refresh id=127546628159 success
tests id=127547765616 skipped
tests / arch-instrument id=127523332558 success
tests / briefs id=127522986658 success
tests / browser id=127523332548 success
tests / ci-ratchet id=127534094951 skipped
tests / claims-autofix id=127524967413 skipped
tests / closure-scope id=127522986506 success
tests / closures id=127523332688 success
tests / closures-autofix id=127534093869 skipped
tests / coverage id=127523332476 success
tests / coverage-ratchet id=127524342863 success
tests / fast (3.14) id=127523332695 success
tests / graders-head-copy id=127524342687 success
tests / lane-proofs id=127525877649 success
tests / mutation id=127522986512 success
tests / mutation-autofix id=127523295718 skipped
tests / mutation-pins id=127523294393 skipped
tests / nightly-ha id=127523335186 skipped
tests / nightly-status id=127522986559 failure
tests / replay id=127523334661 skipped
tests / typing id=127523332664 success
validate id=127547765121 skipped
validate / validate-hacs id=127522986425 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tools/audit/seat/bus.sh
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3229.md b/dev/programme/delivery/3229.md
new file mode 100644
index 000000000..f4aef8f0a
--- /dev/null
+++ b/dev/programme/delivery/3229.md
@@ -0,0 +1 @@
+- [#3229](https://github.com/tvofi/heatpump_optimizer/pull/3229) — **open**, R10-FLY-RELAY-HOLD: fly relay hold (R10-FLY-RELAY-HOLD)
diff --git a/tools/audit/seat/bus.sh b/tools/audit/seat/bus.sh
index 966b9ad20..bb14786a4 100755
--- a/tools/audit/seat/bus.sh
+++ b/tools/audit/seat/bus.sh
@@ -438,12 +438,17 @@ post_verdict() { # pr [expected sha] -> prints one BUS posted|refused|unsigned l
 # re-reads the verdict this post wrote. Off unless HPO_BUS_TRAIN_STATE names
 # the train's state dir; HPO_BUS_TRAIN_MANDATE is a started train's --mandate;
 # HPO_BUS_TRAIN_CMD replaces the command (the self-test's stub). Its whole
-# output is appended to $S/train-add.log. A refused add never fails the post:
+# output is appended to $S/train-add.log. A PR listed in the relay's cloud-handoff-hold file is skipped.
+# A refused add never fails the post:
 # `merge_train.py sweep` is the backstop for a head this missed.
 train_add() { # pr first-line -> one `BUS train-add <pr> rc=<rc> <add's last line>` for a merge verdict
   local sha rc log=$S/train-add.log
   [ -n "${HPO_BUS_TRAIN_STATE:-}" ] || return 0
   case $2 in "Fix review: merge "*) sha=$(verdict_sha "$2") || return 0 ;; *) return 0 ;; esac
+  # THE HOLD (R10-FLY-RELAY-HOLD): a PR in the orchestrator's cloud-handoff-hold file is not added. The
+  # file's one reader is cloud_relay.sh's `held` (rc 0 listed, 2 malformed: neither adds, never hold-none).
+  bash "$ROOT/tools/audit/seat/cloud_relay.sh" held "$1" 2>/dev/null; rc=$?  # mut:trainhold
+  [ $rc = 1 ] || { printf 'BUS train-add %s held (cloud-handoff-hold, rc=%s)\n' "$1" "$rc"; return 0; }
   printf '== %s add %s %s\n' "$(date -u +%FT%TZ)" "$1" "$sha" >> "$log"
   ${HPO_BUS_TRAIN_CMD:-python3 "$ROOT/tools/audit/seat/merge_train.py"} add "$1" "$sha" --repo "$REPO" \
     --state-dir "$HPO_BUS_TRAIN_STATE" ${HPO_BUS_TRAIN_MANDATE:+--mandate "$HPO_BUS_TRAIN_MANDATE"} --auto \
@@ -1141,6 +1146,22 @@ bus-nonce: $N1b" ] && [ "$(grep -c " $N1b " "$W/state/dispatched")" = 2 ] \
   [ "$(echo "$out" | tail -n 1)" = "BUS train-add 7 rc=0 ADDED #7 to the live train (pid 1)" ] \
     && [ "$(cat "$W/train-argv")" = "add|7|$h1|--repo|o/r|--state-dir|$W/train|--mandate|M1|--auto|" ]
   expect "a posted merge verdict is added to the train at its head, after the post (the event add)" $?
+  # The hold (R10-FLY-RELAY-HOLD): train_add reads the relay's cloud-handoff-hold file through its `held`.
+  mkdir -p "$W/hold"; : > "$W/train-argv"
+  hm="Fix review: merge $h1"
+  mkdir -p "$W/tstate"; tadd() { S=$W/tstate REPO=o/r HPO_STATE_DIR=$W/hold HPO_BUS_TRAIN_STATE=$W/train HPO_BUS_TRAIN_CMD="bash $W/addstub" train_add "$@"; }
+  printf '# hold\n7\n' > "$W/hold/cloud-handoff-hold"
+  out=$(tadd 7 "$hm"); [ "$out" = "BUS train-add 7 held (cloud-handoff-hold, rc=0)" ] && [ ! -s "$W/train-argv" ]
+  expect "a PR listed in the hold file is not added to the train" $?
+  out=$(tadd 8 "$hm"); echo "$out" | grep -q "^BUS train-add 8 rc=0 " && [ -s "$W/train-argv" ]
+  expect "a PR the hold file does not list is added (null control for the skip)" $?
+  : > "$W/train-argv"; : > "$W/hold/cloud-handoff-hold"
+  out=$(tadd 7 "$hm"); echo "$out" | grep -q "^BUS train-add 7 rc=0 " && [ -s "$W/train-argv" ]
+  expect "an empty hold file adds as before (null control)" $?
+  : > "$W/train-argv"; printf 'seven\n' > "$W/hold/cloud-handoff-hold"
+  out=$(tadd 7 "$hm"); [ "$out" = "BUS train-add 7 held (cloud-handoff-hold, rc=2)" ] && [ ! -s "$W/train-argv" ]
+  expect "a malformed hold file adds nothing (never hold-none)" $?
+  rm -f "$W/hold/cloud-handoff-hold"; : > "$W/train-argv"
   [ "$(tip "verdict/7^{tree}")" = "$(tip "review/7^{tree}")" ]; expect "the signed verdict carries the reviewer's tree unchanged" $?
   git -C "$W/origin.git" log -1 --format=%B "$v1" | grep -qx "bus-model: opus"
   expect "the signed verdict names the model its dispatch recorded (bus-model:)" $?

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
