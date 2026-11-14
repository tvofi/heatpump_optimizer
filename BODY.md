R10-DRAW-MAP-EVIDENCE part F (design/R10-DRAW-MAP-EVIDENCE 9aa450f5, `Design review: approve 9aa450f5...` at design-verdict f10dd418): a D15-complete debug week. Non-gating by owner order; this pull request opens only after the group's part 1 (handoff/r10-draw-map-evidence 3533ba12) and R10-COP-LEARNER-DRAW-FLOOR merge, and part A lands before or beside it.

What a D15 seat can now conclude from a bundle that it could not before:
- replay any window of the collected week through `tools/replay/debug_replay.py --bundle B --trace --start/--end`, not only the 24 h replay half: every mapped input at minute resolution, keyed by config key and mapped back to its entity through the replay half's own entry;
- read restarts directly (`lifecycle` rows: load, close, start, with the release) instead of inferring them from cycle-row spacing (`d15_restart_gaps.py` prints `RESTART` lines);
- read per cycle whether the learners were frozen, why, and the input watchdog's verdict (D15 M7);
- tell a version 1 bundle from a version 2 one (`schema`, `manifest.sections`), and what the inline cap cut (`manifest.dropped`).

Still unanswerable from a bundle: sub-minute dynamics outside the replay half; the price forecast outside the replay half (the trace carries states, not attributes: a trace window outside it replays with the replay half's attributes in force at its start, said in the document's `downsampled`); entities the entry does not map and the published entities outside the replay half; text from any domain but select, input_select, switch, input_boolean and binary_sensor; anything before the collection started; the arbiter's pass record until part A publishes it (below).

## Head

Measured at 880b015c8b1ba557ef3eb4eda67887c61fef9180; base origin/main 4058469d79 merged with handoff/r10-draw-map-evidence 3533ba12 (commit 7167747213). Taken 2026-11-14T21:44Z (date -u).

## Mutation proof

Failing first: the new `tests/debug_collect.py` section run against the base's `debugger.py`, `store.py` and `tools/replay/debug_ingest.py` (scratch copy of the head with those three restored from 7167747213) stops at its first check: `AttributeError: module 'heatpump_optimizer.debugger' has no attribute 'trace_columns'`.

Diff mutants: `python3 tools/audit/seat/mutant_run.py --diff 7167747213...HEAD --cmd 'bash mutcmd.sh' --max-mutants 400 --report-only`, where the command is `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` then `debug_ingest.gate_checks()` (both must pass), at 128dbfaf: 320 mutants drawn; `custom_components/heatpump_optimizer/debugger.py` and `store.py`: every one KILLED (first run, at 830875fe, listed 31 debugger.py survivors; each was answered by a new check or by removing the dead or redundant code it exposed, commits f0be7daa and 128dbfaf). The tool files were then driven by their own graders, since the command above does not run them: `tools/replay/debug_ingest.py` by `debug_ingest.gate_checks()` (survivors answered by new arms, commit 22de44c2); `tools/replay/dbg_bundle_gen.py` by `dbg_bundle_gen.gate_checks()` (spec run of its 41 diff mutants: 36 KILLED, `gencmd.sh`); `tools/replay/debug_replay.py` by `d15_trace_budget.py --replay-null G` (spec run of its 40 diff mutants: 29 KILLED, and 6 of the 11 survivors KILLED on a re-run once `debug_replay.gate_checks()` gained the trace-document arm, commit 880b015c). Tool survivors and their dispositions: under `## Unpinned sites` (the mutation lane mutates `custom_components/` only).

## Null control

- With the debug option off: no minute timer is registered and nothing is stored (`tests/debug_collect.py` "with the debug option off no minute timer is registered and nothing is stored"); `dev/audit/harnesses/d15_trace_budget.py --writes` prints `option_off store_bytes_written_per_day=[0, 0, 0, 0, 0, 0, 0]`.
- An older bundle read by the new ingest: every trace check is `unfinished`, never passed (`debug_ingest.gate_checks` "an hpo-debug/1 bundle leaves every trace check unfinished, none passed"; on the synthetic version 1 bundle `RESULT unfinished=6`).
- A new bundle read by the old reader fails loudly: the base's `tools/replay/debug_ingest.py` (from 7167747213) on the synthetic version 2 bundle prints `FAIL: schema -- schema='hpo-debug/2'` and `smoke_verdict=fail`.
- Trace against replay half: `debug_replay.offender_window` over the synthetic 2-day bundle, from the replay half and from `trace_document`, gives the same agreement offenders (2 and 2, equal); the perturbation (the hot-water column forced to 20 °C) moves them (0).
- Planted leak: with the diagnostics value pass deliberately broken (`diagnostics._without_values` replaced by identity), the entry's name planted as a selector's state reaches the download's trace (check "the planted leak's control"); with it intact, no planted value (name, full-precision coordinate, person id, token) appears, the name's cell decodes as a flagged gap, and the decoded trace passes `export.violations`.

