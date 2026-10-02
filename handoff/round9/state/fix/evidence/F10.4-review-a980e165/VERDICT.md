Fix review: blocked a980e1650524c3782976e0631b2b4271ee797435 census-hole: dead_members counts a member typed-live when its name collides only with another class's data attribute, so DefrostDerate.samples (base) and coordinator.solar_radiation (head) are neither dead nor in the printed name-kept set; 21 such members at head are missing from the "92 printed" residual

PR #1838, round 1. Code head measured: a980e165 (handoff/r9-f10-gate-infra-4, unchanged at posting). PR head 832e640c = a980e165 + docs/delivery/1838.md only (carry). Body b4293ab5. Base 3bd6f122 = origin/main. Briefs current (`git diff merge-base...origin/main -- tools/audit/briefs/` empty).

## The blocking finding

`tests/structure.py:1506 dead_members()` builds `by_name` from class-body **functions only**. An untyped `x.n` load is then treated as typed (`len(by_name[n]) == 1`) whenever no other class has a *method* named `n`, even when other classes have a *field* or `self.n` store named `n`. Such a member is counted live and kept out of `name_kept`, so it is neither measured nor printed.

The docstring names the shape this exists for, "DefrostDerate.samples stood alive behind AccuracyTracker.samples in every name-based view". Under this head's definition at base 3bd6f122, `DefrostDerate.samples` is still neither dead nor name-kept. At head, `HeatPumpOptimizerCoordinator.solar_radiation` (dead; EG-B2's scope) stands alive behind `ThermalState.solar_radiation` (`coordinator.py:4737`, `thermal_model.py:1232`) the same way.

The reviewer's own probe (not the finder's) re-runs `dead_members()` with every other class's fields added as phantom same-name members: `probe_field_collision.py` in this directory.
- RESULT field_collision_unprinted=21 count (head a980e165), 22 at base under the new definition (the extra is DefrostDerate.samples)
- RESULT name_kept_reported=92 count (both)

So the body's residual, "92 members are kept by name … structure.py prints them", under-states the unmeasured set by 21 (113 at head), and the I4 barrier still has the hole the PR's own docstring cites as its motivating case.

Fix, within this PR's own new code: count class-body assigns/annotations and `self.n` stores of other classes into the collision test that decides typed-live (liveness unchanged, classification only). Plant a self-check case ("a property whose only load is `x.n`, where another class has a field `n`, is name-kept, not measured-live"), and re-state the printed count in the body. `dead_methods` does not move (all 21 stay live), so neither does the budget.

## Checked and holding

- Base under the new definition (head's structure.py + seam_map.json over 3bd6f122, `current_action: core` added to the copy's seam map): RESULT dead_methods=9, coordinator_multiassigned_attrs=120. Head: 3 and 120. Both figures in the body re-derived. `structure_base_newdef.txt`, `structure_head.txt`.
- Head ratchet: STRUCTURE RATCHET PASSED, 40 counting rules hold, rc=0.
- Finder harnesses, base -> head: `reach.py --list` dead_reachability_total 10 -> 4 (3 EG-B2 properties + ENTITY_FAMILY_OVERRIDES const); `screen.py --no-property-exclusion --attribute-only` 11 -> 3. Head lists exactly last_optimization, next_optimization, floor_return_temp.
- Mutants (`mutants.py .`): unmutated rc=0 []; all 12 mutants red. `mutants_head.txt`.
- doc_claims at head: ALL 112 checks PASSED. Renaming `## Initial setup` gives a named anchor FAIL (1 of 107) rather than IndexError. `doc_claims_*.txt`.
- VERSION, manifest, RELEASE_NOTES.md, tests/golden: untouched. `git merge-tree --write-tree origin/main a980e165` rc=0.
- Not re-run: the gate and mutation table (CI's, per step 11), entities.py, and env_drift (no golden in diff). There is no CI run on the PR yet to cite, and red checks are unread for the same reason.

## Budget re-baselines (tvofi's call, not approved here)

- `dead_methods` 0 -> 3: the old 0 was the I4 blindness. Base measures 9 under the new definition and the head 3; the 3 are EG-B2's agreed deletions. A restructure could only avoid this by deleting them here, which the scope split forbids. Honest at the measured value.
- `coordinator_multiassigned_attrs` 117 -> 120: base measures 120 under the new definition (it now counts writers outside the class). Nothing in this diff adds a writer. Honest at the measured value.
- Plan card B5 (F10.md) pre-allows a coordinator budget raise to the measured value, merging only on tvofi's approving review. Both of these qualify. The fix above changes neither number.
