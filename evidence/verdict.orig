Fix review: merge 4c1352f05aa6797e06a7af5fdc456039756f2bcc

bus-nonce: 32b6b8e877c99d08025855e9cef03a8e

Round 3. Earlier rounds:
- Round 1 blocked 3aba8f1eb as vacuous-test (M10). It was resolved at this head; round 2 verified that.
- Round 2 blocked this same head as architecture-unsound. No roster edit amended the R10-VENT-DETECTOR architect note.

Head measured: 4c1352f05aa6797e06a7af5fdc456039756f2bcc (`ev/HEAD`). `git ls-remote` just before writing still returns it (`ev/ls-remote.txt`).
Base: merge base fa16596c3. My contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Step 15 -- the amended architect note (round 2's blocker)

The orchestrator amended the note at handoff/audit-r10-roster d1efd583c, which is still that branch's tip. The amendment is appended to the group's `brief`:

> "ARCHITECT NOTE AMENDED ... the Shape clause ... is satisfied by the detector folding the residual's departure from a tracked reference (level plus heat and sun slopes, fitted by forgetting least squares) ... A residual input with a tracked reference is accepted in place of an independent input."

Non-blocking: the group's separate `architect_note` field still carries the old text. The orchestrator may want to keep the two fields in step.

I judged the added lines against the amended note.

**Shape.** It matches the amendment.
- `Cusum._departure` takes the departure against the reference before this sample moves the fit, then clips it.
- It runs a recursive-least-squares step on the clipped departure, with exp(gap/24 h) forgetting.
- Each variance is capped at the prior by a diagonal D·P·D scaling. That scaling keeps the covariance symmetric positive-definite.
- The first sample seeds the reference clipped. A change in the regressor count re-seeds.
- `_cop_health_cusum` is unchanged: `reference_hours` is None and its payload is identical.

**Feed.**
- `previous_power` cannot be None at the call: it returns earlier at coordinator.py:5055.
- `solar_radiation or 0.0` covers an unknown irradiance.
- `update` refuses non-finite regressors.

**Load.**
- A fit loads only if every cell is finite, each covariance cell is within the prior, and the matrix is symmetric positive-definite.
- Anything else drops the whole fit, and the next sample re-seeds it. That matches the `store.DOMAINS` rows.

**Seam.** The drift.py, store.py and const.py hunks are outside the owning seam, and the body discloses them.
- At d1efd583c, every not-started group listing those files comes after R10-VENT-DETECTOR in the after graph: R10-NIGHT-FOLDS, then R10-RATIO-ANCHOR, then R10-INPUT-STALENESS, then R10-HEAT-METER.
- The other groups listing them are done: R10-FAHRENHEIT, R10-STORE and R10-LEAF-IMPORTS.
- So no after-edge is missing.

**Cost.** The shape's cost is measured in the body and re-derived in round 2, and the amendment accepts it knowingly. The 100 W/K x 8 h window is detected on 17 -> 0 of 20 arms, and 150 W/K x 4 h on 20 -> 16.

Nothing in the added lines departs from the amended note.

## Re-measured this round (files in ev/)

**Mutation proof.** Each run is the full `PYTHONPATH=tests/hastub python3 tests/features.py` on its own worktree of the head.
- M0, unmutated: `ALL 4213 FEATURE CHECKS PASSED`, rc 0.
- M1, departure against zero (`departure = self._clipped(value)`): `7 of 4213 FEATURE CHECKS FAILED`. That is exactly the body's 7 named checks.
- M10, the feed's sun regressor set to 0.0: `1 of 4213 FEATURE CHECKS FAILED`. The failure is `a bias scaling with the sun never trips the detector ...`, which trips at 2026-01-16T10:30, as the body says.
- Files: `features_*.log`, `mutant_*.diff`.

**Finder's harness.** `ident_rolling.py --delivery 0.4`, both plants, run at base fa16596c3 and at the head:

| plant | arm | base | head |
|---|---|---|---|
| P0 | fix1.00 | 0.187 | 0.000 |
| P1 | fix1.00 | 0.172 | 0.000 |
| P1 | fix2.00 | 0.210 | 0.006 |

- ua_bias fix1.00 is identical at both ends: P0 +0.5174, P1 +0.4374.
- These match the body and round 2 (`ident_*.txt`, `ident_summary.txt`).
- Not re-run: the remaining arms of this harness, and the planted-window harness, the companion and the catch-up verifier. Round 2 re-derived every one of their figures at this same head, and production code has not changed since.

**Step 5.** The diff touches no VERSION, manifest, RELEASE_NOTES, golden or claim file.

**Structure.** `STRUCTURE RATCHET PASSED`.

**Step 10, forward-carry.** At d1efd583c, R10-NIGHT-FOLDS.carry holds both carries, each with its control stated as a precondition at that group's merge base and head (`carry_night_folds.txt`):
- (1) the night predicate goes after the `_vent_cusum.update` feed;
- (2) the sun-slope transient.

**Step 11, CI.** The check-runs API at this head lists 48 runs, all completed: 33 success, 15 skipped, none red (`check-runs.txt`). The earlier reds on the branch are named and answered under `## Red checks`, as verified in rounds 1 and 2.

**Step 13, merge.** `git merge-tree --write-tree origin/main(abb397938) 4c1352f05` exits rc 0 with tree 9f0905800 and empty stderr (`merge-tree.*`).

**Step 7.** The body's `## Head` names 4c1352f05. Non-blocking, as in round 2: its stray `bd51be062` paragraph names a commit that does not exist.
