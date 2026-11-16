simulate_plan's comfort and hot-water fields were `vol.Coerce(float)` with no range, so every number selector on the service was a form hint the schema never held, and five of them (`min_temp`, `max_temp`, `comfort_weight`, `comfort_temp_night`, `dhw_min_temperature`) disagreed with the options flow. apply_manual_plan's slot and expiry examples were 2024 instants: sent verbatim the expiry was refused as not in the future. The same class held one more seam: set_away's `return_time` example (2026-09-06), which sent with `active: true` turns away off on the next refresh.

**Carry 0 (5375ae6f).** Each simulate_plan field now takes the range of the path that saves the setting, so a what-if prices only a value a save would store:
- `target_temp`, `comfort_temp_day`, `dhw_setpoint`, `dhw_min_temperature`: the card saves its what-if draft through apply_schedule, so these share apply_schedule's validator objects (`_COMFORT_TEMP_C`, `_DHW_SETPOINT_C`, `_DHW_MIN_TEMP_C` in `services.py`). set_thermal_parameters' `dhw_setpoint` takes `_DHW_SETPOINT_C` too, the same 30..75 it carried as a literal.
- `min_temp`, `max_temp`, `comfort_weight`, `comfort_temp_night`: only the options flow writes these, so the schema reads that flow's own selector range through the new `config_flow.option_range`. The `_OPTION_FIELDS` table stays the one owner of those numbers.
- services.yaml's selectors for those five fields now match the enforced ranges: 14..25, 18..28, 0.1..20 (step 0.1), 15..24 and 35..55.

**Carry 1 (7965f82b).** Every absolute instant goes, because no relative datetime form exists that the production parsers read (`manual_plan._parse_dt` and `away._parse_return_time` both read ISO 8601 only). The removed examples are apply_manual_plan's `space_slots`, `dhw_slots` and `expires_at`, and set_away's `return_time`. The field descriptions in strings.json already state the slot shape. An `away.py` comment that cited "services.yaml's example" is corrected.

**Alternatives and why each lost.**
- Narrowing every simulate field to the options-flow range: this would refuse a what-if of a `target_temp` or `comfort_temp_day` value that apply_schedule saves (5..30).
- Leaving the selectors and documenting them as UI-only: the schema would still admit a `min_temp` of -1000 into the solve.
- New `*_SELECTOR_MIN/MAX` constants in `const.py`, shared by the options flow and services. The first cut did this, and it moved `const_modules_over_50` from 3 to 4 (services.py imported 54 names from `.const`). Reading the options table instead puts services.py at 50 and adds no constant.
- A far-future expiry example: `build_override` clamps it to the window, so it is accepted, but its text would say something the call does not do. A slot example has no far-future form, because a slot starting past the window is refused.

**Carries 2 and 3 need the owner's decision before any code.** Both are listed under `## Owner questions`, and this PR does not touch them.

Closes nothing: the carries are roster items and have no issue.

## Head

`264162c0d754bb24e4e41d24027c005cb779327e` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

de4769fd1e0956cfce1b527d5e99a2ce522ba9b7, measured on origin/main 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c (the merge base).

## Mutation proof

Each mutant restores one production artifact to the merge base inside a head checkout. Command: `PYTHONPATH=tests/hastub python3 tests/entities.py`.

- **M1**, `services.py` and `config_flow.py` at the base (simulate_plan unbounded again). Exit 1. The checks that fail:
  - `simulate_plan: every number field refuses one step past its selector, and each mapped field's selector and schema range are its save path's (r11-service-schema)`
  - `null control: an unbounded comfort_weight and a min_temp selector narrower than its saved range are both refused, and nothing else`
- **M2**, `services.yaml` at the base (the old selectors and the dated examples). Exit 1. The checks that fail:
  - `services.yaml names exactly the registered services, ... every number selector's min and max pass that field's validator (R10-USER-TEXT-VERIFY-STRINGS)`
  - `simulate_plan: every number field refuses one step past its selector, ... (r11-service-schema)`
  - `no services.yaml example is a date or datetime either production parser reads (r11-service-schema)`, listing `['set_away.return_time', 'apply_manual_plan.space_slots', 'apply_manual_plan.dhw_slots', 'apply_manual_plan.expires_at']`
  - `a5:service_bounds fails an out-of-range bound and passes the yaml edges`

