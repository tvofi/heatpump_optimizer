R10-SAV-COMFORT part 3: the month row settles the plan's stored heat and publishes the comfort shortfall beside the saving (carries 0 and 6, under the owner's ruling on carry 7).

Part of #2492. Part of #201. Critical path: R10-SAV-COMFORT. #2492 stays open: the summer start-bound limit (carry 0's second limit) and carry 5 are routed back to it.

**The ruling applied.** tvofi's mandated orchestrator ruling of 2026-11-04 on carry 7: the month row settles stored heat, the thermostat stays start-independent, and the comfort-matched null is reported beside the saving. Each plan step now carries four settlement readings, `ledger.SETTLEMENT_KEYS` (`baseline_kw`, `stored_kw_th`, `comfort_kw`, `steady_cop`), from `optimizer._settlement_schedule` through `get_current_action` (`_settlement_at`) into the coordinator's pending snapshot, which `MonthlyLedger.observe_spot_and_settle_savings` books:

- `stored_kw_th`: the house store's change over the step (`_stored_thermal_energy` at the plan's boundary states), booked as kWh_th on `savings_stored`. `savings_months` converts the month's total once, at the month's mean steady COP (`steady_cop` meta), and prices it once, at the row's metered kWh price, then settles it into `baseline_sek` (`stored_heat_sek`). Heat drawn from the house was not bought; heat left in it was.
- `comfort_kw`: the steady thermostat (`_floor_demand_at_target`) at the step's comfort target less at the room the plan delivered (the slab-fed zone, at the step's midpoint), at the step's steady COP, priced per interval as the baseline is. Published as `comfort_sek` beside `savings_sek`, and not netted out of it. `savings_sek - comfort_sek` is the comfort-matched saving.

The thermostat's booked step (`baseline_kw`) does not change, so start-independence holds: `r10_sav_baseline.py transient` spread stays 0.00 kW.

**Three shapes tried; why each of the first two lost.** The figures come from `dev/audit/harnesses/r10_sav_null_settled.py` (new, below):
1. Stored heat at the settlement caps, converted at each step's COP: `const` arm comfort-matched +0.28 %, but the varying arm read −4.50 %. Each plan's caps follow its own mean outdoor, so a cap that moves between re-plans breaks the telescope: a slab charged above one plan's cap and drawn under the next one's books only the draw.
2. Uncapped, at each step's COP: the varying arm read +0.01 %. The COP-timing saving was cancelled, because heat stored at a warm hour's COP and drawn at a cold hour's books the gain back as a draw.
3. Uncapped, converted at one COP and priced at one price per row (this head): `const` +0.28 %, varying +14.28 %. One conversion for the whole row lets passive heat telescope out the same way the stores do.

Per-interval pricing of the store was not tried, because it cancels the price-timing saving the same way (pinned: `a store charged cheap at COP 4 and drawn dear at COP 2 settles at one COP and one price`).

**Payments (no budget raised).** The diff first breached `class_excess_loc` (+122), `max_class_loc` (+4) and `methods_over_150` (+1, `_record_accuracy` at 154 lines). Each was paid in the code:
- The schedule computation is a module-level pure function of the model and horizon (`_settlement_schedule`). `class_excess_loc` prices class spans only, so this is the module-level function the rule enumerates.
- `ledger.settle_interval_savings`, whose only caller was `observe_spot_and_settle_savings`, is folded into that caller. `MonthlyLedger` is at 296 lines against the 300 limit.
- The pending snapshot copies `SETTLEMENT_KEYS` in one spread that replaces the `baseline_kw` line, so `_record_accuracy` stays at 150 lines and the coordinator class span is flat.
- `_settlement_at` replaces `get_current_action`'s separate baseline branch.

A `bisect_right` step search was tried as a further payment and reverted, because the R10 N-no-expiry barrier in `tests/entities.py` counts it as a covering lookup and changing that lookup's expiry is out of scope. `tests/structure_budgets.json` is byte-identical to main's.

