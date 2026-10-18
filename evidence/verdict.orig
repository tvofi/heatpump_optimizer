Fix review: merge 311e9de3e0c6d5bd0aa2139caf16b7707bf232f6

bus-nonce: fd05f3fcbbf74d093a1fbc08b99c824a

PR #2401, R10-ARCHSCORE-COVERAGE part 5, review round 3.
- Round 1 blocked at `c75609c3a`.
- Round 2 returned merge at `da688f509`; the third PR comment re-posts round 2.
- This round judges two things: the head move `da688f509` -> `40c311ffe` -> `311e9de3e`, as its resolution delta, and the body's new `## Raise justification`.
- I worked from a detached worktree at `311e9de3e0c6d5bd0aa2139caf16b7707bf232f6`, in a cloud seat.
- The roles diff against origin/main is empty, so the contract is current.

## Head move (step 12, as a delta)

- Both new commits are main merges: `40c311ffe` (main `c8cc75e`) and `311e9de3e` (main `176851e95`). `git show --remerge-diff` is empty for both (`ev/remerge_*.txt`), so neither merge has a hand resolution.
- The branch's own three-dot diff did not change. I compared `git diff f1b21daab...da688f509` with `git diff 176851e95...311e9de3e`: the two are byte-identical (`ev/branch_delta_diff.txt`, 0 lines).
- Main's range `f1b21daab..176851e95` touches nothing under `custom_components/`, `tools/audit/archscore/`, `tests/ci_budgets.json` or `tests/closures.json`. No measured value can move from it.
- `git merge-tree --write-tree` exits 0 against both origin/main heads:
  - `176851e95`, the PR base.
  - `106af95a3`, the current main. Main's newer commits again touch none of those paths.

## Re-derived at this head

- **Today's values match their `ci_budgets.json` rows:**
  - `shapes.measure(.)`: `shape_copies` 66, in 18 classes.
  - The other rows: `literal_clone_copies` 186, `card_clone_copies` 108, `card_dead_definitions` 0, `hub_solve_writes` 41.
  - Evidence: `ev/today_values.txt`, `ev/shape_classes_today.txt`.
- **Mutant M1** (`len(v) > 999`, no class is ever formed), run with `calibrate.py --only a3_shape_copies_control,a3_shape_copies_null`:
  - M0: the control reads `WORSENS shape_copies 87->88` and the null reads NULL.
  - M1: the control reads NULL; the null is unchanged.
  - The test is not vacuous (`ev/m0_full.txt`, `ev/m1_full.txt`).
- **Architecture score:** the body's command, `score.py --diff c8cc75e 40c311ffe`, prints `Architecture score: dS +0.0000 NULL`. So does `score.py --diff 176851e95 HEAD`, with the current merge base and the head (`ev/score_*.txt`). The diff touches no `custom_components/` file.
- **Scoped gate:** `closure.py select` prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. That matches the body. `tmp_paths.py --check` prints `0 refused`.
- I could not run `tests/arch_score_head.py` locally, because this seat's venv has no `homeassistant` module. I cite CI's `fast (3.14)` for it.
- **CI at this head:** 46 check-runs, 31 success and 15 skipped, none red (`ev/check_runs.txt`). Every run concluded before I read them. Green runs include:
  - `fast (3.14)`, `arch-score` (two runs) and `closures`.
  - `pr-contract` (two runs) and `budget-raise-gate` (two runs).
  - `coverage` and `coverage-ratchet`.
- No red check, so step 11 owes nothing new.

## Raise justification (step 14)

The only new row from part 5 is `archscore.shape_copies` 66. It is a new key set at its measured value, not an existing row raised. Part 4's three rows ride in from #2373 and are justified there.

Each payment the body lists, judged:

1. **Keep the key out of the vector. Refused, correctly.** That is an instrument choice, not a code improvement. It would also drop the census's only refusing case: `a3_shape_copies_control` reads WORSENS through C23 alone, and NULL with it off. The body says this, and M1 at this head confirms it.
2. **Deduplicate the production copies. Correctly described as not a payment for the row.** Lowering the count lowers the value the row is recorded at, but the row is still owed: `ci_ratchet` refuses any key in the vector that has no row. So no code change removes the need for the row.
3. **Weighted at the floor. Correctly excluded.** It still needs the row, and calibration refuses it on `ca711b56`.

The missed payment I hunted:
- Today's tree holds a real, single-import duplicate in class 11 of `ev/shape_classes_today.txt`: `config_flow:_effective` copies `comfort_band:effective`. The PR's own `a3_shape_copies_fix` case plants exactly this fix.
- Doing it would improve the code and move the row 66 -> 64. It would not avoid a row, so it is not a payment that the raise needed and missed. It is not `metric-gamed`.
- I name it as an improvement the census already points at, for the orchestrator to route. I am not blocking on it.

The body's dS line was taken at `40c311ffe` rather than this head. The two heads' branch diffs are identical, and I re-took the figure at this head: it is still `+0.0000 NULL`.

## Earlier rounds' findings

The round-2 dispositions all carry unchanged, because the authored code is byte-identical:
- the C16b null control and positive fixture;
- `Part of #2259`;
- the item-2 card spellings, marked not delivered and carried;
- the landed companion;
- the #2373 general limit.

## Owed (not blocking)

- **Orchestrator:**
  - Land #2384 for the R10-BRIEFS-FOLD carry.
  - Route the card duplicated-spellings census and the #2235 RCA.
  - Optionally, the `config_flow._effective` dedupe.
- **tvofi or mandate 6175172275 at merge:**
  - Four new `tests/ci_budgets.json` rows: `shape_copies` 66, `literal_clone_copies` 186, `card_clone_copies` 108, `card_dead_definitions` 0.
  - 23 new `expected.json` cases.

## Not verified by me

- The full `--record`, the corpus re-measure and the counterfactual arms. These are CI's `arch-score` and were green; I did not re-run them.
- Mutants M2-M4 and M17-M23. They rest on round 2, and the authored diff is unchanged since then.
- `arch_score_head.py`'s `ALL 18` line. I have only CI's `fast (3.14)`.
