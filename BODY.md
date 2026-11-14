R10-COP-LEARNER-DRAW-FLOOR, built on the approved design (`design.md` at 94d2c9f06576693b31996d21d18af241d41640b2 of design/R10-COP-LEARNER-DRAW-FLOOR; `Design review: approve`, design-verdict at 732212c268). Three carries on the COP learner's one judgement seam, `MeasuredCop` in `accuracy.py`.

What ships, by carry:

- **Carry 0 (84e73ec4), the capped floor.** `draw_range.power_floor_kw(draw, params)` is the one floor `MeasuredCop.judge_floor`, `coordinator._fold_flow_lift` and `accuracy.diagnostics_view` read, each on the same window object. It is `flow_lift_power_floor_kw` capped by the low end (`LOW_PERCENTILE`) of the draws metered under a run ask, never under `on_threshold_kw`. A run ask is an ask at or above the window's configured minimum and above zero: `DrawRange._run_asked`, the pair reader `follows_ask` built inline and now shares. Invariants (a) to (f) of the design are each a check in `tests/features.py`.
- **Carry 1 (35931f4b), hold-then-replay.** `draw_range.ask_evidence` returns one of four states; `follows_ask` is that state as a tri-state, results unchanged. `MeasuredCop.judge_ratio` is an instance method on the interval's row (`accuracy.CopInterval`): a departure beyond `COP_ASK_TOLERANCE` is held while the evidence is pending and reads `COP_REFUSED_NO_EVIDENCE`, no new code. `MeasuredCop.release` is the one place a held row is judged: all fold on follows, none on does-not-follow, base's rule where the evidence is unobtainable, and while it is pending base's rule for a row older than `COP_HOLD_HORIZON_S` (a week) or pushed out of a hold of `draw_range.WINDOW` rows. A released row folds against the scale it was read at. `diagnostics_view` gains `held_intervals`.
- **Carry 2 (R10-COP-GATE-E band), measurement, no build.** Re-run at this head, `dev/audit/harnesses/r10_cop_gate_band.py` reads `fit=none` on both fixtures under `tests/replay/` and its `--synthetic` control fits. The carry stays open on the named owner data (`## Forward-carry`).
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

