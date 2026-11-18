# R11-SEAM-plant-model: one predicate per plant question, and what remains of the law fixes at main

Extends the roster's architect note and ADR-008 (plan/r11 819aa2e354). Base: origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; the group has no `after` edge, so there is no predecessor head. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/`, `tools/` or `dev/`. Each finder harness was run at the base from a copy of `dev/audit/rounds/round11/` on plan/r11, venv-ci python.

## Findings at the base: six do not reproduce

The judge re-ran the D2 and D12 findings in the planted copy (`JUDGE.md`, "planted copy"). Main and the clean baseline 92d38ecb both carry the correct law:

| finding | base reading (finder harness) | code at base |
|---|---|---|
| D2-s1-01 | `D2/s1/batch_parity.py`: 0 mismatches on every arm | `thermal_model.py:3402` `carnot_flow / carnot_ref`, as the batch at `:4493` |
| D2-s1-02 | same run, two-zone valve arms 0 | `mixing_valve.py:144` `max(0.0, ...)` |
| D2-s2-02 | `D2/s2/m2_cop_laws.py`: `duty_law_mismatch=0`, frost ratio 0.7 | `defrost.py:205` subtracts |
| D2-s1-51 | `D2/leads/era_loss_order.py`: `cells_inverted=0`, ratio 0.636 | `presets.py:112` low_energy 0.35 |
| D12-s2-01 | `D12/s2/two_zone_auto.py`: `invented_zone_cells=0`, response 39.908 kWh | `thermal_model.py:1122` compares with ON only |
| D12-s3-01 | `D12/s3/modulation.py`: `on_off_clamped_cells=10`, failing 0 | `thermal_model.py:1473` on_off -> False |

No failing test can fail on today's code for these six, so the note designs no production change for them (stop rule: behaviour not stated precisely enough for a failing test). What it designs instead is the regression evidence in "Evidence". Because the Carnot factor is already right, the expected golden drift and the `claimed_drift.txt` claim go away.

Five reproduce: D12-s1-01 (`D12/s1/plan_zone.py`: zone_plants 8 of 8, 768 rows), D17-s1-03 (`D17/s1/h_zone.py`: `two_zone_only_no_effect=1 ['house_thermal_mass']`), D17-s3-02 (`D17/s3/f02_two_zone_inert.py`: 2 of 4 cells, mode `on` only; `auto` now resolves single-zone and moves 166.438), D8-s1-01 (`D8/s1/gapdhw.py`: no_dhw_priced 12 of 22, dhw_null 4 of 6), and D17-s2-03 (`D17/s2/wood_quick.py`; reading in the handoff line).

## Owning seam

`thermal_model.py` owns the plant-shape predicates (ADR-008 part 1). Callers only: `coordinator.py` (`_build_plan_views`), `optimizer.py` (`OptimizationResult`, which owns the trajectory choice, the `sensor_trajectory` P2 fact in `tests/entities.py`), `config_flow.py`, `services.py`, `sensor.py`, `quick_setup.py` and the text files. One owner per question, so there is no stop.

## Shape

