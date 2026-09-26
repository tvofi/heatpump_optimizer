# D6 round 9 — verifier V3 (reach and class)

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus round-9 evidence (worktree head 6f51db2c). Box: 4-CPU linux container, CPython 3.14, shared with two other sub-seats. Every number below is a count or a ratio of counts, so contention does not affect it. load1 was 0.46–2.72 and thread_factor 1.000–1.004 on every run.

Harnesses, all under `tools/audit/round9/D6/verify-v3/`:
- `v3_checks.py` has one independent metric per finding, and `--perturb` moves each of them. Its outputs are in `v3_checks.baseline.txt` and `v3_checks.perturb.txt`.
- `s2_05_own_perturb.py` is a perturbation that moves D6-s2-05's own number.
- `votes.json` holds the votes.

Command: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/verify-v3/v3_checks.py [--perturb]`.

**Exposure:** one broad grep printed `docs/audit-2026-09.md:609`, a round-earlier D7-01 register row, and two plan rows about #990. None of them is a D6 verdict. I read no verifier report and did not use GitHub.

**Stub trap met (not a finding; `ha_contract.py` already records `Entity` as simplified):** the hastub `Entity` class does not model `entity_registry_enabled_default`. If you read that property with a default of True, the disabled count comes out as 15 on the Finish-now entry and 8 on the full-wizard entry, instead of 26 and 19. Upstream falls back to `_attr_entity_registry_enabled_default`. The finder's census and `v3_checks.enabled_default` both use that fallback, so their numbers match what real Home Assistant would count.

## D6-s1-01 — Heat Pump Action states omit `idle` and `system_identification`
- **Numbers:**
  - Finder harness: `action_states_undocumented=2`; with `--perturb=action_states` it goes to 0.
  - Own harness: `s1_01_states_undocumented=2`. Method: an AST scan of the `"mode"` literals in production, intersected with the sensor's `_attr_options`. `get_current_action` on an empty result returned `idle` (1 of 1). `--perturb` takes it to 0.
- **Reach in real Home Assistant:**
  - `idle` comes from `optimizer.get_current_action` (the empty-plan and pre-horizon branches).
  - `system_identification` comes from `coordinator._run_system_identification` after a button press, with the option enabled.
  - Upstream ENUM validation accepts both, because both are options. 0 of 10 options lack a state translation, so real HA both publishes and displays them.
- **Severity:** low. Automations written from the README list miss two states; no published value is wrong.
- **Seam rule:** `C1[56]` covers both of README's ENUM state lists. No copy of the list exists under `docs/` (grep for `pre_heat`), so it enumerates the property's README scope. It is a fixed row filter rather than a discoverer.
- **Class:** I5 confirmed.
- **Vote:** verify.
- **Metric:** production-written action modes in the options, less `unknown`, that are absent from README's row.

## D6-s1-02 — two-zone split and orientation factor on the wrong options pages
- **Numbers:**
  - Finder harness: 3; `--perturb=orientation` gives 2.
  - Own harness: 3 wrong out of 9 statements (inter_zone_heat_transfer, radiator_power_fraction and solar_orientation_factor all sit on `thermal_model_zones`). `--perturb` gives 0.
- **Reach:** the page labels come from `strings.json` `menu_options`, which is what real HA renders. No stub symbol is on this path.
- **Severity:** low. The field is one menu entry away.
- **Seam rule: partial.**
  - `C52`/`C53` cover only README:391-395.
  - Not covered: the Advanced-page table (README:790-806) and the page statements at README:421, :583, :637, :809, :815 and :898.
  - I checked three of those; 0 of 3 are false.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** README field-to-page statements whose menu label resolves to a different step than the field's `_OPTION_FIELDS` step.

## D6-s1-03 — six hot-water entities disabled on a no-hot-water install, undocumented
- **Numbers:**
  - Finder harness: 6; `--perturb=dhw_config` gives 0.
  - Own harness: I drove the real flow (user → finish_setup → finish_now → setup_overview → create_entry). The created entry has no `dhw_tank_volume`.
  - Census: 26 disabled on that entry, 19 on the full wizard, 6 undocumented. DHW Boost is excluded because a README sentence already calls it disabled. `--perturb` gives 0.
- **Reach:** real HA reads the registry default only at first registration. No production code re-enables an entry (0 hits for `disabled_by` or `async_update_entity`). A user who adds a tank later therefore keeps these six disabled, and README does not point them to it. The workaround is the entity registry.
- **Severity:** low.
- **Seam rule:** enumerates. Both topologies are censused, and the gate is a single predicate (`has_hot_water` plus an optional probe slot). The Quick setup path with its defaults writes a 200 L tank and censuses at 19, the same set as C08.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** entities that are registry-default-off on the entry the real Finish-now flow creates and are not documented as disabled anywhere in README.

## D6-s1-04 — apply_manual_plan "up to 20 hours"
- **Numbers:**
  - Finder harness: 4.0 h; `--perturb=clamp_expiry` gives 0.0.
  - Own harness: I went through `handle_apply_manual_plan` into a real coordinator (refresh mocked) and read its own `pinned_space_steps`.
  - Pinned hours were 20.25, 24.0, 24.0 and 24.0 for expiries of +20, +24, +48 and +168 h. That is 4.0 h beyond 20.
  - A 168 h override is still live 100 h later (`override_live_after_100h=1`).
  - Clamped, the result is 0.25 h. That residue is the quarter-grid overlap rule, not a defect.
- **Attacks:**
  - Nothing clamps downstream: `coordinator.async_apply_manual_plan` stores the override as given.
  - `expires_at` is validated by `cv.string`. The stub's `cv.string` diverges only on None/list/dict, so the path is the same in real HA.
  - The finder's 4.0 h is capped by the 96-step horizon. The wall-clock duration README actually describes has no upper limit, so 4.0 h is a lower bound on the error.
- **Severity:** low for the doc claim. It needs an explicit `expires_at`, and the card caps at 20 h. The code side breaks `const.py:1306-1315`'s invariant ("override shorter than horizon"). That part is P2-shaped and is correctly routed as a lead.
- **Seam rule: partial.** C26 checks README:660 only. The same false bound also appears in:
  - `docs/how-it-works.md:76` ("≤20 h")
  - `strings.json`/`en.json:2266`, the service description real HA shows under Developer Tools → Actions ("for the next 20 hours").
- **Class:** I5.
- **Vote:** verify.
- **Metric:** ON-pinned hours the real coordinator reports for `expires_at=now+48h`, less 20.

## D6-s2-01 — configuration.md "All 74 entities"
- **Numbers:**
  - Finder harness: delta 1, total 75; `--perturb-count` gives 0.
  - Own harness: 75 entities on both the full-wizard entry and the Finish-now entry created through the real flow, so the delta is 1. `--perturb` gives 0.
- **Reach:** the stub only collects what `async_add_entities` receives, so real HA creates the same 75.
- **Severity:** low.
- **Seam rule:** enumerates every numeric count in `docs/*.md`. It misses the spelled-out and "(N total)" forms, but those are all in README and are pinned by `tests/entities.py`.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** entity census for the flow-created entry minus the N at configuration.md:196.

## D6-s2-02 — "Saving this page creates the entry"; flowchart omits the menu and the overview
- **Numbers:**
  - Finder harness: 0 and 11 steps; `--perturb` gives 1 and 10.
  - Own harness: 0. The weather submit returns a form. The trail after it is `setup_overview` → `create_entry` (2 results), and before it sits `menu:finish_setup`. `--perturb` gives 1 and 1.
- **Reach:** this is the production flow. The stub's FlowResult is a plain dict, which does not change the step sequence.
- **Severity:** low.
- **Seam rule: partial.** It drives only the Describe-my-building branch, and the comparison is by eye. The flowchart's "Enter thermal values directly" branch is not driven.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** 1 if the weather submit returns `create_entry`, else 0.

## D6-s2-03 — curve bias "at most 0.5 K per week"
- **Numbers:**
  - Finder harness: 0.600; `--perturb-curve` gives 0.457.
  - Own harness, hourly feed for 365 days: 0.6 K. 5.0 % of all 7-day windows exceed 0.5 K, so it recurs rather than happening once.
  - With `MAX_DOWN_PER_WEEK=0.4`: 0.543 K.
- **Mechanism attack:** under both perturbations the drop still exceeds the configured cap (0.457 > 0.3 and 0.543 > 0.4). The reason is that the cap is measured against the previous step only, and the first step is uncapped. The finder's arm therefore shows direction; it is not a null control.
- **Reach:** real HA reaches it through `coordinator.py:8352` when curve learning is on (opt-in, ECL110).
- **Severity:** low. About 0.1 K/week beyond the stated rate, with an instant reset on any comfort miss.
- **Seam rule: partial.** It finds 6 copies. It misses:
  - `translations/sv.json:1333` ("högst en halv grad per vecka")
  - `curve_learning.py:15/40/107-108`, whose comment states the same 7-day invariant.
- **Class:** I5 for the docs. The code comment asserts the invariant the code breaks, so the fix may belong in production. No production class fits a rate-window defect.
- **Vote:** verify.
- **Metric:** largest bias drop over any 168 h window.

## D6-s2-04 — "two starting points"
- **Numbers:**
  - Finder harness: 4 candidates and 8 minimizations; `--perturb-starts` gives 2.
  - Own harness (a `mock.patch.object` spy over five golden SCENARIOS): candidates per call were [4], [4, 1], [4], [5] and [4]. Every space solve got at least 4 and the maximum is 5 (two-zone, no DHW). The docs say 2.
  - I did not measure the warm-start candidate the coordinator adds.
- **Reach:** pure solver code; no stub is on the path.
- **Severity:** low.
- **Seam rule:** enumerates. The only stated count is `how-it-works.md:108-111`.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** largest candidate list passed to `_multi_start_minimize`.

## D6-s2-05 — simulate_plan prose list omits five wood fields
- **Numbers:**
  - Finder harness: 5 schema-only keys on the simulate_plan row.
  - Own harness: 5 missing out of 16 schema keys.
  - `s2_05_own_perturb.py` drops the `wood_*` keys from the schema in memory and re-runs the finder's harness. The count goes from 5 to 0.
- **Perturbation defect:** the finder's `--perturb` edits the `set_thermal_parameters` and `set_mode` schemas. It moves `services_claims_false` from 1 to 5, but the cited simulate_plan row stays at 5, and the finding's value is not a RESULT line. The finding's own number does not move under its own perturbation. The judge should use `s2_05_own_perturb.py`.
- **Reach:** `services.yaml` lists all 16 fields, so real HA's action UI shows the wood fields. Only the prose is out of date.
- **Severity:** low.
- **Seam rule: partial.** Checking every `**`service`**` paragraph against its schema finds 3 more unnamed keys: `assign_entity.manual_setpoint`, and `apply_topology.dhw` and `apply_topology.wood`. `services_claims.py` does not flag them.
- **Class:** I5.
- **Vote:** verify.
- **Metric:** simulate_plan schema keys absent from configuration.md's "Fields, all optional:" list.
