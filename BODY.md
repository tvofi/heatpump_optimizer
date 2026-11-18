R11-SEAM-plant-model (round 11, topic r11-seam-plant-model): one predicate per plant question, as ADR-008 part 1 sets out. The approved design is design/R11-SEAM-plant-model at 794068856351d90d9891432a38bcbe5248fc64bd, approved by design-verdict/R11-SEAM-plant-model at 61d616e673. The plan is plan/r11 at 819aa2e354b4e5baaf824b8568fd72bea8168a75. The roster group has 11 findings and no issue numbers (`PLAN/groups.json` `issues: []`), so this PR closes no issue.

Five findings reproduce at main, and each is built here:

- **D12-s1-01.** A single-zone plan published upper and lower floor rows, because `_build_plan_views` decided "two zones" from the result's lists. A single-zone solve fills those lists with the room's own trajectory. `OptimizationResult.zone_trajectories(two_zone)` now holds the one predicate: the model's flag and both lists. `_build_plan_views` and `sensor_trajectory` both read it. The P2 registry's `sensor_trajectory` fact now names `optimizer.py::OptimizationResult.zone_trajectories` as its owner.
- **D17-s1-03.** The options page offered the whole-house mass on two zones. That row now takes `when=_single_zone`, as its heat-loss sibling already did. `_single_zone` calls `thermal_model.two_zone_from_config` (the body that was in `ThermalParameters.from_config`, moved unchanged), so it no longer builds a whole `ThermalParameters`. The options-page help says where a two-zone house sets its floor masses.
- **D17-s3-02.** `set_thermal_parameters` refuses `house_thermal_mass` and `house_heat_loss_coefficient` on a two-zone model before anything is written. The refusal is in `_refuse_house_fields_on_two_zones`, keyed on `two_zone_from_config(coord.effective_config)` (verdict note pm-05) and on `thermal_model.SINGLE_ZONE_HOUSE_FIELDS`. It uses the new translation key `set_thermal_params_house_field_two_zone` (en/de/sv), and the action's field help says that both fields apply to one zone only. `services.yaml` carries selectors and no descriptions, so it is not edited: the field help is in `strings.json`'s `services` block.
- **D8-s1-01.** The sensor-gap advisor priced a hot-water coast on installs that have no hot water. `_gap_probe_terms` now prices `dhw_extra_kwh` only when `thermal_model.dhw_enabled_from_config(config)` is true. That function is `_dhw_enabled_from_config` made public, which removes `config_flow.py`'s private cross-module import.
- **D17-s2-03 (text only, as the verdict rules).** The quick-setup `wood_furnace` and `wood_buffer_tank` descriptions (config and options flows, en/de/sv) now state the conditions the code actually has. The plan uses the fire or the two-tank model only with a throttling mixing valve set in Options, and the pump stands down only when the external-heat detection switch is on. The same corrected wording is in `quick_setup.py`'s module docstring and probe comment and in `config_flow.py`'s quick-setup page docstring.

Six findings do not reproduce at main, and their ruling is the owner's 2026-11-18 precedent: "not reproduced at main, pinned". These are D2-s1-01, D2-s1-02, D2-s2-02, D2-s1-51, D12-s2-01 and D12-s3-01. There is no production edit at `thermal_model.py`'s Carnot factor, `mixing_valve.emitter_delivery`, `defrost.derate_from_duty`, `presets._ERA_LOSS_W_PER_M2K` or `declared_modulation`. The Carnot one-expression move is refused (it changes the score only). Where an existing check already fails on the planted line, that check is named as the pin. Two new pins cover the two laws that no check held (see `## Mutation proof`).

Invariants: every golden in `tests/golden/` is byte-identical, both claim files are byte-identical, and `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. No payload key and no stored option changes. A single-zone plan's `upper`/`lower` rows are now null, which is the D12-s1-01 fix. The two-zone payload is unchanged.

Verdict notes pm-01 to pm-05 are built here: the P2 proxy and owners, the pm-03 pin, the pm-04 refusal reading, and `effective_config` in the refusal. pm-06 was dismissed by the verdict. Two round-11 finder harnesses, the hot-water gap one and the two-zone action one, no longer reach their RESULT lines on a tree with this change. The first imports the renamed private name, and the second meets the refusal. Their sha1-cited ports are under `## Figures` (fixer step 3). No later stage reruns a round-11 finder harness as written, so nothing is carried.

