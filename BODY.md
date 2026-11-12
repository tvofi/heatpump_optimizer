Part A of the duty-switch restart learning, built from Bankaifan's pull request 3420 with thanks: the finding, the install's table and the first implementation are theirs, and their ten commits are this branch's first ten, authorship kept. On a Luxtronik install driven over the smart-home interface, a hot water to space mode write while the compressor runs stops it; nothing priced or observed that. This pull request observes each such switch, estimates per pump and per direction how often it ends in a stop and how long the pump then stays off, persists the estimate and publishes it on the compressor-starts sensor. **Nothing reads the estimate to change a plan or a write**: that is parts B and C of the design approved at `design/R10-DUTY-SWITCH-RESTART-LEARNING` abc575172ca1e6758c58ca8d1f265a2dc7c4fa23, which `docs/design/2026-11-10-duty-switch-restart-learning/design.md` now carries. No issue is closed: the finding arrived as pull request 3420, which the orchestrator closes with thanks after the merge.

## Head

bd262a2ada9a10f9afb0e9b395ac4c0fce0f23af

Round 3, on the head the round-2 review blocked, 84405a2a2c96b6a7476832b5e76edd9f7b96e4a2. Three things lie on top of it: the repair commit 23961a5d8592e3fde3ac82ff4f705983da01fe04, which this body's previous version named and whose tree the pull request's head 3a47c7c156ff1ee55bd0a343023606f7655d2638 holds (`git rev-parse 3a47c7c15^{tree} 23961a5d8^{tree}` prints one id twice); a merge of `origin/main` at a7887485deb7b41995b20a48fab2ae411d887954, which carries pull request 3466; and `killed_by` records of the mutation ledger. Nothing else: `git diff --name-only $(git merge-tree --write-tree a7887485d 23961a5d8 | head -1) HEAD | grep -vc '^tests/mutation_ledger/killed_by/'` prints 0, so no production line, test or harness differs from the clean merge of the two, and this pass changed none. The orchestrator ruled that this line lands on the frozen handoff as its fast-forward (`git merge-base --is-ancestor 23961a5d8 HEAD` exits 0).

The merge base is now a7887485deb7b41995b20a48fab2ae411d887954. `origin/main` is 2cfa3d7d6906632c2a842d898f8fe712a71baeb4 (2026-11-12T01:14Z), and `git merge-tree --write-tree origin/main HEAD` exits 0 against it, so it is not merged again. Every command below compares three-dot, against that merge base. Re-taken at this head, the last run ending 2026-11-12T02:45Z by `date -u`: the section, the spec's mutant run, the diff pass over each production file, the predictor's unpinned-site list with its control, the structural ratchet, the architecture score, golden drift, the scoped gate and the reviewer's probe at both ends. Not re-run: the pin passes themselves (the `ledger:` commits), round 3's ledger-operator spec run, which read a list that is empty here, and round 1's closure re-recording.

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

## Review round 1, answered

`Fix review: blocked 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f mutation-vacuous` (`verdict.md` on `probe/revt-r10-duty-switch-restart-learning-f4a692c8`), two blocks.

