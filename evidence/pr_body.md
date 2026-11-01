## Re-cut

This is the re-cut after round 3 of the fix review (`verdict/3050`, blocked at `2be13c572cf34a475d18e3f5e2dbde4f9ff8482a`, class `metric-gamed`). The body is replaced as a whole. Every figure in it was re-taken in this pass, at the head named under `## Head`. The exception is the red-history entries under `## Red checks`, which `pr-contract` requires and which cite their own jobs.

The block had three items:

1. The arm call in `async_arm_system_identification` put six arguments on one 125-column line. The `hold_reason` call in `_run_system_identification` kept its closing parenthesis on its last argument's line. Together these hid 5 layout lines from `tests/structure.py`, so the budgets read 8049 / 17642 where the honest figures are 8054 / 17647.
2. The #1523 null-control marker in `tests/features.py` (`_P5_CONSULT`) matched only the hugging layout.
3. No check separated the ceiling store's median from an upper quantile.

This re-cut changes only what those three items need, in three files:

- `coordinator.py`: the two calls are laid out normally, using the review's null re-wrap verbatim. No production logic changed.
- `tests/structure_budgets.json`: re-recorded at the honest 8054 / 17647. The reason is in commit `e81bf9dbf`'s message. The merge with origin/main composed main's own deltas onto them, to 8051 / 17645.
- `tests/features.py`: the marker is keyed on the consult expression alone, and one item-29 check is added.

Nothing outside the block changed. `git diff 2be13c572 e81bf9dbf --stat` lists exactly those three files (18 insertions, 9 deletions).

**The merge (repair of the refused handoff).** The re-cut tip `e81bf9dbf` was refused by `prepr.sh`: two predicted reds on `governance / wave-script` (the `AGREEMENT UNMERGED` and `GRADER UNMERGED` arms), because origin/main had moved and `tests/features.py` no longer merged. The head is now `deceb3de7`, a merge of origin/main `d052f80f7` into `e81bf9dbf` (merge, not rebase). The resolution:
- `tests/features.py`: both sides appended a tail block. The resolution keeps this PR's R10-CEILING-PROBE block, then main's R10-HOTFIX-AWAY-PRESENCE block. `diff <(git diff 1a8051350 e81bf9dbf -- tests/features.py | grep '^[-+][^-+]' | sort) <(git diff origin/main HEAD -- tests/features.py | grep '^[-+][^-+]' | sort) && echo PR_DELTA_PRESERVED` prints `PR_DELTA_PRESERVED`.
- `tests/structure_budgets.json` and `tests/closures.json` were resolved by the repository's ledger merge driver: `class_excess_loc` 17653 + both deltas = 17645, `max_class_loc` 8059 + both deltas = 8051, and `inert_reads.tests/harness_headers.py` merged as a set.

No other file changed in the merge beyond main's own commits. Every figure below was re-taken at `deceb3de7`.

R10-CEILING-PROBE: the cheap-night ceiling probe, and the system-identification experiment's step reaching a flow set-point install.

Issues #2498 and #2808. The roster lists neither under its `fixes`, so this body names them without a closing keyword. Closing them is the orchestrator's call.

