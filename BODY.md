Part of #2499.

The slab estimate on an install with no floor-return sensor used to advance open-loop along the previous plan's `slab_temp_trajectory`. That is the heat the plan COMMANDED. A pump drawing less left a too-warm slab, and the house heat-loss learner then booked the difference as fabric loss. `house_heat_loss_scale` climbed, and the plan booked more heat each day.

The fix: where a power entity exists, `coordinator._propagated_slab` replays the elapsed interval through the house learner's own `_replay_interval`, at the metered space draw `draw_range.space_draw_kw`. It returns `None` when a resistive element shares the meter, and `0.0` while the observed mode heats no rooms. A reading at or below `draw_range.running_kw`'s floor is standby, not heat. With no reading, no previous sample, a non-positive gap, or a gap past `HOUSE_LOSS_MAX_SAMPLE_HOURS`, it falls back to the plan's trajectory, the old behaviour. An install with no power entity is unchanged.

This body is a re-cut. Every figure in it was taken in this pass.

What this pass changed, to pay the structure ratchet in code rather than in its budget:

- The legionella guard's per-cycle sequence (observer, switch read, cycle follower, ceiling notice, `hours_since`) moves into `LegionellaGuard.async_observe` in `legionella.py`, the module that owns the cycle. The tank block goes back into `_update_current_state`, and `_track_dhw` is deleted.
- The interval learners (lower floor, then house, then observed COP) and the slab seed run through one learning-seam unit, `_async_learn_interval`. It holds the ordering that the house learner's baseline overwrite imposes. Before this, that ordering was a comment in `_update_current_state`. `_async_learn_interval` reads the baseline time itself, so `_update_current_state` no longer reads learner state. `_propagated_slab` is mapped `learning` in `tests/seam_map.json`, the seam it replays through.
- Fixed a defect this pass introduced: `_ctx_of(self).publish(..., dhw_hours_since_legionella=await ...)` bound the context before the await, so a state that an ECL110 message published inside the cycle follower was overwritten. The await now lands in a local first. Caught by `I1/I3: an ECL110 message and a peak-guard flip landing inside _update_current_state's learner awaits survive its later publishes`.
- Added the check `#2499: a tank at the disinfection temperature resets the legionella timer through the coordinator's cycle; a cooler reading or none leaves it unset`. Without it, mutant M3 below survived.
- Merged PR head 7afd9452b7ac703bfa9f6ef88033120189d39d4b. The handoff tip it was dispatched from, 1193fd228, lacks the round-3 checks for the immersion latch and the observed mode, which are on the PR head. The merge was clean and touched only `tests/features.py`.

Alternatives that lost:

- Raise `seam_cut_total` under the mandate. A payment existed, so a raise was not owed.
- Map `_track_dhw` to `core`. That moves the metric with no change to the code.
- Call `_propagated_slab` before the learners. That changes the parameters the replay runs with.
- Let `_async_learn_interval` always propagate the slab and have the caller drop the result. That costs an off-loop replay on every cycle where the slab is sensed.

## Head

fe96b2289e66d9dfe188caa507f3c9dc02ea762a, merge base 12b222007b67c4bc0ac931a509d8b1385c6458cf. At 2026-10-25T04:26:47Z (fetched by this seat) `origin/main` is ab00437c94bd8d8ca7b47b69095c47535f3e645a. `git merge-tree --write-tree origin/main HEAD` exits 0, so per `fixer.md` step 6 the branch is not re-merged. `python3 tests/structure.py` on that merge tree prints `STRUCTURE RATCHET PASSED`. Mutants and the harness ran at 378fba19fa34e2c81c1f629d259cdff604527a94 and 3fd107bd7405c8e561e78f1e4a1ee3702839b1f6. Rule: `git diff --stat 3fd107bd7 fe96b2289 -- custom_components dev/audit/harnesses` prints nothing, and fe96b2289 adds only the legionella check above to 378fba19f.

