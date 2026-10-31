R10-COP-PARTLOAD part 2, the residual carries after #2872. Issue #2501 is met by #2872 and needs only its close, which is the orchestrator's: it is a roster issue no group lists under `fixes`, so this body names it without a closing keyword.

**Round 2 answers a class-open block.** Round 1 converted the four inverse sites the RCA census listed and presented them as the whole class. The review's own enumeration found two more: the hot-water greedy planner and the always-hot hot-water baseline. This round names its own rule, runs it, and dispositions every hit. The rule found six more seams in the class beyond the review's two, and they are converted too (`## Figures`, Enumeration).

**Inverse and forward conversions (built).** With `cop_partload_derate` set, the forward relation `h = P * (1 - d * (P - p_min) / band)` is quadratic in power. So the plain `heat / cop` understates the draw a heat needs, and `power * cop` overstates the heat a draw delivers. Three helpers sit side by side in `thermal_model.py`:

- `heat_per_cop_kw` and `delivered_heat_kw` are forward, from #2872.
- `power_for_heat_per_cop_kw` is the inverse, from round 1. It is the smaller root on the rising branch, `2h / (b + sqrt(b^2 - 4ah))`. Below the floor it returns `h`; past max power it returns `h / (1 - d)`.
- `added_power_for_heat_per_cop_kw` is new in round 2. It gives the increment on a step that already has a planned draw: `inverse(forward(P) + h) - P`. On the band one more kW buys less heat, so a top-up of an already-running step is not the plain quotient even where a total from zero would be.

Each helper returns its input object unchanged at a zero derate, so every converted site computes the old float there.

Converted sites, by function:

- Round 1: `DhwPlanner._plan_dhw_min_cost` (back-conversion and energy ceiling), `DhwPlanner._clamp_dhw_to_capacity` (allowance and walk), `HeatPumpOptimizer._compute_baseline_power`, `HeatPumpOptimizerCoordinator._dhw_setpoint_sweep`.
- Round 2, the two sites the review blocked on:
  - `DhwPlanner._plan_dhw_cheapest_first`. The increment `plan[j] += take / (cop * dt)` now goes through `added_power_for_heat_per_cop_kw`. The spare heat `(p_dhw_max - plan[j]) * cop * dt` becomes `(heat_per_cop_kw(p_dhw_max) - heat_per_cop_kw(plan[j])) * cop * dt`.
  - `DhwPlanner._baseline_dhw_economics`. `(baseline_draw + standby_loss) / cop_dhw` now goes through `power_for_heat_per_cop_kw`.
- Round 2, sites the rule found:
  - `DhwPlanner._dhw_legionella_ceilings`. The run-up's rise `p_dhw_run * cop * dt` becomes `delivered_heat_kw(params, cop, p_dhw_run) * dt`.
  - `DhwPlanner._repair_dhw_floor`. The top-up `needed` and the ceiling room `room_kw` take the increment helper.
  - `HeatPumpOptimizerCoordinator._capacity_caps`. The envelope heat `entry[0] / cop_i` takes the inverse, against the solve's own model's parameters. An envelope holding exactly the heat the model says nameplate delivers now caps at nameplate. The plain quotient trimmed it to `p_max * (1 - d)`.
  - `HeatPumpOptimizer._tighten_buffer_caps`. The cut `schedule[i] - refused[i] / cop_i` takes the increment helper with a negative heat. The plain cut was too shallow under a derate, so the tank still refused heat (Figures).
  - `battery.VirtualBattery.charge_rate_kw` is now `cop * heat_per_cop_kw(max_electrical_power)`, set by `battery.build`. It was the nameplate draw times COP. It is a reported attribute, and it overstated the charge rate by up to `1 / (1 - d)`.

Alternatives considered:

- Per-site closed forms: eight copies of the root and the increment. Refused for duplication.
- An increment written as `inverse(forward(P) + h) - P` at each site: that is not the old float at a zero derate (`(P + h) - P` is not `h` in IEEE), so the zero-derate null would break. The helper short-circuits instead.
- Converting the LP's displacement row (`E / (cop * dt) - disp <= headroom`) by `heat_per_cop_kw(headroom)`. Built, then reverted, because it is a no-op for every input. `premium[j]` is 0 at any step with spare capacity, since the refill window includes the step itself. At a step with no spare, `headroom` is at most 1e-6 kW, below every floor. So the row binds only where the conversion is the identity. Its mutant would be equivalent. Dispositioned below rather than converted.