A set-point-driven install's plan rarely writes the flow ceiling. The metered draw window is therefore censored at the top, and the plugin cannot learn the pump's real maximum (the owner's case: configured 5 kW, believed near 3 kW). This adds a second experiment kind, the ceiling probe, inside the existing cheap-night system-identification gates:

- It commands the configured maximum, and the arbiter writes the ceiling for it.
- The metered draws of those intervals go to a separate store on `DrawRange`.
- The store's raw median is the learned top. It is published in the diagnostics, and R10-COP-GATE part D consumes it.

The design is the approved architect note `dev/programme/designs/R10-CEILING-PROBE.md` at `design/r10-ceiling-probe` 2212054e93c344d62762ac52e3b891bcce93d31d, as amended by its review `design-verdict/r10-ceiling-probe` 621e26313113ce925f7442cb935d0660a2505179. Where the two differ, carries 29-34 supersede the note. Items 7-28 come from the note and from `design-verdict/R10-CEILING-PROBE` e8da829f15771f047ba63b392b15af4d0fe99224. The orchestrator's s9 ruling (roster carry 6) makes that shape final.

**What changes, by owner.**

- `sysid.py` owns when the experiment runs and what it commands.
  - `armable(...) -> (kind, why)` picks the kind:
    - The fit runs while the house learner is unconverged and its own `min_days_between_runs` clock allows.
    - Otherwise the probe runs where the install can run one and the probe's clock allows: 7 days while unlearned, 30 once the store has a learned top.
    - A refusal is published in `result.reason`.
  - The probe's clock is the newer of two times: the store's newest sample, which persists in the accuracy store, and this process's last probe step (`probe_run`). A restart therefore cannot reset it (item 7). The converged denial in `conditions_met` applies to the fit only.
  - A flat price horizon refuses the probe. The fit's price gate is unchanged.
  - `probe_step_hours(...)` is the duration search:
    - It tries whole cycles at the configured maximum's heat, longest first. It returns the first whose predicted peak fits the comfort bound: `max_excursion_c` less the two-zone headroom only (item 14).
    - Below `PROBE_MIN_CYCLES` the arm aborts.
    - The duration found is stored in `_step_hours`, and that is what `step()` compares against (item 15).
  - A probe ends with its last step interval and hands back to the plan without relaxing. It completes uncompleted, with its outcome in `reason`, so `_adopt_system_identification` adopts nothing.
  - `stand_down(reason)` holds an armed experiment that has not started, with the reason published as `held`. A started one still aborts (#2808).
  - `hold_reason(...)` makes the stand-down decision for the coordinator: mode, the learners' freeze, an unread room, and `quiet_windows.quiet_reason`.
  - `arm_from_config(...)` is the arm. It is a module function, not a method, because `SystemIdentification` is over the 300-line limit.
  - The view gains `kind`, `held` and `last_attempt`.
- `pump_arbiter.py` owns how an action becomes a set-point.
  - `_experiment_kw(inp)` reads the experiment's commanded power before the plan's `power_schedule` (item 19).
  - `_planned_duty` returns `space` where `planned_draw_runs(power)` holds (item 32), and `idle` otherwise.
  - `_flow_target` maps that power through `flow_setpoint_for_level`. The install reads in `_flow_command` moved into `thermal_model.flow_setpoint_driven`, which the probe's eligibility shares (item 21).
- `draw_range.py` owns what a sample teaches.
  - `DrawRange.ceiling` is a deque of `(drawn_kw, epoch_s)`.
  - `fold(..., experiment_s=)` routes an experiment interval that `takes_ceiling` to the store and not to the window.
  - `learned_max_kw(now_s)` is the store's median. It is `None` below `CEILING_MIN_SAMPLES`, past `CEILING_LAPSE_DAYS` after the newest sample, or when the newest sample is ahead of the clock. It applies no agreement test (item 29).
  - Two ordinary intervals written at the ceiling that draw more than `AGREE_TOLERANCE` above the learned top drop the store (item 8).
  - The store and the overdraw count persist in the accuracy document.
- `coordinator.py` is wiring only.
  - `_pending_prediction` gains `"mode"`, and the fold routes on it (item 30).
  - The arm is one call, `sysid.arm_from_config`.
  - `_run_system_identification` asks `sysid.hold_reason` and calls `stand_down`.
- `quiet_windows.py`: `quiet_reason(config, now)` names a step inside a configured quiet off or silent window. The experiment stands down inside one: held while armed, aborted once started.
- `thermal_model.py`: `flow_setpoint_driven(config)` and `ceiling_probe_install(config)` sit beside `probe_install`.
- `sensor.py`: `ModelStatusSensor` publishes a recorded `system_identification_outcome` row. The view stays unrecorded (item 17).
- `store.py`, `accuracy.py`, `diagnostics.py` and `payload.py` declare, persist, pass the clock to, and type the new cells.

**Roster carries, answered.**

- Carry 1 (#2465's three):
  - (a) The set-point-to-draw gain is measured here at the one level the probe commands, the ceiling, and that draw is stored as the learned top. The levels between gate and ceiling stay uncalibrated, as the approved note scopes the probe to the top. That residual is forward-carried to R10-COP-GATE-D (`## Forward-carry`).
  - (b) The real maximum is reached by the ceiling probe, folded into the system-identification experiment.
  - (c) A gate-held draw above idle is refused by `takes_ceiling` and stays out of the store.
- Carry 2 (#2808): a converged house arms the probe instead of an experiment that cannot run (`armable`). The pump mode, a learning freeze or an unread room holds an armed experiment that has not started, and aborts one that has (`stand_down`, decided by `sysid.hold_reason`). The outcome is the recorded `system_identification_outcome` attribute (item 17).
- Carry 3 (the three blockers):
  - (1) Actuation: `_experiment_kw` feeds `_planned_duty` and `_flow_target` (items 19, 32). The harness's level arm writes the ceiling at 5.0 kW (Figures).
  - (2) The probe-only run on converged houses, with its 7- and 30-day clocks (items 7, 16).
  - (3) The top is learned from a ceiling store separate from the window, with the lapse and the overdraw drop as its re-test (items 8, 12, 29).
- Carry 4 (the approved r2 ruling): items 7 and 8, as described under `draw_range.py` and `sysid.py` above.
- Carry 5 (R10-COP-GATE part D): the raw accessor of item 29, now pinned against the median's mean, extreme and upper-quantile alternatives. Its interface goes forward under `## Forward-carry`.
- Carry 6 (the s9 ruling): items 29 to 34 bind as written.

**Departures from the note.**

- `button.py` is unchanged. Its availability at main is already `not system_identification_active`, which admits every armable kind. The refusal is published through the recorded outcome row.
- The accessor takes the clock, as `learned_max_kw(now_s)`. `draw_range` reads no clock, and the lapse is a clock. This is forward-carried to R10-COP-GATE-D.
- `stand_down` holds an armed experiment for every reason the coordinator's gate names: the pump mode, the learners' freeze and the unread room.
- Files beyond the note's seven: `thermal_model.py`, `quiet_windows.py`, `store.py`, `accuracy.py` and `diagnostics.py`. Each carries one predicate, one declaration or one argument. The quiet-window stand-down is a seam the step-8 enumeration returned (Figures).
- `tests/golden/claimed_drift.txt` claims the five `coord_*` fixtures for the new view keys and the outcome row. This re-cut does not touch it.

**Alternatives.**

- Probe samples in the rolling window, with `MIN_SAMPLES` lowered: rejected, because it moves the clamp for every install.
- Routing on `_current_action` at the fold: rejected, because it reads the next interval's mode.
- A second capture for the pair: rejected, because `_pending_prediction` already carries the interval's own split and command (#2262).
- The 15 % rule in the accessor: rejected, because part D owns it (item 29).
- Paying the ratchet by moving a `SystemIdentification` method to module level verbatim: not taken, because that is a mechanical split. The arm and the stand-down decision moved as module functions instead.
- Paying the re-cut's 5 lines: no payment that improves code was found inside the block's scope. Any further line removal in the coordinator class would be new scope, which a minimal re-cut excludes. So the budgets are re-recorded at the honest layout. Both still move down against origin/main.

## Head

`f5c4a8c75b4d796b3d0001e5a37ee08408cc590a` merges the authored code head `deceb3de7ee1f01a1e0f6ddd3d93acede6c68e41` and then merges origin/main `d052f80f7` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`deceb3de7ee1f01a1e0f6ddd3d93acede6c68e41`. It is the merge of origin/main `d052f80f7f81d42db5c57a55ebaef7056c7ce01a` into the re-cut tip `e81bf9dbf0beec990324b61335b62d4267b87e54`. That commit's parent is `fcfc221ff`, whose parent is the reviewed PR head `2be13c572cf34a475d18e3f5e2dbde4f9ff8482a`. The merge base is origin/main `d052f80f7f81d42db5c57a55ebaef7056c7ce01a`.

- `fcfc221ff`: the re-wrap of the two calls, the marker re-key, and the median-versus-p90 check.
- `e81bf9dbf`: `python3 tests/structure.py --record --allow-regression=...`, with the reason in its commit message.
- `deceb3de7`: the merge of origin/main described under `## Re-cut`.

## Mutation proof

The block in `tests/features.py` starts at `# --- R10-CEILING-PROBE (#2498, #2808)` and now holds 62 checks. `python3 tools/audit/seat/features_block.py "# --- R10-CEILING-PROBE (#2498, #2808)" "# R10-HOTFIX-AWAY-PRESENCE (tvofi, 2026-10-30"` at the head prints `ALL 62 FEATURES BLOCK PASSED`. The END argument is needed since the merge, because main's block now follows this one and the block runner otherwise runs to the file's close.

- **This re-cut's check.** The p90 mutant `np.median` -> `np.percentile([...], 90)` in `DrawRange._ceiling_median` (the review's `evidence/mut_median_p90.diff`) gives these results:
  - Block: `1 of 62 FEATURES BLOCK FAILED`, failing `item 29: the accessor is the median, not an upper quantile -- nine intervals at 3.0 kW and three at 4.0 kW give 3.0, where the 90th percentile is 4.0`.
  - Whole suite: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `1 of 4742 FEATURE CHECKS FAILED` (rc=1), and that row is the only `FAIL`.
- **The #1523 class check, keyed layout-independently.** In `coordinator.py`, replace `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)` in the `hold_reason` call with `None`. Then the class check and its null control, run alone (header, P5 imports, `_P5_READS` through the null control), print `2 of 2 P5 CLASS CHECKS FAILED`. Failing:
  - `#1523 class check: every learner feeder ... [undispositioned ['_run_system_identification']; ...]`
  - `#1523 class check null control ... [['_run_system_identification']]`
- **The mutation inventory.** Every `mutation_table.candidates` site on the diff's changed production lines was run against the merge base `d052f80f7`, re-taken at `deceb3de7`: 79 sites. Each mutant ran alone through the same block in a worktree copy of the head, with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared. A first pass without those settings read stale bytecode across same-size mutants and was discarded. The block kills 76. The other three:
  - `pump_arbiter.py:620 GUARD_OFF` (`_flow_command`'s guard): killed by the whole `tests/features.py`, 1 of 4742 (`## Figures`).
  - `sysid.py:1466 GUARD_OFF` (the fit's `elif plant is not None:` branch): killed by the whole `tests/features.py`, 39 of 4742 (`## Figures`).
  - `sysid.py:1358 RETURN_DEL` (`probe_step_hours`'s closing `return None`): equivalent, and triaged at `tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json`.
- **Failing test first.** The new check fails under the planted p90 mutant and passes on the production median. It pins existing production code, so it cannot fail before a fix: its failing arm is the mutant, shown above.

## Null control

- **The median check.** At `2be13c572` with the same p90 mutant, the block prints `ALL 61 FEATURES BLOCK PASSED`, because the earlier checks cannot see an upper quantile. The added check is what turns it red.
- **The marker.** The P5 class check and its null control were run alone at three trees:
  - At this head: `ALL 2 P5 CLASS CHECKS PASSED`.
  - At this head with `tests/features.py` from `2be13c572` (the old single-line marker on the re-wrapped tree): `1 of 2 P5 CLASS CHECKS FAILED`, the null control reading `[[]]`. This is the review's suite-red.
  - At `2be13c572` itself: `ALL 2 P5 CLASS CHECKS PASSED`.

  So the old marker passed only in the hugging layout, and the new one passes in the normal layout.
- **The structure figures.** At `fcfc221ff` (re-wrapped, before the re-record), `python3 tests/structure.py` prints `FAIL class_excess_loc 17647 > 17642 (+5)`, `FAIL max_class_loc 8054 > 8049 (+5)` and `2 STRUCTURE BUDGET(S) BREACHED`. Those 5 lines are the layout the review named.
- **The finder's harness.** The draw arm reads flat at both ends, as the fix rightly leaves `observe` alone. The level and store companions read the defect at the base and not at the head (Figures).

## Figures

At `deceb3de7ee1f01a1e0f6ddd3d93acede6c68e41`, merge base origin/main `d052f80f7f81d42db5c57a55ebaef7056c7ce01a` (origin/main's tip when these were taken, 2026-11-01 UTC), unless a line names another tree.

- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4742 FEATURE CHECKS PASSED`, rc=0. The row `#1523 class check null control: dropping the experiment's consult re-opens exactly its seam` is `ok`. The control is under `## Null control`.
- `python3 tools/audit/seat/features_block.py "# --- R10-CEILING-PROBE (#2498, #2808)" "# R10-HOTFIX-AWAY-PRESENCE (tvofi, 2026-10-30"`: `ALL 62 FEATURES BLOCK PASSED`. Under the p90 mutant: `1 of 62 FEATURES BLOCK FAILED`. At `2be13c572` under the same mutant: `ALL 61 FEATURES BLOCK PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, with `RESULT max_class_loc=8051` and `RESULT class_excess_loc=17645`. At the merge base `d052f80f7`, the same command reads 8056 and 17651. The class table, per class, at the merge base and here:
  - `HeatPumpOptimizerCoordinator`: 8056 -> 8051 LOC (-5). This moves both `max_class_loc` and `class_excess_loc` by -5. The payment is the move of the arm's configuration reads and the stand-down decision into `sysid.arm_from_config` and `sysid.hold_reason`, measured with both calls laid out normally.
  - `SystemIdentification`: 1065 -> 1064 LOC (-1 on `class_excess_loc`).
  - `DrawRange` stays under the 300-line limit and costs nothing.
  - `class_excess_loc` totals 17651 -> 17645 (-6).
  - `git diff origin/main -- tests/structure_budgets.json` changes `class_excess_loc` 17651 -> 17645, `max_class_loc` 8056 -> 8051 and `recorded_at`, and no other key. No key rises against origin/main.
- `python3 tools/audit/archscore/score.py --diff d052f80f7f81d42db5c57a55ebaef7056c7ce01a`: `Architecture score: dS +0.0006 IMPROVES` (`coord_footprint 2387 -> 2386`).
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, governance or instrument red predicted against d052f80f7f81` (via `prepr.sh`'s `ci predict` step). It lists no ADDED UNPINNED site.
- `PYTHONPATH=tests/hastub python3 tests/guard_pins.py`: `ALL 61 GUARD PIN CHECKS PASSED`.
- Mutation inventory (scratch driver over `tests/mutation_table.py`'s `changed_lines` and `candidates`, each mutant through `features_block.py`): 79 sites, 76 killed by the block. The three not killed are listed under `## Mutation proof`.
  - Whole `tests/features.py` under `pump_arbiter.py:620 GUARD_OFF`: `1 of 4742 FEATURE CHECKS FAILED` (rc=1), failing `null control: Observe, an indoor set-point, or a plan that writes the compressor frequency (an install that can duty-cycle, whose draw is the plan's echo) records no command`; killed
  - Whole `tests/features.py` under `sysid.py:1466 GUARD_OFF`: `39 of 4742 FEATURE CHECKS FAILED` (rc=1), first `the production sequence (declared plant) never enters identify()`; killed
- The finder's harness `dev/audit/harnesses/ceiling_probe.py` (blob `d1101c541b57a318beb87fc02ca193227d316d59`, file sha1 `4c2f42122ea7cf3f3df04aa46eeb4e19b218ac34`), run with `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/ceiling_probe.py` here and, as a copy, in a worktree at the merge base `d052f80f7`:
  - duty: base `sysid step 5.0 kW -> duty None`, head `-> duty 'space'`. The null arm (a plan action at 5.0 kW) reads `'idle'` at both.
  - draw: `one probe : ((1.5, None), False, None)` and `null 48 ceil: ((1.5, 3.0), False, None)` at both. It drives `observe`, which this change leaves alone.
  - level (companion): the base writes `35` for an experiment at 5.0, 1.5 and 0.0 kW; the head writes `55`, `38` and `25`.
  - store (companion): base `absent (no ceiling store in this tree)`; head `probe samples 12 | learned top 3.0 | window samples at the ceiling 0 | engaged False`.
- Enumeration (step 8). The rule: every reader that turns the experiment's action or kind into a command, a sample or a published state. The commands and their counts:
  - `git grep -n '"system_identification"' -- custom_components/heatpump_optimizer/` returns 17 lines here and 15 at the merge base `d052f80f7`.
  - `git grep -n '_step_kw(\|step_duty(\|plan_step_runs(' -- custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/early_cutoff.py` returns 6.
  - `git grep -n '_sysid_step_off_loop\|learner_samples=' -- custom_components/heatpump_optimizer/` returns 4.

  Dispositions:
  - Closed in this diff: `_experiment_kw`, `_flow_target`'s level, `_planned_duty`, the fold's routing in `_record_accuracy`, the outcome row (`_sysid_outcome`), and the view's publication. Also closed is the plan's quiet windows, which the override bypassed; `sysid.hold_reason` now reads `quiet_reason`.
  - Already guarded: `step_supply` (item 31), `boost.py`'s `RELEASE_SYSID` (item 13), and `early_cutoff.py`'s `_exempt` (its comfort guard; an idle draw is dropped by `takes_ceiling`'s idle rule).
  - Unchanged by design: the override's writer, `payload.py`'s reason, the state lists, and the button's entity key and names.
  - Entry points: `_sysid_step_off_loop`'s definition and its call, the `learner_samples=` argument, and `arm_from_config`'s `ident.arm`.
- Citations, re-resolved at this head:
  - `coordinator.py`: `_record_accuracy` 9725, `async_arm_system_identification` 10817, `_run_system_identification` 10826, `_adopt_system_identification` 10880. The merge moved only these; `git diff --stat e81bf9dbf HEAD` touches no other cited file.
  - `pump_arbiter.py`: `_experiment_kw` 487, `_flow_command` 607, `_flow_target` 636, `_planned_duty` 773, `step_supply` 1197.
  - `sysid.py`: `armable` 1295, `probe_step_hours` 1331, `hold_reason` 1375, `stand_down` 1507, `conditions_met` 1517, `_begin_step_phase` 1633, `_end_step` 1797, `arm_from_config` 2456.
  - `draw_range.py`: `learned_max_kw` 161, `takes_ceiling` 181, `fold` 515, `diagnostics_view` 586.
  - `thermal_model.py`: `flow_setpoint_driven` 1355, `ceiling_probe_install` 1372.
  - `quiet_windows.py`: `quiet_reason` 155.
  - `sensor.py`: `_sysid_outcome` 2050.
- `tools/pr/prepr.sh <body>` at this head against `d052f80f7`: every step is `ok` or `skip`, except one `check` line: `claim files ... tests/golden/claimed_drift.txt changed` (the branch's own earlier claims, untouched here). Its `wave-script` step prints `224 passed, 0 failed`, and its `ci predict` step prints `CI PREDICT: no closures, fast, governance or instrument red predicted against d052f80f7f81`. The two `wave-script` reds that refused `e81bf9dbf` (`UNMERGED` against `e4c9e2016a45`) are gone, because the head now merges into its base.
- Claim files: `git diff 2be13c572 HEAD -- tests/golden/` is empty, so this re-cut changes no claim. `card_claimed_drift.txt` is not in the three-dot diff, so it is byte-identical to origin/main. `VERSION`, the manifest version and `RELEASE_NOTES.md` are not in the three-dot diff.

## Unpinned sites

none: `tools/pr/ci_predict.py --base origin/main` lists no ADDED UNPINNED site at this head. The sites the PR adds are pinned under `tests/mutation_ledger/killed_by/`, and `probe_step_hours RETURN_DEL` is triaged under `survivor_triage/`. This re-cut adds no production site, because the re-wrap moves lines without changing an operator.

## Red checks

At the reviewed head `2be13c572cf34a475d18e3f5e2dbde4f9ff8482a` every concluded check is `success` or `skipped`. That is all 55 check runs on one page of 100, including `tests / fast (3.14)` (124851166636), `tests / mutation` (124851033992), `pr-contract / pr-contract` (124872779668) and `gate` (124873096218). This head has not run CI yet. The one red this re-cut could have caused is the `tests/features.py` null-control row under the re-wrap. The whole suite run above shows it `ok`, and `tests/structure.py` passes after the re-record.

Red in this branch's history, which `pr-contract` walks commit by commit since origin/main. Each was this diff's, and each was repaired before `2be13c572`:

- `tests / mutation-autofix` (job 124800000369, at `08c2477f20bc79d403cba509c0f0f06ae511edfb`): `skip-measure-failed`. Cause: the `tests / mutation` run it repairs from (job 124789115340) refused on four `sysid.py` sites the earlier re-cut added (`hold_reason` 1385 `GUARD_OFF` and 1387 `RETURN_DEL`, `arm_from_config` 2468 `GUARD_OFF` and 2473 `RETURN_DEL`), so it pinned nothing. Answer: the four entries are committed under `tests/mutation_ledger/killed_by/sysid.py/` (`99fd9e26b`), and `tests / mutation` (124851033992) is green at `2be13c572`. Cheaper detector: `prepr.sh`'s `unpinned sites` step lists the ADDED UNPINNED sites offline before the handoff. It is the standing check, and here it reads `the diff adds no unpinned mutation site`.
- `tests / fast (3.14)` (job 124789209502, at the same head): the `#1523 class check null control` row read `[[]]`, because the marker no longer matched the moved consult. Answer: the marker is now the consult expression alone, and that row is `ok` in the whole `tests/features.py` run above. Cheaper detector: one whole `tests/features.py` run per handoff, which fixer step 5 already owes and which this re-cut ran on the re-wrapped tree.

## Forward-carry

- R10-COP-GATE part D (its roster brief, group R10-COP-GATE-D, carry 7; finding-propagation.md):
  - The accessor is `DrawRange.learned_max_kw(now_s)`, taking epoch seconds.
  - `DrawRange.ceiling_since()` is the newest sample's epoch.
  - `CEILING_MIN_SAMPLES` and `CEILING_LAPSE_DAYS` are module constants in `draw_range.py`.
  - The probe's commanded power is `params.max_electrical_power`.

  Carry: R10-COP-GATE-D
- R10-COP-GATE-D carry 8: the gain between set-point and drawn power at levels between the duty gate and the ceiling is unmeasured. The probe measures only the draw at the ceiling, as its approved note scopes it. Carry: R10-COP-GATE-D

## Friction

none
