# Review packet #2979
head: 1dcb1fde33af27e33c380ccd0311638741684aa2
base: 26c9d22a3c37a1b48f8561d061ae58b03eef5b54

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123855826175 success
arch-score / arch-score id=123855774477 success
arm id=123855695802 skipped
budget-raise-gate / budget-raise-gate id=123855774474 success
cancel-superseded id=123860692764 success
codeql / Analyze (actions) id=123855774483 success
codeql / Analyze (javascript-typescript) id=123855774409 success
codeql / Analyze (python) id=123855774380 success
governance / delivery-status id=123855774391 success
governance / delivery-status-publish id=123855776017 skipped
governance / env-matrix id=123855774480 success
governance / instrument-self-tests id=123855774494 in_progress
governance / policy-docs id=123855774464 success
governance / record id=123855776096 skipped
governance / wave-script id=123855774359 success
hassfest / hassfest id=123855774327 success
kernel-points id=123855775472 skipped
prelude id=123860692475 in_progress
refresh id=123860692885 success
tests / arch-instrument id=123855916241 success
tests / briefs id=123855774382 success
tests / browser id=123855916186 success
tests / ci-ratchet id=123857337409 skipped
tests / claims-autofix id=123857337302 skipped
tests / closure-scope id=123855774286 success
tests / closures id=123855916243 success
tests / closures-autofix id=123857296179 skipped
tests / coverage id=123855917639 skipped
tests / coverage-ratchet id=123855918271 skipped
tests / fast (3.14) id=123855916245 success
tests / graders-head-copy id=123855916589 success
tests / lane-proofs id=123857336019 success
tests / mutation id=123855774290 success
tests / mutation-autofix id=123856024030 skipped
tests / mutation-pins id=123856023490 skipped
tests / nightly-ha id=123855918427 skipped
tests / nightly-status id=123855774364 failure
tests / replay id=123855918106 skipped
tests / typing id=123855916190 success
validate / validate-hacs id=123855774292 success

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
diff --git a/dev/programme/delivery/2954.md b/dev/programme/delivery/2954.md
index 1a662ac1c..c1eccbabb 100644
--- a/dev/programme/delivery/2954.md
+++ b/dev/programme/delivery/2954.md
@@ -1 +1 @@
-- [#2954](https://github.com/tvofi/heatpump_optimizer/pull/2954) — **open**, R10-RECORD-API-O1: record-job API carries from the 04:53Z rate-limit RCA (R10-RECORD-API-O1)
+- [#2954](https://github.com/tvofi/heatpump_optimizer/pull/2954) — **merged `e867edb`**, R10-RECORD-API-O1: record-job API carries from the 04:53Z rate-limit RCA (R10-RECORD-API-O1).
diff --git a/dev/programme/delivery/2964.md b/dev/programme/delivery/2964.md
index 7d1f2b80e..ff853fed1 100644
--- a/dev/programme/delivery/2964.md
+++ b/dev/programme/delivery/2964.md
@@ -1 +1 @@
-- [#2964](https://github.com/tvofi/heatpump_optimizer/pull/2964) — **open**, R10-FLY-NIGHTLY-HB: heartbeat stall sampler uses the stdlib remote unwinder where it exists (R10-FLY-NIGHTLY-HB)
+- [#2964](https://github.com/tvofi/heatpump_optimizer/pull/2964) — **merged `8b3d430`**, R10-FLY-NIGHTLY-HB: heartbeat stall sampler uses the stdlib remote unwinder where it exists.
diff --git a/dev/programme/delivery/2967.md b/dev/programme/delivery/2967.md
index 1eadc8828..b2701aa30 100644
--- a/dev/programme/delivery/2967.md
+++ b/dev/programme/delivery/2967.md
@@ -1 +1 @@
-- [#2967](https://github.com/tvofi/heatpump_optimizer/pull/2967) — **open**, R10-MARKETPLACE-EXTRAS: scheduled HACS-action and hassfest runs; D10 Marketplace readiness (R10-MARKETPLACE-EXTRAS)
+- [#2967](https://github.com/tvofi/heatpump_optimizer/pull/2967) — **merged `2ab53fe`**, R10-MARKETPLACE-EXTRAS: scheduled HACS-action and hassfest runs; D10 Marketplace readiness.
diff --git a/dev/programme/delivery/2970.md b/dev/programme/delivery/2970.md
index de4cb744a..59c9fea75 100644
--- a/dev/programme/delivery/2970.md
+++ b/dev/programme/delivery/2970.md
@@ -1 +1 @@
-- [#2970](https://github.com/tvofi/heatpump_optimizer/pull/2970) — **open**, triage: s6 batch 61 (P286-P289) (R10-PROPOSAL-TRIAGE)
+- [#2970](https://github.com/tvofi/heatpump_optimizer/pull/2970) — **merged `26c9d22`**, triage: s6 batch 61 (P286-P289).
diff --git a/dev/programme/delivery/2971.md b/dev/programme/delivery/2971.md
index b0b7fad17..e9862b245 100644
--- a/dev/programme/delivery/2971.md
+++ b/dev/programme/delivery/2971.md
@@ -1 +1 @@
-- [#2971](https://github.com/tvofi/heatpump_optimizer/pull/2971) — **open**, R10-NIGHTLY-SLOW-ROLLING: repair the nightly slow-lane rolling checks (R10-NIGHTLY-SLOW-ROLLING)
+- [#2971](https://github.com/tvofi/heatpump_optimizer/pull/2971) — **merged `2f28a21`**, R10-NIGHTLY-SLOW-ROLLING: repair the nightly slow-lane rolling checks.
diff --git a/dev/programme/delivery/2972.md b/dev/programme/delivery/2972.md
index 59849b2d5..c369522a8 100644
--- a/dev/programme/delivery/2972.md
+++ b/dev/programme/delivery/2972.md
@@ -1 +1 @@
-- [#2972](https://github.com/tvofi/heatpump_optimizer/pull/2972) — **open**, triage: s6 batch 62 (P290) (R10-PROPOSAL-TRIAGE)
+- [#2972](https://github.com/tvofi/heatpump_optimizer/pull/2972) — **merged `da06660`**, triage: s6 batch 62 (P290).
diff --git a/dev/programme/delivery/2974.md b/dev/programme/delivery/2974.md
index ed37e5a43..d81eec0fd 100644
--- a/dev/programme/delivery/2974.md
+++ b/dev/programme/delivery/2974.md
@@ -1 +1 @@
-- [#2974](https://github.com/tvofi/heatpump_optimizer/pull/2974) — **open**, triage: s6 batch 63 (P291, P292) (R10-TRIAGE-S6)
+- [#2974](https://github.com/tvofi/heatpump_optimizer/pull/2974) — **merged `12c60f0`**, triage: s6 batch 63 (P291, P292).
diff --git a/dev/programme/delivery/2979.md b/dev/programme/delivery/2979.md
new file mode 100644
index 000000000..d745d0733
--- /dev/null
+++ b/dev/programme/delivery/2979.md
@@ -0,0 +1 @@
+- [#2979](https://github.com/tvofi/heatpump_optimizer/pull/2979) — **open**, record: delivery rows (autofix)

