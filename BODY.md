R10-SAV-COMFORT part 2: the duty ledger's run fold settles one tick into each step (carry 8); the other seven carries answered.

Part of #2492. Part of #201. Critical path: R10-SAV-COMFORT. #2492 stays open: carries 6 and 7 are routed back to it.

Status: carry 8 built here; carries 2, 3 and 5 already on main; carries 1, 4, 6 and 7 deferred, each routed to #2492 (`Carry: #2492`), carry 7 pending the owner's ruling below.

**Carry 8 (#2968's residue), measured first.** `pump_arbiter._observe` folded a run at any tick reading at or above `on_threshold_kw`. The supply tick writes the switch on the step's first tick, and the arbiter's tick in that same minute reads the meter before the write shows, so the first reading of a planned-idle step after a planned-on step is the on step's tail. The probe is the step-boundary install `tests/features.py` already drives (section "supply switch at step boundaries"): its meter follows the switch one minute late. At the merge base every planned-idle step after a planned-on step books `space-instead` (5 of the install's 16 steps); with the tail removed (`tail=False`, the meter set to the step's own command before the step's first pass) the same steps book `delivered`. The verdict changes with the tail, so the carry's fix applies: `RUN_SETTLE` (one arbiter tick, `_TICK`) in `pump_arbiter`, and `_observe` folds a reading into neither `measured` nor `ran` until the step is that old. One owner, no per-call flag.

The window is one tick, not two. The mechanism measured is the two ticks firing in the same minute. A two-tick window was tried first: it also drops the reading one minute into a step, which `tests/features.py`'s existing duty-ledger checks take as a real in-step reading (`_pa_led`, `_pa_edge`, `_pa_lg` read the meter at minute 1 of each step). A longer meter lag than one tick is not measured anywhere in the tree and is not claimed here.

**Carry 7, measured, and the ruling it needs.** The carry asks for a priced comfort shortfall. `dev/audit/harnesses/r10_sav_null_terms.py` (sha1 `c981e7c840ede1a5fef95aa903e00e5809c92aa7`) already prices exactly that: a steady thermostat at the comfort target against one at the room the plan delivered, through the production `_floor_demand_at_target` and `compute_cop`. Netting that comfort term out of the gap leaves the varying-outdoor arm at +6.93 % of the steady-at-target kWh and the `const` arm at +7.44 %, both above the owner's 3.0 bar. So a priced comfort shortfall alone cannot meet the owner's flat-price null, and no change was made to the month row. In the `const` arm the remainder (9.3 kWh) equals the stored-heat drawdown at the steady COP (9.3 kWh_e), so comfort priced plus stored heat settled at both ends reads about 0 there, which is carry 1's acceptance. Meeting it in the month row means settling stored heat in the ledger row, a seam #2745 did not open and that carry 4's baseline definition owns. The carry's fallback is the owner's ruling, which this seat cannot obtain: which of start-independence (#2255) or comfort matching the month row keeps, and whether the row settles stored heat. Routed to #2492.

**The carries, one by one.**

- Carry 1 (the three-term separation): on main through #2745 (`34cd75bf1`), which reports the terms and keeps the timing term. The null's residual is carry 7's, routed with it. Carry: #2492
- Carry 2 (volume against timing): on main, `34cd75bf1` (#2745: `MonthlyLedger.meter_calibration`). `r10_sav_volume.py` at this head: flat volume +0.00 and timing +0.00, vary timing +74.88. `git merge-base --is-ancestor 34cd75bf1 origin/main` exits 0.
- Carry 3 (card equal to the ledger): on main, `34cd75bf1` (#2745: `tests/card.mjs` renders the Savings tab from the `MonthlySavingsSensor` payload `tests/plan_view.py` builds and asserts each cell against `ledger.savings_months`).
- Carry 4 (the owner's baseline specification): the meter-calibrated basis is on main, `34cd75bf1`; flat-price timing reads 0 (carry 2's arms). The finder's `|pct| < 3.0` null is not met (12.34 % at this head) and is carry 7's question. Carry: #2492
- Carry 5 (the duty ledger's seams): on main. Seam 1, the re-freeze of `planned` at each plan adoption, is `34cd75bf1` (#2745); seam 2, the switch written at step boundaries, is `5d4e0bcfb` (#2968). `git merge-base --is-ancestor 5d4e0bcfb origin/main` exits 0.
- Carry 6 (power ratio against the planner's over-booking on one sample window): not measured here; it needs a sample window the tree does not hold and is outside carry 8's fold. Carry: #2492
- Carry 7 (the flat-price null books the comfort shortfall as a saving): measured above, needs the owner's ruling. Carry: #2492
- Carry 8 (the tail power): built here.

## Head

`a53a7e68286d9455aa2f2a320699b4bf170f6eba`. The branch was cut at `d052f80f7f81d42db5c57a55ebaef7056c7ce01a`; commits: the failing test (`9c42e08d1`), the fix (`5d37f168f`), the mutation-ledger re-pin (`9be75cb36`), a merge of origin/main `ca6333333` (`1c6a87c66`), and a merge of origin/main `407eb0cb38f3cd43e71f4ed7be1c23f80dc32cc1` (this head), both without conflict, each because main moved after a `prepr.sh` run. Neither merged delta (`git diff --stat d052f80f7 407eb0cb3`) touches a file under `custom_components/`, `tests/features.py`, an `r10_sav_*` harness or the `pump_arbiter.py` ledger pins. `tests/features.py`, `r10_sav_actuation_phase.py` and `tests/structure.py` were re-run at `1c6a87c66`, and `prepr.sh` at this head; the mutation proof and the savings harness figures were taken at `5d37f168f` and the base.

## Mutation proof

Mutant: the fix's predicate removed at the head, `if power is not None and now - start >= RUN_SETTLE:` back to `if power is not None:` in `pump_arbiter._observe`, then `PYTHONPATH=tests/hastub python3 tests/features.py` in a detached worktree at the head. It prints `1 of 4682 FEATURE CHECKS FAILED`, rc=1, the one FAIL being `a planned-idle step books no run from the previous step's tail power (#2492 carry 8)`. Restored; the head prints `ALL 4682 FEATURE CHECKS PASSED`, rc=0.

Failing test first: the head's `tests/features.py` against the merge base's `custom_components/` prints `1 of 4682 FEATURE CHECKS FAILED`, the same one check, and its null control passes there.

## Null control

- The same install with the meter tail removed (`_sa_install(0, tail=False)`): every step `delivered` at the merge base and at the head, and its switch writes equal the tailed install's. Pinned as `null control: without the meter tail every step is delivered`.
- `dev/audit/harnesses/r10_sav_actuation_phase.py` (sha1 `d8871c1b96466f7d0d16df9ecc15454512d6adc5`): `AGREE: yes` at both ends. At the merge base phase 0 books `space-instead` at steps 1, 4, 7, 9 and 14; at the head every step from 1 on is `delivered` at both phases. Step 0 at phase 14 stays `idle-instead`, before that install's first cycle, as the harness states.
- `dev/audit/harnesses/r10_sav_baseline.py` (sha1 `bc31f356191ededbfb0b15f768b258249867b134`), unchanged by this diff and identical at both ends: transient SOUND, spread 0.00 kW; coverage SOUND; cost DEFECT (the one-basis row, as #2745 recorded); null DEFECT, 12.336145360155744 %.

## Figures

- Duty verdicts at both ends: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_actuation_phase.py`, at `d052f80f7` and at `5d37f168f` (Null control).
- Feature suite: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head, all pass; with the base's `custom_components/`, one FAIL; with the mutant, one FAIL (Mutation proof).
- Carry 7's terms: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_terms.py` and the same with `const`, at the head and at the base, identical: varying arm comfort gap 6.9 kWh, residual +6.93 %, drawdown -11.3 kWh_e, timing +17.29 %; `const` arm comfort gap 5.2 kWh, residual +7.44 %, drawdown 9.3 kWh_e, timing +0.00 %. The `const` arm's timing +0.00 % is the control separating timing from comfort.
- The finder's null: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline.py`, null 12.336145360155744 % at the head and the base (10.83 % at 92588d581, as the carry records; main moved it, not this diff).
- Volume and timing: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_volume.py` at the head: flat SOUND (0.00), vary SOUND (timing +74.88).
- Class seams: `grep -rn "measured_power_kw" custom_components/heatpump_optimizer/ --include=*.py` returns two readers. `pump_arbiter._observe`, the per-step fold, is closed here. `external_heat.py`'s idle test reads the cycle's own sample against `idle_power_kw` and folds nothing per plan step, so no step boundary applies: not this class.
- Gate scope: `python3 tests/closure.py select --diff d052f80f7f81d42db5c57a55ebaef7056c7ce01a --workdir <dir>` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out` over `pump_arbiter.py` and `tests/features.py`. `features.py` and `structure.py` ran here; the rest of `scope.run` is left to CI.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Mutation ledger: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main --pin-killed` prints `PIN KILLED: 3 pinned, 0 left unpinned` for the rewritten guard line in `_observe` (BOOLOP killed by `tests/guard_pins.py`, CMP_BOUND by `tests/features.py`, GUARD_OFF by `tests/structure.py`); the pin `_observe GUARD_OFF c1a392c4` named the old text of that line and is removed.
- Pre-PR: `bash tools/pr/prepr.sh <body>` at this head, rc=0; its carry step prints `0 bad destination(s)` against the roster ref.

## Red checks

none

## Forward-carry

- Carry 7: the owner's ruling on the month row's flat-price null (start-independence or comfort matching, and whether the row settles stored heat), with the priced-comfort figures above. Carry: #2492
- Carry 6: reconcile `power_ratio` and the planner's over-booking on one sample window (`dev/audit/harnesses/r10_demand_overbook.py`). Carry: #2492

## Friction

none
