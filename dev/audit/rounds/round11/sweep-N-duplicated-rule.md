# Class sweep: N-duplicated-rule (round 11, PLAN phase D)

Class: one rule written as several agreeing copies where a single-owner prototype is admissible.
Not yet in `dev/audit/config/bugclasses.json` (no entry, so no status: new this round, effectively `open`).
Finding: D7-s1-05 (weakened, low, hygiene).

## Enumerator
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_sites.py | grep '^SITE duplication_copies'`
-- the package-wide clone census behind `duplication_copies` (tests/structure.py:duplicate_clones via
archscore's gapped window). Returns 14 clone classes, 18 copies, on handoff/audit-r11-register (28b864af6d).

## Controls
- Positive: re-finds all 14 classes D7-s1-05 lists (8 prototyped + 6 needing a design), exact.
- Null: `dev/audit/rounds/round11/D14/sweep_n_duplicated_rule.py` -> `NULL classes=0` on a clean fixture.
- Perturbation: same script, one copied function added -> `PERTURB classes=1 members=['a','c']`, exit 0.

## Disposition of every seam
Instance (judged sites of D7-s1-05, beyond_finding=false; probe: `m7_prototypes.py --score --only <arm>` admissible, reverts to +0.0000):
1. drift._note / power_guard._note (note)
2. binary_sensor/climate/sensor `available` (avail)
3. pump_arbiter._step_index / _planned_room (step)
4. price_model.observe_day / observe_day_quarters (day)
5. coordinator._update_current_state / _update_external_heat_detection (reader)
6. sysid._lm_solve / _slab_ua_profile_halfwidth (fdjac)
7. ledger.add / observe_meta_mean (entry)
8. legionella.check_overdue / check_mode_block (notice)

Not applicable (no admissible single-owner prototype without a design; the class requires one):
9. inputs.read / read_state -- shared statements are the `_begin` guard; one owner inverts control.
10. optimizer._optimize_space_only / _optimize_with_dhw / _solve_space -- golden-sensitive solve paths.
11. optimizer.objective / objective_batch -- scalar/batch twins, merge changes float order.
12. tariff._smooth_topk_sum / _smooth_topk_sum_batch / peak_cost_batch -- scalar/batch twins.
13. thermal_model._simulate_step_single / _simulate_step_two_zone / simulate_trajectory_batch -- twins.
14. thermal_model.simulate_trajectory / simulate_trajectory_with_dhw -- twins.
These go to their owning seams' designer briefs (finding-propagation.md), not to this class.

Out of the enumerator: `literal_clone_copies` (118, constant-literal clones) is a different metric and
mechanism (repeated literals, not repeated statements); not swept here.

## Result
instances beyond the finding: 0. Barrier: partial -- `duplication_copies` is a ratcheted budget in
tests/structure_budgets.json, so growth is refused, but an agreeing copy is not refused while the
count is paid elsewhere; barriered=false. Proposed barrier: none beyond the ratchet (count stays at 0
beyond-finding instances; cost of a per-class owner check is not justified by this yield).
