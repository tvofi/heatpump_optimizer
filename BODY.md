R11-OUTSIDE-HONEST-METERED-FLOOR: group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS, for outside pull request 3529 by Bankaifan (fork head 1f9daef4d93f), rebuilt from their build commit 7eeb7cd676 under the approved design `design/R11-OUTSIDE-HONEST-METERED-FLOOR` at 080231bb and owner ruling c2 (the learned floor moves the plan). Credit for the finding and its rows (configured 1.1 kW against a 0.53 kW datasheet floor that the metered running draw never reached) is Bankaifan's.

- **Learning.** `draw_range.update_floor`, called once per `DrawRange.observe`, moves the learned floor on the runs asked at the floor in force since it last moved (`floor_evidence`: the COP floor's reader `DrawRange._run_asked`, given two keyword bounds whose defaults are today's, and one low-end statistic `_low_end_kw`, which `power_floor_kw` now reads too). Raise above (1 + `AGREE_TOLERANCE`) of the floor in force, lower below (1 - `AGREE_TOLERANCE`), clear where the new figure is within tolerance above the configured minimum or under it, hold otherwise; no age lapse; a move resets the count (`floor_since`). A configuration change clears the floor; the legacy-commands clear keeps it.
- **Booking.** `solve_band(..., applies_floor=...)` books `min(floor, top)` where the coordinator's `_solve_band` passes `levels_clamped(config)` (group A's predicate is not on main at the merge base); `_band_fields` passes both figures when either end moved.
- **Publishing.** `SolveBand` gains the bottom's source, reason, raw learned floor and pair count; the Learning Model Status sensor publishes `pump_min_power`, `pump_min_power_source` and `pump_min_power_reason` through one helper shared with the top's three (`_pump_power_end`), with the five reason codes and two source codes translated in `strings.json`, en, de and sv; `docs/how-it-works.md` gains the paragraph.
- **Persistence.** `floor_kw` (absent while unset) and `floor_since` ride the existing `draw` record, additive, no version bump; `_stored_floor` reads them, an absent or unreadable leaf reading unset, the count clamped to the rows kept. A bad floor cell costs only itself, and `store._ACCURACY` declares the two leaves so (no `whole`).

**Departure from the note, raised:** `SolveBand` carries a fifth bottom field, `configured_min_kw`, beside the four the note names, because the entity row the note specifies holds the configured minimum and the stamp is the sensor's only input.

**Convergence as measured, for the reviewer:** after a step in the pump's least draw (1.1 to 1.6 kW) the floor moves once, to a value within `AGREE_TOLERANCE` under 1.6 (1.45 on the fixture), and holds there: the hold band admits it, and the floor approaches the new least draw from below, never past it. The loop check states this property, not equality with the new least draw. Whether Bankaifan's install meets the convergence premise (draw nondecreasing in the ask) is not measured here: their report gives a 1.1 to 3.3 kW range, no time series is in the tree, and no finder harness exists for this group.

**Also corrected in this diff:** seeding `finite_boundary.py`'s Arm 6 with a draw window (so the new leaves are driven at all) showed the window's `draw/samples` and `draw/ceiling` cells declared as if a bad cell cost only itself, where `DrawRange.from_dict` drops the row, or a command's pair, by design. Those cells now declare `whole` with that reason; no loader changed.

**Carries received.** Carry 0 (the window's low end read through R10-COP-LEARNER-DRAW-FLOOR's reader, never a second statistic): built; `floor_evidence` reads `DrawRange._run_asked` with bounded asks and a trailing count, and `power_floor_kw` and the floor share `_low_end_kw`; the carry-0 check pins the reader's defaults and the COP floor's figure. Carry 1 (owner ruling c2: the learned floor moves the plan, its convergence shown by a failing test on the build's loop first, with its null control): built; the loop check's failing arm is the build's configured-floor store with its lapse, and null controls (a) to (c) are under `## Null control`. Carry 2 (the store-wide check of every whole= declaration, this body's own Follow-up below, folded onto the roster at the handoff): not built here; it is this group's next part, pending the orchestrator's ruling on its scope.