- `config_flow.option_range` has three added sites: BOOLOP and GUARD_OFF at the key-and-number-selector test, and RAISE_DEL at the `KeyError`. Each is killed by `tests/config_flow_steps.py` (`option_range reads the options table's own number selector for its key` and `option_range refuses ...`). They were pinned by `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c --scripts tests/config_flow_steps.py --pin-killed`, which printed `PIN KILLED: 3 pinned, 0 left unpinned`. Its comment-only null control survived. The ledger entries are in `tests/mutation_ledger/killed_by/config_flow.py/`.

## Null control

- The merge-base tree is M1 plus M2: the class check lists every simulate_plan number field as accepting one step past its selector.
- Inside the check, a planted unbounded `comfort_weight` and a planted `min_temp` selector max of 24 are both refused, and nothing else is.
- The dated-example classifier runs over a generated corpus of 348 cases. Each raw spelling is wrapped unquoted, single- and double-quoted, alone and as a slot's start and end, then YAML-loaded. The corpus covers date only, time with and without seconds, fractional seconds, `T` or a space separator, `Z` and ±offsets, basic and extended format, and lowercase `t`. The oracle is production reading the raw text, and the corpus holds both outcomes. 13 undated example shapes from the tree (window specs, a ULID, numbers, a bool, a list) are not flagged.

## Figures

<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=264162c0d754bb24e4e41d24027c005cb779327e -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- Class census, rule: every `number` selector in services.yaml, probed one step past each bound against the field's registered validator. Instrument: the r11-service-schema check in `tests/entities.py` (`PYTHONPATH=tests/hastub python3 tests/entities.py`).
  - At the base (M1, M2): all 10 simulate_plan comfort and hot-water bounds are open.
  - At the head the check passes. The remaining open seams are dispositioned by name in `_SS_EXEMPT`:
    - simulate_plan `silent_mode_power_fraction` (min 0.6, schema 0..1) is the save path's (apply_schedule) 0..1. It is carry 2's field and not changed here.
    - simulate_plan `wood_price_sek_m3` and `wood_furnace_efficiency` are already guarded: `wood_fuel._wood_override_fuel` answers `wood_fuel_not_ready` outside price > 0 and 10..95 %. The options flow scales the price ceiling by currency (`_money`), so no SEK bound is the saved one.
    - apply_schedule `silent_mode_power_fraction`: carry 2.
    - set_thermal_parameters (29 bound seams): already guarded by design. The schema is the physics guard, deliberately wider than the form, as the `_positive` comment in `services.py` says.
- Dated examples, rule: every `example` leaf in services.yaml that either production datetime parser reads. 4 at the base (M2 output above) and 0 at the head. Instrument: the same check.
- `python3 tests/structure.py`: every row within budget at the head. `const_modules_over_50` stays at its budget, with services.py at 50 `.const` names (the limit is "more than 50").
- `python3 tools/audit/archscore/score.py --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c HEAD`: `Architecture score: dS +0.0493 IMPROVES` (`literal_clone_copies 118 -> 114`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2725 ENTITY CHECKS PASSED`.
- The scoped gate is the 22 scripts `python3 tests/closure.py select --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c` names (`MODE: SCOPED`). All 22 exited 0 at this head, run either through `tests/run.sh` (`GATE_SCOPE=auto GOLDEN_MODE=drift`) or one by one with `PYTHONPATH=tests/hastub`. The `tests/run.sh` run stopped at a 30-minute background-task limit, after the scripts it had finished, so the rest ran one by one.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: it first failed with `the executed harnesses leave their committed output byte-identical`. The D6 harness's C22 counts services that carry an example, and that count moved from 10 to 9 once apply_manual_plan's examples went. Commit 4259f11 commits the regenerated `dev/audit/rounds/round4/D6/claims.{json,md}`, and the script now prints `ALL 115 HARNESS HEADER CHECKS PASSED`.

## Red checks

none

## Forward-carry

none

## Owner questions

Owner decisions this group asks for. Neither is built here, and both are user-facing behaviour changes:

- Carry 2 (56724b85): should apply_schedule treat an explicit `silent_mode_power_fraction: 1.0` as a write that resets a stored lower fraction to the default? Today `_quiet_schedule_fields` drops it as "the default", so the stored fraction stays in force, and the service text already says so. Carry: R11-SERVICE-SCHEMA
- Carry 3 (bde9263f): set_thermal_parameters admits `dhw_legionella_temperature` 55..75, but the 70 °C hard maximum caps every cycle, so 71..75 writes a value no cycle reaches. The choice is between narrowing the schema and selector to max 70, or keeping 55..75 and having the service text say that 71..75 runs at 70. Carry: R11-SERVICE-SCHEMA

## Friction

none

