R10-SAV-VALUATION-RESIDUE, part 1 of 3 (Carry 0 to Carry 4). `_thermostat_held_state` set the zones to the target even where the reference step cannot deliver the target's steady heat. No thermostat keeps that state, so every booked reference step from it drew the house's stores, booked as reference heat nobody paid for. The held zones now sit at the highest temperature the reference step can hold, found by bisection (`_HELD_BISECTIONS`). The bounds are every limit on the heat the step delivers (`_held_unreachable`): behind a valve, the curve's top draw (`thermal_model.valve_top_draw`); on every install, the pump. For the pump bound, the steady heat the step makes (`_thermostat_demand`, the tank's standing loss included) must not need a draw past `max_electrical_power` at the step's own COP (`_reference_cop`, defrost and part-load included). That state is an equilibrium, so a booked step from it draws no stored heat. A reference that can hold the target leaves the held state as before.

This repair answers the blocked verdict at 69078d59 (`class-open: the held state's infeasibility predicate guards only the valve curve's top draw, not the heat pump's capacity`). The predicate now applies both bounds, and the bisection runs on valved and unvalved installs. `## Figures` lists every bound against its disposition, with the census that measures the class's property.

Alternatives and why each lost:
- (a) Settle the reference's store change per booked step in the ledger. That books a sag no thermostat undergoes, and it moves stored-heat valuation, which Carry 4 rules out ("a fix there changes the reference ..., not stored-heat valuation").
- (b) Find the equilibrium by simulating the reference forward until it settles. That costs a horizon of steps per solve on a Pi-class target. The closed-form balance is monotone in the zone temperature, so bisection reaches it in 40 evaluations of arithmetic.
- (c) Book `_compute_baseline_power`'s first simulated step in place of the apportioned one. Measured in `## Figures` (exposed seam). It changes `_apportion_by_steady_demand`, another group's mechanism pinned by its own checks, so it waits on a ruling (`## Forward-carry`).
- (d) For the capacity seam, a second predicate beside the valve's (a pump check in its own branch). One function owning every bound (`_held_unreachable`) keeps a later bound from landing in one branch only. That gap is what blocked the previous head.

