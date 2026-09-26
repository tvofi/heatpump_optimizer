# D5 — verifier V2 (independent), audit round 9, box G4-V2

Evidence tree: /home/claude/ev (baseline 1936d5ca + round9). nproc=4. Every number below is a count or ratio, so contention does not affect it. Harness runs used thread_factor=1.000. load1 ranged from 0.32 to 2.31 while other seats ran. I changed no production file; the only perturbations were in memory. `git status` shows only verify-v2 directories. Harnesses are in `tools/audit/round9/D5/verify-v2/`, and each header gives the command and metric. Node harnesses take `NODE_PATH` from a private `mktemp -d` npm prefix (marked@15, acorn@8).

**Step 1 (re-running the finder harnesses):** all reproduce exactly.
- setup_section: stale_facts=4, and 1 under perturb.
- entity_counts: 75 constructed, disagreeing=1.
- quick_setup_promise: 2, and 0 under perturb.
- card_version_doc: 1.00, and 0.00 under perturb.
- md_tables: 9.
- field_labels: 5, and 4 under perturb.
- service_fields: 5, and 0 under perturb.
- comment_numbers: 3, and 46 of 47.
- card_comment_names: 12 names / 17 mentions, and 5 under perturb.

## D5-s1-01: verify, medium
- **Harness:** v2_setup.py
- **Method:** I drove the real ConfigFlow: `user` with price_source=entity and no token, then `user_sensors`, then the step it returned. I collected the en.json labels (data and menu_options) of every visited step and checked each one against the "## Initial setup" section text. I also counted the entities the 6 platforms construct under 3 configs: bare tibber, entity price with sensors, and two-zone+wood+dhw+buffer.
- **Metric:** labels on the steps the flow visits before `temperature` that the section never names.
- **Results:**
  - unnamed_labels=5: the 3 finish_setup menu entries plus "Electricity price source" and "Price sensor".
  - tokenless_first_screen=1, and the section says the token is **required**. Line 13 says "Only two answers are genuinely required: a Tibber API token".
  - Entity count is 75 under all 3 configs (min=max=75). The doc says 74.
  - Perturb (finish_setup replaced by temperature) moves unnamed_labels from 5 to 2.
- **Attacks:**
  - Could the count depend on config, so that 74 is right somewhere? No: 75 everywhere.
  - Does the section defer to setup.md? Grep for quick/finish/price source/setup.md in the section: 0 hits.
  - Token "required" is true for the default tibber source. But the doc presents it as unconditional, and the flow accepts entity prices without a token.
- **Severity:** medium is kept, because a Nord Pool user is told they need a Tibber token.

## D5-s1-02: verify, medium
- **Harness:** v2_quick_setup.py
- **Method:** unlike the finder, who called `derive` alone, I ran the real flow end to end: user → user_sensors → finish_setup → quick_setup (buffer=yes, wood buffer=yes, both probes) → device_prefill declined → finish_now → setup_overview submit → create_entry data → `ThermalParameters.from_config`. I did this over all 8 combinations of two_zone × dhw × wood_furnace.
- **Metric:** broken (answer set, promise) pairs.
- **Results:**
  - broken_pairs=16 of 16: buffer_is_store False in 8/8, two_tank_modelled False in 8/8. mixing_valve_mode is unset in every entry.
  - Perturb (derive writes mixing_valve_mode=manual): the buffer promise drops to 0 broken. The two-tank promise still fails in 6/8, because two-tank also needs two_zone and wood_furnace.
- **Attacks:**
  - Does device prefill ever set the valve mode? It does not. Grep of modbus_prefill and device_prefill shows no write to mixing_valve_mode.
  - Is it reachable in real HA? Yes: it is the config flow itself.
- **Beyond the claim:** setup.md's statement that "the two probes ... switch the two-tank physics on" is also false without two-zone and wood furnace. The finding understates rather than overstates.

## D5-s1-03: verify, low
- **Harness:** v2_card_version.py
- **Method:** instead of simulating stamps, I read the real release history. For the last 20 v-tags merged into the baseline, I compared CARD_VERSION in `git show <tag>:.../heatpump-optimizer-card.js` against the tag version.
- **Results:**
  - share=1.00 (20/20). Every tag from v6.3.13 onward is equal.
  - The doc still says the banner "is often lower than the integration version" (doc_says_often_lower=1), with a v6.6.8 banner example.
  - Perturb (compare each tag's card against the previous tag's version) gives 0.00.
- **Attacks:** Is the doc true historically? Yes: 5.4.x cards shipped through v6.2.x–v6.3.12. So the paragraph is stale rather than always wrong. Its advice ("compare against the card version in the release notes") still works, because that version now equals the integration version.
- **Severity:** hygiene, low.

