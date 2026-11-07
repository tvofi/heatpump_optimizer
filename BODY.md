R10-GENERIC-HEAT-CURVE, kind `offset` (design option (a)): the heat-curve displace reaches a Home Assistant `number` entity, and the shared off/unload restore hook the two later groups reuse. Built under the owner's ruling (tvofi, #201, 2026-11-07: "Yes, it should be built. Offset kind and a later persistent kind, both in this round. Turning the optimizer off should restore the baseline, retract my 26 september ruling") and the approved design (`Design review: approve 6564b0c7f40c5c81b7d9556ed3dcda8926d91bad`, note `design.md` on `design/R10-GENERIC-HEAT-CURVE`). Outside contribution: PR 3284 by Bankaifan; the design note and probe were read as data, nothing from the fork was run. There is no finding and no issue to close: the build is the owner's ruling.

**What changed.**
- `heat_curve.py` (new) owns the displace's fan-out: the ECL110 `/set` and legacy JSON MQTT arms, moved verbatim from `coordinator.py` (`ecl110_legacy_payload`, `publish_ecl110_topics`), then an entity arm. `async_publish_ecl110_command` still forms the one integer (plan, fixed modes, boost, peak guard, curve bias) and hands it to `heat_curve.publish`; two coordinator stores (`_ecl110_displace_set_topic`, `_ecl110_retain`) are deleted for the entry config.
- Entity arm, kind `offset`: the integer as a temperature difference in the entity's own unit (K, °C or no unit as is, °F ×9/5, any other unit refused), never through the absolute set-point helpers; bounded to ±`heat_curve_offset_band_k` (default 3 K, 0.5–5 K) and the entity's range. W1 write-on-change, W2 held record with its own `HELD_GRACE_S` (90 s, reasoned in code: not the arbiter's Tuya-calibrated `ECHO_GRACE_S`, ghc-r05), W3 give-up latch, W4 `2 × 1440 / interval` guard, W6 saturation latch, T2 range-excludes-0 refusal at save and at every write by one rule (`heat_curve.range_excludes_zero`). The raw reading comes from `inputs.number_reading`, the module that owns entity reads.
- `off_restore.py` (new): the one owner of the off/unload restore. MODE_OFF (through `off_restore.async_mode_change`, called from `async_set_mode`) and `async_unload_entry` write 0 to an offset entity the optimizer wrote; `async_remove_entry` only drops the persisted record (`async_forget`), so the restore has one owner (the note's O4). While off the arm writes nothing. MQTT arms unchanged (W7; ghc-d02 is the owner's).
- Options: `heat_curve_displace_entity` (`number`, `input_number`), `heat_curve_target_kind` (`offset` only), `heat_curve_offset_band_k`; the page is "Heat curve control". `ECL110_TOPIC_SLOTS` gains the entity key. The entity is refused when it equals an entity the optimizer already writes, on every page's save and on the pre-fill save (ghc-r03). Factory reset keeps the kind beside its entity (ghc-d03).
- Docs: `docs/ecl110.md` "Without MQTT: a number entity" (T1–T3 contract, W1–W6, the off rule with the stop case, the Luxtronik SHI example with U1, U2 and ghc-r04, python-luxtronik cited at `02afea84bd5bf3ee87445de6f2a42b8029983169`), `docs/configuration.md`, `README.md`, `docs/architecture.md`.

**The restore hook's interface, which R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT call unchanged.**
- `off_restore.register_consumer(key, factory)` at import; `factory(config)` returns `off_restore.Restorer(entity_id, write, neutral=None, baseline_of=<(hass, entity_id) -> float | None>)`, or `None` when unconfigured.
- `await off_restore.async_arm(hass, entry, config, key)` before each write: the first arm captures `baseline_of(...)` for a consumer with no `neutral` and persists it per entry (store `heatpump_optimizer_<entry_id>_off_restore`), so a restart never re-captures a value the optimizer wrote (the note's O3); `False` refuses the write (no readable baseline).
- The coordinator and `__init__` call `async_mode_change`, `async_restore` and `async_forget`; a consumer never does. A restore write bypasses the consumer's own policy, is counted (`off_restore.diagnostics`), and a failure is latched and keeps the consumer armed for the next off or unload.
- Shown by the check "a stand-in second consumer registers without editing the hook: its baseline, captured before its first write, survives a restart and is what the restore writes" (tests/features.py, section R10-GENERIC-HEAT-CURVE). The arbiter's own MODE_OFF branch (`pump_arbiter._arbitrate`) is untouched here.

**Alternatives, and why each lost.** (1) Pass the coordinator to `heat_curve`/`off_restore` (the note's shape): `tools/audit/archscore` charged every function handed it (coord_footprint 2491 → 2563); keying on the config entry costs one `views` seam cross (`self.entry`) and keeps the score NULL. (2) The restore in `async_publish_current_action`: returns early on MODE_OFF and is not called on unload (verdict note). (3) A Store-free baseline in the options (the note's P1): every write of it reloads the entry (O1); the per-entry store does not. (4) Hand-rolled reads of `state.state`/`min`/`max` in `heat_curve`: a float of entity state outside `inputs.py` (entities.py P8); `inputs.number_reading` owns it. (5) Repeating entity, kind and band in the diagnostics section: they are the config section's; the heat-curve section carries numbers only.

**Write-endurance carry** (12 writes/day, Daikin 7000/yr) binds the persistent kind only and is not built here.

**Toolchain.** `bash tools/audit/seat/cloud-setup.sh` then `--check`: OK, python3 is `/opt/hpo/venv-ci/bin/python3`; numpy 2.5.4 and scipy 1.18.1, matching `tests/requirements-ci.txt`.

## Head

`98ce151cff8b29c82836af504aca20804aa038dc`: `82f313186462d987c2de3058ba79ffe42938a778` with `origin/main` at `364353e670f666be6c97a5942ffa0bea9132b5ce` merged in (fetched 2026-11-07 UTC), merge base `364353e670f666be6c97a5942ffa0bea9132b5ce`.

Where each figure was measured: the mutation proof, the gate scope, the architecture score, the structure ratchet and the suites listed under Figures at `b29ed6a36706854e204d515de128a0da59aab64d` over merge base `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76`. Since then: (1) `origin/main` at `aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98` merged in, which changes `tools/audit/seat/merge_train.py`, `tools/release/stamp.py` and a delivery row, none touched by this diff; `tests/entities.py` reads both tools files and `tests/doc_claims.py` reads `stamp.py`, so both were re-run on that merge: ALL 2645 and ALL 296 PASSED. (2) `82f31318`, a rename of off_restore's private per-entry table (`_HELD` to `_RECORDS`), after which `PYTHONPATH=tests/hastub python3 tests/features.py` ALL 4927 PASSED, `tests/entities.py` ALL 2645 PASSED and `tests/finite_boundary.py` ALL 110 PASSED. (3) `origin/main` at `364353e670f666be6c97a5942ffa0bea9132b5ce` merged in, which adds only `tests/mutation_ledger/killed_by/` pin files outside this diff and read by no closure in `tests/closures.json`. `tools/pr/prepr.sh`, the body check included, ran clean on `98ce151cff8b`.

## Mutation proof

Each mutant is one named production edit at the head, applied, run, restored. The driver ran the `R10-GENERIC-HEAT-CURVE` section of `tests/features.py`, cut verbatim at the head, through a scratch runner (the section alone, 22 checks); the same edit under `PYTHONPATH=tests/hastub python3 tests/features.py` reproduces it. The failing check names, as printed:

```
BASELINE (unmutated b29ed6a3): 22 ok, 0 failing, rc=0

M1 entity arm call deleted (heat_curve.publish): rc=15, 15 failing
    FAIL no topic and an offset entity: one publish of 5 sends one set_value of 5 (R10-GENERIC-HEAT-CURVE)
    FAIL both configured: MQTT first with the full integer, the entity bounded by the 3 K default band
    FAIL a kelvin entity is sent -2 for -2, never 271.15 through the absolute helpers (T1)
    FAIL a Fahrenheit entity is sent the difference x9/5: 2 K is 3.6 °F (T1)
    FAIL an entity range narrower than the displace saturates and is latched once, naming it (W6)
    FAIL inside the grace a differing reading proves nothing: no second write (W2)
    FAIL after the grace the first miss is written once more (W2)
    FAIL a second miss for the same target latches a warning and sends nothing (W3)
    FAIL and a new target is written again (W3)
    FAIL at the guard nothing is written and it is latched; one below it the write goes (W4)
    FAIL absent, unavailable, a non-temperature unit, a sensor, a range without 0 or a raising service: no value lands, the failure is latched, the MQTT a
    FAIL MODE_OFF after a write writes one 0 (the off rule)
    FAIL and while off the arm writes nothing, nor does a second off
    FAIL unload after a write writes one 0, through async_unload_entry (the off rule)
    FAIL a write left armed by a crash is restored by the next run's first off

M2 the off-rule mode hook's call deleted (coordinator.async_set_mode): rc=3, 3 failing
    FAIL MODE_OFF after a write writes one 0 (the off rule)
    FAIL and while off the arm writes nothing, nor does a second off
    FAIL a write left armed by a crash is restored by the next run's first off

M2b off-transition predicate negated (off_restore.async_mode_change): rc=2, 2 failing
    FAIL MODE_OFF after a write writes one 0 (the off rule)
    FAIL a write left armed by a crash is restored by the next run's first off

M3 unload restore deleted (__init__.async_unload_entry): rc=1, 1 failing
    FAIL unload after a write writes one 0, through async_unload_entry (the off rule)

M4 W1 predicate negated (heat_curve._decide): rc=16, 16 failing
    FAIL no topic and an offset entity: one publish of 5 sends one set_value of 5 (R10-GENERIC-HEAT-CURVE)
    FAIL both configured: MQTT first with the full integer, the entity bounded by the 3 K default band
    FAIL a kelvin entity is sent -2 for -2, never 271.15 through the absolute helpers (T1)
    FAIL a Fahrenheit entity is sent the difference x9/5: 2 K is 3.6 °F (T1)
    FAIL an entity range narrower than the displace saturates and is latched once, naming it (W6)
    FAIL a reading already at the target is not written (W1)
    FAIL inside the grace a differing reading proves nothing: no second write (W2)
    FAIL after the grace the first miss is written once more (W2)
    FAIL a second miss for the same target latches a warning and sends nothing (W3)
    FAIL and a new target is written again (W3)
    FAIL at the guard nothing is written and it is latched; one below it the write goes (W4)
    FAIL absent, unavailable, a non-temperature unit, a sensor, a range without 0 or a raising service: no value lands, the failure is latched, the MQTT a
    FAIL MODE_OFF after a write writes one 0 (the off rule)
    FAIL and while off the arm writes nothing, nor does a second off
    FAIL unload after a write writes one 0, through async_unload_entry (the off rule)
    FAIL a write left armed by a crash is restored by the next run's first off

M5 persisted armed set not loaded (off_restore._armed_record): rc=2, 2 failing
    FAIL a write left armed by a crash is restored by the next run's first off
    FAIL a stand-in second consumer registers without editing the hook: its baseline, captured before its first write, survives a restart and is what the 

M6 unit factor ignored (heat_curve.offset_target): rc=1, 1 failing
    FAIL a Fahrenheit entity is sent the difference x9/5: 2 K is 3.6 °F (T1)

M7 band clamp dropped (heat_curve.offset_target): rc=1, 1 failing
    FAIL both configured: MQTT first with the full integer, the entity bounded by the 3 K default band

M8 W3 give-up off (heat_curve._decide): rc=2, 2 failing
    FAIL a second miss for the same target latches a warning and sends nothing (W3)
    FAIL and a new target is written again (W3)

M9 T2 range rule off (heat_curve.range_excludes_zero): rc=1, 1 failing
    FAIL absent, unavailable, a non-temperature unit, a sensor, a range without 0 or a raising service: no value lands, the failure is latched, the MQTT a

M10 W2 grace check off (heat_curve._decide): rc=2, 2 failing
    FAIL inside the grace a differing reading proves nothing: no second write (W2)
    FAIL a second miss for the same target latches a warning and sends nothing (W3)

restored clean: True
```

M1 is also the base's behaviour: at `4b5d771b` the publish is MQTT-only, so the first check (one `set_value` of 5 with no topic) is red there by construction; no entity option exists at the base.

## Null control

The entity option empty, the same publish: no `set_value` call and the `/set` topic carries `5` exactly as before (check "the entity option empty: no set_value, and the /set topic still carries the integer (W7)"). An unconfigured install switched off writes nothing, and one that never wrote is not restored (check "nothing written, nothing restored; an unconfigured entity is never written"). The moved MQTT helpers keep their #193 checks unchanged except for the import (tests/features.py, section "#193 S3"). Goldens: none move and no claim file is touched (prepr step "claim files: byte-identical to origin/main").

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL PASSED at the head; the section's own count is the 22 checks above.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`, `tests/config_flow_steps.py`, `tests/finite_boundary.py`, `tests/debug_collect.py`, `tests/doc_claims.py`, `tests/harness_headers.py`, `tests/manual_plan.py`, `tests/typing_ruler.py`, `tests/guard_pins.py`, `tests/deployment_shape.py`, `tests/arch_score_head.py`, `node tests/card.mjs`, `node tests/card_drift.mjs`: each ALL PASSED at the head (each script's own summary line). Null control for "each": every one of these failed at least once on this branch before its repair (the repairs are the commits named in Red checks).
- `python3 tools/audit/archscore/score.py --diff origin/main`: NULL (no metric moves). The rule: the gate refuses any SCORE metric or tripwire rise. Its null control on this branch: the coordinator-passing shape read WORSENS (coord_footprint 2491 -> 2563, layer_violations 13 -> 14), repaired in the commit "keyed on the config entry".
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: PASSED; against `origin/main`'s budgets every row moved is down (class_excess_loc 17585 -> 17580, max_class_loc 7955 -> 7949, coordinator_attrs 141 -> 139, seam_cut_total 423 -> 421). The 420 -> 421 re-record against this branch's own earlier record carries its `--allow-regression` reason in its commit message.
- Closures: the 22 scripts recorded are those whose committed closure at the merge base lists `coordinator.py` (`python3 -c "import json; d=json.load(open('tests/closures.json'))['closures']; print([s for s,v in d.items() if 'custom_components/heatpump_optimizer/coordinator.py' in v])"`), by `tests/derive_closures.sh --scripts-from` on Linux, merged with `tests/closure.py merge --partial --allow-failures` because `tests/entities.py` exited 1 only on the three checks that read the unmerged file; after the merge it passes. Each of the 22 now lists both new modules.
- Unpinned sites: the count is `tools/pr/ci_predict.py --base origin/main`'s ADDED UNPINNED lines at the head; every key is below.
- Toolchain: numpy 2.5.4, scipy 1.18.1 (`python3 -c "import numpy,scipy;print(numpy.__version__,scipy.__version__)"`), equal to `tests/requirements-ci.txt`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main`: dS +0.0000 NULL; no metric rises, so no line per metric is owed. `off_restore` imports `homeassistant.core.HomeAssistant` for the type of the `hass` it writes through and the store it persists to: it is a glue module, and the layering metric's pair (`off_restore (0 -> 2)`) was that module reaching the glue through `store.py` while claiming to be pure.

## Red checks

Checks this branch turned red locally before the handoff, each repaired in a commit of this branch; each named so the trigger is recorded, not analysed:
- `tests/features.py` factory-reset census and the P6 commandable-slot census (a new kept key and a new written slot): the census is itself the cheapest detector; it ran.
- `tests/entities.py` architecture.md counts, the module map, the HA boundary, P8 (float of entity state outside inputs.py), the N-log-flood list, the InputReader key census, the tracked-file classification and the deployment-shape note: each is its own detector, run by the scoped gate.
- `tests/finite_boundary.py` (a new store needs a loader, a seed and a declared domain), `tests/debug_collect.py` (a new diagnostics section), `tests/doc_claims.py` (history phrases, the bare-ConfigEntry census), `tests/harness_headers.py` (D5/D6 RESULT headers), `node tests/card.mjs` (Health label for a new entity field), `tests/typing_ruler.py` (five strict errors), `tests/manual_plan.py` (an unload stub without `effective_config`), `tests/structure.py` (class_excess_loc +14 before the T2 check left the options-flow class).
- `tools/pr/prepr.sh` REFUSE `ci predict` (two STALE PINs) and REFUSE `no-copies` (`off_restore._held` against `tests/dst_checks.py`'s `_held`): repaired by deleting the two stale pin files by hand, as ci_predict directs, and renaming to `_armed_record`.
- `mutation`: predicted red on the unpinned sites this diff adds (the list under `## Unpinned sites`). The cheaper detector exists and ran: prepr step 6d and `tools/pr/ci_predict.py` list every site before the handoff; per `ci-autofix.md` the `mutation-autofix` job pins them once the pull request exists, and the mutation proof above already kills most of them. No cheaper detector is missing.
`UNDER-SCOPED` and `INHERITED CLAIMS`: none predicted (`ci_predict`: "no closures, fast, governance or instrument red predicted").

## Forward-carry

- The hook's interface (this body's "restore hook" list) changes how R10-ARBITER-OFF-RESTORE and R10-GENERIC-HEAT-CURVE-PERSISTENT must work: register a consumer and arm before the first write, never a second owner of the unload, MODE_OFF or remove path. Lands in those two groups' entries in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ARBITER-OFF-RESTORE. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.
- For the persistent kind: the baseline is persisted per entry by `async_arm`, which answers the note's O3 (a crash's displaced value is never re-captured) and O4 (one owner); O1 does not arise, because the baseline is not in the options. O2 (budget and dwell across reloads) and O5's endurance numbers (12/day, 7000/yr) stay that group's, in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.
- ghc-d02, `decision: owner`: whether the MQTT ECL110 arms also publish displace 0 on MODE_OFF and unload. Not built: W7 keeps MQTT byte-identical. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT.

