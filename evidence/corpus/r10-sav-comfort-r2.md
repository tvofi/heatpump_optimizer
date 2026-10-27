R10-SAV-COMFORT: the savings figures, settled on the owner's baseline specification (2026-10-24), and shown on the card cell for cell.

Part of #2492. Part of #201. #2492 stays open. Carry 5's seam 2 is not done here (see Forward-carry), and the group's roster row lists #2492 under `issues`, not `fixes`.

**The comfort-matched reference (optimizer.py).** The savings thermostat holds the comfort the plan delivered. `_comfort_matched_targets` lowers the comfort schedule by the plan's mean shortfall below it. The shift is uniform, so a dip the plan pays back with heat stored in a cheap hour stays a timing saving. A plan at or above the schedule on average leaves the schedule unchanged. The space path keeps its thermostat at the schedule as the solver's start. It runs a second thermostat at the matched schedule only when the shortfall is positive. `OptimizationResult.held_cost` is the thermostat at the schedule itself, and the advisor's degree price (`coordinator.py`, `monthly_held_cost_delta`) reads it. `_settle_horizon` is the one stored-heat settlement both solve paths book. `_start_gap_cost` debits a warm start by no more than the space heat the thermostat buys plus the end's credit.

**The thermostat at the meter's power levels (ledger.py).** Each settlement books one more line, `savings_plan`: the plan's own modelled kWh on the same intervals as `savings_baseline` and `savings_actual`. `MonthlyLedger.meter_calibration(month)` is metered kWh over modelled kWh, and the month row multiplies the modelled thermostat's cost by it. A month whose savings lines began before the plan line existed stays on the modelled basis, as does one whose plan booked under `MIN_CALIBRATION_KWH`. Both publish `meter_calibration: null`.

**One basis, card equal to the ledger.** In `ledger.savings_months`, Baseline, Actual and Savings are all the covered intervals at spot plus fee. Savings is computed from the two rounded cells. `month_cost` lost its last reader and is deleted. The row gains `meter_calibration` (`SavingsMonth`, payload.py).

**The duty ledger re-freezes `planned` at each plan adoption (pump_arbiter.py `_observe`).** A step is scored against the plan that actuated it.

**The thermostat's per-step inputs, read once (for tests / fast's production-call check).** The matched reference's second thermostat pass took winter/1z/space/pin-off past stress.py's 1.05x production-call allowance. `_compute_baseline_power` now reads its setpoints, the humidity series, the two-tank flag and the floored slab coefficient once per pass, not once per step. The setpoints come from `_baseline_targets`, one array, and `_baseline_target` delegates to it, so the rule has one owner. The demand helpers take `k_slab`. `np.clip`'s lower bound was dead and is dropped: the demand is floored at 0 two lines above, and `compute_cop` returns `max(cop, 1.0)`. Every value is unchanged bit for bit (`env_drift.py --all`, below). Alternatives, and why each lost (`fixer.md` step 17):
- A scenario-scoped allowance in stress.py. It is not needed, because a payment existed, and stress.py's own rule forbids a raise for a single firing.
- Dropping the space path's thermostat at the schedule. It is the solver's start, so every plan would move.
- Deriving the matched pass from the first by linearity in the shift. The 0 and nameplate clips make the map non-affine, so it is not bitwise.
- A precomputed COP shared across passes. It would need a cop parameter on the public `simulate_step`, which widens a surface to save calls this payment did not need.

**The claim file keeps main's claims.** `tests/golden/claimed_drift.txt` adds this branch's own R10-SAV-COMFORT claims, and suspends the may-drift entry of each fixture it claims, since a fixture cannot be both. Main's five R10-SCORES lines (coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone) stand verbatim, restored in 28ddae464 after the previous handoff had deleted them.

## Head

28ddae464f8996f2e7233140c67e5f2e1e62daae, on merge base c176ee55de7c658b0b870182c5dd55d0843ad8f7 (`origin/main` when read, 2026-10-24T23:06Z). The pass adds two commits to the previous handoff fb7683af2: 0bc4445ac merges `origin/main` c176ee55d, and 28ddae464 restores main's five claim lines. `git diff --stat 73b69fe0a c176ee55d -- custom_components/ tests/features.py tests/card.mjs tests/stress.py` prints nothing, so the merge moved no production file and no test file this fix reads. Every figure below was re-taken at 28ddae464 or against c176ee55d. Returned on handoff/r10-sav-comfort-r2, the ref PROMPT.md's Output line names.

## Mutation proof

`dev/audit/harnesses/r10_sav_comfort_mutants.py <copy>`, run on a `git ls-files` copy of 28ddae464. M0 (unmutated): rc=0, failing=0. Every mutant fails at least one check:
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

