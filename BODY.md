R10-SAV-METER-FLOOR, with its two carries. Three changes to the savings row:

- **The meter floor (the group's brief).** `ledger.below_meter_floor` reads a row's *booked* `savings_baseline` kWh over its `savings_actual` kWh. Where that is under `METER_FLOOR` (0.5, `ledger.py`) on a row of the current reference basis with at least `MIN_CALIBRATION_KWH` metered, the row keeps both columns, its saving and percent read `None` as an old-basis row's do, and it carries `below_meter_floor: true`. It reads the booked lines, never the calibrated column, which cancels the meter. The card's table tags the row, and a note under the table and on the receipt says why (en and sv). The receipt event carries `saving_below_meter_floor`, and the notifications blueprint's monthly receipt quotes the card's note. There is no ceiling (binding of triage P387).
- **Carry 1 (owner ruling L5): the wood calibration.** `ExternalHeatState.heating()` answers "did wood heat this interval" (a fire active or fading, any displacement, any free heat). The coordinator's pending snapshot carries it as one key, `wood_heated`, and only on a wood-configured house (`None` elsewhere, so a no-wood ledger books exactly what it booked before). `add_savings_settlement` books a wood-free plan/meter pair (`SAVINGS_WOOD_FREE_LINES`) for intervals with `wood_heated` False. On a wood month, `ledger.applied_calibration` reads that pair, unfloored, once its plan kWh reaches `MIN_CALIBRATION_KWH`. With too few wood-free kWh, and on every month booked before the pair existed, the old floor `max(1.0, measured)` stays as the fallback. Each row states the basis it used as `calibration_basis`: `meter`, `wood_free` or `wood_floor`. No store migration: a month without the pair falls back.
- **Carry 0 (R10-RCA-SAV-ESTIMATE), applied here.**
  - `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`: part 2 is now the floor; "about zero" is corrected to the group's cost; the class is stated not fully barriered while the high side has no meter oracle.
  - `dev/audit/harnesses/r10_rca_sav_estimate.py`: `METER_BAND` is removed, and the `ledger` arm calls production's `ledger.below_meter_floor`.
  - `dev/audit/config/bugclasses.json`: `parts_missing` says "the meter floor" and adds "an inflated reference on a wood house has no meter oracle (owner ruling)"; `countermeasure` and `detector_idea` are updated.
  - The class mint is kept: `fold_ledger.py sync` reports `audit-find.js` already carries it, so there is no code-owned hunk.
  - The 2026-11 ratio is not re-derived (see Forward-carry).

Alternatives considered, and why each lost:
- Carrying the flag as a `SETTLEMENT_KEYS` member was rejected: that tuple is the plan step's readings from `_current_action`, and the flag is the detector's.
- Booking the pair on every house was rejected: it would add two lines to every no-wood store and receipt for nothing.
- Re-deriving "wood heated" in the ledger from published fields was rejected: the carry names `ExternalHeatState` as the owner.

Roster carries, numbered from 1 as the review packet counts them: **Carry 1** is the brief's carry 0 (the R10-RCA-SAV-ESTIMATE rewrite), answered above and under Forward-carry. **Carry 2** is the brief's carry 1 (owner ruling L5, the wood calibration), answered above and in the mutation proof and figures.

## Head

8ec661b55ea8. It is 5851e507c (`mutation-autofix`'s `ci: pin killed mutants`) plus two commits of this repair: 67dbeabe8 adds one `tests/features.py` check, and 8ec661b55 adds the `--pin-killed` record for `ledger.py:199 CMP_BOUND*2`. From the last handoff's head fce99a860 to 5851e507c the delta is the merge of origin/main 19865e5a8, the #3360 delivery row and the bot's pins. `git diff --stat fce99a860 5851e507c` names no production file, harness or test this diff reads: only governance prose, `tools/audit/machinery_ratchet.py`, delivery rows and `tests/mutation_ledger/`. So the figures below that name an older SHA stand as taken. Every figure this repair takes is at 67dbeabe8 or 8ec661b55. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so origin/main was not merged (the brief and `fixer.md` step 6). `prepr.sh` ran clean (rc 0) at 8ec661b55 against origin/main 6457496ab. Main then moved to 3fdaa9da9, 32 commits past the merge base, at 2026-11-09T04:51:22Z. The merge-tree check against 3fdaa9da9 is also conflict-free, so `prepr.sh` was not re-run on a merge.

## Mutation proof

- **The meter floor's bounds (this repair).** `tests / mutation` refused at 5851e507c (jobs 128945717188 and 128945739638): `ADDED UNPINNED custom_components/heatpump_optimizer/ledger.py:199 CMP_BOUND*2`. It named no other site. Both mutants were run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 tests/features.py' --in-place` in a real worktree. The two mutants are `metered_kwh > MIN_CALIBRATION_KWH` (CMP_GE) and `booked_kwh <= METER_FLOOR * metered_kwh` (CMP_LT).
  - At 5851e507c: `SURVIVED NULL`, `SURVIVED CMP_GE`, `KILLED CMP_LT`. CMP_LT is killed by `the meter floor is strict, ...` (booked exactly 0.5 of metered). CMP_GE survived because no check meters exactly `MIN_CALIBRATION_KWH`: `_sb_tiny` meters 0.96 kWh.
  - The new check, `the meter floor's two bounds: exactly MIN_CALIBRATION_KWH metered is floored, a booked kWh of exactly METER_FLOOR of metered is not`, calls production's `ledger.below_meter_floor` at both bounds.
  - At 67dbeabe8: `SURVIVED NULL`, `KILLED CMP_GE`, `KILLED CMP_LT`, rc 0.
  - Then `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main` at 67dbeabe8 printed `pinned ... ledger.py:199 CMP_BOUND -- killed by tests/features.py` twice and `PIN KILLED: 2 pinned, 0 left unpinned`. It wrote `tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json` ("Each of the 2 sites under this anchor was killed"), committed as 8ec661b55.
  - No mutant is equivalent, so no `survivor_triage` record is written.
  - The lane's own command, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3`, run with that record in the tree, prints `0 survivor(s) of 7 evaluated = 0.0%, cap 20.0%` and `MUTATION TABLE PASSED`, rc 0. At 5851e507c CI printed `MUTATION TABLE REFUSED` for it.
- **Carry 1.** Mutant: in `savings_months`, pass the month's all-interval `meter_calibration(key)` in place of the wood-free pair. That calibrates a wood month from all its intervals. Run: `PYTHONPATH=tests/hastub python3 tests/features.py` on a `git archive` of 7cbbf73eb with that one line changed. Red:
  - `a wood house whose wood-free hours meter 0.8 of the plan publishes that calibration, not the floor's 1.0`
  - `a wood house's model that reads the meter low on its wood-free hours is still corrected up`
  - `at one flat price the wood-free calibrated row's saving is the volume difference alone`
  - `a wood month with too few wood-free kWh, or booked before the pair existed, keeps the floor's row exactly`
  - `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`
  - `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`
  - `the coordinator publishes the wood floor from the house's configuration, and no floor without wood`
  - plus `#363 recorded_at`, the `git archive` runner's own failure (`fixer.md` step 2).

  The `wood-plant` arm on the same mutant shows wood's heat cancelled, the 2026-11-04 failure: `RESULT wood_plant_error_m0.8: mean -1.96 % min -4.50`, `m1.0: mean -1.96 % min -4.50`, `m1.2: mean -1.95 % min -4.50`. Restored: the head reads `ALL 4987 FEATURE CHECKS PASSED`, and its `wood-plant` RESULT lines read `+0.00` at every m.
- **The floor.** Mutant: `below_floor = False` (the predicate deleted), on a `git archive` of e9d43e5cb, `tests/features.py`: `a booked reference under the meter floor of its metered kWh states no saving, keeps both columns and says why` goes red. In the harness, `meter-floor` zeroes the booked reference (row withheld), then drops the check by setting `METER_FLOOR` to 0 (row published): `mutant: booked reference zeroed: withheld (expected withheld)` and `... check dropped (METER_FLOOR 0): published (expected published)`.
- **Failing test first.** The new block of `tests/features.py`, run at the merge base 17e621f08 (production code from the base, tests from fd537ed06). The four carry-1 checks FAIL, with the floor publishing `meter_calibration 1.0`. The floor block stops on `ImportError: cannot import name 'METER_FLOOR'`. The no-wood null check is `ok` there.

## Unpinned sites

Each site below is pinned by `mutation-autofix` after the push (its lane mutates `custom_components/`). The value check named beside it is the one in `tests/features.py` expected to kill it. A site that check does not kill is the lane's to triage, and none is claimed killed here.

- `custom_components/heatpump_optimizer/external_heat.py:151 CMP_BOUND*2`, `custom_components/heatpump_optimizer/external_heat.py:151 RETURN_DEL`: pinned by `mutation-autofix`; value check: `the pending snapshot carries wood_heated from the detector on a wood house, and None on a plain one` (its quiet, displacing and free-heat legs).
- `custom_components/heatpump_optimizer/ledger.py:115 CONST`: pinned by `mutation-autofix`; value check: `a booked reference under the meter floor ...` (asserts `METER_FLOOR == 0.5`).
- `custom_components/heatpump_optimizer/ledger.py:187 GUARD_OFF`: pinned by `mutation-autofix`; value check: `R10-SAV-COMFORT null control: an interval without either reading settles nothing` (calibration and basis None).
- `custom_components/heatpump_optimizer/ledger.py:189 GUARD_OFF`: pinned by `mutation-autofix`; value check: `with no wood the calibration stands as specified: the meter cancels at every ratio`.
- `custom_components/heatpump_optimizer/ledger.py:191 GUARD_OFF`: pinned by `mutation-autofix`; value check: `a wood month with too few wood-free kWh, or booked before the pair existed, keeps the floor's row exactly`.
- `custom_components/heatpump_optimizer/ledger.py:193 CLAMP_DROP`, `custom_components/heatpump_optimizer/ledger.py:193 RETURN_DEL`: pinned by `mutation-autofix`; value check: `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`.
- `custom_components/heatpump_optimizer/ledger.py:199 BOOLOP`, `custom_components/heatpump_optimizer/ledger.py:199 RETURN_DEL`: pinned by `mutation-autofix` (5851e507c); value check: `a booked reference under the meter floor ...`.
- `custom_components/heatpump_optimizer/ledger.py:199 CMP_BOUND*2`: pinned by this repair's `--pin-killed` (8ec661b55); value check: `the meter floor's two bounds: ...` (see Mutation proof).
- `custom_components/heatpump_optimizer/ledger.py:271 CLAMP_DROP`: pinned by `mutation-autofix`; `_prune`'s existing `KEEP_MONTHS` checks (the line folded its temporary, unchanged in effect).
- `custom_components/heatpump_optimizer/ledger.py:379 GUARD_OFF`: pinned by `mutation-autofix`; value check: `a no-wood row is unchanged field by field ..., the pair or not` and the wood-free checks.
- `custom_components/heatpump_optimizer/ledger.py:395 RETURN_DEL`: pinned by `mutation-autofix`; every ledger value check reads `line()`.
- `custom_components/heatpump_optimizer/ledger.py:466 CMP_BOUND`, `custom_components/heatpump_optimizer/ledger.py:466 GUARD_OFF`: pinned by `mutation-autofix`; the #2492 checks on `MIN_CALIBRATION_KWH` (a CMP_BOUND kill needs a plan of exactly 1.0 kWh, and none is claimed).
- `custom_components/heatpump_optimizer/ledger.py:468 RETURN_DEL`: pinned by `mutation-autofix`; value check: `#2492: an install whose meter reads its model keeps the modelled figures byte-identical`.
- `custom_components/heatpump_optimizer/ledger.py:515 BOOLOP`: pinned by `mutation-autofix`; value checks: the floor block (an old-basis row stays old basis and not floored; a collapsed row is withheld).
- `custom_components/heatpump_optimizer/notifier.py:106 BOOLOP`: pinned by `mutation-autofix`; value check: `the receipt event says a row under the meter floor states no saving, and an ordinary row says it is not`.

## Null control

- The bounds check. CMP_GE reads `SURVIVED` at 5851e507c, before the check, and `KILLED` at 67dbeabe8, after it. The unedited NULL run reads `SURVIVED` at both heads, so `tests/features.py` is green unmutated at each, and the kill is the mutant's.
- (a) Flat price. The wood-free row at one flat price saves the volume difference alone (a features check). The `wood-plant` arm's flat rows read the same at both ends wherever m is 1.0 or above: `m 1.0 flat pct 7.588885569166417` and `m 1.2 flat pct 7.593865152873221` at 17e621f08 and at 7cbbf73eb. The flat-price null `valve-flat` publishes, `pct 0.5563864792102902` at both ends.
- (b) No-wood houses. Every field (calibration, baseline, actual, saving, percent) of a no-wood row at a meter of 1.0, 0.5 and 0.25 of plan equals its merge-base value, with or without the pair. The existing no-wood check is unchanged and green. The wood fallback (too few wood-free kWh, or no pair) reads the exact merge-base row: `{1.0, 48.0, 4.8, 43.2, 90.0}` and `{1.0, 48.0, 12.0, 36.0, 75.0}`, both read at 17e621f08 in the red run.
- (c) The existing wood checks (a meter under plan earns its saving; an under-reading model is still corrected) are unchanged and green at the head.
- The `wood-plant` perturbation (pump blind to the fire) reads `+0.00 %` at every m, at both ends.

## Figures

- Wood-reference harness, full run (not `--quick`), at 17e621f08 and at 7cbbf73eb, each from a `git archive` export: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py <arm>`.
  - `wood-plant` no-fire booking error at m 0.8: `+25.00 %` (calibration 1.0, the floor) at the base; `+0.00 %` (calibration 0.8, `wood_free`) at the head. That is zero, inside the arm's own spread (sd 0.00).
  - RESULT at the base: `wood_plant_error_m0.8: mean +0.00 % min +0.00 max +0.00 sd 0.00 over 9 fires`; `m1.0: mean +0.00 % ... sd 0.00`; `m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`.
  - RESULT at the head: `+0.00 %`, sd 0.00, at m 0.8, 1.0 and 1.2.
  - So the fire's share stays at its merge-base value at m 0.8 and 1.0. **At m 1.2 it moves from -1.95 % to 0.** There the base's floor let a meter over the plan be scaled down by the fire's fall, cancelling part of wood's heat. The head calibrates from the wood-free hours, so the heat counts in full. This is the one place the carry's "stays at its merge-base value" does not hold, and it moves in the direction the ruling asks.
  - Closed-loop arms, base -> head row percent. Identical: `valve-flat` 0.556, `valve-vary` 25.264, `wood-cold` 0.467, `wood-full` 92.987, `wood-fire` 37.371, `wood-stale` 4.070, `wood-coast` 19.336. Changed: **`wood-unforeseen` 40.417 -> 39.802** (calibration 1.0 -> 0.99). That arm's stated meter cut of 0.5 runs to 24:00, past the fire (17:00 to 21:00) plus the detector's 90-minute fade, which the harness emulates (`_wood_heated`, from `ExternalHeatConfig.decay_minutes`). So 22:30 to 24:00 count as wood-free and read as model error. **This is the predicate's limit: a tank coasting past the detector's fade is calibrated as model error.** In this arm it costs 0.6 points.
- `meter-floor` (asserted, SOUND at 7cbbf73eb). Booked over metered on each arm, all published: `valve-flat` 1.044, `valve-vary` 1.027, `wood-unforeseen` 1.749, `wood-cold` 1.044, `wood-full` 13.532, `wood-fire` 1.627, `wood-stale` 1.078, `wood-coast` 1.289. The six `wood-plant` rows (no fire, and a 12 kW fire from 17:00, at each m) also publish. A month under `MIN_CALIBRATION_KWH` with a zeroed reference publishes. (Its percent is `None` from `savings_pct`'s near-zero-baseline rule; its saving is a figure.)
- Resistive-heavy month (immersion kWh added to the meter at a share of the pump's): `RESULT meter_floor_immersion_share0.5: below_meter_floor False`, `share1.0: False`, `share1.5: True`, `share2.0: True`; booked over metered 0.696, 0.522, 0.417, 0.348. **The floor false-fires once an immersion meters more than about 1.1 times the pump's own kWh in a month**, on this house with a hot-water-free reference. This is the margin the brief asked to be measured. It is stated, not fixed.
- Floor mutant (`below_floor = False`), `PYTHONPATH=tests/hastub python3 tests/features.py` on a `git archive` of e9d43e5cb: `2 of 4987 FEATURE CHECKS FAILED`. The red checks are `a booked reference under the meter floor of its metered kWh states no saving, keeps both columns and says why` and the archive's own `#363 recorded_at`. The guard, strictness and wood checks stay green, as they should: they assert `below_meter_floor` False.
- `python3 tests/structure.py` at e9d43e5cb: no breach. Recorded at 7cbbf73eb: `class_excess_loc` 17558 -> 17555, `max_class_loc` 7933 -> 7932, `duplication_copies` 10 -> 9. The payment is in the commit message: the coordinator's 4-line `interval_h` folds to one; MonthlyLedger's savings lines book through one priced helper, with the calibration choice and the floor rule as module functions. No raise.
- `python3 tools/audit/fold_ledger.py check`: `50 classes, ... 0 violation(s)`. `sync --dry-run`: `audit-find.js already carries`. The class mint is kept, with no `audit-find.js` hunk.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out` at 67dbeabe8. `GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh` at e9d43e5cb: see Red checks. This repair's delta reaches `tests/features.py` alone; that script is green at 67dbeabe8, which is the NULL run above. `python3 tests/structure.py` at 67dbeabe8 prints `STRUCTURE RATCHET PASSED`.
- Class seams: the rule that enumerates where a published saving leaves the package is `git grep -n "savings_sek\|savings_pct" custom_components/`. It returns `ledger.py` (the row), `notifier.py` `_monthly_receipt` (gated: `saving_below_meter_floor`), `sensor.py` `MonthlySavingsSensor` (its state is the row's `savings_sek`, `None` when withheld; the row's flag is in `savings_months`), the card (`heatpump-optimizer-card.js`, tagged and noted), and `payload.py` (the type).

## Red checks

- `tests / mutation`: **pinned**. It was red at 5851e507c on `ledger.py:199 CMP_BOUND*2`, which `mutation-autofix` did not pin (CMP_GE survived; that job concluded skipped). This repair killed CMP_GE with a new check, and `--pin-killed` ran at 67dbeabe8 (`2 pinned, 0 left unpinned`). The head 8ec661b55 adds only the record that run wrote. The cheaper detector is `prepr.sh` step 6d, which lists unpinned sites before the handoff, at no added standing cost. It names a site but cannot say whether one will survive; only a mutant run can say that. The last handoff took the site as `mutation-autofix`'s to pin without running its mutant, which `fixer.md` step 2 asks for ("Run the ledger's own mutant before claiming a kill").
- `tests / mutation-autofix`: red on a commit of this branch. It is the same failure as `tests / mutation` above: an added site that no driver kills (`ledger.py:199`'s CMP_GE) leaves the job with nothing it may pin, and `ci-autofix.md` ("A survivor is red") keeps the triage manual. It is answered by the kill and the pin above. The cheaper detector is the same one, `prepr.sh` step 6d plus the ledger's own mutant run, and adds no standing cost.
- `tests/stress.py`: `the probed scenarios' memory peaks stay within their recorded budgets`. It is red at the head and green at the merge base. The tracemalloc peak of a probe is bimodal at the head, 3.46 or 5.3 MiB, against a ×1.5 threshold of 5.25 MiB. Counts:
  - Head, `python3 tests/stress.py --memory-probe '{"season":"shoulder","building":"heavy_old"}'`: 8 of 17 runs at 5.3. At a fixed `PYTHONHASHSEED=1`, 2 of 4, so it is not hash order.
  - Merge base, same command in a real worktree: 0 of 13. Full `stress.py` runs at the base: 18 of 18 probe readings in budget.
  - The only file this diff changes that the probe imports is `payload.py` (the two `SavingsMonth` keys and their comments). The head's `payload.py` alone in the base tree reads 5.3 in 1 of 4 runs.
  - Through a `runpy` wrapper, at the head: 0 of 7. A `gc.callbacks` snapshot never fired above 4.5 MiB.

  **Not root-caused.** No cheaper detector exists that I could name. This is not a regression in solver memory: the RSS arm reads `attributable 0.0 MiB` at both ends. Re-recording `stress_budgets.json`'s memory half would be a raise, and I did not take it without the owner. Handed to the orchestrator: it needs a decision, or a `root-cause.md` seat on why a `TypedDict` edit moves a traced solver peak by a fixed 1.84 MiB.
- `tests/typing_ruler.py` went red in the first gate run at 7cbbf73eb: `arg-type` in `ledger.py`, from passing the pending snapshot's float-typed value into a `bool` parameter. Fixed at e9d43e5cb (mypy: `no issues found`). The cheaper detector is mypy on the changed module before the commit, at no standing cost. It already exists; I ran it late.

## Forward-carry

- Carry 0's ratio correction ("correct the 2026-11 ratio to what the arm prints") is not done: the `ledger` arm reads the owner's diagnostics export, which is on no ref and not in this container; the RCA now marks the figure unverified, in `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md` part 2. Carry: dismissed: the export is on no ref, so no seat can re-run the arm
- The predicate counts a wood tank coasting past the detector's 90-minute fade as wood-free (`wood-unforeseen` 40.417 -> 39.802), and the floor false-fires on a month whose immersion meters above about 1.1 times the pump's kWh: both measured and stated in this body, as the brief asked. Carry: dismissed: measured and stated as the brief required, no later stage changes

## Friction

none
