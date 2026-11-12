R10-ECL110-MQTT-OFF-NEUTRAL (triage `dev/programme/triage/s6-batch168.md` P582; owner ruling under mandate 6715477401, 2026-11-11: no actuator arm may leave the pump displaced once the optimizer is off or unloaded, MQTT included). Re-homed R10-GENERIC-HEAT-CURVE-PERSISTENT carry 6 (ghc-d02, body item 711d4be1).

**(1) Measured first, at the merge base `fc2a7edcf2`.** A coordinator with both ECL110 topics and the offset entity configured publishes displace -3, then takes MODE_OFF (`async_set_mode`) or unload (`async_unload_entry`). The value standing on each topic is its last publish. With retain off, both paths leave `-3` on `ecl/set` and on `ecl/cmd`. With retain on, they leave `-3`, retained, on both. The entity arm (null control) is restored to 0 on all four paths by `off_restore`. A non-zero displace stands, so (2) applies and (3) does not.

**(2) The fix: one hook, no second owner of unload.** The MQTT arm becomes a second neutral consumer of `off_restore` (`heat_curve.MQTT_CONSUMER`, factory `_mqtt_restorer`, neutral 0). `heat_curve.publish` arms it before the MQTT publish. With no topic configured the factory answers None, and `off_restore.async_arm` then refuses with no side effect, so the arm needs no topic guard of its own. MODE_OFF (`off_restore.async_mode_change`) and unload (`__init__.async_unload_entry` -> `off_restore.async_restore`) therefore publish displace 0 to each configured topic, with the user's qos and retain. That is the same restore, latch and once-only rule the entity arm already gets. `off_restore.py` and `__init__.py` are unchanged.
- `publish_ecl110_topics` now returns whether every configured topic took its publish. The restore writer raises on a refusal, so the restore is latched and the arm stays armed for the next off or unload. The plan's per-cycle publish still ignores the result, as before.
- Design choice: the legacy JSON body of the neutral says `heat_pump_on: true` and reason `off_restore`. Releasing the pump stops holding supply off; it does not command supply off. `heat_pump_on: false`, which the MODE_OFF row of `_fixed_mode_action` carries, would displace a receiver that acts on it.
- Alternative not taken: publishing 0 from `async_publish_current_action` / `_async_peak_guard_transition` on MODE_OFF. That would cover MODE_OFF only, not unload or a crash left armed, and would add a second owner of the off rule beside `off_restore`.

**(4) #3299 and the ghcp carries, re-read at origin/main `fc2a7edcf2`.** #3299's merged diff (merge `20d96598c9`, against its first parent `9b1bb58db7`) added `heat_curve.py` and `off_restore.py` and moved `_ecl110_legacy_payload` / `_publish_ecl110_topics` out of the coordinator. This change builds on exactly that seam.
- ghcp-03 (`origin/design/R10-GENERIC-HEAT-CURVE-PERSISTENT:design.md`, Notes for the fixer): every symbol it names is still at origin/main and none moved module. `Restorer`, `async_arm`, `async_restore`, `async_forget` and the `restored` field are in `off_restore.py`; `state_for` and the delta conversion (`_DELTA_PER_K`) are in `heat_curve.py`.
- ghcp-r3: its line anchors were taken at `e066a630`. The four in `coordinator.py` (6484/6491/6555/7670) and `entry_config.py:289` no longer point at the cited code, because the files grew. The code they name is intact under its symbols: `async_set_mode`, the `off_restore.async_mode_change` call, `async_shutdown`, the `heat_curve.publish(` call and `_WIRING`. `inputs.py:597` (`write_setpoint`) and `__init__.py:426`/`:438` (`async_restore`, `async_forget`) hold. Nothing these citations describe has moved semantically. This change follows each by symbol, never by line.

**Carries, by number.** The brief has two. **Carry 0** is r10-outside-supply-stale-step's body item 30ec8edf. **Carry 1** is its landing on the roster (commit 84184ae668 on `origin/handoff/audit-r10-roster`, replacing d188b50681). Both name the same two sibling publish sites, (1) and (2), answered once here for both carries:
- **Carry 0 and Carry 1, site (1)** (`async_publish_current_action` publishes the displace and set-point of the action cut at the solve): not changed. The plan holds no per-step displace for a late cycle to look up. `displace_value` is derived once per solve from the current action through the optimizer's guard chain (`optimizer.py`, the action builder's `"displace_value": float(displace_value)`). It is a curve offset that stands until the next solve, not the switch command `cycle_supply` re-derives per step. Re-deriving it per step would duplicate that chain outside its owner. Disposition below.
- **Carry 0 and Carry 1, site (2)** (the legacy payload's `heat_pump_on` from that call can disagree with the switch for the landing step): fixed. `_apply_action` passes the `on` it wrote through `_write_supply` into `async_publish_current_action(..., heat_pump_on=on)`. The legacy body is now the switch's own write. Callers that pass nothing (the climate entity, peak-guard release) keep the action's value. Control as the carry named it: a cycle landing one step late (`cycle_supply` answering the landing step against the action's `heat_pump_on: false`) published `heat_pump_on: false` beside a switch write of `true` at the base, and `true` beside `true` at the head. Null control: the same cycle inside its step agrees at both ends (`false` / `false`).

