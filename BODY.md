Part 2 of 4 of R11-PRE-ACK-COMPLETION: builds carries 5-9 (P541 red_brief log fallback, P574 cap line, P578 design-review line, P634 FIRED prefix, P657 carried verdict). Carry 7 (the DESIGN-REVIEW OWED line, its FAMILY and key entries and its pins) was already built by part 1 on main (`ledger.design_reviews_owed`, `tick design_builds`), so this diff holds no code for it; its self-test arm runs green at this head. Carries 0-4 and 10-17 are later parts and answered here by none.

## Head

a56af234d8da872e6463859d32019398544580ff

## Repair (review round 1, block mutation-survivor)

The round-1 verdict at 5356706e02cd174793004a041059c090eb15efba blocked on survivor S1: deleting the `m.group(1) == "merge" and` conjunct of the P657 arm in `Tick._bucket` left `orchestrator_tick.py --self-test` with 0 failed. This head adds one self-test row and nothing else: PR #95, red, CLEAN, whose last line is `Fix review: blocked <h(1095)> x: y` (a non-merge verdict at an older head), with a carry predicate that accepts every pair. Expected: not bucketed `verdicted`, exactly one line, `OWED red-unowned #95`, and the carry predicate never consulted. The `m.group(2) != head and` conjunct (S2) is left as it was, per the verdict's dismissal as an equivalent mutant.

## Mutation proof

- Carry 9 guard (S1, the block): deleting `m.group(1) == "merge" and` turns "P657 merge guard: a carried *blocked* verdict at an older head is not verdicted, still RED-UNOWNED" red (375 checks, 1 failed); the row was run under the mutant before the head was restored (failing case first).
- Carry 8: restoring the column-0 `STAMP` match in `verdict_audit.py` turns "FIRED-prefixed fire inside 12 h..." and "'- FIRED' prefix..." red in `verdict_audit.py --self-test`.
- Carry 6: restoring an `OWED` prefix on the cap line turns "the cap line counts the held refs" and "the cap line is no owed-family line, and every family line the section emits keys" red in `orchestrator_tick.py --self-test`.
- Carry 9: replacing the `_carries` call with `False` (marker `mut:carriedverdict`) turns "P657: a red PR whose head carries an older merge verdict is verdicted" red.
- Carry 5: disabling the empty-output branch (marker `mut:redlog`) turns both "P541" arms red; dropping the `ANSI_ESC.sub` turns the "escapes stripped" arm red.

## Null control

- Carry 9 guard: the new row passes at this head (375 checks, 0 failed); the existing P657 arm (a merge verdict, same carry predicate) is still bucketed `verdicted`, so the row separates on the verdict kind alone.
- Carry 8: the same FIRED line aged 13 h is not held, a stampless FIRED line is ignored.
- Carry 6: exactly CAP_ORPHANS stranded refs print no cap line and none of the board is UNREADABLE; an OWED-prefixed summary stays Unreadable in owed_unactioned.
- Carry 9: the same PR with the carry predicate refusing still prints `OWED red-unowned #95`.
- Carry 5: a check-run with its own output makes no job-log read.

## Figures

The reviewer's mutants from `review/3689` `evidence/mutants.txt`, re-run at a56af234d8da872e6463859d32019398544580ff, each applied alone to a clean worktree, the owning self-test run, the file restored by `git checkout`:

| mutant | self-test result | outcome |
|---|---|---|
| M8 STAMP column-0 (`verdict_audit.py`) | 18 checks, 2 failed | killed |
| M6 cap line re-prefixed `OWED handoffs CAPPED at` | 375 checks, 2 failed | killed |
| M9 `_carries(...)` -> `False` | 375 checks, 1 failed | killed |
| M5 empty-output branch disabled | 375 checks, 2 failed | killed |
| M5b `ANSI_ESC.sub` dropped | 375 checks, 1 failed | killed |
| S1 drop `m.group(1) == "merge" and` | 375 checks, 1 failed | killed (was the survivor) |
| S2 drop `m.group(2) != head and` | 375 checks, 0 failed | survives; equivalent per the verdict, untouched |

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 375 checks, 0 failed at this head (374 at 5356706e02cd174793004a041059c090eb15efba; the one added is the S1 row).
- `python3 tools/audit/seat/verdict_audit.py --self-test`: 18 checks, 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- Gate scope (`tests/closure.py select` against the merge base): `MODE: FULL`, because `tests/closure.py` is in this PR's diff; the delta since the reviewed head is one self-test row in `tools/audit/seat/orchestrator_tick.py`, so prepr ran with `PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1` and CI is the authority for the full suite.

Closure: the tick self-test now reads owed_unactioned.py, so it joins `INERT_EXCEPT` in tests/closure.py and tests/entities.py's recorded closure in tests/closures.json (re-recorded with `derive_closures.sh --single` record-only then `closure.py merge --partial --allow-failures`, the one failure being the classification check this very change cured; entities.py then passes whole).

Design choice (carry 6): the writer stops opening with `OWED`, and the earlier reader-side `CAP_NOTICE` skip in `owed_unactioned.py` is deleted, because the carry rejects coupling the reader to the writer's prose.

prepr: passed rc=0 at a56af234d8da872e6463859d32019398544580ff

## Red checks

none

## Forward-carry

none

## Friction

none
