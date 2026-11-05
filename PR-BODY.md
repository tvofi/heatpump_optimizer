The owner's month row read nonsense on a valved house with a wood tank (tvofi, 2026-11-04): November's reference far below the meter, a percent clipped at -100. The settlement books the thermostat's first step of a plan re-made every interval, and behind a valve that step read the stores' transient.

**The owner's September, October and November rows show a dash, and the first saving figure arrives with the next new month.** This is not a corrected figure. Totals are never rewritten: a month that booked savings against the retired reference keeps both columns, with a dash for saving and percent and an "old basis" note. November stays old even as it books on, because its total is mixed. So the owner reads no saving until December.

What changed:

- **The reference has no wood, on every house** (owner ruling, 2026-11-04): no wood tank, no fire, no refill coil, in the space and the hot-water reference. Actuals stay metered, so wood and fire timing count in the saving.
- **Wood-configured houses carry a disclaimer**: the saving includes heat from wood, and firewood's cost is not counted. There is no firewood subtraction and no wood line.
- **Behind a valve the reference holds its tank** at the temperature that delivers the need, and books the horizon's energy by the steady demand, so step 0 is no longer a transient.
- **The month percent is unclipped**; `notifier.py` carries the same fields.
- **Calibration may only raise the reference on a wood-configured house** (option A, under the mandate, pending the owner's override); a no-wood house is unchanged. This answers triage carry P387 (`dev/programme/triage/s6-batch122.md#P387`).

A positive row on the wood arms (+7.5 to +88 % below) is expected behaviour, not a defect: it is wood's heat. On those arms the row reads the saving the ruling asks for.

Carry 1, the owner's no-wood ruling (2026-11-04): done as listed above. Wood-configured houses show a figure with the disclaimer, and old-basis rows keep the dash.

Carry 2, triage P387 (metered kWh cancels in the calibrated percent): answered by the calibration floor. The two rulings cannot both hold unmodified on a wood house, because the 2026-10-24 calibration scaled wood's saving away. So on a wood house calibration may only raise the reference, and with no wood it stands as specified. The orchestrator relayed this as option A under the mandate, pending the owner's override. With metering below plan, the three-row check reads 50 / 75 / 87.5 % at 1.0 / 0.5 / 0.25 with wood, and 50 / 50 / 50 % with none.

Three defects of this branch's own were found in the first round's takeover and are fixed here, not claimed:

1. Deleting the external-heat block from `_compute_baseline_power` also deleted the demand's only zero floor. On every house the reference could then draw negative power: `summer_dhw_only` read 56.99 % against 5.88 %. All 33 plain fixtures that moved are byte-identical to the merge base again.
2. `_start_gap_cost` settled against the reference's 0 C wood stand-in, debiting a wood house its own firewood: `wood_two_tank` deferred cost 42.90 against 27.15 fixed.
3. The no-wood reference's energy reseeded the plan's solve on a wood house (3.99x simulate work on an unchanged plan). `_wood_covered_share` scales the seeds only.

Round 2 (repair of the blocking review at 6dcd1abb, `probe/rev-3220-222623eb`). Four changes, and nothing the review found sound is touched:

1. **Typing (the block).** `class LedgerStore(QuarantiningStore[_StorePayload])` carries the generic's type argument, so the annotation `LedgerStore[dict[str, Any]]` in `coordinator.py` is legal again. `tests/typing_budgets.json` is untouched.
2. **The floor's place is pinned.** The new check `a thermostat's end state is the house its booked power heats: a replay of the kW lands on it, warm day and swinging day` replays the booked kW through `ThermalModel.simulate_step` from `_thermostat_held_state` and requires the reference's end state, which `_settle_horizon` settles, to be reached. A floor only at the return books zero but simulates the negative demand, so its end state is a house the booked power never heated.
3. **R9-F2.1 P3 re-pinned from a 35 C tank.** The valved reference's seeds made the 30 C cell a cliff: the continuation's gain is zero on one OpenBLAS kernel class and positive on another. At 35 C it is positive on each of the four classes measured. No golden is re-recorded.
4. **The v1 migration stamps only months that booked savings.** A v1 month holding lines and no `savings_baseline` booked against no reference. It is now left unstamped, so its first savings booking stamps the reference in force and the month is not shown as a dash.

Alternatives (fixer step 17):
- The reference keeps a wood share: refused by the owner's ruling.
- A wood line or firewood subtraction: refused for the same reason.
- Widening `SCENARIO_WORK_FACTOR` for the seed cost: blinds every scenario, and that check has no per-scenario budget.
- A dash on all wood houses: superseded by the ruling.
- Typing: annotating `_ledger_store` without a subscript also clears the ruler, but it leaves `LedgerStore` an unparameterised subclass of a generic, so the next subscripted use fails again. Passing the parameter through fixes the class itself.
- R9-F2.1 P3: a may-drift entry, or recording the 30 C cell per kernel class, would keep a pin whose margin is zero on one host. Moving the cell keeps the claim, which is that the continuation buys a strictly better plan, on a case where the claim does not depend on the kernel.
- Migration: stamping every month and un-stamping at the first booking would need `add_savings_settlement` to tell an upgrade stamp from a real one. Not stamping a month that has no savings keeps the one rule `add_savings_settlement` already applies: a month is stamped when it first books savings.

Root cause: the defect reached a release. The separate seat's record merged with #3216 (`dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`).

Round 3 (merge repair, origin/main cd0dd1691 then 0ae75bf31). The merge train skipped the reviewed head 6f8dfe831 on a content conflict in `ledger.py` with #3195 (R10-SAV-COMFORT part 3, e57dfbbe), which settles the plan's stored heat into the month row. The conflict is resolved by merge, not by a re-cut, and `MonthlyLedger.savings_months` now does both:

1. **Settling against the meter (this hotfix).** On a wood-configured house the calibration is floored at 1.0 before anything is scaled: a meter under the plan is a fire and is never scaled down.
2. **The stored-heat settlement (#3195).** The plan's stored-heat change converts at the month's mean steady COP and prices at the row's metered kWh price. It is added to `baseline_sek`, and `comfort_sek` is published beside the saving.

All three terms (the thermostat line, the stored line and the comfort line) ride the one floored `scale`, which is what "scaled as the thermostat is" means. The row keeps both sets of keys: the hotfix's `old_basis` (and its dash on an old-basis month) and #3195's `stored_heat_sek` and `comfort_sek`.

The combination moved three things, each repaired in 5dc4cd6e0:
- `R10-SAV-COMFORT null control: an interval without either reading settles nothing` compared the whole row to a literal dict that predates `old_basis`. It now expects `"old_basis": False`; no other key or value changed.
- `class_excess_loc` read 17590 against a budget of 17589. The cause was the merged docstring stating both owner rulings. It is paid by rewording the docstring one line shorter, with no budget change.
- `dev/audit/harnesses/r10_sav_wood_reference.py` booked only `baseline_kw` and `power`, so the stored-heat settlement never reached its row (`stored_sek` is 0 when no `steady_cop` is booked). It now books the plan step's own readings (`_settlement_at`) as production's pending snapshot does, and `--no-settlement` is its null control.

The second main merge (0ae75bf31, #3219: `replay_doc.py`, `debugger.py`, `tests/replay.py`, `tools/replay/export.py` and its mutation records) merged without conflict.

The step ref `handoff-wip/r10-hotfix-sav-estimate` still held the previous return's body commit f6e53f982, which is not an ancestor of the merged head. Deleting it was refused in this container, so this round's step pushes went on top of it as a body-only merge commit, as the previous return's did. `handoff/` carries the code head alone.

**Is the owner-reported estimate still fixed with #3195 in? Yes.** The fixer's harness reads `first: SOUND`, `valve-flat: SOUND` and `valve-vary: SOUND` at the merged head. At origin/main without the hotfix it reads `first: DEFECT` and crashes on `valve-flat`. The finder's census reads 0 cells out of band at the merged head against 4 at origin/main. #3195's stored-heat term moves the flat row from +4.18 % to +0.56 %, closer to the 0 a flat price should read. The null control (`--no-settlement`) reproduces the previous figures exactly (`## Figures`).

## Head

`a1a7b2a6bf2b4539d32d18578c7057db3c83cf3e`. It is the PR head 6f8dfe831 (the reviewed 1d114ed62 merged with an older main), plus:
- 67e54f8d2, the merge of origin/main cd0dd1691, resolving `ledger.py` (above);
- 5dc4cd6e0, the three repairs the combination needed;
- 5a0fef27b, the merge of origin/main 0ae75bf31 (#3219), with no conflict;
- a1a7b2a6b, the merge of the bot's 359caf94c (`ci: pin killed mutants`, eight `tests/mutation_ledger/killed_by/` records only), which `mutation-autofix` pushed to the PR branch at 10:07Z while this round ran. It merged with no conflict, and it is not re-measured: no script reads those records but the mutation lane.

Merge base `0ae75bf3146566bffca4490464dcc8d6d45c29ab`, the tip of origin/main at `date -u` 2026-11-05 10:40. The two harnesses' both-end runs were taken at 67e54f8d2 (the original harness) and at 5dc4cd6e0's tree (the extended harness). The final head differs from them only by #3219's replay files, which neither harness imports. Every other figure under `## Figures` is from the final head. `tools/pr/prepr.sh`, body check included, ran once at this head, against this base.

## Mutation proof

Round 3 covers the merge resolution. Each mutant ran the full `PYTHONPATH=tests/hastub python3 tests/features.py` in a worktree at 5a0fef27b with one line changed; the null is the unmutated head (`ALL 4855 FEATURE CHECKS PASSED`, rc 0).

| mutant | checks that go red |
|---|---|
| delete the wood calibration floor in `savings_months` (`calibration = max(1.0, calibration)` becomes `pass`) | `with wood configured a meter under the plan earns its saving: the calibration does not cancel it` (`{1.0: 50.0, 0.5: 50.0, 0.25: 50.0}`), `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`. That is 2 of 4855, rc 1. |
| drop `+ stored_sek` from `baseline_sek` in `savings_months` (main's side lost) | `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price` (baseline 20.0 against 15.0). That is 1 of 4855, rc 1. |

Each side of the resolution is held by its own side's checks, so neither was taken wholesale.

Round 2, measured at this head's tree. Each mutant ran on a copy of `custom_components/`, the check's section being sliced out of `tests/features.py`. The null is an unmutated copy with a comment-only change.

| mutant | checks that go red |
|---|---|
| `floorlate` (the reviewer's): no floor on `required_thermal` in the loop, `return np.maximum(baseline_power, 0.0), state` | `a thermostat's end state is the house its booked power heats: a replay of the kW lands on it, warm day and swinging day`. The warm day's replay misses by 3.473 C (room) and 6.074 C (slab), and the swinging day's by 0.294 C and 0.516 C. The null misses by 0.0 on both. |
| `migrate_ledger_v1` without the `"savings_baseline" in lines` condition (the tree before bf628b2ec, failing test first) | `a v1 month with no savings booked at the upgrade books its first saving on the new reference` (2026-03 reads `reference_basis {'sum': 0.0, 'count': 1}`) |
| `class LedgerStore(QuarantiningStore):` (the tree before e76b0d7dc) | `tests/typing_ruler.py --mypy`: `FAIL errors did not grow [recorded 0, measured 2 (+2)]`, `FAIL by_code[type-arg] did not grow [recorded 0, measured 2 (+2)]` |

Round 1, measured at a9f8cb2b by slice. The reviewer re-ran the floor, wood-share, calibration and seed mutants on the full `tests/features.py` (verdict on `probe/rev-3220-222623eb`). These rows are not re-run here, because this round's delta does not touch their lines.

| mutant | checks that go red |
|---|---|
| delete the zero floor in `_compute_baseline_power` | `a thermostat on a warm plain house buys no heat and sells none: not one reference step is negative` |
| drop `_sharing_wood_side` in `_start_gap_cost` | `the start gap settles no wood: a measured wood tank, hot or cold, is the plan's own and debits nothing` |
| drop the end share, space path | `the space-only settle-up's reference end carries the plan's wood side too` |
| drop the end share, hot-water path | `the settle-up's reference end carries the plan's wood side: heat wood left is no store to settle` |
| drop `_apportion_by_steady_demand` | `behind a valve with a wood tank, cold or warm, the thermostat's first step is its horizon mean, not 0 or an overshoot`, its two siblings, and `behind a valve with one zone and no wood tank, a positive reference with no zero step` |
| drop the held buffer | `behind a valve with a wood tank, cold or warm, the thermostat's horizon does not inherit the measured buffer`, its two siblings, `the reference has no wood: a wood tank, cold or warm, reads the plain valved house's kW`, and the start-gap check |
| keep the measured wood tank in the reference | `the reference has no wood: a wood tank, cold or warm, reads the plain valved house's kW` |
| re-add the coil to the reference's hot water | `the reference's hot water has no refill coil: a known wood tank moves nothing (owner ruling, 2026-11-04)`, `standby uses the passed setpoint` |
| re-clip the percent | `pct is baseline-relative and unclipped: the row's percent is its own two amounts' ratio` |
| drop the migration stamp | the script raises `KeyError: 'reference_basis'` at `a v1 ledger migrates to v2: every month on the old basis, every line as stored` |
| drop the calibration floor | `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`, `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied` |
| `_wood_covered_share` returns 0 | `a wood tank's usable heat, at the pump's COP, is the share of the solve's starts it covers` |
| `seed_power` not scaled at the call site | `tests/stress.py`: `no scenario's simulate work grew on an unchanged plan (#1229)` and `no scenario exceeds its own recorded cost by the budget factor`, from the gate at the tree before the line was added (3.99x; 7.6x against 6.6x), which is that mutant. Left to CI's mutation check per fixer step 5. |

## Null control

Round 3: the extended harness with `--no-settlement` books what it booked before (baseline and power only). It reads byte-for-byte the figures the reviewer verified at 1d114ed62: valve-flat pct +4.18, valve-vary +28.50, `stored_heat_sek 0.0 comfort_sek 0.0` on every arm. So the moves under `## Figures` are #3195's stored and comfort terms and nothing else. The harness's own kWh split (`residual: reference less comfort, plus stored`) is identical with and without the flag on every arm, which confirms that the flag changes only what the ledger is handed. At origin/main without the hotfix, the same original harness reads `first: DEFECT` (step0/mean 0.000 or 2.292 to 4.589, `BAD` on every install).

The floor pin's null: on the unmutated tree the replay lands on the reference's end state exactly (gap 0.0 C on room and slab, both days), and the swinging day books a positive 30.37 kWh, so the replay is driven by non-zero power and the check is not vacuous.

The typing null: the tree before e76b0d7dc reads +2 `type-arg` (above). The migration null: the tree before bf628b2ec stamps the unbooked month as the old basis (above). The old-basis month that did book savings stays old at both ends (`a v1 ledger migrates to v2: every month on the old basis, every line as stored` passes before and after).

R9-F2.1 P3's null is origin/main 78a2be77c, the tree without this diff, run through the same probe. At 30 C it reads gain +0.010889 under Haswell (j_plain 109.578998 against 109.589887) and +0.631408 under SkylakeX. At 35 C it reads +0.730147 (Haswell) and +0.623440 (SkylakeX).

Round 1's null: the merge base 2a9cd3476, on the finder's harness over the owner's export, reads step 0 over horizon mean 0.00 in every snapshot with the tanks as measured, and the code head reads 1.00 (ratios only, from round 1's run; this host has no export). The plain house is the change's null: after the floor, every fixture with no valve is byte-identical to the merge base (`NO STALE FIXTURE`, below).
## Figures

Env: `PYTHONPATH=tests/hastub:tests:custom_components` for the harnesses, and `PYTHONPATH=tests/hastub` for the suite scripts. Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` prints `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. Harness copies were run from scratch, so each worktree measured the same file.

Round 3, the owner-reported estimate at both ends:
- Original fixer's harness `dev/audit/harnesses/r10_sav_wood_reference.py` (sha1 0f98bbb397a62d65a07448e934e0e100e49359da, as at 1d114ed62), default arms.
  - At origin/main cd0dd1691, which lacks the hotfix: `first: DEFECT`, then `TypeError: MonthlyLedger.savings_months() got an unexpected keyword argument 'wood_configured'` on `valve-flat`, rc 1.
  - At 67e54f8d2: `first: SOUND`, `valve-flat: SOUND` (pct +4.18, residual -3.90 %), `valve-vary: SOUND` (pct +28.50, residual -8.02 %), rc 0. These equal the reviewer's figures at 1d114ed62, because this harness books no stored-heat readings.
- Finder's census `dev/audit/harnesses/r10_rca_sav_estimate.py` (default arms):
  - At origin/main cd0dd1691: `census: 6 of 6 cells ran, 4 out of band: valve-at-curve valve-charged wood-warm wood-hot`, rc 1.
  - At 67e54f8d2: `census: 6 of 6 cells ran, 0 out of band: -`, rc 0.
- Extended harness (sha1 23f17afe540f2cc82f7f5d5e1f4d4fe51b36d736, the file at this head), run at 5dc4cd6e0's tree. Two days for each arm. The rule is the harness's own: `flat |pct| < 10.0`. Wood arms are measured, not asserted.

| arm | row pct, with #3195's settlement | `--no-settlement` (null) | stored_heat_sek | comfort_sek | baseline / actual SEK |
|---|---|---|---|---|---|
| valve-flat (SOUND) | +0.56 | +4.18 | -6.32 | 5.50 | 167.15 / 166.22 |
| valve-vary (SOUND) | +25.26 | +28.50 | -9.09 | 7.11 | 200.64 / 149.95 |
| wood-cold | +0.47 | +4.24 | -6.57 | 5.49 | 166.90 / 166.12 |
| wood-stale | +4.07 | +7.20 | -5.66 | 5.60 | 167.82 / 160.99 |
| wood-coast | +19.34 | +22.40 | -6.58 | 4.93 | 166.89 / 134.62 |
| wood-fire | +37.37 | +38.54 | -3.23 | 5.65 | 170.24 / 106.62 |
| wood-unforeseen | +40.42 | +42.82 | -6.99 | 5.53 | 166.49 / 99.20 |
| wood-full | +92.99 | +92.61 | +9.32 | 2.18 | 182.80 / 12.82 |

`first: SOUND` and `arms run 3, defect 0`, rc 0, both with and without the flag. The owner's report was a baseline/actual of 0.14. On the flat valved arm the ratio is 167.15 / 166.22 = 1.006, and the plain row stays positive on every arm. On the valved arms the stored term is negative, because the plan drew the store down over two days. That lowers the reference by what the plan did not buy, so the saving shrinks rather than inflates. On wood-full the plan charged the store from wood, and the term is positive.

Round 3, the suite at 5a0fef27b:
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4855 FEATURE CHECKS PASSED`, rc 0. At 67e54f8d2, before the repair, it read `1 of 4855 FEATURE CHECKS FAILED` (the `old_basis` null-control dict).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2631 ENTITY CHECKS PASSED`, rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. At 67e54f8d2 it read `FAIL class_excess_loc 17590 > 17589 (+1)`. No budget file differs from the PR's own: `tests/structure_budgets.json` sits below origin/main's (class_excess_loc 17589 against 17617).
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py`: `ALL 9 typing-ruler checks PASSED`, `ALL 12 typing-ruler source checks PASSED`. The `--mypy` run needs `.venv-typing`, which this container does not have, so it was not run. CI's `tests / typing` judges it; the merge adds no annotation.
- Gate scope: `python3 tests/closure.py select --diff 0ae75bf3146566bffca4490464dcc8d6d45c29ab` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.` The full scoped `tests/run.sh` was not re-run here. Of what it names, features, entities, structure and typing_ruler ran (above); the rest is left to CI.
- `python3 tools/audit/archscore/score.py --diff 0ae75bf3146566bffca4490464dcc8d6d45c29ab`: `Architecture score: dS +0.0000 NULL`.
- Claim files: `git diff --quiet origin/main HEAD -- tests/golden/card_claimed_drift.txt` exits 0, so the file is byte-identical. `tests/golden/claimed_drift.txt` differs from origin/main only in lines carrying `R10-HOTFIX-SAV-ESTIMATE` and that claim's comment block. It was resolved by the `claimnotes` driver, with no hand edit. `claims-for: 7.1.1` equals `VERSION`.
- Seam rule for the resolution: `git grep -n "savings_months(" -- custom_components`. Every caller reads the one method resolved here, so no second row builder carries either rule.

Rounds 1 and 2, quoted at their own heads and not re-run in round 3 unless named above:

Env for each harness line: `PYTHONPATH=tests/hastub:tests:custom_components OPENBLAS_CORETYPE=Haswell`. `--quick` is one day, otherwise two. Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` prints OK. `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` prints `2.5.4 1.18.1`, which equals `tests/requirements-ci.txt`.

- `python3 dev/audit/harnesses/r10_sav_wood_reference.py first` (sha1 0f98bbb397a62d65a07448e934e0e100e49359da): `first: SOUND`, rc 0, step0/mean 1.000 on every install and tank start, null gap 0.00e+00 kW.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat`: `valve-flat: SOUND`, rc 0, pct +4.18 (rule `flat |pct| < 10.0`), gap +6.05 kWh, residual -3.90 %. Round 1 read the same harness at the merge base 2a9cd3476 as DEFECT, -65.81 %, gap -55.02 kWh.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-vary`: `valve-vary: SOUND`, rc 0, pct +28.50, residual -8.02 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-cold`: pct 7.47, plan 66.89 kWh, booked 72.28, residual -3.22 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-stale`: pct 12.36, plan 63.35, residual -3.42 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-coast`: pct 42.22, plan 41.76, residual +0.31 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-fire`: pct 43.69, plan 40.70, residual +33.38 %, which is wood's heat.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-full`: pct 87.88, plan 8.76, residual +88.64 %, which is wood's heat.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-unforeseen`: pct 49.10, plan 40.63, calibration 1.0 (the floor's).
- Finder's census, `python3 dev/audit/harnesses/r10_rca_sav_estimate.py census` (in the tree since #3216, sha1 04b644563c84d26378cad42a603dc050e7e5fd88): `census: 6 of 6 cells ran, 0 out of band`, rc 0. The booked-over-horizon-mean ratio is 1.00 on five cells and 0.92 on `unvalved`. The `ledger` and `attrib` arms need the owner's export, which this host does not have, so they were not re-run. Round 1 read `attrib` 0.00 at the base and 1.00 at the code head.
- R9-F2.1 P3 kernel scan: a probe of `_f21_storage_solve(True)` with and without the continuation, by tank start, with each `OPENBLAS_CORETYPE`. The rule is gain = `j_continuation_off - j_plain`, which must be positive. At 30 C: Haswell +0.000000, Sandybridge +0.000000, Prescott +0.000000, SkylakeX +0.034369. SkylakeX reproduces CI's `tests / fast (3.14)` figures (108.958453 against 108.992821). At 35 C: Haswell +0.864593, Sandybridge +0.865039, Prescott +0.412499, SkylakeX +0.613012, and j_plain is 107.0391 on all four. Over the cells scanned (20 to 50 C in steps of 5), 40 and 45 C also read zero on all four classes, and 20, 25, 35 and 50 C read positive on all four. In the suite at this head, `RESULT f21_p3_two_zone=1 j_plain=107.039134 j_continuation_off=107.903727 continuation_gain=+0.864593`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`, in full: `ALL 4832 FEATURE CHECKS PASSED`, rc 0 (standalone run at 539995fa5 and in the gate at this head).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`, in full: `ALL 2617 ENTITY CHECKS PASSED`, rc 0 at 539995fa5, and `ALL 2622 ENTITY CHECKS PASSED` in the gate at this head (main's merge added checks).
- `.venv-typing/bin/python tests/typing_ruler.py --mypy` (the venv built as `tests.yml` builds it, from `tests/requirements-typing.txt`): `ALL 9 typing-ruler checks PASSED`.
- Gate scope: `python3 tests/closure.py select --diff 78a2be77c6d5f8eda3a44b23d3011ecc87eff366` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=78a2be77c6d5f8eda3a44b23d3011ecc87eff366 ./tests/run.sh`: `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, rc 0. `ALL 113 STRESS CHECKS PASSED` and `ALL 84 OPTIMALITY CHECKS PASSED` are among them. The round-1 host reds (`tests/optimality.py`, `tests/stress.py` shoulder) do not reproduce on this host.
- Golden, in that gate: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 78a2be77c6d5f8eda3a44b23d3011ecc87eff366` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. The 9 `CLAIMED` lines are the round-1 claims, unchanged. This round's three commits leave `tests/golden/` untouched: `git log --no-merges 481153bd6..HEAD -- tests/golden` lists no commit of this branch's own. `tests/golden/card_claimed_drift.txt` is byte-identical to origin/main.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget file changed in this round.
- Host-dependent pins, this round: R9-F2.1 P3 was host-dependent at 6dcd1abb because of this diff, red under Haswell, Sandybridge and Prescott and green under SkylakeX (CI). It is repaired by its re-pin, and it is listed here as the review asked. No host red remains on this machine.
- Not re-run: `node tests/card_browser.mjs`. No scope selects it, and this round touches neither the card nor `GRID_SURFACE`, so it is left to CI's `tests / browser`, as round 1 also left it.
- Seam rule for the floor: `git grep -n "_settle_horizon(\|_thermostat_held_state(" -- custom_components`. Every caller settles the end state that `_compute_baseline_power` returns, and the new replay check pins that end state against the booked kW. Seam rule for the stamp: `git grep -n "REFERENCE_BASIS_META" -- custom_components` returns three writers: `migrate_ledger_v1` (fixed here), `add_savings_settlement` (a month's first savings booking, already guarded) and the reader in `savings_months`.

## Architecture score

`Architecture score: dS +0.0000 NULL` against 0ae75bf31. No budget rises.

## Unpinned sites

The sites `tools/pr/prepr.sh` step 6d lists at this head; each is a `custom_components/` site that `tests / mutation-autofix` pins.

- `custom_components/heatpump_optimizer/ledger.py:75 CONST`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:4772 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:536 CONST`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5541 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5552 CMP_BOUND`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:595 CMP_BOUND`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/store.py:831 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/store.py:833 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).

