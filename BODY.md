The owner's month row read nonsense on a valved house with a wood tank (tvofi, 2026-11-04): November's reference far below the meter, a percent clipped at -100. The settlement books the thermostat's first step of a plan re-made every interval, and behind a valve that step read the stores' transient.

**The owner's September, October and November rows show a dash, and the first saving figure arrives with the next new month.** This is not a corrected figure. Totals are never rewritten: a month booked against the retired reference keeps both columns, with a dash for saving and percent and an "old basis" note. November stays old even as it books on, because its total is mixed. So the owner reads no saving until December.

What changed:

- **The reference has no wood, on every house** (owner ruling, 2026-11-04): no wood tank, no fire, no refill coil, in the space and the hot-water reference. Actuals stay metered, so wood and fire timing count in the saving.
- **Wood-configured houses carry a disclaimer**: the saving includes heat from wood, and firewood's cost is not counted. There is no firewood subtraction and no wood line.
- **Behind a valve the reference holds its tank** at the temperature that delivers the need, and books the horizon's energy by the steady demand, so step 0 is no longer a transient.
- **The month percent is unclipped**; `notifier.py` carries the same fields.
- **Calibration may only raise the reference on a wood-configured house** (option A, under the mandate, pending the owner's override); a no-wood house is unchanged. This answers triage carry P387 (`dev/programme/triage/s6-batch122.md#P387`).

A positive row on the wood arms (+7.5 to +87 % below) is expected behaviour, not a defect: it is wood's heat. On those arms the row reads the saving the ruling asks for.

Carry 1, the owner's no-wood ruling (2026-11-04): done as listed above. Wood-configured houses show a figure with the disclaimer, and old-basis rows keep the dash.

Carry 2, triage P387 (metered kWh cancels in the calibrated percent): answered by the calibration floor. The two rulings cannot both hold unmodified on a wood house, because the 2026-10-24 calibration scaled wood's saving away. So calibration stays on a wood house only to raise the reference, and stands as specified with no wood. The orchestrator relayed this as option A under the mandate, pending the owner's override. The result, metered below plan: the three-row check reads 50 / 75 / 87.5 % at 1.0 / 0.5 / 0.25 with wood, and 50 / 50 / 50 % with none. The closed-loop arm `wood-unforeseen` meters about 0.90 of plan and reads +47.81 %, printed calibration 1.0 being the floor's.

Three defects of this branch's own were found in the takeover and are fixed here, not claimed:

1. Deleting the external-heat block from `_compute_baseline_power` also deleted the demand's only zero floor. On every house the reference could then draw negative power: `summer_dhw_only` read 56.99 % against 5.88 %. All 33 plain fixtures that moved are byte-identical to the merge base again.
2. `_start_gap_cost` settled against the reference's 0 C wood stand-in, debiting a wood house its own firewood: `wood_two_tank` deferred cost 42.90 against 27.15 fixed.
3. The no-wood reference's energy reseeded the plan's solve on a wood house (3.99x simulate work on an unchanged plan). `_wood_covered_share` scales the seeds only.

Alternatives (fixer step 17):
- The reference keeps a wood share: refused by the owner's ruling.
- A wood line or firewood subtraction: same.
- Widening `SCENARIO_WORK_FACTOR` for the seed cost: blinds every scenario, and that check has no per-scenario budget.
- A dash on all wood houses: superseded by the ruling.

Root cause: reached a release; the separate seat runs at `handoff/r10-rca-sav-estimate` d8eeae8f.

## Head

`a9f8cb2b507bebeb2ab1c0c17b3a10d39977df52`, cut from merge base `2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e`, one commit. Every figure below was measured at this head except where a line names another. `git merge-tree --write-tree origin/main HEAD` reports no conflict at origin/main 499162c89 (`date -u` 2026-11-05 00:57).

Overlap: `git merge-tree --write-tree HEAD c383169a50b6b9668a0e88d829bfc3127f4b3c73` (#3195) conflicts in `custom_components/heatpump_optimizer/ledger.py` only; whichever lands second merges.

## Mutation proof

Each mutant ran on a `git archive` copy of this head, through the named checks of `tests/features.py`, slicing the sections that own them. The control column is the unmutated slice: no FAIL in either slice.

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
| `seed_power` not scaled at the call site | `tests/stress.py`: `no scenario's simulate work grew on an unchanged plan (#1229)` and `no scenario exceeds its own recorded cost by the budget factor`, from the gate at the tree before this line was added (3.99x; 7.6x against 6.6x), which is that mutant. Left to CI's mutation check per fixer step 5. |

## Null control

The unmodified tree (merge base 2a9cd3476) on the finder's harness over the owner's export reads step 0 over horizon mean 0.00 in every snapshot with the tanks as measured; this head reads 1.00.

The plain house is the change's null: after the floor, every fixture with no valve is byte-identical to the merge base. `first`'s null prints a wood house's kW equal to the plain valved house's, gap 0.00e+00. In the three-row meter check a no-wood house reads 50 / 50 / 50 % at meter over plan 1.0 / 0.5 / 0.25, and a wood house 50 / 75 / 87.5 %.

## Figures

Synthetic rows: plant equal to the model, reference booked per interval, solve hourly. Env for each harness line: `PYTHONPATH=tests/hastub:tests:custom_components`. `--quick` is one day, otherwise two.

- `python3 dev/audit/harnesses/r10_sav_wood_reference.py first`: SOUND, rc 0, step 0 over mean 1.000 across installs and tank starts.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat`: SOUND, row +4.12 %, rule `|pct| < 10` at a flat price; gap +5.95 kWh; residual -3.75 %. The same harness at the merge base: DEFECT, -65.81 %, gap -55.02 kWh, residual -90.83 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-vary`: row +28.75 %, residual -8.12 %. At the merge base: +18.37 %, gap -46.16 kWh.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-cold`: +7.51 %; booked 72.28 kWh, plan 66.86; residual -3.17 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-stale`: +11.53 %; plan 63.95; residual -3.88 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-coast`: +41.12 %; plan 42.56; residual -0.25 %.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-fire`: +43.83 %; plan 40.60; residual +33.24 %, wood's heat.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-full`: +87.01 %; plan 9.39; residual +87.91 %, wood's heat.
- `python3 dev/audit/harnesses/r10_sav_wood_reference.py --quick wood-unforeseen`: +47.81 %; plan 42.09, metered about 0.90 of it (the row's actual over the arm's price); printed calibration 1.0 is after the floor. The floor's own pin is the three-row meter check above.
- Census, run from `handoff/r10-rca-sav-estimate` d8eeae8f (harness sha1 04b644563c84d26378cad42a603dc050e7e5fd88, not in this tree): 6 of 6 cells in `BAND` (0.5, 1.5), rc 0; booked over horizon mean 1.00 on five, 0.92 on `unvalved`. Its ratio still fits. It lands with or after this PR.
- Same harness, `attrib` over the export (sha1-cited, ratios only): 0.00 at the base, 1.00 at this head, with the arms the row above names. `ledger`: booked over metered September 3.30, October 0.72, November 0.18, the stored rows, the same at both ends: the fix rightly leaves them alone, so the companion is the row below.
- Export's ledger through `migrate_ledger_v1` and `savings_months`, one-off probe: three months, each old basis, both columns present, saving and percent `None`, wood configured or not.
- Golden: `GOLDEN_MODE=drift GOLDEN_REF=2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e PYTHONPATH=tests/hastub python3 tests/golden.py` (rule: `CLAIMED` lines): 9 of 56 move, all valved or wood, each claimed with its direction in `tests/golden/claimed_drift.txt`; 6 may-drift entries suspended by the stamp's grammar. Solver objective on the 8 moved plans, by `objective_value`: 4 fall, 3 rise, 1 unchanged, largest move 0.25.
- `tests/golden/card_claimed_drift.txt` is untouched: `node tests/card_drift.mjs 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e` reads identical in all 45 states. The note is styled inline for this.
- Gate scope: `python3 tests/closure.py select --diff 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`. `GATE_SCOPE=auto ... ./tests/run.sh`, at 583671259 (differs from this head only in `tests/structure_budgets.json`): 4814 feature checks, 108 finite-boundary, card all pass.
- Host reds, this machine only, the first three the same at the merge base: `tests/optimality.py` `one|summer_negative|shoulder` claim, `tests/stress.py` `shoulder: cheaper than holding the setpoint` (4.67 vs 3.96), `tests/card_browser.mjs` `P9 grid: no two text runs share ink` and `P40`. `tests/entities.py` stops at a macOS task-port `PermissionError` in its sampler lane, so it did not finish locally and CI owes it; `tools/pr/ci_predict.py` predicts no red.
- Browser: `node tests/card_browser.mjs` otherwise green, including the old-basis row, the disclaimer painted within 320 px, none with no wood, and a grid cell for the note.
- `python3 tests/structure.py`: passes; `class_excess_loc` recorded down, 17630 to 17602, reason in the commit.
- Seam rule: `git grep -n "_settle_horizon(\|_thermostat_held_state(\|_sharing_wood_side(" -- custom_components`: both settle calls and the start gap share the wood side, closed in this diff. `git grep -nE "savings_pct|saving_pct" -- custom_components`: `ledger.py`, `notifier.py`, `payload.py` and the card, each reads the row's own value; no clip remains. Readers of the old-basis flag: card and notifier, each pinned.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e`: dS +0.0000 NULL. No budget rises.

## Unpinned sites

- `custom_components/heatpump_optimizer/ledger.py:75 CONST`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:78 CONST`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:139 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:151 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:153 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:289 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:443 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:443 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/ledger.py:447 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/notifier.py:102 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:396 CONST`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:401 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:411 CMP_BOUND`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:411 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:413 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:414 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:414 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:444 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:455 CMP_BOUND`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:457 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:461 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:4620 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5374 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5389 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5400 CMP_BOUND`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5400 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/store.py:831 BOOLOP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/store.py:831 GUARD_OFF`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/store.py:833 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/thermal_model.py:1919 CLAMP_DROP`: mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/thermal_model.py:1921 RETURN_DEL`: mutation-autofix (its lane mutates `custom_components/`).

## Red checks

`mutation` (predicted by `prepr.sh` step 6d, never red on the remote): the diff removes nine pinned sites of the deleted wood and coil block, whose ledger files are deleted here, and adds the sites under `## Unpinned sites`, which `mutation-autofix` pins. Cheaper detector: `tools/pr/prepr.sh` step 6d and `ci_predict`, already standing, which named all of it before the handoff.

Host reds on this machine, not check runs, are under `## Figures`.

## Forward-carry

- Empty replay: `debug.manifest.replay` in the owner's export is empty, with the text `refusing to write: 1 entity id(s) not masked to a role or a hashed id`, so this fix could not replay the owner's house. Owner of the fix: `replay_doc.py`. Carry: R10-FLY-REPLAY-MASK
- Open finding, unattributed residual: after comfort and stored heat, the valved arms leave -3.75 % (flat) and -8.12 % (varying), and the wood-cold and wood-stale arms -3.17 % and -3.88 %. Inside `FLAT_BAND_PCT` where that band applies, and not zero. The reference's COP is the lower one (1.820 against the plan's 1.92), which pushes the other way, so COP does not explain it. Not attributed here. It belongs with the month row's settling of stored heat. Carry: R10-SAV-COMFORT
- Open finding: `_apportion_by_steady_demand` has no pump cap. Energy is conserved, but a few demand steps can take a high power; largest seen 4.98 of 6.0 kW, on `summer/2z/space/wood-two-tank`. Under the cap where measured. Carry: R10-SAV-COMFORT

## Friction

none
