R10-CEILING-PROBE: the cheap-night ceiling probe, and the system-identification experiment's step reaching a flow set-point install.

Issues #2498 and #2808. The roster lists neither under its `fixes`, so this body names them without a closing keyword; their close is the orchestrator's.

A set-point-driven install's plan rarely writes the flow ceiling, so the metered draw window is censored at the top and the plugin cannot learn the pump's real maximum (the owner's: configured 5 kW, believed near 3 kW). This adds a second experiment kind, the ceiling probe, inside the existing cheap-night system-identification gates. It commands the configured maximum, the arbiter writes the ceiling for it, and the metered draws of those intervals go to a separate store on `DrawRange`. The store's raw median is the learned top. It is published in the diagnostics, and R10-COP-GATE part D consumes it.

The design is the approved architect note `dev/programme/designs/R10-CEILING-PROBE.md` at `design/r10-ceiling-probe` 2212054e93c344d62762ac52e3b891bcce93d31d, as amended by its review `design-verdict/r10-ceiling-probe` 621e26313113ce925f7442cb935d0660a2505179 (carries 29-34 supersede the note where they differ), with items 7-28 of the note and of `design-verdict/R10-CEILING-PROBE` e8da829f15771f047ba63b392b15af4d0fe99224. The orchestrator's s9 ruling (roster carry 6) makes that shape final.

**What changes, by owner.**

- `sysid.py` owns when the experiment runs and what it commands.
  - `armable(...) -> (kind, why)` (module function) picks the kind. The fit runs while the house learner is unconverged and its own `min_days_between_runs` clock allows. Otherwise the probe runs where the install can run one and the probe's clock allows: 7 days unlearned, 30 once the store has a learned top. A refusal is published in `result.reason`. At main a converged house armed the fit, which then idled silently at "house already converged" (#2808).
  - The probe's clock is the store's newest sample, which persists in the accuracy store, or this process's last probe step (`probe_run`), whichever is newer. So a restart cannot reset it (item 7).
  - The converged denial in `conditions_met` applies to the fit only.
  - A flat price horizon refuses the probe: "a flat price has no cheap hour to probe in". The fit's price gate is unchanged.
  - `probe_step_hours(...)` (module function) is the duration search. At the configured maximum's heat, it tries whole cycles (`DEFAULT_OPTIMIZATION_INTERVAL`), longest first, up to `step_hours`, and returns the first whose predicted peak fits the comfort bound. The bound is `max_excursion_c`, less the two-zone headroom only: the probe fits nothing, so the fit's `SIZING_NOISE_HEADROOM_C` has no noise to absorb (item 14). Below `PROBE_MIN_CYCLES` (2) the arm aborts "no probe step of two cycles fits within the comfort bound". The found duration is stored in `_step_hours` and is what `step()` compares against (item 15).
  - A probe ends with its last step interval and hands back to the plan. It does not relax. It completes uncompleted, its outcome in `reason` ("ceiling probe ran 2.0 h at 5.00 kW"), so `_adopt_system_identification` adopts nothing.
  - `stand_down(reason)` replaces the coordinator's unconditional abort. An armed experiment that has not started is held, with the reason published as `held`. A started one still aborts (#2808).
  - The view gains `kind`, `held` and `last_attempt`.
- `pump_arbiter.py` owns how an action becomes a set-point.
  - `_experiment_kw(inp)` reads the experiment's commanded power from the action, before the plan's `power_schedule` is consulted (item 19).
  - `_planned_duty` returns `space` where `planned_draw_runs(power)` is true (the rule `heat_pump_on` books, item 32) and `idle` otherwise. At main it returned `None`, the baseline row.
  - `_flow_target` maps that power through `flow_setpoint_for_level`, so the configured maximum writes the ceiling and the fit's sized step its own level.
  - `_flow_command`'s install reads moved into `thermal_model.flow_setpoint_driven`, which the probe's eligibility shares (item 21).
- `draw_range.py` owns what a sample teaches.
  - `DrawRange.ceiling` is a deque of `(drawn_kw, epoch_s)`, 48 long.
  - `fold(..., experiment_s=)` routes an experiment interval that `takes_ceiling` (ceiling written, drawn above the idle draw) to the store and not to the window. Every other interval folds into the window as before.
  - `learned_max_kw(now_s)` is the store's median. It is `None` below `CEILING_MIN_SAMPLES` (12), more than `CEILING_LAPSE_DAYS` (45) after the newest sample, or with the newest sample ahead of the clock. It applies no agreement test (item 29). `diagnostics_view` publishes it beside `effective_max_kw`, outside the latch.
  - The overdraw drop (item 8): two ordinary intervals written at the ceiling that draw more than `AGREE_TOLERANCE` above the learned top drop the store. A new store sample restarts the count.
  - Persistence: the store and the count persist in the accuracy document. `from_dict` reads them before the window's configuration key, so a store-only record keeps them. `as_dict` omits the `config` key while nothing has keyed it.
- `coordinator.py` is wiring only.
  - `_pending_prediction` gains `"mode"` beside `split` and `flow_command`. The fold routes on it, so the routing reads the interval's own action and not the one adopted since (item 30, #2262's pairing). No second capture was built.
  - The arm is one call, `sysid.arm_from_config`, which passes `learner_samples` and the draw store where `ceiling_probe_install` holds.
  - `_run_system_identification` asks `sysid.hold_reason` (mode, learners' freeze, unread room, and now `quiet_windows.quiet_reason`) and calls `stand_down`.
- `quiet_windows.py`: `quiet_reason(config, now)` names a step inside a configured quiet off or silent window. The solve honours those windows (`off_steps`, the silent cap). The experiment's override replaces the solve's action, so at main the fit's step ran through a quiet off window on every switch install. The experiment now stands down inside one: held while armed, aborted once started. This was a sibling seam the enumeration found (Figures).
- `thermal_model.py`: `flow_setpoint_driven(config)` and `ceiling_probe_install(config)` sit beside `probe_install` (item 21).
- `sensor.py`: `ModelStatusSensor` publishes a recorded `system_identification_outcome` row (kind, phase, held, reason, last_attempt). The bulky `system_identification` view stays in `_unrecorded_attributes` (item 17). `tests/entities.py`'s attribute registry names the new key.
- `store.py` declares the two new cells (`draw/ceiling/#/0` and `#/1`, `draw/overdraws`). `accuracy.py` persists a store-only draw record. `diagnostics.py` passes the clock to `diagnostics_view`. `payload.py` types the three view keys.

**Departures from the note, raised here.**

- `button.py` is unchanged. Its availability at main is already `not system_identification_active`, which admits every armable kind, so the note's widening is a no-op. Making availability depend on `armable` would hide exactly the refusal #2808 asks to publish. The refusal is published through the recorded outcome row.
- The accessor takes the clock: `learned_max_kw(now_s)`. The lapse is a clock, and `draw_range` reads none, so a no-argument accessor would have to read the wall clock below the glue. Part D's note names the accessor `learned_max_kw()`. The semantics it states (raw median; `None` below twelve or past the lapse) are kept. Its "lapsed (+ newest sample date)" row reads `ceiling_since()`. Forward-carried to R10-COP-GATE below.
- `stand_down` holds an armed experiment for every reason the coordinator's gate names: the pump mode that cannot heat, the learners' freeze, and the unread room. The note says "holds one that has not started, republishing the `_learning_frozen` reason". A held arm injects nothing, so a cooling season holds it with its reason published rather than discarding the press. Three existing checks (`a cooling mode`, `a hot-water-only mode`, `a pump that is off the network`) asserted the abort of an armed experiment, and a fourth (`the aborted result carries the cause`) its reason. They now assert the hold and the abort of a started one, with the same "instead of commanding heat" power arm, and the cause carried by both.
- Files beyond the note's seven: `thermal_model.py`, `quiet_windows.py`, `store.py`, `accuracy.py` and `diagnostics.py`, plus `tests/entities.py` and the test stubs below. Each is one predicate, one declaration or one argument. The quiet-window stand-down is beyond the note. It also changes the fit, on any install with a quiet window configured and an experiment armed. It is a seam the step-8 enumeration returned and that this diff's actuation widens: an override that bypasses the solve's quiet windows now reaches a flow set-point install at the configured maximum. An install with no quiet window reads `None` and is unchanged. `dev/audit/harnesses/r10_setpoint_boost.py` and two `tests/features.py` stubs (`_sp_write`, `_bst_write`) gain `action=None`, because `_flow_target` now reads `inp.action` on its space path, which they did not carry. The harness's output is byte-identical at the head and the merge base (md5 `caf88df6801ec3380cbbeb4f37d33417` at both).
- `tests/golden/claimed_drift.txt` claims the five `coord_*` fixtures for this change, replacing main's inert R10-COP-GATE lines for the same five names. The fixtures gain the new keys: `kind`, `held` and `last_attempt` in both copies of the view, and the outcome row. Each was grafted from that fixture's own capture with `golden.capture_coordinator`, with no existing leaf touched and no float re-recorded (65 lines added, 0 removed). This is the same procedure R10-COP-GATE part 5 used (`d480c8cfc`).

**Roster carries, answered.**

- Carry 1 (#2465's three). (a) The set-point-to-draw gain: this diff measures it at the one level the probe commands, the ceiling, and stores that draw as the learned top. The intermediate levels stay uncalibrated: the approved note scopes the probe to the top, and nothing here identifies the gain between gate and ceiling. That part is not answered by this diff; it is on the roster as the R10-CEILING-PROBE Carry 1 residual, `groups[31].carry[26]` at `cec6621b4`. A level between gate and ceiling still maps to a set-point on the configured power band (`thermal_model.flow_setpoint_for_level`), not on a measured gain. #2465 sent the booked-vs-delivered gap to R10-DEMAND-OVERBOOK, which the roster now marks done, and the orchestrator landed the gain as the carry named above (R10-COP-GATE), so it is routed. (b) Reaching the real maximum: the probe is the ceiling probe, folded into the system-identification experiment, and the synthetic pump with a 3.0 kW maximum behind a configured 5.0 kW is recovered (Null control). (c) A gate-held draw above idle is a control beside its arm (Null control).
- Carry 2 (#2808). A converged house now arms the probe instead of an experiment that cannot run (`armable`). A learning freeze, the pump mode or an unread room holds an armed experiment that has not started, and aborts one that has (`stand_down`). The outcome is the recorded `system_identification_outcome` attribute (item 17).
- Carry 3 (the three blockers). (1) Actuation: `_experiment_kw` feeds `_planned_duty` and `_flow_target` (items 19, 32), and the harness's level arm writes the ceiling at 5.0 kW. (2) The probe-only run on converged houses, with its 7- and 30-day clocks (items 7, 16). (3) The top is learned from a ceiling store separate from the window, at twelve samples, with the 45-day lapse and the overdraw drop as its re-test (items 8, 12, 29). The fit's step samples now book commanded heat (item 10).
- Carry 4 (the approved r2 ruling): items 7 and 8, below.
- Carry 5 (R10-COP-GATE part D): the raw accessor, item 29 below; its interface goes forward under `## Forward-carry`.
- Carry 6 (the s9 ruling): items 29 to 34 bind as written, and each is answered below.

**Items 7-34, answered.**

- 7: the probe clock is the persisted store's newest sample. The restart check: a fresh `SystemIdentification` reading a stored record from three days ago refuses, and one from eight days ago arms.
- 8: the overdraw drop. Two ordinary ceiling draws 20 % over a 3.0 kW top drop the store, one does not, and 10 % over never does.
- 9: no in-flight claim, and no adoption refusal.
- 10: a `sysid` step sample books the heat COMMANDED for the interval beginning at its `when`, the override the same `step` call returns. The meter's reading of that interval reaches `draw_range.fold` a cycle later (`SysIdSample` docstring).
- 11: a probe interval is commanded at the configured maximum. `_fold_capacity_envelope`'s `nameplate` test then holds and folds a capacity observation. That is intended: the probe is the one interval a set-point install truly commands at the ceiling.
- 12: the store's run delimiter is each sample's timestamp. The top is the median of all samples, each sample counted once.
- 13: `boost.py`'s `block_release_reason` returns `RELEASE_SYSID` under an experiment action, so a probe at night releases a live space or hot-water block (`a measurement experiment and a stale plan release either block` pins it).
- 14, 15: the duration search and its stored duration, above. The checks cover the bound from both sides and a 1.0 h probe that steps two intervals.
- 16: twelve store samples are three 2.0 h probes (four step intervals each) or six 1.0 h probes (two each). The synthetic-pump check runs both.
- 17: tested (the outcome row is recorded; the view is not).
- 18: the synthetic pump with a known maximum, and the gate-held draw above idle, each beside its arm (Null control).
- 19: `_experiment_kw` is consulted before `_step_kw`.
- 20: an experiment interval is `space` only. On an arbiter-driven install a hot-water charge the plan booked in that interval is not served. `_commanded_split` still carries the plan's `dhw_power`, so `is_running_space` refuses that interval, and it reaches neither the store nor the window.
- 21: the predicate sits beside `probe_install`, shared with `_flow_command` and the arm.
- 22, 24, 34: the ratchet, per class and per row (Figures).
- 23, 30: the two ordering checks, through the production `_record_accuracy` twice.
- 25, 33: citations re-resolved at the fork (Figures).
- 26: F6/F7 are re-derived through `observe`, which runs `_disagrees`.
- 27: the store is not keyed to `config`. It meters the pump at the ceiling set-point, which the configured power range does not set, so a reconfiguration keeps it. The window's key is unchanged. A record whose configuration is unreadable drops the window and the latch and keeps the store.
- 28: the sibling sites are listed on their own evidence (Figures, Enumeration).
- 29: raw accessor. Twelve samples at 4.5 kW on a 5.0 kW configuration return 4.5; eleven return `None`.
- 31: the supply switch. The cycle books `heat_pump_on = planned_draw_runs(override)` (on at 5.0 kW). `step_supply` returns `None` under an experiment action, so the one-minute tick writes nothing over it between cycles. Null control: a plan step at 0 kW is a tick write of off.
- 32: `planned_draw_runs`, no literal.

**Alternatives.**

- Probe samples in the rolling window, `MIN_SAMPLES` lowered. Rejected: it moves the clamp for every install, and 48 ceiling samples first on an empty window latch it (reversal control).
- Routing on `_current_action` at the fold. Rejected: it reads the next interval's mode (the late-routing control).
- A second capture for the pair. Rejected: `_pending_prediction` already carries the interval's own split and command (#2262).
- The 15 % rule in the accessor. Rejected: part D owns it (item 29).
- A strict `price < cutoff` for the probe's flat-price refusal. Rejected: it refuses every two-rate tariff whose cheap plateau covers more than the cheapest 30 %. The refusal keys on a flat horizon (`np.ptp == 0`) instead.
- Paying the ratchet by moving a `SystemIdentification` method to module level verbatim. Not taken: that is a mechanical split. The payment finishes #1776's `HousePlant` record through the step path instead.

## Head

`db13e69720ad948930acbc8852ba280be5fb1eb3` repairs the three reds at `08c2477f20bc79d403cba509c0f0f06ae511edfb` (`## Red checks`). It merges origin/main twice with no conflict: `92588d581fde4ce287af3db5e8bb61461dc28015` (`961614a9e`), then `6421fe135d9f5a9e65433a4433f000d2419486bf` (`db13e6972`). Between them it adds `tests/features.py`'s re-keyed #1523 null-control marker (`b457c6d70`) and the four `--pin-killed` ledger entries for the re-cut's `sysid.py` sites (`99fd9e26b`). No production line changes. The figures under `## Figures` that open with this repair name the tree each was taken at; the figures beneath them from earlier heads describe those trees.

`08c2477f20bc79d403cba509c0f0f06ae511edfb` is the re-cut after the review at `e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87` (blocked: metric-gamed). Code delta over the reviewed head: the arm and the stand-down decision move out of the coordinator into `sysid.arm_from_config` and `sysid.hold_reason`; `tests/features.py` gains the median pin and the checks for the moved functions; `tests/structure_budgets.json` is re-recorded down (17642, 8049); `origin/main` `df66556f2b20efd0ebd0db321cbcfafd01530dbf` is merged with no conflict. The claim-file union of `94d0669db` is unchanged (main touched no golden file in between).

`08c2477f20bc79d403cba509c0f0f06ae511edfb` is the orchestrator's recarry of main into the previous head. It is not a clean merge of the live head and main (parent 1 570d22c0 is not the live pull-request head e310b8bb), so prepr checked this head.

`570d22c0d4cfa0f3cbdf0f7ce1ff353705718476` is the orchestrator's recarry of main into the previous head. It is not a clean merge of the live head and main (HEAD has 1 parent(s), not a 2-parent merge), so prepr checked this head.

`eee3fa59ca51362ec73ae21bb27bc2ee4cd25d45` is the orchestrator's recarry of main into the previous head. It is not a clean merge of the live head and main (parent 1 434d3bf2 is not the live pull-request head e310b8bb), so prepr checked this head.

`e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87` merges origin/main `2b6bef7453a8bdaf97d42f382a116ce226b35ccc` into `94d0669db00b38d4b723b485bb997e549e02697f`, whose hand resolution of the one conflict (merging main `a7dd7f50d` into `fba24c23916626aa8255218412246410759acf09`) is in `tests/golden/claimed_drift.txt` (the `claimnotes` driver refused: both sides rewrote the claim list for the same five fixtures). Resolution delta: main's whole file, `config_flow` verbatim, and one line each for `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal` and `coord_two_zone` naming both causes (main's `model_status` cop rows and this branch's `system_identification` `kind`, `held`, `last_attempt` plus the `system_identification_outcome` row); `claims-for: 7.1.0` unchanged. Proof: `env_drift.py --all 2b6bef7453a8` prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, with all five claims moved (7 leaves each); both parents' claim lines are present in the merged file; `git merge-tree --write-tree origin/main HEAD` is clean. No code file was resolved by hand; the figures below were taken at `632bd15b9` and the merge brings in main's newer commits only.

`e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87` is the orchestrator's recarry of main into the previous head. It is not a clean merge of the live head and main (parent 1 94d0669d is not the live pull-request head fba24c23), so prepr checked this head.

`e568f720d644256deae755d69e26734b34771609` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/3050.md`. The authored code head is `632bd15b9be154b9eb1c9b51540a77880505dcce`.

`c3d503d122f959297e86689713e36cd049047cca` merges origin/main `c3a47e565` into the authored code head `632bd15b9be154b9eb1c9b51540a77880505dcce` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`632bd15b9be154b9eb1c9b51540a77880505dcce`. It merges origin/main `14ed135512e3d7db899081f2c2639ce5674b8f2a` (the merge base now) into the branch, whose fork point was `0d33c9348b39ab289a64e26ac9c9f42c17adab7f`:

- `055d5d57b64d8b92176624aba2566eebee87147e`: the change, its checks, the harness, the ledger edits, and the five `coord_*` fixture grafts with their claims.
- `8a1c094e5206b5d7ac6299f767cc4ed319512139`: `tests/structure.py --record` at the fork point (`class_excess_loc` 17656 -> 17652, `max_class_loc` 8061 -> 8058). The commit message names the rows.
- `632bd15b9be154b9eb1c9b51540a77880505dcce`: the merge. `git merge-tree` reported one conflict, in `_record_accuracy`'s draw fold. Main's R10-COP-GATE part 6 (#3038) gates that fold on a dwell that saw no hot water and rewrote its comment; this branch adds the `experiment_s` argument to the fold call. The resolution keeps main's comment and condition and adds this branch's argument. The ledger driver merged `tests/structure_budgets.json` to 17651 and 8057, both deltas applied (`recorded_at` stays `0d33c9348`), and merged `tests/closures.json`'s INERT set.

Every figure below was measured at `632bd15b9`, against the merge base `14ed13551`, unless it names another tree. Steps 2 to 8 were re-executed after the merge.

## Mutation proof

The block in `tests/features.py` starts at the comment `# --- R10-CEILING-PROBE (#2498, #2808)` and holds 57 checks. Each mutant below changes one production line and runs the block alone through `tools/audit/seat/features_block.py` (the header's namespace, then the block). The driver lives out of tree (fixer step 18) and restores the file after each mutant. The baseline block run is `ALL 57 FEATURES BLOCK PASSED`.

The design's mutation targets, as amended (the routing key replaces the capture site; no sub-ceiling filter), each run at this head (`632bd15b9`):

- M1, the duty threshold: `planned_draw_runs(experiment)` -> `experiment > 0.0`. 1 failed: `the experiment's duty is space exactly where its booked heat_pump_on is True`.
- M2, the duty branch deleted (the base shape; the plan's step decides): 2 failed, the relax-is-idle check and the duty-threshold check.
- M3, the level source: `_step_kw(inp.plan, now)` only. 2 failed: the probe at the ceiling (`('space', 38, 'Heating')`) and the fit's own level.
- M4, the kind selection (always the fit): 1 failed, the kind check.
- M5, the fit clock (`days >= 0.0`): 1 failed, the kind check.
- M6, the probe clock unlearned (`PROBE_DAYS_UNLEARNED = 0.0`): 2 failed, the clocks check and item 7's restart check.
- M7, the probe clock learned (the unlearned wait used): 1 failed, the clocks check.
- M8, the converged skip (the fit's guard for both kinds): 11 failed. The probe never starts, so the run, the four gate checks, the comfort abort, item 15, the freeze, the synthetic pump and its control, and the no-fit abort all fail.
- M9, the hold/abort branch (always abort): 3 failed, the experiment-level freeze, the coordinator-level freeze and the quiet-window checks.
- M10, the routing key read at the fold (`self._current_action.get("mode")`): 1 failed, item 30's two orderings.
- M11 and M12, the routing predicate without the ceiling test, and without the idle test: 3 and 2 failed (the gate-held check and the store's edges; for M11, the late-routing control too).
- M13, the twelve (`CEILING_MIN_SAMPLES = 11`): 2 failed, both item 29 checks.
- M14, the lapse dropped: 1 failed, the lapse check.
- M15, an agreement test added to the accessor (`None` when the median is within 15 % of 5.0 kW, the shape item 29 forbids): 1 failed, `twelve at 4.5 kW on a 5.0 kW configuration publish 4.5 ...`.
- M16 and M17, the overdraw drop deleted, and its count at 1: 3 and 2 failed (item 8's check, the count-restart check, and for M16 the edge check).
- M18, the searched duration unused (`elapsed >= cfg.step_hours`): 1 failed, item 15.
- M19, the probe's bound taking the noise headroom: 6 failed, including the duration search and the synthetic pump.
- M20, the flat-price refusal deleted: 2 failed, the flat-price gate check and the flat-price null.
- M21, the pending `mode` key not captured: the block raises `KeyError: 'mode'` in item 30's pairing check, which reads the capture.
- M22, a store-only draw not persisted (`accuracy.py`): 1 failed, the persistence check.
- M23, the outcome row nulled (`sensor.py`): 1 failed, the outcome check.
- M24, a probe that relaxes instead of handing back to the plan: 3 failed, including the four-interval run.
- M25, a store-only record losing its store in `from_dict`: 4 failed.
- M26, the quiet window not read by the stand-down gate: 1 failed, the coordinator's quiet-window check.
- M27, `quiet_reason` never naming a window: 2 failed, its own check and the coordinator's.

Failing test first: at the merge base the block cannot import `ceiling_probe_install` (`ImportError`). Its arbiter checks run alone at the base with that import dropped: 4 of 6 fail, each reading the defect: `(None, 35, 'Heating + DHW')` for the probe, the fit and the relax, and `None` duty on every edge of the threshold. The two controls pass at both ends.

The mutation inventory itself: every `mutation_table.candidates` site on the diff's changed production lines, each through the same block in a worktree copy of the head (the driver is out of tree). At this head there are 75 sites. The block kills 72. Of the other three:

- `pump_arbiter.py:620 GUARD_OFF` (`_flow_command`'s guard) and `sysid.py:1448 GUARD_OFF` (the fit's plant branch) are killed by the whole `tests/features.py` at this head: 1 of 4717 and 39 of 4717 checks fail.
- `sysid.py:probe_step_hours RETURN_DEL` (the closing `return None`) is equivalent, and is triaged.

An earlier run of the inventory, on the tree before the edge checks, left 25 sites. Each was answered by a value check at its exact edge or on the arm it names, all in the block: the clocks at exactly 30 and 7 days, the 200-sample boundary, the lapse at exactly 45 days, the store's ceiling and idle edges, the 48-sample window, the stored-row floor, a plan action's own power, the empty outcome row, a probe armed on a declared plant, a house no probe fits, a draw exactly at the overdraw factor, a peak exactly at the bound, the degenerate-house fallback, and the probe's COP floor. Making `_begin_step_phase` return `None` removed its two `RETURN_DEL` sites.

Added at the re-cut after the review at `e310b8bb3` (block now 60 checks, each mutant run alone through `tools/audit/seat/features_block.py`; baseline `ALL 60 FEATURES BLOCK PASSED`):

- M27, the accessor's median (the reviewer's M5): `np.median` -> `np.mean` in `DrawRange._ceiling_median` -> 1 failed: `item 29: the accessor is the median of the store, not its mean or its extreme` (eleven at 3.0 kW plus one at 1.0 or 9.0 kW must read 3.0). Before the check it survived the block and `tests/features.py`.
- M28, `sysid.hold_reason`'s mode branch removed (`if False:`) -> 1 failed: `hold_reason ranks a mode that cannot heat first, then the learners' freeze, then an unread room, then a quiet window`.
- M29, `hold_reason`'s quiet-window term dropped -> 2 failed: that check and `inside a quiet off window the coordinator holds an armed probe with the reason and aborts a started one`.
- M30, `sysid.arm_from_config`'s switch ignored (`ident.config.enabled = True`) -> 1 failed: `arm_from_config takes the switch from the entry's configuration`.

## Null control

- **Flat price.** A flat 48-step horizon never starts a probe. The fit's `conditions_met` on the same flat horizon reads `(True, "ready")`, unchanged from the base. A probe on a priced horizon (`np.linspace(0.5, 2.0, 48)`) at 0.5 starts; at 1.9, above its 30th percentile, it does not.
- **The comfort and price gates hold.** No probe starts outside the night window, outside the outdoor band, on an expensive hour, or on a flat price. The comfort abort stops one mid-step.
- **Duty-cycling installs unchanged.** `ceiling_probe_install` is false without Control duty, without the flow unit, or without a meter. A converged switch install's press is refused with the reason, and no probe arms (the button's route through `async_arm_system_identification`). The arbiter's change is inside `_planned_duty` and `_flow_target`, which only a Control install's command reaches. The supply switch's path (`heat_pump_on = planned_draw_runs(override)`, `_write_supply`, `step_supply`) is untouched, and its existing check (`the step tick writes nothing at a boundary under a system_identification action`) passes. No golden fixture moved (`GOLDEN_MODE=drift`, Figures).
- **Quiet windows.** Inside a quiet off window the coordinator holds an armed probe ("inside a quiet off window") and aborts a started one. A window elsewhere in the day holds nothing. With no window set, `quiet_reason` reads `None`.
- **A plan action is not the experiment's.** A plan step of 5.0 kW with an action reading 0 kW writes `('space', 55.0)`, from the plan.
- **A synthetic pump with a known maximum.** A 3.0 kW electrical maximum behind a configured 5.0 kW is recovered within 2 % through the production experiment, the coordinator's pairing and the production fold: three 2.0 h probes (12 samples) and six 1.0 h probes (12 samples). Control: routed on the mode one interval late, the 1.0 h probes store 6 samples, the top stays `None`, and a 3 kW probe draw reaches the window.
- **A gate-held draw above idle.** At a learned 1.1 kW idle, 1.4 kW with the gate written is a running sample by `is_running_space` and stores nothing. The same 1.4 kW with the ceiling written stores.
- **The latch, reversed.** 48 ceiling draws through `observe` on an empty window latch `planned` to `(3.0, 3.0)`. The same 48 through the experiment's fold leave `engaged` False and `observed()` `None`, with the window empty and the top 3.0 beside it.
- **The finder's harnesses read flat where the fix rightly leaves things alone.** `ceiling_probe.py`'s `draw` arm drives `DrawRange.observe` directly, and prints `((1.5, None), False, None)` and `((1.5, 3.0), False, None)` at both ends: the window is unchanged. Its `duty` arm's code-object line reads `True` at both. Its companions read the defect at the base and not at the head (Figures).

## Figures

At `99fd9e26b9415c91b358eb4d37861b8a7ba7457e`, merge base `92588d581fde4ce287af3db5e8bb61461dc28015`, unless a line names `db13e6972`. `db13e6972` then merges origin/main `6421fe135d9f5a9e65433a4433f000d2419486bf` (no conflict; it brings `dev/programme/delivery/3075.md`, `tools/audit/seat/plan_page.py`, `tools/audit/seat/state_docs.py` and `tools/plan/replan.py`, none of them in `tests/closures.json`'s recorded closure for `tests/features.py`, so the features and pin figures stand):

- `PYTHONPATH=tests/hastub python3 tests/features.py` -> `ALL 4735 FEATURE CHECKS PASSED`; the row `#1523 class check null control: dropping the experiment's consult re-opens exactly its seam` is `ok`. Null control: at `08c2477f2`, with the old marker, the same row fails with `[[]]` (job 124789209502).
- `python3 tests/mutation_table.py --pin-killed --base origin/main` -> `PIN KILLED: 4 pinned, 0 left unpinned`; null control `sysid.py:66 NULL_COMMENT` survived every driver in play.
- `python3 tests/structure.py` at `db13e6972` -> `STRUCTURE RATCHET PASSED` (no budget file changed in this repair).
- `python3 tests/closure.py select --diff 92588d581` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- `tools/pr/prepr.sh <body>` at `db13e6972` against `6421fe135`: every step `ok` or `skip` but one `check` line, `claim files ... tests/golden/claimed_drift.txt changed` (the branch's own earlier claims, untouched here); `CI PREDICT: no closures, fast, governance or instrument red predicted against 6421fe135d9f`. The first run, at `99fd9e26b`, refused `carry` (both `## Forward-carry` items named R10-COP-GATE, now done); the markers now name R10-COP-GATE-D, where the 2026-11-01 routing pass moved both, and `carry_audit.py check` prints `2 routed, 0 unrouted, 0 bad destination(s)`.

- Gate scope: `D=$(mktemp -d); PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=14ed135512e3d7db899081f2c2639ce5674b8f2a PYTHONPATH=tests/hastub bash tests/run.sh` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, `4 TEST SCRIPT(S) FAILED`. The four are `tests/entities.py`, `tests/optimality.py` (1 of 84), `tests/card.mjs` and `tests/stress.py` (2 of 113). Each fails the same way at the merge base on this macOS seat (Red checks). Among the rest:
  - `ALL 4717 FEATURE CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `ALL 108 FINITE BOUNDARY CHECKS PASSED`, `ALL 61 GUARD PIN CHECKS PASSED`.
  - `tests/env_drift.py --all`: `CLAIMED` on the five `coord_*` fixtures (7 leaves each), `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 14ed135512e3d7db899081f2c2639ce5674b8f2a`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
  - `tests/entities.py` ran through its attribute pins before it stopped: `ModelStatusSensor publishes exactly its pinned attribute keys (#373)` and `the pinned attribute surface is the whole measured one (#373)` passed.
- Structure, per class and row: `python3 tests/structure.py` (its class table; `class_excess` in `tests/structure.py`), at the merge base `14ed13551` and here:
  - `SystemIdentification` is 1065 LOC at the merge base and 1064 here: class_excess_loc -1. The closing `return True` of `_begin_step_phase` goes, because its bool lost its one reader when the settling branch's double return folded.
  - `HeatPumpOptimizerCoordinator` is 8059 at the merge base `2b6bef7453a8` (its recorded budget) and 8049 here: class_excess_loc -10 and max_class_loc -10. The earlier claim of -3 is withdrawn: it came from joining the arm's lines and putting the quiet-window read on an existing line, which the review at `e310b8bb3` removed as a null control (re-wrapped in the base layout the coordinator was +5 over its budget). Laid out normally the coordinator read 17661 and 8068 (+12 over the recorded 17649 and 8056). The payment is a move of logic, not of lines: the arm's configuration reads and log are `sysid.arm_from_config`, and the stand-down decision is `sysid.hold_reason`, each a module-level function in `sysid.py` that the coordinator calls in one statement. They are module functions, not `SystemIdentification` methods, because that class is over the 300-line limit: as methods the same move read `class_excess_loc` 17662, the excess moving and not falling.
  - `DrawRange` stays under `GOD_CLASS_LOC_LIMIT` (300), so it costs nothing.
  - `class_excess_loc` is 17653 at the merge base `2b6bef7453a8` and 17642 here; `max_class_loc` is 8059 and 8049. `tests/structure_budgets.json` is re-recorded down to 17642 and 8049 (no row rises, no budget is raised). Architecture score, `tools/audit/archscore/score.py --diff 2b6bef7453a8` (three-dot against the merge base): `dS +0.0006 IMPROVES` (`coord_footprint` 2389 -> 2388); the layout of the review's block (`30c7ac3e0`, lines laid out normally, logic still in the coordinator) read `dS +0.0000 NULL`, and the move against that commit reads `dS +0.0006 IMPROVES`.
  - `coordinator_attrs` 142, unchanged (a dict key, no attribute). `functions_cc_over_15` 27, unchanged: `_record_accuracy` was already over the limit. Every other row is unchanged.
  - `STRUCTURE RATCHET PASSED` here and at the merge base. At the fork point, before the record, `055d5d57b` read `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`.
  - No budget rises.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 14ed135512e3d7db899081f2c2639ce5674b8f2a` -> `Architecture score: dS +0.0000 NULL`. An intermediate tree read `WORSENS (inadmissible: literal_clone_copies 123->125)`: the store's new row repeated `Domain("real", math.nextafter(RUNNING_FLOOR_KW, math.inf))`. Hoisting it into the one `_RUNNING_KW` both rows read made it NULL.
- Typing: `.venv-typing/bin/python tests/typing_ruler.py --mypy` (the `typing` job's pinned toolchain, mypy 2.3.1, homeassistant-stubs 2026.9.3) -> `ALL 9 typing-ruler checks PASSED` (`errors did not grow`, `type_ignores did not grow`).
- CI predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `72 unpinned site(s) the diff adds` and `no closures, fast, governance or instrument red predicted against 14ed135512e3`. Its first run predicted three reds: the new harness's INERT READS entry (written by `--apply-inert`) and two stale pins (deleted). A later run predicted a third stale pin, a triage on a `return False` that is now a bare return (deleted).
- The finder's harnesses, ported as `dev/audit/harnesses/ceiling_probe.py` (blob `d1101c541b57a318beb87fc02ca193227d316d59`, sha1 of the file `4c2f42122ea7cf3f3df04aa46eeb4e19b218ac34`) from `probe_duty.py` (sha1 0d3fbd4541c8a1b7aa0a4ed6304ba55c1828dff5) and `probe_draw.py` (sha1 f4a4344c30aadf764929ec473d1ada2b11eb1e5f). Run with `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/ceiling_probe.py`:
  - duty: the base reads `sysid step 5.0 kW -> duty None`; this head reads `-> duty 'space'`. The null arm (a plan action) reads `'idle'` at both.
  - draw: `one probe : ((1.5, None), False, None)` and `null 48 ceil: ((1.5, 3.0), False, None)` at both. It drives `observe` directly, which this change leaves alone.
  - level (companion): the base writes 35 for an experiment at 5.0, 1.5 and 0.0 kW. This head writes 55, 38 and 25.
  - store (companion): the base prints `absent`. This head prints `probe samples 12 | learned top 3.0 | window samples at the ceiling 0 | engaged False`.
- Failing test first: the block at the merge base -> `ImportError: cannot import name 'ceiling_probe_install'`. Its six arbiter checks alone at the base: `4 of 6 CP CHECKS FAILED`; at this head: `ALL 6 CP CHECKS PASSED`.
- Block: `python3 tools/audit/seat/features_block.py "# --- R10-CEILING-PROBE (#2498, #2808)"` -> `ALL 57 FEATURES BLOCK PASSED`.
- Enumeration, the rule (step 8): every reader that turns the experiment's action or kind into a command, a sample or a published state. `git grep -n '"system_identification"' -- custom_components/heatpump_optimizer/` returns 17 lines here (15 at the merge base). The plan-power readers an override bypasses: `git grep -n '_step_kw(\|step_duty(\|plan_step_runs(' -- custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/early_cutoff.py` returns 6. The note's own sibling command, `git grep -n '_sysid_step_off_loop\|learner_samples=' -- custom_components/heatpump_optimizer/`, returns 4, the entry points. Every seam:
  - Closed in this diff:
    - `pump_arbiter.py:497` `_experiment_kw`: duty and level.
    - `pump_arbiter.py:661` `_flow_target`'s level.
    - `pump_arbiter.py:796` `_planned_duty`'s plan step, now reached only by a non-experiment action.
    - `coordinator.py:9756`, the fold's routing.
    - `sensor.py:2045`, the outcome row.
    - `coordinator.py:7713`, the view's publication (fields added).
  - Already guarded:
    - `pump_arbiter.py:1208` and `:1213`, `step_supply`: the tick writes nothing under an experiment. Item 31, tested.
    - `boost.py:647`, `RELEASE_SYSID`: item 13, pinned by `a measurement experiment and a stale plan release either block`.
    - `early_cutoff.py:225`, `_exempt`'s `step_duty`: the cut-off may still cut an experiment's step on a warm room. That is its comfort guard. A cut interval's spot reading is either the running draw or the idle draw, and the idle draw is dropped by `takes_ceiling`'s idle rule, so the store's value is not biased. At the base the same holds for the fit on a switch install.
  - Unchanged by design: `coordinator.py:10876` (the override's writer); `payload.py:115` (the probe is a kind inside `REASON_SYSTEM_IDENTIFICATION`); `const.py:1554` and the card's `ACTION_HEATING_MODES` (`www/heatpump-optimizer-card.js:2345`), whose state lists gain no name; `button.py:146`, `icons.json:134`, `strings.json:1868` and the two translations at `:1868`, the entity key and names.
  - Definitions, not readers: `pump_arbiter.py:335` (`step_duty`) and `:482` (`_step_kw`).
  - Entry points: `coordinator.py:1844`, `:10823`, `:10852`, `:10858`.
  - Closed in this diff, a seam the rule found outside the note: the plan's quiet windows, which the solve honours (`quiet_windows.compose_with_silent`'s `off_steps` and silent cap) and the override bypasses. The stand-down decision, `sysid.hold_reason`, reads `quiet_reason`.
- Citations (items 25, 33), re-resolved at this head: `coordinator.py` `_record_accuracy` 9727, the fold 9756, the `mode` key 9852, `async_arm_system_identification` 10819, `_run_system_identification` 10828, `stand_down` 10848, `_adopt_system_identification` 10884; `pump_arbiter.py` `_experiment_kw` 487, `_flow_command` 607, `_flow_target` 636, `_planned_duty` 773, `step_supply` 1197; `sysid.py` `armable` 1292, `probe_step_hours` 1328, `stand_down` 1489, `conditions_met` 1499, `_begin_step_phase` 1615, `_end_step` 1779; `draw_range.py` `learned_max_kw` 161, `takes_ceiling` 181, `fold` 515, `diagnostics_view` 586; `thermal_model.py` `flow_setpoint_driven` 1355, `ceiling_probe_install` 1372; `quiet_windows.py` `quiet_reason` 155; `sensor.py` `_unrecorded_attributes` 1994, `_sysid_outcome` 2050.
- Stale-roster check (preamble item 10c): this body cites no carry as landed.

## Unpinned sites

Each line is one site `tools/pr/ci_predict.py --base origin/main` lists as ADDED UNPINNED at this head (72), with the check that killed its mutant here (`N of 57` counts the block's failed checks). One more site (`sysid.py:probe_step_hours RETURN_DEL da9e8e97`) is equivalent and triaged under `tests/mutation_ledger/survivor_triage/`, so it is not listed.

- `custom_components/heatpump_optimizer/draw_range.py:94 CONST`: pinned by mutation-autofix; killed here by `the store keeps the newest 48 samples (CEILING_WINDOW)...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:97 CONST`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (7 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:100 CONST`: pinned by mutation-autofix; killed here by `the top lapses 45 days after the newest sample, and a sample stamped ahead of the clo...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:104 CONST`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (2 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:155 RETURN_DEL`: pinned by mutation-autofix; killed here: the block raises `TypeError: '>' not supported between instances of 'float' and 'NoneTyp`
- `custom_components/heatpump_optimizer/draw_range.py:159 RETURN_DEL`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (7 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:172 CMP_BOUND`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (5 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:172 GUARD_OFF`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (2 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:174 CMP_BOUND*2`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (4 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:174 GUARD_OFF`: pinned by mutation-autofix; killed here by `the top lapses 45 days after the newest sample, and a sample stamped ahead of the clo...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:176 RETURN_DEL`: pinned by mutation-autofix; killed here by `item 29: the accessor is raw -- eleven samples give None, twelve their median...` (6 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:187 CMP_BOUND`: pinned by mutation-autofix; killed here by `the store's edges: a set-point exactly CEILING_TOLERANCE_K under the ceiling is the c...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:188 CMP_BOUND`: pinned by mutation-autofix; killed here by `the store's edges: a set-point exactly CEILING_TOLERANCE_K under the ceiling is the c...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:198 BOOLOP`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:198 CMP_BOUND`: pinned by mutation-autofix; killed here by `an overdraw counts at a set-point exactly CEILING_TOLERANCE_K under the ceiling...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:199 CMP_BOUND`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (2 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:199 GUARD_OFF`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:201 CMP_BOUND`: pinned by mutation-autofix; killed here by `a draw exactly AGREE_TOLERANCE over the learned top is no overdraw...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:201 GUARD_OFF`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (3 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:203 CMP_BOUND`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (2 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:203 GUARD_OFF`: pinned by mutation-autofix; killed here by `item 8: two ordinary ceiling-written draws 20 % over the learned top drop the store;...` (2 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:436 CMP_BOUND`: pinned by mutation-autofix; killed here by `a stored row at the standby floor is dropped, one above it kept; a negative count rea...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:436 GUARD_OFF`: pinned by mutation-autofix; killed here by `the store and its overdraw count persist through the accuracy store, a store-only rec...` (4 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:438 RETURN_DEL`: pinned by mutation-autofix; killed here: the block raises `TypeError: 'NoneType' object is not iterable`
- `custom_components/heatpump_optimizer/draw_range.py:444 CLAMP_DROP`: pinned by mutation-autofix; killed here by `a stored row at the standby floor is dropped, one above it kept; a negative count rea...` (1 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:444 RETURN_DEL`: pinned by mutation-autofix; killed here by `the store and its overdraw count persist through the accuracy store, a store-only rec...` (3 of 57)
- `custom_components/heatpump_optimizer/draw_range.py:551 BOOLOP`: pinned by mutation-autofix; killed here: the block raises `TypeError: float() argument must be a string or a real number, not 'No`
- `custom_components/heatpump_optimizer/draw_range.py:551 GUARD_OFF`: pinned by mutation-autofix; killed here by `an experiment's ceiling interval writes the store, not the window; the same interval...` (6 of 57)
- `custom_components/heatpump_optimizer/pump_arbiter.py:497 GUARD_OFF`: pinned by mutation-autofix; killed here by `a plan action's power is not the experiment's: the plan's own step (5.0 kW) decides d...` (1 of 57)
- `custom_components/heatpump_optimizer/pump_arbiter.py:499 RETURN_DEL`: pinned by mutation-autofix; killed here by `the probe's step (the configured 5.0 kW maximum) is heating at the flow ceiling  [('s...` (4 of 57)
- `custom_components/heatpump_optimizer/pump_arbiter.py:620 GUARD_OFF`: pinned by mutation-autofix; killed here by the whole `tests/features.py`: 1 of 4717 checks failed (`null control: Observe, an indoor set-point, or a plan that writes the compressor frequency ... records no command`)
- `custom_components/heatpump_optimizer/pump_arbiter.py:789 GUARD_OFF`: pinned by mutation-autofix; killed here by `the experiment's zero step (the fit's relax) is idle: the gate is written  [('space',...` (2 of 57)
- `custom_components/heatpump_optimizer/quiet_windows.py:167 RETURN_DEL`: pinned by mutation-autofix; killed here by `a step inside a quiet off or silent window is named; outside one, or with none set, i...` (2 of 57)
- `custom_components/heatpump_optimizer/sensor.py:2058 GUARD_OFF`: pinned by mutation-autofix; killed here by `no experiment view, no outcome row...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:100 CONST`: pinned by mutation-autofix; killed here by `each kind its own clock: the probe waits 7 days unlearned and 30 once learned, from t...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:101 CONST`: pinned by mutation-autofix; killed here by `each kind its own clock: the probe waits 7 days unlearned and 30 once learned, from t...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:103 CONST`: pinned by mutation-autofix; killed here by `the probe's duration search: 2.0 h on the leaky house, 1.0 h on the tight one against...` (5 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1308 CMP_BOUND`: pinned by mutation-autofix; killed here by `the fit's clock is inclusive: exactly 30 days after its last run arms it; 200 learner...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1308 GUARD_OFF`: pinned by mutation-autofix; killed here by `the kind: the fit while unconverged (150, 199), the probe once converged where the in...` (4 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1310 CMP_BOUND`: pinned by mutation-autofix; killed here by `the fit's clock is inclusive: exactly 30 days after its last run arms it; 200 learner...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1310 GUARD_OFF`: pinned by mutation-autofix; killed here: the block raises `TypeError: unsupported format string passed to NoneType.__format__`
- `custom_components/heatpump_optimizer/sysid.py:1315 GUARD_OFF`: pinned by mutation-autofix; killed here: the block raises `AttributeError: 'NoneType' object has no attribute 'learned_max_kw'`
- `custom_components/heatpump_optimizer/sysid.py:1319 BOOLOP`: pinned by mutation-autofix; killed here: the block raises `AttributeError: 'NoneType' object has no attribute 'timestamp'`
- `custom_components/heatpump_optimizer/sysid.py:1322 BOOLOP`: pinned by mutation-autofix; killed here: the block raises `TypeError: unsupported operand type(s) for -: 'float' and 'NoneType'`
- `custom_components/heatpump_optimizer/sysid.py:1322 CMP_BOUND`: pinned by mutation-autofix; killed here by `the probe's clock is inclusive: exactly 7 days after the newest store sample arms it...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1322 GUARD_OFF`: pinned by mutation-autofix; killed here by `each kind its own clock: the probe waits 7 days unlearned and 30 once learned, from t...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1324 RETURN_DEL`: pinned by mutation-autofix; killed here by `each kind its own clock: the probe waits 7 days unlearned and 30 once learned, from t...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1325 RETURN_DEL`: pinned by mutation-autofix; killed here by `the kind: the fit while unconverged (150, 199), the probe once converged where the in...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1353 CMP_BOUND`: pinned by mutation-autofix; killed here by `the duration search's bound is inclusive: a peak exactly at the bound keeps the 2.0 h...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1353 GUARD_OFF`: pinned by mutation-autofix; killed here by `the probe's duration search: 2.0 h on the leaky house, 1.0 h on the tight one against...` (9 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1437 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house with no meter or no flow set-point is refused at the press, and the...` (4 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1446 BOOLOP`: pinned by mutation-autofix; killed here: the block raises `AttributeError: 'NoneType' object has no attribute 'two_zone_enabled'`
- `custom_components/heatpump_optimizer/sysid.py:1446 GUARD_OFF`: pinned by mutation-autofix; killed here by `a probe armed on a declared plant seeds no fit: no slab pair, no re-seeded gains prio...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1448 GUARD_OFF`: pinned by mutation-autofix; killed here by the whole `tests/features.py`: 39 of 4717 checks failed (first: `the production sequence (declared plant) never enters identify()`)
- `custom_components/heatpump_optimizer/sysid.py:1492 GUARD_OFF`: pinned by mutation-autofix; killed here by `a freeze holds an armed experiment and publishes why; once started, it aborts  [('abo...` (3 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1511 BOOLOP`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (13 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1511 CMP_BOUND`: pinned by mutation-autofix; killed here by `a fit armed unconverged stands down at the start once the learner reaches 200 samples...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1511 GUARD_OFF`: pinned by mutation-autofix; killed here by `a fit armed unconverged stands down at the start once the learner reaches 200 samples...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1526 CMP_BOUND`: pinned by mutation-autofix; killed here by `the comfort and price gates hold the probe: none starts on a flat price  [[None, None...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1625 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (6 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1628 CLAMP_DROP`: pinned by mutation-autofix; killed here by `the probe prices its heat at the fit's COP floor (0.1): at a reported COP of 0.05 the...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1630 GUARD_OFF`: pinned by mutation-autofix; killed here: the block raises `TypeError: '>=' not supported between instances of 'float' and 'NoneTy`
- `custom_components/heatpump_optimizer/sysid.py:1639 CMP_BOUND`: pinned by mutation-autofix; killed here by `the fit's degenerate-house fallback is strict: a loss or a mass of exactly 1e-6 is no...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1640 CMP_BOUND`: pinned by mutation-autofix; killed here by `the fit's degenerate-house fallback is strict: a loss or a mass of exactly 1e-6 is no...` (1 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1758 CMP_BOUND`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1758 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (5 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1768 CMP_BOUND`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1768 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (2 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1781 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (3 of 57)
- `custom_components/heatpump_optimizer/sysid.py:1788 GUARD_OFF`: pinned by mutation-autofix; killed here by `a converged house arms a probe: it settles an hour on the plan, steps the configured...` (2 of 57)
- `custom_components/heatpump_optimizer/thermal_model.py:1375 BOOLOP`: pinned by mutation-autofix; killed here by `eligibility is install-level and shared with the arbiter's flow-command rule: a meter...` (1 of 57)
- `custom_components/heatpump_optimizer/thermal_model.py:1375 RETURN_DEL`: pinned by mutation-autofix; killed here by `eligibility is install-level and shared with the arbiter's flow-command rule: a meter...` (4 of 57)

The re-cut after the review at `e310b8bb3` adds four sites in `sysid.py` (the moved arm and stand-down decision), each run alone through the block (61 checks):

- `custom_components/heatpump_optimizer/sysid.py:1385 GUARD_OFF` (`hold_reason`'s `if signals.space_blocked:` -> `if True:`): killed here by `hold_reason ranks a mode that cannot heat first...`, `the coordinator's freeze holds the armed probe with its reason, and aborts a started one` and `inside a quiet off window the coordinator holds an armed probe...` (3 of 60 at the time).
- `custom_components/heatpump_optimizer/sysid.py:1387 RETURN_DEL` (the freeze/room/quiet chain not returned): killed here by the same three checks (3 of 60).
- `custom_components/heatpump_optimizer/sysid.py:2468 GUARD_OFF` (`arm_from_config`'s `if armed:` -> `if True:`): it survived at 60 checks (it only mislogs a refusal as an arming). Pinned by `arm_from_config logs the armed kind once when it arms, and says nothing of arming when it does not`, which then fails: 1 of 61.
- `custom_components/heatpump_optimizer/sysid.py:2473 RETURN_DEL` (`return armed` -> `return None`): killed here by `arm_from_config takes the switch from the entry's configuration` (1 of 60).

All four are now recorded under `tests/mutation_ledger/killed_by/sysid.py/` by `--pin-killed` (`killed by tests/features.py`, commit `99fd9e26b`), so the ratchet reads them as pinned.


## Red checks

Concluded red at `08c2477f20bc79d403cba509c0f0f06ae511edfb`, each this diff's (main's own runs of `tests / fast` and `tests / mutation` at the same base are green):

- `tests / fast (3.14)` (job 124789209502): `tests/features.py` failed one row, `#1523 class check null control: dropping the experiment's consult re-opens exactly its seam  [[]]`. Cause: the re-cut moved the stand-down decision into `sysid.hold_reason`, so the coordinator's consult became `hold_reason`'s `frozen` argument and lost its `else`; the null control's marker (`_P5_CONSULT`) was still the old conditional text, matched nothing, and the unmutated copy re-opened no seam. Answer: the marker is now the moved consult, `self._pump_signals, self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY),`, and the mutant passes `None` in its place; the check still requires the marker to occur exactly once and the mutant to open exactly `{_run_system_identification}`. `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4735 FEATURE CHECKS PASSED` with that row `ok`; at `08c2477f2` the same row printed `[[]]` (the CI job above is the control). Cheaper detector: it exists. `tests/closure.py select` puts `tests/features.py` in this diff's `scope.run` (`MODE: SCOPED -- 27 script(s) run`), and a whole run of it on the seat before the re-cut's handoff would have shown the row; the re-cut ran the R10 block alone through `features_block.py`, which does not reach the P5 class check. Its standing cost is one whole `tests/features.py` run per handoff, which fixer step 5 already owes; no new detector is built.
- `tests / mutation` (job 124789115340): `MUTATION TABLE REFUSED -- 3549 unpinned site(s) against 3558 at the ratchet base 92588d581, 4 of them added by this diff`: `sysid.py` `hold_reason` 1385 `GUARD_OFF` and 1387 `RETURN_DEL`, `arm_from_config` 2468 `GUARD_OFF` and 2473 `RETURN_DEL`. Cause: the re-cut added the two moved functions and the bot pin did not run (next item). Answer: `python3 tests/mutation_table.py --pin-killed --base origin/main` prints `PIN KILLED: 4 pinned, 0 left unpinned`, each `killed by tests/features.py`, and its null control (`sysid.py:66 NULL_COMMENT`) survived every driver in play; the four `killed_by/sysid.py/{hold_reason,arm_from_config}.*.json` entries are committed. Cheaper detector: `prepr.sh` step 6d lists the ADDED UNPINNED sites offline before the handoff; it is the standing check, run here.
- `tests / mutation-autofix` (job 124800000369): `skip-measure-failed`, the repair did not happen. Cause: it follows from the `tests / mutation` red above; the measuring run it repairs from failed, so it pinned nothing. Answer: the pins it would have written are committed by hand (previous item). Cheaper detector: the same `prepr.sh` step 6d listing; no other exists, the job is the autofix itself.
- `pr-contract / pr-contract` (job 124800971736) and `gate`: `check `tests / fast (3.14)` is red and `## Red checks` does not name it` and the same for `tests / mutation-autofix`. Cause: this section did not name the three reds above. Answer: it names them now. Cheaper detector: `prepr.sh --body-check` runs the same contract offline, run here before the push.

Earlier reds, as recorded at the previous heads:

`pr-contract / pr-contract` at fba24c239166 (job 124657591709) and `gate`, which depends on it: `PR-BODY: 1 error(s)`, `check `tests / mutation` is red and `## Red checks` does not name it`. Cause: the red-history walk reads every failure across the 6 commits between origin/main and the head, and found `tests / mutation` (red before the bot's `ci: pin killed mutants`, fba24c239166); this section named it as `mutation`, not by its full check name. Answer: the section now names the full name below; the red was this body's wording, not code. The cheaper detector exists: `body_patch.sh` runs the same contract offline.

Predicted on the pull request: `tests / mutation`, red by construction on the 72 sites under `## Unpinned sites` until `mutation-autofix` pins them. No other red is predicted: `ci_predict.py` -> `no closures, fast, governance or instrument red predicted`.

`gate` at `e310b8bb3` (jobs 124733639993 and 124734678917): the deferral reds the review named, `run(s) [41262300367] at this head are still being judged; their gate decides`. Cause: two `gate` runs started while the deciding suite's run was in flight, and each defers to it; the deciding suite's `gate` (job 124737196827) printed `PASS`. Not this change's, and the re-cut head is a new head with its own runs; no cheaper detector is owed, the deferral is the gate harness's own.

Seat-local reds in the scoped gate, each with its control at the fork point `0d33c9348` on the same seat (no CI check is answered here, and none of these is this change's):

- `tests/entities.py` stops in the heartbeat lane (`_hb_stdlib_reads`, line 18440 here, 18418 before the merge) with `PermissionError: Cannot get task port for PID ...`: macOS refuses the lane's stack sampler a task port without root. At the fork point it stops in the same call with the same error. Its first gate run here also met `OSError: [Errno 28] No space left on device`, because the seat's disk filled; the line above is its re-run after space was freed, and that re-run passes every check before the lane, including the attribute pins. The checks after that line are CI's (Linux).
- `tests/optimality.py`: `FAIL one|summer_negative|shoulder: a recorded claim still has a gap (not stale) [claimed but gap 0.0000% is at or below the bar -- the claim closed and should be removed]`, `1 of 84`. The same check and count at the fork point.
- `tests/card.mjs`: `FATAL ERROR: ... JavaScript heap out of memory`. The same at the fork point (after `tests/plan_view.py`).
- `tests/stress.py`: `FAIL shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`, and in the gate run also `FAIL no scenario exceeds its own recorded cost by the budget factor [summer/1z/space/valve at 4.8x its reference vs its own budget 4.6x ...]`, `2 of 113`. The shoulder check fails with the same two values at the fork point. The budget-factor check is CPU time on a loaded seat: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/stress.py`, run alternately here and at the merge base `14ed13551` twice each, gives `ok   no scenario exceeds its own recorded cost by the budget factor` and `1 of 113 STRESS CHECKS FAILED` (the shoulder check, same values) in every run at both trees.

No cheaper detector is owed: none of the four is a check this branch turned red.

## Forward-carry

- R10-COP-GATE part D (its roster brief, now group R10-COP-GATE-D, which the s9 carry-routing pass of 2026-11-01 gave this item as its carry 7; finding-propagation.md): the accessor is `DrawRange.learned_max_kw(now_s)`, epoch seconds, because the lapse is a clock and `draw_range` reads none. `DrawRange.ceiling_since()` is the newest sample's epoch, which D's "lapsed (+ newest sample date)" row reads. `CEILING_MIN_SAMPLES` and `CEILING_LAPSE_DAYS` are module constants in `draw_range.py`. The probe's commanded power is `params.max_electrical_power` at `_run_system_identification`, the hub's configured figure, which D's invariant 1 keeps configured. Carry: R10-COP-GATE-D
- R10-COP-GATE (landed, roster `groups[31].carry[26]` at `cec6621b4`, "Unanswered residual of R10-CEILING-PROBE Carry 1"; R10-COP-GATE is now done, and the s9 carry-routing pass of 2026-11-01 moved this item to R10-COP-GATE-D as its carry 8): the gain between set-point and drawn power at levels between the duty gate and the ceiling is unmeasured; the probe measures only the draw at the ceiling, as its approved note scopes it. Carry: R10-COP-GATE-D

## Friction

none






