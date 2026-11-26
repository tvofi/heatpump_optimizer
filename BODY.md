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

`439de9e4767af48089c66511eba036a5ac0aea12` merges origin/main `dbdc520e86e4453755f553ab21a39de205a70b34` into the PR head `bf613f006b`, which did not merge cleanly in `tests/deployment_shape.py`. Resolution delta for review: `git diff bf613f006b 439de9e476 -- tests/deployment_shape.py`, read against main's side with `git diff dbdc520e86 439de9e476 -- tests/deployment_shape.py`. The #1218 selection-cost note is the union of both histories (this branch's fault_log.py clause and main's entity-service and flow_limit.py clauses); its count is 181 of the 561 pairs and "all 181 among the 435", re-derived from the merged `tests/closures.json` by the Jaccard 0.80 predicate (main alone gives 182, which the same predicate reproduces). `tests/structure_budgets.json` merged without conflict; `python3 tests/structure.py` `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`; `git merge-tree --write-tree origin/main` on the head is clean.

`0e99fbe6282af2aebf31c7bdf8591d7b94ca4aee` is one commit on the PR head `61e49d1d83ef45aa083f50a054493fa64227f615`, repairing fix review `blocked 61e49d1d test-red`. It changes only `tests/deployment_shape.py`'s #1218 selection-cost note: 180 becomes 182 of the 561 pairs in both places (the count and "all 182 among the 435"). The history clause names the two pairs that the merge bringing R11-SEAM-cycle-solve's solve_gate.py joined at 0.80: env_drift.py/manual_plan.py and golden.py/manual_plan.py. solve_gate.py is read by env_drift.py's, golden.py's and manual_plan.py's closures. The count was derived with entities.py's own `_d308_pairs` predicate over `tests/closures.json`, not copied. It is 180 at `ef876fecad` (121 production files, before solve_gate.py), 182 at the code head `f0a1881e9d` and at `61e49d1d83`, and 182 at its merge with origin/main bb6377b4da, which `61e49d1d83` already contains. Null control: at `61e49d1d83` the note lacks the marker `182 of the 561`, and after the repair every marker entities.py checks is present. `tests/deployment_shape.py`: ALL DEPLOYMENT SHAPE CHECKS PASSED. Delta for review: `git diff 61e49d1d83 0e99fbe628`.

`61e49d1d83ef45aa083f50a054493fa64227f615` was this PR's previous head: its code was already in it and main merged cleanly, so the orchestrator's script set the body without a push.

