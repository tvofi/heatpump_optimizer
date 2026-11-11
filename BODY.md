Plan-page group r10-plan-page-residue, re-cut at round 5. Closes no issue.

## Re-cut

Round 4 blocked on one survivor: `note-replayed`, in `size_durations.run` `input_note(via, since, len(prs), replayed)` becomes `input_note(via, since, len(prs), False)`. This pass adds one self-test arm: `run` driven with `cache` pointing at a fixture `--prs-cache` file, its `rest` read set to raise if called, asserting `sizes_provenance` ends with `input_note("rest", since, n, True)`. The earlier `cache=None` runs are its null. Everything else of the round-4 body is kept, and `origin/main` is merged in (no rebase), which supplies `roster_lib.carry_receivable` the round-4 `pr-contract` red lacked.

## Head

baaf0064355bdf4838021df66683584e3d8608c7

## Mutation proof

- `note-replayed`: `input_note(via, since, len(prs), replayed)` changed to `..., False)` in `size_durations.run`. Before the arm, `size_durations.py --self-test` read `0 failed` (the survivor). With it, `1 failed`, and restored, `0 failed`.
- Each statement the arm adds, deleted once through `mutant_run.py --spec` (`python3 tools/plan/size_durations.py --self-test`, NULL `SURVIVED NULL`): the roster write, the cache write, the `run` call and the `check` call are `KILLED`, as is flipping the expected flag `True` to `False`.
- Earlier survivors `note-run`, `run-via` and `replan-via` stay killed by their arms (unchanged since round 4).
- Diff mode over every changed tool, each with its own `--self-test` through `mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --path <file>`: `size_durations.py` 8 survivors, `replan.py` 11, `plan_page.py` 3, all dispositioned in `## Unpinned sites

The diff-mode survivors, by the counts and lines the three runs printed:
- `replan.py`, production, 1 (`check_plan` closure fallback `default=0` to `default=1`): equivalent. The fallback runs only for a plan without a round-close stamp, which `check_plan` refuses first ("round close: 0 round-close stamps").
- `replan.py`, test-side, 10: strict-bound loosenings (`<`/`>` to `<=`/`>=`) that correct code satisfies either way (closure, in-review, cap, wall-hours arms), failure-detail string constants, and the `sys.modules` stub's `DEFAULT_PERCENTILE`, which the stub ignores.
- `plan_page.py`, test-side, 3: `[:n]` slices in failure-detail arguments and the length of a fixture merge SHA that matches no roster commit.
- `size_durations.py`, test-side, 8: fixture comment indices, the unread `pages[4]` sentinel, four single-line `check(...)` deletions (a deleted arm cannot fail), `gh_raised = True` (unreachable while `_gh` raises), and the new arm's `1 / 0` swapped to `2 / 0` (the stub only needs to raise).
- The mutation lane mutates `custom_components/` only, and this diff touches no file there.

## Null control

- The `graphql` run of `size_durations.run` ends naming `size_durations.fetch (--via graphql)`. Under `note-run`, the null fails too, so the arm reads the appended note and not the model's own provenance.
- The `graphql` call through `replan.main` records `graphql` at index 1, and the `rest` call records `rest` at index 0. Under `replan-via`, both read `graphql`, the stub's default when `via` is absent.
- Before the stub moved into `sys.modules`, the arm imported `size_durations` from beside the script. replan's mutation copies then printed `FAIL the unmutated copy's self-test exits 0 (null control): rc=1`, so every copy's mutant died for that reason alone. With the module stub, that null control is `ok` again.

## Figures

Measured at head baaf0064355bdf4838021df66683584e3d8608c7, origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0, `date -u` 2026-11-11T12:44:25Z.
- `PYTHONPATH=tests/hastub python3 tools/plan/size_durations.py --self-test`: `size_durations self-test: 0 failed`; with the `note-replayed` mutant, `1 failed`.
- `bash tools/pr/prepr.sh` on the committed tree, before this body: rc=0, `merged structure ... STRUCTURE RATCHET PASSED`, `gate mode MODE: SCOPED`, `self-test 515 passed, 0 failed`, `ci predict: no ... red predicted`.
- `tools/plan/durations.json` is unchanged in this pass, so it was not re-measured.
- Class enumeration (step 8): the class is "a wiring of the measurement with no reader". Its rule is the diff-mode command in `## Mutation proof` over every added line; every survivor is dispositioned in `## Unpinned sites`.

## Unpinned sites

The diff-mode survivors, by the counts and lines the three runs printed:
- `replan.py`, production, 1 (`check_plan` closure fallback `default=0` to `default=1`): equivalent. The fallback runs only for a plan without a round-close stamp, which `check_plan` refuses first ("round close: 0 round-close stamps").
- `replan.py`, test-side, 10: strict-bound loosenings (`<`/`>` to `<=`/`>=`) that correct code satisfies either way (closure, in-review, cap, wall-hours arms), failure-detail string constants, and the `sys.modules` stub's `DEFAULT_PERCENTILE`, which the stub ignores.
- `plan_page.py`, test-side, 3: `[:n]` slices in failure-detail arguments and the length of a fixture merge SHA that matches no roster commit.
- `size_durations.py`, test-side, 8: fixture comment indices, the unread `pages[4]` sentinel, four single-line `check(...)` deletions (a deleted arm cannot fail), `gh_raised = True` (unreachable while `_gh` raises), and the new arm's `1 / 0` swapped to `2 / 0` (the stub only needs to raise).
- The mutation lane mutates `custom_components/` only, and this diff touches no file there.

## Red checks

`pr-contract / pr-contract` at the round-4 head failed with `roster_lib` lacking `carry_receivable`; `origin/main` is now merged, which carries it, so the branch no longer differs from main there. `tests / fast` (`features.py` combi census) is red on main since #3398 with a hotfix in flight; it is inherited from main and not fixed here. Carry: dismissed: main's red, not this diff's

`tests / nightly-status` is not in the `merge_train.py owed-reds` set, so it is not answered here.

## Roster carries (the group's six, origin/handoff/audit-r10-roster, field `carry`)

Carry 0 (closure rule, 20 slots, durations): kept. (1) `summary.closure_conditions`, which `check_plan` refuses without. (2) 20 slots. (3) Durations re-measured through the tracked REST read, whose wiring into `run` and `replan --sizes-via` is now pinned (`## Re-cut`).
Carry 1 (outside priority, live stage, counts, None, headings): kept. Item 1 needs no code change, because `dispatch_tier` reads `roster_lib.is_outside`, and existing arms pin that. Carry: dismissed: not reproduced at this head, the code reads the flag
Carry 2 (count sentence): kept. The singular, zero and plural shapes are pinned.
Carry 3 (wave and sort-key None): kept, with a wave-3 group as null control.
Carry 4 (part-merged strip, heading markers): kept, with one predicate for the strip and the row.
Carry 5 (0-based roster index; read 1-based as Carry 6; items 1 to 5): kept. Item 3's hotfix mark is pinned on the rendered page, with five null arms, and `dev/audit/harnesses/r10_plan_page_mutants.py` kills `hot-render`, `hot-gates`, `hot-notdone` and `hot-crit`.

## Forward-carry

none

## Friction

handoff-wip-step-push: cost: refs/heads/handoff-wip/r10-plan-page-residue holds efa87c5a7f, a prior seat's history that forks from 9774026d05 outside this head's ancestry, so no fast-forward step push was possible and none was forced; that ref is left as found. Carry: dismissed: the code went straight to the handoff ref
