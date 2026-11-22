Fix review: merge 48d28b55eb156a8b2585296d7d786f63f67d1247

bus-nonce: dc0e98e6e82cdd056a0c65ae908c572a
pending-ci: gate

Round 2 (delta review after round 1's `blocked 6ef32c22f3 mutation-vacuous`; `review_carry.py 6ef32c22f3 48d28b55eb` prints FRESH-REVIEW, because the branch's own commit `ffb12a9319` changes content).

Note: body-garbled: the `## What it does` lead paragraph has the round-2 mutation-proof text spliced into it. The sentence "measured under `C1, the review's mutant ..." runs on to a stray "## Null control`)." inside the paragraph. `## Head` names three SHAs, and only the first sentence describes 48d28b55. The figures in it are correct (see Evidence). Carry: dismissed: paperwork on this PR's body, which the author's next body write replaces.

## Findings

- Friction: `tools/audit/seat/features_block.py --emit-prelude` leaves out `import asyncio as _asyncio` for the P2 block. `_t5_drive` catches the NameError inside its own `try`, so the emitter sees a block that runs cleanly. The block then fails later with `IndexError` at `_rl_c_on._rl_margins[0]`. Both the author and this review had to add the import to the prelude by hand. The body already names this as a round-end proposal. Carry: dismissed: the author already routed this instrument gap to round-end triage in the body; one instance, no stage brief it constrains.

## Evidence

- Head reviewed: `48d28b55eb156a8b2585296d7d786f63f67d1247` (`ev/HEAD.txt`). It is the live PR head and the head the body's `## Head` names. Merge base `f269ecccb5f1dfd21eca03a3d5dcc43b3a145603`.
- Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merges with main: `git merge-tree --write-tree origin/main 48d28b55eb` exits 0 (`ev/mergetree.txt`).
- Delta since round 1. The PR's own `custom_components/` diff is line-for-line identical at both heads: `git diff 35402f7817...6ef32c22f3` vs `git diff f269ecccb5...48d28b55eb`, over `custom_components/`, compared on +/- lines only. The branch's own new content is `ffb12a9319` (`tests/features.py` only), plus the bot's `dd4c90c425` killed_by pins, the delivery row `5ac06973d1`, and main merges. No production delta, so the review does not widen.
- Round 1's block is resolved. The P2 block was run with `features_block.py` (start `#3616 R11-OUTSIDE-ROOMS-P2`, END `R.section("R10-DRAW-MAP-EVIDENCE part A`). The prelude was emitted at this head with `import asyncio as _asyncio` added (`ev/P2_prelude.py`). Driver: `ev/run.sh` and `ev/c1.py`. Output: `ev/mutants_P2_block.txt`.
  - Unmutated: `ALL 26 FEATURES BLOCK PASSED`, rc 0.
  - C1, both splat builds take `floor_limits(...)["min_temp_margins"]`: `2 of 26 FEATURES BLOCK FAILED`. Both new checks fail with `lifts=None`.
  - C1a, the scheduled build alone: `2 of 26` (the what-if check compares to the scheduled lifts).
  - C1b, the what-if build alone: `1 of 26`, the what-if check only. So each build has its own killing check.
  - C1c is this review's own mutant, not the body's: the what-if's `floor_limits` gets the baseline `config` instead of `scratch_config`. It fails `2 of 26`: the new what-if check (no 0.5 K clip at the 19.5 target) and the existing P2 what-if clip check.
  - The body's figures (24 → 26 checks; 2, 2, 1 failures) match these runs.
- Round 1's other mutants (A1 to A18) and the null-control harness `dev/audit/harnesses/room_lift_solve.py` were not re-run. Production code is unchanged, and the only test delta adds checks.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). `tests/structure_budgets.json` against the merge base moves only `class_excess_loc` 17317 -> 17301 (down) and `recorded_at`. No budget is raised.
- `tools/audit/archscore/score.py --diff f269ecccb5` (merge base) at the head: `Architecture score: dS +0.0000 NULL` (`ev/archscore_mb.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched against the merge base.
- CI on this head:
  - `tests / mutation` is red with `MUTATION TABLE REFUSED -- 1967 unpinned site(s) against 1950 ... 22 of them added by this diff` (`ev/mutation_lane_tail.txt`). These are the `ADDED UNPINNED` sites the body lists under `## Unpinned sites`, and it answers them under `## Red checks` (the `mutation-autofix` pinning step, detected earlier by `prepr.sh` step 6d).
  - `gate`'s early failure is the gate's own timing, as at round 1.
  - Classify printed `WAIT ... pending: gate red: none` from 03:33 to 04:02 UTC (`ev/classify.log`), so the verdict carries `pending-ci: gate`.
