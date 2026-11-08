Fix review: blocked 061a828e18df8ba29a95827fb0e11cd3b7f963b4 ci-red: ledger.py KINDS lacks carry-fold; governance / instrument-self-tests and gate red at this head

bus-nonce: d67abbb036dd6528c8b90a429838adf0

## Block

- Round: not stated in the packet; the verdict history was not readable here, so the round number is unknown.
- At head 061a828e18df8ba29a95827fb0e11cd3b7f963b4, `python3 -I tools/audit/seat/ledger.py --self-test` prints `FAIL every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)` and `101 checks, 1 failed`. I reproduced it myself. The cause is the diff's own `carry_fold_arm`, which writes `level_line carry-fold`, a kind missing from `KINDS` in `tools/audit/seat/ledger.py`.
- The PR body admits the repair is still owed ("the PR must not be read as clean until it lands"). `governance / instrument-self-tests` is red at this head, the required `gate` is red, and `merge_train.py classify` prints RED (pending: none, red: gate).
- Fix: add `carry-fold` to `KINDS`, then re-take the head and the body's Red checks.
- Red checks the body does not name at this head: `tests / ci-ratchet`, `tests / coverage`, `tests / coverage-ratchet`, `tests / graders-head-copy` and `tests / lane-proofs` all concluded cancelled. The packet refuses them as red-unanswered. The body's Red checks section is about the earlier head 6b5d99b5c, so it must be re-taken at the new head. If the cancellations are only the gate's supersession, say so there.
- Merge with origin/main: `git merge-tree --write-tree origin/main HEAD` exits 0 and prints the tree 3c138aa16, so there is no conflict.

## Findings

- Follow-up: re-take the body's Red checks and Figures at the repaired head; the body quotes figures for 30986c09c, not the PR head. Carry: dismissed: owed by this block, nothing to carry beyond the re-cut

## Evidence

- Not done: the mutation proofs, the carry-audit figures and the budgets were not re-derived, because the head is red already. The figure_lint block in the packet shows 13 resolved, 0 not verified.
- Packet refusals: red-unanswered for five checks, and required-red for `gate`.
- Head: ev/HEAD.txt. Ledger self-test output: ev/ledger-selftest.txt. Classify output: ev/classify.txt.
