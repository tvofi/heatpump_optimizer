The owner's request on #2261: an optional delivered-heat energy meter (`heat_pump_heat_energy_entity`, "Heat pump heat energy meter", a `total_increasing` kWh sensor on the options' Power and energy group), read per span, with the heat split between space heating and hot water by the pump's mode entity. Built to the approved design, the architect note `dev/programme/designs/R10-HEAT-METER.md` on `design/R10-HEAT-METER` at `21f4fbfe9`, approved by `design-verdict/R10-HEAT-METER` `ad376684f` ("Design review: approve 21f4fbfe9"). An install with neither the counter nor a live single-duty mode entity reads what it read before: every coordinator golden capture is byte-identical to the merge base, each capture publishing mode `"Unknown"`. An install without the counter but with a live heat or hot-water mode entity does change: `_observe_heat_energy` folds the mode dwell every cycle, so the energy ledger (`_accumulate_energy`), the diagnosis triple, `_cop_reference_curve` and #2753's thermal replay split an interval at the observed `last_changed` instead of by the plan. That is the approved design's observed arm (roster carry 5 of R10-HEAT-METER), pinned by "the ledger and the diagnosis triple split by the same observed dwell".

Part of #2261

**One reader module, the coordinator calls it.** `heat_energy.py` (new, free of Home Assistant) owns the counter, the span and the mode dwell. `HeatEnergyMeter.observe_counters` reads the heat counter (and the electric energy counter beside it) once a cycle and closes a span on elapsed time, at the first read past `close_after_h = max(MIN, MAX - cadence - 0.05)` inside the interval learners' `HOUSE_LOSS_MIN/MAX_SAMPLE_HOURS` bounds (review point A of the design). A span past the maximum is refused (`span_too_long`), a counter that went backwards is a reset (`counter_reset`), one that jumped past 1.5 x the thermal nameplate over the span is a rollover (`counter_rollover`), and a counter too coarse for the heat expected in the span (step / expected > `HEAT_RESOLUTION_EPS`) is refused (`counter_resolution`); each refusal re-baselines, so the next span reads true. The electric delta counts only when it was read at the same instants (aligned on the read instant, never on `last_updated`: dr1-lag-idle); otherwise the span's COP is refused as `unaligned_meters`.

**Which heat source wins.** `flow_meter.read_heat_output_kw` stays the one answer, ranking a configured counter first, then #2753's thermal power entity, then the flow meter, and a configured source answers alone with no fallback: with the counter configured a cycle reads `None` there (the counter answers per span), so neither the thermal reading nor the flow meter is consulted. `probe_install(...).measured_heat` is true for either heat key.

**The consumers, on a counter install.**
1. *COP.* The per-cycle fold runs its gates and stops at `COP_REFUSED_SPAN_OPEN` (`span_open`), so a cycle that passed every gate leaves the span clean for COP; at the close `_async_learn_heat_span` folds heat over electricity on the two deltas through `_fold_cop_evidence` (the fold's tail, split out of `_fold_measured_cop` so a cycle and a span share it), judged on the span's duty.
2. *House heat-loss and lower-floor learners.* At the close the span replays from its opening state over its plan (`settle`), each learner on its own per-cycle gates ANDed over the span (review point B): one frozen, boosted or ventilation cycle refuses that learner's span and only its own. The per-cycle path still feeds the ventilation detector every cycle.
3. *The basis.* `HEAT_LOSS_BASES` gains `measured_heat`, earned at the first fold that replays a measured heat (`_async_earn_heat_basis`): the void path re-anchors the earlier fit through R10-RATIO-ANCHOR's mechanism (`_reanchor_house_heat_loss_scale`, `heat_loss_basis_voids`) before that fold, and the basis is saved; a meter the replay never uses keeps the scale. `store.py` changes the `house_heat_loss_basis` unread string only (no version bump, no migration, the orchestrator's ruling in the note).

