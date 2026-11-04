R10-SAV-COMFORT part 3: the month row settles the plan's stored heat and publishes the comfort shortfall beside the saving (carries 0 and 6, under the owner's ruling on carry 7).

Part of #2492. Part of #201. Critical path: R10-SAV-COMFORT. #2492 stays open: the summer start-bound limit (carry 0's second limit) and carry 5 are routed back to it.

**The ruling applied.** tvofi's mandated orchestrator ruling of 2026-11-04 on carry 7: the month row settles stored heat, the thermostat stays start-independent, and the comfort-matched null is reported beside the saving. Each plan step now carries four settlement readings, `ledger.SETTLEMENT_KEYS` (`baseline_kw`, `stored_kw_th`, `comfort_kw`, `steady_cop`), from `optimizer._settlement_schedule` through `get_current_action` (`_settlement_at`) into the coordinator's pending snapshot, which `MonthlyLedger.observe_spot_and_settle_savings` books:

- `stored_kw_th`: the house store's change over the step (`_stored_thermal_energy` at the plan's boundary states), booked as kWh_th on `savings_stored`. `savings_months` converts the month's total once, at the month's mean steady COP (`steady_cop` meta), and prices it once, at the row's metered kWh price, then settles it into `baseline_sek` (`stored_heat_sek`). Heat drawn from the house was not bought; heat left in it was.
- `comfort_kw`: the steady thermostat (`_floor_demand_at_target`) at the step's comfort target less at the room the plan delivered (the slab-fed zone, at the step's midpoint), at the step's steady COP, priced per interval as the baseline is. Published as `comfort_sek` beside `savings_sek`, and not netted out of it. `savings_sek - comfort_sek` is the comfort-matched saving.

The thermostat's booked step (`baseline_kw`) does not change, so start-independence holds: `r10_sav_baseline.py transient` spread stays 0.00 kW.

**Three shapes tried; why each of the first two lost.** The figures come from `dev/audit/harnesses/r10_sav_null_settled.py`:
1. Stored heat at the settlement caps, converted at each step's COP: `const` arm comfort-matched +0.28 %, but the varying arm read −4.50 %. Each plan's caps follow its own mean outdoor, so a cap that moves between re-plans breaks the telescope.
2. Uncapped, at each step's COP: the varying arm read +0.01 %. The COP-timing saving was cancelled.
3. Uncapped, converted at one COP and priced at one price per row (this head): `const` +0.28 %, varying +14.28 %.

Per-interval pricing of the store was not tried, because it cancels the price-timing saving the same way.

**Payments (no budget raised).** The diff first breached `class_excess_loc`, `max_class_loc` and `methods_over_150`. Each was paid in the code: the schedule is a module-level pure function (`_settlement_schedule`); `ledger.settle_interval_savings` is folded into its one caller; the pending snapshot copies `SETTLEMENT_KEYS` in one spread; `_settlement_at` replaces `get_current_action`'s baseline branch. `tests/structure_budgets.json` is byte-identical to main's.

**This repair (red checks on the previous head `212bef640`).** `tests / fast (3.14)` was branch-caused: `tests/stress.py`'s production-call check read the schedule's per-step work as growth on an unchanged plan. The schedule now (a) reads every trajectory and weather series as a list once, instead of `float(x[i])` per step; (b) reuses one `ThermalState` through attribute assignment, instead of `dataclasses.replace` per boundary; (c) builds the weather-only terms of the steady demand once per step through the new `_floor_demand_terms(model, outdoor_temp, wind_speed, precipitation, solar_radiation) -> (u, a, b)`, with `demand(T) = u * (T - outdoor) - a - b`, and `_floor_demand_at_target` is now one call of it, so the two targets of a step no longer rebuild the loss coefficient and the solar gain twice. Same expressions, same evaluation order. A copy of the formula beside the original, kept to leave the pins alone, breached `duplication_copies` (15 > 14: `tests/structure.py`), which is why the original delegates. The three ledger pins on the old lines of `_floor_demand_at_target` (`GUARD_OFF d85c286a`, `RETURN_DEL 654d95fe`, `RETURN_DEL 6a195c48`) and the bot's pin on `_settlement_schedule`'s old `max(0.0, ...)` line (`CLAMP_DROP 8c85837f`) named sites that no longer exist, and were deleted (`prepr.sh` step 6d predicted each as a STALE PIN).

