The immersion line was booked from the wrong measure, under the wrong name.
`_accumulate_energy` carved everything the meter drew above the PLAN's ask
while the latch held, and called it `immersion` without asking what the
install had configured. The group's brief records the result on the owner's
install -- no element there, and the plan under-reads this pump's own
compressor 1.28x -- as October booking an immersion line worth 3.9 % of the
month's metered kWh while August and September booked none (#2729).

The carve is now one decision, `pump_signals.resistive_carve_out`, so the
booking and the totals cannot drift apart. It books only the draw over the
threshold that tripped the latch -- nameplate x `IMMERSION_FACTOR`, never the
plan's ask -- and names the line its source gives: the pump's tank-booster or
backup-heater flag while it reads on, else `immersion` only when the install
declared an element (`immersion_feedback_enabled`). No element configured, or
both heater flags on at once (the kilowatts cannot be apportioned), refuses
the line. `payload.py` owns the three line names; `ledger.BILLED_LINES`,
`ENERGY_LINES` and the closed month's receipt all read that owner, so a
booster month's kWh reach every figure that is metered energy. The latch itself
still gates the COP learner, the frequency map and the interval space power.

The carve is a partition of the spot line, so the savings lines must not move;
that is a null control below, not an assertion.

C1 (#2805) rides here because its seam is the Fix write in
`setpoint_check._dhw`: the written floor is now quantised UP to the entity's
step in the entity's own unit. A hand-set 48.05 °C floor on a °F entity wrote
118.5 °F, which the entity snaps to 118 °F = 47.78 °C -- below the request --
and the notice re-raised; it now writes 119 °F. An on-step floor is unchanged
(the check carries both nulls).

Acted under the owner's full-scope mandate #6329234399.

## Head

`99367cbc3a012e21ca1183526671a5cc3cc98e3f`

## Mutation proof

Two mutants of the production predicate, each graded by the `features.py`
block that pins it, both restored afterwards. The block is
`tests/features.py`'s ledger-carve section; its fixtures (`_Coord`,
`_asyncio`, `_FakeHass`, `_METER`, `IMMERSION_FACTOR`) are defined 7k-16k lines
above it, so `tools/audit/seat/features_block.py` (which runs the file header
plus the block) cannot run it alone: the block was executed over the mutated
tree by a scratch driver that execs the same file header, the same fixture
slices taken from `tests/features.py`, and the block text, under the same
`tests/hastub` path. The driver is not in the tree; the block itself is.

- M1 -- the pre-fix measure: `coordinator.py`'s
  `threshold_kw=float(ctx._thermal_params.max_electrical_power) * IMMERSION_FACTOR`
  replaced by `threshold_kw=planned_total`. Red (the booster arm and the
  flat-draw null):
  `FAIL R10-IMMERSION-LATCH: a booster flag on books only the draw over the latch
  threshold, under the booster's own line  [{'spot': 1.0, 'grid_fee': 3.45,
  'immersion': 0.0, 'dhw_booster': 2.45, 'backup_heater': 0.0}: spot + booster
  must equal the 3.45 kWh metered, and the fee line keeps the full energy]`
  `FAIL R10-IMMERSION-LATCH null: a flat draw at or below nameplate books zero,
  flag on and latched  [at nameplate {'spot': 1.0, 'grid_fee': 2.5, 'immersion':
  0.0, 'dhw_booster': 1.5, 'backup_heater': 0.0}, under it {'spot': 1.0,
  'grid_fee': 2.0, 'immersion': 0.0, 'dhw_booster': 1.0, 'backup_heater': 0.0}]`
  -- a flat draw at nameplate books 1.5 kWh of "resistive" heat, which is the
  defect the null control exists to catch. The no-element control stays green
  under M1, and that is its own null: the source gate is a different predicate.
