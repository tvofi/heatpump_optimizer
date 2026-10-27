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

**The six operator sites this diff adds are pinned in the tree.** `mutation-autofix` recorded one `killed_by` row per site in 772d1b938 (`ci: pin killed mutants`); this pass's own pin drive found the same six killed and kept the bot's rows (Unpinned sites).

## Head

c91cc71fe1618747f30b48c7567a8bbc17d9e74e, on merge base ab00437c94bd8d8ca7b47b69095c47535f3e645a (`origin/main` when read, 2026-10-25T04:32Z). Its tree is PR #2745's head a39fe9827 (`ci: merge main`, which merged ab00437c9): `git diff --stat origin/fix/r10-sav-comfort HEAD` prints nothing. The pass's commits over 36c985d33: af8857403 merges `origin/main` 9d0ddf8af; ed1826c24 records the six pins from this seat's drive; c91cc71fe merges a39fe9827, whose `mutation-autofix` rows for the same six anchors win the add/add conflict, so ed1826c24's content is gone. Main moved production code between 9d0ddf8af and ab00437c9 (coordinator.py, store.py, thermal_model.py, tests/features.py), so every figure below was re-taken at c91cc71fe or against ab00437c9. Returned on handoff/r10-sav-comfort-r3.

## Mutation proof

`python3 dev/audit/harnesses/r10_sav_comfort_mutants.py <copy>`, run on a `git ls-files` copy of c91cc71fe. M0 (unmutated): rc=0, failing=0. Every mutant fails at least one check:
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

Each mutant is named in the harness's `M` list. The production-call payment (the hoist) is proven by its own channel: tests/stress.py at the head judges 20 of 20 family members against ab00437c9 and none is over (Figures).

## Null control

Each harness was run from the head's file, once in a worktree of the merge base ab00437c9 and once at the head:
- `r10_sav_volume.py flat`. Base: saving −64.51, volume −64.51, timing +0.00 (DEFECT, 0.2154 per metered kWh at one price). Head: 0.00, volume +0.00, timing +0.00, `meter_calibration` 1.56 (SOUND).
- `r10_sav_volume.py vary`. Base: 10.37 = volume −64.51 + timing +74.88. Head: 74.88, volume +0.00, timing +74.88.
- `r10_sav_volume.py gap`, a meter that reads the model. Base and head both save 48.0. Head `meter_calibration`: 1.0.
- `r10_sav_comfort.py const`. Base: +4.95 % saved against timing +0.00 % (DEFECT). Head: +0.35 % against −0.00 % (SOUND).
- `r10_sav_comfort.py vary`. Base: +20.03 % against timing +15.30 % (DEFECT). Head: +16.04 % against +15.31 % (SOUND).
- `r10_sav_baseline.py null`. Base: booked thermostat 128.4 kWh against 121.5 steady at the delivered room (DEFECT). Head: 121.8 against 121.5 (SOUND).
- `r10_sav_baseline.py transient`. Base: step 0 is 1.81e-01 kW off its steady holding power (DEFECT). Head: 8.88e-16 kW off (SOUND).
- The mutation proof's null is M0 above. Each pin's null is its drive's: the comment-only mutant `optimizer.py NULL_COMMENT` survived (Unpinned sites).

## Figures

- Harnesses, both ends: `PYTHONPATH=tests/hastub:tests:custom_components python3 <harness> <arm>`, from a worktree of ab00437c9 and from the head. sha1 of each file:
  - `dev/audit/harnesses/r10_sav_volume.py`: be62082cc746a336a5580742b3047b2acc8f17df
  - `dev/audit/harnesses/r10_sav_comfort.py`: 6615a321e3169db377b9c661f689ade65c31f78e
  - `dev/audit/harnesses/r10_sav_baseline.py`: 88ac23e4b83a349789b5c6674e0cbee6021e736f
  - `dev/audit/harnesses/r10_sav_comfort_mutants.py`: 4ea9f082d160c3a8a1aee430ef96b98eb8ba5f76
  - `dev/audit/harnesses/r10_sav_comfort_opmutants.py`: 76ea211845c8608ba6ab25d7fecb0109bc67f386
- Scope: `python3 tests/closure.py select --diff ab00437c94bd8d8ca7b47b69095c47535f3e645a --workdir <dir>` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=ab00437c94bd8d8ca7b47b69095c47535f3e645a PYTHONPATH=tests/hastub bash tests/run.sh` at the head. Every script was ok except tests/entities.py, 2 of 2440, both under Red checks.
- Goldens: in that run `tests/env_drift.py --all ab00437c9...` and `--claims-only` were both ok, so main's R10-SCORES claims and this branch's own read no stale claim and no unclaimed drift.
- Claim diff: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt | grep '^-[^-]' | grep -vc '^-# may-drift:'` prints 0: every removed line is a suspended may-drift entry, each restated under its suspension note, and main's five R10-SCORES lines stay. `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/card_claimed_drift.txt | wc -l` prints 0.
- Production calls, the class census (`fixer.md` step 8): tests/stress.py in that run printed `production calls: 20 of 20 family members judged against ab00437c94bd... ; re-planned: []; new on this branch: []` and `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan`. Rule: `calls_over_verdict`; the channel enumerates one member of every sweep family (`calls_population`).
- Card equality (owner acceptance): `python3 tests/plan_view.py`, `node tests/card.mjs` and `node tests/card_drift.mjs ab00437c9...`, all ok in the scoped gate.
- Mutation table: `python3 tests/mutation_table.py --base origin/main` at the head prints `3978 unpinned site(s) of 6333 candidate sites, 3981 at the ratchet base ab00437c94bd...; the ledger agrees with the deterministic inventory`, and no `ADDED UNPINNED` line. Its verdict line reads INCONCLUSIVE in this container only because tests/entities.py's baseline is red here (Red checks).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at the head. The `class_excess_loc` re-record (18209 to 18206) carries its reason in 8f5fd0295's commit message.
- `node tools/policy/policy_lint.mjs --budgets` exits 0.
- Architecture: `python3 tools/audit/archscore/score.py --diff ab00437c94bd8d8ca7b47b69095c47535f3e645a HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against ab00437c94bd`.