1. mutation-vacuous. None of the nineteen is triaged: each is killed by a check that fails under it. The reviewer's whole spec (`ev/reviewer_mutant_spec.json`, its thirty-one entries) is appended to this body's spec and run with it under Mutation proof. What was added to the section, all in `tests/features.py`:
   - The arbiter's void inputs (`_switch_context`): the stop of the section's arbiter run is replayed with one reading changed at the install 30 s after the write: the supply switch off, a mode the plan does not command, disinfection, a boost, the backup heater, the hot-water booster, the fault flag, the feedback loop's moved target. Each voids; with every flag reading off the stop is booked, and with the fault flag on but two hours stale it is booked too (`_lit`'s freshness).
   - The count gates' inputs (`_report_write`), each on both sides of its bound: the room at and 0.1 K under its planned set-point; a plan that leaves the target duty 179 s and 181 s after the write; a return 1.9 K and 2.0 K over the command's set-point after a seven-minute leg (round 3: on the return and the flow unit, see round 2's answer); with no return sensor, a replaced mode record 30 s and 60 s old. The last two pin the departures "the space set-point is the command's" and "source-leg age is the replaced mode record's": reverting either now fails a check (`rv_gate_setpoint`, `rv_gate_source_leg`).
   - The write censor: a hot-water set-point the arbiter writes between the stop and the restart costs the stop its off time (`rv_ctx_last_write`).
   - The pass ages the latches, and saves once: a learner usable in both directions, last aged sixty days before, is switched off by the first arbiter pass, which saves that record once over three passes; one aged a minute stays usable and saves nothing (`rv_pass_decay_dropped`, `rv_persist_stays_dirty`).
   - `rv_published_undecayed`: k and n published 14 days after the stamp are half the stored ones, the tallies unchanged. `rv_detach_keeps_episode`: duty mode off with an episode open leaves none and counts none. `rv_book_no_latch`: the fifth stop switches the latch on at the booking, the fourth does not, and a kept episode taking p under the off bound switches it off.
   The brief also asked for `mutant_run.py --diff` over the whole branch diff with every survivor answered; that pass and its three survivors are under Mutation proof. It forced one production change: `wear.EdgeTracker.note` returned `None` right after arming a pending change, a line no reading could tell from its absence (the `confirm` that follows returns `None` for a change armed at that same instant); the line is deleted.
2. carry-missing. `docs/design/2026-11-10-duty-switch-restart-learning/design.md` gains a closing section, "Part A as built: where the code departs from this note", holding each departure this body lists and what parts B and C need of it; the approved text above it is unchanged. The carry to the two groups' briefs is under Forward-carry; the roster branch is not this seat's to write.

The verdict's factory-reset finding is answered under Forward-carry.

## Review round 2, answered

`Fix review: blocked 84405a2a2c96b6a7476832b5e76edd9f7b96e4a2 mutation-vacuous` (`verdict.md` and `ev/` on `probe/rev-3461-edf76a05` at e4e4c6cd5783872a0206bf9d7c01c54fcfa37108), two blocks and six findings. No finder harness exists for this group; the instruments at both ends are the reviewer's own, `ev/reviewer_mutant_spec_round2.json` and `ev/reviewer_probe.py` of that ref.

1. mutation-vacuous. The reviewer's twenty-five entries are appended to this body's spec and run with it under Mutation proof. Four are killed by checks added to the section, each driven through `pump_arbiter.apply` on both sides; the fifth lost its site:
   - `r2_ctx_defrost_interval`: an install with no defrost entity whose interval flag (`ArbiterInputs.defrosting`) reads True from the start opens nothing; the flag turning True 30 s after the write voids the stop; the flag reading False books it.
   - `r2_ctx_economy_dropped`: the same stop on an install in Economy books, as in Auto; in Comfort no single duty is commanded and nothing is booked.
   - `r2_gate_dhw_demand`: a space to hot water write (heating to 00:08, then hot water, the compressor running on) books a kept episode with the tank 0.1 K under its set-point and opens nothing with the tank at it or unread.
   - `r2_gate_plan_now_only`: a write the plan's current step does not hold is reachable through a system-identification experiment, which commands heating whatever the plan books (`_planned_duty`). With the plan on hot water at the write and on heating before the window's end nothing opens; with the plan on heating at the write the same write books the stop. A block on a stale plan, the other route read, is released by `boost.release_blocked` before the write and reaches no single duty.
   - `r2_signal_always`: not triaged, removed. `DutySwitchLearner.note_pass` no longer takes the "signal known" argument: an open episode with an unknown settled class is unreachable, as the verdict reads it, and a lost signal is `edge`'s to void (the section's "signal lost" cause and the arbiter run with an unavailable frequency). The pure check that passed the argument as False went with it. This body's `void_no_signal_pass` mutated the deleted line and is dropped from the spec.