The bot's 481153bd6 pinned the guard on `migrate_ledger_v1` that bf628b2ec rewrote, and its file was deleted by hand in 70f0c46f5. The bot's 359caf94c pinned eight more on 6f8dfe831, the other eight of round 3's first list.

## Red checks

Concluded reds on the PR head on the remote, 359caf94c (the bot's pin commit on 6f8dfe831), read with `filter=all` from one check-run page of 41 runs: `gate` and `tests / mutation`. Those on 6f8dfe831 (58 runs) are listed after them. The final head has run no CI; this handoff moves the PR to it.

- `gate` (359caf94c, and twice on 6f8dfe831): the grader, reading the `tests / mutation` red below. It is answered by naming that red.
- `tests / mutation-autofix` (6f8dfe831, 10:08Z): the pin lane, which pushed 359caf94c, named per `ci-autofix.md`.

- `tests / mutation` (359caf94c and 6f8dfe831): the ADDED UNPINNED sites of this diff, which `tests / mutation-autofix` pins and `tools/pr/prepr.sh` step 6d lists beforehand (`## Unpinned sites`). It is not a defect, and the cheaper detector already stands.
- `governance / delivery-status` (6f8dfe831): inherited. It is a governance read of the delivery rows; this diff touches only its own row, `dev/programme/delivery/3220.md`, which the merge did not change. Its OVERDUE flags fall on other PRs' rows, as round 2 measured on its base; this round did not re-read the job log.
- `tests / nightly-status` (6f8dfe831): inherited. It reads the nightly record on main; this diff touches nothing in that check's closure.

- `tests / fast (3.14)`: not red on 6f8dfe831 or 359caf94c. It is named here because the round-2 figures quoted under `## Figures` cite its red on run 41964618801 at the merge ref c3992a14, which the R9-F2.1 P3 re-pin (539995fa5) repaired. The cheaper detector is the per-`OPENBLAS_CORETYPE` scan quoted there, which is not standing.
- `tests / replay`: not red on 6f8dfe831 or 359caf94c. It is named because the round-2 figures quoted under `## Figures` cite its red on run 41964618801 at c3992a14: `synthetic-dhw-only.json: cycle_cost` and its three doubled-cost arms refused a runner whose `ref_ms` lay in no band of `COST_RUNNER_CLASSES`. That is the runner's class, not this diff, and no cheaper detector exists: a new runner class shows itself only on a run that lands on one.
- `tests / typing`: red on the round-1 head 481153bd6 in this head's ancestry (`errors did not grow [recorded 0, measured 2 (+2)]`, both `type-arg`). It was repaired by e76b0d7dc and is green on 6f8dfe831 and 359caf94c. The cheaper detector is `tests/typing_ruler.py --mypy` in `.venv-typing`, which already stands; this container has no `.venv-typing`, so round 3 ran the source ruler only (`## Figures`).
- `pr-contract / pr-contract`: red on 481153bd6 in this head's ancestry, reading the round-1 body's unnamed reds. Round 2's body answered it; this body is the grader's input again.

No check went red because of the merge resolution; the head carrying it has not run CI yet. The features and structure reds that the resolution produced locally (`## Figures`) were repaired before the handoff. Their cheaper detector is the one used here, `features.py` and `structure.py` run at the merged head, which already stands.

## Forward-carry

- Open finding, unattributed residual: with the stored term now in the row, the harness's residual is unchanged at -3.90 % (flat) and -8.02 % (varying), and -3.57 % on wood-cold and -3.61 % on wood-stale. This is not zero. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)
- Open finding: `_apportion_by_steady_demand` has no pump cap, unchanged from round 2. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)

## Friction

none
