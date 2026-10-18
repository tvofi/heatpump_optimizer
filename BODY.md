Round 10, group `R10-PUMP-MODEL`: what channel the plan's modulation floor
travels on, and where a datetime's step start is computed -- plus the P2 rule
that holds the second. Part of #2232 and Part of #2238.

The group's third finding, **D2-s2-01** (one hot-water lift law), is **not in
this branch**. The owner-side ruling on it (#201 comment 6240984157, under
mandate 6175172275) accepts the fix and returns four steps to this seat; it
follows as its own branch, `handoff/r10-pump-model-d2`, cut from this head, so
this pull request carries no golden or stress movement.

**D7-arch3-04** (#2232, hygiene, class N-shared-config).
`pump_arbiter.step_duty` handed the plan's `duty_floor_kw` to
`thermal_model.planned_draw_runs` by setting a `modulation_floor` attribute on
the function object, cleared by a `@_release_duty_floor` decorator's `finally`.
One module-level slot for a per-plan value: every caller that passed no floor
read whichever plan last wrote. The catch-up verifier measured no production
reader off the loop (`in_optimize_floorless` 0 over 50 solves, `off_main_thread`
0), so this is the channel and not a live race; the fix is the argument list,
and the attribute, the decorator and the reader's fallback are gone rather than
defaulted.

**D7-s3-8x-slotfloor** (#2238, hygiene, class P2). `pump_arbiter._observe`
spelled the 15-minute step start inline, byte for byte the expression
`_step_start` already owns -- the ledger row, the silent-window lookup and the
plan's step index all read that one. Folded.

The slot-floor fact is registered in `tests/entities.py`'s P2 owners block with
a planted sibling, and the seam rule behind it is landed and re-runnable:
`dev/audit/harnesses/r10_slot_floor_twins.py` drives every seam its rule returns
and refuses one it has not classified.

**Merge with main.** `c4304bb1f` was cut from `92accb2cf`; `origin/main` was
merged in at `6e5753a4a`. Its one conflict, `tests/features.py`, was resolved by
union: main's R10-FEEDS and #2239 blocks sit ahead of this branch's
`R10-PUMP-MODEL` section, so main's checks stay in the section they ran in on
main. Read back: every line of main's `tests/features.py` is in the merged file
(`diff <(sort main) <(sort merged) | grep -c '^<'` = 0), the only lines of this
branch's side absent are exactly the 56 that main itself removed from the base
(the two sets compared equal by `diff`), and `R.check(` counts 3747 at the base,
3750 here, 3764 on main, 3767 merged (3747 + 3 + 17).

## Head

`03bffee33`, the merge commit every figure below was taken at, against the
merge base `6e5753a4a` (`origin/main`'s tip was `bad6f7a51` at 2026-10-17 22:29
UTC, which moves only record files this diff does not touch; no figure here is
a function of main's tip). `thermal_model.py` is byte-identical at `6e5753a4a`
and at the findings' baselines, and `pump_arbiter.py`'s two touched seams are
unchanged since `554e2ecfa`, so each "before" arm is the tree the finding was
measured on.

## Mutation proof

Delete each fix's production half, re-run the check that pins it, restore. Each
mutant ran in its own `git archive 03bffee33` export, so the worktree was never
mutated.

**D7-arch3-04.** The channel has two halves -- `pump_arbiter`'s sender (the
`setattr`, the decorator, the two calls without the argument) and
`thermal_model`'s receiver (the `getattr` fallback). Both files restored to
`6e5753a4a` in the export; `python3 tools/audit/seat/features_block.py
"R10-PUMP-MODEL -- the duty floor channel, the step-start fold"` prints
`2 of 3 FEATURES BLOCK FAILED`:

    FAIL D7-arch3-04: the plan's floor reaches planned_draw_runs as an argument --
      a floorless reader is unaffected while step_duty runs  [floorless reads
      [False, False], duty 'idle']
    FAIL D7-arch3-04: no module-state floor is left behind -- no setattr names it,
      and the reader carries no such attribute, so a raise between the reads has
      nothing to leave set  [setattr sites [352, 326], attr '<absent>',
      decorator True]

At the head the same block prints `ALL 3 FEATURES BLOCK PASSED`.

**D7-s3-8x-slotfloor.** Line 879 of `_observe` put back to the inline
`now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)`.
`PYTHONPATH=tests/hastub python3 tests/entities.py` fails:

    FAIL P2 owners: slot_floor_rule is decided only by its owner or a
      dispositioned site, its owner exists, no disposition is stale, the rule is
      live  [SEAM ['pump_arbiter.py:879 in _observe'] OWNER-MISSING []
      STALE-DISPOSITION [] DEAD-RULE False (hits=7)]

and the planted-sibling null-control check fails with it (every fact's plant now
also trips `slot_floor_rule`). `r10_slot_floor_twins.py` on the mutant reads
`seams=6 folded_seams=0 driven=4`. The export also fails git- and
handover-dependent checks (no `.git` in an archive); the unmutated export (M0)
fails those same checks and neither `slot_floor_rule` line, so the two above are
the mutant's.

## Null control

- **D7-arch3-04.** The spy that reads for a floorless caller forwards the
  attribute writes it sees, so the reading is the production channel's; the
  check's `duty == "idle"` arm is the positive control that the plan's floor
  still reaches the reader at the head. The finder's harness carries its own
  null arm, `null_leaked_reads=0`, at both ends.
- **D7-s3-8x-slotfloor.** The census drives the owner against itself
  (`--identity`); the ledger comparison is driven over 24686 instants at both
  ends and reads 0 disagreeing, with the 30-minute reference disagreeing on
  12344 of 24686, so the comparison discriminates.
- **The P2 plant.** `slot_floor_rule`'s planted sibling in `tests/entities.py`'s
  null-control check fails its own fact and no other at the head.

## Figures

Each line names its instrument. The round-10 finder harnesses are out of the
tree (`fixer.md` step 3); each ran from a `git archive` export of the base
(`6e5753a4a`) and of the head (`03bffee33`), with cwd the export.

- D7-arch3-04, `dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py`
  (present at `6e5753a4a`), `PYTHONPATH=tests/hastub python3 <harness>`: base
  `leaked_reads=140281` of `reader_calls=379083`, `null_leaked_reads=0`,
  `reflective_writes_pump_arbiter=2`; head `leaked_reads=0` of `465296`,
  `null_leaked_reads=0`, `reflective_writes_pump_arbiter=0`. The count is a
  race, so the claim is > 0 against = 0, not its size (`load1` 93.20 / 95.76,
  `thread_factor` 1.008 / 1.005).
- D7-s3-8x-slotfloor, `$EXPORT/dev/audit/rounds/round10/D7/arch2-s3/shape_slot_floor.py`
  @ sha1 `a21a0766c7c657a1e5181ba18f4cc9274a227128` (`$EXPORT` is the export
  above, with the harness placed at that path from the commit that added it,
  `1d1974df4`; it is in neither tree),
  `PYTHONPATH=tests/hastub python3 <harness> --root <export>`: base
  `implementations=4 driven=3 disagreeing_probes=0` of 10, `--perturb` 2 of 10;
  head `implementations=3 driven=3 disagreeing_probes=0`, `--perturb` 2 of 10.
  The inline copy is the seam this diff folds, so the census reads the defect at
  the base and not at the head -- the companion `fixer.md` step 3 asks for where
  a fold leaves the driven comparison flat.
- The finder's V2 arm for the fold, a scratch extraction of the `s3_82` arm of
  `dev/audit/rounds/round10/catchup/arch-b/v2_s3.py` @ sha1
  `15a8d534344df9ecaebce2e92282f7da721be2d5` (that file's other arms import
  tariff twins R10-TARIFF folded): `s3_82_floor_disagree=0` of 24686 at both
  ends, `--perturb` 12344 of 24686 at both ends. The fold moves no leaf.
- `python3 dev/audit/harnesses/r10_slot_floor_twins.py` at the head: `seams=5
  folded_seams=1 driven=3 disagreeing_probes=0` of 10, `unclassified_seams=0`;
  `--perturb` (the fold dropped from `_window_slot`): `disagreeing_probes=2` of 10
  (`autumn 02:07 fold1`, `autumn 02:59:59.9 fold1`); `--identity` (the owner
  against itself): `driven=2 disagreeing_probes=0` of 10. On the mutant above:
  `seams=6 folded_seams=0 driven=4`.
- Scope, `python3 tests/closure.py select --diff 6e5753a4a`: `MODE: SCOPED -- 27
  script(s) run, 6 scoped out` over 12 changed files. Run here:
  `PYTHONPATH=tests/hastub python3 tests/features.py` `ALL 4158 FEATURE CHECKS
  PASSED`; `tests/entities.py` `ALL 2347 ENTITY CHECKS PASSED`; `tests/guard_pins.py` `ALL 50 GUARD PIN CHECKS PASSED`;
  `tests/doc_claims.py` `ALL 169 checks PASSED`; `tests/closure.py selftest`
  `ALL 115 closure shrink pins PASSED`; `tests/env_drift.py` `NO UNCLAIMED
  DRIFT: 5 scenario(s) checked against origin/main` and `NO STALE FIXTURE`.
  `tests/harness_headers.py` printed `12 of 109 HARNESS HEADER CHECKS FAILED`
  here, every one `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`
  with `printed=None`: the script's 900 s wall bound expired at host `load1`
  above 370, and a wall overrun returns no stdout. Run alone at this head
  (`PYTHONPATH=tests/hastub` and the three BLAS pins `run_bounded` sets), the
  same harness printed 11 RESULT values, each equal to its header
  (`shipped_presets_armed=3`, `shipped_presets_gate_named=0`,
  `unridged_fitted_typical_s001=0` among them), in `real 711.21` / `user
  191.19` at `load1=374.05` -- under its 480 CPU-s bound. CI's
  `harness_headers.py` run is the figure.
  The heavy scoped scripts (`stress.py`, `optimality.py`, `golden.py`,
  `backtest.py` and the rest of `scope.run`) are CI's; this pull request's
  check-runs are their figures.
- `python3 tools/pr/ci_predict.py --base 6e5753a4a`: `CI PREDICT: no closures
  or fast red predicted against 6e5753a4aca8`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 6e5753a4a`: `Architecture
  score: dS +0.0000 NULL`, gate-only tripwire `reflective_writes 17 -> 15` (the
  two `setattr` sites and the decorator).

## Red checks

`none` on this branch so far.

## Forward-carry

`none` -- nothing here narrows a later stage's technique, invalidates a figure it rests on, or removes an option it expected: both findings are closed in their own group, and D2-s2-01's ruling is carried by its own branch.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds. The four `step_duty` sites (BOOLOP
and CMP_BOUND at both call sites) were pinned by `python3
tests/mutation_table.py --pin-killed` before the merge, each killed by
`tests/features.py`; main touches neither `pump_arbiter.py` nor those ledger
rows, so the merge moved no pin. A local `--scope changed` re-run here was
`MUTATION TABLE INCONCLUSIVE` (its baseline timed out in `tests/env_drift.py`
under host load), so the ledger's verdict at this head is CI's mutation check.

## Friction

- `dev/governance/rules/finding-propagation.md: stale: catchup/arch-b/v2_s3.py,
  the catch-up verifier's own V2 file for D7-s3-81/82/83, imports
  tariff._plateau_aware_day_max, which the R10-TARIFF merge folded; the file
  raises AttributeError before its s3_82 arm, so the arm this finding needs was
  extracted into scratch and is cited by sha1 above.`
- `dev/governance/roles/fixer.md: cost: the round-10 finder harnesses that are
  not in the tree (shape_slot_floor.py) must be recovered from the commit that
  added them before they can be re-run at a new merge base; a resumed seat has
  no other copy.`