2. class-open, `_heated` over an indoor-unit set-point. Fixed at the arbiter's edge, where the unit is known: `_report_write` hands the command's space set-point on only where `_flow_unit` says it is a water temperature, and `SwitchContext` names the field `water_setpoint_c`. `_heated` compares the inlet with it when both are known and otherwise decides by the source leg's age, the rule it already had for an install with no inlet reading. Alternatives: comparing the inlet with the written water record on an indoor install lost, because an indoor install writes no water set-point at all; refusing every indoor-unit switch lost, because it would leave the default unit with no evidence. Driven on all three units through the arbiter: on return and on flow a return 1.9 K over the command's set-point after a seven-minute leg opens nothing and 2.0 K books; on indoor a return 9 K over the room's set-point with a 30 s leg opens nothing (the verdict's instance, booked at the blocked head), the same return with a 60 s leg books, and a return 0.5 K over the room's after a seven-minute leg books, so the room number is not compared at all. Mutants `r3_unit_gate_dropped`, `r3_unit_gate_inverted`, `r3_heated_no_setpoint_refuses`. The class's rule, `git grep -n "water_setpoint_c" -- 'custom_components/heatpump_optimizer/*.py'`, prints the field, its two reads in `_heated` and its one writer, the hand-off line in `_report_write`, closed in this diff; no other reading of the space set-point reaches the learner.
3. The span gate. Fixed in this branch: under `SPAN_FLOOR_N` (0.5, one episode a half-life old; a named constant, not a measurement) of decayed weight `Direction.decay` forgets the first and last day with the evidence, and reports that as a change of the stored record, saved once. Alternative: the exact span of the episodes still above a weight needs every episode's day stored, a schema the estimate does not otherwise need; it lost to one comparison on the count already kept. The reviewer's probe at both ends is under Figures. Section check "the span ages with the evidence", with its null control (a first stop exactly one half-life old still anchors the span, and one a day old). Mutants `r3_span_never_ages`, `r3_span_floor_inclusive`, `r3_span_floor_value`, `r3_span_change_unreported`, `r3_span_last_day_kept`, `r3_span_reported_always`.

The other findings, in the verdict's order:
- Five real episodes never reach n of 5: not changed here, it is the meaning of a constant for the part that first reads `usable`; the check that read as an install's fifth stop is renamed to what it pins ("a stop taking n from 4 to 5"). Under Forward-carry.
- The published k and n change with no observation: not changed here; under Forward-carry.
- The planner-price carry's "controls as in the item above", and the PR-B brief against its carry: the roster's text, not this seat's to write; the two controls are restated in full in this body's Forward-carry line for that group.
- No finder harness: stands as the verdict dismissed it.

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

