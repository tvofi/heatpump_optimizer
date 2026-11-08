R10-COMBI-TANK-STORE (R10-COMBI-TANK PR A, L; design `a605014bff4478f470853109060f4ff7ef605d4c`, approved by `design-verdict/r10-combi-tank` `56810263b`, Cost and Order section's PR A scope). Issue #3225 (outside user Bankaifan): a combi store, where one body of heating water serves the space circuit and hot water through an exchanger, cannot be modelled; entering the store as both tanks counts its heat twice. This PR lands the store physics. **No loader or option sets `dhw_combi_tank_enabled`**, so no install can reach combi, and with the option off every plan is byte-identical (golden drift, below). Refs #3225; PR B (R10-COMBI-TANK, topic `r10-combi-tank-b`) makes it reachable and closes it. This PR closes no issue.

What changes:
- **`thermal_model.py` owns the store.** `DhwStore` (frozen, module level) is the one view every hot-water recursion reads, through `ThermalParameters.dhw_store`. Off combi it is the separate tank's own values and both transforms return their argument itself. In combi it is the buffer store over `buffer_store_volume` (buffer plus potable litres), with the buffer's UA, the tighter of the DHW and buffer limits, and the exchanger effectiveness `combi_dhw_effectiveness` (floored at `COMBI_DHW_EFFECTIVENESS_FLOOR`, capped at 1). `combi_tank_active` is the design's predicate. The tank type is two numbers (`combi_dhw_effectiveness`, `combi_potable_volume_l`), never a code branch (Carry 2).
- **One step, both stores.** `store_step` is the hot-water step for the separate tank and the combi store alike; `simulate_dhw_step`'s body was a second copy of exactly this physics and now calls it, bitwise identical off combi. The draw is debited at the tap temperature (`tap_temp_for_store`), the rating clamp and inlet floor book what they refuse or inject, so `C·dT = (heat_in − draw − loss − refused + injected)·dt` per step.
- **The flux exchange (design, Solver).** The space steps (`_simulate_step_single`, `_simulate_step_two_zone`, `simulate_trajectory_batch`) take the hot-water side's net flux as `WeatherSeries.buffer_exo_kw`, joined to the tank's input behind the valve; every DHW recursion takes the space side's as `tank_exo_kw` (the LP's free trajectory, the legionella walk and reach ramp, the capacity clamp, the min-run repair, the floor repair, the greedy pass, the suppression walk). The published walk (`simulate_trajectory_with_dhw`) is one node: its DHW trajectory is its buffer trajectory.
- **Departure, raised: the exchange is a bounded repair, not a scored candidate.** The design's one extra iteration under the "adopt only if it scores better" gate never adopts: the replan buys more hot water, so it always scores worse on the space objective, and the space side drains the store below the DHW floor: that shape publishes the first plan, which is the harness's `exchange` arm at zero rounds (its `null_worst_shortfall_c`, below). `_combi_flux_exchange` re-plans hot water against the fixed space plan's net flux until the plan stops moving, at most `_COMBI_EXCHANGE_ROUNDS` (4) DHW builds, and keeps the space plan it was computed against: a space re-solve would draw the repair straight back out. `exchange` arm below: 3 rounds, no shortfall; its null (0 rounds) falls short.
- **Readers moved to the view** (census `combi_store_view`): `battery.build` drops `dhw_tank` in combi (the `buffer_tank` component is the store); `_deferred_energy_cost` and `_stored_thermal_energy` skip the DHW term when two-zone already counted the buffer; the setpoint sweep, `_max_pump_rise("dhw")`, `async_fold_draw_stats` and the baseline read `dhw_store`. The litres-at-40 rule moves from the coordinator into `thermal_model.dhw_mixed_litres` (combi: the heat above the store temperature that gives 40 °C at the tap).
- **Tap limits enter the store frame; the legionella target never does** (§T.2a, census `combi_tap_limit`): `dhw_min_temp` and `dhw_idle_min_temp` in `_dhw_window_floors`, the LP's COP floor and `dhw_hold_hours` pass through `store_temp_for_tap`; every `dhw_legionella_temp` read is an identity site.
- **The planner ignores a space-flux series for a separate tank** (`DhwStore.space_flux`): it shares no water with the space side, so the series is dead off (`lp_flux` null control).

