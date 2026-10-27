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

**The roster carries, item by item.**
- Carry 1 (R10-SAV-BASELINE's three terms). Comfort is separated by the matched reference, stored heat by `_settle_horizon` and `_start_gap_cost`, and the timing term survives. The `const` arm reads +0.35 % against timing −0.00 %, the `vary` arm +16.04 % against timing +15.31 % (Null control). The second limit, re-measured at the merge base 28800999b: the committed fixtures read `summer_dhw_only` savings_percentage −3.173852 and `away_setback` 34.044318, identically at the base and at the head. This branch claims neither, and `env_drift.py --all` reads no unclaimed drift (Figures).
- Carry 2 (volume against timing). The modelled thermostat is scaled by `meter_calibration`, so the flat-price null reads 0.00 and the varying profile keeps its timing term +74.88. The meter-reads-the-model install keeps 48.0 at calibration 1.0 (Null control). Mutants M17 to M22.
- Carry 3 (card equal to the ledger). `ledger.savings_months` puts every cell on one basis, and tests/card.mjs renders the Savings page from the sensor payload and asserts each cell against it (M24).
- Carry 4 (the owner's specification). The baseline is the thermostat at the meter's power levels over the same price profile, and timing is 0 under one flat price (Carry 2's arms).
- Carry 5 (the duty ledger). Seam 1 is done here: `planned` re-freezes at each plan adoption (M23). Seam 2 is routed under Forward-carry.

**The claim file keeps main's claims.** `tests/golden/claimed_drift.txt` adds this branch's own R10-SAV-COMFORT claims, and suspends the may-drift entry of each fixture it claims, since a fixture cannot be both. Main's claims stand verbatim: the five R10-LEARNER-ETA coord_* lines and the R10 thermal-power-option `config_flow` line.

**The six operator sites this diff adds are pinned in the tree.** `mutation-autofix` recorded one `killed_by` row per site in 772d1b938 (`ci: pin killed mutants`); an earlier pass's own pin drive found the same six killed and kept the bot's rows (Unpinned sites).

## Head

`7c422999ff40d2c22fd03d123060079ca1225780` merges origin/main `28800999b9ce23793f191101bdfc1e4f598168fc` into this PR's previous head `8d0572dc33d74026d204367409adf47a084f37e7`. It is a merge-only change since the verdict: no code moved. Files resolved: tests/golden/claimed_drift.txt, by hand (both sides rewrote the claim list; this branch's list kept, with main's `config_flow` claim added byte-identical to main's line). tests/closures.json and tests/structure_budgets.json were auto-merged by the ledger driver (`class_excess_loc` 18083, both deltas applied). The branch's one coordinator.py hunk, `monthly_held_cost_delta` reading `held_cost`, is unchanged: `git diff origin/main...HEAD -- custom_components/heatpump_optimizer/coordinator.py` (three-dot) is that one line, as `git diff 5261ba841 8d0572dc3` was. Every figure below was re-taken in this pass at 7c422999f or against its merge base 28800999b, with origin/main's tip at `df478d40be4b546a7aaad150a5d9132483534a3a` (2026-10-26, 05:36Z to 08:30Z, `date -u`). This pass changes no code: the `tests / replay` red it was sent for is not this branch's (Red checks).

`8d0572dc33d74026d204367409adf47a084f37e7` merges main `5261ba841` into the previous head: an automatic merge by the orchestrator, no resolution.

`7ae5e30e0df57b522d527945d398ccc547e0389b` merges origin/main `0825aee641c8` into this PR's previous head `1b6df0e492decf43f14575faaa991408eb81501d`; the only conflict was tests/golden/claimed_drift.txt, resolved by hand: main's R10-LEARNER-ETA coord_* claims kept in place of the superseded R10-SCORES lines, this PR's own claims kept (the R10-SAV-COMFORT lines); no code changed.

Earlier heads (`1b6df0e49`, `a0d9ccc93`, `6160395ef`) are automatic main merges by the orchestrator; the reviewed code is c91cc71fe1618747f30b48c7567a8bbc17d9e74e.

## Mutation proof

`python3 dev/audit/harnesses/r10_sav_comfort_mutants.py <copy>`, run on a `git ls-files` copy of 7c422999f. M0 (unmutated): rc=0, failing=0. Every mutant fails at least one check:
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

Each mutant is named in the harness's `M` list. The production-call payment (the hoist) is proven by its own channel: tests/stress.py at the head judges 20 of 20 family members against 28800999b and none is over (Figures).

## Null control

Each harness was run from the head's file, once in a worktree of the merge base 28800999b and once at the head:
- `r10_sav_volume.py flat`. Base: saving −64.51, volume −64.51, timing +0.00 (DEFECT, 0.2154 per metered kWh at one price). Head: 0.00, volume +0.00, timing +0.00, `meter_calibration` 1.56 (SOUND).
- `r10_sav_volume.py vary`. Base: 10.37 = volume −64.51 + timing +74.88. Head: 74.88, volume +0.00, timing +74.88.
- `r10_sav_volume.py gap`, a meter that reads the model. Base and head both save 48.0. Head `meter_calibration`: 1.0.
- `r10_sav_comfort.py const`. Base: +4.95 % saved against timing +0.00 % (DEFECT). Head: +0.35 % against −0.00 % (SOUND).
- `r10_sav_comfort.py vary`. Base: +20.03 % against timing +15.30 % (DEFECT). Head: +16.04 % against +15.31 % (SOUND).
- `r10_sav_baseline.py null`. Base: booked thermostat 128.4 kWh against 121.5 steady at the delivered room (DEFECT). Head: 121.8 against 121.5 (SOUND).
- `r10_sav_baseline.py transient`. Base: step 0 is 1.81e-01 kW off its steady holding power (DEFECT). Head: 8.88e-16 kW off (SOUND).
- `r10_sav_baseline.py cost`, the #2411 arm that asserts the row's Actual equals the closed-month receipt's bill total. Base: 15.0 against 15.0 (SOUND). Head: receipt 15.0 against row 4.2 (DEFECT). This reversal is the one carry 3 requires. The owner's acceptance moves the row's Baseline, Actual and Savings onto one spot-plus-fee basis, so the row no longer carries the bill's capacity, wear and immersion lines that the receipt totals. `coverage` reads SOUND at both ends.
- The mutation proof's null is M0 above. Each pin's null is its drive's: the comment-only mutant `optimizer.py NULL_COMMENT` survived (Unpinned sites).

## Figures

- Harnesses, both ends: `PYTHONPATH=tests/hastub:tests:custom_components python3 <harness> <arm>`, from a worktree of 28800999b and from the head. sha1 of each file, unchanged since the verdict:
  - `dev/audit/harnesses/r10_sav_volume.py`: be62082cc746a336a5580742b3047b2acc8f17df
  - `dev/audit/harnesses/r10_sav_comfort.py`: 6615a321e3169db377b9c661f689ade65c31f78e
  - `dev/audit/harnesses/r10_sav_baseline.py`: 88ac23e4b83a349789b5c6674e0cbee6021e736f
  - `dev/audit/harnesses/r10_sav_comfort_mutants.py`: 4ea9f082d160c3a8a1aee430ef96b98eb8ba5f76
  - `dev/audit/harnesses/r10_sav_comfort_opmutants.py`: 76ea211845c8608ba6ab25d7fecb0109bc67f386
- Scope: `python3 tests/closure.py select --diff 28800999b9ce23793f191101bdfc1e4f598168fc --workdir <scratch dir>` (the workdir takes its scope files, so it must not be the checkout) prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- Scoped gate (06:18Z to 07:04Z): `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=28800999b9ce23793f191101bdfc1e4f598168fc PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tests/run.sh` at the head. Every script was ok except tests/entities.py, 2 of 2448, both under Red checks. The same two fail at 28800999b in this container (`2 of 2448 ENTITY CHECKS FAILED`, re-run in this pass).
- Goldens: in that run `tests/env_drift.py --all 28800999b...` printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`, and `--claims-only` was ok.
- Carry 1's second limit: `predicted_savings` and `savings_percentage` read from `tests/golden/summer_dhw_only.json` and `tests/golden/away_setback.json` in both worktrees: −0.020559 / −3.173852 and 17.075189 / 34.044318 at both ends.
- Claim diff: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt | grep '^-[^-]' | grep -vc '^-# may-drift:'` prints 0: every removed line is a suspended may-drift entry, each restated under its suspension note, and main's claim lines stay. `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/card_claimed_drift.txt | wc -l` prints 0.
- Production calls, the class census (`fixer.md` step 8): tests/stress.py in that run printed `production calls: 20 of 20 family members judged against 28800999b9ce... ; re-planned: []; new on this branch: []` and `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan`. Rule: `calls_over_verdict`; the channel enumerates one member of every sweep family (`calls_population`).
- Card equality (owner acceptance): `python3 tests/plan_view.py`, `node tests/card.mjs` and `node tests/card_drift.mjs 28800999b...`, all ok in the scoped gate.
- Mutation table: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main` at the head. It prints `3935 unpinned site(s) of 6380 candidate sites, 3938 at the ratchet base 28800999b9ce23793f191101bdfc1e4f598168fc; the ledger agrees with the deterministic inventory`, and no `ADDED UNPINNED` line (`grep -c` prints 0). This pass stopped its seven-mutant drive at the container's two-hour job limit, after features.py's baseline (rc=0, failed=0) and the null `ledger.py:34 NULL_COMMENT`, which survived every driver. So the inventory line is the figure cited here, and no verdict line is cited. The six sites are pinned in the ledger (Unpinned sites).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at the head; `class_excess_loc` is the ledger driver's merge of both sides' deltas. The branch's own re-record (18209 to 18206) carries its reason in 8f5fd0295's commit message.
- `python3 tests/closure.py canonical` leaves tests/closures.json byte-identical (`git diff --quiet`).
- `node tools/policy/policy_lint.mjs --budgets` exits 0.
- Architecture: `python3 tools/audit/archscore/score.py --diff 28800999b9ce23793f191101bdfc1e4f598168fc HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 28800999b9ce`.
- Carry routing: `python3 -I tools/audit/carry_audit.py pr 2745` prints `CARRY-AUDIT #2745: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`.

## Red checks

Every red that stands on a commit this branch pushed, one entry per check name, read from the check-runs API on 2026-10-26 against origin/main `df478d40be4b546a7aaad150a5d9132483534a3a`. Whose each is was checked three-dot (`git merge-base origin/main HEAD` = 28800999b) and against main's own runs.

- `tests / replay`: red once, check run 121226462191 (run 40210190693, pull_request, head 8174249e1), step "Replay recorded days through the real coordinator": `FAIL synthetic-dhw-only.json: cycle_cost [2 offender(s): cpu_ratio 2.216 over its budget 2.173 | loop_cpu_ratio 0.1441 over its budget 0.143]`, `1 of 93 replay checks FAILED`. That runner's reference solve read `ref_ms` 24.1 and `loop_ref_ms` 82.3, the fastest runner class. The current PR head 8d0572dc3 is green on the same lane, check run 121331738480 (cpu_ratio 1.7725, loop_cpu_ratio 0.0901, `ALL 93 replay checks PASSED`), and 8d0572dc3 differs from 8174249e1 only by a main merge. The conflict-resolution head 7c422999f has not run in CI yet. Locally, `PYTHONPATH=tests/hastub python3 tests/replay.py` fails `cycle_cost` on loop_cpu_ratio alone in this container at every SHA tried, origin/main's tip included: 8174249e1 0.1553, 8d0572dc3 0.1499, 7c422999f 0.1517, origin/main df478d40b 0.1445, each against 0.143. So this container sits outside the band the budget was recorded on and cannot decide the question. Interleaved in this container, 16 pairs of `--fixture tests/replay/synthetic-dhw-only.json` at the merge base 28800999b and at 7c422999f: cpu_ratio median 1.9486 base, 2.0287 head, and the paired head/base ratio has median 1.023 with head above base in 10 of 16. loop_cpu_ratio median 0.1408 base, 0.1429 head, paired ratio median 1.019, head above in 10 of 16. A 10-of-16 sign split is not distinguishable from noise (two-sided sign test p about 0.45), and the spread inside each arm (cpu 1.61 to 2.21 base) is about ten times the shift. Across the 33 concluded PR replay runs from 2026-10-23 to 2026-10-26, 32 passed. The one red is 121226462191, 2.0 % and 0.8 % over its two caps. Three of those runs were on the same fast runner class (`loop_ref_ms` under 95): e088bf833 (#2819) at 1.8847 and 0.1105, this branch's own 7ae5e30e0 at 1.7671 and 0.1083, and 4fbe4c6a5 at 1.8417 and 0.1283. So it is not this branch's code: the same reviewed tree passed on that runner class and at the current head, and no code change is made here. Main never runs this lane on push (`replay` is gated to `pull_request` in tests.yml), so there is no main run id to cite. Cheaper detector: none exists. The lane is itself the timed detector. A local run cannot reproduce the CI runner's band, as shown above, where main itself reads red. Widening the budget to stop a 2 % single-run edge is a ratchet raise this PR may not make. Cost test: P(recurrence) is 1 in 33 measured runs. Cost per occurrence is one re-run of a 48 to 62 s lane. Any standing countermeasure, such as running the timed fixture twice, costs at least that same minute on every one of the 33 runs, which is more than it saves. The budget's own comment in tests/replay.py already prescribes re-centring at the next timed week, not on one run.
- `tests / fast (3.14)`: red at 46dc1dda8 (check runs 120942142230 and 120941471531) and at c70c3e464 (120926746399), each `FAILED python3 tests/stress.py`. It is this branch's. stress.py's production-call verdict fired on the matched reference's second thermostat pass (winter/1z/space/pin-off over its 1.05x allowance). It was paid in code by the hoist 8f5fd0295. The current head 8d0572dc3 is green, check run 121331738404, and main is green on it at 28800999b (121369075278) and df478d40b (121402477070). Cheaper detector: the scoped gate's tests/stress.py, run locally. It existed and fired locally first, so its standing cost is already paid and no new detector is owed.
- `tests / mutation`: red at acd865b03 (120921728932), c70c3e464 (120926210442) and 36c985d33 (121028737618), each `ADDED UNPINNED` for sites this diff adds: ledger.py `MIN_CALIBRATION_KWH`, `meter_calibration`, `add_savings_settlement` and optimizer.py `if not shortfall > 0.0` at the first two; the six `_baseline_target(s)` and `_compute_baseline_power` sites at the third. It is this branch's. `mutation-autofix` pinned the first set in 46dc1dda8 and the second in 772d1b938. The current head 8d0572dc3 is green, check run 121326817940. Main is green at 28800999b (121369075017) and df478d40b (121402476255). Cheaper detector: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main`, which already exists, and the autofix job repairs it without a seat (`ci-autofix.md`), so no new detector is owed.
- `governance / delivery-status`: red at 8d0572dc3, check run 121326817924. It reads `DELIVERY STATUS OVERDUE — 146 rowed, 12 pending, 14 overdue (overdue at 12 commits)`, and every overdue row is another pull request's (#2773, #2812, #2813, #2712, #2807, #2804, #2798, #2799, #2780, #2749, #2775, #2797, #2762, #2795). None is #2745. It is programme-wide, not this branch's. The same check was red in the same hour on #2834 (121326741923, e2a808a64) and #2819 (121324659605, 6f91e6d05). It is not a required context: the only required status check in rulesets `main-protect` and `main-protect-checks` is `gate`, and the job prints "This check is NOT a required context and a red here blocks no merge". Cheaper detector: none is owed by this PR. The red is the record backlog draining, which the check exists to show.
- tests/entities.py, 2 of 2448, in this container only: "gate-sweep.yml: on CI's completion ... (U0c)" and "graders-head-copy's delivery_status step is red only when ...". The same two fail in a worktree of 28800999b, so they are not this diff's.
- `tests / ci-ratchet`: red on main's own push at 28800999b (121377149428), where GitHub's repo-wide artifacts listing returned 0 bytes. It is green again at df478d40b (121411469364). This PR does not touch tests/ci_ratchet.py.

## Unpinned sites

All six sites this diff adds are pinned by `mutation-autofix` (772d1b938), each row recorded against 5c0ee1093. An earlier pass's independent drive, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` at af8857403 (base 9d0ddf8af), printed `PIN KILLED: 6 pinned, 0 left unpinned`; its null `optimizer.py NULL_COMMENT` survived tests/features.py, with baseline rc=0 failed=0. The bot's rows were kept. Each site, the bot's row, and both readings:
- `optimizer.py:324 RETURN_DEL` (`_baseline_target`'s return), `_baseline_target.RETURN_DEL.26d08f36`: bot, tests/plan_view.py failed=1; seat, tests/features.py failed=4. Pinned by mutation-autofix.
- `optimizer.py:333 GUARD_OFF` (`if comfort_targets is not None:`), `_baseline_targets.GUARD_OFF.7df02561`: bot and seat, tests/features.py failed=7. Pinned by mutation-autofix.
- `optimizer.py:336 RETURN_DEL` (`return targets.tolist()`), `_baseline_targets.RETURN_DEL.e3ab3cc7`: bot, tests/plan_view.py failed=1; seat, tests/features.py failed=4. Pinned by mutation-autofix.
- `optimizer.py:5294 BOOLOP` (`if two_tank and state.wood_tank_temperature is not None:`), `HeatPumpOptimizer._compute_baseline_power.BOOLOP.03ee6373`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.
- `optimizer.py:5294 GUARD_OFF`, `HeatPumpOptimizer._compute_baseline_power.GUARD_OFF.03ee6373`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.
- `optimizer.py:5335 CLAMP_DROP` (`power = min(required_thermal / cop, p.max_electrical_power)`), `HeatPumpOptimizer._compute_baseline_power.CLAMP_DROP.2bd515d1`: bot and seat, tests/features.py failed=2. Pinned by mutation-autofix.

## Forward-carry

- Carry 5, seam 2: actuate the supply switch at step boundaries from a one-minute tick, rather than at the cycle phase. Its owed controls are a synthetic install with the cycle phase at 0 and at 14 min that books identical duty verdicts, and one mutant per seam. It moves the actuator edge (`coordinator._apply_action`, `early_cutoff`, `pump_arbiter.switch_supply`) and needs a design note first. Main's roster, `dev/programme/rosters/wave-r10-groups.json`, holds the group for it, R10-SAV-ACTUATION (after R10-SAV-COMFORT, issues [2492]), whose `carry` already records both controls. Carry: R10-SAV-ACTUATION
- Review 6387209379's seam census (the Evidence bullet naming card line 8587): a census result, not a defect. Its own words are "No seam is open", and the one reader it names, card line 8587, reads the plan-horizon prediction, divergence (a). Carry: dismissed: census result with no seam open; card line 8587 is divergence (a), already out of scope by carry 3, per the census evidence review 6387209379 cites (item e4b56a35)

## Friction

- dispatch-stale-red: stale: the brief's `tests / mutation` red was repaired by `mutation-autofix` (772d1b938, merged into the PR's head as a39fe9827) while this seat drove the same six pins, which the merge then discarded; about an hour of pin drive and re-take. Carry: dismissed: the orchestrator's brief was snapshotted before the bot commit, and the dispatch carries no re-check step
- local-pin-drive-entities: cost: tests/entities.py's two-check red at the merge base in this container makes `--pin-killed` and `mutation_table.py --base` read INCONCLUSIVE; the drive was re-run with `--scripts tests/features.py`, about 8 extra minutes. Carry: dismissed: environment-only, CI's entities.py baseline is green
