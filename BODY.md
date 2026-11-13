R10-SAV-VALUATION-RESIDUE, part 2 (the pending carries: 4, 9, 10, 14, 15). Behind a valve, `_compute_baseline_power` booked the simulated reference and then re-spread the horizon's energy by steady demand (`_apportion_by_steady_demand`). The method's premise was that "the first steps are the stores' transient". Since part 1, the held state's census (`dev/audit/harnesses/r10_sav_held_capacity_census.py`) reads a first-step store change of 0 on every case, so step 0 from the held state is the thermostat's holding power. The re-spread became the residual's own source: it booked step 0 above the held equilibrium, +11.11 kWh_th over the valve arm (Carry 15). This diff removes the call and the method, and books the reference as simulated.

Alternatives and why each lost:
- (a) Keep the spread and anchor step 0 to the simulated step. That keeps a second power schedule the settlement does not need: the census shows the simulated schedule already starts at equilibrium. It also keeps 26 lines and their pins for no booked effect.
- (b) Cap the spread at the simulated step's power. It still re-shapes steps 1..n by a steady demand the simulation does not follow, so the reference would book heat its own trajectory never drew.

The brief's carries:
- Carry 4 (the attribution and its fix): part 1 fixed the held state's class. This diff removes the apportion class. The reference's store change over the flat valve arm reads +0.00 kWh_th at this head (`## Figures`). The flat arm's residual moves by the term's share, +6.84 % to +4.03 %, which is Carry 15's own prediction.
- Carry 14 (residual and attribution figures): re-taken at the merge base and at this head in `## Figures`. The base matches Carry 14's 056abe4d row.
- Carry 15 (the apportion seam): built here. Its precondition, the census reading 0 at this stage's merge base, holds (`## Figures`). The dispatch of this group's pending carries to this seat is the orchestrator's placement of the removal here. The `_hz_` block in `tests/features.py` that pinned the removed method keeps its two checks that still describe the tree: the held tank at zero demand, and the reference seeding the solve inside its bounds. The spread checks are deleted with the method, and so are its four killed-by rows and one survivor triage under `tests/mutation_ledger/`.
- Carry 9 (valved reference below its setpoint): reproduced on an install's own parameters (`## Figures`, `tests/replay/owner-2026-10-30-away.json`: two-zone, valve `manual`, target 21). It is not built here. See `## Forward-carry`.
- Carry 10 (the store's charge read as one channel): re-measured. It is not built here. See `## Forward-carry`.
- Settled on the roster before this dispatch, so nothing is owed for them here:
  - Carry 0, Carry 2, Carry 3, Carry 6, Carry 7, Carry 8, Carry 11 and Carry 12 are dismissed there (superseded, or duplicates of Carry 3, Carry 4 and Carry 5).
  - Carry 1 is implemented (dca53dc6).
  - Carry 5 and Carry 13 moved to R11-INTAKE-R10-RESIDUE.
  - This diff touches none of their code (`_terminal_cost`, `_deferred_energy_cost`, `_plan_dhw_min_cost`). Carry 3, Carry 6 and Carry 11's -3.90 % / -8.02 % are the part-1 base's figures; this head reads +4.03 % / +0.40 % (`## Figures`). Carry: dismissed: the roster's dispositions, restated

## Head

The head is `b48274c195c101902a1383a76d7043262264cd2d`: seven commits on origin/main `e23124ff6e45bac1d48b4a775dad555a37965355`.
- ee1d3d0d removes the method, adds the failing check and deletes the method's pins and ledger rows.
- The next commit re-records `class_excess_loc` (17514 to 17481, the removed method).
- 21d6df7c, 222032c3 and ee3c5bbc claim the golden drift (`## Figures`). The later two add the three fixtures that `golden.py`, but not `env_drift.py`, reads, and recast the suspensions in the form the stamp restores.
- The last commit deletes the `_compute_baseline_power` `GUARD_OFF` ledger pin, whose site was the removed valve branch (`ci_predict` `STALE PIN`).
- 14e9b16a restates the `R10-HOTFIX-SAV-ESTIMATE` first-step pin. It required exact equality with the horizon mean, `< 1e-9`, which was the removed spread's own output. It is now bounded at `< 1e-3`. Two-zone valved houses read 0.99984: two zones held at one temperature drift apart over the day, which is Carry 9's open seam, not a step-0 transient. This loosening is disclosed with its control in `## Null control`. Measured 2026-11-13 (UTC). VERSION, the manifest and RELEASE_NOTES are untouched.

## Mutation proof

The fix deletes lines, so the mutant restores them: `optimizer.py` at the merge base, with this head's `tests/features.py`. Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" "from profiles import house as _hb_house" "# The start's settlement, at its limits"`. The prelude comes from `features_block.py --emit-prelude` over the same markers.
- Mutant (base production code): `FAIL behind a valve, the booked reference's first step holds its held state  [power 1.4408104309112266; room 19.399999999999636 -> 19.399999999999636, slab 23.599999999999568 -> 23.599999999999586, tank 25.99999999999953 -> 26.16979405144286]`, `1 of 15 FEATURES BLOCK FAILED`.
- Head: `ALL 11 FEATURES BLOCK PASSED`.

## Null control

- The census at the merge base reads `worst first-step dS +0.0000 kWh_th`, `over 0.02 kWh_th 0` across `cases 1728 of 1728`. Its pump-bound controls (two-zone, -25 C, 4.0 kW pump) also read +0.0000, so a census that skipped the store term could not read 0 there.
- The flat arm's comfort term (+6.18 kWh_e) and stored term (-5.07 kWh_e) are the same at both ends, so only the reference's own store moved.
- The restated first-step pin (`R10-HOTFIX-SAV-ESTIMATE` block, `tests/features.py`) still detects a transient at `< 1e-3`. The mutant `state = initial_state` in `_compute_baseline_power`, which starts the reference from the measured state, gives `9 of 9 FEATURES BLOCK FAILED`, with first-step ratios from 0.0 to 3.41. Head: `ALL 9 FEATURES BLOCK PASSED`. Command: `features_block.py "# R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0" "# The owner's no-wood ruling against"`.
- Carry 9's control is the same install with the valve off (`mixing_valve_mode none`): held room 21.000 at every outdoor temperature.

## Figures

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=b48274c195c101902a1383a76d7043262264cd2d -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->
- Census, `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_held_capacity_census.py` (sha1 8d9afaacc33cb783dbe919dbf7157b26fa7422af), at the merge base: `cases 1728 of 1728, worst first-step dS +0.0000 kWh_th`, `over 0.02 kWh_th 0`.
- Residual attribution, `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat` (sha1 4b214a9bc27788bab2b7f5657b70d979bbf84d9f):
  - Base: `residual ... +6.84 %`; `non-steady -6.83; reference stored +11.11 kWh_th`.
  - Head: `residual ... +4.03 %`; `non-steady -6.83; reference stored +0.00 kWh_th`.
  - `plant steps seen 192 of 192` at both ends. Carry: dismissed: evidence for Carry 14 and Carry 15, not a finding
- The same harness, arm `winter_typical`, at this head: `residual ... +0.40 %`; `non-steady -7.46; reference stored +0.00 kWh_th`; `plant steps seen 192 of 192`. At the base the arm reads +3.38 % with reference stored +11.11 (Carry 14's 056abe4d row; production code there differs from the base's by a no-op clamp). The base arm was not re-taken here.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat` and `valve-vary` (sha1 243d49a45b4a10c3e00234c9867573638f6a9900), at this head: `valve-flat: SOUND`, residual +4.03 %; `valve-vary: SOUND`, residual +0.40 %. The brief's -3.90 % / -8.02 % are the part-1 base's figures.
- Carry 9 on the owner's replay install, via a scratch probe that builds `ThermalParameters.from_config` from that fixture's entry and calls `_thermostat_held_state` and `_compute_baseline_power` at a constant outdoor temperature, target 21, 96 steps. The probe is a one-off measurement, so it stays out of the tree (`fixer.md` step 18). Results:
  - Valve on, at +5 / -5 / -15 C: held room 20.557 / 20.077 / 19.596; reference end room 20.750 / 20.398 / 20.046.
  - Valve off (control): held room 21.000 at all three; end room 21.115 / 21.180 / 21.246.
  - The plant alone, driven at the pump for 288 steps from 21 C behind the valve: room 20.749 (+5 C) and 20.045 (-15 C), tank at `buffer_max_temp` 56.00.
- Carry 10, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py exchange` (sha1 e47dc605d1d95abd50b796d52730bd3394c36702), at this head: `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327`. These are the same figures as the carry's source, and this diff touches neither the combi solve nor the ledger.
- Golden drift, `PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/golden.py` (and `tests/env_drift.py`) against origin/main, one environment. Exactly eight valved fixtures move, in `baseline_cost` and the savings derived from it (plan leaves exempt). Every unvalved fixture is unmoved: that is the null.
  - `valve_storage`, `valve_storage_smart_write`, `wood_two_tank` and `wood_two_tank_smart_write`: 129.949456 to 129.18872.
  - `wood_coil`: 144.780619 to 144.019883.
  - `valve_storage_small_tank`: 128.370033 to 126.961988.
  - `valve_upper_direct_slab`: 126.300702 to 129.924919.
  - `valve_storage_low_target`: 113.036724 to 115.88948.
  - All eight are claimed in `tests/golden/claimed_drift.txt` with their direction. `golden.py` reports `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE` after the claim.
  - Six of the eight carry a may-drift entry, and `baseline_cost` is a judged key such an entry cannot excuse. Those six entries are suspended in `stamp.py`'s two-line restore form (`SUSPEND_HEAD_RE`). `stamp.rewrite_claims` run on this file for the next patch version leaves no claims and restores every entry. This is `tests/entities.py`'s "each suspended entry restored with the claims deleted" check.
- Structure: `python3 tests/structure.py --record` moved `class_excess_loc` 17514 to 17481 and nothing else.
@@GATE@@

## Red checks

none

## Unpinned sites

none: the diff adds no production line, so there are no diff mutants to draw.

## Forward-carry

- Carry 9: on the owner's replay install (two-zone, valve `manual`, target 21) the held state sits below the plant's own ceiling. Measured in `## Figures`: held 20.557 against the plant's 20.749 at +5 C, and 19.596 against 20.045 at -15 C. The reference therefore warms over the horizon and stores heat that the booked steps buy.
  - Below 21 C is the install's limit: the plant at the pump with its tank at the cap reaches no higher. The gap between the held state and that limit is not the install's limit.
  - The bound `_held_unreachable` reads holds both zones at one temperature against `thermal_model.valve_top_draw`. The two-zone plant settles with its zones apart (`_thermostat_demand_two_zone`: "One control cannot hold both zones exactly").
  - Aligning the bound changes `thermal_model.py`, a file outside this group's roster `files`. Which group owns that change is a ruling for the orchestrator.
  - A fix is legitimate only if, on this install, the held room equals the plant's own at-pump equilibrium within 0.02 K, and the valve-off control stays at 21.000.
  - Re-measure with the probe recipe in `## Figures` at that stage's merge base.
  - Carry: dismissed: already this group's roster Carry 9, still pending; this body re-measures it for the orchestrator's ruling on its owner
- Carry 10: the flux exchange's split is unchanged at this head (`exchange_dhw_kwh=22.135` against `null_dhw_kwh=5.327`). `sensor.py`'s `split_method` attribute already says which split the tile shows ("apportioned from the planned space/DHW power split"). On a combi store that planned hot-water channel includes the space heat the exchange buys.
  - Whether the tile must read the store's charge as one channel, or whether the attribute's text discharges the carry, is a display ruling. It is for the owner or the orchestrator, since `sensor.py` is outside this group's `files`.
  - Re-measure with the harness's `exchange` arm at that stage's merge base.
  - Carry: dismissed: already this group's roster Carry 10, still pending; this body re-measures it for the owner's or orchestrator's display ruling

## Friction

none