- M3 -- `setpoint_check.py`'s `quantise_setpoint_c(hass, entity_id, floor,
  rounding="up")` with `rounding` dropped (nearest). Red:
  `FAIL #2805: a fractional disinfection floor is written up to the entity's
  step in its own unit; an on-step floor writes unchanged  [{'degF step 1':
  (118.0, 119), 'degC step 1': (48.0, 49), 'degC step 0.5': (48.0, 48.5),
  'null degF on-step': (140.0, 140), 'null degC on-step': (60.0, 60)}]` --
  every fractional floor falls back to the snapped value while both on-step
  nulls stay put.

## Null control

- The unmodified tree is the defect: `python3 tests/features.py` at
  6eb552157 with this branch's tests prints `10 of 4481 FEATURE CHECKS FAILED`
  -- the eight `R10-IMMERSION-LATCH` controls, `#2805`, and the strengthened
  `savings_actual is the metered kWh` arm -- with the measured lines `[{'spot': 1.5, 'grid_fee': 3.0, 'immersion': 1.5, ...}]` for the
  no-element install and `{'degF step 1': (118.5, 119), ...}` for the floor.
- The flat-draw null in the tree: at nameplate and one kW below it, with the
  booster flag on and the latch held, all three resistive lines book 0.0 and
  the spot line carries 2.5 and 2.0 kWh. Its only difference from the booster
  arm is the draw.
- The savings null in the tree: the same interval booked twice, differing only
  in the booster flag -- `savings off (3.45, 8.625, 1.5, 3.45, 3.45) on (3.45,
  8.625, 1.5, 3.45, 2.875)` -- `savings_actual` (kWh and SEK), the thermostat
  baseline and `total_energy_kwh` identical, while the spot line moves by the
  0.575 kWh carved. Priced at one flat spot, so the claim is volume-only.
- The latch's own null: the same 6.9 kW interval with `_immersion_active`
  False books all 3.45 kWh to spot and no resistive line.
- C1's nulls: 60 °C on a whole-degree °C entity and 140 °F on a whole-degree
  °F entity write unchanged (the two `null` arms of the `#2805` check).

## Figures

- `10 of 4481 FEATURE CHECKS FAILED` before the fix, `ALL 4481 FEATURE CHECKS
  PASSED` at this head -- `python3 tests/features.py`
- `R10-IMMERSION-LATCH controls: no element {'spot': 3.0, 'grid_fee': 3.0,
  'immersion': 0.0, 'dhw_booster': 0.0, 'backup_heater': 0.0} booster {'spot':
  2.875, 'grid_fee': 3.45, 'immersion': 0.0, 'dhw_booster':
  0.5750000000000002, 'backup_heater': 0.0} flat at nameplate {'spot': 2.5,
  'grid_fee': 2.5, 'immersion': 0.0, 'dhw_booster': 0.0, 'backup_heater': 0.0}
  savings off (3.45, 8.625, 1.5, 3.45, 3.45) on (3.45, 8.625, 1.5, 3.45,
  2.875)` -- `python3 tests/features.py` (the block prints its controls on the
  pass)
- `class_excess_loc 18041 <= 18047`, `max_class_loc 8216 <= 8222`, both
  re-recorded downwards in this commit -- `python3 tests/structure.py`
