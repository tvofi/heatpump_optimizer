# D5 verify-2 (r11)

Tree: all findings D5-s2/D5-s3 measured in the planted export copy (20 ._* AppleDouble artefacts removed in the private copy so utf-8 reads work). Harness reruns reproduced the expected numbers exactly; load1 0.64-0.98.

## D5-s2-01 - verify (low)
- value: 14/24 menu rows drift; 4 dup fences; 15 dup paragraph units
- metric: count of identical-text repeats (finder: outline units incl. table rows/bullets >=12 words; mine: lines >=12 words, fences skipped) + table rows with differing description
- attacks: null --plant: dup_paragraph 15->16; --dedupe: dup 15->9, menu drift 14->0; --perturb no-op; leave-one-out: 6 of 15 are README/config table rows, 9 are inside configuration.md; 'paragraph' wording loose (unit includes table rows)
- reproduced: dup_paragraph=15 menu_twin_drift=14 dup_fence=4 (3-way mermaid 1.00, how-it-works seq 0.62/18 lines)
- independent: line-level repeats 19 (7 cross-doc); table rows README vs configuration: 24 common, 14 differ (exact match); identical mermaid in 3 docs (README, configuration, setup)
- reach: docs/comments only; no HA runtime path; class new; seam_rule enumerates: partial: names the demonstrated checks, not every doc pair

