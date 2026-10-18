Fix review: blocked c75609c3a172cae8497086606abe25d7b84a6c08 tests-red: fast's tests/arch_score.py fails "null: a callback handed to a package function" (got 1, want 0), because the P18 fold C16b roots a callback a package function only returns; pr-contract also refuses `Closes #2259`
bus-nonce: 0864ca92988fb69693386b6571e81c15

PR #2401, R10-ARCHSCORE-COVERAGE part 5, review round 1. Reviewed from a detached worktree at `c75609c3a172cae8497086606abe25d7b84a6c08` (merge base `3fb386d50`). The role contract matched origin/main `63816b857` (the roles diff was empty). `merge-tree` against origin/main exits 0. Before pushing I re-read `refs/pull/2401/head`, and it was still `c75609c3a172cae8497086606abe25d7b84a6c08`. Load was high, so I ran targeted mutants and cheap checks only, and cite CI for the heavy lanes.

## Blocking

1. **CI `fast (3.14)` is red on `tests/arch_score.py`. The cause is in this PR, and the body does not answer it.** The check-run (job `117678743499`, `fast_log.txt`) prints `1 of 254 ARCHITECTURE SCORE CHECKS FAILED`:
   - `FAIL hub census: null: a callback handed to a package function reads 0 site(s), and 0 with C15 and C16 off  [got 1 (C15/C16 off: 0), base 0]`.
   - The fixture there is `_register(self._on_package_callback)` with `def _register(cb): return cb`, and the call's result is discarded. That is the P18 F1 shape, `_pkg_wrap`, without the HA subscription.
   - C16b (`hub_solve_writes._passes_on`) treats "returns the reference" as "passed on" whatever the caller does with the return value. So a reference nobody subscribes now becomes a hub root. The existing null control pins the opposite, and the PR does not touch `tests/arch_score.py`.
   - Either C16b over-fires, and the pass needs to follow the returned value to a subscribing call (or rather, its consumer), or the semantics changed deliberately and the null control must change with a reason. The body says "CI has not run on this head", so the red is unanswered (step 11).
   - All workflows at the head have concluded, and a `pr-contract` run (`117686903278`) started at 13:23, after this red concluded at 13:14.
2. **`pr-contract` refuses `Closes #2259`.** Both runs print `REFUSE 'Closes #2259' closes #2259; not in the intended list` (`pr_contract_1323_log.txt`).
   - The roster group `R10-ARCHSCORE-COVERAGE` has `fixes: [2228]` and `issues: [2228, 2235, 2259]`. Its brief says to use a closing keyword only for `fixes`, and "Part of" for the rest.
   - The coordinator's brief for part 4 also said #2259 is closed by hand after p5. The body should say `Part of #2259`.
3. **#2259 item 2's "duplicated spellings" in the card is not delivered, so it cannot be closed.** The issue says: "extend the vector to `www/*.js`, at least duplicated spellings, dead definitions and the card's own clone census". Part 4 delivers dead definitions and the 20-token clone census. Part 5's shape census reads Python only. My probe:
   - I used the finder's census, ARCH2-s5 `card_shapes.mjs` at `3930b421a`, which states its perturbation: "any one of the shapes spelled once more anywhere moves its count and the total up by 1".
   - I spelled three of its rules once more (a live-guard, a null test and a finite test), inline inside existing card methods. The finder's total reads 22 -> 25. `card_clone_copies` and `card_dead_definitions` read 108 -> 108 and 0 -> 0, and no other metric reads JS (`card_spellings.py`, `card_spellings_*.txt`; `node --check` passes).
   - The card's docstring claim that "a rule spelled inline in several functions (the live-state guard, the finite-number test) joins its spellers" holds only where a 20-token window happens to match. A one-statement spelling is below the window.
   - The delivery-table row "#2259 2, card coverage ... part 4" is therefore partial. Remedy: deliver it (for example, a card counterpart of C23's shape census for one-statement rules), or record it as not delivered and leave #2259 open with that item carried.
4. **The companion harness has not landed** (step 9, `fixer.md` 18).
   - `shape_family_coverage.py` (sha1 `a6e533f0…`, "in the seat's scratch") produces the body's item-6 figure: `joined=0` at the base and 26 at the head of ARCH-s2's 35 payload-guard implementations. M3's pin rests on it as well.
   - A body figure a later seat must reproduce lands in `dev/audit/harnesses/`, and `tools/audit/seat/tmp_paths.py` must accept it.
   - I could not re-derive 0 -> 26 without rebuilding it, so that figure is unverified by me (step 8).
5. **Inherited from #2373, still open.** This branch carries part 4's code at `69c36cee5`. My #2373 round-3 plants still read IMPROVES here (`p4_open_plants_*.txt`):
   - P6, a class attribute: `literal_clone_copies 186->182`.
   - P7, a constant expression `12 * 2`: `186->182`.

   The R10-BRIEFS-FOLD carry on origin/main still says only "Unless #2373 closes them". It does not yet state the general limit that #2373's round-3 verdict asked for. Since part 4 lands through this PR, that carry is owed before this merges too.

## What holds (re-derived by me)

- **Today's tree:**
  - `shape_copies` reads 66 (`measure_*.txt`).
  - `literal_clone_copies` 186, `card_clone_copies` 108, `card_dead_definitions` 0 and `hub_solve_writes` 41 match the four new `ci_budgets.json` rows and the unchanged hub row.
- **Targeted mutants** (`mut_p5.sh`, `calibrate.py --only`):
  - M0: the eight part-5 and hub cases each classify as recorded. `a3_shape_copies_control` is WORSENS (`shape_copies 87->88`), `_fix` NULL, `_null` NULL and `_respelled_control` NULL. `rt_45` is WORSENS and inadmissible, `rt_20b` NULL, and `a3_hub_event_write_control`/`_fix` are WORSENS/IMPROVES.
  - M1 (no class formed, `len(v) > 999`): `a3_shape_copies_control` WORSENS -> NULL, as the body says.
- **Gate-only calibration:** I accept the decision on the evidence the body gives (respelled control NULL, `ca711b56`). I did not re-run the corpus counterfactual.
- **CI:** 45 check-runs, 28 success, 14 skipped and 3 failure. The failures are `fast (3.14)` and the two `pr-contract` runs above. `arch-score` (the lane that re-derives the full record) is green.

## Owed to tvofi at merge (mandate 6175172275)

- `tests/ci_budgets.json` gains four new rows against the merge base: `archscore.card_clone_copies` 108, `archscore.card_dead_definitions` 0, `archscore.literal_clone_copies` 186 and `archscore.shape_copies` 66. Three come from part 4 and one from part 5.
- `tools/audit/archscore/calibration/expected.json` gains 23 cases (part 4's 17, plus part 5's 5 and `rt_20b`), with no deletions.

## Not verified by me

- The full `--record`.
- The corpus re-measure and the counterfactual arms.
- The companion's 0 -> 26 (item 4).
- M2-M4, M17-M21 and P18's plant script (also in scratch).

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-2401/evidence
