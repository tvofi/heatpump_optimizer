R10-TWO-ZONE-HHL: the two carries on the whole-house heat-loss coefficient (`house_heat_loss_coefficient`) in two-zone mode, in the order Carry 2 sets: the sysid precondition first, then the options-flow hide.

- Carry 1 (plan-energy probe: hide or label the field on two zones): built as a hide, section (2) below; its control and null control are the `opt_thermal_model` checks under `## Figures` and `## Null control`.
- Carry 2 (R10-UX-HEALTH part 3: the sysid step sizer first, then the hide): (1) built in `HousePlant.of_params`, section (1) below; (2) is Carry 1's hide, built after it in this diff. Its control is the harness's `two_zone_sysid_steps` line, re-measured below.

**(1) The sysid sizer, re-measured at the merge base.** The carry's figure (1.738 kW at 0.1, 3.386 kW at 0.4, none at 1.0 "identical to single zone") was the harness, not production: it built a bare `SystemIdentification()` and never called `arm`, so `_two_zone_plant` stayed `None` and it measured the single-zone sizing path in two-zone mode. Production arms first (`sysid.arm_from_config` -> `SystemIdentification.arm`, which keeps a two-zone plant in `_two_zone_plant`), and the armed sizer already rolls the step out on `ThermalModel(two_zone_plant)` (#1524), whose loss is the zones'. At the merge base, the armed sizer's step does not move with the coefficient (figures below). What still carried the whole-house figure on two zones was the plant record itself: `HousePlant.of_params` built `ua` from `heat_loss_coefficient` and `capacity` from `room_thermal_mass` with no two-zone branch, read by the sizer's `ua > 1e-6` gate in `_begin_step_phase`, the degenerate-house guard in `_predict_step_excursion_plant` and the one-state comparison `_size_step_power` logs. The fix gives `of_params` its two-zone branch: `ua` is `house_heat_loss_base * house_heat_loss_scale` (the zones' loss with the learned split, the one owner of "the loss the dynamics use"; single zone it is `heat_loss_coefficient`, unchanged) and `capacity` the two zones' mass, as `arm` already seeds the fit's prior. Sysid now computes from the zone model it is given, with no reader of the whole-house figure left on two zones.

**(2) The hide.** The thermal-model page's `house_heat_loss_coefficient` row carries `when=_single_zone`, the registry's existing reveal mechanism (as the wood block uses `wood_furnace_on`); `_single_zone` is `not ThermalParameters.from_config(config).two_zone_enabled`, the model's own resolution of the mode, so an `auto` entry follows the zone keys as the solve does (the same call `config_flow` already makes for the flow write target, D12-01). Hidden, not cleared: `_clear_absent` walks only rendered rows, and the row is `_SUGGESTED`, never cleared, so the stored value survives a two-zone save and reappears if the entry goes back to one zone (pinned below). Hide over relabel: a relabel would still render an input that changes nothing, which is what Carry 1 asks to stop.

Alternatives: (a) hide alone, refused by Carry 2 and unnecessary now that the record is two-zone; (b) a two-zone branch inside `_size_step_power` instead of `of_params`, which would leave the record the coordinator builds still describing a house the model does not run, and duplicate the zone sum `arm` already owns; (c) relabel, rejected above.

Reader census (step 8): the rule `grep -rn --include=*.py "\bheat_loss_coefficient\b" custom_components/ | grep -v "house_heat_loss_coefficient\|effective_heat_loss_coefficient\|tank_heat_loss_coefficient"` returns every attribute reader. Disposition of each one reached from a two-zone configuration: `sysid.HousePlant.of_params`: closed in this diff. Already branched on `two_zone_enabled` (zones read instead): `coordinator._house_loss_terms`, `_space_demand_kw`, `_house_heat_loss_anchor`, `optimizer._floor_demand_at_target`, `_house_ua_kw_per_c`, `slab_settlement_cap`, `thermal_model.house_heat_loss_base`, `_valve_draw_circuits`, `_simulate_step_single` (single-zone step only), `_substeps_and_loss`, `battery` storage build, `sysid._held_state`, `sysid.arm` prior, `sysid.adoption_decision`. Inert by form: `optimizer.optimize`'s `forecast_heat_loss_factors` is `effective(base)/base`, and `effective_heat_loss_coefficient` is multiplicative in its base, so the ratio does not depend on it. Constructions, not readers: `sysid._sizing_model`, `_candidate_model`, `optimizer` line building `heat_loss_coefficient=u_up + u_lo`, `thermal_model` builders, `mixing_valve` parameter. The service `set_thermal_params` still accepts the key (it writes the parameter, which on two zones nothing reads); not a UI offer, left alone.

Carry 1's control and null control, and Carry 2's control, are figures below. No carry here waits on an owner or orchestrator ruling.

## Head

`5988ba9079b98b88c2310daa8a3b10997759cf10`. Merge-resolution only: the reviewed head is `53ce1267c758ae81bd21af1a0d7eba80bc9223c8`; the change over it is a merge of origin/main (first `d1e7dbbbbe3339de86f4651fdbd97d00a12716b2`, then `2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e`), whose one textual conflict, `tests/features.py`, is resolved by keeping both sides' trailing blocks (this PR's R10-TWO-ZONE-HHL checks, then main's R10-PROD-RESIDUE-PINS checks, each closed by its own `)`). No other file was edited by hand: `git diff -U0 5988ba9079b98b88c2310daa8a3b10997759cf10^1 5988ba9079b98b88c2310daa8a3b10997759cf10` shows no conflict marker, and `tests/entities.py` auto-merged.

The PR's own diff is unchanged: `git diff --stat 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e 5988ba9079b98b88c2310daa8a3b10997759cf10` reads `8 files changed, 149 insertions(+), 17 deletions(-)`, the same as `git diff --stat $(git merge-base 53ce1267c758ae81bd21af1a0d7eba80bc9223c8 2a9cd3476dae) 53ce1267c758ae81bd21af1a0d7eba80bc9223c8` before the merge. Delta over the reviewed head, `git diff --stat 53ce1267c758ae81bd21af1a0d7eba80bc9223c8 5988ba9079b98b88c2310daa8a3b10997759cf10`: `47 files changed, 1323 insertions(+), 170 deletions(-)`, all of it main's merged commits except the `tests/features.py` resolution. origin/main has since moved to `ce7a6bac75041b803158178ba2282082d7747c7e` (records and `tests/closures.json` only; `git merge-tree --write-tree origin/main HEAD` is clean), not merged here; `tools/pr/prepr.sh` ran at `5988ba9079b98b88c2310daa8a3b10997759cf10` against `2a9cd3476dae`.

Figures from the reviewed body below (mutation proofs, harness, null control) describe `53ce1267`'s PR diff, which is byte-identical in production and test files here; the scoped gate was re-run through `prepr.sh` at this head. VERSION, claim files and budgets are untouched. Toolchain: numpy 2.5.4, scipy 1.18.1, matching `tests/requirements-ci.txt`.

## Mutation proof

Production lines reverted in a detached worktree at the head, closure scripts run:

- `sysid.HousePlant.of_params` back to `ua=p.heat_loss_coefficient * p.house_heat_loss_scale, capacity=p.room_thermal_mass` -> `python3 tests/features.py`: `FAIL R10-TWO-ZONE-HHL a two-zone HousePlant is the zones' loss and mass, whatever the whole-house coefficient` (1 of 4779 FEATURE CHECKS FAILED); its null-control check stays ok.
- `when=_single_zone` dropped from the `house_heat_loss_coefficient` row -> `python3 tests/config_flow_steps.py`: `FAIL a two-zone entry is not offered the whole-house heat loss; a single-zone one is (R10-TWO-ZONE-HHL)` (1 of 538 checks FAILED).
- `_single_zone`'s `return` replaced by `pass` (the predictor's RETURN_DEL site) -> `python3 tests/config_flow_steps.py`: `FAIL a two-zone entry is not offered the whole-house heat loss; a single-zone one is (R10-TWO-ZONE-HHL)` and `FAIL every field every page renders is a registry row for that page` (2 of 539 checks FAILED).

