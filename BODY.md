The owner's request on #2261: an optional delivered-heat energy meter (`heat_pump_heat_energy_entity`, "Heat pump heat energy meter", a `total_increasing` kWh sensor on the options' Power and energy group), read per span, with the heat split between space heating and hot water by the pump's mode entity. Built to the approved design, the architect note `dev/programme/designs/R10-HEAT-METER.md` on `design/R10-HEAT-METER` at `21f4fbfe9`, approved by `design-verdict/R10-HEAT-METER` `ad376684f` ("Design review: approve 21f4fbfe9"). An install without the key reads what it read before: every coordinator golden capture is byte-identical to the merge base.

Part of #2261

**One reader module, the coordinator calls it.** `heat_energy.py` (new, free of Home Assistant) owns the counter, the span and the mode dwell. `HeatEnergyMeter.observe_counters` reads the heat counter (and the electric energy counter beside it) once a cycle and closes a span on elapsed time, at the first read past `close_after_h = max(MIN, MAX - cadence - 0.05)` inside the interval learners' `HOUSE_LOSS_MIN/MAX_SAMPLE_HOURS` bounds (review point A of the design). A span past the maximum is refused (`span_too_long`), a counter that went backwards is a reset (`counter_reset`), one that jumped past 1.5 x the thermal nameplate over the span is a rollover (`counter_rollover`), and a counter too coarse for the heat expected in the span (step / expected > `HEAT_RESOLUTION_EPS`) is refused (`counter_resolution`); each refusal re-baselines, so the next span reads true. The electric delta counts only when it was read at the same instants (aligned on the read instant, never on `last_updated`: dr1-lag-idle); otherwise the span's COP is refused as `unaligned_meters`.

**Which heat source wins.** `flow_meter.read_heat_output_kw` stays the one answer, ranking a configured counter first, then #2753's thermal power entity, then the flow meter, and a configured source answers alone with no fallback: with the counter configured a cycle reads `None` there (the counter answers per span), so neither the thermal reading nor the flow meter is consulted. `probe_install(...).measured_heat` is true for either heat key.

**The consumers, on a counter install.**
1. *COP.* The per-cycle fold runs its gates and stops at `COP_REFUSED_SPAN_OPEN` (`span_open`), so a cycle that passed every gate leaves the span clean for COP; at the close `_async_learn_heat_span` folds heat over electricity on the two deltas through `_fold_cop_evidence` (the fold's tail, split out of `_fold_measured_cop` so a cycle and a span share it), judged on the span's duty.
2. *House heat-loss and lower-floor learners.* At the close the span replays from its opening state over its plan (`settle`), each learner on its own per-cycle gates ANDed over the span (review point B): one frozen, boosted or ventilation cycle refuses that learner's span and only its own. The per-cycle path still feeds the ventilation detector every cycle.
3. *The basis.* `HEAT_LOSS_BASES` gains `measured_heat`, earned at the first fold that replays a measured heat (`_async_earn_heat_basis`): the void path re-anchors the earlier fit through R10-RATIO-ANCHOR's mechanism (`_reanchor_house_heat_loss_scale`, `heat_loss_basis_voids`) before that fold, and the basis is saved; a meter the replay never uses keeps the scale. `store.py` changes the `house_heat_loss_basis` unread string only (no version bump, no migration, the orchestrator's ruling in the note).

