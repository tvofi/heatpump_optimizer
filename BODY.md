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

`90b9e87f7dece277cfbf46cbc64b2b3f816d841c`. Round 4, on the head CI last ran
(`6f420a1f7`), which is `origin/main` merged into the branch: the pull request was
DIRTY on `tests/closures.json` alone -- the branch's older ledger driver refuses
main's re-sorted table -- and that one file was finished with the merged tree's
own copy, `tools/merge/ledger_merge.py --resolve tests/closures.json`, which
printed `LEDGER-MERGE: resolved`, `closures.tests/entities.py: merged as a set
(231 entries)` and `inert_reads.tests/harness_headers.py: merged as a set (536
entries)`. No other file was resolved by hand, so the code under review is
unchanged by that merge. On top of it sit `acba8517d` (107 lines added to
`tests/features.py`: twelve checks and one population helper), `279212233` (14
ledger rows, 84 lines, under `tests/mutation_ledger/killed_by/draw_range.py/`
only -- `tests/mutation_budgets.json` untouched), and `90b9e87f7`, the merge of
`a456c5ed` -- `ci: pin killed mutants`, the commit this branch's own
`pull_request` run finally produced once the conflict cleared, whose summary line
reads `AUTOFIX: changed` (job 113801958940). That commit pins two of the fifteen
anchors on the lane's own measurement, and both of its paths collided add/add with
this branch's rows for the same anchors: both are resolved in the LANE's favour,
so twelve rows here are the seat's and two are the lane's, and `draw_range.py`
holds no undisposed site.

Everything below was measured at `90b9e87f7`, except the whole-file `features.py`
arms, which were measured with `tests/features.py` exactly as `acba8517d`
committed it -- `git diff --name-only acba8517d HEAD` lists only
`tests/mutation_ledger/` paths, so no figure depends on a file that moved after.
Main was `b2b6acd64cde` (`date -u`: 2026-10-09T11:45:55Z).

## Mutation proof

Control -- `ALL 51 DR BLOCK PASSED`. The block is sliced out of `tests/features.py`
and executed, never a copy of it, so the 51 are the file's own 51:
`PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/drblock.py`.

Each arm below is one production line edited in a COPY of the package and run
through that block (`/Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/mutproof.py`;
the checkout is never mutated, which is `mutation_table.py`'s own rule, and an arm
whose needle is not unique refuses rather than reporting a pass). Result:
`MUTPROOF: 16 of 16 arm(s) went red (0 survived)`.

- M1 the fold call replaced by the freeze read alone: `1 of 51 FAILED` --
  `the per-cycle settlement folds one running sample: (drawn, space asked)`
- M2 `plan_writes_power` returns False: `2 of 51` -- `plan_writes_power is exactly
  a frequency write (S1)`, `S4 where the plan writes the frequency: None, the draw
  is its own echo`
- M3 the evidence gate removed (engage on sample count alone): `6 of 51` -- both
  null controls, `a sub-floor duty-cycle average overdrawn by the running pump is
  no evidence`, `S4 with no evidence, or a different configuration: None`, and two
  of this round's checks (`the factor boundary is not a disagreement`, `12 of 48
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
- M12 the standby floor removed from S2: `2 of 51` -- `S2: standby draw is not a
  running sample`, `the standby floor is 0.25 kW counted in the test ...`
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

Three shapes at 20 seeds each through the lane's own harness
(`dev/audit/harnesses/draw_range_evidence.py`), and each is a check in the block
too, so the null is pinned rather than observed once:

- `over` (the synthetic overstated nameplate): engaged **20/20** seeds, effective
  `(1.268, 1.739)` on a switch+setpoint surface, `(1.0, 1.739)` on a duty-cycling
  one, `None` on a frequency write.
- `null` (the pump draws exactly what it is asked): engaged **0/20**, `None` on
  every surface. A clamp that engaged here would rewrite a correctly configured
  install's plan.
- `mild` (a correctly sized 6 kW pump part-loading at 1-2 kW, drawing what it is
  asked within +/-10 %): engaged **0/20** though its running P90 (1.943) is under
  half its configured max -- a low ceiling alone is not a contradiction, which is
  the whole reason the latch exists.