## Figures

Commands run from the worktree root with `PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH`; `B` is the owner's newest diagnostics download (private, outside every tree; only byte counts are quoted), `G` the synthetic bundle `PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 2 --out G` (26 s).

- Design P2 to P7 re-run on `B` with the designer's scripts (`python3 -I <probe> B`): reproduced (P3 inputs 1,642,482 / published 600,170 bytes; P4 27 input columns 63,965 bytes a day; P7 non-replay with additions 4,751,393, left for replay 3,375,071 against 3,375,297): the estimate design P7 made.
- The trace priced with the production encoder: `python3 -I dev/audit/harnesses/d15_trace_budget.py --bundle B` (4 s): `trace_columns_inputs=25`; `trace_day_inputs=48482`, `trace_week_inputs=339375` bytes at indent 2; with the arbiter's pass record bounded by 13 copies of the densest input column (no release publishes one yet: the design's 13-column estimate, now an upper bound) `trace_week_with_arbiter_bound=574169`; map rows (part A) `map_rows_columnar=79006`.
- 8 MB budget at 168 h with all of that: `all 7 snapshots: non_replay=4652196 left_for_replay=3474268 replay_24h=3375297 fits=True` (98,971 bytes to spare); with snapshots thinned to two, `left_for_replay=4645329`. On this install the full week fits beside the 24 h replay with no cut; the drop order is pinned by `tests/debug_collect.py` ("at the inline cap the download is cut in the note's order", "thinning keeps the first and the newest snapshot").
- Store writes per day, days 1 to 7 (`python3 dev/audit/harnesses/d15_trace_budget.py --writes [--columns N --change P]`, 2 s each): option off `[0, 0, 0, 0, 0, 0, 0]`; ring without a trace (`--columns 0`) 144,052 to 1,787,620; 27 columns changing in 5 % of minutes 715,797 to 9,415,572; in 30 % 1,255,345 to 16,750,016 bytes.
- Trace null control: `python3 dev/audit/harnesses/d15_trace_budget.py --replay-null G` (26 s): `offenders_replay_half=2 offenders_trace=2 equal=True`; `offenders_perturbed=0 moved=True`.
- Version seam: `PYTHONPATH=tests/hastub:tests python3 tools/replay/debug_ingest.py --bundle G` (0.6 s): `stages_ok=16/16`, `unfinished=1` (trace-arbiter, absent); on a version 1 synthetic bundle and on `B`: `stages_ok=11/11 unfinished=6`, verdict pass; the base's reader on `G`: `FAIL: schema`, verdict fail.
- Restarts: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_restart_gaps.py --bundle G` prints `lifecycle_rows=0 restarts_logged=0`; on a version 1 bundle `lifecycle=absent`; on `G` with a planted close and load, `restarts_logged=1`.
- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: ALL 184 checks pass (4.4 s). `debug_ingest.gate_checks()`: 17 of 17 (0.8 s); `dbg_bundle_gen.gate_checks()`: 6 of 6 (1 s); `debug_replay.gate_checks()`: 6 of 6 (2 s). The DBG block of `tests/features.py` through `tools/audit/seat/features_block.py` with its emitted prelude: ALL 121 pass (1 min 42 s).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, every metric where the base has it.
- `python3 tools/audit/archscore/score.py --diff 7167747213 HEAD`: `Architecture score: dS -0.0017 WORSENS (inadmissible: coord_footprint 2497->2500)`, explained under `## Architecture score`; the first cut read 2497->2506, paid down as stated there.
- `node tools/policy/policy_lint.mjs --budgets`: D15.md 697 tokens against 697; corpus 68955 inside 69118. `node tools/policy/rules_sync.mjs --check`: ok. `node tools/policy/brief_lint.mjs`: ok.
<!-- figure-block: scope-line mb=4058469d79a3b43d840921b82b23f31494ba14b2 head=880b015c8b1ba557ef3eb4eda67887c61fef9180 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

Each `debugger.py` site below was KILLED in the final local run (`mutant_run.py --diff 7167747213...HEAD`, command above: no `debugger.py` or `store.py` line in its SURVIVED list); pinned by mutation-autofix once CI's mutation job records the killer (`tests/debug_collect.py`).