The brief's carries:
- Carry 0 (the unattributed residual, -3.75 % / -8.12 % at its source): #3442 attributed it (Carry 4's text). This diff removes the attributed store term in both of its classes (`## Figures`, residual and attribution).
- Carry 1 (part-load refill pricing in `_terminal_cost` and `_deferred_energy_cost`): built by #3442 (`optimizer._refill_law`, one law for both twins). This diff touches neither function. The hot-water LP's secant stays with Carry 5.
- Carry 2 (Carry 1's segment-or-rate decision and its zero-derate control): decided in #3442 as the stated rate. This diff touches neither function.
- Carry 3 (the residual at the merge base): -3.90 % flat and -8.02 % varying at the base (the fix reviewer's re-take at e59e21fe). At this head: +6.84 % and +3.38 % (`## Figures`).
- Carry 4 (the attribution and its fix): built in this diff. The store term's pump-unreachable class reads 0.00 kWh_th at this head. Its other class, booked steps whose apportioned power exceeds the held equilibrium, reads +11.11 kWh_th; that class comes from `_apportion_by_steady_demand`, not the held state (`## Figures`).
- Carry 6 and Carry 11 repeat Carry 3, and Carry 7 and Carry 12 repeat Carry 4. Each is answered by the carry it repeats, so nothing further is owed for them.
- Carry 5, Carry 8, Carry 10 and Carry 13 belong to parts 2 and 3 and are not answered here. Carry 8 and Carry 13 repeat Carry 5. Carry: dismissed: evidence, not a finding
- Carry 9 also belongs to a later part, and this diff moves its starting point. Where the reference cannot hold the setpoint, by its valve curve or its pump, the reference's held state now starts at that equilibrium below the target, not at 21 C. Carry 9's "19.93 against 21.00" was read from a held 21 C start, so it is not comparable at this head.
  - A pass ending below 21 there is the install's limit, not the controller's. A controller fix is legitimate only if `_held_unreachable` reads false at the target on the install's own parameters.
  - Re-measure `r10_advisor_steady_seams.py fields` at that part's merge base. Carry: dismissed: Carry 9 is already this group's, and its later part reads this body

Disclosed self-correction: the previous body read the harness's reference stored term at 69078d59 as -0.30 kWh_th and took it for the store term at 0. It was a cancellation of two classes: 50 steps whose held state the pump cannot keep drew -13.20 kWh_th, and 142 steps whose booked power exceeds the held equilibrium gained +12.90 (`## Figures`, split). The previous body's residual and store figures are superseded by this body's.

## Head

`bace7b742be1fb14a2da817fec5a131c13105d43`, six commits on the PR head `69078d59a07a929555e77c79432e4aa655941bb2`. 6f396cce rewrites the predicate (`_held_unreachable`, both bounds) and adds the capacity checks. d91e15a8 restores the bisection span's `min()`, which the pump bound needs (a warm day under a pump below the tank's standing loss), adds a check that pins it, and deletes five ledger rows whose lines the rewrite removed. 056abe4d drops the redundant `valved and` from the wood reset (`two_tank_modelled` already requires a throttling valve, `ThermalParameters.topology_layout`), adds the wood-reset and zero-demand checks and two triage rows. fa365370 lands the census harness and deletes the stale pin on the removed unvalved early return. ca118b90 is `ci_predict.py --apply-inert`'s repair (`prepr.sh` refused fa365370 on a predicted `tests / closures` red): the census harness becomes an inert read of `tests/harness_headers.py` in `tests/closures.json`. At ca118b90 the scope reads the same mode line, `tests/harness_headers.py` prints `ALL 115 HARNESS HEADER CHECKS PASSED` and `tests/closure.py selftest` `ALL 118 closure shrink pins PASSED`. bace7b74 answers `prepr.sh`'s diff mutants. It drops the pump bound's `max(0.0, made)`, which clamped nothing: on a held state the zones' needs floor at 0, and the slab and tank sit where their charge terms vanish. It also gives the capacity rows a one-step humidity series, so a read past step 0 raises. Production code is identical at 056abe4d, fa365370 and ca118b90; bace7b74 differs from them by that clamp alone. Figures were measured 2026-11-13 (UTC): the census, block, gate, mutants and `prepr.sh` at bace7b74; the harness and the class split at 056abe4d and fa365370, whose production code differs from bace7b74's only by the no-op clamp. `git merge-tree --write-tree origin/main HEAD` against origin/main f4725015 merges clean. VERSION, the manifest and RELEASE_NOTES are untouched.

## Mutation proof

Command: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- R10-SAV-VALUATION-RESIDUE: stored heat" "# --- R10-WATER-SETPOINT-FEEDBACK"`. Each production line was neutralised in turn, then restored.
- At 6f396cce (7 checks in the block):
  - M1, `if unreachable(held):` to `if False:`: FAIL the valve-curve check and the new capacity check (`a pump too small to hold the setpoint starts the reference where its capacity holds the house, valved or not ...`).
  - M2, the pump bound's `return bool(... > p.max_electrical_power)` to `return False`: FAIL the capacity check alone.
  - M3, the valve bound's conjunct to `if False and ...`: FAIL the valve-curve check alone.
  - M4, `if unreachable(held):` to `if True:`: FAIL both null controls (valve curve able to hold; pump able to hold).
  - M5, the bisection step to `lo, hi = (lo, mid)`: FAIL the valve-curve and capacity checks.
  - M6, the final `held = held_at(lo)` dropped: FAIL the same two checks.
  - M7, `_reference_cop` replaced by `cop_nominal_floored`: FAIL the same two checks.
  - M8, the candidate's tank-at-hold-temperature guard to `False`: FAIL 3 checks.
  - M9, the pump bound read at twice `max_electrical_power`: FAIL the capacity check.
  - NULL, a comment inside the change edited: `ALL 7 FEATURES BLOCK PASSED`.
- Failing test first: the block at fa365370's tests against 69078d59's `optimizer.py` FAILs the capacity check (`1 of 7 FEATURES BLOCK FAILED` at 6f396cce's block). At fa365370 the block reads `ALL 10 FEATURES BLOCK PASSED`.
- Sites the later commits pinned, each measured with the block: `float(weather.humidity[1])` raises `IndexError`; `lo, hi = (outdoor), target` FAILs the warm-day check; `if False:` on the wood reset FAILs the wood check; `>=` on the candidate's zero-demand guard FAILs the zero-demand check.

## Null control

- A valve curve able to hold the setpoint (`mixing_valve_target` 40.0, both zonings, -10 C): held zones exactly 21.0. A 9 kW pump at -25 C, valved and not, both zonings: held zones exactly 21.0. Both are checks in the block, and M4 kills each.
- Census control: the same harness at 69078d59 reads the class open (`## Figures`).
- Flat-price null (mandatory): `valve-flat` is the flat-price arm. Its residual carries no price term, and the store term is price-independent (+11.11 on both arms at this head).

## Figures

<!-- figure-block: scope-line mb=e59e21fee4629623f2f88ea83be76d527b7d0805 head=bace7b742be1fb14a2da817fec5a131c13105d43 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

- **Class enumeration.** The class is every bound on the heat the reference step delivers. That fact has no syntactic shape, so no grep enumerates it. The rule is the step's own path: `_compute_baseline_power` computes `_thermostat_demand`, then `power = min(power_for_heat_per_cop_kw(p, required / cop), p.max_electrical_power)`, then `ThermalModel.simulate_step`. Every cap, clip or derate on that path, read in `thermal_model.py`'s `_single_valve_rates`, `_valve_two_zone_delivery`, `_simulate_step_two_zone`, `_simulate_step_single`, `compute_cop` and `heat_per_cop_kw`, with its disposition:
  - `max_electrical_power`, the reference loop's clip: closed in this diff (`_held_unreachable`'s pump bound).
  - COP, including defrost (`defrost_derate`), flow lift at the tank temperature behind a valve, and the part-load derate (`partload_factor`): closed in this diff. The pump bound reads `_reference_cop` and inverts through `power_for_heat_per_cop_kw`, the loop's own conversions.
  - The valve curve's mix-down (`flow_set`, `t_mix`): closed by the PR's earlier commits (`valve_top_draw`).
  - `buffer_max_temp` (the charge cap): already guarded. `valve_top_draw` draws at `buffer_max_temp`, and `valve_hold_temperature`'s kinks are capped by it. A direct slab's uncapped top is capped by the same.
  - The tank's energy bound (`_tank_bounded_draw`, the two-zone available heat) and its standing loss: closed in this diff. The pump bound's `_thermostat_demand` on the held tank is draw plus loss, so a held state the pump can keep also keeps the tank.
  - The unvalved two-zone tank loss: closed in this diff, by the same `_thermostat_demand` term.
  - `WOOD_TANK_MAX_TEMP` and the wood draw: not a bound on the reference. The reference has no wood, and the held state empties a modelled wood tank (a check pins it).
  - `external_heat_kw` and `min_electrical_power`: neither is an upper bound. The first is free heat, and the second is not a clamp (`_compute_baseline_power`'s comment).
- **Census** (the class's property, every install class driven with the same inputs): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_held_capacity_census.py` (sha1 8d9afaacc33c...). It asserts its own preconditions: every grid case runs, every held room is in [min(outdoor, 21), 21], and the case count is the grid's product.
  - At bace7b74: `cases 1728 of 1728, worst first-step dS +0.0000 kWh_th ..., over 0.02 kWh_th 0`. Controls: two-zone at -25 C, a 4 kW pump holds -1.577 C unvalved and -0.928 C valved at power 4.000 and dS +0.0000; a 9 kW pump holds 21.000.
  - At 69078d59 (the same file, run against that head's code): `cases 1728 of 1728, worst first-step dS -1.0762 kWh_th at ('manual', True, None, 4.0, 25.0, -25.0, 21.0, 4.0), over 0.02 kWh_th 106`. Controls: 4 kW pump, held 21.000, dS -1.0724 (unvalved) and -1.0762 (valved); 9 kW, +0.0000.
- **Held state and first-step store change** (the block's `_svh_case` and `_svh_cap` rows): every row reads |dS| < 0.02 kWh_th at bace7b74 (`ALL 10 FEATURES BLOCK PASSED`).
- **Residual and attribution**: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat` and `winter_typical` (sha1 4b214a9bc277...), run at 056abe4d. `plant steps seen 192 of 192` at both arms.
  - At the base e59e21fe (the fix reviewer's re-take): residual -3.90 % (flat), -8.02 % (varying); reference stored -34.85 kWh_th.
  - At 69078d59 (the fix reviewer's re-take): residual +4.78 % / +1.20 %; reference stored -0.30; non-steady -0.30 / -0.93.
  - At 056abe4d: residual +6.84 % / +3.38 %; reference stored +11.11; non-steady -6.83 / -7.46. Carry: R10-SAV-VALUATION-RESIDUE
- **Store term split by class** (scratch probe wrapping `_compute_baseline_power` in `r10_sav_wood_reference.closed_loop`'s valve arm: each booked step 0 is stepped once from `_thermostat_held_state` at the booked power, and split by whether that held state's steady draw exceeds `max_electrical_power`):
  - At 69078d59: 50 steps above max, dS -13.20 kWh_th; 142 below, dS +12.90; total -0.30.
  - At fa365370: 0 steps above max, dS +0.00; 192 below, dS +11.11; total +11.11. The booked power exceeds the held equilibrium's power summed over the steps: +4.57 kW·step at 69078d59, +17.41 at fa365370.
  - Exposed seam, measured: with `_compute_baseline_power`'s call to `_apportion_by_steady_demand` removed on a scratch tree of fa365370, the same probe reads +0.00 in every step, and the flat harness reads residual +4.03 %, reference stored +0.00 kWh_th, booked reference 155.58 kWh_e (159.94 with the apportion). The apportion spreads the simulated horizon's energy, including the recovery from step 0's sag on later steps, over the steps by steady demand at the target, so step 0 is booked above the held equilibrium. Carry: R10-SAV-VALUATION-RESIDUE
- **Readers of the held state** (`git grep -n "_thermostat_held_state(" -- custom_components/`): the definition, `_compute_baseline_power` and `_start_gap_cost`. Both readers take the new state; none other exists.
- **Structure**: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at bace7b74. `python3 tools/audit/archscore/score.py --diff 69078d59a07a929555e77c79432e4aa655941bb2` prints `Architecture score: dS +0.0000 NULL`.
- **Gate**: `env -u BASH_ENV GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e59e21fe... PYTHONPATH=tests/hastub bash tests/run.sh` at bace7b74 prints `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN` (exit 0), including `ALL 5369 FEATURE CHECKS PASSED`, `ALL 2709 ENTITY CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED` and `ALL 115 HARNESS HEADER CHECKS PASSED`, with env_drift's golden drift check against the merge base passing and no claim file touched.
- **CI prediction**: `python3 tools/pr/ci_predict.py` at bace7b74 prints `no closures, fast, governance or instrument red predicted against e59e21fee462` and `7 unpinned site(s) the diff adds` (`## Unpinned sites`).

## Red checks

- At this head: `tests / mutation` is predicted red, as at 00a7af72, on the seven `ADDED UNPINNED` sites `## Unpinned sites` names, each killed by the group's block and measured, and left to `mutation-autofix`'s lane (`ci-autofix.md`). Root-cause answer: the cheaper detector exists and ran. `ci_predict.py` listed every site locally before the push, and each has a disposition; a red until the lane pins is the ratchet's route for a `custom_components/` kill, so nothing further is built.
- `tests / mutation` at 00a7af72 (job 131279233005, run 43245625153): `MUTATION TABLE REFUSED -- 2612 unpinned site(s) against 2608 at the ratchet base 19baca76..., 4 of them added by this diff`. `mutation-autofix` pinned all four in 11dc22c8, and `tests / mutation` there is green (job 131317100996: `MUTATION TABLE PASSED`). Root-cause answer: as the item above.
- `gate` at 00a7af72 (job 131283135569, run 43245635284): `FAIL run(s) [43245625153] at this head are still being judged; their gate decides`, `tools/ci/gate.py`'s `deferral()` to the reds on `tests / mutation` (above) and `arch-score / arch-score`. The latter failed on `gh: HTTP 503` fetching the pull request (job 131279233398), a GitHub API outage outside this repository, owner GitHub; it is green at 11dc22c8 (job 131317102626). Root-cause answer: no cheaper detector exists. The gate red is derived from the two reds, and the 503 is an outside service.
- `gate` at 11dc22c8 (job 131354606349, run 43256638000): the same `deferral()`, to `pr-contract / pr-contract` (next item). Root-cause answer: derived; it carries no cause of its own.
- `pr-contract / pr-contract` at 11dc22c8 (job 131353666654): `PR-BODY: 3 error(s)` on a body that predated the autofix commit and the 503. Root-cause answer: the cheaper detector is `prepr.sh --body-check`, run before every body push; no local run could have seen a later commit, so nothing further is built.
- `tests / nightly-status` (job 131367041075) is red at 11dc22c8 and is outside the set `python3 tools/audit/seat/merge_train.py owed-reds` prints; it grades `main`, so it is neither answered here nor a block.

## Unpinned sites

Each site is on `custom_components/`, the lane `mutation-autofix` mutates. Each kill was measured with the group's block (`## Mutation proof`'s command) at 056abe4d, whose production code is fa365370's.

- custom_components/heatpump_optimizer/optimizer.py:638 BOOLOP (`if valved or ...`): pinned by `mutation-autofix` (measured: the block raises `UnboundLocalError`)
- custom_components/heatpump_optimizer/optimizer.py:638 CMP_BOUND (`>= 0.0`): pinned by `mutation-autofix` (measured: FAIL the zero-demand check)
- custom_components/heatpump_optimizer/optimizer.py:638 GUARD_OFF: pinned by `mutation-autofix` (measured: 3 of 10 FAIL)
- custom_components/heatpump_optimizer/optimizer.py:641 RETURN_DEL: pinned by `mutation-autofix` (measured: the block raises `AttributeError`)
- custom_components/heatpump_optimizer/optimizer.py:647 GUARD_OFF: pinned by `mutation-autofix` (measured: 2 of 10 FAIL)
- custom_components/heatpump_optimizer/optimizer.py:649 CLAMP_DROP: pinned by `mutation-autofix` (measured: FAIL the warm-day check)
- custom_components/heatpump_optimizer/optimizer.py:685 RETURN_DEL: pinned by `mutation-autofix` (measured: FAIL the capacity check)
- custom_components/heatpump_optimizer/optimizer.py:602 CONST (`_HELD_BISECTIONS` 40 -> 80): triage `survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json` (equivalent; measured, block passes)
- custom_components/heatpump_optimizer/optimizer.py:685 CMP_BOUND (`>=` at the pump bound): triage `survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json` (equivalent; measured, block passes)
- custom_components/heatpump_optimizer/optimizer.py:596 CLAMP_DROP: pinned since 11dc22c8 (`killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json`; measured: 4 of 10 FAIL)

`prepr.sh`'s diff mutants (`MUTANT_CMD` = the block above) at ca118b90 left 7 survivors. Each, with its disposition at bace7b74:
- optimizer.py:627 CONST_SWAP `weather.humidity[1]`: killed (the capacity rows' one-step humidity series; `IndexError`).
- optimizer.py:685 CONST_SWAP `max(1.0, made)`: the clamp is deleted (it clamped nothing, `## Head`).
- optimizer.py:602 CONST_SWAP `_HELD_BISECTIONS = 41`: equivalent, as the CONST triage row argues (41 narrows the bracket by half of 2**-40).
- optimizer.py:634 and :683 CONST_SWAP, dt 0.25 to 0.5 in `need` and in the pump bound's `_thermostat_demand`: equivalent. At level zones on a tank at its hold temperature, the pull-back, slab-charge and tank-charge terms are zero, so dt multiplies nothing; measured: block passes.
- optimizer.py:679 CMP_BOUND, the valve bound's `>=`: equivalent. The arms differ only where the need equals the curve's top draw to the last bit, the equilibrium itself, and the bisection lands within 2**-40 of the span; measured: block passes. Not an inventory site (the condition spans lines), so no triage row keys it.
- optimizer.py:685 CMP_BOUND, the pump bound's `>=`: the triage row above.

Six ledger rows are deleted because the lines they key left the tree, and no inventory site keys them any more: `killed_by/.../_thermostat_held_state.CMP_BOUND.4aa37f7d`, `.GUARD_OFF.42081e68`, `.GUARD_OFF.5c05badb` (the unvalved early return, `ci_predict.py`'s `STALE PIN`), and `survivor_triage/.../@module.CONST.b8c7cb71`, `_thermostat_held_state.CMP_BOUND.42081e68`, `.CMP_BOUND.745fa965`. `_held_unreachable.CMP_BOUND.26b0566e`, added at 056abe4d, is replaced by `.ebd24b04` because the line it keys lost the clamp. Their lines' successors are the sites above.

## Forward-carry

- The apportion seam: `_apportion_by_steady_demand` books step 0 of a valved reference above its held equilibrium (+11.11 kWh_th over the valve arm at this head, +12.90 masked at 69078d59), measured with its control in `## Figures`. Removing the call from `_compute_baseline_power` measures +0.00 and residual +4.03 %. The mechanism is pinned by another group's checks in `tests/features.py` (the `_hz_` block that calls `_apportion_by_steady_demand`), so whether to remove it here, in part 2 or 3, or under its own group is a ruling for the orchestrator. Re-measure with `r10_sav_residual_attribution.py flat` at that stage's merge base; the precondition for removing it is the census reading 0 at that base, so that step 0 from the held state is no longer a transient. Carry: R10-SAV-VALUATION-RESIDUE

## Friction

none