`f0a1881e9d41d3cd80c97b42a701a7637ebe3dbc` merges origin/main `bb6377b4dad4e398d1a28bde54d30036a5b25a82` into `d7324bbc58`. Resolution delta for review: `git diff bb6377b4da f0a1881e9d -- dev/audit/rounds/round4/D6 docs/architecture.md tests/deployment_shape.py tests/features.py`. Each side added one module (`fault_log.py` here, `solve_gate.py` on main), so the module counts become 103 and the package closure 122 files. `fault_log.py` imports `homeassistant` at module level and `solve_gate.py` does not, so 37 such importers. `tests/features.py` keeps both appended blocks, with the fault-record block's last `R.check` closed before main's section. The ledger driver resolved `tests/structure_budgets.json` and `tests/closures.json`. At the merge: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` rc 0 (C32-C35 true, re-generated), `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`, `python3 tests/structure.py` `STRUCTURE RATCHET PASSED` (no metric below its budget, so no gain recorded), `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` `ALL 691 checks PASSED`.

`d7324bbc583ad81a11e6d92c5cff282eb6b54f01` is the code head of round 5. It repairs the block in `verdict/3870` at `ef876fecadb909be228a7c686bda5fb822149ae1`, the PR's head, which merges origin/main `5594a34a49404109b8e0f18bd5be18ddbb667cdf` into `d4e4e66f6b`. The head is one commit on `ef876fecad`.
- `d7324bbc58` adds one line to `tests/config_flow_steps.py`'s `options_fault_text_list`: `await recover(flow, "entities_pump", {key: members[:4], **SAVE_CLOSE})`. It changes no production line.
- Cause: main's `94125c37ed` census refuses a rendered flow error that no flow instance finishes. The fault-text check refused five entities and then saved four, but that flow went back to the menu and never finished. That left `options/entities_pump/too_many_fault_text_entities` unrecovered. The rooms check beside it already recovers its error the same way.
- `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`: at `ef876fecad`, rc 1 `1 of 690 checks FAILED` (`UNRECOVERED options/entities_pump/too_many_fault_text_entities`). At this head, rc 0 `ALL 691 checks PASSED`, `unrecovered_flow_error_triples=0`.
- At origin/main `dc2b2bab316419ced8f919c256908275a2cc3e25`, `git merge-tree --write-tree` reports no conflict, so main is not merged (fixer.md step 6).

Round 4's head and its notes follow.

`d4e4e66f6b6dde3e51e920f11db70ac362a4ff50` is the code head of round 4, a repair of `tests / mutation` at `092e9bc81cc8798f008784c882711806c5e72548` (job 137647802986 of run 45161329980). It is four commits on `092e9bc81c`:
- `ff475701b3` merges origin/main `0f63320c96cb4e1926a584c89d0dfe920d1778ab`; `git merge-tree --write-tree` reported no conflict. The merge is owed by the repair, not by a conflict: the red is main's `97026ed8cf` (`ci: record nightly kills`), which pins `_user_sensors_sections RETURN_DEL cd4695fb` on `    return fields`, a line this branch removed. CI's mutation job measures the merged tree, so only a head carrying the pin can delete it.
- `ffa74c5a6e` deletes that pin, as round 1 deleted its two GUARD_OFF siblings (`## Structure payment` above).
- `49ba06341c` records `fault_log.py:<module> CONST f34207b8` under `killed_by` (`## Red checks`). It changes no production line.
- `d4e4e66f6b` merges origin/main `3210fcd7334af9a870a8a7c23322fcaead7e14eb` (origin/main at 2026-11-25T01:54Z). `git merge-tree --write-tree` reported `CONFLICT (content): Merge conflict in tests/deployment_shape.py`, and prepr refused `merged tree` and `ci predict` (`governance / wave-script AGREEMENT UNMERGED`, `GRADER UNMERGED`) at `49ba06341c`. The conflict is the #1218 note's measured counts: main's `182 of the 561` / `182 among the 435`, against this branch's `167 of the 528` / `167 among the 406`. The resolution is re-measured with `_d308_pairs`' predicate (`tests/entities.py`) over the merged `tests/closures.json`: `180 of the 561`, `435` comparable, `all 121 files`. `config_flow_steps.py`'s pairs with `boost_drift_replay.py` and `plan_view.py` read 0.792, and 0.800 with `fault_log.py` removed from `config_flow_steps.py`'s closure, so this branch's two-pair movement holds on main's tree (182 - 2).
- The four commits were first written as `5f91d3cb32`, `08fc04fe96`, `c06dc46c3d` and `f2e30029bc` under the environment's committer name, then re-committed as `tvofi` with `git commit-tree` on the same trees and parents (`git rev-parse <old>^{tree}` equals `<new>^{tree}` for each). The ledger entry's reason and `## Red checks` cite `08fc04fe96`, the tree of `ffa74c5a6e`; it stays reachable on origin from `handoff-wip/r11-owner-fault-text` at `c06dc46c3d`, which this seat does not move.
- Re-executed at `d4e4e66f6b`: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`; `tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` printed `1874 unpinned site(s) of 8209 candidate sites, 1874 at the ratchet base 3210fcd7334af9a870a8a7c23322fcaead7e14eb; the ledger agrees with the deterministic inventory`; and prepr (`PREPR_SKIP_CLOSURES=1`: this delta adds one ledger file and no selectable script).

Round 3's head and its notes follow.

`b98650edabd8afc2f1d5478172a1e2bd3e973b7e` is the code head of round 3, a local repair. It is one commit on `7a666abfe90b0e0db2468b04dc0b7b43cb0ce582`, the PR's head after its clean merge with main.
- The commit changes two test files: `tests/features.py` (two checks) and `tests/deployment_shape.py` (the #1218 note's pair count). It changes no production line.
- At 2026-11-23T04:40Z origin/main was at `3153a635b4012d3f8a157c2aaaa34f8da5c8d357`. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged (fixer.md step 6).
- Why this push cancels the running pin drive: the `mutation-pins` drive at `7a666abfe9` printed `MUTATION TABLE INCONCLUSIVE`. Its reason was `the baseline is already red in tests/entities.py`: `entities.py`'s #1218 check found `167 of 528 pairs` in the tree, while the note still said 169. The shard that had concluded (3 of 12) left `fault_log.py:142 GUARD_OFF`, `fault_log.py:244 GUARD_OFF` and `modbus_prefill.py:277 GUARD_OFF` unpinned. The fault-record block kills the two `fault_log.py` ones locally (below). The drive's other shards measure against the same red baseline, so their pins cannot be trusted. This head fixes that baseline.

Round 2's head and its notes follow.

`c18501831385cb135f9d893599c42504162e1c26`, merge base `e3cb5c019b464a770cc7c6fe2fbc858ed29debf7`. Round 2: the repair of the round-1 block at `9f133225f72bc9581a411bdc40d544dd447f78ee`, on top of it.
- At 2026-11-22T21:34Z origin/main was at `e3cb5c019b464a770cc7c6fe2fbc858ed29debf7`.
- `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged (fixer.md step 6).