- Contrast, recorded so a consumer does not over-read the nulls: `mild-indep`, the
  same pump whose draw does NOT follow the ask, engages **20/20**. There the plan's
  per-step levels are genuinely wrong about the draw, which is the evidence the
  latch is for -- so `engaged` is not a claim that the nameplate figure is wrong.
- And at the plan level there is nothing to compare, by design: no solve reads
  `draw_range` in 7a, so every plan is byte-identical to main's. That is what the
  golden, `optimality` and `stress` lanes measure at this head (CI's scoped run),
  and `S4 where the plan writes the frequency: None` is the per-install arm of the
  same claim.

## Figures

Main-tip-dependent figures: origin/main was `b2b6acd64cde652676a568e93c05f021571ebe5e`
and every command below ran at `2026-10-09T10:42:50Z` or later (`date -u`).

- Scope of the gate -- `D=$(mktemp -d); ~/.local/state/hpo/venv-ci/bin/python3
  tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D";
  cat "$D/scope.txt"` -- `MODE: SCOPED -- 28 script(s) run, 5 scoped out` (the
  merge base is `c518447eb804`). Keyed on the mode line, never the count.
  `scope.run` names 28 scripts. Run locally and green at this head: the 7a block
  (51/51), `tests/structure.py`, `tests/layout.py`, `tests/mutation_table.py
  --pin-killed` (its own line below), and `tests/features.py` to its end. Left to
  CI's scoped run, per the owner's heavy-scripts ruling (2026-10-07) and because
  this seat's host is at load average ~50, which reddens load-sensitive timing
  arms rather than code (`entities.py`'s gate-lease arm, `harness_headers.py`'s
  wall-limit arms -- disclosed at round 3): `stress`, `optimality`, `golden`,
  `env_drift`, `backtest`, `boost_drift_replay`, `entities`, `harness_headers`,
  `arch_score_head`, `deployment_shape`, `debug_collect`, `doc_claims`,
  `config_flow_steps`, `solar_alignment`, `wood_advisor`, `plan_view`,
  `manual_plan`, `block_duty`, `edge`, `validate`, `typing_ruler`,
  `finite_boundary`, `guard_pins`, `md_tables`, `card`, `card_drift`.
- Whole file -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tests/features.py` -- `1 of 3911 FEATURE CHECKS FAILED`. The one failure is
  `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the
  half-price floor's plan refined under it` (shipped 110.4366 against 110.1297),
  a solve this diff does not reach, on the seat's Accelerate BLAS; the canonical
  CI environment runs the file green -- `fast (3.14)` is `success` at `6f420a1f7`
  (round 3 re-took both of the arm's figures, 110.4366 and 110.1297). 3911 = the
  3899 that head printed plus the twelve checks of `acba8517d`.
- Pin drive of the sites the diff adds -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/drmut.py --only-unpinned --json ...`
  -- `DR MUT: 15 killed of 15 site(s) driven; baseline failing_count=0`. It writes
  each site's OWN mutant (the inventory's `new` text over the site's line, exactly
  `mutation_table.py:3372` does it), runs the block, restores, and applies
  `mutation_table.killed`'s rule: red AND failing above the baseline.
- Both kill forms on the whole file -- `~/.local/state/hpo/venv-ci/bin/python3
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/wholefile.py` --
  baseline `1 of 3911`; the `CONST` arm (`RUNNING_FLOOR_KW = 0.5`) `2 of 3911`,
  killing `S2: the standby floor is 0.25 kW counted in the test ...`; the
  `GUARD_OFF` arm (`if seen is None:` -> `if False:`) raises before the closing
  line, counted `2` by `failing_count`'s traceback term against the baseline's
  `1`. The two forms are what a block-only measurement could have overstated.
- The canonical route, at this head -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 tests/mutation_table.py --pin-killed
  --base origin/main --scripts tests/features.py` --
  `4622 unpinned site(s) of 5933 candidate sites, 4624 at the ratchet base
  c518447eb804c72122a7c4ecd479de2eeda62452; the ledger agrees with the
  deterministic inventory`, then `PIN KILLED: nothing to pin`, rc=0. The count
  FELL BELOW the base, which is what the ratchet asks.
- What CI's pin lane actually measured at `6f420a1f7`, read out of its job logs
  (`gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`): `mutation-autofix`
  (113801958940) `AUTOFIX: changed`; `mutation-pins (2)` (113756244273) `PIN
  KILLED: 2 pinned, 3 left unpinned (3 survived, 0 not started for the budget, 0
  timed out, 0 skipped)`, naming `:175 GUARD_OFF -- killed by tests/features.py` and
  `:262 GUARD_OFF -- killed by tests/structure.py` as pinned and `:48 CONST`,
  `:51 CONST`, `:102 CMP_BOUND` as living; `mutation-pins (1)` (113756244286) and
  `mutation-pins (3)` (113756244274) each `MUTATION TABLE REFUSED -- nothing was
  measured: 0 mutant(s) timed out, 5 not started for --budget-minutes` and
  `measure: skip-measure-failed, 0 anchor(s)`, after 2 h 14 min. The commit those
  shards produced is `a456c5ed`, merged here.
- The engine's drive, asked for one of these anchors -- `PYTHONPATH=tests/hastub
  ~/.local/state/hpo/venv-ci/bin/python3 tests/mutation_table.py --anchor
  "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 443a79fc"
  --scripts tests/features.py` -- `baseline tests/features.py: rc=1 failed=2 730s`
  then `MUTATION TABLE INCONCLUSIVE -- the baseline is already red in
  tests/features.py, so no mutant's verdict means anything`, naming
  `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the
  half-price floor's plan refined under it` (shipped 110.4366, seeded with the
  half-price plan 110.1297). The drive's own baseline line reads `failed=2` where a
  direct run of the same file reads `1 of 3911`: the seat is at load average ~50 and
  the arm's margin is a solve, so the count is load-sensitive while the verdict --
  the baseline is red here -- is not. That is the measurement behind "the rows are
  seat-measured", not a reading of the source.
- Predictor -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tools/pr/ci_predict.py --base c518447eb804` -- `CI PREDICT: no closures or fast
  red predicted against c518447eb804 (a data-file read is not seen)` and **no**
  `ADDED UNPINNED` line; at `acba8517d`, before the rows were recorded, the same
  command printed `CI PREDICT: 14 unpinned site(s) the diff adds` and the 14 keys.
  That command is the rule that enumerates the class; `## Unpinned sites` is its
  output, transcribed by a script (`sites_table.py`) rather than by hand.
- Ledger, source-only (seconds, no mutant run) -- `~/.local/state/hpo/venv-ci/bin/python3
  /Users/timmalmstrom/hpo-seats/live-power-clamp/scratch/r4/ledger_line.py` --
  inventory 5933, unpinned 4622, `draw_range` unpinned **0**, completeness problems
  **0**, ledger form problems **0**, `killed_by` rows 1209, `survivor_triage` rows
  83. `thermal_model.py`'s 273 unpinned sites are the pre-ratchet stock, not this
  diff's (the branch's one added site there, `plan_writes_power`'s
  `RETURN_DEL`, has been pinned since `3c9fe53fa`).
- Structure -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tests/structure.py` -- `STRUCTURE RATCHET PASSED`, 41 counting rules holding,
  against `tests/structure_budgets.json` byte-identical to main's.
- Placement -- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3
  tests/layout.py` -- `layout: GUARD: 0 refusal(s) against c518447eb804`.
- Architecture -- `~/.local/state/hpo/venv-ci/bin/python3
  tools/audit/archscore/score.py --diff origin/main` --
  `Architecture score: dS +0.0000 NULL`.
- Evidence harness -- `PYTHONPATH=tests/hastub:custom_components
  ~/.local/state/hpo/venv-ci/bin/python3 dev/audit/harnesses/draw_range_evidence.py 20`
  -- the four shapes quoted under `## Null control`.
- Claims -- `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt`
  and `... card_claimed_drift.txt`, each followed by its own verdict line: both
  `byte-identical to origin/main's`. This branch claims nothing and moves no
  fixture.
- Versions -- `git diff --name-only $(git merge-base origin/main HEAD)...HEAD --
  VERSION hacs.json RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json`
  -- prints nothing: `VERSION`, the manifest version and the release-notes heading
  are untouched.
- CI at `6f420a1f7` (the head CI has actually run, `gh api
  repos/tvofi/heatpump_optimizer/commits/6f420a1f.../check-runs`): all 17 required
  contexts exist, `mutation` the only red one -- the refusal `MUTATION TABLE
  REFUSED -- 4636 unpinned site(s) against 4623 at the ratchet base b2b6acd64...,
  15 of them added by this diff` (job 113755927879). The `pull_request` runs that
  the DIRTY state had blocked were firing again at that head, which is what let
  this round's dispositions be measured rather than promised.

## Red checks

- `mutation`, red at `6f420a1f7` -- the head CI has run most recently -- and at
  every head of this branch that the lane measured: the ratchet refusal, `4636
  unpinned site(s) against 4623 at the ratchet base b2b6acd64..., 15 of them added
  by this diff` (job 113755927879). Its answer is `ci-autofix.md`'s shape, and the
  lane did its half: it pinned the 2 sites the branch's old checks already killed
  (`a456c5ed`, `AUTOFIX: changed`), proved 3 survivors, and never started the other
  10 for the budget -- so the remaining 13 are disposed of here, in the tree, each
  with the measurement that earned it (`## Unpinned sites`). The cheaper detector exists and costs no mutant run:
  `tests/mutation_table.py`'s source-only trio (`load_budgets`, `inventory`,
  `unpinned_sites`) or `tools/pr/ci_predict.py --base <merge-base>`, both of which
  named all 15 sites and their keys before any push. Measured standing cost at this
  head on a seat at load average ~50: `9453 ms` and `17050 ms` for those two
  commands (`/usr/bin/time`-free wall clock around the call), and round 3's review
  re-derived the same refusal in 2 s on a quieter host. The cost of missing it is a
  review round, which this branch has now paid three times.