**The mode split.** `pump_signals.read` carries a live mode's `last_changed` (`mode_changed_at`); `ModeDwell` places the split there. Only a live heat or hot-water mode is observed; a combination mode, a last-good reading (its `last_changed` is the stale state's own: dr1-last-good), an unrecognised one or an excursion the reads did not see is unobserved, and the interval falls back to the plan's split, which reproduces #2753's figure exactly. `heat_energy.attribution` is the one owner of that choice, and every site that split by the plan asks it: `_interval_measured_heat_kw` (and so #2753's replay of the thermal reading, and `replay_freeze`'s lift, which it is handed), `_cop_reference_curve`, the energy ledger (`_accumulate_energy`) and the diagnosis triple (`_settle_interval_diag`). A point reading (thermal power) is never time-split (review point C): an interval with hot water in it gives no space figure.

**Design deviations and rulings, each stated.**
- *`HEAT_RESOLUTION_EPS = 1.0`, not the design's 0.5*, answering the design review's carry dr3-eps-at-span (roster carry 11 of R10-HEAT-METER: "re-measure the EPS resolution bound at the real ~1.0 h span"). No ruling beyond that carry exists; the earlier body cited one recorded nowhere, withdrawn. At the real span (a 30 min cadence closes one-hour spans) 0.5 refuses every span of an integer-kWh counter at 1.5 kW, which 1.0 reads unbiased; the `EPS` lines of the harness below print both, and two checks pin it (`## Mutation proof`, row Q).
- *The mode entity is optional,* overruling the owner's brief ("The mode entity is REQUIRED when the heat meter is configured, with a refusal if it is missing"). The design note's revision 1 (`dev/programme/designs/R10-HEAT-METER.md` on `design/R10-HEAT-METER`, its line "It also follows two sets of orchestrator rulings under mandate 6329234399") records it ("The mode entity becomes optional and the refusal goes"), approved with the note by `ad376684f`. Without it, or in a combination mode, the split is the plan's, and an interval that heated the tank is not read as space heating.
- *D15 lead L6*, as roster carry 12 of R10-HEAT-METER asks ("key the age on the entity's last report time ... not on the last change"; the age was already keyed on `last_reported` through `inputs.source_polls`, so only the never-re-reporting limit moved): `INPUT_ON_CHANGE_MAX_AGE_MINUTES[CONF_HOUSE_POWER_ENTITY] = math.inf`. At the merge base a whole-house meter reporting only on change, holding 0 W while PV covers the house, read stale after 30 min though healthy; the PV-hold case is pinned.
- *D15 lead L9, instrumented, verification carried*, as roster carry 13 of R10-HEAT-METER asks ("list per snapshot which input made it so", which needs a live bundle): each weekly learner snapshot now records `unhealthy_input`, the first reason `_inputs_unhealthy` gave on that day (the rule over indoor, outdoor and power that marks the day; the house meter is not one of its inputs), and `None` on a healthy day. Outdoor's 180 min limit is unchanged. Which input marked the owner's five snapshots needs the next live bundle; that read is carried to the live-diagnosis group (`## Forward-carry`).
- *The new key's age:* `INPUT_MAX_AGE_MINUTES` 180 min as the energy meter's, and `INPUT_ON_CHANGE_MAX_AGE_MINUTES` `math.inf` (a counter holds while the pump idles), so it is outside `_r10st_same`'s equal-keys declaration, which drops `CONF_HOUSE_POWER_ENTITY` for L6. A dead counter re-reports first in its test (the INPUT-STALENESS precondition).
- *SAV attribution residue (roster carry 5):* dismissed per the design: the observed split fixes single-duty intervals; under a combination selector one meter cannot observe the split, so the plan split and its docstrings stay.
- *"Clamp means reset" (roster carries 10, 14):* kept, and re-measured at the merge base: the void path zeroes both learners' samples before `house_loss_confidence`, so `reanchor_heat_loss` runs at (0, 0), where both clamp branches are skipped (harness `CLAMP` lines).

**Alternatives considered (fixer step 17).** A cycle-count span and a fixed-K close were refused by the design against the learners' strict `dt_h > MAX` bound. Per-cycle time-splitting a point reading was refused (review point C). Since the review at `64d332426`, `bde3c6bd3` moved the span close, the replay gate and the cycle read into `heat_energy.py` (`close_span`, `replay_gate`, `observe_cycle`), the coordinator handing them values, so `coord_footprint` no longer rises (`## Architecture score`). A coordinator attribute for the meter was avoided: `heat_energy.meter_of` keeps it in a `WeakKeyDictionary` side table (`boost.py`'s pattern), and the coordinator's day-health flag moved onto the snapshot ring, so `coordinator_attrs` and `coordinator_multiassigned_attrs` each fell by one.

