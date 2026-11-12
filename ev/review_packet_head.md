# Review packet #3430
head: 9ab334ddeaf5f776cc7c33dff10d76aeca03c465
base: 6cc15e9b8f53b5393bb4ed7297bfc12747d6e2f6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130781120738 success
arch-score / arch-score id=130858846727 success
arm id=130756814183 skipped
budget-raise-gate / budget-raise-gate id=130858847388 success
cancel-superseded id=130858844939 success
codeql id=130765048112 skipped
codeql / Analyze (actions) id=130858846145 success
codeql / Analyze (javascript-typescript) id=130858846907 success
codeql / Analyze (python) id=130858846503 success
gate id=130858850869 success
governance id=130765049083 skipped
governance / delivery-status id=130858846933 success
governance / delivery-status-publish id=130858846818 skipped
governance / env-matrix id=130858846629 success
governance / instrument-self-tests id=130858846991 success
governance / policy-docs id=130858846927 success
governance / record id=130858847138 skipped
governance / wave-script id=130858847071 success
hassfest id=130765048046 skipped
hassfest / hassfest id=130858846966 success
kernel-points id=130858846848 skipped
pr-contract id=130785306175 skipped
pr-contract / pr-contract id=130858851877 success
prelude id=130858917089 success
refresh id=130858845412 success
sweep-self id=130859677435 skipped
tests id=130765048385 skipped
tests / arch-instrument id=130858848827 success
tests / briefs id=130858846924 success
tests / browser id=130858849546 success
tests / ci-ratchet id=130858852089 skipped
tests / claims-autofix id=130858850455 skipped
tests / closure-scope id=130858847206 success
tests / closures id=130858850012 success
tests / closures-autofix id=130858850439 skipped
tests / coverage id=130858849327 success
tests / coverage-ratchet id=130858849737 success
tests / fast (3.14) id=130858849174 success
tests / graders-head-copy id=130858849952 success
tests / lane-proofs id=130858850126 success
tests / mutation id=130858847691 success
tests / mutation-autofix id=130858850688 skipped
tests / mutation-pins id=130858849897 skipped
tests / nightly-ha id=130858848750 skipped
tests / nightly-status id=130858846458 failure
tests / replay id=130858848173 skipped
tests / typing id=130858848757 success
validate id=130765049263 skipped
validate / validate-hacs id=130858846740 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 6bc4f4e1: R10-ARCH-DOCS-DELTA: R10-ARCH-DOCS-DELTA resolved on origin/handoff/audit-r10-roster
NOTE body item d5ef2398: R10-ARCH-DOCS-DELTA: R10-ARCH-DOCS-DELTA resolved on origin/handoff/audit-r10-roster
NOTE body item a44d0012: R10-USER-DOCS-VERIFY
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `cloud_dispatch.py -> bus refs` 308: text of the brief the script renders for a reviewer seat, which pushes the probe ref itself (`seats -->|"writes"| bus`).
             no segment of this names a program this check knows
  unverified - `merge_train.py -> obligations ledger` 4210: a log line telling the reader to run `ledger.py close train-stop`; the train writes nothing there.
             no segment of this names a program this check knows
  unverified - `orchestrator_tick.py -> pull request` 2424: text of a board line naming `open_pr.sh` and `update_pr.sh`.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/closure.py changes the gate itself, so every closure is suspect
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_arch_docs_enumerate.py
             `dev/audit/harnesses/r10_arch_docs_enumerate.py` is in the tree at this head
  ok         gh pr
             gh pr: every long flag accepted

FIGURES: 9 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 822a3556df06781ed7a0a1e8cecd74be0a1ffd01, so there is no finding to confirm resolved)