## Head

`4cb24054d9056d986351e5ab06746cd8ded7ff3e`: the handoff tip `e0a411f2142e54c4eff7fb77e488d21f7f31e7ef` merged with `origin/main` `2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e` (merge, not a re-cut; no conflict, no code change by this repair). `tools/pr/prepr.sh` was run at this head after the merge, rc=0. `tests/structure_budgets.json` and both claim files are byte-identical to `origin/main`.

The measurements below were taken at the heads they name (`bfb9c1324`, `33cf259d6`, `e0a411f2`); the merge brought in main's commits only, and this repair changed no production file, test or budget.

## Mutation proof

Mutant: the settlement removed from the row at `bfb9c1324`. In `MonthlyLedger.savings_months`, `baseline_sek = self.line(key, "savings_baseline")["sek"] * scale + stored_sek` becomes `... * scale`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` prints `1 of 4783 FEATURE CHECKS FAILED`, rc=1. The one FAIL is `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price`.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py const` prints `const: DEFECT`, rc=1.

Restored, the head prints `ALL 4783 FEATURE CHECKS PASSED`, rc=0.

Failing test first for the repair: the red check itself. At the previous head `212bef640`, CI's `tests / fast (3.14)` ran `tests/stress.py` and printed `FAIL no scenario's production calls grew past what its work counts vouch for, on an unchanged plan (round 9)` with four scenarios over 1.05x (table below). The repair's mutant is the schedule's old per-step evaluation (the two `_floor_demand_at_target` calls and a `replace` per boundary): it reads the call counts of the "before" column, which is the red.

## Null control

- Production calls, same meter as `tests/stress.py` (`production_calls` over the package directory, `stress.build_case` of each combo, `PYTHONPATH=tests/hastub:tests:custom_components`), the baseline tree `8e90d8144` against this head `33cf259d6`. Control: the same command on the baseline, which is what the 1.05x allowance is applied to.

  | scenario | baseline | previous head | this head | this head / baseline | allowance |
  |---|---|---|---|---|---|
  | summer/1z/space | 76613 | 81185 | 79229 | 1.034 | 80443 |
  | summer/2z/space | 82941 | 89156 | 86726 | 1.046 | 87088 |
  | summer/2z/space/wood-two-tank | 114060 | not measured | 118233 | 1.037 | 119763 |
  | winter/1z/space/pin-off | 80209 | not measured | 82800 | 1.032 | 84219 |

  The "previous head" figures for the first two rows are the repair's starting point on this machine; CI's figures for the four scenarios at `212bef640` were 1.061x, 1.076x, 1.059x and 1.058x. The full `tests/stress.py` was not run here (CI runs it past the handoff); the four scenarios CI named were measured with its own meter.
- Bit identity of the demand terms: for 5000 random weather inputs each on a single-zone and a two-zone `ThermalModel`, the old inline formula, `_floor_demand_at_target` and `u * (T - out) - a - b` agree with max abs diff 0.0 (a throwaway script outside the tree).
- The same closed loop booked without the new readings (`baseline_kw` alone, the pre-ruling row), inside `r10_sav_null_settled.py`: varying arm 12.34 %, `const` arm 11.86 %.
- `dev/audit/harnesses/r10_sav_baseline.py` (sha1 `bc31f356191ededbfb0b15f768b258249867b134`): transient SOUND, spread 0.00 kW; null DEFECT 12.336145360155744 % (it books `baseline_kw` alone, by construction).
- `dev/audit/harnesses/r10_sav_volume.py` (sha1 `be62082cc746a336a5580742b3047b2acc8f17df`): flat volume +0.00, timing +0.00, vary timing +74.88.
- `tests/features.py`: `R10-SAV-COMFORT null control: an interval without either reading settles nothing`.
- `dev/audit/harnesses/r10_sav_actuation_phase.py` (sha1 `d8871c1b96466f7d0d16df9ecc15454512d6adc5`): `AGREE: yes`.

## Figures

- The ruling's acceptance: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py` (sha1 `eca29a18ee192f0d3727e447e1f981326fe5b9c0`) at `bfb9c1324`, rc=0.
  - vary: saved 32.16 (19.23 %), `stored_heat_sek` 13.15, `comfort_sek` 8.28; comfort-matched 23.88 (+14.28 %), SOUND.
  - const: saved 6.62 (4.77 %), `stored_heat_sek` −11.15, `comfort_sek` 6.23; comfort-matched 0.39 (+0.28 %), SOUND.
  - The verdict rule: `const` `|pct| < 3.0`, vary `pct >= 3.0`.