**Fix review round 1 (verdict/3670, blocked at efc63b60e8, class harness), answered:**

- **Block** (`draw/floor_kw` and `draw/floor_since` declared `whole=_DRAW_KEY` while a bad cell costs only itself): repaired in 95e70c96d4. Both declarations drop `whole` (`Domain("real", _POS)` and `_COUNT`, as `draw/overdraws` is), and their comment states the cost. A new floor-block check, `metered floor, declared cost`, reads each leaf's declaration from `store._ACCURACY` and holds it to the cost `DrawRange.from_dict` measures for every bad value of the reviewer's probe (`floor_kw` `'x'`, `-1.0`, `True`, `[1]`; `floor_since` `'x'`, `-3`, `1.5`): `cell` when only that leaf reads unset (or 0) and the rest of the record comes back identical, `record` when the samples, configuration or latch go with it. Its null control: the good record (a learned floor, a count above 0, samples) round-trips unchanged. Proofs under `## Mutation proof`.
- **Follow-up** (`finite_boundary.py` refuses no `whole=` declaration whose cell costs only itself): the new check closes it for the two leaves this diff adds. A store-wide check is wider than this repair's brief ("do not widen scope"), and its first sibling is measured under `## Figures` (`draw/engaged`, on main before this diff). Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (pending orchestrator ruling on widening the repair to a store-wide `whole` cost check and `draw/engaged`'s declaration)
- **Residual, no finder harness:** disclosed above. Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- **Residual, mutant M13** (dropping `np.isfinite(floor) and` in `_stored_floor`): equivalent on the real load path behind `_sanitize`. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Head

`4afcaaad6d91111de0160b80bfe3c82b881534fb` repairs the red head `41ca33b38dac4622da51359067ac5c6c2bbc455d` (the pull request was `DIRTY` on `tests/golden/claimed_drift.txt`) in two commits. `9a7fee16a2` merges origin/main `8f39313a44` (v10.0.3) with the claimnotes driver installed; the driver refused (`CONFLICTING CLAIMS`: main restamped `claims-for:` 10.0.2 to 10.0.3 and emptied the list), so the resolution by hand is main's file with only this branch's own lines added: the five coord claims and the comment block naming their three leaves, under `claims-for: 10.0.3`. `4afcaaad6d` re-runs the D6 register, which `tests / fast (3.14)` refused (`## Red checks`). No production line changed since 41ca33b38dac. Measured 2026-11-17, UTC, at origin/main `8f39313a44`.

prepr: passed rc=0 at 4afcaaad6d91111de0160b80bfe3c82b881534fb

`41ca33b38dac4622da51359067ac5c6c2bbc455d` is the `mutation-autofix` commit (ci: pin killed mutants) on `e385756030a3`.

`e385756030a3814631722ee04dcf6733b1f1f0e0` is the orchestrator's recarry of main into the previous head. It is not a clean merge of the live head and main (parent 1 and parent 2 do not merge cleanly; a resolution goes through prepr), so prepr checked this head.

`c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3` merges main `92d38ec` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`f4e48cca12ffad04db159d9babf2439f099d4f71` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`95e70c96d40ad5ee4c31582dc64d83ce282e5950` adds one commit on `efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0` (the head the review blocked): `store.py`'s two floor declarations and the floor block's declared-cost check. `git merge-tree --write-tree origin/main 95e70c96d4` at origin/main `6f422812d5` reports no conflict, so no merge; measured 2026-11-16, UTC. prepr passed rc=0 at that head.

`efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0` adds one commit containing only this PR's own row, `dev/programme/delivery/3670.md`.

`281c49216a7e6b14674f2287221fb07843520f59` adds one commit containing only this PR's own row, `dev/programme/delivery/3670.md`.

`e76136488456f245a4c874265fbd95d23f0b91f8` adds one commit containing only this PR's own row, `dev/programme/delivery/3670.md`.

