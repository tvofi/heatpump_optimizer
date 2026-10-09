The foundation for clamping the plan to metered power (#201 decision 6067353918,
under mandate 6067089637): PR 7a of the live-fix wave, built from its binding
design note. **No solve reads anything added here** -- 7b applies the clamp after
this merges -- so the change is one component, its store hosting, and the
diagnostics that surface it.

The planner books `min_electrical_power`..`max_electrical_power` as the draw a
step may run at and credits COP times that draw as delivered heat. Nothing
checked those two figures against the meter: a pump whose configured maximum is
several times its real running draw has every plan book levels the pump never
reaches, and the heat credited for them was never delivered. Synthetic shapes
throughout -- code, tests, harness, this body: configured 1-10 kW, asked U(3, 10),
drawing U(1.2, 1.8).

- **S1** `InstallCapability.plan_writes_power()` (`thermal_model.py`): the plan
  sets the compressor's draw itself only where it writes the frequency;
  everywhere else the meter reads the pump's own choice.
- **S2** `draw_range.is_running_space(...)`: the one running-sample filter over
  plain values -- a metered draw above standby (`RUNNING_FLOOR_KW = 0.25`), the
  space circuit asked and no hot water asked (both through `planned_draw_runs`,
  the plan-running rule's registered owner, with no modulation floor), the
  learners not frozen on the meter, no resistive element or capped compressor, no
  defrost in the interval just closed.
- **S3** `draw_range.DrawRange`: a window of `WINDOW = 336` `(drawn, space asked)`
  running samples; `observed()` is P10/P90 once `MIN_SAMPLES = 48` stand. The
  evidence latch `engaged` sets when a quarter of the running samples disagree by
  more than 1.25x between asked (at or above the configured floor) and drawn. It
  is keyed to the configured `(min, max)` it judged: a changed configuration
  clears samples and latch, and a stored record whose configuration is unreadable,
  absent or non-finite is dropped whole on load, so no reader of `samples` ever
  sees pairs with nothing to judge them against. The metered range cannot release
  it -- once a clamp is in force the plan stops out-asking the pump and that
  evidence fades, so re-testing it would release the clamp and re-book the
  fiction a window later.
- **S4** `draw_range.planned_range(draw, params, cap)`: the effective range a
  solve may book, or `None` (the configured figures stand). `None` wherever
  `plan_writes_power()`, because there the metered draw is the plan's own echo and
  a clamp could only ratchet down. On an install that can duty-cycle the min end
  stays configured: a level below it is an average over the step, which a pump
  running at its metered floor for part of the step delivers.
- **Hosting**: `AccuracyTracker.draw`, persisted as one additive `draw` key in the
  accuracy document (store version unchanged at 1), domains declared in `store.py`
  (`draw/samples/#/0`, `#/1`, `draw/engaged`, `draw/config/#`). An install with no
  running sample writes no key. `draw/config/#` is one key beyond the design
  note's table: the latch is meaningless without the configuration it was judged
  under.
- **Fold**: one call in `_record_accuracy` beside `_fold_flow_lift`, passing
  values (`draw_range.fold(...)`), the power-meter freeze read once on its own
  line; nothing in `draw_range.py` takes the coordinator.
- **Diagnostics (S7)**: `diagnostics.py` publishes module views through one
  `(key, view)` registry, each row isolated by `_never_breaks`; `pump_duty` moved
  onto it and `draw_range` added.

Paid inside the PR, so every structure metric is at or below main's budget and
archscore reads NULL: `_async_watch_learning_drift`'s non-alarmed branch shares
the method's single closing `_async_save_snapshots()` instead of its own
(-1 class line, which the fold's two lines spend: net 0); `_record_accuracy`
reads `_learning_frozen(CONF_POWER_ENTITY)` once instead of twice; `wood_fuel.py`
imports `utc_elapsed_seconds` from `drift`, where it lives, instead of through
`accuracy`'s re-export -- that edge would otherwise have closed a
`thermal_model -> wood_fuel -> accuracy -> draw_range -> thermal_model` cycle.

Why not the capacity envelope (`_fold_capacity_envelope`): it folds only at
>= 0.95 x nameplate commands, derives its thermal figure from the commanded level
(on an overbooking install, the overbooked level itself), and floors its cap at
0.6 x nameplate -- far above the clamp an overstated nameplate needs. It answers
the other end of the range, so 7b composes through the same `power_caps_extra`
channel but does not feed it.

## Head

`9b39bb7c68ff6a0cf5914c27c7cb93293400a9f3`. Round 4's `merge` verdict stands at
`90b9e87f7`; what follows is the update-branch merge the orchestrator handed this
seat, and the reviewer judges that delta alone (`fix-review.md` step 12). Main was
`d8a4bd36f6384dde45486fff388f91ed4a3aa6df` (PR #2059; #2024's flow meter landed at
`a8ce87571`) -- `date -u`: 2026-10-09T17:04:25Z.

The pull request was **DIRTY**: `git merge-tree --write-tree origin/main HEAD`
exited 1 with three content conflicts, and a DIRTY PR runs no CI at all
(`steward` S2, `claim-files.md`). Both sides of this merge added **one production
module each** -- this lane `draw_range.py`, #2024 `flow_meter.py` -- and each side
recorded the resulting census as its own number, so every figure in those records
is a measurement re-taken on the merged tree, not a side picked. Nothing was
averaged; each number below is what the named instrument printed here.

Three conflicts, resolved by instrument:

- `dev/audit/rounds/round4/D6/claims.py` -- two hunks, both sides printing
  `arch_modules_on_disk=74` / `arch_map_listed=74`. Unioned in the file's own
  "N until the additions that raised it" form; the headline re-measured by
  `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`, which
  prints **75** for both (the merged tree holds BOTH new modules),
  `arch_map_missing=0`, `ha_module_level_importers=27`,
  `config_defaults_compared=89`, `config_ranges_compared=91`,
  `claims_extracted=125`, `claims_true=123`, `claims_false=0`, `claims_stale=0`,
  `claims_unverifiable=2`. `tests/harness_headers.py` executes those EXPECTED
  lines against that run, so the header is not this seat's assertion -- it is the
  instrument's.
- `tests/deployment_shape.py` -- the same union in COST OF THE SHAPE, plus the
  pair census re-derived from the merged `tests/closures.json` by the rule
  `tests/entities.py`'s own `_d308_pairs` applies (Jaccard over closure files
  under `custom_components/heatpump_optimizer/`, empty sets skipped): 93 production
  files, 33 scripts, 528 pairs, 406 comparable, **123** pairs at >= 0.80, 18 at
  exactly 1.00. The per-pair shared counts were written from that computation --
  the four that both sides had already agreed on are in the next bullet.
- `tests/features.py` -- both sides appended a check block at the same tail
  place: this lane's 7a `draw_range` block (396 lines) and #2024's #1956
  feedback-gap and flow-meter blocks (227 lines). Union, both kept, in append
  order. The two blocks share no top-level name and no `as _x` import alias
  (`comm` of the defined names, and of the aliases: both empty), and the merged
  file's own run is `## Figures`' whole-file line.

False agreements git settled without a conflict, caught by reading the merged
result rather than the diff (`fixer.md` step 6 -- the class the orchestrator
warned about, and here it was live):

- `docs/architecture.md` -- **both sides wrote "74 modules" identically, and the
  merged tree has 75.** Three sentences were false with no conflict to notice:
  line 8 (`75 modules, of which 27`), the boundary census (`27 of the 75`), and
  the deliberate-freedom count (`The other 47` -- the doc's own rule is
  total minus the module-level importers minus `inputs`, which touches it inside
  a function: 73-27-1=45 at the merge base, 74-27-1=46 on each side, 75-27-1=47
  here). Left alone, `C32` goes false (`documented=74 measured=75`) and
  `tests/harness_headers.py` reddens at this head. It was left alone by neither
  side by design: no check reads the other two sentences, so they are true here
  by this seat's arithmetic, not by an instrument's.
- `tests/deployment_shape.py`'s silent numbers -- `all 92 files` and every
  per-pair count (`92`, `82`, `74`, `56`, `90`, `57`) sat OUTSIDE the markers
  because both sides moved them the same way; the merged census re-derived 93, 93,
  83, 75, 57, 91, 58, and those lines were corrected from the computation above.
  `tests/entities.py`'s `#1218` checks re-derive `all 93 files`, `123 of the 528`
  and `406 pairs` from the recording and fail the lane if the prose differs, so
  this is a pinned sentence, not a claim.
- `dev/audit/rounds/round4/D6/claims.json` + `claims.md` -- the register is
  `claims.py`'s committed output, regenerated by the run above: only its C32/C33
  rows moved (to `documented=75 measured=75` and `on disk=75, listed=75`), and
  nothing else in it changed.
- `custom_components/heatpump_optimizer/coordinator.py` and `.../thermal_model.py`
  auto-merged with no conflict; their hunk ranges are disjoint (ours at
  207/9312/9640/9745 in `coordinator.py`, main's at 274/6033/7520; ours an
  `InstallCapability` method near 1250, main's `feedback_gaps` near 1282 in
  `thermal_model.py`), so the merge is a union of unrelated edits rather than an
  overwrite. That is measured, not asserted: the set of lines this lane adds to
  each file is byte-identical across the merge -- `git diff b2b6acd64...90b9e87f7
  -- <file> | grep '^+'` against `git diff origin/main...HEAD -- <file> | grep
  '^+'`, sorted and diffed, prints nothing for either file (38 added lines in
  `coordinator.py`, 10 in `thermal_model.py`). That is why the 16 mutation arms
  below could be re-run rather than re-derived: `apply()` refuses unless a needle
  matches exactly one line of the merged file, and all sixteen needles matched.
- `tests/closures.json` -- settled by the tree's own driver, never by hand. It ran
  at the merge (`LEDGER-MERGE: resolved tests/closures.json`, 22 lists merged as
  sets) and `tests/closure.py selftest` is green on the result (`ALL 57 closure
  shrink pins PASSED`). Its `re-run the gate that owns this file` is dischargeable
  only by CI's Linux recordings, so no `derive_closures.sh` was run here
  (`gate-scoping.md`: that path once replaced the Linux recordings).

Six files carry a hand resolution -- the three conflicted ones,
`docs/architecture.md`, and the two regenerated register files. Of the 61 files
the merge changed against `90b9e87f7`, every other path is main's byte for byte
(`git diff --quiet HEAD origin/main -- <path>` answers identical for all but
`coordinator.py`, `thermal_model.py` and `closures.json`, which differ because
they are unions of both sides, not because this seat edited them).

Nothing else in the branch moved since round 4: `acba8517d` (twelve checks and one
population helper in the 7a block), `279212233` (14 `killed_by` rows under
`tests/mutation_ledger/killed_by/draw_range.py/`), and `90b9e87f7` (the merge of
the lane's own `a456c5ed -- ci: pin killed mutants`, whose two rows for anchors
`:175` and `:262` replaced this seat's add/add rows, so twelve of the fifteen rows
are the seat's and two are the lane's and `draw_range.py` holds no undisposed
site).

## Mutation proof

Control at this head -- `ALL 51 DR BLOCK PASSED`. The block is sliced out of
`tests/features.py`, never a copy of it, so the 51 are the file's own 51
(`PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
/Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r5/drblock.py`). The slice
rule changed this round, and the change is the finding: round 4's harness ended
the slice at the file's own `sys.exit(R.close(`, which was safe while 7a was the
last block in the file; #2024 appended two blocks after it, so that rule now
over-captures into them and dies on names the slice does not carry
(`NameError: name 'FakeState' is not defined`). The end is now the next top-level
block header (`^# --- `), which the 7a block never uses -- its own header is
`# -- ` -- and the harness asserts that no other header is inside the slice, so an
over-capture refuses rather than reporting a pass. 51 is unchanged: the block's
own executed count, printed by the same `Results` tally the file uses.

Each arm below is one production line edited in a COPY of the package and run
through that block (`.../scratch/r5/mutproof.py`; the checkout is never mutated,
which is `mutation_table.py`'s own rule, and an arm whose needle is not unique
refuses rather than reporting a pass -- that uniqueness test is also what proves no
mutated line moved in the merge). Result at this head: `MUTPROOF: 16 of 16 arm(s)
went red (0 survived)`, every arm's tally and every named check identical to
round 4's, which is what a merge that moves no production line should print.

- M1 the fold call replaced by the freeze read alone: `1 of 51 FAILED` --
  `the per-cycle settlement folds one running sample: (drawn, space asked)`
- M2 `plan_writes_power` returns False: `2 of 51` -- `plan_writes_power is exactly
  a frequency write (S1)`, `S4 where the plan writes the frequency: None, the draw
  is its own echo`
- M3 the evidence gate removed (engage on sample count alone): `6 of 51` -- both
  null controls, `a sub-floor duty-cycle average overdrawn by the running pump is
  no evidence`, `S4 with no evidence, or a different configuration: None`, and two
  of the round-4 checks (`the factor boundary is not a disagreement`, `12 of 48
  engages, 11 of 48 does not`)
- M4 the duty-cycle min end not kept: `2 of 51` -- `S4 where the install can
  duty-cycle: the min end stays configured`, `S4 on a duty-cycling install that
  runs below its configured min ...`
- M5 `AccuracyTracker.from_dict` drops `draw`: `1 of 51` -- `the samples, the latch
  and its configuration persist through the accuracy store`
- M6 defrost not excluded: `2 of 51` -- `S2: defrost in the interval is not a
  running sample`, `and folds nothing for an interval whose closed window saw a
  defrost`
- M7 hot water not excluded: `2 of 51` -- `S2: hot water asked is not a running
  sample`, `and folds nothing under a hot-water ask`
- M8 a configuration change does not reset: 7 named checks FAIL and the run then
  raises, counted 8 -- among them `a changed configuration releases the latch and
  restarts the evidence`, `the latch holds a full window after the plan stops
  out-asking the pump`, `S4 on a switch-plus-setpoint install: both ends metered`
- M9 `MIN_SAMPLES` required lowered to one sample: `3 of 51` -- `short of
  MIN_SAMPLES running samples there is no statistic and no clamp`, `47 samples is
  not a day, 48 is and engages`, `a stored latch that has not reached MIN_SAMPLES
  answers, it does not raise`
- M10 the diagnostics row renamed away: no FAIL line -- `KeyError: 'draw_range'`
- M11 sub-floor asks counted as evidence: `1 of 51` -- `a sub-floor duty-cycle
  average overdrawn by the running pump is no evidence`
- M12 the standby floor removed from S2: `2 of 51` -- `S2: the standby floor is 0.25 kW counted in the test -- ...`,
  `S2: standby draw is not a running sample`
- M13 the space-running test removed from S2: `1 of 51` -- `S2: space circuit off
  is not a running sample`
- R1 `bottom = low` always (the configured min's tolerance rule off): `3 of 51` --
  `a metered floor within 15 % of the configured min keeps the configured min`,
  `inclusive at the bottom ...`, `an engaged latch whose metered ends EACH stand
  within the tolerance returns None`
- R2 `top = high` always: `3 of 51` -- the same three on the max end
- R3 `from_dict`'s unreadable-configuration `except` narrowed so it no longer
  catches: no FAIL line -- `ValueError: could not convert string to float: 'a'`
  escapes `from_dict`, which is the shape round 2's `R3` refused to leave reachable

At the merge base the block fails at import (`cannot import name 'draw_range'`).

## Null control

Three shapes at 20 seeds each through the lane's own harness, re-run at this head
(`PYTHONPATH=tests/hastub:custom_components
~/.local/state/hpo/venv-ci/bin/python3 dev/audit/harnesses/draw_range_evidence.py
20`), and each is a check in the block too, so the null is pinned rather than
observed once. The four rows are identical to round 4's, which is the point: no
solve reads `draw_range` in 7a, so nothing in #2024's merge can move them.

- `over` (the synthetic overstated nameplate): engaged **20/20** seeds, observed
  `(1.268, 1.739)`, effective `(1.268, 1.739)` on a switch+setpoint surface,
  `(1.0, 1.739)` on a duty-cycling one, `None` on a frequency write.
- `null` (the pump draws exactly what it is asked): engaged **0/20**, `None` on
  every surface. A clamp that engaged here would rewrite a correctly configured
  install's plan.
- `mild` (a correctly sized 6 kW pump part-loading at 1-2 kW, drawing what it is
  asked within +/-10 %): engaged **0/20** though its running P90 (1.943) is under
  half its configured max -- a low ceiling alone is not a contradiction, which is
  the whole reason the latch exists.
- Contrast, recorded so a consumer does not over-read the nulls: `mild-indep`, the
  same pump whose draw does NOT follow the ask, engages **20/20** (observed
  `(1.113, 1.898)`). There the plan's per-step levels are genuinely wrong about
  the draw, which is the evidence the latch is for -- so `engaged` is not a claim
  that the nameplate figure is wrong.
- And at the plan level there is nothing to compare, by design: no solve reads
  `draw_range` in 7a, so every plan is byte-identical to main's. That is measured,
  not asserted: `GOLDEN_MODE=drift GOLDEN_REF=d8a4bd36f638` through
  `tests/run.sh` runs `tests/env_drift.py --all d8a4bd36f638` (1932 s at this head,
  rc=0), which re-computes every scenario in this tree and against the merge base
  and printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked against
  d8a4bd36f6384dde45486fff388f91ed4a3aa6df` and `NO STALE FIXTURE: 56 committed
  fixture(s) still match what this tree computes` -- the four `may-drift` rows it
  names are the pre-registered machine-sensitive ones and all read `did not move
  here`. `optimality`, `validate`, `edge` and `backtest` are green in the same
  scoped run. `S4 where the plan writes the frequency: None` is the per-install
  arm of the same claim.

## Figures

Main-tip-dependent figures: origin/main was
`d8a4bd36f6384dde45486fff388f91ed4a3aa6df` and every command below ran at
`2026-10-09T17:04:25Z` or later (`date -u`) at `9b39bb7c6`.

- Scope of the gate -- `D=$(mktemp -d); ~/.local/state/hpo/venv-ci/bin/python3
  tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D";
  cat "$D/scope.txt"; cat "$D/scope.run"` -- `MODE: SCOPED -- 28 script(s) run, 5
  scoped out`; the merge base is `d8a4bd36f638`. Keyed on the mode line, never the
  count (`CLAUDE.md` rule 1). The five scoped out are `arch_score.py`,
  `frontend.py`, `ha_contract.py`, `layout.py`, `open_meteo.py`; `layout.py` is
  therefore run by hand below, as round 4 learned it must be.
- The scoped gate itself -- `GATE_SCOPE=auto GATE_SCOPE_BASE=d8a4bd36f
  GOLDEN_MODE=drift GOLDEN_REF=d8a4bd36f GATE_JOBS=3 bash tests/run.sh` at
  `9b39bb7c6`, on this seat's host (Apple M1, python 3.14.7, BLAS `accelerate (no
  OpenBLAS kernel class)`, numpy 2.4.6 -- the environment line `run.sh` prints
  first, per #1725), **partially by the orchestrator's direction**: the box sat at
  load average 62-110 with other seats mid-merge, and the standing rule is that
  heavy lanes run in CI, so the run was stopped at 41 min and its remaining lanes
  are CI's at this head. What it got through, with its own rc and seconds from
  `run.sh`'s lane manifests: `env_drift.py --claims-only d8a4bd36f` rc=0 (1 s,
  `claims hygiene: ... ok`), `closure.py selftest` rc=0 (7 s, `ALL 57 closure
  shrink pins PASSED`), `tests/features.py` rc=1 (2313 s, `1 of 3930 FEATURE
  CHECKS FAILED` -- the line below), `tests/golden.py` SKIP (GOLDEN_MODE=drift
  routes fixtures through `env_drift`), `env_drift.py --all d8a4bd36f` rc=0 (1932
  s, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`), `validate.py`
  rc=0 (152 s), `edge.py` rc=0 (164 s), `backtest.py` rc=0 (462 s). Stopped in
  flight: `boost_drift_replay.py` (30 min in). `entities.py` is the one lane the
  run reported red on its own account -- `FAILED ... tests/entities.py (190s)` at
  19:36:52, before the stop -- and its log went with `run.sh`'s workdir, so that
  attempt's cause is not recoverable here; what IS measured is that the same
  script, run by hand at this head with no lane around it, prints `ALL 2236 ENTITY
  CHECKS PASSED`, and so does the same script in a detached worktree at
  `origin/main` alone -- the control -- with an identical 46-line set of the
  negative-control arms its judging rows read `ok`. See the two bullets below. Never
  started, and therefore CI's: `harness_headers`, `deployment_shape`,
  `doc_claims`, `arch_score_head`, `config_flow_steps`, `optimality`, `plan_view`,
  `solar_alignment`, `block_duty`, `wood_advisor`, `manual_plan`, `typing_ruler`,
  `finite_boundary`, `guard_pins`, `debug_collect`, `md_tables`, `card`,
  `card_drift`, `structure`, `stress`. `run.sh` holds the gate lease only around
  `stress.py`, which never started: `tests/gate_lock.py status` reads `/tmp/hpo-gate.lock:
  no lease` before and after, so no lease was taken and none was released by hand.
  Three of the lanes it did not reach were run by hand at this head instead,
  because each one owns a number this delta resolved: `structure.py`,
  `deployment_shape.py` and `entities.py`. Beside them the two instruments those
  lanes defer to were run the same way -- `dev/audit/rounds/round4/D6/claims.py`,
  which `harness_headers.py` executes, and `mutation_table.py --pin-killed`, which
  is CI's `mutation` job's own repair step -- and so was `layout.py`, which the
  selection had already scoped out. Every one is cited in its own bullet below.
- Entities, the census authority, at this head -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 tests/entities.py` (run by hand because
  the lane's attempt died at 190 s) -- `ALL 2236 ENTITY CHECKS PASSED`, and among
  its rows the three that grade the prose this merge resolved read `ok`: `the
  deployment-shape lane's closure is the whole tracked package, so any production
  diff selects it (#1218)`, `and the lane's docstring records those measured
  numbers as the selection-cost note (#1218)`, `the overlap predicate counts equal
  sets, skips empty ones and holds the 0.80 boundary (#1218)`. Its null control is
  the same command run in a detached worktree at `origin/main` alone on this same
  host: also `ALL 2236 ENTITY CHECKS PASSED`, and the 46 `FAIL` evidence lines the
  run prints (the negative-control arms -- `hb:positive_control`, `a3:roster`,
  `a5:byte_unchanged`, ... -- whose own judging rows print `ok`) are an IDENTICAL
  name set in the two trees, `diff` empty. So the arm that reddens on this box
  reddens at main too, and the merge turns no entity check red.
- The `#1218` rows `tests/entities.py` asserts about the resolved prose, isolated
  here as well (measured first, while that lane had only just been stopped, and
  kept because it names the four conditions the prose alone depends on) --
  `~/.local/state/hpo/venv-ci/bin/python3 -I
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r5/d308_string_check.py`
  runs that script's own conditions verbatim (the three f-strings it requires in
  the whitespace-normalised docstring, the no-production-closure names, the
  full-coverage set, the selection) and prints `PROD=93 PAIRS=123 TOTAL=528
  COMPARABLE=406`, `strings present: ALL`, `empty-set names in note: True`,
  `full-coverage == [arch_score_head, deployment_shape]: True`, `PROD <= DS
  closure: True | DS selected by a production diff: True`. The lane itself is
  still CI's; what was checkable without the 2235 rows is checked.
- Whole file -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 tests/features.py` at this head, in the
  scoped run above (2313 s) -- `1 of 3930 FEATURE CHECKS FAILED`, rc=1. The one
  failure is `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the
  half-price floor's plan refined under it` (shipped 110.4366, seeded with the
  half-price plan 110.1297), a solve this diff does not reach, on the seat's
  Accelerate BLAS; it reproduces at main on this box, where the branch has no
  lines, and CI's `fast (3.14)` is the authority for it (round 3 re-took both
  of the arm's figures at `6f420a1f7`, green). 3930 is the merged file's own
  output: the 3911 `90b9e87f7` printed, plus the nineteen checks #2024 appended,
  all of them green here -- which is the direct test that the union in
  `tests/features.py` kept both lanes' blocks alive, not just parseable.
- Structure -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tests/structure.py` -- `STRUCTURE RATCHET PASSED`, 41 counting rules holding.
  The ratchet rows are the 16 keys of `tests/structure_budgets.json` less
  `recorded_at` (derived, not carried), and the script prints 21 `ok` lines beside
  them because it adds the counting-rule self-check and the `const.py` symbol
  checks. The two that a merge of two modules could move are at their caps with no
  raise taken or needed: `max_class_loc 8818 <= 8818`, `seam_cut_total 762 <= 762`
  (both budgets files are main's bytes -- `git show origin/main:tests/structure_budgets.json
  | cmp - tests/structure_budgets.json` and the same for `tests/mutation_budgets.json`,
  each followed by its verdict line: identical -- and `git diff --name-only
  origin/main...HEAD -- tests/mutation_budgets.json` prints nothing, so this lane
  moves no cap up anywhere, `CLAUDE.md` rule 2).
- Placement -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tests/layout.py` -- `layout: GUARD: 0 refusal(s) against d8a4bd36f638`,
  `4372 tracked path(s) enumerated`, self-test ok.
- Architecture -- `~/.local/state/hpo/venv-ci/bin/python3
  tools/audit/archscore/score.py --diff origin/main` -- `Architecture score: dS
  +0.0000 NULL`.
- Census, the merged tree's own print -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round4/D6/claims.py` --
  `arch_modules_on_disk=75`, `arch_map_listed=75`, `arch_map_missing=0`,
  `ha_module_level_importers=27`, `config_defaults_compared=89`,
  `config_ranges_compared=91`, `claims_extracted=125`, `claims_true=123`,
  `claims_false=0`, `claims_stale=0`, `claims_unverifiable=2`. It re-records
  `claims.json`/`claims.md`; the regenerated register is committed, not hand-edited
  (`fixer.md` step 10: the generator was run). Against main the register moves on
  exactly two rows: `git diff --numstat origin/main HEAD --
  dev/audit/rounds/round4/D6/claims.json dev/audit/rounds/round4/D6/claims.md`
  prints `2 2` for each file, and both are C32 (`documented=74 measured=74` ->
  `documented=75 measured=75`) and C33 (`on disk=74, listed=74` -> `on disk=75,
  listed=75`), each still **true**.
- Selection-cost census -- the rule `tests/entities.py`'s `_d308_pairs` applies,
  run over a `tests/closures.json` read from any ref (`~/.local/state/hpo/venv-ci/bin/python3 -I
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r5/d308_at.py <closures.json> <label>`;
  the merged tree's own copy for the head line) -- and run at all four trees, which
  is the control for "resolve by picking a side". Columns: production files in
  the union, pairs at >= 0.80, the optimality/validate four, `env_drift`/`golden`,
  the card pair, and `claims.py`'s on-disk module count:
  - merge base `b2b6acd64`: 91, 120, 20, 89, 56, 73
  - round-4 head `90b9e87f7`: 92, 120, 21, 90, 57, 74
  - main `d8a4bd36f`: 92, 120, **20**, 90, 57, 74
  - **this head `9b39bb7c6`: 93, 123, 21, 91, 58, 75**
  Neither side's number is the merged one, and two of them -- the >= 0.80 pair
  count (120 on every tree before the merge, 123 after) and the module census (74
  on both sides, 75 here) -- are numbers NO side's own instrument ever printed, so
  they are the class a clean-resolving merge ships false. The `TOTAL=528` and
  `COMPARABLE=406` and the four scripts holding no production closure are the two
  figures that genuinely survive the merge unchanged, and the no-closure set is
  identical at every tree (`arch_score.py`, `ha_contract.py`, `layout.py`,
  `md_tables.mjs`).
- Ledger, source-only (seconds, no mutant run) -- `~/.local/state/hpo/venv-ci/bin/python3
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/ledger_line.py` at this
  head -- inventory 5943, unpinned 4620, `draw_range` unpinned **0**,
  `thermal_model` 273 (the pre-ratchet stock, not this diff's), completeness
  problems **0**, ledger form problems **0**, `killed_by` rows 1220,
  `survivor_triage` rows 84. Against `90b9e87f7`'s 1209/83 the +11/+1 are #2024's
  rows arriving with main, not this lane's.
- The canonical pin lane, at this head -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 tests/mutation_table.py --pin-killed
  --base origin/main --scripts tests/features.py` -- `4620 unpinned site(s) of
  5943 candidate sites, 4622 at the ratchet base d8a4bd36f...; the ledger agrees
  with the deterministic inventory`, then `PIN KILLED -- 0 new unpinned site(s)
  against d8a4bd36f6384dde45486fff388f91ed4a3aa6df to drive` and `PIN KILLED:
  nothing to pin`, rc=0. The count FELL BELOW the base (4620 < 4622), which is what
  the ratchet asks. This run drove no mutant: with nothing new to pin the tool
  reads the inventory and answers, which is why it is cheap here where round 4's
  `--anchor` drive of one site spent 730 s and printed `MUTATION TABLE INCONCLUSIVE
  -- the baseline is already red in tests/features.py`.
- Ledger re-keying: **nothing to normalize, and that is a measurement, not an
  assumption** -- `mutation_table.layout_problems()` returns 0 problems and
  `ledger_form_problems()` returns NONE on the merged tree
  (`~/.local/state/hpo/venv-ci/bin/python3 -I
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r5/layout_probe.py`).
  Every row of this lane's 42 `killed_by` files -- 39 under `draw_range.py/`, 2
  under `coordinator.py/`, 1 under `thermal_model.py/`, counted by
  `git diff --name-only origin/main...HEAD -- tests/mutation_ledger/ | wc -l`
  (three-dot, because after a merge only three-dot still answers what THIS lane
  adds) -- is content-anchored
  `FILE:SCOPE KIND DIGEST` -- the retired `FILE:LINE KIND` key is refused by the
  same checker -- so main's line shifts move no key, and `--normalize` was not
  run because there was nothing for it to rewrite.
- Predictor -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tools/pr/ci_predict.py --base d8a4bd36f638` -- `CI PREDICT: no closures or fast
  red predicted against d8a4bd36f638 (a data-file read is not seen)` and **no**
  `ADDED UNPINNED` line. That command is the rule that enumerates the class, and
  its output at this head is what `## Unpinned sites` counts.
- Claim files -- `git show origin/main:tests/golden/claimed_drift.txt | cmp -
  tests/golden/claimed_drift.txt` and the same for `card_claimed_drift.txt`, each
  followed by its own verdict line: both `byte-identical to origin/main's`. The
  branch claims no golden drift (`git diff --name-only b2b6acd64 HEAD --
  tests/golden` lists nothing), so the claim file the merge carried in is main's,
  and `tests/env_drift.py --claims-only d8a4bd36f` answers `claims hygiene: ...
  ok` (1 s, inside the scoped run above). The `claimnotes` driver is installed in
  this clone and ran at the merge; it had nothing to union.
- Versions -- `git diff --name-only $(git merge-base origin/main HEAD)...HEAD --
  VERSION hacs.json RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json`
  -- prints nothing: `VERSION`, the manifest version and the release-notes heading
  are untouched (`CLAUDE.md` rule 1).
- The PR merges clean now -- `git merge-tree --write-tree origin/main HEAD` at
  `9b39bb7c6` exits **0** with no CONFLICT line. That is the difference between a
  PR that is red and a PR that cannot run, and it is the reason this round exists.
- Body contract -- `PATH="$HOME/.local/state/hpo/venv-ci/bin:$PATH"
  bash tools/pr/prepr.sh <body.md>` run from this worktree with the body outside
  it (`fixer.md` step 5: an untracked scratch file in the worktree reads as a
  change the gate cannot scope) -- final line `PRE-PR:
  9b39bb7c68ff6a0cf5914c27c7cb93293400a9f3 000000000000000000000000`, rc=0, verdict
  line `clean    no refusal`, with `pr-body PR-BODY: 0 error(s) ... no budget leaf
  raised over d8a4bd36f...9b39bb7c6`, `ancestry reds: the body answers every red
  this branch pushed (fast (3.14) mutation mutation-autofix nightly-ha (stable)
  nightly-status)`, `claim files: byte-identical to origin/main`, `claims hygiene:
  d8a4bd36f638 ok`, `figures ... 0 refused`, and `unpinned sites` SKIPPED -- `the
  diff adds no unpinned mutation site`. (Its `resolved / not verified` counts are
  not quoted: they are a function of this body's own text, so a number that
  describes the document it sits in would be false the moment the document is
  edited.) The only WARN is the handoff itself: `HEAD is 54 commit(s) ahead of
  origin/fix/live-power-clamp-foundation-pr`, which is the frozen-head rule
  (`steward` S10): this seat pushes the handoff refs, never the PR branch.

## Red checks

- `Tests` / every required context, **absent for the whole of this round**: the
  pull request was `DIRTY`, so no `pull_request` run fired at all
  (`steward` S2, `claim-files.md`: "such a PR does not go red, it cannot run").
  The detector is `git merge-tree --write-tree origin/main HEAD` -- seconds, and
  it exits 1 -- and its standing cost for a seat that does not run it is a whole
  round in which nothing can be measured: this branch has now spent two rounds
  (round 3 on `tests/closures.json` alone, round 5 on the three census files) on
  heads whose CI could not start. Resolved here by merge, never by re-cut
  (`fixer.md` step 6, tvofi 2026-10-01), and `## Head` names the instrument behind
  every number the merge moved. The same state at round 3 showed five required
  contexts `ABSENT` rather than red -- `pr-contract`, `policy-docs`, `env-matrix`,
  `budget-raise-gate`, `wave-script` -- which is not a check this range turned: an
  absent context answers no detector, and each of them is a contract this branch
  satisfies by construction (its own body contract, its policy diff, its env
  matrix, no budgets raise, no wave script). They are named here because
  `prepr`'s ancestry arm asks for every name that ever read red or absent in the
  range, and the answer for all five is the same as for the DIRTY state itself --
  the head could not run, and now can: `git merge-tree --write-tree origin/main
  HEAD` exits 0 and the body contract passes at this head (`## Figures`' prepr
  line).
- `mutation`, the one required context red at `6f420a1f7` (the last head CI ran),
  and red at every earlier head of this branch: `MUTATION TABLE REFUSED -- 4636
  unpinned site(s) against 4623 at the ratchet base b2b6acd64..., 15 of them added
  by this diff` (job 113755927879). Its answer is `ci-autofix.md`'s shape, and the
  lane did its half at that head (`a456c5ed`, `AUTOFIX: changed`), proved 3
  survivors, and never started the other 10 for the budget -- so all fifteen are
  disposed of in the tree, each with the measurement that earned it
  (`## Unpinned sites`). At this head the same refusal cannot fire: the canonical
  `--pin-killed` route prints `PIN KILLED: nothing to pin` (rc=0) and the count
  sits below the base (4620 < 4622). The cheaper detector exists and costs no
  mutant run: the source-only trio (`load_budgets`, `inventory`,
  `unpinned_sites`) or `tools/pr/ci_predict.py --base <merge-base>`, both re-taken
  in `## Figures`, which named all 15 sites and their keys before any push.
  Measured standing cost at round 4: seconds for those two.
- `fast (3.14)`, red twice in this branch's range and green at `6f420a1f7`:
  (a) at `325960ef`, `tests/layout.py` refused
  `placement: tools/audit/harnesses/draw_range_evidence.py re-adds a moved path;
  it lives at dev/audit/harnesses/` -- fixed there: the harness is at
  `dev/audit/harnesses/draw_range_evidence.py`, and `PYTHONPATH=tests/hastub
  python3 tests/layout.py` reads `layout: GUARD: 0 refusal(s) against
  d8a4bd36f638` at this head, in seconds. The cheaper detector is that script run
  by hand before the push -- at this head the scoped gate SKIPS it (`SKIP
  tests/layout.py (closure: 3 files, no changed file is in its measured closure)`),
  so which scripts reach `fast` is main's recorded closure table's business, not
  this diff's, and a seat cannot assume the gate will run a placement check for it;
  (b) at `e408b9a28`, `tests/entities.py`'s `--anchor` re-drive of one site
  reported the ledger stale -- round 2 had deleted a line `mutation-autofix`
  still pinned. Fixed there by deleting that pin; the cheaper detector is the
  source-only trio above, which refuses a disposition naming no generated site in
  seconds and with no mutant run, and prints `completeness problems : 0` at this
  head.
- `nightly-ha (stable)` and `nightly-status`, red together at `becd4e383`
  (job 113611720490): `FAILED: 2 of 64 checks: ['hb:positive_control',
  'run:exit_status']`. `hb:positive_control` is the heartbeat instrument's own
  positive control -- whether py-spy's rc=0 section names a planted 600 ms spin --
  and `run:exit_status` is the container exit carrying it; every integration check
  in that lane passed. This range touches neither py-spy nor the heartbeat
  harness, and no cheaper detector exists inside this diff's scope for an
  instrument's self-control: not this PR's red (`defect-root-cause.md`'s "not this
  PR's"). Neither is one of the seventeen required contexts, and `nightly-status`
  reports the nightly lane's own state rather than this head's.
- Nothing in this delta turned a check red that was green at `90b9e87f7`. The
  census instruments that own the resolved numbers all read green at the merged
  head, each with its command in `## Figures`: `claims.py` (`claims_false=0`,
  `arch_modules_on_disk=75`, `arch_map_listed=75`), the `#1218` conditions
  `entities.py` asserts about `deployment_shape.py`'s prose (replicated: `strings
  present: ALL`), `deployment_shape.py` itself (`ALL DEPLOYMENT SHAPE CHECKS
  PASSED`), `structure.py` (`STRUCTURE RATCHET PASSED`), `layout.py` (`GUARD: 0
  refusal(s)`), `env_drift.py --all` (`NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE:
  56`), `entities.py` (`ALL 2236 ENTITY CHECKS PASSED`, with the three `#1218`
  rows that grade the resolved prose reading `ok`, and the identical result at
  `origin/main` alone as the control), and the pin lane (`PIN KILLED: nothing to
  pin`, 4620 under the base's 4622).
- One lane came back red in the partial local run, and it is the disclosed one, not
  a new one: `tests/features.py` `1 of 3930 FEATURE CHECKS FAILED`, the
  `R9-F2.1 P3` storage arm (shipped 110.4366 against the half-price seed 110.1297,
  bound 0.1). It is a per-architecture solver reduction on this box's Accelerate
  BLAS (`fixer.md` step 15), this diff reaches no solve, and the same arm reproduces
  at main on the same host where the branch has no lines -- so it is not this
  range's red and CI's `fast (3.14)`, on the canonical environment, is the
  instrument for it. The remaining nineteen scripts the stop cut off are CI's at
  this head for the same reason: this box was at load average 62-110 while other
  seats ran their own gates, and a timing arm measured there bounds nothing.

## Unpinned sites

The rule that enumerates them is
`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base d8a4bd36f638`,
whose `ADDED UNPINNED` keys are what `tools/pr/prepr.sh` step 6d writes and
`unpinned_line` matches whole. At this head it prints **no `ADDED UNPINNED` line
at all: 0 sites** -- every one of the fifteen the diff adds carries a disposition
in the tree. The count is the merged tree's, re-taken after the merge because the
ratchet base moved from `c518447eb804` to `d8a4bd36f638`.

How they got disposed, unchanged from round 4 and restated because the
dispositions are what a reviewer grades: at `acba8517d` the same command listed 14
keys over 15 sites, all in `draw_range.py`. **Self-correction, disclosed:** the
round-3 body said all 22 of its list were "pinned by `mutation-autofix`"; 15 of
them were not. The pull request was DIRTY, so no `pull_request` run fired and the
pin lane -- gated `if: github.event_name == 'pull_request' &&
needs.mutation.result == 'failure'` (`.github/workflows/tests.yml:895-899`) --
could not measure them. A lane that cannot run is not a disposition. Each key now
carries a row under the ledger's `killed_by` tree: twelve earned by the site's own
mutant taking a named check red at `acba8517d` (the drive is round 4's
`## Figures` pin-drive line, and each row quotes its own FAIL), two recorded by
the lane from its own drive of `6f420a1f7`.

- `custom_components/heatpump_optimizer/draw_range.py:45 CONST`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `RUNNING_FLOOR_KW = 0.5` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `S2: the standby floor is 0.25 kW counted in the test -- 0.3 kW is the pump at its minimum modulation and a sample, 0.2 kW is circulation and not one`
- `custom_components/heatpump_optimizer/draw_range.py:48 CONST`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `WINDOW = 672` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `and the window is a week counted in the test: after 386 running samples only the last 336 stand, so a draw 386 runs back is not the ceiling`
- `custom_components/heatpump_optimizer/draw_range.py:51 CONST`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `MIN_SAMPLES = 96` takes it from rc=0 failed=0 to rc=1 failed=3: FAIL `the evidence floor is a day of half-hour runs counted in the test, not read off the constant: 47 samples is not a day, 48 is and engages`; `a level asked at EXACTLY the configured floor is a level the pump was asked to run at, so its disagreement counts`; `the latch engages at a quarter of the window disagreeing, not below it: 12 of 48 engages, 11 of 48 does not`
- `custom_components/heatpump_optimizer/draw_range.py:54 CONST`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `LOW_PERCENTILE = 20.0` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `the floor is the TENTH percentile: a run of samples at the pump's true minimum sets it when they are 15 % of the window, and a meter glitch of 9 % leaves it alone`
- `custom_components/heatpump_optimizer/draw_range.py:60 CONST`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `DISAGREE_SHARE = 0.5` takes it from rc=0 failed=0 to rc=1 failed=2: FAIL `the latch engages at a quarter of the window disagreeing, not below it: 12 of 48 engages, 11 of 48 does not`; `a level asked at EXACTLY the configured floor is a level the pump was asked to run at, so its disagreement counts`
- `custom_components/heatpump_optimizer/draw_range.py:99 GUARD_OFF`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `if False:` takes it from rc=0 failed=0 to rc=1 failed=1: no FAIL line at all -- with the guard off, `low, high = seen` runs on the `None` the statistic returns short of `MIN_SAMPLES` and raises `TypeError: cannot unpack non-iterable NoneType object`, which `failing_count` counts as one failure; the check that catches it is `a stored latch that has not reached MIN_SAMPLES answers, it does not raise: no statistic, so no clamp`
- `custom_components/heatpump_optimizer/draw_range.py:102 CMP_BOUND`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `top = high if high <= (1.0 - AGREE_TOLERANCE) * cfg_max else cfg_max` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `the tolerance is INCLUSIVE at the top: a metered max at exactly 15 % below the configured one keeps the configured one`
- `custom_components/heatpump_optimizer/draw_range.py:103 CMP_BOUND`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `bottom = cfg_min if abs(low - cfg_min) < AGREE_TOLERANCE * cfg_min else low` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `and inclusive at the bottom: a metered min exactly 15 % above the configured one keeps the configured one (the tie, in floats that tie)`
- `custom_components/heatpump_optimizer/draw_range.py:113 CMP_BOUND`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `on_level = [(d, a) for d, a in self.samples if a > cfg_min]` takes it from rc=0 failed=0 to rc=1 failed=2: FAIL `a level asked at EXACTLY the configured floor is a level the pump was asked to run at, so its disagreement counts`; `the latch engages at a quarter of the window disagreeing, not below it: 12 of 48 engages, 11 of 48 does not`
- `custom_components/heatpump_optimizer/draw_range.py:116 CMP_BOUND*2`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- BOTH comparison bounds on that line (`a >= DISAGREE_FACTOR * d ...` and `... or d >= DISAGREE_FACTOR * a`) were driven separately and each took `a draw exactly DISAGREE_FACTOR times the ask -- either way round -- agrees with the plan: the factor boundary is not a disagreement` from rc=0 failed=0 to rc=1 failed=1, which is what `pin_results` requires before an anchor holding two sites is pinned.
- `custom_components/heatpump_optimizer/draw_range.py:140 GUARD_OFF`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `if False:` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `an engaged latch whose metered ends EACH stand within the tolerance returns None: the configured range stands, it is not echoed back as a clamp`
- `custom_components/heatpump_optimizer/draw_range.py:175 GUARD_OFF`: **pinned by
  `mutation-autofix`** at `a456c5ed` -- its reason reads: Recorded by mutation_table.py --pin-killed against
  b2b6acd64... GUARD_OFF (if False:) took tests/features.py from rc=0 failed=0 to
  rc=1 failed=2. That is the lane's own
  measurement on the canonical environment. The seat's block drive agrees: the same
  mutant takes `a record whose configuration is non-finite is dropped whole: no
  samples, no latch` red, and that check is not new -- it has been in the block
  since round 2, which is why the lane could pin this site and could not pin the
  thirteen that needed a check this round adds.
- `custom_components/heatpump_optimizer/draw_range.py:262 GUARD_OFF`: **pinned by
  `mutation-autofix`** at `a456c5ed`, and the lane names a different driver:
  its reason: GUARD_OFF (if False:) took tests/structure.py from rc=0
  failed=0 to rc=1 failed=1 -- deleting the frequency-write gate moves a structure metric, so the
  ratchet notices before any behavioural check is reached (`pin_results` names the
  earliest driver in the mutant's own order). The seat's drive of the same mutant
  finds `S4 where the plan writes the frequency: None, the draw is its own echo`
  failing in the block, which is the behavioural arm of the same kill. The branch's
  row for this anchor was dropped in the merge so the lane's stands.
- `custom_components/heatpump_optimizer/draw_range.py:271 CLAMP_DROP`: pinned at 279212233, measured at acba8517d, killed by tests/features.py's 7a block -- `low = (cfg_min)` takes it from rc=0 failed=0 to rc=1 failed=1: FAIL `S4 on a duty-cycling install that runs below its configured min: the min end is capped at the metered max, never booked above the max it may book`

No site needed a `survivor_triage` verdict: every one of the fifteen died to a
check, so no equivalence was asserted and none is claimed -- `survivor_triage`
rows in the ledger are 84 at this head, exactly main's count after #2024's one
added row, and none of them is this lane's; the drive that produced them is the
never-automated kind this rule reserves for humans.

Why twelve rows are seat-measured rather than bot-measured, in the lane's own
words. At `6f420a1f7` -- with the conflict cleared, so `pull_request` runs fired
and `mutation-autofix` answered `AUTOFIX: changed` (job 113801958940) -- the three
`mutation-pins` shards measured this:

- shard 2 (job 113756244273) drove five sites and reported `PIN KILLED: 2 pinned,
  3 left unpinned (3 survived, 0 not started for the budget, 0 timed out, 0
  skipped) -- a survivor needs a killing check or a survivor_triage verdict, which
  no tool writes`. It pinned `:175 GUARD_OFF` and `:262 GUARD_OFF`; it drove
  `:48 CONST`, `:51 CONST` and `:102 CMP_BOUND` and all three survived the branch's
  39 checks -- exactly the survivors the seat's block drive measured, from the
  other end of the world.
- shards 1 and 3 (jobs 113756244286, 113756244274) measured nothing at all after
  two hours fourteen minutes: `MUTATION TABLE REFUSED -- nothing was measured: 0
  mutant(s) timed out, 5 not started for --budget-minutes`, reported as
  `measure: skip-measure-failed, 0 anchor(s)`. Ten of the fifteen sites were never
  started: their admission cost, over the drivers `drivers_for` names for
  `draw_range.py`, never fit the step's window.

So the lane could pin 2 of 15 at that head, proved 3 survivors, and could not reach
the other 10 -- and every one of the 13 needs a check that did not exist until
`acba8517d`. That is why the dispositions are recorded here rather than waited for:
the kills were measured per site with the tool's own rule, `killed()`, on each
site's own mutant text, both output forms re-taken on the whole file (round 4's
`## Figures`), and the rows written through `normalize` + `write_budgets` so the
layout stays the lane's. `apply_pins` re-keys against the inventory it finds, so a
later measurement of this head adds nothing: `python3 tests/mutation_table.py
--pin-killed --base origin/main --scripts tests/features.py` at `9b39bb7c6` answers
`PIN KILLED -- 0 new unpinned site(s) against d8a4bd36f... to drive` and `PIN
KILLED: nothing to pin` (rc=0), and the 16 mutation arms were re-driven at this
head anyway (`## Mutation proof`), because after a merge the proof must describe
this tree.

## Forward-carry

- `custom_components/heatpump_optimizer/draw_range.py` (the `DrawRange` docstring,
  the S3 contract its consumers read): `engaged` says the plan's running levels and
  the meter disagree, not that a configured figure is wrong. A correctly sized pump
  whose draw follows the asked level never engages; one whose own controller ignores
  the level engages, sized correctly or not (harness shape `mild-indep`, 20/20
  seeds). The nameplate notice and the COP floor must read it under that meaning.
  Also handed to the orchestrator for the wave's design note, section 6 ("2 vs 7"),
  which lives outside the tree.
- 7b's constraint, in the lane's own resume note
  (`/Users/timmalmstrom/hpo-seats/live-power-clamp/RESUME.md`, section 7b): the
  duty floor both readers take must never exceed the metered running draw's low end
  nor fall below `on_threshold_kw`. The check `S4 on a duty-cycling install that
  runs below its configured min` pins the production behaviour it composes with --
  `planned_range`'s min end is capped at its own max, never booked above it.
- Carried forward to any later lane that adds a module, from this merge's
  measurement: a new production module moves five records at once --
  `docs/architecture.md`'s three sentences (the two the C32 check does not read
  included), `dev/audit/rounds/round4/D6/claims.py`'s two headers and its
  committed register, and `tests/deployment_shape.py`'s selection-cost note with
  every per-pair count in it. When two lanes add one each in the same window, the
  merged tree's numbers belong to neither side and every one of them must be
  re-derived from the instrument, not unioned by hand.

## Friction

- `ci-autofix.md`: cost: the table sends a seat that sees `mutation-autofix` go red
  to `--pin-killed`, and on a macOS seat that drive cannot speak: run for one
  anchor of `draw_range.py` with `tests/features.py` as its only driver, it spent
  730 s on the baseline and printed `MUTATION TABLE INCONCLUSIVE -- the baseline is
  already red in tests/features.py, so no mutant's verdict means anything`, the red
  being the disclosed Accelerate arm (round 4's `## Figures`). The rule it enforces is one
  line (`killed()`: red AND failing above the baseline), so the alternative is
  exactly what was done here -- measure per site by hand and say so in the row.
- `ci-autofix.md`: unenforced: `mutation-autofix`'s repair is a `pull_request`-only
  lane (`.github/workflows/tests.yml:895-899`), so on a `DIRTY` head the rule's
  "wait for the bot commit" instruction has no bot to wait for -- and a body that
  disposed of its sites as "left to `mutation-autofix`" was not wrong about the
  rule, only about the head. Evidence: round 3's verdict at `3c9fe53fa` --
  `30 runs, every one head_sha 3c9fe53fa ... All four workflow runs at this head
  are event=workflow_dispatch ... no pull_request-event run fired, because the PR
  is CONFLICTING/DIRTY` (its `evidence/checks_head3.tsv`), with `ABSENT` against
  five of the seventeen required contexts in its `evidence/required3.txt`. At
  `6f420a1f7`, once the conflict was cleared, this seat read the same listing and
  found all seventeen present and `mutation` the only red one.
- `ci-autofix.md`: cost: the pin lane's green tick and its work are different
  things. Three shards ran 2 h 14 min on this branch's `6f420a1f7`; two of them
  measured nothing (`MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s)
  timed out, 5 not started for --budget-minutes`, `measure: skip-measure-failed, 0
  anchor(s)`) because each site's admission cost over the 24 drivers
  `drivers_for` names for one module never fit the window; the job still answered
  its own `AUTOFIX: changed` on the third shard's two pins, and stood green. A seat
  told to
  "wait for the bot commit" waits for a commit that can carry 2 of 15 dispositions
  while the lane's own tick says it repaired the refusal. Evidence: the three job
  logs quoted under round 4's `## Figures`; the branch's 13 remaining sites and their rows.
- `gate-scoping.md`: stale: this branch's `tests/closures.json` conflicted with
  main's re-sorted table because the branch carries the ledger driver as it stood
  at its own merge base, and main moved `tools/merge/ledger_merge.py` afterwards
  (`918a8c306`, `17f7e0296`, `cb7d99ee3`). So the merge driver that exists to
  settle that file refuses it -- `LEDGER-MERGE: refused tests/closures.json: a
  side is not in its writer's own JSON format` with the checkout on the branch,
  against `LEDGER-MERGE: resolved` with the same clone on main (round 3's
  measurement) -- and no rule names the way out: `grep -rln ledger_merge
  dev/governance/rules/ .claude/rules/ .cursor/rules/` returns nothing. The route
  is main's own `tools/merge/ledger_merge.py --resolve tests/closures.json`. At
  THIS merge the branch already carries that route, so the driver ran by itself and
  printed its own resolved marker (the `LEDGER-MERGE` line in `## Head`), and no
  hand repair was needed: the skew was closed by merging main, which is the
  mechanism the friction note asks to be written down.
- `claim-files.md`: cost: the merge that resolves a census conflict has to be
  driven by a seat with the instruments, not by the merge-main bot, and no rule
  says which files count as "driver files". #2059 added the section (`ci-autofix.md`,
  "A driver-file conflict: one bot merges it, none autofixes it") naming
  `.github/workflows/merge-main.yml` as the only pusher of a `ci: merge main`
  resolution, and this PR's three conflicts are not driver files at all -- they are
  census prose, where the bot's drivers would union two wrong numbers into one.
  The measurement here is what stopped that: both sides' `74` was the merged tree's
  `75`, and a clean-resolving merge could have shipped the false pair. Standing
  cost of the check that catches it: `claims.py` ~90 s plus `entities.py`'s
  `#1218` rows in the gate, against a review round at ~1 h.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