Group carries (roster `R10-COMBI-TANK` at `origin/handoff/audit-r10-roster`, numbered as the roster numbers them; the dispatch brief at `ff395bd0` numbers the same seven 0-6, and the comments in `tests/features.py` and the harness cite the web report by the brief's number, `carry 4, item 1`, which is the roster's Carry 5), one disposition each:
- **Carry 1** (no-probe buffer seed): closed by PR 0, #3268 (`_seed_store` on main). Nothing here.
- **Carry 2** (physically sound, general): the model conserves energy across both volumes as one node (`combi_energy_balance`, residual below), its UA = 0 null control conserves the fluxes to 1e-12, eps moves only tap-stated limits and the below-mixer debit (`eps null control`), and the type is two numbers. The survey and the preset table are PR B's (§T.4).
- **Carry 3** (robustness, integration efficiency, architecture, maintainability): one owner (`thermal_model.py`), one step function for both stores, no type branch, off path byte-identical; the structure ratchet moved down (`class_excess_loc` −12, `max_class_loc` −2) and the architecture score is NULL.
- **Carry 4** (web verification before PR B): binds PR B.
- **Carry 5** (the folded report): PR A takes only item 1's UA. The issue fixture in `tests/features.py` and the harness is the manual's store: 504 l heating volume, 40 l coil, and the ErP standing loss 111 W at 65 °C entered as the cooling rate that gives UA 111/45 W/K; the check asserts the store's UA equals it to 1e-12. The preset and help-text items bind PR B.
- **Carry 6** (open-loop DHW seed from a measured tank temperature): answered by PR 0 (`_seed_store` reads an ok probe first); the combi seed is PR B's `combi_tank_seed`.
- **Carry 7** (the `Co-authored-by: Bankaifan` trailer on the PR that lands the multi-tank setup): not landed here, because PR A lands no setup an install can reach; carried to PR B below.

## Head

`d28e0e411600e0f3c72eb0de40912ff521b90b9a` is the handoff head: this branch merged with `origin/main` `20e83746f` (merges only, no rebase), origin/main's tip at 2026-11-08T22:52Z and the merge base. The evidence below was taken at `d6a6fb72cd5e998ebae74b84f68ac7cd86672918`, the previous merge (with origin/main `51cd5ec8a42a`, the base the figures name); the last two merges brought tools/CI (prepr.sh and the budget-raise gate among them), a card browser test and delivery records, and `git diff --stat d6a6fb72c d28e0e411 -- custom_components tests/features.py tests/entities.py tests/guard_pins.py dev/audit/harnesses/r10_combi_tank.py` is empty. Re-taken at `d28e0e411`: the scope (`MODE: SCOPED -- 27 script(s) run, 6 scoped out.`), `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `tools/pr/ci_predict.py` (no closures, fast, governance or instrument red against `20e83746f`) and `tools/pr/prepr.sh` on this body. origin/main moved to `fdc8d21ad` after that run (2026-11-08T23:23Z); `git merge-tree --write-tree origin/main HEAD` reports no conflict, so per `fixer.md` step 6 the head was left as it is. Branch start: origin/main `17e621f08`, with the PR-0 tip `0ec5d1852` already its ancestor (#3268), so `handoff/r10-combi-tank` fast-forwards onto this head.

## Mutation proof

