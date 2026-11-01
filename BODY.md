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

**Learners.** Every learned store, enumerated as `_restored_stores` (the set the snapshot restore already writes), is voided: with the entry **unloaded** first, so no save in flight writes the old state back: the two heat-loss learners through the one void path #3022 built (`async_reset_heat_loss_learners`, after the undo point), then `voided_documents` drops each store's `_FACTORY_VOID` keys or removes the store: `thermal_learning` (buffer cooling, COP scale, COP baseline and health, open-window detector, immersion events, capacity envelope, solar aperture, internal gains, heat curve, frequency map, flow bias), `dhw_profile` and `dhw_draws` (DHW cooling, profile, draws), `price_model`, `accuracy` (accuracy history, DHW accuracy, defrost, comfort weight). Each then loads absent: its initial state. Kept, as facts: the heat-loss anchors, the meter's last COP, snow memory, the frequency watchdog's stand-down latch, the billed peaks, the operating mode.

**Undo.** Before anything changes, the reset flushes every learner to its store and takes a snapshot whose `before_reset` holds every learned store's document, the settings it drops, and, per (data, options), the three topology keys the reset pins (`entry_config.FACTORY_PINNED`: `two_zone_mode`, `dhw_enabled`, `wood_furnace_enabled`) as they were stored. `restore_learned_snapshot` (`SnapshotRing.undo_target`: the undo point while it is the newest snapshot, else `best_restore`) unloads, writes the documents back, restores the dropped settings and the pinned keys as stored over the wiring in force, and sets the entry up again: every learner, the accuracy history and the settings come back exactly, an auto-mode house auto again. The drift rollback never takes it (`best_restore` skips it); spent, it stays as an ordinary snapshot.

**Refused unload.** Where Home Assistant refuses to unload the entry, nothing is written but the undo point: the heat-loss void runs only after a successful unload. `async_factory_reset` returns False and logs "not applied"; the options step aborts `factory_reset_not_applied` and the service raises `HomeAssistantError` (`factory_reset_not_applied`, placeholder `entry_id`). An undo over a refused unload keeps its undo point and returns False.

## Head

