Fix review: merge c1ad2ede5308d1a9f25379c88f10502b387b0fb2

bus-nonce: 2e780144a750d6921aaaf5a3ea986dcb

Note: packet-unavailable: `bus.sh dispatch` printed `review-packet: unavailable -- git merge-base --is-ancestor b2ce461c origin/handoff/audit-r10-roster: fatal: Not a valid object name b2ce461c`; the review ran from fix-review.md at origin/main (the roles diff from the merge base to origin/main is empty). Carry: dismissed: an instrument condition of the packet renderer, not this pull request's code.
Note: cpu-class: the restated "the choice is live" check still reads scores of non-convex committed plans (now over every commit call of two days rather than one final objective); measured here on arm64 only, CI x86 is its authority and is green at this head. Carry: dismissed: the check's own comment names the CPU-class dependence it removes; no seat owes more.

## Scope

Round 3, a delta review (the owner's 2026-11-09 rule): `git diff b77df3f88d8664d606bc92e2eaaf79f4d7971ce2 c1ad2ede5308d1a9f25379c88f10502b387b0fb2`. `review_carry.py b77df3f8 c1ad2ede` printed FRESH-REVIEW. The own diff (merge-base-relative at each head, 5dd66fd994 and 99436a082c) differs in exactly `tests/features.py` (75cac35ee6: the descents check restated at the commit stage) and the delivery row renamed `3709.md` -> `3805.md`. `git diff b77df3f8 c1ad2ede -- custom_components/` is main's `rooms.py` docstring only (#3803), so no production line of this PR moved and the review does not widen.

## Evidence

- RESULT unmutated, arm64, detached worktree at c1ad2ede: the R10-DUTY-SWITCH-PLANNER-PRICE block (`features_block.py`, marker `# --- R10-DUTY-SWITCH-PLANNER-PRICE block start` to `R.section("R11-OUTSIDE-HONEST-STARTS-RUNS`, emitted prelude) `ALL 104 FEATURES BLOCK PASSED`, both restated checks `ok` (`ev/unmutated.log`).
- RESULT mutant M1, `_commit_runs`' `return min((` -> `max((`: `4 of 104 FEATURES BLOCK FAILED`, among them `a solve that prices a stop commits both descents and ships the lower ...` (`ev/M1_min_to_max.log`). Killed.
- RESULT mutant M2, `for space in relaxed` -> `relaxed[:1]` (only the first descent committed): `3 of 104 FEATURES BLOCK FAILED`, among them both restated checks, `... ships the lower` and `and the choice is live ...` (`ev/M2_first_descent_only.log`). Killed. Driver `ev/mutant_driver.sh`; `git status --porcelain` empty after each restore.
- The restated check pins the decision `_commit_runs` makes (one committed plan per descent, the lowest-scored shipped) instead of the final objective of one non-convex solve per arm; the dropped comparison is the non-guarantee the body's `## Forward-carry` already routes (unchanged since the reviewed head). `_dsp_days` stays in use by `the relaxed descent still leaves a priced switch`, unchanged.
- Merge with main: `git merge-tree --write-tree origin/main c1ad2ede` rc 0; `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt`, `LEDGER-MERGE: resolved tests/structure_budgets.json`, `LEDGER-MERGE: resolved tests/closures.json`.
- Step 5: the delta touches no `VERSION`, manifest or `RELEASE_NOTES.md`.
- Step 7: the body's `## Head` names c1ad2ede5308d1a9f25379c88f10502b387b0fb2; the PR head read back at c1ad2ede before posting.
- Step 11: CI code run 44536189143 completed success at this head (gate job 135745855726 success). The edit run's gate job 135665462830 failed with `run(s) [44536189143] at this head are still being judged; their gate decides`, not a real red; its failed jobs were re-run. `merge_train.py classify` printed GREEN before minting.

## Prior findings

- Round 2's verdict (merge at b77df3f8) had no open blocking finding; its notes concerned figures this delta does not touch.
