R10-FACTORY-RESET (owner request, tvofi 2026-10-30): "There should also be an option to reset all parameters to factory integration defaults if there currently is none". There was none: `restore_learned_snapshot` restores a snapshot or a refit, and the comfort-weight and heat-loss buttons reset one learner each. This adds a reset with three scopes the user picks -- `settings`, `learners`, `both` -- as an options-flow page behind an explicit confirmation (Advanced settings -> Reset to factory defaults) and as a `factory_reset` service taking a required `entry_id` and `scope`. An undo point is taken first, and `restore_learned_snapshot` undoes the reset while that point is the newest snapshot; the confirmation text says so. The entry is then set up again, and its first cycle re-plans.

Where each part lives (fixer.md step 17): the settings rule in `entry_config.py` (the module that owns the entry's settings, Home Assistant-free): `FACTORY_KEPT`, `factory_settings`, `undo_point`, `undone_settings`. The learned stores in `coordinator.py`, which owns them: `_FACTORY_VOID` over `_restored_stores`, `async_factory_reset`, `_async_rewrite_entry`, `_async_undo_factory_reset`. The undo point in `snapshots.py` (`SnapshotRing.take(before_reset=)`, `undo_target`). The options step and the service only orchestrate (`config_flow.HeatPumpOptimizerOptionsFlow.async_step_factory_reset`, `services.handle_factory_reset`). No Home Assistant import is added below the glue.

**Settings.** Every stored key outside `FACTORY_KEPT` is dropped from both `entry.data` and `entry.options`, so it reads as the default the parse of an absent key gives: one home for the defaults, never a second table. Kept, each with its reason (printed by the first command under `## Figures`):

- every entity assignment: each `CONF_` key ending `_entity`, plus `compressor_freq_sensor` (46 keys, listed by that command) -- resetting one disconnects a sensor or actuator;
- `name` -- the entry's name, not a setting;
- `price_source`, `tibber_token` -- the price source and its credential;
- `solar_forecast_source` -- the solar feed, the price source's sibling: its default would leave an assigned radiation sensor unread;
- `two_zone_mode`, `dhw_enabled`, `wood_furnace_enabled` -- zone, tank and furnace topology, **written** as the settings in force derive them: an auto-mode house is two-zone by its zone masses, which the reset drops, so the mode is pinned `on`/`off` first;
- `upper_floor_emitter`, `lower_floor_emitter` -- emitter topology;
- `dhw_wood_coil_enabled` -- tank plumbing;
- `mixing_valve_mode`, `mixing_valve_write_target_kind` -- valve topology and what its write entity is;
- `space_setpoint_unit` -- what the setpoint entity's number means;
- `topology_layout`, `topology_positions` -- the plant layout and its diagram;
- `ecl110_command_topic`, `ecl110_displace_set_topic`, `ecl110_state_topic`, `ecl110_mqtt_qos`, `ecl110_mqtt_retain` -- the controller's MQTT wiring;
- `modbus_prefill_prefix` -- the heat pump device the entities came from;
- `main_fuse_amperes`, `main_fuse_phases` -- the house's main fuse: a default arms the fuse guard against a fuse the house does not have.

**Learners.** Every learned store, enumerated as `_restored_stores` (the set the snapshot restore already writes), is voided: the two heat-loss learners through the one void path #3022 built (`async_reset_heat_loss_learners`, while the entry runs, after the undo point); then, with the entry **unloaded** so no save in flight writes the old state back, `_FACTORY_VOID` drops each store's learned keys or removes the store: `thermal_learning` (buffer cooling, COP scale, COP baseline and health, open-window detector, immersion events, capacity envelope, solar aperture, internal gains, heat curve, frequency map, flow bias), `dhw_profile` and `dhw_draws` (DHW cooling, profile, draws), `price_model`, `accuracy` (accuracy history, DHW accuracy, defrost, comfort weight). Each then loads absent: its initial state. Kept, as facts: the heat-loss anchors, the meter's last COP, snow memory, the frequency watchdog's stand-down latch, the billed peaks, the operating mode.

**Undo.** Before anything changes, the reset flushes every learner to its store and takes a snapshot whose `before_reset` holds every learned store's document and the settings it drops. `restore_learned_snapshot` (`SnapshotRing.undo_target`: the undo point while it is the newest snapshot, else `best_restore`) unloads, writes the documents back, restores the dropped settings over the wiring in force, and sets the entry up again: every learner, the accuracy history and the settings come back exactly. The drift rollback never takes it (`best_restore` skips it); spent, it stays as an ordinary snapshot.

## Head

`0ee5cd675515a36a9095d0d42fd49a7588816aab`, which merges `origin/main` at `2b6bef7453a8bdaf97d42f382a116ce226b35ccc` into `6c690058e4037c6bc9fceb202b7103bc7f002d12`: `tools/pr/ci_predict.py` read the head as unmergeable into main without the ledger driver (both sides re-recorded `tests/structure_budgets.json`; the driver resolves `class_excess_loc` 17649 and `max_class_loc` 7986, `seam_cut_total` stays at this branch's 423). `6c690058` merged `origin/main` at `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0` into `1bf20b3f15d5d70361b3ee9e27dd4356a7c1340a`: `git merge-tree --write-tree origin/main 1bf20b3f` refused `tests/golden/claimed_drift.txt` (MERGE-CLAIM), because main's r10-wood-notify now claims `config_flow` too; the resolution keeps main's list and extends its one `config_flow` line with this branch's reason. `1bf20b3f` and its two parents are this repair round, on the previous code head `9039d17886543a1fe441d2afd89e6fb12d37eedc`: `2e1421f14179147e1e00f1b7affb2d8677db77ea` (the nightly a5 walk posts `{}` to the factory-reset page, and the stub lane checks every page's schema against that payload), `572c912c9f810914c554b9827a407b1077b57879` (the `config_flow` fixture claimed), `1bf20b3f` (the reset's one warning on the N-log-flood barrier). The three touch `tests/` only; this round authors no production line. `9039d178`'s parent `21ed69e8cf74764ff6a6d91cd6f01103ad3c54c7` carries the raise; `915acea21fa907751c52be09a4fe297070204011` merged `origin/main` at `12caba8cfe67b61b50852926564b79228e7304a0`. The feature was cut from `0cae227c329f24d859c10db94b9dbd8a6368d11c`, which contains #3022.

## Mutation proof

Each mutant applied to `21ed69e8` (the head adds only two ledger deletions and a claims-header edit, no code), run through the R10-FACTORY-RESET section of `tests/features.py` (the section only, extracted verbatim with its module helpers), restored after:

- M1 learners dispatch, `coordinator.async_factory_reset` `if scope != FACTORY_RESET_SCOPES[0]:` -> `if True:` -- red: "a settings reset writes no learned store: each is as it was when the entry is set up again".
- M2 settings dispatch, `if scope != FACTORY_RESET_SCOPES[1]:` -> `if True:` -- red: "a learners reset keeps the settings and the stores' facts: the watchdog latch, peaks, mode".
- M3 kept-keys filter, `entry_config.with_settings` keeps every key -- red: "after a settings reset every tunable option reads its default", "a reset of both leaves the wiring alone and every learner at its initial state", "the service needs an entry and a known scope, and resets that entry".
- M4 the entity rule, `and key.endswith("_entity")` -> `and False` -- red: "the kept keys are the listed wiring and every entity assignment, each an option key".
- M5 the drift rollback's skip of the undo point removed -- red: "the drift rollback never takes the reset's undo point; the restore does, while it is newest".
- M6 `undo_target` never returns the undo point -- red: that check, "restore_learned_snapshot undoes the reset: every learner, the accuracy history and the settings as before it", "the spent undo point stays as an ordinary snapshot, so a second restore is the ordinary one".
- M7 the restore's undo branch off -- red: the last two.
- M8 the confirmation ignored -- red: "the options step shows the scope and the confirmation; unconfirmed, nothing changes (null control)".
- M9 the topology pin removed -- red: "after a settings reset every kept key is unchanged, and the topology it implied with it", the undo check.
- M10 the voided documents emptied -- red: "after a learners reset every learner reads what one that never learned reads", the reset-of-both check.
- M11 a refused unload ignored -- red: "a refused unload stops the reset at its undo point: settings kept, nothing set up".

Unmutated, the section reads `ALL 19 fr PASSED`, and the whole of `tests/features.py` reads `ALL 4676 FEATURE CHECKS PASSED` (at `404117b9`, the feature commit this head merges main onto).

Failing test first: the same section at the merge base fails at its import (`ImportError: cannot import name '_FACTORY_VOID' from 'heatpump_optimizer.coordinator'`).

This round's repairs, each failing first:

- R1 (`tests / nightly-ha`): the new check "every options page's shown schema accepts the a5 walk's untouched resubmit" in `tests/config_flow_steps.py`, run against the unfixed `tests/nightly_ha.py` (`2e1421f1` with `option_resubmit` as at `9039d178`): `1 of 537 checks FAILED`, `refused ["factory_reset: extra keys not allowed @ data['after_save']"]` -- the same `InvalidData` real Home Assistant raised on both nightly lanes. Fixed: `ALL 537 checks PASSED`.
- R2 (`tests / fast (3.14)`, `tests / mutation`): `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3` at `2e1421f1` (claim file as main's): `1 UNCLAIMED DRIFT(S)`, `DRIFT config_flow: 4 leaves moved` (`_menu.advanced: length 15 vs 16`, `_seed.confirm`, `_seeded.factory_reset`, `factory_reset`: present on one side only). With the claim (`572c912c`): `CLAIMED config_flow: 4 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, rc 0. Re-taken at this head against main `2b6bef7453a8bdaf97d42f382a116ce226b35ccc` (whose own `config_flow` line names the wood key): the same four leaves `CLAIMED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 2b6bef7453a8bdaf97d42f382a116ce226b35ccc`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- R3 (`tests / fast (3.14)`): the R10 N-log-flood barrier of `tests/entities.py`, its enumerator and verdict executed verbatim from the file (the slice `_R10_LATCH_WORD` .. `_r10_log_found`) over the package at this head: verdict `{}`, 68 unlatched sites read over 84 modules; with the new entry removed, `{('coordinator.py', 'async_factory_reset'): (1, 0)}` -- the exact mismatch CI printed.

## Null control

- The options step submitted unticked returns the advanced menu with the entry's data, options and every store document byte-identical and no unload or set-up (`tests/features.py`, and `tests/config_flow_steps.py`'s untouched-submit sweep).
- "after a learners reset every learner reads what one that never learned reads" compares against a coordinator that never learned, over the configuration the reset left; its own control is "the learned state before the reset is not the initial one, learner by learner".
- A settings reset writes no learned store: each document is as it was at the moment the entry is set up again (the reload's own answer to the options change -- a learner re-anchored or voided by a changed nameplate -- is any options edit's, and not the reset's).
- R1's schema check carries its own: "null control: the factory-reset page's schema refuses an after-save key" (`ok`), so the sweep's reader can refuse; and every other page reads `ok` under the same payload rule, before and after (only `factory_reset` was refused).
- R3's control is the entry removed (above): the barrier then refuses exactly this function at count 1.
- R2's control is the claim removed (above): `env_drift.py` then refuses exactly `config_flow`; the five `coord_*` lines inherited from main read byte-identical in both runs.

## Figures

- Kept keys and their reasons: `PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.entry_config import FACTORY_KEPT; [print(k, '--', v) for k, v in FACTORY_KEPT.items()]"`; the test asserts `set(FACTORY_KEPT)` equals the list above plus every `_entity` option key, all of them option keys (every key a `CONF_` constant names, tuples included, and `name`).
- Every store the integration persists, each dispositioned: the AST walk over every `QuarantiningStore(...)` construction in `tests/features.py`'s "every store the integration persists has a factory-reset disposition" (the rule `tests/finite_boundary.py` arm 1 uses). Voided: `thermal_learning` (learned keys), `accuracy` (learned keys), `price_model`, `dhw_profile`, `dhw_draws`. Kept: `snapshots` (the undo point lives there), `ledger` (billed energy), `energy` (metered totals), `manual_plan`, `away`, `boost` (the user's own overrides), `dhw_legionella` (the last disinfection, a safety fact), `notifier` (which notices were sent), `pump_duty` (what was last written to the pump), `debug` (a diagnostics collection).
- `tests/golden/config_flow.json` re-recorded (float-free: the new page, its two fields): `PYTHONPATH=tests/hastub python3 tests/golden.py --record --only config_flow`.
- `dev/audit/rounds/round4/D6/claims.{json,md}` regenerated: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` (C109 and C111 unverifiable, as at the merge base).
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` at this head against main `2b6bef7453a8bdaf97d42f382a116ce226b35ccc` (2026-10-31): `Architecture score: dS +0.0036 IMPROVES`, `coord_footprint 2389 -> 2383`. At `9039d178` against main `7539d167` it read the same dS (`2390 -> 2384`).
- `python3 tests/structure.py` at this head: `STRUCTURE RATCHET PASSED` (`seam_cut_total 423 <= 423`, after the raise below; `class_excess_loc` and `max_class_loc` were re-recorded lower in `21ed69e8`).
- Scoped gate scope at this head: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out` (merge base `2b6bef74`). Run here at this head: `tests/config_flow_steps.py` (`ALL 537 checks PASSED`), `tests/env_drift.py --all 2b6bef74` (R2), `GOLDEN_MODE=strict tests/golden.py --only config_flow` (`ALL 1 GOLDEN SCENARIOS UNCHANGED`, the auto-merged fixture), `tests/features.py` (`ALL 4693 FEATURE CHECKS PASSED`, the factory-reset section with main's new `wood_lighting_lead_minutes` option in the table), `tests/structure.py`. `tests/entities.py` stops on this host at `_hb_stdlib_reads` (`PermissionError: Cannot get task port`, the macOS sampler), before the barrier, so R3 is measured by the extracted slice; CI's Linux `fast` runs the whole file. The rest of `scope.run` ran green on CI at `e2b12a17` (`tests / fast (3.14)`: `2 TEST SCRIPT(S) FAILED`, `env_drift.py` and `entities.py`, both answered here).
- `python3 tools/pr/ci_predict.py --base 2b6bef74` at this head: `CI PREDICT: no closures, fast, governance or instrument red predicted against 2b6bef7453a8`, and `36 unpinned site(s) the diff adds -- a warning`, each under `## Unpinned sites`. `tools/pr/prepr.sh` at this head, no closures skip: `PRE-PR: 0ee5cd675515a36a9095d0d42fd49a7588816aab ... rc=0`, its `ci predict` step `CI PREDICT: no closures, fast, governance or instrument red predicted`, `unpinned sites` disposed of all 36.
- Main's latest scheduled Nightly, run 41159630948 at `fbc731283` (2026-10-31T02:21Z): `nightly-ha (2025.2.0)` and `nightly-ha (stable)` both success, so neither nightly red is inherited.

Payments for the coordinator's span (`class_excess_loc`, `max_class_loc`): the thermal loader's four scalar blocks share `_stored_learner`; its two snow instants share `_stored_isoformat`; `_apply_learner_payloads`, the humidity read and the DHW probe adopt the shared coercion `finite_float`.

## Raise justification

`seam_cut_total` 422 -> 423, approved by orchestrator s9 under mandate 6329234399 (scope all, budget-raise covered); the reason is in the commit message of `21ed69e8`. The crossing: the undo point must wait for the snapshot store's read, so the learning seam reads the core-owned `_snapshot_store`.

Payments tried: six, one line each below; none improves the code.

- `async_factory_reset` in the `core` seam: +2 (core calls the learning void path; core reads the grid-owned `_price_model_store`), worse.
- Dropping the snapshot-store wait: +0, unsound -- the undo point can be written over a ring not yet loaded, replacing eight weeks of snapshots.
- Refusing the reset while `_snapshots_loaded` is false: +0, but a user-facing refusal and new strings for a window no user reaches, worse than waiting.
- Adding the snapshot store to `_restored_stores`: the same (learning, `_snapshot_store`) pair, +1.
- Handing the unload to a learning helper as a callback: moves the metric by making the code worse, declined.
- Re-labelling `_apply_house_heat_loss_scale`, `_apply_lower_floor_loss_ratio` and `_apply_buffer_cooling_rate` from core to learning in `tests/seam_map.json`: -1, a map edit made to pass the budget -- gaming, declined (and declined by the orchestrator).

Architecture score: dS +0.0036 IMPROVES

(`python3 tools/audit/archscore/score.py --diff origin/main` at `9039d178` against main `7539d1675d7fc8b5020f90b395f4bb0c3485d5b3`, `coord_footprint 2390 -> 2384`; the first take, against `0cae227c`, read dS +0.0048.)

## Judgement calls for tvofi

- The main fuse (`main_fuse_amperes`, `main_fuse_phases`) and the solar-forecast source are kept although the brief names neither: a default fuse arms the fuse guard against a fuse the house does not have, and a default forecast source leaves an assigned radiation sensor unread.
- Tank volumes, the heat pump's power limits and the compressor frequency range are thermal-model numbers and are reset.

## Carries

Each carry on this group's roster entry (`handoff/audit-r10-roster` at `8df6d71f586842bd240e7b596b9282849a05578b`; the third first landed at `134667ca39c16862296d75a1906b8863d1b6b856`):

- Carry 1 (from R10-HOTFIX-LEARNER-INPUTS): the learners scope voids the heat-loss pair through `async_reset_heat_loss_learners()` with `const.HEAT_LOSS_LEARNERS` (its default), after the undo point is taken and saved -- `coordinator.async_factory_reset`. The re-plan is the entry's set-up again (its first cycle solves in the background), not a refresh the reset awaits.
- Carry 2 (the same void path, from this group's brief): as Carry 1; no entity action is added (the options step and the service only), so `tests/features.py`'s RC2 rows gain none.
- Carry 3 (udf-reset-homes): the **`factory_reset`** paragraph under `docs/configuration.md` ## Services, the README ## Services row and `### Reset to factory defaults` are in this diff.

## Red checks

Every check that concluded red at `e2b12a17158195fdafd4188db0b8c33e26d3ff8c`, by its full name:

- `budget-raise-gate / budget-raise-gate`: `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`, over `RAISE tests/structure_budgets.json: seam_cut_total: 422 -> 423`. Red by construction until an approving review at the head, given under mandate 6329234399 (scope all) against `## Raise justification`, whose shape `python3 tools/policy/budget_raise_gate.py --check-body` accepts ("the body's `## Raise justification` names the payments tried and the arch_score figures", rc 0). No cheaper detector exists: the gate is the approval itself.
- `tests / nightly-ha (2025.2.0)` and `tests / nightly-ha (stable)`: `a5:pages_ok` -- `raised=['factory_reset:InvalidData']`, and `run:exit_status` with it. `tests/nightly_ha.option_resubmit` posted the after-save key to the factory-reset page, whose schema has no such field (R1). Not inherited: main's Nightly 41159630948 is green on both. The cheaper detector did not exist: the stub validates no flow schema, so no lane but the Docker one read a page's schema against the walk's payload. It exists now, in `tests/config_flow_steps.py` (38 s in the stub lane, one options flow per page), and it read this red before the fix.
- `tests / fast (3.14)`: `2 TEST SCRIPT(S) FAILED`. `tests/env_drift.py --all 7539d167`: `1 UNCLAIMED DRIFT(S)`, `config_flow` (R2) -- the fixture was re-recorded for the new page and never claimed. `tests/entities.py`: `1 of 2495 ENTITY CHECKS FAILED`, the R10 N-log-flood barrier, `mismatch {('coordinator.py', 'async_factory_reset'): (1, 0)}` (R3). Self-correction: the previous body said `tests/entities.py` "cannot finish on macOS ... environmental", which is true of this host and was read as nothing owed; CI's Linux run owed this one check. Cheaper detectors: `env_drift.py --all` runs locally (here 217-443 s under load) and would have read R2 before the push; for R3 the extracted slice above is seconds, and `prepr.sh`'s CI predict does not read either.
- `tests / mutation`: `MUTATION TABLE REFUSED -- 3610 unpinned site(s) against 3586 at the ratchet base 7539d167, 37 of them added by this diff` (the 36 lines listed in the last section, `coordinator.py:9722 CMP_BOUND*2` carrying two). No mutant was measured: every `tests / mutation-pins (1..8)` shard read `baseline tests/env_drift.py: rc=1 failed=1` and `MUTATION TABLE INCONCLUSIVE` (`measure: skip-measure-failed, 0 anchor(s)`), R2's red. With R2 fixed the baseline is green: a local `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` at `1bf20b3f` (drivers as CI's less `tests/entities.py`, which stops on this host) read `baseline tests/env_drift.py: rc=0 failed=0`, and `rc=0 failed=0` for `config_flow_steps.py`, `typing_ruler.py`, `features.py` and `finite_boundary.py`, with the `config_flow.py:236 NULL_COMMENT` null control surviving each; it was stopped after its baselines (this host's load read 50-198, and a site's verdict prints only at the run's end), so the shards measure. No survivor has been measured at any head yet; one the shards leave is a real gap and is owed a killing test.
- `tests / mutation-autofix`: `mutation-autofix: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`, the same cause; it pins after the shards measure.
- `pr-contract / pr-contract`: "check ... is red and `## Red checks` does not name it", for the six above; each is named here by its full name.
- `gate`: `FAIL tests / fast (3.14): failure`, the aggregate of the required checks; it follows `tests / fast (3.14)`.

## Forward-carry

- udf-reset-homes (design/R10-USER-DOCS-FINAL `be9f30ec9`), on this group's roster carry at `134667ca39c16862296d75a1906b8863d1b6b856`: discharged in this diff by the **`factory_reset`** paragraph under `docs/configuration.md` ## Services, the README ## Services row and the `### Reset to factory defaults` section. Carry: R10-FACTORY-RESET
- `_async_load_thermal_learning` saves the thermal store after the re-anchor and before the COP scale and the T4b learners are loaded, so a crash between leaves the store without them. Carry: R10-LEARNED-STORE-LOAD
- `async_restore_learned_snapshot` reads the snapshot ring without waiting for the snapshot store's read, and restores learner values without their sample counts. Carry: R10-LEARNED-STORE-LOAD


## Unpinned sites

Each is a production line this diff adds; mutation-autofix (its lane mutates `custom_components/`) pins each one the suite kills after the push. At `e2b12a17` none was measured (`## Red checks`, `tests / mutation`): the shards' baseline was red on R2, which this head repairs. The mutants run by hand above (M1-M11) kill the scope dispatch, kept-keys filter, entity rule, undo and unload guards among them. Line numbers are at this head (`tools/pr/ci_predict.py --base origin/main --only mutation`).

- `custom_components/heatpump_optimizer/config_flow.py:3306 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/config_flow.py:3308 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/config_flow.py:3310 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/config_flow.py:3315 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:412 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:423 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:430 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:432 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1402 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1411 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1414 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1416 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1438 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1444 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:4315 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:4317 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:4319 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:4328 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:4351 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9356 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9522 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9524 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9722 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9722 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9722 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9947 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:335 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:341 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:350 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:352 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:371 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/services.py:1194 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/snapshots.py:204 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/snapshots.py:242 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/snapshots.py:242 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/snapshots.py:244 RETURN_DEL`: mutation-autofix

## Friction

none