## Null control

At the merge base the harness's `two_zone_plant` line reads three distinct records across the 0.1/0.4/1.0 sweep, one per coefficient; at the head one. Single zone is unchanged at both ends: `single_zone_sysid_steps=1.738,3.386,None` and `single_zone_max_dkw=4.921374` at base and head, and the single-zone `HousePlant` follows the coefficient (`R10-TWO-ZONE-HHL null control` check in `tests/features.py`, three distinct `ua`). The options page shows the field on a single-zone entry (same check as the hide, its `one_zone_keys` arm).

## Figures

Toolchain: numpy 2.5.4, scipy 1.18.1, matching `tests/requirements-ci.txt`; `tools/audit/seat/cloud-setup.sh --check` OK.

Harness `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_two_zone_hhl_inert.py`, ported in this diff to drive `arm` (the production path) and to add the heavy-zone and plant lines; the base column is this head's harness file run in a worktree at the merge base (the base's own copy raises `TypeError: SystemIdentification._size_step_power() takes 6 positional arguments but 10 were given`, its call predating R10-CEILING-PROBE's `HousePlant` argument):

| line | merge base | head |
|---|---|---|
| `two_zone_max_dkw` | 0.000000 | 0.000000 |
| `two_zone_max_dcost` | 0.000000 | 0.000000 |
| `single_zone_max_dkw` (null) | 4.921374 | 4.921374 |
| `two_zone_sysid_steps` | None,None,None | None,None,None |
| `two_zone_heavy_sysid_steps` | 2.603,2.603,2.603 | 2.603,2.603,2.603 |
| `two_zone_plant` | [(0.1, 10.0), (0.4, 10.0), (1.0, 10.0)] | [(0.33, 2.26)] |
| `single_zone_sysid_steps` (null) | 1.738,3.386,None | 1.738,3.386,None |

