Fix review: blocked fab2d371ede00e9168843c18f6c47dc2425046f9 class-open: coordinator.py:6134 room_record.House reads the plan split as the space share, returned by design section 5 E3 at the head and not dispositioned

bus-nonce: 0ee7b269f4cb6d6b3577baf11e1f6930

Round 1 of this reviewer seat on #3835 (no `--reviewed-head`, review scope full), at head fab2d371ede00e9168843c18f6c47dc2425046f9, merge base 608c95decc94a8240565aba68fa8f0e1dece8c3d.

## Block

- class-open (fix-review.md step 6). The body names its enumeration rule as design section 5's greps E1 to E3 (`## Figures`, item 9b3d1e22), and the design says the fixer re-runs them at the merge base, where a printed line that the tables do not name is a new site. At this head E3 (`git grep -n -E 'get\("(dhw_power|dhw_heating_active|power)"' <rev> -- custom_components/heatpump_optimizer/coordinator.py | wc -l`) reads 15, not the body's "E3 14 / 14": 14 at 78d3b40221, 15 at the merge base 608c95decc, and 15 at the head (`ev/class_enum_E1_E3.txt`). The added line is `coordinator.py:6134`, `room_record.async_note_cycle(..., room_record.House(..., self._measured_power, float(self._current_action.get("power", 0.0)), float(self._current_action.get("dhw_power", 0.0))))`, from main's 2c2f17f749 (#3616), which is not in 78d3b40221. The diff does not touch it, and no body or design row (listed, covered downstream or excluded) names it.
- It is a reader of the class. `room_history._accumulate` counts a cycle as space when `house.space_kw > 0.0 and house.dhw_kw <= 0.0`, which is the plan split. That share is stored in the persisted ring (`HOUSE_FIELDS` "space"). `_house_line` then keeps only periods with `space >= CALLING_SHARE` and fits measured power against the rooms' calling fraction there, which is "the curve phase 3b fits". An unobserved, plan-space-only cycle whose tank rose past `UNPLANNED_CHARGE_RISE_K` (this PR's `heat_energy.unplanned_charge`) is counted as space while its measured power charged the tank, so the house line's slope takes in tank power. This is #3760's mechanism, on a reader the PR's own rule returns.
- What clears it: dispositioning the site in the body under design section 5's tables. Possible routes are an exclusion with its reason (the module states its report goes to diagnostics and one sensor), routing to the seam that owns room history, or reading `_space_evidence` / `HeatEnergyMeter.unplanned_charge` there. The E1 to E3 counts would then be re-taken at the merge base. E1 (35 at both 78d3b40221 and 608c95decc, 42 at the head) and E2 (57 at all three) add no main-side line. The 7 lines E1 adds at the head are this diff's own readers, as the body says.

## Findings

- Two of this reviewer's own mutants survive the whole `tests/features.py` at this head (see `## Evidence`, mutants O and P). The first is the lower-floor learner's per-cycle ask without `evidence=_space_evidence(...)`, at `coordinator.py:5940`. The second is the house learner's per-cycle ask without it, at `coordinator.py:5780`. The body's sweep list does not name these two per-cycle asks (it names `_interval_space_power`, `_interval_measured_heat_kw` and the span close). No check fails when either evidence argument is dropped, so either they are redundant with `_interval_space_power` / `_interval_measured_heat_kw` returning None on an unplanned charge, or they are unpinned. The next round either pins them with a check that tells the two apart, or states in the body that they are redundant, with the measurement that shows it. Carry: dismissed: owed by this PR's next round, which this block returns to the fixer
- Design section 5's plan-flag-off charge arm (`m5_tankfall.py` `booked_kwh_unplanned_max`) reads 3.0160 kWh at both ends in this reviewer's run, past the 0.05 kWh band. Design section 5 says to build this site in this PR in that case, and the PR does not build it. The departure was raised in blocked-stop 0c859e0ca4 with its reason. The orchestrator's answer (inbox/r11-seam-learners entry 1) rules on section 3.3 only. This reviewer confirmed the reason in the tree: `DrawStats.take_back` (`dhw_draws.py:87`) removes `_open_charge_kwh` only, so a dip folded with `charge=False` cannot be taken back. The carry is in the roster at handoff/audit-r11-roster 582010efc2 (R11-SEAM-learners' carry list, the text moved from carry-3769.json), and it states its control, the remeasure and the brief. Whether an unbuilt design row needs the design reviewer's acceptance rather than the orchestrator's silence is for the orchestrator. Carry: #3769

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main fab2d371ede00e9168843c18f6c47dc2425046f9` exit 0, tree ee742d9556; `LEDGER-MERGE: resolved tests/closures.json`. origin/main at baa9a467ac.
- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Mutation proof (step 1), driver `tools/audit/seat/features_block.py` with a prelude from `--emit-prelude` at this head, on the block `R.section("R11-SEAM-learners: the one freeze predicate")` (both learner sections). Restored: `ALL 22 FEATURES BLOCK PASSED` (`ev/block_clean.log`). This reviewer used 17 mutants of its own, different from the body's table (`ev/mutants_learner_block.log`). The block kills 14 of them:
  - A, tank pair never shifts
  - B, the span's opening tank read never set
  - C, `unplanned_charge` ignores `observed`
  - D, the `at_running_floor` tolerance sign flipped
  - E, `if occupied: return occupied` dropped in `dhw_learning`
  - F, CEILING dropped from the room-air kinds
  - G, away recovery raised by away
  - H, the unplanned charge stops refusing METERED_SPACE_HEAT
  - I, the boost reason dropped
  - J, the unusable-key loop dropped
  - K, `_freeze_facts` with `away_recovery=False`
  - M, the span-close freeze note deleted
  - N, the quiet-comfort ask back to ROOM_AIR
  - Q, the draw-range window fold without the unplanned evidence

  The block does not kill L, O or P, so each ran under the whole `tests/features.py` in its own worktree (`ev/features_full_mut{L,O,P}.log`):
  - L, `_freeze_facts` drops the `reading.entity_id` guard: killed by "an unconfigured slot never freezes learning".
  - O and P: see `## Findings`.
