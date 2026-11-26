Fix review: blocked fe2b516c710e65e281f870131b08f95897c6297d ci-red: required gate RED at this head; tests / closures UNDER-SCOPED, tests/entities.py reads tools/ci/shards.py its closure omits

bus-nonce: 575416be850ffa5787851e6e1f8a88d8

## Block

Delta round over 791d83e7..fe2b516c710e65e281f870131b08f95897c6297d (one commit, 4c267409, tools/ci/selftest_closures.json only). The previous block is resolved (see Evidence), but the head is not green: merge_train.py classify reads `RED fe2b516c710e65e281f870131b08f95897c6297d pending: none red: gate` (rc 1). The owed red `tests / closures` names a stale closure this PR causes: `UNDER-SCOPED: tests/entities.py really reads 1 file(s) the committed closure does not list: tools/ci/shards.py`. tools/ci/shards.py is new in this PR; tests/closures.json at the head lists nine tools/ci/ files for tests/entities.py and not shards.py. `tests / closures-autofix` also failed, so no bot commit is coming (ci-autofix.md). Repair: `./tests/derive_closures.sh --single tests/entities.py` on Linux, commit tests/closures.json, and re-run the closures check. `tests / fast (3.14)` is red too (`1 TEST SCRIPT(S) FAILED`) at this head; its failing script must be named and answered at the repaired head.

## Red checks

- tests / closures: PR-caused (an under-scoped closure for tests/entities.py over tools/ci/shards.py); this is the block.
- tests / fast (3.14): red, `1 TEST SCRIPT(S) FAILED`; I did not identify the script from the log tail I read, so it is unattributed. It must be named at the next head.

## Findings

- tests/entities.py's closure in tests/closures.json omits tools/ci/shards.py, which CI's recording reads (tests / closures job 139713900560). The fixer owns this inside the PR. Carry: dismissed: settled inside #3902 by its own fixer before the next review round, the block above

## Evidence

- Previous finding (791d83e7: ci-shards missing from tools/ci/selftest_closures.json) is resolved. `python3 tools/ci/selftest_scope.py static` at the head: `129 gated step(s), 0 problem(s)`, rc 0 (ev/static-head.txt). Null control with 791d83e7's table: `STALE ... missing ['ci-shards']`, `1 problem(s)`, rc 1 (ev/static-null-old-table.txt).
- `selftest_scope.py grows --old <791d83e7 table> --new <head table>`: `0 read(s) of the old table the new one drops`, rc 0 (ev/grows.txt). The delta also widens policy-lint-mutants' probes from carries/.gitattributes, carry-1645.json and carry-201.json to carries/**. That is a superset, and grows agrees.
- Mutant: setting ci-shards' run_sha to zeros makes static report `run text changed since it was recorded: ['ci-shards']`, rc 1 (ev/mutant-runsha.txt). The record is bound to the step's run text.
- The fixer's figures re-taken: static rc 1 -> rc 0 with 129 gated steps and 0 problems, and grows dropping no old read. Both survive.
- `git merge-tree --write-tree origin/main fe2b516c710e65e281f870131b08f95897c6297d`: rc 0, tree bb3bda8b, no conflict; tests/closures.json is resolved by the ledger merge driver (ev/merge-tree.txt).
- classify log: WAIT from 06:14 to 06:25, then RED at 06:26:59 (ev/classify-log.txt). The red set is in ev/owed-reds.txt and ev/review-packet-final.md.
- CI log excerpts: ev/ci-red-closures.txt.
