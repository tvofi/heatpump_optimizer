Closes #3859

Builds the approved design `design/R11-OWNER-MODE-LEGS` 0e59437a (rev 2, verdict a45b5af9): minimum heating and hot-water mode legs as two options, default 10 min, 0..15, read by one rule in `duty_legs` for the planner and the arbiter, and an execution check in `duty_switch.served_leg`.

**Base and serial position.** Cut from `origin/main` 8ef450936a17. The design rebases this group onto R11-OWNER-FROST-HOLD and R11-OWNER-FAULT-HOLD; neither has a handoff ref (`git ls-remote origin 'refs/heads/handoff/r11-owner-f*'` lists only `r11-owner-flowcap`), so this head carries neither, and the design's "frost wins with a young DHW leg latched" pins are owed on whichever lands second (Forward-carry). **Overlap with #3849** (R11-OUTSIDE-3849): `git ls-remote origin refs/heads/handoff/r11-outside-3849` printed nothing at build time. The issue's fixes sit in `duty_legs`/`duty_switch`'s pricing (`planner_pairs`, `drop_unstartable`, `startable_steps`); this diff touches neither function, so nothing of that seam was built here or left to it; the shared files are `duty_switch.py` and `optimizer.py`.

## Head

`4c04cfc81d18217f0b8ceed7267d4092c8575781` is this PR's head (2026-11-26T11:31Z, `origin/main` 1d3077736d): the round-4 repair of fix review `verdict/3869` 18a5d67f7f (blocked ci-red, 9 added sites surviving `tests / mutation`), three commits on the PR's head 39771d9c33 (the bot's pins), then a merge of the PR's moved head 7b71a4dbe4 (`ci: merge main`) with no hand resolution. `git merge-tree --write-tree origin/main HEAD` exits 0. `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.

- 49d3e2692a: four checks in the R11-OWNER-MODE-LEGS block of `tests/features.py`.
- 5b7ae2ff89: `duty_switch._kept_leg` drops `need > 0 and` from its hold test. The kept minutes are never negative, so the guard could not change a result. Its CMP_BOUND twin (`need >= 0`) was an equivalent mutant under the line's one anchor, which blocked that anchor from a pin, and the guard hid `_kept_minutes`'s `max(at, 0.0)` from every check. Without the guard, that floor is what keeps a minimum of 0 from holding a leg, and a fifth check pins it. The two pins on the old line text (BOOLOP and GUARD_OFF d7e66a4a) are removed: the BOOLOP site no longer exists, and the GUARD_OFF site has a new anchor.
- 1190b420e7: five `survivor_triage` entries for the duty_legs survivors no input can tell apart (Unpinned sites).

`4ab51be4391657b622ad008c6fb4629846bf39c4` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`6e1c645f65f7633af41d4a751a9103742725480b` re-keys 9 `## Unpinned sites` line(s) that the main merge and the round-3 repair moved from `392fe0b7eb`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/duty_legs.py:150 CLAMP_DROP -> custom_components/heatpump_optimizer/duty_legs.py:160 CLAMP_DROP; custom_components/heatpump_optimizer/duty_legs.py:158 CLAMP_DROP -> custom_components/heatpump_optimizer/duty_legs.py:168 CLAMP_DROP; custom_components/heatpump_optimizer/duty_legs.py:159 CMP_BOUND -> custom_components/heatpump_optimizer/duty_legs.py:169 CMP_BOUND; custom_components/heatpump_optimizer/duty_legs.py:186 CMP_BOUND -> custom_components/heatpump_optimizer/duty_legs.py:196 CMP_BOUND; custom_components/heatpump_optimizer/duty_legs.py:191 GUARD_OFF -> custom_components/heatpump_optimizer/duty_legs.py:201 GUARD_OFF; custom_components/heatpump_optimizer/duty_legs.py:360 CLAMP_DROP -> custom_components/heatpump_optimizer/duty_legs.py:370 CLAMP_DROP; custom_components/heatpump_optimizer/duty_switch.py:617 GUARD_OFF -> custom_components/heatpump_optimizer/duty_switch.py:616 GUARD_OFF; custom_components/heatpump_optimizer/duty_switch.py:622 CMP_BOUND -> custom_components/heatpump_optimizer/duty_switch.py:621 CMP_BOUND; custom_components/heatpump_optimizer/duty_switch.py:632 CLAMP_DROP -> custom_components/heatpump_optimizer/duty_switch.py:631 CLAMP_DROP.

`bf6c487691d3e60169162b5d2258e91a60e82ae8` is this PR's head: a merge of `origin/main` 70f410e996 into 6e1c645f65, which is three commits on 392fe0b7, a merge of `origin/main` d9100de781 and the round-3 repair of fix review `verdict/3869` 37ab2d58 (blocked metric-gamed), measured against merge base d9100de781 (`origin/main`'s tip at 2026-11-26T00:40Z).

