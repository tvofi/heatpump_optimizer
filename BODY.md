R10-SAV-COMFORT: the savings figures, settled on the owner's baseline specification (2026-10-24), and shown on the card cell for cell.

Part of #2492. Part of #201. #2492 stays open. Carry 5's seam 2 is not done here (see Forward-carry), and the group's roster row lists #2492 under `issues`, not `fixes`.

**The comfort-matched reference (optimizer.py).** The savings thermostat holds the comfort the plan delivered. `_comfort_matched_targets` lowers the comfort schedule by the plan's mean shortfall below it. The shift is uniform, so a dip the plan pays back with heat stored in a cheap hour stays a timing saving. A plan at or above the schedule on average leaves the schedule unchanged. The space path keeps its thermostat at the schedule as the solver's start. It runs a second thermostat at the matched schedule only when the shortfall is positive. `OptimizationResult.held_cost` is the thermostat at the schedule itself, and the advisor's degree price (`coordinator.py`, `monthly_held_cost_delta`) reads it. `_settle_horizon` is the one stored-heat settlement both solve paths book. `_start_gap_cost` debits a warm start by no more than the space heat the thermostat buys plus the end's credit.

**The thermostat at the meter's power levels (ledger.py).** Each settlement books one more line, `savings_plan`: the plan's own modelled kWh on the same intervals as `savings_baseline` and `savings_actual`. `MonthlyLedger.meter_calibration(month)` is metered kWh over modelled kWh, and the month row multiplies the modelled thermostat's cost by it. A month whose savings lines began before the plan line existed stays on the modelled basis, as does one whose plan booked under `MIN_CALIBRATION_KWH`. Both publish `meter_calibration: null`.

**One basis, card equal to the ledger.** In `ledger.savings_months`, Baseline, Actual and Savings are all the covered intervals at spot plus fee. Savings is computed from the two rounded cells. `month_cost` lost its last reader and is deleted. The row gains `meter_calibration` (`SavingsMonth`, payload.py).

**The duty ledger re-freezes `planned` at each plan adoption (pump_arbiter.py `_observe`).** A step is scored against the plan that actuated it.

**The thermostat's per-step inputs, read once (this pass, for tests / fast).** The matched reference's second thermostat pass took winter/1z/space/pin-off past stress.py's 1.05x production-call allowance. `_compute_baseline_power` now reads its setpoints, the humidity series, the two-tank flag and the floored slab coefficient once per pass, not once per step. The setpoints come from `_baseline_targets`, one array, and `_baseline_target` delegates to it, so the rule has one owner. The demand helpers take `k_slab`. `np.clip`'s lower bound was dead and is dropped: the demand is floored at 0 two lines above, and `compute_cop` returns `max(cop, 1.0)`. Every value is unchanged bit for bit (`env_drift.py --all`, below). Alternatives, and why each lost (`fixer.md` step 17):
- A scenario-scoped allowance in stress.py. It is not needed, because a payment existed, and stress.py's own rule forbids a raise for a single firing.
- Dropping the space path's thermostat at the schedule. It is the solver's start, so every plan would move.
- Deriving the matched pass from the first by linearity in the shift. The 0 and nameplate clips make the map non-affine, so it is not bitwise.
- A precomputed COP shared across passes. It would need a cop parameter on the public `simulate_step`, which widens a surface to save calls this payment did not need.

## Head

fb7683af246ccc5c23ebe5229e9447d58708207e, on merge base 73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec. This pass adds three commits to the PR head 46dc1dda8: 8f5fd0295 (the hoist and the structure re-record), 0355f7dc6 (four stale `_baseline_target` pins deleted) and fb7683af2 (two value checks). `git diff --stat 8f5fd0295 fb7683af2` names only tests/features.py and the four pin files, so the scoped gate run at 8f5fd0295 measured the same production code as the head. tests/features.py and tests/entities.py were re-run at the head. `origin/main` was at 2636ce9e9 when read (2026-10-24, about 19:50Z); the branch is not merged with it.

## Mutation proof

