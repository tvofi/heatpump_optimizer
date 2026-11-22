Closes #3859

Builds the approved design `design/R11-OWNER-MODE-LEGS` 0e59437a (rev 2, verdict a45b5af9): minimum heating and hot-water mode legs as two options, default 10 min, 0..15, read by one rule in `duty_legs` for the planner and the arbiter, and an execution check in `duty_switch.served_leg`.

**Base and serial position.** Cut from `origin/main` 8ef450936a17. The design rebases this group onto R11-OWNER-FROST-HOLD and R11-OWNER-FAULT-HOLD; neither has a handoff ref (`git ls-remote origin 'refs/heads/handoff/r11-owner-f*'` lists only `r11-owner-flowcap`), so this head carries neither, and the design's "frost wins with a young DHW leg latched" pins are owed on whichever lands second (Forward-carry). **Overlap with #3849** (R11-OUTSIDE-3849): `git ls-remote origin refs/heads/handoff/r11-outside-3849` printed nothing at build time. The issue's fixes sit in `duty_legs`/`duty_switch`'s pricing (`planner_pairs`, `drop_unstartable`, `startable_steps`); this diff touches neither function, so nothing of that seam was built here or left to it; the shared files are `duty_switch.py` and `optimizer.py`.

## Head

81db193f15522b3dc7df087da32fac9e1cc11457, measured against merge base 8ef450936a1786abf4bb9610dc3336da4e77e8de (`origin/main`'s tip at 2026-11-22T16:28Z).

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

`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8ef450936a17 ./tests/run.sh` at 81db193f15 (a detached worktree of this head): `MODE: SCOPED -- 30 script(s) run, 3 scoped out`; summary line `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN` (the run_always scripts added), `ALL 6044 FEATURE CHECKS PASSED`, `ALL 122 STRESS CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`, rc 0.

## Architecture score

dS +0.0017 IMPROVES; no gate rise.

## Red checks

- `mutation` (predicted by `prepr.sh` step 6d over the 54 unpinned sites below): the repair is `mutation-autofix`'s, which pins each site once the pull request exists (`ci-autofix.md`); the diff's predicates are killed by hand in Mutation proof and its one equivalent mutant is triaged. Cheaper detector: `tools/pr/ci_predict.py` already predicts it locally (seconds per run, run at every prepr); the red is the pinning step's normal state for new production lines, not a defect, so no countermeasure is owed.

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
- custom_components/heatpump_optimizer/entry_config.py:81 BOOLOP -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/entry_config.py:81 CMP_BOUND*2 -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/entry_config.py:81 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/grid_fee.py:149 GUARD_OFF -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand
- custom_components/heatpump_optimizer/grid_fee.py:153 RETURN_DEL -- pinned by `mutation-autofix` (its lane mutates `custom_components/`); the "Mutation proof" list kills the predicates by hand

## Forward-carry

- R11-OWNER-FROST-HOLD and R11-OWNER-FAULT-HOLD are not built; their holds sit downstream of `_served` in the design, so they win over `_kept_leg` by construction. The pins "frost wins with a young DHW leg latched" and the same for the fault hold are owed by whichever of those groups lands after this one. Destination: `dev/programme/rosters/wave-r11-groups.json`, that group's `brief`, on `handoff/audit-r11-roster`; the write is the orchestrator's, as this seat pushes only its handoff refs. Carry: R11-OWNER-FROST-HOLD
- The same pin for the fault hold. Destination: `dev/programme/rosters/wave-r11-groups.json`, that group's `brief`, on `handoff/audit-r11-roster`; the write is the orchestrator's, as this seat pushes only its handoff refs. Carry: R11-OWNER-FAULT-HOLD
- Lease (design carry lease): `lease_expiries` reads 0 at both ends on both seeds; the synthetic plan's hot-water stretches never reach `LEASE_MINUTES`, so the count does not separate. Carry: dismissed: measured flat, the generator does not reach the lease; the soak on the owner's install is the reading that can.

## Friction

none
