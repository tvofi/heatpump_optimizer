Plan-page group r10-plan-page-residue, re-cut at round 4. Closes no issue.

## Re-cut

Round 3 blocked on three unpinned wirings of the REST read into the measurement: `note-run`, `run-via` and `replan-via`. This pass pins all three with failing-first arms, so nothing leaves this PR. `size_durations.run` now takes `reads` (default `READS`) and `roster_file` (passed to `replan.load_roster`'s `file`) by injection. A self-test arm drives `run` with fake reads and the `_fixture()` roster, and asserts that the `rest` read is the one called and that `sizes_provenance` ends with `input_note("rest", ...)`. Its null control is a `graphql` run, which ends naming `fetch`. `replan.py --self-test` stubs `size_durations` in `sys.modules` through `mock.patch.dict` and asserts that `--measure-sizes --sizes-via rest` reaches `size_durations.run` with `via` `rest`, with `graphql` as the null. The stub is a module in `sys.modules`, not a file, so replan's own mutation copies, which have no `size_durations.py` beside them, run the arm too.
Taken out of this PR: nothing. Every carry the round-3 head built is kept, and each is named below.

## Head

0b32b0ba31f0946130b5e2852e9cb0e2adcd0e4c

## Mutation proof

- The round-3 survivors, each applied by hand to the head and run through its own self-test, then restored:
  - `note-run`: deleted `out["sizes_provenance"] += input_note(via, since, len(prs), replayed)` in `size_durations.run`. `size_durations.py --self-test` rc=1, `FAIL run --via rest: sizes_provenance ends naming fetch_rest` and `FAIL run --via graphql (null): sizes_provenance ends naming fetch`.
  - `run-via`: `read_prs(reads, via, ...)` changed to `read_prs(reads, "graphql", ...)`. rc=1, `FAIL run --via rest: the rest read builds the PR list`.
  - `replan-via`: dropped `args.sizes_via` from `replan.main`'s `size_durations.run` call. `REPLAN_MUTATION_CHILD=1 replan.py --self-test` rc=1, `FAIL --measure-sizes --sizes-via rest reaches size_durations.run as via=rest (null: graphql): ['graphql', 'graphql']`.
- Diff mode over the whole kept diff: `python3 tools/audit/seat/mutant_run.py --diff 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444...HEAD --cmd 'sh -c "python3 tools/audit/seat/plan_page.py --self-test && python3 tools/plan/size_durations.py --self-test && REPLAN_MUTATION_CHILD=1 python3 tools/plan/replan.py --self-test"'`. It printed 21 `SURVIVED` lines and rc=1. Each survivor is dispositioned in `## Unpinned sites`, and 20 of them are on self-test lines. `REPLAN_MUTATION_CHILD=1` skips replan's own self-mutation loop and no arm under test.

## Null control

- The `graphql` run of `size_durations.run` ends naming `size_durations.fetch (--via graphql)`. Under `note-run`, the null fails too, so the arm reads the appended note and not the model's own provenance.
- The `graphql` call through `replan.main` records `graphql` at index 1, and the `rest` call records `rest` at index 0. Under `replan-via`, both read `graphql`, the stub's default when `via` is absent.
- Before the stub moved into `sys.modules`, the arm imported `size_durations` from beside the script. replan's mutation copies then printed `FAIL the unmutated copy's self-test exits 0 (null control): rc=1`, so every copy's mutant died for that reason alone. With the module stub, that null control is `ok` again.

## Figures

Measured at head 0b32b0ba31f0946130b5e2852e9cb0e2adcd0e4c, origin/main e67b79c9fce5abf7eb93347aa50fa27b1daec96b, `date -u` 2026-11-11T07:58:57Z.
- `python3 tools/plan/size_durations.py --self-test`: `size_durations self-test: 0 failed`.
- `python3 tools/plan/replan.py --self-test`: `model self-test: 0 failed`, `self-test: 0 failed`, including the mutation copies' null control.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope, from `python3 tests/closure.py select --diff 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `scope.run` names `tests/entities.py`, and `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2707 ENTITY CHECKS PASSED`.
- `git merge-tree --write-tree origin/main HEAD`: exit 0, no conflict.
- `tools/plan/durations.json` is unchanged in this pass. It was not re-measured, because the corpus window is still open. Its `sizes_provenance` names the read it came by.
- Class enumeration (step 8): the class is "a wiring of the measurement with no reader". Its enumeration rule is the diff-mode command above over every added line. All survivors are dispositioned below.

## Unpinned sites

The 21 survivors of the diff-mode run above:
- `replan.py`, production, 1: `check_plan`'s `default=0` in the closure fallback, swapped to `default=1`. This is equivalent. The fallback runs only for a plan without a round-close stamp, and `check_plan` refuses that plan first ("round close: 0 round-close stamps").
- `replan.py`, test-side, 10:
  - Six `CMP_BOUND` loosenings of a strict self-test bound (`<`/`>` to `<=`/`>=`), which correct code satisfies either way: the closure, in-review, cap and wall-hours arms.
  - Two `CONST_SWAP`s in failure-detail strings, which print only on failure.
  - The cap arm's `<= 98.0`.
  - The `sys.modules` stub's `DEFAULT_PERCENTILE`. `main` passes it to the stub's `run`, and the stub ignores it.
- `plan_page.py`, test-side, 3: the `[:3]` slice in two failure-detail arguments, and the `"f" * 40` length of a fixture merge SHA, which matches no roster commit at either length.
- `size_durations.py`, test-side, 7:
  - The fixture comment indices `(1, 2)`. Both sides of the compared flatten are built from the same nodes.
  - The `pages[3]` sentinel key. That page is read only under a production mutant, and the short-page arm kills that mutant.
  - Four single-line `check(...)` deletions. A deleted arm cannot fail.
  - `gh_raised = False` flipped. The line is unreachable while `_gh` raises.
- The mutation lane mutates `custom_components/` only, and this diff touches no file there.

## Red checks

`pr-contract / pr-contract` at 95c04821e5: `carry_audit.py check` raised `AttributeError: module 'roster_lib' has no attribute 'carry_receivable'`. `roster_lib.carry_receivable` landed on main in e08425e904, after this branch's merge base, so the branch's `roster_lib.py` lacks it. `git grep "def carry_receivable"` finds it at origin/main and not at this head. The cheaper detector: none exists that this branch could run. The red appears only when main's reader meets the branch's older module, and the train re-proves the head on current main, where `merge-tree` reports no conflict. Carry: dismissed: a reader that landed on main after the merge base, cleared by the train's re-proof on current main
`tests / nightly-status` is not in the `merge_train.py owed-reds` set, so it is not answered here.

## Roster carries (the group's six, origin/handoff/audit-r10-roster, field `carry`)

Carry 0 (closure rule, 20 slots, durations): kept. (1) `summary.closure_conditions`, which `check_plan` refuses without. (2) 20 slots. (3) Durations re-measured through the tracked REST read, whose wiring into `run` and `replan --sizes-via` is now pinned (`## Re-cut`).
Carry 1 (outside priority, live stage, counts, None, headings): kept. Item 1 needs no code change, because `dispatch_tier` reads `roster_lib.is_outside`, and existing arms pin that. Carry: dismissed: not reproduced at this head, the code reads the flag
Carry 2 (count sentence): kept. The singular, zero and plural shapes are pinned.
Carry 3 (wave and sort-key None): kept, with a wave-3 group as null control.
Carry 4 (part-merged strip, heading markers): kept, with one predicate for the strip and the row.
Carry 5 (items 1 to 5): kept. Item 3's hotfix mark is pinned on the rendered page, with five null arms, and `dev/audit/harnesses/r10_plan_page_mutants.py` kills `hot-render`, `hot-gates`, `hot-notdone` and `hot-crit`.

## Forward-carry

none

## Friction

handoff-wip-step-push: cost: refs/heads/handoff-wip/r10-plan-page-residue holds efa87c5a7f, a prior seat's history that forks from 9774026d05 outside this head's ancestry, so no fast-forward step push was possible and none was forced; that ref is left as found. Carry: dismissed: the code went straight to the handoff ref