## Red checks

- `tests / mutation` at 36c985d33: REFUSED, 3993 unpinned sites against 3990 at the ratchet base, 6 added by this diff.
  - Answer: `mutation-autofix` pinned all six in 772d1b938, and `tests / mutation` is green at a39fe9827. This head's table counts 3978 against 3981 at ab00437c9, with no `ADDED UNPINNED` line (Figures).
  - Cheaper detector: `tests/mutation_table.py --base origin/main`, which prepr step 6d and `tools/pr/ci_predict.py` run in minutes before a handoff. It did run before the previous handoff and listed all six. The seat left them to `mutation-autofix` instead of running `--pin-killed` itself, though `ci-autofix.md` says a red that step 6d predicts is repaired before the handoff. The detector exists and its rule was not followed, so no new detector is owed.
- `pr-contract` and `gate` at 36c985d33: the codescan wait race (`codescan_wait.py`: no finished codeql unit after 600 s; gate: "still being judged"), not a defect of this diff. Its fixes are R10-RCA-CODESCAN-WAIT (#2756) and R10-GATE-DEFER (#2770). Both checks are green at a39fe9827.
- `tests / fast (3.14)`: green at a39fe9827. Its earlier red at 46dc1dda8 (tests/stress.py's production-call verdict on winter/1z/space/pin-off, 1.074x over the 1.05x allowance) was paid in code by the hoist (8f5fd0295). The scoped gate's tests/stress.py fired on it locally before CI, so no new detector is owed.
- tests/entities.py, 2 of 2440, in this container only: "gate-sweep.yml: on CI's completion ... (U0c)" and "graders-head-copy's delivery_status step is red only when ...". `PYTHONPATH=tests/hastub python3 tests/entities.py` in a worktree of ab00437c9 prints the same two and `2 of 2440 ENTITY CHECKS FAILED`, so they are not this diff's. CI's `tests / fast (3.14)` is green.
- `tests / ci-ratchet`: if red, it is main's own push red (the repo-wide artifacts listing), not this diff's. This PR does not touch tests/ci_ratchet.py.

## Unpinned sites

All six sites this diff adds are pinned by `mutation-autofix` (772d1b938), each row recorded against 5c0ee1093. This seat's independent drive, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` at af8857403 (base 9d0ddf8af), printed `PIN KILLED: 6 pinned, 0 left unpinned`; its null `optimizer.py NULL_COMMENT` survived tests/features.py, with baseline rc=0 failed=0. The bot's rows were kept. Each site, the bot's row, and both readings:
- `optimizer.py:324 RETURN_DEL` (`_baseline_target`'s return), `_baseline_target.RETURN_DEL.26d08f36`: bot, tests/plan_view.py failed=1; seat, tests/features.py failed=4. Pinned by mutation-autofix.
- `optimizer.py:333 GUARD_OFF` (`if comfort_targets is not None:`), `_baseline_targets.GUARD_OFF.7df02561`: bot and seat, tests/features.py failed=7. Pinned by mutation-autofix.
- `optimizer.py:336 RETURN_DEL` (`return targets.tolist()`), `_baseline_targets.RETURN_DEL.e3ab3cc7`: bot, tests/plan_view.py failed=1; seat, tests/features.py failed=4. Pinned by mutation-autofix.
- `optimizer.py:5294 BOOLOP` (`if two_tank and state.wood_tank_temperature is not None:`), `HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.
- `optimizer.py:5294 GUARD_OFF`, `HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.
- `optimizer.py:5335 CLAMP_DROP` (`power = min(required_thermal / cop, p.max_electrical_power)`), `HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.

## Forward-carry

- Carry 5, seam 2: actuate the supply switch at step boundaries from a one-minute tick, rather than at the cycle phase. Its owed controls are a synthetic install with the cycle phase at 0 and at 14 min that books identical duty verdicts, and one mutant per seam. It moves the actuator edge (`coordinator._apply_action`, `early_cutoff`, `pump_arbiter.switch_supply`) and needs a design note first. Main's roster, `dev/programme/rosters/wave-r10-groups.json`, holds the group for it, R10-SAV-ACTUATION (after R10-SAV-COMFORT, issues [2492]), whose `carry` already records both controls. Carry: R10-SAV-ACTUATION

## Friction

- dispatch-stale-red: stale: the brief's `tests / mutation` red was repaired by `mutation-autofix` (772d1b938, merged into the PR's head as a39fe9827) while this seat drove the same six pins, which the merge then discarded; about an hour of pin drive and re-take. Carry: dismissed: the orchestrator's brief was snapshotted before the bot commit, and the dispatch carries no re-check step
- local-pin-drive-entities: cost: tests/entities.py's two-check red at the merge base in this container makes `--pin-killed` and `mutation_table.py --base` read INCONCLUSIVE; the drive was re-run with `--scripts tests/features.py`, about 8 extra minutes. Carry: dismissed: environment-only, CI's entities.py baseline is green
