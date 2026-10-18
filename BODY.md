Two test-only rows that reached handoff branches on 2026-10-16 but never main. Part of #201.

1. `.claude/hooks/pre-edit.sh`: self-test row "a non-object entry does not hide a heading beside it" (cherry-pick of 5aff61f38, pushed to handoff/r10-pre-edit-hook after #2323 merged at 0570b86e9; #2323's commits end at e8adc1b56, so it was lost, not dropped: `gh api repos/tvofi/heatpump_optimizer/pulls/2323/commits`, `git log -S'does not hide a heading beside it' origin/main -- .claude/hooks/pre-edit.sh` is empty).
2. `tests/features.py`: direct assertions of the #2329 release/detach path (port of ecaf178cb, 52 lines, no PR ever opened): detach clears listener and wiring; a room event after detach is a no-op through `_changed`'s guard; allow_on with no wiring returns the plan value; null control that an undetached record still cuts.

## Head

89ad03e2db1ca998da56b3f36414b96118744592 (merge of origin/main d79dd4952, 2026-10-18).

## Mutation proof

- Hook: the `isinstance(e, dict)` filter in the edits loop changed so that any non-dict entry empties the parts list: `bash .claude/hooks/pre-edit.sh --self-test` gives `FAIL a non-object entry does not hide a heading beside it (got allow, wanted refuse)`, 21 passed 1 failed; restored, 22 passed 0 failed.
- early_cutoff.py, three mutants, run on a slice of tests/features.py (early cut-off section only, 45 checks; full file left to CI per heavy-to-ci):
  - delete `held.wiring = None` in detach: FAIL "detach drops the room listener and clears the wiring...", FAIL "a room event after detach is a no-op...", and the pre-existing gc check also fails.
  - `if held.wiring is not None:` in `_changed` replaced by `if True:`: FAIL "a room event after detach is a no-op through the wiring guard, not a crash" (only the new check kills it).
  - drop `or held.wiring is None` in allow_on: FAIL "allow_on returns the plan's value when the record carries no wiring (unloaded)" (only the new check kills it).
  All restored; slice 45/45 passes.

## Null control

On unmodified origin/main neither the pre-edit row nor the three new checks exist; the existing gc/weakref pair is the only unload coverage and survives the two guard mutants. The never-detached record in the new block cuts, so the guard check is not vacuous.

## Figures

- `bash .claude/hooks/pre-edit.sh --self-test`: 22 passed, 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, RUN tests/entities.py, tests/features.py. Both are heavy and left to CI (tvofi 2026-10-18); cite the check-runs at the head.
- Slice run: features.py lines 1-91 + the _PaCoord/_Coord fixtures + the early cut-off section, 45 checks passed.

## Red checks

none known; prepr.sh not yet run (box load ~187, heavy-to-ci).

## Forward-carry

none

## Friction

none
