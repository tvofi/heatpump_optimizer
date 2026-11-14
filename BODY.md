Carry 10 (R10-SAV-VALUATION-RESIDUE, part 3): on a combi store the plan's hot-water figures now say which split they show. The carry accepts "count the store's charge as one channel" or "say which split it shows"; under the orchestrator's ruling on the predecessor's BLOCKED question (2026-11-14T10:45Z) this part delivers the second and forward-carries the first.

On an install whose `ThermalParameters.combi_tank_active` holds, DHW Heating Cost (next 24 h), DHW Energy (lifetime), DHW Cost (lifetime) and the climate entity's `dhw_heating_cost` attribute each publish a static `dhw_split` attribute: "what the heat pump spends in hot-water mode; with a combi store this includes space heat drawn from the store" (`entity.COMBI_DHW_SPLIT`, through `entity.dhw_split_attributes`). It is kept out of the recorder the same way as `split_method` (`_unrecorded_attributes` on each class). No entity is renamed, no figure moves, and strings.json and the translations are untouched. On every other install the attributes are what they were. README.md's three sensor rows and docs/configuration.md's combi-tank option say the same thing. tests/doc_claims.py pins the docs to the code's sentence, and tests/entities.py pins the attribute, its null and its unrecorded status.

Edit set: the ruling widened it by sensor.py, climate.py, README.md, the one docs page, tests/entities.py and tests/doc_claims.py. This diff also adds the helper to custom_components/heatpump_optimizer/entity.py, beside `has_hot_water`, because both platforms read it and no platform module imports another. The alternatives were the helper in sensor.py with climate.py importing a sibling platform, or the predicate copied into both, and each lost on that ground. The helper takes the thermal parameters rather than the coordinator. Handing it the coordinator charged its body to `coord_footprint` (+3, inadmissible). Passing the input it reads in is the contract's own rule, and the score reads NULL. No file on the ruling's not-editable list is touched: coordinator.py, heat_energy.py, dhw_planner.py, the exchange (`_combi_flux_exchange`) and the hot-water LP (`_plan_dhw_min_cost`).

## Head

4edd4f2d24 (merge): the merge of origin/main fafd6a9ff5 into 8341359750, with tests/doc_claims.py resolved by hand (authorised); README.md, docs/configuration.md and tests/entities.py auto-merged. Resolution: both sides had added a block at the same place after `check_stateless`, main's R10-CONFIG-FLOW-TEXT-VERIFY block (its pins re-anchored to the merged wording by main's 002bdfeafb) and this part's `check_combi_dhw_split`. The union keeps both whole, and `main()` calls both. The three Carry 10 checks still read the real text: README.md's rows, configuration.md's combi option and `entity.COMBI_DHW_SPLIT` in the merged tree, whose dhw_split lines the merge left unchanged, so none needed a new anchor. `python3 tests/doc_claims.py` passes all 390 checks. Under `mutant_run.py --in-place`, SURVIVED NULL, then KILLED for each Carry 10 perturbation: a README hot-water row loses `dhw_split`, the space row gains it, the combi option loses it, and the code sentence changes. Each fails only its own check. Main's flow pin is also KILLED ("sent again every 5 minutes" made 7 fails "every quoted figure in the flow help (19 pins)"), so the union did not hollow it out. `git diff fafd6a9ff5 HEAD --stat` names only this part's eight files.

8341359750 (code): the branch merged with origin/main at a2ef25b4b2 (PR 3574 landed), which is the merge base every figure below is taken against, at 2026-11-14T13:07:27Z. The code's own commits are unchanged by the merge: `git diff cb97628f08 8341359750` over entity.py, sensor.py, climate.py, tests/entities.py and dev/audit/harnesses/r10_combi_tank.py prints nothing.

## Mutation proof

