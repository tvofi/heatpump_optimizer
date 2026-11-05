The owner's month row read nonsense on a valved house with a wood tank (tvofi, 2026-11-04): November's reference far below the meter, a percent clipped at -100. The settlement booked the thermostat's first step of a plan re-made every interval, and behind a valve that step read the stores' transient. This pull request books the reference with no wood on any house (owner ruling, 2026-11-04), holds its tank behind a valve at the temperature that delivers the need and spreads its horizon by the steady demand, unclips the month percent, floors the calibration at 1.0 on a wood-configured house, and stamps each month with the reference basis it was booked on, so a month booked against the retired reference keeps both columns and states no saving.

**The owner's September, October and November rows show a dash, and the first saving figure arrives with the next new month.** Totals are never rewritten.

Carry 1, the owner's no-wood ruling (2026-11-04): done. The reference has no wood tank, no fire and no refill coil on any house; wood-configured houses show a figure with the disclaimer that the saving includes wood's heat and firewood's cost is not counted, and old-basis rows keep the dash. Pinned by `the reference has no wood: a wood tank, cold or warm, reads the plain valved house's kW` and `the reference's hot water has no refill coil: a known wood tank moves nothing (owner ruling, 2026-11-04)`, both passing in this pass's `tests/features.py` run at ca0d33c12.