Each mutant was applied to a detached worktree at the head `d6a6fb72c`, the `R10-COMBI-TANK-STORE` block of `tests/features.py` was run on `tests/features.py`'s own prelude (the block's imports and helpers, check names unchanged), and the file was restored. FAIL lines are check names:
- **M1** combi branch of `dhw_store_of` dropped (always the separate tank): 9 FAIL, among them `combi: the DHW store is the buffer store, potable water included: one capacity, one loss`; `combi battery: no dhw_tank beside the buffer_tank, whose capacity is the store's`; `lp_flux: a 2 kW valve draw before the window raises the hot water the plan buys, and the store still meets every floor and the window's ready temperature`; `combi flux exchange: the joint plan's store meets the hot-water requirement the space side drains, and its published DHW and buffer trajectories are one`.
- **M2** exo out of the LP's free recursion: FAIL `combi_flux_live census: every DHW walk the planner runs, and each of its three affine recursions, carries the space side's flux, and both space walks read the DHW side's`. Only the census kills it: the LP is a seed, and the repair and greedy stages, which do carry the flux, close what the seed under-buys. Said, not hidden.
- **M3** exo out of the capacity clamp's `allowed`: FAIL `lp_flux: ...`.
- **M4** exo out of the legionella run-up walk: FAIL `combi_flux_live census: ...` (census only, as M2: the walk sets floors the floor repair re-checks against the flux-carrying simulation).
- **M5** battery's combi drop removed: FAIL `combi battery: no dhw_tank beside the buffer_tank, whose capacity is the store's`.
- **M6** settlement skip removed (`_stored_thermal_energy`): FAIL `combi settlement: two-zone counts the store once, as the buffer; single-zone counts it as the DHW term at the store's capacity; off, the separate tank's`.
- **M7** potable volume dropped from `buffer_store_volume` (the double-count mutation of design T.3): FAIL `combi: the DHW store is the buffer store, potable water included: one capacity, one loss`.
- **M8** draw debited at the store temperature, not the tap: FAIL `combi eps null control: with the tap above the mixer, eps 0.6 and 1.0 walk the same store; below it, the colder tap debits less`.
- **M9** legionella target routed through eps at `_dhw_legionella_due`'s ready-temperature write: FAIL `legionella_eps: the cycle's step, hour and target are the same at eps 0.6 and 1.0`; `combi_tap_limit census: every tap-stated minimum the planner and the hold horizon read enters the store frame, and the legionella target never does`.
- **M10** flux exchange skipped in `_co_optimize`: FAIL `combi flux exchange: ...`.
- **M11** single-zone space step's exo dropped: FAIL `combi flux exchange: ...`.
- **M12** `_dhw_window_floors`' tap transform dropped: FAIL `combi: a 45 C tap minimum is a 51.18 C store floor at eps 0.85 (inlet 10 C), in the planner's floors and the hold horizon alike`; `combi_tap_limit census: ...`.
- **M13** exo dropped from `_dhw_shortfall`'s walk: FAIL `lp_flux: ...`; `combi_flux_live census: ...`.

Failing first: the block run against the merge base's production tree (a detached worktree at `51cd5ec8a`, this head's `tests/features.py` copied in, sha1 `691b37ce`) printed `21 of 22 COMBI BLOCK FAILED`: every check of the block fails, and the 22nd is the prelude's own. The three censuses there enumerate the class's seams (listed under `## Figures`).

## Null control

- **Option off, the whole plan:** golden drift, `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, against the merge base (`## Figures`). No claim file is touched.
- **Option off, field for field:** `combi off: the store is the separate tank's own values, bitwise, and the transforms return their argument itself`; harness `off_store_bitwise=1`.
- **Preconditions:** `combi needs the store: no valve, a small tank, no hot water or the wood coil each leave the separate tank in force`.
- **Separate tank and a space-flux series:** `lp_flux null control: a separate tank's plan is unchanged by the same series` (harness `lp_flux_separate_none_kwh` equals `lp_flux_separate_draw_kwh`).
- **UA = 0:** the store conserves its fluxes to 1e-12 relative (`ua_zero_residual_kwh`).
- **eps above the mixer:** eps 0.6 and 1.0 walk the same store, bit for bit (`eps_0.6_end_c` equals `eps_1.0_end_c`), with a live leg below the mixer in the same check.
- **No exchange:** zero exchange rounds leaves the store short of its requirement (`null_worst_shortfall_c`); the battery and settlement nulls are their checks' off arms.