a827c3d985b240fabcc83215e0d35a9692e8fca9, on merge base 9fdba3b8547f9762438dc19b98b310a63d34dcb1. Measured 2026-11-14 18:55 UTC. At that time origin/main is 5b8f05ba4e30d248b9b4a1f4c44fd8e62148c5db, and `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0), so main is not merged; the train re-proves the head on the current main.

## Mutation proof

Failing test first: the block from `R.section("R10-COP-LEARNER-DRAW-FLOOR` to `R.section("R10-COP-GATE (#2262)` of `tests/features.py`, run by `tools/audit/seat/features_block.py` with its emitted prelude, on the base's production files stops at `ImportError: cannot import name 'CopInterval'`; on this head it prints `ALL 33 FEATURES BLOCK PASSED`.

Hand mutants, each applied alone to a detached worktree at db4395285f (the production files are byte-identical at the head: `git diff --stat db4395285f HEAD -- custom_components` prints nothing) and restored, driven by that block and by the block before it (from `# silence the learner. Synthetic numbers only.`). The unmutated tree fails no check. Every mutant fails at least one; the first failing check is named.

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

## Null control

- Harness, unwarmed rows: every `min1_*` and `min3_*` row, `selfmod_independent`, `selfmod_matched`, `selfset_hourly`, `selfset_three_hour`, `selfset_flat`, `fixed3_duty50`, `fixed3_duty70`, `fixed3_duty85`, `liveness`, `true_0.7_4kw` and `p4_follow_noise10` print the same line at the base and at the head (`diff` of the two outputs lists only the rows under `## Figures`).
- The cap moves nothing without run-asked evidence: `min3_running_warm_own`, `min1_duty_cycled_warm_own`, `fixed3_duty50_warm_own` and `fixed3_duty70_warm_own` read the same at both ends.
- The hold loses nothing where no evidence ever arrives: `held_full` and `held_filling` fold 96 of 96 at both ends.
- A window with no run-asked pairs, no window, and a window keyed to another range return `flow_lift_power_floor_kw` bit for bit (checks (c), (d), (e)).
- With no draw window (`_learn_measured_cop()`, as the stubs and the heat-metered harnesses call it) the state is unobtainable, nothing is held and base's rule stands (check "while draw evidence is pending a departure is held on any nameplate ... with no window base's rule stands").
- The mutation driver's own null: the unmutated worktree fails no check of the two blocks.

## Figures

<!-- figure-block: scope-line mb=9fdba3b8547f9762438dc19b98b310a63d34dcb1 head=a827c3d985b240fabcc83215e0d35a9692e8fca9 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

The block is rendered with origin/main's `tests/closure.py` overlaid on this head. origin/main (5b8f05ba4e30) changed that file after this branch's merge base, so the instrument reads a gate-file diff. With the merge base as the base, `python3 -I tools/pr/figure_block.py render scope-line --base 9fdba3b8547f9762438dc19b98b310a63d34dcb1 --head HEAD` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, the line the gate below ran under.

### Harness, both ends

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, the head's harness file run on the base's production tree (a detached worktree at 9fdba3b8547f9762438dc19b98b310a63d34dcb1) and at the head. Rows that differ, `folded/intervals scale`:

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

- `selfmod_independent_4kw` is carry 35931f4b's install: the right scale is 1.000. It folds 24 fewer intervals: the departures base folded before the evidence are held, and dropped when the window says the draw does not follow.
- The `true_<s>` rows fold the departures base refused under the nameplate third before the evidence; each scale is within 0.01 of the base's.
- `min3_running_warm_run_led` folds the 1.9, 2.2 and 2.55 kW draws (floor 1.8 kW). `min3_running_warm_run_low` folds the same three: its low end is 0.9 kW and the floor stops at the 1.5 kW threshold, so 1.0 and 1.2 kW stay refused.
- The `p4_eff0.8_*` rows and `held_filling` are open loop (the draw is a fixed multiple of the ask whatever the scale), so base's scale falls with every fold. The head's falls less: the held rows fold against the scale they were read at and each says 0.8, where the same rows folded live compound. The mutant "replay at the live scale" is the control for that mechanism.
- `true_0.6_max_cycle_move` is note n2's figure: at the head one cycle moves the scale by 0.292, the release of the intervals held while the window filled, each clamped by `COP_LEARNING_MAX_STEP` against the scale the previous one left. The scale after that cycle is above the true 0.6 and the run ends at 0.603.

### Both ends of the input range

- Zero evidence: an empty window holds a departure (check "while draw evidence is pending ..."), and a window that never reaches evidence loses no fold (`held_full`, `held_filling`).
- On the clamp: the floor at `on_threshold_kw` (`min3_running_warm_run_low`, check (b)); the hold at its bound (check "release: the hold is bounded at 336 rows").

### Carry 2, the band measurement

`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_cop_gate_band.py` at the head: `tests/replay/owner-2026-10-30-away.json steps=1 distinct_c=1 fit=none`; `tests/replay/synthetic-dhw-only.json steps=0 distinct_c=0 fit=none`. With `--synthetic`: `synthetic-linear steps=4 distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0`, so `fit=none` is missing data, not an instrument that cannot fit. Missing: at least 3 distinct written flow set-points strictly between gate and ceiling, each held in heat mode with a power reading inside the interval. Note n4, checked: `draw_range.diagnostics_view` publishes `DrawRange.summary()` and the ranges, no window rows, and neither fixture under `tests/replay/` has a store document among its top-level keys, so the fit cannot run on a diagnostics download as it is published today.

### Gate and ratchets

- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=9fdba3b8547f9762438dc19b98b310a63d34dcb1 ./tests/run.sh` at db4395285f: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, rc 0; among them `ALL 5618 FEATURE CHECKS PASSED`, `ALL 2725 ENTITY CHECKS PASSED`, `ALL CARD CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`.
- The two commits after db4395285f change `tests/features.py` and files under `tests/mutation_ledger/` only (`git diff --stat db4395285f HEAD -- custom_components dev` prints nothing). `python3 tests/closure.py select --diff db4395285f` names two scripts for them, `tests/entities.py` and `tests/features.py`, each re-run at the head: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 5621 FEATURE CHECKS PASSED`, rc 0; `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2725 ENTITY CHECKS PASSED`, rc 0.
- Goldens, in that gate run: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 9fdba3b8547f9762438dc19b98b310a63d34dcb1` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. No fixture moved, so neither claim file is touched: `git diff --stat 9fdba3b8547f9762438dc19b98b310a63d34dcb1...HEAD -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`. Five rows moved down and are re-recorded in 66389d31de, whose message names each: `class_excess_loc`, `max_class_loc`, `coordinator_attrs`, `coordinator_multiassigned_attrs` and `seam_cut_total`. Null control for the last three: with the coordinator attribute put back (one assignment in `__init__`, one in `_fold_measured_cop`), `tests/structure.py` printed `FAIL` on each of the three by +1.
- `python3 tools/audit/archscore/score.py --diff 9fdba3b8547f9762438dc19b98b310a63d34dcb1` at the head: `Architecture score: dS +0.0139 IMPROVES` (`coord_footprint` and `coordinator_multiassigned_attrs` fall; no gate metric rises). The mechanism is the walking ratio's move onto `MeasuredCop`. A first cut of `MeasuredCop.release` appended through a conditional target and read `WORSENS (inadmissible: shared_inplace_writes 3->4)`; it was rewritten as a plain branch before the first commit.
- `python3 tools/pr/ci_predict.py --base 9fdba3b8547f9762438dc19b98b310a63d34dcb1` at the head: `no closures, fast, governance or instrument red predicted against 9fdba3b8547f`, and one `ADDED UNPINNED` line per site under `## Unpinned sites`. At db4395285f it printed 28 `STALE PIN` lines; 38c3c4bb4d deletes those 25 `killed_by` pins and 3 triages.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: every finding item routed, 0 bad destinations.

## Unpinned sites

Every site below is on a line this diff adds or rewrites; none is pinned by hand (`ci-autofix.md`), and `tests/mutation_table.py --pin-killed` did not finish on this seat (`## Friction`), so each is `unmeasured` by that instrument and left to the lane. The diff's survivors under prepr's mutant step are listed after them.

- custom_components/heatpump_optimizer/accuracy.py:874 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:874 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:922 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:922 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:922 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:936 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:942 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:942 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:942 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:970 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:975 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:977 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:980 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:997 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:999 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:1001 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:1004 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:1004 CMP_BOUND*3: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:1004 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/accuracy.py:1009 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:962 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:962 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5344 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5344 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5370 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5370 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5377 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5422 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5894 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:246 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:246 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:246 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:489 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:492 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:492 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:493 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:495 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:495 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:500 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:500 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:512 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:534 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:534 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:537 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:537 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:540 CLAMP_DROP*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/draw_range.py:540 RETURN_DEL: pinned by mutation-autofix

Diff survivors `tools/pr/prepr.sh` named at 38c3c4bb4d, with `MUTANT_CMD` running the two `tests/features.py` blocks of `## Mutation proof` through `features_block.py`, each with its emitted prelude (the unmutated copy exits 0):

- custom_components/heatpump_optimizer/accuracy.py:942: survivor (CMP_BOUND `>`), killed in a827c3d985 by the check "base's rule folds a departure whose ask sits exactly on the nameplate third and refuses one just under it": the same command exits 1 on the mutant
- custom_components/heatpump_optimizer/accuracy.py:1077: survivor (CONST_SWAP `round(..., 4)`), killed in a827c3d985 by the check "the diagnostics publish the floor to the watt": the same command exits 1 on the mutant
- custom_components/heatpump_optimizer/accuracy.py:975: survivor (CMP_BOUND `<`), equivalent: triaged in `tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.9d967a75.json`. The comparison was triaged equivalent at its previous text (anchor d2c128b3, deleted here as a stale pin) and this branch only added an operand to its line; the neighbours of the two candidate ratios were re-measured at this head and none gives exactly 0.15

## Red checks

- `mutation` at a827c3d985b2: red by construction on the 47 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. No cheaper detector exists: a pin is that lane's measurement of each site against every driver whose closure reaches it, and the same measurement run here (`tests/mutation_table.py --pin-killed`) costs the lane's whole run on a smaller machine (`## Friction`).

No CI run exists at this head; `ci_predict.py` (`## Figures`) predicts no other red.

## Forward-carry

- Departure 1, where the release runs (behind the freeze gate in `_fold_measured_cop`, not in `_learn_measured_cop`): the design note's call site is refused by the #1523 class check, and the note is silent on a release under a freeze. Pending the orchestrator's ruling on the departure; the control is the mutant "the release ahead of the freeze gate" under `## Mutation proof`. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Departure 2, a replay does not feed the capacity envelope: a held departure asked at or above 0.95 of nameplate fed it at its own tick when base folded it, and feeds nothing when replayed. Feeding it truthfully needs the held row to carry its own outdoor bucket and draw into `_fold_capacity_envelope`. Pending the orchestrator's ruling on whether that is owed; the control is the check "a replayed interval folds the scale and not the capacity envelope". Carry: R10-COP-LEARNER-DRAW-FLOOR
- Note n2, the one-cycle scale move: the instrument is the harness row `true_0.6_max_cycle_move` (`## Figures`); a release folds every held row in one cycle, each clamped by `COP_LEARNING_MAX_STEP` alone. Whether a release is bounded per cycle is the owner's: bounding it delays the replay it was held for. Re-measure with that row at the deciding head. Carry: R10-COP-LEARNER-DRAW-FLOOR
- Design decision, owner: where the evidence is unobtainable a departure keeps base's rule (built here), or is held too. Built arm: a pump that sets its own power under flat asks folds base's departures until its asks first span `FOLLOW_ASK_SPAN`. Other arm: a flat-ask install never folds a departure and invariant (h) is given up. Controls: harness rows `held_full` and `selfset_flat`. Carry: R10-COP-LEARNER-DRAW-FLOOR
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
fixer.md: cost: `tests/mutation_table.py --pin-killed --base origin/main --jobs 3` over the diff's unpinned sites was stopped on a 4-core container once its baselines and null control had run and before any site had finished; the sites are left to `mutation-autofix`, as `ci-autofix.md` allows. Carry: dismissed: the lane exists and the diff's survivors are measured by prepr's mutant step
figure_block.py: cost: the `scope-line` block renders `MODE: FULL` for a branch whose merge base predates a change of `tests/closure.py` on main, because the base's copy is overlaid on the head and then reads as the branch's own diff; the same head against its merge base renders `MODE: SCOPED`. A fixer told not to merge main without a conflict hands off a body whose registered mode line contradicts its gate run. Carry: R11-INTAKE-R10-RESIDUE
