# D6, verifier V2 (independent lens), round 9

Harness (all nine findings): `tools/audit/round9/D6/verify-v2/v2_measure.py`. Run it from `/home/claude/ev` with `PYTHONPATH=tests/hastub`. Its flags are `--only=F1..F9`, `--null`, `--perturb-f1`, `--perturb-f2` and `--perturb-f9`, and the header gives every metric definition and expected value. Evidence tree at baseline 1936d5ca. Every number is a count or a number of hours taken from driven production symbols, so contention does not affect it. Full run: load1 0.65, thread_factor 1.001, swapins 0, on 4 CPUs.

I re-ran every finder harness first (step 1). All values reproduce exactly (load1 0.32–0.61, tf 1.000–1.001):
- `claims.py --no-net` printed 2 / 3 / 6 / 4.0 h, and its four perturbations printed 0 / 2 / 0 / 0.0.
- `flow_census`: 0 creates, 11 steps, 75 entities, delta 1. `--perturb-count` gave 74 / delta 0, and `--perturb` gave 1 / 10.
- `behaviour_claims`: 0.600 K, and 0.457 under perturbation.
- `howitworks_claims`: 4 candidates and 8 calls, and 2 / 4 under perturbation.
- `services_claims`: 1 false; the prose list has 5 missing.

## D6-s1-01: Heat Pump Action states `idle` and `system_identification` missing from README
- **My number:** 2. **Metric:** the distinct `HeatPumpActionSensor.native_value` strings that the real producers yield and that are not backticked in README's "Heat Pump Action" row. The producers are:
  - `optimizer.get_current_action` on an empty result;
  - the same on a pre-horizon clock more than one step early;
  - `coordinator._run_system_identification` with the experiment commanding heat. Only `sysid.step` is stubbed; the label is real.
- **Perturbation:** `--perturb-f1` (`_idle_action` publishes 'off') gives 1.
- **Attacks:**
  - Neither value is backticked in any user doc under `docs/`, so no other page documents them. It is not a stub artefact: `idle` is the empty-plan and pre-horizon fallback, and `system_identification` follows a user button press. The ENUM options already contain both, so HA shows no error; the cost is to automation authors.
  - Severity: low is earned, not inflated.
- **Vote:** verify, low.

## D6-s1-02: README puts the two-zone split and orientation factor on the wrong options pages
- **My number:** 4, out of 9 fields checked. **Metric:** fields named by an unambiguous noun phrase in README's "not all on one page" paragraph whose `_OPTION_FIELDS` step label differs from the page the paragraph names.
- **The 4 mismatches:**
  - "two-zone split", read as `inter_zone_heat_transfer`, `radiator_power_fraction` and `upper_floor_area_ratio`: README says Thermal model (expert), but the fields render on Two-zone model.
  - `solar_orientation_factor`: README says Building type and emitters, but it renders on Two-zone model.
- **Why mine is higher than the finder's 3:** I count `upper_floor_area_ratio` as part of "the two-zone split". The ambiguous "masses, losses" also has its per-floor keys on Two-zone model, and I did not count them.
- **Null control:** power limits, buffer volume, window area and SHGC all match.
- **Perturbation:** `--perturb-f2` (orientation row moved to `building_preset`) gives 3.
- README contradicts itself: line 798's page table correctly puts the per-floor numbers on Two-zone model.
- **Vote:** verify, low.

## D6-s1-03: README's disabled-by-default census omits six hot-water sensors on the no-hot-water install
- **My number:** 26 disabled in total. 7 are neither in the "Disabled by default:" list nor in a README row saying "disabled". Six of them are sensors; the seventh is DHW Boost, whose no-hot-water state README prose states at :600, which leaves 6 = the finder's value.
- **Method:** independent of the finder's synthesized entry. I drove the REAL config flow: user → user_sensors → finish_setup menu → "Finish setup now" → setup_overview submit. The resulting entry has no DHW keys, so `dhw_enabled` is False. The platforms' real `async_setup_entry` then reads `entity_registry_enabled_default`.
- **Null control:** `--null` (Continue setup path, which stores DHW defaults) gives 19 disabled and 0 unlisted, which matches README's "Nineteen".
- **Attacks:**
  - The path is reachable: it is README's own documented "Finish setup now" option, not a hand-built entry.
  - Whether README's "ordinary install" covers this path is arguable. But it is the same install README says produces "a working entry", so 26 against 19 is real.
- **Vote:** verify, low.