- `custom_components/heatpump_optimizer/debugger.py:119 CONST`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:257 BOOLOP`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:257 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:259 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:262 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:267 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:272 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:275 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:282 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:287 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:293 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:295 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:302 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:308 BOOLOP`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:308 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:310 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:312 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:317 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:319 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:324 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:335 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:338 BOOLOP`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:338 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:338 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:343 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:350 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:364 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:367 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:374 BOOLOP`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:377 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:394 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:395 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:653 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:660 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:671 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:671 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:688 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:692 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:713 CLAMP_DROP`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:715 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:775 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:779 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:793 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:795 CMP_BOUND`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:795 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:802 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:803 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:941 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:959 GUARD_OFF`: killed locally by tests/debug_collect.py; pinned by mutation-autofix
- `custom_components/heatpump_optimizer/debugger.py:980 RETURN_DEL`: killed locally by tests/debug_collect.py; pinned by mutation-autofix

The sites below are not this part's lines: they are part 1's (handoff/r10-draw-map-evidence 3533ba12) and R10-COP-LEARNER-DRAW-FLOOR's, in this diff only because neither has merged; their dispositions are in those pull requests' bodies, and they leave this diff when those merge, before this one opens.

- `custom_components/heatpump_optimizer/accuracy.py:874 CLAMP_DROP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:874 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:922 CLAMP_DROP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:922 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:922 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:936 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:942 CLAMP_DROP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:942 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:942 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:970 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:975 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:977 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:980 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:997 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:999 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:1001 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:1004 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:1004 CMP_BOUND*3`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:1004 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/accuracy.py:1009 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:962 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:962 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5345 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5345 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5371 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5371 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5378 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5423 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5895 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:247 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:247 CMP_BOUND*2`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:247 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:496 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:499 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:499 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:500 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:502 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:502 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:511 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:511 CMP_BOUND*2`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:511 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:523 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:545 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:545 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:548 CMP_BOUND`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:548 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:551 CLAMP_DROP*2`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/draw_range.py:551 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line; disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5319 BOOLOP`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line (prepr's anchor for it); disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5319 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line (prepr's anchor for it); disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5352 RETURN_DEL`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line (prepr's anchor for it); disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5397 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line (prepr's anchor for it); disposed in that pull request
- `custom_components/heatpump_optimizer/coordinator.py:5869 GUARD_OFF`: part 1 / R10-COP-LEARNER-DRAW-FLOOR's line (prepr's anchor for it); disposed in that pull request

Tool sites that survived their grader (no `custom_components/` site survived):

- `tools/replay/debug_replay.py` `trim_replay` CMP_BOUND on both comparisons and CONST_SWAP `before[-2:]`: equivalent: a row exactly at the padded start, or one more row before it, leaves the state in force at every replayed minute unchanged. Carry: dismissed: equivalent mutant
- `tools/replay/debug_replay.py` `_attrs_in_force` CONST_SWAP on the start index: equivalent: `found` already starts at the first row's attributes. Carry: dismissed: equivalent mutant
- `tools/replay/debug_replay.py` `main` STMT_DEL of the `--trace` selection: the CLI branch; `trace_document` itself is pinned by `debug_replay.gate_checks()` and the replay null. Carry: dismissed: CLI dispatch line, its callee pinned
- `tools/replay/dbg_bundle_gen.py` `_value_at` STMT_DEL of `found = None`: equivalent on the committed fixture, where every entity has a row at the window's start. Carry: dismissed: equivalent on the fixture
- `tools/replay/dbg_bundle_gen.py` `build_bundle` STMT_DEL of `trace = trace_blocks(fixture)`: `build_bundle` runs a replay, which its gate checks do not; the generator's CLI and `d15_trace_budget.py --replay-null` fail without it. Carry: dismissed: covered by the generator run, not its gate checks
- `tools/replay/dbg_bundle_gen.py` `gate_checks` CONST_SWAP and CMP_BOUND on its own probe constants: test code. Carry: dismissed: the grader's own constants

## Architecture score

- `coord_footprint` 2497 -> 2500: the minute trace needs a clock bound to the entry's life, so `async_setup_debugger` (already handed the coordinator) registers the timer and its callback, and `pass_record(coordinator)` is the one reader of the arbiter's pass record (part A's hook). Paid before this: the first cut handed the coordinator to `DebugCollector.sample` and `arbiter_cells` and computed setup state in `async_setup_debugger` (2497 -> 2506); the collector now takes the cells and the entry, not the coordinator (`sample(now, extra)`, `begin(entry, version)`), which is the sounder seam as well as the smaller charge. Not taken: reading the pass record through a module-level `getattr` constant to hide the two statements of `pass_record`, a spelling change with no design gain.

## Red checks

- `mutation`: predicted red until `mutation-autofix` pins the sites listed under `## Unpinned sites`; every `custom_components/` one of this part was killed locally by `tests/debug_collect.py`, so the job records killers that exist. No cheaper detector is owed: `prepr.sh` step 6d already predicts it before the push, and the repair is `ci-autofix.md`'s, not a defect.
- `budget-raise-gate`: red by design until tvofi's approving review at the head, because this branch raises `files_tokens["dev/governance/dimensions/D15.md"]` 690 -> 697 (`## Raise justification`). No cheaper detector is owed: the gate is the owner-approval control itself, not a defect detector, and `policy_lint.mjs --pr-body` already reports it at prepr time.

