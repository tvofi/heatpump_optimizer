R10-COP-LEARNER-DRAW-FLOOR, built on the approved design (`design.md` at 94d2c9f06576693b31996d21d18af241d41640b2 of design/R10-COP-LEARNER-DRAW-FLOOR; `Design review: approve`, design-verdict at 732212c268). Three carries on the COP learner's one judgement seam, `MeasuredCop` in `accuracy.py`. `Carry N` below is entry N (0-based) of this group's `carry` list on handoff/audit-r10-roster at 30097de04722.

What ships, by carry:

- **Carry 0 (84e73ec4), the capped floor.** `draw_range.power_floor_kw(draw, params)` is the one floor `MeasuredCop.judge_floor`, `coordinator._fold_flow_lift` and `accuracy.diagnostics_view` read, each on the same window object. It is `flow_lift_power_floor_kw` capped by the low end (`LOW_PERCENTILE`) of the draws metered under a run ask, never under `on_threshold_kw`. A run ask is an ask at or above the window's configured minimum and above zero: `DrawRange._run_asked`, the pair reader `follows_ask` built inline and now shares. Invariants (a) to (f) of the design are each a check in `tests/features.py`.
- **Carry 1 (35931f4b), hold-then-replay.** `draw_range.ask_evidence` returns one of four states; `follows_ask` is that state as a tri-state, results unchanged. `MeasuredCop.judge_ratio` is an instance method on the interval's row (`accuracy.CopInterval`): a departure beyond `COP_ASK_TOLERANCE` is held while the evidence is pending and reads `COP_REFUSED_NO_EVIDENCE`, no new code. `MeasuredCop.release` is the one place a held row is judged: all fold on follows, none on does-not-follow, base's rule where the evidence is unobtainable, and while it is pending base's rule for a row older than `COP_HOLD_HORIZON_S` (a week) or pushed out of a hold of `draw_range.WINDOW` rows. A released row folds against the scale it was read at. `diagnostics_view` gains `held_intervals`.
- **Carry 2 (R10-COP-GATE-E band), measurement, no build.** Re-run at this head, `dev/audit/harnesses/r10_cop_gate_band.py` reads `fit=none` on both fixtures under `tests/replay/` and its `--synthetic` control fits. The carry stays open on the named owner data (`## Forward-carry`).
- **Carry 3 (issue 3106 item 4, the set-point-to-draw map), not built here.** It is the brief of R10-DRAW-MAP-EVIDENCE, a live group ordered after this one and built on this handoff; nothing in this diff touches `thermal_model.flow_setpoint_for_level` or `follows_ask`'s slope test. Carry: R10-DRAW-MAP-EVIDENCE
- **Carries 4 to 9 are this body's own items, routed back to this group for a ruling**, each still under `## Forward-carry` or `## Friction` with its text unchanged: Carry 4 (09c5aa75, departure 1), Carry 5 (5b2b2810, departure 2), Carry 6 (ade1b168, note n2), Carry 7 (870278d1, the unobtainable arm), Carry 8 (28d8e538, the cap reads run-asked draws only), Carry 9 (b4659e0c, the `fixer.md` contradiction). None is built in this round: each waits on the owner's or the orchestrator's decision.
- The walking metered/asked ratio moved from the coordinator to `MeasuredCop.walk_ratio` (design note n1), which pays for the coordinator lines the release adds.

**Departures from the design note, each made because the tree refused the note's letter. They are disclosed here for the reviewer and routed under `## Forward-carry` for a ruling.**

1. **Where the release runs.** The note calls `release` from `_learn_measured_cop`, after the interval's own refusal is written. There, the check "#1523 class check: every learner feeder in coordinator.py consults the freeze or carries a disposition" went red (`undispositioned ['_learn_measured_cop']`): a cycle the learners are frozen on would have moved the COP scale. The census accepts a disposition, but its key is the function name, and an entry for `_learn_measured_cop` would also excuse any later fold of present evidence written there (`fixer.md` step 14). So the route changed: the release runs in `_fold_measured_cop`, past the freeze gate and the missing-reading guard and ahead of the interval's own judgement. The census passes with no new disposition. Consequences: a frozen cycle and a cycle with no power reading release nothing, and the hold cannot grow on such a cycle either; released rows fold before the cycle's own interval, not after; the interval's code is still its own, because the replay's return value is discarded.
2. **A replay trains the scale alone.** The note folds each released row through `_fold_cop_evidence`. That function's tail feeds the capacity envelope from this cycle's `_measured_power`, `_commanded_power()` and outdoor bucket, none of which is the held interval's. A replay returns before that tail. Cost: a held departure asked at or above 0.95 of nameplate no longer feeds the envelope, which it did when base folded it at its own tick.
3. **The cap is keyed to the configured range.** `power_floor_kw` returns the configured figure while the window's `config` differs from the live parameters' range. The note's invariant (e) reverts the floor when `DrawRange.observe` clears the window, which is at the next running sample; until then the window's pairs were asked under the old minimum, and a raised minimum would read them as run asks. The check for (e) pins both.
4. **`thermal_model.py` is touched, docstrings only.** The note lists it as not touched and its note n3 asks for `flow_lift_power_floor_kw`'s reference to the judgement to be updated; that reference was false at the head, so two docstrings changed and no code.
5. **One harness row the note lists as a null moves.** `p4_follow_lag1tick` folds fewer intervals than at the base (`## Figures`). Its draw is the previous interval's ask, the window reads that as not following, and the departures base folded before the evidence are now held and dropped. That is carry 35931f4b's stated behaviour on a draw that does not follow its ask; the note's spike did not show the row.

