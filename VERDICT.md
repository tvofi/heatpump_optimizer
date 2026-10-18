Fix review: merge 6f42b729a8e6546733e4ab83d3b569692fcc7b31

bus-nonce: d830280869f991d92c756168cec2e002

Round 1. Measured head 6f42b729a8e6546733e4ab83d3b569692fcc7b31 (code head 89ad03e2d + the delivery row only); re-read before posting, unmoved. Roles diff vs origin/main empty.

## Carry of the orphaned handoffs
- handoff/r10-pre-edit-hook 6d0df376: `git diff 6d0df376 HEAD -- .claude/hooks/pre-edit.sh` is empty. Its fix commit e8adc1b56 is already on main via #2323; the one lost self-test row (5aff61f38) is the PR's only hook line.
- handoff/r10-earlycutoff-coverage ecaf178c: its +52 lines in tests/features.py are byte-identical to the PR's features.py hunk (diffed the +/- lines of both). Nothing dropped or altered.
- PR diff vs merge base d79dd4952: 3 files (pre-edit.sh +1, features.py +52, delivery/2397.md +1). VERSION, manifest and notes heading untouched.

## Mutation proof (reviewer's run)
Slice instrument is mine, not the fixer's: evidence/reviewer-slice.py (features.py header + coordinator _Coord/_FakeEntry imports + pump-arbiter fixtures + the whole early cut-off section, run through features_block.block()). features_block.py alone on that section dies with NameError _PaCoord (evidence/features_block-unsliced-NameError.txt), so you need a fixture slice. Mine holds 60 checks. The body's slice holds 45 under its own definition, and I could not re-derive that 45.
RESULT slice head: ALL 60 SLICE PASSED
RESULT m1 delete `held.wiring = None` (detach): 3 of 60 FAILED, both new detach checks plus the existing gc check, as the body claims
RESULT m2 `_changed` guard -> `if True:`: 1 of 60 FAILED, only "a room event after detach is a no-op..." (AttributeError)
RESULT m3 drop `or held.wiring is None` (allow_on): 1 of 60 FAILED, only "allow_on returns the plan's value..." (AttributeError)
RESULT m4 (reviewer-added) detach without release(): 2 of 60 FAILED, the existing listener check plus the new detach check
RESULT hook mutant (non-dict entry empties parts): 21 passed, 1 failed, FAIL "a non-object entry does not hide a heading beside it"
RESULT restored: hook 22 passed 0 failed; slice ALL 60 PASSED
The null control (an undetached record cuts) passes at head, so the guard check is not vacuous.

## Head / CI
The body's ## Head names 6f42b729a and says what that commit adds (the row only) over code head 89ad03e2d. It matches the measured head.
check-runs at 6f42b729a (API, evidence/check-runs-final.txt): every run concluded. None failure, none cancelled. closures, lane-proofs, composed-proof, coverage-ratchet, fast, mutation, pr-contract all success. The cancelled runs at 89ad03e2d were superseded by the row push, not red. No red check is owed an answer. mutation green: the diff writes no production line, so no mutant is drawn; my targeted mutants above stand in.
merge-tree vs origin/main: exit 0, no conflict.
Class/enumeration: the test-only carry of two named rows has no seam class to open. Forward-carry: none, and none is owed. No budgets or ledgers moved.