- The five required contexts that were ABSENT at `3c9fe53fa` (`pr-contract`,
  `policy-docs`, `env-matrix`, `budget-raise-gate`, `wave-script`), which is not a
  red check but a head that could not run: the pull request was `DIRTY`. The
  detector is `git merge-tree --write-tree origin/main HEAD` (seconds) plus the
  ledger driver's own marker -- with main's driver installed it prints
  `LEDGER-MERGE: resolved` and exits 0, with the branch's older driver it prints
  `LEDGER-MERGE: refused tests/closures.json: a side is not in its writer's own
  JSON format` and exits 1. Standing cost: seconds. The skew was main's, not the
  branch's: `tools/merge/ledger_merge.py` moved in `918a8c306`, `17f7e0296` and
  `cb7d99ee3` after this branch's merge base, so no detector ON the branch could
  have shown it -- the route is main's `ledger_merge.py --resolve`, which the
  orchestrator ran, and the consequence for the next seat is in `## Friction`.
- `fast (3.14)`, red twice in this branch's range and green at `6f420a1f7`:
  (a) at `325960ef`, `tests/layout.py` refused
  `placement: tools/audit/harnesses/draw_range_evidence.py re-adds a moved path;
  it lives at dev/audit/harnesses/` -- fixed here: the harness is at
  `dev/audit/harnesses/draw_range_evidence.py`, and `PYTHONPATH=tests/hastub
  python3 tests/layout.py` reads `layout: GUARD: 0 refusal(s) against
  c518447eb804` at this head, in seconds. The cheaper detector is that script run
  by hand before the push -- at this head the scoped gate SKIPS it (`SKIP
  tests/layout.py (closure: 3 files, no changed file is in its measured closure)`),
  so which scripts reach `fast` is main's recorded closure table's business, not
  this diff's, and a seat cannot assume the gate will run a placement check for it;
  (b) at `e408b9a28`, `tests/entities.py`'s `--anchor` re-drive of one site
  reported the ledger stale -- round 2 had deleted a line `mutation-autofix`
  still pinned. Fixed here by deleting that pin, and the cheaper detector is the
  source-only completeness trio of `## Red checks`'s first bullet, which refuses
  a disposition naming no generated site in seconds and with no mutant run; it
  prints `completeness problems : 0` at this head, and the same trio is what
  `mutation`'s own refusal is made of.