One existing check changed its expectation: "with no draw evidence a departure folds only past the nameplate third ... folds on 4 kW, as base" asserted the base behaviour this carry removes. It now pins both arms: pending holds on 4 kW and on 14 kW, and with no window base's rule stands.

The save cadence of the thermal learning store reads `_cop_samples // 10` crossing, where it read `% 10 == 0`: a release folds several intervals in one cycle and can step over a multiple of ten.

## Head

a472503fe19d7237d3701d9ac6b23e16bd0fb675, on merge base 0a1ef512f42cbf380049b11b096eb89c5a222ccc. Measured 2026-11-15 04:39 UTC. At that time origin/main is 2c69fb3560f23381193ab9e3d2a1632fe38d35ba, and `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0), so main is not merged again; the train re-proves the head on the current main.

Round 3, a repair of the red `tests / mutation` at the pull request's head 5cf3425240ac (`## Red checks`). The head is the round-2 handoff 29b99b6f9f0e merged with 5cf3425240ac (merge 24d89a1b44, no conflict), which brings the bot's `ci: merge main` and `ci: pin killed mutants`, and two commits on that merge: `git diff --stat 24d89a1b44 HEAD` lists `tests/features.py` and two files under `tests/mutation_ledger/killed_by/`. No production line changed in this round: `git diff 24d89a1b44 HEAD -- custom_components` prints nothing. The merge moved the merge base from 9fdba3b8547f to 0a1ef512f42c, so the figures below that are a function of the merge base were re-taken at this head and say so; a figure still naming a round-1 or round-2 commit is that commit's measurement.

- The two sites the lane named alive: one killing check each, under `## Mutation proof`, "Round 3". Neither is triaged.
- Whose line `coordinator.py:962` is: this branch's. `git diff $(git merge-base origin/main HEAD)...HEAD -- custom_components/heatpump_optimizer/coordinator.py` holds one hunk in `_fold_flow_lift`, `-    if commanded < params.flow_lift_power_floor_kw:` and `+    if commanded < draw_range.power_floor_kw(coord._accuracy.draw, params):`. The branch rewrote the right-hand operand (carry 0); the `<` the mutant moves is main's own, unchanged, at line 961 of the merge base.

Round 2 was a repair of `Fix review: blocked a827c3d985b2` (probe/revt-r10-cop-learner-draw-floor-9a909e3e at 67ef8a2fc9cb). One commit on a827c3d985, 29b99b6f9f: `git diff --stat a827c3d985 29b99b6f9f` lists `tests/features.py`, `dev/audit/harnesses/cop_duty_floor.py` and one docstring line of `custom_components/heatpump_optimizer/accuracy.py`. No production code line changed: `git diff a827c3d985 29b99b6f9f -- custom_components` is that one docstring line. What it answers:

