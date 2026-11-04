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

`e0a411f2142e54c4eff7fb77e488d21f7f31e7ef`: the previous head `33cf259d6` plus a typing repair (`_settlement_schedule`'s untyped `_l` lambda is now a typed nested function) and a merge of `origin/main` (`d7582ed404a87603bd02fefda610d7ebbe4181e1`, `prepr.sh` rerun after it, rc=0, 2026-11-04). The previous head was the authored code head plus the repair above, and the merge of the bot's `48b96f391` (`ci: pin killed mutants`, 4 pin files, one of them since retired). `origin/main` was `8e90d81443317f76f22602a89651f7ca17c633f9` at 2026-11-04T14:50Z, the same commit this branch was last merged with, so no merge was owed and `prepr.sh` was run once at this head (rc=0; the body check is `body_push.sh`'s).

The earlier measurements (harness figures below, the ruling's acceptance, the carries) were taken at `bfb9c1324`; the repair touches `_settlement_schedule`'s evaluation and `_floor_demand_at_target`'s body, not the ledger. At this head `tests/features.py` (4783 passed), `tests/structure.py`, `tests/entities.py` (2602 passed) were re-run with `PYTHONPATH=tests/hastub`, and the production-call meter was measured below.

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

`prepr.sh` step 6d lists 24 sites the diff adds with no pin. Every one is under `custom_components/`, the lane `mutation-autofix` mutates, so each one's disposition is `mutation-autofix`: pinned by it when killed. A survivor it reports goes to triage under `tests/mutation_ledger/survivor_triage/`. The bot has already pinned four sites at the previous head (`48b96f391`); three still stand and the fourth was retired above.

- `custom_components/heatpump_optimizer/ledger.py:261 BOOLOP` (`fee_per_kwh = float(fee) if isinstance(fee, (int, float)) an`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:309 CLAMP_DROP` (`self.observe_meta_mean(when, STEADY_COP_META, max(float(stea`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:310 GUARD_OFF` (`if comfort_kw is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/ledger.py:426 CMP_BOUND` (`stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else s`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:355 GUARD_OFF` (`if not p.two_zone_enabled:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:359 RETURN_DEL` (`return u_eff, p.internal_gains, model.compute_solar_gain(sol`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:365 RETURN_DEL` (`return u_lower, q_solar_lower, q_int_lower`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:385 RETURN_DEL` (`return u * (target - outdoor_temp) - a - b`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:434 BOOLOP` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:434 CMP_BOUND` (`buffer_temps if buffer_temps is not None and len(buffer_temp`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:442 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:462 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:465 GUARD_OFF` (`if bufs is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:471 CMP_BOUND` (`if cop < 1e-3:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:471 GUARD_OFF` (`if cop < 1e-3:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:476 GUARD_OFF` (`if two_zone:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:479 GUARD_OFF` (`if bufs is not None:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:492 CMP_BOUND*2` (`(d_t if d_t > 0.0 else 0.0) - (d_d if d_d > 0.0 else 0.0)`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:496 CMP_BOUND` (`if i < n_base:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:496 GUARD_OFF` (`if i < n_base:`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:510 CMP_BOUND` (`if i < len(result.settlement_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:512 CMP_BOUND` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:512 GUARD_OFF` (`if i < len(result.baseline_power_schedule):`): mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:514 RETURN_DEL` (`return {}`): mutation-autofix

## Red checks

- `tests / typing`: branch-caused. 9 `no-untyped-call` errors, all from `_settlement_schedule`'s `_l = lambda x: ...`, which mypy types as untyped. Repaired at the root, not silenced: `_l` is now `def _l(x: Any) -> list[Any]` (no new `# type: ignore`). Measured with the pinned toolchain (`tests/requirements-typing.txt` in a fresh venv): `python3 tests/typing_ruler.py --mypy` prints `ALL 9 typing-ruler checks PASSED`, including `errors did not grow` and `type_ignores did not grow`; `tests/structure.py` passes. The cheaper detector is that same command, which `prepr.sh` does not run (`tests/run.sh` runs only the source-only ruler off the pinned pair); its standing cost is one venv install plus about one minute, owed on any diff adding a lambda or unannotated helper in `custom_components/`.
At the previous head `212bef640`, four checks concluded red:

- `tests / fast (3.14)`: branch-caused, fixed at its root in this head. The failing line is `tests/stress.py`'s production-call check (1.06x to 1.08x of the baseline's calls on four scenarios, work counts flat, over the 1.05x allowance; `optimizer.py` +3580 to +4647 calls). Cause: the new `_settlement_schedule` ran per-step conversions and two full steady-demand evaluations on every solve. The cheaper detector is the production-call meter this seat ran by hand per scenario (`production_calls` over `stress.build_case`, about 20 s per scenario), which `prepr.sh` does not run and the scoped gate leaves to CI; the standing cost of running it before a handoff on any diff that touches `optimizer.py`'s per-solve path is one scenario pair, about 40 s. The repair's figures are in the Null control table.
- `tests / mutation`: the lane's first job refuses unpinned sites; the answer is `mutation-autofix`. It pushed `ci: pin killed mutants` (`48b96f391`) on the previous head, four pins. This seat read no check-run output for the job itself. The repair moves two of the sites, so one of the bot's four pins and the three on `_floor_demand_at_target` are retired here, and the sites that replace them are listed under `## Unpinned sites`. The cheaper detector is `tools/pr/ci_predict.py` (`prepr.sh` step 6d), which predicted each STALE PIN and each unpinned site before the push; its standing cost is one pass per `prepr.sh` run.
- `tests / replay`: not branch-caused. The failing line is `synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.326 over its budget 2.173]`, one of 176 replay checks, and the same log prints `record: synthetic-dhw-only.json cpu_ratio=3.289` for the same fixture (2.326 x sqrt 2). Measured on this machine with `python3 tests/replay.py --one tests/replay/synthetic-dhw-only.json` (the lane's per-fixture child, `HASTUB_TZ=Europe/Stockholm` and the BLAS pins of `child_env`), alternating the baseline tree `8e90d8144` and this branch, three runs each: `cpu_ratio` 2.9269, 2.7924, 2.7136 on the baseline (mean 2.81) and 2.7926, 2.5914, 2.7957 on this branch (mean 2.73), against the 2.173 budget; all six are over it, so the baseline reads the failure too and the number does not separate the trees. `loop_cpu_ratio` (budget 0.143) read 0.136 to 0.152 on the baseline and 0.153 to 0.155 on the branch, three of three over on the branch and one of three on the baseline: this seat does not rule out a small real loop cost from the added per-solve work, and reports it rather than waving it through. `origin/main` at `8e90d8144`'s own CI run reached `tests / replay` green, so the lane is not red on main. The standing detector is the lane itself; a cheaper one does not exist for a ratio of CPU time on a shared runner (this is the class #3174 re-centred, merged). If `replay` is red again at this head after the pins, it is owed a re-centre by the owner of that budget rather than a raise here.
- `tests / nightly-status`: inherited, push-only and unrequired. `origin/main` at `8e90d8144` carries it too: the `Nightly` workflow run on that merge concluded `failure` (run `41818271059`). Its own log says a red there is owed a fix and a proof by `gh workflow run nightly.yml --ref main`, which belongs to whoever owns the nightly and not to this diff, and this seat cannot dispatch it (no `gh` binary).

The R10 N-no-expiry barrier in `tests/entities.py` and the census in `tests/typing_ruler.py` went red locally during the earlier work, never on a pushed head, and both pass at this head's `entities.py` run.

## Forward-carry

- The summer start-bound limit: `optimizer._start_gap_cost` caps the start-of-horizon settlement at the thermostat's space-heat cost, which leaves `summer_dhw_only`'s predicted savings negative (−3.17 %). Carry: #2492
- Carry 5: reconcile `power_ratio` and the planner's over-booking on one sample window (`dev/audit/harnesses/r10_demand_overbook.py`). Carry: #2492
- The replay `loop_cpu_ratio` reading on `synthetic-dhw-only.json` (above) if `tests / replay` is red at this head. Carry: #201

## Friction

none
