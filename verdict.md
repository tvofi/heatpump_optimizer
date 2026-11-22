Design review: revise 1f9f94b2810aa2928cbae0caae7aa22189b1003f architecture-unsound

Reviewed design/R11-OWNER-EXTHEAT-OVERRIDE design.md at 1f9f94b2810a, from a detached worktree of the note's base, origin/main 8ef450936a. Sibling designs read for overlap: every open design/* ref; only design/R11-SEAM-learners touches a site this note names (`_learning_frozen`), and it claims no seam this note claims (see carry C2).
Owner request (in the brief), verbatim: "I want one new switch, an override switch that overrides the external heat detection block." Steps 2 (shape), 3 (sibling sites: dhw_planner.py:1332, wood_fuel.py:629, dhw_learning.py:494, binary_sensor.py:260/274, thermal_model.py:2046 are each placed correctly by the note) and 6 (cost) otherwise pass.

## Revise points

R1 (architecture-unsound, seam): the note misses the override that `external_heat.py` already owns. `ExternalHeatObservation.override` (external_heat.py:108), applied first in `update` (external_heat.py:260-268), is fed by `coordinator._external_heat_override` (coordinator.py:5081), from the configured stove/flue entity `CONF_EXTERNAL_HEAT_ENTITY`. The module docstring (external_heat.py:13-15) and docs/how-it-works.md:869-871 call it the override, and its log line reads "External heat override %s". Its "no" already lifts the block, by deactivating detection. design.md never names it: neither Behaviour, Precedence (design.md:58), Alternatives (design.md:134) nor Sibling sites does. Fix wanted, in the note:
  - (a) Add an alternative: the switch forces `obs.override=False`. State why it loses. Its likely reasons are those of alternatives 3 and 4: detection goes dark, and the learners unfreeze.
  - (b) Add a Precedence line for an entity-sourced activation (`source == "entity"`, the user's own stove switch reporting a fire): does the switch lift that block too? Under `blocking` as drafted it does. Say so and test it. Otherwise route it as an R-question (decision: owner).
  - (c) Pick names that do not collide. `override_on`, `set_override`, `override_active`, the unique key `external_heat_override` and the diagnostics row `external_heat_override` share one word with `obs.override` and `_external_heat_override`, which act the opposite way: the existing one asserts or denies a fire, the new one ignores the block. Use a distinct stem (for example `block_override` / `ignore_block`). The docs paragraph must name both and set them apart.

R2 (harness, cost): the RestoreEntity choice rests on a false premise. design.md:139 prices it at "zero", and design.md:214 says "No new tracked file". Neither holds at the base:
  - `homeassistant.helpers.restore_state` is not in tests/hastub/homeassistant/helpers/ (no restore_state.py). Importing it from switch.py breaks every script that imports the switch platform, so evidence test 7 cannot run as written.
  - It is not in tests/ha_floor_names.json. `ha_floor.py` fails closed on an UNRECORDED question (tests/ha_floor.py:59-61), so `floor_check` on the PR gate fails until `ha_floor.py record` is re-run against the floor tag.
  - No entity in the integration uses `RestoreEntity` or `async_get_last_state` today. The persisted user toggles (away, boost via boost.py:310-312 `_RESTORES`) use HA-free stores.
  Fix wanted: re-price alternative 1 against this. Either adopt it (a store, in pattern, no post-restart gap, and Q2 then needs no caveat), or keep `RestoreEntity` and list the new stub file with its closure classification, the floor re-record and both test files in Hot files, then redo the cost line.

## Routed decisions (not revise points)

- decision: owner -- Q1-Q5 (the orchestrator's defaults) and Q6, Q7 as the note states them. The R1(b) precedence joins them if the designer routes it rather than deciding it.

## Notes for the fixer

- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item switch-detection-attr) -- design.md:119 reads `detection_enabled` "from the published payload", but `payload.ExternalHeat` (payload.py:572-583) and the coordinator view carry no enabled field; publish it (only when it differs from the default, as `override_active` does, so goldens stay still) or read `ExternalHeatDetector.config.enabled` through the owner module.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item seam-learners-rebase) -- design/R11-SEAM-learners rewrites `_learning_frozen` into a facts function; whichever lands second keeps the `external_heat_source` reason reading the raw detection, not `blocking(...)`, and evidence test 5 pins it.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item switch-count-pin) -- tests/entities.py:11769 pins `len(switches) == 6` with a message naming the switches; update both the count and the message.
