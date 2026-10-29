# Review packet #2966
head: 850c81c3fbc76a509adbfb5195774ad3d4adecff
base: fbe5837a5c422db4d96df8c327cc9c01b345957a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123797460973 success
arch-score / arch-score id=123797398013 success
arm id=123797248079 skipped
budget-raise-gate / budget-raise-gate id=123797397875 success
cancel-superseded id=123801027602 success
codeql / Analyze (actions) id=123797398109 success
codeql / Analyze (javascript-typescript) id=123797398203 success
codeql / Analyze (python) id=123797398392 success
governance / delivery-status id=123797398134 success
governance / delivery-status-publish id=123797400485 skipped
governance / env-matrix id=123797398035 success
governance / instrument-self-tests id=123797398386 in_progress
governance / policy-docs id=123797398053 success
governance / record id=123797399635 skipped
governance / wave-script id=123797398146 success
hassfest / hassfest id=123797397977 success
kernel-points id=123797399328 skipped
prelude id=123801027606 in_progress
refresh id=123801027097 success
tests / arch-instrument id=123797580620 success
tests / briefs id=123797397906 success
tests / browser id=123797580528 success
tests / ci-ratchet id=123799435089 skipped
tests / claims-autofix id=123799248238 skipped
tests / closure-scope id=123797398049 success
tests / closures id=123797580617 success
tests / closures-autofix id=123799435281 skipped
tests / coverage id=123797581858 skipped
tests / coverage-ratchet id=123797583568 skipped
tests / fast (3.14) id=123797580533 success
tests / graders-head-copy id=123797582212 success
tests / lane-proofs id=123799245828 success
tests / mutation id=123797397995 success
tests / mutation-autofix id=123797675304 skipped
tests / mutation-pins id=123797675683 skipped
tests / nightly-ha id=123797582572 skipped
tests / nightly-status id=123797397954 failure
tests / replay id=123797582295 skipped
tests / typing id=123797580307 success
validate / validate-hacs id=123797397809 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/delivery_status.py
             `tests/delivery_status.py` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2939.md b/dev/programme/delivery/2939.md
