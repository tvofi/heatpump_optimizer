# Review packet #3008
head: 35ede8b8aa9c1c216d5d3bbef9ff35d3589bf95c
base: c098261d4f4445d80aa4d892a905f329fb5610a2

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124254322332 success
arch-score / arch-score id=124252803439 success
arm id=124252226933 skipped
budget-raise-gate / budget-raise-gate id=124252803204 success
cancel-superseded id=124252279191 skipped
codeql / Analyze (actions) id=124252803574 success
codeql / Analyze (javascript-typescript) id=124252804043 in_progress
codeql / Analyze (python) id=124252803526 success
governance / delivery-status id=124252803379 success
governance / delivery-status-publish id=124252804976 skipped
governance / env-matrix id=124252803448 in_progress
governance / instrument-self-tests id=124252803602 in_progress
governance / policy-docs id=124252803541 success
governance / record id=124252806300 skipped
governance / wave-script id=124252803474 success
hassfest / hassfest id=124252803463 success
kernel-points id=124252805387 skipped
prelude id=124252277637 in_progress
refresh id=124252277295 success
tests / arch-instrument id=124255472152 queued
tests / briefs id=124252803248 in_progress
tests / browser id=124255471982 queued
tests / closure-scope id=124252803551 in_progress
tests / closures id=124255472337 queued
tests / coverage-ratchet id=124256350169 skipped
tests / fast (3.14) id=124255472017 queued
tests / graders-head-copy id=124255472803 queued
tests / mutation id=124252803009 in_progress
tests / nightly-status id=124252803037 success
tests / typing id=124255472063 queued
validate / validate-hacs id=124252803644 success

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
diff --git a/dev/programme/delivery/2925.md b/dev/programme/delivery/2925.md
index e72d70236..fc798a33b 100644
--- a/dev/programme/delivery/2925.md
+++ b/dev/programme/delivery/2925.md
@@ -1 +1 @@
-- [#2925](https://github.com/tvofi/heatpump_optimizer/pull/2925) — **open**, rca(R10-RCA-PREPR-HEAD-GRADERS): root-cause record for a pinned grader the branch edits, graded by CI with the base's copy (R10-RCA-PREPR-HEAD-GRADERS)
+- [#2925](https://github.com/tvofi/heatpump_optimizer/pull/2925) — **merged `08f26aa`**, rca(R10-RCA-PREPR-HEAD-GRADERS): root-cause record for a pinned grader the branch edits, graded by CI with the base's copy.
diff --git a/dev/programme/delivery/2962.md b/dev/programme/delivery/2962.md
index 7384d702f..d2eb0e70a 100644
--- a/dev/programme/delivery/2962.md
+++ b/dev/programme/delivery/2962.md
@@ -1 +1 @@
-- [#2962](https://github.com/tvofi/heatpump_optimizer/pull/2962) — **open**, review_packet: leave the seat mutant harness to #2959 (R10-FLY-PACKET-RED-PATHS)
+- [#2962](https://github.com/tvofi/heatpump_optimizer/pull/2962) — **merged `cc930cd`**, review_packet: leave the seat mutant harness to #2959 (R10-FLY-PACKET-RED-PATHS).
diff --git a/dev/programme/delivery/2987.md b/dev/programme/delivery/2987.md
index 3c77db81e..05a2bb24e 100644
--- a/dev/programme/delivery/2987.md
+++ b/dev/programme/delivery/2987.md
@@ -1 +1 @@
-- [#2987](https://github.com/tvofi/heatpump_optimizer/pull/2987) — **open**, triage: s8 batch 70 (P304 ruling) (R10-TRIAGE-S6)
+- [#2987](https://github.com/tvofi/heatpump_optimizer/pull/2987) — **merged `cf4f6b7`**, triage: s8 batch 70 (P304 ruling).
diff --git a/dev/programme/delivery/2992.md b/dev/programme/delivery/2992.md
index 6480f475a..31b5464d5 100644
--- a/dev/programme/delivery/2992.md
+++ b/dev/programme/delivery/2992.md
@@ -1 +1 @@
-- [#2992](https://github.com/tvofi/heatpump_optimizer/pull/2992) — **open**, R10-TRAIN-OVERLAP-GRADE part 3: park a base-policy refusal with its read reason; record-PR sweep on refusal and after a critical-path entry (R10-TRAIN-OVERLAP-GRADE)
+- [#2992](https://github.com/tvofi/heatpump_optimizer/pull/2992) — **merged `e035c66`**, R10-TRAIN-OVERLAP-GRADE part 3: park a base-policy refusal with its read reason; record-PR sweep on refusal and after a critical-path entry.
diff --git a/dev/programme/delivery/2994.md b/dev/programme/delivery/2994.md
index 5e5337854..8de7f4eb1 100644
--- a/dev/programme/delivery/2994.md
+++ b/dev/programme/delivery/2994.md
@@ -1 +1 @@
-- [#2994](https://github.com/tvofi/heatpump_optimizer/pull/2994) — **open**, R10-FLOW-DESIGN-STAGES: mechanise the design and design-review steps (R10-FLOW-DESIGN-STAGES)
+- [#2994](https://github.com/tvofi/heatpump_optimizer/pull/2994) — **merged `ca0a6cf`**, R10-FLOW-DESIGN-STAGES: mechanise the design and design-review steps (R10-FLOW-DESIGN-STAGES).
diff --git a/dev/programme/delivery/2995.md b/dev/programme/delivery/2995.md
index 13323c608..225786c7a 100644
--- a/dev/programme/delivery/2995.md
+++ b/dev/programme/delivery/2995.md
@@ -1 +1 @@
-- [#2995](https://github.com/tvofi/heatpump_optimizer/pull/2995) — **open**, R10-FLY-GH-READ-RETRY: ghapi: a GET retries a transport failure like a 5xx (R10-FLY-GH-READ-RETRY carry 7, #2859) (R10-FLY-GH-READ-RETRY)
+- [#2995](https://github.com/tvofi/heatpump_optimizer/pull/2995) — **merged `166647f`**, R10-FLY-GH-READ-RETRY: ghapi: a GET retries a transport failure like a 5xx (R10-FLY-GH-READ-RETRY carry 7, #2859) (R10-FLY-GH-READ-RETRY).
diff --git a/dev/programme/delivery/3001.md b/dev/programme/delivery/3001.md
index d9b19732b..edf4b61d7 100644
--- a/dev/programme/delivery/3001.md
+++ b/dev/programme/delivery/3001.md
@@ -1 +1 @@
-- [#3001](https://github.com/tvofi/heatpump_optimizer/pull/3001) — **open**, R10-ORCH-PLANPAGE: plan page published by state_docs, UNAVAILABLE on refusal (R10-ORCH-PLANPAGE)
+- [#3001](https://github.com/tvofi/heatpump_optimizer/pull/3001) — **merged `3a9eca6`**, R10-ORCH-PLANPAGE: plan page published by state_docs, UNAVAILABLE on refusal (R10-ORCH-PLANPAGE).
diff --git a/dev/programme/delivery/3003.md b/dev/programme/delivery/3003.md
index c72032257..4ea9d9b06 100644
--- a/dev/programme/delivery/3003.md
+++ b/dev/programme/delivery/3003.md
@@ -1 +1 @@
-- [#3003](https://github.com/tvofi/heatpump_optimizer/pull/3003) — **open**, triage: s8 batch 73 (P307 ruling) (R10-TRIAGE-S6)
+- [#3003](https://github.com/tvofi/heatpump_optimizer/pull/3003) — **merged `c098261`**, triage: s8 batch 73 (P307 ruling).
diff --git a/dev/programme/delivery/3008.md b/dev/programme/delivery/3008.md
new file mode 100644
index 000000000..e516fe7b7
--- /dev/null
+++ b/dev/programme/delivery/3008.md
@@ -0,0 +1 @@
+- [#3008](https://github.com/tvofi/heatpump_optimizer/pull/3008) — **open**, record: delivery rows (autofix)