**The mode split.** `pump_signals.read` carries a live mode's `last_changed` (`mode_changed_at`); `ModeDwell` places the split there. Only a live heat or hot-water mode is observed; a combination mode, a last-good reading (its `last_changed` is the stale state's own: dr1-last-good), an unrecognised one or an excursion the reads did not see is unobserved, and the interval falls back to the plan's split, which reproduces #2753's figure exactly. `heat_energy.attribution` is the one owner of that choice, and every site that split by the plan asks it: `_interval_measured_heat_kw` (and so #2753's replay of the thermal reading, and `replay_freeze`'s lift, which it is handed), `_cop_reference_curve`, the energy ledger (`_accumulate_energy`) and the diagnosis triple (`_settle_interval_diag`). A point reading (thermal power) is never time-split (review point C): an interval with hot water in it gives no space figure.

**Design deviations and rulings, each stated.**
- *`HEAT_RESOLUTION_EPS = 1.0`, not the design's 0.5* (mandate 6329234399 ruling 1; the design's own dr3-eps-at-span carry asked for the re-measure). At the real span (a 30 min cadence closes one-hour spans) 0.5 refuses every span of an integer-kWh counter at 1.5 kW, which 1.0 reads unbiased; the `EPS` lines of the harness below print both, and two checks pin it (`## Mutation proof`, row Q).
- *The mode entity is optional,* overruling the owner's brief ("The mode entity is REQUIRED when the heat meter is configured, with a refusal if it is missing"). The design's revision 1 records the orchestrator's ruling under mandate 6329234399 ("The mode entity becomes optional and the refusal goes"), approved with the note by `ad376684f`. Without it, or in a combination mode, the split is the plan's, and an interval that heated the tank is not read as space heating.
- *D15 lead L6, accepted* (ruling 2): `INPUT_ON_CHANGE_MAX_AGE_MINUTES[CONF_HOUSE_POWER_ENTITY] = math.inf`. At the merge base a whole-house meter reporting only on change, holding 0 W while PV covers the house, read stale after 30 min though healthy; the PV-hold case is pinned.
- *D15 lead L9, instrumented, verification carried* (ruling 3): each weekly learner snapshot now records `unhealthy_input`, the first reason `_inputs_unhealthy` gave on that day (the rule over indoor, outdoor and power that marks the day; the house meter is not one of its inputs), and `None` on a healthy day. Outdoor's 180 min limit is unchanged. Which input marked the owner's five snapshots needs the next live bundle; that read is carried to the live-diagnosis group (`## Forward-carry`).
- *The new key's age:* `INPUT_MAX_AGE_MINUTES` 180 min as the energy meter's, and `INPUT_ON_CHANGE_MAX_AGE_MINUTES` `math.inf` (a counter holds while the pump idles), so it is outside `_r10st_same`'s equal-keys declaration, which drops `CONF_HOUSE_POWER_ENTITY` for L6. A dead counter re-reports first in its test (the INPUT-STALENESS precondition).
- *SAV attribution residue (carry 4):* dismissed per the design: the observed split fixes single-duty intervals; under a combination selector one meter cannot observe the split, so the plan split and its docstrings stay.
- *"Clamp means reset" (carries 9, 13):* kept, and re-measured at the merge base: the void path zeroes both learners' samples before `house_loss_confidence`, so `reanchor_heat_loss` runs at (0, 0), where both clamp branches are skipped (harness `CLAMP` lines).

**Alternatives considered (fixer step 17).** A cycle-count span and a fixed-K close were refused by the design against the learners' strict `dt_h > MAX` bound. Per-cycle time-splitting a point reading was refused (review point C). A coordinator attribute for the meter was avoided: `heat_energy.meter_of` keeps it in a `WeakKeyDictionary` side table (`boost.py`'s pattern), and the coordinator's day-health flag moved onto the snapshot ring, so `coordinator_attrs` and `coordinator_multiassigned_attrs` each fell by one.

## Head