## Head

`e43f976d22648a95b4c41966a63cc890b2c6c32c` on merge base `fc2a7edcf2be8847037d9e8dc5bde460977befa8` (origin/main at the time of measurement).

## Mutation proof

Block: `python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-GENERIC-HEAT-CURVE — the displace through a number entity' '# A crash: the write was armed'`, where the prelude is the one `--emit-prelude` writes for the same block. Each mutant was applied alone and restored with `git checkout`. The checks that went red:
- M1, the `off_restore.async_arm(hass, entry, config, MQTT_CONSUMER)` call in `heat_curve.publish` replaced by `pass`: FAIL "MODE_OFF and unload leave displace 0 standing on both ECL110 topics, retain on and off"; FAIL "an MQTT arm never published is not restored; one published is restored once, not per off" (2 of 21).
- M2, `heat_pump_on=on` dropped from `_apply_action`'s call: FAIL "the legacy payload's heat_pump_on is the switch's write, inside its step and a step late" (1 of 21).
- M3, MODE_OFF path: `off_restore.async_mode_change` returns 0 instead of restoring. Red: "MODE_OFF after a write writes one 0 (the off rule)", "and while off the arm writes nothing, nor does a second off", and both MQTT checks above (4 of 21).
- M4, unload path: the `off_restore.async_restore` call removed from `async_unload_entry`. Red: "unload after a write writes one 0, through async_unload_entry (the off rule)" and "MODE_OFF and unload leave displace 0 standing on both ECL110 topics, retain on and off" (2 of 21).
- M5 and M6, the `sent = False` in `publish_ecl110_topics`'s `/set` and legacy `except` arms, each deleted: FAIL "a topic refusing the neutral leaves the MQTT arm armed and counts no restore" (1 of 22).
- M7, the `raise RuntimeError(...)` in `_mqtt_restorer`'s writer replaced by `pass`: the same check, FAIL (1 of 22).
- M8, `_mqtt_restorer`'s `if not set_topic and not command_topic: return None` deleted: FAIL "an MQTT arm whose topics were cleared is disarmed unwritten, no restore counted"; FAIL "unload after a write writes one 0, through async_unload_entry (the off rule)" (2 of 23).
- M9, that guard's `and` turned to `or`: FAIL "an MQTT arm never published is not restored; one published is restored once, not per off" (1 of 23).
- M10, `return off_restore.Restorer(...)` replaced by `return None`: 3 of 23 FAIL, the MQTT standing check among them.
- M11, `publish_ecl110_topics`'s final `return sent` (now line 266) replaced by `return None`: FAIL "an MQTT arm never published is not restored; one published is restored once, not per off" (1 of 23). That check now also asserts the restore was counted and disarmed. The earlier form of the check let M11 survive (`ALL 22 FEATURES BLOCK PASSED`), because the neutral is published before the return value is read.
- M12, the action's default in `async_publish_current_action` (`action.get("heat_pump_on", False)`) swapped to `True`: FAIL "the legacy payload's heat_pump_on is the switch's write, inside its step and a step late; no write and no key: off" (1 of 25).
- M13, the neutral body's `heat_pump_on` `True` swapped to `False`: FAIL "the legacy neutral body releases supply: heat_pump_on true, displace 0, reason off_restore" (1 of 25).
- M14, `return sent` replaced by `return False`: FAIL "publish_ecl110_topics with no topic configured publishes nothing and reports success"; FAIL "an MQTT arm never published is not restored; one published is restored once, not per off" (2 of 25).
- M12 to M14 are prepr step 6d's survivors at `04198c0ff2`. The fourth survivor was `publish_ecl110_topics`'s early `return True` with no topic configured. That return is deleted rather than pinned: with no topic both arms are skipped and the function already returns `True`.
- Disclosed self-correction: one intermediate run read the unmutated tree red on that check. It was a stale `heat_curve` bytecode cache: the M11 mutant is the same size as the original line and was restored within the same second. M10, M11 and the clean control were re-run with `python3 -B` and `PYTHONDONTWRITEBYTECODE=1` after deleting the cached `.pyc`. Clean: `ALL 23 FEATURES BLOCK PASSED`.

## Null control

At the merge base the same block fails the three new checks and passes the rest (`3 of 21 FEATURES BLOCK FAILED`). MQTT standing after off/unload was `(-3, retain)` on both topics. The never-published arm's off published nothing at the base, as it does at the head. The late cycle's legacy `heat_pump_on` was `[False]` against a switch of `[True]`. The entity arm reads 0 after off and unload at both ends, and is unchanged by this diff.

## Figures