`3f9f152e2ac87cee1a1ab3ac0018d64bd023f13d`. It merges the PR head `2df0b81ed2fb9726a4b8d52de072fdb64520ded1` (github-actions[bot]'s `ci: pin killed mutants` on `7f6d7e72`, 13 `tests/mutation_ledger/killed_by/` records and nothing else) into `895f03158b222d8a8bd11cf697c3f3baeb01674e`, which merges origin/main `ca6333333afc1ec7937b9792880458d190f4d4d2` into the PR head `7f6d7e72260ca64e98ec13c3b7c46c5e01af62a6` (the orchestrator's merge of origin/main `d052f80f7f81d42db5c57a55ebaef7056c7ce01a` over `116233658`, which merged this round's handoff `fcbf8ec952187bac1adfc46691f1ad43cffa6984` into the previous PR head `78c0e8d0864d880f36cc5f5f09c2c53ae802ea73`). Main's delta `d052f80f..ca633333` touches no production file and not `tests/features.py`; among scripts it touches `tests/entities.py` and `tests/env_drift.py`, both re-run at `895f0315` below; the bot's records are the only delta from there to this head. `tools/pr/prepr.sh` with this body at this head: `PRE-PR: 3f9f152e2ac87cee1a1ab3ac0018d64bd023f13d ... rc=0`. origin/main then moved once more, to `407eb0cb38f3cd43e71f4ed7be1c23f80dc32cc1` (#3049, 2026-11-01 18:21 UTC, during that run): `git merge-tree --write-tree origin/main HEAD` exits 0, and its delta (`tests/closures.json`, `.github/workflows/governance.yml`, `tools/audit/seat/` gh-call instruments, a delivery row) shares no file with this diff, so it is not merged (fixer.md step 6: merge only on a conflict); the figures below are against `ca633333`.

`fcbf8ec9` is this round's one authored commit. It changes tests and the mutation ledger only, no production line: `tests/features.py` (two checks and their controls), `tests/entities.py` (the service stub), and two `survivor_triage` records; it answers the fix review's round-2 block at `d1662cf7b100fe99cc9938c2a536dbced55823f3` (verdict/3047, mutation-vacuous) item by item. The `tests/features.py` figures and the full mutant proof were taken at `9aae13850a26fc1007f0492449d6bd062cae9717`, my own merge of `d052f80f` into `fcbf8ec9`, whose tree `f0a037f0bcbbfca11c26a7e79788654f1cb1bf12` is byte-identical to the orchestrator's `7f6d7e72` (`git rev-parse 7f6d7e722^{tree} 9aae13850^{tree}` prints the same hash twice), and production and `tests/features.py` are unchanged from there to this head (`git diff --name-only 7f6d7e722 895f0315` lists neither). Earlier heads of this PR: `a6592a23e83030aa473d6ea5d688ac3c6b3b249a` (round 2's authored code head), `96211117d1341cb71925086fc44182f68b67139d` (round 1's), cut from `0cae227c329f24d859c10db94b9dbd8a6368d11c`; `21ed69e8cf74764ff6a6d91cd6f01103ad3c54c7` carries the raise.

## Mutation proof

Round 3, every finding of the review at `d1662cf7`, by the reviewer's own mutants (its `evidence/list4.py` and `list5.py` on verdict/3047, applied verbatim by its `run2.py` and `full.py` with only the worktree paths changed), each restored after. Measured at `9aae1385` (tree-identical to `7f6d7e72`; this head changes neither production nor `tests/features.py` from it), and first at `fcbf8ec9`, before the merge, with the same verdict for every mutant: `ALL 4707` there. Unmutated at `9aae1385`: the extracted R10-FACTORY-RESET section reads `ALL 31 FR CHECKS PASSED`; the whole of `PYTHONPATH=tests/hastub python3 tests/features.py` reads `ALL 4713 FEATURE CHECKS PASSED`, rc 0.

Through the whole of `tests/features.py`, each mutant by itself:

- U6-no-flush-before-documents (`await _async_save_restored(coord)` deleted from `coordinator._async_store_documents`): KILLED, `1 of 4713 FEATURE CHECKS FAILED` -- "the undo restores what the learners knew at the reset, learning since the last save included: COP scale 1.21" `[restored True, COP scale 1.13]`. The test was what was missing, not the code: with the flush present the undo restores 1.21.
- U7-undo-ignores-age (`"before_reset" in self.snapshots[-1]` -> `any("before_reset" in s for s in self.snapshots)` in `SnapshotRing.undo_target`): KILLED, `1 of 4713` -- "after an unhealthy snapshot newer than the undo point, the restore takes neither: nothing qualifies, the reset stays" (the mutant hands the restore the unhealthy newest snapshot).
- C2-humidity-low-bound: KILLED, `1 of 4713` -- "the range's two ends are humidities: 0 % and 100 % are read, just past either is refused" `[0 -> None, ...]`.
- C3-humidity-high-bound: KILLED, `1 of 4713` -- the same check `[..., 100 -> None]`.
- C4-dhw-probe-guard-off: KILLED, `3 of 4713` -- among them "a tank probe pinned at its last good value still reads back, and the record refuses it anyway".
- C5-dhw-probe-frozen-dropped: KILLED, `3 of 4713` -- the same three.
- L9955-GUARD_OFF (the probe's guard `if False:`): KILLED -- "a configured, healthy tank probe fills the hot-water accuracy record" `[counts {}]` and three more.
- L360-RETURN_DEL (`_side_pair`'s trailing `return None` -> `pass`): SURVIVED, `ALL 4713` -- equivalent (the function falls off its end and returns None); triaged `equivalent` at `tests/mutation_ledger/survivor_triage/entry_config.py/_side_pair.RETURN_DEL.da9e8e97.json`.
- L9957-RETURN_DEL (`_dhw_probe_temperature`'s trailing `return None` -> `pass`): SURVIVED, `ALL 4713` -- equivalent the same way; triaged at `tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.RETURN_DEL.d7923b87.json`.

Through the extracted section (31 checks; the reviewer's 28 plus this round's three), all 39 other mutants of the reviewer's lists: KILLED -- T1-T6 and T3b, T5b (the undo record's guards), C1, P1-P4, R1-R7, L0, S0, U1-U5, N1, N2, S1, S2, S4, SV1, SV2, L358, L369, L373. The seven the section cannot reach are C2-C5, L9955 (killed in the whole file, above) and the two equivalents.

Failing first: the new U6 and U7 checks pass at `78c0e8d0`'s production code (they pin code that is right and was unpinned) and each fails under its mutant, above. The `tests/entities.py` repair, failing first: at `fcbf8ec9` with the stub's `return True` removed, `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 1 with `HomeAssistantError: The factory reset of test_entry was not applied: Home Assistant refused to unload the entry; nothing was changed` -- the crash CI's `tests / fast (3.14)` printed at `d1662cf7`.

The earlier rounds' proofs (round 1 at `21ed69e8`, M1-M11; round 2 at `c2f9fe90`, `831691af`, `a6592a23`: the 21 `_FACTORY_VOID` entries each killed, the pins, the refused-unload arms, the typing repair) are re-run above by the reviewer's lists where they name them; the void-entry list was re-taken by the review at `d1662cf7` (21 killed, 0 survived) and no production line has moved since.

## Null control

- U6's control: "learning since the last save is in memory only before the reset: COP scale 1.21 held, 1.13 stored (the control)" -- without it, a case whose memory equals its store would pass with or without the flush (every earlier case learns through `_fr_learn`, which saves each store). Unmutated, the undo restores 1.21.
- U7's control: the healthy newer snapshot is "a weekly snapshot newer than the undo point takes the restore back from it", which both the code and U7 pass; the new check plants the newer snapshot unhealthy (`healthy=False`), where `best_restore` hands out nothing (`undo_target() is None is best_restore()`), the restore returns False and the reset's heat-loss state `(1.0, 1.0, 0, 0)` stays.
- `tests/entities.py`'s stub: returning None, the script dies (above); returning True, "factory_reset hands that entry's coordinator its scope and reports both" reads `ok`. The refused arm (`factory_reset_not_applied`) is driven over real stores in `tests/features.py`.
- The options step submitted unticked returns the advanced menu with the entry's data, options and every store document byte-identical and no unload or set-up (`tests/features.py`, and `tests/config_flow_steps.py`'s untouched-submit sweep).
- The per-key void check's control: "before a learners reset every learned store is on disk and holds learned keys beyond its facts" -- at least 25 learned keys.
- The exact-undo check's control: "the house is auto-mode before the reset and pinned two-zone by it".
- The refused-unload checks compare every store document (stamp removed) and the heat-loss pair `(1.4, 1.3, 60, 40)` before and after.

## Figures

`tests/features.py` at `9aae13850a26fc1007f0492449d6bd062cae9717` (tree-identical to `7f6d7e72`; production and `tests/features.py` unchanged since); the rest at `895f03158b222d8a8bd11cf697c3f3baeb01674e`, merge base `ca6333333afc1ec7937b9792880458d190f4d4d2` = origin/main (2026-11-01 17:33 UTC), with `tools/pr/ci_predict.py` re-run at `3f9f152e2ac87cee1a1ab3ac0018d64bd023f13d`.

- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4713 FEATURE CHECKS PASSED`, rc 0 (4707 at `fcbf8ec9`; main's merge adds 6).
- The R10-FACTORY-RESET section of `tests/features.py`, extracted with the module header and `_li_state_of` as the reviewer's `fr_section_head.py` is: `ALL 31 FR CHECKS PASSED`. Mutant results: `## Mutation proof`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2516 ENTITY CHECKS PASSED`, rc 0, the whole script on Linux (2499 at `9aae1385`; main's delta adds 17. With the stub returning None, at `fcbf8ec9`: rc 1, the `factory_reset_not_applied` crash).
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all ca6333333afc1ec7937b9792880458d190f4d4d2`: `CLAIMED config_flow: 4 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56 committed fixture(s)`, rc 0. This round touches neither claim file: `card_claimed_drift.txt` is byte-identical to origin/main, and `claimed_drift.txt` differs from it only by this PR's existing extension of the one `config_flow` line (round 1's; without it env_drift reads the four leaves unclaimed). VERSION, the manifest and RELEASE_NOTES.md are untouched.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, `seam_cut_total 423 <= 423`; this round adds no production line.
- Scoped gate: `python3 tests/closure.py select --diff ca6333333afc1ec7937b9792880458d190f4d4d2` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out`. This round's delta reaches `tests/features.py`, `tests/entities.py` and the ledger: run here, features, entities, structure, env_drift; the rest, unchanged by this round, as the review measured at `d1662cf7`, and to CI.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, governance or instrument red predicted against ca6333333afc`, and no unpinned site: the bot's pins at `2df0b81e` cover the 13 this diff added, and the two triaged equivalents are no longer sites.
- `python3 tools/audit/archscore/score.py --diff ca6333333afc1ec7937b9792880458d190f4d4d2`: `Architecture score: dS +0.0030 IMPROVES`, `coord_footprint 2387 -> 2382`.
- Kept keys and their reasons: `PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.entry_config import FACTORY_KEPT; [print(k, '--', v) for k, v in FACTORY_KEPT.items()]"`.

## Raise justification

`seam_cut_total` 422 -> 423, approved by orchestrator s9 under mandate 6329234399 (scope all, budget-raise covered); the reason is in the commit message of `21ed69e8`. The crossing: the undo point must wait for the snapshot store's read, so the learning seam reads the core-owned `_snapshot_store`.

Payments tried: six, one line each below; none improves the code.

- `async_factory_reset` in the `core` seam: +2 (core calls the learning void path; core reads the grid-owned `_price_model_store`), worse.
- Dropping the snapshot-store wait: +0, unsound -- the undo point can be written over a ring not yet loaded, replacing eight weeks of snapshots.
- Refusing the reset while `_snapshots_loaded` is false: +0, but a user-facing refusal and new strings for a window no user reaches, worse than waiting.
- Adding the snapshot store to `_restored_stores`: the same (learning, `_snapshot_store`) pair, +1.
- Handing the unload to a learning helper as a callback: moves the metric by making the code worse, declined.
- Re-labelling `_apply_house_heat_loss_scale`, `_apply_lower_floor_loss_ratio` and `_apply_buffer_cooling_rate` from core to learning in `tests/seam_map.json`: -1, a map edit made to pass the budget -- gaming, declined (and declined by the orchestrator).

Architecture score: dS +0.0030 IMPROVES

(`python3 tools/audit/archscore/score.py --diff 92588d581fde4ce287af3db5e8bb61461dc28015` at this head, `coord_footprint 2389 -> 2384` (the same against `8fec54ee`); earlier takes read dS +0.0036 against `8fec54ee` at `96211117`, +0.0048 against `0cae227c`.) The fix review at `96211117` judged the six payments and found no missed one.

## Judgement calls for tvofi

- The main fuse (`main_fuse_amperes`, `main_fuse_phases`) and the solar-forecast source are kept although the brief names neither: a default fuse arms the fuse guard against a fuse the house does not have, and a default forecast source leaves an assigned radiation sensor unread.
- Tank volumes, the heat pump's power limits and the compressor frequency range are thermal-model numbers and are reset.

## Carries

Each carry on this group's roster entry (`handoff/audit-r10-roster` at `8df6d71f586842bd240e7b596b9282849a05578b`; the third first landed at `134667ca39c16862296d75a1906b8863d1b6b856`):

- Carry 1 (from R10-HOTFIX-LEARNER-INPUTS): the learners scope voids the heat-loss pair through `async_reset_heat_loss_learners()` with `const.HEAT_LOSS_LEARNERS` (its default), after the undo point is taken and saved and the entry is unloaded -- `coordinator.async_factory_reset`. The re-plan is the entry's set-up again (its first cycle solves in the background), not a refresh the reset awaits.
- Carry 2 (the same void path, from this group's brief): as Carry 1; no entity action is added (the options step and the service only), so `tests/features.py`'s RC2 rows gain none.
- Carry 3 (udf-reset-homes): the **`factory_reset`** paragraph under `docs/configuration.md` ## Services, the README ## Services row and `### Reset to factory defaults` are in this diff.

## Red checks

At the current PR head `2df0b81ed2fb9726a4b8d52de072fdb64520ded1` (62 check runs, one page, read 2026-11-01 18:02 UTC): the only concluded red is `budget-raise-gate / budget-raise-gate` (jobs 124929323233, 124929251151), answered below. `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / typing` (one run), the two nightly-ha lanes, `tests / coverage`, `tests / replay`, `tests / arch-instrument`, `governance / instrument-self-tests` and `codeql / Analyze (python)` were still in progress; every other completed run concluded success, skipped or neutral. This head `3f9f152e` adds only a merge of that PR head, and has run no CI yet.

Every check that concluded red at the PR head `78c0e8d0864d880f36cc5f5f09c2c53ae802ea73` (75 check runs, one page; `tests / mutation-pins (2)`, `(4)`, `tests / arch-instrument`, `governance / instrument-self-tests` and `codeql / Analyze (python)` still in progress when read), by its full name. `3f9f152e` has run no CI yet.

- `tests / fast (3.14)` (job 124890480873; 124865808454 at `d1662cf7`): `tests/entities.py` died on this diff's own stub. `_svc_fr_record` returned None, and `services.handle_factory_reset` (round 2) raises `factory_reset_not_applied` on a falsy reset. Fixed at `fcbf8ec9`: the stub returns True (null control under `## Mutation proof`). The cheaper detector existed and was not run: `PYTHONPATH=tests/hastub python3 tests/entities.py`, about 25 s on CI's Linux and minutes in this container; round 2 ran only its barrier slice because the script stops early on that seat's host (`PermissionError: Cannot get task port`). Its standing cost is that run per handoff, which `fixer.md` step 5 already requires (`scope.run` names `tests/entities.py`); no new detector is owed. This root-cause trigger goes to `root-cause.md`'s seat, not this diff.
- `tests / mutation` (jobs 124890297006, 124890236630): `MUTATION TABLE REFUSED`, the unpinned sites this diff added over the ratchet base. At `2df0b81e` mutation-autofix pinned the 13 added sites the suite kills (the review's L358, L369, L373 and L9955 among them, each killed by hand under `## Mutation proof`); the two equivalent survivors are triaged at `fcbf8ec9`; `tools/pr/ci_predict.py` at this head lists no unpinned site. No cheaper detector is owed beyond the one in use: `ci_predict.py` names the sites before the push, seconds.
- `budget-raise-gate / budget-raise-gate` (jobs 124890296973, 124890236743): `REFUSED: no decisive review by tvofi`, over `seam_cut_total: 422 -> 423`. Red by construction until an approving review at the head under mandate 6329234399 (scope all) against `## Raise justification`. No cheaper detector exists: the gate is the approval itself.

At `d1662cf7` also: `tests / mutation-autofix` (124889991154), which failed on six "lives" sites measured on shards made inconclusive by the `tests / fast (3.14)` baseline above; and `gate`, the aggregate of the reds above. Earlier rounds: `tests / typing` at `822633c7` (fixed at `a6592a23`, green since); `governance / instrument-self-tests` (main's own uutils `sleep` red, fixed on main by #3086); at `e2b12a17`, `tests / nightly-ha (2025.2.0)`, `tests / nightly-ha (stable)`, `tests / fast (3.14)`, `tests / mutation-autofix`, `pr-contract / pr-contract`, all answered and green at `96211117`.

## Forward-carry

- udf-reset-homes (design/R10-USER-DOCS-FINAL `be9f30ec9`), on this group's roster carry at `134667ca39c16862296d75a1906b8863d1b6b856`: discharged in this diff by the **`factory_reset`** paragraph under `docs/configuration.md` ## Services, the README ## Services row and the `### Reset to factory defaults` section. Carry: R10-FACTORY-RESET
- `_async_load_thermal_learning` saves the thermal store after the re-anchor and before the COP scale and the T4b learners are loaded, so a crash between leaves the store without them. Carry: R10-LEARNED-STORE-LOAD
- `async_restore_learned_snapshot` reads the snapshot ring without waiting for the snapshot store's read, and restores learner values without their sample counts. Carry: R10-LEARNED-STORE-LOAD

## Unpinned sites

none: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `3f9f152e` lists no `ADDED UNPINNED` site; the 13 this diff added are pinned by mutation-autofix's `2df0b81e`, and the review's two equivalent survivors are triaged under `tests/mutation_ledger/survivor_triage/`.

## Friction

none
