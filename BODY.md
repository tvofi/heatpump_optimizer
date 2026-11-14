R10-USER-DOCS-VERIFY (savings-valuation delta): the short later pass that #3568 and #3582 both promised for savings-valuation residue parts 3 and 4. Part 3 is #3588 (merge 5cd7b87413, the combi hot-water `dhw_split` attribute), part 4 is #3587 (merge 931970141c, the thermostat reference behind a throttling valve). Every verdict rests on executable code at origin/main d7004eaa77, never a comment, docstring or PR body. This pull request leaves #3139 open.

Carries: R10-USER-DOCS-VERIFY carry 17 (the late delta) is built here: parts 3 and 4 of savings-valuation residue are now read. R10-ARCH-DOCS-DELTA carries 0 and 1 (the "after the last product merge" re-read of docs/architecture.md) now include #3587 and #3588: this pull request re-reads docs/architecture.md against both and changes one sentence.

Product diffs read: `git diff 5cd7b87413^1 5cd7b87413 -- custom_components README.md docs` and `git diff 931970141c^1 931970141c -- custom_components README.md docs`.

What they change for a user:
- #3588: a combi-tank install (`ThermalParameters.combi_tank_active`, thermal_model.py:317, true only with the option on, hot water on, a store buffer and no wood coil) gets a `dhw_split` text attribute on DHW Heating Cost (next 24 h) (sensor.py `DHWHeatingCostSensor.extra_state_attributes`), DHW Cost (lifetime) and DHW Energy (lifetime) (`_AccumulatingSensor.extra_state_attributes`, only for the `dhw` ledger line) and on the climate entity (climate.py, beside `dhw_heating_cost`). Built by `entity.dhw_split_attributes` (entity.py:386-392); nothing on any other install. The attribute is unrecorded.
- #3587: only the savings reference's held state: on a two-zone house behind a throttling valve whose curve cannot deliver the held need, the reference now rests at the plant's valve-top equilibrium (`optimizer._held_at_valve_top`, `thermal_model.valve_top_equilibrium`) instead of a level-zone bisection; no entity, attribute, option or wording changes.

Re-read at origin/main, whole sections, in README.md, docs/setup.md, docs/configuration.md, docs/how-it-works.md, docs/automations.md, docs/dashboard-card.md, docs/ecl110.md and docs/architecture.md. Enumerator: grep -n -i over each of those for `dhw_split`, `combi`, `split_method`, `dhw_heating_cost`, `DHW Heating Cost`, `DHW Energy`, `DHW Cost`, `hot-water mode`, `thermostat`, `baseline`, `reference`, `held`, `unreachable`, `valve top`, `ceiling`, `steady`, `floors`, `savings`, `optimizer.py`, `thermal_model.py`, `entity.py`, `climate.py`, `attribute`; then read README sensor tables (savings, accumulators, the disabled-by-default hot-water list, the climate paragraph), configuration.md's combi row and buffer rows, how-it-works.md's savings reference and wood-tank paragraphs and the price-tile paragraph, dashboard-card.md's savings section and what-if section, and architecture.md's module list and "one owner per duplicated shape" list.

| File | Verdict |
|---|---|
| README.md | none stale. The three rows #3588 changed (lines 594, 598, 624) say the attribute appears "on a combi tank" and what it says; both agree with `combi_tank_active` and `COMBI_DHW_SPLIT` (entity.py:377-380). The climate paragraph ("hot-water status ... ride in its attributes") stays true. The Plan Predicted Savings row ("simulated conventional thermostat ... no wood") stays true after #3587. |
| docs/setup.md | none stale. No mention of the split or of how the reference is held. |
| docs/configuration.md | one sentence changed. The combi row ended "Each says so in its `dhw_split` attribute." The climate entity publishes it too (climate.py, `attrs.update(dhw_split_attributes(...))` beside `dhw_heating_cost`), so it now ends "...and so does the climate entity." The rest of the row (the three named sensors count what the pump spends in hot-water mode, space heat drawn from the tank included) matches `COMBI_DHW_SPLIT`. |
| docs/how-it-works.md | none stale. Savings-reference paragraphs (wood-free reference, meter scaling, price tiles' "steady start (the thermostat baseline's difference)") describe nothing #3587 altered: the reference is still a plain thermostat held steady; only which steady state is chosen on a valve-limited two-zone house moved. |
| docs/automations.md | none stale. The receipt event's saving fields are unchanged; no page names `dhw_split` or the reference's state. |
| docs/dashboard-card.md | none stale. Its savings and what-if sections say a thermostat is priced at the same prices; the hot-water series text (line 399) concerns the action sensor's `power_kw`, which neither PR touched. |
| docs/ecl110.md | none stale. Nothing about hot-water cost attributes or the savings reference. |
| docs/architecture.md | one sentence changed. "One payload read on the entity base" said `entity.py` owns the finite scrub, the payload-number rule and the zone set-point attributes; it now also names the combi store's `dhw_split` attribute, which sensors and the climate entity publish from one function (`dhw_split_attributes`). Module list (thermal_model.py, optimizer.py, climate.py, sensor count 62) stays true: #3587 adds functions to existing modules, #3588 adds no sensor. |
| strings.json and translations | checked only, nothing wrong: the three sensor names (strings.json lines 1960, 1963, 1966) are unchanged by the PRs and match the README rows; no string describes the split or the reference. |

No product defect found.

## Head

Code head 359e580ac4eeb7f7b18379d012c5782a06ad1b04 (`handoff/r10-user-docs-verify-sav`), on origin/main d7004eaa77. Two docs files change: docs/architecture.md and docs/configuration.md, one sentence each.

## Mutation proof

n/a: docs only; no file under custom_components/, tests/ or tools/ changes, so there is no behaviour to break and no check that could go red on a sentence. The sentences were checked by hand against the code lines cited above.

## Null control

n/a: nothing is measured. The unmodified tree's two sentences were each true of three entities and none of the climate entity (configuration.md) and silent on the third publisher (architecture.md); the corrections add exactly those.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
