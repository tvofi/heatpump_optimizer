Round 10, group `R10-PUMP-MODEL`: what channel the plan's modulation floor
travels on, and who owns the plan step an instant falls in -- plus the P2 rule
that holds the second. Part of #2232 and Part of #2238.

The group's third finding, **D2-s2-01** (one hot-water lift law), follows on
its own branch, `handoff/r10-pump-model-d2` (#2368), under the ruling in #201
comment 6240984157; this pull request carries no golden or stress movement.

**Round 2 (#2365 review, blocked at `b00c4a33a`).** Two repairs, both taken in
this head:
1. *mutation-vacuous*: the receiver half of D7-arch3-04 had no check of its
   own. A new check sets the plan's floor on the real `planned_draw_runs` from
   outside `pump_arbiter` and requires a floorless read to ignore it; the
   mutant that restores only the receiver's fallback now fails it.
2. *architecture*: the slot-floor registry entry called `coordinator._solve_anchor`
   "the FORECAST GRID's anchor, not the plan step's". The production text says
   otherwise -- `FORECAST_STEP_MINUTES` is "Resolution the optimizer plans at"
   and `_step_start` was "on the solver's clock" -- so it was one concern on two
   width sources, agreeing only while the two were equal. Taken: the sounder
   fix (`fixer.md` step 17), one owner. The rejected alternative, an honest
   twin entry plus a check that the two widths are one constant, keeps two
   spellings of one concept and pins their agreement instead of removing the
   second; one owner was possible because a leaf module both can import
   exists without `pump_arbiter` importing `coordinator`.
   Also corrected: `_step_start` had two readers (the ledger row at `_observe`
   and the silent-window lookup at `_inside_silent`), not three; `step_duty`
   indexes the plan by `bisect`.

**D7-arch3-04** (#2232, hygiene, class N-shared-config).
`pump_arbiter.step_duty` handed the plan's `duty_floor_kw` to
`thermal_model.planned_draw_runs` by setting a `modulation_floor` attribute on
the function object, cleared by a `@_release_duty_floor` decorator's `finally`.
One module-level slot for a per-plan value: every caller that passed no floor
read whichever plan last wrote. The catch-up verifier measured no production
reader off the loop (`in_optimize_floorless` 0 over 50 solves, `off_main_thread`
0), so this is the channel and not a live race; the fix is the argument list,
and the attribute, the decorator and the reader's fallback are gone rather than
defaulted -- each half now pinned on its own.

**D7-s3-8x-slotfloor** (#2238, hygiene, class P2). The plan step covering now
is one concern: the optimizer plans at it, every forecast series is resampled
to it, the solve's anchor labels it, and the pump arbiter keys its ledger row
and its silent-window lookup on it. It was spelled three times --
`coordinator._solve_anchor` on `FORECAST_STEP_MINUTES`,
`pump_arbiter._step_start` on a literal 15, and `pump_arbiter._observe` inline.
A new leaf module, `custom_components/heatpump_optimizer/plan_step.py`, owns
`PLAN_STEP_MINUTES` and `plan_step_start`; `coordinator.py` and
`pump_arbiter.py` import it, and `_solve_anchor`, `_step_start` and
`FORECAST_STEP_MINUTES` are gone. `pump_arbiter`'s other plan-step widths read
the same constant: the 0.25 h step and the 7 x 96-step week it hands
`quiet_windows.step_actions`, and `step_duty`'s 15-minute expiry of the plan's
last step. `LOG_STEPS = 96` stays a literal: it is the ledger's retention count,
not a width.

The slot-floor fact is registered in `tests/entities.py`'s P2 owners block with
one owner, `plan_step.py::plan_step_start`, and a planted sibling. The census
behind it is landed and re-runnable: `dev/audit/harnesses/r10_slot_floor_twins.py`
drives every seam its rule returns, drives the arbiter's ledger row as the
floor's reader, refuses a seam it has not classified, and gains a `--widen` arm
that widens the tree's one width source to 30 minutes.

## Head

`791fdba93`, the code head every figure below was taken at, against the merge
base `e5f7e169d` (`origin/main`). `custom_components/`, `tests/features.py` and
`tests/entities.py` are byte-identical between `6e5753a4a` and `e5f7e169d`, so a
`git archive 6e5753a4a` export is the merge base's production tree; the
previous head `b00c4a33a` is cited where an arm needs the tree this round
repairs. This head merges `origin/main` at `a8786ce08`; main's side moved only
`dev/programme/` records.

## Mutation proof

Each mutant ran in its own `git archive` export of the head; the worktree was
never mutated. Block command: `python3 tools/audit/seat/features_block.py
"R10-PUMP-MODEL -- the duty floor channel, the step-start fold"`, which prints
`ALL 5 FEATURES BLOCK PASSED` at the head.

**D7-arch3-04, the receiver alone** (m2: `thermal_model.py` at the merge base,
its `getattr` fallback back, the sender still fixed): `1 of 5 FEATURES BLOCK
FAILED`:

    FAIL D7-arch3-04: the reader has no channel -- a floor set on
      planned_draw_runs from outside pump_arbiter does not reach a floorless
      read  [floorless read with the attribute set: False; the same draw
      against the floor passed as the argument: False]

**D7-arch3-04, both halves** (m1: `pump_arbiter.py` and `thermal_model.py`
both at the merge base): `4 of 5 FEATURES BLOCK FAILED` -- all three
D7-arch3-04 checks (`floorless reads [False, False], duty 'idle'`; `setattr
sites [352, 326] ... decorator True`; the receiver check above), and the widen
check, because the merge base's `pump_arbiter` keys its ledger on its own 15.

**D7-s3-8x-slotfloor, a width of the arbiter's own** (m5: `_observe`'s ledger
start back to `now.replace(minute=now.minute - now.minute % 15, ...)`): the
block fails `the arbiter's ledger step and the solve's anchor are one function
on one width -- widened to 30 minutes, both read the 30-minute step
[(ledger, anchor, 30-min floor) minutes: [(15, 0, 0), (45, 30, 30)]]`, and
`PYTHONPATH=tests/hastub python3 tests/entities.py` fails `P2 owners:
slot_floor_rule ... [SEAM ['pump_arbiter.py:877 in _observe'] ...]` with the
planted-sibling null-control check beside it.

**D7-s3-8x-slotfloor, a width of the anchor's own** (m6: `coordinator.py`
defines its own `plan_step_start` on a literal 15 after the import): the block
fails the same check (`[(0, 15, 0), (30, 45, 30)]`), and `tests/entities.py`
fails `the solve anchor is plan_step.plan_step_start, outside the coordinator
class and its module, and the coordinator reads that one function [module=False
class=False same=False]` and `P2 owners: slot_floor_rule ... [SEAM
['coordinator.py:261 in plan_step_start'] ...]`.

The unmutated export (M0) fails none of these lines.

## Null control

- **The receiver check** carries its positive arm: the same 0.5 kW draw against
  the floor passed as the argument reads `False`, so the floorless `True` is
  the channel's absence and not a reader that always answers `True`.
- **The widen check** compares against an independent 30-minute floor computed
  in the check, and the shipped 15-minute width is restored in a `finally`.
- **The census**: `--identity` (the owner against itself) reads 0 of 10;
  `--perturb` (the metering window's fold restore dropped) reads 2 of 10 at
  every tree; `--widen` is the review's perturbation and reads the defect at
  the base and not at the head (Figures).
- **The ledger comparison** over 24686 instants reads 0 disagreeing against
  `plan_step_start`, with the 30-minute reference disagreeing on exactly the
  12344 it must.
- **The P2 plant**: `slot_floor_rule`'s planted sibling fails its own fact and
  no other at the head.

## Figures

The round-10 finder harnesses are out of the tree (`fixer.md` step 3); each ran
from a `git archive` export with cwd the export, `$EXPORT` naming the export of
the merge base (`6e5753a4a`'s production tree).

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_slot_floor_twins.py
  --root <tree>`, with `--widen`, `--perturb` and `--identity`:
  - merge base: `seams=6 driven=5 disagreeing_probes=0` of 10; `--widen`
    `disagreeing_probes=3` (`autumn 02:59:59.9 fold1`, `12:15 edge`,
    `23:59:59.999`);
  - previous head `03bffee33` (production identical to `b00c4a33a`): `seams=5
    folded_seams=1 driven=4 disagreeing_probes=0`; `--widen` 3 of 10, the same
    three probes;
  - this head: `seams=4 folded_seams=3` (`coordinator._solve_anchor`,
    `pump_arbiter._observe`, `pump_arbiter._step_start`) `driven=3
    disagreeing_probes=0 unclassified_seams=0`; `--widen` 0 of 10; `--perturb`
    2 of 10 (`autumn 02:07 fold1`, `autumn 02:59:59.9 fold1`); `--identity`
    `driven=2` 0 of 10.
- D7-s3-8x-slotfloor, `$EXPORT/dev/audit/rounds/round10/D7/arch2-s3/shape_slot_floor.py`
  @ sha1 `a21a0766c7c657a1e5181ba18f4cc9274a227128` (placed in each export from
  `1d1974df4`, the commit that added it; in neither tree): `implementations=4`
  at the merge base, `3` at `03bffee33`, `2` at this head (`plan_step.plan_step_start`
  and `tariff._window_slot`). Its driving arm calls `coordinator._solve_anchor`
  by name and raises `AttributeError` at this head, where that seam is folded;
  the landed census above is the companion that drives at both ends.
- D7-arch3-04, `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py`,
  `PYTHONPATH=tests/hastub python3 <harness>`: merge base `leaked_reads=140281`
  of `reader_calls=379083`, `null_leaked_reads=0`,
  `reflective_writes_pump_arbiter=2`; this head `leaked_reads=0` of `1433735`,
  `null_leaked_reads=0`, `reflective_writes_pump_arbiter=0` (`load1` 153.09).
  The count is a race, so the claim is > 0 against = 0, not its size.
- Scope, `python3 tests/closure.py select --diff e5f7e169d`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out` over 21 changed files. Run
  here: `PYTHONPATH=tests/hastub python3 tests/features.py` `ALL 4160 FEATURE
  CHECKS PASSED`; `tests/entities.py` `ALL 2347 ENTITY CHECKS PASSED`; `tests/doc_claims.py`
  `ALL 169 checks PASSED`; `tests/guard_pins.py` `ALL 50 GUARD PIN CHECKS
  PASSED`. `tests/dst_checks.py` prints `8 of 134 DST / QUARTER-GRID CHECKS
  FAILED` here and the identical FAIL set at `b00c4a33a` (`diff` of the two
  FAIL lists is empty), where CI's run was green: this machine's, not this
  diff's; CI's run is the figure. The heavy scoped scripts are CI's.
- `python3 tools/pr/ci_predict.py --base e5f7e169d`: `CI PREDICT: no closures or fast red predicted against e5f7e169d64b`, and `4 unpinned site(s) the diff adds` (`## Unpinned sites`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff e5f7e169d`: `Architecture score: dS +0.0000 NULL`, gate-only tripwire `reflective_writes 17 -> 15`;
  `--diff b00c4a33a`: `Architecture score: dS +0.0000 NULL`.

## Red checks

`none` on `b00c4a33a`'s check-runs (the reviewer's reading: 30 success, 15
skipped, 0 failed). This head's are CI's.

## Forward-carry

`none` -- nothing here narrows a later stage's technique, invalidates a figure it rests on, or removes an option it expected: both findings are closed in their own group, and the D2 branch merges this head before it moves.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds; `python3 tools/pr/ci_predict.py`
names four, each left for `mutation-autofix` to pin from CI's
mutation drive (`ci-autofix.md`), the lane that drives the killing scripts --
none is triaged here:
- `custom_components/heatpump_optimizer/plan_step.py:41 RETURN_DEL`:
  `plan_step_start`'s return, the new owner's one line; `tests/features.py`'s
  ledger and widen checks read its value;
- `custom_components/heatpump_optimizer/pump_arbiter.py:340 BOOLOP`,
- `custom_components/heatpump_optimizer/pump_arbiter.py:340 CMP_BOUND*2` and
- `custom_components/heatpump_optimizer/pump_arbiter.py:340 GUARD_OFF`:
  `step_duty`'s expiry of the plan's last step, whose text now reads
  `PLAN_STEP_MINUTES`; the arbiter section of `tests/features.py` killed the
  BOOLOP and GUARD_OFF mutants of the same line under its old text.

Three ledger rows are dropped because their lines are gone or
rewritten: `_step_start RETURN_DEL 623e1957` (the function is folded into
`plan_step_start`) and `step_duty BOOLOP 0d0efb52` / `GUARD_OFF 0d0efb52`
(the expiry line now reads `PLAN_STEP_MINUTES`). Their sites are among the four above.

## Friction

- `dev/governance/roles/fixer.md: cost: a fold that deletes a seam by name breaks every finder harness that drives that name (shape_slot_floor.py, catchup v2_s3.py's 82 arm), so the before/after reading of the finder's own instrument exists only for its count arm; the landed census had to learn to read each tree's own names.`
- `dev/governance/rules/finding-propagation.md: stale: catchup/arch-b/v2_s3.py imports tariff._plateau_aware_day_max, which R10-TARIFF folded, and its 82 arm calls pump_arbiter._step_start, which this head folds.`