**Second main merge** (bf6c487691). No hand resolution: git's ort merge with the ledger drivers resolved `tests/structure_budgets.json` (`module_excess_loc` 21763 + both deltas = 21754) and `tests/closures.json`. Without it, the predictor refused 6e1c645f65 (`governance / wave-script AGREEMENT UNMERGED`: HEAD did not merge into main dbdc520e86 without the drivers). At bf6c487691: `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/deployment_shape.py`'s counts are main's, and its closures measure 184 of the 561 pairs, as main records; `ci_predict.py` predicts no closures, fast, governance or instrument red against bdcfee6dcc96, and its 11 unpinned sites are those listed below, at the same lines. The gate below ran at 6e1c645f65; the merge adds no line to this PR's diff.

**Main merge** (c51360d13b, resolution delta 392fe0b7..c51360d13b). One hand resolution, `tests/golden/claimed_drift.txt`. The `claimnotes` driver refused it because both sides added claims. Both are kept: this branch's `config_flow` claim and paragraph, and main's eight R11-SEAM-two-zone-slab claims and #3713 paragraph, under main's `claims-for: 10.1.4`, which equals `VERSION`. `tests/structure_budgets.json` and `tests/closures.json` were resolved by their ledger drivers.

**Round 3 repair** (08ade1c115, 6e1c645f65):

