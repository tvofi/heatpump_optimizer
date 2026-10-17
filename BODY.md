Round 10, group `R10-PUMP-MODEL`: what channel the plan's modulation floor
travels on, and where a datetime's step start is computed -- plus the P2 rule
that holds the second. Part of #2232 and Part of #2238.

The group's third finding, **D2-s2-01** (one hot-water lift law), is **not in
this branch**. It is held on `handoff/r10-pump-model-d2` at `e1eca9bfa`, with
its own body at `handoff-body/r10-pump-model-d2` and its full measurement,
because its blast radius -- 41 of 56 golden fixtures and 36 of 54 stress
scenarios, all claimed and all one direction -- is refused by two guards:
`tests/optimality.py`'s ftol arm, whose fixture no longer clears its own 2.5%
bound on an honest tree (production's ftol is untouched), and
`tests/stress.py`'s solver-work floors. Neither guard may be re-anchored to fit
a diff: the first needs the four-kernel matrix its bound was derived on, and
the second's own floor-override path requires a ruling that does not exist for
this change. `prepr.sh` refuses a handoff on the `optimality.py` red, so that
branch is a record for the orchestrator's ruling, not a pull request this seat
opens.

**D7-arch3-04** (#2232, hygiene, class N-shared-config).
`pump_arbiter.step_duty` handed the plan's `duty_floor_kw` to
`thermal_model.planned_draw_runs` by setting a `modulation_floor` attribute on
the function object, cleared by a `@_release_duty_floor` decorator's `finally`.
One module-level slot for a per-plan value: every caller that passed no floor
read whichever plan last wrote. The catch-up verifier measured no production
reader off the loop (`in_optimize_floorless` 0 over 50 solves, `off_main_thread`
0, both floorless readers on the loop), so this is the channel and not a live
race; the fix is the argument list, and the attribute, the decorator and the
reader's fallback are gone rather than defaulted.

**D7-s3-8x-slotfloor** (#2238, hygiene, class P2). `pump_arbiter._observe`
spelled the 15-minute step start inline, byte for byte the expression
`_step_start` already owns -- the ledger row, the silent-window lookup and the
plan's step index all read that one. Folded.

The slot-floor fact is registered in `tests/entities.py`'s owners block with a
planted sibling, and the seam rule behind it is landed and re-runnable:
`dev/audit/harnesses/r10_slot_floor_twins.py` drives every seam its rule returns
and refuses one it has not classified.

## Head

`c4304bb1f`, the code head every figure below was taken at, against the merge
base `92accb2cf` (`origin/main`'s tip was `d7b171229` at 2026-10-16 23:31 UTC;
no figure here is a function of main's tip). `thermal_model.py` is
byte-identical at `92accb2cf` and at the findings' own baselines `554e2ecfa` and
`17f1c55fad1b`, and `pump_arbiter.py`'s two touched seams are unchanged since
`554e2ecfa` (the file carries an unrelated refactor from another group since),
so each "before" arm below is the tree the finding was measured on.

## Mutation proof

Delete each fix's production half, re-run the check that pins it, restore.

**D7-arch3-04.** The channel has two halves -- `pump_arbiter`'s sender
(`setattr(planned_draw_runs, "modulation_floor", ...)`, the decorator, and the
two calls without the argument) and `thermal_model`'s receiver (the
`getattr(planned_draw_runs, ...)` fallback). `git checkout 92accb2cf --` both
files and the two D7-arch3-04 checks fail:

    FAIL D7-arch3-04: the plan's floor reaches planned_draw_runs as an argument --
      a floorless reader is unaffected while step_duty runs  [floorless reads
      [False, False], duty 'idle']
    FAIL D7-arch3-04: no module-state floor is left behind -- no setattr names it,
      and the reader carries no such attribute, so a raise between the reads has
      nothing to leave set  [setattr sites [352, 326], attr '<absent>',
      decorator True]

Command: `python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- the duty
floor channel, the step-start fold"`. At the head the same block is 3 of 3
green. One half alone is NOT a mutant: with the sender restored and the
receiver's fallback gone -- the state a half-reverted tree is in -- the floorless
read stays `True` and `step_duty` reads the 1.0 kW space step as `space`, which
is what the first run of this proof showed before the receiver was restored too.

**D7-s3-8x-slotfloor.** Put the inline expression back in `_observe`
(`start = now.replace(minute=now.minute - now.minute % 15, second=0,
microsecond=0)`). `tests/entities.py` fails:

    FAIL P2 owners: slot_floor_rule is decided only by its owner or a
      dispositioned site, its owner exists, no disposition is stale, the rule is
      live  [SEAM ['pump_arbiter.py:879 in _observe'] OWNER-MISSING []
      STALE-DISPOSITION [] DEAD-RULE False (hits=7)]

and `dev/audit/harnesses/r10_slot_floor_twins.py` reports the folded seam back
(`seams=6`, `folded_seams=0`, `driven=4`), which is the baseline's own reading.

## Null control

- **D7-arch3-04.** The spy that reads for a floorless caller forwards the
  attribute writes it sees, so the reading is the production channel's; the
  same check's `duty == "idle"` arm is the positive control that the plan's
  floor still reaches the reader at the head. The finder's own harness reads
  `leaked_reads=377352` of `1111275` at the baseline against `0` of `1128820` at
  the head, with its own null arm (`null_leaked_reads=0`) in both, and the
  pin drive's `NULL_COMMENT` control survived every driver.
- **D7-s3-8x-slotfloor.** The census drives the owner against itself
  (`--identity`) and reads 0 of 10; the ledger comparison is driven over 24686
  instants at both ends and reads 0 of 24686, with the 30-minute reference
  agreeing on exactly the instants it must (12344 of 24686 disagree), so the
  comparison discriminates.
- **The P2 plant.** `slot_floor_rule`'s planted sibling in `tests/entities.py`'s
  null-control check -- a new minute-floor -- fails its own fact and no other.

## Figures

Each line names its instrument; the round-10 harnesses are out of the tree
(`fixer.md` step 3), so they are cited as `$EXPORT/<path> @ <sha1>` where
`$EXPORT` is a `git archive 92accb2cf` export.

- D7-arch3-04, `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py`
  @ `5e4cf76785cb79ffda0c4035f0fe65b437aa2c8d`, `PYTHONPATH=tests/hastub python3
  <harness>`: baseline `leaked_reads=377352` of `reader_calls=1111275`,
  `null_leaked_reads=0`, `reflective_writes_pump_arbiter=2`; head
  `leaked_reads=0` of `1128820`, `null_leaked_reads=0`,
  `reflective_writes_pump_arbiter=0`. The count is a race: the claim is > 0
  against = 0, not the size (load1 48.56 / 25.96, `thread_factor` 1.001 both).
- D7-s3-8x-slotfloor, `$EXPORT/dev/audit/rounds/round10/D7/arch2-s3/shape_slot_floor.py`
  @ `a21a0766c7c657a1e5181ba18f4cc9274a227128`, `python3 <harness> --root <tree>`:
  baseline `implementations=4` (`coordinator._solve_anchor`, two `pump_arbiter`
  sites -- `_step_start` and `_observe`'s inline copy -- `tariff._window_slot`),
  `driven=3`, `disagreeing_probes=0` of 10, `--perturb 2`; head
  `implementations=3`, `disagreeing_probes=0`, `--perturb 2`. The inline copy is
  the seam this diff folds, so the census reads the defect at the baseline and
  not at the head -- the companion `fixer.md` step 3 asks for where the folded
  seam leaves the driven comparison flat.
- `python3 dev/audit/harnesses/r10_slot_floor_twins.py` (and `--perturb`,
  `--identity`): baseline `seams=6 folded_seams=0 driven=4 disagreeing_probes=0`
  of 10, `unclassified_seams=0`; head `seams=5 folded_seams=1` (names
  `pump_arbiter._observe`) `driven=3 disagreeing_probes=0 unclassified_seams=0`.
  `--perturb` (the fold dropped from `_window_slot`) reads 2 of 10 at both ends;
  `--identity` (the owner against itself) 0 of 10. The two seams it does not
  drive are its registry's own dispositions, each named with its reason and
  refused by the harness if it is neither driven nor exempt.
- A scratch extraction of the finder's V2 arm for the fold @
  `15a8d534344df9ecaebce2e92282f7da721be2d5` (the `s3_82` arm of
  `dev/audit/rounds/round10/catchup/arch-b/v2_s3.py`, whose other two arms
  import tariff twins R10-TARIFF has since folded, so the file no longer
  reaches its own arm): `s3_82_floor_disagree=0` of 24686 at both ends, and
  12344 of 24686 against the 30-minute reference. The fold moves no leaf, which
  is the finding's "no behavioural consequence".
- The scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=92accb2cf
  ./tests/run.sh`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out` over its 11
  changed files, and `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`. The
  two lanes the held branch reddens are green here: `ALL 84 OPTIMALITY CHECKS
  PASSED`, `ALL 110 STRESS CHECKS PASSED`.
- `python3 tools/pr/ci_predict.py --base 92accb2cf`: `CI PREDICT: no
  closures or fast red predicted` -- after `tests/closures.json` lists the new
  harness in `harness_headers.py`'s `inert_reads` by hand, as the harness that
  reads every harness header (`--single` does not clear an inert read; the
  R10-REGISTRY-LEAK precedent). That one-line data edit came after the scoped
  run above, so the checks that read it were re-run: `python3 tests/entities.py`
  `ALL 2332 ENTITY CHECKS PASSED`, `python3 tests/harness_headers.py` `ALL 109
  HARNESS HEADER CHECKS PASSED`, `python3 tests/closure.py selftest` `ALL 115
  closure shrink pins PASSED`, and the scope re-derived still reads `MODE:
  SCOPED -- 27 script(s) run`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no budget moved;
  the diff removes lines from both production modules).
- `python3 tools/audit/archscore/score.py --diff 92accb2cf`: `dS +0.0000 NULL`,
  and the gate-only tripwire `reflective_writes 17 -> 15` (the two `setattr`
  sites and the decorator). No score metric rises, so there is nothing to
  explain under `## Architecture score`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4141 FEATURE CHECKS
  PASSED`. `python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- the
  duty floor channel, the step-start fold"`: `ALL 3 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2332 ENTITY CHECKS
  PASSED`, including `P2 owners: slot_floor_rule ...` and the null-control
  check that each P2 fact fails on its planted sibling and on no other.
- `python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`: the class
  census the P2 entry's shape comes from reads `F3_cop_law_fork=3` here, the
  same three seams as the merge base -- its `compute_cop_dhw` seam is the one
  the held branch closes, and that branch's body carries the 3 -> 2 reading
  with its `--perturb` control.

## Red checks

`none`. The two guards the group's third finding reddens are on the held
branch, and they are stated there in full.

## Forward-carry

`none` -- nothing here narrows a later stage's technique, invalidates a figure it rests on, or removes an option it expected: both findings are closed in their own group, and the only remaining moved surface is the mutation ledger, which belongs to this diff.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds. Four sites, all pinned and none
left: `python3 tests/mutation_table.py --pin-killed --base 92accb2cf` printed
`PIN KILLED: 5 pinned, 0 left unpinned` on the branch that held all three
findings -- five rows, of which this branch keeps four (its fifth pinned
`compute_cop_dhw`'s return, a line only the held branch adds) -- each killed by
`tests/features.py` (`step_duty` BOOLOP and CMP_BOUND at both call sites, which
the short-schedule and duty fixtures exercise).
`python3 tests/mutation_table.py --scope changed --base 92accb2cf` then printed
`4396 unpinned site(s) of 6134 candidate sites, 4398 at the ratchet base ...;
the ledger agrees with the deterministic inventory`.

## Friction

- `dev/governance/rules/finding-propagation.md: stale: catchup/arch-b/v2_s3.py,
  the catch-up verifier's own V2 file for D7-s3-81/82/83, imports
  tariff._plateau_aware_day_max, which the R10-TARIFF merge folded; the file now
  raises AttributeError before its s3_82 arm, so the arm this finding needs was
  extracted into scratch and is cited by sha1 above.`
- `dev/governance/rules/fixer.md: cost: a fix's blast radius can refuse the
  handoff itself (prepr.sh refuses on the optimality.py red the held branch
  carries), and the only in-scope repair left is to re-anchor a guard's fixture
  -- which this contract forbids. The group therefore hands off in two parts,
  and the held part waits on an owner ruling recorded nowhere as a rule.`
- `dev/governance/rules/finding-propagation.md: unclear: the group's third
  finding is a *sibling seam in the stage that is running*, whose destination by
  that rule is "a new issue filed by the same pull request" -- but every GitHub
  write here is the orchestrator's, so the seat can only hand it over as a
  second ref.`