index 82a53df3a..9a12f4a88 100644
--- a/dev/programme/delivery/2939.md
+++ b/dev/programme/delivery/2939.md
@@ -1 +1 @@
-- [#2939](https://github.com/tvofi/heatpump_optimizer/pull/2939) — **open**, R10-ORCH-REVIEW-PACKET: review_packet refuses a head lacking its handoff; fixer handoff runs it first (R10-ORCH-REVIEW-PACKET)
+- [#2939](https://github.com/tvofi/heatpump_optimizer/pull/2939) — **merged `2795780`**, R10-ORCH-REVIEW-PACKET: review_packet refuses a head lacking its handoff; fixer handoff runs it first (R10-ORCH-REVIEW-PACKET).
diff --git a/dev/programme/delivery/2953.md b/dev/programme/delivery/2953.md
index d085e3e67..526a24b0e 100644
--- a/dev/programme/delivery/2953.md
+++ b/dev/programme/delivery/2953.md
@@ -1 +1 @@
-- [#2953](https://github.com/tvofi/heatpump_optimizer/pull/2953) — **open**, R10-FRICTION-FIXER-MD: root cause of the fixer.md friction key (#2895) (R10-FRICTION-FIXER-MD)
+- [#2953](https://github.com/tvofi/heatpump_optimizer/pull/2953) — **merged `2033b87`**, R10-FRICTION-FIXER-MD: root cause of the fixer.md friction key (#2895) (R10-FRICTION-FIXER-MD).
diff --git a/dev/programme/delivery/2956.md b/dev/programme/delivery/2956.md
index f76660ffb..593a1da69 100644
--- a/dev/programme/delivery/2956.md
+++ b/dev/programme/delivery/2956.md
@@ -1 +1 @@
-- [#2956](https://github.com/tvofi/heatpump_optimizer/pull/2956) — **open**, R10-FRICTION-CLAIM-FALSE: root cause of the claim-false friction key (#2907) (R10-FRICTION-CLAIM-FALSE)
+- [#2956](https://github.com/tvofi/heatpump_optimizer/pull/2956) — **merged `ce5940c`**, R10-FRICTION-CLAIM-FALSE: root cause of the claim-false friction key (#2907) (R10-FRICTION-CLAIM-FALSE).
diff --git a/dev/programme/delivery/2957.md b/dev/programme/delivery/2957.md
index ba85f20d6..c512414da 100644
--- a/dev/programme/delivery/2957.md
+++ b/dev/programme/delivery/2957.md
@@ -1 +1 @@
-- [#2957](https://github.com/tvofi/heatpump_optimizer/pull/2957) — **open**, R10-FRICTION-GATE-SCOPING: root cause of the gate-scoping.md friction key (#2835) (R10-FRICTION-GATE-SCOPING)
+- [#2957](https://github.com/tvofi/heatpump_optimizer/pull/2957) — **merged `553cee1`**, R10-FRICTION-GATE-SCOPING: root cause of the gate-scoping.md friction key (#2835) (R10-FRICTION-GATE-SCOPING).
diff --git a/dev/programme/delivery/2958.md b/dev/programme/delivery/2958.md
index cfa67ac5b..6aa8d9d90 100644
--- a/dev/programme/delivery/2958.md
+++ b/dev/programme/delivery/2958.md
@@ -1 +1 @@
-- [#2958](https://github.com/tvofi/heatpump_optimizer/pull/2958) — **open**, triage: s7 batch 60 (P278-P285) (R10-TRIAGE-S6)
+- [#2958](https://github.com/tvofi/heatpump_optimizer/pull/2958) — **merged `20c2051`**, triage: s7 batch 60 (P278-P285).
diff --git a/dev/programme/delivery/2959.md b/dev/programme/delivery/2959.md
index c40cb03be..dd7d06acb 100644
--- a/dev/programme/delivery/2959.md
+++ b/dev/programme/delivery/2959.md
@@ -1 +1 @@
-- [#2959](https://github.com/tvofi/heatpump_optimizer/pull/2959) — **open**, harness: the carries' mutants in the seat self-tests (R10-FLOW-MAIN-GATE)
+- [#2959](https://github.com/tvofi/heatpump_optimizer/pull/2959) — **merged `2fde526`**, harness: the carries' mutants in the seat self-tests (R10-FLOW-MAIN-GATE).
diff --git a/dev/programme/delivery/2960.md b/dev/programme/delivery/2960.md
index 3df97afdb..450cf63ed 100644
--- a/dev/programme/delivery/2960.md
+++ b/dev/programme/delivery/2960.md
@@ -1 +1 @@
-- [#2960](https://github.com/tvofi/heatpump_optimizer/pull/2960) — **open**, R10-STORE-RACES: census harness recorded as an inert read (R10-STORE-RACES)
+- [#2960](https://github.com/tvofi/heatpump_optimizer/pull/2960) — **merged `e5ddba1`**, R10-STORE-RACES: census harness recorded as an inert read (R10-STORE-RACES).
diff --git a/dev/programme/delivery/2963.md b/dev/programme/delivery/2963.md
index 2e31f0428..de494d7f7 100644
--- a/dev/programme/delivery/2963.md
+++ b/dev/programme/delivery/2963.md
@@ -1 +1 @@
-- [#2963](https://github.com/tvofi/heatpump_optimizer/pull/2963) — **open**, R10-ADVISOR-WHATIF: pin the moved sites mutation_table.py --pin-killed drove (R10-ADVISOR-WHATIF)
+- [#2963](https://github.com/tvofi/heatpump_optimizer/pull/2963) — **merged `7274f7f`**, R10-ADVISOR-WHATIF: pin the moved sites mutation_table.py --pin-killed drove (R10-ADVISOR-WHATIF).
diff --git a/dev/programme/delivery/2966.md b/dev/programme/delivery/2966.md
new file mode 100644
index 000000000..b198d77e9
--- /dev/null
+++ b/dev/programme/delivery/2966.md
@@ -0,0 +1 @@
+- [#2966](https://github.com/tvofi/heatpump_optimizer/pull/2966) — **open**, record: delivery rows (autofix)