Each mutant is named in the harness's `M` list. The production-call payment (the hoist) is proven by its own channel: tests/stress.py at the head judges 20 of 20 family members against c176ee55d and none is over (Figures). The hoist reverted is the earlier head 46dc1dda8, which that channel read at 1.074x on winter/1z/space/pin-off, over the 1.05x allowance; the production code it measured is unchanged since.

## Null control

Each harness was run from the head's file, once in a worktree of the merge base c176ee55d and once at the head:
- `r10_sav_volume.py flat`. Base: saving −64.51, volume −64.51, timing +0.00 (DEFECT, 0.2154 per metered kWh at one price). Head: 0.00, volume +0.00, timing +0.00, `meter_calibration` 1.56 (SOUND).
- `r10_sav_volume.py vary`. Base: 10.37 = volume −64.51 + timing +74.88. Head: 74.88, volume +0.00, timing +74.88.
- `r10_sav_volume.py gap`, a meter that reads the model. Base and head both save 48.0. Head `meter_calibration`: 1.0.
- `r10_sav_comfort.py const`. Base: +4.95 % saved against timing +0.00 % (DEFECT). Head: +0.35 % against −0.00 % (SOUND).
- `r10_sav_comfort.py vary`. Base: +20.03 % against timing +15.30 % (DEFECT). Head: +16.04 % against +15.31 % (SOUND).
- `r10_sav_baseline.py null`. Base: booked thermostat 128.4 kWh against 121.5 steady at the delivered room (DEFECT). Head: 121.8 against 121.5 (SOUND).
- `r10_sav_baseline.py transient`. Base: step 0 reads 2.06 kW from every start, 1.81e-01 kW off its steady holding power (DEFECT). Head: 1.95 kW, 8.88e-16 kW off (SOUND).
- The mutation proof's null is M0 above; each operator-mutant run's null is its unmutated copy (Unpinned sites).

## Figures

- Harnesses, both ends: `PYTHONPATH=tests/hastub:tests:custom_components python3 <harness> <arm>`, from a worktree of c176ee55d and from the head. sha1 of each file:
  - `dev/audit/harnesses/r10_sav_volume.py`: be62082cc746a336a5580742b3047b2acc8f17df
  - `dev/audit/harnesses/r10_sav_comfort.py`: 6615a321e3169db377b9c661f689ade65c31f78e
  - `dev/audit/harnesses/r10_sav_baseline.py`: 88ac23e4b83a349789b5c6674e0cbee6021e736f
  - `dev/audit/harnesses/r10_sav_comfort_mutants.py`: 4ea9f082d160c3a8a1aee430ef96b98eb8ba5f76
  - `dev/audit/harnesses/r10_sav_comfort_opmutants.py`: 76ea211845c8608ba6ab25d7fecb0109bc67f386