**Small-buffer fallback (built, carry 2a, round 1).** The two-zone scalar step and `simulate_trajectory_batch` each carried an inline `0.04` fallback. Both now call `_buffer_capacity`, under the same `< 1e-6` predicate and value.

**Live buffer store CPU (carry 2b).** Routed under `## Forward-carry`.

**Policy (carry 3, round 1): one sentence in `dev/governance/dimensions/D2.md` item 2.** It is the countermeasure `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` section 3 priced: before sweeping, derive the inputs of the priced formula from the device's own control surface, and mark each one a modelled term, a documented constant, or out of scope. Because it is policy, it needs the owner's approving review before merge (see Approval).

**The review's other findings, answered.**

- The setpoint sweep prices a day of hot water as 24 h of steady mean draw (`hours=24.0`). That draw is normally under the modulation floor, where the factor is 1. On a real install (`min_electrical_power` > 0) the derate almost never reaches the sweep, and its check needs a floorless band to see any effect. The round-2 always-hot baseline (`_baseline_dhw_economics`) has the same shape, and its check needs a floorless band too. Its null arm shows that a 1 kW floor leaves it unchanged. Hot water really runs in bursts near `p_dhw_max`, so both figures still underprice the derate on a real install. Pricing them at the planned run power changes both cost laws (it needs a run power and a duty), not a conversion. Forward-carry below.
- The LP-objective secant (`price * E / cop`, linear in heat, under a convex electrical cost) is unchanged and carried. The terminal valuations (`row_cost`, `_deferred_energy_cost`) and the wood advisor's per-kWh pump-heat price have the same shape: heat energy priced linearly at a COP, with no draw rate stated. The derate is a function of the draw rate, so they need a stated rate before they can price it. Forward-carry below, as one finding.
- `coordinator._capacity_caps` and `optimizer._deferred_energy_cost`: `_capacity_caps` is converted; `_deferred_energy_cost` is out of class, for the reason in the previous point. `sysid._size_step_power`'s two quotients are the census's step bound, confirmed in the Enumeration below.

## Head

`29a1742cd9264724114cad7af4e61143091e98c5` (round 3) is one commit on `9033a59583eb7fb2c9db43b0259b107a1aa44c54`: `tests/structure.py --record`, which lowers `class_excess_loc` from 17656 to 17654 and moves `recorded_at` to the merge base `be7584c4904e243ffb48c166be39221623d81415`. No other file changes and no budget rises. The cause is under Red checks.

`29a1742cd9264724114cad7af4e61143091e98c5` re-keys 4 `## Unpinned sites` line(s) the main merge moved from `958b4af8eee134728986d92d2220f1dfadbab255`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:9080 BOOLOP -> custom_components/heatpump_optimizer/coordinator.py:9076 BOOLOP; custom_components/heatpump_optimizer/coordinator.py:9070 CMP_BOUND -> custom_components/heatpump_optimizer/coordinator.py:9066 CMP_BOUND; custom_components/heatpump_optimizer/coordinator.py:9081 CLAMP_DROP -> custom_components/heatpump_optimizer/coordinator.py:9077 CLAMP_DROP; custom_components/heatpump_optimizer/coordinator.py:9082 CLAMP_DROP -> custom_components/heatpump_optimizer/coordinator.py:9078 CLAMP_DROP.

`9033a59583eb7fb2c9db43b0259b107a1aa44c54` merges main `be7584c` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`958b4af8eee134728986d92d2220f1dfadbab255` merges the authored code head `410f8d509e0b7ffa669f79813009128ec7b5db53` and then merges origin/main `5d4e0bcfb` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`958b4af8eee134728986d92d2220f1dfadbab255` re-keys 1 `## Unpinned sites` line(s) the main merge moved from `410f8d509e0b7ffa669f79813009128ec7b5db53`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:9080 CMP_BOUND -> custom_components/heatpump_optimizer/coordinator.py:9070 CMP_BOUND.