`45749c7d90412c2576d37d9219f019306e8d5f44` merges origin/main `367c3b9cac` into the authored code head `fd246e8e5ee70451d3478137b3a378ff14910366` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

fd246e8e5ee70451d3478137b3a378ff14910366, cut from origin/main 030a4d377f9f26f5b8befe5721d86aea454f29e0 (the merge base); measured 2026-11-16, UTC.

## Mutation proof

The floor block: `tests/features.py` from the line `# -- R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor moves the plan` to the script's close, 14 checks at 95e70c96d4 (13 before it), run by `tools/audit/seat/features_block.py` with the prelude its `--emit-prelude` writes (11 statements). The part-D block: from `# -- R10-COP-GATE part D: the learned top reaching the plan` to `# #2808: the outcome is recorded.`, 15 checks, prelude of 31 statements. This pass changes no production line, so no mutant is re-drawn.

- **Round 1's block, failing test first.** The declared-cost check on efc63b60e8's `store.py`: `1 of 14 FEATURES BLOCK FAILED`, `FAIL metered floor, declared cost ... [declared {'floor_kw': 'record', 'floor_since': 'record'} measured {('floor_kw', "'x'"): 'cell', ('floor_kw', '-1.0'): 'cell', ('floor_kw', 'True'): 'cell', ('floor_kw', '[1]'): 'cell', ('floor_since', "'x'"): 'cell', ('floor_since', '-3'): 'cell', ('floor_since', '1.5'): 'cell'}]`. At 95e70c96d4: `ALL 14 FEATURES BLOCK PASSED`, rc 0.
- **Round 1's block, mutants** (each applied in place against the floor block, restored, `git status` clean after): `whole=_DRAW_KEY` restored on `draw/floor_kw` alone: `KILLED rc=1` (declared cost); on `draw/floor_since` alone: `KILLED rc=1` (declared cost); `DrawRange.from_dict` returning an empty range on a bad `floor_kw` (a loader that spends the licence): `KILLED rc=1` (declared cost, and edges). 3 of 3 killed.
- **Failing test first.** The floor block on the merge base's production tree (`git stash` of `custom_components/`, the head's `tests/features.py` kept) raises `TypeError: solve_band() got an unexpected keyword argument 'applies_floor'` in its first check; at efc63b60e8 `ALL 13 FEATURES BLOCK PASSED`.
- **Diff mode**, `python3 tools/audit/seat/mutant_run.py --diff 030a4d377f...HEAD --cmd '<the floor block>'`: 89 mutants (CALL_DEL 1, CMP_BOUND 6, CONST_SWAP 19, GUARD_OFF 6, RETURN_DEL 12, STMT_DEL 45), rc 1 with six `SURVIVED` lines, each killed elsewhere: `draw_range.py:818 RETURN_DEL`, `:821 CMP_BOUND`, `:823 RETURN_DEL`, `sensor.py:2099 RETURN_DEL` and `sensor.py:2059 STMT_DEL` (the top's arms and the status sensor's return) by the part-D block, `--spec` run `KILLED` for all five; `store.py:333 CONST_SWAP` (the count's domain floor 0 to 1) by `tests/finite_boundary.py`, `--spec` run `KILLED store_329_lo1` and `KILLED store_floor_kw_drop` (the floor's declaration deleted), both `SURVIVED` before Arm 6's seed held a draw window.
- **Spec mode, the operators diff mode does not draw** (`BOOLOP`, `CLAMP_DROP`, and bound flips on lines it does not reach), against the floor block: `SURVIVED NULL`, and `KILLED` for each of `254_CLAMP_DROP`, `257_CMP_floor`, `257_CMP_zero`, `257_CMP_lo`, `257_CMP_hi`, `324_CLAMP_DROP`, `493_BOOLOP`, `495_CLAMP_rows`, `495_CLAMP_zero`, `612_CMP_hi`, `615_CMP`, `616_GUARD_OFF`, `814_BOOLOP`, `814_CLAMP_DROP`, `2439_BOOLOP` (15 of 15).
- **The design's mutation targets**, 24 hand mutants in place against the floor block, each restored: all 24 killed, with the failing checks: E's ask bounds (the loop, down and out, alignment, nulls (b)(c)); E's trailing count (down and out); the move's reset (down and out); the count's clamp (persistence, alignment); the clear's reset (down and out, alignment); reconfiguration clearing F (down and out); raise tolerance (the loop); lower tolerance (down and out); clear to configured (down and out, surface); the `MIN_SAMPLES` gate (the loop); `observe` calling the update (the loop, down and out, persistence, null control (a)); `min(F, top)` (application); the keyword's default (application); keyed to the configuration (persistence); reasons unexceeded (surface), cycled (application, coordinator, surface), plan_writes_power (application, surface); the store reader (persistence, alignment); the stored count's clamp (alignment); the stored floor above configured (persistence); `as_dict`'s floor (persistence); the predicate `levels_clamped` (coordinator); `_band_fields`' either-end test (coordinator, null control (a)); the minimum row's count key (surface).