`python3 tools/audit/seat/mutant_run.py --spec <16 named mutants> --cmd '<the Carry 10 block of tests/entities.py>'`. The command ran tests/entities.py's header (through `DATA`) and then the block from the `# R10-SAV-VALUATION-RESIDUE Carry 10` marker, the way `features_block.py` runs a features.py block. Running the whole of `PYTHONPATH=tests/hastub python3 tests/entities.py` per mutant reproduces the same kills, more slowly. `SURVIVED NULL`, then KILLED on each of:
- entity.py: `COMBI_DHW_SPLIT` text changed (entity_const_text), the combi guard `if False` (entity_guard_off), the guard without `combi_tank_active` (entity_guard_on), the `dhw_split` return deleted (entity_return_del).
- sensor.py: DHW Heating Cost's attribute property returns None (sensor_cost_attr_del), drops `or None` (sensor_cost_or_none), is handed no parameters (sensor_cost_params_none), or loses `dhw_split` from `_unrecorded_attributes` (sensor_cost_unrecorded). The accumulator's `_unrecorded_attributes` loses `dhw_split` (sensor_acc_unrecorded). The `_ledger_line == "dhw"` guard is `if False` (sensor_acc_guard_off) or `if True` (sensor_acc_guard_on, killed by the space-figure null). The update call is deleted (sensor_acc_call_del) or handed None (sensor_acc_params_none).
- climate.py: the `_unrecorded_attributes` line is emptied (climate_unrecorded), the update call is deleted (climate_call_del), or it is handed None (climate_params_none).

`mutant_run.py --diff a2ef25b4b2...HEAD` with the same command printed no `SURVIVED` line (rc 0) over the 12 mutants it draws from the added production lines (`--list`).

## Null control

