# D3-s3 REPORT (round 11, box B3, local re-run)

Findings: 3
- D3-s3-01 (low): Closure merge never sheds a file a script stopped touching: 21 stale pairs force 1209 s of runs that cannot see the edit
- D3-s3-02 (low): Scoped gate selects by file: 265 of 1423 selected runs import the edited module but run none of its function bodies
- D3-s3-03 (low): features.py re-solves identical inputs: 60 main-process solves repeat one the same process already ran (exact, 3 runs)

D3-s3-03 is keyed to the 60 main-process repeats. Box B3's total of 113 (60 main + 53 worker repeats) is a stated difference, not the key.

## Crash
Per-pair verdicts lost: prescreen_local.json/.progress.jsonl and prescreen_cheap.* were in the scratch clone under /private/tmp, cleared by the machine reboot at ~17:40Z. Attempt 3 (null control survived every driver, mutants from ~13:59Z) and the cheap-subset screen (from 16:24Z) produced verdicts that cannot be reported. The only verdict in the progress log, away.py:177 'killed' by entities.py at 16:58:57Z, fell in the ENOSPC window (~16:57Z) and is suspect, so it is not counted. examined=0 is the honest count.

## Unfinished
- D3.M2: Re-run the 38-site pool pre-screen (selection_local.txt) on a quiet box. Per-pair verdicts lost: prescreen_local.json/.progress.jsonl and prescreen_cheap.* were in the scratch clone under /private/tmp, cleared by the machine reboot at ~17:40Z. Attempt 3 (null control survived every driver, mutants from ~13:59Z) and the cheap-subset screen (from 16:24Z) produced verdicts that cannot be reported. The only verdict in the progress log, away.py:177 'killed' by entities.py at 16:58:57Z, fell in the ENOSPC window (~16:57Z) and is suspect, so it is not counted. examined=0 is the honest count. Keep the records inside the worktree, not under /private/tmp.
- D3.M2: Pre-screened only the 38-site weighted pool (selection_local.txt), and only the part of it the window allowed (prescreen_table.py: KILLED/LIVES vs OPEN/NOT-RUN). The remaining sites of the 663 universe are listed by file in coverage.not_reached. Each survivor sweep costs about 45 min of features.py plus 20 min of entities.py at load1 40-226 on the shared 8 GB M1. Re-run with: prescreen.py --sites <next lines of select_pool.py --n 663 --per-file 99> --reach-rows --reuse-baselines --progress P.
- D3.M3: The full GATE_SCOPE=full GOLDEN_MODE=drift gate for the top six survivors is owed to the quiet window. Round 10's C3/C5 items (its survivors M08, M01, M03, M22, M21, M19 and its REPORT.md) are not in this export.
- D3.M5: Quiet-box per-script CPU table (C7), kill-overlap matrix via prescreen.py --overlap (C9), and stress.py's S/A row (stress.py runs only in the quiet window).
- D3.M3/M4: Confirm survival of away.py:177 GUARD_OFF and boost.py:595 CMP_BOUND against the full closure (features.py, entities.py), then run the quiet-window full gate.

## Not reached (M2 pool)
All 38 pool sites; load1 46.2 / load5 153.4 at 17:50Z (9 min after reboot), 8 cores: CPU share per runnable ~0.17 core; during the run load1 40-226, swap 3.6/4 GB.

- away.py:177 GUARD_OFF
- boost.py:595 CMP_BOUND
- comfort_band.py:141 CMP_BOUND
- comfort_learning.py:143 CMP_BOUND
- config_flow.py:1049 CMP_BOUND
- curve_learning.py:94 CMP_BOUND
- device_prefill.py:250 GUARD_OFF
- dhw_draws.py:150 CMP_BOUND
- dhw_learning.py:267 GUARD_OFF
- dhw_schedule.py:410 CMP_BOUND
- diagnosis.py:105 GUARD_OFF
- external_heat.py:228 GUARD_OFF
- freq_control.py:150 CMP_BOUND
- legionella.py:256 GUARD_OFF
- mixing_valve.py:175 CLAMP_DROP
- modbus_prefill.py:174 GUARD_OFF
- narrative.py:139 CMP_BOUND
- power_guard.py:84 GUARD_OFF
- presets.py:225 GUARD_OFF
- pump_arbiter.py:1455 CMP_BOUND
- pump_schedule.py:51 CMP_BOUND
- pv.py:70 CLAMP_DROP
- quick_setup.py:140 GUARD_OFF
- repairs.py:36 GUARD_OFF
- wood_fuel.py:347 CMP_BOUND
- frontend.py:91 GUARD_OFF
- open_meteo.py:174 CMP_BOUND
- plan_slots.py:69 CMP_BOUND
- battery.py:316 CLAMP_DROP
- manual_plan.py:147 GUARD_OFF
- wear.py:241 CMP_BOUND
- pump_signals.py:549 GUARD_OFF
- disinfection.py:126 RETURN_DEL
- drift.py:324 GUARD_OFF
- name_match.py:144 RETURN_DEL
- prefill_offer.py:101 GUARD_OFF
- pump_mode.py:271 RETURN_DEL
- silent_mode.py:116 CLAMP_DROP