**This pass (tests / fast's production-call check).** The mutant is the hoist reverted, which is the PR head 46dc1dda8. stress.py's own channel (`capture_calls_pair`, `calls_drift`) against 73b69fe0a on winter/1z/space/pin-off gives:
- at 46dc1dda8: `over: ["winter/1z/space/pin-off: 84263 production calls against the baseline's 78480 = 1.074x on work the counts vouch at 1.001x, over the 1.05x allowance (thermal_model.py +4072, optimizer.py +1654)"]`;
- at fb7683af2: 82167 calls, `over: []`.

The objective is 60.1042784820211 on all three trees.

**The PR's fix.** `dev/audit/harnesses/r10_sav_comfort_mutants.py` was run on a `git ls-files` copy of 0355f7dc6, whose production code is the head's. M0 (unmutated): rc=0, failing=0. Every mutant fails at least one check:
- M1 failing=6
- M2 failing=2
- M3 failing=8
- M4 failing=5
- M5 failing=1
- M6 failing=4
- M7 failing=4
- M8 failing=1
- M9 failing=1
- M10 failing=1
- M11 failing=1
- M12 failing=1
- M13 failing=1
- M14 failing=1
- M15 failing=1
- M16 failing=2, the whole of features.py. One of the two is `#363 recorded_at`, which every copy without `.git` fails. The other is `#2257: the held figure prices a degree from a steady start ...`.
- M17 failing=3
- M18 failing=6
- M19 failing=1
- M20 failing=1
- M21 failing=9
- M22 failing=4
- M23 failing=2, the whole of features.py: `#363 recorded_at` and `#2492: a plan adopted mid-step re-freezes the step's planned duty ...`.
- M24 failing=2, tests/card.mjs: `#2492: the Savings tab's every cell is ledger.savings_months's ...` and `savings tab draws the estimated current-month row`.

Each mutant is named in the harness's `M` list.

## Null control

Each harness was run twice, from the head's file: once in a worktree of the merge base 73b69fe0a and once at the head.
- `r10_sav_volume.py flat`. Base: saving −64.51, volume −64.51, timing +0.00 (DEFECT, 0.2154 per metered kWh at one price). Head: 0.00, volume +0.00, timing +0.00, `meter_calibration` 1.56 (SOUND).
- `r10_sav_volume.py vary`. Base: 10.37 = volume −64.51 + timing +74.88. Head: 74.88, volume +0.00, timing +74.88.
- `r10_sav_volume.py gap`, a meter that reads the model. Base and head both save 48.0. Head `meter_calibration`: 1.0.
- `r10_sav_comfort.py const`. Base: +4.95 % saved against timing +0.00 % (DEFECT). Head: +0.35 % against −0.00 % (SOUND).
- `r10_sav_comfort.py vary`. Base: +20.03 % against timing +15.30 % (DEFECT). Head: +16.04 % against +15.31 % (SOUND).
- `r10_sav_baseline.py null`. Base: booked thermostat 128.4 kWh against 121.5 steady at the delivered room (DEFECT). Head: 121.8 against 121.5 (SOUND).
- `r10_sav_baseline.py transient`. Base: step 0 reads 2.06 kW from every start, 1.81e-01 kW off its steady holding power (DEFECT). Head: 1.90 / 1.88 / 1.95 kW, 8.88e-16 kW off (SOUND).
- The production-call channel's null control is the merge base itself: 78480 calls, the denominator above.

## Figures

- Production calls, one family: `PYTHONPATH=tests/hastub python3 <driver> <repo> 73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec winter/1z/space/pin-off`. The driver is a scratch probe that calls tests/stress.py's `sweep_combinations()`, `capture_calls_pair()` and `calls_drift()` and nothing else. Rule: `calls_over_verdict`, which is over when calls exceed baseline × vouched × (1 + `SCENARIO_CALLS_GROWTH`), where vouched is the larger of the evals and simulate ratios.
- Production calls, the class census (`fixer.md` step 8): tests/stress.py's own sweep at 8f5fd0295 printed `production calls: 20 of 20 family members judged against 73b69fe0a9fa ...; re-planned: []; new on this branch: []` and `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan`. That channel enumerates one member of every sweep family (`calls_population`), so every solve path that runs the thermostat is judged, and none is over.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec PYTHONPATH=tests/hastub bash tests/run.sh` at 8f5fd0295 printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. Every script was ok except tests/entities.py, at 3 of 2425. One of the three was the stale-pin refusal, which 0355f7dc6 removes. The other two are under Red checks.
- Goldens: in that run, `tests/env_drift.py --all 73b69fe0a...` and `--claims-only` were both ok. So the hoist moved no scenario, and the claims stand as `tests/golden/claimed_drift.txt` records them.
- tests/entities.py at the head and at 73b69fe0a, run side by side: `PYTHONPATH=tests/hastub python3 tests/entities.py`. Both print `2 of 2425 ENTITY CHECKS FAILED`, and they are the same two checks.
- tests/features.py at the head: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4377 FEATURE CHECKS PASSED`.
- Card equality (owner acceptance): `python3 tests/plan_view.py` then `node tests/card.mjs`. Both were ok in the scoped gate.
- Structure: `python3 tests/structure.py` exits 0. `class_excess_loc` went from 18209 to 18206 and was re-recorded with `--record`: the hoist shortened `HeatPumpOptimizer` by three lines. The reason is in 8f5fd0295's commit message.
- `node tools/policy/policy_lint.mjs --budgets` exits 0.
- Architecture: `python3 tools/audit/archscore/score.py --diff 73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec HEAD` and `... --diff 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e HEAD` both print `Architecture score: dS +0.0000 NULL`.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head prints `no closures or fast red predicted against 73b69fe0a9fa` and lists 6 unpinned sites, each under Unpinned sites.
- Harnesses, run at both ends with `PYTHONPATH=tests/hastub:tests:custom_components python3 <harness> <arm>`. The sha1 of each file is:
  - `dev/audit/harnesses/r10_sav_volume.py`: be62082cc746a336a5580742b3047b2acc8f17df
  - `dev/audit/harnesses/r10_sav_comfort.py`: 6615a321e3169db377b9c661f689ade65c31f78e
  - `dev/audit/harnesses/r10_sav_baseline.py`: 88ac23e4b83a349789b5c6674e0cbee6021e736f
  - `dev/audit/harnesses/r10_sav_comfort_mutants.py`: 4ea9f082d160c3a8a1aee430ef96b98eb8ba5f76
  - `dev/audit/harnesses/r10_sav_comfort_opmutants.py`: 76ea211845c8608ba6ab25d7fecb0109bc67f386
- Readers of a savings row: `grep -rnE "savings_months|savings_sek|savings_pct|baseline_sek|actual_sek" custom_components/ --include=*.py --include=*.js`, with ledger.py excluded, returns 25 lines in five files:
  - coordinator.py, the payload source;
  - sensor.py, which passes the row through;
  - notifier.py, the receipt;
  - www/heatpump-optimizer-card.js, the tab and the receipt;
  - payload.py, the field list.

  Each one reads the row; none recomputes it.

## Red checks

- `tests / fast (3.14)`, stress.py: "no scenario's production calls grew past what its work counts vouch for, on an unchanged plan". On winter/1z/space/pin-off it read 84263 calls against 78480, 1.074x over the 1.05x allowance. Cause: the matched reference's second thermostat pass, 96 steps of per-step reads that no state moves.
  - Answer: paid in code, with no allowance and no raise (see the hoist above). At the head the channel reads 82167, 1.047x, and none of the 20 families is over.
  - Cheaper detector: one exists, and it fired before CI. The scoped gate runs tests/stress.py, and the previous handoff's local run printed this verdict. That handoff disposed of it as an owner-review pass instead of paying it, so nothing went undetected. No new detector is owed.
- `tests / fast`, tests/entities.py, 2 of 2425: "gate-sweep.yml: on CI's completion ... (U0c)" and "graders-head-copy's delivery_status step is red only when ...". Both fail identically at the merge base 73b69fe0a in this environment, so they are not this diff's. No root cause is owed here.
- `tests / mutation`: red until `mutation-autofix` pins the 6 sites under Unpinned sites. The predictor (prepr step 6d) printed every site before the push, and each one was driven and killed.
- `tests / ci-ratchet`: if it is red, it is main's own push red (the repo-wide artifacts listing), not this diff's. This PR does not touch tests/ci_ratchet.py.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` at the head lists 6 sites. Each one was driven by `tests/mutation_table.py`'s own operator mutant (`candidates()`), using `dev/audit/harnesses/r10_sav_comfort_opmutants.py <copy> full <key>`. Each run used a `git ls-files` copy of the head, beside an unmutated null: rc=1, failing=1, the `#363 recorded_at` check every copy without `.git` fails. Kill rule: `mutation_table.killed()`, a run naming more failing checks than the null. All 6 are killed, so each is pinned by `mutation-autofix`:
- `optimizer.py:324 RETURN_DEL` (`_baseline_target`'s return): failing=3. The three are D1-s2-51, D1-s4-02 (control) and D1-s2-04, all `solve_failed` (the solve raises).
- `optimizer.py:333 GUARD_OFF` (`if comfort_targets is not None:`): failing=7. They include `a night setback lowers the reference, not the reported savings` and `past the comfort schedule's end the thermostat holds the default setpoint ...`.
- `optimizer.py:336 RETURN_DEL` (`return targets.tolist()`): failing=3, the same three `solve_failed` checks as :324.
- `optimizer.py:5294 BOOLOP` (`two_tank or ...`): failing=2. The check that kills it is `the savings reference backs off by the wood share on the two-tank layout, and a wood reading on any other layout moves it not at all`, added in fb7683af2. Before that check existed this site and the next survived tests/features.py at the null's count. They were also unpinned before the hoist, because the condition spanned lines.
- `optimizer.py:5294 GUARD_OFF`: failing=2, the same check.
- `optimizer.py:5335 CLAMP_DROP` (`power = (required_thermal / cop)`): failing=2. The check that kills it is `a demand past the pump's nameplate holds the reference at max_electrical_power`, added in fb7683af2: it reads 1.469 kW against a 1.0 kW pump.

## Forward-carry

- Carry 5, seam 2: actuate the supply switch at step boundaries from a one-minute tick, rather than at the cycle phase. Its owed controls are a synthetic install with the cycle phase at 0 and at 14 min that books identical duty verdicts, and one mutant per seam. It moves the actuator edge (`coordinator._apply_action`, `early_cutoff`, `pump_arbiter.switch_supply`) and needs a design note first. The orchestrator ruled (2026-10-24) that an actuation-seam group carries it. On `origin/main` at 2636ce9e9, `dev/programme/rosters/wave-r10-groups.json` holds no such group yet: R10-SAV-COMFORT is the only row naming 2492. This seat writes no roster. Carry: dev/programme/rosters/wave-r10-groups.json

## Friction

- dispatch-return-ref: contradiction: PROMPT.md's Output line names `handoff/r10-sav-comfort-r4` and `body_push.sh r10-sav-comfort-r4`, and its brief names the topic `r10-sav-comfort`. The brief's later, explicit line was followed. Carry: dev/governance/roles/orchestrator.md
