# Review packet #3851
head: c0c6a9b7c231a95c00ca67062aed0b1da6f20233
base: c0c6a9b7c231a95c00ca67062aed0b1da6f20233

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137199392280 success
arch-score id=137208306144 skipped
arch-score / arch-score id=137208255219 success
arm id=137199030635 success
budget-raise-gate id=137208286514 skipped
budget-raise-gate / budget-raise-gate id=137208254672 success
cancel-superseded id=137208304186 success
codeql id=137208264056 skipped
codeql / Analyze (actions) id=137208254579 success
codeql / Analyze (javascript-typescript) id=137208254697 success
codeql / Analyze (python) id=137208255157 success
gate id=137208263170 success
governance id=137208292459 skipped
governance / env-matrix id=137208255452 success
governance / instrument-self-tests id=137208255463 success
governance / policy-docs id=137208255158 success
governance / record id=137208254771 skipped
governance / wave-script id=137208254567 success
hassfest id=137208263909 skipped
hassfest / hassfest id=137208254508 success
kernel-points id=137208292354 skipped
pr-contract id=137208264026 skipped
pr-contract / pr-contract id=137208256813 success
prelude id=137208282765 success
refresh id=137208276587 success
sweep-self id=137208530100 skipped
tests id=137208263652 skipped
tests / arch-instrument id=137208255718 success
tests / briefs id=137208255429 success
tests / browser id=137208255671 success
tests / ci-ratchet id=137208256147 skipped
tests / claims-autofix id=137208255487 skipped
tests / closure-scope id=137208255167 success
tests / closures id=137208255611 success
tests / closures-autofix id=137208256462 skipped
tests / coverage id=137208255664 success
tests / coverage-ratchet id=137208255783 success
tests / fast (3.14) id=137208255426 success
tests / graders-head-copy id=137208256077 success
tests / lane-proofs id=137208255966 success
tests / mutation id=137208255149 success
tests / mutation-autofix id=137208255841 skipped
tests / mutation-pins id=137208255341 skipped
tests / nightly-ha id=137208255412 skipped
tests / nightly-status id=137208254687 success
tests / replay id=137208255677 skipped
tests / typing id=137208255180 success
validate id=137208263930 skipped
validate / validate-hacs id=137208255297 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: no `## Figures` section -- `policy_lint.mjs --pr-body` is the check that refuses that

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
