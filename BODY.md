Closes #3862

The owner's switch "External Heat Block Override" (`switch.<prefix>_external_heat_ignore_block`): while on, with external-heat detection enabled, the plan is no longer held back by a detected fire, inferred or from the stove/flue entity. It lifts the DHW suppression in the solve state and the free-heat credit to the space plan; detection, the binary sensor's state and the learning freeze keep reading the raw detector. Off by default, persisted in the boost store (key written only while on), no timeout, inert with detection disabled. Diagnostics row `external_heat_block_ignore` records `switch_on` and the effective `block_ignored`; the binary sensor and the payload's `external_heat` publish `block_ignored` only while the switch is on. Built from design ee6bb4da3329dcf1ba16e6a40fd63ef80cdba289 (verdict 5d7384e5, approve), under the orchestrator's rulings of 2026-11-22T18:22Z (mandate 6893738184):

- the block rule is three module functions of `external_heat.py` over the detector (`ignore_effective`, `blocking`, `view`), not methods of `ExternalHeatDetector`, which was over the class span limit at the base: the class's span is unchanged and `class_excess_loc` falls;
- the entity name leads with the family word (en "External Heat Block Override", sv "Extern värme: åsidosätt blockering", de "Externe Wärme: Sperre übersteuern", beside "External Heat Source" / "Extern värmekälla" / "Externe Wärmequelle"), so no `ENTITY_FAMILY_OVERRIDES` entry; unique id and translation key as designed. This departs from the owner's Q9 wording, confirmed by the owner 2026-11-22 per the ruling;
- the card's `statusPill` reconciliation is not in this diff; it is carried to R11-OWNER-CARD-EXTERNAL-HEAT (below).

