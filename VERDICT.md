Fix review: blocked e14a378c12e5d292c1f564bc9100ecb0de39bd76 carry-missing: the round-2 spellings are closed, but the literal fold is open one spelling further (class attribute `_H.L0` +4 copies, constant expression `12 * 2` +4), so the BRIEFS-FOLD carry must state the general limit; a roster carry alone unblocks, with no head move
bus-nonce: 9e9e8d92e86061dc4ba446305b864999

PR #2373, R10-ARCHSCORE-COVERAGE part 4. Review round 3 (round 1 `a19384631` blocked at `28d6a60bb`, round 2 `d21d3b132` blocked at `c06c9e84b`). I judged the delta from `c06c9e84b` to `e14a378c12e5d292c1f564bc9100ecb0de39bd76` from detached worktrees at that head. The delta is the fixer's `45da9204f` (repair), `c5dbc83da` (attempts 42d and 44c, row at 186) and `a70d4a3b6` (closures record), plus the merges `807c80dc5` and `e14a378c1`, whose remerge-diffs are empty. The box was at load ~90-190, so per heavy-to-ci I ran only targeted mutants and cheap checks, and cite CI for the heavy lanes.

## Round-2 items: both closed (re-derived by me at this head)

- **P4, bare `;`:** `card_clone_copies 108->108`.
- **P5, `_c.X`:** `literal_clone_copies 186->186`. My script's label still says 184; the base reads 186.
- **Round-1 plants:** 186->186, 186->186 and 108->108 (`r3_plants_*.txt`).
- **Mutant M13** (`_Inline.visit_Attribute` never resolves): `rt_42d_literal_module_attr` NULL -> IMPROVES (+0.0337).
- **Mutant M15** (`(run or out[-1:] != ["}"])` -> `run`): `rt_44c_card_empty_statement` NULL -> IMPROVES (+0.0844), and `rt_44b` stays NULL. Both match the body (`r3_mut_M13.txt`, `r3_mut_M15.txt`).
- **Calibration** (`--only`, the 17 part-4 cases): every one classifies as recorded. `RED TEAM 8/8 attempts read NULL or inadmissible; IMPROVES: none` (`r3_calib_M0.txt`).
- **Finder harness** (ARCH2-s5, `3930b421a`): F1 reads `delta_S=+0.4701`, `literal_clone_copies=186->134`, and C1-C4 read `delta_S=+1.0958`, `card_dead_definitions=1->0`, `card_clone_copies=108->101`. The perturbation reads 0 and the vector equals the baseline. The F1 shift from +0.4761 (184->132) is the disclosed `store.py` class, present at both ends.
- **Today's tree:** 0 / 108 / 186, matching the rows. The two extra copies are `store.py:300-301` (the `Domain` bounds of `HOUSE_HEAT_LOSS_SCALE_*` and `LOWER_FLOOR_LOSS_RATIO_*`, both 0.3-3.0). That is the over-fire the body discloses as the cost of folding by value. I accept the trade-off: folding by identity would reopen round 1's P1.
- **Corpus:** I ran my own spot-check of the 6 newest corpus trees. Live `literal_clone_copies`/`card_*` equal the stored vectors (`diff=0`, `r3_corpus_spot_*.txt`). None of the 87 corpus trees carries both `c.`-Domain bound pairs, which is consistent with the stored vectors not moving. I did not re-run the full corpus myself (heavy).
- **Merge:** `merge-tree` against origin/main exits 0. The roles contract matches main.

## Why blocked

Step 14, the diff's own move one spelling further, with nothing improved (`plants3_r3.py`, `r3_plants3_*.txt`). Three copies of `_number(1, 24, 1, slider=True)` read the bound through:

- **P6, a class attribute:** `class _RtH: L0 = 24 ...` read as `_RtH.L<i>`. Result: `literal_clone_copies 186->182`.
- **P7, an equal constant expression:** `12 * 2`, `20 + 4`, `48 // 2`. Result: `186->182`.

Neither is closed, and neither is in ABOUT's "What part 4's censuses do not see" list. P7 is not "a value computed at runtime": the AST holds a `BinOp` of literals.

The BRIEFS-FOLD carry (roster `72b97a4a5`) names only the three round-1 moves and says "Unless #2373 closes them". So a brief-writer will read the class as closed.

This is the third round in which the next spelling of a normalising census reads IMPROVES. A census of a finite list of spellings cannot be complete, so I am not asking for P6 and P7 to be closed. **Remedy (the orchestrator's, and the head need not move):** amend the R10-BRIEFS-FOLD carry to state the general limit. For example: "`literal_clone_copies` and `card_clone_copies` normalise a finite list of spellings (ABOUT.md, part 4); any other indirection of the same value -- a class attribute, a constant expression, a spelling not listed there -- reads a copy as removed, so a drop in either is credited only when the copies are actually gone from the source, never on the metric alone."

With that carry at origin/main, a re-dispatch at this same head would be `merge` from me, provided the head's CI concludes green. Adding P6 and P7 to ABOUT's list is welcome but optional, and it would move the head.

## Checks

All 45 check-runs at this head concluded: 30 success, 15 skipped, none red. That includes `arch-score` (both runs), `briefs`, `closures`, `fast (3.14)`, `pr-contract` and `budget-raise-gate` (`r3_check_runs_*.tsv`, read from the check-runs API).

## Owed to tvofi at merge (mandate 6175172275)

- `tests/ci_budgets.json` gains three new rows against the merge base `42e6dedb2`: `archscore.literal_clone_copies` 186, `archscore.card_dead_definitions` 0 and `archscore.card_clone_copies` 108. It also changes `reason` and sets `recorded_at` to `45da9204f`. No existing row moves.
- `tools/audit/archscore/calibration/expected.json` gains 17 cases: the twelve from round 0, plus 42b, 42c, 44b, 42d and 44c. Nothing is deleted.

## Not verified by me

The full `--record`, the full corpus re-measure, M14 and M16, and the ablations. CI's `arch-score` covers the calibration.

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-2373/evidence