Prepr: at `c18501831385cb135f9d893599c42504162e1c26`, a full run with `PREPR_SKIP_CLOSURES=1` (this delta adds no file; closures unchanged) and `MUTANT_CMD` = the fault-record block's `features_block.py` call printed `rc=1`: every code step passed, and its two refusals were the body's, step 7 `figures` (a probe cited by a path not in the tree, now cited by `git show` at the verdict SHA) and `unpinned sites` (the round-1 lines at their old numbers, now listed at this head's). Its diff-mutant step printed the same 16 survivors as round 1, all in lines this round does not touch, each dispositioned below. With the code unchanged, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` on this body then printed `PRE-PR: c18501831385cb135f9d893599c42504162e1c26 … rc=0`. No receipt is written under `PREPR_SKIP_CODE`, so this commit carries no `Prepr:` trailer.

## Mutation proof

Round 5. Each mutant is one exact replacement, followed by `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` and a restore. The tree was clean after the run, and all four mutants were KILLED:
- M1, the cap `> FAULT_TEXT_ENTITIES_MAX` turned to `>=` (`config_flow.py`): rc 1, FAIL `five fault-text entities are refused ...; null control, four save` and `after its entities_pump error the same flow finishes`.
- M2, the recovery without `**SAVE_CLOSE`: rc 1, FAIL `after its entities_pump error the same flow finishes` (the flow returns to the menu) and the census row `[options/entities_pump/too_many_fault_text_entities]`.
- M3, the recovery run on a fresh options flow instead of the one that rendered the error: rc 1, FAIL the census row `[options/entities_pump/too_many_fault_text_entities]`.
- M4, `_fault_text_errors` returning `{}`: rc 1, FAIL `five fault-text entities are refused ...`.

Round 3, the local repair. The driver applies `tests/mutation_table.py`'s own generated mutant (`candidates()`) at each `fault_log.py` site listed in `tests / mutation`'s refusal at `7a666abfe9`. It runs one mutant at a time and restores the file after each. Each mutant runs against `tests/features.py`'s preamble plus its R11-OWNER-FAULT-TEXT section, from the section heading to `# 9: the prefill rows`. Driver: scratch, sha1 `e2bfe3acdba9dcb1ea229df7587b98a7f430e66a`. Section runner: scratch, sha1 `eb8de62e3bdee585b5a4039e0cd9b052895e7fcf`. `git status --short` after the drive lists only this round's two edited test files.
- Null run: `NULL SURVIVED`, and the section printed `ALL 23 FL SECTION PASSED`.
- At this head, all 58 `fault_log.py` sites the refusal lists are `KILLED`, including `142 GUARD_OFF`, `142 BOOLOP`, `142 CMP_BOUND` and `244 GUARD_OFF`.
- Two sites survived the section as it stood at `7a666abfe9` (the same driver, `FL_FEATURES` = that head's `tests/features.py`): `SURVIVED 365 CLAMP_DROP` and `SURVIVED 46 CONST`. Each now has a check:
  - `365 CLAMP_DROP` (`max(0, now_s - log.open[0])` as `now_s - log.open[0]` in `diagnostics_view`): fails `an open row stamped 300 s after the view's clock … shows 0 open seconds, never a negative span …`. Its null control is a row stamped 30 s before the clock, which shows 30.
  - `46 CONST` (`FAULT_LOG_STORE_VERSION = 2`): fails `a fault record saved at store version 1 loads whole and saves back at 1 …`. Its null control is a document stamped version 2, which is refused, so the record starts afresh. Round 1's M45 already showed `finite_boundary.py` killing this mutant, so the new check is a second, direct pin.
- `config_flow.py`'s three listed sites were driven the same way against `tests/config_flow_steps.py` (`NULL SURVIVED`). `1150 RETURN_DEL`, `2659 CMP_BOUND` and `2660 RETURN_DEL` are all `KILLED`.
- `modbus_prefill.py:277` was not driven locally. A full `tests/features.py` run takes over an hour on this host, and the drive above is `features.py`'s own. The mutation drive on this head decides it.

Round 2. The block's failing check and the review's three survivors, driven one mutant at a time on `fault_log.py` through the fault-record block (`features_block.py`, prelude by `--emit-prelude`), restored after each; `git status` after the drive lists only the two edited files. Driver: scratch, sha1 `bcf536df5bbbfc4f35c179c3c9e4b32ad20080c9`. All 9 killed:
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

- Round 5: `tests/config_flow_steps.py` at origin/main `dc2b2bab31`, without this branch: rc 0, `ALL 684 checks PASSED`, `unrecovered_flow_error_triples=0`. The census is green on main, and this head adds 7 checks to it, all passing.
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

Round 3, at `b98650edab`:
- The #1218 pair census is `entities.py`'s `_d308_pairs` (Jaccard over production closure files, empty sets skipped, floor 0.80), re-derived over `git show <rev>:tests/closures.json` by a scratch script:
  - this head: 121 production files, 167 of 528 pairs, 406 comparable;
  - the merge with origin/main `3153a635b4` (`git merge-tree --write-tree`): 167;
  - null control, origin/main `3153a635b4` itself: 120 files, 169 pairs. That 169 is the figure the note carried.
- The two pairs that leave are `config_flow_steps.py` with `boost_drift_replay.py` and `config_flow_steps.py` with `plan_view.py`. Each moves from 0.800 to 0.792. `fault_log.py` is in `config_flow_steps.py`'s recorded closure and in neither of the others'.
- `tests/deployment_shape.py`'s note now says 167, and names the move.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff 7a666abfe9` prints `MODE: SCOPED`. Its run list includes `tests/entities.py`, `tests/features.py` and `tests/deployment_shape.py`. CI runs it.

Round 2:

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

- At `61e49d1d83`:
  - `tests / entities` (reproduced by the reviewer, verdict `blocked 61e49d1d test-red`): the #1218 note check, missing `182 of the 561`. Repaired at `0e99fbe628` (see `## Head`).
  - `gate` (jobs 139191391388 and 139202829812): `FAIL run(s) [45606679346, 45611218188] at this head are still being judged; their gate decides`. The gate waits on those runs; it names no failing lane.
  - `tests / nightly-ha (stable)` and `(2025.2.0)` (jobs 139189653789 and 139189653786): the inherited a5:pages_ok red answered below; main's scheduled Nightly fails the same checks.
  - `tests / nightly-status` (job 139184232368): it reads main's last scheduled Nightly, not this head.

- `tests / fast (3.14)` and `gate`: red at `ef876fecad` (fast job 138978772934, gate job 138995154315) on `tests/config_flow_steps.py`: `FAIL every rendered flow error is recovered on the flow that rendered it [options/entities_pump/too_many_fault_text_entities]`. Repaired at `d7324bbc58` (`## Head`): the fault-text error is now recovered on the flow that rendered it.
  - Cheaper detector: a scoped run of `config_flow_steps.py` on the tree merged with main. The census reached this branch only through the merge of main `5594a34a49` at `ef876fecad`, and no local run was made at that head.
- Local scoped gate at `d7324bbc58` (`GATE_SCOPE=auto GOLDEN_MODE=drift`, `MODE: SCOPED`, load average 50-100): `config_flow_steps.py` ok. Five other scripts failed: `optimality.py` (a recorded claim's gap is at the bar on this host's BLAS), `card.mjs` (node heap out of memory), `entities.py` (3 of 2760), `typing_ruler.py` (the host's unpinned venv-ha interpreter) and `stress.py` (3 timing checks). The diff from the CI-graded `ef876fecad` is one line of `tests/config_flow_steps.py`, which none of those scripts reads, and CI at `ef876fecad` had none of them red, so this is host load and environment, not the change. CI is the authority.
- `python3 tools/pr/ci_predict.py` at `d7324bbc58`: one predicted red, `governance / wave-script AGREEMENT UNMERGED`, because the head did not merge into main. The merge at `f0a1881e9d` (`## Head`) repairs it.
- `tests / mutation`: red at `092e9bc81c` (job 137647802986) with `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory: custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections RETURN_DEL cd4695fb: disposition names no site the inventory generates (old pin '    return fields')`. Reproduced locally on the merge with main, then repaired at `49ba06341c` (head `d4e4e66f6b`). Pins: `unmeasured` at this head.
  - The stale pin is deleted (`## Head`).
  - Behind that refusal, `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` at `08fc04fe96` printed `1875 unpinned site(s) against 1874 at the ratchet base 0f63320c96cb4e1926a584c89d0dfe920d1778ab, 1 of them added by this diff` and `ADDED UNPINNED custom_components/heatpump_optimizer/fault_log.py:62 CONST: REGISTER_MAX = 0xFFFFFFFF`.
  - `python3 tests/mutation_table.py --pin-killed --base origin/main` at `08fc04fe96` printed `PIN KILLED: 0 pinned, 1 left unpinned (0 survived, 0 not started for the budget, 0 exclusive tails cut, 0 timed out, 1 skipped)`, the site `skip-unparseable`. `mutation_table.inventory` forms the mutant `REGISTER_MAX = 8589934590xFFFFFFFF`, because the CONST operator's `_NUM` (`-?\d+\.?\d*`) matches only the leading `0` of a `0x` literal, so no drive applies it.
  - The operator's doubling, applied as the value it names (`REGISTER_MAX = 0x1FFFFFFFE`), in a detached worktree at `08fc04fe96`, with `PYTHONPATH=tests/hastub:tools/devices python3 tools/audit/seat/features_block.py --prelude 'exec(open(OUT).read())' 'from heatpump_optimizer import fault_log as _fl  # noqa: E402' '# 7: the ring and the tally.'` (OUT written by `--emit-prelude` on the same tree): baseline `ALL 7 FEATURES BLOCK PASSED` rc=0; mutant `1 of 7 FEATURES BLOCK FAILED` rc=1, on `the flag slot: ... null control, the same state on a binary_sensor reads through the flag path` (`str(0x100000000)` read as code `0x100000000`, not `NO_CODE`). Null control: the same value written `4294967295`, `ALL 7 FEATURES BLOCK PASSED` rc=0. Recorded as `tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json`, with that command in its reason.
  - After, at `49ba06341c`, the same table command's summary line is `1874 unpinned site(s) of 8209 candidate sites, 1874 at the ratchet base 0f63320c96cb4e1926a584c89d0dfe920d1778ab; the ledger agrees with the deterministic inventory`, and at `d4e4e66f6b` the same against `3210fcd733` (`## Head`). My local 1500 s timeout cut off its drive of the 8 sampled mutants, which is left to CI's required check.
  - Cheaper detector: none within the freeze. The pin landed on main after the handoff, and only a merged tree carries it, which is the tree CI's mutation job measures. The hex-literal site was behind the ledger refusal, so it could not be reached first. Before that: at `7a666abfe9`, red with `MUTATION TABLE REFUSED`, 63 sites added by this diff; the next three sub-items are round 3's.
    - The pin drive at `7a666abfe9` was `INCONCLUSIVE` because its `tests/entities.py` baseline was red on the #1218 pair count (169 in the note, 167 in the tree). This head fixes that note (see `## Head`), and `mutation-autofix` re-measures on this head.
    - The two sites the fault-record block left alive, `fault_log.py:46 CONST` and `fault_log.py:365 CLAMP_DROP`, have killing checks at this head (`## Mutation proof`, round 3).
- `tests / fast (3.14)` (`tests/entities.py`): red at `7a666abfe9` on `and the lane's docstring records those measured numbers as the selection-cost note (#1218)`, because the note said 169 where the tree measures 167. Fixed at this head.
  - The cheaper detector was `prepr.sh`'s scoped run of `entities.py` after the merge with main: that merge's `fault_log.py` closures moved the count. The merge was a hand resolution with no prepr run after it.
- `tests / nightly-ha (stable)` and `(2025.2.0)`: red at `7a666abfe9` on `FAILED: 2 of 66 checks: ['a5:pages_ok', 'run:exit_status']`, with `raised=['grid:InvalidData']`. The check is not required (`tests.yml`'s `nightly-status` note), and this diff does not cause it. `fix/r11-owner-mode-legs`'s run of the same job printed the same line: `a5:pages_ok [raised=['grid:InvalidData'] …]`. This diff touches no grid page.
- Earlier rounds' prediction:
  - The diff adds 57 operator sites. No `killed_by` pin exists for them until `mutation-autofix` writes it after the push.
  - Every site is listed under `## Unpinned sites` with the check that kills it at this head.
  - The cheaper detector is the one that fired: step 6d's offline prediction, which costs nothing beyond the prepr run.
  - None cheaper exists for the pin itself. The pin is written only by the autofix lane, from CI's own mutant drive on the pushed head (`ci-autofix.md`).

## Unpinned sites

- custom_components/heatpump_optimizer/config_flow.py:1150 RETURN_DEL: pinned by mutation-autofix: killed by tests/config_flow_steps.py (every entity row loses its selector: AttributeError, rc 1)
- custom_components/heatpump_optimizer/config_flow.py:2659 CMP_BOUND: pinned by mutation-autofix: killed by tests/config_flow_steps.py (the fault-text cap checks)
- custom_components/heatpump_optimizer/config_flow.py:2660 RETURN_DEL: pinned by mutation-autofix: killed by tests/config_flow_steps.py (the fault-text cap checks)
- custom_components/heatpump_optimizer/fault_log.py:46 CONST: pinned by mutation-autofix: killed by tests/finite_boundary.py (a store version above 1 with no migration hook, #1740) and by the fault-record block's `a fault record saved at store version 1 loads whole …` (round 3)
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
- custom_components/heatpump_optimizer/fault_log.py:365 CLAMP_DROP: pinned by mutation-autofix: killed by the fault-record block's `an open row stamped 300 s after the view's clock …` (round 3; it survived the block before)
- custom_components/heatpump_optimizer/modbus_prefill.py:277 BOOLOP: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive
- custom_components/heatpump_optimizer/modbus_prefill.py:277 GUARD_OFF: pinned by mutation-autofix: killed by the fault-record block of tests/features.py in this head's mutant drive

## Forward-carry

- `tests/mutation_table.py`'s CONST operator forms an unparseable mutant for an integer constant written with a `0x`, `0o` or `0b` prefix: `_NUM` matches the `0` alone (rule: the regex at its definition). `--pin-killed` reports such a site SKIP-UNPARSEABLE, so it can be pinned only by hand, as `fault_log.py` CONST f34207b8 is here. The generator is outside this group's seam, and this seat may push refs only. Carry: dismissed: named in the round-4 handoff report to the orchestrator, who owns routing it to the mutation-table owner.
- FAULT-HOLD's text: when FAULT-TEXT lands first, the pre-fill and docs Fault alarm rows name the freeze and the void but not the 10-minute hold. The carry is appended to R11-OWNER-FAULT-HOLD's roster group, on `handoff/audit-r11-roster` at `981e3402e45381eec0148761147b3b81401832c2`, tagged `From r11-owner-fault-text`. Read back by `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json`: the group's last carry equals the carry text byte for byte. The untagged first landing (7d42e7ad3b) was dropped in the same queue. Carry: R11-OWNER-FAULT-HOLD

## Friction

- roster_queue.readback: unenforced: `roster_queue.py run`'s read-back printed `FAILED group R11-OWNER-FAULT-HOLD not in the roster at 981e3402e`, while `git show 981e3402e4:dev/programme/rosters/wave-r11-groups.json` holds the group and the carry exactly; the same miss printed at 7d42e7ad3 and 39ace5656. Carry: dismissed: a read-back miss after a verified push, recorded here and re-checked by hand