- `MODE: SCOPED -- 28 script(s) run, 5 scoped out` --
  `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- `3.9 %` and `1.28x` are the brief's derived ratios for #2729, quoted from the
  roster and not re-measured here -- `git grep -n '3.9 %' --
  dev/programme/rosters/wave-r10-groups.json`

## Red checks

- `tests / mutation` -- predicted red at this head before the push: 12 unpinned
  sites the diff adds. The cheaper detector already ran and caught it: `prepr.sh`
  step 6d's `tools/pr/ci_predict.py --base 6eb552157b63` prints the 12 `ADDED
  UNPINNED` lines in seconds, pre-push, with no CI run; its standing cost is that
  predict call. Each site's disposition is under `## Unpinned sites`, and the
  surviving mutants' pins are `mutation-autofix`'s to record from the run.

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:10225 CMP_BOUND`: pinned
  by `R10-IMMERSION-LATCH: a booster flag on books only the draw over the latch
  threshold` -- deleting the booking leaves spot at 3.45 and the arm red.
- `custom_components/heatpump_optimizer/coordinator.py:10225 GUARD_OFF`: pinned
  by the same arm, and by the declared-element and backup arms.
- `custom_components/heatpump_optimizer/pump_signals.py:246 CMP_BOUND*2`:
  written triage -- the non-positive-hours and non-positive-threshold guards
  cannot be reached from `_accumulate_energy` (it returns before booking when
  `energy <= 0`, and the threshold is nameplate x 1.15 for a configured pump);
  the branch books nothing on any other path. `mutation-autofix` may record a
  survivor here and that is the triage.
- `custom_components/heatpump_optimizer/pump_signals.py:246 GUARD_OFF`: same
  written triage.
- `custom_components/heatpump_optimizer/pump_signals.py:248 CMP_BOUND`: pinned
  by `R10-IMMERSION-LATCH null: a flat draw at or below nameplate books zero`
  -- the measured red under M1 is exactly this bound moving.
- `custom_components/heatpump_optimizer/pump_signals.py:248 GUARD_OFF`: pinned
  by the same null and by the no-element control.
- `custom_components/heatpump_optimizer/pump_signals.py:250 GUARD_OFF`: pinned
  by `R10-IMMERSION-LATCH: a booster flag on books only the draw over the latch
  threshold, under the booster's own line` (the line would fall through to
  `immersion` or to no line).
- `custom_components/heatpump_optimizer/pump_signals.py:251 GUARD_OFF`: pinned
  by `R10-IMMERSION-LATCH: both heater flags on refuses the line`.
- `custom_components/heatpump_optimizer/pump_signals.py:254 GUARD_OFF`: pinned
  by `R10-IMMERSION-LATCH: a backup-heater flag on books under its own line`.
- `custom_components/heatpump_optimizer/pump_signals.py:256 GUARD_OFF`: pinned
  by `R10-IMMERSION-LATCH: a declared immersion element books the same threshold
  excess`.
- `custom_components/heatpump_optimizer/pump_signals.py:260 RETURN_DEL`: pinned
  by every R10-IMMERSION-LATCH arm -- no arm books a line without it.
- `custom_components/heatpump_optimizer/setpoint_check.py:141 GUARD_OFF`: pinned
  by `#2805: a fractional disinfection floor is written up to the entity's step`
  and its two on-step null arms.

## Forward-carry

- C2, the legionella step-0/step-1 flap, is not fixed here and the carry stands
  as recorded. The alternation is produced in `dhw_planner._dhw_legionella_due`
  / `_place_legionella_step` (dhw_planner.py:156-587) -- which step the plan
  puts the boost on -- and the switch follows that step; a debounce inside
  `coordinator.py` would decouple the written switch from the plan it
  documents, and the alternative the carry names changes the per-boost switch
  contract `docs/configuration.md` states. Neither `dhw_planner.py` nor the
  switch contract is this group's file, and the group that owns the
  planner is done. Carry: dismissed: no live group owns dhw_planner.py; the
  carry stands on this group's roster row.

## Friction

- features-block-header-only: cost: `tools/audit/seat/features_block.py` runs
  only the file header plus one block, so a block whose fixtures are defined
  mid-file (`_Coord` at 9680, `_t2_coord` at 16249) cannot be run alone -- the
  alternative was a full `tests/features.py` per mutant, roughly 45 minutes
  each on this seat; the mutation proofs above used a scratch driver over the
  same file's header and fixture slices. Carry: dismissed: no open group owns
  features_block.py, and a --prefix flag is a seat-instrument change outside
  this seam.
