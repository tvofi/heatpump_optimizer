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

## Head

`41b57b2daf18d7c4dcfa33d074c601626a5a4277`, merge base `8ef450936a1786abf4bb9610dc3336da4e77e8de`.
- At 2026-11-22T19:49Z origin/main was at `e3cb5c019b464a770cc7c6fe2fbc858ed29debf7`.
- `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged (fixer.md step 6). The merge driver resolves `tests/closures.json` as a set.

Prepr: the single `tools/pr/prepr.sh` run, at `41b57b2daf18d7c4dcfa33d074c601626a5a4277` with `PREPR_SKIP_CLOSURES=1` (the closures recorded above) and `MUTANT_CMD` = the fault-record block's `features_block.py` call, printed `PRE-PR: 41b57b2daf18d7c4dcfa33d074c601626a5a4277 00000000000000000000000000000010000 rc=1`. Its one refusal was step 7 `pr-body`: `check \`mutation\` is red and \`## Red checks\` does not name it`. Every code step passed, and its two WARN lines are answered under `## Mutation proof` and `## Unpinned sites`. This body names that red; `tools/pr/prepr.sh --body-check` (step 7 alone, the code untouched) then printed `PR-BODY: 0 error(s)`, rc 0. No receipt was written (rc=1), so this commit carries no `Prepr:` trailer.

## Mutation proof

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

- `OK` then `OK` makes no row. A healthy reading while healthy, and the same code while open, are not changes.
- An entry with no fault slot: no record, no listener, no stop hook, no store file, and a null section. This holds through `async_setup_entry` and through `async_setup` alike.
- The synthetic day sampled once per 30-minute cycle, today's path, sees at most 2 rows. The event path sees 13.
- `heating` on a `binary_sensor` fault slot reads through the flag path, where on a `sensor` it is no reading.
- The flap check with the save window at zero writes 120 saves.
- The pre-fill gives no suggestion for a slot already set, nor for records without the Tuya signature.
- Five fault-text entities are refused; four save.

## Figures

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
- custom_components/heatpump_optimizer/fault_log.py:234 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:240 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:242 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:245 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:247 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:250 RETURN_DEL: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:261 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:264 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:270 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:273 CMP_BOUND: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:273 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:297 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:309 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:323 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:327 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:339 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/fault_log.py:347 CLAMP_DROP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/modbus_prefill.py:277 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/modbus_prefill.py:277 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive

## Forward-carry

- FAULT-HOLD's text: when FAULT-TEXT lands first, the pre-fill and docs Fault alarm rows name the freeze and the void but not the 10-minute hold. The carry is appended to R11-OWNER-FAULT-HOLD's roster group, on `handoff/audit-r11-roster` at `981e3402e45381eec0148761147b3b81401832c2`, tagged `From r11-owner-fault-text`. Read back by `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json`: the group's last carry equals the carry text byte for byte. The untagged first landing (7d42e7ad3b) was dropped in the same queue. Carry: R11-OWNER-FAULT-HOLD

## Friction

- roster_queue.readback: unenforced: `roster_queue.py run`'s read-back printed `FAILED group R11-OWNER-FAULT-HOLD not in the roster at 981e3402e`, while `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json` holds the group and the carry exactly; the same miss printed at 7d42e7ad3 and 39ace5656. Carry: dismissed: a read-back miss after a verified push, recorded here and re-checked by hand