- Carry terms: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_terms.py` (and with `const`, sha1 `c981e7c840ede1a5fef95aa903e00e5809c92aa7`), at the head and the base, identical.
- Summer limit: `tests/golden/summer_dhw_only.json` `savings_percentage` −3.173852 at the head and the base; `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` exits 0.
- Class seams: `git grep -n "observe_spot_and_settle_savings\|add_savings_settlement" -- custom_components`, `git grep -n '"baseline_kw"' -- custom_components` and `git grep -n SETTLEMENT_KEYS -- custom_components` return the coordinator's pending snapshot and the ledger's booking as the only readers, as before the repair. `git grep -n "_floor_demand_at_target\|_floor_demand_terms" -- custom_components` returns `_floor_demand_at_target`'s three other callers (unchanged signature and value, bit-identical per the control above), `_settlement_schedule` and the definitions.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` names a scoped gate; at this head the scripts the diff reaches that were run here are `tests/features.py`, `tests/structure.py`, `tests/entities.py`, plus `tests/stress.py`'s production-call meter as measured above; `tests/stress.py` and the closure re-recording are left to CI.
- Feature suite: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4783 FEATURE CHECKS PASSED` at this head.
- Entities: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2602 ENTITY CHECKS PASSED`.
- Structure: `PYTHONPATH=tests/hastub python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` against main's budgets, byte-identical.
- Pre-PR: `bash tools/pr/prepr.sh` at this head, rc=0.

## Unpinned sites

`prepr.sh` step 6d, run at this head (merge `4cb24054d` of the handoff tip and `origin/main` `2a9cd3476`, rc=0), lists 24 sites the diff adds with no pin: 4 in `ledger.py` and 20 in `optimizer.py`. The earlier body listed 24 `ledger.py`-era sites at old line numbers; the merge with main moved `optimizer.py` and the list below is the whole 6d output at this tree, not a subset. Every site is under `custom_components/`, the one directory `mutation-autofix` mutates, so each one's disposition is `mutation-autofix`: it pins the site when its mutant is killed. This seat has not run a ledger mutant per site; a survivor the lane reports goes to a triage file under `tests/mutation_ledger/survivor_triage/` before merge, and none is claimed killed here. The lines are the 6d line numbers at this head.

