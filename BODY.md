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

`a6592a23e83030aa473d6ea5d688ac3c6b3b249a`. It adds one commit to `fa2d2d91075e001cb6257eb5acb80ecfa244d723`, whose PR head after the opener's update, `822633c7`, was red on `tests / typing` (below): `entry_config._side_pair` narrows each half of the undo record for mypy, and a new check pins the malformed-record arms. `fa2d2d91` was round 2's repair, after the fix review blocked at `96211117d1341cb71925086fc44182f68b67139d` (mutation-vacuous). It fast-forwards the PR head `7837bb0524634acf569414c6f6785930b3eb72bf` (the bot's `ci: pin killed mutants` on `96211117`, which merged `origin/main` `8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f` into `0ee5cd675515a36a9095d0d42fd49a7588816aab`) by this round's commits: `92b1e9e373eb8f90de75ccc113b8e5704d77046b` (the production repairs and their tests), `43d5d2e44be606ec66609a7bfaf60c43bb2177f7` (the void list pinned against a fact list the test owns), `210bb1fdf77b360e909128f3c80b03fa0833f2fe` (the pinned-key round trip), `c2f9fe903cd000b414d00b14cae16b1b71534f0c`'s parent (one warning for both outcomes, the void rule a pure function), `c2f9fe903cd000b414d00b14cae16b1b71534f0c` (structure re-record, rows lower only), `75d7d329b709d708a583f2d6d7572488501c9c19` (the refused-unload check reads the log line), `3e9f90cba70b380e7a2497dfb4fee5cf674bb59a` (docs), `831691af36ec427f7759ac4d667dff9c0ee3012c` (the new exception key registered), `11ca4fa7479f3de46e289527b244d6d5008c7a42` (seven stale pins dropped), and `fa2d2d91075e001cb6257eb5acb80ecfa244d723`, which merges `origin/main` at `92588d581fde4ce287af3db5e8bb61461dc28015`: `tools/pr/ci_predict.py` read the head as unmergeable there, because main's R10-USER-DOCS-FINAL regenerated `dev/audit/rounds/round4/D6/claims.{py,json,md}`; the resolution takes main's three files, re-applies this branch's two `claims.py` changes (`factory_reset` in `SCHEMAS`, without which C20 and C21 read false; the Default-row count note 92 -> 93) and regenerates the register. Main's delta `8fec54ee..92588d58` touches no production file, test of this group, golden fixture or claim file; it touches docs, `tests/doc_claims.py` and `tests/entities.py`, each re-run below. The feature was cut from `0cae227c329f24d859c10db94b9dbd8a6368d11c`, which contains #3022; `21ed69e8cf74764ff6a6d91cd6f01103ad3c54c7` carries the raise.

## Mutation proof

Round 2, every finding of the review at `96211117`, each by a mutant applied at `c2f9fe90` (the last commit to move a production line; the three void entries below at `831691af`) and run through the R10-FACTORY-RESET section of `tests/features.py` (the section extracted verbatim with the module header the reviewer's `ev/fr_section_extract.py` carries; 27 checks), restored after. Unmutated: `ALL 27 FR CHECKS PASSED`. All mutants below are KILLED unless marked:

- The void list, entry by entry (the review's 13 survivors among them): deleting each of the 21 entries of `coordinator._FACTORY_VOID` -- thermal `buffer_cooling_rate`, `buffer_cooling_samples`, `_COP_STORE_KEY`, `cop_samples`, `vent_cusum`, `cop_baseline`, `cop_health_cusum`, `immersion_events`, `capacity_envelope`, `solar_aperture`, `internal_gains_profile`, `curve_learner`, `freq_map`, `flow_bias`; accuracy `accuracy`, `dhw_accuracy`, `defrost`, `comfort`; stores `dhw_profile`, `dhw_draws`, `price_model` (`None` -> `()`) -- 21 of 21 killed, each by "a learners reset drops every learned key, key by key, and keeps every fact, before the entry is set up again" (18 run at `c2f9fe90`, the three my runner's parse of the tuple missed -- `cop_samples`, `immersion_events`, `internal_gains_profile` -- at `831691af`; no production line moved between). My first per-entry check enumerated `_FACTORY_VOID` itself and pinned nothing: 11 of these deletions survived it (disclosed self-correction); the check now reads each store's keys against a fact list the test owns.
- `entry_config.undone_settings` malformed-record guard off (the review's `entry_config.py:350`): killed (`TypeError` in "restore_learned_snapshot undoes a learners reset: every learner back, the settings untouched").
- The restore's early return dropped (the review's `coordinator.py:9524`): killed ("the undo asks the coordinator it unloaded for nothing more: no refresh, no learner applied after it").
- Pins not restored (`wiring = (data, options)`), not recorded (`pinned = [{}, {}]`), restored from the wrong side: each killed ("restore_learned_snapshot undoes the reset ... exactly as before it"; "an undo puts each pinned key back where and as it was stored").
- At `a6592a23e83030aa473d6ea5d688ac3c6b3b249a` (the typing repair): the undo-record guard off, its `or` -> `and`, `_side_pair`'s guard off, its length test off, its dict test off, and its return dropped: 6 of 6 killed ("an undo record missing either half, or holding a malformed one, undoes no settings", and the undo checks).
- A refused unload ignored; the reset reporting done on refusal; the log line saying "applied" on refusal; the options step saying done; the service raising nothing; the undo never spending its point: each killed.
- Full `PYTHONPATH=tests/hastub python3 tests/features.py` at `831691af` (unmutated rc 0): the humidity read's bounds (the review's `coordinator.py:9722 CMP_BOUND` x2) `0.0 <= value` -> `0.0 < value` and `value <= 100.0` -> `value < 100.0`: each killed by "the range's two ends are humidities: 0 % and 100 % are read, just past either is refused" (`0 -> None`, `100 -> None`). The DHW probe's single guard off (`if True: return value`): killed by 3, among them "a tank probe pinned at its last good value still reads back, and the record refuses it anyway" (`probe answers 55.0`). The review's `coordinator.py:9947 GUARD_OFF` on the old two-guard form was equivalent -- `_learning_frozen` is pure, so a None value read None with or without it -- so the guard is folded into one condition rather than triaged.

Failing first: the round's new section run against `7837bb05`'s production code: `4 of 26 FR CHECKS FAILED` -- "restore_learned_snapshot undoes the reset ... exactly as before it" (`config moved ['dhw_enabled', 'two_zone_mode', 'wood_furnace_enabled']`), "a refused unload changes nothing but the undo point" (`done None ... heat loss (1.0, 1.0, 0, 0), stores moved ['thermal_learning']`), "a refused unload refuses the undo too" (`undo True`), "a refused unload is said as not applied" (`{'type': 'abort', 'reason': 'factory_reset_done'}, raised None`). The per-key void and learners-undo checks pass there: they pin code that was right and unpinned.

The earlier rounds' proofs, as measured then (M1-M11 at `21ed69e8`; check names as they stood):

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
- The per-key void check's control: "before a learners reset every learned store is on disk and holds learned keys beyond its facts" -- every store present, each with learned keys, at least 25; without it an empty store would read as voided.
- The exact-undo check's control: "the house is auto-mode before the reset and pinned two-zone by it" -- `two_zone_mode` absent before, `on` after the reset, so "exactly as before" is not trivially the reset's state.
- The refused-unload checks compare every store document (stamp removed) and the heat-loss pair `(1.4, 1.3, 60, 40)` before and after; the confirmed options step ("confirmed, the options step resets, sets the entry up again and closes") is the arm where the same entry is changed.
- R1's sweep: "every options page's shown schema accepts the a5 walk's untouched resubmit, every form page read" counts the pages read against the form pages shown (floor 20); its null control is a planted page whose schema has a required field, run through the same reader `_a5_refusals` and refused.
- A settings reset writes no learned store: each document is as it was at the moment the entry is set up again.

## Figures

At `11ca4fa7` (merge base `8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f`) unless marked; re-taken at `fa2d2d91075e001cb6257eb5acb80ecfa244d723` (merge base `92588d581fde4ce287af3db5e8bb61461dc28015`) where marked [head].

- [head] R10-FACTORY-RESET section, extracted: `ALL 28 FR CHECKS PASSED` at `a6592a23e83030aa473d6ea5d688ac3c6b3b249a`; mutant table above.
- `tests/typing_ruler.py --mypy` under its pins (mypy 2.3.1, homeassistant-stubs 2026.9.3, Python 3.14) at `a6592a23e83030aa473d6ea5d688ac3c6b3b249a`: `ALL 9 typing-ruler checks PASSED`; at `fa2d2d91` the same run read `2 of 10 typing-ruler checks FAILED` (`by_code[index] did not grow [recorded 0, measured 2 (+2)]`, `entry_config.py:365` and `:366`: `Value of type "Any | None" is not indexable`). No `type: ignore` added; the ruler is not re-recorded.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at `a6592a23`: `ALL 4704 FEATURE CHECKS PASSED` (4703 at `831691af`).
- `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` at `3e9f90cb`: `ALL 537 checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f`: `CLAIMED config_flow: 4 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56 committed fixture(s)`.
- `GOLDEN_MODE=strict PYTHONPATH=tests/hastub python3 tests/golden.py --only config_flow` at `3e9f90cb`: `ALL 1 GOLDEN SCENARIOS UNCHANGED` (the new abort reason is not in the fingerprint).
- [head] `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 296 checks PASSED`; `node tests/md_tables.mjs`: `doc_misrendered_lines=0`; `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `claims_true=123`, `claims_false=0`, `claims_unverifiable=2`, `config_defaults_compared=93`, `config_ranges_compared=101`.
- [head] N-log-flood barrier, the slice `_R10_LATCH_WORD` .. `_r10_log_found` of `tests/entities.py` executed verbatim: verdict `{}`, 68 unlatched sites over 84 modules; `async_factory_reset` holds one warning, worded by the outcome. `tests/entities.py` stops on this host at `_hb_stdlib_reads` (`PermissionError: Cannot get task port`), before the barrier; CI's Linux `fast` runs it whole.
- [head] `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; re-recorded in `c2f9fe90` with rows lower only: `class_excess_loc` 17649 -> 17648, `max_class_loc` 7986 -> 7983; `seam_cut_total` 423 (unchanged). A first version without the callbacks (unload explicit in each caller) read `seam_cut_total 428 > 423`; the callback version is kept and its helpers' prose cut to pay `class_excess_loc` (+14 at `92b1e9e3` -> -1).
- `python3 tools/audit/archscore/score.py --diff 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f`: `Architecture score: dS +0.0030 IMPROVES`, `coord_footprint 2389 -> 2384`; [head] `--diff 92588d581fde4ce287af3db5e8bb61461dc28015`: the same.
- Scoped gate: `tests/closure.py select --diff 8fec54ee2` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out`. Run here: features, config_flow_steps, env_drift, golden (config_flow), doc_claims, md_tables, structure; entities by the slice above; the rest to CI.
- [head] `tools/pr/ci_predict.py --base 92588d581fde4ce287af3db5e8bb61461dc28015` at `a6592a23`: `CI PREDICT: no closures, fast, governance or instrument red predicted`, `19 unpinned site(s)`, each listed in the last section. `tools/pr/prepr.sh` at this head, no closures skip: `PRE-PR: a6592a23e83030aa473d6ea5d688ac3c6b3b249a ... rc=0`, its `ci predict` step green, `unpinned sites` disposing of all 19.
- Kept keys and their reasons: `PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.entry_config import FACTORY_KEPT; [print(k, '--', v) for k, v in FACTORY_KEPT.items()]"`.
- Every store the integration persists, each dispositioned: `tests/features.py`'s "every store the integration persists has a factory-reset disposition" (the AST walk `tests/finite_boundary.py` arm 1 uses).

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

Every check that concluded red at the PR heads `822633c7`, `7837bb0524634acf569414c6f6785930b3eb72bf` and `96211117d1341cb71925086fc44182f68b67139d`, by its full name:

- `budget-raise-gate / budget-raise-gate`: `REFUSED: no decisive review by tvofi`, over `seam_cut_total: 422 -> 423`. Red by construction until an approving review at the head under mandate 6329234399 (scope all) against `## Raise justification`, whose shape `python3 tools/policy/budget_raise_gate.py --check-body` accepts. No cheaper detector exists: the gate is the approval itself.
- `tests / typing` (job 124826653199, at `822633c7`): `errors did not grow [recorded 0, measured 2 (+2)]`, `by_code[index] did not grow [+2]` -- two `[index]` errors this diff added in `entry_config.undone_settings`, where `all(...)` over `(settings, pinned)` narrowed neither from `Any | None`. Fixed at `a6592a23e83030aa473d6ea5d688ac3c6b3b249a` by `_side_pair`, which returns a stored (data, options) pair or None, so each half is narrowed where it is read; guard kept; the ruler reads 0 again. The cheaper detector existed and I did not run it: `tests/typing_ruler.py --mypy` in its pinned venv (`--print-requirements`), seconds here; `prepr.sh` does not run it, which is why its rc 0 at `fa2d2d91` did not see this.
- `tests / mutation`: at `7837bb05`, `MUTATION TABLE REFUSED -- 3564 unpinned site(s) against 3572 at the ratchet base 61b0076f4, 5 of them added by this diff` -- the five live sites the review named (`entry_config.py:350 GUARD_OFF`, `coordinator.py:9524 RETURN_DEL`, `coordinator.py:9722 CMP_BOUND` x2, `coordinator.py:9947 GUARD_OFF`). Each is killed or removed at this head (`## Mutation proof`): 350 and 9524 killed by new checks; the two bounds killed by "the range's two ends are humidities"; 9947 was an equivalent mutant (`_learning_frozen` is pure, so a None value read None either way), and the probe is now one guard whose GUARD_OFF returns the value while frozen -- killed. This round adds new lines (`## Unpinned sites`); mutation-autofix pins what the shards kill. The cheaper detector is the section mutant runner used here (seconds per mutant against the shards' hour); it is a scratch instrument, not landed.
- `gate`: `FAIL tests / mutation: failure` beside the raise gate, the aggregate; it follows those two.

At `e2b12a17` (round 1, all answered there and green at `96211117`): `tests / nightly-ha (2025.2.0)`, `tests / nightly-ha (stable)`, `tests / fast (3.14)`, `tests / mutation-autofix`, `pr-contract / pr-contract`.

## Forward-carry

- udf-reset-homes (design/R10-USER-DOCS-FINAL `be9f30ec9`), on this group's roster carry at `134667ca39c16862296d75a1906b8863d1b6b856`: discharged in this diff by the **`factory_reset`** paragraph under `docs/configuration.md` ## Services, the README ## Services row and the `### Reset to factory defaults` section. Carry: R10-FACTORY-RESET
- `_async_load_thermal_learning` saves the thermal store after the re-anchor and before the COP scale and the T4b learners are loaded, so a crash between leaves the store without them. Carry: R10-LEARNED-STORE-LOAD
- `async_restore_learned_snapshot` reads the snapshot ring without waiting for the snapshot store's read, and restores learner values without their sample counts. Carry: R10-LEARNED-STORE-LOAD

## Unpinned sites

Each is a production line this diff adds, at this head (`python3 tools/pr/ci_predict.py --base 92588d581fde4ce287af3db5e8bb61461dc28015 --only mutation` at `a6592a23`); mutation-autofix (its lane mutates `custom_components/`) pins each one the suite kills after the push. The hand-run mutants above kill this round's guards and returns among them.

- `custom_components/heatpump_optimizer/config_flow.py:3315 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1420 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1425 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1441 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1444 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1453 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1464 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:1466 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9730 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9955 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9955 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9957 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:350 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:353 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:358 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:360 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:369 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/entry_config.py:373 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/services.py:1193 GUARD_OFF`: mutation-autofix

## Friction

none
