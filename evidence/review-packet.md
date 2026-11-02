# Review packet #3155
head: 7dc1c501a4dcd18f8a54383295a9d873880cf244
base: 0166aefd7047b98e275bc0ab4e604fac3a7c75c6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125012250354 success
arch-score / arch-score id=125011499896 success
arm id=125010925723 skipped
budget-raise-gate / budget-raise-gate id=125011499968 success
cancel-superseded id=125010920098 skipped
codeql / Analyze (actions) id=125011500053 success
codeql / Analyze (javascript-typescript) id=125011499931 success
codeql / Analyze (python) id=125011499925 success
governance / delivery-status id=125011499994 success
governance / delivery-status-publish id=125011501818 skipped
governance / env-matrix id=125011499921 in_progress
governance / instrument-self-tests id=125011500019 in_progress
governance / policy-docs id=125011499997 success
governance / record id=125011501404 skipped
governance / wave-script id=125011499990 success
hassfest / hassfest id=125011499972 success
kernel-points id=125011501286 skipped
prelude id=125010918638 in_progress
refresh id=125010918904 success
tests / arch-instrument id=125012579044 in_progress
tests / briefs id=125011499940 success
tests / browser id=125012579058 queued
tests / closure-scope id=125011500040 success
tests / closures id=125012579103 queued
tests / coverage id=125012579968 skipped
tests / coverage-ratchet id=125012580967 skipped
tests / fast (3.14) id=125012579022 in_progress
tests / graders-head-copy id=125012579458 queued
tests / mutation id=125011499974 success
tests / mutation-autofix id=125012674259 skipped
tests / mutation-pins id=125012673727 skipped
tests / nightly-ha id=125012580095 skipped
tests / nightly-status id=125011499945 success
tests / replay id=125012580314 skipped
tests / typing id=125012579041 success
validate / validate-hacs id=125011499871 success

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
diff --git a/dev/programme/delivery/3047.md b/dev/programme/delivery/3047.md
index 18a8adfb5..9dca796d6 100644
--- a/dev/programme/delivery/3047.md
+++ b/dev/programme/delivery/3047.md
@@ -1 +1 @@
-- [#3047](https://github.com/tvofi/heatpump_optimizer/pull/3047) — **open**, R10-FACTORY-RESET: factory reset (R10-FACTORY-RESET)
+- [#3047](https://github.com/tvofi/heatpump_optimizer/pull/3047) — **merged `f04b25a`**, R10-FACTORY-RESET: factory reset (R10-FACTORY-RESET).
diff --git a/dev/programme/delivery/3050.md b/dev/programme/delivery/3050.md
index b443deed0..032e62142 100644
--- a/dev/programme/delivery/3050.md
+++ b/dev/programme/delivery/3050.md
@@ -1 +1 @@
-- [#3050](https://github.com/tvofi/heatpump_optimizer/pull/3050) — **open**, R10-CEILING-PROBE: ceiling probe (R10-CEILING-PROBE)
+- [#3050](https://github.com/tvofi/heatpump_optimizer/pull/3050) — **merged `0166aef`**, R10-CEILING-PROBE: ceiling probe (R10-CEILING-PROBE).
diff --git a/dev/programme/delivery/3118.md b/dev/programme/delivery/3118.md
index 8c45a99fc..2a47fdf85 100644
--- a/dev/programme/delivery/3118.md
+++ b/dev/programme/delivery/3118.md
@@ -1 +1 @@
-- [#3118](https://github.com/tvofi/heatpump_optimizer/pull/3118) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster (host paths scrubbed) (R10-ROSTER-OPS)
+- [#3118](https://github.com/tvofi/heatpump_optimizer/pull/3118) — **merged `6d5c235`**, roster: land the round-10 roster from handoff/audit-r10-roster (host paths scrubbed).
diff --git a/dev/programme/delivery/3141.md b/dev/programme/delivery/3141.md
index e9fb91a79..17b369b95 100644
--- a/dev/programme/delivery/3141.md
+++ b/dev/programme/delivery/3141.md
@@ -1 +1 @@
-- [#3141](https://github.com/tvofi/heatpump_optimizer/pull/3141) — **open**, triage: s9 batch 103 (R10-TRIAGE-S6)
+- [#3141](https://github.com/tvofi/heatpump_optimizer/pull/3141) — **merged `7f849a2`**, triage: s9 batch 103.
diff --git a/dev/programme/delivery/3142.md b/dev/programme/delivery/3142.md
index ce18de988..0607d261c 100644
--- a/dev/programme/delivery/3142.md
+++ b/dev/programme/delivery/3142.md
@@ -1 +1 @@
-- [#3142](https://github.com/tvofi/heatpump_optimizer/pull/3142) — **open**, triage: s9 batch 104 (R10-TRIAGE-S6)
+- [#3142](https://github.com/tvofi/heatpump_optimizer/pull/3142) — **merged `a2d8797`**, triage: s9 batch 104.
diff --git a/dev/programme/delivery/3155.md b/dev/programme/delivery/3155.md
new file mode 100644
index 000000000..84fe2f8f7
--- /dev/null
+++ b/dev/programme/delivery/3155.md
@@ -0,0 +1 @@
+- [#3155](https://github.com/tvofi/heatpump_optimizer/pull/3155) — **open**, record: delivery rows (autofix)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
