Fix review: merge 03112803f2909f58ea48218e682b89c111d14149

bus-nonce: b93affcd46a1873f1223a7e9e47ddca2

Round 1. Record PR (triage s8 batch 76): two files added, `dev/programme/triage/s6-batch76.md` and `dev/programme/delivery/3018.md`. No production code, VERSION, manifest or notes heading touched, so mutation, finder-harness and claim-file steps do not apply.

## Findings

- The P312 and P313 Cost entries do not give a `--budgets` row for the capped file they name (`merge_train.py`, 6703 lines), though proposal-triage.md asks for each capped file's row; only 7 of 77 batch files carry one, and no check enforces it. Not blocking. Carry: dismissed: the carry text's own PR will measure `--budgets` when it edits the file, and the ruling's verdicts do not turn on it.

## Evidence

- RESULT P312 ACCEPT: `roster_edit.ruling_verdict` on the head's batch file returns ACCEPT for P312 and DEFER for P313. `triage_refusal` with the carry citing `triage: dev/programme/triage/s6-batch76.md#P312` returns None (passes).
- RESULT line cites at 437f1ba9b: `merge_train.py:1273` is `def _critical`, `:2892` is `def queue_take`, file is 6703 lines. All match the ruling. No `priority` handling exists in the spool today, so the `--priority N` addition is new, as the ruling says. `queue_take` drains the whole spool into one batch, as described.
- R10-TRAIN-OVERLAP-GRADE exists as a group (a harness for it is in the tree) and the carry text is the ruling's own, narrowed to the drain, with a self-test row set and one mutant; it agrees with ACCEPT narrowed and with the REJECTED alternatives. P313 names no roster op, consistent with DEFER.
- Could not re-derive: `seat-ledger.md:2718` and `:1770`, the "16 of 41" train-log figure, the 73 s brief_lint time and the 223 handoff-body tips, all on the orchestrator's machine or on refs I did not walk. They are quoted, not verified here.
- review_packet carry_audit: 0 findings; figure_lint: 3 resolved, 1 not verified (`git log -1 08765983a`).
- Merge with origin/main: `git merge-tree --write-tree` exit 0, no conflict (ev/merge-tree.txt).
- CI at this head: `merge_train.py classify` exit 0, GREEN, nothing pending (ev/classify.txt). Includes tests / briefs, closures, fast, mutation, coverage, instrument-self-tests, delivery-status, budget-raise-gate.
- Head still 03112803f2909f58ea48218e682b89c111d14149 when posted.