## Unpinned sites

`tools/pr/ci_predict.py` lists 61 sites the diff adds, all under `custom_components/`. Disposition of each: **unmeasured, owed to `mutation-autofix`** (`ci: pin killed mutants`); `--pin-killed` did not run on this head (`ci-autofix.md`). The thirteen hand mutants above cover the fix's own predicates; a survivor the lane names is triaged then, by hand.

- `custom_components/heatpump_optimizer/battery.py:326 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/battery.py:326 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:107 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:264 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:269 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:617 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:624 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:627 CMP_BOUND`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:835 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:1413 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1386 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1397 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1397 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1404 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1412 CONST`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1444 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:1447 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:3294 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:3294 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:5562 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:5797 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:329 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:329 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:331 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:336 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:636 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1909 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1911 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1915 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1917 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1922 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1927 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1927 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1929 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1941 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1941 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1948 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1948 CMP_BOUND`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1951 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1952 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1987 CMP_BOUND`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1987 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1991 CLAMP_DROP*2`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1993 CMP_BOUND`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1993 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1996 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1999 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2000 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2013 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2014 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2015 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2016 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2040 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2068 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:2070 RETURN_DEL`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:3373 CLAMP_DROP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:3692 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:3692 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:4406 BOOLOP`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:4406 GUARD_OFF`: unmeasured, `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:4696 GUARD_OFF`: unmeasured, `mutation-autofix`

## Figures

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` prints `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, its golden lane `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; `tests/stress.py` and `tests/entities.py` ran inside it under the lease.
- `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4999 FEATURE CHECKS PASSED` (run at `bb3db519e`, whose tree differs from this head only by main's governance merge).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `class_excess_loc` 17558 → 17546 and `max_class_loc` 7933 → 7931 were re-recorded, the reason in the commit message (the shared `store_step`, `dhw_mixed_litres` out of the coordinator, four planner walks onto `_dhw_plan_temps`). Seam map: no coordinator method added or renamed.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py` prints `no closures, fast, governance or instrument red predicted`; its three STALE PIN lines were repaired by deleting the pins' files.
- Typing: `env -u PYTHONPATH /opt/hpo/venv-ha/bin/python -m mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --python-version 3.13 custom_components/heatpump_optimizer` reports no error (the one `no-any-return` the first gate run found is fixed).
- Size: `git diff --shortstat $(git merge-base origin/main HEAD) HEAD -- custom_components` prints `6 files changed, 524 insertions(+), 243 deletions(-)`.
- Harness `dev/audit/harnesses/r10_combi_tank.py`, sha1 `29f43f1ed7e5a945377a643ae9032b2d62e87ad7`, at the head (`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py`); at the base it cannot run, the combi fields do not exist, and its checks' base reading is the `21 of 22` above:
  - `issue`: `workaround_tank_components=2`, `workaround_tank_kwh_per_c=1.1693` (504 l counted twice) against `combi_tank_components=1`, `combi_tank_kwh_per_c=0.6310` (one store, 544 l); `combi_store_ua_w_per_k=2.4667` (111/45).
  - `off_identity`: `off_store_bitwise=1`.
  - `balance` / `ua_zero`: `balance_residual_kwh=-7.105e-15`, `ua_zero_residual_kwh=3.553e-15`.
  - `eps_null`: `eps_0.6_end_c` = `eps_1.0_end_c` = `62.088350802154`, from 64.5 °C.
  - `legionella_eps`: `(True,4,1.0)` at both eps.
  - `lp_flux`: combi `3.0285` → `6.7956` kWh under the 2 kW valve draw; separate `3.1405` → `3.1405` (the dead series).
  - `exchange`: `exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455` (no shortfall), `exchange_dhw_kwh=22.135`, `exchange_solve_s=2.35`; null `null_rounds=0`, `null_worst_shortfall_c=28.767`, `null_dhw_kwh=5.327`, `null_solve_s=2.21`. The seconds are this container's wall clock, one solve each.