- Finder's harnesses (step 2), this reviewer's runs on Linux, venv-ci python3, `OPENBLAS_CORETYPE=Haswell`. Each is the head's file, with sha1 equal to the body's (`ev/harness_sha1.txt`), copied into a base worktree at merge base 608c95decc (which now holds #3737). Every body figure re-derives exactly (`ev/harness_*_{base,head}.log`):
  - `m3_learner_freeze.py` `contaminated_ingest` 3 -> 0.
  - `m5_tankfall.py` `booked_kwh_long_max` 3.0160 -> 0.0000, `booked_kwh_short_max` 0.0389 -> 0.0000, `booked_kwh_unplanned_max` 3.0160 at both ends.
  - `m5_drawrange.py --run-samples 200` `narrowing_censored_kw` 4.100 -> 0.000. Null `uncensored_overstated_learned_max_kw` 4.000 at both ends.
  - `m5_crosscov.py` `gain_recovery_mean` 0.5573 -> 0.7748, `gain_recovery_max` 0.5687 -> 0.8017, `scale_bias_nogain_mean` +0.0201 -> +0.0186, and the stated cost `gain_spurious_max` 0.0293 -> 0.0571 kW.
  - `cop_duty_floor.py` `defrost_inferred_selfset_2.2_2C_ignored` factor 0.684 count 96 -> factor 1.000 count 0. The null `defrost_inferred_matched_2C_ignored` reads factor 1.000 at both ends, and its count moves 96 -> 0 (the ask-ignored verdict now refuses the matched arm's samples too, at an unchanged factor).
  - Not re-run here: `counter_spans.py` (its counts move with the wall clock, `counter_spans.py:128`), `m5_sysid.py`, `m2_sysid_plant.py`, `cop_dither_fabric.py`, `comments.py`. They are cited from the body and not verified by this seat.
- Claims (step 4): the diff touches no golden fixture and no claim file. `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only 608c95decc` printed `claims hygiene: 608c95decc94a8240565aba68fa8f0e1dece8c3d ok` (`ev/env_drift_claims_only.log`). This seat did not run `--all`; that is CI's lane.
- Versions (step 5): `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are not in the three-dot diff.
- Ratchet (step 14): `python3 tests/structure.py` at the head prints `ok max_class_loc 7814 <= 7814` and `STRUCTURE RATCHET PASSED` (`ev/structure.log`). The budget file moves one value down, `max_class_loc` 7868 -> 7814, and raises nothing. The mechanism is the freeze reasons moving out of `HeatPumpOptimizerCoordinator._learning_frozen` into `learning_freeze.py` (about 70 lines out of the class in the diff).
- Step 16 (an actuator refusal): the diff adds no refusal of a pump write. `SystemIdentification.arm(..., enabled=)` refuses on the entry's switch as `SysIdConfig.enabled` did.
- Mutants O and P under the whole `tests/features.py`: `exit=0` at both, with no `FAIL` check line (`ev/features_full_mutO.log`, `ev/features_full_mutP.log`). Mutant L: `exit=1`.
- CI: `merge_train.py classify fab2d371ede00e9168843c18f6c47dc2425046f9 --pr 3835` read rc=3 WAIT on every run from 16:49 to its last run (`WAIT ... pending: gate red: none`, `ev/classify.log`). This seat stopped polling because the verdict is blocked on code, so no green is owed to it. The digest at render read `gate` failure and `tests / mutation` failure. `tests / mutation` is in the `owed-reds` set, and the body answers it under `## Red checks` (unpinned sites, `ci_predict.py`). This verdict is blocked on code, not on CI.