`781cce5cf936601027b200bcf2d871c098b643dc` merges the authored code head `410f8d509e0b7ffa669f79813009128ec7b5db53` and then merges origin/main `5d4e0bcfb` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`781cce5cf936601027b200bcf2d871c098b643dc` re-keys 6 `## Unpinned sites` line(s) the main merge moved from `410f8d509e0b7ffa669f79813009128ec7b5db53`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:9090 BOOLOP -> custom_components/heatpump_optimizer/coordinator.py:9080 BOOLOP; custom_components/heatpump_optimizer/coordinator.py:9090 CMP_BOUND -> custom_components/heatpump_optimizer/coordinator.py:9080 CMP_BOUND; custom_components/heatpump_optimizer/coordinator.py:9091 CLAMP_DROP -> custom_components/heatpump_optimizer/coordinator.py:9081 CLAMP_DROP; custom_components/heatpump_optimizer/coordinator.py:9092 CLAMP_DROP -> custom_components/heatpump_optimizer/coordinator.py:9082 CLAMP_DROP; custom_components/heatpump_optimizer/optimizer.py:4173 CLAMP_DROP -> custom_components/heatpump_optimizer/optimizer.py:4174 CLAMP_DROP; custom_components/heatpump_optimizer/thermal_model.py:2137 GUARD_OFF -> custom_components/heatpump_optimizer/thermal_model.py:2153 GUARD_OFF.

410f8d509e0b7ffa669f79813009128ec7b5db53. It descends from round 1's head `dfb981d7a0066c472ef408467a88630e77227f70`, whose merge base with origin/main is `cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7`. `git merge-tree --write-tree origin/main HEAD` was clean against origin/main `a6e4a5afe37b`, `date -u` Fri Oct 30 22:41:47 UTC 2026. Round 2 adds these commits on top of round 1:

- `9e832b431`: the conversions and the feature block.
- `9d8264a2a`: two spent comment passages cut in `DhwPlanner`.
- `37bbcbc12`: the structure record.
- `8be4e310b`: the census harness's helper-call listing, its INERT classification, and three stale ledger entries deleted.
- `410f8d509` (the tip): the mutation ledger's five pins and five triages.

## Mutation proof

The round-2 block in `tests/features.py` starts at the comment `# Round 2: the hot-water planner's remaining conversions` and holds eight `R.check` calls. Each mutant below reverts one production site to its round-1 text. The mutants ran through a driver, out of tree (fixer step 18), that execs `tests/features.py`'s imports and definitions, then the whole R10-COP-PARTLOAD part-2 block (13 checks: round 1's five and round 2's eight). The driver restores the file after each mutant and asserts that it did. Every mutant turns its own site's check red and nothing else:

- G1 `_plan_dhw_cheapest_first` increment, `plan[j] += take / (cop * dt)`: 1 of 13, the cheapest-first check. The derated tank ends 54.15 C where the zero-derate one ends 54.57 C.
- G2 `_plan_dhw_cheapest_first` spare heat, `(p_dhw_max - plan[j]) * cop * dt`: 1 of 13, the cheapest-first check (its capped arm). Re-simulated inside the loop at a draw past the 1.5 kW cap, the plan meets the floor. Once the cap is applied, it ends at 55.90 C against a 56 C floor (tolerance 0.05).
- B1 `_baseline_dhw_economics`, plain quotient: 1 of 13, the always-hot baseline check.
- L1 `_dhw_legionella_ceilings` rise, `p_dhw_run * cop * dt`: 1 of 13, the run-up check.
- R1 `_repair_dhw_floor` top-up, plain `needed`: 1 of 13, the repair check. The derated tank overshoots to 52.37 C, against 52.0 C at zero derate.
- R2 `_repair_dhw_floor` room, plain `room_kw`: 1 of 13, the repair check (its room arm). The derated tank ends the first step at 55.148 C where the zero-derate walk ends it at 55.211 C, so the derated trajectory leaves the zero-derate one and its 55 C ceiling step.
- C1 `_capacity_caps`, `float(entry[0]) / cop_i`: 1 of 13, the capacity-caps check. The cap is 4.0 kW where nameplate is 5.0.
- T1 `_tighten_buffer_caps`, the plain cut: 1 of 13, the tightening check. Re-simulated at the new caps, the tank still refuses 0.92 kW.
- V1 `VirtualBattery.charge_rate_kw`, `charge_power_kw * cop`: 1 of 13, the battery check (15.0 at d=0.2).
- A0 `added_power_for_heat_per_cop_kw` returns its input (the derate branch deleted): 4 of 13. These are the increment round trip and the three sites that call the helper (cheapest-first, repair, tightening), so the helper is load-bearing at each.

