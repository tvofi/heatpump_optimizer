fix(R11-LATE-P2-ZONE-GATE): every two-zone presence reader takes the one rule

Group R11-LATE-P2-ZONE-GATE (round 11, late P2 sweep, issue #3744 left open). Whether an install runs two zones has one owner, `thermal_model.two_zone_from_config`; two readers in the action and the payload answered it from something else:

- `set_thermal_parameters` accepted a floor's mass, the inter-zone transfer and the radiator share on an install whose mode keeps it one zone, where nothing reads them. It now refuses them before any write (`services._refuse_zone_fields_on_one_zone`, translation key `set_thermal_params_zone_field_one_zone` in strings, en, de, sv). It mirrors the D17-s3-02 house-field refusal beside it. The refusal is judged on the config the call leaves (`{**effective_config, **asked}`): under `auto` these keys are the presence that turns the model two-zone, so on an auto one-zone install the call is the switch and is still taken.
- The schedule rows took floor temperatures from the trajectories' truthiness. A one-zone solve fills both trajectories with the room's, so every row published a "floor" temperature. The rows now read `OptimizationResult.zone_trajectories` on the model's `two_zone_enabled`, which the thermal view already put in `data`, and publish `None` on one zone. `payload.ScheduleStep` declares them `float | None`. No reader of those row keys exists in `custom_components/` (www included) or in the tests.
- `thermal_model.TWO_ZONE_FIELDS` is the presence rule's key set. `two_zone_from_config` reads it, and the refusal reads it too, so the refused set is the rule's own output and no second list exists.
- P2 owners registry (`tests/entities.py`): `_p2_proxies` reads the constant's keys, so the `two_zone_enabled` rule stays live. The `sensor_trajectory` fact gains an `also` shape: a floor trajectory used as a decision test (`_p2_decides`). That shape returns only the owner at head and the two removed `coordinator.py` sites at the base (AST census below).

Alternatives considered: (a) a new `two_zone` argument to `_apply_result_payload`. It cost a coordinator-class line (`max_class_loc` and `class_excess_loc` +1) and edits to four test callers; reading the flag the thermal view published into `data` costs neither. (b) A refusal inside `async_update_thermal_params`. That would put a validation edge below the service handler, where the sibling D17-s3-02 rule and every other pre-write refusal of this action already live in `services.py`. (c) Refusing on the effective config alone. That breaks the auto-mode switch; mutant MUT-C below shows the null control catching it.

Prior BLOCKED.md: none. `git ls-remote origin` for `*zone-gate*` returned only `dispatch/fixer-r11-late-p2-zone-gate` and `handoff-wip/r11-late-p2-zone-gate-comms` at this seat's start, and neither carries a BLOCKED.md, so there was no option to take.

## Head

56ced7a0a949fc21cebbe74070de3e8565f3fc9b, on merge base 8890fc2bada17f6c7d8a6bbf03e6625a16a0967c (the origin/main tip at measurement). `git merge-tree --write-tree origin/main HEAD` exits 0, no conflict (2026-11-27T01:33Z). Round 2 adds one test-only commit on d554d42e9a; the production tree is d554d42e9a's.

## Round 2: answer to `Fix review: blocked d554d42e9a mutation-vacuous` (probe/rev-3925-84457bb5)

- Block, mutant F (delete `const.CONF_RADIATOR_POWER_FRACTION,` from `TWO_ZONE_FIELDS`, the reviewer's `ev/mut_F.patch`): the block now pins the four keys literally (`_zg_values`, written independently of `TWO_ZONE_FIELDS`). A new check asserts the presence rule's output over `coordinator._THERMAL_PARAM_FIELDS` equals that literal set, and the refusal loop and "wrote nothing" check drive the literal set rather than the rule's output. Under F, 3 of 18 FAIL: `the presence rule turns an auto config two-zone on each of the four zone keys, and on no other action field` [rule=3 keys, pinned=4], `set_thermal_parameters refuses radiator_power_fraction on a single-zone entry` [returned None instead of raising], `the refused calls wrote nothing` [options=['house_thermal_mass', 'radiator_power_fraction']]. The restored head: `ALL 18 FEATURES BLOCK PASSED`. The literal encodes a design choice, stated in the block's comment: the four keys are the two-zone model's own parameters; the census precondition still catches a key the rule starts reading.
- Mutants A to E re-run at 56ced7a0a9 with the same block command, each still failing: A 5 of 18 (the four refusals and "wrote nothing"), B 1 (`a single-zone plan's schedule rows publish no zone temperature` [rows=96 zoned=96]), C 1 (`null control: an auto one-zone entry takes a floor's mass…`), D 1 (`each floor's column is that floor's trajectory…`), E 1 (the rows check, rows=96 zoned=96).
- Not re-checked: whether F's deletion from the inline tuple survived at the base. The base had no check driving `radiator_power_fraction` on one zone (the finder's harness probes three fields), so the gap is older than this PR; this PR now pins it.
- Finding `_sim_coldest` (`coordinator.py`): dismissed in the verdict, no divergence. Carry: dismissed: no divergence — on one zone the floor lists equal the room trajectory, so min() is unchanged

## Mutation proof

Block command (MUTANT_CMD): `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<scratch>/zg_prelude.py').read())" "# D17-s3-02: on two zones the whole-house" "# D17-s2-03: quick setup's wood answers"`. The prelude was written by `features_block.py --emit-prelude <out> "# D17-s3-02: on two zones the whole-house" "# D17-s2-03: quick setup's wood answers"` at this head.

- MUT-A, delete `_refuse_zone_fields_on_one_zone(hass, params)` from `handle_set_thermal_params`: 5 of 15 FAIL. They are `set_thermal_parameters refuses {inter_zone_heat_transfer, lower_floor_thermal_mass, radiator_power_fraction, upper_floor_thermal_mass} on a single-zone entry` and `the refused calls wrote nothing`.
- MUT-B, `zones = result.zone_trajectories(True)` in `_apply_result_payload`: 1 of 15 FAIL, `a single-zone plan's schedule rows publish no zone temperature` [rows=96 zoned=96].
- MUT-C, refusal judged on `coord.effective_config` only: 1 of 15 FAIL, `null control: an auto one-zone entry takes a floor's mass, which makes its persisted config two-zone`.
- Failing test first: commit `test(R11-LATE-P2-ZONE-GATE): failing checks…` on the unfixed production tree gave 7 of 15 FAIL. The census precondition failed (no `TWO_ZONE_FIELDS`), as did the four refusals, "wrote nothing" and the rows check; the four null controls passed.

diff mutants: `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --report-only` printed no `SURVIVED` line at 6e6fac340a (the production and test tree of this head; 4bfaa3dad5 adds only the structure re-record). Its `--list` draws 18 mutants over coordinator.py, payload.py, services.py and thermal_model.py. The first run, before the last test commit, printed:
```
SURVIVED custom_components/heatpump_optimizer/coordinator.py:3147 CONST_SWAP  upper_temps = zones[1][1:] if zones is not None else [None] * n_steps
SURVIVED custom_components/heatpump_optimizer/payload.py:693 STMT_DEL  pass
SURVIVED custom_components/heatpump_optimizer/payload.py:694 STMT_DEL  pass
```
Each now has a killing check: `each floor's column is that floor's trajectory (precondition: the two floors differ somewhere)` and `a schedule row publishes exactly the keys ScheduleStep declares, on either topology`. prepr ran under PREPR_SKIP_CODE=1, so its own diff-mutant step is skipped and the line above is the brief's own `mutant_run.py` run.

## Unpinned sites

prepr's step 6d names four sites the diff adds with no `tests/mutation_ledger/` pin. Each one is killed by MUTANT_CMD and is pinned by `mutation-autofix`, whose lane mutates `custom_components/` and writes the `killed_by` record (`ci-autofix.md`; `--pin-killed` is that lane's, per fixer.md step 2):
- custom_components/heatpump_optimizer/services.py:662 BOOLOP: run by hand (`and` -> `or` in the `asked` filter), 2 of 17 FAIL: `R11-SEAM-plant-model D17-s3-02 null control: a single-zone entry still takes the whole-house mass` and `R11-LATE-P2-ZONE-GATE: a single-zone plan's schedule rows publish no zone temperature`. Pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/services.py:663 GUARD_OFF: killed in the diff-mutant run (no SURVIVED line). Pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/services.py:666 GUARD_OFF: killed in the diff-mutant run; the same predicate as MUT-C/MUT-A. Pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/thermal_model.py:1174 RETURN_DEL: killed in the diff-mutant run (`two_zone_from_config` returns None, so the census precondition and every refusal fail). Pinned by `mutation-autofix`.