**The spec** (`--spec`, at the end of this body): round 1's entries, then the round-1 reviewer's, then the round-2 reviewer's (`r2_`), then this round's own (`r3_`). Entries whose `old` text this round renamed (`space_setpoint_c` to `water_setpoint_c`, the hand-off line in `_report_write`) carry the new text and the same edit; `void_no_signal_pass` and `r2_signal_always` are dropped with the argument they mutated. The count is the `KILLED` lines below.

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
```

**The branch diff** (`--diff origin/main...HEAD --report-only`, run once per production file with `--path`): three survivors, each an equivalent mutant.

```
SURVIVED custom_components/heatpump_optimizer/duty_switch.py:82 CONST_SWAP  STORE_VERSION = 2
SURVIVED custom_components/heatpump_optimizer/duty_switch.py:187 CMP_BOUND  if self.decayed_at is None or utc_elapsed_seconds(when, self.decayed_at) >= 0.0:
SURVIVED custom_components/heatpump_optimizer/pump_arbiter.py:1780 CONST_SWAP  return resolve_reading(None, sensor, states.get, 1.0, 0.0)[0], None, None, True
```

- `duty_switch.py` `STORE_VERSION = 2`: the version is what Home Assistant's `Store` stamps on the file and compares with a stored payload's own; no migration exists for either value and `DutySwitchLearner.from_record` never reads it. The arbiter's own `_STORE_VERSION` carries the same verdict in the ledger. Record: `tests/mutation_ledger/survivor_triage/duty_switch.py/@module.CONST.43e0a892.json`.
- `duty_switch.py` `Direction.decay`, `> 0.0` to `>= 0.0`: the two differ only when the pass is at the stamp's own instant, and the guarded statement then assigns the stamp the instant it holds. The other side of the bound, a stamp half a second old, is driven ("every aging moves the stamp"). Record: `tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.decay.CMP_BOUND.225d3f33.json`.
- `pump_arbiter.py` `_running_signal`, `resolve_reading(None, sensor, states.get, 1.0, 0.0)[0]`: the fourth and fifth arguments are the range `resolve_reading` hands back as elements 1 and 2 of its tuple when no number entity is given; the reader keeps element 0 alone. No ledger record: `tests/mutation_table.py` generates no site for this operator on that line, and a disposition naming no site is refused.

The first diff pass at this round's first commit printed forty-three survivors. One was the `wear.py` return deleted above; the others are each killed by a check added since (the learner's return values, the window's and the censor's bounds, the unstated gates, the median, the published rounding, the stored record's bounds against `store.py`'s registered domain, a failed read and a failed save, the attach and detach guards).

**The ledger's own operators.** `tests / mutation` mutates with `tests/mutation_table.py`'s operators, which `--diff` does not carry (`BOOLOP`, `CLAMP_DROP`, `CONST`). At this head every site the diff adds is pinned by a `killed_by` record that module's own driver wrote: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --shard K/N --jobs 4 --budget-minutes M`, one pass per `ledger: pin` commit of `git log 23961a5d8..HEAD`, each on the committed head it extended and each, by the seats that ran them, ending `PIN KILLED: <n> pinned, 0 left unpinned` beside `baseline tests/features.py: rc=0 failed=0` and a surviving `NULL_COMMENT`. The passes were not re-run for this body; what is re-taken is their result, the predictor's empty list under Unpinned sites, with its control. The repair commit's edits left pins naming no site; the two `ledger: drop` commits delete those and the edited lines are pinned afresh, which the absence of a `STALE PIN` line reads.

Round 3's own run at 23961a5d8592e3fde3ac82ff4f705983da01fe04, before any pin, and not repeatable at this head because the list it reads is empty: for each site `tools/pr/ci_predict.py --base origin/main --only mutation` listed as added and unpinned, that module's own replacement line was written into a spec and run as above: `SURVIVED NULL`, every other line `KILLED`, no other survivor. The first such run left `duty_switch.py` `Direction.book`'s `CLAMP_DROP` alive (the last day no longer moved on); a check now kills it. The spec was built by:

```python
import json, re, sys
from pathlib import Path
sys.path.insert(0, "tests")
import mutation_table as m
want, spec = {}, []
for line in Path(sys.argv[1]).read_text().splitlines():  # ci_predict's output
    hit = re.match(r"PREDICT tests / mutation ADDED UNPINNED (\S+):(\d+) (\w+)", line)
    if hit:
        want.setdefault(hit.group(1), set()).add((int(hit.group(2)), hit.group(3)))
for rel, keys in want.items():
    src = Path(rel).read_text()
    lines, seen = src.split("\n"), {}
    for s in m.anchor_sites(src, list(m.candidates(Path(rel).resolve(), m.RATCHETED, src))):
        if (s["line"], s["kind"]) in keys:
            i = j = s["line"] - 1
            while src.count("\n".join(lines[j:i + 1])) != 1:
                j -= 1
            n = seen[s["line"], s["kind"]] = seen.get((s["line"], s["kind"]), 0) + 1
            spec.append({"name": f"{Path(rel).name}:{s['line']}:{s['kind']}#{n}", "file": rel,
                         "old": "\n".join(lines[j:i + 1]), "new": "\n".join([*lines[j:i], s["new"]])})
print(json.dumps(spec, indent=1))
```