- Block 1 and 2, and the third survivor the review lists under `## Findings` (the span close's window argument): one killing check each, under `## Mutation proof`, "Round 2".
- Block 3: four budget rows moved, not five (`## Figures`, "Gate and ratchets").
- Block 4: `MeasuredCop.release`'s docstring now says where it runs: ahead of a cycle's own judgement, never on a frozen or unread cycle.
- The review's first finding (an install that never asks at or above its configured minimum waits for a full window): its rows are in the harness and in `## Figures`, and the finding is under `## Forward-carry`.
- The review's note that the body names no enumeration rule: the rule and its output are in `## Figures`, "Sibling sites".

## Mutation proof

Failing test first: the block from `R.section("R10-COP-LEARNER-DRAW-FLOOR` to `R.section("R10-COP-GATE (#2262)` of `tests/features.py`, run by `tools/audit/seat/features_block.py` with its emitted prelude, on the base's production files stops at `ImportError: cannot import name 'CopInterval'`; on this head it prints `ALL 33 FEATURES BLOCK PASSED`.

Hand mutants, each applied alone to a detached worktree at db4395285f (the production code is the same at the head: `git diff db4395285f 29b99b6f9f -- custom_components` is one docstring line of `accuracy.py`, and the merge of round 3 brings main's own changes) and restored, driven by that block and by the block before it (from `# silence the learner. Synthetic numbers only.`). The unmutated tree fails no check. Every mutant fails at least one; the first failing check is named.

| mutant | failing check (first) |
|---|---|
| `power_floor_kw`: `min(floor, low_kw)` to `low_kw` | (a) the cap never raises the floor |
| `power_floor_kw`: the `max(on_threshold_kw, ...)` dropped | (b) the floor never goes under on_threshold_kw |
| `power_floor_kw`: every evidence sample in place of `_run_asked` | (d) a draw under an ask below the configured minimum never moves the floor |
| `power_floor_kw`: `cfg_min <= 0.0` guard dropped | (f) with no modulation floor configured the nameplate third stands uncapped |
| `power_floor_kw`: the config-key guard dropped | (e) a window keyed to another configured range caps nothing |
| `power_floor_kw`: `MIN_SAMPLES - 1` | (c) no window, an empty one, and one of 47 run-asked pairs |
| `_run_asked`: the configured-minimum half dropped | (d) |
| `ask_evidence`: no window reads pending | ask_evidence is unobtainable with no window |
| `ask_evidence`: a full window stays pending | ask_evidence is unobtainable ... on a full window |
| `ask_evidence`: `WINDOW - 1` | ask_evidence is unobtainable ... one sample short of full it is still pending |
| `ask_evidence`: flat asks read pending | ask_evidence is unobtainable ... on asks that never moved |
| `judge_ratio`: the pending arm deleted (base's rule) | a departure is held ... only while the evidence is pending |
| `judge_ratio`: held and folded | a departure is held, and reads as awaiting evidence |
| `judge_ratio`: unobtainable held too | a departure is held ... takes base's rule with nothing held where it is unobtainable |
| `release`: does-not-follow judged by base's rule | release: evidence empties the hold |
| `release`: follows judged by base's rule | release: evidence empties the hold |
| `release`: no week exit | release: while the evidence is pending a row waits a week and no longer |
| `release`: week bound exclusive | the same check, at 7 days exactly |
| `release`: a stamp ahead of the clock waits | release: a row stamped ahead of the clock |
| `release`: no push-out exit; push-out off by one | release: the hold is bounded at 336 rows |
| `release`: pushed-out and aged rows returned unjudged | release: while the evidence is pending ... both leave by base's rule |
| `release`: unobtainable folds everything | release: where the evidence is unobtainable |
| `release`: the hold not cleared | release: evidence empties the hold |
| `judge_floor`: reads no window | judge_floor reads the capped floor on the window it is handed |
| `diagnostics_view`: the configured floor; the held count at 0 | a 2.0 kW interval on a 3.0 kW minimum ...; the diagnostics count the held intervals |
| `walk_ratio`: returns the walked value | walk_ratio hands back the value before the interval |
| coordinator: no release | a released interval folds against the scale it was read at |
| coordinator: the release ahead of the freeze gate | a frozen cycle and one with no power reading release nothing |
| coordinator: replay at the live scale; `read_scale` ignored; the row stamped with scale 1.0 | a released interval folds against the scale it was read at |
| coordinator: a replay feeds the present-state tail | a replayed interval folds the scale and not the capacity envelope |
| coordinator: a replay does not count as a sample | a released interval folds against the scale it was read at |
| coordinator: the cycle's floor, the flow-lift floor, each reading no window | a 2.0 kW interval on a 3.0 kW minimum folds its COP and its flow lift |
| coordinator: the save cadence back to `% 10 == 0` | a release that steps the fold count over a multiple of ten |

That is 38 mutants (a row with a semicolon is one mutant per clause). Two more, the survivors prepr's own mutant step drew at 38c3c4bb4d, are killed by checks added in a827c3d985 and listed under `## Unpinned sites`.

The route change of departure 1: with the release in `_learn_measured_cop` (the tree of acf912282f, this branch's first commit) the scoped gate's `tests/features.py` printed `2 of 5616 FEATURE CHECKS FAILED`, the #1523 class check (`undispositioned ['_learn_measured_cop']`) and its null control; at the head both pass.

### Round 2: the review's three survivors

Each of the review's three surviving mutants (`ev/mutants.py` at the probe ref) was first reproduced at a827c3d985 and then run at 29b99b6f9f, by `python3 tools/audit/seat/mutant_run.py --spec <the three as {name, file, old, new}> --cmd <driver>` in its `git archive` copy. The driver runs three blocks of `tests/features.py` through `features_block.py`, each behind the prelude `--emit-prelude` derives from the tree it runs on: the two blocks above and the block from `R.section("R10-HEAT-METER: a delivered-heat counter` to `R.section("supply switch at step boundaries`, where the span close's checks are. Unmutated, a827c3d985 prints `ALL 33`, `ALL 34` and `ALL 77 FEATURES BLOCK PASSED` and 29b99b6f9f `ALL 35`, `ALL 34` and `ALL 78`. The driver's null mutant printed `SURVIVED NULL` in both runs. Each mutant, applied alone to an archive copy of 29b99b6f9f, fails exactly one check of the block that holds it, the one named.

| mutant | at a827c3d985 | at 29b99b6f9f | the check that fails |
|---|---|---|---|
| `judge_ratio`: `or state == ASK_FOLLOWS` deleted (`accuracy.py`) | SURVIVED | KILLED | once the meter shows the draw follows the ask, a departure under the nameplate third teaches |
| the replay's `row.reference` replaced by `self._cop_reference_curve()` (`coordinator.py`) | SURVIVED | KILLED | a released interval is judged against the curve of the cycle it was read on |
| the span close's `coord._accuracy.draw` argument dropped (`coordinator.py`) | SURVIVED | KILLED | the span close judges the duty floor capped by the stored running-draw window |

- The first check asks 2.0 kW drawing 2.6 on a 14 kW nameplate, under the 4.2 kW third, through `judge_ratio` and through `_learn_measured_cop`: it folds on a window that follows and is refused `awaiting_draw_evidence` with no window (the control, base's rule).
- The second check does not pin a folded scale, as the review asked, because the reference cannot move one: with no heat reading `flow_meter.cop_evidence` returns the scale times ask over draw whatever the modelled COP, so a held row replayed against another outdoor temperature or the hot-water curve folds to the same scale. What the reference decides is whether the row folds at all (`COP_REFUSED_BLENDED` for a reference with no curve). The check drives both directions through the cycle with the operating mode observed: an interval held on a space cycle and released by a cycle split evenly between space and hot water folds (the mutant refuses it), and one held on such a blended cycle and released by a space cycle trains nothing (the mutant folds it).
- The third survivor is the one the review dismissed as a no-op in every state the design names. It is not equivalent, so it has a check and no triage: an install that metered its pump running under an overstated minimum and then dropped its power entity keeps the window in the store, and its span close reads the capped floor. The check runs a 2.0 kW counter span on a 3.0 kW minimum with no power entity: it folds behind a window that metered the pump at 1.8 kW and is refused `duty_floor` behind an empty one. This is the design's "one window object" read at its third caller; design note v4 stated the empty-window case only.

### Round 3: the two bound survivors

`tests / mutation` at 5cf3425240ac named `accuracy.py:1004 CMP_BOUND` and `coordinator.py:962 CMP_BOUND` alive. Each line was mutated by `python3 tools/audit/seat/mutant_run.py --spec <the four below as {name, file, old, new}> --cmd <driver>` in its `git archive` copy, at 24d89a1b44 (the merge, before this round's checks) and at this head. The driver runs the block of `tests/features.py` from `R.section("R10-COP-LEARNER-DRAW-FLOOR` to `R.section("R10-COP-GATE (#2262)` through `features_block.py`, behind the prelude `--emit-prelude` derives from the tree it runs on. The driver's null mutant printed `SURVIVED NULL` in both runs; unmutated the block prints `ALL 35 FEATURES BLOCK PASSED` at 24d89a1b44 and `ALL 37` at this head. `accuracy.py:1004` holds three comparisons and the lane's line does not say which survived, so all three were run: two were already killed and are the control that the driver reaches the line.

| mutant | at 24d89a1b44 | at this head | the one check that fails at this head |
|---|---|---|---|
| `release`: `0.0 <= utc_elapsed_seconds(now, row.at)` to `0.0 <` (`accuracy.py`) | SURVIVED | KILLED | release: a row stamped at the clock itself is zero seconds old and waits; a microsecond ahead of the clock it leaves by base's rule |
| `release`: `i >= over` to `i > over` (`accuracy.py`) | KILLED | KILLED | release: the hold is bounded at 336 rows |
| `release`: `<= COP_HOLD_HORIZON_S` to `<` (`accuracy.py`) | KILLED | KILLED | release: while the evidence is pending a row waits a week and no longer |
| `_fold_flow_lift`: `commanded < draw_range.power_floor_kw(...)` to `<=` (`coordinator.py`) | SURVIVED | KILLED | the flow-lift fold takes an ask exactly at the floor and refuses one a nanowatt under it, on the window's cap (1.8 kW) and on the configured figure (2.4 kW) |

- Neither survivor is equivalent, so each has a check and no triage. Age zero is reachable: a held row released on the instant it was stamped (a replayed cycle, a clock that did not advance) has a known age of 0 s; under the mutant it leaves the hold by base's rule, where the design holds it. An ask exactly at the floor is reachable where the plan asks the configured minimum on an install with no run-asked evidence.
- The flow-lift check reads its floor from `draw_range.power_floor_kw` itself and sets the ask to that double and to that double less 1e-9 kW, at both ends of the floor's range: the window's cap and the configured figure (an empty window). It encodes a design choice: the flow-lift floor is exclusive, as `MeasuredCop.judge_floor`'s is.
- The ledger's own mutant: `tests/mutation_table.py --pin-killed --scripts tests/features.py` at a275b26db9 printed `PIN KILLED: 4 pinned, 0 left unpinned` and wrote the two `killed_by` pins of a472503fe1 (anchor 017bc704 covers the three sites of the `release` line, each killed; anchor 04683984 the flow-lift bound).

## Null control

- Harness, unwarmed rows: every `min1_*` and `min3_*` row, `selfmod_independent`, `selfmod_matched`, `selfset_hourly`, `selfset_three_hour`, `selfset_flat`, `fixed3_duty50`, `fixed3_duty70`, `fixed3_duty85`, `liveness`, `true_0.7_4kw` and `p4_follow_noise10` print the same line at the base and at the head (`diff` of the two outputs lists only the rows under `## Figures`).
- The cap moves nothing without run-asked evidence: `min3_running_warm_own`, `min1_duty_cycled_warm_own`, `fixed3_duty50_warm_own` and `fixed3_duty70_warm_own` read the same at both ends.
- The hold loses nothing where no evidence ever arrives: `held_full` and `held_filling` fold 96 of 96 at both ends.
- A window with no run-asked pairs, no window, and a window keyed to another range return `flow_lift_power_floor_kw` bit for bit (checks (c), (d), (e)).
- With no draw window (`_learn_measured_cop()`, as the stubs and the heat-metered harnesses call it) the state is unobtainable, nothing is held and base's rule stands (check "while draw evidence is pending a departure is held on any nameplate ... with no window base's rule stands").
- The mutation driver's own null: the unmutated worktree fails no check of the two blocks.
- Round 3's survivors without round 3's checks: at 24d89a1b44 both mutants print `SURVIVED` under the same driver that kills the line's two other bounds.

## Figures

<!-- figure-block: scope-line mb=0a1ef512f42cbf380049b11b096eb89c5a222ccc head=a472503fe19d7237d3701d9ac6b23e16bd0fb675 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

The block is rendered with origin/main's `tests/closure.py` overlaid on this head. origin/main (`git log 0a1ef512f42c..origin/main -- tests/closure.py` is not empty) changed that file after this branch's merge base, so the instrument reads a gate-file diff. With the merge base as the base, `python3 -I tools/pr/figure_block.py render scope-line --base 0a1ef512f42cbf380049b11b096eb89c5a222ccc --head HEAD` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, the line the gate below ran under.

### Harness, both ends

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, the head's harness file (sha1 396eb847b887af2460e75302c16f7a6b1f6d272f) run on the base's production tree (a detached worktree at 0a1ef512f42cbf380049b11b096eb89c5a222ccc) and at the head, re-taken in round 3. Rows that differ (`diff` of the two outputs), `folded/intervals scale`:

| row | base | head |
|---|---|---|
| `selfmod_independent_4kw` | 29/96 0.789 | 5/96 0.987 |
| `true_0.6` | 241/288 0.604 | 282/288 0.603 |
| `true_0.7` | 241/288 0.704 | 285/288 0.704 |
| `true_0.8` | 241/288 0.805 | 288/288 0.805 |
| `true_1.3` | 241/288 1.307 | 288/288 1.307 |
| `true_0.7_reload150` | 241/288 0.704 | 285/288 0.704 |
| `p4_follow_noise20` | 96/96 1.123 | 96/96 1.116 |
| `p4_eff0.8_noise5` | 96/96 0.563 | 96/96 0.634 |
| `p4_eff0.8_noise10` | 96/96 0.563 | 96/96 0.614 |
| `p4_follow_lag1tick` | 24/96 0.983 | 16/96 1.006 |
| `min3_running_warm_run_led` | 3/15 | 9/15 |
| `min3_running_warm_run_low` | 3/15 | 9/15 |
| `held_filling` | 96/96 0.582 | 96/96 0.650 |
| `true_0.6_max_cycle_move` | 0.012 | 0.292 |
| `sub_min_true_0.6_x288` | 90/288 0.632 | 0/288 1.000 |
| `sub_min_true_0.6_x384` | 122/384 0.614 | 118/384 0.611 |
| `sub_min_true_0.6_x480` | 154/480 0.605 | 150/480 0.603 |

- `selfmod_independent_4kw` is carry 35931f4b's install: the right scale is 1.000. It folds 24 fewer intervals: the departures base folded before the evidence are held, and dropped when the window says the draw does not follow.
- The `true_<s>` rows fold the departures base refused under the nameplate third before the evidence; each scale is within 0.01 of the base's.
- `min3_running_warm_run_led` folds the 1.9, 2.2 and 2.55 kW draws (floor 1.8 kW). `min3_running_warm_run_low` folds the same three: its low end is 0.9 kW and the floor stops at the 1.5 kW threshold, so 1.0 and 1.2 kW stay refused.
- The `p4_eff0.8_*` rows and `held_filling` are open loop (the draw is a fixed multiple of the ask whatever the scale), so base's scale falls with every fold. The head's falls less: the held rows fold against the scale they were read at and each says 0.8, where the same rows folded live compound. The mutant "replay at the live scale" is the control for that mechanism.
- The `sub_min_true_0.6_x<n>` rows are the review's, added to the harness in this round and re-run at both ends: a pump of true scale 0.6 on a 3 kW fixed-speed install whose asks (1.9 to 2.55 kW) never reach the configured minimum. No run-asked pair exists, so the evidence is pending until the window holds `draw_range.WINDOW` running samples and unobtainable after. Base folds from the first interval; the head folds nothing in 288 intervals, releases at the full window, and is within 0.003 of base's scale by 384.
- `true_0.6_max_cycle_move` is note n2's figure: at the head one cycle moves the scale by 0.292, the release of the intervals held while the window filled, each clamped by `COP_LEARNING_MAX_STEP` against the scale the previous one left. The scale after that cycle is above the true 0.6 and the run ends at 0.603.

### Sibling sites

The enumeration rule is the design note's, extended by the two functions this diff adds: `git grep -n -e flow_lift_power_floor_kw -e nameplate_power_floor_kw -e judge_floor -e judge_ratio -e "follows_ask(" -e "power_floor_kw(" -e "ask_evidence(" -- custom_components`. Code sites it returns at this head (docstring and definition lines apart), each with its disposition:

- `MeasuredCop.judge_floor` reads `power_floor_kw(draw, params)`: closed in this diff, mutant "`judge_floor`: reads no window".
- `MeasuredCop._base_folds` reads `nameplate_power_floor_kw`: closed, check "base's rule folds a departure whose ask sits exactly on the nameplate third".
- `MeasuredCop.judge_ratio` and `MeasuredCop.release` read `ask_evidence(draw)`: closed, the `judge_ratio` and `release` rows of the table above and round 2's first check.
- `accuracy.diagnostics_view` reads `power_floor_kw(draw, params)` and `follows_ask(draw)`: closed, mutant "`diagnostics_view`: the configured floor".
- `coordinator._fold_flow_lift` reads `draw_range.power_floor_kw(coord._accuracy.draw, params)`: closed, mutant "the flow-lift floor ... reading no window".
- `coordinator._async_learn_heat_span` calls `judge_floor` with `coord._accuracy.draw`: closed in round 2, the third check.
- `coordinator._fold_measured_cop` calls `judge_floor` and `judge_ratio` with the cycle's window: closed, mutants "the cycle's floor ... reading no window" and "no release".
- `draw_range.follows_ask` reads `ask_evidence`: closed, check "follows_ask is that state as a tri-state".
- `draw_range.power_floor_kw` reads `flow_lift_power_floor_kw`, its one code reader: closed, invariants (a) to (f).
- `ThermalParameters.flow_lift_power_floor_kw` returns `nameplate_power_floor_kw` where no minimum is configured: already guarded, invariant (f).

### Both ends of the input range

- Zero evidence: an empty window holds a departure (check "while draw evidence is pending ..."), and a window that never reaches evidence loses no fold (`held_full`, `held_filling`).
- On the clamp: the floor at `on_threshold_kw` (`min3_running_warm_run_low`, check (b)); the hold at its bound (check "release: the hold is bounded at 336 rows").

### Carry 2, the band measurement

`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_cop_gate_band.py` at the head (re-taken in round 3): `tests/replay/owner-2026-10-30-away.json steps=1 distinct_c=1 fit=none`; `tests/replay/synthetic-dhw-only.json steps=0 distinct_c=0 fit=none`. With `--synthetic`: `synthetic-linear steps=4 distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0`, so `fit=none` is missing data, not an instrument that cannot fit. Missing: at least 3 distinct written flow set-points strictly between gate and ceiling, each held in heat mode with a power reading inside the interval. Note n4, checked: `draw_range.diagnostics_view` publishes `DrawRange.summary()` and the ranges, no window rows, and neither fixture under `tests/replay/` has a store document among its top-level keys, so the fit cannot run on a diagnostics download as it is published today.

### Gate and ratchets

- Scoped gate, re-run whole at this head in round 3: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=0a1ef512f42cbf380049b11b096eb89c5a222ccc ./tests/run.sh`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, rc 0; among them `ALL 5688 FEATURE CHECKS PASSED`, `ALL 2731 ENTITY CHECKS PASSED`, `ALL CARD CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`.
- Goldens, in that gate run: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 0a1ef512f42cbf380049b11b096eb89c5a222ccc` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. No fixture moved, so neither claim file is touched: `git diff --stat 0a1ef512f42cbf380049b11b096eb89c5a222ccc...HEAD -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`. Four rows moved down and are re-recorded in 66389d31de: `max_class_loc`, `coordinator_attrs`, `coordinator_multiassigned_attrs` and `seam_cut_total` (`git diff 0a1ef512f42c...HEAD -- tests/structure_budgets.json` holds those four and `recorded_at`). Correction, from the round-1 review: the round-1 body said five, and the message of 66389d31de names a fifth, `class_excess_loc 17469 -> 17467`, which is wrong; that row is unchanged in the diff. Null control for the last three, taken in round 1: with the coordinator attribute put back (one assignment in `__init__`, one in `_fold_measured_cop`), `tests/structure.py` printed `FAIL` on each of the three by +1.
- `python3 tools/audit/archscore/score.py --diff 0a1ef512f42cbf380049b11b096eb89c5a222ccc` at the head: `Architecture score: dS +0.0141 IMPROVES` (`coord_footprint` and `coordinator_multiassigned_attrs` fall; no gate metric rises). The mechanism is the walking ratio's move onto `MeasuredCop`. A first cut of `MeasuredCop.release` appended through a conditional target and read `WORSENS (inadmissible: shared_inplace_writes 3->4)`; it was rewritten as a plain branch before the first commit.
- `python3 tools/pr/ci_predict.py --base 0a1ef512f42cbf380049b11b096eb89c5a222ccc` at this head: `CI PREDICT: no closures, fast, governance or instrument red predicted against 0a1ef512f42c`, and no `ADDED UNPINNED` line. At db4395285f it printed 28 `STALE PIN` lines; 38c3c4bb4d deletes those 25 `killed_by` pins and 3 triages.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: every finding item routed, 0 bad destinations.

## Unpinned sites

None at this head: `python3 tools/pr/ci_predict.py --base 0a1ef512f42cbf380049b11b096eb89c5a222ccc` prints no `ADDED UNPINNED` line (`## Figures`, "Gate and ratchets"). The 47 sites the round-2 body listed here as left to the lane were measured by it: `ci: pin killed mutants` (5cf3425240ac, 45 files under `tests/mutation_ledger/killed_by/`) pinned every site it killed and named the two it did not, `accuracy.py:1004 CMP_BOUND` and `coordinator.py:962 CMP_BOUND`. Those two are killed by round 3's checks and pinned in a472503fe1 by the ledger's own run (`## Mutation proof`, "Round 3").

Diff survivors `tools/pr/prepr.sh` named at 38c3c4bb4d, with `MUTANT_CMD` running the two `tests/features.py` blocks of `## Mutation proof` through `features_block.py`, each with its emitted prelude (the unmutated copy exits 0):

- custom_components/heatpump_optimizer/accuracy.py:942: survivor (CMP_BOUND `>`), killed in a827c3d985 by the check "base's rule folds a departure whose ask sits exactly on the nameplate third and refuses one just under it": the same command exits 1 on the mutant
- custom_components/heatpump_optimizer/accuracy.py:1077: survivor (CONST_SWAP `round(..., 4)`), killed in a827c3d985 by the check "the diagnostics publish the floor to the watt": the same command exits 1 on the mutant
- custom_components/heatpump_optimizer/accuracy.py:975: survivor (CMP_BOUND `<`), equivalent: triaged in `tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.9d967a75.json`. The comparison was triaged equivalent at its previous text (anchor d2c128b3, deleted here as a stale pin) and this branch only added an operand to its line; the neighbours of the two candidate ratios were re-measured at this head and none gives exactly 0.15

## Red checks

- `tests / mutation` at 5cf3425240ac: red on two added sites no driver killed, `accuracy.py:1004 CMP_BOUND` and `coordinator.py:962 CMP_BOUND`, after `mutation-autofix` pinned the sites it killed. Repaired here by one killing check per site (`## Mutation proof`, "Round 3"). The root-cause trigger's question, whether a cheaper detector could have run: yes for one site, and only partly for the other.
  - `coordinator.py:962 CMP_BOUND` is a mutant `tools/pr/prepr.sh`'s own mutant step draws, and the step never reached it. `python3 tools/audit/seat/mutant_run.py --diff 0a1ef512f42cbf380049b11b096eb89c5a222ccc...HEAD --list` prints it as line 48 of the list, and the step runs the first `MUTANT_MAX` (40) in file order. The cheaper detector is that step with `MUTANT_MAX=0` on a diff the cap truncates. Its standing cost is one driver run per mutant past the cap: this round's one-block driver took 2 min 50 s for five runs (the null and four mutants) on a 4-core container, and the list holds more than twice the cap.
  - `accuracy.py:1004`'s surviving comparison is the second on its line (`0.0 <=`). `mutant_run.py`'s CMP_BOUND moves only the first comparison of a line (`i >= over` there, killed since round 1), so no local diff-mode run draws it at any cap. The detector that does is `tests/mutation_table.py --pin-killed --scripts tests/features.py`, the lane's own measurement narrowed to one driver: it ran to the end on this seat at a275b26db9 (a472503fe1's message), where the round-1 run over every driver was stopped (`## Friction`).
  - Process state: (c), followed and not producing the intended result. Rounds 1 and 2 ran the mutant step, answered each survivor it printed, and its `no survivor among the diff's first 40 mutant(s)` reads as the diff's survivors being answered while the diff holds mutants past the cap and comparisons the operator does not move. No countermeasure is built in this pull request: changing what the step draws or prints changes what a fixer's handoff must do, which is `fixer.md` step 2 and the owner's, and the cause is established in its own seat (`defect-root-cause.md`). It is carried under `## Friction`.

No CI run exists at this head; `ci_predict.py` (`## Figures`) predicts no red.

## Forward-carry

- Departure 1, where the release runs (behind the freeze gate in `_fold_measured_cop`, not in `_learn_measured_cop`): the design note's call site is refused by the #1523 class check, and the note is silent on a release under a freeze. Pending the orchestrator's ruling on the departure; the control is the mutant "the release ahead of the freeze gate" under `## Mutation proof`. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Departure 2, a replay does not feed the capacity envelope: a held departure asked at or above 0.95 of nameplate fed it at its own tick when base folded it, and feeds nothing when replayed. Feeding it truthfully needs the held row to carry its own outdoor bucket and draw into `_fold_capacity_envelope`. Pending the orchestrator's ruling on whether that is owed; the control is the check "a replayed interval folds the scale and not the capacity envelope". Carry: R10-COP-LEARNER-DRAW-FLOOR
- Note n2, the one-cycle scale move: the instrument is the harness row `true_0.6_max_cycle_move` (`## Figures`); a release folds every held row in one cycle, each clamped by `COP_LEARNING_MAX_STEP` alone. Whether a release is bounded per cycle is the owner's: bounding it delays the replay it was held for. Re-measure with that row at the deciding head. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Design decision, owner: where the evidence is unobtainable a departure keeps base's rule (built here), or is held too. Built arm: a pump that sets its own power under flat asks folds base's departures until its asks first span `FOLLOW_ASK_SPAN`. Other arm: a flat-ask install never folds a departure and invariant (h) is given up. Controls: harness rows `held_full` and `selfset_flat`. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Review finding (round 1), the wait on an install whose plan never asks at or above its configured minimum: it learns nothing from a departure until the window is full, where base learned from the first interval; the state is pending until `draw_range.WINDOW` running samples exist, then unobtainable, and the release catches up in one cycle. That is the approved state function. It bears on the owner's pending decision on the unobtainable arm (the item above); the control is the harness rows `sub_min_true_0.6_x288`, `sub_min_true_0.6_x384` and `sub_min_true_0.6_x480` (`## Figures`), to be re-measured at the deciding head. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Design decision, owner: the cap reads run-asked draws only, so an install with an overstated minimum that the plan never asks at or above keeps base's refusal and reads `duty_floor`; the remedy there is the configured figure. Lowering the floor for it lowers it for every duty-cycling install: harness rows `min3_running_warm_own`, `fixed3_duty50_warm_own`, `fixed3_duty70_warm_own` are the control. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Residual, measured and not built (no finding in the brief asks for it): before the evidence exists an interval within `COP_ASK_TOLERANCE` of its ask folds on a pump that sets its own power. Harness rows `selfmod_independent` and `selfmod_independent_4kw` at the head show it (5 folds, scale 0.987 where 1.000 is right). Holding those too holds every interval of every install until `MIN_SAMPLES` run-asked pairs exist. Carry: R11-INTAKE-R10-RESIDUE
- Design decision, orchestrator: group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS (0c692c86d2), the metered floor, reads the same window for the opposite end (asks at or under the configured floor). The pair reader is `DrawRange._run_asked` and the floor is `draw_range.power_floor_kw`; whichever lands second takes its low end from the first's reader, never a second statistic. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS
- Carry 2, the band measurement, stays open on named owner data: a diagnostics download with the week of debug data on, from a set-point install whose pump ran across the band (at least 3 distinct written flow set-points strictly between gate and ceiling, each held in heat mode with a power reading inside the interval). Decision rule, fixed by the design: `max_resid_kw` above `draw_range.AGREE_TOLERANCE` x the fitted draw at the ceiling is non-linear and goes to a new design; at or below it, a recorded refusal with the number. Flat-price null: a flat-price bundle must print `fit=none`. Instrument: `dev/audit/harnesses/r10_cop_gate_band.py`. Carry: R11-INTAKE-R10-RESIDUE
- Note n4, checked: a diagnostics download publishes no running-draw window rows (`draw_range.diagnostics_view` is `DrawRange.summary()` plus the ranges), so the band fit cannot run on the stored `DrawRange.commands` without either the debug week or a change that publishes those rows. Carry: R11-INTAKE-R10-RESIDUE
- Note n9: when fix 3 adds a `COP_REFUSED_*` literal, the same pull request owes its `health.cop_reason_` words in all three languages, or the registry check in `tests/card.mjs` ("copCodes") fails. Fix 3's predicate belongs in `MeasuredCop.judge_ratio`, which is now an instance method on a `CopInterval`. Carry: R11-INTAKE-R10-RESIDUE
- Four harnesses stop with a traceback on origin/main 9fdba3b8547f, before this diff, each run as `PYTHONPATH=tests/hastub:custom_components:tests python3 <path>`: `dev/audit/harnesses/r10_heat_meter.py` (`'Gate' object has no attribute '_config'`), `dev/audit/harnesses/r10_thermal_power_option.py` (`'Gate' object has no attribute '_fold_cop_evidence'`), `dev/audit/harnesses/r10_cop_gate.py` (`cop_observability() got an unexpected keyword argument 'follows'`) and `dev/audit/rounds/round9/D7/s2/learner_table.py` (`_async_learn_house_heat_loss() missing 1 required positional argument: 'interval'`). Their stubs predate later signatures, so they are not ported here; a seat that re-runs one ports it first. `dev/audit/rounds/round9/D7/s2/learner_gates.py` runs, and its `RESULT` lines but the machine-load ones are identical at the base and at this head (its assignment to the coordinator's old ratio attribute is inert now). Carry: R11-INTAKE-R10-RESIDUE

## Friction

designer.md: unenforced: the approved note reuses `_fold_cop_evidence` for the replay and calls `release` from `_learn_measured_cop`, and neither its evidence plan nor its review ran the #1523 class check or traced that function's tail, which reads the present cycle's draw, command and outdoor bucket. The census refused the call site in the fixer's first scoped gate run, inside `tests/features.py`; the tail was found by reading `_fold_capacity_envelope`, and no check reads it. Carry: R11-INTAKE-R10-RESIDUE
fixer.md: contradiction: step 17 has the architect note followed and a departure raised, not made; step 14 forbids the allow-list entry that would have kept the note's call site. With no live seat to ask, the route was changed and the departure is raised in this body. Carry: R10-COP-LEARNER-DRAW-FLOOR
fixer.md: cost: in round 1 `tests/mutation_table.py --pin-killed --base origin/main --jobs 3` over the diff's unpinned sites was stopped on a 4-core container once its baselines and null control had run and before any site had finished; the sites were left to `mutation-autofix`, as `ci-autofix.md` allows, and the lane went red on two of them (`## Red checks`). Carry: dismissed: the lane measured every site and round 3 repaired its two survivors
fixer.md: unenforced: step 2 says the diff's survivors are the fixer's before the handoff and that the mutant step draws only the first 40 mutants of added lines; nothing says a diff holding more than 40, or a line holding more than one comparison, leaves sites that step never draws. The control is `python3 tools/audit/seat/mutant_run.py --diff <merge base>...HEAD --list` against the cap, and a line of two comparisons mutated by hand as in `## Mutation proof`, "Round 3". Re-measure the list's length at the deciding head. Carry: R11-INTAKE-R10-RESIDUE
figure_block.py: cost: the `scope-line` block renders `MODE: FULL` for a branch whose merge base predates a change of `tests/closure.py` on main, because the base's copy is overlaid on the head and then reads as the branch's own diff; the same head against its merge base renders `MODE: SCOPED`. A fixer told not to merge main without a conflict hands off a body whose registered mode line contradicts its gate run. Carry: R11-INTAKE-R10-RESIDUE