- The class census (step 8): three censuses in `tests/features.py`, registered in `_P2_CENSUSES`, each asserting its own reach. At the merge base they return the class's seams, every one dispositioned **closed in this diff**:
  - `combi_store_view`: 17 readers of the separate tank's C or UA outside thermal_model.py at base (battery.py 327, 331; coordinator.py 4457, 4493, 5144; dhw_learning.py 421; dhw_planner.py 373, 612, 817, 905, 1373, 1640, 1817, 1818, 2077; optimizer.py 5476, 5710); 0 at the head.
  - `combi_flux_live`: 11 flux-blind DHW walks at base (dhw_planner.py 485, 1200, 1501, 1556, 1575, 1768, 1870, 1933, 1978, 2010, 2166), the three affine recursions without the flux, and both space walks; all carry it at the head. The baseline replay (`_baseline_dhw_economics`) runs no walk, so the design's "485 passes None" row is moot: 485 is the legionella reach ramp, and it now carries the flux.
  - `combi_tap_limit`: 5 raw tap reads at base (dhw_planner.py 811, 813, 1392; thermal_model.py 3151, 3152); 0 raw at the head, and no `dhw_legionella_temp` read passes through eps.

## Red checks

- `tests / mutation`: predicted red, not yet run (no pull request exists, so no check has run on these commits): the 61 unpinned sites the diff adds, listed under `## Unpinned sites`. Cure: `mutation-autofix` drives each site's lane mutant and pins the kills by a `ci: pin killed mutants` commit (`ci-autofix.md`); a survivor it names is triaged by hand. The cheaper detector exists and ran before the handoff: `prepr.sh` step 6d / `tools/pr/ci_predict.py` listed every site, at no standing cost beyond that step. No new detector is owed.

No other check has run on these commits. Locally, the first scoped gate at `a97cd0ed9` read `2 TEST SCRIPT(S) FAILED`: `tests/features.py` (two test stand-ins replacing `extend_dhw_temps` and `_dhw_raise_fits` kept the old signatures, and the #1520 humidity-seam census could not read `humidity` through a star-args call) and `tests/typing_ruler.py` (one `no-any-return`). All three were fixed before this head; the cheaper detector existed and ran, the scoped gate itself, before any push to a handoff ref.

## Forward-carry

- PR B must empty `unwired_combi` in `tests/features.py` (`the combi store's fields are reachable from no config key until PR B wires them`) when its loader wires the three fields; the check refuses itself the day a wired field stays in the set. Control: the check's own reading at this head (`probe` None for all three). Carry: R10-COMBI-TANK (item unwired-combi-set)
- The flux exchange is a feasibility repair adopted without a score, on the fixed space plan; in combi the hot-water channel buys the heat the space side draws from the store (harness `exchange_dhw_kwh=22.135` against `null_dhw_kwh=5.327` on the same day). PR B's display and accounting (the DHW kWh tile, savings attribution) must read the store's charge as one channel or say which split it shows; re-measure with the harness's `exchange` arm at PR B's merge base. Carry: R10-COMBI-TANK (item exchange-accounting)
- The exo term in the LP's free recursion and in the legionella run-up walk is killed only by the syntactic census `combi_flux_live` (mutants M2, M4): the later planner stages close what the seed under-buys. PR B, or any stage changing the planner's stages, keeps that census and does not read lp_flux as covering those two sites. Carry: R10-COMBI-TANK (item exo-seed-census-only)
- Carry 7, the `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` trailer: not landed here; PR B lands the setup an install reaches and carries it in one of its own commits. Carry: R10-COMBI-TANK (item bankaifan-trailer)

## Friction

none