- `nightly-ha (stable)` and `nightly-status`, red together at `becd4e383`
  (job 113611720490): `FAILED: 2 of 64 checks: ['hb:positive_control',
  'run:exit_status']`. `hb:positive_control` is the heartbeat instrument's own
  positive control -- whether py-spy's rc=0 section names a planted 600 ms spin --
  and `run:exit_status` is the container exit carrying it; every integration check
  in that lane passed (entry loaded, a3-a13, entities, plan, a16). This diff
  touches neither py-spy nor the heartbeat harness, and no cheaper detector exists
  inside this diff's scope for an instrument's self-control: not this PR's red
  (`defect-root-cause.md`'s "not this PR's"). At `6f420a1f7`, `nightly-ha` is
  `skipped` and `nightly-status` is `failure` again -- neither is one of the
  seventeen required contexts, and `nightly-status` reports the nightly lane's own
  state rather than this head's.

## Unpinned sites

The rule that enumerates them is
`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base c518447eb804`,
whose `ADDED UNPINNED` keys are what `tools/pr/prepr.sh` step 6d writes and
`unpinned_line` matches whole. At `acba8517d` it listed 14 keys over 15 sites, all
in `draw_range.py`. **Self-correction, disclosed:** the round-3 body said all 22
of its list were "pinned by `mutation-autofix`"; 15 of them were not. The pull
request was DIRTY, so no `pull_request` run fired and the pin lane -- gated
`if: github.event_name == 'pull_request' && needs.mutation.result == 'failure'`
(`.github/workflows/tests.yml:895-899`) -- could not measure them. A lane that
cannot run is not a disposition. Each key now carries a row under the
ledger's `killed_by` tree: twelve earned by the site's own mutant taking a named
check red at `acba8517d` (the drive is `## Figures`'s pin-drive line, and each row
quotes its own FAIL), two recorded by the lane from its own drive of `6f420a1f7`.

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
rows in the ledger are 83, exactly main's count, and the drive that produced them
is the never-automated kind this rule reserves for humans.

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
site's own mutant text, both output forms re-taken on the whole file (`##
Figures`), and the rows written through `normalize` + `write_budgets` so the layout
stays the lane's. `apply_pins` re-keys against the inventory it finds, so a later
measurement of this head adds nothing: `python3 tests/mutation_table.py
--pin-killed --base origin/main --scripts tests/features.py` at `90b9e87f7` answers
`PIN KILLED -- 0 new unpinned site(s) ... to drive` and `PIN KILLED: nothing to
pin` (rc=0), after the same command run for one anchor of this file printed
`MUTATION TABLE INCONCLUSIVE -- the baseline is already red in tests/features.py,
so no mutant's verdict means anything` on this host (`baseline_refusal`, following
a 730 s baseline run) -- the drive that would have made these rows the lane's
cannot speak here at all.

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

