Fix review: blocked 6514ed1a915edd34dd7856782fa56d085554ff81 scope-and-carry: price-of-a-degree producer exists on main (score sensor price_tiles) and is undelivered; hot-water row unpriced at the default 55 °C; ranking test survives a no-sort mutant; body's carry-1795.json carries nothing

R9-UX-2, PR #1836, round 1. Measured code head 6514ed1a (merge base 8f496ce1). Live PR head e0178c26 = 6514ed1a + main 3bd6f122 merged + docs/delivery/1836.md; `comm` of the two sides' changed files since 8f496ce1 is empty, so these findings hold at e0178c26 unchanged. Contract copy current (`git diff <mb>...origin/main -- tools/audit/briefs/` empty).

## Blocking

1. scope: the brief's "price-of-a-degree tiles when their option is on" is undelivered, and the body's departure rests on a false measurement. The producer exists on main: `OptimizationScoreSensor.extra_state_attributes` publishes `price_tiles` (custom_components/heatpump_optimizer/sensor.py:2623 at the head), filled by `_price_tile_specs` / `_maybe_refresh_price_tile` (coordinator.py, `target_minus_1`, `target_plus_1`, `power_cap_75`, each with `monthly_cost_delta`), gated by `price_tiles_enabled` (const.py:1026, default False). PRE-STUDY-UX.md (1a90e4cb) names exactly this: "attribute on the score sensor, opt-in". The score sensor is enabled by default and the card already reads it (`_plan_optimization_score` in HEADLINE_SUFFIXES), so no entities.py refusal applies. The body's grep (`of a degree|price_per_degree|degree_price`) did not match `price_tiles`. DESIGN-UX row owed: "price of a degree, when enabled: 'Try in what-if' opens the simulator with ±1 °C".

2. defect: the hot-water row carries no money on a default install. `advisorRows` prices it by exact lookup of `current_setpoint` in `candidates`; the sweep is `range(48, 61, 2)` (coordinator.py `_dhw_setpoint_sweep`) and DEFAULT_DHW_SETPOINT is 55.0 (const.py:1134), so `cost(attrs, 55)` is NaN and the row reads "no estimate" and ranks last. The test fixture uses current_setpoint 60, one of the swept values. Probe P1 (fixture current_setpoint 55, production sweep shape 48..60 step 2): `FAIL a priced row shows its monthly value as an estimate` (probe_p1_setpoint55.txt). Any odd or off-grid setpoint does the same.

3. mutation: the ranking check is satisfied by the fixture's own order. Mutant R1 (`return rows.sort(...)` -> `return rows;`) survives: ALL CARD CHECKS PASSED (mut_R1_no_sort.tail.txt). The body's "the ranking check is not satisfied by any order" is false for the identity order; the fixture needs rows whose build order is not their rank order.

4. carry-missing: the Forward-carry names `.claude/workflows/carry-1795.json` for both carries (UX-5 open_schedule -> apply; a later stage's price-of-a-degree read). `git diff 8f496ce1 6514ed1a -- .claude/workflows/` is empty: the file at the head is R9-UX-1's carry only, and `git grep open_schedule` over .claude/ finds nothing. Not carried to R9-UX-5 in the tree (finding-propagation.md, "verify the write landed"). Carry 2 becomes moot once item 1 is delivered.

## Also surviving (not blocking alone; fix with the round)

- R3 (`!(value > 0) ||` dropped from the gap row): survives; a gap advisor at 0 (every slot filled) would show an "Add a … sensor" row valued 0.
- R4 (`to === from` dropped from the hot-water row): survives; an advisor already at its recommendation would show a no-op row.
- R6 (valve target unrounded/unclamped): survives.
- Waiting and error states: the fixtures put `waiting_for`/`reason` on `unavailable` states, which Home Assistant suppresses (sensor.py `_WaitsForEvidenceMixin` docstring: "Home Assistant suppresses extra state attributes while an entity is unavailable"), and none of the three default-on advisors emits `waiting_for`; `first_dhw_cycle` is no producer's code. In production the waiting branch is unreachable and an unavailable advisor shows the error row with no reason. Say so in the body or read the reason where it is published.

## RESULT lines

- RESULT card.mjs at 6514ed1a: rc 0, ALL CARD CHECKS PASSED (card_head.txt; plan_view.py rc 0 first).
- RESULT card_drift.mjs vs 8f496ce1: rc 0, every moved state CLAIMED (output 14 MB, not kept).
- RESULT merge-tree origin/main(3bd6f122) x 6514ed1a: rc 0, tree 5acf2597, no MERGE-CLAIM line.
- RESULT VERSION, manifest version, RELEASE_NOTES heading: untouched.
- RESULT mutants (mine): R2 killed, R5 killed, R7 killed; R1, R3, R4, R6 survived; R8 not applied (string not unique).
- RESULT CI on e0178c26 at 2026-10-01T23:58Z: no red conclusion; Tests not yet reported; two cancelled runs superseded by green reruns (pr-contract, budget-raise-gate).
- Harness: mine (mutants and P1 are hand edits in a scratch worktree); no finder harness exists for a feature PR.