Carry destinations were read from `handoff/audit-r10-roster` at 801bc42b3bf605963110accebfb9dad8de59311a, whose groups hold each `## Forward-carry` item in their `carry`.

## Mutation proof

Each mutant ran in its own detached worktree at 378fba19f with `PYTHONPATH=tests/hastub python3 tests/features.py`. The unmutated tree printed `ALL 4369 FEATURE CHECKS PASSED` (rc=0).

| mutant | site | result | checks red |
|---|---|---|---|
| M1 | `_propagated_slab`: `if kw is not None and ...` -> `if False and ...` | `3 of 4369 FEATURE CHECKS FAILED` | `#2499: a metered pump that drew nothing leaves the slab cooling, not at the plan's commanded 25 degC`; `the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW`; `a gap of exactly the sample window still advances the slab by the meter; a minute past it follows the plan` |
| M2 | `draw_range.running_kw`: `drawn_kw > floor` -> `drawn_kw > 0.0` | `3 of 4369` | `a standby draw under the running floor heats nothing`; `a draw at the running floor is standby, not heat`; `a learned idle draw above the fixed floor raises it to IDLE_MARGIN times the idle draw` |
| M3 | `LegionellaGuard.async_observe`: `if dhw_temp is not None:` -> `if False:` | `ALL 4369 ... PASSED` (survived); with the new check, `1 of 4370 FEATURE CHECKS FAILED` | `#2499: a tank at the disinfection temperature resets the legionella timer through the coordinator's cycle; a cooler reading or none leaves it unset [hot=None cool=None none=None]` |
| M4 | `_update_current_state`: `if tank is not None and (frozen := ...)` -> `if False and ...` | `1 of 4369` | `#2499: a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither` |
| M5 | `_async_learn_interval`: `... if slab_unsensed else None` -> `... if False else None` | `7 of 4369` | `D12-s1-01: and the slab seed follows the previous plan, not the one-time room+1 K seed`, `without a power meter the slab follows the plan (null control)`, and five more `#2499` slab checks |
| M6 | `_propagated_slab`: `shared=...` -> `shared=False` | `1 of 4369` | `#2499: an immersion element latched on the pump's meter leaves the slab on the plan's trajectory, not advanced by its resistive kW as space heat [slab=24.170]` |
| M7 | `_propagated_slab`: `space_served=...` -> `space_served=True` | `1 of 4369` | `#2499: a pump observed in a hot-water-only mode books 0 kW of space heat (the slab cools as with the pump off) ...` |

The M3 re-run and its control both used the committed `tests/features.py` at fe96b2289: the worktree at 378fba19f with that file copied in printed `ALL 4370 FEATURE CHECKS PASSED` (rc=0).

## Null control

- Comment-only edit (`# null control` on the `tank =` line of `_update_current_state`), same command, same head: `ALL 4369 FEATURE CHECKS PASSED` (rc=0).
- M3 shows that the null control is not vacuous: before the new check, the reading branch could be deleted with every check green.
- Harness arms with no shortfall to correct read on the truth at both ends: `null` 1.011 -> 0.98 (true 1.0), `true0.5` 0.511 -> 0.504 (true 0.5), `owner_ideal` 0.611 -> 0.611 (true 0.6). `nometer_half`, the arm with no power entity, is identical at both ends, which is the fix leaving such an install alone.

## Figures

- Harness: `dev/audit/harnesses/r10_demand_overbook.py` (git blob 384f78251a372a49631adab3cab96896ff0d5d61, unchanged by this pass), copied out of the tree under its own basename. Run as `PYTHONPATH=tests/hastub:custom_components:tests python3 <copy>/r10_demand_overbook.py --dp`, with the base end in a worktree at 12b222007 (643 s) and the head end at 3fd107bd7 (521 s). `scale` is the learned `house_heat_loss_scale`. `plan/deliv` is the 12-h plan energy at 00:00 and 12:00, summed per day, over the electric energy delivered, days 2..end. `samples` is the house learner's accepted samples.

