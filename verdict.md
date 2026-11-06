Design review: revise 4ccb8922294c8810c9ece51cc30a24af200b865a class-open

I reviewed design.md at 4ccb8922 from a detached worktree and read the base at 28482eceeb6b9809e44b12d80fc994282cc21645, which is also current origin/main. This is note 3. The owner ruling of ~22:12Z allows up to 10 rounds, so this revise is not a re-cut. As the brief directs, I rechecked only what 964d7611..4ccb8922 changed (§C0, §T, the cost line and the fixer notes) and did not re-review what was already approved.

## What note 3 answers

- **Round-2 point (carry 0, D12-s1-01): answered in substance.**
  - **Site.** The note names coordinator.py:6565-6568. I confirmed at base that `buffer_reading.ok` is the only writer of the value, and that the `CurrentState` default is 40.0 (thermal_model.py:1741).
  - **Shape.** The fix goes through the one `_seed_store` primitive. `combi_tank_seed` uses the same primitive.
  - **Helper and data.** The helper `_open_loop_plan_value` is at coordinator.py:2315. `buffer_temp_trajectory` is empty unless the valve throttles (optimizer.py:3059-3064), so the "never fabricated" arm is real.
  - **Placement and size.** The note names a failing test, a null control, an empty-trajectory arm and a mutation target. PR B carries the fix, at +25 lines, and PR B stays M.
  - **Fixer notes.** Both are carried: buffer-open-loop-nonstore (decided) and exo-sign-check.
- **Owner carry 1 (a)-(d): present.**
  - (a) A survey of five construction types, with type 5 correctly excluded.
  - (b) Each path's parameters are labelled by source. The fetches were refused, and the note says so.
  - (c) A one-node energy balance, with a UA = 0 null control and an ε null control.
  - (d) The tank type is configuration: two numeric fields, slug-keyed presets used only by the config flow, and a `combi_type_branch` census. The vendor-name grep returns 0 at base.
- **Sibling designs.** No other open design/* note names `ExternalHeatObservation`, `buffer_tank_temperature`, `_update_current_state`, `hp_tank_temp` or D12-s1-01. I grepped every design/* ref.

## Revise points

### 1. class-open, §C0 "Observation stays measured" (design.md:243)

**Defect.** The note says coordinator.py:5038 `hp_tank_temp` is a rise detector. At base it is not. Only `dhw_temp` and `buffer_temp` feed `_rate` (external_heat.py:240-246) and the "rising … with the compressor off" evidence (external_heat.py:295-309). `hp_tank_temp` is a **level**: external_heat.py:340-363 uses it as the useful floor for `wood_energy_kwh` and as the denominator of the wood `displacement` and `free_heat_kw` (payload.py:556-557).

**Consequence.** Setting it to None without a buffer probe would silently turn off wood energy and displacement for every wood install with no buffer probe. topology.py:413 has the wood → buffer_tank chain, and the probe is optional. No finding names that behaviour change.

**Fix wanted.**
- Split the observation fields by what they measure. The rise inputs (`dhw_temp`, `buffer_temp`) take the measured value or None.
- `hp_tank_temp` takes the best level estimate. That is the reading if there is one, else the open-loop seed. If neither exists, decide and say whether it falls back to None or to today's default, and give the reason.
- Add an arm: wood, no buffer probe, a moving trajectory. The displacement must be computed against the seed. The null control is the same arm with a probe, where the reading wins. The mutation target is feeding None to `hp_tank_temp`.

### 2. class-open, §T legionella target routed through ε (design.md:92 and 158)

**Defect.** The note sends "the legionella target" through `store_temp_for_tap`. Physically that is wrong. ε describes water **flowing** through the exchanger. Disinfection concerns potable water standing in the coil or inner tank, and standing water reaches the store's own temperature between draws, which is ε = 1.

**Consequence.** With the coil preset (ε 0.85, inlet 10 °C), a 60 °C target becomes a 68.8 °C store requirement. That is close to the `dhw_hard_max` cap of min(70, …) at thermal_model.py:864, and it buys ~9 K of charge the hygiene cycle does not need. The figures are mine; the note does not give them.

**Wrong site name.** The note cites `_dhw_legionella_ceilings`, but the target is set at dhw_planner.py:494 (`ramp >= dhw_legionella_temp`) and 571 (`ready_temps[place_idx] = max(..., dhw_legionella_temp)`), in the scheduling function that starts at 441. The note's own grep returns both lines, and its table names neither.

**Fix wanted.**
- Exclude the legionella target from the tap transform, and name 494 and 571 as identity sites.
- Add an arm: at ε = 0.6 and at ε = 1.0, the legionella placement and its ready temperature are identical.

decision: owner. Should the cycle apply at all when `combi_potable_volume_l` is ≈ 0, as with the external station, where no potable water is stored? That is a product rule (the 3-litre exemption in DVGW W 551); it is not a revise point.

## Fixer notes (carries, not revise points)

- Carry: R10-COMBI-TANK (item tap-limit-census). design.md:158 names a census `combi_tap_limit`, but the evidence plan (design.md:275-277, 286) lists only `combi_store_view`, `combi_flux_live` and `combi_type_branch`. Either add it to `_P2_CENSUSES` or drop the reference.
- Carry: R10-COMBI-TANK (item cop-floor-tap). dhw_planner.py:1392 evaluates COP at `np.maximum(requirement, params.dhw_min_temp)`. That compares a store requirement with a tap limit. In combi the floor should read `store.store_temp_for_tap(dhw_min_temp)`. Otherwise give a reason in the table for leaving it.
- Carry: R10-COMBI-TANK (item loss-midpoint). dhw_planner.py:906 uses `0.5*(dhw_setpoint + dhw_min_temp)` as the store's loss temperature, so the second term is a tap limit. In combi it should go through the same transform, or be listed as left alone with a reason.

## Decisions routed

- **decision: orchestrator, the placement of carry 0.** The no-probe buffer fix affects every install and needs no combi option. Placing it in PR B queues it behind PR A (L) and behind R10-CONFIGFLOW-PAGES. It could instead land first as its own S PR after r10-livestate. PR B would then reuse `_seed_store` for `combi_tank_seed`, and the shared seed path would still be single. The note's placement is sound either way; this is an ordering call.
- **decision: orchestrator, after edges and hot files.** These are unchanged from the round-2 verdict, plus the following:
  - PR B's coordinator.py hot range adds the `ExternalHeatObservation` construction (coordinator.py:5022-5040). `git grep "ExternalHeatObservation("` at base names only that site, and no roster group's design touches it.
  - PR A edges: R10-COP-GATE, R10-ADVISOR-WHATIF and R10-HEAT-METER.
  - PR B edges: after A, after R10-CONFIGFLOW-PAGES and after r10-livestate.

The harness reports no token count for this seat.
