Closes #3859

Builds the approved design `design/R11-OWNER-MODE-LEGS` 0e59437a (rev 2, verdict a45b5af9): minimum heating and hot-water mode legs as two options, default 10 min, 0..15, read by one rule in `duty_legs` for the planner and the arbiter, and an execution check in `duty_switch.served_leg`.

**Base and serial position.** Cut from `origin/main` 8ef450936a17. The design rebases this group onto R11-OWNER-FROST-HOLD and R11-OWNER-FAULT-HOLD; neither has a handoff ref (`git ls-remote origin 'refs/heads/handoff/r11-owner-f*'` lists only `r11-owner-flowcap`), so this head carries neither, and the design's "frost wins with a young DHW leg latched" pins are owed on whichever lands second (Forward-carry). **Overlap with #3849** (R11-OUTSIDE-3849): `git ls-remote origin refs/heads/handoff/r11-outside-3849` printed nothing at build time. The issue's fixes sit in `duty_legs`/`duty_switch`'s pricing (`planner_pairs`, `drop_unstartable`, `startable_steps`); this diff touches neither function, so nothing of that seam was built here or left to it; the shared files are `duty_switch.py` and `optimizer.py`.

## Head

39b182d75fa1b01fa9f063612378a78c4bd342a0, measured against merge base b18edd593c94c9ef5d2d1bcfded4021dbd78fb31. 39b182d75f merges the pull request's head 1aa635d275 (`mutation-autofix`'s pins and its merge of main) into the repair at bc71899abf, tree-identical to this seat's own merge of the same pair. `origin/main`'s tip 0f63320c96cb at 2026-11-25T04:40Z; `git merge-tree --write-tree origin/main HEAD` rc 0, so no re-merge.

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
- `python3 tests/structure.py`: `module_excess_loc` 21779 -> 21772, re-recorded in b72e97c8a7 (the commit message names the payment).
- `python3 tools/audit/archscore/score.py --diff 8ef450936a17`: `Architecture score: dS +0.0017 IMPROVES` (`coord_footprint` 2525 -> 2522). The two rises an earlier cut read (`literal_clone_copies` 114 -> 119, `coord_footprint` +2) were paid by `pump_mode.SINGLE_DUTY`, `np.diff` in `_mode_runs` and `_fields`.
- Scope: `python3 tests/closure.py select --diff 8ef450936a17`: `MODE: SCOPED -- 30 script(s) run, 3 scoped out`.
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8ef450936a17 ./tests/run.sh` at 74f1c87240 red on six scripts; each is repaired by 1690cc83db and 81db193f15 and re-run at the head: `tests/features.py` (6044 checks; 2 red, both repaired: #2365's patched step width, and `_bootstrap`, which fails only outside `run.sh`'s interpreter path and passed in the gate), `tests/doc_claims.py` ALL 441, `tests/typing_ruler.py` ALL 12 with `HPO_TYPING_PYTHON`, `tests/env_drift.py --all` NO UNCLAIMED DRIFT over 56, `tests/finite_boundary.py` ALL 119, `dev/audit/rounds/round3/D5/option_doc_coverage.py` printing its new header values.
- `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted; 54 unpinned sites (below).

## Gate at head

`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=b18edd593c94 ./tests/run.sh` at 39b182d75f (this worktree): `MODE: SCOPED -- 30 script(s) run, 3 scoped out`; `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, `ALL 6134 FEATURE CHECKS PASSED`, `ALL 2761 ENTITY CHECKS PASSED`, `ALL 122 STRESS CHECKS PASSED`, rc 0. The run at 5cac9af1c1 before it was red on `tests/doc_claims.py` alone (T6c's comment over 40 words; re-cut in ff7aa67a47).

## Architecture score

dS +0.0017 IMPROVES; no gate rise.

## Red checks

- `tests / fast (3.14)` at 1aa635d275: `tests/entities.py`, the two checks of #3734's numeric-option census (Mutation proof). The census reached this branch in the merge of `origin/main` 3fd6a00125, after the gate run at 81db193f15. Cheaper detector: none; the cheapest run that sees a check main adds after the fork is `tests/entities.py` on the merged tree, which is this lane. Recorded, nothing built.
- `tests / mutation` (predicted by `prepr.sh` step 6d over the 54 unpinned sites below): the repair is `mutation-autofix`'s, which pins each site once the pull request exists (`ci-autofix.md`); the diff's predicates are killed by hand in Mutation proof and its one equivalent mutant is triaged. Cheaper detector: `tools/pr/ci_predict.py` already predicts it locally (seconds per run, run at every prepr); the red is the pinning step's normal state for new production lines, not a defect, so no countermeasure is owed.

## Unpinned sites

- custom_components/heatpump_optimizer/config_flow.py:4005 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:74 CLAMP_DROP*2 -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:74 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:95 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:112 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:113 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:117 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:121 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:128 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:146 CLAMP_DROP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:146 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:154 CLAMP_DROP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:154 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:155 CLAMP_DROP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:155 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:156 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:182 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:184 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:185 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:187 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:192 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:201 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:222 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:353 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:354 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:354 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:356 CLAMP_DROP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_legs.py:357 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:490 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:552 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:567 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:569 BOOLOP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:569 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:571 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:572 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:573 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:588 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:592 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:597 BOOLOP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:597 CMP_BOUND*4 -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:597 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:599 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:606 BOOLOP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:606 CMP_BOUND -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:606 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:607 CLAMP_DROP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:609 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:633 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/duty_switch.py:644 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/entry_config.py:112 BOOLOP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/entry_config.py:112 CMP_BOUND*2 -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/entry_config.py:112 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/grid_fee.py:149 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/grid_fee.py:153 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand

## Forward-carry

- Carry 0 (roster, from R11-OWNER-FAULT-HOLD item 346bf281, "the fault hold wins with a young leg latched"): not buildable at this head. `git grep -c "_fault_stands" origin/main -- custom_components` prints nothing at `origin/main` 0f63320c96cb, and nothing at this head; the hold is on `handoff/r11-owner-fault-hold` 8d8b30aa only. Its pin, a fault hold standing while a hot-water leg younger than its minimum is latched by `duty_switch._kept_leg` writes the fault mode and not hot water, is owed by whichever of this group and R11-OWNER-FAULT-HOLD merges second. Destination: R11-OWNER-FAULT-HOLD's `carry` in `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r11-roster`, written by the relay, as this seat pushes only its handoff refs. Carry: R11-OWNER-FAULT-HOLD
- Carry 1 (roster, from R11-OWNER-FROST-HOLD item 8bcbefe1, "frost wins with a young DHW leg latched"): not buildable at this head. `git grep -c "frost_holding" origin/main -- custom_components` prints nothing at `origin/main` 0f63320c96cb, and nothing at this head; the hold is on `handoff/r11-owner-frost-hold` 3071796b only. Its pin, a frost hold standing while a young latched hot-water leg is held by `duty_switch._kept_leg` writes the frost mode, is owed by whichever of the two merges second. Destination: R11-OWNER-FROST-HOLD's `carry` in the same roster file and branch, written by the relay. Carry: R11-OWNER-FROST-HOLD
- Lease (design carry lease): `lease_expiries` reads 0 at both ends on both seeds; the synthetic plan's hot-water stretches never reach `LEASE_MINUTES`, so the count does not separate. Carry: dismissed: measured flat, the generator does not reach the lease; the soak on the owner's install is the reading that can.

## Friction

none