## Roster carries

- Carry 1 (the contributor trailer): the body ends with `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>`, and so does the first commit of the branch (`ad975093f`).
- Carry 2 (the band default from the web-research probe): `const.py` `DEFAULT_HEAT_CURVE_OFFSET_BAND_K = 3.0` and `HEAT_CURVE_OFFSET_BAND_RANGE_K = (0.5, 5.0)`, the comment citing handoff-body/r10-ghc-research 52f5a442, BODY.md, its "Recommended defaults" row O5a; the options field is 0.5–5 in 0.5 steps; `docs/ecl110.md` states the 5 K ceiling as *[documented, a third-party app's docs]* and the 3 K default as an *[estimate]*. The write-endurance limits bind the persistent kind only and are not built here (Forward-carry).
- Carry 3 (the owner's "Arbiter too"): the MODE_OFF and unload restore is one hook, `off_restore`, with the interface named above; the arbiter group registers a consumer and arms it, and the two restores share `async_mode_change`, `async_restore` and `async_forget`. A stand-in second consumer registers with no edit to the hook (the check named above). The arbiter's behaviour is untouched here, as the brief's SCOPE requires.

## Design carries

ghc-03 and ghc-04 stay as the note disposed of them (a D6 and a D5 round's); untouched here. The design carries, each disposed of here: ghc-d01 (off rule: MODE_OFF and unload write 0, counted, bypassing W3/W4; tests named above), ghc-d03 (kind kept in `_WIRING`; factory-reset check), ghc-d04 (stopping: written anyway, failure latched and kept armed; docs/ecl110.md), ghc-d05 (roster `after` followed), ghc-d06 (no probe file landed), ghc-d07 (W1/W2/W3 kept in one owner, `heat_curve._decide`; the valve's epsilon block and the arbiter's record are not cloned), ghc-01 (integer sent: checks read `5` and `-2` back), ghc-02 (re-pointed at `EntryConfig`), ghc-r01 (docs say the peak guard and a mode change publish without the staleness check), ghc-r02 (`log_held`), ghc-r03 (refused on every page and the pre-fill save; checks on the heat_curve and building pages), ghc-r04 (docs/ecl110.md), ghc-r05 (`HELD_GRACE_S`, reasoned in code), ghc-r06 (both modules in 22 recorded closures), ghc-r07 (commit named), ghc-r08 (an entity with no state at save is not judged; the arm re-checks the range at every write). Band default cited to its source: const.py `DEFAULT_HEAT_CURVE_OFFSET_BAND_K` names handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults" row O5a; docs/ecl110.md flags the [documented]/[estimate] tags.

## Friction

- frugal-routing: cost: the inline-search budget counted plain sed/cat/tail reads of a file already located, and a Monitor's tail, so file reads went through extra subagents. Carry: dismissed: a session plugin's guard, not this repository's policy

## Unpinned sites

Every site is under `custom_components/`, which the `mutation-autofix` lane mutates; most are already killed by the checks in the mutation proof above.
- custom_components/heatpump_optimizer/config_flow.py:2191 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2191 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2193 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2214 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2214 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2216 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:2253 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/config_flow.py:3699 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:66 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:67 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:88 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:90 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:95 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:97 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:148 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:148 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:152 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:169 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:209 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:209 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:219 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:219 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:229 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:232 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:235 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:237 CLAMP_DROP*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:239 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:240 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:241 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:242 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:243 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:248 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:248 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:248 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:250 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:251 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:251 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:253 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:254 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:254 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:257 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:257 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:262 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:262 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:277 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:279 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:281 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:294 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:294 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:297 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:300 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:306 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/heat_curve.py:310 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:635 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:43 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:48 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:98 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:100 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:104 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:109 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:128 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:131 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:134 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:142 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:159 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:175 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:186 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:188 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/off_restore.py:206 GUARD_OFF: pinned by mutation-autofix

Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>