- `custom_components/heatpump_optimizer/ledger.py:261 BOOLOP` (`fee_per_kwh = float(fee) if isinstance(fee, (int, float)) an`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:309 CLAMP_DROP` (`self.observe_meta_mean(when, STEADY_COP_META, max(float(stea`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:310 GUARD_OFF` (`if comfort_kw is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:426 CMP_BOUND` (`stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else s`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:375 GUARD_OFF` (`if not p.two_zone_enabled:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:379 RETURN_DEL` (`return u_eff, p.internal_gains, model.compute_solar_gain(sol`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:385 RETURN_DEL` (`return u_lower, q_solar_lower, q_int_lower`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:405 RETURN_DEL` (`return u * (target - outdoor_temp) - a - b`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:454 BOOLOP` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:454 CMP_BOUND` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:465 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:485 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:488 GUARD_OFF` (`if bufs is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:494 CMP_BOUND` (`if cop < 1e-3:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:494 GUARD_OFF` (`if cop < 1e-3:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:499 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:502 GUARD_OFF` (`if bufs is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:515 CMP_BOUND*2` (`(d_t if d_t > 0.0 else 0.0) - (d_d if d_d > 0.0 else 0.0)`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:519 CMP_BOUND` (`if i < n_base:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:519 GUARD_OFF` (`if i < n_base:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:533 CMP_BOUND` (`if i < len(result.settlement_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:535 CMP_BOUND` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:535 GUARD_OFF` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:537 RETURN_DEL` (`return {}`): mutation-autofix

## Red checks

Concluded reds on the pull request's current head `6f742a33e5216932d4fb0f4583e09b137432ea9f` (the check-run set read in full, 66 runs over two workflow runs; other jobs were still in progress or green or skipped). The pull request has not yet been moved to this head, so no CI has concluded at it:

- `tests / typing`: branch-caused (9 `no-untyped-call` errors from `_settlement_schedule`'s untyped `_l` lambda). Repaired at the root in `e0a411f2`: `_l` is `def _l(x: Any) -> list[Any]`, no new `# type: ignore`. Measured at this head with the pinned toolchain (`mypy 2.4.1`, `homeassistant-stubs 2026.9.3`, `scipy-stubs 1.18.1.1`): `python3 tests/typing_ruler.py --mypy` prints `ALL 9 typing-ruler checks PASSED`, including `errors did not grow` and `type_ignores did not grow`. Cheaper detector: that same command; `prepr.sh` does not run it, and its standing cost is a pinned venv plus about one minute, owed on any diff adding a lambda or unannotated helper in `custom_components/`.
- `tests / mutation`: the lane refuses unpinned sites; the answer is `mutation-autofix` for every site under `## Unpinned sites`. Cheaper detector: `tools/pr/ci_predict.py` (`prepr.sh` step 6d), which predicted the list before the push at the cost of one pass per `prepr.sh` run. The prior body listed an out-of-date set, which is the fault this repair fixes.
- `tests / nightly-status`: inherited, push-only and unrequired; it concluded `failure` on `origin/main` as well (the `Nightly` workflow, run `41818271059` at `8e90d8144`), and is owed a `gh workflow run nightly.yml --ref main` by the nightly's owner. No cheaper detector exists for a nightly's state.

- `tests / mutation-autofix`: red per the pull-request-body check at this tree (the check-run listing read here shows it `skipped` in the workflow run I could read, so the red run's output was not read by this seat). It is the lane that pins the sites under `## Unpinned sites`; its red is the same unpinned-site refusal as `tests / mutation`, and the answer is the same: the list below is now complete at this tree, so the lane has every site's disposition. Cheaper detector: `prepr.sh` step 6d (`ci_predict.py`), one pass per run; it predicted all 24 here.
- `tests / replay`: concluded `failure` at `6f742a33` (job `126851204938`, 20:41 to 20:53Z). This seat did not read the failing line: the job log tail the tool returned held only checkout cleanup. The earlier body measured the same class (`synthetic-dhw-only.json` `cpu_ratio` over its budget on the baseline tree as well); whether this run is that fixture is not established here. If it is, the answer stands as written in the earlier-heads paragraph below (not branch-caused, owed a re-centre by the budget's owner). The cheaper detector: none exists for a CPU-time ratio on a shared runner.

Earlier heads (`212bef640`): `tests / fast (3.14)` (stress production-call meter, repaired by the schedule rewrite above; cheaper detector: the production-call meter by hand, about 40 s per scenario pair) and `tests / replay` (`synthetic-dhw-only.json` `cpu_ratio`, not branch-caused: the baseline reads over budget on the same machine, six of six runs). `fast (3.14)` was still in progress at `6f742a33` when read; if either concludes red at the final head it is owed the same answers.

## Forward-carry

- The summer start-bound limit: `optimizer._start_gap_cost` caps the start-of-horizon settlement at the thermostat's space-heat cost, which leaves `summer_dhw_only`'s predicted savings negative (−3.17 %). Carry: #2492
- Carry 5: reconcile `power_ratio` and the planner's over-booking on one sample window (`dev/audit/harnesses/r10_demand_overbook.py`). Carry: #2492
- The replay `loop_cpu_ratio` reading on `synthetic-dhw-only.json` (above) if `tests / replay` is red at this head. Carry: #201

## Friction

none