## Null control

Each a check in the floor block, green at the head:

- **(a)** A full `async_run_optimization` twice on an on/off install (`compressor_modulation: on_off`, so `levels_clamped` holds): a pump whose least draw is the configured minimum learns no floor, and the solve books the same minimum, the same `power_schedule` and the same top fields as with an empty window. Its perturbation, a least draw of twice the configured minimum, moves the solve's minimum to it with reason `measured`.
- **(b)** A draw of ask + 0.053 kW (under 15 % of the configured 0.53) over four windows learns no floor and the band stays 0.53 at every step.
- **(c)** A window of 3.0 kW asks only on a pump whose least draw is 1.1 learns no floor.
- **The build's form**, as the failing arm of the loop check: Bankaifan's configured-floor store with its `CEILING_LAPSE_DAYS` lapse, emulated in the block on the same pump, returns the band to 0.53 three times over four lapse periods; the head's form moves it once.
- **Declared cost** (round 1's block): the good record, with a learned floor, a count above 0 and samples, reads back from `DrawRange.from_dict` identical to what `as_dict` wrote; the check asserts that precondition before comparing any bad cell's cost.
- **Goldens**: five coord fixtures move in exactly the three claimed leaves each; every other fixture unmoved (`## Figures

## Figures

<!-- figure-block: scope-line mb=69053da4f99c4e90952f6947c169aa6e96129dc6 head=4afcaaad6d91111de0160b80bfe3c82b881534fb -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

- At 4afcaaad6d (this pass): `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: C115 reads `0 of 88 entity names identical in sv and en`, committed. The same run in a worktree of origin/main `8f39313a44` leaves that tree's committed register byte-identical (`git status --short` printed nothing there), C115 `0 of 86`; no verdict changes. At 41ca33b38dac the committed register still read 86, so the run left it modified, which `tests / fast (3.14)` refused. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 115 HARNESS HEADER CHECKS PASSED`, rc 0 (at 41ca33b38dac: `1 of 115 HARNESS HEADER CHECKS FAILED`). `python3 tests/env_drift.py --claims-only 8f39313a44`: `claims hygiene: 8f39313a44a4baec18b239ba925f6e164eb26bd2 ok`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- At 95e70c96d4 (round 1's repair): `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`: `ALL 114 FINITE BOUNDARY CHECKS PASSED`, rc 0. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget touched. `python3 tools/pr/ci_predict.py --base origin/main` on a scratch merge of the head with origin/main 6f422812d5 (the tree CI's mutation job reads): `no closures, fast, governance or instrument red predicted`, 27 unpinned sites, the same file, line and operator, one for one, as `## Unpinned sites` below; at the unmerged head the same draw_range.py sites carry other numbers (254 for 255, 567 for 578 and so on), which `prepr.sh` step 7d reads; `## Unpinned sites` lists each site under both numberings.
- Class seams of round 1's block. Rule: every `store._ACCURACY` key whose `whole` is `_DRAW_KEY` (`[k for k, d in _ACCURACY.items() if not isinstance(d, str) and d.whole == _DRAW_KEY]`), each driven with a bad value through `DrawRange.from_dict` on a record holding a floor, samples and the latch. At 95e70c96d4 it returns two: `draw/config/#` (`['x', 3.3]`: samples dropped, latch False; the licence holds, already guarded by Arm 6), and `draw/engaged` (`'x'`: samples kept, only the latch reads False; the same over-broad licence, declared on main before this diff, carried with the follow-up above). Before the repair it also returned `draw/floor_kw` and `draw/floor_since`, closed in this diff. Null: the same record unperturbed round-trips unchanged (`True`).
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=030a4d377f ./tests/run.sh`, at b441ed4737 (the head less fd246e8e5e, which adds checks to the floor block alone): `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, then `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, exit 0. At 5bf4b03f0b: `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN`, exit 0.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at 95e70c96d4: `ALL 5733 FEATURE CHECKS PASSED`, exit 0 (at efc63b60e8: `ALL 5732 FEATURE CHECKS PASSED`; the one added is the declared-cost check).
- `tests/env_drift.py --all 030a4d377f` inside that gate: `CLAIMED` coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone, each `3 leaves moved`, the three `sensors.model_status.extra_state_attributes.pump_min_power*` leaves `present on one side only`; `no committed fixture is stale`; no `UNCLAIMED` line. `tests/golden/card_claimed_drift.txt` is byte-identical to the merge base (`git diff --quiet 030a4d377f HEAD -- tests/golden/card_claimed_drift.txt && echo CARD-CLAIMS-IDENTICAL` prints `CARD-CLAIMS-IDENTICAL`).
- `python3 tests/structure.py` at efc63b60e8: `STRUCTURE RATCHET PASSED`, no budget touched. At c58140029a it read `FAIL functions_cc_over_15 27 > 26`; paid by moving the bottom end's ruling out of `solve_band` into `_bottom_fields`, not by a raise.
- `python3 tools/audit/archscore/score.py --diff 030a4d377f fix/r11-outside-honest-metered-floor`: `Architecture score: dS +0.0000 NULL`. At 5bf4b03f0b's parent it read `dS -0.6607 WORSENS (inadmissible: duplication_copies 18->19)`, the new sensor reader a copy of the top's (`counters.gapped_clones` over the package, the one added class `sensor.py _pump_max_power, _pump_min_power`); paid by one shared `_pump_power_end`.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` at efc63b60e8: `ALL 114 FINITE BOUNDARY CHECKS PASSED`. With the draw seed and without the `_DRAW_ROW` declarations: `2 of 114 FINITE BOUNDARY CHECKS FAILED`, `DOMAIN accuracy:accuracy/draw/ceiling/#/# bad cell -0.75 cost 2 neighbour(s)` and four `draw/samples` lines like it, plus two `UNREACHED` on a command cell beside a null partner.
- `python3 tools/pr/ci_predict.py --base origin/main` at b441ed4737: `no closures, fast, governance or instrument red predicted`; 27 unpinned sites, below. Before the nine `killed_by` pins on edited lines were deleted (8306167a13) it predicted nine `STALE PIN` reds on `ledger`.
- Convergence, from the loop check's own fixture (`_mf_run`, plan asking the band's minimum on even steps): g = max(a, 1.1) and g_f(f) = 1.1 move once, at step 94 (the 48th ask at the minimum), to 1.1; the step in least draw moves once more, at a step past `2 * WINDOW`, to 1.45, within 15 % under 1.6.

## Unpinned sites

- custom_components/heatpump_optimizer/coordinator.py:2439 BOOLOP: pinned by mutation-autofix; killed locally by spec `2439_BOOLOP`
- custom_components/heatpump_optimizer/coordinator.py:2439 GUARD_OFF: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:255 CLAMP_DROP: pinned by mutation-autofix; killed locally by spec `254_CLAMP_DROP`
- custom_components/heatpump_optimizer/draw_range.py:258 CMP_BOUND*4: pinned by mutation-autofix; killed locally by spec `257_CMP_floor`, `257_CMP_zero`, `257_CMP_lo`, `257_CMP_hi`
- custom_components/heatpump_optimizer/draw_range.py:325 CLAMP_DROP: pinned by mutation-autofix; killed locally by spec `324_CLAMP_DROP`
- custom_components/heatpump_optimizer/draw_range.py:494 BOOLOP: pinned by mutation-autofix; killed locally by spec `493_BOOLOP`
- custom_components/heatpump_optimizer/draw_range.py:495 CMP_BOUND: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:496 CLAMP_DROP*2: pinned by mutation-autofix; killed locally by spec `495_CLAMP_rows`, `495_CLAMP_zero`
- custom_components/heatpump_optimizer/draw_range.py:496 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:578 GUARD_OFF: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:586 CMP_BOUND: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:586 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:592 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:608 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:623 CMP_BOUND*2: pinned by mutation-autofix; killed locally by diff mode (the lower bound) and spec `612_CMP_hi` (the upper)
- custom_components/heatpump_optimizer/draw_range.py:623 GUARD_OFF: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:626 CMP_BOUND: pinned by mutation-autofix; killed locally by spec `615_CMP`
- custom_components/heatpump_optimizer/draw_range.py:627 GUARD_OFF: pinned by mutation-autofix; killed locally by spec `616_GUARD_OFF`
- custom_components/heatpump_optimizer/draw_range.py:825 BOOLOP: pinned by mutation-autofix; killed locally by spec `814_BOOLOP`
- custom_components/heatpump_optimizer/draw_range.py:825 CLAMP_DROP: pinned by mutation-autofix; killed locally by spec `814_CLAMP_DROP`
- custom_components/heatpump_optimizer/draw_range.py:826 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:832 CMP_BOUND: pinned by mutation-autofix; killed locally by the part-D block (spec `lapsed_CMP_BOUND`)
- custom_components/heatpump_optimizer/draw_range.py:835 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:847 GUARD_OFF: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:849 GUARD_OFF: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/sensor.py:2099 RETURN_DEL: pinned by mutation-autofix; killed locally by the part-D block (spec `pump_max_power_RETURN_DEL`)
- custom_components/heatpump_optimizer/sensor.py:2105 RETURN_DEL: pinned by mutation-autofix; killed locally by diff mode (the floor block)
- custom_components/heatpump_optimizer/draw_range.py:829 RETURN_DEL and :834 RETURN_DEL (diff-mode survivors of the floor block, already pinned lines re-cut by `band`): killed locally by the part-D block (specs `plan_writes_power_RETURN_DEL`, `not_below_RETURN_DEL`)
- custom_components/heatpump_optimizer/draw_range.py:254 CLAMP_DROP: the site listed above as `draw_range.py:255 CLAMP_DROP`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:257 CMP_BOUND*4: the site listed above as `draw_range.py:258 CMP_BOUND*4`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:324 CLAMP_DROP: the site listed above as `draw_range.py:325 CLAMP_DROP`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:493 BOOLOP: the site listed above as `draw_range.py:494 BOOLOP`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:494 CMP_BOUND: the site listed above as `draw_range.py:495 CMP_BOUND`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:495 CLAMP_DROP*2: the site listed above as `draw_range.py:496 CLAMP_DROP*2`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:495 RETURN_DEL: the site listed above as `draw_range.py:496 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:567 GUARD_OFF: the site listed above as `draw_range.py:578 GUARD_OFF`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:575 CMP_BOUND: the site listed above as `draw_range.py:586 CMP_BOUND`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:575 RETURN_DEL: the site listed above as `draw_range.py:586 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:581 RETURN_DEL: the site listed above as `draw_range.py:592 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:597 RETURN_DEL: the site listed above as `draw_range.py:608 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:612 CMP_BOUND*2: the site listed above as `draw_range.py:623 CMP_BOUND*2`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:612 GUARD_OFF: the site listed above as `draw_range.py:623 GUARD_OFF`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:615 CMP_BOUND: the site listed above as `draw_range.py:626 CMP_BOUND`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:616 GUARD_OFF: the site listed above as `draw_range.py:627 GUARD_OFF`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:814 BOOLOP: the site listed above as `draw_range.py:825 BOOLOP`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:814 CLAMP_DROP: the site listed above as `draw_range.py:825 CLAMP_DROP`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:815 RETURN_DEL: the site listed above as `draw_range.py:826 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:821 CMP_BOUND: the site listed above as `draw_range.py:832 CMP_BOUND`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:824 RETURN_DEL: the site listed above as `draw_range.py:835 RETURN_DEL`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:836 GUARD_OFF: the site listed above as `draw_range.py:847 GUARD_OFF`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states
- custom_components/heatpump_optimizer/draw_range.py:838 GUARD_OFF: the site listed above as `draw_range.py:849 GUARD_OFF`, numbered at the unmerged head 95e70c96d4 rather than on its merge with origin/main 6f422812d5; pinned by mutation-autofix; killed locally as that line states

## Red checks

- `tests / fast (3.14)` at 41ca33b38dac: `tests/harness_headers.py` failed `the executed harnesses leave their committed output byte-identical` (`M dev/audit/rounds/round4/D6/claims.json`, `M dev/audit/rounds/round4/D6/claims.md`). Main's #3678 re-ran the register at 86 entity names, the recarry merge e385756030a3 took main's copy, and this branch adds two names, so C115 read 88 against a committed 86. Repaired in 4afcaaad6d by committing the re-run (`## Figures`). Cheaper detector: running `dev/audit/rounds/round4/D6/claims.py` (seconds) after any merge of main that touches the translations. None is built here: the committed register depends on main's tip, so only a check run after the merge can see the mismatch, and the first gate run after the merge is the one that caught it.

- `gate` at 41ca33b38dac: the aggregate of `tests / fast (3.14)` and `pr-contract / pr-contract`, answered on those lines; no cause of its own.

- `pr-contract / pr-contract` at 41ca33b38dac: the body did not name the `tests / fast (3.14)` red, and its figure block named head e385756030a3. Both are answered in this body (the line above; the block re-rendered by `figure_block.py refresh`). Cheaper detector: `tools/pr/prepr.sh`'s body check, already in place. The autofix commit 41ca33b moved the head after the body was written, and no check before the push can see that.

- `tests / mutation` at fd246e8e5ee7: red by construction on the 27 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. No cheaper detector: each site is killed locally (`## Mutation proof`), and the red is the ledger's pin lag, which only the push clears.

- `tests / nightly-status`: red because main's nightly `slow` lane failed last night (NIGHTLY FAILED: slow failed last night); the job grades main, not this diff, and the diff touches none of its reporter inputs. Cheaper detector: none owed by this pull request (owner ruling 2026-11-07: nightly-status is not a required check).

- `governance / env-matrix` at 02266951b6e0: red once on `pr / policy_lint` (`[budgets] tools/audit/briefs/nudge.md` has a files_tokens cap but matches no POLICY_GLOBS pattern), a defect inherited from main, not from this diff; the same job passed on the same head on re-run, and the merge of main with its hotfix (#3698) carries the fix. Cheaper detector: none owed by this pull request, the red was main's and is cleared.

- `governance / policy-docs` at 02266951b6e0: red once on the same inherited main defect as env-matrix (`[budgets]` files_tokens caps for `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` matched by no POLICY_GLOBS pattern); this diff touches neither, and the job passed on the same head on re-run. Cheaper detector: none owed by this pull request, the red was main's and is cleared.

## Forward-carry

none

## Friction

none
