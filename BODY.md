Round 10, group `R10-PUMP-MODEL`: three findings on one subsystem -- what the
model charges for a hot-water tank, what channel the plan's modulation floor
travels on, and where a datetime's step start is computed. Part of #2238 and
Part of #2232.

**D2-s2-01** (#2238, low, class P2). `ThermalModel.compute_cop_dhw` took its law
from the space circuit's valve flag. With `cop_flow_carnot` the tank paid
`_cop_law`'s Carnot lift at its own water temperature; without it, a linear
0.008/K penalty floored at 0.5 with no upper bound. The flag is a space-circuit
fact -- it decides whether a passed flow temperature is the supply the machine
runs at, which is what prices the buffer tank's lift -- and it has no reading on
how hard a hot-water tank is to heat. The same tank at the same outdoor was
priced up to 1.4346 apart (7 °C outdoor, 65 °C tank), and below the 35 °C
reference flow the linear arm handed out a boost up to 1.2x that the Carnot arm
and `_batch_cop`'s own comment refuse ("a below-ref tank must not earn a COP
boost it never gets"). The tank now pays `_cop_law` at its own water
temperature on both plants: one law, one-sided, the ratio the buffer pays. The
alternative fix -- make both arms linear -- loses, and the `_cop_law` comment
says why: the linear form is the fitted %/K that "hits the floor" at storage
temperatures where a real unit still manages 1.5-2.0, and it is the arm that
grants the refused below-reference boost.

**D7-arch3-04** (#2232, hygiene, class N-shared-config).
`pump_arbiter.step_duty` handed the plan's `duty_floor_kw` to
`thermal_model.planned_draw_runs` by setting a `modulation_floor` attribute on
the function object, cleared by a `@_release_duty_floor` decorator's `finally`.
One module-level slot for a per-plan value: every caller that passed no floor
read whichever plan last wrote. The catch-up verifier measured no production
reader off the loop (`in_optimize_floorless` 0 over 50 solves, `off_main_thread`
0, both floorless readers on the loop), so this is the channel and not a live
race; the fix is the argument list, and the channel, the decorator and the
fallback are gone rather than defaulted.

**D7-s3-8x-slotfloor** (#2238, hygiene, class P2). `pump_arbiter._observe`
spelled the 15-minute step start inline, byte for byte the expression
`_step_start` already owns -- the ledger row, the silent-window lookup and the
plan's step index all read that one. Folded.

The two P2 facts are registered in `tests/entities.py`'s owners block with a
planted sibling each, and the seam rule behind them is landed and re-runnable:
`dev/audit/harnesses/r10_slot_floor_twins.py` drives every seam its rule returns
and refuses one it has not classified.

## Head

`e1eca9bfa`, the code head every figure below was taken at, against the merge
base `92accb2cf` (`origin/main`'s tip was `d7b171229` at 2026-10-16 23:31 UTC;
no figure here is a function of main's tip, and the closure's MODE line is a
function of the merge base). `thermal_model.py` is byte-identical at
`92accb2cf` and at the findings' own baselines `554e2ecfa` and `17f1c55fad1b`,
and `pump_arbiter.py`'s three touched seams are unchanged since `554e2ecfa`
(the file carries an unrelated refactor from another group since), so each
"before" arm below is the tree the finding was measured on.

## Mutation proof

Delete each fix's production line, re-run the check that pins it, restore.

**D2-s2-01.** `thermal_model.py` `ThermalModel.compute_cop_dhw`: replace the
`return self._cop_law(outdoor_temp, humidity, dhw_temp)` body with the removed
two-law body (the `cop_flow_carnot` guard plus the linear penalty). The block
fails 3 of its 4 D2 checks:

    FAIL D2-s2-01: the space-valve flag does not price the hot-water tank -- both
      plants charge one lift, over the whole outdoor/tank grid  [worst ratio 1.4346
      at outdoor=7.0 tank=65.0]
    FAIL D2-s2-01: the tank's price is _cop_law at the tank's own water temperature,
      humidity and all -- not a penalty of its own
    FAIL D2-s2-01: a tank below the reference flow earns no lift and a hot one pays
      it (the one-sided rule _batch_cop states)  [below-ref boost 1.2000 ...]

Command: `python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- DHW lift,
the duty floor channel, the step-start fold"`. At the head the same block is
7 of 7 green.

**D7-arch3-04.** The channel has two halves -- `pump_arbiter`'s sender
(`setattr(planned_draw_runs, "modulation_floor", ...)`, the decorator, and the
two calls without the argument) and `thermal_model`'s receiver (the
`getattr(planned_draw_runs, ...)` fallback). Restore both halves and the two
D7-arch3-04 checks fail, with the D2-s2-01 checks green beside them (measured on
`git checkout 92accb2cf -- <both files>` with only D2-s2-01's one-line body
re-applied, so the failures are the channel's):

    FAIL D7-arch3-04: the plan's floor reaches planned_draw_runs as an argument --
      a floorless reader is unaffected while step_duty runs  [floorless reads
      [False, False], duty 'idle']
    FAIL D7-arch3-04: no module-state floor is left behind -- no setattr names it,
      and the reader carries no such attribute, so a raise between the reads has
      nothing to leave set  [setattr sites [352, 326], attr '<absent>',
      decorator True]

(The reader's probe is a spy that stands in for a floorless caller and forwards
the attribute writes it sees, so the reading is the production channel's; `duty
'idle'` is the positive control that the floor still reaches the reader. One
half alone is NOT a mutant: with the sender restored and the receiver's fallback
gone -- the state a half-reverted tree is in -- the floorless read stays `True`
and `step_duty` reads the 1.0 kW space step as `space`, which is what the first
run of this proof showed before the receiver was restored too.)

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

- **D2-s2-01.** Two arms. (a) The same 2296-cell grid priced at the valve plant
  is bit-identical across the fix (`valve_digest` equal at both ends): the fix
  moves the arm the defect was in and nothing else. (b) The flag is not inert --
  it still prices the SPACE buffer's lift (`compute_cop(o, flow_temp=65)` is
  strictly lower on the valve plant at every probe outdoor), so check 4 of the
  block reads the flag's own fact and the identity in check 1 is not a statement
  that the flag does nothing.
- **D7-arch3-04.** The harness's own null arm (thread A idle) reads 0 leaked
  reads against the defect's 377352, and the block's `duty == "idle"` arm shows
  the plan's floor still reaches the reader.
- **D7-s3-8x-slotfloor.** The census drives the owner against itself
  (`--identity`) and reads 0 of 10; the ledger comparison is driven over 24686
  instants at both ends and reads 0 of 24686, with the 30-minute reference
  reading 12344 of 24686 -- so the comparison discriminates.
- **The P2 plants.** Each new registry entry has a planted sibling in
  `tests/entities.py`'s null-control check: a new flag-forked COP helper and a
  new minute-floor both fail their own fact and no other. The class census that
  enumerates the COP family (D14's `enumerate_p2.py`, F3) moves 3 -> 2 at the
  head and returns to 3 under its own `--perturb`.

## Figures

Each line names its instrument; the round-10 harnesses are out of the tree
(`fixer.md` step 3), so they are cited as `$EXPORT/<path> @ <sha1>` where
`$EXPORT` is a `git archive 92accb2cf` export.

**The finding's harnesses, both ends.**

- D2-s2-01, `$EXPORT/dev/audit/rounds/round10/D2/s2/cop_laws.py` @
  `675cda50526bb9313ff3a1bc7791d5dbb640917c`, `PYTHONPATH=tests/hastub python3
  <harness>` with the tree's root as cwd: baseline `dhw_mode_ratio_max=1.4346`
  (at outdoor 7.0, tank 65.0), `dhw_mode_dev_cells=41 min=0.2000 max=0.4346
  drop_max=0.4346`, `dhw_below_ref_boost_max=1.2000`; head `1.0000`, `min=0.0000
  max=0.0000`, `1.0000`. The harness's own `--perturb` arm reads `1.0000 /
  1.0000` at the baseline. Its non-findings are flat at both ends:
  `cop_outdoor_monotone_violations=0`, `cop_flow_monotone_violations=0`,
  `batch_scalar_cop_mismatch=0 of 63570` (load1 48.90 baseline / 25.17 head,
  `thread_factor` 1.000 both).
- D7-arch3-04, `$EXPORT/dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py`
  @ `5e4cf76785cb79ffda0c4035f0fe65b437aa2c8d`, `PYTHONPATH=tests/hastub python3
  <harness>`: baseline `leaked_reads=377352` of `reader_calls=1111275`,
  `null_leaked_reads=0`, `reflective_writes_pump_arbiter=2`; head
  `leaked_reads=0` of `1128820`, `null_leaked_reads=0`,
  `reflective_writes_pump_arbiter=0`. The count is a race: the claim is > 0
  against = 0, not the size (load1 48.56 / 25.96, `thread_factor` 1.001 both).
- D7-s3-8x-slotfloor, `$EXPORT/dev/audit/rounds/round10/D7/arch2-s3/shape_slot_floor.py`
  @ `a21a0766c7c657a1e5181ba18f4cc9274a227128`, `python3 <harness> --root <tree>`:
  baseline `implementations=4` (`coordinator._solve_anchor`, two
  `pump_arbiter` sites -- `_step_start` and `_observe`'s inline copy --
  `tariff._window_slot`), `driven=3`, `disagreeing_probes=0` of 10, `--perturb
  2`; head `implementations=3`, `disagreeing_probes=0`, `--perturb 2`. The
  inline copy is the seam this diff folds, so the census reads the defect at
  the baseline and not at the head -- which is the companion `fixer.md` step 3
  asks for where the folded seam leaves the driven comparison flat.

**The P2 rules, and the seams they return.**

- `python3 tests/entities.py` (`PYTHONPATH=tests/hastub`): every P2 fact green,
  including the two added here, and the null-control check that each fails on
  its planted sibling (`cop_law_fork` on a new flag-forked COP helper,
  `slot_floor_rule` on a new minute-floor) and on no other fact.
- `python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`: baseline
  `F3_cop_law_fork=3` (`compute_cop`, `compute_cop_dhw`, `_batch_cop`),
  `seams_total=78`; head `F3_cop_law_fork=2`, `seams_total=77`, both remaining
  seams the owners the registry entry names; `--perturb` at the head
  `before=2 after=3 moved=1`. Every seam the rule returns is dispositioned:
  `compute_cop`/`_batch_cop` are the registered owners, `compute_cop_dhw`'s fork
  is closed in this diff.
- `python3 dev/audit/harnesses/r10_slot_floor_twins.py` (and `--perturb`,
  `--identity`): baseline `seams=6 folded_seams=0 driven=4 disagreeing_probes=0`
  of 10, `unclassified_seams=0`; head `seams=5 folded_seams=1` (names
  `pump_arbiter._observe`) `driven=3 disagreeing_probes=0 unclassified_seams=0`.
  `--perturb` (the fold dropped from `_window_slot`) reads 2 of 10 at both
  ends; `--identity` (the owner against itself) 0 of 10. The two seams it does
  not drive are the registry's own dispositions, each named with its reason and
  refused by the harness if it is neither driven nor exempt.
- A scratch probe @ `f26517749939b35ef5aa0a25d25ce5da5178aa00` over 2296
  (outdoor, tank) cells: baseline `valve_digest=8686b22d6d1a5dd4`,
  `direct_digest=94e5189c2c6d1ce3`, `valve_is_law=2296 of 2296`,
  `direct_is_law=190 of 2296`; head `valve_digest` unchanged,
  `direct_digest=8686b22d6d1a5dd4`, `direct_is_law=2296 of 2296`. So the fix
  moves the arm the defect is in, leaves the valve arm bit-identical, and the
  190 baseline cells that did follow the law are exactly the tanks at or below
  the 35 °C reference flow where the lift is skipped (`5 tanks x 38 outdoor`).
- A scratch extraction of the finder's V2 arm for the fold @
  `15a8d534344df9ecaebce2e92282f7da721be2d5` (the `s3_82` arm of
  `dev/audit/rounds/round10/catchup/arch-b/v2_s3.py`, whose other two arms
  import tariff twins R10-TARIFF has since folded, so the file no longer
  reaches its own arm): `s3_82_floor_disagree=0` of 24686 at both ends, and
  12344 of 24686 against the 30-minute reference. The fold moves no leaf, which
  is the finding's "no behavioural consequence".

**The claims and the gate.**

- `GOLDEN_MODE=drift GOLDEN_REF=92accb2cf python3 tests/env_drift.py --all
  92accb2cf`: 41 of the 56 scenarios drift, all with the same direction
  (`baseline_cost` up on every one it appears in, `dhw_heating_cost`
  8.206833 -> 8.779495 on the same fixtures, plan keys either way);
  `winter_single_no_dhw` is byte-identical, which is the null (its scenario has
  no hot water). All 41 are claimed in `tests/golden/claimed_drift.txt`; the
  twelve of them that carry a may-drift entry have that entry suspended for
  this release, which is what the judged-key rule leaves (`baseline_cost` is a
  `MAY_DRIFT_JUDGED_KEY`, and a name cannot be both -- the R8-P3 `wood_coil`
  precedent, recorded in the file).
- `python3 tests/env_drift.py --claims-only 92accb2cf`: `claims hygiene ok`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `rc=0`, all three
  committed model figures byte-identical to the regenerated ones. The two
  regenerated files are `docs/img/model/dhw-demand-windows.svg` (the tank
  temperature line and two caption figures: lowest-inside 45.2 -> 45.1 °C,
  outside 42.4 -> 42.9 °C) and `marginal-cop.svg` (the left panel's DHW curve;
  the right panel's, drawn with `cop_flow_carnot` on, is unchanged, and the
  generator's `dhw-store-decay.svg` is byte-identical).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no budget moved;
  the diff removes lines from both production modules).
- `python3 tools/audit/archscore/score.py --diff 92accb2cf`: `dS +0.0000 NULL`,
  and the gate-only tripwire `reflective_writes 17 -> 15` (the two `setattr`
  sites and the decorator). No score metric rises, so there is nothing to
  explain under `## Architecture score`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4145 FEATURE
  CHECKS PASSED` (4138 at the baseline, all green there too -- the six the fix
  moved are re-anchored in this diff and each records its pre-fix value).
  `python3 tools/audit/seat/features_block.py "R10-PUMP-MODEL -- DHW lift, the
  duty floor channel, the step-start fold"`: `ALL 7 FEATURE CHECKS PASSED`.

## Red checks

Four checks went red on this branch. Three are the D2-s2-01 blast radius, and
two of those three name a repair a fixer may not make: a guard's fixture
re-derived (which needs the four-kernel matrix the block's bound was derived
on) and a coverage floor lowered (which needs a ruling the file says must be
cited). They are stated here rather than worked around, and this branch is
handed off instead of opened: the ask is the orchestrator's.

- **`mutation` refused the ledger** (`tests/entities.py`'s `--anchor` arm
  printed `MUTATION TABLE REFUSED`, and so did `tests/mutation_table.py` before
  any driver ran). Three dispositions named sites this diff rewrote or deleted,
  which is the ledger's design: a disposition does not outlive its line.
  `step_duty BOOLOP 296c284b` and `step_duty BOOLOP 399c5f97` pinned the two
  lines the floor argument rewrote -- re-measured and re-keyed by `--pin-killed`
  under the new anchors (`264cd0e6`, `fe0d2ae4`), which the same lines' new
  CMP_BOUND sites join. `ThermalModel.compute_cop_dhw GUARD_OFF ca964a78`
  retires with the `cop_flow_carnot` guard it pinned; its kill (the #1530
  equality, still green) is what the new D2-s2-01 checks replace.
  `planned_draw_runs`'s CMP_BOUND and GUARD_OFF rows needed nothing: the fix
  kept those two lines' text, so their anchors did not move. The cheaper
  detector: `python3 tests/mutation_table.py --scope changed --base
  <merge-base>`, source-only, printing the refusal before any driver runs
  (seconds against the lane's minutes). No new detector is owed; the check that
  exists is the cheap one and it is in the local path (`prepr.sh` step 6d).
- **`doc_claims.py` went red on its generated-figure freshness arm**
  (`dhw-demand-windows.svg` and `marginal-cop.svg` matched the regenerated
  bytes at 15769/13856 B but not byte for byte), which is also what stopped the
  mutation pin drive's baseline. The two figures draw production code --
  `marginal_cop` at the tank temperature, and the DHW planner's tank line -- so
  the fix's own law moved them; regenerating by the generator's documented
  recipe and committing the two files is the repair, with
  `dhw-store-decay.svg` byte-identical as the control that the generator
  reproduces this environment. Cheaper detector: **none** -- the freshness arm
  is the first second of `doc_claims.py`, and it is the only check that reads
  the relation between the model and `docs/img/model/`. It read green at the
  merge base in this environment, so it named this diff's own omission rather
  than a machine difference.
- **`stress.py`: two checks, both the fix's own blast radius.**
  `the production-call check covers at least 15 of 20 families [6 covered;
  re-planned: ...]` and `the solver-work check still covers most of the sweep
  [only 18 of 54 scenarios are judged, against a floor of 40: 36 were
  re-planned by this branch and 0 have no baseline solve]`. Every scenario with
  hot water re-plans, because the price of hot water changed -- the same
  population `tests/golden/claimed_drift.txt` claims (41 of 56). The check's
  own text names the answer: "a branch that re-plans this much on purpose says
  so in its PR body -- how many plans moved and why -- the way a moved fixture
  is claimed, rather than reaching for a variable that no longer exists". So:
  41 golden fixtures and 36 of the 54 stress scenarios, all by D2-s2-01, all in
  the same direction (a lower tank COP), all claimed or stated here. The
  floor's other path is a `coverage_floor_override` budget entry, which "must
  cite the ruling that sanctioned it"; the only ruling recorded there is
  #1207's, for the economics-polish re-plan, and citing it here would be a
  false citation -- so the literal 40 stands and this is the answer.
- **`optimality.py`: `the production stop rule (ftol) buys a materially better
  plan [ftol 1e-6 60.58 vs loosened 1e-2 both sites 60.96 (0.63% gap, bound
  2.5%)]`.** Production's ftol is unchanged (1e-6, `optimizer.py`'s two options
  dicts untouched); the arm is bit-identical to the file's own. What moved is
  the scenario's *sensitivity*: at the merge base the same block read
  `61.28` production against `64.97` loosened (+5.7%, the +5.04-5.74% the
  block documents across kernels), and under the one DHW law the loosened arm
  lands nearly the same plan (`60.96`). The block's own note says why the check
  lives only on this cell -- "single-zone is insensitive to ftol on this
  scenario and the dhw-off two-zone cell is non-monotone under loosening" --
  and its bound is half the smallest of four environments' measurements
  (`k1725_blas_kernel_gap.py`), which a seat here cannot re-run. Cheaper
  detector: none -- this block is the only place the stop rule is raced, and
  the guard still *fires* on a loosened production ftol (the two solves
  converge by construction); what it no longer does is clear its own bound on
  an honest tree. **This is the reason this branch is handed off rather than
  opened as a pull request**: re-deriving that fixture needs the kernel matrix,
  and a fixer may not lower the bound to fit its own diff.
- **`env_drift` reported 41 unclaimed drifts** on the first run. That is the
  fix's own blast radius and the reason the claim file exists; the second run
  with the claims is the green one above. Cheaper detector: the same script's
  `--claims-only`, which refuses a claim-file problem in about a second before
  the capture runs.

## Forward-carry

`none`.

Nothing here narrows a later stage's technique, invalidates a figure it rests
on, or removes an option it expected. The D2-s2-01 reds below are a decision for
this pull request (an owner ruling on the documented two-law design, and a
guard's fixture re-derived), not a constraint a later stage inherits: a later
group reading `docs/how-it-works.md` reads the tree it is given, and the tree
here still documents the two-law behaviour.

## Unpinned sites

`prepr.sh` step 6d lists what the diff adds. Five sites, all pinned and none
left: `python3 tests/mutation_table.py --pin-killed --base 92accb2cf` printed
`PIN KILLED: 5 pinned, 0 left unpinned`, each killed by `tests/features.py`
(`step_duty` BOOLOP and CMP_BOUND at both call sites -- the short-schedule and
duty fixtures exercise them -- and `compute_cop_dhw`'s return, which the new
D2-s2-01 checks divide by). `tests/mutation_table.py --scope changed --base
92accb2cf` then printed `4393 unpinned site(s) of 6131 candidate sites, 4398 at
the ratchet base ...; the ledger agrees with the deterministic inventory`.

## Friction

- `dev/governance/rules/finding-propagation.md: stale: catchup/arch-b/v2_s3.py, the catch-up verifier's own V2 file for D7-s3-81/82/83, imports tariff._plateau_aware_day_max, which the R10-TARIFF merge folded; the file now raises AttributeError before its s3_82 arm, so the arm this finding needs was extracted into scratch and is cited by sha1 above. The finding's own harness (shape_slot_floor.py) is unaffected.`
- `dev/governance/rules/claim-files.md: contradiction: a fixture whose baseline_cost moves cannot be claimed while it carries a may-drift entry (env_drift refuses a name that is both), and a may-drift entry cannot excuse a MAY_DRIFT_JUDGED_KEY move. The only green path is to suspend an owner-sanctioned entry for the release, which is the R8-P3 wood_coil precedent but is recorded nowhere as the rule -- twelve entries are suspended here.`
- `dev/governance/roles/fixer.md: unclear: step 3 keeps a round's dev/audit/rounds/*.py harnesses out of the tree, step 18 lands what a later seat reruns. Resolved by landing the new census under dev/audit/harnesses/ (it is what a later seat re-runs) and citing the round harnesses as $EXPORT/<path> @ <sha1>.`