Alternatives not taken: methods on `ExternalHeatDetector` (the design's shape) raise `class_excess_loc` on a class already past the limit (measured +8 at 663cfb94); a one-member `ENTITY_FAMILY_OVERRIDES` family raises the archscore gate metric `family_orphan_overrides`; a `RestoreEntity` switch would be a second persistence path beside the boost store that already holds the sibling timed switches' state.

## Head

d75c04ad77236c068962405f4468990e384213e6 (merge base baa9a467ac518bc3f8733d2603ea8ae406b235af; origin/main e3cb5c019b464a770cc7c6fe2fbc858ed29debf7 at 2026-11-22T21:43Z).

## Mutation proof

`python3 tools/audit/seat/features_block.py --prelude 'exec(open("x62_prelude.py").read())' "# --- #3862: the owner's switch" "# --- #1955 planner power"` (prelude from `--emit-prelude` on the same tree), one production line mutated per run, then restored:

- M1 `blocking`: `and not ignore_effective(...)` -> `and ignore_effective(...)`: 5 fail — "an active or fading fire blocks with the switch off, and not with it on (#3862)", "null: an entity-reported fire blocks with the switch off (#3862)", "the switch lifts an entity-reported fire's block, and the fire stays detected from the entity (#3862)", "null: with the switch off a fire credits the space plan with free heat (#3862)", "with the switch on the space plan gets no free-heat credit (#3862)".
- M2 `ignore_effective`: drop `and detector.config.enabled`: 3 fail — "with detection disabled the switch is not effective and publishes block_ignored false (#3862)", "null: with detection disabled the switch on leaves the cached burn in the solve (#3862)", "diagnostics report the switch on and, with detection disabled, not effective (#3862)".
- M3 `view`: publish the key with the switch off: 2 fail — "null: with detection enabled the switch is effective, and off publishes no key (#3862)", "null: an entity-reported fire blocks with the switch off (#3862)".
- M4 `ExternalHeatState.as_dict`: `if block_ignored is not None` -> `if True`: 3 fail.
- M5 coordinator forecast gate back to `self._external_heat.suppressing`: 1 fail — "with the switch on the space plan gets no free-heat credit (#3862)".
- M6 coordinator solve state: the switch term made inert (`and not extheat.ignore_effective(` -> `or 0*extheat.ignore_effective(`): 3 fail — "the cached burn reaches the solve with the switch off, and the switch lifts it (#3862)", "with the switch on the fire's hot-water plan equals the no-fire plan slot for slot (#3862)", "the switch lifts an entity-reported fire's block, and the fire stays detected from the entity (#3862)".
- M7 `boost._store_payload`: write the key with the switch off: 2 fail — "the boost store carries the switch only while it is on (#3862)", "turning the switch off waits for the restore, then wins over the stored on (#3862)".
- M8 `boost.restore`: delete the adopt line: 1 fail — "a stored true restores the switch on; stored false or absent restores it off (#3862)".

RC2 durability block (`features_block.py` from "# RC2 (round 9): the class behind" to "# F1.4 (round 9) extends the RC2 block", prelude by `--emit-prelude`), whose census refused the switch's actions until they were rows:

- R1 `boost.restore`: delete the adopt line: 1 fail — "every entity action's state survives a restart before any cycle completes" (`ExternalHeatIgnoreBlockSwitch.async_turn_on(): False != True`).
- R2 `ExternalHeatIgnoreBlockSwitch.async_turn_on` awaiting the refresh (measured at 56de786f, before the setter's refresh arm was deleted): 1 fail — "every entity action returns before the solve it asks for completes".

Unmutated, the same command prints `ALL 20 FEATURES BLOCK PASSED`. Failing first: the head's tests/features.py run by the same command over the base's production tree (baa9a467) stops at the block's first check with `AttributeError: module 'heatpump_optimizer.external_heat' has no attribute 'blocking'`.

## Null control

Every #3862 check has its switch-off or detection-off twin in the same block. Harness: `dev/audit/harnesses/solve_inputs_parity.py` (sha1 e77213759f4b2c2d685d9ade3ec43b7e7b717b56, unchanged base to head) prints byte-identical output at baa9a467 and at this head (`cmp` exit 0), switch off. It measures what this fix leaves alone and reads flat under its own perturbation too: with the solve line forced to `external_heat_active=True` its output is still identical, so it does not observe the term. The companion reading the term is features check "the cached burn reaches the solve with the switch off, and the switch lifts it (#3862)" (M6 kills it).

The hot-water checks (design item 3) run with the stub clock frozen at 2026-11-22T19:30Z (`_X62_AT`): the suppression only removes discretionary slots in the first two hours and the solve fixture anchors its prices on the clock, so unpinned the switch-off null passed or failed by the hour. Control: the same block with `_X62_AT` at 21:30Z fails "null: with the switch off a fire suppresses discretionary hot water (#3862)" (`fire 16.694 kW-steps, no fire 16.694`), as the unpinned block did when run live at 21:xx UTC; at 19:30Z all 20 pass.

## Figures

- Mutation: 8 mutants over the #3862 block, 8 killed, plus 2 over the RC2 durability block, 2 killed; commands under `## Mutation proof`.
- `python3 tests/structure.py`: `class_excess_loc`, `max_class_loc`, `module_excess_loc` read lower than the base's budget and are re-recorded in this branch (`--record`, rows named in the commit); no row fails.
- `python3 tools/audit/archscore/score.py --diff baa9a467ac518bc3f8733d2603ea8ae406b235af`: `Architecture score: dS -0.0017 WORSENS (inadmissible: coord_footprint 2525->2528)`; `shape_copies` 38 -> 37 (the shared `_KeyedSwitch` base)
- Scoped gate: `GATE_SCOPE=auto GATE_SCOPE_BASE=baa9a467ac518bc3f8733d2603ea8ae406b235af GOLDEN_MODE=drift bash tests/run.sh`: `MODE: SCOPED`; every script it names passed (features.py `ALL 6048 FEATURE CHECKS PASSED` re-run alone at this head after the clock pin and the rename; the run itself at 5576fd96, its scripts after features.py, cut off by the session's 30-minute background limit and run one by one with the same environment, each exit 0, `harness_headers.py` `ALL 115 HARNESS HEADER CHECKS PASSED`), `stress.py` exit 0 (`ALL 122 STRESS CHECKS PASSED`). At 3c003f43 the same run's reds were features.py's RC2 census (fixed by the two rows), doc_claims (a README bare-relative link and a history phrase in how-it-works; fixed), structure (three improved rows unrecorded; recorded), harness_headers (the round-4 D6 claims harness hard-coded the README's six switches, so C14 read false and its committed output moved; its literal now names the README's seventh row and its output is regenerated: `claims_true` 123, `claims_false` 0, as its header states) and stress.py (exit at 0 s while a second harness_headers run held the machine lease; re-run alone, the exit 0 above)
- `python3 tests/closure.py select --diff baa9a467ac518bc3f8733d2603ea8ae406b235af`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`

## Architecture score

- `coord_footprint` rises by the switch's own state handling, which counts because both functions take the coordinator: `boost.extheat_block_ignored` (one statement) and `boost.set_extheat_block_ignored` (three: await the restore gate, set, persist), the same shape as the sibling timed switches' setters in `boost.py`. Paid: the setter's never-taken refresh arm deleted and the solve site's one-use local inlined (+5 at 663cfb94, +3 here); the rule itself lives in `external_heat.py`, so the coordinator's three call sites only pass the held switch to it.

## Unpinned sites

Each site the ci_predict step lists, with the ledger's own operator (`tests/mutation_table.py` `candidates`) applied at this head and the check that kills it; pinned by `mutation-autofix` after the push. The four `_decay` sites replace the four `killed_by` pins this branch deleted (their lines merged), killed by the same file, tests/features.py.

- `custom_components/heatpump_optimizer/boost.py:351 RETURN_DEL`: the #3862 block: 8 fail, among them "the cached burn reaches the solve with the switch off, and the switch lifts it (#3862)".
- `custom_components/heatpump_optimizer/boost.py:577 GUARD_OFF`: the #3862 block: "the boost store carries the switch only while it is on (#3862)".
- `custom_components/heatpump_optimizer/coordinator.py:5219 GUARD_OFF`: the #3862 block: "with the switch on the space plan gets no free-heat credit (#3862)".
- `custom_components/heatpump_optimizer/external_heat.py:174 GUARD_OFF`: the #3862 block: raises `KeyError: 'block_ignored'` (rc 1).
- `custom_components/heatpump_optimizer/external_heat.py:176 RETURN_DEL`: the #3862 block: raises `TypeError: 'NoneType' object is not subscriptable` (rc 1).
- `custom_components/heatpump_optimizer/external_heat.py:466 BOOLOP`: the item-28 wood block (`features_block.py` from `R.section("Wood furnace displacement (item 28)")` to `R.section("Unknown price horizon (item 7)")`): raises `TypeError` on `None <= float` (rc 1).
- `custom_components/heatpump_optimizer/external_heat.py:466 CMP_BOUND`: the item-28 wood block (`features_block.py` from `R.section("Wood furnace displacement (item 28)")` to `R.section("Unknown price horizon (item 7)")`): "a measurably spent wood tank ends the decay early".
- `custom_components/heatpump_optimizer/external_heat.py:467 CMP_BOUND`: the item-28 wood block (`features_block.py` from `R.section("Wood furnace displacement (item 28)")` to `R.section("Unknown price horizon (item 7)")`): "a measurably spent wood tank ends the decay early".
- `custom_components/heatpump_optimizer/external_heat.py:467 GUARD_OFF`: the item-28 wood block (`features_block.py` from `R.section("Wood furnace displacement (item 28)")` to `R.section("Unknown price horizon (item 7)")`): raises `AttributeError` on `None.tzinfo` (rc 1).
- `custom_components/heatpump_optimizer/external_heat.py:505 BOOLOP`: the #3862 block: 8 fail, among them "an active or fading fire blocks with the switch off, and not with it on (#3862)".
- `custom_components/heatpump_optimizer/external_heat.py:505 RETURN_DEL`: the #3862 block: 7 fail, among them "with detection disabled the switch is not effective and publishes block_ignored false (#3862)".
- `custom_components/heatpump_optimizer/external_heat.py:510 BOOLOP`: the #3862 block: 4 fail, among them "null: a quiet detector blocks neither way (#3862)".
- `custom_components/heatpump_optimizer/external_heat.py:510 RETURN_DEL`: the #3862 block: 5 fail, among them "an active or fading fire blocks with the switch off, and not with it on (#3862)".
- `custom_components/heatpump_optimizer/switch.py:253 RETURN_DEL`: tests/entities.py (the #3862 block does not reach the attribute): "the external-heat override switch is off and not effective on a fresh coordinator (#3862)" and "ExternalHeatIgnoreBlockSwitch publishes exactly its pinned attribute keys (#373)".

## Red checks

- `mutation` at d75c04ad7723: red by construction on the 14 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. No cheaper detector is owed: prepr's ci_predict step already predicts the red locally, and each site's kill is measured above.

## Forward-carry

- The card's `statusPill` external-heat branch must also test `attributes.block_ignored !== true` on the twin binary sensor, with the mutation target "drop the `block_ignored` test, a tests/card.mjs case with the switch effective fails" and this group's switch-off case as the null; this PR publishes `block_ignored` in `binary_sensor.<prefix>_external_heat_source`'s attributes as its input. Landed in the group's `carry` on dev/programme/rosters/wave-r11-groups.json at handoff/audit-r11-roster (58e94013). Carry: R11-OWNER-CARD-EXTERNAL-HEAT

## Friction

none
