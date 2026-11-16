Design review: revise ef9b12e7dd92d347b17d3f2d51a089630540861f golden-unclaimed

Round 2. I read design.md at ef9b12e7dd in a detached worktree and the code at d4968fe08b. The note's base, 5825e1346c, is an ancestor of d4968fe08b, 124 commits back. Group credited: outside pull request 3529 by Bankaifan.

## Round-1 revise point 1 (class-open, user surface): answered

The note now designs the parts round 1 asked for: three new floor attributes, two translated enums in strings.json and the en, de and sv files, the pin at tests/entities.py:13064, and the paragraph for docs/how-it-works.md:1220. The max row stays byte for byte, and the limit sentence now names the entity and the docs as the way down. At d4968fe08b, `_pump_max_power` is at sensor.py:2095-2106 and the pin set is at tests/entities.py:13063-13066.

## Revise point

1. golden-unclaimed (evidence plan, design-review.md step 4). design.md, "Evidence, by file", says "`python3 tests/env_drift.py --all`: no golden carries a draw window; both claim files byte-identical". Null control (a) asserts the "max attributes identical to the base". Both statements are true of the max row, but the design adds three new keys to the Learning Model Status entity. `_pump_max_power` (sensor.py:2095) writes its keys even when there is no band: the row is None and the codes are `b.get(...)`, also None. So every coord capture gains three null leaves under `sensors.model_status.extra_state_attributes`: tests/golden/coord_minimal.json:1903-1905, and likewise coord_all_features, coord_dhw, coord_grid_fee and coord_two_zone. tests/golden.py:1488-1489 reports each one as a "new field" DIFF. R10-COP-GATE-D set the precedent at tests/golden/claimed_drift.txt:744-753 (commit ee92b1b2f6). It claimed those five fixtures' added keys, recording the direction as ADDED and stating that no other leaf moves. It did not re-record them. Fix wanted: name the five coord fixtures as goldens that move. Name the claim line each takes in tests/golden/claimed_drift.txt, under the `claims-for:` live at build time, with ADDED as the direction, written the way R10-COP-GATE-D's was. Keep tests/golden/card_claimed_drift.txt byte-identical. Restate null control (a): the band, the plan and the existing max attributes stay identical, and each fixture's diff is only those three added null keys, measured with env_drift --all. The parent note's sentence "C moves no golden" (a63a2ca6cd) no longer holds once C publishes on the entity, so say so. The parent group R11-OUTSIDE-HONEST-STARTS-RUNS also claims coord_all_features, so whichever of the two lands second merges its claim line through the claimnotes driver.

## Decision still routed (not a revise point)

- decision: orchestrator. Round 1 routed whether C also raises a notice through issues.py (brief bindings 1 and 4). The note now gives its own answer, no notice, and a fallback shape. The scope is still the orchestrator's to settle.

## Convergence claim (carry 1): attacked again, held

The note has the same shape as in round 1: evidence E at the floor in force, n reset on every move, no age lapse, and moves only by more than a factor of 1 ± tol between the configured floor and the top. Round 1's argument holds unchanged, and the note now states the premise g_f(f) = m (`_band_kw` maps on `planned_min_kw`, pump_arbiter.py:702). The r2 alignment paths (WINDOW eviction, the clamp in `from_dict`, both clears in `observe`) are designed and tested in test 6. The new attributes do not touch E or its statistic.

## Notes for the fixer (carried observations)

- Reason code "agrees" is designed as "F unset, E full", with the text "Configured: the metered minimum agrees with it". The shape never lowers F under configured, so an install whose statistic over E is below (1 - tol) x configured also returns "agrees", and that text is false for it (brief binding 4). Either give that branch a code whose text holds, as the max side's `not_below_configured` does, or word the text one-sided, for example "does not exceed it". Test 7 then reaches that branch. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item v2a)
- tests/features.py:87852-87873 (carry 6) pins the max codes against strings.json and SHIPPED_CATALOGUES. Test 7 should extend that same check to the two min attributes rather than add a second loop. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item v2b)
- A new attribute or docs line can shift dev/audit/rounds/round4/D6/claims.{json,md}. ee92b1b2f6 regenerated that register for the same kind of change. Rerun its generator at the head. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item v2c)

## Checked and clean

- Seam: draw_range.py stays the only owner. The update and the store reader are module-level, `_run_asked` has keyword defaults, and there is no second sample store.
- Siblings in flight: I re-read the design/* refs. R11-OUTSIDE-SELF-SETTING-PUMP reads draw_range.py and leaves it unchanged. No other open design touches `_pump_max_power`, the learning_model_status strings or how-it-works.md:1205-1221. archive/design/R10-DRAW-MAP-EVIDENCE is still not on main.
- Sibling sites: the readers of `pump_max_power` at d4968fe08b match the note's list (coordinator, payload, sensor, the four string files, entities, docs). The goldens above are the exception. tests/golden/config_flow.json's hits are `heat_pump_max_power`, the configuration field, which is unaffected.
- Size: an M group with new files only in user text. The churn fits.

Token count: not reported by this harness.