`4f191ac0f69cef0777d36a37f228ca751a198eec`, merge base `a441d2e15986033840c226eb39c4833c177f4dc8` (#2753's merge, `git merge-base origin/main HEAD`). origin/main's tip `e0ffb1213` at 2026-10-26 06:53 UTC; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so no merge was made (fixer.md step 6).

## Mutation proof

The in-tree table `python3 dev/audit/harnesses/r10_heat_meter_mutants.py -j 3`, run from the committed tree at `e11b67b61` (each mutant one exact replacement in its own `git archive` copy, `tests/features.py` in full; production and tests are unchanged to this head: `git diff --quiet e11b67b61 HEAD -- custom_components tests/features.py && echo UNCHANGED` printed UNCHANGED). The design's ten targets (C1 to I), the precedence check mirroring #2753's M1 (P), and the carries' three (D, L6, L9). Two deviations from a clean table, stated. First, the null row (a comment-only edit) is not green: it fails one check, #363's `recorded_at`, which fails in every `git archive` copy because the copy has no git history (fixer.md step 2). The table therefore kills a mutant on the checks it fails beyond that one, and prints those checks by name. Second, the table covers the design's targets and the carries' rows, 13 mutants with 0 survivors. It does not cover the diff's 112 sites; those are under `## Unpinned sites`:

```
NULL      N0 null control (a comment): 1 of 4460 FEATURE CHECKS FAILED; 0 beyond the null
KILLED    C1 span closes at the minimum, not past close_after_h: 8 of 4460 FEATURE CHECKS FAILED; 7 beyond the null
      FAIL a counter span closes on elapsed time, inside the learners' sample bounds, under a drifting cadence and one event-driven cycle (null control: no drift
      FAIL a counter span folds COP as heat over electricity, exactly the plant's on a known-COP plant; inside the span a cycle folds nothing
      FAIL an electric counter not read at the close leaves the span unaligned (None), never a delta over other instants
      FAIL an integer-kWh counter is refused at 0.6 kW, reads 1.5 kW unbiased over its spans (null control: 3.0 kW reads 3.0)
KILLED    C2 a span past the maximum is not refused: 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a counter span closes on elapsed time, inside the learners' sample bounds, under a drifting cadence and one event-driven cycle (null control: no drift
KILLED    Q resolution bound dropped: 3 of 4460 FEATURE CHECKS FAILED; 2 beyond the null
      FAIL an integer-kWh counter is refused at 0.6 kW, reads 1.5 kW unbiased over its spans (null control: 3.0 kW reads 3.0)
      FAIL null control for the resolution bound: at the design's 0.5 the one-hour span refuses every integer-kWh span at 1.5 kW, which 1.0 reads
KILLED    R reset branch dropped: 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a counter reset and a rollover are refused, and the next span reads true (null control: the same plant without either)
KILLED    P counter-first precedence dropped: 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a configured heat counter outranks the thermal power entity and the flow meter, and a cycle reads no heat from it (null control: the thermal entity al
KILLED    O observed test inverted: 5 of 4460 FEATURE CHECKS FAILED; 4 beyond the null
      FAIL a single-duty step the arbiter wrote (owned) counts as observed
      FAIL heat then hot water inside one interval splits at the mode's last_changed (10 of 30 minutes space), and an integrated heat takes that share
      FAIL the ledger and the diagnosis triple split by the same observed dwell (one third space) where the plan said all space
      FAIL the same interval on a point reading (thermal power) gives no space figure, not a half (null control: a space-only interval gives the reading)
KILLED    L split at the read, not at last_changed: 4 of 4460 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a mode that left and came back between two reads is an unseen excursion: the interval is unobserved and splits by the plan
      FAIL heat then hot water inside one interval splits at the mode's last_changed (10 of 30 minutes space), and an integrated heat takes that share
      FAIL the ledger and the diagnosis triple split by the same observed dwell (one third space) where the plan said all space
KILLED    E earned basis never set: 3 of 4460 FEATURE CHECKS FAILED; 2 beyond the null
      FAIL the earned basis is saved and restored with the meter still configured; with it removed the basis is the configured one and the fit is kept, not voide
      FAIL the first fold that replays a measured heat earns the measured_heat basis, voiding the earlier fit first; the next fold keeps it (null controls: no he
KILLED    A span_clean AND dropped (last cycle wins): 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL one gated middle cycle refuses that learner's span and only its own; the span replays from its opening state over its plan
KILLED    I integrated branch ignored: 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL the same interval on a point reading (thermal power) gives no space figure, not a half (null control: a space-only interval gives the reading)
KILLED    D the heat counter's on-change decision dropped: 4 of 4460 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a quiet heat counter holding its value reads fresh; one that re-reported and then fell silent past 180 min is stale; MWh reads as kWh
      FAIL all 28 age-limited keys: a quiet on-change source is stale only on a key named equal; a silent polling source is stale on every key, remembered past a
      FAIL every age-limited key declares its on-change limit, no lower than its polling one, and each kept equal is named with its reason
KILLED    L6 the house meter's on-change limit back to 30 min: 4 of 4460 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a house meter holding 0 W for 4 h on change only reads 0 kW (PV covering the house); one that re-reported and then fell silent 40 min is stale
      FAIL all 28 age-limited keys: a quiet on-change source is stale only on a key named equal; a silent polling source is stale on every key, remembered past a
      FAIL every age-limited key declares its on-change limit, no lower than its polling one, and each kept equal is named with its reason
KILLED    L9 the snapshot ignores the named input: 2 of 4460 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a snapshot on an unhealthy day names the input that made it so, and a healthy day names none (D15 L9)
0 survivor(s) of 13 mutant(s); the null fails ['and the path that proceeds still stamps a resolvable recorded_at (#363)']
```

Base-failing for the carried leads: L6's mutant is the merge base's value (house meter on-change 30 min), D drops the counter's on-change decision (the INPUT-STALENESS declaration check refuses it, as its carry's control says), and L9's restores the base's unnamed snapshot. The rest of the section's checks import `heatpump_optimizer.heat_energy`, which the base does not have.

