R10-PARAMS-OWNER: one owner of the thermal parameters, copy-on-write, published whole; one fabric interval; user-command and per-cycle writers wait for their store's startup read.

Closes #2232. Part of #2248, #2249, #2258 and #2674.

- **D7-s1-82 (#2232).** `_publish_params` is the one writer of the coordinator's `ThermalParameters`: every write builds a new snapshot with `dataclasses.replace` (which re-runs the divisor floor) and publishes it whole, through the `_hub` facade, which rebinds the context. A `set_thermal_parameters` call is one clamped snapshot published before any await. The DHW learner and the legionella guard read through a reader, and the DHW learner proposes changes through the publisher. The unread live optimizer is gone.
- **D7-s4-8x-fabric (#2249, class N-order-coupling).** The house and lower-floor learners replay one `FabricInterval`, closed once per cycle by `_close_fabric_interval`, so the learner that runs first can no longer silence the one after it.
- **ls-r1 and #2674.** `async_update_thermal_params` awaits the thermal-learning store's read before it resets the fabric scale and the buffer cooling rate, and the DHW learner's read before an explicit DHW cooling rate. `async_restore_learned_snapshot` awaits every restored store's read. The price-shape fold (#2674 lead 4) and the legionella observer each await their store's read. The six other #2674 leads are closed by the gates the harness names (dispositions under `## Figures`).
- **L4 hygiene.** The context is never edited in place: the one place that publishes parameters rebinds the whole `CoordinatorContext` (R10-LIVESTATE's carry: the instance is write-once, and the `_ctx` binding stays rebindable).
- **R10-SCORES' forward carry (mass basis and band), decided by this group as the owner of the parameters.** `envelope_score`'s time constant now reads `ThermalParameters.envelope_thermal_mass`, which covers every store the house's loss drains (the zones, or the room, plus the emitter slab), so the grade is for the house the model simulates. The 20-100 h literals are replaced by the band the shipped presets derive (`presets.envelope_band_hours`), on a log scale.
- **A repair to this branch, not new scope.** The mass-basis change had dropped the grade's massless guard, and this restores it on the new basis: `envelope_thermal_mass <= 0` reads `no_house_model`, as `room_thermal_mass <= 0` did at the base. Ten existing checks in `tests/features.py` still encoded the old 20-100 h band, or read a snapshot bound before a write (copy-on-write rightly leaves that snapshot whole). They are re-stated on `presets.envelope_band_hours()` and on the snapshot as published now. The N-log-flood registry in `tests/entities.py` is re-keyed from `async_update_thermal_params` to `_thermal_param_changes`, which now holds the window-spec warning and is reached only from that service call.

## Head

`198d396f552f2d52f1b1ccb03145e882b77322ec`, merged with origin/main `da12aa37dee15b9e9567bd6c848493436f2592dd` (also the merge base; #2712 included) at 2026-10-25. Since the earlier handoff at 4fbe4c6a5: the PR's row commit 935a7a6b1, then main merged in (c4817603b). That merge has a semantic resolution with #2712's `_async_learn_interval`. It keeps main's one learner sequence: the baseline time is read first, then the lower and house learners, the COP save and the slab seed. Inside it, both fabric learners replay the one interval `_close_fabric_interval` closes (#2249), and the former `_async_learn_fabric` is folded into it and removed. The budgets were re-recorded at this base (198d396f5). Before that merge: the race probe's `_restore` command in `tests/features.py` was renamed `_race_restore_snapshot`, because it is a different function from `entry_config._restore`; `tests/closure.py no-copies` prints clean at this head.

## Mutation proof

Runner: each mutant deletes or reverts one line of the fix in a fresh `git archive` copy of the head, then runs `PYTHONPATH=tests/hastub python3 tests/features.py`. The baseline row is the unmutated head.

Two runners, both on a `git archive` of the head. The first is `$SCRATCH/mutants.py`, which runs the fix's checks, taken verbatim from `tests/features.py`, against each mutant; it was re-run at 198d396f5. The second runs the whole of `tests/features.py`, for the two mutants the first set does not reach; it was run at bd8b11b1d. The code those two mutants touch is unchanged since. At 198d396f5, `displace_snapshot_stale` also fails the D7-s1-82 check in the first runner, and `no_mass_guard` reads 0 there, because the massless check is not in that set.

Fix checks (baseline: 0 failing):
- `publish_in_place` (edit the snapshot in place instead of `replace` plus rebind): FAIL "a parameter call publishes one clamped snapshot before any await and leaves the snapshot it replaced whole (D7-s1-82)"
- `no_thermal_read_wait`: FAIL "set_thermal_parameters resets the learned heat loss survives the store read in flight at startup", FAIL "... resets the buffer cooling rate survives ..."
- `no_dhw_read_wait`: FAIL "set_thermal_parameters' explicit DHW cooling rate survives the store read in flight at startup"
- `no_restore_read_wait`: FAIL "restore_snapshot's restored DHW profile survives the store read in flight at startup"
- `no_price_read_wait`: FAIL "the price shape's folded day (#2674 lead 4) survives the store read in flight at startup"
- `no_legionella_read_wait`: FAIL "an observed disinfection cycle (#2674's legionella observer) survives the store read in flight at startup"
- `lower_reads_baseline` (the split learner reads its own baseline again): FAIL "the fabric interval is closed once, so the house learner run first does not silence the split learner"
- `grade_room_mass` (the time constant on `room_thermal_mass`): FAIL "the house grade's band is the presets' own ..." (`240 presets, 24 clipped`), FAIL "the house grade reads the mass the dynamics store ..."
- `grade_linear_band`: FAIL "doubling the house's time constant moves its grade by the same points wherever it starts"

Whole `tests/features.py` (the baseline reads 1 failing, "the path that proceeds still stamps a resolvable recorded_at (#363)". That check fails in any `git archive` copy, as `fixer.md` step 2 notes, and it appears in every row below):
- `no_mass_guard` (drop `or params.envelope_thermal_mass <= 0.0`): +1, FAIL "#2258: a converged learner on a massless house, or one at the loss floor, has no house model -- not a grade of 0" (`massless {'envelope': 0.0 ...}`)
- `displace_snapshot_stale` (drop the publisher's context rebind): +29, among them "the displace limit is mirrored where the publisher clamps against it", "a mapped parameter is applied" and "the live model reads the snapshot the call published"

`PYTHONPATH=tests/hastub python3 tests/features.py` at the merged head (c4817603b, same code as 198d396f5): rc 0, no FAIL.

## Null control

- Interleave harness `--null` (every field requested at the value it already holds): base `mixed_snapshots=0 unclamped_hub=0`, head `0 0`. With fields that change, base reads 3/3 and head 0/0, so the probe can see a torn snapshot.
- Fabric harness: the learner order `lower_house` gives 12/12 samples at both ends. Only the order `house_lower` moves (0 to 12).
- Store-load leads harness: every lead's `null` arm (the writer runs after the read lands) is 0 at base and at head.
- Envelope harness, split arm: `split_max_abs_gap=0.0` on all 10 cells. The house-health grade and the envelope grade agree at the head.
- `python3 tools/audit/archscore/score.py --diff HEAD` (the head against itself): `Architecture score: dS +0.0000 NULL`. The instrument reads no change where there is none.

## Figures

Harnesses run from the base export (`git archive de794b537`, sha1s below) against the base tree and against the code head before main's merge (`git archive` of c8a234897; the fix's code is unchanged since, apart from the massless guard, whose own check and mutant are under `## Mutation proof`). They were not re-taken after main's merges, except the fabric harness: at the merged head it reads all four order arms at 12, `house_lower_lower_samples_after_12=12`, because #2712's `_async_learn_interval` is the call site it drives. Each command runs from the root of the tree it measures:

- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/catchup/arch-a/v2_params_interleave.py` (sha1 ac5419f3a2f088d4f130fc13296c625f07ba3106): `mixed_snapshots` 3 -> 0, `unclamped_hub` 3 -> 0, `unclamped_solve` 0 -> 0 (`yielded=1` at both ends; the arm measured a suspension).
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/catchup/arch-b/v2_s4_fabric.py --root <tree>` (sha1 0bcd55bf73ced3cb8aab6faeb44bee4eea8e2f3c): `house_lower_lower_samples_after_12` 0 -> 12. The other three order arms are 12 at both ends.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D14/sweep-N-shared-config/shared_config_seams.py --root <tree>` (sha1 9f042421741c0a4dd2caa14a34add93a077bccba), the rule that enumerates the N-shared-config class: `family_B` (hub in-place writes reachable from a solve root) 16 -> 1, `seams_total` 44 -> 29, and families A, C and D unchanged (3, 3, 22). The one family-B seam left, `coordinator.py _opt_config.comfort_weight`, is `_opt_config`, not `_thermal_params`. It is already guarded, per the class sweep (`## Forward-carry`). Families A, C and D are other owners' seams, also outside this group.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_store_load_leads.py` (in tree, sha1 9b69a689bda785ea14769dc8d42858a493cacbde; #2674's probe): `price_shape_lost` 1 -> 0 and `extra_legionella_observer_lost` 1 -> 0, with `null=0` at both ends. Six leads are `closed_by` their first-refresh gate, with `fresh_call_writes=0` at both ends: buffer_cooling, dhw_dynamics, legionella_cycle, energy_totals, ledger and accuracy. Their forced `gate_open` arms read `lost=1` at both ends. That is the counterfactual which shows each lead is closed by exactly that gate and not by a dead probe. Disposition: already guarded.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py` (sha1 f45215cf2dcd23b5a0fec897c73aaf24f3424133). Band arm, 40 preset rows (4 fabrics x 5 eras x one- and two-zone): the 8 timber rows before 1980 grade 0.0 on the base rule (`grade`, room mass on the 20-100 h band), and 21.8-54.8 on the head rule (`tree_grade`). The clip count is not this harness's figure. It is the check "the house grade's band is the presets' own" in `tests/features.py`, which drives all 240 presets and fails with `240 presets, 24 clipped` under the `grade_room_mass` mutant.
- The same harness with `--bundle <owner's diagnostics bundle>`, run locally with the bundle (R10-SCORES' blocked carry; the bundle is not committed): `scale=1.953 ratio=1.807 samples=475 two_zone=True`. The stored scale is 1.95x, not the suspected 2.6x. At the base: `tau_effective_h=7.3 grade=0.0`. At the head: `tree_grade=6.5`.
- `python3 tools/audit/archscore/score.py --diff da12aa37d` (the merge base): `Architecture score: dS +16.8185 IMPROVES` (`hub_solve_writes` 16 -> 1, `coord_footprint` 2446 -> 2423; `reflective_writes` 15 -> 11 and `computed_attr_access` 32 -> 28, gate only). It was measured after R10-ARCHSCORE-COVERAGE extended the census, so the pre-extension figure is not credited (carry 1).
- `python3 tests/structure.py`: `seam_cut_total` measures 419 on origin/main da12aa37d (a `git archive` of it) and 424 at the head. Against main, the rows recorded with it also move: `max_class_loc` 8311 -> 8248, `class_excess_loc` 18102 -> 18093, `methods_over_150` 17 -> 16, `functions_cc_over_15` 30 -> 29. STRUCTURE RATCHET PASSED at the head.
- The scoped gate: `python3 tests/closure.py select --diff da12aa37d --workdir D` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. Each script `scope.run` names was run locally with `PYTHONPATH=tests/hastub`: `tests/features.py` rc 0 (re-run after this round's repairs). `tests/structure.py`: STRUCTURE RATCHET PASSED after the record. These exited 0: arch_score_head, backtest, block_duty, boost_drift_replay, config_flow_steps, debug_collect, deployment_shape, doc_claims, edge, env_drift, finite_boundary, guard_pins, and the rest of `scope.run` but the four named under Red checks. `tests/stress.py` and `tests/golden.py` were left to CI.

## Architecture score

Architecture score: dS +16.8185
- hub_solve_writes 16 -> 1: the solve roots no longer write the hub in place, because every parameter write is `_publish_params`' copy-on-write.
- coord_footprint 2446 -> 2423: the removal of the unread live optimizer and the DHW setter.
- reflective_writes 15 -> 11, computed_attr_access 32 -> 28 (gate only): the `setattr` loops over parameter fields became one `replace`.

## Raise justification

`seam_cut_total` 419 -> 424 (+5) over origin/main da12aa37d. It was ruled under mandate 6329234399 (scope `all`) by main for the measured value only, and re-derived at this merge base right before the push: `python3 tests/structure.py` measures 419 on main and 424 at the head. Main moved 420 -> 419 with #2712. Cross-seam edges this diff adds against main, from `tests/structure.py`'s `seam_metrics` dumped at both ends (no edge removed):

- `dhw -> coordinator._publish_params` and `learning -> coordinator._publish_params`. These are the two publisher adoptions: the DHW learner and the fabric learners now publish through the one owner instead of editing the snapshot in place.
- `_thermal_learning_store` read from `core` (`async_update_thermal_params` awaits its read) and `_price_model_store` read from `learning` (the price-shape fold awaits its read). These are the two awaited reads, ls-r1 and #2674 lead 4.
- The fifth is the lost fabric credit, not a new edge. Against the old base, this diff's fabric collapse (core calling two learners became one call) paid back one cut. #2712 made the same collapse on main (`_async_learn_interval`), so that credit is main's now. Per seam against main: learning 124 -> 127, dhw 31 -> 32, grid 103 -> 104.

Payments tried: seam placement (measured), in-place publishing, dropping the awaited reads, and payment elsewhere in the coordinator class.
1. **Seam placement of the two new helpers**, measured over all 12 placements of `coordinator._publish_params` (core, learning, dhw, grid, views, fetch) x `_close_fabric_interval` (learning, core): totals 424, 426, 429, 431, 429, 431, 432, 434, 431, 433, 431, 433. The chosen placement (core, learning) is the minimum, 424.
2. **Publishing in place, with no publisher**: this is the D7-s1-82 defect itself. The mutant `publish_in_place` shows the check failing.
3. **Dropping the awaited reads**: this deletes the ls-r1 / #2674 fix (the mutants `no_thermal_read_wait` and `no_price_read_wait` fail). A helper owned by the reading seam would still read the other seam's store, so it is the same edge under another name.
4. **Paying elsewhere in the coordinator class**: the architect note confines this group to the `_thermal_params` and context seam, and a hunk outside it is a new conflict surface. `max_class_loc` (-63), `class_excess_loc` (-9), `methods_over_150` (-1) and `functions_cc_over_15` (-1) already move down in this diff, and are recorded with the raise.

Architecture score: dS +16.8185 IMPROVES (`python3 tools/audit/archscore/score.py --diff da12aa37d`, at the same merge base).

The `--allow-regression` reason names the four cuts and is in the commit messages of bd8b11b1d, 4fbe4c6a5 and 198d396f5 (the last names the lost fabric credit and main's 420 -> 419). **A budget-file head merges serially** (`tests/structure_budgets.json` is in this diff).

## Unpinned sites

Keyed at the head 198d396f5 (merged with da12aa37d) by `tools/pr/ci_predict.py --base origin/main`, the predictor prepr runs. Each is a `custom_components/` site. The massless-guard and band-clamp lines are also killed by the proof's `no_mass_guard` and `grade_linear_band` mutants.

- custom_components/heatpump_optimizer/coordinator.py:2269 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:2827 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:2879 CMP_BOUND*2: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:2879 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:2887 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:2887 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:3234 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:5446 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:5449 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:5451 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:5493 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:5652 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6295 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6303 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6305 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6317 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6329 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6331 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/coordinator.py:6498 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/dhw_learning.py:158 CLAMP_DROP: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/presets.py:301 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/thermal_model.py:565 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/thermal_model.py:567 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/thermal_model.py:579 GUARD_OFF: pinned by mutation-autofix (a custom_components/ site)
- custom_components/heatpump_optimizer/thermal_model.py:583 RETURN_DEL: pinned by mutation-autofix (a custom_components/ site)

## Red checks

- prepr `no-copies` (COPY-CLAIMED, at the open's merge of 052e5c5d2): the test helper `_restore` collided by name with `entry_config._restore`. They are different functions, and the helper is renamed. The cheaper detector already exists: `tests/closure.py no-copies`, which takes seconds and which `prepr.sh` step 6c runs. Running it before the handoff would have caught this. This head prints it clean.
- **budget-raise-gate / budget-raise-gate**: red by design until the mandate approval lands at the final head. This diff raises `tests/structure_budgets.json`'s `seam_cut_total` from 419 to 424. Under mandate 6329234399 (scope `all`), main approves it. The answer is `## Raise justification` above. No cheaper detector exists: this gate is the owner-approval check itself, and nothing earlier can stand in for an approval.
- **tests / mutation**: "MUTATION TABLE REFUSED -- 3975 unpinned site(s) against 3960 at the ratchet base bc52ad2af..., at head 4fbe4c6a5, 26 of them added by this diff" (check-run 121208504832). These are the 25 keys under `## Unpinned sites`; `coordinator.py`'s massless guard holds two CMP_BOUND mutants, which makes 26, and CI's log names the same set. All are `custom_components/` sites. The `tests / mutation-pins` jobs (mutation-autofix) are repairing it by pinning every site a driver kills, per `ci-autofix.md`, and the head waits for that bot commit rather than duplicating it. Any survivor comes back to this seat for `tests/mutation_ledger/survivor_triage/`. The cheaper detector already exists and fired: `prepr.sh` step 6d's unpinned-site list, from `tools/pr/ci_predict.py`. `body_push.sh` runs it on every handoff, so it adds no standing cost; it took a few minutes here at load average ~200. It listed the same 25 sites before the PR opened. The pin itself is CI's by design, because the pinning mutants run on Linux.
- `tests / closures` UNDER-SCOPED (predicted): `presets.py` is newly imported by `coordinator.py`. It was repaired in the diff by re-recording each affected script with `tests/derive_closures.sh --single`, the last being `tests/boost_drift_replay.py`. `tools/pr/ci_predict.py --base origin/main` at the head now predicts no closures red. This is named per `ci-autofix.md`.
- `ledger` STALE PIN x10 (predicted at the earlier head): the ten pins on lines this diff edits were deleted by hand, and `mutation-autofix` re-pins the edited lines.
- Local, at the code head 052e5c5d2 before main's merge, and not this diff's:
  - `tests/optimality.py` reads 1 FAIL ("one|summer_negative|shoulder: a recorded claim still has a gap ... the claim closed and should be removed"), and the same one FAIL on the base export de794b537. It is main's, or this machine's, not this branch's.
  - `tests/entities.py` reads 4 FAIL, all the heartbeat-control checks from `tests/nightly_ha.py`'s py-spy control (for example "two tries took 0.83s against a 1.0s rest"). They are timing checks run at load average ~200. No file in this diff is in their path. CI decides them.
  - `tests/card.mjs` aborted with a JavaScript heap out-of-memory error under the same load, and is left to CI.
- `tests/stress.py` and `tests/golden.py` were not run locally. They are CI's (heavy-runs-on-cloud).

## Forward-carry

- Carry 1 (re-measure D7-s1-82's dS after R10-ARCHSCORE-COVERAGE): re-measured at da12aa37d, under `## Figures`. Carry: dismissed: discharged in this diff
- Carry 2 (two owners of the ECL110 displace limits; a runtime seal on published snapshots): these stay leads as this group's roster entry records them, not owed. Carry: dismissed: recorded leads, not owed
- Carry 3 (mutation-ledger re-key, quiet-window stress re-take): the ledger re-key is the ten stale pins named above plus `mutation-autofix`. The stress re-take is CI's required mutation check. Carry: dismissed: discharged in this diff and by CI
- R10-SERVICES-GUARD's precondition: `services.py` is untouched, and `handle_set_thermal_params` still resolves `_loaded_coordinators(hass)` before any return. The census "every action resolves its config entries before it returns" passes in `tests/features.py` at the head. Carry: dismissed: precondition holds at the head
- R10-SCORES' mass-basis, band and bundle carries: decided and measured here (`## Figures`). Carry: dismissed: discharged in this diff
- The family-B seam left by the N-shared-config enumeration, `_opt_config.comfort_weight` (`_apply_comfort_weight`): already guarded, per `dev/audit/rounds/round10/sweep-N-shared-config.md`. It is one synchronous write with no await before its reader, it is declared in `CYCLE_HUB_WRITERS`, and the solve reads deep copies. Carry: dismissed: already guarded per the class sweep

## Friction

none
