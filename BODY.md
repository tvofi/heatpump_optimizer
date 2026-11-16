R11-START-EVALUATION-LAND (part 2): grade the loop-ledger instrument page

`tools/audit/seat/instruments/loop_ledger.py.md` reached main in pull request 3657 (30d545ce63) after revision 4 of the start evaluation, so `python3 -I tools/audit/check_scopes.py --repo . --ref 92d38ecb64 --round 11` refused the record with `has no keep/change/remove verdict for tools/audit/seat/instruments/loop_ledger.py.md`. This adds that one row to `dev/audit/yardstick/round11/EVALUATION.json`, with a `revision_5` block recording the change, as revision 4 did for its four rows. No existing verdict, card, `decision`, `ruling`, `merged` or `gates_finders` moves.

Verdict: `keep`. The yield is NO-READ, as for every sibling instrument page, because no refusal is logged with its outcome (card E11-N-INSTRUMENT-YIELD). Cost read from `instrument_cost.py` at 92d38ecb64: `tools/audit/seat/loop_ledger.py` 353 lines, 0 at the window's start, 0 merges and 0 roster groups in the window. The page's claims were checked against the script. The seven fields are `roster_lib.CONVERGENCE_FIELDS`, and all are in `roster_edit.py`'s `SET_FIELDS`. The vocabularies match `FOUND_BY`, `CAUSES`, `CM_KINDS` and `convergence_why`. The owing rules match `loop_ledger.owed`, and scorecard's E line calls `owned_split`. `--self-test` printed 21 ok and 0 failed (rc 0). A live run printed `unread (k of n ...)` wherever an owing group is unrecorded, as the page says. `tools/audit/seat/loop_ledger.py` itself is no object of objective.json's globs (only `tools/audit/seat/instruments/*.md`), so it needs no row.

## Head

bb917b8a997519ee240d9f47b11f93ccad99c549

Measurement: `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD --round 11`.
- At 92d38ecb64 (before): FAIL, 11 gaps. The missing-verdict line, then the ten `accepted and not merged` lines (E11-N-P744-SCOPE, E11-U1, U2, U4 to U10).
- At bb917b8a99 (after): FAIL, 11 gaps. The missing-verdict line is gone. The ten `accepted and not merged` lines are byte-identical. One line is new: `at review sha 83dc948818... is missing or graded other objects than this record`. check_scopes.py compares the record's `objects` with those at the review sha, so any added row raises this line until a reviewer approves at a commit that holds the row. That delta review is owed (`revision_5.review_owed`). The evaluator cannot clear it.

Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` -> `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, 4 test scripts passed, rc 0. prepr was not run.

## Mutation proof

n/a: a record-only change with no code or check. The refusal it answers is check_scopes.py's own `an object with no verdict is refused` self-test arm.

## Null control

On the unmodified tree (92d38ecb64), check_scopes.py prints the missing-verdict line and the ten `accepted and not merged` lines. After this change, those ten lines are unchanged and the PARALLEL list (12 cards) is unchanged.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