## D5-s2-02 - verify (low)
- value: 1 orphan (CONTRIBUTING.md); inbound 0
- metric: docs/*.md with no inbound link from README/docs
- attacks: --link-orphans: orphan 1->0 (null direction ok); grep README/docs/CLAUDE.md for CONTRIBUTING: 0 hits; GitHub itself surfaces docs/CONTRIBUTING.md automatically, so consequence is trivial
- reproduced: orphan_doc=1
- independent: regex of ](...basename) inbound per doc: 0 for CONTRIBUTING, >=1 for the other seven
- reach: docs/comments only; no HA runtime path; class new; seam_rule enumerates: yes for the 8 docs (every docs/*.md counted)

## D5-s2-03 - verify (low)
- value: basis_gap_pct 18.9; basis_stated 0 of 5
- metric: relative gap of two published heat-loss bases; reader units naming sysid loss that state basis
- attacks: --ratio 1.0 null: gap 0.0; --doc-fix: stated 0->1; payload.py:587 comment says the field 'names the basis' only in code, not reader docs
- reproduced: gap 18.9% units 5 stated 0
- independent: read sysid._zone_heat_loss (U+L) vs sensor effective*1000 at sensor.py:2061: different bases confirmed by code; README:623 and how-it-works 1199-1257 give no basis
- reach: docs/comments only; no HA runtime path; sensor attributes are real HA-visible; class I5; seam_rule enumerates: partial: keyed on one profile

## D5-s2-04 - verify (low)
- value: false_units 2 (1 here), is_inert False
- metric: comment units whose executed check contradicts them
- attacks: --perturb-closure: false 2->1; --perturb-text: ->0, long 8->0; closure.is_inert('docs/img/model/make_model_figures.py')=False, in INERT_EXCEPT; doc_claims.py loads it via importlib (l.196)
- reproduced: false_units=2 long=8 (this file: 1 false + 45-word sentence l.427)
- independent: direct call closure.is_inert=False; INERT_EXCEPT membership True; closures.json lists file in 1 closure
- reach: docs/comments only; no HA runtime path; class I5; seam_rule enumerates: partial

## D5-s2-05 - verify (low)
- value: false font-stack claim + 5 long sentences
- metric: false comment unit; sentences >40 words
- attacks: --perturb-text: false->0 long->0; README hero is ![...](banner.png), no CSS font stack (head of README)
- reproduced: long[card_figures.mjs]=5 (41,55,44,46,43), false 1
- independent: README head shows banner.png image; my crude comment splitter finds 8 >40 (merges sentences, so counts differ, direction holds)
- reach: docs/comments only; no HA runtime path; class I5; seam_rule enumerates: partial

## D5-s2-06 - weaken (info)
- value: 2 sentences 51 and 55 words
- metric: sentences >40 words in header comment
- attacks: --perturb-text long->0; no false fact (finder says so); pure style criterion C5
- reproduced: long[make_card_weekly_figure.mjs]=2
- independent: crude splitter: 3 over 40 (51,86,66) - merged sentences; confirms >=2
- reach: docs/comments only; no HA runtime path; severity weaken to style-only; class new; seam_rule enumerates: partial

## D5-s2-07 - verify (low)
- value: plant_refused=0 planted_units=0 rc=1
- metric: per-seat null control result (plant_refused, rc)
- attacks: --perturb (plant into first D5-suffix file): plant_refused 1 rc 0; null control D6 over same files: plant_refused 1; comments.py check also shows plant_refused=0 in README.md / d5_first=1
- reproduced: plant_refused=0 rc=1
- independent: comments.py own ledger run reproduces plant_refused=0 in README.md and =1 when a .mjs is first (2nd harness path)
- reach: tooling only, no HA path; class new; seam_rule enumerates: yes: rule keyed on file suffix of first file for all 10 seats (finder's note: only s2 starts with .md)

## D5-s2-08 - verify (medium)
- value: 7 of 57 mismatches
- metric: doc number vs production value pairs
- attacks: perturb-code 7->3, -age 7->5, -echo 7->6, -doc 7->3 (all move down); null: 50 other pairs ok; leave-one-out per cause consistent
- reproduced: pairs=57 mismatches=7
- independent: grep: const DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS=10.0 (const.py:1600), QUIET_STORE_MAX_AGE_MINUTES=360 (const.py:297, indoor+tank), ECHO_GRACE_S=20.0 (pump_arbiter.py:226); docs state 7 days, 60 min, 60 s - all three confirmed by hand
- reach: yes: user-visible doc defaults wrong in real HA; class I5; seam_rule enumerates: yes: enumerates all 57 mechanism numbers (defaults_table.py), not just the demonstrated ones

## D5-s2-09 - verify (low)
- value: swing_minus_flat 0.000
- metric: priced start term difference swing vs flat
- attacks: --null (swing through zero): 22.0; --perturb (smooth |dP| term): 23.5; direction ok; runs.start_count_batch read: counts off-to-on via running_share, no |dP| term
- reproduced: swing-flat=0.0 doc_smooth_units=1
- independent: code read of runs.start_count_batch (needs*(1-through)) confirms no step-to-step difference term; doc l.827-829 states smooth term
- reach: docs/comments only; no HA runtime path; behaviour real in HA; class I5; seam_rule enumerates: partial: one paragraph

## D5-s2-10 - verify (low)
- value: contradicted 7 of 7
- metric: presence-trio subsets left off by resolver given explicit dhw_enabled=False
- attacks: --null (no switch): 0; --perturb (drop switch branch): 0; config_flow writes dhw_enabled (wizard step)
- reproduced: 7/7
- independent: read thermal_model._dhw_enabled_from_config: returns bool(config[CONF_DHW_ENABLED]) first, presence only fallback; confirmed
- reach: yes: real config flow writes the key; class I5; seam_rule enumerates: partial

## D5-s2-11 - verify (low)
- value: quick_setup_from_end=2
- metric: position of quick_setup from end in shown init menu
- attacks: --perturb (drop advanced): 1; null setup_overview index 0; config_flow l.3466 adds 'advanced' label last
- reproduced: 2
- independent: code read config_flow async_step_init: labels['advanced'] appended last
- reach: docs/comments only; no HA runtime path; menu is real HA flow; class I5; seam_rule enumerates: partial

## D5-s3-01 - verify (low)
- value: claimed_but_needs_ha=1 (grid_fee)
- metric: modules whose docstring claims HA-free that fail to import without homeassistant
- attacks: --perturb (currency import under TYPE_CHECKING): 1->0; null: 10 other claimants import fine
- reproduced: claimed=11 needs_ha=1; thread_factor 0.449 (count, immune)
- independent: read imports: grid_fee l.56 'from .currency import money_scale'; currency.py l.21 'from homeassistant.core import HomeAssistant' at module level
- reach: docstring false only; real HA always has homeassistant, so no runtime effect; class new; seam_rule enumerates: yes: scans all 11 claimants

## D5-s3-02 - verify (low)
- value: overshoot_c=0.0 vs docstring +1
- metric: climate max_temp minus configured ceiling
- attacks: --perturb (entity sees +1): overshoot 1.0, stale_rows 0; baseline 0.0
- reproduced: overshoot 0.0 stale_rows=1
- independent: climate.py:124 _attr_max_temp = config.max_temperature (only max_temp assignment in file)
- reach: stale comment only; slider max real in HA = ceiling; class new; seam_rule enumerates: partial

## D5-s3-03 - weaken (info)
- value: long_units=363/2855
- metric: D5 units (text_ledger) with a sentence >40 words
- attacks: --perturb (split dhw_planner long sentences): 363->343 dhw_planner 29->9; leave-one-out w/o coordinator 272 (still large); 43/45 files
- reproduced: 363, 43 of 45 files
- independent: own ast+tokenize (docstrings + single comment lines, splitter by punctuation): 216 units in 41 of 45 files; count is definition-dependent (finder merges comment blocks), direction and breadth hold
- reach: style criterion only, no runtime effect; class new; seam_rule enumerates: yes: enumerates all units of the cells