## Friction

- `ci-autofix.md`: cost: the table sends a seat that sees `mutation-autofix` go red
  to `--pin-killed`, and on a macOS seat that drive cannot speak: run for one
  anchor of `draw_range.py` with `tests/features.py` as its only driver, it spent
  730 s on the baseline and printed `MUTATION TABLE INCONCLUSIVE -- the baseline is
  already red in tests/features.py, so no mutant's verdict means anything`, the red
  being the disclosed Accelerate arm (`## Figures`). The rule it enforces is one
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
  logs quoted under `## Figures`; the branch's 13 remaining sites and their rows.
- `gate-scoping.md`: stale: this branch's `tests/closures.json` conflicted with
  main's re-sorted table because the branch carries the ledger driver as it stood
  at its own merge base, and main moved `tools/merge/ledger_merge.py` afterwards
  (`918a8c306`, `17f7e0296`, `cb7d99ee3`). So the merge driver that exists to
  settle that file refuses it -- `LEDGER-MERGE: refused tests/closures.json: a
  side is not in its writer's own JSON format` with the checkout on the branch,
  against `LEDGER-MERGE: resolved` with the same clone on main (round 3's
  measurement) -- and no rule names the way out: `grep -rln ledger_merge
  dev/governance/rules/ .claude/rules/ .cursor/rules/` returns nothing. The route
  is main's own `tools/merge/ledger_merge.py --resolve tests/closures.json`, which
  the orchestrator ran; `## Head` names it.
