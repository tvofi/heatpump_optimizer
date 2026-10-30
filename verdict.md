Fix review: merge f45a551f4ac270511bcfbe70cdad54b9fb798b19

bus-nonce: 535b9553ea84553cff003e0c5ed07fde

## Findings

none

## Evidence

- RESULT head measured: f45a551f4ac270511bcfbe70cdad54b9fb798b19 (PR head at post time; base e77418f, equal to origin/main).
- RESULT diff: 5 files, only dev/programme/delivery/<N>.md row files (2973, 2975, 2991, 2993 rewritten from open to merged; 2996 added). Each is one line anchoring its own PR number. The merge SHAs 1afdef8, 507a9ec, 1687630 and e77418f are all "Merge pull request #N" commits on origin/main for the matching PR numbers.
- RESULT tests/delivery_status.py at head: OK, 97 rowed, 0 pending, 0 overdue.
- RESULT merge-tree --write-tree origin/main head: exit 0, no conflict (ev/merge-tree.txt).
- RESULT VERSION, manifest and RELEASE_NOTES untouched; no claim, golden, budget or closure file in the diff.
- RESULT roles diff against origin/main is empty, so the contract is current.
- RESULT mutation proof and null control: n/a, since there is no production or test code in the diff. A diff of this kind draws no mutant.
- RESULT checks on this head (check-runs API): no red check. gate, pr-contract, budget-raise-gate, mutation, closures, fast, typing, hassfest, validate-hacs and the codeql lanes are all success; the rest are skipped.
- RESULT the body's Red checks section answers record, nightly-status and delivery-status, none of which is red on this head. Forward-carry is none, as expected for a record-only diff.
- RESULT carry_audit at head: 0 findings. figure_lint: 1 resolved.
