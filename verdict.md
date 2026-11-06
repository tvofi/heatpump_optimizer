Design review: approve a605014bff4478f470853109060f4ff7ef605d4c

I reviewed design.md at a605014b (note 4 of at most 10) from a detached worktree. I read the base at 28482eceeb6b9809e44b12d80fc994282cc21645, which is still origin/main's tip. As the brief directs, I rechecked only what 4ccb8922..a605014b changed (§C0 observation split, §T.2a, §L, the sibling table rows, Cost, Order and the fixer notes) against the two revise points of verdict 0aa84d1b6. Every file:line cited below was re-read at base.

## Round-3 revise points: both answered

1. **Observation split (class-open, design.md:225-227).** Answered.
   - The rise inputs, coordinator.py:5028-5029, take the measured value or None. `_rate` returns `(None, previous)` on None (external_heat.py:203-204), so a missing probe yields no rise and no evidence (external_heat.py:295-309).
   - The level input, `hp_tank_temp` at 5038, keeps its text and reads the best estimate, so wood energy and displacement (external_heat.py:340-363) are computed against the seed and never switched off.
   - Neither seed nor reading: the prior value or the 40.0 default (thermal_model.py:1741) is kept, which is base's behaviour, and the note gives its reason.
   - The DHW rise input also stops reading the R9 open-loop seed. The reason is stated and sound: a planned rise while the compressor is idle would otherwise be booked as external-heat evidence. It has its own arm and mutation target.
   - The `wood_seed` arm, its null control (probe present, reading wins), its no-seed arm and the "None to hp_tank_temp" mutation are all present.
2. **Legionella target (class-open, design.md:161-165 and the sibling table).** Answered.
   - The target is read as a store temperature (ε = 1 for standing water).
   - `grep -n "dhw_legionella_temp"` at base gives 9 non-const hits. The table names all of them, with 494 and 571 inside `_dhw_legionella_due` (def 429) as identity sites. The wrong `_dhw_legionella_ceilings` citation is withdrawn.
   - The `ready_temps` frame claim holds at base. 811 is the local; 922 fills `ready_temps` in `_dhw_window_floors` (797); the call at 979 returns it; 1025 passes it on; 707 hands it to `_dhw_legionella_due`. So at 571 both operands are store temperatures.
   - The `legionella_eps` arm compares ε 0.6 against 1.0 with zero draws over the ramp. Mutating 571 gives 10 + 50/0.6 = 93.3 °C, which I re-derived. The census `combi_tap_limit` names both halves.

The three round-3 carries are decided in the note:
- **tap-limit-census:** added to `_P2_CENSUSES`.
- **cop-floor-tap:** 1392 is routed, and `requirement` there is the store-frame level.
- **loss-midpoint:** 906 reads the 811 local that is transformed at its read, so it needs no edit.

## What else changed, checked

- **§L (the 3-litre default).**
  - I confirmed the reader census at base: `grep -n "dhw_legionella_enabled"` gives 15 non-const hits. The behaviour readers move to `ThermalParameters.legionella_cycle_active`: dhw_planner.py:458, thermal_model.py:863, legionella.py:273/523/637/659/697, setpoint_check.py:119 and coordinator.py:4160.
  - The inputs and display stay raw: coordinator.py:2491/7761, services.py:500, thermal_model.py:470/986 and payload.py:805.
  - Off combi the property equals the raw flag, and the null control pins that.
  - The default is data, not a type branch. The boundary, force and `not combi_tank_active` mutations are each caught.
  - It changes behaviour only on combi, which no install can reach before PR B.
- **PR 0, R10-BUFFER-OPENLOOP (S), after r10-livestate.**
  - It carries `_seed_store`, the buffer seed and the observation split. PR B reuses that primitive, so the seed path stays single.
  - `git grep -n "ExternalHeatObservation(" 28482ece` names only coordinator.py:5026.
  - I grepped every other open design/* note for legionella.py, setpoint_check, ExternalHeatObservation, external_heat, `_update_current_state`, `buffer_tank_temperature` and `_seed_store`. Only design/r10-livestate (R10-LIVESTATE.md:20-46) touches `_update_current_state`, and PR 0 and PR B are both ordered after it.
- **Cost.** +630–800 production lines across three PRs: PR 0 S, PR A L, PR B M. PR 0's +25 comes out of PR B, which stays M.

## Fixer notes (carries, not revise points)

- Carry: R10-COMBI-TANK (item livestate-copy). PR 0's seed writes to `buffer_tank_temperature` must follow R10-LIVESTATE's invariants I1/I2 (R10-LIVESTATE.md:46): write to the copy before it is published, never in place on the published `_current_state`.
- Carry: R10-COMBI-TANK (item observation-read-in-place). For the rise inputs, prefer reading `CONF_BUFFER_TANK_TEMP_ENTITY` and `CONF_DHW_TEMP_ENTITY` with the `reader` already built in `_update_external_heat_detection` (coordinator.py:5010-5025, the pattern `outlet`/`wood_top` use). design.md:225 instead has "readings `_update_current_state` keeps beside the state", which adds a coordinator attribute carried across methods. If the fixer keeps that shape, the body says why.
- Carry: R10-COMBI-TANK (item wood-seed-valve). The `wood_seed` arm needs a throttling valve to be configured, since `buffer_temp_trajectory` is empty otherwise (optimizer.py:3059-3064). Say so in the arm's setup, or the arm silently collapses into its own no-seed control.
- Carry: R10-COMBI-TANK (item split-wording). design.md:281 says "Split into two PRs" over a list of three. Fix the text when the plan row is written.
- Carry: R10-COMBI-TANK (item w551-proxy). §L sources DVGW W 551 "as recalled, not re-read". W 551's 3-litre criterion is stated for the potable volume of the pipe run downstream of the heater, so using the heater's stored potable volume is a proxy. Name it as a proxy in the option help, and in the owner's sight line.

## Decisions routed

- **decision: owner, the §L default.** The orchestrator ruled default-off at ≤ 3 l with a force option, and the note records that the owner may overrule. That is the product question round 3 routed to the owner, and it stays theirs. It is no revise point.
- **decision: orchestrator, after edges and hot files** for folding into the plan:
  - **PR 0 (R10-BUFFER-OPENLOOP, S):** after r10-livestate. Hot files: coordinator.py (`_update_current_state` around 6454-6663 and `_update_external_heat_detection` 5010-5040) and tests/features.py.
  - **PR A (R10-COMBI-TANK-STORE, L):** serialised with R10-COP-GATE and R10-ADVISOR-WHATIF on optimizer.py and coordinator.py, and with R10-HEAT-METER on thermal_model.py. Hot files: thermal_model.py, dhw_planner.py, optimizer.py, battery.py, coordinator.py (advisor readers and `litres_40c`) and dhw_learning.py.
  - **PR B (R10-COMBI-TANK, M):** after PR A, PR 0, R10-CONFIGFLOW-PAGES (config_flow.py, position 3 of 3) and r10-livestate. Hot files: config_flow.py, entry_config.py, const.py, topology.py, sensor.py, coordinator.py (`_update_current_state`, learners, 4160), legionella.py, setpoint_check.py, tests/features.py and tests/entities.py.
  - No edge to R10-UX-HEALTH or r10-ceiling-probe.

The harness reports no token count for this seat.
