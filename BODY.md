R10-WHY-NOW-WIDGET part 2: the three carries the roster held after part 1 (#3274). Each was checked against origin/main `5bc009bc8`. Two were already done in code. This PR adds the one thing still missing: a check that pins the P9 clip walk part 1 fixed.

- **Carry 0 (the widget spec): settled by #3274.** `slot_drivers.py` publishes `why_now` from the solve's own inputs. `coordinator.py` puts it in the payload under that one key, and the card renders it as the "Why now" block (`whyNowHtml`). The en and sv strings are in `STRINGS`, and `tests/card.mjs` has the "why-now:" cases (rows, the no-data line, the all-neutral line, sv). The metric explanation does not match the brief word for word on purpose. Part 1's fix review found that "mostly decides the hour" overclaims, because the rows are pushes on the plan and the pump can still do the opposite (commit `9cde30560`). Nothing is left to do here.
- **Carry 1 and carry 2 (item 7c609975, filed twice): fixed in #3274 by `ce5a395e9`, which had no pin until now.** `unreachable()` in `tests/card_browser.mjs` now starts its walk at `run.el`, but nothing failed if the walk went back to `parentOf(run.el)`. This PR exports the walk as `H.unreachable` and adds a probe at the start of `p9Grid`, before its cells. A text run clipped by its own box (40 px wide, `overflow:hidden`) must read as clipped. An unclipped run in the same 40 px column must read as clear; that is the null control.

## Head

8708d433d576354ed0f4c43c236f5eda14afc696, on origin/main 5bc009bc82962df5d239cbacc2e570dffd9a9cf9.

## Mutation proof

To mutate, put the walk's start back to the pre-#3274 form: in `unreachable()`, `for (let n = run.el; ...` becomes `for (let n = parentOf(run.el); ...`. Then run `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs`:

    FAIL  P9 instrument: a text run clipped by its own box reads as clipped, and an unclipped one as clear
    1 BROWSER CHECK(S) FAILED

That one check fails and no other does. It reports `own box 0.0 px, unclipped 0.0 px`. After the run the line was restored with `git checkout tests/card_browser.mjs`, and `git diff --quiet` confirmed the tree was clean.

## Null control

In the same probe, a run that no box clips reads 0.0 px on both the fixed walk and the mutated one. The check needs `own > 0.5 && free <= 0.5`, so a walk that marked every run as clipped would also fail. On the unmodified tree the full P9 grid still passes, so the walk now starting one element lower finds no clipped run in any card cell.

## Figures

- `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` at the head, after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`: `ALL BROWSER CHECKS PASSED`, including `P9 instrument: a text run clipped by its own box reads as clipped, and an unclipped one as clear`. The probe reports the own-box run as 187.1 px clipped and the unclipped run as 0.0 px. The run took 4m33s wall time.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The only changed file is `tests/card_browser.mjs`. It is on the grid surface (`GRID_SURFACE`), which no scope selects, so `card_browser.mjs` was run by hand as shown above.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Diff mutants: `MUTANT_CMD` was set to the browser suite. `tools/audit/seat/mutant_run.py --diff` mutates added Python lines only, and this diff adds none, so it made 0 mutants and found 0 survivors. The hand mutation above covers the JS line.
- origin/main had not moved from `5bc009bc8` at the prepr run, so no second run was needed.

## Red checks

none

## Unpinned sites

n/a: the diff adds no Python and no `custom_components/` line, so step 6d lists no site.

## Forward-carry

none

## Friction

none
