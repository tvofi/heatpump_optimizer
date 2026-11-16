Part 2 of 4 of R11-PRE-ACK-COMPLETION: builds carries 5-9 (P541 red_brief log fallback, P574 cap line, P578 design-review line, P634 FIRED prefix, P657 carried verdict). Carry 7 (the DESIGN-REVIEW OWED line, its FAMILY and key entries and its pins) was already built by part 1 on main (`ledger.design_reviews_owed`, `tick design_builds`), so this diff holds no code for it; its self-test arm runs green at this head. Carries 0-4 and 10-17 are later parts and answered here by none.

## Head

e88651b6978180777cd28f553e9f71ad1530c084

## Mutation proof

- Carry 8: restoring the column-0 `STAMP` match in `verdict_audit.py` turns "FIRED-prefixed fire inside 12 h..." and "'- FIRED' prefix..." red in `verdict_audit.py --self-test`.
- Carry 6: restoring an `OWED` prefix on the cap line turns "the cap line counts the held refs" and "the cap line is no owed-family line, and every family line the section emits keys" red in `orchestrator_tick.py --self-test`.
- Carry 9: replacing the `_carries` call with `False` (marker `mut:carriedverdict`) turns "P657: a red PR whose head carries an older merge verdict is verdicted" red.
- Carry 5: disabling the empty-output branch (marker `mut:redlog`) turns both "P541" arms red.

## Null control

- Carry 8: the same FIRED line aged 13 h is not held, a stampless FIRED line is ignored.
- Carry 6: exactly CAP_ORPHANS stranded refs print no cap line and none of the board is UNREADABLE; an OWED-prefixed summary stays Unreadable in owed_unactioned.
- Carry 9: the same PR with the carry predicate refusing still prints `OWED red-unowned #95`.
- Carry 5: a check-run with its own output makes no job-log read.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 0 failed at this head.
- `python3 tools/audit/seat/verdict_audit.py --self-test` and `python3 tools/audit/seat/owed_unactioned.py --self-test`: 0 failed.
- `python3 tests/structure.py`: RATCHET PASSED, no budget touched.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL ENTITY CHECKS PASSED (the scoped gate's one script).

Closure: the tick self-test now reads owed_unactioned.py, so it joins `INERT_EXCEPT` in tests/closure.py and tests/entities.py's recorded closure in tests/closures.json (re-recorded with `derive_closures.sh --single` record-only then `closure.py merge --partial --allow-failures`, the one failure being the classification check this very change cured; entities.py then passes whole).

Design choice (carry 6): the writer stops opening with `OWED`, and the earlier reader-side `CAP_NOTICE` skip in `owed_unactioned.py` is deleted, because the carry rejects coupling the reader to the writer's prose.

prepr: passed rc=0 at e88651b6978180777cd28f553e9f71ad1530c084

## Red checks

none

## Forward-carry

none

## Friction

none