## Approval

Policy change: `dev/governance/dimensions/D15.md` step 5, with the `files_tokens` raise below. Step 5 now reads "... over the replay half or `--trace` any trace window: the lane's judges, offenders per cycle." This is a policy change: it changes what a D15 seat runs. Root-cause state addressed: (d), the process existed and its precondition changed, because a new input (the minute trace) exists that step 5 did not name. It is the owner's card S4 ("Prepare it in the part F pull request"), and it merges only on the owner's approving review. It sits in its own commit with the budget raise below.

## Raise justification

- Cap: `dev/governance/config/policy_budgets.json` `files_tokens["dev/governance/dimensions/D15.md"]`, 690 before, 697 after, the value `node tools/policy/policy_lint.mjs --budgets` measures after the edit (2759 bytes, 690 tokens before; 697 after). Its line cap (37; 36 lines) and every aggregate cap are untouched; corpus 68955 tokens inside cap 68618 + band 500.
- Payments tried: (b) trimming another D15.md line to pay for this one, refused: the file is the owner's own wording and trimming another of his lines is not a payment the orchestrator may approve; a shorter step 5, refused: the file had 2 bytes of slack and no form naming the trace fits in 2 bytes without dropping the tool path or "the lane's judges"; the line as written is the shortest form considered (+30 bytes; the longer form measured +53 bytes, 703 tokens).
- The policy commit alone: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff fc81f01e42 830875fefa`: it changes no Python); part F against its own base 7167747213 reads dS -0.0017, all of it the code commits' `coord_footprint` rise explained under `## Architecture score`.
- Approved by the orchestrator under mandate 6715477401 (scope all), pending the owner's approving review at the head.
- Architecture score: dS +0.0121 WORSENS (the score the gate reads, three-dot from origin/main 4058469d to this head: it includes part 1 and R10-COP-LEARNER-DRAW-FLOOR, both unmerged and judged in their own pull requests)

## Forward-carry

- Hook owed by part A: the trace reads the arbiter's pass record through a module function `pump_arbiter.pass_record(coord)` returning a mapping (or dataclass) of the pass fields; each field becomes a column `arbiter/<field>` through the same cell rules. Until part A defines it the manifest says `arbiter: absent: this release's arbiter publishes no pass record` and `debug_ingest` reports `trace-arbiter` unfinished. Part A names the function so, or this one-line `getattr` is renamed when the two land together. Carry: R10-DRAW-MAP-EVIDENCE
- Part A, handed off and passed review at cc335482, exposes the pass record as `ArbiterState.last_pass` (a `PassRecord`, decided in `pump_arbiter.pass_origin`), not as a `pump_arbiter.pass_record(coord)` function: when F is stacked on A, `debugger.pass_record` needs that one reader wired (`pump_arbiter.state_for(coord).last_pass`), or the arbiter columns stay absent. Carry: R10-DRAW-MAP-EVIDENCE
- Carry 0 (owner scope addition for part 2: what the debug week and the download must carry for a D15 seat): built here for the debug-week half: each field tied to its D15 question (trace: M5, M7, M8 and the map; lifecycle: M1; freeze and verdict: M7), its size (Figures), its write volume on a Pi-class host (Figures), its pass through both diagnostics passes (Null control), and the bundle shape marker (`schema` hpo-debug/2, `manifest.sections`). The map rows are part A's. Carry: R10-DRAW-MAP-EVIDENCE
- Carry 1 (the ceiling store fills only from the probe, body item 19509d31): not built here; it is part B's ([CE] in the design). Carry: R10-DRAW-MAP-EVIDENCE
- Store wear: with the option on, the hourly save rewrites the whole ring, so the trace multiplies the write volume by the day (Figures: about 9.4 to 16.7 MB on day 7 for 27 columns, against 1.8 MB for the ring without a trace). Disclosed in docs/configuration.md; a per-day trace store written once a day would cut it, at the cost of a second store document and its migration. Carry: R10-DRAW-MAP-EVIDENCE

## Friction

- brief: cost: the brief said not to raise a cap, and D15.md had 2 bytes of token slack, so the owner-ordered line could not land without a raise; resolved by the orchestrator's ruling under the mandate. Carry: dismissed: ruled in this pull request
