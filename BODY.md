Draft pass of R10-CLOSEOUT-PREP deliverable 1 (carry-file destinations), handed off ahead of the open groups; a short final pass adds what merges after this. Part of the closure check; deliverable 2 (dev/README.md) and carry 2 are not in this pull request.

Removes what a landed commit answers: `carry-1774.json` (its own brief records the discharge: R9-EG-A4, 4efdd6cea1) and `carry-201.json` entry 5 (prepare_baseline.sh now carries the files tests/entities.py opens, 57a47dd9aa and d176dd1435). Their closure-table lines go with them.

Not closed, listed for the final pass: carry-1645 is answered (both anchor lookups guarded, 16e8fef927; `tests/doc_claims.py` passes) but deleting it edits `LEGACY_CONTROL_FILES` in the pinned grader `tools/policy/brief_lint.mjs`, which `ci_predict` reads as BOOTSTRAP, so it needs a grader-only part first. carry-2065 (`min3_running_folded` reads 3/15), carry-2066 (`selfmod_independent_4kw` reads 0.789), carry-2075 (the file branch of `app_approve.sh` still excludes a bot_paths file whole), carry-1922 (canon and `tests/layout.py` GUARD_EXEMPT still live) and the remaining 23 entries of carry-201 are unanswered and still lack a roster group as destination; this draft does not assign them.

## Head

071f551147a95b22b8591f2a0cb354e1fac6342f, on origin/main 6e100ef6980216a81eaa0438bdc215d62b19271f (unmoved since the cut, so no second prepr run).

## Mutation proof

n/a: data files only, no production line.

## Null control

At the merge base `PYTHONPATH=tests/hastub python3 tests/entities.py` passes; with only the two carry files deleted it fails `inert_reads` and one scoped-path check, which the closure-table lines removed here restore (head: all entity checks pass).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