- Scope: `python3 tests/closure.py select --diff c176ee55de7c658b0b870182c5dd55d0843ad8f7 --workdir <dir>` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=c176ee55de7c658b0b870182c5dd55d0843ad8f7 PYTHONPATH=tests/hastub bash tests/run.sh` at the head, under a `tests/gate_lock.py` lease. Every script was ok except tests/entities.py, 2 of 2425, both under Red checks.
- Goldens: in that run `tests/env_drift.py --all c176ee55d...` and `--claims-only` were both ok, so main's R10-SCORES claims and this branch's own read no stale claim and no unclaimed drift.
- Claim diff: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` removes no claim line: its only `-` lines are the suspended may-drift entries, each restated under its suspension note. card_claimed_drift.txt is byte-identical to main's.
- Production calls, the class census (`fixer.md` step 8): tests/stress.py in that run printed `production calls: 20 of 20 family members judged against c176ee55de7c... ; re-planned: []; new on this branch: []` and `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan`. Rule: `calls_over_verdict`, over when calls exceed baseline × vouched × (1 + `SCENARIO_CALLS_GROWTH`); the channel enumerates one member of every sweep family (`calls_population`).
- Card equality (owner acceptance): `python3 tests/plan_view.py` then `node tests/card.mjs`, both ok in the scoped gate.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at the head. The earlier `class_excess_loc` re-record (18209 to 18206) carries its reason in 8f5fd0295's commit message.
- `node tools/policy/policy_lint.mjs --budgets` exits 0.
- Architecture: `python3 tools/audit/archscore/score.py --diff c176ee55de7c658b0b870182c5dd55d0843ad8f7 HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head prints `no closures, fast, wave-script or instrument red predicted against c176ee55de7c` and 6 unpinned sites, each under Unpinned sites.
- Readers of a savings row: `grep -rnE "savings_months|savings_sek|savings_pct|baseline_sek|actual_sek" custom_components/ --include=*.py --include=*.js`, ledger.py excluded, returns lines in five files: coordinator.py (the payload source), sensor.py (passes the row through), notifier.py (the receipt), www/heatpump-optimizer-card.js (the tab and the receipt), payload.py (the field list). Each reads the row; none recomputes it.

## Red checks

- `tests / fast (3.14)`, stress.py, at the earlier head 46dc1dda8: "no scenario's production calls grew past what its work counts vouch for, on an unchanged plan". On winter/1z/space/pin-off it read 84263 calls against 78480, 1.074x over the 1.05x allowance. Cause: the matched reference's second thermostat pass, 96 steps of per-step reads that no state moves.
  - Answer: paid in code, with no allowance and no raise (the hoist above, 8f5fd0295). At this head the channel judges 20 of 20 families against c176ee55d and none is over (Figures).
  - Cheaper detector: one exists, and it fired before CI. The scoped gate runs tests/stress.py, and the handoff before 46dc1dda8's push printed this verdict locally; that handoff disposed of it as an owner-review pass instead of paying it, so nothing went undetected. No new detector is owed.
- `tests / fast`, tests/entities.py, 2 of 2425: "gate-sweep.yml: on CI's completion ... (U0c)" and "graders-head-copy's delivery_status step is red only when ...". Both fail identically at the merge base c176ee55d in this environment (`PYTHONPATH=tests/hastub python3 tests/entities.py` in its worktree), so they are not this diff's and no root cause is owed here.
- `tests / mutation`: red until `mutation-autofix` pins the 6 sites under Unpinned sites. The predictor printed every site before the push, and each was driven and killed.
- `tests / ci-ratchet`: if red, it is main's own push red (the repo-wide artifacts listing), not this diff's. This PR does not touch tests/ci_ratchet.py.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` at the head lists 6 sites. Each was driven by `tests/mutation_table.py`'s own operator mutant (`candidates()`), with `dev/audit/harnesses/r10_sav_comfort_opmutants.py <copy> full <key>` on a `git ls-files` copy of the head, beside an unmutated null: rc=1, failing=1, the `#363 recorded_at` check every copy without `.git` fails. Kill rule: `mutation_table.killed()`, a run naming more failing checks than the null. All 6 are killed, so each is pinned by `mutation-autofix`:
- `custom_components/heatpump_optimizer/optimizer.py:324 RETURN_DEL` (`_baseline_target`'s return): failing=3, D1-s2-51, D1-s4-02 (control) and D1-s2-04, all `solve_failed` (the solve raises). Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/optimizer.py:333 GUARD_OFF` (`if comfort_targets is not None:`): failing=7, among them `a night setback lowers the reference, not the reported savings` and `past the comfort schedule's end the thermostat holds the default setpoint ...`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/optimizer.py:336 RETURN_DEL` (`return targets.tolist()`): failing=3, the same three `solve_failed` checks as :324. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/optimizer.py:5294 BOOLOP` (`two_tank or ...`): failing=2; the killing check is `the savings reference backs off by the wood share on the two-tank layout, and a wood reading on any other layout moves it not at all`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/optimizer.py:5294 GUARD_OFF`: failing=2, the same check. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/optimizer.py:5335 CLAMP_DROP` (`power = (required_thermal / cop)`): failing=2; the killing check is `a demand past the pump's nameplate holds the reference at max_electrical_power`, which reads 1.469 kW against a 1.0 kW pump. Pinned by mutation-autofix.

## Forward-carry

- Carry 5, seam 2: actuate the supply switch at step boundaries from a one-minute tick, rather than at the cycle phase. Its owed controls are a synthetic install with the cycle phase at 0 and at 14 min that books identical duty verdicts, and one mutant per seam. It moves the actuator edge (`coordinator._apply_action`, `early_cutoff`, `pump_arbiter.switch_supply`) and needs a design note first. Main's roster, `dev/programme/rosters/wave-r10-groups.json`, now holds the group for it, R10-SAV-ACTUATION (after R10-SAV-COMFORT, issues [2492]), whose `carry` already records both controls. Carry: R10-SAV-ACTUATION

## Friction

- dispatch-return-ref: contradiction: PROMPT.md's Output line names `handoff/r10-sav-comfort-r2` and `body_push.sh r10-sav-comfort-r2`, and its brief's closing line names `handoff/r10-sav-comfort`. The Output line, which the pool prompt's return signal (`handoff/<topic>`) agrees with, was followed. Carry: dismissed: the seat followed the two sources that agree, and the orchestrator renders both lines, so it reads the r2 refs it named