| arm (true scale) | base scale | head scale | base plan/deliv | head plan/deliv | samples base/head |
|---|---|---|---|---|---|
| owner_i01 (0.6) | 1.221 | 0.616 | 1.674 | 0.854 | 323/350 |
| owner_i01_spread (0.6) | 1.584 | 0.733 | 1.847 | 0.666 | 399/391 |
| owner_i03 (0.6) | 1.0 | 1.0 | 1.642 | 1.084 | 0/0 |
| meter_half (1.0) | 2.041 | 1.289 | 1.711 | 1.097 | 166/187 |
| meter_sat3 (1.0) | 1.099 | 0.994 | 1.25 | 1.194 | 282/279 |
| slab3x (1.0) | 0.911 | 0.888 | 0.953 | 0.938 | 287/287 |
| nometer_half (1.0) | 1.858 | 1.858 | 1.908 | 1.908 | 287/287 |
| owner_i01_oracle (0.6) | 0.619 | 0.619 | 0.854 | 0.854 | 346/346 |
| meter_half_oracle (1.0) | 1.051 | 1.051 | 1.016 | 1.016 | 201/201 |

  The `_oracle` arms seed the TRUE slab, the upper bound. The head reaches it on owner_i01: 0.616 against 0.619. meter_half sits above its oracle, 1.289 against 1.051, and that gap is the share of the bias this fix leaves. DP reference (`--dp`, owner_i01's last 12-h window, on the learned model): base plan 6.95 kWh against DP 5.38; head plan 5.27 against DP 3.75. This is one window, a reference and not a proof.
- Structure: `PYTHONPATH=tests/hastub python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at fe96b2289. Against main 12b222007 the recorded rows are `seam_cut_total` 420 -> 419, `max_class_loc` 8449 -> 8417, `class_excess_loc` 18209 -> 18208 and `duplication_copies` 17 -> 16. Every other row is main's, and nothing is raised. The control is the round-4 head merged with this base, e70c0e74e, which prints `seam_cut_total=424`. The crossing pairs come from `seam_metrics`' own partition: against main, `_track_dhw` added (`dhw`, `publish`) and (`dhw`, call `_track_dhw`); `_propagated_slab` as `core` added (`learning`, `_last_house_sample_time`) and (`learning`, call `_replay_interval`). At fe96b2289 the only crossing added is (`learning`, `_last_house_sample_time`), the slab seed's return value. Removed: the core calls to `_async_learn_lower_floor_loss`, `_async_learn_house_heat_loss` and `_learn_measured_cop`. Added: the call to `_async_learn_interval`.
- Architecture: `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff 12b222007b67c4bc0ac931a509d8b1385c6458cf 378fba19fa34e2c81c1f629d259cdff604527a94` prints `Architecture score: dS +0.3255 WORSENS (inadmissible: coord_footprint 2463->2464)`. The same command at the before tree, e70c0e74e, prints `dS +0.3249 WORSENS (inadmissible: coord_footprint 2463->2465)`, so this pass reads better, not worse. See `## Architecture score`.
- Predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at fe96b2289 prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 12b222007b67` and `7 unpinned site(s) the diff adds` (see `## Unpinned sites`).
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` The run at fe96b2289, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`, prints the same mode line and `1 TEST SCRIPT(S) FAILED`: `tests/entities.py`, `2 of 2440 ENTITY CHECKS FAILED` (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`). Control: `PYTHONPATH=tests/hastub python3 tests/entities.py` at the base 12b222007 prints the same `2 of 2440 ENTITY CHECKS FAILED` with the same two names, so they are this environment's and not this diff's. Every other script in scope printed `ok`, `tests/stress.py` and `tests/features.py` included. Golden, same run: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 12b222007b67c4bc0ac931a509d8b1385c6458cf` and `no committed fixture is stale`. Nothing is claimed: `git diff --quiet 12b222007 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0.
- Class census (`fixer.md` step 8). Rule: `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py` lists each place where a plan prediction stands in for an unsensed state. At fe96b2289 it returns the definition (`coordinator.py:1969`) and two calls. `coordinator.py:1012`, `slab_temp_trajectory`, is the fallback inside `_propagated_slab`, closed in this diff. `coordinator.py:6388`, `dhw_temp_trajectory`, is the tank seed, a distinct case: no learner replays from it. It is carried below.

## Architecture score

- `coord_footprint` 2463 -> 2464: `_async_learn_interval` captures the house learner's baseline time before the learner overwrites it (`prior_at = self._last_house_sample_time`), one statement. Each way to drop it costs more. Passing it in from `_update_current_state` re-adds a seam crossing. Computing the seed unconditionally costs an off-loop replay on every cycle where the slab is sensed. The round-4 tree was at 2465.

## Unpinned sites

`ci_predict.py` lists 7 `ADDED UNPINNED` sites at fe96b2289. They are lines this pass added or moved, all under `custom_components/`, the lane `mutation-autofix` pins. The stale `_update_current_state BOOLOP 8f67bdf0` pin for the moved COP line was deleted by hand, as the predictor instructs.

- `custom_components/heatpump_optimizer/coordinator.py:5442 BOOLOP` (the COP save cadence, moved from `_update_current_state` unchanged): pinned by `mutation-autofix`. Its previous pin was a killed one.
- `custom_components/heatpump_optimizer/coordinator.py:5444 RETURN_DEL` (`_async_learn_interval`'s return): value checks, M5's seven, which drive that line's conditional. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/coordinator.py:6486 BOOLOP` and `custom_components/heatpump_optimizer/coordinator.py:6486 GUARD_OFF` (the tank guard): value check `a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither` (M4). Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/coordinator.py:6511 GUARD_OFF` (`if seed is not None:`): value checks, M5's. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:482 GUARD_OFF`: value check `a tank at the disinfection temperature resets the legionella timer through the coordinator's cycle; ...` (M3, with the null run beside it). Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/legionella.py:487 RETURN_DEL` (`return self.hours_since()`): pinned by `mutation-autofix`.

## Red checks

- `tests / mutation`: predicted red until `mutation-autofix` pins the 7 sites above (`ci-autofix.md`: once the PR exists, wait for the bot commit). The cheaper detector exists and ran here: `tools/pr/ci_predict.py` lists the sites statically, at nil standing cost.

## Forward-carry

- No power entity, so a draw shortfall cannot be told from UA. Harness arm `nometer_half`: scale 1.858 and plan/deliv 1.908 at both ends. The health surface must report the learned scale as unobservable on such an install. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-UX-HEALTH
- A standby-drawing, under-delivering pump gives the house learner no evidence. Harness arm `owner_i03`: 0 samples at both ends, because `COP_TRACKING_ERROR_GATE` in `_interval_space_power` refuses every interval. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-LEARNER-DEFAULT
- Optimality lead, not a proof: on its own learned model the plan books more than the relaxed DP optimum at both ends (`--dp`: 6.95 against 5.38, 5.27 against 3.75). Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-BUFFER-STORE
- The `dhw_temp_trajectory` tank seed is open-loop (class census above). Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-BUFFER-STORE

## Friction

- R10-PREPR-UNPINNED-RED: unenforced: `tools/pr/prepr.sh` `body_line` still appends the bare red name `mutation` for step 6d's unpinned sites (line 787 on main 12b222007), while `pr-contract` passes the check-run name `tests / mutation`. Carry: R10-FLOW-JIDOKA
- R10-FIXER-DISPATCH-REF: contradiction: this pass's brief named handoff tip 1193fd228 as "the code of PR #2712", but the PR head 7afd9452b carries round-3 checks absent from it (`git log 7afd9452b --not 1193fd228 origin/main` lists f95291914). Continuing from 1193fd228 alone would have dropped two checks. Carry: R10-ORCH-DISPATCH-REG
- R10-HARNESS-COPY-NAME: cost: a round-3 copy of the harness named `harness.py` shadowed `tests/harness.py`; this pass copied it under its own basename and both ends ran. Carry: dismissed: one-off copy error, not reproduced
