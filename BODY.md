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

`10f75266e6fd1774cf42e4196e7708c87bea10af` is the code head measured in this round: it merges origin/main `e8cb7e683` into the bot head `4607ba956` (clean, no resolution) and adds one commit answering `tests / mutation` and `tests / typing` (`## Red checks`).

`c616d5e7278c0cad4fea370305b6426fbc2c1409` re-keys 11 `## Unpinned sites` line(s) the main merge moved from `99367cbc3a012e21ca1183526671a5cc3cc98e3f`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:10225 CMP_BOUND -> custom_components/heatpump_optimizer/coordinator.py:10239 CMP_BOUND; custom_components/heatpump_optimizer/coordinator.py:10225 GUARD_OFF -> custom_components/heatpump_optimizer/coordinator.py:10239 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:246 CMP_BOUND -> custom_components/heatpump_optimizer/pump_signals.py:247 CMP_BOUND; custom_components/heatpump_optimizer/pump_signals.py:246 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:247 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:248 CMP_BOUND -> custom_components/heatpump_optimizer/pump_signals.py:249 CMP_BOUND; custom_components/heatpump_optimizer/pump_signals.py:248 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:249 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:250 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:251 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:251 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:252 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:254 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:255 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:256 GUARD_OFF -> custom_components/heatpump_optimizer/pump_signals.py:257 GUARD_OFF; custom_components/heatpump_optimizer/pump_signals.py:260 RETURN_DEL -> custom_components/heatpump_optimizer/pump_signals.py:261 RETURN_DEL.

