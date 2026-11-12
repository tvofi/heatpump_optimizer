Part A of the duty-switch restart learning, built from Bankaifan's pull request 3420 with thanks: the finding, the install's table and the first implementation are theirs, and their ten commits are this branch's first ten, authorship kept. On a Luxtronik install driven over the smart-home interface, a hot water to space mode write while the compressor runs stops it; nothing priced or observed that. This pull request observes each such switch, estimates per pump and per direction how often it ends in a stop and how long the pump then stays off, persists the estimate and publishes it on the compressor-starts sensor. **Nothing reads the estimate to change a plan or a write**: that is parts B and C of the design approved at `design/R10-DUTY-SWITCH-RESTART-LEARNING` abc575172ca1e6758c58ca8d1f265a2dc7c4fa23, which `docs/design/2026-11-10-duty-switch-restart-learning/design.md` now carries. No issue is closed: the finding arrived as pull request 3420, which the orchestrator closes with thanks after the merge.

## Re-cut

The seventh repair, answering the seventh review, past the three-round bound by owner ruling: outside request, drive to merge. This body replaces the earlier ones under `fixer.md`'s re-cut rule: round history is deleted, and every figure below was re-taken at the head named under Head, but where a line says it was not re-run. The round-7 review (`Fix review: blocked 112f0d777b8f8c921a75982d36305e94ffd2f7f4 mutation-vacuous: r7v_unsettled_with_pending_runs`, `verdict.md` on `probe/rev-3461-ba74baae`) is answered under "Review round 7, answered". Since 112f0d77 the branch adds two checks to the duty-switch section of `tests/features.py` and a `fresh` argument to its `_ds_wrapped` driver, merges `origin/main` three times, last 19baca76181cb019d9b1cfd93ee6bc0a08e20047, and gives the section's arbiter fake the `dhw_max_temp` that main's 4498df97 made the arbiter read; no production line moved.
## Head

9453c5e25523a963106e27aad6e9fe16846aa367

The merge base is 19baca76181cb019d9b1cfd93ee6bc0a08e20047 (`git merge-base origin/main HEAD` at this head), which is `origin/main`: this head merges it. Every command below compares three-dot against the merge base. The mutant runs, the drift, structure and architecture figures and the diff pass ran at a5e0e78df906e41e3a59b503a0b9531a8edadf22, which merged `origin/main` 6e100ef6980216a81eaa0438bdc215d62b19271f; this head differs from it by the merges of `origin/main` cbe8d93b and 19baca76 alone, whose delta from 6e100ef6 touches nothing under `custom_components/` and not `tests/features.py` (`git diff --stat 6e100ef69 19baca761 -- custom_components tests/features.py` prints nothing), so the diff pass's mutant set and the section are the same. The scoped gate (`GOLDEN_REF=cbe8d93b`) ran at f6b7356ef7dc89555f5182f5a3a5e0f830f4c503, which merged `origin/main` cbe8d93b; this head adds only the merge of `origin/main` 19baca76, whose delta from cbe8d93b is seven files under `tools/plan/`, `tools/audit/seat/`, `dev/audit/harnesses/` and `dev/programme/delivery/`, and nothing under `custom_components/` or `tests/`. `tools/pr/prepr.sh` with this body ran at this head.
## Brief carries