## Null control

- `SURVIVED NULL` above: the unmutated tree passes the section.
- An install where no switch stops the compressor, one where it does, and a flat-price day: the split order and every service call are equal between an empty learner and one latched usable in both directions (three checks named "null control" in the section). They hold by construction, and a fourth check pins the construction: only `pump_arbiter.py` and `sensor.py` name `duty_switch`, through eight names none of which reads the estimate.
- Both ends of the learner's range: an empty learner publishes no key and changes nothing; one saturated at p = 1 changes nothing either.
- `tests/env_drift.py --all` against the merge base reports no unclaimed drift and no stale fixture; neither claim file is touched (`git diff origin/main...HEAD --stat -- tests/golden/` prints nothing).
- Round 3's: the indoor-unit rows beside the same return with a full leg; the interval defrost beside the flag reading False; Economy and Auto beside Comfort; the tank at its set-point beside 0.1 K under; the off-plan write beside the same write on a step that holds it; the aged span beside a first stop one half-life old. Both ends of the span rule's range: an empty direction has no day to forget (the section reads `Direction().span_days` as 0), and one saturated keeps its days (the latch row at n 40 switches on, which needs its two-day span).
- Each check added in round 2 carries its own: every void reading beside the same install with the flags off; every count gate beside the step the other side of its bound; the censoring write beside the same install without it; the aged learner beside one aged a minute.

## Figures

- Section checks: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`
- Mutants killed, the null and the diff pass's survivors: the two `mutant_run.py` runs under Mutation proof, at this head. The unpinned-site list: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation | grep -c -e 'ADDED UNPINNED' -e 'STALE PIN'` prints 0 at this head and 105 at 6dac686e24e88e6e2df5c0ec3dbf432278777279 (a detached worktree of it), the merge of main before the repair commit and before any pin.
- Ledger records this line adds over the clean merge of main and the repair commit: `git diff --name-status $(git merge-tree --write-tree a7887485d 23961a5d8 | head -1) HEAD | cut -c1 | sort | uniq -c` prints one line, `107 A`; the same list through `grep -vc '^A.tests/mutation_ledger/killed_by/'` prints 0.
- Malformed payloads driven through the loader: the count in the check name the section prints ("malformed or out-of-bounds payloads").
- Golden drift: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/env_drift.py --all $(git merge-base origin/main HEAD)`
- `tests/features.py` at the head: exits 0, its last line the script's own all-passed count; the `combi_type_branch` census that was its one failing check at 23961a5d8592e3fde3ac82ff4f705983da01fe04 passes with pull request 3466 merged. Control: the previous version of this body, at that head, where the same command printed that check as its only `FAIL` line. `PYTHONPATH=tests/hastub python3 tests/features.py`
- Scoped gate, run at this head: `MODE: SCOPED`, exit 0, every script it ran green. Control: at 23961a5d8592e3fde3ac82ff4f705983da01fe04 the same command exited non-zero on `tests/features.py` alone. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`
- Gate mode: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- Structural ratchet: `python3 tests/structure.py`
- Architecture score: `python3 -I tools/audit/archscore/score.py --diff "$(git merge-base origin/main HEAD)" HEAD`
- Closures: the scripts whose recorded closure held `pump_arbiter.py`, `sensor.py` or `store.py` were re-recorded on Linux with `./tests/derive_closures.sh --scripts-from <list>` and merged with `python3 tests/closure.py merge --in-dir <dir> --partial --allow-failures`; `tests/entities.py` exited 1 while recorded only on checks that read the not-yet-merged table, and passes at the head.
- The reviewer's probe at both ends: `$EXPORT/ev/reviewer_probe.py` (sha1 95dc3977d920f6cda166f278c67d85dbdcb085a8), `$EXPORT` being a `git archive` export of `probe/rev-3461-edf76a05` at e4e4c6cd5783872a0206bf9d7c01c54fcfa37108, run from the root of the tree it measures; it is the reviewer's evidence and not in this tree. At 84405a2a2c96b6a7476832b5e76edd9f7b96e4a2 (a `git archive` export): `span_probe6 ... span_days=366 usable=True`, its control `span_days=1 usable=False`; `heated_room_unit ... heated=True`, its control `heated=False`. At this head, with the probe's two `space_setpoint_c=` arguments renamed (`space_setpoint_c=21.0` becomes `water_setpoint_c=None`, which is what the arbiter now hands over for a room-unit set-point; `space_setpoint_c=32.0` becomes `water_setpoint_c=32.0`): `span_probe6 ... span_days=1 usable=False`, equal to its control; `heated_room_unit ... heated=False`, equal to its control. The probe's `fifth_episode` and `attr_churn` lines read the same at both ends: neither is changed here.
- The heated gate at the install, per unit: the rows of `_ds_gates` and `_ds_gates_open` in the section, which the two gate checks print on failure. The water set-point the arbiter commands on the fixture is its heating ceiling, read from the section's own service calls, so the bound is that ceiling plus `HEATED_MARGIN_K`.
- Seams of the class (fixer step 8), `git grep -n -E "select_option|await _command\(" -- 'custom_components/heatpump_optimizer/*.py'`: the one mode write, in `_write`, closed in this diff by the report there; its callers `_arbitrate` and `release`, covered through it (`release` detaches first).

