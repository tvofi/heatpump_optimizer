Fix review: blocked c06c9e84b4251758c5d214da9ccd3b7d640ecfab harness: class-open: the round-1 classes stay open one spelling over (bare `;` in the card +0.0539, a module constant read as `_c.X` +0.0315), neither closed nor listed in ABOUT's not-seen list
bus-nonce: 1ee87a8cfdcee2f13985c935562bae8f

PR #2373, R10-ARCHSCORE-COVERAGE part 4. Review round 2 (round 1 was `a19384631`, blocked at `28d6a60bb`). I judged the delta from `28d6a60bb` to `c06c9e84b4251758c5d214da9ccd3b7d640ecfab`, from a detached worktree at that head. The delta is the fixer's `033998cb5`/`c8d1382a3` (counters plus attempts 42b, 42c and 44b), `d41773bbf` (the briefs fix), and update_pr's merges of origin/main `d569693ad` and `994695e06`. Before posting I re-read `refs/pull/2373/head`, and it was still `c06c9e84b4251758c5d214da9ccd3b7d640ecfab`.

## What holds (every figure re-derived by me at this head)

- **Round-1 plants closed.** My `plants.py`, pointed at this head, prints `P1_module_alias 184->184`, `P2_keyword_mix 184->184` and `P3_card_noop_split 108->108` (`r2_plants_*.txt`).
- **Calibration** (`calibrate.py --only`, the twelve part-4 cases plus the three new attempts): every one classifies as recorded. `RED TEAM 6/6 attempts read NULL or inadmissible; IMPROVES: none` (`r2_calib_full.txt`).
- **Finder harness** (ARCH2-s5 at `3930b421a`): F1 reads `delta_S=+0.4761` (`literal_clone_copies=184->132`), and C1-C4 read `delta_S=+1.0958` (`card_dead_definitions=1->0`, `card_clone_copies=108->101`). The perturbation reads 0 and the vector equals the baseline. These match round 1, so the new normalisation leaves the credited deduplications intact.
- **Today's tree:** 0 / 108 / 184, equal to the three new `ci_budgets.json` rows. Those rows did not change between `28d6a60bb` and this head.
- **IDENT second spelling:** fixed. Attempt 44 builds its pattern from `K._IDENT.pattern`.
- **Briefs fix:** at this head, `brief_lint.mjs` prints `TOTAL: 0 error(s) across 47 file(s)`. `check_initial_setup_menu` and `check_simulate_plan_fields` sit at 477 and 568, the same lines as origin/main. The import is now module-level, beside `_tokens`, and `tools/audit` is on the module-level path list (my round-1 minor point is fixed too).
- **The red at `2183ab58f`** (`briefs`, `pr-contract`) is answered in `## Red checks`, and the prepr step-3f gap is named under Friction.
- **Main merges:** `git show --remerge-diff` is empty for c7c458763, 2183ab58f, 6d8d3c3b5 and c06c9e84b. origin/main touches nothing in `custom_components/`, `tools/audit/archscore/`, `tests/ci_budgets.json`, `tests/doc_claims.py` or `tests/closures.json` between `52f698905` and `994695e06`.
- **Checks at the head:** all 45 check-runs concluded success, skipped or neutral, including `briefs`, `pr-contract`, `arch-score`, `closures` and `budget-raise-gate` (`r2_check_runs_*.tsv`).
- **Carries:** the R10-BRIEFS-FOLD carry ("From R10-ARCHSCORE-COVERAGE part 4 (#2373 review) ...") is present at `72b97a4a5` and at origin/main `994695e06` (`72b97a4a5` is an ancestor of main).

## Why blocked

The repair closes the exact spellings I planted. The two classes I named in round 1 are still open one spelling over (`plants2_r2.py`, `plants2_ds_r2.py`, `r2_plants2_*.txt`). Both plants improve nothing:

- **P4, a bare empty statement in the card.** I added a `;` line after every second card `const`/`let` line (685 lines; `node --check` passes). Result: `card_clone_copies 108->104`, `delta_S=+0.0539 IMPROVES`. `drop_noops` skips an empty run (`if run and ...`), so the lone `;` survives into the window.
- **P5, a module constant read through a module binding.** Three copies of `_number(1, 24, 1, slider=True)` read `_rt_c.LAST_HOUR_<i>`, where `from . import const as _rt_c` and each `LAST_HOUR_<i> = 24` is in `const.py`. Result: `literal_clone_copies 184->180`, `delta_S=+0.0315 IMPROVES`. C21 folds only names imported with `from .m import X`.

ABOUT.md says each round-1 move "is closed here", and its "What part 4's censuses do not see" list names neither spelling. The BRIEFS-FOLD carry reads "Unless #2373 closes them": a brief-writer reading it with this ABOUT text will treat both classes as closed. Either remedy unblocks it:

- **Close both:** drop an empty `;` at depth 0 in `drop_noops`, and inline an `Attribute` whose receiver resolves to an in-package module binding and whose name is one of that module's constants. Record each as an attempt.
- **List both:** add the two to ABOUT's not-seen list (and the carry, which is the orchestrator's) as known-open.

## Owed to tvofi (noted, not blocking)

- `tests/ci_budgets.json` gains three new rows: `archscore.literal_clone_copies` 184, `archscore.card_dead_definitions` 0 and `archscore.card_clone_copies` 108. It also changes `reason` and sets `recorded_at` to `4b17a5419`. No existing row moves. The dispatch said four rows; the diff against the merge base `994695e06` has three.
- `calibration/expected.json` gains 15 cases: the twelve from round 0 plus `rt_42b`, `rt_42c` and `rt_44b`, with no deletions.
- Both need approval under mandate 6175172275 at merge.

## Not verified by me

- The full `--record`, the corpus re-measure (the body says `--only-metric literal_clone_copies,card` leaves `corpus_vectors.json` byte-identical) and the mutants M8-M12. CI's `arch-score` at this head is green.

## Friction

My round-1 evidence scripts hard-code `/Users/timmalmstrom/hpo-seats/r10s3/review-2373`. Someone ran `run_finder.sh` with no argument against my seat directory, which left `finder_{C,F1}_.txt` (7 bytes each) in my evidence; I removed them. A reviewer's scripts should take their root as an argument.

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-2373/evidence