**The carries.**
- Carry 0 (the month row's comfort-matched null, and the summer start-bound limit): the first limit is met at this head. `const` comfort-matched +0.28 % with stored heat settled; the varying arm keeps the timing term (+14.28 %, not 0). The second limit, `summer_dhw_only`'s predicted savings, is `optimizer._start_gap_cost`'s and lies outside this diff. At the merge base and at the head it reads `savings_percentage` −3.173852 in `tests/golden/summer_dhw_only.json`, and `tests/golden.py` (drift mode) passes at the head, so this diff moves no fixture. The −12.74 % the carry quotes was taken at R10-SAV-BASELINE's branch head and is not on main. Carry: #2492
- Carry 3 (the owner's baseline specification): the flat-price arm stays timing 0 and the card stays equal to `ledger.savings_months` cell for cell. `tests/card.mjs` passes; it renders from `tests/plan_view.py`'s sensor payload and asserts `baseline − actual = savings` per row, which is why the store settles into `baseline_sek` and not beside it. `r10_sav_volume.py` flat +0.00 / +0.00, vary timing +74.88. The meter-calibrated thermostat basis landed in #2745 (`34cd75bf1`). This diff scales both new terms by `meter_calibration`, as it scales the thermostat.
- Carry 5 (`power_ratio` against the planner's over-booking on one sample window): not measured here, because it needs a sample window the tree does not hold and it sits outside the savings seam this diff changes. Carry: #2492
- Carry 6 (the flat-price null books the comfort shortfall as a saving): answered by the ruling. The shortfall is now published beside the saving (`comfort_sek`), and the comfort-matched `const` null reads +0.28 % (bar 3.0).
- Carry 7: implemented by #3145 (`eb0cf1893`). It is cited here only for the ruling, and this diff does not touch `pump_arbiter.py`.

## Head

`b1a1213687f345207cd514905db1aa28e0112a9a`: a merge of origin/main `616868bdc5ca54d9555cfc89715f05a33527661e` into `e834ac7dcbcab873d345a0455e09c7798f358a70`. `e834ac7dc` is itself a merge of origin/main `a9c2f90fc77be2e7a870f3f2735dcd0f79b5f475` (mutation-ledger pins only) into code head `bfb9c132416371dcf71b6c775e8ebcc01c97e3b1`. Both merges were conflict-free; the ledger merge driver resolved `tests/closures.json`. The branch was cut at `c3a279e3252a8b57bb00b5a677318cd4fe20387f`. Its commits are the failing test (`9c33612db`), the fix (`6358a2286`), the harness classification with the stale pin dropped (`d77a7f112`), the one-reader and revert commit (`bfb9c1324`), and the two merges. `364e08bfb` recorded a `class_excess_loc` gain that `bfb9c1324` returns to main's recording.

The suite runs, harness figures and proofs below were taken at `bfb9c1324`. The two merged deltas touch nothing under `custom_components/`, `tests/features.py` or `dev/audit/harnesses/r10_sav_*`:
- `git diff --stat c3a279e32 a9c2f90fc` is 55 pin files under `tests/mutation_ledger/killed_by/`.
- `git diff --stat a9c2f90fc 616868bdc` is `tests/ci_ratchet.py`, `tests/arch_score.py`, `tools/audit/archscore/`, `tests/closures.json` and two delivery rows.

At this head, `tests/harness_headers.py`, `tests/structure.py`, `tests/arch_score_head.py` and `tests/entities.py` were re-run with `PYTHONPATH=tests/hastub`, all rc=0, and `prepr.sh` ran here. origin/main was `616868bdc` at 2026-11-04T10:47:42Z.

## Mutation proof

Mutant: the settlement removed from the row in a detached worktree at `bfb9c1324`. In `MonthlyLedger.savings_months`, `baseline_sek = self.line(key, "savings_baseline")["sek"] * scale + stored_sek` becomes `... * scale`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` prints `1 of 4783 FEATURE CHECKS FAILED`, rc=1. The one FAIL is `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price`.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py const` prints `const: comfort-matched saving 11.54 (+7.70 % of the settled baseline)`, `const: DEFECT`, rc=1. That matches #3145's +7.44 % residual on the same arm.

Restored, the head prints `ALL 4783 FEATURE CHECKS PASSED`, rc=0.

Failing test first: the head's `tests/features.py` against the merge base's `custom_components/` (a detached worktree at `c3a279e32`) stops with `TypeError: MonthlyLedger.add_savings_settlement() got an unexpected keyword argument 'stored_kw_th'`, rc=1. The base ledger takes no stored-heat reading.

## Null control

- The same closed loop booked without the new readings (`baseline_kw` alone, the pre-ruling row), inside `r10_sav_null_settled.py`: varying arm 12.34 %, `const` arm 11.86 %. These are the defect the settled row removes.
- `dev/audit/harnesses/r10_sav_baseline.py` (sha1 `bc31f356191ededbfb0b15f768b258249867b134`), identical at both ends: transient SOUND, spread 0.00 kW at four starts; coverage SOUND; cost DEFECT (the one-basis row, as #2745 recorded); null DEFECT, 12.336145360155744 %. Its null arm books `baseline_kw` alone, so it still measures the pre-ruling row by construction. The ruling's figure is the new harness's.
- `dev/audit/harnesses/r10_sav_volume.py` (sha1 `be62082cc746a336a5580742b3047b2acc8f17df`): flat volume +0.00 and timing +0.00 (SOUND), vary timing +74.88 (SOUND). Its rows carry `stored_heat_sek 0.0`, `comfort_sek 0.0`, because it books no plan readings: the row without readings is unchanged.
- `tests/features.py`: `R10-SAV-COMFORT null control: an interval without either reading settles nothing`. A row booked without the readings equals the base's row, plus the two zero cells.
- `dev/audit/harnesses/r10_sav_actuation_phase.py` (sha1 `d8871c1b96466f7d0d16df9ecc15454512d6adc5`): `AGREE: yes`.

## Figures

- The ruling's acceptance: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py` (sha1 `eca29a18ee192f0d3727e447e1f981326fe5b9c0`) at `bfb9c1324`, rc=0.
  - vary: settled row baseline 167.25, actual 135.09, saved 32.16 (19.23 %), `stored_heat_sek` 13.15, `comfort_sek` 8.28; comfort-matched 23.88 (+14.28 %), SOUND.
  - const: baseline 138.73, actual 132.11, saved 6.62 (4.77 %), `stored_heat_sek` −11.15, `comfort_sek` 6.23; comfort-matched 0.39 (+0.28 %), SOUND.
  - The verdict rule: `const` `|pct| < 3.0`, vary `pct >= 3.0`. The rejected shapes' figures (−4.50 %, +0.01 %) were taken with the same harness on the intermediate trees described above.
- Carry terms: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_terms.py`, and the same with `const` (sha1 `c981e7c840ede1a5fef95aa903e00e5809c92aa7`), at the head and the base, identical. Varying arm: comfort gap 6.9 kWh, timing +17.29 %, stored heat drawn −20.1 kWh_th (the house gained heat, so the settled row credits the plan, `stored_heat_sek` +13.15). `const`: comfort gap 5.2, timing +0.00 %, drawdown 9.3 kWh_e.
- Finder's null: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline.py` at the head, null 12.336145360155744 % (Null control).
- Summer limit: `tests/golden/summer_dhw_only.json` `savings_percentage` −3.173852 at the head and the base. `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` exits 0 at the head.
- Class seams: `git grep -n "observe_spot_and_settle_savings\|add_savings_settlement" -- custom_components` returns the coordinator's `_accumulate_energy` (the one production booking site, which takes the pending snapshot this diff extends) and the ledger's own definitions. `git grep -n '"baseline_kw"' -- custom_components` returns `optimizer._settlement_schedule` and `_settlement_at` (the action's one source) and `ledger.SETTLEMENT_KEYS`; `git grep -n SETTLEMENT_KEYS -- custom_components` returns the coordinator's pending snapshot and the ledger's booking, the two readers. Every reader of the step's settlement readings goes through `SETTLEMENT_KEYS`.
- Gate scope: `python3 tests/closure.py select --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f --workdir <dir>` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. Every script it names ran at `bfb9c1324` with `PYTHONPATH=tests/hastub` (golden with `GOLDEN_MODE=drift`), rc=0, except `tests/stress.py`, which is left to CI.
- Feature suite: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4783 FEATURE CHECKS PASSED`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` against main's budgets, byte-identical.
- Typing: `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py`, rc=0 (0 errors, as recorded).
- Pre-PR: `bash tools/pr/prepr.sh <body>` at the head, rc=0.

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main --pin-killed` was run at this head and stopped at its 7000 s bound after the driver baselines and the null control (`ledger.py:40 NULL_COMMENT` survived every driver), with no mutant driven, rc=124. No site below is claimed killed. Every site is under `custom_components/`, the lane `mutation-autofix` mutates, so each one's disposition is `mutation-autofix`: pinned by it when killed. A survivor it reports goes to triage under `tests/mutation_ledger/survivor_triage/` and is not settled here (`ci-autofix.md`).

- `custom_components/heatpump_optimizer/ledger.py:261 BOOLOP` (`fee_per_kwh = float(fee) if isinstance(fee, (int, float)) an`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:307 GUARD_OFF` (`if stored_kw_th is not None and steady_cop is not None and n`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:309 CLAMP_DROP` (`self.observe_meta_mean(when, STEADY_COP_META, max(float(stea`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:310 GUARD_OFF` (`if comfort_kw is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:426 CMP_BOUND` (`stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else s`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:421 BOOLOP` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:421 CMP_BOUND` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:430 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:433 GUARD_OFF` (`if buffer is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:435 RETURN_DEL` (`return opt._stored_thermal_energy(state)`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:442 CLAMP_DROP` (`cop = max(model.compute_cop(float(h.outdoor_temps[i]), humid`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:452 CLAMP_DROP` (`max(0.0, _floor_demand_at_target(model, targets[i], *weather`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:453 CLAMP_DROP` (`- max(0.0, _floor_demand_at_target(model, delivered, *weathe`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:457 CMP_BOUND` (`if i < len(baseline):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:457 GUARD_OFF` (`if i < len(baseline):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:461 RETURN_DEL` (`return schedule`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:470 CMP_BOUND` (`if i < len(result.settlement_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:470 GUARD_OFF` (`if i < len(result.settlement_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:472 CMP_BOUND` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:472 GUARD_OFF` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:474 RETURN_DEL` (`return {}`): mutation-autofix

## Red checks

- `mutation`: red at the `handoff-wip/r10-sav-comfort-p3` step push `e834ac7dc`, as `prepr.sh`'s pr-body step reports from that commit's check runs. This seat cannot read check-run output (no check-runs API), so the cause below is the tree's prediction and was not read from the run. `tools/pr/ci_predict.py` (`prepr.sh` step 6d) lists the 21 unpinned sites the diff adds, each disposed of under `## Unpinned sites`, and predicts no other red. That is the cheaper detector, and it ran before the push: its standing cost is one `ci_predict.py` pass per `prepr.sh` run. By `ci-autofix.md`, `mutation-autofix` pins the killed ones once the pull request exists. A survivor is triaged, not pinned, and is not settled here.
- The R10 N-no-expiry barrier in `tests/entities.py` and the census in `tests/typing_ruler.py` went red locally during the work, never on a pushed head, and both pass at `bfb9c1324`. Their own detectors caught them: both scripts are in `scope.run`.

## Forward-carry

- The summer start-bound limit: `optimizer._start_gap_cost` caps the start-of-horizon settlement at the thermostat's space-heat cost, which leaves `summer_dhw_only`'s predicted savings negative (−3.17 % at `a9c2f90fc`). The month row's own store settlement is uncapped and telescopes over the row, so this limit stays with `predicted_savings`. Carry: #2492
- Carry 5: reconcile `power_ratio` and the planner's over-booking on one sample window (`dev/audit/harnesses/r10_demand_overbook.py`). Carry: #2492

## Friction

none
