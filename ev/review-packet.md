# Review packet #2990
head: 2f5d5065e5361237ed23ab6f92b7ad2fd20f817e
base: 507a9ec264eb373b132248d752259254d8a9fa4d

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124065412363 success
arch-score / arch-score id=124065344144 success
arm id=124064696791 skipped
budget-raise-gate / budget-raise-gate id=124065343841 success
cancel-superseded id=124064766931 skipped
codeql / Analyze (actions) id=124065343713 success
codeql / Analyze (javascript-typescript) id=124065343747 success
codeql / Analyze (python) id=124065343861 success
governance / delivery-status id=124065343860 success
governance / delivery-status-publish id=124065346376 skipped
governance / env-matrix id=124065343804 success
governance / instrument-self-tests id=124065344016 in_progress
governance / policy-docs id=124065343783 success
governance / record id=124065346721 skipped
governance / wave-script id=124065343847 success
hassfest / hassfest id=124065343849 success
kernel-points id=124065346262 skipped
prelude id=124064765222 in_progress
refresh id=124064764848 success
tests / arch-instrument id=124065720404 success
tests / briefs id=124065343838 success
tests / browser id=124065720599 success
tests / ci-ratchet id=124067617447 skipped
tests / claims-autofix id=124067616677 skipped
tests / closure-scope id=124065343877 success
tests / closures id=124065720713 success
tests / closures-autofix id=124067472095 skipped
tests / coverage id=124065721903 skipped
tests / coverage-ratchet id=124065723734 skipped
tests / fast (3.14) id=124065720502 success
tests / graders-head-copy id=124065721012 success
tests / lane-proofs id=124067615306 success
tests / mutation id=124065343943 success
tests / mutation-autofix id=124065840237 skipped
tests / mutation-pins id=124065838684 skipped
tests / nightly-ha id=124065724626 skipped
tests / nightly-status id=124065343864 success
tests / replay id=124065722147 skipped
tests / typing id=124065720407 success
validate / validate-hacs id=124065343803 success

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
diff --git a/dev/programme/delivery/2872.md b/dev/programme/delivery/2872.md
index c2a531a33..0fc8d8e3b 100644
--- a/dev/programme/delivery/2872.md
+++ b/dev/programme/delivery/2872.md
@@ -1 +1 @@
-- [#2872](https://github.com/tvofi/heatpump_optimizer/pull/2872) — **open**, roster: R10-COP-PARTLOAD.
+- [#2872](https://github.com/tvofi/heatpump_optimizer/pull/2872) — **merged `d1c7708`**, R10-COP-PARTLOAD: price the compressor's power in COP, off by default (R10-COP-PARTLOAD).
diff --git a/dev/programme/delivery/2976.md b/dev/programme/delivery/2976.md
index 936fe1962..1f676a985 100644
--- a/dev/programme/delivery/2976.md
+++ b/dev/programme/delivery/2976.md
@@ -1 +1 @@
-- [#2976](https://github.com/tvofi/heatpump_optimizer/pull/2976) — **open**, R10-UX-HEALTH: the Health tab, from the owner's report of 2026-10-14 (R10-UX-HEALTH)
+- [#2976](https://github.com/tvofi/heatpump_optimizer/pull/2976) — **merged `559134e`**, R10-UX-HEALTH: the Health tab, from the owner's report of 2026-10-14 (R10-UX-HEALTH).
diff --git a/dev/programme/delivery/2977.md b/dev/programme/delivery/2977.md
index 869e82fa5..8ecc60b15 100644
--- a/dev/programme/delivery/2977.md
+++ b/dev/programme/delivery/2977.md
@@ -1 +1 @@
-- [#2977](https://github.com/tvofi/heatpump_optimizer/pull/2977) — **open**, R10-FLY-CARRY-CLAIM-DRIVER: a claim file the driver resolved carries (R10-FLY-CARRY-CLAIM-DRIVER)
+- [#2977](https://github.com/tvofi/heatpump_optimizer/pull/2977) — **merged `96ac7d6`**, R10-FLY-CARRY-CLAIM-DRIVER: a claim file the driver resolved carries (R10-FLY-CARRY-CLAIM-DRIVER).
diff --git a/dev/programme/delivery/2978.md b/dev/programme/delivery/2978.md
index 5693ea7ff..164a6d541 100644
--- a/dev/programme/delivery/2978.md
+++ b/dev/programme/delivery/2978.md
@@ -1 +1 @@
-- [#2978](https://github.com/tvofi/heatpump_optimizer/pull/2978) — **open**, R10-TRAIN-OVERLAP-GRADE part 2: one admission rule for add and the batch drain (R10-TRAIN-OVERLAP-GRADE)
+- [#2978](https://github.com/tvofi/heatpump_optimizer/pull/2978) — **merged `89ccf73`**, R10-TRAIN-OVERLAP-GRADE part 2: one admission rule for add and the batch drain (R10-TRAIN-OVERLAP-GRADE).
diff --git a/dev/programme/delivery/2980.md b/dev/programme/delivery/2980.md
index ce6a134be..40f90621a 100644
--- a/dev/programme/delivery/2980.md
+++ b/dev/programme/delivery/2980.md
@@ -1 +1 @@
-- [#2980](https://github.com/tvofi/heatpump_optimizer/pull/2980) — **open**, triage: s7 batch 64, P293 carry_audit Evidence items (R10-TRIAGE-S7)
+- [#2980](https://github.com/tvofi/heatpump_optimizer/pull/2980) — **merged `bf8103f`**, triage: s7 batch 64, P293 carry_audit Evidence items.
diff --git a/dev/programme/delivery/2985.md b/dev/programme/delivery/2985.md
index 960b723ab..dc8e7bf9a 100644
--- a/dev/programme/delivery/2985.md
+++ b/dev/programme/delivery/2985.md
@@ -1 +1 @@
-- [#2985](https://github.com/tvofi/heatpump_optimizer/pull/2985) — **open**, triage: s8 batch 68 (P299 ruling) (R10-TRIAGE-S6)
+- [#2985](https://github.com/tvofi/heatpump_optimizer/pull/2985) — **merged `1cbf563`**, triage: s8 batch 68 (P299 ruling).
diff --git a/dev/programme/delivery/2986.md b/dev/programme/delivery/2986.md
index 744e34e1e..349338b25 100644
--- a/dev/programme/delivery/2986.md
+++ b/dev/programme/delivery/2986.md
@@ -1 +1 @@
-- [#2986](https://github.com/tvofi/heatpump_optimizer/pull/2986) — **open**, triage: s8 batch 69 (P301 ruling) (R10-TRIAGE-S6)
+- [#2986](https://github.com/tvofi/heatpump_optimizer/pull/2986) — **merged `fe709cb`**, triage: s8 batch 69 (P301 ruling).
diff --git a/dev/programme/delivery/2988.md b/dev/programme/delivery/2988.md
index 99ee57214..e0b17e5bc 100644
--- a/dev/programme/delivery/2988.md
+++ b/dev/programme/delivery/2988.md
@@ -1 +1 @@
-- [#2988](https://github.com/tvofi/heatpump_optimizer/pull/2988) — **open**, roster: batch s8 (merge main; plan-optimization ops; s7 refused-op replays) (R10-ROSTER-OPS)
+- [#2988](https://github.com/tvofi/heatpump_optimizer/pull/2988) — **merged `b014193`**, roster: batch s8 (merge main; plan-optimization ops; s7 refused-op replays).
diff --git a/dev/programme/delivery/2990.md b/dev/programme/delivery/2990.md
new file mode 100644
index 000000000..e489fcdc5
--- /dev/null
+++ b/dev/programme/delivery/2990.md
@@ -0,0 +1 @@
+- [#2990](https://github.com/tvofi/heatpump_optimizer/pull/2990) — **open**, record: delivery rows (autofix)