- Block 1 (metric-gamed). ec6be8dbdf's re-wrap of `optimizer._leg_rule`'s call is gone. `duty_legs.entry_rule(split, cfg, before)` is now the one reading of `cfg.mode_leg_heat_min_minutes`, `cfg.mode_leg_dhw_min_minutes` and the leg the pump is in as the plan starts. `duty_switch.leg_rule` (the arbiter) and `optimizer._leg_rule` (the planner) both call it; before, the planner passed the three values as three extra `leg_rule` parameters and the arbiter `_replace`d them itself. `leg_rule` takes main's three parameters again. The planner's call no longer lists the two minimums, which is where `optimizer.py`'s line goes: `module_excess_loc` 21756 -> 21755, re-recorded in 6e1c645f65.
- Block 2 (surviving mutant on `leg_rule`'s neighbour). A check drives `optimizer._leg_rule` with `duty_leg_before` DHW and SPACE through `duty_legs.plan_legs` (Mutation proof).

`392fe0b7eb427ab84c9d4971256defe611b9a839` was the previous head: its code was already in it and main merged cleanly, so the orchestrator's script set that body without a push.

54a8c81c15f0fcc99066f82908c64f64b4f5abe5, measured against merge base d3d66c40408e76351ffc528686353cadf815a05c (`origin/main`'s tip at 2026-11-25T13:30Z).

**Pin repair** (delta 180da49d41..54a8c81c15). f244a4b7b5 merges the pull request's own head f4ec7bf618, `mutation-autofix`'s `ci: pin killed mutants` on 02fc3cde92 (31 ledger files, 5 byte-identical to the pins below), so the handoff is a fast-forward of the pull request's head and keeps its pins; the merge was clean. 54a8c81c15 drops that commit's `leg_rule` CMP_BOUND pin (2413dc3f), recorded on the pre-merge `return LegRule(...)` line the merge of `origin/main` replaced: `prepr.sh` predicted it a `STALE PIN` red. `ci_predict` named added unpinned sites at 180da49d41 for `tests / mutation`. `tests/mutation_table.py --pin-killed --base d3d66c40 --jobs 4 --budget-minutes 110` at 180da49d41 pinned the 6 it reached, all killed (5 ledger files under `tests/mutation_ledger/killed_by/duty_legs.py/`: `_mode_runs` CMP_BOUND, `_split` GUARD_OFF and RETURN_DEL, `leg_minimum` CLAMP_DROP and RETURN_DEL); 0 survived, and 38 were not started within the budget (`tests/features.py` takes 861 s per run on this container's 4 cores). Of those 38, the pull request's pins cover all but the 9 listed under Unpinned sites. The merge resolution is otherwise unchanged.

**Merge repair** (resolution delta 02fc3cde92e3..180da49d412b). `origin/main` d3d66c4040 did not merge into 02fc3cde92 without a resolution: three content conflicts and two mutation-ledger rename/rename pairs. Each was resolved as the union of both sides:

- `duty_legs.leg_rule` takes main's `unlatched` mask (issue 3849) third and this diff's `heat_min`, `dhw_min` and `before` after it, and returns the `LegRule` NamedTuple. Main's `both_step_legs` stays deleted, as this diff deleted it for `plan_legs`.
- `duty_switch._fields` reads main's `DutySwitchLearner.config_fields()` and adds this diff's minimum legs and `duty_leg_before`.
- `optimizer._leg_rule` passes main's latched stops and mask with this diff's minimum legs. `OptimizationConfig` carries both sides' fields.
- The ledger pairs were four different sites that git's rename detection had paired. `mutation_table.py --carry-rows` rebuilt the ledger from main's, byte-identical to keeping all four entries. 180da49d41 drops main's two pins, on `leg_rule`'s and `planner_fields`' old returns, which the merge replaced: `prepr.sh` predicted them as `STALE PIN` reds.
- Main's new `tests/features.py` checks compared a leg rule with 2-tuples, and one of them called the removed `both_step_duty`. They now compare with `LegRule(...)` and call `served_leg` (ec6be8dbdf).
- `_leg_rule`'s call lost one line, which paid the merged tree's `module_excess_loc` +1 (`tests/structure.py` rc 0). The fix review blocked that re-wrap as metric-gamed; round 3 replaces it with `duty_legs.entry_rule` (`## Head`).

**Round 2 repair** (block `mutation-vacuous` at 8ca95413, `probe/rev-3869-8ba22bbd` 7c308abb), two defects:

- `tests / fast (3.14)` red on `tests/entities.py`: #3734 (on main, merged in after this branch forked) added the numeric-option census, which refused `_leg_minutes`. 8630bbf58c: `_leg_minutes` reads a refused stored value as the key's default, as `_interval_minutes` and `_lead_minutes` do, so it joins `entry_config._DEFAULTED_NUMBERS` and the census's `_MIG_NUMERIC_PARSES`.
- Three survivors of the minimum-leg rule over the whole of `tests/features.py`: `duty_legs.py:184` R2's `left[..., s_slot] == DHW` and `right[..., s_slot] == DHW` each dropped, and `duty_legs.py:146` the forward fill's `before` replaced by `IDLE`. 5cac9af1 adds T6b and T6c, 186ccc5a8d T6d for two more R2 survivors `prepr.sh`'s diff mutants named, and bc71899abf T6e for `leg_minimum` and the batched rule (Mutation proof).

## Design departures

- `served_leg` replaces `both_step_duty` and also carries the `_share` plumbing the design names as the `pump_arbiter.py` payment (`served_leg` is the design's `duty_switch.served_leg`); the entry and leave checks are one function, `_kept_leg`, not `enter_ok` and `held_leg`.
- A both step's first run joined to the leg the pump is in (`LegRule.before`) is unbounded (`math.inf`): the design's R1 skips a hot-water leg "joined to a neighbouring DHW leg", and the pump's current leg has no known start.
- `_share` exempts an active block as well as a boost: holding hot water under a hot-water block would hand `_without_block` an idle step in place of space.
- `pump_mode.SINGLE_DUTY` is new: the mode-to-duty map was spelled in `pump_arbiter._report_write` and would have been spelled again in `duty_switch` (archscore `literal_clone_copies`).
- One record of mode legs (design carry leg-history-owner): `_Record.leg` stays apart from `ArbiterState.written["mode"]` and `dhw_since`. `written` is dropped by `hold()` and `_forget()` and re-stamped by a re-send; `dhw_since` follows the step duty, not the landed mode. `rec.leg` moves only when the landed mode does. R11-OWNER-STEP-KICK does not read it (the orchestrator's option (a)).
- Design carry legrule-tuple: `_legs` and `availability` read `LegRule(*rule)`, so a 2-tuple rule still reads.
- `planner_fields(coord, cfg)`: the coordinator passes `ctx._config` on its existing line (0 lines added); the body is `_fields(rec, cfg)`, which takes no coordinator (archscore `coord_footprint`).

## Mutation proof

**Round 4** (the 9 sites of verdict 18a5d67f7f). MUTANT_CMD is `features_block.py` over the R11-OWNER-MODE-LEGS block (`"# --- R11-OWNER-MODE-LEGS (#3859): minimum heating"` to `"# --- R10-CEILING-PROBE (#2498"`, with the prelude from `--emit-prelude`). It has 25 checks at the head, and its null run passes (`SURVIVED NULL`). The drive is `mutant_run.py --spec`, over the exact mutants `tests/mutation_table.py`'s `candidates()` generates at each line.

- At 49d3e2692a (12 mutants): killed are duty_legs.py:370 CLAMP_DROP, duty_switch.py:616 GUARD_OFF, and 621 CMP_BOUND `0.0 < age_min`, `age_min <= keep` and `_kept_minutes(...) <= need`. Surviving are 621 CMP_BOUND `need >= 0` (equivalent, which the anchor cannot carry next to three killed twins), duty_switch.py:631 CLAMP_DROP, and duty_legs.py 160, 168, 169, 196 and 201.
- At 5b7ae2ff89 (10 mutants of `_kept_leg` and `_kept_minutes`): all 10 are killed. These include 621's three CMP_BOUND mutants, its new GUARD_OFF, and 631 CLAMP_DROP, which the check `with a heating minimum of 0, heating is entered ... 5 min into it` kills.
- The killing checks are: `a 2-min hot-water leg ... passes idle and an unknown duty through` (616); `held from the instant it starts (age 0) and released when exactly its 10-min minimum old` (621 `<` and `<=` on the age); `a heating leg the plan keeps exactly the 10-min heating minimum is entered` (621 `<=` on the kept minutes); and `a step that loses 1/3 to the hot-water minimum and 0.8 to a stop leaves heating a share of 0, never negative` (370, where the mutant returns -0.133).
- `mutant_run.py --diff 1d3077736d...HEAD --max-mutants 40 --report-only --path duty_legs.py --path duty_switch.py` under the same MUTANT_CMD at the head: rc 0. It reports 15 SURVIVED, all in duty_legs.py, and only the block is narrow. 169, 196 and 201 are triaged below. The ratcheted 131 GUARD_OFF, 135 CMP_BOUND, 187 GUARD_OFF/CMP_BOUND and 188 RETURN_DEL already hold `killed_by` pins on the whole of `tests/features.py`, or the round-1 triage 4c27fbc3. The CONST_SWAP lines (59, 60, 98, 159, 164, 187, 192) are not a ratcheted operator.

Driver: a one-off script (scratch, not committed) that applies each mutant to its production line, runs `python3 tools/audit/seat/features_block.py` over the duty-switch block of `tests/features.py` (`"from heatpump_optimizer import duty_switch as _ds_mod"` to `"# --- R10-CEILING-PROBE (#2498"`, 86 checks with this diff's 15, its prelude from `--emit-prelude`), and restores the line. 18 of 19 killed at the head:

- R1 `short = two & (dhw_run < dhw_min)` -> never: T3, T5, T7 fail.
- R2 `space_run < heat_min` -> never: T4, T5, T6, T7 fail.
- R1 collapse dropped from `whole`: T3 fails.
- idle forward-fill removed (`codes = np.where(codes != IDLE, codes, before)`): T3, T7 fail.
- fixed-point loop `range(1)`: T5 fails.
- `run = inf` for a run joined to `before` deleted: T9 and the left-neighbour check fail.
- `availability` without `moved`: T8 fails. The `charged.any() or (moved > 0).any()` gate -> `charged.any()`: the block raises (T8's `None` reaches arithmetic).
- latch age `0.0 <= age_min < keep` -> False: T2, T10, the stamp-ahead check fail; `0.0 <=` dropped: the stamp-ahead check fails.
- `previous == MODE_DHW` guard dropped: T1b fails.
- entry check -> False: T1, T1b fail. `_kept_minutes`' idle continuation dropped: T1b's idle-next-step control fails.
- `rec.leg` update -> `pass`: T1, T1b, T2 and two more fail. `rec.solve_before = before` -> `pass`: the left-neighbour check fails.
- `_share`'s boost/block exemption removed: T2, T10 fail; the block alone removed: T10 fails.
- `EntryConfig` bound `0 <= minutes <= PLAN_STEP_MINUTES` -> True: T11 fails.
- Optimizer: `_stop_availability`'s `lost = 0.0 if stops is None else ...` restored to `if stops is None: return None`: "a solve with no stop priced reads the minimum legs' availability" fails (R10-DUTY-SWITCH-PLANNER-PRICE block, 79 checks).
- Survivor: `if not (heat_min > 0 or dhw_min > 0):` -> `if False:` (0 failing): equivalent, a fast path; triaged in `tests/mutation_ledger/survivor_triage/duty_legs.py/_with_minimums.{GUARD_OFF,CMP_BOUND}.4c27fbc3.json`.

Round 2, the same driver over the same block (88 checks with T6b and T6c) at 5cac9af1 (T6c's comment re-cut at ff7aa67a47, comment-only), the reviewer's mutant texts (`ev/mutant_driver.py` on 7c308abb):

- R2 `(left[..., s_slot] == DHW) & ` dropped: T6b fails (a space-first heating leg after an idle step merges).
- R2 ` & (right[..., s_slot] == DHW)` dropped: T6b fails (the plan's last heating leg merges).
- forward fill's `before` -> `IDLE`: T6c fails (the pump's hot-water leg, two idle steps, then a 6-min hot-water leg is lengthened to 10).
- bc71899abf adds T6e; each mutant applied alone at it fails the block: `duty_legs.py:74` `leg_minimum`'s `None` read as `1.0` and its clamp dropped (T6e fails; the review's clamp survivor is killed), and `duty_legs.py:151` the run sums' zero column shaped `codes.shape[:-2]` (the batched call raises `ValueError`).
- Still surviving, as the review read it: `duty_switch.py:592` `current == wanted` dropped (both later branches return `current`, which is `wanted`): equivalent on reachable inputs, on the Unpinned sites list for `mutation-autofix`.
- `prepr.sh`'s diff mutants (`MUTANT_CMD` the same block) at ff7aa67a47 named two more R2 survivors; 186ccc5a8d adds T6d, and each mutant applied alone at it fails T6d alone: `duty_legs.py:154` `s_idx > 0` -> `s_idx >= 0` (step 0's left side read as its own code, not the pump's leg) and `duty_legs.py:155` `idx[-1]` -> `idx[-2]` (the last step's heating leg reads nothing on its right).
- Baseline at bc71899abf: ALL 90 FEATURES BLOCK PASSED.
- `prepr.sh`'s diff mutants at bc71899abf, the survivors left after T6e, each equivalent on every input: `duty_legs.py:145` CONST_SWAP (`-1` -> `-2`: only `known >= 0` reads the fill); `duty_legs.py:150` CONST_SWAP (`idx[-1]` -> `idx[-2]` as the end fill: the last slot always ends a run, so the fill changes only a run that reaches it over two or more slots, whose last slot then holds a single step's 0 minutes, and its right side, which reads its own code, as `IDLE` does for R2); `duty_legs.py:155` CMP_BOUND (`<` -> `<=`: the last run's right side reads its own code, not `DHW`, for a heating run); `duty_legs.py:173` GUARD_OFF, CMP_BOUND, CONST_SWAP and `:174` RETURN_DEL (the both-zero fast path: the loop runs and changes nothing; triaged as above); `duty_legs.py:95` CMP_BOUND and `config_flow.py:4005` GUARD_OFF are on the Unpinned sites list.

The entities.py repair, `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree at 52b5be52f5 (this branch merged with main, before 8630bbf58c):

- baseline: `2 of 2761 ENTITY CHECKS FAILED`, rc 1: "every numeric option a release stores is declared in EntryConfig with a numeric parse" (`undeclared: ['mode_leg_dhw_min_minutes', 'mode_leg_heat_min_minutes']`) and "the migration repairs every member's non-number ..." (`open: {'mode_leg_dhw_min_minutes': ["'abc'", 'None' ...`).
- only the census half of 8630bbf58c applied (`_DEFAULTED_NUMBERS` unchanged): `1 of 2761`, the migration check fails.
- only the production half applied (`_MIG_NUMERIC_PARSES` unchanged): `1 of 2761`, the declared-parse check fails.
- both (the head): `tests/entities.py` passes in the gate (Gate at head).

Failing first: the same 15 checks as their own block (`"# --- R11-OWNER-MODE-LEGS (#3859)"` to `"# --- R10-CEILING-PROBE (#2498"`) with `custom_components/` stashed back to the merge base: T1, T1b and T2 FAIL, then `AttributeError: module 'heatpump_optimizer.duty_legs' has no attribute 'plan_legs'` at T3; at the head ALL 15 PASSED.

**Round 3** (at 08ade1c115, `features_block.py` from the check's comment "The solve's own rule carries it" to "The leg record:", preludes `duty_legs as _ds_legs`, `optimizer as _ml_om`, `SimpleNamespace`). Unmutated: `ALL 1 FEATURES BLOCK PASSED`. Each mutant applied alone, then restored:

- `optimizer._leg_rule`'s `opt.config.duty_leg_before` -> `duty_legs.IDLE`: `FAIL the solve's leg rule (optimizer._leg_rule) joins step 0's 6-min hot-water leg to a pump in hot water; null control, a pump in heating lengthens it to 10  [{2: 'dhw:10 space:5', 1: 'dhw:10 space:5'}]`.
- `duty_legs.entry_rule`'s `before=before` -> `before=IDLE`: the same check FAILs with the same values.
- At c51360d13b (the merged head, before the refactor), `_leg_rule`'s `opt.config.duty_leg_before` argument -> `duty_legs.IDLE`, the reviewer's R6: the same check FAILs with the same values. The check passes unmutated there too.

## Null control

- Options at 0 reproduce today: the existing duty-switch, `_PaCoord` and `_rp2` checks run with both options at 0 and pass unchanged in value; T1, T1b and T2 each carry an options-off arm that writes main's sequence.
- T7: 400 seeded 12-step plans, M and N from {5, 10, 12, 15}: 0 plans with a short leg; the same plans under both minimums 0 have short legs in a positive count, so the generator reaches the case.
- Harness null (`--heat 0 --dhw 0`) equals the merge base's counts on both seeds, and both kWh figures read 0.0 (Figures).

## Figures

- `dev/audit/harnesses/mode_legs.py` sha1 8a90a3c2ea919f3fc08a79911a26e9904021c43f, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/mode_legs.py --synthetic --seed S --heat H --dhw M`, 48 invented hours, a re-solve every 30 min at a seeded off-boundary second:
  - seed 3859, 10/10: h2d_per_hour 1.083, legs_under_10_resolve 0, legs_under_10_plan 0, legs_under_10_other 0, lease_expiries 0, space_priced_minus_delivered_kwh -3.943, tank_unpriced_kwh 7.409.
  - seed 3859, 0/0: 1.708, 34, 25, 0, 0, 0.0, 0.0.
  - seed 7, 10/10: 1.042, 0, 0, 0, 0, -1.375, 7.891. seed 7, 0/0: 1.417, 20, 23, 0, 0, 0.0, 0.0.
  - merge base (the same file, run with `custom_components/` stashed; it prints the counts only there): seed 3859 1.708, 34, 25, 0, 0; seed 7 1.417, 20, 23, 0, 0, equal to the 0/0 nulls.
  - space_priced_minus_delivered is negative: the execution checks keep heating the plan priced as hot water, after a re-solve. The design's bound is max(N, M) minutes of step 0 per re-solve; 95 re-solves at a level of at most 5.5 kW bound it at 87 kWh, so the second availability pass the design names was not added.
- Batch cost (design carry batch-cost, D9): `switch_weights_batch` on a [64, 192] batch, min of 5x20 calls, `timeit`: default rule 0.61-0.97 ms (two runs, this box is shared); N = M = 10: 3.9-6.3 ms, two fixed-point passes. Only a solve that prices a stop calls it (`_switch_cost_fn` returns `None` otherwise).
- `python3 tests/structure.py`: `module_excess_loc` 21779 -> 21772, re-recorded in b72e97c8a7 (the commit message names the payment). At 08ade1c115 it prints `gain module_excess_loc 21755 (budget 21756, -1)` with every other row `ok`; `--record` wrote 21755 in 6e1c645f65. Null control: the same script at c51360d13b, which still carries the re-wrap, prints `STRUCTURE RATCHET PASSED` at 21756, and the reviewer's revert of the re-wrap alone printed `FAIL module_excess_loc 21757 > 21756`.
- `python3 tools/audit/archscore/score.py --diff HEAD` at c51360d13b, run over 08ade1c115's tree: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/audit/archscore/score.py --diff 8ef450936a17`: `Architecture score: dS +0.0017 IMPROVES` (`coord_footprint` 2525 -> 2522). The two rises an earlier cut read (`literal_clone_copies` 114 -> 119, `coord_footprint` +2) were paid by `pump_mode.SINGLE_DUTY`, `np.diff` in `_mode_runs` and `_fields`.
- Scope: `python3 tests/closure.py select --diff 8ef450936a17`: `MODE: SCOPED -- 30 script(s) run, 3 scoped out`.
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8ef450936a17 ./tests/run.sh` at 74f1c87240 red on six scripts; each is repaired by 1690cc83db and 81db193f15 and re-run at the head: `tests/features.py` (6044 checks; 2 red, both repaired: #2365's patched step width, and `_bootstrap`, which fails only outside `run.sh`'s interpreter path and passed in the gate), `tests/doc_claims.py` ALL 441, `tests/typing_ruler.py` ALL 12 with `HPO_TYPING_PYTHON`, `tests/env_drift.py --all` NO UNCLAIMED DRIFT over 56, `tests/finite_boundary.py` ALL 119, `dev/audit/rounds/round3/D5/option_doc_coverage.py` printing its new header values.
- `python3 tools/pr/ci_predict.py` at bf6c487691: no closures, fast, governance or instrument red predicted against bdcfee6dcc96; 11 unpinned sites the diff adds, each with a line below.

## Gate at head

At 6e1c645f65: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=d9100de781 ./tests/run.sh` under the gate lease, `MODE: SCOPED -- 31 script(s) run, 3 scoped out`, rc 1 with four scripts red. Each red comes from this arm64 seat, not from the diff:
- `tests/optimality.py` `1 of 84`: `one|summer_negative|shoulder: a recorded claim still has a gap (not stale)` (gap 0.0000 %, obj 0.254795). The claim's own comment in `tests/optimality.py` records that the arm64 seat reaches the basin (obj 0.2548) while CI's linux lane measures +10.55 %, "so this claim reads stale on arm64 only".
- `tests/typing_ruler.py`: `mypy is pinned at 2.4.1 [found 2.3.1]`, the seat's venv, and the census under `HPO_TYPING_PYTHON` exiting 1 with it.
- `node tests/card.mjs`: `ENDED BEFORE ITS SUMMARY (exit 250)`, a V8 `OOMErrorHandler` abort on a host running two gates (it took 2272 s).
- `tests/entities.py` `1 of 2767`: `a measured script's late-writing descendant is waited for, not recorded as nodata`. The closure recorder's self-test timed out waiting for `entities` (the script took 5145 s on the loaded host).
CI is the authority for all four.

`PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` (code steps run) at 54a8c81c15: `MODE: SCOPED`, `PRE-PR: 54a8c81c15… rc=0`; `ci predict` names no closures, fast, governance or instrument red, `merged structure` reads `STRUCTURE RATCHET PASSED` against current `origin/main`, and step 7d reads every one of the 9 site lines disposed of. `tests/entities.py` at b736a6addc (54a8c81c15 adds only ledger files and a merge of them): `ALL 2763 ENTITY CHECKS PASSED`, rc 0. At 180da49d41, before the pins: `tests/features.py` `ALL 6190 FEATURE CHECKS PASSED`, rc 0, with this PR's mode-leg checks (T6b–T6e) among them.

## Architecture score

At bf6c487691, `python3 tools/audit/archscore/score.py --diff origin/main` (70f410e996): `dS +0.0006 IMPROVES` (`coord_footprint` 2526 -> 2525); no gate rise.

## Red checks

- `codeql / Analyze (python)` at f4ec7bf618 (run 45630904629): the runner received a shutdown signal at 14:58:53Z during CodeQL's file extraction (`tests/entities.py` alone took 714 s to extract) and produced no analysis; no alert was raised. It re-runs at this head. Cheaper detector: none, as a runner stopped by its host is not a property of the diff; recorded, nothing built.
- `tests / fast (3.14)` at 1aa635d275: `tests/entities.py`, the two checks of #3734's numeric-option census (Mutation proof). The census reached this branch in the merge of `origin/main` 3fd6a00125, after the gate run at 81db193f15. Cheaper detector: none; the cheapest run that sees a check main adds after the fork is `tests/entities.py` on the merged tree, which is this lane. Recorded, nothing built.
- `tests / mutation` at 4ab51be4 (job 139793015722): the table refused 14 unpinned sites, and `mutation-autofix` left 9 alive (verdict 18a5d67f7f). At 4c04cfc81d: 4 of the 9 have killing checks and 5 carry an `equivalent` triage. The 5 anchors prepr step 7d names (`5 site(s) the diff adds with no pin`) are those the round-4 drive killed, owed a pin by `mutation-autofix` once the head moves (`ci-autofix.md`): duty_legs.py:370 CLAMP_DROP, and duty_switch.py:616 GUARD_OFF, 621 GUARD_OFF, 621 CMP_BOUND*3 and 631 CLAMP_DROP. Cheaper detector: `mutant_run.py --spec` over the block, which this round ran. The earlier rounds left the sites unmeasured within `--pin-killed`'s budget and handed them to the bot. Owed: a fixer drives each site the diff adds over its own block before the handoff, which `fg3-fixer-mutants.txt` now asks.

## Unpinned sites

- custom_components/heatpump_optimizer/duty_legs.py:370 CLAMP_DROP -- killed at 49d3e2692a by `a step that loses 1/3 to the hot-water minimum and 0.8 to a stop leaves heating a share of 0`; pinned by `mutation-autofix`
- custom_components/heatpump_optimizer/duty_switch.py:616 GUARD_OFF -- killed at 49d3e2692a by `a 2-min hot-water leg ... passes idle and an unknown duty through`; pinned by `mutation-autofix`
- custom_components/heatpump_optimizer/duty_switch.py:621 GUARD_OFF -- killed at 5b7ae2ff89 (new anchor e54ba5a2 of the rewritten line) by the block (`mutant_run.py --spec`, KILLED); pinned by `mutation-autofix`
- custom_components/heatpump_optimizer/duty_switch.py:621 CMP_BOUND*3 -- each killed at 5b7ae2ff89 (age 0, age at the minimum, kept minutes at the minimum); pinned by `mutation-autofix`
- custom_components/heatpump_optimizer/duty_switch.py:631 CLAMP_DROP -- killed at 5b7ae2ff89 by `with a heating minimum of 0, heating is entered ... 5 min into it`; pinned by `mutation-autofix`
- custom_components/heatpump_optimizer/duty_legs.py:160 CLAMP_DROP -- survivor_triage equivalent `_mode_runs.CLAMP_DROP.5ba171ad`: a wrapped -1 read that np.where discards
- custom_components/heatpump_optimizer/duty_legs.py:168 CLAMP_DROP -- survivor_triage equivalent `_mode_runs.CLAMP_DROP.66bb4d09`: a wrapped -1 read that np.where discards
- custom_components/heatpump_optimizer/duty_legs.py:169 CMP_BOUND -- survivor_triage equivalent `_mode_runs.CMP_BOUND.a4744748`: the last run's right neighbour is read only by the sandwich test, on a SPACE slot
- custom_components/heatpump_optimizer/duty_legs.py:196 CMP_BOUND -- survivor_triage equivalent `_with_minimums.CMP_BOUND.a257ad19`: a run at its minimum is lengthened by 0
- custom_components/heatpump_optimizer/duty_legs.py:201 GUARD_OFF -- survivor_triage equivalent `_with_minimums.GUARD_OFF.463d143f`: the fixed-point break; passes after it change nothing

Null control for the triage: a differential probe (scratch, not committed) of `plan_legs` and `availability` at the head, original against each of the five mutants. Over 3000 seeded random plans (1-8 steps, both leg orders, extra None/0.5/2/5, minimums 0-45 min, before IDLE/SPACE/DHW, lost 0/0.1/0.5) it reads `differing per mutant {160: 0, 168: 0, 169: 0, 196: 0, 201: 0}`.

- custom_components/heatpump_optimizer/duty_legs.py:98 RETURN_DEL -- killed at 6e1c645f65; pinned by `mutation-autofix` in 39771d9c33
- custom_components/heatpump_optimizer/duty_switch.py:569 RETURN_DEL -- killed at 6e1c645f65; pinned by `mutation-autofix` in 39771d9c33

## Forward-carry

- Carry 0 (roster, from R11-OWNER-FAULT-HOLD item 346bf281, "the fault hold wins with a young leg latched"): not buildable at this head. `git grep -c "_fault_stands" origin/main -- custom_components` prints nothing at `origin/main` 0f63320c96cb, and nothing at this head; the hold is on `handoff/r11-owner-fault-hold` 8d8b30aa only. Its pin, a fault hold standing while a hot-water leg younger than its minimum is latched by `duty_switch._kept_leg` writes the fault mode and not hot water, is owed by whichever of this group and R11-OWNER-FAULT-HOLD merges second. Destination: R11-OWNER-FAULT-HOLD's `carry` in `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r11-roster`, written by the relay, as this seat pushes only its handoff refs. Carry: R11-OWNER-FAULT-HOLD
- Carry 1 (roster, from R11-OWNER-FROST-HOLD item 8bcbefe1, "frost wins with a young DHW leg latched"): not buildable at this head. `git grep -c "frost_holding" origin/main -- custom_components` prints nothing at `origin/main` 0f63320c96cb, and nothing at this head; the hold is on `handoff/r11-owner-frost-hold` 3071796b only. Its pin, a frost hold standing while a young latched hot-water leg is held by `duty_switch._kept_leg` writes the frost mode, is owed by whichever of the two merges second. Destination: R11-OWNER-FROST-HOLD's `carry` in the same roster file and branch, written by the relay. Carry: R11-OWNER-FROST-HOLD
- Lease (design carry lease): `lease_expiries` reads 0 at both ends on both seeds; the synthetic plan's hot-water stretches never reach `LEASE_MINUTES`, so the count does not separate. Carry: dismissed: measured flat, the generator does not reach the lease; the soak on the owner's install is the reading that can.

## Friction

none