## D5-s1-04: verify, low
- **Harness:** v2_md_tables.mjs, using a different renderer (marked@15 GFM lexer) from the finder's markdown-it.
- **Results:**
  - misplaced_lines=9: orphaned pipe rows at configuration.md:185-187 (3) and swallowed prose at 633-638 (6). All other files are clean.
  - Perturb (move the interposed paragraph below the rows, add a blank line after the table): 0. The perturbation touches only these two shapes.
- **Attack:** is this a renderer artefact? No: two independent GFM implementations give the identical 9 lines.
- **Severity:** content is still readable, so low hygiene is right.

## D5-s1-05: verify, low
- **Harness:** v2_field_labels.py
- **Method:** I matched the Two-zone table's Setting column, with "A / B" rows split per floor, plus every label-shaped *italic* span in configuration.md and how-it-works.md, against every field label anywhere in en.json. Parentheticals and a trailing "sensor" were stripped.
- **Results:**
  - 9 unmatched out of 19 refs.
  - Four are false positives of my wider rule, checked by grep. They are option or selector values, not field names: "Flow temperature" (2) and "Read from a sensor" are selector options in en.json, and "HP Setting mode" is a third-party Modbus entity name.
  - The remaining **5 are exactly the finder's**. Each of those 5 has a close en.json label (difflib ≥0.6) except "Radiator power fraction" (actual label: "Share of heat going to radiators").
  - Perturb (relabel radiator_power_fraction): 9 → 8.
- **Severity:** hygiene, low.

## D5-s1-06: verify, low
- **Harness:** v2_service_fields.py
- **Method:** I read the keys of every SERVICE_SCHEMA_* voluptuous object, not the registration stub, and searched for each key in backticks across README and the 7 docs.
- **Results:**
  - undocumented_fields=5: wood_slots, wood_type, wood_packing, wood_price_sek_m3, wood_furnace_efficiency, out of 60 keys read. SET_AWAY's vol.All wrapper was skipped, which is 2 fewer keys than the finder's 62. It does not affect the count.
  - Table says 16; the paragraph lists 11; the schema has 16.
  - Perturb (the doc names the 5): 0.
- **Attack/mitigation:** undocumented_but_in_services_yaml=5. HA's Developer Tools does describe all five, so a user can still discover them.
- **Severity:** low hygiene; no stronger than that.

## D5-s2-01: verify, low
- **Harness:** v2_card_comments.mjs
- **Method:** I used the acorn tokenizer. I took `_name` identifiers in comments that occur in no non-comment token of the card (identifiers, property names, string and template contents) and in no word of production Python. This does not use the finder's TS parser or live-member reflection.
- **Results:**
  - stale_names=12, stale_mentions=17, with_successor=7. The names are identical to the finder's.
  - Perturb (rewrite the 7 to their successors): 5 names / 6 mentions.
- **Attacks:** I read the no-successor comments at lines 2936, 5899, 8756, 10126 and 11533. All describe current behaviour by a name that no longer exists; none is marked as history.
- **Severity:** hygiene, low.

## D5-s2-02: verify, low
- **Harness:** v2_comment_numbers.py
- **Method:**
  - C1: DefrostDerate.observe was called 2000 times at a delivered ratio of 0.01. The EMA settles at floor=0.5500, but the comment says "less than half".
  - C2 and C3: I recorded the update_interval kwarg the coordinator passes to DataUpdateCoordinator. The hastub drops it, so I wrapped the base `__init__` in memory. I also read the optimization_interval NumberSelector in both flows: range 10–120, step 5.
- **Metrics:** default_mismatches counts comment numbers that differ from the shipped default or bound. strict_mismatches counts comment numbers that no admissible config can produce.
- **Results:**
  - default_mismatches=3, which matches the finder's metric.
  - strict_mismatches=2. "every 15 minutes" is an admissible setting, though not the default of 30. "5-minute" is below the selector minimum of 10 in both flows. The 0.5 derate floor is not the 0.55 clamp.
  - Perturb: both counts go to 0.
- **Attack outcome:** one of the three rows is arguable as an example rather than a claim. Under my stricter metric the finding still stands at 2.
- **Severity:** hygiene, low.

## D5-s2-03: verify, low
- **Harness:** v2_comment_numbers.py (C4)
- **Method:** I recovered the draw's cold end from `dhw_draw_power`, a property: cold = setpoint − P/(lph·Cp), with greywater set to 0. I did this at each dhw_inlet_temp selector setting (2–25, step 0.5, which is 47 settings).
- **Results:**
  - draw_cold_end_off_constant=46 of 47. Only the default of 10.0 matches.
  - Perturb (dhw_inlet_reference forced to the constant): 0.
- **Attacks:**
  - The grid inflates the count, since most installs sit at the default (and it matches there). But the coupling the comment asserts is structurally false: all 3 production callers of `dhw_coil_draw_reduction` pass `inlet_temp=...dhw_inlet_reference`/`inlet`, so the constant is only an unused default argument.
  - The comment's rationale ("named so ... cannot quietly disagree") therefore describes code that no longer exists.
- **Severity:** hygiene, low.