## Architecture score

- coord_footprint: rises by the registry's three entry points that take the coordinator (`duty_switch.record_for`, `detach`, `starts_attributes`) and one call line each in `_write`, `_arbitrate`, `_listen` and `release_listeners`. A first cut also raised `duplication_copies`, `literal_clone_copies` and `computed_attr_access`; those were paid (a shared hand-off method, two named domains, named fields) and every function below the registry now takes the pump's record instead of the coordinator. What remains is the new feature's own entry, not a duplicate of anything.

## Unpinned sites

None at this head: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` prints no `ADDED UNPINNED` and no `STALE PIN` line. Every site the previous version of this section listed as left to `mutation-autofix` now carries a `killed_by` record this branch commits, written by the lane's own driver (Mutation proof, "The ledger's own operators"); the two equivalent sites carry a `survivor_triage` record, as before. Control: the same command at 6dac686e24e88e6e2df5c0ec3dbf432278777279, the merge of main before any pin, prints `ADDED UNPINNED` lines (count under Figures).

## Red checks

- `tests / mutation`: red on pull request 3461 at 3a47c7c156ff1ee55bd0a343023606f7655d2638, as `tools/pr/prepr.sh` step 6d predicted: that head adds sites no record pins. Answered at this head by the pins: the predictor lists no unpinned and no stale site here (Unpinned sites). Cheaper detector: step 6d itself, which named every site before the push at no cost beyond the self-check; the kill runs that write a pin are the lane's own and nothing cheaper than them can pin a site.
- `gate`: red at the same head; it is the aggregate of the required checks and failed on `tests / mutation` alone, the one required check red there. Cheaper detector: the line above.
- `tests / fast (3.14)`: red at the head the round-2 review read, 84405a2a2c96b6a7476832b5e76edd9f7b96e4a2, on `tests/features.py`'s `combi_type_branch` census, which was red on `origin/main` itself on six lines none of which this diff adds. Green on the pull request since pull request 3466 reached main, and `tests/features.py` passes at this head, which merges it (Figures). Cheaper detector: none on this branch; the script that fails is the detector, and it ran on main.

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
  "old": "supply_on=not _pump_off(inp),",
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
  "old": "    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))\n    if mode != DUTY_CONTROL or _pump_off(inp):\n        return",
  "new": "    if mode != DUTY_CONTROL or _pump_off(inp):\n        return\n    await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))"
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
 }
]
```