**A defect in this branch's own code, fixed here (`a9055ce32`).** `HeatEnergyMeter.observe_counters` pruned the mode dwell from the next span's opening instant before `settle` read the span just closed, so a span with a mid-span mode switch lost its segments and fell back to the plan split. The prune is now bounded by the closed span's own opening instant. The check "a span that switched to hot water 20 min in splits 20/40 at its close, not by the plan" fails on the pre-fix `heat_energy.py` (`switched Attribution(space=2.0, dhw=0.0, observed=False)`) and passes at the head; its null, a span with no change, reads all space at both.

## Head

`db4493c3e45432b8f15b1320790cced5ce723824`, merge base `0137c4cb052e134c953f31054907c01393d55ad7` (`git merge-base origin/main HEAD`). This head merges the PR head `91d78cbca` (its `ci: pin killed mutants` commit) into the earlier handoff `52aa1f5d1` (`056cf9dbd`), then `origin/main` twice (`234312dfe`, then `db4493c3e` after #2834 landed). Both merges were resolved by hand in `tests/golden/claimed_drift.txt` alone, where the `claimnotes` driver refused: the result is main's claim list with only `config_flow`'s note replaced by this diff's. `tests/structure_budgets.json` keeps this branch's lowered rows; main moved none of them. origin/main's tip `3b4180dcc` (#2858, tooling only) at 2026-10-26T18:32Z: `git merge-tree --write-tree origin/main HEAD` exits 0, so no further merge was made (fixer.md step 6).

## Mutation proof

Two instruments, both re-run at this head.

**The in-tree table**, `python3 dev/audit/harnesses/r10_heat_meter_mutants.py -j 3` at `db4493c3e` (each mutant one exact replacement in its own `git archive` copy, `tests/features.py` in full): the design's ten targets (C1 to I), the precedence check (P) and the carries' three (D, L6, L9). The null row (a comment-only edit) fails one check, #363's `recorded_at`, which fails in every `git archive` copy because the copy has no git history; a mutant is killed on the checks it fails beyond that one.

```
NULL      N0 null control (a comment): 1 of 4494 FEATURE CHECKS FAILED; 0 beyond the null
KILLED    C1 span closes at the minimum, not past close_after_h: 13 of 4494 FEATURE CHECKS FAILED; 12 beyond the null
      FAIL a closed span reaches the house and lower-floor learners with its 6 kW of space heat; a span whose house gate failed reaches the lower floor alone
      FAIL a counter span closes on elapsed time, inside the learners' sample bounds, under a drifting cadence and one event-driven cycle (null control: no drift
      FAIL a counter span folds COP as heat over electricity, exactly the plant's on a known-COP plant; inside the span a cycle folds nothing
      FAIL a span of exactly the learners' 1.5 h maximum is read (their bound is strict); an idle span reads zero heat, not a reset; a delta of exactly 1.5 x the
KILLED    C2 a span past the maximum is not refused: 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a counter span closes on elapsed time, inside the learners' sample bounds, under a drifting cadence and one event-driven cycle (null control: no drift
KILLED    Q resolution bound dropped: 3 of 4494 FEATURE CHECKS FAILED; 2 beyond the null
      FAIL an integer-kWh counter is refused at 0.6 kW, reads 1.5 kW unbiased over its spans (null control: 3.0 kW reads 3.0)
      FAIL null control for the resolution bound: at the design's 0.5 the one-hour span refuses every integer-kWh span at 1.5 kW, which 1.0 reads
KILLED    R reset branch dropped: 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a counter reset and a rollover are refused, and the next span reads true (null control: the same plant without either)
KILLED    P counter-first precedence dropped: 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a configured heat counter outranks the thermal power entity and the flow meter, and a cycle reads no heat from it (null control: the thermal entity al
KILLED    O observed test inverted: 6 of 4494 FEATURE CHECKS FAILED; 5 beyond the null
      FAIL a single-duty step the arbiter wrote (owned) counts as observed
      FAIL a span that switched to hot water 20 min in splits 20/40 at its close, not by the plan (null control: no change reads all space)
      FAIL heat then hot water inside one interval splits at the mode's last_changed (10 of 30 minutes space), and an integrated heat takes that share
      FAIL the ledger and the diagnosis triple split by the same observed dwell (one third space) where the plan said all space
KILLED    L split at the read, not at last_changed: 6 of 4494 FEATURE CHECKS FAILED; 5 beyond the null
      FAIL a change stamped ahead of its read lands at the read, and one stamped before the previous read lands at that read
      FAIL a mode that left and came back between two reads is an unseen excursion: the interval is unobserved and splits by the plan
      FAIL a span that switched to hot water 20 min in splits 20/40 at its close, not by the plan (null control: no change reads all space)
      FAIL heat then hot water inside one interval splits at the mode's last_changed (10 of 30 minutes space), and an integrated heat takes that share
KILLED    E earned basis never set: 4 of 4494 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL only an unearned meter on a measured-heat install earns the basis, and only on a heat reading (null control: the same install with a reading earns it)
      FAIL the earned basis is saved and restored with the meter still configured; with it removed the basis is the configured one and the fit is kept, not voide
      FAIL the first fold that replays a measured heat earns the measured_heat basis, voiding the earlier fit first; the next fold keeps it (null controls: no he
KILLED    A span_clean AND dropped (last cycle wins): 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL one gated middle cycle refuses that learner's span and only its own; the span replays from its opening state over its plan
KILLED    I integrated branch ignored: 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL the same interval on a point reading (thermal power) gives no space figure, not a half (null control: a space-only interval gives the reading)
KILLED    D the heat counter's on-change decision dropped: 4 of 4494 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a quiet heat counter holding its value reads fresh; one that re-reported and then fell silent past 180 min is stale; MWh reads as kWh
      FAIL all 28 age-limited keys: a quiet on-change source is stale only on a key named equal; a silent polling source is stale on every key, remembered past a
      FAIL every age-limited key declares its on-change limit, no lower than its polling one, and each kept equal is named with its reason
KILLED    L6 the house meter's on-change limit back to 30 min: 4 of 4494 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a house meter holding 0 W for 4 h on change only reads 0 kW (PV covering the house); one that re-reported and then fell silent 40 min is stale
      FAIL all 28 age-limited keys: a quiet on-change source is stale only on a key named equal; a silent polling source is stale on every key, remembered past a
      FAIL every age-limited key declares its on-change limit, no lower than its polling one, and each kept equal is named with its reason
KILLED    L9 the snapshot ignores the named input: 2 of 4494 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL a snapshot on an unhealthy day names the input that made it so, and a healthy day names none (D15 L9)
0 survivor(s) of 13 mutant(s); the null fails ['and the path that proceeds still stamps a resolvable recorded_at (#363)']
```

**The diff's added sites.** `tests / mutation` refused 34 diff-added sites at `91d78cbca` that `mutation-autofix` could not pin (`## Red checks`). This head adds checks to `tests/features.py` until every site `tools/pr/ci_predict.py` lists is killed or triaged, measured by the fixer's drive: each candidate mutant of each listed site applied to a copy of the tree, and the heat-meter section of `tests/features.py` (with the top-level definitions it needs) run against it, verdict against an unmutated baseline. At `a9055ce32` over 45 sites, 46 mutants: 37 killed by a failing check, 5 by an uncaught exception, 4 survived. Three survivors were gaps, each now killed by a new check with its null control (driven again at `2f78b7983`, baseline 94 of 94 passing, each mutant failing exactly the new check):

```
KILLED  coordinator.py:1064 BOOLOP -> if heat_kw is not None or meter.earns_basis(...)   1 new fail: "only an unearned meter on a measured-heat install earns the basis, and only on a heat reading ..."
KILLED  heat_energy.py:507 BOOLOP -> if got.space_kw is not None or e is not None:      1 new fail: "a span whose resolution is refused replays into no fabric learner ..."
KILLED  heat_energy.py:473 BOOLOP -> return not self.earned or measured_heat            1 new fail: "only an unearned meter on a measured-heat install earns the basis, ..."
```

The fourth, `heat_energy.py:135 RETURN_DEL` (`return None` -> `pass`, the last statement of `resolution_refusal`), is equivalent on every input and is triaged under `tests/mutation_ledger/survivor_triage/heat_energy.py/resolution_refusal.RETURN_DEL.da9e8e97.json`. The five exception kills (`heat_energy.py` 133 CMP_BOUND on `expected_kwh > 0.0`, 417 BOOLOP, 503 GUARD_OFF, 533 RETURN_DEL, 541 RETURN_DEL) count as one failing check each under `tests/mutation_table.py`'s `failing_count` ("plus one for an uncaught exception"), which `killed` reads.

## Null control

The unmodified tree (merge base `0137c4cb0`) has no counter key: the harness feeds both trees the same cycling plant, and the base reads the point thermal meter on every arm, so its `counter`, `reset` and `integer` arms print the `point` arm's scales, bit for bit. The head's `point` and `commanded` arms (no counter configured) are bitwise identical to the base's, the null for an install without the key; every coordinator golden capture is byte-identical to the merge base (each publishes mode `"Unknown"`, so attribution takes the plan arm). Inside the suite each new check carries its own null, named in its text: heat equal to the model's COP times the electricity holds `cop_scale` at 1.0; the reset and rollover plants against the same plant unplanted; 3.0 kW on an integer counter reads exact; a space-only interval on a point reading gives the reading; no heat reading and a flow-meter estimate keep their basis; a healthy day names no input; the same install with a heat reading earns the basis where the one without does not; a fine counter's span replays into both learners where the refused one replays into none; a span with no mode change reads all space where the switched one splits 20/40.

## Figures

All at head `db4493c3e45432b8f15b1320790cced5ce723824` against merge base `0137c4cb052e134c953f31054907c01393d55ad7` unless stated.

- `python3 dev/audit/harnesses/r10_heat_meter.py` (sha1 `222052bb36eb292972f30a49f9b6f3d99172566c`; the fixer's own instrument, not a finder's: this group is an owner feature request with no audit finding behind it, so no finder's harness exists) -- the #2753 plant cycling at 40 % duty, 9 kW while on, 600 refreshes of 30 min at each of 7 outdoor points. Head: `counter` spread 0.0000, every scale 0.900011 against `TRUE_K` 0.9, 2093 span folds; `reset` spread 0.0000 at 0.900018 on 1981 folds; `integer` spread 0.0009, 0.89914 to 0.90006. Base: all three print the `point` arm, the defect: spread 0.4566, `cop_scale` 1.6 (`COP_SCALE_MAX`) from -15 to -2 degC and 1.3559, 1.2703, 1.1434 above. `point` and `commanded` print identical scales and fold counts at both trees.
- The same command's `CLAMP` lines (roster carries 10 and 14, both trees): the void path's confidence is (0.0, 0.0) and over 45 stored cases `reanchor_heat_loss` resets 0 (max |value - 1| = 0.0); its null at confidence (1.0, 1.0) resets 37. Identical at both trees.
- The same command's `EPS` lines (dr3-eps-at-span, head only): 199 one-hour spans of an integer-kWh counter. At `HEAT_RESOLUTION_EPS` 1.0: 0.6 kW keeps 0; 1.5 kW keeps 199, mean 1.4975, sd 0.5; 2.2 kW keeps 199, mean 2.196, sd 0.397; 3.0 kW keeps 199, mean 3.0, sd 0.0. At 0.5: 1.5 kW keeps 0, the rest as at 1.0.
- `python3 dev/audit/harnesses/r10_heat_meter_mutants.py -j 3` (sha1 `19eea15bb6e32029200c45d0392a403c8784e1a4`) -- the table in `## Mutation proof`, 0 survivors of 13.
- `PYTHONPATH=tests/hastub GATE_SCOPE=auto GATE_SCOPE_BASE=0137c4cb0 GOLDEN_MODE=drift GOLDEN_REF=0137c4cb0 bash tests/run.sh` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`, `4 TEST SCRIPT(S) FAILED`; among its lines `ALL 4494 FEATURE CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 0137c4cb052e134c953f31054907c01393d55ad7`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, `ALL 112 HARNESS HEADER CHECKS PASSED`. The four, each this macOS seat's and not this diff's: `tests/optimality.py` `1 of 84` (`one|summer_negative|shoulder: a recorded claim still has a gap (not stale)`), `tests/stress.py` `1 of 113` (`shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`) and `node tests/card.mjs` (V8 heap out of memory), each failing identically in a detached worktree of the previous merge base `1f82fee49` on this seat (#2834 and #2858 between it and `0137c4cb0`/`3b4180dcc` touch no solver or card plan path) (optimality the same check, stress the same 4.67 vs 3.96, card.mjs the same `FATAL ERROR: Ineffective mark-compacts near heap limit` after `tests/plan_view.py`); and `tests/entities.py` `4 of 2463`: four heartbeat py-spy positive controls (`hb:positive_control survives one hung py-spy sample ...`, `and a try whose sample misses the spin ...`, `the control rests between tries ...`, `the control survives two hung samples ...`, py-spy unable to sample without root on macOS, failing identically at the earlier merge base `a441d2e15` on this seat). CI's Linux `tests / fast` is the arbiter for all four.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`. Recorded down, no row raised: `coordinator_attrs` 143 -> 142, `coordinator_multiassigned_attrs` 110 -> 109, `max_class_loc` 8241 -> 8186, `seam_cut_total` 424 -> 423 (`1838090da`), `class_excess_loc` 18080 -> 18077 (`52aa1f5d1`).
- `python3 tools/audit/archscore/score.py --diff 0137c4cb0 HEAD` -- `Architecture score: dS +0.0131 IMPROVES`, `coordinator_multiassigned_attrs 110 -> 109 +0.0131`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 0137c4cb0` -- `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 0137c4cb052e (a data-file read is not seen)` and `44 unpinned site(s) the diff adds`, each under `## Unpinned sites`.
- Seams (fixer step 8): the sites that split an interval between space and hot water, enumerated by `git grep -n "_commanded_split()\|dhw_share\|space_share" a441d2e15 -- custom_components/heatpump_optimizer/coordinator.py`; each now asks `heat_energy.attribution` (`_interval_measured_heat_kw`, `_cop_reference_curve`, `_accumulate_energy`, `_settle_interval_diag`). The dwell's readers are `settle` (the span) and the cycle read; the prune that starved `settle` (`a9055ce32`) was the only writer that dropped segments before both had read them.

## Architecture score

Architecture score: dS +0.0131

- `coordinator_multiassigned_attrs` 110 -> 109: the day-health flag moved onto the snapshot ring. The review at `64d332426` read `coord_footprint 2423->2440`; `bde3c6bd3` moved that wiring into `heat_energy.py`, which reads no coordinator private (`coordinator_private_reach` 0), and the score no longer lists `coord_footprint`.

## Unpinned sites

The 44 sites `tools/pr/ci_predict.py --base 0137c4cb0` lists, each driven in the fixer's drive (`## Mutation proof`; at `a9055ce32`, where `coordinator.py`'s 5583, 5622, 5689 and 5734 read 5571, 5610, 5677 and 5722, the same lines before main's #2834 shifted them); `mutation-autofix` pins each after the push.

- `custom_components/heatpump_optimizer/coordinator.py:1064 BOOLOP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1064 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1095 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1097 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:1099 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5583 RETURN_DEL` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5622 RETURN_DEL` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5689 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:5734 RETURN_DEL` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:46 CONST` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:54 CONST` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:63 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:90 CLAMP_DROP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:133 CMP_BOUND*2` -- the `/ expected_kwh >` bound killed by a failing `tests/features.py` check, the `expected_kwh > 0.0` bound by an uncaught exception (`ZeroDivisionError`, which `failing_count` counts as one failing check); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:162 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:172 BOOLOP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:178 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:185 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:199 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:237 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:241 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:248 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:251 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:253 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:259 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:299 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:417 BOOLOP` -- killed by an uncaught exception in `tests/features.py` (`failing_count` counts it as one failing check); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:417 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:419 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:428 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:430 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:432 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:434 CMP_BOUND` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:466 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:473 BOOLOP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:473 RETURN_DEL` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:503 GUARD_OFF` -- killed by an uncaught exception in `tests/features.py` (`failing_count` counts it as one failing check); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:507 BOOLOP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:507 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:531 GUARD_OFF` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:533 BOOLOP` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:533 RETURN_DEL` -- killed by an uncaught exception in `tests/features.py` (`failing_count` counts it as one failing check); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/heat_energy.py:541 RETURN_DEL` -- killed by an uncaught exception in `tests/features.py` (`failing_count` counts it as one failing check); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_signals.py:266 RETURN_DEL` -- killed by a failing `tests/features.py` check in the fixer's drive; pinned by `mutation-autofix`

## Red checks

Every failure conclusion on this branch's commits since it forked, read from the check-runs API at the PR head `91d78cbca` and from `pr-contract`'s `red-history` line there (`prelude, tests / closures, tests / mutation`). Causes read from each job's log with `tools/audit/seat/failure_logs.sh` at `91d78cbca`.

- `tests / mutation` (red at `91d78cbca`): `MUTATION TABLE REFUSED -- 3935 unpinned site(s) against 3913 at the ratchet base 5fb833930..., 34 of them added by this diff`. `mutation-autofix` pinned what its drive killed (`91d78cbca`, `ci: pin killed mutants`) and left 34 survivors unpinned, so its lane stayed red. Fixed at the cause: the checks this head adds kill every site the diff adds but one, triaged equivalent (`## Mutation proof`, `## Unpinned sites`); the remaining 44 are pinned by `mutation-autofix` after the push. Root-cause trigger answered: the cheaper detector for which sites survive is a local drive of the sites `tools/pr/ci_predict.py` lists; the fixer's drive over the heat-meter section took 2561 s for 46 mutants, against `mutation-autofix`'s pin drive after the push. `ci_predict.py` (prepr step 6d, about 35 s here) lists the sites but cannot say which survive, and the full local `--pin-killed` costs a 21-minute `tests/features.py` run per mutant. No new detector is proposed: the drive this seat ran is the detector, and its cost is the fixer's, before the handoff.
- `gate` (red at `91d78cbca`): `FAIL tests / mutation: failure (this run)`. The required aggregate of the line above; no cause of its own.
- `pr-contract / pr-contract` (red at `91d78cbca`): `ERROR [pr-body] ... check \`prelude\` is red and \`## Red checks\` does not name it`. The body at that head named `tests / mutation` and `tests / closures` but not `prelude`. This body names it below. Root-cause trigger answered: the cheaper detector exists, `tools/pr/prepr.sh --body-check`, which runs the same `policy_lint.mjs` before the push; it cannot see a red that a later CI run produces, which this one was. No new detector.
- `prelude` (red on run `40286212552`, `CI edit pr=2854`, at `64d332426`): `FAIL run(s) [40286212845] still adding sources after 8700 s` -- the body-edit dispatch's prelude waited on another run of the same head past its bound and gave up; nothing in this diff's code or body was graded. `prelude` at `91d78cbca` is `success`. Root-cause trigger answered: no cheaper detector exists; the wait is on CI's own queue, which no local run can see.
- `tests / closures` (red on an earlier commit of this branch, before the bot's `3a3b51f1c` `ci: re-record closures`): `heat_energy.py` was a new module reached through `coordinator.py`, so 19 recorded closures were UNDER-SCOPED. Repaired by the fixer before handoff for the scripts `ci_predict.py` named and by `closures-autofix` for the rest; green at `64d332426` and since. Root-cause trigger answered: the cheaper detector exists and fired, `ci_predict.py` naming each script before the push.

## Forward-carry

All three are in their stages' own briefs on `origin/main`, in `dev/programme/rosters/wave-r10-groups.json` (landed from `handoff/audit-r10-roster`; that branch's tip `071c715da` carries them too):

- **R10-COP-GATE**, appended by `3aab36e9a` (`roster_edit append-carry R10-COP-GATE`): render `span_open` (`COP_REFUSED_SPAN_OPEN`) as a span still open, never a refusal, and `counter_reset`, `counter_rollover`, `counter_resolution`, `span_too_long` (`heat_energy.SPAN_REFUSED_*`) and `unaligned_meters` as their own codes. Control: a counter install whose span folds shows its COP as measured while every cycle in between reads `span_open`. Carry: R10-COP-GATE
- **R10-UX-HEALTH**, appended by `95e478db3` (`roster_edit append-carry R10-UX-HEALTH`): a Health string for `span_open` (waiting for the span, not a fault) and for each span refusal code. Control: the Health panel on a counter install mid-span renders the string, never the raw code. Carry: R10-UX-HEALTH
- **R10-REPLAY-REAL-DAY** (D15 lead L9), appended by `8c918fd2b`: read `unhealthy_input` from each weekly learner snapshot in the next live bundle, name the input that marked each unhealthy snapshot, and change outdoor's 180 min on-change limit only on that evidence. Controls: a week with every input reporting names none (null); a week with one input silent all day names that input. Carry: R10-REPLAY-REAL-DAY

## Friction

none