- Carry 1 (the build input; the brief prints it as carry 0): done as asked. The branch starts from pull request 3420's ten commits at e05c6b1ccc17f2486160669f4a64a33b79ea6a17, the head `git ls-remote origin refs/pull/3420/head` still printed at the start, re-committed with author and author date kept; the build was measured against the approved design and the reviewer's comparison section, as the next section answers line by line, and not rebuilt from scratch: the episode and void logic, the pass-confirmed debounce, the store's three census registrations and the stop, kept, defrost and reload tests are the contributor's, moved behind the design's seam.
- Carry 2 (this body's own round-1 item be768cab, folded onto the roster): done in the tree. `docs/design/2026-11-10-duty-switch-restart-learning/design.md`, section "Part A as built", now holds it: no read API and where the first reader goes, the conditional keys, the wider loop void, n with no ceiling but the load bound. The groups it constrains are parts B and C, so it is carried on to their briefs under Forward-carry.
- Carry 3 (round-1 item 25e8fe39, folded likewise): done in the tree, in the same section of the design note: the supply minimum-run hold of pull request 3420 is removed and built nowhere. Where it is built is the orchestrator's decision and is not made here.

## What was cut from pull request 3420, and what moved

Each line answers one conflict of `verdict.md`'s section "Pull request 3420 at e05c6b1ccc against this design" on `design-verdict/R10-DUTY-SWITCH-RESTART-LEARNING`.

- Scope: `supply_hold.py`, `cycle_supply`, the retry in `supply_tick`, the split hook in `_share`, and the edits to `coordinator.py` and `early_cutoff.py` are removed; `git diff origin/main...HEAD --stat -- custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/early_cutoff.py custom_components/heatpump_optimizer/diagnostics.py` prints nothing.
- Seam: `ArbiterState` gains no field; `duty_switch.py` holds a `WeakKeyDictionary` registry of its own and no longer imports `pump_arbiter.py`. The arbiter makes four calls into it (`attach`, `detach`, `note_mode_write`, `note_pass`) and builds the context in `_switch_context` and `_report_write`.
- Running signal: `wear.compressor_running` and `wear.EdgeTracker`. The floor is `RUNNING_FLOOR_HZ`, the line `freq_control.FrequencyMap.observe` already refuses a sample under (item n9: no install's stopped reading was available to this seat; the constant says so).
- Estimate: two decayed weights per direction, a stored latch with the four thresholds, an off list capped on write and refused on load when longer.
- Load: a record loads whole or empty (`DutySwitchLearner.from_record`); a failed read is not marked loaded.
- Heated gate: `_flow_inlet_c`, per direction (below).
- Void list: the feedback loop and the same-option re-send are added.
- Publication: the sensor's attributes; the diagnostics key is removed.
- `tests/guard_pins.py`'s two coordinator stubs gain an `entry`: the learner's store is keyed on it as the arbiter's is, and the stubs had none because the arbiter's own persist swallows the `AttributeError`.

## Departures from the approved design, each for the owner or reviewer to overrule

- Store encoding. The design stores k and n. `Direction` stores k and the kept weight, n their sum: with k and n, `tests/finite_boundary.py`'s in-domain probe of k exceeded n, was refused as k > n and read as unreached; two addends make every in-domain pair valid. Published attributes are still k and n.
- Tallies. `stopped` and `kept` are stored integers beside `void` and `censored`: the design publishes them and its store list omits them.
- Read API. The design lists a read API "unused in A". It is not built: an unused module-level function raises `dead_top_level_symbols`, which sits at zero headroom. `Direction.usable`, `.p` and `.median_off_s` hold the three values.
- Origin (share, lease, other) is not in the context: nothing in A reads it.
- 3405's loop voids on any target the loop moved off the open-loop one (`FeedbackRun.sent_c` set), raised as well as lowered: the base is not in reach of the pass, and a wider void costs evidence only.
- Source-leg age is the replaced mode record's age, not `dhw_since`, which `_leased` has already reset on the pass that leaves hot water.
- The space set-point the heated gate reads is the command's, written right after the mode, not the written record, which at that instant is still the hot-water leg's.
- Publication is conditional. Five `coord_*` goldens snapshot the starts sensor's `extra_state_attributes`, so the design's premise that the sensor is off the goldens does not hold, and fourteen always-present keys read as five stale fixtures in `tests/env_drift.py --all`. A direction publishes its keys only once it holds a stopped, kept or void episode; an install that never switches duty while running publishes what it did before, and no golden moves. Mutant `publish_only_observed`.
- Factory reset keeps the store (`_FR_STORES`, the contributor's disposition). Learned state elsewhere is voided there; the owner may want this voided too.

## Review round 7, answered

1. mutation-vacuous. The survivor is killed by one check added to the duty-switch section, beside its null control; it is not triaged.
   - `r7v_unsettled_with_pending_runs` (`duty_switch.note_mode_write` counting an unsettled tracker with an edge pending as running): "through duty_switch.note_mode_write, a mode write on a record just loaded whose first reading, 50 Hz, came inside the debounce before the write and is still pending opens nothing and books nothing". Driven through `_Record`, `note_signal`, `note_mode_write` and `note_pass`: `_ds_wrapped`'s new `fresh` argument skips the settling reading and pass, so the record is as loaded (`settled is None`); its first reading, 50 Hz, is taken `_DS_START_LEAD` (10 s) before the hot water to heating write with no pass between, so it is pending at the write; nothing opens and nothing is booked, whether the reading holds through the window or reads 0 Hz 15 s after the write. The check asserts `0 < _DS_START_LEAD < wear.EDGE_DEBOUNCE_S`. Null control: the running row of the round-5 check, the compressor settled running at the write, books it kept through the same passes. `fresh` defaults to False and leaves every earlier call unchanged.
   The failing check, from applying the mutant to a `git archive` copy of this head and running the section:
   ```
     FAIL through duty_switch.note_mode_write, a mode write on a record just loaded whose first reading, 50 Hz, came inside the debounce before the write and is still pending opens nothing and books noth
   1 of 59 DUTY-SWITCH SECTION CHECKS FAILED
   ```
   The reviewer's command, `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'env PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py'`, with each of the verdict's two round-7 specs read from `probe/rev-3461-ba74baae` (`ev/reviewer_mutant_spec_round7.json`, `ev/reviewer_mutant_spec_round7b.json`), at the repair commit, before the merge:
   ```
   ### round7
   SURVIVED NULL
   KILLED r7v_unsettled_with_pending_runs
   KILLED r7v_stopped_with_pending_runs_only
   KILLED r7v_pending_start_counts
   KILLED r7v_unsettled_no_pending_runs
   ### round7b
   SURVIVED NULL
   KILLED r7v_running_with_pending_runs
   KILLED r7v_stopped_no_pending_runs
   ```
   Control: the verdict's `ev/mutants_reviewer_round7.txt` prints `SURVIVED` for `r7v_unsettled_with_pending_runs` at 112f0d77. Both round-7 specs are appended to this body's spec (Mutant spec) and were re-run whole at this head (Mutation proof).
2. The whole-branch diff pass, run by this seat before the handoff, found one survivor beyond the three recorded: `duty_switch.py:396 STMT_DEL`, the alias `Reader = Callable[...]` deleted, an operator `mutant_run.py` gained on main since the last body. Killed, not triaged: Python 3.14 defers the arbiter's `-> tuple[str | None, duty_switch.Reader]` annotation, but Home Assistant 2025.2, this integration's floor in `hacs.json`, runs 3.13, which evaluates it when `pump_arbiter` is imported. The check "the reader's annotations resolve, as Python 3.13 resolves the arbiter's at import" resolves `_running_signal`'s and `attach`'s annotations with `typing.get_type_hints` and asserts they name one reader type; null control, a seam annotated with a name no module binds does not resolve. Under the mutant (spec entry `r8f_reader_alias_deleted`), in a `git archive` copy:
   ```
     FAIL the reader's annotations resolve, as Python 3.13 resolves the arbiter's at import: _running_signal returns and attach takes the one reader type; null control, a seam annotated with a name no mo
   1 of 59 DUTY-SWITCH SECTION CHECKS FAILED
   ```
3. The merge of `origin/main` 6e100ef6 broke the section on a line git reported nowhere: main's 4498df97 has `pump_arbiter._dhw_write` read `params.dhw_max_temp` and gave main's fakes the field, and this branch's `_DsArb` fake lacked it (`AttributeError` in the section). The fake now carries `dhw_max_temp=60.0`, above the 50 C set-point the censor check writes; a limit equal to the 48 C set-point, as main's fakes carry, capped that write away and failed the censor check. The diff pass at the merge is how it was found, refusing on its baseline.
4. Findings: the fence of the body's `## Mutant spec` opens `json` again; the round count is the seventh review, answered by this repair; no finder harness exists, as in rounds 1 to 6.

## Verdict notes

- n10: the heated gate is per direction (`duty_switch._heated`): inlet minus water set-point into space (round 2: only where the set-point is a water temperature), the source leg's age into hot water; the table's three kept rows pin it with an inlet under the set-point. Mutant `heated_direction_gate`.
- n12: built to the note's rule, empty on any invalid shape or bound.
- n13: `DutySwitchLearner`, `Direction` and `SwitchContext` take no Home Assistant object; the tests drive them directly.
- n14: one call, `duty_switch.starts_attributes`, returns the finished dict; the check the note asks for found the opposite of what the design assumed: the five `coord_*` fixtures do hold that sensor's attributes. See the conditional publication above.
- n15: `functions_cc_over_15` and `methods_over_150` read as at the merge base (`python3 tests/structure.py`); the report is one unconditional call in `_write`, its filter in `_report_write`.
- n16: the note reads a re-send as returning before the service call. It does not: `hold` drops the record first, so `_write` sees none and sends. The report sits after the landed write, and a test drives a person's change through `hold` and the re-send.
- n17: n1 to n7 stand; n5 as widened above.

## Mutation proof

Every mutant ran through `tools/audit/seat/mutant_run.py`, in its `git archive` copy, at the head above, with one command: `env PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`.

**The spec** (`--spec`, at the end of this body): the previous body's 149 entries, then the round-7 reviewer's two specs whole (`r7v_`) and this seat's `r8f_reader_alias_deleted`. The count is the `KILLED` lines below, 156, one run with the null surviving; `SURVIVED NULL` is the unmutated tree.

```
SURVIVED NULL
KILLED latch_n_on
KILLED latch_p_on
KILLED latch_span_on
KILLED latch_n_off
KILLED latch_p_off
KILLED void_supply_off
KILLED void_not_plan_control
KILLED void_defrost
KILLED void_disinfection
KILLED void_boost
KILLED void_electric_heat
KILLED void_fault
KILLED void_feedback_loop
KILLED void_foreign_write
KILLED void_no_signal_edge
KILLED void_other_mode_write
KILLED void_stopped_before_write
KILLED void_check_after_stop
KILLED count_running
KILLED count_heated
KILLED count_demand
KILLED count_plan_stays
KILLED count_no_void_at_open
KILLED heated_margin
KILLED heated_source_leg
KILLED heated_direction_gate
KILLED window_stop_inside
KILLED window_expiry
KILLED window_pending_holds
KILLED censor_on_write
KILLED censor_on_cause
KILLED off_cap
KILLED decay_scales_k
KILLED load_strict_fields
KILLED load_empty_on_invalid
KILLED load_off_cap
KILLED load_retry
KILLED report_before_load_dropped
KILLED pending_blocks_open
KILLED pass_confirms_edge
KILLED save_on_change
KILLED debounce
KILLED one_frame_zero
KILLED edge_keeps_first_time
KILLED floor_inclusive
KILLED no_signal_is_none
KILLED source_never_mixed
KILLED report_line_in_write
KILLED pass_call
KILLED attach
KILLED detach
KILLED report_slot_filter
KILLED context_defrost
KILLED reader_frequency_sensor
KILLED publish
KILLED feed_edge_to_learner
KILLED publish_only_observed
KILLED rv_median_first
KILLED rv_no_decay
KILLED rv_stamp_not_advanced
KILLED rv_book_no_latch
KILLED rv_load_day_order
KILLED rv_load_bool_tally
KILLED rv_load_direction_set
KILLED rv_load_row_keys
KILLED rv_off_time_dropped
KILLED rv_pass_decay_dropped
KILLED rv_detach_keeps_episode
KILLED rv_persist_stays_dirty
KILLED rv_published_undecayed
KILLED rv_ctx_supply
KILLED rv_ctx_plan_control
KILLED rv_ctx_disinfecting
KILLED rv_ctx_boost
KILLED rv_ctx_electric
KILLED rv_ctx_fault
KILLED rv_ctx_loop
KILLED rv_ctx_mode_at
KILLED rv_ctx_last_write
KILLED rv_gate_demand_true
KILLED rv_gate_plan_any
KILLED rv_gate_source_leg
KILLED rv_gate_setpoint
KILLED rv_gate_inlet
KILLED rv_reader_power_threshold
KILLED rv_reader_entity_meter_only
KILLED rv_lit_ignores_freshness
KILLED rv_old_option
KILLED r2_interrupt_unchecked_void
KILLED r2_edge_none_checked
KILLED r2_explained_mode_stamp
KILLED r2_book_at_now_not_write
KILLED r2_weights_no_clamp
KILLED r2_running_ignores_pending
KILLED r2_attach_not_idempotent
KILLED r2_attach_no_first_read
KILLED r2_detach_keeps_tracker
KILLED r2_pass_after_gate
KILLED r2_ctx_defrost_entity
KILLED r2_ctx_defrost_interval
KILLED r2_ctx_booster_only
KILLED r2_ctx_boost_space_only
KILLED r2_ctx_economy_dropped
KILLED r2_gate_dhw_demand
KILLED r2_gate_plan_now_only
KILLED r2_gate_both_dropped
KILLED r2_reader_freq_floor_arg
KILLED r2_sensor_order
KILLED r2_tracker_pending_reset
KILLED r2_load_marks_loaded_on_fail
KILLED r2_tally_bool
KILLED r2_void_not_counted
KILLED r3_unit_gate_dropped
KILLED r3_unit_gate_inverted
KILLED r3_heated_no_setpoint_refuses
KILLED r3_span_never_ages
KILLED r3_span_floor_inclusive
KILLED r3_span_floor_value
KILLED r3_span_change_unreported
KILLED r3_span_last_day_kept
KILLED r3_span_reported_always
KILLED r3v_aged_on_predecay_n
KILLED r3v_span_floor_on_k
KILLED r3v_unit_gate_return_only
KILLED r3v_unit_gate_flow_only
KILLED r3v_wrapper_pending_false
KILLED r3v_wrapper_pending_true
KILLED r3v_wrapper_dirty_dropped
KILLED r3v_heated_margin_strict
KILLED r3v_heated_falls_to_leg
KILLED r3v_pass_expiry_ignores_pending
KILLED r3v_ageout_keeps_reporting
KILLED r4v_last_write_min
KILLED r4v_first_day_overwritten
KILLED r4v_plan_stays_no_both
KILLED r4v_checked_every_pass
KILLED r4v_supply_ignores_switch
KILLED r4v_tracker_settled_any
KILLED r5v_span_floor_on_kept_w
KILLED r5v_tracker_settled_not_none
KILLED r5v_tracker_settled_dropped
KILLED r5v_wrapper_pending_inverted
KILLED r5v_pass_judges_before_confirm
KILLED r5v_write_pending_ignored_when_stopped
KILLED r6v_settled_or_pending
KILLED r6v_running_const_true
KILLED r6v_stopped_with_pending_start_runs
KILLED r6v_checked_never_set
KILLED r6v_confirm_after_judge_too
KILLED r7v_unsettled_with_pending_runs
KILLED r7v_stopped_with_pending_runs_only
KILLED r7v_pending_start_counts
KILLED r7v_unsettled_no_pending_runs
KILLED r7v_running_with_pending_runs
KILLED r7v_stopped_no_pending_runs
KILLED r8f_reader_alias_deleted
rc=0
```

**The branch diff** (`--diff 6e100ef6980216a81eaa0438bdc215d62b19271f...HEAD`, at a5e0e78df9, one run over the whole branch diff, the 361 mutants `--list` enumerates; it prints survivors only): every survivor printed is listed. The `STMT_DEL` survivor at `duty_switch.py:396` that the same pass printed at the merge commit is killed (Review round 7, answered, item 2) and does not appear.

```
SURVIVED custom_components/heatpump_optimizer/duty_switch.py:82 CONST_SWAP  STORE_VERSION = 2
SURVIVED custom_components/heatpump_optimizer/duty_switch.py:187 CMP_BOUND  if self.decayed_at is None or utc_elapsed_seconds(when, self.decayed_at) >= 0.0:
SURVIVED custom_components/heatpump_optimizer/pump_arbiter.py:1991 CONST_SWAP  return resolve_reading(None, sensor, states.get, 1.0, 0.0)[0], None, None, True
rc=1
```

Each is an equivalent mutant, as recorded, and each was recorded so by the previous body at its own head:

- `duty_switch.py` `STORE_VERSION = 2`: the version is what Home Assistant's `Store` stamps on the file and compares with a stored payload's own; no migration exists for either value and `DutySwitchLearner.from_record` never reads it. The arbiter's own `_STORE_VERSION` carries the same verdict in the ledger. Record: `tests/mutation_ledger/survivor_triage/duty_switch.py/@module.CONST.43e0a892.json`.
- `duty_switch.py` `Direction.decay`, `> 0.0` to `>= 0.0`: the two differ only when the pass is at the stamp's own instant, and the guarded statement then assigns the stamp the instant it holds. The other side of the bound, a stamp half a second old, is driven ("every aging moves the stamp"). Record: `tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.decay.CMP_BOUND.225d3f33.json`.
- `pump_arbiter.py` `_running_signal`, `resolve_reading(None, sensor, states.get, 1.0, 0.0)[0]`: the fourth and fifth arguments are the range `resolve_reading` hands back as elements 1 and 2 of its tuple when no number entity is given; the reader keeps element 0 alone. No ledger record: `tests/mutation_table.py` generates no site for this operator on that line, and a disposition naming no site is refused.

**The ledger's own operators.** `tests / mutation` mutates with `tests/mutation_table.py`'s operators. Every site the diff adds was pinned by a `killed_by` record that module's own driver wrote (`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py ...`, the `ledger: pin` commits of the branch); those passes were not re-run for this body. What is re-taken is their result: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` prints no `ADDED UNPINNED` and no `STALE PIN` line at this head (Unpinned sites). This repair adds lines under `tests/` only, which the lane does not mutate.

## Null control

- `SURVIVED NULL` above: the unmutated tree passes the section.
- An install where no switch stops the compressor, one where it does, and a flat-price day: the split order and every service call are equal between an empty learner and one latched usable in both directions (three checks named "null control" in the section). They hold by construction, and a fourth check pins the construction: only `pump_arbiter.py` and `sensor.py` name `duty_switch`, through eight names none of which reads the estimate.
- Both ends of the learner's range: an empty learner publishes no key and changes nothing; one saturated at p = 1 changes nothing either.
- `tests/env_drift.py --all` against the merge base reports no unclaimed drift and no stale fixture; neither claim file is touched (`git diff origin/main...HEAD --stat -- tests/golden/` prints nothing).
- The indoor-unit rows beside the same return with a full leg; the interval defrost beside the flag reading False; Economy and Auto beside Comfort; the tank at its set-point beside 0.1 K under; the off-plan write beside the same write on a step that holds it; the aged span beside a first stop one half-life old. Both ends of the span rule's range: an empty direction has no day to forget (the section reads `Direction().span_days` as 0), and one saturated keeps its days (the latch row at n 40 switches on, which needs its two-day span).
- Each void and gate check carries its own: every void reading beside the same install with the flags off; every count gate beside the step the other side of its bound; the censoring write beside the same install without it; the aged learner beside one aged a minute.
- The round-4 checks: three stops beside the three kept episodes; no stop read beside the stop pending across the window's end; the compressor read running at the write beside the signal unknown there.
- The round-5 checks: the compressor read running at the write beside it read stopped there; the stop with no defrost and a restart beside the stop with a defrost first read on the pass after the confirming one.
- The round-6 check: the compressor settled running at the write beside it settled stopped with a start pending there.
- The round-7 checks: the compressor settled running at the write beside a record just loaded with its first reading pending there; the reader's seams resolving beside a seam annotated with an unbound name.

## Figures

- Section checks: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py` exits 0, its last line the all-passed count.
- Mutants: the `mutant_run.py` runs under Mutation proof and under "Review round 7, answered", at this head.
- The failing check per surviving mutant: each mutant's `old` text replaced by its `new` text in the working tree, in a `git archive` copy, the section run (the blocks under "Review round 7, answered").
- Unpinned sites: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` prints no `ADDED UNPINNED` and no `STALE PIN` line.
- Golden drift: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/env_drift.py --all $(git merge-base origin/main HEAD)` prints `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE`, rc 0.
- Gate mode: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`.
- Scoped gate: `MODE: SCOPED`, rc 0, every script it ran green (`TEST SCRIPT(S) PASSED` line). `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`
- Structural ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, rc 0.
- Architecture score: `python3 -I tools/audit/archscore/score.py --diff "$(git merge-base origin/main HEAD)" HEAD` prints dS -0.0081, `coord_footprint` 2492 to 2506 (Architecture score).
- Merge with main: `git merge-tree --write-tree origin/main HEAD` exits 0; this head merges `origin/main` (Head).
- Seams of the class (fixer step 8), `git grep -n -E "select_option|await _command\(" -- 'custom_components/heatpump_optimizer/*.py'`: the one mode write, in `_write`, closed in this diff by the report there; its callers `_arbitrate` and `release`, covered through it (`release` detaches first). Not changed by this repair, which touches no production file.
- `tools/pr/prepr.sh` with this body: rc 0 at this head; `origin/main` had not moved from the merge base when it ran.

## Architecture score

- coord_footprint: rises by the registry's three entry points that take the coordinator (`duty_switch.record_for`, `detach`, `starts_attributes`) and one call line each in `_write`, `_arbitrate`, `_listen` and `release_listeners`. A first cut also raised `duplication_copies`, `literal_clone_copies` and `computed_attr_access`; those were paid (a shared hand-off method, two named domains, named fields) and every function below the registry now takes the pump's record instead of the coordinator. What remains is the new feature's own entry, not a duplicate of anything.

## Unpinned sites

None at this head: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` prints no `ADDED UNPINNED` and no `STALE PIN` line. The sites carry `killed_by` records this branch commits, written by the lane's own driver; the two equivalent sites carry a `survivor_triage` record (Mutation proof).

## Red checks

- `tests / mutation`: red on pull request 3461 at 3a47c7c156ff1ee55bd0a343023606f7655d2638, as `tools/pr/prepr.sh` step 6d predicted: that head adds sites no record pins. Answered at this head by the pins: the predictor lists no unpinned and no stale site here (Unpinned sites). Cheaper detector: step 6d itself, which named every site before the push at no cost beyond the self-check; the kill runs that write a pin are the lane's own and nothing cheaper than them can pin a site.
- `tests / coverage-ratchet` and `tests / fast (3.14)`: red at 112f0d777b8f8c921a75982d36305e94ffd2f7f4 in run 43210133740, which tested that head merged with `origin/main` 6e100ef6 (the jobs' `GOLDEN_REF`). `fast` ends `1 TEST SCRIPT(S) FAILED`; the ratchet reads `COVERAGE RATCHET BREACHED` with `pump_arbiter.py` at 91.25 % under the 95 % module floor. That merge is the one under "Review round 7, answered", item 3: the duty-switch section of `tests/features.py` raises `AttributeError` on `dhw_max_temp` there, reproduced in this seat, and the script stopping early is the inferred cause of the arbiter's low coverage; which script `fast` named was not read from its log. Answered at this head by the fake's `dhw_max_temp`: the section passes, and the scoped gate runs `tests/features.py` green (Figures). Run 43218147229 at the same head reads both green. Cheaper detector: the section harness on the merged tree, seconds per run, which found it here; `prepr.sh` runs no test script on a merge of main, and the gate is what runs one.
- `tests / fast (3.14)`: red at the head the round-2 review read, 84405a2a2c96b6a7476832b5e76edd9f7b96e4a2, on `tests/features.py`'s `combi_type_branch` census, which was red on `origin/main` itself on six lines none of which this diff adds. Green on the pull request since pull request 3466 reached main, and `tests/features.py` passes at this head, which merges it (Figures). Cheaper detector: none on this branch; the script that fails is the detector, and it ran on main.
- `arch-score / arch-score`: red at 2e1e33a70a4c on its first run (job 131259916984), in the PR-lookup step on `gh: HTTP 503`; nothing was scored. The re-run (job 131265782270) is success. Cause outside this repository (GitHub API, owner GitHub). Cheaper detector: none exists. Countermeasure: a retry of the read inside the step. Carry: dismissed: transient GitHub API 503 in the PR-lookup step, re-run success, owner GitHub

## Forward-carry

- Parts B and C get no ready read API from part A: `Direction.usable`, `.p` and `.median_off_s` hold the three values, and the part that first reads them adds the module-level reader with its first caller. Control: a reader added with no caller turns `tests/structure.py`'s `dead_top_level_symbols` red. The published keys are conditional (a direction with no stopped, kept or void episode publishes none), so a reader takes an absent key as no observation, never as zero; control: the mutant `publish_only_observed` of this body's spec fails the section's attribute check. The loop void is wider than the design's and n has no ceiling but the load bound. Re-measure at the part's own merge base. Lands in `docs/design/2026-11-10-duty-switch-restart-learning/design.md`, section "Part A as built", and is owed to the group's brief on the round's roster. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The same finding for the planner's price of a switch: it reads the estimate through a reader it adds with its first caller, and an absent published key is no observation. Controls: a reader added with no caller turns `tests/structure.py`'s `dead_top_level_symbols` red, and the mutant `publish_only_observed` of this body's spec fails the section's attribute check. Lands in the same section of the design note, and is owed to the group's brief on the round's roster. Carry: R10-DUTY-SWITCH-PLANNER-PRICE
- Factory reset keeps the duty-switch store (`_FR_STORES`, "kept: observed facts"), where every other learned estimate is voided; the record holds an estimate with a latch, and voiding it would also need the in-memory learner emptied. Accepted by the review for part A, where nothing reads the estimate; the owner rules before a part does. Lands in the design note's "Part A as built". Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The supply minimum-run hold of pull request 3420 is removed and built nowhere; where it goes is the orchestrator's decision the design verdict routed. Lands in the design note's "Part A as built". Carry: R10-DUTY-SWITCH-RESTART-LEARNING
- `tests/features.py`'s `combi_type_branch` census was red on `origin/main` itself while pull requests 3398 and 3433 had both landed and 3466 had not: the census refuses a vendor name in the package's Python and six comment lines named one. Pull request 3466 reworded those lines on main, this head merges it, and the script passes here (Figures). Carry: dismissed: resolved on main by pull request 3466
- `usable` needs a sixth episode in practice: each booking decays the earlier ones first, so five stops ten hours apart end at n under `N_ON` (the reviewer's probe, `fifth_episode`; control: five bookings at one instant reach it, the section's "a stop taking n from 4 to 5"). The part that first reads `usable` decides whether `N_ON` means five episodes or a weight of five. Re-measure with the probe at that part's merge base. Owed to the group's brief on the round's roster. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The published k and n decay continuously, so the starts sensor's attributes change with no observation (the reviewer's probe, `attr_churn`; control: an empty learner publishes nothing). Not changed in part A; the part that first reads or widens the publication decides its resolution. Re-measure with the probe. Owed to the same brief. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- `span_days` now reads 0 beside non-zero tallies once a direction's weight is under `SPAN_FLOOR_N`: a reader takes that as "nothing recent", never as "never observed". Control: the mutant `r3_span_never_ages` fails the section's span check. In `docs/design/2026-11-10-duty-switch-restart-learning/design.md`, "Part A as built"; owed to the same brief. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The heated gate is decided per set-point unit, and on a water unit it compares the inlet with the commanded set-point, which `_flow_target` keeps at or above the inlet plus the minimum lift up to the heating ceiling: a hot water to space switch there counts only with the return `HEATED_MARGIN_K` over that ceiling (the section's return and flow rows, one each side of the bound). On the indoor unit every switch after a source leg of `SOURCE_LEG_MIN_S` counts. So evidence accrues at different rates per unit, and a part reading n must not assume otherwise. Controls: `r3_unit_gate_dropped` and `r3_unit_gate_inverted`. Re-measure with the section at that part's merge base. In the design note's "Part A as built"; owed to the same brief. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B

## Friction

- fixer.md: unclear: the brief has the build start from pull request 3420's commits with authorship kept, and `ref_privacy.py guard` refuses all ten for a session trailer and a co-author trailer in each message; they were re-committed with author and date kept and those two lines dropped, which `--adopt-email` then admits. Carry: dismissed: resolved in this pull request, the adopt arm's note could say a message is judged too
- fixer.md: cost: a new production module read by the arbiter re-records 22 closures before the gate can scope. Carry: dismissed: the price of a measured closure, paid once
- fixer.md: cost: `mutant_run.py --diff` carries five operators and `tests / mutation` seven, three of them not shared, so a diff pass with no survivor still left one site the lane would have refused; the ledger's replacements had to be turned into a spec by hand to see it. Carry: dismissed: one site in this diff, and the lane itself reports it at the pull request
- fixer.md: cost: two seats worked this topic at once, one repairing the blocked head and one merging main and pinning; the first handed off and froze `handoff/` while the second's line was being built, so the second stopped on a question and a third seat re-took the whole body at the merged head. Carry: dismissed: the orchestrator ruled on it in this seat's dispatch, and the line lands as a fast-forward
- fixer.md: cost: main's `_pump_off` gained an argument and `off_restore` a weak reference to the entry while this branch was in review, so a conflict git reported in two files also broke a call and a fake it reported nowhere, and a third pull request landing during the measurement broke the fake again and cost a second merge and a second full re-take; the section harness found each in one run. Carry: dismissed: found by the group's own harness on the merged tree, before the handoff
- fixer.md: cost: merging main broke the section on a fake git did not report, main's arbiter newly reading `params.dhw_max_temp`; found by the diff pass refusing its baseline, before the handoff. Carry: dismissed: found by the group's own harness on the merged tree

## Mutant spec

```json
[
 {
  "name": "latch_n_on",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "self.usable = self.n >= N_ON and",
  "new": "self.usable = True and"
 },
 {
  "name": "latch_p_on",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and self.p >= P_ON and",
  "new": "and True and"
 },
 {
  "name": "latch_span_on",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and self.span_days >= SPAN_DAYS_ON",
  "new": "and True"
 },
 {
  "name": "latch_n_off",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "not (self.n < N_OFF or",
  "new": "not (False or"
 },
 {
  "name": "latch_p_off",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "or self.p < P_OFF)",
  "new": "or False)"
 },
 {
  "name": "void_supply_off",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"supply_off\", not self.supply_on)",
  "new": "(\"supply_off\", False)"
 },
 {
  "name": "void_not_plan_control",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"not_plan_control\", not self.plan_control)",
  "new": "(\"not_plan_control\", False)"
 },
 {
  "name": "void_defrost",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"defrost\", self.defrosting)",
  "new": "(\"defrost\", False)"
 },
 {
  "name": "void_disinfection",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"disinfection\", self.disinfecting)",
  "new": "(\"disinfection\", False)"
 },
 {
  "name": "void_boost",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"boost\", self.boost_held)",
  "new": "(\"boost\", False)"
 },
 {
  "name": "void_electric_heat",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"electric_heat\", self.electric_heat)",
  "new": "(\"electric_heat\", False)"
 },
 {
  "name": "void_fault",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"fault\", self.fault)",
  "new": "(\"fault\", False)"
 },
 {
  "name": "void_feedback_loop",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "(\"feedback_loop\", self.loop_moved)",
  "new": "(\"feedback_loop\", False)"
 },
 {
  "name": "void_foreign_write",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "explained = ctx.void_cause() is not None or ctx.mode_written_at != ep.at",
  "new": "explained = ctx.void_cause() is not None"
 },
 {
  "name": "void_no_signal_edge",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._close(ep, True, None) if ep.checked else self._void(ep)",
  "new": "return False"
 },
 {
  "name": "void_other_mode_write",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._void(ep) if ep.stop_at is None else self._close(ep, True, None)",
  "new": "return self._close(ep, True, None)"
 },
 {
  "name": "void_stopped_before_write",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if since_s < 0.0:",
  "new": "if False:"
 },
 {
  "name": "void_check_after_stop",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            if explained:\n                return self._void(ep)\n        wrote",
  "new": "            if False:\n                return self._void(ep)\n        wrote"
 },
 {
  "name": "count_running",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "direction is not None and running and _heated",
  "new": "direction is not None and _heated"
 },
 {
  "name": "count_heated",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and _heated(direction, ctx) and ctx.target_demand",
  "new": "and ctx.target_demand"
 },
 {
  "name": "count_demand",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and ctx.target_demand\n",
  "new": "and True\n"
 },
 {
  "name": "count_plan_stays",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and ctx.plan_stays and",
  "new": "and"
 },
 {
  "name": "count_no_void_at_open",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "and ctx.void_cause() is None):",
  "new": "):"
 },
 {
  "name": "heated_margin",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "ctx.inlet_c - ctx.water_setpoint_c >= HEATED_MARGIN_K",
  "new": "ctx.inlet_c - ctx.water_setpoint_c >= -100.0"
 },
 {
  "name": "heated_source_leg",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "ctx.source_leg_s >= SOURCE_LEG_MIN_S",
  "new": "ctx.source_leg_s >= 0.0"
 },
 {
  "name": "heated_direction_gate",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if direction == \"dhw_space\" and ctx.inlet_c is not None and ctx.water_setpoint_c is not None:",
  "new": "if ctx.inlet_c is not None and ctx.water_setpoint_c is not None:"
 },
 {
  "name": "window_stop_inside",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if since_s > STOP_WINDOW_S:",
  "new": "if False:"
 },
 {
  "name": "window_expiry",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "utc_elapsed_seconds(when, ep.at) >= STOP_WINDOW_S:",
  "new": "utc_elapsed_seconds(when, ep.at) >= 0.0:"
 },
 {
  "name": "window_pending_holds",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if not pending and utc_elapsed_seconds",
  "new": "if utc_elapsed_seconds"
 },
 {
  "name": "censor_on_write",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if wrote or explained:",
  "new": "if explained:"
 },
 {
  "name": "censor_on_cause",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if wrote or explained:\n            return self._close(ep, True, None)\n        return changed",
  "new": "if wrote:\n            return self._close(ep, True, None)\n        return changed"
 },
 {
  "name": "off_cap",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "[*self.off_s, off_s][-OFF_SAMPLES_MAX:]",
  "new": "[*self.off_s, off_s]"
 },
 {
  "name": "decay_scales_k",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "self.k, self.kept_w = self.k * factor, self.kept_w * factor",
  "new": "self.kept_w = self.kept_w * factor"
 },
 {
  "name": "load_strict_fields",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "set(row) != _ROW_KEYS or not all(",
  "new": "set(row) != _ROW_KEYS or not any("
 },
 {
  "name": "load_empty_on_invalid",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        except (TypeError, KeyError, ValueError, OverflowError):\n            return cls()",
  "new": "        except (TypeError, KeyError, OverflowError):\n            return cls()"
 },
 {
  "name": "load_off_cap",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "len(v) <= OFF_SAMPLES_MAX and",
  "new": "True and"
 },
 {
  "name": "load_retry",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            return False\n        rec.learner, rec.loaded",
  "new": "            rec.loaded = True\n            return False\n        rec.learner, rec.loaded"
 },
 {
  "name": "report_before_load_dropped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    if not rec.loaded:\n        return\n    running",
  "new": "    running"
 },
 {
  "name": "pending_blocks_open",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "rec.tracker.settled is True"
 },
 {
  "name": "pass_confirms_edge",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    rec.feed(rec.tracker.confirm(when))\n",
  "new": "    rec.feed(None)\n"
 },
 {
  "name": "save_on_change",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    if rec.dirty:\n        await _persist(rec)",
  "new": "    if False:\n        await _persist(rec)"
 },
 {
  "name": "debounce",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "utc_elapsed_seconds(when, pending[1]) < EDGE_DEBOUNCE_S",
  "new": "utc_elapsed_seconds(when, pending[1]) < 0.0"
 },
 {
  "name": "one_frame_zero",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "        if running == self.settled:\n            self.pending = None\n            return None",
  "new": "        if running == self.settled:\n            return None"
 },
 {
  "name": "edge_keeps_first_time",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "if self.pending is None or self.pending[0] != running:",
  "new": "if True:"
 },
 {
  "name": "floor_inclusive",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "return bool(float(reading) >= float(floor))",
  "new": "return bool(float(reading) > float(floor))"
 },
 {
  "name": "no_signal_is_none",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "if reading is None or floor is None or not (np.isfinite(reading) and np.isfinite(floor)):\n        return None",
  "new": "if reading is None or floor is None or not (np.isfinite(reading) and np.isfinite(floor)):\n        return False"
 },
 {
  "name": "source_never_mixed",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "reading, floor = (frequency_hz, RUNNING_FLOOR_HZ) if by_frequency else (power_kw, threshold_kw)",
  "new": "reading, floor = (frequency_hz, RUNNING_FLOOR_HZ) if frequency_hz is not None else (power_kw, threshold_kw)"
 },
 {
  "name": "report_line_in_write",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    _report_write(duty_switch.record_for(coord), boost.held_for(coord), held, inp, slot, recorded, now, command)\n",
  "new": "    pass\n"
 },
 {
  "name": "pass_call",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))\n",
  "new": "    pass\n"
 },
 {
  "name": "attach",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    duty_switch.attach(duty_switch.record_for(coord), *_running_signal(inp))\n",
  "new": "    pass\n"
 },
 {
  "name": "detach",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    duty_switch.detach(coord)\n",
  "new": "    pass\n"
 },
 {
  "name": "report_slot_filter",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if slot != \"mode\":\n        return\n    context, mode",
  "new": "    context, mode"
 },
 {
  "name": "context_defrost",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "defrosting=bool(defrost_interval(inp.defrosting)) or _lit(inp, CONF_HEAT_PUMP_DEFROST_ENTITY),",
  "new": "defrosting=False,"
 },
 {
  "name": "reader_frequency_sensor",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "return resolve_reading(None, sensor, states.get, 0.0, 0.0)[0], None, None, True",
  "new": "return None, None, None, True"
 },
 {
  "name": "publish",
  "file": "custom_components/heatpump_optimizer/sensor.py",
  "old": "return {**starts, **duty_switch.starts_attributes(self.coordinator)}",
  "new": "return {**starts}"
 },
 {
  "name": "feed_edge_to_learner",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            self.dirty = self.learner.edge(*edge) or self.dirty",
  "new": "            pass"
 },
 {
  "name": "publish_only_observed",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            if not (d.stopped or d.kept or d.void):\n                continue",
  "new": "            if False:\n                continue"
 },
 {
  "name": "rv_median_first",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return (offs[(len(offs) - 1) // 2] + offs[len(offs) // 2]) / 2.0 if offs else None",
  "new": "return offs[0] if offs else None"
 },
 {
  "name": "rv_no_decay",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "factor = 0.5 ** (age_s / (HALF_LIFE_DAYS * 86400.0))",
  "new": "factor = 1.0"
 },
 {
  "name": "rv_stamp_not_advanced",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            self.decayed_at = when\n",
  "new": "            pass\n"
 },
 {
  "name": "rv_book_no_latch",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "                self.off_s = [*self.off_s, off_s][-OFF_SAMPLES_MAX:]\n        self._latch()",
  "new": "                self.off_s = [*self.off_s, off_s][-OFF_SAMPLES_MAX:]"
 },
 {
  "name": "rv_load_day_order",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "first is not None and last is not None and first > last",
  "new": "False"
 },
 {
  "name": "rv_load_bool_tally",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "isinstance(value, (int, float)) and not isinstance(value, bool) and",
  "new": "isinstance(value, (int, float)) and"
 },
 {
  "name": "rv_load_direction_set",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if not isinstance(rows, dict) or set(rows) != set(DIRECTIONS):",
  "new": "if not isinstance(rows, dict):"
 },
 {
  "name": "rv_load_row_keys",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "set(row) != _ROW_KEYS or not all(",
  "new": "not all("
 },
 {
  "name": "rv_off_time_dropped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._close(ep, True, utc_elapsed_seconds(when, ep.stop_at)) if running else False",
  "new": "return self._close(ep, True, None) if running else False"
 },
 {
  "name": "rv_pass_decay_dropped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "changed = any([d.decay(when) for d in self.directions.values()])",
  "new": "changed = False"
 },
 {
  "name": "rv_detach_keeps_episode",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.unsub, rec.reader, rec.tracker, rec.learner.episode = None, None, wear.EdgeTracker(), None",
  "new": "rec.unsub, rec.reader, rec.tracker = None, None, wear.EdgeTracker()"
 },
 {
  "name": "rv_persist_stays_dirty",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        return\n    rec.dirty = False",
  "new": "        return\n    rec.dirty = True"
 },
 {
  "name": "rv_published_undecayed",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "k, n = d.weights(when)",
  "new": "k, n = d.k, d.n"
 },
 {
  "name": "rv_ctx_supply",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "supply_on=not _pump_off(inp, held),",
  "new": "supply_on=True,"
 },
 {
  "name": "rv_ctx_plan_control",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "plan_control=inp.mode in (MODE_AUTO, MODE_ECONOMY) and duty_mode(inp.config) == DUTY_CONTROL,",
  "new": "plan_control=True,"
 },
 {
  "name": "rv_ctx_disinfecting",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "disinfecting=bool(inp.disinfecting),",
  "new": "disinfecting=False,"
 },
 {
  "name": "rv_ctx_boost",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "boost_held=any(boosts.active(c, now) for c in (boost.CHANNEL_SPACE, boost.CHANNEL_DHW)),",
  "new": "boost_held=False,"
 },
 {
  "name": "rv_ctx_electric",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "electric_heat=_lit(inp, CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY, CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY),",
  "new": "electric_heat=False,"
 },
 {
  "name": "rv_ctx_fault",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "fault=_lit(inp, CONF_HEAT_PUMP_FAULT_ENTITY),",
  "new": "fault=False,"
 },
 {
  "name": "rv_ctx_loop",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "loop_moved=held.feedback is not None and held.feedback.sent_c is not None,",
  "new": "loop_moved=False,"
 },
 {
  "name": "rv_ctx_mode_at",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "mode_written_at=mode[1] if mode else None,",
  "new": "mode_written_at=None,"
 },
 {
  "name": "rv_ctx_last_write",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "last_write_at=max((at for _value, at in held.written.values()), default=None),",
  "new": "last_write_at=None,"
 },
 {
  "name": "rv_gate_demand_true",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "target_demand=_reads_below(room, planned) if target == \"space\" else _reads_below(tank, inp.params.dhw_setpoint),",
  "new": "target_demand=True,"
 },
 {
  "name": "rv_gate_plan_any",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "plan_stays=all(step_duty(inp.plan, at) in (target, \"both\")",
  "new": "plan_stays=any(step_duty(inp.plan, at) in (target, \"both\")"
 },
 {
  "name": "rv_gate_source_leg",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "source_leg_s=utc_elapsed_seconds(now, replaced[1]) if replaced else None,",
  "new": "source_leg_s=1e9,"
 },
 {
  "name": "rv_gate_setpoint",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "inlet_c=_flow_inlet_c(inp), water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "inlet_c=_flow_inlet_c(inp), water_setpoint_c=0.0 if _flow_unit(inp.config) else None,"
 },
 {
  "name": "rv_gate_inlet",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "inlet_c=_flow_inlet_c(inp), water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "inlet_c=None, water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,"
 },
 {
  "name": "rv_reader_power_threshold",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "return None, state_power_kw(states.get(meter), \"clamp\"), on_threshold_kw(thermal.params), False",
  "new": "return None, state_power_kw(states.get(meter), \"clamp\"), 0.0, False"
 },
 {
  "name": "rv_reader_entity_meter_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    return sensor or meter, reader",
  "new": "    return meter, reader"
 },
 {
  "name": "rv_lit_ignores_freshness",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "return any(reading.ok and bool(reading.flag) for reading in map(reader.read_bool, keys))",
  "new": "return any(bool(reading.flag) for reading in map(reader.read_bool, keys))"
 },
 {
  "name": "rv_old_option",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "duty_switch.note_mode_write(learner, now, replaced[0] if replaced else None, mode, context)",
  "new": "duty_switch.note_mode_write(learner, now, None, mode, context)"
 },
 {
  "name": "r2_interrupt_unchecked_void",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._void(ep) if ep.stop_at is None else self._close(ep, True, None)",
  "new": "return self._void(ep)"
 },
 {
  "name": "r2_edge_none_checked",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._close(ep, True, None) if ep.checked else self._void(ep)",
  "new": "return self._void(ep)"
 },
 {
  "name": "r2_explained_mode_stamp",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "explained = ctx.void_cause() is not None or ctx.mode_written_at != ep.at",
  "new": "explained = ctx.void_cause() is not None"
 },
 {
  "name": "r2_book_at_now_not_write",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        day = when.date()\n        self.first_day, self.last_day = self.first_day or day, max(self.last_day or day, day)",
  "new": "        day = when.date()\n        self.first_day, self.last_day = day, max(self.last_day or day, day)"
 },
 {
  "name": "r2_weights_no_clamp",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "age_s = max(0.0, utc_elapsed_seconds(when, self.decayed_at))",
  "new": "age_s = utc_elapsed_seconds(when, self.decayed_at)"
 },
 {
  "name": "r2_running_ignores_pending",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is True"
 },
 {
  "name": "r2_attach_not_idempotent",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if rec.unsub is not None or not entity:",
  "new": "if not entity:"
 },
 {
  "name": "r2_attach_no_first_read",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    rec.unsub = async_track_state_change_event(rec.hass, [entity], _changed)\n    note_signal(rec, dt_util.now())",
  "new": "    rec.unsub = async_track_state_change_event(rec.hass, [entity], _changed)"
 },
 {
  "name": "r2_detach_keeps_tracker",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.unsub, rec.reader, rec.tracker, rec.learner.episode = None, None, wear.EdgeTracker(), None",
  "new": "rec.unsub, rec.reader, rec.learner.episode = None, None, None"
 },
 {
  "name": "r2_pass_after_gate",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))\n    if mode != DUTY_CONTROL or _pump_off(inp, held):\n        return",
  "new": "    if mode != DUTY_CONTROL or _pump_off(inp, held):\n        return\n    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))"
 },
 {
  "name": "r2_ctx_defrost_entity",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "defrosting=bool(defrost_interval(inp.defrosting)) or _lit(inp, CONF_HEAT_PUMP_DEFROST_ENTITY),",
  "new": "defrosting=bool(defrost_interval(inp.defrosting)),"
 },
 {
  "name": "r2_ctx_defrost_interval",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "defrosting=bool(defrost_interval(inp.defrosting)) or _lit(inp, CONF_HEAT_PUMP_DEFROST_ENTITY),",
  "new": "defrosting=_lit(inp, CONF_HEAT_PUMP_DEFROST_ENTITY),"
 },
 {
  "name": "r2_ctx_booster_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "electric_heat=_lit(inp, CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY, CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY),",
  "new": "electric_heat=_lit(inp, CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY),"
 },
 {
  "name": "r2_ctx_boost_space_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "for c in (boost.CHANNEL_SPACE, boost.CHANNEL_DHW)),",
  "new": "for c in (boost.CHANNEL_SPACE,)),"
 },
 {
  "name": "r2_ctx_economy_dropped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "plan_control=inp.mode in (MODE_AUTO, MODE_ECONOMY) and duty_mode(inp.config) == DUTY_CONTROL,",
  "new": "plan_control=inp.mode in (MODE_AUTO,) and duty_mode(inp.config) == DUTY_CONTROL,"
 },
 {
  "name": "r2_gate_dhw_demand",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "if target == \"space\" else _reads_below(tank, inp.params.dhw_setpoint),",
  "new": "if target == \"space\" else True,"
 },
 {
  "name": "r2_gate_plan_now_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "for at in (now, utc_shift(now, timedelta(seconds=duty_switch.STOP_WINDOW_S)))),",
  "new": "for at in (utc_shift(now, timedelta(seconds=duty_switch.STOP_WINDOW_S)),)),"
 },
 {
  "name": "r2_gate_both_dropped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "plan_stays=all(step_duty(inp.plan, at) in (target, \"both\")",
  "new": "plan_stays=all(step_duty(inp.plan, at) in (target,)"
 },
 {
  "name": "r2_reader_freq_floor_arg",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "return resolve_reading(None, sensor, states.get, 0.0, 0.0)[0], None, None, True",
  "new": "return resolve_reading(None, sensor, states.get, 0.0, 0.0)[0], None, None, False"
 },
 {
  "name": "r2_sensor_order",
  "file": "custom_components/heatpump_optimizer/sensor.py",
  "old": "return {**starts, **duty_switch.starts_attributes(self.coordinator)}",
  "new": "return {**duty_switch.starts_attributes(self.coordinator)}"
 },
 {
  "name": "r2_tracker_pending_reset",
  "file": "custom_components/heatpump_optimizer/wear.py",
  "old": "        if self.pending is None or self.pending[0] != running:\n            self.pending = (running, when)",
  "new": "        self.pending = (running, when)"
 },
 {
  "name": "r2_load_marks_loaded_on_fail",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            _LOGGER.debug(\"Could not load the duty-switch record: %s\", err)\n            return False",
  "new": "            _LOGGER.debug(\"Could not load the duty-switch record: %s\", err)\n            rec.loaded = True\n            return False"
 },
 {
  "name": "r2_tally_bool",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return isinstance(value, int) and _stored_number(value, _TALLY_MAX)",
  "new": "return _stored_number(value, _TALLY_MAX)"
 },
 {
  "name": "r2_void_not_counted",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        self.episode = None\n        self.directions[ep.direction].void += 1",
  "new": "        self.episode = None"
 },
 {
  "name": "r3_unit_gate_dropped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "water_setpoint_c=command.space_setpoint,"
 },
 {
  "name": "r3_unit_gate_inverted",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "water_setpoint_c=None,"
 },
 {
  "name": "r3_heated_no_setpoint_refuses",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if direction == \"dhw_space\" and ctx.inlet_c is not None and ctx.water_setpoint_c is not None:",
  "new": "if direction == \"dhw_space\" and ctx.inlet_c is not None and ctx.water_setpoint_c is None:\n        return False\n    if direction == \"dhw_space\" and ctx.inlet_c is not None:"
 },
 {
  "name": "r3_span_never_ages",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N",
  "new": "aged_out = False"
 },
 {
  "name": "r3_span_floor_inclusive",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "self.n < SPAN_FLOOR_N",
  "new": "self.n <= SPAN_FLOOR_N"
 },
 {
  "name": "r3_span_floor_value",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "SPAN_FLOOR_N = 0.5",
  "new": "SPAN_FLOOR_N = 0.25"
 },
 {
  "name": "r3_span_change_unreported",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return self._latch() or aged_out",
  "new": "return self._latch()"
 },
 {
  "name": "r3_span_last_day_kept",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "self.first_day = self.last_day = None",
  "new": "self.first_day = None"
 },
 {
  "name": "r3_span_reported_always",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N",
  "new": "aged_out = self.n < SPAN_FLOOR_N"
 },
 {
  "name": "r3v_aged_on_predecay_n",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N",
  "new": "aged_out = self.first_day is not None and n < SPAN_FLOOR_N"
 },
 {
  "name": "r3v_span_floor_on_k",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N",
  "new": "aged_out = self.first_day is not None and self.k < SPAN_FLOOR_N"
 },
 {
  "name": "r3v_unit_gate_return_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "water_setpoint_c=command.space_setpoint if EntryConfig.from_mapping(inp.config).space_setpoint_unit == \"return\" else None,"
 },
 {
  "name": "r3v_unit_gate_flow_only",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "water_setpoint_c=command.space_setpoint if _flow_unit(inp.config) else None,",
  "new": "water_setpoint_c=command.space_setpoint if EntryConfig.from_mapping(inp.config).space_setpoint_unit == \"flow\" else None,"
 },
 {
  "name": "r3v_wrapper_pending_false",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty",
  "new": "rec.dirty = rec.learner.note_pass(when, ctx, False) or rec.dirty"
 },
 {
  "name": "r3v_wrapper_pending_true",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty",
  "new": "rec.dirty = rec.learner.note_pass(when, ctx, True) or rec.dirty"
 },
 {
  "name": "r3v_wrapper_dirty_dropped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty",
  "new": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None)"
 },
 {
  "name": "r3v_heated_margin_strict",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "return ctx.inlet_c - ctx.water_setpoint_c >= HEATED_MARGIN_K",
  "new": "return ctx.inlet_c - ctx.water_setpoint_c > HEATED_MARGIN_K"
 },
 {
  "name": "r3v_heated_falls_to_leg",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        return ctx.inlet_c - ctx.water_setpoint_c >= HEATED_MARGIN_K",
  "new": "        if ctx.inlet_c - ctx.water_setpoint_c >= HEATED_MARGIN_K:\n            return True"
 },
 {
  "name": "r3v_pass_expiry_ignores_pending",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "if not pending and utc_elapsed_seconds(when, ep.at) >= STOP_WINDOW_S:",
  "new": "if utc_elapsed_seconds(when, ep.at) >= STOP_WINDOW_S:"
 },
 {
  "name": "r3v_ageout_keeps_reporting",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        if aged_out:\n            self.first_day = self.last_day = None",
  "new": "        if aged_out:\n            self.last_day = None"
 },
 {
  "name": "r4v_last_write_min",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "last_write_at=max((at for _value, at in held.written.values()), default=None),",
  "new": "last_write_at=min((at for _value, at in held.written.values()), default=None),"
 },
 {
  "name": "r4v_first_day_overwritten",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "self.first_day, self.last_day = self.first_day or day, max(self.last_day or day, day)",
  "new": "self.first_day, self.last_day = day, max(self.last_day or day, day)"
 },
 {
  "name": "r4v_plan_stays_no_both",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "plan_stays=all(step_duty(inp.plan, at) in (target, \"both\")",
  "new": "plan_stays=all(step_duty(inp.plan, at) in (target,)"
 },
 {
  "name": "r4v_checked_every_pass",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "        if not ep.checked:\n            ep.checked = True\n            if explained:",
  "new": "        if True:\n            ep.checked = True\n            if explained:"
 },
 {
  "name": "r4v_supply_ignores_switch",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "supply_on=not _pump_off(inp, held),",
  "new": "supply_on=True,"
 },
 {
  "name": "r4v_tracker_settled_any",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is not False and rec.tracker.pending is None"
 },
 {
  "name": "r5v_span_floor_on_kept_w",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "aged_out = self.first_day is not None and self.n < SPAN_FLOOR_N",
  "new": "aged_out = self.first_day is not None and self.kept_w < SPAN_FLOOR_N"
 },
 {
  "name": "r5v_tracker_settled_not_none",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is not None and rec.tracker.pending is None"
 },
 {
  "name": "r5v_tracker_settled_dropped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.pending is None"
 },
 {
  "name": "r5v_wrapper_pending_inverted",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty",
  "new": "rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is None) or rec.dirty"
 },
 {
  "name": "r5v_pass_judges_before_confirm",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    rec.feed(rec.tracker.confirm(when))\n    rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty\n",
  "new": "    rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty\n    rec.feed(rec.tracker.confirm(when))\n"
 },
 {
  "name": "r5v_write_pending_ignored_when_stopped",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is True and rec.tracker.pending is None or rec.tracker.settled is False"
 },
 {
  "name": "r6v_settled_or_pending",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is True or rec.tracker.pending is None"
 },
 {
  "name": "r6v_running_const_true",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = True"
 },
 {
  "name": "r6v_stopped_with_pending_start_runs",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = (rec.tracker.settled is True) == (rec.tracker.pending is None)"
 },
 {
  "name": "r6v_checked_never_set",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "            ep.checked = True\n",
  "new": "            ep.checked = False\n"
 },
 {
  "name": "r6v_confirm_after_judge_too",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "    rec.feed(rec.tracker.confirm(when))\n    rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty\n",
  "new": "    _edge = rec.tracker.confirm(when)\n    rec.dirty = rec.learner.note_pass(when, ctx, rec.tracker.pending is not None) or rec.dirty\n    rec.feed(_edge)\n"
 },
 {
  "name": "r7v_unsettled_with_pending_runs",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = (rec.tracker.settled is True and rec.tracker.pending is None) or (rec.tracker.settled is None and rec.tracker.pending is not None)"
 },
 {
  "name": "r7v_stopped_with_pending_runs_only",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = (rec.tracker.settled is True and rec.tracker.pending is None) or (rec.tracker.settled is False and rec.tracker.pending is not None)"
 },
 {
  "name": "r7v_pending_start_counts",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = (rec.tracker.settled is True and rec.tracker.pending is None) or (rec.tracker.pending is not None and rec.tracker.pending[0] is True)"
 },
 {
  "name": "r7v_unsettled_no_pending_runs",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is not False and rec.tracker.pending is None"
 },
 {
  "name": "r7v_running_with_pending_runs",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is True"
 },
 {
  "name": "r7v_stopped_no_pending_runs",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "running = rec.tracker.settled is True and rec.tracker.pending is None",
  "new": "running = rec.tracker.settled is not None and rec.tracker.pending is None"
 },
 {
  "name": "r8f_reader_alias_deleted",
  "file": "custom_components/heatpump_optimizer/duty_switch.py",
  "old": "Reader = Callable[[], tuple[float | None, float | None, float | None, bool]]",
  "new": "pass"
 }
]
```