## Null control

The unmodified tree (merge base `a441d2e15`) has no counter key: the harness feeds both trees the same cycling plant, and the base reads the point thermal meter on every arm, so its `counter`, `reset` and `integer` arms print the `point` arm's scales, bit for bit. The head's `point` and `commanded` arms (no counter configured) are bitwise identical to the base's, the null for an install without the key; and every coordinator golden capture (`coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`) is byte-identical to the merge base, as the design predicted (each publishes mode `"Unknown"`, so attribution takes the plan arm). Inside the suite each new check carries its own null (named in each check's text): heat equal to the model's COP times the electricity holds `cop_scale` at 1.0; the reset and rollover plants against the same plant unplanted; 3.0 kW on an integer counter reads exact; a space-only interval on a point reading gives the reading; no heat reading and a flow-meter estimate keep their basis; a healthy day names no input.

## Figures

All at head `4f191ac0f69cef0777d36a37f228ca751a198eec` against merge base `a441d2e15986033840c226eb39c4833c177f4dc8` (`git merge-base origin/main HEAD`; origin/main's tip `e0ffb1213` at 2026-10-26 06:53 UTC, which `git merge-tree --write-tree origin/main HEAD` merges with no conflict, so no merge was made).

- `python3 dev/audit/harnesses/r10_heat_meter.py a441d2e15986033840c226eb39c4833c177f4dc8` (sha1 `1e8620b9f7d7d0611800027466e00fd541a25eac`) -- the #2753 plant cycling at 40 % duty, 9 kW while on, 600 refreshes of 30 min at each of 7 outdoor points. Head: `counter` spread 0.0000, every scale within 2e-5 of `TRUE_K` 0.9, 2093 span folds; `reset` (the heat counter planted back to zero every 37 refreshes) spread 0.0000 at 0.90002 on 1981 folds, 16 resets x 7 points refused; `integer` (whole-kWh counter) spread 0.0009, 0.8991 to 0.90006. Base: all three equal the `point` arm, the defect: spread 0.4566, `cop_scale` on its `COP_SCALE_MAX` 1.6 from -15 to -2 degC and 1.143 to 1.356 above (a point reading of a cycling pump is its full output or nothing, and the zero reads are refused, so the fold sees only the on instants). Comparisons printed by the commands themselves: `diff <(head point line) <(base point line) && echo point-IDENTICAL` printed point-IDENTICAL, and likewise commanded-IDENTICAL and CLAMP-IDENTICAL; `diff <(base counter scales) <(base point scales) && echo base-counter-EQUALS-POINT` printed base-counter-EQUALS-POINT, and likewise for reset and integer. Both ends of the input range: `commanded` is the zero-evidence install (no heat reading), `point` the clamp (it sits on `COP_SCALE_MAX`).
- The same command's `CLAMP` lines (carries 9 and 13, at both trees): the void path's confidence is (0.0, 0.0), and over 45 stored (scale, ratio, nameplate move) cases from 0.05 to 20x `reanchor_heat_loss` resets 0 and returns the configuration (max |value - 1| = 0.0); its null, the same grid at a converged learner's confidence (1.0, 1.0), resets 37. Identical at both trees (CLAMP-IDENTICAL above), so "clamp means reset" stands unchanged and the earned basis cannot reach a clamp branch.
- The same command's `EPS` lines (dr3-eps-at-span, head only): an integer-kWh counter on a 30 min cadence closes 199 one-hour spans in 400 refreshes. At `HEAT_RESOLUTION_EPS` 1.0: 0.6 kW keeps 0 of 199; 1.5 kW keeps 199, mean 1.4975 kW, sd 0.5; 2.2 kW keeps 199, mean 2.196, sd 0.397; 3.0 kW keeps 199, mean 3.0, sd 0.0. At the design's 0.5: 1.5 kW keeps 0 of 199, the rest as at 1.0.
- `python3 dev/audit/harnesses/r10_heat_meter_mutants.py -j 3` (sha1 `65392a33516e80681c760abf293b64e5d4f2aa9b`) at `e11b67b61` -- the table in `## Mutation proof`; production and tests unchanged since (`git diff --quiet e11b67b61 HEAD -- custom_components tests && echo PROD-AND-TESTS-UNCHANGED` printed PROD-AND-TESTS-UNCHANGED).
- `PYTHONPATH=tests/hastub python3 tests/features.py` -- ALL 4460 FEATURE CHECKS PASSED (in the scoped gate below).
- `GOLDEN_MODE=drift GOLDEN_REF=a441d2e15986033840c226eb39c4833c177f4dc8 PYTHONPATH=tests/hastub python3 tests/golden.py` -- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against a441d2e15986033840c226eb39c4833c177f4dc8` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. The one moved fixture is the float-free `config_flow` (the new field: 3 leaves added, no value moved), re-recorded with `--record --only config_flow` and claimed in `tests/golden/claimed_drift.txt`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -- `4 of 2445 ENTITY CHECKS FAILED`: four heartbeat positive-control checks (`hb:positive_control survives one hung py-spy sample ...`, `and a try whose sample misses the spin ...`, `the control rests between tries ...`, `the control survives two hung samples ...`) that fail identically at the merge base on this seat (`tests/entities.py` run in a detached worktree of `a441d2e15`: `4 of 2445 ENTITY CHECKS FAILED`, those four), so they are this macOS seat's py-spy timing, not this diff.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`. Recorded down, no row raised (commit `1838090da`): `coordinator_attrs` 143 -> 142 and `coordinator_multiassigned_attrs` 110 -> 109 (the day-health flag moved onto the snapshot ring), `max_class_loc` 8241 -> 8186 and `seam_cut_total` 424 -> 423 (spent prose deleted from the COP fold, the COP reference curve, the house learner and the commanded split; the span read moved into `heat_energy.span_heat`); the payments for the ratchet's zero-headroom rows were made in code (`_replay_gate` and `_replay_fabric` shared by both learners instead of a clone, the snapshot ring's `observe_health`/`start_day`).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -- `ALL 112 HARNESS HEADER CHECKS PASSED` (the D5 and D6 round harnesses re-measured: 202 and 235 option fields, 83 modules).
- `python3 tests/closure.py select --diff a441d2e15986033840c226eb39c4833c177f4dc8 --workdir <tmp>` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out.` (it read `MODE: FULL` before the closures below recorded `heat_energy.py`).
- `env -u BASH_ENV PYTHONPATH=tests/hastub GATE_SCOPE=auto GATE_SCOPE_BASE=a441d2e15986033840c226eb39c4833c177f4dc8 GOLDEN_MODE=drift GOLDEN_REF=a441d2e15986033840c226eb39c4833c177f4dc8 bash tests/run.sh` at `df1f70675` (before the `arch_score_head.py` closure and the deployment-shape note, `4f191ac0f`, which `tests/entities.py` above re-took) -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`, `4 TEST SCRIPT(S) FAILED`; among its lines ALL 4460 FEATURE CHECKS PASSED, STRUCTURE RATCHET PASSED, NO UNCLAIMED DRIFT: 56 scenario(s) checked, ALL 112 HARNESS HEADER CHECKS PASSED. The four: `tests/entities.py` (repaired in `4f191ac0f` but for the four heartbeat controls above); `tests/optimality.py` `1 of 84` (`one|summer_negative|shoulder: a recorded claim still has a gap (not stale)`), `tests/stress.py` `1 of 113` (`shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`) and `node tests/card.mjs` (a V8 heap out-of-memory after 1269 ok lines). Each of the three fails the same way at the merge base on this seat, run in a detached worktree of `a441d2e15`: optimality `1 of 84` on that check, stress `1 of 113` on that check with the same 4.67 vs 3.96, and card.mjs the same heap OOM. They are the seat's, not this diff's, which moves no golden and no plan.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base a441d2e15986033840c226eb39c4833c177f4dc8` -- `CI PREDICT: no closures, fast, wave-script or instrument red predicted against a441d2e15986` and 112 unpinned sites, each listed under `## Unpinned sites`; the two INERT READS it predicted earlier were applied with `--apply-inert`, and the eight STALE PINs this diff staled were deleted.
- `python3 tools/audit/archscore/score.py --diff a441d2e15986033840c226eb39c4833c177f4dc8 HEAD` -- `Architecture score: dS +0.0030 WORSENS (inadmissible: coord_footprint 2423->2440)`, with `coordinator_multiassigned_attrs 110 -> 109`; explained below.
- Seams (fixer step 8): the sites that split an interval between space and hot water are enumerated by `git grep -n "_commanded_split()\|dhw_share\|space_share" a441d2e15 -- custom_components/heatpump_optimizer/coordinator.py` at the merge base; each now asks `heat_energy.attribution` (`_interval_measured_heat_kw`, `_cop_reference_curve`, `_accumulate_energy`, `_settle_interval_diag`), and the check "the ledger and the diagnosis triple split by the same observed dwell" drives two of them with one dwell. The age-limit census in `tests/features.py` drives every key of `INPUT_MAX_AGE_MINUTES` alike, the new key included, and the P2 `state_age` registry in `tests/entities.py` gains `pump_signals.py::read` as a disposition (it carries the mode's value-change instant, never an age).

## Architecture score

Architecture score: dS +0.0030

- `coord_footprint` 2423 -> 2440: the counter's wiring into the coordinator's learners, 17 logic statements in five module functions handed the coordinator (`_observe_heat_energy`, `_replay_gate`, `_replay_fabric`, `_async_earn_heat_basis`, `_async_learn_heat_span`): the reads of the coordinator's own learner state (its baseline sample, its plan split, its two learners) cannot move out of it without a new published view per learner. Paid where it could be: the span arithmetic, the attribution and the resolution and reset rules are in `heat_energy.py` (no footprint), the two learners share `_replay_gate`/`_replay_fabric` instead of a copy each, and two earlier in-place writes to the ring (`shared_inplace_writes` 3 -> 5 in the first cut) and a `pump_signals` import that put `heat_energy` on layer 2 were removed before the handoff.

## Unpinned sites

The 112 sites `tools/pr/ci_predict.py --base a441d2e15986033840c226eb39c4833c177f4dc8` lists, by key. The ten design targets and the carries' three, each killed by `tests/features.py` in the in-tree table (`## Mutation proof`), are marked with their row; every site is pinned by `mutation-autofix` after the push (its lane mutates `custom_components/` only, and every one of these is there); a survivor it reports is triaged under `tests/mutation_ledger/survivor_triage/` in the next pass, never in a body.

- `custom_components/heatpump_optimizer/coordinator.py:919 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1051 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1054 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1055 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1065 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1081 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1092 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1095 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1095 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1097 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1099 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1101 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5057 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5059 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5107 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5129 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5137 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5512 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5563 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5564 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5572 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5611 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5665 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5672 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5673 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5678 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5678 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5695 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5723 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:9458 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/flow_meter.py:64 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:46 CONST` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:52 CONST` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:54 CONST` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:63 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:86 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:88 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:88 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:88 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:90 CLAMP_DROP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:92 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:97 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:98 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:100 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:122 CLAMP_DROP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:122 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:133 CMP_BOUND*2` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:133 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:135 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:162 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:162 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:164 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:167 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:169 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:171 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:172 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:176 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:178 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:182 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:185 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:187 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:189 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:193 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:199 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:206 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:224 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:226 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:237 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:240 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:240 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:241 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:242 CMP_BOUND*2` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:242 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:248 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:248 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:251 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:251 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:253 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:253 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:259 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:259 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:299 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:305 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:339 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:362 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:363 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:366 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:366 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:368 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:377 CMP_BOUND` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row C2
- `custom_components/heatpump_optimizer/heat_energy.py:377 GUARD_OFF` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row C2
- `custom_components/heatpump_optimizer/heat_energy.py:379 CMP_BOUND` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row C1
- `custom_components/heatpump_optimizer/heat_energy.py:379 GUARD_OFF` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row C1
- `custom_components/heatpump_optimizer/heat_energy.py:381 CMP_BOUND` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row R
- `custom_components/heatpump_optimizer/heat_energy.py:381 GUARD_OFF` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row R
- `custom_components/heatpump_optimizer/heat_energy.py:383 CMP_BOUND` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:383 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:403 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:404 BOOLOP` -- pinned by `mutation-autofix`; its line is killed in the in-tree table, row A
- `custom_components/heatpump_optimizer/heat_energy.py:407 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:407 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:413 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:413 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:415 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:417 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:426 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:426 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:435 GUARD_OFF` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:437 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/snapshots.py:83 RETURN_DEL` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1450 BOOLOP` -- pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1450 RETURN_DEL` -- pinned by `mutation-autofix`

## Red checks

- `tests / mutation`: red on this branch's head until `mutation-autofix` pins the 112 unpinned sites `## Unpinned sites` lists (`ci: pin killed mutants`); its lane mutates `custom_components/` only, where every one of them is. This PR's, by design: a new module adds sites no pin can cover before the push. The in-tree table (`## Mutation proof`) kills all 13 design and carry targets before the push, 0 survivors. Root-cause trigger answered: the cheaper detector already exists and fired, `tools/pr/ci_predict.py` (prepr step 6d) listing every site in about 16 s before the handoff; the standing cost of the repair before the PR exists would be `tests/mutation_table.py --pin-killed`, measured at about 67 minutes for 17 sites on #2753 (so hours for 112), which `ci-autofix.md` assigns to `mutation-autofix` after the push. No new detector is proposed.
- `tests / closures` and `tests / fast (3.14)`: `heat_energy.py` is a new module, which 19 recorded closures reach through `coordinator.py`, so `ci_predict.py` predicted UNDER-SCOPED and `tests/entities.py`'s three closure checks red ("every tracked file is either measured or deliberately classified", "and still covers every python file of the integration", the deployment-shape lane's closure check). Repaired before the handoff in commit `34a61c0dd`: `tests/derive_closures.sh --scripts-from <16 scripts> --record-only`, then `tests/closure.py merge --partial --allow-failures` (`tests/entities.py` ran to its summary line under the recording, failing only those three and the four heartbeat controls that fail at the merge base too). Each changed closure grew by `custom_components/heatpump_optimizer/heat_energy.py` alone, and nothing was dropped: `tests/block_duty.py`, `tests/boost_drift_replay.py`, `tests/config_flow_steps.py`, `tests/debug_collect.py`, `tests/deployment_shape.py`, `tests/doc_claims.py`, `tests/entities.py`, `tests/env_drift.py`, `tests/features.py`, `tests/finite_boundary.py`, `tests/golden.py`, `tests/manual_plan.py`, `tests/plan_view.py`, `tests/solar_alignment.py`, `tests/wood_advisor.py`, plus the two node closures `tests/card.mjs` and `tests/card_drift.mjs`. Those two node closures are Darwin growth only, picked up through the merge's widening rule, and no Linux node recording was replaced (ruled under mandate 6329234399). `tests/harness_headers.py` records under strace, which is Linux-only, so a cloud Linux seat recorded it with `tests/derive_closures.sh --single tests/harness_headers.py` (commit `df1f70675`, `ci: record harness_headers closure (Linux)`, one line: that closure gains `heat_energy.py`). `tests/arch_score_head.py`, which `ci_predict.py` does not name, is a full-coverage closure the deployment-shape lane's note counts, and `--single` grew it by `heat_energy.py` alone (`4f191ac0f`, with the note's file count, 100 to 101). The Python recordings are Darwin `sys.addaudithook` recordings, sound for those lanes (`ci-autofix.md`). The check is CI's Linux `closures` job, which re-verifies every one. Root-cause trigger answered: the cheaper detector exists and fired, `ci_predict.py` naming each script before the push.

## Forward-carry

- **R10-COP-GATE** (this diff adds a per-cycle refusal code a COP gate would read as a failure). Text: "From R10-HEAT-METER (#2261; finding-propagation.md). On a counter install (`heat_pump_heat_energy_entity` configured) the per-cycle COP fold returns `COP_REFUSED_SPAN_OPEN` (`span_open`) on every cycle that passed its gates: the COP folds at the span's close in `_async_learn_heat_span`, through `_fold_cop_evidence`. Render `span_open` as a span still open, never as a refusal or a not-measurable state, and the span refusals `counter_reset`, `counter_rollover`, `counter_resolution` and `span_too_long` (`heat_energy.SPAN_REFUSED_*`) and `unaligned_meters` as their own codes. Control: a counter install whose span folds shows its COP as measured while every cycle in between reads `span_open`." Carry: R10-COP-GATE
- **R10-UX-HEALTH** (the same codes reach `_measured_cop.refusal`, which the Health panel shows). Text: "From R10-HEAT-METER (#2261; finding-propagation.md). Beyond `unaligned_meters`, the COP refusal on a counter install is `span_open` on each cycle between span closes, and a closed span can be refused as `counter_reset`, `counter_rollover`, `counter_resolution` or `span_too_long` (`heat_energy.SPAN_REFUSED_*`). Give each a Health string, `span_open` reading as waiting for the span, not a fault. Control: the Health panel on a counter install mid-span renders the string, never the raw code." Carry: R10-UX-HEALTH
- **D15 live diagnosis, lead L9** (instrumented here, verification carried; the orchestrator routes it to the existing live-diagnosis group). Text: "From R10-HEAT-METER (#2261; D15 lead L9, finding-propagation.md). Each weekly learner snapshot now records `unhealthy_input`. It holds the first reason `_inputs_unhealthy` gave on that day: the rule over the indoor, outdoor and power inputs that marks a snapshot unhealthy. The house meter is not one of its inputs. On a healthy day it holds None. Read it in the next live bundle. Name which input marked each unhealthy weekly snapshot, and say whether that input was genuinely silent or whether outdoor's 180 min on-change limit flagged a quiet, healthy sensor. Change that limit only on that evidence. Controls: a week with every input reporting marks the snapshot healthy and names none (null); a week with one input silent all day names that input." Carry: R10-REPLAY-REAL-DAY

## Friction

none
