The foundation for clamping the plan to metered power (#201, decision comment 6067353918, under mandate 6067089637), PR 7a of the live-fix wave's binding design note. No solve reads anything added here; 7b applies the clamp after this merges.

The planner books `min_electrical_power`..`max_electrical_power` as the draw a step may run at and credits COP times that draw as heat. Nothing checked those figures against the meter: a pump whose configured maximum is several times its real running draw has every plan book levels it never reaches (the synthetic shape used throughout: configured 1-10 kW, asked U(3, 10), drawing U(1.2, 1.8)). This PR adds the shared observed-draw component the wave's other fixes consume:

- **S1** `InstallCapability.plan_writes_power()` (`thermal_model.py`): the plan sets the draw itself only with a frequency write; everywhere else the meter reads the pump's own choice.
- **S2** `draw_range.is_running_space(...)`: one running-sample filter over plain values -- draw above standby (`RUNNING_FLOOR_KW = 0.25`), space circuit asked and no hot water asked (both through `planned_draw_runs`, the plan-running rule's registered owner, with no modulation floor), learners not frozen on the meter, no immersion/capped compressor, no defrost in the closed interval.
- **S3** `draw_range.DrawRange`: a window of `WINDOW = 336` `(drawn, space asked)` running samples; `observed()` is P10/P90 from `MIN_SAMPLES = 48`. An evidence latch `engaged` sets when at least 25 % of running samples disagree by more than 1.25x between asked (at or above the configured floor) and drawn. It is keyed to the configured `(min, max)` it judged: a changed configuration clears the samples and the latch, and a stored record whose configuration is unreadable, absent or non-finite is dropped whole on load (samples included), so no reader of `samples` sees pairs with nothing to judge them against. It is not released by the metered range, because once a clamp is in force the plan stops out-asking the pump and the evidence fades -- re-testing it would re-book the fiction a window later.
- **S4** `draw_range.planned_range(draw, params, cap)`: the effective range, or `None` (configured stands). `None` where `plan_writes_power()` (the draw is the plan's own echo, so a clamp could only ratchet down); on an install that can duty-cycle the min end stays configured (a sub-floor level is an average a pump at its metered floor delivers), so a correctly configured duty-cycling plan is unchanged.
- **Hosting**: `AccuracyTracker.draw`, persisted as one additive `draw` key in the accuracy store document (store version unchanged at 1), domains declared in `store.py` (`draw/samples/#/0`, `#/1`, `draw/engaged`, `draw/config/#`). An install with no running sample writes no key. `draw/config/#` is one key beyond the design note's table: the latch is meaningless without the configuration it was judged under.
- **Fold**: one call in `_record_accuracy` beside `_fold_flow_lift`, passing values (`draw_range.fold(...)`), with the power-meter freeze bound on its own line before it; nothing in `draw_range.py` takes the coordinator.
- **Diagnostics (S7)**: `diagnostics.py` now publishes module views through one `(key, view)` registry, each row isolated by `_never_breaks`; `pump_duty` moved onto it and `draw_range` added (`running_samples`, `observed_min_kw`/`observed_max_kw`, `engaged`, `effective_min_kw`/`effective_max_kw`).

Paid inside the PR, so every structure metric is at or below main's budget (`tests/structure_budgets.json` is byte-identical to origin/main's) and archscore reads NULL:
- `_async_watch_learning_drift`'s non-alarmed branch shares the method's single closing `_async_save_snapshots()` instead of its own save-and-return (same calls in the same order on every path; -1 class line, which the fold's two lines spend: net 0).
- `_record_accuracy` reads `_learning_frozen(CONF_POWER_ENTITY)` once (the fold's `frozen` and the defrost settlement's gate) instead of twice; nothing between the two reads writes a freeze input.
- `wood_fuel.py` imports `utc_elapsed_seconds` from `drift`, where it lives, instead of through `accuracy`'s re-export; that edge would otherwise have closed a `thermal_model -> wood_fuel -> accuracy -> draw_range -> thermal_model` import cycle.

Generated or derived prose this module moves, updated with it: `docs/architecture.md`'s module map and its three module counts (`dev/audit/rounds/round4/D6/claims.py` re-run, its register committed), and `tests/deployment_shape.py`'s selection-cost note (#1218), where every exactly-equal pair's shared count rises by one because `draw_range.py` joins each closure that reads `accuracy.py` (`tests/closures.json`, 27 closures; CI's closure re-record is the authority).

Why not the capacity envelope (`_fold_capacity_envelope`): it folds only at >= 0.95 x nameplate commands, derives its thermal figure from the commanded level (on an overbooking install, the overbooked level itself), and floors its cap at 0.6 x nameplate, far above the clamp an overstated nameplate needs. It answers the opposite end of the range, so it is related (7b composes the ceiling through the same `power_caps_extra` channel) but not fed.

## Head

`e408b9a28fa04f5e5d732ff2c9c4e78435fca3fd`: round 2 on the PR head `becd4e383` (round 1's `7c5f647`, its delivery row `325960ef6` and `mutation-autofix`'s pins), one commit: the review's repairs.

## Mutation proof

M1-M13 were applied at `50760e82b` (round 1) and R1-R3 at this head; each time the new check block in `tests/features.py` run (`PYTHONPATH=tests/hastub:custom_components:tests`, block driven on its own), restored:

- M1 the fold call in `_record_accuracy` replaced by the freeze read alone: `FAIL the per-cycle settlement folds one running sample: (drawn, space asked)`
- M2 `plan_writes_power` returns False: `FAIL plan_writes_power is exactly a frequency write (S1)`, `FAIL S4 where the plan writes the frequency: None, the draw is its own echo`
- M3 evidence gate removed (engage on sample count alone): `FAIL null control: a pump that draws what it is asked never engages`, `FAIL null control: a correctly sized 6 kW pump part-loading at 1-2 kW ...`, `FAIL a sub-floor duty-cycle average overdrawn by the running pump is no evidence`, `FAIL S4 with no evidence, or a different configuration: None`
- M4 duty-cycle min end not kept: `FAIL S4 where the install can duty-cycle: the min end stays configured`
- M5 `AccuracyTracker.from_dict` drops `draw`: `FAIL the samples, the latch and its configuration persist through the accuracy store`
- M6 defrost not excluded: `FAIL S2: defrost in the interval is not a running sample`, `FAIL and folds nothing for an interval whose closed window saw a defrost`
- M7 hot water not excluded: `FAIL S2: hot water asked is not a running sample`, `FAIL and folds nothing under a hot-water ask`
- M8 configuration change does not reset: `FAIL a changed configuration releases the latch and restarts the evidence`
- M9 `MIN_SAMPLES` not required: `FAIL short of MIN_SAMPLES running samples there is no statistic and no clamp`
- M10 `draw_range` row removed from the diagnostics registry: the block raises `KeyError: 'draw_range'`
- M11 sub-floor asks counted as evidence: `FAIL a sub-floor duty-cycle average overdrawn by the running pump is no evidence`
- M12 standby floor removed from S2: `FAIL S2: standby draw is not a running sample`
- M13 the space-running test removed from S2: `FAIL S2: space circuit off is not a running sample`
- R1 (round 1's survivor) `bottom = low` always: `FAIL a metered floor within 15 % of the configured min keeps the configured min`
- R2 (round 1's survivor) `top = high` always: `FAIL a metered top within 15 % of the configured max keeps the configured max`
- R3 `from_dict` keeps samples beside an unreadable configuration: `FAIL a record whose configuration is unreadable is dropped whole ...`, and the same for `absent` and `non-finite`

At the merge base the block fails at import (`cannot import name 'draw_range'`).

## Null control

- A pump that draws exactly what it is asked never engages (check `null control: a pump that draws what it is asked never engages`; harness shape `null`, configured 1-10 kW: engaged 0/20 seeds).
- A correctly sized 6 kW pump part-loading in mild weather -- asked 1-2 kW, drawing what it is asked within +/-10 % -- never engages, though its running P90 is under half its configured max (check `null control: a correctly sized 6 kW pump part-loading ...`; harness shape `mild`: engaged 0/20 seeds).
- Contrast, recorded so a consumer does not over-read the null: the same pump whose draw does NOT follow the ask (asked U(1,2), drew U(1,2) independently) engages in 20/20 seeds (harness shape `mild-indep`). There the plan's per-step levels are genuinely wrong about the draw, which is the evidence the latch is for.
- No solve changes in this PR; the golden and optimality scripts are left to CI's scoped run.

## Figures

- Engagement and effective range per shape and surface: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_range_evidence.py 20` (rule: `WINDOW` samples per seed, seeds 0-19; the latch's `engaged` and `planned_range` per `InstallCapability` surface).
- Structure: `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` against main's unchanged budgets.
- Architecture: `python3 tools/audit/archscore/score.py --diff origin/main` -- `dS +0.0000 NULL`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -- `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. Run locally on the head and green: structure, typing_ruler, guard_pins, deployment_shape, debug_collect, wood_advisor, solar_alignment, plan_view, manual_plan, block_duty, finite_boundary, doc_claims, config_flow_steps, edge, validate, md_tables. Run locally and red only on load-sensitive arms this diff does not touch (load average about 75 on the seat): entities.py's gate-lease timing arm ("the lease has one winner ..."), and harness_headers.py's `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` wall-limit arms (rc=124 at 72 s CPU). features.py ran locally to the end: 3891 of 3892, its one red the solver-optimality arm `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` (110.4366 against 110.1297), a solve this diff does not reach (no solve reads `draw_range` in 7a) on the seat's Accelerate BLAS, which the canonical CI environment exists for; the new block alone: 32 of 32. Left to CI: stress, boost_drift_replay, backtest, optimality, golden, env_drift, arch_score_head, card, card_drift.

## Red checks

- `fast (3.14)` at `325960ef`: `tests/layout.py` refused `placement: tools/audit/harnesses/draw_range_evidence.py re-adds a moved path; it lives at dev/audit/harnesses/`. Fixed here: the harness is at `dev/audit/harnesses/draw_range_evidence.py`, and `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/layout.py` reads `GUARD: 0 refusal(s)` at this head. The cheaper detector is that same script run before the push: about 4 s, no network. It is in this branch's `scope.run` (`tests/closure.py select`), so the seat's scoped local run was where it would have been caught; the round-1 run omitted it.
- `mutation` at `325960ef`: `MUTATION TABLE REFUSED` on the sites the diff adds -- the `ci-autofix.md` shape, repaired by `mutation-autofix` (`becd4e383 ci: pin killed mutants`), named here as that rule requires.
- `nightly-ha (stable)` and `nightly-status` at `becd4e383` (job 113611720490): `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`. `hb:positive_control` is the heartbeat instrument's own positive control -- whether py-spy's rc=0 section names a planted 600 ms spin -- and `run:exit_status` is the container's exit carrying it; every integration check in the lane passed (entry loaded, a3-a13, entities, plan, a16). This diff touches neither py-spy nor the heartbeat harness; no cheaper detector in this diff's scope exists for an instrument's self-control. Not this PR's red (`defect-root-cause.md`).

## Forward-carry

- `custom_components/heatpump_optimizer/draw_range.py` (the `DrawRange` docstring, the S3 contract its consumers read): `engaged` says the plan's running levels and the meter disagree, not that a configured figure is wrong. A correctly sized pump whose draw follows the asked level never engages; one whose own controller ignores the level engages, sized correctly or not (harness shape `mild-indep`: 20 of 20 seeds). The nameplate notice and the COP floor read it under that meaning. Also handed to the orchestrator for the wave's design note, section 6 ("2 vs 7"), which lives outside the tree.

## Unpinned sites

`python3 tools/pr/ci_predict.py --base 4dbe5aace` lists 22 sites the diff adds that `mutation-autofix` has not yet pinned (round 1's pins landed in `becd4e383`); each is left to `mutation-autofix` after the push (`ci-autofix.md`), and a survivor gets a written triage in a follow-up commit, never an automated one:

- `custom_components/heatpump_optimizer/draw_range.py:45 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:48 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:51 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:54 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:58 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:60 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:63 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:99 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:102 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:103 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:104 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:113 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:116 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:118 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:140 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:142 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:175 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:175 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:185 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:262 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/draw_range.py:271 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1261 RETURN_DEL`: pinned by `mutation-autofix`

## Friction

none
