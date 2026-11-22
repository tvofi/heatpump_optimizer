R11-OWNER-FAULT-TEXT: the pump's fault codes, with start and end, are recorded and shown in Download diagnostics. The heat-pump pre-fill now also suggests the fault-alarm entity (owner ruling 2026-11-22). Built from the approved design `design/R11-OWNER-FAULT-TEXT` 3850f3368e69.

Closes #3857

**What it does.**
- A new options-only slot, `heat_pump_fault_text_entities`, takes 1 to 4 `sensor`/`text`/`input_text` entities. It sits on Heat pump telemetry beside Fault alarm. The step refuses a fifth entity with `too_many_fault_text_entities`, because the multiple entity selector caps nothing.
- `fault_log.py` is the new owner of the record. It listens to that slot. With no text slot configured, it listens to the Fault alarm flag slot, read strictly as `InputReader.read_bool` reads it. A positive integral reading up to 32 bits is kept as its hex code.
- Each state change is stamped with its `last_changed`.
- The record holds:
  - a ring of the newest 200 closed rows `[start_s, end_s, code, late]`, plus the count of rows dropped;
  - the open row;
  - a per-code tally of at most 32 codes plus `other`.
- It is saved on every row opened or closed, at most once per 60 s. A save asked for inside that window is deferred to its end, never dropped.
- The stop event and `async_unload_entry` both run one idempotent `async_close`: unsubscribe, cancel the deferred save, then save.
- A setup that raises after `fault_log.async_setup` (the frontend registration or the platform forward) reaches no `async_unload_entry`; Home Assistant runs only the entry's `async_on_unload` callbacks. One of them, `_ended`, runs the same once-only `_release` (unsubscribe, cancel the deferred save) and starts the last save as a task, kept on the record as `ending`. The next `async_setup` for the entry awaits that task before it loads, so the last save lands before the load and no second record writes the store. On the unload path `async_close` has already released, so `_ended` does nothing.
  - Alternatives that lost: moving `fault_log.async_setup` after the last step of setup that can raise holds only while no later step is added, where the callback holds under any order; releasing without the last save drops a row closed inside the 60 s window; saving from the callback without the await lets that save land after the next setup's load (mutant M5 below reads the row closed late instead of watched).
- A restored open row continues if the first read after a restart gives the same code. Otherwise it closes at that read, marked `late`.
- The download shows the record under `coordinator.fault_log`. The section is null when no fault source is configured.
- Pre-fill:
  - the Tuya table gains `("binary_sensor", "fault")` and `("sensor", "fault_description")`;
  - `modbus_prefill._NAMED` gains `binary_sensor.{p}_alarm`;
  - `infer` suggests the text slot as a one-member list while it is empty.

**Departures from the design note, each forced by a check and measured.**
1. The design's one-key tuple of list slots in `modbus_prefill.infer` is an inline read of the one key instead. `config_flow_steps.py`'s absent-fallback census reads a tuple member as an unproven named read. With the key unproven it would have had to join `_ABSENT_IS_NOT_DEFAULT`. That made an untouched Heat pump telemetry save write `None` and reload the entry: the three `no untouched page reloads` checks went red at the intermediate head.
2. `device_prefill.py` joins `_NOOP_STATIC_SKIP` beside `config_flow.py`, `const.py` and `diagnostics.py`. It is handed registry records, never a configuration, and a key there is a table role. Null control: the census at the merge base, with and without this skip, prints the same `82 with a named read not proven; 199 proven safe` (Figures).
3. `fault_log` reads the two slots as `EntryConfig` fields (`heat_pump_fault_entity`, `heat_pump_fault_text_entities`, declared here), not off the merged mapping. `__init__` passes `EntryConfig.from_mapping(config)`. The reason: `entities.py`'s entry-config census refused an unclassified mapping reader.
4. The pre-fill and docs text naming the hold: FAULT-HOLD is not on main, so the pre-fill and docs text names only the learning freeze and the duty-switch void, as the design's own carry says. The hold is carried to FAULT-HOLD (Forward-carry).