Carry 2, triage P387 (`dev/programme/triage/s6-batch122.md#P387`, metered kWh cancels in the calibrated percent): answered by the calibration floor. On a wood-configured house calibration may only raise the reference, so a meter under the plan is never scaled down (option A, relayed by the orchestrator under the mandate, pending the owner's override); with no wood the 2026-10-24 calibration stands as specified. Pinned by `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`, passing in the same run.

## Re-cut

Round 4. The production change is the reviewed one (1d114ed62, merge verdict at 6790e0966) and is untouched here: this pass only answers `tests / mutation`, which refused the eight sites the diff adds without a disposition, and `tests / mutation-autofix`, red on `skip-nothing-killed` (run 42024722714). Per `ci-autofix.md` the triage is manual: six sites get a killing check, two a written `equivalent` verdict, and `--pin-killed` records the kills. Every figure below was taken in this pass.

## Head

`95aa1e74e86fbe3dce7dc48d27a6bbc8d5c2e721`. It is the PR head 6790e0966 plus:
- 5011cdd1e, the merge of origin/main 8bf45e5dc (no conflict);
- 5854e298a, the store, ledger and zero-demand checks and the assert triage;
- ca0d33c12, the feasible-start check and the wood stand-in triage;
- ea6fbc8fb, `ci: pin killed mutants`, the six `killed_by` rows `--pin-killed` recorded at ca0d33c12;
- 17e27ef51, the merge of origin/main 8b49d50b0 (#3228: CI-ratchet tooling, `tests/ci_budgets.json` and its delivery row; no conflict);
- 95aa1e74e, the merge of origin/main 2dc960f4a (#3222 and #3227: seat-identity guards, the body contract, carry tooling and `prepr.sh`; no conflict).

Merge base `2dc960f4a92b1ebf56ed5aa33f55400d8e269a10`, the tip of origin/main at 2026-11-05 19:55 UTC (`date -u`). Main moved twice during this pass. `tools/pr/prepr.sh` and `tests/structure.py` ran at this head, against this base. The mutation table and the scoped gate ran at 17e27ef51 against 8b49d50b0; the last merge's delta is governance tooling, policy fixtures and their closures, and touches no production file, no test those two ran beyond its own tooling, and no mutation record. Every other figure names the commit it was taken at, each before both merges; neither merge touches a production file or a mutation record.

The step ref `handoff-wip/r10-hotfix-sav-estimate` held the previous return's body commit 5f35e7664, not an ancestor of this head; deleting it was refused in this container, so this pass's step pushes are commits on top of it whose tree is this head's. `handoff/` carries the code head alone.

## Mutation proof

Each survivor, with the check present and absent. "Absent" is the tree at 5011cdd1e (the merged PR head, without this pass's checks); "present" is the drive at ca0d33c12 (`--pin-killed`) or 5854e298a (`--anchor`, store sites). Line numbers are at this head.

| site | disposition | absent | present |
|---|---|---|---|
| `store.py:831 BOOLOP` (`LedgerStore._async_migrate_func`) | check in `tests/finite_boundary.py`: `the ledger store migrates only a v1 mapping; a newer major and a v1 non-mapping reach the default hook's NotImplementedError` | `mutation_table.py --anchor ... --scripts tests/finite_boundary.py`: `LIVES` | same command: `killed by tests/finite_boundary.py`; `--pin-killed`: `pinned ... -- killed by tests/finite_boundary.py` |
| `store.py:833 RETURN_DEL` (same method) | the same check | `LIVES` | `killed by tests/finite_boundary.py`; `--pin-killed`: `pinned ... -- killed by tests/finite_boundary.py` |
| `ledger.py:75 CONST` (`REFERENCE_BASIS = 1` to 2) | check in `tests/features.py`: `a month a v2 store holds stamped 1 reads on the current reference` | `--anchor ... --scripts tests/features.py`: `LIVES` | `--pin-killed`: `pinned ... -- killed by tests/features.py` |
| `optimizer.py:595 CMP_BOUND` (`_thermostat_held_state`, `need > 0.0` to `>=`) | check in `tests/features.py`: `behind a valve at zero demand the held tank keeps its measured temperature, and a horizon with no steady demand keeps its simulated schedule` | `--anchor`: `LIVES` | `--pin-killed`: `pinned ... -- killed by tests/features.py` |
| `optimizer.py:5552 CMP_BOUND` (`_apportion_by_steady_demand`, `total <= 0.0` to `<`) | the same check | the mutant applied to 5011cdd1e, full `tests/features.py`: `ALL 4855 FEATURE CHECKS PASSED`, rc 0 | `--pin-killed`: `pinned ... -- killed by tests/features.py` |
| `optimizer.py:4772 CLAMP_DROP` (`_optimize_space_only`, the seed's `np.clip`) | check in `tests/features.py`: `behind a valve, a reference spread past the pump seeds the space solve only inside its bounds` | the mutant applied to 5011cdd1e, full `tests/features.py`: `ALL 4855 FEATURE CHECKS PASSED`, rc 0 | `--pin-killed`: `pinned ... -- killed by tests/features.py` |
| `optimizer.py:5541 BOOLOP` (`_apportion_by_steady_demand`'s assert) | `survivor_triage`, `equivalent`: its only caller, `_compute_baseline_power`, asserts the identical conjunction on the same series first | n/a | n/a |
| `optimizer.py:536 CONST` (`_NO_WOOD_TANK_C = 0.0` to 1.0) | `survivor_triage`, `equivalent`: below every zone, either value takes no wood share; differential drive under `## Figures` | n/a | n/a |

Two absent runs were taken as one mutant run of the full `tests/features.py` rather than `--anchor`, which costs about 40 minutes a site on this 4-core host (baseline, null and mutant). The present-check runs of `--anchor` for the store sites read `null control ... NULL_COMMENT survived tests/finite_boundary.py` beside the kill, so the driver separates a real mutant from a comment edit.

## Null control

- The zero-demand probe is not vacuous: on the head the held tank stays at its measured 37.5 C, and the mutant at line 595 sets it to 21.0 C (`valve_hold_temperature` at a need of 0), measured by a direct call before the check was written. At 30 C outdoor and 800 W/m2 the steady demand is 0 on every step, so `total` is exactly 0.0 and the line-5552 mutant divides by it.
- The feasible-start check asserts its own precondition: the reference peak must exceed the pump (`max(_hz_baselines) > p_max`), so it cannot pass on a horizon where the clamp never bites. Over a 27-case probe (pump 3, 4 and 6 kW; -25, -15 and -5 C nights; 0, 400 and 900 W/m2 midday sun; manual valve), the reference peak reached 1.226x the pump at 3 kW, -25 C and 400 W/m2 (the check's case), and every start the solve was handed read at most 1.000x its bound at the head.
- The stamp check uses the literal 1.0 a v2 store holds on disk. The first-booking check beside it (`a month's first savings booking stamps the reference in force, once`) compares against the constant itself, which is why the CONST mutant survived it.
- Wood stand-in null: the 192-case differential drive below with the constant unchanged against itself is the head's own run; the mutant's run is the same driver with `optimizer._NO_WOOD_TANK_C = 1.0` set before any solve. The same 192 cases were also driven with the CLAMP_DROP mutant: 0 differ, and over those cases the seed never left [0, p_max], so that grid is the reason a targeted horizon was needed for the check.

## Figures

Env: `PYTHONPATH=tests/hastub` for the suite scripts, `PYTHONPATH=tests/hastub:tests:custom_components` for the harnesses and probes. Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` prints `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`; `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` prints `2.5.4 1.18.1`, equal to `tests/requirements-ci.txt`.

The fix, at both ends (harness copies run from scratch, so each tree measured the same file):
- `dev/audit/harnesses/r10_sav_wood_reference.py` (sha1 23f17afe540f2cc82f7f5d5e1f4d4fe51b36d736), arms `first`, `valve-flat`, `valve-vary`:
  - at origin/main 8bf45e5dc: `first: DEFECT` (`wood-valve buf 40.0 wood 5.0: step0 0.000 mean 1.460 step0/mean 0.000 zero 13 BAD`), and `valve-flat` and `valve-vary` stop on `TypeError: MonthlyLedger.savings_months() got an unexpected keyword argument 'wood_configured'`;
  - at this pass's tree (production identical to 6790e0966): `first: SOUND` (step0/mean 1.000), `valve-flat: SOUND` (pct +0.56, residual -3.90 %, rule `flat |pct| < 10.0`), `valve-vary: SOUND` (pct +25.26, residual -8.02 %).
- The finder's census `dev/audit/harnesses/r10_rca_sav_estimate.py census` (sha1 04b644563c84d26378cad42a603dc050e7e5fd88): at origin/main `census: 6 of 6 cells ran, 4 out of band: valve-at-curve valve-charged wood-warm wood-hot`; at this tree `census: 6 of 6 cells ran, 0 out of band: -`.

The wood stand-in's differential drive (the probe stays in scratch, a one-off per fixer step 18): `HeatPumpOptimizer.optimize` over 192 cases, weather `winter_cold`, `winter_mild`, `shoulder`, `summer_cool`; prices `flat`, `winter_extreme`, `winter_typical`; single and two zone; no valve and a manual valve; with and without the two-tank 4-way layout (24 cases resolve `two_tank_modelled`); wood tanks at 60 and 80 C. Rule: a case differs when any of predicted cost, predicted saving or the baseline power schedule differs bitwise. Head against `_NO_WOOD_TANK_C = 1.0`: 0 of 192 differ.

The suite (each line names its commit):
- `python3 tests/features.py` at ca0d33c12: `ALL 4858 FEATURE CHECKS PASSED`, rc 0 (4855 at 5011cdd1e; this pass adds three).
- `python3 tests/finite_boundary.py` at 5854e298a: `ALL 109 FINITE BOUNDARY CHECKS PASSED`, rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (standalone at 5854e298a, in the gate at 17e27ef51, and standalone at this head). No budget file changed in this pass; `tests/structure_budgets.json` differs from origin/main only downward (class_excess_loc 17589 against 17617), as before.
- `python3 tests/typing_ruler.py`: `ALL 12 typing-ruler source checks PASSED`. `tests/typing_ruler.py --mypy` under a Python 3.14.7 venv installed `--no-deps --require-hashes` from `tests/requirements-typing.txt`, as `tests.yml` installs it: `ALL 9 typing-ruler checks PASSED`.
- Gate scope: `python3 tests/closure.py select --diff 8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f` at 17e27ef51 prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f ./tests/run.sh`: `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, rc 0, with `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 8b49d50b0...` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- Mutation table, CI's command at 17e27ef51: `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3`: `3091 unpinned site(s) of 6799 candidate sites, 3093 at the ratchet base 8b49d50b0...`, no refusal, and `MUTATION TABLE PASSED`, rc 0; its ten sampled mutants were each killed, among them four this pass pinned (`optimizer.py:4772 CLAMP_DROP`, `optimizer.py:5552 CMP_BOUND`, `store.py:831 BOOLOP`, `store.py:833 RETURN_DEL` by the driver its row names). At 6790e0966 against 7af0c2a79 the same table refused 3099 against 3093 with 8 added.
- `python3 tools/audit/archscore/score.py --diff 8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc` at ca0d33c12: `Architecture score: dS +0.0000 NULL`.
- Claim files: `git diff --quiet origin/main HEAD -- tests/golden/card_claimed_drift.txt` exits 0. `tests/golden/claimed_drift.txt` differs from origin/main only in this PR's nine `R10-HOTFIX-SAV-ESTIMATE` claims, their suspended may-drift entries and their comment block; this pass does not touch it. `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to origin/main.
- `bash tools/pr/prepr.sh` with this body, at this head against 2dc960f4a, body check included: clean (`PRE-PR ... rc=0`). It also read clean at 17e27ef51 against 8b49d50b0, before the last merge of main.

## Architecture score

`Architecture score: dS +0.0000 NULL` against 8bf45e5dc, at ca0d33c12 (this pass adds no production line). No budget rises.

## Unpinned sites

The eight sites the diff adds, each with its disposition (`## Mutation proof`): six pinned by this pass's `--pin-killed` under `tests/mutation_ledger/killed_by/` (`store.py:831 BOOLOP`, `store.py:833 RETURN_DEL`, `ledger.py:75 CONST`, `optimizer.py:595 CMP_BOUND`, `optimizer.py:5552 CMP_BOUND`, `optimizer.py:4772 CLAMP_DROP`), two triaged `equivalent` under `tests/mutation_ledger/survivor_triage/optimizer.py/` (`optimizer.py:5541 BOOLOP`, `optimizer.py:536 CONST`).

## Red checks

The final head has run no CI; this handoff moves the PR to it. Concluded reds on the PR head 6790e0966, read from the check-run listing (69 runs, one page of 100), each cause read from its job log:

- `tests / mutation` (run 42024722714): `MUTATION TABLE REFUSED -- 3099 unpinned site(s) against 3093 ... 8 of them added by this diff`. Answered by this pass: at 17e27ef51 the table reads 3091 against 3093 with none added and passes (`## Figures`).
- `tests / mutation-autofix` (run 42024722714): `skip-nothing-killed`, its drive killed none of the eight. Answered by this pass's checks and `--pin-killed` (`ci-autofix.md`: a red autofix job means no bot commit comes). The cheaper detector is `prepr.sh` step 6d, which listed the eight before the round-3 handoff; round 3 gave them to the bot instead of triaging them, which is the miss.
- `gate` (three runs, the latest 42025404620): `FAIL tests / mutation: failure (run 42024722714)`, the grader reading the red above.
- `tests / replay` (run 42024722714, job 127236492371): **not** the runner-class band refusal. `1 of 194 replay checks FAILED`: `FAIL owner-2026-10-30-away.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1238: budget 0.249 cannot see a 2x cycle; re-record 0.1751]`. The runner measured the owner fixture's event-loop CPU ratio at under half its budget, so the budget could not see a doubled cycle. The diff does touch what replay runs (it drives the real coordinator, and this PR changes `optimizer.py`, `ledger.py` and `store.py`), so I do not call it inherited. Against that: origin/main 8bf45e5dc's push run 42038071453 reads `tests / replay` green, no replay file changed between 7af0c2a79 (the run's base) and 8bf45e5dc, and the offender is the loop-thread ratio, while this PR's solve runs off the loop. It is a timing measurement on one runner; this pass changes no production line, and the new head's run is the measurement that decides it. Its owner, if it recurs on that head, is R10-REPLAY-COST-BUDGET.
- `governance / delivery-status` (run 42024722714): inherited. Its log lists `pending` and `overdue` rows of other PRs (#3205, #3216, #3193 and on), and states it blocks no merge; this diff's only delivery file is its own row.
- `tests / fast (3.14)`: green on 6790e0966 (run 42024722714). `prepr.sh`'s body check names it as a red of this branch's history: the round-2 record has it red on run 41964618801 at the merge ref c3992a14, the R9-F2.1 P3 pin's continuation gain reading zero on one OpenBLAS kernel class, repaired by that round's re-pin 539995fa5. Not re-measured in this pass. Its cheaper detector, a per-`OPENBLAS_CORETYPE` scan of that pin, does not stand; the round-2 record found no standing one cheaper than the CI lane itself.
- `tests / typing`: green on 6790e0966. Named because the branch's history has it red at the round-1 head 481153bd6 (`errors did not grow [recorded 0, measured 2 (+2)]`, both `type-arg`, on `LedgerStore` subclassing the generic store unparameterised), repaired by e76b0d7dc. Re-measured in this pass: `tests/typing_ruler.py --mypy` at this pass's tree reads `ALL 9 typing-ruler checks PASSED` (`## Figures`). Its cheaper detector is that ruler run locally, which already stands.
- `pr-contract / pr-contract`: green on 6790e0966. Named because the branch's history has it red at 481153bd6, reading the round-1 body's unnamed reds; this body is its input again, and `tools/pr/prepr.sh`'s body check is the standing cheaper detector, run here.
- `tests / nightly-status` (run 42024722714): inherited. `NIGHTLY FAILED: slow failed last night`, scheduled run 41943946464 at head 499162c on main; outside this diff.

## Forward-carry

- Open finding, unchanged: `_apportion_by_steady_demand` has no pump cap. This pass measured it: on a 3 kW pump, a -25 C night and 400 W/m2 midday sun the spread reference peaks at 1.226x the pump. The solve's seed is clamped (now pinned), but the booked reference itself can ask a step the pump cannot deliver. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`).
- Open finding, unchanged: the harness's unattributed residual (-3.90 % flat, -8.02 % varying). Carry: R10-SAV-COMFORT (same roster).

## Friction

none