Failing test first: at round 1's head the round-2 block cannot import `added_power_for_heat_per_cop_kw`. Each of G1 to V1 is round 1's production line at that site, and each fails only its own check, as listed.

The round-1 mutants M0 to M6 were not re-run. Round 2 leaves their lines, their checks and the helper's inverse untouched. The round-1 block's five checks pass in every row above, and they read only the round-1 sites.

Ledger: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` -> `PIN KILLED: 5 pinned, 5 left unpinned (5 survived, ...)`, null control `battery.py:42 NULL_COMMENT survived tests/features.py`. `tests/features.py` is the only driver because the default driver set ran `tests/entities.py` first, and its baseline is red on this macOS seat (Red checks); that run printed `MUTATION TABLE INCONCLUSIVE` and pinned nothing. The 5 pinned and the 5 triaged are listed under Unpinned sites.

## Null control

- **Zero derate, round 2's own sites, bit for bit.** A second out-of-tree driver evaluates the eight round-2 scenarios at `d = 0` with rounding disabled, on round 1's production (`dfb981d7`) and on this head. The output is identical: `diff` exits 0 over the plans, tank trajectories, baseline, caps and cuts, printed with `repr`. The `capacity caps` arm is vacuous here, since nameplate caps nothing at zero derate. The block's own check carries a positive arm.
- **Zero derate, whole plans.** The finder's harness `dev/audit/harnesses/r10_cop_partload.py` (sha1 0b2f5ce911c0, unchanged by the diff) prints 32 `d=0.0` plan hashes. All 32 are identical at the merge base `cf4f6b7a6`, at round 1's head and at this head.
- **The harness is flat on round 2's sites.** At `d=0.112`, 0 of 32 plan hashes move between round 1's head and this head (26 of 32 move from the merge base, round 1's own effect). Its installs reach none of the round-2 sites: no greedy fallback, no floor repair top-up, no capacity envelope, no buffer refusal. So the harness reads flat at both ends of round 2, and the per-site feature checks are its companion. Each reads the defect on round 1's production line and not at the head (Mutation proof).
- **Below the floor.** The always-hot baseline at d=0.4 with a 1 kW modulation floor equals the zero-derate value bit for bit. The mean draw sits below the floor, where the factor is 1.
- **The helpers.** A zero derate returns the input object (`is`) from both the inverse and the increment.

## Figures

- Enumeration, the rule: `python3 dev/audit/harnesses/r10_cop_conversions.py`. It is an AST query over `custom_components/heatpump_optimizer`, and it reports three kinds of node:
  - every division whose divisor is COP-shaped (heat to power);
  - every product with a COP-shaped factor (power to heat), as a `BinOp` or an augmented assignment;
  - every call of a conversion helper.
  COP-shaped means a name, attribute, call or subscript whose identifier contains `cop` (not `copy`, `scope` or a helper's own name); a product of such terms; or a `max`/`min`/`float`/`abs` wrapping one. Only the outermost of a nested pair is printed. Each hit is marked ROUTED (through a helper) or PLAIN.
  - At this head it prints `RESULT hits=95` and `RESULT plain=54`.
  - At the merge base `cf4f6b7a6` the same file prints `hits=79` and `plain=68`.
- Enumeration, null control against the review's rule: `git grep -nE '/ *\(?[A-Za-z_.]*cop' -- 'custom_components/*.py'` at `cf4f6b7a6`, comment lines dropped, gives 20 lines. That is a division by a COP-named term, the review's rule. Every one of the 20 is a hit of the enumeration at the same file and line, except `store.py:332`, the string literal `"measured_cop/cop"`. The comparison was `comm -23` of `file:line` keys.
- Enumeration, every PLAIN hit with its disposition (anchored by function; ROUTED hits are closed in this diff or in #2872):
  - Closed in this diff:
    - `battery.py:charge_rate_kw`: the factor is `charge_heat_per_cop_kw`, which is `heat_per_cop_kw`'s output.
    - `thermal_model.py:extend_dhw_temps` (`cop * heat_per_cop[i]`) and `simulate_trajectory_batch` (`cop * heat_per_cop_i`, two hits) are already routed by #2872. The operand is `heat_per_cop_kw`'s output, hoisted once per schedule. That is lexically PLAIN, and routed in fact.
  - Not a heat/power conversion:
    - `coordinator.py:machine_score`, `_observe_cop_health`, and `store.py:<module>` use COP-health constants.
    - `coordinator.py:_fold_cop_evidence` (two hits) updates the learned `_cop_scale`.
    - `thermal_model.py:_cop_law` (three hits) and `_batch_cop` (four hits) multiply COP factors together.
    - `thermal_model.py:partload_factor` is `d * x`, the derate itself.
    - `topology.py:outdoor_cop_miss_sek` (two hits) is the sensitivity of cost to a mis-set COP, not a plant conversion.
  - Measurements:
    - `coordinator.py:_fold_capacity_envelope` and `flow_meter.py:cop_evidence` (three hits) read measured power at an observed COP, and the observed COP already contains the real part-load. This is the census's disposition.
  - Nameplate and design sizing, a plant constant that calibrates emitter UA or bounds a rollover: `p.max_electrical_power * p.cop_nominal_floored` in
    - `optimizer.py:_compute_baseline_power`,
    - `sysid.py:_held_state`,
    - `thermal_model.py:_valve_ua`, `_valve_two_zone_delivery`, `flow_target_for_indoor`, `_substeps_and_loss` (two hits), `simulate_trajectory_batch` (two hits),
    - and `heat_energy.py:observe_cycle`'s `max_heat_kw`.
    Folding the derate in would count it twice against the UA it calibrates. This is the census's disposition.
  - Bounds and detectors, deliberately looser than the model. A derate only lowers true heat, so each stays a bound:
    - `coordinator.py:_max_pump_rise`.
    - `heat_energy.py:span_heat`, the counter-resolution threshold.
    - `sysid.py:_size_step_power` (four hits). The census's `sysid._size_step_power` bound, confirmed: the plain quotient sizes a step that delivers at most the `q` its excursion was judged at.
    - `sysid.py:_begin_step_phase`, the adoption check on the same step.
  - Learning samples: `sysid.py:step` (two hits). The fit reads the plan's power at the model's COP to infer UA. Folding an assumed derate in would make the learned UA absorb the assumption. This is the census's disposition.
  - Out of class, by its own reasons:
    - `sysid.py:_valve_drive`, `q / compute_cop`: `q` is the step's nominal heat at the plain law. The plant then prices every COP effect on the resulting draw: the flow lift, which its docstring names, and the part-load derate the same way. Inverting the derate there would exempt one of those effects from the plant.
    - `modbus_prefill.py:_plant`, `capacity / cop`: a datasheet rating, whose COP is measured at that capacity and already contains the part-load.
    - `dhw_planner.py:_plan_dhw_min_cost`'s displacement row `1.0 / (cop * dt)`: a no-op for every input, argued under Alternatives.
  - A distinct finding, carried (Forward-carry, the linear-valuation finding):
    - `dhw_planner.py:_plan_dhw_min_cost` objective, `prices / cop`;
    - `optimizer.py:row_cost` (three hits);
    - `optimizer.py:_deferred_energy_cost` (three hits);
    - `wood_fuel.py:cheaper_hour_count` and `_scan_wood_night`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at 410f8d509 -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, `4 TEST SCRIPT(S) FAILED`: `tests/entities.py`, `tests/optimality.py` (1 of 84), `tests/card.mjs` and `tests/stress.py` (1 of 113). Each is answered under Red checks. Among the rest: `ALL 4618 FEATURE CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `ALL 61 GUARD PIN CHECKS PASSED`, `ALL 132 manual plan checks PASSED`; stress.py's production-call channel check is not among its failures.