1. **Two-zone, public.** `thermal_model.two_zone_from_config(config: Mapping[str, Any]) -> bool` gets the body of `thermal_model.py:1119-1135` unchanged, and `ThermalParameters.from_config` calls it. `config_flow._single_zone` (`config_flow.py:1665`) calls it rather than building a whole `ThermalParameters`. The other `from_config(...).two_zone_enabled` readers (`config_flow.py:2398`, `modbus_prefill.py:250`, `presets.py:317`) already agree, and they stay as they are: no finding gives them a new reader.
2. **Plan views (D12-s1-01).** `OptimizationResult.zone_trajectories(two_zone: bool) -> tuple[list[float], list[float]] | None` holds the one predicate `two_zone and self.upper_temp_trajectory and self.lower_temp_trajectory`, and `sensor_trajectory` (`optimizer.py:2629`) calls it. `_build_plan_views` (`coordinator.py:4856`) calls `result.zone_trajectories(ctx._thermal_params.two_zone_enabled)`, as the `sensor_trajectory` callers at `coordinator.py:10228` and `:10272` already pass the model's flag. The P2 owner in `tests/entities.py` ("sensor_trajectory" fact) moves to `optimizer.py::OptimizationResult.zone_trajectories`. Payload keys are unchanged, and a single-zone plan publishes `upper`/`lower` as null.
3. **Options page (D17-s1-03).** The `CONF_HOUSE_THERMAL_MASS` row (`config_flow.py:1865`) takes `when=_single_zone`, as its heat-loss sibling at `:1866` does. Its `strings.json` description adds that a two-zone house sets its masses on the Two-zone model page.
4. **Action (D17-s3-02).** `handle_set_thermal_params` (`services.py:643`) refuses before any write, the way the hot-water windows check refuses. For each target entry, `merged = {**entry.data, **entry.options}` (the shape of `services.py:910`), and if `two_zone_from_config(merged)` is true and the call carries `house_heat_loss_coefficient` or `house_thermal_mass`, it raises `ServiceValidationError` with a new translation key, `set_thermal_params_house_field_two_zone`. The error names the action's `upper_floor_thermal_mass`/`lower_floor_thermal_mass` fields and the options page's zone heat loss. `services.yaml` field help says the two fields apply to one zone only.
5. **Has hot water (D8-s1-01).** `_dhw_enabled_from_config` is renamed `dhw_enabled_from_config` (`thermal_model.py:1166`). Its readers are `config_flow.py:484` and `:2531`, `tests/config_flow_steps.py:6048`, and `tests/entities.py:3892`, `:3929`, `:3951` and `:19177-19183`. The new reader is `sensor._gap_probe_terms`: `dhw_extra_kwh` stays 0.0 unless `dhw_enabled_from_config(config)` is true (`sensor.py:3015`). This is the call that banks the `private_cross_module` fall under ADR-008. The red-team case `tools/audit/archscore/planted/redteam/45_shape_private_copy.py` edits the pinned tree, not this one, so it needs no change (no tooling edit).
6. **Quick setup (D17-s2-03).** Text only, per the routed decision below. The `wood_furnace` and `wood_buffer_tank` descriptions (config and options `quick_setup` steps in `strings.json`) name the conditions the base actually has: a throttling mixing valve in Options for the two-tank model (`thermal_model.py:385` `topology_layout`), and the external-heat detection switch for standing the pump down. The wording follows `buffer_tank`'s existing sentence. The `quick_setup.py:28-32` docstring claim that the probes are "the model's own gate" is corrected to match.

**Invariants.** Every golden in `tests/golden/` stays byte-identical, with no claim added. Neither claim file is touched (rule 3; `claim-files.md`). No payload key and no stored option changes. Defaults move nothing, so the release notes owe no upgrade step.

## Alternatives

- Empty `upper/lower_temp_trajectory` for single-zone solves at `optimizer.py:3908`, which is the convention of `wood_temp_trajectory` at `:3882`. Lost because `tests/golden.py:832` records both lists, which moves 36 single-zone fixtures (counted at the base) for a display fix.
- A `two_zone` field on `OptimizationResult`. Lost because it would be a second encoding of a fact the result's trajectories and the model's flag already carry: the P2 shape this group removes.
- Mapping the house fields onto the zones in the action (D17-s3-02). Lost because it invents a split between zones, and adding zone heat-loss fields needs a reset rule for `lower_floor_loss_ratio` (`thermal_model.py:597-604`), which the learners seam owns. That would give the group two owners.
- Gating the hot-water row in `topology.rank_sensor_gaps`. Lost because `tests/features.py:12344` drives that row with an unconfigured mapping. The coast term is `_gap_probe_terms`'s, and that is where the finder's own perturbation acts.
- One shared Carnot expression for `:3398-3402` and `:4482-4493`. Not counted: at the base the census (`tests/structure.py` `duplicate_clones`) lists seven clone classes and none in `thermal_model.py`, so `duplication_copies` reads 0.0, and the PLAN risk row's 43.0 % does not arise. Routed below.

## Sibling sites (commands)