- Non-combi install: the four hot-water readers and a space reader, on the issue's store with `dhw_combi_tank_enabled` off, publish byte-identical attributes at a2ef25b4b2 and at the head. This was checked by printing each `extra_state_attributes` (Home Assistant's default None standing in where a class defines none) as sorted JSON at both trees and diffing them. They are identical, and the combi rows differ only by the `dhw_split` key.
- The test's own null: "and off a combi store none states it (Carry 10 null)" passes at both base and head, and the space figure on the combi store carries no `dhw_split` at the head.
- Combi `null` row and figures: no plan, ledger or payload code is touched. `dev/audit/harnesses/r10_combi_tank.py exchange` prints identical `exchange` and `null` rows at a77d71fb75 (6ce29b69ab's harness copy), at cb97628f08 and at 8341359750 (after the merge of a2ef25b4b2) (diff of the RESULT lines less `solve_s`).
- Flat-price switch: the savings figure is not read or written by this diff, so its move under `tests/golden/flat_prices.json` is 0 by construction, and the share the channel change accounts for is 0 because no channel changes. No golden fixture moves (`GOLDEN_MODE=drift` in the scoped gate).

## Figures

<!-- figure-block: scope-line mb=fafd6a9ff58b01ea2e9462cb16dc449fdc9f63c5 head=4edd4f2d24108139bdedf2bce07841e31a4a7e63 -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

Reader census (the FIRST STEP; the orchestrator accepted the predecessor's census as measured, and these are re-taken at this head): `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py exchange`. Base and head are identical:

| row | rounds | dhw_kwh (plan, kWh_el) | published_dhw_heating_cost | tap_draw_kwh_th | worst_shortfall_c |
|---|---|---|---|---|---|
| exchange | 3 | 22.135 | 46.357 | 7.830 | -1.455 |
| null | 0 | 5.327 | 7.304 | 7.830 | 28.767 |

User-visible readers of the plan's hot-water split, by code read at a77d71fb75 (`git diff --stat a77d71fb75 a2ef25b4b2 -- custom_components/` names neither sensor.py, climate.py, the card nor dhw_planner.py; its ledger.py change is the `REFERENCE_BASIS` bump, which reads no split):
1. Card DHW kWh tile: none exists. The card's tiles are `tiles.price_now`, `tiles.planned`, `tiles.cost` and `tiles.indoor` (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js). Its DHW series is the `dhw_slots` power bars, and the receipt shows `BILLED_LINES` only.
2. DHW Heating Cost (next 24 h): the sensor and the climate attribute show the exchanged heat as hot water (46.357 against 7.304 above). It comes from `_baseline_dhw_economics` in dhw_planner.py. It now carries `dhw_split`.
3. DHW Energy (lifetime) and DHW Cost (lifetime): booked from the coordinator's planned split through heat_energy's attribution, i.e. the actuated slot's `dhw_power`. They now carry `dhw_split`.
4. Savings (`Ledger.observe_spot_and_settle_savings`): books total `actual_kwh` and `pending["power"]`, so it does not read the split.

Attribute presence, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py split_attrs` (the arm run over the head's harness copy at a77d71fb75 for the before end):
- `combi_{DHWHeatingCostSensor,DHWEnergySensor,DHWCostSensor,HeatPumpOptimizerClimate}_dhw_split` reads 1 at the head and 0 at the base.
- `combi_SpaceEnergySensor_dhw_split` and every `separate_*_dhw_split` read 0 at both.

Failing-first: tests/entities.py's Carry 10 block at the base (the head's test file over a2ef25b4b2) prints `FAIL on a combi store each hot-water figure says it is the pump's hot-water mode, space heat drawn from the store included (Carry 10)` and `FAIL the split statement is shown but never recorded (Carry 10, #1462's rule)`, with the null check `ok`. At the head all three pass. tests/doc_claims.py passes at the head with its three Carry 10 checks.

Seam census (fixer step 8): the readers that show the plan's hot-water figure to a user are enumerated by `git grep -nE '"dhw_heating_cost"|dhw_energy_kwh|"dhw_cost"' -- custom_components/heatpump_optimizer/sensor.py custom_components/heatpump_optimizer/climate.py custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`. Disposition: DHWHeatingCostSensor, DHWEnergySensor and DHWCostSensor, and the climate's `dhw_heating_cost`, are closed in this diff. The card reads none of the three keys. The monthly `this_month_kwh`/`this_month_cost` ride on the DHW accumulators and so carry the same `dhw_split`.

Structure: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.

## Architecture score

`python3 tools/audit/archscore/score.py --diff a2ef25b4b2` prints `Architecture score: dS +0.0000 NULL`.

## Red checks

- `tests / mutation` (predicted by `prepr.sh` step 6d): the five sites under `## Unpinned sites` have no `tests/mutation_ledger/killed_by` pin yet. Every one is killed by tests/entities.py's Carry 10 block (`## Mutation proof`, plus `entity_boolop_or` and `entity_return_empty_del` for the BOOLOP and `return {}` operators). The `mutation-autofix` job measures and pins killed sites in custom_components/ on the pull request, as `ci-autofix.md` assigns it. The cheaper detector already exists and fired: `prepr.sh` step 6d predicted this red locally before any CI ran, at no added standing cost. No further countermeasure is owed.

## Unpinned sites

- custom_components/heatpump_optimizer/entity.py:390 BOOLOP: pinned by mutation-autofix (killed by tests/entities.py's Carry 10 null check; measured as `entity_boolop_or`)
- custom_components/heatpump_optimizer/entity.py:390 GUARD_OFF: pinned by mutation-autofix (killed by the Carry 10 combi check; `entity_guard_off`)
- custom_components/heatpump_optimizer/entity.py:392 RETURN_DEL: pinned by mutation-autofix (killed by the Carry 10 checks, as `attrs.update(None)` raises; `entity_return_empty_del`)
- custom_components/heatpump_optimizer/sensor.py:1279 RETURN_DEL: pinned by mutation-autofix (killed by the Carry 10 combi check; `sensor_cost_attr_del`)
- custom_components/heatpump_optimizer/sensor.py:1829 GUARD_OFF: pinned by mutation-autofix (killed by the Carry 10 combi check; `sensor_acc_guard_off`)

## Forward-carry

- The one-channel recount (route (b) in the predecessor's BLOCKED question). On a combi store the three figures would count only hot water: the settled split in the coordinator's planned split and heat_energy's attribution, and the forecast in dhw_planner.py's `_baseline_dhw_economics`. It is legitimate only if the separate-tank install and the combi `null` row (zero exchange rounds) stay bitwise, and if the savings figure, which reads total power and not the split, does not move. The measurement is the census above. Re-measure with `r10_combi_tank.py exchange` at your merge base. Once the recount lands, `dhw_split`'s sentence is false and goes with it: `entity.COMBI_DHW_SPLIT` and the docs pinned by tests/doc_claims.py's `check_combi_dhw_split`. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