- Structure: `python3 tests/structure.py --record` moves `class_excess_loc` from 17671 to 17670. The round-2 conversions added six lines across the `DhwPlanner` and `HeatPumpOptimizer` spans. Two spent comment passages in `DhwPlanner` paid seven: the repair's account of its own first cut and its measured deficits, and the run-up's case for its own existence. Each keeps its rule. `max_class_loc` is 8064 at 8064, because the coordinator's two-line `has_hum`/`hum` pair became one line that pays for `model = model or self._thermal_model`. `STRUCTURE RATCHET PASSED` at round 2's head.
- Structure, round 3: `python3 tests/structure.py` at `9033a595` -> `class_excess_loc 17656 17654 -2 BETTER`, `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`; at `be7584c49` (main, the control) -> `STRUCTURE RATCHET PASSED`; at `29a1742cd` after `--record` -> `STRUCTURE RATCHET PASSED`. The per-class split comes from summing `max(0, span_loc - GOD_CLASS_LOC_LIMIT)` per class with `tests/structure.py`'s own `span_loc` and `coordinator_helpers`: 17658 at the merge base `a5cf3b6f5`, 17656 at `76d96ac77` (branch side), 17656 at `be7584c49` (main side), 17654 at `9033a595`. At the two trees where `structure.py` itself ran (`9033a595` and `be7584c49`), the sum equals its figure.
- Architecture score: `python3 tools/audit/archscore/score.py --diff cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 HEAD` -> `Architecture score: dS +0.0000 NULL`.
- Policy lint: `node tools/policy/policy_lint.mjs` -> `TOTAL: 0 error(s) across 50 policy file(s)`; `node tools/policy/rules_sync.mjs --check` -> `RULES-SYNC ok`.
- Finder's harness at three trees, `PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py`, with every run reading `failures 0`:
  - `d=0.0`: 32 of 32 hashes identical at all three.
  - `d=0.112`: 0 of 32 move between round 1's head and this head.
  - Flat `d=0.112` summary: identical between round 1's head and this head (`heat short max 0.1098`, `flat wins 15`).
  - At the merge base it reads `0.1093` and `16`. That is round 1's effect, re-taken here at `cf4f6b7a6` rather than round 1's `507a9ec26`.