## Null control

Round 2: the unmutated head 56ced7a0a9 runs the block at `ALL 18 FEATURES BLOCK PASSED`; that is the control for every mutant line above (each changes one production line and nothing else, driver `git diff` recorded per mutant). The finder's harness figures below are round 1's, at a production tree this round leaves unchanged.

Finder's harness `$EXPORT/dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py`, taken from 872510cd3e:dev/audit/rounds/round11/sweep/P2/D14-sweep-P2/probes_p2.py, sha1 5058a46432166867f8e75a5d4846acea20d0b752. Each end ran in a `git archive` export: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py`.

- Base fd93aa3e9b: `probes_failed=6 of 10`. All four zone seams FAIL: `_apply_result_payload (schedule upper/lower)` with 96 of 96 rows zoned, and `_THERMAL_PARAM_FIELDS.{upper_floor_thermal_mass, lower_floor_thermal_mass, inter_zone_heat_transfer}` accepted with plan delta 0.000 and 0.000 after restart.
- Base, `--perturb` (each seam handed its sibling's guard): `probes_failed=0 of 10`, so the probe reads the divergence and nothing else. `house_thermal_mass` on the same install moves the plan 45.771 kW-steps.
- Head 6e6fac340a (export at cd1ea3c9e4, the same production tree): `probes_failed=2 of 10`. The four zone seams pass (0 of 96 rows zoned; each field `accepted=False`). The two still failing are `_async_drive_pumps (VVC)` and `async_fold_draw_stats (draw label)`, DHW weekday-window seams outside this group's seam.
- Companion probe (scratch, one-off), every field the axis could hold, on a mode-off install: `radiator_power_fraction` at the base is accepted with plan delta 0.000 and restart delta 0.000, like the brief's three. That is why the refused set is the rule's four keys and not the brief's three. At the head it is refused with `set_thermal_params_zone_field_one_zone`. On an auto install with no zone key, `upper_floor_thermal_mass` at the base gives delta 0.000 and restart delta 56.365, with two_zone after restart True: the call is a topology switch, which the head keeps (MUT-C's null control).