**Golden.** The `config_flow` fixture is float-free and compared exactly, so it is re-recorded (`golden.py --record --only config_flow`) and claimed in `tests/golden/claimed_drift.txt` under `claims-for: 10.1.2`. Three leaves move, each "present on one side only": the plain render, the seeded render and the seed each gain the fault-text field. Every other fixture is unmoved: `env_drift.py --all 8ef450936a` printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`. An intermediate head moved 115 leaves of that fixture, because `_entity_of` passed `multiple=False` into every entity selector's config. The key is now set only for the list field.

**Structure payment (design's primary).** `_user_sensors_fields` is built from `_USER_SENSORS_GROUPS` instead of spelling its fourteen keys a second time.
- `module_excess_loc` 21779 -> 21771, re-recorded (commits 9d4298a47e and d287b46fff name the row).
- `_user_sensors_sections`' forgotten-field fallback is unreachable once both are one table, so it is removed. Its two `killed_by` pins (GUARD_OFF cc44e904, e7efd72e) name no site and are deleted.
- The test that drove the fallback by rebinding the table now pins the single-table property: rebound to one group, the sections and the flat fields both hold exactly its two pickers. The intact table's three sections hold all 14 flat fields, open.

Carry 0: (FAULT-HOLD's flag-prefill-reach, adding the hold's 10 minutes to the pre-fill rows on FAULT-TEXT's rebase) is conditional on FAULT-HOLD merging first, and it has not: `git grep -n -i 'FAULT_HOLD\|fault hold' 2f4e32c2a3b959142e29966e001292d42ff1affd -- custom_components` (origin/main at 2026-11-22T23:05Z) prints nothing. So this head's pre-fill rows name no hold, and the hold's text is carried the other way, to R11-OWNER-FAULT-HOLD (Forward-carry), whichever lands second.

## Head

`c18501831385cb135f9d893599c42504162e1c26`, merge base `e3cb5c019b464a770cc7c6fe2fbc858ed29debf7`. Round 2: the repair of the round-1 block at `9f133225f72bc9581a411bdc40d544dd447f78ee`, on top of it.
- At 2026-11-22T21:34Z origin/main was at `e3cb5c019b464a770cc7c6fe2fbc858ed29debf7`.
- `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged (fixer.md step 6).

