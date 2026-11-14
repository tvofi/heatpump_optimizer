HOTFIX (owner, 2026-11-14: "Do a CI-ratchet fix, but don't let it delay anything"). `tests/ci_ratchet.py`'s push-window walk (`_walk`) refused CI push run 43602217369 (merge 97a3a921e0), cancelled at its prelude, as `has no completed \`tests / *\` job (fail closed)`. Its recorded job listing (`GET repos/tvofi/heatpump_optimizer/actions/runs/43602217369/jobs`, 14 jobs) holds `prelude` cancelled, the `tests` caller and every other unit skipped, and no `tests / *` job at all: the walk excluded a run with a *cancelled* tests job but had no arm for a run whose tests never ran. The new predicate `_cut_at_prelude` excludes a CI run whose `prelude` concluded cancelled and whose every tests job (the `tests` caller and any `tests / *`) concluded skipped, beside the existing cancelled-job exclusion in `_walk`; anything else keeps the refusal.

**Part two (advisory on push) is already on main, so this diff builds nothing for it.** The owner's 2026-11-11 ruling, as triage recorded it (`dev/programme/triage/s6-batch218.md#P666`: "on push, ci-ratchet is reported advisory (its result printed, never a gate failure); on pull requests it stays as today"), was built by R10-GATE-PUSH-RATCHET at ef4556bb42 (2026-11-12T08:55Z, before the four red pushes of 2026-11-14): `tools/ci/gate.py`'s `PUSH_REPORT_ONLY` holds `ci-ratchet`, and `machinery_line()` prints its conclusion while the gate passes. Its self-test pins the arm and both nulls: `a push with ci-ratchet red passes and reports it in the one machinery line`, `a push with coverage-ratchet red still fails`, `B3: push owes coverage-ratchet and no longer ci-ratchet (report-only)`. The `ci-ratchet` job runs only on push to main (`tests.yml`'s `if:`), so no pull-request run has a ratchet step to keep refusing. A second advisory in the workflow step or the script, turning the job itself green, would make a second owner of the rule and blank the input `machinery_line()` reports (it would always read `success`): rejected under the brief's own "one owner" condition. Departure from the brief's "never built", raised here and in `## Friction`.

## Head

bc85e0900add6d276b90ba0f83fa6272b92e8d9c, measured on merge base 9fdba3b8547f9762438dc19b98b310a63d34dcb1 (origin/main at 2026-11-14T16:34Z).

## Mutation proof

Each mutant applied to `tests/ci_ratchet.py` at the head, `python3 -I tests/ci_ratchet.py --self-test` run, restored. Every mutant reddens a named arm:

- M1, the `or (kind == "CI" and _cut_at_prelude(jobs))` term removed (the base's behaviour): `FAIL a run cancelled at its prelude, its every tests job skipped, is not in the window (run 43602217369)`; 72 checks, 1 failed.
- M2, the prelude-cancelled conjunct replaced by `True`: `FAIL null: a CI push run with no completed tests job whose prelude succeeded still refuses`; 1 failed.
- M3, `bool(tests)` dropped: `FAIL null: ... whose prelude was cancelled and whose listing holds no tests job still refuses`; 1 failed.
- M4, the all-skipped conjunct dropped: `FAIL null: ... whose prelude was cancelled but a tests job never completed still refuses` and `FAIL null: ... whose prelude was cancelled but its tests caller failed still refuses`; 2 failed.
- M5, the `TESTS_CALLER` name match disabled: `FAIL a run cancelled at its prelude ...`; 1 failed.
- M6, `kind == "CI"` flipped to `"Tests"`: `FAIL a run cancelled at its prelude ...`; 1 failed.

Failing test first: commit 990dcfaf20 adds the arms alone; there the self-test exits 1 with `FAIL a run cancelled at its prelude, its every tests job skipped, is not in the window (run 43602217369) -- ci-ratchet: CI push run 43602217369 has no completed \`tests / *\` job (fail closed)`, the message the four red pushes printed.

## Null control

Four nulls, each the recorded listing with one property removed, each still refusing `(fail closed)` at the head: prelude `success`; prelude cancelled plus a `tests / fast (3.14)` job with no `completed_at` (a tests job genuinely missing); prelude cancelled with the `tests` caller `failure`; prelude cancelled with no tests job in the listing. The pre-existing arm `a CI push run that has no completed tests job refuses` is unchanged and green.

## Figures

- `python3 -I tests/ci_ratchet.py --self-test` at bc85e0900a: `ci-ratchet self-test: 72 checks, 0 failed`; at 990dcfaf20 (test only): rc 1, the one arm above failed.
- Mutants M1-M6: the self-test command above per mutant; killed 6 of 6 (rule: a mutant is killed when the summary line reports >= 1 failed).
- `python3 -I tools/ci/gate.py --self-test` at bc85e0900a (file unchanged by this diff): `gate self-test: 106 checks, 0 failed`.
- Window replay (scratch probe, not landed: the self-test arms reproduce it): a runs.json of the recorded 43602217369 listing plus one measured run, graded by `critical_path_minutes` from each tree's `git show <sha>:tests/ci_ratchet.py`: at 9fdba3b854 `REFUSED: ... has no completed \`tests / *\` job (fail closed)`; at bc85e0900a `21.0` (the measured run alone). Null control: the same window with the prelude set `success` refuses at both.
- Scope and run: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py`; run with `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2725 ENTITY CHECKS PASSED`; `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
<!-- figure-block: scope-line mb=9fdba3b8547f9762438dc19b98b310a63d34dcb1 head=bc85e0900add6d276b90ba0f83fa6272b92e8d9c -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

- brief: stale: the brief states the owner's 2026-11-11 advisory-on-push ruling "was never built"; it landed at ef4556bb42 (R10-GATE-PUSH-RATCHET, `tools/ci/gate.py` `PUSH_REPORT_ONLY`, 2026-11-12) before the reds the brief cites, so this diff builds no second owner. Carry: dismissed: built at ef4556bb42; recorded in this body for the reviewer