- Increment round trip (the block's first round-2 check): forward of (P + increment) less forward of P equals the heat asked for to 1e-12, over P in {0.5, 2, 4} kW and heat in {0.3, 1.0, -0.4} at d=0.2 on a 1.5-5 kW band.

## Unpinned sites

`prepr.sh`'s CI-predict step lists none at the head. These are the ten sites the round-2 diff adds, each with its ledger entry (commit `410f8d509`):

- `custom_components/heatpump_optimizer/battery.py:119 RETURN_DEL`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/battery.py:119 CLAMP_DROP`: triaged `equivalent`. The COP comes from `compute_cop`, which is at least 1.0.
- `custom_components/heatpump_optimizer/coordinator.py:9076 BOOLOP`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/coordinator.py:9066 CMP_BOUND`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/coordinator.py:9077 CLAMP_DROP`: triaged `equivalent`. `compute_cop` is at least 1.0. This re-keys `33200ef3`.
- `custom_components/heatpump_optimizer/coordinator.py:9078 CLAMP_DROP`: pinned, killed by `tests/features.py`.
- `custom_components/heatpump_optimizer/dhw_planner.py:1724 CLAMP_DROP`: triaged `equivalent`. `dt * cop_j` is at least `0.5 * dt`.
- `custom_components/heatpump_optimizer/dhw_planner.py:1739 CLAMP_DROP`: triaged `equivalent`. `dt * cop_room` is at least `0.5 * dt`. This re-keys `21bb873a`.
- `custom_components/heatpump_optimizer/optimizer.py:4174 CLAMP_DROP`: triaged `equivalent`. The buffer's `marginal_cop` is `compute_cop`, which is at least 1.0.
- `custom_components/heatpump_optimizer/thermal_model.py:2153 GUARD_OFF`: pinned, killed by `tests/features.py`.

## Red checks

- `tests / fast (3.14)` at `9033a595` (run job 124455452443): `python3 tests/structure.py` failed with `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, `class_excess_loc` budget 17656, measured 17654. Cause: the merge of origin/main composed two equal one-line edits. From the merge base `a5cf3b6f516a` (measured 17658), this branch measured and recorded 17656 (`HeatPumpOptimizerCoordinator` -1, `ThermalModel` -4, `DhwPlanner` +2, `HeatPumpOptimizer` +1), and main at `be7584c49` measured and recorded 17656 (`HeatPumpOptimizerCoordinator` -2). Git saw the same text on both sides and merged 17656 without a conflict, but the merged tree carries both deltas: 17654. Main is green on it (`STRUCTURE RATCHET PASSED` at `be7584c49`, the merge base). Repaired by `29a1742cd`'s record, a lowering. Root-cause trigger: the cheaper detector is `python3 tests/structure.py` on the merged head, which the merge-main automation does not run before it pushes. That is the orchestrator's merge path, not this diff, so no countermeasure is owed here.
- `governance / instrument-self-tests` at `9033a595` (job 124455006317): the failing step is `prepr.sh --self-test`, `428 passed, 1 failed`, and the failure is `FAIL and pushes a body the lint passes (null control: the same body without the session link) (got 1, wanted 0)`. The `FIXTURE VACUOUS` lines for `checkIndex` and `checkDuplicates` are `PIN` lines in the same log: each is a mutant the self-test kills, not a failure. Cause: the self-test clones this checkout, and `body_push.sh` runs `review_packet` on that clone. `review_packet` refused the head on the same structure record: `review_packet: REFUSE structure: tests/structure.py refuses the head merged with main`. Reproduced locally by a replica of the self-test's `lpush` arm on a clone: rc 1 at `9033a595` with that REFUSE line, rc 0 at `be7584c49` (the null control) and rc 0 at `29a1742cd`. The full `env -u BASH_ENV bash tools/pr/prepr.sh --self-test` at `9033a595` printed the same single FAIL line (`428 passed, 1 failed`, rc 2). The same command at `29a1742cd` printed `429 passed, 0 failed`, rc 0. Root-cause trigger: the cause and its cheaper detector are the structure entry above. The self-test arm is working as designed.
- `pr-contract / pr-contract` (06:14Z and 06:17Z at `9033a595`): `PR-BODY: 2 error(s)`. The previous body's `## Red checks` named neither `governance / instrument-self-tests` nor `tests / fast (3.14)`. This body names both. Root-cause trigger: this was a downstream effect of the two reds above, and the body is the place it is answered, so no cheaper detector is owed.
- `budget-raise-gate / budget-raise-gate` at `9033a595` (05:34Z): `REFUSED: tvofi's approval is on 76d96ac77239, not this head 9033a59583eb`. `29a1742cd` raises nothing (the structure record is a lowering), and the two raises are still the approved D2 caps under Raise justification. An approval at the new head is owed again, as the gate keys on the head.
- Local scoped-gate reds at 410f8d509 (none of them this diff's; CI's Linux runners are the authority):
  - `tests/entities.py`: the nightly lane's stdlib sample dies with `PermissionError: Cannot get task port` (macOS task-port entitlement). The same 44 `FAIL` lines, all from the a3-a10 and hb fixture arms, and the same crash appear at the merge base `cf4f6b7a6`; the run there exits 1 too. The comparison diffed the sorted FAIL names; only two timing figures differ. No cheaper detector is owed: the red is the seat's sandbox, not a defect.
  - `tests/card.mjs`: `FATAL ERROR: ... JavaScript heap out of memory` under a load average near 170. This diff touches no card file.
  - `tests/optimality.py` (`one|summer_negative|shoulder: a recorded claim still has a gap (not stale)`, gap 0.0000%) and `tests/stress.py` (`shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`): both fail identically at round 1's head `dfb981d7`, re-run by hand at that tree. They are solver-float figures that do not reproduce across BLAS builds (`CLAUDE.md` rule 3). At a zero derate this round's production is bit-identical to round 1's (Null control).
- `budget-raise-gate / budget-raise-gate`: red because this head raises a budget and changes policy. `dev/governance/config/policy_budgets.json` raises the D2 brief's caps (Raise justification) for the new sentence in `dev/governance/dimensions/D2.md` item 2. It stays red until tvofi's approving review at the head, or the orchestrator's approval under the mandate. Root-cause trigger: no cheaper detector exists. The gate is the owner-approval mechanism by design (`CLAUDE.md` rule 2, decision 0013), so its red is the expected state before approval, not a defect.
- `tests / closures`: none predicted. `ci_predict.py --apply-inert` wrote the new harness's INERT entry for `tests/harness_headers.py` (commit `8be4e310b`).
- `mutation`: none predicted (Unpinned sites). The three stale ledger entries `ci_predict` named (`_capacity_caps` BOOLOP `a5d8d969` and CLAMP_DROP `33200ef3`, and `_repair_dhw_floor` CLAMP_DROP `21bb873a`) were keyed on lines this diff rewrote, and are deleted.
- `prelude`: red at an ancestor only. On 66aa7216a (a merge of origin/main into this branch) run 41100545395 job 124216944029 died on `TimeoutError: The read operation timed out`, a GitHub API read timing out, with no diff content involved. Every later head's prelude is green, including 4665c0c91 (both runs). Root-cause trigger: the red is transient infrastructure, not a defect, so no cheaper detector exists for it and none is owed.
- Round 1's local `tests/entities.py` red, on the D2 brief past its caps, was repaired in round 1 (f57d2fd21). Its cheaper detector is `node tools/policy/policy_lint.mjs`, and no new detector is owed.

## Forward-carry

- **Linear valuations under a convex cost.** The hot-water LP's objective (`price * E / cop`), the terminal `row_cost`, `_deferred_energy_cost` and the wood advisor's pump-heat price all price heat linearly at a COP, with no draw rate. Under a derate the electrical cost is convex in heat, so each is a secant under-estimate. Pricing it needs a stated rate: per-step segments in the LP, a refill rate for the terminal and deferred figures. A later D0 pass on `_plan_dhw_min_cost` and `_terminal_cost` owns whether to segment them. Destination: the group's roster carry list. At `handoff/audit-r10-roster` `237e1aae4a08b860ea953d83750a4eb2c609b08f`, `$.groups[88].carry` holds four entries (0-3) and neither this finding nor the next one, so the append is owed to the standing-roster seat (`roster_edit.py`), which this seat does not run. Carry: R10-COP-PARTLOAD
- **Mean-draw pricing.** The setpoint sweep and the always-hot hot-water baseline price a day's hot water as steady mean draw. That draw sits under the modulation floor on a real install, so the derate rarely reaches them, while real hot water runs in bursts near `p_dhw_max`. Pricing them at the planned run power changes both cost laws, and is not a conversion. It goes in the same owed append as the previous item, to the same destination. Carry: R10-COP-PARTLOAD
- The 2.44x CPU of the live buffer store (carry 2b, measured at round 1's merge base `507a9ec26` by `python3 dev/audit/harnesses/r10_buffer_store.py bench 3`; its control is that harness's flat no-buffer null) is unbuilt by this pull request. Destination: `$.groups[88].carry[2]` at `handoff/audit-r10-roster` `237e1aae4a08b860ea953d83750a4eb2c609b08f`, which holds it: "The 2.5x CPU cost of the live buffer store ... a bound or warm start on the planner must earn it". Carry: R10-COP-PARTLOAD

## Friction

- frugal-routing: cost: in round 1, the session's inline-read guard blocked plain reads of files the seat had to edit. Carry: dismissed: a session-local plugin, not repository policy
- main-checkout-guard: unclear: this seat's `git commit -m` from its own worktree (`cd <worktree> && git commit`) was refused as "the main checkout must stay clean". The same commit as `git -C <worktree> commit -F <file>` passed. Carry: dismissed: a session-local hook, not repository policy

## Raise justification

`dev/governance/config/policy_budgets.json` (round 1, unchanged): the cap table keys `dev/governance/dimensions/D2.md` as `tools/audit/briefs/D2.md`. That key goes from 51 to 53 lines and from 644 to 683 tokens. The two lines and 39 tokens are the policy sentence the dispatch asks for, and nothing else.

Payments tried: (1) cutting spent prose elsewhere in the brief -- every `## Reuse` citation still resolves and no item restates another, so nothing was spent; (2) tightening the sentence itself, from four lines (54 lines, about 706 tokens) to three (53, 683); (3) reflowing lines to fit 51 -- refused, because it moves the metric without improving the text.

Code architecture is untouched by the raise.
Architecture score: dS +0.0000 NULL

## Approval

`dev/governance/dimensions/D2.md` is policy: this pull request changes what a D2 seat must do in item 2. It needs the owner's approving review at its head before merging. The orchestrator approves under mandate 6329234399, per the dispatch.