<!-- figure-block: scope-line mb=fc2a7edcf2be8847037d9e8dc5bde460977befa8 head=e43f976d22648a95b4c41966a63cc890b2c6c32c -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- MQTT standing value after MODE_OFF/unload, retain on and off, entity arm as null control: `python3 tools/audit/seat/features_block.py --through '# A crash: the write was armed'`, check "MODE_OFF and unload leave displace 0 standing on both ECL110 topics, retain on and off". Its failure detail prints the per-path standing map. At the base it read `-3` on both topics on all four paths; at the head every path reads `{ecl/set: (0, retain), ecl/cmd: (0, retain), entity: 0}`.
- Carry 2 control: the same command, check "the legacy payload's heat_pump_on is the switch's write, inside its step and a step late". Base: `inside=([False], [False]) late=([True], [False])`. Head: passes.
- Structure: `python3 tests/structure.py`, every row ok at the head. The first cut read `max_class_loc` and `class_excess_loc` +4, from the coordinator docstring. That was paid by collapsing the docstring to one line, not by re-recording.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`, `MODE: SCOPED`. Every script it selected passed except `tests/features.py`. That failure was three test doubles of `async_publish_current_action` (`_raise_publish` in `tests/entities.py`, `_rec_plan` and `_g_rec` in `tests/features.py`) not taking the new keyword; they now take it. After that, `PYTHONPATH=tests/hastub python3 tests/features.py` passed (`ALL 5307 FEATURE CHECKS PASSED` at `7a688b2c71`; the section's later edits re-run by block above). `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` exited 0 at `7a688b2c71`; its only change to `tests/closures.json` was the recorded `rc`, not kept. At `d48cfceee7`, prepr's closure recording of `tests/entities.py` exited 1 on the two ledger pins of the deleted early return. With them removed, `PYTHONPATH=tests/hastub python3 tests/entities.py` reads `ALL 2709 ENTITY CHECKS PASSED` at the head.

## Unpinned sites

Step 6d's list at an earlier head had five sites. The fifth, `heat_curve.py:286 GUARD_OFF`, was the redundant topic guard in `publish`; it is deleted (see above), so no site is owed for it. Each remaining site is killed by a value check in the R10-GENERIC-HEAT-CURVE section of `tests/features.py`, proven above. Disposition for each: pinned by `mutation-autofix` once CI's mutation lane kills it.
- `custom_components/heatpump_optimizer/heat_curve.py:167 BOOLOP`: value check "an MQTT arm never published is not restored; one published is restored once, not per off" (M9). Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/heat_curve.py:167 GUARD_OFF`: value check "an MQTT arm whose topics were cleared is disarmed unwritten, no restore counted" (M8). Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/heat_curve.py:177 RETURN_DEL`: value check "MODE_OFF and unload leave displace 0 standing on both ECL110 topics, retain on and off" (M10). Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/heat_curve.py:266 RETURN_DEL`: value check "an MQTT arm never published is not restored; one published is restored once, not per off" (M11). Pinned by `mutation-autofix`.

## Architecture score

`Architecture score: dS +0.0000 NULL` (command above). No new module: the MQTT arm's restorer sits in `heat_curve.py` beside the entity arm's, and `off_restore.py` stays the one owner of off and unload.

## Red checks

- `tests / mutation`: red at the head as predicted by `tools/pr/ci_predict.py`, on the four ADDED UNPINNED sites `heat_curve.py:167 BOOLOP`, `:167 GUARD_OFF`, `:177 RETURN_DEL` and `:266 RETURN_DEL`. Each is killed by a value check (M8 to M11, `## Unpinned sites`), and the lane's repair is mutation-autofix's pin commit (`ci-autofix.md`). Cheaper detector: none to build. `tools/pr/prepr.sh` step 6d is already the cheaper, earlier detector of this red: it ran locally before the handoff, named each site, and costs nothing more per run than it already does. The red is the lane's designed handoff to the autofix, not an escape. The two stale ledger pins the same prediction named (`publish_ecl110_topics` BOOLOP/GUARD_OFF `8b6644d6`, on the early return this diff deletes) are removed in this diff.

## Forward-carry

- Carry 0 and Carry 1, site (1) (item 30ec8edf): the displace `async_publish_current_action` publishes stays the action's, cut at the solve. The plan carries no per-step displace, and re-deriving one per step would duplicate the optimizer's displace guard chain outside its owner. Carry: dismissed: no per-step displace exists in the plan for a late cycle to agree with; the displace is a curve offset owned by the solve, not the switch command `cycle_supply` re-derives.
- Carry 0 and Carry 1, site (2) (item 30ec8edf): built in this PR (`_apply_action` -> `async_publish_current_action(heat_pump_on=on)`). Carry: dismissed: closed in this diff.
- ghcp-r3's stale line anchors (`coordinator.py` 6484/6491/6555/7670, `entry_config.py:289` at `e066a630`) are a record of a merged design note and stay as written. The symbols they name hold at origin/main. Carry: dismissed: a measurement record recounts, it is not re-anchored.

## Friction

none