Carry 2's control ("a single distinct value in two_zone_sysid_steps") holds at both ends of the armed path; on the probe's config no step fits at any coefficient (a uniform `None`), so the heavy-zone line (`HEAVY`: both zone masses 4.0 kWh/°C) is the non-vacuous one: one distinct fitted step. The defect the head removes is the `two_zone_plant` line.

- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` Every script in `scope.run` ran ok at the head under `GATE_SCOPE=auto GOLDEN_MODE=drift`, `tests/entities.py` included after the round-trip fix (`ALL 2602 ENTITY CHECKS PASSED; the scoped run was cut by a 30-minute local limit after tests/entities.py's first, pre-fix red, and the scripts after it were run singly: finite_boundary, golden, harness_headers, deployment_shape, each exit 0`).
- `python3 tests/env_drift.py --all origin/main`: ok (no golden moved; no claim file touched).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: one unpinned site added (below), no closures, fast, governance or instrument red predicted.

## Unpinned sites

- custom_components/heatpump_optimizer/config_flow.py:1571 RETURN_DEL (`_single_zone`'s return): pinned by `mutation-autofix`; killed locally by `tests/config_flow_steps.py` (mutation proof above), so its lane records a kill, not a survivor.

## Red checks

At `5988ba9079b98b88c2310daa8a3b10997759cf10`: `tools/pr/prepr.sh` rc=0 (`MODE: SCOPED`), `python3 tests/structure.py` passes (`STRUCTURE RATCHET PASSED`; the resolution adds no metric movement), no concluded red check at this head. The predicted `mutation` red (one unpinned site, `_single_zone`'s RETURN_DEL) is already pinned in-tree by the `_single_zone.RETURN_DEL.6de1e154.json` record in this diff; the earlier `tests/entities.py` red was answered before the first handoff, as stated in the reviewed body.

## Forward-carry

none

## Friction

none
