fix(nightly): post the record review before the train hold (R10-RECORD-HOLD-APPROVE)

Record PRs deadlock under back-to-back trains (V118; triage: dev/programme/triage/s6-batch34.md#P198). In `.github/workflows/nightly.yml`'s step "Approve and merge a row-only record pull request" (`id: automerge`), the train-hold block ran before `guard` and the approver App's review. `merge_train.py`'s `--bot-prs` sweep merges on `record_row.py`'s guard alone and leaves that review to the beat. So while trains ran back to back, no beat posted the review and the record PR waited at REVIEW_REQUIRED. Instance: #2856 at b6de9fad, about 3 h, nightly run 40300518367 `skip-train-hold`; worked around by a hand approval (review 5650544835).

Change: the hold block (`HOLD_REF=train-hold` through its `fi`, with its comment) moves to after the approver App's review and before THE PITCH. A held beat now reads the head, runs the guard, dismisses on refusal (`refused`), posts the one approving review per head, and exits `skip-train-hold` without merging. The hold still keeps every merge off a live train: only the merge moves main, and the merge still comes after the hold. The hold comment now states its position and why. THE PITCH's comment ("Behind the train hold ... after the guard and the approval") stays true under the new order. `merge_train.py` is unchanged. `nudge.md` section 6 ("by hand only when ... a `skip-` other than `skip-train-hold`") and `dev/README.md`'s train-hold line stay true and are unchanged.

Alternatives: the filed arm (a), the train posting the approver review itself, is REJECTED per the triage. It adds a second approval site, puts the approver key into the train and touches a hot file. A reorder inside one step is the smallest sound fix.

Tests, over `tests/entities.py`'s executed `_train_hold_status` harness. The harness gains `green_rc` (the green wait's exit), `reviews` (the reviews read) and `run` (a mutant step text). A wrapper `_hold_calls` returns (status, reviewed, dismissed, merged) from the stubbed curl log.
- A live hold with the guard passing returns `skip-train-hold`, records the approver POST, and calls no merge. This replaces the old "skips while a live merge train holds" check, which ran at `guard_rc=1` and was misnamed `tests.yml`.
- A live hold with the guard refusing returns `refused`, dismisses the bot's older approval, and posts no review.
- An in-test mutant moves the hold back ahead of the head read, the guard and the review. It is built from the step's own text and returns `skip-train-hold` with no review. A mutant that cannot be built is red.
- The hold's null controls (stale, future-dated, 422, 404, 500, an unreadable body) now run at `guard_rc=0`, so the hold is reached at all. Their expectations are unchanged.
- Null: no hold, or a stale one, with the green wait passing → reviewed, `merged`.
- The pitch check's live-hold arm keeps `skip-train-hold`. Its title and comment now state the new order.

## Head

1224b42d35314d7e73b7cfec0431137daa39e493, cut from origin/main 0b8f8b585daf6a84ae9470389a709d5fec2a4f47.

## Mutation proof

The fix's production change is the block's position, so the mutant is the pre-fix order: `git show origin/main:.github/workflows/nightly.yml > .github/workflows/nightly.yml`, then `PYTHONPATH=tests/hastub python3 tests/entities.py`, then restore. It printed `3 of 2470 ENTITY CHECKS FAILED`, and all three were the new checks:
- `FAIL nightly.yml's automerge reviews a record pull request the guard passes under a live merge train hold, then skips the merge (executed, issue #2302, V118)  [bound=3600, (status, reviewed, dismissed, merged)=('skip-train-hold', False, False, False); ...]`
- `FAIL and under a live hold a head the guard refuses is refused, its approver App approvals dismissed and no review posted  [(status, reviewed, dismissed, merged)=('skip-train-hold', False, False, False)]`
- `FAIL and the hold moved back ahead of the review leaves the held head unreviewed, so the reviewed-under-a-live-hold check sees it (mutant)  [order ok=False, mutant ...=None]`

The in-test mutant is the same mutation applied to the head's step text. At the head it reads `('skip-train-hold', False, False, False)`, and the reviewed-under-a-live-hold check requires `True` there.

## Null control

At the head, no hold (422) or a stale hold, with the guard and the green wait passing, returns `('merged', True, False, True)`: reviewed, then merged, as before the fix. The hold's six non-skipping arms still return `refused`, and only the two unreadable arms warn. `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head printed `ALL 2470 ENTITY CHECKS PASSED`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at 1224b42d: `ALL 2470 ENTITY CHECKS PASSED` (the count is the script's own total line).
- The same command with `.github/workflows/nightly.yml` replaced by `git show origin/main:.github/workflows/nightly.yml`: `3 of 2470 ENTITY CHECKS FAILED`, the three named under Mutation proof.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL`, reason `.github/workflows/nightly.yml changes the gate itself`. That is a gate-file diff, not an instruction to reproduce CI (fixer.md step 5). The changed script's closure, `tests/entities.py`, was run above.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Class rule (fixer.md step 8): the step's exits that end the beat before the review are read in the step's own order (`grep -n "say \|exit 0" ` over the `automerge` step). Before the review there are only `skip-unread` (the head is unreadable, so there is nothing to review) and `refused` (the guard refuses, so no review is wanted). `skip-train-hold`, `skip-pitch`, `approved-pending` and the merge outcomes all come after it. Every exit is dispositioned: no early exit is left that skips a review the sweep needs.

## Red checks

none

## Forward-carry

none

## Friction

none