`c616d5e7278c0cad4fea370305b6426fbc2c1409` merges origin/main `ea36188c3` into the authored code head `99367cbc3a012e21ca1183526671a5cc3cc98e3f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

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

Round 2 (`10f75266e`, the four survivors `tests / mutation` refused at
`4607ba956`). Each mutant is a copy of `custom_components/` with one line
changed, imported by a scratch driver that runs `tests/features.py` from its
first line to just past the new checks (1421 checks), from a root whose
`custom_components` is the mutant (`harness.py` inserts that path
cwd-relative). The unmutated tree is the null: `ALL 1421 PREFIX CHECKS
PASSED`. The driver is not in the tree; the checks are.

- M4 `pump_signals.py` `actual_kw <= threshold_kw` -> `<`: `1 of 1421 PREFIX
  CHECKS FAILED`, `R10-IMMERSION-LATCH: the carve refuses at its bounds`
  `[bounds {'at threshold': ('dhw_booster', 0.0), 'zero hours': None, 'zero
  threshold': None} ...]`.
- M5 `hours <= 0.0` -> `<`: the same check, `'zero hours': ('dhw_booster',
  0.0)`.
- M6 `threshold_kw <= 0.0` -> `<`: the same check, `'zero threshold':
  ('dhw_booster', 3.45)`.
- M7 `coordinator.py` `if resistive_line:` -> `if False:`: `4 of 1421`, the
  booster, backup, declared-element and sub-epsilon arms.
- M8, the failing test first -- the pre-fix guard restored, `if resistive_kwh
  > 1e-6:`: `1 of 1421`, `R10-IMMERSION-LATCH: a carve smaller than any
  epsilon is booked` `[{'spot': 2.875, 'grid_fee': 2.8750005, ...,
  'dhw_booster': 0.0, ...}]` -- 5e-7 kWh left spot and reached no line.

## Null control

- The unmodified tree is the defect: `python3 tests/features.py` at
  6eb552157 with this branch's tests prints `8 of 4480 FEATURE CHECKS FAILED`
  -- the seven `R10-IMMERSION-LATCH` controls and `#2805` -- with the measured
  lines `[{'spot': 1.5, 'grid_fee': 3.0, 'immersion': 1.5, ...}]` for the
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

- `8 of 4480 FEATURE CHECKS FAILED` before the fix, `ALL 4480 FEATURE CHECKS
  PASSED` at this head -- `python3 tests/features.py`
- `R10-IMMERSION-LATCH controls: no element {'spot': 3.0, 'grid_fee': 3.0,
  'immersion': 0.0, 'dhw_booster': 0.0, 'backup_heater': 0.0} booster {'spot':
  2.875, 'grid_fee': 3.45, 'immersion': 0.0, 'dhw_booster': 0.575, ...} flat at
  nameplate {'spot': 2.5, ...} savings off (3.45, 8.625, 1.5, 3.45, 3.45) on
  (3.45, 8.625, 1.5, 3.45, 2.875)` -- `python3 tests/features.py` (the block
  prints its controls on the pass)
- `class_excess_loc 18041 <= 18047`, `max_class_loc 8216 <= 8222`, both
  re-recorded downwards in this commit -- `python3 tests/structure.py`
- `MODE: SCOPED -- 28 script(s) run, 5 scoped out` --
  `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- `3.9 %` and `1.28x` are the brief's derived ratios for #2729, quoted from the
  roster and not re-measured here -- `git grep -n '3.9 %' --
  dev/programme/rosters/wave-r10-groups.json`

- `ALL 1421 PREFIX CHECKS PASSED` at `10f75266e`, and M4-M8's failing
  counts above -- the scratch prefix driver over `tests/features.py` (above)
- `ALL 9 typing-ruler checks PASSED` at `10f75266e`; `2 of 10 typing-ruler
  checks FAILED` at `4607ba956` (CI job 122537218510) -- `python3
  tests/typing_ruler.py --mypy` under the pinned venv-ha
- `STRUCTURE RATCHET PASSED` at `10f75266e` -- `python3 tests/structure.py`
- `CI PREDICT: 3 unpinned site(s) the diff adds` at `10f75266e` (the lines
  under `## Unpinned sites`) -- `python3 tools/pr/ci_predict.py --base
  e8cb7e68302b`
- `MODE: SCOPED -- 22 script(s) run, 11 scoped out` for `10f75266e` over its
  own parent -- `python3 tests/closure.py select --diff HEAD~1`; run locally:
  the scripts under 20 s recorded, each green; `features.py`, `entities.py`,
  `boost_drift_replay.py`, `harness_headers.py`, `arch_score_head.py`,
  `finite_boundary.py` and `card.mjs` are CI's
## Red checks

- `tests / mutation` -- red at `4607ba956` after `ci: pin killed mutants`:
  `MUTATION TABLE REFUSED -- 3803 unpinned site(s) against 3802 at the ratchet
  base e8cb7e683..., 4 of them added by this diff` (job 122537018832). The four
  were survivors: no check reached the carve's three refusal bounds at
  equality or zero, and the coordinator's `resistive_kwh > 1e-6` bound moved
  by one changes no observable line. Repaired at `10f75266e` by real
  assertions (see `## Mutation proof` M4-M8) and by removing the epsilon
  guard, never by triage. Cheaper detector: `tools/pr/ci_predict.py --base
  <merge-base>` (prepr step 6d) lists every added unpinned site pre-push in
  seconds -- it named these at the original handoff; what it cannot say is
  which will survive, which only the drive (CI's `mutation-pins`, or a local
  mutant run of the block) answers. No cheaper detector of survival exists
  than running the mutant.
- `tests / typing` -- red at `c616d5e72` and `4607ba956`: `FAIL errors did not
  grow [recorded 0, measured 1 (+1)]`, `by_code[arg-type]`, the line being
  `setpoint_check.py:142: Argument 2 to "quantise_setpoint_c" has
  incompatible type "str | None"` (job 122537218510). Repaired at `10f75266e`.
  Cheaper detector exists: the scoped gate selects `tests/typing_ruler.py`
  for this diff, and with `HPO_TYPING_PYTHON` set (the seat shim exports it
  when `venv-ha` exists) it runs the pinned mypy census locally; standing cost
  about 30 s per gate run on this seat. Unset, it prints what goes unchecked
  and passes, which is how the census regression reached CI.
- `prelude` -- red at `c616d5e72` (run 40587828577, job 122483930403):
  `tools/ci/prelude.py` exited 3 on `RATE-LIMITED ... actions/runs/.../jobs`,
  GitHub's API quota at run time, not the diff. No cheaper detector exists: the
  condition is the shared API bucket when the run executes; the next run's
  `prelude` at `4607ba956` was green.

## Unpinned sites

At `10f75266e` (`ci_predict.py`). The rest the original handoff listed are
pinned in the ledger by `ci: pin killed mutants` (`4607ba956`); the
`coordinator.py` `if resistive_kwh > 1e-6:` site is gone with its line, and its
stale GUARD_OFF pin removed.

- `custom_components/heatpump_optimizer/coordinator.py:10239 GUARD_OFF`
  (`if resistive_line:`): pinned by `mutation-autofix` -- killed by
  `R10-IMMERSION-LATCH: a booster flag on books only the draw over the latch
  threshold` and three sibling arms (M7).
- `custom_components/heatpump_optimizer/pump_signals.py:247 CMP_BOUND*2`:
  pinned by `mutation-autofix` -- killed by `R10-IMMERSION-LATCH: the carve
  refuses at its bounds` (M5, M6). The earlier written triage
  (unreachable from `_accumulate_energy`) is withdrawn: the bounds are the
  public decision's contract and are now checked on it directly.
- `custom_components/heatpump_optimizer/pump_signals.py:249 CMP_BOUND`:
  pinned by `mutation-autofix` -- killed by the same check (M4).

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