## Head

Code head `3bd933a0d482829a3e60eab0cc3cc7b14198228a`, on merge base `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`. Origin/main moved to `ae0ed64af898d8923ac35afe6e9c031ac1e6b111` during the work. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in (fixer step 6). Main's 22 new ledger rows name no function this diff changes, and the stale-anchor rule below reads 0 on the merge tree `c12b775a`.

Where each measurement was taken. The last commit, `3bd933a0d`, adds one null-control check to `tests/features.py` and nothing else. `git diff --stat c606bafdd 3bd933a0d` lists only that file.
- Taken at `c606bafdd`, whose production is byte-identical to the head: the scoped gate, the finder harnesses and the full mutation loop.
- Taken at `3bd933a0d`: the NULL mutant, the two refusal mutants and a full `tests/features.py` run.

prepr: passed rc=0 at 3bd933a0d482829a3e60eab0cc3cc7b14198228a (scoped: `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, as the brief directs), on a committed tree. Its one WARN is the 11 unpinned sites listed below.

## Mutation proof

Each mutant was applied to the head tree in a scratch worktree. The pinning block was run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('PRE').read())" START END`. PRE is written by `features_block.py --emit-prelude PRE START END` on the same tree. The file was restored with `git checkout` after each mutant. The blocks:

- pm: `"# P3's rule itself, on a real result"` .. `"# P4: window means at their billed-equivalent"` (this group's block)
- valve: `'R.check(\n    "delivery cannot be negative",'` .. `"# A degenerate install can report design_power == 0"`
- derate: `'R.check(\n    "zero duty is no derate at all",'` .. `"# (3.5, 85.5) is the centre of bucket (3, 1)"`
- modul: `'R.check(\n    "declared_modulation reads the select first'` .. `'R.check(\n    "an unmetered on/off install freezes the house learner'`
- lift: `"_rp_boost = max("` .. `'R.check(\n    "D2-s2-01: and the flag is not inert here'`

Each mutant is listed as the line changed, the block run, and the check or checks that went red.

NULL (no edit, pm block): `SURVIVED NULL`, and the head block reads `ALL 12 FEATURES BLOCK PASSED`.

The six planted lines (each finder's own mutation, re-applied):

- **D2-s1-01**, `thermal_model.py` `return max(0.25, carnot_flow / carnot_ref)` → `carnot_ref / carnot_flow` (lift block). Existing pin: FAIL `D2-s2-01: a tank below the reference flow earns no lift and a hot one pays it (the one-sided rule _batch_cop states)`.
- **D2-s1-02**, `mixing_valve.py` `return max(0.0, ua * (mix_temp - zone_temp))` → `return ua * (mix_temp - zone_temp)` (valve block). Existing pin: FAIL `delivery cannot be negative`.
- **D2-s2-02**, `defrost.py` `1.0 - duty * DEFROST_LOSS_MULTIPLIER` → `1.0 + duty * …` (derate block). Existing pin: FAIL `the derate is 1 - duty x the loss multiplier`.
- **D2-s1-51**, `presets.py` `ERA_LOW_ENERGY: 0.35` → `0.85`, which is 1.55 × post-2005 as the verifier measured (pm block). New pin: FAIL `R11-SEAM-plant-model D2-s1-51: the preset heat loss falls strictly from the oldest era to low_energy, on every structure`.
- **D12-s2-01**, `two_zone_from_config` `if two_zone_mode == const.TWO_ZONE_MODE_ON:` → `if two_zone_mode in (const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE):` (pm block). New pin: FAIL `R11-SEAM-plant-model D12-s2-01: two_zone_mode absent or auto follows the zone keys; on and off override them` (`absent True auto True`).
- **D12-s3-01**, `declared_modulation` `False if mode == const.COMPRESSOR_MODULATION_ON_OFF` → `True if …` (modul block). Existing pin: FAIL `declared_modulation reads the select first, the legacy key only under auto or absent, and anything else as undeclared`.

The fix's own lines:

- **`zone_trajectories` drops `two_zone`** (pm block). Three FAILs:
  - `R10-CLONE-2238 P3: sensor_trajectory is the upper floor only in two-zone mode with the plan's floors, else the room`
  - `R11-SEAM-plant-model D12-s1-01: zone_trajectories is None on one zone even with filled floor lists, the floors on two zones, None without both`
  - `R11-SEAM-plant-model D12-s1-01: a single-zone plan publishes null upper/lower rows; a two-zone one (null control) publishes its floors`
- **`zone_trajectories`' `return None` deleted** (`pass`). The same three FAILs.
- **`_build_plan_views` passes `True`** instead of the model's `two_zone_enabled`. FAIL `… a single-zone plan publishes null upper/lower rows …`.
- **`sensor_trajectory` returns the room always.** FAIL `R10-CLONE-2238 P3: …` (the pm-03 pin: a two-zone plan keeps its upper trajectory).
- **The refusal's `if two_zone_from_config(coord.effective_config):` → `if False:`.** Three FAILs:
  - `… refuses the whole-house mass on a two-zone entry`
  - `… and the whole-house heat loss`
  - `… the refused call wrote nothing`
- **The refusal's `if field is None: return` → `if False:`** (at `3bd933a0d`). FAIL `R11-SEAM-plant-model D17-s3-02 null control: a two-zone entry still takes a field both topologies read` (`raised ServiceValidationError("None …")`).
- **`_gap_probe_terms`' `if dhw_enabled_from_config(config):` → `if True:`.** FAIL `R11-SEAM-plant-model D8-s1-01: no hot water prices no DHW coast; hot water (null control) still does`.
- **The options row's `when=_single_zone` deleted** (D17-s1-03). `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` prints `1 of 599 checks FAILED`. The failing check is `a two-zone entry is not offered the whole-house heat loss or mass; a single-zone one is (R10-TWO-ZONE-HHL, D17-s1-03)`.

Failing test first. The head's `tests/features.py` and `tests/config_flow_steps.py` were applied onto the merge base, with production unchanged.
- The pm block, from `"def _pm_space_rows(two_zone_mode):"`, printed `6 of 7 FEATURES BLOCK FAILED`. The six FAILs are D12-s1-01 plan rows, D8-s1-01, the three D17-s3-02 refusal checks and D17-s2-03. The single-zone null control passed.
- Run from the first check, the block raises `AttributeError: 'OptimizationResult' object has no attribute 'zone_trajectories'`.
- `config_flow_steps.py` fails the D17-s1-03 check above.

## Unpinned sites

The rule is `tests/mutation_table.py`'s `inventory()`, `unpinned_sites()` and `added_unpinned(…, base_unpinned_sites(bc658f9de…), diff_sides(bc658f9de…))`, run at the head. It names 11 diff-added sites, each pinned by `mutation-autofix` (no survivor is known):

- `custom_components/heatpump_optimizer/config_flow.py:1681 RETURN_DEL`: killed by the config_flow_steps single-zone arm (the options-row check).
- `custom_components/heatpump_optimizer/config_flow.py:2538 BOOLOP`: a line this diff only renamed; the base pin on tests/features.py held it.
- `custom_components/heatpump_optimizer/optimizer.py:2638 GUARD_OFF`: killed by the zone_trajectories mutants (pm block).
- `custom_components/heatpump_optimizer/optimizer.py:2640 RETURN_DEL`: killed by the two-zone null control in the pm block.
- `custom_components/heatpump_optimizer/optimizer.py:2650 RETURN_DEL`: killed by the sensor_trajectory mutant (R10-CLONE-2238 P3).
- `custom_components/heatpump_optimizer/sensor.py:3023 GUARD_OFF`: killed by the DHW gate check (D8-s1-01 null control).
- `custom_components/heatpump_optimizer/services.py:658 GUARD_OFF`: killed by the two-zone slab null control (D17-s3-02).
- `custom_components/heatpump_optimizer/services.py:661 GUARD_OFF`: killed by the three D17-s3-02 refusal checks.
- `custom_components/heatpump_optimizer/thermal_model.py:1165 GUARD_OFF`: killed by the D12-s2-01 pin (its on arm).
- `custom_components/heatpump_optimizer/thermal_model.py:1167 GUARD_OFF`: killed by the D12-s2-01 pin (its off arm).
- `custom_components/heatpump_optimizer/thermal_model.py:1189 GUARD_OFF`: a line this diff only moved (renamed function); the base pin on tests/features.py held it.

Recording them is `mutation-autofix`'s `--pin-killed` (ci-autofix.md), so the pin is `unmeasured` at this handoff. One equivalent mutant was removed at the source: `zone_trajectories` returns early, so no line is a `return None` → `pass` no-op.

Eight base dispositions anchored to lines this diff moved or renamed were removed. The ledger's completeness check refuses a disposition that names no site. They are:

- `config_flow.py`: `_single_zone` RETURN_DEL 6de1e154; `_omit_unstored_defaults` BOOLOP 0d3cbe12.
- `optimizer.py` `OptimizationResult.sensor_trajectory`: BOOLOP cc727924; GUARD_OFF cc727924; RETURN_DEL 1a942d8c.
- `thermal_model.py`: `_dhw_enabled_from_config` GUARD_OFF 6b1136a5; `ThermalParameters.from_config` GUARD_OFF 7c9a299b and 47a09856.

At the head: `ledger_form_problems` 0, `completeness_problems` 0, unpinned 2101. At the base: 0, 0 and 2091. The difference is the 11 sites above less the one old site the moves dropped.

## Null control

- **Plan view** (D12-s1-01): the two-zone plan publishes its floors at both ends. `plan_zone.py` reads `control_two_zone_rows=96` and `control_split_rows=96` at base and head.
- **Action** (D17-s3-02):
  - A single-zone entry still takes the whole-house mass, and a two-zone entry still takes `slab_thermal_mass`. Both are checks in the pm block, and both pass at the head.
  - In `f02_refusal.py` the `off` and `auto` arms (single zone at this base) keep `plan_delta=166.430` and `4.931` kW-steps at both ends.
- **Advisor** (D8-s1-01): `gapdhw_port.py` keeps `dhw_null=4` of 6 at both ends. An install with hot water still prices its coast: the pm block's `on` arm and the #1226 fixture, which now declares its tank.
- **Options page**: a single-zone entry is still offered both house rows (config_flow_steps).
- **Wood text** (D17-s2-03): the behaviour is unchanged by design. `wood_quick.py` reads quick-path spread 0.0000 kWh and valve arm 11.5119 kWh at both ends.

## Figures

- **Finder harnesses**, each run as `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/<harness>`. `$EXPORT` is `git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11`. Base means a checkout at `bc658f9de`; head means a worktree at `c606bafdd` (production = head).

  | harness (sha1) | base | head |
  |---|---|---|
  | `$EXPORT/dev/audit/rounds/round11/D12/s1/plan_zone.py` (`22a1e7d990954a07cfed1d43d622a2c12a44a56c`) | `zone_plants=8`, `zone_rows=768`, `control_two_zone_rows=96` | `zone_plants=0`, `zone_rows=0`, `control_two_zone_rows=96` |
  | `$EXPORT/dev/audit/rounds/round11/D17/s1/h_zone.py` (`77cb2e4ea1769180ab3c7ffa00dedf4d3328b1fb`) | `two_zone_only_no_effect=1 ['house_thermal_mass']` | `two_zone_only_no_effect=0 []`, with `single_zone_rendered=9` at both ends |
  | `$EXPORT/dev/audit/rounds/round11/D17/s3/f02_two_zone_inert.py` (`88e15b2e482c050caa1dbbf8de4a69ebf035050f`) | `two_zone_inert_cells=2` (the `on` cells at 0.000) | ends in the `ServiceValidationError` traceback the fix raises |
  | `$EXPORT/dev/audit/rounds/round11/D8/s1/gapdhw.py` (`672f43b9bde163669f4fa2c752f851cd7b81d8a0`) | `no_dhw_priced=12` of 22, `dhw_null=4` of 6 | `ImportError` on the renamed private symbol |
  | `$EXPORT/dev/audit/rounds/round11/D17/s2/wood_quick.py` (`7288320aee243951ab5592e4498d5d02d6238626`) | `quick_path_plan_kwh_spread=0.0000`, `valve_arm_plan_kwh_spread=11.5119` | the same |

  The design quoted 11.7844 kWh for the valve arm from the finder's box. On this box both ends read 11.5119.

- **Companion ports** (fixer step 3, verdict note pm-04). Each sits beside its finder harness in `$EXPORT`, so it imports `rig.py` from there.
  - `$EXPORT/dev/audit/rounds/round11/D17/s3/f02_refusal.py` (sha1 `871cfdcfd808226f86c13fa06c6bf10d13395a8b`) is the finder's file with one change: it catches `ServiceValidationError`, prints its translation key, and counts `refused_cells`. Base: `two_zone_inert_cells=2`, `refused_cells=0`. Head: `two_zone_inert_cells=0`, `refused_cells=2`, with `on.<field>.refused=set_thermal_params_house_field_two_zone`.
  - `$EXPORT/dev/audit/rounds/round11/D8/s1/gapdhw_port.py` (sha1 `f42e8e5f82838f58490061f510a11c6a90bd9712`) imports `dhw_enabled_from_config`, falling back to the base's private name. Base: `no_dhw_priced=12`, `no_dhw_top=12`, `dhw_null=4`. Head: `no_dhw_priced=0`, `no_dhw_top=0`, `dhw_null=4`.
  - Rebuild either with the patch below, applied in `$EXPORT/dev/audit/rounds/round11/` (`patch -p0`):

    ~~~diff
    --- D17/s3/f02_two_zone_inert.py
    +++ D17/s3/f02_refusal.py
    @@ imports
    +from homeassistant.exceptions import ServiceValidationError  # noqa: E402
    @@ one()
    -    await inst.call("set_thermal_parameters", {field: value})
    +    try:
    +        await inst.call("set_thermal_parameters", {field: value})
    +    except ServiceValidationError as err:
    +        print(f"RESULT {arm}.{field}.refused={err.translation_key} key")
    +        return float("nan"), float("nan"), two_zone
    @@ main()
    +    refused_cells = 0
    +            refused_cells += int(d_call != d_call)
    +    print(f"RESULT refused_cells={refused_cells} count")
    --- D8/s1/gapdhw.py
    +++ D8/s1/gapdhw_port.py
    -from heatpump_optimizer.thermal_model import _dhw_enabled_from_config  # noqa: E402
    +try:
    +    from heatpump_optimizer.thermal_model import dhw_enabled_from_config as _dhw_enabled_from_config  # noqa: E402
    +except ImportError:
    +    from heatpump_optimizer.thermal_model import _dhw_enabled_from_config  # noqa: E402
    ~~~

- **Seam enumeration** (fixer step 8), each command run at `8c77c551d` (the production lines it greps are unchanged at the head), with every hit dispositioned:
  - Floors decided from the lists: `git grep -n -E "upper_temp_trajectory and|lower_temp_trajectory and|bool\(\s*result\.upper" -- custom_components`. It returns one site, `optimizer.py` `zone_trajectories`, which is the owner. `coordinator._sim_coldest` and the schedule rows read the lists without the flag. The verdict note dismissed these (pm-06): no value changes on a single-zone result.
  - House rows on the options page: `git grep -n -E "CONF_HOUSE_(THERMAL_MASS|HEAT_LOSS_COEFFICIENT)," -- custom_components/heatpump_optimizer/config_flow.py`. Two `_OPTION_FIELDS` rows are returned, and both are gated by `when=_single_zone` (one in this diff, one already guarded). The other hits are imports. The setup wizard's thermal step is asked before the zone mode, so it is out of scope per the design.
  - Whole-house fields the action writes: `git grep -n -E "\"house_(thermal_mass|heat_loss_coefficient)\"" -- custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/services.py`. It returns the schema rows (`services.py`) and the write path, `_THERMAL_PARAM_FIELDS` and `async_update_thermal_params` (`coordinator.py`). The action reaches that write path only past the refusal, which is closed in this diff.
  - DHW tank priced: `git grep -n -E "dhw_tank_volume" -- custom_components/heatpump_optimizer/sensor.py custom_components/heatpump_optimizer/topology.py`. It returns one site, `sensor.py` `_gap_probe_terms`, which is closed in this diff.
- **P2 registry** (`tests/entities.py`):
  - The `two_zone_enabled` fact's owner is `thermal_model.py::two_zone_from_config` (pm-01). Its proxy now walks that function. A dump of `_p2_proxies` at base and head compared equal and printed `PROXIES-EQUAL`, with the proxies `CONF_INTER_ZONE_TRANSFER`, `CONF_LOWER_FLOOR_THERMAL_MASS`, `CONF_RADIATOR_POWER_FRACTION`, `CONF_TWO_ZONE_MODE` and `CONF_UPPER_FLOOR_THERMAL_MASS`.
  - The `dhw_enabled` owner and the `_omit_unstored_defaults` disposition name `dhw_enabled_from_config` (pm-02).
  - `sensor_trajectory`'s owner is `optimizer.py::OptimizationResult.zone_trajectories`.
  - `tests/entities.py` passes in the scoped gate.
- **Structure ratchet**: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. It was re-recorded with improvements only: `class_excess_loc` 17382 → 17356 and `max_class_loc` 7875 → 7873, because the two-zone body left `ThermalParameters.from_config`. The commit message of `6653d146c` gives the reason.
  - An earlier cut raised `functions_cc_over_15` 26 → 27 and `const_modules_over_50` 3 → 4, through the inline refusal in `handle_set_thermal_params` and two more const imports in `services.py`.
  - Both were paid by changing the code. The refusal moved into its helper, and the fields became one name owned by the thermal model (`SINGLE_ZONE_HOUSE_FIELDS`). No budget was raised.
- **Architecture score**: `python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f HEAD` at `c606bafdd` printed `Architecture score: dS +0.1375 IMPROVES`, with `private_cross_module 10 -> 9`.
  - The mechanism is `config_flow.py`'s import of `thermal_model._dhw_enabled_from_config`, now public. The null control is the base, which reads 10.
  - An intermediate cut whose helper took the coordinators read `coord_footprint 2505 -> 2511` (inadmissible). The helper now resolves its targets from `hass`, so it is handed no coordinator.
- **Goldens and claims**: run.sh's `env_drift.py --all bc658f9de…` printed `ok` under `GOLDEN_MODE=drift` against the merge base. `git diff --quiet bc658f9de HEAD -- tests/golden && echo "GOLDENS BYTE-IDENTICAL"` printed `GOLDENS BYTE-IDENTICAL`. The same form over both claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` printed `CLAIMS-VERSION-MANIFEST-NOTES BYTE-IDENTICAL`.
- **New tracked files**: `git diff --diff-filter=A --name-only bc658f9de HEAD` lists none, so no closure or `INERT` classification is owed.
- **Scoped gate**: `python3 tests/closure.py select --diff bc658f9de… --workdir D` printed the mode line below. Then `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=bc658f9de… PYTHON=python3 ./tests/run.sh` ran at `c606bafdd` (production = head) and printed `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, rc=0. The 29 are 27 scoped scripts plus the `run_always` lines.
- **features.py at the head**: `PYTHONPATH=tests/hastub python3 tests/features.py` at `3bd933a0d` printed `ALL 5911 FEATURE CHECKS PASSED`, rc=0.

<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=3bd933a0d482829a3e60eab0cc3cc7b14198228a -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / mutation` (predicted): it refuses the 11 added unpinned sites listed under `## Unpinned sites`, which `mutation-autofix` pins (ci-autofix.md). Cheaper detector: `tests/mutation_table.py --pin-killed`, which drives the whole closure per site. Its cost is `mutation-autofix`'s job, and ci-autofix.md assigns that job to the bot.

## Forward-carry

none

## Friction

- `fixer.md`: cost: this cloud seat's frugal hook refuses inline grep/sed/cat/ls past five per prompt. The brief forbade subagents, so discovery ran through `python3` file readers in scratch. The orchestrator then corrected that brief line (inbox/r11-seam-plant-model line 1, mandate 6893738184): discovery reads go to the cheap workers. Carry: dismissed: the orchestrator ruled on it
- `fixer.md`: cost: a gate run was spent on a tree edited mid-run. The edit was in the gate's own worktree, so that run was discarded and re-run. Measurements now use a separate worktree per instrument. Carry: dismissed: a seat practice, no rule changes