Prepr: at `c18501831385cb135f9d893599c42504162e1c26`, a full run with `PREPR_SKIP_CLOSURES=1` (this delta adds no file; closures unchanged) and `MUTANT_CMD` = the fault-record block's `features_block.py` call printed `rc=1`: every code step passed, and its two refusals were the body's, step 7 `figures` (a probe cited by a path not in the tree, now cited by `git show` at the verdict SHA) and `unpinned sites` (the round-1 lines at their old numbers, now listed at this head's). Its diff-mutant step printed the same 16 survivors as round 1, all in lines this round does not touch, each dispositioned below. With the code unchanged, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` on this body then printed `PRE-PR: c18501831385cb135f9d893599c42504162e1c26 … rc=0`. No receipt is written under `PREPR_SKIP_CODE`, so this commit carries no `Prepr:` trailer.

## Mutation proof

Round 2 (this repair). The block's failing check and the review's three survivors, driven one mutant at a time on `fault_log.py` through the fault-record block (`features_block.py`, prelude by `--emit-prelude`), restored after each; `git status` after the drive lists only the two edited files. Driver: scratch, sha1 `bcf536df5bbbfc4f35c179c3c9e4b32ad20080c9`. All 9 killed:
- M1 `_ended` not registered; M2 `_ended` releases without saving; M5 setup does not await `old.ending`; M6 the last save not kept on `ending`: each fails `a setup that fails after the record's … releases the listener and the deferred save …`.
- M3 `_release` not once: fails `open, then unload, then an event fired after close …` (a second close saves again).
- M4 `async_close` skips its save: fails 5 checks, `open, the stop event, then a reload …` and `through async_setup_entry …` among them.
- F `if part.strip()` removed from `code_text`: fails `an empty item between or after commas records nothing …`.
- K `[-EPISODES_MAX:]` removed from `loaded`: fails `a stored document of 250 rows … loads as its newest 200 …`.
- L `max(now_s, start_s)` as `now_s` in `note`: fails `a reading stamped before the open row's start closes it at its start …`.

Failing test first: this head's `tests/features.py` on `9f133225f7`'s `fault_log.py` fails exactly the failed-setup check: `(listeners left, timers left, rows the next setup loads, listeners after it, saves on one event)` read `failed=(1, 1, [[…205, …205, 'P3', True]], 2, 1)` against the unload control's `(0, 0, [[…205, …206, 'P3', False]], 1, 1)`: the listener and the deferred save survive, the row closed inside the window is never saved, and two listeners run (`1 of 24 FEATURES BLOCK FAILED`); at this head `ALL 24 FEATURES BLOCK PASSED`. The F, K and L checks pass at both, as a check for a survivor does: their kill is the mutant above.

Round 1:

The mutants are applied one at a time to the head's production lines and restored after each run; `git diff --stat` is unchanged after every drive. The driver is a scratch script, sha1 `ae88b8d8ff0ac35858c025bb6da5ad45540920f4`. Each runs the fault-record block through `tools/audit/seat/features_block.py` (prelude by `--emit-prelude`), W1067-G7b-1 for the Tuya table, or `tests/config_flow_steps.py` / `tests/finite_boundary.py` where named. Every one of the 53 is killed (M46–M53 are below):
- M1 healthy set without `AMBIGUOUS_ACTIVITY_TOKENS`: fails `the text slot: heating and idle record nothing …`.
- M2 `strict=False`: fails `the flag slot: … heating on a sensor fault slot is no reading (strict) …`.
- M3 `_UNREAD = ()`: fails `unavailable mid-episode does not close the row …`.
- M4 no split on `,`; M5 no length budget; M6 head instead of tail: each fails `two faulted GCHV members keep their items …`.
- M7 no ring cap: fails `250 episodes keep the newest 200 …` and the store check. M8 no code cap and M9 no `dropped` count: the same ring check.
- M10 no save on open or close: fails `120 flaps …` and `open, then unload …`.
- M11 no deferred timer; M12 window at zero; M26 `SAVE_MIN_S = 120`; M38 timer not cleared after firing: each fails `120 flaps in 120 s write at most 3 saves …`.
- M13 close leaves the listener: fails `… the listener is gone …`. M14 close not idempotent: the same check (3 saves, not 2).
- M15 no stop hook; M41 stop hook does not close: each fails `… open, the stop event, then a reload …`.
- M16 `late` never set: fails `a stored P3 whose first read after a restart is OK closes …, marked late`. M36 `fresh` never cleared: the same check's second row.
- M17 first read member by member: fails `a restart whose first member reads OK …`.
- M18 view `{}` with no record; M19 a record with no source: each fails `no fault source: … the section is null`.
- M20 no list suggestion; M21 no `binary_sensor.{p}_alarm` row: each fails `pre-fill: …`.
- M22 no Tuya `fault` row; M23 no `fault_description` row: each fails W1067-G7b-1 `the tuya_heat_pump table resolves each role …`.
- M24 cap `> 99`: fails `config_flow_steps.py` `five fault-text entities are refused …`.
- M25 no options row: fails four checks, `the telemetry page renders the fault-text field …` among them.
- M27 tally of a row with no code: fails `the flag slot's section: …`. M28 tally without its last end: fails `a synthetic day …`.
- M29 healthy-after-healthy reported as a change, and M42 same-code reported as a change: each fails `OK, E5, OK 40 s apart …`.
- M30 clip at `<`; M31 a 3-character join: each fails `the 160-character budget is inclusive …`.
- M32 `1 < number`; M33 no 32-bit cap: each fails `the flag slot: …` (1 gives 0x0001; 2**32 gives no code).
- M34 absent `dropped` reads 1: fails the store check.
- M35 an unreadable flag mid-episode closes the row: fails `a sensor fault slot reading a register: …`.
- M37 `wait <= 1`; M40 setup keeps the old record: each fails `one second before the save window ends …`.
- M39 a failed save re-raised; M43 no `releases` field: each block exits 1 on the raised `OSError` or `AttributeError`.
- M44 setup sections collapsed: fails `config_flow_steps.py` `the intact grouping table hides nothing …`.
- M45 `FAULT_LOG_STORE_VERSION = 2`: fails `finite_boundary.py` `a store whose version exceeds 1 overrides the default migration hook …`.

Diff sweep:
- Command: `python3 -I tools/audit/seat/mutant_run.py --diff 8ef450936a...HEAD --path <file> --report-only`, over every operator site with no cap. The block runs for `fault_log.py` and `modbus_prefill.py`, `config_flow_steps.py` for `config_flow.py`.
- At a7909830de it left 6 survivors in `fault_log.py` and 1 in `config_flow.py`:
  - five are killed at this head by M42, M44, M45 and the deletions of `__all__` and the `unsub` field;
  - one is triaged equivalent (`tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json`: `0 <= number` cannot differ, since parse_bool reads 0 as healthy before that line).
- `modbus_prefill.py`: none survived.

`prepr.sh`'s own diff-mutant step drew the first 40 mutants in file order, all run under `MUTANT_CMD` = the fault-record block. It reported 16 survivors. None of them is a mutant of the block's own lines; each is killed by the script that reads its line, measured one at a time by the same driver:
- `config_flow.py`:
  - `multiple: bool = True` as the default (M46): `config_flow_steps.py` exits on `TypeError`.
  - `"multiple": False` and the row's `multiple=False` (M53, M52): 23 checks fail.
  - `>=` at the cap (M47) and the cap's `RETURN_DEL`: `five fault-text entities are refused …`.
  - `collapsed: True` (M44): `the intact grouping table hides nothing …`.
  - The step without its check (M48): `five fault-text entities are refused …`.
  - The `STMT_DEL`s at `defaults = {`, the two `return {` and `too_many =`: the run exits on the `NameError` or on a `None` schema. This is the earlier `config_flow.py` sweep's result, where only the `collapsed` mutant survived.
- `const.py` `FAULT_TEXT_ENTITIES_MAX: Final = 5` (M49): `five fault-text entities are refused …`.
- `device_prefill.py` scale `2.0` on either new row (M50, M51): W1067-G7b-1 `the tuya_heat_pump table resolves each role … at scale 1.0`.
- `fault_log.py` `FAULT_LOG_STORE_VERSION = 2` (M45): `finite_boundary.py`.

Failing test first, at the merge base's production with this head's tests (worktree at 8ef450936a):
- the fault-record block exits on `ImportError: cannot import name 'fault_log'`;
- W1067-G7b-1 exits on `AttributeError: … no attribute 'CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES'`;
- `config_flow_steps.py` fails `the flat fields and the sections are one table …` and exits on the same `AttributeError`.

## Null control

- The failed-setup check's control is the unload path, `async_close` then the same callbacks: `(0, 0, [P3 row watched to its end], 1, 1)` for both at this head.
- The empty-item check's control: `E5, E6` reads `E5, E6`, and a lone comma reads healthy. The 250-row load's: exactly 200 rows load whole. The back-stamped reading's: a reading 30 s after the start closes a 30 s row.
- `OK` then `OK` makes no row. A healthy reading while healthy, and the same code while open, are not changes.
- An entry with no fault slot: no record, no listener, no stop hook, no store file, and a null section. This holds through `async_setup_entry` and through `async_setup` alike.
- The synthetic day sampled once per 30-minute cycle, today's path, sees at most 2 rows. The event path sees 13.
- `heating` on a `binary_sensor` fault slot reads through the flag path, where on a `sensor` it is no reading.
- The flap check with the save window at zero writes 120 saves.
- The pre-fill gives no suggestion for a slot already set, nor for records without the Tuya signature.
- Five fault-text entities are refused; four save.

## Figures

- The reviewer's probe (`git show 170e96ec5c3d003f8fa7f4e09b5424dfd0d087d1:evidence/probe_failed_setup.py`, the `verdict/3870` ref; sha1 `1728c7fdb3325abce4b9086976fe7093a0ff59b7`), inserted after the failed-setup check in a scratch copy of `tests/features.py` and run through `features_block.run` (driver sha1 `be2bbf5fb52b43876f6b6142b0c1ff0b6a456eb2`), `(listeners, saves on one event)`:
  - on `9f133225f7`'s `fault_log.py`: failed setup `(2, 2)`, null control `(1, 1)`;
  - at this head: failed setup `(1, 1)`, null control `(1, 1)`.
  - An intermediate state of this repair, saving from `_ended` without the await, read `(1, 2)`: the first record's last save landed inside the second setup's event window. That is why the next setup awaits it.
- This repair's scope: `python3 tests/closure.py select --diff 9f133225f7` prints `MODE: SCOPED -- 15 script(s) run, 18 scoped out`. Each of the 15 was run at this head with `PYTHONPATH=tests/hastub` (`golden.py` under `GOLDEN_MODE=drift GOLDEN_REF=e3cb5c019b`, `env_drift.py --all e3cb5c019b`, `typing_ruler.py` with `HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python`), each rc 0: `ALL 6058 FEATURE CHECKS PASSED`, `ALL 2761 ENTITY CHECKS PASSED`, `ALL 615 checks PASSED` (config_flow_steps), `ALL 441 checks PASSED` (doc_claims), `ALL 164 DEBUG COLLECT CHECKS PASSED`, `ALL 153 BLOCK DUTY CHECKS PASSED`, `ALL 132 manual plan checks PASSED`, `ALL 120 FINITE BOUNDARY CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`, `ALL 12 typing-ruler source checks PASSED`, `ALL DEPLOYMENT SHAPE CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, and golden and env_drift `NO UNCLAIMED DRIFT` with `NO STALE FIXTURE: 56 committed fixture(s)`. The other 18 scripts of the merge-base scope read neither changed file and were green at `41b57b2daf` (round 1 figures).
- Architecture score at this head: `score.py --diff e3cb5c019b` and `score.py --diff 9f133225f7` each printed `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`; `tests/comment_ratchet.py` printed `comment_ratchet: OK`.

Round 1 figures, at `41b57b2daf` (merge base `8ef450936a`):

- Harness `dev/audit/harnesses/r11_owner_fault_text.py`, sha1 `91e2cf769f0ec43efd76d3b7a67dddf8f59ef03f`, prints counts only. Run on invented bundles (scratch, not committed):
  - a two-row text section prints `episodes 2`, `open 1`, `distinct_texts 2`, `late 1`, rc 0;
  - with one row deleted (the header's perturbation) it prints `episodes 1`, `late 0`;
  - a bundle with no section prints `fault_log absent`, rc 1.
  - The owner runs it on a real bundle; none is committed.
- Step 8, the readers of the two slots:

  `git grep -n "CONF_HEAT_PUMP_FAULT_ENTITY\|CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES\|heat_pump_fault_entity\|heat_pump_fault_text_entities" 41b57b2daf -- 'custom_components/heatpump_optimizer/*.py'`, excluding import lines.

  Every row it returns, with its disposition:
  - `fault_log.py:199` and `fault_log.py:202`: the record's source, this diff.
  - `pump_signals.py:514` (the learner freeze) and `pump_arbiter.py:1748` (the duty-switch void): unchanged in code. The pre-fill suggestion brings an accepting install under them, as the design rules.
  - `topology.py:140` (card slot), `const.py:1834` (staleness limit) and `config_flow.py:1472` (setup picker group): unchanged.
  - `config_flow.py:1754` and `config_flow.py:1757` (options rows), and `config_flow.py:2659`–`config_flow.py:2660` (the cap): this diff.
  - `device_prefill.py:135`–`device_prefill.py:136` and `modbus_prefill.py:106`, `modbus_prefill.py:276`–`modbus_prefill.py:278`: the pre-fill rows, this diff.
  - `entry_config.py:109` and `entry_config.py:132`: the declarations, this diff.
  - `const.py:152` and `const.py:158`: the names.
- Absent-fallback census null control, at 8ef450936a: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` prints `218 candidate key(s): … 82 with a named read not proven; 199 proven safe` with the base's `_NOOP_STATIC_SKIP` and again with `device_prefill.py` added. Both runs print `ALL 609 checks PASSED`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 8ef450936a1786abf4bb9610dc3336da4e77e8de` printed `Architecture score: dS +0.0000 NULL`.
  - An intermediate head printed `WORSENS (inadmissible: literal_clone_copies 114->116)`: `int(datetime.now(timezone.utc).timestamp())` was spelled twice in `fault_log.py`. It is now `_now_s()`.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` (`module_excess_loc` re-recorded as above). An intermediate head breached it by 1 (`FAIL module_excess_loc 21773 > 21772`), and `_entity_of`'s one-expression `multiple` paid that back.
- Comment ratchet: `python3 tests/comment_ratchet.py` printed `comment_ratchet: OK`.
- Closures: `tests/derive_closures.sh --scripts-from <16 scripts whose closure held __init__.py or diagnostics.py and that set an entry up> --record-only`, then `tests/closure.py merge --partial --allow-failures`.
  - `fault_log.py` joins 15 closures (`wood_advisor.py` never opens it).
  - The one failing recording, `entities.py`, failed exactly the three checks that read `fault_log.py`'s absence from `closures.json` (`… covers every python file`, the deployment-shape lane, `every tracked file is either measured or deliberately classified`); this merge answers them.
- CI prediction: `python3 tools/pr/ci_predict.py` printed `no closures, fast, governance or instrument red predicted against 8ef450936a17`.
- Scoped gate: `HPO_GATE_LOCK_LABEL=fault-text-gate GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8ef450936a ./tests/run.sh` at d287b46fff printed `MODE: SCOPED -- 30 script(s) run, 3 scoped out` and `1 TEST SCRIPT(S) FAILED`. The failure was `tests/typing_ruler.py`: `by_code[typeddict-item] did not grow  [recorded 0, measured 1 (+1)]`, from `_entity_of` unpacking a plain dict into `EntitySelectorConfig`. The head 41b57b2daf changes that one line only. On it, these re-ran green:
  - `tests/typing_ruler.py` (with `HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python`): `ALL 12 typing-ruler source checks PASSED`, `errors did not grow`;
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`;
  - `tests/config_flow_steps.py`: `ALL 615 checks PASSED`;
  - `tests/env_drift.py --all 8ef450936a`: `NO UNCLAIMED DRIFT`;
  - the architecture score: NULL.
  The other 28 scripts passed at d287b46fff.

## Red checks

- `tests / mutation`: predicted red by `prepr.sh` step 6d.
  - The diff adds 57 operator sites. No `killed_by` pin exists for them until `mutation-autofix` writes it after the push.
  - Every site is listed under `## Unpinned sites` with the check that kills it at this head.
  - The cheaper detector is the one that fired: step 6d's offline prediction, which costs nothing beyond the prepr run.
  - None cheaper exists for the pin itself. The pin is written only by the autofix lane, from CI's own mutant drive on the pushed head (`ci-autofix.md`).

## Unpinned sites

- custom_components/heatpump_optimizer/config_flow.py:1150 RETURN_DEL: pinned by mutation-autofix: killed by tests/config_flow_steps.py (every entity row loses its selector: AttributeError, rc 1)
- custom_components/heatpump_optimizer/config_flow.py:2659 CMP_BOUND: pinned by mutation-autofix: killed by tests/config_flow_steps.py (the fault-text cap checks)
- custom_components/heatpump_optimizer/config_flow.py:2660 RETURN_DEL: pinned by mutation-autofix: killed by tests/config_flow_steps.py (the fault-text cap checks)
- custom_components/heatpump_optimizer/fault_log.py:46 CONST: pinned by mutation-autofix: killed by tests/finite_boundary.py (a store version above 1 with no migration hook, #1740)
- custom_components/heatpump_optimizer/fault_log.py:48 CONST: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:50 CONST: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:53 CONST: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:55 CONST: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:62 CONST: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:84 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:86 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:100 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:100 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:102 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:102 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:104 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:106 CLAMP_DROP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:109 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:109 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:113 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:115 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:120 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:120 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:132 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:136 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:142 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:142 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:142 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:147 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:158 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:164 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:165 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:167 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:169 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:183 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:192 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:200 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:203 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:236 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:242 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:244 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:247 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:249 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:252 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:263 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:266 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:272 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:275 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:275 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:298 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:298 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:301 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:313 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:326 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:334 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:338 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:340 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:346 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:346 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:357 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:365 CLAMP_DROP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/modbus_prefill.py:277 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/modbus_prefill.py:277 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive

## Forward-carry

- FAULT-HOLD's text: when FAULT-TEXT lands first, the pre-fill and docs Fault alarm rows name the freeze and the void but not the 10-minute hold. The carry is appended to R11-OWNER-FAULT-HOLD's roster group, on `handoff/audit-r11-roster` at `981e3402e45381eec0148761147b3b81401832c2`, tagged `From r11-owner-fault-text`. Read back by `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json`: the group's last carry equals the carry text byte for byte. The untagged first landing (7d42e7ad3b) was dropped in the same queue. Carry: R11-OWNER-FAULT-HOLD

## Friction

- roster_queue.readback: unenforced: `roster_queue.py run`'s read-back printed `FAILED group R11-OWNER-FAULT-HOLD not in the roster at 981e3402e`, while `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json` holds the group and the carry exactly; the same miss printed at 7d42e7ad3 and 39ace5656. Carry: dismissed: a read-back miss after a verified push, recorded here and re-checked by hand