- `grep -n "two_zone_enabled\b" custom_components/heatpump_optimizer/*.py`: every reader takes the model's flag except `coordinator.py:4856`. `binary_sensor.py:198` and `climate.py:249` read the payload key the coordinator publishes from the flag.
- `grep -n "when=_single_zone\|HOUSE_THERMAL_MASS\|HOUSE_HEAT_LOSS" custom_components/heatpump_optimizer/config_flow.py`: the house mass row is the only ungated house-level row. The setup wizard's thermal step (`:3083`) is out of scope: it is asked before `async_step_zones` decides the mode.
- `grep -n "dhw_tank_volume\|DHW_TEMP_ENTITY" custom_components/heatpump_optimizer/sensor.py custom_components/heatpump_optimizer/topology.py`: the `rank_sensor_gaps` rows (`topology.py:922-948`). Only the DHW row prices an unconfigured feature (the finder's seam rule reads the same).
- `grep -n "_THERMAL_PARAM_FIELDS" -A22 custom_components/heatpump_optimizer/coordinator.py`: only `house_heat_loss_coefficient` and `house_thermal_mass` are single-zone-only. `slab_*` is read on both topologies (`thermal_model.py:631`).

## Evidence, by file

- **Failing tests first** (`tests/features.py`, beside the #2238 P3 rule, `features.py:90269`): (a) a single-zone `OptimizationResult` with filled zone lists gives `zone_trajectories(False) is None`, and the published `space_plan` rows carry null `upper`/`lower`; (b) the options schema for `two_zone_mode: on` omits `house_thermal_mass`; (c) `set_thermal_parameters` with `house_thermal_mass` on a `two_zone_mode: on` entry raises the new key and writes no option; (d) `_gap_probe_terms` with no hot-water key returns `dhw_extra_kwh == 0.0`; (e) a strings test that both wood descriptions name the valve condition.
- **Finder harness at both ends**: `plan_zone.py` 8 -> 0 with control rows 96 kept; `h_zone.py` 1 -> 0; `f02_two_zone_inert.py` reads refusal, not 0.000, on the `on` cells while the `auto` deltas are unchanged; `gapdhw.py` 12 -> 0 with dhw_null 4 kept (null control); `wood_quick.py` spread unchanged, valve arm 11.805 unchanged.
- **The six non-reproducing findings**: apply each planted line in a private copy, run `GATE_SCOPE=auto`'s scripts, and add a pin only where none fails. Candidates: a scalar/batch parity row in `tests/features.py` for the lift factor and `emitter_delivery`, the era-order monotone check, the duty law, and the `two_zone_mode` absent -> presence rule.
- **Mutation targets**: the `zone_trajectories` conjunction, the `when=_single_zone` row, the refusal's `two_zone_from_config` test, and the `dhw_enabled_from_config` gate in `_gap_probe_terms`.
- **Goldens**: `tests/env_drift.py` byte-identical, and both claim files byte-identical.

## Hot files and serial position

Edited: `thermal_model.py`, `optimizer.py`, `coordinator.py` (one line), `config_flow.py`, `services.py`, `services.yaml`, `sensor.py`, `quick_setup.py` (docstring), `strings.json`, plus `translations/en.json` and, for the new exception key, `translations/de.json`/`sv.json`. None of these four files is on the roster. `translations/en.json` sits on the config / product-text row. Not edited: `mixing_valve.py`, `defrost.py`, `presets.py`, `topology.py`, which can leave the group's files. The base fits PLAN's order: `inputs-guards` before plant-model on `thermal_model.py`, and `kernel-step` on `coordinator.py`/`sensor.py`. Open #3711 (`sensor.py`, `coordinator.py`, `strings.json`) and #3709 (`optimizer.py`) touch other functions, so they are a rebase, not a conflict. Carries: none owed or received. There is no p1/p2 split.

## Decisions routed (orchestrator)

1. Close D2-s1-01, D2-s1-02, D2-s2-02, D2-s1-51, D12-s2-01 and D12-s3-01 as not present at main, with their pins as the deliverable. Recommendation: yes. The group then drops the `N-wrong-law`/`N-table-value` work and the S6/T6 claim. The size may fall to M.
2. Carnot one-expression move: recommendation is no. There is no defect and no counted clone, and the twins' equality rests on BLAS order (ADR-006 part 3).
3. D17-s2-03, text versus making quick setup write `external_heat_detection_enabled` with the furnace. Recommendation: text. Writing the switch would flip detection on existing entries that re-run quick setup.

## Notes for the fixer

- Carry: R11-SEAM-plant-model (item pm-01): the P2 registry's `two_zone_enabled` proxy (`tests/entities.py:3885-3890`) walks `If` nodes inside `from_config`. Once the body moves to `two_zone_from_config`, check that the proxy still finds it, and set the owner to `thermal_model.py::two_zone_from_config`.
- Carry: R11-SEAM-plant-model (item pm-02): the `dhw_enabled` fact's owner string (`tests/entities.py:3929`) and the `_omit_unstored_defaults` disposition text name the old private name, so rename both.
