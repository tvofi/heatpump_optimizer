# Review packet #3844
head: 2996954eb5d19b0733b6c95fbcf75c03a7098b59
base: f269ecccb5f1dfd21eca03a3d5dcc43b3a145603

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137069049001 success
arch-score / arch-score id=137078612769 success
arm id=137054724405 skipped
budget-raise-gate / budget-raise-gate id=137078612735 success
cancel-superseded id=137078639349 success
codeql id=137078612425 skipped
codeql / Analyze (actions) id=137065500914 success
codeql / Analyze (javascript-typescript) id=137065501079 success
codeql / Analyze (python) id=137065500925 success
gate id=137078612257 success
governance id=137078612551 skipped
governance / env-matrix id=137065500974 success
governance / instrument-self-tests id=137065500956 success
governance / policy-docs id=137065500971 success
governance / record id=137065501977 skipped
governance / wave-script id=137065501034 success
hassfest id=137078643234 skipped
hassfest / hassfest id=137065500894 success
kernel-points id=137078612500 skipped
pr-contract id=137078613348 skipped
pr-contract / pr-contract id=137076100276 success
prelude id=137078612038 success
refresh id=137078636298 success
sweep-self id=137083715401 skipped
tests id=137078636460 skipped
tests / arch-instrument id=137068204038 success
tests / briefs id=137065500962 success
tests / browser id=137068204606 success
tests / ci-ratchet id=137074870880 skipped
tests / claims-autofix id=137073354255 skipped
tests / closure-scope id=137065500953 success
tests / closures id=137068204097 success
tests / closures-autofix id=137074871226 skipped
tests / coverage id=137068205089 skipped
tests / coverage-ratchet id=137068205648 skipped
tests / fast (3.14) id=137068204080 success
tests / graders-head-copy id=137068204278 success
tests / lane-proofs id=137075495499 success
tests / mutation id=137065500984 success
tests / mutation-autofix id=137068685060 skipped
tests / mutation-pins id=137068684933 skipped
tests / nightly-ha id=137068205636 skipped
tests / nightly-status id=137065500944 success
tests / replay id=137068205834 skipped
tests / typing id=137068204063 success
validate id=137078612614 skipped
validate / validate-hacs id=137065500869 success

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

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3728.md b/dev/programme/delivery/3728.md
index 32273bfc3b..b30a8f40f7 100644
--- a/dev/programme/delivery/3728.md
+++ b/dev/programme/delivery/3728.md
@@ -1 +1 @@
-- [#3728](https://github.com/tvofi/heatpump_optimizer/pull/3728) — **open**, R11-SEAM-kernel-step: one plan step kernel (R11-SEAM-kernel-step)
+- [#3728](https://github.com/tvofi/heatpump_optimizer/pull/3728) — **merged `4ebd430`**, R11-SEAM-kernel-step: one plan step kernel (R11-SEAM-kernel-step).
diff --git a/dev/programme/delivery/3729.md b/dev/programme/delivery/3729.md
index d95d02f4e1..179b19697e 100644
--- a/dev/programme/delivery/3729.md
+++ b/dev/programme/delivery/3729.md
@@ -1 +1 @@
-- [#3729](https://github.com/tvofi/heatpump_optimizer/pull/3729) — **open**, R11-SEAM-ratchets: ratchets (R11-SEAM-ratchets)
+- [#3729](https://github.com/tvofi/heatpump_optimizer/pull/3729) — **merged `f269ecc`**, R11-SEAM-ratchets: ratchets (R11-SEAM-ratchets).
diff --git a/dev/programme/delivery/3737.md b/dev/programme/delivery/3737.md
index ad60a38cb7..2673a169f6 100644
--- a/dev/programme/delivery/3737.md
+++ b/dev/programme/delivery/3737.md
@@ -1 +1 @@
-- [#3737](https://github.com/tvofi/heatpump_optimizer/pull/3737) — **open**, R11-CARRY-DRAWMAP: r11 carry drawmap (R11-CARRY-DRAWMAP)
+- [#3737](https://github.com/tvofi/heatpump_optimizer/pull/3737) — **merged `35402f7`**, R11-CARRY-DRAWMAP: r11 carry drawmap.
diff --git a/dev/programme/delivery/3814.md b/dev/programme/delivery/3814.md
index 5f1da62025..8667e19032 100644
--- a/dev/programme/delivery/3814.md
+++ b/dev/programme/delivery/3814.md
@@ -1 +1 @@
-- [#3814](https://github.com/tvofi/heatpump_optimizer/pull/3814) — **open**, audit round 11: land finder box D3-top6 (-)
+- [#3814](https://github.com/tvofi/heatpump_optimizer/pull/3814) — **merged `e4c929b`**, audit round 11: land finder box D3-top6.
diff --git a/dev/programme/delivery/3836.md b/dev/programme/delivery/3836.md
index 8ea4970e80..b6af1baf54 100644
--- a/dev/programme/delivery/3836.md
+++ b/dev/programme/delivery/3836.md
@@ -1 +1 @@
-- [#3836](https://github.com/tvofi/heatpump_optimizer/pull/3836) — **open**, roster: land the round-11 roster from handoff/audit-r10-roster 320a1ada
+- [#3836](https://github.com/tvofi/heatpump_optimizer/pull/3836) — **merged `6f6a85c`**, roster: land the round-11 roster from handoff/audit-r10-roster 320a1ada.
diff --git a/dev/programme/delivery/3844.md b/dev/programme/delivery/3844.md
new file mode 100644
index 0000000000..a0a2db73a3
--- /dev/null
+++ b/dev/programme/delivery/3844.md
@@ -0,0 +1 @@
+- [#3844](https://github.com/tvofi/heatpump_optimizer/pull/3844) — **open**, record: delivery rows (autofix)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
