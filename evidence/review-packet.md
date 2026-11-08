# Review packet #3312
head: a5ea296904e9539dc70cd473d9b1c6d144a01f99
base: f9a9632032e619bea166af92b9afcb0c69215454

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128674826140 success
arch-score / arch-score id=128680834029 success
arm id=128674220045 skipped
budget-raise-gate / budget-raise-gate id=128680842634 success
cancel-superseded id=128680809750 success
codeql id=128680836053 skipped
codeql / Analyze (actions) id=128674777479 success
codeql / Analyze (javascript-typescript) id=128674777598 success
codeql / Analyze (python) id=128674777469 success
gate id=128680809574 success
governance id=128680836394 skipped
governance / delivery-status id=128674777448 success
governance / delivery-status-publish id=128674778498 skipped
governance / env-matrix id=128674777510 success
governance / instrument-self-tests id=128674777500 success
governance / policy-docs id=128674777516 success
governance / record id=128674778724 skipped
governance / wave-script id=128674777465 success
hassfest id=128680846331 skipped
hassfest / hassfest id=128674777554 success
kernel-points id=128680833361 skipped
pr-contract id=128680810708 skipped
pr-contract / pr-contract id=128680486194 success
prelude id=128680835411 success
refresh id=128680835413 success
tests id=128680825724 skipped
tests / arch-instrument id=128675208284 success
tests / briefs id=128674777458 success
tests / browser id=128675208240 success
tests / ci-ratchet id=128679436747 skipped
tests / claims-autofix id=128677776950 skipped
tests / closure-scope id=128674777439 success
tests / closures id=128675208223 success
tests / closures-autofix id=128678782304 skipped
tests / coverage id=128675208293 success
tests / coverage-ratchet id=128679435836 success
tests / fast (3.14) id=128675208216 success
tests / graders-head-copy id=128679435919 success
tests / lane-proofs id=128679435863 success
tests / mutation id=128674777459 success
tests / mutation-autofix id=128675038194 skipped
tests / mutation-pins id=128675037963 skipped
tests / nightly-ha id=128675209429 skipped
tests / nightly-status id=128674777471 success
tests / replay id=128675210360 skipped
tests / typing id=128675208262 success
validate id=128680809925 skipped
validate / validate-hacs id=128674777454 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item f2c2c0b2: dismissed:part 3's own scope; no later stage's brief changes
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3312.md b/dev/programme/delivery/3312.md
new file mode 100644
index 000000000..ef0b252c3
--- /dev/null
+++ b/dev/programme/delivery/3312.md
@@ -0,0 +1 @@
+- [#3312](https://github.com/tvofi/heatpump_optimizer/pull/3312) — **open**, R10-BODY-CONTRACT (part 3 bootstrap): register figure_block.py as pending in main's field-coverage registry (R10-BODY-CONTRACT)
diff --git a/tools/policy/field_coverage.mjs b/tools/policy/field_coverage.mjs
index db55a8af0..853318694 100644
--- a/tools/policy/field_coverage.mjs
+++ b/tools/policy/field_coverage.mjs
@@ -347,6 +347,7 @@ const DECLARED = {
   'pinned tools/audit/preflight.sh': { none: 'runs other checks; no input of its own' },
   'pinned tools/audit/prepr.sh': { none: 'runs other checks over a body; no input of its own' },
   'pinned tools/audit/prepare_baseline.sh': { none: 'check-wave-script reads its ISOLATED_DIMS line as text; it grades no input here' },
+  'pinned tools/pr/figure_block.py': { none: 'reads the figures a pull-request body states against the commands that produced them; graded by its own self-test, no arm here', pending: 'R10-BODY-CONTRACT part 3 pins it in governance.yml' },
   'pinned tools/audit/machinery_ratchet.py': { none: 'reads machinery_budgets.json through load_budgets(), which refuses a key it does not read and requires each it does (its --self-test pins both), and merge history; no arm here' },
   'pinned tools/audit/round6/D11/fix/codeowners_gap.py': { none: 'reads CODEOWNERS and workflows; residual (D11-s1-03), no arm here' },
   'stamp rule 4': { none: 'reads commit parents and subjects; residual (D11-s1-02), no arm here' },

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
