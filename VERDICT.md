Fix review: merge da688f50971bd31043383aeffca623d3b713c86b
bus-nonce: 62444ef18f3cdcae7179c88536389af3

PR #2401, R10-ARCHSCORE-COVERAGE part 5, review round 2 (round 1 `0283ca6b5`/`aae44320c` blocked at `c75609c3a`). I judged the delta from `c75609c3a` to `da688f50971bd31043383aeffca623d3b713c86b` from detached worktrees at that head and at its merge base `f1b21daab`.

- The fixer's commits are `473d1cf36` (C16b) and `dfaaf9e18` (companion, general limit).
- The merges `9151f90af` and `da688f509` have empty remerge-diffs, and `merge-tree` against origin/main exits 0.
- The roles contract matches main.
- Before pushing I re-read `refs/pull/2401/head`, and it was still `da688f50971bd31043383aeffca623d3b713c86b`.

## Round-1 findings, each re-checked at this head

1. **The `tests/arch_score.py` red is fixed.**
   - C16b now roots a returned callback only where `_consumed` finds the call's value handed on.
   - I ran `hub_spellings()` alone (my `hub_only.py`, which is cheap): all nine hub cases are `ok`. That includes "null: a callback handed to a package function reads 0" and the new positive fixture "returns into a Home Assistant subscription (C16b) reads 1".
   - My mutants pin both arms. M22 (a returned reference rooted always) fails the null control (`got 1`). M23 (the returned arm off) fails the positive fixture (`got 0`).
   - CI's `fast (3.14)` at this head is green. The body's `## Red checks` answers the red, naming the cheaper detector (`hub_spellings`, which runs alone).
2. **`Closes #2259` is fixed:** the body says `Part of #2259` and `Part of #2235`, `closingIssuesReferences` is `[]`, and `pr-contract` at this head is green.
3. **#2259 item 2's "duplicated spellings" is now dispositioned honestly.**
   - The delivery table marks it "not delivered" with my probe's figures, and it says both issues stay open.
   - It is carried "to the orchestrator to route" as a card counterpart of C23, accepted by ARCH2-s5's `card_shapes.mjs` perturbation. Routing it is owed by the orchestrator (below).
4. **The companion has landed** as `dev/audit/harnesses/archscore_shape_family_coverage.py`.
   - I ran it myself on ref `554e2ecfa`. With the base instrument (`f1b21daab`, no `metrics/shapes.py`) it prints `implementations=35 joined=0 classes_spanned=0`. With the head instrument it prints `implementations=35 joined=26 classes_spanned=3`, which matches the body.
   - Its `family()` equals `arch-s2/shape_payload_guard.py`'s once unparsed, except for the dropped type annotations.
5. **The #2373 general limit is stated.**
   - `ABOUT.md` now says C20/C21 fold spellings, not values. It names the class attribute and the constant expression (186 -> 182 each), and says a literal census is a floor.
   - The superseding R10-BRIEFS-FOLD carry ("normalise a finite list of spellings ... credited only when the copies are actually gone from the source") is on the roster branch `handoff/audit-r10-roster` (PR #2384, open). It is not yet on origin/main.

## Also checked

- **Today's tree:** `shape_copies` reads 66, `card_clone_copies` 108, `card_dead_definitions` 0, `literal_clone_copies` 186 and `hub_solve_writes` 41. The four new `ci_budgets.json` rows match, and main's merged production changes move none of them.
- **CI at this head:** 45 check-runs, 30 success and 15 skipped, none red. `arch-score`, `fast (3.14)`, `closures`, `pr-contract` and `budget-raise-gate` are all green.

## Owed (not blocking)

- **To the orchestrator, before or with this merge:**
  - Land #2384, which carries the R10-BRIEFS-FOLD general-limit carry, so the destination holds it on main.
  - Route #2259 item 2's card duplicated-spellings census, and the #2235 RCA, both carried in the body. #2259 and #2235 stay open, to be closed by hand.
- **To tvofi at merge (mandate 6175172275):**
  - `tests/ci_budgets.json` gains four new rows: `archscore.card_clone_copies` 108, `archscore.card_dead_definitions` 0, `archscore.literal_clone_copies` 186 and `archscore.shape_copies` 66.
  - `tools/audit/archscore/calibration/expected.json` gains 23 cases (part 4's 17, part 5's 5 and `rt_20b`), with no deletions.

## Not verified by me

- The full `--record` and the corpus re-measure, which are CI's `arch-score`, green.
- The mutants M2-M4 and M17-M21.

Evidence: ~/hpo-seats/r10s3/review-2401/evidence2