## Figures

- Quantified set, the refused fields: rule `{k for k in coordinator._THERMAL_PARAM_FIELDS if thermal_model.two_zone_from_config({k: 1.0})}`, asserted equal to `TWO_ZONE_FIELDS` and non-empty by the block's census-precondition check (`tests/features.py`, "R11-LATE-P2-ZONE-GATE census precondition"). Its null: at the base the check failed because the constant was absent.
- Quantified set, the plan-floors decision sites: rule = every `If`/`IfExp` test or `BoolOp` operand in `custom_components/heatpump_optimizer/*.py` that is a bare `.upper_temp_trajectory`/`.lower_temp_trajectory` attribute (an inline `ast.walk` census, the same shape the new `also` matcher registers). Head: `optimizer.py:2705` ×2, the owner `OptimizationResult.zone_trajectories`. Base: those two plus `coordinator.py:3205` and `coordinator.py:3210`, which are closed in this diff. Kept as `entities.py`'s `P2 owners: sensor_trajectory` row.
- Quantified set, readers of the schedule rows' `upper_temp`/`lower_temp` keys: rule `git grep -n '"upper_temp"\|"lower_temp"' -- custom_components tests`. It returns only the writer in `coordinator.py`, so changing those keys to `None` breaks no reader.
- `python3 tests/structure.py`: no FAIL line at the head. At 6e6fac340a it read `gain module_excess_loc 21644 (budget 21646, -2)`; 4bfaa3dad5 records it (`--record`, rows moved named in the commit), the only row moved. The first fix commit read `class_excess_loc +1`, `max_class_loc +1` and `module_excess_loc +3`, paid by reading the published flag and by sharing one comment between the two topology field sets. No budget was re-recorded.
- `python3 tools/audit/archscore/score.py --diff fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5 --workdir <d>`: `MODE: SCOPED`; scope.run names 28 scripts.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at cd1ea3c9e4: `ALL 2786 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at cd1ea3c9e4: `ALL 6282 FEATURE CHECKS PASSED`. The block alone at 6e6fac340a, after the two added checks: `ALL 17 FEATURES BLOCK PASSED`.

- Round 2, the block at 56ced7a0a9: `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<scratch>/zg_prelude.py').read())" "# D17-s3-02: on two zones the whole-house" "# D17-s2-03: quick setup's wood answers"`: `ALL 18 FEATURES BLOCK PASSED`; under mutant F `3 of 18 FEATURES BLOCK FAILED`.
- Round 2, `python3 tests/structure.py` at 56ced7a0a9: `STRUCTURE RATCHET PASSED` (the commit touches only `tests/features.py`).

- Round 2, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <body>`: `PRE-PR: 56ced7a0a949fc21cebbe74070de3e8565f3fc9b 000000000000000000 rc=0 elapsed=80s`.

## Red checks

- `tests / mutation`: predicted red, not yet run (prepr step 6d `PREDICT tests / mutation ADDED UNPINNED`) for the four killed-but-unpinned sites under `## Unpinned sites`. The cheaper detector is prepr's step 6d itself, which caught it here before any CI run; its standing cost is under a second per prepr, already paid. The repair is `mutation-autofix`'s pin commit; no second countermeasure is owed, because the class is the one that lane exists for.

## Forward-carry

none

## Friction

none