## D6-s1-04: README says apply_manual_plan pins "up to 20 hours"
- **My number:** 47 h. **Metric:** the largest whole hour k after apply at which the override returned by the real `services.handle_apply_manual_plan(space_slots=[], expires_at=now+48h)` still pins step 0 of a plan anchored at now+k.
- **How mine differs from the finder's metric:** the finder measured 4 h beyond 20 within one 24 h horizon. My metric shows the pin persists across re-plans for the full 48 h, so the finder's number understates the gap.
- **Null control:** `expires_at` omitted gives 19, the default 20 h.
- **Attacks:**
  - `build_override` rejects only a past expiry.
  - strings.json also claims the expiry is "deliberately shorter than the optimizer's 24-hour horizon". configuration.md :993 says only "defaults to 20 hours", which is correct. So the README row and strings.json are wrong.
  - It is user-invoked (the card uses the default), so low.
- **Vote:** verify, low.

## D6-s2-01: configuration.md says "All 74 entities"; the platforms create 75
- **My number:** delta +1 on both the Continue-path entry and the Finish-now entry, from 75 created by the six platforms' real `async_setup_entry`.
- **Metric:** entities added for a flow-created entry, minus the integer in configuration.md's "All N entities appear".
- **Attacks:** no documented entry yields 74; I tried two paths. README :417 and architecture.md :37 say 75.
- **Vote:** verify, low.

## D6-s2-02: weather page does not create the entry; flowchart omits the menu and overview
- **My numbers:**
  - `v2_forms_after_weather_submit` = 1 (`setup_overview`) on the real Continue path.
  - `v2_flow_steps_absent_from_flowchart` = 3: `user_sensors`, `finish_setup` and `setup_overview`. The count is 2 if node A's "+ optional sensors" is taken to cover `user_sensors`.
- **Real trail:** user, user_sensors, finish_setup (menu), temperature, building (menu), building_describe, building_extras, dhw, weather_sensitivity, setup_overview, then create.
- **Attacks:** the entry is created one page later, so "Saving this page creates the entry" is false. The flowchart also numbers Temperatures as step 2.
- **Vote:** verify, low.

## D6-s2-03: curve bias "at most 0.5 K per week" is false; 0.6 K in 7 days
- **My number:** 0.600 K, the same in all 20 seeds. **Metric:** the maximum bias drop between any two instants 168 h apart. `CurveLearner.record_day` is fed once per calendar day at a random 00:00–00:40 time (the coordinator folds each day at the first cycle after midnight), with margin 1.0 K, for 120 days.
- **Null control:** `--null` (`MAX_DOWN_PER_WEEK` = 0.3) gives 0.458 K.
- **Attacks:**
  - Read as a long-run average rate, the claim holds: 0.480 K/week over days 7–42. Only the windowed reading fails.
  - The code's own comment in `_step_down` ("at most MAX_DOWN_PER_WEEK of movement per 7 days") states the windowed invariant, and the code breaks it. So the claim is also false against the code's own documentation.
  - The consequence is 0.1 K of extra cooling bias in a worst week, and any comfort miss resets the bias to 0. Low.
- **Vote:** verify, low.

## D6-s2-04: how-it-works.md says "two starting points"
- **My numbers:** `len(candidates)` at every `_multi_start_minimize` call, over three `stress.build_case` cells:
  - winter single-zone no-DHW: [4]
  - winter single-zone DHW: [4]
  - winter two-zone DHW: [4, 1], where 1 is the warm-started co-optimization pass

  L-BFGS-B runs (the module's `minimize`, method L-BFGS-B) per cell: 8, 8 and 10.
- **Attacks:** the finder's metric covered one cell; I checked 3. No cell's first solve gets 2 candidates. In production the previous plan adds a fifth (`_warm_start_starts`, read, not driven), and two-zone space-only adds a deep low-energy seed. The doc's "not worth doubling the runtime" rationale is stale as well.
- **Vote:** verify, low.

## D6-s2-05: configuration.md simulate_plan prose omits five wood fields
- **My number:** 5 (`wood_furnace_efficiency`, `wood_packing`, `wood_price_sek_m3`, `wood_slots`, `wood_type`). **Metric:** keys of the schema actually handed to `hass.services.async_register("simulate_plan")`, captured with a fake services registry, that are absent from the backticked names in the configuration.md paragraph beginning "**`simulate_plan`**".
- **Perturbation:** `--perturb-f9` (wood keys dropped before registration) gives 0.
- **Method defect in the finder's record:** its perturbation edits `set_thermal_params` and `set_mode`, not `simulate_plan`, and its recorded `observed_value` of 5 equals the finding's value. The finding's own number therefore does not move under the finding's own perturbation; only the harness aggregate moves (1 to 5). Under `judge.md` that is grounds to void the harness as recorded. My perturbation shows the metric does move, so the defect is in the record, not the phenomenon. The judge should decide whether it needs a re-recorded perturbation.
- **Vote:** verify, low.

Tree state: only my own `tools/audit/round9/D6/verify-v2/` was written. The D5 and D11 verify-v2 directories belong to sibling sub-seats. No production file was mutated on disk; every perturbation is in memory.
