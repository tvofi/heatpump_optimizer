# Review packet #2897
head: a8cf7889ef2cbbb0b913d2e9f5eabb918fef5996
base: e8cb7e68302b1d350bb8219fea99e911170af030

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=122564037815 success
arch-score / arch-score id=122572047722 success
arm id=122563890495 skipped
budget-raise-gate / budget-raise-gate id=122572047599 success
cancel-superseded id=122563840768 success
codeql id=122572048876 skipped
codeql / Analyze (actions) id=122563979150 success
codeql / Analyze (javascript-typescript) id=122563979044 success
codeql / Analyze (python) id=122563979188 success
gate id=122573698417 success
governance id=122572049433 skipped
governance / delivery-status id=122563979072 success
governance / delivery-status-publish id=122563981211 skipped
governance / env-matrix id=122563979114 success
governance / instrument-self-tests id=122563979049 success
governance / policy-docs id=122563979016 success
governance / record id=122563980453 skipped
governance / wave-script id=122563979083 success
hassfest id=122572049409 skipped
hassfest / hassfest id=122563979055 success
kernel-points id=122572049161 skipped
pr-contract / pr-contract id=122572549756 success
prelude id=122563841220 success
refresh id=122563841087 success
tests id=122572049201 skipped
tests / arch-instrument id=122564104203 success
tests / briefs id=122563979215 success
tests / browser id=122564104201 success
tests / ci-ratchet id=122565585005 skipped
tests / claims-autofix id=122565585426 skipped
tests / closure-scope id=122563979391 success
tests / closures id=122564104189 success
tests / closures-autofix id=122565226422 skipped
tests / coverage id=122564106786 skipped
tests / coverage-ratchet id=122564106656 skipped
tests / fast (3.14) id=122564104439 success
tests / graders-head-copy id=122564104553 success
tests / lane-proofs id=122565582879 success
tests / mutation id=122563979149 success
tests / mutation-autofix id=122564278775 skipped
tests / mutation-pins id=122564277806 skipped
tests / nightly-ha id=122564106004 skipped
tests / nightly-status id=122563979213 success
tests / replay id=122564106098 skipped
tests / typing id=122564104152 success
validate id=122572048731 skipped
validate / validate-hacs id=122563979076 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/record_row.py --plan --merges-file <the three merges from --enumerate> --roster-ref origin/main
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         python3 tests/delivery_status.py --require-rows --repo tvofi/heatpump_optimizer --since v7.0.4
             `tests/delivery_status.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2878.md b/dev/programme/delivery/2878.md
index b04f83afb..039aecb61 100644
--- a/dev/programme/delivery/2878.md
+++ b/dev/programme/delivery/2878.md
@@ -1 +1 @@
-- [#2878](https://github.com/tvofi/heatpump_optimizer/pull/2878) — **open**, roster: round-10 batch 24 (R10-ROSTER-BATCH24)
+- [#2878](https://github.com/tvofi/heatpump_optimizer/pull/2878) — **merged `22a2c9c`**, roster: round-10 batch 24 (R10-ROSTER-BATCH24).
diff --git a/dev/programme/delivery/2888.md b/dev/programme/delivery/2888.md
index 2c1d571bc..5a7f51566 100644
--- a/dev/programme/delivery/2888.md
+++ b/dev/programme/delivery/2888.md
@@ -1 +1 @@
-- [#2888](https://github.com/tvofi/heatpump_optimizer/pull/2888) — **open**, Triage s6 batch 40: correct P211 -- the lease half is a real second carry (R10-PREPR-CAP)
+- [#2888](https://github.com/tvofi/heatpump_optimizer/pull/2888) — **merged `939f0c6`**, Triage s6 batch 40: correct P211 -- the lease half is a real second carry.
diff --git a/dev/programme/delivery/2889.md b/dev/programme/delivery/2889.md
index ca030923d..e7901f160 100644
--- a/dev/programme/delivery/2889.md
+++ b/dev/programme/delivery/2889.md
@@ -1 +1 @@
-- [#2889](https://github.com/tvofi/heatpump_optimizer/pull/2889) — **open**, record: delivery rows (autofix)
+- [#2889](https://github.com/tvofi/heatpump_optimizer/pull/2889) — **merged `6b9bf5b`**, roster_sync: a carry the destination already holds from the same pull request is not re-appended.
diff --git a/dev/programme/delivery/2897.md b/dev/programme/delivery/2897.md
new file mode 100644
index 000000000..507aaafbc
--- /dev/null
+++ b/dev/programme/delivery/2897.md
@@ -0,0 +1 @@
+- [#2897](https://github.com/tvofi/heatpump_optimizer/pull/2897) — **open**, record: rewrite the open rows of #2878, #2888, #2889 to their merges (R10-RECORDS)

